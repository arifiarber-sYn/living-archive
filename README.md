# The Living Archive (Arkivi i Gjallë)

**An honest retrieval agent for small organizations — answers with verifiable
citations, refuses to fabricate, measures itself, and learns from feedback.
Fully local: no external APIs, no credentials, no cloud.**

Built solo in a timed 24-hour-format sprint (delivered in ~70 minutes) and
evaluated against a private adversarial answer key. Original documentation in
Albanian: [README.sq.md](README.sq.md), [PITCH.sq.md](PITCH.sq.md),
[DITARI.sq.md](DITARI.sq.md) (the honest build journal).

## Why it exists

Small institutions (municipalities, NGOs) sit on hundreds of documents nobody
can search — and they cannot afford an AI that invents answers. In an
institutional context, a confident fabrication is worse than "I don't know."
This system makes the trust boundary part of the product:

- **Verifiable citations** — every answer cites fragment IDs `[dNN-N]`;
  one click opens the actual source fragment.
- **Mandatory "I don't know"** — if the retrieved fragments don't cover the
  question, the answer is `S'E DI` (I don't know). Fabrication is designed out,
  and the refusal rate is measured, not hidden.
- **Self-measurement** — the agent builds its own benchmark questions and
  displays the numbers in the UI (no "trust me").
- **Provable learning** — user feedback ("correct" +0.04 / "wrong" −0.12 per
  citation) shifts retrieval ranking. Not cosmetic: measurably changes results.
- **Local-first** — embeddings (`nomic-embed-text`) and generation run through
  a local Ollama instance on `127.0.0.1`. Client data never leaves the machine.

## Quick start (a stranger, under 10 minutes)

```bash
# 1) put your documents (text or PDF) into korpus/
python3 app/arkivi.py gelltit   # ingest: index + report what was/wasn't understood
python3 app/ui.py               # UI at http://127.0.0.1:8903
```

Dependencies: `pdftotext` (for PDFs), `ollama` with `nomic-embed-text` and a
local chat model.

## How it works

1. **Ingestion** — per file: read (PDFs via `pdftotext`) → chunk → embed →
   store. The ingestion report explicitly lists documents that were **not**
   understood (e.g. scanned PDFs with no extractable text) — no silent gaps.
2. **Answering** — embed the question → retrieve top-5 fragments → the local
   LLM answers **only from those fragments**, citing `[id]`; if they don't
   cover the question → `S'E DI`.
3. **Feedback** — per-citation boosts adjust future ranking; wrong answers
   make similar queries retrieve differently.

## Measured results (adversarial test corpus)

Tested on a 50-document poisoned corpus (fictional municipality + Wikipedia
articles): planted contradictions with explicit repeal clauses, duplicate
pairs, an empty file, a German-language document, scanned PDFs, and trap
questions with no answer in the corpus.

- Private jury battery (12 questions): **8/9 factual questions answered
  correctly with citations** — including resolving a planted contradiction to
  the currently-valid value and answering across languages — and **3/3 trap
  questions correctly refused. Zero fabrications.**
- Self-harness (15 questions, shown in UI): 8 correct, 7 over-cautious
  refusals, **0 fabrications** — the failure mode is deliberately conservative.
- Honest negative result, self-declared: lowering the similarity threshold
  0.45 → 0.35 did **not** reduce wrong refusals (they come from the model's
  judgment over fragments, not the threshold) — change reverted, documented.

## Repository layout

- `app/arkivi.py` — ingestion, retrieval, citation-grounded answering, feedback boosts
- `app/agjenti.py` — the visible agentic ingestion loop (observe → decide → index → report)
- `app/harness.py` — self-evaluation harness
- `app/ui.py` — minimal async UI (citations clickable, feedback buttons, live stats)
- `indeksi/harness.json` — harness questions + measured results
- `korpus-test/` — small test corpus
- `video-demo.mp4` — 47-second demo (Albanian; EN version planned)

## License

MIT — see [LICENSE](LICENSE).
