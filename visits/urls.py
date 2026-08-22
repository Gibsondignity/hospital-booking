from django.urls import path

from . import views

app_name = "visits"

urlpatterns = [
    path("", views.visit_list, name="list"),
    path("queue/", views.waiting_queue, name="queue"),
    path("walk-in/", views.walk_in, name="walk_in"),
    path("<int:pk>/status/", views.visit_status, name="status"),
]
