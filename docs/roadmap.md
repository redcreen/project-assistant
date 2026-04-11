# Roadmap

[English](roadmap.md) | [中文](roadmap.zh-CN.md)

## Scope

This roadmap describes the evolution of the `project-assistant` skill itself. It does not replace current execution truth from `.codex/status.md`.

## Now / Next / Later

| Horizon | Focus | Exit Signal |
| --- | --- | --- |
| Now | convergent retrofit, progress, handoff, and document-system gates | control surface, docs, and public-doc i18n all validate |
| Next | deeper doc refactoring quality and stronger templates | less manual README and docs reshaping on real repos |
| Later | richer validation, better recovery automation, more visual reporting | new repos need fewer manual steering prompts |

## Milestones

| Milestone | Status | Goal | Depends On | Exit Criteria |
| --- | --- | --- | --- | --- |
| M1 | done | establish `.codex` control surface and tiering | core skill routing | current state is recoverable |
| M2 | done | establish convergent retrofit | control-surface scripts | retrofit no longer stops midway |
| M3 | done | establish progress and handoff workflows | module layer + snapshot scripts | progress and handoff are stable |
| M4 | done | establish durable-doc standards and doc validation | document standards + docs scripts | durable docs pass structural gates |
| M5 | active | establish bilingual public-doc switching and validation | i18n rules + i18n validator | public docs switch cleanly between English and Chinese |
| M6 | next | improve narrative quality for automatic doc restructuring | previous milestones | less manual cleanup after retrofit |

## Milestone Flow

```mermaid
flowchart LR
    M1["M1 Control Surface"] --> M2["M2 Convergent Retrofit"]
    M2 --> M3["M3 Progress + Handoff"]
    M3 --> M4["M4 Document Standards"]
    M4 --> M5["M5 Public Doc I18n"]
    M5 --> M6["M6 Deeper Doc Refactoring"]
```

## Risks and Dependencies

- document sync can scaffold structure faster than it can rewrite polished prose
- public-doc bilingual quality still depends on good content generation, not only file-pair checks
- exact context-usage thresholds still require runtime support
