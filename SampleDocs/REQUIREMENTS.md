# CLAWE UI — Requirements

> The testable contract for the CLAWE Interactive Emitters App: what it must do (functional) and how well (non-functional), each requirement traced to a section of `DESIGN.md`.

> **Rendered version:** `CLAWE_Requirements.html` (in the design-doc suite). This Markdown file is the
> editable source — regenerate the HTML after a substantive change. If the two disagree, this file
> wins.

**Version:** 1.6 · **Status:** Draft · **Updated:** September 2026

---

## Table of contents

1. [Overview](#1-overview)
2. [Definitions](#2-definitions)
3. [Functional requirements](#3-functional-requirements)
4. [Non-functional requirements](#4-non-functional-requirements)
5. [Constraints & assumptions](#5-constraints--assumptions)
6. [Out of scope](#6-out-of-scope)
7. [Traceability matrix](#7-traceability-matrix)
8. [Open questions](#8-open-questions)
9. [Changelog](#9-changelog)

---

## 1. Overview

This document specifies the CLAWE Interactive Emitters App ("CLAWE UI") as a checkable set of
requirements derived from [`DESIGN.md`](DESIGN.md) (v1.6). Every functional requirement (`FR-<n>`)
is one testable statement with acceptance criteria; every non-functional requirement (`NFR-<n>`)
names a measurable target and a verification method. Section 7 traces each requirement to the design
element that motivates it.

A reader should already know the design: the standalone-app architecture (`DESIGN.md` §1, DD-1), the
proxy plus split single-purpose views (§4, DD-5), the two-layer protobuf-blob storage (§8, DD-2), and
the two network interfaces — B (STS UI ↔ CLAWE UI) and C (CLAWE UI ↔ HOCA). Field-level detail for
the data model is in [`CLAWE_Data_Schema.html`](CLAWE_Data_Schema.html); the interface-B/C message
contract is in `DESIGN.md` §6.2 / §6.3 and, in full, [`CLAWE_Interface_B.html`](CLAWE_Interface_B.html)
— a normative extension of the design that requirements may trace to.

Requirements are stated for the whole v1 system. Many are satisfied incrementally across the
[12-iteration timeline](CLAWE_UI_Iterative_Timeline.html); an acceptance clause is verifiable once
the iteration that builds it lands, and `TASKS`/timeline traceability is filled in §7's third column.

## 2. Definitions

| Term | Meaning |
|---|---|
| **Operator** | The human authoring radars in the Maintenance View, or driving a running radar in an Execution View. |
| **STS** | The existing PRISM application. The client on interface B; registers CLAWE as an "interactive emitter source". |
| **HOCA** | Heterogeneous Open Computing Architecture — the hardware-abstraction layer. Drives execution over interface C. |
| **CLAWE Proxy** | The always-on CLAWE-side process that owns the interface-B/C connections and launches views. |
| **Maintenance View** | The singleton authoring window. The only writer to `CLAWE DB`. |
| **Execution View** | A window locked to one assigned radar mode, launched by HOCA. `0..n` may run. Never writes `CLAWE DB`. |
| **CLAWE DB** | CLAWE UI's SQLite database. One per host, at `%LocalAppData%\CLAWE\clawe.db`. |
| **Radar / Mode / Waveform** | `ClaweRadarInstance` / `ClaweRadarModeInstance` / `ClaweWaveformInstance` — the three nested data levels. |
| **Constraint envelope** | A mode's `ConstraintEnvelope`: CF constraint, max duty cycle, CPI-duration rule, and `PDConstraints` / `SPConstraints`. |
| **Modifier stack** | The nine independently-toggleable modifier categories on a waveform (Phase, Frequency, Pulse Compression, PRI, PW, Amplitude, Leading Edge, Trailing Edge, Discrimination). |
| **The deck / deck ranges** | `CLAWE UI Requirements.pptx`, slides 27–32 — the authoritative min/max for every modifier parameter. |
| **Blob** | `ClaweRadarProtoBlob.ProtoBytes` — the serialized `ClaweRadarInstance`, the canonical form of a radar. |
| **Index rows** | The thin relational rows (`ClaweRadar`, `ClaweRadarMode`) that make radars listable without deserializing a blob. |
| **Rollup** | A computed, non-canonical projection: `ClaweRadarSummary` (interface B) or `ClaweWaveformCalcRollup` (calc metrics). |
| **Calc metrics** | The five families computed by `CLAWE.Calc`: CPI duration, processing gain, eclipsing, range ambiguity, velocity ambiguity. |

## 3. Functional requirements

### 3.1 Data model & persistence

> **FR-1 — Author the three-level radar structure**
> The system SHALL let an operator create and edit a `ClaweRadarInstance` containing `1..N`
> `ClaweRadarModeInstance` children, each containing a `ConstraintEnvelope` and `0..N`
> `ClaweWaveformInstance` children.
> **Rationale:** the core purpose (`DESIGN.md` §2 goal 1, §8).
> **Acceptance:** an operator creates a radar, adds a second mode, adds three waveforms to a mode,
> reopens the radar — all structure is present and unchanged.
> **Traces to:** `DESIGN.md` §5 (CLAWE DB), §8.

> **FR-2 — Radar name uniqueness**
> The system SHALL reject saving a radar whose `name` duplicates an existing radar's `name`
> (case-insensitive), with a message naming the conflict rather than a raw database error.
> **Rationale:** `name` is the sole external handle (`DESIGN.md` DD-11).
> **Acceptance:** creating a second radar named "AN/APQ-Demo" is blocked with a friendly message;
> the first radar is untouched.
> **Traces to:** `DESIGN.md` §8, DD-11.

> **FR-3 — Mode name uniqueness within a radar**
> The system SHALL require each `ClaweRadarModeInstance.name` to be unique within its parent radar,
> and SHALL allow two different radars to each have a mode of the same name.
> **Rationale:** uniqueness is scoped to the parent (`DESIGN.md` §8; schema doc §3.1).
> **Acceptance:** adding a second mode named "Track" to one radar is blocked; a mode named "Track"
> under a different radar saves.
> **Traces to:** `DESIGN.md` §8.

> **FR-4 — Waveform ID uniqueness within a mode**
> The system SHALL require each `ClaweWaveformInstance.waveform_id` (uint32) to be unique within its
> parent mode, and SHALL assign the lowest unused `waveform_id` when a waveform is added.
> **Rationale:** the Auto schedule and interface C reference waveforms by ID (`DESIGN.md` §8, §6.3).
> **Acceptance:** adding a waveform to a mode with IDs {1, 2, 4} assigns 3; two waveforms in one
> mode cannot be saved with the same `waveform_id`.
> **Traces to:** `DESIGN.md` §8, §6.3.

> **FR-5 — A radar always has at least one mode**
> The system SHALL ensure every radar has `1..N` modes: it SHALL seed a default `TTR`/`Manual` mode
> when a radar is created, SHALL refuse to delete a radar's last remaining mode, and SHALL seed a
> default mode into any pre-existing modeless radar on database upgrade.
> **Rationale:** matches STS's effective `>=1`-mode rule; lead-confirmed (`DESIGN.md` DD-8).
> **Acceptance:** a newly created radar shows one mode; the per-row delete control is disabled when a
> radar is down to one mode; `RadarModeRepository.DeleteModeAsync` throws on the last mode; opening a
> database that contains a modeless radar leaves that radar with exactly one seeded mode.
> **Traces to:** `DESIGN.md` DD-8.

> **FR-6 — At most one NATO name and one ELNOT per radar**
> The system SHALL allow a radar to carry `0..1` NATO alternate name and `0..1` ELNOT designator, and
> SHALL enforce this at the editor, the repository, and the database (`IX_ClaweRadarAlternateName_OnePerKind`).
> **Rationale:** mirrors STS's one-textbox-per-identifier-kind UI; lead-confirmed (`DESIGN.md` DD-7).
> **Acceptance:** the editor exposes exactly one "NATO Name" and one "ELNOT" field; setting either to
> blank clears it; a hand-inserted duplicate-kind row is rejected by the unique index.
> **Traces to:** `DESIGN.md` DD-7, §8.

> **FR-7 — Canonical blob plus index, written atomically**
> On every radar write the system SHALL re-serialize the entire `ClaweRadarInstance` to a single
> `ClaweRadarProtoBlob` row and update the thin index rows (`ClaweRadar`, `ClaweRadarMode`) in the
> **same transaction**, so the two layers never disagree.
> **Rationale:** two-layer storage (`DESIGN.md` DD-2, §6.1).
> **Acceptance:** a test that commits a multi-mode radar then reads both layers finds identical mode
> lists; a fault injected between the blob write and the index write rolls back both.
> **Traces to:** `DESIGN.md` DD-2, §6.1, §8.

> **FR-8 — Rename propagates everywhere**
> When a radar or mode is renamed, the system SHALL update the blob's identity fields, the index
> row, and (for a radar) SHALL emit a `RadarModifiedEvent` with `change_kind = RENAMED` and
> `previous_name` set.
> **Rationale:** `name` is the sole handle, and STS caches by name (`DESIGN.md` DD-11, §6.2).
> **Acceptance:** after a rename, `RequestRadars()` returns the new name; the emitted event carries
> both names; no stale index row remains.
> **Traces to:** `DESIGN.md` DD-11, §5 (Proxy), §8.

> **FR-9 — Delete removes blob and index together**
> Deleting a radar SHALL cascade-delete its `ClaweRadarMode` index rows and its `ClaweRadarProtoBlob`
> row, leaving nothing orphaned at either layer.
> **Rationale:** `DESIGN.md` §8.
> **Acceptance:** after deleting a radar, no `ClaweRadar`, `ClaweRadarMode`, or `ClaweRadarProtoBlob`
> row referencing it remains.
> **Traces to:** `DESIGN.md` §8.

> **FR-10 — Versioned, atomic schema upgrades**
> The system SHALL evolve `CLAWE DB` through an ordered list of patch steps recorded in a
> `ClaweSchemaVersion` table, run each step in a transaction, record a step's version only on its
> success, and refuse to start (with a diagnostic) if a step fails.
> **Rationale:** no EF Migrations (`DESIGN.md` DD-3); FM-4.
> **Acceptance:** a deliberately failing patch step leaves `ClaweSchemaVersion` at the previous
> version and the app does not launch; a clean upgrade advances the version and the app launches.
> **Traces to:** `DESIGN.md` DD-3, §5 (CLAWE DB), §9 (FM-4).

> **FR-11 — Persistence across relaunch**
> Data committed by the Maintenance View SHALL survive process exit and be readable by a fresh
> process opening the same database file, including the effect of deletions.
> **Rationale:** the iteration-1 demo bar; `DESIGN.md` §5.
> **Acceptance:** `PersistenceAcrossRelaunchTests` — write via one context, dispose, reopen at the
> same path, assert data and a deletion both survived.
> **Traces to:** `DESIGN.md` §5 (CLAWE DB).

### 3.2 Radar / mode / waveform authoring

> **FR-12 — Combined radar-and-mode editor**
> The system SHALL present radar identity and the selected mode in a single editor, with a mode
> selector (pill strip) to switch modes and an "add mode" action that keeps the current radar.
> **Rationale:** STS EmitterMaker style (`DESIGN.md` §5 Maintenance View, §6.1).
> **Acceptance:** an operator edits radar name and mode fields in one form; switching modes with
> unsaved mode edits prompts to discard; "+ Mode" adds a mode without leaving the radar.
> **Traces to:** `DESIGN.md` §5 (Maintenance View), §6.1.

> **FR-13 — Field validation against deck ranges at entry**
> The system SHALL validate every modifier parameter and constraint-envelope field against its hard
> min/max from deck slides 27–32 as it is entered, using `INotifyDataErrorInfo`.
> **Rationale:** the editor is the validation authority (`DESIGN.md` §2 goal 2, §6.1).
> **Acceptance:** entering a `DropRate_percent` of 10 (below the 25–75 range) flags the field
> immediately; entering 50 clears it.
> **Traces to:** `DESIGN.md` §2, §5 (Maintenance View), §9 (FM-6).

> **FR-14 — Save gated on a clean form**
> While any validation error stands, the system SHALL disable Save, show a per-tab error indicator,
> and list the offending fields in a summary banner; it SHALL NOT write a radar with a known-invalid
> field.
> **Rationale:** `DESIGN.md` §6.1, FM-6.
> **Acceptance:** with one out-of-range field, Save is disabled and the banner names that field; no
> `ClaweRadarProtoBlob` row is written.
> **Traces to:** `DESIGN.md` §6.1, §9 (FM-6).

> **FR-15 — A mode must allow at least one base waveform**
> The system SHALL require a mode to have `PDConstraints`, `SPConstraints`, or both, and SHALL block
> saving a mode that has neither.
> **Rationale:** FM-7.
> **Acceptance:** clearing both PD and SP constraint blocks disables Save with an explanatory message.
> A base waveform that one of the mode's waveforms uses can't be cleared at all (FR-18).
> **Traces to:** `DESIGN.md` §9 (FM-7).

> **FR-16 — Exactly one operating mode**
> The system SHALL require each mode to set exactly one of Manual, Auto, or Cognitive; Auto SHALL
> carry a repeating `WaveformScheduleEntry` list; Cognitive SHALL carry an `OptimizationType`
> (`Learning` or `Speed`). An Auto mode MAY be saved with an empty schedule; the editor SHALL show
> this as a notice, not a validation error.
> **Rationale:** the `operating_mode` oneof (`DESIGN.md` §8). The empty-schedule allowance is
> `DESIGN.md` DD-15: a new mode has no waveforms until it is saved, so it couldn't otherwise be
> saved as Auto at all.
> **Acceptance:** the editor offers a single-choice operating-mode selector; choosing Auto reveals a
> schedule table; choosing Cognitive reveals the Learning/Speed toggle; the saved blob has exactly
> one oneof arm set. An Auto mode with no schedule entries saves, with a notice under the table.
> **Traces to:** `DESIGN.md` §8, DD-15.

> **FR-17 — Auto schedule references waveforms by ID**
> The system SHALL let an operator build an Auto-mode schedule as an ordered list of
> `(waveform_id, duration_s)` entries where `duration_s = 0` means "play once"; SHALL only offer
> `waveform_id` values that exist in the mode; and SHALL prevent deleting a waveform while an
> Auto-mode schedule entry references it, telling the operator which entries to clear first.
> **Rationale:** `DESIGN.md` §8, §6.3.
> **Acceptance:** the schedule editor's waveform picker lists the mode's current waveforms (by name
> and ID), and "add entry" is unavailable while the mode has none; attempting to delete a scheduled
> waveform is blocked with a message naming the referencing entries; deleting a waveform no
> schedule references succeeds.
> **Traces to:** `DESIGN.md` §8, §6.3, DD-15.

> **FR-18 — Full nine-category modifier stack**
> The system SHALL let an operator independently enable and configure each of the nine modifier
> categories on a waveform, exposing only the branches and parameters valid for the waveform's
> `base_waveform` and the mode's `AllowedModifiers` set. The system SHALL NOT let a mode's
> `AllowedModifiers` set, or its PD / SP enablement, be narrowed to exclude a sub-type or base
> waveform that one of the mode's waveforms uses (including the open waveform's unsaved state).
> **Rationale:** `DESIGN.md` §8; the PD/SP compatibility matrix (deck slide 15). The narrowing lock
> is `DESIGN.md` DD-14: it keeps a mode save from ever leaving its waveforms invalid, which FR-14
> could otherwise only enforce by blocking the save outright.
> **Acceptance:** for a PD waveform, PRI/PW/Trailing-Edge modifiers are offered and Amplitude is not;
> for an SP waveform, Amplitude is offered and PRI/PW/Trailing-Edge are not; a modifier not in the
> mode's `AllowedModifiers` is disabled. With a waveform using Base Agile PRI, the mode's Base Agile
> checkbox is disabled and its tooltip names that waveform; once no waveform uses it, it can be
> unchecked.
> **Traces to:** `DESIGN.md` §8, §5 (Maintenance View), DD-14.

> **FR-19 — Phase modifier three-way split**
> The system SHALL model the Phase modifier as `None` / `PartialPhaseEncoded` (with
> `phase_pattern_duration`) / `FullPhaseEncoded`.
> **Rationale:** schema v3.0 (`DESIGN.md` §8; timeline iteration 3).
> **Acceptance:** the Phase modifier editor offers the three states; `PartialPhaseEncoded` shows the
> pattern-duration field.
> **Traces to:** `DESIGN.md` §8.

> **FR-20 — `NumPulses` distinct from FFT size**
> The system SHALL model a PD waveform's `num_pulses` as a settable value defaulting to the fixed
> 1024-point FFT size, and SHALL allow it to be set lower.
> **Rationale:** schema v3.0; affects processing gain (`DESIGN.md` §8).
> **Acceptance:** a new PD waveform shows `num_pulses = 1024`; setting it to 512 is accepted and
> feeds the processing-gain metric (FR-26).
> **Traces to:** `DESIGN.md` §8.

> **FR-64 — Values behind a waveform's Fixed choices**
> The system SHALL store, for a waveform whose center-frequency type is Fixed, its `cf_hz`; for a PD
> waveform whose PRI type is Fixed, its `base_pri_s`; and for an SP waveform, or a PD waveform
> whose PW type is Fixed, its `base_pw_s`. The system SHALL require each, and SHALL reject a value
> the mode's envelope doesn't allow: a CF outside the carrier-frequency range (or, for a
> channelized range, not at a channel centre) or not among its discretes; a PRI outside the PRI
> range or not among its discretes; a PW outside the PD or SP PW range. A mode that sets PW by duty
> cycle SHALL require waveforms whose PW type is Duty cycle, and the reverse. A Random choice stores
> no value.
> **Rationale:** deck slide 12 (`CF_hz`, `BasePRI_s`, `BasePW_s`); the calculation engine's inputs
> (FR-26 to FR-31) need them. v0.3.0 stored only the Fixed/Random choice; found in the lead's
> v0.3.0 review.
> **Acceptance:** with a mode of CF 9.0–9.5 GHz, PRI 1–100 µs and PW 0.1–10 µs, a Fixed waveform with
> CF 9.7 GHz or PRI 250 µs is rejected and names the mode's range; 9.25 GHz and 100 µs save and
> reload unchanged. In a channelized range with 100 MHz channels from 9.0 GHz, 9.15 GHz saves and
> 9.1 GHz is rejected. Tightening the mode's range so a saved waveform falls outside flags that
> waveform. A Random center-frequency waveform writes no `cf_hz`.
> **Traces to:** `DESIGN.md` §8.

> **FR-21 — TTR authorable; other mode types visible but disabled**
> The system SHALL allow `radar_mode_type = TTR` to be selected and SHALL show `Search`, `TAR`, and
> `Missile` as visible, non-selectable options.
> **Rationale:** v1 scope (`DESIGN.md` DD-12).
> **Acceptance:** the mode-type control lists all four values; only `TTR` is selectable.
> **Traces to:** `DESIGN.md` DD-12.

> **FR-22 — Draft-then-save radar creation**
> Creating a radar SHALL open a blank unsaved draft; nothing SHALL persist until the operator saves.
> **Rationale:** `DESIGN.md` §6.1 ("create radar … save").
> **Acceptance:** starting a new radar and closing the editor without saving leaves no new row.
> **Traces to:** `DESIGN.md` §6.1.

> **FR-23 — Confirmation before destructive delete**
> The system SHALL require an explicit confirmation dialog before deleting a radar or a mode.
> **Rationale:** ported `ConfirmDeleteDialog` pattern; prevents accidental loss.
> **Acceptance:** the per-row delete control opens a dialog naming the target; Cancel/Esc aborts with
> the item still present; confirming deletes it.
> **Traces to:** `DESIGN.md` §5 (Maintenance View).

> **FR-24 — Unsaved-changes indicator**
> The system SHALL show a visible "unsaved" indicator whenever the editor holds uncommitted changes,
> and SHALL clear it on a successful save.
> **Rationale:** `DESIGN.md` §6.1 ("unsaved indicator clears").
> **Acceptance:** editing any field shows the indicator; Save clears it; discarding restores the
> saved state and clears it.
> **Traces to:** `DESIGN.md` §6.1.

> **FR-25 — Radar search / filter overlay**
> The system SHALL provide a slide-out overlay to search radars by name, description, and alternate
> name, and SHALL be extensible to add frequency-range and PRI-range filters once rollup data exists.
> **Rationale:** lead request; mirrors STS's `EmitterFilterPanel` (`DESIGN.md` §2 "recognises the app").
> **Acceptance:** typing in the search box filters the radar list by the three text fields;
> selecting a result opens it in the editor. (Freq/PRI sections land with iteration 10.)
> **Traces to:** `DESIGN.md` §2, §5 (Maintenance View).

### 3.3 Waveform calculation & summary

> **FR-26 — Five calc-metric families plus a text description**
> The system SHALL compute, for any waveform, the CPI duration, processing gain, eclipsing fraction,
> range-ambiguity zone size and count, velocity-ambiguity zone size and count, and an auto-generated
> plain-text waveform description — as pure functions of the waveform, its mode's envelope, and the
> fixed `ScenarioAssumptions`.
> **Rationale:** the Waveform Summary Screen (`DESIGN.md` §5 Calc Engine).
> **Acceptance:** `WaveformMetricsCalculator.Compute(WaveformCalcInput)` returns all five families
> and the description for a representative waveform.
> **Traces to:** `DESIGN.md` §5 (Waveform Calculation Engine).

> **FR-27 — Every deck worked example reproduced**
> The calc engine SHALL reproduce every worked numeric example in `CLAWE Waveform Calculations.pptx`
> within a stated tolerance.
> **Rationale:** the deck is the spec (`DESIGN.md` §5 Calc Engine).
> **Acceptance:** an xUnit `[Theory]` with one `[InlineData]` row per deck example, all passing.
> **Traces to:** `DESIGN.md` §5.

> **FR-28 — Guarded against NaN and divide-by-zero**
> The calc engine SHALL never throw or produce `NaN`/`Infinity` for a partially-entered or
> zero-valued input; it SHALL return a "not computable" sentinel that the UI renders as "—".
> **Rationale:** FM-8; the `GraphsAndFieldsReview.md` gap.
> **Acceptance:** computing with a zero PRI or an unset field yields the sentinel, not an exception;
> the summary shows "—" for that metric.
> **Traces to:** `DESIGN.md` §9 (FM-8).

> **FR-29 — Live Waveform Summary Screen**
> The Waveform Summary Screen SHALL recompute and redisplay all metrics whenever a bound editor field
> changes, without a polling timer, and SHALL show the CPI (Tx / processing) and processing-gain
> (per-nonideal-effect) breakdowns.
> **Rationale:** `DESIGN.md` §5 Calc Engine; timeline iteration 8.
> **Acceptance:** changing a modifier value updates every metric and the breakdowns in the same
> interaction; no timer is used (same cadence as `RadarModeEditorViewModel`).
> **Traces to:** `DESIGN.md` §5.

> **FR-30 — Eclipsing chart**
> The summary SHALL render a processing-gain-loss-versus-target-range chart for the current waveform,
> updating live with the other metrics.
> **Rationale:** `DESIGN.md` §5; timeline iteration 8.
> **Acceptance:** the chart is present, themed to match STS, and redraws on field change.
> **Traces to:** `DESIGN.md` §5, DD-10.

> **FR-31 — Metrics browsable across a mode's waveforms**
> The system SHALL let an operator browse and filter all of a mode's waveforms by name and by ranges
> of their computed metrics and parameters (frequency, PRI, PW, CPI duration, processing gain) and by
> modulation type, querying cached rollup rows and never deserializing a blob per row.
> **Rationale:** `DESIGN.md` §2 goal 3, §3 (scale), DD-2.
> **Acceptance:** with several thousand waveforms in a mode, a filtered query returns results from
> `ClaweWaveformCalcRollup` rows only (verified by a no-blob-read assertion) and meets NFR-2.
> **Traces to:** `DESIGN.md` §2, §3, DD-2, DD-9.

> **FR-32 — Live signal preview**
> The waveform editor SHALL show a signal-shape preview (pulse train / PRI-PW timeline plus
> modifier-effect visualisation) that updates as fields change.
> **Rationale:** `DESIGN.md` §2 goal 5 (previews); timeline iteration 9.
> **Acceptance:** editing a PRI modifier updates the pulse-train preview in the same interaction.
> **Traces to:** `DESIGN.md` §2, §5 (Maintenance View), DD-10.

### 3.4 Process & instance model

> **FR-33 — Always-on proxy**
> The CLAWE Proxy SHALL start at user logon (in the user's session, so it can open views — DD-21),
> stay running independently of any view, and hold the
> RabbitMQ connections for interfaces B and C plus a read-only `CLAWE DB` connection.
> **Rationale:** `DESIGN.md` §4, §5 (Proxy), DD-5.
> **Acceptance:** with no view open, the proxy process is running and answers `RequestRadars()`.
> **Traces to:** `DESIGN.md` §4, §5 (Proxy), DD-5.

> **FR-34 — Singleton Maintenance View**
> The system SHALL permit at most one Maintenance View per host, enforced by the system-wide named
> mutex `Global\CLAWE_UI_Maintenance` acquired when the view enters maintenance mode; the proxy SHALL
> check it before spawning and a batch-file/double-click launch SHALL check it on startup.
> **Rationale:** single-writer safety (`DESIGN.md` §4, DD-5, FM-1).
> **Acceptance:** a second launch attempt while a maintenance view runs does not open a second
> writer — it is focused (proxy path) or exits with a message (direct path).
> **Traces to:** `DESIGN.md` §4, DD-5, §9 (FM-1).

> **FR-35 — Maintenance View is the sole writer**
> Only the Maintenance View SHALL write `CLAWE DB`; the proxy and every Execution View SHALL open it
> read-only. A write-owner row SHALL back the mutex: the Maintenance View claims it at startup, every
> commit it makes SHALL check it first, and a write attempted by a non-owner SHALL throw before
> committing. An owner whose process has died MAY be taken over.
> **Rationale:** `DESIGN.md` §4, DD-5, DD-18, FM-2.
> **Acceptance:** a read-only context cannot commit; a second writer (even in the same process —
> NFR-7) can't claim the row, and its commits throw with nothing written.
> **Traces to:** `DESIGN.md` §4, DD-5, DD-18, §9 (FM-2).

> **FR-36 — Two launch paths, one mutex**
> A view SHALL be startable either by the proxy (in response to a network message) or directly by a
> batch file / double-click; both paths SHALL honour the singleton mutex, and a directly-launched
> Maintenance View SHALL register with the proxy so a subsequent `LaunchMaintenanceUiCommand` focuses
> it.
> **Rationale:** `DESIGN.md` §4, §5 (Maintenance View).
> **Acceptance:** double-clicking the exe opens maintenance; a later `LaunchMaintenanceUiCommand`
> returns `FOCUSED` and brings that window forward.
> **Traces to:** `DESIGN.md` §4.

> **FR-37 — Mode-parameterised host process**
> `CLAWE.Host` SHALL run as `--mode maintenance` (singleton, writer) or `--mode execution` (`0..n`,
> read-only), replacing the single-window Maintenance/Operate `NavigationView` shell.
> **Rationale:** `DESIGN.md` §4, DD-5; timeline iteration 4.
> **Acceptance:** `CLAWE.Host --mode execution` starts a mode-locked window and never a maintenance
> editor; `--mode maintenance` starts the editor and acquires the mutex.
> **Traces to:** `DESIGN.md` §4, DD-5.

> **FR-38 — One proxy and one database per host**
> The system SHALL assume exactly one proxy and one `CLAWE DB` per host, and SHALL NOT attempt
> cross-host coordination of the singleton rule.
> **Rationale:** `DESIGN.md` §3 assumptions, §2 non-goal.
> **Acceptance:** the mutex name and DB path are host-scoped; documentation states multi-host CLAWE
> means independent proxies and databases.
> **Traces to:** `DESIGN.md` §2, §3.

### 3.5 Interface B — STS integration

> **FR-39 — `RequestRadars()` returns a rollup, no waveform detail**
> On `RequestRadars()` the proxy SHALL return a list of `ClaweRadarSummary`, each with per-radar
> identity and per-mode rollups, and SHALL NOT include any `ClaweWaveformInstance` detail.
> **Rationale:** STS only picks a mode and validates a frequency (`DESIGN.md` §6.2, DD-9).
> **Acceptance:** the response contains no waveform-instance fields; it contains, per mode, the
> fields in FR-40.
> **Traces to:** `DESIGN.md` §6.2, DD-9.

> **FR-40 — `ClaweRadarSummary` rollup content**
> Each `ClaweRadarModeSummary` SHALL carry `name`, `description`, `radar_mode_type`, `operating_mode`,
> the set of waveform base types present (`Pulsed` / `SinglePulse` / `CW`), `min/max` centre
> frequency, `min/max` PRI, `min/max` PW, and `modulation_types` — the **6-value subset** {Phase,
> Frequency, PRI, PW, Leading Edge, Trailing Edge} of the nine modifier categories, restricted to
> those enabled across the mode's waveforms. Each value is derived from the mode envelope unioned
> with per-waveform rollups.
> **Rationale:** `DESIGN.md` DD-9; `CLAWE_Interface_B.html` §5. The 6-value set follows the deck's
> `ModulationType` enum; whether the omission of Pulse Compression / Amplitude / Discrimination is
> intended is open (OQ-8).
> **Acceptance:** met in two stages.
> - **Iteration 4 (hand-rolled builder, envelope-only):**
>   - `min/max` frequency, PRI and PW come from the mode's constraint envelope. A PD duty-cycle PW
>     is duty % × the PRI bounds.
>   - `waveform_types` is the envelope's allowed types plus those of the authored waveforms.
>   - `modulation_types` contains only values from the 6-value set, and only those actually
>     enabled.
> - **Iteration 10 (rollups):** for a mode with two PD waveforms, `min/max` frequency spans the
>   envelope widened by any per-waveform centre frequency outside it. Since FR-64, a waveform's
>   CF, PRI and PW must lie inside the envelope, so that widening can no longer occur. What the
>   rollup could still add is the span of the waveforms actually authored, if the lead wants that
>   reported instead of the envelope (to confirm with the lead; not yet in the open-question register).
> **Traces to:** `DESIGN.md` DD-9, §8.

> **FR-41 — Frequency data sufficient for STS validation**
> The `ClaweRadarSummary` SHALL carry, per mode, the centre-frequency bounds (and, for a channelized
> range, the channel spacing) that STS validates a scenario emitter's centre frequency against.
> **Rationale:** frequency validation is the point of interface B (`DESIGN.md` §6.2).
> **Acceptance:** STS can accept or reject a chosen centre frequency using only summary fields.
> **Traces to:** `DESIGN.md` §6.2, DD-9.

> **FR-42 — `RadarModifiedEvent` on every write**
> The system SHALL publish a `RadarModifiedEvent` to the `clawe.ifaceB.events` fanout exchange
> whenever a radar, mode, or waveform write commits, carrying `radar_name`, `change_kind`
> (`CREATED` / `UPDATED` / `RENAMED` / `DELETED`), `previous_name` on `RENAMED`, a UTC `timestamp`,
> and `source_name`.
> **Rationale:** STS refreshes on change, not by polling (`DESIGN.md` §2 goal 4, §6.1).
> **Acceptance:** each of create / edit-a-mode / rename / delete produces one event with the correct
> `change_kind`; a mode or waveform edit produces a radar-grained `UPDATED`.
> **Traces to:** `DESIGN.md` §6.1, §5 (Proxy).

> **FR-43 — Event coalescing**
> The system SHALL debounce `UPDATED` events per radar so a burst of writes (e.g. saving a radar with
> many modes) produces one `UPDATED` after a quiet period of **250 ms** (a configurable default)
> following the last write, with total create-to-event latency ≤ 1 s; `CREATED` / `DELETED` /
> `RENAMED` SHALL be sent without debounce.
> **Rationale:** `DESIGN.md` §6.2 (interface-B message table); `CLAWE_Interface_B.html` §4.3
> ("Coalescing").
> **Acceptance:** ten saves to one radar within 250 ms of each other yield one `UPDATED` ~250 ms
> after the last; a create followed by edits yields one prompt `CREATED` then one coalesced
> `UPDATED`.
> **Traces to:** `DESIGN.md` §5 (Proxy), §6.2.

> **FR-44 — `LaunchMaintenanceUiCommand`**
> On `LaunchMaintenanceUiCommand` the proxy SHALL start a Maintenance View if none runs and return
> `LAUNCHED`; SHALL focus the existing one and return `FOCUSED` if one runs on the same host; and
> SHALL return `REJECTED` with detail when it cannot comply. An optional `radar_name` SHALL open the
> view with that radar selected.
> **Rationale:** `DESIGN.md` §4; `CLAWE_Interface_B.html` §4.2.
> **Acceptance:** first call → `LAUNCHED`; second call → `FOCUSED` and the window comes forward; a
> spawn failure → `REJECTED` with a message. (OQ-10's proposed answer: focus; cross-host can't arise
> under FR-38.) Windows may only flash the window's taskbar button when the request comes from the
> background proxy (DD-20).
> **Traces to:** `DESIGN.md` §4, §5 (Proxy).

> **FR-45 — Answer `RequestRadars()` with no view running**
> The proxy SHALL answer `RequestRadars()` from its own read-only database connection without
> starting any view.
> **Rationale:** `DESIGN.md` §5 (Proxy), DD-5.
> **Acceptance:** with no view process running, `RequestRadars()` returns the current catalogue.
> **Traces to:** `DESIGN.md` §5 (Proxy).

> **FR-46 — Transport and broker objects**
> Interface B SHALL run over TCP + RabbitMQ (AMQP 0-9-1) + Protobuf, using a request/command queue
> per CLAWE endpoint (`clawe.ifaceB.rpc.<source_name>` — namespaced so several CLAWE hosts can
> share one broker, OQ-11) and a fanout exchange (`clawe.ifaceB.events`); every message SHALL travel
> inside an `InterfaceBEnvelope` carrying a timestamp and protocol version.
> **Rationale:** `DESIGN.md` DD-6; `CLAWE_Interface_B.html` §2.
> **Acceptance:** a test client using RabbitMQ + the compiled `clawe_interface_b.proto` completes
> `RequestRadars`, `LaunchMaintenanceUiCommand`, and receives `RadarModifiedEvent`.
> **Traces to:** `DESIGN.md` DD-6, §5 (Proxy).

> **FR-47 — DB-unavailable is an error response, not a timeout**
> If the proxy cannot open or read `CLAWE DB`, it SHALL return an explicit error response to
> `RequestRadars()` with detail, not let the request time out.
> **Rationale:** FM-5 — STS must distinguish "errored" from "offline".
> **Acceptance:** with the database file removed, `RequestRadars()` returns an error response within
> the deadline; STS shows the source as errored.
> **Traces to:** `DESIGN.md` §9 (FM-5).

> **FR-48 — Broker-loss behaviour**
> On loss of the RabbitMQ connection the STS-facing behaviour SHALL be: source shown offline,
> reconnect with backoff, no radar list served until restored; on reconnect STS SHALL re-run
> `RequestRadars()` unconditionally to resync.
> **Rationale:** FM-9, FM-12; events are an optimisation, not the source of truth.
> **Acceptance:** killing the broker marks the source offline; restoring it reconnects and STS
> re-fetches without operator action.
> **Traces to:** `DESIGN.md` §9 (FM-9, FM-12).

> **FR-63 — Response attribution and version tag**
> The `RequestRadars` response SHALL echo the `source_name` STS registered for this CLAWE endpoint
> and SHALL carry a `schema_version` string identifying the `ClaweRadarSummary` contract version.
> **Rationale:** STS attributes the list to the source and detects a contract mismatch
> (`DESIGN.md` §6.2 message table; `CLAWE_Interface_B.html` §4.1).
> **Acceptance:** the response's `source_name` matches the registered source; `schema_version` is a
> stable identifier (e.g. `clawe-ifaceB-1`) that changes only on a breaking contract change.
> **Traces to:** `DESIGN.md` §6.2, DD-9.

### 3.6 Interface C — execution

> **FR-49 — HOCA launches a mode-locked Execution View**
> On `LaunchExecutionUI(ActiveRadarMode)` (payload: radar name, mode name, CF, amplitude) the proxy
> SHALL create (or show) an Execution View locked to that mode.
> **Rationale:** `DESIGN.md` §6.3; deck slide 8.
> **Acceptance:** the message opens a window whose title/header names the radar and mode and whose
> capability/constraint fields are read-only.
> **Traces to:** `DESIGN.md` §5 (Execution View), §6.3.

> **FR-50 — Execution View lock**
> An Execution View SHALL NOT allow edits to the radar's or mode's capabilities or constraints; it
> SHALL allow adding and editing `ClaweWaveformInstance` entries within the assigned mode.
> **Rationale:** `DESIGN.md` §5 (Execution View), §6.3.
> **Acceptance:** constraint-envelope controls are disabled; a new waveform can be added to the
> locked mode.
> **Traces to:** `DESIGN.md` §5 (Execution View).

> **FR-51 — Execution View never writes the database**
> An Execution View SHALL open `CLAWE DB` read-only and SHALL hold only transient run state.
> **Rationale:** `DESIGN.md` §4, §5 (Execution View), FM-2.
> **Acceptance:** the Execution View's database context cannot commit; closing it leaves the database
> unchanged.
> **Traces to:** `DESIGN.md` §4, §5 (Execution View).

> **FR-52 — Load waveforms and schedule to HOCA**
> On activation the Execution View SHALL send `LoadWaveforms(List<waveform>)` with every waveform
> instance for the active radar and, when the mode is Auto, `LoadSchedule(List<WaveformID, Duration>)`
> with the schedule. It SHALL refuse to activate an Auto mode whose schedule is empty, and say why.
> **Rationale:** `DESIGN.md` §6.3; deck slide 8. The empty-schedule refusal is the other half of
> DD-15, which lets such a mode be saved.
> **Acceptance:** against a mocked HOCA, both messages are sent with the correct payloads on
> `ActivateRadar()`; an Auto mode with an empty schedule is not activated and no `LoadSchedule` is
> sent.
> **Traces to:** `DESIGN.md` §5 (Execution View), §6.3.

> **FR-53 — Activate / deactivate**
> The Execution View SHALL start radar operation on `ActivateRadar()` and end it on
> `DeactivateRadar()`, showing itself if hidden, and SHALL remain open after `DeactivateRadar()`.
> **Rationale:** `DESIGN.md` §6.3; deck slide 8.
> **Acceptance:** `ActivateRadar()` begins schedule playback; `DeactivateRadar()` stops it and the
> window stays open.
> **Traces to:** `DESIGN.md` §6.3.

> **FR-54 — Multiple concurrent Execution Views**
> The system SHALL allow `0..n` Execution Views to run at once, each locked to its own assigned mode.
> **Rationale:** `DESIGN.md` §4, §5 (Execution View).
> **Acceptance:** a second `LaunchExecutionUI` for a different mode opens a second independent window.
> **Traces to:** `DESIGN.md` §4, §5 (Execution View).

> **FR-55 — Operator-in-the-loop and cognitive control**
> In an Execution View the operator SHALL be able to search and select the active waveform
> (operator-in-the-loop) or hand control to cognitive optimisation (Learning / Speed), switching
> between the two.
> **Rationale:** `DESIGN.md` §6.3; deck UI notes (slides 33–34).
> **Acceptance:** the Control tab offers an operating-mode switch; in operator-in-the-loop the
> operator picks a waveform from the mode's list; in cognitive the Learning/Speed state is shown.
> **Traces to:** `DESIGN.md` §5 (Execution View), §6.3.

> **FR-56 — HOCA connection loss mid-run**
> If the interface-C connection drops during a scenario, the Execution View SHALL hold its last
> state, show a disconnected banner, and SHALL NOT exit; on reconnect it SHALL accept a re-sent
> `ActivateRadar()`.
> **Rationale:** FM-10.
> **Acceptance:** dropping the mocked HOCA connection mid-run leaves the window open with a banner;
> restoring it and re-sending `ActivateRadar()` resumes.
> **Traces to:** `DESIGN.md` §9 (FM-10).

> **FR-57 — Dockable graph-window container**
> The Execution View SHALL provide a container in which graph windows (2D RDI scope, 3D RDI scope,
> target table) can be added, resized, and removed.
> **Rationale:** `DESIGN.md` §5 (Execution View); deck UI notes (slides 33–34).
> **Acceptance:** an operator adds a target-table window, resizes it, and removes it; the container
> lays out multiple windows without overlap.
> **Traces to:** `DESIGN.md` §5 (Execution View), OQ-4.

> **FR-58 — RDI scope and target-table windows render their feeds**
> The 2D RDI scope SHALL render compressed-RDI data and the target-table window SHALL list active
> targets and their information, each updating live as its feed changes.
> **Rationale:** deck UI notes; `DESIGN.md` §5 (Execution View).
> **Acceptance:** **verified against a simulated feed** — the 2D RDI scope redraws from a mock
> compressed-RDI stream and the target table updates from mock target data. **Live-feed acceptance is
> deferred** until the interface-C telemetry path is specified (OQ-3b); until then FR-58's live-data
> clause is held at Draft.
> **Traces to:** `DESIGN.md` §5 (Execution View), §6.3, OQ-3b.

> **FR-61 — Execution View cannot open the database**
> If an Execution View cannot open `CLAWE DB` read-only at launch, it SHALL report the failure to
> HOCA over interface C, SHALL NOT enter execution mode, and SHALL start no partial run.
> **Rationale:** `DESIGN.md` §9 (FM-13).
> **Acceptance:** launching `CLAWE.Host --mode execution` with the database file removed sends an
> error to the (mocked) HOCA and the window does not activate any radar.
> **Traces to:** `DESIGN.md` §9 (FM-13).

> **FR-62 — HOCA rejects a waveform or schedule load**
> If HOCA rejects `LoadWaveforms` or `LoadSchedule`, the Execution View SHALL display the rejection
> detail, SHALL remain in a not-activated state, and SHALL refuse `ActivateRadar()` until a valid
> load succeeds.
> **Rationale:** `DESIGN.md` §9 (FM-14).
> **Acceptance:** a mocked HOCA that nacks `LoadWaveforms` leaves the view not-activated with the
> reason shown; a subsequent `ActivateRadar()` is refused; a successful reload clears the state.
> **Traces to:** `DESIGN.md` §9 (FM-14).

### 3.7 Look and feel

> **FR-59 — Copied, not referenced, PRISM theme**
> `CLAWE.UI` SHALL carry its own copies of the `PRISM.UI` theme tokens and control styles it uses,
> with attribution, and SHALL NOT hold a `ProjectReference` into the PRISM solution.
> **Rationale:** architectural independence (`DESIGN.md` DD-1, DD-4).
> **Acceptance:** the CLAWE solution builds with no PRISM project reference; the theme files are
> local copies.
> **Traces to:** `DESIGN.md` DD-4.

> **FR-60 — STS-matching chrome**
> The application window SHALL render the WPF-UI dark Mica chrome, the Spartan-helmet icon, and the
> STS blue accent, applying the theme explicitly at startup.
> **Rationale:** `DESIGN.md` §2 ("recognises the app"), DD-4 (the startup gotcha).
> **Acceptance:** the built exe launches with dark Mica chrome and the correct icon; a visual
> checkpoint at timeline iterations 2, 7, 8, and 9 confirms parity with the lead.
> **Traces to:** `DESIGN.md` §2, DD-4.

<Total: 64 functional requirements.>

## 4. Non-functional requirements

> **NFR-1 — Whole-radar save latency**
> Saving a radar (which re-serializes the entire `ClaweRadarInstance`) SHALL complete in ≤ 500 ms for
> a radar holding 2,000 waveforms on the reference benchmark host (§5).
> **Verification:** a benchmark that builds a 2,000-waveform radar and times a save, recorded per
> iteration from iteration 3. `WaveformSaveLatencyBenchmarkTests` times the full editor Save, which
> is three whole-blob writes: radar identity, mode, waveform. Iteration 3: median 63 ms (Release,
> 572 KiB blob) on a 20-core dev machine; not yet run on the reference host.
> **Traces to:** `DESIGN.md` DD-2, §3 (scale), OQ-9.

> **NFR-2 — Waveform-browser query latency**
> A filtered waveform-browser query over a mode of 5,000 waveforms SHALL return the first page in
> ≤ 200 ms on the reference benchmark host (§5) and SHALL execute against `ClaweWaveformCalcRollup`
> rows only, with zero blob deserializations.
> **Verification:** a benchmark plus an assertion that no `ClaweRadarProtoBlob` read occurs during
> the query.
> **Traces to:** `DESIGN.md` §3 (scale), DD-2, DD-9.

> **NFR-3 — Live-recompute responsiveness**
> The Waveform Summary Screen and the signal preview SHALL fully update within 100 ms of a bound
> field change on the reference benchmark host (§5), without a polling timer.
> **Verification:** measured latency from a simulated property change to the rendered update.
> **Traces to:** `DESIGN.md` §5 (Calc Engine), §6.1.

> **NFR-4 — `RequestRadars()` deadline**
> The proxy SHALL respond to `RequestRadars()` within a 5 s RPC deadline for the design catalogue
> size of 500 radars (§5, `DESIGN.md` §3) on the reference benchmark host; a response that would
> exceed the deadline SHALL be paged or streamed (mechanism — OQ-12).
> **Verification:** load test with a 500-radar database.
> **Traces to:** `DESIGN.md` §3 (scale), §6.2, §9 (FM-11), OQ-12.

> **NFR-5 — Two storage layers never diverge**
> After any sequence of radar writes, the mode list in each `ClaweRadarProtoBlob` SHALL exactly match
> the `ClaweRadarMode` index rows for that radar.
> **Verification:** a property/invariant test that performs randomised write sequences and asserts
> equality after each commit.
> **Traces to:** `DESIGN.md` DD-2, §6.1.

> **NFR-6 — Atomic schema upgrade**
> No schema-update run SHALL leave `CLAWE DB` in a state where the applied structure and the
> `ClaweSchemaVersion` value disagree.
> **Verification:** fault-injection test that fails each patch step in turn and asserts the version
> and structure both reflect the last fully-applied step.
> **Traces to:** `DESIGN.md` DD-3, §9 (FM-4).

> **NFR-7 — Single-writer guarantee under mutex bypass**
> Even if two processes both believe they hold the maintenance role, at most one SHALL be able to
> commit a write; the second SHALL fail before committing.
> **Verification:** a test that opens two writer contexts against one file and asserts the second
> commit throws.
> **Traces to:** `DESIGN.md` DD-5, §9 (FM-2).

> **NFR-8 — Isolation from PRISM data**
> CLAWE UI SHALL never open, read, or write `emitters.db` or any PRISM database, and SHALL share no
> connection, schema, or primary-key sequence with PRISM.
> **Verification:** static review of all `DbContext` construction plus a check that the CLAWE
> solution references no PRISM project.
> **Traces to:** `DESIGN.md` DD-1, DD-3.

> **NFR-9 — Offline authoring**
> The Maintenance View SHALL perform all authoring, validation, and calculation with no network
> access.
> **Verification:** run the full author-a-radar flow with networking disabled.
> **Traces to:** `DESIGN.md` §3 (platform).

> **NFR-10 — Proxy auto-start**
> The CLAWE Proxy SHALL be configured to start at user logon (DD-21) and to restart within 30 s of an
> unexpected exit.
> **Verification:** deployment check on the reference host — (a) a reboot and logon leave the proxy running;
> (b) killing the proxy process, it is running again within 30 s.
> **Traces to:** `DESIGN.md` §5 (Proxy), DD-5.

> **NFR-11 — Backward-compatible blobs**
> An additive proto3 field SHALL NOT prevent an older `clawe-v1` blob from deserializing; the reader
> SHALL apply defaults for absent fields.
> **Verification:** a round-trip test that reads a stored `clawe-v1` blob with the current schema.
> **Traces to:** `DESIGN.md` §9 (FM-3), DD-2.

> **NFR-12 — Transport-neutral message contract**
> The `CLAWE.Contracts` message types SHALL contain no RabbitMQ-specific code, so a switch to ZeroMQ
> would change only `CLAWE.Messaging`.
> **Verification:** review — `CLAWE.Contracts` has no transport dependency.
> **Traces to:** `DESIGN.md` DD-6, OQ-2.

> **NFR-13 — Multi-host operation**
> The system SHALL function with STS UI, CLAWE UI, and HOCA on separate machines, making no same-host
> assumption about another component's database or filesystem.
> **Verification:** an integration test (or review of every cross-component access) confirming only
> network calls cross component boundaries; an end-to-end run across two machines before release.
> **Traces to:** `DESIGN.md` §3 (assumptions), DD-1.

> **NFR-14 — Iteration demo cadence**
> Every 2-week iteration SHALL end in a runnable demo `.exe` that preserves all prior demo
> functionality.
> **Verification:** the iteration review records a built exe and a regression check of prior demo
> flows.
> **Traces to:** `DESIGN.md` §1; `CLAWE_UI_Iterative_Timeline.html`.

> **NFR-15 — Calc-engine determinism and purity**
> `WaveformMetricsCalculator.Compute` SHALL be a pure function — same `WaveformCalcInput` and
> `ScenarioAssumptions` always yield the same result, with no WPF, EF, or I/O dependency.
> **Verification:** `CLAWE.Calc` references neither WPF nor EF; repeated calls with equal input
> return equal output.
> **Traces to:** `DESIGN.md` §5 (Calc Engine).

> **NFR-16 — Validation coverage of the deck**
> Every modifier parameter listed in deck slides 27–32 SHALL have an enforced min/max in the editor.
> **Verification:** a test that enumerates the deck parameter table and asserts a validation rule
> exists for each entry.
> **Traces to:** `DESIGN.md` §2 (goal 2), §6.1.

<Total: 16 non-functional requirements.>

## 5. Constraints & assumptions

Carried from `DESIGN.md` §3:

- **Platform:** C#/WPF/.NET 10; SQLite via EF Core; Protobuf (proto3, `Clawe.V1`); RabbitMQ
  (AMQP 0-9-1) for interfaces B and C; Windows desktop.
- **Approved data model:** `ClaweRadarInstance` / `ClaweRadarModeInstance` / `ClaweWaveformInstance`
  approved as-is 2026-08-18; the two cardinality narrowings (DD-7, DD-8) are lead-confirmed. No
  schema-concept changes are pending.
- **Look and feel:** must match the STS UI (`PRISM.UI` conventions) and follow `PRISM.Database` DB
  patterns.
- **Scale:** hundreds to thousands of waveforms per mode.
- **Assumptions:** STS / CLAWE / HOCA may be co-located or on separate machines; one proxy and one
  `CLAWE DB` per host; a radar always has `1..N` modes; authoring happens only in the singleton
  Maintenance View.
- **Legacy parity:** field names and behaviour are reconciled against `sparta/`'s CLAWE settings
  objects during iteration 3 (`DESIGN.md` OQ-5) — the data model itself does not change.
- **Delivery:** ~20 hrs/week, 2-week iterations, 12 iterations (~24 weeks); `1.0.0` is a deliberate
  release-readiness pass after iteration 12.
- **Reference benchmark host:** performance targets (NFR-1, NFR-2, NFR-3, NFR-4) are stated against
  the project's CI benchmark host — a mid-range developer laptop (4-core x64, 16 GB RAM, SSD),
  running the self-contained Release build. Numbers are recorded per iteration so regressions are
  visible even if the exact host changes.
- **Catalogue size:** a `CLAWE DB` is expected to hold on the order of a few hundred radars; **500
  radars** is the design figure for interface-B response sizing (`DESIGN.md` §3).

## 6. Out of scope

From `DESIGN.md` §2 non-goals, plus clarifications:

- CW waveform authoring (parameters, modifiers, editor). The `BaseWaveform.CW` enum value ships for
  interface-B vocabulary stability only.
- `RadarModeType` values other than `TTR` (authoring). They are modelled and shown, not authorable.
- Any PRISM-plugin packaging or shared runtime assembly with PRISM.
- Implementing HOCA, STEEM, the SPARTA SW Simulator, or the STS static-scenario builder.
- Standing up or operating the RabbitMQ broker.
- Cross-host coordination of the single-writer rule.
- A general emitter-authoring tool — CLAWE UI models closed-loop CLAWE radars only.
- The internal algorithm of cognitive optimisation (Learning vs Speed search). Only its UI and state
  display are in scope.
- The specific 3D-RDI-scope rendering library — a placeholder is acceptable; any library that fits
  may be used (see §8.2 item 2).
- Interface A, D, E, F.

## 7. Traceability matrix

The Task ID column is filled from the [iteration timeline](CLAWE_UI_Iterative_Timeline.html) (used
here in place of a `TASKS.md`) as work is scheduled.

| Requirement | Design section | Timeline iteration |
|---|---|---|
| FR-1 | §5 (CLAWE DB), §8 | 1–3 |
| FR-2 | §8, DD-11 | 1 |
| FR-3 | §8 | 2 |
| FR-4 | §8, §6.3 | 3 |
| FR-5 | DD-8 | 2 |
| FR-6 | DD-7, §8 | 1 |
| FR-7 | DD-2, §6.1, §8 | 2–3 |
| FR-8 | DD-11, §5, §8 | 1 (rename), 4 (event) |
| FR-9 | §8 | 1 |
| FR-10 | DD-3, §5, §9 (FM-4) | 1 |
| FR-11 | §5 (CLAWE DB) | 1 |
| FR-12 | §5 (Maintenance View), §6.1 | 2 |
| FR-13 | §2, §5, §9 (FM-6) | 2–3 |
| FR-14 | §6.1, §9 (FM-6) | 2–3 |
| FR-15 | §9 (FM-7) | 2 |
| FR-16 | §8, DD-15 | 2, 3 |
| FR-17 | §8, §6.3, DD-15 | 2, 3 |
| FR-18 | §8, DD-14 | 3 |
| FR-19 | §8 | 3 |
| FR-20 | §8 | 3 |
| FR-21 | DD-12 | 2 |
| FR-22 | §6.1 | 1 |
| FR-23 | §5 (Maintenance View) | 1 |
| FR-24 | §6.1 | 2 |
| FR-25 | §2, §5 (Maintenance View) | 1 (shell), 10 (Freq/PRI) |
| FR-26 | §5 (Calc Engine) | 5 |
| FR-27 | §5 (Calc Engine) | 5 |
| FR-28 | §9 (FM-8) | 5, 8 |
| FR-29 | §5 (Calc Engine) | 8 |
| FR-30 | §5, DD-10 | 8 |
| FR-31 | §2, §3, DD-2, DD-9 | 10 |
| FR-32 | §2, §5, DD-10 | 9 |
| FR-33 | §4, §5 (Proxy), DD-5 | 4 |
| FR-34 | §4, DD-5, §9 (FM-1) | 4 |
| FR-35 | §4, DD-5, §9 (FM-2) | 4 |
| FR-36 | §4, §5 (Maintenance View) | 4 |
| FR-37 | §4, DD-5 | 4 |
| FR-38 | §2, §3 | 4 |
| FR-39 | §6.2, DD-9 | 4 |
| FR-40 | DD-9, §8 | 4 (hand-rolled), 10 (rollup) |
| FR-41 | §6.2, DD-9 | 4 |
| FR-42 | §6.1, §5 (Proxy) | 4 |
| FR-43 | §5 (Proxy), §6.2 | 4 |
| FR-44 | §4, §5 (Proxy) | 4 |
| FR-45 | §5 (Proxy) | 4 |
| FR-46 | DD-6, §5 (Proxy) | 4 |
| FR-47 | §9 (FM-5) | 4 |
| FR-48 | §9 (FM-9, FM-12) | 4 |
| FR-49 | §5 (Execution View), §6.3 | 6 (demo launch), 11 (HOCA launch) |
| FR-50 | §5 (Execution View) | 6 |
| FR-51 | §4, §5 (Execution View) | 6 |
| FR-52 | §5 (Execution View), §6.3, DD-15 | 6 (empty-schedule refusal), 11 (HOCA load) |
| FR-53 | §6.3 | 6, 11 |
| FR-54 | §4, §5 (Execution View) | 6 |
| FR-55 | §5 (Execution View), §6.3 | 6, 12 (cognitive) |
| FR-56 | §9 (FM-10) | 11 |
| FR-57 | §5 (Execution View), OQ-4 | 7 |
| FR-58 | §5 (Execution View), §6.3, OQ-3b | 6 (target table), 7 (container, RDI scope), deferred (live feed) |
| FR-59 | DD-4 | 1 |
| FR-60 | §2, DD-4 | 1 |
| FR-61 | §9 (FM-13) | 6 (local report), 11 (report to HOCA) |
| FR-62 | §9 (FM-14) | 11 |
| FR-63 | §6.2, DD-9 | 4 |
| FR-64 | §8 | 4 |
| NFR-1 | DD-2, §3, OQ-9 | 3, ongoing |
| NFR-2 | §3, DD-2, DD-9 | 10 |
| NFR-3 | §5 (Calc Engine), §6.1 | 8-9 |
| NFR-4 | §6.2, §9 (FM-11), OQ-12 | 4, 10 |
| NFR-5 | DD-2, §6.1 | 2–3 |
| NFR-6 | DD-3, §9 (FM-4) | 1 |
| NFR-7 | DD-5, §9 (FM-2) | 4 |
| NFR-8 | DD-1, DD-3 | 1 |
| NFR-9 | §3 | 1 |
| NFR-10 | §5 (Proxy), DD-5 | 4, 12 |
| NFR-11 | §9 (FM-3), DD-2 | 3 |
| NFR-12 | DD-6, OQ-2 | 4 |
| NFR-13 | §3, DD-1 | 4, 11, 12 |
| NFR-14 | §1 | every |
| NFR-15 | §5 (Calc Engine) | 5 |
| NFR-16 | §2, §6.1 | 3 |

## 8. Open questions

The open questions themselves live in the **canonical register** — [`DESIGN.md`](DESIGN.md) §10,
`OQ-1` … `OQ-16`. This section only records **which requirement each one blocks or refines**, and
which design elements deliberately produced no requirement.

### 8.1 Requirements blocked or limited by an open question

| Open question | Requirement affected | How |
|---|---|---|
| **OQ-3b** — interface-C telemetry feed | FR-58 (live-feed clause), FR-57 (partial) | FR-57's container is verifiable now; FR-58's live-feed acceptance is held at Draft and verified against a mock until the feed is specified. |
| **OQ-12** — large-response paging/streaming | NFR-4, FR-39 | NFR-4 states the 5 s deadline. Measured in iteration 4: 1,000 radars take 37 ms (128 KiB), so a paging mechanism isn't needed at the design scale. |
| **OQ-10** — second-launch behaviour | FR-44 | FR-44 covers same-host focus and reject. Proposed in iteration 4, pending the lead: focus; cross-host can't arise under FR-38. |
| **OQ-16** — Execution View waveform edits vs. the single writer | FR-50, FR-51 | FR-50 lets the operator add/edit waveforms in an Execution View; FR-51 says it never writes. One of them changes once the lead decides whether those edits are transient. Before iteration 9. |
| **OQ-8** — `modulation_types` 6-of-9 scope | FR-40 | FR-40 specifies the 6-value set provisionally; whether the 3 omitted categories are intended is open. |
| **OQ-6** — calc-engine formula ambiguities | FR-26, FR-27 | FR-27's tolerance for the affected worked examples cannot be fixed until the formulas are confirmed. |
| **OQ-1** — RabbitMQ broker ownership | §3.5 / §3.6 (operational) | Not a requirement gap — an environment decision. The interface requirements are testable against a local broker regardless (a Docker broker since iteration 4). |
| **OQ-2** — RabbitMQ vs ZeroMQ | (none; resolved) | Resolved in iteration 4: RabbitMQ, per the deck. NFR-12 still holds, so a later change would touch only `CLAWE.Messaging`. |
| **OQ-11** — proxy multi-PC identity / discovery | NFR-13, FR-38 | NFR-13 is verifiable with statically-configured endpoints until discovery is designed. |
| **OQ-5** — legacy field reconciliation | (none; resolved) | Resolved in iteration 3 with no schema change (`CLAWE_Legacy_Reconciliation.md`). Its open deck questions moved to OQ-15. |
| **OQ-15** — waveform-parameter gaps and legacy conflicts | FR-13 | FR-13 validates against the deck's ranges. Six fields the deck leaves unbounded are checked `≥ 0` only. The SP Rampup / SP Prepulse ranges conflict with legacy values. Each is tightened or widened once the deck author answers. |
| **OQ-13** — high-pulse-count preview strategy | FR-32, FR-58 | These state *that* a preview / RDI scope renders and updates; the rendering approach for ~1,024-pulse trains is held open and iterated with the lead. |
| **OQ-14** — `LoadWaveforms` radar vs. mode scope | FR-52 | FR-52 follows the deck's "every waveform instance for the active radar" wording provisionally; if the answer is "active mode", the payload narrows; if "whole radar", waveform IDs need a radar-wide-unique or composite key. |

### 8.2 Design elements that deliberately produced no requirement

Flagged so a reviewer does not read the absence as an omission:

1. **Cognitive-optimisation internals.** `DESIGN.md` §6.3 / §8 name `OptimizationType {Learning,
   Speed}` but not the search behaviour. Out of scope by decision (§6); FR-55 covers only the UI and
   state display.
2. **The 3D RDI scope beyond FR-57's container.** `DESIGN.md` OQ-4 and the timeline treat it as a
   genuine placeholder; a dedicated requirement would be premature.
3. **`DESIGN.md` DD-13** (git-repo structure, Markdown-is-source). A documentation-process decision,
   not product behaviour — out of scope for this spec by nature.

## 9. Changelog

- **v1.6 — September 2026** — Iteration 4 (`DESIGN.md` v1.6, DD-18 to DD-21):
  - **Iteration numbers follow timeline Draft v5** (running-radar demo first): the Execution View and
    a simulated radar are iteration 6, the graph container and 2D RDI scope 7, the summary screen 8,
    the live preview 9, rollups and the browser 10, interface C and real HOCA 11. §7 is remapped
    (FR-25, 26–32, 40, 49–58, 61, 62; NFR-2, 3, 4, 13).
  - Added **FR-64** (the values behind a waveform's Fixed CF / PRI / PW choices, checked against the
    mode's envelope), from the lead's v0.3.0 review. Total 63 → 64 FR.
  - **FR-33** and **NFR-10:** the proxy starts at user logon, in the user's session (DD-21),
    rather than at system start.
  - **FR-35:** the write-owner row is claimed at startup and checked before every commit; the
    acceptance names NFR-7's same-process case.
  - **FR-40:** acceptance split into iteration 4 (envelope-only) and iteration 10 (rollups). Waveforms
    store their CF, PRI and PW from v0.4.0 (FR-64), and FR-64 keeps them inside the envelope.
  - **FR-44:** notes OQ-10's proposed answer, and the Windows foreground limit.
  - **FR-46:** the request queue is namespaced per endpoint, `clawe.ifaceB.rpc.<source_name>`.
  - §8.1: OQ-2 resolved; OQ-10 and OQ-12 updated; new **OQ-16** (FR-50 vs. FR-51).

- **v1.5 — September 2026** — Iteration 3 decisions recorded (`DESIGN.md` DD-14, DD-15):
  - **FR-18:** a mode's allowed modifiers and PD / SP enablement can't be narrowed under a waveform
    that uses them (DD-14). FR-15 notes the lock.
  - **FR-16:** an Auto mode may be saved with an empty schedule, shown as a notice (DD-15).
  - **FR-17:** the schedule picker lists the mode's waveforms, and "add entry" needs one.
  - **FR-52:** activation refuses an Auto mode with an empty schedule.

  Also: NFR-1 records the iteration-3 benchmark figure (63 ms). §8.1 marks OQ-5 resolved and adds
  OQ-15, affecting FR-13.

- **v1.4 — September 2026** — Added **OQ-14** (`LoadWaveforms` radar vs. mode scope) to §8.1,
  affecting FR-52.

- **v1.3 — September 2026** — Added **OQ-13** (high-pulse-count preview rendering strategy) to
  §8.1, affecting FR-32 and FR-58. Raised by the lead's v0.2.0 feedback.
- **v1.2 — September 2026** — §8 restructured: open questions now live in the canonical register
  (`DESIGN.md` §10, `OQ-1` … `OQ-12`); §8.1 maps each `OQ` to the requirement it blocks, §8.2 keeps
  the "no requirement generated" notes. All `§8.x` / `§10 (Qn)` cross-references in FR/NFR bodies and
  the traceability matrix replaced with `OQ-<n>`. Fixed an FR-20 acceptance typo (`FR-25` → `FR-26`).
- **v1.1 — September 2026** — Applied `SPEC_REVIEW.md` findings. FR-17 rewritten as a single
  testable rule (block deleting a scheduled waveform) — F-2. FR-57 / FR-58 split into a
  verifiable-now container requirement and a Draft live-feed clause — F-3. Added a reference
  benchmark host and a 500-radar catalogue figure to §5, and re-anchored NFR-1 – NFR-4 on them —
  F-4, F-5. FR-43 given a 250 ms debounce window and a ≤ 1 s latency bound — F-6. FR-5 trace
  corrected — F-7. FR-40 names the 6-value modulation set explicitly — F-10. Added FR-61 / FR-62
  for the interface-C load-failure paths (`DESIGN.md` FM-13 / FM-14) — F-9. FR-4 states ID
  auto-assignment — F-15. NFR-10 verifies restart-on-failure — F-16. Added §8 item 10 (DD-13
  produced no requirement) — F-11. Added FR-63 for the `RequestRadars` response `source_name` /
  `schema_version` fields — F-R1 (2nd review pass). Total 60 → 63 FR.
- **v1.0 — September 2026** — Initial draft. 60 functional and 16 non-functional requirements
  derived from `DESIGN.md` v1.0, covering data model and persistence, authoring and validation, the
  waveform calculation engine, the proxy and instance model, interface B, interface C and execution,
  and look-and-feel. Open questions recorded, including design elements (cognitive-search internals,
  3D RDI scope) that deliberately generated no requirement.
