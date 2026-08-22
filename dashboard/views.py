from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils import timezone

from appointment.models import Appointment
from patients.models import Patient
from visits.models import Visit


@login_required
def dashboard(request):
    today = timezone.localdate()
    metrics = {
        "active_patients": Patient.objects.filter(is_active=True).count(),
        "today_appointments": Appointment.objects.filter(appointment_date=today).count(),
        "waiting_patients": Visit.objects.filter(status=Visit.Status.WAITING, checked_in_at__date=today).count(),
        "completed_today": Visit.objects.filter(status=Visit.Status.COMPLETED, consultation_ended_at__date=today).count(),
        "new_patients_this_month": Patient.objects.filter(registered_at__year=today.year, registered_at__month=today.month).count(),
    }
    upcoming = Appointment.objects.select_related("patient", "practitioner").filter(appointment_date__gte=today, status__in=[Appointment.Status.SCHEDULED, Appointment.Status.CONFIRMED])[:8]
    queue = Visit.objects.select_related("patient", "practitioner").filter(status=Visit.Status.WAITING, checked_in_at__date=today)[:8]
    return render(request, "dashboard/dashboard.html", {"metrics": metrics, "upcoming_appointments": upcoming, "waiting_queue": queue, "today": today})
