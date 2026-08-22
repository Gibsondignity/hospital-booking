from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from clinic.auth import clinic_permission_required
from clinic.services import log_event
from visits.models import Visit

from .forms import AppointmentForm
from .models import Appointment


@clinic_permission_required("appointment.view_appointment")
def appointment_list(request):
    status = request.GET.get("status", "")
    date = request.GET.get("date", "")
    appointments = Appointment.objects.select_related("patient", "practitioner")
    if status:
        appointments = appointments.filter(status=status)
    if date:
        appointments = appointments.filter(appointment_date=date)
    page = Paginator(appointments, 20).get_page(request.GET.get("page"))
    return render(request, "appointment/list.html", {"page_obj": page, "status_choices": Appointment.Status.choices, "selected_status": status, "selected_date": date, "today": timezone.localdate()})


@clinic_permission_required("appointment.add_appointment")
def appointment_create(request):
    initial = {"patient": request.GET.get("patient")}
    form = AppointmentForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        appointment = form.save(commit=False)
        appointment.created_by = request.user
        appointment.save()
        log_event(actor=request.user, action="appointment.created", resource=appointment)
        messages.success(request, f"Appointment {appointment.reference} scheduled.")
        return redirect("appointment:list")
    return render(request, "shared/form.html", {"form": form, "page_title": "Schedule appointment", "submit_label": "Save appointment"})


@clinic_permission_required("appointment.change_appointment")
@require_POST
def appointment_status(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    new_status = request.POST.get("status")
    allowed = {Appointment.Status.CONFIRMED, Appointment.Status.CANCELLED, Appointment.Status.NO_SHOW}
    if new_status not in allowed:
        messages.error(request, "This appointment status transition is not permitted.")
        return redirect("appointment:list")
    appointment.status = new_status
    appointment.save(update_fields=["status", "updated_at"])
    log_event(actor=request.user, action="appointment.status_changed", resource=appointment, metadata={"status": new_status})
    messages.success(request, "Appointment status updated.")
    return redirect("appointment:list")


@clinic_permission_required(("appointment.change_appointment", "visits.add_visit"))
@require_POST
def appointment_check_in(request, pk):
    with transaction.atomic():
        appointment = get_object_or_404(Appointment.objects.select_for_update().select_related("patient"), pk=pk)
        if appointment.status not in {Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED}:
            messages.error(request, "Only scheduled or confirmed appointments can be checked in.")
            return redirect("appointment:list")
        visit = Visit.objects.create(patient=appointment.patient, appointment=appointment, practitioner=appointment.practitioner, chief_complaint=appointment.reason, visit_type=Visit.VisitType.APPOINTMENT, created_by=request.user)
        appointment.status = Appointment.Status.CHECKED_IN
        appointment.save(update_fields=["status", "updated_at"])
        log_event(actor=request.user, action="appointment.checked_in", resource=appointment, metadata={"visit_number": visit.visit_number})
    messages.success(request, f"{appointment.patient.full_name} checked in.")
    return redirect("visits:queue")
