"""# Transformation

## Examples

```python
from hcraft.elements import Item, Stack, Zone
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE
```

### Add an item in player inventory
```python
DIRT = Item("dirt")
search_for_dirt = Transformation(
    "search_for_dirt",
    inventory_changes=[Yield(PLAYER, DIRT)],
)
```

### Modify the player position
```python
FOREST = Zone("forest")
move_to_forest = Transformation(
    "move_to_forest",
    destination=FOREST,
)
```

### Restrict a transformation to a set of zones
```python
WOOD = Item("wood")
search_for_wood = Transformation(
    "search_for_wood",
    inventory_changes=[Yield(PLAYER, WOOD)],
    zones=[FOREST],
)
```

### Modify the player inventory
```python
PLANK = Item("plank")
craft_wood_plank = Transformation(
    "craft_wood_plank",
    inventory_changes=[
        Use(PLAYER, WOOD, consume=1),
        Yield(PLAYER, PLANK, 4)
    ],
)
```
Note the use of Stack to give a quantity > 1.

### Modify the current zone's inventory
```python
HOUSE = Item("house")  # Need 12 WOOD and 64 PLANK to
build_house = Transformation(
    "build_house",
    inventory_changes=[
        Use(PLAYER, WOOD, 12),
        Use(PLAYER, PLANK, 64),
        Yield(CURRENT_ZONE, HOUSE),
    ],
)
```

### Move with a cost
```python
TREETOPS = Zone("treetops")
LADDER = Item("ladder")
climb_tree = Transformation(
    "climb_tree",
    destination=TREETOPS,
    inventory_changes=[Use(PLAYER, LADDER, consume=1)],
    zones=[FOREST],
)
```

### Modify the destination's inventory
```python
# Jump from treetops
CRATER = Item("crater")
jump_from_tree = Transformation(
    "jump_from_tree",
    destination=FOREST,
    inventory_changes=[Yield("destination", CRATER)],
    zones=[TREETOPS],
)
```

### Move with a required item and required item in zone
```python
INSIDE_HOUSE = Zone("house")
DOOR = Item("door")
KEY = Item("key")
enter_house = Transformation(
    destination=INSIDE_HOUSE,
    inventory_changes=[
        Use(PLAYER, KEY),  # Ensure has key
        Use(CURRENT_ZONE, DOOR),  # Ensure has door
    ],
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
press_red_button = Transformation(
    "press_red_button",
    inventory_changes=[
        Use(CURRENT_ZONE, STRANGE_RED_BUTTON),  # Ensure has door
        Yield(SPACE, INCOMING_MISSILES),  # An 'absolute' specific zone
    ],
)
```
Note that the player may not see the effect of such a transformation,
because the player only observe the current zone items.


"""


from typing import TYPE_CHECKING, Dict, List, Optional, Set, Tuple, Union, Any
from enum import Enum
from dataclasses import dataclass

import numpy as np

from hcraft.elements import Item, Stack, Zone

if TYPE_CHECKING:
    from hcraft.env import HcraftState
    from hcraft.world import World


class InventoryOwner(Enum):
    """Enumeration of possible owners of inventory changes."""

    PLAYER = "player"
    """The player inventory"""
    CURRENT = "current_zone"
    """The current zone inventory"""
    DESTINATION = "destination"
    """The destination zone inventory"""
    ZONES = "zones"
    """A specific zone inventory"""


PLAYER = InventoryOwner.PLAYER
CURRENT_ZONE = InventoryOwner.CURRENT
DESTINATION = InventoryOwner.DESTINATION


@dataclass()
class Use:
    """Use the given item in the given inventory."""

    owner: Union[InventoryOwner, Zone]
    """Owner of the inventory to change."""
    item: Item
    """Item to use."""
    consume: int = 0
    """Amout of the item to remove from the inventory. Defaults to 0."""
    min: Optional[int] = None
    """Minimum amout of the item *before* the transformation to be valid.

    By default, min is 1 if consume is 0, else min=consume.

    """

    def __post_init__(self):
        if not isinstance(self.owner, Zone):
            self.owner = InventoryOwner(self.owner)
        if self.min is None:
            self.min = self.consume if self.consume > 0 else 1


@dataclass()
class Yield:
    """Yield the given item in the given inventory."""

    owner: Union[InventoryOwner, Zone]
    """Owner of the inventory to change."""
    item: Item
    """Item to use."""
    create: int = 1
    """Amout of the item to create in the inventory. Defaults to 1."""
    max: int = np.inf
    """Maximum amout of the item *before* the transformation to be valid. Defaults to inf."""

    def __post_init__(self):
        if not isinstance(self.owner, Zone):
            self.owner = InventoryOwner(self.owner)


class InventoryOperation(Enum):
    """Enumeration of operations that can be done on an inventory."""

    REMOVE = "remove"
    """Remove the list of stacks."""
    ADD = "add"
    """Add the list of stacks."""
    MAX = "max"
    """Superior limit to the list of stacks *before* the transformation."""
    MIN = "min"
    """Inferior limit to the list of stacks *before* the transformation."""
    APPLY = "apply"
    """Effects of applying the transformation."""


InventoryChange = Union[Use, Yield]
InventoryChanges = Dict[
    InventoryOperation,
    Union[List[Union[Item, Stack]], Dict[Zone, List[Union[Item, Stack]]]],
]
InventoryOperations = Dict[InventoryOperation, np.ndarray]


class Transformation:
    """The building blocks of every HierarchyCraft environment.

    A list of transformations is what defines each HierarchyCraft environement.
    Transformation becomes the available actions and all available transitions of the environment.

    Each transformation defines changes of:

    * the player inventory
    * the player position to a given destination
    * the current zone inventory
    * the destination zone inventory (if a destination is specified).
    * all specific zones inventories

    Each inventory change is a list of removed (-) and added (+) Stack.

    If specified, they may be restricted to only a subset of valid zones,
    all zones are valid by default.

    A Transformation can only be applied if valid in the given state.
    A transformation is only valid if the player in a valid zone
    and all relevant inventories have enough items to be removed *before* adding new items.

    The picture bellow illustrates the impact of
    an example transformation on a given `hcraft.HcraftState`:
    <img
        src="https://raw.githubusercontent.com/IRLL/HierarchyCraft/master/docs/images/hcraft_transformation.png"
    width="90%"/>

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
        name: Optional[str] = None,
        destination: Optional[Zone] = None,
        inventory_changes: Optional[List[InventoryChange]] = None,
        zones: Optional[List[Zone]] = None,
    ) -> None:
        """The building blocks of every HierarchyCraft environment.

        Args:
            destination: Destination zone.
                Defaults to None.
            inventory_changes: List of inventory changes done by this transformation.
                Defaults to None.
            zones: List of valid zones, if None all zones are valid.
                Defaults to None.
        """
        self.destination = destination
        self._destination = None

        self.zones = zones
        self._zones = None

        self._changes_list = inventory_changes
        self.inventory_changes = _format_inventory_changes(inventory_changes)
        self._inventory_operations: Optional[
            Dict[InventoryOwner, InventoryOperations]
        ] = None

        self.name = name if name is not None else self.__repr__()

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

    def is_valid(self, state: "HcraftState") -> bool:
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
        self, owner: InventoryOwner, operation: InventoryOperation, default: Any = None
    ) -> Optional[Union[List[Stack], Dict[Zone, List[Stack]]]]:
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
        return operations.get(operation, default)

    def production(self, owner: InventoryOwner) -> Set["Item"]:
        """Set of produced items for the given owner by this transformation."""
        return self._relevant_items_changed(owner, InventoryOperation.ADD)

    def consumption(self, owner: InventoryOwner) -> Set["Item"]:
        """Set of consumed items for the given owner by this transformation."""
        return self._relevant_items_changed(owner, InventoryOperation.REMOVE)

    def min_required(self, owner: InventoryOwner) -> Set["Item"]:
        """Set of items for which a minimum is required by this transformation
        for the given owner."""
        return self._relevant_items_changed(owner, InventoryOperation.MIN)

    def max_required(self, owner: InventoryOwner) -> Set["Item"]:
        """Set of items for which a maximum is required by this transformation
        for the given owner."""
        return self._relevant_items_changed(owner, InventoryOperation.MAX)

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

    @property
    def min_required_zones_items(self) -> Set["Item"]:
        """Set of zone items for which a minimum is required by this transformation."""
        return (
            self.min_required(InventoryOwner.CURRENT)
            | self.min_required(InventoryOwner.DESTINATION)
            | self.min_required(InventoryOwner.ZONES)
        )

    @property
    def max_required_zones_items(self) -> Set["Item"]:
        """Set of zone items for which a maximum is required by this transformation."""
        return (
            self.max_required(InventoryOwner.CURRENT)
            | self.max_required(InventoryOwner.DESTINATION)
            | self.max_required(InventoryOwner.ZONES)
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
        min_items: Optional[np.ndarray],
    ):
        added = 0 if added is None else added
        removed = 0 if removed is None else removed
        if max_items is not None and np.any(inventory > max_items):
            return False
        if min_items is not None and np.any(inventory < min_items):
            return False
        return True

    def _is_valid_player_inventory(self, player_inventory: np.ndarray):
        items_changes = self._inventory_operations.get(InventoryOwner.PLAYER, {})
        added = items_changes.get(InventoryOperation.ADD, 0)
        removed = items_changes.get(InventoryOperation.REMOVE)
        max_items = items_changes.get(InventoryOperation.MAX)
        min_items = items_changes.get(InventoryOperation.MIN)
        return self._is_valid_inventory(
            player_inventory, added, removed, max_items, min_items
        )

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
        min_items = zones_changes.get(InventoryOperation.MIN, zeros.copy())

        # Current zone
        current_changes = self._inventory_operations.get(InventoryOwner.CURRENT, {})
        current_slot = position.nonzero()[0]
        added[current_slot] += current_changes.get(InventoryOperation.ADD, 0)
        removed[current_slot] += current_changes.get(InventoryOperation.REMOVE, 0)
        max_items[current_slot] = np.minimum(
            max_items[current_slot],
            current_changes.get(InventoryOperation.MAX, np.inf),
        )
        min_items[current_slot] = np.maximum(
            min_items[current_slot],
            current_changes.get(InventoryOperation.MIN, -np.inf),
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
            min_items[dest_slot] = np.maximum(
                min_items[dest_slot],
                dest_changes.get(InventoryOperation.MIN, -np.inf),
            )

        return self._is_valid_inventory(
            zones_inventories, added, removed, max_items, min_items
        )

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
        stacks: List[Stack],
        world_items_list: List["Item"],
        default_value: int = 0,
    ) -> np.ndarray:
        operation = default_value * np.ones(len(world_items_list), dtype=np.int32)
        for stack in stacks:
            item_slot = world_items_list.index(stack.item)
            operation[item_slot] = stack.quantity
        return operation

    def _build_zones_items_op(
        self,
        stacks_per_zone: Dict[Zone, List["Stack"]],
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
        return self.name

    def __repr__(self) -> str:
        return f"{self._preconditions_repr()}=>{self._effects_repr()}"

    def _preconditions_repr(self) -> str:
        preconditions_text = ""

        owners_brackets = {
            PLAYER: ".",
            CURRENT_ZONE: "Zone(.)",
            DESTINATION: "Dest(.)",
        }

        for owner in InventoryOwner:
            if owner is InventoryOwner.ZONES:
                continue
            owner_texts = []
            owner_texts += _stacks_precontions_str(
                self.get_changes(owner, InventoryOperation.MIN),
                symbol=">",
            )
            owner_texts += _stacks_precontions_str(
                self.get_changes(owner, InventoryOperation.MAX),
                symbol="<",
            )
            stacks_text = ",".join(owner_texts)
            if not owner_texts:
                continue
            if preconditions_text:
                preconditions_text += " "
            preconditions_text += owners_brackets[owner].replace(".", stacks_text)

        zones_specific_ops: Dict[Zone, Dict[InventoryOperation, List[Stack]]] = {}
        for op, zones_stacks in self.inventory_changes.get(
            InventoryOwner.ZONES, {}
        ).items():
            for zone, stacks in zones_stacks.items():
                if zone not in zones_specific_ops:
                    zones_specific_ops[zone] = {}
                if op not in zones_specific_ops[zone]:
                    zones_specific_ops[zone][op] = []
                zones_specific_ops[zone][op] += stacks

        for zone, operations in zones_specific_ops.items():
            owner_texts = []
            owner_texts += _stacks_precontions_str(
                operations.get(InventoryOperation.MIN, []),
                symbol=">",
            )
            owner_texts += _stacks_precontions_str(
                operations.get(InventoryOperation.MAX, []),
                symbol="<",
            )
            stacks_text = ",".join(owner_texts)
            if not owner_texts:
                continue
            if preconditions_text:
                preconditions_text += " "
            preconditions_text += f"{zone.name}({stacks_text})"

        if self.zones is not None:
            if preconditions_text:
                preconditions_text += " "
            zones_str = ",".join([zone.name for zone in self.zones])
            preconditions_text += f"| {zones_str}"

        if preconditions_text:
            preconditions_text += " "

        return preconditions_text

    def _effects_repr(self) -> str:
        effects_text = ""
        owners_brackets = {
            PLAYER: ".",
            CURRENT_ZONE: "Zone(.)",
            DESTINATION: "Dest(.)",
        }

        for owner in InventoryOwner:
            if owner is InventoryOwner.ZONES:
                continue
            owner_texts = []
            owner_texts += _stacks_effects_str(
                self.get_changes(owner, InventoryOperation.REMOVE),
                stack_prefix="-",
            )
            owner_texts += _stacks_effects_str(
                self.get_changes(owner, InventoryOperation.ADD),
                stack_prefix="+",
            )
            stacks_text = ",".join(owner_texts)
            if not owner_texts:
                continue
            effects_text += " "
            effects_text += owners_brackets[owner].replace(".", stacks_text)

        zones_specific_ops: Dict[Zone, Dict[InventoryOperation, List[Stack]]] = {}
        for op, zones_stacks in self.inventory_changes.get(
            InventoryOwner.ZONES, {}
        ).items():
            for zone, stacks in zones_stacks.items():
                if zone not in zones_specific_ops:
                    zones_specific_ops[zone] = {}
                if op not in zones_specific_ops[zone]:
                    zones_specific_ops[zone][op] = []
                zones_specific_ops[zone][op] += stacks

        for zone, operations in zones_specific_ops.items():
            owner_texts = []
            owner_texts += _stacks_effects_str(
                operations.get(InventoryOperation.REMOVE, []),
                stack_prefix="-",
            )
            owner_texts += _stacks_effects_str(
                operations.get(InventoryOperation.ADD, []),
                stack_prefix="+",
            )
            stacks_text = ",".join(owner_texts)
            if not owner_texts:
                continue
            effects_text += " "
            effects_text += f"{zone.name}({stacks_text})"

        if self.destination is not None:
            effects_text += " "
            effects_text += f"| {self.destination.name}"

        return effects_text


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


def _stacks_effects_str(
    stacks: Optional[List["Stack"]],
    prefix: str = "",
    suffix: str = "",
    stack_prefix: str = "",
) -> List[str]:
    strings = []
    if not stacks:
        return strings
    strings.append(_unstacked_str(stacks, prefix, suffix, stack_prefix))
    return strings


def _stacks_precontions_str(
    stacks: Optional[List["Stack"]],
    prefix: str = "",
    suffix: str = "",
    symbol: str = "",
) -> List[str]:
    strings = []
    if not stacks:
        return strings
    strings.append(_unstacked_condition_str(stacks, prefix, suffix, symbol))
    return strings


def _unstacked_condition_str(
    stacks: List["Stack"], prefix: str = "", suffix: str = "", symbol: str = ""
):
    items_text = ",".join(
        [f"{stack.item.name}{symbol}{stack.quantity}" for stack in stacks]
    )
    return f"{prefix}{items_text}{suffix}"


def _unstacked_str(
    stacks: List["Stack"], prefix: str = "", suffix: str = "", stack_prefix: str = ""
):
    items_text = ",".join([f"{stack_prefix}{stack}" for stack in stacks])
    return f"{prefix}{items_text}{suffix}"


def _append_changes(
    dict_of_changes: Dict[InventoryOwner, InventoryChanges],
    change: InventoryChange,
    zone: Optional[Zone] = None,
):
    owner = change.owner
    if zone is not None:
        owner = InventoryOwner.ZONES

    if owner not in dict_of_changes:
        dict_of_changes[owner] = {}

    def _append_stack(operation: InventoryOperation, stack: Stack):
        if operation not in dict_of_changes[owner]:
            dict_of_changes[owner][operation] = []
            if zone is not None:
                dict_of_changes[owner][operation] = {}

        if zone is None:
            dict_of_changes[owner][operation].append(stack)
            return

        if zone not in dict_of_changes[owner][operation]:
            dict_of_changes[owner][operation][zone] = []
        dict_of_changes[owner][operation][zone].append(stack)

    if isinstance(change, Use):
        if change.min > -np.inf:
            min_stack = Stack(change.item, change.min)
            _append_stack(InventoryOperation.MIN, min_stack)

        if change.consume > 0:
            rem_stack = Stack(change.item, change.consume)
            _append_stack(InventoryOperation.REMOVE, rem_stack)

    elif isinstance(change, Yield):
        if change.max < np.inf:
            max_stack = Stack(change.item, change.max)
            _append_stack(InventoryOperation.MAX, max_stack)

        if change.create > 0:
            add_stack = Stack(change.item, change.create)
            _append_stack(InventoryOperation.ADD, add_stack)


def _format_inventory_changes(
    list_of_changes: Optional[List[InventoryChange]],
) -> Dict[InventoryOwner, InventoryChanges]:
    dict_of_stacks = {}
    if list_of_changes is None:
        return dict_of_stacks

    for inv_change in list_of_changes:
        zone = None
        if isinstance(inv_change.owner, Zone):
            zone = inv_change.owner
        _append_changes(dict_of_stacks, inv_change, zone=zone)
    return dict_of_stacks


def _items_from_stack_list(stacks: List["Stack"]) -> Set["Item"]:
    return set(stack.item for stack in stacks)
