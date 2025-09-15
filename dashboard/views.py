from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import models
from accounts.models import CustomUser
from .models import Booking, DoctorManagement, HospitalManagement, Hospital, Doctor, Appointment, Service, BlockedTimeSlot
from .forms import HospitalForm, DoctorForm, ServiceForm
from django.contrib.auth.forms import UserCreationForm

@login_required
def dashboard(request):
    """Main dashboard view with comprehensive role-based analytics"""
    user = request.user

    # Get user's appointments based on role
    if user.role == 'admin':
        # System admin can see all appointments
        user_appointments = Appointment.objects.all().order_by('-created_at')[:10]
        appointments_count = Appointment.objects.all().count()
    elif user.role in ['hospital_admin', 'staff'] and user.hospital:
        # Hospital staff can see all appointments for their hospital
        user_appointments = Appointment.objects.filter(hospital=user.hospital).order_by('-created_at')[:10]
        appointments_count = Appointment.objects.filter(hospital=user.hospital).count()
    else:
        # Patients can only see their own appointments
        user_appointments = Appointment.objects.filter(email=user.email).order_by('-created_at')[:10]
        appointments_count = Appointment.objects.filter(email=user.email).count()

    # Get recent bookings
    recent_bookings = Booking.objects.filter(user=user).order_by('-booking_date')[:5]

    # Initialize variables
    doctor_management = DoctorManagement.objects.none()
    hospital_management = HospitalManagement.objects.none()
    hospitals_with_services = Hospital.objects.none()
    hospitals_count = 0
    doctors_count = 0
    services_count = 0
    confirmed_appointments_count = 0
    pending_appointments_count = 0

    # Get data based on user role
    if user.role == 'admin':
        # System Admin - Full system analytics
        doctor_management = DoctorManagement.objects.all().order_by('-timestamp')[:5]
        hospital_management = HospitalManagement.objects.all().order_by('-timestamp')[:5]
        hospitals_with_services = Hospital.objects.prefetch_related('doctors', 'services', 'appointments').all()[:6]
        hospitals_count = Hospital.objects.count()
        doctors_count = Doctor.objects.count()
        services_count = Service.objects.count()
        confirmed_appointments_count = Appointment.objects.filter(status='confirmed').count()
        pending_appointments_count = Appointment.objects.filter(status='pending').count()

    elif user.role in ['hospital_admin', 'staff'] and user.hospital:
        # Hospital Admin & Staff - Hospital-specific analytics
        doctor_management = DoctorManagement.objects.filter(
            doctor__hospital=user.hospital
        ).order_by('-timestamp')[:5]
        hospital_management = HospitalManagement.objects.filter(
            hospital=user.hospital
        ).order_by('-timestamp')[:5]
        hospitals_with_services = Hospital.objects.filter(id=user.hospital.id).prefetch_related('doctors', 'services', 'appointments')
        hospitals_count = 1
        doctors_count = Doctor.objects.filter(hospital=user.hospital).count()
        services_count = Service.objects.filter(hospital=user.hospital).count()
        confirmed_appointments_count = Appointment.objects.filter(hospital=user.hospital, status='confirmed').count()
        pending_appointments_count = Appointment.objects.filter(hospital=user.hospital, status='pending').count()

    else:
        # Patients - Limited view
        doctor_management = DoctorManagement.objects.none()
        hospital_management = HospitalManagement.objects.none()
        hospitals_with_services = Hospital.objects.prefetch_related('doctors').all()[:6]
        hospitals_count = Hospital.objects.count()
        doctors_count = Doctor.objects.count()
        services_count = Service.objects.count()
        confirmed_appointments_count = Appointment.objects.filter(email=user.email, status='confirmed').count()
        pending_appointments_count = Appointment.objects.filter(email=user.email, status='pending').count()

    # Calculate additional metrics
    total_appointments = confirmed_appointments_count + pending_appointments_count
    appointment_completion_rate = (confirmed_appointments_count / total_appointments * 100) if total_appointments > 0 else 0

    context = {
        'user_appointments': user_appointments,
        'recent_bookings': recent_bookings,
        'doctor_management': doctor_management,
        'hospital_management': hospital_management,
        'hospitals_with_services': hospitals_with_services,
        'hospitals_count': hospitals_count,
        'doctors_count': doctors_count,
        'services_count': services_count,
        'appointments_count': appointments_count,
        'confirmed_appointments_count': confirmed_appointments_count,
        'pending_appointments_count': pending_appointments_count,
        'appointment_completion_rate': round(appointment_completion_rate, 1),
        'user_role': user.role,
        'user_hospital': user.hospital,
        'request': request,  # Add request to context for template access
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def manage_bookings(request):
    """View for managing bookings"""
    user = request.user
    
    # Handle appointment status changes (for staff roles)
    if request.method == 'POST' and user.role in ['admin', 'hospital_admin', 'staff']:
        action = request.POST.get('action')
        appointment_id = request.POST.get('appointment_id')
        
        if appointment_id and action:
            try:
                appointment = Appointment.objects.get(id=appointment_id)
                
                # Check if user has permission to manage this appointment
                if user.role == 'admin' or (user.hospital and appointment.hospital == user.hospital):
                    if action == 'confirm':
                        appointment.status = 'confirmed'
                        appointment.save()
                        messages.success(request, f'Appointment for {appointment.full_name} has been confirmed.')
                    elif action == 'cancel':
                        appointment.status = 'cancelled'
                        appointment.save()
                        messages.success(request, f'Appointment for {appointment.full_name} has been cancelled.')
                else:
                    messages.error(request, 'You do not have permission to manage this appointment.')
            except Appointment.DoesNotExist:
                messages.error(request, 'Appointment not found.')
        
        return redirect('manage_bookings')
    
    # Get appointments based on user role (staff manage appointments, not just bookings)
    if user.role == 'admin':
        # System admin sees all appointments
        appointments = Appointment.objects.all().order_by('-created_at')
    elif user.role in ['hospital_admin', 'staff'] and user.hospital:
        # Hospital admin and staff see appointments for their hospital
        appointments = Appointment.objects.filter(hospital=user.hospital).order_by('-created_at')
    else:
        # Patients see only their own bookings (actual Booking objects)
        bookings = Booking.objects.filter(user=user).order_by('-booking_date')
        appointments = [booking.appointment for booking in bookings]
    
    context = {
        'appointments': appointments,
        'user_role': user.role,
        'user_hospital': user.hospital,
    }
    
    return render(request, 'dashboard/manage_bookings.html', context)

@login_required
def view_appointments(request):
    """View for viewing appointments (Main Admin, Hospital Admin, Staff)"""
    user = request.user
    
    # Handle appointment status changes (for staff roles)
    if request.method == 'POST' and user.role in ['admin', 'hospital_admin', 'staff']:
        action = request.POST.get('action')
        appointment_id = request.POST.get('appointment_id')
        
        if appointment_id and action:
            try:
                appointment = Appointment.objects.get(id=appointment_id)
                
                # Check if user has permission to manage this appointment
                if user.role == 'admin' or (user.hospital and appointment.hospital == user.hospital):
                    if action == 'confirm':
                        appointment.status = 'confirmed'
                        appointment.save()
                        messages.success(request, f'Appointment for {appointment.full_name} has been confirmed.')
                    elif action == 'cancel':
                        appointment.status = 'cancelled'
                        appointment.save()
                        messages.success(request, f'Appointment for {appointment.full_name} has been cancelled.')
                    elif action == 'complete':
                        appointment.status = 'completed'
                        appointment.save()
                        messages.success(request, f'Appointment for {appointment.full_name} has been marked as completed.')
                else:
                    messages.error(request, 'You do not have permission to manage this appointment.')
            except Appointment.DoesNotExist:
                messages.error(request, 'Appointment not found.')
        
        return redirect('view_appointments')
    
    # Get appointments based on user role
    if user.role == 'admin':
        # System admin can view all appointments
        appointments = Appointment.objects.all().order_by('-created_at')
    elif user.role in ['hospital_admin', 'staff'] and user.hospital:
        # Hospital admin and staff can view appointments for their hospital
        appointments = Appointment.objects.filter(hospital=user.hospital).order_by('-created_at')
    else:
        # Patients cannot access this page
        return render(request, 'dashboard/access_denied.html')

    context = {
        'appointments': appointments,
        'user_role': user.role,
        'user_hospital': user.hospital,
    }
    
    return render(request, 'dashboard/view_appointments.html', context)

@login_required
def manage_doctors(request):
    """View for managing doctors (Hospital Admin & Staff)"""
    # Role-based access control
    if request.user.role == 'admin':
        # System admin can manage all doctors
        doctors_queryset = Doctor.objects.all()
        hospitals_queryset = Hospital.objects.all()
    elif request.user.role in ['hospital_admin', 'staff'] and request.user.hospital:
        # Hospital admin and staff can only manage doctors in their hospital
        doctors_queryset = Doctor.objects.filter(hospital=request.user.hospital)
        hospitals_queryset = Hospital.objects.filter(id=request.user.hospital.id)
    else:
        # Patients cannot access this page
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
        return redirect('manage_doctors')
    
    # Handle edit request
    if request.method == 'POST' and 'edit_doctor' in request.POST:
        doctor_id = request.POST.get('doctor_id')
        doctor = get_object_or_404(Doctor, id=doctor_id)
        form = DoctorForm(request.POST, request.FILES, instance=doctor)
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
            return redirect('manage_doctors')
    elif request.method == 'POST':
        form = DoctorForm(request.POST, request.FILES)
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
            return redirect('manage_doctors')
    else:
        form = DoctorForm()
    
    doctors = doctors_queryset
    # Filter management activities based on user's hospital if they're a hospital admin
    if request.user.role == 'hospital_admin' and request.user.hospital:
        management_activities = DoctorManagement.objects.filter(
            doctor__hospital=request.user.hospital
        ).order_by('-timestamp')[:10]
    else:
        management_activities = DoctorManagement.objects.all().order_by('-timestamp')[:10]

    context = {
        'doctors': doctors,
        'management_activities': management_activities,
        'form': form,
        'hospitals': hospitals_queryset,
        'user_role': request.user.role,
        'user_hospital': request.user.hospital,
    }
    
    return render(request, 'dashboard/manage_doctors.html', context)

@login_required
def manage_hospitals(request):
    """View for managing hospitals (Main Admin only)"""
    # Only system admins can manage hospitals
    if request.user.role != 'admin':
        return render(request, 'dashboard/access_denied.html')

    hospitals_queryset = Hospital.objects.all()
    can_add_hospital = True
    
    # Handle hospital admin assignment
    if request.method == 'POST' and 'assign_hospital_admin' in request.POST:
        hospital_id = request.POST.get('hospital_id')
        user_email = request.POST.get('user_email')
        hospital = get_object_or_404(Hospital, id=hospital_id)

        try:
            user = CustomUser.objects.get(email=user_email)
            user.role = 'hospital_admin'
            user.hospital = hospital
            user.save()
            messages.success(request, f'{user.username} has been assigned as Hospital Admin for {hospital.name}!')
        except CustomUser.DoesNotExist:
            messages.error(request, f'User with email {user_email} not found.')
        except Exception as e:
            messages.error(request, f'Error assigning hospital admin: {str(e)}')

        return redirect('manage_hospitals')

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
        return redirect('manage_hospitals')
    
    # Handle edit request
    if request.method == 'POST' and 'edit_hospital' in request.POST:
        hospital_id = request.POST.get('hospital_id')
        hospital = get_object_or_404(Hospital, id=hospital_id)
        form = HospitalForm(request.POST, request.FILES, instance=hospital)
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
            return redirect('manage_hospitals')
    elif request.method == 'POST':
        form = HospitalForm(request.POST, request.FILES)
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
            return redirect('manage_hospitals')
    else:
        form = HospitalForm()
    
    hospitals = hospitals_queryset
    # Filter management activities based on user's role
    if request.user.role == 'hospital_admin' and request.user.hospital:
        management_activities = HospitalManagement.objects.filter(
            hospital=request.user.hospital
        ).order_by('-timestamp')[:10]
    else:
        management_activities = HospitalManagement.objects.all().order_by('-timestamp')[:10]

    # Add hospital admin information to each hospital
    hospitals_with_admins = []
    for hospital in hospitals:
        try:
            hospital_admin = CustomUser.objects.filter(
                hospital=hospital,
                role='hospital_admin'
            ).first()
            hospital.hospital_admin = hospital_admin
        except:
            hospital.hospital_admin = None
        hospitals_with_admins.append(hospital)

    context = {
        'hospitals': hospitals_with_admins,
        'management_activities': management_activities,
        'form': form,
        'can_add_hospital': can_add_hospital,
        'user_role': request.user.role,
        'user_hospital': request.user.hospital,
    }

    return render(request, 'dashboard/manage_hospitals.html', context)

@login_required
def manage_services(request):
    """View for managing services (Hospital Admin & Staff)"""
    # Role-based access control
    if request.user.role == 'admin':
        # System admin can manage all services
        services_queryset = Service.objects.all().order_by('hospital__name', 'name')
        hospitals_queryset = Hospital.objects.all()
    elif request.user.role in ['hospital_admin', 'staff'] and request.user.hospital:
        # Hospital admin and staff can only manage services in their hospital
        services_queryset = Service.objects.filter(hospital=request.user.hospital).order_by('name')
        hospitals_queryset = Hospital.objects.filter(id=request.user.hospital.id)
    else:
        # Patients cannot access this page
        return render(request, 'dashboard/access_denied.html')

    # Handle delete request
    if request.method == 'POST' and 'delete_service' in request.POST:
        service_id = request.POST.get('service_id')
        service = get_object_or_404(Service, id=service_id)
        service_name = service.name
        service.delete()
        messages.success(request, f'Service {service_name} has been deleted successfully!')
        return redirect('manage_services')

    # Handle edit request
    if request.method == 'POST' and 'edit_service' in request.POST:
        service_id = request.POST.get('service_id')
        service = get_object_or_404(Service, id=service_id)
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service {service.name} has been updated successfully!')
            return redirect('manage_services')
    elif request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            service = form.save()
            messages.success(request, f'Service {service.name} has been added successfully!')
            return redirect('manage_services')
    else:
        form = ServiceForm()

    services = services_queryset

    context = {
        'services': services,
        'form': form,
        'hospitals': hospitals_queryset,
        'user_role': request.user.role,
        'user_hospital': request.user.hospital,
    }

    return render(request, 'dashboard/manage_services.html', context)

@login_required
def manage_users(request):
    """View for managing users and assigning them to hospitals"""
    # Main Admin & Hospital Admin can manage users
    if request.user.role not in ['admin', 'hospital_admin']:
        return render(request, 'dashboard/access_denied.html')

    # Handle user creation
    if request.method == 'POST' and 'create_user' in request.POST:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        hospital_id = request.POST.get('hospital')

        try:
            # Create new user
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role
            )
            
            # Assign hospital if needed
            if role in ['hospital_admin', 'staff'] and hospital_id:
                user.hospital = Hospital.objects.get(id=hospital_id)
                user.save()
            
            messages.success(request, f'User {username} has been created successfully!')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
        
        return redirect('manage_users')

    # Handle role and hospital assignment
    if request.method == 'POST' and 'update_user' in request.POST:
        user_id = request.POST.get('user_id')
        new_role = request.POST.get('role')
        hospital_id = request.POST.get('hospital')

        try:
            user = CustomUser.objects.get(id=user_id)
            user.role = new_role

            if new_role in ['hospital_admin', 'staff']:
                if hospital_id:
                    user.hospital = Hospital.objects.get(id=hospital_id)
                else:
                    user.hospital = None
            else:
                # System admin and patients don't have hospitals
                user.hospital = None

            user.save()
            messages.success(request, f'User {user.username} has been updated successfully!')
        except CustomUser.DoesNotExist:
            messages.error(request, 'User not found.')
        except Hospital.DoesNotExist:
            messages.error(request, 'Hospital not found.')
        except Exception as e:
            messages.error(request, f'Error updating user: {str(e)}')

        return redirect('manage_users')

    # Get users based on role
    if request.user.role == 'admin':
        # Main Admin can see all users except themselves
        users = CustomUser.objects.exclude(id=request.user.id).order_by('username')
    elif request.user.role == 'hospital_admin' and request.user.hospital:
        # Hospital Admin can see all users in their hospital and unassigned staff/patients
        users = CustomUser.objects.filter(
            models.Q(hospital=request.user.hospital) |
            models.Q(hospital__isnull=True, role__in=['staff', 'patient'])
        ).exclude(id=request.user.id).order_by('username')
    else:
        users = CustomUser.objects.none()

    # Filter available hospitals and roles based on current user's role
    if request.user.role == 'admin':
        available_hospitals = Hospital.objects.all()
        available_roles = CustomUser.ROLE_CHOICES
    elif request.user.role == 'hospital_admin' and request.user.hospital:
        available_hospitals = Hospital.objects.filter(id=request.user.hospital.id)
        # Hospital admin can only create staff and manage patients
        available_roles = [
            ('staff', 'Hospital Staff'),
            ('patient', 'Patient'),
        ]
    else:
        available_hospitals = Hospital.objects.none()
        available_roles = []

    context = {
        'users': users,
        'hospitals': available_hospitals,
        'role_choices': available_roles,
        'user_role': request.user.role,
        'user_hospital': request.user.hospital,
    }

    return render(request, 'dashboard/manage_users.html', context)

@login_required
def manage_blocked_slots(request):
    """View for managing blocked time slots (Hospital Admin & Staff)"""
    user = request.user
    
    # Role-based access control
    if user.role not in ['admin', 'hospital_admin', 'staff']:
        return render(request, 'dashboard/access_denied.html')
    
    # Handle creating new blocked slot
    if request.method == 'POST' and 'create_block' in request.POST:
        try:
            hospital_id = request.POST.get('hospital')
            doctor_id = request.POST.get('doctor')
            date = request.POST.get('date')
            start_time = request.POST.get('start_time')
            end_time = request.POST.get('end_time')
            block_type = request.POST.get('block_type')
            reason = request.POST.get('reason', '')

            # Validate permissions
            if user.role in ['hospital_admin', 'staff'] and user.hospital:
                if int(hospital_id) != user.hospital.id:
                    messages.error(request, 'You can only block slots for your hospital.')
                    return redirect('manage_blocked_slots')

            blocked_slot = BlockedTimeSlot.objects.create(
                hospital_id=hospital_id,
                doctor_id=doctor_id if doctor_id else None,
                date=date,
                start_time=start_time,
                end_time=end_time,
                block_type=block_type,
                reason=reason,
                created_by=user
            )
            
            doctor_name = blocked_slot.doctor.name if blocked_slot.doctor else "All Doctors"
            messages.success(request, f'Time slot blocked successfully for {doctor_name} on {date}')
            
        except Exception as e:
            messages.error(request, f'Error creating blocked slot: {str(e)}')
        
        return redirect('manage_blocked_slots')
    
    # Handle deleting blocked slot
    if request.method == 'POST' and 'delete_block' in request.POST:
        block_id = request.POST.get('block_id')
        try:
            blocked_slot = get_object_or_404(BlockedTimeSlot, id=block_id)
            
            # Check permissions
            if user.role in ['hospital_admin', 'staff'] and user.hospital:
                if blocked_slot.hospital != user.hospital:
                    messages.error(request, 'You can only delete blocks for your hospital.')
                    return redirect('manage_blocked_slots')
            
            doctor_name = blocked_slot.doctor.name if blocked_slot.doctor else "All Doctors"
            blocked_slot.delete()
            messages.success(request, f'Blocked slot removed for {doctor_name}')
            
        except Exception as e:
            messages.error(request, f'Error deleting blocked slot: {str(e)}')
        
        return redirect('manage_blocked_slots')
    
    # Get blocked slots based on user role
    if user.role == 'admin':
        blocked_slots = BlockedTimeSlot.objects.select_related('hospital', 'doctor', 'created_by').all()
        hospitals_queryset = Hospital.objects.all()
    elif user.role in ['hospital_admin', 'staff'] and user.hospital:
        blocked_slots = BlockedTimeSlot.objects.select_related('hospital', 'doctor', 'created_by').filter(hospital=user.hospital)
        hospitals_queryset = Hospital.objects.filter(id=user.hospital.id)
    else:
        blocked_slots = BlockedTimeSlot.objects.none()
        hospitals_queryset = Hospital.objects.none()

    context = {
        'blocked_slots': blocked_slots.order_by('-created_at'),
        'hospitals': hospitals_queryset,
        'block_types': BlockedTimeSlot.BLOCK_TYPE_CHOICES,
        'user_role': user.role,
        'user_hospital': user.hospital,
    }
    
    return render(request, 'dashboard/manage_blocked_slots.html', context)
