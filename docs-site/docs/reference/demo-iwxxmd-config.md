---
sidebar_position: 5
title: iwxxmd.cfg reference
---

# `iwxxmd.cfg` sections

The file watcher daemon [`iwxxmd.py`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/demo/iwxxmd.py) reads an INI-style config (see sample [`iwxxmd.cfg`](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/demo/iwxxmd.cfg)). Canonical behavior and log patterns: [demo/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/demo/README.md).

## `[internals]`

| Key | Meaning |
|-----|---------|
| `product` | One of **`metar`** (includes SPECI), **`taf`**, **`vaa`**, **`tca`**, **`swa`** |
| `delete_after_read` | If true, remove each TAC file from the input directory after it is read |
| `wmo_ahl_line` | If true, first line of each output file is the WMO AHL and extension is **`.txt`**; if false, output is **`.xml`** without the AHL line |
| `geo_locations_file` | Path to pickled ICAO → aerodrome map; **required for `metar` / `taf`**, ignored (may be empty) for other products |

## `[directories]`

| Key | Meaning |
|-----|---------|
| `input` | Directory to watch for incoming TAC (must **pre-exist**) |
| `output` | Where `MeteorologicalBulletin` files are written (must **pre-exist**) |
| `logs` | Log output directory (must **pre-exist**) |

## Runtime notes

- Requires **`pip install watchdog`**.
- **`kill -USR1`** toggles DEBUG logging (see demo README).
- Sample bulk TAC files under `demo/` (`metars.txt`, `tafs.txt`, `tca.txt`, `vaa.txt`) illustrate expected shapes for the GUI and regex wiring.

## See also

- [IWXXMD daemon workflow](../workflows/iwxxmd-daemon)
- [Demo GUI workflow](../workflows/demo-gui)
- [Demo architecture](../architecture/demo-modules)
