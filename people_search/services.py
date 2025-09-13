import logging
import os
from typing import Any

import requests
from django.utils import timezone

from ip_rotator.services import get_rotated_session

from .models import PersonProfile, SearchQuery

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


def _process_and_store_results(search_query: SearchQuery, results_data: list):
    """
    Processes the raw results from ReachStream and stores them as PersonProfile objects.
    """
    profiles_to_create = []
    for item in results_data:
        profiles_to_create.append(
            PersonProfile(
                search_query=search_query,
                full_name=item.get("contact_name"),
                job_title=item.get("contact_job_title_1"),
                company_name=item.get("company_company_name"),
                email=item.get("contact_email_1"),
                linkedin_url=item.get("contact_social_linkedin"),
                raw_data=item,
            )
        )

    if profiles_to_create:
        PersonProfile.objects.bulk_create(profiles_to_create)
        logger.info(
            f"Stored {len(profiles_to_create)} profiles for search query {search_query.id}"
        )


def poll_and_process_results() -> str:
    """
    Polls for results of processing searches and saves them to the database.
    This would be run as a background task.
    """
    processing_queries = SearchQuery.objects.filter(
        status=SearchQuery.SearchStatus.PROCESSING
    )
    if not processing_queries.exists():
        return "No running queries to process."

    api_key = os.environ.get("REACHSTREAM_API_KEY")
    if not api_key:
        return "Cannot poll results, REACHSTREAM_API_KEY is not set."

    processed_count = 0
    for query in processing_queries:
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
                continue

            response.raise_for_status()
            data = response.json()

            if data.get("status") == 200 and "data" in data:
                _process_and_store_results(query, data["data"])
                query.status = SearchQuery.SearchStatus.COMPLETED
                query.completed_at = timezone.now()
                query.save()
                processed_count += 1
                logger.info(f"Search query {query.id} completed successfully.")
            else:
                raise Exception(
                    f"API returned an error: {data.get('message', 'Unknown error')}"
                )

        except requests.RequestException as e:
            logger.error(f"HTTP request failed while polling for {query.id}: {e}")
            query.status = SearchQuery.SearchStatus.FAILED
            query.error_message = f"Polling failed: {e}"
            query.save()
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while polling for {query.id}: {e}"
            )
            query.status = SearchQuery.SearchStatus.FAILED
            query.error_message = f"An unexpected error occurred during polling: {e}"
            query.save()

    return f"Polling complete. Processed {processed_count} of {len(processing_queries)} running queries."
