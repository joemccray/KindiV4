import logging
import random

import boto3  # noqa: F401
import requests
from django.utils import timezone

from .models import ApiGatewayProxy

logger = logging.getLogger(__name__)


def get_rotated_session(target_site: str) -> requests.Session:
    """
    Provides a requests.Session object configured to use a random, active proxy
    for the specified target site.
    """
    session = requests.Session()

    # Find an active proxy for the target site
    active_proxies = ApiGatewayProxy.objects.filter(
        target_site=target_site, status=ApiGatewayProxy.ProxyStatus.ACTIVE
    )

    if not active_proxies.exists():
        logger.warning(
            f"No active proxies available for {target_site}. Using direct connection."
        )
        return session

    # Select a random proxy from the available pool
    proxy = random.choice(list(active_proxies))

    # The requests-ip-rotator library uses a custom HTTPAdapter.
    # For a native implementation, we can simply set the `proxies` attribute on the session.
    # The format is a dictionary mapping scheme to the proxy URL.
    # AWS API Gateway endpoints are HTTPS.
    proxy_url = proxy.endpoint_url
    proxies = {
        "http": proxy_url,
        "https": proxy_url,
    }
    session.proxies = proxies

    # It's good practice to disable SSL verification for the proxy itself,
    # but verify for the destination. However, API Gateway has valid certs.
    # session.verify = True

    # Update the last_used timestamp
    proxy.last_used = timezone.now()
    proxy.save()

    logger.info(
        f"Session configured to use proxy {proxy.api_id} in region {proxy.aws_region} for {target_site}"
    )

    return session


def provision_gateways(target_site: str, regions: list[str]) -> list[ApiGatewayProxy]:
    """
    Provisions new API Gateway proxies in the specified AWS regions for the target site.

    This is a placeholder for the actual Boto3 implementation.
    """
    # TODO: Implement Boto3 logic to create API Gateways.
    # 1. Initialize boto3 client for apigateway.
    # 2. For each region in `regions`:
    #    a. Check if a gateway for this site/region already exists in DB.
    #    b. Create REST API in AWS.
    #    c. Get root resource ID.
    #    d. Create proxy resource '{proxy+}'.
    #    e. Create 'ANY' method for the proxy resource.
    #    f. Set up integration with the target site.
    #    g. Create deployment.
    #    h. Construct the endpoint URL.
    #    i. Save the new ApiGatewayProxy object to the database.

    logger.warning(
        "`provision_gateways` is not fully implemented. No gateways were created."
    )
    return []


def decommission_gateways(proxy_ids: list[str]):
    """
    Decommissions the API Gateway proxies corresponding to the given IDs.

    This is a placeholder for the actual Boto3 implementation.
    """
    # TODO: Implement Boto3 logic to delete API Gateways.
    # 1. Fetch ApiGatewayProxy objects from DB.
    # 2. For each proxy:
    #    a. Initialize boto3 client for the correct region.
    #    b. Delete the REST API using the `api_id`.
    #    c. If successful, delete the ApiGatewayProxy object from the DB.

    logger.warning(
        "`decommission_gateways` is not fully implemented. No gateways were deleted."
    )
    pass
