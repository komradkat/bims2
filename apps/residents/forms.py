# Residents forms
from django import forms
from django.core.exceptions import ValidationError
from .models import Resident
from datetime import date


class ResidentForm(forms.ModelForm):
    """
    Form for creating and editing resident profiles.
    """
    
    class Meta:
        model = Resident
        fields = [
            # Personal Information
            'first_name', 'middle_name', 'last_name', 'suffix',
            'date_of_birth', 'sex', 'civil_status', 'citizenship',
            'place_of_birth', 'religion', 'blood_type',
            # Education & Employment
            'educational_attainment', 'employment_status', 'occupation',
            # Contact Information
            'mobile_number', 'email',
            'philhealth_no', 'sss_gsis_no', 'tin_no',
            'emergency_contact_name', 'emergency_contact_number',
            # Residence Information
            'purok', 'address', 'years_of_residency',
            'is_household_head', 'household_head', 'relationship_to_head',
            # Sectoral Information
            'is_senior_citizen', 'is_pwd', 'disability_type',
            'is_solo_parent', 'is_4ps', 'is_indigent',
            'is_voter', 'precinct_number',
            # Photo
            'photo',
        ]
        
        widgets = {
            # Personal Information
            'first_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. Juan'
            }),
            'middle_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. Tamad'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. Dela Cruz'
            }),
            'suffix': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. Jr., Sr., III'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'input input-bordered w-full',
                'type': 'date'
            }),
            'sex': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'civil_status': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'citizenship': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'value': 'Filipino'
            }),
            'place_of_birth': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'City/Municipality'
            }),
            'religion': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. Roman Catholic'
            }),
            'blood_type': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            
            # Education & Employment
            'educational_attainment': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'employment_status': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'occupation': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. Tricycle Driver'
            }),
            
            # Contact Information
            'mobile_number': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '0917-123-4567'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'juan@example.com'
            }),
            'philhealth_no': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'XX-XXXXXXXXX-X'
            }),
            'sss_gsis_no': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'XX-XXXXXXX-X'
            }),
            'tin_no': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'XXX-XXX-XXX-XXX'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'Contact Person'
            }),
            'emergency_contact_number': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': '09XX-XXX-XXXX'
            }),
            
            # Residence Information
            'purok': forms.Select(attrs={'class': 'select select-bordered w-full'}),
            'address': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. 123 Kalye Serye'
            }),
            'years_of_residency': forms.NumberInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. 10',
                'min': '0'
            }),
            'is_household_head': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-primary',
                'x-model': 'isHouseholdHead'
            }),
            'household_head': forms.Select(attrs={
                'class': 'select select-bordered w-full',
                'x-show': '!isHouseholdHead'
            }),
            'relationship_to_head': forms.TextInput(attrs={
                'class': 'input input-bordered w-full',
                'placeholder': 'e.g. Spouse, Son, Daughter',
                'x-show': '!isHouseholdHead'
            }),
            
            # Sectoral Information
            'is_senior_citizen': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-sm'}),
            'is_pwd': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-sm checkbox-secondary',
                'x-model': 'isPWD'
            }),
            'disability_type': forms.TextInput(attrs={
                'class': 'input input-sm input-bordered w-full',
                'placeholder': 'e.g. Visual, Orthopedic, Psychosocial',
                'x-show': 'isPWD'
            }),
            'is_solo_parent': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-sm'}),
            'is_4ps': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-sm'}),
            'is_indigent': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-sm'}),
            'is_voter': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-sm',
                'x-model': 'isVoter'
            }),
            'precinct_number': forms.TextInput(attrs={
                'class': 'input input-sm input-bordered w-full',
                'placeholder': 'e.g. 0123A',
                'x-show': 'isVoter'
            }),
            
            # Photo
            'photo': forms.FileInput(attrs={
                'class': 'file-input file-input-bordered w-full',
                'accept': 'image/*'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make certain fields required
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['date_of_birth'].required = True
        self.fields['sex'].required = True
        self.fields['civil_status'].required = True
        self.fields['purok'].required = True
        self.fields['address'].required = True
        
        # Populate purok choices dynamically
        puroks = Resident.objects.values_list('purok', flat=True).distinct().order_by('purok')
        purok_choices = [('', 'Select Purok')] + [(p, p) for p in puroks if p]
        # Add common puroks if not in database
        common_puroks = ['Purok 1', 'Purok 2', 'Purok 3', 'Sitio Kawayan']
        for purok in common_puroks:
            if purok not in [p for _, p in purok_choices]:
                purok_choices.append((purok, purok))
        self.fields['purok'].widget = forms.Select(
            attrs={'class': 'select select-bordered w-full'},
            choices=sorted(purok_choices, key=lambda x: x[1] if x[1] else '')
        )
        
        # Populate household head choices (only household heads)
        household_heads = Resident.objects.filter(
            is_household_head=True,
            is_active=True
        ).order_by('last_name', 'first_name')
        
        household_head_choices = [('', 'Select Household Head')] + [
            (h.id, h.full_name) for h in household_heads
        ]
        self.fields['household_head'].widget.choices = household_head_choices
        self.fields['household_head'].required = False
    
    def clean(self):
        cleaned_data = super().clean()
        is_household_head = cleaned_data.get('is_household_head')
        household_head = cleaned_data.get('household_head')
        relationship_to_head = cleaned_data.get('relationship_to_head')
        
        # Validate household head logic
        if not is_household_head:
            if not household_head:
                raise ValidationError({
                    'household_head': 'Please select a household head if this person is not the head.'
                })
            if not relationship_to_head:
                raise ValidationError({
                    'relationship_to_head': 'Please specify the relationship to the household head.'
                })
        else:
            # If is household head, clear household_head and relationship
            cleaned_data['household_head'] = None
            cleaned_data['relationship_to_head'] = ''
        
        # Validate age for senior citizen
        date_of_birth = cleaned_data.get('date_of_birth')
        is_senior_citizen = cleaned_data.get('is_senior_citizen')
        
        if date_of_birth and is_senior_citizen:
            today = date.today()
            age = today.year - date_of_birth.year - (
                (today.month, today.day) < (date_of_birth.month, date_of_birth.day)
            )
            if age < 60:
                raise ValidationError({
                    'is_senior_citizen': 'Person must be 60 years or older to be marked as Senior Citizen.'
                })
        
        # Validate PWD disability type
        is_pwd = cleaned_data.get('is_pwd')
        disability_type = cleaned_data.get('disability_type')
        
        if is_pwd and not disability_type:
            raise ValidationError({
                'disability_type': 'Please specify the disability type for PWD.'
            })
        
        # Validate voter precinct
        is_voter = cleaned_data.get('is_voter')
        precinct_number = cleaned_data.get('precinct_number')
        
        if is_voter and not precinct_number:
            raise ValidationError({
                'precinct_number': 'Please provide the precinct number for registered voters.'
            })
        
        return cleaned_data

class HouseholdHeadForm(ResidentForm):
    """Form specifically for the household head."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_household_head'].initial = True
        self.fields['is_household_head'].widget = forms.HiddenInput()
        self.fields['household_head'].widget = forms.HiddenInput()
        self.fields['relationship_to_head'].widget = forms.HiddenInput()

class HouseholdMemberForm(ResidentForm):
    """Form specifically for household members."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_household_head'].initial = False
        self.fields['is_household_head'].widget = forms.HiddenInput()
        self.fields['household_head'].widget = forms.HiddenInput()
        self.fields['relationship_to_head'].required = True
        
        # In bulk registration, address and purok are usually shared
        # but we keep them for flexibility, maybe with smaller widgets
        self.fields['purok'].widget.attrs.update({'class': 'select select-sm select-bordered w-full'})
        self.fields['address'].widget.attrs.update({'class': 'input input-sm input-bordered w-full'})

from django.forms import inlineformset_factory

# Since members are linked to the head via the 'household_head' foreign key
HouseholdMemberFormSet = inlineformset_factory(
    Resident, 
    Resident,
    form=HouseholdMemberForm,
    fk_name='household_head',
    extra=1,
    can_delete=True
)
