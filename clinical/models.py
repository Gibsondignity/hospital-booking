"""Normalized visit-linked eye examination and spectacle prescription records."""

from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from clinic.models import ClinicConfiguration
from clinic.services import next_identifier

AXIS_VALIDATORS = [MinValueValidator(0), MaxValueValidator(180)]
PRESSURE_VALIDATORS = [MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("100.00"))]
PD_VALIDATORS = [MinValueValidator(Decimal("10.00")), MaxValueValidator(Decimal("100.00"))]
CUP_RATIO_VALIDATORS = [MinValueValidator(Decimal("0.00")), MaxValueValidator(Decimal("1.00"))]


class ClinicalExamination(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_PROGRESS = "in_progress", "In progress"
        FINALIZED = "finalized", "Finalized"

    class AffectedEye(models.TextChoices):
        RIGHT = "right", "OD · Right eye"
        LEFT = "left", "OS · Left eye"
        BOTH = "both", "OU · Both eyes"
        NOT_APPLICABLE = "not_applicable", "Not applicable"

    class ReferralUrgency(models.TextChoices):
        ROUTINE = "routine", "Routine"
        SOON = "soon", "Soon"
        URGENT = "urgent", "Urgent"
        EMERGENCY = "emergency", "Emergency"

    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="clinical_examinations")
    visit = models.OneToOneField("visits.Visit", on_delete=models.PROTECT, related_name="clinical_examination")
    practitioner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="clinical_examinations")
    examined_at = models.DateTimeField(default=timezone.now, db_index=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT, db_index=True)
    chief_complaint = models.TextField(blank=True)
    complaint_duration = models.CharField(max_length=100, blank=True)
    affected_eye = models.CharField(max_length=16, choices=AffectedEye.choices, default=AffectedEye.NOT_APPLICABLE)
    presenting_history = models.TextField(blank=True)
    previous_spectacle_use = models.TextField(blank=True)
    contact_lens_use = models.TextField(blank=True)
    previous_eye_condition = models.TextField(blank=True)
    previous_eye_surgery = models.TextField(blank=True)
    previous_eye_trauma = models.TextField(blank=True)
    current_eye_medication = models.TextField(blank=True)
    general_medication = models.TextField(blank=True)
    systemic_illness = models.TextField(blank=True)
    family_ocular_history = models.TextField(blank=True)
    additional_history = models.TextField(blank=True)
    clinical_assessment = models.TextField(blank=True)
    clinical_impression = models.TextField(blank=True)
    clinical_notes = models.TextField(blank=True)
    practitioner_comments = models.TextField(blank=True)
    referral_required = models.BooleanField(default=False)
    referred_to = models.CharField(max_length=180, blank=True)
    referral_facility = models.CharField(max_length=180, blank=True)
    referral_reason = models.TextField(blank=True)
    referral_urgency = models.CharField(max_length=16, choices=ReferralUrgency.choices, default=ReferralUrgency.ROUTINE)
    referral_notes = models.TextField(blank=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_clinical_examinations")
    updated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="updated_clinical_examinations")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-examined_at"]
        indexes = [models.Index(fields=["status", "examined_at"]), models.Index(fields=["practitioner", "examined_at"])]
        permissions = [
            ("finalize_examination", "Can finalize clinical examinations"),
            ("amend_finalized_examination", "Can amend finalized clinical examinations"),
            ("record_preconsult_observations", "Can record limited pre-consultation observations"),
        ]

    def __str__(self):
        return f"{self.visit.visit_number} · {self.patient.full_name}"

    def clean(self):
        errors = {}
        if self.visit_id and self.patient_id and self.visit.patient_id != self.patient_id:
            errors["patient"] = "The examination patient must match the visit patient."
        if self.practitioner_id and (not self.practitioner.is_clinician or not self.practitioner.is_active):
            errors["practitioner"] = "The practitioner must be an active optometrist or ophthalmologist."
        if self.referral_required and not self.referral_reason:
            errors["referral_reason"] = "A reason is required when requesting a referral."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if self.pk:
            existing_status = type(self).objects.filter(pk=self.pk).values_list("status", flat=True).first()
            if existing_status == self.Status.FINALIZED and not getattr(self, "_allow_finalized_amendment", False):
                raise ValidationError("Finalized examinations cannot be modified through standard workflows.")
        self.full_clean()
        return super().save(*args, **kwargs)


class VisualAcuity(models.Model):
    examination = models.OneToOneField(ClinicalExamination, on_delete=models.CASCADE, related_name="visual_acuity")
    od_distance_unaided = models.CharField(max_length=20, blank=True)
    od_distance_aided = models.CharField(max_length=20, blank=True)
    od_distance_pinhole = models.CharField(max_length=20, blank=True)
    od_near_unaided = models.CharField(max_length=20, blank=True)
    od_near_aided = models.CharField(max_length=20, blank=True)
    os_distance_unaided = models.CharField(max_length=20, blank=True)
    os_distance_aided = models.CharField(max_length=20, blank=True)
    os_distance_pinhole = models.CharField(max_length=20, blank=True)
    os_near_unaided = models.CharField(max_length=20, blank=True)
    os_near_aided = models.CharField(max_length=20, blank=True)
    ou_distance = models.CharField(max_length=20, blank=True)
    ou_near = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Visual acuity records"

    def __str__(self):
        return f"Visual acuity · {self.examination.visit.visit_number}"


class Refraction(models.Model):
    class Stage(models.TextChoices):
        OBJECTIVE = "objective", "Objective refraction"
        SUBJECTIVE = "subjective", "Subjective / final refraction"

    examination = models.ForeignKey(ClinicalExamination, on_delete=models.CASCADE, related_name="refractions")
    stage = models.CharField(max_length=16, choices=Stage.choices)
    od_sphere = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    od_cylinder = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    od_axis = models.PositiveSmallIntegerField(null=True, blank=True, validators=AXIS_VALIDATORS)
    od_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    od_prism = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    od_base = models.CharField(max_length=20, blank=True)
    od_visual_acuity = models.CharField(max_length=20, blank=True)
    os_sphere = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    os_cylinder = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    os_axis = models.PositiveSmallIntegerField(null=True, blank=True, validators=AXIS_VALIDATORS)
    os_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    os_prism = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    os_base = models.CharField(max_length=20, blank=True)
    os_visual_acuity = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["examination", "stage"], name="clinical_one_refraction_per_stage")]

    def __str__(self):
        return f"{self.get_stage_display()} · {self.examination.visit.visit_number}"


class EyeMeasurement(models.Model):
    class TonometryMethod(models.TextChoices):
        GOLDMANN = "goldmann", "Goldmann applanation"
        NON_CONTACT = "non_contact", "Non-contact tonometry"
        TONOPEN = "tonopen", "Tonopen"
        ICARE = "icare", "iCare"
        OTHER = "other", "Other"

    examination = models.OneToOneField(ClinicalExamination, on_delete=models.CASCADE, related_name="measurements")
    binocular_pd = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PD_VALIDATORS)
    od_monocular_pd = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PD_VALIDATORS)
    os_monocular_pd = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PD_VALIDATORS)
    od_iop = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PRESSURE_VALIDATORS)
    os_iop = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PRESSURE_VALIDATORS)
    iop_method = models.CharField(max_length=20, choices=TonometryMethod.choices, blank=True)
    iop_measured_at = models.TimeField(null=True, blank=True)
    iop_notes = models.TextField(blank=True)
    od_k1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    od_k1_axis = models.PositiveSmallIntegerField(null=True, blank=True, validators=AXIS_VALIDATORS)
    od_k2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    od_k2_axis = models.PositiveSmallIntegerField(null=True, blank=True, validators=AXIS_VALIDATORS)
    os_k1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    os_k1_axis = models.PositiveSmallIntegerField(null=True, blank=True, validators=AXIS_VALIDATORS)
    os_k2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    os_k2_axis = models.PositiveSmallIntegerField(null=True, blank=True, validators=AXIS_VALIDATORS)
    od_colour_vision = models.CharField(max_length=100, blank=True)
    os_colour_vision = models.CharField(max_length=100, blank=True)
    od_pupil_findings = models.CharField(max_length=180, blank=True)
    os_pupil_findings = models.CharField(max_length=180, blank=True)
    od_extraocular_movements = models.CharField(max_length=180, blank=True)
    os_extraocular_movements = models.CharField(max_length=180, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Measurements · {self.examination.visit.visit_number}"


class EyeFinding(models.Model):
    class Eye(models.TextChoices):
        OD = "od", "OD · Right eye"
        OS = "os", "OS · Left eye"

    examination = models.ForeignKey(ClinicalExamination, on_delete=models.CASCADE, related_name="eye_findings")
    eye = models.CharField(max_length=2, choices=Eye.choices)
    anterior_normal = models.BooleanField(null=True, blank=True)
    eyelids = models.CharField(max_length=180, blank=True)
    lashes = models.CharField(max_length=180, blank=True)
    conjunctiva = models.CharField(max_length=180, blank=True)
    cornea = models.CharField(max_length=180, blank=True)
    anterior_chamber = models.CharField(max_length=180, blank=True)
    iris = models.CharField(max_length=180, blank=True)
    pupil = models.CharField(max_length=180, blank=True)
    lens = models.CharField(max_length=180, blank=True)
    posterior_normal = models.BooleanField(null=True, blank=True)
    optic_disc = models.CharField(max_length=180, blank=True)
    cup_disc_ratio = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, validators=CUP_RATIO_VALIDATORS)
    macula = models.CharField(max_length=180, blank=True)
    vessels = models.CharField(max_length=180, blank=True)
    retina = models.CharField(max_length=180, blank=True)
    vitreous = models.CharField(max_length=180, blank=True)
    fundus_notes = models.TextField(blank=True)
    slit_lamp_findings = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["examination", "eye"], name="clinical_one_finding_per_eye")]

    def __str__(self):
        return f"{self.get_eye_display()} findings · {self.examination.visit.visit_number}"


class Diagnosis(models.Model):
    name = models.CharField(max_length=180, unique=True)
    clinical_code = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ExaminationDiagnosis(models.Model):
    examination = models.ForeignKey(ClinicalExamination, on_delete=models.CASCADE, related_name="diagnoses")
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.PROTECT, related_name="examination_entries")
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="recorded_examination_diagnoses")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["examination", "diagnosis"], name="clinical_unique_examination_diagnosis"),
            models.UniqueConstraint(fields=["examination"], condition=models.Q(is_primary=True), name="clinical_single_primary_diagnosis"),
        ]

    def __str__(self):
        return f"{self.diagnosis.name} · {self.examination.visit.visit_number}"


class EyeglassPrescriptionQuerySet(models.QuerySet):
    def active(self, on_date=None):
        day = on_date or timezone.localdate()
        return self.filter(status=EyeglassPrescription.Status.ACTIVE, issue_date__lte=day, valid_until__gte=day)

    def expiring_soon(self, days=30, on_date=None):
        day = on_date or timezone.localdate()
        return self.active(on_date=day).filter(valid_until__lte=day + timedelta(days=days))

    def expired(self, on_date=None):
        day = on_date or timezone.localdate()
        return self.filter(status=EyeglassPrescription.Status.ACTIVE, valid_until__lt=day)


class EyeglassPrescription(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Finalized / active"
        CANCELLED = "cancelled", "Cancelled"

    class PrescriptionType(models.TextChoices):
        DISTANCE = "distance", "Distance"
        READING = "reading", "Reading"
        BIFOCAL = "bifocal", "Bifocal"
        PROGRESSIVE = "progressive", "Progressive"
        OCCUPATIONAL = "occupational", "Occupational"
        OTHER = "other", "Other"

    prescription_number = models.CharField(max_length=24, unique=True, editable=False)
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="eyeglass_prescriptions")
    visit = models.ForeignKey("visits.Visit", on_delete=models.PROTECT, related_name="eyeglass_prescriptions")
    examination = models.OneToOneField(ClinicalExamination, on_delete=models.PROTECT, related_name="eyeglass_prescription")
    prescriber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="issued_eyeglass_prescriptions")
    od_sphere = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    od_cylinder = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    od_axis = models.PositiveSmallIntegerField(null=True, blank=True, validators=AXIS_VALIDATORS)
    od_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    od_prism = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    od_base = models.CharField(max_length=20, blank=True)
    os_sphere = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    os_cylinder = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    os_axis = models.PositiveSmallIntegerField(null=True, blank=True, validators=AXIS_VALIDATORS)
    os_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    os_prism = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    os_base = models.CharField(max_length=20, blank=True)
    binocular_pd = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PD_VALIDATORS)
    od_monocular_pd = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PD_VALIDATORS)
    os_monocular_pd = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PD_VALIDATORS)
    prescription_type = models.CharField(max_length=20, choices=PrescriptionType.choices, default=PrescriptionType.DISTANCE)
    issue_date = models.DateField(default=timezone.localdate, db_index=True)
    valid_until = models.DateField(null=True, blank=True, db_index=True)
    notes = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT, db_index=True)
    finalized_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EyeglassPrescriptionQuerySet.as_manager()

    class Meta:
        ordering = ["-issue_date", "-created_at"]
        indexes = [models.Index(fields=["status", "valid_until"])]
        permissions = [
            ("view_finalized_prescription", "Can view finalized spectacle prescriptions without clinical notes"),
            ("finalize_prescription", "Can finalize spectacle prescriptions"),
        ]

    def __str__(self):
        return f"{self.prescription_number} · {self.patient.full_name}"

    def clean(self):
        errors = {}
        if self.examination_id:
            if self.patient_id != self.examination.patient_id:
                errors["patient"] = "The prescription patient must match the examination patient."
            if self.visit_id != self.examination.visit_id:
                errors["visit"] = "The prescription visit must match the examination visit."
        if self.issue_date and self.valid_until and self.valid_until < self.issue_date:
            errors["valid_until"] = "The prescription cannot expire before its issue date."
        if self.prescriber_id and (not self.prescriber.is_clinician or not self.prescriber.is_active):
            errors["prescriber"] = "The prescriber must be an active optometrist or ophthalmologist."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        if not self.valid_until and self.issue_date:
            clinic = ClinicConfiguration.active()
            validity_days = clinic.default_prescription_validity_days if clinic else 365
            self.valid_until = self.issue_date + timedelta(days=validity_days)
        if self.pk:
            old_status = type(self).objects.filter(pk=self.pk).values_list("status", flat=True).first()
            if old_status == self.Status.ACTIVE and not getattr(self, "_allow_finalized_amendment", False):
                raise ValidationError("Finalized prescriptions cannot be modified through standard workflows.")
        self.full_clean()
        if not self.prescription_number:
            with transaction.atomic():
                self.prescription_number = next_identifier(key="prescription", prefix="RX")
                return super().save(*args, **kwargs)
        return super().save(*args, **kwargs)


class FollowUpQuerySet(models.QuerySet):
    def due(self, on_date=None):
        return self.filter(required=True, due_date__lte=on_date or timezone.localdate(), completed_at__isnull=True)

    def upcoming(self, days=30, on_date=None):
        day = on_date or timezone.localdate()
        return self.filter(required=True, due_date__range=(day, day + timedelta(days=days)), completed_at__isnull=True)


class FollowUpRecommendation(models.Model):
    examination = models.OneToOneField(ClinicalExamination, on_delete=models.CASCADE, related_name="follow_up")
    patient = models.ForeignKey("patients.Patient", on_delete=models.PROTECT, related_name="follow_up_recommendations")
    required = models.BooleanField(default=False)
    due_date = models.DateField(null=True, blank=True, db_index=True)
    interval_days = models.PositiveIntegerField(null=True, blank=True)
    reason = models.CharField(max_length=255, blank=True)
    notes = models.TextField(blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = FollowUpQuerySet.as_manager()

    class Meta:
        indexes = [models.Index(fields=["required", "due_date"])]

    def __str__(self):
        return f"Follow-up · {self.patient.patient_number}"

    def clean(self):
        errors = {}
        if self.examination_id and self.patient_id != self.examination.patient_id:
            errors["patient"] = "The follow-up patient must match the examination patient."
        if self.required and not self.due_date:
            errors["due_date"] = "A follow-up date is required."
        if self.due_date and self.examination_id and self.due_date < timezone.localtime(self.examination.examined_at).date():
            errors["due_date"] = "The follow-up cannot be earlier than the consultation date."
        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
