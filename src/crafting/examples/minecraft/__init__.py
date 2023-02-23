"""# MineCrafting: Inspired from the popular game Minecraft.

![MineCrafting demo](../../../../docs/images/MineCrafting_human_demo.gif)

![MineCrafting hierarchy](../../../../docs/images/minecrafting_crafts_hierarchy.png)

"""

from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.zones import *
from crafting.task import GetItemTask, GoToZoneTask, PlaceItemTask
from crafting.purpose import Purpose

# gym is an optional dependency
try:
    import gym

    ENV_PATH = "crafting.examples.minecraft.env:MineCraftingEnv"

    # Simple MineCrafting with no reward, only penalty on illegal actions
    gym.register(
        id="MineCrafting-NoReward-v1",
        entry_point=ENV_PATH,
    )

    # Get COBBLESTONE
    gym.register(
        id="MineCrafting-Stone-v1",
        entry_point=ENV_PATH,
        kwargs={
            "purpose": GetItemTask(COBBLESTONE, reward=10),
        },
    )

    # Get IRON_INGOT
    gym.register(
        id="MineCrafting-Iron-v1",
        entry_point=ENV_PATH,
        kwargs={
            "purpose": GetItemTask(IRON_INGOT, reward=10),
        },
    )

    # Get DIAMOND
    gym.register(
        id="MineCrafting-Diamond-v1",
        entry_point=ENV_PATH,
        kwargs={
            "purpose": GetItemTask(DIAMOND, reward=10),
        },
    )

    # Get ENCHANTING_TABLE
    gym.register(
        id="MineCrafting-EnchantingTable-v1",
        entry_point=ENV_PATH,
        kwargs={
            "purpose": GetItemTask(ENCHANTING_TABLE, reward=10),
        },
    )

    # Go to the END
    gym.register(
        id="MineCrafting-End-v1",
        entry_point=ENV_PATH,
        kwargs={
            "purpose": GoToZoneTask(END, reward=10),
        },
    )

    # Kill the ender dragon
    purpose = Purpose()
    purpose.add_task(
        GetItemTask(ENDER_DRAGON_HEAD, reward=100), reward_shaping="required"
    )
    gym.register(
        id="MineCrafting-Dragon-v1",
        entry_point=ENV_PATH,
        kwargs={
            "purpose": purpose,
        },
    )

    # Obtain all items
    env = MineCraftingEnv()
    purpose = Purpose(timestep_reward=-1)
    for item in env.world.items:
        purpose.add_task(GetItemTask(item, reward=10))
    for zone in env.world.zones:
        purpose.add_task(GoToZoneTask(zone, reward=10))
    for item in env.world.zones_items:
        purpose.add_task(PlaceItemTask(item, reward=10))
    gym.register(
        id="MineCrafting-Platinium-v1",
        entry_point=ENV_PATH,
        kwargs={
            "purpose": purpose,
        },
    )


except ImportError:
    pass
