from dataclasses import dataclass
from typing import Any, Union

import numpy as np
import pytest
import pytest_check as check

from crafting.transformation import Transformation
from crafting.elements import Item, ItemStack, Zone
from crafting.world import World
from tests.custom_checks import check_np_equal


@dataclass
class DummyState:
    player_inventory: Any = None
    position: Any = None
    zones_inventories: Any = None


class TestTransformationIsValid:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.zones = [Zone("0"), Zone("1"), Zone("2")]
        self.items = [Item("0"), Item("1"), Item("2")]
        self.zones_items = [Item("0"), Item("z1")]
        self.world = World(self.items, self.zones, self.zones_items, [])

    def test_item_as_input(self):
        transfo = Transformation(
            added_player_items=[Item("0")],
            removed_player_items=[Item("0")],
            added_zone_items=[Item("0")],
            removed_zone_items=[Item("0")],
            added_destination_items=[Item("0")],
            removed_destination_items=[Item("0")],
            added_zones_items={Zone("0"): [Item("0")]},
            removed_zones_items={Zone("0"): [Item("0")]},
        )

        for operation in transfo.OPERATIONS[2:]:
            attribute: Union[list, dict] = getattr(transfo, operation)
            if isinstance(attribute, dict):
                _attribute = []
                for sub_list in attribute.values():
                    _attribute.extend(sub_list)
                attribute = _attribute
            for item_stack in attribute:
                check.is_instance(item_stack, ItemStack)

    def test_position_is_valid(self):
        transfo = Transformation(
            destination=self.zones[0], zones=[self.zones[0], self.zones[2]]
        )
        transfo.build(self.world)

        check.is_false(transfo.is_valid(DummyState(position=np.array([1, 0, 0]))))
        check.is_false(transfo.is_valid(DummyState(position=np.array([0, 1, 0]))))
        check.is_true(transfo.is_valid(DummyState(position=np.array([0, 0, 1]))))

    def test_player_items_is_valid(self):
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
        position = np.array([1, 0, 0])

        state = DummyState(position=position, player_inventory=np.array([2, 0, 3]))
        check.is_true(transfo.is_valid(state))
        state = DummyState(position=position, player_inventory=np.array([1, 0, 3]))
        check.is_false(transfo.is_valid(state))
        state = DummyState(position=position, player_inventory=np.array([3, 5, 2]))
        check.is_false(transfo.is_valid(state))

    def test_zone_items_is_valid(self):
        transfo = Transformation(removed_zone_items=[ItemStack(self.zones_items[0], 3)])
        transfo.build(self.world)
        position = np.array([0, 1, 0])

        state = DummyState(
            position=position, zones_inventories=np.array([[0, 0], [3, 0], [0, 0]])
        )
        check.is_true(transfo.is_valid(state))
        state = DummyState(
            position=position, zones_inventories=np.array([[10, 10], [0, 10], [10, 10]])
        )
        check.is_false(transfo.is_valid(state))

    def test_zones_items_is_valid(self):
        transfo = Transformation(
            removed_zones_items={self.zones[1]: [ItemStack(self.zones_items[0], 3)]},
        )
        transfo.build(self.world)
        state = DummyState(zones_inventories=np.array([[0, 0], [3, 0], [0, 0]]))
        check.is_true(transfo.is_valid(state))
        state = DummyState(zones_inventories=np.array([[10, 10], [0, 10], [10, 10]]))
        check.is_false(transfo.is_valid(state))

    def test_destination_items_is_valid(self):
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
        state = DummyState(
            position=position, zones_inventories=np.array([[0, 0], [3, 0], [0, 0]])
        )
        check.is_true(transfo.is_valid(state))
        state = DummyState(
            position=position, zones_inventories=np.array([[10, 10], [0, 10], [10, 10]])
        )
        check.is_false(transfo.is_valid(state))

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
        position = np.array([1, 0, 0])
        inventory = np.array([3, 0, 3])
        transfo.apply(inventory, position, None)
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

    def test_zones_items(self):
        transfo = Transformation(
            removed_zones_items={
                self.zones[0]: [
                    ItemStack(self.zones_items[0], 3),
                    ItemStack(self.zones_items[1], 1),
                ]
            },
            added_zones_items={self.zones[2]: [ItemStack(self.zones_items[1], 7)]},
        )
        transfo.build(self.world)
        position = np.array([0, 1, 0])
        zones_inventories = np.array([[3, 1], [4, 2], [5, 3]])
        transfo.apply(None, position, zones_inventories)
        check_np_equal(zones_inventories, np.array([[0, 0], [4, 2], [5, 10]]))

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

    def test_removed_zones_items(self):
        tranfo = Transformation(
            removed_zones_items={self.zones[0]: [ItemStack(self.zones_items[1], 2)]}
        )
        tranfo.build(self.world)

        expected_op = np.zeros(
            (len(self.zones), len(self.zones_items)), dtype=np.uint16
        )
        expected_op[0, 1] = 2
        check_np_equal(tranfo._removed_zones_items, expected_op)

    def test_no_removed_zones_items(self):
        tranfo = Transformation(removed_zones_items=None)
        tranfo.build(self.world)
        check.is_none(tranfo._removed_zones_items)

        check.is_none(tranfo._added_zone_items)

    def test_added_zones_items(self):
        tranfo = Transformation(
            added_zones_items={self.zones[0]: [ItemStack(self.zones_items[1], 2)]}
        )
        tranfo.build(self.world)

        expected_op = np.zeros(
            (len(self.zones), len(self.zones_items)), dtype=np.uint16
        )
        expected_op[0, 1] = 2
        check_np_equal(tranfo._added_zones_items, expected_op)

    def test_no_added_zones_items(self):
        tranfo = Transformation(added_zones_items=None)
        tranfo.build(self.world)
        check.is_none(tranfo._added_zones_items)

    def test_str(self):
        tranfo = Transformation(
            added_player_items=[
                ItemStack(Item("wood"), 2),
                ItemStack(Item("stone"), 3),
            ]
        )
        check_equal_str(str(tranfo), "> wood[2],stone[3]")

        tranfo = Transformation(
            removed_player_items=[
                ItemStack(Item("wood"), 2),
                ItemStack(Item("stone"), 3),
            ]
        )
        check_equal_str(str(tranfo), "wood[2],stone[3] > ")

        tranfo = Transformation(
            added_zone_items=[
                ItemStack(Item("wood"), 2),
                ItemStack(Item("stone"), 3),
            ]
        )
        check_equal_str(str(tranfo), "> Zone(wood[2],stone[3])")

        tranfo = Transformation(
            removed_zone_items=[
                ItemStack(Item("wood"), 2),
                ItemStack(Item("stone"), 3),
            ]
        )
        check_equal_str(str(tranfo), "Zone(wood[2],stone[3]) > ")

        tranfo = Transformation(
            added_destination_items=[
                ItemStack(Item("wood"), 2),
                ItemStack(Item("stone"), 3),
            ]
        )
        check_equal_str(str(tranfo), "> Dest(wood[2],stone[3])")

        tranfo = Transformation(
            removed_destination_items=[
                ItemStack(Item("wood"), 2),
                ItemStack(Item("stone"), 3),
            ]
        )
        check_equal_str(str(tranfo), "Dest(wood[2],stone[3]) > ")

        tranfo = Transformation(destination=Zone("other zone"))
        check_equal_str(str(tranfo), "> | other zone")

        tranfo = Transformation(destination=Zone("other zone"))
        check_equal_str(str(tranfo), "> | other zone")

        tranfo = Transformation(
            removed_player_items=[
                ItemStack(Item("P1")),
                ItemStack(Item("P2")),
            ],
            removed_zone_items=[
                ItemStack(Item("Z1")),
                ItemStack(Item("Z2")),
            ],
            removed_destination_items=[
                ItemStack(Item("D1")),
                ItemStack(Item("D2")),
            ],
            removed_zones_items={
                Zone("A"): [
                    ItemStack(Item("A1")),
                    ItemStack(Item("A2")),
                ],
                Zone("B"): [
                    ItemStack(Item("B1")),
                    ItemStack(Item("B2")),
                ],
            },
            added_player_items=[
                ItemStack(Item("P3")),
                ItemStack(Item("P4")),
            ],
            added_zone_items=[
                ItemStack(Item("Z3")),
                ItemStack(Item("Z4")),
            ],
            added_destination_items=[
                ItemStack(Item("D3")),
                ItemStack(Item("D4")),
            ],
            added_zones_items={
                Zone("A"): [
                    ItemStack(Item("A3")),
                    ItemStack(Item("A4")),
                ],
                Zone("B"): [
                    ItemStack(Item("B3")),
                    ItemStack(Item("B4")),
                ],
            },
            destination=Zone("D"),
        )
        check_equal_str(
            str(tranfo),
            "P1,P2 Zone(Z1,Z2) Dest(D1,D2) A(A1,A2) B(B1,B2) "
            "> P3,P4 Zone(Z3,Z4) Dest(D3,D4) A(A3,A4) B(B3,B4) | D",
        )


def check_equal_str(actual, expected):
    check.equal(actual, expected, msg=f"\n{expected}\n{actual}")
