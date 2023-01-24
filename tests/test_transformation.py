import pytest
import pytest_check as check
import numpy as np

from crafting.world import Item, ItemStack, Zone, World
from crafting.transformation import Transformation

from tests.check_array import check_np_equal


class TestTransformationApply:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.zones = [Zone("0"), Zone("1"), Zone("2")]
        self.items = [Item("0"), Item("1"), Item("2")]
        self.zones_items = [Item("0"), Item("z1")]
        self.world = World(self.items, self.zones, self.zones_items)

    def test_destination(self):
        transfo = Transformation(destination=self.zones[1])
        transfo.build(self.world)
        position = np.array([1, 0, 0])
        transfo.apply(None, position, None)
        check_np_equal(position, np.array([0, 1, 0]))

    def test_player_items(self):
        transfo = Transformation(
            removed_player_items=[
                ItemStack(self.items[0], 2),
                ItemStack(self.items[2], 3),
            ],
            added_player_items=[
                ItemStack(self.items[1], 5),
            ],
        )
        transfo.build(self.world)
        inventory = np.array([3, 0, 3])
        transfo.apply(inventory, None, None)
        check_np_equal(inventory, np.array([1, 5, 0]))

    def test_zone_items(self):
        transfo = Transformation(
            removed_zone_items=[
                ItemStack(self.zones_items[0], 3),
            ],
            added_zone_items=[
                ItemStack(self.zones_items[1], 7),
            ],
        )
        transfo.build(self.world)
        position = np.array([0, 1, 0])
        zones_inventories = np.array([[3, 1], [4, 2], [5, 3]])
        transfo.apply(None, position, zones_inventories)
        check_np_equal(zones_inventories, np.array([[3, 1], [1, 9], [5, 3]]))

    def test_destination_items(self):
        transfo = Transformation(
            destination=self.zones[1],
            removed_destination_items=[
                ItemStack(self.zones_items[0], 3),
            ],
            added_destination_items=[
                ItemStack(self.zones_items[1], 7),
            ],
        )
        transfo.build(self.world)
        position = np.array([1, 0, 0])
        zones_inventories = np.array([[3, 1], [4, 2], [5, 3]])
        transfo.apply(None, position, zones_inventories)
        check_np_equal(zones_inventories, np.array([[3, 1], [1, 9], [5, 3]]))


class TestTransformationOperations:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.zones = [Zone("0"), Zone("1"), Zone("2")]
        self.items = [Item("0"), Item("1"), Item("2")]
        self.zones_items = [Item("0"), Item("z1")]
        self.world = World(self.items, self.zones, self.zones_items)

    def test_destination(self):
        transfo = Transformation(destination=self.zones[1])
        transfo.build(self.world)

        expected_op = np.zeros(len(self.zones), dtype=np.uint16)
        expected_op[1] = 1
        check_np_equal(transfo._destination, expected_op)

    def test_no_destination(self):
        transfo = Transformation(destination=None)
        transfo.build(self.world)
        check.is_none(transfo._destination)

    def test_zones_requirement(self):
        tranfo = Transformation(zones=[self.zones[0], self.zones[2]])
        tranfo.build(self.world)

        expected_op = np.zeros(len(self.zones), dtype=np.uint16)
        expected_op[0] = 1
        expected_op[2] = 1
        check_np_equal(tranfo._zones, expected_op)

    def test_no_zones_requirement(self):
        tranfo = Transformation(zones=None)
        tranfo.build(self.world)
        check.is_none(tranfo._zones)

    def test_removed_player_items(self):
        tranfo = Transformation(removed_player_items=[ItemStack(self.items[1], 2)])
        tranfo.build(self.world)

        expected_op = np.zeros(len(self.items), dtype=np.uint16)
        expected_op[1] = 2
        check_np_equal(tranfo._removed_player_items, expected_op)

    def test_no_removed_player_items(self):
        tranfo = Transformation(removed_player_items=None)
        tranfo.build(self.world)
        check.is_none(tranfo._removed_player_items)

    def test_added_player_items(self):
        tranfo = Transformation(added_player_items=[ItemStack(self.items[1], 2)])
        tranfo.build(self.world)

        expected_op = np.zeros(len(self.items), dtype=np.uint16)
        expected_op[1] = 2
        check_np_equal(tranfo._added_player_items, expected_op)

    def test_no_added_player_items(self):
        tranfo = Transformation(added_player_items=None)
        tranfo.build(self.world)
        check.is_none(tranfo._added_player_items)

    def test_removed_destination_items(self):
        tranfo = Transformation(
            removed_destination_items=[ItemStack(self.zones_items[1], 2)]
        )
        tranfo.build(self.world)

        expected_op = np.zeros(len(self.zones_items), dtype=np.uint16)
        expected_op[1] = 2
        check_np_equal(tranfo._removed_destination_items, expected_op)

    def test_no_removed_destination_items(self):
        tranfo = Transformation(removed_destination_items=None)
        tranfo.build(self.world)
        check.is_none(tranfo._removed_destination_items)

    def test_added_destination_items(self):
        tranfo = Transformation(
            added_destination_items=[ItemStack(self.zones_items[1], 2)]
        )
        tranfo.build(self.world)

        expected_op = np.zeros(len(self.zones_items), dtype=np.uint16)
        expected_op[1] = 2
        check_np_equal(tranfo._added_destination_items, expected_op)

    def test_no_added_destination_items(self):
        tranfo = Transformation(added_player_items=None)
        tranfo.build(self.world)
        check.is_none(tranfo._added_destination_items)

    def test_removed_zone_items(self):
        tranfo = Transformation(removed_zone_items=[ItemStack(self.zones_items[1], 2)])
        tranfo.build(self.world)

        expected_op = np.zeros(len(self.zones_items), dtype=np.uint16)
        expected_op[1] = 2
        check_np_equal(tranfo._removed_zone_items, expected_op)

    def test_no_removed_zone_items(self):
        tranfo = Transformation(removed_zone_items=None)
        tranfo.build(self.world)
        check.is_none(tranfo._removed_zone_items)

    def test_added_zone_items(self):
        tranfo = Transformation(added_zone_items=[ItemStack(self.zones_items[1], 2)])
        tranfo.build(self.world)

        expected_op = np.zeros(len(self.zones_items), dtype=np.uint16)
        expected_op[1] = 2
        check_np_equal(tranfo._added_zone_items, expected_op)

    def test_no_added_zone_items(self):
        tranfo = Transformation(added_zone_items=None)
        tranfo.build(self.world)
        check.is_none(tranfo._added_zone_items)
