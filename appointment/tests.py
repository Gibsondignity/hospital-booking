from datetime import timedelta

from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone

from clinic.test_helpers import ClinicTestCase
from visits.models import Visit

from .forms import AppointmentForm
from .models import Appointment


class AppointmentTests(ClinicTestCase):
    def test_appointment_has_reference_and_patient(self):
        appointment = self.make_appointment()
        self.assertEqual(appointment.reference, "APT-000001")
        self.assertEqual(appointment.patient.first_name, "Akosua")

    def test_past_appointment_is_rejected(self):
        appointment = self.make_appointment()
        appointment.appointment_date = timezone.localdate() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            appointment.full_clean()

    def test_non_clinician_cannot_be_practitioner(self):
        appointment = self.make_appointment()
        appointment.practitioner = self.receptionist
        with self.assertRaises(ValidationError):
            appointment.full_clean()

    def test_double_booked_practitioner_is_rejected(self):
        appointment = self.make_appointment()
        another_patient = self.make_patient(first_name="Kofi", phone="0247777778")
        form = AppointmentForm(data={"patient": another_patient.pk, "appointment_date": appointment.appointment_date, "appointment_time": "09:00", "practitioner": self.clinician.pk, "appointment_type": "eye_exam", "reason": "", "notes": ""})
        self.assertFalse(form.is_valid())

    def test_receptionist_can_schedule_appointment(self):
        patient = self.make_patient()
        self.client.force_login(self.receptionist)
        response = self.client.post(reverse("appointment:create"), {"patient": patient.pk, "appointment_date": timezone.localdate() + timedelta(days=2), "appointment_time": "10:30", "practitioner": self.clinician.pk, "appointment_type": "eye_exam", "reason": "Blurred vision", "notes": ""})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Appointment.objects.get(patient=patient).reason, "Blurred vision")

    def test_receptionist_can_change_appointment_status(self):
        appointment = self.make_appointment()
        self.client.force_login(self.receptionist)
        response = self.client.post(reverse("appointment:status", args=[appointment.pk]), {"status": "confirmed"})
        self.assertEqual(response.status_code, 302)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CONFIRMED)

    def test_check_in_creates_exactly_one_visit(self):
        appointment = self.make_appointment()
        self.client.force_login(self.receptionist)
        response = self.client.post(reverse("appointment:check_in", args=[appointment.pk]))
        self.assertEqual(response.status_code, 302)
        appointment.refresh_from_db()
        self.assertEqual(appointment.status, Appointment.Status.CHECKED_IN)
        self.assertEqual(Visit.objects.get(appointment=appointment).patient, appointment.patient)
        self.client.post(reverse("appointment:check_in", args=[appointment.pk]))
        self.assertEqual(Visit.objects.filter(appointment=appointment).count(), 1)

    def test_accountant_cannot_check_in_appointment(self):
        appointment = self.make_appointment()
        self.client.force_login(self.accountant)
        self.assertEqual(self.client.post(reverse("appointment:check_in", args=[appointment.pk])).status_code, 403)
