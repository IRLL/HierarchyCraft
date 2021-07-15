# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Rendering of the MineCrafting environment """

import os
from typing import List, Tuple
import numpy as np

import pygame
from pygame.surface import Surface
import pygame_menu

from crafting.env import CraftingEnv
from crafting.world.world import World
from crafting.world.zones import Zone
from crafting.player.inventory import Inventory

from pygame.event import Event


def load_and_scale(
    path: str,
    canevas_shape: Tuple[int],
    size_ratio: float,
    relative_to: str='width'
    ) -> Surface:
    """ Load and rescales an image using pygame.

    Load and rescales an image relatively to canevas_shape preserving aspect ratio.

    Args:
        path: Path to the image file.
        canevas_shape: Shape of the canevas where the image will be blited.
        size_ratio: Size (in percent) of the loaded image compared to canevas shape.
        relative_to: One of ('width', 'height'), dimention to consider for size_ratio.

    """
    image = pygame.image.load(path).convert_alpha()
    image_shape = image.get_size()

    if relative_to.startswith('w'):
        scale_ratio = int(size_ratio * canevas_shape[0]) / image_shape[0]
    elif relative_to.startswith('h'):
        scale_ratio = int(size_ratio * canevas_shape[1]) / image_shape[1]
    else:
        raise ValueError(f"Unknowed value for 'relative_to': {relative_to}")

    new_shape = (int(image_shape[0] * scale_ratio), int(image_shape[1] * scale_ratio))
    return pygame.transform.scale(image, new_shape)


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


def make_menus(world: World, window_shape: tuple):

    def on_button_click(action_type, identification):
        return action_type, identification
    
    resources_path = world.resources_path
    id_to_action = {}

    # Item Menu
    items_menu_height = int(0.75 * window_shape[1])
    items_menu_width = int(0.15 * window_shape[0])

    items_menu = pygame_menu.Menu(
        title='Search',
        height=items_menu_height,
        width=items_menu_width,
        position=(0, 0),
        theme=pygame_menu.themes.THEME_BLUE,
    )

    items_images_path = os.path.join(resources_path, 'items')
    for item in world.searchable_items:
        image_path = os.path.join(items_images_path, f"{item.item_id}.png")
        image = pygame_menu.baseimage.BaseImage(image_path).scale(0.5, 0.5)

        button = items_menu.add.button(
            ' '*8,
            on_button_click,
            'get',
            item.item_id,
            padding=(12, 0, 12, 0)
        )

        decorator = button.get_decorator()
        decorator.add_baseimage(0, 0, image, centered=True)
        id_to_action[button.get_id()] = ('get', item.item_id)

    # Recipes Menu
    recipes_menu_height = window_shape[1] - items_menu_height
    recipes_menu_width = window_shape[0]

    recipes_menu = pygame_menu.Menu(
        title='Craft',
        height=recipes_menu_height,
        width=recipes_menu_width,
        rows=1,
        columns=world.n_recipes,
        position=(0, 100),
        column_max_width=int(0.08 * window_shape[0]),
        theme=pygame_menu.themes.THEME_ORANGE
    )

    recipes_images_path = os.path.join(resources_path, 'items')
    for recipe in world.recipes:
        image_path = os.path.join(recipes_images_path, f"{recipe.recipe_id}.png")
        image = pygame_menu.baseimage.BaseImage(image_path).scale(0.5, 0.5)

        button = recipes_menu.add.button(
            ' '*8,
            on_button_click,
            'craft',
            recipe.recipe_id,
            padding=(16, 0, 16, 0)
        )

        decorator = button.get_decorator()
        decorator.add_baseimage(0, 0, image, centered=True)
        id_to_action[button.get_id()] = ('craft', recipe.recipe_id)

    # Zones Menu
    zones_menu_height = items_menu_height
    zones_menu_width = int(0.20 * window_shape[0])

    zones_menu = pygame_menu.Menu(
        title='Move',
        height=zones_menu_height,
        width=zones_menu_width,
        position=(100, 0),
        theme=pygame_menu.themes.THEME_GREEN,
    )

    zones_images_path = os.path.join(resources_path, 'zones')
    for zone in world.zones:
        image_path = os.path.join(zones_images_path, f"{zone.zone_id}.png")
        image = pygame_menu.baseimage.BaseImage(image_path).scale(0.2, 0.2)

        button = zones_menu.add.button(
            ' '*19,
            on_button_click,
            'move',
            zone.zone_id,
            padding=(26, 0, 26, 0)
        )

        decorator = button.get_decorator()
        decorator.add_baseimage(0, 0, image, centered=True)
        id_to_action[button.get_id()] = ('move', zone.zone_id)

    return (items_menu, recipes_menu, zones_menu), id_to_action


def create_window(env: CraftingEnv):
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    window_shape = (int(16/9 * 600), 720)

    pygame.init()
    clock = pygame.time.Clock()

    # Create window
    screen = pygame.display.set_mode(window_shape)
    pygame.display.set_caption('MineCrafting')

    # Create menu
    menus, id_to_action = make_menus(env.world, window_shape)

    # Create inventory widget
    position = (int(0.15 * window_shape[0]), int(0.15 * window_shape[0]))
    inv_widget = InventoryWidget(
        env.player.inventory,
        env.world.resources_path,
        position,
        window_shape
    )

    # Create zone widget
    position = (int(0.52 * window_shape[0]), int(0.02 * window_shape[0]))
    zone_widget = ZoneWidget(
        env.world.zones,
        env.world.zone_properties,
        env.world.resources_path,
        position,
        window_shape
    )

    position = (int(0.17 * window_shape[0]), int(0.01 * window_shape[0]))
    font_size = int(0.06 * window_shape[0])
    score_widget = ScoreWidget(
        env.world.resources_path,
        position,
        font_size,
    )

    return {
        'clock': clock,
        'screen': screen,
        'menus': menus,
        'inv_widget': inv_widget,
        'zone_widget': zone_widget,
        'score_widget': score_widget,
        'id_to_action': id_to_action
    }

def update_rendering(env: CraftingEnv, clock, screen, menus, inv_widget, zone_widget,
    score_widget, id_to_action, additional_events:List[Event]=None, fps:float=60):
    # Tick
    clock.tick(fps)

    # Paint background
    screen.fill((198, 198, 198))

    # Execute main from principal menu if is enabled
    events = pygame.event.get()
    if additional_events is not None:
        events += additional_events
    for event in events:
        if event.type == pygame.QUIT:
            exit()

    inv_widget.update(env.player.inventory)
    inv_widget.draw(screen)

    zone_widget.update(env.player.zone)
    zone_widget.draw(screen)

    score_widget.update(env.player.score)
    score_widget.draw(screen)

    action = None
    action_is_legal = env.get_action_is_legal()
    for menu in menus:
        buttons = [
            widget for widget in menu.get_widgets()
            if isinstance(widget, pygame_menu.widgets.Button)
        ]
        for button in buttons:
            action_id = env.action(*id_to_action[button.get_id()])
            if action_is_legal[action_id]:
                button.show()
            else:
                button.hide()

        menu.update(events)
        menu.draw(screen)

        selected_widget = menu.get_selected_widget()
        if selected_widget is not None and selected_widget.update(events):
            action = selected_widget.apply()

    # Update surface
    pygame.display.update()
    return action

def get_human_action(env, additional_events=None, can_be_none=False, **kwargs):
    action_chosen = False
    while not action_chosen:
        action = update_rendering(env, additional_events=additional_events, **kwargs)
        action_chosen = action is not None or can_be_none
    return action


if __name__ == '__main__':
    from crafting.examples.minecraft.items import ENCHANTING_TABLE
    from crafting.examples import MineCraftingEnv

    env = MineCraftingEnv(verbose=1, max_step=100,
        tasks=['obtain_enchanting_table'], tasks_can_end=[True]
    )

    import matplotlib.pyplot as plt
    # fig, ax = plt.subplots()
    # env.world.draw_requirements_graph(ax)
    # plt.show()

    ALL_GET_OPTIONS = env.world.get_all_options()

    enchant_table_option = ALL_GET_OPTIONS[f"Get {ENCHANTING_TABLE}"]
    # print(enchant_table_option)

    for _ in range(2):
        observation = env.reset()
        done = False
        total_reward = 0
        while not done:
            rgb_array = env.render(mode='rgb_array')

            enchant_action_id, _ = enchant_table_option(observation)
            print(f'For Enchanting Table: {env.action_from_id(enchant_action_id)}')

            # additional_events = [
            #     Event(MOUSEBUTTONDOWN, pos=(75, 331), button=1, window=None),
            #     Event(MOUSEBUTTONUP, pos=(75, 331), button=1, window=None)
            # ]
            action = get_human_action(env,
                # additional_events=additional_events,
                **env.render_variables
            )
            action_id = env.action(*action)
            print(f'Human did: {env.action_from_id(action_id)}')

            observation, reward, done, infos = env(action_id)
            total_reward += reward

        print("SCORE: ", total_reward)
