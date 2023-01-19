# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""Main module for RandomCrafting environment."""

import gym

from crafting.examples.random.env import RandomCraftingEnv
from crafting.render.render import render_env_with_human

if __name__ == "__main__":
    env: RandomCraftingEnv = gym.make(
        "RandomCrafting-v1",
        verbose=1,
        n_items=12,
        n_tools=2,
        n_findables=5,
        n_zones=1,
        n_required_tools=[0.25, 0.4, 0.2, 0.1, 0.05],
        n_inputs_per_craft=[0.1, 0.6, 0.3],
    )
    render_env_with_human(env)
