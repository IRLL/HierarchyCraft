# # Crafting a meta-environment to simultate inventory managment
# # Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Widgets for rendering of the Crafting environments """

import os
from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Union

import numpy as np

# pygame in an optional dependency
try:
    from pygame.font import Font
    from pygame.image import load as load_pygame_image
    from pygame_menu.locals import ALIGN_LEFT
    from pygame_menu.menu import Menu
    from pygame_menu.themes import THEME_DEFAULT, Theme
    from pygame_menu.widgets import Button
    from pygame_menu.widgets import Image as PyImage
except ImportError:
    Menu = object
    THEME_DEFAULT = None

from crafting.render.utils import (
    _to_menu_image,
    build_transformation_image,
    draw_text_on_image,
    load_image,
    pilImageToSurface,
    scale,
)
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack, Zone

if TYPE_CHECKING:
    from PIL.Image import Image
    from pygame.surface import Surface

    from crafting.env import CraftingEnv


class InventoryDisplayMode(Enum):
    ALL = "all"
    DISCOVERED = "discovered"
    CURRENT = "current"


class InventoryWidget(Menu):
    def __init__(
        self,
        title: str,
        height: int,
        width: int,
        position,
        items: List[Item],
        resources_path: str,
        display_mode: InventoryDisplayMode,
        rows: int = 9,
        theme: "Theme" = THEME_DEFAULT,
    ):
        super().__init__(
            title=title,
            center_content=True,
            height=height,
            width=width,
            rows=rows,
            columns=len(items) // rows + 1,
            position=position,
            overflow=(False, True),
            theme=theme,
        )

        self.items = items
        self.resources_path = resources_path
        self.display_mode = InventoryDisplayMode(display_mode)
        self.base_images = _load_base_images(items, resources_path)

        self.button_id_to_item = {}
        self.old_quantity = {}
        for item in self.items:
            self._build_button(item)

    def update(self, inventory: np.ndarray, discovered: np.ndarray, events) -> bool:
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
                base_image = self.base_images[item]
                if quantity == 0:
                    # Grayscale
                    base_image = base_image.convert("LA").convert("RGBA")
                if quantity != 1:
                    image = draw_text_on_image(
                        base_image,
                        text=str(quantity),
                        resources_path=self.resources_path,
                    )
                button.set_image(_to_menu_image(image, 0.5))
                button.render()

            button.set_title(str(ItemStack(item, quantity)))
            self.old_quantity[item] = quantity

            show_button = True
            if self.display_mode is InventoryDisplayMode.CURRENT:
                show_button = quantity > 0
            elif self.display_mode is InventoryDisplayMode.DISCOVERED:
                show_button = discovered[item_slot]

            if show_button:
                button.show()
            else:
                button.hide()
        return super().update(events)

    def _build_button(self, item: Item) -> None:
        image = self.base_images[item]
        if image is not None:
            image = draw_text_on_image(image, "0", self.resources_path)
            button: PyImage = self.add.image(_to_menu_image(image, 0.5))
        else:
            button: Button = self.add.button(str(item))
        button.is_selectable = False
        self.button_id_to_item[button.get_id()] = item


def _load_base_images(
    objs: List[Union[Item, Zone]], resources_path: str
) -> Dict[Union[Item, Zone], "Image"]:
    base_images = {}
    for obj in objs:
        base_images[obj] = load_image(resources_path, obj=obj)
    return base_images


class TransformationsWidget(Menu):
    def __init__(
        self,
        title: str,
        height: int,
        width: int,
        position,
        transformations: List[Transformation],
        resources_path: str,
        theme: "Theme" = THEME_DEFAULT,
    ):
        super().__init__(
            title=title,
            center_content=False,
            height=height,
            width=width,
            rows=len(transformations),
            columns=1,
            position=position,
            overflow=(False, True),
            theme=theme,
        )

        self.transformations = transformations
        self.resources_path = resources_path
        self.button_id_to_transfo = {}
        self.old_quantity = {}
        for index, transfo in enumerate(self.transformations):
            button = self._build_transformation_button(transfo, index)
            self.button_id_to_transfo[button.get_id()] = transfo

    def _build_transformation_button(
        self, transfo: Transformation, action_id: int
    ) -> "Button":
        button: PyImage = self.add.button(
            " ",
            lambda x: x,
            action_id,
            padding=(16, 16, 16, 16),
            align=ALIGN_LEFT,
        )
        image = build_transformation_image(transfo, self.resources_path)
        if image is not None:
            decorator = button.get_decorator()
            menu_image = _to_menu_image(image, 0.4)
            decorator.add_baseimage(0, 0, menu_image, centered=True)
            img_width, img_height = menu_image.get_size()
            width_padding = (img_width - button.get_width(apply_padding=False)) // 2
            height_padding = (img_height - button.get_height(apply_padding=False)) // 2
            button.set_padding((height_padding, width_padding))
            button.set_margin(8, 16)
        else:
            button.set_title(str(transfo))
        return button

    def update(self, env: "CraftingEnv", events) -> bool:
        action_is_legal = env.actions_mask
        action_buttons = [
            widget for widget in self.get_widgets() if isinstance(widget, (Button))
        ]
        for button in action_buttons:
            transfo = self.button_id_to_transfo[button.get_id()]
            action = env.transformations.index(transfo)
            show_button = action_is_legal[action]
            if show_button:
                button.show()
            else:
                button.hide()
        return super().update(events)


class PostitionWidget(Menu):
    def __init__(
        self,
        title: str,
        height: int,
        width: int,
        position,
        zones: List[Zone],
        resources_path: str,
    ):
        super().__init__(
            title=title,
            center_content=False,
            height=height,
            width=width,
            rows=len(zones),
            columns=1,
            position=position,
            overflow=(False, True),
            theme=Theme(
                background_color=(186, 214, 177),
                selection_color=(255, 255, 255, 0),
                widget_font_color=(255, 255, 255),
                title=False,
                border_width=0,
                widget_border_width=0,
                scrollbar_slider_pad=0,
                scrollarea_outer_margin=(0, 0),
                scrollbar_thick=8,
                widget_alignment=ALIGN_LEFT,
            ),
        )

        self.zones = zones
        self.base_images = _load_base_images(zones, resources_path)
        self.resources_path = resources_path
        self.button_id_to_zone = {}
        self.old_quantity = {}
        for zone in self.zones:
            self._build_button(zone)

    def update(self, position: np.ndarray, events) -> bool:
        buttons = [
            widget for widget in self.get_widgets() if isinstance(widget, Button)
        ]
        for button in buttons:
            zone = self.button_id_to_zone[button.get_id()]
            zone_slot = self.zones.index(zone)
            show_button = position[zone_slot] == 1
            if show_button:
                button.show()
            else:
                button.hide()
        return super().update(events)

    def _build_button(self, zone: Zone) -> None:
        image = self.base_images[zone]
        font = os.path.join(self.resources_path, "font.ttf")
        button: Button = self.add.button(
            zone.name.capitalize(),
            font_name=font,
            font_color="white",
            font_size=48,
            border_width=0,
        )
        if image is not None:
            decorator = button.get_decorator()
            menu_image = _to_menu_image(image, 0.4)
            decorator.add_baseimage(0, 0, menu_image, centered=True)
            img_width, img_height = menu_image.get_size()
            width_padding = (img_width - button.get_width(apply_padding=False)) // 2
            height_padding = (img_height - button.get_height(apply_padding=False)) // 2
            button.set_padding((height_padding, width_padding))
        button.is_selectable = False
        self.button_id_to_zone[button.get_id()] = zone


# class ScoreWidget:

#     """Display the current score"""

#     def __init__(self, font_path: str, position: Tuple[int], font_size: int):
#         self.position = position
#         self.font = Font(font_path, font_size)
#         self.reward = 0
#         self.score = 0

#     def update(self, env: "CraftingEnv"):
#         self.score = env.player.score

#     def draw(self, surface: "Surface"):
#         score_name_img = self.font.render(f"SCORE {self.score}", False, "#c95149")
#         surface.blit(score_name_img, self.position)


# class StepLeftWidget:

#     """Display the number of steps left until the environment is done."""

#     def __init__(self, font_path: str, position: Tuple[int], font_size: int):
#         self.position = position
#         self.font = Font(font_path, font_size)
#         self.steps_left = None

#     def update(self, env: "CraftingEnv"):
#         self.steps_left = env.max_step - env.steps

#     def draw(self, surface: "Surface"):
#         score_name_img = self.font.render(
#             f"Steps left: {self.steps_left}", False, "#803300"
#         )
#         surface.blit(score_name_img, self.position)
