---
name: remind
description: Schedule a future reminder/task (profile cron, or `at` as fallback) so the agent brings it up later. Use when the user says "remind me", "tomorrow at 09:00 …".
---

# remind

When the user asks for a future reminder:
1. Try the profile's cron: `openclaw --profile nebius cron add --name remind-<id> --at "<ISO timestamp>" --message "<text>"`.
2. If the profile has no gateway (cron refuses), fall back to `at`: `printf '%s\n' "<text>" | at <HH:MM> <date>`.
3. Verify with `openclaw --profile nebius cron list` or `atq`, and report the output — that is the PROOF of "always-on".
