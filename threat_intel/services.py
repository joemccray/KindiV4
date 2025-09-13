import logging
import time

import requests
from django.core.cache import cache

from ip_rotator.services import get_rotated_session

from .models import Indicator, ThreatReport

logger = logging.getLogger(__name__)

THREATMINER_BASE_URL = "https://api.threatminer.org/v2"
RATE_LIMIT_KEY = "threatminer_api_request_timestamps"
RATE_LIMIT_COUNT = 10  # 10 queries
RATE_LIMIT_PERIOD_SECONDS = 60  # per minute


def _check_rate_limit():
    """
    Checks and enforces a 10 queries/minute rate limit.
    Returns True if a request can be made, False otherwise.
    """
    timestamps = cache.get(RATE_LIMIT_KEY, [])
    now = time.time()

    valid_timestamps = [t for t in timestamps if now - t < RATE_LIMIT_PERIOD_SECONDS]

    if len(valid_timestamps) < RATE_LIMIT_COUNT:
        valid_timestamps.append(now)
        cache.set(RATE_LIMIT_KEY, valid_timestamps, timeout=RATE_LIMIT_PERIOD_SECONDS)
        return True

    logger.warning("ThreatMiner API rate limit exceeded. Skipping request.")
    return False


def _query_and_store(session, indicator, endpoint, rt_map):
    """Helper function to query report types and store results."""
    for rt_code, report_name in rt_map.items():
        if not _check_rate_limit():
            logger.warning(
                f"Rate limited. Skipping report '{report_name}' for {indicator.value}"
            )
            continue

        try:
            url = f"{THREATMINER_BASE_URL}/{endpoint}?q={indicator.value}&rt={rt_code}"
            response = session.get(url, timeout=20)
            response.raise_for_status()
            data = response.json()

            if data.get("status_code") == "200":
                ThreatReport.objects.update_or_create(
                    indicator=indicator,
                    report_type=report_name,
                    defaults={"raw_data": data["results"]},
                )
                logger.info(
                    f"Successfully fetched report '{report_name}' for {indicator.value}"
                )
            else:
                logger.warning(
                    f"No results for report '{report_name}' for {indicator.value}: {data.get('status_message')}"
                )

        except requests.RequestException as e:
            logger.error(
                f"Error fetching report '{report_name}' for {indicator.value}: {e}"
            )
        time.sleep(1)  # Add a small delay between requests to be courteous


def get_domain_intel(domain: str) -> Indicator:
    """
    Retrieves all available intelligence for a given domain from ThreatMiner.
    """
    indicator, created = Indicator.objects.get_or_create(
        value=domain, defaults={"type": Indicator.IndicatorType.DOMAIN}
    )
    if not created:
        indicator.save()  # to update last_seen timestamp

    session = get_rotated_session(THREATMINER_BASE_URL)

    # Report types for domains
    rt_map = {
        1: "whois",
        2: "passive_dns",
        3: "uris",
        4: "related_samples",
        5: "subdomains",
    }
    _query_and_store(session, indicator, "domain.php", rt_map)

    return indicator


def get_ip_intel(ip_address: str) -> Indicator:
    """
    Retrieves all available intelligence for a given IP address.
    """
    indicator, created = Indicator.objects.get_or_create(
        value=ip_address, defaults={"type": Indicator.IndicatorType.IPV4}
    )
    if not created:
        indicator.save()

    session = get_rotated_session(THREATMINER_BASE_URL)

    # Report types for hosts/IPs
    rt_map = {
        1: "whois",
        2: "passive_dns",
        3: "uris",
        4: "related_samples",
        5: "ssl_certificates",
    }
    _query_and_store(session, indicator, "host.php", rt_map)

    return indicator


def get_hash_intel(file_hash: str) -> Indicator:
    """
    Retrieves all available intelligence for a given file hash.
    """
    # Basic type inference
    if len(file_hash) == 32:
        hash_type = Indicator.IndicatorType.MD5
    elif len(file_hash) == 40:
        hash_type = Indicator.IndicatorType.SHA1
    else:
        hash_type = Indicator.IndicatorType.SHA256

    indicator, created = Indicator.objects.get_or_create(
        value=file_hash, defaults={"type": hash_type}
    )
    if not created:
        indicator.save()

    session = get_rotated_session(THREATMINER_BASE_URL)

    # Report types for samples/hashes
    rt_map = {
        1: "metadata",
        2: "http_traffic",
        3: "hosts",
        4: "mutants",
        5: "registry_keys",
        6: "av_detections",
    }
    _query_and_store(session, indicator, "sample.php", rt_map)

    return indicator
