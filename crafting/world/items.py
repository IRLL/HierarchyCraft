# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

from typing import List, Tuple, Union


class Item():

    def __init__(self, id: int, name: str, max_stack: int=1):
        self.id = id
        self.name = name
        self.max_stack = max_stack
    
    def __repr__(self):
        return f"{self.name.capitalize()}({self.id})"


class Tool(Item):

    def __init__(self, id: int, name: str, params: dict):
        super().__init__(id, name, max_stack=1)
        self.params = list(params.keys())
        for name, value in params.items():
            setattr(self, name, value)

    def __repr__(self):
        params = [getattr(self, param) for param in self.params]
        return f"{self.name.capitalize()}({self.id}){params}"


class ItemStack(Item):

    def __init__(self, item: Item, size):
        super().__init__(id, name, max_stack=1)
        self.item = item
        self.size = size

    def add(self, size: int) -> List[Item]:
        new_size = self.size + size
        if new_size <= self.max_size:
            return [ItemStack(self.item, new_size)]
        else:
            new_stack = ItemStack(self.item, 0)
            new_stacks = new_stack.add(new_size - self.max_size)
            return [ItemStack(self.item, self.max_size)] + new_stacks

    def sub(self, size: int) -> List[Item]:
        if self.size == size:
            return []
        elif self.size > size:
            return [ItemStack(self.item, self.size - size)]
        else:
            raise ValueError("Not enough in initial stack to remove")

    def __add__(self, other: Item) -> List[Item]:
        assert isinstance(other, ItemStack)
        assert self.id == other.id
        return self.add(other.size)

    def __sub__(self, other: Item) -> List[Item]:
        assert isinstance(other, ItemStack)
        assert self.id == other.id
        return self.sub(other.size)

    def __repr__(self) -> str:
        return f"{self.size} {self.name.capitalize()}({self.id})"

