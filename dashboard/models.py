from django.db import models
from appointment.models import Hospital, Doctor, Appointment
from accounts.models import CustomUser

class Booking(models.Model):
    """Model to track bookings made by users"""
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending')  # pending, confirmed, cancelled
    
    def __str__(self):
        return f"Booking {self.id} - {self.user.username}"

class DoctorManagement(models.Model):
    """Model to track doctor management activities"""
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # added, updated, removed
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.action} - {self.doctor.name} by {self.manager.username}"
        
class HospitalManagement(models.Model):
    """Model to track hospital management activities"""
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    manager = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    action = models.CharField(max_length=50)  # added, updated, removed
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.action} - {self.hospital.name} by {self.manager.username}"
