from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    # Add any additional fields you want for your user model
    phone_number = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return self.username
