# Build journal — timestamped, git-tracked

> Auditable memory: every claim in the README has a row here, and every row has a commit.

| When (Europe/Belgrade) | What | Evidence |
|---|---|---|
| 2026-10-12 17:45 | Repo skeleton: README (4 judging criteria), Apache-2.0, Makefile, tests | `3ae44ef` |
| 2026-10-12 17:47 | Video capability **proved**: real screencast + `ffprobe` verification (h264+aac, ok:true) | `/tmp/video-prova.mp4` → `docs/agent/gara/` |
| 2026-10-12 17:52 | Demo URL opened (portal + token): `/health`, `/kosto` | `e2fe036` |
| 2026-10-12 17:53 | Tavily helper sketch (know layer, **fail-closed** without key) | `4f1cdb1` |
| 2026-10-12 17:54 | Real Token Factory measurements: p50 **0.608 s**, **$0.0000181**/call | `matje/prova-tani.json`, `e7125a5` |
| 2026-10-12 18:03 | Archive built: **387 real units** (decisions + lessons), secrets masked | `arkiva/`, `2a3f367` |
| 2026-10-12 18:04 | Baseline eval: **5/12 (41.7%)**; cross-lingual variant regressed to 4/12 — documented, not hidden | `harness/report.json`, `report-v2-perkthim.json` |
| 2026-10-12 18:10 | Embeddings (Qwen3-Embedding-8B, 387 units, dim 4096, 291k tokens, one-off) | `src/embeddings.py` |
| 2026-10-12 18:11 | Semantic eval: **9/12 (75%)**, refusals **3/3** | `harness/report-v3-semantik.json`, `22f4a81` |
| 2026-10-12 18:12 | Real demo: `/pyet` answers with citations or refuses | `4737800` |
| 2026-10-12 18:14 | README filled with real numbers; `JOURNAL.md`, `COSTS.md`; `make run` verified from a clean checkout | `9fb025c` |
| 2026-10-12 18:24 | v4 failed: RRF fusion + forced citation retry gave **the same 9/12** at 4× latency and +38% cost → both switches default **off** | `harness/report-v4-hibrid.json`, `09d1957` |
| 2026-10-13 11:2x | Blind jury (8 LLM judges, Nebius rubric) on `ee1ad42`: **66.2/100**; weakest = Impact (sample, author-only corpus, inconsistent 12-vs-13 numbers) | `openclaw-knowledge/docs/agent/gara/JURIA-NEBIUS-13-10.md` |
| 2026-10-13 11:3x | Tests: 1 → **23** (archive integrity, BM25, refusal before the model costs $0, citation regex, cost table, no-secrets scan, README↔report consistency, Tavily fail-closed, demo routes) | `tests/test_know.py`, `tests/test_repo.py` |
| 2026-10-13 11:4x | **Bug (honesty):** cost priced at Nano rates while Super answered → per-model `CMIMET` from the official catalog; `make eval` re-run: cost/question $0.00017 → **$0.00084** | `src/know.py`, `harness/report.json` |
| 2026-10-13 11:5x | **Bug (honesty):** harness counted a failed call as OK when no expected id (fail-open); now fails closed and requires a citation → headline **10/13 → 9/13** (`p09` correct but uncited) | `harness/eval.py`, `harness/report.json` |
| 2026-10-13 11:5x | README: one model (Super), one set (13), one date; `make index` target; history of the 12-set kept as history | `README.md`, `Makefile`, `COSTS.md` |


- 2026-10-13 **D1 (Halim)** — profil i izoluar `nebius` mbi **Nemotron** (Token Factory): R1 (thinking default → content jo-bosh) ✓ · R2 (tool-calling përmes OpenClaw) ✓ · R3 (SSE) ✓; dëshmia `matje/dita1.json`.

- 2026-10-13 **D2 (Halim)** — 3 skill-e te profilit `nebius`: ask-archive (citime/refuzim; e2e -> `[vendim-d-070]`), remember (arkiva + git commit, fail-closed; commit 6a56364), remind (cron/at). Deshmia `matje/dita2.json`.
| 2026-10-13 12:0x | **Public example corpus (H6, Halim PO):** 744 Python PEPs → `arkiva-peps/` (`ndaj_korpusin.py --burimi peps`, `burimi`+`licenca` per unit); embedding cost measured **before** spending (`--mat` $0.00551) and after (547,609 tokens = $0.00548); harness `pyetjet-peps.json` → **10/13**, refusals 4/4, p50 4.36 s, $0.00067/q; 3 misses = right PEP named without brackets. `ARK_ARKIVA`/`ARK_PYETJE`/`ARK_RAPORT`; citations filtered to retrieved ids (`[utf-8]` ≠ citation). 28 tests. | `harness/report-peps.json`, `arkiva-peps/embeddings.json` |
| 2026-10-13 12:0x | **Bug (ours) + fix:** `--shto` appended a vector at the end of the index while `kerko_semantike` took texts by *position* → right id, wrong text → private set 5/13 then 3/13 (both runs kept in /tmp only; the cause was found by a raw call: «the text does not mention…» while `d-070` was listed). Fix: text by id + test. **Prompt A/B (after the fix, same sets):** old wording 10/13 private · 9/13 PEPs; **v2 terse** («one or two sentences; every claim ends with the id in brackets, never a bare id») **12/13 private (9/9 cited, p08 still the open miss) · 13/13 PEPs (9/9, 4/4)** — repeated once each: identical. p50 2.0–2.5 s, $0.00084 / $0.00068 per question. 30 tests. | `harness/report.json`, `harness/report-peps.json`, `src/know.py` |
| 2026-10-13 12:1x | Blind jury #3 (8 jurors, rubric nebius) on `329d10b`: **75.0/100** (66.2 this morning, 43.1 on 12.10). Hard requirements nebius/nvidia/licenca/demo 8/8 yes; **video 8/8 no**; top fixes: video · `demo/transcript.md` stale (9/13 vs 12/13) → re-recorded + test ties it to `report.json` · `make run` now builds the index on first use. | `JOURNAL.md`, `demo/transcript.md`, `Makefile` |

- 2026-10-13 **D3 (Halim)** — `src/web_tavily.py`: Tavily si vegel web PAS portes se privatesise (pa `--lejo` → exit 2; me `--lejo` → rezultate reale). K-B u mbyll (celesi ne thesar).
| 2026-10-13 13:4x | **G5–G7, G12–G14:** 100-question PEP set (ground truth by construction) → **88/100, traps 20/20**, p50 3.103 s, $0.00071/q; miss taxonomy in README. Third run of both 13-sets: 12/13 · 13/13 (stable ×3) + **evidence funnel** (model sees 7.6 % / 1.06 % of corpus; expected unit top-1 3/7 · 9/9). `src/audit.py` + `make audit` (6-question memory audit from files+git). UI in English + `/njesi` `/historia` `/diff`. `tools/pergatit_publik.sh` builds the public tree without `arkiva/` (redacted private rows, public transcript, tests ✓, gitleaks 0) — push waits for the owner's URL decision. 33 tests. | `harness/report-peps-100.json`, `src/audit.py`, `src/server.py`, `tools/pergatit_publik.sh` |
| 2026-10-13 14:0x | Knobs `ARK_PRAG`/`ARK_SNIP`; sweep: 0.45 = same, 0.50 = 10/13; SNIP 3000 = 89/100 at 1.9× cost, private 11/13 → **defaults kept** (documented as rejected fixes). Public tree pushed: `living-archive` main `627168a` (single commit, no `arkiva/`); builder now fail-closed on missing public transcript + private-marker scan. | `README.md`, `tools/pergatit_publik.sh` |
