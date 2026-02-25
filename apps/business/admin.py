from django.contrib import admin
from .models import BusinessPermit, BusinessClearance
from simple_history.admin import SimpleHistoryAdmin


@admin.register(BusinessPermit)
class BusinessPermitAdmin(SimpleHistoryAdmin):
    list_display = (
        "business_name",
        "permit_number",
        "owner_name",
        "status",
        "expiration_date",
        "issued_date",
    )
    list_filter = ("status", "issued_date", "expiration_date")
    search_fields = ("business_name", "permit_number", "owner_name", "tin")
    date_hierarchy = "issued_date"
    readonly_fields = ("permit_number", "created_at", "updated_at")

    fieldsets = (
        (
            "Business Information",
            {
                "fields": (
                    ("business_name", "nature_of_business"),
                    ("owner_name", "contact_number"),
                    "address",
                    "owner_address",
                    "email",
                )
            },
        ),
        (
            "Registration & Legal",
            {
                "fields": (
                    ("permit_number", "dti_sec_number", "tin"),
                    ("cedula_number", "cedula_date"),
                )
            },
        ),
        ("Financials", {"fields": (("gross_sales", "clearance_fee", "or_number"),)}),
        (
            "Status & Validity",
            {"fields": (("issued_date", "expiration_date"), "status", "created_by")},
        ),
    )


@admin.register(BusinessClearance)
class BusinessClearanceAdmin(SimpleHistoryAdmin):
    list_display = ("permit", "or_number", "amount_paid", "issued_date", "issued_by")
    list_filter = ("issued_date", "issued_by")
    search_fields = ("permit__business_name", "or_number")
    date_hierarchy = "issued_date"
    readonly_fields = ("issued_date",)
