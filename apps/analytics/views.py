from django.db.models import Count
from django.db.models.functions import ExtractHour
from django.utils import timezone
from datetime import timedelta
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from apps.scanning.models import Avatar, ScanSession, Region


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def frequent_visitors(request):
    """Top 50 most frequently seen avatars."""
    days = int(request.query_params.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    visitors = (
        Avatar.objects.filter(detected_at__gte=since)
        .values('name', 'avatar_uuid')
        .annotate(visit_count=Count('id'))
        .order_by('-visit_count')[:50]
    )
    return Response({'period_days': days, 'visitors': list(visitors)})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def peak_hours(request):
    """Scan activity grouped by hour of day."""
    days = int(request.query_params.get('days', 30))
    since = timezone.now() - timedelta(days=days)

    hours = (
        ScanSession.objects.filter(timestamp__gte=since)
        .annotate(hour=ExtractHour('timestamp'))
        .values('hour')
        .annotate(scan_count=Count('id'), total_avatars=Count('avatars'))
        .order_by('hour')
    )
    return Response({'period_days': days, 'hours': list(hours)})


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def overview(request):
    """Dashboard overview stats."""
    days = int(request.query_params.get('days', 7))
    since = timezone.now() - timedelta(days=days)

    total_scans = ScanSession.objects.filter(timestamp__gte=since).count()
    total_avatars = Avatar.objects.filter(detected_at__gte=since).count()
    unique_avatars = Avatar.objects.filter(detected_at__gte=since).values('name').distinct().count()
    active_regions = Region.objects.filter(last_scanned__gte=since).count()

    # Recent scans
    recent = ScanSession.objects.select_related('region').order_by('-timestamp')[:10]
    recent_data = [
        {
            'id': str(s.id),
            'region': s.region.name,
            'avatar_count': s.avatar_count,
            'timestamp': s.timestamp.isoformat(),
        }
        for s in recent
    ]

    return Response({
        'period_days': days,
        'total_scans': total_scans,
        'total_avatars_detected': total_avatars,
        'unique_avatars': unique_avatars,
        'active_regions': active_regions,
        'recent_scans': recent_data,
    })