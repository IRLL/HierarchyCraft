import pytest_check as check

from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.items import WOOD, STONE_PICKAXE
from crafting.examples.minecraft.zones import FOREST, BEDROCK, UNDERGROUND


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


def test_close_portal_require_zone_where_is():
    mc_world = McWorld()
    graph = mc_world.requirements_graph
    check.is_true(graph.has_node(UNDERGROUND))
    check.is_true(graph.has_node("close_ender_portal"))
    check.is_true(graph.has_edge(UNDERGROUND, "close_ender_portal"))


def test_close_portal_do_not_require_itself():
    mc_world = McWorld()
    graph = mc_world.requirements_graph
    check.is_true(graph.has_node("close_ender_portal"))
    check.is_false(graph.has_edge("close_ender_portal", "close_ender_portal"))
