""" Module testing utils functions for hcraft behaviors. """

from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import pytest_check as check


from hcraft.elements import Item
from hcraft.examples.minecraft.env import ALL_ITEMS, MineHcraftEnv
from hcraft.examples.minecraft.tools import (
    MC_TOOLS_BY_TYPE_AND_MATERIAL,
    Material,
    ToolType,
)
from hcraft.task import GetItemTask

if TYPE_CHECKING:
    from unified_planning.io import PDDLWriter

WOODEN_PICKAXE = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][Material.WOOD]
STONE_PICKAXE = MC_TOOLS_BY_TYPE_AND_MATERIAL[ToolType.PICKAXE][Material.STONE]


WOOD_LEVEL_ITEMS = [
    "wood_pickaxe",
    "wood_shovel",
    "wood_axe",
    "wood_sword",
    "cobblestone",
    "gravel",
]

STONE_LEVEL_ITEMS = [
    "stone_pickaxe",
    "stone_sword",
    "stone_shovel",
    "stone_axe",
    "iron_ore",
    "furnace",
    "flint",
    "coal",
]

LEATHER_TIER_ITEMS = [
    "leather",
    "book",
]

IRON_TIER_ITEMS = [
    "iron_ingot",
    "flint_and_steel",
    "iron_axe",
    "iron_pickaxe",
    "iron_shovel",
    "iron_sword",
]

DIAMOND_TIER_ITEMS = [
    "diamond",
    "gold_ore",
    "ender_pearl",
    "diamond_axe",
    "diamond_pickaxe",
    "diamond_shovel",
    "diamond_sword",
    "obsidian",
    "enchanting_table",
]

GOLD_TIER_ITEMS = [
    "gold_ingot",
    "redstone",
    "clock",
    "gold_axe",
    "gold_pickaxe",
    "gold_shovel",
    "gold_sword",
]

NETHER_LEVEL_ITEMS = [
    "netherrack",
    "blaze_rod",
    "blaze_powder",
]

END_LEVEL_ITEMS = [
    "ender_eye",
    "ender_dragon_head",
]

KNOWN_TO_FAIL_ITEM_FOR_PLANNER = {
    "enhsp": LEATHER_TIER_ITEMS
    + IRON_TIER_ITEMS
    + DIAMOND_TIER_ITEMS
    + GOLD_TIER_ITEMS
    + NETHER_LEVEL_ITEMS
    + END_LEVEL_ITEMS,
    "aries": WOOD_LEVEL_ITEMS
    + STONE_LEVEL_ITEMS
    + LEATHER_TIER_ITEMS
    + IRON_TIER_ITEMS
    + DIAMOND_TIER_ITEMS
    + GOLD_TIER_ITEMS
    + NETHER_LEVEL_ITEMS
    + END_LEVEL_ITEMS,
}


@pytest.mark.slow
@pytest.mark.parametrize("item", [item.name for item in ALL_ITEMS])
@pytest.mark.parametrize("planner_name", ["enhsp", "aries"])
def test_get_item_flat(planner_name: str, item: str):
    """All items should be gettable by planning behavior."""
    up = pytest.importorskip("unified_planning")
    task = GetItemTask(Item(item))
    env = MineHcraftEnv(purpose=task, max_step=500)
    write = False
    problem = env.planning_problem(timeout=5, planner_name=planner_name)

    if write:
        writer: "PDDLWriter" = up.io.PDDLWriter(problem.upf_problem)
        pddl_dir = Path("planning", "pddl", env.name)
        pddl_dir.mkdir(exist_ok=True)
        writer.write_domain(pddl_dir / "MineHCraftDomain.pddl")
        writer.write_problem(pddl_dir / f"Get{item.capitalize()}Problem.pddl")

    if item in KNOWN_TO_FAIL_ITEM_FOR_PLANNER[planner_name]:
        pytest.xfail(f"{planner_name} planner is known to fail to get {item}")

    done = False
    _observation = env.reset()
    while not done:
        action = problem.action_from_plan(env.state)
        _observation, _reward, done, _ = env.step(action)
    check.is_true(env.purpose.terminated, msg=f"Plan failed :{problem.plans}")
    check.equal(env.current_step, len(problem.plans[0].actions))
