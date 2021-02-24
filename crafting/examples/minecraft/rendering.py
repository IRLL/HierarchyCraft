# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

"""

"""

import os

import pygame
import pygame_menu

from crafting.examples.minecraft.items import MC_FOUDABLE_ITEMS
from crafting.examples.minecraft.recipes import MC_RECIPES
from crafting.examples.minecraft.zones import MC_ZONES


def on_button_click(action_type, identification):
    return action_type, identification

def make_menus(window_width: int, window_height: int):
    # Menus sizes
    recipes_menu_height = int(0.25 * window_height)
    recipes_menu_width = window_width

    items_menu_height = window_height - recipes_menu_height
    items_menu_width = int(0.15 * window_width)

    zones_menu_height = items_menu_height
    zones_menu_width = int(0.20 * window_width)

    # Item Menu
    items_menu = pygame_menu.Menu(
        title='Search',
        height=items_menu_height,
        width=items_menu_width,
        menu_position=(0, 0),
        theme=pygame_menu.themes.THEME_BLUE,
    )

    items_images_path = os.path.join('crafting', 'examples', 'minecraft', 'images', 'items')
    for item in MC_FOUDABLE_ITEMS:
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

    # Recipes Menu

    recipes_menu = pygame_menu.Menu(
        title='Craft',
        height=recipes_menu_height,
        width=recipes_menu_width,
        rows=1,
        columns=len(MC_RECIPES),
        menu_position=(0, 100),
        theme=pygame_menu.themes.THEME_ORANGE,
    )

    recipes_images_path = os.path.join('crafting', 'examples', 'minecraft', 'images', 'items')
    for recipe in MC_RECIPES:
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


    zones_menu = pygame_menu.Menu(
        title='Move',
        height=zones_menu_height,
        width=zones_menu_width,
        menu_position=(100, 0),
        theme=pygame_menu.themes.THEME_GREEN,
    )

    zones_images_path = os.path.join('crafting', 'examples', 'minecraft', 'images', 'zones')
    for zone in MC_ZONES:
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

    return items_menu, recipes_menu, zones_menu

class InventoryWidget():

    def __init__(self, background, position, shape):
        self.background = background
        self.position = position
        self.shape = shape

    def update(self, events):
        pass

    def draw(self, surface):
        surface.blit(self.background, self.position)

def create_window():
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    window_shape = (int(16/9 * 600), 720)
    pygame.init()
    clock = pygame.time.Clock()

    # Create window
    screen = pygame.display.set_mode(window_shape)
    pygame.display.set_caption('MineCrafting')

    # Create menu
    menus = make_menus(*window_shape)

    # Create inventory
    background_path = os.path.join('crafting', 'examples', 'minecraft', 'images', 'inventory.png')
    background = pygame.image.load(background_path).convert()

    background_width, background_height = background.get_size()
    scale_ratio = int(0.65 * window_shape[0]) / background_width
    new_shape = (int(background_width * scale_ratio), int(background_height * scale_ratio))
    background = pygame.transform.scale(background, new_shape) # Rescale background

    position = (int(0.15 * window_shape[0]), int(0.15 * window_shape[0]))
    inv_widget = InventoryWidget(background, position, new_shape)

    return clock, screen, menus, inv_widget

def update_rendering(clock, screen, menus, inv_widget, fps=60):
    # Tick
    clock.tick(fps)

    # Paint background
    screen.fill((198, 198, 198))

    # Execute main from principal menu if is enabled
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            exit()

    inv_widget.update(events)
    inv_widget.draw(screen)

    action = None
    for menu in menus:
        menu.update(events)
        menu.draw(screen)
        selected_widget = menu.get_selected_widget()
        if selected_widget.update(events):
            action = selected_widget.apply()

    # Update surface
    pygame.display.update()
    return action

def get_human_action(clock, screen, menus, inv_widget, fps=60):
    action_chosen = False
    pygame.time.delay(100)
    while not action_chosen:
        action = update_rendering(clock, screen, menus, inv_widget, fps)
        action_chosen = action is not None
    return action


if __name__ == '__main__':
    clock, screen, menus, inv_widget = create_window()
    while True:
        print(get_human_action(clock, screen, menus, inv_widget))
