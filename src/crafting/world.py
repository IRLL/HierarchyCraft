from typing import List

from dataclasses import dataclass


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
