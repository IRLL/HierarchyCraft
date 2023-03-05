"""# MineCrafting: Inspired from the popular game Minecraft.

![MineCrafting demo](../../../../docs/images/MineCrafting_human_demo.gif)

![MineCrafting hierarchy](../../../../docs/images/minecrafting_crafts_hierarchy.png)

"""
from typing import Optional

from crafting.env import CraftingEnv
from crafting.examples.minecraft.env import MineCraftingEnv
import crafting.examples.minecraft.items as items
from crafting.purpose import Purpose, RewardShaping
from crafting.task import GetItemTask, GoToZoneTask, PlaceItemTask

# gym is an optional dependency
try:
    import gym

    ENV_PATH = "crafting.examples.minecraft.env:MineCraftingEnv"

    # Simple MineCrafting with no reward, only penalty on illegal actions
    gym.register(
        id="MineCrafting-NoReward-v1",
        entry_point=ENV_PATH,
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

    def _register_platinium(
        env: "CraftingEnv",
        env_path: str,
        success_reward: float = 10.0,
        timestep_reward: float = -0.1,
        version: int = 1,
    ):
        purpose = Purpose(timestep_reward=timestep_reward)
        for item in env.world.items:
            purpose.add_task(GetItemTask(item, reward=success_reward))
        for zone in env.world.zones:
            purpose.add_task(GoToZoneTask(zone, reward=success_reward))
        for item in env.world.zones_items:
            purpose.add_task(PlaceItemTask(item, reward=success_reward))
        gym.register(
            id=f"{env.name}-v{version}",
            entry_point=env_path,
            kwargs={"purpose": purpose},
        )

    _register_minecrafting_single_item(items.DIRT)
    _register_minecrafting_single_item(items.COBBLESTONE, name="Stone")
    _register_minecrafting_single_item(items.IRON_INGOT, name="Iron")
    _register_minecrafting_single_item(items.DIAMOND)
    _register_minecrafting_single_item(items.ENCHANTING_TABLE)
    _register_minecrafting_single_item(items.ENDER_DRAGON_HEAD, name="Dragon")
    _register_platinium(env=MineCraftingEnv(), env_path=ENV_PATH)


except ImportError:
    pass
