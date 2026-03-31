from rest_framework import serializers
from .models import DiscordWebhookConfig


class DiscordWebhookConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordWebhookConfig
        fields = ['id', 'webhook_url', 'is_active', 'notify_new_avatar', 'notify_specific_avatars', 'created_at']
        read_only_fields = ['id', 'created_at']