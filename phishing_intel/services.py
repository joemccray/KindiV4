import logging
import os

from ip_rotator.services import get_rotated_session

from .models import URLCheck

logger = logging.getLogger(__name__)

PHISHTANK_CHECK_URL = "http://checkurl.phishtank.com/checkurl/"
PHISHTANK_API_KEY = os.environ.get("PHISHTANK_API_KEY")

# Cache keys for rate limiting
RATE_LIMIT_LIMIT_KEY = "phishtank_limit"
RATE_LIMIT_REMAINING_KEY = "phishtank_remaining"
RATE_LIMIT_RESET_KEY = "phishtank_reset"


def check_url_for_phishing(url_to_check: str) -> URLCheck:
    """
    Checks a URL against the PhishTank database.
    """
    # Placeholder for a more robust rate limit check
    # if cache.get(RATE_LIMIT_REMAINING_KEY, 1) <= 0:
    #     logger.warning("PhishTank rate limit likely exceeded. Skipping check.")
    #     # Return a cached result or raise an exception
    #     return URLCheck.objects.filter(url_to_check=url_to_check).first()

    get_rotated_session("http://checkurl.phishtank.com")

    # user_agent = getattr(settings, "KINDI_USER_AGENT", "kindi-platform/1.0")
    # headers = {"User-Agent": user_agent}

    # post_data = {
    #     "url": url_to_check,
    #     "format": "json",
    #     "app_key": PHISHTANK_API_KEY,
    # }

    # Placeholder for actual API call
    # response = session.post(PHISHTANK_CHECK_URL, data=post_data, headers=headers)
    # response.raise_for_status()
    # data = response.json()

    # Simulate a response for a non-phishing URL for now
    data = {"meta": {"status": "ok"}, "results": {"in_database": False}}

    # Create a record of the check
    check_record, created = URLCheck.objects.update_or_create(
        url_to_check=url_to_check,
        defaults={
            "is_phishing": data["results"].get("valid", False)
            and data["results"].get("in_database", False),
            "in_phishtank_database": data["results"].get("in_database", False),
            "phishtank_id": data["results"].get("phish_id"),
            "details_url": data["results"].get("phish_detail_page"),
            "raw_response": data,
        },
    )

    return check_record
