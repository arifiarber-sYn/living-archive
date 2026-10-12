# Motori REJA — i njejti arkiv, i njejti premtim, tjeter motor

> Dega lokale `reja-motor`. **Nuk eshte shtyre** ne GitHub — pret vendimin (A/B/C te
> `VENDIM-REPO-NEBIUS.md`).

## Cka eshte
Arkivi i Gjalle punon lokale (Ollama). Ky shtese shton nje motor te dyte qe perdor
**Nebius Token Factory**: embedime `Qwen/Qwen3-Embedding-8B` dhe pergjigje
`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`. Premtimi s'ndryshon: *pergjigja OSE citon,
OSE refuzon.*

```bash
export NEBIUS_API_KEY=***          # ose celesi lokal (0600)
cp korpus-test/* korpus/            # korpus shembulli
python3 app/reja.py gelltit         # indeksim me Token Factory
python3 app/reja.py pyet "pyetja"
python3 app/reja.py kosto           # kosto e grumbulluar, nga përdorimi real
```

## Numrat e këtij raundi (12.10.2026)
| Cka | Vlera | Burimi |
|---|---|---|
| Indeksimi i korpusit shembull (6 skedare) | 5 njesi, **611 token-a** | `indeksi/reja.json` |
| Harness cloud (5 pyetje me baze + 3 pa baze) | **8/8 = 100%**, refuzime **3/3** | `indeksi/harness-reja.json` |
| Latence p50 | **1.91 s** | idem |
| Kosto mesatare per pyetje | **$0.000041** | idem |

> **Parazgjedhja kaloi ne `nvidia/nemotron-3-super-120b-a12b` (12.10.2026)**, pas krahasimit:
> Super **8/8**, Nano 7/8, Lightning **3/8 me nje fabrikim**. Super, edhe pse 5x me i shtrenjte per
> token, doli **me i lirе per pyetje** se Nano (pergjigje me te shkurtra). Krahasimi i plote:
> `docs/HULUMTIMI-12-10.md` + `krahasimi-modele/`.
>
> Numrat e meparshem (Nano): 7/8, p50 3.11 s, $0.000057/pyetje — te ruajtura ne
> `krahasimi-modele/nano.json`.
| Pyetje jashte teme | refuzim, **$0.0** (pa thirrje modeli) | idem |

## Tri rrezimet e radhes (secila e matur)

**1. Pragut (0.373) — i rrezuar.** Ndarja 0.0003 ishte rastesi; `grep -c taksa` = 0 ne fragmentin
"fitues". Similituda mat tematiken, jo pergjigjen → u zevendesua me dysheme sigurie + verifikim.

**2. Kontrata e citimit — e rrezuar si besim ndaj modelit.** Me nje prompt qe *pershkruante*
kllapat, modeli u pergjigj saktë (142,500,000 euro) por **pa citim** → 3/8. Me nje shembull
konkret ne prompt: 4/8. Modeli e le kllapen kur pergjigja zgjatet.

**3. Citimi u LLOGARIT, nuk u besua (zgjidhja).** `atribuo_citime()` nuk i beson modelit:
merr numrat qe shfaqen ne pergjigje dhe kerkon fragmentin qe i permban te gjithe. Kjo e coi
**3/8 → 7/8 (87.5%)**, pa nje cent shtese.

> Parimi: **citimi eshte deshmi e verifikuar, jo deklaratë e modelit.**

Rasti i vetem i mbetur (b5) eshte kufizim i vleresimit tim: kerkoj numrin e vendimit (118)
ne pergjigje, ndersa fragmenti i cituar s'e permbante ate shifer.

## Zbulimi kryesor i raundit: ngjashmeria NUK eshte provë
Kalibrimi (`app/kalibrim.py`) dha nje ndarje qe dukej e paster:
me i larti *pa mbulim* **0.3733** vs me i uleti *me mbulim* **0.3736** — diference 0.0003.

**Por ndarja ishte e rreme.** Pyetja "me e sigurt" (taksat) shënon 0.37 si *ngjashmeri tematike*,
ndersa fragmenti i gjetur (`vendim-buxheti-2027.txt`) **nuk permban asnje shifer takse**
(`grep -c taksa` = 0). Similituda kosine mat *tematiken*, jo *pergjigjen*.

### Pasoja per dizajnin (e zbatuar, jo e propozuar)
Refuzimi s'vendoset me nje prag te vetem. Dy shtresa:
1. **Dysheme sigurie** (`PRAG_MIN=0.30`) — poshte saj, refuzim pa thirrje modeli (kosto zero).
2. **Verifikim i citimit** — nese pergjigja s'mban nje id te fragmentit te gjetur, hidhet poshte
   dhe kthehet `S'E DI`. Kjo s'mund te kalohet duke u dukur i sigurt.

Kjo e kap rastin me te rrezikshem: pergjigje e rrjedhshme, pa baze.

## Çka mbetet e hapur
- Bashkimi nuk eshte shtyre; README-ja anglisht dhe shqip s'eshte perditesuar ende me kete motor.
- Arkivi privat (387 njesi) **nuk** kalon ne publik: 514 rreshta me emra, IP e shtigje.
- Kalibrimi duhet perseritur mbi nje korpus ku *dihet* se cila pyetje mbulohët — jo mbi hamendje.
