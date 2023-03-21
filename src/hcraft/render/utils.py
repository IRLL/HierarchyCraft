""" Utilitaries functions for rendering of the HierarchyCraft environments """

import logging
import os
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional, Tuple, Union

import numpy as np
from PIL import Image, ImageDraw, ImageFont

# pygame is an optional dependency
try:
    import pygame
    from pygame_menu.baseimage import BaseImage
except ImportError:
    pass


from hcraft.elements import Item, Stack, Zone

if TYPE_CHECKING:
    from pygame.surface import Surface

    from hcraft.transformation import Transformation


# Disable PIL logging to avoid spam (see https://github.com/camptocamp/pytest-odoo/issues/15)
logging.getLogger("PIL").setLevel(logging.INFO)


def load_image(resources_path: Path, obj: Union[Item, Zone]) -> Optional[Image.Image]:
    """Load a PIL image for and obj in a world.

    Args:
        resources_path: path to environment resources.
        obj: A HierarchyCraft Item, Zone, Recipe or property.

    Returns:
        A PIL image corresponding to the given object.

    """
    if obj is None:
        return None

    if isinstance(obj, Item):
        image_path = os.path.join(resources_path, "items", f"{obj.name}.png")
    elif isinstance(obj, Zone):
        image_path = os.path.join(resources_path, "zones", f"{obj.name}.png")
    else:
        raise TypeError(f"Unsupported type for loading images: {type(obj)}")

    try:
        image = Image.open(image_path).convert("RGBA")
    except FileNotFoundError:
        return None

    if isinstance(obj, Item):
        wanted_size = (120, 120)
    elif isinstance(obj, Zone):
        wanted_size = (699, 394)

    scale_ratio = _get_scale_ratio(image.size, wanted_size)
    image = image.resize(
        (
            int(scale_ratio * image.size[0]),
            int(scale_ratio * image.size[1]),
        ),
        resample=Image.Resampling.NEAREST,
    )

    return image


def draw_text_on_image(
    image: "Image.Image",
    text: str,
    resources_path: str,
    text_relative_size: float = 0.3,
) -> Optional["BaseImage"]:
    """Draw on top of an image, converting it to Pygame image.

    Args:
        image (Image): image to draw on to of.
        text (Optional): Text to draw on top of the image.
        text_relative_size: If a text is given,
            this is the relative size of the text compared to the image size.

    Returns:
        A BaseImage corresponding with the given text.

    """
    font_path = _font_path(resources_path)
    image = image.copy()
    image_draw = ImageDraw.Draw(image)
    text_px_size = int(3 * text_relative_size * min(image.size))
    text_pt_size = int(0.75 * text_px_size)
    font = ImageFont.truetype(font_path, size=text_pt_size)
    font_offset = (int(0.05 * image.size[0]), int(0.95 * image.size[1]))
    image_draw.text(font_offset, text, font=font, anchor="lb")
    return image


def _to_menu_image(image: "Image.Image", scaling: float) -> "BaseImage":
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)
    return BaseImage(buffered).scale(scaling, scaling)


def create_text_image(
    text: str, resources_path: str, image_size=(None, 120)
) -> "Image.Image":
    """Create a PIL image for an Item or Zone.

    Args:
        obj: A HierarchyCraft Item, Zone, Recipe or property.
        resources_path: Path to the resources folder.

    Returns:
        A PIL image corresponding to the given object.

    """
    if image_size[0] is None:
        image_size = (image_size[1] * len(text) // 4, image_size[1])

    image = Image.new("RGBA", image_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    center_x, center_y = image_size[0] // 2, image_size[1] // 2
    font_path = _font_path(resources_path)
    text_pt_size = min(
        int(0.60 * image_size[1]), int(4 * 0.60 * image_size[0] / len(text))
    )
    font = ImageFont.truetype(font_path, size=text_pt_size)
    draw.text((center_x, center_y), text, fill=(200, 200, 200), font=font, anchor="mm")
    return image


def build_transformation_image(
    transformation: "Transformation",
    resources_path: str,
    zone_bg_color=(185, 215, 115),
    dest_bg_color=(220, 200, 175),
):
    """Build a transformation image from items and zones images."""
    added_images: List[Image.Image] = []

    added_player_items = transformation.get_changes("player", "add")
    if added_player_items is not None:
        added_images += load_or_create_images(added_player_items, resources_path)
    added_zone_items = transformation.get_changes("current_zone", "add")
    if added_zone_items is not None:
        added_images += load_or_create_images(
            added_zone_items, resources_path, bg_color=zone_bg_color
        )
    added_destination_items = transformation.get_changes("destination", "add")
    if added_destination_items is not None:
        added_images += load_or_create_images(
            added_destination_items, resources_path, bg_color=dest_bg_color
        )
    added_zones_items = transformation.get_changes("zones", "add")
    if added_zones_items is not None:
        for _zone, zones_items in added_zones_items.items():
            added_images += load_or_create_images(
                zones_items, resources_path, bg_color=dest_bg_color
            )

    arrow_image = create_text_image("->", resources_path)

    removed_images: List["Image.Image"] = []
    removed_player_items = transformation.get_changes("player", "remove")
    if removed_player_items is not None:
        removed_images += load_or_create_images(removed_player_items, resources_path)
    removed_zone_items = transformation.get_changes("current_zone", "remove")
    if removed_zone_items is not None:
        removed_images += load_or_create_images(
            removed_zone_items, resources_path, bg_color=zone_bg_color
        )
    removed_destination_items = transformation.get_changes("destination", "remove")
    if removed_destination_items is not None:
        removed_images += load_or_create_images(
            removed_destination_items,
            resources_path,
            bg_color=dest_bg_color,
        )

    removed_zones_items = transformation.get_changes("zones", "remove")
    if removed_zones_items is not None:
        for _zone, zones_items in removed_zones_items.items():
            added_images += load_or_create_images(
                zones_items, resources_path, bg_color=dest_bg_color
            )

    destination_images = []
    if transformation.destination is not None:
        destination_images = load_or_create_images(
            [transformation.destination], resources_path
        )
        for zone_image in destination_images:
            zone_image.thumbnail((214, 120), Image.LANCZOS)

    items_images = removed_images + [arrow_image] + added_images + destination_images
    total_width = sum(i.width for i in items_images)
    height = max(i.height for i in items_images)
    transformation_image = Image.new("RGBA", (total_width, height))
    x_offset = 0
    for i, image in enumerate(items_images):
        transformation_image.paste(image, (x_offset, (height - image.height) // 2))
        x_offset += image.width

    return transformation_image


def load_or_create_image(obj: Union[Stack, Zone], resources_path: str, bg_color=None):
    """Load or create an image for an item or zone."""

    if isinstance(obj, Stack):
        obj_name = str(obj)
        quantity = obj.quantity
        obj = obj.item
    else:
        obj_name = obj.name
        quantity = 0

    image = load_image(obj=obj, resources_path=resources_path)
    if image is None:
        image_size = (None, 120)
        if isinstance(obj, Zone):
            image_size = (699, 394)
        image = create_text_image(obj_name, resources_path, image_size=image_size)
    elif quantity > 1:
        image = draw_text_on_image(image, str(quantity), resources_path)
    if bg_color is not None:
        image = _add_background_elipsis(image, bg_color)

    return image


def load_or_create_images(
    objs: List[Union[Stack, Zone]], resources_path: str, bg_color=None
) -> List["Image.Image"]:
    """Load or create images for the given objects."""
    return [load_or_create_image(obj, resources_path, bg_color) for obj in objs]


def _add_background_elipsis(
    image: "Image.Image", bg_color: Tuple[int, int, int]
) -> "Image.Image":
    image_bg = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image_bg)
    draw.ellipse((0, 0, image.width, image.height), fill=(*bg_color, 25))
    image_bg.alpha_composite(image)
    return image_bg


def surface_to_rgb_array(surface: "Surface") -> np.ndarray:
    """Transforms a pygame surface to a conventional rgb array.

    Args:
        surface: pygame surface.

    Returns:
        A rgb_array representing the given surface.

    """
    return pygame.surfarray.array3d(surface).swapaxes(0, 1)


def _font_path(resources_path: str):
    from hcraft.world import _default_resources_path

    font_path = os.path.join(resources_path, "font.ttf")
    if not os.path.exists(font_path):
        font_path = os.path.join(_default_resources_path(), "font.ttf")
    return font_path


def _get_scale_ratio(initial_shape, wanted_shape) -> float:
    if wanted_shape[0] == initial_shape[0] or wanted_shape[1] == initial_shape[1]:
        return 1
    if wanted_shape[0] > initial_shape[0]:
        if wanted_shape[1] > initial_shape[1]:
            return min(
                1 + (wanted_shape[0] - initial_shape[0]) / initial_shape[0],
                1 + (wanted_shape[1] - initial_shape[1]) / initial_shape[1],
            )
    if wanted_shape[0] < initial_shape[0]:
        if wanted_shape[1] < initial_shape[1]:
            return max(
                1 - (wanted_shape[0] - initial_shape[0]) / initial_shape[0],
                1 - (wanted_shape[1] - initial_shape[1]) / initial_shape[1],
            )
    raise NotImplementedError(f"Scaling {initial_shape} -> {wanted_shape}")
