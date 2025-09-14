import json

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .models import Activity, Entity, Event, Location, Workspace
from .serializers import (
    EntitySerializer,
    EventSerializer,
    LocationSerializer,
    WorkspaceSerializer,
)


class WorkspaceViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows workspaces to be viewed or edited.
    """

    queryset = Workspace.objects.all().order_by("-updated_at")
    serializer_class = WorkspaceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """
        Custom create action to automatically log the creation activity.
        """
        workspace = serializer.save()
        Activity.objects.create(
            workspace=workspace,
            type=Activity.ActivityType.WORKSPACE_CREATED,
            description=f"Workspace '{workspace.name}' was created.",
        )

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy action to return a success message upon deletion.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={"success": True, "message": "Workspace deleted successfully"},
            status=status.HTTP_200_OK,
        )


class EventViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows events to be viewed or edited.
    """

    queryset = Event.objects.all().order_by("-timestamp")
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy action to return a success message upon deletion.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={"success": True, "message": "Event deleted successfully"},
            status=status.HTTP_200_OK,
        )


class LocationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows locations to be viewed or edited.
    """

    queryset = Location.objects.all().order_by("-created_at")
    serializer_class = LocationSerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy action to return a success message upon deletion.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={"success": True, "message": "Location deleted successfully"},
            status=status.HTTP_200_OK,
        )


class EntityViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows entities to be viewed or edited.

    Provides `list`, `create`, `retrieve`, `update`, and `destroy` actions.
    """

    queryset = Entity.objects.all().order_by("-created_at")
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated]

    def destroy(self, request, *args, **kwargs):
        """
        Custom destroy action to return a success message upon deletion.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            data={"success": True, "message": "Entity deleted successfully"},
            status=status.HTTP_200_OK,
        )


# --- Search API Views ---


class GlobalSearchAPIView(APIView, PageNumberPagination):
    """
    Performs a global search across entities, events, and locations.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query", None)
        if not query:
            return Response(
                {"error": "A 'query' parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        search_types_str = request.query_params.get(
            "types", "entities,events,locations"
        )
        search_types = [t.strip() for t in search_types_str.split(",")]

        results = {}
        total_results = 0

        if "entities" in search_types:
            entities = Entity.objects.filter(
                Q(name__icontains=query) | Q(attributes__icontains=query)
            )
            results["entities"] = EntitySerializer(entities, many=True).data
            total_results += entities.count()

        if "events" in search_types:
            events = Event.objects.filter(
                Q(title__icontains=query) | Q(description__icontains=query)
            )
            results["events"] = EventSerializer(events, many=True).data
            total_results += events.count()

        if "locations" in search_types:
            locations = Location.objects.filter(name__icontains=query)
            results["locations"] = LocationSerializer(locations, many=True).data
            total_results += locations.count()

        # Note: A proper implementation would paginate the combined results,
        # which is complex. For this iteration, we return unpaginated results
        # within each type, but the pagination class is included for future extension.

        return Response(
            {
                **results,
                "totalResults": total_results,
            }
        )


class AdvancedSearchAPIView(APIView):
    """
    Performs an advanced search with multiple filters.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query", None)
        if not query:
            return Response(
                {"error": "A 'query' parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Build filters based on query parameters
        entity_filters = Q()
        event_filters = Q()
        location_filters = Q()

        # Text search logic
        if request.query_params.get("exactMatch") == "true":
            lookup = "exact"
        else:
            lookup = "contains"

        if request.query_params.get("caseSensitive") != "true":
            lookup = f"i{lookup}"
        search_field = lookup

        # Entity filters
        if "entities" in request.query_params.get("types", "entities"):
            entity_q = Q(**{f"name__{search_field}": query})
            if request.query_params.get("includeAttributes", "true") == "true":
                # SQLite does not support case-sensitive 'contains' on JSONField.
                # We will always use 'icontains' for attribute searches.
                entity_q |= Q(attributes__icontains=query)
            entity_filters &= entity_q

            if request.query_params.get("entityTypes"):
                entity_filters &= Q(
                    type__in=request.query_params.get("entityTypes").split(",")
                )

        # Event filters
        if "events" in request.query_params.get("types", "events"):
            event_filters &= Q(**{f"title__{search_field}": query}) | Q(
                **{f"description__{search_field}": query}
            )
            if request.query_params.get("eventTypes"):
                event_filters &= Q(
                    type__in=request.query_params.get("eventTypes").split(",")
                )
            if request.query_params.get("startDate"):
                event_filters &= Q(timestamp__gte=request.query_params.get("startDate"))
            if request.query_params.get("endDate"):
                event_filters &= Q(timestamp__lte=request.query_params.get("endDate"))

        # Location filters
        if "locations" in request.query_params.get("types", "locations"):
            location_filters &= Q(**{f"name__{search_field}": query})
            if request.query_params.get("locationTypes"):
                location_filters &= Q(
                    marker_type__in=request.query_params.get("locationTypes").split(",")
                )

        # Execute queries
        entities = (
            Entity.objects.filter(entity_filters)
            if "entities" in request.query_params.get("types", "entities")
            else Entity.objects.none()
        )
        events = (
            Event.objects.filter(event_filters)
            if "events" in request.query_params.get("types", "events")
            else Event.objects.none()
        )
        locations = (
            Location.objects.filter(location_filters)
            if "locations" in request.query_params.get("types", "locations")
            else Location.objects.none()
        )

        return Response(
            {
                "entities": EntitySerializer(entities, many=True).data,
                "events": EventSerializer(events, many=True).data,
                "locations": LocationSerializer(locations, many=True).data,
                "totalResults": entities.count() + events.count() + locations.count(),
            }
        )


class SearchSuggestionsAPIView(APIView):
    """
    Returns search suggestions based on partial input.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query", None)
        if not query:
            return Response(
                {"error": "A 'query' parameter is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        max_suggestions = int(request.query_params.get("maxSuggestions", 5))

        # Gather suggestions from different models
        entity_suggestions = Entity.objects.filter(name__icontains=query).values_list(
            "name", flat=True
        )
        location_suggestions = Location.objects.filter(
            name__icontains=query
        ).values_list("name", flat=True)
        event_suggestions = Event.objects.filter(title__icontains=query).values_list(
            "title", flat=True
        )

        # Combine, get unique suggestions, and limit the count
        all_suggestions = (
            list(entity_suggestions)
            + list(location_suggestions)
            + list(event_suggestions)
        )

        # A simple way to get unique suggestions while preserving some order
        unique_suggestions = sorted(
            list(set(all_suggestions)), key=lambda x: x.lower().find(query.lower())
        )

        return Response({"suggestions": unique_suggestions[:max_suggestions]})


# --- Relationship Analysis API Views ---


class RelationshipStrengthAPIView(APIView):
    """
    Calculates and returns the relationship strength between two entities.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        entity1_id = request.query_params.get("entity1")
        entity2_id = request.query_params.get("entity2")

        if not entity1_id or not entity2_id:
            return Response(
                {
                    "error": "Both 'entity1' and 'entity2' query parameters are required."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            entity1 = Entity.objects.get(pk=entity1_id)
            entity2 = Entity.objects.get(pk=entity2_id)
        except Entity.DoesNotExist:
            return Response(
                {"error": "One or both entities not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        data = services.calculate_relationship_strength(entity1, entity2)
        return Response(data)


class RelationshipNetworkAPIView(APIView):
    """
    Returns network graph data by calling the service layer.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        entity_ids_str = request.query_params.get("entityIds")
        depth = int(request.query_params.get("depth", 1))
        min_strength = int(request.query_params.get("minStrength", 0))

        if entity_ids_str:
            root_entities = Entity.objects.filter(pk__in=entity_ids_str.split(","))
        else:
            root_entities = Entity.objects.all()

        graph_data = services.build_relationship_network(
            list(root_entities), depth, min_strength
        )
        return Response(graph_data)


class RelationshipPathAPIView(APIView):
    """
    Finds the shortest path between two entities by calling the service layer.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        source_id = request.query_params.get("sourceId")
        target_id = request.query_params.get("targetId")
        max_depth = int(request.query_params.get("maxDepth", 3))

        if not source_id or not target_id:
            return Response(
                {"error": "sourceId and targetId are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            source_entity = Entity.objects.get(pk=source_id)
            target_entity = Entity.objects.get(pk=target_id)
        except Entity.DoesNotExist:
            return Response(
                {"error": "Source or target entity not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        path_data = services.find_shortest_path(source_entity, target_entity, max_depth)
        return Response(path_data)


# --- Import/Export API Views ---


class WorkspaceExportAPIView(APIView):
    """
    Exports a complete workspace and its related data as a JSON file.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        workspace_id = kwargs.get("id")
        try:
            workspace = Workspace.objects.get(pk=workspace_id)
        except Workspace.DoesNotExist:
            return Response(
                {"error": "Workspace not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the workspace and its related objects
        # We need a serializer that can handle the full nested structure for export.
        # For simplicity, we'll build the data structure manually here.

        entities = workspace.entities.all()
        events = workspace.events.all()
        locations = workspace.locations.all()

        export_data = {
            "version": "1.0",
            "exported_at": timezone.now().isoformat(),
            "workspace": WorkspaceSerializer(workspace).data,
            "related_data": {
                "entities": EntitySerializer(entities, many=True).data,
                "events": EventSerializer(events, many=True).data,
                "locations": LocationSerializer(locations, many=True).data,
            },
        }

        # Remove summary fields from the nested workspace data
        for field in ["entityCount", "eventCount", "locationCount", "activityCount"]:
            if field in export_data["workspace"]:
                del export_data["workspace"][field]

        # Prepare the response for file download
        filename = (
            f"workspace-{workspace.name}-{timezone.now().strftime('%Y%m%d')}.json"
        )
        response = Response(
            export_data, status=status.HTTP_200_OK, content_type="application/json"
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

        return response


class WorkspaceImportAPIView(APIView):
    """
    Imports a workspace from a JSON file.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        file_obj = request.data.get("file", None)
        if not file_obj:
            return Response(
                {"error": "File upload is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            import_data = json.load(file_obj)
        except json.JSONDecodeError:
            return Response(
                {"error": "Invalid JSON file."}, status=status.HTTP_400_BAD_REQUEST
            )

        # --- Deserialization and Object Creation ---

        # 1. Create Workspace by building a clean data dictionary
        ws_data = import_data.get("workspace", {})
        workspace_create_data = {
            key: ws_data[key]
            for key in [
                "name",
                "description",
                "status",
                "priority",
                "notes",
                "analysis_state",
                "tags",
            ]
            if key in ws_data
        }

        workspace_serializer = WorkspaceSerializer(data=workspace_create_data)
        if not workspace_serializer.is_valid():
            return Response(
                workspace_serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )
        new_workspace = workspace_serializer.save()

        # 2. Create Related Objects
        # This is a simplified import. A real-world version would need to handle
        # conflicts, updates, and mapping old IDs to new ones.
        # Here, we just create new objects based on the imported data.

        related_data = import_data.get("related_data", {})

        # Entities
        created_entities = []
        for entity_data in related_data.get("entities", []):
            entity_data.pop("id", None)
            entity_serializer = EntitySerializer(data=entity_data)
            if entity_serializer.is_valid():
                created_entities.append(entity_serializer.save())

        # Locations
        created_locations = []
        for loc_data in related_data.get("locations", []):
            loc_data.pop("id", None)
            loc_serializer = LocationSerializer(data=loc_data)
            if loc_serializer.is_valid():
                created_locations.append(loc_serializer.save())

        # Events (depend on locations and entities)
        created_events = []
        for event_data in related_data.get("events", []):
            event_data.pop("id", None)
            # We can't map old relations, so we clear them for this simple import
            event_data["location"] = None
            event_data["entities"] = []
            event_serializer = EventSerializer(data=event_data)
            if event_serializer.is_valid():
                created_events.append(event_serializer.save())

        # 3. Associate new objects with the new workspace
        new_workspace.entities.set(created_entities)
        new_workspace.events.set(created_events)
        new_workspace.locations.set(created_locations)
        new_workspace.save()

        return Response(
            {"success": True, "workspace": WorkspaceSerializer(new_workspace).data},
            status=status.HTTP_201_CREATED,
        )
