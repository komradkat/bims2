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


from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages

# Existing imports ...

class BlipListView(LoginRequiredMixin, NonBootstrapRequiredMixin, ListView):
    model = EmergencyService
    template_name = 'gis/blip_list.html'
    context_object_name = 'blips'
    
    def get_queryset(self):
        return EmergencyService.objects.filter(is_active=True).order_by('service_type', 'name')

class BlipCreateView(LoginRequiredMixin, NonBootstrapRequiredMixin, CreateView):
    model = EmergencyService
    template_name = 'gis/blip_form.html'
    fields = ['name', 'service_type', 'description', 'address', 'contact_number', 'icon_emoji', 'latitude', 'longitude']
    success_url = reverse_lazy('gis:blip_list')
    
    def form_valid(self, form):
        messages.success(self.request, f"Blip '{form.instance.name}' created successfully.")
        return super().form_valid(form)

class BlipUpdateView(LoginRequiredMixin, NonBootstrapRequiredMixin, UpdateView):
    model = EmergencyService
    template_name = 'gis/blip_form.html'
    fields = ['name', 'service_type', 'description', 'address', 'contact_number', 'icon_emoji', 'latitude', 'longitude', 'is_active']
    success_url = reverse_lazy('gis:blip_list')

    def form_valid(self, form):
        messages.success(self.request, f"Blip '{form.instance.name}' updated successfully.")
        return super().form_valid(form)

class BlipDeleteView(LoginRequiredMixin, NonBootstrapRequiredMixin, DeleteView):
    model = EmergencyService
    template_name = 'gis/blip_confirm_delete.html'
    success_url = reverse_lazy('gis:blip_list')

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
