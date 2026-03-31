from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
    path('api/scan/', include('apps.scanning.urls')),
    path('api/message/', include('apps.messaging.urls')),
    path('api/discord/', include('apps.discord_integration.urls')),
    path('api/analytics/', include('apps.analytics.urls')),
]