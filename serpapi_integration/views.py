from rest_framework import status, viewsets
from rest_framework.response import Response

from . import services
from .serializers import SerpApiQuerySerializer


class SerpApiViewSet(viewsets.ViewSet):
    """
    ViewSet for making calls to various SerpAPI search engines.
    """

    serializer_class = SerpApiQuerySerializer

    def _handle_query(self, request, query_function):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        query = serializer.validated_data["query"]

        results = query_function(query)

        return Response(results, status=status.HTTP_200_OK)

    def create_ai_overview_search(self, request, *args, **kwargs):
        return self._handle_query(request, services.search_google_ai_overview)

    def create_news_search(self, request, *args, **kwargs):
        return self._handle_query(request, services.search_google_news)

    def create_scholar_search(self, request, *args, **kwargs):
        return self._handle_query(request, services.search_google_scholar)

    def create_trends_search(self, request, *args, **kwargs):
        return self._handle_query(request, services.search_google_trends)

    def create_maps_search(self, request, *args, **kwargs):
        return self._handle_query(request, services.search_google_maps)

    def create_events_search(self, request, *args, **kwargs):
        return self._handle_query(request, services.search_google_events)

    def create_finance_search(self, request, *args, **kwargs):
        return self._handle_query(request, services.search_google_finance)

    def create_youtube_search(self, request, *args, **kwargs):
        return self._handle_query(request, services.search_youtube)
