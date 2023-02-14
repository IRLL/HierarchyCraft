from typing import TYPE_CHECKING, List, Optional, Tuple, Union

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
    ]

    def __init__(
        self,
        destination: Optional[Zone] = None,
        zones: Optional[List[Zone]] = None,
        removed_player_items: Optional[List[ItemStack]] = None,
        added_player_items: Optional[List[ItemStack]] = None,
        removed_destination_items: Optional[List[ItemStack]] = None,
        added_destination_items: Optional[List[ItemStack]] = None,
        removed_zone_items: Optional[List[ItemStack]] = None,
        added_zone_items: Optional[List[ItemStack]] = None,
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

    def apply(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventories: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
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
        if self._zones is not None and not np.any(
            np.multiply(self._zones, state.position)
        ):
            return False
        if self._removed_player_items is not None and not np.all(
            state.player_inventory >= self._removed_player_items
        ):
            return False

        if self._removed_zone_items is not None:
            current_zone_slot = state.position.nonzero()[0]
            current_zone_inventory = state.zones_inventories[current_zone_slot, :]
            if not np.all(current_zone_inventory >= self._removed_zone_items):
                return False

        if (
            self._destination is not None
            and self._removed_destination_items is not None
        ):
            destination_zone_slot = self._destination.nonzero()[0]
            destination_inventory = state.zones_inventories[destination_zone_slot, :]
            if not np.all(destination_inventory >= self._removed_destination_items):
                return False
        return True

    def build(self, world: World) -> None:
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


def _items_from_stack_list(stacks: List[ItemStack]) -> List[Item]:
    return [stack.item for stack in stacks]
