"""Appointment scheduling for a single eye clinic."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone

from clinic.models import ClinicConfiguration
from clinic.services import next_identifier


class Appointment(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        CONFIRMED = "confirmed", "Confirmed"
        CHECKED_IN = "checked_in", "Checked in"
        IN_CONSULTATION = "in_consultation", "In consultation"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"
        NO_SHOW = "no_show", "No show"

    class AppointmentType(models.TextChoices):
        GENERAL_EYE_EXAM = "eye_exam", "General eye examination"
        CONSULTATION = "consultation", "Eye consultation"
        REFRACTION = "refraction", "Refraction"
        GLASSES_REVIEW = "glasses_review", "Glasses review"
        FOLLOW_UP = "follow_up", "Follow-up"
        CONTACT_LENS_REVIEW = "contact_lens_review", "Contact lens review"
        EMERGENCY = "emergency", "Emergency"
        OTHER = "other", "Other"

    reference = models.CharField(max_length=24, unique=True, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="appointments")
    appointment_date = models.DateField(db_index=True)
    appointment_time = models.TimeField()
    practitioner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="practitioner_appointments")
    appointment_type = models.CharField(max_length=24, choices=AppointmentType.choices, default=AppointmentType.GENERAL_EYE_EXAM)
    reason = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SCHEDULED, db_index=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="created_appointments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]
        indexes = [models.Index(fields=["appointment_date", "status"])]
        constraints = [models.UniqueConstraint(fields=["practitioner", "appointment_date", "appointment_time"], condition=~models.Q(status="cancelled") & models.Q(practitioner__isnull=False), name="appointment_unique_active_practitioner_slot")]

    def __str__(self):
        return f"{self.reference} · {self.patient.full_name}"

    def clean(self):
        if self.appointment_date and self.appointment_date < timezone.localdate():
            raise ValidationError({"appointment_date": "Appointments cannot be scheduled in the past."})
        if self.practitioner and not self.practitioner.is_clinician:
            raise ValidationError({"practitioner": "The assigned practitioner must be a clinician."})

    def save(self, *args, **kwargs):
        if self.reference:
            return super().save(*args, **kwargs)
        with transaction.atomic():
            clinic = ClinicConfiguration.objects.select_for_update().filter(is_active=True).first()
            prefix = clinic.appointment_number_prefix if clinic else "APT"
            self.reference = next_identifier(key="appointment", prefix=prefix)
            return super().save(*args, **kwargs)
