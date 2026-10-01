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
| `agents/` | The six pipeline subagents — nothing else (see below). |
| `templates/` | Markdown skeletons for the three working documents. Moved out of `agents/templates/` on 2026-09-10 — see below. |
| `.claude-plugin/plugin.json` | Plugin manifest — install via `claude --plugin-dir`. |
| `skills/design-pipeline/` | Orchestrator skill — `/design-docs:design-pipeline`. |
| `PLUGIN_PACKAGING.md` | Plugin packaging record — done, including the rename. |

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
2. ~~**Package as a Claude Code plugin**~~ — T-1–T-4 done, T-5 declined,
   2026-09-10; renamed `design-docs-template` → `design-docs` the same day
   (open question §5.1 in [`PLUGIN_PACKAGING.md`](PLUGIN_PACKAGING.md)
   closed). See below.
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

## Plugin packaging T-1–T-4 (2026-09-10)

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

T-5 (marketplace entry) was declined: `--plugin-dir` already covers this
repo's actual consumers. T-4 (`skills/design-pipeline/SKILL.md`, an
orchestrator skill invocable as `/design-docs-template:design-pipeline` at
the time) was then built and smoke-tested live: a fresh brief drove
straight into `design-doc-author`, which produced a full `DESIGN.md` and
stopped only at the test sandbox's own write-permission prompt. Bumped
`plugin.json` to 1.1.0 for the new skill.

**Renamed the plugin `design-docs-template` → `design-docs`** (same day,
per the user's request) — closes open question §5.1. The old name read as
a repo name, not a namespace; the invocation is now
`/design-docs:design-pipeline` and agents load as `design-docs:<agent-name>`.
Only `plugin.json`'s `name` field and the docs that quote the namespace
needed updating — nothing else hardcoded it.

## Conventions

- Offline-first: no CDNs, no external fonts/scripts/images. `lib/mermaid.min.js`
  is vendored on purpose.
- All colors come from CSS tokens in `lib/doc.css` — never hard-code hex in
  markup.
- Why-first prose: rationale sits next to the decision it explains.
- Stable IDs, never renumbered: `FR-*` / `NFR-*` (requirements), `DD-*` (design
  decisions), `T-*` (tasks). Dropped items are marked withdrawn, not deleted.

## Overview view (added after 2026-09-10)

Added `overview-author` (agent), `templates/OVERVIEW.template.md`, and
`DESIGN_DOC_INSTRUCTIONS.md` §12: a derived, tables-and-diagrams-only
`OVERVIEW.md` for PMs/management, rendered to `overview.html` by
`html-suite-builder`. `TASKS.md` milestones gain an optional `Status` column.
Plugin version bumped to 1.2.0.

Dry run (rebuilt `mdtoc` sources, deliberately verbose milestone rows): the
overview compressed a ~90-word milestone row to one sentence + status, counts
audited correct, and it flagged a source gap (component in diagram, no
Components entry). It exposed 9 rule ambiguities — risk source, open vs
resolved counts, Gantt without durations, date, link form, etc. — settled in
`overview-author.md` rule 9 and the template. Re-run after further prompt
changes; HTML rendering of `overview.html` is still untested.

**HTML render test (mdtoc):** all 6 pages open from `file://` with 0 external
requests, 0 console errors, Mermaid renders, no page-level horizontal scroll.
Fixes it drove: `html-suite-builder` lacked Bash (could not copy
`mermaid.min.js`); no stat-tile component (added `.stat-strip`/`.stat` to
`doc.css`, §6.4); no status-word→pill mapping (§6.4); no ID-anchor convention
(§12.3: lowercase ids, every Ref linked); `overview.html` exempted from the
open-High gate since it displays that state. Known remaining: sources with
gaps in section numbering (e.g. §3, §4, §6) make the builder hack `.toc`
numbering with inline `counter-set` — not yet given a sanctioned class.

**Real-project run (`SampleDocs/`, CLAWE UI):** `overview-author` produced
`SampleDocs/OVERVIEW.md` (12 milestones, 13 open decisions, 9 risks, 4
cross-document contradictions found) and `html-suite-builder` rendered
`SampleDocs/overview-html/overview.html` (0 external requests, diagram
renders). No `TASKS.md` exists there — the iteration timeline stood in. Found:
`dateFormat X` Gantt charts do not work in the vendored Mermaid (all bars
stack), so Gantt is now calendar-dates-only; Gantt label colours fixed in
`lib/mermaid-init.js`. Open: the page runs ~6 screens (13 decisions, 12
milestones) — longer than the §12 "two printed pages" target; no stand-in
rule yet for a missing `TASKS.md`; stale-SPEC_REVIEW handling is by agent
judgement only.

**Caps run (CLAWE):** §12.4 caps + key-row + Visuals applied. OVERVIEW.md
1,759 -> 1,392 words; iterations 1-4 collapsed to one row, M7 marked key;
risks 9->6, decisions 14->5, with "+N more" lines. Rendered page height
barely moved (6,192 -> 6,361 px) because the architecture diagram renders tall;
hand-built roadmap is 5,672 px with 5 mockups. Rule added: stale SPEC_REVIEW
-> "Not re-validated", never "Yes". Open: cap diagram height; decide whether
open decisions should be filtered to management-level ones (needs an owner
field in the source).

**Round 3 (CLAWE):** architecture diagram forced to `graph LR` <= 8 nodes in a
`.diagram-container.compact` (max 260 px svg; container ~365 px, was ~700);
milestone chart removed (table only); Visuals now a `.thumb-row`; open
questions gain **Owner** + **Level (Management|Technical)** in DESIGN/
REQUIREMENTS templates, `design-doc-author`, `spec-validator` (missing =
Low finding), and `overview-author` rule 10 (Management first; falls back to
earliest-milestone-blocked when the source lacks the fields — CLAWE's
DESIGN.md §10 does, so its Owner column is inferred from "Resolved by"
prose). Risk order: risks touching not-yet-Done milestones rank first. Page
height 6,361 -> 5,436 px (hand-built roadmap: 5,672 with 5 mockups).
Not done: the CLAWE DESIGN.md itself has no Owner/Level fields (user's
document; left unedited).
