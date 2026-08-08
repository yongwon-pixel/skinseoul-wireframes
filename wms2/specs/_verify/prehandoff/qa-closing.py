#!/usr/bin/env python3
"""
Pre-handoff QA — wms2/specs/closing.md §8, every [WF] scenario (74 per §8.16).

Executes against the local wireframe (file://…/wms2/closing/index.html), which is
byte-identical to tag review-baseline-20260803 (verified: git diff --stat is empty).

§8.0 execution protocol implemented:
  R1  fresh page.goto() before every scenario (superset of "reload between mutating")
  R2  clone-and-strip .dot before any text comparison   -> window.__t
  R2b nested functional descendants asserted with startswith, per spec
  R3  states/modals addressed by [data-state]/[data-modal], never tab text
  R4  speech instrumented via add_init_script before the page script runs
  R5  rows addressed by first-cell text within the active section
  R6  byte-exact strings pasted from the spec verbatim (· — ✓ ⚠ ✕ ① intact)
  R6b reads/is exactly -> ==, starts with -> startswith, contains -> in,
      yields N -> querySelectorAll().length == N
  R7  voiceOn is page-global; lastState only via [data-goto]
  R8  demo limitations asserted as demo behavior (U-a, U-b, U-e, U-g, U-h, U-j …)
  R9  activation via .wf-tab click unless the scenario names another route

Output: verdict table on stdout + JSON to the session scratchpad (not the repo).
"""
import json, os, pathlib, sys
from playwright.sync_api import sync_playwright

# Legacy consoles (Windows cp949 / cp1252) otherwise abort the suite mid-run with
# UnicodeEncodeError on the first non-ASCII character, leaving a partial pass count.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover - non-reconfigurable stream
    pass


HERE = pathlib.Path(__file__).resolve().parent
URL = "file://" + str((HERE / ".." / ".." / ".." / "closing" / "index.html").resolve())
OUT_JSON = os.environ.get(
    "QA_CLOSING_OUT",
    str(pathlib.Path(__file__).with_name("qa-closing-prehandoff-results.json")))
# HANDOFF.md §4 documents `python3 qa-<screen>.py [--json out.json]` for all eight runners,
# so the flag wins over both the env var and the in-tree default.
if "--json" in sys.argv:
    OUT_JSON = sys.argv[sys.argv.index("--json") + 1]

INIT = r"""
window.__spoken = [];
window.SpeechSynthesisUtterance = function (txt) { this.text = txt; this.lang = ''; this.voice = null; };
Object.defineProperty(window, 'speechSynthesis', { configurable: true, value: {
  speak: u => window.__spoken.push({ text: u.text, lang: u.lang }),
  cancel: () => {}, getVoices: () => [] } });
window.__t = function (el) { if (el === null || el === undefined) return null;
  const c = el.cloneNode(true);
  c.querySelectorAll('.dot').forEach(d => d.remove());
  return c.textContent.replace(/\s+/g, ' ').trim(); };
window.__row = function (sectionSel, label) {
  return [...document.querySelectorAll(sectionSel + ' table.tbl tbody tr')]
    .find(r => window.__t(r.cells[0]) === label) || null; };
"""

results = []


class Sc:
    def __init__(self, page, sid, title):
        self.page, self.sid, self.title = page, sid, title
        self.fails, self.passes, self.notes = [], [], []

    def ok(self, desc, cond, expected="", actual=""):
        rec = {"assert": desc, "expected": str(expected), "actual": str(actual)}
        (self.passes if cond else self.fails).append(rec)
        return bool(cond)

    def eq(self, desc, expected, actual):
        return self.ok(desc, expected == actual, expected, actual)

    def starts(self, desc, prefix, actual):
        return self.ok(desc, (actual or "").startswith(prefix), f"startswith {prefix!r}", actual)

    def has(self, desc, needle, hay):
        return self.ok(desc, needle in (hay or ""), f"contains {needle!r}", hay)

    def note(self, txt):
        self.notes.append(txt)

    def finish(self):
        v = "FAIL" if self.fails else "PASS"
        results.append(dict(id=self.sid, title=self.title, verdict=v,
                            fails=self.fails, notes=self.notes, npass=len(self.passes)))
        print(f"{v:4}  {self.sid}")
        for f in self.fails:
            print(f"      ✗ {f['assert']}\n        expected: {f['expected']}\n        actual:   {f['actual']}")
        return v


# ── helpers ──────────────────────────────────────────────────────────────
def load(page):
    page.goto(URL)
    page.wait_for_load_state("domcontentloaded")


def state(page, sid):                              # R9 / R3
    page.click(f'.wf-tab[data-state="{sid}"]')


def ev(page, script):
    return page.evaluate(script)


def t(page, sel):
    return page.evaluate("s => window.__t(document.querySelector(s))", sel)


def texts(page, sel):
    return page.evaluate("s => [...document.querySelectorAll(s)].map(e => window.__t(e))", sel)


def count(page, sel):
    return page.evaluate("s => document.querySelectorAll(s).length", sel)


def has_class(page, sel, cls):
    return page.evaluate(
        "([s,c]) => { const e=document.querySelector(s); return !!e && e.classList.contains(c); }",
        [sel, cls])


def row_t(page, section_sel, label):
    """R5 — full row cell texts (R2-normalized) or None."""
    return page.evaluate(
        "([sec,lab]) => { const r = window.__row(sec, lab); if (!r) return null;"
        "  return [...r.cells].map(c => window.__t(c)); }", [section_sel, label])


def row_prop(page, section_sel, label, js):
    return page.evaluate(
        "([sec,lab,js]) => { const r = window.__row(sec, lab); if (!r) return null;"
        "  return (new Function('r', 'return ' + js))(r); }", [section_sel, label, js])


def spoken(page):
    return page.evaluate("() => window.__spoken")


def clear_spoken(page):
    page.evaluate("() => { window.__spoken.length = 0; }")


# ═════════════════ 8.1 QA-S0 ═════════════════
def qa_s0_01(page):
    s = Sc(page, "QA-S0-01", "page opens on the pre-start screen")
    load(page)
    s.ok("section#s0 has class on", has_class(page, "#s0", "on"), "on", "")
    for o in ["s1", "s2", "s2b", "s3", "s4", "shist"]:
        s.ok(f"section#{o} does not have class on", not has_class(page, f"#{o}", "on"), "not on", "")
    s.ok('.wf-tab[data-state="s0"] has class on', has_class(page, '.wf-tab[data-state="s0"]', "on"), "on", "")
    s.eq(".wf-tab s0 text", "0 · Before Start (manual count)", t(page, '.wf-tab[data-state="s0"]'))
    n = ev(page, "() => [...document.querySelectorAll('#s0 .pagepad div')]"
               ".filter(e => window.__t(e) === \"① Today's Outbound Target (manual count)\").length")
    s.eq("exactly one #s0 .pagepad div matches the card-heading text", 1, n)
    ti = ev(page, "() => { const e=document.getElementById('targetIn0');"
                  "return e && {ph:e.placeholder, v:e.value, sib:window.__t(e.nextElementSibling)}; }")
    s.ok("#targetIn0 exists", bool(ti), "exists", ti)
    if ti:
        s.eq("#targetIn0 placeholder", "Hand-counted qty", ti["ph"])
        s.eq("#targetIn0 value is empty", "", ti["v"])
        s.eq("followed by the literal text 'orders'", "orders", ti["sib"])
    s.eq("#startBtn0 label", "Start Closing", t(page, "#startBtn0"))
    return s.finish()


def qa_s0_02(page):
    s = Sc(page, "QA-S0-02", "(negative) Start blocked with explicit error on empty/invalid input [WF-8]")
    load(page)
    page.click("#startBtn0")
    s.ok("section#s0 still on after empty submit", has_class(page, "#s0", "on"), "on", "")
    s.ok("section#s1 not on", not has_class(page, "#s1", "on"), "not on", "")
    s.eq("no .scanbig inside the active section (#s0)", 0, count(page, "#s0 .scanbig"))
    s.eq("red toast on empty input", "✕ Enter the hand-counted parcel count first",
         t(page, "#s0 .toast.err"))
    page.fill("#targetIn0", "abc")
    page.click("#startBtn0")
    s.ok("section#s0 still on after 'abc'", has_class(page, "#s0", "on"), "on", "")
    s.eq("newest red toast after 'abc' (first .toast.err in DOM)",
         "✕ The count must be a whole number of 1 or more", t(page, "#s0 .toast.err"))
    page.fill("#targetIn0", "0")
    page.click("#startBtn0")
    s.ok("section#s0 still on after '0'", has_class(page, "#s0", "on"), "on", "")
    s.eq("newest red toast after '0'",
         "✕ The count must be a whole number of 1 or more", t(page, "#s0 .toast.err"))
    return s.finish()


def qa_s0_03(page):
    s = Sc(page, "QA-S0-03", "Start with a value enters the in-progress screen (destructive)")
    load(page)
    page.fill("#targetIn0", "84")
    page.click("#startBtn0")
    s.ok("section#s1 has class on", has_class(page, "#s1", "on"), "on", "")
    s.ok("section#s0 does not", not has_class(page, "#s0", "on"), "not on", "")
    s.ok('.wf-tab[data-state="s1"] has class on', has_class(page, '.wf-tab[data-state="s1"]', "on"), "on", "")
    return s.finish()


def qa_s0_04(page):
    s = Sc(page, "QA-S0-04", "(negative) pre-start exposes nothing but the count")
    load(page)
    for sel in ["#s0 .scanbig", "#s0 .clsstat", "#s0 .prog", "#s0 table.tbl", "#s0 .okline"]:
        s.eq(f"no {sel}", 0, count(page, sel))
    n = ev(page, "() => [...document.querySelectorAll('#s0 button')]"
               ".filter(b => (window.__t(b)||'').startsWith('Confirm Closing')).length")
    s.eq("no button starting 'Confirm Closing' in #s0", 0, n)
    return s.finish()


# ═════════════════ 8.2 QA-SCAN ═════════════════
def qa_scan_01(page):
    s = Sc(page, "QA-SCAN-01", "scan input present and correctly shaped")
    load(page); state(page, "s1")
    info = ev(page, "() => { const i=document.querySelector('#s1 .scanbig input');"
                    "return i && {ph:i.placeholder, v:i.value, dis:i.disabled}; }")
    s.ok("#s1 .scanbig input exists", bool(info), "exists", info)
    if info:
        s.eq("placeholder", "Scan the tracking barcode — outbound status is judged instantly on scan", info["ph"])
        s.eq("value", "YT2618100710108810", info["v"])
        s.eq("input not disabled", False, info["dis"])
    sib = ev(page, "() => { const b=document.querySelector('#s1 .scanbig button.btn-blue');"
                   "return b && window.__t(b); }")
    s.eq("sibling button.btn-blue labelled 'Scan'", "Scan", sib)
    return s.finish()


def qa_scan_02(page):
    s = Sc(page, "QA-SCAN-02", "(negative) no scan surface before start [E-9]")
    load(page)
    s.eq("#s0 .scanbig does not exist", 0, count(page, "#s0 .scanbig"))
    others = ev(page, "() => [...document.querySelectorAll('#s0 input')]"
                     ".filter(i => i.id !== 'targetIn0').length")
    s.eq("no input other than #targetIn0 in #s0", 0, others)
    return s.finish()


def qa_scan_13(page):
    s = Sc(page, "QA-SCAN-13", "(negative) State 4 scan input rendered enabled (documents U-b)")
    load(page); state(page, "s4")
    info = ev(page, "() => { const i=document.querySelector('#s4 .scanbig input');"
                    "return i && {v:i.value, dis:i.hasAttribute('disabled')}; }")
    s.ok("#s4 .scanbig input exists", bool(info), "exists", info)
    if info:
        s.eq("value is ''", "", info["v"])
        s.eq("does not carry disabled", False, info["dis"])
    s.note("Known demo divergence U-b: shipping behavior (disabled) is QA-CONFIRM-12 [ADMIN].")
    return s.finish()


def qa_scan_16(page):
    s = Sc(page, "QA-SCAN-16", "(negative) wireframe implements no refocus loop (demo gap)")
    load(page); state(page, "s1")
    page.click("#s1 h2")   # a non-interactive page-background area
    focused = ev(page, "() => document.activeElement === document.querySelector('#s1 .scanbig input')")
    s.eq("focus does NOT move to the scan input", False, focused)
    return s.finish()


# ═════════════════ 8.3 QA-VERDICT ═════════════════
def qa_verdict_01(page):
    s = Sc(page, "QA-VERDICT-01", "an OK row renders green with the exact pill")
    load(page); state(page, "s1")
    s.ok("row #1 has class row-ok", row_prop(page, "#s1", "#1", "r.classList.contains('row-ok')"),
         "row-ok", "")
    s.eq("Order Status cell pill (span.cs-shipped)", "Prepare Shipment",
         row_prop(page, "#s1", "#1", "window.__t(r.cells[5].querySelector('span.cs-shipped'))"))
    s.eq("Closing Verdict cell pill (span.cs-shipped)", "✓ Outbounded",
         row_prop(page, "#s1", "#1", "window.__t(r.cells[6].querySelector('span.cs-shipped'))"))
    s.eq("Notes cell reads '–'", "–", row_prop(page, "#s1", "#1", "window.__t(r.cells[8])"))
    s.eq("Worker cell reads 'Dean'", "Dean", row_prop(page, "#s1", "#1", "window.__t(r.cells[7])"))
    return s.finish()


def qa_verdict_02(page):
    s = Sc(page, "QA-VERDICT-02", "compact OK line present and byte-exact [L-S1-2]")
    load(page); state(page, "s1")
    s.eq("#s1 .okline exists", 1, count(page, "#s1 .okline"))
    s.eq(".okline b reads exactly", "✓ #5 Outbounded", t(page, "#s1 .okline b"))
    s.has("okline contains order line", "Order 413540 · Tracking YT2618100710108810 · Prepare Shipment",
          t(page, "#s1 .okline"))
    s.eq("muted right-hand text", "18:41:07 · Dean", t(page, "#s1 .okline .mut"))
    s.eq("no .bigstatus in #s1", 0, count(page, "#s1 .bigstatus"))
    return s.finish()


def qa_verdict_03(page):
    s = Sc(page, "QA-VERDICT-03", "Processing scan renders warning row and in-row action")
    load(page); state(page, "s2")
    s.ok("row #4 has class row-bad", row_prop(page, "#s2", "#4", "r.classList.contains('row-bad')"),
         "row-bad", "")
    s.eq("Order Status pill", "Processing",
         row_prop(page, "#s2", "#4", "window.__t(r.cells[5].querySelector('span.cs-processing'))"))
    s.eq("Closing Verdict pill", "⚠ Not outbounded",
         row_prop(page, "#s2", "#4", "window.__t(r.cells[6].querySelector('span.cs-processing'))"))
    btn = row_prop(page, "#s2", "#4",
                   "(b => b && {t: window.__t(b), m: b.dataset.modal})(r.cells[8].querySelector('button'))")
    s.ok("Notes contains button 'Process this order' with data-modal=m-process",
         bool(btn) and btn["t"] == "Process this order" and btn["m"] == "m-process",
         "{'t':'Process this order','m':'m-process'}", btn)
    s.eq("no .bigstatus in #s2 [WF-5]", 0, count(page, "#s2 .bigstatus"))
    return s.finish()


def qa_verdict_04(page):
    s = Sc(page, "QA-VERDICT-04", "(negative) OK rows carry no resolution button")
    load(page); state(page, "s1")
    bad = ev(page, "() => [...document.querySelectorAll('#s1 tr.row-ok')]"
                  ".filter(r => [...r.querySelectorAll('button')]"
                  ".some(b => window.__t(b) === 'Process this order')).length")
    s.eq("no tr.row-ok contains 'Process this order'", 0, bad)
    pills = ev(page, "() => [...document.querySelectorAll('#s1 tr.row-ok')]"
                    ".filter(r => r.querySelector('span.cs-processing, span.cs-dup')).length")
    s.eq("no tr.row-ok contains cs-processing or cs-dup", 0, pills)
    return s.finish()


def qa_verdict_05(page):
    s = Sc(page, "QA-VERDICT-05", "scan-list column contract [L-S1-6]")
    load(page); state(page, "s1")
    ths = texts(page, "#s1 table.tbl thead th")
    s.eq("thead yields exactly 10 cells with the specified texts",
         ["#", "Scan Time", "Tracking Barcode", "Order ID", "Items",
          "Order Status", "Closing Verdict", "Worker", "Notes", ""], ths)
    para = ev(page, "() => { const tb=document.querySelector('#s1 table.tbl');"
                    "return tb && window.__t(tb.nextElementSibling); }")
    s.eq("paragraph beneath the table",
         "Sequence (#) = cumulative from 1 after closing starts · lowest first · all rows stored in the backend (fully included in the closing report export)",
         para)
    return s.finish()


# ═════════════════ 8.4 QA-UNKNOWN ═════════════════
def qa_unknown_01(page):
    s = Sc(page, "QA-UNKNOWN-01", "unknown row renders with dashes and the red pill")
    load(page); state(page, "s2b")
    s.ok("row #7 has class row-bad", row_prop(page, "#s2b", "#7", "r.classList.contains('row-bad')"),
         "row-bad", "")
    cells = row_t(page, "#s2b", "#7")
    if s.ok("row #7 exists", bool(cells), "exists", cells):
        s.eq("Order ID reads –", "–", cells[3])
        s.eq("Items reads –", "–", cells[4])
        s.eq("Order Status reads –", "–", cells[5])
    s.eq("Closing Verdict pill span.cs-dup", "⚠ Unknown order",
         row_prop(page, "#s2b", "#7", "window.__t(r.cells[6].querySelector('span.cs-dup'))"))
    return s.finish()


def qa_unknown_02(page):
    s = Sc(page, "QA-UNKNOWN-02", "prescribed operator copy intact")
    load(page); state(page, "s2b")
    s.eq("row #7 Notes cell reads exactly",
         "Mistyped tracking no. or an order from another system — check the physical label",
         row_prop(page, "#s2b", "#7", "window.__t(r.cells[8])"))
    return s.finish()


def qa_unknown_03(page):
    s = Sc(page, "QA-UNKNOWN-03", "warnings tile names the unknown class")
    load(page); state(page, "s2b")
    s.eq("#s2b .tile.warn .lab", "Warnings (not outbounded · duplicate · unknown order)",
         t(page, "#s2b .tile.warn .lab"))
    s.eq("#s2b .tile.warn .val", "4", t(page, "#s2b .tile.warn .val"))
    s.has("#s2b .proglab contains", "unknown orders are not counted", t(page, "#s2b .proglab"))
    return s.finish()


# ═════════════════ 8.5 QA-DUP ═════════════════
def qa_dup_01(page):
    s = Sc(page, "QA-DUP-01", "duplicate row cites the collision with time and worker")
    load(page); state(page, "s3")
    s.ok("row #6 has class row-bad", row_prop(page, "#s3", "#6", "r.classList.contains('row-bad')"),
         "row-bad", "")
    s.eq("verdict pill span.cs-dup", "⚠ Duplicate scan",
         row_prop(page, "#s3", "#6", "window.__t(r.cells[6].querySelector('span.cs-dup'))"))
    s.eq("Notes b reads", "Duplicate of #2",
         row_prop(page, "#s3", "#6", "window.__t(r.cells[8].querySelector('b'))"))
    s.has("Notes followed by the text", "— first scanned 18:40:18 (Miranti)",
          row_prop(page, "#s3", "#6", "window.__t(r.cells[8])"))
    return s.finish()


def qa_dup_02(page):
    s = Sc(page, "QA-DUP-02", "State 1 duplicate row variant")
    load(page); state(page, "s1")
    s.ok("row #3 has class row-bad", row_prop(page, "#s1", "#3", "r.classList.contains('row-bad')"),
         "row-bad", "")
    s.eq("shows span.cs-dup", "⚠ Duplicate scan",
         row_prop(page, "#s1", "#3", "window.__t(r.cells[6].querySelector('span.cs-dup'))"))
    s.eq("Notes b reads", "Duplicate of #2",
         row_prop(page, "#s1", "#3", "window.__t(r.cells[8].querySelector('b'))"))
    s.has("Notes contains the text", "same tracking no. (check for combined box)",
          row_prop(page, "#s1", "#3", "window.__t(r.cells[8])"))
    s.note("Spec: this earlier phrasing is superseded by §3.7 canonical (time + worker) — demo copy asserted as-is.")
    return s.finish()


def qa_dup_03(page):
    s = Sc(page, "QA-DUP-03", "first scan of a duplicated tracking is annotated")
    load(page); state(page, "s1")
    cells = row_t(page, "#s1", "#2")
    if s.ok("row #2 exists in #s1", bool(cells), "exists", cells):
        s.eq("tracking", "YT2618100710184356", cells[2])
        s.eq("worker", "Miranti", cells[7])
        s.eq("Notes reads 'First scan'", "First scan", cells[8])
    s.ok("row #2 has class row-ok", row_prop(page, "#s1", "#2", "r.classList.contains('row-ok')"),
         "row-ok", "")
    state(page, "s3")
    s.eq("same annotation on #s3 row #2", "First scan",
         row_prop(page, "#s3", "#2", "window.__t(r.cells[8])"))
    return s.finish()


# ═════════════════ 8.6 QA-VOICE ═════════════════
def qa_voice_01(page):
    s = Sc(page, "QA-VOICE-01", "entering a warning state speaks the exact utterance")
    load(page)
    s.eq("__spoken empty on fresh load", 0, ev(page, "() => window.__spoken.length"))
    for sid in ["s2", "s2b", "s3"]:
        clear_spoken(page)
        state(page, sid)
        sp = spoken(page)
        s.ok(f"tab {sid}: exactly one utterance 'Please check this order' lang en-US",
             len(sp) == 1 and sp[0]["text"] == "Please check this order" and sp[0]["lang"] == "en-US",
             "[{'text':'Please check this order','lang':'en-US'}]", sp)
        s.eq(f"section#{sid} data-voice attribute", "Please check this order",
             ev(page, f"() => document.getElementById('{sid}').dataset.voice"))
    return s.finish()


def qa_voice_02(page):
    s = Sc(page, "QA-VOICE-02", "the toggle reflects state")
    load(page); state(page, "s1")
    clear_spoken(page)
    page.click("#voiceToggle")
    s.eq("#voiceState text becomes Off", "Off", t(page, "#voiceState"))
    s.ok("#s1 .vtrack gains class off", has_class(page, "#s1 .vtrack", "off"), "off", "")
    s.eq("__spoken gains no entry from this click", 0, ev(page, "() => window.__spoken.length"))
    return s.finish()


def qa_voice_03(page):
    s = Sc(page, "QA-VOICE-03", "(negative) voice OFF never suppresses the visual warning [E-46]")
    load(page); state(page, "s1")
    page.click("#voiceToggle")
    s.eq("precondition: #voiceState reads Off", "Off", t(page, "#voiceState"))
    before = ev(page, "() => window.__t(document.querySelector('#s3 .proglab'))")
    clear_spoken(page)
    state(page, "s3")
    s.eq("__spoken still empty", 0, ev(page, "() => window.__spoken.length"))
    s.eq("row #6 still renders span.cs-dup '⚠ Duplicate scan'", "⚠ Duplicate scan",
         row_prop(page, "#s3", "#6", "window.__t(r.cells[6].querySelector('span.cs-dup'))"))
    s.ok("row #6 still row-bad", row_prop(page, "#s3", "#6", "r.classList.contains('row-bad')"),
         "row-bad", "")
    s.eq("red .proglab copy unchanged", before, t(page, "#s3 .proglab"))
    return s.finish()


def qa_voice_04(page):
    s = Sc(page, "QA-VOICE-04", "Test voice overrides the toggle without changing it")
    load(page); state(page, "s1")
    page.click("#voiceToggle")
    s.eq("precondition: Off", "Off", t(page, "#voiceState"))
    s.eq("#voiceTest label", "🔊 Test voice", t(page, "#voiceTest"))
    clear_spoken(page)
    page.click("#voiceTest")
    sp = spoken(page)
    s.ok("exactly one utterance 'Please check this order'",
         len(sp) == 1 and sp[0]["text"] == "Please check this order",
         "[{'text':'Please check this order'}]", sp)
    s.eq("#voiceState still Off", "Off", t(page, "#voiceState"))
    s.ok(".vtrack still has class off", has_class(page, "#s1 .vtrack", "off"), "off", "")
    return s.finish()


def qa_voice_05(page):
    s = Sc(page, "QA-VOICE-05", "turning the toggle ON plays one confirmation utterance")
    load(page); state(page, "s1")
    page.click("#voiceToggle")
    s.eq("precondition: Off", "Off", t(page, "#voiceState"))
    clear_spoken(page)
    page.click("#voiceToggle")
    s.eq("#voiceState becomes On", "On", t(page, "#voiceState"))
    s.ok(".vtrack loses class off", not has_class(page, "#s1 .vtrack", "off"), "no off", "")
    s.eq("exactly one utterance", 1, ev(page, "() => window.__spoken.length"))
    return s.finish()


def qa_voice_08(page):
    s = Sc(page, "QA-VOICE-08", "the replay control exists in every state")
    load(page)
    s.eq("#s1 #voiceTest labelled", "🔊 Test voice", t(page, "#s1 #voiceTest"))
    for sid in ["s2", "s2b", "s3"]:
        s.eq(f"#{sid} .sim-voice labelled", "🔊 Play again", t(page, f"#{sid} .sim-voice"))
    s.eq("#s4 .sim-voice labelled", "🔊 Test voice", t(page, "#s4 .sim-voice"))
    s.note("Label split is demo copy (U-h); canonical admin label is '🔊 Test voice' everywhere.")
    return s.finish()


# ═════════════════ 8.7 QA-COUNT ═════════════════
def qa_count_01(page):
    s = Sc(page, "QA-COUNT-01", "State 1 tiles render the demo values (documents U-a)")
    load(page); state(page, "s1")
    s.eq("four #s1 .tile .val in order", ["84", "3", "2", "79"], texts(page, "#s1 .tile .val"))
    s.eq("four #s1 .tile .lab in order",
         ["Today's outbound target (manual input)", "OK (outbounded)",
          "Warnings (not outbounded · duplicate)", "Remaining scans"],
         texts(page, "#s1 .tile .lab"))
    s.note("79 is the known demo-data defect U-a; the §3.5 formula gives 81 (QA-COUNT-04 [ADMIN]).")
    return s.finish()


def qa_count_02(page):
    s = Sc(page, "QA-COUNT-02", "the progress bar segments")
    load(page); state(page, "s1")
    s.eq("#s1 .prog i.p-ok inline width", "3.6%",
         ev(page, "() => document.querySelector('#s1 .prog i.p-ok').style.width"))
    s.eq("#s1 .prog i.p-warn inline width", "2.4%",
         ev(page, "() => document.querySelector('#s1 .prog i.p-warn').style.width"))
    return s.finish()


def qa_count_03(page):
    s = Sc(page, "QA-COUNT-03", "the progress label states the gate rule verbatim")
    load(page); state(page, "s1")
    s.eq("#s1 .proglab reads",
         "Closing progress 3.6% — OK 3/84 (81 short of the manual count) · 2 warnings to resolve — closing confirms only at an exact OK 84/84 match with 0 warnings; over-scan is also a mismatch",
         t(page, "#s1 .proglab"))
    return s.finish()


def qa_count_09(page):
    s = Sc(page, "QA-COUNT-09", "warning-state tiles in the demo")
    load(page); state(page, "s2b")
    s.eq("#s2b tile vals", ["84", "4", "4", "80"], texts(page, "#s2b .tile .val"))
    s.eq("#s2b .prog i.p-warn width", "4.8%",
         ev(page, "() => document.querySelector('#s2b .prog i.p-warn').style.width"))
    state(page, "s3")
    s.eq("#s3 tile vals", ["84", "4", "3", "80"], texts(page, "#s3 .tile .val"))
    s.has("#s3 .proglab contains", "duplicates are not double-counted", t(page, "#s3 .proglab"))
    return s.finish()


def qa_count_10(page):
    s = Sc(page, "QA-COUNT-10", "State 2 tiles and bar")
    load(page); state(page, "s2")
    s.eq("#s2 tile vals", ["84", "4", "3", "80"], texts(page, "#s2 .tile .val"))
    s.eq("#s2 .prog i.p-ok width", "4.8%",
         ev(page, "() => document.querySelector('#s2 .prog i.p-ok').style.width"))
    s.eq("#s2 .prog i.p-warn width", "3.6%",
         ev(page, "() => document.querySelector('#s2 .prog i.p-warn').style.width"))
    s.eq("#s2 .proglab reads",
         "Closing progress 4.8% — Confirm Closing becomes available after resolving 3 warnings",
         t(page, "#s2 .proglab"))
    return s.finish()


# ═════════════════ 8.8 QA-TARGET ═════════════════
def qa_target_01(page):
    s = Sc(page, "QA-TARGET-01", "locked banner shows the target and the starter")
    load(page); state(page, "s1")
    bs = ev(page, "() => [...document.querySelectorAll('#s1 .clsbanner.info b')].map(b => window.__t(b))")
    s.ok("banner contains b '① Today's Outbound Target (manual count)'",
         "① Today's Outbound Target (manual count)" in (bs or []),
         "① Today's Outbound Target (manual count)", bs)
    s.has("banner contains text 'Closing in progress (started 18:02 · Dean)'",
          "Closing in progress (started 18:02 · Dean)", t(page, "#s1 .clsbanner.info"))
    ti = ev(page, "() => { const i=document.getElementById('targetIn1');"
                  "return i && {v:i.value, dis:i.hasAttribute('disabled')}; }")
    s.ok("#targetIn1 value 84 and disabled", bool(ti) and ti["v"] == "84" and ti["dis"],
         "{'v':'84','dis':True}", ti)
    s.eq("#targetEdit label", "↺ Edit count", t(page, "#targetEdit"))
    s.eq("#closeCancel label", "✕ Cancel Closing", t(page, "#closeCancel"))
    return s.finish()


def qa_target_02(page):
    s = Sc(page, "QA-TARGET-02", "Edit count unlocks the field (destructive)")
    load(page); state(page, "s1")
    page.click("#targetEdit")
    st = ev(page, "() => { const i=document.getElementById('targetIn1');"
                  "return {dis:i.hasAttribute('disabled'), act:document.activeElement===i,"
                  "selAll:i.selectionStart===0 && i.selectionEnd===i.value.length}; }")
    s.eq("#targetIn1 no longer disabled", False, st["dis"])
    s.eq("#targetIn1 is document.activeElement", True, st["act"])
    s.eq("value selected", True, st["selAll"])
    s.eq("#targetEdit text becomes 'Save'", "Save", t(page, "#targetEdit"))
    return s.finish()


def qa_target_03(page):
    s = Sc(page, "QA-TARGET-03", "Save re-locks the field")
    load(page); state(page, "s1")
    page.click("#targetEdit")                     # unlock
    s.eq("precondition: unlocked (button 'Save')", "Save", t(page, "#targetEdit"))
    page.click("#targetEdit")                     # Save
    s.eq("#targetIn1 disabled again", True,
         ev(page, "() => document.getElementById('targetIn1').hasAttribute('disabled')"))
    s.eq("button text returns", "↺ Edit count", t(page, "#targetEdit"))
    return s.finish()


def qa_target_04(page):
    s = Sc(page, "QA-TARGET-04", "(negative) Cancel Closing takes the confirm dialog [WF-7] (destructive)")
    load(page); state(page, "s1")
    page.click("#closeCancel")
    s.ok("#m-cancel gains class open", has_class(page, "#m-cancel", "open"), "open", "")
    s.ok("section#s1 keeps class on", has_class(page, "#s1", "on"), "on", "")
    s.starts("modal header starts with", "Cancel today's closing?", t(page, "#m-cancel header"))
    s.eq("body b reads", "5 scans will be removed from this session.", t(page, "#m-cancel .body b"))
    s.eq("footer buttons", ["Keep scanning", "Yes — cancel closing"],
         texts(page, "#m-cancel .foot button"))
    page.click("#m-cancel .foot button[data-close]")     # Keep scanning
    s.ok("#m-cancel loses class open", not has_class(page, "#m-cancel", "open"), "not open", "")
    s.ok("section#s1 still on — a true no-op", has_class(page, "#s1", "on"), "on", "")
    page.click("#closeCancel")
    page.click("#cancelYes")
    s.ok("#m-cancel closes", not has_class(page, "#m-cancel", "open"), "not open", "")
    s.ok("section#s0 becomes active", has_class(page, "#s0", "on"), "on", "")
    return s.finish()


def qa_target_12(page):
    s = Sc(page, "QA-TARGET-12", "(negative) warning states render a muted target line (documents U-j)")
    load(page)
    for sid in ["s2", "s2b", "s3"]:
        state(page, sid)
        s.eq(f"#{sid} .clsbanner.info does not exist", 0, count(page, f"#{sid} .clsbanner.info"))
        muts = ev(page, f"() => [...document.querySelectorAll('#{sid} p.mut')].map(e => window.__t(e))")
        want = "① Today's outbound target (manual count): 84 orders — closing started 18:02 (Dean)"
        s.ok(f"a #{sid} p.mut reads the muted line", want in (muts or []), want, muts)
        s.eq(f"#{sid} contains no #targetEdit", 0, count(page, f"#{sid} #targetEdit"))
        s.eq(f"#{sid} contains no #closeCancel", 0, count(page, f"#{sid} #closeCancel"))
    return s.finish()


# ═════════════════ 8.9 QA-M1 ═════════════════
def qa_m1_01(page):
    s = Sc(page, "QA-M1-01", "the modal opens from the warning row")
    load(page); state(page, "s2")
    page.evaluate("() => { const r=window.__row('#s2','#4');"
                  "r.cells[8].querySelector('button[data-modal=\"m-process\"]').click(); }")
    s.ok("#m-process gains class open (from #s2 row #4)", has_class(page, "#m-process", "open"), "open", "")
    load(page); state(page, "s1")
    btn = row_prop(page, "#s1", "#4",
                   "!!r.cells[8].querySelector('button[data-modal=\"m-process\"]')")
    s.ok("same button exists inside #s1 row #4", bool(btn), "exists", btn)
    page.evaluate("() => { const r=window.__row('#s1','#4');"
                  "r.cells[8].querySelector('button[data-modal=\"m-process\"]').click(); }")
    s.ok("and opens the same modal", has_class(page, "#m-process", "open"), "open", "")
    return s.finish()


def qa_m1_02(page):
    s = Sc(page, "QA-M1-02", "the modal content is byte-exact")
    load(page)
    page.click('.wf-tab[data-modal="m-process"]')          # R9
    s.starts("header starts with", "Process Processing Order — Order 413511",
             t(page, "#m-process header"))
    s.eq("body b reads", "This order has not been outbound-processed yet.",
         t(page, "#m-process .body > b"))
    s.has("body contains the line", "Tracking YT2618100710223471 · 1 item · Status Processing",
          t(page, "#m-process .body"))
    cb = ev(page, "() => { const c=document.querySelector('#m-process input[type=checkbox]');"
                  "return c && window.__t(c.closest('label')); }")
    s.has("checkbox label contains 'Packing status of this order verified at Zero Packing'",
          "Packing status of this order verified at Zero Packing", cb)
    s.has("checkbox label contains '(step 6 of the current closing process)'",
          "(step 6 of the current closing process)", cb)
    s.eq("textarea.mtextarea placeholder",
         "Packing status and actions taken — if written, it is also recorded to the order's Comments history and the closing log",
         ev(page, "() => { const x=document.querySelector('#m-process textarea.mtextarea');"
                  "return x && x.placeholder; }"))
    note = t(page, "#m-process .note")
    s.has(".note contains status-change copy", "changes the real order status Processing → Prepare Shipment", note)
    s.has(".note contains rescan copy", "If packing is incomplete, handle it separately and rescan.", note)
    return s.finish()


def qa_m1_03(page):
    s = Sc(page, "QA-M1-03", "the footer buttons")
    load(page)
    page.click('.wf-tab[data-modal="m-process"]')
    foot = texts(page, "#m-process .foot button")
    s.ok("foot contains 'Close'", "Close" in (foot or []), "Close", foot)
    s.eq("button.btn-green labelled", "Process Outbound → resolve warning",
         t(page, "#m-process .foot button.btn-green"))
    return s.finish()


def qa_m1_04(page):
    s = Sc(page, "QA-M1-04", "(negative) dismissal changes nothing")
    for closer, desc in [
        ("[...document.querySelectorAll('#m-process .foot button')].find(b => window.__t(b)==='Close').click()", "Close button"),
        ("document.querySelector('#m-process header button.x').click()", "header ✕"),
        ("document.getElementById('m-process').click()", "overlay click"),
    ]:
        load(page); state(page, "s2")
        page.evaluate("() => { const r=window.__row('#s2','#4');"
                      "r.cells[8].querySelector('button[data-modal=\"m-process\"]').click(); }")
        s.ok(f"[{desc}] modal open before dismissal", has_class(page, "#m-process", "open"), "open", "")
        page.evaluate(f"() => {{ {closer}; }}")
        s.ok(f"[{desc}] #m-process loses class open", not has_class(page, "#m-process", "open"),
             "not open", "")
        s.eq(f"[{desc}] row #4 still shows '⚠ Not outbounded'", "⚠ Not outbounded",
             row_prop(page, "#s2", "#4", "window.__t(r.cells[6].querySelector('span.cs-processing'))"))
        s.ok(f"[{desc}] 'Process this order' button intact",
             row_prop(page, "#s2", "#4", "!!r.cells[8].querySelector('button[data-modal=\"m-process\"]')"),
             "exists", "")
    return s.finish()


def qa_m1_11(page):
    s = Sc(page, "QA-M1-11", "(negative) wireframe does not gate the button on the checkbox (documents the gap)")
    load(page); state(page, "s2")
    page.evaluate("() => { const r=window.__row('#s2','#4');"
                  "r.cells[8].querySelector('button[data-modal=\"m-process\"]').click(); }")
    st = ev(page, "() => { const b=document.querySelector('#m-process .foot button.btn-green');"
                  "const c=document.querySelector('#m-process input[type=checkbox]');"
                  "return {checked:c.checked, dis:b.hasAttribute('disabled'), close:b.hasAttribute('data-close')}; }")
    s.eq("checkbox unticked", False, st["checked"])
    s.eq("button NOT disabled in the demo", False, st["dis"])
    s.eq("button merely carries data-close", True, st["close"])
    page.click("#m-process .foot button.btn-green")
    s.ok("modal closes on click", not has_class(page, "#m-process", "open"), "not open", "")
    s.eq("underlying row unchanged (no transition)", "⚠ Not outbounded",
         row_prop(page, "#s2", "#4", "window.__t(r.cells[6].querySelector('span.cs-processing'))"))
    return s.finish()


# ═════════════════ 8.10 QA-DEL ═════════════════
def _open_scandel_row3(page):
    load(page); state(page, "s1")
    page.evaluate("() => { const r=window.__row('#s1','#3');"
                  "r.querySelector('button.scandel').click(); }")


def qa_del_01(page):
    s = Sc(page, "QA-DEL-01", "the modal identifies the row it will remove")
    load(page); state(page, "s1")
    firsts = ev(page, "() => [...document.querySelectorAll('#s1 table.tbl tbody tr')]"
                     ".map(r => window.__t(r.cells[0]))")
    s.eq("rows #1–#5 present", ["#1", "#2", "#3", "#4", "#5"], firsts)
    tl = row_prop(page, "#s1", "#3", "r.querySelector('button.scandel').title")
    s.eq("scandel button title", "Delete scan row", tl)
    page.evaluate("() => { const r=window.__row('#s1','#3');"
                  "r.querySelector('button.scandel').click(); }")
    s.ok("#m-scandel gains class open", has_class(page, "#m-scandel", "open"), "open", "")
    s.starts("header starts with", "Delete Scan Row", t(page, "#m-scandel header"))
    s.eq("body b reads", "Remove this scan?", t(page, "#m-scandel .body b"))
    s.eq("#scandelInfo reads exactly", "#3 · YT2618100710184356", t(page, "#scandelInfo"))
    return s.finish()


def qa_del_02(page):
    s = Sc(page, "QA-DEL-02", "(negative) 'No' is a true no-op")
    _open_scandel_row3(page)
    s.ok("precondition: modal open", has_class(page, "#m-scandel", "open"), "open", "")
    page.evaluate("() => [...document.querySelectorAll('#m-scandel .foot button')]"
                  ".find(b => window.__t(b) === 'No').click()")
    s.ok("#m-scandel loses class open", not has_class(page, "#m-scandel", "open"), "not open", "")
    firsts = ev(page, "() => [...document.querySelectorAll('#s1 table.tbl tbody tr')]"
                     ".map(r => window.__t(r.cells[0]))")
    s.eq("still 5 rows including #3", ["#1", "#2", "#3", "#4", "#5"], firsts)
    return s.finish()


def qa_del_03(page):
    s = Sc(page, "QA-DEL-03", "'Yes — remove' removes the row, preserves numbering (destructive)")
    _open_scandel_row3(page)
    s.eq("#scandelYes label", "Yes — remove", t(page, "#scandelYes"))
    page.click("#scandelYes")
    s.ok("overlay closes", not has_class(page, "#m-scandel", "open"), "not open", "")
    firsts = ev(page, "() => [...document.querySelectorAll('#s1 table.tbl tbody tr')]"
                     ".map(r => window.__t(r.cells[0]))")
    s.eq("4 rows, first cells #1,#2,#4,#5 — no renumbering [BR-17]",
         ["#1", "#2", "#4", "#5"], firsts)
    return s.finish()


def qa_del_04(page):
    s = Sc(page, "QA-DEL-04", "the retention promise is stated in the modal")
    load(page)
    s.eq("#m-scandel .note reads",
         "Deleting excludes it from the list and the closing counts — for clearing mis-scans, unknown orders, etc. Deletion history is kept in the backend.",
         t(page, "#m-scandel .note"))
    return s.finish()


def qa_del_05(page):
    s = Sc(page, "QA-DEL-05", "(negative) wireframe does not recompute tiles (demo limitation, destructive)")
    load(page); state(page, "s1")
    s.eq("precondition tiles 84/3/2/79", ["84", "3", "2", "79"], texts(page, "#s1 .tile .val"))
    page.evaluate("() => { const r=window.__row('#s1','#3');"
                  "r.querySelector('button.scandel').click(); }")
    page.click("#scandelYes")
    s.eq("tiles unchanged after deleting row #3", ["84", "3", "2", "79"],
         texts(page, "#s1 .tile .val"))
    s.eq(".prog i.p-warn still 2.4%", "2.4%",
         ev(page, "() => document.querySelector('#s1 .prog i.p-warn').style.width"))
    return s.finish()


def qa_del_10(page):
    s = Sc(page, "QA-DEL-10", "the modal is also reachable from the wf-bar tab")
    load(page)
    page.click('.wf-tab[data-modal="m-scandel"]')
    s.ok("#m-scandel gains class open", has_class(page, "#m-scandel", "open"), "open", "")
    s.eq("#scandelInfo retains its default text", "#7 · YT2618100719984412", t(page, "#scandelInfo"))
    return s.finish()


# ═════════════════ 8.11 QA-CONFIRM ═════════════════
def qa_confirm_01(page):
    s = Sc(page, "QA-CONFIRM-01", "the disabled button carries the blockers")
    load(page); state(page, "s1")
    bs = ev(page, "() => [...document.querySelectorAll('#s1 .clsbanner.done b')].map(b => window.__t(b))")
    s.ok("banner contains b 'Confirm Closing'", "Confirm Closing" in (bs or []), "Confirm Closing", bs)
    s.eq("button text exactly", "Confirm Closing (79 remaining · 2 warnings)",
         t(page, "#s1 .clsbanner.done button"))
    banner = t(page, "#s1 .clsbanner.done")
    s.has("banner contains no-auto-confirm copy",
          "no auto-confirm; closing happens only when this button is pressed.", banner)
    s.has("banner contains over-scan copy",
          "an over-scan makes it a mismatch and disables the button again", banner)
    s.has("banner contains PD-71 copy",
          "the admin's Closing History replaces the retired Daily Shipping Status spreadsheet", banner)
    return s.finish()


def qa_confirm_02(page):
    s = Sc(page, "QA-CONFIRM-02", "the button renders as disabled")
    load(page); state(page, "s1")
    s.ok("button carries class btn-gray",
         has_class(page, "#s1 .clsbanner.done button", "btn-gray"), "btn-gray", "")
    return s.finish()


def qa_confirm_03(page):
    s = Sc(page, "QA-CONFIRM-03", "the completion panel is the only large panel on the page")
    load(page); state(page, "s4")
    s.ok("#s4 .bigstatus has class bs-ok", has_class(page, "#s4 .bigstatus", "bs-ok"), "bs-ok", "")
    s.eq(".big text", "Today's closing complete — all orders verified", t(page, "#s4 .bigstatus .big"))
    s.has(".bmeta contains",
          "Manual count 84 = OK scans 84, an exact match · 0 warnings · closing confirmed 2026-07-13 18:52 (Yongwon)",
          t(page, "#s4 .bigstatus .bmeta"))
    bside = t(page, "#s4 .bside")
    s.has(".bside contains 'Warnings'", "Warnings", bside)
    s.has(".bside contains '0'", "0", bside)
    s.has(".bside contains 'Remaining scans 0'", "Remaining scans 0", bside)
    s.eq(".bs-warn yields zero anywhere [WF-5]", 0, count(page, ".bs-warn"))
    s.eq(".bigstatus yields exactly one", 1, count(page, ".bigstatus"))
    s.eq("…inside #s4", 1, count(page, "#s4 .bigstatus"))
    return s.finish()


def qa_confirm_04(page):
    s = Sc(page, "QA-CONFIRM-04", "the confirmation toast copy")
    load(page); state(page, "s4")
    s.has("#s4 .toast contains", "✓ Today's closing confirmed — 84/84 orders", t(page, "#s4 .toast"))
    s.eq("its small reads", "Closing record saved · replaces the retired Daily Shipping Status sheet",
         t(page, "#s4 .toast small"))
    s.ok("#s4 .toast does not carry class err",
         not has_class(page, "#s4 .toast", "err"), "no err", "")
    return s.finish()


def qa_confirm_05(page):
    s = Sc(page, "QA-CONFIRM-05", "the Closing Report banner, and no print affordance [BR-24]")
    load(page); state(page, "s4")
    bs = ev(page, "() => [...document.querySelectorAll('#s4 .clsbanner.done b')].map(b => window.__t(b))")
    s.ok("banner contains b 'Closing Report'", "Closing Report" in (bs or []), "Closing Report", bs)
    s.has("banner contains retirement copy",
          "replaces the manual copy/paste and formula-stripping into SS Daily Shipping Status (sheet retired 2026-08-03)",
          t(page, "#s4 .clsbanner.done"))
    s.eq("button labelled", "Download Closing Report (CSV)",
         t(page, "#s4 .clsbanner.done button"))
    s.eq("no 'Print' text anywhere in the document", False,
         ev(page, "() => document.body.textContent.includes('Print')"))
    n = ev(page, "() => [...document.querySelectorAll('button')]"
               ".filter(b => window.__t(b) === 'Print').length")
    s.eq("no button whose normalized text is 'Print'", 0, n)
    return s.finish()


def qa_confirm_06(page):
    s = Sc(page, "QA-CONFIRM-06", "the Warning Resolution Summary and the State 4 tiles")
    load(page); state(page, "s4")
    bs = ev(page, "() => [...document.querySelectorAll('#s4 .clsbanner.info b')].map(b => window.__t(b))")
    s.ok("banner contains b 'Warning Resolution Summary'",
         "Warning Resolution Summary" in (bs or []), "Warning Resolution Summary", bs)
    s.has("banner contains summary text",
          "3 warnings today — 1 Processing (413511, resolved after Outbound) · 2 duplicates (combined-box confirmed, logged in Comments).",
          t(page, "#s4 .clsbanner.info"))
    s.eq("four #s4 .tile .val", ["84", "84", "0", "0"], texts(page, "#s4 .tile .val"))
    labs = texts(page, "#s4 .tile .lab")
    s.eq("third .lab reads", "Warnings (resolved)", labs[2] if labs and len(labs) > 2 else None)
    s.eq("#s4 .prog i.p-ok width 100%", "100%",
         ev(page, "() => document.querySelector('#s4 .prog i.p-ok').style.width"))
    s.eq("no i.p-warn in #s4", 0, count(page, "#s4 .prog i.p-warn"))
    return s.finish()


def qa_confirm_15(page):
    s = Sc(page, "QA-CONFIRM-15", "(negative) State 4 exposes no session controls")
    load(page); state(page, "s4")
    s.eq("no #targetEdit in #s4", 0, count(page, "#s4 #targetEdit"))
    s.eq("no #closeCancel in #s4", 0, count(page, "#s4 #closeCancel"))
    n = ev(page, "() => [...document.querySelectorAll('#s4 .clsbanner.info b')]"
               ".filter(b => window.__t(b).includes(\"Today's Outbound Target (manual count)\")).length")
    s.eq("no .clsbanner.info with the target-banner b", 0, n)
    n2 = ev(page, "() => [...document.querySelectorAll('#s4 button')]"
                ".filter(b => (window.__t(b)||'').startsWith('Confirm Closing')).length")
    s.eq("no button starting 'Confirm Closing' in #s4", 0, n2)
    muts = ev(page, "() => [...document.querySelectorAll('#s4 p.mut')].map(e => window.__t(e))")
    want = "① Today's outbound target (manual count): 84 orders — closing started 18:02 (Dean)"
    s.ok("instead a p.mut reads the muted line", want in (muts or []), want, muts)
    return s.finish()


# ═════════════════ 8.12 QA-HIST ═════════════════
def qa_hist_01(page):
    s = Sc(page, "QA-HIST-01", "history page reachable from the closing screen")
    load(page); state(page, "s1")
    s.eq('#s1 [data-goto="shist"] label', "Closing History", t(page, '#s1 [data-goto="shist"]'))
    page.click('#s1 [data-goto="shist"]')
    s.ok("section#shist has class on", has_class(page, "#shist", "on"), "on", "")
    s.ok("section#s1 does not", not has_class(page, "#s1", "on"), "not on", "")
    for sid in ["s0", "s2", "s2b", "s3", "s4"]:
        s.eq(f"same tab exists in #{sid}", 1, count(page, f'#{sid} [data-goto="shist"]'))
    return s.finish()


def qa_hist_02(page):
    s = Sc(page, "QA-HIST-02", "the table contract")
    load(page); state(page, "shist")
    ths = texts(page, "#shist table.logtbl th")
    s.eq("header cells in order",
         ["Date", "Outbound Target (manual)", "OK Scans", "Warnings (raised→resolved)",
          "Match", "Closed By", "Confirmed At", ""], ths)
    return s.finish()


def qa_hist_03(page):
    s = Sc(page, "QA-HIST-03", "today's row and the CSV action")
    load(page); state(page, "shist")
    row = ev(page, "() => { const rows=[...document.querySelectorAll('#shist table.logtbl tr')]"
                  ".filter(r => r.querySelector('td')); const r=rows[0];"
                  "return { cells:[...r.cells].map(c => window.__t(c)),"
                  "  csv:[...r.querySelectorAll('button')].some(b => window.__t(b)==='CSV'),"
                  "  style:r.getAttribute('style'),"
                  "  bg:getComputedStyle(r).backgroundColor,"
                  "  others:rows.slice(1).map(x => ({style:x.getAttribute('style'),"
                  "                                  bg:getComputedStyle(x).backgroundColor})) }; }")
    c = row["cells"]
    s.eq("Date", "07-13 (today)", c[0])
    s.eq("Outbound Target", "84", c[1])
    s.eq("OK Scans", "84", c[2])
    s.eq("Warnings", "3→3", c[3])
    s.eq("Match", "✓ Match", c[4])
    s.eq("Closed By", "Yongwon", c[5])
    s.eq("Confirmed At", "18:52", c[6])
    s.ok("contains a button labelled CSV", row["csv"], "CSV", "")
    s.eq("inline style attribute exactly", "background:var(--green-soft)", row["style"])
    diff = all(row["bg"] != o["bg"] for o in row["others"])
    s.ok("computed background differs from every other data row", diff,
         f"≠ {row['bg']}", row["others"])
    no_inline = all(not (o["style"] and "background" in o["style"]) for o in row["others"])
    s.ok("the other four carry no inline background", no_inline, "no inline background",
         [o["style"] for o in row["others"]])
    return s.finish()


def qa_hist_04(page):
    s = Sc(page, "QA-HIST-04", "the invariant is stated on screen")
    load(page); state(page, "shist")
    below = ev(page, "() => { const tb=document.querySelector('#shist table.logtbl');"
                     "return window.__t(tb.nextElementSibling); }")
    s.eq("paragraph below the table",
         'Closing cannot be confirmed while mismatched, so records are always saved as "Match" — mismatch causes (missed scans · over-scans · unresolved warnings) must be resolved before confirmation.',
         below)
    above = ev(page, "() => { const tb=document.querySelector('#shist table.logtbl');"
                     "return window.__t(tb.previousElementSibling); }")
    s.eq("intro paragraph above the table",
         "Daily snapshots saved automatically on closing confirmation — an audit trail of outbound target (manual count) · OK scans · warning resolution · confirmer",
         above)
    return s.finish()


def qa_hist_05(page):
    s = Sc(page, "QA-HIST-05", "the Closing tab returns to the previous view")
    load(page); state(page, "s2")
    page.click('#s2 [data-goto="shist"]')
    s.ok("section#shist active", has_class(page, "#shist", "on"), "on", "")
    try:
        ls = ev(page, "() => lastState")
        s.eq("wireframe lastState is 's2'", "s2", ls)
    except Exception as e:
        s.note(f"lastState not readable from the page ({e}); asserted behaviorally below.")
    s.eq('#shist [data-goto="back"] label', "Closing", t(page, '#shist [data-goto="back"]'))
    page.click('#shist [data-goto="back"]')
    s.ok("section#s2 becomes active again", has_class(page, "#s2", "on"), "on", "")
    return s.finish()


def qa_hist_10(page):
    s = Sc(page, "QA-HIST-10", "every demo row is a Match")
    load(page); state(page, "shist")
    rows = ev(page, "() => [...document.querySelectorAll('#shist table.logtbl tr')]"
                   ".filter(r => r.querySelector('td'))"
                   ".map(r => ({ date:window.__t(r.cells[0]), tgt:window.__t(r.cells[1]),"
                   "  ok:window.__t(r.cells[2]), match:window.__t(r.cells[4]),"
                   "  csv:[...r.querySelectorAll('button')].some(b => window.__t(b)==='CSV'),"
                   "  amend:[...r.querySelectorAll('button.amendbtn')].some(b => window.__t(b)==='Amend') }))")
    s.eq("5 data rows", 5, len(rows))
    for i, start in enumerate(["07-13 (today)", "07-12", "07-11", "07-10", "07-09"]):
        if i < len(rows):
            s.starts(f"row {i+1} Date starts with", start, rows[i]["date"])
    for i, r in enumerate(rows):
        s.eq(f"row {i+1} Match reads", "✓ Match", r["match"])
        s.eq(f"row {i+1} OK equals target", r["tgt"], r["ok"])
        s.ok(f"row {i+1} carries CSV + Amend buttons", r["csv"] and r["amend"], "CSV+Amend", r)
    return s.finish()


# ═════════════════ 8.13 QA-HUB ═════════════════
def qa_hub_01(page):
    s = Sc(page, "QA-HUB-01", "the hub opens with an unread badge")
    load(page); state(page, "s1")
    s.starts('nav [data-open="inbox1"] starts with', "💬 Comments", t(page, '#s1 [data-open="inbox1"]'))
    s.eq("carries .badge-n reading 2", "2", t(page, '#s1 [data-open="inbox1"] .badge-n'))
    page.click('#s1 [data-open="inbox1"]')
    s.ok("#inbox1 gains class open", has_class(page, "#inbox1", "open"), "open", "")
    s.starts("Mentions pane header starts with", "Comments mentioning me · Click to open the order",
             t(page, '#inbox1 [data-pane="mentions"] .paneheader'))
    bolds = texts(page, '#inbox1 [data-pane="mentions"] .it b')
    s.eq("three entries, bold entity labels",
         ["Order 413540", "Order 413498", "Order 413330"], bolds)
    unread = ev(page, "() => [...document.querySelectorAll('#inbox1 [data-pane=\"mentions\"] .it')]"
                     ".map(e => e.classList.contains('unread'))")
    s.eq("first two entries carry class unread", [True, True, False], unread)
    return s.finish()


def qa_hub_02(page):
    s = Sc(page, "QA-HUB-02", "tab switching")
    load(page); state(page, "s1")
    page.click('#s1 [data-open="inbox1"]')
    s.eq('tab label', "★ Saved", t(page, '#inbox1 [data-tab="saved"]'))
    page.click('#inbox1 [data-tab="saved"]')
    s.ok("saved tab gains class on", has_class(page, '#inbox1 [data-tab="saved"]', "on"), "on", "")
    vis = ev(page, "() => getComputedStyle(document.querySelector('#inbox1 [data-pane=\"saved\"]')).display")
    s.ok('[data-pane="saved"] becomes visible', vis != "none", "display != none", vis)
    s.starts("its .paneheader starts with", "Saved comments · Click to open the order",
             t(page, '#inbox1 [data-pane="saved"] .paneheader'))
    hid = ev(page, "() => getComputedStyle(document.querySelector('#inbox1 [data-pane=\"mentions\"]')).display")
    s.eq('[data-pane="mentions"] is hidden', "none", hid)
    entries = texts(page, '#inbox1 [data-pane="saved"] .it b')
    s.eq("Saved pane lists exactly one entry, Order 413498", ["Order 413498"], entries)
    return s.finish()


def qa_hub_03(page):
    s = Sc(page, "QA-HUB-03", "the star toggle (destructive)")
    load(page); state(page, "s1")
    page.click('#s1 [data-open="inbox1"]')
    pre = ev(page, "() => { const its=[...document.querySelectorAll('#inbox1 [data-pane=\"mentions\"] .it')];"
                   "const e413498=its.find(i => window.__t(i.querySelector('b'))==='Order 413498');"
                   "return e413498.querySelector('.star').classList.contains('on'); }")
    s.eq("'Order 413498' star already carries class on at load", True, pre)
    js = ("() => { const its=[...document.querySelectorAll('#inbox1 [data-pane=\"mentions\"] .it')];"
          "const it=its.find(i => window.__t(i.querySelector('b'))==='Order 413540');"
          "const st=it.querySelector('.star'); st.click(); return st.classList.contains('on'); }")
    s.eq("clicking the star on 'Order 413540' gains class on", True, ev(page, js))
    s.eq("clicking it again removes the class", False, ev(page, js))
    return s.finish()


def qa_hub_07(page):
    s = Sc(page, "QA-HUB-07", "(negative) only State 1 wires the dropdown (documents U-e)")
    load(page)
    for sid in ["s2", "s0", "s2b", "s3", "s4", "shist"]:
        btn = ev(page, f"() => {{ const b=[...document.querySelectorAll('#{sid} .icon-btn')]"
                       f".find(x => window.__t(x).startsWith('💬 Comments'));"
                       f"return b ? b.hasAttribute('data-open') : null; }}")
        s.eq(f"#{sid} Comments button carries no data-open", False, btn)
        s.eq(f"no inbox dropdown inside #{sid}", 0, count(page, f"#{sid} .inboxdd"))
    return s.finish()


# ═════════════════ 8.15 QA-CHROME ═════════════════
def qa_chrome_01(page):
    s = Sc(page, "QA-CHROME-01", "the global nav is present on every state [L-F1]")
    load(page)
    for sid in ["s0", "s1", "s2", "s2b", "s3", "s4", "shist"]:
        nav = ev(page, f"() => {{ const n=document.querySelector('#{sid} .nav'); if(!n) return null;"
                       "const c=n.cloneNode(true); c.querySelectorAll('.dot,.avatar').forEach(d=>d.remove());"
                       "const txt=c.textContent.replace(/\\s+/g,' ');"
                       "return { brand: window.__t(n.querySelector('.brand')),"
                       "  menus: ['Operation AI ▾','Catalog Management ▾','OMS Center ▾','Site Management ▾']"
                       "          .every(m => txt.includes(m)),"
                       "  comments: [...n.querySelectorAll('button')].some(b => window.__t(b).startsWith('💬 Comments')),"
                       "  user: (u => u && (cl => {cl.querySelectorAll('.avatar,.dot').forEach(d=>d.remove());"
                       "         return cl.textContent.replace(/\\s+/g,' ').trim();})(u.cloneNode(true)))"
                       "        (n.querySelector('.user')),"
                       "  logout: [...n.querySelectorAll('button')].some(b => window.__t(b)==='Logout') }; }")
        ok = (nav and nav["brand"] == "SkinSeoul" and nav["menus"] and nav["comments"]
              and nav["user"] == "Yongwon Ryu" and nav["logout"])
        s.ok(f"#{sid} .nav complete (brand/menus/Comments/user chip/Logout)", bool(ok),
             "SkinSeoul + 4 menus + 💬 Comments + Yongwon Ryu + Logout", nav)
    return s.finish()


def qa_chrome_02(page):
    s = Sc(page, "QA-CHROME-02", "the page header and in-page tabs [L-F2] [L-S1-11]")
    load(page)
    for sid in ["s0", "s1", "s2", "s2b", "s3", "s4", "shist"]:
        s.eq(f"#{sid} h2 reads", "WMS - Closing", t(page, f"#{sid} h2"))
        s.eq(f"#{sid} first p.sub (addressed per spec as .pagepad > p.sub:first-of-type)",
             "Barcode-scan verification of today's packed orders",
             t(page, f"#{sid} .pagepad > p.sub:first-of-type"))
        tabs = texts(page, f"#{sid} .pagetabs button")
        s.eq(f"#{sid} .pagetabs has exactly two buttons", ["Closing", "Closing History"], tabs)
        active = ev(page, f"() => {{ const b=document.querySelector('#{sid} .pagetabs button.on');"
                          "return b && window.__t(b); }")
        s.eq(f"#{sid} active in-page tab", "Closing History" if sid == "shist" else "Closing", active)
    return s.finish()


def qa_chrome_03(page):
    s = Sc(page, "QA-CHROME-03", "the toast slot shape [L-F3]")
    load(page); state(page, "s1")
    s.eq("#s1 .toast span reads", "✓ Outbound confirmed — YT2618100710108810",
         t(page, "#s1 .toast span"))
    s.eq("#s1 .toast small reads", "Ready for the next barcode scan", t(page, "#s1 .toast small"))
    shape = ev(page, "() => { const t=document.querySelector('#s4 .toast');"
                     "return t && !!t.querySelector('span') && !!t.querySelector('small'); }")
    s.eq("#s4 .toast follows the same two-part shape", True, shape)
    load(page)   # fresh load for the negative clause
    s.eq("no .toast.err on a fresh load", 0, count(page, ".toast.err"))
    return s.finish()


def qa_chrome_04(page):
    s = Sc(page, "QA-CHROME-04", "(negative) legend-unit count from DOM units, never tabs [WF-12]")
    load(page)
    s.eq('.wf-tab[data-modal="m-process"] yields 1', 1, count(page, '.wf-tab[data-modal="m-process"]'))
    s.eq(".legend ol > li yields 20", 20, count(page, ".legend ol > li"))
    s.eq("modal dots yield 3", 3, count(page, "#m-process .dot, #m-scandel .dot, #m-amend .dot"))
    s.eq("#s1 .legend > p yields 1", 1, count(page, "#s1 .legend > p"))
    s.eq(".wf-tab yields 10", 10, count(page, ".wf-tab"))
    s.eq(".wf-tab[data-modal] yields 3", 3, count(page, ".wf-tab[data-modal]"))
    return s.finish()


def qa_chrome_06(page):
    s = Sc(page, "QA-CHROME-06", "single-screen layout constraint [L-S1-9] [E-50]")
    load(page); state(page, "s1")
    dims = ev(page, "() => ({ sw: document.body.scrollWidth, cw: document.body.clientWidth })")
    s.ok("body does not scroll horizontally", dims["sw"] <= dims["cw"],
         "scrollWidth <= clientWidth", dims)
    ths = ev(page, "() => [...document.querySelectorAll('#s1 table.tbl thead th')]"
                  ".map(th => getComputedStyle(th).display)")
    s.ok("all 10 thead th rendered, none display:none",
         len(ths) == 10 and all(d != "none" for d in ths), "10 × display != none", ths)
    full = ev(page, "() => [...document.querySelectorAll('#s1 table.tbl td')]"
                   ".some(td => window.__t(td) === 'YT2618100710184356')")
    s.eq("longest tracking text fully present in the DOM", True, full)
    s.eq("no ellipsis character in the scan table", False,
         ev(page, "() => document.querySelector('#s1 table.tbl').textContent.includes('…')"))
    return s.finish()


# ═════════════════ 8.15b QA-AMEND ═════════════════
def qa_amend_01(page):
    s = Sc(page, "QA-AMEND-01", "every History row carries an Amend button")
    load(page); state(page, "shist")
    rows = ev(page, "() => [...document.querySelectorAll('#shist table.logtbl tr')]"
                   ".filter(r => r.querySelector('td'))"
                   ".map(r => { const a=r.querySelector('button.amendbtn');"
                   "  return a && { label: window.__t(a), date: a.dataset.date||null,"
                   "                meta: a.dataset.meta||null,"
                   "                besideCsv: [...r.querySelectorAll('button')].some(b => window.__t(b)==='CSV') }; })")
    s.eq("5 rows with amendbtn", 5, len([r for r in rows if r]))
    for i, r in enumerate(rows):
        ok = r and r["label"] == "Amend" and r["date"] and r["meta"] and r["besideCsv"]
        s.ok(f"row {i+1} amendbtn labelled 'Amend' beside CSV with data-date/data-meta",
             bool(ok), "Amend + data-date + data-meta + CSV", r)
    s.eq("5 in total", 5, count(page, "#shist button.amendbtn"))
    return s.finish()


def qa_amend_02(page):
    s = Sc(page, "QA-AMEND-02", "M3 opens with the owner's byte-exact copy")
    load(page); state(page, "shist")
    page.click('#shist button.amendbtn[data-date="07-13"]')
    s.ok("#m-amend gains class open", has_class(page, "#m-amend", "open"), "open", "")
    s.starts("header starts with", "Amend Closing — 07-13", t(page, "#m-amend header"))
    s.eq("its .dot reads", "M3", ev(page, "() => document.querySelector('#m-amend .dot').textContent.trim()"))
    s.eq("body b reads exactly",
         "Amend the closing for 07-13? The confirmed record stays until you re-confirm.",
         t(page, "#m-amend .body b"))
    s.eq("#amendMeta reads", "Confirmed 84/84 · 18:52 (Yongwon)", t(page, "#amendMeta"))
    s.eq("footer buttons", ["Keep the record", "Amend — open the closing"],
         texts(page, "#m-amend .foot button"))
    return s.finish()


def qa_amend_03(page):
    s = Sc(page, "QA-AMEND-03", "(negative) Keep the record is a true no-op")
    row_snapshot = None
    for closer, desc in [
        ("[...document.querySelectorAll('#m-amend .foot button')].find(b => window.__t(b)==='Keep the record').click()", "Keep the record"),
        ("document.querySelector('#m-amend header button.x').click()", "header ✕"),
        ("document.getElementById('m-amend').click()", "overlay click"),
    ]:
        load(page); state(page, "shist")
        if row_snapshot is None:
            row_snapshot = ev(page, "() => window.__t([...document.querySelectorAll("
                                    "'#shist table.logtbl tr')].filter(r => r.querySelector('td'))[0])")
        page.click('#shist button.amendbtn[data-date="07-13"]')
        s.ok(f"[{desc}] modal open before dismissal", has_class(page, "#m-amend", "open"), "open", "")
        page.evaluate(f"() => {{ {closer}; }}")
        s.ok(f"[{desc}] #m-amend loses class open", not has_class(page, "#m-amend", "open"), "not open", "")
        s.ok(f"[{desc}] section#shist still on", has_class(page, "#shist", "on"), "on", "")
        s.eq(f"[{desc}] #amendBanner computed display none", "none",
             ev(page, "() => getComputedStyle(document.getElementById('amendBanner')).display"))
        now = ev(page, "() => window.__t([...document.querySelectorAll("
                       "'#shist table.logtbl tr')].filter(r => r.querySelector('td'))[0])")
        s.eq(f"[{desc}] the 07-13 row is unchanged", row_snapshot, now)
    return s.finish()


def qa_amend_04(page):
    s = Sc(page, "QA-AMEND-04", "entering amendment mode (destructive)")
    load(page); state(page, "shist")
    page.click('#shist button.amendbtn[data-date="07-13"]')
    page.click("#amendYes")
    s.ok("#m-amend closes", not has_class(page, "#m-amend", "open"), "not open", "")
    s.ok("section#s1 becomes active", has_class(page, "#s1", "on"), "on", "")
    s.eq("#amendBanner computed display", "flex",
         ev(page, "() => getComputedStyle(document.getElementById('amendBanner')).display"))
    s.eq("#amendBannerB reads exactly", "AMENDING — 07-13 closing (confirmed 84/84)",
         t(page, "#amendBannerB"))
    s.eq("'✕ Exit amendment' button present", "✕ Exit amendment", t(page, "#amendExit"))
    s.eq("#targetIn1 value 85", "85", ev(page, "() => document.getElementById('targetIn1').value"))
    s.eq("#s1 scan input not disabled", False,
         ev(page, "() => document.querySelector('#s1 .scanbig input').hasAttribute('disabled')"))
    s.eq("#confirmBtn1 reads exactly", "Re-confirm Closing (1 remaining)", t(page, "#confirmBtn1"))
    # repeat from the 07-11 row
    load(page); state(page, "shist")
    page.click('#shist button.amendbtn[data-date="07-11"]')
    page.click("#amendYes")
    s.eq("07-11: banner interpolates", "AMENDING — 07-11 closing (confirmed 78/78)",
         t(page, "#amendBannerB"))
    s.eq("07-11: #targetIn1 value 79", "79", ev(page, "() => document.getElementById('targetIn1').value"))
    return s.finish()


def qa_amend_05(page):
    s = Sc(page, "QA-AMEND-05", "Exit amendment restores the resting demo state (destructive)")
    load(page); state(page, "shist")
    page.click('#shist button.amendbtn[data-date="07-13"]')
    page.click("#amendYes")
    s.ok("precondition: amendment mode active (s1 on)", has_class(page, "#s1", "on"), "on", "")
    page.click("#amendExit")
    s.ok("section#shist becomes active", has_class(page, "#shist", "on"), "on", "")
    s.eq("#amendBanner computed display none", "none",
         ev(page, "() => getComputedStyle(document.getElementById('amendBanner')).display"))
    s.eq("#targetIn1 back to 84", "84", ev(page, "() => document.getElementById('targetIn1').value"))
    s.eq("#confirmBtn1 reads the resting string", "Confirm Closing (79 remaining · 2 warnings)",
         t(page, "#confirmBtn1"))
    return s.finish()


def qa_amend_06(page):
    s = Sc(page, "QA-AMEND-06", "the Amended badge demo")
    load(page); state(page, "shist")
    s.eq("exactly one .amended-badge", 1, count(page, ".amended-badge"))
    info = ev(page, "() => { const b=document.querySelector('.amended-badge'); if(!b) return null;"
                    "const row=b.closest('tr');"
                    "return { txt: window.__t(b), inDateCell: b.closest('td') === row.cells[0],"
                    "  rowDate: window.__t(row.cells[0]),"
                    "  rowStyle: row.getAttribute('style') }; }")
    s.ok("inside the 07-12 row's Date cell",
         bool(info) and info["inDateCell"] and info["rowDate"].startswith("07-12"),
         "07-12 Date cell", info)
    s.eq("reads exactly", "Amended v2 · Dean · 07-13 09:12", info["txt"] if info else None)
    s.ok("badge does not alter the row's inline background",
         bool(info) and not (info["rowStyle"] and "background" in info["rowStyle"]),
         "no inline background on 07-12 row", info["rowStyle"] if info else None)
    today = ev(page, "() => [...document.querySelectorAll('#shist table.logtbl tr')]"
                    ".filter(r => r.querySelector('td'))[0].getAttribute('style')")
    s.eq("QA-HIST-03 highlight contract untouched", "background:var(--green-soft)", today)
    return s.finish()


SCENARIOS = [
    qa_s0_01, qa_s0_02, qa_s0_03, qa_s0_04,
    qa_scan_01, qa_scan_02, qa_scan_13, qa_scan_16,
    qa_verdict_01, qa_verdict_02, qa_verdict_03, qa_verdict_04, qa_verdict_05,
    qa_unknown_01, qa_unknown_02, qa_unknown_03,
    qa_dup_01, qa_dup_02, qa_dup_03,
    qa_voice_01, qa_voice_02, qa_voice_03, qa_voice_04, qa_voice_05, qa_voice_08,
    qa_count_01, qa_count_02, qa_count_03, qa_count_09, qa_count_10,
    qa_target_01, qa_target_02, qa_target_03, qa_target_04, qa_target_12,
    qa_m1_01, qa_m1_02, qa_m1_03, qa_m1_04, qa_m1_11,
    qa_del_01, qa_del_02, qa_del_03, qa_del_04, qa_del_05, qa_del_10,
    qa_confirm_01, qa_confirm_02, qa_confirm_03, qa_confirm_04, qa_confirm_05,
    qa_confirm_06, qa_confirm_15,
    qa_hist_01, qa_hist_02, qa_hist_03, qa_hist_04, qa_hist_05, qa_hist_10,
    qa_hub_01, qa_hub_02, qa_hub_03, qa_hub_07,
    qa_chrome_01, qa_chrome_02, qa_chrome_03, qa_chrome_04, qa_chrome_06,
    qa_amend_01, qa_amend_02, qa_amend_03, qa_amend_04, qa_amend_05, qa_amend_06,
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script(INIT)
        page = ctx.new_page()
        for fn in SCENARIOS:
            try:
                fn(page)
            except Exception as e:
                results.append(dict(id=fn.__name__, title="(crashed)", verdict="ERROR",
                                    fails=[{"assert": "runner exception", "expected": "",
                                            "actual": repr(e)}], notes=[], npass=0))
                print(f"ERR   {fn.__name__}: {e!r}")
        browser.close()

    n = len(results)
    npass = sum(1 for r in results if r["verdict"] == "PASS")
    nfail = sum(1 for r in results if r["verdict"] == "FAIL")
    nerr = sum(1 for r in results if r["verdict"] == "ERROR")
    print(f"\n== {n} scenarios · PASS {npass} · FAIL {nfail} · ERROR {nerr} ==")
    pathlib.Path(OUT_JSON).parent.mkdir(parents=True, exist_ok=True)
    # encoding 미지정이면 Windows 기본 코덱(cp949)으로 열려 한글 시나리오에서 죽는다.
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=1)
    print("json:", OUT_JSON)
    return 0 if nfail == 0 and nerr == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
