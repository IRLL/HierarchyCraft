from typing import TYPE_CHECKING, List, Dict, Optional, Tuple, Union

import numpy as np

from crafting.world import Item, ItemStack, World, Zone

if TYPE_CHECKING:
    from crafting.env import CraftingState


class Transformation:
    OPERATIONS = [
        "destination",
        "zones",
        "removed_player_items",
        "added_player_items",
        "removed_destination_items",
        "added_destination_items",
        "removed_zone_items",
        "added_zone_items",
        "removed_zones_items",
        "added_zones_items",
    ]

    def __init__(
        self,
        destination: Optional[Zone] = None,
        zones: Optional[List[Zone]] = None,
        removed_player_items: Optional[List[Union[ItemStack, Item]]] = None,
        added_player_items: Optional[List[Union[ItemStack, Item]]] = None,
        removed_destination_items: Optional[List[Union[ItemStack, Item]]] = None,
        added_destination_items: Optional[List[Union[ItemStack, Item]]] = None,
        removed_zone_items: Optional[List[Union[ItemStack, Item]]] = None,
        added_zone_items: Optional[List[Union[ItemStack, Item]]] = None,
        removed_zones_items: Optional[Dict[Zone, List[Union[ItemStack, Item]]]] = None,
        added_zones_items: Optional[Dict[Zone, List[Union[ItemStack, Item]]]] = None,
    ) -> None:
        self.destination = destination
        self._destination = None

        self.zones = zones
        self._zones = None

        self.removed_player_items = _stack_items_list(removed_player_items)
        self._removed_player_items = None
        self.added_player_items = _stack_items_list(added_player_items)
        self._added_player_items = None

        self.removed_destination_items = _stack_items_list(removed_destination_items)
        self._removed_destination_items = None
        self.added_destination_items = _stack_items_list(added_destination_items)
        self._added_destination_items = None

        self.removed_zone_items = _stack_items_list(removed_zone_items)
        self._removed_zone_items = None
        self.added_zone_items = _stack_items_list(added_zone_items)
        self._added_zone_items = None

        self.removed_zones_items = _stack_dict_items_list(removed_zones_items)
        self._removed_zones_items = None
        self.added_zones_items = _stack_dict_items_list(added_zones_items)
        self._added_zones_items = None

    def apply(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventories: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Apply the transformation in place on the given state."""
        position_slot: int = position.nonzero()[0]
        if self._added_player_items is not None:
            player_inventory += self._added_player_items
        if self._removed_player_items is not None:
            player_inventory -= self._removed_player_items
        if self._added_zone_items is not None:
            zones_inventories[position_slot, :] += self._added_zone_items
        if self._removed_zone_items is not None:
            zones_inventories[position_slot, :] -= self._removed_zone_items
        if self._destination is not None:
            destination_slot: int = self._destination.nonzero()[0]
            if self._added_destination_items is not None:
                zones_inventories[destination_slot, :] += self._added_destination_items
            if self._removed_destination_items is not None:
                zones_inventories[
                    destination_slot, :
                ] -= self._removed_destination_items
            position[...] = self._destination
        return player_inventory, position, zones_inventories

    def is_valid(self, state: "CraftingState") -> bool:
        """Is the transformation valid in the given state?"""
        if not self._is_valid_position(state.position):
            return False
        if not self._is_valid_inventory(state.player_inventory):
            return False
        if not self._is_valid_current_zone_inventory(
            state.position, state.zones_inventories
        ):
            return False
        if not self._is_valid_zones_inventory(state.zones_inventories):
            return False
        if not self._is_valid_destination_inventory(state.zones_inventories):
            return False
        return True

    def build(self, world: World) -> None:
        """Build the transformation array operations on the given world."""
        for op_name in self.OPERATIONS:
            if getattr(self, op_name) is not None:
                builder = getattr(self, f"_build_{op_name}_op")
                builder(world)

    @property
    def produced_items(self) -> List[Item]:
        """List of produced items by this transformation."""
        items = []
        if self.added_player_items:
            items += _items_from_stack_list(self.added_player_items)
        return items

    @property
    def produced_zones_items(self) -> List[Item]:
        """List of produced zones items by this transformation."""
        items = []
        if self.added_zone_items:
            items += _items_from_stack_list(self.added_zone_items)
        if self.added_destination_items:
            items += _items_from_stack_list(self.added_destination_items)
        return items

    @property
    def consumed_items(self) -> List[Item]:
        """List of consumed items by this transformation."""
        items = []
        if self.removed_player_items:
            items += _items_from_stack_list(self.removed_player_items)
        return items

    @property
    def consumed_zones_items(self) -> List[Item]:
        """List of consumed zones items by this transformation."""
        items = []
        if self.removed_zone_items:
            items += _items_from_stack_list(self.removed_zone_items)
        return items

    @property
    def consumed_destination_items(self) -> List[Item]:
        """List of consumed zones items at destination by this transformation."""
        items = []
        if self.removed_destination_items:
            items += _items_from_stack_list(self.removed_destination_items)
        return items

    def _is_valid_position(self, position: np.ndarray):
        if self._zones is not None and not np.any(np.multiply(self._zones, position)):
            return False
        return True

    def _is_valid_inventory(self, player_inventory: np.ndarray):
        if self._removed_player_items is not None and not np.all(
            player_inventory >= self._removed_player_items
        ):
            return False
        return True

    def _is_valid_current_zone_inventory(
        self, position: np.ndarray, zones_inventories: np.ndarray
    ):
        if self._removed_zone_items is not None:
            current_zone_slot = position.nonzero()[0]
            current_zone_inventory = zones_inventories[current_zone_slot, :]
            if not np.all(current_zone_inventory >= self._removed_zone_items):
                return False
        return True

    def _is_valid_zones_inventory(self, zones_inventories: np.ndarray):
        if self._removed_zones_items is not None:
            if not np.all(zones_inventories >= self._removed_zones_items):
                return False
        return True

    def _is_valid_destination_inventory(self, zones_inventories: np.ndarray):
        if (
            self._destination is not None
            and self._removed_destination_items is not None
        ):
            destination_zone_slot = self._destination.nonzero()[0]
            destination_inventory = zones_inventories[destination_zone_slot, :]
            if not np.all(destination_inventory >= self._removed_destination_items):
                return False
        return True

    def _build_destination_op(self, world: World) -> None:
        self._destination = np.zeros(world.n_zones, dtype=np.uint16)
        self._destination[world.slot_from_zone(self.destination)] = 1

    def _build_zones_op(self, world: World) -> None:
        self._zones = np.zeros(world.n_zones, dtype=np.uint16)
        for zone in self.zones:
            self._zones[world.slot_from_zone(zone)] = 1

    def _build_removed_player_items_op(self, world: World) -> None:
        self._build_items_op("removed_player_items", world.items)

    def _build_added_player_items_op(self, world: World) -> None:
        self._build_items_op("added_player_items", world.items)

    def _build_removed_destination_items_op(self, world: World) -> None:
        self._build_items_op("removed_destination_items", world.zones_items)

    def _build_added_destination_items_op(self, world: World) -> None:
        self._build_items_op("added_destination_items", world.zones_items)

    def _build_removed_zone_items_op(self, world: World) -> None:
        self._build_items_op("removed_zone_items", world.zones_items)

    def _build_added_zone_items_op(self, world: World) -> None:
        self._build_items_op("added_zone_items", world.zones_items)

    def _build_items_op(self, op_name: str, world_item_list: List[Item]):
        operation = np.zeros(len(world_item_list), dtype=np.uint16)
        itemstacks: List[ItemStack] = getattr(self, op_name)
        for itemstack in itemstacks:
            item_slot = world_item_list.index(itemstack.item)
            operation[item_slot] = itemstack.quantity
        setattr(self, f"_{op_name}", operation)

    def _build_removed_zones_items_op(self, world: World) -> None:
        self._build_zones_items_op(
            "removed_zones_items", world.zones, world.zones_items
        )

    def _build_added_zones_items_op(self, world: World) -> None:
        self._build_zones_items_op("added_zones_items", world.zones, world.zones_items)

    def _build_zones_items_op(
        self, op_name: str, zones: List[Zone], zones_items: List[Item]
    ):
        operation = np.zeros((len(zones), len(zones_items)), dtype=np.uint16)
        stacks_per_zone: Dict[Zone, List[ItemStack]] = getattr(self, op_name)
        for zone, stacks in stacks_per_zone.items():
            zone_slot = zones.index(zone)
            for stack in stacks:
                item_slot = zones_items.index(stack.item)
                operation[zone_slot, item_slot] = stack.quantity
        setattr(self, f"_{op_name}", operation)

    def __str__(self) -> str:
        transfo_text = ""

        remove_texts = []
        if self.removed_player_items is not None:
            remove_texts.append(_unstacked_str(self.removed_player_items))
        if self.removed_zone_items is not None:
            remove_texts.append(_unstacked_str(self.removed_zone_items, "Zone(", ")"))
        if self.removed_destination_items is not None:
            remove_texts.append(
                _unstacked_str(self.removed_destination_items, "Dest(", ")")
            )

        if remove_texts:
            transfo_text = " ".join(remove_texts)
            transfo_text += " "

        transfo_text += "> "

        add_texts = []
        if self.added_player_items is not None:
            add_texts.append(_unstacked_str(self.added_player_items))
        if self.added_zone_items is not None:
            add_texts.append(_unstacked_str(self.added_zone_items, "Zone(", ")"))
        if self.added_destination_items is not None:
            add_texts.append(_unstacked_str(self.added_destination_items, "Dest(", ")"))

        if add_texts:
            transfo_text += " ".join(add_texts)
            if self.destination is not None:
                transfo_text += " "

        if self.destination is not None:
            transfo_text += f"| {self.destination.name}"

        return transfo_text


def _unstacked_str(itemstacks: List[ItemStack], prefix: str = "", suffix: str = ""):
    items_text = ",".join([str(itemstack) for itemstack in itemstacks])
    return f"{prefix}{items_text}{suffix}"


def _stack_items_list(
    items_or_stacks: Optional[List[Union[Item, ItemStack]]]
) -> Optional[List[ItemStack]]:
    if items_or_stacks is None:
        return None
    for i, item_or_stack in enumerate(items_or_stacks):
        if not isinstance(item_or_stack, ItemStack):
            items_or_stacks[i] = ItemStack(item_or_stack)
    return items_or_stacks


def _stack_dict_items_list(
    dict_of_stacks: Optional[Dict[Zone, List[Union[ItemStack, Item]]]]
):
    if dict_of_stacks is None:
        return None
    return {
        zone: _stack_items_list(items_or_stacks)
        for zone, items_or_stacks in dict_of_stacks.items()
    }


def _items_from_stack_list(stacks: List[ItemStack]) -> List[Item]:
    return [stack.item for stack in stacks]
