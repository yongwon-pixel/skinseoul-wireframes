#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ADVERSARIAL QA EXECUTION — wms2/specs/order-management.md  §8
System under test: wms2/order-management/index.html (identical to the deployed page)

Rules of engagement (Method 2):
  * Executes each [WF] scenario EXACTLY as the spec words it.
  * Uses ONLY the selectors / labels / expected strings the spec supplies.
  * Where the spec supplies no selector, the scenario's own literal strings are
    used to locate the node; where it supplies neither, the scenario is recorded
    AMBIGUOUS and NOT improvised.
  * §8.0 rule 5 ("Text assertions are byte-exact") is enforced literally.
    Where a literal read fails but a lenient read (contains / trimmed) passes,
    BOTH results are recorded so the culprit can be attributed.

Run:  python3 qa-order-management.py            (table to stdout, JSON to ./qa-order-management.results.json)
"""

import json
import os
import sys
import traceback

from playwright.sync_api import sync_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = os.path.normpath(os.path.join(HERE, "..", "..", "order-management", "index.html"))
URL = "file://" + PAGE

# ─────────────────────────────────────────────────────────────── spec constants
GREEN = "rgb(25, 135, 84)"
AMBER = "rgb(180, 83, 9)"
STAR = "rgb(245, 158, 11)"
LINE_STRONG = "rgb(187, 186, 190)"
SS_PURPLE = "rgb(88, 45, 181)"

RESULTS = []


class Ambiguous(Exception):
    pass


class Unrunnable(Exception):
    pass


def eq(actual, expected, label):
    if actual != expected:
        raise AssertionError(
            f"{label}: spec says {expected!r} · page has {actual!r}"
        )
    return True


def contains(haystack, needle, label):
    if needle not in haystack:
        raise AssertionError(f"{label}: spec says contains {needle!r} · page has {haystack!r}")
    return True


def truthy(cond, label):
    if not cond:
        raise AssertionError(label)
    return True


def scenario(sid, title):
    def deco(fn):
        fn._sid = sid
        fn._title = title
        return fn

    return deco


def fresh(page, sentinel=True):
    page.goto(URL)
    if sentinel:
        page.evaluate("window.__qaSentinel = 'om'")


def sentinel_ok(page):
    return page.evaluate("window.__qaSentinel === 'om'")


def css(page, sel, prop, nth=0):
    return page.evaluate(
        "([s,p,n]) => getComputedStyle(document.querySelectorAll(s)[n]).getPropertyValue(p)",
        [sel, prop, nth],
    )


def texts(page, sel):
    return page.eval_on_selector_all(sel, "els => els.map(e => e.textContent)")


def open_modal(page, sel):
    page.click(sel)


# ══════════════════════════════════════════════ 8.1  Block IMP


@scenario("QA-IMP-01", "Open the import modal from the filter bar")
def t_imp_01(page):
    fresh(page)
    page.click('.filterbar button[data-modal="m-import"]')
    label = page.text_content('.filterbar button[data-modal="m-import"]')
    eq(label, "⬆ Import", "trigger label")
    truthy(page.evaluate("document.getElementById('m-import').classList.contains('open')"), "#m-import open")
    hdr = page.text_content("#m-import header")
    truthy(hdr.startswith("Marketing Order Import"), f"header starts with 'Marketing Order Import' · got {hdr!r}")
    truthy(sentinel_ok(page), "sentinel survived")
    n = page.evaluate("document.querySelectorAll('.gtoast').length")
    eq(n, 0, "no .gtoast yet")
    return f"open=True · header={hdr!r} · gtoast=0 · sentinel held"


@scenario("QA-IMP-02", "Open the import modal from the wf-bar")
def t_imp_02(page):
    fresh(page)
    label = page.text_content('.wf-bar button[data-modal="m-import"]')
    eq(label, "Modal: Marketing Import", "wf-bar label")
    page.click('.wf-bar button[data-modal="m-import"]')
    truthy(page.evaluate("document.getElementById('m-import').classList.contains('open')"), "#m-import open")
    # "identical content to QA-IMP-01" — compare the modal innerHTML across both entry points
    a = page.evaluate("document.querySelector('#m-import .modal').innerHTML")
    fresh(page)
    page.click('.filterbar button[data-modal="m-import"]')
    b = page.evaluate("document.querySelector('#m-import .modal').innerHTML")
    eq(a, b, "content identical between wf-bar and filter-bar entry")
    return "wf-bar opens #m-import; modal innerHTML byte-identical to filter-bar entry"


@scenario("QA-IMP-03", "Step 1 copy")
def t_imp_03(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    blk = page.evaluate(
        """() => {
            const b=[...document.querySelectorAll('#m-import b')].find(x=>x.textContent==='1. Template');
            if(!b) return null;
            const d=b.parentElement;
            return {bold:b.textContent,
                    btn:d.querySelector('button').textContent,
                    btncls:d.querySelector('button').className,
                    helper:d.querySelector('span').textContent};
        }"""
    )
    truthy(blk, "first step block located by its bold label '1. Template'")
    eq(blk["bold"], "1. Template", "bold label")
    eq(blk["btn"], "⬇ Download Template (.xlsx)", "template button label")
    contains(blk["btncls"], "btn-line", "template button class")
    eq(
        blk["helper"],
        "Standard form from the dev team — Recipient · Contact · Address · Country · SKU · Qty · Campaign name",
        "helper text",
    )
    return f"bold={blk['bold']!r} · btn={blk['btn']!r} class={blk['btncls']!r} · helper byte-exact"


@scenario("QA-IMP-05", "Order Type default state")
def t_imp_05(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    truthy(page.evaluate("document.getElementById('otChipSeed').classList.contains('on')"), "#otChipSeed .on")
    eq(page.text_content("#otChipSeed"), "Influencer Seeding", "#otChipSeed text")
    eq(page.text_content("#otChipCustom"), "✎ Custom", "#otChipCustom text")
    truthy(not page.evaluate("document.getElementById('otChipCustom').classList.contains('on')"), "#otChipCustom no .on")
    eq(page.evaluate("document.getElementById('otCustom').style.display"), "none", "#otCustom style.display")
    return "seed=on/'Influencer Seeding' · custom='✎ Custom' no .on · #otCustom display:none"


@scenario("QA-IMP-06", "Order Type custom toggle and focus")
def t_imp_06(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    page.click("#otChipCustom")
    truthy(page.evaluate("document.getElementById('otChipCustom').classList.contains('on')"), "#otChipCustom .on")
    truthy(not page.evaluate("document.getElementById('otChipSeed').classList.contains('on')"), "#otChipSeed lost .on")
    eq(page.evaluate("document.getElementById('otCustom').style.display"), "inline-block", "#otCustom display")
    eq(page.get_attribute("#otCustom", "placeholder"), "Enter type (e.g. Pop-up event giveaway)", "#otCustom placeholder")
    truthy(page.evaluate("document.activeElement === document.getElementById('otCustom')"), "activeElement is #otCustom")
    return "chip swap ok · display=inline-block · placeholder exact · activeElement=#otCustom"


@scenario("QA-IMP-07", "Toggling back hides the custom input but keeps its value")
def t_imp_07(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    page.click("#otChipCustom")
    page.fill("#otCustom", "Pop-up event giveaway")
    page.click("#otChipSeed")
    eq(page.evaluate("document.getElementById('otCustom').style.display"), "none", "#otCustom display")
    truthy(page.evaluate("document.getElementById('otChipSeed').classList.contains('on')"), "#otChipSeed .on")
    eq(page.input_value("#otCustom"), "Pop-up event giveaway", "#otCustom.value retained")
    return "display=none · seed=on · value retained 'Pop-up event giveaway'"


@scenario("QA-IMP-08", "PIC defaults and helper copy")
def t_imp_08(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    data = page.evaluate(
        """() => {
            const sel=document.querySelector('#m-import select');
            const blk=[...document.querySelectorAll('#m-import b')].find(x=>x.textContent==='3. PIC').parentElement;
            return {opts:[...sel.options].map(o=>o.textContent),
                    selected:sel.options[sel.selectedIndex].textContent,
                    picbtn:document.getElementById('picCustomBtn').textContent,
                    picdisp:document.getElementById('picCustomIn').style.display,
                    picph:document.getElementById('picCustomIn').placeholder,
                    helper:blk.querySelector('span').textContent};
        }"""
    )
    eq(data["opts"], ["Yongwon Ryu (me)", "Harshit", "EuJin", "Adinda"], "PIC options")
    eq(data["selected"], "Yongwon Ryu (me)", "PIC selected")
    eq(data["picbtn"], "✎ Custom", "#picCustomBtn text")
    eq(data["picdisp"], "none", "#picCustomIn display")
    eq(data["picph"], "Enter PIC name", "#picCustomIn placeholder")
    eq(
        data["helper"],
        "Default = logged-in user · Recorded as the PIC for this entire import — shown in the order list & RTO",
        "PIC helper text",
    )
    return "options/selected/btn/placeholder/helper all byte-exact"


@scenario("QA-IMP-09", "PIC custom toggle and focus")
def t_imp_09(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    page.click("#picCustomBtn")
    eq(page.evaluate("document.getElementById('picCustomIn').style.display"), "inline-block", "1st click display")
    truthy(page.evaluate("document.activeElement === document.getElementById('picCustomIn')"), "activeElement=#picCustomIn")
    page.click("#picCustomBtn")
    eq(page.evaluate("document.getElementById('picCustomIn').style.display"), "none", "2nd click display")
    return "toggle inline-block → focus → none"


@scenario("QA-IMP-10", "Upload step copy")
def t_imp_10(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    b = page.evaluate(
        "() => [...document.querySelectorAll('#m-import b')].some(x=>x.textContent==='4. Upload')"
    )
    truthy(b, "bold label '4. Upload' present")
    eq(page.text_content("#m-import .dropzone"), "📄 Drag the completed template here or click to upload", "dropzone text")
    return "'4. Upload' bold present · dropzone text byte-exact"


@scenario("QA-IMP-11", "Preview header format")
def t_imp_11(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    found = page.evaluate(
        """() => [...document.querySelectorAll('#m-import b')]
                 .map(b=>b.textContent)
                 .filter(t=>t.startsWith('Preview'))"""
    )
    truthy(found, "a bold node starting 'Preview' exists")
    eq(found[0], "Preview — mkt_seeding_batch3.xlsx · 12 rows parsed · 0 errors", "preview header")
    return f"{found[0]!r} (NOTE: spec gives no selector for 'the preview header')"


@scenario("QA-IMP-12", "Preview table headers")
def t_imp_12(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    th = texts(page, "#m-import thead th")
    eq(len(th), 7, "#m-import thead th length")
    expected = ["Recipient", "Country", "SKU", "Product Name", "Qty", "Campaign", "Carrier (auto)"]
    # §8.0 rule 5: byte-exact
    eq(th, expected, "the seven headers (byte-exact per §8.0 rule 5)")
    return "n/a"


@scenario("QA-IMP-13", "Brand-bold product names [G-6]")
def t_imp_13(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    rows = page.evaluate(
        """() => [...document.querySelectorAll('#m-import tbody tr')]
                  .filter(r=>r.cells.length===7)
                  .map(r=>r.cells[3].innerHTML)"""
    )
    eq(rows[0], "<b>Dr.Jart+</b> Cicapair Gentle Cleansing Foam", "row 1 Product Name")
    eq(rows[1], "<b>Dr.Jart+</b> Cicapair Sleepair Mask", "row 2 Product Name")
    eq(rows[2], "<b>innisfree</b> Green Tea Seed Hyaluronic Serum", "row 3 Product Name")
    return "rows 1-3 innerHTML byte-exact with <b> brand wrapper"


@scenario("QA-IMP-14", "Connected-carrier rendering [L-M1b]")
def t_imp_14(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    out = page.evaluate(
        """() => [...document.querySelectorAll('#m-import tbody tr')]
                  .filter(r=>r.cells.length===7 && r.cells[1].textContent==='GB')
                  .map(r=>{const c=r.cells[6];const s=getComputedStyle(c);
                           return {t:c.textContent,color:s.color,fw:s.fontWeight};})"""
    )
    truthy(len(out) == 3, f"3 GB rows expected, got {len(out)}")
    for i, r in enumerate(out):
        eq(r["t"], "YunExpress", f"GB row {i+1} carrier text")
        eq(r["color"], GREEN, f"GB row {i+1} colour")
        eq(r["fw"], "700", f"GB row {i+1} font-weight")
    return f"3 GB rows · all 'YunExpress' / {GREEN} / 700"


@scenario("QA-IMP-15", "(neg) Unconnected carrier does not block [L-M1b] [E-7]")
def t_imp_15(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    r = page.evaluate(
        """() => {const row=[...document.querySelectorAll('#m-import tbody tr')]
                    .find(r=>r.cells.length===7 && r.cells[0].textContent==='Lucia Ramos');
                  const c=row.cells[row.cells.length-1];const s=getComputedStyle(c);
                  return {country:row.cells[1].textContent,t:c.textContent,color:s.color,fw:s.fontWeight};}"""
    )
    eq(r["country"], "PE", "Lucia Ramos country")
    eq(r["t"], "Not connected — contact the Fulfillment Center", "unconnected copy")
    eq(r["color"], AMBER, "unconnected colour")
    eq(r["fw"], "700", "unconnected font-weight")
    dis = page.evaluate(
        "() => {const b=document.getElementById('mktConfirm');return {d:b.hasAttribute('disabled'),a:b.getAttribute('aria-disabled')};}"
    )
    truthy(dis["d"] is False and dis["a"] is None, f"#mktConfirm not disabled · {dis}")
    return f"PE row copy/colour/weight exact · #mktConfirm disabled={dis['d']} aria-disabled={dis['a']}"


@scenario("QA-IMP-16", "Confirm button label format")
def t_imp_16(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    eq(page.text_content("#mktConfirm"), "Confirm Import (12 orders)", "#mktConfirm text")
    contains(page.get_attribute("#mktConfirm", "class"), "btn-mkt", "#mktConfirm class")
    return "label byte-exact · class contains btn-mkt"


@scenario("QA-IMP-17", "Confirm toast text, colour, dismissal and no reload [E-43] [E-45]")
def t_imp_17(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    page.click("#mktConfirm")
    truthy(not page.evaluate("document.getElementById('m-import').classList.contains('open')"), "modal closed")
    t = page.evaluate(
        """() => {const n=document.getElementById('gtoast');if(!n)return null;const s=getComputedStyle(n);
                  return {disp:s.display,pos:s.position,top:s.top,right:s.right,bg:s.backgroundColor,
                          first:n.firstChild.textContent,small:n.querySelector('small').textContent};}"""
    )
    truthy(t, "#gtoast exists")
    truthy(t["disp"] != "none", f"display not none · got {t['disp']!r}")
    eq(t["pos"], "fixed", "position")
    eq(t["top"], "16px", "top")
    eq(t["right"], "16px", "right")
    eq(t["bg"], GREEN, "background")
    eq(t["first"], "✓ Confirmed — 12 orders imported", "first text node")
    eq(
        t["small"],
        "Carrier auto-assigned per country · 1 not connected — flagged to contact Fulfillment Center",
        "<small> text",
    )
    page.wait_for_timeout(2900)
    eq(css(page, "#gtoast", "display"), "none", "display after ~2600ms")
    truthy(sentinel_ok(page), "sentinel held (no reload)")
    return "toast text/colour/geometry exact · hidden after 2.9s · sentinel held"


@scenario("QA-IMP-18", "Modal note copy (BR-1 operator-visible)")
def t_imp_18(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    eq(
        page.text_content(".note.mkt"),
        "On confirm, orders are created as MKT- orders and appear immediately in Ready to be Outbonded (Marketing view) regardless of stock or inbound status.",
        ".note.mkt",
    )
    return "byte-exact incl. preserved 'Outbonded'"


@scenario("QA-IMP-19", "(neg) No stock-error copy anywhere in the modal [E-20]")
def t_imp_19(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    r = page.evaluate(
        """() => {const t=document.getElementById('m-import').textContent.toLowerCase();
                  const bad=['out of stock','not in the warehouse','insufficient','재고'].filter(s=>t.includes(s));
                  const idx=[];let i=t.indexOf('stock');while(i>=0){idx.push(i);i=t.indexOf('stock',i+1);}
                  return {bad, n:idx.length, ctx:idx.map(i=>t.slice(Math.max(0,i-30),i+40))};}"""
    )
    eq(r["bad"], [], "forbidden substrings")
    eq(r["n"], 1, "occurrences of 'stock'")
    contains(r["ctx"][0], "regardless of stock or inbound status", "the single occurrence sits in the BR-1 note")
    return f"0 forbidden substrings · 1× 'stock' in {r['ctx'][0]!r}"


@scenario("QA-IMP-20", "(neg) No print, scan or carrier-picker affordance in the modal")
def t_imp_20(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    r = page.evaluate(
        """() => {const m=document.getElementById('m-import');
                  return {btns:[...m.querySelectorAll('button')].map(b=>b.textContent),
                          inputs:[...m.querySelectorAll('input')].map(i=>({t:i.type,r:i.getAttribute('role')})),
                          selects:[...m.querySelectorAll('select')].map(s=>[...s.options].map(o=>o.textContent))};}"""
    )
    truthy(not any("Print" in b for b in r["btns"]), f"no Print button · {r['btns']}")
    truthy(not any(i["t"] == "file" for i in r["inputs"]), f"no file input · {r['inputs']}")
    eq(len(r["selects"]), 1, "select count")
    eq(r["selects"][0], ["Yongwon Ryu (me)", "Harshit", "EuJin", "Adinda"], "the only select is the PIC picker")
    return f"buttons={r['btns']} · inputs={r['inputs']} · 1 select = PIC"


@scenario("QA-IMP-35", "(neg) Preview collapse row under-spans — documents [WF-15 · proposed]")
def t_imp_35(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    r = page.evaluate(
        """() => {const c=[...document.querySelectorAll('#m-import tbody td[colspan]')];
                  return {n:c.length,t:c[0]&&c[0].textContent,cs:c[0]&&c[0].getAttribute('colspan'),
                          th:document.querySelectorAll('#m-import thead th').length};}"""
    )
    eq(r["n"], 1, "colspan cell count")
    eq(r["t"], "⋯ +8 more rows", "collapse row text")
    eq(r["cs"], "6", "colspan attribute")
    eq(r["th"], 7, "thead th length")
    return "1 colspan cell · text exact · colspan=6 vs 7 headers — defect reproduced as specified"


@scenario("QA-IMP-36", "Preview row arithmetic matches the header count")
def t_imp_36(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    r = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#m-import tbody tr')];
                  return {named:rows.filter(x=>x.cells.length===7).map(x=>x.cells[0].textContent),
                          collapse:rows.filter(x=>x.querySelector('td[colspan]')).map(x=>x.textContent)};}"""
    )
    eq(r["named"], ["Svetlana Jaloba", "Zoe Garner", "Mariana Maheha", "Lucia Ramos"], "4 named rows")
    eq(r["collapse"], ["⋯ +8 more rows"], "1 collapse row")
    return "4 named + '⋯ +8 more rows' → 4+8=12 consistent with header"


@scenario("QA-IMP-37", "(neg) The dropzone is inert in the mock")
def t_imp_37(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    before = page.evaluate("document.querySelector('#m-import tbody').innerHTML")
    chooser = {"fired": False}
    page.on("filechooser", lambda fc: chooser.__setitem__("fired", True))
    page.click("#m-import .dropzone")
    page.wait_for_timeout(300)
    after = page.evaluate("document.querySelector('#m-import tbody').innerHTML")
    truthy(not chooser["fired"], "no file picker opened")
    eq(page.evaluate("document.querySelectorAll('input[type=file]').length"), 0, "input[type=file] count")
    eq(after, before, "preview unchanged")
    return "no filechooser event · 0 file inputs · preview innerHTML unchanged"


@scenario("QA-IMP-38", "Modal geometry and dismissal controls")
def t_imp_38(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    r = page.evaluate(
        """() => {const m=document.querySelector('#m-import .modal');
                  return {cls:m.className,mw:getComputedStyle(m).maxWidth,
                          x:!!m.querySelector('header .x[data-close]'),
                          foot:[...m.querySelectorAll('.foot button')].map(b=>b.textContent)};}"""
    )
    # spec: "it carries classes `modal wide`"
    for c in ("modal", "wide"):
        contains(r["cls"], c, f"class {c}")
    eq(r["mw"], "720px", "max-width")
    truthy(r["x"], "header .x[data-close] present")
    eq(r["foot"], ["Cancel", "Confirm Import (12 orders)"], "footer buttons")
    return f"class={r['cls']!r} · max-width=720px · ✕ present · foot={r['foot']}"


@scenario("QA-IMP-39", "(neg) Repeated confirms reuse one toast node")
def t_imp_39(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    page.click("#mktConfirm")
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    page.click("#mktConfirm")
    n = page.evaluate("document.querySelectorAll('.gtoast').length")
    ids = page.evaluate("[...document.querySelectorAll('.gtoast')].map(x=>x.id)")
    eq(n, 1, ".gtoast count")
    eq(ids, ["gtoast"], ".gtoast ids")
    return "1 node, id='gtoast', reused across two confirms"


# ══════════════════════════════════════════════ 8.2  Block SMP


@scenario("QA-SMP-01", "ON button opens M2")
def t_smp_01(page):
    fresh(page)
    sel = '.actionrow button[data-modal="m-sampleon"]'
    eq(page.text_content(sel), "Sample Assignment ON", "trigger label")
    contains(page.get_attribute(sel, "class"), "btn-green", "trigger class")
    page.click(sel)
    truthy(page.evaluate("document.getElementById('m-sampleon').classList.contains('open')"), "#m-sampleon open")
    hdr = page.text_content("#m-sampleon header")
    truthy(hdr.startswith("Sample Assignment ON"), f"header · got {hdr!r}")
    truthy(sentinel_ok(page), "sentinel held")
    return f"open=True · header={hdr!r} · sentinel held"


@scenario("QA-SMP-02", "Target radios")
def t_smp_02(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleon"]')
    r = page.evaluate(
        """() => {const m=document.getElementById('m-sampleon');
                  const bolds=[...m.querySelectorAll('b')].map(b=>b.textContent);
                  const rad=[...m.querySelectorAll('input[name="samptarget"]')];
                  return {bolds, n:rad.length, checked:rad.map(x=>x.checked),
                          labels:rad.map(x=>x.closest('label').textContent)};}"""
    )
    truthy("Assignment Target" in r["bolds"], f"bold group label · bolds={r['bolds']}")
    eq(r["n"], 2, "radio count")
    truthy(r["checked"][0] is True, "first radio checked")
    eq(r["labels"][0].strip(), "All new orders in this period", "first label (trimmed)")
    eq(r["labels"][1].strip(), "Selected orders only (2)", "second label (trimmed)")
    lit = r["labels"][0] == "All new orders in this period"
    return f"2 radios · first checked · labels ok (trimmed). Literal byte-exact label match={lit} (DOM has leading space {r['labels'][0]!r})"


@scenario("QA-SMP-03", "Period fields and `forever` default")
def t_smp_03(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleon"]')
    r = page.evaluate(
        """() => {const m=document.getElementById('m-sampleon');
                  const bolds=[...m.querySelectorAll('b')].map(b=>b.textContent);
                  const ins=[...m.querySelectorAll('input')].filter(i=>i.type!=='radio');
                  const cb=[...m.querySelectorAll('input[type=checkbox]')][0];
                  return {bolds, vals:ins.map(i=>({v:i.value,p:i.placeholder,t:i.type})),
                          tilde:m.textContent.includes('~'),
                          cbLabel:cb.closest('label').textContent, cbChecked:cb.checked};}"""
    )
    truthy("Assignment Period" in r["bolds"], f"bold group label · {r['bolds']}")
    vals = [x for x in r["vals"] if x["t"] == "text" or x["t"] == ""]
    truthy(any(x["v"] == "2026-07-23" for x in r["vals"]), f"start date input valued 2026-07-23 · {r['vals']}")
    truthy(any(x["v"] == "10:00" for x in r["vals"]), "start time input valued 10:00")
    truthy(r["tilde"], "`~` separator present")
    truthy(any(x["p"] == "End date" for x in r["vals"]), "End date placeholder")
    truthy(any(x["p"] == "Time" for x in r["vals"]), "Time placeholder")
    eq(r["cbLabel"].strip(), "forever (no end date)", "forever label (trimmed)")
    truthy(r["cbChecked"] is True, "forever checked")
    return "2026-07-23 / 10:00 / ~ / 'End date' / 'Time' / forever checked — all present"


@scenario("QA-SMP-04", "(neg) Modal note and absence of any sample-type picker")
def t_smp_04(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleon"]')
    note = page.text_content("#m-sampleon .note")
    contains(note, "product type is not selected", "note")
    contains(note, "exactly 1 sample set per order", "note")
    eq(page.evaluate("document.querySelectorAll('#m-sampleon select').length"), 0, "select count in M2")
    return "note contains both phrases · 0 <select> in #m-sampleon"


@scenario("QA-SMP-05", "Footer buttons")
def t_smp_05(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleon"]')
    r = page.evaluate(
        """() => [...document.querySelectorAll('#m-sampleon .foot button')]
                  .map(b=>({t:b.textContent,c:b.className}))"""
    )
    eq(len(r), 2, "footer button count")
    eq(r[0]["t"], "Cancel", "1st label")
    contains(r[0]["c"], "btn-gray", "1st is grey")
    eq(r[1]["t"], "Start Assignment (ON)", "2nd label")
    contains(r[1]["c"], "btn-green", "2nd is green")
    return f"{r}"


@scenario("QA-SMP-15", "Cancel button opens M3")
def t_smp_15(page):
    fresh(page)
    sel = '.actionrow button[data-modal="m-sampleoff"]'
    eq(page.text_content(sel), "Cancel Sample Assignment", "trigger label")
    page.click(sel)
    truthy(page.evaluate("document.getElementById('m-sampleoff').classList.contains('open')"), "#m-sampleoff open")
    hdr = page.text_content("#m-sampleoff header")
    truthy(
        hdr.startswith("Cancel Sample Assignment — Current Assignment Periods"),
        f"header · got {hdr!r}",
    )
    return f"open=True · header={hdr!r}"


@scenario("QA-SMP-16", "M3 table content")
def t_smp_16(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleoff"]')
    r = page.evaluate(
        """() => {const m=document.getElementById('m-sampleoff');
                  return {th:[...m.querySelectorAll('thead th')].map(t=>t.textContent),
                          rows:[...m.querySelectorAll('tbody tr')].map(tr=>({
                              cells:[...tr.cells].map(c=>c.textContent),
                              bhtml:tr.cells[1]?tr.cells[1].innerHTML:null}))};}"""
    )
    eq(r["th"], ["", "Assignment Period", "Target", "Status"], "M3 headers")
    eq(r["rows"][0]["cells"][1], "2026-07-01 09:00 → forever", "row1 period")
    eq(r["rows"][0]["cells"][2], "All new orders", "row1 target")
    eq(r["rows"][0]["cells"][3], "Active", "row1 status")
    contains(r["rows"][0]["bhtml"], "<b>forever</b>", "row1 'forever' inside <b>")
    eq(r["rows"][1]["cells"][1], "2026-07-15 00:00 → 2026-07-20 23:59", "row2 period")
    eq(r["rows"][1]["cells"][2], "34 selected orders", "row2 target")
    eq(r["rows"][1]["cells"][3], "Active", "row2 status")
    eq(r["rows"][2]["cells"][1], "2026-06-01 00:00 → 2026-06-30 23:59", "row3 period")
    eq(r["rows"][2]["cells"][2], "All new orders", "row3 target")
    eq(r["rows"][2]["cells"][3], "Ended", "row3 status")
    return "headers + all 3 rows byte-exact; row1 'forever' in <b>"


@scenario("QA-SMP-17", "(neg) Ended row has no checkbox element [E-27]")
def t_smp_17(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleoff"]')
    r = page.evaluate(
        """() => [...document.querySelectorAll('#m-sampleoff tbody tr')]
                  .map(tr=>({status:tr.cells[3].textContent,
                             cb:tr.querySelectorAll('input[type=checkbox]').length}))"""
    )
    ended = [x for x in r if x["status"] == "Ended"]
    active = [x for x in r if x["status"] == "Active"]
    eq([x["cb"] for x in ended], [0], "Ended row checkbox count")
    eq([x["cb"] for x in active], [1, 1], "Active rows checkbox count")
    return f"{r}"


@scenario("QA-SMP-18", "M3 note copy")
def t_smp_18(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleoff"]')
    eq(
        page.text_content("#m-sampleoff .note"),
        "Multiple assignment periods may exist — select the period(s) to cancel, then confirm. Ended periods are for record only (cannot be cancelled). Cancellation immediately stops new assignments for that period (already-assigned orders are kept).",
        "#m-sampleoff .note",
    )
    return "byte-exact"


@scenario("QA-SMP-19", "Cancel toast text and no reload")
def t_smp_19(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleoff"]')
    truthy(
        page.evaluate("document.querySelectorAll('#m-sampleoff tbody input[type=checkbox]')[0].checked"),
        "row 1 checkbox checked by default",
    )
    eq(page.text_content("#sampCancelBtn"), "Cancel Selected Periods", "#sampCancelBtn label")
    bg = css(page, "#sampCancelBtn", "background-color")
    page.click("#sampCancelBtn")
    truthy(not page.evaluate("document.getElementById('m-sampleoff').classList.contains('open')"), "modal closed")
    t = page.evaluate(
        """() => {const n=document.getElementById('gtoast2');if(!n)return null;const s=getComputedStyle(n);
                  return {disp:s.display,first:n.firstChild.textContent,small:n.querySelector('small').textContent};}"""
    )
    truthy(t and t["disp"] != "none", f"#gtoast2 visible · {t}")
    eq(t["first"], "✓ Assignment period cancelled", "first text node")
    eq(
        t["small"],
        "New assignments stopped for the selected period · already-assigned orders kept",
        "<small> text",
    )
    truthy(sentinel_ok(page), "sentinel held")
    return f"btn bg={bg} · toast text byte-exact · sentinel held"


@scenario("QA-SMP-28", "M2 opens from the wf-bar")
def t_smp_28(page):
    fresh(page)
    sel = '.wf-bar button[data-modal="m-sampleon"]'
    eq(page.text_content(sel), "Modal: Sample Assignment ON", "wf-bar label")
    page.click(sel)
    truthy(page.evaluate("document.getElementById('m-sampleon').classList.contains('open')"), "#m-sampleon open")
    a = page.evaluate("document.querySelector('#m-sampleon .modal').innerHTML")
    fresh(page)
    page.click('.actionrow button[data-modal="m-sampleon"]')
    b = page.evaluate("document.querySelector('#m-sampleon .modal').innerHTML")
    eq(a, b, "content identical to action-row entry")
    return "wf-bar opens M2; innerHTML identical to action-row entry"


@scenario("QA-SMP-29", "M3 opens from the wf-bar")
def t_smp_29(page):
    fresh(page)
    sel = '.wf-bar button[data-modal="m-sampleoff"]'
    eq(page.text_content(sel), "Modal: Cancel Sample Assignment", "wf-bar label")
    page.click(sel)
    truthy(page.evaluate("document.getElementById('m-sampleoff').classList.contains('open')"), "#m-sampleoff open")
    a = page.evaluate("document.querySelector('#m-sampleoff .modal').innerHTML")
    fresh(page)
    page.click('.actionrow button[data-modal="m-sampleoff"]')
    b = page.evaluate("document.querySelector('#m-sampleoff .modal').innerHTML")
    eq(a, b, "content identical to action-row entry")
    return "wf-bar opens M3; innerHTML identical to action-row entry"


@scenario("QA-SMP-30", "(neg) `Start Assignment (ON)` is silent — documents [WF-16 · proposed]")
def t_smp_30(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleon"]')
    eq(page.evaluate("document.querySelectorAll('.gtoast').length"), 0, "precondition: no .gtoast node")
    page.click("#m-sampleon .foot button.btn-green")
    truthy(not page.evaluate("document.getElementById('m-sampleon').classList.contains('open')"), "modal closed")
    eq(page.evaluate("document.querySelectorAll('.gtoast').length"), 0, ".gtoast count after click")
    noid = page.evaluate("!document.querySelector('#m-sampleon .foot button.btn-green').id")
    truthy(noid, "button lacks an id")
    return "modal closed · 0 toasts · button has no id — defect reproduced as specified"


@scenario("QA-SMP-31", "(neg) Cancel toasts at zero selection — documents [WF-17 · proposed]")
def t_smp_31(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleoff"]')
    page.uncheck("#m-sampleoff tbody input[type=checkbox] >> nth=0")
    n = page.evaluate("[...document.querySelectorAll('#m-sampleoff tbody input[type=checkbox]')].filter(c=>c.checked).length")
    eq(n, 0, "zero checkboxes checked")
    dis = page.evaluate("document.getElementById('sampCancelBtn').disabled")
    dlg = {"fired": False}
    page.on("dialog", lambda d: (dlg.__setitem__("fired", True), d.dismiss()))
    page.click("#sampCancelBtn")
    truthy(dis is False, "#sampCancelBtn not disabled")
    truthy(not dlg["fired"], "no confirm dialog")
    shown = page.evaluate(
        "() => {const n=document.getElementById('gtoast2');return !!n && getComputedStyle(n).display!=='none';}"
    )
    truthy(shown, "#gtoast2 shown anyway")
    return "disabled=False · no dialog · #gtoast2 shown — defect reproduced as specified"


@scenario("QA-SMP-32", "M3 default checkbox states")
def t_smp_32(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleoff"]')
    r = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#m-sampleoff tbody tr')];
                  return {per:rows.map(tr=>[...tr.querySelectorAll('input[type=checkbox]')].map(c=>c.checked)),
                          total:document.querySelectorAll('#m-sampleoff tbody input[type=checkbox]').length};}"""
    )
    eq(r["per"][0], [True], "row1 checked")
    eq(r["per"][1], [False], "row2 unchecked")
    eq(r["per"][2], [], "row3 has none")
    eq(r["total"], 2, "total checkbox elements in tbody")
    return f"{r}"


@scenario("QA-SMP-33", "(neg) `forever` does not disable the end fields — documents [WF-19 · proposed]")
def t_smp_33(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleon"]')
    truthy(
        page.evaluate("[...document.querySelectorAll('#m-sampleon input[type=checkbox]')][0].checked"),
        "forever checked",
    )
    r = page.evaluate(
        """() => [...document.querySelectorAll('#m-sampleon input')]
                  .filter(i=>i.placeholder==='End date'||i.placeholder==='Time')
                  .map(i=>({p:i.placeholder,d:i.disabled}))"""
    )
    eq(len(r), 2, "End date + Time inputs found")
    truthy(all(x["d"] is False for x in r), f"neither disabled · {r}")
    page.fill("#m-sampleon input[placeholder='End date']", "2026-08-01")
    eq(page.input_value("#m-sampleon input[placeholder='End date']"), "2026-08-01", "accepts typed input")
    return f"{r} · typed input accepted — defect reproduced as specified"


@scenario("QA-SMP-34", "Cancel toast uses its own node")
def t_smp_34(page):
    fresh(page)
    open_modal(page, '.actionrow button[data-modal="m-sampleoff"]')
    page.click("#sampCancelBtn")
    r = page.evaluate(
        """() => {const g2=document.getElementById('gtoast2');
                  return {exists:!!g2, cls:g2?g2.className:null,
                          ids:[...document.querySelectorAll('.gtoast')].map(x=>x.id)};}"""
    )
    truthy(r["exists"], "#gtoast2 exists")
    contains(r["cls"], "gtoast", "#gtoast2 carries class gtoast")
    return f"ids={r['ids']} · gtoast2.class={r['cls']!r}"


# ══════════════════════════════════════════════ 8.3  Block LST


@scenario("QA-LST-01", "Placeholder contract text")
def t_lst_01(page):
    fresh(page)
    r = page.evaluate(
        """() => {const d=document.querySelector('.pagepad div.anno[style*="dashed"]');
                  if(!d) return null;
                  return {txt:d.textContent, dot:d.querySelector('.dot')?d.querySelector('.dot').textContent:null,
                          inlineDot:d.querySelector('.dot')?getComputedStyle(d.querySelector('.dot')).display:null};}"""
    )
    truthy(r, "div.anno[style*='dashed'] inside .pagepad located")
    contains(r["txt"], "Order list table — same as the current admin (omitted)", "headline")
    contains(
        r["txt"],
        "Default columns ↔ Columns toggle view, 2,818 total, and pagination — all unchanged.",
        "sub-line",
    )
    contains(r["txt"], "MKT- marketing orders", "sub-line MKT phrase")
    eq(r["dot"], "4", "inline dot")
    return f"dot={r['dot']!r} display={r['inlineDot']!r}; strings present (NOTE: literal 'reads' fails — textContent starts with the dot glyph '4')"


@scenario("QA-LST-02", "MKT style tokens exist")
def t_lst_02(page):
    fresh(page)
    r = page.evaluate(
        """() => {const cs=getComputedStyle(document.documentElement);
                  const rules=[];
                  for(const sh of document.styleSheets){for(const rr of sh.cssRules){if(rr.selectorText)rules.push([rr.selectorText,rr.cssText]);}}
                  const find=s=>{const f=rules.find(r=>r[0]===s);return f?f[1]:null;};
                  return {mkt:cs.getPropertyValue('--mkt'), soft:cs.getPropertyValue('--mkt-soft'),
                          r1:find('.tbl tr.mkt'), r2:find('.tbl tr.mkt:hover'),
                          r3:find('.tbl tr:hover'), r4:find('.mkt-badge')};}"""
    )
    eq(r["mkt"].strip(), "#7C3AED", "--mkt")
    eq(r["soft"].strip(), "#F3EEFF", "--mkt-soft")
    truthy(r["r1"] and "var(--mkt-soft)" in r["r1"], f".tbl tr.mkt · {r['r1']!r}")
    # CSSOM re-serialises hex to rgb(); accept either form
    truthy(
        r["r2"] and ("#EBE1FF" in r["r2"].upper() or "rgb(235, 225, 255)" in r["r2"]),
        f".tbl tr.mkt:hover · {r['r2']!r}",
    )
    truthy(r["r3"] and "var(--blue-soft)" in r["r3"], f".tbl tr:hover · {r['r3']!r}")
    for decl in ("var(--mkt)", "font-weight: 800", "letter-spacing: 0.3px", "margin-left: 5px"):
        truthy(r["r4"] and decl in r["r4"], f".mkt-badge missing {decl!r} · {r['r4']!r}")
    return f"--mkt={r['mkt'].strip()} --mkt-soft={r['soft'].strip()} · 4 rules present"


@scenario("QA-LST-03", "Header and count [L-F2]")
def t_lst_03(page):
    fresh(page)
    eq(page.text_content(".ptitle h2"), "Order Management Dashboard", ".ptitle h2")
    eq(page.text_content(".ptitle .count"), "2,818 orders", ".count")
    return "byte-exact"


@scenario("QA-LST-04", "(neg) Bulk Hold Shipment must not exist [L-3]")
def t_lst_04(page):
    fresh(page)
    r = page.evaluate(
        """() => {const ctl=[...document.querySelectorAll('button,input,select,a,option')];
                  const hits=ctl.map(e=>((e.textContent||'')+' '+(e.value||'')+' '+(e.placeholder||'')).toLowerCase())
                               .filter(t=>t.includes('hold shipment')||t.includes('bulk hold'));
                  const li=[...document.querySelectorAll('.legend li')];
                  const l3=li[2]?li[2].textContent:null;
                  const docHits=(document.body.innerHTML.toLowerCase().match(/hold shipment|bulk hold/g)||[]).length;
                  return {ctlHits:hits, l3, docHits};}"""
    )
    eq(r["ctlHits"], [], "no control carries 'Hold Shipment'/'Bulk Hold'")
    contains(r["l3"], "Bulk Hold Shipment button removed", "legend item 3")
    return f"0 control hits · legend 3 retains the negative entry · document-wide occurrences={r['docHits']} (all in the legend)"


@scenario("QA-LST-05", "(neg) No print or scan surface anywhere on the page")
def t_lst_05(page):
    fresh(page)
    r = page.evaluate(
        """() => ({btns:[...document.querySelectorAll('button')].map(b=>b.textContent),
                   inputs:[...document.querySelectorAll('input')].map(i=>({t:i.type,p:i.placeholder||'',n:i.name||''})),
                   audio:document.querySelectorAll('audio').length})"""
    )
    truthy(not any("Print" in b for b in r["btns"]), f"no Print button · {r['btns']}")
    truthy(not any(i["t"] == "file" for i in r["inputs"]), "no file input")
    truthy(
        not any("scan" in (i["p"] + i["n"]).lower() for i in r["inputs"]),
        f"no scan field · {r['inputs']}",
    )
    eq(r["audio"], 0, "<audio> count")
    return f"{len(r['btns'])} buttons, none 'Print' · no file/scan input · 0 <audio>"


@scenario("QA-LST-06", "Action-row inventory [L-F4]")
def t_lst_06(page):
    fresh(page)
    r = page.evaluate(
        """() => {const a=document.querySelector('.actionrow');
                  const si=a.querySelector('.sel-info');const s=getComputedStyle(si);
                  return {firstCb:!!a.querySelector('input[type=checkbox]'),
                          firstCbLabel:a.querySelector('input[type=checkbox]').closest('label').textContent,
                          sel:si.textContent,color:s.color,fw:s.fontWeight,
                          btns:[...a.querySelectorAll('button')].map(b=>b.textContent)};}"""
    )
    truthy(r["firstCb"], "Select all checkbox present")
    contains(r["firstCbLabel"], "Select all", "Select all label")
    eq(r["sel"], "2 selected", ".sel-info text")
    eq(r["color"], SS_PURPLE, ".sel-info colour")
    eq(r["fw"], "700", ".sel-info font-weight")
    eq(r["btns"], ["⧉ Merge Orders", "Sample Assignment ON", "Cancel Sample Assignment"], "button order")
    return f"{r['btns']} · .sel-info={r['sel']!r} {r['color']} fw{r['fw']}"


@scenario("QA-LST-07", "Filter-bar inventory [L-F3]")
def t_lst_07(page):
    fresh(page)
    r = page.evaluate(
        """() => {const f=document.querySelector('.filterbar');
                  const dates=[...f.querySelectorAll('input.date')].map(i=>i.value);
                  const inps=[...f.querySelectorAll('input.inp')].map(i=>i.placeholder);
                  const sels=[...f.querySelectorAll('select')].map(s=>s.options[0].textContent);
                  const cbs=[...f.querySelectorAll('.chkgrp input[type=checkbox]')]
                              .map(c=>({l:c.closest('label').textContent.trim(),c:c.checked}));
                  return {dates,inps,sels,cbs,sep:!!f.querySelector('.sep'),
                          tilde:[...f.children].some(e=>e.textContent==='~'),
                          btns:[...f.querySelectorAll('button')].map(b=>b.textContent)};}"""
    )
    eq(r["dates"], ["2026-06-01", "2026-07-14"], "date inputs")
    truthy(r["tilde"], "`~` separator")
    truthy(r["sep"], ".sep present")
    eq(r["inps"], ["Search (order / product)", "Search PIC"], "text input placeholders")
    eq(r["sels"], ["All Status", "Country: AU", "15"], "select first options")
    eq(r["cbs"], [{"l": "Order #", "c": True}, {"l": "Tracking #", "c": False}], "checkboxes")
    eq(r["btns"], ["▦ Columns", "⬇ Export", "⬇ Yun Export", "⬆ Import"], "buttons in order")
    return f"{r}"


@scenario("QA-LST-12", "Global navigation shell [L-F6]")
def t_lst_12(page):
    fresh(page)
    r = page.evaluate(
        """() => {const n=document.querySelector('.nav');
                  return {brand:n.querySelector('.brand').textContent,
                          menus:[...n.querySelectorAll('span')].map(s=>s.textContent).filter(t=>t.endsWith('▾')),
                          links_tc:[...n.querySelectorAll('.navlink')].map(s=>s.textContent),
                          links_it:[...n.querySelectorAll('.navlink')].map(s=>s.innerText),
                          cmt:n.querySelector('[data-open="inbox1"]').textContent,
                          badge:n.querySelector('[data-open="inbox1"] .badge-n').textContent,
                          user:n.querySelector('.user').textContent,
                          avatar:n.querySelector('.avatar').textContent,
                          logout:n.querySelector('.logout').textContent};}"""
    )
    eq(r["brand"], "SkinSeoul", "brand")
    eq(
        r["menus"],
        ["Operation AI ▾", "Catalog Management ▾", "OMS Center ▾", "Site Management ▾", "System Management ▾", "Customer Management ▾"],
        "menus",
    )
    # §8.0 rule 5 — byte-exact quick links
    eq(
        r["links_tc"],
        ["Agent Telemetry", "Role Assets", "Shared Asset Health", "SkinSeoul WP Admin"],
        "quick links (byte-exact per §8.0 rule 5)",
    )
    return "n/a"


@scenario("QA-LST-13", "(neg) No pagination is rendered in the mock")
def t_lst_13(page):
    fresh(page)
    eq(page.evaluate("document.querySelectorAll('.pager').length"), 0, ".pager count")
    return "0 .pager elements"


@scenario("QA-LST-17", "(neg) No MKT row is rendered in the mock")
def t_lst_17(page):
    fresh(page)
    eq(page.evaluate("document.querySelectorAll('tr.mkt').length"), 0, "tr.mkt count")
    return "0 tr.mkt elements"


# ══════════════════════════════════════════════ 8.4  Block CMT


@scenario("QA-CMT-01", "Hub opens and closes from its trigger")
def t_cmt_01(page):
    fresh(page)
    sel = '.nav button[data-open="inbox1"]'
    contains(page.text_content(sel), "💬 Comments", "trigger label")
    page.click(sel)
    truthy(page.evaluate("document.getElementById('inbox1').classList.contains('open')"), "#inbox1 open")
    eq(page.text_content(f"{sel} .badge-n"), "3", "badge")
    page.click(sel)
    truthy(not page.evaluate("document.getElementById('inbox1').classList.contains('open')"), "#inbox1 closed again")
    return "open → badge 3 → close"


@scenario("QA-CMT-02", "Tabs and pane headers")
def t_cmt_02(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    r = page.evaluate(
        """() => {const dd=document.getElementById('inbox1');
                  const tb=[...dd.querySelectorAll('.tabs button')];
                  const ph=dd.querySelector('[data-pane="mentions"] .paneheader');
                  return {tabs:tb.map(b=>({t:b.textContent,on:b.classList.contains('on'),
                                           badge:b.querySelector('.badge-n')?b.querySelector('.badge-n').textContent:null})),
                          ph:ph.textContent, small:ph.querySelector('small').textContent,
                          // spec says "right-aligned" without giving a probe; measured geometrically
                          gapL:ph.querySelector('small').getBoundingClientRect().left-ph.getBoundingClientRect().left,
                          gapR:ph.getBoundingClientRect().right-ph.querySelector('small').getBoundingClientRect().right};}"""
    )
    truthy(r["tabs"][0]["on"], "first tab has class on")
    contains(r["tabs"][0]["t"], "@ Mentions", "tab 1 label")
    eq(r["tabs"][0]["badge"], "3", "tab 1 inline badge")
    eq(r["tabs"][1]["t"], "★ Saved", "tab 2 label")
    contains(r["ph"], "Comments mentioning me · Click to open the order", "mentions pane header")
    eq(r["small"], "Mark all read", "pane action")
    truthy(
        r["gapR"] < r["gapL"],
        f"action right-aligned: left gap {r['gapL']:.1f}px vs right gap {r['gapR']:.1f}px",
    )
    return (f"tabs={[t['t'] for t in r['tabs']]} · header ok · action={r['small']!r} "
            f"flush right (left gap {r['gapL']:.0f}px, right gap {r['gapR']:.0f}px). "
            "NOTE: spec supplies no probe for 'right-aligned'; getComputedStyle(...).marginLeft returns '0px' for the auto margin.")


@scenario("QA-CMT-03", "Saved tab")
def t_cmt_03(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    page.click('#inbox1 .tabs button[data-tab="saved"]')
    r = page.evaluate(
        """() => {const dd=document.getElementById('inbox1');
                  const sp=dd.querySelector('[data-pane="saved"]');const mp=dd.querySelector('[data-pane="mentions"]');
                  const ph=sp.querySelector('.paneheader');
                  return {sdisp:getComputedStyle(sp).display,mdisp:getComputedStyle(mp).display,
                          ph:ph.textContent,hint:ph.querySelector('small').textContent,
                          rows:[...sp.querySelectorAll('.it')].map(x=>x.querySelector('b').textContent)};}"""
    )
    truthy(r["sdisp"] != "none", "saved pane displayed")
    eq(r["mdisp"], "none", "mentions pane hidden")
    contains(r["ph"], "Saved comments · Click to open the order", "saved pane header")
    eq(r["hint"], "Unstar to remove from list", "hint")
    eq(r["rows"], ["Order MKT-40218"], "exactly one row")
    return f"{r['rows']} · header/hint byte-exact · mentions hidden"


@scenario("QA-CMT-04", "Search hides the tabs and renders a result header")
def t_cmt_04(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    eq(page.get_attribute("#inbox1 .csearch input", "placeholder"),
       "🔍 Search all comments — order no. · author · text", "search placeholder")
    page.fill("#inbox1 .csearch input", "MKT")
    r = page.evaluate(
        """() => {const dd=document.getElementById('inbox1');
                  const csr=dd.querySelector('[data-pane="csr"]');
                  return {tabs:getComputedStyle(dd.querySelector('.tabs')).display,
                          csr:getComputedStyle(csr).display,
                          ph:csr.querySelector('.paneheader').textContent};}"""
    )
    eq(r["tabs"], "none", ".tabs display")
    truthy(r["csr"] != "none", "csr pane displayed")
    eq(r["ph"], "3 results · newest first · click to open the order", "result header")
    return f"tabs=none · csr shown · header={r['ph']!r}"


@scenario("QA-CMT-05", "(neg) Search with no hits [E-38]")
def t_cmt_05(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    page.fill("#inbox1 .csearch input", "zzzz")
    r = page.evaluate(
        """() => {const csr=document.querySelector('[data-pane="csr"]');
                  return {all:csr.textContent, empty:csr.querySelector('.empty')?csr.querySelector('.empty').textContent:null,
                          rows:csr.querySelectorAll('.it').length};}"""
    )
    eq(r["rows"], 0, "result rows")
    eq(r["empty"], "No matching comments", "empty state text")
    literal = r["all"] == "No matching comments"
    if not literal:
        raise AssertionError(
            "literal read of \"[data-pane=\\\"csr\\\"] contains exactly the text 'No matching comments'\": "
            f"pane textContent is {r['all']!r} — the result header is also inside the pane. "
            "Lenient read (a .empty node whose text is exactly 'No matching comments' + zero .it rows) PASSES."
        )
    return "n/a"


@scenario("QA-CMT-06", "Clearing the search restores the tabs")
def t_cmt_06(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    page.fill("#inbox1 .csearch input", "MKT")
    page.fill("#inbox1 .csearch input", "")
    r = page.evaluate(
        """() => {const dd=document.getElementById('inbox1');
                  const on=dd.querySelector('.tabs button.on').dataset.tab;
                  return {tabs:getComputedStyle(dd.querySelector('.tabs')).display,
                          csr:getComputedStyle(dd.querySelector('[data-pane="csr"]')).display,
                          onTab:on,
                          onPane:getComputedStyle(dd.querySelector('[data-pane="'+on+'"]')).display};}"""
    )
    truthy(r["tabs"] != "none", ".tabs displayed")
    eq(r["csr"], "none", "csr hidden")
    truthy(r["onPane"] != "none", f"pane of the .on tab ({r['onTab']}) displayed")
    return f"{r}"


@scenario("QA-CMT-07", "Star toggle")
def t_cmt_07(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    star = "#inbox1 [data-pane='mentions'] .it >> nth=0 >> .star"
    r0 = page.evaluate(
        """() => {const it=[...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
                    .find(x=>x.querySelector('b').textContent==='Order MKT-40233');
                  return it.querySelector('.star').className;}"""
    )
    page.click(star)
    a = page.evaluate(
        """() => {const s=[...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
                    .find(x=>x.querySelector('b').textContent==='Order MKT-40233').querySelector('.star');
                  return {on:s.classList.contains('on'),c:getComputedStyle(s).color};}"""
    )
    truthy(a["on"], "gains class on")
    eq(a["c"], STAR, "starred colour")
    page.click(star)
    b = page.evaluate(
        """() => {const s=[...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
                    .find(x=>x.querySelector('b').textContent==='Order MKT-40233').querySelector('.star');
                  return {on:s.classList.contains('on'),c:getComputedStyle(s).color};}"""
    )
    truthy(not b["on"], "loses class on")
    eq(b["c"], LINE_STRONG, "unstarred colour")
    return f"initial class={r0!r} → on/{STAR} → off/{LINE_STRONG}"


@scenario("QA-CMT-08", "(neg) Search input cannot inject markup [E-48]")
def t_cmt_08(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    page.fill("#inbox1 .csearch input", "<b>x")
    r = page.evaluate(
        """() => {const csr=document.querySelector('[data-pane="csr"]');
                  return {empty:csr.querySelector('.empty')?csr.querySelector('.empty').textContent:null,
                          bs:document.querySelectorAll('[data-pane="csr"] b').length};}"""
    )
    eq(r["empty"], "No matching comments", "empty state rendered")
    eq(r["bs"], 0, "<b> elements inside csr")
    return "empty state · 0 <b> nodes — query escaped"


@scenario("QA-CMT-15", "Numeric-order search returns sales orders only")
def t_cmt_15(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    page.fill("#inbox1 .csearch input", "421")
    r = page.evaluate(
        """() => {const csr=document.querySelector('[data-pane="csr"]');
                  return {ph:csr.querySelector('.paneheader').textContent,
                          rows:[...csr.querySelectorAll('.it b')].map(b=>b.textContent)};}"""
    )
    eq(r["ph"], "2 results · newest first · click to open the order", "header")
    eq(r["rows"], ["Order 421771", "Order 421502"], "rows in order")
    return f"{r}"


@scenario("QA-CMT-16", "Author search and `<mark>` highlighting")
def t_cmt_16(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    page.fill("#inbox1 .csearch input", "Harshit")
    r = page.evaluate(
        """() => {const csr=document.querySelector('[data-pane="csr"]');
                  return {ph:csr.querySelector('.paneheader').textContent,
                          rows:[...csr.querySelectorAll('.it')].map(it=>({
                              o:it.querySelector('b').textContent,
                              marks:[...it.querySelectorAll('mark')].map(m=>({t:m.textContent,fw:getComputedStyle(m).fontWeight}))}))};}"""
    )
    eq(r["ph"], "2 results · newest first · click to open the order", "header")
    eq([x["o"] for x in r["rows"]], ["Order MKT-40233", "Order MKT-40191"], "row order")
    for x in r["rows"]:
        truthy(any(m["t"] == "Harshit" for m in x["marks"]), f"<mark>Harshit</mark> in {x['o']} · {x['marks']}")
        truthy(all(m["fw"] == "700" for m in x["marks"]), f"mark font-weight · {x['marks']}")
    return f"header ok · rows={[x['o'] for x in r['rows']]} · marks fw700"


@scenario("QA-CMT-17", "Results are ordered newest-first")
def t_cmt_17(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    page.fill("#inbox1 .csearch input", "4")
    r = page.evaluate(
        """() => {const csr=document.querySelector('[data-pane="csr"]');
                  return {ph:csr.querySelector('.paneheader').textContent,
                          rows:[...csr.querySelectorAll('.it b')].map(b=>b.textContent)};}"""
    )
    eq(r["ph"], "5 results · newest first · click to open the order", "header")
    eq(
        r["rows"],
        ["Order MKT-40233", "Order MKT-40218", "Order 421771", "Order MKT-40191", "Order 421502"],
        "recency order",
    )
    return f"{r['rows']}"


@scenario("QA-CMT-18", "(neg) `Mark all read` is inert in the mock")
def t_cmt_18(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    before = page.evaluate("document.querySelectorAll('#inbox1 .it.unread').length")
    eq(before, 3, "3 .it.unread rows")
    page.click('#inbox1 [data-pane="mentions"] .paneheader small')
    page.wait_for_timeout(200)
    r = page.evaluate(
        """() => ({unread:document.querySelectorAll('#inbox1 .it.unread').length,
                   badge:document.querySelector('.nav [data-open="inbox1"] .badge-n').textContent})"""
    )
    eq(r["unread"], 3, "rows keep class unread")
    eq(r["badge"], "3", "nav badge unchanged")
    return "3 unread before and after · badge still '3'"


@scenario("QA-CMT-19", "Unread and saved states in the demo data")
def t_cmt_19(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    r = page.evaluate(
        """() => [...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')]
                  .map(it=>({o:it.querySelector('b').textContent,
                             unread:it.classList.contains('unread'),
                             star:it.querySelector('.star').classList.contains('on')}))"""
    )
    eq(len(r), 3, "3 rows")
    truthy(all(x["unread"] for x in r), f"all unread · {r}")
    eq([x["o"] for x in r], ["Order MKT-40233", "Order MKT-40218", "Order 421771"], "row entities")
    eq([x["o"] for x in r if x["star"]], ["Order MKT-40218"], "only MKT-40218 starred")
    saved = page.evaluate(
        "[...document.querySelectorAll('#inbox1 [data-pane=\"saved\"] .it b')].map(b=>b.textContent)"
    )
    eq(saved, ["Order MKT-40218"], "Saved pane single row matches")
    return f"{r} · saved={saved}"


@scenario("QA-CMT-20", "(neg) The hub does not close on an outside click — documents [WF-21 · proposed]")
def t_cmt_20(page):
    fresh(page)
    page.click('.nav button[data-open="inbox1"]')
    page.click(".pagepad", position={"x": 5, "y": 5})
    truthy(page.evaluate("document.getElementById('inbox1').classList.contains('open')"), "#inbox1 still open")
    handlers = page.evaluate(
        "document.documentElement.outerHTML.includes(\"document.addEventListener('click'\")"
    )
    truthy(not handlers, "no document-level click close handler")
    return "hub stays open on outside click · no document-level handler — defect reproduced as specified"


@scenario("QA-CMT-21", "Corpus mixes marketing and sales entities")
def t_cmt_21(page):
    raise Ambiguous(
        "When-clause is 'search for an empty-adjacent common term and read the full dataset via QA-CMT-17'. "
        "No concrete query string is given ('empty-adjacent common term' is undefined; the empty query hides the "
        "csr pane entirely, so it cannot be the intended input). Executed under the only concrete reading available "
        "(the QA-CMT-17 query `4`) the assertion holds: rows = "
        "['Order MKT-40233','Order MKT-40218','Order 421771','Order MKT-40191','Order 421502'] — 3 MKT- + 2 numeric. "
        "Recorded AMBIGUOUS because the input is not specified."
    )


# ══════════════════════════════════════════════ 8.5  Block GBL


@scenario("QA-GBL-01", "Legend closing paragraph [L-F1]")
def t_gbl_01(page):
    fresh(page)
    p = page.text_content(".legend > p")
    contains(
        p,
        "Global nav · filter bar (dates · Search · PIC · Status · Order#/Tracking# checkboxes · Country · page size) · Merge Orders · Export/Yun Export · 2,818 total · pagination all stay as in the live screen.",
        "sentence 1",
    )
    contains(
        p,
        "Sample assignment was redesigned 2026-07-23 as a simple ON/OFF (no product-type selection)",
        "sentence 2",
    )
    return "both sentences present byte-exact"


@scenario("QA-GBL-02", "Toast placement and styling [L-F5]")
def t_gbl_02(page):
    fresh(page)
    open_modal(page, '.filterbar button[data-modal="m-import"]')
    page.click("#mktConfirm")
    r = page.evaluate(
        """() => {const n=document.querySelector('.gtoast');const s=getComputedStyle(n);
                  const sm=n.querySelector('small');const ss=getComputedStyle(sm);
                  return {pos:s.position,top:s.top,right:s.right,z:s.zIndex,bg:s.backgroundColor,
                          color:s.color,fw:s.fontWeight,fs:s.fontSize,
                          smfs:ss.fontSize,smop:ss.opacity};}"""
    )
    eq(r["pos"], "fixed", "position")
    eq(r["top"], "16px", "top")
    eq(r["right"], "16px", "right")
    eq(r["z"], "200", "z-index")
    eq(r["bg"], GREEN, "background")
    eq(r["color"], "rgb(255, 255, 255)", "white text")
    eq(r["fw"], "700", "font-weight")
    eq(r["fs"], "13.5px", "font-size")
    eq(r["smfs"], "11.5px", "<small> font-size")
    eq(r["smop"], "0.9", "<small> opacity")
    return f"{r}"


@scenario("QA-GBL-03", "(neg) No reload after any action [E-43] [G-2]")
def t_gbl_03(page):
    fresh(page)
    for sel in ('.filterbar button[data-modal="m-import"]',
                '.actionrow button[data-modal="m-sampleon"]',
                '.actionrow button[data-modal="m-sampleoff"]'):
        page.click(sel)
        mid = page.evaluate("document.querySelector('.overlay.open').id")
        page.click(f"#{mid} header .x")
    page.click('.filterbar button[data-modal="m-import"]')
    page.click("#mktConfirm")
    page.click('.actionrow button[data-modal="m-sampleoff"]')
    page.click("#sampCancelBtn")
    page.click('.nav button[data-open="inbox1"]')
    page.click('.nav button[data-open="inbox1"]')
    page.click("#annoToggle")
    truthy(sentinel_ok(page), "sentinel held through the whole sequence")
    return "3 modals opened+closed · #mktConfirm · #sampCancelBtn · hub open/close · #annoToggle → sentinel intact"


@scenario("QA-GBL-04", "(neg) Every dismissal path creates nothing")
def t_gbl_04(page):
    fresh(page)
    page.click('.filterbar button[data-modal="m-import"]')
    page.mouse.click(5, 5)  # overlay backdrop, outside .modal
    truthy(not page.evaluate("document.getElementById('m-import').classList.contains('open')"), "backdrop closes")
    page.click('.filterbar button[data-modal="m-import"]')
    page.click("#m-import header .x")
    truthy(not page.evaluate("document.getElementById('m-import').classList.contains('open')"), "✕ closes")
    page.click('.filterbar button[data-modal="m-import"]')
    page.click("#m-import .foot button[data-close]:not(#mktConfirm)")
    truthy(not page.evaluate("document.getElementById('m-import').classList.contains('open')"), "Cancel closes")
    eq(page.evaluate("document.querySelectorAll('.gtoast').length"), 0, ".gtoast count")
    return "backdrop / ✕ / Cancel all close · .gtoast stays 0"


@scenario("QA-GBL-09", "(neg) Two independent toast nodes — documents [WF-18 · proposed] [E-62]")
def t_gbl_09(page):
    fresh(page)
    page.click('.filterbar button[data-modal="m-import"]')
    page.click("#mktConfirm")
    page.click('.actionrow button[data-modal="m-sampleoff"]')
    page.click("#sampCancelBtn")
    r = page.evaluate(
        """() => [...document.querySelectorAll('.gtoast')].map(n=>{const s=getComputedStyle(n);
                  return {id:n.id,disp:s.display,top:s.top,right:s.right};})"""
    )
    eq(len(r), 2, ".gtoast count")
    eq([x["id"] for x in r], ["gtoast", "gtoast2"], "ids")
    truthy(all(x["disp"] == "block" for x in r), f"both display:block · {r}")
    truthy(r[0]["top"] == r[1]["top"] and r[0]["right"] == r[1]["right"], f"same coordinates · {r}")
    return f"{r} — overlap defect reproduced as specified"


@scenario("QA-GBL-10", "(neg) `Esc` does not dismiss anything — documents [WF-20 · proposed] [E-97]")
def t_gbl_10(page):
    fresh(page)
    page.click('.filterbar button[data-modal="m-import"]')
    page.keyboard.press("Escape")
    truthy(page.evaluate("document.getElementById('m-import').classList.contains('open')"), "#m-import still open")
    for trig, mid in (('.actionrow button[data-modal="m-sampleon"]', "m-sampleon"),
                      ('.actionrow button[data-modal="m-sampleoff"]', "m-sampleoff")):
        page.click("#m-import header .x")
        page.click(trig)
        page.keyboard.press("Escape")
        truthy(page.evaluate(f"document.getElementById('{mid}').classList.contains('open')"), f"#{mid} still open")
        page.click(f"#{mid} header .x")
        page.click('.filterbar button[data-modal="m-import"]')
    page.click("#m-import header .x")
    page.click('.nav button[data-open="inbox1"]')
    page.keyboard.press("Escape")
    truthy(page.evaluate("document.getElementById('inbox1').classList.contains('open')"), "#inbox1 still open")
    nolistener = page.evaluate("!document.documentElement.outerHTML.includes('keydown')")
    truthy(nolistener, "no keydown listener anywhere in the file")
    return "all four surfaces survive Escape · no 'keydown' string in the file — defect reproduced as specified"


@scenario("QA-GBL-11", "(neg) Wireframe-only chrome inventory (must not ship)")
def t_gbl_11(page):
    fresh(page)
    r = page.evaluate(
        """() => ({wf:!!document.querySelector('.wf-bar'),
                   btns:[...document.querySelectorAll('.wf-bar button')].map(b=>b.textContent),
                   dots:document.querySelectorAll('.dot').length,
                   legend:document.querySelectorAll('.legend').length})"""
    )
    truthy(r["wf"], ".wf-bar exists")
    eq(
        r["btns"],
        ["Modal: Marketing Import", "Modal: Sample Assignment ON", "Modal: Cancel Sample Assignment", "Hide annotations"],
        "wf-bar buttons",
    )
    truthy(r["dots"] > 0, ".dot elements exist")
    truthy(r["legend"] > 0, ".legend exists")
    return f"wf-bar 4 buttons exact · {r['dots']} .dot · {r['legend']} .legend"


@scenario("QA-GBL-12", "Annotation toggle")
def t_gbl_12(page):
    fresh(page)
    eq(page.text_content("#annoToggle"), "Hide annotations", "initial button text")
    page.click("#annoToggle")
    r = page.evaluate(
        """() => ({cls:document.body.classList.contains('no-anno'),
                   dots:[...document.querySelectorAll('.dot')].map(d=>getComputedStyle(d).display),
                   legend:[...document.querySelectorAll('.legend')].map(l=>getComputedStyle(l).display),
                   btn:document.getElementById('annoToggle').textContent})"""
    )
    truthy(r["cls"], "body.no-anno")
    truthy(all(d == "none" for d in r["dots"]), f".dot display · {set(r['dots'])}")
    truthy(all(l == "none" for l in r["legend"]), f".legend display · {set(r['legend'])}")
    eq(r["btn"], "Show annotations", "button text")
    page.click("#annoToggle")
    r2 = page.evaluate(
        """() => ({cls:document.body.classList.contains('no-anno'),
                   dots:[...document.querySelectorAll('.dot')].map(d=>getComputedStyle(d).display),
                   legend:[...document.querySelectorAll('.legend')].map(l=>getComputedStyle(l).display),
                   btn:document.getElementById('annoToggle').textContent})"""
    )
    truthy(not r2["cls"], "no-anno removed")
    truthy(all(d != "none" for d in r2["dots"]), "dots restored")
    truthy(all(l != "none" for l in r2["legend"]), "legend restored")
    eq(r2["btn"], "Hide annotations", "button text restored")
    return "toggle both directions verified"


@scenario("QA-GBL-13", "(neg) No audio anywhere [G-3]")
def t_gbl_13(page):
    fresh(page)
    r = page.evaluate(
        """() => {const h=document.documentElement.outerHTML;
                  return ['<audio','AudioContext','webkitAudioContext','speechSynthesis','SpeechSynthesisUtterance']
                           .filter(s=>h.includes(s));}"""
    )
    eq(r, [], "audio/TTS tokens present in the document")
    return "0 of 5 tokens present"


@scenario("QA-GBL-14", "(neg) No scanner surface [G-1]")
def t_gbl_14(page):
    fresh(page)
    r = page.evaluate(
        """() => {const ins=[...document.querySelectorAll('input')];
                  const h=document.documentElement.outerHTML;
                  return {n:ins.length,
                          autofocus:ins.filter(i=>i.hasAttribute('autofocus')).length,
                          activeIsInput:document.activeElement && document.activeElement.tagName==='INPUT',
                          onfocus:ins.filter(i=>i.hasAttribute('onfocus')).length,
                          selectCalls:(h.match(/\\.select\\(\\)/g)||[]).length,
                          focusCalls:(h.match(/\\.focus\\(\\)/g)||[]).length};}"""
    )
    eq(r["autofocus"], 0, "inputs with autofocus")
    truthy(not r["activeIsInput"], "no input focused on load")
    eq(r["onfocus"] + r["selectCalls"], 0, "select-on-focus behaviour")
    # spec's fourth clause, read literally:
    eq(r["focusCalls"], 0, "code paths that return focus to an input after an action (.focus() call sites)")
    return "n/a"


@scenario("QA-GBL-15", "Layout minimums [E-96]")
def t_gbl_15(page):
    fresh(page)
    r = page.evaluate(
        """() => ({mock:getComputedStyle(document.querySelector('.mock')).minWidth,
                   tbl:[...document.querySelectorAll('.tbl')].map(t=>getComputedStyle(t).minWidth),
                   wrap:getComputedStyle(document.querySelector('.mockwrap')).overflowX})"""
    )
    eq(r["mock"], "1240px", ".mock min-width")
    truthy(r["tbl"] and all(x == "1180px" for x in r["tbl"]), f".tbl min-width · {r['tbl']}")
    eq(r["wrap"], "auto", ".mockwrap overflow-x")
    return f"{r}"


# ─────────────────────────────────────────────────────────────── runner

ALL = [v for k, v in sorted(globals().items()) if callable(v) and hasattr(v, "_sid")]
ALL.sort(key=lambda f: f._sid)


def main():
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1500, "height": 1000})
        for fn in ALL:
            rec = {"id": fn._sid, "title": fn._title}
            try:
                ev = fn(page)
                rec["verdict"] = "PASS"
                rec["evidence"] = ev
            except Ambiguous as e:
                rec["verdict"] = "AMBIGUOUS"
                rec["evidence"] = str(e)
            except Unrunnable as e:
                rec["verdict"] = "UNRUNNABLE"
                rec["evidence"] = str(e)
            except AssertionError as e:
                rec["verdict"] = "FAIL"
                rec["evidence"] = str(e)
            except Exception as e:  # harness error — surfaced, never swallowed
                rec["verdict"] = "FAIL"
                rec["evidence"] = f"[harness] {type(e).__name__}: {e}"
                rec["trace"] = traceback.format_exc()[-800:]
            RESULTS.append(rec)
            print(f"{rec['verdict']:10} {rec['id']}  {rec['title']}")
            if rec["verdict"] != "PASS":
                print(f"           ↳ {rec['evidence']}")
        browser.close()

    counts = {}
    for r in RESULTS:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print("\n" + json.dumps(counts, ensure_ascii=False))
    out = os.path.join(HERE, "qa-order-management.results.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump({"url": URL, "counts": counts, "results": RESULTS}, f, ensure_ascii=False, indent=2)
    print("→", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
