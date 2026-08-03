#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adversarial QA execution of specs/tracking-missing.md  §8  (all [WF] scenarios).

Method-2 rules:
  * Execute each scenario EXACTLY as written, using ONLY the selectors / labels /
    strings the spec supplies.
  * If the spec does not say what to click or what to assert -> AMBIGUOUS.
  * Do NOT improvise from prior knowledge of the page.

Verdicts: PASS | FAIL | AMBIGUOUS | UNRUNNABLE
Run:  python3 qa-tracking-missing.py            (headless chromium)
      python3 qa-tracking-missing.py --json     (machine-readable)
"""
import json
import sys
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]          # .../wms2
URL = (ROOT / "tracking-missing" / "index.html").as_uri()
CLOSING = ROOT / "closing" / "index.html"

RESULTS = []          # (id, verdict, evidence)


def rec(sid, verdict, evidence):
    RESULTS.append((sid, verdict, evidence))


def q(s):
    """quote for evidence, keep it one line"""
    return repr(s)[:400]


# ── spec-declared baseline ────────────────────────────────────────────────────
BASE_JS_SENTINEL = """
window.__qa = {nav: 0, beforeunload: 0, hist0: history.length};
window.addEventListener('beforeunload', () => window.__qa.beforeunload++);
"""


def reset(page):
    """Spec §8.0 'Reset procedure for [WF] runs': reload the page."""
    page.goto(URL, wait_until="load")
    page.evaluate(BASE_JS_SENTINEL)


def baseline_ok(page):
    return page.evaluate("""() => ({
      poolCount: document.getElementById('poolCount').textContent,
      poolCountBottom: document.getElementById('poolCountBottom').textContent,
      rowHits: document.querySelectorAll('.row-hit').length,
      row1: !!document.getElementById('poolrow1'),
      mOpen: document.getElementById('m-match').classList.contains('open'),
      inboxOpen: document.getElementById('inbox1').classList.contains('open'),
      toast: getComputedStyle(document.getElementById('matchToast')).display,
      anno: !document.body.classList.contains('no-anno'),
    })""")


# ══════════════════════════════════════════════════════════════════════════════
# 8.1  Block LOAD
# ══════════════════════════════════════════════════════════════════════════════
def load(page):
    reset(page)

    # QA-LOAD-01
    t = page.eval_on_selector("h2", "e => e.textContent")
    rec("QA-LOAD-01", "PASS" if t == "WMS - Unrecognized Tracking List" else "FAIL",
        f"<h2> textContent = {q(t)}")

    # QA-LOAD-02
    sub = page.eval_on_selector(".sub", "e => e.textContent")
    mut = page.eval_on_selector(".sub .mut", "e => e.textContent")
    ok = ("Unrecognized & missing-tracking status" in sub and
          "Coupang creates the order number immediately but generates the tracking number a few hours later" in mut)
    rec("QA-LOAD-02", "PASS" if ok else "FAIL", f".sub={q(sub)}")

    # QA-LOAD-03
    ph = page.evaluate("""() => {
      const e = document.querySelector('.poolhead'), cs = getComputedStyle(e);
      return {bg: cs.backgroundColor, bc: cs.borderTopColor,
              b: e.querySelector('b').textContent};
    }""")
    ok = (ph["bg"] == "rgb(255, 251, 214)" and ph["bc"] == "rgb(245, 158, 11)"
          and ph["b"] == "⚠ Unrecognized product pool · 3 items")
    rec("QA-LOAD-03", "PASS" if ok else "FAIL", json.dumps(ph, ensure_ascii=False))

    # QA-LOAD-04 -- literal reading: <th> texts EXACTLY, in order.
    expect = ["Tracking No", "Order No", "Product Name", "Product Name KR", "Size",
              "Barcode", "Qty", "Memo", "Registrant (Center)", "Registered At",
              "Suspected Orders (Auto-matched)", "Action"]
    got = page.evaluate(
        "() => [...document.querySelectorAll('table.tbl')[0].querySelectorAll('th')].map(t=>t.textContent)")
    got_stripped = page.evaluate("""() => [...document.querySelectorAll('table.tbl')[0]
        .querySelectorAll('th')].map(t=>{const c=t.cloneNode(true);
        c.querySelectorAll('.dot').forEach(d=>d.remove());return c.textContent;})""")
    if got == expect:
        rec("QA-LOAD-04", "PASS", "12 headers exact")
    else:
        note = ("passes only after removing the annotation .dot children (spec gives no such instruction); "
                f"stripped={got_stripped}")
        rec("QA-LOAD-04", "FAIL",
            f"spec: {expect[2]!r}/{expect[10]!r}/{expect[11]!r}; page: "
            f"{got[2]!r}/{got[10]!r}/{got[11]!r} -- {note}")

    # QA-LOAD-05
    d = page.evaluate("""() => {
      const tb = document.querySelectorAll('table.tbl')[0].querySelector('tbody');
      const trs = [...tb.querySelectorAll('tr')];
      return {pc: poolCount.textContent, pcb: poolCountBottom.textContent,
              n: trs.length, allHit: trs.every(r=>r.classList.contains('row-hit')),
              nTbodies: document.querySelectorAll('table.tbl tbody').length};
    }""")
    ok = d["pc"] == "3" and d["pcb"] == "3" and d["n"] == 3 and d["allHit"]
    rec("QA-LOAD-05", "PASS" if ok else "FAIL",
        json.dumps(d) + "  [note: 2 'table.tbl tbody' exist; spec says 'the <tbody>' -- scoped to the pool table]")

    # QA-LOAD-06 (neg)
    sels = ['.searchbar', '.pager', '.bulkbar', '.picava', '.picname', '.cntchip',
            '.wait', '.slack-pill', '.logsec', 'input[type=checkbox]']
    hits = page.evaluate("(s) => s.filter(x => document.querySelectorAll(x).length)", sels)
    rec("QA-LOAD-06", "PASS" if not hits else "FAIL", f"rendered matches = {hits}")

    # QA-LOAD-07
    d = page.evaluate("""() => ({
      li: [...document.querySelectorAll('.legend ol > li')].length,
      ns: [...document.querySelectorAll('.legend ol > li .n')].map(n=>n.textContent),
      dots: document.querySelectorAll('.dot').length,
      m1dot: !!document.querySelector('#m-match .dot')})""")
    ok = d["li"] == 6 and d["ns"] == ["0", "1", "2", "3", "4", "5"] and d["dots"] == 7 and d["m1dot"]
    rec("QA-LOAD-07", "PASS" if ok else "FAIL", json.dumps(d))

    # QA-LOAD-08
    d = page.evaluate("""() => {
      const ol = document.querySelector('.legend ol');
      const ps = []; let n = ol.nextElementSibling;
      while (n) { if (n.tagName === 'P') ps.push(n.textContent); n = n.nextElementSibling; }
      return ps;}""")
    ok = (len(d) == 2 and "2026-07-23 simplification decision:" in d[0]
          and "(Confirmed 2026-08-02) Unrequested inbound shipments also use this pool" in d[1])
    rec("QA-LOAD-08", "PASS" if ok else "FAIL", f"{len(d)} <p> after legend <ol>; first60={q(d[0][:60]) if d else None}")

    # QA-LOAD-09 (neg)
    n = page.evaluate("() => document.querySelectorAll('input').length")
    rec("QA-LOAD-09", "PASS" if n == 0 else "FAIL", f"<input> count = {n}")

    # QA-LOAD-10 (neg)
    d = page.evaluate("""() => ({
      printText: document.body.textContent.includes('Print'),
      audio: document.querySelectorAll('audio').length,
      ac: [...document.querySelectorAll('script')].some(s=>/AudioContext/.test(s.textContent)),
      greens: [...document.querySelectorAll('.btn-green')].map(b=>b.textContent)})""")
    ok = (not d["printText"] and d["audio"] == 0 and not d["ac"]
          and d["greens"] == ["Match to this product", "Match to this product"])
    rec("QA-LOAD-10", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    # QA-LOAD-11
    d = page.evaluate("""() => ({
      h1: document.querySelector('.wf-bar h1').textContent,
      tab: [...document.querySelectorAll('.wf-tab')].map(b=>b.textContent),
      anno: document.getElementById('annoToggle').textContent})""")
    ok = (d["h1"] == "WMS 2.0 · Unrecognized Tracking Wireframe"
          and "Modal: Match Review (M1)" in d["tab"] and d["anno"] == "Hide annotations")
    rec("QA-LOAD-11", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))


# ══════════════════════════════════════════════════════════════════════════════
# 8.2  Block ROW
# ══════════════════════════════════════════════════════════════════════════════
def row(page):
    reset(page)
    cells = "(r,i) => r.querySelectorAll('td')[i]"

    d = page.evaluate("""() => {
      const r = document.getElementById('poolrow1'), td = r.querySelectorAll('td');
      return {c0: td[0].textContent, c1: td[1].textContent,
              c1col: getComputedStyle(td[1]).color,
              c1cp: td[1].textContent.codePointAt(0)};}""")
    ok = d["c0"] == "10323100841207" and d["c1"] == "–" and d["c1col"] == "rgb(126, 124, 131)"
    rec("QA-ROW-01", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    d = page.evaluate("""() => {const td=document.getElementById('poolrow1').querySelectorAll('td')[2];
      return {b: td.querySelector('b')?.textContent, rest: td.querySelector('b')?.nextSibling?.textContent};}""")
    ok = d["b"] == "COSRX" and d["rest"] == " Advanced Snail 96 Mucin Power Essence, 100ml"
    rec("QA-ROW-02", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    d = page.evaluate("""() => {const td=document.getElementById('poolrow1').querySelectorAll('td')[3];
      return {b: td.querySelector('b')?.textContent, rest: td.querySelector('b')?.nextSibling?.textContent};}""")
    ok = d["b"] == "COSRX" and d["rest"] == " 어드밴스드 스네일 96 뮤신 에센스"
    rec("QA-ROW-03", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    d = page.evaluate("""() => {const r=document.querySelectorAll('table.tbl')[0]
        .querySelectorAll('tbody tr')[2], td=r.querySelectorAll('td');
      return {en: td[2].querySelector('b').textContent,
              kr: td[3].querySelector('b').textContent,
              krRest: td[3].querySelector('b').nextSibling.textContent};}""")
    ok = (d["en"] == "medicube" and d["kr"] == "Medicube"
          and d["krRest"] == " 제로 모공 패드 2.0 (1+1)")
    rec("QA-ROW-04", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    grid = page.evaluate("""() => [...document.querySelectorAll('table.tbl')[0]
        .querySelectorAll('tbody tr')].map(r=>[...r.querySelectorAll('td')].map(t=>t.textContent))""")
    ok = ([g[4] for g in grid] == ["100ml", "250ml", "70ea"]
          and [g[5] for g in grid] == ["8809416470726", "8809640733458", "8809894261234"]
          and [g[6] for g in grid] == ["1", "1", "2"])
    rec("QA-ROW-05", "PASS" if ok else "FAIL",
        f"size={[g[4] for g in grid]} barcode={[g[5] for g in grid]} qty={[g[6] for g in grid]}")

    memos = [g[7] for g in grid]
    rec("QA-ROW-06", "PASS" if memos == ["Box label damaged", "–", "Looks like a 1+1 set"] else "FAIL",
        f"memos={memos!r}")

    regs, ats = [g[8] for g in grid], [g[9] for g in grid]
    ok = regs == ["Miranti", "Dean", "Dean"] and ats == ["07-13 10:12", "07-13 09:48", "07-13 09:30"]
    rec("QA-ROW-07", "PASS" if ok else "FAIL", f"registrant={regs} at={ats}")

    # QA-ROW-08 : descending order + "no <th> click handler, no sort glyph"
    cdp = page.context.new_cdp_session(page)
    listeners = []
    try:
        doc = cdp.send("DOM.getDocument", {"depth": -1})
        nodes = cdp.send("DOM.querySelectorAll",
                         {"nodeId": doc["root"]["nodeId"], "selector": "table.tbl th"})
        for nid in nodes["nodeIds"]:
            obj = cdp.send("DOM.resolveNode", {"nodeId": nid})
            ls = cdp.send("DOMDebugger.getEventListeners",
                          {"objectId": obj["object"]["objectId"]})
            listeners += [l["type"] for l in ls.get("listeners", [])]
        listener_probe = f"CDP getEventListeners on all th = {listeners}"
    except Exception as e:                                          # pragma: no cover
        listener_probe = f"CDP probe failed: {e}"
    glyphs = page.evaluate(
        "() => [...document.querySelectorAll('table.tbl')[0].querySelectorAll('th')]"
        ".filter(t=>/[\\u25b2\\u25bc\\u2191\\u2193\\u2b06\\u2b07\\u21c5]/.test(t.textContent)).length")
    onclicks = page.evaluate(
        "() => [...document.querySelectorAll('table.tbl th')].filter(t=>t.getAttribute('onclick')).length")
    ok = ats == ["07-13 10:12", "07-13 09:48", "07-13 09:30"] and not listeners and glyphs == 0 and onclicks == 0
    rec("QA-ROW-08", "PASS" if ok else "FAIL",
        f"desc order OK; sort glyphs={glyphs}; onclick attrs={onclicks}; {listener_probe}")

    d = page.evaluate("() => [...document.querySelectorAll('tr[id]')].map(r=>r.id)")
    rec("QA-ROW-09", "PASS" if d == ["poolrow1"] else "FAIL", f"tr[id] = {d}")


# ══════════════════════════════════════════════════════════════════════════════
# 8.3  Block SUS
# ══════════════════════════════════════════════════════════════════════════════
def sus(page):
    reset(page)
    n = page.evaluate("() => document.getElementById('poolrow1').querySelectorAll('td')[10].querySelectorAll('div').length")
    rec("QA-SUS-01", "PASS" if n == 2 else "FAIL", f"candidate <div> count = {n}")

    d = page.evaluate("""() => {
      const c = document.getElementById('poolrow1').querySelectorAll('td')[10];
      const l = c.querySelectorAll('div')[0];
      const ord = l.querySelectorAll('span')[0], mut = l.querySelector('.mut');
      return {text: l.textContent, b: l.querySelector('b').textContent,
              ordText: ord.textContent, ordColor: getComputedStyle(ord).color,
              ordWeight: getComputedStyle(ord).fontWeight,
              mutText: mut.textContent, mutColor: getComputedStyle(mut).color};}""")
    ok = (d["text"] == "Dean · Order 414230 · JIT (Naver) · Processing"
          and d["b"] == "Dean" and d["ordText"] == "Order 414230"
          and d["ordColor"] == "rgb(13, 110, 253)" and d["ordWeight"] == "700"
          and d["mutText"] == "JIT (Naver) · Processing")
    rec("QA-SUS-02", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    t = page.evaluate("() => document.getElementById('poolrow1').querySelectorAll('td')[10].querySelectorAll('div')[1].textContent")
    rec("QA-SUS-03", "PASS" if t == "Egita · Order 413871 · JIT (Official Mall) · Processing" else "FAIL",
        q(t))

    d = page.evaluate("""() => [...document.querySelectorAll('table.tbl')[0].querySelectorAll('tbody tr')]
        .slice(1).map(r=>{const c=r.querySelectorAll('td')[10];
        return {n: c.querySelectorAll('div').length, t: c.textContent};})""")
    ok = (d[0]["n"] == 1 and d[1]["n"] == 1
          and d[0]["t"] == "Harshit · Order 414102 · JIT (Naver) · Processing"
          and d[1]["t"] == "Miranti · Order 413998 · JIT (Official Mall) · Processing")
    rec("QA-SUS-04", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    # QA-SUS-05 (neg) -- "any route/channel label on the page": no selector given.
    reading_a = page.evaluate("""() => [...document.querySelectorAll(
        '.tag-jit,.tag-smartbuy,.tag-wholesale,.tag-partnership')].map(e=>{
        const cs=getComputedStyle(e);
        return {t:e.textContent,bg:cs.backgroundColor,color:cs.color,
                bw:cs.borderTopWidth+'/'+cs.borderLeftWidth};})""")
    reading_b = page.evaluate("""() => [...document.querySelectorAll('table.tbl')[0]
        .querySelectorAll('tbody tr td:nth-child(11) .mut')].map(e=>{
        const cs=getComputedStyle(e);
        return {t:e.textContent,bg:cs.backgroundColor,color:cs.color,
                bw:cs.borderTopWidth+'/'+cs.borderLeftWidth};})""")
    a_ok = all(x["bg"] == "rgba(0, 0, 0, 0)" and x["color"] == "rgb(20, 16, 27)"
               and x["bw"] == "0px/0px" for x in reading_a)
    b_ok = all(x["bg"] == "rgba(0, 0, 0, 0)" and x["color"] == "rgb(20, 16, 27)"
               and x["bw"] == "0px/0px" for x in reading_b)
    rec("QA-SUS-05", "AMBIGUOUS",
        "spec gives no selector for 'route/channel label'. "
        f"Reading A (.tag-jit etc, modal-only, n={len(reading_a)}): {'satisfies' if a_ok else 'violates'} the assertion. "
        f"Reading B (pool-cell route text '.mut' in the Suspected Orders column, n={len(reading_b)}): "
        f"{'satisfies' if b_ok else 'VIOLATES'} -- e.g. {json.dumps(reading_b[0], ensure_ascii=False) if reading_b else '-'} "
        "(colour is ink-3 rgb(126,124,131), not the ink rgb(20,16,27) the spec demands)")


# ══════════════════════════════════════════════════════════════════════════════
# 8.4  Block M1
# ══════════════════════════════════════════════════════════════════════════════
def m1(page):
    reset(page)
    page.click("#poolrow1 >> text=Review & Match")
    d = page.evaluate("""() => ({open: document.getElementById('m-match').classList.contains('open'),
        hdr: document.querySelector('#m-match header').textContent,
        hdrFirstNode: document.querySelector('#m-match header').firstChild.textContent})""")
    if d["open"] and d["hdr"] == "Review & Match — Unrecognized Product":
        rec("QA-M1-01", "PASS", json.dumps(d, ensure_ascii=False))
    else:
        rec("QA-M1-01", "FAIL",
            f"open={d['open']}; spec: <header> text is EXACTLY 'Review & Match — Unrecognized Product'; "
            f"page: {q(d['hdr'])} -- the header also contains the close button '✕' "
            f"(text node alone = {q(d['hdrFirstNode'])})")

    reset(page)
    page.click(".wf-tab")
    rec("QA-M1-02",
        "PASS" if page.evaluate("() => document.getElementById('m-match').classList.contains('open')") else "FAIL",
        "wf-bar demo button opens #m-match")

    d = page.evaluate("""() => {
      const card = document.querySelector('#m-match .body > div');
      return {b: card.querySelector('b').textContent,
              rest: card.querySelector('b').nextSibling.textContent,
              mut: card.querySelector('.mut').textContent};}""")
    expect_mut = ('Barcode 8809416470726 · Tracking 10323100841207 · No order number · 1 unit '
                  '· Registered by: Miranti (Center) 07-13 10:12 · Memo "Box label damaged"')
    ok = d["b"] == "COSRX" and d["rest"] == " Advanced Snail 96 Mucin Power Essence, 100ml" and d["mut"] == expect_mut
    rec("QA-M1-03", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    d = page.evaluate("""() => {
      const panel = document.querySelectorAll('#m-match .body > div')[1];
      return {b: panel.querySelector('b').textContent, mut: panel.querySelector('.mut').textContent};}""")
    ok = (d["b"] == "Suspected orders (auto-matched)"
          and "Match by selecting a product line, not the order" in d["mut"])
    rec("QA-M1-04", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    ths = page.evaluate("() => [...document.querySelectorAll('#m-match thead th')].map(t=>t.textContent)")
    rec("QA-M1-05", "PASS" if ths == ["Order", "PIC", "Channel", "Included Product", ""] else "FAIL", f"{ths!r}")

    d = page.evaluate("""() => [...document.querySelectorAll('#m-match tbody tr')].map(r=>{
        const td=[...r.querySelectorAll('td')];
        return {cells: td.slice(0,4).map(t=>t.textContent),
                bold: td[3].querySelector('b')?.textContent,
                btn: td[4].querySelector('button')?.textContent};})""")
    ok = (len(d) == 2
          and d[0]["cells"] == ["414230", "Dean", "JIT (Naver)", "COSRX Snail 96 Essence ×1"]
          and d[1]["cells"] == ["413871", "Egita", "JIT (Official Mall)", "COSRX Snail 96 Essence ×1"]
          and all(x["bold"] == "COSRX" and x["btn"] == "Match to this product" for x in d))
    rec("QA-M1-06", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    note = page.eval_on_selector("#m-match .note", "e => e.textContent")
    frags = ["tracking number 10323100841207 is registered to the selected product line",
             "this item disappears from the pool",
             '"@Miranti (unrecognized registrant) Matched the unrecognized product (COSRX Snail 96 Essence) to this order"']
    missing = [f for f in frags if f not in note]
    rec("QA-M1-07", "PASS" if not missing else "FAIL",
        f"missing fragments = {missing}" if missing else "all 3 fragments present")

    d = page.evaluate("""() => {
      const foot = document.querySelector('#m-match .foot');
      const btns = [...foot.querySelectorAll('button')].map(b=>b.textContent);
      const bad = [...document.querySelectorAll('#m-match button')]
        .map(b=>b.textContent.trim())
        .filter(t=>['Confirm','OK','Save','Match'].includes(t));
      return {footBtns: btns, bad};}""")
    ok = d["footBtns"] == ["Cancel"] and not d["bad"]
    rec("QA-M1-09", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    d = page.evaluate("""() => [...document.querySelectorAll('#m-match tbody tr td:nth-child(3) span')].map(e=>{
        const cs=getComputedStyle(e);
        return {t:e.textContent, bg:cs.backgroundColor, pad:cs.padding, color:cs.color};})""")
    ok = (len(d) == 2 and [x["t"] for x in d] == ["JIT (Naver)", "JIT (Official Mall)"]
          and all(x["bg"] == "rgba(0, 0, 0, 0)" and x["pad"] == "0px" and x["color"] == "rgb(20, 16, 27)" for x in d))
    rec("QA-M1-10", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))


# ══════════════════════════════════════════════════════════════════════════════
# 8.5  Block MATCH
# ══════════════════════════════════════════════════════════════════════════════
def match(page):
    reset(page)
    page.click("#poolrow1 >> text=Review & Match")
    page.evaluate("() => window.__qa.href = location.href")
    page.click("#m-match tbody tr:nth-child(1) .pmatch")

    rec("QA-MATCH-01",
        "PASS" if not page.evaluate("() => document.getElementById('m-match').classList.contains('open')") else "FAIL",
        "#m-match class list no longer contains 'open'")
    rec("QA-MATCH-02",
        "PASS" if page.evaluate("() => !document.getElementById('poolrow1')") else "FAIL",
        "#poolrow1 removed from DOM")
    d = page.evaluate("() => [poolCount.textContent, poolCountBottom.textContent]")
    rec("QA-MATCH-03", "PASS" if d == ["2", "2"] else "FAIL", f"counters = {d}")

    d = page.evaluate("""() => {const t=document.getElementById('matchToast'), cs=getComputedStyle(t);
        return {display: cs.display, bg: cs.backgroundColor, text: t.textContent,
                span: t.querySelector('span').textContent, small: t.querySelector('small').textContent};}""")
    ok = (d["display"] == "flex" and d["bg"] == "rgb(25, 135, 84)"
          and d["span"] == "✓ Matched to Order 414230 · COSRX Snail 96"
          and d["small"] == "Tracking 10323100841207 registered · removed from pool · @Miranti notified via Slack")
    rec("QA-MATCH-04", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    page.wait_for_timeout(4600)
    d = page.evaluate("""() => ({display: getComputedStyle(matchToast).display,
        unloaded: window.__qa === undefined, beforeunload: window.__qa?.beforeunload,
        sameHref: window.__qa?.href === location.href})""")
    ok = d["display"] == "none" and not d["unloaded"] and d["beforeunload"] == 0 and d["sameHref"]
    rec("QA-MATCH-05", "PASS" if ok else "FAIL", json.dumps(d))


# ══════════════════════════════════════════════════════════════════════════════
# 8.6  Block XDEL
# ══════════════════════════════════════════════════════════════════════════════
def xdel(page):
    reset(page)
    page.evaluate("""() => {window.__qa.overlayOpenSeen = false;
      new MutationObserver(()=>{ if(document.querySelector('.overlay.open')) window.__qa.overlayOpenSeen = true; })
        .observe(document.documentElement,{subtree:true,attributes:true,attributeFilter:['class']});
      window.__qa.toastSeen = false;
      setInterval(()=>{ if(getComputedStyle(matchToast).display!=='none') window.__qa.toastSeen=true; },20);}""")
    page.click("table.tbl tbody tr:nth-of-type(2) .xdel")
    d = page.evaluate("""() => ({rows: document.querySelectorAll('table.tbl')[0].querySelectorAll('tbody tr').length,
        trk: [...document.querySelectorAll('table.tbl')[0].querySelectorAll('tbody tr')]
               .map(r=>r.querySelectorAll('td')[0].textContent),
        pc: poolCount.textContent, pcb: poolCountBottom.textContent})""")
    ok = d["rows"] == 2 and "10323100838455" not in d["trk"] and d["pc"] == "2" and d["pcb"] == "2"
    rec("QA-XDEL-01", "PASS" if ok else "FAIL", json.dumps(d))

    page.wait_for_timeout(200)
    d = page.evaluate("() => ({ov: window.__qa.overlayOpenSeen, toast: window.__qa.toastSeen, "
                      "now: getComputedStyle(matchToast).display})")
    ok = not d["ov"] and not d["toast"] and d["now"] == "none"
    rec("QA-XDEL-02", "PASS" if ok else "FAIL", json.dumps(d))

    reset(page)
    for _ in range(3):
        page.click("table.tbl tbody tr:nth-of-type(1) .xdel")
    d = page.evaluate("() => [poolCount.textContent, poolCountBottom.textContent]")
    ok = d == ["0", "0"] and not any(v.startswith("-") for v in d)
    rec("QA-XDEL-03", "PASS" if ok else "FAIL", f"counters after 3 removals = {d}")


# ══════════════════════════════════════════════════════════════════════════════
# 8.7  Block CMT
# ══════════════════════════════════════════════════════════════════════════════
def cmt(page):
    reset(page)
    d = page.evaluate("""() => {
      const b=[...document.querySelectorAll('.nav button')].find(x=>x.textContent.startsWith('💬 Comments'));
      return {found: !!b, text: b?.textContent, badge: b?.querySelector('.badge-n')?.textContent};}""")
    ok = d["found"] and d["badge"] == "3"
    rec("QA-CMT-01", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    page.click("[data-open='inbox1']")
    d = page.evaluate("""() => ({open: inbox1.classList.contains('open'),
        tabs: [...document.querySelectorAll('#inbox1 .tabs button')].map(b=>b.textContent),
        badge: document.querySelector('#inbox1 .tabs .badge-n')?.textContent})""")
    ok = (d["open"] and d["tabs"][0].startswith("@ Mentions") and d["badge"] == "3"
          and d["tabs"][1] == "★ Saved")
    rec("QA-CMT-02", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    d = page.evaluate("""() => {
      const p=document.querySelector('#inbox1 [data-pane=mentions]');
      const h=p.querySelector('.paneheader');
      return {hdr: h.textContent, small: h.querySelector('small').textContent,
              smallML: getComputedStyle(h.querySelector('small')).marginLeft,
              items: p.querySelectorAll('.it').length,
              unread: p.querySelectorAll('.it.unread').length};}""")
    ok = ("Comments mentioning me" in d["hdr"] and d["small"] == "Mark all read"
          and d["items"] == 4 and d["unread"] == 3)
    rec("QA-CMT-03", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    d = page.evaluate("""() => {
      const it=document.querySelectorAll('#inbox1 [data-pane=mentions] .it')[1];
      return {entity: it.querySelector('b').textContent, body: it.querySelector('.body').textContent,
              time: it.querySelector('time').textContent};}""")
    ok = (d["entity"] == "Unrecognized pool" and d["time"] == "10:12"
          and 'Miranti: "@Yongwon Left a memo on the Snail essence (box label damaged). '
              'Please check whose order this is"' in d["body"])
    rec("QA-CMT-04", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    page.click("#inbox1 .tabs button[data-tab='saved']")
    d = page.evaluate("""() => {
      const m=document.querySelector('#inbox1 [data-pane=mentions]'), s=document.querySelector('#inbox1 [data-pane=saved]');
      return {mentionsDisplay: getComputedStyle(m).display, savedDisplay: getComputedStyle(s).display,
              hdr: s.querySelector('.paneheader').textContent,
              items: s.querySelectorAll('.it').length,
              entity: s.querySelector('.it b').textContent};}""")
    ok = (d["mentionsDisplay"] == "none" and d["savedDisplay"] != "none"
          and "Saved comments" in d["hdr"] and "Unstar to remove from the list" in d["hdr"]
          and d["items"] == 1 and d["entity"] == "Unrecognized pool")
    rec("QA-CMT-05", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    reset(page)
    page.click("[data-open='inbox1']")
    # "the .star button on the first item" -- .it items are not :first-of-type
    # (.paneheader is also a <div>), so address the first .it positionally.
    star = "#inbox1 [data-pane=mentions] .it >> nth=0 >> .star"
    before = page.eval_on_selector("#inbox1 [data-pane=mentions] .it .star",
                                   "e => e.classList.contains('on')")
    page.click(star)
    on1 = page.eval_on_selector("#inbox1 [data-pane=mentions] .it .star",
                                "e => e.classList.contains('on')")
    page.click(star)
    on2 = page.eval_on_selector("#inbox1 [data-pane=mentions] .it .star",
                                "e => e.classList.contains('on')")
    rec("QA-CMT-06", "PASS" if (on1 and not on2) else "FAIL",
        f"initial on={before} -> after 1st click on={on1} -> after 2nd click on={on2}")

    reset(page)
    page.click("[data-open='inbox1']")
    page.click("h2")
    afterBody = page.evaluate("() => inbox1.classList.contains('open')")
    page.keyboard.press("Escape")
    afterEsc = page.evaluate("() => inbox1.classList.contains('open')")
    rec("QA-CMT-11", "PASS" if (afterBody and afterEsc) else "FAIL",
        f"open after outside click={afterBody}; open after Esc={afterEsc}")


# ══════════════════════════════════════════════════════════════════════════════
# 8.8  Block FURN
# ══════════════════════════════════════════════════════════════════════════════
def furn(page):
    reset(page)
    t = page.eval_on_selector("p.mut:has(#poolCountBottom)", "e => e.textContent")
    rec("QA-FURN-01", "PASS" if t == "Unrecognized pool · 3 items" else "FAIL", q(t))

    reset(page)
    page.click("#poolrow1 >> text=Review & Match")
    page.click("#m-match tbody tr:nth-child(1) .pmatch")
    d = page.evaluate("""() => {
      const t=document.getElementById('matchToast'), cs=getComputedStyle(t), tb=t.getBoundingClientRect();
      const acts=[...document.querySelectorAll('table.tbl')[0].querySelectorAll('tbody tr')]
        .map(r=>r.querySelectorAll('td')[11].getBoundingClientRect());
      const hit=acts.filter(a=>!(tb.right<a.left||tb.left>a.right||tb.bottom<a.top||tb.top>a.bottom)).length;
      return {position: cs.position, top: cs.top, right: cs.right, z: cs.zIndex,
              intersects: hit, toast: [tb.top,tb.right,tb.bottom,tb.left],
              actions: acts.map(a=>[a.top,a.left])};}""")
    ok = (d["position"] == "fixed" and d["top"] == "18px" and d["right"] == "18px"
          and int(d["z"]) > 0 and d["intersects"] == 0)
    rec("QA-FURN-02", "PASS" if ok else "FAIL", json.dumps(d))

    reset(page)
    page.evaluate("() => window.__qa.hist0 = history.length")
    page.click("#poolrow1 >> text=Review & Match")
    page.click("#m-match tbody tr:nth-child(1) .pmatch")
    page.click("table.tbl tbody tr:nth-of-type(1) .xdel")
    d = page.evaluate("() => ({alive: !!window.__qa, hist0: window.__qa?.hist0, hist: history.length, "
                      "bu: window.__qa?.beforeunload})")
    ok = d["alive"] and d["hist"] == d["hist0"] and d["bu"] == 0
    rec("QA-FURN-03", "PASS" if ok else "FAIL", json.dumps(d))

    reset(page)
    d = page.evaluate("""() => {
      const nav=document.querySelector('.nav');
      return {brand: nav.querySelector('.brand').textContent,
              menus: [...nav.querySelectorAll(':scope > span')].map(s=>s.textContent).filter(t=>t.includes('▾')),
              user: nav.querySelector('.user').textContent,
              avatar: nav.querySelector('.avatar').textContent,
              logout: nav.querySelector('.logout').textContent};}""")
    ok = (d["brand"] == "SkinSeoul"
          and d["menus"] == ["Operation AI ▾", "Catalog Management ▾", "OMS Center ▾", "Site Management ▾"]
          and "Yongwon Ryu" in d["user"] and d["avatar"] == "Y" and d["logout"] == "Logout")
    rec("QA-FURN-04", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    rec("QA-FURN-05",
        "PASS" if page.evaluate("() => getComputedStyle(matchToast).display") == "none" else "FAIL",
        "baseline #matchToast computed display = none")


# ══════════════════════════════════════════════════════════════════════════════
# 8.9  Block NEG   (WF subset)
# ══════════════════════════════════════════════════════════════════════════════
def neg(page):
    reset(page)
    page.click("#poolrow1 >> text=Review & Match")
    d = page.evaluate("""() => {
      const b=document.querySelector('#m-match tbody tr:nth-child(1) .pmatch');
      const cyc=[]; const iv=setInterval(()=>cyc.push(getComputedStyle(matchToast).display),20);
      b.dispatchEvent(new MouseEvent('click',{bubbles:true}));
      b.dispatchEvent(new MouseEvent('click',{bubbles:true}));
      return {rows: document.querySelectorAll('table.tbl')[0].querySelectorAll('tbody tr').length,
              pc: poolCount.textContent, pcb: poolCountBottom.textContent,
              toast: getComputedStyle(matchToast).display, iv};}""")
    ok = d["rows"] == 2 and d["pc"] == "2" and d["pcb"] == "2" and d["toast"] == "flex"
    rec("QA-NEG-01", "PASS" if ok else "FAIL",
        json.dumps({k: v for k, v in d.items() if k != 'iv'}) +
        "  [double-click guarded by finishMatch()'s `if(row)` check]")

    reset(page)
    d = page.evaluate("""() => {
      const b=document.querySelectorAll('.xdel')[0];
      b.dispatchEvent(new MouseEvent('click',{bubbles:true}));
      b.dispatchEvent(new MouseEvent('click',{bubbles:true}));
      return {rowsRemaining: document.querySelectorAll('table.tbl')[0].querySelectorAll('tbody tr').length,
              pc: poolCount.textContent, pcb: poolCountBottom.textContent};}""")
    ok = d["rowsRemaining"] == 2 and d["pc"] == "2" and d["pcb"] == "2"
    rec("QA-NEG-03", "PASS" if ok else "FAIL",
        f"spec: 'exactly one row is removed And both counters decrement by exactly 1'; page: {json.dumps(d)} "
        "-- the row is removed once but poolDec() runs twice, because `.xdel`'s handler calls "
        "`b.closest('tr')` on a button that is still attached to the now-detached <tr>, so `.remove()` "
        "is a silent no-op while the counter decrements again (index.html L400-404)")


# ══════════════════════════════════════════════════════════════════════════════
# 8.11 Block EMPTY   (WF subset)
# ══════════════════════════════════════════════════════════════════════════════
def empty(page):
    reset(page)
    for _ in range(3):
        page.click("table.tbl tbody tr:nth-of-type(1) .xdel")
    d = page.evaluate("""() => {const ph=document.querySelector('.poolhead');
      return {pc: poolCount.textContent, pcb: poolCountBottom.textContent,
              poolheadRendered: !!ph && getComputedStyle(ph).display!=='none',
              poolheadH: ph.getBoundingClientRect().height,
              mockH: document.querySelector('.mock').getBoundingClientRect().height};}""")
    ok = d["pc"] == "0" and d["pcb"] == "0" and d["poolheadRendered"] and d["mockH"] > 300
    rec("QA-EMPTY-01", "PASS" if ok else "FAIL",
        json.dumps(d) + "  ['layout has not collapsed' has no spec-given metric; asserted mock height > 300px]")

    outcomes = {}
    for label, closer in (("Cancel", "cancel"), ("header X", "x"), ("backdrop", "backdrop")):
        reset(page)
        page.click("#poolrow1 >> text=Review & Match")
        if closer == "cancel":
            page.click("#m-match .foot >> text=Cancel")
        elif closer == "x":
            page.click("#m-match header .x")
        else:
            page.mouse.click(5, 5)
        outcomes[label] = page.evaluate("""() => ({open: document.getElementById('m-match').classList.contains('open'),
            rows: document.querySelectorAll('table.tbl')[0].querySelectorAll('tbody tr').length,
            pc: poolCount.textContent, pcb: poolCountBottom.textContent,
            toast: getComputedStyle(matchToast).display})""")
    ok = all(o["open"] is False and o["rows"] == 3 and o["pc"] == "3" and o["pcb"] == "3"
             and o["toast"] == "none" for o in outcomes.values())
    rec("QA-EMPTY-05", "PASS" if ok else "FAIL", json.dumps(outcomes))


# ══════════════════════════════════════════════════════════════════════════════
# 8.12 Block XPG   (WF subset)
# ══════════════════════════════════════════════════════════════════════════════
def xpg(page):
    if not CLOSING.exists():
        rec("QA-XPG-05", "UNRUNNABLE", f"closing wireframe not found at {CLOSING}")
        return
    rec("QA-XPG-05", "UNRUNNABLE",
        "Tagged [WF] but three of its four clauses are unobservable in a static wireframe and it targets a "
        "DIFFERENT system under test (the closing page). 'no pool row ... is produced' and 'no "
        "#unrecognized-tracking message is produced' are server/Slack state; the closing wireframe holds "
        "no state and emits no messages. Only 'the warning stays on the Closing page / no navigation' is "
        "[WF]-assertable. Spec also gives no click path ('When a scan produces the unknown-order warning' "
        "names no selector or button on the closing page).")


# ══════════════════════════════════════════════════════════════════════════════
# 8.14 Block A11Y   (WF subset)
# ══════════════════════════════════════════════════════════════════════════════
def a11y(page):
    reset(page)
    page.evaluate("() => document.body.focus()")
    seq, seen = [], 0
    for _ in range(40):
        page.keyboard.press("Tab")
        info = page.evaluate("""() => {const a=document.activeElement;
          return {inRow1: !!a.closest?.('#poolrow1'), cls: a.className, text: (a.textContent||'').trim()};}""")
        if info["inRow1"]:
            seq.append(info["text"])
            seen += 1
            if seen >= 2:
                break
        elif seq:
            break
    ok = seq[:2] == ["Review & Match", "✕"]
    rec("QA-A11Y-01", "PASS" if ok else "FAIL",
        f"tab order inside #poolrow1 = {seq!r} (spec: Review & Match, then .xdel)")

    page.set_viewport_size({"width": 900, "height": 800})
    reset(page)
    page.set_viewport_size({"width": 900, "height": 800})
    d = page.evaluate("""() => {
      const wraps=[...document.querySelectorAll('.mockwrap')].map(w=>({
        sw:w.scrollWidth, cw:w.clientWidth, scrollable:w.scrollWidth>w.clientWidth}));
      const ths=[...document.querySelectorAll('table.tbl')[0].querySelectorAll('th')].map(t=>{
        const c=t.cloneNode(true); c.querySelectorAll('.dot').forEach(d=>d.remove()); return c.textContent;});
      const body=document.documentElement;
      return {wraps, nTh: ths.length, ths, docScrollX: body.scrollWidth>body.clientWidth};}""")
    expect = ["Tracking No", "Order No", "Product Name", "Product Name KR", "Size", "Barcode", "Qty",
              "Memo", "Registrant (Center)", "Registered At", "Suspected Orders (Auto-matched)", "Action"]
    outer = d["wraps"][0]["scrollable"] if d["wraps"] else False
    # "Action column buttons remain reachable by scrolling"
    # NOTE: two .mockwrap elements nest and BOTH must be scrolled for the Action
    # column to come into view. The spec names ".mockwrap" in the singular.
    reach = page.evaluate("""() => {
      const ws=[...document.querySelectorAll('.mockwrap')];
      const outerOnly=(()=>{ws.forEach(w=>w.scrollLeft=0); ws[0].scrollLeft=ws[0].scrollWidth;
        const b=document.querySelector('#poolrow1 .xdel').getBoundingClientRect();
        return b.right>0 && b.left<innerWidth;})();
      ws.forEach(w=>w.scrollLeft=w.scrollWidth);
      const b=document.querySelector('#poolrow1 .xdel').getBoundingClientRect();
      return {outerOnlyVisible: outerOnly, left:b.left, right:b.right, vw:innerWidth,
              visible: b.right>0 && b.left<innerWidth};}""")
    ok = outer and d["nTh"] == 12 and d["ths"] == expect and reach["visible"]
    rec("QA-A11Y-05", "PASS" if ok else "FAIL",
        json.dumps({"outerMockwrap": d["wraps"][0] if d["wraps"] else None,
                    "innerMockwrap": d["wraps"][1] if len(d["wraps"]) > 1 else None,
                    "headersIntactInOrder": d["ths"] == expect, "actionReachable": reach}) +
        "  [spec says '.mockwrap' (singular) but two nested elements match and BOTH must be "
        "scrolled; scrolling only the outer one leaves the Action buttons off-screen]")
    page.set_viewport_size({"width": 1280, "height": 800})


# ══════════════════════════════════════════════════════════════════════════════
# 8.15 Block WFQ
# ══════════════════════════════════════════════════════════════════════════════
def wfq(page):
    reset(page)
    page.click("table.tbl tbody tr:nth-of-type(2) >> text=Review & Match")
    d = page.evaluate("""() => ({open: document.getElementById('m-match').classList.contains('open'),
        mut: document.querySelector('#m-match .mut').textContent})""")
    ok = d["open"] and "Tracking 10323100841207" in d["mut"]
    rec("QA-WFQ-01", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))

    reset(page)
    page.click("#poolrow1 .xdel")
    page.click(".wf-tab")
    page.click("#m-match tbody tr:nth-child(1) .pmatch")
    d = page.evaluate("() => ({toast: getComputedStyle(matchToast).display, pc: poolCount.textContent})")
    rec("QA-WFQ-02", "PASS" if (d["toast"] == "flex" and d["pc"] == "2") else "FAIL", json.dumps(d))

    reset(page)
    page.evaluate("""() => {window.__qa.dialog=false; window.__qa.toast=false;
      new MutationObserver(()=>{if(document.querySelector('.overlay.open'))window.__qa.dialog=true;})
        .observe(document.documentElement,{subtree:true,attributes:true,attributeFilter:['class']});
      setInterval(()=>{if(getComputedStyle(matchToast).display!=='none')window.__qa.toast=true;},20);}""")
    page.click("#poolrow1 .xdel")
    page.wait_for_timeout(200)
    d = page.evaluate("() => ({dialog: window.__qa.dialog, toast: window.__qa.toast, "
                      "overlays: document.querySelectorAll('.overlay.open').length})")
    ok = not d["dialog"] and not d["toast"] and d["overlays"] == 0
    rec("QA-WFQ-03", "PASS" if ok else "FAIL", json.dumps(d))

    reset(page)
    n = page.evaluate("() => document.querySelectorAll('a').length")
    spans = page.evaluate("""() => [...document.querySelectorAll('table.tbl')[0]
        .querySelectorAll('tbody tr td:nth-child(11) div')]
        .map(d=>[...d.childNodes].find(n=>/^Order \\d+$/.test(n.textContent||''))?.nodeName)""")
    rec("QA-WFQ-04", "PASS" if (n == 0 and set(spans) == {"SPAN"}) else "FAIL",
        f"<a> count = {n}; candidate order-number tags = {set(spans)}")

    page.click("[data-open='inbox1']")
    d = page.evaluate("""() => ({open: inbox1.classList.contains('open'),
        inputs: inbox1.querySelectorAll('input,textarea').length,
        placeholders: inbox1.querySelectorAll('[placeholder]').length})""")
    ok = d["open"] and d["inputs"] == 0 and d["placeholders"] == 0
    rec("QA-WFQ-05", "PASS" if ok else "FAIL", json.dumps(d))

    reset(page)
    page.click("#annoToggle")
    d1 = page.evaluate("""() => ({noAnno: document.body.classList.contains('no-anno'),
        dotsVisible: [...document.querySelectorAll('.dot')].filter(e=>getComputedStyle(e).display!=='none').length,
        legendVisible: [...document.querySelectorAll('.legend')].filter(e=>getComputedStyle(e).display!=='none').length,
        btn: annoToggle.textContent})""")
    page.click("#annoToggle")
    d2 = page.evaluate("""() => ({noAnno: document.body.classList.contains('no-anno'),
        dotsVisible: [...document.querySelectorAll('.dot')].filter(e=>getComputedStyle(e).display!=='none').length,
        legendVisible: [...document.querySelectorAll('.legend')].filter(e=>getComputedStyle(e).display!=='none').length,
        btn: annoToggle.textContent})""")
    ok = (d1["noAnno"] and d1["dotsVisible"] == 0 and d1["legendVisible"] == 0
          and d1["btn"] == "Show annotations"
          and not d2["noAnno"] and d2["dotsVisible"] == 7 and d2["legendVisible"] == 1
          and d2["btn"] == "Hide annotations")
    rec("QA-WFQ-06", "PASS" if ok else "FAIL", f"after 1st={json.dumps(d1)} after 2nd={json.dumps(d2)}")


# ══════════════════════════════════════════════════════════════════════════════
def main():
    with sync_playwright() as p:
        b = p.chromium.launch()
        page = b.new_page(viewport={"width": 1280, "height": 800})
        reset(page)
        base = baseline_ok(page)
        print("BASELINE (spec §8.0):", json.dumps(base), file=sys.stderr)

        for fn in (load, row, sus, m1, match, xdel, cmt, furn, neg, empty, xpg, a11y, wfq):
            try:
                fn(page)
            except Exception as e:                                   # pragma: no cover
                rec(fn.__name__.upper() + "-BLOCK", "ERROR", f"{type(e).__name__}: {e}")
        b.close()

    if "--json" in sys.argv:
        print(json.dumps([{"id": i, "verdict": v, "evidence": e} for i, v, e in RESULTS],
                         ensure_ascii=False, indent=1))
        return
    counts = {}
    for _, v, _ in RESULTS:
        counts[v] = counts.get(v, 0) + 1
    for i, v, e in RESULTS:
        print(f"{v:10} {i:14} {e}")
    print("\nTOTAL", len(RESULTS), counts)


if __name__ == "__main__":
    main()
