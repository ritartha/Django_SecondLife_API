import logging
import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def send_discord_embed(webhook_url: str, embed: dict):
    try:
        requests.post(webhook_url, json={'embeds': [embed]}, timeout=10)
    except Exception as e:
        logger.error(f'Discord webhook error: {e}')


def send_scan_to_discord(region_name: str, avatar_names: list):
    from .models import DiscordWebhookConfig

    ts = timezone.now().isoformat()

    embed = {
        'title': '🔍 Avatar Scan Report',
        'color': 0x00ff88,
        'fields': [
            {'name': '🌐 Region', 'value': region_name, 'inline': True},
            {'name': '👥 Count', 'value': str(len(avatar_names)), 'inline': True},
            {'name': '📋 Avatars', 'value': '\n'.join(avatar_names[:25]) or 'None', 'inline': False},
        ],
        'timestamp': ts,
        'footer': {'text': 'SL Insight Dashboard'},
    }

    if settings.DISCORD_WEBHOOK_URL:
        send_discord_embed(settings.DISCORD_WEBHOOK_URL, embed)

    for cfg in DiscordWebhookConfig.objects.filter(is_active=True):
        watched = cfg.watched_avatars
        matched = [n for n in avatar_names if n in watched]
        if matched:
            alert = {
                'title': '🚨 Watched Avatar Alert!',
                'color': 0xff0044,
                'fields': [
                    {'name': '🌐 Region', 'value': region_name, 'inline': True},
                    {'name': '👤 Detected', 'value': '\n'.join(matched), 'inline': False},
                ],
                'timestamp': ts,
                'footer': {'text': 'SL Insight Dashboard'},
            }
            send_discord_embed(cfg.webhook_url, alert)
        elif cfg.notify_new_avatar:
            send_discord_embed(cfg.webhook_url, embed)