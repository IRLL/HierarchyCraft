""" Widgets for rendering of the HierarchyCraft environments """

from enum import Enum
from typing import TYPE_CHECKING, Dict, List, Optional, Union

import numpy as np

# pygame in an optional dependency
try:
    from pygame_menu.locals import ALIGN_LEFT
    from pygame_menu.menu import Menu
    from pygame_menu.themes import THEME_DEFAULT, Theme
    from pygame_menu.widgets import Button
    from pygame_menu.widgets import Image as PyImage
except ImportError:
    Menu = object
    THEME_DEFAULT = None

from PIL.Image import Image

from hcraft.elements import Item, Stack, Zone
from hcraft.render.utils import (
    _font_path,
    _get_scale_ratio,
    _to_menu_image,
    build_transformation_image,
    create_text_image,
    draw_text_on_image,
    load_image,
)
from hcraft.transformation import Transformation

if TYPE_CHECKING:
    from pygame_menu.menu import Menu

    from hcraft.env import HcraftEnv


class DisplayMode(Enum):
    """Display modes for menus buttons."""

    ALL = "all"
    """Button are all displayed."""
    DISCOVERED = "discovered"
    """Button are displayed if they have been discovered or are currently available."""
    CURRENT = "current"
    """Button are only displayed if currently available."""


class ContentMode(Enum):
    """Display modes for buttons content."""

    ALWAYS = "always"
    """Button content are always displayed."""
    DISCOVERED = "discovered"
    """Button content are displayed if they have been discovered."""
    NEVER = "never"
    """Button content are never displayed."""


class InventoryWidget(Menu):
    def __init__(
        self,
        title: str,
        height: int,
        width: int,
        position,
        items: List[Item],
        resources_path: str,
        display_mode: DisplayMode,
        rows: int = 7,
        theme: "Theme" = THEME_DEFAULT,
        **kwargs,
    ):
        theme.title_font_size = 24
        super().__init__(
            title=title,
            center_content=True,
            height=height,
            width=width,
            rows=rows,
            columns=len(items) // rows + 1,
            position=position,
            overflow=(True, False),
            theme=theme,
            **kwargs,
        )

        self.items = items
        self.resources_path = resources_path
        self.display_mode = DisplayMode(display_mode)
        self.base_images = _load_base_images(items, resources_path)

        self.button_id_to_item = {}
        self.old_quantity = {}
        for item in self.items:
            self._build_button(item)

    def update_inventory(
        self,
        inventory: np.ndarray,
        discovered: np.ndarray,
        events,
        title: Optional[str] = None,
    ) -> bool:
        items_buttons = [
            widget
            for widget in self.get_widgets()
            if isinstance(widget, (Button, PyImage))
        ]
        for button in items_buttons:
            self._update_button(button, inventory, discovered)
        if title is not None:
            self.set_title(title)
        return super().update(events)

    def _build_button(self, item: Item) -> None:
        image = self.base_images[item]
        if image is not None:
            image = draw_text_on_image(image, "0", self.resources_path)
            button: "PyImage" = self.add.image(_to_menu_image(image, 0.5))
        else:
            button: "Button" = self.add.button(str(item))
        button.is_selectable = False
        self.button_id_to_item[button.get_id()] = item

    def _update_button(
        self,
        button: Union["Button", "PyImage"],
        inventory: np.ndarray,
        discovered: np.ndarray,
    ):
        item = self.button_id_to_item[button.get_id()]
        item_slot = self.items.index(item)
        quantity = inventory[item_slot]
        old_quantity = self.old_quantity.get(item, None)

        if old_quantity is not None and quantity == old_quantity:
            return

        if isinstance(button, PyImage):
            self._update_button_image(
                button, self.base_images[item], quantity, self.resources_path
            )

        button.set_title(str(Stack(item, quantity)))
        self.old_quantity[item] = quantity

        if show_button(self.display_mode, quantity > 0, discovered[item_slot]):
            button.show()
        else:
            button.hide()

    @staticmethod
    def _update_button_image(
        button: "PyImage", image: "Image", quantity: int, resources_path: str
    ):
        if quantity == 0:
            # Grayscale
            image = image.convert("LA").convert("RGBA")
        if quantity > 1:
            image = draw_text_on_image(
                image,
                text=str(quantity),
                resources_path=resources_path,
            )
        button.set_image(_to_menu_image(image, 0.5))
        button.render()


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
        display_mode: DisplayMode,
        content_display_mode: ContentMode,
        theme: "Theme" = THEME_DEFAULT,
        **kwargs,
    ):
        theme.title_font_size = 24
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
            **kwargs,
        )

        self.transformations = transformations
        self.resources_path = resources_path
        self.display_mode = DisplayMode(display_mode)
        self.content_display_mode = ContentMode(content_display_mode)
        self.button_id_to_transfo = {}
        self.old_display = {}
        self.old_legal = {}
        self.buttons_base_image: Dict[str, "Image"] = {}
        self.buttons_hidden_image: Dict[str, "Image"] = {}
        for index, transfo in enumerate(self.transformations):
            button = self._build_transformation_button(transfo, index)
            self.button_id_to_transfo[button.get_id()] = transfo

    def _build_transformation_button(
        self, transfo: Transformation, action_id: int
    ) -> "Button":
        button: "Button" = self.add.button(
            " ",
            lambda x: x,
            action_id,
            padding=(16, 16, 16, 16),
            align=ALIGN_LEFT,
        )
        image = build_transformation_image(transfo, self.resources_path)
        if image is not None:
            self.buttons_base_image[button.get_id()] = image
            self.buttons_hidden_image[button.get_id()] = create_text_image(
                text=str(action_id),
                resources_path=self.resources_path,
                image_size=image.size,
            )
            self._add_button_image(button, image)
        return button

    def update_transformations(self, env: "HcraftEnv", events) -> bool:
        action_is_legal = env.action_masks()
        action_buttons = [
            widget for widget in self.get_widgets() if isinstance(widget, Button)
        ]
        for button in action_buttons:
            self._update_button(button, env, action_is_legal)
        if env.max_step is not None:
            self.set_title(self._remaining_text(env.max_step - env.current_step))
        return super().update(events)

    @staticmethod
    def _remaining_text(actions_remaining: int):
        return f"Actions ({actions_remaining} remaining)"

    def _update_button(
        self, button: "Button", env: "HcraftEnv", action_is_legal: np.ndarray
    ):
        transfo = self.button_id_to_transfo[button.get_id()]
        action = env.world.transformations.index(transfo)
        discovered = env.state.discovered_transformations[action]
        legal = action_is_legal[action]
        old_display = self.old_display.get(button.get_id(), None)
        old_legal = self.old_legal.get(button.get_id(), None)

        button_image = self.buttons_base_image.get(button.get_id(), None)
        display_content = show_content(self.content_display_mode, discovered)
        self.old_display[button.get_id()] = display_content
        self.old_legal[button.get_id()] = legal

        if old_display != display_content or legal != old_legal:
            if display_content:
                if button_image:
                    if not legal:
                        button_image = button_image.convert("LA").convert("RGBA")
                    self._update_button_image(button, button_image)
                else:
                    button.set_title(str(transfo))
            else:
                if button_image:
                    hidden_image = self.buttons_hidden_image[button.get_id()]
                    self._update_button_image(button, hidden_image)
                else:
                    button.set_title(str(action))

        if show_button(self.display_mode, legal, discovered):
            button.show()
        else:
            button.hide()

    @staticmethod
    def _add_button_image(button: "Button", image: "Image") -> str:
        decorator = button.get_decorator()
        menu_image = _to_menu_image(image, 0.4)
        baseimage_id = decorator.add_baseimage(0, 0, menu_image, centered=True)
        img_width, img_height = menu_image.get_size()
        width_padding = (img_width - button.get_width(apply_padding=False)) // 2
        height_padding = (img_height - button.get_height(apply_padding=False)) // 2
        button.set_padding((height_padding, width_padding))
        button.set_margin(16, 16)
        return baseimage_id

    @staticmethod
    def _update_button_image(button: "Button", image: "Image") -> str:
        menu_image = _to_menu_image(image, 0.4)
        decorator = button.get_decorator()
        decorator.remove_all()
        return decorator.add_baseimage(0, 0, menu_image, centered=True)


class PostitionWidget(Menu):
    def __init__(
        self,
        title: str,
        height: int,
        width: int,
        position,
        zones: List[Zone],
        resources_path: str,
        display_mode: DisplayMode,
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
                background_color=(255, 255, 255, 0),
                selection_color=(255, 255, 255, 0),
                widget_font_color=(255, 255, 255),
                title=False,
                border_width=0,
                widget_border_width=0,
                scrollbar_slider_pad=0,
                scrollarea_outer_margin=(0, 0),
                scrollbar_thick=8,
            ),
        )

        self.shape = (width, height)
        self.zones = zones
        self.base_images = _load_base_images(zones, resources_path)
        self.resources_path = resources_path
        self.display_mode = DisplayMode(display_mode)
        self.button_id_to_zone = {}
        self.old_quantity = {}
        for zone in self.zones:
            self._build_button(zone)

    def update_position(
        self, position: np.ndarray, discovered: np.ndarray, events
    ) -> bool:
        buttons = [
            widget for widget in self.get_widgets() if isinstance(widget, Button)
        ]
        for button in buttons:
            zone = self.button_id_to_zone[button.get_id()]
            zone_slot = self.zones.index(zone)
            if show_button(
                self.display_mode, position[zone_slot], discovered[zone_slot]
            ):
                button.show()
            else:
                button.hide()
        return super().update(events)

    def _build_button(self, zone: Zone) -> None:
        image = self.base_images[zone]
        font = _font_path(self.resources_path)
        button: "Button" = self.add.button("", border_width=0)
        if image is not None:
            decorator = button.get_decorator()
            menu_image = _to_menu_image(image, _get_scale_ratio(image.size, self.shape))
            decorator.add_baseimage(0, 0, menu_image, centered=True)
            img_width, img_height = menu_image.get_size()
            width_padding = img_width - button.get_width(apply_padding=False)
            height_padding = img_height - button.get_height(apply_padding=False)
            button.set_padding((0, width_padding, height_padding, 0))
        else:
            button.set_title(zone.name.capitalize())
            button.set_font(
                font,
                font_size=48,
                color="white",
                selected_color="white",
                readonly_color="white",
                readonly_selected_color="white",
                background_color=None,
                antialias=False,
            )
        button.is_selectable = False
        self.button_id_to_zone[button.get_id()] = zone


def show_button(display_mode: DisplayMode, is_current: bool, discovered: bool) -> bool:
    """Whether to show the button depending on its display mode and current state."""
    _show_button = True
    if display_mode is DisplayMode.CURRENT:
        _show_button = is_current
    elif display_mode is DisplayMode.DISCOVERED:
        _show_button = discovered or is_current
    return _show_button


def show_content(content_mode: ContentMode, discovered: bool) -> bool:
    """Whether to show the button content depending on its content mode and current state."""
    display_content = True
    if content_mode is ContentMode.NEVER:
        display_content = False
    elif content_mode is ContentMode.DISCOVERED:
        display_content = discovered
    return display_content
