import numpy as np

from crafting.world import ItemStack, Zone, World


class GetItemTask:
    def __init__(self, item_stack: ItemStack, item_reward: float = 0.0):
        self.item_stack = item_stack
        self.item_reward = item_reward
        self.is_terminated = False

    def build(self, world: World) -> None:
        self._terminate_player_items = np.zeros(world.n_items, dtype=np.uint16)
        item_slot = world.items.index(self.item_stack.item)
        self._terminate_player_items[item_slot] = self.item_stack.quantity

    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        return np.all(player_inventory >= self._terminate_player_items)

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
            return self.item_reward
        return 0.0


class GoToZoneTask:
    def __init__(self, zone: Zone, zone_reward: float) -> None:
        self.zone = zone
        self.zone_reward = zone_reward
        self.is_terminated = False
        self._terminate_position = None

    def build(self, world: World):
        self._terminate_position = np.zeros(world.n_zones, dtype=np.uint16)
        self._terminate_position[world.zones.index(self.zone)] = 1

    def is_terminal(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventory: np.ndarray,
    ) -> bool:
        return np.all(position == self._terminate_position)

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
            return self.zone_reward
        return 0.0
