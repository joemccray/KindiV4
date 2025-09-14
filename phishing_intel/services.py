import logging

from .models import URLCheck
from .tasks import task_check_url_for_phishing

logger = logging.getLogger(__name__)


def check_url_for_phishing(url_to_check: str) -> URLCheck:
    """
    Checks a URL against the PhishTank database by triggering an asynchronous task.
    Returns an existing record if available, otherwise creates a pending one.
    """
    # Check our local cache first to avoid redundant API calls
    existing_check, created = URLCheck.objects.get_or_create(url_to_check=url_to_check)

    # If we just created the record, it means we haven't checked it yet.
    # Trigger the background task to check it.
    if created:
        logger.info(f"New URL {url_to_check} detected. Triggering async check.")
        task_check_url_for_phishing.delay(url_to_check)
    else:
        logger.info(f"Returning cached result for {url_to_check}")

    return existing_check
