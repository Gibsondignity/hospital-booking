from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
import json
from datetime import datetime, timedelta
from dashboard.models import Hospital, Doctor, Appointment, Service

# Helper functions for appointment validation
def check_pending_appointments(email, phone):
    """
    Check if a patient has any pending appointments.
    Returns True if there are pending appointments, False otherwise.
    """
    pending_appointments = Appointment.objects.filter(
        Q(email=email) | Q(phone=phone),
        status='pending'
    )
    return pending_appointments.exists()

def check_approved_appointment_cooldown(email, phone):
    """
    Check if a patient has had an approved appointment within the last month.
    Returns True if they need to wait, False if they can book.
    """
    one_month_ago = timezone.now() - timedelta(days=30)
    recent_approved = Appointment.objects.filter(
        Q(email=email) | Q(phone=phone),
        status__in=['confirmed', 'completed'],
        created_at__gte=one_month_ago
    )
    return recent_approved.exists()

def validate_appointment_booking(email, phone):
    """
    Validate if a patient can book a new appointment based on business rules.
    Returns (can_book: bool, error_message: str)
    """
    # Check for pending appointments first
    if check_pending_appointments(email, phone):
        return False, "You have a pending appointment that has not been approved yet. Please wait for approval before booking another appointment."
    
    # Check for recent approved appointments (1-month cooldown)
    if check_approved_appointment_cooldown(email, phone):
        return False, "You have had an approved appointment within the last month. Please wait 30 days from your last appointment before booking a new one."
    
    return True, None

def index(request):
    """Render the homepage"""
    # Get random featured hospitals (3 random hospitals)
    import random
    all_hospitals = list(Hospital.objects.all())
    if len(all_hospitals) >= 3:
        featured_hospitals = random.sample(all_hospitals, 3)
    else:
        featured_hospitals = all_hospitals
    return render(request, 'index.html', {'featured_hospitals': featured_hospitals})

def hospitals(request):
    """Render the hospitals listing page"""
    hospitals = Hospital.objects.all()
    # Convert hospitals to JSON for JavaScript filtering
    hospitals_json = []
    for hospital in hospitals:
        hospitals_json.append({
            'id': hospital.id,
            'name': hospital.name,
            'location': hospital.location,
            'description': hospital.description,
            'phone_number': hospital.phone_number,
            'image': hospital.image.url if hospital.image else None
        })
    return render(request, 'hospitals.html', {
        'hospitals': hospitals,
        'hospitals_json': json.dumps(hospitals_json)
    })

def hospital_detail(request, hospital_id):
    """Render the hospital detail page"""
    hospital = get_object_or_404(Hospital, id=hospital_id)
    doctors = Doctor.objects.filter(hospital=hospital)
    services = Service.objects.filter(hospital=hospital, is_active=True)

    return render(request, 'hospital-detail.html', {
        'hospital': hospital,
        'doctors': doctors,
        'services': services
    })

def doctor_profile(request, doctor_id):
    """Render the doctor profile page"""
    doctor = get_object_or_404(Doctor, id=doctor_id)
    hospital = doctor.hospital
    return render(request, 'doctor-profile.html', {
        'doctor': doctor,
        'hospital': hospital
    })

def book_appointment(request):
    """Render the book appointment page"""
    return render(request, 'book-appointment.html')

def appointment_success(request, appointment_id):
    """Render the appointment success page"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'appointment_success.html', {
        'appointment': appointment
    })

# API Views for AJAX requests
def get_hospitals(request):
    """API endpoint to get all hospitals"""
    hospitals = Hospital.objects.all().values('id', 'name')
    return JsonResponse(list(hospitals), safe=False)

def get_doctors(request):
    """API endpoint to get doctors for a specific hospital"""
    hospital_id = request.GET.get('hospitalId')
    if hospital_id:
        doctors = Doctor.objects.filter(hospital_id=hospital_id).values('id', 'name', 'specialty', 'availability_data')
        doctors_list = []
        for doctor in doctors:
            doctors_list.append({
                'id': doctor['id'],
                'name': doctor['name'],
                'specialty': doctor['specialty'],
                'availability': doctor['availability_data']
            })
        return JsonResponse(doctors_list, safe=False)
    return JsonResponse([], safe=False)

def get_services(request):
    """API endpoint to get services for a specific hospital"""
    hospital_id = request.GET.get('hospitalId')
    if hospital_id:
        services = Service.objects.filter(hospital_id=hospital_id, is_active=True).values('id', 'name', 'description', 'duration')
        services_list = []
        for service in services:
            services_list.append({
                'id': service['id'],
                'name': service['name'],
                'description': service['description'],
                'duration': service['duration']
            })
        return JsonResponse(services_list, safe=False)
    return JsonResponse([], safe=False)

@csrf_exempt
def create_appointment(request):
    """Create a new appointment - handles both AJAX and form submissions"""
    if request.method == 'POST':
        try:
            # Check if this is an AJAX request or form submission
            if request.content_type == 'application/json' or 'application/json' in request.META.get('HTTP_CONTENT_TYPE', ''):
                # AJAX request - return JSON
                data = json.loads(request.body)
            else:
                # Regular form submission - get data from POST
                data = request.POST

            # Extract email and phone for validation
            email = data['email']
            phone = data['phone']
            
            # Validate appointment booking based on business rules
            can_book, error_message = validate_appointment_booking(email, phone)
            
            if not can_book:
                # Return appropriate error response
                if request.content_type == 'application/json' or 'application/json' in request.META.get('HTTP_CONTENT_TYPE', ''):
                    return JsonResponse({'success': False, 'error': error_message})
                else:
                    messages.error(request, error_message)
                    return redirect('book_appointment')

            appointment = Appointment(
                full_name=data['full_name'],
                email=email,
                phone=phone,
                hospital_id=data['hospital_id'],
                doctor_id=data['doctor_id'],
                service_id=data.get('service_id'),  # Optional service
                date=data['date'],
                time=data['time'],
                reason=data['reason']
            )
            appointment.save()

            # Check if this was an AJAX request
            if request.content_type == 'application/json' or 'application/json' in request.META.get('HTTP_CONTENT_TYPE', ''):
                return JsonResponse({'success': True, 'appointmentId': appointment.id})
            else:
                # Regular form submission - redirect to success page
                messages.success(request, 'Your appointment has been booked successfully!')
                return redirect('appointment_success', appointment_id=appointment.id)

        except Exception as e:
            if request.content_type == 'application/json' or 'application/json' in request.META.get('HTTP_CONTENT_TYPE', ''):
                return JsonResponse({'success': False, 'error': str(e)})
            else:
                messages.error(request, f'Error booking appointment: {str(e)}')
                return redirect('book_appointment')
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Test function to validate the implementation works correctly
def test_appointment_validation():
    """
    Test function to verify the appointment validation logic works correctly.
    This function can be called from Django shell or during development.
    """
    from django.utils import timezone
    from datetime import timedelta
    
    # Test email and phone
    test_email = "test@example.com"
    test_phone = "+233123456789"
    
    print("Testing appointment validation logic...")
    
    # Test 1: No existing appointments - should allow booking
    can_book, error_msg = validate_appointment_booking(test_email, test_phone)
    print(f"Test 1 (No appointments): Can book = {can_book}, Error = {error_msg}")
    assert can_book == True, "Should allow booking when no appointments exist"
    
    # Test 2: Create a pending appointment
    hospital = Hospital.objects.first()
    doctor = Doctor.objects.first()
    service = Service.objects.first()
    
    if hospital and doctor:
        pending_appointment = Appointment.objects.create(
            full_name="Test User",
            email=test_email,
            phone=test_phone,
            hospital=hospital,
            doctor=doctor,
            service=service,
            date=timezone.now().date() + timedelta(days=1),
            time="10:00",
            reason="Test appointment",
            status='pending'
        )
        
        # Test that pending appointment prevents new booking
        can_book, error_msg = validate_appointment_booking(test_email, test_phone)
        print(f"Test 2 (Pending appointment): Can book = {can_book}, Error = {error_msg}")
        assert can_book == False, "Should prevent booking when pending appointment exists"
        assert "pending appointment" in error_msg.lower(), "Error message should mention pending appointment"
        
        # Change status to confirmed and test cooldown
        pending_appointment.status = 'confirmed'
        pending_appointment.save()
        
        can_book, error_msg = validate_appointment_booking(test_email, test_phone)
        print(f"Test 3 (Recent approved): Can book = {can_book}, Error = {error_msg}")
        assert can_book == False, "Should prevent booking when recent approved appointment exists"
        assert "within the last month" in error_msg.lower(), "Error message should mention cooldown period"
        
        # Test with different email/phone (should allow booking)
        can_book, error_msg = validate_appointment_booking("different@example.com", "+233987654321")
        print(f"Test 4 (Different user): Can book = {can_book}, Error = {error_msg}")
        assert can_book == True, "Should allow booking for different user"
        
        # Clean up test data
        pending_appointment.delete()
        
        print("All tests passed! ✅")
        return True
    else:
        print("⚠️  Cannot run full tests - no hospital/doctor data found")
        return False
