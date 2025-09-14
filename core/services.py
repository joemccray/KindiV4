"""
Core business logic for the Kindi-Lite application.

This service layer encapsulates complex operations, especially those that
involve multiple models or complex algorithms, keeping the views thin
and focused on handling HTTP requests and responses.
"""

from django.db.models import Q

from .models import Entity, Event, Location
from .serializers import EntitySerializer


def calculate_relationship_strength(entity1: Entity, entity2: Entity) -> dict:
    """
    Calculates the relationship strength between two entities based on shared
    events and locations.
    """
    shared_events = Event.objects.filter(entities=entity1).filter(entities=entity2)
    shared_locations = Location.objects.filter(associated_entities=entity1).filter(
        associated_entities=entity2
    )

    strength = shared_events.count() + shared_locations.count()

    return {
        "strength": strength,
        "connections": {
            "sharedEvents": [
                {"id": str(e.id), "title": e.title} for e in shared_events
            ],
            "sharedLocations": [
                {"id": str(loc.id), "name": loc.name} for loc in shared_locations
            ],
        },
    }


def _get_entity_neighbors(entity: Entity) -> list[Entity]:
    """Helper to find all entities connected to the given entity."""
    events = entity.events.all()
    locations = entity.locations.all()
    neighbor_q = Q(events__in=events) | Q(locations__in=locations)
    neighbors = Entity.objects.filter(neighbor_q).distinct().exclude(pk=entity.pk)
    return neighbors


def find_shortest_path(
    source_entity: Entity, target_entity: Entity, max_depth: int = 3
) -> dict:
    """
    Finds the shortest path between two entities using Breadth-First Search.
    """
    queue = [
        (source_entity, [source_entity])
    ]  # Queue stores (current_node, path_to_node)
    visited = {source_entity.pk}

    while queue:
        current_node, path = queue.pop(0)

        if current_node == target_entity:
            # Path found, now format it for the response
            formatted_path = []
            for i in range(len(path) - 1):
                # For each step in the path, find the connection
                shared_events = Event.objects.filter(entities=path[i]).filter(
                    entities=path[i + 1]
                )
                shared_locs = Location.objects.filter(
                    associated_entities=path[i]
                ).filter(associated_entities=path[i + 1])

                connection = None
                if shared_events.exists():
                    event = shared_events.first()
                    connection = {
                        "type": "event",
                        "id": str(event.id),
                        "name": event.title,
                    }
                elif shared_locs.exists():
                    loc = shared_locs.first()
                    connection = {
                        "type": "location",
                        "id": str(loc.id),
                        "name": loc.name,
                    }

                formatted_path.append(
                    {"entity": EntitySerializer(path[i]).data, "connection": connection}
                )
            # Add the final entity in the path
            formatted_path.append(
                {"entity": EntitySerializer(path[-1]).data, "connection": None}
            )

            return {"path": formatted_path, "pathLength": len(path) - 1}

        if len(path) > max_depth:
            continue

        for neighbor in _get_entity_neighbors(current_node):
            if neighbor.pk not in visited:
                visited.add(neighbor.pk)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append((neighbor, new_path))

    return {"path": [], "pathLength": 0}


def build_relationship_network(
    root_entities: list[Entity], depth: int, min_strength: int
) -> dict:
    """
    Builds a node-link graph of entities and their relationships.
    """
    if not root_entities:
        return {"nodes": [], "links": []}

    nodes = set()
    links = set()
    queue = [(entity, 0) for entity in root_entities]  # (entity, current_depth)
    visited = {entity.pk for entity in root_entities}

    while queue:
        current_entity, current_depth = queue.pop(0)
        nodes.add(current_entity)

        if current_depth >= depth:
            continue

        neighbors = _get_entity_neighbors(current_entity)

        for neighbor in neighbors:
            strength_data = calculate_relationship_strength(current_entity, neighbor)
            strength = strength_data["strength"]

            if strength >= min_strength:
                # Add link (use a tuple of sorted IDs to ensure uniqueness)
                link_tuple = tuple(sorted((str(current_entity.pk), str(neighbor.pk))))
                links.add((link_tuple[0], link_tuple[1], strength))

            if neighbor.pk not in visited:
                visited.add(neighbor.pk)
                queue.append((neighbor, current_depth + 1))

    # Format for response
    formatted_nodes = [
        {"id": str(n.id), "name": n.name, "type": n.type, "group": 1} for n in nodes
    ]
    formatted_links = [
        {"source": link[0], "target": link[1], "value": link[2]} for link in links
    ]

    return {"nodes": formatted_nodes, "links": formatted_links}
