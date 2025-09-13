# Technical Plan: Kindi-BE3 People Search App

## 1. Overview

The `people_search` app will provide the core functionality for searching for business contacts and organizations using the ReachStream API. It will feature an asynchronous workflow to handle potentially long-running searches and will store the retrieved data in a structured format for future analysis within the Kindi platform. All outgoing requests to the ReachStream API will be routed through the `ip_rotator` service.

## 2. Database Schema

We'll need models to manage the search process and store the results.

**File:** `people_search/models.py`

```python
import uuid
from django.db import models
# from django.contrib.auth.models import User # Or custom user model

class SearchQuery(models.Model):
    """
    Represents a search initiated by a user. Manages the async process.
    """
    class SearchStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_filter = models.JSONField(help_text="The filter object sent to ReachStream.")
    status = models.CharField(max_length=10, choices=SearchStatus.choices, default=SearchStatus.PENDING)
    reachstream_batch_id = models.CharField(max_length=100, null=True, blank=True, help_text="The batch_process_id from ReachStream.")
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
    search_query = models.ForeignKey(SearchQuery, on_delete=models.CASCADE, related_name="results")
    full_name = models.CharField(max_length=255, null=True, blank=True)
    job_title = models.CharField(max_length=255, null=True, blank=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True)
    raw_data = models.JSONField(help_text="The full, raw JSON response for this profile.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name or "Unnamed Profile"
```

## 3. Architecture & Core Logic

**File:** `people_search/services.py`

*   **`initiate_reachstream_search(query_filter: dict)` function:**
    *   Creates a `SearchQuery` record in the database with `PENDING` status.
    *   Uses the `ip_rotator.services.get_rotated_session()` to get a proxied `requests.Session`.
    *   Makes a `POST` request to ReachStream's `/api/v2/async/records/filter/data` endpoint.
    *   If successful, it updates the `SearchQuery` record with the `reachstream_batch_id` and sets the status to `PROCESSING`.
    *   If it fails, it updates the status to `FAILED` and records the error.
    *   This function will likely be called from the API ViewSet.

*   **`poll_reachstream_results()` background task:**
    *   This function is designed to be run periodically (e.g., by a Celery task or a Django management command run by cron).
    *   It finds all `SearchQuery` records with `PROCESSING` status.
    *   For each query, it uses a rotated session to poll ReachStream's `/api/v2/records/batch-process` endpoint.
    *   If the data is ready, it fetches the results.
    *   It calls `_process_and_store_results()` to save the data.
    *   It updates the `SearchQuery` status to `COMPLETED`.
    *   If polling results in an error (e.g., "still processing"), it does nothing and waits for the next run.

*   **`_process_and_store_results(search_query, results_data)` private function:**
    *   Iterates through the list of person records from the ReachStream response.
    *   For each record, it creates a `PersonProfile` instance, mapping the relevant fields and storing the full record in the `raw_data` JSONField.
    *   Uses `bulk_create` for efficient database insertion.

## 4. API Endpoints

**File:** `people_search/views.py`, `people_search/serializers.py`, `people_search/urls.py`

*   **`POST /api/v1/people-search/`**
    *   **Action:** Initiates a new people search.
    *   **Request Body:** A JSON object matching the ReachStream `filter` parameter.
    *   **Response:** A serialized `SearchQuery` object with its ID and `PENDING` status. The user can use this ID to check the status of their search.
*   **`GET /api/v1/people-search/<uuid:query_id>/`**
    *   **Action:** Checks the status of a search.
    *   **Response:** The `SearchQuery` object, including its current status.
*   **`GET /api/v1/people-search/<uuid:query_id>/results/`**
    *   **Action:** Retrieves the results for a completed search.
    *   **Response:** A paginated list of `PersonProfile` objects associated with the `SearchQuery`.

## 5. Configuration

*   `REACHSTREAM_API_KEY`: Will need to be added to the `.env` file and loaded in `settings.py`.
*   `REACHSTREAM_BASE_URL`: `https://api-prd.reachstream.com` will be stored as a constant in `people_search/services.py`.
