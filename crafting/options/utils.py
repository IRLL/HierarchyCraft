# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module for utility functions to apply on handcrafted Option. """

from typing import Set

from option_graph import OptionGraph

from crafting.world.items import Item
from crafting.options.feature_conditions import HasItem, HasProperty, IsInZone
from crafting.options.actions import SearchItem, CraftRecipe, MoveToZone
from crafting.options.options import GetItem, ReachZone


def get_items_in_graph(graph: OptionGraph) -> Set[Item]:
    items_in_graph = set()
    for node in graph.nodes():
        if isinstance(node, (SearchItem, GetItem)):
            items_in_graph.add(node.item)
        if isinstance(node, CraftRecipe):
            for itemstack in node.recipe.outputs:
                items_in_graph.add(itemstack.item)
    return items_in_graph
