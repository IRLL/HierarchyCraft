from hcraft.task import PlaceItemTask
from hcraft.purpose import Purpose
from hcraft.elements import Item, Zone, Stack

from tests.envs import classic_env
import pytest


@pytest.mark.slow
def test_hcraft_classic():
    pytest.importorskip("unified_planning")
    env, _, named_transformations, start_zone, items, zones, zones_items = classic_env()

    task = PlaceItemTask(Stack(Item("table"), 1), Zone("other_zone"))
    env.purpose = Purpose(task)

    problem = env.planning_problem(planner_name="aries")
    print(problem.upf_problem)

    problem.solve()

    expected_plan = [
        "1_search_wood(start)",
        "0_move_to_other_zone(start)",
        "3_craft_plank(other_zone)",
        "4_craft_table(other_zone)",
    ]
    assert expected_plan == [str(action) for action in problem.plan.actions]
