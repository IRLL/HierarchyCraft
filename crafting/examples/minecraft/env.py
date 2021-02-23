# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" MineCrafting Environment

Crafting environment adapted to the Minecraft inventory

"""

from crafting.env import CraftingEnv

from crafting.examples.minecraft.abc import McPlayer
from crafting.examples.minecraft.world import McWorld

class MineCraftingEnv(CraftingEnv):

    """ MineCrafting Environment """

    def __init__(self, max_step: int=500, verbose: int=0):
        world = McWorld()
        player = McPlayer(world)
        super().__init__(
            world=world,
            player=player,
            max_step=max_step,
            verbose=verbose
        )
