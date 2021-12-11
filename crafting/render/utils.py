# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Utilitaries functions for rendering of the Crafting environments """

from typing import TYPE_CHECKING, Optional, Tuple, Union

import os
import numpy as np

import pygame
from pygame.surface import Surface

from PIL import Image, ImageFont, ImageDraw

from crafting.world.zones import Zone
from crafting.world.items import Item, Tool
from crafting.world.recipes import Recipe

if TYPE_CHECKING:
    from crafting.world.world import World


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


def create_image(
    world: "World",
    obj: Union[Item, Zone, Recipe, str],
    with_text: bool = False,
):
    """Create a PIL image for and obj in a world.

    Args:
        world: A crafting World.
        obj: A crafting Item, Zone, Recipe or property.
        with_text: If True, draw an alternative text on the image center.

    Returns:
        A PIL image corresponding to the given object.

    """

    def _get_text_color(obj: Union[Item, Zone, Recipe, str]):
        if isinstance(obj, Item):
            alt_txt = str(obj.item_id)
            if isinstance(obj, Tool):
                color = (0, 255, 255, 255)
            elif obj in world.foundable_items:
                color = (0, 125, 0, 255)
            else:
                color = (0, 0, 255, 255)
        elif isinstance(obj, Zone):
            alt_txt = str(obj)
            color = None
        elif isinstance(obj, str):
            alt_txt = obj
            color = None
        elif isinstance(obj, Recipe):
            if obj.outputs is not None:
                return _get_text_color(obj.outputs)
            if len(obj.added_properties) > 0:
                prop, _ = obj.added_properties.popitem()
                return _get_text_color(prop)
        return alt_txt, color

    if isinstance(obj, Zone):
        image_size = (699, 394)
    else:
        image_size = (120, 120)

    image = Image.new("RGBA", image_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    cx, cy = image_size[0] // 2, image_size[1] // 2
    bbox = [0, 0, image_size[0], image_size[1]]
    alt_txt, color = _get_text_color(obj)

    if color is not None:
        draw.rectangle(bbox, outline=color, width=5)

    if with_text:
        text_pt_size = int(0.60 * image_size[1])
        font = ImageFont.truetype(world.font_path, size=text_pt_size)
        draw.text((cx, cy), alt_txt, fill=(0, 0, 0), font=font, anchor="mm")
    return image


def load_image(
    world: "World",
    obj: Union[Item, Zone, Recipe, str],
    text: Optional[str] = None,
    text_relative_size: float = 0.3,
):
    """Load a PIL image for and obj in a world.

    Args:
        world: A crafting World.
        obj: A crafting Item, Zone, Recipe or property.
        text (Optional): Text to draw on top of the image.
        text_relative_size: If a text is given,
            this is the relative size of the text compared to the image size.

    Returns:
        A PIL image corresponding to the given object.

    """
    if obj is None:
        return None

    if isinstance(obj, Item):
        image_path = os.path.join(world.resources_path, "items", f"{obj.item_id}.png")
    elif isinstance(obj, Zone):
        image_path = os.path.join(world.resources_path, "zones", f"{obj.zone_id}.png")
    elif isinstance(obj, str):
        image_path = os.path.join(world.resources_path, "properties", f"{obj}.png")
    elif isinstance(obj, Recipe):
        if obj.outputs is not None:
            return load_image(world, obj.outputs[0], text, text_relative_size)
        if len(obj.added_properties) > 0:
            prop, _ = obj.added_properties.popitem()
            return load_image(world, prop, text, text_relative_size)
        raise ValueError(f"Recipe {obj} has no output nor added_properties.")
    else:
        raise TypeError(f"Unkowned type {type(obj)}")

    try:
        image = Image.open(image_path).convert("RGBA")
    except FileNotFoundError:
        image = create_image(world, obj, with_text=text is None)

    if text is not None:
        image_draw = ImageDraw.Draw(image)
        image_shape = np.array(image).shape

        text_px_size = int(3 * text_relative_size * min(image_shape[:1]))
        text_pt_size = int(0.75 * text_px_size)
        font = ImageFont.truetype(world.font_path, size=text_pt_size)
        font_offset = (int(0.05 * image_shape[0]), int(0.95 * image_shape[1]))
        image_draw.text(font_offset, text, font=font, anchor="lb")
    return image


def scale(
    image: Surface,
    canevas_shape: Tuple[int],
    size_ratio: float,
    relative_to: str = "width",
) -> Surface:
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
