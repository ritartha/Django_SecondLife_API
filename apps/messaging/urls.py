from django.urls import path
from . import views

urlpatterns = [
    path('send/', views.send_message, name='send_message'),
    path('history/', views.MessageHistoryView.as_view(), name='message_history'),
    path('pending/', views.pending_messages, name='pending_messages'),
    path('confirm/', views.confirm_delivery, name='confirm_delivery'),
]