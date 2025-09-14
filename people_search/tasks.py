import logging
import os

import requests
from celery import shared_task
from django.utils import timezone

from ip_rotator.services import get_rotated_session

from .models import PersonProfile, SearchQuery

logger = logging.getLogger(__name__)

REACHSTREAM_BASE_URL = "https://api-prd.reachstream.com"


def _process_and_store_results(search_query: SearchQuery, results_data: list):
    """
    Processes the raw results from ReachStream and stores them as PersonProfile objects.
    """
    if profiles_to_create := [
        PersonProfile(
            search_query=search_query,
            full_name=item.get("contact_name"),
            job_title=item.get("contact_job_title_1"),
            company_name=item.get("company_company_name"),
            email=item.get("contact_email_1"),
            linkedin_url=item.get("contact_social_linkedin"),
            raw_data=item,
        )
        for item in results_data
    ]:
        PersonProfile.objects.bulk_create(profiles_to_create)
        logger.info(
            f"Stored {len(profiles_to_create)} profiles for search query {search_query.id}"
        )


@shared_task
def poll_and_process_search(search_query_id: str):
    """
    Celery task to poll for the result of a single search query.
    """
    try:
        query = SearchQuery.objects.get(
            id=search_query_id, status=SearchQuery.SearchStatus.PROCESSING
        )
    except SearchQuery.DoesNotExist:
        logger.warning(
            f"SearchQuery {search_query_id} not found or not in processing state."
        )
        return

    api_key = os.environ.get("REACHSTREAM_API_KEY")
    if not api_key:
        logger.error("Cannot poll results, REACHSTREAM_API_KEY is not set.")
        query.status = SearchQuery.SearchStatus.FAILED
        query.error_message = "REACHSTREAM_API_KEY is not set."
        query.save()
        return

    logger.info(
        f"Polling for results for search query {query.id} with batch ID {query.reachstream_batch_id}"
    )
    try:
        session = get_rotated_session(REACHSTREAM_BASE_URL)
        url = f"{REACHSTREAM_BASE_URL}/api/v2/records/batch-process"
        params = {"batch_process_id": query.reachstream_batch_id}
        headers = {"X-API-Key": api_key}

        response = session.get(url, params=params, headers=headers, timeout=30)

        if response.status_code == 400 and "still being processed" in response.text:
            logger.info(f"Query {query.id} is still processing.")
            # Optionally, re-queue the task with a countdown
            # poll_and_process_search.apply_async(args=[search_query_id], countdown=60)
            return

        response.raise_for_status()
        data = response.json()

        if data.get("status") != 200 or "data" not in data:
            raise Exception(
                f"API returned an error: {data.get('message', 'Unknown error')}"
            )

        _process_and_store_results(query, data["data"])
        query.status = SearchQuery.SearchStatus.COMPLETED
        query.completed_at = timezone.now()
        query.save()
        logger.info(f"Search query {query.id} completed successfully.")
    except requests.RequestException as e:
        logger.error(f"HTTP request failed while polling for {query.id}: {e}")
        query.status = SearchQuery.SearchStatus.FAILED
        query.error_message = f"Polling failed: {e}"
        query.save()
    except Exception as e:
        logger.error(f"An unexpected error occurred while polling for {query.id}: {e}")
        query.status = SearchQuery.SearchStatus.FAILED
        query.error_message = f"An unexpected error occurred during polling: {e}"
        query.save()
