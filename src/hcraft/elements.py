from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    """Represent an item for any hcraft environement."""

    name: str


@dataclass(frozen=True)
class Stack:
    """Represent a stack of an item for any hcraft environement"""

    item: Item
    quantity: int = 1

    def __str__(self) -> str:
        quantity_str = f"[{self.quantity}]" if self.quantity > 1 else ""
        return f"{quantity_str}{self.item.name}"


@dataclass(frozen=True)
class Zone:
    """Represent a zone for any hcraft environement."""

    name: str
