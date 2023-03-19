"""# MineCrafting: Inspired from the popular game Minecraft.

![MineCrafting demo](../../../../docs/images/MineCrafting_human_demo.gif)

![MineCrafting hierarchy](../../../../docs/images/minecrafting_crafts_hierarchy.png)

"""
from typing import Optional

import crafting.examples.minecraft.items as items
from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.purpose import Purpose, RewardShaping, platinium_purpose
from crafting.task import GetItemTask

# gym is an optional dependency
try:
    import gym

    ENV_PATH = "crafting.examples.minecraft.env:MineCraftingEnv"

    # Simple MineCrafting with no reward, only penalty on illegal actions
    gym.register(
        id="MineCrafting-NoReward-v1",
        entry_point=ENV_PATH,
        kwargs={"purpose": None},
    )

    # Get all items, place all zones_items and go everywhere
    gym.register(
        id="MineCrafting-v1",
        entry_point=ENV_PATH,
        kwargs={"purpose": platinium_purpose(MineCraftingEnv().world)},
    )

    def _to_camel_case(name: str):
        return "".join([subname.capitalize() for subname in name.split("_")])

    def _register_minecrafting_single_item(
        item: items.Item,
        name: Optional[str] = None,
        success_reward: float = 10.0,
        timestep_reward: float = -0.1,
        reward_shaping: RewardShaping = RewardShaping.REQUIREMENTS_ACHIVEMENTS,
        version: int = 1,
    ):
        purpose = Purpose(timestep_reward=timestep_reward)
        purpose.add_task(
            GetItemTask(item, reward=success_reward),
            reward_shaping=reward_shaping,
        )
        if name is None:
            name = _to_camel_case(item.name)
        gym.register(
            id=f"MineCrafting-{name}-v{version}",
            entry_point=ENV_PATH,
            kwargs={"purpose": purpose},
        )

    _register_minecrafting_single_item(items.DIRT)
    _register_minecrafting_single_item(items.COBBLESTONE, name="Stone")
    _register_minecrafting_single_item(items.IRON_INGOT, name="Iron")
    _register_minecrafting_single_item(items.DIAMOND)
    _register_minecrafting_single_item(items.ENCHANTING_TABLE)
    _register_minecrafting_single_item(items.ENDER_DRAGON_HEAD, name="Dragon")


except ImportError:
    pass
