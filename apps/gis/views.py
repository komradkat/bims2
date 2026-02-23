from django.views.generic import TemplateView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import NonBootstrapRequiredMixin
from django.views import View
from apps.residents.models import Resident
from apps.core.models import BarangayInfo
from .models import EmergencyService

class MapView(LoginRequiredMixin, NonBootstrapRequiredMixin, TemplateView):
    template_name = 'gis/map.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        info = BarangayInfo.objects.first()

        # Default: geographic center of the Philippines
        DEFAULT_LAT  = 12.8797
        DEFAULT_LNG  = 121.7740
        DEFAULT_ZOOM = 7

        if info and info.latitude and info.longitude:
            ctx['barangay_lat']  = info.latitude
            ctx['barangay_lng']  = info.longitude
            ctx['barangay_zoom'] = 15          # street-level when coords are set
            ctx['has_coords']    = True
        else:
            ctx['barangay_lat']  = DEFAULT_LAT
            ctx['barangay_lng']  = DEFAULT_LNG
            ctx['barangay_zoom'] = DEFAULT_ZOOM
            ctx['has_coords']    = False

        ctx['barangay_name'] = info.name if info else 'Barangay'
        return ctx


class ResidentGeoJSONView(LoginRequiredMixin, NonBootstrapRequiredMixin, View):
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


class EmergencyServiceGeoJSONView(LoginRequiredMixin, NonBootstrapRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = EmergencyService.objects.filter(is_active=True).values(
            'id', 'name', 'service_type', 'latitude', 'longitude', 'contact_number', 'address'
        )

        features = []
        for s in services:
            features.append({
                'type': 'Feature',
                'geometry': {
                    'type': 'Point',
                    'coordinates': [s['longitude'], s['latitude']]
                },
                'properties': {
                    'id': s['id'],
                    'name': s['name'],
                    'type': s['service_type'],
                    'contact': s['contact_number'],
                    'address': s['address'],
                }
            })

        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }

        return JsonResponse(geojson)
