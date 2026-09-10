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
| `agents/` | The five pipeline subagents — nothing else (see below). |
| `templates/` | Markdown skeletons for the three working documents. Moved out of `agents/templates/` on 2026-09-10 — see below. |
| `.claude-plugin/plugin.json` | Plugin manifest — install via `claude --plugin-dir`. |
| `PLUGIN_PACKAGING.md` | Scope + remaining tasks (T-4, T-5) for the plugin packaging work. |

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

1. ~~**Dry-run the pipeline** on a sample brief~~ — done 2026-09-09, see
   below. Re-run after any further prompt changes.
2. **Package as a Claude Code plugin** — T-1–T-3 done 2026-09-10, see below.
   T-4 (orchestrator skill) and T-5 (marketplace entry) remain, both
   optional and gated on the open questions in
   [`PLUGIN_PACKAGING.md`](PLUGIN_PACKAGING.md).
3. **Mermaid bundle provenance** — record the exact `mermaid` version, source,
   and refresh command in `DESIGN_DOC_INSTRUCTIONS.md` Appendix C.
4. **Optional CI** — HTML validation + internal-link check for the templates and
   any generated suite.

## Dry run (2026-09-09)

Ran the full pipeline by hand (`design-doc-author` → `requirements-author` →
`tasks-planner` → `spec-validator`) against a sample brief — `mdtoc`, a CLI
that keeps an in-file Markdown TOC in sync with a file's own headings.
Output is not checked in (it's a throwaway sample, not this repo's own
design); it produced 7 failure modes, 16 FR + 6 NFR, 17 tasks, and a
`SPEC_REVIEW.md` with 2 Critical / 2 Medium / 2 Low findings. Two findings
were genuine prompt gaps and were fixed in this commit:

- **`tasks-planner`** listed task size as "S (≤2 h), M (≤1 day), or L (split
  it)" — phrased so a task could end up sized `L` in the final plan instead
  of being split. Tightened to make `L` explicitly not a valid final size,
  in `tasks-planner.md`, `templates/TASKS.template.md`, and
  `DESIGN_DOC_INSTRUCTIONS.md` §11.3; `spec-validator.md`'s sizing check
  wording matches.
- **`requirements-author`** had no rule stopping it from writing a firm
  `SHALL` requirement for a decision `DESIGN.md` §10 still lists as open,
  which silently closes the question without the resolution the design
  calls for. Added rule 6 (write it provisional, or leave it in Open
  questions, until the design question closes).

The other findings (a design component's responsibility with no
requirement, an implicit command surface with no dedicated FR) were the
pipeline working as intended — `spec-validator` catching what an authoring
agent missed — not prompt bugs.

## Plugin packaging T-1–T-3 (2026-09-10)

Built the minimum viable plugin per `PLUGIN_PACKAGING.md`: `.claude-plugin/plugin.json`
(name `design-docs-template`, no `author` field — none was available to put there
truthfully), smoke-tested with `claude --plugin-dir`, and documented the install
path in `README.md`.

Running `claude plugin validate .` and the `--plugin-dir` smoke test surfaced a
real bug the scope doc didn't anticipate: Claude Code's plugin loader treats
**every** `.md` file under `agents/`, recursively, as an agent definition. With
`agents/README.md` and `agents/templates/*.md` still in place, the smoke test
showed four broken pseudo-agents (`design-docs-template:README`,
`design-docs-template:templates:DESIGN.template`, etc.) alongside the five real
ones. Fixed by moving `templates/` to the repo root and merging `agents/README.md`'s
content into the top-level `README.md`; `agents/` now holds exactly the five agent
files. Re-ran both checks clean (only the pre-existing "no author" warning remains).
All in-repo references to the old `agents/templates/` and `agents/README.md` paths
are updated (`agents/design-doc-author.md`, `agents/requirements-author.md`,
`agents/tasks-planner.md`, `DESIGN_DOC_INSTRUCTIONS.md`).

## Conventions

- Offline-first: no CDNs, no external fonts/scripts/images. `lib/mermaid.min.js`
  is vendored on purpose.
- All colors come from CSS tokens in `lib/doc.css` — never hard-code hex in
  markup.
- Why-first prose: rationale sits next to the decision it explains.
- Stable IDs, never renumbered: `FR-*` / `NFR-*` (requirements), `DD-*` (design
  decisions), `T-*` (tasks). Dropped items are marked withdrawn, not deleted.
