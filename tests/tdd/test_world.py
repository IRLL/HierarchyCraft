import pytest
import pytest_check as check

from crafting.world import Item, Zone, World


class TestWorld:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.n_items = 5
        self.n_zones = 4
        self.n_transformations = 6

        self.items = [Item(str(i)) for i in range(self.n_items)]
        self.zones = [Zone(str(i)) for i in range(self.n_zones)]
        self.world = World(self.items, self.zones)

    def test_slot_from_item(self):
        item_3 = self.items[3]
        check.equal(self.world.slot_from_item(item_3), 3)

    def test_slot_from_zone(self):
        zone_3 = self.zones[3]
        check.equal(self.world.slot_from_zone(zone_3), 3)
