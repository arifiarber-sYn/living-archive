# The agent body — OpenClaw profile `nebius`

The Living Archive is the memory + brain; this directory is the **body**: a real
OpenClaw agent whose primary model is **NVIDIA Nemotron on Nebius Token Factory**.

## What is here
- `openclaw.json` — an **isolated** OpenClaw profile (`openclaw --profile nebius`; state under `~/.openclaw-nebius`). **No keys:** the API key is a SecretRef resolved from the environment (`NEBIUS_API_KEY`).
- `skills/ask-archive` — ask the archive: an answer **with citations**, or a visible refusal.
- `skills/remember` — write a new archive unit **and `git commit`** it (an auditable action).
- `skills/remind` — schedule a future reminder (profile cron, `at` fallback).
- `skills/web-tavily` — live web search **behind a privacy gate** (refuses without an explicit `--lejo`).

## Stand it up in 5 minutes
1. `export NEBIUS_API_KEY=<your Token Factory key>`
2. `mkdir -p ~/.openclaw-nebius/workspace && cp -r openclaw/skills ~/.openclaw-nebius/workspace/ && cp openclaw/openclaw.json ~/.openclaw-nebius/`
3. `openclaw --profile nebius models list`
4. `openclaw --profile nebius agent --local -m "Use the ask-archive skill: <your question>"`
5. `openclaw --profile nebius agent --local -m "Use the remember skill to save '<fact>'"` → verify with `git log -1`.

This is the same agent that red-teamed Apertus v1.5 and that maintains this repository's history.
