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
| `agents/` | The six pipeline subagent definitions — nothing else lives in this directory (see below on why). |
| `templates/` | Markdown skeletons (`DESIGN.template.md`, `REQUIREMENTS.template.md`, `TASKS.template.md`, `OVERVIEW.template.md`) matching `DESIGN_DOC_INSTRUCTIONS.md` §11.3. The agents start from these when present. |
| `.claude-plugin/plugin.json` | Plugin manifest — lets a project install the six agents with `--plugin-dir` (or a marketplace, once one exists) instead of copying files. |

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

   (optional, from the same approved set)
                          overview-author ──▶ OVERVIEW.md ──▶ overview.html
```

| Agent | Reads | Writes | Edits |
|---|---|---|---|
| [`design-doc-author`](agents/design-doc-author.md) | the user's prompt / brief + codebase | `DESIGN.md` | — |
| [`requirements-author`](agents/requirements-author.md) | `DESIGN.md` + user input | `REQUIREMENTS.md` | — |
| [`tasks-planner`](agents/tasks-planner.md) | `DESIGN.md` + `REQUIREMENTS.md` | `TASKS.md` | `REQUIREMENTS.md` §7 only |
| [`spec-validator`](agents/spec-validator.md) | all three | `SPEC_REVIEW.md` | nothing (report only) |
| [`html-suite-builder`](agents/html-suite-builder.md) | the approved Markdown set + `DESIGN_DOC_INSTRUCTIONS.md` | the offline HTML suite | — |
| [`overview-author`](agents/overview-author.md) | the approved Markdown set | `OVERVIEW.md` (tables/diagrams only, for PMs and management) | nothing (derived view) |

Each stage is a checkpoint: review the Markdown, then run the next agent. The
authoring agents stay in their lane — `requirements-author` will not silently
expand scope, `spec-validator` will not edit the specs.

## Installing the agents in a project

`agents/` holds exactly the six files above — nothing else — because Claude
Code's plugin loader treats *every* `.md` file under an `agents/` directory
as an agent definition, recursively. A stray `README.md` or a `templates/`
subfolder in there gets registered as a broken agent with no name or
description. That's also why `templates/` lives at the repo root instead of
`agents/templates/`.

**Plugin (recommended) — no copying, updates by re-pulling this repo:**
```bash
claude --plugin-dir /path/to/design-docs-template
```
Claude Code loads all six agents namespaced as `design-docs:<agent-name>`
(e.g. `design-docs:design-doc-author`) for that session, plus the
`/design-docs:design-pipeline` skill — invoke it with a fresh brief for a
guided walk through all six stages instead of naming each agent yourself.
Add the flag multiple times to load other plugins alongside it, or point it
at a project that vendors this repo as a subfolder/submodule. There is no
marketplace entry yet — see `PLUGIN_PACKAGING.md` if you want to add one.

**Symlink (macOS/Linux) — updates flow through automatically:**
```bash
mkdir -p .claude/agents
ln -s ../../design-docs-template/agents/*.md .claude/agents/
```

**Symlink (Windows, PowerShell, Developer Mode or admin):**
```powershell
New-Item -ItemType Directory -Force .claude\agents | Out-Null
Get-ChildItem design-docs-template\agents\*.md |
  ForEach-Object { New-Item -ItemType SymbolicLink -Path ".claude\agents\$($_.Name)" -Target $_.FullName }
```

**Copy (any OS) — re-copy to pick up updates:**
```bash
mkdir -p .claude/agents && cp design-docs-template/agents/*.md .claude/agents/
```

Whichever method you use, only the six files in `agents/*.md` land in
`.claude/agents/` — the glob above only matches that directory's top level,
and `templates/` is no longer inside it. Then invoke by name, e.g. *"Use
design-doc-author to draft a design for …"*.

## Using the agents with GitHub Copilot

The agents are Claude Code subagents, but their prompt bodies are plain
Markdown. `scripts/export-copilot.py` converts them into Copilot custom agents
(`tools:` mapped to Copilot aliases, `model:` dropped, body copied verbatim):

```bash
# from the project root, with this repo vendored at ./design-docs-template/
python3 design-docs-template/scripts/export-copilot.py
```

That writes `.github/agents/<name>.agent.md` for all six agents; commit them
and they appear in Copilot's agent picker. `--out DIR` changes the target and
`--check` exits 1 if the generated files are stale (useful in CI). Always edit
`agents/*.md` and re-run — never the generated files. Keep the repo (or at
least `DESIGN_DOC_INSTRUCTIONS.md` and `templates/`) in the project, since the
agents read those by name. Copilot has no automatic stage hand-off, so run
the stages in order yourself, and verify the frontmatter against GitHub's
current custom-agents docs if a field is rejected.

## Using it in a project

1. Copy this whole folder into the project (e.g. `<project>/design-docs-template/`), or
   keep it as a submodule / symlink — or skip copying entirely and use the plugin
   install method above.
2. Make the agents discoverable (see "Installing the agents" above).
3. Invoke `design-doc-author` with your brief. Review `DESIGN.md`, then run the next agent.
4. When the Markdown set is approved, run `html-suite-builder`, then work the §10
   checklist in `DESIGN_DOC_INSTRUCTIONS.md`.

**HTML suite in 3 steps (manual path):** copy `lib/` + `template.html` into a new folder,
rename to `index.html`, edit the `EDIT ME` links in `lib/nav.js`. Details in the
instructions, Appendix A.
