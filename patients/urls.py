from django.urls import path

from . import views

app_name = "patients"

urlpatterns = [
    path("", views.patient_list, name="list"),
    path("new/", views.patient_create, name="create"),
    path("<int:pk>/", views.patient_detail, name="detail"),
    path("<int:pk>/edit/", views.patient_update, name="update"),
    path("<int:pk>/medical-history/", views.medical_history_update, name="medical_history"),
]
