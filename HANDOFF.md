# Handoff

Context bridge for picking this work up in a new session (e.g. a cloud session).
See `README.md` for full usage and `DESIGN_DOC_INSTRUCTIONS.md` for the authoring
rules.

## What this repo is

A reusable, project-agnostic **design-documentation system**: a set of Markdown
authoring agents that take a plain-language brief to `DESIGN.md` →
`REQUIREMENTS.md` → `TASKS.md`, plus an offline HTML rendering system (one visual
language, zero network dependencies) for the polished, shareable version.

## Layout

| Path | Purpose |
|---|---|
| `DESIGN_DOC_INSTRUCTIONS.md` | The instruction document — archetypes, tokens, components, offline Mermaid, writing style, the Markdown working-doc rules (§11), QA checklist. |
| `template.html` | Narrative-page skeleton + live component gallery. |
| `template-interactive.html` | Self-contained interactive reference-browser skeleton. |
| `lib/` | Shared stylesheet (`doc.css`), offline Mermaid bundle + init, lightbox, nav. |
| `agents/` | The five pipeline subagents + `agents/README.md` (install) + `agents/templates/` Markdown skeletons. |

## What the seeding session did (2026-09-08 / 09)

- Made the system generic — removed all PRISM/HOCA/STSSE references from
  `DESIGN_DOC_INSTRUCTIONS.md`, `README.md`, both HTML templates, and `lib/*`
  header comments; fixed path references to `design-docs-template/`.
- Added `DESIGN_DOC_INSTRUCTIONS.md` **§11** — the Markdown working-document
  structure and per-document outlines, plus the Markdown → HTML mapping.
- Added the `agents/` pipeline:
  `design-doc-author` → `requirements-author` → `tasks-planner` →
  `spec-validator` → `html-suite-builder`, with `agents/templates/`
  (`DESIGN.template.md`, `REQUIREMENTS.template.md`, `TASKS.template.md`).
- Initialized git and pushed to `github.com/jcallaway82/design-docs-template`.

## Suggested next steps

1. **Dry-run the pipeline** on a sample brief; tighten each agent prompt based on
   what the drafts actually produce (over/under-specification, section drift).
2. **Package as a Claude Code plugin** (`agents/` + a `skills/` entry) so a
   project can install the pipeline in one command instead of copying files.
3. **Mermaid bundle provenance** — record the exact `mermaid` version, source,
   and refresh command in `DESIGN_DOC_INSTRUCTIONS.md` Appendix C.
4. **Optional CI** — HTML validation + internal-link check for the templates and
   any generated suite.

## Conventions

- Offline-first: no CDNs, no external fonts/scripts/images. `lib/mermaid.min.js`
  is vendored on purpose.
- All colors come from CSS tokens in `lib/doc.css` — never hard-code hex in
  markup.
- Why-first prose: rationale sits next to the decision it explains.
- Stable IDs, never renumbered: `FR-*` / `NFR-*` (requirements), `DD-*` (design
  decisions), `T-*` (tasks). Dropped items are marked withdrawn, not deleted.
