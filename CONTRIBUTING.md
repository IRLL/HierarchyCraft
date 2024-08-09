# Contributing to HierarchyCraft

Whenever you encounter a :bug: **bug** or have :tada: **feature request**,
report this via `Github issues <https://github.com/IRLL/HierarchyCraft/issues>`_.

We are happy to receive contributions in the form of **pull requests** via Github.
Feel free to fork the repository, implement your changes and create a merge request to the `master` branch.

## Build from source (for contributions)

```bash
git clone https://github.com/IRLL/HierarchyCraft.git
```

Install hcraft as an editable package with  dev requirements and all other optional requirements
```bash
pip install -e .[dev,gym,planning,gui,htmlvis]
```

Check installation by running tests
```bash
pytest
```
