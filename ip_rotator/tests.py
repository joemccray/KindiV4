import requests
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import ApiGatewayProxy
from .services import get_rotated_session


class ApiGatewayProxyModelTest(TestCase):
    """
    Tests for the ApiGatewayProxy model.
    """

    def test_create_proxy(self):
        proxy = ApiGatewayProxy.objects.create(
            target_site="https://example.com",
            aws_region="us-east-1",
            api_id="abcdef123",
            endpoint_url="https://abcdef123.execute-api.us-east-1.amazonaws.com/proxy",
            status=ApiGatewayProxy.ProxyStatus.ACTIVE,
        )
        self.assertEqual(str(proxy), "https://example.com (us-east-1) - ACTIVE")
        self.assertEqual(ApiGatewayProxy.objects.count(), 1)


class IpRotatorServiceTest(TestCase):
    """
    Tests for the services in the ip_rotator app.
    """

    @classmethod
    def setUpTestData(cls):
        cls.proxy = ApiGatewayProxy.objects.create(
            target_site="https://httpbin.org",
            aws_region="us-west-2",
            api_id="testapi123",
            endpoint_url="https://test-proxy.com/api",
            status=ApiGatewayProxy.ProxyStatus.ACTIVE,
        )

    def test_get_rotated_session_with_active_proxy(self):
        """
        Test that get_rotated_session returns a session with correct proxy info.
        """
        session = get_rotated_session("https://httpbin.org")
        self.assertIsInstance(session, requests.Session)

        expected_proxies = {
            "http": self.proxy.endpoint_url,
            "https": self.proxy.endpoint_url,
        }
        self.assertEqual(session.proxies, expected_proxies)

        # Verify the last_used timestamp was updated
        self.proxy.refresh_from_db()
        self.assertIsNotNone(self.proxy.last_used)

    def test_get_rotated_session_with_no_active_proxy(self):
        """
        Test that a standard session is returned when no active proxy is available.
        """
        # Deactivate the only proxy
        self.proxy.status = ApiGatewayProxy.ProxyStatus.INACTIVE
        self.proxy.save()

        session = get_rotated_session("https://httpbin.org")
        self.assertIsInstance(session, requests.Session)
        self.assertEqual(session.proxies, {})


class IpRotatorApiTest(APITestCase):
    """
    Tests for the ip_rotator API endpoints.
    """

    @classmethod
    def setUpTestData(cls):
        cls.proxy1 = ApiGatewayProxy.objects.create(
            target_site="https://site1.com",
            aws_region="eu-central-1",
            api_id="api1",
            endpoint_url="https://api1.example.com",
            status=ApiGatewayProxy.ProxyStatus.ACTIVE,
        )
        cls.proxy2 = ApiGatewayProxy.objects.create(
            target_site="https://site2.com",
            aws_region="ap-southeast-1",
            api_id="api2",
            endpoint_url="https://api2.example.com",
            status=ApiGatewayProxy.ProxyStatus.INACTIVE,
        )
        cls.list_url = reverse("apigatewayproxy-list")
        cls.detail_url = reverse("apigatewayproxy-detail", kwargs={"id": cls.proxy1.id})

    def test_list_proxies(self):
        """
        Ensure we can list all proxy objects.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(
            response.data[0]["api_id"], self.proxy2.api_id
        )  # Default ordering is -created_at

    def test_retrieve_proxy(self):
        """
        Ensure we can retrieve a single proxy object.
        """
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(self.proxy1.id))
        self.assertEqual(response.data["target_site"], self.proxy1.target_site)

    def test_cannot_create_proxy_via_api(self):
        """
        Ensure that POST requests to the list endpoint are not allowed.
        """
        data = {"target_site": "https://new.com", "aws_region": "us-east-1"}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_update_proxy_via_api(self):
        """
        Ensure that PUT requests to the detail endpoint are not allowed.
        """
        data = {"status": ApiGatewayProxy.ProxyStatus.INACTIVE}
        response = self.client.put(self.detail_url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_cannot_delete_proxy_via_api(self):
        """
        Ensure that DELETE requests to the detail endpoint are not allowed.
        """
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
