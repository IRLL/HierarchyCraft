"""# MineCrafting: Inspired from the popular game Minecraft.

![MineCrafting demo](../../../../docs/images/MineCrafting_human_demo.gif)

![MineCrafting hierarchy](../../../../docs/images/minecrafting_crafts_hierarchy.png)

"""

from crafting.env import CraftingEnv
from crafting.examples.minecraft.env import MineCraftingEnv
from crafting.examples.minecraft.items import *
from crafting.examples.minecraft.zones import *
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
        item: Item,
        name: Optional[str] = None,
        success_reward: float = 10.0,
        timestep_reward: float = -0.01,
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

    def _register_platinium(env: "CraftingEnv"):
        purpose = Purpose(timestep_reward=-1)
        for item in env.world.items:
            purpose.add_task(GetItemTask(item, reward=10))
        for zone in env.world.zones:
            purpose.add_task(GoToZoneTask(zone, reward=10))
        for item in env.world.zones_items:
            purpose.add_task(PlaceItemTask(item, reward=10))
        gym.register(
            id=f"{env.name}-Platinium-v1",
            entry_point=ENV_PATH,
            kwargs={"purpose": purpose},
        )

    _register_minecrafting_single_item(DIRT)
    _register_minecrafting_single_item(COBBLESTONE, name="Stone")
    _register_minecrafting_single_item(IRON_INGOT, name="Iron")
    _register_minecrafting_single_item(DIAMOND)
    _register_minecrafting_single_item(ENCHANTING_TABLE)
    _register_minecrafting_single_item(ENDER_DRAGON_HEAD, name="Dragon")
    _register_platinium(env=MineCraftingEnv())


except ImportError:
    pass
