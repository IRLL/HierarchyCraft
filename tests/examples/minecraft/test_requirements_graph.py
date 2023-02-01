import pytest
import pytest_check as check

import matplotlib.pyplot as plt

from crafting import MineCraftingEnv
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import (
    MC_TOOLS_BY_TYPE_AND_MATERIAL,
    ToolType,
    Material,
)

from crafting.examples.minecraft.zones import *
from crafting.requirement_graph import _str_zone_item

IRON_PICKAXE = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][Material.IRON]


class TestMineCraftingReqGraph:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.env = MineCraftingEnv()
        self.graph = self.env.requirements_graph

    def test_wood_require_forest(self):
        check.is_true(self.graph.has_node(FOREST.name))
        check.is_true(self.graph.has_node(WOOD.name))
        check.is_true(self.graph.has_edge(FOREST.name, WOOD.name))

    def test_bedrock_require_iron_pickaxe(self):
        check.is_true(self.graph.has_node(BEDROCK.name))
        check.is_true(self.graph.has_node(IRON_PICKAXE.name))
        check.is_true(self.graph.has_edge(IRON_PICKAXE.name, BEDROCK.name))

    def test_close_portal_require_zone_where_is(self):
        check.is_true(self.graph.has_node(STRONGHOLD.name))
        check.is_true(self.graph.has_node(_str_zone_item(CLOSE_ENDER_PORTAL.name)))
        check.is_true(
            self.graph.has_edge(
                STRONGHOLD.name, _str_zone_item(CLOSE_ENDER_PORTAL.name)
            )
        )

    def test_close_portal_do_not_require_itself(self):
        check.is_true(self.graph.has_node(_str_zone_item(CLOSE_ENDER_PORTAL.name)))
        check.is_false(
            self.graph.has_edge(
                _str_zone_item(CLOSE_ENDER_PORTAL.name),
                _str_zone_item(CLOSE_ENDER_PORTAL.name),
            )
        )

    def test_nether_portal_in_nether_should_not_make_a_loop(self):
        check.is_true(self.graph.has_node(_str_zone_item(OPEN_NETHER_PORTAL.name)))
        check.is_true(self.graph.has_node(NETHER.name))
        check.is_false(
            self.graph.has_edge(NETHER.name, _str_zone_item(OPEN_NETHER_PORTAL.name))
        )

    def test_furnace_do_not_require_coal(self):
        check.is_true(self.graph.has_node(_str_zone_item(FURNACE.name)))
        check.is_true(self.graph.has_node(COAL.name))
        check.is_false(self.graph.has_edge(COAL.name, _str_zone_item(FURNACE.name)))


def test_draw_requirements_graph():
    fig, ax = plt.subplots()
    env = MineCraftingEnv()
    env.draw_requirements_graph(ax, layout="spring")
    plt.close(fig)
