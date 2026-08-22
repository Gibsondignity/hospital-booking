from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme

from clinic.auth import clinic_permission_required
from clinic.services import log_event

from .forms import CustomAuthenticationForm, StaffUserCreationForm
from .models import CustomUser


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard:home")
    form = CustomAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        destination = request.GET.get("next")
        if destination and url_has_allowed_host_and_scheme(destination, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
            return redirect(destination)
        return redirect("dashboard:home")
    return render(request, "accounts/login.html", {"form": form})


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@clinic_permission_required("accounts.view_customuser")
def staff_list(request):
    staff = CustomUser.objects.select_related("staff_profile").order_by("first_name", "last_name")
    return render(request, "accounts/staff_list.html", {"staff_members": staff})


@clinic_permission_required("accounts.add_customuser")
def staff_create(request):
    form = StaffUserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        log_event(actor=request.user, action="staff.created", resource=user, metadata={"role": user.role})
        messages.success(request, "Staff account created successfully.")
        return redirect("accounts:staff_list")
    return render(request, "shared/form.html", {"form": form, "page_title": "Add staff member", "submit_label": "Create account"})
