from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ThreatIntelViewSet

router = DefaultRouter()
router.register(r"query", ThreatIntelViewSet, basename="threatintel")

urlpatterns = [
    path("", include(router.urls)),
]
