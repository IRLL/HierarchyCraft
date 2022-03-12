from crafting.render.render import render_env_with_human
from crafting.examples.random.env import RandomCraftingEnv

env = RandomCraftingEnv(
    n_items=12,
    n_tools=2,
    n_foundables=5,
    n_required_tools=[0.25, 0.4, 0.2, 0.1, 0.05],
    n_inputs_per_craft=[0.1, 0.6, 0.3],
    n_zones=1,
    tasks=["obtain_random_item"],
    tasks_can_end=[True],
)

render_env_with_human(env)
