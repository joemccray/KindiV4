import uuid

from django.db import models


class SerpApiSearch(models.Model):
    """
    Represents a single search query made to any SerpAPI endpoint.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    engine = models.CharField(
        max_length=100,
        help_text="The SerpAPI engine used, e.g., 'google_news', 'google_scholar'.",
    )
    search_parameters = models.JSONField(
        help_text="The parameters sent to the SerpAPI."
    )
    raw_response = models.JSONField(
        help_text="The full JSON response from the SerpAPI."
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.engine} search - {self.created_at.isoformat()}"
