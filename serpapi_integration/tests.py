import os
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import SerpApiSearch


class SerpApiModelTest(TestCase):
    def test_create_serpapi_search(self):
        search = SerpApiSearch.objects.create(
            engine="google_news",
            search_parameters={"q": "testing"},
            raw_response={"results": []},
        )
        self.assertEqual(SerpApiSearch.objects.count(), 1)
        self.assertIn("google_news search", str(search))


class SerpApiServiceTest(TestCase):
    @patch("serpapi_integration.services.GoogleSearch")
    @patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"})
    def test_search_google_news_service(self, mock_google_search):
        # Configure the mock to return a predictable dictionary
        mock_instance = mock_google_search.return_value
        mock_instance.get_dict.return_value = {
            "search_metadata": {"status": "Success"},
            "news_results": [{"title": "Test News"}],
        }

        from . import services

        results = services.search_google_news("test")

        self.assertEqual(results["search_metadata"]["status"], "Success")
        self.assertEqual(SerpApiSearch.objects.count(), 1)
        search_log = SerpApiSearch.objects.first()
        self.assertEqual(search_log.engine, "google_news")
        self.assertEqual(search_log.search_parameters["q"], "test")


class SerpApiEndpointTest(APITestCase):
    def _test_endpoint(self, url_name, service_path, mock_return_value):
        with patch(service_path) as mock_service_call:
            mock_service_call.return_value = mock_return_value

            url = reverse(url_name)
            data = {"query": "test"}

            response = self.client.post(url, data, format="json")

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            mock_service_call.assert_called_once_with("test")
            self.assertEqual(response.data["query"], "test")

    def test_all_endpoints(self):
        endpoints = [
            (
                "serpapi-ai-overview",
                "serpapi_integration.views.services.search_google_ai_overview",
            ),
            ("serpapi-news", "serpapi_integration.views.services.search_google_news"),
            (
                "serpapi-scholar",
                "serpapi_integration.views.services.search_google_scholar",
            ),
            (
                "serpapi-trends",
                "serpapi_integration.views.services.search_google_trends",
            ),
            ("serpapi-maps", "serpapi_integration.views.services.search_google_maps"),
            (
                "serpapi-events",
                "serpapi_integration.views.services.search_google_events",
            ),
            (
                "serpapi-finance",
                "serpapi_integration.views.services.search_google_finance",
            ),
            ("serpapi-youtube", "serpapi_integration.views.services.search_youtube"),
        ]

        for url_name, service_path in endpoints:
            with self.subTest(endpoint=url_name):
                self._test_endpoint(
                    url_name, service_path, {"query": "test", "results": []}
                )
