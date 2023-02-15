from typing import List

from crafting.env import CraftingEnv
from crafting.world import Item, Zone, ItemStack, world_from_transformations
from crafting.transformation import Transformation

import pytest_check as check


class KeyDoorCrafting(CraftingEnv):
    START = Zone("start_room")
    BALL_ROOM = Zone("ball_room")

    KEY = Item("key")
    BALL = Item("ball")

    OPEN_DOOR = Item("open_door")
    CLOSED_DOOR = Item("closed_door")
    LOCKED_DOOR = Item("locked_door")

    def __init__(self, **kwargs) -> None:
        transformations = self.build_transformations()
        world = world_from_transformations(
            transformations=transformations,
            start_zones_items={self.BALL_ROOM: [self.BALL]},
        )
        super().__init__(
            world,
            resources_path=None,
            name="KeyDoorCrafting",
            **kwargs,
        )

    def build_transformations(self) -> List[Transformation]:
        transformations = []

        search_for_key = Transformation(added_zone_items=[self.KEY], zones=[self.START])
        transformations.append(search_for_key)
        for carriable_item in (self.KEY, self.BALL):
            pickup = Transformation(
                removed_zone_items=[carriable_item], added_player_items=[carriable_item]
            )
            put_down = Transformation(
                removed_player_items=[carriable_item], added_zone_items=[carriable_item]
            )
            transformations += [pickup, put_down]

        search_for_door = Transformation(
            added_zones_items={
                self.START: [self.LOCKED_DOOR],
                self.BALL_ROOM: [self.LOCKED_DOOR],
            },
            zones=[self.START, self.BALL_ROOM],
        )
        transformations.append(search_for_door)

        unlock_door = Transformation(
            removed_zones_items={
                self.START: [self.LOCKED_DOOR],
                self.BALL_ROOM: [self.LOCKED_DOOR],
            },
            added_zones_items={
                self.START: [self.CLOSED_DOOR],
                self.BALL_ROOM: [self.CLOSED_DOOR],
            },
            zones=[self.START, self.BALL_ROOM],
        )
        transformations.append(unlock_door)

        open_door = Transformation(
            removed_zones_items={
                self.START: [self.CLOSED_DOOR],
                self.BALL_ROOM: [self.CLOSED_DOOR],
            },
            added_zones_items={
                self.START: [self.OPEN_DOOR],
                self.BALL_ROOM: [self.OPEN_DOOR],
            },
            zones=[self.START, self.BALL_ROOM],
        )
        transformations.append(open_door)

        return transformations


def test_build_env():
    env = KeyDoorCrafting()
    check.is_instance(env, CraftingEnv)
    expected_items = {
        Item("key"),
        Item("ball"),
    }
    check.equal(
        expected_items,
        set(env.world.items),
        msg=str(expected_items - set(env.world.items)),
    )
    expected_zones_items = {
        Item("open_door"),
        Item("closed_door"),
        Item("locked_door"),
        Item("key"),
        Item("ball"),
    }
    check.equal(
        expected_zones_items,
        set(env.world.zones_items),
        msg=str(expected_zones_items - set(env.world.zones_items)),
    )
    expected_zones = {
        Zone("start_room"),
        Zone("ball_room"),
    }
    check.equal(
        expected_zones,
        set(env.world.zones),
        msg=str(expected_zones - set(env.world.zones)),
    )
