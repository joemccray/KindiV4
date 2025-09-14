import logging
import os
import time

import requests
from django.conf import settings
from django.core.cache import cache

from ip_rotator.services import get_rotated_session

from .models import URLCheck

logger = logging.getLogger(__name__)

PHISHTANK_CHECK_URL = "http://checkurl.phishtank.com/checkurl/"

# Cache keys for rate limiting
RATE_LIMIT_REMAINING_KEY = "phishtank_remaining"
RATE_LIMIT_RESET_KEY = "phishtank_reset"


def _check_rate_limit():
    """
    Checks PhishTank rate limit based on cached headers from previous responses.
    Returns True if a request can be made, False otherwise.
    """
    remaining = cache.get(RATE_LIMIT_REMAINING_KEY)
    reset_time = cache.get(RATE_LIMIT_RESET_KEY)

    # If we have no data, assume we can make a request.
    if remaining is None or reset_time is None:
        return True

    if int(remaining) > 0:
        return True

    # If limit is 0, check if the reset time has passed.
    if time.time() >= int(reset_time):
        return True

    logger.warning("PhishTank API rate limit exceeded. Skipping check.")
    return False


def _update_rate_limit_cache(headers):
    """Updates the cache with the latest rate limit headers from the API response."""
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


def check_url_for_phishing(url_to_check: str) -> URLCheck:
    """
    Checks a URL against the PhishTank database.
    """
    # Check our local cache first to avoid redundant API calls
    existing_check = URLCheck.objects.filter(url_to_check=url_to_check).first()
    if existing_check:
        logger.info(f"Returning cached result for {url_to_check}")
        return existing_check

    if not _check_rate_limit():
        raise Exception("PhishTank API rate limit exceeded.")

    api_key = os.environ.get("PHISHTANK_API_KEY")
    if not api_key:
        raise ValueError("PHISHTANK_API_KEY is not set in environment.")

    session = get_rotated_session("http://checkurl.phishtank.com")
    user_agent = getattr(settings, "KINDI_USER_AGENT", "kindi-platform/1.0")
    headers = {"User-Agent": user_agent}
    post_data = {
        "url": url_to_check,
        "format": "json",
        "app_key": api_key,
    }

    try:
        response = session.post(
            PHISHTANK_CHECK_URL, data=post_data, headers=headers, timeout=20
        )
        _update_rate_limit_cache(response.headers)
        response.raise_for_status()
        data = response.json()

        results = data.get("results", {})
        # The 'valid' key from PhishTank means it's a valid, active phish. It can be a string 'y'.
        is_phishing = results.get("in_database") is True and results.get("valid") == "y"
        phish_id_str = results.get("phish_id")

        check_record = URLCheck.objects.create(
            url_to_check=url_to_check,
            is_phishing=is_phishing,
            in_phishtank_database=results.get("in_database", False),
            phishtank_id=int(phish_id_str) if phish_id_str else None,
            details_url=results.get("phish_detail_url"),
            raw_response=data,
        )
        return check_record

    except requests.RequestException as e:
        logger.error(f"PhishTank API request failed for url {url_to_check}: {e}")
        raise  # Re-raise the exception to be handled by the caller
    except Exception as e:
        logger.error(f"An unexpected error occurred checking {url_to_check}: {e}")
        raise
