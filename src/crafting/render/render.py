# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=no-member

""" Rendering of the Crafting environments """

import os
import sys
from typing import TYPE_CHECKING, List, Dict, Optional, Union, Tuple

try:
    import pygame
    from pygame.time import Clock
    from pygame_menu.themes import THEME_DARK, THEME_GREEN, Theme
except ImportError:
    pass


if TYPE_CHECKING:
    from PIL.Image import Image
    from pygame.event import Event
    from crafting.env import CraftingEnv

from crafting.render.widgets import (
    InventoryWidget,
    InventoryDisplayMode,
    PostitionWidget,
    TransformationsWidget,
    TransformationContentMode,
    TransformationDisplayMode,
)


class CraftingWindow:
    def __init__(
        self,
        env: "CraftingEnv",
        player_inventory_display: InventoryDisplayMode,
        zone_inventory_display: InventoryDisplayMode,
        transformation_content_mode: TransformationContentMode,
        transformation_display_mode: TransformationDisplayMode,
    ) -> None:
        """Initialise pygame window, menus and widgets for the UI.

        Args:
            env: The running Crafting environment.
        """
        try:
            pygame.init()
        except NameError as error:
            raise ImportError(
                "Missing import for rendering user interface. "
                "Install using 'pip install crafting-gym[gui]'."
            ) from error

        self.env = env
        self.window_shape = (int(16 / 9 * 720), 720)
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        self.clock = Clock()

        # Create window
        self.screen = pygame.display.set_mode(self.window_shape)
        pygame.display.set_caption("Crafting")

        # Create menus
        self.make_menus(
            player_inventory_display,
            zone_inventory_display,
            transformation_content_mode,
            transformation_display_mode,
        )

    def update_rendering(
        self,
        additional_events: Optional[List["Event"]] = None,
        fps: Optional[float] = None,
    ) -> Union[int, None]:
        """Update the User Interface returning action if one was found.

        Args:
            additional_events (Optional): Additional pygame events to simulate.
            fps: frames_per_seconds

        Returns:
            Action found while updating the UI. (can be None)

        """
        # Tick
        if fps is not None:
            self.clock.tick(fps)

        # Paint background
        self.screen.fill((198, 198, 198))

        # Execute main from principal menu if is enabled
        events = pygame.event.get()
        if additional_events is not None:
            events += additional_events
        for event in events:
            if event.type == pygame.QUIT:
                sys.exit()

        # for widget in widgets:
        #     widget.update(env)
        #     widget.draw(screen)

        # Update inventories
        if self.player_inventory:
            self.player_inventory.update_inventory(
                self.env.player_inventory, self.env.discovered_items, events
            )
            self.player_inventory.draw(self.screen)

        if self.zone_inventory:
            self.zone_inventory.update_inventory(
                self.env.current_zone_inventory, self.env.discovered_zones_items, events
            )
            self.zone_inventory.draw(self.screen)

        # Update position
        if self.position:
            self.position.update(self.env.position, events)
            self.position.draw(self.screen)

        # Update actions menu
        self.actions_menu.update(self.env, events)
        self.actions_menu.draw(self.screen)

        # Gather action taken if any
        action_taken = None
        selected_widget = self.actions_menu.get_selected_widget()
        if selected_widget is not None and selected_widget.update(events):
            action_taken: int = selected_widget.apply()

        # Update surface
        pygame.display.update()
        return action_taken

    def make_menus(
        self,
        player_inventory_display: InventoryDisplayMode,
        zone_inventory_display: InventoryDisplayMode,
        transformation_content_mode: TransformationContentMode,
        transformation_display_mode: TransformationDisplayMode,
    ):
        """Build menus for user interface.

        Args:
            world: The current world.
            window_shape: Shape of the window containing menus.

        """

        # Transformations (Actions)
        menus_shapes = menus_sizes(
            self.env.world.n_items,
            self.env.world.n_zones_items,
            self.env.world.n_zones,
            self.window_shape,
        )

        self.actions_menu = TransformationsWidget(
            title="Actions",
            height=menus_shapes["actions"][1],
            width=menus_shapes["actions"][0],
            transformations=self.env.transformations,
            position=(0, 0),
            resources_path=self.env.resources_path,
            display_mode=transformation_display_mode,
            content_display_mode=transformation_content_mode,
            theme=THEME_DARK,
        )

        # Player inventory
        self.player_inventory = None
        if menus_shapes["player"] != (0, 0):
            self.player_inventory = InventoryWidget(
                title="Inventory",
                height=menus_shapes["player"][1],
                width=menus_shapes["player"][0],
                position=(
                    menus_shapes["actions"][0],
                    self.window_shape[1] - menus_shapes["player"][1],
                    False,
                ),
                items=self.env.world.items,
                resources_path=self.env.resources_path,
                display_mode=player_inventory_display,
                theme=Theme(
                    background_color=(60, 60, 60),
                    title_background_color=(47, 48, 51),
                    title_font_color=(215, 215, 215),
                    selection_color=(255, 255, 255, 0),
                    widget_font_color=(255, 255, 255),
                ),
            )

        # Current zone inventory
        self.zone_inventory = None
        if menus_shapes["zone"] != (0, 0):
            self.zone_inventory = InventoryWidget(
                title="Zone",
                height=menus_shapes["zone"][1],
                width=menus_shapes["zone"][0],
                position=(
                    menus_shapes["actions"][0] + menus_shapes["player"][0],
                    self.window_shape[1] - menus_shapes["zone"][1],
                    False,
                ),
                items=self.env.world.zones_items,
                resources_path=self.env.resources_path,
                display_mode=zone_inventory_display,
                theme=Theme(
                    title=False,
                    background_color=(186, 214, 177),
                    title_background_color=(47, 48, 51),
                    title_font_color=(215, 215, 215),
                    selection_color=(255, 255, 255, 0),
                    widget_font_color=(255, 255, 255),
                ),
            )

        # Position
        self.position = None
        if menus_shapes["position"] != (0, 0):
            self.position = PostitionWidget(
                title="Position",
                height=menus_shapes["position"][1],
                width=menus_shapes["position"][0],
                position=(
                    self.window_shape[0] - menus_shapes["position"][0],
                    0,
                    False,
                ),
                zones=self.env.world.zones,
                resources_path=self.env.resources_path,
            )

    def close(self):
        """Closes the pygame window."""
        pygame.display.quit()


def menus_sizes(
    n_items: int, n_zones_items: int, n_zones: int, window_shape: Tuple[int, int]
) -> Dict[str, Tuple[int, int]]:
    actions_size = (int(0.3 * window_shape[0]), window_shape[1])
    header_height = int(0.22 * window_shape[1])

    player_size = (0, 0)
    if n_items > 0:
        player_width = window_shape[0] - actions_size[0]
        if n_zones_items > 0:
            player_width = int(0.475 * window_shape[0])
        player_size = (player_width, window_shape[1] - header_height)

    zone_size = (0, 0)
    if n_zones_items > 0:
        zone_size = (
            window_shape[0] - actions_size[0] - player_size[0],
            window_shape[1] - header_height,
        )

    position_size = (0, 0)
    if n_zones > 1:
        position_size = (int(16 * header_height / 9), header_height)

    return {
        "actions": actions_size,
        "player": player_size,
        "zone": zone_size,
        "position": position_size,
    }
