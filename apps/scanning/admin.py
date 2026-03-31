from django.contrib import admin
from .models import Region, Parcel, ScanSession, Avatar, Attachment


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ('name', 'region_uuid', 'last_scanned')
    search_fields = ('name',)


@admin.register(Parcel)
class ParcelAdmin(admin.ModelAdmin):
    list_display = ('name', 'region', 'owner_name', 'scanned_at')
    list_filter = ('region',)


@admin.register(ScanSession)
class ScanSessionAdmin(admin.ModelAdmin):
    list_display = ('region', 'avatar_count', 'timestamp')
    list_filter = ('region',)


@admin.register(Avatar)
class AvatarAdmin(admin.ModelAdmin):
    list_display = ('name', 'avatar_uuid', 'region', 'distance', 'is_sitting', 'detected_at')
    list_filter = ('region', 'is_sitting')
    search_fields = ('name',)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'avatar', 'detected_at')