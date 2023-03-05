"""#Crafting environement examples.

Here is the table of available Crafting environments examples.

If you built one of your own, send us a pull request so we can add it to the list!

| Gym name                    | CLI name          | Reference                               |
|:----------------------------|:------------------|:----------------------------------------|
| "MineCrafting-v1"           | `minecraft`       |`crafting.examples.minecraft`            |
| "TowerCrafting-v1"          | `tower`           |`crafting.examples.tower`                |
| "RecursiveCrafting-v1"      | `recursive`       |`crafting.examples.recursive`            |
| "LightRecursiveCrafting-v1" | `light-recursive` |`crafting.examples.recursive`            |
| "RandomCrafting-v1"         | `random`          |`crafting.examples.random_simple`        |
| "KeyDoorCrafting-v1"        | `keydoor`         |`crafting.examples.keydoor`              |

"""

import crafting.examples.keydoor as keydoor
import crafting.examples.minecraft as minecraft
import crafting.examples.random_simple as random_simple
import crafting.examples.recursive as recursive
import crafting.examples.tower as tower

from crafting.examples.keydoor import KeyDoorCraftingEnv
from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.examples.random_simple import RandomCraftingEnv
from crafting.examples.recursive import LightRecursiveCraftingEnv, RecursiveCraftingEnv
from crafting.examples.tower import TowerCraftingEnv

__all__ = [
    "keydoor",
    "minecraft",
    "random_simple",
    "recursive",
    "tower",
    "KeyDoorCraftingEnv",
    "MineCraftingEnv",
    "RandomCraftingEnv",
    "LightRecursiveCraftingEnv",
    "RecursiveCraftingEnv",
    "TowerCraftingEnv",
]
