# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=arguments-differ, inconsistent-return-statements

""" MineCrafting Environment

Crafting environment adapted to the Minecraft inventory

"""

import pygame

from crafting.env import CraftingEnv
from crafting.task import Task

from crafting.examples.minecraft.abc import McPlayer
from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.rendering import create_window, update_rendering
from crafting.examples.minecraft.tasks import TASKS

class MineCraftingEnv(CraftingEnv):

    """ MineCrafting Environment """

    def __init__(self, **kwargs):
        """ A minecraft-like Crafting Environment.

        Kwargs:
            max_step: The maximum number of steps until done.
            verbose: Verbosity level. {0: quiet, 1: print actions results}.
            observe_legal_actions: If True, add legal actions to observations.
            tasks: List of tasks.
            tasks_weights: Weight of tasks used for reward.
            tasks_can_end: Whether task can end the environment.
            tasks_early_stopping: If 'all', all task that can end have to be done to stop the
                environment. If 'any', any task that can end will stop the environment when done.
            fail_penalty: Reward penalty for each non-successful action.
            timestep_penalty: Reward penalty for each timestep.
            moving_penalty: Reward penalty for moving to an other zone.

        """
        world = McWorld()
        player = McPlayer(world)
        self.render_variables = None
        tasks = kwargs.pop('tasks', None)
        self.frame_per_sec = kwargs.pop('fps', 60)

        if tasks is not None:
            tasks = [self._get_tasks(task, world) for task in tasks]

        super().__init__(
            name='MineCrafting',
            world=world,
            player=player,
            tasks=tasks,
            **kwargs
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

    def render(self, mode='human'):
        if mode not in ('human', 'rgb_array'):
            return super().render(mode)
        if self.render_variables is None:
            self.render_variables = create_window(self)
        update_rendering(env=self, fps=self.frame_per_sec, **self.render_variables)
        if mode == 'rgb_array':
            rgb_array = pygame.surfarray.array3d(self.render_variables['screen'])
            return rgb_array.swapaxes(0, 1)
