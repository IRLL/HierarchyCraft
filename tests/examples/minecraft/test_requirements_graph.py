import matplotlib.pyplot as plt
import pytest
import pytest_check as check

from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.tools import (
    MC_TOOLS_BY_TYPE_AND_MATERIAL,
    Material,
    ToolType,
)
from crafting.examples.minecraft.zones import *
from crafting.requirements import ReqNodesTypes, req_node_name

IRON_PICKAXE = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][Material.IRON]


class TestMineCraftingReqGraph:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.env = MineCraftingEnv()
        self.graph = self.env.requirements.graph

    def test_wood_require_forest(self):
        forest_node = req_node_name(FOREST, ReqNodesTypes.ZONE)
        check.is_true(self.graph.has_node(forest_node))
        wood_node = req_node_name(WOOD, ReqNodesTypes.ITEM)
        check.is_true(self.graph.has_node(wood_node))
        check.is_true(self.graph.has_edge(forest_node, wood_node))

    def test_bedrock_require_iron_pickaxe(self):
        bedrock_node = req_node_name(BEDROCK, ReqNodesTypes.ZONE)
        check.is_true(self.graph.has_node(bedrock_node))
        iron_pickaxe_node = req_node_name(IRON_PICKAXE, ReqNodesTypes.ITEM)
        check.is_true(self.graph.has_node(iron_pickaxe_node))
        check.is_true(self.graph.has_edge(iron_pickaxe_node, bedrock_node))

    def test_close_portal_require_zone_where_is(self):
        stronghold_node = req_node_name(STRONGHOLD, ReqNodesTypes.ZONE)
        check.is_true(self.graph.has_node(stronghold_node))
        ender_portal_node = req_node_name(CLOSE_ENDER_PORTAL, ReqNodesTypes.ZONE_ITEM)
        check.is_true(self.graph.has_node(ender_portal_node))
        check.is_true(self.graph.has_edge(stronghold_node, ender_portal_node))

    def test_close_portal_do_not_require_itself(self):
        ender_portal_node = req_node_name(CLOSE_ENDER_PORTAL, ReqNodesTypes.ZONE_ITEM)
        check.is_true(self.graph.has_node(ender_portal_node))
        check.is_false(self.graph.has_edge(ender_portal_node, ender_portal_node))

    def test_furnace_do_not_require_coal(self):
        furnace_node = req_node_name(FURNACE, ReqNodesTypes.ZONE_ITEM)
        check.is_true(self.graph.has_node(furnace_node))
        coal_node = req_node_name(COAL, ReqNodesTypes.ITEM)
        check.is_true(self.graph.has_node(coal_node))
        check.is_false(self.graph.has_edge(coal_node, furnace_node))


def test_draw_requirements_graph():
    fig, ax = plt.subplots()
    env = MineCraftingEnv()
    env.requirements.draw(ax, layout="spring")
    plt.close(fig)
