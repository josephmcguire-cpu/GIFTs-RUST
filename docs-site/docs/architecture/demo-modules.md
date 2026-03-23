---
sidebar_position: 24
title: demo package modules
---

# `demo` directory modules

Applications that **drive** `gifts` encoders: a **Tk** GUI and a **watchdog** daemon. They are not installed as the `gifts` package itself but live alongside it in the monorepo.

## Component boundaries

```mermaid
flowchart TB
  subgraph gui_app [demo1_py]
    tk[Tk_widgets]
    logh[TextHandler_logging]
    pick[file_dialog]
  end

  subgraph daemon_app [iwxxmd_py]
    cfg[config_parser]
    obs[watchdog_observer]
  end

  subgraph lib [gifts_library]
    encoders[METAR_TAF_TCA_VAA_Encoder_instances]
  end

  pick --> encoders
  tk --> logh
  gui_app --> encoders
  daemon_app --> encoders
```

## GUI vs library responsibilities

| Layer | Responsibility |
|-------|----------------|
| `simpleGUI` / Tk | File selection, user feedback, triggering encode |
| `gifts.*.Encoder` | AHL/TAC parsing, IWXXM generation |
| `Bulletin.write` | Meteorological bulletin file on disk |

## User journey (cross-link)

The operator-facing steps are diagrammed in [Demo GUI workflow](../workflows/demo-gui).

## Class sketch (GUI)

```mermaid
classDiagram
  class simpleGUI {
    +window_Tk
    +encoders_list
    +encode(event)
    +open_file(event)
    +clear_fields()
  }

  class TextHandler {
    +emit(record)
  }

  class Logger {
  }

  simpleGUI --> TextHandler : adds_handler
  TextHandler --> Logger : formats_records
```

## Related

- [iwxxmd daemon workflow](../workflows/iwxxmd-daemon)
- [demo/README](https://github.com/josephmcguire-cpu/GIFTs-RUST/blob/main/demo/README.md)
