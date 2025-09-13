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


class PeopleSearchServiceTest(TestCase):
    @patch("people_search.services.get_rotated_session")
    @patch.dict(os.environ, {"REACHSTREAM_API_KEY": "test-key"})
    def test_initiate_search_success(self, mock_get_session):
        # Mock the rotator service to return a dummy session
        mock_get_session.return_value = MagicMock()

        query_filter = {"company_name": {"0": "Kindi"}}
        search_query = services.initiate_reachstream_search(query_filter)

        self.assertIsNotNone(search_query)
        self.assertEqual(search_query.status, SearchQuery.SearchStatus.PROCESSING)
        self.assertIsNotNone(search_query.reachstream_batch_id)
        self.assertIsNone(search_query.error_message)
        mock_get_session.assert_called_once_with(services.REACHSTREAM_BASE_URL)

    @patch("people_search.services.get_rotated_session")
    @patch.dict(os.environ, {"REACHSTREAM_API_KEY": "test-key"})
    def test_initiate_search_failure(self, mock_get_session):
        # Simulate an exception during the API call
        mock_get_session.side_effect = Exception("Connection Timeout")

        query_filter = {"company_name": {"0": "Kindi"}}
        search_query = services.initiate_reachstream_search(query_filter)

        self.assertEqual(search_query.status, SearchQuery.SearchStatus.FAILED)
        self.assertIsNotNone(search_query.error_message)
        self.assertIn("Connection Timeout", search_query.error_message)


class PeopleSearchApiTest(APITestCase):
    def setUp(self):
        # We need to patch the service layer to avoid real API calls
        self.mock_initiate_search = patch(
            "people_search.views.services.initiate_reachstream_search"
        ).start()
        self.addCleanup(self.mock_initiate_search.stop)

    def test_create_search(self):
        """
        Test the POST /api/v1/people-search/ endpoint.
        """
        # Configure the mock to return a predictable SearchQuery object
        test_uuid = uuid.uuid4()
        mock_query = SearchQuery(
            id=test_uuid,
            status=SearchQuery.SearchStatus.PROCESSING,
            query_filter={"company_name": {"0": "kindi"}},
        )
        self.mock_initiate_search.return_value = mock_query

        url = reverse("peoplesearch-list")
        data = {"filter": {"company_name": {"0": "kindi"}}}

        response = self.client.post(url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.mock_initiate_search.assert_called_once_with(data["filter"])
        self.assertEqual(response.data["id"], str(test_uuid))
        self.assertEqual(response.data["status"], SearchQuery.SearchStatus.PROCESSING)

    def test_retrieve_search_status(self):
        """
        Test the GET /api/v1/people-search/{id}/ endpoint.
        """
        query = SearchQuery.objects.create(
            query_filter={}, status=SearchQuery.SearchStatus.COMPLETED
        )
        url = reverse("peoplesearch-detail", kwargs={"id": query.id})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(query.id))
        self.assertEqual(response.data["status"], SearchQuery.SearchStatus.COMPLETED)

    def test_get_results_for_completed_search(self):
        """
        Test the GET /api/v1/people-search/{id}/results/ endpoint for a complete search.
        """
        query = SearchQuery.objects.create(
            query_filter={}, status=SearchQuery.SearchStatus.COMPLETED
        )
        PersonProfile.objects.create(
            search_query=query, full_name="Jane Doe", raw_data={}
        )
        PersonProfile.objects.create(
            search_query=query, full_name="John Smith", raw_data={}
        )

        url = reverse("peoplesearch-results", kwargs={"id": query.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["full_name"], "Jane Doe")

    def test_get_results_for_pending_search(self):
        """
        Test the GET /api/v1/people-search/{id}/results/ endpoint for a pending search.
        """
        query = SearchQuery.objects.create(
            query_filter={}, status=SearchQuery.SearchStatus.PENDING
        )
        url = reverse("peoplesearch-results", kwargs={"id": query.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
