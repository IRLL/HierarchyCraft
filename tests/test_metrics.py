import pytest
import pytest_check as check

from crafting.env import CraftingEnv
from crafting.purpose import Purpose, GetItemTask, PlaceItemTask
from crafting.world import Item

from tests.envs import classic_env


class TestScore:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world, self.named_transformations = classic_env()[1:3]
        self.purpose = Purpose()
        self.purpose.add_task(GetItemTask(Item("wood"), 1), terminal_groups=None)
        self.purpose.add_task(GetItemTask(Item("stone"), 10), terminal_groups="stone")
        self.purpose.add_task(
            PlaceItemTask(Item("table"), reward=15), terminal_groups="table"
        )
        self.env = CraftingEnv(self.world, purpose=self.purpose)

    def test_score_values(self):
        actions_per_episodes = []
        actions_per_episodes.append(["search_wood", "craft_plank", "craft_table"])
        actions_per_episodes.append(["search_wood", "search_stone"])

        for episode, actions in enumerate(actions_per_episodes):
            self.env.reset()
            score = 0
            for action in actions:
                transfo = self.named_transformations.get(action)
                action_id = self.env.world.transformations.index(transfo)
                _, reward, done, infos = self.env.step(action_id)
                score += reward
                print(episode, action, reward)
                if episode == 0:
                    check.equal(infos["score"], score)
                    check.equal(infos["score_average"], score)
                    if done:
                        check.equal(infos["score"], 16)
                        check.equal(infos["score_average"], 16)
                if episode == 1 and done:
                    check.equal(reward, 10)
                    check.equal(infos["score"], 1 + 10)
                    check.equal(
                        infos["score_average"],
                        (16 + score) / 2,
                        msg=f"{self.env.cumulated_score=},{self.env.episodes=}",
                    )
