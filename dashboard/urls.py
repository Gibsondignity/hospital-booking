from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bookings/', views.manage_bookings, name='manage_bookings'),
    path('doctors/', views.manage_doctors, name='manage_doctors'),
    path('hospitals/', views.manage_hospitals, name='manage_hospitals'),
    path('services/', views.manage_services, name='manage_services'),
    path('users/', views.manage_users, name='manage_users'),
    path('appointments/', views.view_appointments, name='view_appointments'),
]