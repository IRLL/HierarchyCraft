import numpy as np
from abc import abstractmethod

from crafting.world import ItemStack, Zone, World


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

    def __init__(self, item_stack: ItemStack, reward: float):
        super().__init__(reward)
        self.item_stack = item_stack

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
    """Task to place a quantity of item in a given zone."""

    def __init__(self, item_stack: ItemStack, zone: Zone, reward: float):
        super().__init__(reward)
        self.item_stack = item_stack
        self.zone = zone

    def build(self, world: World):
        super().build(world)
        zone_slot = world.zones.index(self.zone)
        zone_item_slot = world.zones_items.index(self.item_stack.item)
        self._terminate_zones_items[
            zone_slot, zone_item_slot
        ] = self.item_stack.quantity

    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        return np.all(zones_inventory >= self._terminate_zones_items)
