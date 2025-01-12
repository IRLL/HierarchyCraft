# Contributing to HierarchyCraft

Whenever you encounter a :bug: **bug** or have :tada: **feature request**,
report this via `Github issues <https://github.com/IRLL/HierarchyCraft/issues>`_.

We are happy to receive contributions in the form of **pull requests** via Github.
Feel free to fork the repository, implement your changes and create a merge request to the `master` branch.

## Build from source (for contributions)

1. Clone the repository

```bash
git clone https://github.com/IRLL/HierarchyCraft.git
```

2. Install `uv`

`uv` is a rust-based extremely fast package management tool 
that we use for developement.

See [`uv` installation instructions](https://docs.astral.sh/uv/getting-started/installation/).

3. Install all dependencies in a virtual environment using uv

Install hcraft as an editable package with
dev requirements and all other extra requirements using uv:
```bash
uv sync --extra gym --extra gui --extra planning --extra htmlvis
```

4. Check installation

Check installation by running (fast) tests,
remove the marker flag to run even slow tests:
```bash
pytest -m "not slow"
```
