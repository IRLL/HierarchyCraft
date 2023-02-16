"""#Crafting environement examples.

Here is the table of available Crafting environments examples.

If you built one of your own, send us a pull request so we can add it to the list!

| Gym name                    | CLI name          |Interest                                              | Reference                               | 
|:----------------------------|:------------------|:-----------------------------------------------------|:----------------------------------------|
| "MineCrafting-Dragon-v1"    | `minecraft`       | Complex real-case hierarchies.                       |`crafting.examples.minecraft`            |
| "TowerCrafting-v1"          | `tower`           | Polynomial growth with reuse hierarchies.            |`crafting.examples.tower`                |
| "RecursiveCrafting-v1"      | `recursive`       | Exponential growth with reuse hierarchies.           |`crafting.examples.recursive`            |
| "LightRecursiveCrafting-v1" | `light-recursive` | Exponential (smaller) growth with reuse hierarchies. |`crafting.examples.recursive`            |
| "RandomCrafting-v1"         | `random`          | Random hierarchical structures.                      |`crafting.examples.random_simple`        |
| "KeyDoorCrafting-v1"        | `keydoor`         | Gridworld like structure.                            |`crafting.examples.keydoor`              |

"""

from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.examples.random_simple import RandomCraftingEnv
from crafting.examples.recursive import RecursiveCraftingEnv, LightRecursiveCraftingEnv
from crafting.examples.tower import TowerCraftingEnv
from crafting.examples.keydoor import KeyDoorCraftingEnv
