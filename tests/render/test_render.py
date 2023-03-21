import pytest_check as check

from hcraft.render.render import menus_sizes


class TestMenusSizes:
    def test_no_zone_no_zone_items(self):
        shapes = menus_sizes(
            n_items=1,
            n_zones_items=0,
            n_zones=0,
            window_shape=[200, 100],
        )
        check.equal(shapes["actions"], (70, 100))
        check.equal(shapes["player"], (130, 100))

    def test_one_zone_no_zone_items(self):
        """No need to show position when only one zone"""
        shapes = menus_sizes(
            n_items=1,
            n_zones_items=0,
            n_zones=1,
            window_shape=[200, 100],
        )
        check.equal(shapes["zone"], (0, 0))
        check.equal(shapes["position"], (0, 0))

    def test_two_zone_no_zone_items(self):
        shapes = menus_sizes(
            n_items=1,
            n_zones_items=0,
            n_zones=2,
            window_shape=[200, 100],
        )
        check.equal(shapes["position"], (130, 73))

    def test_one_zone_no_player_item(self):
        shapes = menus_sizes(
            n_items=0,
            n_zones_items=10,
            n_zones=1,
            window_shape=[200, 100],
        )
        check.equal(shapes["player"], (0, 0))
        check.not_equal(shapes["zone"], (0, 0))

    def test_two_zones_no_player_item(self):
        shapes = menus_sizes(
            n_items=0,
            n_zones_items=10,
            n_zones=2,
            window_shape=[200, 100],
        )
        check.equal(shapes["player"], (0, 0))
        check.not_equal(shapes["zone"], (0, 0))
        check.not_equal(shapes["position"], (0, 0))

    def test_all(self):
        shapes = menus_sizes(
            n_items=10,
            n_zones_items=10,
            n_zones=10,
            window_shape=[200, 100],
        )
        check.equal(shapes["actions"], (70, 100))
        check.not_equal(shapes["player"], (0, 0))
        check.not_equal(shapes["zone"], (0, 0))
        check.not_equal(shapes["position"], (0, 0))
