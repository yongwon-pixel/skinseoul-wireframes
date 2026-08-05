#!/usr/bin/env python3
"""
Adversarial QA execution of wms2/specs/closing.md  §8  — every [WF] scenario (68).

Rules implemented verbatim from §8.0:
  R1 reload between mutating scenarios      -> every scenario gets a fresh goto()
  R2 strip .dot before comparing text       -> window.__t()
  R3 address states/modals by attribute     -> .wf-tab[data-state=..] / [data-modal=..]
  R4 instrument speech before page script   -> add_init_script
  R5 rows addressed by first-cell text
  R6 byte-exact incl. · — ✓ ⚠ ✕ ①
  R7 page-global demo state
  R8 known demo limitations asserted as-is

Verdicts: PASS / FAIL / AMBIGUOUS / UNRUNNABLE
Usage:  python3 qa-closing.py            (prints table + writes results json next to it)
"""
import json, os, sys, pathlib
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
URL = "file://" + str((HERE / ".." / ".." / "closing" / "index.html").resolve())

R4 = r"""
window.__spoken = [];
window.SpeechSynthesisUtterance = function (txt) { this.text = txt; this.lang = ''; this.voice = null; };
Object.defineProperty(window, 'speechSynthesis', { configurable: true, value: {
  speak: u => window.__spoken.push({ text: u.text, lang: u.lang }),
  cancel: () => {}, getVoices: () => [] } });
window.__t = function (el) { if (!el) return null; const c = el.cloneNode(true);
  c.querySelectorAll('.dot').forEach(d => d.remove());
  return c.textContent.replace(/\s+/g, ' ').trim(); };
window.__row = function (sectionSel, label) {
  return [...document.querySelectorAll(sectionSel + ' table.tbl tbody tr')]
    .find(r => window.__t(r.cells[0]) === label) || null; };
window.__vis = function (el) { return !!(el && el.getClientRects().length); };
"""

results = []   # {id, verdict, notes:[...]}


class Sc:
    def __init__(self, page, sid, title):
        self.page, self.sid, self.title = page, sid, title
        self.fails, self.passes, self.amb, self.unrun = [], [], [], []

    def ok(self, desc, cond, ev=""):
        (self.passes if cond else self.fails).append(f"{desc} | {ev}")
        return cond

    def eq(self, desc, expected, actual):
        return self.ok(desc, expected == actual,
                       f"spec={expected!r} page={actual!r}")

    def contains(self, desc, needle, hay):
        return self.ok(desc, needle in (hay or ""),
                       f"spec-contains={needle!r} page={(hay or '')[:220]!r}")

    def ambiguous(self, why):
        self.amb.append(why)

    def unrunnable(self, why):
        self.unrun.append(why)

    def finish(self):
        if self.unrun:
            v = "UNRUNNABLE"
        elif self.fails:
            v = "FAIL"
        elif self.amb and not self.passes:
            v = "AMBIGUOUS"
        else:
            v = "PASS"
        results.append(dict(id=self.sid, title=self.title, verdict=v,
                            fails=self.fails, amb=self.amb, unrun=self.unrun,
                            npass=len(self.passes)))
        return v


def load(page):
    page.goto(URL)
    page.wait_for_load_state("domcontentloaded")


def state(page, sid):
    """R3: activate a state by its wf-bar tab attribute."""
    page.click(f'.wf-tab[data-state="{sid}"]')


def t(page, sel, root="document"):
    return page.evaluate(f"() => window.__t({root}.querySelector({json.dumps(sel)}))")


def texts(page, sel):
    return page.evaluate(
        "s => [...document.querySelectorAll(s)].map(e => window.__t(e))", sel)


def count(page, sel):
    return page.evaluate("s => document.querySelectorAll(s).length", sel)


def has_class(page, sel, cls):
    return page.evaluate(
        "([s,c]) => { const e=document.querySelector(s); return !!e && e.classList.contains(c); }",
        [sel, cls])


# ───────────────────────────── 8.1 QA-S0 ─────────────────────────────
def qa_s0_01(page):
    s = Sc(page, "QA-S0-01", "page opens on the pre-start screen")
    load(page)
    s.ok("section#s0 has class on", has_class(page, "#s0", "on"))
    for o in ["s1", "s2", "s2b", "s3", "s4", "shist"]:
        s.ok(f"section#{o} not on", not has_class(page, f"#{o}", "on"))
    s.ok('.wf-tab[data-state="s0"] has class on',
         has_class(page, '.wf-tab[data-state="s0"]', "on"))
    s.eq('wf-tab s0 text', "0 · Before Start (manual count)",
         t(page, '.wf-tab[data-state="s0"]'))
    heading = page.evaluate(
        "() => [...document.querySelectorAll('#s0 *')]"
        ".filter(e => window.__t(e) === \"① Today's Outbound Target (manual count)\").length")
    s.ok("card heading reads exactly '① Today's Outbound Target (manual count)'",
         heading >= 1, f"matching elements={heading}")
    s.ambiguous("'the card heading' names no selector; resolved by exact-text search inside #s0")
    ti = page.evaluate("() => { const e=document.getElementById('targetIn0');"
                       "return e && {ph:e.placeholder, v:e.value}; }")
    s.ok("#targetIn0 exists", bool(ti), f"{ti}")
    if ti:
        s.eq("#targetIn0 placeholder", "Hand-counted qty", ti["ph"])
        s.eq("#targetIn0 value", "", ti["v"])
    sib = page.evaluate("() => { const i=document.getElementById('targetIn0');"
                        "return i ? window.__t(i.nextElementSibling) : null; }")
    s.eq("literal text 'orders' follows the input", "orders", sib)
    s.eq("#startBtn0 label", "Start Closing", t(page, "#startBtn0"))
    return s.finish()


def qa_s0_02(page):
    s = Sc(page, "QA-S0-02", "(negative) Start blocked with an empty count [E-16]")
    load(page)
    s.eq("precondition #targetIn0.value", "",
         page.evaluate("() => document.getElementById('targetIn0').value"))
    page.click("#startBtn0")
    s.ok("section#s0 still on", has_class(page, "#s0", "on"))
    s.ok("section#s1 NOT on", not has_class(page, "#s1", "on"))
    s.ok("no .scanbig inside active section",
         count(page, "section.state.on .scanbig") == 0,
         f"count={count(page,'section.state.on .scanbig')}")
    vis_toast = page.evaluate(
        "() => [...document.querySelectorAll('.toast')].filter(window.__vis).length")
    s.ok("no toast element appears", vis_toast == 0, f"visible .toast={vis_toast}")
    return s.finish()


def qa_s0_03(page):
    s = Sc(page, "QA-S0-03", "Start with a value enters the in-progress screen (destructive)")
    load(page)
    page.fill("#targetIn0", "84")
    page.click("#startBtn0")
    s.ok("section#s1 on", has_class(page, "#s1", "on"))
    s.ok("section#s0 not on", not has_class(page, "#s0", "on"))
    s.ok('.wf-tab[data-state="s1"] on', has_class(page, '.wf-tab[data-state="s1"]', "on"))
    return s.finish()


def qa_s0_04(page):
    s = Sc(page, "QA-S0-04", "(negative) pre-start screen exposes nothing but the count")
    load(page)
    for sel in [".scanbig", ".clsstat", ".prog", "table.tbl", ".okline"]:
        s.ok(f"#s0 has no {sel}", count(page, f"#s0 {sel}") == 0,
             f"count={count(page, f'#s0 {sel}')}")
    n = page.evaluate("() => [...document.querySelectorAll('#s0 button')]"
                      ".filter(b => (window.__t(b)||'').startsWith('Confirm Closing')).length")
    s.ok("#s0 has no button starting 'Confirm Closing'", n == 0, f"count={n}")
    return s.finish()


# ───────────────────────────── 8.2 QA-SCAN ─────────────────────────────
def qa_scan_01(page):
    s = Sc(page, "QA-SCAN-01", "scan input present and correctly shaped")
    load(page); state(page, "s1")
    inp = page.evaluate("() => { const e=document.querySelector('#s1 .scanbig input');"
                        "return e && {ph:e.placeholder, v:e.value, dis:e.hasAttribute('disabled')}; }")
    s.ok("#s1 .scanbig input exists", bool(inp), f"{inp}")
    if inp:
        s.eq("placeholder",
             "Scan the tracking barcode — outbound status is judged instantly on scan", inp["ph"])
        s.eq("value", "YT2618100710108810", inp["v"])
        s.ok("input is NOT disabled", not inp["dis"], f"disabled={inp['dis']}")
    s.eq("sibling button.btn-blue labelled Scan", "Scan",
         t(page, "#s1 .scanbig button.btn-blue"))
    return s.finish()


def qa_scan_02(page):
    s = Sc(page, "QA-SCAN-02", "(negative) no scan surface before start [E-9]")
    load(page)
    s.ok("#s0 .scanbig does not exist", count(page, "#s0 .scanbig") == 0)
    ids = page.evaluate("() => [...document.querySelectorAll('#s0 input')].map(i=>i.id)")
    s.ok("#s0 contains no input other than #targetIn0", ids == ["targetIn0"], f"inputs={ids}")
    return s.finish()


def qa_scan_13(page):
    s = Sc(page, "QA-SCAN-13", "(negative) State 4 scan input rendered enabled (U-b)")
    load(page); state(page, "s4")
    inp = page.evaluate("() => { const e=document.querySelector('#s4 .scanbig input');"
                        "return e && {v:e.value, dis:e.hasAttribute('disabled')}; }")
    s.ok("#s4 .scanbig input exists", bool(inp), f"{inp}")
    if inp:
        s.eq("value is empty string", "", inp["v"])
        s.ok("does not carry disabled", not inp["dis"], f"disabled={inp['dis']}")
    return s.finish()


def qa_scan_16(page):
    s = Sc(page, "QA-SCAN-16", "(negative) wireframe implements no refocus loop")
    load(page); state(page, "s1")
    page.evaluate("() => document.body.click()")
    page.mouse.click(3, 3)
    focused = page.evaluate("() => document.activeElement === document.querySelector('#s1 .scanbig input')")
    s.ok("focus does NOT move to #s1 .scanbig input", not focused,
         f"scan-input focused={focused}")
    return s.finish()


# ───────────────────────────── 8.3 QA-VERDICT ─────────────────────────────
def qa_verdict_01(page):
    s = Sc(page, "QA-VERDICT-01", "OK row renders green with the exact pill")
    load(page); state(page, "s1")
    r = page.evaluate("""() => { const r = window.__row('#s1','#1'); if(!r) return null;
      return {cls:[...r.classList], st:window.__t(r.cells[5]),
        stSpan:!!r.cells[5].querySelector('span.cs-shipped'),
        cvSpan:!!r.cells[6].querySelector('span.cs-shipped'),
        cv:window.__t(r.cells[6]), worker:window.__t(r.cells[7]), notes:window.__t(r.cells[8])}; }""")
    s.ok("row #1 exists", bool(r), f"{r}")
    if r:
        s.ok("row #1 has class row-ok", "row-ok" in r["cls"], f"classes={r['cls']}")
        s.ok("Order Status cell has span.cs-shipped", r["stSpan"])
        s.eq("Order Status text", "Prepare Shipment", r["st"])
        s.ok("Closing Verdict cell has span.cs-shipped", r["cvSpan"])
        s.eq("Closing Verdict text", "✓ Outbounded", r["cv"])
        s.eq("Notes cell", "–", r["notes"])
        s.eq("Worker cell", "Dean", r["worker"])
    return s.finish()


def qa_verdict_02(page):
    s = Sc(page, "QA-VERDICT-02", "compact OK line byte-exact")
    load(page); state(page, "s1")
    s.ok("#s1 .okline exists", count(page, "#s1 .okline") == 1)
    s.eq("okline b", "✓ #5 Outbounded", t(page, "#s1 .okline b"))
    s.contains("okline contains order/tracking/status line",
               "Order 413540 · Tracking YT2618100710108810 · Prepare Shipment",
               t(page, "#s1 .okline"))
    s.eq("muted right-hand text", "18:41:07 · Dean", t(page, "#s1 .okline .mut"))
    s.ok("#s1 contains NO .bigstatus", count(page, "#s1 .bigstatus") == 0,
         f"count={count(page,'#s1 .bigstatus')}")
    return s.finish()


def qa_verdict_03(page):
    s = Sc(page, "QA-VERDICT-03", "Processing scan renders warning row + in-row action")
    load(page); state(page, "s2")
    r = page.evaluate("""() => { const r = window.__row('#s2','#4'); if(!r) return null;
      const b = r.cells[8].querySelector('button');
      return {cls:[...r.classList], stSpan:!!r.cells[5].querySelector('span.cs-processing'),
        st:window.__t(r.cells[5]), cvSpan:!!r.cells[6].querySelector('span.cs-processing'),
        cv:window.__t(r.cells[6]), btn:b&&window.__t(b), dm:b&&b.getAttribute('data-modal')}; }""")
    s.ok("row #4 exists in #s2", bool(r), f"{r}")
    if r:
        s.ok("class row-bad", "row-bad" in r["cls"], f"classes={r['cls']}")
        s.ok("Order Status span.cs-processing", r["stSpan"])
        s.eq("Order Status text", "Processing", r["st"])
        s.ok("Closing Verdict span.cs-processing", r["cvSpan"])
        s.eq("Closing Verdict text", "⚠ Not outbounded", r["cv"])
        s.eq("Notes button label", "Process this order", r["btn"])
        s.eq("button data-modal", "m-process", r["dm"])
    s.ok("#s2 contains no .bigstatus", count(page, "#s2 .bigstatus") == 0)
    return s.finish()


def qa_verdict_04(page):
    s = Sc(page, "QA-VERDICT-04", "(negative) OK rows carry no resolution button")
    load(page); state(page, "s1")
    bad = page.evaluate("""() => [...document.querySelectorAll('#s1 tr.row-ok')].filter(r =>
        [...r.querySelectorAll('button')].some(b => window.__t(b)==='Process this order')).length""")
    s.ok("no tr.row-ok has 'Process this order'", bad == 0, f"count={bad}")
    bad2 = page.evaluate("""() => [...document.querySelectorAll('#s1 tr.row-ok')].filter(r =>
        r.querySelector('span.cs-processing') || r.querySelector('span.cs-dup')).length""")
    s.ok("no tr.row-ok has cs-processing/cs-dup", bad2 == 0, f"count={bad2}")
    return s.finish()


def qa_verdict_05(page):
    s = Sc(page, "QA-VERDICT-05", "scan-list column contract")
    load(page); state(page, "s1")
    th = texts(page, "#s1 table.tbl thead th")
    exp = ["#", "Scan Time", "Tracking Barcode", "Order ID", "Items",
           "Order Status", "Closing Verdict", "Worker", "Notes", ""]
    s.eq("10 R2-normalized thead th texts", exp, th)
    raw = page.evaluate("""() => { const c=[...document.querySelectorAll('#s1 table.tbl thead th')];
      return [c[0].textContent.trim(), c[6].textContent.trim()]; }""")
    s.eq("raw textContent shows the dots", ["#6", "Closing Verdict5"], raw)
    p = page.evaluate("""() => { const tb=document.querySelector('#s1 table.tbl');
      let n=tb.nextElementSibling; while(n && n.tagName!=='P') n=n.nextElementSibling;
      return n && window.__t(n); }""")
    s.eq("paragraph beneath the table",
         "Sequence (#) = cumulative from 1 after closing starts · lowest first · all rows "
         "stored in the backend (fully included in the closing report export)", p)
    return s.finish()


# ───────────────────────────── 8.4 QA-UNKNOWN ─────────────────────────────
def qa_unknown_01(page):
    s = Sc(page, "QA-UNKNOWN-01", "unknown row renders with dashes and the red pill")
    load(page); state(page, "s2b")
    r = page.evaluate("""() => { const r=window.__row('#s2b','#7'); if(!r) return null;
      return {cls:[...r.classList], oid:window.__t(r.cells[3]), items:window.__t(r.cells[4]),
        st:window.__t(r.cells[5]), cvSpan:!!r.cells[6].querySelector('span.cs-dup'),
        cv:window.__t(r.cells[6])}; }""")
    s.ok("row #7 exists in #s2b", bool(r), f"{r}")
    if r:
        s.ok("class row-bad", "row-bad" in r["cls"], f"classes={r['cls']}")
        s.eq("Order ID cell", "–", r["oid"])
        s.eq("Items cell", "–", r["items"])
        s.eq("Order Status cell", "–", r["st"])
        s.ok("Closing Verdict has span.cs-dup", r["cvSpan"])
        s.eq("Closing Verdict text", "⚠ Unknown order", r["cv"])
    return s.finish()


def qa_unknown_02(page):
    s = Sc(page, "QA-UNKNOWN-02", "prescribed operator copy is intact")
    load(page); state(page, "s2b")
    notes = page.evaluate("() => { const r=window.__row('#s2b','#7'); return r && window.__t(r.cells[8]); }")
    s.eq("Notes cell reads exactly",
         "Mistyped tracking no. or an order from another system — check the physical label", notes)
    return s.finish()


def qa_unknown_03(page):
    s = Sc(page, "QA-UNKNOWN-03", "warnings tile names the unknown class")
    load(page); state(page, "s2b")
    s.eq("#s2b .tile.warn .lab", "Warnings (not outbounded · duplicate · unknown order)",
         t(page, "#s2b .tile.warn .lab"))
    s.eq("#s2b .tile.warn .val", "4", t(page, "#s2b .tile.warn .val"))
    s.contains("#s2b .proglab", "unknown orders are not counted", t(page, "#s2b .proglab"))
    return s.finish()


# ───────────────────────────── 8.5 QA-DUP ─────────────────────────────
def qa_dup_01(page):
    s = Sc(page, "QA-DUP-01", "duplicate row cites the collision with time and worker")
    load(page); state(page, "s3")
    r = page.evaluate("""() => { const r=window.__row('#s3','#6'); if(!r) return null;
      return {cls:[...r.classList], cvSpan:!!r.cells[6].querySelector('span.cs-dup'),
        cv:window.__t(r.cells[6]), b:window.__t(r.cells[8].querySelector('b')),
        notes:window.__t(r.cells[8])}; }""")
    s.ok("row #6 exists in #s3", bool(r), f"{r}")
    if r:
        s.ok("class row-bad", "row-bad" in r["cls"], f"classes={r['cls']}")
        s.ok("Closing Verdict has span.cs-dup", r["cvSpan"])
        s.eq("Closing Verdict text", "⚠ Duplicate scan", r["cv"])
        s.eq("Notes b element", "Duplicate of #2", r["b"])
        s.contains("Notes trailing text", "— first scanned 18:40:18 (Miranti)", r["notes"])
    return s.finish()


def qa_dup_02(page):
    s = Sc(page, "QA-DUP-02", "State 1 duplicate row variant")
    load(page); state(page, "s1")
    r = page.evaluate("""() => { const r=window.__row('#s1','#3'); if(!r) return null;
      return {cls:[...r.classList], cvSpan:!!r.cells[6].querySelector('span.cs-dup'),
        cv:window.__t(r.cells[6]), b:window.__t(r.cells[8].querySelector('b')),
        notes:window.__t(r.cells[8])}; }""")
    s.ok("row #3 exists in #s1", bool(r), f"{r}")
    if r:
        s.ok("class row-bad", "row-bad" in r["cls"], f"classes={r['cls']}")
        s.ok("shows span.cs-dup", r["cvSpan"])
        s.eq("verdict text", "⚠ Duplicate scan", r["cv"])
        s.eq("Notes b element", "Duplicate of #2", r["b"])
        s.contains("Notes text", "same tracking no. (check for combined box)", r["notes"])
    return s.finish()


def qa_dup_03(page):
    s = Sc(page, "QA-DUP-03", "first scan of a duplicated tracking is annotated")
    load(page); state(page, "s1")
    r = page.evaluate("""() => { const r=window.__row('#s1','#2'); if(!r) return null;
      return {cls:[...r.classList], trk:window.__t(r.cells[2]), w:window.__t(r.cells[7]),
        notes:window.__t(r.cells[8])}; }""")
    s.ok("row #2 exists in #s1", bool(r), f"{r}")
    if r:
        s.eq("tracking", "YT2618100710184356", r["trk"])
        s.eq("worker", "Miranti", r["w"])
        s.ok("class row-ok", "row-ok" in r["cls"], f"classes={r['cls']}")
        s.eq("Notes reads 'First scan'", "First scan", r["notes"])
    state(page, "s3")
    n3 = page.evaluate("() => { const r=window.__row('#s3','#2'); return r && window.__t(r.cells[8]); }")
    s.eq("same annotation on #s3 row #2", "First scan", n3)
    return s.finish()


# ───────────────────────────── 8.6 QA-VOICE ─────────────────────────────
def qa_voice_01(page):
    s = Sc(page, "QA-VOICE-01", "entering a warning state speaks the exact utterance")
    for st in ["s2", "s2b", "s3"]:
        load(page)
        s.ok(f"[{st}] __spoken empty on load",
             page.evaluate("() => window.__spoken.length") == 0)
        state(page, st)
        sp = page.evaluate("() => window.__spoken")
        s.ok(f"[{st}] exactly one entry", len(sp) == 1, f"spoken={sp}")
        if sp:
            s.eq(f"[{st}] text", "Please check this order", sp[0]["text"])
            s.eq(f"[{st}] lang", "en-US", sp[0]["lang"])
        s.eq(f"[{st}] data-voice attribute", "Please check this order",
             page.evaluate("s => document.getElementById(s).getAttribute('data-voice')", st))
    return s.finish()


def qa_voice_02(page):
    s = Sc(page, "QA-VOICE-02", "the toggle reflects state")
    load(page); state(page, "s1")
    page.evaluate("() => window.__spoken.length = 0")
    page.click("#voiceToggle")
    s.eq("#voiceState text", "Off", t(page, "#voiceState"))
    s.ok("#s1 .vtrack gains class off", has_class(page, "#s1 .vtrack", "off"))
    sp = page.evaluate("() => window.__spoken")
    s.ok("no new spoken entry", len(sp) == 0, f"spoken={sp}")
    return s.finish()


def qa_voice_03(page):
    s = Sc(page, "QA-VOICE-03", "(negative) voice OFF never suppresses the visual warning")
    load(page); state(page, "s1")
    page.click("#voiceToggle")
    s.eq("#voiceState reads Off", "Off", t(page, "#voiceState"))
    page.evaluate("() => window.__spoken.length = 0")
    state(page, "s3")
    s.ok("__spoken still empty", page.evaluate("() => window.__spoken.length") == 0,
         f"spoken={page.evaluate('() => window.__spoken')}")
    r = page.evaluate("""() => { const r=window.__row('#s3','#6');
      return r && {cls:[...r.classList], cv:window.__t(r.cells[6].querySelector('span.cs-dup'))}; }""")
    s.ok("row #6 still row-bad", r and "row-bad" in r["cls"], f"{r}")
    s.eq("row #6 still ⚠ Duplicate scan", "⚠ Duplicate scan", r and r["cv"])
    s.eq("red .proglab copy unchanged",
         "Closing progress 4.8% — duplicates are not double-counted", t(page, "#s3 .proglab"))
    return s.finish()


def qa_voice_04(page):
    s = Sc(page, "QA-VOICE-04", "Test voice overrides the toggle without changing it")
    load(page); state(page, "s1")
    page.click("#voiceToggle")
    s.eq("#voiceState Off", "Off", t(page, "#voiceState"))
    page.evaluate("() => window.__spoken.length = 0")
    s.eq("#voiceTest label", "🔊 Test voice", t(page, "#voiceTest"))
    page.click("#voiceTest")
    sp = page.evaluate("() => window.__spoken")
    s.ok("exactly one entry", len(sp) == 1, f"spoken={sp}")
    if sp:
        s.eq("entry text", "Please check this order", sp[0]["text"])
    s.eq("#voiceState still Off", "Off", t(page, "#voiceState"))
    s.ok(".vtrack still has class off", has_class(page, "#s1 .vtrack", "off"))
    return s.finish()


def qa_voice_05(page):
    s = Sc(page, "QA-VOICE-05", "turning the toggle ON plays one confirmation utterance")
    load(page); state(page, "s1")
    page.click("#voiceToggle")
    s.eq("precondition Off", "Off", t(page, "#voiceState"))
    page.evaluate("() => window.__spoken.length = 0")
    page.click("#voiceToggle")
    s.eq("#voiceState becomes On", "On", t(page, "#voiceState"))
    s.ok(".vtrack loses class off", not has_class(page, "#s1 .vtrack", "off"))
    sp = page.evaluate("() => window.__spoken")
    s.ok("exactly one entry", len(sp) == 1, f"spoken={sp}")
    return s.finish()


def qa_voice_08(page):
    s = Sc(page, "QA-VOICE-08", "replay control exists in every state")
    load(page)
    s.ok("#s1 contains #voiceTest", count(page, "#s1 #voiceTest") == 1)
    s.eq("#voiceTest label", "🔊 Test voice", t(page, "#s1 #voiceTest"))
    for sid in ["s2", "s2b", "s3"]:
        lbls = texts(page, f"#{sid} .sim-voice")
        s.eq(f"#{sid} .sim-voice label", ["🔊 Play again"], lbls)
    s.eq("#s4 .sim-voice label", ["🔊 Test voice"], texts(page, "#s4 .sim-voice"))
    return s.finish()


# ───────────────────────────── 8.7 QA-COUNT ─────────────────────────────
def qa_count_01(page):
    s = Sc(page, "QA-COUNT-01", "State 1 tiles render the demo values (U-a)")
    load(page); state(page, "s1")
    s.eq("#s1 .tile .val", ["84", "3", "2", "79"], texts(page, "#s1 .tile .val"))
    s.eq("#s1 .tile .lab",
         ["Today's outbound target (manual input)", "OK (outbounded)",
          "Warnings (not outbounded · duplicate)", "Remaining scans"],
         texts(page, "#s1 .tile .lab"))
    s.contains("proglab already says 81 short", "81 short of the manual count",
               t(page, "#s1 .proglab"))
    return s.finish()


def qa_count_02(page):
    s = Sc(page, "QA-COUNT-02", "progress bar segments")
    load(page); state(page, "s1")
    s.eq("#s1 .prog i.p-ok inline width", "3.6%",
         page.evaluate("() => document.querySelector('#s1 .prog i.p-ok').style.width"))
    s.eq("#s1 .prog i.p-warn inline width", "2.4%",
         page.evaluate("() => document.querySelector('#s1 .prog i.p-warn').style.width"))
    return s.finish()


def qa_count_03(page):
    s = Sc(page, "QA-COUNT-03", "progress label states the gate rule verbatim")
    load(page); state(page, "s1")
    s.eq("#s1 .proglab",
         "Closing progress 3.6% — OK 3/84 (81 short of the manual count) · 2 warnings to "
         "resolve — closing confirms only at an exact OK 84/84 match with 0 warnings; "
         "over-scan is also a mismatch", t(page, "#s1 .proglab"))
    return s.finish()


def qa_count_09(page):
    s = Sc(page, "QA-COUNT-09", "warning-state tiles in the demo")
    load(page); state(page, "s2b")
    s.eq("#s2b .tile .val", ["84", "4", "4", "80"], texts(page, "#s2b .tile .val"))
    s.eq("#s2b i.p-warn width", "4.8%",
         page.evaluate("() => document.querySelector('#s2b .prog i.p-warn').style.width"))
    state(page, "s3")
    s.eq("#s3 .tile .val", ["84", "4", "3", "80"], texts(page, "#s3 .tile .val"))
    s.contains("#s3 .proglab", "duplicates are not double-counted", t(page, "#s3 .proglab"))
    return s.finish()


def qa_count_10(page):
    s = Sc(page, "QA-COUNT-10", "State 2 tiles and bar")
    load(page); state(page, "s2")
    s.eq("#s2 .tile .val", ["84", "4", "3", "80"], texts(page, "#s2 .tile .val"))
    s.eq("#s2 i.p-ok width", "4.8%",
         page.evaluate("() => document.querySelector('#s2 .prog i.p-ok').style.width"))
    s.eq("#s2 i.p-warn width", "3.6%",
         page.evaluate("() => document.querySelector('#s2 .prog i.p-warn').style.width"))
    s.eq("#s2 .proglab",
         "Closing progress 4.8% — Confirm Closing becomes available after resolving 3 warnings",
         t(page, "#s2 .proglab"))
    return s.finish()


# ───────────────────────────── 8.8 QA-TARGET ─────────────────────────────
def qa_target_01(page):
    s = Sc(page, "QA-TARGET-01", "locked banner shows the target and the starter")
    load(page); state(page, "s1")
    s.eq("banner b", "① Today's Outbound Target (manual count)",
         t(page, "#s1 .clsbanner.info b"))
    s.contains("banner text", "Closing in progress (started 18:02 · Dean)",
               t(page, "#s1 .clsbanner.info"))
    v = page.evaluate("() => { const e=document.getElementById('targetIn1');"
                      "return {v:e.value, dis:e.hasAttribute('disabled')}; }")
    s.eq("#targetIn1 value", "84", v["v"])
    s.ok("#targetIn1 disabled", v["dis"], f"disabled={v['dis']}")
    s.eq("#targetEdit label", "↺ Edit count", t(page, "#targetEdit"))
    s.eq("#closeCancel label", "✕ Cancel Closing", t(page, "#closeCancel"))
    return s.finish()


def qa_target_02(page):
    s = Sc(page, "QA-TARGET-02", "Edit count unlocks the field (destructive)")
    load(page); state(page, "s1")
    page.click("#targetEdit")
    r = page.evaluate("""() => { const i=document.getElementById('targetIn1');
      return {dis:i.hasAttribute('disabled'), active:document.activeElement===i,
        selStart:i.selectionStart, selEnd:i.selectionEnd, len:i.value.length,
        btn:window.__t(document.getElementById('targetEdit'))}; }""")
    s.ok("#targetIn1 no longer disabled", not r["dis"], f"{r}")
    s.ok("#targetIn1 is document.activeElement", r["active"], f"{r}")
    s.ok("value is selected", r["selStart"] == 0 and r["selEnd"] == r["len"], f"{r}")
    s.eq("#targetEdit text becomes Save", "Save", r["btn"])
    return s.finish()


def qa_target_03(page):
    s = Sc(page, "QA-TARGET-03", "Save re-locks the field")
    load(page); state(page, "s1")
    page.click("#targetEdit")
    page.click("#targetEdit")
    s.ok("#targetIn1 disabled again",
         page.evaluate("() => document.getElementById('targetIn1').hasAttribute('disabled')"))
    s.eq("button text returns", "↺ Edit count", t(page, "#targetEdit"))
    return s.finish()


def qa_target_04(page):
    s = Sc(page, "QA-TARGET-04", "(negative) cancel without a dialog (WF-7) (destructive)")
    load(page); state(page, "s1")
    before = count(page, ".overlay.open")
    page.click("#closeCancel")
    after = count(page, ".overlay.open")
    s.ok("section#s0 becomes active", has_class(page, "#s0", "on"))
    s.ok("section#s1 loses class on", not has_class(page, "#s1", "on"))
    s.ok("no .overlay.open at any point", before == 0 and after == 0,
         f"before={before} after={after}")
    return s.finish()


def qa_target_12(page):
    s = Sc(page, "QA-TARGET-12", "(negative) warning states render a muted target line (U-j)")
    load(page)
    for sid in ["s2", "s2b", "s3"]:
        state(page, sid)
        s.ok(f"#{sid} .clsbanner.info does not exist",
             count(page, f"#{sid} .clsbanner.info") == 0)
        muts = texts(page, f"#{sid} p.mut")
        want = "① Today's outbound target (manual count): 84 orders — closing started 18:02 (Dean)"
        s.ok(f"#{sid} p.mut reads the muted target line", want in muts,
             f"spec={want!r} page={muts!r}")
        s.ok(f"#{sid} contains no #targetEdit", count(page, f"#{sid} #targetEdit") == 0)
        s.ok(f"#{sid} contains no #closeCancel", count(page, f"#{sid} #closeCancel") == 0)
    return s.finish()


# ───────────────────────────── 8.9 QA-M1 ─────────────────────────────
def qa_m1_01(page):
    s = Sc(page, "QA-M1-01", "modal opens from the warning row")
    load(page); state(page, "s2")
    page.evaluate("""() => { const r=window.__row('#s2','#4');
      [...r.cells[8].querySelectorAll('button')].find(b=>window.__t(b)==='Process this order').click(); }""")
    s.ok("#m-process gains class open", has_class(page, "#m-process", "open"))
    load(page); state(page, "s1")
    n = page.evaluate("""() => { const r=window.__row('#s1','#4');
      return [...r.cells[8].querySelectorAll('button')].filter(b=>window.__t(b)==='Process this order').length; }""")
    s.ok("same button exists inside #s1 row #4", n == 1, f"count={n}")
    page.evaluate("""() => { const r=window.__row('#s1','#4');
      [...r.cells[8].querySelectorAll('button')].find(b=>window.__t(b)==='Process this order').click(); }""")
    s.ok("and opens the same modal", has_class(page, "#m-process", "open"))
    return s.finish()


def qa_m1_02(page):
    s = Sc(page, "QA-M1-02", "modal content is byte-exact")
    load(page)
    page.click('.wf-tab[data-modal="m-process"]')
    hdr = t(page, "#m-process header")
    s.ok("header starts with 'Process Processing Order — Order 413511'",
         (hdr or "").startswith("Process Processing Order — Order 413511"),
         f"page={hdr!r}")
    s.eq("body b", "This order has not been outbound-processed yet.",
         t(page, "#m-process .body b"))
    s.contains("body tracking line",
               "Tracking YT2618100710223471 · 1 item · Status Processing",
               t(page, "#m-process .body"))
    lbl = page.evaluate("""() => { const cb=document.querySelector('#m-process input[type=checkbox]');
      return cb ? window.__t(cb.closest('label')) : null; }""")
    s.ok("checkbox present", lbl is not None, f"label={lbl!r}")
    s.contains("label mentions Zero Packing verification",
               "Packing status of this order verified at Zero Packing", lbl)
    s.contains("label mentions step 6", "(step 6 of the current closing process)", lbl)
    ph = page.evaluate("() => { const e=document.querySelector('#m-process textarea.mtextarea');"
                       "return e && e.placeholder; }")
    s.eq("textarea.mtextarea placeholder",
         "Packing status and actions taken — if written, it is also recorded to the order's "
         "Comments history and the closing log", ph)
    note = t(page, "#m-process .note")
    s.contains("note status change", "changes the real order status Processing → Prepare Shipment", note)
    s.contains("note fallback", "If packing is incomplete, handle it separately and rescan.", note)
    return s.finish()


def qa_m1_03(page):
    s = Sc(page, "QA-M1-03", "footer buttons")
    load(page)
    page.click('.wf-tab[data-modal="m-process"]')
    foot = texts(page, "#m-process .foot button")
    s.ok("foot contains a button labelled Close", "Close" in foot, f"page={foot}")
    green = texts(page, "#m-process .foot button.btn-green")
    s.eq("btn-green label", ["Process Outbound → resolve warning"], green)
    return s.finish()


def qa_m1_04(page):
    s = Sc(page, "QA-M1-04", "(negative) dismissal changes nothing")
    def row_intact(tag):
        r = page.evaluate("""() => { const r=window.__row('#s2','#4'); if(!r) return null;
          return {cv:window.__t(r.cells[6].querySelector('span.cs-processing')),
                  btn:[...r.cells[8].querySelectorAll('button')].map(b=>window.__t(b))}; }""")
        s.eq(f"[{tag}] row #4 verdict still ⚠ Not outbounded", "⚠ Not outbounded", r and r["cv"])
        s.ok(f"[{tag}] 'Process this order' button intact",
             r and "Process this order" in r["btn"], f"{r}")

    # a) footer Close
    load(page); state(page, "s2")
    page.click('.wf-tab[data-modal="m-process"]')
    page.evaluate("""() => [...document.querySelectorAll('#m-process .foot button')]
        .find(b=>window.__t(b)==='Close').click()""")
    s.ok("[Close] #m-process loses class open", not has_class(page, "#m-process", "open"))
    row_intact("Close")
    # b) header ✕
    load(page); state(page, "s2")
    page.click('.wf-tab[data-modal="m-process"]')
    page.click("#m-process header button.x")
    s.ok("[✕] #m-process loses class open", not has_class(page, "#m-process", "open"))
    row_intact("✕")
    # c) click on the overlay itself
    load(page); state(page, "s2")
    page.click('.wf-tab[data-modal="m-process"]')
    page.evaluate("""() => document.getElementById('m-process')
        .dispatchEvent(new MouseEvent('click',{bubbles:true}))""")
    s.ok("[overlay] #m-process loses class open", not has_class(page, "#m-process", "open"))
    row_intact("overlay")
    return s.finish()


def qa_m1_11(page):
    s = Sc(page, "QA-M1-11", "(negative) wireframe does not gate the button on the checkbox")
    load(page); state(page, "s2")
    page.click('.wf-tab[data-modal="m-process"]')
    r = page.evaluate("""() => { const b=[...document.querySelectorAll('#m-process .foot button')]
        .find(x=>window.__t(x)==='Process Outbound → resolve warning');
      return {dis:b.hasAttribute('disabled'), close:b.hasAttribute('data-close'),
        checked:document.querySelector('#m-process input[type=checkbox]').checked}; }""")
    s.ok("checkbox unticked", not r["checked"], f"{r}")
    s.ok("button is NOT disabled", not r["dis"], f"disabled={r['dis']}")
    s.ok("button merely carries data-close", r["close"], f"data-close={r['close']}")
    page.evaluate("""() => [...document.querySelectorAll('#m-process .foot button')]
        .find(x=>window.__t(x)==='Process Outbound → resolve warning').click()""")
    s.ok("modal closes", not has_class(page, "#m-process", "open"))
    after = page.evaluate("""() => { const r=window.__row('#s2','#4');
      return {cls:[...r.classList], cv:window.__t(r.cells[6])}; }""")
    s.ok("underlying row unchanged",
         "row-bad" in after["cls"] and after["cv"] == "⚠ Not outbounded", f"{after}")
    return s.finish()


# ───────────────────────────── 8.10 QA-DEL ─────────────────────────────
def open_del(page, label):
    page.evaluate("l => window.__row('#s1', l).querySelector('button.scandel').click()", label)


def qa_del_01(page):
    s = Sc(page, "QA-DEL-01", "modal identifies the row it will remove")
    load(page); state(page, "s1")
    s.eq("precondition rows #1..#5", ["#1", "#2", "#3", "#4", "#5"],
         page.evaluate("() => [...document.querySelectorAll('#s1 table.tbl tbody tr')]"
                       ".map(r=>window.__t(r.cells[0]))"))
    title = page.evaluate("() => window.__row('#s1','#3').querySelector('button.scandel').title")
    s.eq("✕ button title", "Delete scan row", title)
    open_del(page, "#3")
    s.ok("#m-scandel gains class open", has_class(page, "#m-scandel", "open"))
    hdr = t(page, "#m-scandel header")
    s.eq("header reads 'Delete Scan Row'", "Delete Scan Row", hdr)
    s.eq("body b reads 'Remove this scan?'", "Remove this scan?", t(page, "#m-scandel .body b"))
    s.eq("#scandelInfo reads exactly", "#3 · YT2618100710184356", t(page, "#scandelInfo"))
    return s.finish()


def qa_del_02(page):
    s = Sc(page, "QA-DEL-02", "(negative) 'No' is a true no-op")
    load(page); state(page, "s1")
    open_del(page, "#3")
    page.evaluate("""() => [...document.querySelectorAll('#m-scandel .foot button')]
        .find(b=>window.__t(b)==='No').click()""")
    s.ok("#m-scandel loses class open", not has_class(page, "#m-scandel", "open"))
    rows = page.evaluate("() => [...document.querySelectorAll('#s1 table.tbl tbody tr')]"
                         ".map(r=>window.__t(r.cells[0]))")
    s.eq("still 5 rows including #3", ["#1", "#2", "#3", "#4", "#5"], rows)
    return s.finish()


def qa_del_03(page):
    s = Sc(page, "QA-DEL-03", "'Yes — remove' removes the row, preserves numbering (destructive)")
    load(page); state(page, "s1")
    open_del(page, "#3")
    s.eq("#scandelYes label", "Yes — remove", t(page, "#scandelYes"))
    page.click("#scandelYes")
    s.ok("overlay closes", not has_class(page, "#m-scandel", "open"))
    rows = page.evaluate("() => [...document.querySelectorAll('#s1 table.tbl tbody tr')]"
                         ".map(r=>window.__t(r.cells[0]))")
    s.eq("4 rows, no renumbering", ["#1", "#2", "#4", "#5"], rows)
    return s.finish()


def qa_del_04(page):
    s = Sc(page, "QA-DEL-04", "retention promise stated in the modal")
    load(page)
    page.click('.wf-tab[data-modal="m-scandel"]')
    s.eq("#m-scandel .note",
         "Deleting excludes it from the list and the closing counts — for clearing mis-scans, "
         "unknown orders, etc. Deletion history is kept in the backend.",
         t(page, "#m-scandel .note"))
    return s.finish()


def qa_del_05(page):
    s = Sc(page, "QA-DEL-05", "(negative) wireframe does not recompute tiles (destructive)")
    load(page); state(page, "s1")
    s.eq("precondition tiles", ["84", "3", "2", "79"], texts(page, "#s1 .tile .val"))
    open_del(page, "#3")
    page.click("#scandelYes")
    s.eq("tiles unchanged", ["84", "3", "2", "79"], texts(page, "#s1 .tile .val"))
    s.eq("i.p-warn still 2.4%", "2.4%",
         page.evaluate("() => document.querySelector('#s1 .prog i.p-warn').style.width"))
    return s.finish()


def qa_del_10(page):
    s = Sc(page, "QA-DEL-10", "modal also reachable from the wf-bar tab")
    load(page)
    page.click('.wf-tab[data-modal="m-scandel"]')
    s.ok("#m-scandel gains class open", has_class(page, "#m-scandel", "open"))
    s.eq("#scandelInfo default text", "#7 · YT2618100719984412", t(page, "#scandelInfo"))
    return s.finish()


# ───────────────────────────── 8.11 QA-CONFIRM ─────────────────────────────
def qa_confirm_01(page):
    s = Sc(page, "QA-CONFIRM-01", "disabled button carries the blockers")
    load(page); state(page, "s1")
    s.eq("banner b", "Confirm Closing", t(page, "#s1 .clsbanner.done b"))
    btns = texts(page, "#s1 .clsbanner.done button")
    s.eq("button R2-normalized text", ["Confirm Closing (79 remaining · 2 warnings)"], btns)
    txt = t(page, "#s1 .clsbanner.done")
    for frag in ["no auto-confirm; closing happens only when this button is pressed.",
                 "an over-scan makes it a mismatch and disables the button again",
                 "auto-updates Daily Shipping Status"]:
        s.contains("banner text", frag, txt)
    return s.finish()


def qa_confirm_02(page):
    s = Sc(page, "QA-CONFIRM-02", "button renders as disabled")
    load(page); state(page, "s1")
    cls = page.evaluate("() => [...document.querySelector('#s1 .clsbanner.done button').classList]")
    s.ok("button carries class btn-gray", "btn-gray" in cls, f"classes={cls}")
    cur = page.evaluate("() => getComputedStyle(document.querySelector('#s1 .clsbanner.done button')).cursor")
    s.eq("cursor:not-allowed", "not-allowed", cur)
    return s.finish()


def qa_confirm_03(page):
    s = Sc(page, "QA-CONFIRM-03", "completion panel is the only large panel on the page")
    load(page); state(page, "s4")
    s.ok("#s4 .bigstatus has class bs-ok", has_class(page, "#s4 .bigstatus", "bs-ok"))
    s.eq(".big text", "Today's closing complete — all orders verified", t(page, "#s4 .bigstatus .big"))
    s.contains(".bmeta",
               "Manual count 84 = OK scans 84, an exact match · 0 warnings · closing confirmed "
               "2026-07-13 18:52 (Yongwon)", t(page, "#s4 .bmeta"))
    bside = t(page, "#s4 .bside")
    s.contains(".bside Warnings", "Warnings", bside)
    s.contains(".bside 0", "0", bside)
    s.contains(".bside Remaining scans 0", "Remaining scans 0", bside)
    s.ok(".bs-warn yields zero elements", count(page, ".bs-warn") == 0,
         f"count={count(page,'.bs-warn')}")
    s.ok(".bigstatus yields exactly one, inside #s4",
         count(page, ".bigstatus") == 1 and count(page, "#s4 .bigstatus") == 1,
         f"doc={count(page,'.bigstatus')} in-s4={count(page,'#s4 .bigstatus')}")
    return s.finish()


def qa_confirm_04(page):
    s = Sc(page, "QA-CONFIRM-04", "confirmation toast copy")
    load(page); state(page, "s4")
    s.contains("#s4 .toast", "✓ Today's closing confirmed — 84/84 orders", t(page, "#s4 .toast"))
    s.eq("#s4 .toast small", "Daily Shipping Status auto-updated", t(page, "#s4 .toast small"))
    s.ok("#s4 .toast has no class err", not has_class(page, "#s4 .toast", "err"))
    return s.finish()


def qa_confirm_05(page):
    s = Sc(page, "QA-CONFIRM-05", "Closing Report banner, and no print affordance")
    load(page); state(page, "s4")
    bs = [x for x in texts(page, "#s4 .clsbanner.done b")]
    s.ok("banner b 'Closing Report'", "Closing Report" in bs, f"page={bs}")
    s.contains("banner text",
               "replaces the manual copy/paste and formula-stripping into SS Daily Shipping Status",
               t(page, "#s4 .clsbanner.done"))
    s.ok("Download Closing Report (CSV) button",
         "Download Closing Report (CSV)" in texts(page, "#s4 .clsbanner.done button"),
         f"page={texts(page,'#s4 .clsbanner.done button')}")
    n = page.evaluate("() => [...document.querySelectorAll('*')]"
                      ".filter(e => e.children.length===0 && (e.textContent||'').includes('Print')).length")
    s.ok("no element text contains 'Print'", n == 0, f"leaf elements containing 'Print'={n}")
    nb = page.evaluate("() => [...document.querySelectorAll('button')]"
                       ".filter(b => window.__t(b)==='Print').length")
    s.ok("no button whose normalized text is 'Print'", nb == 0, f"count={nb}")
    return s.finish()


def qa_confirm_06(page):
    s = Sc(page, "QA-CONFIRM-06", "Warning Resolution Summary and the State 4 tiles")
    load(page); state(page, "s4")
    s.eq("#s4 .clsbanner.info b", "Warning Resolution Summary", t(page, "#s4 .clsbanner.info b"))
    s.contains("summary text",
               "3 warnings today — 1 Processing (413511, resolved after Outbound) · 2 duplicates "
               "(combined-box confirmed, logged in Comments).", t(page, "#s4 .clsbanner.info"))
    s.eq("#s4 .tile .val", ["84", "84", "0", "0"], texts(page, "#s4 .tile .val"))
    labs = texts(page, "#s4 .tile .lab")
    s.eq("third .lab", "Warnings (resolved)", labs[2] if len(labs) > 2 else None)
    s.eq("#s4 i.p-ok width", "100%",
         page.evaluate("() => document.querySelector('#s4 .prog i.p-ok').style.width"))
    s.ok("no i.p-warn in #s4", count(page, "#s4 .prog i.p-warn") == 0)
    return s.finish()


def qa_confirm_15(page):
    s = Sc(page, "QA-CONFIRM-15", "(negative) State 4 exposes no session controls")
    load(page); state(page, "s4")
    s.ok("no #targetEdit in #s4", count(page, "#s4 #targetEdit") == 0)
    s.ok("no #closeCancel in #s4", count(page, "#s4 #closeCancel") == 0)
    n = page.evaluate("""() => [...document.querySelectorAll('#s4 .clsbanner.info')]
        .filter(x => [...x.querySelectorAll('b')]
          .some(b => window.__t(b)==="Today's Outbound Target (manual count)")).length""")
    s.ok("no .clsbanner.info with that b", n == 0, f"count={n}")
    nb = page.evaluate("() => [...document.querySelectorAll('#s4 button')]"
                       ".filter(b => (window.__t(b)||'').startsWith('Confirm Closing')).length")
    s.ok("no button starting 'Confirm Closing'", nb == 0, f"count={nb}")
    muts = texts(page, "#s4 p.mut")
    want = "① Today's outbound target (manual count): 84 orders — closing started 18:02 (Dean)"
    s.ok("p.mut reads the muted target line", want in muts, f"spec={want!r} page={muts!r}")
    return s.finish()


# ───────────────────────────── 8.12 QA-HIST ─────────────────────────────
def qa_hist_01(page):
    s = Sc(page, "QA-HIST-01", "history page reachable from the closing screen")
    load(page); state(page, "s1")
    s.eq('#s1 [data-goto="shist"] label', "Closing History", t(page, '#s1 [data-goto="shist"]'))
    page.click('#s1 [data-goto="shist"]')
    s.ok("#shist has class on", has_class(page, "#shist", "on"))
    s.ok("#s1 does not", not has_class(page, "#s1", "on"))
    for sid in ["s0", "s2", "s2b", "s3", "s4"]:
        s.ok(f"tab exists in #{sid}", count(page, f'#{sid} [data-goto="shist"]') == 1,
             f"count={count(page, f'#{sid} [data-goto=\"shist\"]')}")
    return s.finish()


def qa_hist_02(page):
    s = Sc(page, "QA-HIST-02", "table contract")
    load(page); state(page, "shist")
    th = texts(page, "#shist table.logtbl th")
    s.eq("header cells", ["Date", "Outbound Target (manual)", "OK Scans",
                          "Warnings (raised→resolved)", "Match", "Closed By",
                          "Confirmed At", ""], th)
    return s.finish()


def qa_hist_03(page):
    s = Sc(page, "QA-HIST-03", "today's row and the CSV action")
    load(page); state(page, "shist")
    row = page.evaluate("""() => { const rs=[...document.querySelectorAll('#shist table.logtbl tr')];
      const r=rs[1]; return {cells:[...r.cells].slice(0,7).map(c=>window.__t(c)),
        btn:window.__t(r.cells[7].querySelector('button')),
        bg:getComputedStyle(r).backgroundColor,
        bg2:getComputedStyle(rs[2]).backgroundColor, inline:r.getAttribute('style')}; }""")
    s.eq("first data row cells",
         ["07-13 (today)", "84", "84", "3→3", "✓ Match", "Yongwon", "18:52"], row["cells"])
    s.eq("CSV button", "CSV", row["btn"])
    s.ok("row background is the green highlight (differs from the next row)",
         row["bg"] != row["bg2"] and "green-soft" in (row["inline"] or ""),
         f"row1={row['bg']} row2={row['bg2']} inline={row['inline']!r}")
    s.ambiguous("'the green highlight' is not given a value or selector; "
                "resolved via the inline style token and a diff against row 2")
    return s.finish()


def qa_hist_04(page):
    s = Sc(page, "QA-HIST-04", "the invariant is stated on screen")
    load(page); state(page, "shist")
    ps = texts(page, "#shist p.mut")
    below = ('Closing cannot be confirmed while mismatched, so records are always saved as '
             '"Match" — mismatch causes (missed scans · over-scans · unresolved warnings) '
             'must be resolved before confirmation.')
    above = ("Daily snapshots saved automatically on closing confirmation — an audit trail of "
             "outbound target (manual count) · OK scans · warning resolution · confirmer")
    s.ok("paragraph below the table", below in ps, f"spec={below!r} page={ps!r}")
    s.ok("intro paragraph above the table", above in ps, f"spec={above!r} page={ps!r}")
    return s.finish()


def qa_hist_05(page):
    s = Sc(page, "QA-HIST-05", "the Closing tab returns to the previous view")
    load(page)
    state(page, "s2")
    page.click('#s2 [data-goto="shist"]')
    s.ok("#shist active", has_class(page, "#shist", "on"))
    try:
        ls = page.evaluate("() => lastState")
    except Exception as e:
        ls = f"<unreadable: {e}>"
    s.eq("wireframe lastState", "s2", ls)
    s.eq('#shist [data-goto="back"] label', "Closing", t(page, '#shist [data-goto="back"]'))
    page.click('#shist [data-goto="back"]')
    s.ok("#s2 becomes active again", has_class(page, "#s2", "on"))
    return s.finish()


def qa_hist_10(page):
    s = Sc(page, "QA-HIST-10", "every demo row is a Match")
    load(page); state(page, "shist")
    d = page.evaluate("""() => { const rs=[...document.querySelectorAll('#shist table.logtbl tr')].slice(1);
      return rs.map(r => ({date:window.__t(r.cells[0]), tgt:window.__t(r.cells[1]),
        ok:window.__t(r.cells[2]), match:window.__t(r.cells[4]),
        csv:window.__t(r.cells[7].querySelector('button'))})); }""")
    s.eq("5 data rows in order",
         ["07-13 (today)", "07-12", "07-11", "07-10", "07-09"], [r["date"] for r in d])
    s.ok("every Match cell reads '✓ Match'", all(r["match"] == "✓ Match" for r in d),
         f"page={[r['match'] for r in d]}")
    s.ok("every OK Scans equals Outbound Target", all(r["ok"] == r["tgt"] for r in d),
         f"page={[(r['tgt'], r['ok']) for r in d]}")
    s.ok("every row carries a CSV button", all(r["csv"] == "CSV" for r in d),
         f"page={[r['csv'] for r in d]}")
    return s.finish()


# ───────────────────────────── 8.13 QA-HUB ─────────────────────────────
def qa_hub_01(page):
    s = Sc(page, "QA-HUB-01", "hub opens with an unread badge")
    load(page); state(page, "s1")
    btn = t(page, '#s1 [data-open="inbox1"]')
    s.eq('nav button reads "💬 Comments"', "💬 Comments", btn)
    s.eq("badge-n text", "2", t(page, '#s1 [data-open="inbox1"] .badge-n'))
    page.click('#s1 [data-open="inbox1"]')
    s.ok("#inbox1 gains class open", has_class(page, "#inbox1", "open"))
    hdr = t(page, '#inbox1 [data-pane="mentions"] .paneheader')
    s.eq('Mentions pane header reads "Comments where I\'m tagged"',
         "Comments where I'm tagged", hdr)
    ents = page.evaluate("""() => [...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
        .map(e => ({b: window.__t(e.querySelector('b')), unread: e.classList.contains('unread')}))""")
    s.eq("three entries with bold entity labels",
         ["Order 413540", "Order 413498", "Order 413330"], [e["b"] for e in ents])
    s.ok("first two entries carry class unread",
         len(ents) == 3 and ents[0]["unread"] and ents[1]["unread"] and not ents[2]["unread"],
         f"unread={[e['unread'] for e in ents]}")
    return s.finish()


def qa_hub_02(page):
    s = Sc(page, "QA-HUB-02", "tab switching")
    load(page); state(page, "s1")
    page.click('#s1 [data-open="inbox1"]')
    s.eq('[data-tab="saved"] label', "★ Saved", t(page, '#inbox1 [data-tab="saved"]'))
    page.click('#inbox1 [data-tab="saved"]')
    s.ok("tab gains class on", has_class(page, '#inbox1 [data-tab="saved"]', "on"))
    vis = page.evaluate("""() => ({saved: window.__vis(document.querySelector('#inbox1 [data-pane="saved"]')),
        mentions: window.__vis(document.querySelector('#inbox1 [data-pane="mentions"]'))})""")
    s.ok("saved pane visible", vis["saved"], f"{vis}")
    s.ok("mentions pane hidden", not vis["mentions"], f"{vis}")
    s.eq("saved pane header", "Comments I saved",
         t(page, '#inbox1 [data-pane="saved"] .paneheader'))
    ents = texts(page, '#inbox1 [data-pane="saved"] .it b')
    s.eq("exactly one entry, Order 413498", ["Order 413498"], ents)
    return s.finish()


def qa_hub_03(page):
    s = Sc(page, "QA-HUB-03", "the star toggle (destructive)")
    load(page); state(page, "s1")
    page.click('#s1 [data-open="inbox1"]')
    js = """() => [...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
        .find(e => window.__t(e.querySelector('b'))==='Order 413540').querySelector('.star')"""
    page.evaluate(js + ".click()")
    s.ok("star gains class on", page.evaluate(f"() => ({js})().classList.contains('on')"))
    page.evaluate(js + ".click()")
    s.ok("clicking again removes the class",
         not page.evaluate(f"() => ({js})().classList.contains('on')"))
    on498 = page.evaluate("""() => [...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
        .find(e => window.__t(e.querySelector('b'))==='Order 413498')
        .querySelector('.star').classList.contains('on')""")
    s.ok("Order 413498 star already class on at load", on498, f"on={on498}")
    return s.finish()


def qa_hub_07(page):
    s = Sc(page, "QA-HUB-07", "(negative) only State 1 wires the dropdown (U-e)")
    load(page)
    for sid in ["s2", "s0", "s2b", "s3", "s4", "shist"]:
        n = page.evaluate("""s => [...document.querySelectorAll('#'+s+' .nav button')]
            .filter(b => (window.__t(b)||'').startsWith('💬 Comments'))
            .filter(b => b.hasAttribute('data-open')).length""", sid)
        s.ok(f"#{sid} Comments button carries no data-open", n == 0, f"count={n}")
        s.ok(f"#{sid} contains no .inboxdd dropdown", count(page, f"#{sid} .inboxdd") == 0,
             f"count={count(page, f'#{sid} .inboxdd')}")
    return s.finish()


# ───────────────────────────── 8.15 QA-CHROME ─────────────────────────────
SECTIONS = ["s0", "s1", "s2", "s2b", "s3", "s4", "shist"]


def qa_chrome_01(page):
    s = Sc(page, "QA-CHROME-01", "global nav present on every state")
    load(page)
    for sid in SECTIONS:
        nav = t(page, f"#{sid} .nav")
        s.ok(f"#{sid} has .nav", nav is not None)
        s.contains(f"#{sid} brand", "SkinSeoul", nav)
        for m in ["Operation AI ▾", "Catalog Management ▾", "OMS Center ▾", "Site Management ▾"]:
            s.contains(f"#{sid} menu {m}", m, nav)
        nb = page.evaluate("""s => [...document.querySelectorAll('#'+s+' .nav button')]
            .filter(b => (window.__t(b)||'').startsWith('💬 Comments')).length""", sid)
        s.ok(f"#{sid} has a 💬 Comments button", nb >= 1, f"count={nb}")
        s.contains(f"#{sid} user chip", "Yongwon Ryu", t(page, f"#{sid} .nav .user"))
        s.contains(f"#{sid} Logout button", "Logout", t(page, f"#{sid} .nav .logout"))
    return s.finish()


def qa_chrome_02(page):
    s = Sc(page, "QA-CHROME-02", "page header and in-page tabs")
    load(page)
    for sid in SECTIONS:
        s.eq(f"#{sid} h2", "WMS - Closing", t(page, f"#{sid} h2"))
        subs = texts(page, f"#{sid} p.sub")
        s.ok(f"#{sid} p.sub reads the subtitle",
             "Barcode-scan verification of today's packed orders" in subs,
             f"page p.sub list={subs}")
        tabs = texts(page, f"#{sid} .pagetabs button")
        s.eq(f"#{sid} .pagetabs buttons", ["Closing", "Closing History"], tabs)
        act = page.evaluate("""s => { const b=document.querySelector('#'+s+' .pagetabs button.on');
            return b && window.__t(b); }""", sid)
        s.eq(f"#{sid} active tab", "Closing History" if sid == "shist" else "Closing", act)
    s.ambiguous("'p.sub reads X' — s0/s1/s2/s2b/s3/s4 each contain 2 p.sub nodes "
                "(the 2nd is the 'Scan list' caption); resolved as membership")
    return s.finish()


def qa_chrome_03(page):
    s = Sc(page, "QA-CHROME-03", "toast slot shape")
    load(page); state(page, "s1")
    s.eq("#s1 .toast span", "✓ Outbound confirmed — YT2618100710108810",
         t(page, "#s1 .toast span"))
    s.eq("#s1 .toast small", "Ready for the next barcode scan", t(page, "#s1 .toast small"))
    s.ok("#s4 .toast has a span and a small",
         count(page, "#s4 .toast span") == 1 and count(page, "#s4 .toast small") == 1,
         f"span={count(page,'#s4 .toast span')} small={count(page,'#s4 .toast small')}")
    s.ok("no .toast.err element exists", count(page, ".toast.err") == 0,
         f"count={count(page,'.toast.err')}")
    return s.finish()


def qa_chrome_04(page):
    s = Sc(page, "QA-CHROME-04", "(negative) wf-bar duplicate tab must not be counted")
    load(page)
    tt = texts(page, '.wf-tab[data-modal="m-process"]')
    s.ok("yields 2 elements", len(tt) == 2, f"count={len(tt)} texts={tt}")
    s.ok("with identical text 'Modal: Process Processing Order'",
         tt == ["Modal: Process Processing Order"] * 2, f"texts={tt}")
    units = page.evaluate("""() => document.querySelectorAll('.legend ol > li').length
        + document.querySelectorAll('.overlay .modal > .dot').length
        + document.querySelectorAll('#s1 .legend > p').length""")
    s.eq("legend-unit count = 22", 22, units)
    tabs = count(page, ".wf-tab")
    s.ambiguous("'the tab count, which would give 23' — the spec never defines what 'the tab "
                f"count' counts. document.querySelectorAll('.wf-tab') = {tabs}, not 23. "
                "(Reconstructible only as 19 li + 1 p + 3 modal TABS = 23, but that method is "
                "not stated.) Clause left unasserted.")
    return s.finish()


def qa_chrome_06(page):
    s = Sc(page, "QA-CHROME-06", "single-screen layout constraint")
    page.set_viewport_size({"width": 1440, "height": 900})
    load(page); state(page, "s1")
    d = page.evaluate("() => ({sw: document.body.scrollWidth, cw: document.body.clientWidth})")
    s.ok("body does not scroll horizontally", d["sw"] <= d["cw"],
         f"body.scrollWidth={d['sw']} body.clientWidth={d['cw']}")
    th = page.evaluate("""() => [...document.querySelectorAll('#s1 table.tbl thead th')]
        .map(x => getComputedStyle(x).display)""")
    s.ok("all 10 thead th rendered, none display:none",
         len(th) == 10 and all(x != "none" for x in th), f"display list={th}")
    trk = page.evaluate("""() => { const c=[...document.querySelectorAll('#s1 table.tbl tbody tr')]
        .map(r => window.__t(r.cells[2]));
      return {cells:c, hasEllipsis: c.some(x => x.includes('…'))}; }""")
    s.ok("longest tracking text fully present with no ellipsis",
         "YT2618100710184356" in trk["cells"] and not trk["hasEllipsis"], f"{trk}")
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
]


def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(viewport={"width": 1440, "height": 900})
        ctx.add_init_script(R4)
        page = ctx.new_page()
        for fn in SCENARIOS:
            try:
                fn(page)
            except Exception as e:
                results.append(dict(id=fn.__name__, title="", verdict="ERROR",
                                    fails=[f"harness exception: {type(e).__name__}: {e}"],
                                    amb=[], unrun=[], npass=0))
        b.close()

    counts = {}
    for r in results:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print(f"{'ID':<18} {'VERDICT':<11} pass  detail")
    for r in results:
        d = ""
        if r["fails"]:
            d = " || ".join(r["fails"])
        elif r["amb"]:
            d = "AMB: " + "; ".join(r["amb"])
        print(f"{r['id']:<18} {r['verdict']:<11} {r['npass']:<5} {d[:400]}")
    print("\nTOTAL", len(results), counts)
    (HERE / "qa-closing-results.json").write_text(json.dumps(results, indent=1, ensure_ascii=False), encoding="utf-8")
if __name__ == "__main__":
    main()
