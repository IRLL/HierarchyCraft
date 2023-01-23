# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""Main module for MineCrafting environment."""

import gym

from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.render.render import render_env_with_human

if __name__ == "__main__":
    env: MineCraftingEnv = gym.make("MineCrafting-EnderDragon-v1", verbose=1)
    render_env_with_human(env)
