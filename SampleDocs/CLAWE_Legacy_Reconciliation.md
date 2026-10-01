# CLAWE waveform schema ↔ legacy SPARTA reconciliation

**Status:** Resolves `DESIGN.md` OQ-5 · **Date:** 2026-09-14 · **Iteration:** 3

The approved `clawe.v1` waveform model (`proto/clawe/v1/clawe_radar.proto`,
`CLAWE_Data_Schema.html` §4.3–§4.4) was checked against the legacy SPARTA CLAWE implementation, so
the two stay recognisably the same thing and any deliberate divergence is written down. **No schema
change results.** Where the legacy app and the deck disagree, the deck (the approved model) wins,
and each disagreement worth confirming goes to the deck author as `DESIGN.md` OQ-15.

**Legacy sources read** (all under `sparta/Components/`):

- `libSPARTABase/.../SMDLObjects/CLAWE/ClaweControlSettings.cs`: `ClaweWaveformDefinition` (and
  its `...ForPD` / `...ForSP` subclasses), plus the `*_MODIFIER_ENUM` constant structs that define
  every option and sub-parameter value.
- `libSPARTASimulation/.../Components/CLAWE/ProcessingPath/ClaweWaveformController.cs`: how the
  legacy simulator actually applies each setting (used to pin down phase-coding behaviour and pulse
  count).

## 1. How the two models differ in shape

| | Legacy SPARTA | `clawe.v1` |
|---|---|---|
| Option selection | A display string per modifier (`PRIModifier = "Base PRI Agile"`) plus a typed `...Def` object | A `oneof selection` per modifier message; unset means None |
| Parameter values | **Fixed pick-lists** (e.g. drop rate ∈ {25 %, 50 %, 60 %}) | **Continuous values** checked against the deck's hard ranges (NFR-16) |
| Units | Percent stored as a fraction (`0.25`); times in seconds | Percent stored as percent (`25`); SI units (`_s`, `_hz`) |
| Base-waveform split | Separate PD and SP value lists per modifier | One message per modifier; PD-only / SP-only categories gated by `base_waveform` |

The pick-list vs. range difference is the main one. Legacy values are useful as **realistic
defaults and sanity checks**, and they fill in bounds the deck leaves open (§3).

## 2. Field-by-field correspondence

| `clawe.v1` | Legacy | Match | Notes |
|---|---|---|---|
| `WaveformCompression` (fixed 30 dB, 1,024-pt FFT) | `ProcessingGain` ∈ {27, 30, 33 dB} → `FFTSize` {512, 1,024, 2,048} (36 dB / 4,096 defined but not offered) | **Diverges (deliberately)** | The deck fixes 30 dB / 1,024 "for now". Legacy made it a per-waveform choice; if it becomes selectable again, `WaveformCompression` already has the two fields to carry it. |
| `num_pulses` | *(none)*: the PD pulse train is always `FFTSize` pulses (`ClaweWaveformController` builds the subsample pattern over `FFTSize` PRIs) | **Net-new** | Decoupling pulse count from FFT size is what the calc deck's "waveform duration < FFT" loss term needs. |
| `base_waveform` PD / SP | `ClaweWaveformDefinitionForPD` / `...ForSP` | 1 : 1 | |
| `base_waveform` CW | *(none)* | **Net-new** | Enum value only (OQ-7). |
| `range_resolution_s` | `RangeRes_s` (+ `RangeResOverride`) | 1 : 1 | |
| `center_freq_type`, `clear_chan`, `pri_type`, `pw_type`, `rdi_integration` | not found in `ClaweWaveformDefinition` | **Net-new** | Come from the requirements deck's `ClaweWaveformInstance` definition. |
| **Phase** None / Partial / Full | `PhaseModifier` ∈ {None, "Phase Encoded"} | **Same behaviour, now a choice** | One legacy option behaves differently per base waveform. **PD:** each pulse gets an independent random start phase (= **Full**). **SP:** a random per-chip PSK pattern one FFT length long, repeated to the end of the pulse (= **Partial**, pattern duration = FFT-size chips). `clawe.v1` makes Partial vs. Full selectable for both, per the deck. |
| **Frequency** Spread Spectrum | `FreqModifier` "Spread Spectrum": Chan Spread, Subchan Spread, Spread BW, Spread BW (2) ∈ {10, 20, 30, 40, 50 MHz} | 1 : 1 | Same four parameters, same five bandwidths. |
| Spread Spectrum `sidelobe_detection` | `FreqModifier` "Spread Sidelobe Detect", **a separate option** with a Sidelobe number ∈ {1…4 Left, 1…4 Right} | Same values, different placement | The deck (slides 12, 29) and `clawe.v1` use the same eight sidelobes plus None, but as a setting inside Spread Spectrum rather than a separate option. |
| **Pulse Compression** PSK16 / Barker13 / LFM | `BandwidthModifier` "BW Spread": Spread Type ∈ {PSK, BPSK}, Bandwidth ∈ {5, 8, 10, 15 MHz} | **Nearest match, not 1 : 1** | ⚠ **Naming trap:** legacy "Bandwidth Modifier" is intra-pulse phase coding that widens the pulse bandwidth. It is Pulse Compression, not the Frequency modifier, even though its definition type is `ClaweFreqModifier`. Legacy codes are *random* PSK/BPSK at a chosen bandwidth; `clawe.v1` has fixed codes (16-bit PSK, 13-bit Barker) plus LFM with a bandwidth. |
| **PRI** Base Agile `drop_rate_percent` (25–75) | "Base PRI Agile" Drop Rate ∈ {25, 50, 60 %} | 1 : 1, values in range | |
| **PRI** Random Agile `agility_percent` (0–75) | "Random PRI Agile" Agility ∈ {25, 50, 65 %} | 1 : 1, values in range | A legacy code comment caps agility at 80 %. |
| **PW** Random Agile `agility_percent` (0–50), PD only | "Random PW Agile" (PD only) Agility ∈ {25, 40, 50 %} | 1 : 1, values in range | |
| **Amplitude** Chop, SP only | "Chop" (SP only): Duty Cycle ∈ {25, 50, 75 %}, Max On Time ∈ {5, 10, 20 µs}, Increase Duty Cycle Before Target Range | 1 : 1 | `max_on_time_s` has no deck bound; legacy's 5–20 µs is a usable hint (OQ-15). |
| **Leading Edge** Rampup `ramp_time_s` (0.25–2 µs) | "Ramp-up" Ramp Time: PD ∈ {0.5, 1 µs}, SP ∈ {0.5, 1, **4** µs} | **Range conflict (SP)** | Legacy SP offers 4 µs, outside the deck's 0.25–2 µs. |
| **Leading Edge** Prepulse `pw_s` (0.25–1 µs), `gap_s` (0–0.5 µs), freq type, freq offset, apply freq mods | "Prepulse": PW PD ∈ {0.5, 1 µs}, SP ∈ {**10, 50, 100** µs}; Gap ∈ {0, 0.5 µs}; Freq Type {Stable, Random}; Freq Offset (Hz, free); Apply Freq Mods | **Range conflict (SP PW)** | Same parameters. Legacy SP prepulse widths are 10–100× the deck's 1 µs maximum. The deck range may only have been written with PD in mind (OQ-15). |
| **Trailing Edge** Postpulse, PD only | "Postpulse" (PD only), same sub-parameters as Prepulse | 1 : 1 | |
| **Discrimination** Leading Edge Track / WB LFM (`lfm_bandwidth_hz` 0–2 GHz, `repeat` 1–4) | PD ∈ {**Scintillation Detect**, Leading Edge Track, WB LFM}; SP ∈ {Leading Edge Track, WB LFM}; WB LFM Repeat ∈ {1–4} | **Legacy has one more option** | "Scintillation Detect" (PD only) isn't in the deck or `clawe.v1`. Legacy WB LFM has no bandwidth setting of its own. |

## 3. What this adds to the deck-gap list

Iteration 3 shipped six fields with a `≥ 0` check only, because the deck gives no bound or default:
`PartialPhaseEncoded.phase_pattern_duration_s`, `LfmCompression.lfm_bandwidth_hz`,
`ChopAmplitude.max_on_time_s`, Prepulse/Postpulse `freq_offset_hz`, `range_resolution_s` (the deck
gives "100–400 ns" but no default), and `num_pulses`' upper bound. What the legacy code contributes:

| Gap | Legacy evidence |
|---|---|
| `max_on_time_s` bound | 5, 10, 20 µs |
| `LfmCompression.lfm_bandwidth_hz` bound | Nearest legacy analogue (BW Spread) uses 5–15 MHz |
| `phase_pattern_duration_s` | Legacy SP pattern = FFT-size chips (an implicit, derived duration, not a setting) |
| `freq_offset_hz` | Free entry in legacy too, no bound |
| `range_resolution_s` default | Legacy `RangeRes_s` is set per waveform (with an override flag); no fixed default found |
| `num_pulses` upper bound | Legacy has no such field (pulse count = FFT size, max 4,096) |

The legacy check also turned up three things the deck should confirm:

1. **SP Rampup / SP Prepulse ranges**: legacy SP values (4 µs ramp; 10–100 µs prepulse) fall outside
   the deck's ranges.
2. **Scintillation Detect**: a legacy PD discrimination option absent from the deck. Dropped
   intentionally?
3. **Processing gain**: fixed at 30 dB for now (deck) vs. selectable in legacy. Still the intent?

(`SidelobeDetection` started out on this list as a 2-value placeholder, until a re-read found the
deck spells out its values: slide 12 lists {None, R1–R4, L1–L4}, and slide 29 describes it as the
spread-spectrum sidelobe to process. The proto and editor now carry those nine values.)

All of these are collected as **`DESIGN.md` OQ-15**. The editor keeps enforcing the deck's ranges
until they are answered.
