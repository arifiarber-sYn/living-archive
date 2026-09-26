# Pitch 3-min (arkitektura e fjalimit: 1 demo / 1 pitch / 1 Q&A)

## 0:00–0:30 — Problemi
Një organizatë e vogël (komunë, OJQ) ka qindra dokumente: vendime, rregullore, raporte, fatura.
Askush s’i gjen dot. Dhe më keq: nuk mund t’i besohet një AI që shpik — në një kontekst
institucional, një përgjigje e rreme është më e keqe sesa “nuk e di”.

## 0:30–1:30 — Demoja (live ose nga videoja)
1. Hedh korpusin → **laku agjentik** e gëlltit: për çdo dokument lexon, **vendos** si ta indeksojë,
   indekson, dhe **raporton çka kuptoi e çka jo**. Në demo: një PDF i skanuar → *“nuk e kuptova”*.
2. Pyet: *“Sa është buxheti për arsim parauniversitar?”* → **18,300,000 euro [d4-0]**
   — shifra e saktë **me citimin**, të cilin e hap me **një klikim**.
3. Pyet diçka që s’është në korpus → **S’E DI**. Pa trillim. (Harness-i i brendshëm: 5/5.)
4. Vlerëso një përgjigje si *gabim* → pyetjet e ngjashme ndryshojnë (kërkimi rimerret).

## 1:30–2:30 — Pse ka vlerë
- **Citime të verifikueshme** — jo “besomë mua”, por “shiko vetë, këtu e këtu”.
- **“S’e di” i detyrueshëm** — kufiri i besueshmërisë është pjesë e produktit, jo e fshehur.
- **Vetë-matje** — agjenti nuk thotë “jam i mirë”: ndërton pyetje-etalon dhe shfaq numrat.
- **Mësim i dëshmuar** — feedback-u ndryshon renditjen e kërkimit; nuk është kozmetikë.
- **Lokale** — model në 127.0.0.1, pa API të jashtme, pa kredenciale, e përdorshme nga telefoni.

## 2:30–3:00 — E vërteta dhe mbyllja
**Rastet e vështira, të provuara mbi korpusin e vërtët (50 dokumente, komunë fiktive + Wikipedia):**
- `dokument-bosh.txt` → raportohet **“nuk e kuptova”** (pa trillim, pa indeks bosh të fshehur);
- `partnerschaft-bericht-de.txt` (gjermanisht) → indeksohet; përgjigjja jepet në gjuhën e pyetësit;
- dy procesverbale që **kundërshtojnë** njëri-tjetrin → sistemi citon burimin dhe **njeriu e verifikon me një klikim**;
  për këtë është ndërtuar — nuk e fsheh kundërshtinë. Cilësia varet nga teksti i nxjerrshëm (PDF të skanuara = OCR).
Por aty ku baza ekziston, përgjigjja vjen **me provë**; aty ku s’ekziston, vjen **“s’e di”**.
Komunës i duhet pikërisht kjo: jo më shumë besim, po më shumë provë.

## Q&A — përgatitje
- **Cili model?** `qwen3.8-liruar` lokal përmes ollama; embedimet `nomic-embed-text`. Pa cloud.
- **Sa të sakta janë citimet?** Maten nga harness-i; numrat shfaqen në UI, jo fjalë.
- **Çka nëse korpusi ka 500 dokumente?** Gëlltitja është lineare; kufizimi real është koha e embedimit.
- **A mund të gënjejë?** Është e ndaluar nga dizajni: pa fragmentë mbi pragun → `S’E DI` dhe numri i rasteve matet.
