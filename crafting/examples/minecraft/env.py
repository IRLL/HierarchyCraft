# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting Environment

Crafting environment adapted to the Minecraft inventory

"""

from crafting.env import CraftingEnv

from crafting.examples.minecraft.abc import McPlayer
from crafting.examples.minecraft.world import McWorld
from crafting.examples.minecraft.rendering import create_window, update_rendering

class MineCraftingEnv(CraftingEnv):

    """ MineCrafting Environment """

    def __init__(self, max_step: int=500, verbose: int=0):
        world = McWorld()
        player = McPlayer(world)
        self.render_variables = None
        super().__init__(
            world=world,
            player=player,
            max_step=max_step,
            verbose=verbose
        )

    def render(self, mode='human', frame_per_sec=60):
        if mode != 'human':
            return super().render(mode)
        if self.render_variables is None:
            self.render_variables = create_window(self.player.inventory)
        update_rendering(self.player, *self.render_variables, fps=frame_per_sec)
