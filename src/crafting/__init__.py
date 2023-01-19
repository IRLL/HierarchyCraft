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

    gym.register(
        id="RandomCrafting-n10-v1",
        entry_point="crafting.examples.random.env:RandomCraftingEnv",
        max_episode_steps=200,
        kwargs={
            "n_items": 10,
            "n_tools": 0,
            "n_findables": 1,
            "n_required_tools": [1.0],
            "n_inputs_per_craft": [0.1, 0.6, 0.3],
        },
    )
except ImportError:
    pass
