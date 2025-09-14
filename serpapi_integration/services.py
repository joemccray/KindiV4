from .tasks import task_execute_serpapi_search


def search_google_ai_overview(query: str):
    params = {"q": query, "engine": "google"}
    task_execute_serpapi_search.delay(params, "google_ai_overview")


def search_google_news(query: str):
    params = {"q": query, "engine": "google", "tbm": "nws"}
    task_execute_serpapi_search.delay(params, "google_news")


def search_google_scholar(query: str):
    params = {"q": query, "engine": "google_scholar"}
    task_execute_serpapi_search.delay(params, "google_scholar")


def search_google_trends(query: str):
    params = {"q": query, "engine": "google_trends"}
    task_execute_serpapi_search.delay(params, "google_trends")


def search_google_maps(query: str):
    params = {"q": query, "engine": "google_maps"}
    task_execute_serpapi_search.delay(params, "google_maps")


def search_google_events(query: str):
    params = {"q": query, "engine": "google_events"}
    task_execute_serpapi_search.delay(params, "google_events")


def search_google_finance(query: str):
    params = {"q": query, "engine": "google_finance"}
    task_execute_serpapi_search.delay(params, "google_finance")


def search_youtube(query: str):
    params = {"search_query": query, "engine": "youtube"}
    task_execute_serpapi_search.delay(params, "youtube")
