# Contributing to HierarchyCraft

Whenever you encounter a :bug: **bug** or have :tada: **feature request**,
report this via `Github issues <https://github.com/IRLL/HierarchyCraft/issues>`_.

We are happy to receive contributions in the form of **pull requests** via Github.
Feel free to fork the repository, implement your changes and create a merge request to the `master` branch.

## Build from source (for contributions)

```bash
git clone https://github.com/IRLL/HierarchyCraft.git
```

Install `uv` the [rust-based extremely fast package management tool](https://docs.astral.sh/uv/getting-started/installation/).


Install hcraft as an editable package with 
dev requirements and all other extra requirements using uv:
```bash
uv sync --extra gym --extra gui --extra planning --extra htmlvis
```

Check installation by running (fast) tests,
remove the marker flag to run even slow tests:
```bash
pytest -m "not slow"
```
