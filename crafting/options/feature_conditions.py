# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Module to define FeatureCondition nodes for the OptionGraph of the Crafting environment. """

from typing import TYPE_CHECKING
import numpy as np

from option_graph import FeatureCondition

from crafting.render.utils import load_image

if TYPE_CHECKING:
    from crafting.world.items import Item
    from crafting.world.zones import Zone
    from crafting.world.world import World


class HasItem(FeatureCondition):

    """FeatureCondition to check if player has an Item in a given quantity."""

    def __init__(self, item: "Item", world: "World", quantity: int = 1) -> None:
        name = f"Has {quantity} {item}?"
        conditon_text = f"{quantity}" if quantity > 1 else ""
        image = np.array(load_image(world, item, text=conditon_text))
        super().__init__(name=name, image=image)

        self.world = world
        self.item = item
        self.quantity = quantity
        self.slot = self.world.item_id_to_slot[item.item_id]

    def __call__(self, observation) -> int:
        inventory_content = observation[: self.world.n_items]
        return inventory_content[self.slot] >= self.quantity


class IsInZone(FeatureCondition):

    """FeatureCondition to check if in a Zone."""

    def __init__(self, zone: "Zone", world: "World") -> None:
        name = f"Is in {zone}?"
        image = np.array(load_image(world, zone))
        super().__init__(name=name, image=image)

        self.world = world
        self.zone = zone
        self.slot = self.world.zone_id_to_slot[zone.zone_id]

    def __call__(self, observation) -> int:
        actual_zone_id = self.world.zone_id_from_observation(observation)
        return actual_zone_id == self.zone.zone_id


class HasProperty(FeatureCondition):

    """FeatureCondition to check if a Zone has the given property."""

    def __init__(self, prop: str, world: "World") -> None:
        name = f"Has property '{prop}' ?"
        image = np.array(load_image(world, prop))
        super().__init__(name=name, image=image)

        self.world = world
        self.prop = prop

    def __call__(self, observation) -> int:
        props = self.world.properties_from_observation(observation)
        return self.prop in props
