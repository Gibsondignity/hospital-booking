"""Explicit role-to-permission policy, backed by Django groups."""

from accounts.models import StaffRole

PATIENT_BASIC = ["patients.view_patient", "patients.add_patient", "patients.change_patient"]
APPOINTMENT_BASIC = ["appointment.view_appointment", "appointment.add_appointment", "appointment.change_appointment"]
VISIT_RECEPTION = ["visits.view_visit", "visits.add_visit"]
CLINICAL = ["patients.view_sensitive_history", "patients.view_patientmedicalhistory", "patients.change_patientmedicalhistory", "visits.change_visit"]
CLINICAL_MODELS = ("clinicalexamination", "visualacuity", "refraction", "eyemeasurement", "eyefinding", "diagnosis", "examinationdiagnosis", "eyeglassprescription", "followuprecommendation")
CLINICAL += [f"clinical.{action}_{model}" for model in CLINICAL_MODELS for action in ("view", "add", "change")]
CLINICAL += ["clinical.finalize_examination", "clinical.finalize_prescription", "clinical.view_finalized_prescription"]
NURSING = ["clinical.record_preconsult_observations"] + [f"clinical.{action}_{model}" for model in ("visualacuity", "eyemeasurement") for action in ("view", "add", "change")]

ROLE_PERMISSIONS = {
    StaffRole.SYSTEM_ADMIN: "all",
    StaffRole.CLINIC_ADMIN: "all",
    StaffRole.OPTOMETRIST: PATIENT_BASIC + APPOINTMENT_BASIC + VISIT_RECEPTION + CLINICAL,
    StaffRole.OPHTHALMOLOGIST: PATIENT_BASIC + APPOINTMENT_BASIC + VISIT_RECEPTION + CLINICAL,
    StaffRole.NURSE: PATIENT_BASIC + APPOINTMENT_BASIC + VISIT_RECEPTION + ["patients.view_sensitive_history", "patients.view_patientmedicalhistory"] + NURSING,
    StaffRole.RECEPTIONIST: PATIENT_BASIC + APPOINTMENT_BASIC + VISIT_RECEPTION,
    StaffRole.OPTICIAN: ["patients.view_patient", "appointment.view_appointment", "visits.view_visit", "clinical.view_finalized_prescription"],
    StaffRole.PHARMACIST: ["patients.view_patient", "visits.view_visit"],
    StaffRole.ACCOUNTANT: ["patients.view_patient", "appointment.view_appointment", "visits.view_visit"],
}
