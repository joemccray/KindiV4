# Technical Plan: Kindi-BE3 Vulnerability Intel App

## 1. Overview

The `vulnerability_intel` app will provide a comprehensive vulnerability intelligence service by integrating with two primary sources: the NVD API and the Vulners API. The app will allow users to query for vulnerabilities by CVE ID or product keywords, and it will aggregate and store the results from both APIs. All outgoing requests will use the `ip_rotator` service.

## 2. Database Schema

A unified model is needed to store vulnerability data from different sources, with a clear link back to the source.

**File:** `vulnerability_intel/models.py`

```python
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _

class Vulnerability(models.Model):
    """
    Represents a unique vulnerability, typically identified by a CVE ID.
    """
    id = models.CharField(max_length=50, primary_key=True, help_text="e.g., CVE-2021-44228")
    description = models.TextField(null=True, blank=True)
    cvss_v3_score = models.FloatField(null=True, blank=True)
    cvss_v3_vector = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.id

class VulnerabilityReference(models.Model):
    """
    Stores a reference URL for a vulnerability.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.CASCADE, related_name="references")
    url = models.URLField(max_length=2048)

    def __str__(self):
        return self.url

class VulnerabilitySourceData(models.Model):
    """
    Stores the raw JSON data for a vulnerability from a specific source (NVD or Vulners).
    """
    class Source(models.TextChoices):
        NVD = 'NVD', _('NIST National Vulnerability Database')
        VULNERS = 'VULNERS', _('Vulners Database')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vulnerability = models.ForeignKey(Vulnerability, on_delete=models.CASCADE, related_name="source_data")
    source = models.CharField(max_length=10, choices=Source.choices)
    raw_data = models.JSONField()
    fetched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('vulnerability', 'source')

    def __str__(self):
        return f"{self.get_source_display()} data for {self.vulnerability.id}"
```

## 3. Architecture & Core Logic

**File:** `vulnerability_intel/services.py`

*   **`_get_nvd_data(cve_id: str)` private function:**
    *   Handles the specific logic for calling the NVD API for a given CVE ID.
    *   Uses `ip_rotator` service.
    *   Returns the parsed JSON data.

*   **`_get_vulners_data(cve_id: str)` private function:**
    *   Handles the specific logic for calling the Vulners API (`/api/v3/search/id/`) for a given CVE ID.
    *   Uses `ip_rotator` service.

*   **`get_vulnerability_intel(cve_id: str)` primary service function:**
    *   Takes a CVE ID.
    *   Calls `_get_nvd_data` and `_get_vulners_data` (can be done in parallel).
    *   Parses the data from both sources to create or update a `Vulnerability` record.
    *   Creates or updates `VulnerabilityReference` and `VulnerabilitySourceData` records.
    *   Returns the fully populated `Vulnerability` object.

## 4. API Endpoints

**File:** `vulnerability_intel/views.py`, `vulnerability_intel/serializers.py`, `vulnerability_intel/urls.py`

*   **`GET /api/v1/vulnerabilities/<str:cve_id>/`**
    *   **Action:** Retrieves aggregated intelligence for a specific CVE ID. It will first check the local database for cached data. If the data is old or missing, it triggers a fresh pull from the APIs via the service layer.
    *   **Response:** A detailed, serialized `Vulnerability` object with nested references and source data.

## 5. Configuration

*   `NVD_API_KEY`: To be added to `.env`.
*   `VULNERS_API_KEY`: To be added to `.env`.
*   Base URLs for both APIs will be constants in `services.py`.
