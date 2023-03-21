""" Module to define FeatureCondition nodes for the HEBGraph of the HierarchyCraft environment. """

from typing import TYPE_CHECKING, Optional

import numpy as np
from hebg import FeatureCondition

from hcraft.elements import Stack, Zone
from hcraft.render.utils import load_or_create_image
from hcraft.task import _quantity_str

if TYPE_CHECKING:
    from hcraft.env import HcraftEnv


class HasStack(FeatureCondition):

    """FeatureCondition to check if player has an Item in a given quantity."""

    def __init__(self, env: "HcraftEnv", stack: Stack) -> None:
        image = load_or_create_image(stack, env.world.resources_path)
        super().__init__(name=self.get_name(stack), image=np.array(image), complexity=1)

        self.stack = stack
        self.n_items = env.world.n_items
        self.slot = env.world.items.index(stack.item)

    @staticmethod
    def get_name(stack: Stack):
        """Name of the HasStack feature condition given the stack."""
        quantity_str = _quantity_str(stack.quantity)
        return f"Has{quantity_str}{stack.item.name}?"

    def __call__(self, observation) -> int:
        inventory_content = observation[: self.n_items]
        return inventory_content[self.slot] >= self.stack.quantity


class HasLessStack(FeatureCondition):

    """FeatureCondition to check if player has an Item in less than a given quantity."""

    def __init__(self, env: "HcraftEnv", stack: Stack) -> None:
        image = load_or_create_image(stack, env.world.resources_path)
        super().__init__(name=self.get_name(stack), image=np.array(image), complexity=1)

        self.stack = stack
        self.n_items = env.world.n_items
        self.slot = env.world.items.index(stack.item)

    @staticmethod
    def get_name(stack: Stack):
        """Name of the HasStack feature condition given the stack."""
        return f"Has less than {stack.quantity} {stack.item.name}?"

    def __call__(self, observation) -> int:
        inventory_content = observation[: self.n_items]
        return inventory_content[self.slot] <= self.stack.quantity


class IsInZone(FeatureCondition):

    """FeatureCondition to check if player is in a Zone."""

    def __init__(self, env: "HcraftEnv", zone: Zone) -> None:
        image = load_or_create_image(zone, env.world.resources_path)
        super().__init__(name=self.get_name(zone), image=image, complexity=1)

        self.n_items = env.world.n_items
        self.n_zones = env.world.n_zones
        self.zone = zone
        self.slot = env.world.slot_from_zone(zone)

    @staticmethod
    def get_name(zone: Zone):
        """Name of the IsInZone feature condition given the zone."""
        return f"Is in {zone.name}?"

    def __call__(self, observation) -> int:
        position = observation[self.n_items : self.n_items + self.n_zones]
        return position[self.slot] == 1


class HasZoneItem(FeatureCondition):

    """FeatureCondition to check if a Zone has the given property."""

    def __init__(
        self, env: "HcraftEnv", stack: Stack, zone: Optional[Zone] = None
    ) -> None:
        image = np.array(load_or_create_image(stack, env.world.resources_path))
        super().__init__(name=self.get_name(stack, zone), image=image, complexity=1)

        self.stack = stack
        self.n_items = env.world.n_items
        self.n_zones = env.world.n_zones
        self.item_slot = env.world.zones_items.index(stack.item)
        self.zone_slot = env.world.zones.index(zone) if zone is not None else None

        # We cheat for now, we will deal with partial observability later.
        self.state = env.state

    @staticmethod
    def get_name(stack: Stack, zone: Optional[Zone] = None):
        """Name of the HasZoneItem feature condition given stack and optional zone."""
        zone_str = "Current zone" if zone is None else zone.name.capitalize()
        quantity_str = _quantity_str(stack.quantity)
        return f"{zone_str} has{quantity_str}{stack.item.name}?"

    def __call__(self, observation) -> int:
        if self.zone_slot is None:
            zone_items = observation[self.n_items + self.n_zones :]
            return zone_items[self.item_slot] >= self.stack.quantity
        return (
            self.state.zones_inventories[self.zone_slot, self.item_slot]
            >= self.stack.quantity
        )
