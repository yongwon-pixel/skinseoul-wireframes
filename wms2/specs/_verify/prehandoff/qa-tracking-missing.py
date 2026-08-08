#!/usr/bin/env python3
"""Pre-handoff [WF] QA runner — tracking-missing (spec v1.3 §8, 66 [WF] scenarios).

Runs against the LOCAL wireframe via file:// (identical to tag review-baseline-20260803).
Follows §8.0: reload-per-scenario reset, .dot stripping before text comparison,
pool table = first table.tbl, .it addressed positionally, CDP probe for listener
clauses (recorded not-run when unavailable), every [WF] scenario on this one page.

Output: JSON report on stdout. Exit 0 always (verdicts live in the JSON).
"""
import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

import pathlib

# Legacy consoles (Windows cp949 / cp1252) otherwise abort the suite mid-run with
# UnicodeEncodeError on the first non-ASCII character, leaving a partial pass count.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover - non-reconfigurable stream
    pass


HERE = Path(__file__).resolve()
WF_FILE = HERE.parents[3] / "tracking-missing" / "index.html"
URL = WF_FILE.as_uri()

EN = "–"   # – en dash
EM = "—"  # — em dash

RESULTS = []


class Fail(Exception):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual
        super().__init__(f"expected={expected!r} actual={actual!r}")


def ck(cond, expected, actual):
    if not cond:
        raise Fail(str(expected), str(actual))


def record(sid, status, expected="", actual="", note=""):
    RESULTS.append({"id": sid, "status": status, "expected": expected,
                    "actual": actual, "note": note})


INIT_JS = """
window.qtxt = el => { const c = el.cloneNode(true);
  c.querySelectorAll('.dot').forEach(d => d.remove());
  return c.textContent.replace(/\\s+/g, ' ').trim(); };
window.qcs = (el, p) => getComputedStyle(el)[p];
"""


def fresh(page):
    page.goto(URL)
    page.wait_for_selector("#poolCount")


def open_m1_from_row1(page):
    page.click("#poolrow1 [data-modal='m-match']")
    page.wait_for_selector("#m-match.open")


def texts(page, sel):
    return page.evaluate(
        "sel => [...document.querySelectorAll(sel)].map(e => window.qtxt(e))", sel)


def txt(page, sel):
    return page.evaluate("sel => window.qtxt(document.querySelector(sel))", sel)


def cs(page, sel, prop):
    return page.evaluate(
        "([sel, p]) => getComputedStyle(document.querySelector(sel))[p]", [sel, prop])


def count(page, sel):
    return page.evaluate("sel => document.querySelectorAll(sel).length", sel)


def pool_counts(page):
    return (txt(page, "#poolCount"), txt(page, "#poolCountBottom"),
            count(page, ".mock table.tbl tbody tr"))


# ───────────────────────── LOAD ─────────────────────────

def qa_load_01(page):
    t = txt(page, ".pagepad h2")
    ck(t == "WMS - Unrecognized Tracking List", "h2 == 'WMS - Unrecognized Tracking List'", t)


def qa_load_02(page):
    sub = txt(page, ".pagepad .sub")
    ck("Unrecognized & missing-tracking status" in sub, "sub contains status line", sub)
    mut = txt(page, ".pagepad .sub .mut")
    ck("Coupang creates the order number immediately but generates the tracking number a few hours later" in mut,
       "sub .mut contains Coupang timing sentence", mut)


def qa_load_03(page):
    bg = cs(page, ".poolhead", "backgroundColor")
    bc = cs(page, ".poolhead", "borderTopColor")
    lead = txt(page, ".poolhead > b")
    ck(bg == "rgb(255, 251, 214)", "poolhead bg rgb(255, 251, 214)", bg)
    ck(bc == "rgb(245, 158, 11)", "poolhead border rgb(245, 158, 11)", bc)
    ck(lead == "⚠ Unrecognized product pool · 3 items",
       "lead '⚠ Unrecognized product pool · 3 items'", lead)


def qa_load_04(page):
    ths = texts(page, ".mock table.tbl thead th")
    want = ["Tracking No", "Order No", "Product Name", "Product Name KR", "Size",
            "Barcode", "Qty", "Memo", "Registrant (Center)", "Registered At",
            "Suspected Orders (Auto-matched)", "Action"]
    ck(ths == want, str(want), str(ths))


def qa_load_05(page):
    pc, pcb, rows = pool_counts(page)
    ck(pc == "3" and pcb == "3" and rows == 3,
       "#poolCount=3, #poolCountBottom=3, 3 tbody rows",
       f"poolCount={pc} bottom={pcb} rows={rows}")
    hit = count(page, ".mock table.tbl tbody tr.row-hit")
    ck(hit == 3, "all 3 rows carry .row-hit", f"{hit} rows with .row-hit")


def qa_load_06(page):
    sels = [".searchbar", ".pager", ".bulkbar", ".picava", ".picname", ".cntchip",
            ".wait", ".slack-pill", ".logsec", "input[type=checkbox]"]
    found = {s: count(page, s) for s in sels if count(page, s)}
    ck(not found, "none of the 2026-07-23 removals rendered", str(found or "none"))


def qa_load_07(page):
    lis = count(page, ".legend ol > li")
    badges = texts(page, ".legend ol > li .n")
    dots = count(page, ".dot")
    ck(lis == 6 and badges == ["0", "1", "2", "3", "4", "5"],
       "6 legend li with badges 0..5", f"lis={lis} badges={badges}")
    ck(dots == 8, "exactly 8 .dot elements", f"{dots} dots")


def qa_load_08(page):
    ps = texts(page, ".legend > p")
    ck(len(ps) == 2, "exactly 2 <p> after legend <ol>", f"{len(ps)} paragraphs")
    ck("2026-07-23 simplification decision:" in ps[0],
       "p1 contains simplification record", ps[0][:120])
    ck("(Confirmed 2026-08-02) Unrequested inbound shipments also use this pool" in ps[1],
       "p2 contains unrequested-inbound confirmation", ps[1][:120])


def qa_load_09(page):
    info = page.evaluate("""() => {
      const all = [...document.querySelectorAll('input')];
      return {total: all.length,
              outside: all.filter(i => !i.closest('#m-remove')).length,
              inside_ids: all.filter(i => i.closest('#m-remove')).map(i => i.id)};
    }""")
    ck(info["outside"] == 0 and info["total"] == 1 and info["inside_ids"] == ["rmInbound"],
       "0 inputs outside #m-remove; exactly one (#rmInbound) inside", str(info))


def qa_load_10(page):
    r = page.evaluate("""() => ({
      printText: /\\bPrint\\b/.test(document.body.innerText),
      audio: !!document.querySelector('audio'),
      audioCtx: [...document.scripts].some(s => s.textContent.includes('AudioContext')),
      greens: [...document.querySelectorAll('.btn-green')].map(b =>
        [window.qtxt(b), !!b.closest('#m-match')])
    })""")
    ck(not r["printText"], "no rendered 'Print' text", str(r["printText"]))
    ck(not r["audio"] and not r["audioCtx"], "no <audio>, no AudioContext",
       f"audio={r['audio']} audioCtx={r['audioCtx']}")
    ck(len(r["greens"]) == 2 and all(t == "Match to this product" and inm for t, inm in r["greens"]),
       "only .btn-green = two 'Match to this product' in #m-match", str(r["greens"]))


def qa_load_11(page):
    h1 = txt(page, ".wf-bar h1")
    tabs = texts(page, ".wf-tab")
    tog = txt(page, "#annoToggle")
    ck(h1 == "WMS 2.0 · Unrecognized Tracking Wireframe", "wf-bar h1", h1)
    ck("Modal: Match Review (M1)" in tabs and "Modal: Remove Confirm (M2)" in tabs,
       "wf-tab M1 + M2 buttons", str(tabs))
    ck(tog == "Hide annotations", "annoToggle reads 'Hide annotations'", tog)


# ───────────────────────── ROW ─────────────────────────

def qa_row_01(page):
    c0 = txt(page, "#poolrow1 td:nth-child(1)")
    c1 = txt(page, "#poolrow1 td:nth-child(2)")
    col = cs(page, "#poolrow1 td:nth-child(2)", "color")
    ck(c0 == "10323100841207", "cell1 '10323100841207'", c0)
    ck(c1 == EN, "cell2 en dash U+2013", repr(c1))
    ck(col == "rgb(126, 124, 131)", "cell2 color rgb(126, 124, 131)", col)


def _name_cell(page, row_sel, col, brand, rest):
    r = page.evaluate("""([sel, col]) => {
      const td = document.querySelector(sel).cells[col];
      const b = td.querySelector('b');
      return {b: b ? b.textContent : null,
              after: b && b.nextSibling ? b.nextSibling.textContent : null};
    }""", [row_sel, col])
    ck(r["b"] == brand, f"<b> == {brand!r}", str(r["b"]))
    ck(r["after"] == rest, f"text after <b> == {rest!r}", repr(r["after"]))


def qa_row_02(page):
    _name_cell(page, "#poolrow1", 2, "COSRX", " Advanced Snail 96 Mucin Power Essence, 100ml")


def qa_row_03(page):
    _name_cell(page, "#poolrow1", 3, "COSRX", " 어드밴스드 스네일 96 뮤신 에센스")


def qa_row_04(page):
    row = ".mock table.tbl tbody tr:nth-of-type(3)"
    _name_cell(page, row, 3, "Medicube", " 제로 모공 패드 2.0 (1+1)")
    en_b = page.evaluate(
        "sel => document.querySelector(sel).cells[2].querySelector('b').textContent", row)
    ck(en_b == "medicube", "EN name <b> == 'medicube' (lowercase)", en_b)


def _col_values(page, col):
    return page.evaluate(
        "col => [...document.querySelectorAll('.mock table.tbl tbody tr')].map(r => window.qtxt(r.cells[col]))",
        col)


def qa_row_05(page):
    sizes, bars, qtys = _col_values(page, 4), _col_values(page, 5), _col_values(page, 6)
    ck(sizes == ["100ml", "250ml", "70ea"], "sizes 100ml/250ml/70ea", str(sizes))
    ck(bars == ["8809416470726", "8809640733458", "8809894261234"], "barcodes", str(bars))
    ck(qtys == ["1", "1", "2"], "qty 1/1/2", str(qtys))


def qa_row_06(page):
    memos = _col_values(page, 7)
    ck(memos == ["Box label damaged", EN, "Looks like a 1+1 set"],
       "memos with literal en dash for empty", str([repr(m) for m in memos]))


def qa_row_07(page):
    regs, ats = _col_values(page, 8), _col_values(page, 9)
    ck(regs == ["Miranti", "Dean", "Dean"], "registrants Miranti/Dean/Dean", str(regs))
    ck(ats == ["07-13 10:12", "07-13 09:48", "07-13 09:30"], "Registered At values", str(ats))
    ck(all(re.fullmatch(r"\d{2}-\d{2} \d{2}:\d{2}", a) for a in ats),
       "MM-DD HH:mm format", str(ats))


def qa_row_08(page, cdp_ctx):
    ats = _col_values(page, 9)
    ck(ats == sorted(ats, reverse=True), "ordered by Registered At descending", str(ats))
    ths = page.evaluate("""() => [...document.querySelectorAll('.mock table.tbl thead th')].map(th => ({
        t: window.qtxt(th),
        onclick: th.hasAttribute('onclick'), ds: th.hasAttribute('data-sort'),
        aria: th.hasAttribute('aria-sort')}))""")
    glyphs = [t["t"] for t in ths if any(g in t["t"] for g in "▲▼↑↓⇅")]
    attrs = [t["t"] for t in ths if t["onclick"] or t["ds"] or t["aria"]]
    ck(not glyphs, "(a) no sort glyph in any th", str(glyphs or "none"))
    ck(not attrs, "(b) no onclick/data-sort/aria-sort on any th", str(attrs or "none"))
    # (c) CDP listener probe
    note = ""
    try:
        cdp = cdp_ctx["page"].context.new_cdp_session(cdp_ctx["page"])
        bound = []
        for i in range(12):
            r = cdp.send("Runtime.evaluate", {
                "expression": f"document.querySelectorAll('.mock table.tbl thead th')[{i}]"})
            oid = r["result"].get("objectId")
            lr = cdp.send("DOMDebugger.getEventListeners", {"objectId": oid})
            if lr.get("listeners"):
                bound.append(i)
        ck(not bound, "(c) getEventListeners [] on all 12 th", f"listeners on th idx {bound}")
        note = "(c) CDP probe ran: 0 listeners on all 12 th"
    except Fail:
        raise
    except Exception as e:  # CDP unavailable → clause (c) not-run per §8.0 rule 6
        note = f"(c) not-run (CDP unavailable: {type(e).__name__})"
    return note


def qa_row_09(page):
    ids = page.evaluate(
        "() => [...document.querySelectorAll('tr[id]')].map(r => r.id)")
    ck(ids == ["poolrow1"], "exactly one tr with id, == poolrow1", str(ids))


# ───────────────────────── SUS ─────────────────────────

def qa_sus_01(page):
    n = count(page, "#poolrow1 td:nth-child(11) > div")
    ck(n == 2, "2 candidate <div> lines in row1", str(n))


def qa_sus_02(page):
    r = page.evaluate("""() => {
      const d = document.querySelector('#poolrow1 td:nth-child(11) > div');
      const b = d.querySelector('b');
      const ord = d.querySelector('span.num');
      const mut = d.querySelector('span.mut');
      const co = getComputedStyle(ord), cm = getComputedStyle(mut);
      return {line: window.qtxt(d), b: b.textContent, ord: window.qtxt(ord),
              ordColor: co.color, ordWeight: co.fontWeight,
              mut: window.qtxt(mut), mutColor: cm.color};
    }""")
    ck(r["line"] == "Dean · Order 414230 · JIT (Naver) · Processing",
       "line 'Dean · Order 414230 · JIT (Naver) · Processing'", r["line"])
    ck(r["b"] == "Dean", "'Dean' in <b>", r["b"])
    ck(r["ord"] == "Order 414230" and r["ordColor"] == "rgb(13, 110, 253)"
       and r["ordWeight"] == "700",
       "Order 414230 rgb(13,110,253) weight 700",
       f"{r['ord']} {r['ordColor']} {r['ordWeight']}")
    ck(r["mut"] == "JIT (Naver) · Processing" and r["mutColor"] == "rgb(126, 124, 131)",
       "one span.mut 'JIT (Naver) · Processing' rgb(126,124,131)",
       f"{r['mut']} {r['mutColor']}")


def qa_sus_03(page):
    t = page.evaluate(
        "() => window.qtxt(document.querySelectorAll('#poolrow1 td:nth-child(11) > div')[1])")
    ck(t == "Egita · Order 413871 · JIT (Official Mall) · Processing",
       "'Egita · Order 413871 · JIT (Official Mall) · Processing'", t)


def qa_sus_04(page):
    r = page.evaluate("""() => {
      const rows = [...document.querySelectorAll('.mock table.tbl tbody tr')];
      return [2, 3].map(i => {
        const divs = rows[i - 1].cells[10].querySelectorAll(':scope > div');
        return {n: divs.length, t: window.qtxt(divs[0])};
      });
    }""")
    ck(r[0]["n"] == 1 and r[0]["t"] == "Harshit · Order 414102 · JIT (Naver) · Processing",
       "row2: 1 line 'Harshit · Order 414102 · JIT (Naver) · Processing'", str(r[0]))
    ck(r[1]["n"] == 1 and r[1]["t"] == "Miranti · Order 413998 · JIT (Official Mall) · Processing",
       "row3: 1 line 'Miranti · Order 413998 · JIT (Official Mall) · Processing'", str(r[1]))


def qa_sus_05(page):
    r = page.evaluate("""() => {
      const muts = [...document.querySelectorAll('.mock table.tbl tbody td:nth-child(11) span.mut')];
      return muts.map(m => { const c = getComputedStyle(m); return {
        t: window.qtxt(m), bg: c.backgroundColor,
        bs: [c.borderTopStyle, c.borderRightStyle, c.borderBottomStyle, c.borderLeftStyle].join(','),
        pad: [c.paddingTop, c.paddingRight, c.paddingBottom, c.paddingLeft].join(','),
        col: c.color, w: c.fontWeight}; });
    }""")
    ck(len(r) == 4, "exactly four trailing span.mut", str(len(r)))
    bad = [m for m in r if not (m["bg"] == "rgba(0, 0, 0, 0)"
           and m["bs"] == "none,none,none,none"
           and m["pad"] == "0px,0px,0px,0px"
           and m["col"] == "rgb(126, 124, 131)"
           and int(m["w"]) < 700)]
    ck(not bad, "all 4: transparent bg, no border, 0 padding, rgb(126,124,131), non-bold",
       str(bad or "all ok"))


# ───────────────────────── M1 ─────────────────────────

def qa_m1_01(page):
    open_m1_from_row1(page)
    r = page.evaluate("""() => {
      const h = document.querySelector('#m-match .modal header');
      const first = h.childNodes[0];
      const x = h.querySelector('button.x[data-close]');
      return {open: document.getElementById('m-match').classList.contains('open'),
              lead: first && first.nodeType === 3 ? first.nodeValue : null,
              xInHeader: !!x && x.parentElement === h};
    }""")
    ck(r["open"], "#m-match has class open", str(r["open"]))
    ck(r["lead"] == f"Review & Match {EM} Unrecognized Product",
       "leading text node 'Review & Match — Unrecognized Product' (U+2014)", repr(r["lead"]))
    ck(r["xInHeader"], "button.x[data-close] is a child of <header>", str(r["xInHeader"]))


def qa_m1_02(page):
    page.click(".wf-tab[data-modal='m-match']")
    page.wait_for_selector("#m-match.open")


def _open_m1(page):
    open_m1_from_row1(page)


def qa_m1_03(page):
    _open_m1(page)
    r = page.evaluate("""() => {
      const card = document.querySelector('#m-match .body > div');
      const b = card.querySelector('b');
      return {b: b.textContent, after: b.nextSibling ? b.nextSibling.textContent : null,
              mut: window.qtxt(card.querySelector('.mut'))};
    }""")
    ck(r["b"] == "COSRX" and r["after"] == " Advanced Snail 96 Mucin Power Essence, 100ml",
       "<b>COSRX</b> + ' Advanced Snail 96 Mucin Power Essence, 100ml'", str(r))
    want = ('Barcode 8809416470726 · Tracking 10323100841207 · No order number '
            '· 1 unit · Registered by: Miranti (Center) 07-13 10:12 '
            '· Memo "Box label damaged"')
    ck(r["mut"] == want, want, r["mut"])


def qa_m1_04(page):
    _open_m1(page)
    r = page.evaluate("""() => {
      const panel = document.querySelectorAll('#m-match .body > div')[1];
      return {b: window.qtxt(panel.querySelector('b')),
              mut: window.qtxt(panel.querySelector('span.mut'))};
    }""")
    ck(r["b"] == "Suspected orders (auto-matched)",
       "bold heading 'Suspected orders (auto-matched)'", r["b"])
    ck("Match by selecting a product line, not the order" in r["mut"],
       "explanation contains 'Match by selecting a product line, not the order'", r["mut"])


def qa_m1_05(page):
    _open_m1(page)
    ths = texts(page, "#m-match table.tbl thead th")
    ck(ths == ["Order", "PIC", "Channel", "Included Product", ""],
       "['Order','PIC','Channel','Included Product',''] — 5 columns", str(ths))


def qa_m1_06(page):
    _open_m1(page)
    rows = page.evaluate("""() => [...document.querySelectorAll('#m-match table.tbl tbody tr')].map(r => ({
        cells: [...r.cells].map(c => window.qtxt(c)),
        b: r.cells[3].querySelector('b') ? r.cells[3].querySelector('b').textContent : null,
        btn: r.cells[4].querySelector('button') ? window.qtxt(r.cells[4].querySelector('button')) : null}))""")
    ck(len(rows) == 2, "exactly 2 candidate rows", str(len(rows)))
    w1 = ["414230", "Dean", "JIT (Naver)", "COSRX Snail 96 Essence ×1"]
    w2 = ["413871", "Egita", "JIT (Official Mall)", "COSRX Snail 96 Essence ×1"]
    ck(rows[0]["cells"][:4] == w1 and rows[1]["cells"][:4] == w2,
       f"{w1} / {w2}", str([r["cells"][:4] for r in rows]))
    ck(all(r["b"] == "COSRX" and r["btn"] == "Match to this product" for r in rows),
       "COSRX in <b>, button 'Match to this product' in each row", str(rows))


def qa_m1_07(page):
    _open_m1(page)
    note = txt(page, "#m-match .note")
    for frag in ["tracking number 10323100841207 is registered to the selected product line",
                 "this item disappears from the pool",
                 '"@Miranti (unrecognized registrant) Matched the unrecognized product (COSRX Snail 96 Essence) to this order"']:
        ck(frag in note, f".note contains {frag!r}", note)


def qa_m1_09(page):
    _open_m1(page)
    r = page.evaluate("""() => ({
      foot: [...document.querySelectorAll('#m-match .foot button')].map(b => window.qtxt(b)),
      solo: [...document.querySelectorAll('#m-match button')].map(b => window.qtxt(b))
            .filter(t => ['Confirm', 'OK', 'Save', 'Match'].includes(t))})""")
    ck(r["foot"] == ["Cancel"], ".foot has exactly one button 'Cancel'", str(r["foot"]))
    ck(not r["solo"], "no element labelled Confirm/OK/Save/Match alone", str(r["solo"]))


def qa_m1_10(page):
    _open_m1(page)
    r = page.evaluate("""() => [...document.querySelectorAll('#m-match tbody td:nth-child(3) .tag-jit')]
      .map(t => { const c = getComputedStyle(t); return {t: window.qtxt(t),
        bg: c.backgroundColor, pad: c.paddingTop + c.paddingRight + c.paddingBottom + c.paddingLeft,
        col: c.color}; })""")
    ck(len(r) == 2 and [x["t"] for x in r] == ["JIT (Naver)", "JIT (Official Mall)"],
       "Channel cells JIT (Naver) / JIT (Official Mall)", str(r))
    bad = [x for x in r if not (x["bg"] == "rgba(0, 0, 0, 0)" and x["pad"] == "0px0px0px0px"
                                and x["col"] == "rgb(20, 16, 27)")]
    ck(not bad, "transparent bg, zero padding, ink rgb(20,16,27)", str(bad or "all ok"))


# ───────────────────────── MATCH chain ─────────────────────────

def match_chain(page):
    fresh(page)
    page.evaluate("window.__alive = true")
    open_m1_from_row1(page)
    t0 = time.monotonic()
    page.click("#m-match .pmatch")
    out = []
    # MATCH-01
    try:
        opened = page.evaluate("() => document.getElementById('m-match').classList.contains('open')")
        ck(not opened, "#m-match no longer has class open", f"open={opened}")
        out.append(("QA-MATCH-01", "PASS", "", ""))
    except Fail as f:
        out.append(("QA-MATCH-01", "FAIL", f.expected, f.actual))
    # MATCH-02
    try:
        n = count(page, "#poolrow1")
        ck(n == 0, "#poolrow1 absent from DOM", f"{n} matches")
        out.append(("QA-MATCH-02", "PASS", "", ""))
    except Fail as f:
        out.append(("QA-MATCH-02", "FAIL", f.expected, f.actual))
    # MATCH-03
    try:
        pc, pcb, _ = pool_counts(page)
        ck(pc == "2" and pcb == "2", "#poolCount=2 and #poolCountBottom=2", f"{pc}/{pcb}")
        out.append(("QA-MATCH-03", "PASS", "", ""))
    except Fail as f:
        out.append(("QA-MATCH-03", "FAIL", f.expected, f.actual))
    # MATCH-04
    try:
        r = page.evaluate("""() => { const t = document.getElementById('matchToast');
          const c = getComputedStyle(t);
          return {d: c.display, bg: c.backgroundColor,
                  main: t.querySelector('span') ? t.querySelector('span').textContent : '',
                  sub: t.querySelector('small') ? t.querySelector('small').textContent : ''}; }""")
        ck(r["d"] == "flex", "toast display flex", r["d"])
        ck(r["main"] == "✓ Matched to Order 414230 · COSRX Snail 96",
           "'✓ Matched to Order 414230 · COSRX Snail 96'", r["main"])
        ck(r["sub"] == "Tracking 10323100841207 registered · removed from pool · @Miranti notified via Slack",
           "'Tracking 10323100841207 registered · removed from pool · @Miranti notified via Slack'", r["sub"])
        ck(r["bg"] == "rgb(25, 135, 84)", "toast bg rgb(25, 135, 84)", r["bg"])
        out.append(("QA-MATCH-04", "PASS", "", ""))
    except Fail as f:
        out.append(("QA-MATCH-04", "FAIL", f.expected, f.actual))
    # MATCH-05
    try:
        hidden = False
        while time.monotonic() - t0 < 4.5:
            if page.evaluate("() => getComputedStyle(document.getElementById('matchToast')).display") == "none":
                hidden = True
                break
            time.sleep(0.1)
        alive = page.evaluate("() => window.__alive === true")
        ck(hidden, "toast display none within 4.5 s", "still visible at 4.5 s" if not hidden else "")
        ck(alive, "document never unloaded (marker survived)", f"marker={alive}")
        out.append(("QA-MATCH-05", "PASS", "", ""))
    except Fail as f:
        out.append(("QA-MATCH-05", "FAIL", f.expected, f.actual))
    for sid, st, e, a in out:
        record(sid, st, e, a)


# ───────────────────────── XDEL ─────────────────────────

def qa_xdel_01(page):
    page.click(".mock table.tbl tbody tr:nth-of-type(2) .xdel")
    page.wait_for_selector("#m-remove.open")
    r = page.evaluate("""() => {
      const h = document.querySelector('#m-remove .modal header');
      return {lead: h.childNodes[0].nodeValue,
              sum: window.qtxt(document.getElementById('rmSummary')),
              disabled: document.getElementById('rmConfirm').disabled,
              rows: document.querySelectorAll('.mock table.tbl tbody tr').length,
              pc: window.qtxt(document.getElementById('poolCount')),
              pcb: window.qtxt(document.getElementById('poolCountBottom'))};
    }""")
    ck(r["lead"] == "Remove this item from the pool?",
       "header leading text 'Remove this item from the pool?'", repr(r["lead"]))
    ck("Anua" in r["sum"] and "10323100838455" in r["sum"],
       "#rmSummary contains Anua and 10323100838455", r["sum"])
    ck("Memo" not in r["sum"], "no Memo fragment (row2 memo is en dash)", r["sum"])
    ck(r["disabled"], "#rmConfirm disabled", f"disabled={r['disabled']}")
    ck(r["rows"] == 3 and r["pc"] == "3" and r["pcb"] == "3",
       "no row removed yet; 3 rows, counters 3/3",
       f"rows={r['rows']} pc={r['pc']} pcb={r['pcb']}")
    page.select_option("#rmReason", label="Registered by mistake")
    page.click("#rmConfirm")
    r2 = page.evaluate("""() => {
      const t = document.getElementById('matchToast');
      return {gone: ![...document.querySelectorAll('.mock table.tbl tbody tr')]
                .some(tr => tr.cells[0].textContent.includes('10323100838455')),
              rows: document.querySelectorAll('.mock table.tbl tbody tr').length,
              pc: window.qtxt(document.getElementById('poolCount')),
              pcb: window.qtxt(document.getElementById('poolCountBottom')),
              main: t.querySelector('span') ? t.querySelector('span').textContent : '',
              sub: t.querySelector('small') ? t.querySelector('small').textContent : ''};
    }""")
    ck(r2["gone"] and r2["rows"] == 2, "Anua row absent from DOM", str(r2))
    ck(r2["pc"] == "2" and r2["pcb"] == "2", "counters 2/2", f"{r2['pc']}/{r2['pcb']}")
    ck(r2["main"] == "✓ Removed from pool · Anua Heartleaf 77% Soothing Toner, 250ml",
       "'✓ Removed from pool · Anua Heartleaf 77% Soothing Toner, 250ml'", r2["main"])
    ck(r2["sub"] == "Reason: Registered by mistake · Tracking 10323100838455",
       "'Reason: Registered by mistake · Tracking 10323100838455'", r2["sub"])


def qa_xdel_02(page):
    for path, act in [("Cancel", lambda: page.click("#m-remove .foot button.btn-line")),
                      ("header ✕", lambda: page.click("#m-remove header .x")),
                      ("backdrop", lambda: page.mouse.click(10, 300))]:
        page.click("#poolrow1 .xdel")
        page.wait_for_selector("#m-remove.open")
        page.select_option("#rmReason", label="Registered by mistake")
        act()
        r = page.evaluate("""() => ({
          open: document.getElementById('m-remove').classList.contains('open'),
          rows: document.querySelectorAll('.mock table.tbl tbody tr').length,
          pc: window.qtxt(document.getElementById('poolCount')),
          pcb: window.qtxt(document.getElementById('poolCountBottom')),
          toast: getComputedStyle(document.getElementById('matchToast')).display})""")
        ck(not r["open"], f"[{path}] modal closed", f"open={r['open']}")
        ck(r["rows"] == 3 and r["pc"] == "3" and r["pcb"] == "3",
           f"[{path}] 3 rows, counters 3/3", str(r))
        ck(r["toast"] == "none", f"[{path}] toast stayed display:none", r["toast"])


def _remove_first_row(page, reason):
    page.click(".mock table.tbl tbody tr:nth-of-type(1) .xdel")
    page.wait_for_selector("#m-remove.open")
    page.select_option("#rmReason", label=reason)
    page.click("#rmConfirm")


def qa_xdel_03(page):
    for _ in range(3):
        _remove_first_row(page, "No action needed")
    pc, pcb, rows = pool_counts(page)
    ck(pc == "0" and pcb == "0" and rows == 0,
       "after 3 removals counters 0/0, no negative", f"pc={pc} pcb={pcb} rows={rows}")


# ───────────────────────── CMT ─────────────────────────

def qa_cmt_01(page):
    r = page.evaluate("""() => { const b = document.querySelector('.nav .icon-btn');
      return {t: b.textContent, badge: b.querySelector('.badge-n').textContent}; }""")
    ck(r["t"].startswith("\U0001f4ac Comments"), "button text starts '💬 Comments'", r["t"])
    ck(r["badge"] == "3", ".badge-n reads 3", r["badge"])


def _open_inbox(page):
    page.click(".nav .icon-btn")
    page.wait_for_selector("#inbox1.open")


def qa_cmt_02(page):
    _open_inbox(page)
    r = page.evaluate("""() => {
      const tabs = [...document.querySelectorAll('#inbox1 .tabs button')];
      return {t0: window.qtxt(tabs[0]), b0: tabs[0].querySelector('.badge-n') ?
              tabs[0].querySelector('.badge-n').textContent : null, t1: window.qtxt(tabs[1])};
    }""")
    ck(r["t0"].startswith("@ Mentions") and r["b0"] == "3",
       "tab '@ Mentions' with inline badge 3", str(r))
    ck(r["t1"] == "★ Saved", "tab '★ Saved'", r["t1"])


def qa_cmt_03(page):
    _open_inbox(page)
    r = page.evaluate("""() => {
      const pane = document.querySelector('#inbox1 .tabpane[data-pane="mentions"]');
      const ph = pane.querySelector('.paneheader');
      const small = ph.querySelector('small');
      const c = ph.cloneNode(true); c.querySelector('small').remove();
      const phBox = ph.getBoundingClientRect(), smBox = small.getBoundingClientRect();
      const items = [...pane.querySelectorAll('.it')];
      return {head: c.textContent.replace(/\\s+/g, ' ').trim(),
              small: small.textContent.trim(),
              rightAligned: smBox.left > phBox.left + phBox.width / 2,
              items: items.length,
              unread: items.filter(i => i.classList.contains('unread')).length};
    }""")
    ck(r["head"] == "Comments mentioning me · Click to open the order",
       "'Comments mentioning me · Click to open the order'", r["head"])
    ck(r["small"] == "Mark all read" and r["rightAligned"],
       "right-aligned 'Mark all read'", str(r))
    ck(r["items"] == 4 and r["unread"] == 3,
       "exactly 4 .it items, exactly 3 unread", f"items={r['items']} unread={r['unread']}")


def qa_cmt_04(page):
    _open_inbox(page)
    r = page.evaluate("""() => {
      const it = [...document.querySelectorAll('#inbox1 .tabpane[data-pane="mentions"] .it')][1];
      return {ent: it.querySelector('.body b').textContent,
              body: window.qtxt(it.querySelector('.body')),
              time: it.querySelector('time').textContent};
    }""")
    ck(r["ent"] == "Unrecognized pool", "entity label exactly 'Unrecognized pool'", r["ent"])
    ck('Miranti: "@Yongwon Left a memo on the Snail essence (box label damaged). Please check whose order this is"' in r["body"],
       "body contains Miranti memo comment", r["body"])
    ck(r["time"] == "10:12", "time 10:12", r["time"])


def qa_cmt_05(page):
    _open_inbox(page)
    page.click("#inbox1 .tabs button[data-tab='saved']")
    r = page.evaluate("""() => {
      const m = document.querySelector('#inbox1 .tabpane[data-pane="mentions"]');
      const s = document.querySelector('#inbox1 .tabpane[data-pane="saved"]');
      const ph = s.querySelector('.paneheader');
      const c = ph.cloneNode(true); c.querySelector('small').remove();
      const items = [...s.querySelectorAll('.it')];
      return {mDisp: getComputedStyle(m).display, sDisp: getComputedStyle(s).display,
              head: c.textContent.replace(/\\s+/g, ' ').trim(),
              small: ph.querySelector('small').textContent.trim(),
              n: items.length,
              ent: items[0] ? items[0].querySelector('.body b').textContent : null};
    }""")
    ck(r["mDisp"] == "none" and r["sDisp"] == "block",
       "mentions hidden, saved shown", f"mentions={r['mDisp']} saved={r['sDisp']}")
    ck(r["head"] == "Saved comments · Click to open the order",
       "'Saved comments · Click to open the order'", r["head"])
    ck(r["small"] == "Unstar to remove from the list",
       "'Unstar to remove from the list'", r["small"])
    ck(r["n"] == 1 and r["ent"] == "Unrecognized pool",
       "exactly 1 item, entity 'Unrecognized pool'", f"n={r['n']} ent={r['ent']}")


def qa_cmt_06(page):
    _open_inbox(page)
    on0 = page.evaluate("() => document.querySelector('#inbox1 .it .star').classList.contains('on')")
    ck(not on0, "first .it star initially not .on", f"on={on0}")
    page.click("#inbox1 .it .star")
    on1 = page.evaluate("() => document.querySelector('#inbox1 .it .star').classList.contains('on')")
    ck(on1, "star gains .on after click", f"on={on1}")
    page.click("#inbox1 .it .star")
    on2 = page.evaluate("() => document.querySelector('#inbox1 .it .star').classList.contains('on')")
    ck(not on2, "star loses .on after second click", f"on={on2}")


def qa_cmt_11(page):
    _open_inbox(page)
    page.click(".pagepad h2")
    o1 = page.evaluate("() => document.getElementById('inbox1').classList.contains('open')")
    ck(o1, "still open after outside click (wireframe quirk §2.4.8)", f"open={o1}")
    page.keyboard.press("Escape")
    o2 = page.evaluate("() => document.getElementById('inbox1').classList.contains('open')")
    ck(o2, "still open after Esc (wireframe quirk §2.4.8)", f"open={o2}")


# ───────────────────────── FURN ─────────────────────────

def qa_furn_01(page):
    t = txt(page, ".pagepad > p.mut")
    inner = txt(page, "#poolCountBottom")
    ck(t == "Unrecognized pool · 3 items", "'Unrecognized pool · 3 items'", t)
    ck(inner == "3", "count inside #poolCountBottom == 3", inner)


def qa_furn_02(page):
    open_m1_from_row1(page)
    page.click("#m-match .pmatch")
    r = page.evaluate("""() => {
      const t = document.getElementById('matchToast');
      const c = getComputedStyle(t);
      const tb = t.getBoundingClientRect();
      const cells = [...document.querySelectorAll('.mock table.tbl tbody tr')]
        .map(row => row.cells[11].getBoundingClientRect());
      const hit = cells.some(b => !(tb.right < b.left || tb.left > b.right ||
                                    tb.bottom < b.top || tb.top > b.bottom));
      return {pos: c.position, top: c.top, right: c.right, z: c.zIndex, hit,
              display: c.display};
    }""")
    ck(r["display"] == "flex", "toast visible after match", r["display"])
    ck(r["pos"] == "fixed" and r["top"] == "18px" and r["right"] == "18px",
       "position fixed, top 18px, right 18px", f"{r['pos']}/{r['top']}/{r['right']}")
    ck(r["z"] not in ("auto", "") and int(r["z"]) > 0, "z-index above the table", str(r["z"]))
    ck(not r["hit"], "toast box does not intersect any remaining Action cell", f"intersects={r['hit']}")


def qa_furn_03(page):
    page.evaluate("""() => { window.__alive = true; window.__bu = false;
      window.addEventListener('beforeunload', () => window.__bu = true);
      window.__hist = history.length; }""")
    open_m1_from_row1(page)
    page.click("#m-match .pmatch")
    _remove_first_row(page, "No action needed")
    r = page.evaluate("""() => ({alive: window.__alive === true, bu: window.__bu === true,
                                 histSame: history.length === window.__hist})""")
    ck(r["alive"] and not r["bu"] and r["histSame"],
       "no unload, no beforeunload, no new navigation entry", str(r))


def qa_furn_04(page):
    r = page.evaluate("""() => ({
      brand: window.qtxt(document.querySelector('.nav .brand')),
      menus: [...document.querySelectorAll('.nav > span')]
             .map(s => window.qtxt(s)).filter(t => t.includes('▾')),
      user: window.qtxt(document.querySelector('.nav .user')),
      avatar: window.qtxt(document.querySelector('.nav .avatar')),
      logout: window.qtxt(document.querySelector('.nav .logout'))})""")
    ck(r["brand"] == "SkinSeoul", "brand 'SkinSeoul'", r["brand"])
    ck(r["menus"] == ["Operation AI ▾", "Catalog Management ▾",
                      "OMS Center ▾", "Site Management ▾"],
       "four menu labels with ▾", str(r["menus"]))
    ck(r["user"] == "Y Yongwon Ryu" or r["user"] == "YYongwon Ryu",
       "user block 'Yongwon Ryu' with avatar", r["user"])
    ck(r["avatar"] == "Y", "avatar 'Y'", r["avatar"])
    ck(r["logout"] == "Logout", "Logout button", r["logout"])


def qa_furn_05(page):
    d = cs(page, "#matchToast", "display")
    ck(d == "none", "baseline toast display none", d)


# ───────────────────────── NEG-01 ─────────────────────────

def qa_neg_01(page):
    open_m1_from_row1(page)
    pc0 = txt(page, "#poolCount")
    ck(pc0 == "3", "precondition #poolCount 3", pc0)
    page.evaluate("""() => { window.__samples = [];
      const t = document.getElementById('matchToast');
      window.__iv = setInterval(() => window.__samples.push(getComputedStyle(t).display), 100); }""")
    page.evaluate("""() => { const b = document.querySelector('#m-match .pmatch');
      b.click(); b.click(); }""")
    time.sleep(6.2)
    samples = page.evaluate("() => { clearInterval(window.__iv); return window.__samples; }")
    pc, pcb, rows = pool_counts(page)
    ck(pc == "2" and rows == 2, "#poolCount 2 (never 1), one row removed",
       f"pc={pc} pcb={pcb} rows={rows}")
    # exactly one display cycle: flex... then none..., no flex after the first none
    joined = "".join("F" if s == "flex" else "N" for s in samples)
    ck(re.fullmatch(r"N*F+N+", joined) is not None,
       "one contiguous flex block then none for the rest of 6 s",
       f"pattern={joined}")


# ───────────────────────── EMPTY ─────────────────────────

def qa_empty_01(page):
    for _ in range(3):
        _remove_first_row(page, "No action needed")
    # §8.0 rule 3: '.mockwrap' matches two nested elements. The collapse guard measures
    # the OUTER wrapper (the one wrapping .mock, held at >= 520px by .mock's min-height).
    # The inner wrapper holds only the table and legitimately shrinks to the header row,
    # so it is not the collapse signal and must not be the measured element.
    r = page.evaluate("""() => {
      const wraps = [...document.querySelectorAll('.mockwrap')];
      const outer = wraps.find(w => w.querySelector('.mock'));
      const inner = wraps.find(w => w !== outer);
      const thead = document.querySelector('.mock table.tbl thead');
      const ths = thead ? thead.querySelectorAll('th').length : 0;
      const ph = document.querySelector('.poolhead');
      const pcb = document.getElementById('poolCountBottom');
      return {pc: window.qtxt(document.getElementById('poolCount')),
              pcbT: window.qtxt(pcb),
              phH: ph.getBoundingClientRect().height,
              outerFound: !!outer,
              outerH: outer ? outer.getBoundingClientRect().height : -1,
              innerH: inner ? inner.getBoundingClientRect().height : -1,
              ths,
              pcbBelow: pcb.getBoundingClientRect().top > thead.getBoundingClientRect().bottom};
    }""")
    ck(r["pc"] == "0" and r["pcbT"] == "0", "both counters read 0", f"{r['pc']}/{r['pcbT']}")
    ck(r["phH"] > 0, ".poolhead still rendered (height > 0)", f"h={r['phH']:.0f}px")
    ck(r["ths"] == 12, "thead still rendered with 12 th", f"{r['ths']} th")
    ck(r["pcbBelow"], "#poolCountBottom below the thead", str(r["pcbBelow"]))
    ck(r["outerFound"], "the outer .mockwrap (wrapping .mock) is identifiable",
       "no .mockwrap contains .mock")
    ck(r["outerH"] > 300, "outer .mockwrap bounding-box height > 300 px",
       f"outer .mockwrap height = {r['outerH']:.0f}px "
       f"(inner = {r['innerH']:.0f}px, not the measured element)")


def qa_empty_05(page):
    for path, act in [("Cancel", lambda: page.click("#m-match .foot button")),
                      ("header ✕", lambda: page.click("#m-match header .x")),
                      ("backdrop", lambda: page.mouse.click(10, 300))]:
        open_m1_from_row1(page)
        act()
        r = page.evaluate("""() => ({
          open: document.getElementById('m-match').classList.contains('open'),
          rows: document.querySelectorAll('.mock table.tbl tbody tr').length,
          pc: window.qtxt(document.getElementById('poolCount')),
          pcb: window.qtxt(document.getElementById('poolCountBottom'))})""")
        ck(not r["open"], f"[{path}] modal closed", f"open={r['open']}")
        ck(r["rows"] == 3 and r["pc"] == "3" and r["pcb"] == "3",
           f"[{path}] 3 rows remain, counters 3/3", str(r))


# ───────────────────────── A11Y ─────────────────────────

def qa_a11y_01(page):
    seq = []
    for _ in range(40):
        page.keyboard.press("Tab")
        d = page.evaluate("""() => { const a = document.activeElement;
          if (!a || a === document.body) return null;
          return {cls: a.className, t: (a.textContent || '').trim().slice(0, 30),
                  inRow1: !!a.closest('#poolrow1')}; }""")
        seq.append(d)
        if d and d["inRow1"] and "xdel" in (d["cls"] or ""):
            break
    idx_rm = next((i for i, d in enumerate(seq)
                   if d and d["inRow1"] and d["t"] == "Review & Match"), None)
    ck(idx_rm is not None, "Tab reaches row1 'Review & Match'",
       f"sequence={[(d or {}).get('t') for d in seq]}")
    nxt = seq[idx_rm + 1] if idx_rm + 1 < len(seq) else None
    ck(nxt and nxt["inRow1"] and "xdel" in nxt["cls"],
       "next Tab lands on row1 .xdel", str(nxt))


def qa_a11y_05(page):
    r = page.evaluate("""() => {
      const wraps = [...document.querySelectorAll('.mockwrap')];
      const pre = wraps.map(w => ({sw: w.scrollWidth, cw: w.clientWidth}));
      const ths = [...document.querySelectorAll('.mock table.tbl thead th')];
      const visible = ths.filter(t => t.getBoundingClientRect().width > 0).length;
      const order = ths.map(t => window.qtxt(t));
      const xdel = document.querySelector('#poolrow1 .xdel');
      xdel.scrollIntoView({block: 'center', inline: 'nearest'});
      wraps.forEach(w => w.scrollLeft = w.scrollWidth);
      const b = xdel.getBoundingClientRect();
      return {pre, visible, order,
              box: {l: b.left, r: b.right, t: b.top, b: b.bottom},
              vw: window.innerWidth, vh: window.innerHeight};
    }""")
    both = all(p["sw"] > p["cw"] for p in r["pre"][:2])
    ck(both, "both nested .mockwrap scrollWidth > clientWidth at 900 px",
       str(r["pre"]))
    ck(r["visible"] == 12 and r["order"][0] == "Tracking No" and r["order"][-1] == "Action",
       "12 th all rendered in original order", f"visible={r['visible']} order={r['order']}")
    box = r["box"]
    ck(box["l"] >= 0 and box["r"] <= r["vw"] and box["t"] >= 0 and box["b"] <= r["vh"],
       "row1 .xdel bounding box fully inside the 900 px viewport after scrolling both wrappers",
       str(box))


# ───────────────────────── WFQ ─────────────────────────

def qa_wfq_01(page):
    page.click(".mock table.tbl tbody tr:nth-of-type(2) [data-modal='m-match']")
    page.wait_for_selector("#m-match.open")
    s = txt(page, "#m-match .body > div .mut")
    ck("Tracking 10323100841207" in s and "8809416470726" in s,
       "M1 shows row 1's COSRX item (Tracking 10323100841207)", s)


def qa_wfq_02(page):
    _remove_first_row(page, "Registered by mistake")
    pc = txt(page, "#poolCount")
    ck(pc == "2", "after removing #poolrow1, count 2", pc)
    page.click(".wf-tab[data-modal='m-match']")
    page.wait_for_selector("#m-match.open")
    page.click("#m-match .pmatch")
    r = page.evaluate("""() => { const t = document.getElementById('matchToast');
      return {d: getComputedStyle(t).display,
              main: t.querySelector('span') ? t.querySelector('span').textContent : '',
              pc: window.qtxt(document.getElementById('poolCount'))}; }""")
    ck(r["d"] == "flex" and r["main"].startswith("✓ Matched to Order 414230"),
       "toast appears showing the match text", str(r))
    ck(r["pc"] == "2", "#poolCount stays 2 (no further decrement)", r["pc"])


def qa_wfq_03(page):
    page.click("#poolrow1 .xdel")
    page.wait_for_selector("#m-remove.open")
    r = page.evaluate("""() => ({
      open: document.getElementById('m-remove').classList.contains('open'),
      rows: document.querySelectorAll('.mock table.tbl tbody tr').length,
      pc: window.qtxt(document.getElementById('poolCount')),
      pcb: window.qtxt(document.getElementById('poolCountBottom')),
      toast: getComputedStyle(document.getElementById('matchToast')).display})""")
    ck(r["open"], "#m-remove opens", str(r["open"]))
    ck(r["rows"] == 3 and r["pc"] == "3" and r["pcb"] == "3",
       "no row removed, counters 3/3", str(r))
    ck(r["toast"] == "none", "no toast until Remove from pool is confirmed", r["toast"])


def qa_wfq_04(page):
    n = count(page, "a")
    tags = page.evaluate("""() => [...document.querySelectorAll('.mock table.tbl tbody td:nth-child(11) .num')]
      .map(e => e.tagName)""")
    ck(n == 0, "zero <a> elements in the document", f"{n} anchors")
    ck(tags and all(t == "SPAN" for t in tags),
       "every candidate order number is a <span>", str(tags))


def qa_wfq_05(page):
    _open_inbox(page)
    r = page.evaluate("""() => ({
      inputs: document.querySelectorAll('#inbox1 input').length,
      ph: document.querySelectorAll('#inbox1 [placeholder]').length})""")
    ck(r["inputs"] == 0 and r["ph"] == 0,
       "no search input, no placeholder element in #inbox1", str(r))


def qa_wfq_06(page):
    page.click("#annoToggle")
    r = page.evaluate("""() => ({
      cls: document.body.classList.contains('no-anno'),
      dotsHidden: [...document.querySelectorAll('.dot')].every(d => getComputedStyle(d).display === 'none'),
      legendHidden: getComputedStyle(document.querySelector('.legend')).display === 'none',
      t: document.getElementById('annoToggle').textContent})""")
    ck(r["cls"] and r["dotsHidden"] and r["legendHidden"] and r["t"] == "Show annotations",
       "body.no-anno; all .dot and .legend hidden; text 'Show annotations'", str(r))
    page.click("#annoToggle")
    r2 = page.evaluate("""() => ({
      cls: document.body.classList.contains('no-anno'),
      dotVis: getComputedStyle(document.querySelector('.dot')).display !== 'none',
      legendVis: getComputedStyle(document.querySelector('.legend')).display !== 'none',
      t: document.getElementById('annoToggle').textContent})""")
    ck(not r2["cls"] and r2["dotVis"] and r2["legendVis"] and r2["t"] == "Hide annotations",
       "second click restores dots/legend and 'Hide annotations'", str(r2))


def qa_wfq_07(page):
    page.evaluate("""() => { const b = document.querySelector('#poolrow1 .xdel');
      b.click(); b.click(); }""")
    r = page.evaluate("""() => ({
      nOpen: document.querySelectorAll('.overlay.open').length,
      rmOpen: document.getElementById('m-remove').classList.contains('open'),
      rows: document.querySelectorAll('.mock table.tbl tbody tr').length})""")
    ck(r["nOpen"] == 1 and r["rmOpen"], "exactly one #m-remove overlay open", str(r))
    ck(r["rows"] == 3, "no row removed by the double ✕ click", f"rows={r['rows']}")
    page.select_option("#rmReason", label="Registered by mistake")
    page.evaluate("""() => { window.__samples = [];
      const t = document.getElementById('matchToast');
      window.__iv = setInterval(() => window.__samples.push(getComputedStyle(t).display), 100); }""")
    page.evaluate("""() => { const c = document.getElementById('rmConfirm');
      c.click(); c.click(); }""")
    time.sleep(5.0)
    samples = page.evaluate("() => { clearInterval(window.__iv); return window.__samples; }")
    pc, pcb, rows = pool_counts(page)
    ck(rows == 2 and pc == "2" and pcb == "2",
       "exactly one row removed; counters 2/2 == rendered rows",
       f"rows={rows} pc={pc} pcb={pcb}")
    joined = "".join("F" if s == "flex" else "N" for s in samples)
    ck(re.fullmatch(r"N*F+N+", joined) is not None,
       "exactly one toast display cycle", f"pattern={joined}")


# ───────────────────────── harness ─────────────────────────

SIMPLE = [
    ("QA-LOAD-01", qa_load_01), ("QA-LOAD-02", qa_load_02), ("QA-LOAD-03", qa_load_03),
    ("QA-LOAD-04", qa_load_04), ("QA-LOAD-05", qa_load_05), ("QA-LOAD-06", qa_load_06),
    ("QA-LOAD-07", qa_load_07), ("QA-LOAD-08", qa_load_08), ("QA-LOAD-09", qa_load_09),
    ("QA-LOAD-10", qa_load_10), ("QA-LOAD-11", qa_load_11),
    ("QA-ROW-01", qa_row_01), ("QA-ROW-02", qa_row_02), ("QA-ROW-03", qa_row_03),
    ("QA-ROW-04", qa_row_04), ("QA-ROW-05", qa_row_05), ("QA-ROW-06", qa_row_06),
    ("QA-ROW-07", qa_row_07), ("QA-ROW-09", qa_row_09),
    ("QA-SUS-01", qa_sus_01), ("QA-SUS-02", qa_sus_02), ("QA-SUS-03", qa_sus_03),
    ("QA-SUS-04", qa_sus_04), ("QA-SUS-05", qa_sus_05),
    ("QA-M1-01", qa_m1_01), ("QA-M1-02", qa_m1_02), ("QA-M1-03", qa_m1_03),
    ("QA-M1-04", qa_m1_04), ("QA-M1-05", qa_m1_05), ("QA-M1-06", qa_m1_06),
    ("QA-M1-07", qa_m1_07), ("QA-M1-09", qa_m1_09), ("QA-M1-10", qa_m1_10),
    ("QA-XDEL-01", qa_xdel_01), ("QA-XDEL-02", qa_xdel_02), ("QA-XDEL-03", qa_xdel_03),
    ("QA-CMT-01", qa_cmt_01), ("QA-CMT-02", qa_cmt_02), ("QA-CMT-03", qa_cmt_03),
    ("QA-CMT-04", qa_cmt_04), ("QA-CMT-05", qa_cmt_05), ("QA-CMT-06", qa_cmt_06),
    ("QA-CMT-11", qa_cmt_11),
    ("QA-FURN-01", qa_furn_01), ("QA-FURN-02", qa_furn_02), ("QA-FURN-03", qa_furn_03),
    ("QA-FURN-04", qa_furn_04), ("QA-FURN-05", qa_furn_05),
    ("QA-NEG-01", qa_neg_01),
    ("QA-EMPTY-01", qa_empty_01), ("QA-EMPTY-05", qa_empty_05),
    ("QA-A11Y-01", qa_a11y_01),
    ("QA-WFQ-01", qa_wfq_01), ("QA-WFQ-02", qa_wfq_02), ("QA-WFQ-03", qa_wfq_03),
    ("QA-WFQ-04", qa_wfq_04), ("QA-WFQ-05", qa_wfq_05), ("QA-WFQ-06", qa_wfq_06),
    ("QA-WFQ-07", qa_wfq_07),
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1600, "height": 1000})
        ctx.add_init_script(INIT_JS)
        page = ctx.new_page()

        for sid, fn in SIMPLE:
            try:
                fresh(page)
                fn(page)
                record(sid, "PASS")
            except Fail as f:
                record(sid, "FAIL", f.expected, f.actual)
            except Exception as e:
                record(sid, "ERROR", "", f"{type(e).__name__}: {e}")

        # QA-ROW-08 (needs CDP handle)
        try:
            fresh(page)
            note = qa_row_08(page, {"page": page})
            record("QA-ROW-08", "PASS", note=note or "")
        except Fail as f:
            record("QA-ROW-08", "FAIL", f.expected, f.actual)
        except Exception as e:
            record("QA-ROW-08", "ERROR", "", f"{type(e).__name__}: {e}")

        # MATCH chain (01..05, one session)
        try:
            match_chain(page)
        except Exception as e:
            for sid in [f"QA-MATCH-{i:02d}" for i in range(1, 6)]:
                if not any(r["id"] == sid for r in RESULTS):
                    record(sid, "ERROR", "", f"{type(e).__name__}: {e}")

        # A11Y-05 needs a 900 px viewport
        try:
            ctx2 = browser.new_context(viewport={"width": 900, "height": 900})
            ctx2.add_init_script(INIT_JS)
            p2 = ctx2.new_page()
            p2.goto(URL)
            p2.wait_for_selector("#poolCount")
            qa_a11y_05(p2)
            record("QA-A11Y-05", "PASS")
            ctx2.close()
        except Fail as f:
            record("QA-A11Y-05", "FAIL", f.expected, f.actual)
        except Exception as e:
            record("QA-A11Y-05", "ERROR", "", f"{type(e).__name__}: {e}")

        browser.close()

    order = {"FAIL": 0, "ERROR": 1, "PASS": 2}
    RESULTS.sort(key=lambda r: (order.get(r["status"], 3), r["id"]))
    npass = sum(1 for r in RESULTS if r["status"] == "PASS")
    nfail = sum(1 for r in RESULTS if r["status"] == "FAIL")
    nerr = sum(1 for r in RESULTS if r["status"] == "ERROR")
    summary = {
        "wireframe": str(WF_FILE),
        "total": len(RESULTS),
        "pass": npass,
        "fail": nfail,
        "error": nerr,
        "results": RESULTS,
    }
    # HANDOFF.md §4 documents `python3 qa-<screen>.py [--json out.json]` for all eight
    # runners. Without this the flag is accepted, nothing is written, and the run still
    # exits 0 — a pass rate with no artefact behind it.
    if "--json" in sys.argv:
        _out = sys.argv[sys.argv.index("--json") + 1]
        _p = pathlib.Path(_out)
        _p.parent.mkdir(parents=True, exist_ok=True)
        with open(_p, "w", encoding="utf-8") as _f:
            json.dump(summary, _f, ensure_ascii=False, indent=1)
        print("wrote", _p)
    print(json.dumps(summary, ensure_ascii=False, indent=1))
    # Machine-readable tail line for the supervisor's aggregator (last line of stdout).
    print(f"== SUMMARY == PASS {npass} · FAIL {nfail} · ERROR {nerr}")


if __name__ == "__main__":
    main()
