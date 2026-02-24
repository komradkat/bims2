from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.core.mixins import NonBootstrapRequiredMixin
from django.views import View
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.decorators import method_decorator

from apps.residents.models import Resident
from apps.core.models import BarangayInfo
from apps.core.decorators import tier_required
from .models import EmergencyService
from .forms import EmergencyServiceForm

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
        
        # Add Blip Management context
        license_tier = getattr(self.request, 'license', {}).get('tier', 'community')
        if license_tier == 'ultra':
            ctx['blips'] = EmergencyService.objects.all().order_by('service_type', 'name')
            ctx['form'] = EmergencyServiceForm(initial={'is_active': True})
            
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


@method_decorator(tier_required(['ultra']), name='dispatch')
class BlipCreateView(LoginRequiredMixin, NonBootstrapRequiredMixin, CreateView):
    model = EmergencyService
    form_class = EmergencyServiceForm
    template_name = 'gis/blip_form.html'
    success_url = reverse_lazy('gis:map')
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        info = BarangayInfo.objects.first()
        if info:
            ctx['barangay_lat'] = info.latitude
            ctx['barangay_lng'] = info.longitude
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f"Blip '{form.instance.name}' created successfully.")
        return super().form_valid(form)

@method_decorator(tier_required(['ultra']), name='dispatch')
class BlipUpdateView(LoginRequiredMixin, NonBootstrapRequiredMixin, UpdateView):
    model = EmergencyService
    form_class = EmergencyServiceForm
    template_name = 'gis/blip_form.html'
    success_url = reverse_lazy('gis:map')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        info = BarangayInfo.objects.first()
        if info:
            ctx['barangay_lat'] = info.latitude
            ctx['barangay_lng'] = info.longitude
        return ctx

    def form_valid(self, form):
        messages.success(self.request, f"Blip '{form.instance.name}' updated successfully.")
        return super().form_valid(form)

@method_decorator(tier_required(['ultra']), name='dispatch')
class BlipDeleteView(LoginRequiredMixin, NonBootstrapRequiredMixin, DeleteView):
    model = EmergencyService
    template_name = 'gis/blip_confirm_delete.html'
    success_url = reverse_lazy('gis:map')

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        messages.success(request, f"Blip '{obj.name}' deleted.")
        return super().delete(request, *args, **kwargs)


class EmergencyServiceGeoJSONView(LoginRequiredMixin, NonBootstrapRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        services = EmergencyService.objects.filter(is_active=True).values(
            'id', 'name', 'service_type', 'latitude', 'longitude', 'contact_number', 'address', 'description', 'icon_emoji'
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
                    'description': s['description'],
                    'icon': s['icon_emoji'],
                }
            })

        geojson = {
            'type': 'FeatureCollection',
            'features': features
        }

        return JsonResponse(geojson)
