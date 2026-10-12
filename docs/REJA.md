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
| Pyetje e vertete (taksat) | refuzim **i sakte**, kosto $0.00014 | `indeksi/reja-kosto.jsonl` |
| Pyetje jashte teme | refuzim, **$0.0** (pa thirrje modeli) | idem |

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
