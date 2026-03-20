# PEP 723 — Inline script metadata

Use for **single-file scripts** that need third-party packages without a full project layout.

## Minimal pattern

At the **top** of the script (after the shebang if present), add a TOML block in a comment:

```python
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "requests",
#   "rich",
# ]
# ///

import requests
from rich import print
```

Run with uv (reads the block and syncs deps for that invocation):

```bash
uv run script.py
```

## Notes

- The `/// script` / `///` fence is the PEP 723 convention; uv documents this as **inline script metadata**.
- Prefer this over `requirements.txt` for standalone scripts.
- For anything multi-file or installable, use `uv init` / `pyproject.toml` instead.

## See also

- [uv docs: Running scripts](https://docs.astral.sh/uv/guides/scripts/) (inline metadata)
