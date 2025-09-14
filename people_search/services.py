import logging
import os
from typing import Any

import requests

from ip_rotator.services import get_rotated_session

from .models import SearchQuery
from .tasks import poll_and_process_search

logger = logging.getLogger(__name__)

REACHSTREAM_BASE_URL = "https://api-prd.reachstream.com"


def initiate_reachstream_search(
    query_filter: dict[str, Any], fetch_count: int = 100
) -> SearchQuery:
    """
    Creates a SearchQuery record and initiates the async search on ReachStream.
    """
    search_query = SearchQuery.objects.create(query_filter=query_filter)
    api_key = os.environ.get("REACHSTREAM_API_KEY")

    if not api_key:
        msg = "REACHSTREAM_API_KEY is not set in environment."
        logger.error(msg)
        search_query.status = SearchQuery.SearchStatus.FAILED
        search_query.error_message = msg
        search_query.save()
        return search_query

    try:
        session = get_rotated_session(REACHSTREAM_BASE_URL)
        url = f"{REACHSTREAM_BASE_URL}/api/v2/async/records/filter/data"
        headers = {"X-API-Key": api_key, "Content-Type": "application/json"}
        payload = {"fetchCount": fetch_count, "filter": query_filter}

        response = session.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()

        if data.get("status") == 200 and data.get("data", {}).get(
            "unique_processing_id"
        ):
            search_query.reachstream_batch_id = data["data"]["unique_processing_id"]
            search_query.status = SearchQuery.SearchStatus.PROCESSING
            logger.info(
                f"Successfully initiated search for query {search_query.id}, batch ID: {search_query.reachstream_batch_id}"
            )
            # Trigger the first polling task after a delay
            poll_and_process_search.apply_async(args=[search_query.id], countdown=60)
        else:
            raise Exception(
                f"API returned an error: {data.get('message', 'Unknown error')}"
            )

    except requests.RequestException as e:
        logger.error(
            f"HTTP request failed for initiating search {search_query.id}: {e}"
        )
        search_query.status = SearchQuery.SearchStatus.FAILED
        search_query.error_message = f"Request failed: {e}"
    except Exception as e:
        logger.error(
            f"An unexpected error occurred initiating search {search_query.id}: {e}"
        )
        search_query.status = SearchQuery.SearchStatus.FAILED
        search_query.error_message = f"An unexpected error occurred: {e}"

    search_query.save()
    return search_query


def trigger_poll_for_all_searches() -> str:
    """
    Triggers the Celery task to poll for all currently processing searches.
    """
    processing_queries = SearchQuery.objects.filter(
        status=SearchQuery.SearchStatus.PROCESSING
    )
    if not processing_queries.exists():
        return "No running queries to process."

    count = 0
    for query in processing_queries:
        poll_and_process_search.delay(query.id)
        count += 1

    return f"Triggered polling for {count} queries."
