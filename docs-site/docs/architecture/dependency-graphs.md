---
sidebar_position: 19
title: Dependency graphs
---

# Dependency graphs

How **logical services**, **artifacts**, and **key modules** depend on each other across the monorepo. `validation/` is a **sibling tree** to `gifts/`; it is **not** a Python dependency of the `gifts` package in [`pyproject.toml`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/pyproject.toml).

## Logical services and consumers

```mermaid
flowchart TB
  subgraph lib [gifts_Python_package]
    encoders[Encoders_and_Bulletin]
  end

  subgraph consumers [Consumers_of_gifts]
    demo1[demo1_py]
    iwxxmd[iwxxmd_py]
    pytest[pytest_suites]
    freeze[tools_freeze_pipeline_cases]
  end

  subgraph val [validation_tree_sibling]
    iwxxm[iwxxmValidator_py]
    crux[CRUX_jar]
    fs[schemas_schematrons_externalSchemas]
  end

  subgraph ci [CI_workflows]
    tg[test_gifts]
    tv[test_validation]
    td[test_demo]
    e2e[e2e]
    docswf[docs_site_build]
  end

  demo1 --> lib
  iwxxmd --> lib
  pytest --> lib
  freeze --> lib
  lib -->|"IWXXM_XML_on_disk"| val
  iwxxm --> crux
  iwxxm --> fs
  tg --> lib
  tv --> val
  td --> lib
  td --> demo1
  e2e --> lib
  e2e --> val
  docswf --> docswf
```

Notes:

- **Tests** import `gifts` and sometimes invoke `validation/` scripts as subprocesses or skip when Java/schemas are missing.
- **e2e** ties **encode → files → `iwxxmValidator`** (see [E2E workflow](../workflows/e2e)).

## Artifact and data flow

```mermaid
flowchart LR
  tac[TAC_plus_AHL]
  enc[gifts_Encoder_encode]
  bull[bulletin_Bulletin]
  xml[IWXXM_XML_files]
  val[iwxxmValidator]
  crux[CRUX_schema_Schematron]

  tac --> enc
  enc --> bull
  bull --> xml
  enc --> xml
  xml --> val
  val --> crux
```

Optional paths:

- **Pipeline goldens** — replay TAC with fixed time/UUID → compare to `testdata/pipeline/.../golden/` (see [Pipeline goldens](../testing/pipeline-goldens)).
- **E2e** — same idea with real validator invocation when the environment provides Java + layout under `validation/`.

## gifts module stack (direction of use)

```mermaid
flowchart TB
  subgraph products [Product_packages]
    METAR[METAR_py]
    TAF[TAF_py]
    TCA[TCA_py]
    VAA[VAA_py]
    SWA[SWA_py]
  end

  subgraph common [gifts_common]
    Enc[Encoder_py]
    Bull[bulletin_py]
    Xcfg[xmlConfig_py]
    Xut[xmlUtilities_py]
  end

  subgraph decenc [Per_product]
    dec[*Decoder_Annex3]
    encm[*Encoder_Annex3]
  end

  subgraph data [Data_and_support]
    rdf[gifts_data_RDF]
    geo[gifts_database_pickle]
    sky[skyfield_support]
  end

  products --> Enc
  METAR --> dec
  METAR --> encm
  TAF --> dec
  TAF --> encm
  TCA --> dec
  TCA --> encm
  VAA --> dec
  VAA --> encm
  SWA --> dec
  SWA --> encm
  Enc --> Bull
  Enc --> Xcfg
  Enc --> Xut
  encm --> Xcfg
  dec --> Xcfg
  encm --> rdf
  METAR --> geo
  TAF --> geo
  products --> sky
```

| Layer | Depends on |
|-------|------------|
| Product `Encoder` | `common.Encoder`, `re_AHL` / `re_TAC`, `*Decoder`, `*Encoder`, optional `geoLocationsDB` |
| `common.Encoder` | `bulletin`, `xmlConfig`, `xmlUtilities`, `decoder`/`encoder` callables |
| IWXXM build | `xmlConfig` (site/IWXXM options), RDF under `gifts/data` where applicable |
| METAR/TAF | Pickled geo map via `gifts/database` |

## validation tool and filesystem stack

Run `iwxxmValidator.py` with **current working directory** = `validation/` so relative paths resolve (see [validation layout](../reference/validation-layout)).

```mermaid
flowchart TD
  cli[iwxxmValidator_main]
  cat[catalog_from_template]
  java[java_CRUX_jar]
  xsd[schemas_version]
  sch[schematrons_iwxxm_sch]
  ext[externalSchemas_mirror]
  gml[checkGMLReferences_optional]
  fetch[codeListsToSchematron_fetch_path]

  cli --> cat
  cli --> java
  java --> xsd
  java --> sch
  java --> ext
  cli --> gml
  cli --> fetch
```

| Component | Depends on |
|-----------|------------|
| `iwxxmValidator.py` | `bin/crux-1.3-all.jar`, `externalSchemas/`, generated `catalog-<ver>.xml`, `schemas/<ver>/`, `schematrons/<ver>/` |
| CRUX invocation | Catalog file, Schematron path, glob of `*.xml` in target directory |
| GML pass | `checkGMLReferences.py`; optional network if `-u` |
| `-f` / missing schema path | `codeListsToSchematron.py` and downloads per [validation README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/validation/README.md) |

## CI and docs isolation

```mermaid
flowchart LR
  subgraph triggers [Typical_triggers]
    py[Python_trees]
    ds[docs_site_only]
    all[push_PR_main]
  end

  subgraph jobs [Workflows]
    lint[lint_yml]
    tg[test_gifts_yml]
    doc[docs_yml]
  end

  py --> lint
  py --> tg
  ds --> doc
```

The **docs** workflow builds only [`docs-site/`](../reference/repository-layout) and does not need the `gifts` Python package.

## See also

- [Repository layout](../reference/repository-layout) — directory map
- [Repository overview](./overview) — narrative component view
- [gifts modules](./gifts-modules) — package diagram
- [gifts products](./gifts-products) — per-product wiring
- [Docker](../reference/docker) — image boundaries vs this graph
