from django import forms
from .models import BusinessPermit


class BusinessPermitForm(forms.ModelForm):
    class Meta:
        model = BusinessPermit
        fields = [
            "business_name",
            "owner_name",
            "owner_address",
            "address",
            "contact_number",
            "email",
            "dti_sec_number",
            "tin",
            "nature_of_business",
            "cedula_number",
            "cedula_date",
            "gross_sales",
            "clearance_fee",
            "or_number",
            "status",
        ]
        widgets = {
            "business_name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "As registered with DTI/SEC",
                }
            ),
            "owner_name": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Search or enter resident name...",
                }
            ),
            "owner_address": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Complete address",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "e.g. 123 Main St, Purok 1",
                }
            ),
            "contact_number": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "09123456789",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "email@example.com",
                }
            ),
            "dti_sec_number": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "e.g. DTI-123456789",
                }
            ),
            "tin": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "XXX-XXX-XXX-XXX",
                }
            ),
            "nature_of_business": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "e.g. Sari-Sari Store",
                }
            ),  # Or Select if we had choices
            "cedula_number": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "e.g. 12345678",
                }
            ),
            "cedula_date": forms.DateInput(
                attrs={"class": "input input-bordered w-full", "type": "date"}
            ),
            "gross_sales": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "0.00",
                    "step": "0.01",
                }
            ),
            "clearance_fee": forms.NumberInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "₱200-₱500",
                    "step": "0.01",
                }
            ),
            "or_number": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Official Receipt No.",
                }
            ),
            "status": forms.Select(attrs={"class": "select select-bordered w-full"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make certain fields required/optional as needed
        self.fields["email"].required = False
        self.fields["contact_number"].required = False
        self.fields["gross_sales"].required = False
        # status should only be editable in update view or if admin?
        # For now let's leave it as is, but maybe hide it in create view if we want default pending/active logic.
        # But the view logic handles default status.
