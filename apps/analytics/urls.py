from django.urls import path
from . import views

urlpatterns = [
    path('visitors/', views.frequent_visitors, name='frequent_visitors'),
    path('peak-hours/', views.peak_hours, name='peak_hours'),
    path('overview/', views.overview, name='overview'),
]