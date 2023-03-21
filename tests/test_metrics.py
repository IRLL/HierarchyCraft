import pytest
import pytest_check as check

from hcraft.elements import Item
from hcraft.env import HcraftEnv
from hcraft.purpose import GetItemTask, PlaceItemTask, Purpose
from tests.envs import classic_env


def _actions_per_episodes():
    return [
        ["search_wood", "craft_plank", "craft_table"],
        ["search_wood", "search_stone"],
    ]


class TestMetricsPurposeLess:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world, self.named_transformations = classic_env()[1:3]
        self.env = HcraftEnv(self.world)

    def test_successes(self):
        for _, actions in enumerate(_actions_per_episodes()):
            self.env.reset()
            for action in actions:
                transfo = self.named_transformations.get(action)
                action_id = self.env.world.transformations.index(transfo)
                _, _, _, infos = self.env.step(action_id)
                check.equal(len(infos), 3)


class TestMetricsSinglePurpose:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world, self.named_transformations = classic_env()[1:3]

        self.purpose = Purpose()
        self.get_wood_task = GetItemTask(Item("wood"), 1)
        self.purpose.add_task(self.get_wood_task, terminal_groups=None)
        self.place_table_task = PlaceItemTask(Item("table"), reward=15)
        self.purpose.add_task(self.place_table_task, terminal_groups="table")
        self.env = HcraftEnv(self.world, purpose=self.purpose, max_step=4)

    def test_successes(self):
        for episode, actions in enumerate(_actions_per_episodes()):
            self.env.reset()
            for action in actions:
                transfo = self.named_transformations.get(action)
                action_id = self.env.world.transformations.index(transfo)
                _, _, done, infos = self.env.step(action_id)
                if episode == 0:
                    check.equal(infos[f"{self.get_wood_task.name} is done"], True)
                    check.equal(infos[f"{self.place_table_task.name} is done"], done)
                    check.equal(infos[f"{self.get_wood_task.name} success rate"], 1.0)
                    check.equal(
                        infos[f"{self.place_table_task.name} success rate"], float(done)
                    )
                    check.equal(infos["Purpose is done"], done)
                    check.equal(infos["Purpose success rate"], float(done))
                if episode == 1:
                    check.equal(infos[f"{self.get_wood_task.name} is done"], True)
                    check.equal(infos[f"{self.place_table_task.name} is done"], False)
                    check.equal(infos[f"{self.get_wood_task.name} success rate"], 1.0)
                    check.equal(
                        infos[f"{self.place_table_task.name} success rate"], 0.5
                    )
                    check.equal(infos["Purpose is done"], False)
                    check.equal(infos["Purpose success rate"], 0.5)


class TestMetricsMultiPurpose:
    @pytest.fixture(autouse=True)
    def setup_method(self):
        self.world, self.named_transformations = classic_env()[1:3]
        self.purpose = Purpose()
        self.get_wood_task = GetItemTask(Item("wood"), 1)
        self.purpose.add_task(self.get_wood_task, terminal_groups=None)
        self.get_stone_task = GetItemTask(Item("stone"), 10)
        self.purpose.add_task(self.get_stone_task, terminal_groups="stone")
        self.place_table_task = PlaceItemTask(Item("table"), reward=15)
        self.purpose.add_task(self.place_table_task, terminal_groups="table")
        self.env = HcraftEnv(self.world, purpose=self.purpose)

    def test_successes(self):
        for episode, actions in enumerate(_actions_per_episodes()):
            self.env.reset()
            for action in actions:
                transfo = self.named_transformations.get(action)
                action_id = self.env.world.transformations.index(transfo)
                _, _, done, infos = self.env.step(action_id)
                if episode == 0:
                    check.equal(infos[f"{self.get_wood_task.name} is done"], True)
                    check.equal(infos[f"{self.place_table_task.name} is done"], done)
                    check.equal(infos[f"{self.get_wood_task.name} success rate"], 1.0)
                    check.equal(
                        infos[f"{self.place_table_task.name} success rate"], float(done)
                    )
                    check.equal(infos["Terminal group 'stone' is done"], False)
                    check.equal(infos["Terminal group 'table' is done"], done)
                    check.equal(infos["Terminal group 'stone' success rate"], 0.0)
                    check.equal(
                        infos["Terminal group 'table' success rate"], float(done)
                    )
                if episode == 1:
                    check.equal(infos[f"{self.get_wood_task.name} is done"], True)
                    check.equal(infos[f"{self.place_table_task.name} is done"], False)
                    check.equal(infos[f"{self.get_wood_task.name} success rate"], 1.0)
                    check.equal(
                        infos[f"{self.place_table_task.name} success rate"], 0.5
                    )
                    check.equal(infos["Terminal group 'table' is done"], False)
                    check.equal(infos["Terminal group 'table' success rate"], 0.5)
                    if done:
                        check.equal(infos[f"{self.get_stone_task.name} is done"], True)
                        check.equal(
                            infos[f"{self.get_stone_task.name} success rate"], 0.5
                        )
                        check.equal(infos["Terminal group 'stone' is done"], True)
                        check.equal(infos["Terminal group 'stone' success rate"], 0.5)

    def test_successes_window(self):
        actions_per_wood_10_episodes = [["search_wood"]] * 10
        actions_per_stone_10_episodes = [["search_stone"]] * 10
        wood_info = f"{self.get_wood_task.name} success rate"
        stone_info = f"{self.get_stone_task.name} success rate"
        for episode, actions in enumerate(actions_per_wood_10_episodes):
            self.env.reset()
            for action in actions:
                transfo = self.named_transformations.get(action)
                action_id = self.env.world.transformations.index(transfo)
                _, _, _, infos = self.env.step(action_id)
                check.equal(infos[wood_info], 1.0, msg=f"episode={episode}")
                check.equal(infos[stone_info], 0.0, msg=f"episode={episode}")
        for episode, actions in enumerate(actions_per_stone_10_episodes, start=1):
            self.env.reset()
            for action in actions:
                transfo = self.named_transformations.get(action)
                action_id = self.env.world.transformations.index(transfo)
                _, _, _, infos = self.env.step(action_id)
                check.almost_equal(
                    infos[wood_info],
                    1 - episode / 10,
                    msg=f"episode={episode}|{wood_info}",
                )
                check.almost_equal(
                    infos[stone_info],
                    episode / 10,
                    msg=f"episode={episode}|{stone_info}",
                )
                check.almost_equal(
                    infos["Terminal group 'stone' success rate"],
                    episode / 10,
                    msg=f"episode={episode}|Terminal group 'stone'",
                )

    def test_score_values(self):
        for episode, actions in enumerate(_actions_per_episodes()):
            self.env.reset()
            score = 0
            for action in actions:
                transfo = self.named_transformations.get(action)
                action_id = self.env.world.transformations.index(transfo)
                _, reward, done, infos = self.env.step(action_id)
                score += reward
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
                        msg=f"cumulated_score={self.env.cumulated_score}"
                        f"episode={self.env.episodes}",
                    )
