from argparse import ArgumentParser, Namespace, _SubParsersAction
from typing import List, Optional

from hcraft.elements import Item
from hcraft.env import HcraftEnv
from hcraft.examples import (
    LightRecursiveHcraftEnv,
    MineHcraftEnv,
    RandomHcraftEnv,
    RecursiveHcraftEnv,
    TowerHcraftEnv,
)
from hcraft.purpose import Purpose
from hcraft.render.render import HcraftWindow
from hcraft.render.widgets import ContentMode, DisplayMode
from hcraft.task import GetItemTask


def hcraft_cli(args: Optional[List[str]] = None) -> HcraftEnv:
    """Parse arguments to build a hcraft environment.

    Args:
        args: Optional list of arguments to parse. Parses argv if None. Defaults to None.
    """
    parser = ArgumentParser()

    subparsers = parser.add_subparsers(help="Available environments")
    _minecraft_sub_parser(subparsers)
    _tower_sub_parser(subparsers)
    _recursive_sub_parser(subparsers)
    _light_recursive_sub_parser(subparsers)
    _random_sub_parser(subparsers)

    parser.add_argument(
        "--max-step",
        "-m",
        type=int,
        default=None,
        help="Max number of steps, no limit if None. Default to None.",
    )

    purpose = parser.add_argument_group("purpose")
    purpose.add_argument(
        "--goal-reward",
        type=float,
        default=10.0,
        help="Reward for completed tasks. Default to 10.",
    )
    purpose.add_argument(
        "--get-item",
        action="append",
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
        default=DisplayMode.CURRENT,
        choices=[mode.value for mode in DisplayMode],
        help="Which transformations to display.",
    )
    rendering.add_argument(
        "--transformation-content",
        "-tc",
        default=ContentMode.ALWAYS,
        choices=[mode.value for mode in ContentMode],
        help="When to display transformation's content.",
    )
    args = parser.parse_args(args)
    if "func" in args:
        env: "HcraftEnv" = args.func(args)
        return env
    raise ValueError(
        "No environment choosen. See available environments using 'hcraft --help'"
    )


def _window_from_cli(args: Namespace):
    return HcraftWindow(
        window_shape=args.window_shape,
        player_inventory_display=args.player_inventory_display,
        zone_inventory_display=args.zone_inventory_display,
        position_display=args.position_display,
        transformation_display=args.transformation_display,
        transformation_content=args.transformation_content,
    )


def _purpose_from_cli(args: Namespace):
    purpose = Purpose()
    for item_name in args.get_item:
        task = GetItemTask(Item(item_name), reward=args.goal_reward)
        purpose.add_task(task)
    return purpose


def _minecraft_sub_parser(subparsers: "_SubParsersAction[ArgumentParser]"):
    subparser = subparsers.add_parser(
        "minecraft",
        help="MineHcraft: Inspired from the popular game Minecraft.",
    )
    subparser.set_defaults(func=_minehcraft_from_cli)


def _minehcraft_from_cli(args: Namespace):
    window = _window_from_cli(args)
    purpose = _purpose_from_cli(args)
    env = MineHcraftEnv(
        purpose=purpose,
        render_window=window,
        max_step=args.max_step,
    )
    return env


def _tower_sub_parser(subparsers: "_SubParsersAction[ArgumentParser]"):
    subparser = subparsers.add_parser(
        "tower",
        help="TowerHcraft: Evaluate sub-behaviors reusability.",
        description="The goal of the environment is to get the item on top of the tower."
        " The tower has 'height' layers and 'width' items per layer"
        "plus the final item on top of the last layer."
        " Each item in the tower requires all the items of the previous layer to be built."
        " Items of the floor layer require nothing and can be built from the start.",
    )
    subparser.set_defaults(func=_towerhcraft_from_cli)
    subparser.add_argument(
        "--height", "-t", type=int, default=3, help="Height of the tower."
    )
    subparser.add_argument(
        "--width", "-w", type=int, default=2, help="Width of the tower."
    )


def _towerhcraft_from_cli(args: Namespace):
    window = _window_from_cli(args)
    env = TowerHcraftEnv(
        height=args.height,
        width=args.width,
        render_window=window,
        max_step=args.max_step,
    )
    return env


def _recursive_sub_parser(subparsers: "_SubParsersAction[ArgumentParser]"):
    subparser = subparsers.add_parser(
        "recursive",
        help="RecursiveHcraft: naive worst case if not using reusability.",
    )
    subparser.set_defaults(func=_recursivehcraft_from_cli)
    subparser.add_argument("--n-items", "-n", type=int, default=6)


def _recursivehcraft_from_cli(args: Namespace):
    window = _window_from_cli(args)
    env = RecursiveHcraftEnv(
        n_items=args.n_items,
        render_window=window,
        max_step=args.max_step,
    )
    return env


def _light_recursive_sub_parser(subparsers: "_SubParsersAction[ArgumentParser]"):
    subparser = subparsers.add_parser(
        "light-recursive",
        help="LightRecursiveHcraft: Lighter naive worst case if not using reusability.",
    )
    subparser.set_defaults(func=_light_recursivehcraft_from_cli)
    subparser.add_argument("--n-items", "-n", type=int, default=10)
    subparser.add_argument("--n-required-previous", "-p", type=int, default=2)


def _light_recursivehcraft_from_cli(args: Namespace):
    window = _window_from_cli(args)
    return LightRecursiveHcraftEnv(
        n_items=args.n_items,
        n_required_previous=args.n_required_previous,
        render_window=window,
        max_step=args.max_step,
    )


def _random_sub_parser(subparsers: "_SubParsersAction[ArgumentParser]"):
    subparser = subparsers.add_parser(
        "random",
        help="RandomHcraft: Random simple hierarchical structures.",
    )
    subparser.set_defaults(func=_randomhcraft_from_cli)
    subparser.add_argument(
        "--n-items-0",
        "-n0",
        type=int,
        default=1,
        help="Number of items without any inputs.",
    )
    for n_inputs in range(1, 5):
        subparser.add_argument(
            f"--n-items-{n_inputs}",
            f"-n{n_inputs}",
            type=int,
            default=0,
            help=f"Number of items with {n_inputs} input.",
        )


def _randomhcraft_from_cli(args: Namespace):
    window = _window_from_cli(args)
    n_items_per_n_inputs = {
        n_inputs: getattr(args, f"n_items_{n_inputs}") for n_inputs in range(5)
    }
    if sum(n_items_per_n_inputs.values()) == 1:
        n_items_per_n_inputs = None
    return RandomHcraftEnv(
        n_items_per_n_inputs=n_items_per_n_inputs,
        render_window=window,
        max_step=args.max_step,
    )


if __name__ == "__main__":
    hcraft_cli()
