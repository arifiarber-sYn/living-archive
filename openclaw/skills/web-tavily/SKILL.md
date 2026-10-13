---
name: web-tavily
description: Live web search through Tavily, BEHIND a privacy gate. Use when current information from the internet is needed; requires the user's EXPLICIT permission (`--lejo` = allow) before the query leaves the machine.
---

# web-tavily

`$ARCHIVE_REPO` = the directory this repository was cloned into (e.g. `~/living-archive`).

1. Run: `python3 "$ARCHIVE_REPO/src/web_tavily.py" --pyetja "<question>" [--lejo]` (`--pyetja` = the query, `--lejo` = allow it to leave the machine).
2. WITHOUT `--lejo` the gate REFUSES (exit 2) and the query is never sent. Ask the user for permission BEFORE adding `--lejo`.
3. Return the results WITH their URLs; never invent a source. For a cited answer that combines the archive and the web, use the demo's `/web?q=…&allow=1` instead (`src/web_know.py`).
