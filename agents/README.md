# Design-docs pipeline agents

Five Claude Code subagents that take a project from a plain-language brief to a
polished offline HTML design-doc suite. They share the structural and style rules
in `../DESIGN_DOC_INSTRUCTIONS.md` (§9 and §11).

| Agent | Reads | Writes | Edits |
|---|---|---|---|
| [`design-doc-author`](design-doc-author.md) | the user's brief + codebase | `DESIGN.md` | — |
| [`requirements-author`](requirements-author.md) | `DESIGN.md` + user input | `REQUIREMENTS.md` | — |
| [`tasks-planner`](tasks-planner.md) | `DESIGN.md` + `REQUIREMENTS.md` | `TASKS.md` | `REQUIREMENTS.md` §7 only |
| [`spec-validator`](spec-validator.md) | all three | `SPEC_REVIEW.md` | nothing (report only) |
| [`html-suite-builder`](html-suite-builder.md) | the approved `.md` set | `design-docs/` HTML suite | — |

```
brief → design-doc-author → DESIGN.md
                              → requirements-author → REQUIREMENTS.md
                                → tasks-planner → TASKS.md
                                  → spec-validator → SPEC_REVIEW.md
                                    → (fix findings, re-run authors + validator)
                                      → html-suite-builder → design-docs/index.html …
```

Each stage is a checkpoint: review the Markdown, then run the next agent. The
authoring agents stay in their lane — `requirements-author` will not silently
expand scope, `spec-validator` will not edit the specs.

## Installing them in a project

Claude Code discovers subagents in `.claude/agents/` at the project root. Point
that directory at these files:

**macOS / Linux — symlink (updates flow through):**
```bash
mkdir -p .claude/agents
ln -s ../../design-docs-template/agents/*.md .claude/agents/
```

**Windows (PowerShell, Developer Mode or admin) — symlink:**
```powershell
New-Item -ItemType Directory -Force .claude\agents | Out-Null
Get-ChildItem design-docs-template\agents\*.md |
  ForEach-Object { New-Item -ItemType SymbolicLink -Path ".claude\agents\$($_.Name)" -Target $_.FullName }
```

**Any OS — copy (re-copy to update):**
```bash
mkdir -p .claude/agents && cp design-docs-template/agents/*.md .claude/agents/
```

Do **not** copy `README.md` or `templates/` into `.claude/agents/` — only the
five agent files. Then invoke by name, e.g. *"Use design-doc-author to draft a
design for …"*.

## Templates

`templates/` holds Markdown skeletons matching the outlines in
`DESIGN_DOC_INSTRUCTIONS.md` §11.3. The agents start from these when present, so
edit them to set house defaults (extra sections, a standard NFR list, etc.).
