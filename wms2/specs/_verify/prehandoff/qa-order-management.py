#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-handoff [WF] QA runner — order-management (spec v1.3, 2026-08-03, §8).

Re-baselined 2026-08-03 onto the applied wireframe fixes [WF-15]…[WF-21]
(spec v1.3, §8.0 rule 7): QA-IMP-35, QA-SMP-19/30/31/33, QA-CMT-20,
QA-GBL-09/10 now assert the fixed behaviour, keeping their ids.
Executes all 77 [WF]-tagged scenarios from specs/order-management.md against
wms2/order-management/index.html loaded via file:// (annotations shown).

Harness rules honoured (§8.0):
  1. reload sentinel  window.__qaSentinel='om'
  2. toast identity by node id, display probe, ~2600ms window
  3. colours in rgb() computed form
  4. modal open == classList contains 'open'
  5. byte-exact text after the three declared normalisations (5a <br>→space,
     5b <label> trim, 5c strip descendant .dot text)
  6. modal identity == .modal innerHTML string equality between entry paths
Fresh page load per scenario (strict isolation; every Given starts clean).

Output: JSON report on stdout {passed, failed, results:[...]}.
"""
import json
import pathlib
import sys

from playwright.sync_api import sync_playwright

# Legacy consoles (Windows cp949 / cp1252) otherwise abort the suite mid-run with
# UnicodeEncodeError on the first non-ASCII character, leaving a partial pass count.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover - non-reconfigurable stream
    pass


BASE = pathlib.Path(__file__).resolve().parents[3]  # .../wms2
PAGE_URL = (BASE / "order-management" / "index.html").as_uri()

# ---- byte-exact strings from the spec/wireframe -----------------------------
S_STEP1_HELP = "Standard form from the dev team — Recipient · Contact · Address · Country · SKU · Qty · Campaign name"
S_PIC_HELP = "Default = logged-in user · Recorded as the PIC for this entire import — shown in the order list & RTO"
S_PREVIEW = "Preview — mkt_seeding_batch3.xlsx · 12 rows parsed · 0 errors"
S_NOTCONN = "Cannot import — no connected carrier"
S_BLOCKMSG = ("Cannot import — these countries have no connected carrier: PE. "
              "Ask the fulfillment team to connect them, or remove those rows and upload again.")
S_NOTE_MKT = "On confirm, orders are created as MKT- orders and appear immediately in Ready to be Outbonded (Marketing view) regardless of stock or inbound status."
S_TOAST1 = "✓ Confirmed — 12 orders imported"
S_TOAST1_SUB = "Carrier auto-assigned per country"
S_M3_NOTE = "Multiple assignment periods may exist — select the period(s) to cancel, then confirm. Ended periods are for record only (cannot be cancelled). Cancellation immediately stops new assignments for that period (already-assigned orders are kept)."
S_TOAST2 = "✓ Assignment period cancelled"
S_TOAST2_SUB = "New assignments stopped for the selected period · already-assigned orders kept"
S_TOAST3 = "✓ Sample assignment started"
S_TOAST3_SUB = "All new sales orders from 2026-07-23 10:00 → forever · exactly 1 sample set per order"
S_DROPZONE = "📄 Drag the completed template here or click to upload"
S_M2_HDR = "Sample Assignment ON"
S_M3_HDR = "Cancel Sample Assignment — Current Assignment Periods"
S_LEGEND_P1 = "Global nav · filter bar (dates · Search · PIC · Status · Order#/Tracking# checkboxes · Country · page size) · Merge Orders · Export/Yun Export · 2,818 total · pagination all stay as in the live screen."
S_LEGEND_P2 = "Sample assignment was redesigned 2026-07-23 as a simple ON/OFF (no product-type selection)"
S_RESULTS_TAIL = " results · newest first · click to open the order"

HELPERS = """() => {
window.__own = el => { const c = el.cloneNode(true);
  c.querySelectorAll('.dot').forEach(d => d.remove()); return c.textContent; };
window.__br = el => { let s = '';
  el.childNodes.forEach(n => { if (n.nodeType === 3) s += n.textContent;
    else if (n.nodeName === 'BR') s += ' '; else s += n.textContent; });
  return s; };
window.__cs = (el, p) => getComputedStyle(el)[p];
return true; }"""

SCEN = []


def scen(sid, title):
    def deco(fn):
        SCEN.append((sid, title, fn))
        return fn
    return deco


class C:
    """Check collector for one scenario."""

    def __init__(self):
        self.fails = []

    def eq(self, label, actual, expected):
        if actual != expected:
            self.fails.append({"check": label, "expected": expected, "actual": actual})

    def ok(self, label, cond, actual="", expected=""):
        if not cond:
            self.fails.append({"check": label, "expected": expected or "true",
                               "actual": actual or "false"})

    def has(self, label, haystack, needle):
        if needle not in (haystack or ""):
            self.fails.append({"check": label, "expected": "contains: " + needle,
                               "actual": (haystack or "")[:400]})


def sentinel(page):
    page.evaluate("window.__qaSentinel = 'om'")


def sentinel_ok(page):
    return page.evaluate("window.__qaSentinel === 'om'")


def open_import(page):
    page.click('.filterbar button[data-modal="m-import"]')


def open_m2(page):
    page.click('.actionrow button[data-modal="m-sampleon"]')


def open_m3(page):
    page.click('.actionrow button[data-modal="m-sampleoff"]')


def open_hub(page):
    page.click('.nav button[data-open="inbox1"]')


def hub_search(page, q):
    page.fill('#inbox1 .csearch input', q)


# =========================== Block IMP =======================================

@scen("QA-IMP-01", "Open the import modal from the filter bar")
def imp01(page, c):
    sentinel(page)
    open_import(page)
    r = page.evaluate("""() => ({
      open: document.getElementById('m-import').classList.contains('open'),
      hdr: document.querySelector('#m-import header').textContent,
      toasts: document.querySelectorAll('.gtoast').length,
      sen: window.__qaSentinel })""")
    c.ok("modal open", r["open"])
    c.ok("header starts with 'Marketing Order Import'",
         r["hdr"].startswith("Marketing Order Import"), r["hdr"])
    c.eq("sentinel", r["sen"], "om")
    c.eq("no .gtoast yet", r["toasts"], 0)


@scen("QA-IMP-02", "Open the import modal from the wf-bar — identical content")
def imp02(page, c):
    page.click('.wf-bar button[data-modal="m-import"]')
    c.ok("open via wf-bar", page.evaluate(
        "document.getElementById('m-import').classList.contains('open')"))
    h1 = page.evaluate("document.getElementById('m-import').querySelector('.modal').innerHTML")
    page.click('#m-import header .x')
    open_import(page)
    h2 = page.evaluate("document.getElementById('m-import').querySelector('.modal').innerHTML")
    c.ok("innerHTML identical between entry paths (§8.0 rule 6)", h1 == h2,
         "differs (len %d vs %d)" % (len(h1), len(h2)))


@scen("QA-IMP-03", "Step 1 copy")
def imp03(page, c):
    open_import(page)
    r = page.evaluate("""() => {
      const body = document.querySelector('#m-import .body');
      const b = [...body.querySelectorAll('b')].find(x => x.textContent === '1. Template');
      const btn = [...body.querySelectorAll('button')].find(x => x.textContent === '⬇ Download Template (.xlsx)');
      return { hasLabel: !!b, hasBtn: !!btn,
        btnLine: btn ? btn.classList.contains('btn-line') : false,
        text: body.textContent };
    }""")
    c.ok("bold label '1. Template'", r["hasLabel"])
    c.ok("button '⬇ Download Template (.xlsx)'", r["hasBtn"])
    c.ok("button has class btn-line", r["btnLine"])
    c.has("helper text", r["text"], S_STEP1_HELP)


@scen("QA-IMP-05", "Order Type default state")
def imp05(page, c):
    open_import(page)
    r = page.evaluate("""() => ({
      seedOn: document.getElementById('otChipSeed').classList.contains('on'),
      seedTxt: document.getElementById('otChipSeed').textContent,
      custTxt: document.getElementById('otChipCustom').textContent,
      custOn: document.getElementById('otChipCustom').classList.contains('on'),
      disp: document.getElementById('otCustom').style.display })""")
    c.ok("#otChipSeed has class on", r["seedOn"])
    c.eq("#otChipSeed text", r["seedTxt"], "Influencer Seeding")
    c.eq("#otChipCustom text", r["custTxt"], "✎ Custom")
    c.ok("#otChipCustom has no on class", not r["custOn"])
    c.eq("#otCustom display", r["disp"], "none")


@scen("QA-IMP-06", "Order Type custom toggle and focus")
def imp06(page, c):
    open_import(page)
    page.click('#otChipCustom')
    r = page.evaluate("""() => ({
      custOn: document.getElementById('otChipCustom').classList.contains('on'),
      seedOn: document.getElementById('otChipSeed').classList.contains('on'),
      disp: document.getElementById('otCustom').style.display,
      ph: document.getElementById('otCustom').placeholder,
      focused: document.activeElement === document.getElementById('otCustom') })""")
    c.ok("#otChipCustom on", r["custOn"])
    c.ok("#otChipSeed not on", not r["seedOn"])
    c.eq("#otCustom display", r["disp"], "inline-block")
    c.eq("placeholder", r["ph"], "Enter type (e.g. Pop-up event giveaway)")
    c.ok("focus moved into #otCustom", r["focused"])


@scen("QA-IMP-07", "Toggling back hides the custom input but keeps its value")
def imp07(page, c):
    open_import(page)
    page.click('#otChipCustom')
    page.fill('#otCustom', 'Pop-up event giveaway')
    page.click('#otChipSeed')
    r = page.evaluate("""() => ({
      disp: document.getElementById('otCustom').style.display,
      seedOn: document.getElementById('otChipSeed').classList.contains('on'),
      val: document.getElementById('otCustom').value })""")
    c.eq("#otCustom display", r["disp"], "none")
    c.ok("#otChipSeed on", r["seedOn"])
    c.eq("value retained", r["val"], "Pop-up event giveaway")


@scen("QA-IMP-08", "PIC defaults and helper copy")
def imp08(page, c):
    open_import(page)
    r = page.evaluate("""() => {
      const sel = document.querySelector('#m-import select');
      return { opts: [...sel.options].map(o => o.textContent),
        selTxt: sel.options[sel.selectedIndex].textContent,
        btnTxt: document.getElementById('picCustomBtn').textContent,
        disp: document.getElementById('picCustomIn').style.display,
        ph: document.getElementById('picCustomIn').placeholder,
        body: document.querySelector('#m-import .body').textContent };
    }""")
    c.eq("options", r["opts"], ["Yongwon Ryu (me)", "Harshit", "EuJin", "Adinda"])
    c.eq("selected", r["selTxt"], "Yongwon Ryu (me)")
    c.eq("#picCustomBtn text", r["btnTxt"], "✎ Custom")
    c.eq("#picCustomIn display", r["disp"], "none")
    c.eq("#picCustomIn placeholder", r["ph"], "Enter PIC name")
    c.has("helper text", r["body"], S_PIC_HELP)


@scen("QA-IMP-09", "PIC custom toggle and focus")
def imp09(page, c):
    open_import(page)
    page.click('#picCustomBtn')
    r1 = page.evaluate("""() => ({
      disp: document.getElementById('picCustomIn').style.display,
      focused: document.activeElement === document.getElementById('picCustomIn') })""")
    c.eq("display after first click", r1["disp"], "inline-block")
    c.ok("focus moved into #picCustomIn", r1["focused"])
    page.click('#picCustomBtn')
    c.eq("display after second click",
         page.evaluate("document.getElementById('picCustomIn').style.display"), "none")


@scen("QA-IMP-10", "Upload step copy")
def imp10(page, c):
    open_import(page)
    r = page.evaluate("""() => {
      const body = document.querySelector('#m-import .body');
      const b = [...body.querySelectorAll('b')].find(x => x.textContent === '4. Upload');
      return { hasLabel: !!b,
        dz: document.querySelector('#m-import .dropzone').textContent };
    }""")
    c.ok("bold label '4. Upload'", r["hasLabel"])
    c.eq("dropzone text", r["dz"], S_DROPZONE)


@scen("QA-IMP-11", "Preview header format")
def imp11(page, c):
    open_import(page)
    r = page.evaluate("""() => {
      const el = document.querySelector('#m-import table.tbl').previousElementSibling;
      return { tag: el.tagName, txt: el.textContent };
    }""")
    c.eq("element is <b>", r["tag"], "B")
    c.eq("preview header", r["txt"], S_PREVIEW)


@scen("QA-IMP-12", "Preview table headers")
def imp12(page, c):
    open_import(page)
    r = page.evaluate("""() => {
      const ths = [...document.querySelectorAll('#m-import thead th')];
      return { n: ths.length, own: ths.map(t => window.__own(t)),
        raw7: ths.length === 7 ? ths[6].textContent : null };
    }""")
    c.eq("thead th length", r["n"], 7)
    c.eq("own texts (rule 5c)", r["own"],
         ["Recipient", "Country", "SKU", "Product Name", "Qty", "Campaign", "Carrier (auto)"])
    c.eq("raw textContent of 7th cell", r["raw7"], "Carrier (auto)M1b")


@scen("QA-IMP-13", "Brand-bold product names [G-6]")
def imp13(page, c):
    open_import(page)
    rows = page.evaluate("""() =>
      [...document.querySelectorAll('#m-import tbody tr')]
        .filter(tr => !tr.querySelector('td[colspan]'))
        .map(tr => tr.cells[3].innerHTML)""")
    c.has("row 1", rows[0], "<b>Dr.Jart+</b> Cicapair Gentle Cleansing Foam")
    c.has("row 2", rows[1], "<b>Dr.Jart+</b> Cicapair Sleepair Mask")
    c.has("row 3", rows[2], "<b>innisfree</b> Green Tea Seed Hyaluronic Serum")


@scen("QA-IMP-14", "Connected-carrier rendering [L-M1b]")
def imp14(page, c):
    open_import(page)
    r = page.evaluate("""() =>
      [...document.querySelectorAll('#m-import tbody tr')]
        .filter(tr => !tr.querySelector('td[colspan]') && tr.cells[1].textContent === 'GB')
        .map(tr => { const td = tr.cells[tr.cells.length - 1];
          return { txt: td.textContent, col: window.__cs(td, 'color'),
                   fw: window.__cs(td, 'fontWeight') }; })""")
    c.ok("at least one GB row", len(r) > 0)
    for i, cell in enumerate(r):
        c.eq("GB row %d carrier" % (i + 1), cell["txt"], "YunExpress")
        c.eq("GB row %d colour" % (i + 1), cell["col"], "rgb(25, 135, 84)")
        c.eq("GB row %d font-weight" % (i + 1), cell["fw"], "700")


@scen("QA-IMP-15", "(neg) Unconnected carrier blocks the whole file [E-7] [G-17]")
def imp15(page, c):
    open_import(page)
    probe = """() => {
      const tr = [...document.querySelectorAll('#m-import tbody tr')]
        .find(t => !t.querySelector('td[colspan]') && t.cells[0].textContent === 'Lucia Ramos');
      const td = document.getElementById('mktPECell');
      const blk = document.getElementById('mktBlock');
      const btn = document.getElementById('mktConfirm');
      return { country: tr.cells[1].textContent, txt: td.textContent,
        col: window.__cs(td, 'color'), fw: window.__cs(td, 'fontWeight'),
        blk: window.__cs(blk, 'display'), blkTxt: blk.textContent.trim(),
        dis: btn.hasAttribute('disabled'), aria: btn.getAttribute('aria-disabled') };
    }"""
    # default preview = clean file: PE resolves, nothing is blocked
    a = page.evaluate(probe)
    c.eq("country", a["country"], "PE")
    c.eq("clean: carrier", a["txt"], "YunExpress")
    c.eq("clean: colour", a["col"], "rgb(25, 135, 84)")
    c.eq("clean: no block banner", a["blk"], "none")
    c.ok("clean: #mktConfirm enabled", not a["dis"] and a["aria"] != "true")

    # WF-16b toggle -> unconnected preview: the file is refused in full [G-17].
    # The toggle lives on the wf-bar, so the modal must be closed to reach it.
    page.click('#m-import [data-close]')
    page.click("#impPreviewToggle")
    open_import(page)
    b = page.evaluate(probe)
    c.eq("blocked: red string", b["txt"], S_NOTCONN)
    c.eq("blocked: colour", b["col"], "rgb(220, 53, 69)")
    c.eq("blocked: font-weight", b["fw"], "700")
    c.eq("blocked: banner shown", b["blk"], "block")
    c.eq("blocked: banner copy", b["blkTxt"], S_BLOCKMSG)
    c.ok("blocked: #mktConfirm disabled", b["dis"] and b["aria"] == "true")


@scen("QA-IMP-16", "Confirm button label format")
def imp16(page, c):
    open_import(page)
    r = page.evaluate("""() => ({
      txt: document.getElementById('mktConfirm').textContent,
      cls: document.getElementById('mktConfirm').classList.contains('btn-mkt') })""")
    c.eq("label", r["txt"], "Confirm Import (12 orders)")
    c.ok("class btn-mkt", r["cls"])


@scen("QA-IMP-17", "Confirm toast text, colour, dismissal and no reload [E-43][E-45]")
def imp17(page, c):
    sentinel(page)
    open_import(page)
    page.click('#mktConfirm')
    r = page.evaluate("""() => {
      const t = document.getElementById('gtoast');
      return { modalOpen: document.getElementById('m-import').classList.contains('open'),
        exists: !!t, disp: t ? window.__cs(t, 'display') : null,
        pos: t ? window.__cs(t, 'position') : null,
        top: t ? window.__cs(t, 'top') : null, right: t ? window.__cs(t, 'right') : null,
        bg: t ? window.__cs(t, 'backgroundColor') : null,
        first: t ? t.firstChild.textContent : null,
        small: t ? (t.querySelector('small') || {}).textContent : null };
    }""")
    c.ok("modal closed", not r["modalOpen"])
    c.ok("#gtoast exists", r["exists"])
    c.ok("display not none", r["disp"] != "none", r["disp"])
    c.eq("position", r["pos"], "fixed")
    c.eq("top", r["top"], "16px")
    c.eq("right", r["right"], "16px")
    c.eq("background", r["bg"], "rgb(25, 135, 84)")
    c.eq("title text node", r["first"], S_TOAST1)
    c.eq("subtext", r["small"], S_TOAST1_SUB)
    try:
        page.wait_for_function(
            "document.getElementById('gtoast').style.display === 'none'", timeout=4000)
    except Exception:
        c.ok("auto-dismiss ~2600ms", False, "still visible after 4s")
    c.ok("sentinel — no reload", sentinel_ok(page))


@scen("QA-IMP-18", "Modal note copy (BR-1)")
def imp18(page, c):
    open_import(page)
    c.eq("note text", page.evaluate(
        "document.querySelector('#m-import .note.mkt').textContent"), S_NOTE_MKT)


@scen("QA-IMP-19", "(neg) No stock-error copy anywhere in the modal [E-20]")
def imp19(page, c):
    open_import(page)
    r = page.evaluate("""() => {
      const all = document.getElementById('m-import').textContent.toLowerCase();
      const note = document.querySelector('#m-import .note.mkt').textContent.toLowerCase();
      const count = (s, n) => s.split(n).length - 1;
      return { oos: all.includes('out of stock'), niw: all.includes('not in the warehouse'),
        ins: all.includes('insufficient'),
        stockAll: count(all, 'stock'), stockNote: count(note, 'stock') };
    }""")
    c.ok("no 'out of stock'", not r["oos"])
    c.ok("no 'not in the warehouse'", not r["niw"])
    c.ok("no 'insufficient'", not r["ins"])
    c.ok("every 'stock' occurrence is inside .note.mkt",
         r["stockAll"] == r["stockNote"] and r["stockNote"] >= 1,
         "modal:%d note:%d" % (r["stockAll"], r["stockNote"]))


@scen("QA-IMP-20", "(neg) No print, scan, or carrier-picker affordance in the modal")
def imp20(page, c):
    open_import(page)
    r = page.evaluate("""() => ({
      printBtns: [...document.querySelectorAll('#m-import button')]
        .filter(b => b.textContent.includes('Print')).length,
      fileInputs: [...document.querySelectorAll('#m-import input')]
        .filter(i => i.type === 'file').length,
      selects: document.querySelectorAll('#m-import select').length,
      selFirst: (document.querySelector('#m-import select') || { options: [{}] })
        .options[0].textContent })""")
    c.eq("no Print button", r["printBtns"], 0)
    c.eq("no file input", r["fileInputs"], 0)
    c.eq("exactly one select (PIC picker)", r["selects"], 1)
    c.eq("that select is the PIC picker", r["selFirst"], "Yongwon Ryu (me)")


@scen("QA-IMP-35", "Preview collapse row spans the full table — re-baselined on [WF-15], applied 2026-08-03")
def imp35(page, c):
    open_import(page)
    r = page.evaluate("""() => {
      const tds = [...document.querySelectorAll('#m-import tbody td[colspan]')];
      return { n: tds.length, txt: tds[0] ? tds[0].textContent : null,
        span: tds[0] ? tds[0].getAttribute('colspan') : null,
        ths: document.querySelectorAll('#m-import thead th').length };
    }""")
    c.eq("exactly one colspan cell", r["n"], 1)
    c.eq("collapse text", r["txt"], "⋯ +8 more rows")
    c.eq("colspan attribute is 7 ([WF-15] applied)", r["span"], "7")
    c.eq("thead th length", r["ths"], 7)
    c.eq("colspan equals the header count — the row spans the full table",
         r["span"], str(r["ths"]))


@scen("QA-IMP-36", "Preview row arithmetic matches the header count")
def imp36(page, c):
    open_import(page)
    r = page.evaluate("""() => {
      const rows = [...document.querySelectorAll('#m-import tbody tr')];
      const named = rows.filter(t => !t.querySelector('td[colspan]'))
        .map(t => t.cells[0].textContent);
      const coll = rows.find(t => t.querySelector('td[colspan]'));
      return { named, collTxt: coll ? coll.textContent : null,
        hdr: document.querySelector('#m-import table.tbl').previousElementSibling.textContent };
    }""")
    c.eq("named rows", r["named"],
         ["Svetlana Jaloba", "Zoe Garner", "Mariana Maheha", "Lucia Ramos"])
    c.eq("collapse row text", r["collTxt"], "⋯ +8 more rows")
    c.ok("4 + 8 = 12 consistent with header", "12 rows parsed" in r["hdr"], r["hdr"])


@scen("QA-IMP-37", "(neg) The dropzone is inert in the mock (demo limitation)")
def imp37(page, c):
    open_import(page)
    fired = []
    page.on("filechooser", lambda fc: fired.append(1))
    before = page.evaluate("document.querySelector('#m-import table.tbl').outerHTML")
    page.click('#m-import .dropzone')
    page.wait_for_timeout(300)
    after = page.evaluate("document.querySelector('#m-import table.tbl').outerHTML")
    c.eq("no file picker opened", len(fired), 0)
    c.eq("no input[type=file] anywhere",
         page.evaluate("document.querySelectorAll('input[type=file]').length"), 0)
    c.ok("preview unchanged", before == after)


@scen("QA-IMP-38", "Modal geometry and dismissal controls")
def imp38(page, c):
    open_import(page)
    r = page.evaluate("""() => {
      const m = document.querySelector('#m-import .modal');
      const foot = [...document.querySelectorAll('#m-import .foot button')];
      return { modal: m.classList.contains('modal'), wide: m.classList.contains('wide'),
        maxw: window.__cs(m, 'maxWidth'),
        x: !!document.querySelector('#m-import header .x[data-close]'),
        xTxt: (document.querySelector('#m-import header .x[data-close]') || {}).textContent,
        footN: foot.length, footTxt: foot.map(b => b.textContent) };
    }""")
    c.ok("classes modal wide", r["modal"] and r["wide"])
    c.eq("max-width", r["maxw"], "720px")
    c.ok("header ✕ control", r["x"] and r["xTxt"] == "✕")
    c.eq("footer button count", r["footN"], 2)
    c.eq("footer buttons", r["footTxt"], ["Cancel", "Confirm Import (12 orders)"])


@scen("QA-IMP-39", "(neg) Repeated confirms reuse one toast node")
def imp39(page, c):
    open_import(page)
    page.click('#mktConfirm')
    open_import(page)
    page.click('#mktConfirm')
    r = page.evaluate("""() => {
      const ts = [...document.querySelectorAll('.gtoast')];
      return { n: ts.length, ids: ts.map(t => t.id) };
    }""")
    c.eq(".gtoast count", r["n"], 1)
    c.eq("id", r["ids"], ["gtoast"])


# =========================== Block SMP =======================================

@scen("QA-SMP-01", "ON button opens M2")
def smp01(page, c):
    sentinel(page)
    r0 = page.evaluate("""() => {
      const b = document.querySelector('.actionrow button[data-modal="m-sampleon"]');
      return { txt: b.textContent, green: b.classList.contains('btn-green') };
    }""")
    c.eq("button label", r0["txt"], "Sample Assignment ON")
    c.ok("class btn-green", r0["green"])
    open_m2(page)
    r = page.evaluate("""() => ({
      open: document.getElementById('m-sampleon').classList.contains('open'),
      hdr: document.querySelector('#m-sampleon header').textContent,
      sen: window.__qaSentinel })""")
    c.ok("modal open", r["open"])
    c.ok("header starts with 'Sample Assignment ON'", r["hdr"].startswith(S_M2_HDR), r["hdr"])
    c.eq("sentinel", r["sen"], "om")


@scen("QA-SMP-02", "Target radios")
def smp02(page, c):
    open_m2(page)
    r = page.evaluate("""() => {
      const radios = [...document.querySelectorAll('#m-sampleon input[name="samptarget"]')];
      const grp = [...document.querySelectorAll('#m-sampleon b')]
        .find(b => b.textContent === 'Assignment Target');
      return { grp: !!grp, n: radios.length, first: radios[0] ? radios[0].checked : null,
        labels: radios.map(x => x.closest('label').textContent.trim()) };
    }""")
    c.ok("bold group label 'Assignment Target'", r["grp"])
    c.eq("radio count", r["n"], 2)
    c.ok("first checked", r["first"] is True)
    c.eq("labels (rule 5b)", r["labels"],
         ["All new orders in this period", "Selected orders only (2)"])


@scen("QA-SMP-03", "Period fields and forever default")
def smp03(page, c):
    open_m2(page)
    r = page.evaluate("""() => {
      const grp = [...document.querySelectorAll('#m-sampleon b')]
        .find(b => b.textContent === 'Assignment Period');
      const sep = [...document.querySelectorAll('#m-sampleon span')]
        .some(s => s.textContent === '~');
      return { grp: !!grp,
        sd: document.getElementById('sampStartDate').value,
        st: document.getElementById('sampStartTime').value,
        sep,
        edPh: document.getElementById('sampEndDate').placeholder,
        etPh: document.getElementById('sampEndTime').placeholder,
        fv: document.getElementById('sampForever').checked,
        fvLabel: document.getElementById('sampForever').closest('label').textContent.trim() };
    }""")
    c.ok("bold group label 'Assignment Period'", r["grp"])
    c.eq("start date", r["sd"], "2026-07-23")
    c.eq("start time", r["st"], "10:00")
    c.ok("~ separator", r["sep"])
    c.eq("end date placeholder", r["edPh"], "End date")
    c.eq("end time placeholder", r["etPh"], "Time")
    c.ok("forever checked", r["fv"])
    c.eq("forever label (rule 5b)", r["fvLabel"], "forever (no end date)")


@scen("QA-SMP-04", "(neg) Modal note and absence of any sample-type picker")
def smp04(page, c):
    open_m2(page)
    r = page.evaluate("""() => ({
      note: document.querySelector('#m-sampleon .note').textContent,
      selects: document.querySelectorAll('#m-sampleon select').length })""")
    c.has("note", r["note"], "product type is not selected")
    c.has("note", r["note"], "exactly 1 sample set per order")
    c.eq("zero <select> elements (BR-6)", r["selects"], 0)


@scen("QA-SMP-05", "Footer buttons")
def smp05(page, c):
    open_m2(page)
    r = page.evaluate("""() =>
      [...document.querySelectorAll('#m-sampleon .foot button')]
        .map(b => ({ txt: b.textContent, gray: b.classList.contains('btn-gray'),
                     green: b.classList.contains('btn-green') }))""")
    c.eq("count", len(r), 2)
    c.ok("grey Cancel", r[0]["txt"] == "Cancel" and r[0]["gray"], json.dumps(r[0]))
    c.ok("green Start Assignment (ON)",
         r[1]["txt"] == "Start Assignment (ON)" and r[1]["green"], json.dumps(r[1]))


@scen("QA-SMP-15", "Cancel button opens M3")
def smp15(page, c):
    r0 = page.evaluate(
        "document.querySelector('.actionrow button[data-modal=\"m-sampleoff\"]').textContent")
    c.eq("button label", r0, "Cancel Sample Assignment")
    open_m3(page)
    r = page.evaluate("""() => ({
      open: document.getElementById('m-sampleoff').classList.contains('open'),
      hdr: document.querySelector('#m-sampleoff header').textContent })""")
    c.ok("modal open", r["open"])
    c.ok("header starts with M3 title", r["hdr"].startswith(S_M3_HDR), r["hdr"])


@scen("QA-SMP-16", "M3 table content")
def smp16(page, c):
    open_m3(page)
    r = page.evaluate("""() => {
      const ths = [...document.querySelectorAll('#m-sampleoff thead th')].map(t => t.textContent);
      const rows = [...document.querySelectorAll('#m-sampleoff tbody tr')].map(tr => ({
        period: tr.cells[1].textContent, periodHtml: tr.cells[1].innerHTML,
        target: tr.cells[2].textContent, status: tr.cells[3].textContent }));
      return { ths, rows };
    }""")
    c.eq("headers", r["ths"], ["", "Assignment Period", "Target", "Status"])
    c.eq("row1 period", r["rows"][0]["period"], "2026-07-01 09:00 → forever")
    c.has("row1 forever in <b>", r["rows"][0]["periodHtml"], "<b>forever</b>")
    c.eq("row1 target/status", [r["rows"][0]["target"], r["rows"][0]["status"]],
         ["All new orders", "Active"])
    c.eq("row2", [r["rows"][1]["period"], r["rows"][1]["target"], r["rows"][1]["status"]],
         ["2026-07-15 00:00 → 2026-07-20 23:59", "34 selected orders", "Active"])
    c.eq("row3", [r["rows"][2]["period"], r["rows"][2]["target"], r["rows"][2]["status"]],
         ["2026-06-01 00:00 → 2026-06-30 23:59", "All new orders", "Ended"])


@scen("QA-SMP-17", "(neg) Ended row has no checkbox element [E-27]")
def smp17(page, c):
    open_m3(page)
    r = page.evaluate("""() =>
      [...document.querySelectorAll('#m-sampleoff tbody tr')].map(tr => ({
        status: tr.cells[3].textContent,
        boxes: tr.querySelectorAll('input[type=checkbox]').length }))""")
    for row in r:
        if row["status"] == "Ended":
            c.eq("Ended row checkbox count", row["boxes"], 0)
        else:
            c.eq("%s row checkbox count" % row["status"], row["boxes"], 1)


@scen("QA-SMP-18", "M3 note copy")
def smp18(page, c):
    open_m3(page)
    c.eq("note", page.evaluate(
        "document.querySelector('#m-sampleoff .note').textContent"), S_M3_NOTE)


@scen("QA-SMP-19", "Confirm dialog precedes the cancel toast; text and no reload — re-baselined on [WF-17], applied 2026-08-03")
def smp19(page, c):
    sentinel(page)
    open_m3(page)
    # Step 1 — the cancel button opens the confirm overlay and toasts nothing yet.
    page.click('#sampCancelBtn')
    r1 = page.evaluate("""() => {
      const cf = document.getElementById('m-sampcancel-confirm');
      const hd = cf ? cf.querySelector('header') : null;
      return { m3open: document.getElementById('m-sampleoff').classList.contains('open'),
        confirmExists: !!cf,
        confirmOpen: cf ? cf.classList.contains('open') : false,
        hdrFirst: hd ? hd.childNodes[0].textContent : null,
        t2: !!document.getElementById('gtoast2') };
    }""")
    c.ok("#m-sampleoff still has class open", r1["m3open"], "already closed")
    c.ok("confirm overlay #m-sampcancel-confirm exists", r1["confirmExists"])
    c.ok("#m-sampcancel-confirm gains class open", r1["confirmOpen"])
    c.eq("confirm header first text node (count follows the selection)",
         r1["hdrFirst"], "Cancel 1 assignment period(s)?")
    c.ok("no node with id gtoast2 exists yet", not r1["t2"],
         "gtoast2 fired before the confirm step")
    # Step 2 — confirming with #sampConfirmGo closes both overlays and fires the toast.
    page.click('#sampConfirmGo')
    r2 = page.evaluate("""() => {
      const t = document.getElementById('gtoast2');
      return { confirmOpen: document.getElementById('m-sampcancel-confirm').classList.contains('open'),
        m3open: document.getElementById('m-sampleoff').classList.contains('open'),
        exists: !!t, visible: t ? window.__cs(t, 'display') !== 'none' : false,
        first: t ? t.firstChild.textContent : null,
        small: t && t.querySelector('small') ? t.querySelector('small').textContent : null,
        sen: window.__qaSentinel };
    }""")
    c.ok("#m-sampcancel-confirm loses class open", not r2["confirmOpen"])
    c.ok("#m-sampleoff loses class open", not r2["m3open"])
    c.ok("#gtoast2 visible", r2["exists"] and r2["visible"],
         "gtoast2 %s" % ("absent" if not r2["exists"] else "hidden"))
    if r2["exists"]:
        c.eq("toast title", r2["first"], S_TOAST2)
        c.eq("toast subtext", r2["small"], S_TOAST2_SUB)
    c.eq("sentinel", r2["sen"], "om")


@scen("QA-SMP-28", "M2 opens from the wf-bar — identical content")
def smp28(page, c):
    page.click('.wf-bar button[data-modal="m-sampleon"]')
    c.ok("open via wf-bar", page.evaluate(
        "document.getElementById('m-sampleon').classList.contains('open')"))
    h1 = page.evaluate("document.getElementById('m-sampleon').querySelector('.modal').innerHTML")
    page.click('#m-sampleon header .x')
    open_m2(page)
    h2 = page.evaluate("document.getElementById('m-sampleon').querySelector('.modal').innerHTML")
    c.ok("innerHTML identical (§8.0 rule 6)", h1 == h2,
         "differs (len %d vs %d)" % (len(h1), len(h2)))
    r = page.evaluate("""() => {
      const radios = [...document.querySelectorAll('#m-sampleon input[name="samptarget"]')];
      return { n: radios.length, first: radios[0].checked };
    }""")
    c.eq("QA-SMP-02 radios hold", [r["n"], r["first"]], [2, True])


@scen("QA-SMP-29", "M3 opens from the wf-bar — identical content")
def smp29(page, c):
    page.click('.wf-bar button[data-modal="m-sampleoff"]')
    c.ok("open via wf-bar", page.evaluate(
        "document.getElementById('m-sampleoff').classList.contains('open')"))
    h1 = page.evaluate("document.getElementById('m-sampleoff').querySelector('.modal').innerHTML")
    page.click('#m-sampleoff header .x')
    open_m3(page)
    h2 = page.evaluate("document.getElementById('m-sampleoff').querySelector('.modal').innerHTML")
    c.ok("innerHTML identical (§8.0 rule 6)", h1 == h2,
         "differs (len %d vs %d)" % (len(h1), len(h2)))


@scen("QA-SMP-30", "Start Assignment (ON) shows the specified toast — re-baselined on [WF-16], applied 2026-08-03")
def smp30(page, c):
    open_m2(page)
    c.eq("no .gtoast before", page.evaluate(
        "document.querySelectorAll('.gtoast').length"), 0)
    d = page.evaluate("""() => ({
      target: document.querySelector('#m-sampleon input[name="samptarget"]').checked,
      sd: document.getElementById('sampStartDate').value,
      st: document.getElementById('sampStartTime').value,
      fv: document.getElementById('sampForever').checked })""")
    c.ok("default target is 'All new orders in this period'", d["target"])
    c.eq("default start date", d["sd"], "2026-07-23")
    c.eq("default start time", d["st"], "10:00")
    c.ok("forever checked by default", d["fv"])
    page.click('#m-sampleon .foot button.btn-green')
    r = page.evaluate("""() => {
      const btn = document.querySelector('#m-sampleon .foot button.btn-green');
      const t = document.getElementById('gtoast3');
      return { m2open: document.getElementById('m-sampleon').classList.contains('open'),
        btnId: btn.id || '(none)', exists: !!t,
        cls: t ? t.classList.contains('gtoast') : false,
        visible: t ? window.__cs(t, 'display') !== 'none' : false,
        first: t ? t.firstChild.textContent : null,
        small: t && t.querySelector('small') ? t.querySelector('small').textContent : null };
    }""")
    c.eq("the green footer button carries id sampStartBtn", r["btnId"], "sampStartBtn")
    c.ok("modal loses class open", not r["m2open"])
    c.ok("#gtoast3 exists", r["exists"], "gtoast3 absent (no toast fired)")
    c.ok("#gtoast3 carries class gtoast", r["cls"])
    c.ok("#gtoast3 is visible", r["visible"])
    if r["exists"]:
        c.eq("toast title (byte-exact §3.6.5)", r["first"], S_TOAST3)
        c.eq("toast subtext (byte-exact §3.6.5)", r["small"], S_TOAST3_SUB)


@scen("QA-SMP-31", "(neg) Zero selection disables cancel on the wireframe — re-baselined on [WF-17], applied 2026-08-03")
def smp31(page, c):
    open_m3(page)
    page.uncheck('#m-sampleoff tbody tr:nth-child(1) input[type=checkbox]')
    c.eq("zero checkboxes checked", page.evaluate(
        "[...document.querySelectorAll('#m-sampleoff tbody input[type=checkbox]')].filter(b => b.checked).length"), 0)
    disabled = page.evaluate("document.getElementById('sampCancelBtn').disabled")
    page.evaluate("document.getElementById('sampCancelBtn').click()")
    r = page.evaluate("""() => ({
      confirmOpen: (document.getElementById('m-sampcancel-confirm') || { classList: { contains: () => false } })
        .classList.contains('open'),
      t2: !!document.getElementById('gtoast2') })""")
    c.ok("#sampCancelBtn.disabled === true at zero selection", disabled,
         "button is enabled at zero selection")
    c.ok("#m-sampcancel-confirm does not gain class open", not r["confirmOpen"],
         "confirm overlay opened from a blocked click")
    c.ok("no #gtoast2 node is created", not r["t2"],
         "gtoast2 was created by a blocked click")
    # The gate tracks the selection, not the page load: re-checking row 1 re-enables it.
    page.check('#m-sampleoff tbody tr:nth-child(1) input[type=checkbox]')
    c.ok("re-checking row 1 re-enables the button", page.evaluate(
        "document.getElementById('sampCancelBtn').disabled") is False,
        "button stayed disabled after re-checking")


@scen("QA-SMP-32", "M3 default checkbox states")
def smp32(page, c):
    open_m3(page)
    r = page.evaluate("""() => {
      const rows = [...document.querySelectorAll('#m-sampleoff tbody tr')];
      return { r1: rows[0].querySelector('input[type=checkbox]')?.checked ?? null,
        r2: rows[1].querySelector('input[type=checkbox]')?.checked ?? null,
        r3n: rows[2].querySelectorAll('input[type=checkbox]').length,
        total: document.querySelectorAll('#m-sampleoff tbody input[type=checkbox]').length };
    }""")
    c.ok("row1 checked", r["r1"] is True)
    c.ok("row2 unchecked", r["r2"] is False)
    c.eq("row3 has none", r["r3n"], 0)
    c.eq("total checkbox elements", r["total"], 2)


@scen("QA-SMP-33", "(neg) forever clears and disables the end fields — re-baselined on [WF-19], applied 2026-08-03")
def smp33(page, c):
    open_m2(page)
    probe = """() => ({
      fv: document.getElementById('sampForever').checked,
      edDis: document.getElementById('sampEndDate').disabled,
      etDis: document.getElementById('sampEndTime').disabled,
      edVal: document.getElementById('sampEndDate').value,
      etVal: document.getElementById('sampEndTime').value })"""
    r = page.evaluate(probe)
    c.ok("forever is checked (shipped default)", r["fv"])
    c.ok("End date input is disabled", r["edDis"], "sampEndDate.disabled === false")
    c.ok("Time input is disabled", r["etDis"], "sampEndTime.disabled === false")
    c.eq("End date value is empty", r["edVal"], "")
    c.eq("Time value is empty", r["etVal"], "")
    # Unchecking re-enables both.
    page.uncheck('#sampForever')
    r2 = page.evaluate(probe)
    c.ok("unchecking forever re-enables End date", not r2["edDis"])
    c.ok("unchecking forever re-enables Time", not r2["etDis"])
    # forever wins over a previously typed end value: re-checking clears and disables.
    page.fill('#sampEndDate', '2026-08-31')
    page.fill('#sampEndTime', '18:00')
    page.check('#sampForever')
    r3 = page.evaluate(probe)
    c.ok("re-checking forever disables End date again", r3["edDis"])
    c.ok("re-checking forever disables Time again", r3["etDis"])
    c.eq("re-checking forever clears the typed End date", r3["edVal"], "")
    c.eq("re-checking forever clears the typed Time", r3["etVal"], "")


@scen("QA-SMP-34", "Cancel toast uses its own node")
def smp34(page, c):
    open_m3(page)
    page.click('#sampCancelBtn')
    # Baseline behaviour change: #sampCancelBtn alone no longer fires the toast —
    # a confirm dialog now intervenes; route through it so the cancel toast fires.
    if page.evaluate(
            "(document.getElementById('m-sampcancel-confirm')||{classList:{contains:()=>false}}).classList.contains('open')"):
        page.click('#sampConfirmGo')
    r = page.evaluate("""() => {
      const t2 = document.getElementById('gtoast2');
      const t1 = document.getElementById('gtoast');
      return { exists: !!t2, cls: t2 ? t2.classList.contains('gtoast') : false,
        distinct: !t1 || t1 !== t2 };
    }""")
    c.ok("node #gtoast2 exists", r["exists"])
    c.ok("carries class gtoast", r["cls"])
    c.ok("separate from #gtoast", r["distinct"])


# =========================== Block LST =======================================

@scen("QA-LST-01", "Placeholder contract text")
def lst01(page, c):
    r = page.evaluate("""() => {
      const el = [...document.querySelectorAll('.pagepad div.anno')]
        .find(d => (d.getAttribute('style') || '').includes('dashed'));
      if (!el) return null;
      const line1 = window.__own(el.children[0]);
      const dot = el.querySelector('.dot');
      return { line1, sub: el.children[1].textContent, dot: dot ? dot.textContent : null };
    }""")
    c.ok("dashed placeholder exists", r is not None)
    if r:
        c.eq("line 1 (rule 5c)", r["line1"], "Order list table — same as the current admin (omitted)")
        c.has("sub-line", r["sub"],
              "Default columns ↔ Columns toggle view, 2,818 total, and pagination — all unchanged.")
        c.has("sub-line", r["sub"], "MKT- marketing orders")
        c.eq("inline dot renders 4", r["dot"], "4")


@scen("QA-LST-02", "MKT style tokens exist")
def lst02(page, c):
    r = page.evaluate("""() => {
      const rs = getComputedStyle(document.documentElement);
      const rules = [];
      for (const sh of document.styleSheets)
        try { for (const rr of sh.cssRules) rules.push(rr.cssText); } catch (e) {}
      const find = sel => rules.find(t => t.startsWith(sel + ' {') || t.startsWith(sel + '{')) || '';
      return { mkt: rs.getPropertyValue('--mkt').trim(),
        soft: rs.getPropertyValue('--mkt-soft').trim(),
        rMkt: find('.tbl tr.mkt'), rMktHover: find('.tbl tr.mkt:hover'),
        rHover: find('.tbl tr:hover'), rBadge: find('.mkt-badge') };
    }""")
    c.eq("--mkt", r["mkt"], "#7C3AED")
    c.eq("--mkt-soft", r["soft"], "#F3EEFF")
    c.has("tr.mkt background", r["rMkt"], "var(--mkt-soft)")
    c.ok("tr.mkt:hover background #EBE1FF (either serialised form, rule 5)",
         ("#EBE1FF" in r["rMktHover"]) or ("rgb(235, 225, 255)" in r["rMktHover"]),
         r["rMktHover"])
    c.has("tr:hover background", r["rHover"], "var(--blue-soft)")
    c.has(".mkt-badge background", r["rBadge"], "var(--mkt)")
    c.ok(".mkt-badge color #fff", ("#fff" in r["rBadge"]) or ("rgb(255, 255, 255)" in r["rBadge"]),
         r["rBadge"])
    c.has(".mkt-badge font-weight", r["rBadge"], "font-weight: 800")
    c.ok(".mkt-badge letter-spacing .3px",
         ("letter-spacing: 0.3px" in r["rBadge"]) or ("letter-spacing: .3px" in r["rBadge"]),
         r["rBadge"])
    c.has(".mkt-badge margin-left", r["rBadge"], "margin-left: 5px")


@scen("QA-LST-03", "Header and count [L-F2]")
def lst03(page, c):
    r = page.evaluate("""() => ({
      h2: document.querySelector('.ptitle h2').textContent,
      count: document.querySelector('.ptitle .count').textContent })""")
    c.eq("h2", r["h2"], "Order Management Dashboard")
    c.eq("count", r["count"], "2,818 orders")


@scen("QA-LST-04", "(neg) Bulk Hold Shipment must not exist [L-3]")
def lst04(page, c):
    r = page.evaluate("""() => {
      const ctrls = [...document.querySelectorAll('button, input, select, option, a, [role=menuitem]')];
      const bad = ctrls.filter(el => {
        const t = ((el.textContent || '') + ' ' + (el.value || '')).toLowerCase();
        return t.includes('hold shipment') || t.includes('bulk hold');
      }).map(el => el.tagName + ':' + (el.textContent || '').slice(0, 60));
      const leg3 = [...document.querySelectorAll('.legend li')]
        .find(li => li.querySelector('.n') && li.querySelector('.n').textContent === '3');
      return { bad, leg3: leg3 ? leg3.textContent : null };
    }""")
    c.eq("no control names Hold Shipment / Bulk Hold", r["bad"], [])
    c.has("legend item 3 keeps the negative entry", r["leg3"] or "",
          "Bulk Hold Shipment button removed")


@scen("QA-LST-05", "(neg) No print or scan surface anywhere on the page")
def lst05(page, c):
    r = page.evaluate("""() => ({
      printBtns: [...document.querySelectorAll('button')]
        .filter(b => b.textContent.includes('Print')).length,
      fileInputs: [...document.querySelectorAll('input')]
        .filter(i => i.type === 'file').length,
      audio: document.querySelectorAll('audio').length })""")
    c.eq("no Print button", r["printBtns"], 0)
    c.eq("no file input", r["fileInputs"], 0)
    c.eq("no <audio>", r["audio"], 0)


@scen("QA-LST-06", "Action-row inventory [L-F4]")
def lst06(page, c):
    r = page.evaluate("""() => {
      const row = document.querySelector('.actionrow');
      const selInfo = row.querySelector('.sel-info');
      return {
        selectAll: !!row.querySelector('label input[type=checkbox]'),
        selectAllTxt: row.querySelector('label').textContent.trim(),
        selInfoTxt: selInfo.textContent, col: window.__cs(selInfo, 'color'),
        fw: window.__cs(selInfo, 'fontWeight'),
        btns: [...row.querySelectorAll('button')].map(b => b.textContent) };
    }""")
    c.ok("Select all checkbox", r["selectAll"])
    c.eq("Select all label (rule 5b)", r["selectAllTxt"], "Select all")
    c.eq("'2 selected' text", r["selInfoTxt"], "2 selected")
    c.eq("sel-info colour", r["col"], "rgb(88, 45, 181)")
    c.eq("sel-info font-weight", r["fw"], "700")
    c.eq("buttons in order", r["btns"],
         ["⧉ Merge Orders", "Sample Assignment ON", "Cancel Sample Assignment"])


@scen("QA-LST-07", "Filter-bar inventory [L-F3]")
def lst07(page, c):
    r = page.evaluate("""() => {
      const fb = document.querySelector('.filterbar');
      const dates = [...fb.querySelectorAll('input.date')].map(i => i.value);
      const tilde = [...fb.querySelectorAll('span')].some(s => s.textContent === '~');
      const sep = !!fb.querySelector('.sep');
      const inps = [...fb.querySelectorAll('input.inp')].map(i => i.placeholder);
      const sels = [...fb.querySelectorAll('select')].map(s => s.options[0].textContent);
      const chks = [...fb.querySelectorAll('.chkgrp label')]
        .map(l => ({ txt: l.textContent.trim(), on: l.querySelector('input').checked }));
      const btns = [...fb.querySelectorAll('button')].map(b => window.__own(b).trim());
      return { dates, tilde, sep, inps, sels, chks, btns };
    }""")
    c.eq("date values", r["dates"], ["2026-06-01", "2026-07-14"])
    c.ok("~ separator", r["tilde"])
    c.ok(".sep present", r["sep"])
    c.eq("search placeholders", r["inps"], ["Search (order / product)", "Search PIC"])
    c.eq("select first options", r["sels"], ["All Status", "Country: AU", "15"])
    c.eq("checkboxes (rule 5b)", r["chks"],
         [{"txt": "Order #", "on": True}, {"txt": "Tracking #", "on": False}])
    c.eq("buttons", r["btns"], ["▦ Columns", "⬇ Export", "⬇ Yun Export", "⬆ Import"])


@scen("QA-LST-12", "Global navigation shell [L-F6]")
def lst12(page, c):
    r = page.evaluate("""() => {
      const nav = document.querySelector('.nav');
      const links = [...nav.querySelectorAll('.navlink')];
      return { brand: nav.querySelector('.brand').textContent,
        navTxt: nav.textContent,
        cmt: !!nav.querySelector('button[data-open="inbox1"]'),
        badge: nav.querySelector('button[data-open="inbox1"] .badge-n').textContent,
        avatar: nav.querySelector('.avatar').textContent,
        user: nav.querySelector('.user').textContent,
        logout: !!([...nav.querySelectorAll('button')].find(b => b.textContent === 'Logout')),
        n: links.length,
        joined: links.map(s => window.__br(s)),
        raw: links.map(s => s.textContent) };
    }""")
    c.eq("brand", r["brand"], "SkinSeoul")
    for m in ["Operation AI ▾", "Catalog Management ▾", "OMS Center ▾",
              "Site Management ▾", "System Management ▾", "Customer Management ▾"]:
        c.has("menu", r["navTxt"], m)
    c.ok("💬 Comments button", r["cmt"])
    c.eq("badge", r["badge"], "3")
    c.eq("avatar", r["avatar"], "Y")
    c.has("user chip", r["user"], "Yongwon Ryu")
    c.ok("Logout", r["logout"])
    c.eq(".navlink length", r["n"], 4)
    c.eq("joined across <br> (rule 5a)", r["joined"],
         ["Agent Telemetry", "Role Assets", "Shared Asset Health", "SkinSeoul WP Admin"])
    c.eq("raw textContent", r["raw"],
         ["AgentTelemetry", "RoleAssets", "Shared AssetHealth", "SkinSeoulWP Admin"])


@scen("QA-LST-13", "(neg) No pagination is rendered in the mock")
def lst13(page, c):
    c.eq(".pager count", page.evaluate("document.querySelectorAll('.pager').length"), 0)


@scen("QA-LST-17", "(neg) No MKT row is rendered in the mock")
def lst17(page, c):
    c.eq("tr.mkt count", page.evaluate("document.querySelectorAll('tr.mkt').length"), 0)


# =========================== Block CMT =======================================

@scen("QA-CMT-01", "Hub opens and closes from its trigger")
def cmt01(page, c):
    open_hub(page)
    r = page.evaluate("""() => ({
      open: document.getElementById('inbox1').classList.contains('open'),
      badge: document.querySelector('.nav button[data-open="inbox1"] .badge-n').textContent })""")
    c.ok("open after click", r["open"])
    c.eq("badge", r["badge"], "3")
    open_hub(page)
    c.ok("closed after second click", not page.evaluate(
        "document.getElementById('inbox1').classList.contains('open')"))


@scen("QA-CMT-02", "Tabs and pane headers")
def cmt02(page, c):
    open_hub(page)
    r = page.evaluate("""() => {
      const tabs = [...document.querySelectorAll('#inbox1 .tabs button')];
      const hdr = document.querySelector('#inbox1 [data-pane="mentions"] .paneheader');
      const smalls = hdr.querySelectorAll('small');
      const h = hdr.getBoundingClientRect(), s = smalls[0].getBoundingClientRect();
      return { t0: tabs[0].textContent, t0on: tabs[0].classList.contains('on'),
        t0badge: (tabs[0].querySelector('.badge-n') || {}).textContent,
        t1: tabs[1].textContent,
        first: hdr.firstChild.textContent, nSmall: smalls.length,
        smallTxt: smalls[0].textContent,
        geoRight: h.right - s.right, geoLeft: s.left - h.left };
    }""")
    c.has("tab 0", r["t0"], "@ Mentions")
    c.ok("tab 0 on", r["t0on"])
    c.eq("tab 0 badge", r["t0badge"], "3")
    c.eq("tab 1", r["t1"], "★ Saved")
    c.eq("mentions header firstChild.textContent", r["first"],
         "Comments mentioning me · Click to open the order ")
    c.eq("exactly one <small>", r["nSmall"], 1)
    c.eq("small text", r["smallTxt"], "Mark all read")
    c.ok("geometric right-alignment (h.right - s.right <= 20)",
         r["geoRight"] <= 20, str(r["geoRight"]))
    c.ok("geometric right-alignment (s.left - h.left >= 100)",
         r["geoLeft"] >= 100, str(r["geoLeft"]))


@scen("QA-CMT-03", "Saved tab")
def cmt03(page, c):
    open_hub(page)
    page.click('#inbox1 .tabs button[data-tab="saved"]')
    r = page.evaluate("""() => {
      const saved = document.querySelector('#inbox1 [data-pane="saved"]');
      const mentions = document.querySelector('#inbox1 [data-pane="mentions"]');
      const hdr = saved.querySelector('.paneheader');
      return { savedDisp: saved.style.display, mentionsDisp: mentions.style.display,
        first: hdr.firstChild.textContent.trim(),
        small: hdr.querySelector('small').textContent,
        rows: [...saved.querySelectorAll('.it')].map(i => i.querySelector('b').textContent) };
    }""")
    c.eq("saved pane displayed", r["savedDisp"], "block")
    c.eq("mentions pane hidden", r["mentionsDisp"], "none")
    c.eq("header", r["first"], "Saved comments · Click to open the order")
    c.eq("hint", r["small"], "Unstar to remove from the list")
    c.eq("rows", r["rows"], ["Order MKT-40218"])


@scen("QA-CMT-04", "Search hides the tabs and renders a result header")
def cmt04(page, c):
    open_hub(page)
    hub_search(page, "MKT")
    r = page.evaluate("""() => ({
      tabsDisp: document.querySelector('#inbox1 .tabs').style.display,
      csrDisp: document.querySelector('#inbox1 [data-pane="csr"]').style.display,
      hdr: document.querySelector('#inbox1 [data-pane="csr"] .paneheader').textContent })""")
    c.eq("tabs hidden", r["tabsDisp"], "none")
    c.eq("csr displayed", r["csrDisp"], "block")
    c.eq("result header", r["hdr"], "3" + S_RESULTS_TAIL)


@scen("QA-CMT-05", "(neg) Search with no hits [E-38]")
def cmt05(page, c):
    open_hub(page)
    hub_search(page, "zzzz")
    r = page.evaluate("""() => ({
      empty: document.querySelector('#inbox1 [data-pane="csr"] .empty').textContent,
      its: document.querySelectorAll('#inbox1 [data-pane="csr"] .it').length,
      hdr: document.querySelector('#inbox1 [data-pane="csr"] .paneheader').textContent })""")
    c.eq("empty state", r["empty"], "No matching comments")
    c.eq(".it length", r["its"], 0)
    c.eq("result header", r["hdr"], "0" + S_RESULTS_TAIL)


@scen("QA-CMT-06", "Clearing the search restores the tabs")
def cmt06(page, c):
    open_hub(page)
    hub_search(page, "MKT")
    hub_search(page, "")
    r = page.evaluate("""() => {
      const on = document.querySelector('#inbox1 .tabs button.on');
      const pane = document.querySelector('#inbox1 [data-pane="' + on.dataset.tab + '"]');
      return { tabsDisp: document.querySelector('#inbox1 .tabs').style.display,
        csrDisp: document.querySelector('#inbox1 [data-pane="csr"]').style.display,
        activePaneDisp: pane.style.display };
    }""")
    c.eq("tabs displayed", r["tabsDisp"], "flex")
    c.eq("csr hidden", r["csrDisp"], "none")
    c.eq("active tab pane displayed", r["activePaneDisp"], "block")


@scen("QA-CMT-07", "Star toggle")
def cmt07(page, c):
    open_hub(page)
    star = ('[...document.querySelectorAll(\'#inbox1 [data-pane="mentions"] .it\')]'
            '.find(i => i.textContent.includes("Order MKT-40233")).querySelector(".star")')
    page.evaluate(star + ".click()")
    r1 = page.evaluate("""() => {
      const s = [...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
        .find(i => i.textContent.includes('Order MKT-40233')).querySelector('.star');
      return { on: s.classList.contains('on'), col: window.__cs(s, 'color') };
    }""")
    c.ok("gains class on", r1["on"])
    c.eq("colour when on", r1["col"], "rgb(245, 158, 11)")
    page.evaluate(star + ".click()")
    r2 = page.evaluate("""() => {
      const s = [...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
        .find(i => i.textContent.includes('Order MKT-40233')).querySelector('.star');
      return { on: s.classList.contains('on'), col: window.__cs(s, 'color') };
    }""")
    c.ok("class removed", not r2["on"])
    c.eq("colour when off", r2["col"], "rgb(187, 186, 190)")


@scen("QA-CMT-08", "(neg) Search input cannot inject markup [E-48]")
def cmt08(page, c):
    open_hub(page)
    hub_search(page, "<b>x")
    r = page.evaluate("""() => ({
      empty: document.querySelector('#inbox1 [data-pane="csr"] .empty').textContent,
      bs: document.querySelectorAll('#inbox1 [data-pane="csr"] b').length })""")
    c.eq("empty state", r["empty"], "No matching comments")
    c.eq("no <b> injected", r["bs"], 0)


@scen("QA-CMT-15", "Numeric-order search returns sales orders only")
def cmt15(page, c):
    open_hub(page)
    hub_search(page, "421")
    r = page.evaluate("""() => ({
      hdr: document.querySelector('#inbox1 [data-pane="csr"] .paneheader').textContent,
      rows: [...document.querySelectorAll('#inbox1 [data-pane="csr"] .it b')]
        .map(b => b.textContent) })""")
    c.eq("header", r["hdr"], "2" + S_RESULTS_TAIL)
    c.eq("rows in order", r["rows"], ["Order 421771", "Order 421502"])


@scen("QA-CMT-16", "Author search and <mark> highlighting")
def cmt16(page, c):
    open_hub(page)
    hub_search(page, "Harshit")
    r = page.evaluate("""() => {
      const its = [...document.querySelectorAll('#inbox1 [data-pane="csr"] .it')];
      return { hdr: document.querySelector('#inbox1 [data-pane="csr"] .paneheader').textContent,
        rows: its.map(i => i.querySelector('b').textContent),
        marks: its.map(i => { const m = [...i.querySelectorAll('mark')]
            .find(x => x.textContent === 'Harshit');
          return m ? window.__cs(m, 'fontWeight') : null; }) };
    }""")
    c.eq("header", r["hdr"], "2" + S_RESULTS_TAIL)
    c.eq("rows in order", r["rows"], ["Order MKT-40233", "Order MKT-40191"])
    c.eq("each row has <mark>Harshit</mark> at fw 700", r["marks"], ["700", "700"])


@scen("QA-CMT-17", "Results are ordered newest-first")
def cmt17(page, c):
    open_hub(page)
    hub_search(page, "4")
    r = page.evaluate("""() => ({
      hdr: document.querySelector('#inbox1 [data-pane="csr"] .paneheader').textContent,
      rows: [...document.querySelectorAll('#inbox1 [data-pane="csr"] .it b')]
        .map(b => b.textContent) })""")
    c.eq("header", r["hdr"], "5" + S_RESULTS_TAIL)
    c.eq("rows newest-first", r["rows"],
         ["Order MKT-40233", "Order MKT-40218", "Order 421771",
          "Order MKT-40191", "Order 421502"])


@scen("QA-CMT-18", "(neg) Mark all read is inert in the mock (demo limitation)")
def cmt18(page, c):
    open_hub(page)
    c.eq("three unread rows before", page.evaluate(
        "document.querySelectorAll('#inbox1 .it.unread').length"), 3)
    page.click('#inbox1 [data-pane="mentions"] .paneheader small')
    r = page.evaluate("""() => ({
      unread: document.querySelectorAll('#inbox1 .it.unread').length,
      badge: document.querySelector('.nav button[data-open="inbox1"] .badge-n').textContent })""")
    c.eq("rows keep unread", r["unread"], 3)
    c.eq("badge still 3", r["badge"], "3")


@scen("QA-CMT-19", "Unread and saved states in the demo data")
def cmt19(page, c):
    open_hub(page)
    r = page.evaluate("""() => {
      const its = [...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')];
      return { n: its.length,
        unread: its.map(i => i.classList.contains('unread')),
        refs: its.map(i => i.querySelector('b').textContent),
        starOn: its.map(i => i.querySelector('.star').classList.contains('on')) };
    }""")
    c.eq("three rows", r["n"], 3)
    c.eq("all unread", r["unread"], [True, True, True])
    c.eq("references", r["refs"], ["Order MKT-40233", "Order MKT-40218", "Order 421771"])
    c.eq("only MKT-40218 star on", r["starOn"], [False, True, False])


@scen("QA-CMT-20", "The hub closes on an outside click — re-baselined on [WF-21], applied 2026-08-03")
def cmt20(page, c):
    open_hub(page)
    page.click('.ptitle h2')  # a click on .pagepad content, outside the dropdown
    c.ok("#inbox1 loses class open on an outside click", page.evaluate(
        "document.getElementById('inbox1').classList.contains('open')") is False,
        "hub stayed open — no document-level close handler")
    # A click inside the panel leaves it open (the stopPropagation guards are live).
    open_hub(page)
    page.click('#inbox1 .csearch input')
    c.ok("a click on #inbox1 .csearch input leaves the hub open", page.evaluate(
        "document.getElementById('inbox1').classList.contains('open')"),
        "hub closed on an inside click (.csearch)")
    page.click('#inbox1 .tabs button[data-tab="saved"]')
    c.ok("a click on a tab button leaves the hub open", page.evaluate(
        "document.getElementById('inbox1').classList.contains('open')"),
        "hub closed on an inside click (tab button)")


@scen("QA-CMT-21", "Corpus mixes marketing and sales entities")
def cmt21(page, c):
    open_hub(page)
    hub_search(page, "4")
    r = page.evaluate("""() => ({
      n: document.querySelectorAll('#inbox1 [data-pane="csr"] .it').length,
      rows: [...document.querySelectorAll('#inbox1 [data-pane="csr"] .it b')]
        .map(b => b.textContent) })""")
    c.eq(".it length", r["n"], 5)
    c.eq("rows", r["rows"],
         ["Order MKT-40233", "Order MKT-40218", "Order 421771",
          "Order MKT-40191", "Order 421502"])
    mkt = [x for x in r["rows"] if "MKT-" in x]
    c.ok("3 MKT + 2 plain numeric in one list", len(mkt) == 3 and len(r["rows"]) - len(mkt) == 2)


# =========================== Block GBL =======================================

@scen("QA-GBL-01", "Legend closing paragraph [L-F1]")
def gbl01(page, c):
    txt = page.evaluate("document.querySelector('.legend > p').textContent")
    c.has("as-is contract sentence", txt, S_LEGEND_P1)
    c.has("redesign sentence", txt, S_LEGEND_P2)


@scen("QA-GBL-02", "Toast placement and styling [L-F5]")
def gbl02(page, c):
    open_import(page)
    page.click('#mktConfirm')
    r = page.evaluate("""() => {
      const t = document.getElementById('gtoast');
      const s = t.querySelector('small');
      return { pos: window.__cs(t, 'position'), top: window.__cs(t, 'top'),
        right: window.__cs(t, 'right'), z: window.__cs(t, 'zIndex'),
        bg: window.__cs(t, 'backgroundColor'), col: window.__cs(t, 'color'),
        fw: window.__cs(t, 'fontWeight'), fs: window.__cs(t, 'fontSize'),
        sfs: s ? window.__cs(s, 'fontSize') : null,
        sop: s ? window.__cs(s, 'opacity') : null };
    }""")
    c.eq("position", r["pos"], "fixed")
    c.eq("top", r["top"], "16px")
    c.eq("right", r["right"], "16px")
    c.eq("z-index", r["z"], "200")
    c.eq("background", r["bg"], "rgb(25, 135, 84)")
    c.eq("color", r["col"], "rgb(255, 255, 255)")
    c.eq("font-weight", r["fw"], "700")
    c.eq("font-size", r["fs"], "13.5px")
    c.eq("small font-size", r["sfs"], "11.5px")
    c.eq("small opacity", r["sop"], "0.9")


@scen("QA-GBL-03", "(neg) No reload after any action [E-43][G-2]")
def gbl03(page, c):
    sentinel(page)
    open_import(page)
    page.click('#m-import header .x')
    open_m2(page)
    page.click('#m-sampleon header .x')
    open_m3(page)
    page.click('#m-sampleoff header .x')
    open_import(page)
    page.click('#mktConfirm')
    open_m3(page)
    page.click('#sampCancelBtn')
    # baseline now interposes a confirm dialog; dismiss whatever opened
    if page.evaluate(
            "(document.getElementById('m-sampcancel-confirm')||{classList:{contains:()=>false}}).classList.contains('open')"):
        page.click('#m-sampcancel-confirm .foot button[data-close]')
        page.click('#m-sampleoff .foot button[data-close]')
    open_hub(page)
    open_hub(page)
    page.click('#annoToggle')
    page.click('#annoToggle')
    c.ok("sentinel holds throughout — no reload", sentinel_ok(page))


@scen("QA-GBL-04", "(neg) Every dismissal path creates nothing")
def gbl04(page, c):
    open_import(page)
    page.click('#m-import', position={"x": 8, "y": 8})  # backdrop
    c.ok("backdrop closes", not page.evaluate(
        "document.getElementById('m-import').classList.contains('open')"))
    open_import(page)
    page.click('#m-import header .x')
    c.ok("header ✕ closes", not page.evaluate(
        "document.getElementById('m-import').classList.contains('open')"))
    open_import(page)
    page.click('#m-import .foot button[data-close]')
    c.ok("footer Cancel closes", not page.evaluate(
        "document.getElementById('m-import').classList.contains('open')"))
    c.eq(".gtoast count stays 0", page.evaluate(
        "document.querySelectorAll('.gtoast').length"), 0)


@scen("QA-GBL-09", "(neg) Concurrent toasts are stacked, never overlaid — re-baselined on [WF-18], applied 2026-08-03 [E-62]")
def gbl09(page, c):
    open_import(page)
    page.click('#mktConfirm')
    # within the 2600 ms window, drive the cancel path through its confirm step
    open_m3(page)
    page.click('#sampCancelBtn')
    page.click('#sampConfirmGo')
    r = page.evaluate("""() => {
      const ts = [...document.querySelectorAll('.gtoast')];
      const rects = ts.map(t => t.getBoundingClientRect());
      return { n: ts.length, ids: ts.map(t => t.id),
        vis: ts.map(t => window.__cs(t, 'display')),
        tops: ts.map(t => window.__cs(t, 'top')),
        heights: ts.map(t => t.offsetHeight),
        rects: rects.map(x => ({ top: x.top, bottom: x.bottom })) };
    }""")
    c.eq(".gtoast length", r["n"], 2)
    c.eq("ids", sorted(r["ids"]), ["gtoast", "gtoast2"])
    c.eq("both display block", r["vis"], ["block", "block"])
    if r["n"] == 2:
        # The contract is the offset formula, not the demo-copy pixel values.
        c.eq("first visible toast sits at top:16px", r["tops"][0], "16px")
        expect2 = "%dpx" % (16 + r["heights"][0] + 8)
        c.eq("second toast at previous.top + previous.offsetHeight + 8px",
             r["tops"][1], expect2)
        a, b = r["rects"][0], r["rects"][1]
        c.ok("bounding boxes do not intersect while both are visible",
             a["bottom"] <= b["top"] or b["bottom"] <= a["top"],
             "rects overlap: %s vs %s" % (a, b))


@scen("QA-GBL-10", "Esc dismisses the topmost overlay, else the Comments hub — re-baselined on [WF-20], applied 2026-08-03 [E-97]")
def gbl10(page, c):
    before = page.evaluate("document.querySelectorAll('.gtoast').length")
    # One overlay at a time — each is closed by a single Escape.
    for mid in ["m-import", "m-sampleon", "m-sampleoff", "m-sampcancel-confirm"]:
        page.evaluate("document.getElementById('%s').classList.add('open')" % mid)
        page.keyboard.press("Escape")
        c.ok("#%s loses class open after Esc" % mid, page.evaluate(
            "document.getElementById('%s').classList.contains('open')" % mid) is False,
            "#%s survived Esc" % mid)
        page.evaluate("document.getElementById('%s').classList.remove('open')" % mid)
    # Topmost unwind: confirm stacked on top of M3 — one press per overlay.
    page.evaluate("""() => { document.getElementById('m-sampleoff').classList.add('open');
      document.getElementById('m-sampcancel-confirm').classList.add('open'); }""")
    page.keyboard.press("Escape")
    r1 = page.evaluate("""() => ({
      cf: document.getElementById('m-sampcancel-confirm').classList.contains('open'),
      m3: document.getElementById('m-sampleoff').classList.contains('open') })""")
    c.ok("first Esc closes only the confirm overlay", not r1["cf"])
    c.ok("first Esc leaves #m-sampleoff open (topmost only)", r1["m3"],
         "#m-sampleoff was closed by the same press")
    page.keyboard.press("Escape")
    c.ok("second Esc closes #m-sampleoff", page.evaluate(
        "document.getElementById('m-sampleoff').classList.contains('open')") is False)
    # No overlay open: Esc falls through to the Comments hub.
    open_hub(page)
    page.keyboard.press("Escape")
    c.ok("#inbox1 loses class open when no overlay is open", page.evaluate(
        "document.getElementById('inbox1').classList.contains('open')") is False,
        "#inbox1 survived Esc")
    c.eq("no dismissal created a toast", page.evaluate(
        "document.querySelectorAll('.gtoast').length"), before)


@scen("QA-GBL-11", "(neg) Wireframe-only chrome inventory (must not ship)")
def gbl11(page, c):
    r = page.evaluate("""() => ({
      bar: !!document.querySelector('.wf-bar'),
      btns: [...document.querySelectorAll('.wf-bar button')].map(b => b.textContent),
      dots: document.querySelectorAll('.dot').length,
      legend: !!document.querySelector('.legend') })""")
    c.ok(".wf-bar exists", r["bar"])
    c.eq("wf-bar buttons", r["btns"],
         ["Modal: Marketing Import", "Modal: Sample Assignment ON",
          "Modal: Cancel Sample Assignment", "Import preview: unconnected row",
          "Hide annotations"])
    c.ok(".dot elements exist", r["dots"] > 0, str(r["dots"]))
    c.ok(".legend exists", r["legend"])


@scen("QA-GBL-12", "Annotation toggle")
def gbl12(page, c):
    page.click('#annoToggle')
    r1 = page.evaluate("""() => ({
      no: document.body.classList.contains('no-anno'),
      dot: window.__cs(document.querySelector('.dot'), 'display'),
      leg: window.__cs(document.querySelector('.legend'), 'display'),
      txt: document.getElementById('annoToggle').textContent })""")
    c.ok("body.no-anno", r1["no"])
    c.eq(".dot display", r1["dot"], "none")
    c.eq(".legend display", r1["leg"], "none")
    c.eq("button text", r1["txt"], "Show annotations")
    page.click('#annoToggle')
    r2 = page.evaluate("""() => ({
      no: document.body.classList.contains('no-anno'),
      dot: window.__cs(document.querySelector('.dot'), 'display'),
      txt: document.getElementById('annoToggle').textContent })""")
    c.ok("restored", not r2["no"] and r2["dot"] != "none")
    c.eq("button text restored", r2["txt"], "Hide annotations")


@scen("QA-GBL-13", "(neg) No audio anywhere [G-3] (BR-28)")
def gbl13(page, c):
    html = page.content()
    for token in ["<audio", "AudioContext", "webkitAudioContext",
                  "speechSynthesis", "SpeechSynthesisUtterance"]:
        c.ok("no '%s'" % token, token not in html)


@scen("QA-GBL-14", "(neg) No scanner surface [G-1] (BR-28)")
def gbl14(page, c):
    r = page.evaluate("""() => {
      const scripts = [...document.querySelectorAll('script')].map(s => s.textContent).join('');
      return { autofocus: document.querySelectorAll('[autofocus]').length,
        active: document.activeElement === document.body,
        focusCalls: (scripts.match(/\\.focus\\(\\)/g) || []).length,
        otSite: scripts.includes("document.getElementById('otCustom').focus()"),
        picSite: scripts.includes('x.focus()'),
        selectCalls: (scripts.match(/\\.select\\(\\)/g) || []).length };
    }""")
    c.eq("no autofocus", r["autofocus"], 0)
    c.ok("activeElement on load is body", r["active"])
    c.eq("exactly two .focus() call sites", r["focusCalls"], 2)
    c.ok("they are the #otCustom / #picCustomIn affordances",
         r["otSite"] and r["picSite"])
    c.eq("no select-on-focus", r["selectCalls"], 0)


@scen("QA-GBL-15", "Layout minimums [E-96]")
def gbl15(page, c):
    r = page.evaluate("""() => ({
      mock: window.__cs(document.querySelector('.mock'), 'minWidth'),
      tbl: window.__cs(document.querySelector('.tbl'), 'minWidth'),
      wrap: window.__cs(document.querySelector('.mockwrap'), 'overflowX') })""")
    c.eq(".mock min-width", r["mock"], "1240px")
    c.eq(".tbl min-width", r["tbl"], "1180px")
    c.eq(".mockwrap overflow-x", r["wrap"], "auto")


# =========================== Runner ==========================================

def main():
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1500, "height": 1000})
        for sid, title, fn in SCEN:
            page = ctx.new_page()
            c = C()
            try:
                page.goto(PAGE_URL)
                page.evaluate(HELPERS)
                fn(page, c)
                status = "pass" if not c.fails else "fail"
            except Exception as e:  # runner-level error, not a spec verdict
                status = "error"
                c.fails.append({"check": "runner exception", "expected": "clean run",
                                "actual": "%s: %s" % (type(e).__name__, e)})
            finally:
                page.close()
            results.append({"id": sid, "title": title, "status": status,
                            "fails": c.fails})
        browser.close()
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = [r for r in results if r["status"] != "pass"]
    # HANDOFF.md §4 documents `python3 qa-<screen>.py [--json out.json]` for all eight
    # runners. Without this the flag is accepted, nothing is written, and the run still
    # exits 0 — a pass rate with no artefact behind it.
    if "--json" in sys.argv:
        _out = sys.argv[sys.argv.index("--json") + 1]
        _p = pathlib.Path(_out)
        _p.parent.mkdir(parents=True, exist_ok=True)
        with open(_p, "w", encoding="utf-8") as _f:
            json.dump({"total": len(results), "passed": passed,
                       "failed": len(failed), "results": results}, _f, ensure_ascii=False, indent=1)
        print("wrote", _p)
    print(json.dumps({"total": len(results), "passed": passed,
                      "failed": len(failed), "results": results},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
