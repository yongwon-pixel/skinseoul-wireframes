#!/usr/bin/env python3
"""QA runner — ready-to-outbound spec v1.2 §8, all [WF] scenarios (93).

Target: wms2/ready-to-outbound/index.html via file:// (baseline review-baseline-20260803).
Reset rule (§8.0): fresh page load before every scenario. [ADMIN] scenarios are deferred
rows, not failures — they are not represented here.
Reading rules honoured (§8.0): #pfill inline width only; #pbarLabel.childNodes[0];
M1 header first text node; running-label samples retained only from width >= 20%.
"""
import json, re, sys
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


WF_URL = (Path(__file__).resolve().parents[3] / "ready-to-outbound" / "index.html").as_uri()

IDLE_LABEL = "Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion"
DEFAULT_SUB = "Disappears automatically after a few seconds"

BTN = {
    "ppl": "document.querySelectorAll('.bulkbar button')[0]",
    "bpl": "document.querySelectorAll('.bulkbar button')[1]",
    "bo":  "document.querySelectorAll('.bulkbar button')[2]",
    "m1":  "document.querySelector('#m-pick .foot .bulk-run')",
}

RUN_JS = """
(btnExpr) => new Promise((resolve) => {
  const btn = eval(btnExpr);
  const fill = document.getElementById('pfill'), label = document.getElementById('pbarLabel');
  const toast = document.getElementById('toast'), mp = document.getElementById('m-pick');
  const samples = [];
  const push = () => samples.push({w: fill.style.width, l: label.childNodes[0].textContent,
                                   t: toast.style.display, m: mp.classList.contains('open')});
  const guard = setTimeout(() => { clearInterval(iv); resolve({timeout: true, samples}); }, 15000);
  const iv = setInterval(() => { push();
    if (fill.style.width === '100%') { clearInterval(iv); clearTimeout(guard);
      setTimeout(() => resolve({timeout: false, samples,
        toastB: toast.querySelector('b').textContent,
        toastS: toast.querySelector('small').textContent,
        toastDisplay: toast.style.display}), 60); }
  }, 50);
  btn.click(); push();
})
"""

TOAST_TIMING_JS = """
(btnExpr) => new Promise((resolve) => {
  const btn = eval(btnExpr);
  const toast = document.getElementById('toast');
  let shownAt = null, info = null;
  const guard = setTimeout(() => { clearInterval(iv); resolve({timeout: true}); }, 20000);
  const iv = setInterval(() => {
    const vis = toast.style.display !== 'none';
    if (vis && shownAt === null) { shownAt = performance.now();
      const cs = getComputedStyle(toast);
      info = {display: toast.style.display, top: cs.top, right: cs.right,
              b: toast.querySelector('b').textContent}; }
    if (!vis && shownAt !== null) { clearTimeout(guard); clearInterval(iv);
      resolve(Object.assign({timeout: false, dur: performance.now() - shownAt}, info)); }
  }, 50);
  btn.click();
})
"""

ROWS_JS = """() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')].map(r => ({
  oid: r.querySelector('.oid').textContent,
  checked: r.querySelector('input[type=checkbox]').checked,
  visible: r.style.display !== 'none'}))"""

M1_ROWS_JS = """() => [...document.querySelectorAll('#m-pick .picktbl tbody tr')].map(tr => {
  const td = [...tr.children];
  return {loc: td[0].textContent.trim(), pill: td[0].querySelector('.locpill') ? td[0].querySelector('.locpill').textContent : null,
          sku: td[1].textContent.trim(), prod: td[2].textContent.trim(),
          qty: td[3].textContent.trim(), qtyBold: !!td[3].querySelector('b'),
          order: td[4].textContent.trim()};
})"""


class Fail(Exception):
    def __init__(self, expected, actual):
        self.expected, self.actual = expected, actual


def check(cond, expected, actual):
    if not cond:
        raise Fail(expected, str(actual))


def retained(samples):
    out = []
    for s in samples:
        w = s["w"]
        if w and w.endswith("%") and int(w[:-1]) >= 20:
            out.append(s)
    return out


def run_batch(page, key):
    r = page.evaluate(RUN_JS, BTN[key])
    check(not r.get("timeout"), "batch reaches 100%", "sampler timeout — run never completed")
    return r


def open_m1(page):
    page.evaluate(f"() => {{ {BTN['ppl']}.click(); }}")
    check(page.evaluate("() => document.getElementById('m-pick').classList.contains('open')"),
          "#m-pick gains class open", "modal did not open")


def wait_toast_hidden(page):
    page.wait_for_function("() => document.getElementById('toast').style.display === 'none'",
                           timeout=6000)


SCN = []
def scenario(sid):
    def deco(fn):
        SCN.append((sid, fn)); return fn
    return deco


# ---------------- QA-L1 ----------------

@scenario("QA-L1-01")
def _(page, errors):
    rows = page.evaluate(ROWS_JS)
    check(len(rows) == 5, "5 order rows in .tbl tbody tr[data-view]:not(.crow)", f"{len(rows)} rows")
    got = {r["oid"]: r["checked"] for r in rows}
    exp = {"422221": True, "422176": True, "422165": True, "MKT-40233": False, "422164": False}
    check(got == exp, "422221/422176/422165 checked; MKT-40233/422164 unchecked", got)
    cnt = page.text_content(".bulkbar .cnt")
    check(cnt == "3 selected", ".bulkbar .cnt textContent equals `3 selected`", cnt)


@scenario("QA-L1-02")
def _(page, errors):
    labels = page.evaluate("() => [...document.querySelectorAll('.bulkbar button')].map(b => b.textContent)")
    exp = ["🖨 Print Pick Locations (3 orders · 8 items)", "🖨 Bulk Print Labels (3 orders)",
           "📦 Bulk Outbound (3 orders)"]
    check(labels == exp, str(exp), labels)


@scenario("QA-L1-03")
def _(page, errors):
    badges = page.evaluate("""() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .filter(r => r.querySelector('input[type=checkbox]').checked)
      .map(r => parseInt(r.querySelector('.cb-total').textContent))""")
    check(sorted(badges) == [1, 2, 5], "checked rows' Total Items badges are 5, 1, 2", badges)
    check(sum(badges) == 8, "badge sum is 8", sum(badges))
    lbl = page.evaluate(f"() => {BTN['ppl']}.textContent")
    check("8 items" in lbl, "`8 items` in the [L-2] label", lbl)
    hdr = page.evaluate("() => document.querySelector('#m-pick .modal > header').firstChild.textContent")
    check("8 units total" in hdr, "`8 units total` in the M1 header", hdr)


@scenario("QA-L1-04")
def _(page, errors):
    page.click(".bulkbar label input[type=checkbox]")
    page.click(".tbl thead input[type=checkbox]")
    rows = page.evaluate(ROWS_JS)
    got = {r["oid"]: r["checked"] for r in rows}
    exp = {"422221": True, "422176": True, "422165": True, "MKT-40233": False, "422164": False}
    check(got == exp, "the five row checkboxes are unchanged ([RTO-WFX-1])", got)
    cnt = page.text_content(".bulkbar .cnt")
    check(cnt == "3 selected", "`.bulkbar .cnt` still reads `3 selected`", cnt)
    labels = page.evaluate("() => [...document.querySelectorAll('.bulkbar button')].map(b => b.textContent)")
    exp_l = ["🖨 Print Pick Locations (3 orders · 8 items)", "🖨 Bulk Print Labels (3 orders)",
             "📦 Bulk Outbound (3 orders)"]
    check(labels == exp_l, "the three button labels are unchanged", labels)


# ---------------- QA-L2 ----------------

@scenario("QA-L2-01")
def _(page, errors):
    check(not page.evaluate("() => document.getElementById('m-pick').classList.contains('open')"),
          "#m-pick without class open before click", "already open")
    page.evaluate(f"() => {{ {BTN['ppl']}.click(); }}")
    st = page.evaluate("""() => ({open: document.getElementById('m-pick').classList.contains('open'),
      disp: getComputedStyle(document.getElementById('m-pick')).display})""")
    check(st["open"] and st["disp"] == "flex", "#m-pick gains class open and is visible", st)


@scenario("QA-L2-02")
def _(page, errors):
    pre = page.evaluate("() => document.getElementById('pfill').style.width")
    check(pre == "", "#pfill.style.width === '' on fresh load", repr(pre))
    page.evaluate(f"() => {{ {BTN['ppl']}.click(); }}")
    page.wait_for_timeout(2000)
    st = page.evaluate("""() => ({w: document.getElementById('pfill').style.width,
      l: document.getElementById('pbarLabel').childNodes[0].textContent,
      t: document.getElementById('toast').style.display})""")
    check(st["w"] == "", "#pfill.style.width still '' after 2 s", repr(st["w"]))
    check(st["l"] == IDLE_LABEL, f"#pbarLabel still equals `{IDLE_LABEL}`", st["l"])
    check(st["t"] == "none", "#toast still display:none", st["t"])


@scenario("QA-L2-03")
def _(page, errors):
    page.click('.wf-bar button:has-text("Modal: Print Pick Locations (Picking List)")')
    check(page.evaluate("() => document.getElementById('m-pick').classList.contains('open')"),
          "#m-pick opens from the wf-toggle demo button", "not open")
    page.click("#m-pick .x")
    check(not page.evaluate("() => document.getElementById('m-pick').classList.contains('open')"),
          "modal closed with ✕", "still open")
    page.click(".wf-bar button.wf-tab")
    check(page.evaluate("() => document.getElementById('m-pick').classList.contains('open')"),
          "#m-pick opens from the wf-tab demo button too ([RTO-WFX-2])", "not open")


# ---------------- QA-M1 ----------------

@scenario("QA-M1-01")
def _(page, errors):
    open_m1(page)
    hdr = page.evaluate("() => document.querySelector('#m-pick .modal > header').firstChild.textContent")
    exp = "Print Pick Locations — Picking List (3 orders selected · 4 SKUs · 8 units total)"
    check(hdr == exp, f"header first text node equals `{exp}`", hdr)
    badges = page.evaluate("""() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .filter(r => r.querySelector('input[type=checkbox]').checked)
      .map(r => parseInt(r.querySelector('.cb-total').textContent))""")
    check(sum(badges) == 8, "8 equals the sum of selected rows' Total Items badges", sum(badges))


@scenario("QA-M1-02")
def _(page, errors):
    open_m1(page)
    ths = page.evaluate("() => [...document.querySelectorAll('#m-pick .picktbl thead th')].map(t => t.textContent)")
    exp = ["Location", "SKU", "Product", "Qty", "Order"]
    check(ths == exp, str(exp), ths)


@scenario("QA-M1-03")
def _(page, errors):
    open_m1(page)
    rows = page.evaluate(M1_ROWS_JS)
    check(len(rows) == 5, "exactly 5 rows (4 product + sample-set; re-baselined for WF-9)", f"{len(rows)} rows")
    locs = [r["loc"] for r in rows[:4]]
    exp = ["A-02-13", "A-03-02", "B-01-07", "B-02-11"]
    check(locs == exp, f"product-row locations {exp} strictly ascending [BR-7]", locs)
    check(locs == sorted(locs), "strictly ascending", locs)
    check(rows[4]["pill"] == "Sample", "sample row last; first cell is a .locpill reading `Sample`",
          f"pill={rows[4]['pill']!r} loc={rows[4]['loc']!r}")


@scenario("QA-M1-04")
def _(page, errors):
    open_m1(page)
    rows = page.evaluate(M1_ROWS_JS)
    skus = [r["sku"] for r in rows[:4]]
    exp = ["100039958", "100039420", "100035912", "100013286"]
    check(skus == exp, f"SKU column values {exp}", skus)
    main = page.evaluate("""() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .flatMap(r => [...r.querySelectorAll('.item-line')].map(il => ({
        oid: r.querySelector('.oid').textContent, sku: il.querySelector('.skupill').textContent})))""")
    pairs = {(m["oid"], m["sku"]) for m in main}
    for r in rows[:4]:
        check((r["order"], r["sku"]) in pairs,
              f"M1 SKU {r['sku']} matches the .skupill of the {r['order']} main-table item line", pairs)
    check(rows[4]["sku"] == "—", "sample row SKU cell reads `—`", rows[4]["sku"])


@scenario("QA-M1-05")
def _(page, errors):
    open_m1(page)
    rows = page.evaluate(M1_ROWS_JS)
    check(rows[1]["prod"] == "마데카 크림 타이트닝", "row 2 Product `마데카 크림 타이트닝`", rows[1]["prod"])
    check(rows[2]["prod"] == "세라마이드 아토 컨센트레이트 크림", "row 3 Product `세라마이드 아토 컨센트레이트 크림`", rows[2]["prod"])
    check(rows[3]["prod"] == "마데카 크림 타임 리버스", "row 4 Product `마데카 크림 타임 리버스`", rows[3]["prod"])
    check(rows[0]["qty"] == "5" and rows[0]["qtyBold"], "row 1 Qty `5` inside <b>", rows[0])
    check(rows[0]["order"] == "422221", "row 1 Order `422221`", rows[0]["order"])
    for i in (1, 2, 3):
        check(rows[i]["qty"] == "1" and not rows[i]["qtyBold"], f"row {i+1} Qty `1` and not bold", rows[i])
    check(rows[4]["prod"] == "sample set", "row 5 Product exactly `sample set`", rows[4]["prod"])
    check(rows[4]["qty"] == "×1" and rows[4]["qtyBold"], "row 5 Qty `×1` inside <b>", rows[4])


@scenario("QA-M1-06")
def _(page, errors):
    open_m1(page)
    orders = [r["order"] for r in page.evaluate(M1_ROWS_JS)]
    exp = ["422221", "422165", "422176", "422165", "422165"]
    check(orders == exp, f"Order column {exp} — ordered by location, not grouped by order", orders)


@scenario("QA-M1-07")
def _(page, errors):
    open_m1(page)
    rows = page.evaluate(M1_ROWS_JS)
    prod_165 = [r for r in rows[:4] if r["order"] == "422165"]
    check(len(prod_165) == 2 and {r["loc"] for r in prod_165} == {"A-03-02", "B-02-11"},
          "two separate product rows for 422165 (A-03-02, B-02-11) [BR-19]", prod_165)
    for r in rows:
        check(len(re.findall(r"\d{6}", r["order"])) <= 1 and "MKT" not in r["order"].replace("MKT-", ""),
              "no Order cell contains more than one order number", r["order"])
    sample_rows = [r for r in rows if r["pill"] == "Sample"]
    check(len(sample_rows) == 1 and sample_rows[0]["order"] == "422165",
          "exactly one sample-set row exists, naming 422165", sample_rows)


@scenario("QA-M1-08")
def _(page, errors):
    open_m1(page)
    rows = page.evaluate(M1_ROWS_JS)
    check(all(r["sku"] != "100012534" for r in rows),
          "no picking-list row carries SKU 100012534", [r["sku"] for r in rows])
    check(all(r["loc"] != "Not inbounded" for r in rows),
          "no row's Location cell reads `Not inbounded`", [r["loc"] for r in rows])


@scenario("QA-M1-09")
def _(page, errors):
    open_m1(page)
    rows = page.evaluate(M1_ROWS_JS)
    check("Centellian24" not in rows[1]["prod"],
          "row 2 Product does not contain `Centellian24` ([RTO-WFX-5])", rows[1]["prod"])
    has_brand = page.evaluate("""() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .some(r => r.querySelector('.oid').textContent === '422165'
        && [...r.querySelectorAll('.item-line b')].some(b => b.textContent === 'Centellian24'))""")
    check(has_brand, "main-grid row for 422165 renders <b>Centellian24</b>", "not found")
    check(rows[0]["prod"] == "AtoBarrier365 Body …",
          "row 1 Product reads the elided English `AtoBarrier365 Body …`", rows[0]["prod"])


@scenario("QA-M1-10")
def _(page, errors):
    open_m1(page)
    note = page.evaluate("() => document.querySelector('#m-pick .note').textContent")
    exp = ("Sorted by location (ascending) (A-02-13 → B-01-07 → Shelf 3) — pick everything in one pass "
           "along the route. Printing: no refresh · selection kept; progress bar, then a top-right "
           "completion toast.")
    check(note == exp, f"note textContent equals `{exp}`", note)


@scenario("QA-M1-11")
def _(page, errors):
    open_m1(page)
    r = run_batch(page, "m1")
    check(r["samples"][0]["m"] is False, "#m-pick loses class open on Print click", r["samples"][0])
    ret = retained(r["samples"])
    check(len(ret) > 0, "samples exist from the first tick onward", r["samples"])
    check(all("Print Pick Locations in progress" in s["l"] and "No refresh · selection kept" in s["l"]
              for s in ret), "label contains `Print Pick Locations in progress` and `No refresh · selection kept`",
          [s["l"] for s in ret])
    check(all("refreshes after completion" not in s["l"] for s in ret),
          "label does not contain `refreshes after completion`", [s["l"] for s in ret])
    check(r["toastB"] == "✓ Print Pick Locations complete — 3 orders",
          "`✓ Print Pick Locations complete — 3 orders`", r["toastB"])
    rows = page.evaluate(ROWS_JS)
    check(len(rows) == 5, "the five order rows are still present", len(rows))
    check(sum(1 for x in rows if x["checked"]) == 3, "the three checkboxes are still checked [BR-8]",
          {x["oid"]: x["checked"] for x in rows})


@scenario("QA-M1-12")
def _(page, errors):
    open_m1(page)
    page.click('#m-pick .foot button:has-text("Cancel")')
    check(not page.evaluate("() => document.getElementById('m-pick').classList.contains('open')"),
          "Cancel closes M1", "still open")
    open_m1(page)
    page.click("#m-pick", position={"x": 8, "y": 8})
    check(not page.evaluate("() => document.getElementById('m-pick').classList.contains('open')"),
          "backdrop click closes M1", "still open")
    open_m1(page)
    page.click("#m-pick .x")
    check(not page.evaluate("() => document.getElementById('m-pick').classList.contains('open')"),
          "✕ closes M1", "still open")
    st = page.evaluate("""() => ({w: document.getElementById('pfill').style.width,
      t: document.getElementById('toast').style.display})""")
    check(st["w"] == "" and st["t"] == "none",
          "after all three closes #pfill.style.width is '' and #toast hidden [NE-4]", st)

# ---------------- QA-L3 ----------------

@scenario("QA-L3-01")
def _(page, errors):
    r = run_batch(page, "bpl")
    ret = retained(r["samples"])
    check(len(ret) > 0, "samples exist from the first tick onward", r["samples"])
    check(all("Bulk Print Labels in progress" in s["l"] and "No refresh · selection kept" in s["l"]
              for s in ret), "label contains `Bulk Print Labels in progress` and `No refresh · selection kept`",
          [s["l"] for s in ret])
    check(all("refreshes after completion" not in s["l"] for s in ret),
          "label does not contain `refreshes after completion`", [s["l"] for s in ret])


@scenario("QA-L3-02")
def _(page, errors):
    r = run_batch(page, "bpl")
    check(r["toastB"] == "✓ Bulk Print Labels complete — 3 orders",
          "`✓ Bulk Print Labels complete — 3 orders`", r["toastB"])
    check(r["toastS"] == DEFAULT_SUB, f"`{DEFAULT_SUB}`", r["toastS"])


@scenario("QA-L3-03")
def _(page, errors):
    page.evaluate("() => { window.__sentinel = 'alive'; }")
    check(page.evaluate("() => typeof sndOutbound.ac === 'undefined'"),
          "sndOutbound.ac is undefined before the click", "already defined")
    run_batch(page, "bpl")
    st = page.evaluate("""() => ({sent: window.__sentinel,
      ac: typeof sndOutbound.ac === 'undefined'})""")
    check(st["sent"] == "alive", "the sentinel still exists (the page did not reload)", st)
    check(st["ac"], "sndOutbound.ac is still undefined (no outbound sound) [G-3a]", st)
    rows = page.evaluate(ROWS_JS)
    check(sum(1 for x in rows if x["checked"]) == 3, "the three row checkboxes are still checked [BR-8]",
          {x["oid"]: x["checked"] for x in rows})


@scenario("QA-L3-04")
def _(page, errors):
    lbl = page.evaluate(f"() => {BTN['bpl']}.textContent")
    check("Outbound" not in lbl, "Bulk Print Labels button textContent contains no `Outbound` substring", lbl)


# ---------------- QA-L4 ----------------

@scenario("QA-L4-01")
def _(page, errors):
    r = page.evaluate("""() => {
      const btn = document.querySelectorAll('.bulkbar button')[2];
      const pre = typeof sndOutbound.ac === 'undefined';
      btn.click();
      const AC = window.AudioContext || window.webkitAudioContext;
      let constructible = false;
      if (AC) { try { const t = new AC(); constructible = true; if (t.close) t.close(); } catch (e) {} }
      return {pre, constructible, isInstance: AC ? (sndOutbound.ac instanceof AC) : null};
    }""")
    check(r["pre"], "sndOutbound.ac is undefined on a fresh load", r)
    check(len(errors) == 0, "no uncaught exception is raised", errors)
    if r["constructible"]:
        check(r["isInstance"],
              "sndOutbound.ac is an AudioContext instance constructed inside this click gesture", r)


@scenario("QA-L4-02")
def _(page, errors):
    r = run_batch(page, "bo")
    ret = retained(r["samples"])
    check(len(ret) > 0, "samples exist from the first tick onward", r["samples"])
    check(all("Bulk Outbound in progress" in s["l"] and "refreshes after completion" in s["l"]
              for s in ret), "label contains `Bulk Outbound in progress` and `refreshes after completion`",
          [s["l"] for s in ret])
    check(all("No refresh · selection kept" not in s["l"] for s in ret),
          "label does not contain `No refresh · selection kept`", [s["l"] for s in ret])


@scenario("QA-L4-03")
def _(page, errors):
    r = page.evaluate(TOAST_TIMING_JS, BTN["bo"])
    check(not r.get("timeout"), "toast appears and dismisses", "timing sampler timeout")
    check(r["display"] == "flex", "#toast visible with inline display:flex", r["display"])
    check(r["top"] == "54px" and r["right"] == "16px", "positioned top-right (top:54px; right:16px)",
          {"top": r["top"], "right": r["right"]})
    check(r["b"] == "✓ Bulk Outbound complete — 3 orders",
          "`✓ Bulk Outbound complete — 3 orders`", r["b"])
    check(2800 <= r["dur"] <= 4200,
          "returns to display:none within 3–4 s of becoming visible", f"{r['dur']:.0f} ms")


@scenario("QA-L4-04")
def _(page, errors):
    hits = page.evaluate("""() => [...document.querySelectorAll('button')]
      .filter(b => { const tx = b.textContent || '';
        return /Outbound/.test(tx) && !/Cancel/.test(tx) && !/Outbounded/.test(tx); })
      .map(b => b.textContent.trim())""")
    check(hits == ["📦 Bulk Outbound (3 orders)"],
          "exactly one button qualifies: `📦 Bulk Outbound (3 orders)`", hits)


@scenario("QA-L4-05")
def _(page, errors):
    n = page.evaluate("""() => [...document.querySelectorAll('button')]
      .filter(b => (b.textContent || '').includes('Ready to be Outbonded')).length""")
    check(n == 0, "no element whose text contains `Ready to be Outbonded` is a button", f"{n} buttons")


# ---------------- QA-L5 ----------------

@scenario("QA-L5-01")
def _(page, errors):
    counts = page.evaluate("""() => ({pbar: document.querySelectorAll('.pbar').length,
      pfill: document.querySelectorAll('#pfill, [id="pfill"]').length})""")
    check(counts["pbar"] == 1 and counts["pfill"] == 1,
          "exactly one .pbar and one #pfill", counts)
    for key in ("bpl", None, "bo"):
        if key is None:
            open_m1(page); r = run_batch(page, "m1")
        else:
            r = run_batch(page, key)
        check(r["samples"][-1]["w"] == "100%", "each action animates the same #pfill to 100%",
              r["samples"][-1])


@scenario("QA-L5-02")
def _(page, errors):
    r = run_batch(page, "bpl")
    ws = [int(s["w"][:-1]) for s in r["samples"] if s["w"].endswith("%")]
    check(len(ws) == len(r["samples"]), "every sample has a percentage width", r["samples"])
    check(ws[0] == 0, "the samples begin at `0%`", f"first sample {ws[0]}%")
    check(all(a <= b for a, b in zip(ws, ws[1:])), "never decrease", ws)
    check(ws[-1] == 100, "end at `100%`", f"last sample {ws[-1]}%")


LABEL_RE = re.compile(r"^(Print Pick Locations|Bulk Print Labels|Bulk Outbound) in progress — "
                      r"(\d+)% · (No refresh · selection kept|refreshes after completion) · "
                      r"toast on completion$")
MODE = {"Print Pick Locations": "No refresh · selection kept",
        "Bulk Print Labels": "No refresh · selection kept",
        "Bulk Outbound": "refreshes after completion"}


def _run_three(page):
    """Run BPL, M1 Print, BO on one page; return [(action, retained samples), ...]."""
    out = []
    r = run_batch(page, "bpl"); out.append(("Bulk Print Labels", retained(r["samples"])))
    open_m1(page)
    r = run_batch(page, "m1"); out.append(("Print Pick Locations", retained(r["samples"])))
    r = run_batch(page, "bo"); out.append(("Bulk Outbound", retained(r["samples"])))
    return out


@scenario("QA-L5-03")
def _(page, errors):
    for action, ret in _run_three(page):
        check(len(ret) > 0, "samples exist from the first tick onward", action)
        for s in ret:
            m = LABEL_RE.match(s["l"])
            check(bool(m), "label matches `{Action} in progress — {p}% · {mode} · toast on completion`",
                  s["l"])
            check(m.group(1) == action and m.group(3) == MODE[action],
                  f"action `{action}` renders its own mode string `{MODE[action]}`", s["l"])


@scenario("QA-L5-04")
def _(page, errors):
    for action, ret in _run_three(page):
        if action == "Bulk Outbound":
            bad = [s["l"] for s in ret if "No refresh · selection kept" in s["l"]]
            check(not bad, "a Bulk Outbound run never renders `No refresh · selection kept`", bad)
        else:
            bad = [s["l"] for s in ret if "refreshes after completion" in s["l"]]
            check(not bad, f"a {action} run never renders `refreshes after completion`", bad)


@scenario("QA-L5-05")
def _(page, errors):
    idle = page.evaluate("() => document.getElementById('pbarLabel').childNodes[0].textContent")
    check(idle == IDLE_LABEL, f"idle label equals `{IDLE_LABEL}`", idle)
    for action, ret in _run_three(page):
        bad = [s["l"] for s in ret if "3/5" in s["l"]]
        check(not bad, "the `3/5` fraction appears in no running state", bad)


# ---------------- QA-L6 ----------------

@scenario("QA-L6-01")
def _(page, errors):
    r = page.evaluate(TOAST_TIMING_JS, BTN["bpl"])
    check(not r.get("timeout"), "toast appears and dismisses", "timing sampler timeout")
    check(r["display"] == "flex", "#toast has inline display:flex", r["display"])
    check(r["top"] == "54px" and r["right"] == "16px",
          "anchored top-right (top:54px; right:16px)", {"top": r["top"], "right": r["right"]})
    check(2800 <= r["dur"] <= 4200,
          "returns to display:none within 3–4 s of becoming visible", f"{r['dur']:.0f} ms")


@scenario("QA-L6-02")
def _(page, errors):
    open_m1(page)
    r = run_batch(page, "m1")
    check(r["toastB"] == "✓ Print Pick Locations complete — 3 orders",
          "`✓ Print Pick Locations complete — 3 orders`", r["toastB"])
    wait_toast_hidden(page)
    r = run_batch(page, "bpl")
    check(r["toastB"] == "✓ Bulk Print Labels complete — 3 orders",
          "`✓ Bulk Print Labels complete — 3 orders`", r["toastB"])
    wait_toast_hidden(page)
    r = run_batch(page, "bo")
    check(r["toastB"] == "✓ Bulk Outbound complete — 3 orders",
          "`✓ Bulk Outbound complete — 3 orders`", r["toastB"])


@scenario("QA-L6-03")
def _(page, errors):
    page.evaluate(f"() => {{ {BTN['bpl']}.click(); }}")
    page.wait_for_function("() => document.getElementById('toast').style.display !== 'none'",
                           timeout=6000)
    page.evaluate(f"() => {{ {BTN['bo']}.click(); }}")
    page.wait_for_function(
        "() => document.querySelector('#toast b').textContent.includes('Bulk Outbound')", timeout=6000)
    st = page.evaluate("""() => ({n: document.querySelectorAll('.toast').length,
      b: document.querySelector('#toast b').textContent})""")
    check(st["n"] == 1, "at most one #toast element is visible at any moment (single slot)", st)
    check(st["b"] == "✓ Bulk Outbound complete — 3 orders",
          "its text is the most recent action's [E-18]", st["b"])


@scenario("QA-L6-04")
def _(page, errors):
    st = page.evaluate("""() => {
      const rules = [];
      for (const ss of document.styleSheets) for (const r of ss.cssRules)
        if (r.selectorText && r.selectorText.includes('toast')) rules.push(r.cssText);
      return {n: document.querySelectorAll('.toast').length,
        bg: getComputedStyle(document.getElementById('toast')).backgroundColor,
        redRules: rules.filter(t => t.includes('--red')),
        otherToastEls: [...document.querySelectorAll('*')].filter(e =>
          [...e.classList].some(c => /toast/.test(c)) && e.id !== 'toast').length};
    }""")
    check(st["n"] == 1, "document.querySelectorAll('.toast').length === 1", st["n"])
    check(st["bg"] == "rgb(25, 135, 84)", "toast backgroundColor is rgb(25, 135, 84) (--green #198754)", st["bg"])
    check(st["redRules"] == [], "no toast rule's cssText contains `--red`", st["redRules"])
    check(st["otherToastEls"] == 0, "no element other than #toast carries a class matching /toast/",
          st["otherToastEls"])
    open_m1(page)
    for key in ("m1", "bpl", "bo"):
        r = run_batch(page, key)
        low = (r["toastB"] + " " + r["toastS"]).lower()
        check(all(w not in low for w in ("failed", "error", "partial")),
              "neither #toast b nor #toast small contains failed/error/partial [BR-9]", low)
        wait_toast_hidden(page)


@scenario("QA-L6-05")
def _(page, errors):
    r = run_batch(page, "bpl")
    check(r["toastS"] == DEFAULT_SUB,
          f"#toast small equals `{DEFAULT_SUB}` and never the exclusion subtext", r["toastS"])

# ---------------- QA-L7 ----------------

@scenario("QA-L7-01")
def _(page, errors):
    t = page.evaluate("""() => { const r = [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .find(r => r.querySelector('.oid').textContent === '422164');
      const b = r.querySelector('.jit-badge'); return b ? b.textContent : null; }""")
    check(t == "Fully Inbounded", "row 422164 has a .jit-badge whose textContent equals `Fully Inbounded`", t)


@scenario("QA-L7-02")
def _(page, errors):
    st = page.evaluate("""() => ({mock: document.querySelector('.mock').textContent.includes('JIT (channel) completed'),
      m1: document.querySelector('#m-pick').textContent.includes('JIT (channel) completed')})""")
    check(not st["mock"] and not st["m1"],
          "`.mock` and `#m-pick` contain no occurrence of `JIT (channel) completed` [BR-4] "
          "(.legend/.wf-bar exempt and not scanned)", st)


@scenario("QA-L7-03")
def _(page, errors):
    rows = [r["oid"] for r in page.evaluate(ROWS_JS)]
    has_cls = page.evaluate("""() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .find(r => r.querySelector('.oid').textContent === '422164').classList.contains('row-jit')""")
    check(has_cls, "the 422164 row carries class row-jit", "class missing")
    check(rows[-1] == "422164" and rows[-2] == "MKT-40233",
          "in view All it is the last order row, after MKT-40233 [BR-2]", rows)


# ---------------- QA-L8 ----------------

def _mkt_row_js(expr):
    return ("() => { const r = [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]"
            ".find(r => r.querySelector('.oid').textContent === 'MKT-40233'); return " + expr + "; }")


@scenario("QA-L8-01")
def _(page, errors):
    st = page.evaluate(_mkt_row_js("({cls: r.classList.contains('row-mkt'), "
                                   "badge: r.querySelector('.mkt-badge') ? r.querySelector('.mkt-badge').textContent : null})"))
    check(st["cls"] and st["badge"] == "MKT",
          "MKT-40233 row carries class row-mkt and a .mkt-badge with textContent `MKT`", st)


@scenario("QA-L8-02")
def _(page, errors):
    st = page.evaluate(_mkt_row_js("({cust: r.children[3].textContent, "
                                   "pic: r.children[3].querySelector('div') ? r.children[3].querySelector('div').textContent : null})"))
    check("Influencer @glowwithjade" in st["cust"], "Customer cell contains `Influencer @glowwithjade`", st)
    check(st["pic"] == "PIC: Harshit", "second line reading exactly `PIC: Harshit`", st)


@scenario("QA-L8-03")
def _(page, errors):
    st = page.evaluate(_mkt_row_js("""(() => {
      const pills = [...r.children[6].querySelectorAll('.locpill')];
      const cs = pills.length > 1 ? getComputedStyle(pills[1]) : null;
      return {n: pills.length, first: pills[0] && pills[0].textContent,
        second: pills[1] && pills[1].textContent,
        bg: cs && cs.backgroundColor, border: cs && cs.borderTopColor, color: cs && cs.color};
    })()"""))
    check(st["n"] == 2, "the Pick Locations cell contains two .locpill elements", st)
    check(st["first"] == "A-01-04", "the first reads `A-01-04`", st)
    check(st["second"] == "Not inbounded", "the second reads `Not inbounded`", st)
    check(st["bg"] == "rgb(255, 243, 224)" and st["border"] == "rgb(253, 186, 116)"
          and st["color"] == "rgb(180, 83, 9)",
          "styled amber (background --amber-soft, border --amber-line, colour --amber) [BR-23]", st)


@scenario("QA-L8-04")
def _(page, errors):
    rows = [r["oid"] for r in page.evaluate(ROWS_JS)]
    exp = ["422221", "422176", "422165", "MKT-40233", "422164"]
    check(rows == exp, f"order-row sequence {exp} [BR-2]", rows)


# ---------------- QA-L9 ----------------

@scenario("QA-L9-01")
def _(page, errors):
    pre = page.evaluate("() => document.getElementById('crow1').style.display")
    check(pre == "none", "#crow1 starts display:none", pre)
    page.click('.cmtbtn[data-open="crow1"]')
    st = page.evaluate("""() => ({disp: document.getElementById('crow1').style.display,
      prevOid: document.getElementById('crow1').previousElementSibling.querySelector('.oid').textContent})""")
    check(st["disp"] == "table-row", "#crow1 changes to display:table-row", st)
    check(st["prevOid"] == "422221", "it is the row immediately below the 422221 row", st)


@scenario("QA-L9-02")
def _(page, errors):
    page.click('.cmtbtn[data-open="crow1"]')
    st = page.evaluate("""() => { const c = document.getElementById('crow1');
      return {who: c.querySelector('.who').textContent, at: c.querySelector('.at').textContent,
        text: c.querySelector('.c-item span:nth-child(2)').textContent,
        time: c.querySelector('time').textContent}; }""")
    check(st["who"] == "Egita", "contains `Egita`", st)
    check(st["at"] == "@Yongwon", "an .at element reading `@Yongwon`", st)
    check("Please double-check the ×5 quantity." in st["text"],
          "the text `Please double-check the ×5 quantity.` with the trailing period ([RTO-WFX-8])", st)
    check(st["time"] == "07-21 09:40", "a time element reading `07-21 09:40`", st)


@scenario("QA-L9-03")
def _(page, errors):
    st = page.evaluate("""() => ({p1: document.querySelector('#crow1 input').placeholder,
      p2: document.querySelector('#crow2 input').placeholder})""")
    exp1 = "Write a comment — @mention sends an automatic Slack notification (order no. · text · time · author)"
    exp2 = "Write a comment — @mention sends an automatic Slack notification"
    check(st["p1"] == exp1, f"#crow1 input placeholder equals `{exp1}`", st["p1"])
    check(st["p2"] == exp2, f"#crow2 input placeholder equals `{exp2}`", st["p2"])


@scenario("QA-L9-04")
def _(page, errors):
    page.click('.cmtbtn[data-open="crow2"]')
    st = page.evaluate("""() => { const c = document.getElementById('crow2');
      return {disp: c.style.display, empty: c.querySelector('.c-item').textContent.trim(),
        hasInput: !!c.querySelector('input'),
        post: c.querySelector('button') ? c.querySelector('button').textContent : null}; }""")
    check(st["disp"] == "table-row", "#crow2 shows", st)
    check(st["empty"] == "No comments yet", "`No comments yet` in muted text", st["empty"])
    check(st["hasInput"] and st["post"] == "Post", "still offers the write row with a Post button", st)


@scenario("QA-L9-05")
def _(page, errors):
    st = page.evaluate("""() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .map(r => ({oid: r.querySelector('.oid').textContent,
        badge: r.querySelector('.cmtbtn .badge-n') ? r.querySelector('.cmtbtn .badge-n').textContent : null}))""")
    got = {r["oid"]: r["badge"] for r in st}
    exp = {"422221": "1", "422165": "1", "422176": None, "MKT-40233": None, "422164": None}
    check(got == exp, "`.cmtbtn` badges: 422221 and 422165 each `1`; 422176/MKT-40233/422164 none", got)


@scenario("QA-L9-06")
def _(page, errors):
    st = page.evaluate("""() => ({c4prev: document.getElementById('crow4').previousElementSibling
        .querySelector('.oid').textContent,
      c5prev: document.getElementById('crow5').previousElementSibling.querySelector('.oid').textContent})""")
    check(st["c4prev"] == "422164", "#crow4 belongs to the JIT row 422164", st)
    check(st["c5prev"] == "MKT-40233", "#crow5 belongs to the MKT row MKT-40233", st)
    page.click('.cmtbtn[data-open="crow5"]')
    st2 = page.evaluate("""() => ({c5: document.getElementById('crow5').style.display,
      c4: document.getElementById('crow4').style.display})""")
    check(st2["c5"] == "table-row" and st2["c4"] == "none",
          "clicking .cmtbtn[data-open=crow5] opens the panel under the MKT row, not the JIT row "
          "([RTO-WFX-8])", st2)


# ---------------- QA-L10 ----------------

def open_hub(page):
    page.click('.icon-btn[data-open="inbox1"]')
    check(page.evaluate("() => document.getElementById('inbox1').classList.contains('open')"),
          "#inbox1 gains class open", "hub did not open")


@scenario("QA-L10-01")
def _(page, errors):
    open_hub(page)
    badge = page.evaluate("() => document.querySelector('.icon-btn[data-open=\"inbox1\"] .badge-n').textContent")
    check(badge == "2", "the button's .badge-n reads `2`", badge)


@scenario("QA-L10-02")
def _(page, errors):
    open_hub(page)
    st = page.evaluate("""() => { const p = document.querySelector('#inbox1 [data-pane="mentions"]');
      return {header: p.querySelector('.paneheader').textContent,
        items: [...p.querySelectorAll('.it.unread')].map(it => ({
          body: it.querySelector('.body').textContent.replace(/\\s+/g, ' ').trim(),
          time: it.querySelector('time').textContent}))}; }""")
    check(len(st["items"]) == 2, "exactly 2 .it.unread entries", st["items"])
    check(st["items"][0]["body"].startswith('Order 422165 · Dean: "@Yongwon Please take extra care packing this order"')
          and st["items"][0]["time"] == "10:12",
          '`Order 422165 · Dean: "@Yongwon Please take extra care packing this order"` at 10:12', st["items"][0])
    check(st["items"][1]["body"].startswith('Order 422221 · Egita: "@Yongwon Please double-check the ×5 quantity"')
          and st["items"][1]["time"] == "09:40",
          '`Order 422221 · Egita: "@Yongwon Please double-check the ×5 quantity"` at 09:40', st["items"][1])
    check("Comments mentioning me · Click to open the order" in st["header"]
          and "Mark all read" in st["header"],
          "pane header `Comments mentioning me · Click to open the order` with `Mark all read`", st["header"])


@scenario("QA-L10-03")
def _(page, errors):
    open_hub(page)
    page.click('#inbox1 .tabs button[data-tab="saved"]')
    st = page.evaluate("""() => ({mDisp: document.querySelector('#inbox1 [data-pane="mentions"]').style.display,
      sDisp: document.querySelector('#inbox1 [data-pane="saved"]').style.display,
      items: [...document.querySelectorAll('#inbox1 [data-pane="saved"] .it')].map(it =>
        it.querySelector('.body').textContent.replace(/\\s+/g, ' ').trim()),
      header: document.querySelector('#inbox1 [data-pane="saved"] .paneheader').textContent})""")
    check(st["mDisp"] == "none", "the mentions pane hides", st)
    check(st["sDisp"] == "block", "the saved pane shows", st)
    check(len(st["items"]) == 1 and st["items"][0].startswith("Order 422221 · Egita"),
          "exactly 1 entry (Order 422221 · Egita)", st["items"])
    check("Saved comments · Click to open the order" in st["header"]
          and "Unstar to remove from the list" in st["header"],
          "header `Saved comments · Click to open the order` with `Unstar to remove from the list`",
          st["header"])


@scenario("QA-L10-04")
def _(page, errors):
    open_hub(page)
    star = page.locator('#inbox1 [data-pane="mentions"] .it').first.locator(".star")
    check(not page.evaluate("""() => document.querySelector('#inbox1 [data-pane="mentions"] .it .star')
      .classList.contains('on')"""), "the first mentions entry star starts unfilled", "already on")
    star.click()
    on1 = page.evaluate("""() => document.querySelector('#inbox1 [data-pane="mentions"] .it .star')
      .classList.contains('on')""")
    t1 = page.evaluate("() => document.getElementById('toast').style.display")
    star.click()
    on2 = page.evaluate("""() => document.querySelector('#inbox1 [data-pane="mentions"] .it .star')
      .classList.contains('on')""")
    t2 = page.evaluate("() => document.getElementById('toast').style.display")
    check(on1, "it gains class on", on1)
    check(not on2, "clicking again removes it", on2)
    check(t1 == "none" and t2 == "none", "no toast is shown at any point [BR-34]", (t1, t2))


CSR_JS = """() => { const pane = document.querySelector('#inbox1 [data-pane="csr"]');
  return {tabsDisp: getComputedStyle(document.querySelector('#inbox1 .tabs')).display,
    paneDisp: pane ? pane.style.display : null,
    header: pane ? pane.querySelector('.paneheader').textContent : null,
    empty: pane && pane.querySelector('.empty') ? pane.querySelector('.empty').textContent : null,
    items: pane ? [...pane.querySelectorAll('.it')].map(it => ({
      b: it.querySelector('b') ? it.querySelector('b').textContent : null,
      time: it.querySelector('time') ? it.querySelector('time').textContent : null,
      marks: [...it.querySelectorAll('mark')].map(m => m.textContent)})) : []}; }"""


@scenario("QA-L10-05")
def _(page, errors):
    open_hub(page)
    page.fill('#inbox1 .csearch input', "422")
    st = page.evaluate(CSR_JS)
    check(st["tabsDisp"] == "none", ".tabs is hidden (display:none)", st["tabsDisp"])
    check(st["header"] == "4 results · newest first · click to open the order",
          "header `4 results · newest first · click to open the order`", st["header"])
    got = [(i["b"], i["time"]) for i in st["items"]]
    exp = [("Order 422165", "Today 10:12"), ("Order 422221", "Today 09:40"),
           ("Order 422176", "Today 08:52"), ("Order 422108", "Yesterday 16:45")]
    check(got == exp, f"results ordered {exp}", got)
    check(all(any(m == "422" for m in i["marks"]) for i in st["items"]),
          "each matched substring is wrapped in <mark>", [i["marks"] for i in st["items"]])


@scenario("QA-L10-06")
def _(page, errors):
    open_hub(page)
    page.fill('#inbox1 .csearch input', "Aldo")
    st = page.evaluate(CSR_JS)
    check(len(st["items"]) == 1 and st["items"][0]["b"] == "Order 421990",
          "exactly 1 result renders, for Order 421990 — not a row in this table [E-38]", st["items"])


@scenario("QA-L10-07")
def _(page, errors):
    open_hub(page)
    page.fill('#inbox1 .csearch input', "zzzz")
    st = page.evaluate(CSR_JS)
    check(st["header"] == "0 results · newest first · click to open the order",
          "header `0 results · newest first · click to open the order`", st["header"])
    check(st["empty"] == "No matching comments", "body shows `No matching comments`", st["empty"])


@scenario("QA-L10-08")
def _(page, errors):
    open_hub(page)
    page.click('#inbox1 .tabs button[data-tab="saved"]')
    page.fill('#inbox1 .csearch input', "422")
    check(page.evaluate("() => getComputedStyle(document.querySelector('#inbox1 .tabs')).display") == "none",
          "tabs hidden while searching", "tabs visible")
    page.fill('#inbox1 .csearch input', "")
    st = page.evaluate("""() => ({tabsDisp: getComputedStyle(document.querySelector('#inbox1 .tabs')).display,
      saved: document.querySelector('#inbox1 [data-pane="saved"]').style.display,
      mentions: document.querySelector('#inbox1 [data-pane="mentions"]').style.display})""")
    check(st["tabsDisp"] == "flex", ".tabs is visible again", st)
    check(st["saved"] == "block" and st["mentions"] == "none",
          "the Saved pane is the one displayed, not Mentions", st)


@scenario("QA-L10-09")
def _(page, errors):
    open_hub(page)
    page.click('#inbox1 .csearch input')
    check(page.evaluate("() => document.getElementById('inbox1').classList.contains('open')"),
          "the hub stays open for the inside click", "closed on inside click")
    page.click(".ptitle h2")
    check(not page.evaluate("() => document.getElementById('inbox1').classList.contains('open')"),
          "loses class open for the outside click", "still open")


@scenario("QA-L10-10")
def _(page, errors):
    open_hub(page)
    page.fill('#inbox1 .csearch input', "4")
    st = page.evaluate(CSR_JS)
    orders = [i["b"] for i in st["items"]]
    check(len(st["items"]) == 5, "5 results render", orders)
    check("Order 422108" in orders and "Order 421990" in orders,
          "including 422108 and 421990, neither of which is a table row [E-38]", orders)

# ---------------- QA-L11 ----------------

@scenario("QA-L11-01")
def _(page, errors):
    pad = page.evaluate("() => getComputedStyle(document.querySelector('.pagepad')).padding")
    check(pad == "16px 14px 0px", "computed padding of .pagepad equals `16px 14px 0px`", pad)


@scenario("QA-L11-02")
def _(page, errors):
    st = page.evaluate("""() => ({ox: getComputedStyle(document.querySelector('.mockwrap')).overflowX,
      mw: getComputedStyle(document.querySelector('.mock')).minWidth})""")
    check(st["ox"] == "auto", ".mockwrap has overflow-x: auto", st)
    check(st["mw"] == "1240px", ".mock has min-width: 1240px", st)
    page.set_viewport_size({"width": 900, "height": 700})
    sc = page.evaluate("""() => { const w = document.querySelector('.mockwrap');
      return {scroll: w.scrollWidth, client: w.clientWidth}; }""")
    check(sc["scroll"] > sc["client"],
          "narrowing the viewport produces a horizontal scrollbar rather than dropped/wrapped columns", sc)


# ---------------- QA-L12 ----------------

@scenario("QA-L12-01")
def _(page, errors):
    ths = page.evaluate("() => [...document.querySelectorAll('.tbl thead th')].map(t => t.textContent)")
    check(ths[6].startswith("Pick Locations"), "the 7th th starts with `Pick Locations`", ths)
    check(ths[5].startswith("Ready Item Details"), "positioned immediately after `Ready Item Details`", ths)


@scenario("QA-L12-02")
def _(page, errors):
    st = page.evaluate("""() => { const r = [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .find(r => r.querySelector('.oid').textContent === '422165');
      return {items: r.children[5].querySelectorAll('.item-line').length,
        locs: [...r.children[6].querySelectorAll('.locline .locpill')].map(p => p.textContent)}; }""")
    check(st["items"] == 2, "Ready Item Details cell contains 2 .item-line elements", st)
    check(st["locs"] == ["A-03-02", "B-02-11"],
          "the first locator is A-03-02 and the second is B-02-11 (line-for-line pairing)", st["locs"])


@scenario("QA-L12-03")
def _(page, errors):
    st = page.evaluate("""() => { const r = [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .find(r => r.querySelector('.oid').textContent === '422164');
      return [...r.children[6].querySelectorAll('.locpill')].map(p => p.textContent); }""")
    check(st == ["Shelf 3"], "row 422164's Pick Locations cell contains a single .locpill reading `Shelf 3`", st)


@scenario("QA-L12-04")
def _(page, errors):
    st = page.evaluate("""() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .map(r => ({oid: r.querySelector('.oid').textContent,
        cellText: r.children[6].textContent.trim(),
        loclines: [...r.children[6].querySelectorAll('.locline')].map(l =>
          l.querySelector('.locpill') ? l.querySelector('.locpill').textContent.trim() : '')}))""")
    for r in st:
        check(r["cellText"] != "", f"Pick Locations cell of {r['oid']} is not whitespace [BR-23]", st)
        check(all(p != "" for p in r["loclines"]),
              f"every .locline of {r['oid']} contains a non-empty .locpill", st)


# ---------------- QA-L13 ----------------

@scenario("QA-L13-01")
def _(page, errors):
    got = page.evaluate("""() => Object.fromEntries([...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .map(r => [r.querySelector('.oid').textContent, r.querySelector('.cb-total').textContent]))""")
    check(got["422221"] == "5", "row 422221 Total Items reads `5` (one SKU × 5 units) [BR-5]", got)
    check(got["422176"] == "1", "row 422176 reads `1`", got)
    check(got["422165"] == "2", "row 422165 reads `2` (two SKUs × 1 unit each)", got)


@scenario("QA-L13-02")
def _(page, errors):
    got = page.evaluate("""() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .find(r => r.querySelector('.oid').textContent === 'MKT-40233').querySelector('.cb-total').textContent""")
    check(got == "3", "row MKT-40233 reads `3` even though only 2 of its 3 units are inbounded [BR-16]", got)


@scenario("QA-L13-03")
def _(page, errors):
    st = page.evaluate("""() => ({ths: document.querySelectorAll('.tbl thead th').length,
      cbReady: document.querySelectorAll('.cb-ready').length})""")
    check(st["ths"] == 9, "document.querySelectorAll('.tbl thead th').length is exactly 9", st)
    check(st["cbReady"] == 0, "no element in the document uses the class cb-ready ([RTO-WFX-4])", st)


# ---------------- QA-L14 ----------------

def visible_oids(page):
    return [r["oid"] for r in page.evaluate(ROWS_JS) if r["visible"]]


@scenario("QA-L14-01")
def _(page, errors):
    st = page.evaluate("""() => ({on: document.querySelector('.vtab.on').dataset.view,
      labels: [...document.querySelectorAll('.vtab')].map(t => t.textContent.trim())})""")
    check(st["on"] == "all", "`.vtab[data-view=all]` has class on", st)
    exp = ["All (5)", "Inventory (3)", "Marketing (1)", "JIT (1)"]
    check(st["labels"] == exp, f"tab labels read {exp} (3+1+1=5)", st["labels"])


@scenario("QA-L14-02")
def _(page, errors):
    page.click('.vtab[data-view="inv"]')
    got = visible_oids(page)
    check(got == ["422221", "422176", "422165"], "exactly rows 422221, 422176, 422165 visible", got)
    ft = page.text_content("#foundTxt")
    check(ft == "Found 3 order(s) with items ready for outbound",
          "`Found 3 order(s) with items ready for outbound`", ft)


@scenario("QA-L14-03")
def _(page, errors):
    page.click('.vtab[data-view="mkt"]')
    got = visible_oids(page)
    check(got == ["MKT-40233"], "exactly MKT-40233 visible", got)
    ft = page.text_content("#foundTxt")
    check(ft == "Found 1 order(s) with items ready for outbound",
          "`Found 1 order(s) with items ready for outbound`", ft)


@scenario("QA-L14-04")
def _(page, errors):
    page.click('.vtab[data-view="jit"]')
    got = visible_oids(page)
    check(got == ["422164"], "exactly 422164 visible", got)
    st = page.evaluate("""() => { const r = [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .find(r => r.querySelector('.oid').textContent === '422164');
      return {badge: r.querySelector('.jit-badge').textContent, cls: r.classList.contains('row-jit'),
        pick: r.children[6].textContent.trim()}; }""")
    check(st["badge"] == "Fully Inbounded" and st["cls"], "shows the Fully Inbounded badge, carries row-jit", st)
    check(st["pick"] == "Shelf 3", "its Pick Locations cell reads `Shelf 3`", st)
    ft = page.text_content("#foundTxt")
    check(ft == "Found 1 order(s) with items ready for outbound",
          "`Found 1 order(s) with items ready for outbound`", ft)


@scenario("QA-L14-05")
def _(page, errors):
    page.click('.cmtbtn[data-open="crow1"]')
    check(page.evaluate("() => document.getElementById('crow1').style.display") == "table-row",
          "#crow1 expanded", "not expanded")
    page.click('.vtab[data-view="jit"]')
    d1 = page.evaluate("() => document.getElementById('crow1').style.display")
    check(d1 == "none", "#crow1 is display:none after the first switch [E-17]", d1)
    page.click('.vtab[data-view="all"]')
    d2 = page.evaluate("() => document.getElementById('crow1').style.display")
    check(d2 == "none", "#crow1 remains hidden after returning to All", d2)
    got = visible_oids(page)
    check(len(got) == 5, "all 5 order rows are visible", got)
    ft = page.text_content("#foundTxt")
    check(ft == "Found 5 order(s) with items ready for outbound",
          "`Found 5 order(s) with items ready for outbound`", ft)


@scenario("QA-L14-06")
def _(page, errors):
    for v in ("inv", "mkt", "jit", "all"):
        page.click(f'.vtab[data-view="{v}"]')
        n = page.evaluate("() => document.querySelectorAll('.vtab.on').length")
        check(n == 1, "after each click exactly one .vtab carries class on", f"{n} after {v}")
    got = visible_oids(page)
    check(len(got) == 5, "the final state shows all 5 order rows", got)


@scenario("QA-L14-07")
def _(page, errors):
    page.click('.vtab[data-view="mkt"]')
    ft = page.text_content("#foundTxt")
    check(ft == "Found 1 order(s) with items ready for outbound",
          "the literal `order(s)` form is preserved even when the count is 1 [BR-35]", ft)


# ---------------- QA-F ----------------

@scenario("QA-F-01")
def _(page, errors):
    st = page.evaluate("""() => ({h2: document.querySelector('.ptitle h2').textContent,
      h3: document.querySelector('.psub h3').textContent})""")
    check(st["h2"] == "WMS - Ready to be Outbonded", "`.ptitle h2` equals `WMS - Ready to be Outbonded`", st)
    check(st["h3"] == "Ready to be Outbonded Orders", "`.psub h3` equals `Ready to be Outbonded Orders`", st)
    check("Outbounded" not in st["h2"] and "Outbounded" not in st["h3"],
          "the string `Outbounded` must not appear in either element", st)


@scenario("QA-F-02")
def _(page, errors):
    t = page.evaluate("""() => { const b = document.querySelector('.psub button.btn.btn-blue');
      return b ? b.textContent : null; }""")
    check(t == "Refresh", "a button.btn.btn-blue with textContent `Refresh` in the .psub heading row", t)


@scenario("QA-F-03")
def _(page, errors):
    ft = page.text_content("#foundTxt")
    check(ft == "Found 5 order(s) with items ready for outbound",
          "`Found 5 order(s) with items ready for outbound` on load", ft)


@scenario("QA-F-04")
def _(page, errors):
    st = page.evaluate("""() => ({b: document.querySelector('.howto b').textContent,
      lis: [...document.querySelectorAll('.howto li')].map(li => li.textContent)})""")
    check(st["b"] == "How to use:", "a bold `How to use:`", st["b"])
    exp = ["Click \"Refresh\" to load the latest orders ready for outbound",
           "Orders shown here have at least one line item with \"INBOUNDED\" status",
           "Click the Order ID link to see full order details and process outbound",
           "Only items marked as INBOUNDED are ready for outbound processing",
           "This page uses the dedicated readyToBeOutbonded API for optimized results"]
    check(st["lis"] == exp, f"exactly 5 li elements: {exp}", st["lis"])


@scenario("QA-F-05")
def _(page, errors):
    st = page.evaluate("""() => ({ths: [...document.querySelectorAll('.tbl thead th')].map(t => t.textContent),
      firstHasCb: !!document.querySelector('.tbl thead th input[type=checkbox]'),
      rows: document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)').length,
      printbtns: document.querySelectorAll('.printbtn').length})""")
    check(len(st["ths"]) == 9, "9 thead th elements", st["ths"])
    check(st["firstHasCb"] and st["ths"][0] == "", "the first contains a checkbox and has empty textContent", st)
    starts = ["Order ID", "Order Date", "Customer", "Total Items", "Ready Item Details",
              "Pick Locations", "Comments", "Print"]
    for i, s in enumerate(starts):
        check(st["ths"][i + 1].startswith(s), f"th {i+2} starts with `{s}`", st["ths"])
    check(st["rows"] == 5 and st["printbtns"] == 5, "exactly 5 order rows and 5 .printbtn buttons", st)


@scenario("QA-F-06")
def _(page, errors):
    st = page.evaluate("""() => ({viewOrder: [...document.querySelectorAll('*')]
        .filter(e => e.textContent === 'View Order').length,
      nonPrint: [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
        .flatMap(r => [...r.children[8].querySelectorAll('*')])
        .filter(e => !e.classList.contains('printbtn')).length})""")
    check(st["viewOrder"] == 0,
          "no element's textContent === 'View Order' (strict equality) [BR-12]", st)
    check(st["nonPrint"] == 0, "every element inside each row's Print cell carries class printbtn", st)


@scenario("QA-F-07")
def _(page, errors):
    dates = page.evaluate("""() => [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .map(r => r.children[2].textContent)""")
    check(all(d == "2026. 7. 21." for d in dates),
          "every order row's third cell textContent equals `2026. 7. 21.` [E-72]", dates)


@scenario("QA-F-08")
def _(page, errors):
    st = page.evaluate("""() => ({ns: [...document.querySelectorAll('.legend ol > li .n')].map(n => n.textContent),
      liCount: document.querySelectorAll('.legend ol > li').length,
      dots: document.querySelectorAll('.dot').length,
      mockDots: document.querySelectorAll('.mock .dot').length,
      m1Dots: document.querySelectorAll('#m-pick .dot').length})""")
    check(st["liCount"] == 14, "14 legend li elements", st)
    exp = ["1", "2", "3", "4", "5", "6", "7", "8", "14", "13", "12", "9", "10", "11"]
    check(st["ns"] == exp, f"legend .n texts in document order {exp}", st["ns"])
    check(st["dots"] == 15 and st["mockDots"] == 14 and st["m1Dots"] == 1,
          "15 .dot elements — 14 inside .mock plus the M1 dot inside #m-pick", st)


@scenario("QA-F-09")
def _(page, errors):
    page.click("#annoToggle")
    st = page.evaluate("""() => ({noAnno: document.body.classList.contains('no-anno'),
      dotsHidden: [...document.querySelectorAll('.dot')].every(d => getComputedStyle(d).display === 'none'),
      legendHidden: getComputedStyle(document.querySelector('.legend')).display === 'none',
      btn: document.getElementById('annoToggle').textContent})""")
    check(st["noAnno"], "document.body gains class no-anno", st)
    check(st["dotsHidden"] and st["legendHidden"], "every .dot and the .legend compute to display:none", st)
    check(st["btn"] == "Show annotations", "the button textContent becomes `Show annotations`", st["btn"])
    page.click("#annoToggle")
    st2 = page.evaluate("""() => ({noAnno: document.body.classList.contains('no-anno'),
      dotsShown: [...document.querySelectorAll('.dot')].some(d => getComputedStyle(d).display !== 'none'),
      btn: document.getElementById('annoToggle').textContent})""")
    check(not st2["noAnno"] and st2["dotsShown"] and st2["btn"] == "Hide annotations",
          "clicking again restores all of it", st2)


@scenario("QA-F-11")
def _(page, errors):
    st = page.evaluate("""() => [...document.querySelectorAll('.oid')].map(e => ({
      tag: e.tagName, href: e.hasAttribute('href'), inA: !!e.closest('a'), text: e.textContent}))""")
    check(len(st) == 5, "exactly 5 .oid elements", st)
    check(all(e["tag"] == "SPAN" and not e["href"] and not e["inA"] for e in st),
          ".oid elements are SPAN nodes with no href and no ancestor <a> ([RTO-WFX-3])", st)
    check([e["text"] for e in st] == ["422221", "422176", "422165", "MKT-40233", "422164"],
          "reading 422221, 422176, 422165, MKT-40233, 422164", [e["text"] for e in st])

# ---------------- QA-E (the six [WF] rows) ----------------

@scenario("QA-E-01")
def _(page, errors):
    page.evaluate("() => document.querySelector('tr[data-view=\"mkt\"]:not(.crow)').remove()")
    page.click('.vtab[data-view="mkt"]')
    check(len(errors) == 0, "no exception is thrown", errors)
    got = visible_oids(page)
    check(got == [], "the tbody shows no order row", got)
    ft = page.text_content("#foundTxt")
    check(ft == "Found 0 order(s) with items ready for outbound",
          "`Found 0 order(s) with items ready for outbound`", ft)


@scenario("QA-E-02")
def _(page, errors):
    page.evaluate("""() => { window.AudioContext = function(){ throw new Error('blocked'); };
      window.webkitAudioContext = window.AudioContext; }""")
    r = run_batch(page, "bo")
    check(len(errors) == 0, "no uncaught exception reaches the console", errors)
    check(r["samples"][-1]["w"] == "100%", "#pfill.style.width still reaches 100%", r["samples"][-1])
    check(r["toastB"] == "✓ Bulk Outbound complete — 3 orders",
          "#toast b still reads `✓ Bulk Outbound complete — 3 orders` — audio never gates the action",
          r["toastB"])


@scenario("QA-E-03")
def _(page, errors):
    st = page.evaluate("""() => ({ws: getComputedStyle(document.querySelector('.item-line')).whiteSpace,
      lastIsQty: [...document.querySelectorAll('.tbl .item-line')].every(l =>
        l.lastElementChild && l.lastElementChild.classList.contains('qtypill'))})""")
    check(st["ws"] == "nowrap", "computed whiteSpace of .item-line equals `nowrap`", st)
    check(st["lastIsQty"], "the row's ×qty pill remains the last element of its line", st)


@scenario("QA-E-04")
def _(page, errors):
    st = page.evaluate("""() => ({ox: getComputedStyle(document.querySelector('.mockwrap')).overflowX,
      mw: getComputedStyle(document.querySelector('.mock')).minWidth})""")
    check(st["ox"] == "auto" and st["mw"] == "1240px",
          ".mockwrap computes overflow-x: auto and .mock computes min-width: 1240px", st)
    page.set_viewport_size({"width": 800, "height": 600})
    sc = page.evaluate("""() => { const w = document.querySelector('.mockwrap');
      return {scrolls: w.scrollWidth > w.clientWidth,
        ths: document.querySelectorAll('.tbl thead th').length}; }""")
    check(sc["scrolls"], "narrowing the window produces horizontal scrolling", sc)
    check(sc["ths"] == 9, "`.tbl thead th` count remains 9 (qualified selector)", sc)


@scenario("QA-E-05")
def _(page, errors):
    page.evaluate("""() => { window.__samples = [];
      const fill = document.getElementById('pfill');
      window.__iv = setInterval(() => { window.__samples.push(fill.style.width); }, 50); }""")
    page.focus('.bulkbar button:has-text("Bulk Outbound")')
    page.keyboard.press("Enter")
    page.wait_for_function("() => document.getElementById('pfill').style.width === '100%'", timeout=6000)
    page.evaluate("""() => { clearInterval(window.__iv);
      window.__samples.push(document.getElementById('pfill').style.width); }""")
    ws = [int(w[:-1]) for w in page.evaluate("() => window.__samples") if w.endswith("%")]
    check(len(ws) > 0 and all(a <= b for a, b in zip(ws, ws[1:])) and ws[-1] == 100,
          "exactly one progress run occurs (single monotonic 0→100 ascent)", ws)
    tb = page.evaluate("() => document.querySelector('#toast b').textContent")
    check(tb == "✓ Bulk Outbound complete — 3 orders",
          "exactly one toast appears — identical to a mouse click", tb)


@scenario("QA-E-06")
def _(page, errors):
    st = page.evaluate("""() => { const r = [...document.querySelectorAll('.tbl tbody tr[data-view]:not(.crow)')]
      .find(r => r.querySelector('.oid').textContent === '422165');
      return {skus: [...r.querySelectorAll('.item-line .skupill')].map(s => s.textContent),
        loclines: r.children[6].querySelectorAll('.locline').length}; }""")
    check(st["skus"] == ["100039420", "100013286"],
          "row 422165's two item lines (100039420, 100013286) render as two separate .item-line elements",
          st)
    check(st["loclines"] == 2, "with two separate .locline locators", st)
    m1 = page.evaluate(M1_ROWS_JS)
    m1_165 = [r["sku"] for r in m1 if r["order"] == "422165" and r["pill"] is None]
    check(sorted(m1_165) == ["100013286", "100039420"],
          "M1 renders them as two separate rows — the page never merges lines it did not create", m1_165)


# ---------------- harness ----------------

def main():
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        errors = []
        page.on("pageerror", lambda e: errors.append(str(e)))
        for sid, fn in SCN:
            errors.clear()
            page.set_viewport_size({"width": 1280, "height": 720})
            page.goto(WF_URL)
            try:
                fn(page, errors)
                results.append({"id": sid, "status": "pass"})
            except Fail as f:
                results.append({"id": sid, "status": "fail", "expected": f.expected, "actual": f.actual})
            except Exception as e:  # runner bug, not a spec verdict
                results.append({"id": sid, "status": "error", "detail": repr(e)})
        browser.close()
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = [r for r in results if r["status"] == "fail"]
    errored = [r for r in results if r["status"] == "error"]
    # HANDOFF.md §4 documents `python3 qa-<screen>.py [--json out.json]` for all eight
    # runners. Without this the flag is accepted, nothing is written, and the run still
    # exits 0 — a pass rate with no artefact behind it.
    if "--json" in sys.argv:
        _out = sys.argv[sys.argv.index("--json") + 1]
        _p = pathlib.Path(_out)
        _p.parent.mkdir(parents=True, exist_ok=True)
        with open(_p, "w", encoding="utf-8") as _f:
            json.dump({"executed": len(results), "passed": passed,
                       "failed": failed, "runner_errors": errored}, _f, ensure_ascii=False, indent=1)
        print("wrote", _p)
    print(json.dumps({"executed": len(results), "passed": passed,
                      "failed": failed, "runner_errors": errored}, ensure_ascii=False, indent=1))
    return 0 if not failed and not errored else 1


if __name__ == "__main__":
    sys.exit(main())
