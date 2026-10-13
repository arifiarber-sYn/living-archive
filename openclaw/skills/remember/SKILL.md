---
name: remember
description: Store a fact or decision permanently in the archive as a new memory unit (a file + a git commit). Use when the user says "remember", "save this", "keep in mind".
---

# remember

`$ARCHIVE_REPO` = the directory this repository was cloned into (e.g. `~/living-archive`).

When the user asks you to remember something:
1. Pick a short `--id` (e.g. `r-01`) and a `--kategoria` (category, e.g. `shenim` = note).
2. Run: `python3 "$ARCHIVE_REPO/src/remember.py" --id <id> --kategoria <category> --tekst "<text>" --burimi "conversation <date>"`
   (`--tekst` = the text to remember, `--burimi` = its source; add `--indeks` to append one vector to the local index at once).
3. Then: `cd "$ARCHIVE_REPO" && make index` (so retrieval sees the new unit) — unless you used `--indeks`.
4. Report `git log -1 --oneline` — the commit IS the auditable action (and what the demo shows).
Fail-closed: if a unit with that id already exists the script refuses (exit 2) — never force it, pick another id.
