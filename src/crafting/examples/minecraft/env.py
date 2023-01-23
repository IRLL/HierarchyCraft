# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=arguments-differ, inconsistent-return-statements

""" MineCrafting Environment

Crafting environment adapted to the Minecraft inventory

"""

from crafting.env import CraftingEnv
from crafting.examples.minecraft.abc import McPlayer
from crafting.examples.minecraft.world import McWorld


class MineCraftingEnv(CraftingEnv):

    """MineCrafting Environment"""

    def __init__(self, **kwargs):
        """A minecraft-like Crafting Environment.

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
        self.metadata["video.frames_per_second"] = kwargs.pop("fps", 10)

        super().__init__(name="MineCrafting", world=world, player=player, **kwargs)
