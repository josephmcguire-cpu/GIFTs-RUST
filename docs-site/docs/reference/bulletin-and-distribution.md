---
sidebar_position: 4
title: Bulletin and distribution
---

# Bulletin and AMHS-oriented output

[`gifts/common/bulletin.py`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/gifts/common/bulletin.py) implements the in-memory **Meteorological Bulletin** wrapper around one or more IWXXM XML roots.

## API (conceptual)

| Method / behavior | Role |
|-------------------|------|
| `set_bulletinIdentifier(**kwargs)` | Builds internal bulletin id from AHL-derived fields (`A_`, `tt`, `aaii`, `cccc`, `yygg`, `bbb`, …) |
| `append(element)` | Add an IWXXM `xml.etree.ElementTree.Element`; children must be homogeneous |
| `write(path=..., compress=False)` | Serialize `<MeteorologicalBulletin>`; **`compress=True`** emits gzip suitable for AMHS file transfer (see [root README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/README.md)) |
| `__iter__` / indexing | Access individual report elements |

## Data flow

```mermaid
flowchart LR
  enc[gifts_Encoder_encode]
  bull[bulletin_Bulletin]
  file[XML_or_gzip_file]

  enc --> bull
  bull --> file
```

## See also

- [Library encode workflow](../workflows/library-encode)
- [Demo GUI](../workflows/demo-gui) — `bulletin.write()` after encode
