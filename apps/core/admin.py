from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, LicenseKey

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'barangay_position', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('BIMS Info', {'fields': ('role', 'barangay_position')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('BIMS Info', {'fields': ('role', 'barangay_position')}),
    )


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

