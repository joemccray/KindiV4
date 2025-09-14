import json

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

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
    # permission_classes = [permissions.IsAuthenticated]

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
    # permission_classes = [permissions.IsAuthenticated]

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
    # permission_classes = [permissions.IsAuthenticated]

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
    # permission_classes = [permissions.IsAuthenticated] # Will be enabled later

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
            lookup = "i" + lookup
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

        # Find shared events and locations
        shared_events = Event.objects.filter(entities=entity1).filter(entities=entity2)
        shared_locations = Location.objects.filter(associated_entities=entity1).filter(
            associated_entities=entity2
        )

        # Calculate strength (simple count for now)
        strength = shared_events.count() + shared_locations.count()

        return Response(
            {
                "strength": strength,
                "connections": {
                    "sharedEvents": [
                        {"id": str(e.id), "title": e.title} for e in shared_events
                    ],
                    "sharedLocations": [
                        {"id": str(loc.id), "name": loc.name}
                        for loc in shared_locations
                    ],
                },
            }
        )


class RelationshipNetworkAPIView(APIView):
    """
    Returns network graph data for visualization.
    """

    def get(self, request, *args, **kwargs):
        entity_ids_str = request.query_params.get("entityIds")
        depth = int(request.query_params.get("depth", 1))
        min_strength = int(request.query_params.get("minStrength", 0))

        # Start with a root set of entities
        if entity_ids_str:
            root_entities = Entity.objects.filter(pk__in=entity_ids_str.split(","))
        else:
            # If no IDs are provided, this could be a very large query.
            # In a real app, we would require root IDs or apply other limits.
            # For now, we'll proceed but this is a potential performance issue.
            root_entities = Entity.objects.all()

        if not root_entities.exists():
            return Response({"nodes": [], "links": []})

        # Use BFS to explore the graph
        nodes = set()
        links = set()
        queue = [(entity, 0) for entity in root_entities]  # (entity, current_depth)
        visited = {entity.pk for entity in root_entities}

        while queue:
            current_entity, current_depth = queue.pop(0)
            nodes.add(current_entity)

            if current_depth >= depth:
                continue

            # Find neighbors
            events = current_entity.events.all()
            locations = current_entity.locations.all()
            neighbor_q = Q(events__in=events) | Q(locations__in=locations)
            neighbors = (
                Entity.objects.filter(neighbor_q)
                .distinct()
                .exclude(pk=current_entity.pk)
            )

            for neighbor in neighbors:
                # Calculate strength
                shared_events_count = (
                    Event.objects.filter(entities=current_entity)
                    .filter(entities=neighbor)
                    .count()
                )
                shared_locs_count = (
                    Location.objects.filter(associated_entities=current_entity)
                    .filter(associated_entities=neighbor)
                    .count()
                )
                strength = shared_events_count + shared_locs_count

                if strength >= min_strength:
                    # Add link (use a tuple of sorted IDs to ensure uniqueness)
                    link_tuple = tuple(
                        sorted((str(current_entity.pk), str(neighbor.pk)))
                    )
                    links.add((link_tuple[0], link_tuple[1], strength))

                if neighbor.pk not in visited:
                    visited.add(neighbor.pk)
                    queue.append((neighbor, current_depth + 1))

        # Format for response
        formatted_nodes = [
            {"id": str(n.id), "name": n.name, "type": n.type, "group": 1} for n in nodes
        ]
        formatted_links = [
            {"source": link[0], "target": link[1], "value": link[2]} for link in links
        ]

        return Response({"nodes": formatted_nodes, "links": formatted_links})


class RelationshipPathAPIView(APIView):
    """
    Finds the shortest path between two entities using Breadth-First Search.
    """

    def _get_neighbors(self, entity):
        """Helper to find all entities connected to the given entity."""
        # Find events and locations connected to the entity
        events = entity.events.all()
        locations = entity.locations.all()

        # Find all other entities connected to those events/locations
        neighbor_q = Q(events__in=events) | Q(locations__in=locations)
        neighbors = Entity.objects.filter(neighbor_q).distinct().exclude(pk=entity.pk)
        return neighbors

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
            source_node = Entity.objects.get(pk=source_id)
            target_node = Entity.objects.get(pk=target_id)
        except Entity.DoesNotExist:
            return Response(
                {"error": "Source or target entity not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # BFS implementation
        queue = [
            (source_node, [source_node])
        ]  # Queue stores (current_node, path_to_node)
        visited = {source_node.pk}

        while queue:
            current_node, path = queue.pop(0)

            if current_node == target_node:
                # Path found, now format it for the response
                formatted_path = []
                for i in range(len(path) - 1):
                    # For each step in the path, find the connection
                    shared_events = Event.objects.filter(entities=path[i]).filter(
                        entities=path[i + 1]
                    )
                    shared_locs = Location.objects.filter(
                        associated_entities=path[i]
                    ).filter(associated_entities=path[i + 1])

                    connection = None
                    if shared_events.exists():
                        event = shared_events.first()
                        connection = {
                            "type": "event",
                            "id": str(event.id),
                            "name": event.title,
                        }
                    elif shared_locs.exists():
                        loc = shared_locs.first()
                        connection = {
                            "type": "location",
                            "id": str(loc.id),
                            "name": loc.name,
                        }

                    formatted_path.append(
                        {
                            "entity": EntitySerializer(path[i]).data,
                            "connection": connection,
                        }
                    )
                # Add the final entity in the path
                formatted_path.append(
                    {"entity": EntitySerializer(path[-1]).data, "connection": None}
                )

                return Response({"path": formatted_path, "pathLength": len(path) - 1})

            if len(path) > max_depth:
                continue

            for neighbor in self._get_neighbors(current_node):
                if neighbor.pk not in visited:
                    visited.add(neighbor.pk)
                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append((neighbor, new_path))

        return Response({"path": [], "pathLength": 0}, status=status.HTTP_200_OK)


# --- Import/Export API Views ---


class WorkspaceExportAPIView(APIView):
    """
    Exports a complete workspace and its related data as a JSON file.
    """

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
