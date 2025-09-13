import boto3
from django.core.management import call_command
from django.test import TestCase
from moto import mock_aws

from . import services
from .models import ApiGatewayProxy


@mock_aws
class IpRotatorServiceTest(TestCase):
    def setUp(self):
        # We need to create a client for the test methods to use
        self.region = "us-east-1"
        self.client = boto3.client("apigateway", region_name=self.region)

    def test_provision_gateways_success(self):
        """
        Test that provision_gateways successfully creates an API Gateway
        and saves the proxy object.
        """
        target_site = "https://httpbin.org"

        # Action
        created_proxies = services.provision_gateways(target_site, [self.region])

        # Assertions
        self.assertEqual(len(created_proxies), 1)
        self.assertEqual(ApiGatewayProxy.objects.count(), 1)

        proxy = ApiGatewayProxy.objects.first()
        self.assertEqual(proxy.target_site, target_site)
        self.assertEqual(proxy.aws_region, self.region)
        self.assertEqual(proxy.status, ApiGatewayProxy.ProxyStatus.ACTIVE)
        self.assertIsNotNone(proxy.api_id)
        self.assertIn(proxy.api_id, proxy.endpoint_url)

        # Check AWS resources using boto3 against the mocked environment
        rest_apis = self.client.get_rest_apis()["items"]
        self.assertEqual(len(rest_apis), 1)
        self.assertEqual(rest_apis[0]["id"], proxy.api_id)

        # Check deployment
        deployments = self.client.get_deployments(restApiId=proxy.api_id)["items"]
        self.assertEqual(len(deployments), 1)

    def test_decommission_gateways_success(self):
        """
        Test that decommission_gateways successfully removes the API Gateway
        and the proxy object from the database.
        """
        target_site = "https://httpbin.org"

        # Setup: First, provision a gateway to decommission
        services.provision_gateways(target_site, [self.region])
        self.assertEqual(ApiGatewayProxy.objects.count(), 1)
        proxy_to_delete = ApiGatewayProxy.objects.first()

        # Action
        services.decommission_gateways([proxy_to_delete.id])

        # Assertions
        self.assertEqual(ApiGatewayProxy.objects.count(), 0)

        # Check that the API Gateway is gone from the mocked AWS environment
        rest_apis = self.client.get_rest_apis()["items"]
        self.assertEqual(len(rest_apis), 0)

    def test_get_rotated_session(self):
        """
        Test the get_rotated_session function. This doesn't need moto
        but we can test it in the same class.
        """
        # No active proxies
        session = services.get_rotated_session("https://example.com")
        self.assertEqual(session.proxies, {})

        # Add an active proxy
        proxy = ApiGatewayProxy.objects.create(
            target_site="https://example.com",
            aws_region=self.region,
            api_id="test-api-id",
            endpoint_url="https://test.example.com",
            status=ApiGatewayProxy.ProxyStatus.ACTIVE,
        )

        session = services.get_rotated_session("https://example.com")
        self.assertEqual(session.proxies["https"], proxy.endpoint_url)


@mock_aws
class ManagementCommandTest(TestCase):
    def test_provision_command(self):
        """Test the provision_proxies management command."""
        call_command(
            "provision_proxies",
            "--site",
            "https://test.com",
            "--regions",
            "us-east-1",
            "us-west-2",
        )
        self.assertEqual(ApiGatewayProxy.objects.count(), 2)
        self.assertTrue(ApiGatewayProxy.objects.filter(aws_region="us-east-1").exists())
        self.assertTrue(ApiGatewayProxy.objects.filter(aws_region="us-west-2").exists())

    def test_decommission_command(self):
        """Test the decommission_proxies management command."""
        # First create one to delete
        call_command(
            "provision_proxies", "--site", "https://test.com", "--regions", "us-east-1"
        )
        proxy_id = ApiGatewayProxy.objects.first().id

        # Now decommission it
        call_command("decommission_proxies", str(proxy_id))
        self.assertEqual(ApiGatewayProxy.objects.count(), 0)
