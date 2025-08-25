from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('bookings/', views.manage_bookings, name='manage_bookings'),
    path('doctors/', views.manage_doctors, name='manage_doctors'),
    path('hospitals/', views.manage_hospitals, name='manage_hospitals'),
    path('appointments/', views.view_appointments, name='view_appointments'),
]