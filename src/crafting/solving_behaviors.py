from typing import TYPE_CHECKING, Dict

from hebg import Behavior

from crafting.task import Task, GetItemTask, GoToZoneTask, PlaceItemTask
from crafting.behaviors.behaviors import (
    AbleAndPerformTransformation,
    GetItem,
    GetZoneItem,
    ReachZone,
)

if TYPE_CHECKING:
    from crafting.env import CraftingEnv


def build_all_solving_behaviors(env: "CraftingEnv") -> Dict[str, "Behavior"]:
    """Return a dictionary of handcrafted behaviors to get each item, zone and property."""
    all_behaviors = {}
    all_behaviors = _reach_zones_behaviors(env, all_behaviors)
    all_behaviors = _get_item_behaviors(env, all_behaviors)
    all_behaviors = _get_zone_item_behaviors(env, all_behaviors)
    all_behaviors = _do_transfo_behaviors(env, all_behaviors)
    return all_behaviors


def task_to_behavior_name(task: Task) -> str:
    """Get the behavior name that will solve the given task.

    Args:
        task: Task to be solved.

    Raises:
        NotImplementedError: If task is not supported yet.

    Returns:
        str: Name of the solving behavior.
    """
    if isinstance(task, GetItemTask):
        behavior_name = GetItem.get_name(task.item_stack.item)
    elif isinstance(task, GoToZoneTask):
        behavior_name = ReachZone.get_name(task.zone)
    elif isinstance(task, PlaceItemTask):
        behavior_name = GetZoneItem.get_name(task.item_stack.item)
    else:
        raise NotImplementedError
    return behavior_name


def _reach_zones_behaviors(env: "CraftingEnv", all_behaviors: Dict[str, "Behavior"]):
    for zone in env.world.zones:
        behavior = ReachZone(zone, env, all_behaviors=all_behaviors)
        all_behaviors[behavior.name] = behavior
    return all_behaviors


def _get_item_behaviors(env: "CraftingEnv", all_behaviors: Dict[str, "Behavior"]):
    for item in env.world.items:
        behavior = GetItem(item, env, all_behaviors=all_behaviors)
        all_behaviors[behavior.name] = behavior
    return all_behaviors


def _get_zone_item_behaviors(env: "CraftingEnv", all_behaviors: Dict[str, "Behavior"]):
    for item in env.world.zones_items:
        behavior = GetZoneItem(item, env, all_behaviors=all_behaviors)
        all_behaviors[behavior.name] = behavior
    return all_behaviors


def _do_transfo_behaviors(env: "CraftingEnv", all_behaviors: Dict[str, "Behavior"]):
    for transfo in env.transformations:
        behavior = AbleAndPerformTransformation(
            env, transfo, all_behaviors=all_behaviors
        )
        all_behaviors[behavior.name] = behavior
    return all_behaviors
