from django.urls import path

from . import views

app_name = "appointment"

urlpatterns = [
    path("", views.appointment_list, name="list"),
    path("new/", views.appointment_create, name="create"),
    path("<int:pk>/status/", views.appointment_status, name="status"),
    path("<int:pk>/check-in/", views.appointment_check_in, name="check_in"),
]
