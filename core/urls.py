from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AdvancedSearchAPIView,
    EntityViewSet,
    EventViewSet,
    GlobalSearchAPIView,
    LocationViewSet,
    RelationshipNetworkAPIView,
    RelationshipPathAPIView,
    RelationshipStrengthAPIView,
    SearchSuggestionsAPIView,
    WorkspaceExportAPIView,
    WorkspaceImportAPIView,
    WorkspaceViewSet,
)

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r"entities", EntityViewSet)
router.register(r"locations", LocationViewSet)
router.register(r"events", EventViewSet)
router.register(r"workspaces", WorkspaceViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path("", include(router.urls)),
    # Search endpoints
    path("search/", GlobalSearchAPIView.as_view(), name="global-search"),
    path("search/advanced/", AdvancedSearchAPIView.as_view(), name="advanced-search"),
    path(
        "search/suggestions/",
        SearchSuggestionsAPIView.as_view(),
        name="search-suggestions",
    ),
    # Relationship analysis endpoints
    path(
        "relationships/strength/",
        RelationshipStrengthAPIView.as_view(),
        name="relationship-strength",
    ),
    path(
        "relationships/network/",
        RelationshipNetworkAPIView.as_view(),
        name="relationship-network",
    ),
    path(
        "relationships/path/",
        RelationshipPathAPIView.as_view(),
        name="relationship-path",
    ),
    # Import/Export endpoints
    path(
        "export/workspace/<uuid:id>/",
        WorkspaceExportAPIView.as_view(),
        name="workspace-export",
    ),
    path(
        "import/workspace/", WorkspaceImportAPIView.as_view(), name="workspace-import"
    ),
]
