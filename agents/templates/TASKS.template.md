# <Project / Feature> — Implementation Tasks

> One line: what gets built and in what order.

**Version:** 1.0 · **Status:** Draft · **Updated:** <Month Year>

---

## 1. Overview

<Links to [`DESIGN.md`](DESIGN.md) (v<x>) and [`REQUIREMENTS.md`](REQUIREMENTS.md)
(v<x>). One paragraph on the build strategy — what order, and why.>

## 2. Milestones

| Milestone | Demoable increment | Tasks |
|---|---|---|
| M1 <name> | <what works at the end of it> | T-1, T-2, T-3 |
| M2 <name> | … | T-4, T-5 |

## 3. Tasks

### T-1 — <short title>
**Goal:** <what this task delivers>
**Touches:** `<path>`, `<path>`, `<test path>`
**Depends on:** <task IDs, or "none">
**Satisfies:** <FR / NFR IDs>
**Acceptance:** <checkable without later tasks>
**Size:** S / M / L

### T-2 — …

## 4. Dependency graph

```mermaid
graph LR
    T1 --> T2
    T1 --> T3
    T2 --> T4
    T3 --> T4
```

## 5. Risks & mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| <unknown / external blocker / uncovered requirement> | … | … |

## 6. Changelog

- **v1.0 — <Month Year>** — Initial draft.
