from datetime import date, timedelta

from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone

from clinic.models import AuditLog
from clinic.test_helpers import ClinicTestCase

from .forms import PatientForm
from .models import Patient, PatientMedicalHistory


class PatientModelTests(ClinicTestCase):
    def test_patient_receives_independent_unique_number(self):
        first = self.make_patient(pk=42)
        second = self.make_patient(first_name="Kofi", phone="+233245554322")
        self.assertEqual(first.patient_number, "EC-000001")
        self.assertEqual(second.patient_number, "EC-000002")

    def test_custom_patient_number_prefix(self):
        self.configuration.patient_number_prefix = "VISION"
        self.configuration.save()
        self.assertEqual(self.make_patient().patient_number, "VISION-000001")

    def test_nonempty_national_id_must_be_unique(self):
        self.make_patient(national_id="GHA-111111111-1")
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.make_patient(first_name="Kofi", phone="0240000012", national_id="GHA-111111111-1")

    def test_multiple_blank_national_ids_are_allowed(self):
        self.make_patient()
        self.make_patient(first_name="Kofi", phone="0240000012")
        self.assertEqual(Patient.objects.count(), 2)

    def test_future_birth_date_is_invalid(self):
        patient = self.make_patient()
        patient.date_of_birth = timezone.localdate() + timedelta(days=1)
        with self.assertRaisesMessage(Exception, "Date of birth cannot be in the future"):
            patient.full_clean()

    def test_search_by_full_name_patient_number_phone_and_id(self):
        patient = self.make_patient(national_id="GHA-111111111-1")
        for query in ["Akosua Owusu", patient.patient_number, "245554321", "GHA-111111111-1"]:
            with self.subTest(query=query):
                self.assertIn(patient, Patient.objects.search(query))

    def test_duplicate_patient_requires_confirmation(self):
        self.make_patient()
        data = {"first_name": "Ama", "last_name": "Owusu", "date_of_birth": "1990-01-01", "gender": "female", "phone": "0245554321"}
        form = PatientForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertTrue(hasattr(form, "duplicate_candidates"))
        form = PatientForm(data={**data, "confirm_duplicate": "true"})
        self.assertTrue(form.is_valid(), form.errors)


class PatientViewTests(ClinicTestCase):
    def test_receptionist_can_register_patient(self):
        self.client.force_login(self.receptionist)
        response = self.client.post(reverse("patients:create"), {"first_name": "Efua", "last_name": "Mensah", "date_of_birth": "1993-02-03", "gender": "female", "phone": "0247777777"})
        self.assertEqual(response.status_code, 302)
        patient = Patient.objects.get(first_name="Efua")
        self.assertEqual(patient.registered_by, self.receptionist)
        self.assertTrue(AuditLog.objects.filter(action="patient.created").exists())

    def test_patient_search_page_returns_matching_patient(self):
        patient = self.make_patient()
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("patients:list"), {"q": patient.patient_number})
        self.assertContains(response, patient.full_name)

    def test_profile_shows_overview_and_history_tabs(self):
        patient = self.make_patient()
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("patients:detail", args=[patient.pk]))
        self.assertContains(response, patient.patient_number)
        self.assertContains(response, "Eye examinations")

    def test_receptionist_cannot_access_medical_history(self):
        patient = self.make_patient()
        self.client.force_login(self.receptionist)
        self.assertEqual(self.client.get(reverse("patients:medical_history", args=[patient.pk])).status_code, 403)

    def test_clinician_can_update_medical_history(self):
        patient = self.make_patient()
        self.client.force_login(self.clinician)
        response = self.client.post(reverse("patients:medical_history", args=[patient.pk]), {"allergies": "Penicillin", "existing_conditions": "", "current_medications": "", "previous_eye_surgery": "", "family_eye_disease_history": "", "other_notes": ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PatientMedicalHistory.objects.get(patient=patient).allergies, "Penicillin")
