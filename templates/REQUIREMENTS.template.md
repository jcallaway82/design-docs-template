# <Project / Feature> — Requirements

> One line: the scope this specifies.

**Version:** 1.0 · **Status:** Draft · **Updated:** <Month Year>

---

## 1. Overview

<Scope of this document. Links to [`DESIGN.md`](DESIGN.md) (version <x>). What a
reader should already know.>

## 2. Definitions

| Term | Meaning |
|---|---|
| <term> | <definition> |
| <actor> | <who / what system> |

## 3. Functional requirements

> **FR-1 — <short title>**
> The system SHALL <single testable behavior>.
> **Rationale:** <why — cite DESIGN.md §>
> **Acceptance:** <objectively checkable condition(s)>
> **Traces to:** DESIGN.md §<n> (<element>)

> **FR-2 — …**

<Total: N functional requirements.>

## 4. Non-functional requirements

> **NFR-1 — <category: performance / reliability / security / …>**
> <measurable target, e.g. "P95 latency ≤ 200 ms at 100 concurrent users">
> **Verification:** <load test / static analysis / review / …>
> **Traces to:** DESIGN.md §<n>

<Total: N non-functional requirements.>

## 5. Constraints & assumptions

- <carried from DESIGN.md §3, plus any new>

## 6. Out of scope

- <explicit non-requirement>

## 7. Traceability matrix

| Requirement | Design section | Task ID |
|---|---|---|
| FR-1 | DESIGN.md §5 | <filled by tasks-planner> |
| NFR-1 | DESIGN.md §3 | |

## 8. Open questions

1. <question — and which FR/NFR it blocks>
2. <design element with no requirement yet, if any>

## 9. Changelog

- **v1.0 — <Month Year>** — Initial draft.
