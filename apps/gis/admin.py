from django.contrib import admin
from .models import EmergencyService

@admin.register(EmergencyService)
class EmergencyServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_type', 'is_active', 'latitude', 'longitude')
    list_filter = ('service_type', 'is_active')
    search_fields = ('name', 'description', 'address')
    readonly_fields = ('created_at', 'updated_at')
