from crafting.env import CraftingEnv
from crafting.transformation import Transformation
from crafting.elements import Item, ItemStack, Zone
from crafting.world import world_from_transformations


def classic_env():
    start_zone = Zone("start")
    other_zone = Zone("other_zone")
    zones = [start_zone, other_zone]

    move_to_other_zone = Transformation(
        destination=other_zone,
        zones=[start_zone],
    )

    wood = Item("wood")
    search_wood = Transformation(
        added_player_items=[ItemStack(wood)],
    )

    stone = Item("stone")
    search_stone = Transformation(
        added_player_items=[ItemStack(stone, 1)],
    )

    plank = Item("plank")
    craft_plank = Transformation(
        removed_player_items=[ItemStack(wood, 1)],
        added_player_items=[ItemStack(plank, 4)],
    )

    table = Item("table")
    craft_table = Transformation(
        removed_player_items=[ItemStack(plank, 4)],
        added_zone_items=[ItemStack(table)],
    )

    wood_house = Item("wood house")
    build_house = Transformation(
        removed_player_items=[ItemStack(plank, 32), ItemStack(wood, 8)],
        added_zone_items=[ItemStack(wood_house)],
    )

    items = [wood, stone, plank]
    zones_items = [table, wood_house]
    named_transformations = {
        "move_to_other_zone": move_to_other_zone,
        "search_wood": search_wood,
        "search_stone": search_stone,
        "craft_plank": craft_plank,
        "craft_table": craft_table,
        "build_house": build_house,
    }

    world = world_from_transformations(
        transformations=list(named_transformations.values()),
        start_zone=start_zone,
    )
    env = CraftingEnv(world)
    return env, world, named_transformations, start_zone, items, zones, zones_items


def player_only_env():
    wood = Item("wood")
    search_wood = Transformation(
        added_player_items=[ItemStack(wood)],
    )

    stone = Item("stone")
    search_stone = Transformation(
        added_player_items=[ItemStack(stone, 1)],
    )

    plank = Item("plank")
    craft_plank = Transformation(
        removed_player_items=[ItemStack(wood, 1)],
        added_player_items=[ItemStack(plank, 4)],
    )

    items = [wood, stone, plank]
    named_transformations = {
        "search_wood": search_wood,
        "search_stone": search_stone,
        "craft_plank": craft_plank,
    }

    world = world_from_transformations(
        transformations=list(named_transformations.values())
    )
    env = CraftingEnv(world)
    return env, world, named_transformations, None, items, [], []


def zone_only_env():
    start_zone = Zone("start")
    wood = Item("wood")
    search_wood = Transformation(
        added_zone_items=[ItemStack(wood)],
    )

    stone = Item("stone")
    search_stone = Transformation(
        added_zone_items=[ItemStack(stone, 1)],
    )

    plank = Item("plank")
    craft_plank = Transformation(
        removed_zone_items=[ItemStack(wood, 1)],
        added_zone_items=[ItemStack(plank, 4)],
    )

    zones_items = [wood, stone, plank]
    named_transformations = {
        "search_wood": search_wood,
        "search_stone": search_stone,
        "craft_plank": craft_plank,
    }

    world = world_from_transformations(
        transformations=list(named_transformations.values()),
        start_zone=start_zone,
    )
    env = CraftingEnv(world)
    return env, world, named_transformations, start_zone, [], [], zones_items
