from crafting.render.render import render_env_with_human
from crafting.examples.minecraft.env import MineCraftingEnv

env = MineCraftingEnv(
    verbose=1,
    max_step=50,
    tasks=["obtain_enchanting_table"],
    tasks_can_end=[True],
)

render_env_with_human(env)
