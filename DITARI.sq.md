# DITARI — Arkivi i Gjalle (24h, nisja 2026-09-26 09:57:44)
- **Hash i verifikuar:** 5542824482c55ec6c4fc6fb38f5c8d923ee32ecfaaba75e6db44f0fc15e51240 ✓
- **Rregullat:** L-131 aktiv ✓; L-132 (cdo ore nga `date`) ✓; rregulli 10-min me perjashtimin e te pakthyeshmeve ✓.
- **Ndalimi i prere:** e diel 27.09 10:00 — por dorezohet sapo mbaron.
- **Dorezimi:** repo + video ≤2 min + pitch 3-min + ky ditar (shkeljet e L-131 + minutat zero→demo e pare).

## Plani i blloqeve dhe pushimeve (qendrueshmeria)
- **Blloku 1:** gelltitja + indeksimi + raporti "cka kuptova" → rruga e demos me korpus provash.
- *Pushim i vertete (largohem nga tavolina).*
- **Blloku 2:** pergjigjet + citimet + rregulli "s e di".
- *Pushim.*
- **Blloku 3:** harness-i i vete-vleresimit + mesimi nga feedback-u.
- *Pushim.*
- **Blloku 4:** UI + demo publike + videoja + pitch-i + README.
- **Checkpoint ne fund te cdo blloku:** gjendja shkruhet ne repo (konteksti mund te humbe, puna jo).

| Ora (date) | Cka ndodhi | Shkelje L-131? |
|---|---|---|
| 2026-09-26 09:57:44 | Hash i verifikuar; problemi lexuar; arena + plani i blloqeve. | jo |
| 09:59:06 | RRUGA E DEMOS PUNON: gelltitje (4 dok -> 4 copa), pyetje me citim te sakte [d4-0], dhe "S E DI" per pyetje pa baze. UI u ngrit. | jo |
| 09:59:33 | PDF-te: nje i lexueshem (libreoffice) + nje i skanuar/bosh -> raporti "kuptova: JO" per te dyftin. Gelltitja mbi 5 dokumente. | jo |
| 10:00:45 | Blloku 2: laku agjentik i gelltitjes u ndertua dhe u lidh ne UI (butoni + tabela live + vendimi per çdo dokument). U nis nga UI. | jo |
| 10:02:04 | Blloku 3: harness-i i vete-vleresimit (>=15 pyetje te ndertuara vetë + 5 pa baze) u nis; metrikat: saktesia e citimeve, S E DI e gabuar, trillimi. | jo |
| 10:06:25 | Blloku 4: demo publike e provuar (HTTP 200) dhe e shuar; teardown i verifikuar nga te dyja anet (konfig bosh + URL 000). | jo |
| 10:06:25 | BUG i gjetur duke shikuar faqen: tuple-index i gabuar ne kodin e boost-it -> vije e kuqe ne UI. Rregulluar. (Vlera e ta shohesh me sy.) | jo |
| 10:06:25 | VIDEO: 3 kuadro + narracion shqip (Piper) -> ffprobe 49.600000 s (matur). | jo |
| 10:06:25 | Dorezimi: repo + video + PITCH 3-min + README + ditar. | jo |

## Matjet (E-44)
- **Minuta 00:00 -> demo e pare qe punon: ~1.5** (nisja 09:57:30 -> pyetja me citim 09:58:55).
- **Shkelje L-131: 0** (nderhyrjet ishin funksion: bug-u i tuple-it, matja e harness-it, lidhja ne UI).
- **Koha: nga `date` ne çdo rresht** (L-132 i zbatuar plotesisht).
- **Bllok 1-2 u mbyllen brenda ~3.6 minutash**; videon/pitch-in/README i mbylli blloku 4.
| 10:07:10 | KORPUSI MBERRITI (50 skedare, hash i manifestit i verifikuar + kontroll skedar-per-skedar OK). U vendos ne arene dhe u nis gelltitja. | jo |
| 10:07:58 | KORPUSI I VERTETE: 50 dokumente -> 351 copa ne 7.52s (lak agjentik, nga UI). Nuk u kuptua: saktesisht 1 = dokument-bosh.txt (0 shkronja). | jo |
| 10:07:58 | Harness-i u nis mbi korpusin e vertete (tani arrin >=15 pyetje) + nje prove me 4 pyetje te veshtira (kundershti, gjermanisht, pa baze, buxheti). | jo |
| 10:07:58 | Pitch + README u mprehen me rastet konkrete te veshtira (bosh, gjermanisht, procesverbale qe kundershtojne). | jo |
| 10:08:15 | Provat mbi korpusin e vertete (4 pyetje te veshtira): buxheti 3.200.000 euro [d4-0] ✓; pyetje gjermanisht -> pergjigjje shqip me citim [d27-0] ✓; Mars -> S E DI ✓; kundershtia -> S E DI ✓. | jo |
| 10:08:57 | VIDEO FINALE me numrat e korpusit te vertete (3 kuadro: buxheti 3,200,000 [d4-0], dokumenti gjermanisht, S E DI) + narracion 43.05s -> ffprobe: duration=47.200000 | size=872173 | jo |
| 10:31:55 | EKSPERIMENT I MBYLLUR (me rezultat negativ, i ndershem): pragu 0.45->0.35 NUK ndryshoi asgje -> 8/15 sakte, 7 "S E DI" te gabuar, trillime 0. Pra refuzimet NUK vijne nga pragu, po nga gjykimi i modelit mbi fragmentet; diagnoza zbriti nje nivel. Pragu u kthye 0.45 (gjendja e verifikuar). | jo |
