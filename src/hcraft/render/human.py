from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from pygame.event import Event

    from hcraft.env import HcraftEnv


def get_human_action(
    env: "HcraftEnv",
    additional_events: List["Event"] = None,
    can_be_none: bool = False,
    fps: Optional[float] = None,
):
    """Update the environment rendering and gather potential action given by the UI.

    Args:
        env: The running HierarchyCraft environment.
        additional_events (Optional): Additional simulated pygame events.
        can_be_none: If False, this function will loop on rendering until an action is found.
            If True, will return None if no action was found after one rendering update.

    Returns:
        The action found using the UI.

    """
    action_chosen = False
    while not action_chosen:
        action = env.render_window.update_rendering(additional_events, fps)
        action_chosen = action is not None or can_be_none
    return action


def render_env_with_human(env: "HcraftEnv", n_episodes: int = 1):
    """Render the given environment with human iteractions.

    Args:
        env (HcraftEnv): The HierarchyCraft environment to run.
        n_episodes (int, optional): Number of episodes to run. Defaults to 1.
    """
    print("Purpose: ", env.purpose)

    for _ in range(n_episodes):
        env.reset()
        done = False
        total_reward = 0
        while not done:
            env.render()
            action = get_human_action(env)
            print(f"Human did: {env.world.transformations[action]}")

            _observation, reward, done, _info = env.step(action)
            total_reward += reward

        print("SCORE: ", total_reward)
