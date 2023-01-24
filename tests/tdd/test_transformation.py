import pytest
import pytest_check as check
import numpy as np

from crafting.world import Item, Zone, World
from crafting.transformation import Transformation

from tests.check_array import check_np_equal


class TestTransformation:
    def setup_method(self):
        self.zones = [Zone("0"), Zone("1"), Zone("2")]
        self.items = [Item("0"), Item("1"), Item("2")]
        self.world = World(self.items, self.zones)

    def test_move_transformation(self):
        move_to_zone_1 = Transformation(
            destination=self.zones[1],
            zones=[self.zones[0], self.zones[2]],
        )
        move_to_zone_1._build_ops(self.world)
        expected_destination_ops = np.zeros(len(self.zones), dtype=np.uint16)
        check_np_equal(move_to_zone_1.destination_ops, expected_destination_ops)
