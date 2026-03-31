from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import DiscordWebhookConfig
from .serializers import DiscordWebhookConfigSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def configure_webhook(request):
    config, created = DiscordWebhookConfig.objects.update_or_create(
        user=request.user,
        defaults={
            'webhook_url': request.data.get('webhook_url', ''),
            'is_active': request.data.get('is_active', True),
            'notify_new_avatar': request.data.get('notify_new_avatar', True),
            'notify_specific_avatars': request.data.get('notify_specific_avatars', ''),
        },
    )
    return Response(DiscordWebhookConfigSerializer(config).data,
                    status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_config(request):
    try:
        config = DiscordWebhookConfig.objects.get(user=request.user)
        return Response(DiscordWebhookConfigSerializer(config).data)
    except DiscordWebhookConfig.DoesNotExist:
        return Response({'message': 'No Discord configuration found.'}, status=status.HTTP_404_NOT_FOUND)