import uuid

from django.db import models

# from django.contrib.auth.models import User # Or custom user model


class SearchQuery(models.Model):
    """
    Represents a search initiated by a user. Manages the async process.
    """

    class SearchStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSING = "PROCESSING", "Processing"
        COMPLETED = "COMPLETED", "Completed"
        FAILED = "FAILED", "Failed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_filter = models.JSONField(help_text="The filter object sent to ReachStream.")
    status = models.CharField(
        max_length=10, choices=SearchStatus.choices, default=SearchStatus.PENDING
    )
    reachstream_batch_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text="The batch_process_id from ReachStream.",
    )
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Search {self.id} - {self.status}"


class PersonProfile(models.Model):
    """
    Stores the profile of a person retrieved from ReachStream.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    search_query = models.ForeignKey(
        SearchQuery, on_delete=models.CASCADE, related_name="results"
    )
    full_name = models.CharField(max_length=255, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    raw_data = models.JSONField(
        help_text="The full, raw JSON response for this profile."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or "Unnamed Profile"
