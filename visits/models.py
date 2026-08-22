"""Actual clinic encounters, separate from scheduled appointments."""

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from clinic.models import ClinicConfiguration
from clinic.services import next_identifier


class Visit(models.Model):
    class Status(models.TextChoices):
        WAITING = "waiting", "Waiting"
        IN_CONSULTATION = "in_consultation", "In consultation"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class VisitType(models.TextChoices):
        APPOINTMENT = "appointment", "Scheduled appointment"
        WALK_IN = "walk_in", "Walk-in"
        FOLLOW_UP = "follow_up", "Follow-up"
        EMERGENCY = "emergency", "Emergency"

    visit_number = models.CharField(max_length=24, unique=True, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="visits")
    appointment = models.OneToOneField("appointment.Appointment", on_delete=models.SET_NULL, null=True, blank=True, related_name="visit")
    practitioner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="practitioner_visits")
    checked_in_at = models.DateTimeField(default=timezone.now, db_index=True)
    consultation_started_at = models.DateTimeField(null=True, blank=True)
    consultation_ended_at = models.DateTimeField(null=True, blank=True)
    visit_type = models.CharField(max_length=16, choices=VisitType.choices, default=VisitType.APPOINTMENT)
    chief_complaint = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.WAITING, db_index=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_visits")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["checked_in_at"]
        indexes = [models.Index(fields=["status", "checked_in_at"])]

    def __str__(self):
        return f"{self.visit_number} · {self.patient.full_name}"

    def save(self, *args, **kwargs):
        if self.visit_number:
            return super().save(*args, **kwargs)
        with transaction.atomic():
            clinic = ClinicConfiguration.objects.select_for_update().filter(is_active=True).first()
            prefix = clinic.visit_number_prefix if clinic else "VIS"
            self.visit_number = next_identifier(key="visit", prefix=prefix)
            return super().save(*args, **kwargs)
