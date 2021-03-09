# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=arguments-differ, inconsistent-return-statements

""" MineCrafting Environment

Crafting environment adapted to the Minecraft inventory

"""

from typing import List, Union

from crafting.env import CraftingEnv
from crafting.tasks.task import Task

from crafting.examples.minecraft.abc import McPlayer
from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.rendering import create_window, update_rendering
from crafting.examples.minecraft.tasks import TASKS

class MineCraftingEnv(CraftingEnv):

    """ MineCrafting Environment """

    def __init__(self, max_step: int=500, verbose: int=0,
            tasks: List[str]=None,
            tasks_weights: Union[list, dict]=None,
            tasks_can_end: Union[list, dict]=None
        ):
        world = McWorld()
        player = McPlayer(world)
        self.render_variables = None
        if tasks is not None:
            tasks = [self._get_tasks(task, world) for task in tasks]
        super().__init__(
            world=world,
            player=player,
            max_step=max_step,
            verbose=verbose,
            tasks=tasks,
            tasks_weights=tasks_weights,
            tasks_can_end=tasks_can_end
        )

    @staticmethod
    def _get_tasks(task, world):
        if isinstance(task, Task):
            return task
        if isinstance(task, str):
            task_class = TASKS[task.lower()]
            return task_class(world)
        raise TypeError(
            f'task should be str or Task instances but was {type(task)}'
        )

    def render(self, mode='human', frame_per_sec=60):
        if mode != 'human':
            return super().render(mode)
        if self.render_variables is None:
            self.render_variables = create_window(self)
        update_rendering(self, *self.render_variables, fps=frame_per_sec)
