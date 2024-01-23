"""#HierarchyCraft environement examples.

Here is the table of available HierarchyCraft environments examples.

If you built one of your own, send us a pull request so we can add it to the list!

| Gym name                         | CLI name          | Reference                                       |
|:---------------------------------|:------------------|:------------------------------------------------|
| MineHcraft-v1                    | `minecraft`       | `hcraft.examples.minecraft`                     |
| MiniHCraftEmpty-v1               | `minicraft`       | `hcraft.examples.minicraft.empty`               |
| MiniHCraftFourRooms-v1           | `minicraft`       | `hcraft.examples.minicraft.fourrooms`           |
| MiniHCraftMultiRoom-v1           | `minicraft`       | `hcraft.examples.minicraft.multiroom`           |
| MiniHCraftCrossing-v1            | `minicraft`       | `hcraft.examples.minicraft.crossing`            |
| MiniHCraftKeyCorridor-v1         | `minicraft`       | `hcraft.examples.minicraft.keycorridor`         |
| MiniHCraftDoorKey-v1             | `minicraft`       | `hcraft.examples.minicraft.doorkey`             |
| MiniHCraftUnlock-v1              | `minicraft`       | `hcraft.examples.minicraft.unlock`              |
| MiniHCraftUnlockPickup-v1        | `minicraft`       | `hcraft.examples.minicraft.unlockpickup`        |
| MiniHCraftBlockedUnlockPickup-v1 | `minicraft`       | `hcraft.examples.minicraft.unlockpickupblocked` |
| TowerHcraft-v1                   | `tower`           | `hcraft.examples.tower`                         |
| RecursiveHcraft-v1               | `recursive`       | `hcraft.examples.recursive`                     |
| LightRecursiveHcraft-v1          | `light-recursive` | `hcraft.examples.light_recursive`               |
| Treasure-v1                      | `treasure`        | `hcraft.examples.treasure`                      |
| RandomHcraft-v1                  | `random`          | `hcraft.examples.random_simple`                 |


"""


import hcraft.examples.minecraft as minecraft
import hcraft.examples.minicraft as minicraft
import hcraft.examples.random_simple as random_simple
import hcraft.examples.recursive as recursive
import hcraft.examples.light_recursive as light_recursive
import hcraft.examples.tower as tower
import hcraft.examples.treasure as treasure


from hcraft.examples.minecraft import MineHcraftEnv, MINEHCRAFT_GYM_ENVS
from hcraft.examples.minicraft import MINICRAFT_ENVS, MINICRAFT_GYM_ENVS
from hcraft.examples.recursive import RecursiveHcraftEnv
from hcraft.examples.light_recursive import LightRecursiveHcraftEnv
from hcraft.examples.tower import TowerHcraftEnv
from hcraft.examples.treasure import TreasureEnv
from hcraft.examples.random_simple import RandomHcraftEnv

EXAMPLE_ENVS = [
    MineHcraftEnv,
    *MINICRAFT_ENVS,
    TowerHcraftEnv,
    RecursiveHcraftEnv,
    LightRecursiveHcraftEnv,
    TreasureEnv,
    # RandomHcraftEnv,
]

HCRAFT_GYM_ENVS = [
    *MINEHCRAFT_GYM_ENVS,
    *MINICRAFT_GYM_ENVS,
    "TowerHcraft-v1",
    "RecursiveHcraft-v1",
    "LightRecursiveHcraft-v1",
    "Treasure-v1",
]


__all__ = [
    "minecraft",
    "minicraft",
    "recursive",
    "light_recursive",
    "tower",
    "treasure",
    "random_simple",
    "MineHcraftEnv",
    "RandomHcraftEnv",
    "LightRecursiveHcraftEnv",
    "RecursiveHcraftEnv",
    "TowerHcraftEnv",
]
