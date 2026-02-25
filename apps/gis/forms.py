from django import forms
from .models import EmergencyService


class EmergencyServiceForm(forms.ModelForm):
    class Meta:
        model = EmergencyService
        fields = [
            "name",
            "service_type",
            "description",
            "address",
            "contact_number",
            "icon_emoji",
            "latitude",
            "longitude",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"class": "input input-bordered input-sm w-full"}
            ),
            "service_type": forms.Select(
                attrs={"class": "select select-bordered select-sm w-full"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered h-20 w-full",
                    "placeholder": "Optional details about this location",
                }
            ),
            "address": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered h-20 w-full",
                    "placeholder": "Full address...",
                }
            ),
            "contact_number": forms.TextInput(
                attrs={
                    "class": "input input-bordered input-sm w-full",
                    "placeholder": "Optional contact...",
                }
            ),
            "icon_emoji": forms.TextInput(
                attrs={
                    "class": "input input-bordered input-sm w-full",
                    "placeholder": "e.g. 🏫",
                }
            ),
            "latitude": forms.NumberInput(
                attrs={
                    "class": "input input-bordered input-sm w-full",
                    "step": "any",
                    "id": "id_latitude",
                }
            ),
            "longitude": forms.NumberInput(
                attrs={
                    "class": "input input-bordered input-sm w-full",
                    "step": "any",
                    "id": "id_longitude",
                }
            ),
        }

    def clean_latitude(self):
        lat = self.cleaned_data.get("latitude")
        if lat < -90 or lat > 90:
            raise forms.ValidationError("Latitude must be between -90 and 90.")
        return lat

    def clean_longitude(self):
        lon = self.cleaned_data.get("longitude")
        if lon < -180 or lon > 180:
            raise forms.ValidationError("Longitude must be between -180 and 180.")
        return lon
