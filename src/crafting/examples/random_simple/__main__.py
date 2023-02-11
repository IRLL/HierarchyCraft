"""Main module for RandomCrafting environment."""

from crafting.examples.random_simple.env import RandomCraftingEnv
from crafting.render.human import render_env_with_human

if __name__ == "__main__":
    env = RandomCraftingEnv(n_items_per_n_inputs={0: 1, 2: 10})
    render_env_with_human(env)
