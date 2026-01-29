from django.contrib import admin
from .models import CertificateType, Certificate
from simple_history.admin import SimpleHistoryAdmin

@admin.register(CertificateType)
class CertificateTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_price', 'is_active', 'template_file')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Certificate)
class CertificateAdmin(SimpleHistoryAdmin):
    list_display = ('transaction_number', 'resident', 'certificate_type', 'status', 'issued_at')
    list_filter = ('status', 'certificate_type', 'issued_at')
    search_fields = ('transaction_number', 'resident__first_name', 'resident__last_name', 'or_number')
    date_hierarchy = 'created_at'
    readonly_fields = ('transaction_number', 'issued_by', 'issued_at')
