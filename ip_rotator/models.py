import uuid

from django.db import models


class ApiGatewayProxy(models.Model):
    """
    Represents a provisioned AWS API Gateway endpoint used for IP rotation.
    """

    class ProxyStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        CREATING = "CREATING", "Creating"
        DELETING = "DELETING", "Deleting"
        ERROR = "ERROR", "Error"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_site = models.URLField(
        max_length=255, help_text="The base URL this proxy is configured for."
    )
    aws_region = models.CharField(
        max_length=50, help_text="The AWS region where the gateway is deployed."
    )
    api_id = models.CharField(
        max_length=50, unique=True, help_text="The AWS API Gateway ID."
    )
    endpoint_url = models.URLField(
        max_length=255, unique=True, help_text="The invocation URL of the API Gateway."
    )
    status = models.CharField(
        max_length=10, choices=ProxyStatus.choices, default=ProxyStatus.INACTIVE
    )
    last_used = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last time this proxy was used.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.target_site} ({self.aws_region}) - {self.status}"

    class Meta:
        verbose_name = "API Gateway Proxy"
        verbose_name_plural = "API Gateway Proxies"
        ordering = ["-created_at"]
