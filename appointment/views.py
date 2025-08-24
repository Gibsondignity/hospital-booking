from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Hospital, Doctor, Appointment

def index(request):
    """Render the homepage"""
    # Get featured hospitals (first 3)
    featured_hospitals = Hospital.objects.all()[:3]
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
            'image': hospital.image
        })
    return render(request, 'hospitals.html', {
        'hospitals': hospitals,
        'hospitals_json': json.dumps(hospitals_json)
    })

def hospital_detail(request, hospital_id):
    """Render the hospital detail page"""
    hospital = get_object_or_404(Hospital, id=hospital_id)
    doctors = Doctor.objects.filter(hospital=hospital)
    
    # For equipment, we'll create some sample data since it's not in the model
    equipment = [
        {'name': 'MRI Scanner', 'description': 'High-resolution magnetic resonance imaging for detailed diagnostic imaging'},
        {'name': 'CT Scanner', 'description': 'Advanced computed tomography for rapid diagnostic imaging'},
        {'name': 'Ultrasound Machine', 'description': 'State-of-the-art ultrasound equipment for various diagnostic procedures'}
    ]
    
    return render(request, 'hospital-detail.html', {
        'hospital': hospital,
        'doctors': doctors,
        'equipment': equipment
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

@csrf_exempt
def create_appointment(request):
    """API endpoint to create a new appointment"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            appointment = Appointment(
                full_name=data['full_name'],
                email=data['email'],
                phone=data['phone'],
                hospital_id=data['hospital_id'],
                doctor_id=data['doctor_id'],
                date=data['date'],
                time=data['time'],
                reason=data['reason']
            )
            appointment.save()
            return JsonResponse({'success': True, 'appointmentId': appointment.id})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})
