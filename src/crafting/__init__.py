# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Crafting : A gym environment for inventory managment """

from crafting.env import CraftingEnv
from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.examples.random.env import RandomCraftingEnv
from crafting.task import Task

try:
    import gym

    gym.register(
        id="CraftingEnchantingTable-v1",
        entry_point="crafting.examples.minecraft.env:MineCraftingEnv",
        max_episode_steps=200,
        kwargs={"observe_legal_actions": False},
    )
except ImportError:
    pass
