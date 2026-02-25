from django import forms
from .models import Certificate


class CertificateIssueForm(forms.ModelForm):
    class Meta:
        model = Certificate
        fields = ["resident", "certificate_type", "purpose", "or_number"]
        widgets = {
            "resident": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "certificate_type": forms.Select(
                attrs={"class": "select select-bordered w-full"}
            ),
            "purpose": forms.Textarea(
                attrs={
                    "class": "textarea textarea-bordered w-full",
                    "rows": 2,
                    "placeholder": "e.g. Scholarship, Employment, Travel",
                }
            ),
            "or_number": forms.TextInput(
                attrs={
                    "class": "input input-bordered w-full",
                    "placeholder": "Optional Receipt No.",
                }
            ),
        }
