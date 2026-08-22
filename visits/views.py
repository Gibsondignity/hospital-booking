from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from appointment.models import Appointment
from clinic.auth import clinic_permission_required
from clinic.services import log_event

from .forms import WalkInVisitForm
from .models import Visit


@clinic_permission_required("visits.view_visit")
def visit_list(request):
    visits = Visit.objects.select_related("patient", "practitioner", "appointment").order_by("-checked_in_at")
    page = Paginator(visits, 20).get_page(request.GET.get("page"))
    return render(request, "visits/list.html", {"page_obj": page})


@clinic_permission_required("visits.view_visit")
def waiting_queue(request):
    visits = Visit.objects.select_related("patient", "practitioner", "appointment").filter(status__in=[Visit.Status.WAITING, Visit.Status.IN_CONSULTATION], checked_in_at__date=timezone.localdate())
    return render(request, "visits/queue.html", {"visits": visits})


@clinic_permission_required("visits.add_visit")
def walk_in(request):
    form = WalkInVisitForm(request.POST or None, initial={"patient": request.GET.get("patient")})
    if request.method == "POST" and form.is_valid():
        visit = form.save(commit=False)
        visit.visit_type = Visit.VisitType.WALK_IN
        visit.created_by = request.user
        visit.save()
        log_event(actor=request.user, action="visit.walk_in_created", resource=visit)
        messages.success(request, f"Walk-in visit {visit.visit_number} created.")
        return redirect("visits:queue")
    return render(request, "shared/form.html", {"form": form, "page_title": "Register walk-in visit", "submit_label": "Check patient in"})


@clinic_permission_required("visits.change_visit")
@require_POST
def visit_status(request, pk):
    visit = get_object_or_404(Visit.objects.select_related("appointment"), pk=pk)
    new_status = request.POST.get("status")
    if new_status == Visit.Status.IN_CONSULTATION and visit.status == Visit.Status.WAITING:
        visit.consultation_started_at = timezone.now()
        appointment_status = Appointment.Status.IN_CONSULTATION
    elif new_status == Visit.Status.COMPLETED and visit.status == Visit.Status.IN_CONSULTATION:
        visit.consultation_ended_at = timezone.now()
        appointment_status = Appointment.Status.COMPLETED
    else:
        messages.error(request, "This visit status transition is not permitted.")
        return redirect("visits:queue")
    visit.status = new_status
    visit.save()
    if visit.appointment:
        visit.appointment.status = appointment_status
        visit.appointment.save(update_fields=["status", "updated_at"])
    log_event(actor=request.user, action="visit.status_changed", resource=visit, metadata={"status": new_status})
    messages.success(request, "Visit status updated.")
    return redirect("visits:queue")
