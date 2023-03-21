import pytest
import pytest_check as check

from hcraft.examples.minecraft.env import MineHcraftEnv
import hcraft.examples.minecraft.items as items
import hcraft.examples.minecraft.zones as zones
from hcraft.examples.minecraft.tools import (
    MC_TOOLS_BY_TYPE_AND_MATERIAL,
    Material,
    ToolType,
)
from hcraft.requirements import RequirementNode, req_node_name

IRON_PICKAXE = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][Material.IRON]


class TestMineHcraftReqGraph:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.env = MineHcraftEnv()
        self.graph = self.env.world.requirements.graph

    def test_wood_require_forest(self):
        forest_node = req_node_name(zones.FOREST, RequirementNode.ZONE)
        check.is_true(self.graph.has_node(forest_node))
        wood_node = req_node_name(items.WOOD, RequirementNode.ITEM)
        check.is_true(self.graph.has_node(wood_node))
        check.is_true(self.graph.has_edge(forest_node, wood_node))

    def test_bedrock_require_iron_pickaxe(self):
        bedrock_node = req_node_name(zones.BEDROCK, RequirementNode.ZONE)
        check.is_true(self.graph.has_node(bedrock_node))
        iron_pickaxe_node = req_node_name(IRON_PICKAXE, RequirementNode.ITEM)
        check.is_true(self.graph.has_node(iron_pickaxe_node))
        check.is_true(self.graph.has_edge(iron_pickaxe_node, bedrock_node))

    def test_close_portal_require_zone_where_is(self):
        stronghold_node = req_node_name(zones.STRONGHOLD, RequirementNode.ZONE)
        check.is_true(self.graph.has_node(stronghold_node))
        ender_portal_node = req_node_name(
            items.CLOSE_ENDER_PORTAL, RequirementNode.ZONE_ITEM
        )
        check.is_true(self.graph.has_node(ender_portal_node))
        check.is_true(self.graph.has_edge(stronghold_node, ender_portal_node))

    def test_close_portal_do_not_require_itself(self):
        ender_portal_node = req_node_name(
            items.CLOSE_ENDER_PORTAL, RequirementNode.ZONE_ITEM
        )
        check.is_true(self.graph.has_node(ender_portal_node))
        check.is_false(self.graph.has_edge(ender_portal_node, ender_portal_node))

    def test_furnace_do_not_require_coal(self):
        furnace_node = req_node_name(items.FURNACE, RequirementNode.ZONE_ITEM)
        check.is_true(self.graph.has_node(furnace_node))
        coal_node = req_node_name(items.COAL, RequirementNode.ITEM)
        check.is_true(self.graph.has_node(coal_node))
        check.is_false(self.graph.has_edge(coal_node, furnace_node))

    def test_stronghold_is_not_directly_accessible_from_nether(self):
        stronghold_node = req_node_name(zones.STRONGHOLD, RequirementNode.ZONE)
        check.is_true(self.graph.has_node(stronghold_node))
        nether_node = req_node_name(zones.NETHER, RequirementNode.ZONE)
        check.is_true(self.graph.has_node(nether_node))

        assert self.graph.has_edge(nether_node, stronghold_node)
        assert self.graph.has_edge(stronghold_node, stronghold_node)
        from_nether_indexes = []
        self_indexes = []
        for start, end, key in self.graph.in_edges(stronghold_node, keys=True):
            if start == nether_node:
                from_nether_indexes.append(key)
            if end == start == stronghold_node:
                self_indexes.append(key)
        check.is_true(
            any(key in self_indexes for key in from_nether_indexes),
            msg=f"self_indexes={self_indexes},from_nether_indexes={from_nether_indexes}",
        )
