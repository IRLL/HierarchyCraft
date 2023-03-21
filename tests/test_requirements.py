import pytest_check as check

from hcraft.elements import Item, Stack, Zone
from hcraft.requirements import _available_in_zones_stacks


class TestAvailableFromStart:
    def test_no_consumed_stacks(self):
        zone = Zone("0")
        check.is_true(
            _available_in_zones_stacks(
                stacks=None,
                zone=zone,
                zones_stacks={zone: []},
            )
        )

    def test_consumed_stacks_in_start_zone(self):
        zone = Zone("0")
        req_item = Item("requirement")
        req_stack = Stack(req_item)
        check.is_true(
            _available_in_zones_stacks(
                stacks=[req_stack],
                zone=zone,
                zones_stacks={zone: [req_stack]},
            )
        )

    def test_consumed_stacks_not_in_start_zone(self):
        zone = Zone("0")
        req_item = Item("requirement")
        req_stack = Stack(req_item)
        check.is_false(
            _available_in_zones_stacks(
                stacks=[req_stack],
                zone=zone,
                zones_stacks={zone: []},
            )
        )

    def test_consumed_stacks_not_enough_in_start_zone(self):
        zone = Zone("0")
        req_item = Item("requirement")
        req_stack = Stack(req_item, 2)
        check.is_false(
            _available_in_zones_stacks(
                stacks=[req_stack],
                zone=zone,
                zones_stacks={zone: [Stack(req_item, 1)]},
            )
        )

    def test_consumed_stacks_other_in_start_zone(self):
        zone = Zone("0")
        req_item = Item("requirement")
        req_stack = Stack(req_item)
        check.is_false(
            _available_in_zones_stacks(
                stacks=[req_stack],
                zone=zone,
                zones_stacks={zone: [Stack(Item("1"))]},
            )
        )
