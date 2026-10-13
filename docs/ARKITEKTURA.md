# Architecture — The Living Archive as an OpenClaw agent

Memory is plain files under git; the brain is **NVIDIA Nemotron on Nebius Token Factory**;
the body is an **isolated OpenClaw profile** that can act (remember / remind), not just answer.

```mermaid
flowchart LR
  U[User] -->|question| A[OpenClaw agent\nprofile: nebius]
  A -->|ask-archive| R[Retriever]
  subgraph Memory [Memory = plain files under git]
    C[(arkiva-peps/*.md\n744 public PEPs)]
    E[(embeddings)]
    C --- E
  end
  R -->|local embedding search\ntop-k, no cloud| C
  R -->|below evidence threshold| X[Refuse: \"I don't know\"\n0 model calls, 0 cost]
  R -->|enough evidence| N[Nemotron 3 Super\nNebius Token Factory\nthinking OFF]
  N -->|answer WITH citations| A
  A -->|remember| W[write new unit + git commit\nauditable action]
  A -->|remind| T[schedule (cron / at)]
  A -->|web-tavily| G{privacy gate}
  G -->|without --lejo| X2[Refuse: query stays local]
  G -->|--lejo| TV[Tavily web search]
```

## Measured (no claims without a file)
| Metric | Value | Where |
|---|---|---|
| Answerable set (13 q) | 12/13 stable x3 | `harness/report.json` |
| Public PEP set (100 q) | 88/100, traps 20/20 | `harness/` |
| Cost / question | $0.00074 (thinking off) | `matje/` |
| p50 latency | 5.43 s (thinking off) | `matje/dita1.json` + H13 |
| Hallucination guard | refuse before the model when evidence is thin | `src/know.py` |
| Auditable memory | every `remember` = a `git commit` | `src/remember.py`, `git log` |

_Diagram: Halim (orchestrator), 13.10.2026._
