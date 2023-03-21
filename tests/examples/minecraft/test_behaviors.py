""" Module testing utils functions for hcraft behaviors. """

import matplotlib.pyplot as plt
import pytest
import pytest_check as check

from hcraft.behaviors.utils import get_items_in_graph, get_zones_items_in_graph
from hcraft.examples.minecraft.env import MineHcraftEnv
from hcraft.examples.minecraft.items import (
    OPEN_NETHER_PORTAL,
    STICK,
    WOOD_PLANK,
)
from hcraft.examples.minecraft.tools import (
    MC_TOOLS_BY_TYPE_AND_MATERIAL,
    Material,
    ToolType,
)
from hcraft.examples.minecraft.zones import NETHER, UNDERGROUND
from hcraft.purpose import platinium_purpose
from hcraft.task import GetItemTask, GoToZoneTask

WOODEN_PICKAXE = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][Material.WOOD]
STONE_PICKAXE = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][Material.STONE]


@pytest.mark.slow
def test_solving_behaviors():
    """All tasks should be solved by their solving behavior."""
    mc_env = MineHcraftEnv(
        purpose=platinium_purpose(MineHcraftEnv().world), max_step=200
    )
    done = False
    observation = mc_env.reset()
    while not done:
        for task in mc_env.purpose.tasks:
            if not task.terminated:
                solving_behavior = mc_env.solving_behavior(task)
                break
        action = solving_behavior(observation)
        observation, _rew, done, _infos = mc_env.step(action)
    check.is_true(done)


class TestItemsInWoodenPickaxeGraph:
    """get_items_in_graph"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.mc_env = MineHcraftEnv()
        task = GetItemTask(WOODEN_PICKAXE)
        self.pickaxe_behavior = self.mc_env.solving_behavior(task)

    def test_graph_rolled(self):
        """should give direct needed items in wooden_pickaxe graph."""
        expected_items = {WOOD_PLANK, STICK, WOODEN_PICKAXE}
        graph = self.pickaxe_behavior.graph
        items = get_items_in_graph(graph, all_behaviors=self.mc_env.all_behaviors)
        check.equal(
            items,
            expected_items,
            msg=f"\nAll nodes in graph:\n{list(graph.nodes())}",
        )

    def test_graph_draw(self):
        fig, ax = plt.subplots()
        self.pickaxe_behavior.graph.draw(ax)
        plt.close(fig)


def test_go_to_zone_with_tool_needed():
    env = MineHcraftEnv()
    task = GoToZoneTask(UNDERGROUND)
    go_to_underground = env.solving_behavior(task)
    items = get_items_in_graph(go_to_underground.graph, all_behaviors=env.all_behaviors)
    check.is_in(STONE_PICKAXE, items)


def test_go_to_nether_needs_open_portal():
    env = MineHcraftEnv()
    task = GoToZoneTask(NETHER)
    go_to_nether = env.solving_behavior(task)
    zone_items = get_zones_items_in_graph(
        go_to_nether.graph, all_behaviors=env.all_behaviors
    )
    check.is_in(OPEN_NETHER_PORTAL, zone_items)
