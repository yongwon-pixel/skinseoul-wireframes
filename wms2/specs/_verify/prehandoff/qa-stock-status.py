#!/usr/bin/env python3
"""
Pre-handoff QA — wms2/specs/stock-status.md §8, all 90 [WF]-tier scenarios.

Executed against the local wireframe file.

Manual stock adjustment 2026-08-08 ([L-19] / [L-20], owner decision of the same date). The
screen gained a `✎` on every Current Stocks `Total` cell and a source trail inside every
`ADJUST` Type cell, so this runner gained a QA-ADJ block of fifteen scenarios (QA-ADJ-01 –
QA-ADJ-15) and three rows were rewritten where the screen changed under them:
  * QA-RES-06 — the [L-M4] note gained the `Release` source sentence; the expected string was
    extended, and the new sentence is additionally asserted on its own so a regression names it.
  * QA-HIS-05 — the ADJUST `Type` cell now holds a second child, so the per-row type is read off
    `span.ty` instead of the whole cell, `span.src-note` is asserted separately, and every Type
    cell is checked to hold exactly one badge.
  * QA-HIS-18 — the ADJUST row is resolved through `span.ty-adj`.closest('tr') instead of by
    cell text, plus the `span.src-note` census the spec assigns to this row.
None of the three was loosened: each was re-anchored on the element that carries the contract.
Every clause added or rewritten on 2026-08-08 was mutation-tested — 29 single-edit regressions
injected into a throwaway copy of the wireframe, 29 caught by the intended scenario and no other.

QA-ADJ-16 – QA-ADJ-29 remain [ADMIN] in the spec and are deliberately absent here: they need a
persisted event, FIFO receipt consumption, auto-comments, a Slack dispatch, a second operator, a
409, a network fault, a debounce key, a server integer ceiling, the production filter vocabulary
or a seven-order reservation — none of which the shipped file has. QA-ADJ-27 – QA-ADJ-29
(authoritative Total/Reserved at apply, server-side re-validation, and the commit boundary when a
side effect fails) were added by the implementation-lens verification pass and are [ADMIN] for the
same reason: they assert server behaviour the drawing cannot produce, so the [WF] set stays 90. The one clause of QA-ADJ-06
that the fixture cannot reach (the `+N more` truncation line, since no shipped SKU reserves
against more than three orders) is asserted as far as it can be — the cap constant and the
absence of a truncation line under the cap — and the render itself stays with QA-ADJ-20 [ADMIN].

De-monetisation 2026-08-04 (owner decision: "재고 실사의 손실액은 계산하지 말자. 그냥 −1 +1
이런 것만 보이게 하자"). The Stock Audit carries no money at all. Removed from the wireframe: the
`Loss (₩)` audit column and its eleven row cells, the `Loss` columns in [L-M1] / [L-M2] / [L-M2b],
the [L-15] `Total Loss` column, the `Diff × product cost` calculation, and every ₩ figure. The
audit now reports the adjustment count — `Adjustments: {n} ({−a} / {+b}) · New additions: {m}` —
which is what the centre manager tracks toward 0.

Strings and column contracts follow stock-status.md §3.3, §3.11, §3.13, §3.14 and [BR-4] / [E-72]
as landed 2026-08-04. Where the spec's §8 rows had not yet caught up with its own §3 prose at the
time of writing, the §3 prose was taken as authoritative.

Assertions that existed only to check money were converted to must-NOT-exist negatives rather than
deleted, so a reintroduced Loss column or ₩ figure fails loudly: QA-CS-14 and QA-AUD-01 assert
exactly two audit headers, QA-AUD-06 exactly two `td.audcol` per row, QA-AUD-16 no cell after
`Diff`, QA-AUD-22 seven [L-M1] cells, QA-LOG-02 six [L-15] cells, QA-LOG-03 six [L-M2] cells, and
QA-GLB-11 is a page-wide currency negative. QA-LOG-09 was rewritten, NOT retired: its old subject
(the `Total Loss` amber/red/green scale and the ` · target met` suffix) is gone, but the one colour
rule that survived — a zero adjustment count renders green, per §3.11 — moved onto the surviving
`Adjustments` column and is still asserted under that same ID. It is asserted there and nowhere
else, so a colour regression names one scenario. That round left the executed count at 75 and retired
no [WF] ID; the QA-ADJ block of 2026-08-08 took it to the 90 this file runs today.

Money that is NOT audit loss is out of scope and untouched: Inbound Request `Unit Cost` /
`JIT Price` (procurement cost of record) and Order Detail order totals (WooCommerce commerce data)
live on other pages with their own runners.

Protocol implemented exactly per §8.0:
  * Preflight before every scenario: load, wait #p-current.on, click Hide annotations,
    assert body.no-anno + button reads 'Show annotations'.
  * innerText only, normalised: norm(s)=s.replace(NBSP,' ').collapse-ws.strip-trailing-✕.trim()
  * "exactly" = strict equality after norm; bare "reads/contains/begins/ends" = containment/prefix/suffix.
  * Visibility = rendered (getClientRects>0 && display!=none) — offsetParent is unusable for
    position:fixed nodes (.overlay, #auDrop), so the rendered-box test is used as the §8.0
    "renders / is visible" assertion.
  * Reset between scenarios = fresh page load.
  * Colour tokens per the §8.0 table.
  * GLB-08 clause 3 is executed per the spec's own definition sentence ("a plain input merely
    retaining focus is not a scan loop and is not what this test forbids"): after Enter, focus
    is moved away with a user gesture and the assertion is that focus does NOT return to any
    .bcin without a gesture. The literal activeElement-immediately-after-Enter reading is
    recorded as evidence but does not decide the verdict (see notes in the report).

Run:  python3 qa-stock-status.py
"""
import json
import re
import sys
import traceback

from playwright.sync_api import sync_playwright

import pathlib

# Legacy consoles (Windows cp949 / cp1252) otherwise abort the suite mid-run with
# UnicodeEncodeError on the first non-ASCII character, leaving a partial pass count.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:  # pragma: no cover - non-reconfigurable stream
    pass

# 레포 상대경로 — 절대경로를 박으면 클론한 사람 기계에서 전부 미기동된다.
TARGET = (pathlib.Path(__file__).resolve().parents[3] / "stock-status" / "index.html").as_uri()

HELPERS = r"""
window.QA = {
  norm: s => (s ?? '').replace(/ /g, ' ').replace(/\s+/g, ' ').replace(/\s*✕\s*$/, '').trim(),
  t: el => window.QA.norm(el ? el.innerText : ''),
  vis: el => !!el && el.getClientRects().length > 0
        && getComputedStyle(el).display !== 'none'
        && getComputedStyle(el).visibility !== 'hidden',
  clickText: (sel, txt) => {
    const els = [...document.querySelectorAll(sel)];
    const hit = els.find(e => window.QA.norm(e.innerText) === window.QA.norm(txt));
    if (!hit) throw new Error('clickText: no ' + sel + ' with text ' + txt);
    hit.click(); return true;
  },
  rowBySku: sku => [...document.querySelectorAll('#p-current tbody tr')]
      .filter(r => !r.classList.contains('audrow'))
      .find(r => window.QA.norm(r.cells[0].innerText) === sku) || null,
};
"""

COLORS = {
    "amber": "rgb(180, 83, 9)",
    "red": "rgb(220, 53, 69)",
    "green": "rgb(25, 135, 84)",
    "purple": "rgb(88, 45, 181)",
    "purple50": "rgb(247, 243, 255)",
    "ambersoft": "rgb(255, 243, 224)",
}

KO_ALLOW = [
    "글로우 세럼", "미감수 클렌징 티슈", "바이탈 하이드라 워터크림", "마데카솔 크림",
    "시카페어 젠틀 클렌징 폼", "포어레미디 리뉴잉 폼", "시카페어 슬리페어 마스크",
    "제로 모공 패드 2.0", "석류 콜라겐 탄력 크림", "바디로션", "하트리프 77% 수딩 토너",
    "딥 대미지 트리트먼트", "실크 헤어 오일", "자작나무 수분 크림", "다이브인 저분자 세럼",
    "듀 틴트",
    # 17 → 16 (spec §8.0, 2026-08-04): the data string `신규` existed only inside the retired
    # `Loss (₩)` / `Loss` cells as `— (신규)`. Removing money removed the page's last non-product
    # Hangul, so the allow-list is now exactly the product names.
]

# Money was removed from the Stock Audit entirely (owner decision 2026-08-04): the audit reports
# quantity differences only (−1 / +1). There is therefore no money census left to assert — the
# assertion inverted into a must-NOT-exist negative (QA-GLB-11). This page carries no non-audit
# money either, so the negative is page-wide. Inbound Request `Unit Cost` / `JIT Price` and Order
# Detail order totals are deliberately out of scope: different pages, different runners.
MONEY_FORBIDDEN = re.compile(r"₩|\bKRW\b|\$|\bUSD\b|product cost|Loss \(", re.I)


def norm(s):
    s = (s or "").replace(" ", " ")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\s*✕\s*$", "", s)
    return s.strip()


class Mismatch(Exception):
    def __init__(self, expected, actual):
        super().__init__(f"expected={expected!r} actual={actual!r}")
        self.expected = expected
        self.actual = actual


def check(cond, expected, actual):
    if not cond:
        raise Mismatch(expected, actual)


SCENARIOS = []


def scenario(sid):
    def deco(fn):
        SCENARIOS.append((sid, fn))
        return fn
    return deco


def preflight(page):
    page.goto(TARGET)
    page.wait_for_function(
        "document.querySelector('#p-current') && document.querySelector('#p-current').classList.contains('on')"
    )
    page.click("#annoToggle")
    ok = page.evaluate(
        "document.body.classList.contains('no-anno') && QA.norm(document.getElementById('annoToggle').innerText)==='Show annotations'"
    )
    check(ok, "preflight: body.no-anno + annoToggle reads 'Show annotations'",
          page.evaluate("document.getElementById('annoToggle').innerText"))


def go_pane(page, wf_label):
    page.evaluate(f"QA.clickText('.wf-tab', {json.dumps(wf_label)})")


def open_modal_via_wfbar(page, wf_label):
    page.evaluate(f"QA.clickText('.wf-tab', {json.dumps(wf_label)})")


def enter_audit(page):
    page.click("#toggleAudit")


# ---------------------------------------------------------------- QA-NAV -----

@scenario("QA-NAV-01")
def nav01(page):
    r = page.evaluate("""() => {
      const on = id => document.getElementById(id).classList.contains('on');
      const sub = [...document.querySelectorAll('.subtabs button')]
        .find(b => QA.t(b).startsWith('Current Stocks'));
      return {pc: on('p-current'), ps: on('p-search'), pi: on('p-inbound'), po: on('p-outbound'),
              subOn: sub ? sub.classList.contains('on') : false,
              subTxt: sub ? QA.t(sub) : null};
    }""")
    check(r["pc"] and not r["ps"] and not r["pi"] and not r["po"],
          "#p-current only pane with class on", r)
    check(r["subOn"], "sub-tab starting 'Current Stocks' has class on", r)
    check("● new · default" in r["subTxt"], "sub-tab carries marker '● new · default'", r["subTxt"])


@scenario("QA-NAV-02")
def nav02(page):
    page.evaluate("QA.clickText('.subtabs button','Stock History')")
    r1 = page.evaluate("""() => ({
      onPanes: [...document.querySelectorAll('.pane')].filter(p=>p.classList.contains('on')).map(p=>p.id),
      wfOn: [...document.querySelectorAll('.wf-tab')].filter(b=>b.classList.contains('on')).map(b=>QA.t(b)),
    })""")
    check(r1["onPanes"] == ["p-search"], "#p-search only active pane after sub-tab click", r1)
    check(r1["wfOn"] == ["Stock History Search"], "wf-bar 'Stock History Search' gains on", r1)
    go_pane(page, "Inbound Form")
    r2 = page.evaluate("""() => ({
      onPanes: [...document.querySelectorAll('.pane')].filter(p=>p.classList.contains('on')).map(p=>p.id),
      subOn: [...document.querySelectorAll('.subtabs button')].filter(b=>b.classList.contains('on')).map(b=>QA.t(b)),
    })""")
    check(r2["onPanes"] == ["p-inbound"], "#p-inbound only active after wf-bar 'Inbound Form'", r2)
    check(r2["subOn"] and r2["subOn"][0].startswith("Inbound Stock"),
          "sub-tab 'Inbound Stock' gains on", r2)


@scenario("QA-NAV-03")
def nav03(page):
    open_modal_via_wfbar(page, "Modal: Reserved Orders")
    r1 = page.evaluate("""() => ({
      open: document.getElementById('m-reserved').classList.contains('open'),
      pc: document.getElementById('p-current').classList.contains('on')})""")
    check(r1["open"] and r1["pc"], "#m-reserved open AND #p-current still on", r1)
    page.evaluate("QA.clickText('#m-reserved [data-close]','Close')")
    r2 = page.evaluate("""() => ({
      open: document.getElementById('m-reserved').classList.contains('open'),
      pc: document.getElementById('p-current').classList.contains('on')})""")
    check((not r2["open"]) and r2["pc"], "#m-reserved closed, #p-current still active", r2)


@scenario("QA-NAV-04")
def nav04(page):
    t = page.evaluate("QA.t(document.querySelector('.ptitle h2'))")
    check(t == "WMS — Inventory", "'.ptitle h2' exactly 'WMS — Inventory'", t)


PANE_WF = ["Current Stocks (default)", "Stock History Search", "Inbound Form", "Outbound Form"]
MODAL_WF = ["Modal: Reserved Orders", "Modal: Cancel Inbound (Release Reservation)",
            "Modal: Past Audit Logs", "Modal: ADJUST Events (07-22)",
            "Modal: ADJUST Events (06-30)", "Modal: Confirm Audit Differences"]


def sweep_texts(page):
    """Return list of (scope, normalised innerText) for the 4 panes + 6 modals."""
    out = []
    for lbl in PANE_WF:
        go_pane(page, lbl)
        out.append((lbl, page.evaluate("QA.t(document.querySelector('.mock'))")))
    for lbl in MODAL_WF:
        open_modal_via_wfbar(page, lbl)
        mid = page.evaluate("""() => {
          const o=[...document.querySelectorAll('.overlay')].find(o=>o.classList.contains('open'));
          return o? o.id : null;}""")
        out.append((lbl, page.evaluate("QA.t([...document.querySelectorAll('.overlay')].find(o=>o.classList.contains('open')))")))
        page.evaluate("[...document.querySelectorAll('.overlay.open [data-close]')][0].click()")
    return out


@scenario("QA-NAV-06")
def nav06(page):
    for scope, txt in sweep_texts(page):
        check(not re.search(r"print", txt, re.I), f"no /print/i in innerText ({scope})", txt[:200])
    bad = page.evaluate("""() => [...document.querySelectorAll('button,a,input')]
        .map(e => QA.norm((e.innerText||'')+' '+(e.getAttribute('aria-label')||'')+' '
                  +(e.title||'')+' '+(e.placeholder||'')+' '+(e.value||'')))
        .filter(n => /print/i.test(n))""")
    check(bad == [], "no button/a/input accessible name matching /print/i", bad)


@scenario("QA-NAV-07")
def nav07(page):
    r = page.evaluate("""() => ({
      subs: [...document.querySelectorAll('.subtabs button')].map(b=>QA.t(b)),
      auditlog: [...document.querySelectorAll('.subtabs button, .wf-tab')]
                 .map(b=>QA.t(b)).filter(t=>/^Audit Log/.test(t)),
    })""")
    starts = ["Current Stocks", "Stock History", "Inbound Stock", "Outbound Stock"]
    check(len(r["subs"]) == 4 and all(r["subs"][i].startswith(starts[i]) for i in range(4)),
          "exactly four sub-tab buttons beginning " + str(starts), r["subs"])
    check(r["auditlog"] == [], "no .subtabs button / .wf-tab matching /^Audit Log/", r["auditlog"])


@scenario("QA-NAV-08")
def nav08(page):
    pats = [r"procurement hub", r"return.?bin", r"sample", r"photo|upload"]
    for scope, txt in sweep_texts(page):
        for p in pats:
            check(not re.search(p, txt, re.I), f"no /{p}/i in innerText ({scope})", txt[:200])
    nfile = page.evaluate("document.querySelectorAll('input[type=file]').length")
    check(nfile == 0, "no input[type=file]", nfile)


@scenario("QA-NAV-09")
def nav09(page):
    r = page.evaluate("""() => ({
      tabs: [...document.querySelectorAll('.wf-tab')].map(b=>QA.t(b)),
      toggles: [...document.querySelectorAll('.wf-toggle')].map(b=>b.id)})""")
    expect = PANE_WF + MODAL_WF
    check(r["tabs"] == expect, "10 wf-tab buttons labelled exactly " + str(expect), r["tabs"])
    check(r["toggles"] == ["annoToggle"], "one .wf-toggle (#annoToggle)", r["toggles"])


@scenario("QA-NAV-11")
def nav11(page):
    r = page.evaluate("""() => {
      const nav = document.querySelector('.nav');
      const cats = [...nav.querySelectorAll(':scope > span')]
          .filter(s => !s.className && QA.t(s).endsWith('▾')).map(s => QA.t(s));
      const links = [...nav.querySelectorAll('.navlink')].map(s => QA.t(s));
      const btn = nav.querySelector('[data-open="inbox1"]');
      const badge = btn ? btn.querySelector('.badge-n') : null;
      const user = nav.querySelector('.user'); const av = user ? user.querySelector('.avatar') : null;
      const lo = nav.querySelector('button.logout');
      return {brand: QA.t(nav.querySelector('.brand')), cats, links,
              btnTxt: btn ? QA.norm(btn.childNodes[0].textContent) : null,
              badge: badge ? QA.t(badge) : null,
              avatar: av ? QA.norm(av.textContent) : null,
              userTail: user ? QA.norm(user.textContent).replace(/^Y\\s*/, '') : null,
              logout: lo ? QA.t(lo) : null};
    }""")
    check(r["brand"] == "SkinSeoul", ".brand exactly 'SkinSeoul'", r["brand"])
    cats = ["Operation AI ▾", "Catalog Management ▾", "OMS Center ▾",
            "Site Management ▾", "System Management ▾", "Customer Management ▾"]
    check(r["cats"] == cats, "six category labels exactly " + str(cats), r["cats"])
    links = ["Agent Telemetry", "Role Assets", "Shared Asset Health", "SkinSeoul WP Admin"]
    check(r["links"] == links, "four .navlink exactly " + str(links), r["links"])
    check(r["btnTxt"] == "💬 Comments" and r["badge"] == "3",
          "'💬 Comments' button with .badge-n '3'", r)
    check(r["avatar"] == "Y" and r["userTail"] == "Yongwon Ryu",
          ".user = .avatar 'Y' + 'Yongwon Ryu'", r)
    check(r["logout"] == "Logout", "button.logout exactly 'Logout'", r["logout"])


# ----------------------------------------------------------------- QA-CS -----

CS_SKUS = ["100031877", "100024743", "100005088", "100004819", "100039958",
           "100005104", "100040311", "100012534", "100043697", "100038120", "100045210"]
CS_AVAIL = ["82", "61", "55", "34", "23", "16", "11", "6", "4", "2", "1"]


def data_rows(page):
    return page.evaluate("""() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r => !r.classList.contains('audrow'))
        .map(r => [...r.cells].map(c => QA.t(c)))""")


@scenario("QA-CS-01")
def cs01(page):
    rows = data_rows(page)
    skus = [r[0] for r in rows]
    avail = [r[10] for r in rows]
    check(len(rows) == 11, "eleven data rows", len(rows))
    check(skus == CS_SKUS, "SKU order " + ",".join(CS_SKUS), skus)
    check(avail == CS_AVAIL, "Available values " + ",".join(CS_AVAIL), avail)


@scenario("QA-CS-03")
def cs03(page):
    opts = page.evaluate("""[...document.querySelectorAll('.cs-controls select.sel')[0].options].map(o=>QA.norm(o.textContent))""")
    check(opts[0] == "All Locations", "option 1 'All Locations'", opts)
    check(opts[1:] == ["Line A", "Line B", "Line C"], "remaining options Line A/B/C only", opts)
    check(not any(re.match(r"^[A-Z]-\d", o) for o in opts), "no full location code option", opts)


@scenario("QA-CS-05")
def cs05(page):
    opts = page.evaluate("""[...document.querySelectorAll('.cs-controls select.sel')[1].options].map(o=>QA.norm(o.textContent))""")
    expect = ["All Sourcing Routes", "SMART BUY", "JIT", "WHOLESALE", "PARTNERSHIP"]
    check(opts == expect, "second select exactly " + str(expect), opts)


@scenario("QA-CS-08")
def cs08(page):
    r = page.evaluate("""() => [...document.querySelectorAll('.tag-smartbuy,.tag-jit,.tag-wholesale,.tag-partnership')]
        .map(e => ({cls: e.className, bg: getComputedStyle(e).backgroundColor, fw: getComputedStyle(e).fontWeight}))""")
    check(len(r) > 0, "route tags exist", r)
    for e in r:
        check(e["bg"] in ("rgba(0, 0, 0, 0)", "transparent"),
              f"transparent background on {e['cls']}", e)
        check(e["fw"] == "800", f"font-weight 800 on {e['cls']}", e)


@scenario("QA-CS-09")
def cs09(page):
    r = page.evaluate("""() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r => {const c = r.cells[3];
          return {sku: QA.t(r.cells[0]), first: c.firstElementChild ? c.firstElementChild.tagName : null,
                  brand: c.firstElementChild ? QA.norm(c.firstElementChild.textContent) : null,
                  txt: QA.t(c)};})""")
    for e in r:
        check(e["first"] == "B", f"KR cell first element child is <b> (SKU {e['sku']})", e)
    row = next(e for e in r if e["sku"] == "100005104")
    check(row["brand"] == "Dr.Jart+" and row["txt"] == "Dr.Jart+ 포어레미디 리뉴잉 폼",
          "100005104 renders '<b>Dr.Jart+</b> 포어레미디 리뉴잉 폼'", row)


@scenario("QA-CS-10")
def cs10(page):
    r = page.evaluate("""() => {const row = QA.rowBySku('100038120');
      if (!row) return null;
      const i = row.querySelector('input.loc-in');
      return {value: i.value, ph: i.placeholder, visible: QA.vis(row)};}""")
    check(r is not None, "row for SKU 100038120 present", r)
    check(r["value"] == "" and r["ph"] == "Unassigned" and r["visible"],
          "loc-in value empty, placeholder 'Unassigned', row visible", r)


@scenario("QA-CS-14")
def cs14(page):
    r = page.evaluate("""() => {
      const ths = [...document.querySelectorAll('#p-current thead th')];
      return {vis: ths.filter(t=>getComputedStyle(t).display!=='none').map(t=>QA.t(t)),
              aud: ths.filter(t=>t.classList.contains('audcol'))
                     .map(t=>({txt: QA.norm(t.textContent), disp: getComputedStyle(t).display}))};}""")
    expect = ["SKU", "Image", "Product Name", "Product Name KR", "Size", "Barcode",
              "Sourcing Route", "Location", "Total", "Reserved", "Available"]
    check(r["vis"] == expect, "visible headers exactly " + str(expect), r["vis"])
    # NEGATIVE (money removed 2026-08-04): exactly TWO audit columns. A third `Loss (₩)` column
    # must not exist — the audit is quantity-only.
    check([a["txt"] for a in r["aud"]] == ["Counted Qty", "Diff"],
          "exactly two th.audcol 'Counted Qty','Diff' — no Loss column", r["aud"])
    check(not any(MONEY_FORBIDDEN.search(a["txt"]) for a in r["aud"]),
          "no money/cost token in any audit header", r["aud"])
    check(all(a["disp"] == "none" for a in r["aud"]), "th.audcol computed display none", r["aud"])


@scenario("QA-CS-15")
def cs15(page):
    r = page.evaluate("""() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r=>({thumb: r.querySelector('.thumb') ? QA.t(r.querySelector('.thumb')) : null,
                  size: QA.t(r.cells[4])}))""")
    check(all(e["thumb"] == "IMG" for e in r), "all rows render .thumb 'IMG'", r)
    sizes = [e["size"] for e in r]
    expect = ["30ml", "50ea", "50ml", "50ml", "350ml", "150ml", "100ml", "75ml", "150ml", "70ea", "250ml"]
    check(sizes == expect, "Size cells " + str(expect), sizes)


@scenario("QA-CS-16")
def cs16(page):
    r = page.evaluate("""() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r=>{const c=r.cells[9];
          return {res: !!c.querySelector('.reslink'), a: !!c.querySelector('a'),
                  dm: !!c.querySelector('[data-modal]') || c.hasAttribute('data-modal')};})""")
    check(all(not (e["res"] or e["a"] or e["dm"]) for e in r),
          "no Reserved cell contains .reslink / <a> / [data-modal]", r)


# ---------------------------------------------------------------- QA-LOC -----

@scenario("QA-LOC-01")
def loc01(page):
    r = page.evaluate("""() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r=>({n: r.querySelectorAll('input.loc-in').length,
                  v: r.querySelector('input.loc-in') ? r.querySelector('input.loc-in').value : null}))""")
    check(all(e["n"] == 1 for e in r), "each row exactly one input.loc-in", r)
    vals = [e["v"] for e in r]
    expect = ["B-02-03", "A-03-02", "B-01-07", "A-02-13", "C-01-05",
              "A-01-04", "A-01-05", "A-02-20", "C-02-01", "", "B-03-02"]
    check(vals == expect, "loc-in values " + str(expect), vals)


@scenario("QA-LOC-08")
def loc08(page):
    r = page.evaluate("""() => {
      const r1 = QA.rowBySku('100024743'), r2 = QA.rowBySku('100031877');
      return {ph: r1.cells[5].querySelector('input.bcin') ? r1.cells[5].querySelector('input.bcin').placeholder : null,
              plain: QA.t(r2.cells[5]), hasInput2: !!r2.cells[5].querySelector('input'),
              scoped: document.querySelectorAll('#p-current tbody tr:not(.audrow) .bcin').length};}""")
    check(r["ph"] == "Enter barcode", "100024743 renders input.bcin placeholder 'Enter barcode'", r)
    check(r["plain"] == "8809738317481" and not r["hasInput2"],
          "100031877 renders plain text '8809738317481'", r)
    check(r["scoped"] == 1, "#p-current tbody tr:not(.audrow) .bcin count === 1", r["scoped"])


@scenario("QA-LOC-18")
def loc18(page):
    page.evaluate("window.__qa_alive = 1")
    inp = page.locator('#p-current tbody tr:not(.audrow)').filter(has_text="100004819").locator("input.loc-in")
    inp.click()
    inp.fill("")
    inp.fill("A-02-14")
    inp.press("Enter")
    r = page.evaluate("""() => ({
      v: QA.rowBySku('100004819').querySelector('input.loc-in').value,
      alive: window.__qa_alive || 0})""")
    check(r["v"] == "A-02-14", "input live value exactly 'A-02-14'", r)
    check(r["alive"] == 1, "document not re-navigated / no form submission", r)


# ---------------------------------------------------------------- QA-AUD -----

AUDIT_SORTED = ["100005104", "100040311", "100004819", "100012534", "100024743",
                "100005088", "100031877", "100045210", "100039958", "100043697", "100038120"]


@scenario("QA-AUD-01")
def aud01(page):
    pre = page.evaluate("""() => ({
      btn: QA.t(document.getElementById('toggleAudit')),
      audVis: [...document.querySelectorAll('#p-current .audcol')].some(QA.vis),
      sumVis: QA.vis(document.getElementById('auditSummary')),
      rowVis: QA.vis(document.querySelector('#p-current .audrow'))})""")
    check(pre["btn"] == "Start Stock Audit" and not pre["audVis"] and not pre["sumVis"] and not pre["rowVis"],
          "pre-state: 'Start Stock Audit', audcol/summary/audrow hidden", pre)
    enter_audit(page)
    post = page.evaluate("""() => {
      const rows = [...document.querySelectorAll('#p-current tbody tr')];
      const heads = [...document.querySelectorAll('#p-current thead th.audcol')].map(t=>({t: QA.norm(t.textContent), v: QA.vis(t)}));
      return {btn: QA.t(document.getElementById('toggleAudit')),
        heads,
        sumVis: QA.vis(document.getElementById('auditSummary')),
        lastIsAudrow: rows[rows.length-1].classList.contains('audrow'),
        audrowVis: QA.vis(document.querySelector('#p-current .audrow')),
        order: rows.filter(r=>!r.classList.contains('audrow')).map(r=>QA.t(r.cells[0]))};}""")
    check(post["btn"] == "Exit Stock Audit", "button becomes exactly 'Exit Stock Audit'", post["btn"])
    check([h["t"] for h in post["heads"]] == ["Counted Qty", "Diff"]
          and all(h["v"] for h in post["heads"]),
          "audit headers 'Counted Qty','Diff' visible — no third Loss column", post["heads"])
    check(post["audrowVis"] and post["lastIsAudrow"], ".audrow visible as last tbody row", post)
    check(post["sumVis"], "#auditSummary visible", post["sumVis"])
    check(post["order"] == AUDIT_SORTED,
          "location-ascending order with 100038120 (empty) last: " + str(AUDIT_SORTED), post["order"])


@scenario("QA-AUD-02")
def aud02(page):
    enter_audit(page)
    page.click("#toggleAudit")
    r = page.evaluate("""() => ({
      btn: QA.t(document.getElementById('toggleAudit')),
      audAllHidden: [...document.querySelectorAll('#p-current .audcol')].every(c=>getComputedStyle(c).display==='none'),
      sumHidden: getComputedStyle(document.getElementById('auditSummary')).display==='none',
      rowHidden: getComputedStyle(document.querySelector('#p-current .audrow')).display==='none',
      first: QA.t([...document.querySelectorAll('#p-current tbody tr')].filter(r=>!r.classList.contains('audrow'))[0].cells[0])})""")
    check(r["btn"] == "Start Stock Audit", "button reads 'Start Stock Audit'", r["btn"])
    check(r["audAllHidden"] and r["sumHidden"] and r["rowHidden"],
          "every .audcol / #auditSummary / .audrow display none", r)
    check(r["first"] == "100031877", "first data row SKU 100031877 (Available-desc restored)", r["first"])


@scenario("QA-AUD-03")
def aud03(page):
    enter_audit(page)
    r = page.evaluate("""() => ({
      txt: QA.t(document.getElementById('auditSummary')),
      pre: QA.t(document.querySelector('#auditSummary span')),
      btn: [...document.querySelectorAll('#auditSummary button')].map(b=>QA.t(b))})""")
    # Rewritten 2026-08-04 (spec §3.3): the bar carries counts, not a cost-weighted total.
    check(r["pre"] == "Adjustments: 2 (−1 / +2) · New additions: 1",
          "text before the button exactly 'Adjustments: 2 (−1 / +2) · New additions: 1'", r["pre"])
    # NEGATIVE: no currency value, no cost-weighted total, no monetary target may return here.
    check(not MONEY_FORBIDDEN.search(r["txt"]) and "target 0" not in r["txt"],
          "no ₩ / cost token and no monetary 'target 0' in #auditSummary", r["txt"])
    check(r["btn"] == ["Confirm Audit Differences (ADJUST log)"],
          "button exactly 'Confirm Audit Differences (ADJUST log)'", r["btn"])


@scenario("QA-AUD-04")
def aud04(page):
    enter_audit(page)
    r = page.evaluate("""() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r=>({sku: QA.t(r.cells[0]), total: QA.t(r.cells[8]),
                  counted: r.querySelector('input.qty-in') ? r.querySelector('input.qty-in').value : null}))""")
    eq = [e for e in r if e["total"] == e["counted"]]
    ne = {e["sku"]: (e["total"], e["counted"]) for e in r if e["total"] != e["counted"]}
    check(len(eq) == 9, "exactly nine rows prefilled equal to Total", r)
    check(ne == {"100005104": ("18", "17"), "100012534": ("9", "11")},
          "two seeded diffs: 100005104 18/17, 100012534 9/11", ne)


@scenario("QA-AUD-06")
def aud06(page):
    enter_audit(page)
    r = page.evaluate("""() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r=>({sku: QA.t(r.cells[0]), diff: QA.t(r.cells[12]),
                  nAud: r.querySelectorAll('td.audcol').length, txt: QA.t(r)}))""")
    by = {e["sku"]: e["diff"] for e in r}
    check(by["100005104"] == "−1", "100005104 Diff −1", by["100005104"])
    check(by["100012534"] == "+2", "100012534 Diff +2", by["100012534"])
    others = {k: v for k, v in by.items() if k not in ("100005104", "100012534")}
    check(all(v == "0" for v in others.values()), "other nine rows Diff 0", others)
    # Count reconciliation replaces the retired money reconciliation: two non-zero rows, one
    # negative and one positive, matching #auditSummary's `Adjustments: 2 (−1 / +2)` (QA-AUD-03).
    nz = [v for v in by.values() if v != "0"]
    check(len(nz) == 2 and sorted(nz) == ["+2", "−1"],
          "two non-zero Diffs (−1 / +2) reconcile with 'Adjustments: 2 (−1 / +2)'", nz)
    # NEGATIVE (money removed 2026-08-04): exactly two td.audcol per row — no per-row money cell.
    check(all(e["nAud"] == 2 for e in r), "every data row exposes exactly two td.audcol", r)
    check(not any(MONEY_FORBIDDEN.search(e["txt"]) for e in r),
          "no row renders ₩ / a cost token", [e["txt"] for e in r if MONEY_FORBIDDEN.search(e["txt"])])


@scenario("QA-AUD-11")
def aud11(page):
    r = page.evaluate("""() => ({
      sum: getComputedStyle(document.getElementById('auditSummary')).display,
      aud: [...document.querySelectorAll('#p-current .audcol')].map(c=>getComputedStyle(c).display),
      row: getComputedStyle(document.querySelector('#p-current .audrow')).display})""")
    check(r["sum"] == "none" and r["row"] == "none" and all(d == "none" for d in r["aud"]),
          "audit off: #auditSummary, every .audcol, .audrow display none", r)


@scenario("QA-AUD-12")
def aud12(page):
    enter_audit(page)
    page.fill("#auSearch", "UNOVE")
    r = page.evaluate("""() => ({
      vis: QA.vis(document.getElementById('auDrop')),
      entries: [...document.querySelectorAll('#auDrop div[data-sku]')].map(d=>QA.t(d))})""")
    check(r["vis"], "#auDrop becomes visible", r)
    expect = ["UNOVE 딥 대미지 트리트먼트 · 320ml · 100048201",
              "UNOVE 실크 헤어 오일 · 150ml · 100051200"]
    check(r["entries"] == expect, "exactly two entries with size shown: " + str(expect), r["entries"])


@scenario("QA-AUD-13")
def aud13(page):
    enter_audit(page)
    page.fill("#auSearch", "zzzz")
    r = page.evaluate("""() => ({
      txt: QA.t(document.getElementById('auDrop')),
      n: document.querySelectorAll('#auDrop div[data-sku]').length})""")
    check(r["txt"] == "No match — register manually via Unrecognized flow (F)",
          "#auDrop exactly 'No match — register manually via Unrecognized flow (F)'", r["txt"])
    check(r["n"] == 0, "zero div[data-sku]", r["n"])


@scenario("QA-AUD-14")
def aud14(page):
    enter_audit(page)
    before = page.evaluate("document.querySelectorAll('#p-current tbody tr').length")
    page.fill("#auSearch", "Torrid")
    page.click("#auAdd")
    r = page.evaluate("""() => ({
      rows: document.querySelectorAll('#p-current tbody tr').length,
      active: document.activeElement ? document.activeElement.id : null})""")
    check(r["rows"] == before, "tbody row count unchanged", {"before": before, "after": r["rows"]})
    check(r["active"] == "auSearch", "document.activeElement is #auSearch", r["active"])


def add_torriden(page):
    page.fill("#auSearch", "Torriden")
    page.click('#auDrop div[data-sku="100027733"]')
    page.fill("#auLoc", "B-01-02")
    page.fill("#auQty", "3")
    page.click("#auAdd")


@scenario("QA-AUD-16")
def aud16(page):
    enter_audit(page)
    add_torriden(page)
    r = page.evaluate("""() => {
      const tr = document.querySelector('#p-current tbody').firstElementChild;
      const c = tr.cells;
      return {bg: getComputedStyle(tr).backgroundColor,
        sku: QA.t(c[0]), kr: QA.t(c[3]), size: QA.t(c[4]),
        total: QA.t(c[8]), res: QA.t(c[9]), avail: QA.t(c[10]),
        counted: c[11].querySelector('input.qty-in') ? c[11].querySelector('input.qty-in').value : null,
        diff: QA.t(c[12]), nCells: c.length, rowTxt: QA.t(tr),
        s: document.getElementById('auSearch').value,
        l: document.getElementById('auLoc').value,
        q: document.getElementById('auQty').value};}""")
    check(r["bg"] == COLORS["purple50"], "new row purple-tinted (rgb(247, 243, 255))", r["bg"])
    check(r["sku"] == "100027733", "SKU 100027733", r["sku"])
    check("Torriden 다이브인 저분자 세럼" in r["kr"] and "[NEW]" in r["kr"],
          "KR name 'Torriden 다이브인 저분자 세럼' with [NEW] marker", r["kr"])
    check(r["size"] == "50ml", "size 50ml", r["size"])
    check((r["total"], r["res"], r["avail"]) == ("0", "0", "0"), "Total 0 / Reserved 0 / Available 0", r)
    check(r["counted"] == "3" and r["diff"] == "+3", "Counted Qty 3, Diff +3", r)
    # NEGATIVE (money removed 2026-08-04): the inserted row ends at Diff. The former
    # `Loss — (신규)` cell must not exist — a new addition is a quantity, not an amount.
    check(r["nCells"] == 13, "inserted row has exactly 13 cells (Diff is last, no Loss cell)", r["nCells"])
    check(not MONEY_FORBIDDEN.search(r["rowTxt"]) and "(신규)" not in r["rowTxt"],
          "inserted row renders no ₩ / cost token and no '(신규)' loss placeholder", r["rowTxt"])
    check(r["s"] == "" and r["l"] == "" and r["q"] == "", "#auSearch/#auLoc/#auQty cleared", r)


@scenario("QA-AUD-17")
def aud17(page):
    enter_audit(page)
    page.fill("#auSearch", "자작나무")
    page.click('#auDrop div[data-sku="100032911"]')
    page.click("#auAdd")
    r = page.evaluate("""() => {
      const tr = document.querySelector('#p-current tbody').firstElementChild;
      return {counted: tr.querySelector('input.qty-in').value,
              loc: tr.querySelector('input.loc-in').value};}""")
    check(r["counted"] == "1", "inserted row Counted Qty 1", r)
    check(r["loc"] == "Unassigned", "inserted row .loc-in value 'Unassigned'", r)


@scenario("QA-AUD-22")
def aud22(page):
    enter_audit(page)
    page.evaluate("QA.clickText('#auditSummary button','Confirm Audit Differences (ADJUST log)')")
    r = page.evaluate("""() => {
      const m = document.getElementById('m-adjust');
      const rows = [...m.querySelectorAll('tbody tr')].map(r=>[...r.cells].map(c=>QA.t(c)));
      const news = [...m.querySelectorAll('tbody tr')].filter(r=>/\\[NEW\\]/.test(r.cells[1].textContent)).length;
      const primary = m.querySelector('.foot .btn-blue');
      return {open: m.classList.contains('open'), head: QA.t(m.querySelector('header')),
              rows, news, primary: primary ? QA.t(primary) : null};}""")
    check(r["open"], "#m-adjust gains class open", r["open"])
    check(r["head"] == "Confirm Audit Differences — July 2026 Stock Audit (Auditor: Yongwon)",
          "header exactly (normalised)", r["head"])
    check(len(r["rows"]) == 3, "exactly three body rows", r["rows"])
    expect = [("100005104", "18", "17", "−1"), ("100012534", "9", "11", "+2"), ("100048201", "0", "3", "+3")]
    got = [(x[0], x[3], x[4], x[5]) for x in r["rows"]]
    check(got == expect, "cell-by-cell SKU/System/Counted/Diff " + str(expect), got)
    check(r["news"] == 1, "exactly one row carries [NEW]", r["news"])
    check(all(x[5] != "0" for x in r["rows"]), "no zero-diff row", [x[5] for x in r["rows"]])
    # NEGATIVE (money removed 2026-08-04): seven columns ending at Action — no Loss column.
    check(all(len(x) == 7 for x in r["rows"]), "every row has exactly 7 cells (Action is last)", r["rows"])
    check(not any(MONEY_FORBIDDEN.search(c) for x in r["rows"] for c in x),
          "no ₩ / cost token in any [L-M1] row", r["rows"])
    check(r["primary"] == "Confirm — record 3 ADJUST events",
          "primary footer button exactly 'Confirm — record 3 ADJUST events'", r["primary"])


@scenario("QA-AUD-23")
def aud23(page):
    enter_audit(page)
    page.evaluate("QA.clickText('#auditSummary button','Confirm Audit Differences (ADJUST log)')")
    r = page.evaluate("""() => {
      const notes = [...document.querySelectorAll('#m-adjust .note')].map(n=>QA.t(n));
      return notes;}""")
    check(len(r) == 2, "two notes in #m-adjust", r)
    check(r[0].startswith("⚠ Reserved shortage check") and r[0].endswith("None in this audit."),
          "amber note begins '⚠ Reserved shortage check' / ends 'None in this audit.'", r[0])
    exp = ("Adjustments: 2 (−1 / +2) · New additions: 1 (counted separately) — on confirm, "
           "Current Stocks · Available update immediately; monthly audit logs retained.")
    check(r[1] == exp, "second note exactly (spec §3.13, rewritten 2026-08-04)", r[1])
    check(not MONEY_FORBIDDEN.search(r[1]), "NEGATIVE: no money total in the [L-M1] note", r[1])


@scenario("QA-AUD-36")
def aud36(page):
    enter_audit(page)
    add_torriden(page)
    open_modal_via_wfbar(page, "Modal: Past Audit Logs")
    page.evaluate("QA.clickText('#m-auditlog [data-close]','Close')")
    r = page.evaluate("""() => ({
      btn: QA.t(document.getElementById('toggleAudit')),
      first: QA.t(document.querySelector('#p-current tbody').firstElementChild.cells[0]),
      pc: document.getElementById('p-current').classList.contains('on')})""")
    check(r["btn"] == "Exit Stock Audit", "#toggleAudit still reads 'Exit Stock Audit'", r["btn"])
    check(r["first"] == "100027733", "added row still first tbody child", r["first"])
    check(r["pc"], "#p-current still the active pane", r["pc"])


# ---------------------------------------------------------------- QA-LOG -----

@scenario("QA-LOG-01")
def log01(page):
    page.evaluate("QA.clickText('#p-current button','📋 Past Audit Logs')")
    r = page.evaluate("""() => ({
      open: document.getElementById('m-auditlog').classList.contains('open'),
      head: QA.t(document.querySelector('#m-auditlog header'))})""")
    check(r["open"], "#m-auditlog gains class open", r)
    check(r["head"].startswith("Past Audit Logs — monthly session records"),
          "header starts 'Past Audit Logs — monthly session records'", r["head"])


@scenario("QA-LOG-02")
def log02(page):
    open_modal_via_wfbar(page, "Modal: Past Audit Logs")
    r = page.evaluate("""() => ({
      head: [...document.querySelectorAll('#m-auditlog thead th')].map(t=>QA.t(t)),
      rows: [...document.querySelectorAll('#m-auditlog tbody tr')].map(r=>[...r.cells].slice(0,5).map(c=>QA.t(c))),
      nCells: [...document.querySelectorAll('#m-auditlog tbody tr')].map(r=>r.cells.length)})""")
    # Six columns (spec §3.11). The seventh, `Total Loss`, was RETIRED 2026-08-04 — not renamed.
    check(r["head"] == ["Audit Date", "Auditor", "SKUs Checked", "Adjustments", "New Additions", "Detail"],
          "header row exactly six columns — no 'Total Loss' / 'Total Diff'", r["head"])
    expect = [["2026-07-22", "Yongwon", "10", "2 (−1 / +2)", "1"],
              ["2026-06-30", "Dean", "9", "5 (−4 / +1)", "0"],
              ["2026-05-31", "Dean", "9", "0", "0"]]
    check(r["rows"] == expect, "exactly three body rows with values " + str(expect), r["rows"])
    check(r["nCells"] == [6, 6, 6], "NEGATIVE: every row has exactly 6 cells, no seventh", r["nCells"])
    check(not any(MONEY_FORBIDDEN.search(c) for row in r["rows"] for c in row)
          and not any(MONEY_FORBIDDEN.search(h) for h in r["head"]),
          "NEGATIVE: no ₩ / cost token anywhere in [L-15]", r)
    # The `Adjustments` colour rule (§3.11: a zero count renders green) is NOT asserted here —
    # it is owned by QA-LOG-09, which was rewritten onto that column rather than retired. Keeping
    # it in one place only, so a colour regression names a single scenario.


@scenario("QA-LOG-03")
def log03(page):
    open_modal_via_wfbar(page, "Modal: Past Audit Logs")
    page.evaluate("""() => {
      const row = [...document.querySelectorAll('#m-auditlog tbody tr')].find(r=>QA.t(r.cells[0])==='2026-07-22');
      row.querySelector('a[data-modal]').click();}""")
    r = page.evaluate("""() => {
      const m = document.getElementById('m-adjlog');
      const rows = [...m.querySelectorAll('tbody tr')];
      return {open: m.classList.contains('open'), head: QA.t(m.querySelector('header')),
        cols: [...m.querySelectorAll('thead th')].map(t=>QA.t(t)),
        times: rows.map(r=>QA.t(r.cells[0])),
        nCells: rows.map(r=>r.cells.length),
        thirdBg: getComputedStyle(rows[2]).backgroundColor,
        thirdNew: /\\[NEW ADDITION\\]/.test(rows[2].cells[2].textContent),
        bodyTxt: QA.t(m.querySelector('.body'))};}""")
    check(r["open"], "#m-adjlog gains class open", r)
    check(r["head"] == "2026-07-22 Stock Audit — 3 ADJUST events (Auditor: Yongwon, confirmed 14:20)",
          "header exactly (normalised)", r["head"])
    check(r["times"] == ["14:20:11"] * 3, "three rows all timestamped 14:20:11", r["times"])
    check(r["thirdBg"] == COLORS["purple50"] and r["thirdNew"],
          "third row purple-tinted and carries [NEW ADDITION]", r)
    # NEGATIVE (money removed 2026-08-04): the ADJUST-event table ends at `Adjustment`. The former
    # `Loss` column — and the third row's `—` money placeholder with it — must not exist.
    check(r["cols"] == ["Time", "SKU", "Product", "Location", "System → Counted", "Adjustment"],
          "six columns ending at 'Adjustment' — no Loss column", r["cols"])
    check(r["nCells"] == [6, 6, 6], "every row has exactly 6 cells", r["nCells"])
    check(not MONEY_FORBIDDEN.search(r["bodyTxt"]), "no ₩ / cost token in [L-M2]", r["bodyTxt"])


@scenario("QA-LOG-04")
def log04(page):
    open_modal_via_wfbar(page, "Modal: Past Audit Logs")
    page.evaluate("""() => {
      const row = [...document.querySelectorAll('#m-auditlog tbody tr')].find(r=>QA.t(r.cells[0])==='2026-06-30');
      row.querySelector('a[data-modal]').click();}""")
    r = page.evaluate("""() => {
      const m = document.getElementById('m-adjlog6');
      return {open: m.classList.contains('open'), head: QA.t(m.querySelector('header')),
        times: [...m.querySelectorAll('tbody tr')].map(r=>QA.t(r.cells[0])),
        note: QA.t(m.querySelector('.note'))};}""")
    check(r["open"], "#m-adjlog6 opens", r)
    check(r["head"] == "2026-06-30 Stock Audit — 5 ADJUST events (Auditor: Dean, confirmed 17:05)",
          "header exactly (normalised)", r["head"])
    check(r["times"] == ["17:05:42"] * 5, "five rows all timestamped 17:05:42", r["times"])
    exp = ("Adjustments: 5 (−4 / +1) — June is the outlier; root-cause investigation "
           "in progress (suspected picking mis-outbound).")
    check(exp in r["note"], "note reads (contains) the June outlier text", r["note"])
    check(not MONEY_FORBIDDEN.search(r["note"]),
          "NEGATIVE: the June outlier is stated in counts, never in money", r["note"])


@scenario("QA-LOG-05")
def log05(page):
    open_modal_via_wfbar(page, "Modal: Past Audit Logs")
    r = page.evaluate("""() => {
      const row = [...document.querySelectorAll('#m-auditlog tbody tr')].find(r=>QA.t(r.cells[0])==='2026-05-31');
      const a = row.cells[5].querySelector('a');   // Detail moved 6 → 5 when `Total Loss` retired
      const before = [...document.querySelectorAll('.overlay.open')].map(o=>o.id);
      if (a) a.click();
      const after = [...document.querySelectorAll('.overlay.open')].map(o=>o.id);
      return {detail: QA.t(row.cells[5]), hasDM: a ? a.hasAttribute('data-modal') : null, before, after};}""")
    check("—" in r["detail"], "2026-05-31 Detail cell contains literal '—'", r["detail"])
    check(r["hasDM"] is False, "anchor carries no data-modal attribute", r["hasDM"])
    check(r["before"] == r["after"] == ["m-auditlog"], "clicking it opens no modal", r)


@scenario("QA-LOG-06")
def log06(page):
    open_modal_via_wfbar(page, "Modal: ADJUST Events (07-22)")
    r = page.evaluate("""() => ({
      note: QA.t(document.querySelector('#m-adjlog .note')),
      prods: [...document.querySelectorAll('#m-adjlog tbody tr')]
        .map(row=>{const c=row.cells[2];
          return {first: c.firstElementChild ? c.firstElementChild.tagName : null,
                  brand: c.firstElementChild ? QA.norm(c.firstElementChild.textContent) : null};})})""")
    exp = ("Each event is also recorded as ADJUST type in that SKU's Stock History — search the SKU "
           "and filter by type to inspect individually. Adjustments: 2 (−1 / +2) · "
           "New additions: 1 (counted separately).")
    check(r["note"] == exp, "note exactly", r["note"])
    check(all(p["first"] == "B" and p["brand"] for p in r["prods"]),
          "every Product cell first element child is a <b> brand", r["prods"])


@scenario("QA-LOG-09")
def log09(page):
    """[L-15] adjustment-count colour rule — REWRITTEN 2026-08-04, not retired.

    This ID used to assert the amber / red / green scale on the `Total Loss` cell plus the
    ` · target met` suffix on the zero row. Money left the audit, so that column, its three-tier
    scale and that suffix are gone. The one colour rule that survived moved onto the surviving
    `Adjustments` column — spec §3.11: "a zero count renders green, every non-zero count renders
    in the table's default colour" — and that is what this ID now pins (spec §8 QA-LOG-09).

    Do not re-add a money column or a money colour scale under this ID. The colour rule lives
    here and NOT in QA-LOG-02, so a regression names exactly one scenario.
    """
    open_modal_via_wfbar(page, "Modal: Past Audit Logs")
    r = page.evaluate("""() => ({
      cells: [...document.querySelectorAll('#m-auditlog tbody tr')]
        .map(r => ({d: QA.t(r.cells[0]), c: getComputedStyle(r.cells[3]).color})),
      head: QA.t(document.querySelector('#m-auditlog thead tr')),
      text: QA.t(document.querySelector('#m-auditlog'))})""")
    # Guard the precondition: cells[3] must actually be `Adjustments`, or the colour probe below
    # would be reading whatever column drifted into slot 3 and would pass for the wrong reason.
    check(r["head"] == "Audit Date Auditor SKUs Checked Adjustments New Additions Detail",
          "column 4 is `Adjustments` — the colour probe targets the right cell", r["head"])
    zero = [e for e in r["cells"] if e["d"] == "2026-05-31"]
    rest = [e for e in r["cells"] if e["d"] != "2026-05-31"]
    check(len(zero) == 1 and len(rest) == 2,
          "three [L-15] rows, exactly one being the zero-adjustment 2026-05-31 session", r["cells"])
    check(zero[0]["c"] == COLORS["green"],
          "2026-05-31 `Adjustments` cell computes --green " + COLORS["green"], zero)
    check(all(e["c"] != COLORS["green"] for e in rest),
          "the 2026-07-22 and 2026-06-30 `Adjustments` cells are NOT green", rest)
    # Structural fallback named in the spec. Asserted *in addition to* the token comparison above,
    # never instead of it — it is a drift detector, not a weaker substitute.
    colors = [e["c"] for e in r["cells"]]
    check(len(set(colors)) == 2,
          "exactly one of the three `Adjustments` cells differs from the other two", colors)
    check("target met" not in r["text"],
          "NEGATIVE: the retired ' · target met' suffix appears nowhere in [L-15]", r["text"][:400])


# ---------------------------------------------------------------- QA-RES -----

def open_search_pane(page):
    page.evaluate("QA.clickText('.subtabs button','Stock History')")


@scenario("QA-RES-01")
def res01(page):
    open_search_pane(page)
    r = page.evaluate("""() => {
      const card = [...document.querySelectorAll('#p-search .card')].find(c=>QA.t(c.querySelector('h4')).includes('Stock Status'));
      const nums = [...card.querySelectorAll('.bignum')].map(b=>({n: QA.t(b.querySelector('.n')), l: QA.t(b.querySelector('.l'))}));
      const link = card.querySelector('span.reslink');
      const cs = link ? getComputedStyle(link) : null;
      return {nums, linkTxt: link ? QA.t(link) : null,
              deco: cs ? cs.textDecorationStyle : null, line: cs ? cs.textDecorationLine : null,
              note: QA.t(card.querySelector('p'))};}""")
    check(r["nums"] == [{"n": "42", "l": "Total Qty"}, {"n": "8", "l": "Reserved Qty"}, {"n": "34", "l": "Available Qty"}],
          "42/Total Qty, 8/Reserved Qty, 34/Available Qty", r["nums"])
    check(r["linkTxt"] == "8" and r["deco"] == "dotted" and "underline" in (r["line"] or ""),
          "the 8 wrapped in span.reslink with dotted underline", r)
    check(r["note"] == "Click Reserved → allocated orders modal (incl. releasing phantom orders · restock)",
          "card note text", r["note"])


@scenario("QA-RES-02")
def res02(page):
    open_search_pane(page)
    page.click("span.reslink")
    r = page.evaluate("""() => {
      const m = document.getElementById('m-reserved');
      const b = m.querySelector('header b');
      return {open: m.classList.contains('open'), head: QA.t(m.querySelector('header')),
              bTxt: b ? QA.norm(b.textContent) : null,
              cols: [...m.querySelectorAll('thead th')].map(t=>QA.t(t))};}""")
    check(r["open"], "#m-reserved gains class open", r)
    check(r["head"] == "Reserved Quantity — Dongkook 마데카솔 크림 50ml (100004819) · 8 reserved",
          "header exactly (normalised per §8.0 3b)", r["head"])
    check(r["bTxt"] == "Dongkook", "'Dongkook' inside a <b>", r["bTxt"])
    check(r["cols"] == ["Order ID", "Order Date", "Customer", "Status", "Reserved Qty", "Reserved At", "Action"],
          "table header exact", r["cols"])


@scenario("QA-RES-03")
def res03(page):
    open_modal_via_wfbar(page, "Modal: Reserved Orders")
    r = page.evaluate("""() => [...document.querySelectorAll('#m-reserved tbody tr')].map(row=>({
        cells: [...row.cells].slice(0,6).map(c=>QA.t(c)),
        bg: getComputedStyle(row).backgroundColor,
        phantom: /SUSPECTED PHANTOM/.test(row.cells[3].textContent),
        btnBorder: getComputedStyle(row.querySelector('td:last-child button')).borderTopColor}))""")
    check(len(r) == 3, "exactly three body rows", r)
    expect = [["407812", "2026-06-30", "Sarah Kim", "processing", "2", "07-12 11:05"],
              ["413650", "2026-07-08", "Emma Park", "processing", "3", "07-08 14:22"]]
    check([x["cells"] for x in r[:2]] == expect, "rows 1-2 values", [x["cells"] for x in r[:2]])
    c3 = r[2]["cells"]
    check(c3[0] == "409112" and c3[1] == "2026-07-02" and c3[2] == "Liam Chen"
          and c3[3].startswith("cancelled") and c3[4] == "3" and c3[5] == "07-02 09:10",
          "row 3 = 409112 / 2026-07-02 / Liam Chen / cancelled / 3 / 07-02 09:10", c3)
    check(r[2]["bg"] == COLORS["ambersoft"] and r[0]["bg"] != COLORS["ambersoft"] and r[1]["bg"] != COLORS["ambersoft"],
          "only 409112 row background rgb(255, 243, 224)", [x["bg"] for x in r])
    check(r[2]["phantom"] and not r[0]["phantom"] and not r[1]["phantom"],
          "only 409112 carries SUSPECTED PHANTOM", [x["phantom"] for x in r])
    check(r[2]["btnBorder"] == COLORS["red"] and r[0]["btnBorder"] != COLORS["red"] and r[1]["btnBorder"] != COLORS["red"],
          "only 409112 Cancel Inbound has red border rgb(220, 53, 69)", [x["btnBorder"] for x in r])


@scenario("QA-RES-04")
def res04(page):
    open_modal_via_wfbar(page, "Modal: Reserved Orders")
    note = page.evaluate("QA.t(document.querySelector('#m-reserved .note'))")
    exp = ("Total 8 = 2+3+3 · Suspected phantom = the order is cancelled/refunded but the reservation "
           "was never released — release target. If reservation-order mismatches persist, investigate "
           "unconfirmed events with the Pending confirm filter in Stock History (linked to Dean's report).")
    check(note == exp, "note exactly", note)
    check(2 + 3 + 3 == 8, "2+3+3 reconciles with header count 8", "2+3+3=8")


@scenario("QA-RES-05")
def res05(page):
    open_modal_via_wfbar(page, "Modal: Reserved Orders")
    page.evaluate("""() => {
      const row = [...document.querySelectorAll('#m-reserved tbody tr')].find(r=>QA.t(r.cells[0])==='409112');
      row.querySelector('button[data-modal]').click();}""")
    r = page.evaluate("""() => {
      const m = document.getElementById('m-resrelease');
      const steps = [...m.querySelectorAll('.body > b, .body > div > b')].map(b=>QA.norm(b.textContent));
      const radios = [...m.querySelectorAll('input[name=resback]')];
      const labels = radios.map(x=>QA.t(x.closest('label')));
      const qty = [...m.querySelectorAll('.body input')].find(i=>i.type!=='radio');
      const hint = qty ? QA.norm(qty.nextElementSibling.textContent) : null;
      const memo = m.querySelector('textarea');
      return {open: m.classList.contains('open'), head: QA.t(m.querySelector('header')),
        steps, nRadios: radios.length, firstChecked: radios[0] ? radios[0].checked : null,
        secondChecked: radios[1] ? radios[1].checked : null, labels,
        qtyVal: qty ? qty.value : null, hint, memoPh: memo ? memo.placeholder : null};}""")
    check(r["open"], "#m-resrelease gains class open", r["open"])
    check(r["head"] == "Cancel Inbound — Order 409112 · Dongkook 마데카솔 크림 × 3",
          "header exactly (normalised per §8.0 3b)", r["head"])
    steps = ["1. Release the reservation (Reserved) on this order?", "2. Restock the units?",
             "3. Restock Qty", "4. Memo (Optional)"]
    check(all(s in r["steps"] for s in steps), "four bold numbered steps present " + str(steps), r["steps"])
    check(r["nRadios"] == 2 and r["firstChecked"] is True and r["secondChecked"] is False,
          "two input[name=resback]; first checked by default", r)
    check(r["labels"][0] == "Yes — Available +3 (restock)"
          and r["labels"][1] == "No — exclude from stock (damaged · lost etc., record the loss as ADJUST(−3))",
          "radio labels exact", r["labels"])
    check(r["qtyVal"] == "3" and r["hint"] == "Default = qty originally inbounded (editable)",
          "Restock Qty holds 3 with hint", r)
    check(r["memoPh"] == "Cancellation reason or notes — if written, also recorded in the order's Comments history",
          "memo placeholder exact", r["memoPh"])


@scenario("QA-RES-06")
def res06(page):
    open_modal_via_wfbar(page, "Modal: Cancel Inbound (Release Reservation)")
    r = page.evaluate("""() => ({
      note: QA.t(document.querySelector('#m-resrelease .note')),
      foot: [...document.querySelectorAll('#m-resrelease .foot button')].map(b=>QA.t(b))})""")
    # Rewritten 2026-08-08 ([L-20], spec §8 QA-RES-06): the note gained a third sentence naming
    # the `Release` source, so that the ADJUST row this path writes is distinguishable from the
    # one [L-19] writes. The trailing `[19]` is a legend reference — wireframe chrome that must
    # not ship — and its absence in production is QA-ADJ-25's job, not this row's.
    RELEASE_SENTENCE = ('A "No" choice additionally records ADJUST with source Release '
                        "— distinct from a Manual adjustment [19].")
    exp = ('On release, Reserved 8 → 5; choosing "Yes" brings Available 34 → 37. '
           "The action is recorded in Stock History as a RESERVE release event. "
           + RELEASE_SENTENCE)
    check(RELEASE_SENTENCE in r["note"], "note states the Release source sentence", r["note"])
    check(r["note"] == exp, "note exactly", r["note"])
    check(r["foot"] == ["Cancel", "Confirm"], "footer exactly two buttons Cancel / Confirm", r["foot"])


# ---------------------------------------------------------------- QA-HIS -----

@scenario("QA-HIS-01")
def his01(page):
    open_search_pane(page)
    r = page.evaluate("""() => {
      const bar = document.querySelector('#p-search .searchbar');
      return {opts: [...bar.querySelector('select.sel').options].map(o=>QA.norm(o.textContent)),
              val: bar.querySelector('input.inp').value, ph: bar.querySelector('input.inp').placeholder,
              btn: QA.t(bar.querySelector('button'))};}""")
    check(r["opts"] == ["SKU", "Product Name", "Order ID", "Tracking No"], "select keys exact", r["opts"])
    check(r["val"] == "100004819" and r["ph"] == "Enter SKU (e.g. 100004819)",
          "term input value/placeholder", r)
    check(r["btn"] == "🔍 Search", "button reads '🔍 Search'", r["btn"])


@scenario("QA-HIS-03")
def his03(page):
    open_search_pane(page)
    r = page.evaluate("""() => {
      const card = [...document.querySelectorAll('#p-search .card')].find(c=>QA.t(c.querySelector('h4')).includes('Product Information'));
      const kv = [...card.querySelectorAll('.kv')].map(x=>({k: QA.t(x.querySelector('.k')), v: QA.t(x.children[1])}));
      const krb = [...card.querySelectorAll('.kv')].find(x=>QA.t(x.querySelector('.k'))==='Name KR').children[1].querySelector('b');
      const tag = card.querySelector('.tag-smartbuy');
      const cs = tag ? getComputedStyle(tag) : null;
      return {kv, krb: krb ? QA.norm(krb.textContent) : null,
              tagBg: cs ? cs.backgroundColor : null, tagFw: cs ? cs.fontWeight : null};}""")
    kv = {e["k"]: e["v"] for e in r["kv"]}
    check(kv.get("SKU") == "100004819", "SKU 100004819", kv)
    check(kv.get("Name") == "Madecassol Cream 50ml", "Name Madecassol Cream 50ml", kv)
    check(kv.get("Name KR") == "Dongkook 마데카솔 크림" and r["krb"] == "Dongkook",
          "Name KR renders Dongkook in <b> + 마데카솔 크림", r)
    check(kv.get("Brand") == "Dongkook", "Brand Dongkook", kv)
    check(kv.get("Sourcing Route") == "SMART BUY" and r["tagBg"] in ("rgba(0, 0, 0, 0)", "transparent")
          and r["tagFw"] == "800", "Sourcing Route SMART BUY transparent-bg bold", r)


@scenario("QA-HIS-04")
def his04(page):
    open_search_pane(page)
    r = page.evaluate("""() => {
      const card = [...document.querySelectorAll('#p-search .card')].find(c=>QA.t(c.querySelector('h4')).includes('By Location'));
      const rows = [...card.querySelectorAll('.loc-row')].map(x=>({pill: QA.t(x.querySelector('.loc-pill')), qty: QA.t(x.querySelector('.num'))}));
      return {rows, note: QA.t(card.querySelector('p'))};}""")
    check(len(r["rows"]) == 1, "exactly one .loc-row", r["rows"])
    check(r["rows"][0] == {"pill": "A-02-13", "qty": "42"}, "A-02-13 / 42", r["rows"][0])
    check("One location per SKU — change locations via the Current Stocks input field" in r["note"],
          "note text", r["note"])


HIS_ROWS = [("INBOUND", "+6", "PENDING"), ("OUTBOUND", "−2", "CONFIRMED"),
            ("RESERVE", "−8", "CONFIRMED"), ("INBOUND", "+30", "CONFIRMED"),
            ("ADJUST", "−1", "CONFIRMED"), ("INBOUND", "+12", "CONFIRMED")]


@scenario("QA-HIS-05")
def his05(page):
    open_search_pane(page)
    # Rewritten 2026-08-08 ([L-20], spec §8 QA-HIS-05). The `Type` cell of the ADJUST row now
    # holds a second child, `span.src-note`, so the old whole-cell equality failed by
    # construction. The row census is re-anchored on `span.ty` — the badge itself — which keeps
    # it strict: a badge whose label, or whose presence, regresses still fails, and a row that
    # loses its badge yields '' and fails too. The source trail is asserted separately below so
    # that losing it names this scenario rather than silently passing.
    r = page.evaluate("""() => {
      const tbl = document.querySelector('#p-search .tbl');
      const rows = [...tbl.querySelectorAll('tbody tr')];
      const badge = tbl.querySelector('tbody span.ty-adj');
      const adjCell = badge ? badge.closest('td') : null;
      return {head: [...tbl.querySelectorAll('thead th')].map(t=>QA.t(t)),
              rows: rows.map(row=>[QA.t(row.cells[0].querySelector('span.ty')),
                                   QA.t(row.cells[1]), QA.t(row.cells[2])]),
              nBadge: rows.map(row=>row.cells[0].querySelectorAll('span.ty').length),
              adjSrc: adjCell && adjCell.querySelector('span.src-note')
                        ? QA.t(adjCell.querySelector('span.src-note')) : null};}""")
    check(r["head"] == ["Type", "Quantity", "Status", "Tracking No", "Carrier", "Location", "Order ID", "Created At", "Auditor"],
          "events table header exact — nine columns, no Reason and no Source column", r["head"])
    check(all(n == 1 for n in r["nBadge"]), "every Type cell holds exactly one span.ty", r["nBadge"])
    got = [tuple(x) for x in r["rows"]]
    check(got == HIS_ROWS, "six body rows in order (type read off span.ty) " + str(HIS_ROWS), got)
    check(r["adjSrc"] == "Audit #2026-07",
          "the ADJUST row's Type cell carries span.src-note reading 'Audit #2026-07'", r["adjSrc"])


@scenario("QA-HIS-06")
def his06(page):
    open_search_pane(page)
    r = page.evaluate("""() => {
      const rows = [...document.querySelectorAll('#p-search .tbl tbody tr')];
      const pend = rows.filter(r=>r.classList.contains('pending'));
      const p = pend[0];
      return {nPend: pend.length,
        cells: p ? [...p.cells].map(c=>QA.t(c)) : null,
        bg: p ? getComputedStyle(p).backgroundColor : null,
        badges: rows.map(r=>QA.t(r.cells[2]))};}""")
    check(r["nPend"] == 1, "only one tr.pending", r["nPend"])
    c = r["cells"]
    check(c[0] == "INBOUND" and c[1] == "+6" and c[3] == "12101316464794" and c[4] == "Coupang"
          and c[6] == "407847" and c[8] == "Miranti",
          "pending row = INBOUND +6, tracking 12101316464794, Coupang, 407847, Miranti", c)
    check(r["bg"] == COLORS["ambersoft"], "amber background rgb(255, 243, 224)", r["bg"])
    check(r["badges"] == ["PENDING", "CONFIRMED", "CONFIRMED", "CONFIRMED", "CONFIRMED", "CONFIRMED"],
          "PENDING badge on it, CONFIRMED on the five others", r["badges"])


@scenario("QA-HIS-07")
def his07(page):
    open_search_pane(page)
    r = page.evaluate("""() => {
      const p = document.querySelector('#p-search .tbl tbody tr.pending');
      return {btn: p.querySelectorAll('button').length, a: p.querySelectorAll('a').length,
              cb: p.querySelectorAll('input[type=checkbox]').length,
              inputs: p.querySelectorAll('input,select,textarea').length};}""")
    check(r["btn"] == 0 and r["a"] == 0 and r["cb"] == 0 and r["inputs"] == 0,
          "PENDING row contains no button/a/checkbox/other affordance", r)


@scenario("QA-HIS-08")
def his08(page):
    open_search_pane(page)
    r = page.evaluate("""() => [...document.querySelectorAll('#p-search .filterchip')]
        .map(b=>({t: QA.t(b), on: b.classList.contains('on')}))""")
    check([e["t"] for e in r] == ["All", "Confirmed", "Pending confirm"],
          "exactly three chips All / Confirmed / Pending confirm", r)
    check([e["on"] for e in r] == [True, False, False], "only 'All' has class on", r)


@scenario("QA-HIS-15")
def his15(page):
    open_search_pane(page)
    r = page.evaluate("""() => [...document.querySelectorAll('#p-search .tbl tbody tr')].map(row=>QA.t(row.cells[7]))""")
    expect = ["07-13 09:12", "07-12 18:40", "07-12 11:05", "07-10 14:22", "07-09 16:50", "07-08 10:11"]
    check(r == expect, "Created At cells " + str(expect), r)
    check(all(re.fullmatch(r"\d{2}-\d{2} \d{2}:\d{2}", x) for x in r), "compact MM-DD HH:MM form", r)


@scenario("QA-HIS-18")
def his18(page):
    open_search_pane(page)
    # Rewritten 2026-08-08 ([L-20], spec §8 QA-HIS-18). The ADJUST row is now resolved through
    # `span.ty-adj`.closest('tr'); the old text match on the whole `Type` cell stopped resolving
    # the moment the cell gained `span.src-note`. Anchoring on the badge class is not a
    # weakening — a row that loses the badge, or a badge that lands on the wrong row, leaves
    # `adj` null and every clause below fails.
    r = page.evaluate("""() => {
      const tbl = document.querySelector('#p-search .tbl');
      const rows = [...tbl.querySelectorAll('tbody tr')];
      const census = {};
      rows.forEach(row=>{const b=row.cells[0].querySelector('.ty');
        const cls=b ? [...b.classList].find(c=>c.startsWith('ty-')) : 'MISSING';
        census[QA.t(b)+'/'+cls]=(census[QA.t(b)+'/'+cls]||0)+1;});
      const badge = tbl.querySelector('tbody span.ty-adj');
      const adj = badge ? badge.closest('tr') : null;
      const srcs = [...tbl.querySelectorAll('tbody span.src-note')];
      return {census,
              adjQty: adj ? QA.t(adj.cells[1]) : null,
              adjQtyClass: adj ? [...adj.cells[1].classList] : null,
              adjQtyInner: adj ? !!adj.cells[1].querySelector('.diff-neg') : null,
              nSrc: srcs.length, srcTxt: srcs.map(s=>QA.t(s)),
              srcInAdjCell: !!adj && srcs.length === 1 && srcs[0].closest('td') === adj.cells[0]};}""")
    check(r["census"] == {"INBOUND/ty-in": 3, "OUTBOUND/ty-out": 1, "RESERVE/ty-res": 1, "ADJUST/ty-adj": 1},
          "badge census INBOUND×3(ty-in) OUTBOUND×1 RESERVE×1 ADJUST×1", r["census"])
    check(r["adjQty"] == "−1", "the span.ty-adj row is the −1 row", r["adjQty"])
    check("diff-neg" in (r["adjQtyClass"] or []) or r["adjQtyInner"],
          "ADJUST −1 quantity carries diff-neg class", r)
    check(r["nSrc"] == 1 and r["srcTxt"] == ["Audit #2026-07"] and r["srcInAdjCell"],
          "exactly one span.src-note in the table, inside the ADJUST Type cell, "
          "reading 'Audit #2026-07'", r)


# ---------------------------------------------------------------- QA-FRM -----

FRM_LABELS = ["SKU *", "Quantity *", "Tracking No", "Carrier", "Order ID (optional)"]


@scenario("QA-FRM-01")
def frm01(page):
    page.evaluate("QA.clickText('.subtabs button','Inbound Stock')")
    r = page.evaluate("""() => ({
      labels: [...document.querySelectorAll('#p-inbound .fld label')].map(l=>QA.t(l)),
      carrier: [...document.querySelectorAll('#p-inbound .fld select')[0].options].map(o=>QA.norm(o.textContent)),
      btn: QA.t(document.querySelector('#p-inbound > button'))})""")
    check(r["labels"] == FRM_LABELS, "five .fld labels exact " + str(FRM_LABELS), r["labels"])
    check(r["carrier"] == ["Coupang", "Deleo", "Direct"], "Carrier offers Coupang/Deleo/Direct", r["carrier"])
    check(r["btn"] == "＋ Record Inbound", "submit reads '＋ Record Inbound'", r["btn"])


@scenario("QA-FRM-02")
def frm02(page):
    r = page.evaluate("""() => [...document.querySelectorAll('#p-inbound .fld label, #p-outbound .fld label')]
        .map(l=>QA.t(l)).filter(t=>t==='Location')""")
    check(r == [], "no field labelled 'Location' on either form", r)


@scenario("QA-FRM-03")
def frm03(page):
    page.evaluate("QA.clickText('.subtabs button','Inbound Stock')")
    note = page.evaluate("QA.t(document.querySelector('#p-inbound .form-note'))")
    exp = ("Record a warehouse inbound directly, without a specific order (return restock · manual inbound). "
           "Location auto-applies the SKU's single registered location. For order-linked inbound, "
           "use the row Inbound buttons on View Orders or Order Detail.")
    check(note == exp, "form-note exactly [INV-WFX-2 applied wording]", note)


@scenario("QA-FRM-08")
def frm08(page):
    page.evaluate("QA.clickText('.subtabs button','Outbound Stock')")
    r = page.evaluate("""() => ({
      labels: [...document.querySelectorAll('#p-outbound .fld label')].map(l=>QA.t(l)),
      carrier: [...document.querySelectorAll('#p-outbound .fld select')[0].options].map(o=>QA.norm(o.textContent)),
      btn: QA.t(document.querySelector('#p-outbound > button')),
      note: QA.t(document.querySelector('#p-outbound .form-note'))})""")
    check(r["labels"] == FRM_LABELS, "five fields in the same order as [L-F2]", r["labels"])
    check(r["carrier"] == ["Deleo", "YUN", "Coupang"], "Carrier offers Deleo/YUN/Coupang", r["carrier"])
    check(r["btn"] == "－ Record Outbound", "button reads '－ Record Outbound'", r["btn"])
    exp = ("Record a warehouse outbound directly. Location auto-applies the SKU's registered location; "
           "outbound exceeding Available Qty is blocked.")
    check(r["note"] == exp, "form-note exactly", r["note"])


@scenario("QA-FRM-19")
def frm19(page):
    r = page.evaluate("""() => ['p-inbound','p-outbound'].map(id=>{
      const pane = document.getElementById(id);
      const sels = [...pane.querySelectorAll('select')];
      const carrierFld = [...pane.querySelectorAll('.fld')].find(f=>QA.t(f.querySelector('label'))==='Carrier');
      const sel = carrierFld ? carrierFld.querySelector('select') : null;
      return {id, nSel: sels.length, hasCarrierSel: !!sel,
        disabled: sel ? sel.disabled : null, readonly: sel ? sel.hasAttribute('readonly') : null};})""")
    for e in r:
        check(e["nSel"] == 1 and e["hasCarrierSel"], f"{e['id']}: exactly one Carrier <select>", e)
        check(not e["disabled"] and not e["readonly"],
              f"{e['id']}: carrier select operator-choosable (not disabled/readonly)", e)


# ---------------------------------------------------------------- QA-COM -----

def open_hub(page):
    page.click('[data-open="inbox1"]')


@scenario("QA-COM-01")
def com01(page):
    r0 = page.evaluate("""() => {
      const b = document.querySelector('[data-open="inbox1"]');
      return {txt: QA.norm(b.childNodes[0].textContent), badge: QA.t(b.querySelector('.badge-n'))};}""")
    check(r0["txt"] == "💬 Comments" and r0["badge"] == "3", "nav button '💬 Comments' with red badge '3'", r0)
    open_hub(page)
    r = page.evaluate("""() => {
      const dd = document.getElementById('inbox1');
      const tab = [...dd.querySelectorAll('.tabs button')].find(b=>QA.t(b).startsWith('@ Mentions'));
      const its = [...dd.querySelectorAll('[data-pane="mentions"] .it.unread')]
        .map(i=>QA.norm(i.querySelector('b').textContent));
      return {open: dd.classList.contains('open'), tabOn: tab.classList.contains('on'), its};}""")
    check(r["open"] and r["tabOn"], "#inbox1 open, '@ Mentions' tab on", r)
    check(r["its"] == ["Order 409112", "Order 407847", "Order 407506"],
          "exactly three .it.unread for 409112/407847/407506", r["its"])


@scenario("QA-COM-02")
def com02(page):
    open_hub(page)
    page.evaluate("QA.clickText('#inbox1 .tabs button','★ Saved')")
    r = page.evaluate("""() => {
      const dd = document.getElementById('inbox1');
      const men = dd.querySelector('[data-pane="mentions"]');
      const sav = dd.querySelector('[data-pane="saved"]');
      return {menDisp: getComputedStyle(men).display, savDisp: getComputedStyle(sav).display,
        entries: [...sav.querySelectorAll('.it')].map(i=>QA.norm(i.querySelector('b').textContent)),
        head: QA.t(sav.querySelector('.paneheader'))};}""")
    check(r["menDisp"] == "none" and r["savDisp"] == "block", "mentions pane hides, saved shows", r)
    check(r["entries"] == ["Order 407847"], "exactly one saved entry (Order 407847)", r["entries"])
    check("Saved comments · Click to open the order" in r["head"], "pane header text", r["head"])


@scenario("QA-COM-03")
def com03(page):
    open_hub(page)
    r0 = page.evaluate("""() => [...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
        .map(i=>({o: QA.norm(i.querySelector('b').textContent), on: i.querySelector('.star').classList.contains('on')}))""")
    check(r0 == [{"o": "Order 409112", "on": False}, {"o": "Order 407847", "on": True}, {"o": "Order 407506", "on": False}],
          "407847 star on; 409112/407506 stars off", r0)
    star = page.locator('#inbox1 [data-pane="mentions"] .it', has_text="409112").locator(".star")
    star.click()
    on1 = page.evaluate("""[...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')].find(i=>/409112/.test(i.textContent)).querySelector('.star').classList.contains('on')""")
    check(on1, "409112 star gains on after click", on1)
    star.click()
    on2 = page.evaluate("""[...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')].find(i=>/409112/.test(i.textContent)).querySelector('.star').classList.contains('on')""")
    check(not on2, "409112 star loses on after second click", on2)


@scenario("QA-COM-04")
def com04(page):
    open_hub(page)
    page.fill("#inbox1 .csearch input", "phantom")
    r = page.evaluate("""() => {
      const dd = document.getElementById('inbox1');
      const pane = dd.querySelector('[data-pane="csr"]');
      return {tabsDisp: getComputedStyle(dd.querySelector('.tabs')).display,
        head: QA.t(pane.querySelector('.paneheader')),
        its: [...pane.querySelectorAll('.it')].map(i=>QA.norm(i.querySelector('b').textContent)),
        mark: pane.querySelector('mark') ? QA.norm(pane.querySelector('mark').textContent) : null};}""")
    check(r["tabsDisp"] == "none", ".tabs bar is hidden", r["tabsDisp"])
    check(r["head"] == "1 results · newest first · click to open the order", "header exactly", r["head"])
    check(r["its"] == ["Order 409112"], "exactly one .it (Order 409112)", r["its"])
    check(r["mark"] == "phantom", "'phantom' wrapped in <mark>", r["mark"])


@scenario("QA-COM-05")
def com05(page):
    open_hub(page)
    page.fill("#inbox1 .csearch input", "zzzz")
    r = page.evaluate("""() => {
      const pane = document.querySelector('#inbox1 [data-pane="csr"]');
      return {empty: QA.t(pane.querySelector('.empty')), head: QA.t(pane.querySelector('.paneheader'))};}""")
    check(r["empty"] == "No matching comments", ".empty exactly 'No matching comments'", r["empty"])
    check(r["head"] == "0 results · newest first · click to open the order",
          ".paneheader exactly '0 results · newest first · click to open the order'", r["head"])
    page.fill("#inbox1 .csearch input", "")
    r2 = page.evaluate("""() => {
      const dd = document.getElementById('inbox1');
      return {tabs: getComputedStyle(dd.querySelector('.tabs')).display,
        mentions: getComputedStyle(dd.querySelector('[data-pane="mentions"]')).display,
        csr: getComputedStyle(dd.querySelector('[data-pane="csr"]')).display};}""")
    check(r2["tabs"] == "flex" and r2["mentions"] == "block" and r2["csr"] == "none",
          "tabs reappear, previously active pane (mentions) restored", r2)


@scenario("QA-COM-12")
def com12(page):
    open_hub(page)
    page.fill("#inbox1 .csearch input", "Dean")
    r = page.evaluate("""() => {
      const pane = document.querySelector('#inbox1 [data-pane="csr"]');
      return {head: QA.t(pane.querySelector('.paneheader')),
        its: [...pane.querySelectorAll('.it')].map(i=>QA.norm(i.querySelector('b').textContent))};}""")
    check(r["head"] == "2 results · newest first · click to open the order", "header reads 2 results", r["head"])
    check(r["its"] == ["Order 409112", "Order 407812"], "entries newest-first: 409112 then 407812", r["its"])


@scenario("QA-COM-14")
def com14(page):
    open_hub(page)
    page.fill("#inbox1 .csearch input", "<b>x</b>")
    r = page.evaluate("""() => {
      const pane = document.querySelector('#inbox1 [data-pane="csr"]');
      return {nB: pane.querySelectorAll('b').length, txt: QA.t(pane)};}""")
    check(r["nB"] == 0, "no bold element created inside the result pane (HTML-escaped)", r)


# ---------------------------------------------------------------- QA-EXP -----

@scenario("QA-EXP-01")
def exp01(page):
    r = page.evaluate("""() => {
      const h = [...document.querySelectorAll('.ptitle button')].map(b=>({t: QA.t(b), gray: b.classList.contains('btn-gray')}));
      const c = [...document.querySelectorAll('.cs-controls button')].map(b=>({t: QA.t(b), gray: b.classList.contains('btn-gray')}));
      return {h, c};}""")
    hh = [e for e in r["h"] if e["t"] == "⬇ Export Stock Status"]
    cc = [e for e in r["c"] if e["t"] == "⬇ Export"]
    check(len(hh) == 1 and hh[0]["gray"], "page-header button exactly '⬇ Export Stock Status', grey", r["h"])
    check(len(cc) == 1 and cc[0]["gray"], ".cs-controls button exactly '⬇ Export', grey", r["c"])


# ---------------------------------------------------------------- QA-GLB -----

@scenario("QA-GLB-08")
def glb08(page):
    n_scanfeed = page.evaluate("""[...document.querySelectorAll('*')]
        .filter(e => /scan|feed/i.test(e.id||'') || /scan|feed/i.test(e.getAttribute('class')||'')).length""")
    check(n_scanfeed == 0, "clause 1: zero elements with id/class matching /scan|feed/i", n_scanfeed)
    for scope, txt in sweep_texts(page):
        check(not re.search(r"scan", txt, re.I), f"clause 2: no /scan/i in innerText ({scope})", txt[:200])
    # clause 3 — per the spec's own definition: focus returning WITHOUT a user gesture is the
    # failure mode; an input merely retaining focus is explicitly not forbidden.
    go_pane(page, "Current Stocks (default)")
    bc = page.locator("#p-current tbody tr:not(.audrow) .bcin")
    bc.click()
    page.keyboard.type("8809738317481")
    page.keyboard.press("Enter")
    lit1 = page.evaluate("document.activeElement && document.activeElement.classList.contains('bcin')")
    page.click(".ptitle h2")  # user gesture moves focus away
    page.wait_for_timeout(400)
    r1 = page.evaluate("document.activeElement && document.activeElement.classList.contains('bcin')")
    check(not r1, "clause 3a: focus does not return to a .bcin without a user gesture "
          f"(literal post-Enter activeElement-is-bcin={lit1}: retained focus, allowed per definition)", r1)
    enter_audit(page)
    page.click("#auSearch")
    page.keyboard.type("zzzz")
    page.keyboard.press("Enter")
    lit2 = page.evaluate("document.activeElement && document.activeElement.classList.contains('bcin')")
    page.click(".ptitle h2")
    page.wait_for_timeout(400)
    r2 = page.evaluate("document.activeElement && document.activeElement.classList.contains('bcin')")
    check(not r2, "clause 3b: #auSearch — no gesture-free refocus "
          f"(literal post-Enter={lit2}: retained focus, allowed per definition)", r2)


def collect_full_text(page):
    texts = [t for _, t in sweep_texts(page)]
    go_pane(page, "Current Stocks (default)")
    enter_audit(page)
    texts.append(page.evaluate("QA.t(document.querySelector('.mock'))"))
    return texts


@scenario("QA-GLB-09")
def glb09(page):
    texts = collect_full_text(page)
    bad = []
    for txt in texts:
        for run in re.findall(r"[가-힣]+", txt):
            if not any(run in allow for allow in KO_ALLOW):
                bad.append(run)
    check(bad == [], "every Hangul run is a substring of one of the 16 allow-listed strings "
                     "(17 → 16 on 2026-08-04: `신규` lived only in the retired Loss cells)", bad)
    chrome = page.evaluate("""[...document.querySelectorAll('th,label,button,h2,h4,.paneheader,.form-note')]
        .map(e=>e.textContent).filter(t=>/[\\uac00-\\ud7a3]/.test(t))""")
    check(chrome == [], "no Hangul inside th/label/button/h2/h4/.paneheader/.form-note", chrome)


@scenario("QA-GLB-11")
def glb11(page):
    """NEGATIVE — money must NOT exist anywhere on this page.

    Was a money-census assertion (10 ₩ tokens, thousands separators, explicit signs). The owner
    removed money from the stock audit on 2026-08-04: the audit reports quantity differences only.
    Since every money value on this page belonged to the audit, the census inverted into a
    page-wide must-NOT-exist. Money that is NOT audit loss — Inbound Request `Unit Cost` /
    `JIT Price`, Order Detail order totals — lives on other pages and other runners, and is
    deliberately untouched.
    """
    texts = collect_full_text(page)
    hits = []
    for txt in texts:
        for m in MONEY_FORBIDDEN.finditer(txt):
            lo = max(0, m.start() - 40)
            hits.append(txt[lo:m.end() + 40])
    check(hits == [], "no ₩ / KRW / $ / USD / 'product cost' / 'Loss (' anywhere on the page "
                      "or in any of its six modals", hits)
    # Positive counterpart: the audit still reports its outcome — as counts (spec [E-72]).
    # Signed counts (−1, +2) are not money and must survive the negative above.
    joined = " ".join(texts)
    check("Adjustments: 2 (−1 / +2)" in joined,
          "the audit still reports its outcome, as signed counts rather than money", joined[:300])


@scenario("QA-GLB-12")
def glb12(page):
    pat = re.compile(r"\b(edit|delete|reverse|undo|re-?open)\b", re.I)
    bad = []
    for lbl in PANE_WF:
        go_pane(page, lbl)
        names = page.evaluate("""[...document.querySelectorAll('.mock button, .mock a')]
            .filter(QA.vis).map(e=>QA.norm((e.innerText||'')+' '+(e.title||'')+' '+(e.getAttribute('aria-label')||'')))""")
        bad += [(lbl, n) for n in names if pat.search(n)]
    for lbl in MODAL_WF:
        open_modal_via_wfbar(page, lbl)
        names = page.evaluate("""[...document.querySelectorAll('.overlay.open button, .overlay.open a')]
            .map(e=>QA.norm((e.innerText||'')+' '+(e.title||'')+' '+(e.getAttribute('aria-label')||'')))""")
        bad += [(lbl, n) for n in names if pat.search(n)]
        page.evaluate("[...document.querySelectorAll('.overlay.open [data-close]')][0].click()")
    check(bad == [], "no edit/delete/reverse/undo/re-open control in any pane or modal", bad)


@scenario("QA-GLB-13")
def glb13(page):
    page.set_viewport_size({"width": 900, "height": 800})
    preflight(page)  # reload at the new viewport with preflight
    r = page.evaluate("""() => {
      const de = document.documentElement, mw = document.querySelector('.mockwrap'),
            mk = document.querySelector('.mock');
      const ths = [...document.querySelectorAll('#p-current thead th')].filter(t=>getComputedStyle(t).display!=='none');
      return {docSW: de.scrollWidth, docCW: de.clientWidth,
        mwOX: getComputedStyle(mw).overflowX, mwSW: mw.scrollWidth, mwCW: mw.clientWidth,
        mockMinW: getComputedStyle(mk).minWidth,
        nTh: ths.length, hasAvail: ths.some(t=>QA.t(t)==='Available')};}""")
    check(r["docSW"] <= r["docCW"], "page body never scrolls horizontally (scrollWidth <= clientWidth)",
          {"scrollWidth": r["docSW"], "clientWidth": r["docCW"]})
    check(r["mwOX"] == "auto" and r["mwSW"] > r["mwCW"],
          ".mockwrap overflow-x auto and scrolls internally", r)
    check(r["mockMinW"] == "1140px", ".mock min-width 1140px", r["mockMinW"])
    check(r["nTh"] == 11 and r["hasAvail"], "all eleven visible th incl. Available", r)


# ---------------------------------------------------------------- QA-ADJ -----
# [L-19] manual stock adjustment + [L-20] ADJUST source trail, spec §3.22 / §3.23, added
# 2026-08-08. Fifteen [WF] rows here (QA-ADJ-01 – QA-ADJ-15).
#
# QA-ADJ-16 – QA-ADJ-29 stay [ADMIN] in stock-status.md §8 and are deliberately NOT written
# here: each needs something the shipped file does not contain — a persisted event and its
# actor/timestamp (16), FIFO receipt consumption (17), auto-comments and a Slack dispatch (18),
# two builds' controls in one assertion (19), a seven-order reservation (20), a second operator
# and a 409 (21), a network fault (22), a debounce/idempotency key (23), a server-side integer
# ceiling (24), the production admin's own filter and column set (25), a null location record
# (26), a server that owns Total and Reserved at apply (27), requests that bypass the editor
# (28), and a transaction boundary with failing side effects (29). Faking any of them in a
# wireframe runner would produce a green that proves nothing.
#
# Every row below assumes audit mode is OFF — the affordance does not exist while it is on
# (QA-ADJ-14) — and the §8.0 preflight, including norm().

ADJ_SKU = "100004819"        # Madecassol — Total 42, Reserved 8, three holding orders
ADJ_SKU2 = "100031877"       # Beauty of Joseon Glow Serum — Total 88, Reserved 6
ADJ_ROW = '#p-current tbody tr[data-sku="%s"]'
ADJ_REASONS = [("", "Select a reason…"),
               ("Damaged", "Damaged — unsellable through breakage"),
               ("Expired", "Expired — past shelf life or degraded"),
               ("Lost", "Lost — inbound record trusted, goods gone"),
               ("Miscount", "Miscount — the book figure was wrong")]
# Census of the shipped below-Reserved sentence. It names the reserved total (8) where the
# contract is the shortfall (8 − 5 = 3) — `[INV-WFX-3 · proposed]`. Asserted here as a drawing
# of what ships; the contract is asserted at [ADMIN] tier by QA-ADJ-18.
ADJ_WARN_BODY = ("Allowed, but 8 unit(s) are held by orders that can no longer be filled from "
                 "stock. Applying comments on each order and notifies #fulfillment-admin-comments.")


def open_current_pane(page):
    go_pane(page, PANE_WF[0])


def open_adjust(page, sku=ADJ_SKU):
    page.click((ADJ_ROW % sku) + " .tot-edit")


def type_qty(page, value):
    """Enter a quantity through the editor's own 'input' listener."""
    page.fill(".tot-pop .tot-in", value)


def pop_state(page):
    """Everything the open editor asserts on. `open: False` when no editor exists."""
    return page.evaluate("""() => {
      const pop = document.querySelector('.tot-pop');
      if (!pop) return {open: false, n: document.querySelectorAll('.tot-pop').length};
      const sel = pop.querySelector('.tot-rsn'), warn = pop.querySelector('.tot-warn');
      return {open: true, n: document.querySelectorAll('.tot-pop').length,
        hint: QA.t(pop.querySelector('.tot-hint')),
        okDisabled: pop.querySelector('.tot-ok').disabled,
        selVis: QA.vis(sel), selNeed: sel.classList.contains('need'),
        warnVis: QA.vis(warn),
        warnHead: QA.t(warn.querySelector('.wh')),
        warnTxt: QA.t(warn),
        warnItems: [...warn.querySelectorAll('li:not(.more)')].map(li=>QA.t(li)),
        warnMore: [...warn.querySelectorAll('li.more')].map(li=>QA.t(li))};}""")


def row_state(page, sku=ADJ_SKU):
    return page.evaluate("""sku => {
      const row = document.querySelector('#p-current tbody tr[data-sku="'+sku+'"]');
      const cell = row.querySelector('td.tot-cell');
      const cnt = row.querySelector('input.qty-in');
      return {tot: QA.t(cell.querySelector('span.tot-v')),
              orig: cell.dataset.orig, res: cell.dataset.res,
              avail: QA.t(row.querySelectorAll('td')[10]),
              countedLive: cnt ? cnt.value : null,
              countedAttr: cnt ? cnt.getAttribute('value') : null,
              chipVis: QA.vis(cell.querySelector('span.tot-saved')),
              chipTxt: QA.t(cell.querySelector('span.tot-saved')),
              toastVis: QA.vis(document.getElementById('gtoast')),
              nPop: document.querySelectorAll('.tot-pop').length};}""", sku)


@scenario("QA-ADJ-01")
def adj01(page):
    r = page.evaluate("""() => {
      const btns = [...document.querySelectorAll('#p-current tbody .tot-edit')];
      const rows = [...document.querySelectorAll('#p-current tbody tr')]
        .filter(t => !t.classList.contains('audrow'));
      const cell = document.querySelector('#p-current tbody tr[data-sku="100004819"] td.tot-cell');
      return {n: btns.length, nRows: rows.length,
        onAudrow: document.querySelectorAll('#p-current tbody tr.audrow .tot-edit').length,
        vis: btns.filter(QA.vis).length,
        txt: [...new Set(btns.map(b => QA.t(b)))],
        title: [...new Set(btns.map(b => b.title))],
        aria: [...new Set(btns.map(b => b.getAttribute('aria-label')))],
        inCell: btns.every(b => {
          const c = b.closest('td.tot-cell');
          return !!c && !!c.querySelector('span.tot-v');}),
        totMatchesOrig: rows.every(t => {
          const c = t.querySelector('td.tot-cell');
          return !!c && QA.t(c.querySelector('span.tot-v')) === c.dataset.orig;}),
        skus: rows.filter(t => t.dataset.sku).length,
        orig: cell.dataset.orig, res: cell.dataset.res};}""")
    check(r["n"] == 11 and r["nRows"] == 11 and r["onAudrow"] == 0,
          "exactly 11 .tot-edit — one per data row, none on .audrow", r)
    check(r["vis"] == 11, "all 11 rendered with audit mode off", r["vis"])
    check(r["txt"] == ["✎"], "every button's innerText is exactly '✎'", r["txt"])
    check(r["title"] == ["Adjust stock quantity"] and r["aria"] == ["Adjust stock quantity"],
          "title and aria-label both exactly 'Adjust stock quantity'", r)
    check(r["inCell"], "every button sits in a td.tot-cell that also holds span.tot-v", r["inCell"])
    check(r["totMatchesOrig"], "every span.tot-v renders its cell's data-orig", r["totMatchesOrig"])
    check(r["skus"] == 11, "every data row carries data-sku", r["skus"])
    check((r["orig"], r["res"]) == ("42", "8"),
          "SKU 100004819 td.tot-cell data-orig='42' data-res='8'", r)


@scenario("QA-ADJ-02")
def adj02(page):
    open_adjust(page)
    r = page.evaluate("""() => {
      const pop = document.querySelector('.tot-pop');
      const inp = pop.querySelector('input.tot-in');
      return {n: document.querySelectorAll('.tot-pop').length,
        inRowCell: pop.closest('td.tot-cell') ===
          document.querySelector('#p-current tbody tr[data-sku="100004819"] td.tot-cell'),
        type: inp.type, min: inp.getAttribute('min'), val: inp.value,
        okTxt: QA.t(pop.querySelector('button.tot-ok')),
        okDisabled: pop.querySelector('button.tot-ok').disabled,
        noTxt: QA.t(pop.querySelector('button.tot-no')),
        selVis: QA.vis(pop.querySelector('select.tot-rsn')),
        hint: QA.t(pop.querySelector('div.tot-hint')),
        warnVis: QA.vis(pop.querySelector('div.tot-warn')),
        activeIsInput: document.activeElement === inp};}""")
    check(r["n"] == 1 and r["inRowCell"],
          "exactly one div.tot-pop, inside that row's td.tot-cell", r)
    check((r["type"], r["min"], r["val"]) == ("number", "0", "42"),
          "input.tot-in type=number min=0 live value 42", r)
    check(r["okTxt"] == "✓" and r["okDisabled"], "button.tot-ok reads '✓' and is disabled", r)
    check(r["noTxt"] == "✗", "button.tot-no reads '✗'", r["noTxt"])
    check(not r["selVis"], "select.tot-rsn is not visible", r["selVis"])
    check(r["hint"] == "Unchanged", "div.tot-hint reads exactly 'Unchanged'", r["hint"])
    check(not r["warnVis"], "div.tot-warn is not visible", r["warnVis"])
    check(r["activeIsInput"], "document.activeElement is the input.tot-in", r["activeIsInput"])


@scenario("QA-ADJ-03")
def adj03(page):
    open_adjust(page)
    type_qty(page, "45")
    r = pop_state(page)
    check(not r["selVis"], "select.tot-rsn stays not visible on an increase", r["selVis"])
    check(not r["warnVis"], "div.tot-warn stays not visible", r["warnVis"])
    check(not r["okDisabled"], "button.tot-ok becomes enabled with no reason picked", r["okDisabled"])
    check(r["hint"] == "Increase of 3 — recorded as Miscount",
          "hint exactly 'Increase of 3 — recorded as Miscount'", r["hint"])


@scenario("QA-ADJ-04")
def adj04(page):
    open_adjust(page)
    type_qty(page, "20")
    before = pop_state(page)
    check(before["selVis"], "select.tot-rsn becomes visible on a decrease", before["selVis"])
    check(before["okDisabled"], "button.tot-ok is disabled before a reason is picked", before)
    check(before["hint"] == "Decrease of 22 — a reason is required",
          "hint exactly 'Decrease of 22 — a reason is required'", before["hint"])
    page.select_option(".tot-pop .tot-rsn", "Damaged")
    after = pop_state(page)
    check(not after["okDisabled"], "button.tot-ok becomes enabled once Damaged is picked", after)
    check(after["hint"] == before["hint"], "hint unchanged by picking a reason", after["hint"])


@scenario("QA-ADJ-05")
def adj05(page):
    # NEGATIVE — the reason list is closed. No Other, no Wrong SKU, no free text anywhere.
    open_adjust(page)
    type_qty(page, "20")
    r = page.evaluate("""() => {
      const pop = document.querySelector('.tot-pop');
      return {opts: [...pop.querySelectorAll('select.tot-rsn option')]
                      .map(o => [o.value, QA.norm(o.textContent)]),
        nTextarea: pop.querySelectorAll('textarea').length,
        inputs: [...pop.querySelectorAll('input')].map(i => i.className),
        nContentEditable: pop.querySelectorAll('[contenteditable]').length};}""")
    got = [tuple(x) for x in r["opts"]]
    check(got == ADJ_REASONS, "exactly five options " + str(ADJ_REASONS), got)
    bad = [o for o in got if re.search(r"other|wrong sku", o[0] + " " + o[1], re.I)]
    check(bad == [], "no option matches /other/i or /wrong sku/i", bad)
    check(r["nTextarea"] == 0 and r["inputs"] == ["tot-in"] and r["nContentEditable"] == 0,
          "div.tot-pop holds no textarea, no contenteditable and no input but input.tot-in", r)


@scenario("QA-ADJ-06")
def adj06(page):
    open_adjust(page)
    type_qty(page, "5")
    r = pop_state(page)
    check(r["warnVis"], "div.tot-warn becomes visible below Reserved", r["warnVis"])
    check(r["warnHead"] == "Below Reserved (8)",
          "first line reads exactly 'Below Reserved (8)'", r["warnHead"])
    check(r["warnItems"] == ["#407812 — 2", "#413650 — 3", "#409112 — 3"],
          "lists exactly the three holding orders", r["warnItems"])
    check(r["selNeed"], "select.tot-rsn gains the class 'need'", r["selNeed"])
    # The five-line cap. No shipped SKU reserves against more than three orders, so the
    # `+N more` line cannot be made to render against this file without inventing fixture data —
    # that render, and the proof that truncation never truncates the written data, is QA-ADJ-20
    # at [ADMIN] tier. What IS checkable here: the cap constant the drawing ships, and that a
    # three-order SKU is listed whole with no truncation line.
    cap = page.evaluate("() => (typeof MAX_RESV_SHOWN === 'number' ? MAX_RESV_SHOWN : null)")
    check(cap == 5, "the shipped display cap MAX_RESV_SHOWN is 5", cap)
    check(r["warnMore"] == [],
          "three holders are under the cap, so no '+N more' line renders", r["warnMore"])
    # Census clause, not a contract: the shipped sentence names the reserved total where the
    # contract is the shortfall (8 − 5 = 3). `[INV-WFX-3 · proposed]`; contract = QA-ADJ-18.
    check(ADJ_WARN_BODY in r["warnTxt"],
          "shipped body sentence (census, [INV-WFX-3]) " + ADJ_WARN_BODY, r["warnTxt"])
    check(r["okDisabled"], "apply still needs the reason", r["okDisabled"])
    page.select_option(".tot-pop .tot-rsn", "Damaged")
    after = pop_state(page)
    check(not after["okDisabled"],
          "with a reason picked the shortage WARNS, it does not block", after["okDisabled"])


@scenario("QA-ADJ-07")
def adj07(page):
    # NEGATIVE — non-integer, negative and empty are all refused identically.
    open_adjust(page)
    base = row_state(page)
    for v in ["4.5", "-3", ""]:
        type_qty(page, v)
        r = pop_state(page)
        check(r["okDisabled"], "button.tot-ok disabled for input " + repr(v), r)
        check(r["hint"] == "Enter a whole number of 0 or more",
              "hint exactly 'Enter a whole number of 0 or more' for input " + repr(v), r["hint"])
        check(not r["warnVis"], "div.tot-warn not visible for input " + repr(v), r["warnVis"])
        now = row_state(page)
        check((now["tot"], now["orig"], now["avail"]) == (base["tot"], base["orig"], base["avail"]),
              "row unchanged for input " + repr(v), {"before": base, "after": now})


@scenario("QA-ADJ-08")
def adj08(page):
    # NEGATIVE ([NE-14]) — an identical value can never be applied, so it can never emit.
    open_adjust(page)
    left = pop_state(page)
    check(left["okDisabled"] and left["hint"] == "Unchanged",
          "value left at Total: disabled + 'Unchanged'", left)
    type_qty(page, "50")
    moved = pop_state(page)
    check(not moved["okDisabled"], "sanity: a real change enables apply", moved)
    type_qty(page, "42")
    back = pop_state(page)
    check(back["okDisabled"] and back["hint"] == "Unchanged",
          "value typed back to Total: disabled + 'Unchanged'", back)


@scenario("QA-ADJ-09")
def adj09(page):
    # BOUNDARY — zero is an ordinary decrease, not a special case.
    open_adjust(page)
    type_qty(page, "0")
    r = pop_state(page)
    check(r["hint"] == "Decrease of 42 — a reason is required",
          "hint exactly 'Decrease of 42 — a reason is required'", r["hint"])
    check(r["selVis"], "select.tot-rsn visible", r["selVis"])
    check(r["okDisabled"], "button.tot-ok disabled until a reason is picked", r["okDisabled"])
    check(r["warnVis"] and r["warnHead"] == "Below Reserved (8)"
          and r["warnItems"] == ["#407812 — 2", "#413650 — 3", "#409112 — 3"],
          "0 < Reserved 8 so the QA-ADJ-06 warning block also renders", r)
    page.select_option(".tot-pop .tot-rsn", "Damaged")
    check(not pop_state(page)["okDisabled"], "zero applies once a reason is picked", pop_state(page))


@scenario("QA-ADJ-10")
def adj10(page):
    page.evaluate("window.__qa_alive = 1")
    open_adjust(page)
    type_qty(page, "45")
    page.press(".tot-pop .tot-in", "Enter")
    r = row_state(page)
    alive = page.evaluate("window.__qa_alive || 0")
    check(r["nPop"] == 0, "Enter applies and the editor closes", r["nPop"])
    check(r["tot"] == "45", "span.tot-v reads 45", r["tot"])
    check(r["avail"] == "37", "Available recomputed to 37 (45 − Reserved 8)", r["avail"])
    check(r["chipVis"] and r["chipTxt"] == "✓ Saved",
          "the in-place span.tot-saved chip shows '✓ Saved'", r)
    # CP-9 / [G-2]: success confirms in place. A success toast here is a failure, not a pass.
    check(not r["toastVis"], "#gtoast is NOT visible — success is the chip, never a toast", r)
    # The live DOM property, not the HTML attribute: the attribute still reads 42 by design.
    check(r["countedLive"] == "45" and r["countedAttr"] == "42",
          "audit Counted Qty live value synced to 45 (attribute untouched)", r)
    check(r["orig"] == "45", "td.tot-cell data-orig is now 45", r["orig"])
    check(alive == 1, "document not re-navigated", alive)


@scenario("QA-ADJ-11")
def adj11(page):
    # NEGATIVE ([NE-14], [E-113]) — every dismissal leaves the row exactly as it was.
    base = row_state(page)

    def dismissed(how):
        r = row_state(page)
        check(r["nPop"] == 0, "editor closed by " + how, r["nPop"])
        check((r["tot"], r["avail"], r["orig"]) == (base["tot"], base["avail"], base["orig"]),
              "row unchanged after " + how, {"before": base, "after": r})

    open_adjust(page)
    type_qty(page, "10")
    page.click(".tot-pop .tot-no")
    dismissed("clicking button.tot-no")

    open_adjust(page)
    type_qty(page, "10")
    page.press(".tot-pop .tot-in", "Escape")
    dismissed("pressing Escape in input.tot-in")

    open_adjust(page)
    type_qty(page, "10")
    page.evaluate("document.querySelector('.ptitle h2').click()")
    dismissed("clicking outside the editor (.ptitle h2)")

    open_adjust(page)
    open_adjust(page, ADJ_SKU2)
    r = page.evaluate("""() => ({
      n: document.querySelectorAll('.tot-pop').length,
      onSecond: !!document.querySelector('#p-current tbody tr[data-sku="100031877"] .tot-pop')})""")
    check(r["n"] == 1 and r["onSecond"],
          "opening a second row's ✎ leaves exactly one div.tot-pop, on that second row", r)


@scenario("QA-ADJ-12")
def adj12(page):
    open_adjust(page)
    type_qty(page, "3")
    page.select_option(".tot-pop .tot-rsn", "Lost")
    page.click(".tot-pop .tot-ok")
    r = page.evaluate("""() => {
      const t = document.getElementById('gtoast');
      return {vis: QA.vis(t), bad: t.classList.contains('bad'), txt: QA.t(t),
        tot: QA.t(document.querySelector(
          '#p-current tbody tr[data-sku="100004819"] span.tot-v'))};}""")
    check(r["vis"], "#gtoast becomes visible", r["vis"])
    check(not r["bad"], "#gtoast is NOT class 'bad' — a notification, not a failure", r["bad"])
    check(r["txt"].startswith("Adjusted below Reserved")
          and "Affected orders commented · #fulfillment-admin-comments notified" in r["txt"],
          "toast reads 'Adjusted below Reserved' + the notification line", r["txt"])
    check(r["tot"] == "3", "the apply itself succeeds — span.tot-v reads 3", r["tot"])


@scenario("QA-ADJ-13")
def adj13(page):
    open_search_pane(page)
    before = page.evaluate("document.querySelectorAll('#p-search .tbl tbody tr').length")
    check(before == 6, "fixture starts at six Stock History rows", before)
    open_current_pane(page)
    open_adjust(page)
    type_qty(page, "45")
    page.press(".tot-pop .tot-in", "Enter")
    open_search_pane(page)
    r = page.evaluate("""() => {
      const tb = document.querySelector('#p-search .tbl tbody');
      const f = tb.firstElementChild;
      return {n: tb.children.length,
        ty: QA.t(f.cells[0].querySelector('span.ty.ty-adj')),
        src: QA.t(f.cells[0].querySelector('span.src-note')),
        qty: QA.t(f.cells[1]), qtyCls: [...f.cells[1].classList],
        stt: QA.t(f.cells[2])};}""")
    check(r["n"] == before + 1, "the table gains exactly one row", r["n"])
    check(r["ty"] == "ADJUST", "the new first row's Type cell holds span.ty.ty-adj 'ADJUST'", r["ty"])
    check(r["src"] == "Manual · Miscount",
          "and span.src-note 'Manual · Miscount' — an increase is recorded as Miscount", r["src"])
    check(r["qty"] == "+3" and "diff-pos" in r["qtyCls"],
          "quantity cell carries the sign of the delta", r)
    check(r["stt"] == "CONFIRMED", "status badge reads CONFIRMED", r["stt"])
    # Demo-data scoping, NOT a business rule: the shipped fixture holds the Madecassol SKU only.
    # In production every SKU's adjustment appends to that SKU's history (QA-ADJ-16).
    open_current_pane(page)
    open_adjust(page, ADJ_SKU2)
    type_qty(page, "90")
    page.press(".tot-pop .tot-in", "Enter")
    open_search_pane(page)
    after = page.evaluate("document.querySelectorAll('#p-search .tbl tbody tr').length")
    check(after == r["n"], "an adjustment on another SKU leaves the row count unchanged", after)


@scenario("QA-ADJ-14")
def adj14(page):
    r0 = page.evaluate(
        "[...document.querySelectorAll('#p-current tbody .tot-edit')].filter(QA.vis).length")
    check(r0 == 11, "11 visible .tot-edit before the audit", r0)
    open_adjust(page)
    check(pop_state(page)["open"], "an editor is open before entering audit mode", pop_state(page))
    enter_audit(page)
    on = page.evaluate("""() => ({
      vis: [...document.querySelectorAll('#p-current tbody .tot-edit')].filter(QA.vis).length,
      nPop: document.querySelectorAll('.tot-pop').length})""")
    check(on["vis"] == 0, "no .tot-edit is visible while audit mode is on", on["vis"])
    check(on["nPop"] == 0, "any open div.tot-pop is gone", on["nPop"])
    page.click("#toggleAudit")
    off = page.evaluate(
        "[...document.querySelectorAll('#p-current tbody .tot-edit')].filter(QA.vis).length")
    check(off == 11, "all 11 restored on exit", off)


@scenario("QA-ADJ-15")
def adj15(page):
    enter_audit(page)
    add_torriden(page)
    during = page.evaluate("""() => {
      const tr = document.querySelector('#p-current tbody tr[data-sku="100027733"]');
      return {isFirst: document.querySelector('#p-current tbody').firstElementChild === tr,
              vis: QA.vis(tr.querySelector('.tot-edit'))};}""")
    check(during["isFirst"], "the [L-13] row is inserted first", during["isFirst"])
    check(not during["vis"],
          "its .tot-edit is not visible while the session is open", during["vis"])
    page.evaluate("QA.clickText('#toggleAudit','Exit Stock Audit')")
    after = page.evaluate("""() => {
      const tr = document.querySelector('#p-current tbody tr[data-sku="100027733"]');
      return {vis: QA.vis(tr.querySelector('.tot-edit')),
              orig: tr.querySelector('td.tot-cell').dataset.orig,
              nVis: [...document.querySelectorAll('#p-current tbody .tot-edit')]
                      .filter(QA.vis).length};}""")
    check(after["vis"], "after Exit Stock Audit the added row carries the affordance", after["vis"])
    check(after["nVis"] == 12, "12 visible .tot-edit (11 + the addition)", after["nVis"])
    # Wireframe-only client state: in production nothing is adjustable until [L-M1] Confirm
    # creates the row ([E-106]). Do not read this as licence to adjust an unconfirmed addition.
    check(after["orig"] == "0", "the row still carries data-orig='0'", after["orig"])


# ------------------------------------------------------------------- run -----

def main():
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        # 1280x1600: the audit-row autocomplete dropdown is position:fixed at the bottom of the
        # 11-row table (~y=730); at the default 720px viewport it falls outside the viewport and
        # Playwright cannot click it. Taller viewport = runner environment fix, not a spec deviation
        # (a real operator's browser shows the dropdown at the input).
        ctx = browser.new_context(viewport={"width": 1280, "height": 1600})
        ctx.add_init_script(HELPERS)
        for sid, fn in SCENARIOS:
            page = ctx.new_page()
            try:
                if sid != "QA-GLB-13":       # GLB-13 does its own viewport+preflight
                    preflight(page)
                fn(page)
                results.append({"id": sid, "verdict": "PASS"})
            except Mismatch as m:
                results.append({"id": sid, "verdict": "FAIL",
                                "expected": str(m.expected), "actual": str(m.actual)})
            except Exception:
                results.append({"id": sid, "verdict": "ERROR",
                                "error": traceback.format_exc(limit=4)})
            finally:
                page.close()
        browser.close()
    passed = sum(1 for r in results if r["verdict"] == "PASS")
    # HANDOFF.md §4 documents `python3 qa-<screen>.py [--json out.json]` for all eight
    # runners. Without this the flag is accepted, nothing is written, and the run still
    # exits 0 — a pass rate with no artefact behind it.
    if "--json" in sys.argv:
        _out = sys.argv[sys.argv.index("--json") + 1]
        _p = pathlib.Path(_out)
        _p.parent.mkdir(parents=True, exist_ok=True)
        with open(_p, "w", encoding="utf-8") as _f:
            json.dump({"total": len(results), "passed": passed,
                       "failed": [r for r in results if r["verdict"] != "PASS"],
                       "all": results}, _f, ensure_ascii=False, indent=1)
        print("wrote", _p)
    print(json.dumps({"total": len(results), "passed": passed,
                      "failed": [r for r in results if r["verdict"] != "PASS"],
                      "all": results}, ensure_ascii=False, indent=1))
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
