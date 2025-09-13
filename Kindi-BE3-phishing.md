# Technical Plan: Kindi-BE3 Phishing Intel App

## 1. Overview

The `phishing_intel` app will allow Kindi users to check if a given URL is a known phishing site by integrating with the PhishTank API. The app will use the real-time `checkurl` endpoint, manage API rate limits based on response headers, and use the `ip_rotator` service for all outgoing requests.

## 2. Database Schema

A simple model is needed to log the checks and cache the results.

**File:** `phishing_intel/models.py`

```python
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
    phishtank_id = models.PositiveIntegerField(null=True, blank=True, help_text="The PhishTank ID for the phish.")
    details_url = models.URLField(max_length=2048, null=True, blank=True, help_text="The PhishTank detail page for the phish.")
    checked_at = models.DateTimeField(auto_now_add=True)
    raw_response = models.JSONField(null=True, blank=True, help_text="The full JSON response from the PhishTank API.")

    def __str__(self):
        return f"{self.url_to_check} - Is Phishing: {self.is_phishing}"
```

## 3. Architecture & Core Logic

**File:** `phishing_intel/services.py`

*   **Rate Limiting:** The service will not use a simple time-based check like the ThreatMiner one. Instead, it will read the `X-Request-Limit-*` headers from the *previous* API response and store them in the Django cache. Before making a new request, it will check the cache to see if it's approaching the limit.

*   **`check_url_for_phishing(url_to_check: str)` function:**
    *   Takes a URL string as input.
    *   Checks the rate limit based on cached header values.
    *   Uses `ip_rotator.services.get_rotated_session()` to get a session.
    *   URL-encodes the input URL.
    *   Constructs the `POST` request to `http://checkurl.phishtank.com/checkurl/` with the `url`, `format=json`, and the `PHISHTANK_API_KEY`.
    *   Sets a custom `User-Agent` header.
    *   Executes the request.
    *   Parses the response headers to update the rate limit information in the cache.
    *   Parses the response body.
    *   Creates or updates a `URLCheck` record in the database with the results.
    *   Returns the `URLCheck` object.

## 4. API Endpoints

A simple endpoint is needed to submit a URL for checking.

**File:** `phishing_intel/views.py`, `phishing_intel/serializers.py`, `phishing_intel/urls.py`

*   **`POST /api/v1/phishing-intel/check/`**
    *   **Action:** Submits a URL to be checked against PhishTank.
    *   **Request Body:** `{"url": "https://example.com/suspicious-link"}`
    *   **Response:** A serialized `URLCheck` object with the results of the check.

## 5. Configuration

*   `PHISHTANK_API_KEY`: Will need to be acquired and added to the `.env` file and loaded in `settings.py`.
*   `PHISHTANK_CHECK_URL`: `http://checkurl.phishtank.com/checkurl/` will be a constant in `services.py`.
*   `KINDI_USER_AGENT`: A custom user agent string will be defined in `settings.py`.
