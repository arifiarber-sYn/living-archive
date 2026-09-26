# Arkivi i Gjallë — hackathon 24h (26.09.2026)

Sistem agjentik për një organizatë të vogël: gëlltit një korpus dokumentesh,
përgjigjet me **citime të verifikueshme**, thotë **“s’e di”** kur s’ka bazë, **mat veten** dhe
**mëson nga feedback-u** i përdoruesit. Gjithçka **lokale** (ollama, pa API të jashtme).

## Si niset (i huaj, nën 10 minuta)
```bash
# 1) korpusi: vendos skedarët (tekst ose PDF) te korpus/
python3 app/arkivi.py gelltit      # indekson + shkruan raportin “çka kuptova e çka jo”
python3 app/ui.py                  # UI: http://127.0.0.1:8903
```
Varësitë: `pdftotext` (PDF-të), `ollama` me `nomic-embed-text` dhe `qwen3.8-liruar:latest`.

## Korpusi i vërtët (i verifikuar)
`korpus/` = 50 dokumente · 42 txt, 4 md, 3 PDF · shqip + një gjermanisht.
Burimi: `MANIFEST.sha256` (hash i verifikuar + kontroll skedar-për-skedar) + `LEXOME-KORPUSI.md`.
Përmban **qëllimisht** raste të vështira: skedar bosh, dyfishime, procesverbale që kundërshtojnë, gjuhë tjetër.
Korpus i pastër demoje: komunë **fiktive** (asnjë entitet real) + artikuj Wikipedia (CC BY-SA).

## Si punon
1. **Gëlltitja** — për çdo skedar: lexo (PDF me `pdftotext`) → copëto → embedo → ruaj;
   raporti shënon dokumentet që **nuk** u kuptuan (p.sh. PDF të skanuar — pa tekst të nxjerrshëm).
2. **Përgjigjja** — embedo pyetjen → kërko 5 copat më të ngjashme → LLM lokal përgjigjet
   **vetëm nga fragmentet** dhe citon `[id]`; nëse fragmentet s’e mbulojnë → `S E DI` (pa trillim).
3. **Citime** — çdo citim është i klikueshëm te UI dhe hap fragmentin e vërtetë (një klikim).

## Gjendja e provuar (kohë reale, nga `date`)
- **Nisja e garës:** 2026-09-26 09:57:30 CEST
- **Rruga e demos punon:** 09:58:55 — pyetje me citim të saktë `[d4-0]` → *“18,300,000 euro”* ✓
  dhe pyetje pa bazë → *“S E DI”* ✓
- **Gëlltitja mbi 6 dokumente** (4 tekst + 1 PDF i lexueshëm + 1 PDF i skanuar) → 5 copa;
  raporti: 5×“po”, 1×“JO” (PDF-ja e skanuar) ✓

## Të mbetura (blloqet 2–4)
- Laku agjentik i gëlltitjes **i dukshëm në UI** (vëzhgo→vendos→indekso→raporto, me progres për dokument).
- Harness i vetë-vlerësimit (≥15 pyetje-etalon) + normë e “S E DI” të gabuar—të dukshme në UI.
- Mësimi nga feedback-u: përgjigjet e vlerësuara “gabim” ndikojnë pyetjet e ngjashme.
- Demo publike (funnel) + video ≤2 min + pitch 3-min.
