from django.urls import path

from .views import SerpApiViewSet

urlpatterns = [
    path(
        "ai-overview/",
        SerpApiViewSet.as_view({"post": "create_ai_overview_search"}),
        name="serpapi-ai-overview",
    ),
    path(
        "news/",
        SerpApiViewSet.as_view({"post": "create_news_search"}),
        name="serpapi-news",
    ),
    path(
        "scholar/",
        SerpApiViewSet.as_view({"post": "create_scholar_search"}),
        name="serpapi-scholar",
    ),
    path(
        "trends/",
        SerpApiViewSet.as_view({"post": "create_trends_search"}),
        name="serpapi-trends",
    ),
    path(
        "maps/",
        SerpApiViewSet.as_view({"post": "create_maps_search"}),
        name="serpapi-maps",
    ),
    path(
        "events/",
        SerpApiViewSet.as_view({"post": "create_events_search"}),
        name="serpapi-events",
    ),
    path(
        "finance/",
        SerpApiViewSet.as_view({"post": "create_finance_search"}),
        name="serpapi-finance",
    ),
    path(
        "youtube/",
        SerpApiViewSet.as_view({"post": "create_youtube_search"}),
        name="serpapi-youtube",
    ),
]
