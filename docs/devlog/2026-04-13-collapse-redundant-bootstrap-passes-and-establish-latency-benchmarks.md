# Collapse redundant bootstrap passes and establish latency benchmarks

- Date: 2026-04-13
- Status: resolved

## Problem

Users are now explicitly reporting blank-project bootstrap around 6m50 and retrofit runs that feel too slow. The repo needed to stop treating this as a vague performance complaint and determine whether the cost came from raw scripts, repeated bootstrap passes, missing one-pass surfaces, or agent-side orchestration.

## Thinking

A first synthetic benchmark pass showed that the raw scripts were already in the low-single-digit-second range, which contradicted the user-facing wait time. That shifted the root-cause hypothesis away from single-script runtime and toward repeated orchestration. Two concrete gaps stood out: sync_docs_system.py and sync_markdown_governance.py always reran sync_control_surface.py even when the control surface was already current, and sync_control_surface.py itself did not create entry-routing even though medium/large repos expected it. That combination forced extra reruns and made the end-to-end path look much slower than the raw work.

## Solution

Added a repeatable scripts/benchmark_latency.py harness for blank bootstrap and synthetic retrofit timing. Updated sync_docs_system.py and sync_markdown_governance.py to skip control-surface bootstrap when the repo is already on the current control-surface generation with all required surfaces present. Updated sync_control_surface.py to create entry-routing in the same pass for medium/large repos. Promoted bootstrap/retrofit latency into the active control-surface phase so the next round can target the remaining agent/orchestration overhead explicitly.

## Validation

python3 scripts/benchmark_latency.py --format text now reports synthetic blank-bootstrap at about 1.604s and synthetic retrofit-pipeline at about 1.404s on the local baseline. validate_control_surface.py, validate_docs_system.py, and validate_entry_routing.py all pass on the skill repo after the changes.

## Follow-Ups

- Measure the remaining end-to-end latency outside raw scripts so agent/orchestration cost is isolated instead of guessed.
- Evaluate a transaction-style bootstrap/retrofit fast path that can run control-surface, docs, governance, and gates without repeated assistant-side orchestration.

## Related Files

- scripts/sync_control_surface.py
- scripts/sync_docs_system.py
- scripts/sync_markdown_governance.py
- scripts/benchmark_latency.py
