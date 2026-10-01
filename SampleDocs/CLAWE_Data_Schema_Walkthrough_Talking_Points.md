# CLAWE Data Schema Walkthrough — Talking Points

> **Superseded (2026-09-08).** These notes were written for the walkthrough of
> `CLAWE_Data_Schema.html` **v1.2**; the schema is now **v3.0**. The narrative (why a
> blob + thin index, ClaweDB/PrismDB independence, the `oneof` shape) still holds, but
> the specifics — `AlternateName` and `Modes` cardinality, the Phase-modifier split,
> `NumPulses`, `CW` — have moved. See the schema doc's Changelog for the current state.

**Audience:** PRISM/STS lead software/project manager + the PRISM parent-app developer.
Both already know the existing PRISM/STSSE patterns well — including `oneof` usage in
`stsse.v7` (`WaveformRecipeDefinition.detail`, `ModulationDefinition.detail`) — and they're
the ones who made the ClaweDB/PrismDB independence call. Lean on that shared context
throughout: reference existing patterns by name instead of re-deriving them, and spend
the meeting's time on what's actually new (CLAWE-specific field shapes) rather than
re-explaining PRISM conventions this room already owns.

Reference doc: `CLAWE_Data_Schema.html` (v1.2, In Review). Walk it top to bottom — its
section order is this outline's section order.

---

## 1. Open — one breath, then the headline

- Scope: CLAWE Emitters App's own data only — not the STS-side scenario integration.
- Built off the requirements deck's three-level structure (Radar → Mode → Waveform),
  cross-checked against legacy `sparta/`.
- **Lead with the resolution, not the walkthrough:** "All 9 open questions from the first
  review are decided — including the one you two answered: ClaweDB and PrismDB are
  completely separate, independent databases." Get this out in the first minute.

## 2. The two diagrams — narrate the pairing, not just the contents

Walk Fig. 1 (class diagram) then Fig. 2 (ER diagram). The point of showing both is the
gap between them — say that explicitly, don't just present two pictures.

- **Fig. 1:** "Full authored shape — Radar contains Modes, Modes contain Waveforms, each
  Waveform carries a stack of 9 independently-toggleable modifiers."
- **The `oneof` pattern — keep this short for this room:** "Every modifier uses a
  `oneof`, same as `WaveformRecipeDefinition.detail` already does for recipe kind in
  `stsse.v7` — applied nine more times, nothing new structurally." Don't build up
  "discriminated union" from first principles here; name-drop the existing pattern and
  move on.
  - **If asked "why does `None` get its own explicit oneof branch instead of just
    leaving the `oneof` unset"** (a question this audience is likely to actually ask):
    the deck enumerates `None` as one of the modifier's legal values
    (`{None, Rampup, Prepulse}`), so it's a deliberate authored choice, not the absence
    of one. An explicit `None` branch lets the data distinguish "this modifier was
    turned off on purpose" from "this modifier was never touched" — unset can't make
    that distinction on round-trip. Optional fields that are genuinely just "not yet
    considered" stay unset; a toggle the deck explicitly enumerates as having a "none"
    state gets an explicit branch.
  - **Second, distinct pattern also in play, worth not conflating with the above:**
    `ClaweWaveformInstance.BaseWaveform` (`{PD, SP}`) is a plain enum that gates whether
    *other sibling fields* on the same message apply — `PRIModifier`/`PWModifier`/
    `TrailingEdgeModifier` only when PD; `AmplitudeModifier` only when SP. Not a `oneof`
    structurally (they're independent optional fields), but the same discipline: a
    well-defined field decides which other fields are meaningful, rather than leaving it
    to convention.
- **Fig. 2:** "Deliberately much sparser than Fig. 1 — only what actually needs to be a
  queryable SQLite column." The size gap between the two diagrams is the visual case for
  section 3.

## 3. Two-layer storage + database independence — the core of the meeting

- Blob-vs-index split, quickly: "Everything in Fig. 1 serializes as one protobuf blob
  per radar — that's the source of truth. Fig. 2 is a thin index that exists only so a
  picker list can show names without deserializing a blob per row."
- Why thinner than the Emitter/EmitterMaker pattern they know: "EmitterMaker needs deep
  rollup tables because it filters a shared library of 1-2M+ rows it doesn't author.
  We're an authoring tool over our own data — no filtering requirement today, so we're
  not building query infrastructure nobody's asked for."
- **Database independence — confirm back to them, don't pitch it as new:** "ClaweDB and
  PrismDB are two fully separate SQLite files, two separate DbContexts, per your call.
  No shared connection, no shared `SchemaVersion` table, and no risk of our PKs ever
  colliding with `PrismDatabase`'s emitter records, since we're not in the same database
  at all." Frame this as confirming their decision landed in the schema correctly, not
  as convincing them of something.
- Ready answer if asked "won't two databases mean extra sync work": no — there's no sync
  requirement, they're independent by design, not by omission.
- Fallback if anyone wants it more concrete: §3.1's worked example (`AN/APQ-Demo` radar,
  two modes, actual `ClaweRadarPk`/`ClaweRadarModePk` values) shows the blob-vs-FK
  linkage with real numbers instead of the abstract description.

## 4. Field reference tables — reference, don't read

- Hit the shape once per table, don't read rows aloud: "4.1 is radar identity. 4.2 is
  the mode — this is where the constraint envelope lives, the parametric min/max
  replacement for legacy's hardcoded lookup tables. 4.3 is a waveform instance. 4.4 is
  the modifier stack, one row per modifier."
- One number worth having ready: 7 of 9 modifiers have a direct legacy equivalent, 1 is
  a merge of two legacy fields, and Pulse Compression is genuinely new — legacy has
  nothing like it.

## 5. Open questions table — the resolution record

- All 9 decided. Call out the ones with real structural consequences, since they're easy
  to miss in a table skim: dropping `radar_id`/`mode_id` for `Name`-only identity
  (Q6), PD+SP coexisting on one mode (Q5), and DB independence (Q7).
- Everything else (list-vs-bitmask, placeholder fields, WaveformCompression) is
  lower-stakes — don't dwell.

## 6. Close

- State the ask plainly: with all 9 questions resolved, is this the green light to move
  from "discussion draft" to actually writing the `.proto` files and `ClaweDbContext`
  EF entities?
- Mention, briefly, that the bare plugin shell (`PRISM.ClaweEmitters`) already exists and
  loads cleanly in `PRISM.Host` — the plumbing is proven out. Don't dwell; that's not
  what this meeting is deciding.

---

## Pre-armed for this specific room

- **"Why does `None` need its own oneof branch instead of relying on unset?"** — see §2
  above; have this one ready verbatim, this audience is exactly the kind to ask it.
- **"Why not just put CLAWE tables in the existing PrismDatabase?"** — this is their own
  decision; if asked to restate the reasoning, don't invent one — ask them to confirm
  what drove it, since that context wasn't captured beyond "decided."
- **"Does this affect the STS side?"** — no, out of scope for this doc entirely.
- **"Isn't storing everything as one blob risky to query into?"** — no, by design:
  anything worth querying gets its own indexed column in the thin tables; the blob is
  round-trip storage, not a query target.
- **"How were the specific Fig. 2 columns chosen?"** — one rule, applied consistently:
  a field only gets a column if a picker/list screen actually needs to display or click
  into it, nothing else.
  - `ClaweRadar`: `Name`/`Description`/`ModeCount` — what a radar-library list row shows.
  - `ClaweRadarAlternateName` got its own table for a different reason than the rest —
    it's *searchable* ("find the radar with ELNOT X"), not just displayed. That's the
    only field promoted for search rather than list-display.
  - `ClaweRadarMode` / `ClaweRadarModeWaveform`: `Name` + one or two type/category
    fields — enough for a mode list or a waveform picker dropdown.
  - Everything else — the full constraint envelope, all 9 modifiers' parameters — stays
    blob-only. The line was drawn by absence of a requirement, not by depth: nothing in
    the deck asks for range/filter queries across a radar library the way EmitterMaker's
    rollup tables do, so no column was added speculatively for a query nobody described.
    Same reversibility note as above — a real filtering need later gets served by an
    additive rollup table, not a redesign.
