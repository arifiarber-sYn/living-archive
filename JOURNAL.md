# Build journal — the cloud engine (REJA)

> Auditable memory: every number in the README has a row here, and every row is a commit.
> Times are Europe/Belgrade, 12.10.2026. Branch `reja-motor` (not pushed yet).

| Time | What happened | Evidence |
|---|---|---|
| 18:27 | Public repo cloned and inspected read-only; found it is a **different, complete product** (local Ollama) | `VENDIM-REPO-NEBIUS.md` |
| 18:28 | Cloud engine written: Token Factory (`Qwen/Qwen3-Embedding-8B`, `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`) | `app/reja.py` |
| 18:29 | Sample corpus indexed: **5 units, 611 tokens** | `indeksi/reja.json` |
| 18:30 | Threshold calibration tool written and run: separation looked clean — **0.3733 vs 0.3736** | `app/kalibrim.py` |
| 18:31 | **The separation was an artifact.** The winning fragment had `grep -c taksa` = **0**: similarity measures topicality, not answerability | `korpus/vendim-buxheti-2027.txt` |
| 18:33 | Two-layer refusal implemented: safety floor + **citation verification** | `app/reja.py` |
| 18:43 | First cloud harness: **3/8** — the model answered correctly but **without citations** | `indeksi/harness-reja.json` |
| 18:44 | A concrete example in the prompt raised it to **4/8** — the model still drops brackets on long answers | commit `4e4ace3` |
| 18:45 | **Citations computed, not trusted** (`atribuo_citime`): the numbers in the answer must all appear in a retrieved fragment → **7/8 (87.5%)**, refusals **3/3** | `indeksi/harness-reja.json` |
| 18:47 | README (EN + SQ) and a Makefile with **one file, two engines** (`ARK_ENGINE=reja|vendor`) | commit `347878d` |
| 18:51 | 180-second video scenario for the unified archive, 0 placeholders | `docs/VIDEO-SKENAR-REJA.json` |
| 18:52 | **Recording proof run**: 59.8 s, h264 + aac, `ok: true` | `/tmp/prova-reja.mp4` |
| 18:56 | Runtime cost file removed from git (it grows with every call; reproducible from usage) | commit `6fce7ff` |
| 19:00 | Pricing verified against the official catalog: our `COSTS.md` figures are **correct** | `docs/HULUMTIMI-12-10.md` |
| 19:01 | **Model comparison on the same harness**: Super **8/8**, Nano 7/8, Lightning **3/8 + 1 fabrication** | `krahasimi-modele/` |
| 19:05 | Default switched to Super; both harnesses re-run: cloud **8/8**, private archive **10/12** | commits `43092f2`, `87a4092` |

## What was rejected (kept on purpose)

1. **An absolute similarity threshold** — the "clean" 0.0003 separation was luck, not evidence.
2. **A citation contract described in words** — the model ignores it when the answer grows.
3. **Trusting the model's own citations** — replaced by a check the answer cannot talk its way past.

## What is not claimed

- The sample corpus is small (6 files); the 87.5% is a baseline on 8 questions, not a benchmark win.
- The private 387-unit archive used on 12.10 is **not** in this repo (514 lines carry names, IPs, paths).
- No hosting, no authentication, no multi-user isolation in this build.
