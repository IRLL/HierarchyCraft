# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021 Mathïs FEDERICO <https://www.gnu.org/licenses/>

""" Rendering of the MineCrafting environment """

import os
from typing import List

import pygame, pygame_menu
from pygame.event import Event

from crafting.env import CraftingEnv
from crafting.render.widgets import InventoryWidget, ScoreWidget, ZoneWidget
from crafting.world.world import World

def get_human_action(env, additional_events=None, can_be_none=False, **kwargs):
    action_chosen = False
    while not action_chosen:
        action = update_rendering(env, additional_events=additional_events, **kwargs)
        action_chosen = action is not None or can_be_none
    return action

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
        buttons = [widget for widget in menu.get_widgets()
            if isinstance(widget, pygame_menu.widgets.Button)]
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


if __name__ == '__main__':
    from pygame.locals import MOUSEBUTTONDOWN, MOUSEBUTTONUP
    from crafting.examples import MineCraftingEnv
    

    env = MineCraftingEnv(verbose=1, max_step=100,
        tasks=['obtain_enchanting_table'], tasks_can_end=[True]
    )

    import matplotlib.pyplot as plt
    # fig, ax = plt.subplots()
    # env.world.draw_requirements_graph(ax)
    # plt.show()

    ALL_GET_OPTIONS = env.world.get_all_options()

    enchant_table_option = ALL_GET_OPTIONS[ENCHANTING_TABLE.item_id]
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
