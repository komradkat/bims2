from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, LicenseKey, BarangayOfficial, BarangayInfo

@admin.register(BarangayInfo)
class BarangayInfoAdmin(admin.ModelAdmin):
    list_display = ('name', 'city_municipality', 'province', 'is_setup_complete')
    
    def has_add_permission(self, request):
        # Only allow one instance
        return not BarangayInfo.objects.exists()

@admin.register(BarangayOfficial)
class BarangayOfficialAdmin(admin.ModelAdmin):
    list_display = ('full_name_display', 'position', 'is_active', 'has_account', 'order')
    list_filter = ('position', 'is_active')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('order', 'position', 'last_name')
    
    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Name'
    
    def has_account(self, obj):
        return hasattr(obj, 'user_account') and obj.user_account is not None
    has_account.boolean = True
    has_account.short_description = 'Linked Account'

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'full_name_display', 'email', 'role', 'official_link', 'is_bootstrap', 'is_staff')
    list_filter = ('role', 'is_bootstrap', 'is_staff', 'is_active')
    
    fieldsets = UserAdmin.fieldsets + (
        ('BIMS Info', {'fields': ('role', 'barangay_position', 'official', 'is_bootstrap')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('BIMS Info', {'fields': ('role', 'barangay_position', 'official', 'is_bootstrap')}),
    )
    
    def full_name_display(self, obj):
        if obj.first_name or obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return "-"
    full_name_display.short_description = 'Full Name'
    
    def official_link(self, obj):
        if obj.official:
            return obj.official.full_name
        return format_html('<span style="color: grey;">(System User)</span>')
    official_link.short_description = 'Linked Official'


@admin.register(LicenseKey)
class LicenseKeyAdmin(admin.ModelAdmin):
    list_display = ('key_preview', 'tier', 'hardware_id_preview', 'is_active', 'expiry_date', 'issued_date', 'is_valid_status')
    list_filter = ('tier', 'is_active', 'issued_date')
    search_fields = ('key', 'hardware_id')
    readonly_fields = ('issued_date',)
    
    def key_preview(self, obj):
        """Show first 12 characters of key"""
        return f"{obj.key[:12]}..." if len(obj.key) > 12 else obj.key
    key_preview.short_description = 'License Key'
    
    def hardware_id_preview(self, obj):
        """Show first 16 characters of hardware ID"""
        if not obj.hardware_id:
            return "Not bound"
        return f"{obj.hardware_id[:16]}..." if len(obj.hardware_id) > 16 else obj.hardware_id
    hardware_id_preview.short_description = 'Hardware ID'
    
    def is_valid_status(self, obj):
        """Show if license is currently valid"""
        return "✓ Valid" if obj.is_valid() else "✗ Invalid"
    is_valid_status.short_description = 'Status'

