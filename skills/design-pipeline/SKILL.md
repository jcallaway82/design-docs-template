---
description: >-
  Walk a plain-language brief through the design-docs-template pipeline
  (design-doc-author -> requirements-author -> tasks-planner ->
  spec-validator -> html-suite-builder) to produce DESIGN.md,
  REQUIREMENTS.md, TASKS.md, SPEC_REVIEW.md, and the offline HTML suite. Use
  when the user has a brief, ticket, or rough idea and wants a design doc,
  requirements, a task breakdown, a spec review, or the full pipeline run
  end to end, and hasn't named a single agent already.
---

# Design docs pipeline

This plugin ships five subagents that turn a brief into a reviewed, offline
HTML design-doc suite. Each stage is a human checkpoint — do not skip ahead
without the user reviewing the previous stage's output, unless they've
explicitly asked for the whole pipeline run unattended.

1. **`design-doc-author`** — brief → `DESIGN.md`. Start here when the user
   has a brief and no `DESIGN.md` exists yet.
2. **`requirements-author`** — `DESIGN.md` + user input → `REQUIREMENTS.md`.
   Run once `DESIGN.md` is reviewed.
3. **`tasks-planner`** — `DESIGN.md` + `REQUIREMENTS.md` → `TASKS.md` (also
   fills `REQUIREMENTS.md` §7's Task ID column).
4. **`spec-validator`** — all three → `SPEC_REVIEW.md` (report only, never
   edits the specs). Run before implementation starts.
5. **`html-suite-builder`** — the approved Markdown set → `design-docs/`
   HTML suite. Run last, and only once `SPEC_REVIEW.md` has no open
   Critical or High findings.

Invoke the next agent by name — do not reimplement any agent's job inline;
each has its own operating rules in `agents/<name>.md` and knows its own
output format. After running one, stop and let the user review its output
before continuing, then print that agent's own "next step" line rather than
inventing your own.

If `DESIGN.md`, `REQUIREMENTS.md`, or `TASKS.md` already exists, resume
from the first stage whose output is missing or the user wants revised —
do not restart from `design-doc-author` on an existing project unless
asked.
