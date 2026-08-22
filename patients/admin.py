from django.contrib import admin

from .models import Patient, PatientMedicalHistory


class PatientMedicalHistoryInline(admin.StackedInline):
    model = PatientMedicalHistory
    extra = 0


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ("patient_number", "first_name", "last_name", "phone", "is_active")
    list_filter = ("gender", "is_active", "region")
    search_fields = ("patient_number", "first_name", "last_name", "phone", "national_id")
    readonly_fields = ("patient_number", "registered_at", "updated_at")
    inlines = (PatientMedicalHistoryInline,)
