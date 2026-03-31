import uuid
from django.db import models
from django.conf import settings


class Region(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, db_index=True)
    region_uuid = models.CharField(max_length=36, blank=True, default='')
    map_image_url = models.URLField(blank=True, default='')
    first_seen = models.DateTimeField(auto_now_add=True)
    last_scanned = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'regions'

    def __str__(self):
        return self.name


class Parcel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='parcels')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    owner_name = models.CharField(max_length=100, blank=True, default='')
    coordinates = models.CharField(max_length=100, blank=True, default='')
    scanned_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'parcels'

    def __str__(self):
        return f'{self.name} @ {self.region.name}'


class ScanSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='scan_sessions')
    scanned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='scan_sessions',
    )
    object_key = models.CharField(max_length=36, blank=True, default='')
    avatar_count = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'scan_sessions'
        ordering = ['-timestamp']

    def __str__(self):
        return f'Scan @ {self.region.name} ({self.avatar_count} avatars)'


class Avatar(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan_session = models.ForeignKey(ScanSession, on_delete=models.CASCADE, related_name='avatars')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='avatars')
    name = models.CharField(max_length=100, db_index=True)
    avatar_uuid = models.CharField(max_length=36, blank=True, default='')
    distance = models.FloatField(default=0.0)
    is_sitting = models.BooleanField(default=False)
    scripted_attachments_count = models.PositiveIntegerField(default=0)
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'avatars'
        ordering = ['-detected_at']

    def __str__(self):
        return f'{self.name} @ {self.region.name}'


class Attachment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    avatar = models.ForeignKey(Avatar, on_delete=models.CASCADE, related_name='attachments')
    name = models.CharField(max_length=255)
    detected_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attachments'

    def __str__(self):
        return f'{self.name} on {self.avatar.name}'