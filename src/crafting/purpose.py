from typing import TYPE_CHECKING, Union, List, Dict, Optional
from enum import Enum

import numpy as np

from crafting.task import Task, GetItemTask, GoToZoneTask

if TYPE_CHECKING:
    from crafting.env import CraftingEnv
    from crafting.world import World


class RewardShaping(Enum):
    NONE = "none"
    ALL_ACHIVEMENTS = "all"
    REQUIRED_ACHIVEMENTS = "required"
    TRANSFORMATION_INPUTS_ACHIVEMENT = "inputs"


class Purpose:
    """A purpose for a Crafting player based on a list of tasks."""

    def __init__(
        self,
        tasks: Optional[Union[Task, List[Task]]] = None,
        timestep_reward: float = 0.0,
        default_reward_shaping: RewardShaping = RewardShaping.NONE,
    ) -> None:
        """A purpose for a Crafting player based on a list of tasks.

        Args:
            tasks (Union[Task, List[Task]], optional): Tasks to add to the Purpose.
                Defaults to None.
            timestep_reward (float, optional): Reward for each timestep.
                Defaults to 0.0.
            default_reward_shaping (RewardShaping, optional): Default reward shaping for tasks.
                Defaults to RewardShaping.NONE.
        """
        self.tasks: List[Task] = []
        self.timestep_reward = timestep_reward
        self.default_reward_shaping = default_reward_shaping

        self.task_has_ended: Dict[Task, bool] = {}
        self.reward_shaping: Dict[Task, RewardShaping] = {}

        if isinstance(tasks, Task):
            tasks = [tasks]
        elif tasks is None:
            tasks = []
        for task in tasks:
            self.add_task(task, default_reward_shaping)

    def add_task(self, task: Task, reward_shaping: Optional[RewardShaping] = None):
        """Add a new task to the purpose.

        Args:
            task (Task): Task to be added to the purpose.
            reward_shaping (Optional[RewardShaping], optional): Reward shaping for this task.
                Defaults to purpose's default reward shaping.
        """
        if reward_shaping is None:
            reward_shaping = self.default_reward_shaping
        reward_shaping = RewardShaping(reward_shaping)
        self.task_has_ended[task] = False
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
        return all(self.task_has_ended.values())

    def _add_reward_shaping_subtasks(
        self, task: Task, env: "CraftingEnv", reward_shaping: RewardShaping
    ) -> List[Task]:
        if reward_shaping == RewardShaping.NONE:
            return []
        if reward_shaping == RewardShaping.ALL_ACHIVEMENTS:
            return [GetItemTask(item, reward=1.0) for item in env.world.items]

        raise NotImplementedError
