import datetime

from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Activity, Entity, Event, Location, Workspace


class SearchAPITests(APITestCase):
    """
    Tests for the various search API endpoints.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)
        self.entity1 = Entity.objects.create(name="Project Chimera", type="asset")
        self.entity2 = Entity.objects.create(
            name="John Smith", type="person", attributes={"notes": "Related to Chimera"}
        )
        self.event1 = Event.objects.create(
            title="Chimera Launch", timestamp=timezone.now()
        )
        self.location1 = Location.objects.create(
            name="Site Chimera", latitude=1.0, longitude=1.0
        )
        self.search_url = reverse("global-search")

    def test_global_search_requires_query(self):
        """
        Ensure the global search endpoint returns an error if no query is provided.
        """
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_global_search_finds_all_types(self):
        """
        Ensure the global search returns results from all models by default.
        """
        response = self.client.get(self.search_url, {"query": "Chimera"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["entities"]), 2)
        self.assertEqual(len(response.data["events"]), 1)
        self.assertEqual(len(response.data["locations"]), 1)
        self.assertEqual(response.data["totalResults"], 4)

    def test_global_search_filters_by_type(self):
        """
        Ensure the global search can be limited to specific types.
        """
        response = self.client.get(
            self.search_url, {"query": "Chimera", "types": "events,locations"}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("entities", response.data)
        self.assertEqual(len(response.data["events"]), 1)
        self.assertEqual(len(response.data["locations"]), 1)
        self.assertEqual(response.data["totalResults"], 2)

    def test_global_search_no_results(self):
        """
        Ensure the global search returns empty lists for a query with no matches.
        """
        response = self.client.get(self.search_url, {"query": "nonexistent"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["entities"]), 0)
        self.assertEqual(len(response.data["events"]), 0)
        self.assertEqual(len(response.data["locations"]), 0)
        self.assertEqual(response.data["totalResults"], 0)

    def test_advanced_search_entity_type_filter(self):
        """
        Ensure advanced search can filter entities by type.
        """
        url = reverse("advanced-search")
        response = self.client.get(url, {"query": "Smith", "entityTypes": "person"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["entities"]), 1)
        self.assertEqual(response.data["entities"][0]["name"], "John Smith")

        response = self.client.get(url, {"query": "Smith", "entityTypes": "asset"})
        self.assertEqual(len(response.data["entities"]), 0)

    def test_advanced_search_exact_and_case_sensitive(self):
        """
        Ensure advanced search can perform exact and case-sensitive searches.
        Note: Case-sensitive 'contains' is not reliably supported on SQLite.
        This test focuses on the 'exact' lookup.
        """
        url = reverse("advanced-search")
        # Test exactMatch=true (case-insensitive by default)
        response = self.client.get(url, {"query": "john smith", "exactMatch": "true"})
        self.assertEqual(len(response.data["entities"]), 1)
        response = self.client.get(url, {"query": "John", "exactMatch": "true"})
        self.assertEqual(len(response.data["entities"]), 0)

        # Test caseSensitive=true with exactMatch=true
        response = self.client.get(
            url, {"query": "john smith", "exactMatch": "true", "caseSensitive": "true"}
        )
        self.assertEqual(len(response.data["entities"]), 0)
        response = self.client.get(
            url, {"query": "John Smith", "exactMatch": "true", "caseSensitive": "true"}
        )
        self.assertEqual(len(response.data["entities"]), 1)

    def test_advanced_search_date_filter(self):
        """
        Ensure advanced search can filter events by date.
        """
        url = reverse("advanced-search")
        yesterday = (timezone.now() - datetime.timedelta(days=1)).isoformat()

        Event.objects.create(
            title="Old Event", timestamp=timezone.now() - datetime.timedelta(days=5)
        )

        response = self.client.get(url, {"query": "Event", "startDate": yesterday})
        self.assertEqual(
            len(response.data["events"]), 0
        )  # The main "Chimera Launch" is not found by "Event"

        response = self.client.get(url, {"query": "Launch", "startDate": yesterday})
        self.assertEqual(len(response.data["events"]), 1)

        response = self.client.get(url, {"query": "Launch", "endDate": yesterday})
        self.assertEqual(len(response.data["events"]), 0)

    def test_search_suggestions(self):
        """
        Ensure the suggestions endpoint returns a list of relevant strings.
        """
        url = reverse("search-suggestions")
        # Create more data for suggestions
        Entity.objects.create(name="Project Griffin", type="asset")
        Event.objects.create(title="Griffin Test Flight", timestamp=timezone.now())

        response = self.client.get(url, {"query": "Griffin"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("suggestions", response.data)
        self.assertEqual(len(response.data["suggestions"]), 2)
        self.assertIn("Project Griffin", response.data["suggestions"])
        self.assertIn("Griffin Test Flight", response.data["suggestions"])

    def test_search_suggestions_limit(self):
        """
        Ensure the maxSuggestions parameter is respected.
        """
        url = reverse("search-suggestions")
        response = self.client.get(url, {"query": "Project", "maxSuggestions": 1})
        self.assertEqual(len(response.data["suggestions"]), 1)


class RelationshipAnalysisAPITests(APITestCase):
    """
    Tests for the relationship analysis API endpoints.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)
        # Create a network of entities
        self.e1 = Entity.objects.create(name="E1", type="person")
        self.e2 = Entity.objects.create(name="E2", type="person")
        self.e3 = Entity.objects.create(name="E3", type="organization")

        # Create shared connections
        self.loc1 = Location.objects.create(name="L1", latitude=1, longitude=1)
        self.loc1.associated_entities.add(self.e1, self.e2)

        self.event1 = Event.objects.create(title="Ev1", timestamp=timezone.now())
        self.event1.entities.add(self.e1, self.e2)

        self.event2 = Event.objects.create(title="Ev2", timestamp=timezone.now())
        self.event2.entities.add(self.e1, self.e3)

        self.strength_url = reverse("relationship-strength")

    def test_strength_requires_params(self):
        """
        Ensure the strength endpoint returns an error if params are missing.
        """
        response = self.client.get(self.strength_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        response = self.client.get(self.strength_url, {"entity1": self.e1.pk})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_strength_calculation(self):
        """
        Ensure the strength calculation is correct.
        """
        # E1 and E2 share one event and one location
        response = self.client.get(
            self.strength_url, {"entity1": self.e1.pk, "entity2": self.e2.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["strength"], 2)
        self.assertEqual(len(response.data["connections"]["sharedEvents"]), 1)
        self.assertEqual(
            response.data["connections"]["sharedEvents"][0]["title"], "Ev1"
        )
        self.assertEqual(len(response.data["connections"]["sharedLocations"]), 1)

        # E2 and E3 share nothing
        response = self.client.get(
            self.strength_url, {"entity1": self.e2.pk, "entity2": self.e3.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["strength"], 0)

    def test_path_finding(self):
        """
        Ensure the path finding endpoint returns the shortest path.
        """
        # E2 -> E1 -> E3
        # E2 is connected to E1 via loc1/event1
        # E1 is connected to E3 via event2
        path_url = reverse("relationship-path")

        # Test path from E2 to E3
        response = self.client.get(
            path_url, {"sourceId": self.e2.pk, "targetId": self.e3.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["pathLength"], 2)
        self.assertEqual(len(response.data["path"]), 3)  # Path includes 3 entities
        self.assertEqual(response.data["path"][0]["entity"]["name"], "E2")
        self.assertEqual(response.data["path"][1]["entity"]["name"], "E1")
        self.assertEqual(response.data["path"][2]["entity"]["name"], "E3")
        # Check that the connection is correctly identified
        self.assertEqual(response.data["path"][1]["connection"]["name"], "Ev2")

    def test_path_not_found(self):
        """
        Ensure the endpoint handles cases where no path exists.
        """
        e4 = Entity.objects.create(name="E4", type="asset")  # Unconnected
        path_url = reverse("relationship-path")
        response = self.client.get(
            path_url, {"sourceId": self.e1.pk, "targetId": e4.pk}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["pathLength"], 0)
        self.assertEqual(len(response.data["path"]), 0)

    def test_network_graph(self):
        """
        Ensure the network endpoint returns a correct graph structure.
        """
        network_url = reverse("relationship-network")
        response = self.client.get(network_url, {"entityIds": str(self.e2.pk)})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # With depth=1, starting from E2, we should find E1.
        self.assertEqual(len(response.data["nodes"]), 2)
        self.assertEqual(len(response.data["links"]), 1)
        self.assertEqual(
            response.data["links"][0]["value"], 2
        )  # E1 and E2 share 2 items

    def test_network_graph_depth(self):
        """
        Ensure the depth parameter is respected.
        """
        network_url = reverse("relationship-network")
        # With depth=2, starting from E2, we should find E1 and then E3.
        response = self.client.get(
            network_url, {"entityIds": str(self.e2.pk), "depth": 2}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["nodes"]), 3)
        self.assertEqual(len(response.data["links"]), 2)

    def test_strength_service_function(self):
        """
        Directly test the calculate_relationship_strength service function.
        """
        from . import services

        result = services.calculate_relationship_strength(self.e1, self.e2)
        self.assertEqual(result["strength"], 2)
        self.assertEqual(len(result["connections"]["sharedEvents"]), 1)

    def test_path_service_function(self):
        """
        Directly test the find_shortest_path service function.
        """
        from . import services

        result = services.find_shortest_path(self.e2, self.e3)
        self.assertEqual(result["pathLength"], 2)
        self.assertEqual(len(result["path"]), 3)


class ImportExportAPITests(APITestCase):
    """
    Tests for the import/export API endpoints.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)
        self.workspace = Workspace.objects.create(name="Export Case")
        self.entity = Entity.objects.create(name="E1", type="person")
        self.event = Event.objects.create(title="Ev1", timestamp=timezone.now())
        self.workspace.entities.add(self.entity)
        self.workspace.events.add(self.event)

    def test_export_workspace(self):
        """
        Ensure the export endpoint returns a correctly formatted JSON file.
        """
        url = reverse("workspace-export", kwargs={"id": self.workspace.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertIn("attachment; filename=", response["Content-Disposition"])

        # Check the content of the exported data
        json_data = response.json()
        self.assertEqual(json_data["workspace"]["name"], "Export Case")
        self.assertEqual(len(json_data["related_data"]["entities"]), 1)
        self.assertEqual(json_data["related_data"]["entities"][0]["name"], "E1")
        self.assertEqual(len(json_data["related_data"]["events"]), 1)

    def test_import_workspace(self):
        """
        Ensure a workspace can be imported from a valid JSON file.
        """
        # First, export a workspace to get a valid file format
        export_url = reverse("workspace-export", kwargs={"id": self.workspace.pk})
        export_response = self.client.get(export_url)
        json_content = export_response.content

        # Now, import it
        import_url = reverse("workspace-import")
        from django.core.files.uploadedfile import SimpleUploadedFile

        upload_file = SimpleUploadedFile(
            "import.json", json_content, content_type="application/json"
        )

        # We need to use a different client for file uploads
        from rest_framework.test import APIClient

        client = APIClient()
        client.force_authenticate(user=self.user)
        response = client.post(import_url, {"file": upload_file}, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workspace.objects.count(), 2)  # Original + imported

        # Verify the imported workspace
        new_workspace = Workspace.objects.get(pk=response.data["workspace"]["id"])
        self.assertEqual(new_workspace.name, self.workspace.name)
        self.assertEqual(new_workspace.entities.count(), 1)
        self.assertEqual(new_workspace.events.count(), 1)
        self.assertEqual(new_workspace.entities.first().name, self.entity.name)


class WorkspaceAPITests(APITestCase):
    """
    Comprehensive tests for the Workspace API endpoint.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)
        self.entity = Entity.objects.create(name="E1", type="person")
        self.location = Location.objects.create(name="L1", latitude=1, longitude=1)
        self.event = Event.objects.create(title="Ev1", timestamp=timezone.now())
        self.workspace1 = Workspace.objects.create(name="Case Alpha", priority="high")
        self.workspace1.entities.add(self.entity)
        self.list_url = reverse("workspace-list")

    def test_create_workspace(self):
        """
        Ensure we can create a new workspace and an activity is logged.
        """
        data = {
            "name": "Case Bravo",
            "description": "A new case.",
            "status": "active",
            "priority": "critical",
            "entities": [self.entity.pk],
            "locations": [self.location.pk],
            "events": [self.event.pk],
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Workspace.objects.count(), 2)
        new_workspace = Workspace.objects.get(name="Case Bravo")
        self.assertEqual(new_workspace.priority, "critical")
        self.assertIn(self.entity, new_workspace.entities.all())

        # Test that the creation activity was logged
        self.assertEqual(Activity.objects.count(), 1)
        activity = Activity.objects.first()
        self.assertEqual(activity.workspace, new_workspace)
        self.assertEqual(activity.type, Activity.ActivityType.WORKSPACE_CREATED)

    def test_list_workspaces_summary(self):
        """
        Ensure the list view returns a summary with counts.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(response.data["results"]), 1)

        summary_data = response.data["results"][0]
        self.assertEqual(summary_data["name"], "Case Alpha")
        self.assertIn("entityCount", summary_data)
        self.assertEqual(summary_data["entityCount"], 1)
        self.assertEqual(summary_data["eventCount"], 0)
        self.assertEqual(summary_data["locationCount"], 0)
        self.assertNotIn(
            "analysis_state", summary_data
        )  # Ensure detail fields are excluded

    def test_retrieve_workspace_detail(self):
        """
        Ensure the retrieve view returns full details, not a summary.
        """
        detail_url = reverse("workspace-detail", kwargs={"pk": self.workspace1.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        detail_data = response.data
        self.assertEqual(detail_data["name"], "Case Alpha")
        self.assertIn("analysis_state", detail_data)  # Detail field should be present
        self.assertIn(self.entity.pk, detail_data["entities"])
        self.assertNotIn("entityCount", detail_data)  # Summary field should be excluded

    def test_delete_workspace(self):
        """
        Ensure we can delete a workspace. Deleting should cascade to activities.
        """
        Activity.objects.create(
            workspace=self.workspace1, type="note_added", description="test"
        )
        self.assertEqual(Activity.objects.count(), 1)

        detail_url = reverse("workspace-detail", kwargs={"pk": self.workspace1.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Workspace deleted successfully")
        self.assertEqual(Workspace.objects.count(), 0)
        self.assertEqual(Activity.objects.count(), 0)  # Should be cascade deleted


class EventAPITests(APITestCase):
    """
    Comprehensive tests for the Event API endpoint.
    """

    def setUp(self):
        """
        Set up initial data for tests.
        """
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)
        self.entity = Entity.objects.create(name="Test Entity", type="person")
        self.location = Location.objects.create(
            name="Test Location", latitude=1.0, longitude=1.0
        )
        self.event1 = Event.objects.create(
            title="Initial Meeting",
            timestamp=timezone.now() - datetime.timedelta(days=1),
            location=self.location,
        )
        self.event2 = Event.objects.create(
            title="Follow-up Call", timestamp=timezone.now()
        )
        self.event1.entities.add(self.entity)
        self.list_url = reverse("event-list")

    def test_create_event(self):
        """
        Ensure we can create a new event object.
        """
        data = {
            "title": "New Surveillance Op",
            "timestamp": timezone.now().isoformat(),
            "location": self.location.pk,
            "entities": [self.entity.pk],
            "severity": "high",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Event.objects.count(), 3)
        new_event = Event.objects.get(title="New Surveillance Op")
        self.assertEqual(new_event.severity, "high")
        self.assertIn(self.entity, new_event.entities.all())

    def test_list_events(self):
        """
        Ensure we can list all event objects.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)
        # Events are ordered by -timestamp
        self.assertEqual(response.data["results"][0]["title"], "Follow-up Call")
        self.assertEqual(response.data["results"][1]["title"], "Initial Meeting")

    def test_retrieve_event(self):
        """
        Ensure we can retrieve a single event object.
        """
        detail_url = reverse("event-detail", kwargs={"pk": self.event1.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], self.event1.title)
        self.assertEqual(response.data["location"], self.location.pk)
        self.assertIn(self.entity.pk, response.data["entities"])

    def test_update_event(self):
        """
        Ensure we can update an existing event object.
        """
        detail_url = reverse("event-detail", kwargs={"pk": self.event1.pk})
        updated_data = {
            "title": "Secret Meeting",
            "timestamp": self.event1.timestamp.isoformat(),
            "description": "Updated description.",
        }
        response = self.client.put(detail_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.event1.refresh_from_db()
        self.assertEqual(self.event1.title, "Secret Meeting")
        self.assertEqual(self.event1.description, "Updated description.")

    def test_delete_event(self):
        """
        Ensure we can delete an event object.
        """
        detail_url = reverse("event-detail", kwargs={"pk": self.event2.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Event deleted successfully")
        self.assertEqual(Event.objects.count(), 1)


class LocationAPITests(APITestCase):
    """
    Comprehensive tests for the Location API endpoint.
    """

    def setUp(self):
        """
        Set up initial data for tests.
        """
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)
        self.location1 = Location.objects.create(
            name="Safe House Alpha",
            latitude=40.7128,
            longitude=-74.0060,
            marker_type=Location.MarkerType.PRIMARY,
        )
        self.location2 = Location.objects.create(
            name="Abandoned Warehouse",
            latitude=34.0522,
            longitude=-118.2437,
            marker_type=Location.MarkerType.THREAT,
        )
        self.list_url = reverse("location-list")

    def test_create_location(self):
        """
        Ensure we can create a new location object.
        """
        data = {
            "name": "Rooftop Vantage Point",
            "latitude": "40.7129",
            "longitude": "-74.0061",
            "markerType": "asset",
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Location.objects.count(), 3)
        self.assertEqual(
            Location.objects.get(name="Rooftop Vantage Point").marker_type, "asset"
        )

    def test_list_locations(self):
        """
        Ensure we can list all location objects.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["name"], "Abandoned Warehouse")
        self.assertEqual(response.data["results"][1]["name"], "Safe House Alpha")

    def test_retrieve_location(self):
        """
        Ensure we can retrieve a single location object.
        """
        detail_url = reverse("location-detail", kwargs={"pk": self.location1.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.location1.name)
        self.assertEqual(response.data["markerType"], "primary")

    def test_update_location(self):
        """
        Ensure we can update an existing location object using PUT.
        """
        detail_url = reverse("location-detail", kwargs={"pk": self.location1.pk})
        updated_data = {
            "name": "Compromised Safe House",
            "latitude": "40.7128",
            "longitude": "-74.0060",
            "markerType": "threat",
        }
        response = self.client.put(detail_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.location1.refresh_from_db()
        self.assertEqual(self.location1.name, "Compromised Safe House")
        self.assertEqual(self.location1.marker_type, "threat")

    def test_delete_location(self):
        """
        Ensure we can delete a location object.
        """
        detail_url = reverse("location-detail", kwargs={"pk": self.location2.pk})
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Location deleted successfully")
        self.assertEqual(Location.objects.count(), 1)


class EntityAPITests(APITestCase):
    """
    Comprehensive tests for the Entity API endpoint.
    """

    def setUp(self):
        """
        Set up initial data for tests.
        """
        self.user = User.objects.create_user(username="testuser")
        self.client.force_authenticate(user=self.user)
        self.entity1 = Entity.objects.create(
            name="John Doe",
            type=Entity.EntityType.PERSON,
            attributes={"email": "john.doe@example.com"},
            coordinates={"x": 10, "y": 20},
        )
        self.entity2 = Entity.objects.create(
            name="Acme Corp",
            type=Entity.EntityType.ORGANIZATION,
            attributes={"industry": "Manufacturing"},
        )
        self.list_url = reverse("entity-list")

    def test_create_entity(self):
        """
        Ensure we can create a new entity object.
        """
        data = {
            "name": "New Asset",
            "type": "asset",
            "attributes": {"status": "active"},
            "coordinates": {"x": 150, "y": 250},
        }
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Entity.objects.count(), 3)
        self.assertEqual(Entity.objects.get(name="New Asset").type, "asset")

    def test_list_entities(self):
        """
        Ensure we can list all entity objects.
        """
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        self.assertEqual(len(response.data["results"]), 2)
        # Names should be in reverse order of creation due to model ordering
        self.assertEqual(response.data["results"][0]["name"], "Acme Corp")
        self.assertEqual(response.data["results"][1]["name"], "John Doe")

    def test_retrieve_entity(self):
        """
        Ensure we can retrieve a single entity object.
        """
        detail_url = reverse("entity-detail", kwargs={"pk": self.entity1.pk})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], self.entity1.name)
        self.assertEqual(response.data["attributes"]["email"], "john.doe@example.com")

    def test_update_entity(self):
        """
        Ensure we can update an existing entity object using PUT.
        """
        detail_url = reverse("entity-detail", kwargs={"pk": self.entity1.pk})
        updated_data = {
            "name": "Johnathan Doe",
            "type": "person",  # Type must be provided for PUT
            "attributes": {"email": "j.doe@new-example.com", "verified": True},
            "coordinates": {"x": 15, "y": 25},
        }
        response = self.client.put(detail_url, updated_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.entity1.refresh_from_db()
        self.assertEqual(self.entity1.name, "Johnathan Doe")
        self.assertTrue(self.entity1.attributes["verified"])

    def test_partial_update_entity(self):
        """
        Ensure we can partially update an existing entity object using PATCH.
        """
        detail_url = reverse("entity-detail", kwargs={"pk": self.entity1.pk})
        patch_data = {"name": "Johnny Doe"}
        response = self.client.patch(detail_url, patch_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.entity1.refresh_from_db()
        self.assertEqual(self.entity1.name, "Johnny Doe")

    def test_delete_entity(self):
        """
        Ensure we can delete an entity object.
        """
        detail_url = reverse("entity-detail", kwargs={"pk": self.entity2.pk})
        response = self.client.delete(detail_url)
        # Custom destroy returns 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Entity deleted successfully")
        self.assertEqual(Entity.objects.count(), 1)
        self.assertFalse(Entity.objects.filter(pk=self.entity2.pk).exists())

    def test_entity_type_choices(self):
        """
        Ensure invalid entity types are rejected.
        """
        data = {"name": "Invalid Entity", "type": "invalid_type"}
        response = self.client.post(self.list_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)
        self.assertIn(
            '"invalid_type" is not a valid choice.', str(response.data["type"])
        )
