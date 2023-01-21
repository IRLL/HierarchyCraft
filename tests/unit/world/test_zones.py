# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2022 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=attribute-defined-outside-init

import pytest
import pytest_check as check

from crafting.world.zones import Zone
from crafting.world.items import Tool, Item


class TestZone:
    "Zone"

    @pytest.fixture(autouse=True)
    def setup(self):
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

    def test_zone_str(self):
        """should be converted to string correctly."""
        check.equal(str(self.forest), "Forest(0)")

    def test_zone_repr(self):
        """should be represented correctly."""
        expected_repr = (
            "Forest(0)"
            + "{'has_crafting': False, 'has_furnace': False}"
            + "[Egg(666), Wood(17), Stone(1)]"
        )
        check.equal(repr(self.forest), expected_repr)

    def test_zone_search_with_required(self):
        """should allow finding with proper tools, but not without."""
        findings_with_pick = self.forest.search_for(self.stone, self.wooden_pickaxe)
        check.equal(
            findings_with_pick[0].item_id,
            self.stone.item_id,
            msg=f"Unexpected findings with wooden_pickaxe {findings_with_pick}",
        )

        findings_with_none = self.forest.search_for(self.stone, None)
        check.equal(
            len(findings_with_none),
            0,
            msg=f"Unexpected findings with None {findings_with_none}",
        )

    def test_zone_search_with_none_required(self):
        """should allow finding without proper tool if None is requried."""

        # When required_tools is None
        findings_with_pick = self.forest.search_for(self.egg, None)
        check.equal(
            findings_with_pick[0].item_id,
            self.egg.item_id,
            msg=f"Unexpected findings with None {findings_with_pick}",
        )

        # When None is in required_tools
        findings_with_pick = self.forest.search_for(self.wood, None)
        check.equal(
            findings_with_pick[0].item_id,
            self.wood.item_id,
            msg=f"Unexpected findings with None {findings_with_pick}",
        )

    def test_reach_by_default(self):
        """should be reachable by any other zone by default (except itself)."""
        check.is_true(self.forest.can_be_reach_from(Zone(1, "otherzone", items=[])))
        check.is_false(self.forest.can_be_reach_from(self.forest))

    def test_accessible_by_default(self):
        """should be accessible using any Tool (even None)."""
        check.is_true(self.forest.can_access_with(Tool(0, "random_tool")))
        check.is_true(self.forest.can_access_with(None))


def test_reach_with_required_property():
    """should be reachable by any other zone
    if and only if the current zone has required properties."""
    nokey_zone = Zone(0, "nokey", items=[])
    false_key_zone = Zone(1, "false_key", items=[], properties={"key": False})
    key_zone = Zone(2, "key", items=[], properties={"key": True})
    goal_zone = Zone(3, "goal", items=[], required_properties={"key": True})

    check.is_false(goal_zone.can_be_reach_from(nokey_zone))
    check.is_false(goal_zone.can_be_reach_from(false_key_zone))
    check.is_true(goal_zone.can_be_reach_from(key_zone))


def test_accessible_with_required_tool():
    """should be accessible if and only if using any of the required Tool."""
    rock = Tool(0, "rock")
    key = Tool(1, "key")
    master_key = Tool(2, "master_key")

    zone = Zone(0, "nokey", items=[], required_tools=[key, master_key])
    check.is_false(zone.can_access_with(None))
    check.is_false(zone.can_access_with(rock))
    check.is_true(zone.can_access_with(key))
    check.is_true(zone.can_access_with(master_key))
