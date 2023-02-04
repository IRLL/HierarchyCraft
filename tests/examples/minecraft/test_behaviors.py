# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module testing utils functions for crafting behaviors. """

import pytest
import pytest_check as check

import matplotlib.pyplot as plt
from hebg.unrolling import unroll_graph

from crafting import MineCraftingEnv
from crafting.examples.minecraft.items import (
    WOOD,
    WOOD_PLANK,
    STICK,
    OPEN_NETHER_PORTAL,
    CRAFTING_TABLE,
)
from crafting.examples.minecraft.tools import (
    MC_TOOLS_BY_TYPE_AND_MATERIAL,
    ToolType,
    Material,
)


from crafting.examples.minecraft.zones import UNDERGROUND, NETHER

from crafting.behaviors.utils import (
    get_items_in_graph,
    get_zones_items_in_graph,
)


WOODEN_PICKAXE = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][Material.WOOD]
STONE_PICKAXE = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][Material.STONE]


class TestItemsInWoodenPickaxeGraph:
    """get_items_in_graph"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.mc_env = MineCraftingEnv()
        self.all_behaviors = self.mc_env.get_all_behaviors()
        self.pickaxe_behavior = self.all_behaviors[f"Get {WOODEN_PICKAXE.name}"]

    def test_graph_rolled(self):
        """should give direct needed items in wooden_pickaxe graph."""
        expected_items = {WOOD_PLANK, STICK, WOODEN_PICKAXE}
        graph = self.pickaxe_behavior.graph
        items = get_items_in_graph(graph, all_behaviors=self.all_behaviors)
        check.equal(
            items,
            expected_items,
            msg=f"\nAll nodes in graph:\n{list(graph.nodes())}",
        )

    @pytest.mark.xfail
    def test_graph_unrolled(self):
        """should give all needed items in unrolled wooden_pickaxe graph."""
        expected_items = {WOOD, WOOD_PLANK, STICK, WOODEN_PICKAXE}
        expected_zone_items = {CRAFTING_TABLE}

        unrolled_graph = unroll_graph(
            self.pickaxe_behavior.graph, cut_looping_alternatives=True
        )
        items = get_items_in_graph(unrolled_graph)
        zone_items = get_zones_items_in_graph(unrolled_graph)
        check.equal(
            items,
            expected_items,
            msg=f"\nItems in graph:\n{items}",
        )
        check.equal(
            zone_items,
            expected_zone_items,
            msg=f"\nZone items in graph:\n{zone_items}",
        )

    def test_graph_draw(self):
        fig, ax = plt.subplots()
        self.pickaxe_behavior.graph.draw(ax)
        plt.close(fig)


def test_go_to_zone_with_tool_needed():
    env = MineCraftingEnv()
    all_behaviors = env.get_all_behaviors()
    go_to_behavior = all_behaviors[f"Reach {UNDERGROUND.name}"]
    items = get_items_in_graph(go_to_behavior.graph, all_behaviors=all_behaviors)
    check.is_in(STONE_PICKAXE, items)


def test_go_to_nether_needs_open_portal():
    env = MineCraftingEnv()
    all_behaviors = env.get_all_behaviors()
    go_to_behavior = all_behaviors[f"Reach {NETHER.name}"]
    zone_items = get_zones_items_in_graph(
        go_to_behavior.graph, all_behaviors=all_behaviors
    )
    check.is_in(OPEN_NETHER_PORTAL, zone_items)
