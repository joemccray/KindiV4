import os
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import services
from .models import URLCheck


class PhishingIntelModelTest(TestCase):
    def test_create_url_check(self):
        check = URLCheck.objects.create(
            url_to_check="https://example.com/phish",
            is_phishing=True,
            in_phishtank_database=True,
            phishtank_id=12345,
        )
        self.assertEqual(URLCheck.objects.count(), 1)
        self.assertEqual(str(check), "https://example.com/phish - Is Phishing: True")


class PhishingIntelServiceTest(TestCase):
    @patch("phishing_intel.services.get_rotated_session")
    @patch.dict(os.environ, {"PHISHTANK_API_KEY": "test-key"})
    def test_check_url_service(self, mock_get_session):
        mock_get_session.return_value = MagicMock()

        url = "http://innocent-looking.com"
        result = services.check_url_for_phishing(url)

        self.assertIsInstance(result, URLCheck)
        self.assertEqual(result.url_to_check, url)
        self.assertFalse(result.is_phishing)
        mock_get_session.assert_called_once()


class PhishingIntelApiTest(APITestCase):
    @patch("phishing_intel.views.services.check_url_for_phishing")
    def test_check_url_api(self, mock_check_url):
        # Configure the mock to return a predictable URLCheck object
        test_url = "https://a-test-url.com/login"
        mock_check = URLCheck(
            url_to_check=test_url, is_phishing=False, in_phishtank_database=False
        )
        mock_check_url.return_value = mock_check

        url = reverse(
            "phishing-check-list"
        )  # The action is 'create' which maps to the list route for POST
        data = {"url": test_url}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_check_url.assert_called_once_with(test_url)
        self.assertEqual(response.data["url_to_check"], test_url)
        self.assertFalse(response.data["is_phishing"])

    def test_check_url_api_invalid_url(self):
        """
        Test that the API returns a 400 Bad Request for an invalid URL.
        """
        url = reverse("phishing-check-list")
        data = {"url": "this-is-not-a-url"}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
