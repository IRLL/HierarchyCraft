"""Main module for MineCrafting environment."""

from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.render.human import render_env_with_human

if __name__ == "__main__":
    env = MineCraftingEnv()
    render_env_with_human(env)
