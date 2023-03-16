from unified_planning.shortcuts import OneshotPlanner
from crafting.planning import world_task_to_planning_problem
from crafting.task import PlaceItemTask
from crafting.elements import Item, Zone, ItemStack

from tests.envs import classic_env


def test_crafting_classic():
    env, _, named_transformations, start_zone, items, zones, zones_items = classic_env()

    task = PlaceItemTask(ItemStack(Item("table"), 1), Zone("other_zone"))

    problem = world_task_to_planning_problem(env.world, env.name, task)
    print(problem)

    with OneshotPlanner(problem_kind=problem.kind) as planner:
        result = planner.solve(problem)

    expected_plan = (
        "[1_search_wood(start), "
        "0_move_to_other_zone(start), "
        "3_craft_plank(other_zone), "
        "4_craft_table(other_zone)]"
    )

    assert repr(result.plan) == expected_plan
