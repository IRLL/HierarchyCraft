# # Crafting a meta-environment to simultate inventory managment
# # Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>

# """ Widgets for rendering of the Crafting environments """

# import os
# from typing import TYPE_CHECKING, List, Tuple
# from pathlib import Path

# import numpy as np

# try:
#     from pygame.image import load as load_pygame_image
#     from pygame.font import Font
# except ImportError:
#     pass

# from crafting.render.utils import load_or_create_image, pilImageToSurface, scale

# if TYPE_CHECKING:
#     from pygame.surface import Surface

#     from crafting.env import CraftingEnv
#     from crafting.world import World, Zone


# class EnvWidget:

#     """Display widget base class for any crafting environment."""

#     def update(self, env: "CraftingEnv"):
#         """Update the widget given the environment state."""
#         raise NotImplementedError

#     def draw(self, surface: "Surface"):
#         """Draw the widget on a given surface."""
#         raise NotImplementedError


# class InventoryWidget(EnvWidget):

#     """Displays the player's inventory."""

#     def __init__(
#         self,
#         env: "CraftingEnv",
#         position: Tuple[int],
#         window_shape: Tuple[int],
#     ):
#         self.env = env
#         self.background = self._load_background(window_shape)
#         self.shape = self.background.get_size()
#         self.position = np.array(position)
#         self.font = Font(self.env.font_path, int(0.1 * self.shape[1]))

#         self.item_images_per_id = {
#             item_id: self._load_image(item_id) for item_id in self.inventory.items_ids
#         }

#     def _load_background(self, window_shape) -> "Surface":
#         background_path = os.path.join(self.env.resources_path, "inventory.png")
#         background_image = load_pygame_image(background_path)
#         return scale(background_image, window_shape, 0.65)

#     def _load_image(self, item_id) -> "Surface":
#         image = load_or_create_image(
#             self.env.font_path,
#             self.env.ressources_path,
#             self.env.world.items[item_id],
#         )
#         image = pilImageToSurface(image)
#         return scale(image, self.shape, 0.09)

#     @property
#     def inventory(self) -> np.ndarray:
#         return self.env.player_inventory

#     def draw(self, surface: "Surface"):
#         surface.blit(self.background, self.position)

#         non_empty_items = self.inventory.content != 0

#         items_in_inv = np.array(self.inventory.items)[non_empty_items]
#         content = self.inventory.content[non_empty_items]

#         offset = np.array([int(0.029 * self.shape[0]), int(0.155 * self.shape[1])])
#         x_step = y_step = int(0.108 * self.shape[0])
#         font_offset = np.array([int(0.85 * x_step), int(0.9 * y_step)])

#         content_position = self.position + offset
#         for i, (item, quantity) in enumerate(zip(items_in_inv, content)):
#             x_offset = (i % 9) * x_step
#             y_last_offset = int(0.22 * y_step) if i // 9 > 2 else 0
#             y_offset = (i // 9) * y_step + y_last_offset
#             item_position = content_position + np.array([x_offset, y_offset])
#             surface.blit(self.item_images_per_id[item.item_id], item_position)
#             if quantity > 1:
#                 text_position = item_position + font_offset
#                 text = self.font.render(str(quantity), False, "white")
#                 text_rect = text.get_rect()
#                 text_rect.right = text_position[0]
#                 text_rect.bottom = text_position[1]
#                 surface.blit(text, text_rect)


# class ZoneWidget(EnvWidget):

#     """Displays the current player zone and its active properties."""

#     def __init__(
#         self,
#         zones: List["Zone"],
#         properties: List[str],
#         world: "World",
#         position: Tuple[int],
#         window_shape: Tuple[int],
#     ):
#         self.zone = zones[0]
#         self.position = np.array(position)
#         self.world = world

#         self.zones_images = {
#             zone.zone_id: self._load_zone_image(zone.zone_id, window_shape)
#             for zone in zones
#         }

#         self.shape = self.zones_images[0].get_size()

#         self.properties_images = {
#             prop: self._load_property_image(prop) for prop in properties
#         }

#         self.font = Font(world.font_path, int(0.3 * self.shape[1]))

#     def _load_zone_image(self, zone_id, window_shape):
#         image = load_or_create_image(self.world, self.world.zone_from_id[zone_id])
#         image = pilImageToSurface(image)
#         return scale(image, window_shape, 0.25)

#     def _load_property_image(self, prop: str):
#         image = load_or_create_image(self.world, prop)
#         image = pilImageToSurface(image)
#         return scale(image, self.shape, 0.2)

#     def update(self, env: "CraftingEnv"):
#         self.zone = env.player.zone

#     def draw(self, surface: "Surface"):
#         zone_image = self.zones_images[self.zone.zone_id]
#         surface.blit(zone_image, self.position)

#         zone_name_img = self.font.render(self.zone.name.capitalize(), False, "white")
#         font_shift = np.array([int(0.05 * self.shape[0]), 0])
#         surface.blit(zone_name_img, self.position + font_shift)

#         prop_shift = np.array([int(0.02 * self.shape[0]), int(0.90 * self.shape[1])])
#         x_step = int(0.22 * self.shape[0])

#         n_active_props = 0
#         for prop, prop_is_true in self.zone.properties.items():
#             if prop_is_true:
#                 prop_image = self.properties_images[prop]
#                 _, prop_img_height = prop_image.get_size()
#                 shift = np.array([n_active_props * x_step, -prop_img_height])
#                 prop_position = self.position + prop_shift + shift
#                 surface.blit(prop_image, prop_position)
#                 n_active_props += 1


# class ScoreWidget(EnvWidget):

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


# class StepLeftWidget(EnvWidget):

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
