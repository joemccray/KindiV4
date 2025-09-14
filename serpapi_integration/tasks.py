import logging
import os

from celery import shared_task
from serpapi import GoogleSearch

from .models import SerpApiSearch

logger = logging.getLogger(__name__)


@shared_task
def task_execute_serpapi_search(params: dict, engine_name: str):
    """
    Celery task to execute a search using the SerpApi client and log the result.
    """
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        logger.error("SERPAPI_API_KEY is not set in environment.")
        return

    search_params = params.copy()
    search_params["api_key"] = api_key

    try:
        search = GoogleSearch(search_params)
        results = search.get_dict()

        if "error" in results:
            logger.error(
                f"SerpAPI returned an error for {engine_name}: {results['error']}"
            )

        SerpApiSearch.objects.create(
            engine=engine_name,
            search_parameters=params,
            raw_response=results,
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred during SerpAPI search: {e}")
        SerpApiSearch.objects.create(
            engine=engine_name,
            search_parameters=params,
            raw_response={"error": f"Unexpected client error: {e}"},
        )
