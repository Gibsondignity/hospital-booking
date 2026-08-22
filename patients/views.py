from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from clinic.auth import clinic_permission_required
from clinic.services import log_event

from .forms import PatientForm, PatientMedicalHistoryForm
from .models import Patient, PatientMedicalHistory


@clinic_permission_required("patients.view_patient")
def patient_list(request):
    query = request.GET.get("q", "")
    patients = Patient.objects.filter(is_active=True).search(query)
    page = Paginator(patients, 20).get_page(request.GET.get("page"))
    return render(request, "patients/list.html", {"page_obj": page, "query": query})


@clinic_permission_required("patients.add_patient")
def patient_create(request):
    form = PatientForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        patient = form.save(commit=False)
        patient.registered_by = request.user
        patient.save()
        log_event(actor=request.user, action="patient.created", resource=patient)
        messages.success(request, f"Patient {patient.patient_number} registered successfully.")
        return redirect(patient)
    return render(request, "patients/form.html", {"form": form, "page_title": "Register patient", "duplicate_candidates": getattr(form, "duplicate_candidates", [])})


@clinic_permission_required("patients.view_patient")
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    visits = patient.visits.select_related("practitioner").order_by("-checked_in_at")[:10]
    appointments = patient.appointments.select_related("practitioner").order_by("-appointment_date", "-appointment_time")[:10]
    medical_history = None
    if request.user.has_perm("patients.view_sensitive_history"):
        medical_history = PatientMedicalHistory.objects.filter(patient=patient).first()
    upcoming_appointment = patient.appointments.filter(appointment_date__gte=timezone.localdate(), status__in=["scheduled", "confirmed"]).order_by("appointment_date", "appointment_time").first()
    return render(request, "patients/detail.html", {"patient": patient, "visits": visits, "appointments": appointments, "last_visit": visits.first(), "upcoming_appointment": upcoming_appointment, "medical_history": medical_history, "active_tab": request.GET.get("tab", "overview")})


@clinic_permission_required("patients.change_patient")
def patient_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, request.FILES or None, instance=patient)
    if request.method == "POST" and form.is_valid():
        patient = form.save()
        log_event(actor=request.user, action="patient.updated", resource=patient)
        messages.success(request, "Patient information updated.")
        return redirect(patient)
    return render(request, "patients/form.html", {"form": form, "page_title": "Update patient", "patient": patient, "duplicate_candidates": getattr(form, "duplicate_candidates", [])})


@clinic_permission_required("patients.change_patientmedicalhistory")
def medical_history_update(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    history, _ = PatientMedicalHistory.objects.get_or_create(patient=patient)
    form = PatientMedicalHistoryForm(request.POST or None, instance=history)
    if request.method == "POST" and form.is_valid():
        history = form.save()
        log_event(actor=request.user, action="patient.medical_history_updated", resource=history)
        messages.success(request, "Medical history updated.")
        return redirect(patient)
    return render(request, "shared/form.html", {"form": form, "page_title": f"Medical history · {patient.full_name}", "submit_label": "Save medical history"})
