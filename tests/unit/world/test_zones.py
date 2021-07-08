# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=attribute-defined-outside-init

import pytest
import pytest_check as check

from crafting.world.zones import Zone
from crafting.world.items import Tool, Item

class TestZone:
    "Zone"

    @pytest.fixture(autouse=True)
    def setup(self):
        """ Setup reused variables. """
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

    def test_zone_str(self):
        """ should be converted to string correctly. """
        check.equal(str(self.forest), "Forest(0)")

    def test_zone_repr(self):
        """ should be represented correctly. """
        expected_repr = "Forest(0)" + \
            "{'has_crafting': False, 'has_furnace': False}" + \
            "[Egg(666), Wood(17), Stone(1)]"
        check.equal(repr(self.forest), expected_repr)

    def test_zone_search_with_required(self):
        """ should allow finding with proper tools, but not without. """
        findings_with_pick = self.forest.search_for(self.stone, self.wooden_pickaxe)
        check.equal(findings_with_pick[0].item_id, self.stone.item_id,
            msg=f"Unexpected findings with wooden_pickaxe {findings_with_pick}")

        findings_with_none = self.forest.search_for(self.stone, None)
        check.equal(len(findings_with_none), 0,
            msg=f"Unexpected findings with None {findings_with_none}")

    def test_zone_search_with_none_required(self):
        """ should allow finding without proper tool if None is requried. """

        # When required_tools is None
        findings_with_pick = self.forest.search_for(self.egg, None)
        check.equal(findings_with_pick[0].item_id, self.egg.item_id,
            msg=f"Unexpected findings with None {findings_with_pick}")

        # When None is in required_tools
        findings_with_pick = self.forest.search_for(self.wood, None)
        check.equal(findings_with_pick[0].item_id, self.wood.item_id,
            msg=f"Unexpected findings with None {findings_with_pick}")
