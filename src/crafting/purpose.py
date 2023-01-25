from typing import Union, List

from crafting.world import World
from crafting.task import Task


class Purpose:
    """A purpose for a Crafting player based on a list of tasks."""

    def __init__(self, tasks: Union[Task, List[Task]]) -> None:
        if isinstance(tasks, Task):
            tasks = [tasks]
        self.tasks = tasks

    def build(self, world: World):
        """Build the purpose of the player based on the given world."""
        for task in self.tasks:
            task.build(world)
