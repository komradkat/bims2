from django.contrib import admin
from .models import Fee, OfficialReceipt
from simple_history.admin import SimpleHistoryAdmin

@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    list_display = ('name', 'default_amount', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name',)

@admin.register(OfficialReceipt)
class OfficialReceiptAdmin(SimpleHistoryAdmin):
    list_display = ('or_number', 'payor', 'amount', 'date', 'status', 'created_by')
    list_filter = ('status', 'date', 'created_by')
    search_fields = ('or_number', 'payor', 'particulars')
    date_hierarchy = 'date'
    readonly_fields = ('date',)
