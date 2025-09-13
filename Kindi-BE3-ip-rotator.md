# Technical Plan: Kindi-BE3 IP Rotator App

## 1. Overview

The `ip_rotator` app will provide a centralized, persistent, and scalable IP rotation service for the entire Kindi platform. It will adapt the core logic of the `requests-ip-rotator` library into a native Django application. Instead of creating and destroying proxies on-the-fly, this app will manage a long-lived pool of AWS API Gateway endpoints, storing their state in the database and providing a simple service for other Kindi apps to use.

## 2. Database Schema

We will use a single model to store the state of each provisioned proxy gateway.

**File:** `ip_rotator/models.py`

```python
from django.db import models
import uuid

class ApiGatewayProxy(models.Model):
    """
    Represents a provisioned AWS API Gateway endpoint used for IP rotation.
    """
    class ProxyStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        CREATING = 'CREATING', 'Creating'
        DELETING = 'DELETING', 'Deleting'
        ERROR = 'ERROR', 'Error'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    target_site = models.URLField(max_length=255, help_text="The base URL this proxy is configured for.")
    aws_region = models.CharField(max_length=50, help_text="The AWS region where the gateway is deployed.")
    api_id = models.CharField(max_length=50, unique=True, help_text="The AWS API Gateway ID.")
    endpoint_url = models.URLField(max_length=255, unique=True, help_text="The invocation URL of the API Gateway.")
    status = models.CharField(max_length=10, choices=ProxyStatus.choices, default=ProxyStatus.INACTIVE)
    last_used = models.DateTimeField(null=True, blank=True, help_text="Timestamp of the last time this proxy was used.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.target_site} ({self.aws_region}) - {self.status}"

    class Meta:
        verbose_name = "API Gateway Proxy"
        verbose_name_plural = "API Gateway Proxies"
        ordering = ['-created_at']
```

## 3. Architecture & Core Logic

The app's logic will be encapsulated in a `services.py` file to separate business logic from the views/models.

**File:** `ip_rotator/services.py`

*   **`provision_gateways(target_site, regions)` function:**
    *   Accepts a target site URL and a list of AWS regions.
    *   Uses `boto3` to create API Gateways in each region.
    *   For each successful creation, it creates an `ApiGatewayProxy` instance in the database.
    *   Manages status updates (e.g., `CREATING` -> `ACTIVE` or `ERROR`).
    *   This will likely be exposed as a Django management command for administrative use (e.g., `python manage.py provision_proxies`).

*   **`decommission_gateways(proxy_ids)` function:**
    *   Accepts a list of `ApiGatewayProxy` IDs.
    *   Uses `boto3` to delete the corresponding API Gateways from AWS.
    *   Updates the status to `DELETING` and finally removes the record from the database upon success.
    *   This will also be exposed as a management command.

*   **`get_rotated_session(target_site)` function:**
    *   This is the primary function other apps will call.
    *   It retrieves an active `ApiGatewayProxy` for the given `target_site` from the database (e.g., the least recently used one).
    *   It creates a `requests.Session` object.
    *   It creates a custom `requests.adapters.HTTPAdapter` that uses the selected proxy's `endpoint_url`.
    *   It mounts the adapter to the session for the `target_site`.
    *   It updates the `last_used` timestamp for the proxy.
    *   It returns the configured `requests.Session` object.

## 4. API Endpoints

While the primary interface for other apps will be the Python service functions, we can expose simple administrative endpoints.

**File:** `ip_rotator/views.py`, `ip_rotator/serializers.py`, `ip_rotator/urls.py`

*   **`GET /api/v1/ip-rotator/proxies/`**
    *   Lists all `ApiGatewayProxy` instances from the database.
    *   Useful for monitoring the state of the proxy pool.
    *   Read-only endpoint.
*   **`GET /api/v1/ip-rotator/proxies/<uuid:id>/`**
    *   Retrieves details of a specific proxy.
    *   Read-only.

## 5. Third-Party Libraries

*   `boto3`: The AWS SDK for Python, for interacting with AWS services.
*   `requests`: For making HTTP requests.

These will be added to `requirements.txt`.

## 6. Configuration

The following settings will be needed in `kindi_be3/settings.py`:

*   `AWS_ACCESS_KEY_ID`
*   `AWS_SECRET_ACCESS_KEY`
*   `AWS_DEFAULT_REGION` (as a fallback)

These should be loaded from environment variables using `python-dotenv`, which is already installed.
