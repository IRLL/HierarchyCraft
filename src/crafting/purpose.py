from typing import Union, List

import numpy as np

from crafting.world import World
from crafting.task import Task


class Purpose:
    """A purpose for a Crafting player based on a list of tasks."""

    def __init__(self, tasks: Union[Task, List[Task]]) -> None:
        if isinstance(tasks, Task):
            tasks = [tasks]
        self.tasks = tasks
        self.task_has_ended = {task: False for task in self.tasks}

    def build(self, world: World):
        """
        Builds the purpose of the player based on the given world.
        """
        for task in self.tasks:
            task.build(world)

    def reward(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> float:
        """
        Returns the purpose reward for the given state based on tasks.
        """
        reward = 0.0
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
        for task in self.tasks:
            if not self.task_has_ended[task] and task.is_terminal(
                player_inventory, position, zones_inventory
            ):
                self.task_has_ended[task] = True
        return all(self.task_has_ended.values())
