from rest_framework import serializers
from .models import MessageLog


class SendMessageSerializer(serializers.Serializer):
    target_uuid = serializers.CharField(max_length=36)
    target_name = serializers.CharField(max_length=100)
    message = serializers.CharField(max_length=1024)


class MessageLogSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.sl_avatar_name', read_only=True)

    class Meta:
        model = MessageLog
        fields = [
            'id', 'sender_name', 'target_uuid', 'target_name',
            'message', 'status', 'created_at', 'sent_at', 'error_message',
        ]


class PendingMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = ['id', 'target_uuid', 'target_name', 'message']