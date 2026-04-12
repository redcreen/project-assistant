# Add development-log capture to project assistant

- Date: 2026-04-12
- Status: resolved

## Problem

The skill could converge structure and docs, but it did not preserve durable debugging paths or retrofit reasoning in a dedicated narrative artifact. Important conclusions were still trapped in chat history, diffs, or status updates.

## Thinking

Status, roadmap, and ADRs each answer a narrower question than the full implementation path. We needed a separate note type for non-obvious problems where future maintainers would care about the tension, failed assumptions, and validation trail. The log also needed script support and a gate so it would not stay as an optional habit.

## Solution

Added a devlog mode, a writer script, a validator, docs-index integration, and deep-gate coverage. The governed doc stack now includes docs/devlog/README.md and README.zh-CN.md, while individual entries can capture durable reasoning without replacing status or ADRs.

## Validation

Updated the skill docs, generated the devlog indexes, wrote this entry with the writer script, and ran the deep validation gate on the skill repo.

## Follow-Ups

- Evaluate later whether devlog entries should have an optional machine-readable metadata block.
- Keep devlog entries compact so they remain useful for future debugging.

## Related Files

- /Users/redcreen/.codex/skills/project-assistant/SKILL.md
- /Users/redcreen/.codex/skills/project-assistant/scripts/write_development_log.py
- /Users/redcreen/.codex/skills/project-assistant/scripts/validate_development_log.py
