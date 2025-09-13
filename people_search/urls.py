from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PeopleSearchViewSet

router = DefaultRouter()
router.register(r"search", PeopleSearchViewSet, basename="peoplesearch")

urlpatterns = [
    path("", include(router.urls)),
]
