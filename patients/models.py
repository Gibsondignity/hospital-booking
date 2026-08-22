"""Patient identity and basic medical history; clinical findings belong to visits."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from clinic.models import ClinicConfiguration
from clinic.services import next_identifier, normalise_ghana_phone


class PatientQuerySet(models.QuerySet):
    def search(self, query):
        query = query.strip()
        if not query:
            return self
        terms = query.split()
        filters = Q(patient_number__icontains=query) | Q(first_name__icontains=query) | Q(middle_name__icontains=query) | Q(last_name__icontains=query) | Q(phone__icontains=query) | Q(national_id__iexact=query)
        if len(terms) > 1:
            filters |= Q(first_name__icontains=terms[0], last_name__icontains=terms[-1])
        return self.filter(filters)


class Patient(models.Model):
    class Gender(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"
        OTHER = "other", "Other"

    patient_number = models.CharField(max_length=24, unique=True, editable=False)
    first_name = models.CharField(max_length=80, db_index=True)
    middle_name = models.CharField(max_length=80, blank=True)
    last_name = models.CharField(max_length=80, db_index=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=12, choices=Gender.choices)
    phone = models.CharField(max_length=20, db_index=True)
    alternative_phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    national_id = models.CharField(max_length=32, blank=True, db_index=True)
    occupation = models.CharField(max_length=100, blank=True)
    photograph = models.ImageField(upload_to="patients/photos/", blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    region = models.CharField(max_length=100, blank=True)
    emergency_contact_name = models.CharField(max_length=120, blank=True)
    emergency_contact_relationship = models.CharField(max_length=60, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    registered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="registered_patients")
    is_active = models.BooleanField(default=True, db_index=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = PatientQuerySet.as_manager()

    class Meta:
        ordering = ["last_name", "first_name"]
        indexes = [models.Index(fields=["last_name", "first_name", "date_of_birth"])]
        constraints = [models.UniqueConstraint(fields=["national_id"], condition=~Q(national_id=""), name="patients_unique_nonempty_national_id")]

    def __str__(self):
        return f"{self.patient_number} · {self.full_name}"

    @property
    def full_name(self):
        return " ".join(part for part in [self.first_name, self.middle_name, self.last_name] if part)

    @property
    def age(self):
        today = timezone.localdate()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

    def get_absolute_url(self):
        return reverse("patients:detail", kwargs={"pk": self.pk})

    def clean(self):
        if self.date_of_birth and self.date_of_birth > timezone.localdate():
            raise ValidationError({"date_of_birth": "Date of birth cannot be in the future."})
        if self.phone:
            self.phone = normalise_ghana_phone(self.phone)
        if self.alternative_phone:
            self.alternative_phone = normalise_ghana_phone(self.alternative_phone)

    def save(self, *args, **kwargs):
        if self.patient_number:
            return super().save(*args, **kwargs)
        with transaction.atomic():
            clinic = ClinicConfiguration.objects.select_for_update().filter(is_active=True).first()
            prefix = clinic.patient_number_prefix if clinic else "EC"
            self.patient_number = next_identifier(key="patient", prefix=prefix)
            return super().save(*args, **kwargs)

    def possible_duplicates(self):
        filters = Q(phone=self.phone) | Q(first_name__iexact=self.first_name, last_name__iexact=self.last_name, date_of_birth=self.date_of_birth)
        if self.national_id:
            filters |= Q(national_id__iexact=self.national_id)
        return type(self).objects.filter(filters).exclude(pk=self.pk)


class PatientMedicalHistory(models.Model):
    patient = models.OneToOneField(Patient, on_delete=models.CASCADE, related_name="medical_history")
    allergies = models.TextField(blank=True)
    existing_conditions = models.TextField(blank=True)
    current_medications = models.TextField(blank=True)
    has_diabetes = models.BooleanField(default=False)
    has_hypertension = models.BooleanField(default=False)
    previous_eye_surgery = models.TextField(blank=True)
    family_eye_disease_history = models.TextField(blank=True)
    other_notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Patient medical histories"
        permissions = [("view_sensitive_history", "Can view sensitive patient medical history")]

    def __str__(self):
        return f"Medical history · {self.patient.patient_number}"
