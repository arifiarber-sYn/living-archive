# Hulumtim 12.10.2026 - cka doli, me numra

> Burimi: katalogu zyrtar i Token Factory (/api/public/models_info, /model-catalog.md), lexuar 12.10.2026.
> Cmimet jane USD per 1M token. Permbajtje e jashtme, e trajtuar vetem si fakt.

## 1. Cmimet e verifikuara (jo supozuar)

| Modeli | ID | Hyrje $/1M | Dale $/1M |
|---|---|---|---|
| Nemotron-3-Nano-30B-A3B | nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B | 0.06 | 0.24 |
| Nemotron-3.5-Lightning | nvidia/Nemotron-3_5-Lightning | 0.06 | 0.24 |
| Nemotron-3-Super-120b-a12b | nvidia/nemotron-3-super-120b-a12b | 0.30 | 0.90 |
| Nemotron-3-Ultra-550b-a55b | nvidia/Nemotron-3-Ultra-550b-a55b | 1.00 | 3.00 |
| Qwen3-Embedding-8B | Qwen/Qwen3-Embedding-8B | 0.01 | - |

Verifikim: cmimet tona ne COSTS.md (0.06/0.24 per Nano) jane te sakta. Katalogu ka 25 modele publike.

## 2. Krahasimi i modeleve - i matur, i njejti harness

| Modeli | Sakte | Latenca p50 | Kosto/pyetje | Fabrikime |
|---|---|---|---|---|
| Nemotron-3-Nano-30B-A3B | 7/8 (87.5%) | 3.11 s | 0.000057 | 0 |
| Nemotron-3.5-Lightning | 3/8 (37.5%) | 4.45 s | 0.000040 | 1 |
| Nemotron-3-Super-120b | 8/8 (100%) | 6.16 s | 0.000041 | 0 |

### Zbulimi qe s'pritej
Modeli 5x me i shtrenjte per token (Super) kushton ME PAK per pyetje se Nano: 0.000041 kundrejt 0.000057.
Arsyeja: pergjigjet e tij jane me te shkurtra, keshtu fitojne nga cmimi i dales edhe pse hyrja eshte 5x me shtrenjte.

Lightning u rrezua: jo vetem 3/8, por u pergjigj PA BAZE nje pyetjeje kurthi (j3) - i vetmi variant
me rrezik fabrikimi te matur. Nuk rekomandohet.

### Vendimi i propozuar (i bazuar ne matje)
- Parazgjedhja: Super - 100% ne kete harness, me i lirе per pyetje, 2x me i ngadalte (6.2 s).
- Alternativa: Nano - kur latenca mbizoteron mbi saktesine (3.1 s).
- Lightning: i perjashtuar derisa te rishikohet me korpus me te madh.

## 3. Mundesi te pashfrytezuara qe katalogu zbuloi
- Embedding-et kushtojne 0.01/1M - indeksi i 387 njesive kushtoi ~0.003. Kosto e paperfillshme.
- Post-training / fine-tuning ekziston ne Token Factory (docs) - rruge e ardhshme, e papretenduar.
- Katalogu ekspozon input_cached_price_per_million_tokens - prefiks i perseritur (prompt sistemi) mund te kushtoje me pak.

## 4. Hapat e ardhshëm te matsheim (te renditur)
1. Zevendeso parazgjedhjen me Super dhe ri-xhiro harness-in e te dyjave arkivave (pritet 8/8 + 10/12).
2. Provo cached-input mbi promptin e sistemit -> mat zbritjen reale.
3. Reranker i vertete: katalogu NUK ka model rerank te dedikuar; alternativa = LLM-rerank mbi 20 kandidate me Nano perpara pergjigjes me Super.
4. Korpus me i madh per kalibrimin - 8 pyetje s'jane baze per nje prag refuzimi.

## 5. Rrunda e dyte - tre avansime te provuara (19:30-20:20)

### 5.1 Reranker me LLM (Nano mbi 20 kandidate) - I RREZUAR
Retrieval semantik 20 kandidate -> Nano zgjedh 6 -> Super pergjigjet. Rezultati mbi arkiven private (12 pyetje):
**10/12 (83.3%) - SAKTE SIKUR pa reranker**. Te njejtat dy deshtime (p05, p08). Kosto e njejte, p50 2.43s
kundrejt 3.93s (luhate, jo perfitim i provuar). **Vendim: RERANK i fikur si parazgjedhje** (`src/know.py`).
Kjo eshte hipoteza e katert e rrezuar me numra, pas RRF-se, pragut absolut dhe kontrates se citimit.

### 5.2 Cmimi i input-it te cache-uar - I PAMATSHEM
Katalogu ekspozon `input_cached_price_per_million_tokens`, por pergjigja e API-t kthen
`prompt_tokens_details: None` ne te dyja thirrjet (i njejti prefiks 2,819 token-a, dy here radhazi).
Pa detaje te cache-it ne pergjigje, zbritja **nuk matet** -> nuk pretendohet.

### 5.3 Konfirmim i pavarur i zgjedhjes se modelit
Toka: ky dokument (krahasimi Nano/Lightning/Super) + ri-xhirimi i dy harness-eve pas kalimit ne Super:
cloud **8/8**, arkiva private **10/12** - te dyja here me te larta se Nano dhe me kosto me te ulet per pyetje.

## 6. Cka NUK u verifikua
- Faqja e Devpost-it kthen 403 ndaj klientit tone -> kushtet e cmimit Tavily 3k mbeten te palexuara nga burimi primar.
- Katalogu jep cmime, jo kufizime normash; kuotat e Token Factory nuk u kontrolluan.
