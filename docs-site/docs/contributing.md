---
sidebar_position: 99
title: Contributing
---

# Contributing

## Lint and style

- **Ruff** runs in CI on agreed Python trees (see [`.github/workflows/lint.yml`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/.github/workflows/lint.yml) and the [`Makefile`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/Makefile)).
- Match existing patterns in the tree you touch; avoid drive-by reformatting of unrelated files.

## Validate IWXXM before merge

Encoder changes should produce **schema- and Schematron-clean** IWXXM where Annex 3–conformant TAC allows it. Before treating XML as ready for dissemination:

1. Generate `.xml` (or bulletin output) from representative TAC.
2. Run **`validation/iwxxmValidator.py`** on a directory of those files (from **`validation/`** as CWD).

See [Validation workflow](./workflows/validation) and [validation/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/validation/README.md).

## Tests and coverage

- Layout, markers, and Makefile targets: [Testing overview](./testing/overview).
- Pipeline goldens: [Pipeline goldens (testing)](./testing/pipeline-goldens).
- CI summary: [CI workflows](./reference/ci-workflows).

## Documentation

This Docusaurus site **summarizes** the repo; keep canonical procedural detail in the root, `demo/`, `validation/`, and `tests/` READMEs when adding features.
