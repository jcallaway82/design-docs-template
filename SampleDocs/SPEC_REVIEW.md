# CLAWE UI — Spec Review

> An independent cross-check of `DESIGN.md`, `REQUIREMENTS.md`, and the iteration timeline for gaps, contradictions, untestable requirements, and traceability holes. Read-only — this document reports, it does not edit the specs.

**Reviewed:** September 2026 (2nd pass)
**Documents reviewed:** `DESIGN.md` v1.1 · `REQUIREMENTS.md` v1.1 · `CLAWE_UI_Iterative_Timeline` Draft v4 (used in place of a `TASKS.md`)

> **Note (post-review, 2026-09-09):** after this review the open questions were consolidated into a
> canonical register — `DESIGN.md` §10, `OQ-1` … `OQ-12`. References below to `DESIGN.md §10 Qn` and
> `REQUIREMENTS.md §8.x` map to `OQ-n` (position-preserved; `OQ-12` is new). `DESIGN.md` and
> `REQUIREMENTS.md` are now v1.2. No finding changed.
>
> **Note (post-review, 2026-10-01):** the counts below are as audited on 2026-09-09. Since then FR-64
> was added (64 FR, 80 requirements in all), and iteration numbers follow timeline Draft v5 (so
> "iteration 8" for rollups is now iteration 10). `REQUIREMENTS.md` §7 and `DESIGN.md` carry the current figures.

---

## 1. Summary

| Severity | 1st pass | 2nd pass |
|---|---|---|
| Critical | 0 | 0 |
| High | 3 | **0** |
| Medium | 8 | **0** |
| Low | 6 | **0** |
| **Total open** | 17 | **0** |

**Verdict: ready to implement.** All 17 first-pass findings are resolved. The one residual the 2nd pass raised (F-R1 — no requirement for the `RequestRadars` response's `source_name` / `schema_version` fields) was fixed in the same pass by adding FR-63. No open findings remain.

Counted claims re-audited after all edits and correct: **63 functional** requirements (was 60; FR-61/FR-62 for the interface-C load-failure paths, FR-63 for response attribution), 16 non-functional, 79 traceability rows matching, **14 failure modes** in `DESIGN.md` (was 12; FM-13/FM-14 added), 13 design decisions, 10 items in `REQUIREMENTS.md` §8. Every design component, key flow, and all 14 failure modes generate at least one requirement.

---

## 2. Findings

### 2.1 First-pass findings — resolution

| ID | Sev | Status | How resolved |
|---|---|---|---|
| F-1 | High | **Resolved** | `DESIGN.md` §5 (Maintenance View) now describes the `RadarFilterPanel` search / filter overlay in Responsibility and Interfaces; FR-25 traces to it. |
| F-2 | High | **Resolved** | FR-17 rewritten as one testable rule: the system SHALL prevent deleting a waveform while an Auto-schedule entry references it, naming the entries to clear. No more "either / or". |
| F-3 | High | **Resolved** | Split: FR-57 is now the container (add / resize / remove — verifiable now); FR-58 is the feed rendering, verified against a mock, with the live-feed clause explicitly held at Draft pending §8.1. |
| F-4 | Medium | **Resolved** | `REQUIREMENTS.md` §5 defines a "reference benchmark host" (4-core x64 / 16 GB / SSD, Release build); NFR-1 – NFR-4 now cite it. |
| F-5 | Medium | **Resolved** | `DESIGN.md` §3 states 500 radars as the design figure for interface-B sizing; `REQUIREMENTS.md` §5 carries it; NFR-4 traces to both. |
| F-6 | Medium | **Resolved** | FR-43 specifies a 250 ms debounce window (configurable default) and a ≤ 1 s create-to-event latency bound. |
| F-7 | Medium | **Resolved** | FR-5 now traces to `DESIGN.md` DD-8 only — the dangling "§9 (FM handled by design)" reference is gone. |
| F-8 | Medium | **Resolved** | `DESIGN.md` §6.2 and §6.3 gained compact message-contract tables (interface B: 3 messages + transport; interface C: 5 messages); §1 names `CLAWE_Interface_B.html` a normative extension that requirements may trace to; `REQUIREMENTS.md` §1 says the same. FR-43 and FR-46 re-anchored on §6.2. |
| F-9 | Medium | **Resolved** | `DESIGN.md` §9 gained FM-13 (Execution View cannot open `CLAWE DB`) and FM-14 (`LoadWaveforms` / `LoadSchedule` rejected); `REQUIREMENTS.md` gained FR-61 and FR-62 tracing to them. |
| F-10 | Medium | **Resolved** | FR-40 names the 6-value modulation set {Phase, Frequency, PRI, PW, Leading Edge, Trailing Edge} explicitly and flags the 6-vs-9 scope as provisional (§8.4). |
| F-11 | Medium | **Resolved** | `REQUIREMENTS.md` §8 item 10 records that DD-13 produced no requirement by design. |
| F-12 | Low | **Resolved** | `DESIGN.md` §1 no longer says `REQUIREMENTS.md` does not exist; v1.1 changelog entry added; §1 links `REQUIREMENTS.md`. |
| F-13 | Low | **Resolved** | `DESIGN.md` §5 (Execution View) states the graph-window shell is WPF controls inside `CLAWE.UI`, not a separate project — count stays eight. |
| F-14 | Low | **Resolved** | `DESIGN.md` §2 goal 3 now reads "range ambiguity, velocity ambiguity" (five families, matching §5 and FR-26). |
| F-15 | Low | **Resolved** | FR-4 states the editor SHALL assign the lowest unused `waveform_id` on add; acceptance gives the {1,2,4}→3 example. |
| F-16 | Low | **Resolved** | NFR-10 requires restart within 30 s of an unexpected exit and verifies it with a kill test. |
| F-17 | Low | **No action (recorded)** | The traceability matrix's "Timeline iteration" column instead of "Task ID" is a documented adaptation (no `TASKS.md`). Left as-is. |

### 2.2 Second-pass findings

| ID | Severity | Where | Finding | Status |
|---|---|---|---|---|
| F-R1 | Low | `DESIGN` §6.2 (interface-B table) ↔ `REQUIREMENTS` §3.5 | The message table added for F-8 listed `RequestRadarsResponse` fields `source_name` and `schema_version`, but no FR required them. | **Resolved** — FR-63 added ("Response attribution and version tag"), tracing to `DESIGN.md` §6.2 and DD-9. |

---

## 3. Coverage matrices

### 3.1 Design element → requirement

| Design element | Requirement(s) | Notes |
|---|---|---|
| §5 CLAWE Proxy | FR-33, FR-42–FR-48, NFR-10, NFR-12 | complete |
| §5 Maintenance View | FR-12–FR-25, FR-34–FR-36 | F-1 resolved — FR-25 now anchored |
| §5 Execution View | FR-49–FR-58, FR-61, FR-62, NFR-13 | F-9 resolved — load-failure paths covered |
| §5 CLAWE DB | FR-1–FR-11, NFR-5, NFR-6, NFR-8, NFR-11 | complete |
| §5 Waveform Calculation Engine | FR-26–FR-32, NFR-3, NFR-15, NFR-16 | complete |
| §6.1 Authoring a radar | FR-7, FR-12–FR-14, FR-22, FR-24, FR-42 | complete |
| §6.2 STS adds a CLAWE radar | FR-39–FR-41, FR-43, FR-45–FR-48, FR-63 | complete (FR-63 closed F-R1) |
| §6.3 HOCA runs a radar mode | FR-49–FR-53, FR-55, FR-56, FR-61, FR-62 | live telemetry feed deferred (§8.1) |
| DD-1 … DD-12 | see §2.1 of the 1st-pass review — all mapped | complete |
| DD-13 repo structure / Markdown source | **(none — by design, `REQUIREMENTS` §8.10)** | F-11 resolved — now listed |
| §9 FM-1 … FM-12 | FR-34 / FR-35+NFR-7 / NFR-11 / FR-10+NFR-6 / FR-47 / FR-13+FR-14 / FR-15 / FR-28 / FR-48 / FR-56 / NFR-4 / FR-48 | complete |
| §9 FM-13 Execution View cannot open DB | FR-61 | new — complete |
| §9 FM-14 load rejected by HOCA | FR-62 | new — complete |

**Every design element maps to at least one requirement except DD-13, which is intentionally out of scope for the product spec and is now recorded as such.**

### 3.2 Requirement → timeline iteration

All 79 requirements (FR-1–FR-63, NFR-1–NFR-16) carry an iteration in `REQUIREMENTS.md` §7 — no empty cells. Requirements whose full acceptance depends on an unresolved open question, unchanged from the first pass except FR-57/FR-58:

| Requirement | Blocked / limited by |
|---|---|
| FR-25 (Freq/PRI filter sections) | rollup data — iteration 10; text search deliverable now |
| FR-40 (rollup-backed) | calc rollup — iteration 10; hand-rolled builder covers iteration 4 |
| **FR-58 (live feed clause only)** | interface-C telemetry feed unspecified — §8.1; FR-57 container is not blocked |
| FR-27 (affected examples) | calc-formula ambiguities — §8.5 |
| FR-44 (cross-host) | second-launch cross-host behaviour — §8.3 |
| NFR-4 (mechanism for oversized catalogues) | paging vs streaming undecided — §8.2 |

---

## 4. What's good

- **The revision was surgical.** All 17 first-pass findings were addressed by edits to the authoring documents only; no requirement was dropped, and only the genuinely-missing items were added (FR-61 / FR-62 for the interface-C failure paths, FR-63 for response attribution).
- **Failure-mode coverage stayed complete and bidirectional** through the FM-12 → FM-14 growth — every FM maps to a requirement and the requirements cite back.
- **The interface message tables in `DESIGN.md` §6.2 / §6.3** close the "requirements trace to a sibling HTML doc" gap without duplicating the full field-level contract — the design now carries enough for a requirement to anchor on.
- **Counted claims are all correct after the edits** — 63 FR / 16 NFR / 79 matrix rows / 14 FM / 13 DD, each restated consistently in the totals and the changelogs.
- **`REQUIREMENTS.md` §8 remains honest** — it now names three design elements (cognitive-search internals, 3D RDI scope, DD-13) that deliberately produced no requirement.

---

## Next step

No open findings. The specs are ready: begin implementation at the current timeline position
(iteration 3 — waveform editor + schema v3.0 proto changes), or render `DESIGN.md` and
`REQUIREMENTS.md` into the HTML suite alongside the other design docs.
