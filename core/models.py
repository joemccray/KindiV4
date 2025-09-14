import uuid

from django.db import models


class Workspace(models.Model):
    """
    A container for an investigation, grouping entities, events, and locations.
    """

    class WorkspaceStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        ON_HOLD = "on_hold", "On Hold"
        COMPLETED = "completed", "Completed"
        ARCHIVED = "archived", "Archived"

    class WorkspacePriority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"
        CRITICAL = "critical", "Critical"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    status = models.CharField(
        max_length=20, choices=WorkspaceStatus.choices, default=WorkspaceStatus.ACTIVE
    )
    priority = models.CharField(
        max_length=20,
        choices=WorkspacePriority.choices,
        default=WorkspacePriority.MEDIUM,
    )
    notes = models.TextField(blank=True)
    analysis_state = models.JSONField(
        default=dict, blank=True, help_text="Stores UI state, filters, etc."
    )
    tags = models.JSONField(
        default=list, blank=True, help_text="A list of tags for categorization."
    )

    entities = models.ManyToManyField("Entity", related_name="workspaces", blank=True)
    events = models.ManyToManyField("Event", related_name="workspaces", blank=True)
    locations = models.ManyToManyField(
        "Location", related_name="workspaces", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-updated_at"]


class Activity(models.Model):
    """
    Logs an action or change that occurred within a workspace.
    """

    class ActivityType(models.TextChoices):
        WORKSPACE_CREATED = "workspace_created", "Workspace Created"
        NOTE_ADDED = "note_added", "Note Added"
        ENTITY_SELECTED = "entity_selected", "Entity Selected"
        FILTER_APPLIED = "filter_applied", "Filter Applied"
        SEARCH_PERFORMED = "search_performed", "Search Performed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workspace = models.ForeignKey(
        Workspace, on_delete=models.CASCADE, related_name="activities"
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=50, choices=ActivityType.choices)
    description = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.get_type_display()} in {self.workspace.name} at {self.timestamp}"

    class Meta:
        ordering = ["-timestamp"]
        verbose_name_plural = "Activities"


class Event(models.Model):
    """
    Represents an incident or activity in an investigation timeline.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, help_text="The title of the event.")
    timestamp = models.DateTimeField(help_text="The date and time the event occurred.")
    description = models.TextField(
        blank=True, help_text="A detailed description of the event."
    )

    # These fields are flexible as per the spec not defining choices
    severity = models.CharField(
        max_length=50,
        blank=True,
        help_text="The severity level of the event (e.g., low, medium, high).",
    )
    type = models.CharField(
        max_length=50,
        blank=True,
        help_text="The type of event (e.g., communication, transaction).",
    )

    location = models.ForeignKey(
        "Location",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="events",
        help_text="The location where the event occurred.",
    )
    entities = models.ManyToManyField(
        "Entity",
        related_name="events",
        blank=True,
        help_text="Entities involved in this event.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Event"
        verbose_name_plural = "Events"
        ordering = ["-timestamp"]


class Location(models.Model):
    """
    Represents a geographic location relevant to an investigation.
    """

    class MarkerType(models.TextChoices):
        PRIMARY = "primary", "Primary"
        SECONDARY = "secondary", "Secondary"
        THREAT = "threat", "Threat"
        ASSET = "asset", "Asset"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="The name of the location.")
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, help_text="The latitude of the location."
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, help_text="The longitude of the location."
    )
    marker_type = models.CharField(
        max_length=20,
        choices=MarkerType.choices,
        default=MarkerType.SECONDARY,
        help_text="The type of map marker for this location.",
    )

    # Relationships will be added here
    associated_entities = models.ManyToManyField(
        "Entity",
        related_name="locations",
        blank=True,
        help_text="Entities associated with this location.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        ordering = ["-created_at"]


class Entity(models.Model):
    """
    Represents a person, organization, or asset in an investigation.
    """

    class EntityType(models.TextChoices):
        PERSON = "person", "Person"
        ORGANIZATION = "organization", "Organization"
        ASSET = "asset", "Asset"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text="The name of the entity.")
    type = models.CharField(
        max_length=20, choices=EntityType.choices, help_text="The type of the entity."
    )
    attributes = models.JSONField(
        default=dict,
        blank=True,
        help_text="Flexible key-value pair attributes for the entity.",
    )
    coordinates = models.JSONField(
        default=dict,
        blank=True,
        help_text="Visual graph coordinates, e.g., {'x': 100, 'y': 200}.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

    class Meta:
        verbose_name = "Entity"
        verbose_name_plural = "Entities"
        ordering = ["-created_at"]
