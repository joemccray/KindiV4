import os
import uuid
from unittest.mock import MagicMock, patch

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from . import services
from .models import PersonProfile, SearchQuery


class PeopleSearchModelsTest(TestCase):
    def test_create_search_query(self):
        query = SearchQuery.objects.create(query_filter={"company_name": {"0": "test"}})
        self.assertEqual(query.status, SearchQuery.SearchStatus.PENDING)
        self.assertEqual(SearchQuery.objects.count(), 1)

    def test_create_person_profile(self):
        query = SearchQuery.objects.create(query_filter={})
        profile = PersonProfile.objects.create(
            search_query=query, full_name="John Doe", raw_data={"key": "value"}
        )
        self.assertEqual(profile.search_query, query)
        self.assertEqual(str(profile), "John Doe")


@patch.dict(os.environ, {"REACHSTREAM_API_KEY": "test-key"})
class PeopleSearchServiceTest(TestCase):
    @patch("people_search.services.get_rotated_session")
    def test_initiate_search_success(self, mock_get_session):
        # Mock the requests.Session object that the rotator returns
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        # Mock the response from the session's post method
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 200,
            "data": {"unique_processing_id": "12345-abcde"},
        }
        mock_session.post.return_value = mock_response

        query_filter = {"company_name": {"0": "Kindi"}}
        search_query = services.initiate_reachstream_search(query_filter)

        self.assertEqual(search_query.status, SearchQuery.SearchStatus.PROCESSING)
        self.assertEqual(search_query.reachstream_batch_id, "12345-abcde")
        mock_session.post.assert_called_once()

    @patch("people_search.services.get_rotated_session")
    def test_poll_and_process_success(self, mock_get_session):
        # Setup: Create a query that is processing
        query = SearchQuery.objects.create(
            query_filter={},
            status=SearchQuery.SearchStatus.PROCESSING,
            reachstream_batch_id="12345-abcde",
        )

        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": 200,
            "data": [
                {"contact_name": "Jane Doe", "contact_email_1": "jane@example.com"},
                {"contact_name": "John Smith", "contact_email_1": "john@example.com"},
            ],
        }
        mock_session.get.return_value = mock_response

        services.poll_and_process_results()

        query.refresh_from_db()
        self.assertEqual(query.status, SearchQuery.SearchStatus.COMPLETED)
        self.assertEqual(query.results.count(), 2)
        self.assertEqual(PersonProfile.objects.count(), 2)
        names = set(PersonProfile.objects.values_list("full_name", flat=True))
        self.assertEqual(names, {"Jane Doe", "John Smith"})


class PeopleSearchApiTest(APITestCase):
    @patch("people_search.views.services.initiate_reachstream_search")
    def test_create_search_api(self, mock_initiate_search):
        test_uuid = uuid.uuid4()
        mock_query = SearchQuery(
            id=test_uuid,
            status=SearchQuery.SearchStatus.PROCESSING,
            query_filter={"company_name": {"0": "kindi"}},
        )
        mock_initiate_search.return_value = mock_query

        url = reverse("peoplesearch-list")
        data = {"filter": {"company_name": {"0": "kindi"}}}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertEqual(response.data["id"], str(test_uuid))
