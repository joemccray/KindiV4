from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import services
from .models import PersonProfile, SearchQuery
from .serializers import (
    PersonProfileSerializer,
    SearchQueryCreateSerializer,
    SearchQuerySerializer,
)


class PeopleSearchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for initiating a people search and retrieving its status and results.
    """

    queryset = SearchQuery.objects.all()
    serializer_class = SearchQuerySerializer
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "create":
            return SearchQueryCreateSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        """
        Initiates a new search.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        query_filter = serializer.validated_data["filter"]

        search_query = services.initiate_reachstream_search(query_filter)

        output_serializer = SearchQuerySerializer(search_query)
        return Response(output_serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(detail=True, methods=["get"])
    def results(self, request, id=None):
        """
        Retrieves the results for a completed search query.
        """
        search_query = self.get_object()
        if search_query.status != SearchQuery.SearchStatus.COMPLETED:
            return Response(
                {"detail": "Search is not complete."}, status=status.HTTP_404_NOT_FOUND
            )

        results = PersonProfile.objects.filter(search_query=search_query)
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = PersonProfileSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PersonProfileSerializer(results, many=True)
        return Response(serializer.data)
