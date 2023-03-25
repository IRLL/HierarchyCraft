"""# MineHcraft: Inspired from the popular game Minecraft.

![MineHcraft demo](../../../../docs/images/MineHcraft_human_demo.gif)

![MineHcraft hierarchy](../../../../docs/images/minehcraft_crafts_hierarchy.png)

"""
from typing import Optional

import hcraft.examples.minecraft.items as items
from hcraft.examples.minecraft.env import MineHcraftEnv
from hcraft.purpose import Purpose, RewardShaping, platinium_purpose
from hcraft.task import GetItemTask

MINEHCRAFT_GYM_ENVS = []

# gym is an optional dependency
try:
    import gym

    ENV_PATH = "hcraft.examples.minecraft.env:MineHcraftEnv"

    # Simple MineHcraft with no reward, only penalty on illegal actions
    gym.register(
        id="MineHcraft-NoReward-v1",
        entry_point=ENV_PATH,
        kwargs={"purpose": None},
    )
    MINEHCRAFT_GYM_ENVS.append("MineHcraft-NoReward-v1")

    # Get all items, place all zones_items and go everywhere
    gym.register(
        id="MineHcraft-v1",
        entry_point=ENV_PATH,
        kwargs={"purpose": platinium_purpose(MineHcraftEnv().world)},
    )
    MINEHCRAFT_GYM_ENVS.append("MineHcraft-v1")

    def _to_camel_case(name: str):
        return "".join([subname.capitalize() for subname in name.split("_")])

    def _register_minehcraft_single_item(
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
        gym_name = f"MineHcraft-{name}-v{version}"
        gym.register(
            id=gym_name,
            entry_point=ENV_PATH,
            kwargs={"purpose": purpose},
        )
        MINEHCRAFT_GYM_ENVS.append(gym_name)

    _register_minehcraft_single_item(items.WOOD)
    _register_minehcraft_single_item(items.COBBLESTONE, name="Stone")
    _register_minehcraft_single_item(items.IRON_INGOT, name="Iron")
    _register_minehcraft_single_item(items.DIAMOND)
    _register_minehcraft_single_item(items.ENCHANTING_TABLE)
    _register_minehcraft_single_item(items.ENDER_DRAGON_HEAD, name="Dragon")


except ImportError:
    pass
