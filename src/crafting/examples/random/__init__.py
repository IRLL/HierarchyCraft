# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

# gym is an optional dependency
try:
    import gym

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
except ImportError:
    pass
