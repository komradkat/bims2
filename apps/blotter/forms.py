from django import forms
from .models import BlotterCase, Complainant, Respondent, Hearing


class BlotterCaseForm(forms.ModelForm):
    # Additional field for nature of complaint which maps to narrative in view
    nature_of_complaint = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={"class": "input input-bordered w-full"}),
    )
    incident_datetime = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(
            attrs={"class": "input input-bordered w-full", "type": "datetime-local"}
        ),
    )

    class Meta:
        model = BlotterCase
        fields = ["incident_type", "incident_location", "narrative", "status"]
        widgets = {
            "incident_location": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "e.g. Purok 4, Near Chapel",
                }
            ),
            "narrative": forms.Textarea(
                attrs={"class": "textarea textarea-bordered w-full", "rows": 4}
            ),
            "status": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "incident_type": forms.Select(
                attrs={"class": "select select-bordered w-full"}
            ),
        }


class ComplainantForm(forms.ModelForm):
    class Meta:
        model = Complainant
        fields = ["resident", "name", "address", "contact_number"]
        widgets = {
            "resident": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Full Name (if non-resident)",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Address (if non-resident)",
                }
            ),
            "contact_number": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "09XX-XXX-XXXX",
                }
            ),
        }


class RespondentForm(forms.ModelForm):
    class Meta:
        model = Respondent
        fields = ["resident", "name", "address", "contact_number"]
        widgets = {
            "resident": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Full Name (if non-resident)",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Address (if non-resident)",
                }
            ),
            "contact_number": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "09XX-XXX-XXXX",
                }
            ),
        }


class HearingForm(forms.ModelForm):
    class Meta:
        model = Hearing
        fields = ["scheduled_at", "status", "remarks"]
        widgets = {
            "scheduled_at": forms.DateTimeInput(
                attrs={"class": "input input-bordered w-full", "type": "datetime-local"}
            ),
            "status": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "remarks": forms.Textarea(
                attrs={"class": "textarea textarea-bordered w-full", "rows": 2}
            ),
        }
