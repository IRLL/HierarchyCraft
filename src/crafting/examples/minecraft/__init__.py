# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>


# gym is an optional dependency
try:
    import gym

    ENV_PATH = "crafting.examples.minecraft.env:MineCraftingEnv"

    # Simple MineCrafting with no reward, only penalty on illegal actions
    gym.register(
        id="MineCrafting-NoReward-v1",
        entry_point=ENV_PATH,
    )

except ImportError:
    pass
