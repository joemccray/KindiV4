# Technical Plan: Kindi-BE3 SerpAPI Integration

## 1. Overview

The `serpapi_integration` app will provide a centralized service for querying various Google search endpoints via the SerpAPI service. This app will encapsulate the usage of the `google-search-results` Python library and provide a clean, unified API for other Kindi services.

## 2. Database Schema

A generic model is needed to log all search queries and store their results.

**File:** `serpapi_integration/models.py`

```python
import uuid
from django.db import models

class SerpApiSearch(models.Model):
    """
    Represents a single search query made to any SerpAPI endpoint.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    engine = models.CharField(max_length=100, help_text="The SerpAPI engine used, e.g., 'google_news', 'google_scholar'.")
    search_parameters = models.JSONField(help_text="The parameters sent to the SerpAPI.")
    raw_response = models.JSONField(help_text="The full JSON response from the SerpAPI.")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.engine} search - {self.created_at.isoformat()}"
```

## 3. Architecture & Core Logic

**File:** `serpapi_integration/services.py`

*   The service layer will consist of separate functions for each of the 8 required Google search types. Each function will take the necessary search parameters as arguments.
*   **Example function:** `search_google_news(query: str, location: str = None)`
    *   It will construct the `params` dictionary required by the `google-search-results` library, including the `q`, `tbm: 'nws'`, and the API key.
    *   It will instantiate the `GoogleSearch` class and call `get_dict()` to get the results.
    *   It will handle any exceptions from the library.
    *   It will create a `SerpApiSearch` record to log the request and store the full JSON response.
    *   It will return the parsed dictionary response.
*   Similar functions will be created for `google_scholar`, `google_trends`, `google_maps`, `google_events`, `google_finance`, `youtube`, and `google_ai_overview`.

## 4. API Endpoints

The API will expose a separate `POST` endpoint for each search type for clarity.

**File:** `serpapi_integration/views.py`, `serpapi_integration/serializers.py`, `serpapi_integration/urls.py`

*   **`POST /api/v1/serpapi/news-search/`**
    *   **Action:** Triggers a Google News search.
    *   **Request Body:** `{"query": "cybersecurity trends"}`
    *   **Response:** The raw JSON search results from SerpAPI.
*   ...and similar endpoints for the other 7 search types.

## 5. Configuration

*   `SERPAPI_API_KEY`: Will need to be acquired and added to the `.env` file. The service will load this from the environment.
