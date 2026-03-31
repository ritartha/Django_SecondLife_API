from django.contrib import admin
from .models import MessageLog


@admin.register(MessageLog)
class MessageLogAdmin(admin.ModelAdmin):
    list_display = ('sender', 'target_name', 'status', 'created_at', 'sent_at')
    list_filter = ('status',)
    search_fields = ('target_name',)