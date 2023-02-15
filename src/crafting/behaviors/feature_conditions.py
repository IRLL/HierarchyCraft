""" Module to define FeatureCondition nodes for the HEBGraph of the Crafting environment. """

from typing import TYPE_CHECKING

import numpy as np
from hebg import FeatureCondition

from crafting.render.utils import load_or_create_image

if TYPE_CHECKING:
    from crafting.env import CraftingEnv
    from crafting.world import ItemStack, Zone


class HasItemStack(FeatureCondition):

    """FeatureCondition to check if player has an Item in a given quantity."""

    def __init__(self, itemstack: "ItemStack", env: "CraftingEnv") -> None:
        quantity = itemstack.quantity
        conditon_text = f" {quantity}" if quantity > 1 else ""
        name = f"Has{conditon_text} {itemstack.item.name}?"
        image = load_or_create_image(itemstack, env.resources_path)
        super().__init__(name=name, image=np.array(image), complexity=1)

        self.itemstack = itemstack
        self.n_items = env.world.n_items
        self.slot = env.world.items.index(itemstack.item)

    def __call__(self, observation) -> int:
        inventory_content = observation[: self.n_items]
        return inventory_content[self.slot] >= self.itemstack.quantity


class IsInZone(FeatureCondition):

    """FeatureCondition to check if player is in a Zone."""

    def __init__(self, zone: "Zone", env: "CraftingEnv") -> None:
        name = f"Is in {zone.name}?"
        image = load_or_create_image(zone, env.resources_path)
        super().__init__(name=name, image=image, complexity=1)

        self.n_items = env.world.n_items
        self.n_zones = env.world.n_zones
        self.zone = zone
        self.slot = env.world.slot_from_zone(zone)

    def __call__(self, observation) -> int:
        position = observation[self.n_items : self.n_items + self.n_zones]
        return position[self.slot] == 1


class HasZoneItem(FeatureCondition):

    """FeatureCondition to check if a Zone has the given property."""

    def __init__(self, itemstack: "ItemStack", env: "CraftingEnv") -> None:
        name = f"Current zone has item {itemstack.item.name}?"
        image = np.array(load_or_create_image(itemstack, env.resources_path))
        super().__init__(name=name, image=image, complexity=1)

        self.itemstack = itemstack
        self.n_items = env.world.n_items
        self.n_zones = env.world.n_zones
        self.slot = env.world.zones_items.index(itemstack.item)

    def __call__(self, observation) -> int:
        zone_items = observation[self.n_items + self.n_zones :]
        return zone_items[self.slot] >= self.itemstack.quantity
