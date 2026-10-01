# Builds CLAWE_Roadmap_Overview.html (self-contained: mockup PNGs embedded) for the PM.
import base64, pathlib
here = pathlib.Path(__file__).parent

def img(name):
    return "data:image/png;base64," + base64.b64encode((here / name).read_bytes()).decode()

shots = [
    ("m06_control_tab.png", "Iteration 6 — Simulated radar + Execution Control tab",
     "Open a mode in the editor, click Run, pick a waveform, press Play. Targets appear in the table. Everything is labelled as simulated."),
    ("m07_graph_windows.png", "Iteration 7 — Graph windows + 2D RDI scope (the buyer-demo milestone)",
     "The first build that shows a radar running: a live range-Doppler scope and target table in resizable, removable windows. A 3D scope placeholder holds its place."),
    ("m08_waveform_summary.png", "Iteration 8 — Waveform summary + editor layout rework",
     "A plain-language description, the five calculations, the eclipsing chart, and “What if…” trade-offs while you edit. Waveforms get their own workspace, so the mode's tabs are less crowded."),
    ("m09_live_preview.png", "Iteration 9 — Live signal preview",
     "Pulse detail, a PRI histogram and a spectrogram redraw as you change a field. The exact set of views is still to be decided, because 1,024 pulses can't be drawn one by one."),
    ("m10_waveform_browser.png", "Iteration 10 — Waveform browser and filters",
     "Find a waveform among thousands by name, parameter ranges, calculated metrics and modulation type."),
    ("m12_cognitive.png", "Iteration 12 — Cognitive mode (proposed panels)",
     "The radar tries waveforms against jamming and adapts. Shown with a simulated jammer, so the closed-loop story can be demonstrated without hardware."),
]

rows = [
    ("1–4 ✅", "1–8", "Radar, mode and waveform editors; connection to STS over interface B (proxy + RabbitMQ)", "Built", ""),
    ("5", "9–10", "Waveform calculation engine: CPI duration, processing gain, eclipsing, range/velocity ambiguity", "None (behind the scenes)", ""),
    ("6", "11–12", "<b>Simulated radar</b> + Execution View Control tab, Play/Stop, Auto schedule, target table, “Run this mode” button", "New", "Mockup 6"),
    ("7", "13–14", "<b>Graph windows + 2D RDI scope.</b> <b>First build you can demo to buyers.</b>", "New", "Mockup 7"),
    ("8", "15–16", "Waveform summary screen with trade-offs; waveform editor layout rework", "New / reworked", "Mockup 8"),
    ("9", "17–18", "Live signal preview in the waveform editor", "New", "Mockup 9"),
    ("10", "19–20", "Waveform browser and filters (thousands of waveforms)", "New", "Mockup 10"),
    ("11", "21–22", "Real HOCA / hardware connection (interface C); the simulator stays for demos", "Almost none (a “Simulated / HOCA” badge)", "—"),
    ("12", "23–24", "Cognitive mode (with a simulated jammer), 3D scope, hardening, installer", "New", "Mockup 12"),
]

html = ["""<!doctype html><html><head><meta charset="utf-8"><title>CLAWE UI — Proposed delivery order</title><style>
body{font-family:"Segoe UI",system-ui,sans-serif;color:#1c1c1c;max-width:1100px;margin:28px auto;padding:0 24px;line-height:1.5}
h1{font-size:26px;margin:0 0 4px}h2{font-size:18px;margin:28px 0 8px;border-bottom:1px solid #ddd;padding-bottom:4px}
.sub{color:#555;margin-bottom:18px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #d6d6d6;padding:7px 10px;text-align:left;vertical-align:top}
th{background:#f1f1f1}tr.demo td{background:#fff6dd}.key{background:#eef6ff;border:1px solid #bcd8f5;border-radius:6px;padding:12px 16px;margin:14px 0}
.shot{margin:18px 0;break-inside:avoid;page-break-inside:avoid}.shot img{width:100%;border:1px solid #bbb;border-radius:4px;display:block}.shot h3{font-size:15px;margin:0 0 4px}.shot p{margin:4px 0 0;color:#444;font-size:13px}
li{margin:4px 0}.note{color:#555;font-size:13px}
@media print{body{margin:0;max-width:none}h2{break-after:avoid}.shot{page-break-after:always}}
</style></head><body>
<h1>CLAWE UI — Proposed delivery order</h1>
<div class="sub">Draft v5 · September 30, 2026 · for review. Mockups are illustrations of what each step would add, not built screens.</div>
<div class="key"><b>What changes:</b> the first build that shows a <b>radar running</b> moves from iteration 11 (week 22) to <b>iteration 7 (week 14)</b>, eight weeks sooner.
It runs on a <b>simulated radar</b> behind an interface that real HOCA / hardware replaces later (iteration 11). Nothing is dropped. The total stays 12 iterations (about 24 weeks).
The waveform summary, live preview and browser move later, since the editor already works.</div>
<h2>Overview</h2>
<table><tr><th>Iteration</th><th>Weeks</th><th>What you get</th><th>New screens</th><th>Mockup</th></tr>"""]
for it, wk, what, scr, mk in rows:
    cls = ' class="demo"' if it == "7" else ""
    html.append(f"<tr{cls}><td>{it}</td><td>{wk}</td><td>{what}</td><td>{scr}</td><td>{mk}</td></tr>")
html.append("""</table>
<p class="note">Weeks count from the start of the project. Iterations 1–4 are finished.</p>
<h2>Before and after</h2>
<table><tr><th></th><th>Previous order</th><th>Proposed order</th></tr>
<tr><td>First running radar with a scope</td><td>Iteration 11 (week 22)</td><td><b>Iteration 7 (week 14)</b></td></tr>
<tr><td>Waveform summary screen</td><td>Iteration 6 (week 12)</td><td>Iteration 8 (week 16)</td></tr>
<tr><td>Live signal preview</td><td>Iteration 7 (week 14)</td><td>Iteration 9 (week 18)</td></tr>
<tr><td>Real HOCA / hardware</td><td>Iteration 9 and 12</td><td>Iteration 11 (second to last)</td></tr>
<tr><td>Total length</td><td>12 iterations</td><td>12 iterations</td></tr></table>
<h2>Decisions needed</h2>
<ol>
<li><b>Order.</b> Is it acceptable that the summary screen and live preview arrive after the running-radar demo?</li>
<li><b>Closed-loop story.</b> The strongest thing to show buyers may be the cognitive mode adapting to a simulated jammer (iteration 12 above). Should it move to follow iteration 7?</li>
<li><b>Simulated data.</b> The demo shows simulated targets, clutter and jamming, labelled as simulated. Is that acceptable for buyer demos, and how realistic does it need to look?</li>
<li><b>Waveform editing during a run.</b> The first demo only selects among existing waveforms. Do buyers need to edit waveforms while the radar runs?</li>
</ol>
<h2>Mockups</h2>""")
for f, t, c in shots:
    html.append(f'<div class="shot"><h3>{t}</h3><img src="{img(f)}" alt="{t}"><p>{c}</p></div>')
html.append('<p class="note">Iteration 5 (calculation engine) and iteration 11 (hardware connection) add no new screens of their own.</p></body></html>')
out = here.parent / "CLAWE_Roadmap_Overview.html"
out.write_text("\n".join(html), encoding="utf-8")
print(out, out.stat().st_size)
