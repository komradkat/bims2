from django.urls import path
from . import views

app_name = 'gis'

urlpatterns = [
    path('map/', views.MapView.as_view(), name='map'),
    path('api/residents/', views.ResidentGeoJSONView.as_view(), name='resident_geojson'),
    path('api/emergency/', views.EmergencyServiceGeoJSONView.as_view(), name='emergency_service_geojson'),
]
