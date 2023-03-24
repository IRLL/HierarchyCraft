import pytest
import pytest_check as check


@pytest.mark.slow
def test_doc_example():
    from hcraft.examples import MineHcraftEnv
    from hcraft.examples.minecraft.items import DIAMOND
    from hcraft.task import GetItemTask

    get_diamond = GetItemTask(DIAMOND)
    env = MineHcraftEnv(purpose=get_diamond, max_step=50)
    solving_behavior = env.solving_behavior(get_diamond)

    done = False
    observation = env.reset()
    while not done:
        action = solving_behavior(observation)
        observation, _reward, done, _info = env.step(action)

    check.is_true(get_diamond.terminated)  # DIAMOND has been obtained !
