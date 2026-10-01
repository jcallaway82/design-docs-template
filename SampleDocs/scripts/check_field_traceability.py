"""Checks every field in the requirements deck against clawe_radar.proto and the design docs,
and writes Design/CLAWE_Field_Traceability.md.

For each deck field it verifies:
  Proto   - the declaration exists (Message.field), and reports its line number;
  Schema  - CLAWE_Data_Schema.html mentions the deck name or the proto name;
  Browser - CLAWE_Data_Model_Browser.html has the same message with a field of the same name
            and the same type as the proto.

Run:  python scripts/check_field_traceability.py        (from the Design folder)
Exit code is 1 if any row fails. Not part of the CLAWE_UI repo.
"""
import importlib.util
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
DESIGN = HERE.parent
PROTO = DESIGN.parent / "CLAWE_UI" / "proto" / "clawe" / "v1" / "clawe_radar.proto"
SCHEMA = DESIGN / "CLAWE_Data_Schema.html"
BROWSER = DESIGN / "CLAWE_Data_Model_Browser.html"
OUT = DESIGN / "CLAWE_Field_Traceability.md"

spec = importlib.util.spec_from_file_location("regen", HERE / "regen_data_model_browser.py")
regen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(regen)

# (group, deck field, [(Message, field-or-None)], [schema tokens: any one is enough])
ROWS = [
    ("Radar (slide 6)", None, None, None),
    ("Name", [("ClaweRadarInstance", "name")], ["name"]),
    ("Description", [("ClaweRadarInstance", "description")], ["description"]),
    ("AlternateName[]", [("ClaweRadarInstance", "alternate_names")], ["alternatename"]),
    ("AlternateNameType {NATO, ELNOT}", [("ClaweAlternateName", "kind")], ["alternatename"]),
    ("AlternateName Name", [("ClaweAlternateName", "value")], ["elnot"]),
    ("Modes[]", [("ClaweRadarInstance", "modes")], ["modes"]),
    ("Mode (slide 8)", None, None, None),
    ("Mode Name", [("ClaweRadarModeInstance", "name")], ["radarmode"]),
    ("Mode Description", [("ClaweRadarModeInstance", "description")], ["radarmode"]),
    ("RadarModeType", [("ClaweRadarModeInstance", "radar_mode_type")], ["radarmodetype"]),
    ("OperatingMode {Manual, Auto, Cognitive}", [("ClaweRadarModeInstance", "manual"), ("ClaweRadarModeInstance", "auto"), ("ClaweRadarModeInstance", "cognitive")], ["operatingmode"]),
    ("Auto.Schedule[]", [("AutoOperatingMode", "schedule")], ["schedule"]),
    ("Schedule.WaveformID", [("WaveformScheduleEntry", "waveform_id")], ["waveformid"]),
    ("Schedule.Duration_s", [("WaveformScheduleEntry", "duration_s")], ["duration_s"]),
    ("Cognitive.OptimizationType", [("CognitiveOperatingMode", "optimization_type")], ["optimizationtype"]),
    ("CFConstraintType {Range, Discretes}", [("ConstraintEnvelope", "carrier_frequency"), ("CFConstraint", "range"), ("CFConstraint", "discretes")], ["cfconstrainttype"]),
    ("CF Range.MinFreq_hz", [("CFRange", "min_hz")], ["minfreq_hz"]),
    ("CF Range.MaxFreq_hz", [("CFRange", "max_hz")], ["maxfreq_hz"]),
    ("CF Range.Channelized", [("CFRange", "channelized")], ["channelized"]),
    ("CF Range.ChanSpacing_hz", [("CFRange", "chan_spacing_hz")], ["chanspacing_hz"]),
    ("CF Discretes.Frequency_hz[]", [("CFDiscretes", "freqs_hz")], ["frequency_hz"]),
    ("MaxDutyCycle_percent", [("ConstraintEnvelope", "max_duty_cycle_percent")], ["maxdutycycle_percent"]),
    ("CPIDurationType {Fixed, Variable}", [("ConstraintEnvelope", "cpi_duration"), ("CPIDurationConstraint", "kind")], ["cpidurationtype"]),
    ("CPI Fixed.Duration_s", [("CPIDurationConstraint", "duration_s")], ["fixed.duration_s"]),
    ("Pulsed constraints (slide 9)", None, None, None),
    ("PD.PRIType {Range, Discretes}", [("PDConstraints", "pri_kind"), ("PDConstraints", "pri")], ["pritype"]),
    ("PD PRI Range.MinPRI_s", [("PriRange", "min_s")], ["minpri_s"]),
    ("PD PRI Range.MaxPRI_s", [("PriRange", "max_s")], ["maxpri_s"]),
    ("PD PRI Discretes.PRI_s[]", [("PriDiscretes", "pri_s")], ["discretes.pri_s"]),
    ("PD.PWType {Range, DutyCycle}", [("PDConstraints", "pw_kind"), ("PDConstraints", "pw")], ["pwtype"]),
    ("PD PW Range.MinPW_s", [("PwRange", "min_s")], ["minpw_s"]),
    ("PD PW Range.MaxPW_s", [("PwRange", "max_s")], ["maxpw_s"]),
    ("PD PW DutyCycle.DutyCycle_percent", [("PwDutyCycle", "duty_cycle_percent")], ["dutycycle.dutycycle_percent"]),
    ("PD.AllowedModifiers", [("PDConstraints", "allowed_modifiers")], ["allowedmodifiers"]),
    ("  PhaseModifier", [("PDAllowedModifiers", "phase")], ["allowedmodifiers"]),
    ("  FrequencyModifier", [("PDAllowedModifiers", "frequency")], ["allowedmodifiers"]),
    ("  PulseCompressionModifier", [("PDAllowedModifiers", "pulse_compression")], ["allowedmodifiers"]),
    ("  PRIModifier", [("PDAllowedModifiers", "pri")], ["allowedmodifiers"]),
    ("  PWModifier", [("PDAllowedModifiers", "pw")], ["allowedmodifiers"]),
    ("  LeadingEdgeModifier", [("PDAllowedModifiers", "leading_edge")], ["allowedmodifiers"]),
    ("  TrailingEdgeModifier", [("PDAllowedModifiers", "trailing_edge")], ["allowedmodifiers"]),
    ("  DiscriminationModifier", [("PDAllowedModifiers", "discrimination")], ["allowedmodifiers"]),
    ("Single pulse constraints (slide 9)", None, None, None),
    ("SP.PWType {Range}", [("SPConstraints", "pw_kind"), ("SPConstraints", "pw")], ["pwtype"]),
    ("SP.AllowedModifiers", [("SPConstraints", "allowed_modifiers")], ["allowedmodifiers"]),
    ("  PhaseModifier", [("SPAllowedModifiers", "phase")], ["allowedmodifiers"]),
    ("  FrequencyModifier", [("SPAllowedModifiers", "frequency")], ["allowedmodifiers"]),
    ("  PulseCompressionModifier", [("SPAllowedModifiers", "pulse_compression")], ["allowedmodifiers"]),
    ("  AmplitudeModifier", [("SPAllowedModifiers", "amplitude")], ["allowedmodifiers"]),
    ("  LeadingEdgeModifier", [("SPAllowedModifiers", "leading_edge")], ["allowedmodifiers"]),
    ("  DiscriminationModifier", [("SPAllowedModifiers", "discrimination")], ["allowedmodifiers"]),
    ("Waveform (slides 12-13)", None, None, None),
    ("WaveformID", [("ClaweWaveformInstance", "waveform_id")], ["waveformid"]),
    ("Name", [("ClaweWaveformInstance", "name")], ["name"]),
    ("Description", [("ClaweWaveformInstance", "description")], ["description"]),
    ("RangeResolution_s", [("ClaweWaveformInstance", "range_resolution_s")], ["rangeresolution_s"]),
    ("CenterFreqType {Fixed, Random}", [("ClaweWaveformInstance", "center_freq_type")], ["centerfreqtype"]),
    ("CF_hz", [("ClaweWaveformInstance", "cf_hz")], ["cf_hz"]),
    ("ClearChan", [("ClaweWaveformInstance", "clear_chan")], ["clearchan"]),
    ("WaveformCompression {30 dB}", [("ClaweWaveformInstance", "compression"), ("WaveformCompression", "fft_size"), ("WaveformCompression", "compression_db")], ["waveformcompression"]),
    ("BaseWaveform {PD, SP}", [("ClaweWaveformInstance", "base_waveform")], ["basewaveform"]),
    ("PD.PRIType {Fixed, Random}", [("ClaweWaveformInstance", "pri_type")], ["pritype"]),
    ("PD.BasePRI_s", [("ClaweWaveformInstance", "base_pri_s")], ["basepri_s"]),
    ("PD.PWType {Fixed, DutyCycle}", [("ClaweWaveformInstance", "pw_type")], ["pwtype"]),
    ("BasePW_s", [("ClaweWaveformInstance", "base_pw_s")], ["basepw_s"]),
    ("RDIIntegration {None, 2..64}", [("ClaweWaveformInstance", "rdi_integration")], ["rdiintegration"]),
    ("PhaseModifier", [("ClaweWaveformInstance", "phase_modifier")], ["phasemodifier"]),
    ("FrequencyModifier", [("ClaweWaveformInstance", "frequency_modifier")], ["frequencymodifier"]),
    ("  ChannelSpread", [("SpreadSpectrum", "channel_spread")], ["channelspread"]),
    ("  SubchannelSpread", [("SpreadSpectrum", "subchannel_spread")], ["subchannelspread"]),
    ("  SpreadBW1", [("SpreadSpectrum", "spread_bw1_hz")], ["spreadbw1"]),
    ("  SpreadBW2", [("SpreadSpectrum", "spread_bw2_hz")], ["spreadbw1/2", "spreadbw2"]),
    ("  SidelobeDetection", [("SpreadSpectrum", "sidelobe_detection")], ["sidelobedetection"]),
    ("PulseCompressionModifier {None, PSK16, Barker13, LFM}", [("ClaweWaveformInstance", "pulse_compression_modifier"), ("PulseCompressionModifier", "psk16"), ("PulseCompressionModifier", "barker13"), ("PulseCompressionModifier", "lfm")], ["pulsecompressionmodifier"]),
    ("  LFM.LFMBandwidth_hz", [("LfmCompression", "lfm_bandwidth_hz")], ["lfmbandwidth_hz"]),
    ("PRIModifier {None, BaseAgile, RandomAgile}", [("ClaweWaveformInstance", "pri_modifier")], ["primodifier"]),
    ("  BaseAgile.DropRate_percent", [("BaseAgilePri", "drop_rate_percent")], ["droprate_percent"]),
    ("  RandomAgile.Agility_percent", [("RandomAgilePri", "agility_percent")], ["agility_percent"]),
    ("PWModifier {None, RandomAgile}", [("ClaweWaveformInstance", "pw_modifier")], ["pwmodifier"]),
    ("  RandomAgile.Agility_percent", [("RandomAgilePw", "agility_percent")], ["agility_percent"]),
    ("AmplitudeModifier {None, Chop}", [("ClaweWaveformInstance", "amplitude_modifier")], ["amplitudemodifier"]),
    ("  Chop.DutyCycle_percent", [("ChopAmplitude", "duty_cycle_percent")], ["dutycycle_percent"]),
    ("  Chop.MaxOnTime_s", [("ChopAmplitude", "max_on_time_s")], ["maxontime_s"]),
    ("  Chop.IncreaseDutyCycleBeforeTargetRange", [("ChopAmplitude", "increase_duty_cycle_before_target_range")], ["increasedutycyclebeforetargetrange"]),
    ("LeadingEdgeModifier {None, Rampup, Prepulse}", [("ClaweWaveformInstance", "leading_edge_modifier")], ["leadingedgemodifier"]),
    ("  Rampup.RampTime_s", [("Rampup", "ramp_time_s")], ["ramptime_s"]),
    ("  Prepulse.PW_s", [("Prepulse", "pw_s")], ["prepulse"]),
    ("  Prepulse.Gap_s", [("Prepulse", "gap_s")], ["gap_s"]),
    ("  Prepulse.FreqType", [("Prepulse", "freq_type")], ["freqtype"]),
    ("  Prepulse.FreqOffset_hz", [("Prepulse", "freq_offset_hz")], ["freqoffset_hz"]),
    ("  Prepulse.ApplyFreqMods", [("Prepulse", "apply_freq_mods")], ["applyfreqmods"]),
    ("TrailingEdgeModifier {None, PostPulse}", [("ClaweWaveformInstance", "trailing_edge_modifier")], ["trailingedgemodifier"]),
    ("  PostPulse.PW_s", [("Postpulse", "pw_s")], ["postpulse"]),
    ("  PostPulse.Gap_s", [("Postpulse", "gap_s")], ["gap_s"]),
    ("  PostPulse.FreqType", [("Postpulse", "freq_type")], ["freqtype"]),
    ("  PostPulse.FreqOffset_hz", [("Postpulse", "freq_offset_hz")], ["freqoffset_hz"]),
    ("  PostPulse.ApplyFreqMods", [("Postpulse", "apply_freq_mods")], ["applyfreqmods"]),
    ("DiscriminationModifier {None, LeadingEdgeTrack, WBLFM}", [("ClaweWaveformInstance", "discrimination_modifier"), ("DiscriminationModifier", "leading_edge_track"), ("DiscriminationModifier", "wblfm")], ["discriminationmodifier"]),
    ("  WBLFM.LFMBandwidth_hz", [("WblfmDiscrimination", "lfm_bandwidth_hz")], ["wblfm"]),
    ("  WBLFM.Repeat", [("WblfmDiscrimination", "repeat")], ["repeat"]),
    ("Added by us, not in the requirements deck", None, None, None),
    ("NumPulses (calc deck)", [("ClaweWaveformInstance", "num_pulses")], ["num_pulses"]),
    ("Phase pattern duration (calc deck)", [("PartialPhaseEncoded", "phase_pattern_duration_s")], ["phase_pattern_duration"]),
    ("Phase Partial / Full split (calc deck)", [("PhaseModifier", "partial"), ("PhaseModifier", "full")], ["partialphaseencoded"]),
    ("BaseWaveform CW (interface deck)", [("ClaweWaveformInstance", "base_waveform")], ["cw"]),
    ("Internal mode ID (iteration 4)", [("ClaweRadarModeInstance", "mode_id")], ["mode_id"]),
]


def proto_index():
    """{(message, field): (line, type)} for every proto field."""
    idx, stack = {}, []
    for ln, raw in enumerate(PROTO.read_text(encoding="utf-8").splitlines(), 1):
        code = raw.split("//")[0].strip()
        m = re.match(r"^(message|enum)\s+(\w+)\s*\{(.*)\}\s*$", code)
        if m:  # one-line message
            for stmt in [x.strip() for x in m.group(3).split(";") if x.strip()]:
                fm = re.match(r"^(repeated\s+)?([\w.]+)\s+(\w+)\s*=", stmt)
                if fm:
                    idx[(m.group(2), fm.group(3))] = (ln, fm.group(2))
            continue
        m = re.match(r"^(message|enum)\s+(\w+)\s*\{$", code)
        if m:
            stack.append(m.group(2))
            continue
        if re.match(r"^oneof\s+\w+\s*\{$", code):
            stack.append(stack[-1])
            continue
        if code == "}":
            stack.pop()
            continue
        fm = re.match(r"^(repeated\s+)?([\w.]+)\s+(\w+)\s*=\s*\d+\s*;", code)
        if fm and stack:
            idx[(stack[-1], fm.group(3))] = (ln, fm.group(2))
    return idx


def browser_items():
    page = BROWSER.read_text(encoding="utf-8")
    a = page.index("const ITEMS = ") + len("const ITEMS = ")
    b = page.index("\n};", a) + 2
    return regen.parse_js_obj(page[a:b])


def main():
    idx = proto_index()
    items = browser_items()
    schema = re.sub(r"<[^>]+>", " ", SCHEMA.read_text(encoding="utf-8")).lower()
    schema = re.sub(r"\s+", " ", schema)

    lines = ["# CLAWE field traceability: requirements deck to proto to design docs", "",
             "Generated by `scripts/check_field_traceability.py`. Do not edit by hand; re-run it.", "",
             "Every field in the requirements deck's data structures (slides 6, 8, 9, 12, 13) is matched to its "
             "declaration in `clawe_radar.proto` (all rows are in that file) and checked against "
             "`CLAWE_Data_Schema.html` and `CLAWE_Data_Model_Browser.html`. `DESIGN.md` and `REQUIREMENTS.md` "
             "summarise the model and defer to the Schema, so they are not checked field by field.", "",
             "Legend: ✓ present and consistent · ✗ missing or different.", "",
             "| Deck field | Proto declaration | Line | Schema | Browser |", "|---|---|---|---|---|"]
    fails, total = 0, 0
    for row in ROWS:
        if row[1] is None:
            lines.append(f"| **{row[0]}** | | | | |")
            continue
        deck, decls, tokens = row
        total += 1
        found = [(m, f, idx.get((m, f))) for m, f in decls]
        proto_ok = all(v is not None for _, _, v in found)
        names = ", ".join(f"`{m}.{f}`" for m, f, _ in found)
        nums = ", ".join(str(v[0]) for _, _, v in found if v)
        schema_ok = any(t in schema for t in tokens) or any(f.replace("_", "") in schema.replace("_", "") for _, f, _ in found)
        browser_ok = True
        for m, f, v in found:
            it = items.get(m)
            fld = next((x for x in (it or {}).get("fields", []) if x["n"] == f), None)
            if it is None or fld is None or (v and fld["t"] != v[1]):
                browser_ok = False
        ok = proto_ok and schema_ok and browser_ok
        fails += 0 if ok else 1
        lines.append(f"| {deck} | {names} | {nums} | {'✓' if schema_ok else '✗'} | {'✓' if browser_ok else '✗'} |")
    lines += ["", f"**{total} deck fields checked, {total - fails} fully consistent, {fails} not.**", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"{total} deck fields checked, {total - fails} OK, {fails} failing")
    if fails:
        for l in lines:
            if "✗" in l and l.startswith("|"):
                print(l)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
