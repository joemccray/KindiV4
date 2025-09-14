import os
from unittest.mock import patch

from django.contrib.auth.models import User
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
    @patch("phishing_intel.services.task_check_url_for_phishing.delay")
    def test_check_url_triggers_task_for_new_url(self, mock_delay):
        """
        Test that the service function triggers the celery task for a URL not yet in the DB.
        """
        url = "http://new-phish-test.com"
        services.check_url_for_phishing(url)
        # The service function should create a pending record
        self.assertTrue(URLCheck.objects.filter(url_to_check=url).exists())
        # The celery task should be called to perform the actual check
        mock_delay.assert_called_once_with(url)

    @patch("phishing_intel.services.task_check_url_for_phishing.delay")
    def test_check_url_returns_cache_and_does_not_trigger_task(self, mock_delay):
        """
        Test that if a URL is already in the DB, the service returns it and does not trigger a new task.
        """
        url = "http://existing-phish.com"
        URLCheck.objects.create(url_to_check=url, is_phishing=True)

        services.check_url_for_phishing(url)

        # The celery task should NOT be called
        mock_delay.assert_not_called()


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
