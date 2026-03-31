import uuid
from django.db import models
from django.conf import settings


class MessageLog(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SENT = 'sent', 'Sent'
        DELIVERED = 'delivered', 'Delivered'
        FAILED = 'failed', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    target_uuid = models.CharField(max_length=36, db_index=True)
    target_name = models.CharField(max_length=100)
    message = models.TextField(max_length=1024)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, default='')

    class Meta:
        db_table = 'message_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.sender} → {self.target_name}: {self.status}'