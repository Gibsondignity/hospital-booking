from django.db import models

class Hospital(models.Model):
    name = models.CharField(max_length=200)
    address = models.CharField(max_length=300)
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    def __str__(self):
        return self.name

class Doctor(models.Model):
    name = models.CharField(max_length=200)
    specialty = models.CharField(max_length=100)
    title = models.CharField(max_length=100, blank=True)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    education = models.CharField(max_length=300, blank=True)
    experience = models.IntegerField(default=0)
    image = models.CharField(max_length=300, blank=True)
    availability_data = models.JSONField(default=dict)  # Store availability as JSON
    
    def __str__(self):
        return f"Dr. {self.name} - {self.specialty}"
    
    def get_availability(self):
        """Return availability data"""
        return self.availability_data

class Appointment(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.CharField(max_length=20)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Appointment for {self.full_name} with {self.doctor.name} on {self.date} at {self.time}"
