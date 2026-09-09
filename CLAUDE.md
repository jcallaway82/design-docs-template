# CLAUDE.md

Project-agnostic design-documentation system: Markdown authoring agents plus an
offline HTML rendering system that share one visual language and one set of
structural rules.

## Pipeline

`brief → design-doc-author → DESIGN.md → requirements-author → REQUIREMENTS.md →
tasks-planner → TASKS.md → spec-validator → SPEC_REVIEW.md →
html-suite-builder → design-docs/ (HTML)`

Each stage is a human review checkpoint. Agents stay in their lane:
`requirements-author` does not expand scope; `spec-validator` reports, never
edits. Agent definitions and install instructions are in `agents/`.

## Authoring rules

- `DESIGN_DOC_INSTRUCTIONS.md` is the source of truth — §9 (writing style) and
  §11 (Markdown working-document structure) govern the `.md` documents; §3–§10
  govern the HTML.
- Offline-first: no CDNs, no external fonts/scripts/images. `lib/mermaid.min.js`
  is vendored deliberately.
- All colors from CSS tokens in `lib/doc.css`; never hard-code hex in markup.
- Why-first prose; precise numbers over vague words; enumerate failure modes.
- Stable IDs, never renumbered: `FR-*`, `NFR-*`, `DD-*`, `T-*`.

## Status

See `HANDOFF.md` for what the seeding session did and the current next steps.
