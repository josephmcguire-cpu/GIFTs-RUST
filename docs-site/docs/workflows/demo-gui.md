---
sidebar_position: 11
title: Demo GUI workflow
---

# Demo GUI workflow (`demo1.py`)

`demo1.py` is a **Tkinter** demonstrator: pick a TAC file, run the matching GIFTs encoder, show **activity messages**, and write a **Meteorological Bulletin** beside the demo.

## User journey

```mermaid
flowchart TD
  start([Operator_starts_demo1])
  pick[Click_TAC_File_choose_path]
  gen[Click_Generate_IWXXM_From_TAC]
  match[Scan_AHL_regex_list]
  enc[Selected_Encoder_encode]
  log[Logger_to_scrolled_text_and_demo_log]
  write[bulletin_write_output_file]
  show[Show_internal_bulletin_id_in_XML_field]
  start --> pick
  pick --> gen
  gen --> match
  match --> enc
  enc --> log
  log --> write
  write --> show
```

## Data flow (same scenario, artifact view)

```mermaid
flowchart LR
  file[tac_file_on_disk]
  read[read_full_text]
  slice[substring_from_AHL_match]
  gifts[gifts_METAR_TAF_TCA_VAA_Encoder]
  bull[bulletin_Bulletin]
  fs[MeteorologicalBulletin_file]

  file --> read
  read --> slice
  slice --> gifts
  gifts --> bull
  bull --> fs
```

## Notes

- **Geo database**: unpickles `aerodromes.db` (Unix-like) or `aerodromes.win.db` (Windows) before building encoders that need it.
- **Encoder selection**: ordered list of `(regexp, Encoder)`; first AHL match wins (`demo1.py`).
- **Logging**: `logging` goes to **`demo.log`** and to the **Activity Msgs** `ScrolledText` via a custom `TextHandler`.
- **Output name**: `bulletin.write()` uses internal bulletin id (see `Bulletin` implementation); the GUI displays `bulletin._internalBulletinId` in the **IWXXM XML File** field.

See [Demo modules](../architecture/demo-modules) for component boundaries.
