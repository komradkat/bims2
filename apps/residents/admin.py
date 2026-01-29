# Residents admin
from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import Resident, HouseholdMember


@admin.register(Resident)
class ResidentAdmin(SimpleHistoryAdmin):
    """Admin configuration for Resident model with history tracking"""
    
    list_display = [
        'get_full_name',
        'age',
        'sex',
        'purok',
        'get_sectors_display',
        'is_household_head',
        'is_active',
        'created_at',
    ]
    
    list_filter = [
        'sex',
        'civil_status',
        'purok',
        'is_household_head',
        'is_senior_citizen',
        'is_pwd',
        'is_voter',
        'is_4ps',
        'is_active',
    ]
    
    search_fields = [
        'first_name',
        'middle_name',
        'last_name',
        'mobile_number',
        'email',
        'address',
    ]
    
    readonly_fields = ['created_at', 'updated_at', 'age']
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                ('first_name', 'middle_name', 'last_name', 'suffix'),
                ('date_of_birth', 'sex', 'civil_status'),
                ('citizenship', 'place_of_birth'),
                ('religion', 'blood_type'),
                'photo',
            )
        }),
        ('Education & Employment', {
            'fields': (
                ('educational_attainment', 'employment_status'),
                'occupation',
            )
        }),
        ('Contact Information', {
            'fields': (
                ('mobile_number', 'email'),
                ('philhealth_no', 'sss_gsis_no', 'tin_no'),
                ('emergency_contact_name', 'emergency_contact_number'),
            )
        }),
        ('Residence Information', {
            'fields': (
                ('purok', 'address'),
                'years_of_residency',
                ('is_household_head', 'household_head'),
                'relationship_to_head',
            )
        }),
        ('Sectoral Information', {
            'fields': (
                ('is_senior_citizen', 'is_pwd', 'disability_type'),
                ('is_solo_parent', 'is_4ps', 'is_indigent'),
                ('is_voter', 'precinct_number'),
            )
        }),
        ('Metadata', {
            'fields': (
                'is_active',
                ('created_at', 'updated_at'),
            ),
            'classes': ('collapse',),
        }),
    )
    
    def get_full_name(self, obj):
        return obj.full_name
    get_full_name.short_description = 'Full Name'
    get_full_name.admin_order_field = 'last_name'
    
    def get_sectors_display(self, obj):
        sectors = obj.sectors
        if not sectors:
            return '-'
        return ', '.join(sectors[:3]) + ('...' if len(sectors) > 3 else '')
    get_sectors_display.short_description = 'Sectors'


@admin.register(HouseholdMember)
class HouseholdMemberAdmin(SimpleHistoryAdmin):
    """Admin configuration for HouseholdMember model"""
    
    list_display = [
        'member',
        'household_head',
        'relationship',
        'created_at',
    ]
    
    list_filter = ['relationship']
    
    search_fields = [
        'member__first_name',
        'member__last_name',
        'household_head__first_name',
        'household_head__last_name',
    ]
    
    autocomplete_fields = ['household_head', 'member']
