# CLAWE UI — Iteration Review

> **Rendered version:** `Iteration_Review.html` (in the design-doc suite). This Markdown
> file is the editable source — regenerate the HTML after a substantive change. If the two
> disagree, this file wins.

**Current iteration:** 4 (`v0.4.0`)
**Updated:** 2026-10-01
**Status:** Iteration 4 **built on `feature/interface-b`** (branched from
`feature/waveform-editor`; `v0.3.0` is merged to `master` at `50c05c1`). Not yet
committed. The full solution builds clean, and **368 tests pass** across 7 test projects, plus 2
benchmarks, including the 4 broker tests against a live RabbitMQ 4 broker. The end-to-end demo
bar was also checked against that broker (§1).

> **This is a rolling document.** It is rewritten at the end of each iteration to review
> the most recently completed one in full (§1), keep a cumulative snapshot of what the
> app is now (§2–§4), and summarise earlier iterations in one paragraph each (§5). For
> the forward plan see [`CLAWE_UI_Iterative_Timeline.md`](CLAWE_UI_Iterative_Timeline.md);
> for the release-by-release detail see `CLAWE_UI/CHANGELOG.md`.

---

## 1. Latest iteration — Iteration 4 (weeks 7–8, `v0.4.0`)

### Scope (from the timeline's demo bar)

> "Over RabbitMQ from a test client: fetch radar summaries, remote-launch maintenance (2nd
> launch focuses/refused), receive modified-events on edits. Double-click still launches
> maintenance via the proxy."

**Built.** Each piece is covered by tests. Locally, without a broker, it was checked that:
- views register with a real proxy process;
- a second double-click focuses the first editor and exits;
- the proxy retries while the broker is down;
- a second proxy exits.

**Against a live RabbitMQ 4 broker** (the Docker dev broker, a real proxy and the test client), it
was also checked that:
- `radars` answers;
- `launch` returns `LAUNCHED`, and a second one returns `FOCUSED` (naming a missing radar);
- a create, five quick edits, a rename and a delete arrive as `CREATED`, **one** `UPDATED`,
  `RENAMED` (with the old name) and `DELETED`;
- after a broker restart the proxy reconnects by itself and answers again;
- a missing database gives an error reply, not a timeout, and no file is created.

The editor's writes came from a scratch harness using the editor's real unit of work and
proxy connection; nobody clicked through the UI. The check found one real bug: RabbitMQ 4
refuses non-durable, non-exclusive queues, so the request queue is now durable. The iteration
stayed a single iteration; it didn't split into 4a/4b.

### Open questions going in

| OQ | Outcome |
|---|---|
| **OQ-2** RabbitMQ vs ZeroMQ | **Resolved: RabbitMQ**, per the deck (user decision). STS carries only NetMQ today, so its side of interface B needs a RabbitMQ client too. |
| **OQ-1** broker ownership | Didn't block the work: development uses a Docker broker. It does block the lead's click-through, which needs a broker on their machine. |
| **OQ-10** second launch | Built as *focus*, which FR-44 already says. The cross-host case can't arise (FR-38). Proposed to the lead for closure. |
| **OQ-11** multi-host identity | Queue namespaced by source name (`clawe.ifaceB.rpc.<source>`). The STS side must agree the naming. |
| **OQ-12** large response | Measured: 1,000 radars in 37 ms (128 KiB). One reply stays. |
| **New OQ-16** | FR-50 (an Execution View edits waveforms) vs FR-51 (it never writes). Needs the lead before iteration 6; the demo build keeps waveform edits out of the Execution View. |

A review agent checked the plan against the code before implementation began. It found 15
issues, and all were folded in. The four serious ones would have lost data or broken the
build:
- a blob cache that bypassed `RadarRepository`;
- `mode_id` being wiped on every save;
- a `Page` hosted directly in a `Grid`;
- a summary builder that assumed per-waveform frequency values that don't exist.

### What was delivered

**Database access for several processes** (DD-18, the timeline's "first task"):
- **Context per operation.** No process holds one long-lived context any more. Contexts come from
  a writer factory (the Maintenance View) or a read-only one (`Mode=ReadOnly`: the proxy and
  Execution Views).
- **Unit of work for multi-step writes.** `IClaweUnitOfWork` owns its transaction (DD-16's rule
  kept). Repositories edit a working copy of the radar graph, and the unit writes each radar's
  blob **once, at commit**. The editor's full Save of a 2,000-waveform radar went from about
  56 ms to **16 ms** (median, Release).
- **Post-commit change journal.** It records one change per radar (Created / Updated / Renamed /
  Deleted, strongest wins), and goes to a sink only after the commit.
- **Write-owner row** (schema v7, FR-35, NFR-7). The editor claims it at startup and checks it
  before every commit, so a second writer fails with nothing written. A dead owner is taken
  over.
- **Minimum readable schema.** Read-only processes accept any schema from v6 on.

**Internal mode ID** (DD-19, schema v8):
- **What it is:** `mode_id` links a mode's index row to its blob entry, instead of the name.
- **Across saves:** it survives renames and edits, since the editor never sets it and the
  repository keeps it.
- **Upgrade:** v8 numbers existing modes in creation order, including drifted entries, and adds
  a unique index.

**Process split** (FR-34, FR-36, FR-37):
- **Command line:** `CLAWE.Host` takes `--mode maintenance` (the default), `--mode execution`, or
  the dev-only `--mode vizspike`.
- **Window:** the Maintenance/Operate `NavigationView` is gone. The editor page sits in a `Frame`,
  and the close guard is wired directly.
- **Startup order:** mutex → register with the proxy → database init and owner claim → window →
  focus server. The mutex is taken before anything else. An abandoned mutex is taken over; one
  held by another user counts as held.
- **Execution View stub:** read-only; it shows the locked mode's constraints through the
  interface-B summary builder.

**Local IPC** (DD-20). There are two named pipes:
- **`clawe-proxy`** — views register there, and the editor forwards committed changes.
- **`clawe-maintenance`** — the running editor answers "come forward (and open radar X)".

The editor works with no proxy running.

**`CLAWE.Proxy`** (DD-21, FR-33):
- **The process:** a headless user-session process, one per host, logging to
  `%LocalAppData%\CLAWE\logs\proxy.log`.
- **`RequestRadars`:** read-only, with an error response instead of a timeout. A damaged radar
  is skipped.
- **`LaunchMaintenanceUiCommand`:** returns `FOCUSED`, `LAUNCHED` or `REJECTED` with a reason.
- **Events:** the editor's changes are debounced into `RadarModifiedEvent`s. `UPDATED` waits for
  250 ms of quiet; `CREATED`, `RENAMED` and `DELETED` go out at once.

**`CLAWE.Messaging`** (RabbitMQ.Client 7.2.2, replacing the unused NetMQ pin):
- **Connection:** automatic and topology recovery, plus a first-connect retry with backoff.
- **Server:** request/reply on the namespaced queue; requests expire after 30 s; unreadable
  requests are dropped.
- **Events:** a fanout exchange.
- **Client:** used by the test client and the tests.

**`CLAWE.Contracts`** is no longer empty:
- the `RadarSummaryBuilder`, envelope-only (see below);
- the interface-B names and versions;
- the local pipe protocol and the mutex.

**Supporting pieces:**
- `clawe_interface_b.proto` is compiled, with a new `error` field; `clawe_local.proto` is new.
- `tools/CLAWE.TestClient` (`radars`, `launch`, `watch`) and `dev/rabbitmq/docker-compose.yml`.

**The summary is envelope-only for now.** The frequency, PRI and PW bounds come from the mode's
envelope, and widening them by per-waveform values waits for iteration 10's rollups. FR-40's
acceptance was split accordingly. (Until the lead's v0.3.0 review this note said waveforms didn't
store the values at all. That was a schema gap, closed below; the summary stays envelope-only
because the rollup layer is iteration 10's.)

**Waveform fields added after the lead's v0.3.0 review.** The lead felt some waveform options were
missing, so the editor was checked against the requirements deck (slides 9, 12, 13, 29–33) and the
calc deck. Deck slide 12 nests a value under each Fixed choice that the schema had dropped:
- center frequency (`CF_hz`), PRI (`BasePRI_s`) and PW (`BasePW_s`) are now stored, required, and
  checked against the mode's envelope (FR-64). The calc engine (iteration 5) needs all three.
- Spread BW 1 and 2 can be None, as the deck lists.
- The PW type loses its "Random" value, which the deck doesn't have.
The modifier stack and its ranges matched the deck.

**Also fixed:** maximizing on a larger external monitor stopped at the laptop screen's size,
because the window's maximum size was capped to the primary screen.

**Tests:** 250 → **368** (plus 2 benchmarks), across 7 test projects. They cover:
- the unit of work: one blob write per Save, rollback, and the journal's rules;
- read-only access, the owner row, and NFR-7's two writers in one process;
- reading a WAL file after the writer closed;
- mode IDs and the v8 upgrade from a v0.3.0-shaped file;
- launch options, radar-by-name, and the execution stub;
- summary derivation, pipe framing and the mutex;
- the coalescer, launcher outcomes, and `RequestRadars`;
- the broker round trips (skipped without a broker).

**Checked by hand before the release build:**
- The editor runs with no proxy and no broker (responsive, clean exit).
- The proxy keeps running when the broker is unreachable (it logs "retrying every 1s"), and its local
  pipe stays up, with the broker unreachable or switched off (`Broker:Enabled` false).
- The packaged build against a live RabbitMQ 4 broker: `radars` answers, `launch` opens the editor, a
  second `launch` focuses it, and only one editor runs.

### Not in this iteration

- **A human click-through** of the editor against the proxy: the event path was exercised by a
  harness, not by editing in the UI.
- **Proxy autostart / installer:** iteration 12. Start `CLAWE.Proxy.exe` by hand.
- **A working Execution View with a simulated radar:** iteration 6. **Interface C and real HOCA:** iteration 11.
- **Per-waveform widening of the summary:** iteration 10.

### Process

- **Field traceability:** every field in the requirements deck (101 rows, slides 6, 8, 9, 12, 13) is checked
  against `clawe_radar.proto`, the Data Schema and the Data Model Browser by
  `scripts/check_field_traceability.py`, which writes `CLAWE_Field_Traceability.md`. All 101 pass. The
  check found the Browser stale (it still showed v0.2.0's flat modifier enum and a sketched waveform
  subtree), so it is now generated from the proto by `scripts/regen_data_model_browser.py`, and the
  Schema gained field-level rows for the carrier-frequency, CPI, PRI and PW constraint parameters.
- **Version:** `<Version>` 0.3.0 → **0.4.0**, with a `CHANGELOG.md` `[0.4.0]` entry.
- **`RELEASING.md`:** now publishes both executables into one folder, plus the optional test
  client. It adds the 0.4.0 database-compatibility row (v7/v8 are additive) and the broker setup
  for `SETUP.txt`.
- **READMEs:** new ones for `CLAWE.Proxy` and `CLAWE.Messaging`; rewrites for `CLAWE.Host`,
  `CLAWE.Contracts`, `CLAWE.Database` and the solution.
- **Design docs:** `DESIGN.md` v1.6 (DD-18–21, OQ updates, OQ-16), `REQUIREMENTS.md` v1.6,
  `CLAWE_Interface_B.html` v0.3 (§6.3 now relays through the proxy; namespaced queue; `error`
  field).

---

## 2. What exists now (cumulative app state)

### Solution structure

Standalone C#/WPF/.NET 10 solution (`CLAWE_UI.slnx`) — **not** a PRISM plugin. Matches
STS's look/feel and DB design patterns, but is its own processes, executables, and database.

| Project | Role |
|---|---|
| `CLAWE.Host` | WPF executable for the views: `--mode maintenance` (editor) / `execution` (stub) / `vizspike` |
| `CLAWE.Proxy` | Always-on proxy: interface B, view registry, launch/focus, event relay |
| `CLAWE.UI` | Theme resources (copied from `PRISM.UI`), reusable controls and converters; `ScottPlot` + `GraphThemeHelper` |
| `CLAWE.Database` | EF Core + SQLite — context factory, unit of work, repositories, schema steps v1–v8 |
| `CLAWE.Proto` | Compiles `clawe_radar.proto`, `clawe_interface_b.proto`, `clawe_local.proto` |
| `CLAWE.Contracts` | `ClaweRadarSummary` builder, interface-B names/versions, local pipe protocol, mutex |
| `CLAWE.Messaging` | RabbitMQ transport for interface B |

Each has a matching `*.Tests` project, and there's a dev-only `tools/CLAWE.TestClient`.
`CLAWE.Calc` (iteration 5) will be the eighth production project.

### Look and feel

- **Theme:** tokens (`Tokens.Dark.xaml`, `ControlStyles.xaml`) are **copied** from `PRISM.UI`,
  not referenced. CLAWE UI shares no runtime code with PRISM.
- **Window:** WPF-UI dark Mica chrome, with the Spartan-helmet title-bar icon and app icon (the
  same asset as `PRISM.Host`). The window title is "CLAWE Controller". The editor fills the
  window; there's no navigation pane.
- **Radar pages:** `RadarListPage` / `RadarEditorView` are styled to match `PRISM.EmitterMaker`:
  - the left "RADAR BUILDER" rail;
  - the combined radar + mode editor with its mode-pill strip;
  - segmented radios and black-background parameter tables;
  - STS's blue Save button;
  - a status footer with a location breadcrumb and an "● Unsaved" mark.
- **Waveforms tab:** follows STS EmitterMaker's waveform tab (square `+` / `x` list buttons,
  resizable list | editor | preview columns).

### Database (CLAWE DB)

- **Setup:** one file per host, `%LocalAppData%\CLAWE\clawe.db`, in WAL mode. It uses
  `EnsureCreated` (no EF migrations) and versioned `ApplySchemaUpdatesAsync` steps **v1–v8**, each
  one transaction.
- **Access:**
  - a context per operation, from a writer factory (Maintenance View only) or a read-only one;
  - multi-step writes through a unit of work that writes each blob once and announces changes
    after the commit;
  - a write-owner row checked before every commit.
- **Entities:**
  - `ClaweRadar`;
  - `ClaweRadarAlternateName` (one NATO + one ELNOT);
  - thin index rows `ClaweRadarMode` (with `ModeId`) and `ClaweRadarModeWaveform`;
  - `ClaweRadarProtoBlob`, the canonical serialized `ClaweRadarInstance`;
  - `ClaweWriteOwner`.
- **Repositories:** radar, mode and waveform. They:
  - give friendly errors, and keep blob and index in step;
  - require at least one mode per radar;
  - assign waveform IDs from 1 and mode IDs as the highest + 1;
  - compare names with one rule (`ClaweNameComparer`, SQLite `NOCASE`);
  - refuse non-finite numbers.

### Application features

- **Processes:**
  - the proxy;
  - one Maintenance View per host (a second double-click brings it forward);
  - read-only Execution View stubs.
- **Interface B:**
  - `RequestRadars` returns `ClaweRadarSummary` rollups, envelope-only for now;
  - `LaunchMaintenanceUiCommand` focuses or launches the editor;
  - `RadarModifiedEvent` is debounced per radar.
- **Radar management:**
  - list, and draft-then-save create;
  - rename and edit description;
  - one NATO and one ELNOT alternate name;
  - delete with confirmation;
  - an unsaved-changes prompt before leaving a radar or closing the window;
  - `--radar NAME` (or STS's `radar_name`) opens a radar.
- **Radar mode editor:** identity, `RadarModeType` (TTR only for v1), `OperatingMode`
  (Manual / Auto with a waveform-picker schedule / Cognitive), and the full constraint
  envelope. It's validated, and allowed modifiers are locked while waveforms use them.
- **Waveform editor:** the full nine-modifier stack, PD / SP fields and deck-range validation.
  It has a searchable list, resizable columns and a preview placeholder.
- **Radar search/filter slide-out overlay** (`RadarFilterPanel`). Text search only for now:
  Frequency / PRI filters need the iteration-8 rollup.
- **Viz Spike** (`--mode vizspike`, throwaway, dev-only): remove it when iteration 9's live preview lands.

### Persistence proven

- **Relaunch:** `PersistenceAcrossRelaunchTests` writes through one context, reopens a fresh one
  on the same file, and checks that data and deletions survived.
- **Upgrades:**
  - the v4 default-mode backfill;
  - v6 on a real file;
  - v8 on a v0.3.0-shaped file with drift.
- **Save speed:** `WaveformSaveLatencyBenchmarkTests` runs the footer Save's unit of work against
  2,000 waveforms, taking 16 ms.
- **Atomicity:** fault-injection tests fail one exact SQL command in a repository write, a footer
  Save, a unit commit or a schema step, and check that nothing partial survives.
- **Multi-process:** a read-only reader sees the writer's commits, including after the writer has
  closed. The reader can't write, and a second writer can't commit.

---

## 3. Process / infrastructure

- **Versioning:** a single `<Version>` in `Directory.Build.props`, with one minor bump per 2-week
  iteration (`0.4.0` for iteration 4). **`1.0.0` is reserved for a deliberate release-readiness
  pass after iteration 12.**
- **Changelog:** `CHANGELOG.md` in Keep a Changelog format, with one entry per version.
- **Docs:**
  - per-project `README.md`s;
  - `RELEASING.md`, with repeatable self-contained publish steps for both executables and
    database-compatibility notes;
  - the design-doc suite hub at `Design/index.html`.
- **Git:** `CLAWE_UI/` is its own repo, with no remote yet. There's no auto-committing: the user
  reviews and confirms each drafted commit message first.
- **Release builds:** review zips for v0.1.0 through v0.2.3 were sent to the lead. **v0.3.0**
  (awaiting the lead's click-through) and then **v0.4.0** are next.
- **Dev broker:** `docker compose -f dev/rabbitmq/docker-compose.yml up -d`.

---

## 4. Open questions / feedback

### Feedback received

- **v0.1.x:** positive on the look; the "Edit Radar" search flow became the filter overlay.
- **v0.2.0 → v0.2.3:** three rounds of mode-editor fixes, confirmed by the lead before the merge.
- **Iteration 3 click-through:** selection, scrolling, saving and layout fixes, plus layout
  requests. All were addressed in `v0.3.0`.
- **Iteration 4:** none yet — `v0.3.0`'s review comes first.

### Still open

The open questions live in the canonical register — `DESIGN.md` §10 (`OQ-*`). The ones that bear on
the current / next iterations:

| Register ID | Question | Why it matters here |
|---|---|---|
| **OQ-1** | RabbitMQ broker ownership | Every interface-B review needs a broker on the reviewer's machine; iteration 12's packaging depends on it. |
| **OQ-3** | HOCA — a runnable instance (OQ-3a); the interface-C RDI / target stream (OQ-3b) | Gates iteration 11 running against a real HOCA vs mocks (iterations 6-7 use a simulated radar). |
| **OQ-4** | The STS "RTSA window" pattern | Iteration 7's dockable graph-window container is built against it. |
| **OQ-6** | Calc-engine formula ambiguities | Gates iteration 5 (`CLAWE.Calc`). |
| **OQ-7** | CW waveform authoring | Enum + interface-B support ship; the CW editor is deferred. |
| **OQ-9** | Blob storage granularity | 16 ms per Save now; re-run on the reference host, revisit in iteration 10. |
| **OQ-10** | Second-launch behaviour | Built as focus; needs the lead's nod to close. |
| **OQ-11** | Multi-host identity | Queue naming by source name needs STS's agreement. |
| **OQ-13** | High-pulse-count preview rendering strategy | Iterations 7 and 9 iterate on it with the lead. |
| **OQ-14** | `LoadWaveforms` scope: radar or mode | Decide before iteration 11's interface C. |
| **OQ-15** | Waveform-parameter gaps and legacy conflicts | Six fields checked `≥ 0` only; SP ranges conflict with legacy. Ask the deck author. |
| **OQ-16** | Execution View waveform edits vs. the single writer | Decide before iteration 6 (the demo build avoids it). |

### Resolved since iteration 3

- **OQ-2**, RabbitMQ vs ZeroMQ: RabbitMQ, per the deck.
- **OQ-12**, large responses: measured at 37 ms for 1,000 radars; one reply stays.

---

## 5. Earlier iterations

### Iteration 3 (weeks 5–6, `v0.3.0`) — merged to `master` at `50c05c1`

- **Waveforms:** the full `ClaweWaveformInstance` with the nine-category modifier stack
  (Phase split into Partial/Full, `num_pulses`, `CW` value only), `WaveformRepository`, and a
  searchable Waveforms tab. Deck-range validation throughout.
- **Rules settled with the lead:** a mode can't be narrowed under its waveforms (DD-14); an Auto
  mode may be saved with an empty schedule (DD-15).
- **Hardening pass** from a third-party review:
  - an all-or-nothing Save (DD-16);
  - one NOCASE name rule (DD-17, schema v6);
  - blob checksum checks;
  - NaN refusal.
- **Measured:** OQ-9 at 63 ms for 2,000 waveforms. **Resolved:** OQ-5, with no schema change
  (OQ-15 raised).
- **Result:** 251 tests.

### Iteration 2 (weeks 3–4, `v0.2.0` → `v0.2.3`) — merged to `master` at `f0d3f61`

- **Proto and storage:** the canonical proto layer (`clawe_radar.proto`) with the full mode
  constraint envelope, and `ClaweRadarProtoBlob` storage.
- **Editor:** `RadarModeRepository`, and the combined radar + mode editor in STS EmitterMaker
  style.
- **`CLAWE.Proto`:** extracted so non-EF consumers can use the types.
- **Visualization spike:** ScottPlot 5, confirmed as the charting foundation.
- **Feedback:** three rounds of lead-feedback fixes.
- **Result:** 104 tests.

### Iteration 1 (weeks 1–2, `v0.1.0` + `v0.1.1`) — merged to `master` at `5d5aa7b`

- **Solution and database:** scaffolded the standalone solution, themed to match STS, with
  `ClaweDbContext` (SQLite, WAL).
- **UI:** radar CRUD, the filter overlay, the delete dialog, and one NATO + one ELNOT name per
  radar.
- **Process:** versioning, changelog, READMEs and git set up.
- **Result:** 35 tests.

---

## 6. Next iteration

**Iteration 5 — Domain validation out of the ViewModels, then the Waveform Calculation
Engine** (see [`CLAWE_UI_Iterative_Timeline.md`](CLAWE_UI_Iterative_Timeline.md) row 5):

- **First task:** move the mode and waveform authoring rules and the proto↔field conversion out
  of `RadarModeEditorViewModel` / `WaveformEditorViewModel`, into a WPF-free module that every
  write path calls.
- **`CLAWE.Calc`:** five stateless calculators behind `WaveformMetricsCalculator.Compute`, with
  one unit test per deck worked example.
- **Gated by OQ-6** (calc-deck formula ambiguities).

**Order after iteration 5 (timeline Draft v5, running-radar demo first):** 6 simulated radar +
Execution View Control tab; 7 graph windows + 2D RDI scope (the buyer-demo milestone); 8 summary
screen; 9 live preview; 10 rollups + browser; 11 interface C + real HOCA; 12 cognitive mode + polish.
