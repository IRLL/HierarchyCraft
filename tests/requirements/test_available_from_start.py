import pytest
import pytest_check as check

from hcraft.elements import Item, Stack, Zone
from hcraft.requirements import _available_in_zones_stacks


class TestAvailableFromStart:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.zone = Zone("0")
        self.req_item = Item("requirement")
        self.req_stack = Stack(self.req_item)

    def test_no_consumed_stacks(self):
        check.is_true(
            _available_in_zones_stacks(
                stacks=None,
                zone=self.zone,
                zones_stacks={self.zone: []},
            )
        )

    def test_consumed_stacks_in_start_zone(self):
        check.is_true(
            _available_in_zones_stacks(
                stacks=[self.req_stack],
                zone=self.zone,
                zones_stacks={self.zone: [self.req_stack]},
            )
        )

    def test_consumed_stacks_not_in_start_zone(self):
        check.is_false(
            _available_in_zones_stacks(
                stacks=[self.req_stack],
                zone=self.zone,
                zones_stacks={self.zone: []},
            )
        )

    def test_consumed_stacks_not_enough_in_start_zone(self):
        req_stack = Stack(self.req_item, 2)
        check.is_false(
            _available_in_zones_stacks(
                stacks=[req_stack],
                zone=self.zone,
                zones_stacks={self.zone: [Stack(self.req_item, 1)]},
            )
        )

    def test_consumed_stacks_other_in_start_zone(self):
        check.is_false(
            _available_in_zones_stacks(
                stacks=[self.req_stack],
                zone=self.zone,
                zones_stacks={self.zone: [Stack(Item("1"))]},
            )
        )
