# Architecture Retrofit

Use this reference when the repo's main problem is architectural drift rather than only missing control docs or messy Markdown structure.

Short commands:

- `项目助手 架构 整改`
- `project assistant architecture retrofit`

Use this mode when:

- fixes keep cascading and the real cause is probably above the current patch
- boundaries, ownership, or state flow are wrong at a system level
- duplicate architecture docs or competing sources of truth are keeping the repo confused
- the repo keeps adding one-off special cases because the correct layer is unclear

Core rule:

- ordinary retrofit fixes structure drift
- architecture retrofit fixes direction drift

That means architecture retrofit must:

1. classify the root problem as an architecture problem, not only a local bug
2. define the target architecture before applying scattered fixes
3. map which code, docs, tests, modules, and release surfaces must move together
4. run a convergence plan that reduces special cases and duplicate owners

Prefer this sequence:

1. run `scripts/sync_architecture_retrofit.py`
2. read `.codex/architecture-retrofit.md`
3. convert the retrofit into one or more explicit slices
4. generate the current execution line from the chosen architecture-retrofit slice
5. apply the architecture retrofit itself across code, docs, tests, and control surface
6. keep the architecture signal visible during the retrofit
7. finish on `deep`; if release-facing work changed, also finish on `release`

Default expectation:

- `项目助手 架构 整改` should directly execute the retrofit to convergence
- the architecture-retrofit note is a working artifact, not the default stopping point
- only stop after producing a note or checklist when the user explicitly asks for audit-only behavior

The working note should answer:

- what symptoms show this is an architecture problem
- what root-cause drivers are most likely
- which boundaries are affected
- which docs are canonical owners and which must be demoted or archived
- what the target architecture is
- what the retrofit scope is
- how execution will be sliced and validated
- what conditions must be true before the retrofit is considered complete

Do not treat architecture retrofit as "rewrite everything". Prefer the minimum structural correction that restores the right boundaries and lets future work stop accumulating local-only fixes.
