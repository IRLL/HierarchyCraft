from typing import List

from hcraft.elements import Item, Zone
from hcraft.env import HcraftEnv
from hcraft.transformation import Transformation, Use, Yield, PLAYER, CURRENT_ZONE
from hcraft.world import world_from_transformations


def classic_env(player=PLAYER, current_zone=CURRENT_ZONE, include_move=True):
    start_zone = Zone("start")
    other_zone = Zone("other_zone")
    zones = [start_zone, other_zone]

    transformations: List[Transformation] = []
    if include_move:
        move_to_other_zone = Transformation(
            "move_to_other_zone",
            destination=other_zone,
            zones=[start_zone],
        )
        transformations.append(move_to_other_zone)

    wood = Item("wood")
    search_wood = Transformation(
        "search_wood",
        inventory_changes=[Yield(player, wood)],
    )
    transformations.append(search_wood)

    stone = Item("stone")
    search_stone = Transformation(
        "search_stone",
        inventory_changes=[Yield(player, stone)],
    )
    transformations.append(search_stone)

    plank = Item("plank")
    craft_plank = Transformation(
        "craft_plank",
        inventory_changes=[
            Use(player, wood, consume=1),
            Yield(player, plank, create=4),
        ],
    )
    transformations.append(craft_plank)

    table = Item("table")
    craft_table = Transformation(
        "craft_table",
        inventory_changes=[
            Use(player, plank, consume=4),
            Yield(current_zone, table),
        ],
    )
    transformations.append(craft_table)

    wood_house = Item("wood house")
    build_house = Transformation(
        "build_house",
        inventory_changes=[
            Use(player, plank, consume=32),
            Use(player, wood, consume=8),
            Yield(current_zone, wood_house),
        ],
    )
    transformations.append(build_house)

    items = [wood, stone, plank]
    zones_items = [table, wood_house]
    named_transformations = {t.name: t for t in transformations}

    start_zone = start_zone if include_move else None
    world = world_from_transformations(
        transformations=list(named_transformations.values()),
        start_zone=start_zone,
    )
    env = HcraftEnv(world)
    return env, world, named_transformations, start_zone, items, zones, zones_items


def player_only_env():
    return classic_env(current_zone=PLAYER, include_move=False)


def zone_only_env():
    return classic_env(player=CURRENT_ZONE)
