from django import forms
from django.db.models import Q

from accounts.forms import StyledFormMixin
from clinic.services import normalise_ghana_phone

from .models import Patient, PatientMedicalHistory


class PatientForm(StyledFormMixin, forms.ModelForm):
    confirm_duplicate = forms.BooleanField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Patient
        fields = ("first_name", "middle_name", "last_name", "date_of_birth", "gender", "phone", "alternative_phone", "email", "national_id", "occupation", "photograph", "address", "city", "region", "emergency_contact_name", "emergency_contact_relationship", "emergency_contact_phone")
        widgets = {"date_of_birth": forms.DateInput(attrs={"type": "date"})}

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone")
        first_name = cleaned_data.get("first_name")
        last_name = cleaned_data.get("last_name")
        birth_date = cleaned_data.get("date_of_birth")
        national_id = cleaned_data.get("national_id")
        if not phone or not first_name or not last_name or not birth_date:
            return cleaned_data
        phone = normalise_ghana_phone(phone)
        cleaned_data["phone"] = phone
        duplicates = Patient.objects.exclude(pk=self.instance.pk).filter(Q(phone=phone) | Q(first_name__iexact=first_name, last_name__iexact=last_name, date_of_birth=birth_date))
        if national_id:
            duplicates = duplicates | Patient.objects.exclude(pk=self.instance.pk).filter(national_id__iexact=national_id)
        if duplicates.exists() and not cleaned_data.get("confirm_duplicate"):
            self.duplicate_candidates = duplicates.distinct()
            raise forms.ValidationError("A similar patient already exists. Review the matching records and confirm before continuing.")
        return cleaned_data


class PatientMedicalHistoryForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PatientMedicalHistory
        exclude = ("patient",)
        widgets = {field: forms.Textarea(attrs={"rows": 2}) for field in ("allergies", "existing_conditions", "current_medications", "previous_eye_surgery", "family_eye_disease_history", "other_notes")}
