import pytest_check as check

from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.items import WOOD, STONE_PICKAXE
from crafting.examples.minecraft.zones import FOREST, BEDROCK


def test_wood_require_forest():
    mc_world = McWorld()
    graph = mc_world.requirements_graph
    check.is_true(graph.has_node(FOREST))
    check.is_true(graph.has_node(WOOD))
    check.is_true(graph.has_edge(FOREST, WOOD))


def test_bedrock_require_stone_pickaxe():
    mc_world = McWorld()
    graph = mc_world.requirements_graph
    check.is_true(graph.has_node(BEDROCK))
    check.is_true(graph.has_node(STONE_PICKAXE))
    check.is_true(graph.has_edge(STONE_PICKAXE, BEDROCK))
