"""#HierarchyCraft environement examples.

Here is the table of available HierarchyCraft environments examples.

If you built one of your own, send us a pull request so we can add it to the list!

| Gym name                    | CLI name          | Reference                               |
|:----------------------------|:------------------|:----------------------------------------|
| "MineHcraft-v1"           | `minecraft`       |`hcraft.examples.minecraft`            |
| "TowerHcraft-v1"          | `tower`           |`hcraft.examples.tower`                |
| "RecursiveHcraft-v1"      | `recursive`       |`hcraft.examples.recursive`            |
| "LightRecursiveHcraft-v1" | `light-recursive` |`hcraft.examples.recursive`            |
| "RandomHcraft-v1"         | `random`          |`hcraft.examples.random_simple`        |

"""

import hcraft.examples.minecraft as minecraft
import hcraft.examples.minicraft as minicraft
import hcraft.examples.random_simple as random_simple
import hcraft.examples.recursive as recursive
import hcraft.examples.tower as tower

from hcraft.examples.minecraft import MineHcraftEnv, MINEHCRAFT_GYM_ENVS
from hcraft.examples.random_simple import RandomHcraftEnv
from hcraft.examples.recursive import LightRecursiveHcraftEnv, RecursiveHcraftEnv
from hcraft.examples.tower import TowerHcraftEnv
from hcraft.examples.minicraft import MINICRAFT_ENVS, MINICRAFT_GYM_ENVS

EXAMPLE_ENVS = [
    MineHcraftEnv,
    *MINICRAFT_ENVS,
    TowerHcraftEnv,
    RecursiveHcraftEnv,
    LightRecursiveHcraftEnv,
    # RandomHcraftEnv,
]

HCRAFT_GYM_ENVS = [
    *MINEHCRAFT_GYM_ENVS,
    *MINICRAFT_GYM_ENVS,
    "TowerHcraft-v1",
    "RecursiveHcraft-v1",
    "LightRecursiveHcraft-v1",
]


__all__ = [
    "minecraft",
    "minicraft",
    "recursive",
    "tower",
    "random_simple",
    "MineHcraftEnv",
    "RandomHcraftEnv",
    "LightRecursiveHcraftEnv",
    "RecursiveHcraftEnv",
    "TowerHcraftEnv",
]
