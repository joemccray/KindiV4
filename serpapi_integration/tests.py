import os
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import services
from .models import SerpApiSearch


class SerpApiModelTest(TestCase):
    def test_create_serpapi_search(self):
        SerpApiSearch.objects.create(
            engine="google_news",
            search_parameters={"q": "testing"},
            raw_response={"results": []},
        )
        self.assertEqual(SerpApiSearch.objects.count(), 1)


@patch.dict(os.environ, {"SERPAPI_API_KEY": "test-key"})
class SerpApiServiceTest(TestCase):
    @patch("serpapi_integration.services.GoogleSearch")
    def test_search_google_news(self, mock_google_search):
        mock_instance = mock_google_search.return_value
        mock_instance.get_dict.return_value = {"search_metadata": {"status": "Success"}}

        services.search_google_news("test query")

        self.assertEqual(SerpApiSearch.objects.count(), 1)
        search_log = SerpApiSearch.objects.first()
        self.assertEqual(search_log.engine, "google_news")

        expected_params = {
            "q": "test query",
            "engine": "google",
            "tbm": "nws",
            "api_key": "test-key",
        }
        mock_google_search.assert_called_once_with(expected_params)

    @patch("serpapi_integration.services.GoogleSearch")
    def test_search_youtube(self, mock_google_search):
        mock_instance = mock_google_search.return_value
        mock_instance.get_dict.return_value = {"search_metadata": {"status": "Success"}}

        services.search_youtube("test query")

        self.assertEqual(SerpApiSearch.objects.count(), 1)
        search_log = SerpApiSearch.objects.first()
        self.assertEqual(search_log.engine, "youtube")

        expected_params = {
            "search_query": "test query",
            "engine": "youtube",
            "api_key": "test-key",
        }
        mock_google_search.assert_called_once_with(expected_params)


class SerpApiEndpointTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)

    @patch("serpapi_integration.views.services.search_google_news")
    def test_news_search_api(self, mock_search_service):
        mock_search_service.return_value = {"results": "some news"}

        url = reverse("serpapi-news")
        data = {"query": "test"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_search_service.assert_called_once_with("test")
        self.assertEqual(response.data["results"], "some news")
