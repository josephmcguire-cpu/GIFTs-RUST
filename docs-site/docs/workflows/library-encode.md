---
sidebar_position: 10
title: Library encode workflow
---

# Library encode workflow

End-to-end data flow when using the **`gifts`** package programmatically (any product encoder: METAR, TAF, TCA, VAA, SWA).

## Steps

1. Build **full message text**: WMO AHL line + TAC body (and further TACs if the product regex allows multiples).
2. Instantiate the product **`Encoder`** (e.g. `gifts.METAR.Encoder(geoLocationsDB)`).
3. Call **`encode(text, receiptTime=None, **attrs)`**:
   - Parses AHL via `re_AHL`; on failure, returns an **empty** `Bulletin`.
   - Sets bulletin identifier from AHL groups + product `T1T2`.
   - For each TAC match from `re_TAC`: **decode** → optional geo enrichment → **encode** to IWXXM `Element`; append successes to the bulletin.
4. Consume **`Bulletin`**: iterate XML roots, inspect, or call **`write()`** / **`write(compress=True)`**.

## Data flow

```mermaid
flowchart TD
  msg[messageText_AHL_plus_TAC]
  enc[product_Encoder]
  ahl[re_AHL_match]
  bid[set_bulletinIdentifier]
  loop[for_each_TAC_match]
  dec[decoder_tac]
  geo[optional_geoLocationsDB]
  iwxxm[encoder_decoded_tac]
  bull[bulletin_Bulletin]
  out[write_MeteorologicalBulletin]

  msg --> enc
  enc --> ahl
  ahl --> bid
  bid --> loop
  loop --> dec
  dec --> geo
  geo --> iwxxm
  iwxxm --> bull
  bull --> out
```

## Related architecture

- [gifts modules](../architecture/gifts-modules) — module layout and `Encoder` hierarchy.
- [METAR pipeline](../architecture/metar-pipeline) — detailed METAR decode/encode chain.
