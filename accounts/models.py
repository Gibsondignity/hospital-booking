from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'System Admin'),           # Full access
        ('hospital_admin', 'Hospital Admin'), # Manages one hospital
        ('staff', 'Hospital Staff'),         # Limited access (e.g., reception)
        ('patient', 'Patient'),              # Regular user
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    
    # Link to hospital (only for hospital_admin, staff; null for system admin/patient)
    hospital = models.ForeignKey('dashboard.Hospital', on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_hospital_admin(self):
        return self.role == 'hospital_admin'

    @property
    def is_staff_or_admin(self):
        return self.role in ['hospital_admin', 'staff']