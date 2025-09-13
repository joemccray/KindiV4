from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from . import services
from .serializers import URLCheckRequestSerializer, URLCheckResponseSerializer


class PhishingIntelViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    ViewSet for checking a URL against the PhishTank database.
    """

    serializer_class = URLCheckRequestSerializer

    def create(self, request, *args, **kwargs):
        """
        Accepts a URL, checks it against PhishTank, and returns the result.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        url_to_check = serializer.validated_data["url"]

        result_record = services.check_url_for_phishing(url_to_check)

        response_serializer = URLCheckResponseSerializer(result_record)
        return Response(response_serializer.data, status=status.HTTP_200_OK)
