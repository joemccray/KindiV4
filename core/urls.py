from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EntityViewSet, EventViewSet, LocationViewSet, WorkspaceViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"entities", EntityViewSet)
router.register(r"locations", LocationViewSet)
router.register(r"events", EventViewSet)
router.register(r"workspaces", WorkspaceViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
]
