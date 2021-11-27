# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Utilitaries functions for rendering of the Crafting environments """

from __future__ import annotations
from typing import TYPE_CHECKING, Tuple, Union

import os
import numpy as np

from pygame.image import load
from pygame.transform import scale
from pygame.surface import Surface

from PIL import Image, ImageFont, ImageDraw

if TYPE_CHECKING:
    from crafting.world.world import World
from crafting.world.zones import Zone
from crafting.world.items import Item


def load_image(
    world: World,
    obj: Union[Item, Zone, str],
    text: str = None,
    text_relative_size: float = 0.3,
):
    if obj is None:
        return None

    if isinstance(obj, Item):
        image_path = os.path.join(world.resources_path, "items", f"{obj.item_id}.png")
    elif isinstance(obj, Zone):
        image_path = os.path.join(world.resources_path, "zones", f"{obj.zone_id}.png")
    elif isinstance(obj, str):
        image_path = os.path.join(world.resources_path, "properties", f"{obj}.png")
    else:
        raise TypeError(f"Unkowned type {type(obj)}")

    try:
        image = Image.open(image_path).convert("RGBA")
    except FileNotFoundError:
        image = None

    if text is not None and image is not None:
        image_draw = ImageDraw.Draw(image)
        image_shape = np.array(image).shape

        text_px_size = int(3 * text_relative_size * min(image_shape[:1]))
        text_pt_size = int(0.75 * text_px_size)
        font = ImageFont.truetype(world.font_path, size=text_pt_size)
        font_offset = (int(0.05 * image_shape[0]), int(0.95 * image_shape[1]))
        image_draw.text(font_offset, text, font=font, anchor="lb")
    return np.array(image)


def load_and_scale(
    path: str, canevas_shape: Tuple[int], size_ratio: float, relative_to: str = "width"
) -> Surface:
    """Load and rescales an image using pygame.

    Load and rescales an image relatively to canevas_shape preserving aspect ratio.

    Args:
        path: Path to the image file.
        canevas_shape: Shape of the canevas where the image will be blited.
        size_ratio: Size (in percent) of the loaded image compared to canevas shape.
        relative_to: One of ('width', 'height'), dimention to consider for size_ratio.

    """
    image = load(path).convert_alpha()
    image_shape = image.get_size()

    if relative_to.startswith("w"):
        scale_ratio = int(size_ratio * canevas_shape[0]) / image_shape[0]
    elif relative_to.startswith("h"):
        scale_ratio = int(size_ratio * canevas_shape[1]) / image_shape[1]
    else:
        raise ValueError(f"Unknowed value for 'relative_to': {relative_to}")

    new_shape = (int(image_shape[0] * scale_ratio), int(image_shape[1] * scale_ratio))
    return scale(image, new_shape)
