import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class Indicator(models.Model):
    """
    Represents a unique Indicator of Compromise (IOC).
    """

    class IndicatorType(models.TextChoices):
        DOMAIN = "DOMAIN", _("Domain")
        IPV4 = "IPV4", _("IPv4 Address")
        MD5 = "MD5", _("MD5 Hash")
        SHA1 = "SHA1", _("SHA1 Hash")
        SHA256 = "SHA256", _("SHA256 Hash")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    value = models.CharField(max_length=255, unique=True, db_index=True)
    type = models.CharField(max_length=10, choices=IndicatorType.choices)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_type_display()}: {self.value}"


class ThreatReport(models.Model):
    """
    Stores a specific report (e.g., Passive DNS, WHOIS) for a given Indicator.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    indicator = models.ForeignKey(
        Indicator, on_delete=models.CASCADE, related_name="reports"
    )
    report_type = models.CharField(
        max_length=50, help_text="e.g., 'passive_dns', 'whois', 'related_samples'"
    )
    raw_data = models.JSONField(
        help_text="The raw JSON 'results' from the ThreatMiner API."
    )
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("indicator", "report_type")

    def __str__(self):
        return f"{self.report_type} for {self.indicator.value}"
