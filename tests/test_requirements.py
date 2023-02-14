from crafting.requirements import _available_from_start
import pytest_check as check

from crafting.world import Zone, ItemStack, Item


class TestAvailableFromStart:
    def test_no_consumed_stacks(self):
        zone = Zone("0")
        check.is_true(
            _available_from_start(
                stacks=None,
                zone=zone,
                start_zones_stacks={zone: []},
            )
        )

    def test_consumed_stacks_in_start_zone(self):
        zone = Zone("0")
        req_item = Item("requirement")
        req_stack = ItemStack(req_item)
        check.is_true(
            _available_from_start(
                stacks=[req_stack],
                zone=zone,
                start_zones_stacks={zone: [req_stack]},
            )
        )

    def test_consumed_stacks_not_in_start_zone(self):
        zone = Zone("0")
        req_item = Item("requirement")
        req_stack = ItemStack(req_item)
        check.is_false(
            _available_from_start(
                stacks=[req_stack],
                zone=zone,
                start_zones_stacks={zone: []},
            )
        )

    def test_consumed_stacks_not_enough_in_start_zone(self):
        zone = Zone("0")
        req_item = Item("requirement")
        req_stack = ItemStack(req_item, 2)
        check.is_false(
            _available_from_start(
                stacks=[req_stack],
                zone=zone,
                start_zones_stacks={zone: [ItemStack(req_item, 1)]},
            )
        )

    def test_consumed_stacks_other_in_start_zone(self):
        zone = Zone("0")
        req_item = Item("requirement")
        req_stack = ItemStack(req_item)
        check.is_false(
            _available_from_start(
                stacks=[req_stack],
                zone=zone,
                start_zones_stacks={zone: [ItemStack(Item("1"))]},
            )
        )
