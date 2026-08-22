from django.contrib import admin

from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ("visit_number", "patient", "visit_type", "practitioner", "status", "checked_in_at")
    list_filter = ("status", "visit_type", "checked_in_at")
    search_fields = ("visit_number", "patient__patient_number", "patient__first_name", "patient__last_name")
