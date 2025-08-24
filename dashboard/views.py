from django.shortcuts import render, redirect
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
def manage_doctors(request):
    """View for managing doctors"""
    # Only staff users can manage doctors
    if not request.user.is_staff:
        return render(request, 'dashboard/access_denied.html')
    
    if request.method == 'POST':
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
    }
    
    return render(request, 'dashboard/manage_doctors.html', context)

@login_required
def manage_hospitals(request):
    """View for managing hospitals"""
    # Only staff users can manage hospitals
    if not request.user.is_staff:
        return render(request, 'dashboard/access_denied.html')
    
    if request.method == 'POST':
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
