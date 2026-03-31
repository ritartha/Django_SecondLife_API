from django.urls import path
from . import views

urlpatterns = [
    # LSL ingest (API key auth)
    path('region/', views.ingest_region, name='ingest_region'),
    path('avatars/', views.ingest_avatars, name='ingest_avatars'),
    path('parcels/', views.ingest_parcel, name='ingest_parcel'),
    # Dashboard (JWT auth)
    path('regions/', views.RegionListView.as_view(), name='region_list'),
    path('sessions/', views.ScanSessionListView.as_view(), name='scan_session_list'),
]