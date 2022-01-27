# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module to define Action nodes for the OptionGraph of the Crafting environment. """

from typing import TYPE_CHECKING
import numpy as np

from option_graph import Action

from crafting.render.utils import load_or_create_image

if TYPE_CHECKING:
    from crafting.world.items import Item
    from crafting.world.zones import Zone
    from crafting.world.world import World
    from crafting.world.recipes import Recipe


class SearchItem(Action):

    """Action to search to for an Item."""

    def __init__(self, item: "Item", world: "World") -> None:
        name = f"Search {item}"
        image = np.array(load_or_create_image(world, item))
        action = world.action("get", item.item_id)
        super().__init__(action, name=name, image=image)


class MoveToZone(Action):

    """Action to move to a Zone."""

    def __init__(self, zone: "Zone", world: "World") -> None:
        name = f"Move to {zone}"
        image = np.array(load_or_create_image(world, zone))
        action = world.action("move", zone.zone_id)
        super().__init__(action, name=name, image=image)


class CraftRecipe(Action):

    """Action to use a Recipe."""

    def __init__(self, recipe: "Recipe", world: "World") -> None:
        name = f"Craft {recipe}"

        if recipe.outputs is not None:
            obj = recipe.outputs[0]
        else:
            obj = list(recipe.added_properties.keys())[0]

        image = np.array(load_or_create_image(world, obj))
        action = world.action("craft", recipe.recipe_id)
        super().__init__(action, name=name, image=image)
