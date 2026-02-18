from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from apps.residents.models import Resident

class MapView(LoginRequiredMixin, TemplateView):
    template_name = 'gis/map.html'

class ResidentGeoJSONView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        # Filter residents with valid coordinates
        residents = Resident.objects.filter(
            latitude__isnull=False, 
            longitude__isnull=False,
            is_active=True
        ).values(
            'id', 'first_name', 'last_name', 'latitude', 'longitude', 'purok', 'address'
        )
        
        features = []
        for resident in residents:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [resident['longitude'], resident['latitude']]
                },
                'properties': {
                    'id': resident['id'],
                    'name': f"{resident['first_name']} {resident['last_name']}",
                    'purok': resident['purok'],
                    'address': resident['address'],
                }
            })
            
        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }
        
        return JsonResponse(geojson)
