# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for utility functions to apply on handcrafted Behavior. """

from typing import Dict, Set, Union

from hebg import HEBGraph, Behavior

from crafting.behaviors.actions import CraftRecipe, SearchItem
from crafting.behaviors.behaviors import GetItem, ReachZone
from crafting.world.items import Item


def get_items_in_graph(
    graph: HEBGraph,
    all_behaviors: Dict[str, Union[GetItem, ReachZone]] = None,
) -> Set[Item]:
    """Get items in a Crafting HEBGraph.

    Args:
        graph (HEBGraph): An  of the Crafting environment.

    Returns:
        Set[Item]: Set of items that appears in the given graph.
    """
    all_behaviors = all_behaviors if all_behaviors is not None else {}
    items_in_graph = set()
    for node in graph.nodes():
        if isinstance(node, Behavior) and node in all_behaviors:
            node = all_behaviors[node]
        if isinstance(node, (SearchItem, GetItem)) and isinstance(node.item, Item):
            items_in_graph.add(node.item)
        if isinstance(node, CraftRecipe) and node.recipe.outputs is not None:
            items_in_graph += {itemstack.item for itemstack in node.recipe.outputs}
    return items_in_graph


def get_properties_in_graph(
    graph: HEBGraph,
    all_behaviors: Dict[str, Union[GetItem, ReachZone]] = None,
) -> Set[str]:
    """Get properties in a Crafting HEBGraph.

    Args:
        graph (HEBGraph): An HEBehavior graph of the Crafting environment.
        all_behaviors (Dict[str, Union[GetItem, ReachZone]): References to all known behaviors.

    Returns:
        Set[str]: Set of properties that appears in the given graph.
    """
    all_behaviors = all_behaviors if all_behaviors is not None else {}
    props_in_graph = set()
    for node in graph.nodes():
        if isinstance(node, Behavior) and node in all_behaviors:
            node = all_behaviors[node]
        if isinstance(node, GetItem) and isinstance(node.item, str):
            props_in_graph.add(node.item)
        if isinstance(node, CraftRecipe) and node.recipe.added_properties is not None:
            props_in_graph += {
                prop for prop, value in node.recipe.added_properties.items() if value
            }
    return props_in_graph
