# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module to define Action nodes for the HEBGraph of the Crafting environment. """

from typing import TYPE_CHECKING

import numpy as np
from hebg import Action

from crafting.constants import ActionTypes
from crafting.render.utils import load_or_create_image

if TYPE_CHECKING:
    from crafting.world.items import Item
    from crafting.world.recipes import Recipe
    from crafting.world.world import World
    from crafting.world.zones import Zone


class SearchItem(Action):

    """Action to search to for an Item."""

    def __init__(self, item: "Item", world: "World") -> None:
        name = f"Search {item}"
        image = np.array(load_or_create_image(world, item))
        action = world.action(ActionTypes.SEARCH, item.item_id)
        super().__init__(action, name=name, image=image, complexity=1)
        self.item = item


class MoveToZone(Action):

    """Action to move to a Zone."""

    def __init__(self, zone: "Zone", world: "World") -> None:
        name = f"Move to {zone}"
        image = np.array(load_or_create_image(world, zone))
        action = world.action(ActionTypes.MOVE, zone.zone_id)
        super().__init__(action, name=name, image=image, complexity=1)
        self.zone = zone


class CraftRecipe(Action):

    """Action to use a Recipe."""

    def __init__(self, recipe: "Recipe", world: "World") -> None:
        name = f"Craft {recipe}"

        if recipe.outputs is not None:
            obj = recipe.outputs[0]
        else:
            obj = list(recipe.added_properties.keys())[0]

        image = np.array(load_or_create_image(world, obj))
        action = world.action(ActionTypes.CRAFT, recipe.recipe_id)
        super().__init__(action, name=name, image=image, complexity=1)
        self.recipe = recipe
