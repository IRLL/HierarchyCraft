from typing import Dict, List, Union

from hcraft.purpose import Task, TerminalGroup


class SuccessCounter:
    """Counter of success rates of tasks or terminal groups."""

    def __init__(self, elements: List[Union[Task, TerminalGroup]]) -> None:
        self.elements = elements
        self.step_states = {}
        self.successes: Dict[Union[Task, TerminalGroup], Dict[int, bool]] = {
            element: {} for element in self.elements
        }

    def step_reset(self):
        """Set the state of elements."""
        self.step_states = {element: element.terminated for element in self.elements}

    def new_episode(self, episode: int):
        """Add a new episode successes."""
        for element in self.elements:
            self.successes[element][episode] = False
            if len(self.successes[element]) > 10:
                self.successes[element].pop(episode - 10)

    def update(self, episode: int):
        """Update the success state of the given element for the given episode."""
        for element in self.elements:
            # Just terminated
            if element.terminated != self.step_states[element]:
                self.successes[element][episode] = True

    @property
    def done_infos(self) -> Dict[str, bool]:
        return {
            self._is_done_str(self._name(element)): element.terminated
            for element in self.elements
        }

    @property
    def rates_infos(self) -> Dict[str, float]:
        return {
            self._success_str(self._name(element)): self._rate(element)
            for element in self.elements
        }

    @staticmethod
    def _success_str(name: str):
        return f"{name} success rate"

    @staticmethod
    def _is_done_str(name: str):
        return f"{name} is done"

    def _name(self, element: Union[Task, TerminalGroup]):
        if isinstance(element, Task):
            return element.name
        group_name = "Purpose"
        if len(self.elements) > 1:
            group_name = f"Terminal group '{element.name}'"
        return group_name

    def _rate(self, element: Union[Task, TerminalGroup]) -> float:
        n_episodes = max(1, len(self.successes[element]))
        return sum(self.successes[element].values()) / n_episodes
