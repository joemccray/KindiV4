from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class ClerkWebhookSyncViewTests(APITestCase):
    """
    Tests for the ClerkWebhookSyncView.
    """

    def test_webhook_endpoint_returns_200_ok_on_post(self):
        """
        Ensure the webhook endpoint can be reached and acknowledges POST requests.
        """
        url = reverse("users:clerk-webhook-sync")
        # The payload can be empty for this placeholder test
        data = {}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Webhook received"})

    def test_webhook_endpoint_rejects_get_requests(self):
        """
        Ensure the webhook endpoint only allows POST requests.
        """
        url = reverse("users:clerk-webhook-sync")

        response = self.client.get(url)

        # Expect a 405 Method Not Allowed response
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
