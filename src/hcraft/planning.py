"""# HierarchyCraft as planning problem

HierarchyCraft environments can be converted to planning problem in one line
thanks to the Unified Planning Framework (UPF):

```python
problem = env.planning_problem()
print(problem.upf_problem)
```

Then they can be solved with an installed planner (default is enhsp):

```python
problem.solve()
print(problem.plan)
```

Actions can be extracted from a planner to interact with the environment:

```python
done = False
_observation = env.reset()
while not done:
    action = problem.action_from_plan(env.state)
    _observation, _reward, done, _ = env.step(action)

print(f"Plans were :{problem.plans}")

# If the plan is a success, purpose should be terminated.
assert env.purpose.terminated
```

## HierarchyCraft as PDDL2.1 domain & problem

The Unified Planning Framework itself allows to write planning problems in the PDDL2.1 language,
commonly used in the planning community. For instructions, refer to the
[UPF documentation](https://unified-planning.readthedocs.io/en/stable/interoperability.html).


![](../../docs/images/PDDL_HierarchyCraft_domain.png)

### Types
There is only three types in every HierarchyCraft environment:
- zones
- items that the player can obtain
- items that zones can obtain.

### Constants
Most of the time, zones and items will be directly referenced in actions of the PDDL problem.
Hence, all zones and items will be constants of the domain and not objects of the problem.

### Predicates
The only predicates are about the player position.
They allow to track where is the player currently ("pos") and where has has been ("visited").

### Functions
HierarchyCraft relies on numerical-fluents from PDDL2.1,
they allow to define the player inventory ("amount") and the inventories of each zone ("amount_at")

### Actions
Actions are directly defined by transformations.
Each transformation will be converted to an action.
Respectfully, the min/max conditions of the transformation will become the preconditions of the PDDL action
and the added/removed items and updated position of the transformation will become the effects of the PDDL action.

![](../../docs/images/PDDL_HierarchyCraft_problem.png)

### Initialisation
The problem file, will define the initial state
of every inventory for every item together with the initial position of the player.

### Goal
The PDDL goal is translated from the HierarchyCraft purpose.
If multiple terminal groups exists in the purpose, the PDDL goal will be the highest value terminal group.

"""

from typing import TYPE_CHECKING, Dict, Optional, Union, List
from copy import deepcopy


from hcraft.transformation import Transformation, InventoryOwner
from hcraft.task import Task, GetItemTask, PlaceItemTask, GoToZoneTask
from hcraft.purpose import Purpose
from hcraft.elements import Zone, Item

# unified_planning is an optional dependency.
UPF_AVAILABLE = True
try:
    import unified_planning.shortcuts as ups
    from unified_planning.plans import SequentialPlan
    from unified_planning.engines.results import PlanGenerationResult
    from unified_planning.model.problem import Problem

    UserType = ups.UserType
    Object = ups.Object
    BoolType = ups.BoolType
    IntType = ups.IntType
    Fluent = ups.Fluent
    InstantaneousAction = ups.InstantaneousAction
    OneshotPlanner = ups.OneshotPlanner
    OR = ups.Or
    AND = ups.And
    GE = ups.GE
    LE = ups.LE


except ImportError:
    UPF_AVAILABLE = False


if TYPE_CHECKING:
    from hcraft.state import HcraftState

Statistics = Dict[str, Union[int, float]]


class HcraftPlanningProblem:
    """Interface between the unified planning framework and HierarchyCraft."""

    def __init__(
        self,
        state: "HcraftState",
        name: str,
        purpose: Optional["Purpose"],
        timeout: float = 60,
        planner_name: Optional[str] = None,
    ) -> None:
        """Initialize a HierarchyCraft planning problem on the given state and purpose.

        Args:
            state: Initial state of the HierarchyCraft environment.
            name: Name of the planning problem.
            purpose: Purpose used to compute the planning goal.
            timeout: Time budget (s) for the plan to be found before giving up.
                Set to -1 for no limit. Defaults to 60.
        """
        if not UPF_AVAILABLE:
            raise ImportError(
                "Missing planning dependencies. Install with:\n"
                "pip install hcraft[planning]"
            )
        self.upf_problem: "Problem" = self._init_problem(state, name, purpose)
        self.plan: Optional[SequentialPlan] = None
        self.plans: List[SequentialPlan] = []
        self.stats: List[Statistics] = []
        self.timeout = timeout
        self.planner_name = planner_name

    def action_from_plan(self, state: "HcraftState") -> Optional[int]:
        """Get the next gym action from a given state.

        If a plan is already existing, just use the next action in the plan.
        If no plan exists, first update and solve the planning problem.

        Args:
            state (HcraftState): Current state of the hcraft environement.

        Returns:
            int: Action to take according to the plan. Returns None if no action is required.
        """
        if self.plan is None:
            self.update_problem_to_state(self.upf_problem, state)
            self.solve()
        if not self.plan.actions:  # Empty plan, nothing to do
            return None
        plan_action_name = str(self.plan.actions.pop(0))
        if not self.plan.actions:
            self.plan = None
        action = int(plan_action_name.split("_")[0])
        return action

    def update_problem_to_state(self, upf_problem: "Problem", state: "HcraftState"):
        """Update the planning problem initial state to the given state.

        Args:
            state: HierarchyCraft state to use as reference for the
                initial state of the planning problem.
        """
        current_pos = state.current_zone
        for zone in state.world.zones:
            discovered = state.has_discovered(zone)
            if current_pos is not None:
                upf_problem.set_initial_value(
                    self.pos(self.zones_obj[zone]), zone == current_pos
                )
            upf_problem.set_initial_value(
                self.visited(self.zones_obj[zone]), discovered
            )

        for item in state.world.items:
            quantity = state.amount_of(item)
            upf_problem.set_initial_value(self.amount(self.items_obj[item]), quantity)

        for zone in state.world.zones:
            for zone_item in state.world.zones_items:
                quantity = state.amount_of(zone_item, zone)
                upf_problem.set_initial_value(
                    self.amount_at(
                        self.zone_items_obj[zone_item], self.zones_obj[zone]
                    ),
                    quantity,
                )

    def solve(self) -> PlanGenerationResult:
        """Solve the current planning problem with a planner."""
        planner_kwargs = {"problem_kind": self.upf_problem.kind}
        if self.planner_name is not None:
            planner_kwargs.update(name=self.planner_name)
        with OneshotPlanner(**planner_kwargs) as planner:
            results: PlanGenerationResult = planner.solve(
                self.upf_problem, timeout=self.timeout
            )
        if results.plan is None:
            raise ValueError("Not plan could be found for this problem.")
        self.plan = deepcopy(results.plan)
        self.plans.append(deepcopy(results.plan))
        self.stats.append(_read_statistics(results))
        return results

    def _init_problem(
        self, state: "HcraftState", name: str, purpose: Optional["Purpose"]
    ) -> Problem:
        """Build a unified planning problem from the given world and purpose.

        Args:
            world: HierarchyCraft world to generate the problem from.
            name: Name given to the planning problem.
            purpose: Purpose of the agent.
                Will be used to set the goal of the planning problem.

        Returns:
            Problem: Unified planning problem.
        """
        upf_problem = Problem(name)
        self.zone_type = UserType("zone")
        self.player_item_type = UserType("player_item")
        self.zone_item_type = UserType("zone_item")

        self.zones_obj: Dict[Zone, Object] = {}
        for zone in state.world.zones:
            self.zones_obj[zone] = Object(zone.name, self.zone_type)

        self.items_obj: Dict[Item, Object] = {}
        for item in state.world.items:
            self.items_obj[item] = Object(item.name, self.player_item_type)

        self.zone_items_obj: Dict[Item, Object] = {}
        for item in state.world.zones_items:
            self.zone_items_obj[item] = Object(
                f"{item.name}_in_zone", self.zone_item_type
            )

        upf_problem.add_objects(self.zones_obj.values())
        upf_problem.add_objects(self.items_obj.values())
        upf_problem.add_objects(self.zone_items_obj.values())

        self.pos = Fluent("pos", BoolType(), zone=self.zone_type)
        self.visited = Fluent("visited", BoolType(), zone=self.zone_type)
        self.amount = Fluent("amount", IntType(), item=self.player_item_type)
        self.amount_at = Fluent(
            "amount_at", IntType(), item=self.zone_item_type, zone=self.zone_type
        )

        upf_problem.add_fluent(self.pos, default_initial_value=False)
        upf_problem.add_fluent(self.visited, default_initial_value=False)
        upf_problem.add_fluent(self.amount, default_initial_value=0)
        upf_problem.add_fluent(self.amount_at, default_initial_value=0)

        actions = []
        for t_id, transfo in enumerate(state.world.transformations):
            actions.append(self._action_from_transformation(transfo, t_id))

        upf_problem.add_actions(actions)

        if purpose is not None and purpose.terminal_groups:
            upf_problem.add_goal(self._purpose_to_goal(purpose))

        self.update_problem_to_state(upf_problem, state)
        return upf_problem

    def _action_from_transformation(
        self, transformation: "Transformation", transformation_id: int
    ) -> InstantaneousAction:
        action_name = f"{transformation_id}_{transformation.name}"
        action = InstantaneousAction(action_name)
        loc = None
        if len(self.zones_obj) > 0:
            action = InstantaneousAction(action_name, loc=self.zone_type)
            loc = action.parameter("loc")
            action.add_precondition(self.pos(loc))

        if transformation.zone and len(self.zones_obj) > 1:
            action.add_precondition(self.pos(self.zones_obj[transformation.zone]))

        if transformation.destination is not None:
            action.add_effect(self.pos(loc), False)
            action.add_effect(
                self.visited(self.zones_obj[transformation.destination]), True
            )
            action.add_effect(
                self.pos(self.zones_obj[transformation.destination]), True
            )

        self._add_player_operation(action, transformation)
        self._add_current_zone_operations(action, transformation, loc)
        return action

    def _add_player_operation(
        self,
        action: "InstantaneousAction",
        transfo: Transformation,
    ):
        player = InventoryOwner.PLAYER
        for stack in transfo.get_changes(player, "add", []):
            stack_amount = self.amount(self.items_obj[stack.item])
            action.add_increase_effect(stack_amount, stack.quantity)

        for max_stack in transfo.get_changes(player, "max", []):
            stack_amount = self.amount(self.items_obj[max_stack.item])
            action.add_precondition(LE(stack_amount, max_stack.quantity))

        for stack in transfo.get_changes(player, "remove", []):
            stack_amount = self.amount(self.items_obj[stack.item])
            action.add_decrease_effect(stack_amount, stack.quantity)

        for min_stack in transfo.get_changes(player, "min", []):
            stack_amount = self.amount(self.items_obj[min_stack.item])
            action.add_precondition(GE(stack_amount, min_stack.quantity))

    def _add_current_zone_operations(
        self,
        action: "InstantaneousAction",
        transfo: Transformation,
        loc,
    ):
        current = InventoryOwner.CURRENT
        for stack in transfo.get_changes(current, "add", []):
            amount_at_loc = self.amount_at(self.zone_items_obj[stack.item], loc)
            action.add_increase_effect(amount_at_loc, stack.quantity)

        for max_stack in transfo.get_changes(current, "max", []):
            amount_at_loc = self.amount_at(self.zone_items_obj[max_stack.item], loc)
            action.add_precondition(LE(amount_at_loc, max_stack.quantity))

        for rem_stack in transfo.get_changes(current, "remove", []):
            amount_at_loc = self.amount_at(self.zone_items_obj[rem_stack.item], loc)
            action.add_decrease_effect(amount_at_loc, rem_stack.quantity)

        for min_stack in transfo.get_changes(current, "min", []):
            stack_amount = self.amount_at(self.zone_items_obj[min_stack.item], loc)
            action.add_precondition(GE(stack_amount, min_stack.quantity))

    def _task_to_goal(self, task: "Task"):
        if isinstance(task, GetItemTask):
            item = self.items_obj[task.item_stack.item]
            return GE(self.amount(item), task.item_stack.quantity)
        if isinstance(task, PlaceItemTask):
            item = self.zone_items_obj[task.item_stack.item]
            zones = self.zones_obj.keys()
            if task.zone is not None:
                zones = [task.zone]
            conditions = [
                GE(
                    self.amount_at(item, self.zones_obj[zone]),
                    task.item_stack.quantity,
                )
                for zone in zones
            ]
            if len(conditions) == 1:
                return conditions[0]
            return OR(*conditions)
        if isinstance(task, GoToZoneTask):
            return self.visited(self.zones_obj[task.zone])
        raise NotImplementedError

    def _purpose_to_goal(self, purpose: "Purpose"):
        # Individual tasks goals
        goals = {}
        for task in purpose.tasks:
            goals[task] = self._task_to_goal(task)

        # We only consider the best terminal group goal
        return AND(*[goals[task] for task in purpose.best_terminal_group.tasks])


def _read_statistics(results: "PlanGenerationResult") -> Statistics:
    if results.engine_name == "SAT-enhsp":
        return _read_enhsp_stats(results)
    elif results.engine_name == "aries":
        return _read_aries_stats(results)
    elif results.engine_name == "lpg":
        return _read_lpg_stats(results)
    raise NotImplementedError(
        "Cannot read statistics for engine %s", results.engine_name
    )


def _read_lpg_stats(results: "PlanGenerationResult"):
    metric = results.metrics if results.metrics is not None else {}
    statistic_logs = results.log_messages[0].message.split("\n\n")[-1].split("\r\n")

    solution_metrics_paragraph = False
    for stat_log in statistic_logs:
        stat_log = stat_log.replace("\r", "")
        name_and_value = stat_log.split(":")
        if name_and_value[0].strip() == "Solution number":
            solution_metrics_paragraph = True
        elif not solution_metrics_paragraph:
            continue
        elif name_and_value[0].strip() == "Plan file":
            solution_metrics_paragraph = False
            continue
        try:
            metric[name_and_value[0]] = int(name_and_value[1])
        except ValueError:
            metric[name_and_value[0]] = float(name_and_value[1])
    return metric


def _read_aries_stats(results: "PlanGenerationResult"):
    return results.metrics


def _read_enhsp_stats(results: "PlanGenerationResult"):
    statistic_logs = results.log_messages[0].message.split("\n\n")[-1].split("\n")
    stats = {}
    for stat_log in statistic_logs:
        stat_log = stat_log.replace("\r", "")
        name_and_value = stat_log.split(":")
        if len(name_and_value) != 2:
            continue
        try:
            stats[name_and_value[0]] = int(name_and_value[1])
        except ValueError:
            stats[name_and_value[0]] = float(name_and_value[1])
    return stats
