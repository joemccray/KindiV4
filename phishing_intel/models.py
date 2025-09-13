import uuid

from django.db import models


class URLCheck(models.Model):
    """
    Represents a check of a URL against the PhishTank database and its result.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url_to_check = models.URLField(max_length=2048)
    is_phishing = models.BooleanField(default=False)
    in_phishtank_database = models.BooleanField(default=False)
    phishtank_id = models.PositiveIntegerField(
        null=True, blank=True, help_text="The PhishTank ID for the phish."
    )
    details_url = models.URLField(
        max_length=2048,
        null=True,
        blank=True,
        help_text="The PhishTank detail page for the phish.",
    )
    checked_at = models.DateTimeField(auto_now_add=True)
    raw_response = models.JSONField(
        null=True,
        blank=True,
        help_text="The full JSON response from the PhishTank API.",
    )

    def __str__(self):
        return f"{self.url_to_check} - Is Phishing: {self.is_phishing}"
