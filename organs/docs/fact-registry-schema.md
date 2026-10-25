# Fact registry schema (theoretical description)

The memory layer stores durable facts, not chat transcripts:

| Field | Type | Purpose |
|---|---|---|
| subject | dotted key | Stable namespace for the fact. |
| fact | one sentence | The assertion itself, atomic and testable. |
| source | provenance | Session, document or command that produced it. |
| recorded_at | timestamp | When it entered the registry. |
| supersedes | reference | The earlier fact this one replaces. |
| status | enum | active / superseded / retracted. |

Replacement is append-only: a correction never deletes the previous entry, it marks it
superseded and links forward. This keeps a time-ordered audit trail without rewriting
history.
