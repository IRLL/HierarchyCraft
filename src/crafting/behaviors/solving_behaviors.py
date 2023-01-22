from typing import TYPE_CHECKING, Dict

from crafting.constants import ActionTypes
from crafting.behaviors.behaviors import GetItem, ReachZone


if TYPE_CHECKING:
    from crafting.world.world import World


def build_all_solving_behaviors(world: "World") -> Dict[str, "Behavior"]:
    """Return a dictionary of handcrafted behaviors to get each item, zone and property."""
    all_behaviors = {}
    all_behaviors = _reach_zones_behaviors(world, all_behaviors)
    all_behaviors = _search_item_behaviors(world, all_behaviors)
    all_behaviors = _craft_item_behaviors(world, all_behaviors)
    return all_behaviors


def _reach_zones_behaviors(world: "World", all_behaviors: Dict[str, "Behavior"]):
    for zone in world.zones:
        zone_behavior = ReachZone(zone, world)
        all_behaviors[str(zone_behavior)] = zone_behavior
    return all_behaviors


def _search_item_behaviors(world: "World", all_behaviors: Dict[str, "Behavior"]):
    for item in world.foundable_items:
        zones_id_needed = []
        for zone in world.zones:
            if item.item_id in zone.items:
                zones_id_needed.append(zone.zone_id)

        items_needed = []
        if item.required_tools is not None:
            for tool in item.required_tools:
                crafting_behavior = [(tool.item_id, 1)] if tool is not None else None
                items_needed.append(crafting_behavior)

        dropped_items = [item]

        if hasattr(item, "items_dropped"):
            dropped_items = item.items_dropped
        for dropped_item in dropped_items:
            item_behavior = GetItem(
                world=world,
                item=dropped_item,
                all_behaviors=all_behaviors,
                items_needed=items_needed,
                last_action=(ActionTypes.SEARCH, item.item_id),
                zones_id_needed=zones_id_needed,
            )
        all_behaviors[str(item_behavior)] = item_behavior

    return all_behaviors


def _craft_item_behaviors(world: "World", all_behaviors: Dict[str, "Behavior"]):
    for recipe in world.recipes:

        items_needed = [
            [(itemstack.item_id, itemstack.size) for itemstack in recipe.inputs]
        ]

        if recipe.outputs is not None:
            for output in recipe.outputs:
                recipe_behavior = GetItem(
                    world=world,
                    item=output.item,
                    all_behaviors=all_behaviors,
                    items_needed=items_needed,
                    zones_properties_needed=recipe.needed_properties,
                    last_action=(ActionTypes.CRAFT, recipe.recipe_id),
                )
                all_behaviors[str(recipe_behavior)] = recipe_behavior

        if recipe.added_properties is not None:
            for zone_property in recipe.added_properties:
                zone_property_behavior = GetItem(
                    world=world,
                    item=zone_property,
                    all_behaviors=all_behaviors,
                    items_needed=items_needed,
                    zones_properties_needed=recipe.needed_properties,
                    last_action=(ActionTypes.CRAFT, recipe.recipe_id),
                )
                all_behaviors[str(zone_property_behavior)] = zone_property_behavior

    return all_behaviors
