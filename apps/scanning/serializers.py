from rest_framework import serializers
from .models import Region, Parcel, ScanSession, Avatar, Attachment


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'name', 'detected_at']


class AvatarSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Avatar
        fields = [
            'id', 'name', 'avatar_uuid', 'distance',
            'is_sitting', 'scripted_attachments_count',
            'detected_at', 'attachments',
        ]


class ScanSessionSerializer(serializers.ModelSerializer):
    avatars = AvatarSerializer(many=True, read_only=True)
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = ScanSession
        fields = [
            'id', 'region', 'region_name', 'object_key',
            'avatar_count', 'timestamp', 'avatars',
        ]


class ParcelSerializer(serializers.ModelSerializer):
    region_name = serializers.CharField(source='region.name', read_only=True)

    class Meta:
        model = Parcel
        fields = [
            'id', 'region', 'region_name', 'name', 'description',
            'owner_name', 'coordinates', 'scanned_at',
        ]


class RegionSerializer(serializers.ModelSerializer):
    parcels = ParcelSerializer(many=True, read_only=True)
    scan_count = serializers.SerializerMethodField()

    class Meta:
        model = Region
        fields = [
            'id', 'name', 'region_uuid', 'map_image_url',
            'first_seen', 'last_scanned', 'parcels', 'scan_count',
        ]

    def get_scan_count(self, obj):
        return obj.scan_sessions.count()


# --- LSL Ingest Serializers ---

class RegionIngestSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    region_uuid = serializers.CharField(max_length=36, required=False, default='')
    map_image_url = serializers.URLField(required=False, default='')


class AvatarIngestDataSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    uuid = serializers.CharField(max_length=36, required=False, default='')
    distance = serializers.FloatField(default=0.0)
    is_sitting = serializers.BooleanField(default=False)
    scripted_attachments_count = serializers.IntegerField(default=0)
    attachments = serializers.ListField(
        child=serializers.CharField(max_length=255), required=False, default=list,
    )


class AvatarIngestSerializer(serializers.Serializer):
    region_name = serializers.CharField(max_length=255)
    object_key = serializers.CharField(max_length=36, required=False, default='')
    avatars = AvatarIngestDataSerializer(many=True)


class ParcelIngestSerializer(serializers.Serializer):
    region_name = serializers.CharField(max_length=255)
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, default='')
    owner_name = serializers.CharField(max_length=100, required=False, default='')
    coordinates = serializers.CharField(max_length=100, required=False, default='')