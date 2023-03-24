from dataclasses import dataclass, field

import numpy as np
import pytest
import pytest_check as check

from hcraft.elements import Item, Stack, Zone
from hcraft.transformation import (
    Transformation,
    Use,
    Yield,
    PLAYER,
    CURRENT_ZONE,
    DESTINATION,
)
from hcraft.world import World, world_from_transformations
from tests.custom_checks import check_np_equal


@dataclass
class DummyState:
    player_inventory: np.ndarray = field(default_factory=lambda: np.array([]))
    position: np.ndarray = field(default_factory=lambda: np.array([]))
    zones_inventories: np.ndarray = field(default_factory=lambda: np.array([]))

    @property
    def current_zone_inventory(self):
        if self.zones_inventories is None or self.position is None:
            return None
        return self.zones_inventories[self.position.nonzero()[0], :]


class TestTransformationIsValid:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.zones = [Zone("0"), Zone("1"), Zone("2")]
        self.items = [Item("0"), Item("1"), Item("2")]
        self.zones_items = [Item("0"), Item("z1")]
        self.world = World(self.items, self.zones, self.zones_items, [])

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
            inventory_changes=[
                Use(PLAYER, self.items[0], consume=2),
                Yield(PLAYER, self.items[1]),
            ],
        )
        transfo.build(self.world)
        position = np.array([1, 0, 0])

        inv_examples = [
            (True, np.array([2, 0, 0])),  # Minimal required
            (False, np.array([1, 0, 0])),  # Hit default minimum items[0] (-1 < 0)
        ]

        for expected_valid, player_inventory in inv_examples:
            state = DummyState(position=position, player_inventory=player_inventory)
            check.equal(
                transfo.is_valid(state),
                expected_valid,
                msg=f"{state}, {transfo.is_valid(state)}|{expected_valid}",
            )

    def test_player_items_is_valid_min_max(self):
        transfo = Transformation(
            inventory_changes=[
                Use(PLAYER, self.items[0], consume=2, min=1),
                Yield(PLAYER, self.items[1], max=1),
                Yield(PLAYER, self.items[2], max=0),
            ],
        )
        transfo.build(self.world)
        position = np.array([1, 0, 0])

        inv_examples = [
            (True, np.array([1, 0, 0])),  # Minimal required
            (False, np.array([0, 0, 0])),  # Hit minimum items[0] (0 < 1)
            (False, np.array([1, 2, 0])),  # Hit maximum items[1] (2 > 1)
            (False, np.array([1, 0, 1])),  # Hit maximum items[2] (1 > 0)
        ]

        for expected_valid, player_inventory in inv_examples:
            state = DummyState(position=position, player_inventory=player_inventory)
            check.equal(
                transfo.is_valid(state),
                expected_valid,
                msg=f"{state}, {transfo.is_valid(state)}|{expected_valid}",
            )

    def test_zone_items_is_valid(self):
        transfo = Transformation(
            inventory_changes=[
                Use(CURRENT_ZONE, self.zones_items[0], consume=3, min=1),
                Yield(CURRENT_ZONE, self.zones_items[1], max=0),
            ],
        )
        transfo.build(self.world)
        position = np.array([0, 1, 0])

        inv_examples = [
            (True, np.array([[0, 0], [1, 0], [0, 0]])),  # Minimal required
            (False, np.array([[9, 0], [0, 0], [9, 0]])),  # Hit minimum
            (False, np.array([[0, 0], [1, 1], [0, 0]])),  # Hit maximum
        ]

        for expected_valid, zones_inventories in inv_examples:
            state = DummyState(position=position, zones_inventories=zones_inventories)
            check.equal(
                transfo.is_valid(state),
                expected_valid,
                msg=f"{state}, {transfo.is_valid(state)}|{expected_valid}",
            )

    def test_destination_items_is_valid(self):
        transfo = Transformation(
            destination=self.zones[1],
            inventory_changes=[
                Use(DESTINATION, self.zones_items[0], consume=3, min=1),
                Yield(DESTINATION, self.zones_items[1], max=0),
            ],
        )
        transfo.build(self.world)
        position = np.array([1, 0, 0])

        inv_examples = [
            (True, np.array([[0, 0], [1, 0], [0, 0]])),  # Minimal required
            (False, np.array([[9, 0], [0, 0], [9, 0]])),  # Hit minimum
            (False, np.array([[0, 0], [1, 1], [0, 0]])),  # Hit maximum
        ]

        for expected_valid, zones_inventories in inv_examples:
            state = DummyState(position=position, zones_inventories=zones_inventories)
            check.equal(
                transfo.is_valid(state),
                expected_valid,
                msg=f"{state}, {transfo.is_valid(state)}|{expected_valid}",
            )

    def test_zones_items_is_valid(self):
        transfo = Transformation(
            inventory_changes=[
                Use(self.zones[1], self.zones_items[0], consume=3, min=1),
                Yield(self.zones[1], self.zones_items[1], max=0),
            ],
        )
        transfo.build(self.world)
        inv_examples = [
            (True, np.array([[0, 0], [1, 0], [0, 0]])),  # Minimal required
            (False, np.array([[9, 0], [0, 0], [9, 0]])),  # Not enough items
            (False, np.array([[0, 0], [1, 1], [0, 0]])),  # Hit maximum
        ]

        for expected_valid, zones_inventories in inv_examples:
            state = DummyState(zones_inventories=zones_inventories)
            check.equal(
                transfo.is_valid(state),
                expected_valid,
                msg=f"{state}, {transfo.is_valid(state)}|{expected_valid}",
            )

    def test_destination_op(self):
        transfo = Transformation(destination=self.zones[1])
        transfo.build(self.world)

        expected_op = np.zeros(len(self.zones), dtype=np.int32)
        expected_op[1] = 1
        check_np_equal(transfo._destination, expected_op)

    def test_destination(self):
        transfo = Transformation(destination=self.zones[1])
        transfo.build(self.world)
        position = np.array([1, 0, 0])
        transfo.apply(None, position, None)
        check_np_equal(position, np.array([0, 1, 0]))

    def test_player_items(self):
        transfo = Transformation(
            inventory_changes=[
                Use(PLAYER, self.items[0], consume=2),
                Use(PLAYER, self.items[2], consume=3),
                Yield(PLAYER, self.items[1], create=5),
            ],
        )
        transfo.build(self.world)
        position = np.array([1, 0, 0])
        inventory = np.array([3, 0, 3])
        transfo.apply(inventory, position, None)
        check_np_equal(inventory, np.array([1, 5, 0]))

    def test_zone_items(self):
        transfo = Transformation(
            inventory_changes=[
                Use(CURRENT_ZONE, self.zones_items[0], consume=3),
                Yield(CURRENT_ZONE, self.zones_items[1], create=7),
            ],
        )
        transfo.build(self.world)
        position = np.array([0, 1, 0])
        zones_inventories = np.array([[3, 1], [4, 2], [5, 3]])
        transfo.apply(None, position, zones_inventories)
        check_np_equal(zones_inventories, np.array([[3, 1], [1, 9], [5, 3]]))

    def test_zones_items(self):
        transfo = Transformation(
            inventory_changes=[
                Use(self.zones[0], self.zones_items[0], consume=3),
                Use(self.zones[0], self.zones_items[1], consume=1),
                Yield(self.zones[2], self.zones_items[1], create=7),
            ],
        )
        transfo.build(self.world)
        position = np.array([0, 1, 0])
        zones_inventories = np.array([[3, 1], [4, 2], [5, 3]])
        transfo.apply(None, position, zones_inventories)
        check_np_equal(zones_inventories, np.array([[0, 0], [4, 2], [5, 10]]))

    def test_destination_items(self):
        transfo = Transformation(
            destination=self.zones[1],
            inventory_changes=[
                Use(DESTINATION, self.zones_items[0], consume=3),
                Yield(DESTINATION, self.zones_items[1], create=7),
            ],
        )
        transfo.build(self.world)
        position = np.array([1, 0, 0])
        zones_inventories = np.array([[3, 1], [4, 2], [5, 3]])
        transfo.apply(None, position, zones_inventories)
        check_np_equal(zones_inventories, np.array([[3, 1], [1, 9], [5, 3]]))

    def test_no_destination(self):
        transfo = Transformation(destination=None)
        transfo.build(self.world)
        check.is_none(transfo._destination)

    def test_zones_requirement(self):
        tranfo = Transformation(zones=[self.zones[0], self.zones[2]])
        tranfo.build(self.world)

        expected_op = np.zeros(len(self.zones), dtype=np.int32)
        expected_op[0] = 1
        expected_op[2] = 1
        check_np_equal(tranfo._zones, expected_op)

    def test_no_zones_requirement(self):
        tranfo = Transformation(zones=None)
        tranfo.build(self.world)
        check.is_none(tranfo._zones)


ZONE_A = Zone("A")


class TestRepr:
    owner_expected_prefix = {
        PLAYER: "",
        CURRENT_ZONE: "Zone(",
        DESTINATION: "Dest(",
        ZONE_A: f"{ZONE_A.name}(",
    }

    owner_expected_suffix = {
        PLAYER: "",
        CURRENT_ZONE: ")",
        DESTINATION: ")",
        ZONE_A: ")",
    }

    @pytest.mark.parametrize("owner", [PLAYER, CURRENT_ZONE, DESTINATION, ZONE_A])
    def test_add(self, owner):
        tranfo = Transformation(
            inventory_changes=[Yield(owner, Item("wood"), create=2)]
        )
        prefix = self.owner_expected_prefix[owner]
        suffix = self.owner_expected_suffix[owner]
        check_equal_str(repr(tranfo), f"=> {prefix}+[2]wood{suffix}")

    @pytest.mark.parametrize("owner", [PLAYER, CURRENT_ZONE, DESTINATION, ZONE_A])
    def test_max(self, owner):
        tranfo = Transformation(
            inventory_changes=[Yield(owner, Item("wood"), create=0, max=2)]
        )
        prefix = self.owner_expected_prefix[owner]
        suffix = self.owner_expected_suffix[owner]
        check_equal_str(repr(tranfo), f"{prefix}wood<2{suffix} =>")

    @pytest.mark.parametrize("owner", [PLAYER, CURRENT_ZONE, DESTINATION, ZONE_A])
    def test_remove(self, owner):
        tranfo = Transformation(inventory_changes=[Use(owner, Item("wood"), consume=3)])
        prefix = self.owner_expected_prefix[owner]
        suffix = self.owner_expected_suffix[owner]
        check_equal_str(
            repr(tranfo), f"{prefix}wood>3{suffix} => {prefix}-[3]wood{suffix}"
        )

    @pytest.mark.parametrize("owner", [PLAYER, CURRENT_ZONE, DESTINATION, ZONE_A])
    def test_min(self, owner):
        tranfo = Transformation(
            inventory_changes=[Use(owner, Item("wood"), consume=0, min=2)]
        )
        prefix = self.owner_expected_prefix[owner]
        suffix = self.owner_expected_suffix[owner]
        check_equal_str(repr(tranfo), f"{prefix}wood>2{suffix} =>")

    def test_destination(self):
        tranfo = Transformation(destination=Zone("other zone"))
        check_equal_str(repr(tranfo), "=> | other zone")

    def test_zones(self):
        tranfo = Transformation(zones=[Zone("A"), Zone("B")])
        check_equal_str(repr(tranfo), "| A,B =>")

    def test_full(self):
        tranfo = Transformation(
            inventory_changes=[
                Use(PLAYER, Item("P1"), consume=1),
                Use(PLAYER, Item("P2"), consume=0, min=1),
                Yield(PLAYER, Item("P3"), create=1),
                Yield(PLAYER, Item("P4"), create=0, max=1),
                Use(CURRENT_ZONE, Item("Z1"), consume=2, min=-1),
                Yield(CURRENT_ZONE, Item("Z2"), create=1, max=3),
                Use(DESTINATION, Item("D1"), consume=1),
                Use(DESTINATION, Item("D2"), consume=0, min=1),
                Yield(DESTINATION, Item("D3"), create=1),
                Yield(DESTINATION, Item("D4"), create=0, max=1),
                Use(Zone("A"), Item("A1"), consume=1),
                Use(Zone("A"), Item("A2"), consume=0, min=1),
                Yield(Zone("A"), Item("A3"), create=1),
                Yield(Zone("A"), Item("A4"), create=0, max=3),
                Use(Zone("B"), Item("B1"), consume=1),
                Use(Zone("B"), Item("B2"), consume=0, min=1),
                Yield(Zone("B"), Item("B3"), create=1),
                Yield(Zone("B"), Item("B4"), create=0, max=3),
            ],
            destination=Zone("D"),
            zones=[Zone("E"), Zone("F")],
        )
        check_equal_str(
            repr(tranfo),
            "P1>1,P2>1,P4<1 "
            "Zone(Z1>-1,Z2<3) "
            "Dest(D1>1,D2>1,D4<1) "
            "A(A1>1,A2>1,A4<3) "
            "B(B1>1,B2>1,B4<3) "
            "| E,F "
            "=> "
            "-P1,+P3 "
            "Zone(-[2]Z1,+Z2) "
            "Dest(-D1,+D3) "
            "A(-A1,+A3) "
            "B(-B1,+B3) "
            "| D",
        )


def test_docstring_examples():
    transformations = []

    DIRT = Item("dirt")
    search_for_dirt = Transformation(
        "search_for_dirt",
        inventory_changes=[Yield(PLAYER, DIRT)],
    )
    transformations.append(search_for_dirt)

    FOREST = Zone("forest")
    move_to_forest = Transformation(
        "move_to_forest",
        destination=FOREST,
    )
    transformations.append(move_to_forest)

    WOOD = Item("wood")
    search_for_wood = Transformation(
        "search_for_wood",
        inventory_changes=[Yield(PLAYER, WOOD)],
        zones=[FOREST],
    )
    transformations.append(search_for_wood)

    PLANK = Item("plank")
    craft_wood_plank = Transformation(
        "craft_wood_plank",
        inventory_changes=[Use(PLAYER, WOOD, consume=1), Yield(PLAYER, PLANK, 4)],
    )
    transformations.append(craft_wood_plank)

    HOUSE = Item("house")  # Need 12 WOOD and 64 PLANK to
    build_house = Transformation(
        "build_house",
        inventory_changes=[
            Use(PLAYER, WOOD, 12),
            Use(PLAYER, PLANK, 64),
            Yield("current_zone", HOUSE),
        ],
    )
    transformations.append(build_house)

    TREETOPS = Zone("treetops")
    LADDER = Item("ladder")
    climb_tree = Transformation(
        "climb_tree",
        destination=TREETOPS,
        inventory_changes=[Use(PLAYER, LADDER, consume=1)],
        zones=[FOREST],
    )
    transformations.append(climb_tree)

    CRATER = Item("crater")
    jump_from_tree = Transformation(
        "jump_from_tree",
        destination=FOREST,
        inventory_changes=[Yield("destination", CRATER)],
        zones=[TREETOPS],
    )
    transformations.append(jump_from_tree)

    INSIDE_HOUSE = Zone("house")
    DOOR = Item("door")
    KEY = Item("key")
    enter_house = Transformation(
        destination=INSIDE_HOUSE,
        inventory_changes=[
            Use(PLAYER, KEY),  # Ensure has key
            Use("current_zone", DOOR),  # Ensure has door
        ],
    )
    transformations.append(enter_house)

    STRANGE_RED_BUTTON = Item("don't press me")
    SPACE = Zone("space")
    INCOMING_MISSILES = Item("incoming_missiles")
    press_red_button = Transformation(
        "press_red_button",
        inventory_changes=[
            Use("current_zone", STRANGE_RED_BUTTON),  # Ensure has door
            Yield(SPACE, INCOMING_MISSILES),  # An 'absolute' specific zone
        ],
    )
    transformations.append(press_red_button)

    world = world_from_transformations(
        transformations,
        start_zone=FOREST,
        start_items=[Stack(DIRT, 4)],
        start_zones_items={FOREST: [HOUSE]},
    )

    world = world


def check_equal_str(actual, expected):
    check.equal(actual, expected, msg=f"\n{actual}\n{expected}")
