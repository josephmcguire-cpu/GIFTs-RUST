# Security tooling (hooks + CI)

Layer **fast feedback** (local hooks) with **deeper checks** (CI).

## Local / pre-push (typical)

| Tool | Role |
|------|------|
| **shellcheck** | Lint `*.sh` |
| **detect-secrets** | Block accidental credential patterns |
| **actionlint** | Validate GitHub Actions YAML |
| **zizmor** | Static analysis for workflow security |

Wire these through **prek** (or pre-commit if the project uses it). Prefer **`uv run`** in hook commands.

## CI / scheduled

| Tool | Role |
|------|------|
| **pip-audit** | Report known vulnerabilities in locked deps (`uv.lock`) |
| **Dependabot** | Open PRs for dependency bumps (see [dependabot.md](dependabot.md)) |

## pip-audit with uv

Run against the project environment (example pattern):

```bash
uv sync --all-groups
uv run pip-audit
```

Pin `pip-audit` in a **dependency group** (e.g. `audit`) rather than ad-hoc global installs.

## Principle

Keep **secrets and workflow hygiene** in hooks; keep **supply-chain visibility** in CI with a clear policy for failing builds on critical CVEs.
