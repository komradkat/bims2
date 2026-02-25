from django.contrib import admin
from .models import BlotterCase, Complainant, Respondent, Hearing


class ComplainantInline(admin.TabularInline):
    model = Complainant
    extra = 1
    autocomplete_fields = ["resident"]


class RespondentInline(admin.TabularInline):
    model = Respondent
    extra = 1
    autocomplete_fields = ["resident"]


class HearingInline(admin.TabularInline):
    model = Hearing
    extra = 1


@admin.register(BlotterCase)
class BlotterCaseAdmin(admin.ModelAdmin):
    list_display = [
        "case_number",
        "incident_type",
        "incident_date",
        "status",
        "created_at",
    ]
    list_filter = ["status", "incident_type", "incident_date"]
    search_fields = [
        "case_number",
        "narrative",
        "complainants__name",
        "respondents__name",
        "complainants__resident__last_name",
        "respondents__resident__last_name",
    ]
    inlines = [ComplainantInline, RespondentInline, HearingInline]
    readonly_fields = ["case_number", "created_at", "updated_at"]

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Hearing)
class HearingAdmin(admin.ModelAdmin):
    list_display = ["case", "scheduled_at", "status"]
    list_filter = ["status", "scheduled_at"]
    search_fields = ["case__case_number", "remarks"]
