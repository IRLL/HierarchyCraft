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
        if isinstance(node, Behavior) and str(node) in all_behaviors:
            node = all_behaviors[str(node)]
        if isinstance(node, (SearchItem, GetItem)):
            if isinstance(node.item, Item):
                items_in_graph.add(node.item)
        if isinstance(node, CraftRecipe):
            if node.recipe.outputs is not None:
                for itemstack in node.recipe.outputs:
                    items_in_graph.add(itemstack.item)
    return items_in_graph
