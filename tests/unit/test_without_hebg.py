import sys
from typing import List

import pytest


class PackageDiscarder:
    def __init__(self, pkgnames: List[str]):
        self.pkgnames = pkgnames
        for package in self.pkgnames:
            sys.modules.pop(package, None)

    def find_spec(self, fullname, path, target=None):
        if fullname in self.pkgnames:
            raise ImportError()

    def activate(self):
        sys.meta_path.insert(0, self)

    def deactivate(self):
        if self in sys.meta_path:
            sys.meta_path.remove(self)


@pytest.fixture
def no_hebg():
    discarder = PackageDiscarder("hebg")
    discarder.activate()
    yield
    discarder.deactivate()


@pytest.fixture(autouse=True)
def cleanup_imports():
    sys.modules.pop("crafting", None)
    yield
    sys.modules.pop("hebg", None)


def test_hebg_available():
    import hebg


@pytest.mark.usefixtures("no_hebg")
def test_hebg_missing():
    with pytest.raises(ImportError):
        import hebg


@pytest.mark.usefixtures("no_hebg")
def test_minecrafting_without_hebg():
    from crafting import MineCraftingEnv

    env = MineCraftingEnv(max_step=10, verbose=1)
    done = False
    while not done:
        _observation, _reward, done, _info = env.step(0)
