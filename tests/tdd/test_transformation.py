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

    def test_destination(self):
        transfo = Transformation(destination=self.zones[1])
        transfo._build_ops(self.world)

        expected_op = np.zeros(len(self.zones), dtype=np.uint16)
        expected_op[1] = 1
        check_np_equal(transfo._destination, expected_op)

    def test_no_destination(self):
        transfo = Transformation(destination=None)
        transfo._build_ops(self.world)
        check.is_none(transfo._destination)

    def test_zones_requirement(self):
        tranfo = Transformation(zones=[self.zones[0], self.zones[2]])
        tranfo._build_ops(self.world)

        expected_op = np.zeros(len(self.zones), dtype=np.uint16)
        expected_op[0] = 1
        expected_op[2] = 1
        check_np_equal(tranfo._zones, expected_op)

    def test_no_zones_requirement(self):
        tranfo = Transformation(zones=None)
        tranfo._build_ops(self.world)
        check.is_none(tranfo._zones)
