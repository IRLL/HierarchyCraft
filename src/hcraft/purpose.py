"""# Purpose in HierarchyCraft

**Every** hcraft environments are sandbox environments
and do not have a precise purpose by default.
But of course, purpose can be added in **any** HierarchyCraft environment
by setting up one or multiple tasks.

Tasks can be one of:
* Get the given item: `hcraft.task.GetItemTask`
* Go to the given zone: `hcraft.task.GoToZoneTask`
* Place the given item in the given zone (or any zone if none given): `hcraft.task.PlaceItemTask`


## Single task purpose

When a single task is passed to a HierarchyCraft environment, it will automaticaly build a purpose.
Then the environment will terminates if the task is completed.

Let's take an example on the MineHcraft environment.
(This is still work on any other HierarchyCraft environment)
```python
from hcraftort MineHcraftv
from hcraft.purpose import GetItemTask
from hcraft.examples.minecraft.items import DIAMOND

get_diamond = GetItemTask(DIAMOND, reward=10)
env = MineHcraftEnv(purpose=get_diamond)
```

## Reward shaping

Achievement tasks only rewards the player when completed. But this long term feedback is known
to be challenging. To ease learning such tasks, HierarchyCraft Purpose can generate substasks to give
intermediate feedback, this process is also known as reward shaping.
See `hcraft.purpose.RewardShaping` for more details.

For example, let's add the "required" reward shaping to the get_diamond task:

```python
from hcraftort MineHcraftEnv
from hcraft.purpose import Purpose, GetItemTask
from hcraft.examples.minecraft.items import DIAMOND

get_diamond = GetItemTask(DIAMOND, reward=10)
purpose = Purpose(shaping_value=2)
purpose.add_task(get_diamond, reward_shaping="required")

env = MineHcraftEnv(purpose=purpose)
```

Then getting the IRON_INGOT item for the first time will give a reward of 2.0 to the player, because
IRON_INGOT is used to craft the IRON_PICKAXE that is itself used to get a DIAMOND.

## Multi-tasks and terminal groups

In a sandbox environment, why limit ourselves to only one task ?
In HierarchyCraft, a purpose can be composed on multiple tasks.
But when does the purpose terminates ? When any task is done ? When all tasks are done ?

To solve this, we need to introduce terminal groups.
Terminal groups are represented with strings.

The purpose will terminate if ANY of the terminal groups have ALL its tasks done.

When adding a task to a purpose, one can choose one or multiple terminal groups like so:

```python
from hcraft import MineHcraftEnv
from hcraft.purpose import Purpose, GetItemTask, GoToZone
from hcraft.examples.minecraft.items import DIAMOND, GOLD_INGOT, EGG
from hcraft.examples.minecraft.zones import END

get_diamond = GetItemTask(DIAMOND, reward=10)
get_gold = GetItemTask(GOLD_INGOT, reward=5)
get_egg = GetItemTask(EGG, reward=100)
go_to_end = GoToZone(END, reward=20)

purpose = Purpose()
purpose.add_task(get_diamond, reward_shaping="required", terminal_groups="get rich!")
purpose.add_task(get_gold, terminal_groups=["golden end", "get rich!"])
purpose.add_task(go_to_end, reward_shaping="inputs", terminal_groups="golden end")
purpose.add_task(get_egg, terminal_groups=None)

env = MineHcraftEnv(purpose=purpose)
```

Here the environment will terminate if the player gets both diamond
and gold_ingot items ("get rich!" group) or if the player gets a gold_ingot
and reaches the end zone ("golden end" group).
The task get_egg is optional and cannot terminate the purpose anyhow,
but it will still reward the player if completed.

Just like this last task, reward shaping subtasks are always optional.

"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Set, Union

import networkx as nx
import numpy as np

from hcraft.requirements import RequirementNode, req_node_name
from hcraft.task import GetItemTask, GoToZoneTask, PlaceItemTask, Task

if TYPE_CHECKING:
    from hcraft.elements import Item, Zone
    from hcraft.env import HcraftEnv, HcraftState
    from hcraft.world import World


class RewardShaping(Enum):
    """Enumeration of all reward shapings possible."""

    NONE = "none"
    """No reward shaping"""
    ALL_ACHIVEMENTS = "all"
    """All items and zones will be associated with an achievement subtask."""
    REQUIREMENTS_ACHIVEMENTS = "required"
    """All (recursively) required items and zones for the given task
    will be associated with an achievement subtask."""
    INPUTS_ACHIVEMENT = "inputs"
    """Items and zones consumed by any transformation solving the task
    will be associated with an achievement subtask."""


@dataclass
class TerminalGroup:
    """Terminal groups are groups of tasks that can terminate the purpose.

    The purpose will termitate if ANY of the terminal groups have ALL its tasks done.
    """

    name: str
    tasks: List[Task] = field(default_factory=list)

    @property
    def terminated(self) -> bool:
        """True if all tasks of the terminal group are terminated."""
        return all(task.terminated for task in self.tasks)

    def __eq__(self, other) -> bool:
        if isinstance(other, str):
            return self.name == other
        if isinstance(other, TerminalGroup):
            return self.name == other.name
        return False

    def __hash__(self) -> int:
        return self.name.__hash__()


class Purpose:
    """A purpose for a HierarchyCraft player based on a list of tasks."""

    def __init__(
        self,
        tasks: Optional[Union[Task, List[Task]]] = None,
        timestep_reward: float = 0.0,
        default_reward_shaping: RewardShaping = RewardShaping.NONE,
        shaping_value: float = 1.0,
    ) -> None:
        """
        Args:
            tasks: Tasks to add to the Purpose.
                Defaults to None.
            timestep_reward: Reward for each timestep.
                Defaults to 0.0.
            default_reward_shaping: Default reward shaping for tasks.
                Defaults to RewardShaping.NONE.
            shaping_value: Reward value used in reward shaping if any.
                Defaults to 1.0.
        """
        self.tasks: List[Task] = []
        self.timestep_reward = timestep_reward
        self.shaping_value = shaping_value
        self.default_reward_shaping = default_reward_shaping
        self.built = False

        self.reward_shaping: Dict[Task, RewardShaping] = {}
        self.terminal_groups: List[TerminalGroup] = []

        if isinstance(tasks, Task):
            tasks = [tasks]
        elif tasks is None:
            tasks = []
        for task in tasks:
            self.add_task(task, reward_shaping=default_reward_shaping)

        self._best_terminal_group = None

    def add_task(
        self,
        task: Task,
        reward_shaping: Optional[RewardShaping] = None,
        terminal_groups: Optional[Union[str, List[str]]] = "default",
    ):
        """Add a new task to the purpose.

        Args:
            task: Task to be added to the purpose.
            reward_shaping: Reward shaping for this task.
                Defaults to purpose's default reward shaping.
            terminal_groups: Purpose terminates when ALL the tasks of ANY terminal group terminates.
                If terminal groups is "" or None, task will be optional and will
                not allow to terminate the purpose at all.
                By default, tasks are added in the "default" group and hence
                ALL tasks have to be done to terminate the purpose.
        """
        if reward_shaping is None:
            reward_shaping = self.default_reward_shaping
        reward_shaping = RewardShaping(reward_shaping)
        if terminal_groups:
            if isinstance(terminal_groups, str):
                terminal_groups = [terminal_groups]
            for terminal_group in terminal_groups:
                existing_group = self._terminal_group_from_name(terminal_group)
                if not existing_group:
                    existing_group = TerminalGroup(terminal_group)
                    self.terminal_groups.append(existing_group)
                existing_group.tasks.append(task)

        self.reward_shaping[task] = reward_shaping
        self.tasks.append(task)

    def build(self, env: "HcraftEnv"):
        """
        Builds the purpose of the player relative to the given environment.

        Args:
            env: The HierarchyCraft environment to build upon.
        """
        if self.built:
            return

        if not self.tasks:
            return
        # Add reward shaping subtasks
        for task in self.tasks:
            subtasks = self._add_reward_shaping_subtasks(
                task, env, self.reward_shaping[task]
            )
            for subtask in subtasks:
                self.add_task(subtask, RewardShaping.NONE, terminal_groups=None)

        # Build all tasks
        for task in self.tasks:
            task.build(env.world)

        self.built = True

    def reward(self, state: "HcraftState") -> float:
        """
        Returns the purpose reward for the given state based on tasks.
        """
        reward = self.timestep_reward
        if not self.tasks:
            return reward
        for task in self.tasks:
            reward += task.reward(state)
        return reward

    def is_terminal(self, state: "HcraftState") -> bool:
        """
        Returns True if the given state is terminal for the whole purpose.
        """
        if not self.tasks:
            return False
        for task in self.tasks:
            task.is_terminal(state)
        for terminal_group in self.terminal_groups:
            if terminal_group.terminated:
                return True
        return False

    def reset(self) -> None:
        """Reset the purpose."""
        for task in self.tasks:
            task.reset()

    @property
    def optional_tasks(self) -> List[Task]:
        """List of tasks in no terminal group hence being optinal."""
        terminal_tasks = []
        for group in self.terminal_groups:
            terminal_tasks += group.tasks
        return [task for task in self.tasks if task not in terminal_tasks]

    @property
    def terminated(self) -> bool:
        """True if any of the terminal groups are terminated."""
        return any(
            all(task.terminated for task in terminal_group.tasks)
            for terminal_group in self.terminal_groups
        )

    @property
    def best_terminal_group(self) -> TerminalGroup:
        """Best rewarding terminal group."""
        if self._best_terminal_group is not None:
            return self._best_terminal_group

        best_terminal_group, best_terminal_value = None, -np.inf
        for terminal_group in self.terminal_groups:
            terminal_value = sum(task._reward for task in terminal_group.tasks)
            if terminal_value > best_terminal_value:
                best_terminal_value = terminal_value
                best_terminal_group = terminal_group

        self._best_terminal_group = best_terminal_group
        return best_terminal_group

    def _terminal_group_from_name(self, name: str) -> Optional[TerminalGroup]:
        if name not in self.terminal_groups:
            return None
        group_id = self.terminal_groups.index(name)
        return self.terminal_groups[group_id]

    def _add_reward_shaping_subtasks(
        self, task: Task, env: "HcraftEnv", reward_shaping: RewardShaping
    ) -> List[Task]:
        if reward_shaping == RewardShaping.NONE:
            return []
        if reward_shaping == RewardShaping.ALL_ACHIVEMENTS:
            return _all_subtasks(env.world, self.shaping_value)
        if reward_shaping == RewardShaping.INPUTS_ACHIVEMENT:
            return _inputs_subtasks(task, env.world, self.shaping_value)
        if reward_shaping == RewardShaping.REQUIREMENTS_ACHIVEMENTS:
            return _required_subtasks(task, env, self.shaping_value)
        raise NotImplementedError

    def __str__(self) -> str:
        terminal_groups_str = []
        for terminal_group in self.terminal_groups:
            tasks_str_joined = self._tasks_str(terminal_group.tasks)
            group_str = f"{terminal_group.name}:[{tasks_str_joined}]"
            terminal_groups_str.append(group_str)
        optional_tasks_str = self._tasks_str(self.optional_tasks)
        if optional_tasks_str:
            group_str = f"optional:[{optional_tasks_str}]"
            terminal_groups_str.append(group_str)
        joined_groups_str = ", ".join(terminal_groups_str)
        return f"Purpose({joined_groups_str})"

    def _tasks_str(self, tasks: List[Task]) -> str:
        tasks_str = []
        for task in tasks:
            shaping = self.reward_shaping[task]
            shaping_str = f"#{shaping.value}" if shaping != RewardShaping.NONE else ""
            tasks_str.append(f"{task}{shaping_str}")
        return ",".join(tasks_str)


def platinium_purpose(
    world: "World",
    success_reward: float = 10.0,
    timestep_reward: float = -0.1,
):
    purpose = Purpose(timestep_reward=timestep_reward)
    for item in world.items:
        purpose.add_task(GetItemTask(item, reward=success_reward))
    for zone in world.zones:
        purpose.add_task(GoToZoneTask(zone, reward=success_reward))
    for item in world.zones_items:
        purpose.add_task(PlaceItemTask(item, reward=success_reward))
    return purpose


def _all_subtasks(world: "World", shaping_reward: float) -> List[Task]:
    return _build_reward_shaping_subtasks(
        world.items, world.zones, world.zones_items, shaping_reward
    )


def _required_subtasks(
    task: Task, env: "HcraftEnv", shaping_reward: float
) -> List[Task]:
    relevant_items = set()
    relevant_zones = set()
    relevant_zone_items = set()

    if isinstance(task, GetItemTask):
        goal_item = task.item_stack.item
        goal_requirement_nodes = [req_node_name(goal_item, RequirementNode.ITEM)]
    elif isinstance(task, PlaceItemTask):
        goal_item = task.item_stack.item
        goal_requirement_nodes = [req_node_name(goal_item, RequirementNode.ZONE_ITEM)]
        goal_zones = task.zones if task.zones else []
        for zone in goal_zones:
            relevant_zones.add(zone)
            goal_requirement_nodes.append(req_node_name(zone, RequirementNode.ZONE))
    elif isinstance(task, GoToZoneTask):
        goal_requirement_nodes = [req_node_name(task.zone, RequirementNode.ZONE)]
    else:
        raise NotImplementedError(
            f"Unsupported reward shaping {RewardShaping.REQUIREMENTS_ACHIVEMENTS}"
            f"for given task type: {type(task)} of {task}"
        )

    requirements_acydigraph = env.world.requirements.acydigraph
    for requirement_node in goal_requirement_nodes:
        for ancestor in nx.ancestors(requirements_acydigraph, requirement_node):
            if ancestor == "START#":
                continue
            ancestor_node = requirements_acydigraph.nodes[ancestor]
            item_or_zone: Union["Item", "Zone"] = ancestor_node["obj"]
            ancestor_type = RequirementNode(ancestor_node["type"])
            if ancestor_type is RequirementNode.ITEM:
                relevant_items.add(item_or_zone)
            if ancestor_type is RequirementNode.ZONE:
                relevant_zones.add(item_or_zone)
            if ancestor_type is RequirementNode.ZONE_ITEM:
                relevant_zone_items.add(item_or_zone)
    return _build_reward_shaping_subtasks(
        relevant_items,
        relevant_zones,
        relevant_zone_items,
        shaping_reward,
    )


def _inputs_subtasks(task: Task, world: "World", shaping_reward: float) -> List[Task]:
    relevant_items = set()
    relevant_zones = set()
    relevant_zone_items = set()

    goal_zones = []
    goal_item = None
    goal_zone_item = None
    if isinstance(task, GetItemTask):
        goal_item = task.item_stack.item
    elif isinstance(task, GoToZoneTask):
        goal_zones = [task.zone]
    elif isinstance(task, PlaceItemTask):
        goal_zone_item = task.item_stack.item
        if task.zones:
            goal_zones = task.zones
            relevant_zones |= set(task.zones)
    else:
        raise NotImplementedError(
            f"Unsupported reward shaping {RewardShaping.INPUTS_ACHIVEMENT}"
            f"for given task type: {type(task)} of {task}"
        )
    transfo_giving_item = [
        transfo
        for transfo in world.transformations
        if goal_item in transfo.production("player")
        and goal_item not in transfo.min_required("player")
    ]
    transfo_placing_zone_item = [
        transfo
        for transfo in world.transformations
        if goal_zone_item in transfo.produced_zones_items
        and goal_zone_item not in transfo.min_required_zones_items
    ]
    transfo_going_to_any_zones = [
        transfo
        for transfo in world.transformations
        if transfo.destination is not None and transfo.destination in goal_zones
    ]
    relevant_transformations = (
        transfo_giving_item + transfo_placing_zone_item + transfo_going_to_any_zones
    )

    for transfo in relevant_transformations:
        relevant_items |= transfo.consumption("player")
        relevant_zone_items |= transfo.consumption("current_zone")
        relevant_zone_items |= transfo.consumption("destination")
        relevant_zone_items |= transfo.consumption("zones")
        if transfo.zones:
            relevant_zones |= set(transfo.zones)

    return _build_reward_shaping_subtasks(
        relevant_items,
        relevant_zones,
        relevant_zone_items,
        shaping_reward,
    )


def _build_reward_shaping_subtasks(
    items: Optional[Union[List["Item"], Set["Item"]]] = None,
    zones: Optional[Union[List["Zone"], Set["Zone"]]] = None,
    zone_items: Optional[Union[List["Item"], Set["Item"]]] = None,
    shaping_reward: float = 1.0,
) -> List[Task]:
    subtasks = []
    if items:
        subtasks += [GetItemTask(item, reward=shaping_reward) for item in items]
    if zones:
        subtasks += [GoToZoneTask(zone, reward=shaping_reward) for zone in zones]
    if zone_items:
        subtasks += [PlaceItemTask(item, reward=shaping_reward) for item in zone_items]
    return subtasks
