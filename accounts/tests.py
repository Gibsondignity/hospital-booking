from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

from accounts.models import StaffRole
from clinic.test_helpers import ClinicTestCase


class AuthenticationAndStaffTests(ClinicTestCase):
    def test_dashboard_requires_authentication(self):
        response = self.client.get(reverse("dashboard:home"))
        self.assertRedirects(response, f"{reverse('accounts:login')}?next=/")

    def test_internal_patient_route_redirects_anonymous_user(self):
        response = self.client.get(reverse("patients:list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_login_rejects_external_redirect(self):
        response = self.client.post(f"{reverse('accounts:login')}?next=https://example.com/steal", {"username": "receptionist", "password": "TestPass-482!"})
        self.assertRedirects(response, reverse("dashboard:home"))

    def test_accountant_cannot_register_patients(self):
        self.client.force_login(self.accountant)
        response = self.client.get(reverse("patients:create"))
        self.assertEqual(response.status_code, 403)

    def test_receptionist_cannot_manage_staff(self):
        self.client.force_login(self.receptionist)
        self.assertEqual(self.client.get(reverse("accounts:staff_list")).status_code, 403)

    def test_administrator_can_view_staff(self):
        self.client.force_login(self.administrator)
        self.assertEqual(self.client.get(reverse("accounts:staff_list")).status_code, 200)

    def test_administrator_can_create_staff_profile(self):
        self.client.force_login(self.administrator)
        response = self.client.post(reverse("accounts:staff_create"), {"username": "newnurse", "first_name": "Esi", "last_name": "Nurse", "email": "esi@example.com", "phone": "0240000002", "role": StaffRole.NURSE, "professional_title": "Nurse", "registration_number": "", "department": "Nursing", "password1": "StrongClinicPass-947!", "password2": "StrongClinicPass-947!"})
        self.assertEqual(response.status_code, 302)
        user = get_user_model().objects.get(username="newnurse")
        self.assertEqual(user.staff_profile.role, StaffRole.NURSE)

    def test_state_changing_requests_require_csrf_token(self):
        patient = self.make_patient()
        appointment = self.make_appointment(patient=patient)
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.receptionist)
        response = client.post(reverse("appointment:check_in", args=[appointment.pk]))
        self.assertEqual(response.status_code, 403)
