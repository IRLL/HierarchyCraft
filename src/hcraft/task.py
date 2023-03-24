from abc import abstractmethod
from typing import TYPE_CHECKING, List, Optional, Union

import numpy as np

from hcraft.elements import Item, Stack, Zone

if TYPE_CHECKING:
    from hcraft.env import HcraftState
    from hcraft.world import World


class Task:
    """Abstract base class for all HierarchyCraft tasks."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.terminated = False
        self._terminate_player_items = None
        self._terminate_position = None
        self._terminate_zones_items = None

    def build(self, world: "World") -> None:
        """Build the task operation arrays based on the given world."""
        self._terminate_position = np.zeros(world.n_zones, dtype=np.int32)
        self._terminate_player_items = np.zeros(world.n_items, dtype=np.int32)
        self._terminate_zones_items = np.zeros(
            (world.n_zones, world.n_zones_items), dtype=np.int32
        )

    def is_terminal(self, state: "HcraftState") -> bool:
        """
        Returns whether the task is terminated.
        """
        if self.terminated:
            return True
        self.terminated = self._is_terminal(state)
        return self.terminated

    @abstractmethod
    def _is_terminal(self, state: "HcraftState") -> bool:
        """"""

    @abstractmethod
    def reward(self, state: "HcraftState") -> float:
        """
        Returns the reward for the given state.
        """

    def reset(self) -> None:
        """
        Reset the task termination.
        """
        self.terminated = False

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return self.name


class AchievementTask(Task):
    """Task giving a reward to the player only the first time achieved."""

    def __init__(self, name: str, reward: float):
        super().__init__(name)
        self._reward = reward

    @abstractmethod
    def _is_terminal(self, state: "HcraftState") -> bool:
        """
        Returns when the achievement is completed.
        """

    def reward(self, state: "HcraftState") -> float:
        if not self.terminated and self._is_terminal(state):
            return self._reward
        return 0.0


class GetItemTask(AchievementTask):
    """Task of getting a given quantity of an item."""

    def __init__(self, item_stack: Union[Item, Stack], reward: float = 1.0):
        self.item_stack = _stack_item(item_stack)
        super().__init__(name=self.get_name(self.item_stack), reward=reward)

    def build(self, world: "World") -> None:
        super().build(world)
        item_slot = world.items.index(self.item_stack.item)
        self._terminate_player_items[item_slot] = self.item_stack.quantity

    def _is_terminal(self, state: "HcraftState") -> bool:
        return np.all(state.player_inventory >= self._terminate_player_items)

    @staticmethod
    def get_name(stack: Stack):
        """Name of the task for a given Stack"""
        quantity_str = _quantity_str(stack.quantity)
        return f"Get{quantity_str}{stack.item.name}"


class GoToZoneTask(AchievementTask):
    """Task to go to a given zone."""

    def __init__(self, zone: Zone, reward: float = 1.0) -> None:
        super().__init__(name=self.get_name(zone), reward=reward)
        self.zone = zone

    def build(self, world: "World"):
        super().build(world)
        zone_slot = world.zones.index(self.zone)
        self._terminate_position[zone_slot] = 1

    def _is_terminal(self, state: "HcraftState") -> bool:
        return np.all(state.position == self._terminate_position)

    @staticmethod
    def get_name(zone: Zone):
        """Name of the task for a given Stack"""
        return f"Go to {zone.name}"


class PlaceItemTask(AchievementTask):
    """Task to place a quantity of item in a given zone.

    If no zone is given, consider any of zones.

    """

    def __init__(
        self,
        item_stack: Union[Item, Stack],
        zones: Optional[Union[Zone, List[Zone]]] = None,
        reward: float = 1.0,
    ):
        item_stack = _stack_item(item_stack)
        self.item_stack = item_stack
        self.zones = _ensure_zone_list(zones)
        super().__init__(name=self.get_name(item_stack, zones), reward=reward)

    def build(self, world: "World"):
        super().build(world)
        if self.zones is None:
            zones_slots = np.arange(self._terminate_zones_items.shape[0])
        else:
            zones_slots = np.array([world.slot_from_zone(zone) for zone in self.zones])
        zone_item_slot = world.zones_items.index(self.item_stack.item)
        self._terminate_zones_items[
            zones_slots, zone_item_slot
        ] = self.item_stack.quantity

    def _is_terminal(self, state: "HcraftState") -> bool:
        if self.zones is None:
            return np.any(
                np.all(state.zones_inventories >= self._terminate_zones_items, axis=1)
            )
        return np.all(state.zones_inventories >= self._terminate_zones_items)

    @staticmethod
    def get_name(stack: Stack, zones: Optional[List[Zone]]):
        """Name of the task for a given Stack and list of Zone"""
        quantity_str = _quantity_str(stack.quantity)
        zones_str = _zones_str(_ensure_zone_list(zones))
        return f"Place{quantity_str}{stack.item.name}{zones_str}"


def _stack_item(item_or_stack: Union[Item, Stack]) -> Stack:
    if not isinstance(item_or_stack, Stack):
        item_or_stack = Stack(item_or_stack)
    return item_or_stack


def _quantity_str(quantity: int):
    return f" {quantity} " if quantity > 1 else " "


def _ensure_zone_list(zones: Optional[Union[Zone, List[Zone]]]) -> Optional[List[Zone]]:
    if isinstance(zones, Zone):
        zones = [zones]
    return zones


def _zones_str(zones: Optional[List[Zone]]):
    if zones is None:
        return " anywhere"
    if len(zones) == 1:
        return f" in {zones[0].name}"
    return f" in any of {set(zones)}"
