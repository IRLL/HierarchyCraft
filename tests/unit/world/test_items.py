# Crafting a gym-environment to simultate inventory managment
# Copyright (C) 2021-2023 Mathïs FEDERICO <https://www.gnu.org/licenses/>
# pylint: disable=attribute-defined-outside-init

""" Item and subclasses tests """

import pytest
import pytest_check as check
from crafting.world.items import Item, Tool, ItemStack


@pytest.fixture
def item():
    """Dummy item"""
    return Item(12, name="item_name")


class TestItem:
    """Item"""

    @pytest.fixture(autouse=True)
    def setup(self, item):
        """Setup reused variables."""
        self.item = item

    def test_init(self):
        """should instanciate attributes correctly."""
        check.equal(self.item.item_id, 12)
        check.equal(self.item.name, "item_name")

    def test_str(self):
        """should be converted to str correctly."""
        expected_item_name = "Item_name(12)"
        check.equal(str(self.item), expected_item_name)


class TestItemStack:
    """ItemStack"""

    @pytest.fixture(autouse=True)
    def setup(self, item):
        """Setup reused variables."""
        self.item = item

    def test_init(self):
        """should instanciate correctly."""
        stack = ItemStack(self.item, 8)
        check.equal(stack.item_id, self.item.item_id)
        check.equal(stack.size, 8)


class TestTool:
    """Tool"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup reused variables."""
        self.tool_id = 18
        self.tool_name = "tool_name"
        self.tool = Tool(self.tool_id, self.tool_name)

    def test_init(self):
        """should instanciate correctly."""
        check.equal(self.tool.item_id, self.tool_id)
        check.equal(self.tool.name, self.tool_name)

    def test_use_item(self, item):
        """should find item on use on item."""
        findings = self.tool.use(item)
        check.equal(findings[0].item_id, item.item_id)
        check.equal(findings[0].size, 1)

    def test_use_none(self):
        """should find nothing on use on None."""
        findings = self.tool.use(None)
        check.equal(findings, [])

    def test_str(self):
        """should be converted to str correctly."""
        check.equal(str(self.tool), f"{self.tool_name.capitalize()}({self.tool_id})")
