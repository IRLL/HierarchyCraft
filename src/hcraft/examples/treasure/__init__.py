"""A simple environment used in for the env building tutorial:
[`hcraft.env`](https://irll.github.io/HierarchyCraft/hcraft/env.html)

Requirements graph:
<div class="graph">
.. include:: ../../../../docs/images/requirements_graphs/TreasureHcraft.html
</div>

"""

from hcraft.examples.treasure.env import TreasureEnv

__all__ = ["TreasureEnv"]

# gym is an optional dependency
try:
    import gym

    gym.register(
        id="Treasure-v1",
        entry_point="hcraft.examples.treasure.env:TreasureEnv",
    )


except ImportError:
    pass
