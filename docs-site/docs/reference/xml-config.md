---
sidebar_position: 3
title: xmlConfig
---

# `xmlConfig` (site and IWXXM options)

[`gifts/common/xmlConfig.py`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/gifts/common/xmlConfig.py) holds **site-wide** toggles and URIs for all TAC→IWXXM encoders. The source file is the authority; this page lists the most cross-cutting symbols.

## Translation centre

| Name | Role |
|------|------|
| `TRANSLATOR` | When `True`, encoder populates translated-bulletin metadata (`TranslationCentreName` / `TranslationCentreDesignator` apply) |
| `TranslationCentreName` / `TranslationCentreDesignator` | Identifiers for bulk translation scenarios |

## IWXXM version and validation alignment

| Name | Role |
|------|------|
| `_iwxxm` / `_release` | Internal IWXXM version strings used to build `IWXXM_URI` / `IWXXM_URL` |
| `IWXXM_URI` | Namespace URI embedded in output XML |
| `IWXXM_URL` | Published schema URL hint |
| `IWXXM_VALIDATOR_VERSION` | Directory name under `validation/schemas/` and `validation/schematrons/` for `iwxxmValidator.py -v` — **keep aligned** when validating GIFTs output |

## Code registry / RDF

| Name | Role |
|------|------|
| `CodesFilePath` | Directory containing downloaded RDF from the WMO Code Registry (files under `gifts/data/`) |

Additional variables (elevations, CRS, titles, etc.) are documented inline in `xmlConfig.py`.

## See also

- [Technical requirements](../trd)
- [Validation layout](./validation-layout)
