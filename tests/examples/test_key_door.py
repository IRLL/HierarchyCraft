from typing import List

import networkx as nx

from crafting.env import CraftingEnv
from crafting.world import Item, Zone, world_from_transformations
from crafting.transformation import Transformation
from crafting.task import GetItemTask

import pytest_check as check
from tests.custom_checks import check_isomorphic


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
            start_zone=self.START,
            start_zones_items={self.BALL_ROOM: [self.BALL]},
        )
        self.goal = GetItemTask(self.BALL)
        super().__init__(
            world,
            purpose=self.goal,
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
            removed_player_items=[self.KEY],
            added_player_items=[self.KEY],
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

        move_to_ball_room = Transformation(
            destination=self.BALL_ROOM,
            removed_zone_items=[self.OPEN_DOOR],
            added_zone_items=[self.OPEN_DOOR],
            zones=[self.START],
        )
        transformations.append(move_to_ball_room)

        move_to_start_room = Transformation(
            destination=self.START,
            removed_zone_items=[self.OPEN_DOOR],
            added_zone_items=[self.OPEN_DOOR],
            zones=[self.BALL_ROOM],
        )
        transformations.append(move_to_start_room)

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


def test_can_solve():
    env = KeyDoorCrafting(max_step=20)
    solving_behavior = env.solving_behavior(env.goal)
    done = False
    observation = env.reset()
    while not done:
        action = solving_behavior(observation)
        observation, _reward, done, _ = env.step(action)
    check.is_true(env.goal.is_terminated)


def test_requirements_graph():
    draw = False

    expected_graph = nx.DiGraph()
    expected_graph.add_edge("START#", "start_room")
    expected_graph.add_edge("start_room", "key_in_zone")
    expected_graph.add_edge("key_in_zone", "key")
    expected_graph.add_edge("key", "key_in_zone")
    expected_graph.add_edge("key", "closed_door")
    expected_graph.add_edge("key", "open_door")
    expected_graph.add_edge("start_room", "locked_door")
    expected_graph.add_edge("ball_room", "locked_door")
    expected_graph.add_edge("locked_door", "closed_door")
    expected_graph.add_edge("locked_door", "open_door")
    expected_graph.add_edge("start_room", "closed_door")
    expected_graph.add_edge("ball_room", "closed_door")
    expected_graph.add_edge("closed_door", "open_door")
    expected_graph.add_edge("start_room", "open_door")
    expected_graph.add_edge("ball_room", "open_door")
    expected_graph.add_edge("open_door", "ball_room")
    expected_graph.add_edge("start_room", "ball_room")
    expected_graph.add_edge("open_door", "start_room")
    expected_graph.add_edge("ball_room", "start_room")
    expected_graph.add_edge("ball_in_zone", "ball")
    expected_graph.add_edge("ball", "ball_in_zone")
    expected_graph.add_edge("ball_room", "ball_in_zone")

    env = KeyDoorCrafting(max_step=20)
    check_isomorphic(env.requirements.digraph, expected_graph)

    if draw:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        env.requirements.draw(ax, layout="spring")
        plt.show()
        plt.close()
