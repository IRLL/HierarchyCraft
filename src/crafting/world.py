"""# World

The World is what is given to the general CraftingEnv class
to instanciate each individual Crafting environment.

It represents the mapping between items, zones and zone items to their state indexes.

A world can always be built from a list of transformations using 
`crafting.world.world_from_transformations`.



## Example

Build a World from a list of transformations,
starting in zone "Start zone",
with items "Head" and 2 "Hand",
with a zone "Secret zone" containing items "Secret item" and 3 "Gold tresure".


```python
from crafting.elements import Item, ItemStack, Zone, world_from_transformations

transformations: List["Transformation"] = ...
world = world_from_transformations(
    transformations=transformations,
    start_zone=Zone("Start zone"),
    start_items=[Item("Head"), ItemStack(Item("Hand"), 2)],
    start_zones_items={
        Zone("Secret zone"): [Item("Secret item"), ItemStack(Item("Gold tresure"), 3)]
    }
)
```

"""

import os
from dataclasses import dataclass, field
from functools import partial
from typing import TYPE_CHECKING, List, Set, Dict, Tuple, Optional, Union

from crafting.elements import Item, ItemStack, Zone
from crafting.requirements import Requirements, RequirementNode, req_node_name

if TYPE_CHECKING:
    from crafting.transformation import Transformation


def _default_resources_path() -> str:
    current_dir = os.path.dirname(__file__)
    return os.path.join(current_dir, "render", "default_resources")


@dataclass()
class World:
    """Contain all elements a crafting environment will have

    Elements are items, zones, zones_items and transformations
    Also contain optional start_zone, start_items and start_zones_items.
    """

    items: List[Item]
    zones: List[Zone]
    zones_items: List[Item]
    transformations: List["Transformation"] = field(default_factory=list)

    start_zone: Optional[Zone] = None
    start_items: List[ItemStack] = field(default_factory=list)
    start_zones_items: Dict[Zone, List[ItemStack]] = field(default_factory=dict)

    resources_path: str = field(default_factory=_default_resources_path)
    order_world: bool = False

    def __post_init__(self):
        self._requirements = None

        if self.order_world:
            item_rank = partial(
                _get_node_level, self.requirements, node_type=RequirementNode.ITEM
            )
            self.items.sort(key=item_rank)

            zone_item_rank = partial(
                _get_node_level, self.requirements, node_type=RequirementNode.ZONE_ITEM
            )
            self.zones_items.sort(key=zone_item_rank)

            zone_rank = partial(
                _get_node_level, self.requirements, node_type=RequirementNode.ZONE
            )
            self.zones.sort(key=zone_rank)

        for transfo in self.transformations:
            transfo.build(self)

    @property
    def n_items(self) -> int:
        """Number of different items the player can have."""
        return len(self.items)

    @property
    def n_zones(self) -> int:
        """Number of different zones."""
        return len(self.zones)

    @property
    def n_zones_items(self) -> int:
        """Number of different items the zones can have."""
        return len(self.zones_items)

    @property
    def requirements(self) -> Requirements:
        """Requirements object to draw an manipulate requirements graph.

        See `crafting.requirements` for more details.

        """
        if self._requirements is None:
            self._requirements = Requirements(self)
        return self._requirements

    def slot_from_item(self, item: Item) -> int:
        """Item's slot in the world"""
        return self.items.index(item)

    def slot_from_zone(self, zone: Zone) -> int:
        """Zone's slot in the world"""
        return self.zones.index(zone)

    def slot_from_zoneitem(self, zone: Zone) -> int:
        """Item's slot in the world as a zone item."""
        return self.zones_items.index(zone)


def world_from_transformations(
    transformations: List["Transformation"],
    start_zone: Optional[Zone] = None,
    start_items: Optional[List[Union[ItemStack, Item]]] = None,
    start_zones_items: Optional[Dict[Zone, List[Union[ItemStack, Item]]]] = None,
    order_world: bool = True,
) -> World:
    """Reads the transformation to build the list of items, zones and zones_items
    composing the world."""
    start_items = start_items if start_items is not None else []
    for i, stack in enumerate(start_items):
        if not isinstance(stack, ItemStack):
            start_items[i] = ItemStack(stack)
    start_zones_items = start_zones_items if start_zones_items is not None else {}
    for zone, items in start_zones_items.items():
        for i, stack in enumerate(items):
            if not isinstance(stack, ItemStack):
                start_zones_items[zone][i] = ItemStack(stack)

    zones, items, zones_items = _start_elements(
        start_zone, start_items, start_zones_items
    )

    for transfo in transformations:
        zones, items, zones_items = _transformations_elements(
            transfo, zones, items, zones_items
        )

    return World(
        items=list(items),
        zones=list(zones),
        zones_items=list(zones_items),
        transformations=transformations,
        start_zone=start_zone,
        start_items=start_items,
        start_zones_items=start_zones_items,
        order_world=order_world,
    )


def _start_elements(
    start_zone: Optional[Zone],
    start_items: List[Union[ItemStack, Item]],
    start_zones_items: Dict[Zone, List[Union[ItemStack, Item]]],
) -> Tuple[Set[Zone], Set[Item], Set[Item]]:
    zones = set()
    if start_zone is not None:
        zones.add(start_zone)

    items = set(itemstack.item for itemstack in start_items)
    zones_items = set()
    for zone, zone_items in start_zones_items.items():
        zones.add(zone)
        zones_items |= set(itemstack.item for itemstack in zone_items)
    return zones, items, zones_items


def _transformations_elements(
    transfo: "Transformation",
    zones: Set[Zone],
    items: Set[Item],
    zones_items: Set[Item],
) -> Tuple[Set[Zone], Set[Item], Set[Item]]:
    if transfo.destination is not None:
        zones.add(transfo.destination)
    if transfo.zones is not None:
        zones |= set(transfo.zones)
    items = _add_items_to(transfo.removed_player_items, items)
    items = _add_items_to(transfo.added_player_items, items)
    zones_items = _add_items_to(transfo.removed_destination_items, zones_items)
    zones_items = _add_items_to(transfo.added_destination_items, zones_items)
    zones_items = _add_items_to(transfo.removed_zone_items, zones_items)
    zones_items = _add_items_to(transfo.added_zone_items, zones_items)
    zones_items, zones = _add_dict_items_to(
        transfo.removed_zones_items, zones_items, zones
    )
    zones_items, zones = _add_dict_items_to(
        transfo.added_zones_items, zones_items, zones
    )
    return zones, items, zones_items


def _get_node_level(
    requirements: Requirements, obj: Union[Item, Zone], node_type: RequirementNode
):
    node_name = req_node_name(obj, node_type=node_type)
    return (requirements.graph.nodes[node_name].get("level", 1000), node_name)


def _add_items_to(stacks: Optional[List[ItemStack]], items_set: Set[Item]):
    if stacks is not None:
        for itemstack in stacks:
            items_set.add(itemstack.item)
    return items_set


def _add_dict_items_to(
    dict_of_stacks: Optional[Dict[Zone, List[ItemStack]]],
    items_set: Set[Item],
    zones_set: Set[Zone],
):
    if dict_of_stacks is not None:
        for zone, stacks in dict_of_stacks.items():
            zones_set.add(zone)
            items_set = _add_items_to(stacks, items_set)
    return items_set, zones_set
