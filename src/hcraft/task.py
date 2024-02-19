from abc import abstractmethod
from typing import TYPE_CHECKING, List, Optional, Union

import numpy as np

from hcraft.elements import Item, Stack, Zone

if TYPE_CHECKING:
    from hcraft.state import HcraftState
    from hcraft.world import World


class Task:
    """Abstract base class for all HierarchyCraft tasks."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.terminated = False
        self._terminate_player_items: Optional[np.ndarray] = None
        self._terminate_position: Optional[np.ndarray] = None
        self._terminate_zones_items: Optional[np.ndarray] = None

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
        if self._terminate_player_items is None:
            raise ValueError("terminate_player_items was not built")
        self._terminate_player_items[item_slot] = self.item_stack.quantity

    def _is_terminal(self, state: "HcraftState") -> bool:
        if self._terminate_player_items is None:
            raise ValueError("terminate_player_items was not built")
        return bool(np.all(state.player_inventory >= self._terminate_player_items))

    @staticmethod
    def get_name(stack: Stack) -> str:
        """Name of the task for a given Stack"""
        quantity_str = _quantity_str(stack.quantity)
        return f"Get{quantity_str}{stack.item.name}"


class GoToZoneTask(AchievementTask):
    """Task to go to a given zone."""

    def __init__(self, zone: Zone, reward: float = 1.0) -> None:
        super().__init__(name=self.get_name(zone), reward=reward)
        self.zone = zone

    def build(self, world: "World") -> None:
        super().build(world)
        zone_slot = world.zones.index(self.zone)
        if self._terminate_position is None:
            raise ValueError("terminate_position was not built")
        self._terminate_position[zone_slot] = 1

    def _is_terminal(self, state: "HcraftState") -> bool:
        return bool(np.all(state.position == self._terminate_position))

    @staticmethod
    def get_name(zone: Zone) -> str:
        """Name of the task for a given Stack"""
        return f"Go to {zone.name}"


class PlaceItemTask(AchievementTask):
    """Task to place a quantity of item in a given zone.

    If no zone is given, consider placing the item anywhere.

    """

    def __init__(
        self,
        item_stack: Union[Item, Stack],
        zone: Optional[Zone] = None,
        reward: float = 1.0,
    ):
        item_stack = _stack_item(item_stack)
        self.item_stack = item_stack
        self.zone = zone
        super().__init__(name=self.get_name(item_stack, zone), reward=reward)

    def build(self, world: "World") -> None:
        super().build(world)
        if self._terminate_zones_items is None:
            raise ValueError("terminate_zones_items was not built")
        if self.zone is None:
            zones_slots = np.arange(self._terminate_zones_items.shape[0])
        else:
            zones_slots = np.array([world.slot_from_zone(self.zone)])
        zone_item_slot = world.zones_items.index(self.item_stack.item)
        self._terminate_zones_items[
            zones_slots, zone_item_slot
        ] = self.item_stack.quantity

    def _is_terminal(self, state: "HcraftState") -> bool:
        if self._terminate_zones_items is None:
            raise ValueError("terminate_zones_items was not built")
        if self.zone is None:
            _is_terminal = np.any(
                np.all(state.zones_inventories >= self._terminate_zones_items, axis=1)
            )
        else:
            _is_terminal = np.all(
                state.zones_inventories >= self._terminate_zones_items
            )
        return bool(_is_terminal)

    @staticmethod
    def get_name(stack: Stack, zone: Optional[Zone]) -> str:
        """Name of the task for a given Stack and list of Zone"""
        quantity_str = _quantity_str(stack.quantity)
        zones_str = _zones_str(zone)
        return f"Place{quantity_str}{stack.item.name}{zones_str}"


def _stack_item(item_or_stack: Union[Item, Stack]) -> Stack:
    if not isinstance(item_or_stack, Stack):
        item_or_stack = Stack(item_or_stack)
    return item_or_stack


def _quantity_str(quantity: int) -> str:
    return f" {quantity} " if quantity > 1 else " "


def _zones_str(zone: Optional[Zone]) -> str:
    if zone is None:
        return " anywhere"
    return f" in {zone.name}"
