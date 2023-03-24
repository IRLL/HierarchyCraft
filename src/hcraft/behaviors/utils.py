""" Module for utility functions to apply on handcrafted Behavior. """

from typing import Dict, Set, Union

from hebg import Behavior, HEBGraph

from hcraft.behaviors.behaviors import (
    AbleAndPerformTransformation,
    GetItem,
    ReachZone,
    PlaceItem,
)
from hcraft.elements import Item


def get_items_in_graph(
    graph: HEBGraph,
    all_behaviors: Dict[str, Union[GetItem, ReachZone]] = None,
) -> Set[Item]:
    """Get items in a HierarchyCraft HEBGraph.

    Args:
        graph (HEBGraph): An  of the HierarchyCraft environment.

    Returns:
        Set[Item]: Set of items that appears in the given graph.
    """
    all_behaviors = all_behaviors if all_behaviors is not None else {}
    items_in_graph = set()
    for node in graph.nodes():
        if isinstance(node, Behavior) and node in all_behaviors:
            node = all_behaviors[node]
        if isinstance(node, GetItem):
            items_in_graph.add(node.item)
        if isinstance(node, AbleAndPerformTransformation):
            items_in_graph |= node.transformation.production("player")
            items_in_graph |= node.transformation.consumption("player")
            items_in_graph |= node.transformation.min_required("player")
            items_in_graph |= node.transformation.max_required("player")
    return items_in_graph


def get_zones_items_in_graph(
    graph: HEBGraph,
    all_behaviors: Dict[str, Union[GetItem, ReachZone]] = None,
) -> Set[Item]:
    """Get properties in a HierarchyCraft HEBGraph.

    Args:
        graph (HEBGraph): An HEBehavior graph of the HierarchyCraft environment.
        all_behaviors (Dict[str, Union[GetItem, ReachZone]): References to all known behaviors.

    Returns:
        Set[Item]: Set of zone items that appears in the given graph.
    """
    all_behaviors = all_behaviors if all_behaviors is not None else {}
    zone_items_in_graph = set()
    for node in graph.nodes():
        if isinstance(node, Behavior) and node in all_behaviors:
            node = all_behaviors[node]
        if isinstance(node, PlaceItem):
            zone_items_in_graph.add(node.item)
        if isinstance(node, AbleAndPerformTransformation):
            zone_items_in_graph |= node.transformation.produced_zones_items
            zone_items_in_graph |= node.transformation.consumed_zones_items
            zone_items_in_graph |= node.transformation.min_required_zones_items
            zone_items_in_graph |= node.transformation.max_required_zones_items
    return zone_items_in_graph
