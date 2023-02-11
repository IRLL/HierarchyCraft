"""#Crafting environement examples.

Here is the table of available Crafting environments examples.

If you built one of your own, send us a pull request so we can add it to the list!

| Environment name       | CLI name          |Interest                                              | Reference                               | 
|:-----------------------|:------------------|:-----------------------------------------------------|:----------------------------------------|
| MineCrafting           | `minecraft`       | Complex real-case hierarchies.                       |`crafting.examples.minecraft`            |
| TowerCrafting          | `tower`           | Polynomial growth with reuse hierarchies.            |`crafting.examples.tower`                |
| RecursiveCrafting      | `recursive`       | Exponential growth with reuse hierarchies.           |`crafting.examples.recursive`            |
| LightRecursiveCrafting | `light-recursive` | Exponential (smaller) growth with reuse hierarchies. |`crafting.examples.recursive`            |
| RandomCrafting         | `random`          | Random hierarchical structures.                      |`crafting.examples.random_simple`        |


"""

from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.examples.random_simple import RandomCraftingEnv
from crafting.examples.recursive import RecursiveCraftingEnv, LightRecursiveCraftingEnv
from crafting.examples.tower import TowerCraftingEnv
