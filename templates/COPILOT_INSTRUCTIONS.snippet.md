## Design documentation

- Design docs live in `{{DOCS_DIR}}/`. House rules are in
  `{{TEMPLATE_DIR}}/DESIGN_DOC_INSTRUCTIONS.md` (§9 writing style, §11 Markdown
  working-document structure; §3–§10 govern the HTML).
- Pipeline order — one custom agent per stage, never skip ahead, and stop for
  human review between stages: `design-doc-author` → `DESIGN.md` →
  `requirements-author` → `REQUIREMENTS.md` → `tasks-planner` → `TASKS.md` →
  `spec-validator` → `SPEC_REVIEW.md` → `html-suite-builder` → HTML suite
  (optionally `overview-author` → `OVERVIEW.md`).
- Agents stay in their lane: `requirements-author` does not expand scope;
  `spec-validator` reports and never edits the specs.
- IDs are stable and never renumbered: `FR-*`, `NFR-*`, `DD-*`, `T-*`.
- Write why-first prose, use precise numbers over vague words, and enumerate
  failure modes.
- HTML output is offline-only: no CDNs, no external fonts, scripts or images;
  all colors come from the CSS tokens in `{{TEMPLATE_DIR}}/lib/doc.css`.
- Do not edit `.github/agents/*.agent.md` by hand; they are generated from
  `{{TEMPLATE_DIR}}/agents/*.md` by `{{TEMPLATE_DIR}}/scripts/export-copilot.py`.
