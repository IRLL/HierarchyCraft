from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    name: str


@dataclass(frozen=True)
class Zone:
    name: str
