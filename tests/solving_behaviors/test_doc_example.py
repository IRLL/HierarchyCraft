from matplotlib import pyplot as plt
import pytest
import pytest_check as check


@pytest.mark.slow
def test_doc_example():
    from hcraft.examples import MineHcraftEnv
    from hcraft.examples.minecraft.items import DIAMOND
    from hcraft.task import GetItemTask

    draw_call_graph = False
    render = False

    if draw_call_graph:
        _fig, ax = plt.subplots()

    get_diamond = GetItemTask(DIAMOND)
    env = MineHcraftEnv(purpose=get_diamond, max_step=50)
    solving_behavior = env.solving_behavior(get_diamond)

    done = False
    observation = env.reset()
    if render:
        env.render()
    while not done:
        action = solving_behavior(observation)

        if draw_call_graph:
            plt.cla()
            solving_behavior.graph.call_graph.draw(ax)
            plt.show(block=False)

        observation, _reward, done, _info = env.step(action)
        if render:
            env.render()

    check.is_true(get_diamond.terminated)  # DIAMOND has been obtained !
