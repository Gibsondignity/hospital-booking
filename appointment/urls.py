from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hospitals/', views.hospitals, name='hospitals'),
    path('hospital/<int:hospital_id>/', views.hospital_detail, name='hospital_detail'),
    path('doctor/<int:doctor_id>/', views.doctor_profile, name='doctor_profile'),
    path('book-appointment/', views.book_appointment, name='book_appointment'),
    path('appointment-success/<int:appointment_id>/', views.appointment_success, name='appointment_success'),

    # API endpoints
    path('api/hospitals/', views.get_hospitals, name='get_hospitals'),
    path('api/doctors/', views.get_doctors, name='get_doctors'),
    path('api/services/', views.get_services, name='get_services'),
    path('api/appointments/', views.create_appointment, name='create_appointment'),
]