import pytest

from crafting.env import CraftingEnv
from crafting.render.human import render_env_with_human
from crafting.transformation import Transformation
from crafting.world import Item, ItemStack, Zone


class TestCratingEnv:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.start_zone = Zone("start")
        self.other_zone = Zone("other_zone")
        self.zones = [self.start_zone, self.other_zone]

        self.move_to_other_zone = Transformation(
            destination=self.other_zone,
            zones=[self.start_zone],
        )

        self.wood = Item("wood")
        self.search_wood = Transformation(
            added_player_items=[ItemStack(self.wood)],
        )

        self.stone = Item("stone")
        self.search_stone = Transformation(
            added_player_items=[ItemStack(self.stone, 1)],
        )

        self.plank = Item("plank")
        self.craft_plank = Transformation(
            removed_player_items=[ItemStack(self.wood, 1)],
            added_player_items=[ItemStack(self.plank, 4)],
        )

        self.table = Item("table")
        self.craft_table = Transformation(
            removed_player_items=[ItemStack(self.plank, 4)],
            added_zone_items=[ItemStack(self.table)],
        )

        self.wood_house = Item("wood house")
        self.build_house = Transformation(
            removed_player_items=[ItemStack(self.plank, 32), ItemStack(self.wood, 8)],
            added_zone_items=[ItemStack(self.wood_house)],
        )

        self.items = [self.wood, self.stone, self.plank]
        self.zones_items = [self.table, self.wood_house]
        self.transformations = [
            self.move_to_other_zone,
            self.search_wood,
            self.search_stone,
            self.craft_plank,
            self.craft_table,
            self.build_house,
        ]

    def test_render_rgb_array(self):
        pytest.importorskip("pygame")
        pytest.importorskip("pygame_menu")
        env = CraftingEnv(self.transformations, start_zone=self.start_zone)
        rgb_array = env.render(render_mode="rgb_array")
        env.close()
