from django.urls import path

from .views import health_check, whoami

app_name = "auth_clerk"

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("whoami/", whoami, name="whoami"),
]
