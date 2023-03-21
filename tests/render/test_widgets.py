import pytest_check as check

from hcraft.render.widgets import ContentMode, DisplayMode, show_button, show_content


class TestShowButton:
    def test_all(self):
        mode = DisplayMode.ALL
        check.is_true(show_button(mode, is_current=False, discovered=False))

    def test_discovered(self):
        mode = DisplayMode.DISCOVERED
        check.is_false(show_button(mode, is_current=False, discovered=False))
        check.is_true(show_button(mode, is_current=False, discovered=True))
        check.is_true(show_button(mode, is_current=True, discovered=False))

    def test_current(self):
        mode = DisplayMode.CURRENT
        check.is_false(show_button(mode, is_current=False, discovered=False))
        check.is_false(show_button(mode, is_current=False, discovered=True))
        check.is_true(show_button(mode, is_current=True, discovered=False))
        check.is_true(show_button(mode, is_current=True, discovered=True))


class TestShowTransformationContent:
    def test_all(self):
        mode = ContentMode.ALWAYS
        check.is_true(show_content(mode, discovered=False))

    def test_discovered(self):
        mode = ContentMode.DISCOVERED
        check.is_false(show_content(mode, discovered=False))
        check.is_true(show_content(mode, discovered=True))

    def test_current(self):
        mode = ContentMode.NEVER
        check.is_false(show_content(mode, discovered=False))
        check.is_false(show_content(mode, discovered=True))
