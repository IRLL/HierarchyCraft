# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=no-member

""" Rendering of the Crafting environments """

import os
import sys
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

try:
    import pygame
    from pygame.time import Clock
    from pygame_menu.themes import THEME_DARK, THEME_GREEN, Theme
except ImportError:
    pass


from crafting.render.widgets import (
    ContentMode,
    DisplayMode,
    InventoryWidget,
    PostitionWidget,
    TransformationsWidget,
)

if TYPE_CHECKING:
    from PIL.Image import Image
    from pygame.event import Event

    from crafting.env import CraftingEnv


class CraftingWindow:
    """Render window for any Crafting environment UI."""

    def __init__(
        self,
        window_shape: Tuple[int, int] = (1280, 720),
        player_inventory_display: DisplayMode = DisplayMode.CURRENT,
        zone_inventory_display: DisplayMode = DisplayMode.CURRENT,
        position_display: DisplayMode = DisplayMode.CURRENT,
        transformation_display_mode: DisplayMode = DisplayMode.DISCOVERED,
        transformation_content_mode: ContentMode = ContentMode.DISCOVERED,
    ) -> None:
        """Initialize a Crafting window without building it on a specific environment (yet).

        Args:
            window_shape (Tuple[int, int], optional): Size of the window. Defaults to (1280, 720).
            player_inventory_display (DisplayMode, optional): When to see items in inventory.
                Defaults to DisplayMode.CURRENT.
            zone_inventory_display (DisplayMode, optional): When to see current zone items.
                Defaults to DisplayMode.CURRENT.
            position_display (DisplayMode, optional): When to see zones.
                Defaults to DisplayMode.CURRENT.
            transformation_display_mode (DisplayMode, optional): When to see transformations.
                Defaults to DisplayMode.DISCOVERED.
            transformation_content_mode (ContentMode, optional): When to reveal transformations.
                Defaults to ContentMode.DISCOVERED.

        Raises:
            ImportError: If pygame could not be imported.
        """
        try:
            pygame.init()
        except NameError as error:
            raise ImportError(
                "Missing import for rendering user interface. "
                "Install using 'pip install crafting-gym[gui]'."
            ) from error

        self.env = None
        self.clock = None
        self.screen = None
        self.menus = {}
        self.window_shape = window_shape

        self.player_inventory_display = player_inventory_display
        self.zone_inventory_display = zone_inventory_display
        self.position_display = position_display
        self.transformation_display_mode = transformation_display_mode
        self.transformation_content_mode = transformation_content_mode

    @property
    def built(self) -> bool:
        """True only if the render window has been built on a specific Crafting environement."""
        return self.env is not None

    def build(self, env: "CraftingEnv"):
        """Build the render window on the given environement.

        Args:
            env (CraftingEnv): Crafting environment on which to build the render window.
        """
        self.env = env
        self.clock = Clock()

        # Create window with loading screen
        os.environ["SDL_VIDEO_CENTERED"] = "1"
        self.screen = pygame.display.set_mode(self.window_shape)
        pygame.display.set_caption("Crafting")
        self._loading_screen()

        # Create menus
        self.menus = self.make_menus(
            self.player_inventory_display,
            self.zone_inventory_display,
            self.position_display,
            self.transformation_display_mode,
            self.transformation_content_mode,
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

        if not self.built:
            raise RuntimeError("Render window tried to update before being built.")

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
        if self.menus["player_inventory"]:
            self.menus["player_inventory"].update_inventory(
                self.env.player_inventory, self.env.discovered_items, events
            )
            self.menus["player_inventory"].draw(self.screen)

        if self.menus["zone_inventory"]:
            self.menus["zone_inventory"].update_inventory(
                self.env.current_zone_inventory, self.env.discovered_zones_items, events
            )
            self.menus["zone_inventory"].draw(self.screen)

        # Update position
        if self.menus["position"]:
            self.menus["position"].update_position(
                self.env.position, self.env.discovered_zones, events
            )
            self.menus["position"].draw(self.screen)

        # Update actions menu
        self.menus["actions"].update_transformations(self.env, events)
        self.menus["actions"].draw(self.screen)

        # Gather action taken if any
        action_taken = None
        selected_widget = self.menus["actions"].get_selected_widget()
        if selected_widget is not None and selected_widget.update(events):
            action_taken: int = selected_widget.apply()

        # Update surface
        pygame.display.update()
        return action_taken

    def make_menus(
        self,
        player_inventory_display: DisplayMode,
        zone_inventory_display: DisplayMode,
        position_display: DisplayMode,
        transformation_display_mode: DisplayMode,
        transformation_content_mode: ContentMode,
    ) -> Dict[str, Union[TransformationsWidget, InventoryWidget, PostitionWidget]]:
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

        actions_menu = TransformationsWidget(
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
        player_inventory = None
        if menus_shapes["player"] != (0, 0):
            player_inventory = InventoryWidget(
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
        zone_inventory = None
        if menus_shapes["zone"] != (0, 0):
            zone_inventory = InventoryWidget(
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
        position = None
        if menus_shapes["position"] != (0, 0):
            position = PostitionWidget(
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
                display_mode=position_display,
            )

        return {
            "actions": actions_menu,
            "player_inventory": player_inventory,
            "zone_inventory": zone_inventory,
            "position": position,
        }

    def close(self):
        """Closes the pygame window."""
        pygame.display.quit()

    def _loading_screen(self):
        bg_color = (55, 55, 55)
        self.screen.fill(bg_color)
        quarter_width = self.window_shape[0] // 4
        quarter_height = self.window_shape[1] // 4
        pygame.draw.rect(
            self.screen,
            color=(0, 130, 60),
            rect=(quarter_width, quarter_height, 2 * quarter_width, 2 * quarter_height),
            border_radius=8,
        )
        font = pygame.font.SysFont(
            os.path.join(self.env.resources_path, "font.ttf"), 30
        )
        font_surface = font.render("Loading ...", True, bg_color)
        text_size = font_surface.get_size()
        self.screen.blit(
            font_surface,
            (
                self.window_shape[0] // 2 - text_size[0] // 2,
                self.window_shape[1] // 2 - text_size[1] // 2,
            ),
        )
        pygame.display.update()


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
