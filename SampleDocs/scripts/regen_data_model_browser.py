"""Regenerates the ITEMS table in CLAWE_Data_Model_Browser.html from clawe_radar.proto.

What comes from the proto (so it cannot drift): every message and enum, every field's name,
type, cardinality, units, and every enum value.
What is kept from the existing HTML (hand-written prose): each item's plain / desc / section /
parent, and each field's description when a field of the same name already had one.
New messages get their text from the proto comments.

Run:  python scripts/regen_data_model_browser.py        (from the Design folder)
Not part of the CLAWE_UI repo; lives with the design docs.
"""
import json
import pathlib
import re

HERE = pathlib.Path(__file__).resolve().parent
DESIGN = HERE.parent
PROTO = DESIGN.parent / "CLAWE_UI" / "proto" / "clawe" / "v1" / "clawe_radar.proto"
HTML = DESIGN / "CLAWE_Data_Model_Browser.html"

SECTION_RULES = [  # first match wins; used only for items the HTML has not seen before
    (r"^(ClaweRadarInstance|AlternateNameKind|ClaweAlternateName)$", "4.1"),
    (r"^(ClaweWaveformInstance|BaseWaveform|CenterFreqType|WaveformPriType|WaveformPwType|RDIIntegration|WaveformCompression)$", "4.3"),
    (r"(Modifier$|^PartialPhaseEncoded$|^FullPhaseEncoded$|^SpreadSpectrum$|^SidelobeDetection$|Compression$|Pri$|Pw$|^ChopAmplitude$|^Rampup$|^Prepulse$|^Postpulse$|^EdgeFreqType$|Discrimination$)", "4.4"),
]
UNIT_SUFFIXES = [("_hz", "Hz"), ("_s", "s"), ("_percent", "%"), ("_db", "dB")]
MANY_REQUIRED = {("ClaweRadarInstance", "modes")}  # 1..N, enforced outside the wire format


# ───────────────────────────── proto parsing ─────────────────────────────

def parse_proto(text):
    """Returns an ordered list of dicts: {kind, name, doc, fields:[{n,t,rep,oneof,doc,num}]}."""
    out, stack, pending = [], [], []
    for raw in text.splitlines():
        s = raw.strip()
        if not s:
            pending = []
            continue
        if s.startswith("//"):
            pending.append(s[2:].strip())
            continue
        code, _, trailing = s.partition("//")
        code, trailing = code.strip(), trailing.strip()
        doc = " ".join(pending + ([trailing] if trailing else [])).strip()

        m = re.match(r"^(message|enum)\s+(\w+)\s*\{(.*)\}\s*$", code)  # one-line body
        if m:
            item = {"kind": m.group(1), "name": m.group(2), "doc": " ".join(pending).strip(), "fields": []}
            out.append(item)
            for stmt in [x.strip() for x in m.group(3).split(";") if x.strip()]:
                add_field(item, stmt + ";", "", None)
            pending = []
            continue
        m = re.match(r"^(message|enum)\s+(\w+)\s*\{$", code)
        if m:
            item = {"kind": m.group(1), "name": m.group(2), "doc": " ".join(pending).strip(), "fields": []}
            out.append(item)
            stack.append(item)
            pending = []
            continue
        m = re.match(r"^oneof\s+(\w+)\s*\{$", code)
        if m:
            stack.append({"oneof": m.group(1), "owner": stack[-1]})
            pending = []
            continue
        if code == "}":
            stack.pop()
            pending = []
            continue
        if code.startswith(("syntax", "package", "option", "import", "reserved")):
            pending = []
            continue
        if stack:
            top = stack[-1]
            owner, oneof = (top["owner"], top["oneof"]) if "oneof" in top else (top, None)
            add_field(owner, code, doc, oneof)
        pending = []
    return out


def add_field(item, stmt, doc, oneof):
    if item["kind"] == "enum":
        m = re.match(r"^(\w+)\s*=\s*(-?\d+)\s*;", stmt)
        if m:
            item["fields"].append({"n": m.group(1), "num": int(m.group(2)), "doc": doc})
        return
    m = re.match(r"^(repeated\s+)?([\w.]+)\s+(\w+)\s*=\s*(\d+)\s*;", stmt)
    if m:
        item["fields"].append({"n": m.group(3), "t": m.group(2), "rep": bool(m.group(1)),
                               "oneof": oneof, "num": int(m.group(4)), "doc": doc})


# ───────────────────────────── existing HTML ─────────────────────────────

def parse_js_obj(text):
    pos, n = 0, len(text)

    def ws():
        nonlocal pos
        while pos < n:
            if text[pos].isspace():
                pos += 1
            elif text.startswith("//", pos):
                pos = text.index("\n", pos)
            else:
                break

    def string():
        nonlocal pos
        i = pos + 1
        while text[i] != '"':
            i += 2 if text[i] == "\\" else 1
        raw, pos = text[pos:i + 1], i + 1
        return json.loads(raw)

    def value():
        nonlocal pos
        ws()
        c = text[pos]
        if c == "{":
            pos += 1
            d = {}
            while True:
                ws()
                if text[pos] == "}":
                    pos += 1
                    return d
                if text[pos] == '"':
                    k = string()
                else:
                    m = re.compile(r"[A-Za-z_$][\w$]*").match(text, pos)
                    k, pos = m.group(0), m.end()
                ws()
                pos += 1  # ':'
                d[k] = value()
                ws()
                if text[pos] == ",":
                    pos += 1
        if c == "[":
            pos += 1
            a = []
            while True:
                ws()
                if text[pos] == "]":
                    pos += 1
                    return a
                a.append(value())
                ws()
                if text[pos] == ",":
                    pos += 1
        if c == '"':
            return string()
        m = re.compile(r"null|true|false|-?\d+(\.\d+)?").match(text, pos)
        pos = m.end()
        return json.loads(m.group(0))

    return value()


def q(v):
    return json.dumps(v, ensure_ascii=False)


# Text for messages / fields the proto leaves uncommented. Used only where the page has none.
FILL = {
    "PriRange": ("A PRI band: the smallest and largest PRI the mode allows.", {"min_s": "Smallest allowed PRI (deck: MinPRI_s).", "max_s": "Largest allowed PRI (deck: MaxPRI_s)."}),
    "PriDiscretes": ("An explicit list of the PRIs the mode allows.", {"pri_s": "One allowed PRI (deck: PRI_s)."}),
    "PwRange": ("A pulse-width band: the smallest and largest PW the mode allows.", {"min_s": "Smallest allowed PW (deck: MinPW_s).", "max_s": "Largest allowed PW (deck: MaxPW_s)."}),
    "PwDutyCycle": ("A required duty cycle; the PW follows from the PRI.", {"duty_cycle_percent": "Required duty cycle (deck: DutyCycle_percent). Example: 20 % at a 10 µs PRI gives a 2 µs PW."}),
    "FrequencyModifierType": ("The frequency-modifier sub-types a mode may allow.", {}),
    "PulseCompressionModifierType": ("The pulse-compression sub-types a mode may allow.", {}),
    "PriModifierType": ("The PRI-modifier sub-types a mode may allow.", {}),
    "PwModifierType": ("The PW-modifier sub-types a mode may allow.", {}),
    "AmplitudeModifierType": ("The amplitude-modifier sub-types a mode may allow (single pulse only).", {}),
    "LeadingEdgeModifierType": ("The leading-edge sub-types a mode may allow.", {}),
    "TrailingEdgeModifierType": ("The trailing-edge sub-types a mode may allow (pulsed only).", {}),
    "DiscriminationModifierType": ("The discrimination sub-types a mode may allow.", {}),
    "PDAllowedModifiers": (None, {"phase": "Allowed phase sub-types.", "frequency": "Allowed frequency sub-types.", "pulse_compression": "Allowed pulse-compression sub-types.", "pri": "Allowed PRI-modifier sub-types.", "pw": "Allowed PW-modifier sub-types.", "leading_edge": "Allowed leading-edge sub-types.", "trailing_edge": "Allowed trailing-edge sub-types.", "discrimination": "Allowed discrimination sub-types."}),
    "SPAllowedModifiers": (None, {"phase": "Allowed phase sub-types.", "frequency": "Allowed frequency sub-types.", "pulse_compression": "Allowed pulse-compression sub-types.", "amplitude": "Allowed amplitude sub-types.", "leading_edge": "Allowed leading-edge sub-types.", "discrimination": "Allowed discrimination sub-types."}),
    "PDConstraints": (None, {"pri": "The PRI band or list. Its shape follows pri_kind.", "pw": "The PW band or duty cycle. Its shape follows pw_kind."}),
    "SPConstraints": (None, {"pw": "The single-pulse PW band."}),
    "WaveformPriType": ("How a pulsed waveform picks its PRI: fixed, or random within the mode's constraints.", {}),
    "WaveformPwType": ("How a pulsed waveform picks its PW: fixed, or from the mode's duty cycle. (RANDOM is retired.)", {}),
    "RDIIntegration": ("How many consecutive RDI maps are integrated to improve SNR.", {}),
    "PartialPhaseEncoded": ("Phase modifier that repeats a short random phase pattern.", {}),
    "FullPhaseEncoded": ("Phase modifier with a random phase for every pulse across the CPI. No parameters yet.", {}),
    "SpreadSpectrum": ("Frequency modifier that spreads the waveform across the channel and sub-channels.", {"channel_spread": "Spread across the whole channel bandwidth.", "subchannel_spread": "Spread across the whole sub-channel bandwidth.", "spread_bw2_hz": "Second optional spread bandwidth; 0 means None. Same choices as spread_bw1_hz.", "sidelobe_detection": "Which spread-spectrum sidelobe to process: None, right 1–4 or left 1–4."}),
    "Psk16Compression": ("16-bit PSK pulse compression. Fixed 12 dB gain; no parameters.", {}),
    "Barker13Compression": ("13-bit Barker-code pulse compression. Fixed 11 dB gain; no parameters.", {}),
    "LfmCompression": ("Linear-FM pulse compression across a set bandwidth.", {}),
    "BaseAgilePri": ("Base-agile PRI: a share of the pulses is dropped.", {}),
    "RandomAgilePri": ("Random-agile PRI: the PRI varies randomly about the base PRI.", {}),
    "RandomAgilePw": ("Random-agile PW: the PW varies randomly about the base PW.", {}),
    "ChopAmplitude": ("Amplitude chop: each pulse is chopped to a target duty cycle (single pulse).", {"increase_duty_cycle_before_target_range": "When true, the duty cycle before the expected target range is raised to about 90 %, then drops to the set value."}),
    "Rampup": ("Leading-edge ramp-up of each pulse.", {}),
    "Prepulse": ("A short pulse played just before each main pulse.", {"freq_type": "Stable: main frequency plus the offset. Random: a random frequency within the offset either side.", "apply_freq_mods": "Also apply the main pulse's frequency modifiers to the prepulse."}),
    "Postpulse": ("A short pulse played just after each main pulse. Same shape as Prepulse.", {"pw_s": "Postpulse width, 0.25–1 µs.", "gap_s": "Gap between the main pulse and the postpulse, 0–0.5 µs.", "freq_type": "Stable: main frequency plus the offset. Random: a random frequency within the offset either side.", "freq_offset_hz": "Offset used with freq_type. No range is given (OQ-15).", "apply_freq_mods": "Also apply the main pulse's frequency modifiers to the postpulse."}),
    "LeadingEdgeTrackDiscrimination": ("Leading-edge-track discrimination. No parameters.", {}),
    "WblfmDiscrimination": ("Wideband-LFM discrimination across the waveform.", {}),
    "ClaweWaveformInstance": (None, {"compression": "Fixed 1024-point FFT and 30 dB. The editor always writes these constants."}),
}

# Wording that went stale when the waveform subtree shipped (iteration 3). Applied if present.
STALE = [
    ('//   kind    : "message" | "enum" | "planned"  (planned = proto stub, fields from\n//             CLAWE_Data_Schema.html §4.3/§4.4 + requirements deck slides 27–32)',
     '//   kind    : "message" | "enum" | "planned"  (planned = a derived projection that is\n//             computed, never stored in the proto: section 4.5)'),
    ('// Radar / Mode / ConstraintEnvelope / operating modes / ClaweAlternateName are\n// VERBATIM from CLAWE_UI/proto/clawe/v1/clawe_radar.proto (shipped in iteration 2).\n// ClaweWaveformInstance + the nine modifiers are marked "planned" — the proto for\n// that subtree lands in iteration 3.',
     '// GENERATED from CLAWE_UI/proto/clawe/v1/clawe_radar.proto by scripts/regen_data_model_browser.py:\n// every message, enum, field name, type, cardinality and unit comes from the proto. The prose\n// (plain / desc / field descriptions) is hand-written and kept across regenerations. Do not edit\n// the field rows by hand; change the proto and re-run the script.'),
    ('<span class="kind-tag planned">planned · iteration 3</span>', '<span class="kind-tag planned">derived · not stored</span>'),
    ('<div class="note"><strong>Not yet in the proto.</strong> This subtree is a stub in <code>clawe_radar.proto</code> today; the fields below are from <code>CLAWE_Data_Schema.html</code> §4.3/§4.4 and the requirements deck (slides 27–32). The proto lands in timeline iteration 3.</div>',
     '<div class="note"><strong>Derived, not stored.</strong> This is a computed projection (design decision DD-9), so it is not part of <code>clawe_radar.proto</code>. The fields below follow <code>CLAWE_Data_Schema.html</code> §4.5.</div>'),
    ('Radar / mode / constraint-envelope items are exact to the shipped\n       proto; the <span style="color:var(--warn)">planned</span> waveform subtree is from the schema doc\n       + requirements deck pending timeline iteration 3.</p>',
     'Every message, enum and field is generated from the shipped\n       proto; the <span style="color:var(--warn)">derived</span> items in section 4.5 are computed projections that are not stored.</p>'),
    ('desc: "<strong>Proto stub in iteration 2</strong> (id / name / description / base waveform only). The full field set below is from <code>CLAWE_Data_Schema.html</code> §4.3 and the requirements deck (slides 27–32); the proto for the modifier stack and PD/SP fields lands in <strong>iteration 3</strong>.",',
     'desc: "The waveform instance as shipped in iteration 3: the base type, the fields behind the Fixed choices (center frequency, PRI, PW), and a nine-category modifier stack. Field names follow <code>clawe_radar.proto</code>; the deck\'s names are in <code>CLAWE_Data_Schema.html</code> §4.3.",'),
    ("Unique within the parent mode. (In the proto stub today.)", "Unique within the parent mode."),
    ("iteration 3's per-waveform modifier stack reuses these same enums.", "the per-waveform modifier stack reuses these same enums."),
]


# ───────────────────────────── build ─────────────────────────────

def units_for(name):
    for suffix, unit in UNIT_SUFFIXES:
        if name.endswith(suffix):
            return unit
    return "—"


def first_sentence(doc, fallback):
    doc = doc.strip()
    if not doc:
        return fallback
    return re.split(r"(?<=[.!?])\s", doc, maxsplit=1)[0]


def main():
    proto = parse_proto(PROTO.read_text(encoding="utf-8"))
    names = {p["name"] for p in proto}
    page = HTML.read_text(encoding="utf-8")
    a = page.index("const ITEMS = ") + len("const ITEMS = ")
    b = page.index("\n};", a) + 2
    old = parse_js_obj(page[a:b])

    # parent = the first message (in proto order) whose fields mention the type
    first_user = {}
    for p in proto:
        for f in p["fields"]:
            t = f.get("t")
            if t in names and t != p["name"] and t not in first_user:
                first_user[t] = p["name"]

    old_ci = {k.lower(): k for k in old}  # the old page wrote PRIModifier / PWModifier; the proto says Pri / Pw
    renamed = {}
    items = {}
    for p in proto:
        key = p["name"]
        o = old.get(key) or old.get(old_ci.get(key.lower(), ""))
        if o is not None and key not in old:
            renamed[old_ci[key.lower()]] = key
        section = next((s for rx, s in SECTION_RULES if re.search(rx, key)), "4.2")
        item = {
            "kind": "enum" if p["kind"] == "enum" else "message",
            "section": o["section"] if o else section,
            "parent": (o["parent"] if o else first_user.get(key)),
            "plain": o["plain"] if o else first_sentence(p["doc"], f"{key}."),
            "desc": (o.get("desc") if o else p["doc"]) or "",
            "fields": [],
        }
        old_fields = {f["n"]: f for f in (o or {}).get("fields", [])}
        for f in p["fields"]:
            prev = old_fields.get(f["n"])
            if p["kind"] == "enum":
                d = prev["d"] if prev else (f"= {f['num']}." + (f" {f['doc']}" if f["doc"] else ""))
                item["fields"].append({"n": f["n"], "t": "", "c": "", "u": "", "d": d})
                continue
            if (key, f["n"]) in MANY_REQUIRED:
                c = "1..N"
            elif f["rep"]:
                c = "0..N"
            elif prev and prev["c"] in ("1", "0..1"):
                c = prev["c"]
            else:
                c = "0..1"
            d = prev["d"] if prev else f["doc"]
            if f["oneof"] and not d.startswith("oneof"):
                d = f"oneof <code>{f['oneof']}</code> arm." + (f" {d}" if d else "")
            item["fields"].append({"n": f["n"], "t": f["t"], "c": c, "u": units_for(f["n"]), "d": d})
        plain, field_text = FILL.get(key, (None, {}))
        if plain and item["plain"] == key + ".":
            item["plain"] = plain
        for f in item["fields"]:
            if not f["d"] and f["n"] in field_text:
                f["d"] = field_text[f["n"]]
        items[key] = item

    for key, o in old.items():  # derived projections that are not in the proto (4.5)
        if key not in items and o["section"] == "4.5":
            items[key] = o

    lines = ["{", ""]
    for i, (key, it) in enumerate(items.items()):
        lines.append(f'  {q(key)}: {{')
        lines.append(f'    kind: {q(it["kind"])}, section: {q(it["section"])}, parent: {q(it["parent"])},')
        lines.append(f'    plain: {q(it["plain"])},')
        lines.append(f'    desc: {q(it["desc"])},')
        lines.append("    fields: [")
        for j, f in enumerate(it["fields"]):
            comma = "," if j < len(it["fields"]) - 1 else ""
            lines.append(f'      {{ n: {q(f["n"])}, t: {q(f["t"])}, c: {q(f["c"])}, u: {q(f["u"])}, d: {q(f["d"])} }}{comma}')
        lines.append("    ]")
        lines.append("  }" + ("," if i < len(items) - 1 else ""))
        lines.append("")
    lines.append("};")
    page = page[:a] + "\n".join(lines) + page[b:]
    for old_text, new_text in STALE:
        page = page.replace(old_text, new_text)

    HTML.write_text(page, encoding="utf-8", newline="\n")
    kept = sum(1 for k in items if k in old)
    print(f"{len(items)} items ({kept} kept prose, {len(items) - kept} new, "
          f"{len([k for k in old if k not in items and k not in renamed])} dropped: "
          f"{[k for k in old if k not in items and k not in renamed]}; renamed: {renamed})")


if __name__ == "__main__":
    main()
