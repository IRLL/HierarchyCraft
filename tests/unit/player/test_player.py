# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=attribute-defined-outside-init

import pytest

from crafting.world.items import Item, Tool
from crafting.world.zones import Zone
from crafting.player.player import Player
from crafting.player.inventory import Inventory


class TestPlayer:
    "Player"

    @pytest.fixture(autouse=True)
    def setup(self):
        """ Setup variables. """
        self.egg = Item(666, 'egg')

        self.wooden_axe = Tool(18, 'wooden_axe')
        self.wood = Item(17, 'wood', required_tools=[None, self.wooden_axe])

        self.wooden_pickaxe = Tool(18, 'wooden_pickaxe')
        self.stone = Item(1, 'stone', required_tools=[self.wooden_pickaxe])

        self.forest = Zone(
            zone_id=0,
            name='forest',
            properties={'has_crafting': False, 'has_furnace': False},
            items=[self.egg, self.wood, self.stone]
        )

        self.inventory = Inventory([self.egg, self.wood, self.stone])

    def test_init(self):
        """ should instanciate correctly. """
        self.player = Player(self.inventory, self.forest)
