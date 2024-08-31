from typing import Optional, Type, List
import warnings
import pytest
from hcraft.env import HcraftEnv
from tests.envs import classic_env


class TestPlanning:
    @pytest.fixture(autouse=True)
    def setup(self, planning_fixture: "PlanningFixture"):
        self.fixture = planning_fixture

    def test_warn_no_goal(self):
        env, _, _, _, _, _, _ = classic_env()
        self.fixture.given_env(env)
        self.fixture.when_building_planning_problem()
        self.fixture.then_warning_should_be_given(UserWarning, "plans will be empty")


@pytest.fixture
def planning_fixture() -> "PlanningFixture":
    return PlanningFixture()


class PlanningFixture:
    def given_env(self, env: HcraftEnv) -> None:
        self.env = env

    def when_building_planning_problem(self) -> None:
        with pytest.warns() as self.warning_records:
            self.planning_problem = self.env.planning_problem()

    def then_warning_should_be_given(
        self,
        warning_type: Type[Warning] = Warning,
        match: Optional[str] = None,
    ) -> None:
        assert _warning_in_records(
            warning_records=self.warning_records, warning_type=warning_type, match=match
        ), "Could not find required warning"


def _warning_in_records(
    warning_records: List[warnings.WarningMessage],
    warning_type: Type[Warning],
    match: Optional[str],
) -> bool:
    for record in warning_records:
        if not isinstance(record.message, warning_type):
            continue
        if match is None:
            return True
        for arg in record.message.args:
            if isinstance(arg, str) and match in arg:
                return True
    return False
