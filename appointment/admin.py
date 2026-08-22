from django.contrib import admin

from .models import Appointment


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("reference", "patient", "appointment_date", "appointment_time", "practitioner", "status")
    list_filter = ("status", "appointment_type", "appointment_date")
    search_fields = ("reference", "patient__patient_number", "patient__first_name", "patient__last_name")
