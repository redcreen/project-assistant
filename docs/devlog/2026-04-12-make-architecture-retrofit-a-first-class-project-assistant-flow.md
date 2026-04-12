# Make architecture retrofit a first-class project-assistant flow

- Date: 2026-04-12
- Status: resolved

## Problem

Ordinary retrofit could converge structure drift, but it still did not clearly address repos whose real problem was architectural direction drift, wrong boundaries, or repeated wrong-layer fixes.

## Thinking

We needed to separate direction repair from generic structure cleanup. That required more than a new command label: the skill needed an architecture-first working note, an explicit validator, updated menus and templates, and a way to surface the capability in progress, handoff, and usable-now reporting.

## Solution

Added architecture-retrofit commands, a dedicated reference, a repo-local working-note generator, a validator, gate integration, template updates, and self-dogfooded the flow by generating `.codex/architecture-retrofit.md` inside the skill repo itself.

## Validation

Generated an architecture-retrofit working note for the skill repo, passed `validate_architecture_retrofit.py`, then reran both deep and release gate profiles successfully.

## Follow-Ups

- Try the architecture-retrofit flow on representative repos where the root problem is boundary drift rather than only document drift.
- Keep refining the audit heuristics so reference docs are not mistaken for canonical architecture owners.

## Related Files

- scripts/sync_architecture_retrofit.py
- scripts/validate_architecture_retrofit.py
- references/architecture-retrofit.md
- .codex/architecture-retrofit.md
- SKILL.md
