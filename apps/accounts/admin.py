from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, OTPRequest


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('sl_avatar_name', 'sl_uuid', 'is_verified', 'is_active', 'date_joined')
    list_filter = ('is_verified', 'is_active', 'is_staff')
    search_fields = ('sl_avatar_name', 'sl_uuid')
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('sl_avatar_name', 'password')}),
        ('SL Info', {'fields': ('sl_uuid', 'profile_image_url')}),
        ('Status', {'fields': ('is_verified', 'is_active', 'is_staff', 'is_superuser')}),
        ('Dates', {'fields': ('date_joined', 'last_seen')}),
        ('Permissions', {'fields': ('groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',), 'fields': ('sl_avatar_name', 'is_verified')}),
    )


@admin.register(OTPRequest)
class OTPRequestAdmin(admin.ModelAdmin):
    list_display = ('sl_avatar_name', 'otp_code', 'created_at', 'is_used', 'is_delivered')
    list_filter = ('is_used', 'is_delivered')
    search_fields = ('sl_avatar_name',)