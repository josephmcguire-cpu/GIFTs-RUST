"""Source definitions for testdata/pipeline goldens (regenerate via tools/freeze_pipeline_cases.py)."""

# Shared freeze time for stable decoder timestamps (translationTime, etc.)
DEFAULT_FREEZE_TIME = "2015-01-15T12:00:00Z"

GOLDEN_CASE_INPUTS = [
    {
        "case_id": "metar_biar",
        "product": "METAR",
        "freeze_time": DEFAULT_FREEZE_TIME,
        "notes": "METAR with geo DB; aligns with tests/e2e METAR smoke sample.",
        "input": """SAXX99 XXXX 151200
METAR BIAR 290000Z 33003KT 280V010 9999 OVC032 04/M00 Q1023=
""",
        "geo_db": {"BIAR": "AKUREYRI|AEY|AKI|65.67 -18.07 27"},
    },
    {
        "case_id": "taf_sbaf_nil",
        "product": "TAF",
        "freeze_time": DEFAULT_FREEZE_TIME,
        "notes": "NIL TAF with aerodrome geo metadata.",
        "input": """FTXX01 LFKJ 072000
TAF SBAF 072000Z NIL=
""",
        "geo_db": {"SBAF": "AFONSOS ARPT MI|||-22.87 -43.37"},
    },
    {
        "case_id": "tca_tokyo_exer",
        "product": "TCA",
        "freeze_time": DEFAULT_FREEZE_TIME,
        "notes": "TCA exercise advisory (from gifts/tests/test_tca_encoding.py).",
        "input": """FKPQ30 RJTD 111800
TC ADVISORY
STATUS:               EXER
DTG:                  20180911/1800Z
TCAC:                 TOKYO
TC:                   MANGKHUT
ADVISORY NR:          2018/19
OBS PSN:              11/1800Z N1400 E13725
CB:                   WI 180NM OF TC CENTRE TOP ABV FL450
MOV:                  W 12KT
INTST CHANGE:         INTSF
C:                    905HPA
MAX WIND:             110KT
FCST PSN +6 HR:       12/0000Z N1405 E13620
FCST MAX WIND +6 HR:  110KT
FCST PSN +12 HR:      12/0600Z N1420 E13510
FCST MAX WIND +12 HR: 110KT
FCST PSN +18 HR:      12/1200Z N1430 E134
FCST MAX WIND +18 HR: 110KT
FCST PSN +24 HR:      12/1800Z N1450 E13250
FCST MAX WIND +24 HR: 110KT
RMK:                  NIL
NXT MSG:              BFR 20180912/0000Z=
""",
    },
    {
        "case_id": "vaa_exercise",
        "product": "VAA",
        "freeze_time": DEFAULT_FREEZE_TIME,
        "notes": "VAA exercise (from gifts/tests/test_vaa_encoding.py).",
        "input": """FVAU03 ADRM 150252
VA ADVISORY
STATUS: EXERCISE
DTG: 20251215/0000Z
VAAC: NONE
VOLCANO: UNKNOWN
PSN: UNKNOWN
AREA: UNKNOWN
SOURCE ELEV: UNKNOWN
ADVISORY NR: 0000/0
INFO SOURCE: NONE
ERUPTION DETAILS: NONE
EST VA DTG: NOT PROVIDED
EST VA CLD: NOT PROVIDED
FCST VA CLD +6HR: 15/0600ZNOT PROVIDED
FCST VA CLD +12HR: 15/1200Z NOT AVBL
FCST VA CLD +18HR: 15/1800Z NO VA EXP
RMK: NONE
NXT ADVISORY: NO FURTHER ADVISORIES""",
    },
    {
        "case_id": "swa_exercise",
        "product": "SWA",
        "freeze_time": DEFAULT_FREEZE_TIME,
        "notes": "SWA exercise (from gifts/tests/test_swa_encoding.py); uses skyfield daylight path.",
        "input": """FNXX01 KWNP 301202
SWX ADVISORY
STATUS:             EXERCISE
DTG:                20200430/1200Z
SWXC:               BOULDER
ADVISORY NR:        2020/1
SWX EFFECT:         HF COM MOD AND GNSS MOD
OBS SWX:            30/1200Z NO SWX EXP
FCST SWX +6 HR:     30/1800Z NOT AVBL
FCST SWX +12 HR:    01/0000Z NOT AVBL
FCST SWX +18 HR:    01/0600Z NO SWX EXP
FCST SWX +24 HR:    01/1200Z NO SWX EXP
RMK:                NIL
NXT ADVISORY:       NO FURTHER ADVISORIES=
""",
    },
]
