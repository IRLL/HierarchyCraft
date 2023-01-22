# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module testing utils functions for crafting behaviors. """

import pytest
import pytest_check as check

from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.items import WOODEN_PICKAXE, WOOD, WOOD_PLANK, STICK
from crafting.examples.minecraft.zones import UNDERGROUND, NETHER

from crafting.behaviors.utils import get_items_in_graph, get_properties_in_graph


class TestItemsInWoodenPickaxeGraph:
    """get_items_in_graph"""

    @pytest.fixture(autouse=True)
    def setup(self):
        self.mcworld = McWorld()
        self.all_behaviors = self.mcworld.get_all_behaviors()
        self.pickaxe_behavior = self.all_behaviors[f"Get {WOODEN_PICKAXE}"]

    def test_graph_rolled(self):
        """should give direct needed items in wooden_pickaxe graph."""
        expected_items = {WOOD_PLANK, STICK, WOODEN_PICKAXE}
        items = get_items_in_graph(
            self.pickaxe_behavior.graph,
            all_behaviors=self.all_behaviors,
        )
        check.equal(items, expected_items)

    def test_graph_unrolled(self):
        """should give all needed items in unrolled wooden_pickaxe graph."""
        expected_items = {WOOD, WOOD_PLANK, STICK, WOODEN_PICKAXE}
        items = get_items_in_graph(self.pickaxe_behavior.graph.unrolled_graph)
        check.equal(items, expected_items)


def test_go_to_zone_with_tool_needed():
    world = McWorld()
    all_behaviors = world.get_all_behaviors()
    go_to_behavior = all_behaviors[f"Reach {UNDERGROUND}"]
    items = get_items_in_graph(go_to_behavior.graph, all_behaviors=all_behaviors)
    check.is_in(WOODEN_PICKAXE, items)


def test_go_to_zone_with_property_needed():
    world = McWorld()
    all_behaviors = world.get_all_behaviors()
    go_to_behavior = all_behaviors[f"Reach {NETHER}"]
    props = get_properties_in_graph(go_to_behavior.graph, all_behaviors=all_behaviors)
    check.is_in("open_nether_portal", props)
