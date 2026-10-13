# Costs — measured, not estimated

All figures come from the `usage` block returned by Token Factory for each call; the same numbers are
written by the harness into `harness/report*.json` and `matje/*.json`.

| Item | Unit price used | Measured |
|---|---|---|
| Nemotron-3-Nano-30B-A3B (chat) | $0.06 / 1M input, $0.24 / 1M output | p50 0.61 s, **$0.0000181** per short call |
| Qwen3-Embedding-8B | **one-off** index build | 291,011 tokens for 387 units |
| End-to-end question, **Nemotron 3 Super** ($0.30 / $0.90 per 1M, catalog 13.10) | — | **$0.00083** per question, p50 3.711 s (`harness/report.json`) |
| End-to-end question, Nemotron 3 Nano (12.10 run) | $0.06 / $0.24 per 1M | $0.000183 per question, p50 1.37 s (`harness/report-v3-semantik.json`) |
| Full 13-question evaluation (Super) | — | **$0.0108** total |
| Everything spent during the whole 12.10 session | — | **≈ $0.008** |

**Budget guard:** at $0.00083 per question (Super), the $25 Builders credit is ~30,110 questions.

**Correction 13.10:** until 13.10 `src/know.py` priced every call at Nano rates even when Super answered; the per-model table `CMIMET` fixes it. Earlier Super rows in `harness/report-v6…v10` carry the understated cost.
The repo contains **no** key; the harness reads it from the environment (`NEBIUS_API_KEY`) or a local vault file.

### Public example corpus (PEPs) — 13.10
| Item | Tokens | Price | Cost |
|---|---|---|---|
| Embedding index, 744 PEPs, `Qwen/Qwen3-Embedding-8B` (measured `--mat` first: 551,370 tokens est. → $0.00551) | 547,609 | $0.01 / 1M | **$0.00548** |
| Harness, 13 questions, Nemotron 3 Super | — | $0.30 / $0.90 per 1M | $0.0088 |
| Harness runs 13.10 11:5x–12:1x (prompt A/B + bug hunt): 5× private set + 5× PEP set | — | Super | ≈ $0.10 |
| 100-question PEP set: generation (80 short calls) + evaluation | — | Super | ≈ $0.03 + $0.071 |
| Third run of both 13-sets (funnel metrics) | — | Super | ≈ $0.02 |
| Threshold sweep (0.45/0.50 × 2 sets) + snippet 3000 (13-set ×1, 100-set ×1) — both rejected | — | Super | ≈ $0.04 + $0.16 |
| Model routing (13.10 14:3x): Ultra × 2 sets ($0.0360 + $0.0296) + Nano × 2 sets ($0.0022 + $0.0018) — Super kept as default | — | Ultra $1 / $3 · Nano $0.06 / $0.24 per 1M | **$0.0696** |
| Web layer (Tavily → Super), live checks + 5 screenshots: ~6 answers + ~8 Tavily credits (free tier 1 000/month) | — | Super | ≈ $0.004 |
