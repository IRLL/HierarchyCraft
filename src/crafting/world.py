from typing import List

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    name: str


@dataclass(frozen=True)
class Zone:
    name: str


@dataclass(frozen=True)
class World:
    items: List[Item]
    zones: List[Zone]

    @property
    def n_items(self) -> int:
        return len(self.items)

    @property
    def n_zones(self) -> int:
        return len(self.zones)

    def slot_from_item(self, item: Item) -> int:
        return self.items.index(item)

    def slot_from_zone(self, zone: Zone) -> int:
        return self.zones.index(zone)
