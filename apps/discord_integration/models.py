import uuid
from django.db import models
from django.conf import settings


class DiscordWebhookConfig(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='discord_config')
    webhook_url = models.URLField()
    is_active = models.BooleanField(default=True)
    notify_new_avatar = models.BooleanField(default=True)
    notify_specific_avatars = models.TextField(blank=True, default='', help_text='Comma-separated names')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'discord_webhook_configs'

    def __str__(self):
        return f'Discord config for {self.user.sl_avatar_name}'

    @property
    def watched_avatars(self):
        if not self.notify_specific_avatars:
            return []
        return [n.strip() for n in self.notify_specific_avatars.split(',') if n.strip()]