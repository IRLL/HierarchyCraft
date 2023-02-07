from typing import TYPE_CHECKING, Union, List, Dict, Set, Optional
from enum import Enum

import numpy as np
import networkx as nx

from crafting.world import Item, Zone
from crafting.task import Task, GetItemTask, GoToZoneTask, PlaceItemTask
from crafting.requirement_graph import ReqNodesTypes, req_node_name

if TYPE_CHECKING:
    from crafting.env import CraftingEnv


class RewardShaping(Enum):
    NONE = "none"
    ALL_ACHIVEMENTS = "all"
    REQUIRED_ACHIVEMENTS = "required"
    INPUTS_ACHIVEMENT = "inputs"


class Purpose:
    """A purpose for a Crafting player based on a list of tasks."""

    def __init__(
        self,
        tasks: Optional[Union[Task, List[Task]]] = None,
        timestep_reward: float = 0.0,
        default_reward_shaping: RewardShaping = RewardShaping.NONE,
        shaping_reward: float = 1.0,
    ) -> None:
        """A purpose for a Crafting player based on a list of tasks.

        Args:
            tasks (Union[Task, List[Task]], optional): Tasks to add to the Purpose.
                Defaults to None.
            timestep_reward (float, optional): Reward for each timestep.
                Defaults to 0.0.
            default_reward_shaping (RewardShaping, optional): Default reward shaping for tasks.
                Defaults to RewardShaping.NONE.
            shaping_reward (float, optional): Reward value used in reward shaping if any.
                Defaults to 1.0.
        """
        self.tasks: List[Task] = []
        self.timestep_reward = timestep_reward
        self.shaping_reward = shaping_reward
        self.default_reward_shaping = default_reward_shaping

        self.task_has_ended: Dict[Task, bool] = {}
        self.reward_shaping: Dict[Task, RewardShaping] = {}
        self.terminal_groups: Dict[str, List[Task]] = {}

        if isinstance(tasks, Task):
            tasks = [tasks]
        elif tasks is None:
            tasks = []
        for task in tasks:
            self.add_task(task, reward_shaping=default_reward_shaping)

    def add_task(
        self,
        task: Task,
        reward_shaping: Optional[RewardShaping] = None,
        terminal_group: Optional[str] = "default",
    ):
        """Add a new task to the purpose.

        Args:
            task (Task): Task to be added to the purpose.
            reward_shaping (Optional[RewardShaping], optional): Reward shaping for this task.
                Defaults to purpose's default reward shaping.
            terminal_group: (Optional[str], optional): Purpose terminates when all the tasks of
                any terminal_group have been done.
                If terminal group is '' or None, task will be optional and will
                not allow to terminate the purpose at all.
                By default, tasks are added in the 'default' group and hence
                all tasks have to be done to terminate the purpose.
        """
        if reward_shaping is None:
            reward_shaping = self.default_reward_shaping
        reward_shaping = RewardShaping(reward_shaping)
        self.task_has_ended[task] = False
        if terminal_group:
            if terminal_group not in self.terminal_groups:
                self.terminal_groups[terminal_group] = []
            self.terminal_groups[terminal_group].append(task)
        self.reward_shaping[task] = reward_shaping
        self.tasks.append(task)

    def build(self, env: "CraftingEnv"):
        """
        Builds the purpose of the player based on the given world.
        """
        if not self.tasks:
            return
        # Add reward shaping subtasks
        for task in self.tasks:
            subtasks = self._add_reward_shaping_subtasks(
                task, env, self.reward_shaping[task]
            )
            for subtask in subtasks:
                self.add_task(subtask, RewardShaping.NONE)

        # Build all tasks
        for task in self.tasks:
            task.build(env.world)

    def reward(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> float:
        """
        Returns the purpose reward for the given state based on tasks.
        """
        reward = self.timestep_reward
        if not self.tasks:
            return reward
        for task in self.tasks:
            reward += task.reward(player_inventory, position, zones_inventory)
        return reward

    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        """
        Returns True if the state is terminal for the whole purpose.
        """
        if not self.tasks:
            return False
        for task in self.tasks:
            if not self.task_has_ended[task] and task.is_terminal(
                player_inventory, position, zones_inventory
            ):
                self.task_has_ended[task] = True
        for _terminal_group, group_tasks in self.terminal_groups.items():
            group_has_ended = all(self.task_has_ended[task] for task in group_tasks)
            if group_has_ended:
                return True
        return False

    def _add_reward_shaping_subtasks(
        self, task: Task, env: "CraftingEnv", reward_shaping: RewardShaping
    ) -> List[Task]:
        if reward_shaping == RewardShaping.NONE:
            return []
        if reward_shaping == RewardShaping.ALL_ACHIVEMENTS:
            return _all_subtasks(env)
        if reward_shaping == RewardShaping.INPUTS_ACHIVEMENT:
            return _inputs_subtasks(task, env, self.shaping_reward)
        if reward_shaping == RewardShaping.REQUIRED_ACHIVEMENTS:
            return _required_subtasks(task, env, self.shaping_reward)
        raise NotImplementedError


def _all_subtasks(env: "CraftingEnv") -> List[Task]:
    return _build_reward_shaping_subtasks(env.world.items, env.world.zones)


def _required_subtasks(
    task: Task, env: "CraftingEnv", shaping_reward: float
) -> List[Task]:
    relevant_items = set()
    relevant_zones = set()
    relevant_zone_items = set()

    if isinstance(task, GetItemTask):
        goal_item = task.item_stack.item
        goal_requirement_nodes = [req_node_name(goal_item, ReqNodesTypes.ITEM)]
    elif isinstance(task, PlaceItemTask):
        goal_item = task.item_stack.item
        goal_requirement_nodes = [req_node_name(goal_item, ReqNodesTypes.ZONE_ITEM)]
        goal_zones = task.zones if task.zones else []
        for zone in goal_zones:
            relevant_zones.add(zone)
            goal_requirement_nodes.append(req_node_name(zone, ReqNodesTypes.ZONE))
    elif isinstance(task, GoToZoneTask):
        goal_requirement_nodes = [req_node_name(task.zone, ReqNodesTypes.ZONE)]
    else:
        raise NotImplementedError(
            f"Unsupported reward shaping {RewardShaping.REQUIRED_ACHIVEMENTS}"
            f"for given task type: {type(task)} of {task}"
        )

    for requirement_node in goal_requirement_nodes:
        for ancestor in nx.ancestors(env.requirements_graph, requirement_node):
            ancestor_node = env.requirements_graph.nodes[ancestor]
            item_or_zone: Union[Item, Zone] = ancestor_node["obj"]
            ancestor_type = ReqNodesTypes(ancestor_node["type"])
            if ancestor_type is ReqNodesTypes.ITEM:
                relevant_items.add(item_or_zone)
            if ancestor_type is ReqNodesTypes.ZONE:
                relevant_zones.add(item_or_zone)
            if ancestor_type is ReqNodesTypes.ZONE_ITEM:
                relevant_zone_items.add(item_or_zone)
    return _build_reward_shaping_subtasks(
        relevant_items,
        relevant_zones,
        relevant_zone_items,
        shaping_reward,
    )


def _inputs_subtasks(
    task: Task, env: "CraftingEnv", shaping_reward: float
) -> List[Task]:
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
        for transfo in env.transformations
        if goal_item in transfo.produced_items
        and goal_item not in transfo.consumed_items
    ]
    transfo_placing_zone_item = [
        transfo
        for transfo in env.transformations
        if goal_zone_item in transfo.produced_zones_items
        and goal_zone_item not in transfo.consumed_zones_items
    ]
    transfo_going_to_any_zones = [
        transfo
        for transfo in env.transformations
        if transfo.destination is not None and transfo.destination in goal_zones
    ]
    relevant_transformations = (
        transfo_giving_item + transfo_placing_zone_item + transfo_going_to_any_zones
    )

    for transfo in relevant_transformations:
        relevant_items |= set(transfo.consumed_items)
        relevant_zone_items |= set(transfo.consumed_zones_items)
        if transfo.zones:
            relevant_zones |= set(transfo.zones)

    return _build_reward_shaping_subtasks(
        relevant_items,
        relevant_zones,
        relevant_zone_items,
        shaping_reward,
    )


def _build_reward_shaping_subtasks(
    items: Optional[Union[List[Item], Set[Item]]] = None,
    zones: Optional[Union[List[Zone], Set[Zone]]] = None,
    zone_items: Optional[Union[List[Item], Set[Item]]] = None,
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
