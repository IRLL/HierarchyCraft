# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=no-member

""" Rendering of the Crafting environments """

import os
import sys

from typing import TYPE_CHECKING, Dict, List, Optional, Union

import numpy as np

try:
    import pygame
    from pygame.time import Clock
    from pygame_menu.menu import Menu
    from pygame_menu.themes import THEME_DARK, THEME_GREEN, THEME_DEFAULT, Theme
    from pygame_menu.widgets import Button, Image as PyImage
except ImportError:
    pass

from crafting.world import ItemStack


if TYPE_CHECKING:
    from PIL.Image import Image
    from pygame.event import Event
    from crafting.env import CraftingEnv

from crafting.world import Item, Zone
from crafting.render.utils import draw_text_on_image, load_image


class InventoryWidget(Menu):
    def __init__(
        self,
        title: str,
        height: int,
        width: int,
        position,
        items: List[Item],
        base_images: Dict[Item, "Image"],
        resources_path: str,
        theme: Theme = THEME_DEFAULT,
    ):
        super().__init__(
            title=title,
            center_content=True,
            height=height,
            width=width,
            rows=len(items),
            columns=1,
            position=position,
            overflow=(False, True),
            theme=theme,
        )

        self.items = items
        self.base_images = base_images
        self.resources_path = resources_path
        self.button_id_to_item = {}
        self.old_quantity = {}
        for item in self.items:
            image = self.base_images[item]
            if image is not None:
                image = draw_text_on_image(image, "0", self.resources_path)
                button: PyImage = self.add.image(image)
            else:
                button: Button = self.add.button(str(item))
            button.is_selectable = False
            self.button_id_to_item[button.get_id()] = item

    def update(self, inventory: np.ndarray, events) -> bool:
        items_buttons = [
            widget
            for widget in self.get_widgets()
            if isinstance(widget, (Button, PyImage))
        ]
        for button in items_buttons:
            item = self.button_id_to_item[button.get_id()]
            item_slot = self.items.index(item)
            quantity = inventory[item_slot]
            old_quantity = self.old_quantity.get(item, None)

            if old_quantity is not None and quantity == old_quantity:
                continue

            if isinstance(button, PyImage):
                image = draw_text_on_image(
                    self.base_images[item],
                    text=str(quantity),
                    ressources_path=self.resources_path,
                )
                button.set_image(image)
                button.render()

            button.set_title(str(ItemStack(item, quantity)))
            self.old_quantity[item] = quantity

            show_button = quantity > 0
            if show_button:
                button.show()
            else:
                button.hide()
        return super().update(events)


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

        # Load images
        self.base_images = self.load_base_images()

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

        # Update actions menu
        action_taken = None
        action_is_legal = self.env.actions_mask
        action_buttons = [
            widget
            for widget in self.actions_menu.get_widgets()
            if isinstance(widget, (Button, PyImage))
        ]
        for button in action_buttons:
            action = self.button_id_to_action[button.get_id()]
            show_button = action_is_legal[action]
            if show_button:
                button.show()
            else:
                button.hide()

        self.actions_menu.update(events)
        self.actions_menu.draw(self.screen)

        # Gather action taken if any
        selected_widget = self.actions_menu.get_selected_widget()
        if selected_widget is not None and selected_widget.update(events):
            action_taken: int = selected_widget.apply()

        # Update surface
        pygame.display.update()
        return action_taken

    def load_base_images(self) -> Dict[Union[Item, Zone], "Image"]:
        base_images = {}
        for obj in (
            self.env.world.items + self.env.world.zones_items + self.env.world.zones
        ):
            base_images[obj] = load_image(self.env.resources_path, obj=obj)
        return base_images

    def make_menus(self):
        """Build menus for user interface.

        Args:
            world: The current world.
            window_shape: Shape of the window containing menus.

        """

        # Transformations (Actions)
        action_menu_width = int(0.5 * self.window_shape[0])
        self.actions_menu = Menu(
            title="Actions",
            center_content=True,
            height=self.window_shape[1],
            width=action_menu_width,
            rows=len(self.env.transformations),
            columns=1,
            position=(0, 0),
            overflow=(True, True),
            theme=THEME_DARK,
        )

        self.button_id_to_action = {}
        for action, transfo in enumerate(self.env.transformations):
            button_id = _add_button_to_menu(
                self.actions_menu,
                text=str(transfo),
                text_width=8,
                index=action,
                padding=(16, 0, 16, 0),
            )
            self.button_id_to_action[button_id] = action

        player_menu_width = int(0.25 * self.window_shape[0])
        self.player_inventory = InventoryWidget(
            title="Inventory",
            height=self.window_shape[1],
            width=player_menu_width,
            position=(action_menu_width, 0, False),
            items=self.env.world.items,
            base_images=self.base_images,
            resources_path=self.env.resources_path,
        )

        # Current zone inventory
        zone_menu_height = int(0.7 * self.window_shape[1])
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
            base_images=self.base_images,
            resources_path=self.env.resources_path,
            theme=THEME_GREEN,
        )


def _add_button_to_menu(
    menu: "Menu",
    text_width: int,
    index: int,
    padding,
    image: Optional["Image"] = None,
    text: Optional[str] = None,
):
    if text is None:
        text = " " * text_width
    button = menu.add.button(
        text,
        lambda x: x,
        index,
        padding=padding,
        font_size=20,
    )
    if image is not None:
        decorator = button.get_decorator()
        decorator.add_baseimage(0, 0, image, centered=True)
    return button.get_id()
