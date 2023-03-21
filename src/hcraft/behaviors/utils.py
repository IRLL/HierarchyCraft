""" Module for utility functions to apply on handcrafted Behavior. """

from typing import Dict, Set, Union

from hebg import Behavior, HEBGraph

from hcraft.behaviors.behaviors import (
    AbleAndPerformTransformation,
    GetItem,
    ReachZone,
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
        if isinstance(node, GetItem) and isinstance(node.item, Item):
            items_in_graph.add(node.item)
        if isinstance(node, AbleAndPerformTransformation):
            added_player_items = node.transformation.get_changes("player", "add")
            if added_player_items is not None:
                items_in_graph |= {stack.item for stack in added_player_items}
            removed_player_items = node.transformation.get_changes("player", "remove")
            if removed_player_items is not None:
                items_in_graph |= {stack.item for stack in removed_player_items}
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
        if isinstance(node, GetItem) and isinstance(node.item, str):
            zone_items_in_graph.add(node.item)

        if (
            isinstance(node, AbleAndPerformTransformation)
            and node.transformation.get_changes("current_zone", "add") is not None
        ):
            added_zone_items = node.transformation.get_changes("current_zone", "add")
            if added_zone_items is not None:
                zone_items_in_graph |= {stack.item for stack in added_zone_items}
            removed_zone_items = node.transformation.get_changes(
                "current_zone", "remove"
            )
            if removed_zone_items is not None:
                zone_items_in_graph |= {stack.item for stack in removed_zone_items}
    return zone_items_in_graph
