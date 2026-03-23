---
sidebar_position: 22
title: METAR decode and encode pipeline
---

# METAR decode and encode pipeline

Worked example for **METAR/SPECI**: `gifts.METAR.Encoder` wires **`metarDecoder.Annex3`** and **`metarEncoder.Annex3`** through `gifts.common.Encoder.Encoder`.

## Conceptual decode pipeline

The decoder turns a **TAC substring** into a **nested dict** (groups such as `ident`, `itime`, `wind`, `vsby`, trends, etc.). On failure it may attach **`err_msg`**; the base encoder may skip IWXXM generation when `TRANSLATOR` is false.

```mermaid
flowchart TD
  tac[METAR_TAC_substring]
  dec[metarDecoder_Annex3]
  tokens[parse_Annex3_tokens]
  tree[decoded_dict_ident_itime_groups]
  err{err_msg_present}

  tac --> dec
  dec --> tokens
  tokens --> tree
  tree --> err
```

## Conceptual encode pipeline

The encoder consumes the **decoded dict** and original **TAC string** to emit an **`xml.etree.ElementTree.Element`** IWXXM root.

```mermaid
flowchart TD
  d[decoded_dict]
  t[original_TAC]
  enc[metarEncoder_Annex3]
  elem[IWXXM_Element_root]

  d --> enc
  t --> enc
  enc --> elem
```

## Sequence: `METAR.Encoder.encode`

```mermaid
sequenceDiagram
  participant Caller
  participant MetarEnc as METAR_Encoder
  participant Base as common_Encoder
  participant Bull as Bulletin
  participant Dec as metarDecoder_Annex3
  participant Enc as metarEncoder_Annex3

  Caller->>MetarEnc: encode(text)
  MetarEnc->>Base: re_AHL_search
  Base->>Bull: set_bulletinIdentifier
  loop each_TAC_match
    Base->>Dec: decoder(tac)
    Dec-->>Base: decoded_dict
    opt geoLocationsDB
      Base->>Base: enrich_ident_metadata
    end
    Base->>Enc: encoder(decoded_dict, tac)
    Enc-->>Base: Element_or_SyntaxError
    Base->>Bull: append(Element)
  end
  MetarEnc-->>Caller: Bulletin
```

## Related

- [Library encode workflow](../workflows/library-encode)
- Source: `gifts/METAR.py`, `gifts/metarDecoder.py`, `gifts/metarEncoder.py`, `gifts/common/Encoder.py`
