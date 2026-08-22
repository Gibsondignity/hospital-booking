"""Section-based clinical forms backed by the existing normalized records."""

from django import forms

from accounts.forms import StyledFormMixin
from .models import ClinicalExamination, EyeFinding, EyeMeasurement, EyeglassPrescription, FollowUpRecommendation, Refraction, VisualAcuity


class ClinicalSectionForm(StyledFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.setdefault("rows", 2)
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={"type": "date", "class": "form-control"})


class HistoryForm(ClinicalSectionForm):
    class Meta:
        model = ClinicalExamination
        fields = ("chief_complaint", "complaint_duration", "affected_eye", "presenting_history", "previous_spectacle_use", "contact_lens_use", "previous_eye_condition", "previous_eye_surgery", "previous_eye_trauma", "current_eye_medication", "general_medication", "systemic_illness", "family_ocular_history", "additional_history")


class AssessmentForm(ClinicalSectionForm):
    class Meta:
        model = ClinicalExamination
        fields = ("clinical_assessment", "clinical_impression", "clinical_notes", "practitioner_comments", "referral_required", "referred_to", "referral_facility", "referral_reason", "referral_urgency", "referral_notes")


class VisualAcuityForm(ClinicalSectionForm):
    class Meta:
        model = VisualAcuity
        exclude = ("examination",)


class RefractionForm(ClinicalSectionForm):
    class Meta:
        model = Refraction
        exclude = ("examination", "stage")


class MeasurementForm(ClinicalSectionForm):
    class Meta:
        model = EyeMeasurement
        exclude = ("examination",)


class EyeFindingForm(ClinicalSectionForm):
    class Meta:
        model = EyeFinding
        exclude = ("examination", "eye")


class PrescriptionForm(ClinicalSectionForm):
    class Meta:
        model = EyeglassPrescription
        exclude = ("prescription_number", "patient", "visit", "examination", "prescriber", "status", "finalized_at")


class FollowUpForm(ClinicalSectionForm):
    class Meta:
        model = FollowUpRecommendation
        exclude = ("examination", "patient", "completed_at")


class DiagnosisForm(StyledFormMixin, forms.Form):
    name = forms.CharField(max_length=180, label="Diagnosis")
    is_primary = forms.BooleanField(required=False, initial=True, label="Primary diagnosis")
