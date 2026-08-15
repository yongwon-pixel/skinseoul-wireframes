#!/usr/bin/env python3
"""
Adversarial QA execution of §8 [WF] scenarios from
  wms2/specs/ready-to-outbound.md
against
  wms2/ready-to-outbound/index.html  (identical to the deployed page)

Rules of engagement (Verification Method 2):
  * Execute each scenario EXACTLY as the spec writes it — only the selectors,
    labels and expected strings the spec itself supplies.
  * If the spec does not say what to click or what to assert => AMBIGUOUS,
    recorded and skipped. Never improvise from knowledge of the page.
  * Every scenario runs on a FRESH page load (§8.0 precondition).

Run:  python3 qa-ready-to-outbound.py [--headed]
Out:  JSON summary on stdout + per-scenario lines.
"""
import json
import os
import sys
import time
from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
TARGET = "file://" + os.path.normpath(os.path.join(HERE, "..", "..", "ready-to-outbound", "index.html"))

RESULTS = []          # (id, verdict, evidence)
_console_errors = []


def record(sid, verdict, evidence):
    RESULTS.append((sid, verdict, evidence))
    print(f"{verdict:<10} {sid}  {evidence}", flush=True)


def eq(sid, actual, expected, label=""):
    if actual == expected:
        record(sid, "PASS", f"{label}{'=' if label else ''}{actual!r}")
        return True
    record(sid, "FAIL", f"spec: {expected!r} / page: {actual!r}")
    return False


# ---------------------------------------------------------------- helpers

JS_HELPERS = r"""
window.__qa = {
  rows: () => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')],
  rowByOid: (oid) => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .find(r => r.querySelector('.oid') && r.querySelector('.oid').textContent === oid),
  firstTextNode: (el) => { for (const n of el.childNodes) if (n.nodeType === 3) return n.textContent; return null; },
  pfill: () => document.getElementById('pfill').style.width,
  plabel: () => document.getElementById('pbarLabel').childNodes[0].textContent,
  toastVisible: () => document.getElementById('toast').style.display,
  toastB: () => document.getElementById('toast').querySelector('b').textContent,
  toastSmall: () => document.getElementById('toast').querySelector('small').textContent,
};
"""


def fresh(page):
    page.goto(TARGET)
    page.wait_for_load_state("domcontentloaded")
    page.evaluate(JS_HELPERS)


def start_sampler(page):
    """Page-side 100 ms sampler of #pfill inline width + toast state (QA-L5-02, QA-L6-03)."""
    page.evaluate(r"""
      window.__samples = [];
      window.__sampler = setInterval(() => {
        const t = document.getElementById('toast');
        window.__samples.push({
          w: document.getElementById('pfill').style.width,
          td: t.style.display,
          tb: t.querySelector('b').textContent,
          n: document.querySelectorAll('.toast').length
        });
      }, 100);
    """)


def stop_sampler(page):
    return page.evaluate("(() => { clearInterval(window.__sampler); return window.__samples; })()")


def btn_by_text(page, text):
    """Locate a <button> whose textContent is exactly `text` (spec quotes labels verbatim)."""
    return page.locator("button").filter(has_text=text).first


def run_batch(page, selector, wait_ms=2200):
    page.click(selector)
    page.wait_for_timeout(wait_ms)


# ---------------------------------------------------------------- scenarios


def qa_l1_01(page):
    fresh(page)
    n = page.evaluate("document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)').length")
    checked = page.evaluate("""
      (() => { const o = {};
        for (const r of window.__qa.rows()) {
          o[r.querySelector('.oid').textContent] = r.querySelector('input[type=checkbox]').checked;
        } return o; })()
    """)
    cnt = page.evaluate("document.querySelector('.bulkbar .cnt').textContent")
    ok = (n == 5 and checked == {"422221": True, "422176": True, "422165": True,
                                 "MKT-40233": False, "422164": False} and cnt == "3 selected")
    record("QA-L1-01", "PASS" if ok else "FAIL",
           f"rows={n} checked={checked} cnt={cnt!r}" if ok else
           f"spec: 5 rows / 3 checked / '3 selected'; page: rows={n} {checked} cnt={cnt!r}")


def qa_l1_02(page):
    fresh(page)
    labels = page.evaluate("[...document.querySelectorAll('.bulkbar button')].map(b=>b.textContent)")
    expected = ["🖨 Print Pick Locations (3 orders · 8 items)",
                "🖨 Bulk Print Labels (3 orders)",
                "📦 Bulk Outbound (3 orders)"]
    eq("QA-L1-02", labels, expected)


def qa_l1_04(page):
    fresh(page)
    before = page.evaluate("[...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow) input[type=checkbox]')].map(c=>c.checked)")
    lbefore = page.evaluate("[...document.querySelectorAll('.bulkbar button')].map(b=>b.textContent)")
    page.click(".bulkbar input[type=checkbox]")
    page.click(".tbl thead input[type=checkbox]")
    after = page.evaluate("[...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow) input[type=checkbox]')].map(c=>c.checked)")
    cnt = page.evaluate("document.querySelector('.bulkbar .cnt').textContent")
    lafter = page.evaluate("[...document.querySelectorAll('.bulkbar button')].map(b=>b.textContent)")
    ok = before == after and cnt == "3 selected" and lbefore == lafter
    record("QA-L1-04", "PASS" if ok else "FAIL",
           f"row cbs unchanged {after}, cnt={cnt!r}, labels unchanged" if ok
           else f"before={before} after={after} cnt={cnt!r}")


def qa_l2_02(page):
    fresh(page)
    pre_w = page.evaluate("window.__qa.pfill()")
    pre_t = page.evaluate("window.__qa.toastVisible()")
    page.click("button.btn-line[data-modal='m-pick']")
    page.wait_for_timeout(2000)
    w = page.evaluate("window.__qa.pfill()")
    lab = page.evaluate("window.__qa.plabel()")
    td = page.evaluate("window.__qa.toastVisible()")
    exp_lab = "Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion"
    ok = pre_w == "" and pre_t == "none" and w == "" and lab == exp_lab and td == "none"
    record("QA-L2-02", "PASS" if ok else "FAIL",
           f"pfill={w!r} toast={td!r} label unchanged" if ok
           else f"spec: pfill '' / label {exp_lab!r} / toast none; page: pfill={w!r} label={lab!r} toast={td!r}")


def qa_l2_03(page):
    fresh(page)
    page.click("button[data-modal='m-pick'].wf-toggle")
    o1 = page.evaluate("document.getElementById('m-pick').classList.contains('open')")
    page.click("#m-pick header .x")
    page.click("button[data-modal='m-pick'].wf-tab")
    o2 = page.evaluate("document.getElementById('m-pick').classList.contains('open')")
    ok = o1 and o2
    record("QA-L2-03", "PASS" if ok else "FAIL", f"open after btn1={o1}, after btn2={o2}")


def qa_m1_01(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    hdr = page.evaluate("window.__qa.firstTextNode(document.querySelector('#m-pick .modal > header'))")
    badges = page.evaluate("""
      [...window.__qa.rows()].filter(r=>r.querySelector('input[type=checkbox]').checked)
        .map(r=>+r.querySelector('.cntbadge').textContent)
    """)
    l2 = page.evaluate("document.querySelector(\"button.btn-line[data-modal='m-pick']\").textContent")
    exp = "Print Pick Locations — Picking List (3 orders selected · 4 SKUs · 8 units total)"
    ok = hdr == exp and sum(badges) == 8 and "8 items" in l2
    record("QA-M1-01", "PASS" if ok else "FAIL",
           f"header={hdr!r}; badges {badges} sum=8; L-2 has '8 items'" if ok
           else f"spec: {exp!r}; page: {hdr!r} badges={badges}")


def qa_m1_03(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    locs = page.evaluate("[...document.querySelectorAll('#m-pick .picktbl tbody tr')].map(r=>r.cells[0].textContent)")
    ok = locs == ["A-02-13", "A-03-02", "B-01-07", "B-02-11"]
    record("QA-M1-03", "PASS" if ok else "FAIL", f"rows={len(locs)} locations={locs}")


def qa_m1_05(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    data = page.evaluate("""
      [...document.querySelectorAll('#m-pick .picktbl tbody tr')].map(r=>({
        product: r.cells[2].textContent,
        qty: r.cells[3].textContent,
        qtyBold: !!r.cells[3].querySelector('b'),
        order: r.cells[4].textContent }))
    """)
    ok = (data[1]["product"] == "마데카 크림 타이트닝" and
          data[2]["product"] == "세라마이드 아토 컨센트레이트 크림" and
          data[3]["product"] == "마데카 크림 타임 리버스" and
          data[0]["qty"] == "5" and data[0]["qtyBold"] and data[0]["order"] == "422221" and
          all(d["qty"] == "1" and not d["qtyBold"] for d in data[1:]))
    record("QA-M1-05", "PASS" if ok else "FAIL", json.dumps(data, ensure_ascii=False))


def qa_m1_06(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    orders = page.evaluate("[...document.querySelectorAll('#m-pick .picktbl tbody tr')].map(r=>r.cells[4].textContent)")
    eq("QA-M1-06", orders, ["422221", "422165", "422176", "422165"])


def qa_m1_07(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    rows = page.evaluate("""
      [...document.querySelectorAll('#m-pick .picktbl tbody tr')].map(r=>({loc:r.cells[0].textContent,order:r.cells[4].textContent}))
    """)
    dupes = [r for r in rows if r["order"] == "422165"]
    multi = [r for r in rows if len(r["order"].split()) > 1 or "," in r["order"]]
    ok = len(dupes) == 2 and {d["loc"] for d in dupes} == {"A-03-02", "B-02-11"} and not multi
    record("QA-M1-07", "PASS" if ok else "FAIL",
           f"422165 appears as 2 separate rows {sorted(d['loc'] for d in dupes)}; no multi-order cell" if ok else str(rows))


def qa_m1_08(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    skus = page.evaluate("[...document.querySelectorAll('#m-pick .picktbl tbody tr')].map(r=>r.cells[1].textContent)")
    locs = page.evaluate("[...document.querySelectorAll('#m-pick .picktbl tbody tr')].map(r=>r.cells[0].textContent)")
    ok = "100012534" not in skus and "Not inbounded" not in locs
    record("QA-M1-08", "PASS" if ok else "FAIL", f"skus={skus} locs={locs}")


def qa_m1_09(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    r2 = page.evaluate("document.querySelectorAll('#m-pick .picktbl tbody tr')[1].cells[2].textContent")
    r1 = page.evaluate("document.querySelectorAll('#m-pick .picktbl tbody tr')[0].cells[2].textContent")
    grid = page.evaluate("window.__qa.rowByOid('422165').innerHTML.includes('<b>Centellian24</b>')")
    ok = "Centellian24" not in r2 and grid and r1 == "AtoBarrier365 Body …"
    record("QA-M1-09", "PASS" if ok else "FAIL",
           f"M1 row2 product={r2!r} (no brand); grid has <b>Centellian24</b>={grid}; row1={r1!r}")


def qa_m1_10(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    note = page.evaluate("document.querySelector('#m-pick .note').textContent")
    exp = ("Sorted by location (ascending) (A-02-13 → B-01-07 → Shelf 3) — pick everything in one pass "
           "along the route. Printing: no refresh · selection kept; progress bar, then a top-right completion toast.")
    eq("QA-M1-10", note, exp)


def qa_m1_11(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    start_sampler(page)
    page.evaluate("""
      window.__labels = [];
      window.__labelTimer = setInterval(()=>{window.__labels.push(document.getElementById('pbarLabel').childNodes[0].textContent);},100);
    """)
    page.click("#m-pick .foot button.bulk-run")
    page.wait_for_timeout(1800)
    labels = page.evaluate("(()=>{clearInterval(window.__labelTimer);return window.__labels;})()")
    stop_sampler(page)
    open_cls = page.evaluate("document.getElementById('m-pick').classList.contains('open')")
    w = page.evaluate("window.__qa.pfill()")
    tb = page.evaluate("window.__qa.toastB()")
    td = page.evaluate("window.__qa.toastVisible()")
    rows = page.evaluate("window.__qa.rows().length")
    checked = page.evaluate("[...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow) input[type=checkbox]')].filter(c=>c.checked).length")
    IDLE = "Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion"
    stale = [l for l in labels if l == IDLE]           # pre-first-tick window, see spec-fix S-2
    running = [l for l in labels if "in progress" in l and l != IDLE and "100%" not in l]
    ok = (not open_cls and w == "100%" and
          all("Print Pick Locations in progress" in l and "No refresh · selection kept" in l
              and "refreshes after completion" not in l for l in running) and running and
          td == "flex" and tb == "✓ Print Pick Locations complete — 3 orders" and rows == 5 and checked == 3)
    record("QA-M1-11", "PASS" if ok else "FAIL",
           f"modal closed={not open_cls} pfill={w!r} toast b={tb!r} rows={rows} checked={checked}; "
           f"running sample={running[0]!r}; CAVEAT: {len(stale)} samples in the first ~250 ms still showed "
           f"the previous/idle copy {IDLE!r} — spec never bounds 'during the run'"
           if running else f"labels={labels}")


def qa_m1_12(page):
    fresh(page)
    # 1: Cancel
    page.click("button.btn-line[data-modal='m-pick']")
    page.click("#m-pick .foot button.btn-gray")
    a = page.evaluate("document.getElementById('m-pick').classList.contains('open')")
    # 2: backdrop
    page.click("button.btn-line[data-modal='m-pick']")
    page.mouse.click(4, 4)
    b = page.evaluate("document.getElementById('m-pick').classList.contains('open')")
    # 3: X
    page.click("button.btn-line[data-modal='m-pick']")
    page.click("#m-pick header .x")
    c = page.evaluate("document.getElementById('m-pick').classList.contains('open')")
    page.wait_for_timeout(1600)
    w = page.evaluate("window.__qa.pfill()")
    td = page.evaluate("window.__qa.toastVisible()")
    ok = not a and not b and not c and w == "" and td == "none"
    record("QA-M1-12", "PASS" if ok else "FAIL",
           f"closed via Cancel/backdrop/X = {not a}/{not b}/{not c}; pfill={w!r} toast={td!r}")


def qa_l3_01(page):
    fresh(page)
    page.evaluate("window.__labels=[];window.__t=setInterval(()=>window.__labels.push(document.getElementById('pbarLabel').childNodes[0].textContent),100);")
    page.click("button.bulk-run[data-label='Bulk Print Labels']")
    page.wait_for_timeout(1600)
    labels = page.evaluate("(()=>{clearInterval(window.__t);return window.__labels;})()")
    running = [l for l in labels if "in progress" in l and "3/5" not in l]
    ok = bool(running) and all("Bulk Print Labels in progress" in l and "No refresh · selection kept" in l
                               and "refreshes after completion" not in l for l in running)
    record("QA-L3-01", "PASS" if ok else "FAIL", f"sample={running[0]!r}" if running else f"labels={labels}")


def qa_l3_02(page):
    fresh(page)
    run_batch(page, "button.bulk-run[data-label='Bulk Print Labels']", 1500)
    tb = page.evaluate("window.__qa.toastB()")
    ts = page.evaluate("window.__qa.toastSmall()")
    ok = tb == "✓ Bulk Print Labels complete — 3 orders" and ts == "Disappears automatically after a few seconds"
    record("QA-L3-02", "PASS" if ok else "FAIL", f"b={tb!r} small={ts!r}")


def qa_l3_03(page):
    fresh(page)
    page.evaluate("window.__sentinel='alive'")
    run_batch(page, "button.bulk-run[data-label='Bulk Print Labels']", 1500)
    sent = page.evaluate("window.__sentinel")
    ac = page.evaluate("typeof window.sndOutbound.ac")
    checked = page.evaluate("[...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow) input[type=checkbox]')].filter(c=>c.checked).length")
    ok = sent == "alive" and ac == "undefined" and checked == 3
    record("QA-L3-03", "PASS" if ok else "FAIL", f"sentinel={sent!r} sndOutbound.ac={ac} checked={checked}")


def qa_l3_04(page):
    fresh(page)
    tx = page.evaluate("document.querySelector(\"button.bulk-run[data-label='Bulk Print Labels']\").textContent")
    ok = "Outbound" not in tx
    record("QA-L3-04", "PASS" if ok else "FAIL", f"label={tx!r} contains 'Outbound' = {'Outbound' in tx}")


def qa_l4_01(page):
    fresh(page)
    pre = page.evaluate("typeof window.sndOutbound.ac")
    errs_before = len(_console_errors)
    page.click("button.bulk-run[data-label='Bulk Outbound']")
    page.wait_for_timeout(400)
    kind = page.evaluate("(()=>{const a=window.sndOutbound.ac; return a? a.constructor.name : 'undefined';})()")
    constructible = page.evaluate("!!(window.AudioContext||window.webkitAudioContext)")
    new_errs = _console_errors[errs_before:]
    ok = pre == "undefined" and not new_errs and ((not constructible) or kind == "AudioContext")
    record("QA-L4-01", "PASS" if ok else "FAIL",
           f"no uncaught exception; sndOutbound.ac = {kind} (AudioContext constructible={constructible})")


def qa_l4_02(page):
    fresh(page)
    page.evaluate("window.__labels=[];window.__t=setInterval(()=>window.__labels.push(document.getElementById('pbarLabel').childNodes[0].textContent),100);")
    page.click("button.bulk-run[data-label='Bulk Outbound']")
    page.wait_for_timeout(1600)
    labels = page.evaluate("(()=>{clearInterval(window.__t);return window.__labels;})()")
    running = [l for l in labels if "in progress" in l and "3/5" not in l]
    ok = bool(running) and all("Bulk Outbound in progress" in l and "refreshes after completion" in l
                               and "No refresh · selection kept" not in l for l in running)
    record("QA-L4-02", "PASS" if ok else "FAIL", f"sample={running[0]!r}" if running else f"labels={labels}")


def qa_l4_03(page):
    fresh(page)
    page.click("button.bulk-run[data-label='Bulk Outbound']")
    t0 = time.time()
    page.wait_for_function("document.getElementById('toast').style.display==='flex'", timeout=5000)
    t_show = time.time() - t0
    disp = page.evaluate("document.getElementById('toast').style.display")
    pos = page.evaluate("(()=>{const s=getComputedStyle(document.getElementById('toast'));return {position:s.position,top:s.top,right:s.right};})()")
    tb = page.evaluate("window.__qa.toastB()")
    t1 = time.time()
    page.wait_for_function("document.getElementById('toast').style.display==='none'", timeout=6000)
    dwell = time.time() - t1
    ok = (disp == "flex" and tb == "✓ Bulk Outbound complete — 3 orders"
          and pos["top"] == "54px" and pos["right"] == "16px" and dwell <= 4.5)
    record("QA-L4-03", "PASS" if ok else "FAIL",
           f"display={disp!r} {pos} b={tb!r}; toast up at t+{t_show:.2f}s, auto-hid {dwell:.2f}s later "
           f"(anchor for '~4 s' not stated in the spec — measured from toast appearance)")


def qa_l4_04(page):
    fresh(page)
    qual = page.evaluate("""
      [...document.querySelectorAll('button')].map(b=>b.textContent||'')
        .filter(tx=>/Outbound/.test(tx) && !/Cancel/.test(tx) && !/Outbounded/.test(tx))
    """)
    ok = qual == ["📦 Bulk Outbound (3 orders)"]
    record("QA-L4-04", "PASS" if ok else "FAIL", f"qualifying buttons = {qual}")


def qa_l4_05(page):
    fresh(page)
    bad = page.evaluate("""
      [...document.querySelectorAll('*')]
        .filter(e=>(e.textContent||'').includes('Ready to be Outbonded') && e.tagName==='BUTTON')
        .map(e=>e.textContent)
    """)
    ok = bad == []
    record("QA-L4-05", "PASS" if ok else "FAIL", f"buttons containing 'Ready to be Outbonded' = {bad}")


def qa_l5_01(page):
    fresh(page)
    n = page.evaluate("({pbar:document.querySelectorAll('.pbar').length, pfill:document.querySelectorAll('#pfill').length})")
    seen = []
    for sel, waitms in (("button.bulk-run[data-label='Bulk Print Labels']", 1500),
                        (None, 1500),
                        ("button.bulk-run[data-label='Bulk Outbound']", 1500)):
        if sel is None:
            page.click("button.btn-line[data-modal='m-pick']")
            page.click("#m-pick .foot button.bulk-run")
        else:
            page.click(sel)
        page.wait_for_timeout(waitms)
        seen.append(page.evaluate("window.__qa.pfill()"))
        page.wait_for_timeout(2200)
    ok = n["pbar"] == 1 and n["pfill"] == 1 and seen == ["100%", "100%", "100%"]
    record("QA-L5-01", "PASS" if ok else "FAIL", f".pbar={n['pbar']} #pfill={n['pfill']}; each run ended {seen}")


def qa_l5_02(page):
    fresh(page)
    start_sampler(page)
    page.click("button.bulk-run[data-label='Bulk Print Labels']")
    page.wait_for_timeout(1700)
    s = stop_sampler(page)
    widths = [x["w"] for x in s if x["w"] != ""]
    nums = [float(w.rstrip("%")) for w in widths]
    ok = bool(nums) and nums[0] == 0.0 and all(b >= a for a, b in zip(nums, nums[1:])) and nums[-1] == 100.0
    record("QA-L5-02", "PASS" if ok else "FAIL", f"samples={widths}")


def qa_l5_04(page):
    """Executed LITERALLY: 'a Bulk Outbound run never renders `No refresh · selection kept`'.
    'never' is absolute, so every sample taken while the run is in flight counts."""
    fresh(page)
    page.evaluate("window.__labels=[];window.__t=setInterval(()=>window.__labels.push(document.getElementById('pbarLabel').childNodes[0].textContent),40);")
    page.click("button.bulk-run[data-label='Bulk Outbound']")
    page.wait_for_timeout(1500)
    out = page.evaluate("(()=>{clearInterval(window.__t);return window.__labels;})()")
    page.wait_for_timeout(2200)
    page.evaluate("window.__labels=[];window.__t=setInterval(()=>window.__labels.push(document.getElementById('pbarLabel').childNodes[0].textContent),40);")
    page.click("button.bulk-run[data-label='Bulk Print Labels']")
    page.wait_for_timeout(1500)
    prn = page.evaluate("(()=>{clearInterval(window.__t);return window.__labels;})()")
    bad_out = [l for l in out if "No refresh · selection kept" in l]
    bad_prn = [l for l in prn if "refreshes after completion" in l]
    if not bad_out and not bad_prn:
        record("QA-L5-04", "PASS", f"{len(out)}+{len(prn)} samples, no mode-string cross-over")
        return
    record("QA-L5-04", "FAIL",
           "spec: 'a Bulk Outbound run NEVER renders `No refresh · selection kept`'. "
           f"page: {len(bad_out)} of {len(out)} in-flight samples did — the label is not rewritten until the "
           f"first 250 ms interval tick, so for the opening ~250 ms of every Bulk Outbound run #pbarLabel still "
           f"shows the previous action's copy: {bad_out[0]!r}"
           + (f" | print side: {len(bad_prn)} bad samples {bad_prn[0]!r}" if bad_prn else ""))


def qa_l5_05(page):
    fresh(page)
    lab = page.evaluate("window.__qa.plabel()")
    exp = "Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion"
    page.evaluate("window.__labels=[];window.__t=setInterval(()=>window.__labels.push(document.getElementById('pbarLabel').childNodes[0].textContent),80);")
    page.click("button.bulk-run[data-label='Bulk Print Labels']")
    page.wait_for_timeout(1500)
    running = page.evaluate("(()=>{clearInterval(window.__t);return window.__labels;})()")
    ok = lab == exp and all("3/5" not in l for l in running if "in progress" in l and l != exp)
    record("QA-L5-05", "PASS" if ok else "FAIL", f"idle={lab!r}; '3/5' absent from every running-state label")


def qa_l6_02(page):
    fresh(page)
    got = []
    page.click("button.btn-line[data-modal='m-pick']")
    page.click("#m-pick .foot button.bulk-run")
    page.wait_for_timeout(1500); got.append(page.evaluate("window.__qa.toastB()")); page.wait_for_timeout(2200)
    page.click("button.bulk-run[data-label='Bulk Print Labels']")
    page.wait_for_timeout(1500); got.append(page.evaluate("window.__qa.toastB()")); page.wait_for_timeout(2200)
    page.click("button.bulk-run[data-label='Bulk Outbound']")
    page.wait_for_timeout(1500); got.append(page.evaluate("window.__qa.toastB()"))
    eq("QA-L6-02", got, ["✓ Print Pick Locations complete — 3 orders",
                         "✓ Bulk Print Labels complete — 3 orders",
                         "✓ Bulk Outbound complete — 3 orders"])


def qa_l6_03(page):
    fresh(page)
    start_sampler(page)
    page.click("button.bulk-run[data-label='Bulk Print Labels']")
    page.wait_for_timeout(1500)          # toast now up
    page.click("button.bulk-run[data-label='Bulk Outbound']")   # before dismissal
    page.wait_for_timeout(1500)
    tb = page.evaluate("window.__qa.toastB()")
    s = stop_sampler(page)
    max_visible = max((1 if x["td"] == "flex" else 0) * x["n"] for x in s)
    ok = max_visible <= 1 and tb == "✓ Bulk Outbound complete — 3 orders"
    record("QA-L6-03", "PASS" if ok else "FAIL",
           f"max simultaneously-visible .toast = {max_visible}; final text = {tb!r}")


def qa_l6_04(page):
    fresh(page)
    # Runnable half: no completion string contains failed/error/partial.
    strings = []
    page.click("button.btn-line[data-modal='m-pick']")
    page.click("#m-pick .foot button.bulk-run"); page.wait_for_timeout(1500)
    strings += [page.evaluate("window.__qa.toastB()"), page.evaluate("window.__qa.toastSmall()")]
    page.wait_for_timeout(2200)
    page.click("button.bulk-run[data-label='Bulk Print Labels']"); page.wait_for_timeout(1500)
    strings += [page.evaluate("window.__qa.toastB()"), page.evaluate("window.__qa.toastSmall()")]
    page.wait_for_timeout(2200)
    page.click("button.bulk-run[data-label='Bulk Outbound']"); page.wait_for_timeout(1500)
    strings += [page.evaluate("window.__qa.toastB()"), page.evaluate("window.__qa.toastSmall()")]
    words_ok = not any(w in s.lower() for s in strings for w in ("failed", "error", "partial"))
    record("QA-L6-04", "AMBIGUOUS",
           "clause 2 (no completion string contains failed/error/partial) runs and holds "
           f"({words_ok}); clause 1 'the document contains no red/failure styling variant of #toast bound to "
           "batch completion' names no selector, no class, and no definition of 'variant' — not executable as written")


def qa_l6_05(page):
    fresh(page)
    smalls = []
    for sel in ("button.bulk-run[data-label='Bulk Print Labels']", "button.bulk-run[data-label='Bulk Outbound']"):
        page.click(sel); page.wait_for_timeout(1500)
        smalls.append(page.evaluate("window.__qa.toastSmall()")); page.wait_for_timeout(2200)
    ok = smalls == ["Disappears automatically after a few seconds"] * 2
    record("QA-L6-05", "PASS" if ok else "FAIL", f"#toast small after each batch = {smalls}")


def qa_l7_02(page):
    fresh(page)
    present = page.evaluate("document.body.textContent.includes('JIT (channel) completed')")
    where = page.evaluate("""
      (() => { const hit=[...document.querySelectorAll('.legend li, .tbl td, #m-pick *')]
          .filter(e=>(e.textContent||'').includes('JIT (channel) completed'));
        return hit.length ? hit[hit.length-1].textContent.slice(0,180) : null; })()
    """)
    if not present:
        record("QA-L7-02", "PASS", "'JIT (channel) completed' absent from document.body.textContent")
    else:
        record("QA-L7-02", "FAIL",
               "spec: document.body.textContent contains NO occurrence of 'JIT (channel) completed' "
               "— 'not in the table, not in the legend, not in the modal'. "
               f"page: it IS present, in legend item 7: …{where!r}")


def qa_l8_03(page):
    fresh(page)
    d = page.evaluate("""
      (() => { const r = window.__qa.rowByOid('MKT-40233');
        const pills=[...r.cells[6].querySelectorAll('.locpill')];
        const s=getComputedStyle(pills[1]);
        return {n:pills.length, first:pills[0].textContent, second:pills[1].textContent,
                bg:s.backgroundColor, bc:s.borderTopColor, fg:s.color,
                vars:{amber:getComputedStyle(document.documentElement).getPropertyValue('--amber').trim(),
                      soft:getComputedStyle(document.documentElement).getPropertyValue('--amber-soft').trim(),
                      line:getComputedStyle(document.documentElement).getPropertyValue('--amber-line').trim()}};})()
    """)
    def hx(rgb):
        import re
        m = re.findall(r"\d+", rgb)
        return "#" + "".join(f"{int(x):02X}" for x in m[:3])
    ok = (d["n"] == 2 and d["first"] == "A-01-04" and d["second"] == "Not inbounded" and
          hx(d["bg"]).lower() == d["vars"]["soft"].lower() and
          hx(d["bc"]).lower() == d["vars"]["line"].lower() and
          hx(d["fg"]).lower() == d["vars"]["amber"].lower())
    record("QA-L8-03", "PASS" if ok else "FAIL",
           f"pills={d['n']} [{d['first']!r},{d['second']!r}] bg={hx(d['bg'])} border={hx(d['bc'])} color={hx(d['fg'])} vs vars {d['vars']}")


def qa_l9_02(page):
    fresh(page)
    page.click("button.cmtbtn[data-open='crow1']")
    d = page.evaluate("""
      (() => { const c=document.getElementById('crow1');
        return {who:c.querySelector('.who').textContent, at:c.querySelector('.at').textContent,
                text:c.querySelector('.c-item span:not(.who)').textContent.replace('@Yongwon','').trim(),
                time:c.querySelector('time').textContent};})()
    """)
    ok = (d["who"] == "Egita" and d["at"] == "@Yongwon" and
          d["text"] == "Please double-check the ×5 quantity." and d["time"] == "07-21 09:40")
    record("QA-L9-02", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))


def qa_l9_03(page):
    fresh(page)
    p1 = page.evaluate("document.querySelector('#crow1 input').placeholder")
    p2 = page.evaluate("document.querySelector('#crow2 input').placeholder")
    e1 = "Write a comment — @mention sends an automatic Slack notification (order no. · text · time · author)"
    e2 = "Write a comment — @mention sends an automatic Slack notification"
    ok = p1 == e1 and p2 == e2
    record("QA-L9-03", "PASS" if ok else "FAIL", f"crow1={p1!r} crow2={p2!r}")


def qa_l9_06(page):
    fresh(page)
    owner = page.evaluate("""
      (() => { const f=id=>{const r=document.getElementById(id);
          const prev=r.previousElementSibling; return prev.querySelector('.oid').textContent;};
        return {crow4:f('crow4'), crow5:f('crow5')};})()
    """)
    page.click(".cmtbtn[data-open='crow5']")
    opened = page.evaluate("""
      (() => { const r=document.getElementById('crow5');
        return {disp:r.style.display, above:r.previousElementSibling.querySelector('.oid').textContent};})()
    """)
    ok = owner == {"crow4": "422164", "crow5": "MKT-40233"} and opened["disp"] == "table-row" and opened["above"] == "MKT-40233"
    record("QA-L9-06", "PASS" if ok else "FAIL", f"owners={owner}; after click crow5 {opened}")


def qa_l10_04(page):
    fresh(page)
    page.click(".icon-btn[data-open='inbox1']")
    star = page.locator("#inbox1 [data-pane='mentions'] .it").first.locator(".star")
    star.click()
    on1 = page.evaluate("document.querySelector(\"#inbox1 [data-pane='mentions'] .it .star\").classList.contains('on')")
    t1 = page.evaluate("document.getElementById('toast').style.display")
    star.click()
    on2 = page.evaluate("document.querySelector(\"#inbox1 [data-pane='mentions'] .it .star\").classList.contains('on')")
    t2 = page.evaluate("document.getElementById('toast').style.display")
    ok = on1 and not on2 and t1 == "none" and t2 == "none"
    record("QA-L10-04", "PASS" if ok else "FAIL", f"on after 1st={on1}, after 2nd={on2}; toast display {t1!r}/{t2!r}")


def qa_l10_05(page):
    fresh(page)
    page.click(".icon-btn[data-open='inbox1']")
    page.fill("#inbox1 .csearch input", "422")
    d = page.evaluate("""
      (() => { const dd=document.getElementById('inbox1');
        const pane=dd.querySelector('[data-pane="csr"]');
        return {tabs:getComputedStyle(dd.querySelector('.tabs')).display,
                header:pane.querySelector('.paneheader').textContent,
                items:[...pane.querySelectorAll('.it')].map(i=>i.textContent.replace(/\\s+/g,' ').trim()),
                marks:[...pane.querySelectorAll('.it')].map(i=>i.querySelectorAll('mark').length)};})()
    """)
    order_ok = all(o in d["items"][i] for i, o in enumerate(["422165", "422221", "422176", "422108"])) \
        and all(t in d["items"][i] for i, t in enumerate(["10:12", "09:40", "08:52", "16:45"]))
    ok = (d["tabs"] == "none" and d["header"] == "4 results · newest first · click to open the order"
          and len(d["items"]) == 4 and order_ok and all(m >= 1 for m in d["marks"]))
    record("QA-L10-05", "PASS" if ok else "FAIL",
           f"tabs={d['tabs']!r} header={d['header']!r} order ok={order_ok} marks/row={d['marks']}")


def qa_l10_07(page):
    fresh(page)
    page.click(".icon-btn[data-open='inbox1']")
    page.fill("#inbox1 .csearch input", "zzzz")
    d = page.evaluate("""
      (() => { const p=document.querySelector('#inbox1 [data-pane="csr"]');
        return {h:p.querySelector('.paneheader').textContent, body:p.querySelector('.empty') ? p.querySelector('.empty').textContent : null};})()
    """)
    ok = d["h"] == "0 results · newest first · click to open the order" and d["body"] == "No matching comments"
    record("QA-L10-07", "PASS" if ok else "FAIL", f"{d}")


def qa_l10_08(page):
    fresh(page)
    page.click(".icon-btn[data-open='inbox1']")
    page.click("#inbox1 .tabs button[data-tab='saved']")
    page.fill("#inbox1 .csearch input", "422")
    page.fill("#inbox1 .csearch input", "")
    d = page.evaluate("""
      (() => { const dd=document.getElementById('inbox1');
        return {tabs:getComputedStyle(dd.querySelector('.tabs')).display,
                saved:getComputedStyle(dd.querySelector('[data-pane="saved"]')).display,
                mentions:getComputedStyle(dd.querySelector('[data-pane="mentions"]')).display};})()
    """)
    ok = d["tabs"] != "none" and d["saved"] != "none" and d["mentions"] == "none"
    record("QA-L10-08", "PASS" if ok else "FAIL", f"{d}")


def qa_l10_09(page):
    fresh(page)
    page.click(".icon-btn[data-open='inbox1']")
    page.click("#inbox1 .csearch input")
    inside = page.evaluate("document.getElementById('inbox1').classList.contains('open')")
    page.mouse.click(600, 700)
    outside = page.evaluate("document.getElementById('inbox1').classList.contains('open')")
    ok = inside and not outside
    record("QA-L10-09", "PASS" if ok else "FAIL", f"open after inside click={inside}; after outside click={outside}")


def qa_l10_10(page):
    fresh(page)
    page.click(".icon-btn[data-open='inbox1']")
    page.fill("#inbox1 .csearch input", "4")
    items = page.evaluate("[...document.querySelectorAll('#inbox1 [data-pane=\"csr\"] .it')].map(i=>i.textContent.replace(/\\s+/g,' ').trim())")
    ok = len(items) == 5 and any("422108" in i for i in items) and any("421990" in i for i in items)
    record("QA-L10-10", "PASS" if ok else "FAIL", f"{len(items)} results; includes 422108/421990 = "
           f"{any('422108' in i for i in items)}/{any('421990' in i for i in items)}")


def qa_l11_01(page):
    fresh(page)
    pad = page.evaluate("getComputedStyle(document.querySelector('.pagepad')).padding")
    eq("QA-L11-01", pad, "16px 14px 0px")


def qa_l13_03(page):
    fresh(page)
    th = page.evaluate("document.querySelectorAll('.tbl thead th').length")
    cb = page.evaluate("document.querySelectorAll('.cb-ready').length")
    ok = th == 9 and cb == 0
    record("QA-L13-03", "PASS" if ok else "FAIL", f"thead th={th}; elements with class cb-ready={cb}")


def qa_l14_05(page):
    fresh(page)
    page.click("button.cmtbtn[data-open='crow1']")
    before = page.evaluate("document.getElementById('crow1').style.display")
    page.click(".vtab[data-view='jit']")
    after1 = page.evaluate("document.getElementById('crow1').style.display")
    page.click(".vtab[data-view='all']")
    after2 = page.evaluate("document.getElementById('crow1').style.display")
    vis = page.evaluate("window.__qa.rows().filter(r=>getComputedStyle(r).display!=='none').length")
    found = page.evaluate("document.getElementById('foundTxt').textContent")
    ok = (before == "table-row" and after1 == "none" and after2 == "none" and vis == 5
          and found == "Found 5 order(s) with items ready for outbound")
    record("QA-L14-05", "PASS" if ok else "FAIL",
           f"crow1 {before!r}→JIT {after1!r}→All {after2!r}; visible rows={vis}; foundTxt={found!r}")


def qa_l14_07(page):
    fresh(page)
    page.click(".vtab[data-view='mkt']")
    found = page.evaluate("document.getElementById('foundTxt').textContent")
    eq("QA-L14-07", found, "Found 1 order(s) with items ready for outbound")


def qa_f_01(page):
    fresh(page)
    h2 = page.evaluate("document.querySelector('.ptitle h2').textContent")
    h3 = page.evaluate("document.querySelector('.psub h3').textContent")
    ok = (h2 == "WMS - Ready to be Outbonded" and h3 == "Ready to be Outbonded Orders"
          and "Outbounded" not in h2 and "Outbounded" not in h3)
    record("QA-F-01", "PASS" if ok else "FAIL", f"h2={h2!r} h3={h3!r}")


def qa_f_04(page):
    fresh(page)
    b = page.evaluate("document.querySelector('.howto b').textContent")
    lis = page.evaluate("[...document.querySelectorAll('.howto li')].map(l=>l.textContent)")
    exp = ['Click "Refresh" to load the latest orders ready for outbound',
           'Orders shown here have at least one line item with "INBOUNDED" status',
           'Click the Order ID link to see full order details and process outbound',
           'Only items marked as INBOUNDED are ready for outbound processing',
           'This page uses the dedicated readyToBeOutbonded API for optimized results']
    ok = b == "How to use:" and lis == exp
    record("QA-F-04", "PASS" if ok else "FAIL", f"b={b!r}; {len(lis)} li, match={lis == exp}")


def qa_f_06(page):
    fresh(page)
    exact = page.evaluate("[...document.querySelectorAll('*')].filter(e=>e.textContent==='View Order').length")
    contains = page.evaluate("""
      [...document.querySelectorAll('*')].filter(e=>!e.children.length && (e.textContent||'').includes('View Order')).map(e=>e.tagName)
    """)
    contains_any = page.evaluate("document.body.textContent.includes('View Order')")
    printcol = page.evaluate("""
      (() => window.__qa.rows().every(r => { const c=r.cells[8];
          return [...c.children].every(x=>x.classList.contains('printbtn')) && c.children.length===1; }))()
    """)
    record("QA-F-06", "AMBIGUOUS",
           f"under equality reading ('has textContent \"View Order\"') it PASSES: 0 elements equal it, "
           f"Print column holds only .printbtn = {printcol}. Under the containment reading used by the "
           f"sibling scenario QA-L7-02 it FAILS: document.body.textContent contains 'View Order' = {contains_any} "
           f"(legend prose 'View Order button removed'). Spec does not say which reading applies.")


def qa_f_08(page):
    fresh(page)
    lis = page.evaluate("document.querySelectorAll('.legend ol > li').length")
    ns = page.evaluate("[...document.querySelectorAll('.legend ol > li .n')].map(n=>n.textContent)")
    dots = page.evaluate("document.querySelectorAll('.dot').length")
    inmock = page.evaluate("document.querySelectorAll('.mock .dot').length")
    inm1 = page.evaluate("document.querySelectorAll('#m-pick .dot').length")
    ok = (lis == 14 and ns == "1 2 3 4 5 6 7 8 14 13 12 9 10 11".split()
          and dots == 15 and inmock == 14 and inm1 == 1)
    record("QA-F-08", "PASS" if ok else "FAIL", f"li={lis} order={' '.join(ns)}; .dot={dots} (.mock {inmock} + #m-pick {inm1})")


def qa_f_09(page):
    fresh(page)
    page.click("#annoToggle")
    d1 = page.evaluate("""
      (() => ({cls:document.body.classList.contains('no-anno'),
               dots:[...document.querySelectorAll('.dot')].every(d=>getComputedStyle(d).display==='none'),
               legend:getComputedStyle(document.querySelector('.legend')).display,
               txt:document.getElementById('annoToggle').textContent}))()
    """)
    page.click("#annoToggle")
    d2 = page.evaluate("""
      (() => ({cls:document.body.classList.contains('no-anno'),
               dots:[...document.querySelectorAll('.mock .dot')].every(d=>getComputedStyle(d).display!=='none'),
               legend:getComputedStyle(document.querySelector('.legend')).display,
               txt:document.getElementById('annoToggle').textContent}))()
    """)
    ok = (d1["cls"] and d1["dots"] and d1["legend"] == "none" and d1["txt"] == "Show annotations"
          and not d2["cls"] and d2["dots"] and d2["legend"] != "none" and d2["txt"] == "Hide annotations")
    record("QA-F-09", "PASS" if ok else "FAIL", f"after hide {d1}; after show {d2}")


def qa_e_01(page):
    fresh(page)
    errs_before = len(_console_errors)
    page.evaluate("document.querySelector('tr[data-view=\"mkt\"]:not(.crow)').remove()")
    page.click(".vtab[data-view='mkt']")
    vis = page.evaluate("window.__qa.rows().filter(r=>getComputedStyle(r).display!=='none').length")
    found = page.evaluate("document.getElementById('foundTxt').textContent")
    ok = not _console_errors[errs_before:] and vis == 0 and found == "Found 0 order(s) with items ready for outbound"
    record("QA-E-01", "PASS" if ok else "FAIL",
           f"exceptions={_console_errors[errs_before:]}; visible order rows={vis}; foundTxt={found!r}")


def qa_e_02(page):
    fresh(page)
    page.evaluate("""
      (() => {
        window.AudioContext=function(){throw new Error('stub');};
        window.webkitAudioContext=function(){throw new Error('stub');};
        return 'stubbed';
      })()
    """)
    errs_before = len(_console_errors)
    run_batch(page, "button.bulk-run[data-label='Bulk Outbound']", 1500)
    w = page.evaluate("window.__qa.pfill()")
    tb = page.evaluate("window.__qa.toastB()")
    ok = not _console_errors[errs_before:] and w == "100%" and tb == "✓ Bulk Outbound complete — 3 orders"
    record("QA-E-02", "PASS" if ok else "FAIL",
           f"uncaught={_console_errors[errs_before:]}; pfill={w!r}; toast b={tb!r}")


def qa_e_05(page):
    fresh(page)
    start_sampler(page)
    page.focus("button.bulk-run[data-label='Bulk Outbound']")
    page.keyboard.press("Enter")
    page.wait_for_timeout(1600)
    s = stop_sampler(page)
    resets = sum(1 for a, b in zip([None] + [x["w"] for x in s], [x["w"] for x in s]) if b == "0%" and a != "0%")
    toast_edges = sum(1 for a, b in zip([{"td": "none"}] + s, s) if b["td"] == "flex" and a["td"] != "flex")
    tb = page.evaluate("window.__qa.toastB()")
    ok = resets == 1 and toast_edges == 1 and tb == "✓ Bulk Outbound complete — 3 orders"
    record("QA-E-05", "PASS" if ok else "FAIL",
           f"progress runs (0% resets)={resets}; toast show-transitions={toast_edges}; b={tb!r}")


def qa_m1_04(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    skus = page.evaluate("[...document.querySelectorAll('#m-pick .picktbl tbody tr')].map(r=>r.cells[1].textContent)")
    grid = page.evaluate("[...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow) .skupill')].map(s=>s.textContent)")
    ok = skus == ["100039958", "100039420", "100035912", "100013286"] and all(s in grid for s in skus)
    record("QA-M1-04", "PASS" if ok else "FAIL", f"M1 skus={skus}; all present among grid .skupill {grid}")


def qa_l6_01(page):
    fresh(page)
    for sel in ("button.bulk-run[data-label='Bulk Print Labels']", "button.bulk-run[data-label='Bulk Outbound']"):
        page.click(sel)
        page.wait_for_function("document.getElementById('toast').style.display==='flex'", timeout=5000)
        d = page.evaluate("document.getElementById('toast').style.display")
        s = page.evaluate("(()=>{const c=getComputedStyle(document.getElementById('toast'));return {top:c.top,right:c.right};})()")
        t = time.time()
        page.wait_for_function("document.getElementById('toast').style.display==='none'", timeout=6000)
        dwell = time.time() - t
        if not (d == "flex" and s["top"] == "54px" and s["right"] == "16px" and 2.5 <= dwell <= 4.5):
            record("QA-L6-01", "FAIL", f"{sel}: display={d!r} {s} dwell={dwell:.2f}s")
            return
    record("QA-L6-01", "PASS", f"display:flex, top 54px / right 16px, auto-dismiss ~{dwell:.2f}s for both actions")


def qa_l7_01(page):
    fresh(page)
    t = page.evaluate("window.__qa.rowByOid('422164').querySelector('.jit-badge').textContent")
    eq("QA-L7-01", t, "Fully Inbounded")


def qa_l7_03(page):
    fresh(page)
    cls = page.evaluate("window.__qa.rowByOid('422164').classList.contains('row-jit')")
    order = page.evaluate("window.__qa.rows().map(r=>r.querySelector('.oid').textContent)")
    ok = cls and order[-1] == "422164" and order[-2] == "MKT-40233"
    record("QA-L7-03", "PASS" if ok else "FAIL", f"row-jit={cls}; document order={order}")


def qa_l8_04(page):
    fresh(page)
    order = page.evaluate("window.__qa.rows().map(r=>r.querySelector('.oid').textContent)")
    eq("QA-L8-04", order, ["422221", "422176", "422165", "MKT-40233", "422164"])


def qa_l9_05(page):
    fresh(page)
    d = page.evaluate("""
      (() => { const o={}; for (const r of window.__qa.rows()) {
          const b=r.querySelector('.cmtbtn .badge-n');
          o[r.querySelector('.oid').textContent] = b ? b.textContent : null; } return o; })()
    """)
    ok = d == {"422221": "1", "422176": None, "422165": "1", "MKT-40233": None, "422164": None}
    record("QA-L9-05", "PASS" if ok else "FAIL", f"{d}")


def qa_l10_02(page):
    fresh(page)
    page.click(".icon-btn[data-open='inbox1']")
    d = page.evaluate("""
      (() => { const p=document.querySelector('#inbox1 [data-pane="mentions"]');
        return {n:p.querySelectorAll('.it.unread').length,
                items:[...p.querySelectorAll('.it.unread')].map(i=>i.querySelector('.body').textContent),
                times:[...p.querySelectorAll('.it.unread time')].map(t=>t.textContent),
                header:p.querySelector('.paneheader').textContent,
                mark:p.querySelector('.paneheader small').textContent};})()
    """)
    ok = (d["n"] == 2 and
          d["items"][0].startswith('Order 422165 · Dean: "@Yongwon Please take extra care packing this order"') and
          d["items"][1].startswith('Order 422221 · Egita: "@Yongwon Please double-check the ×5 quantity"') and
          d["times"] == ["10:12", "09:40"] and
          d["header"].startswith("Comments mentioning me · Click to open the order") and d["mark"] == "Mark all read")
    record("QA-L10-02", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False)[:400])


def qa_l10_06(page):
    fresh(page)
    page.click(".icon-btn[data-open='inbox1']")
    page.fill("#inbox1 .csearch input", "Aldo")
    items = page.evaluate("[...document.querySelectorAll('#inbox1 [data-pane=\"csr\"] .it')].map(i=>i.textContent.replace(/\\s+/g,' ').trim())")
    tablerows = page.evaluate("window.__qa.rows().map(r=>r.querySelector('.oid').textContent)")
    ok = len(items) == 1 and "421990" in items[0] and "421990" not in tablerows
    record("QA-L10-06", "PASS" if ok else "FAIL", f"{len(items)} result(s): {items}; 421990 in table = {'421990' in tablerows}")


def qa_l11_02(page):
    fresh(page)
    d = page.evaluate("""
      ({wrap:getComputedStyle(document.querySelector('.mockwrap')).overflowX,
        mock:getComputedStyle(document.querySelector('.mock')).minWidth})
    """)
    ok = d["wrap"] == "auto" and d["mock"] == "1240px"
    record("QA-L11-02", "PASS" if ok else "FAIL", f"{d}")


def qa_l12_02(page):
    fresh(page)
    d = page.evaluate("""
      (() => { const r=window.__qa.rowByOid('422165');
        return {items:[...r.cells[5].querySelectorAll('.item-line')].map(i=>i.textContent),
                locs:[...r.cells[6].querySelectorAll('.locline')].map(l=>l.textContent)};})()
    """)
    ok = (len(d["items"]) == 2 and len(d["locs"]) == 2 and d["locs"][0] == "A-03-02"
          and d["locs"][1] == "B-02-11" and "마데카 크림 타이트닝" in d["items"][0])
    record("QA-L12-02", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))


def qa_l13_01(page):
    fresh(page)
    d = page.evaluate("""
      (() => { const o={}; for (const r of window.__qa.rows())
          o[r.querySelector('.oid').textContent]=r.querySelector('.cntbadge').textContent; return o; })()
    """)
    ok = d["422221"] == "5" and d["422176"] == "1" and d["422165"] == "2"
    record("QA-L13-01", "PASS" if ok else "FAIL", f"{d}")


def qa_l14_01(page):
    fresh(page)
    on = page.evaluate("document.querySelector('.vtab[data-view=\"all\"]').classList.contains('on')")
    labels = page.evaluate("[...document.querySelectorAll('.vtab')].map(t=>t.textContent)")
    ok = on and labels == ["All (5)", "Inventory (3)", "Marketing (1)", "JIT (1)"]
    record("QA-L14-01", "PASS" if ok else "FAIL", f"all.on={on} labels={labels}")


def qa_f_05(page):
    fresh(page)
    d = page.evaluate("""
      (() => { const th=[...document.querySelectorAll('.tbl thead th')];
        return {n:th.length, firstCb:!!th[0].querySelector('input[type=checkbox]'), firstTxt:th[0].textContent,
                rest:th.slice(1).map(t=>t.textContent),
                rows:window.__qa.rows().length, print:document.querySelectorAll('.printbtn').length};})()
    """)
    exp = ["Order ID", "Order Date", "Customer", "Total Items", "Ready Item Details", "Pick Locations", "Comments", "Print"]
    ok = (d["n"] == 9 and d["firstCb"] and d["firstTxt"] == "" and
          all(a.startswith(b) for a, b in zip(d["rest"], exp)) and d["rows"] == 5 and d["print"] == 5)
    record("QA-F-05", "PASS" if ok else "FAIL", json.dumps(d, ensure_ascii=False))


def qa_f_07(page):
    fresh(page)
    dates = page.evaluate("window.__qa.rows().map(r=>r.cells[2].textContent)")
    ok = dates == ["2026. 7. 21."] * 5
    record("QA-F-07", "PASS" if ok else "FAIL", f"{dates}")


def qa_f_11(page):
    fresh(page)
    d = page.evaluate("""
      (() => { const o=[...document.querySelectorAll('.oid')];
        return {n:o.length, tags:[...new Set(o.map(x=>x.tagName))],
                href:o.some(x=>x.hasAttribute('href')), anc:o.some(x=>x.closest('a')),
                txt:o.map(x=>x.textContent)};})()
    """)
    ok = (d["n"] == 5 and d["tags"] == ["SPAN"] and not d["href"] and not d["anc"]
          and d["txt"] == ["422221", "422176", "422165", "MKT-40233", "422164"])
    record("QA-F-11", "PASS" if ok else "FAIL", f"{d}")


def qa_e_03(page):
    fresh(page)
    ws = page.evaluate("getComputedStyle(document.querySelector('.item-line')).whiteSpace")
    last = page.evaluate("""
      window.__qa.rows().every(r=>[...r.cells[5].querySelectorAll('.item-line')]
        .every(l=>l.lastElementChild && l.lastElementChild.classList.contains('qtypill')))
    """)
    ok = ws == "nowrap" and last
    record("QA-E-03", "PASS" if ok else "FAIL", f"white-space={ws!r}; ×qty pill is last element of every line = {last}")


def qa_e_04(page):
    fresh(page)
    page.set_viewport_size({"width": 800, "height": 800})
    page.wait_for_timeout(150)
    d = page.evaluate("""
      (() => { const w=document.querySelector('.mockwrap');
        return {ox:getComputedStyle(w).overflowX, mw:getComputedStyle(document.querySelector('.mock')).minWidth,
                scroll:w.scrollWidth>w.clientWidth, th:document.querySelectorAll('.tbl thead th').length};})()
    """)
    page.set_viewport_size({"width": 1440, "height": 900})
    ok = d["ox"] == "auto" and d["mw"] == "1240px" and d["scroll"] and d["th"] == 9
    record("QA-E-04", "PASS" if ok else "FAIL", f"{d}")


def qa_e_06(page):
    fresh(page)
    page.click("button.btn-line[data-modal='m-pick']")
    d = page.evaluate("""
      (() => { const r=window.__qa.rowByOid('422165');
        return {skus:[...r.cells[5].querySelectorAll('.item-line .skupill')].map(s=>s.textContent),
                lines:r.cells[5].querySelectorAll('.item-line').length,
                locs:r.cells[6].querySelectorAll('.locline').length,
                m1:[...document.querySelectorAll('#m-pick .picktbl tbody tr')]
                     .filter(t=>t.cells[4].textContent==='422165').length};})()
    """)
    ok = (d["skus"] == ["100039420", "100013286"] and d["lines"] == 2 and d["locs"] == 2 and d["m1"] == 2)
    record("QA-E-06", "PASS" if ok else "FAIL", f"{d}")


SCENARIOS = [
    ("QA-L1-01", qa_l1_01), ("QA-L1-02", qa_l1_02), ("QA-L1-04", qa_l1_04),
    ("QA-L2-02", qa_l2_02), ("QA-L2-03", qa_l2_03),
    ("QA-M1-01", qa_m1_01), ("QA-M1-03", qa_m1_03), ("QA-M1-04", qa_m1_04), ("QA-M1-05", qa_m1_05),
    ("QA-M1-06", qa_m1_06), ("QA-M1-07", qa_m1_07), ("QA-M1-08", qa_m1_08),
    ("QA-M1-09", qa_m1_09), ("QA-M1-10", qa_m1_10), ("QA-M1-11", qa_m1_11), ("QA-M1-12", qa_m1_12),
    ("QA-L3-01", qa_l3_01), ("QA-L3-02", qa_l3_02), ("QA-L3-03", qa_l3_03), ("QA-L3-04", qa_l3_04),
    ("QA-L4-01", qa_l4_01), ("QA-L4-02", qa_l4_02), ("QA-L4-03", qa_l4_03),
    ("QA-L4-04", qa_l4_04), ("QA-L4-05", qa_l4_05),
    ("QA-L5-01", qa_l5_01), ("QA-L5-02", qa_l5_02), ("QA-L5-04", qa_l5_04), ("QA-L5-05", qa_l5_05),
    ("QA-L6-01", qa_l6_01), ("QA-L6-02", qa_l6_02), ("QA-L6-03", qa_l6_03),
    ("QA-L6-04", qa_l6_04), ("QA-L6-05", qa_l6_05),
    ("QA-L7-01", qa_l7_01), ("QA-L7-02", qa_l7_02), ("QA-L7-03", qa_l7_03),
    ("QA-L8-03", qa_l8_03), ("QA-L8-04", qa_l8_04),
    ("QA-L9-02", qa_l9_02), ("QA-L9-03", qa_l9_03), ("QA-L9-05", qa_l9_05), ("QA-L9-06", qa_l9_06),
    ("QA-L10-02", qa_l10_02), ("QA-L10-04", qa_l10_04), ("QA-L10-05", qa_l10_05),
    ("QA-L10-06", qa_l10_06), ("QA-L10-07", qa_l10_07),
    ("QA-L10-08", qa_l10_08), ("QA-L10-09", qa_l10_09), ("QA-L10-10", qa_l10_10),
    ("QA-L11-01", qa_l11_01), ("QA-L11-02", qa_l11_02),
    ("QA-L12-02", qa_l12_02),
    ("QA-L13-01", qa_l13_01), ("QA-L13-03", qa_l13_03),
    ("QA-L14-01", qa_l14_01), ("QA-L14-05", qa_l14_05), ("QA-L14-07", qa_l14_07),
    ("QA-F-01", qa_f_01), ("QA-F-04", qa_f_04), ("QA-F-05", qa_f_05), ("QA-F-06", qa_f_06),
    ("QA-F-07", qa_f_07), ("QA-F-08", qa_f_08), ("QA-F-09", qa_f_09), ("QA-F-11", qa_f_11),
    ("QA-E-01", qa_e_01), ("QA-E-02", qa_e_02), ("QA-E-03", qa_e_03),
    ("QA-E-04", qa_e_04), ("QA-E-05", qa_e_05), ("QA-E-06", qa_e_06),
]


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("--")]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless="--headed" not in sys.argv)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.on("pageerror", lambda e: _console_errors.append(str(e)))
        for sid, fn in SCENARIOS:
            if only and sid not in only:
                continue
            try:
                fn(page)
            except Exception as ex:                                  # noqa: BLE001
                record(sid, "ERROR", f"{type(ex).__name__}: {ex}")
        browser.close()
    counts = {}
    for _, v, _ in RESULTS:
        counts[v] = counts.get(v, 0) + 1
    print("\n== SUMMARY ==")
    print(json.dumps({"attempted": len(RESULTS), "counts": counts,
                      "fails": [r for r in RESULTS if r[1] in ("FAIL", "ERROR")]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
