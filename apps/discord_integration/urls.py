from django.urls import path
from . import views

urlpatterns = [
    path('configure/', views.configure_webhook, name='discord_configure'),
    path('config/', views.get_config, name='discord_config'),
]