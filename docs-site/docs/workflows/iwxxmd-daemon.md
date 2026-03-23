---
sidebar_position: 12
title: iwxxmd daemon workflow
---

# `iwxxmd` daemon workflow

`demo/iwxxmd.py` watches an **input** directory with **watchdog**, encodes arriving TAC files with a configured product encoder, and writes results to an **output** directory. Logging rotates by day-of-week (`demo/README`).

## Process flow

```mermaid
flowchart TD
  cfg[read_config_file]
  start[spawn_watchdog_observer]
  wait[wait_for_file_events]
  parse[read_TAC_validate_shape]
  encode[product_Encoder_encode]
  write[write_output_xml_or_txt]
  log[append_product_log]
  cfg --> start
  start --> wait
  wait --> parse
  parse --> encode
  encode --> write
  write --> log
  log --> wait
```

## Operator signals

- **`kill -USR1 <pid>`** toggles DEBUG logging (`demo/README`).

## Optional state view

```mermaid
stateDiagram-v2
  [*] --> idle: observer_running
  idle --> processing: file_detected
  processing --> idle: encode_complete
  idle --> idle: USR1_toggles_debug
```

## Related docs

- [Demo modules](../architecture/demo-modules)
- Canonical behavior: [demo/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/demo/README.md)
