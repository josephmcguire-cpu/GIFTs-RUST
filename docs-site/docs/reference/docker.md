---
sidebar_position: 7
title: Docker
---

# Docker

Local images mirror **dependency boundaries** in the monorepo (see [Dependency graphs](../architecture/dependency-graphs)).

## Dockerfiles

| File | Base | Copies | Default command |
|------|--------|--------|-----------------|
| [`Dockerfile.gifts`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/Dockerfile.gifts) | `python:3.11-slim-bookworm` | `pyproject` metadata + `gifts/` | `pytest gifts/tests` with coverage gate |
| [`Dockerfile.validation`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/Dockerfile.validation) | same + **OpenJDK 17 JRE** | `gifts/` + `validation/` | `WORKDIR /app/validation`; `pytest tests` (i.e. `validation/tests`) |
| [`Dockerfile.demo`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/Dockerfile.demo) | same + **Tk libs** (headless tests) | `gifts/` + `demo/` | `pytest demo/tests` |

All install **`pip install -e ".[test]"`** (and `watchdog` for demo image).

## docker-compose

[`docker-compose.yml`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/docker-compose.yml):

| Service | Build | Working dir / notes |
|---------|-------|---------------------|
| `gifts` | `Dockerfile.gifts` | `/app`; mount `.` → `/app` |
| `validation` | `Dockerfile.validation` | **`/app/validation`** for validator-centric work |
| `demo` | `Dockerfile.demo` | `/app` |
| `e2e` | `Dockerfile.gifts` | **Profile `e2e`**: runs `pytest tests/e2e -m e2e` |

Typical smoke:

```bash
docker compose build
docker compose run --rm gifts
docker compose run --rm validation
docker compose run --rm demo
docker compose --profile e2e run --rm e2e
```

Exact `compose run` invocations follow comments in the compose file.

## Relationship to validation on the host

The **validation** image includes Java for CRUX-style workflows in CI-style environments; **running `iwxxmValidator.py` on the host** still requires the same layout documented in [Validation layout](./validation-layout).
