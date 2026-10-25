# Owner-held memory and recovery infrastructure for long-running automated assistants

## Problem

Long-running assistants accumulate memory across months: decisions, corrections, lessons, and the
state of the work itself. Most platforms keep that memory inside their own product. When the
account closes, the model changes, or the machine dies, the memory goes with it — or survives as
a chat log nobody can audit.

## What this is

Four independent components, none of them tied to a model or a vendor:

1. **Memory under version control.** Durable facts, decisions and lessons live in plain files in a
   git repository the owner controls. A fact registry stores atomic assertions with provenance and
   append-only replacement: a correction marks the earlier entry superseded instead of rewriting
   history.
2. **Recovery drill.** A scripted procedure that rebuilds a working assistant from a clean directory
   using only owner-held encrypted backups: identifies owned repositories, clones them, locates the
   vault snapshot, restores configuration and registries, reinstalls scheduled units, and verifies
   the result.
3. **Handoff protocol.** Work that outlives a session is passed between processes and entities as
   files with a validated schema, plus a rate-limited notification gate — so nothing depends on one
   conversation staying open.
4. **Integrity shield.** A file-integrity monitor over the owner's tier-1 files, run on a fixed
   cadence, with an explicit accept/verify workflow.

## Design principles

- **Owner-held.** The data lives in the owner's repositories and backups, not in a vendor account.
- **Vendor-independent.** No component requires a specific model, provider or platform to function.
- **Append-only history.** Corrections never delete evidence; they supersede it and link forward.
- **Tested recovery.** A backup is not done until a restore has been proven. The drill is the test.

## Measured status

| Check | Result | Date |
|---|---|---|
| Recovery drill steps | 8/8 passed | 2026-08-20 |
| Repository restore | 13/13 repositories, 13 483 files compared | 2026-10-20 |
| Fact registry | append-only schema with supersession | in use |
- All four components expose a command-line interface and run without a network connection.
- Verification is reproducible: the drill writes a machine-readable report on each run.

## What is being prepared for release

- English documentation for each component, written for someone who has never seen the system.
- Tests that run from a clean clone, without the author's machine or data.
- Packaging and continuous integration, so the components can be installed and tried.
- A security note covering the threat model, the backup chain and the recovery assumptions.

## Status

Pre-release. The components are in daily use by their author; the public materials above are being
prepared. This document describes the infrastructure, not any particular assistant built on top of it.

## License

Intended: MIT. To be confirmed at publication.
