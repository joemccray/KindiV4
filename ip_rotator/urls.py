from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ApiGatewayProxyViewSet

router = DefaultRouter()
router.register(r"proxies", ApiGatewayProxyViewSet, basename="apigatewayproxy")

urlpatterns = [
    path("", include(router.urls)),
]
