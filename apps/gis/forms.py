from django import forms
from .models import EmergencyService

class EmergencyServiceForm(forms.ModelForm):
    class Meta:
        model = EmergencyService
        fields = [
            'name', 'service_type', 'description', 'address', 
            'contact_number', 'icon_emoji', 'latitude', 'longitude', 'is_active'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional details about this location'}),
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Full address...'}),
            'latitude': forms.NumberInput(attrs={'step': 'any', 'id': 'id_latitude'}),
            'longitude': forms.NumberInput(attrs={'step': 'any', 'id': 'id_longitude'}),
        }

    def clean_latitude(self):
        lat = self.cleaned_data.get('latitude')
        if lat < -90 or lat > 90:
            raise forms.ValidationError("Latitude must be between -90 and 90.")
        return lat

    def clean_longitude(self):
        lon = self.cleaned_data.get('longitude')
        if lon < -180 or lon > 180:
            raise forms.ValidationError("Longitude must be between -180 and 180.")
        return lon
