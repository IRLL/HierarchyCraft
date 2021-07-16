from typing import List, Tuple

import os
import numpy as np

import pygame
from pygame.surface import Surface

from crafting.player.inventory import Inventory
from crafting.world.zones import Zone
from crafting.render.utils import load_and_scale


class InventoryWidget():

    def __init__(self,
        inventory: Inventory,
        resources_path:str,
        position: Tuple[int],
        window_shape: Tuple[int]
    ):
        self.inventory = inventory
        self.resources_path = resources_path

        self.background = self._load_background(window_shape)
        self.shape = self.background.get_size()
        self.position = np.array(position)

        font_path = os.path.join(self.resources_path, 'minecraft_font.ttf')
        self.font = pygame.font.Font(font_path, int(0.1 * self.shape[1]))

        self.item_images_per_id = {
           item_id: self._load_image(item_id)
           for item_id in self.inventory.items_ids
           if item_id != 0
        }

    def _load_background(self, window_shape):
        background_path = os.path.join(self.resources_path, 'inventory.png')
        return load_and_scale(background_path, window_shape, 0.65)

    def _load_image(self, item_id):
        image_path = os.path.join(self.resources_path, 'items', f'{item_id}.png')
        return load_and_scale(image_path, self.shape, 0.09)

    def update(self, inventory: Inventory=None):
        self.inventory = inventory

    def draw(self, surface: Surface):
        surface.blit(self.background, self.position)

        non_empty_items = np.logical_and(
            self.inventory.content != 0,
            np.not_equal(self.inventory.items_ids, 0)
        )

        items_in_inv = np.array(self.inventory.items)[non_empty_items]
        content = self.inventory.content[non_empty_items]

        offset = np.array([int(0.029 * self.shape[0]), int(0.155* self.shape[1])])
        x_step = y_step = int(0.108 * self.shape[0])
        font_offset = np.array([int(0.85 * x_step), int(0.9 * y_step)])

        content_position = self.position + offset
        for i, (item, quantity) in enumerate(zip(items_in_inv, content)):
            x_offset = (i % 9) * x_step
            y_last_offset = int(0.22 * y_step) if i // 9 > 2 else 0
            y_offset = (i // 9) * y_step + y_last_offset
            item_position = content_position + np.array([x_offset, y_offset])
            surface.blit(self.item_images_per_id[item.item_id], item_position)
            if quantity > 1:
                text_position = item_position + font_offset
                text = self.font.render(str(quantity), False, 'white')
                text_rect = text.get_rect()
                text_rect.right = text_position[0]
                text_rect.bottom = text_position[1]
                surface.blit(text, text_rect)


class ZoneWidget():

    def __init__(self,
            zones: List[Zone],
            properties: List[str],
            resources_path: str,
            position: Tuple[int],
            window_shape: Tuple[int]
        ):
        self.zone = zones[0]
        self.position = np.array(position)
        self.resources_path = resources_path

        self.zones_images = {
            zone.zone_id: self._load_zone_image(zone.zone_id, window_shape)
            for zone in zones
        }

        self.shape = self.zones_images[0].get_size()

        self.properties_images = {
            prop: self._load_property_image(prop)
            for prop in properties
        }

        font_path = os.path.join(self.resources_path, 'minecraft_font.ttf')
        self.font = pygame.font.Font(font_path, int(0.3 * self.shape[1]))

    def _load_zone_image(self, zone_id, window_shape):
        image_path = os.path.join(self.resources_path, 'zones', f'{zone_id}.png')
        return load_and_scale(image_path, window_shape, 0.25)

    def _load_property_image(self, prop: str):
        if prop == "has_crafting":
            prop_id = 58
        elif prop == "has_furnace":
            prop_id = 61
        else:
            raise ValueError(f'Unknowed property :{prop}')
        image_path = os.path.join(self.resources_path, 'items', f'{prop_id}.png')
        return load_and_scale(image_path, self.shape, 0.2)

    def update(self, zone: Zone):
        self.zone = zone

    def draw(self, surface):
        zone_image = self.zones_images[self.zone.zone_id]
        surface.blit(zone_image, self.position)

        zone_name_img = self.font.render(self.zone.name.capitalize(), False, 'white')
        font_shift = np.array([int(0.05 * self.shape[0]), 0])
        surface.blit(zone_name_img, self.position + font_shift)

        prop_shift = np.array([int(0.05 * self.shape[0]), int(0.6 * self.shape[1])])
        x_step = int(0.22 * self.shape[0])

        n_active_props = 0
        for prop, prop_is_true in self.zone.properties.items():
            if prop_is_true:
                prop_image = self.properties_images[prop]
                shift = np.array([n_active_props * x_step, 0])
                prop_position = self.position + prop_shift + shift
                surface.blit(prop_image, prop_position)
                n_active_props += 1


class ScoreWidget():

    def __init__(self,
            resources_path: str,
            position: Tuple[int],
            font_size: int
        ):
        self.position = position
        font_path = os.path.join(resources_path, 'minecraft_font.ttf')
        self.font = pygame.font.Font(font_path, font_size)
        self.reward = 0
        self.score = 0

    def update(self, score: float):
        self.score = score

    def draw(self, surface):
        score_name_img = self.font.render(f"SCORE {self.score}", False, '#c95149')
        surface.blit(score_name_img, self.position)
