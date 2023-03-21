from typing import TYPE_CHECKING, Optional

import numpy as np

if TYPE_CHECKING:
    from hcraft.world import World
    from hcraft.elements import Zone, Item


class HcraftState:
    """State manager of HierarchyCraft environments.

    The state of every HierarchyCraft environment is composed of three parts:
    * The player's inventory: `state.player_inventory`
    * The one-hot encoded player's position: `state.position`
    * All zones inventories: `state.zones_inventories`

    The mapping of items, zones, and zones items to their respective indexes is done through
    the given World. (See `hcraft.world`)

    ![hcraft state](../../docs/images/hcraft_state.png)

    """

    def __init__(self, world: "World") -> None:
        """
        Args:
            world: World to build the state for.
        """
        self.player_inventory = np.array([], dtype=np.int32)
        self.position = np.array([], dtype=np.int32)
        self.zones_inventories = np.array([], dtype=np.int32)

        self.discovered_items = np.array([], dtype=np.ubyte)
        self.discovered_zones = np.array([], dtype=np.ubyte)
        self.discovered_zones_items = np.array([], dtype=np.ubyte)
        self.discovered_transformations = np.array([], dtype=np.ubyte)

        self.world = world
        self.reset()

    @property
    def current_zone_inventory(self) -> np.ndarray:
        """Inventory of the zone where the player is."""
        if self.position.shape[0] == 0:
            return np.array([])  # No Zone
        return self.zones_inventories[self._current_zone_slot, :][0]

    @property
    def observation(self) -> np.ndarray:
        """The player's observation is a subset of the state.

        Only the inventory of the current zone is shown.

        ![hcraft state](../../docs/images/hcraft_observation.png)

        """
        return np.concatenate(
            (
                self.player_inventory,
                self.position,
                self.current_zone_inventory,
            )
        )

    def amount_of(self, item: "Item", owner: Optional["Zone"] = "player") -> int:
        """Current amount of the given item owned by owner.

        Args:
            item: Item to get the amount of.
            owner: Owner of the inventory to check. Defaults to player.

        Returns:
            int: Amount of the item in the owner's inventory.
        """

        if owner in self.world.zones:
            zone_index = self.world.zones.index(owner)
            zone_item_index = self.world.zones_items.index(item)
            return int(self.zones_inventories[zone_index, zone_item_index])

        item_index = self.world.items.index(item)
        return int(self.player_inventory[item_index])

    def has_discovered(self, zone: "Zone") -> bool:
        """Whether the given zone was discovered.

        Args:
            zone (Zone): Zone to check.

        Returns:
            bool: True if the zone was discovered.
        """
        zone_index = self.world.zones.index(zone)
        return bool(self.discovered_zones[zone_index])

    @property
    def current_zone(self) -> Optional["Zone"]:
        """Current position of the player."""
        if self.world.n_zones == 0:
            return None
        return self.world.zones[self._current_zone_slot[0]]

    @property
    def _current_zone_slot(self) -> int:
        return self.position.nonzero()[0]

    def apply(self, action: int) -> bool:
        """Apply the given action to update the state.

        Args:
            action (int): Index of the transformation to apply.

        Returns:
            bool: True if the transformation was applied succesfuly. False otherwise.
        """
        choosen_transformation = self.world.transformations[action]
        if not choosen_transformation.is_valid(self):
            return False
        choosen_transformation.apply(
            self.player_inventory,
            self.position,
            self.zones_inventories,
        )
        self._update_discoveries(action)
        return True

    def reset(self) -> None:
        """Reset the state to it's initial value."""
        self.player_inventory = np.zeros(self.world.n_items, dtype=np.int32)
        for stack in self.world.start_items:
            item_slot = self.world.items.index(stack.item)
            self.player_inventory[item_slot] = stack.quantity

        self.position = np.zeros(self.world.n_zones, dtype=np.int32)
        start_slot = 0  # Start in first Zone by default
        if self.world.start_zone is not None:
            start_slot = self.world.slot_from_zone(self.world.start_zone)
        if self.position.shape[0] > 0:
            self.position[start_slot] = 1

        self.zones_inventories = np.zeros(
            (self.world.n_zones, self.world.n_zones_items), dtype=np.int32
        )
        for zone, zone_stacks in self.world.start_zones_items.items():
            zone_slot = self.world.slot_from_zone(zone)
            for stack in zone_stacks:
                item_slot = self.world.zones_items.index(stack.item)
                self.zones_inventories[zone_slot, item_slot] = stack.quantity

        self.discovered_items = np.zeros(self.world.n_items, dtype=np.ubyte)
        self.discovered_zones_items = np.zeros(self.world.n_zones_items, dtype=np.ubyte)
        self.discovered_zones = np.zeros(self.world.n_zones, dtype=np.ubyte)
        self.discovered_transformations = np.zeros(
            len(self.world.transformations), dtype=np.ubyte
        )
        self._update_discoveries()

    def _update_discoveries(self, action: Optional[int] = None) -> None:
        self.discovered_items = np.bitwise_or(
            self.discovered_items, self.player_inventory > 0
        )
        self.discovered_zones_items = np.bitwise_or(
            self.discovered_zones_items, self.current_zone_inventory > 0
        )
        self.discovered_zones = np.bitwise_or(self.discovered_zones, self.position > 0)
        if action is not None:
            self.discovered_transformations[action] = 1
