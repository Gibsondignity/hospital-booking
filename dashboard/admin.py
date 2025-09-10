from django.contrib import admin
from .models import *

# Register your models here.
# Register your models here.
admin.site.site_header = "Hospital Management Admin"
admin.site.site_title = "Hospital Management Admin Portal"
admin.site.index_title = "Welcome to Hospital Management Admin Portal"

admin.site.register(Doctor)
admin.site.register(Appointment)
admin.site.register(Hospital)
admin.site.register(Service)
admin.site.register(Booking)
admin.site.register(DoctorManagement)
admin.site.register(HospitalManagement)