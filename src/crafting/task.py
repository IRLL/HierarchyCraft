from typing import Optional, Union, List
from abc import abstractmethod

import numpy as np

from crafting.world import Item, ItemStack, Zone, World


class Task:
    """Abstract base class for all Crafting tasks."""

    def __init__(self) -> None:
        self._terminate_player_items = None
        self._terminate_position = None
        self._terminate_zones_items = None

    def build(self, world: World) -> None:
        """Build the task operation arrays based on the given world."""
        self._terminate_position = np.zeros(world.n_zones, dtype=np.uint16)
        self._terminate_player_items = np.zeros(world.n_items, dtype=np.uint16)
        self._terminate_zones_items = np.zeros(
            (world.n_zones, world.n_zones_items), dtype=np.uint16
        )

    @abstractmethod
    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        """
        Returns whether the task is terminated.
        """

    @abstractmethod
    def reward(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> float:
        """
        Returns the reward for the given state.
        """


class AchievementTask(Task):
    """Task giving a reward to the player only the first time achieved."""

    def __init__(self, reward: float):
        super().__init__()
        self._reward = reward
        self.is_terminated = False

    def reward(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> float:
        if not self.is_terminated and self.is_terminal(
            player_inventory, position, zones_inventory
        ):
            self.is_terminated = True
            return self._reward
        return 0.0


class GetItemTask(AchievementTask):
    """Task of getting a given quantity of an item."""

    def __init__(self, item_stack: Union[Item, ItemStack], reward: float):
        super().__init__(reward)
        self.item_stack = stack_item(item_stack)

    def build(self, world: World) -> None:
        super().build(world)
        item_slot = world.items.index(self.item_stack.item)
        self._terminate_player_items[item_slot] = self.item_stack.quantity

    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        return np.all(player_inventory >= self._terminate_player_items)


class GoToZoneTask(AchievementTask):
    """Task to go to a given zone."""

    def __init__(self, zone: Zone, reward: float) -> None:
        super().__init__(reward)
        self.zone = zone

    def build(self, world: World):
        super().build(world)
        zone_slot = world.zones.index(self.zone)
        self._terminate_position[zone_slot] = 1

    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        return np.all(position == self._terminate_position)


class PlaceItemTask(AchievementTask):
    """Task to place a quantity of item in a given zone.

    If no zone is given, consider any of zones.

    """

    def __init__(
        self,
        item_stack: Union[Item, ItemStack],
        zones: Optional[Union[Zone, List[Zone]]] = None,
        reward: float = 1.0,
    ):
        super().__init__(reward)
        self.item_stack = stack_item(item_stack)
        if isinstance(zones, Zone):
            zones = [zones]
        self.zones = zones

    def build(self, world: World):
        super().build(world)
        if self.zones is None:
            zones_slots = np.arange(self._terminate_zones_items.shape[0])
        else:
            zones_slots = np.array([world.zones.index(zone) for zone in self.zones])
        zone_item_slot = world.zones_items.index(self.item_stack.item)
        self._terminate_zones_items[
            zones_slots, zone_item_slot
        ] = self.item_stack.quantity

    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        return np.all(zones_inventory >= self._terminate_zones_items)


def stack_item(item_or_stack: Union[Item, ItemStack]) -> ItemStack:
    if not isinstance(item_or_stack, ItemStack):
        item_or_stack = ItemStack(item_or_stack)
    return item_or_stack