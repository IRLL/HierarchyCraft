# Crafting a meta-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Utilitaries functions for rendering of the Crafting environments """

import os
from typing import TYPE_CHECKING, Optional, Tuple, Union
import logging
from pathlib import Path

import numpy as np

from PIL import Image, ImageDraw, ImageFont


# pygame is an optional dependency
try:
    import pygame
except ImportError:
    pass

from crafting.world import Item, Zone
from crafting.transformation import Transformation

if TYPE_CHECKING:
    from pygame.surface import Surface


# Disable PIL logging to avoid spam (see https://github.com/camptocamp/pytest-odoo/issues/15)
logging.getLogger("PIL").setLevel(logging.INFO)


def create_image(font_path: Path, obj: Union[Item, Zone, Transformation]):
    """Create a PIL image for and obj in a world.

    Args:
        world: A crafting World.
        obj: A crafting Item, Zone, Recipe or property.

    Returns:
        A PIL image corresponding to the given object.

    """

    if isinstance(obj, Zone):
        image_size = (699, 394)
    else:
        image_size = (120, 120)

    image = Image.new("RGBA", image_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    cx, cy = image_size[0] // 2, image_size[1] // 2
    bbox = [0, 0, image_size[0], image_size[1]]
    alt_txt = str(obj)
    color = (0, 0, 255, 255)
    draw.rectangle(bbox, outline=color, width=5)

    text_pt_size = int(0.60 * image_size[1])
    font = ImageFont.truetype(font_path, size=text_pt_size)
    draw.text((cx, cy), alt_txt, fill=(0, 0, 0), font=font, anchor="mm")
    return image


def load_image(resources_path: Path, obj: Union[Item, Zone, Transformation]):
    """Load a PIL image for and obj in a world.

    Args:
        world: A crafting World.
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
    elif isinstance(obj, Transformation):
        return None
    else:
        raise TypeError(f"Unsupported type for loading images: {type(obj)}")

    return Image.open(image_path).convert("RGBA")


def load_or_create_image(
    font_path: Path,
    ressources_path: Path,
    obj: Union[Item, Zone, Transformation],
    text: Optional[str] = None,
    text_relative_size: float = 0.3,
):
    """Load or create a PIL image for and obj in a world.

    Args:
        world: A crafting World.
        obj: A crafting Item, Zone, Recipe or property.
        text (Optional): Text to draw on top of the image.
        text_relative_size: If a text is given,
            this is the relative size of the text compared to the image size.

    Returns:
        A PIL image corresponding to the given object.

    """
    try:
        image = load_image(ressources_path, obj)
    except FileNotFoundError:
        image = create_image(font_path, obj)

    if text is not None:
        image_draw = ImageDraw.Draw(image)
        image_shape = np.array(image).shape

        text_px_size = int(3 * text_relative_size * min(image_shape[:1]))
        text_pt_size = int(0.75 * text_px_size)
        font = ImageFont.truetype(font_path, size=text_pt_size)
        font_offset = (int(0.05 * image_shape[0]), int(0.95 * image_shape[1]))
        image_draw.text(font_offset, text, font=font, anchor="lb")
    return image


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
