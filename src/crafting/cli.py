import argparse

from typing import Optional, List

from crafting.env import CraftingEnv
from crafting.world import Item
from crafting.purpose import Purpose
from crafting.task import GetItemTask, GoToZoneTask
from crafting.render.render import CraftingWindow

from crafting.examples import (
    MineCraftingEnv,
    RandomCraftingEnv,
    RecursiveCraftingEnv,
    LightRecursiveCraftingEnv,
    TowerCraftingEnv,
)
from crafting.render.human import render_env_with_human

from crafting.render.widgets import DisplayMode, ContentMode


def crafting_cli(args: Optional[List[str]] = None) -> CraftingEnv:
    """Parse arguments to build a crafting environment.

    Args:
        args: Optional list of arguments to parse. Parses argv if None. Defaults to None.
    """
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(help="Available Crafting environments")
    minecraft_parser = subparsers.add_parser(
        "minecraft",
        help="MineCrafting environment inspired from the popular game Minecraft.",
    )
    minecraft_parser.set_defaults(func=_minecrafting_from_cli)

    purpose = parser.add_argument_group("purpose")
    purpose.add_argument(
        "--goal-reward",
        type=float,
        default=10.0,
        help="Reward for completed tasks. Default to 10.",
    )
    purpose.add_argument(
        "--get-items",
        action="extend",
        nargs="+",
        type=str,
        default=[],
        help="Items to get as task given to the player.",
    )

    rendering = parser.add_argument_group("rendering")
    rendering.add_argument(
        "--window-shape",
        "-s",
        type=tuple,
        default=(1280, 720),
        help="Shape of the render windon. Default to (1280, 720).",
    )
    rendering.add_argument(
        "--player-inventory-display",
        "-id",
        type=str,
        default=DisplayMode.CURRENT,
        choices=[mode.value for mode in DisplayMode],
        help="Which items in the inventory to display.",
    )
    rendering.add_argument(
        "--zone-inventory-display",
        "-zd",
        type=str,
        default=DisplayMode.CURRENT,
        choices=[mode.value for mode in DisplayMode],
        help="Which items of the current zone to display.",
    )
    rendering.add_argument(
        "--position-display",
        "-pd",
        type=str,
        default=DisplayMode.CURRENT,
        choices=[mode.value for mode in DisplayMode],
        help="Which zones to display.",
    )
    rendering.add_argument(
        "--transformation-display",
        "-td",
        type=str,
        default=DisplayMode.DISCOVERED,
        choices=[mode.value for mode in DisplayMode],
        help="Which transformations to display.",
    )
    rendering.add_argument(
        "--transformation-content",
        "-tc",
        default=ContentMode.DISCOVERED,
        choices=[mode.value for mode in ContentMode],
        help="When to display transformation's content.",
    )
    args = parser.parse_args(args)
    if "func" in args:
        env: "CraftingEnv" = args.func(args)
        return env
    raise ValueError(
        "No environment choosen. See available environments using 'crafting --help'"
    )


def _window_from_cli(args: argparse.Namespace):
    return CraftingWindow(
        window_shape=args.window_shape,
        player_inventory_display=args.player_inventory_display,
        zone_inventory_display=args.zone_inventory_display,
        position_display=args.position_display,
        transformation_display=args.transformation_display,
        transformation_content=args.transformation_content,
    )


def _purpose_from_cli(args: argparse.Namespace):
    purpose = Purpose()
    for item_name in args.get_items:
        task = GetItemTask(Item(item_name), reward=args.goal_reward)
        purpose.add_task(task)
    return purpose


def _minecrafting_from_cli(args: argparse.Namespace):
    window = _window_from_cli(args)
    purpose = _purpose_from_cli(args)
    env = MineCraftingEnv(purpose=purpose, render_window=window)
    return env


if __name__ == "__main__":
    crafting_cli()
