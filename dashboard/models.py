# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.urls import reverse

from accounts.models import CustomUser

# Custom User Model with role support

# Hospital Model
class Hospital(models.Model):
    name = models.CharField(max_length=200, unique=True)
    address = models.CharField(max_length=300)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="Kenya")  # or your country
    location = models.CharField(max_length=200, help_text="e.g., GPS coordinates or neighborhood", blank=True)
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    # Image for frontend display
    image = models.ImageField(upload_to='hospitals/', blank=True, null=True, help_text="Hospital branding image")
    
    # Optional: gallery of images
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('hospital_detail', args=[str(self.id)])

    class Meta:
        ordering = ['name']


# Service Model (Each hospital offers services)
class Service(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    duration = models.PositiveIntegerField(default=30, help_text="Duration in minutes")
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='services')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} @ {self.hospital.name}"

    class Meta:
        unique_together = ('name', 'hospital')
        ordering = ['name']


# Doctor Model
class Doctor(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    name = models.CharField(max_length=200)
    title = models.CharField(max_length=50, blank=True, help_text="e.g., Dr., Prof.")
    specialty = models.CharField(max_length=100)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='doctors')
    
    bio = models.TextField(blank=True, help_text="Short biography")
    education = models.CharField(max_length=300, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    
    # Profile image
    image = models.ImageField(upload_to='doctors/', blank=True, null=True)
    
    # Availability stored as JSON (can be enhanced with proper availability model later)
    availability_data = models.JSONField(default=dict, blank=True, help_text="e.g., {'monday': '9:00-17:00'}")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Dr. {self.name} - {self.specialty}"

    def get_full_name(self):
        return f"{self.title} {self.name}".strip()


# Appointment Model
class Appointment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='appointments')  # New: link to service
    
    date = models.DateField()
    time = models.CharField(max_length=20)  # Could be improved with TimeField + slot logic
    reason = models.TextField(blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Appt: {self.full_name} | {self.hospital.name} | {self.date} {self.time}"

    class Meta:
        ordering = ['-created_at']
        unique_together = ('doctor', 'date', 'time')  # Prevent double-booking same slot


# Booking Model (Tracks user's booking of an appointment)
class Booking(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bookings')
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='confirmed')  # Synced or independent

    def __str__(self):
        return f"Booking: {self.user.username} → {self.appointment}"

    class Meta:
        ordering = ['-booking_date']


# Audit Logs
class DoctorManagement(models.Model):
    ACTION_CHOICES = [
        ('added', 'Added'),
        ('updated', 'Updated'),
        ('removed', 'Removed'),
        ('deactivated', 'Deactivated'),
    ]
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action.title()}: {self.doctor} by {self.manager}"


class HospitalManagement(models.Model):
    ACTION_CHOICES = [
        ('added', 'Added'),
        ('updated', 'Updated'),
        ('removed', 'Removed'),
        ('deactivated', 'Deactivated'),
    ]
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    manager = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    timestamp = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.action.title()} hospital: {self.hospital}"


# Blocked Time Slots Model
class BlockedTimeSlot(models.Model):
    """Model to store blocked time slots that cannot be booked"""
    BLOCK_TYPE_CHOICES = [
        ('doctor', 'Doctor Unavailable'),
        ('maintenance', 'Maintenance/Cleaning'),
        ('emergency', 'Emergency Block'),
        ('holiday', 'Holiday/Leave'),
        ('training', 'Staff Training'),
        ('other', 'Other Reason'),
    ]
    
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='blocked_slots')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='blocked_slots', null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPE_CHOICES, default='other')
    reason = models.TextField(blank=True, help_text="Optional reason for blocking")
    
    # Who created the block
    created_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, related_name='created_blocks')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Active status
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        doctor_info = f" - {self.doctor.name}" if self.doctor else " - All Doctors"
        return f"Blocked: {self.hospital.name}{doctor_info} on {self.date} {self.start_time}-{self.end_time}"
    
    def get_time_slots(self):
        """
        Return a list of individual 30-minute time slots that are blocked.
        Converts the start_time to end_time range into specific appointment slots.
        """
        from datetime import datetime, timedelta
        
        # Convert to datetime objects for manipulation
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        
        # Generate 30-minute slots
        slots = []
        current = start_dt
        while current < end_dt:
            slots.append(current.time().strftime('%H:%M'))
            current += timedelta(minutes=30)
        
        return slots
    
    class Meta:
        ordering = ['-date', '-start_time']
        indexes = [
            models.Index(fields=['hospital', 'date', 'is_active']),
            models.Index(fields=['doctor', 'date', 'is_active']),
        ]