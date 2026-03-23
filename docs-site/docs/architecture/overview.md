---
sidebar_position: 20
title: Repository overview
---

# Repository overview

High-level map of the monorepo: **installable library**, **applications**, **validation tooling**, and **tests/assets**.

## Component diagram

```mermaid
flowchart TB
  subgraph gifts_pkg [gifts_Python_package]
    common[gifts_common]
    products[gifts_METAR_TAF_TCA_VAA_SWA]
    db[gifts_database]
  end

  subgraph demo_layer [demo_applications]
    gui[demo1_Tk_GUI]
    daemon[iwxxmd_watchdog]
  end

  subgraph validation_layer [validation_tooling]
    valpy[iwxxmValidator_py]
    crux[CRUX_java_jar]
    schemas[schemas_schematrons_externalSchemas]
  end

  subgraph test_layer [tests_and_testdata]
    unit[gifts_validation_demo_tests]
    pipe[tests_pipeline]
    data[testdata_pipeline]
  end

  demo_layer --> gifts_pkg
  test_layer --> gifts_pkg
  gifts_pkg -->|IWXXM_XML| validation_layer
  valpy --> crux
  valpy --> schemas
  pipe --> data
```

## Typical artifact flow

```mermaid
flowchart LR
  tac[TAC_plus_AHL]
  enc[gifts_Encoder]
  xml[IWXXM_documents]
  bull[MeteorologicalBulletin_optional]
  check[iwxxmValidator]

  tac --> enc
  enc --> xml
  enc --> bull
  xml --> check
  bull --> check
```

## Directory roles

| Path | Role |
|------|------|
| `gifts/` | TAC decoders/encoders, `common/`, package data RDF |
| `demo/` | GUI and daemon entrypoints |
| `validation/` | Validator CLI, CRUX, schemas, Schematron, external schemas |
| `tests/` | Cross-cutting pytest suites |
| `testdata/` | Frozen pipeline cases and golden XML |

## See also

- [Dependency graphs](./dependency-graphs) — services, artifacts, `gifts` and `validation` stacks
- [Repository layout](../reference/repository-layout) — top-level directory map with links to READMEs
