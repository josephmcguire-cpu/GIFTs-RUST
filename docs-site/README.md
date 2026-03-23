# GIFTs documentation site (Docusaurus)

This directory builds the static documentation site (TRD, use cases, workflows, Mermaid diagrams).

## Prerequisites

- **Node.js ≥ 18** and npm
- **`overrides.serialize-javascript`** in `package.json` pins a patched release for a transitive advisory (webpack/Docusaurus stack). Revisit when upgrading Docusaurus if `npm audit` stays clean without it.

## Commands

```bash
cd docs-site
npm install    # first time; commit package-lock.json when it appears for reproducible CI
npm start      # local dev server with live reload
npm run build  # production build → build/
npm run serve  # serve build/ locally
```

From the **repository root**, the same flows are available via `make` (requires Node/npm on `PATH`):

| Target | Effect |
|--------|--------|
| `make docs-build` | `npm ci` or `npm install`, then production build |
| `make docs` | Same as `docs-build` |
| `make docs-dev` | Dev server with live reload (`npm start`) |
| `make docs-serve` | Build, then serve `build/` (`npm run serve`) |
| `make docs-clean` | Remove `node_modules`, `build/`, `.docusaurus` |
| `make docs-build NPM="$(command -v npm)"` | Use when `npm` works in Terminal but not under `make` |
| `make docs-docker-build` | Build using **Node 20 in Docker** (no host `npm`; requires Docker; bind-mounts `docs-site/`) |

`make distclean` also removes `docs-site/build` and `docs-site/.docusaurus` (not `node_modules`).

If `make docs-build` prints `./scripts/docs-with-npm.sh` without **`bash`** in the line, your **Makefile is outdated** — save/pull the current repo version (it should invoke `bash "$(CURDIR)/scripts/docs-with-npm.sh"`).

### `make` says `npm: command not found`

GNU Make runs recipes with a minimal environment. The repo includes [`scripts/docs-with-npm.sh`](../scripts/docs-with-npm.sh), which the `docs-*` Make targets use to:

- Source **nvm** from `~/.nvm/nvm.sh` or `~/.config/nvm/nvm.sh`
- Prepend **Volta** and **Homebrew** binary dirs (`~/.volta/bin`, `/opt/homebrew/bin`, `/usr/local/bin`)
- Run **`fnm env`** when `fnm` is available
- Run **`nvm use`** in `docs-site/` when `.nvmrc` is present

If it still fails:

1. Install Node 18+ (e.g. `brew install node`), **or**
2. From a terminal where `npm` already works, run:
   ```bash
   make docs-build NPM="$(command -v npm)"
   ```
   That passes the full path to `npm` into the helper script.

The helper also tries **login shells** (`zsh -il`, `bash -lc`) to match what Terminal loads from `~/.zprofile` / `~/.bash_profile`, which plain `make` does not read.

## GitHub Pages

- Workflow: [.github/workflows/docs.yml](../.github/workflows/docs.yml)
- **Pull requests** that touch `docs-site/` or the workflow: **build only** (validates the site compiles).
- **Push to `main`**: build + deploy to the **`gh-pages`** branch via [peaceiris/actions-gh-pages](https://github.com/peaceiris/actions-gh-pages).
- In the GitHub repo: **Settings → Pages → Build and deployment → Source: GitHub Actions**.

## Configure `baseUrl` and `url`

Edit [docusaurus.config.ts](./docusaurus.config.ts):

- **`url`**: `https://<owner>.github.io`
- **`baseUrl`**: `/<repository-name>/` for project pages (trailing slash)
- **`organizationName`** / **`projectName`**: must match the GitHub owner and repo if you use the generated GitHub navbar link

If the repository is renamed, update these fields and redeploy.

## Mermaid

Diagrams use fenced `mermaid` blocks in Markdown. The site enables `@docusaurus/theme-mermaid` (see `docusaurus.config.ts`).

## Canonical docs

Long-form operational detail remains in the repository root and subtree READMEs; this site summarizes and links out where appropriate.
