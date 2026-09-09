# Design Document Instructions

**Audience:** AI agents (and humans) generating design documents, technical specs, and API references for any software project.
**Output format:** polished, self-contained HTML that renders perfectly offline.
**Companion assets:** this file lives in the `design-docs-template/` folder alongside `template.html` (narrative-page skeleton + live component gallery), `template-interactive.html` (interactive reference browser skeleton), `lib/` (shared stylesheet, offline Mermaid bundle, init/lightbox/nav scripts), and `agents/` (subagent definitions for the Markdown → HTML authoring pipeline). Copy them when starting a new document suite. If you only have this file, everything needed to regenerate the system is in the appendices.

**Two ways in:** author HTML directly from `template.html` (this document, §5 onward), or run the agent pipeline — `DESIGN.md` → `REQUIREMENTS.md` → `TASKS.md` as Markdown, validated, then rendered to the HTML suite. The Markdown documents follow the same structural rules as the HTML pages (§11). The pipeline is described in `agents/README.md`.

---

## 1. Mission & core principles

You are producing engineering design documentation that a reader can open from disk, years later, on an air-gapped machine, and immediately understand. Every decision below serves four principles:

1. **Offline-first, zero dependencies.** Documents must render fully from `file://` with no network access. No CDNs, no Google Fonts, no external images, no analytics. Mermaid renders from a local `lib/mermaid.min.js`. This is a hard requirement, not a preference.
2. **Intuitive at first glance.** A reader should orient in seconds: title → one-line subtitle → version/status/date → table of contents → numbered sections. Diagrams are visual anchors; tables carry the dense facts; prose explains the *why*.
3. **One visual system.** Every document in every suite uses the same dark GitHub-style palette, the same badge shapes, the same table treatment, the same callouts. A reader moving between documents should never feel a style change.
4. **Explain the why, not just the what.** The highest-value content is design rationale: why a field lives where it does, why an alternative was rejected, why a timeout is 10 s. Use cross-notes and feature boxes to put rationale next to the facts it justifies.

---

## 2. Document archetypes

Choose one of two archetypes per page. Both share the same tokens and palette.

### Archetype A — Narrative document (default)

A centered reading column (960 px; 1200 px for table-heavy pages) with numbered sections, Mermaid diagrams, tables, and callouts. Use for: design overviews, protocol phase descriptions, sequence-diagram pages, failure matrices, ADRs, migration guides. Start from `template.html`.

### Archetype B — Interactive reference browser

A full-viewport app shell: sticky header with live search, collapsible sidebar tree, content pane, light/dark theme toggle. All data lives in a single JS object; navigation, search, breadcrumbs, cross-links, and backlinks derive from it automatically. Use for: message/schema references (protobuf, JSON schemas), API endpoint catalogs, config references — anything with dozens of interlinked records a reader will *look things up in* rather than read linearly. Start from `template-interactive.html`.

**Rule of thumb:** if readers read it top-to-bottom, use A. If they search it, use B. A suite typically has one index page and many A-pages, plus at most one or two B-pages for the big references.

---

## 3. Suite structure & file conventions

A document suite is a folder that stands alone (can be zipped and emailed):

```
My Project Design/
├── index.html                  ← hub / entry point (Archetype A)
├── Sequence Diagrams/
│   ├── Project_Sequence_Phase0_Init.html
│   └── Project_Sequence_Phase1_Launch.html
├── Errors/
│   └── Project_Failure_Matrix_Phase.html
├── Reference/
│   └── Project_Message_Reference.html      ← Archetype B
└── lib/
    ├── doc.css                 ← shared stylesheet (Appendix B)
    ├── mermaid.min.js          ← offline Mermaid bundle (~2.7 MB)
    ├── mermaid-init.js         ← shared Mermaid config (Appendix C)
    ├── lightbox.js             ← click-to-enlarge for diagrams
    └── nav.js                  ← shared nav bar (edit links array once)
```

Conventions:

- **`index.html` is the hub.** It gives the overview, the architecture diagram, the phase/section table, and a card grid linking to every child document. Every child document is reachable from it.
- **File names:** `Project_Topic_Subtopic.html`, underscores, Title_Case words. Folder names are plain English with spaces, grouped by category.
- **Every page links `lib/doc.css`** (adjust relative depth: `lib/doc.css` vs `../lib/doc.css`) rather than duplicating styles. A one-off standalone document (no suite) may instead inline the full stylesheet from Appendix B into a `<style>` block — never link to files outside its own folder tree.
- **The nav bar** (`lib/nav.js`) defines the suite's page list once; every page gets a sticky top nav with the active page highlighted. Include it right after `<body>`:
  ```html
  <div id="page-nav"></div>
  <script src="../lib/nav.js"></script>
  ```
- **Cross-links between pages are mandatory.** Failure matrices link to sequence diagrams and vice versa; references link back to the concepts that use them. Use relative paths only.
- **`lib/mermaid.min.js`:** copy it from `design-docs-template/lib/` (or any existing suite). If genuinely unavailable, obtain the Mermaid UMD build once (npm package `mermaid`, file `dist/mermaid.min.js`) and save it locally. Never reference a CDN URL in a page.

---

## 4. Design tokens

All colors come from CSS variables defined in `doc.css`. Never hard-code a hex value in page markup when a token exists.

### Surfaces & text

| Token | Value | Use |
|---|---|---|
| `--bg` | `#0d1117` | Page background |
| `--bg-raised` | `#161b22` | Cards, containers, table headers |
| `--bg-inset` | `#1c2129` | Inline-code background, deepest wells |
| `--border` | `#30363d` | Primary borders |
| `--border-light` | `#21262d` | Subtle row separators |
| `--text` | `#c9d1d9` | Body text |
| `--text-muted` | `#7d8590` | Secondary text, captions, table headers |
| `--text-bright` | `#e6edf3` | Headings, `<strong>` |

### Semantic accents — use by meaning, never decoratively

| Token | Value | Meaning |
|---|---|---|
| `--accent` (blue) | `#58a6ff` | Links, primary actions, informational, Low severity |
| `--green` | `#56d364` | Success, running/healthy, Resume recovery, Medium severity |
| `--amber` | `#d29922` | Warning, caution, Retry recovery, High severity, Draft status |
| `--red` | `#f47067` | Critical, danger, Abort recovery, breaking changes, infrastructure failures |
| `--purple` | `#b48eff` | Special states, Degrade recovery, handshake/contract phases, cross-notes |
| `--teal` | `#39d2c0` | Error codes, identifiers, numbering schemes |

Each accent has a matching dark "tint" background for badges (`--tint-blue: #1a3a5c`, `--tint-green: #1a3528`, `--tint-amber: #3b2e12`, `--tint-red: #3c1520`, `--tint-purple: #2a1f4e`, `--tint-teal: #1a3040`, `--tint-neutral: #1c2129`) and callouts use near-black wells (`--well-blue: #111a2e`, `--well-amber: #1a1710`, `--well-red: #1a1012`, `--well-green: #101a14`).

### Fonts

- Body: `"Segoe UI", system-ui, -apple-system, sans-serif`
- Mono: `"Cascadia Code", "Fira Code", "JetBrains Mono", Consolas, monospace`

System fonts only — never load font files.

---

## 5. Page anatomy (Archetype A)

Every narrative page follows this order exactly:

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Project — Page Title</title>
<link rel="stylesheet" href="../lib/doc.css">
</head>
<body>

<div id="page-nav"></div>
<script src="../lib/nav.js"></script>

<h1>Page Title — Design Document</h1>
<p class="subtitle">One line: what this covers, which components talk to which</p>
<div class="doc-meta">
  <span><strong>Version:</strong> 1.0</span>
  <span><strong>Status:</strong> Draft</span>
  <span><strong>Date:</strong> August 2026</span>
</div>

<!-- TOC (index/long pages only — pages under ~3 sections may omit) -->

<!-- Numbered h2 sections: 1. Overview … N. Changelog -->

<script src="../lib/mermaid.min.js"></script>
<script src="../lib/mermaid-init.js"></script>
<script src="../lib/lightbox.js"></script>
</body>
</html>
```

Rules:

- **`<h1>` once per page.** Section headings are numbered `<h2 id="anchor">1. Title</h2>`; sub-headings `<h3>` (unnumbered). TOC entries link to the `h2` ids.
- **The doc-meta line is mandatory** — Version, Status (Draft / In Review / Approved), Date. Bump version and add a changelog entry on every substantive edit.
- **First section is always "1. Overview":** 2–4 paragraphs — what the document covers, the cast of components (bold on first mention), and how this page relates to sibling documents.
- **Last section is always the Changelog** (see §6.9).
- **Scope callout:** detail pages (sequence diagrams, matrices) open with a `.note` telling the reader where this page sits in the flow and linking to prerequisites — the "How to read this document" pattern.
- Scripts load at the end of `<body>`, local files only. Omit the Mermaid pair on pages without diagrams; keep order `mermaid.min.js` → `mermaid-init.js` → `lightbox.js`.
- **Table-heavy pages** add `class="wide"` to `<body>` for a 1200 px column.

---

## 6. Component catalog

All classes below are defined in `doc.css`. `template.html` renders every one of them — check it when unsure how something should look.

### 6.1 Table of contents

```html
<div class="toc">
  <h4>Contents</h4>
  <ol>
    <li><a href="#overview">Overview</a></li>
    <li><a href="#phases">Protocol Phases</a></li>
  </ol>
</div>
```

The `<ol>` auto-numbers via CSS counters — numbers must match the `h2` numbering.

### 6.2 Card grid — visual index of child documents

```html
<div class="card-grid">
  <div class="card">
    <h4><span class="badge badge-blue">Phase 1</span> Script Launch</h4>
    <p>RUN command, subprocess spawn, worker connects back.</p>
    <a href="Sequence Diagrams/Project_Sequence_Phase1.html">View diagram →</a>
  </div>
</div>
```

One card per child page; short description; link text is an action ("View diagram →", "View matrix →").

### 6.3 Tables

Tables are the workhorse. Header cells are auto-styled (uppercase, small, muted). Conventions:

- Set explicit widths on all but the widest column: `<th style="width:12%">`.
- Rows may carry a bold name plus a muted detail line:
  ```html
  <td><span class="row-name">Core unreachable</span>
      <div class="detail">Connection refused or 10 s timeout.</div></td>
  ```
- Error codes / identifiers: `<span class="err-code">1404</span>`; numeric values in prose tables: `<span class="mono-val">10 s</span>`.
- Follow any counted table with a totals line:
  ```html
  <p class="table-footnote">Total: <strong>21 generic failure modes</strong> across six phases.</p>
  ```
- `table-layout: fixed` via `class="fixed"` when long content should wrap rather than stretch columns.

### 6.4 Badges, status pills, legend

**Badges** (rectangular, for categories): `badge badge-blue|badge-green|badge-amber|badge-red|badge-purple|badge-teal|badge-neutral`.
Severity/recovery aliases keep markup semantic: `severity sev-critical|sev-high|sev-medium|sev-low`, `recovery rec-abort|rec-retry|rec-resume|rec-degrade`.

**Status pills** (rounded, for lifecycle): `status s-draft|s-review|s-complete|s-planned|s-deprecated`, placed after the thing they describe.

**Legend strip** — required above any table using severity/recovery badges:

```html
<div class="legend">
  <div class="legend-section">
    <h5>Severity</h5>
    <div class="legend-items">
      <span class="severity sev-critical">Critical</span>
      <span class="severity sev-high">High</span>
      <span class="severity sev-medium">Medium</span>
      <span class="severity sev-low">Low</span>
    </div>
  </div>
</div>
```

Color-to-meaning mapping is fixed suite-wide (see §4). Never repurpose a color.

### 6.5 Callouts

```html
<div class="note"><strong>Scope:</strong> …</div>       <!-- blue: scope, how-to-read, info -->
<div class="warn"><strong>Caution:</strong> …</div>     <!-- amber: gotchas, surprising behavior -->
<div class="danger"><strong>Breaking:</strong> …</div>  <!-- red: breaking changes, hard failures -->
<div class="success"><strong>Resolved:</strong> …</div> <!-- green: confirmed decisions -->
```

Every callout opens with a bold label word. Keep callouts short — 1–3 sentences; longer material belongs in a feature box.

### 6.6 Cross-note — design rationale in place

```html
<div class="cross-note">
  <strong>Why this lives here:</strong> the mode-level list is the site-wide
  stylesheet; lower scopes are more specific rules — like CSS.
</div>
```

Use wherever a reader would ask "why is it like this?" — duplicated fields, precedence rules, rejected alternatives. This is the pattern that makes these documents good; use it liberally.

### 6.7 Feature box — bordered multi-paragraph spec block

```html
<div class="feature-box teal">
  <h3>Error Code Scheme — <code>CPNN</code></h3>
  <p>…prose, tables, lists…</p>
</div>
```

Variants: (default blue) general guidance; `teal` code/ID schemes; `amber` timing & cautionary implementation guidance; `purple` contracts; `red` hard constraints; `green` resolved designs.

### 6.8 Grouped sections (matrices, per-phase listings)

```html
<div class="phase-group">
  <div class="phase-header">
    <span class="phase-badge badge-blue">Phase 1</span>
    <span class="phase-title">Script Launch</span>
    <span class="section-count">3 failures</span>
  </div>
  <table>…</table>
</div>
```

### 6.9 Changelog — last section of every page

```html
<h2 id="changelog">7. Changelog</h2>
<div class="changelog">
  <div class="entry">
    <div class="date">August 2026 — v1.1</div>
    <div class="detail">Added Phase 4 timeout table; clarified RESET semantics.</div>
  </div>
  <div class="entry">
    <div class="date">February 2026 — v1.0</div>
    <div class="detail">Initial version.</div>
  </div>
</div>
```

Newest first. Every version bump in `doc-meta` gets an entry.

---

## 7. Mermaid diagrams (offline)

### 7.1 Setup

Diagrams are authored as Mermaid source in the page and rendered client-side by the **local** bundle:

```html
<div class="diagram-container">
  <pre class="mermaid">
sequenceDiagram
    participant UI as Client UI
    participant Core
    UI ->> Core: Command(RUN)
  </pre>
</div>
<p class="diagram-caption">Fig. 1 — Launch flow. Click to enlarge.</p>

<!-- end of body -->
<script src="../lib/mermaid.min.js"></script>
<script src="../lib/mermaid-init.js"></script>
<script src="../lib/lightbox.js"></script>
```

- `mermaid-init.js` configures the dark theme to match the palette, calls `mermaid.run()` after DOM load, and fires a `mermaid:rendered` event.
- `lightbox.js` then makes every `.diagram-container` click-to-enlarge (full-screen overlay, Esc/click-out to close) and shows a "🔍 Click to enlarge" affordance on hover. It needs no extra markup.
- The container provides the raised card look and `overflow-x: auto` so wide diagrams scroll instead of breaking the layout.
- If `mermaid.min.js` is missing, pages still load — diagrams show as raw source and a console error explains the fix. Don't ship in that state: the offline bundle is part of the deliverable.

### 7.2 Choosing a diagram type

| Content | Type | Notes |
|---|---|---|
| Component/architecture overview | `graph LR` with `subgraph` per component | Label edges with the channel/protocol (`A -- "REQ/REP<br/>RUN, STOP" --> B`) |
| Message flows over time | `sequenceDiagram` | One page per flow; use `alt`/`else` for success/failure branches, `Note over` for user actions and milestones |
| Lifecycle/status rules | `stateDiagram-v2`, `direction LR` | Annotate transitions with trigger + effect (`RUNNING --> PAUSED : PAUSE\nhardware pauses`) |
| Data model relationships | `erDiagram` or Archetype B instead | Prefer the interactive browser once entities exceed ~8 |

### 7.3 Legibility rules

- **One idea per diagram.** Cap sequence diagrams at ~6 participants and ~20 messages; split longer flows into phases (that's why suites have per-phase pages).
- Keep labels short; use `<br/>` (flowcharts) or `\n` (state/sequence) for two-line labels.
- Every diagram sits in a `.diagram-container`; add a `.diagram-caption` when the page has more than one diagram (Fig. N — description).
- Always pair a state diagram with a table listing each state: terminal?, meaning, transitions out (see `template.html` §2 and the state table pattern).
- Diagrams complement tables and prose — every diagram's content must also be stated in text or a table so the page is searchable and readable if rendering ever fails.

---

## 8. Interactive reference browser (Archetype B)

Start from `template-interactive.html` — a single self-contained file, no `lib/` dependencies. Replace the `ITEMS` data object; the engine below it generally needs no edits.

Required features (all present in the template — don't remove them):

- **Sticky header:** title + version, live search box, Home button, light/dark theme toggle (persisted to `localStorage`).
- **Sidebar tree** built from `parent` relationships; active item highlighted; hidden rows while searching.
- **Search** filters by item name, field name, and field description.
- **Hash routing** (`#ItemName`) so views are linkable/bookmarkable.
- **Breadcrumbs** from root to the current item.
- **Type click-through:** a field whose type is another item renders as a clickable badge.
- **"Used by" backlinks** computed automatically at the bottom of each item.

Data conventions per item:

- `plain`: one-sentence plain-English summary, shown bold under the title. Write it for a newcomer ("The 'index card' for one radar in the library").
- `desc`: full prose, why-first.
- Fields carry **name, type, cardinality, units, description**. Cardinality is one of `1`, `0..1`, `0..N`, `1..N` — rendered as required/optional/repeated badges. Units always live in the units slot (`Hz`, `ns`, `dBm`, `degrees`, `—` if unitless), never only buried in prose.
- Deprecated fields stay listed, marked `⚠ DEPRECATED` in the description with the migration path.

If the reference needs Mermaid diagrams, load the same three scripts and call `mermaid.run()` after each render that injects diagram source.

---

## 9. Writing style

- **Voice:** confident, direct, present tense. "The Plugin binds the ROUTER socket." Not "The Plugin should probably bind…".
- **Why-first.** Every non-obvious decision gets its rationale nearby (cross-note, feature box, or a "Why X" subsection like "Why ZMQ"). If you compared alternatives, show the comparison as a table.
- **Bold sparingly, purposefully:** component names on first mention, key terms, the lead word of callouts. `<code>` for every identifier: message names, fields, commands, error codes, file names.
- **Precision over vagueness:** "10 s command timeout", "every 200 ms", "21 generic failure modes" — never "a short timeout", "periodically", "several".
- **Counted claims are audited:** if the page says 21 failures, the tables must contain exactly 21 rows, and the totals footnote restates it.
- **Reader orientation:** reference pages open with a "How to read this document" note; alternate views of the same data (by-phase vs by-channel) link to each other and state that they contain the same items.
- **Terminal-state honesty:** specs define both success and failure paths. Every operation's failure modes, severities, and recovery strategies are enumerated — a design doc without failure handling is incomplete.

---

## 10. Quality checklist

Before delivering, verify every item:

- [ ] Opens from `file://` with the network disabled — zero external requests (fonts, scripts, images, CSS).
- [ ] All Mermaid diagrams render; lightbox zoom opens and closes (click, ×, Esc).
- [ ] `lib/mermaid.min.js` present in the suite (~2.7 MB — if the lib folder is tiny, you forgot it).
- [ ] Every internal link resolves (nav, TOC anchors, cross-page links, card links) — relative paths only.
- [ ] `doc-meta` present (Version / Status / Date); changelog section exists and matches the version.
- [ ] TOC numbering matches `h2` numbering.
- [ ] All colors via tokens; badge colors match the fixed semantic mapping (§4).
- [ ] Tables: header widths set, badge tables have a legend, counted tables have a totals footnote.
- [ ] Wide content (tables, diagrams) scrolls inside its container — no horizontal scroll on the page body.
- [ ] Hover states work: cards, table rows, nav links, diagram zoom affordance.
- [ ] index.html links every child page; every child page's nav highlights the active entry.
- [ ] No lorem ipsum, no placeholder links (`href="#"`) in delivered documents.

---

## 11. Markdown working documents (the agent pipeline)

Before a project has a polished HTML suite it has a set of **Markdown working documents** that the design agents produce and iterate on. They are plain `.md` files at the project root (or in `docs/`), version-controlled with the code, and readable in any editor or PR diff. When the design stabilizes, the HTML-suite builder renders them into an Archetype-A suite.

### 11.1 The three documents

| File | Produced by | Reads | Purpose |
|---|---|---|---|
| `DESIGN.md` | `design-doc-author` | the user's prompt / brief | The *what* and the *why*: problem, goals, architecture, component responsibilities, key flows, design decisions with rejected alternatives, failure modes, open questions. |
| `REQUIREMENTS.md` | `requirements-author` | `DESIGN.md` + user input | Numbered, individually testable functional and non-functional requirements, each traced back to a design section, each with acceptance criteria. |
| `TASKS.md` | `tasks-planner` | `DESIGN.md` + `REQUIREMENTS.md` | An ordered, dependency-aware implementation breakdown. Each task cites the requirement IDs it satisfies and has its own acceptance criteria. |

A fourth agent, `spec-validator`, reads all three and writes `SPEC_REVIEW.md` — a findings report (gaps, contradictions, untestable requirements, orphaned design decisions, traceability holes). It never edits the documents. A fifth agent, `html-suite-builder`, converts the approved Markdown set into the HTML suite per §3–§10.

### 11.2 Shared structural rules (all three documents)

The Markdown documents obey the same principles as the HTML pages (§1, §9):

- **Front matter block** at the top: one-line description, then `**Version:** · **Status:** Draft | In Review | Approved · **Updated:** <Month Year>`. Bump the version and add a changelog entry on every substantive edit.
- **First section is `## 1. Overview`** — 2–4 paragraphs: what the document covers, the cast of components (**bold** on first mention), how it relates to its sibling documents.
- **Numbered `##` sections**, `###` sub-headings unnumbered. A short table of contents for documents over ~5 sections.
- **Last section is `## N. Changelog`** — newest first, one entry per version bump: `- **v1.1 — March 2026** — Added retry budget to FR-7; split task 4.`
- **Why-first.** Every non-obvious decision carries its rationale next to it — a `> **Why:**` blockquote is the Markdown equivalent of the HTML cross-note. Rejected alternatives are shown, ideally as a small comparison table.
- **Precision over vagueness** — "200 ms", "3 retries", "12 endpoints", never "fast", "a few", "several".
- **Counted claims are audited** — if the text says 14 requirements, the list has exactly 14, and any summary line restates it.
- **Terminal-state honesty** — every operation's failure modes, severities, and recovery strategies are enumerated. A design without failure handling is incomplete.
- **Mermaid** diagrams are authored in fenced ` ```mermaid ` blocks (they survive the HTML conversion unchanged) and every diagram's content is also stated in prose or a table.
- **Stable IDs** — requirements are `FR-<n>` / `NFR-<n>`, tasks are `T-<n>` (or `<milestone>.<n>`), design decisions are `DD-<n>`. IDs are never renumbered once assigned; a dropped item is marked `withdrawn`, not deleted.

### 11.3 Per-document outline

**`DESIGN.md`** — `1. Overview` · `2. Goals & non-goals` · `3. Context & constraints` · `4. Architecture` (component Mermaid diagram + prose) · `5. Components` (one `###` per component: responsibility, interfaces, owned data) · `6. Key flows` (sequence diagrams) · `7. Design decisions` (`DD-<n>`: decision, rationale, alternatives rejected, consequences) · `8. Data model` (if applicable) · `9. Failure modes & recovery` · `10. Open questions` · `11. Changelog`.

**`REQUIREMENTS.md`** — `1. Overview` (scope + link to `DESIGN.md`) · `2. Definitions` · `3. Functional requirements` (`FR-<n>`: statement using SHALL, rationale, acceptance criteria, traces-to design section) · `4. Non-functional requirements` (`NFR-<n>`: measurable target + method of verification) · `5. Constraints & assumptions` · `6. Out of scope` · `7. Traceability matrix` (requirement ID → design section → task ID, filled in as `TASKS.md` lands) · `8. Open questions` · `9. Changelog`.

**`TASKS.md`** — `1. Overview` (links to both upstream docs) · `2. Milestones` · `3. Tasks` (`T-<n>`: goal, files/areas touched, `depends on:`, `satisfies:` FR/NFR IDs, acceptance criteria, rough size S/M/L) · `4. Dependency graph` (optional Mermaid) · `5. Risks & mitigations` · `6. Changelog`.

### 11.4 Rendering to HTML

`html-suite-builder` maps each Markdown document to an Archetype-A page: front matter → `<h1>` + `.subtitle` + `.doc-meta`; `> **Why:**` blockquotes → `.cross-note`; failure tables → the severity/recovery legend + badges; ` ```mermaid ` blocks → `.diagram-container`; the changelog section → the `.changelog` component. The result passes the §10 checklist. Skeleton Markdown files matching these outlines live in `agents/templates/`.

---

## Appendix A — Bootstrapping a new suite

1. Copy `design-docs-template/lib/` into the new suite folder.
2. Copy `template.html` → rename to `index.html`; strip the gallery sections you don't need.
3. Edit the `links` array in `lib/nav.js` (marked `EDIT ME`) to list the suite's pages.
4. For a schema/API reference, copy `template-interactive.html` into the suite and replace its `ITEMS` object.
5. Run the §10 checklist.

For a **single standalone document** (no suite): inline the full stylesheet (Appendix B) into a `<style>` block, keep `lib/` next to the file with just `mermaid.min.js`, `mermaid-init.js`, and `lightbox.js`, and skip the nav.

## Appendix B — Canonical stylesheet

The canonical copy is `design-docs-template/lib/doc.css`. If you do not have it, recreate it exactly from the tokens in §4 and the component specs in §6 — or preferably ask for the file. Do not invent divergent styles: consistency across suites is the point of this system.

## Appendix C — Canonical Mermaid configuration

The canonical copy is `design-docs-template/lib/mermaid-init.js`. Key facts if recreating: `startOnLoad: false` then `mermaid.run()` on `DOMContentLoaded`; `theme: 'dark'`; themeVariables — `primaryColor #1a3a5c`, `primaryTextColor #c9d1d9`, `primaryBorderColor #30363d`, `lineColor #58a6ff`, `secondaryColor #161b22`, `tertiaryColor #0d1117`, `noteBkgColor #1c2129`, `noteTextColor #c9d1d9`, `noteBorderColor #30363d`, `actorBkg #161b22`, `actorTextColor #e6edf3`, `actorBorder #58a6ff`, `signalColor/signalTextColor #c9d1d9`; sequence — `mirrorActors false`, `wrap true`, `width 180`, `messageMargin 40`, `actorMargin 60`, `useMaxWidth true`; flowchart — `useMaxWidth true`. Dispatch a `mermaid:rendered` event after `run()` resolves so `lightbox.js` can bind.
