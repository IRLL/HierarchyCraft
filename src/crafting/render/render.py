# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=no-member

""" Rendering of the Crafting environments """

import os
import sys

from typing import TYPE_CHECKING, List, Optional, Union

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
    TransformationsWidget,
    PostitionWidget,
)


class CraftingWindow:
    def __init__(self, env: "CraftingEnv") -> None:
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
        self.make_menus()

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
        self.player_inventory.update(self.env.player_inventory, events)
        self.player_inventory.draw(self.screen)

        self.zone_inventory.update(self.env.current_zone_inventory, events)
        self.zone_inventory.draw(self.screen)

        # Update position
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

    def make_menus(self):
        """Build menus for user interface.

        Args:
            world: The current world.
            window_shape: Shape of the window containing menus.

        """

        # Transformations (Actions)
        action_menu_width = int(0.3 * self.window_shape[0])
        self.actions_menu = TransformationsWidget(
            title="Actions",
            height=self.window_shape[1],
            width=action_menu_width,
            transformations=self.env.transformations,
            position=(0, 0),
            resources_path=self.env.resources_path,
            theme=THEME_DARK,
        )

        player_menu_width = int(0.475 * self.window_shape[0])
        self.player_inventory = InventoryWidget(
            title="Inventory",
            height=self.window_shape[1],
            width=player_menu_width,
            position=(action_menu_width, 0, False),
            items=self.env.world.items,
            resources_path=self.env.resources_path,
            theme=Theme(
                background_color=(60, 60, 60),
                title_background_color=(47, 48, 51),
                title_font_color=(215, 215, 215),
                selection_color=(255, 255, 255, 0),
                widget_font_color=(255, 255, 255),
            ),
        )

        # Current zone inventory
        zone_menu_height = int(0.78 * self.window_shape[1])
        zone_menu_width = self.window_shape[0] - action_menu_width - player_menu_width
        self.zone_inventory = InventoryWidget(
            title="Zone",
            height=zone_menu_height,
            width=zone_menu_width,
            position=(
                action_menu_width + player_menu_width,
                self.window_shape[1] - zone_menu_height,
                False,
            ),
            items=self.env.world.zones_items,
            resources_path=self.env.resources_path,
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
        position_menu_height = self.window_shape[1] - zone_menu_height
        self.position = PostitionWidget(
            title="Position",
            height=position_menu_height,
            width=zone_menu_width,
            position=(action_menu_width + player_menu_width, 0, False),
            zones=self.env.world.zones,
            resources_path=self.env.resources_path,
        )

    def close(self):
        """Closes the pygame window."""
        pygame.display.quit()
