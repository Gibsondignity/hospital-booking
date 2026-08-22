from django.urls import reverse

from appointment.models import Appointment
from clinic.test_helpers import ClinicTestCase

from .models import Visit


class VisitTests(ClinicTestCase):
    def test_walk_in_visit_does_not_require_appointment(self):
        patient = self.make_patient()
        self.client.force_login(self.receptionist)
        response = self.client.post(reverse("visits:walk_in"), {"patient": patient.pk, "practitioner": self.clinician.pk, "chief_complaint": "Eye pain", "notes": ""})
        self.assertEqual(response.status_code, 302)
        visit = Visit.objects.get(patient=patient)
        self.assertEqual(visit.visit_type, Visit.VisitType.WALK_IN)
        self.assertIsNone(visit.appointment)

    def test_waiting_queue_shows_checked_in_patient(self):
        appointment = self.make_appointment()
        self.client.force_login(self.receptionist)
        self.client.post(reverse("appointment:check_in", args=[appointment.pk]))
        response = self.client.get(reverse("visits:queue"))
        self.assertContains(response, appointment.patient.full_name)

    def test_clinician_can_start_and_complete_consultation(self):
        appointment = self.make_appointment()
        visit = Visit.objects.create(patient=appointment.patient, appointment=appointment, practitioner=self.clinician, created_by=self.receptionist)
        self.client.force_login(self.clinician)
        self.client.post(reverse("visits:status", args=[visit.pk]), {"status": "in_consultation"})
        visit.refresh_from_db()
        appointment.refresh_from_db()
        self.assertEqual(visit.status, Visit.Status.IN_CONSULTATION)
        self.assertEqual(appointment.status, Appointment.Status.IN_CONSULTATION)
        self.assertIsNotNone(visit.consultation_started_at)
        self.client.post(reverse("visits:status", args=[visit.pk]), {"status": "completed"})
        visit.refresh_from_db()
        appointment.refresh_from_db()
        self.assertEqual(visit.status, Visit.Status.COMPLETED)
        self.assertEqual(appointment.status, Appointment.Status.COMPLETED)
        self.assertIsNotNone(visit.consultation_ended_at)

    def test_receptionist_cannot_modify_clinical_visit_status(self):
        patient = self.make_patient()
        visit = Visit.objects.create(patient=patient, created_by=self.receptionist)
        self.client.force_login(self.receptionist)
        self.assertEqual(self.client.post(reverse("visits:status", args=[visit.pk]), {"status": "in_consultation"}).status_code, 403)

    def test_invalid_visit_transition_is_rejected(self):
        patient = self.make_patient()
        visit = Visit.objects.create(patient=patient, created_by=self.receptionist)
        self.client.force_login(self.clinician)
        self.client.post(reverse("visits:status", args=[visit.pk]), {"status": "completed"})
        visit.refresh_from_db()
        self.assertEqual(visit.status, Visit.Status.WAITING)
