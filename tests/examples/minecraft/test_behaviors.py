""" Module testing utils functions for hcraft behaviors. """

import os
from pathlib import Path

import matplotlib.pyplot as plt
import pytest
import pytest_check as check

from unified_planning.io import PDDLWriter

from hcraft.elements import Item
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
    env = MineHcraftEnv(purpose=platinium_purpose(MineHcraftEnv().world), max_step=500)
    done = False
    observation = env.reset()
    solving_behavior = None
    tasks_left = env.purpose.tasks.copy()
    task = None
    while not done and not env.purpose.terminated:
        tasks_left = [t for t in tasks_left if not t.terminated]
        if task is None:
            task = tasks_left.pop(0)
            print(f"Task started: {task} (step={env.current_step})")
            solving_behavior = env.solving_behavior(task)
        action = solving_behavior(observation)
        observation, _rew, done, _infos = env.step(action)
        if task.terminated:
            print(f"Task finished: {task}, tasks_left: {tasks_left}")
            task = None
    print(f"Last unfinished task: {task}")
    if len(tasks_left) <= 4:
        pytest.xfail("Harder tasks cannot be done for now ...")
    check.is_true(env.purpose.terminated, msg=f"tasks not completed: {tasks_left}")


KNOWN_TO_FAIL_ITEM = [
    "leather",
    "book",
    "flint_and_steel",
    "iron_axe",
    "iron_pickaxe",
    "iron_shovel",
    "iron_sword",
    "ender_pearl",
    "diamond",
    "gold_ore",
    "redstone",
    "diamond_axe",
    "diamond_pickaxe",
    "diamond_shovel",
    "diamond_sword",
    "gold_ingot",
    "clock",
    "gold_axe",
    "gold_pickaxe",
    "gold_shovel",
    "gold_sword",
    "obsidian",
    "enchanting_table",
    "blaze_rod",
    "netherrack",
    "blaze_powder",
    "ender_eye",
    "ender_dragon_head",
]


@pytest.mark.slow
@pytest.mark.parametrize("item", [item.name for item in MineHcraftEnv().world.items])
def test_get_all_items_pddl(item: str):
    """All items should be gettable by planning behavior."""
    task = GetItemTask(Item(item))
    env = MineHcraftEnv(purpose=task, max_step=500)
    write = False
    problem = env.planning_problem(timeout=5)

    if item in KNOWN_TO_FAIL_ITEM:
        pytest.xfail(f"ENHSP planner is known to fail to get {item}")

    if write:
        writer = PDDLWriter(problem.upf_problem)
        pddl_dir = Path("planning", "pddl", env.name)
        os.makedirs(pddl_dir, exist_ok=True)
        writer.write_domain(pddl_dir / "domain.pddl")
        writer.write_problem(pddl_dir / f"{task.name}.pddl")

    done = False
    _observation = env.reset()
    while not done:
        action = problem.action_from_plan(env.state)
        _observation, _reward, done, _ = env.step(action)
    check.is_true(env.purpose.terminated, msg=f"Plan failed :{problem.plans}")
    check.equal(env.current_step, problem.stats[0]["Plan-Length"])


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
