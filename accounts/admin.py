from django.contrib import admin
from .models import CustomUser

# Register your models here.
admin.site.site_header = "Hospital Management Admin"
admin.site.site_title = "Hospital Management Admin Portal"
admin.site.index_title = "Welcome to Hospital Management Admin Portal"
admin.site.register(CustomUser)