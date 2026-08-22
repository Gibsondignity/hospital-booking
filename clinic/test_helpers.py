from datetime import date, timedelta
from io import StringIO

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from accounts.models import StaffRole
from appointment.models import Appointment
from clinic.models import ClinicConfiguration
from patients.models import Patient


class ClinicTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_clinic_roles", stdout=StringIO())
        cls.configuration = ClinicConfiguration.objects.create(name="Accra Eye Clinic", address="1 Clinic Road", city="Accra", phone="0240000000")
        User = get_user_model()
        cls.receptionist = User.objects.create_user(username="receptionist", password="TestPass-482!", role=StaffRole.RECEPTIONIST, first_name="Ama", last_name="Reception")
        cls.receptionist.groups.add(Group.objects.get(name=StaffRole.RECEPTIONIST))
        cls.clinician = User.objects.create_user(username="clinician", password="TestPass-482!", role=StaffRole.OPTOMETRIST, first_name="Kojo", last_name="Doctor")
        cls.clinician.groups.add(Group.objects.get(name=StaffRole.OPTOMETRIST))
        cls.accountant = User.objects.create_user(username="accountant", password="TestPass-482!", role=StaffRole.ACCOUNTANT)
        cls.accountant.groups.add(Group.objects.get(name=StaffRole.ACCOUNTANT))
        cls.administrator = User.objects.create_user(username="administrator", password="TestPass-482!", role=StaffRole.CLINIC_ADMIN)
        cls.administrator.groups.add(Group.objects.get(name=StaffRole.CLINIC_ADMIN))

    def make_patient(self, **overrides):
        data = {"first_name": "Akosua", "last_name": "Owusu", "date_of_birth": date(1994, 4, 12), "gender": Patient.Gender.FEMALE, "phone": "+233245554321", "registered_by": self.receptionist}
        data.update(overrides)
        return Patient.objects.create(**data)

    def make_appointment(self, patient=None, **overrides):
        data = {"patient": patient or self.make_patient(), "appointment_date": timezone.localdate() + timedelta(days=1), "appointment_time": "09:00", "practitioner": self.clinician, "created_by": self.receptionist}
        data.update(overrides)
        return Appointment.objects.create(**data)
