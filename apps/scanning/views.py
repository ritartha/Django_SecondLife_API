from django.conf import settings
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .models import Region, Parcel, ScanSession, Avatar, Attachment
from .serializers import (
    RegionSerializer, ScanSessionSerializer,
    RegionIngestSerializer, AvatarIngestSerializer, ParcelIngestSerializer,
)
from apps.discord_integration.services import send_scan_to_discord


def _check_lsl_key(request):
    return request.META.get('HTTP_X_API_KEY', '') == settings.LSL_API_KEY


def _broadcast(region_name, data):
    """Push real-time update over WebSocket."""
    ch = get_channel_layer()
    group = f'scan_{region_name.lower().replace(" ", "_")}'
    async_to_sync(ch.group_send)(group, {'type': 'scan_update', 'data': data})
    async_to_sync(ch.group_send)('scan_dashboard', {'type': 'scan_update', 'data': data})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def ingest_region(request):
    if not _check_lsl_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    ser = RegionIngestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data

    region = Region.objects.filter(name__iexact=d['name']).first()
    if region:
        region.region_uuid = d.get('region_uuid', '') or region.region_uuid
        region.map_image_url = d.get('map_image_url', '') or region.map_image_url
        region.save(update_fields=['region_uuid', 'map_image_url'])
        created = False
    else:
        region = Region.objects.create(
            name=d['name'], region_uuid=d.get('region_uuid', ''),
            map_image_url=d.get('map_image_url', ''),
        )
        created = True

    _broadcast(region.name, {'type': 'region_update', 'region': RegionSerializer(region).data})
    return Response({'message': 'Region data received.', 'region_id': str(region.id), 'created': created})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def ingest_avatars(request):
    if not _check_lsl_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    ser = AvatarIngestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data

    region = Region.objects.filter(name__iexact=d['region_name']).first()
    if not region:
        region = Region.objects.create(name=d['region_name'])

    session = ScanSession.objects.create(
        region=region, object_key=d.get('object_key', ''), avatar_count=len(d['avatars']),
    )

    names = []
    for av in d['avatars']:
        avatar = Avatar.objects.create(
            scan_session=session, region=region, name=av['name'],
            avatar_uuid=av.get('uuid', ''), distance=av.get('distance', 0.0),
            is_sitting=av.get('is_sitting', False),
            scripted_attachments_count=av.get('scripted_attachments_count', 0),
        )
        names.append(av['name'])
        for att_name in av.get('attachments', []):
            Attachment.objects.create(avatar=avatar, name=att_name)

    _broadcast(region.name, {
        'type': 'avatar_scan', 'region': region.name, 'avatar_count': len(d['avatars']),
        'avatars': [{'name': a['name'], 'uuid': a.get('uuid', ''), 'distance': a.get('distance', 0)} for a in d['avatars']],
        'session_id': str(session.id),
    })
    send_scan_to_discord(region.name, names)

    return Response({'message': f'Scan recorded: {len(d["avatars"])} avatars.', 'session_id': str(session.id)})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def ingest_parcel(request):
    if not _check_lsl_key(request):
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    ser = ParcelIngestSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    d = ser.validated_data

    region = Region.objects.filter(name__iexact=d['region_name']).first()
    if not region:
        region = Region.objects.create(name=d['region_name'])
    parcel, created = Parcel.objects.update_or_create(
        region=region, name=d['name'],
        defaults={'description': d.get('description', ''), 'owner_name': d.get('owner_name', ''),
                  'coordinates': d.get('coordinates', '')},
    )
    return Response({'message': 'Parcel data received.', 'parcel_id': str(parcel.id), 'created': created})


class RegionListView(generics.ListAPIView):
    serializer_class = RegionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Region.objects.all().order_by('-last_scanned')


class ScanSessionListView(generics.ListAPIView):
    serializer_class = ScanSessionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = ScanSession.objects.select_related('region').prefetch_related(
            'avatars__attachments'
        ).order_by('-timestamp')
        region_id = self.request.query_params.get('region')
        if region_id:
            qs = qs.filter(region_id=region_id)
        return qs