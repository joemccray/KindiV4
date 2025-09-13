from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PhishingIntelViewSet

router = DefaultRouter()
router.register(r"check", PhishingIntelViewSet, basename="phishing-check")

urlpatterns = [
    path("", include(router.urls)),
]
