from typing import TYPE_CHECKING
from hcraft.task import GetItemTask, PlaceItemTask
from hcraft.purpose import Purpose
from hcraft.elements import Item, Zone, Stack

from tests.envs import classic_env
import pytest

if TYPE_CHECKING:
    import unified_planning.model.htn as htn


def test_classic_flat():
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
        "3_craft_plank",
        "4_craft_table(other_zone)",
    ]

    assert str(expected_plan).replace("'", "") in repr(problem.plan)


class TestClassicHierarchical:
    @pytest.fixture(autouse=True)
    def setup(self):
        pytest.importorskip("unified_planning")
        (
            self.env,
            _,
            named_transformations,
            start_zone,
            items,
            zones,
            zones_items,
        ) = classic_env()

    def test_get_item_no_precondition_multiple(self):
        task = GetItemTask(Stack(Item("wood"), 3))
        self.env.purpose = Purpose(task)

        problem = self.env.planning_problem(hierarchical=True)

        htn: "htn" = pytest.importorskip("unified_planning.model.htn")
        assert isinstance(problem.upf_problem, htn.HierarchicalProblem)

        print(problem.upf_problem)

        problem.solve()

        expected_plan = [
            "1_search_wood",
            "1_search_wood",
            "1_search_wood",
        ]

        assert str(expected_plan).replace("'", "") in repr(problem.plan.actions)

    # def test_place_item_in_zone(self):
    #     task = PlaceItemTask(Stack(Item("table"), 1), Zone("other_zone"))
    #     self.env.purpose = Purpose(task)

    #     problem = self.env.planning_problem(hierarchical=True)

    #     htn: "htn" = pytest.importorskip("unified_planning.model.htn")
    #     assert isinstance(problem.upf_problem, htn.HierarchicalProblem)

    #     print(problem.upf_problem)

    #     problem.solve()

    #     expected_plan = [
    #         "1_search_wood(start)",
    #         "0_move_to_other_zone(start)",
    #         "3_craft_plank(other_zone)",
    #         "4_craft_table(other_zone)",
    #     ]

    #     assert str(expected_plan).replace("'", "") in repr(problem.plan.actions)
