import pytest_check as check

from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.items import WOOD
from crafting.examples.minecraft.zones import FOREST


def test_wood_require_forest():
    mc_world = McWorld()
    graph = mc_world.requirements_graph
    check.is_true(graph.has_node(FOREST))
    check.is_true(graph.has_node(WOOD))
    check.is_true(graph.has_edge(FOREST, WOOD))
