from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Set, Dict, Optional

if TYPE_CHECKING:
    from crafting.transformation import Transformation


@dataclass(frozen=True)
class Item:
    name: str


@dataclass(frozen=True)
class ItemStack:
    item: Item
    quantity: int = 1

    def __str__(self) -> str:
        name = self.item.name
        if self.quantity > 1:
            name += f"[{self.quantity}]"
        return name


@dataclass(frozen=True)
class Zone:
    name: str


@dataclass(frozen=True)
class Player:
    name: str = "Player"


@dataclass(frozen=True)
class World:
    items: List[Item]
    zones: List[Zone]
    zones_items: List[Item]
    transformations: List["Transformation"] = field(default_factory=list)

    start_zone: Optional[Zone] = None
    start_items: List[ItemStack] = field(default_factory=list)
    start_zones_items: Dict[Zone, List[ItemStack]] = field(default_factory=dict)

    def __post_init__(self):
        for transfo in self.transformations:
            transfo.build(self)

    @property
    def n_items(self) -> int:
        return len(self.items)

    @property
    def n_zones(self) -> int:
        return len(self.zones)

    @property
    def n_zones_items(self) -> int:
        return len(self.zones_items)

    def slot_from_item(self, item: Item) -> int:
        return self.items.index(item)

    def slot_from_zone(self, zone: Zone) -> int:
        return self.zones.index(zone)

    def slot_from_zoneitem(self, zone: Zone) -> int:
        return self.zones_items.index(zone)


def world_from_transformations(
    transformations: List["Transformation"],
    start_zone: Optional[Zone] = None,
    start_items: Optional[List[ItemStack]] = None,
    start_zones_items: Optional[Dict[Zone, List[ItemStack]]] = None,
) -> World:
    """Reads the transformation to build the list of items, zones and zones_items
    composing the world."""
    start_items = start_items if start_items is not None else []
    start_zones_items = start_zones_items if start_zones_items is not None else {}

    # Start elements
    zones = set()
    if start_zone is not None:
        zones.add(start_zone)

    items = set(itemstack.item for itemstack in start_items)
    zones_items = set()
    for zone, zone_items in start_zones_items.items():
        zones.add(zone)
        zones_items |= set(itemstack.item for itemstack in zone_items)

    # Elements by transformations
    for transfo in transformations:
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

    return World(
        items=list(items),
        zones=list(zones),
        zones_items=list(zones_items),
        transformations=transformations,
        start_zone=start_zone,
        start_items=start_items,
        start_zones_items=start_zones_items,
    )


def _add_items_to(itemstacks: Optional[List[ItemStack]], items_set: Set[Item]):
    if itemstacks is not None:
        for itemstack in itemstacks:
            items_set.add(itemstack.item)
    return items_set
