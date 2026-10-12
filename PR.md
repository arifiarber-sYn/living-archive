# PR: motori REJA — i njejti arkiv, dy motorë (Token Factory + NVIDIA Nemotron)

## Titulli i PR-se
`reja: motor cloud (Nebius Token Factory + NVIDIA Nemotron) me refuzim te verifikuar`

## Trupi

Ky PR shton **motorin e dyte** te Arkivit te Gjalle. Motori vendor (Ollama) mbetet parazgjedhja;
motori REJA perdor **Nebius Token Factory**: embedime `Qwen/Qwen3-Embedding-8B` dhe pergjigje
`nvidia/nemotron-3-super-120b-a12b`.

### Permbajtja
- `app/reja.py` — motor cloud: indeksim, kerkim, pergjigje me citim ose refuzim
- `app/harness_reja.py` — harness-i cloud (8 pyetje, metrika te matura)
- `app/kalibrim.py` — mjet kalibrimi (i perdorur, pastaj i rrezuar me prova)
- `Makefile` — nje skedar, dy motorë (`ARK_ENGINE=reja|vendor`)
- `docs/REJA.md`, `docs/HULUMTIMI-12-10.md`, `JOURNAL.md` — numrat, zbulimet, deshtimet e ruajtura
- `krahasimi-modele/` — Nano, Lightning, Super, te njejtat pyetje

### Numrat (te matur, jo te vleresuar)
| Metrika | Vlera |
|---|---|
| Pyetje me citim te verifikueshem (korpus shembull) | 8/8 (100%) |
| Pyetje kurthi te refuzuara | 3/3 |
| Latenca p50 | 1.91 s |
| Kosto per pyetje | $0.000041 |
| Krahasim modelesh | Super 8/8 · Nano 7/8 · Lightning 3/8 (+1 fabrikim) |

### Çka u rrezua dhe eshte ruajtur
1. Pragu absolut i ngjashmerise (ndarja 0.0003 ishte rastesi)
2. Bashkimi RRF semantik+leksikor (pa perfitim)
3. Kontrata e citimit e pershkruar me fjalë (modeli e leshon)
4. Reranker me LLM mbi 20 kandidate (pa perfitim)
5. HyDE (pa perfitim; parashikimi nuk doli)
6. Porta e refuzimit me gjyqtar te lire (10/13, nuk e rregulloi rastin e synuar)

### Licenca
Repo-ja eshte MIT; ky PR nuk e ndryshon.

### Pa sekrete
Skanimi i degës: 0 gjetje. Çelesi lexohet nga `NEBIUS_API_KEY` ose nje skedar lokal 0600.

---
## Shenim i gjendjes
- Dega `reja-motor` eshte lokale; shtytja **nuk u krye** sepse porta e publikimit kerkon PO (halim_guard: `act_if_preapproved`).
- Ky skedar eshte pergatitja; shtytja behet me nje komande pas aprovimit.
