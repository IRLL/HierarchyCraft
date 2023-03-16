"""# Transformation

## Examples

```python
from crafting.elements import Item, ItemStack, Zone
from crafting.transformation import Transformation
```

### Add an item in player inventory
```python
DIRT = Item("dirt")
Transformation(inventory_changes={"player": {"add":[DIRT]}})
```

### Modify the player position
```python
FOREST = Zone("forest")
Transformation(destination=FOREST)
```

### Restrict a transformation to a set of zones
```python
WOOD = Item("wood")
Transformation(
    inventory_changes={"player": {"add":[WOOD]}},
    zones=[FOREST]
)
```

### Modify the player inventory
```python
PLANK = Item("plank")
Transformation(
    inventory_changes={
        "player": {
            "add":[ItemStack(PLANK, 4)]
            "remove": [WOOD]
        },
    },
)
```
Note the use of ItemStack to give a quantity > 1.

### Modify the current zone's inventory
```python
HOUSE = Item("house") # Need 12 WOOD and 64 PLANK
Transformation(
    inventory_changes={
        "player": {"remove": [ItemStack(WOOD, 12), ItemStack(PLANK, 64)]},
        "current_zone": {"add": [HOUSE]}
    },
)
```

### Move with a cost
```python
TREETOPS = Zone("treetops")
LADDER = Item("ladder")
Transformation(
    destination=TREETOPS,
    inventory_changes={"player": {"remove":[LADDER]}},
)
```

### Modify the destination's inventory
```python
# Jump from treetops
CRATER = Item("crater")
Transformation(
    destination=FOREST,
    inventory_changes={"destination": {"add":[CRATER]}},
    zones=[TREETOPS]
)
```

### Move with a required item and required item in zone
```python
INSIDE_HOUSE = Zone("house")
DOOR = Item("door")
KEY = Item("key")
Transformation(
    destination=INSIDE_HOUSE,
    inventory_changes={
        "player": {
            "remove": [KEY],  # Ensure has key
            "add":[KEY],      # Then give it back
        },
        "current_zone": {
            "remove": [DOOR],  # Ensure has door
            "add":[DOOR],      # Then give it door
        }
    },
)
```
By removing and adding the same item,
we make sure that the item is required to be in the inventory but is not consumed.

### Modifiy any specific zones inventories
```python
# What if there is a strange red button you can press ?
STRANGE_RED_BUTTON = Item("don't press me")
SPACE = Zone("space")
INCOMING_MISSILES = Item("incoming_missiles")
Transformation(
    inventory_changes={
        "current_zone": {  # Current zone
            "remove": [STRANGE_RED_BUTTON],
            "add":[STRANGE_RED_BUTTON],
        },
        SPACE: {  # An 'absolute' specific zone
            "add": [ItemStack(INCOMING_MISSILES, 64)]
        },
    },
)
```
Note that the player may not see the effect of such a transformation,
because the player only observe the current zone items.


"""


from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union
from enum import Enum

import numpy as np

from crafting.elements import Item, ItemStack, Zone

if TYPE_CHECKING:
    from crafting.env import CraftingState
    from crafting.world import World


class InventoryOwner(Enum):
    PLAYER = "player"
    CURRENT = "current_zone"
    DESTINATION = "destination"
    ZONES = "zones"


class InventoryOperation(Enum):
    REMOVE = "remove"
    ADD = "add"
    MAX = "max"
    APPLY = "apply"


InventoryChanges = Dict[
    InventoryOperation,
    Union[List[Union[Item, ItemStack]], Dict[Zone, List[Union[Item, ItemStack]]]],
]
InventoryOperations = Dict[InventoryOperation, np.ndarray]


class Transformation:
    """The building blocks of every crafting environment.

    A list of transformations is what defines each crafting environement.
    Transformation becomes the available actions and all available transitions of the environment.

    Each transformation defines changes of:

    * the player inventory
    * the player position to a given destination
    * the current zone inventory
    * the destination zone inventory (if a destination is specified).
    * all specific zones inventories

    Each inventory change is a list of removed (-) and added (+) ItemStack.

    If specified, they may be restricted to only a subset of valid zones,
    all zones are valid by default.

    A Transformation can only be applied if valid in the given state.
    A transformation is only valid if the player in a valid zone
    and all relevant inventories have enough items to be removed *before* adding new items.

    The picture bellow illustrates the impact of
    an example transformation on a given `crafting.CraftingState`:
    ![crafting transformation](https://raw.githubusercontent.com/IRLL/Crafting/master/docs/images/crafting_state.png)

    In this example, when applied, the transformation will:

    * <span style="color:red">(-)</span>
        Remove 1 item "0", then <span style="color:red">(+)</span>
        Add 4 item "3" in the <span style="color:red">player inventory</span>.
    * Update the <span style="color:gray">player position</span>
        from the <span style="color:green">current zone</span> "1".
        to the <span style="color:orange">destination zone</span> "3".
    * <span style="color:green">(-)</span>
        Remove 2 zone item "0" and 1 zone item "1", then <span style="color:green">(+)</span>
        Add 1 item "1" in the <span style="color:green">current zone</span> inventory.
    * <span style="color:orange">(-)</span>
        Remove 1 zone item "2", then <span style="color:orange">(+)</span>
        Add 1 item "0" in the <span style="color:orange">destination zone</span> inventory.
    * <span style="color:blue">(-)</span>
        Remove 1 zone item "0" in the zone "1" inventory
        and 2 zone item "2" in the zone "2" inventory,
        then <span style="color:blue">(+)</span>
        Add 1 zone item "1" in the zone "0" inventory
        and 1 zone item "2" in the zone "1" inventory.

    """

    def __init__(
        self,
        destination: Optional[Zone] = None,
        inventory_changes: Optional[Dict[InventoryOwner, InventoryChanges]] = None,
        zones: Optional[List[Zone]] = None,
    ) -> None:
        """The building blocks of every crafting environment.

        Args:
            destination: Destination zone.
                Defaults to None.
            inventory_changes: Dictionary inventory changes for
                the player, the current zone, the destination zone and each zone.
                Defaults to None.
            zones: List of valid zones, if None all zones are valid.
                Defaults to None.
        """
        self.destination = destination
        self._destination = None

        self.zones = zones
        self._zones = None

        self.inventory_changes = _format_inventory_changes(inventory_changes)
        self._inventory_operations: Optional[
            Dict[InventoryOwner, InventoryOperations]
        ] = None

    def apply(
        self,
        player_inventory: np.ndarray,
        position: np.ndarray,
        zones_inventories: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Apply the transformation in place on the given state."""

        for owner, operations in self._inventory_operations.items():
            operation_arr = operations[InventoryOperation.APPLY]
            if operation_arr is not None:
                _update_inventory(
                    owner,
                    player_inventory,
                    position,
                    zones_inventories,
                    self._destination,
                    operation_arr,
                )
        if self._destination is not None:
            position[...] = self._destination

    def is_valid(self, state: "CraftingState") -> bool:
        """Is the transformation valid in the given state?"""
        if not self._is_valid_position(state.position):
            return False
        if not self._is_valid_player_inventory(state.player_inventory):
            return False
        if not self._is_valid_zones_inventory(state.zones_inventories, state.position):
            return False
        return True

    def build(self, world: "World") -> None:
        """Build the transformation array operations on the given world."""
        self._build_destination_op(world)
        self._build_inventory_ops(world)
        self._build_zones_op(world)

    def get_changes(
        self, owner: InventoryOwner, operation: InventoryOperation
    ) -> Optional[Union[List[ItemStack], Dict[Zone, List[ItemStack]]]]:
        """Get individual changes for a given owner and a given operation.

        Args:
            owner: Owner of the inventory changes to get.
            operation: Operation on the inventory to get.

        Returns:
            Changes of the inventory of the given owner with the given operation.
        """
        owner = InventoryOwner(owner)
        operation = InventoryOperation(operation)
        operations = self.inventory_changes.get(owner, {})
        return operations.get(operation, None)

    def production(self, owner: InventoryOwner) -> Set["Item"]:
        """Set of produced items for the given owner by this transformation."""
        return self._relevant_items_changed(owner, InventoryOperation.ADD)

    def consumption(self, owner: InventoryOwner) -> Set["Item"]:
        """Set of consumed items for the given owner by this transformation."""
        return self._relevant_items_changed(owner, InventoryOperation.REMOVE)

    @property
    def produced_zones_items(self) -> Set["Item"]:
        """Set of produced zones items by this transformation."""
        return (
            self.production(InventoryOwner.CURRENT)
            | self.production(InventoryOwner.DESTINATION)
            | self.production(InventoryOwner.ZONES)
        )

    @property
    def consumed_zones_items(self) -> Set["Item"]:
        """Set of consumed zones items by this transformation."""
        return (
            self.consumption(InventoryOwner.CURRENT)
            | self.consumption(InventoryOwner.DESTINATION)
            | self.consumption(InventoryOwner.ZONES)
        )

    def _relevant_items_changed(
        self, owner: InventoryOwner, operation: InventoryOperation
    ):
        added_stacks = self.get_changes(owner, operation)
        items = set()

        if added_stacks:
            if owner is not InventoryOwner.ZONES:
                return _items_from_stack_list(added_stacks)

            for _zone, stacks in added_stacks.items():
                items |= _items_from_stack_list(stacks)

        return items

    def _is_valid_position(self, position: np.ndarray):
        if self._zones is not None and not np.any(np.multiply(self._zones, position)):
            return False
        if self._destination is not None and np.all(self._destination == position):
            return False
        return True

    def _is_valid_inventory(
        self,
        inventory: np.ndarray,
        added: Optional[np.ndarray],
        removed: Optional[np.ndarray],
        max_items: Optional[np.ndarray],
    ):
        if added is None:
            added = 0
        if removed is not None and not np.all(inventory >= removed):
            return False
        if max_items is not None and np.any(inventory + added > max_items):
            return False
        return True

    def _is_valid_player_inventory(self, player_inventory: np.ndarray):
        items_changes = self._inventory_operations.get(InventoryOwner.PLAYER, {})
        added = items_changes.get(InventoryOperation.ADD, 0)
        removed = items_changes.get(InventoryOperation.REMOVE)
        max_items = items_changes.get(InventoryOperation.MAX)
        return self._is_valid_inventory(player_inventory, added, removed, max_items)

    def _is_valid_zones_inventory(
        self, zones_inventories: np.ndarray, position: np.ndarray
    ):
        if zones_inventories.size == 0:
            return True

        # Specific zones operations
        zones_changes = self._inventory_operations.get(InventoryOwner.ZONES, {})
        zeros = np.zeros_like(zones_inventories)
        added = zones_changes.get(InventoryOperation.ADD, zeros.copy())
        removed = zones_changes.get(InventoryOperation.REMOVE, zeros.copy())
        infs = np.inf * np.ones_like(zones_inventories)
        max_items = zones_changes.get(InventoryOperation.MAX, infs.copy())

        # Current zone
        current_changes = self._inventory_operations.get(InventoryOwner.CURRENT, {})
        current_slot = position.nonzero()[0]
        added[current_slot] += current_changes.get(InventoryOperation.ADD, 0)
        removed[current_slot] += current_changes.get(InventoryOperation.REMOVE, 0)
        max_items[current_slot] = np.minimum(
            max_items[current_slot],
            current_changes.get(InventoryOperation.MAX, np.inf),
        )

        # Destination
        if self._destination is not None:
            dest_changes = self._inventory_operations.get(
                InventoryOwner.DESTINATION, {}
            )
            dest_slot = self._destination.nonzero()[0]
            added[dest_slot] += dest_changes.get(InventoryOperation.ADD, 0)
            removed[dest_slot] += dest_changes.get(InventoryOperation.REMOVE, 0)
            max_items[dest_slot] = np.minimum(
                max_items[dest_slot],
                dest_changes.get(InventoryOperation.MAX, np.inf),
            )

        return self._is_valid_inventory(zones_inventories, added, removed, max_items)

    def _build_destination_op(self, world: "World") -> None:
        if self.destination is None:
            return
        self._destination = np.zeros(world.n_zones, dtype=np.int32)
        self._destination[world.slot_from_zone(self.destination)] = 1

    def _build_zones_op(self, world: "World") -> None:
        if self.zones is None:
            return
        self._zones = np.zeros(world.n_zones, dtype=np.int32)
        for zone in self.zones:
            self._zones[world.slot_from_zone(zone)] = 1

    def _build_inventory_ops(self, world: "World"):
        self._inventory_operations = {}
        for owner, operations in self.inventory_changes.items():
            self._build_inventory_operation(owner, operations, world)
        self._build_apply_operations()

    def _build_inventory_operation(
        self, owner: InventoryOwner, operations: InventoryChanges, world: "World"
    ):
        owner = InventoryOwner(owner)
        if owner is InventoryOwner.PLAYER:
            world_items_list = world.items
        else:
            world_items_list = world.zones_items
        for operation, stacks in operations.items():
            operation = InventoryOperation(operation)
            default_value = 0
            if operation is InventoryOperation.MAX:
                default_value = np.inf
            if owner is InventoryOwner.ZONES:
                operation_arr = self._build_zones_items_op(
                    stacks, world.zones, world.zones_items, default_value
                )
            else:
                operation_arr = self._build_operation_array(
                    stacks, world_items_list, default_value
                )
            if owner not in self._inventory_operations:
                self._inventory_operations[owner] = {}
            self._inventory_operations[owner][operation] = operation_arr

    def _build_apply_operations(self):
        for owner, operations in self._inventory_operations.items():
            apply_op = InventoryOperation.APPLY
            apply_arr = _build_apply_operation_array(operations)
            self._inventory_operations[owner][apply_op] = apply_arr

    def _build_operation_array(
        self,
        itemstacks: List[ItemStack],
        world_items_list: List["Item"],
        default_value: int = 0,
    ) -> np.ndarray:
        operation = default_value * np.ones(len(world_items_list), dtype=np.int32)
        for itemstack in itemstacks:
            item_slot = world_items_list.index(itemstack.item)
            operation[item_slot] = itemstack.quantity
        return operation

    def _build_zones_items_op(
        self,
        stacks_per_zone: Dict[Zone, List["ItemStack"]],
        zones: List[Zone],
        zones_items: List["Item"],
        default_value: float = 0.0,
    ) -> np.ndarray:
        operation = default_value * np.ones(
            (len(zones), len(zones_items)), dtype=np.int32
        )
        for zone, stacks in stacks_per_zone.items():
            zone_slot = zones.index(zone)
            for stack in stacks:
                item_slot = zones_items.index(stack.item)
                operation[zone_slot, item_slot] = stack.quantity
        return operation

    def __str__(self) -> str:
        transfo_text = ""

        remove_texts = []
        remove_texts += _stacks_str(
            self.get_changes(InventoryOwner.PLAYER, InventoryOperation.REMOVE)
        )
        remove_texts += _stacks_str(
            self.get_changes(InventoryOwner.CURRENT, InventoryOperation.REMOVE),
            "Zone(",
            ")",
        )
        remove_texts += _stacks_str(
            self.get_changes(InventoryOwner.DESTINATION, InventoryOperation.REMOVE),
            "Dest(",
            ")",
        )
        remove_texts += _dict_stacks_str(
            self.get_changes(InventoryOwner.ZONES, InventoryOperation.REMOVE),
        )

        if remove_texts:
            transfo_text = " ".join(remove_texts)
            transfo_text += " "

        transfo_text += "> "

        add_texts = []
        add_texts += _stacks_str(
            self.get_changes(InventoryOwner.PLAYER, InventoryOperation.ADD)
        )
        add_texts += _stacks_str(
            self.get_changes(InventoryOwner.CURRENT, InventoryOperation.ADD),
            "Zone(",
            ")",
        )
        add_texts += _stacks_str(
            self.get_changes(InventoryOwner.DESTINATION, InventoryOperation.ADD),
            "Dest(",
            ")",
        )
        add_texts += _dict_stacks_str(
            self.get_changes(InventoryOwner.ZONES, InventoryOperation.ADD)
        )
        if add_texts:
            transfo_text += " ".join(add_texts)
            if self.destination is not None:
                transfo_text += " "

        if self.destination is not None:
            transfo_text += f"| {self.destination.name}"

        return transfo_text


def _update_inventory(
    owner: InventoryOwner,
    player_inventory: np.ndarray,
    position: np.ndarray,
    zones_inventories: np.ndarray,
    destination: np.ndarray,
    operation_arr: np.ndarray,
):
    position_slot: int = position.nonzero()[0]
    if owner is InventoryOwner.PLAYER:
        player_inventory[...] += operation_arr
    elif owner is InventoryOwner.CURRENT:
        zones_inventories[position_slot, :] += operation_arr
    elif owner is InventoryOwner.DESTINATION:
        destination_slot: int = destination.nonzero()[0]
        zones_inventories[destination_slot, :] += operation_arr
    elif owner is InventoryOwner.ZONES:
        zones_inventories[...] += operation_arr
    else:
        raise NotImplementedError


def _build_apply_operation_array(
    operations: InventoryOperations,
) -> Optional[np.ndarray]:
    apply_operation = None
    if InventoryOperation.ADD in operations:
        add_op = operations[InventoryOperation.ADD]
        if apply_operation is None:
            apply_operation = np.zeros_like(add_op)
        apply_operation += add_op
    if InventoryOperation.REMOVE in operations:
        rem_op = operations[InventoryOperation.REMOVE]
        if apply_operation is None:
            apply_operation = np.zeros_like(rem_op)
        apply_operation -= rem_op
    return apply_operation


def _dict_stacks_str(dict_of_stacks: Optional[Dict[Zone, List["ItemStack"]]]):
    strings = []
    if dict_of_stacks is None:
        return strings
    for zone, stacks in dict_of_stacks.items():
        strings += _stacks_str(stacks, f"{zone.name}(", ")")
    return strings


def _stacks_str(
    stacks: Optional[List["ItemStack"]],
    prefix: str = "",
    suffix: str = "",
) -> List[str]:
    strings = []
    if stacks is None:
        return strings
    strings.append(_unstacked_str(stacks, prefix, suffix))
    return strings


def _unstacked_str(itemstacks: List["ItemStack"], prefix: str = "", suffix: str = ""):
    items_text = ",".join([str(itemstack) for itemstack in itemstacks])
    return f"{prefix}{items_text}{suffix}"


def _stack_items_list(
    items_or_stacks: Optional[List[Union["Item", "ItemStack"]]]
) -> Optional[List["ItemStack"]]:
    if items_or_stacks is None:
        return None
    for i, item_or_stack in enumerate(items_or_stacks):
        if not isinstance(item_or_stack, ItemStack):
            items_or_stacks[i] = ItemStack(item_or_stack)
    return items_or_stacks


def _group_zones_operations(
    inventory_changes: Dict[InventoryOwner, InventoryChanges]
) -> Dict[InventoryOwner, InventoryChanges]:
    zones = InventoryOwner.ZONES
    for owner_or_zone in list(inventory_changes.keys()):
        if not isinstance(owner_or_zone, Zone):
            continue
        if zones not in inventory_changes:
            inventory_changes[zones] = {}

        changes = inventory_changes.pop(owner_or_zone)
        for operation, stacks in changes.items():
            if operation not in inventory_changes[zones]:
                inventory_changes[zones][operation] = {}
            inventory_changes[zones][operation][owner_or_zone] = stacks
    return inventory_changes


def _format_inventory_changes(
    dict_of_items_or_stacks: Optional[Dict[InventoryOwner, InventoryChanges]]
) -> Dict[InventoryOwner, InventoryChanges]:
    dict_of_stacks = {}
    if dict_of_items_or_stacks is None:
        return dict_of_stacks

    dict_of_items_or_stacks = _group_zones_operations(dict_of_items_or_stacks)

    for owner, sub_dict in dict_of_items_or_stacks.items():
        owner = InventoryOwner(owner)
        if owner is not InventoryOwner.ZONES:
            dict_of_stacks[owner] = {
                InventoryOperation(op): _stack_items_list(items_or_stacks)
                for op, items_or_stacks in sub_dict.items()
            }
            continue
        if owner not in dict_of_stacks:
            dict_of_stacks[owner] = {}
        for op, zones_items_or_stacks in sub_dict.items():
            zones_stacks = {
                zone: _stack_items_list(items_or_stacks)
                for zone, items_or_stacks in zones_items_or_stacks.items()
            }
            dict_of_stacks[owner][InventoryOperation(op)] = zones_stacks

    return dict_of_stacks


def _items_from_stack_list(stacks: List["ItemStack"]) -> Set["Item"]:
    return set(stack.item for stack in stacks)
