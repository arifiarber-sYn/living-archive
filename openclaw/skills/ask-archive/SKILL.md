---
name: ask-archive
description: Ask the user's knowledge archive — an answer WITH citations, or a visible refusal. Use when the user asks about their archive/documents ("what do I know about …", "which decision …", "which PEP …").
---

# ask-archive

`$ARCHIVE_REPO` = the directory this repository was cloned into (e.g. `~/living-archive`).

When the user asks something about the archive:
1. Run: `cd "$ARCHIVE_REPO" && make run Q="<question>"` (or `curl -s 'http://127.0.0.1:8077/pyet?q=<question>'` if the demo server is running).
2. Return the answer AS IS, with its `[id]` citations. If the system refuses (below the evidence threshold, or the model says «I don't know»), say so plainly — NEVER invent an answer.
3. Never drop a citation; never add a fact without a source.
