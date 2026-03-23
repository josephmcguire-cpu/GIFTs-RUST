---
sidebar_position: 21
title: gifts package modules
---

# `gifts` package modules

## Package and file map

```mermaid
flowchart TB
  subgraph common_mod [gifts_common]
    Encoder_py[Encoder_py]
    bulletin_py[bulletin_py]
    xmlConfig_py[xmlConfig_py]
    xmlUtilities_py[xmlUtilities_py]
    Common_py[Common_py]
    tpg_py[tpg_py]
  end

  subgraph products [product_packages]
    METAR[METAR_py]
    TAF[TAF_py]
    TCA[TCA_py]
    VAA[VAA_py]
    SWA[SWA_py]
  end

  subgraph decenc [decoders_and_encoders]
    md[metarDecoder_metarEncoder]
    td[tafDecoder_tafEncoder]
    tcd[tcaDecoder_tcaEncoder]
    vd[vaaDecoder_vaaEncoder]
    sd[swaDecoder_swaEncoder]
  end

  subgraph support [supporting]
    sky[skyfield_support_py]
    gdb[gifts_database]
  end

  products --> common_mod
  METAR --> md
  TAF --> td
  TCA --> tcd
  VAA --> vd
  SWA --> sd
  Encoder_py --> products
```

## Encoder class pattern

Each product defines **`class Encoder(E.Encoder)`** with:

- `re_AHL`, `re_TAC`, `T1T2`
- `decoder` — typically `Annex3()` instance from `*Decoder`
- `encoder` — typically `Annex3()` from `*Encoder`
- `geoLocationsDB` where aerodrome metadata is required (METAR/TAF)

```mermaid
classDiagram
  class EncoderBase {
    +geoLocationsDB
    +re_AHL
    +re_TAC
    +T1T2
    +decoder
    +encoder
    +encode(text, receiptTime, **attrs) Bulletin
    +iter_encode_stages(text, receiptTime, **attrs)
  }

  class MetarEncoder {
    +METAR_AHL_and_TAC_patterns
  }

  class TafEncoder {
    +TAF_patterns
  }

  class TcaEncoder {
    +TCA_patterns
  }

  class VaaEncoder {
    +VAA_patterns
  }

  class SwaEncoder {
    +SWA_patterns
  }

  class Bulletin {
    +set_bulletinIdentifier(**kwargs)
    +append(Element)
    +write(path, compress)
  }

  EncoderBase <|-- MetarEncoder
  EncoderBase <|-- TafEncoder
  EncoderBase <|-- TcaEncoder
  EncoderBase <|-- VaaEncoder
  EncoderBase <|-- SwaEncoder
  EncoderBase ..> Bulletin : builds
```

## Product family (compact)

Non-METAR products follow the **same abstract pipeline** as METAR (AHL → bulletin id → TAC iterations → decode → encode) with **different** regexes, decoders, and encoders. See [METAR pipeline](./metar-pipeline) for the fully expanded example and [gifts products](./gifts-products) for TAF/TCA/VAA/SWA wiring.

## See also

- [Dependency graphs](./dependency-graphs) — full `gifts` stack in context
