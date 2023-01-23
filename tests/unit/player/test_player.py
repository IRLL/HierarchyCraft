# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

import pytest
import pytest_check as check

from crafting.world.items import Item, Tool, ItemStack
from crafting.world.zones import Zone
from crafting.player.player import Player
from crafting.player.inventory import Inventory


class TestPlayer:
    "Player"

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup variables."""
        self.egg = Item(666, "egg")

        self.wooden_axe = Tool(18, "wooden_axe")
        self.wood = Item(17, "wood", required_tools=[None, self.wooden_axe])

        self.wooden_pickaxe = Tool(18, "wooden_pickaxe")
        self.stone = Item(1, "stone", required_tools=[self.wooden_pickaxe])

        self.forest = Zone(
            zone_id=0,
            name="forest",
            properties={"has_crafting": False, "has_furnace": False},
            items=[self.egg, self.wood, self.stone],
        )

        self.caves = Zone(
            zone_id=1,
            name="caves",
            properties={
                "has_crafting": False,
                "has_furnace": False,
                "nether_portal": True,
            },
            items=[self.stone],
            required_tools=[self.wooden_pickaxe],
        )

        self.nether = Zone(
            zone_id=2,
            name="nether",
            items=[self.stone],
            properties={"nether_portal": True},
            required_properties={"nether_portal": True},
        )

        self.inventory = Inventory(
            [
                self.egg,
                self.wood,
                self.stone,
                self.wooden_pickaxe,
                self.wooden_axe,
            ]
        )

    def test_can_move_to_caves_only_with_pickaxe(self):
        """should be able to move to caves only with pickaxe in inventory."""
        player = Player(self.inventory, self.forest)
        check.is_false(player.can_move_to(self.caves))

        player.inventory.add_stacks([ItemStack(self.wooden_pickaxe)])
        check.is_true(player.can_move_to(self.caves))

    def test_can_move_to_nether_only_with_portal(self):
        """should be able to move to caves only with pickaxe in inventory."""
        player = Player(self.inventory, self.forest)
        check.is_false(
            player.can_move_to(self.nether),
            "could move without the portal property",
        )

        player.zone = self.caves
        check.is_true(
            player.can_move_to(self.nether),
            "couldn't move with the portal property",
        )
