from rest_framework import serializers

from .models import Activity, Entity, Event, Location, Workspace


class ActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for the Activity model.
    """

    class Meta:
        model = Activity
        fields = "__all__"


class WorkspaceSerializer(serializers.ModelSerializer):
    """
    Serializer for the Workspace model. Handles both list and detail views.
    """

    # Use SerializerMethodField to get counts for the list view, matching the spec.
    entityCount = serializers.SerializerMethodField()
    eventCount = serializers.SerializerMethodField()
    locationCount = serializers.SerializerMethodField()
    activityCount = serializers.SerializerMethodField()

    # When retrieving a single workspace, we might want to show full details.
    # For now, we'll use the default PrimaryKeyRelatedField for relationships.
    # The detail view can be customized later to nest serializers if needed.
    activities = ActivitySerializer(many=True, read_only=True)

    # Explicitly define M2M fields to mark them as not required for validation during import.
    entities = serializers.PrimaryKeyRelatedField(
        queryset=Entity.objects.all(), many=True, required=False
    )
    events = serializers.PrimaryKeyRelatedField(
        queryset=Event.objects.all(), many=True, required=False
    )
    locations = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all(), many=True, required=False
    )

    class Meta:
        model = Workspace
        fields = [
            "id",
            "name",
            "description",
            "status",
            "priority",
            "notes",
            "analysis_state",
            "tags",
            "entities",
            "events",
            "locations",
            "created_at",
            "updated_at",
            # Count fields for summary view
            "entityCount",
            "eventCount",
            "locationCount",
            "activityCount",
            # Detailed relationships for detail view
            "activities",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "activities"]

    def get_entityCount(self, obj):
        return obj.entities.count()

    def get_eventCount(self, obj):
        return obj.events.count()

    def get_locationCount(self, obj):
        return obj.locations.count()

    def get_activityCount(self, obj):
        return obj.activities.count()

    def to_representation(self, instance):
        """
        Customize the representation based on the view action.
        For 'list', return a summary. For 'retrieve', return full details.
        """
        ret = super().to_representation(instance)

        # If the view is a list view, we only want the summary fields.
        is_list_view = getattr(self.context.get("view"), "action", "") == "list"

        if is_list_view:
            # For list views, return a summary representation.
            summary_fields = [
                "id",
                "name",
                "description",
                "status",
                "priority",
                "created_at",
                "updated_at",
                "entityCount",
                "eventCount",
                "locationCount",
                "activityCount",
            ]
            # The spec also includes 'noteLength', which we can add.
            ret["noteLength"] = len(instance.notes)

            # Filter the representation to only include summary fields.
            return {key: ret[key] for key in summary_fields if key in ret}
        else:
            # For detail views (retrieve, create, update), remove the summary count fields.
            del ret["entityCount"]
            del ret["eventCount"]
            del ret["locationCount"]
            del ret["activityCount"]

        return ret


class EventSerializer(serializers.ModelSerializer):
    """
    Serializer for the Event model.
    """

    class Meta:
        model = Event
        fields = [
            "id",
            "title",
            "timestamp",
            "description",
            "severity",
            "type",
            "location",
            "entities",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class LocationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Location model.
    """

    # To match the API spec's "markerType" field name.
    markerType = serializers.ChoiceField(
        choices=Location.MarkerType.choices, source="marker_type"
    )

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "latitude",
            "longitude",
            "markerType",
            "associated_entities",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class EntitySerializer(serializers.ModelSerializer):
    """
    Serializer for the Entity model.

    Handles serialization and deserialization of Entity instances,
    converting them to and from the JSON format defined in the API spec.
    """

    class Meta:
        model = Entity
        fields = [
            "id",
            "name",
            "type",
            "attributes",
            "coordinates",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
