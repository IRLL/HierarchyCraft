"""#HierarchyCraft environement examples.

Here is the list of available HierarchyCraft environments examples.

If you built one of your own, send us a pull request so we can add it to the list!

##Minecraft inspired

See `hcraft.examples.minecraft` for more details.
[CLI keyword: `minecraft`]

| Gym name                         | Task description                                                       |
|:---------------------------------|:-----------------------------------------------------------------------|
| MineHcraft-NoReward-v1           | No task (Sandbox)                                                      |
| MineHcraft-Stone-v1              | Get the cobblestone item mining it with a wooden pickaxe               |
| MineHcraft-Iron-v1               | Get the iron-ingot item smelting raw ore gathered with a stone pickage |
| MineHcraft-Diamond-v1            | Get the diamond item mining it with an iron pickaxe                    |
| MineHcraft-EnchantingTable-v1    | Craft the enchanting table from a book, obsidian and diamonds          |
| MineHcraft-Dragon-v1             | Get the ender-dragon-head by killing it in the ender                   |
| MineHcraft-[name]-v1             | Get one of the Item of given `name` where Item is in env.world.items   |
| MineHcraft-v1                    | Get all items at least once                                            |


##Minigrid inspired

[CLI keyword: `minicraft`]

| Gym name                         | Documentation reference                         |
|:---------------------------------|:------------------------------------------------|
| MiniHCraftEmpty-v1               | `hcraft.examples.minicraft.empty`               |
| MiniHCraftFourRooms-v1           | `hcraft.examples.minicraft.fourrooms`           |
| MiniHCraftMultiRoom-v1           | `hcraft.examples.minicraft.multiroom`           |
| MiniHCraftCrossing-v1            | `hcraft.examples.minicraft.crossing`            |
| MiniHCraftKeyCorridor-v1         | `hcraft.examples.minicraft.keycorridor`         |
| MiniHCraftDoorKey-v1             | `hcraft.examples.minicraft.doorkey`             |
| MiniHCraftUnlock-v1              | `hcraft.examples.minicraft.unlock`              |
| MiniHCraftUnlockPickup-v1        | `hcraft.examples.minicraft.unlockpickup`        |
| MiniHCraftBlockedUnlockPickup-v1 | `hcraft.examples.minicraft.unlockpickupblocked` |

##Parametrised toy structures
| Gym name                         | CLI name          | Reference                                       |
|:---------------------------------|:------------------|:------------------------------------------------|
| TowerHcraft-v1                   | `tower`           | `hcraft.examples.tower`                         |
| RecursiveHcraft-v1               | `recursive`       | `hcraft.examples.recursive`                     |
| LightRecursiveHcraft-v1          | `light-recursive` | `hcraft.examples.light_recursive`               |

##Stochastic parametrised toy structures
| Gym name                         | CLI name          | Reference                                       |
|:---------------------------------|:------------------|:------------------------------------------------|
| RandomHcraft-v1                  | `random`          | `hcraft.examples.random_simple`                 |

##Other examples
| Gym name                         | CLI name          | Reference                                       |
|:---------------------------------|:------------------|:------------------------------------------------|
| Treasure-v1                      | `treasure`        | `hcraft.examples.treasure`                      |


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
