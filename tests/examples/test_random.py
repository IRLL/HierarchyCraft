import pytest
import pytest_check as check

from hcraft.examples.random_simple.env import RandomHcraftEnv
from tests.custom_checks import check_isomorphic, check_not_isomorphic


class TestRandomHcraft:

    """Test the RandomHcraft environment"""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Setup test fixtures."""
        self.n_items_per_n_inputs = {0: 1, 1: 5, 2: 10, 4: 1}
        self.n_items = sum(self.n_items_per_n_inputs.values())

    def test_gym_make(self):
        gym = pytest.importorskip("gym")
        env: RandomHcraftEnv = gym.make(
            "RandomHcraft-v1",
            n_items_per_n_inputs=self.n_items_per_n_inputs,
            seed=42,
        )
        check.equal(len(env.world.items), self.n_items)
        check.equal(env.seed, 42)

    def test_same_seed_same_requirements_graph(self):
        env = RandomHcraftEnv(self.n_items_per_n_inputs, seed=42)
        env2 = RandomHcraftEnv(self.n_items_per_n_inputs, seed=42)
        check.equal(env.seed, env2.seed)
        check_isomorphic(
            env.world.requirements.graph,
            env2.world.requirements.graph,
        )

    def test_different_seed_different_requirements_graph(self):
        env = RandomHcraftEnv(self.n_items_per_n_inputs, seed=42)
        env2 = RandomHcraftEnv(self.n_items_per_n_inputs, seed=43)
        check.not_equal(env.seed, env2.seed)
        check_not_isomorphic(
            env.world.requirements.graph,
            env2.world.requirements.graph,
        )
