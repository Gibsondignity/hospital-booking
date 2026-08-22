"""Clinic configuration, staff profiles and privacy-conscious audit events."""

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from accounts.models import StaffRole


class ClinicConfiguration(models.Model):
    name = models.CharField(max_length=180)
    logo = models.ImageField(upload_to="clinic/branding/", blank=True, null=True)
    address = models.CharField(max_length=255)
    region = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20)
    alternative_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    currency = models.CharField(max_length=3, default="GHS")
    timezone = models.CharField(max_length=50, default="Africa/Accra")
    receipt_prefix = models.CharField(max_length=12, default="RCP")
    patient_number_prefix = models.CharField(max_length=12, default="EC")
    appointment_number_prefix = models.CharField(max_length=12, default="APT")
    visit_number_prefix = models.CharField(max_length=12, default="VIS")
    appointment_duration_minutes = models.PositiveSmallIntegerField(default=30)
    default_prescription_validity_days = models.PositiveSmallIntegerField(default=365)
    sms_sender_name = models.CharField(max_length=30, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Clinic configuration"
        verbose_name_plural = "Clinic configuration"
        constraints = [models.UniqueConstraint(fields=["is_active"], condition=models.Q(is_active=True), name="clinic_single_active_configuration")]

    def __str__(self):
        return self.name

    @classmethod
    def active(cls):
        return cls.objects.filter(is_active=True).first()


class StaffProfile(models.Model):
    class EmploymentStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_LEAVE = "on_leave", "On leave"
        SUSPENDED = "suspended", "Suspended"
        TERMINATED = "terminated", "Terminated"

    staff_id = models.CharField(max_length=24, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="staff_profile")
    role = models.CharField(max_length=24, choices=StaffRole.choices, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    professional_title = models.CharField(max_length=80, blank=True)
    registration_number = models.CharField(max_length=80, blank=True)
    department = models.CharField(max_length=80, blank=True)
    employment_status = models.CharField(max_length=16, choices=EmploymentStatus.choices, default=EmploymentStatus.ACTIVE)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateField(default=timezone.localdate)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["user__first_name", "user__last_name", "staff_id"]

    def __str__(self):
        return f"{self.staff_id} · {self.user}"

    def clean(self):
        if self.role in {StaffRole.OPTOMETRIST, StaffRole.OPHTHALMOLOGIST} and not self.registration_number:
            raise ValidationError({"registration_number": "Clinical practitioners need a registration number."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
        if self.user.role != self.role:
            self.user.role = self.role
            self.user.save(update_fields=["role"])
        role_group_names = set(StaffRole.values)
        self.user.groups.remove(*self.user.groups.filter(name__in=role_group_names))
        group, _ = Group.objects.get_or_create(name=self.role)
        self.user.groups.add(group)


class IdentifierSequence(models.Model):
    """Independent business-number counters; never expose database primary keys."""

    key = models.CharField(max_length=32, unique=True)
    next_value = models.PositiveBigIntegerField(default=1)

    def __str__(self):
        return f"{self.key}: {self.next_value}"


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
    action = models.CharField(max_length=80, db_index=True)
    resource_type = models.CharField(max_length=80, db_index=True)
    resource_id = models.CharField(max_length=80, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-timestamp"]
        permissions = [("view_clinic_audit", "Can view clinic audit history")]

    def __str__(self):
        return f"{self.action} · {self.resource_type} · {self.timestamp:%Y-%m-%d %H:%M}"
