# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Crafting : A gym environment for inventory managment """

from crafting.env import CraftingEnv
from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.examples.random.env import RandomCraftingEnv
from crafting.task import Task

try:
    import gym

    # Simple MineCrafting with no reward, only penalty on illegal actions
    gym.register(
        id="MineCrafting-NoReward-v1",
        entry_point="crafting.examples.minecraft.env:MineCraftingEnv",
        kwargs={
            "fail_penalty": 1,
            "timestep_penalty": 0,
            "moving_penalty": 0,
        },
    )

    gym.register(
        id="MineCrafting-EnchantingTable-v1",
        entry_point="crafting.examples.minecraft.env:MineCraftingEnv",
        kwargs={
            "tasks": ["obtain_enchanting_table"],
            "fail_penalty": 1,
            "timestep_penalty": 0.1,
            "moving_penalty": 0.4,
        },
    )

    gym.register(
        id="RandomCrafting-v1",
        entry_point="crafting.examples.random.env:RandomCraftingEnv",
        kwargs={
            "n_tools": 0,
            "n_findables": 1,
            "n_required_tools": [1.0],
            "n_inputs_per_craft": [0.1, 0.6, 0.3],
        },
    )

    gym.register(
        id="RecursiveCrafting-v1",
        entry_point="crafting.examples.simple.recursive:RecursiveCraftingEnv",
    )

    gym.register(
        id="TowerCrafting-v1",
        entry_point="crafting.examples.simple.tower:TowerCraftingEnv",
    )

except ImportError:
    pass
