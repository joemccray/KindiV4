import logging
import os
from typing import Any

from django.utils import timezone

from ip_rotator.services import get_rotated_session

from .models import PersonProfile, SearchQuery

logger = logging.getLogger(__name__)

REACHSTREAM_BASE_URL = "https://api-prd.reachstream.com"


def initiate_reachstream_search(query_filter: dict[str, Any]) -> SearchQuery:
    """
    Creates a SearchQuery record and initiates the async search on ReachStream.
    """
    search_query = SearchQuery.objects.create(query_filter=query_filter)

    # In a real implementation, we would now make the API call.
    # This logic will be fully implemented later.
    # For now, we simulate success by giving it a fake batch ID and setting status.

    try:
        api_key = os.environ.get("REACHSTREAM_API_KEY")
        if not api_key:
            raise ValueError("REACHSTREAM_API_KEY is not set in environment.")

        # Get a proxied session from our rotator service
        get_rotated_session(REACHSTREAM_BASE_URL)

        # This is where the actual call would go
        # url = f"{REACHSTREAM_BASE_URL}/api/v2/async/records/filter/data"
        # headers = {"X-API-Key": REACHSTREAM_API_KEY, "Content-Type": "application/json"}
        # payload = {"fetchCount": 100, "filter": query_filter} # fetchCount could be a parameter
        # response = session.post(url, json=payload, headers=headers)
        # response.raise_for_status()
        # data = response.json()

        # Simulate a successful API call for now
        search_query.reachstream_batch_id = f"fake-batch-{search_query.id}"
        search_query.status = SearchQuery.SearchStatus.PROCESSING
        logger.info(
            f"Successfully initiated search for query {search_query.id}, batch ID: {search_query.reachstream_batch_id}"
        )

    except Exception as e:
        logger.error(
            f"Failed to initiate ReachStream search for query {search_query.id}: {e}"
        )
        search_query.status = SearchQuery.SearchStatus.FAILED
        search_query.error_message = str(e)

    search_query.save()
    return search_query


def poll_and_process_results():
    """
    Polls for results of processing searches and saves them to the database.
    This would be run as a background task.
    """
    processing_queries = SearchQuery.objects.filter(
        status=SearchQuery.SearchStatus.PROCESSING
    )

    if not processing_queries.exists():
        return "No queries to process."

    for query in processing_queries:
        logger.info(
            f"Polling for results for search query {query.id} with batch ID {query.reachstream_batch_id}"
        )
        # In a real implementation, we would poll the ReachStream API here.
        # For now, we will simulate a successful result for one of the queries.

        # Simulate finding results and storing them
        _process_and_store_results(
            query, []
        )  # Pass empty list to avoid creating profiles yet
        query.status = SearchQuery.SearchStatus.COMPLETED
        query.completed_at = timezone.now()
        query.save()
        logger.info(f"Search query {query.id} completed.")

    return f"Processed {len(processing_queries)} queries."


def _process_and_store_results(search_query: SearchQuery, results_data: list):
    """
    Processes the raw results from ReachStream and stores them as PersonProfile objects.
    """
    # This function will contain the logic to map the API response fields
    # to our PersonProfile model. For now, it's a placeholder.
    PersonProfile.objects.bulk_create(
        [
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
        ]
    )
    logger.info(
        f"Stored {len(results_data)} profiles for search query {search_query.id}"
    )
