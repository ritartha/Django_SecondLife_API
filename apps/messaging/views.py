from django.conf import settings
from django.utils import timezone
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import MessageLog
from .serializers import SendMessageSerializer, MessageLogSerializer, PendingMessageSerializer


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request):
    ser = SendMessageSerializer(data=request.data)
    ser.is_valid(raise_exception=True)
    msg = MessageLog.objects.create(sender=request.user, **ser.validated_data)
    return Response({'message': 'Message queued.', 'message_id': str(msg.id)}, status=status.HTTP_201_CREATED)


class MessageHistoryView(generics.ListAPIView):
    serializer_class = MessageLogSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MessageLog.objects.filter(sender=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def pending_messages(request):
    if request.META.get('HTTP_X_API_KEY', '') != settings.LSL_API_KEY:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    msgs = MessageLog.objects.filter(status=MessageLog.Status.PENDING).order_by('created_at')[:10]
    data = PendingMessageSerializer(msgs, many=True).data
    MessageLog.objects.filter(id__in=[m.id for m in msgs]).update(status=MessageLog.Status.SENT, sent_at=timezone.now())
    return Response({'pending_messages': data})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def confirm_delivery(request):
    if request.META.get('HTTP_X_API_KEY', '') != settings.LSL_API_KEY:
        return Response({'error': 'Unauthorized'}, status=status.HTTP_403_FORBIDDEN)

    mid = request.data.get('message_id')
    del_status = request.data.get('status', 'delivered')
    error = request.data.get('error', '')

    try:
        msg = MessageLog.objects.get(id=mid)
        msg.status = MessageLog.Status.DELIVERED if del_status == 'delivered' else MessageLog.Status.FAILED
        msg.error_message = error
        msg.save()
        return Response({'message': 'Status updated.'})
    except MessageLog.DoesNotExist:
        return Response({'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)