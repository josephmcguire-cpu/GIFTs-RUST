# prek — fast git hooks

**prek** is a Rust-native alternative to the Python **pre-commit** framework: hooks run quickly without bootstrapping a Python interpreter for the hook runner itself.

## When to use

- New projects where the team wants **speed** and minimal hook overhead
- Replacing `pre-commit` when migrating to uv-centric workflows

## Typical setup (conceptual)

1. Install prek per its upstream docs (package manager or binary release).
2. Define hooks in the format prek expects (often TOML or project-specific config—follow current prek documentation).
3. Install hooks into `.git/hooks` via prek’s install command.

## Relationship to uv

- Use **`uv run`** inside hook commands so tools (`ruff`, `ty`, `pytest`) resolve from the project environment.
- Dev tool versions stay pinned in `pyproject.toml` / `uv.lock`, not duplicated in a separate pre-commit YAML.

## Caveat

If the repository already standardizes on **pre-commit** + `.pre-commit-config.yaml`, do not rip it out unless the user asks to migrate—respect existing workflows.
