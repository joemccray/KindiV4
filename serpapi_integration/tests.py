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
    @patch("serpapi_integration.services.task_execute_serpapi_search.delay")
    def test_search_google_news_triggers_task(self, mock_delay):
        """
        Test that the service function triggers the celery task with the correct params.
        """
        services.search_google_news("test query")
        expected_params = {"q": "test query", "engine": "google", "tbm": "nws"}
        mock_delay.assert_called_once_with(expected_params, "google_news")

    @patch("serpapi_integration.services.task_execute_serpapi_search.delay")
    def test_search_youtube_triggers_task(self, mock_delay):
        """
        Test that the service function triggers the celery task with the correct params.
        """
        services.search_youtube("test query")
        expected_params = {"search_query": "test query", "engine": "youtube"}
        mock_delay.assert_called_once_with(expected_params, "youtube")


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
