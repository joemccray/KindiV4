import logging
import random
import time
from contextlib import suppress

import boto3
import requests
from botocore.exceptions import ClientError
from django.utils import timezone

from .models import ApiGatewayProxy

logger = logging.getLogger(__name__)


def get_rotated_session(target_site: str) -> requests.Session:
    """
    Provides a requests.Session object configured to use a random, active proxy
    for the specified target site.
    """
    session = requests.Session()
    active_proxies = ApiGatewayProxy.objects.filter(
        target_site=target_site, status=ApiGatewayProxy.ProxyStatus.ACTIVE
    )

    if not active_proxies.exists():
        logger.warning(
            f"No active proxies available for {target_site}. Using direct connection."
        )
        return session

    proxy = random.choice(list(active_proxies))
    proxy_url = proxy.endpoint_url
    proxies = {"http": proxy_url, "https": proxy_url}
    session.proxies = proxies

    proxy.last_used = timezone.now()
    proxy.save(update_fields=["last_used"])

    logger.info(
        f"Session configured to use proxy {proxy.api_id} in region {proxy.aws_region} for {target_site}"
    )
    return session


def provision_gateways(target_site: str, regions: list[str]) -> list[ApiGatewayProxy]:
    """
    Provisions new API Gateway proxies in the specified AWS regions.
    """
    created_proxies = []
    for region in regions:
        proxy, created = ApiGatewayProxy.objects.get_or_create(
            target_site=target_site,
            aws_region=region,
            defaults={"status": ApiGatewayProxy.ProxyStatus.CREATING},
        )
        if not created and proxy.status == ApiGatewayProxy.ProxyStatus.ACTIVE:
            logger.info(
                f"Proxy for {target_site} in {region} already exists and is active."
            )
            created_proxies.append(proxy)
            continue

        try:
            client = boto3.client("apigateway", region_name=region)

            # Create the REST API
            api_name = f"kindi-proxy-{int(time.time())}"
            response = client.create_rest_api(
                name=api_name,
                description=f"Kindi IP rotator proxy for {target_site}",
                endpointConfiguration={"types": ["REGIONAL"]},
            )
            api_id = response["id"]
            proxy.api_id = api_id
            proxy.save(update_fields=["api_id"])

            # Get the root resource ID
            root_resource_id = client.get_resources(restApiId=api_id)["items"][0]["id"]

            # Create a proxy resource
            proxy_resource = client.create_resource(
                restApiId=api_id, parentId=root_resource_id, pathPart="{proxy+}"
            )
            proxy_resource_id = proxy_resource["id"]

            # Create the ANY method for the proxy resource
            client.put_method(
                restApiId=api_id,
                resourceId=proxy_resource_id,
                httpMethod="ANY",
                authorizationType="NONE",
            )

            # Set up the integration
            client.put_integration(
                restApiId=api_id,
                resourceId=proxy_resource_id,
                httpMethod="ANY",
                type="HTTP_PROXY",
                integrationHttpMethod="ANY",
                uri=f"{target_site}/{{proxy}}",
                connectionType="INTERNET",
                requestParameters={
                    "integration.request.path.proxy": "method.request.path.proxy"
                },
            )

            # Create a deployment
            client.create_deployment(restApiId=api_id, stageName="prod")

            # Construct the endpoint URL
            endpoint_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/prod"
            proxy.endpoint_url = endpoint_url
            proxy.status = ApiGatewayProxy.ProxyStatus.ACTIVE
            proxy.save(update_fields=["endpoint_url", "status"])

            created_proxies.append(proxy)
            logger.info(
                f"Successfully provisioned proxy for {target_site} in {region}."
            )

        except ClientError as e:
            logger.error(
                f"Failed to provision proxy for {target_site} in {region}: {e}"
            )
            proxy.status = ApiGatewayProxy.ProxyStatus.ERROR
            proxy.save(update_fields=["status"])
            # Clean up failed creation if possible
            if "api_id" in locals():
                with suppress(ClientError):
                    # Ignore errors during cleanup
                    client.delete_rest_api(restApiId=api_id)

    return created_proxies


def decommission_gateways(proxy_ids: list[str]):
    """
    Decommissions the API Gateway proxies corresponding to the given IDs.
    """
    proxies_to_delete = ApiGatewayProxy.objects.filter(id__in=proxy_ids)
    for proxy in proxies_to_delete:
        logger.info(f"Decommissioning proxy {proxy.id} in region {proxy.aws_region}...")
        proxy.status = ApiGatewayProxy.ProxyStatus.DELETING
        proxy.save(update_fields=["status"])

        try:
            client = boto3.client("apigateway", region_name=proxy.aws_region)
            client.delete_rest_api(restApiId=proxy.api_id)
            logger.info(f"Successfully deleted REST API {proxy.api_id} from AWS.")
            proxy.delete()
        except ClientError as e:
            logger.error(f"Failed to delete REST API {proxy.api_id} from AWS: {e}")
            proxy.status = ApiGatewayProxy.ProxyStatus.ERROR
            proxy.save(update_fields=["status"])
