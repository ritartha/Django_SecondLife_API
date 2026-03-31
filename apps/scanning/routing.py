from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/scan/$', consumers.ScanConsumer.as_asgi()),
    re_path(r'ws/scan/(?P<region_name>[\w\-\+%]+)/$', consumers.ScanConsumer.as_asgi()),
]