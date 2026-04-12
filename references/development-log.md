# Development Log

Use a development log when a piece of work produces durable reasoning that should survive the current session.

Development logs are not the same as:

- `status.md`: current truth and next actions
- `roadmap.md`: milestone order and long-line direction
- `ADR`: a compact durable design decision

Use a devlog when future maintainers would benefit from the full path:

- the problem or tension
- what was observed
- what options were considered
- why one path was chosen
- how the result was verified

## When To Write One

Write or update a devlog entry when:

- a retrofit uncovered a non-obvious documentation or structure issue
- a bug fix required important root-cause reasoning
- a design boundary changed because evidence contradicted the earlier assumption
- a future maintainer would otherwise need to reconstruct the same reasoning from git diffs

Do not write a devlog for trivial edits.

## Default Location

Use:

- `docs/devlog/README.md`
- `docs/devlog/README.zh-CN.md`
- `docs/devlog/YYYY-MM-DD-topic.md`

Treat the index pages as durable navigation. Treat individual entries as internal durable notes, not canonical product docs.

## Default Sections

- `Problem`
- `Thinking`
- `Solution`
- `Validation`
- `Follow-Ups`
- `Related Files`

## Workflow

1. keep `status.md` and `plan.md` focused on current truth
2. when a durable reasoning thread appears, create or update a devlog entry
3. link the relevant files or commands that proved the solution
4. keep the narrative compact; optimize for future debugging, not storytelling

If the repo contains `scripts/write_development_log.py`, prefer using it.
