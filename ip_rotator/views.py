from rest_framework import mixins, viewsets

from .models import ApiGatewayProxy
from .serializers import ApiGatewayProxySerializer


class ApiGatewayProxyViewSet(
    mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """
    A read-only ViewSet for listing and retrieving API Gateway Proxies.
    """

    queryset = ApiGatewayProxy.objects.all()
    serializer_class = ApiGatewayProxySerializer
    permission_classes = []  # In a real app, this should be IsAuthenticated or a custom permission
    lookup_field = "id"
