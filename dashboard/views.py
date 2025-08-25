from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from appointment.models import Appointment, Hospital, Doctor
from accounts.models import CustomUser
from .models import Booking, DoctorManagement, HospitalManagement
from .forms import HospitalForm, DoctorForm

@login_required
def dashboard(request):
    """Main dashboard view"""
    # Get user's appointments
    user_appointments = Appointment.objects.filter(email=request.user.email)
    
    # Get recent bookings
    recent_bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')[:5]
    
    # Get management activities
    doctor_management = DoctorManagement.objects.filter(manager=request.user).order_by('-timestamp')[:5]
    hospital_management = HospitalManagement.objects.filter(manager=request.user).order_by('-timestamp')[:5]
    
    # Get hospitals with doctors
    hospitals_with_services = Hospital.objects.prefetch_related('doctors').all()[:6]
    
    # Get counts
    hospitals_count = Hospital.objects.count()
    doctors_count = Doctor.objects.count()
    
    context = {
        'user_appointments': user_appointments,
        'recent_bookings': recent_bookings,
        'doctor_management': doctor_management,
        'hospital_management': hospital_management,
        'hospitals_with_services': hospitals_with_services,
        'hospitals_count': hospitals_count,
        'doctors_count': doctors_count,
    }
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def manage_bookings(request):
    """View for managing bookings"""
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    return render(request, 'dashboard/manage_bookings.html', {'bookings': bookings})

@login_required
def view_appointments(request):
    """View for viewing all appointments (admin only)"""
    # Only staff users can view all appointments
    if not request.user.is_staff:
        return render(request, 'dashboard/access_denied.html')
    
    appointments = Appointment.objects.all().order_by('-created_at')
    
    context = {
        'appointments': appointments,
    }
    
    return render(request, 'dashboard/view_appointments.html', context)

@login_required
def manage_doctors(request):
    """View for managing doctors"""
    # Only staff users can manage doctors
    if not request.user.is_staff:
        return render(request, 'dashboard/access_denied.html')
    
    # Handle delete request
    if request.method == 'POST' and 'delete_doctor' in request.POST:
        doctor_id = request.POST.get('doctor_id')
        doctor = get_object_or_404(Doctor, id=doctor_id)
        doctor_name = doctor.name
        doctor.delete()
        # Log the management activity
        DoctorManagement.objects.create(
            doctor=doctor,
            manager=request.user,
            action='removed',
            notes=f'Doctor {doctor_name} was removed from the system'
            )
        messages.success(request, f'Doctor {doctor_name} has been deleted successfully!')
        return redirect('dashboard:manage_doctors')
    
    # Handle edit request
    if request.method == 'POST' and 'edit_doctor' in request.POST:
        doctor_id = request.POST.get('doctor_id')
        doctor = get_object_or_404(Doctor, id=doctor_id)
        form = DoctorForm(request.POST, instance=doctor)
        if form.is_valid():
            doctor = form.save()
            # Log the management activity
            DoctorManagement.objects.create(
                doctor=doctor,
                manager=request.user,
                action='updated',
                notes=f'Doctor {doctor.name} was updated in the system'
            )
            messages.success(request, f'Doctor {doctor.name} has been updated successfully!')
            return redirect('dashboard:manage_doctors')
    elif request.method == 'POST':
        form = DoctorForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            # Log the management activity
            DoctorManagement.objects.create(
                doctor=doctor,
                manager=request.user,
                action='added',
                notes=f'Doctor {doctor.name} was added to the system'
            )
            messages.success(request, f'Doctor {doctor.name} has been added successfully!')
            return redirect('dashboard:manage_doctors')
    else:
        form = DoctorForm()
    
    doctors = Doctor.objects.all()
    management_activities = DoctorManagement.objects.all().order_by('-timestamp')[:10]
    
    context = {
        'doctors': doctors,
        'management_activities': management_activities,
        'form': form,
        'hospitals': Hospital.objects.all(),
    }
    
    return render(request, 'dashboard/manage_doctors.html', context)

@login_required
def manage_hospitals(request):
    """View for managing hospitals"""
    # Only staff users can manage hospitals
    if not request.user.is_staff:
        return render(request, 'dashboard/access_denied.html')
    
    # Handle delete request
    if request.method == 'POST' and 'delete_hospital' in request.POST:
        hospital_id = request.POST.get('hospital_id')
        hospital = get_object_or_404(Hospital, id=hospital_id)
        hospital_name = hospital.name
        hospital.delete()
        # Log the management activity
        HospitalManagement.objects.create(
            hospital=hospital,
            manager=request.user,
            action='removed',
            notes=f'Hospital {hospital_name} was removed from the system'
        )
        messages.success(request, f'Hospital {hospital_name} has been deleted successfully!')
        return redirect('dashboard:manage_hospitals')
    
    # Handle edit request
    if request.method == 'POST' and 'edit_hospital' in request.POST:
        hospital_id = request.POST.get('hospital_id')
        hospital = get_object_or_404(Hospital, id=hospital_id)
        form = HospitalForm(request.POST, instance=hospital)
        if form.is_valid():
            hospital = form.save()
            # Log the management activity
            HospitalManagement.objects.create(
                hospital=hospital,
                manager=request.user,
                action='updated',
                notes=f'Hospital {hospital.name} was updated in the system'
            )
            messages.success(request, f'Hospital {hospital.name} has been updated successfully!')
            return redirect('dashboard:manage_hospitals')
    elif request.method == 'POST':
        form = HospitalForm(request.POST)
        if form.is_valid():
            hospital = form.save()
            # Log the management activity
            HospitalManagement.objects.create(
                hospital=hospital,
                manager=request.user,
                action='added',
                notes=f'Hospital {hospital.name} was added to the system'
            )
            messages.success(request, f'Hospital {hospital.name} has been added successfully!')
            return redirect('dashboard:manage_hospitals')
    else:
        form = HospitalForm()
    
    hospitals = Hospital.objects.all()
    management_activities = HospitalManagement.objects.all().order_by('-timestamp')[:10]
    
    context = {
        'hospitals': hospitals,
        'management_activities': management_activities,
        'form': form,
    }
    
    return render(request, 'dashboard/manage_hospitals.html', context)
