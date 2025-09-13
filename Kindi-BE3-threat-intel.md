# Technical Plan: Kindi-BE3 Threat Intel App

## 1. Overview

The `threat_intel` app will provide Kindi users with the ability to query for threat intelligence data on various indicators of compromise (IOCs) such as domains, IP addresses, and file hashes. It will integrate with the public ThreatMiner API, use the `ip_rotator` service for all outgoing requests, and include a mechanism to respect the API's rate limits.

## 2. Database Schema

A generic model structure is best suited to handle the variety of data from ThreatMiner.

**File:** `threat_intel/models.py`

```python
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class Indicator(models.Model):
    """
    Represents a unique Indicator of Compromise (IOC).
    """
    class IndicatorType(models.TextChoices):
        DOMAIN = 'DOMAIN', _('Domain')
        IPV4 = 'IPV4', _('IPv4 Address')
        MD5 = 'MD5', _('MD5 Hash')
        SHA1 = 'SHA1', _('SHA1 Hash')
        SHA256 = 'SHA256', _('SHA256 Hash')

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
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, related_name="reports")
    report_type = models.CharField(max_length=50, help_text="e.g., 'passive_dns', 'whois', 'related_samples'")
    raw_data = models.JSONField(help_text="The raw JSON 'results' from the ThreatMiner API.")
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('indicator', 'report_type')

    def __str__(self):
        return f"{self.report_type} for {self.indicator.value}"
```

## 3. Architecture & Core Logic

**File:** `threat_intel/services.py`

*   **Rate Limiting:** A simple rate limiter will be implemented. We can use Django's cache framework to store timestamps of recent requests. Before making a new request, the service will check the cache to ensure the 10 queries/minute limit is not breached.

*   **`get_domain_intel(domain_name: str)` function:**
    *   Takes a domain name.
    *   Checks the rate limit.
    *   Uses `ip_rotator.services.get_rotated_session()` to get a session.
    *   Makes parallel or sequential requests to the ThreatMiner domain endpoint for various report types (`rt=1, 2, 5`, etc.).
    *   For each successful response, it creates or updates an `Indicator` record and saves the results in a `ThreatReport` record.
    *   Returns the collected `ThreatReport` objects.

*   **`get_ip_intel(ip_address: str)` function:**
    *   Similar to `get_domain_intel`, but for IP addresses, using the `/v2/host.php` endpoint.

*   **`get_hash_intel(file_hash: str)` function:**
    *   Similar to the above, but for file hashes, using the `/v2/sample.php` endpoint.

## 4. API Endpoints

The API will be designed for simplicity, with a separate endpoint for each indicator type.

**File:** `threat_intel/views.py`, `threat_intel/serializers.py`, `threat_intel/urls.py`

*   **`GET /api/v1/threat-intel/domain/<str:domain_name>/`**
    *   **Action:** Triggers a fresh data pull from ThreatMiner for the given domain.
    *   **Response:** A serialized `Indicator` object with its related `ThreatReport` objects nested within.
*   **`GET /api/v1/threat-intel/ip/<str:ip_address>/`**
    *   **Action:** Triggers a fresh data pull for the given IP address.
    *   **Response:** A serialized `Indicator` object with its nested reports.
*   **`GET /api/v1/threat-intel/hash/<str:file_hash>/`**
    *   **Action:** Triggers a fresh data pull for the given file hash.
    *   **Response:** A serialized `Indicator` object with its nested reports.

## 5. Configuration

*   `THREATMINER_BASE_URL`: `https://api.threatminer.org` will be stored as a constant in `threat_intel/services.py`.
*   No API key is needed.
