# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>


# gym is an optional dependency
try:
    import gym

    ENV_PATH = "crafting.examples.minecraft.env:MineCraftingEnv"

    # Simple MineCrafting with no reward, only penalty on illegal actions
    gym.register(
        id="MineCrafting-NoReward-v1",
        entry_point=ENV_PATH,
        kwargs={
            "fail_penalty": 1,
            "timestep_penalty": 0,
            "moving_penalty": 0,
        },
    )

    gym.register(
        id="MineCrafting-EnchantingTable-v1",
        entry_point=ENV_PATH,
        kwargs={
            "tasks": ["obtain_enchanting_table"],
            "fail_penalty": 1,
            "timestep_penalty": 0.1,
            "moving_penalty": 0.4,
        },
    )

    gym.register(
        id="MineCrafting-EnderDragon-v1",
        entry_point=ENV_PATH,
        kwargs={
            "tasks": ["obtain_ender_dragon_head"],
            "fail_penalty": 1,
            "timestep_penalty": 0.1,
            "moving_penalty": 0.4,
            "max_step": 300,
        },
    )
except ImportError:
    pass
