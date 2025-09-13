import logging
import os

from serpapi import GoogleSearch

from .models import SerpApiSearch

logger = logging.getLogger(__name__)


def _execute_search(params: dict, engine_name: str) -> dict:
    """
    A helper function to execute a search and log it.
    """
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        raise ValueError("SERPAPI_API_KEY is not set in environment.")

    search_params = params.copy()
    search_params["api_key"] = api_key

    try:
        search = GoogleSearch(search_params)
        results = search.get_dict()

        if "error" in results:
            logger.error(
                f"SerpAPI returned an error for {engine_name}: {results['error']}"
            )
            # Still log the attempt, but with the error response
            SerpApiSearch.objects.create(
                engine=engine_name,
                search_parameters=params,
                raw_response=results,
            )
            return results

        SerpApiSearch.objects.create(
            engine=engine_name,
            search_parameters=params,
            raw_response=results,
        )
        return results

    except Exception as e:
        logger.error(f"An unexpected error occurred during SerpAPI search: {e}")
        # Log the failure
        SerpApiSearch.objects.create(
            engine=engine_name,
            search_parameters=params,
            raw_response={"error": f"Unexpected client error: {e}"},
        )
        raise


def search_google_ai_overview(query: str):
    # Note: As per SerpAPI docs, AI Overviews are part of the standard google engine
    params = {"q": query, "engine": "google"}
    return _execute_search(params, "google_ai_overview")


def search_google_news(query: str):
    params = {"q": query, "engine": "google", "tbm": "nws"}
    return _execute_search(params, "google_news")


def search_google_scholar(query: str):
    params = {"q": query, "engine": "google_scholar"}
    return _execute_search(params, "google_scholar")


def search_google_trends(query: str):
    params = {"q": query, "engine": "google_trends"}
    return _execute_search(params, "google_trends")


def search_google_maps(query: str):
    params = {"q": query, "engine": "google_maps"}
    return _execute_search(params, "google_maps")


def search_google_events(query: str):
    params = {"q": query, "engine": "google_events"}
    return _execute_search(params, "google_events")


def search_google_finance(query: str):
    params = {"q": query, "engine": "google_finance"}
    return _execute_search(params, "google_finance")


def search_youtube(query: str):
    params = {"search_query": query, "engine": "youtube"}
    return _execute_search(params, "youtube")
