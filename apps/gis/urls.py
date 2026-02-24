from django.urls import path
from . import views

app_name = 'gis'

urlpatterns = [
    path('map/', views.MapView.as_view(), name='map'),
    
    # Blip Management
    path('blips/add/', views.BlipCreateView.as_view(), name='blip_add'),
    path('blips/<int:pk>/edit/', views.BlipUpdateView.as_view(), name='blip_edit'),
    path('blips/<int:pk>/delete/', views.BlipDeleteView.as_view(), name='blip_delete'),

    path('api/residents/', views.ResidentGeoJSONView.as_view(), name='resident_geojson'),
    path('api/emergency/', views.EmergencyServiceGeoJSONView.as_view(), name='emergency_service_geojson'),
]
