"""Central authentication and role definitions for clinic staff."""

from django.contrib.auth.models import AbstractUser
from django.db import models


class StaffRole(models.TextChoices):
    SYSTEM_ADMIN = "system_admin", "System Administrator"
    CLINIC_ADMIN = "clinic_admin", "Clinic Administrator"
    OPTOMETRIST = "optometrist", "Optometrist"
    OPHTHALMOLOGIST = "ophthalmologist", "Ophthalmologist"
    NURSE = "nurse", "Nurse"
    RECEPTIONIST = "receptionist", "Receptionist"
    OPTICIAN = "optician", "Optician"
    PHARMACIST = "pharmacist", "Pharmacist / Dispensing Staff"
    ACCOUNTANT = "accountant", "Accountant / Cashier"


class CustomUser(AbstractUser):
    """One authenticated identity per staff member."""

    role = models.CharField(max_length=24, choices=StaffRole.choices, default=StaffRole.RECEPTIONIST, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to="staff/profiles/", blank=True, null=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_clinician(self):
        return self.role in {StaffRole.OPTOMETRIST, StaffRole.OPHTHALMOLOGIST}

    @property
    def is_clinic_administrator(self):
        return self.is_superuser or self.role in {StaffRole.SYSTEM_ADMIN, StaffRole.CLINIC_ADMIN}
