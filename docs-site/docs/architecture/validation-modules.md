---
sidebar_position: 23
title: validation package modules
---

# `validation` directory modules

Python modules support **IWXXM XML** validation; **CRUX** (Java) performs schema and Schematron evaluation. The validator is **not** a TAC parser.

## Component diagram

```mermaid
flowchart TB
  cli[iwxxmValidator_main]
  fetch[optional_fetch_codeListsToSchematron]
  catalog[catalog_xml_from_template]
  crux[java_jar_CRUX]
  sch[schematrons_version_iwxxm_sch]
  xsd[schemas_version]
  ext[externalSchemas_tree]
  gml[checkGMLReferences]

  cli --> fetch
  cli --> catalog
  catalog --> crux
  crux --> sch
  crux --> xsd
  crux --> ext
  cli --> gml
```

## Sequence: validate directory

```mermaid
sequenceDiagram
  participant User
  participant Main as iwxxmValidator_main
  participant FS as filesystem
  participant Java as CRUX_process
  participant GML as checkGMLReferences

  User->>Main: CLI_directory_and_flags
  Main->>FS: ensure_schemas_schematron_or_fetch
  Main->>FS: write_catalog_from_template
  Main->>Java: os_system_java_jar_catalog_schematron_glob_xml
  Java-->>Main: exit_status
  opt GML_checks
    Main->>GML: check_GML_references(dir, version, useInternet)
    GML-->>Main: check_status
  end
  Main-->>User: aggregate_exit_code
```

## Module roles

| Module | Role |
|--------|------|
| `iwxxmValidator.py` | CLI entry; orchestrates catalog, CRUX, GML pass |
| `checkGMLReferences.py` | GML / registry-oriented checks |
| `codeListsToSchematron.py` | Tooling to refresh codelist / Schematron-related artifacts when fetching |

## Related

- [Validation workflow](../workflows/validation)
- [validation/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/validation/README.md)
