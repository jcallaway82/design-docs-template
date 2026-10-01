# CLAWE UI — Iterative Delivery Timeline

> **Rendered version:** `CLAWE_UI_Iterative_Timeline.html` (in the design-doc suite). This
> Markdown file is the editable source — regenerate the HTML after a substantive change
> (the `html-suite-builder` agent does this). If the two disagree, this file wins.

**Pace:** ~20 hrs/week (half time) · **Cadence:** 2-week iterations, each ending in a
runnable demo `.exe` for the lead to open and click through. Iterations are additive —
each keeps every prior demo working.

**Status:** Draft v5 (2026-09-30) — reordered to reach a *running radar demo* sooner (see "Draft v5
changes" below). Draft v4 (2026-09-08)
changes" below). Draft v3 (2026-08-25) added a mid-course Radar search/filter overlay
(see that section below). Draft v2 (2026-08-18) changes summarized below still stand.

### Draft v5 changes (2026-09-30)

The PM wants to start demos to potential buyers as soon as a radar can be shown running, and the
HOCA / hardware side is the least important part. Changes:

- **Running-radar path pulled forward.** A simulated radar behind a runtime interface (6), then the
  graph container + 2D RDI scope (7). The demo-able build moves from iteration 11 (week 22) to
  **iteration 7 (week 14)**, eight weeks sooner.
- **HOCA moves last** (iteration 11, with its data wiring). The simulator stays as the demo source.
- **Authoring polish moves later:** summary screen 6 → 8, live preview 7 → 9, rollups + browser 8 → 10.
- **Total unchanged:** 12 iterations, ~24 weeks. Nothing was dropped; the target table and Control tab
  came from old iterations 9 and 10, and the 2D RDI scope from old 11.
- The traceability matrix in `REQUIREMENTS.md` §7 still uses the old numbers; it will be remapped once
  the PM approves this order.

### Draft v4 changes (2026-09-08)

Three inputs landed and are folded into the iteration table below:

- **`STS SW Interface Descriptions.pptx`** — interface B is now a concrete spec
  (TCP + RabbitMQ + Protobuf, a `ClaweRadarSummary` response, a radar-modified pub/sub
  event, "one maintenance UI at a time: yes") and interface C now has a control-message
  spec. Interface B's iteration grows to also carry the **proxy + split single-purpose
  view** process-model restructure (per the 2026-09-08 meeting: an always-on proxy,
  a singleton maintenance view that is the sole DB writer, `0..n` execution views).
- **`CLAWE Waveform Calculations.pptx`** — a new **Waveform Summary Screen** requirement
  backed by a **calculation engine** (5 formula families), and the lead wants the results
  browsable across a mode's hundreds–thousands of waveforms via a **filterable list**.
- Small schema change: Phase modifier splits into Full/Partial Phase Encoded; FFT size
  vs Num Pulses; `BaseWaveform += CW` (enum only). Documented in `CLAWE_Data_Schema.html`
  v3.0; the proto edits land as part of iteration 3's waveform stack.

Net effect: **9 → 12 iterations, 18 → ~24 weeks / ~360 → ~480 hours.** The +6 weeks are
the calc engine + summary screen + waveform browser + rollup foundation, plus the proxy
restructure inside the interface-B iteration. See the compression levers note under the
table if ~24 weeks is not acceptable.

1. **Framework/CRUD iterations compressed.** Scaffolding, `CLAWE DB` setup, and basic
   list/CRUD screens are expected to go faster than originally budgeted — they're
   well-trodden ground (`PRISM.Database`/`PRISM.UI` patterns to copy, approved schema
   already in hand, no open questions blocking them).
2. **Visualization gets its own runway, earlier.** The lead developer is visual and
   wants CLAWE UI's charts/waveform previews/tables/signal displays to mirror STS's
   existing data-visualization work (`PRISM.UI` signal preview controls, the RTSA
   window pattern, `PRISM.EmitterMaker`'s preview graphs). That's the highest-risk,
   least-precedented part of this project for CLAWE UI specifically — time saved on
   the framework iterations is reallocated there instead of compressing the total
   schedule, so visualization isn't crunched at the end.

Revisit the back half again once HOCA and the RTSA-window pattern are located (see
`DESIGN.md` §10, OQ-3 and OQ-4) — iterations 11–12 are the most likely to shift.

> The schema `.pptx` in this folder (`CLAWE_Data_Schema.pptx`) is **superseded** by
> `CLAWE_Data_Schema.html` (now v3.0, ~2 major versions ahead) — use the HTML.

**This plan is fluid.** It's a working draft, not a commitment — expect it to move as
new requirements or features surface once we're actually building, and as the open
questions below get answered. Treat each iteration boundary as a natural checkpoint to
re-baseline, not just a status update.

---

## De-risking call-out: do the visualization spike early, not late

Rather than discovering charting/rendering problems in iteration 7 when the graph
windows are due, iteration 2 below includes a **half-iteration spike**: pick and prove
out the charting/rendering approach CLAWE UI will use for *everything visual* —
waveform/pulse-train previews in the maintenance-mode editors **and** the RDI
scopes/target table in operate mode later — before either depends on it.

Concretely, that means before iteration 2 ends, answer:
- What does STS/`PRISM.UI` actually use for its signal preview controls and (once
  located) the RTSA window — a WPF charting library (e.g. OxyPlot, ScottPlot,
  LiveCharts), custom `Canvas`/`DrawingVisual` rendering, or something else? Match it,
  don't introduce a second charting stack into a codebase meant to look-and-feel like
  STS.
- Does that approach comfortably handle the two very different visual jobs CLAWE UI
  needs: (a) static/low-frequency parameter previews (a waveform's pulse train, a
  modifier's effect) in the maintenance-mode editors, and (b) higher-rate streaming
  data (2D/3D RDI scope, target table updates) in operate mode?
- One throwaway prototype control, themed with real `PRISM.UI` tokens, rendering a
  representative CLAWE waveform (e.g. a PD pulse train with a PRI modifier applied) —
  proof that the visual language will actually match STS before it's load-bearing in
  four different editors and two graph-window types.

This spike is a small, contained cost now against the alternative: rebuilding the
preview/graph plumbing mid-project because the first real attempt (the eclipsing chart
in iteration 8, or the RDI scope in iteration 7) turns out to be the wrong foundation.

---

## Iteration table

**Dependency spine:** schema extension (3) → interface B + proxy (4) → calc engine (5) →
simulated radar + Control tab (6) → graph container + 2D RDI scope (7, **buyer-demo milestone**) →
summary screen (8) → live preview (9) → rollup + browser (10) → interface C + real HOCA (11) →
cognitive + 3D scope + polish (12).

**Why this order (Draft v5):** the product demo is a *running* radar, and HOCA/hardware is the
least important dependency. So the running-radar path (calc engine → simulated radar → scope)
comes first, behind a runtime interface that real HOCA replaces in iteration 11. The authoring-side
polish (summary, preview, browser) follows, since the editor already works.

| # | Weeks | Focus | Demo-able at end |
|---|---|---|---|
| 1 ✅ | 1–2 | **Scaffolding + DB + Radar CRUD.** *(Complete — shipped v0.1.0 / v0.1.1.)* Standalone CLAWE UI solution (WPF, .NET 10), `PRISM.UI` theme, `CLAWE DB` (EF Core + SQLite), Maintenance/Operate nav shell, Radar CRUD + NATO/ELNOT alt-names, plus the mid-course Radar search/filter overlay and delete-confirmation dialog. | Exe launches themed to match STS; create/rename/alt-name/delete radars persist across relaunch. |
| 2 ✅ | 3–4 | **Radar Mode editor + visualization spike.** *(Complete and merged to `master` — shipped v0.2.0, then three rounds of lead feedback fixes as v0.2.1/v0.2.2/v0.2.3.)* Add/edit `ClaweRadarModeInstance`: identity, `RadarModeType` (TTR enabled, others disabled), `OperatingMode` (Manual/Auto/Cognitive) with Auto schedule + Cognitive OptimizationType, full constraint envelope — built as a **combined radar + mode editor** (STS EmitterMaker style: radar identity + first mode in one form, mode-pill strip to switch modes). **Plus the visualization spike** (ScottPlot 5 — PRISM's stack — one throwaway themed pulse-train page + a `GraphThemeHelper` copy from `PRISM.UI`). **Also done:** relabel "PD" → "Pulsed" in UI text; **extracted proto compilation into a new `CLAWE.Proto` project** (`Google.Protobuf` + `Grpc.Tools` + the `.proto` files; namespace `Clawe.V1` unchanged) so `CLAWE.Calc` / `CLAWE.Contracts` / `CLAWE.Proxy` can reference the types without `CLAWE.Database`'s EF dependency. | Author a full TTR mode, validated. One themed ScottPlot pulse-train control matching STS's visual approach — the charting foundation for iterations 6–11. |
| 3 ✅ | 5–6 | **Waveform editor — data entry + schema extension.** *(Complete — v0.3.0 on `feature/waveform-editor`, merge pending the lead's click-through. The editor is a searchable list + form on a fourth Waveforms tab, with a static preview placeholder; OQ-9 measured at 63 ms for 2,000 waveforms; OQ-5 resolved → OQ-15. A hardening pass from a third-party implementation review is folded into v0.3.0: the Save is one transaction (DD-16), there is one name rule (DD-17, schema update v6), the blob checksum is checked, and NaN values are refused.)* Write the full `ClaweWaveformInstance` proto: base + PD/SP fields, **`num_pulses`** (distinct from the fixed 1024-pt FFT), the nine-modifier stack with the requirements deck's hard min/max validation, **the phase-modifier split** (`None` / `PartialPhaseEncoded(phase_pattern_duration)` / `FullPhaseEncoded`), and the **`CW` enum value** (no CW authoring UI — value only). Promote the stub `ClaweRadarModeWaveform` table to a real entity + `IWaveformRepository` (blob-graph upsert + index-in-step, same pattern as `RadarModeRepository`). Bump `ClaweRadarBlobStore.ProtoVersionTag` → `clawe-v2`. Forms only — live preview lands in iteration 7. | Author a complete waveform with several modifiers enabled, every field validated against deck ranges; persists and round-trips through the blob. |
| 4 ✅ | 7–8 | **Interface B + proxy / process-model restructure.** *(Complete — v0.4.0 on `feature/interface-b`, pending review and the v0.3.0 merge, built in one iteration. Database access: a context per operation from a writer or read-only factory, with writes through a unit of work that writes the blob once (full Save of a 2,000-waveform radar: 56 → 16 ms), a post-commit change journal (DD-18), and a write-owner row (FR-35). An internal mode ID (DD-19). The process split: `CLAWE.Host --mode maintenance` / `--mode execution`, the mutex, and an execution stub. `CLAWE.Proxy` as a user-session process (DD-21), reached by the views over local named pipes (DD-20). `CLAWE.Messaging` on RabbitMQ and an envelope-only `ClaweRadarSummary` builder. A test client and a Docker dev broker. Measured: a 1,000-radar `RequestRadars` in 37 ms. OQ-2 resolved: RabbitMQ.)* **First task: database access for multiple processes.** Replace the single long-lived `ClaweDbContext` with an `IDbContextFactory` (a context per operation or unit of work), with separate **read-only** (the proxy) and **writer** (Maintenance View, gated by the singleton mutex) factories, keeping DD-16's rollback ownership. Revisit a single aggregate radar write for the Save then. Also add a stable **internal** mode ID for blob-to-index matching; names stay interface B's handles (DD-11, DD-17). New **`CLAWE.Proxy`** always-on process. Split `CLAWE.Host` into `--mode maintenance` (singleton, sole DB writer) / `--mode execution` (`0..n`); drop the `NavigationView`. Swap the pinned `NetMQ` → `RabbitMQ.Client`. `CLAWE.Contracts` + `clawe_interface_b.proto` compiled via `CLAWE.Proto`; transport helpers in a new `CLAWE.Messaging`. `LaunchMaintenanceUI()` + single-instance (named mutex → focus-or-refuse). `RequestRadars()` → `List<ClaweRadarSummary>` via a **hand-rolled builder** that walks blobs (replaced by the rollup layer in iteration 8). Pub/sub `RadarModifiedEvent` published from one write chokepoint (a decorator over the repository / `ClaweDatabaseService` layer). Small test client (or the real `PRISM.StaticScenarioBuilder` "Add Emitter" flow if ready). See `Design/CLAWE_Interface_B.html`. | Over RabbitMQ from a test client: fetch radar summaries, remote-launch maintenance (2nd launch focuses/refused), receive modified-events on edits. Double-click still launches maintenance, and the view registers with the proxy. |
| 5 | 9–10 | **First task: domain validation outside the ViewModels.** Move the mode and waveform authoring rules, and the proto↔field conversion, out of `RadarModeEditorViewModel` / `WaveformEditorViewModel` into a WPF-free module that every write path calls: editor, repositories, and later the proxy and execution view. The VMs keep only UI affordances and map the module's errors onto fields. **Then: Waveform Calculation Engine, a new `CLAWE.Calc` library** (`net10.0`, no WPF/EF). Five stateless calculators (`CpiDuration`, `ProcessingGain`, `Eclipsing`, `RangeAmbiguity`, `VelocityAmbiguity`) + `WaveformDescriptionGenerator`, behind a `WaveformMetricsCalculator.Compute(WaveformCalcInput)` façade. `ScenarioAssumptions` record with the calc deck's documented defaults (end range 150 km, target range 50 km for PG, FPGA clock 4 ns, MaxV 2500 mph, default range resolution). xUnit `[Theory]`/`[InlineData]` — **one row per deck worked example**. Dev-only debug panel. *(Unchanged from Draft v4. The calc engine now feeds the simulated radar in iteration 6, as well as the summary screen.)* | Every worked example in `CLAWE Waveform Calculations.pptx` is reproduced by a passing unit test; a debug screen shows all computed metrics for any authored waveform. |
| 6 | 11–12 | **Simulated radar + Execution View Control tab** *(new in Draft v5; pulls the useful half of old iterations 9 and 10 forward).* A **runtime interface** (`IRadarRuntime`: activate / deactivate, load waveforms and a schedule, play a waveform, and streams of RDI frames, target reports and status) with a **`SimulatedRadar`** behind it. The simulator generates plausible data from a waveform's own parameters, using `CLAWE.Calc` for CPI, processing gain, eclipsing and ambiguities: a few moving targets, clutter, and detection SNR from the processing gain. It is deterministic (seeded) and **always labelled “Simulated”** in the UI. The **Execution View Control tab**: locked to its assigned radar mode, operating-mode switch (operator-in-the-loop; Cognitive shown but disabled), a waveform picker (a plain searchable list), Play / Stop and status, **Auto-schedule playback** (an empty schedule refuses to start, FR-52), now-playing summary, and an event log. The first window of the future graph container: the **target table**. A **“Run this mode” button** in the editor launches an Execution View for the open mode (a demo launcher; the real launch path is HOCA's, in iteration 11). Resolves OQ-16 for the demo by keeping waveform edits out of the Execution View for now (select only). *Mockup: `m06_control_tab`.* | Open a mode in the editor, click Run, pick a waveform, press Play, and watch simulated targets appear in the table; switch waveforms live; run an Auto schedule; a second Execution View launches fine (`0..n`). |
| 7 | 13–14 | **Graph-window container + 2D RDI scope — the buyer-demo milestone** *(old iterations 10 and 11, minus the target table, which moved to 6).* Dockable / resizable / removable graph-window container per the requirements deck (built against the RTSA-window pattern if located by week 13; otherwise a placeholder custom container, swapped later without changing outward behaviour). **2D RDI scope** fed by the simulator: compressed range-Doppler heatmap, axes, colour scale, target markers, integration and PG readout. A 3D RDI scope placeholder window. **Gated by OQ-13**: the heatmap and any later pulse-train drawing must not paint every pulse, and the lead expects review-and-redo cycles here. Packaged demo script for buyer demos. *Mockup: `m07_graph_windows`.* | **A running radar, simulated: pick a waveform, press Play, and watch the 2D RDI scope and target table update live; add, resize and remove windows.** This is the first build suitable for demos to potential buyers. |
| 8 | 15–16 | **Waveform Summary Screen + editor layout rework** *(old iteration 6).* Companion pane beside the waveform editor; `WaveformSummaryViewModel` subscribes to the editor VM's `PropertyChanged`, rebuilds `WaveformCalcInput`, recomputes (no timer, NaN / divide-by-zero guarded per `GraphsAndFieldsReview.md`). Plain-language description; CPI duration + CTD/CPD breakdown; PG + per-nonideal-effect breakdown; eclipsing % + the **PG-loss-vs-target-range ScottPlot chart**; range/velocity ambiguity zone size + count; and a **“What if…” trade-offs** list showing what a candidate change would do. **Layout rework** (the PM's feedback that the tabs under a mode are near the limit of one window): waveforms get their own workspace instead of a fourth tab under the mode. The summary and metrics are also shown in the Control tab for the playing waveform. **Visual checkpoint.** *Mockup: `m08_waveform_summary`.* | Build a waveform, watch every metric, the eclipsing chart and the trade-offs update live, themed to match STS. |
| 9 | 17–18 | **Waveform editor — live signal preview** *(old iteration 7).* Pulse-train / PRI-PW detail, a whole-CPI PRI histogram, a spread-spectrum spectrogram, and modifier-effect visualization (prepulse / postpulse shaping, pulse-compression gain) updating as fields change. Built on the OQ-13 decision made for iteration 7's scope. **Visual checkpoint.** *Mockup: `m09_live_preview`.* | Edit a waveform's modifiers and watch the signal-shape preview update live alongside the summary. |
| 10 | 19–20 | **Rollup infrastructure + Waveform browser** *(old iteration 8).* New `ClaweWaveformCalcRollup` table (scalar calc metrics + Min/Max Freq/PRI/PW + modulation-type flags), populated on every `SaveWaveformAsync`, backfilled by an additive schema-update step. `WaveformFilterPanel` generalizing `RadarFilterPanel` (range sections for Freq, PRI, PW, CPI duration, PG; enum-flag sections for modulation type and base waveform). Queries hit rollup rows, **never blob deserialization**. **Retrofit** the `ClaweRadarSummary` builder onto rollups (widening FR-40's bounds by per-waveform values); **retrofit** the radar filter overlay's Freq/PRI sections. The Control tab's waveform picker upgrades from a plain list to this browser. *Mockup: `m10_waveform_browser`.* | Browse/filter thousands of waveforms by name, parameter ranges, computed-metric ranges and modulation type; the radar overlay gains its Freq/PRI filters; the Control tab picks from the browser. |
| 11 | 21–22 | **Interface C + real HOCA wiring** *(old iteration 9's interface half, plus iteration 12's data wiring).* Swap `SimulatedRadar` for a **HOCA-backed `IRadarRuntime`**: `LaunchExecutionUI(ActiveRadarMode)` launching the Execution View through the proxy, `ActivateRadar` / `DeactivateRadar`, `LoadWaveforms` / `LoadSchedule`, and the RDI / target-report stream adapter. The simulator stays as the demo and test source. A source badge in the UI flips “Simulated” ↔ “HOCA”. **Gated by OQ-3** (what HOCA is as a deployable thing; the data-stream message), OQ-14 (`LoadWaveforms` scope); if HOCA can't be tested against by week 21, this iteration builds against a mocked HOCA and says so. Few new screens. | The Execution View launched by a (mock or real) HOCA plays a waveform and streams data through interface C; the badge shows the source. |
| 12 | 23–24 | **Cognitive mode + 3D RDI scope + polish** *(old iteration 9's Cognitive half and iteration 12).* Cognitive operating-mode UI: Learning / Speed, status, detection-quality-by-waveform and target-SNR windows; a **simulated jammer** in the simulator, so the closed-loop adaptation can be demonstrated without hardware (**proposed**; confirm with the PM). 3D RDI scope (`spectrum3d` is reference-only). `GraphsAndFieldsReview.md`-style hardening pass over all editors and preview controls. Packaging, proxy autostart/installer. `1.0.0` readiness pass. *Mockup: `m12_cognitive`.* | Full demo exe: author a radar end to end with live previews and summary, browse waveforms, connect from a test STS client, run an Execution View in operator or cognitive mode against a simulated jammer or real HOCA, no known validation gaps. |

**Compression levers if ~24 weeks is not acceptable:** merge iterations 8 + 9 (summary + preview)
→ 11 iterations; or defer the waveform browser (10) to a post-iteration-12 addition (interface B
then ships with only the hand-rolled `ClaweRadarSummary` builder, replaced later). Neither is
recommended over just accepting the extra runway, per the same "don't crunch the visual/high-scrutiny
work" reasoning behind Draft v2.

**Option for the PM:** the closed-loop story (cognitive mode adapting to a simulated jammer) is the
strongest thing to show buyers. It is in iteration 12 above; it can move to follow iteration 7,
ahead of the summary screen, if that is worth more to the demos.

---

## Mid-course addition (2026-08-25): Radar search/filter overlay

**Trigger:** the lead reviewed the iteration-1 (v0.1.0) demo build, liked the visual
direction, and asked whether an "Edit Radar" search flow is planned — matching how STS's
EmitterMaker handles "Edit Emitter" (a button that opens a slide-out overlay,
`PRISM.UI/Controls/EmitterFilterPanel.xaml`, with a Search box, per-parameter filter
sections, and a results list) rather than showing the list inline the way CLAWE's Radars
page does today. **Lead's direction:** build the same overlay pattern for Radars,
filterable on multiple fields (name, frequency range, PRI range, etc.), not just a plain
search box. Not on the original plan — inserted here per that explicit request, to be
started fresh in a new session using the ~1 week remaining in the current iteration.

**Scope split — important, because most of the requested filter fields don't have backing
data yet:**

- **Buildable now**, against iteration 1's existing `ClaweRadar` schema (Name,
  Description, AlternateNames): replace the Radars list's current always-visible layout
  with STS's pattern — an "Edit Radar" button in the left rail that opens a slide-out
  overlay panel. Reuse `EmitterFilterPanel.xaml`'s structure directly: a Search `TextBox`
  filtering name/description/alt-name text, the same rounded-row `ListBox` styling
  already partially copied into `CLAWE.UI/Resources/ControlStyles.xaml`
  (`PrismFilterPanelRow*Brush`, `PrismFilterDeleteButton`) — copy in
  `PrismFilterEditButton`/`PrismFilterInfoButton` from the same source dictionary
  (`PRISM.UI/Resources/EmitterFilterPanel.xaml`) too if row-level pencil/info affordances
  are wanted.
- **Blocked on data that doesn't exist yet**: a frequency-range filter, a PRI-range
  filter, or any other technical-parameter filter needs cached rollup values on
  `ClaweRadar` (or computed live from its `ClaweRadarMode`/`ClaweRadarModeWaveform`
  children) — analogous to PRISM's `Emitter` entity's `MinFrequencyHz`/`MaxFrequencyHz`/
  `MinPriNs`/`MaxPriNs`/etc. columns, which are populated from nested mode/waveform data.
  None of that exists on `ClaweRadar` yet — it depends on iteration 2's Mode constraint
  envelope (CF constraint range) for frequency, and iteration 3's Waveform PRI/PW fields
  for PRI. **This is not a blocker for starting the overlay work** — it's a scope
  boundary the next session needs going in, so it doesn't discover partway through that
  "frequency range" has nothing to filter yet.

**Recommended approach for the new session:**
1. Build the overlay **shell + text search** first. Swapping the inline list for an
   Edit-Radar-button-triggered overlay is a UI restructure of iteration 1's *existing*
   Radar CRUD, not new iteration-2 data-model work — it can proceed independently and
   immediately, without waiting on the Mode editor.
2. Design the overlay's filter-section layout to be **extensible from day one**. Mirror
   `EmitterFilterPanel.xaml`'s pattern of independently-visible per-parameter `Expander`
   sections (its `Options.Frequency`/`Options.Pri`/etc. flags driving a
   `SectionVisibilityConverter`) so a Frequency section and a PRI section can be dropped
   into the *same* overlay later without rebuilding it.
3. Add the frequency-range filter once iteration 2 lands the Mode constraint envelope
   (and a rollup-column decision is made); add the PRI-range filter once iteration 3
   lands the Waveform PRI fields. Both should land as small additions to the same
   overlay, not a second redesign.

**Reference to build against:**
`SPARTA Test System/PRISM/PRISM.UI/Controls/EmitterFilterPanel.xaml` (+ `.xaml.cs`) and
its resource dictionary `PRISM.UI/Resources/EmitterFilterPanel.xaml` — the Search box,
`Options`-driven per-section visibility, `ListBox` row styling, and Clear/Done footer are
all directly reusable patterns already explored once this session (see the per-row
delete-button copy already in `CLAWE.UI`).

This doesn't renumber or change the scope of the later iterations — it's new near-term
work using this iteration's remaining time, not a schedule compression elsewhere.

> **Update (Draft v4, 2026-09-08):** the overlay shell + text search shipped in v0.1.1.
> Its Freq/PRI filter sections are now folded into **iteration 10** (rollup infrastructure
> + Waveform browser), where the `ClaweWaveformCalcRollup` layer finally gives them
> backing data, and where the same `FilterSection<T>` machinery is built for the waveform
> browser anyway.

---

## What would still shift this plan

The open questions themselves are in the canonical register (`DESIGN.md` §10, `OQ-*`); this section
is about their *schedule* impact.

- **HOCA (OQ-3)** — *partly resolved.* Interface C's **control** messages are now specified
  (`LaunchExecutionUI(ActiveRadarMode)`, `ActivateRadar`, `DeactivateRadar`,
  `LoadWaveforms`, `LoadSchedule` — `STS SW Interface Descriptions.pptx` slide 8), and
  `PRISM.Host/Services/HocaLiteService.cs` is a working reference for the STS↔HOCA side.
  Still open: what HOCA actually is as a deployable, and the **RDI / target-report
  data-stream** direction (the slide-5 RTSA streams are the STS↔HOCA analog). Since Draft v5 this no longer
  blocks the demo: iterations 6–7 run on the simulated radar. It affects iteration 11 (a live HOCA to
  test against may not exist; the `ActiveRadarMode` payload is known) and the RDI data source.
  Unresolved → iteration 11 proceeds against a mocked HOCA, flagged in the demo changelog.
- **RabbitMQ broker (OQ-1; OQ-2 resolved)** — RabbitMQ it is, per the deck (resolved in
  iteration 4). Development runs a Docker broker, so the build isn't blocked. Who runs the broker
  in integration and deployment is still open, and every interface-B demo needs one on the
  reviewer's machine. Iteration 12's packaging depends on the answer.
- **RTSA-window pattern (OQ-4)** — iteration 7's graph-window container is built against it;
  if not located by week 13, a placeholder custom dock container ships instead and gets
  swapped later without changing the demo's outward behavior.
- **spectrum3d role** — resolved: reference only (per the iteration review). Iteration
  12's 3D RDI scope is a genuine placeholder; any library that fits may be used.
- **Chosen charting/rendering approach** (iteration 2 spike outcome) — if STS's actual
  approach turns out to be a poor fit for high-rate streaming data (RDI scopes), that
  surfaces at the *spike*, in week 4, not mid-way through iteration 7. Worst case, a
  second look-and-feel-matched rendering approach gets adopted specifically for the
  streaming graph windows — cheap to absorb in week 4, expensive in week 13.
- **High-pulse-count preview strategy (OQ-13)** — the iteration-2 spike proved ScottPlot
  is the right *library*, not the right *approach* for a ~1,024-pulse train (can't paint
  every pulse). The lead flagged this on the v0.2.0 demo and expects it to take a few
  iterations to converge (per-pulse vs. envelope/density vs. decimated vs. PRI-stagger
  summary vs. spectrogram, likely several coordinated views). Iteration 7's 2D RDI scope
  and iteration 9's live preview both build on whatever's decided; budget review-and-redo
  cycles into those iterations rather than treating the preview as a one-shot deliverable.
- **Blob storage granularity (OQ-9)** — one protobuf blob per radar means every waveform save
  re-serializes + re-hashes the whole radar. "Hundreds to thousands of waveforms per
  mode" (the lead's browser ask) may force per-waveform blob rows. Measure in iteration
  3; revisit storage in iteration 10 if it bites.
- **Iteration 4 size** — *landed in one iteration* (it was the single largest structural change
  in the project, and could have split into 4a/4b). The plan stays at 12 iterations.
- **Execution View waveform edits (OQ-16)** — FR-50 lets the operator edit waveforms there, but
  FR-51 says the view never writes. Iteration 6 needs the answer before building the Control tab (the demo build keeps waveform edits out
  of the Execution View, so it isn't blocked).

---

## Cadence

Send the lead the demo `.exe` at the end of each 2-week block with a short changelog:
what's new, what's still stubbed/mocked, what's blocked on an open question. Iterations
**2, 7, 8, and 9** in particular are worth flagging explicitly as "this is what the visual
language will look like" checkpoints (the spike, the first running radar with the 2D RDI scope,
the waveform summary screen + eclipsing chart, and the live signal preview), since that's the area the lead cares most about
getting right early.
