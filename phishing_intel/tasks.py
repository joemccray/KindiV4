import logging
import os
import time

import requests
from celery import shared_task
from django.conf import settings
from django.core.cache import cache

from ip_rotator.services import get_rotated_session

from .models import URLCheck

logger = logging.getLogger(__name__)

PHISHTANK_CHECK_URL = "http://checkurl.phishtank.com/checkurl/"

RATE_LIMIT_REMAINING_KEY = "phishtank_remaining"
RATE_LIMIT_RESET_KEY = "phishtank_reset"


def _check_rate_limit():
    """Checks and enforces PhishTank rate limit."""
    remaining = cache.get(RATE_LIMIT_REMAINING_KEY)
    reset_time = cache.get(RATE_LIMIT_RESET_KEY)
    if remaining is None or reset_time is None:
        return True
    if int(remaining) > 0:
        return True
    if time.time() >= int(reset_time):
        return True
    logger.warning("PhishTank API rate limit exceeded. Skipping check.")
    return False


def _update_rate_limit_cache(headers):
    """Updates the cache with the latest rate limit headers."""
    if "X-Request-Limit-Remaining" in headers:
        cache.set(
            RATE_LIMIT_REMAINING_KEY,
            int(headers["X-Request-Limit-Remaining"]),
            timeout=int(headers.get("X-Request-Limit-Interval", 300)),
        )
    if "X-Request-Limit-Reset" in headers:
        cache.set(
            RATE_LIMIT_RESET_KEY,
            int(headers["X-Request-Limit-Reset"]),
            timeout=int(headers.get("X-Request-Limit-Interval", 300)),
        )


@shared_task
def task_check_url_for_phishing(url_to_check: str):
    """
    Celery task to check a URL against the PhishTank database.
    """
    if not _check_rate_limit():
        logger.warning(f"Rate limit exceeded. Re-queuing task for {url_to_check}.")
        # Re-queue the task to run again after the rate limit reset period (e.g., 60 seconds)
        task_check_url_for_phishing.apply_async(args=[url_to_check], countdown=60)
        return

    api_key = os.environ.get("PHISHTANK_API_KEY")
    if not api_key:
        logger.error("PHISHTANK_API_KEY is not set in environment.")
        return

    session = get_rotated_session(PHISHTANK_CHECK_URL)
    user_agent = getattr(settings, "KINDI_USER_AGENT", "kindi-platform/1.0")
    headers = {"User-Agent": user_agent}
    post_data = {"url": url_to_check, "format": "json", "app_key": api_key}

    try:
        response = session.post(
            PHISHTANK_CHECK_URL, data=post_data, headers=headers, timeout=20
        )
        _update_rate_limit_cache(response.headers)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", {})
        is_phishing = results.get("in_database") is True and results.get("valid") == "y"
        phish_id_str = results.get("phish_id")

        URLCheck.objects.update_or_create(
            url_to_check=url_to_check,
            defaults={
                "is_phishing": is_phishing,
                "in_phishtank_database": results.get("in_database", False),
                "phishtank_id": int(phish_id_str) if phish_id_str else None,
                "details_url": results.get("phish_detail_url"),
                "raw_response": data,
            },
        )
    except requests.RequestException as e:
        logger.error(f"PhishTank API request failed for url {url_to_check}: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred checking {url_to_check}: {e}")
