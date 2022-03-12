# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""Main module for MineCrafting environment."""

from crafting.render.render import render_env_with_human
from crafting.examples.minecraft.env import MineCraftingEnv

env = MineCraftingEnv(
    verbose=1,
    max_step=50,
    tasks=["obtain_enchanting_table"],
    tasks_can_end=[True],
)

render_env_with_human(env)
