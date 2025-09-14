from rest_framework import status, viewsets
from rest_framework.response import Response

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
