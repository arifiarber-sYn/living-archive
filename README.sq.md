# Arkivi i Gjallë — hackathon 24h (26.09.2026)

Sistem agjentik për një organizatë të vogël: gëlltit një korpus dokumentesh,
përgjigjet me **citime të verifikueshme**, thotë **“s’e di”** kur s’ka bazë, **mat veten** dhe
**mëson nga feedback-u** i përdoruesit. Gjithçka **lokale** (ollama, pa API të jashtme).

## Si niset (i huaj, nën 10 minuta)
```bash
# 0) shkarko dy modelet lokale (të dyja publike, një komandë secila)
ollama pull nomic-embed-text   # embedimet (default; ndrysho me ARK_EMB)
ollama pull qwen3:4b           # modeli bisedues (default ARK_LLM; çdo model lokal punon)

# 1) korpusi: vendos skedarët (tekst ose PDF) te korpus/ (deshi NUK është në repo)
mkdir -p korpus && cp skedaret/* korpus/

# 2) indekson + shkruan raportin “çka kuptova e çka jo”
#    dështon me zë (exit ≠ 0) nëse endpoint-i i embedimeve bie ose kthen vektor bosh
python3 app/arkivi.py gelltit

# 3) UI: http://127.0.0.1:8903 — ekzekuton edhe lakun agjentik të gëlltitjes
#    (vezhgo → vendos → indekso → raporto, progres live për dokument)
python3 app/ui.py
```
Varësitë: `pdftotext` (PDF-të), `ollama` me `nomic-embed-text` dhe një model
bisedues lokal (default `qwen3:4b`; ndrysho me variablin `ARK_LLM`).

**Shënim korpusi:** korpusi i 50 dokumenteve adversar (përdorur për rezultatet
e matura) **nuk** është në këtë repo — është artikull privat vlerësimi, i
mbajtur me `MANIFEST.sha256` (verifikim me hash). `korpus-test/` ka një korpus
 të vogël 6-skedarësh që ta provosh pipeline-in menjëherë.

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
