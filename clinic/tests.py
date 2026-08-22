from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from accounts.models import StaffRole

from .models import AuditLog, ClinicConfiguration, StaffProfile
from .services import log_event, next_identifier, normalise_ghana_phone, send_sms
from .test_helpers import ClinicTestCase


class ClinicConfigurationTests(ClinicTestCase):
    def test_single_active_clinic_configuration(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ClinicConfiguration.objects.create(name="Other", address="Road", phone="0241111111")

    def test_independent_identifier_sequence(self):
        self.assertEqual(next_identifier(key="test", prefix="EC"), "EC-000001")
        self.assertEqual(next_identifier(key="test", prefix="EC"), "EC-000002")

    def test_ghana_phone_normalisation(self):
        self.assertEqual(normalise_ghana_phone("024 555 4321"), "+233245554321")

    def test_sms_fails_closed_without_provider_credentials(self):
        result = send_sms(recipient="0245554321", message="Appointment reminder")
        self.assertFalse(result.successful)

    def test_audit_log_redacts_sensitive_metadata(self):
        event = log_event(actor=self.receptionist, action="staff.updated", resource=self.clinician, metadata={"role": "optometrist", "password": "never-store-this", "api_key": "secret"})
        self.assertEqual(event.metadata, {"role": "optometrist"})
        self.assertEqual(AuditLog.objects.count(), 1)


class StaffProfileTests(ClinicTestCase):
    def test_staff_profile_assigns_role_group(self):
        profile = StaffProfile.objects.create(staff_id="STF-000001", user=self.receptionist, role=StaffRole.RECEPTIONIST)
        self.assertTrue(profile.user.groups.filter(name=StaffRole.RECEPTIONIST).exists())

    def test_clinician_requires_registration_number(self):
        with self.assertRaises(ValidationError):
            StaffProfile.objects.create(staff_id="STF-000002", user=self.clinician, role=StaffRole.OPTOMETRIST)

    def test_all_nine_role_groups_exist(self):
        self.assertEqual(Group.objects.filter(name__in=StaffRole.values).count(), 9)
