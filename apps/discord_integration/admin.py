from django.contrib import admin
from .models import DiscordWebhookConfig


@admin.register(DiscordWebhookConfig)
class DiscordWebhookConfigAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'notify_new_avatar', 'created_at')
    list_filter = ('is_active',)