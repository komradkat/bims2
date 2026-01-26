from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

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
