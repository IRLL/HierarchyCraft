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


KNOWN_TO_FAIL_ITEM_ENHSP = [
    "reeds",
    "wood_pickaxe",
    "wood_axe",
    "cobblestone",
    "coal",
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
@pytest.mark.parametrize("item", [item.name for item in ALL_ITEMS])
def test_get_all_items_pddl(item: str):
    """All items should be gettable by planning behavior."""
    up = pytest.importorskip("unified_planning")
    task = GetItemTask(Item(item))
    env = MineHcraftEnv(purpose=task, max_step=500)
    write = False
    problem = env.planning_problem(timeout=5)

    if write:
        writer: "PDDLWriter" = up.io.PDDLWriter(problem.upf_problem)
        pddl_dir = Path("planning", "pddl", env.name)
        pddl_dir.mkdir(exist_ok=True)
        writer.write_domain(pddl_dir / "MineHCraftDomain.pddl")
        writer.write_problem(pddl_dir / f"Get{item.capitalize()}Problem.pddl")

    if item in KNOWN_TO_FAIL_ITEM_ENHSP:
        pytest.xfail(f"ENHSP planner is known to fail to get {item}")

    done = False
    _observation = env.reset()
    while not done:
        action = problem.action_from_plan(env.state)
        _observation, _reward, done, _ = env.step(action)
    check.is_true(env.purpose.terminated, msg=f"Plan failed :{problem.plans}")
    check.equal(env.current_step, problem.stats[0]["Plan-Length"])
