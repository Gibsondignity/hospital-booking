from django.urls import reverse

from clinic.test_helpers import ClinicTestCase
from visits.models import Visit


class DashboardTests(ClinicTestCase):
    def test_dashboard_shows_real_patient_metrics(self):
        patient = self.make_patient()
        Visit.objects.create(patient=patient, created_by=self.receptionist)
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("dashboard:home"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["metrics"]["active_patients"], 1)
        self.assertEqual(response.context["metrics"]["waiting_patients"], 1)

    def test_dashboard_does_not_show_fake_financial_metrics(self):
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("dashboard:home"))
        self.assertNotContains(response, "Today's revenue")

    def test_navigation_hides_staff_management_from_receptionist(self):
        self.client.force_login(self.receptionist)
        response = self.client.get(reverse("dashboard:home"))
        self.assertNotContains(response, reverse("accounts:staff_list"))
