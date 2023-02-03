# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Utilitaries functions for rendering of the Crafting environments """

import os
from io import BytesIO
from typing import TYPE_CHECKING, Optional, Tuple, Union, Dict, List
import logging
from pathlib import Path

import numpy as np

from PIL import Image, ImageDraw, ImageFont


# pygame is an optional dependency
try:
    import pygame
    from pygame_menu.baseimage import BaseImage
except ImportError:
    pass

from crafting.world import Item, Zone, ItemStack
from crafting.transformation import Transformation

if TYPE_CHECKING:
    from pygame.surface import Surface


# Disable PIL logging to avoid spam (see https://github.com/camptocamp/pytest-odoo/issues/15)
logging.getLogger("PIL").setLevel(logging.INFO)


def load_image(resources_path: Path, obj: Union[Item, Zone]) -> Optional[Image.Image]:
    """Load a PIL image for and obj in a world.

    Args:
        resources_path: path to environment resources.
        obj: A crafting Item, Zone, Recipe or property.

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
        return Image.open(image_path).convert("RGBA")
    except FileNotFoundError:
        return None


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
    font_path = os.path.join(resources_path, "font.ttf")
    image = image.copy()
    image_draw = ImageDraw.Draw(image)
    image_shape = np.array(image).shape

    text_px_size = int(3 * text_relative_size * min(image_shape[:1]))
    text_pt_size = int(0.75 * text_px_size)
    font = ImageFont.truetype(font_path, size=text_pt_size)
    font_offset = (int(0.05 * image_shape[0]), int(0.95 * image_shape[1]))
    image_draw.text(font_offset, text, font=font, anchor="lb")
    return image


def _to_menu_image(image: "Image.Image", scaling: float) -> "BaseImage":
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    buffered.seek(0)
    return BaseImage(buffered).scale(scaling, scaling)


def create_text_image(
    text: str, resources_path: str, image_size=(120, 120)
) -> "Image.Image":
    """Create a PIL image for an Item or Zone.

    Args:
        obj: A crafting Item, Zone, Recipe or property.
        resources_path: Path to the resources folder.

    Returns:
        A PIL image corresponding to the given object.

    """

    image = Image.new("RGBA", image_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    cx, cy = image_size[0] // 2, image_size[1] // 2
    text_pt_size = int(0.60 * image_size[1])
    font_path = os.path.join(resources_path, "font.ttf")
    font = ImageFont.truetype(font_path, size=text_pt_size)
    draw.text((cx, cy), text, fill=(200, 200, 200), font=font, anchor="mm")
    return image


def build_transformation_image(
    transformation: Transformation,
    resources_path: str,
    zone_bg_color=(185, 215, 115),
    dest_bg_color=(220, 200, 175),
):
    """Build a transformation image from items and zones images."""
    added_images: List[Image.Image] = []

    if transformation.added_player_items is not None:
        added_images += load_or_create_images(
            transformation.added_player_items, resources_path
        )
    if transformation.added_zone_items is not None:
        added_images += load_or_create_images(
            transformation.added_zone_items,
            resources_path,
            bg_color=zone_bg_color,
        )
    if transformation.added_destination_items is not None:
        added_images += load_or_create_images(
            transformation.added_destination_items,
            resources_path,
            bg_color=dest_bg_color,
        )

    arrow_image = create_text_image("->", resources_path)

    removed_images: List["Image.Image"] = []
    if transformation.removed_player_items is not None:
        removed_images += load_or_create_images(
            transformation.removed_player_items, resources_path
        )
    if transformation.removed_zone_items is not None:
        removed_images += load_or_create_images(
            transformation.removed_zone_items,
            resources_path,
            bg_color=zone_bg_color,
        )
    if transformation.removed_destination_items is not None:
        removed_images += load_or_create_images(
            transformation.removed_destination_items,
            resources_path,
            bg_color=dest_bg_color,
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


def load_or_create_image(
    obj: Union[ItemStack, Zone], resources_path: str, bg_color=None
):
    """Load or create an image for an item or zone."""
    quantity = 0
    if isinstance(obj, ItemStack):
        quantity = obj.quantity
        obj = obj.item
    image = load_image(obj=obj, resources_path=resources_path)
    if image is None:
        image_size = (120, 120)
        if isinstance(obj, Zone):
            image_size = (699, 394)
        image = create_text_image(str(obj), resources_path, image_size=image_size)
    elif quantity > 0:
        image = draw_text_on_image(image, str(quantity), resources_path)
    if bg_color is not None:
        image = _add_background_elipsis(image, bg_color)
    return image


def load_or_create_images(
    objs: List[Union[ItemStack, Zone]], resources_path: str, bg_color=None
) -> List["Image.Image"]:
    """Load or create images for the given objects."""
    return [load_or_create_image(obj, resources_path, bg_color) for obj in objs]


def _add_background_elipsis(
    image: "Image.Image", bg_color: Tuple[int, int, int]
) -> "Image.Image":
    image_bg = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image_bg)
    draw.ellipse((0, 0, image.width, image.height), fill=bg_color)
    image_bg.alpha_composite(image)
    return image_bg


def scale(
    image: "Surface",
    canevas_shape: Tuple[int],
    size_ratio: float,
    relative_to: str = "width",
) -> "Surface":
    """Load and rescales an image using pygame.

    Load and rescales an image relatively to canevas_shape preserving aspect ratio.

    Args:
        path: Path to the image file.
        canevas_shape: Shape of the canevas where the image will be blited.
        size_ratio: Size (in percent) of the loaded image compared to canevas shape.
        relative_to: One of ('width', 'height'), dimention to consider for size_ratio.

    """
    image_shape = image.get_size()

    if relative_to.startswith("w"):
        scale_ratio = int(size_ratio * canevas_shape[0]) / image_shape[0]
    elif relative_to.startswith("h"):
        scale_ratio = int(size_ratio * canevas_shape[1]) / image_shape[1]
    else:
        raise ValueError(f"Unknowed value for 'relative_to': {relative_to}")

    new_shape = (int(image_shape[0] * scale_ratio), int(image_shape[1] * scale_ratio))
    return pygame.transform.scale(image, new_shape)


def surface_to_rgb_array(surface: "Surface") -> np.ndarray:
    """Transforms a pygame surface to a conventional rgb array.

    Args:
        surface: pygame surface.

    Returns:
        A rgb_array representing the given surface.

    """
    return pygame.surfarray.array3d(surface).swapaxes(0, 1)


def pilImageToSurface(pilImage: Image.Image):
    """Convert a PIL Image to a pygame Surface.

    Args:
        pilImage: PIL Image to convert.

    Returns:
        A pygame Surface.

    """
    return pygame.image.fromstring(
        pilImage.tobytes(), pilImage.size, pilImage.mode
    ).convert_alpha()
