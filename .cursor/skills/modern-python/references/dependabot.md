# Dependabot (GitHub)

**Dependabot** opens pull requests when dependencies (including **uv** / **pip** ecosystems) have updates. Pair with **`uv.lock`** so CI proves the new graph resolves and tests pass.

## basics

- Enable in repository **Settings → Code security and analysis → Dependabot**.
- Add `.github/dependabot.yml`:

```yaml
version: 2
updates:
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
```

Adjust **`directory`** to where `pyproject.toml` / `uv.lock` live (often repo root).

## Workflow expectations

- CI should run `uv sync` + tests on Dependabot PRs.
- For libraries, review semver impact; for apps, merging lockfile updates quickly reduces CVE exposure.

## Complement

Use **pip-audit** in CI for **vulnerability signal**; Dependabot for **routine bumps**. See [security-setup.md](security-setup.md).
