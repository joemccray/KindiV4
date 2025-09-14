import os
from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
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
            raw_response={},
        )
        self.assertEqual(URLCheck.objects.count(), 1)
        self.assertEqual(str(check), "https://example.com/phish - Is Phishing: True")


@override_settings(
    CACHES={"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
)
@patch.dict(os.environ, {"PHISHTANK_API_KEY": "test-key"})
class PhishingIntelServiceTest(TestCase):
    def tearDown(self):
        cache.clear()

    @patch("phishing_intel.services.get_rotated_session")
    def test_check_url_success_is_phish(self, mock_get_session):
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.headers = {
            "X-Request-Limit-Remaining": "49",
            "X-Request-Limit-Reset": "300",
        }
        mock_response.json.return_value = {
            "results": {
                "in_database": True,
                "url": "http://phish.com",
                "phish_id": "123",
                "phish_detail_page": "http://phishtank.com/phish_detail.php?phish_id=123",
                "verified": "y",
                "valid": "y",  # valid means it's an active phish
            }
        }
        mock_session.post.return_value = mock_response

        result = services.check_url_for_phishing("http://phish.com")

        self.assertTrue(result.is_phishing)
        self.assertTrue(result.in_phishtank_database)
        self.assertEqual(result.phishtank_id, 123)
        self.assertEqual(cache.get(services.RATE_LIMIT_REMAINING_KEY), 49)

    @patch("phishing_intel.services.get_rotated_session")
    def test_check_url_rate_limit_works(self, mock_get_session):
        # Setup cache to indicate rate limit is exceeded
        cache.set(services.RATE_LIMIT_REMAINING_KEY, 0)
        cache.set(services.RATE_LIMIT_RESET_KEY, 9999999999)  # A time in the future

        with self.assertRaises(Exception) as cm:
            services.check_url_for_phishing("http://another-url.com")

        self.assertIn("PhishTank API rate limit exceeded", str(cm.exception))
        mock_get_session.assert_not_called()

    @patch("phishing_intel.services.get_rotated_session")
    def test_local_cache_works(self, mock_get_session):
        URLCheck.objects.create(url_to_check="http://cached-url.com", is_phishing=True)

        result = services.check_url_for_phishing("http://cached-url.com")

        self.assertTrue(result.is_phishing)
        mock_get_session.assert_not_called()  # Should not make an API call


class PhishingIntelApiTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)

    @patch("phishing_intel.views.services.check_url_for_phishing")
    def test_check_url_api(self, mock_check_url):
        test_url = "https://a-test-url.com/login"
        mock_check = URLCheck(
            url_to_check=test_url, is_phishing=False, in_phishtank_database=False
        )
        mock_check_url.return_value = mock_check

        url = reverse("phishing-check-list")
        data = {"url": test_url}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_check_url.assert_called_once_with(test_url)
        self.assertEqual(response.data["url_to_check"], test_url)
        self.assertFalse(response.data["is_phishing"])
