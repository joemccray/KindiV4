import logging
import time

from django.core.cache import cache

from ip_rotator.services import get_rotated_session

from .models import Indicator

logger = logging.getLogger(__name__)

THREATMINER_BASE_URL = "https://api.threatminer.org"
RATE_LIMIT_KEY = "threatminer_api_request_timestamps"
RATE_LIMIT_COUNT = 10
RATE_LIMIT_PERIOD_SECONDS = 60


def _check_rate_limit():
    """
    Checks and enforces a 10 queries/minute rate limit.
    Returns True if a request can be made, False otherwise.
    """
    timestamps = cache.get(RATE_LIMIT_KEY, [])
    now = time.time()

    # Remove timestamps older than the rate limit period
    valid_timestamps = [t for t in timestamps if now - t < RATE_LIMIT_PERIOD_SECONDS]

    if len(valid_timestamps) < RATE_LIMIT_COUNT:
        valid_timestamps.append(now)
        cache.set(RATE_LIMIT_KEY, valid_timestamps, timeout=RATE_LIMIT_PERIOD_SECONDS)
        return True

    logger.warning("ThreatMiner API rate limit exceeded. Skipping request.")
    return False


def get_domain_intel(domain: str) -> Indicator:
    """
    Retrieves all available intelligence for a given domain from ThreatMiner.
    """
    if not _check_rate_limit():
        # Maybe return cached data or raise an exception
        # For now, we'll just return the existing object if it exists
        indicator, _ = Indicator.objects.get_or_create(
            value=domain, type=Indicator.IndicatorType.DOMAIN
        )
        return indicator

    get_rotated_session(THREATMINER_BASE_URL)
    indicator, created = Indicator.objects.get_or_create(
        value=domain, type=Indicator.IndicatorType.DOMAIN
    )
    if not created:
        indicator.save()  # to update last_seen timestamp

    # Placeholder for making actual API calls for different report types (rt=1, 2, 5 etc.)
    # and creating ThreatReport objects.
    # Example for one report type:
    # report_type = "passive_dns"
    # url = f"{THREATMINER_BASE_URL}/v2/domain.php?q={domain}&rt=2"
    # response = session.get(url)
    # if response.status_code == 200 and response.json()['status_code'] == 200:
    #     ThreatReport.objects.update_or_create(
    #         indicator=indicator,
    #         report_type=report_type,
    #         defaults={'raw_data': response.json()['results']}
    #     )

    logger.info(
        f"Threat intel service called for domain: {domain} (logic is placeholder)."
    )
    return indicator


def get_ip_intel(ip_address: str) -> Indicator:
    """
    Retrieves all available intelligence for a given IP address.
    (Placeholder)
    """
    indicator, _ = Indicator.objects.get_or_create(
        value=ip_address, type=Indicator.IndicatorType.IPV4
    )
    logger.info(
        f"Threat intel service called for IP: {ip_address} (logic is placeholder)."
    )
    return indicator


def get_hash_intel(file_hash: str) -> Indicator:
    """
    Retrieves all available intelligence for a given file hash.
    (Placeholder)
    """
    # Basic type inference, could be improved
    if len(file_hash) == 32:
        hash_type = Indicator.IndicatorType.MD5
    elif len(file_hash) == 40:
        hash_type = Indicator.IndicatorType.SHA1
    else:
        hash_type = Indicator.IndicatorType.SHA256

    indicator, _ = Indicator.objects.get_or_create(value=file_hash, type=hash_type)
    logger.info(
        f"Threat intel service called for hash: {file_hash} (logic is placeholder)."
    )
    return indicator
