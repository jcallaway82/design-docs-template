# Design Docs Template

A reusable design-documentation system for any software project: a set of Markdown
authoring agents plus an offline HTML rendering system, sharing one visual language and
one set of structural rules.

Give `DESIGN_DOC_INSTRUCTIONS.md` to an AI agent (or a human) to generate polished,
fully-offline HTML design documents and API references. Or run the agent pipeline in
`agents/` to go from a plain-language brief to `DESIGN.md` → `REQUIREMENTS.md` →
`TASKS.md`, validate them, and render the HTML suite.

## Contents

| File | Purpose |
|---|---|
| `DESIGN_DOC_INSTRUCTIONS.md` | **The instruction document.** Pass this to agents. Covers archetypes, suite structure, design tokens, components, offline Mermaid, writing style, the Markdown working-document rules (§11), and a QA checklist. |
| `template.html` | Narrative-page skeleton **and** live component gallery — open it in a browser to see every component rendered. Copy to start a new document. |
| `template-interactive.html` | Interactive reference-browser skeleton (sidebar tree, search, theme toggle, cross-links). Single file, self-contained. Replace its `ITEMS` data object. |
| `lib/doc.css` | Canonical shared stylesheet (design tokens + all components). |
| `lib/mermaid.min.js` | Offline Mermaid bundle (~2.7 MB) — required for diagrams to render without a network. |
| `lib/mermaid-init.js` | Shared Mermaid dark-theme configuration. |
| `lib/lightbox.js` | Click-to-enlarge overlay for diagrams (no markup needed). |
| `lib/nav.js` | Shared sticky nav bar — edit its `links` array once per suite. |
| `agents/` | Subagent definitions for the authoring pipeline, plus `agents/templates/` Markdown skeletons. See `agents/README.md`. |

## The agent pipeline

```
brief ──▶ design-doc-author ──▶ DESIGN.md
                                   │
              user input ──────────┤
                                   ▼
                          requirements-author ──▶ REQUIREMENTS.md
                                   │
                                   ▼
                            tasks-planner ──▶ TASKS.md
                                   │
                                   ▼
                           spec-validator ──▶ SPEC_REVIEW.md   (report only, no edits)
                                   │
                          (address findings, iterate)
                                   ▼
                         html-suite-builder ──▶ index.html + per-section pages + lib/
```

| Agent | Reads | Writes |
|---|---|---|
| `design-doc-author` | the user's prompt / brief | `DESIGN.md` |
| `requirements-author` | `DESIGN.md` + user input | `REQUIREMENTS.md` |
| `tasks-planner` | `DESIGN.md` + `REQUIREMENTS.md` | `TASKS.md` |
| `spec-validator` | all three | `SPEC_REVIEW.md` (findings only) |
| `html-suite-builder` | the approved Markdown set + `DESIGN_DOC_INSTRUCTIONS.md` | the offline HTML suite |

## Using it in a project

1. Copy this whole folder into the project (e.g. `<project>/design-docs-template/`), or
   keep it as a submodule / symlink.
2. Make the agents discoverable: symlink or copy `agents/*.md` into the project's
   `.claude/agents/` directory (`design-docs-template/agents/README.md` has the one-liners
   for macOS/Linux/Windows).
3. Invoke `design-doc-author` with your brief. Review `DESIGN.md`, then run the next agent.
4. When the Markdown set is approved, run `html-suite-builder`, then work the §10
   checklist in `DESIGN_DOC_INSTRUCTIONS.md`.

**HTML suite in 3 steps (manual path):** copy `lib/` + `template.html` into a new folder,
rename to `index.html`, edit the `EDIT ME` links in `lib/nav.js`. Details in the
instructions, Appendix A.
