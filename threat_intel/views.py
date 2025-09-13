from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .serializers import IndicatorSerializer


class ThreatIntelViewSet(viewsets.ViewSet):
    """
    ViewSet for querying threat intelligence on various indicators.
    This is not a ModelViewSet because we have custom, non-resource-based actions.
    """

    # permission_classes = [IsAuthenticated] # Add permissions later

    @action(detail=False, methods=["get"], url_path=r"domain/(?P<domain_name>[^/]+)")
    def domain_lookup(self, request, domain_name=None):
        """
        Looks up threat intelligence for a domain.
        """
        if not domain_name:
            return Response(
                {"error": "Domain name not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        indicator = services.get_domain_intel(domain_name)
        serializer = IndicatorSerializer(indicator)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="ip/(?P<ip_address>[^/]+)")
    def ip_lookup(self, request, ip_address=None):
        """
        Looks up threat intelligence for an IP address.
        """
        if not ip_address:
            return Response(
                {"error": "IP address not provided."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        indicator = services.get_ip_intel(ip_address)
        serializer = IndicatorSerializer(indicator)
        return Response(serializer.data)

    @action(detail=False, methods=["get"], url_path="hash/(?P<file_hash>[^/]+)")
    def hash_lookup(self, request, file_hash=None):
        """
        Looks up threat intelligence for a file hash.
        """
        if not file_hash:
            return Response(
                {"error": "File hash not provided."}, status=status.HTTP_400_BAD_REQUEST
            )

        indicator = services.get_hash_intel(file_hash)
        serializer = IndicatorSerializer(indicator)
        return Response(serializer.data)
