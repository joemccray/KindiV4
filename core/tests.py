import datetime

from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Activity, Entity, Event, Location, Workspace


class WorkspaceAPITests(APITestCase):
    """
    Comprehensive tests for the Workspace API endpoint.
    """

    def setUp(self):
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
        self.assertEqual(len(response.data), 1)

        summary_data = response.data[0]
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
        self.assertEqual(len(response.data), 2)
        # Events are ordered by -timestamp
        self.assertEqual(response.data[0]["title"], "Follow-up Call")
        self.assertEqual(response.data[1]["title"], "Initial Meeting")

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
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["name"], "Abandoned Warehouse")
        self.assertEqual(response.data[1]["name"], "Safe House Alpha")

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
        self.assertEqual(len(response.data), 2)
        # Names should be in reverse order of creation due to model ordering
        self.assertEqual(response.data[0]["name"], "Acme Corp")
        self.assertEqual(response.data[1]["name"], "John Doe")

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
