# Demo transcript — public corpus (Python PEPs), real calls (13.10.2026 13:4x, `ARK_ARKIVA=arkiva-peps ARK_PORT=8125 make demo`)

Recorded with `curl` against `src/server.py` over `arkiva-peps/`; model `nvidia/nemotron-3-super-120b-a12b` on **Nebius Token Factory**. Nothing edited except truncating the long answer. `/kosto` here reflects `harness/report-peps.json`.

## 1. An answerable question → answer **with citation**, and the citation is a file you can open
```bash
curl -s "http://127.0.0.1:8125/pyet?q=Which+PEP+added+assignment+expressions%2C+the+walrus+operator%3F"
```
```json
{
  "pergjigja": "PEP 572 introduced assignment expressions, commonly known as the walrus operator. [pep-0572]",
  "citime": [
    "pep-0572"
  ],
  "refuzim": false,
  "semantike": true,
  "sekonda": 2.087,
  "hyr": 2393,
  "dal": 28,
  "kosto_usd": 0.0007431,
  "gjetjet": [
    "pep-0572",
    "pep-0379",
    "pep-0577",
    "pep-0203",
    "pep-0532",
    "pep-0308"
  ],
  "skoret": [
    0.7495,
    0.7362,
    0.6918
  ],
  "prova_citimi": 0,
  "njesi_arkive": 745
}
```
```bash
curl -s http://127.0.0.1:8125/njesi/pep-0572 | head -12
```
```
---
id: pep-0572
burimi: https://peps.python.org/pep-0572/
licenca: Public domain (per the PEP copyright section)
titulli: Assignment Expressions
statusi: Final
lloji: Standards Track
krijuar: 28-Feb-2018
shkurtuar: po
---
# PEP 572 — Assignment Expressions (Status: Final · Type: Standards Track · Created: 28-Feb-2018)

```

## 2. A PEP that does not exist → the model is asked and says *I don't know*; an off-domain question → refused **before** the model (cost $0)
```bash
curl -s "http://127.0.0.1:8125/pyet?q=What+does+PEP+9999+propose%3F" ; curl -s "http://127.0.0.1:8125/pyet?q=What+is+the+classic+recipe+for+Albanian+byrek+with+spinach%3F"
```
```json
{
  "pergjigja": "I don't know.",
  "citime": [],
  "refuzim": true,
  "sekonda": 2.063,
  "kosto_usd": 0.0007422,
  "gjetjet": [
    "pep-0001",
    "pep-0009",
    "pep-0012",
    "pep-0042",
    "pep-8001",
    "pep-0676"
  ]
}
{
  "pergjigja": "I don't know — no archive entry passes the evidence threshold.",
  "citime": [],
  "refuzim": true,
  "sekonda": 1.7,
  "kosto_usd": 0.0,
  "hyr": 0,
  "dal": 0
}
```

## 3. The memory audit trail: what the agent remembered, when, in which commit
```bash
curl -s http://127.0.0.1:8125/historia | head -12
```
```json
{
  "arkiva": "arkiva-peps",
  "commits": [
    {
      "sha": "5c8424d",
      "data": "2026-10-13T12:12:31+02:00",
      "mesazhi": "remember: nebius-video-1"
    },
    {
      "sha": "1a29097",
      "data": "2026-10-13T11:46:51+02:00",
      "mesazhi": "Korpusi publik PEPs (H6): 744 njesi me burimi+licenca, kosto e matur para ($0.0055) dhe pas ($0.00548); harness peps 10/13, refuzime 4/4; ARK_ARKIVA/ARK_PYETJE/ARK_RAPORT; citime vetem per id te gjetura; 28 teste"
    }
  ]
}
```

## 4. Health + measured numbers (`harness/report-peps.json`)
```bash
curl -s http://127.0.0.1:8125/health ; curl -s http://127.0.0.1:8125/kosto
```
```json
{"status":"pass"}
{
  "shkalla": "2026-10-13",
  "modeli": "nvidia/nemotron-3-super-120b-a12b",
  "njesi_arkive": 744,
  "pyetje": 13,
  "sakte": 13,
  "sakte_pct": 100.0,
  "citim_sakte": 9,
  "refuzime_sakte": 4,
  "refuzime_totale": 4,
  "latence_p50_s": 2.548,
  "kosto_totale_usd": 0.0088839,
  "kosto_mesatare_usd": 0.00068338,
  "arkiva": "744 units from arkiva-peps"
}
```
