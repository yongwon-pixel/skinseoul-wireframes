#!/usr/bin/env python3
"""Pre-handoff [WF] QA runner — inbound-request (spec v1.3, 2026-08-03).

Executes all 57 scenarios carrying a [WF] assertion from specs/inbound-request.md §8
against the local wireframe file (== tag review-baseline-20260803).
Every scenario starts from a fresh document load (§8.0 NX) unless it manages its
own navigation (QA-C-01). Text comparisons follow §8.0a: .dot descendants stripped,
declared trailing elements (.badge-n / .x) removed where the scenario says so,
whitespace runs collapsed to single spaces.
"""
import json
import sys
import traceback
from pathlib import Path

from playwright.sync_api import sync_playwright

WF_FILE = Path(__file__).resolve().parents[3] / "inbound-request" / "index.html"
assert WF_FILE.is_file(), f"wireframe not found: {WF_FILE}"
URL = WF_FILE.as_uri()

SCENARIOS = []


def scenario(sid, nav="N1"):
    def deco(fn):
        SCENARIOS.append((sid, nav, fn))
        return fn
    return deco


class Fail(Exception):
    def __init__(self, expected, actual):
        self.expected = expected
        self.actual = actual


def check(cond, expected, actual):
    if not cond:
        raise Fail(expected, str(actual))


# ── helpers ────────────────────────────────────────────────────────────────

JS_TXT = r"""(el, rm) => {
  const c = el.cloneNode(true);
  c.querySelectorAll(rm).forEach(x => x.remove());
  return c.textContent.replace(/\s+/g, ' ').trim();
}"""


def T(page, sel, rm=".dot"):
    """textContent of first match, minus `rm` descendants, whitespace-collapsed."""
    return page.eval_on_selector(sel, JS_TXT, rm)


def T_all(page, sel, rm=".dot"):
    return page.eval_on_selector_all(
        sel,
        r"""(els, rm) => els.map(el => {
          const c = el.cloneNode(true);
          c.querySelectorAll(rm).forEach(x => x.remove());
          return c.textContent.replace(/\s+/g, ' ').trim();
        })""",
        rm,
    )


def count(page, sel):
    return page.evaluate(r"(s) => document.querySelectorAll(s).length", sel)


def has_class(page, sel, cls):
    return page.eval_on_selector(sel, "(el, c) => el.classList.contains(c)", cls)


def gtoast(page):
    """Return {exists, visible, bold, small} for #gtoast."""
    return page.evaluate(r"""() => {
      const t = document.getElementById('gtoast');
      if (!t) return {exists: false, visible: false, bold: '', small: ''};
      const c = t.cloneNode(true);
      const s = c.querySelector('small');
      const small = s ? s.textContent.replace(/\s+/g, ' ').trim() : '';
      if (s) s.remove();
      return {exists: true, visible: t.style.display === 'block',
              bold: c.textContent.replace(/\s+/g, ' ').trim(), small};
    }""")


def no_gtoast(page):
    g = gtoast(page)
    return (not g["exists"]) or (not g["visible"])


def nav_to(page, nav):
    page.goto("about:blank")
    page.goto(URL)
    if nav == "N2":
        page.click('.wf-tab[data-state="s2"]')
    elif nav == "N3":
        page.click('.wf-tab[data-state="s3"]')
    elif nav == "NM":
        page.click('.wf-tab[data-modal="m-invoice"]')
    # N1 / self: nothing more


def s3_row_sel(page, inbound_no):
    """nth-child selector for the Request List data row with this Inbound No."""
    idx = page.evaluate(
        r"""(no) => {
          const rows = [...document.querySelectorAll('#s3 .tbl > tbody > tr')]
            .filter(r => !r.classList.contains('cpanel-ir'));
          const i = rows.findIndex(r => r.children[1].textContent.trim() === no);
          if (i < 0) return -1;
          return [...document.querySelectorAll('#s3 .tbl > tbody > tr')].indexOf(rows[i]) + 1;
        }""",
        inbound_no,
    )
    if idx < 0:
        raise Fail(f"Request List row {inbound_no} exists", "row not found")
    return f"#s3 .tbl > tbody > tr:nth-child({idx})"


# ── Block A ────────────────────────────────────────────────────────────────

@scenario("QA-A-01")
def a01(page):
    check(has_class(page, "#s1", "on"), "#s1 has class on on load", "not on")
    h2 = T(page, "#s1 .pagepad h2")
    check(h2 == "WMS - Inbound Request", "h2 reads exactly `WMS - Inbound Request`", h2)
    sub = T(page, "#s1 .pagepad .sub")
    check(sub == "Inbound Request — New Request", "`.sub` reads exactly `Inbound Request — New Request`", sub)
    tabs = T_all(page, "#s1 .pagetabs button")
    check(tabs == ["New Request", "Request List"],
          ".pagetabs contains exactly two buttons `New Request` and `Request List`", tabs)
    check(has_class(page, "#s1 .pagetabs button:nth-child(1)", "on"),
          "`New Request` tab carries class on", "not on")
    trail = T(page, "#s1 .pagepad > p.mut")
    check(trail == "Registered requests are viewed and managed by status in the [Request List] tab above.",
          "trailing paragraph reads exactly `Registered requests are viewed and managed by status in the [Request List] tab above.`",
          trail)


@scenario("QA-A-02")
def a02(page):
    n = count(page, "#s1 .routecards .routecard")
    check(n == 4, "exactly 4 .routecard elements", n)
    titles = T_all(page, "#s1 .routecards .routecard b")
    check(titles == ["Smart Buy", "Wholesale", "Brand Partnership", "Other"],
          "titles Smart Buy / Wholesale / Brand Partnership / Other", titles)
    badges = T_all(page, "#s1 .routecards .rc-badge")
    check(badges == ["SMART BUY", "WHOLESALE", "PARTNERSHIP", "OTHER"],
          "badges SMART BUY / WHOLESALE / PARTNERSHIP / OTHER", badges)
    check(has_class(page, "#s1 .routecards .routecard:nth-child(1)", "on"),
          "first card carries class on", "not on")
    check("JIT" not in titles and "JIT" not in badges,
          "no routecard title/badge reads JIT", f"{titles}+{badges}")


@scenario("QA-A-03")
def a03(page):
    page.click('#s1 .routecards .routecard:nth-child(2) b')  # Wholesale title
    check(has_class(page, "#s1 .routecards .routecard:nth-child(2)", "on"),
          "Wholesale card gains on", "not on")
    check(not has_class(page, "#s1 .routecards .routecard:nth-child(1)", "on"),
          "Smart Buy card loses on", "still on")
    n = count(page, "#s1 .routecards .routecard.on")
    check(n == 1, "exactly one .routecard carries on", n)


@scenario("QA-A-04")
def a04(page):
    page.click('#s1 .routecards .routecard:nth-child(4) b')  # Other title
    check(has_class(page, "#s1 .routecards .routecard:nth-child(4)", "on"),
          "Other card gains on", "not on")
    st = page.evaluate(r"""() => {
      const etc = document.querySelector('#s1 .routecards .routecard:nth-child(4) .etc-in');
      return {disabled: etc.disabled, ph: etc.placeholder, focused: document.activeElement === etc};
    }""")
    check(st["ph"] == "Enter channel name", "placeholder `Enter channel name`", st["ph"])
    check(st["disabled"] is False, ".etc-in disabled === false", st["disabled"])
    check(st["focused"], ".etc-in is document.activeElement", "not focused")


@scenario("QA-A-05")
def a05(page):
    page.click('#s1 .routecards .routecard:nth-child(4) b')
    page.click('#s1 .routecards .routecard:nth-child(1) b')
    st = page.evaluate(r"""() => {
      const card = document.querySelector('#s1 .routecards .routecard:nth-child(4)');
      const etc = card.querySelector('.etc-in');
      return {disabled: etc.disabled, focused: document.activeElement === etc,
              on: card.classList.contains('on')};
    }""")
    check(st["disabled"] is True, ".etc-in disabled === true again", st["disabled"])
    check(not st["focused"], ".etc-in no longer holds focus", "still focused")
    check(not st["on"], "Other card no longer carries on", "still on")


@scenario("QA-A-07")
def a07(page):
    ph = page.eval_on_selector("#s1 .auto input", "el => el.placeholder")
    check(ph == "Type any SKU No. · brand · product name → click a suggestion to add a row below",
          "search placeholder exact", ph)
    val = page.eval_on_selector("#s1 .auto input", "el => el.value")
    check(val == "100045210", "search value `100045210`", val)
    n = count(page, "#s1 .auto .opt")
    check(n == 3, "exactly 3 `#s1 .auto .opt` rows", n)
    check(has_class(page, "#s1 .auto .opt:nth-of-type(1)", "sel") or
          page.evaluate(r"() => document.querySelectorAll('#s1 .auto .opt')[0].classList.contains('sel')"),
          "first .opt carries class sel", "no sel")
    opts = T_all(page, "#s1 .auto .opt")
    exp = ["Anua — Heartleaf 77% Soothing Toner, 250ml 100045210",
           "Anua — Heartleaf 80% Moisture Soothing Ampoule, 30ml 100045233",
           "Anua — Heartleaf Quercetinol Pore Deep Cleansing Foam, 150ml 100045240"]
    check(opts == exp, "opt rows read Brand — Product with trailing SKU", opts)


@scenario("QA-A-10")
def a10(page):
    st = page.evaluate(r"""() => {
      const tr = document.querySelectorAll('#s1 .prodtbl tbody tr')[2];
      const ins = [...tr.querySelectorAll('input')].slice(0, 3);
      return {
        prefill: tr.classList.contains('prefill'),
        ro: ins.map(i => i.hasAttribute('readonly')),
        pe: ins.map(i => getComputedStyle(i).pointerEvents),
        vals: ins.map(i => i.value),
      };
    }""")
    check(st["prefill"], "third row carries class prefill", "no prefill")
    check(all(st["ro"]), "SKU/Brand/Product inputs carry readonly", st["ro"])
    check(all(v == "none" for v in st["pe"]), "computed pointer-events: none", st["pe"])
    # attempt to type into each
    for i in range(3):
        page.evaluate(
            r"(i) => document.querySelectorAll('#s1 .prodtbl tbody tr')[2].querySelectorAll('input')[i].focus()", i)
        page.keyboard.type("XX")
    vals = page.evaluate(
        r"() => [...document.querySelectorAll('#s1 .prodtbl tbody tr')[2].querySelectorAll('input')].slice(0,3).map(i => i.value)")
    check(vals == ["100045210", "Anua", "Heartleaf 77% Soothing Toner, 250ml"],
          "values unchanged `100045210` / `Anua` / `Heartleaf 77% Soothing Toner, 250ml`", vals)


@scenario("QA-A-11")
def a11(page):
    n = count(page, "#s1 .prodtbl tbody tr")
    check(n == 3, "#s1 .prodtbl tbody contains exactly 3 rows", n)
    np = count(page, "#s1 .prodtbl tbody tr.prefill")
    check(np == 1, "exactly one row carries class prefill", np)
    st = page.evaluate(r"""() => [...document.querySelectorAll('#s1 .prodtbl tbody tr')].map(tr => {
      const rms = tr.querySelectorAll('.rm');
      return {n: rms.length, title: rms[0] && rms[0].title, txt: rms[0] && rms[0].textContent.trim()};
    })""")
    check(all(r["n"] == 1 and r["title"] == "Delete row" and r["txt"] == "✕" for r in st),
          "every row has exactly one .rm with title=`Delete row` and text `✕`", st)


@scenario("QA-A-13")
def a13(page):
    ths = T_all(page, "#s1 .prodtbl thead th")
    exp = ["SKU No.", "Brand", "Product Name", "Order Qty", "Unit Cost (KRW) *", "JIT Price (KRW)", ""]
    check(ths == exp, "header cells (dots stripped) read exactly in order incl. one empty cell", ths)
    disc = T(page, "#s1 .formcard .fsec:nth-of-type(2) p.mut")  # the disclaimer above the table
    check("enter 0 if free of charge (required)" in disc,
          "disclaimer contains `enter 0 if free of charge (required)`", disc)
    check("leave blank if unknown (optional)" in disc,
          "disclaimer contains `leave blank if unknown (optional)`", disc)
    phs = page.evaluate(r"""() => {
      const tr = document.querySelector('#s1 .prodtbl tbody tr.prefill');
      const ins = tr.querySelectorAll('input');
      return [ins[4].placeholder, ins[5].placeholder];
    }""")
    check(phs[0] == "Per-unit price ₩ (0 if free)", "prefill Unit Cost placeholder `Per-unit price ₩ (0 if free)`", phs[0])
    check(phs[1] == "Blank if unknown", "prefill JIT placeholder `Blank if unknown`", phs[1])


@scenario("QA-A-17")
def a17(page):
    sup = page.evaluate(r"""() => {
      const fld = [...document.querySelectorAll('#s1 .fld')].find(f => {
        const l = f.querySelector('label'); return l && l.textContent.includes('Supplier');
      });
      const label = fld.querySelector('label');
      const star = [...label.querySelectorAll('span')].find(s => s.textContent.trim() === '*');
      const inp = fld.querySelector('input');
      return {label: label.textContent.replace(/\s+/g, ' ').trim(),
              starColor: star ? getComputedStyle(star).color : null,
              ph: inp.placeholder, val: inp.value};
    }""")
    check(sup["starColor"] == "rgb(220, 53, 69)", "required `*` computed color rgb(220, 53, 69)", sup["starColor"])
    check("— who is shipping the goods" in sup["label"], "qualifier `— who is shipping the goods`", sup["label"])
    check(sup["ph"] == "e.g. 비엠유통, Coupang", "placeholder `e.g. 비엠유통, Coupang`", sup["ph"])
    check(sup["val"] == "Coupang", "value `Coupang`", sup["val"])
    trk = page.evaluate(r"""() => {
      const fld = document.querySelector('#s1 .fld-inv');
      return {cls: fld.className, label: fld.querySelector('label').textContent.replace(/\s+/g, ' ').trim(),
              ph: fld.querySelector('input').placeholder};
    }""")
    check("fld-inv" in trk["cls"], "Tracking No wrapper has class fld-inv", trk["cls"])
    check("optional · can be added later after dispatch" in trk["label"],
          "label contains `optional · can be added later after dispatch`", trk["label"])
    check(trk["ph"] == "Add after dispatch — you can submit without it (add later)",
          "placeholder `Add after dispatch — you can submit without it (add later)`", trk["ph"])
    d = page.evaluate(r"""() => {
      const i = document.querySelector('#s1 input[type=date]');
      return {type: i.type, val: i.value};
    }""")
    check(d["type"] == "date" and d["val"] == "2026-07-16",
          "Expected arrival input[type=date] value 2026-07-16", d)


@scenario("QA-A-18")
def a18(page):
    url0 = page.url
    page.click("#s1 .submitrow .btn-blue")
    g = gtoast(page)
    check(g["visible"], "#gtoast visible after Register", g)
    check(g["bold"] == "✓ Inbound request registered",
          "toast bold `✓ Inbound request registered`", g["bold"])
    check(g["small"] == "Inbound No. auto-assigned · added to the Request List · No refresh",
          "secondary `Inbound No. auto-assigned · added to the Request List · No refresh`", g["small"])
    check(page.url == url0, "URL unchanged", page.url)
    check(count(page, "#s1 .formcard") == 1, "form still in DOM", "missing")
    page.wait_for_timeout(3000)
    g2 = gtoast(page)
    check(not g2["visible"], "after 2600 ms #gtoast hidden again", g2)


@scenario("QA-A-19")
def a19(page):
    page.click("#s1 .submitrow .btn-blue")
    page.wait_for_timeout(400)
    page.click("#s1 .submitrow .btn-blue")  # 2nd click ~400-500ms after 1st
    n_id = page.evaluate(r"() => document.querySelectorAll('[id=\"gtoast\"]').length")
    n_cls = count(page, ".gtoast")
    check(n_id == 1 and n_cls == 1, "exactly one #gtoast element — toasts never stack", f"id:{n_id} cls:{n_cls}")
    # first click's 2600ms timer would fire ~2200ms after 2nd click; check reset:
    page.wait_for_timeout(2400)
    check(gtoast(page)["visible"], "hide timer reset — still visible 2.4s after 2nd click", gtoast(page))
    page.wait_for_timeout(800)
    check(not gtoast(page)["visible"], "hidden 2.6s+ after 2nd click", gtoast(page))


@scenario("QA-A-23")
def a23(page):
    st = page.evaluate(r"""() => {
      const note = [...document.querySelectorAll('#s1 .note.purple')]
        .find(n => n.textContent.includes('auto-matches it to View Orders'));
      if (!note) return null;
      return {a: note.querySelectorAll('a').length, b: note.querySelectorAll('button').length,
              dm: note.querySelectorAll('[data-modal]').length};
    }""")
    check(st is not None, ".note.purple containing `auto-matches it to View Orders` exists", "not found")
    check(st["a"] == 0 and st["b"] == 0 and st["dm"] == 0,
          "no <a>, no <button>, no [data-modal] inside the note", st)


@scenario("QA-A-24")
def a24(page):
    st = page.evaluate(r"""() => {
      const flds = [...document.querySelectorAll('#s1 .fld')];
      const f = flds.find(x => { const l = x.querySelector('label'); return l && l.textContent.trim() === 'Memo (Optional)'; });
      if (!f) return null;
      const t = f.querySelector('textarea.mtextarea');
      return t ? {ph: t.placeholder, val: t.value} : 'no textarea';
    }""")
    check(isinstance(st, dict), "textarea.mtextarea under label `Memo (Optional)` exists", st)
    check(st["ph"] == "Notes about this inbound — anything written here is also logged to the request's Comments history",
          "memo placeholder exact", st["ph"])
    check(st["val"] == "", "empty value", st["val"])


@scenario("QA-A-25")
def a25(page):
    st = page.evaluate(r"""() => {
      const p = getComputedStyle(document.querySelector('#s1 .pagepad'));
      const m = getComputedStyle(document.querySelector('#s1 .mock'));
      return {pad: [p.paddingTop, p.paddingRight, p.paddingBottom, p.paddingLeft], minw: m.minWidth,
              submit: !!document.querySelector('#s1 .formcard .submitrow')};
    }""")
    check(st["pad"] == ["18px", "16px", "0px", "16px"],
          "#s1 .pagepad computed padding 18px 16px 0px", st["pad"])
    check(st["minw"] == "1280px", "#s1 .mock declares min-width: 1280px", st["minw"])
    check(st["submit"], "#s1 .submitrow present inside #s1 .formcard", "missing")


@scenario("QA-A-26")
def a26(page):
    page.click('.wf-tab[data-state="s3"]')  # N1 then N3
    nav_btn = T(page, "#s1 .nav .icon-btn", ".dot")
    check(nav_btn.startswith("💬 Comments"), "nav button label begins with `💬 Comments`", nav_btn)
    btns = T_all(page, "#s3 .comment-btn", ".dot")
    check(len(btns) == 7, "7 .comment-btn buttons", len(btns))
    check(all(b.startswith("💬 Comments") for b in btns),
          "every .comment-btn label begins with `💬 Comments`", btns)
    tabs = T_all(page, "#inbox1 .tabs button", ".dot")
    check(tabs[0].startswith("@ Mentions") and tabs[1] == "★ Saved",
          "hub tabs begin `@ Mentions` and read `★ Saved`", tabs)
    bad = page.evaluate(r"""() => {
      const ctrls = [...document.querySelectorAll('.comment-btn, .icon-btn, .inboxdd .tabs button')];
      return ctrls.filter(c => /메모|Notes|Remarks/.test(c.textContent)).map(c => c.textContent.trim());
    }""")
    check(bad == [], "no localised/alternative label (메모, Notes, Remarks) on comments controls", bad)


@scenario("QA-A-28")
def a28(page):
    order_ok = page.evaluate(r"""() => {
      const seq = [
        document.querySelector('#s1 .routecards'),
        document.querySelector('#s1 .auto'),
        document.querySelector('#s1 .prodtbl'),
        document.querySelector('#s1 input[placeholder="e.g. 비엠유통, Coupang"]'),
        document.querySelector('#s1 .fld-inv input'),
        document.querySelector('#s1 input[type=date]'),
        document.querySelector('#s1 textarea.mtextarea'),
      ];
      if (seq.some(x => !x)) return 'missing element';
      for (let i = 0; i < seq.length - 1; i++) {
        if (!(seq[i].compareDocumentPosition(seq[i+1]) & Node.DOCUMENT_POSITION_FOLLOWING)) return 'order broken at ' + i;
      }
      return true;
    }""")
    check(order_ok is True, "DOM order route cards → search → table → Supplier → Tracking → Expected arrival → Memo", order_ok)
    ths = T_all(page, "#s1 .prodtbl thead th")
    check(ths[:6] == ["SKU No.", "Brand", "Product Name", "Order Qty", "Unit Cost (KRW) *", "JIT Price (KRW)"],
          "product table header order", ths)
    size = page.evaluate(r"""() => {
      const els = [...document.querySelectorAll('#s1 th, #s1 label, #s1 td')];
      const named = els.filter(e => {
        const c = e.cloneNode(true); c.querySelectorAll('.dot').forEach(d => d.remove());
        return c.textContent.replace(/\s+/g, ' ').trim() === 'Size';
      });
      const ctl = [...document.querySelectorAll('#s1 input, #s1 select, #s1 textarea')]
        .filter(i => (i.name === 'Size') || (i.placeholder === 'Size'));
      return named.length + ctl.length;
    }""")
    check(size == 0, "no <th>/<label>/form control/table cell named `Size`", size)


# ── Block B ────────────────────────────────────────────────────────────────

@scenario("QA-B-01", nav="N2")
def b01(page):
    check(has_class(page, "#s2", "on"), "#s2 has class on", "not on")
    check(has_class(page, "#s2 .routecards .routecard:nth-child(2)", "on"),
          "Wholesale card carries on", "not on")
    others = page.evaluate(
        r"() => [1, 3, 4].map(i => document.querySelector(`#s2 .routecards .routecard:nth-child(${i})`).classList.contains('on'))")
    check(others == [False, False, False], "the other three cards do not carry on", others)
    inb = page.evaluate(r"""() => {
      const labels = [...document.querySelectorAll('#s2 .formcard label')]
        .filter(l => l.textContent.includes('Inbound No.'));
      const inputs = [...document.querySelectorAll('#s2 .formcard input, #s2 .formcard select')]
        .filter(i => (i.placeholder || '').includes('Inbound No.') || (i.name || '').includes('Inbound'));
      return labels.length + inputs.length;
    }""")
    check(inb == 0, "no Inbound No. input / preview panel / labelled element inside #s2 .formcard", inb)
    mut = T(page, "#s2 .submitrow .mut")
    exp = ("On registration, status = REQUESTED (tracking number entered → View Orders matching active immediately) "
           "· Inbound No. auto-assigned — shown in the Request List")
    check(mut == exp, f"`#s2 .submitrow .mut` reads exactly `{exp}`", mut)


@scenario("QA-B-02", nav="N2")
def b02(page):
    row2 = page.evaluate(r"""() => {
      const tr = document.querySelectorAll('#s2 .prodtbl tbody tr')[1];
      const ins = tr.querySelectorAll('input');
      return {brand: ins[1].value, name: ins[2].value, qty: ins[3].value, cost: ins[4].value, jit: ins[5].value};
    }""")
    check(row2["brand"] == "Round Lab" and row2["name"] == "1025 Dokdo Cleanser, 150ml",
          "row 2 is Round Lab / 1025 Dokdo Cleanser, 150ml", row2)
    check(row2["qty"] == "300", "Order Qty = 300", row2["qty"])
    check(row2["cost"] == "0", "Unit Cost (KRW) = 0", row2["cost"])
    check(row2["jit"] == "", "empty JIT Price", row2["jit"])
    expl = page.evaluate(r"""() => {
      const p = [...document.querySelectorAll('#s2 p.mut')].find(x => x.textContent.includes('free promotional stock'));
      return p ? p.textContent.replace(/\s+/g, ' ').trim() : null;
    }""")
    check(expl and "0 entered directly in Unit Cost (0 allowed)" in expl,
          "explanatory line contains `0 entered directly in Unit Cost (0 allowed)`", expl)
    foc = page.evaluate(r"""() => {
      const cbs = [...document.querySelectorAll('input[type=checkbox]')]
        .filter(c => /free of charge|FOC/i.test(((c.closest('label') || {}).textContent) || (c.title || '')));
      const labels = [...document.querySelectorAll('label')]
        .filter(l => /free of charge|FOC/.test(l.textContent) && l.querySelector('input'));
      return cbs.length + labels.length;
    }""")
    check(foc == 0, "no checkbox/toggle/label control bound to a free-of-charge behavior", foc)


@scenario("QA-B-03", nav="N2")
def b03(page):
    st = page.evaluate(r"""() => {
      const sup = [...document.querySelectorAll('#s2 .fld')].find(f => (f.querySelector('label') || {textContent: ''}).textContent.includes('Supplier'));
      const trk = document.querySelector('#s2 .fld-inv input');
      const date = document.querySelector('#s2 input[type=date]');
      const memo = document.querySelector('#s2 textarea.mtextarea');
      const note = document.querySelector('#s2 .note.purple');
      return {sup: sup.querySelector('input').value, trkVal: trk.value, trkPh: trk.placeholder,
              date: date.value, memo: memo.value, note: note.textContent.replace(/\s+/g, ' ').trim()};
    }""")
    check(st["sup"] == "비엠유통", "Supplier value exactly `비엠유통`", st["sup"])
    check(st["trkVal"] == "10325661220417", "Tracking No value `10325661220417`", st["trkVal"])
    check(st["trkPh"] == "Add after dispatch — you can submit without it",
          "placeholder `Add after dispatch — you can submit without it`", st["trkPh"])
    check(st["date"] == "2026-07-18", "Expected arrival 2026-07-18", st["date"])
    check(st["memo"] == "Wholesale vendor direct ship — 2 pallets, forklift needed",
          "Memo contains `Wholesale vendor direct ship — 2 pallets, forklift needed`", st["memo"])
    check("matches to View Orders the moment it registers" in st["note"],
          ".note.purple contains `matches to View Orders the moment it registers`", st["note"])


@scenario("QA-B-04", nav="N2")
def b04(page):
    page.click("#s2 .submitrow .btn-blue")
    g = gtoast(page)
    check(g["visible"] and g["bold"] == "✓ Inbound request registered"
          and g["small"] == "Inbound No. auto-assigned · added to the Request List · No refresh",
          "toast identical to State 1 — `✓ Inbound request registered` + secondary line", g)


@scenario("QA-B-06", nav="N2")
def b06(page):
    foot = page.evaluate(r"""() => {
      const legends = [...document.querySelectorAll('.legend')];
      const s2l = legends.find(l => l.querySelector('h3') && l.querySelector('h3').textContent.includes('State 2'));
      const p = s2l.querySelector('ol + p, p');
      return p ? p.textContent.replace(/\s+/g, ' ').trim() : null;
    }""")
    check(foot and "REQUESTED → PARTIAL → INBOUNDED" in foot,
          "State 2 legend footer contains `REQUESTED → PARTIAL → INBOUNDED`", foot)
    check("SHIPPED retired 2026-07-27 · PARTIAL added 2026-08-02" in foot,
          "footer records `SHIPPED retired 2026-07-27 · PARTIAL added 2026-08-02`", foot)
    shipped = page.evaluate(r"""() => [...document.querySelectorAll('.chip, .tag, .pill, option, button')]
      .filter(e => e.textContent.includes('SHIPPED')).length""")
    check(shipped == 0, "no .chip/.tag/.pill/<option>/<button> reads SHIPPED", shipped)


# ── Block C ────────────────────────────────────────────────────────────────

@scenario("QA-C-01", nav="self")
def c01(page):
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.goto("about:blank")
    page.goto(URL + "#reqlist")
    check(has_class(page, "#s3", "on"), "#reqlist load: #s3 has class on on first paint", "not on")
    check(has_class(page, '.wf-tab[data-state="s3"]', "on"),
          "top-bar tab 3 carries class on", "not on")
    page.goto("about:blank")
    page.goto(URL + "#s3")
    check(has_class(page, "#s3", "on"), "#s3 load: #s3 active", "not on")
    # load #s3 again while #s3 already active (fresh document each time)
    page.goto("about:blank")
    page.goto(URL + "#s3")
    n_on = count(page, ".state.on")
    check(n_on == 1 and has_class(page, "#s3", "on"),
          "re-load with #s3 is a no-op: exactly one active state (#s3)", f"active states: {n_on}")
    page.goto("about:blank")
    page.goto(URL + "#nosuchtab")
    n_on = count(page, ".state.on")
    check(n_on == 1 and has_class(page, "#s1", "on"),
          "unknown hash: #s1 keeps exactly one active state", f"active states: {n_on}, s1 on: {has_class(page, '#s1', 'on')}")
    check(errors == [], "no error is thrown", errors)


@scenario("QA-C-02", nav="N3")
def c02(page):
    chips = T_all(page, "#s3 .filterchips .chip")
    exp = ["All 13", "REQUESTED 8", "PARTIAL 1", "INBOUNDED 3", "CANCELLED 1"]
    check(chips == exp, "exactly 5 chips: All 13 / REQUESTED 8 / PARTIAL 1 / INBOUNDED 3 / CANCELLED 1", chips)
    check(has_class(page, "#s3 .filterchips .chip:nth-of-type(1)", "on") or
          page.evaluate(r"() => document.querySelectorAll('#s3 .filterchips .chip')[0].classList.contains('on')"),
          "`All 13` chip carries class on", "not on")
    check(8 + 1 + 3 + 1 == 13, "counts sum to All (8+1+3+1=13)", "n/a")
    check(not any("SHIPPED" in c for c in chips), "no chip labelled SHIPPED", chips)


@scenario("QA-C-03", nav="N3")
def c03(page):
    page.evaluate(r"""() => [...document.querySelectorAll('#s3 .filterchips .chip')]
      .find(c => c.textContent.replace(/\s+/g, ' ').trim() === 'PARTIAL 1').click()""")
    st = page.evaluate(r"""() => {
      const chips = [...document.querySelectorAll('#s3 .filterchips .chip')];
      return {partial: chips[2].classList.contains('on'), all: chips[0].classList.contains('on'),
              n: chips.filter(c => c.classList.contains('on')).length};
    }""")
    check(st["partial"], "PARTIAL chip gains on", st)
    check(not st["all"], "All 13 loses on", st)
    check(st["n"] == 1, "exactly one chip carries on", st["n"])


@scenario("QA-C-05", nav="N3")
def c05(page):
    btn = T(page, "#s3 .bulkbar .btn")
    check(btn == "Bulk add tracking numbers", "bulk button labelled exactly `Bulk add tracking numbers`", btn)
    cnt = T(page, "#s3 .bulkbar .cnt")
    check(cnt == "2 selected · Inbound processing (INBOUNDED transition) is applied automatically by View Orders scans",
          "count text exact", cnt)
    st = page.evaluate(r"""() => {
      const btns = [...document.querySelectorAll('#s3 .bulkbar button')];
      return {n: btns.length, shipped: btns.filter(b => /Mark as shipped/i.test(b.textContent)).length};
    }""")
    check(st["shipped"] == 0 and st["n"] == 1,
          "no `Mark as shipped` / no manual status control in the bulk bar (single bulk button)", st)


@scenario("QA-C-07", nav="N3")
def c07(page):
    tags = page.evaluate(r"""() => [...document.querySelectorAll('#s3 .tbl tbody .tag-smartbuy, #s3 .tbl tbody .tag-wholesale, #s3 .tbl tbody .tag-partnership')]
      .map(t => { const cs = getComputedStyle(t);
        return {txt: t.textContent.trim(), bg: cs.backgroundColor, color: cs.color, fw: cs.fontWeight}; })""")
    check(len(tags) > 0, "route .tag spans exist", tags)
    check(all(t["bg"] in ("rgba(0, 0, 0, 0)", "transparent") for t in tags),
          "computed background-color fully transparent", tags)
    check(all(t["color"] == "rgb(20, 16, 27)" for t in tags), "computed color rgb(20, 16, 27)", tags)
    check(all(t["fw"] == "800" for t in tags), "font-weight 800", tags)
    texts = sorted({t["txt"] for t in tags})
    check(texts == ["PARTNERSHIP", "SMART BUY", "WHOLESALE"],
          "cells render SMART BUY / WHOLESALE / PARTNERSHIP", texts)


@scenario("QA-C-08", nav="N3")
def c08(page):
    r4 = s3_row_sel(page, "202607120004")
    cell = page.eval_on_selector(f"{r4} td:nth-child(7)", r"""el => {
      const c = el.cloneNode(true); c.querySelectorAll('.dot').forEach(d => d.remove());
      const note = c.querySelector('.route-note');
      return {txt: c.textContent, note: note ? note.textContent.trim() : null};
    }""")
    check("10325661220417" in cell["txt"] and "10325661220418" in cell["txt"],
          "row 202607120004 renders two tracking numbers 10325661220417 and 10325661220418", cell["txt"])
    check(cell["note"] == "2 tracking numbers — all matching active",
          "note `2 tracking numbers — all matching active`", cell["note"])
    for no in ("202607130003", "202607130002"):
        r = s3_row_sel(page, no)
        t = T_all(page, f"{r} td:nth-child(7) button")
        check(t == ["Add tracking"], f"row {no} renders an `Add tracking` button", t)
    r1 = s3_row_sel(page, "202607120001")
    st = page.eval_on_selector(f"{r1} td:nth-child(7)", r"""el => ({
      txt: el.textContent.replace(/\s+/g, ' ').trim(), btns: el.querySelectorAll('button').length})""")
    check(st["txt"] == "10324880021991" and st["btns"] == 0,
          "row 202607120001 renders single number 10324880021991 with no Add tracking button", st)
    for no in ("202607120004", "202607120001"):
        r = s3_row_sel(page, no)
        nb = count(page, f"{r} td:nth-child(7) button")
        check(nb == 0, f"row {no} (has numbers): no Add tracking / inline add affordance", nb)


@scenario("QA-C-09", nav="N3")
def c09(page):
    r = s3_row_sel(page, "202607120001")
    pill = T(page, f"{r} td:nth-child(11) .tag")
    check(pill == "PARTIAL 120/180", "status pill `PARTIAL 120/180`", pill)
    qty = page.eval_on_selector(f"{r} td:nth-child(6)", r"""el => {
      const note = el.querySelector('.route-note');
      return {txt: el.textContent.replace(/\s+/g, ' ').trim(),
              note: note ? note.textContent.replace(/\s+/g, ' ').trim() : null,
              title: note ? note.title : null};
    }""")
    check(qty["txt"].startswith("180"), "Qty cell shows 180", qty["txt"])
    check(qty["note"] == "✎ 300→180 (damaged)", "edit-history note `✎ 300→180 (damaged)`", qty["note"])
    check(qty["title"] == "Expected qty edit history", "title exactly `Expected qty edit history`", qty["title"])
    check("(damaged)" in qty["note"] and "Damaged/defective" not in qty["txt"],
          "short token `damaged`, not the full enum string", qty["txt"])


@scenario("QA-C-10", nav="N3")
def c10(page):
    for no, rd in (("202607100005", "07-11 14:22"), ("202607090002", "07-09 10:05")):
        r = s3_row_sel(page, no)
        pill = T(page, f"{r} td:nth-child(11) .tag")
        check(pill == "INBOUNDED", f"row {no} shows INBOUNDED pill", pill)
        cell = T(page, f"{r} td:nth-child(9)")
        check(cell == rd, f"row {no} Received Date `{rd}`", cell)
        links = page.evaluate(
            r"""(sel) => { const tr = document.querySelector(sel);
              return [...tr.querySelectorAll('a, button')].filter(x => /View Orders/i.test(x.textContent + ' ' + (x.title || ''))).length; }""",
            r)
        check(links == 0, f"row {no}: no <a>/<button> pointing to View Orders", links)
    note = page.eval_on_selector(s3_row_sel(page, "202607100005") + " td:nth-child(7) .route-note",
                                 "el => el.textContent.trim()")
    check(note == "Switched by View Orders scan inbound",
          "202607100005 tracking note `Switched by View Orders scan inbound`", note)


@scenario("QA-C-11", nav="N3")
def c11(page):
    ths = T_all(page, "#s3 .tbl thead th")
    exp = ["", "Inbound No.", "Sourcing Route", "Brand · Product", "SKU", "Qty", "Tracking No",
           "Expected arrival", "Received Date", "Requested by", "Status", "Actions"]
    check(len(ths) == 12, "exactly 12 th cells", len(ths))
    check(ths == exp, "th texts in order (dots stripped), first = checkbox cell", ths)
    check(page.evaluate(r"() => !!document.querySelector('#s3 .tbl thead th input[type=checkbox]')"),
          "first th holds the checkbox", "no checkbox")
    carrier = page.evaluate(r"""() => [...document.querySelectorAll('#s3 .tbl th, #s3 .tbl td')]
      .filter(e => { const c = e.cloneNode(true); c.querySelectorAll('.dot').forEach(d => d.remove());
        return c.textContent.replace(/\s+/g, ' ').trim() === 'Carrier'; }).length""")
    check(carrier == 0, "no <th> or cell labelled `Carrier`; no 13th column", carrier)


@scenario("QA-C-12", nav="N3")
def c12(page):
    for no in ("202607100005", "202607090002"):
        r = s3_row_sel(page, no)
        n = page.evaluate(
            r"""(sel) => [...document.querySelector(sel).querySelectorAll('button')]
                 .filter(b => b.textContent.trim() === 'Add tracking').length""", r)
        check(n == 0, f"INBOUNDED row {no} contains no `Add tracking` button", n)


@scenario("QA-C-13", nav="N3")
def c13(page):
    note = page.evaluate(r"""() => {
      const n = [...document.querySelectorAll('#s3 .note.purple')].pop();
      if (!n) return null;
      const c = n.cloneNode(true); c.querySelectorAll('.dot').forEach(d => d.remove());
      return c.textContent.replace(/\s+/g, ' ').trim();
    }""")
    for sub in ("is not done manually on this screen", "#wholesale-ops", "#partnership-kr"):
        check(note and sub in note, f".note.purple below the table contains `{sub}`", note)


@scenario("QA-C-14", nav="N3")
def c14(page):
    foot = page.evaluate(r"""() => {
      const p = [...document.querySelectorAll('#s3 .pagepad > p.mut')].find(x => x.textContent.includes('Showing'));
      return p ? p.textContent.replace(/\s+/g, ' ').trim() : null;
    }""")
    exp = "Showing 7 of 13 request(s) · Status: REQUESTED 8 · PARTIAL 1 · INBOUNDED 3 · CANCELLED 1"
    check(foot == exp, f"footer line reads exactly `{exp}`", foot)
    rows = page.evaluate(
        r"() => [...document.querySelectorAll('#s3 .tbl > tbody > tr')].filter(r => !r.classList.contains('cpanel-ir')).length")
    check(rows == 7, "exactly 7 data rows rendered (excluding .cpanel-ir)", rows)


@scenario("QA-C-15", nav="N3")
def c15(page):
    page.evaluate(r"""() => [...document.querySelectorAll('#s3 button')]
      .find(b => b.textContent.replace(/\s+/g, ' ').trim() === '＋ New Inbound Request').click()""")
    check(has_class(page, "#s1", "on"), "#s1 becomes the active state", "not on")
    check(page.evaluate(r"""() => {
      const b = [...document.querySelectorAll('#s1 .pagetabs button')].find(x => x.textContent.trim() === 'New Request');
      return b.classList.contains('on');
    }"""), "`New Request` tab in #s1 .pagetabs carries class on", "not on")


@scenario("QA-C-16", nav="N3")
def c16(page):
    r = s3_row_sel(page, "202607130003")
    cell = page.eval_on_selector(f"{r} td:nth-child(4)", r"""el => ({
      b: el.querySelector('b') ? el.querySelector('b').textContent.trim() : null,
      txt: el.textContent.replace(/\s+/g, ' ').trim()})""")
    check(cell["b"] == "COSRX", "brand `COSRX` inside <b>", cell)
    check(cell["txt"] == "COSRX Advanced Snail 96 Mucin Essence, 100ml +2 more",
          "cell reads `COSRX Advanced Snail 96 Mucin Essence, 100ml +2 more`", cell["txt"])
    sku = T(page, f"{r} td:nth-child(5)")
    check(sku == "100040311 +2", "SKU cell reads `100040311 +2`", sku)
    r2 = s3_row_sel(page, "202607100005")
    cell2 = page.eval_on_selector(f"{r2} td:nth-child(4)", r"""el => ({
      b: el.querySelector('b') ? el.querySelector('b').textContent.trim() : null,
      txt: el.textContent.replace(/\s+/g, ' ').trim()})""")
    check(cell2["b"] == "Beauty of Joseon", "brand `Beauty of Joseon` in bold", cell2)
    check("Relief Sun, 50ml +1 more" in cell2["txt"], "with `Relief Sun, 50ml +1 more`", cell2["txt"])
    sku2 = T(page, f"{r2} td:nth-child(5)")
    check(sku2 == "100031820 +1", "SKU `100031820 +1`", sku2)


@scenario("QA-C-19", nav="N3")
def c19(page):
    st = page.evaluate(r"""() => {
      const nav = document.querySelector('#s3 .nav');
      const kids = [...nav.children].map(k => k.textContent.replace(/\s+/g, ' ').trim());
      const badge = nav.querySelector('.icon-btn .badge-n');
      const av = nav.querySelector('.user .avatar');
      return {kids, badgeBg: badge ? getComputedStyle(badge).backgroundColor : null,
              avatar: av ? av.textContent.trim() : null};
    }""")
    kids = st["kids"]
    check(kids[0] == "SkinSeoul", "brand `SkinSeoul` first", kids)
    check(kids[1:5] == ["Operation AI ▾", "Catalog Management ▾", "OMS Center ▾", "Site Management ▾"],
          "menu labels in order", kids)
    check(any(k.startswith("💬 Comments") for k in kids), "a `💬 Comments` button", kids)
    check(st["badgeBg"] == "rgb(220, 53, 69)", "red count badge", st["badgeBg"])
    check(any("Yongwon Ryu" in k for k in kids), "user block `Yongwon Ryu`", kids)
    check(st["avatar"] == "Y", "avatar initial `Y`", st["avatar"])
    check(kids[-1] == "Logout", "a `Logout` button last", kids)


@scenario("QA-C-24", nav="self")
def c24(page):
    page.goto("about:blank")
    page.goto(URL)
    # element exists before any click
    st = page.evaluate(r"""() => {
      const t = document.querySelector('#s3 .toast');
      if (!t) return null;
      const c = t.cloneNode(true); const s = c.querySelector('small');
      const small = s ? s.textContent.replace(/\s+/g, ' ').trim() : ''; if (s) s.remove();
      return {txt: c.textContent.replace(/\s+/g, ' ').trim(), small, id: t.id || '',
              gtoast: !!document.getElementById('gtoast')};
    }""")
    check(st is not None, "static .toast present inside #s3 before any click", "absent")
    check(st["txt"] == "✓ Inbound request registered — 202607130003",
          "reads `✓ Inbound request registered — 202607130003`", st["txt"])
    check(st["small"] == "No refresh · added to top of the list",
          "sub-line `No refresh · added to top of the list`", st["small"])
    check(st["id"] != "gtoast" and not st["gtoast"], "element is not #gtoast / not created by gtoastShow", st)
    page.click('.wf-tab[data-state="s3"]')
    page.wait_for_timeout(2900)
    vis = page.eval_on_selector("#s3 .toast", "el => getComputedStyle(el).display !== 'none'")
    check(vis, "static toast does not auto-hide (still visible after 2.6 s+)", vis)


@scenario("QA-C-25", nav="N3")
def c25(page):
    rows = page.evaluate(r"""() => [...document.querySelectorAll('#s3 .tbl > tbody > tr')]
      .filter(r => !r.classList.contains('cpanel-ir')).map(tr => {
        const no = tr.children[1].textContent.trim();
        const cell = tr.children[11];
        const e = cell.querySelectorAll('.req-edit'); const c = cell.querySelectorAll('.req-cancel');
        const cb = cell.querySelector('.comment-btn');
        const after = cb && e[0] && (cb.compareDocumentPosition(e[0]) & Node.DOCUMENT_POSITION_FOLLOWING) &&
                      e[0] && c[0] && (e[0].compareDocumentPosition(c[0]) & Node.DOCUMENT_POSITION_FOLLOWING);
        return {no, ne: e.length, nc: c.length,
                eTxt: e[0] && e[0].textContent.trim(), cTxt: c[0] && c[0].textContent.trim(),
                eDis: e[0] && e[0].disabled, cDis: c[0] && c[0].disabled,
                eGray: e[0] && e[0].classList.contains('btn-gray'), cGray: c[0] && c[0].classList.contains('btn-gray'),
                eTitle: e[0] && e[0].title, cTitle: c[0] && c[0].title, after: !!after};
      })""")
    check(len(rows) == 7 and all(r["ne"] == 1 and r["nc"] == 1 for r in rows),
          "every one of the 7 rows carries exactly one .req-edit and one .req-cancel", rows)
    check(all(r["eTxt"] == "✎ Edit" and r["cTxt"] == "Cancel" for r in rows),
          "labelled `✎ Edit` / `Cancel`", [(r["eTxt"], r["cTxt"]) for r in rows])
    check(all(r["after"] for r in rows), "both buttons after the .comment-btn", rows)
    by = {r["no"]: r for r in rows}
    for no in ("202607130003", "202607130002", "202607120004"):
        r = by[no]
        check(not r["eDis"] and not r["cDis"], f"row {no} (REQUESTED): both enabled", r)
        check(r["eTitle"] == "Edit request — REQUESTED only" and r["cTitle"] == "Cancel request — REQUESTED only",
              f"row {no} titles `Edit request — REQUESTED only` / `Cancel request — REQUESTED only`",
              (r["eTitle"], r["cTitle"]))
    r = by["202607120001"]
    check(r["eDis"] and r["cDis"] and r["eGray"] and r["cGray"],
          "row 202607120001 (PARTIAL): both disabled .btn-gray", r)
    check(r["eTitle"].startswith("Stock already received against this request")
          and r["cTitle"].startswith("Stock already received against this request"),
          "PARTIAL titles begin `Stock already received against this request`", (r["eTitle"], r["cTitle"]))
    for no in ("202607100005", "202607090002"):
        r = by[no]
        check(r["eDis"] and r["cDis"], f"row {no} (INBOUNDED): both disabled", r)
        check(r["eTitle"].startswith("Stock has already moved") and r["cTitle"].startswith("Stock has already moved"),
              f"row {no} titles begin `Stock has already moved`", (r["eTitle"], r["cTitle"]))
    r = by["202607110006"]
    check(r["eDis"] and r["cDis"], "row 202607110006 (CANCELLED): both disabled", r)
    check(r["eTitle"] == "Request cancelled — terminal" and r["cTitle"] == "Request cancelled — terminal",
          "CANCELLED titles exactly `Request cancelled — terminal`", (r["eTitle"], r["cTitle"]))


@scenario("QA-C-26", nav="N3")
def c26(page):
    r = s3_row_sel(page, "202607130002")
    page.click(f"{r} .req-cancel")
    check(has_class(page, "#m-cancel", "open"), "#m-cancel gains class open", "not open")
    hdr = T(page, "#m-cancel header", ".dot,.x")
    check(hdr == "Cancel Inbound Request — 202607130002",
          "header (excluding .x) reads exactly `Cancel Inbound Request — 202607130002` — live-bound", hdr)
    opts = T_all(page, "#mcReason option")
    check(opts == ["Purchase cancelled", "Wrong entry", "Other"],
          "#mcReason contains exactly `Purchase cancelled` / `Wrong entry` / `Other`", opts)
    page.evaluate(r"""() => [...document.querySelectorAll('#m-cancel .foot button')]
      .find(b => b.textContent.trim() === 'Keep request').click()""")
    check(not has_class(page, "#m-cancel", "open"), "Keep request: #m-cancel loses open", "still open")
    check(no_gtoast(page), "no #gtoast appears", gtoast(page))
    pill = T(page, f"{r} td:nth-child(11) .tag")
    check(pill == "REQUESTED", "row still renders the REQUESTED pill", pill)
    # reopen → Wrong entry → confirm
    page.click(f"{r} .req-cancel")
    page.select_option("#mcReason", label="Wrong entry")
    page.click("#mcConfirm")
    check(not has_class(page, "#m-cancel", "open"), "confirm: #m-cancel loses open", "still open")
    st = page.eval_on_selector(f"{r} td:nth-child(11)", r"""el => {
      const tag = el.querySelector('.tag'); const note = el.querySelector('.route-note');
      return {tag: tag ? tag.textContent.trim() : null, cls: tag ? tag.className : '',
              note: note ? note.textContent.replace(/\s+/g, ' ').trim() : null};
    }""")
    check(st["tag"] == "CANCELLED" and "tag-cancelled" in st["cls"],
          "Status cell renders the gray CANCELLED pill", st)
    check(st["note"] == "Wrong entry · just now", "note `Wrong entry · just now`", st["note"])
    dis = page.evaluate(r"""(sel) => { const tr = document.querySelector(sel);
      return {e: tr.querySelector('.req-edit').disabled, c: tr.querySelector('.req-cancel').disabled}; }""", r)
    check(dis["e"] and dis["c"], ".req-edit / .req-cancel become disabled", dis)
    tcell = page.eval_on_selector(f"{r} td:nth-child(7)", r"""el => {
      const note = el.querySelector('.route-note');
      return {txt: el.textContent.replace(/\s+/g, ' ').trim(),
              note: note ? note.textContent.replace(/\s+/g, ' ').trim() : null,
              addBtn: [...el.querySelectorAll('button')].filter(b => b.textContent.trim() === 'Add tracking').length};
    }""")
    check(tcell["txt"].startswith("–"), "Tracking No cell renders `–`", tcell["txt"])
    check(tcell["note"] == "Tracking matching deactivated", "note `Tracking matching deactivated`", tcell["note"])
    check(tcell["addBtn"] == 0, "no `Add tracking` button", tcell["addBtn"])
    g = gtoast(page)
    check(g["visible"] and g["bold"] == "✓ Inbound request cancelled",
          "#gtoast shows `✓ Inbound request cancelled`", g)
    check(g["small"] == "Row kept in the list for audit · Tracking matching deactivated · No refresh",
          "secondary line `Row kept in the list for audit · Tracking matching deactivated · No refresh`", g["small"])


@scenario("QA-C-27", nav="N3")
def c27(page):
    r = s3_row_sel(page, "202607130003")
    page.click(f"{r} .req-edit")
    check(has_class(page, "#s1", "on"), "#s1 becomes the active state", "not on")
    check(has_class(page, "#editBanner", "on"), "#editBanner gains class on", "not on")
    b = T(page, "#editBanner b")
    check(b == "Editing request 202607130003", "banner <b> reads exactly `Editing request 202607130003`", b)
    page.click("#s1 .submitrow .btn-blue")
    g = gtoast(page)
    check(g["visible"] and g["bold"] == "✓ Inbound request updated — 202607130003",
          "toast `✓ Inbound request updated — 202607130003`", g)
    check(g["small"] == "Changed fields logged as an auto-comment (old → new) · Requester notified on Slack · No refresh",
          "secondary line exact", g["small"])
    check(not has_class(page, "#editBanner", "on"), "#editBanner loses class on", "still on")
    page.click("#s1 .submitrow .btn-blue")
    g2 = gtoast(page)
    check(g2["bold"] == "✓ Inbound request registered",
          "second click shows the default registered toast — edit mode does not leak", g2)
    # Exit edit mode path
    page.click('.wf-tab[data-state="s3"]')
    page.click(f"{r} .req-edit")
    check(has_class(page, "#editBanner", "on"), "edit mode re-entered (banner on)", "not on")
    page.click("#editExit")
    check(not has_class(page, "#editBanner", "on"), "`Exit edit mode` hides the banner", "still on")
    page.click("#s1 .submitrow .btn-blue")
    g3 = gtoast(page)
    check(g3["bold"] == "✓ Inbound request registered",
          "next Register click toasts the registered copy", g3)


@scenario("QA-C-28", nav="N3")
def c28(page):
    r = s3_row_sel(page, "202607110006")
    st = page.eval_on_selector(r, r"""tr => {
      const route = tr.children[2].querySelector('.tag');
      const prod = tr.children[3]; const b = prod.querySelector('b');
      const qty = tr.children[5]; const tcell = tr.children[6];
      const tnote = tcell.querySelector('.route-note');
      const rd = tr.children[8];
      const scell = tr.children[10];
      const stag = scell.querySelector('.tag'); const snote = scell.querySelector('.route-note');
      const dot = scell.querySelector('.dot');
      return {
        route: route ? route.textContent.trim() : null,
        b: b ? b.textContent.trim() : null,
        prod: prod.textContent.replace(/\s+/g, ' ').trim(),
        qty: (() => { const c = qty.cloneNode(true); c.querySelectorAll('.dot').forEach(d => d.remove());
                      return c.textContent.replace(/\s+/g, ' ').trim(); })(),
        tTxt: tcell.textContent.replace(/\s+/g, ' ').trim(),
        tNote: tnote ? tnote.textContent.trim() : null,
        addBtn: [...tcell.querySelectorAll('button')].filter(x => x.textContent.trim() === 'Add tracking').length,
        rd: rd.textContent.trim(),
        sTag: stag ? stag.textContent.trim() : null, sCls: stag ? stag.className : '',
        sNote: snote ? snote.textContent.replace(/\s+/g, ' ').trim() : null,
        dot: dot ? dot.textContent.trim() : null,
        cb: !!tr.children[0].querySelector('input[type=checkbox]'),
        commentsDisabled: tr.querySelector('.comment-btn').disabled,
      };
    }""")
    check(st["route"] == "WHOLESALE", "WHOLESALE route tag", st["route"])
    check(st["b"] == "Torriden" and "Dive-In Low Molecular Hyaluronic Acid Serum, 50ml" in st["prod"],
          "`Torriden` in bold with `Dive-In Low Molecular Hyaluronic Acid Serum, 50ml`", st["prod"])
    check(st["qty"] == "150", "Qty 150", st["qty"])
    check(st["tTxt"].startswith("–") and st["tNote"] == "Tracking matching deactivated" and st["addBtn"] == 0,
          "muted `–` Tracking No cell + `Tracking matching deactivated`, no Add tracking button",
          (st["tTxt"], st["tNote"], st["addBtn"]))
    check(st["rd"] == "–", "en-dash Received Date", st["rd"])
    check(st["sTag"] == "CANCELLED" and "tag-cancelled" in st["sCls"], "gray CANCELLED pill", st)
    check(st["sNote"] == "Purchase cancelled · 07-12", "note `Purchase cancelled · 07-12`", st["sNote"])
    check(st["dot"] == "12", "annotation dot 12 on the Status cell", st["dot"])
    check(st["cb"], "checkbox present", st["cb"])
    check(not st["commentsDisabled"], "💬 Comments enabled", st["commentsDisabled"])


# ── Block D ────────────────────────────────────────────────────────────────

@scenario("QA-D-01", nav="NM")
def d01(page):
    check(has_class(page, "#m-invoice", "open"), "#m-invoice gains class open", "not open")
    hdr = T(page, "#m-invoice header", ".dot,.x")
    check(hdr == "Add Tracking No — 202607130003",
          "header (excluding .x) reads exactly `Add Tracking No — 202607130003`", hdr)
    body = T(page, "#m-invoice .body")
    check("Enter the tracking number(s) once the goods have shipped." in body,
          "body contains `Enter the tracking number(s) once the goods have shipped.`", body)
    check("One inbound request can hold multiple tracking numbers" in body,
          "body contains `One inbound request can hold multiple tracking numbers`", body)


@scenario("QA-D-02", nav="N3")
def d02(page):
    r = s3_row_sel(page, "202607130003")
    page.click(f"{r} td:nth-child(7) button")
    check(has_class(page, "#m-invoice", "open"), "the same #m-invoice overlay gains class open", "not open")


@scenario("QA-D-03", nav="NM")
def d03(page):
    n0 = count(page, "#tnList .qrow")
    check(n0 == 1, "#tnList contains exactly 1 .qrow", n0)
    page.click("#tnAdd")
    page.click("#tnAdd")
    st = page.evaluate(r"""() => {
      const rows = [...document.querySelectorAll('#tnList .qrow')];
      return {n: rows.length,
              ok: rows.every(r => r.querySelector('input') && r.querySelector('.tn-del') &&
                                  r.querySelector('.tn-del').textContent.trim() === '✕'),
              focused: document.activeElement === rows[rows.length - 1].querySelector('input')};
    }""")
    check(st["n"] == 3, "3 .qrow rows after two clicks", st["n"])
    check(st["ok"], "each row has an input and a .tn-del ✕ button", st)
    check(st["focused"], "newest input is document.activeElement", st)
    page.click("#tnList .qrow:nth-child(1) .tn-del")
    page.click("#tnList .qrow:nth-child(1) .tn-del")
    n2 = count(page, "#tnList .qrow")
    check(n2 == 1, "two rows removed, one survives", n2)
    page.fill("#tnList .qrow input", "TEST123")
    page.click("#tnList .qrow .tn-del")
    st2 = page.evaluate(r"""() => {
      const rows = document.querySelectorAll('#tnList .qrow');
      return {n: rows.length, val: rows[0] ? rows[0].querySelector('input').value : null};
    }""")
    check(st2["n"] == 1, "final row remains in the DOM — row count never reaches 0", st2["n"])
    check(st2["val"] == "", "typed marker TEST123 was cleared to empty string", st2["val"])


@scenario("QA-D-04", nav="NM")
def d04(page):
    page.click("#m-invoice .foot .btn-blue")
    check(not has_class(page, "#m-invoice", "open"), "#m-invoice loses class open", "still open")
    g = gtoast(page)
    check(g["visible"] and g["bold"] == "✓ Tracking number(s) saved",
          "toast `✓ Tracking number(s) saved`", g)
    check(g["small"] == "Every registered number is now matched to View Orders · No refresh",
          "secondary line `Every registered number is now matched to View Orders · No refresh`", g["small"])


@scenario("QA-D-05", nav="NM")
def d05(page):
    page.evaluate(r"""() => [...document.querySelectorAll('#m-invoice .foot button')]
      .find(b => b.textContent.trim() === 'Cancel').click()""")
    check(not has_class(page, "#m-invoice", "open"), "Cancel: modal loses open", "still open")
    check(no_gtoast(page), "no #gtoast appears (Cancel)", gtoast(page))
    page.click('.wf-tab[data-modal="m-invoice"]')
    page.click("#m-invoice header .x")
    check(not has_class(page, "#m-invoice", "open"), "header ✕: modal loses open", "still open")
    check(no_gtoast(page), "no #gtoast appears (✕)", gtoast(page))
    page.click('.wf-tab[data-modal="m-invoice"]')
    page.click("#m-invoice", position={"x": 10, "y": 10})
    check(not has_class(page, "#m-invoice", "open"), "backdrop click: modal loses open", "still open")
    check(no_gtoast(page), "no #gtoast appears (backdrop)", gtoast(page))


@scenario("QA-D-06", nav="NM")
def d06(page):
    ph = page.eval_on_selector("#tnList .qrow input", "el => el.placeholder")
    check(ph == "e.g. 10325661220417 — last-mile / Coupang tracking number",
          "first .qrow placeholder exact", ph)
    page.click("#tnAdd")
    ph2 = page.evaluate(r"() => [...document.querySelectorAll('#tnList .qrow input')].pop().placeholder")
    check(ph2 == "Additional tracking number", "appended row placeholder `Additional tracking number`", ph2)
    body = T(page, "#m-invoice .body")
    check("status stays REQUESTED" in body, "modal body contains `status stays REQUESTED`", body)
    titles = page.evaluate(r"() => [...document.querySelectorAll('#m-invoice .tn-del')].map(b => b.title)")
    check(all(t == "Remove this tracking number" for t in titles),
          "each .tn-del carries title `Remove this tracking number`", titles)


@scenario("QA-D-17", nav="NM")
def d17(page):
    page.click("#m-invoice", position={"x": 10, "y": 10})
    check(not has_class(page, "#m-invoice", "open"),
          "backdrop click outside .modal: #m-invoice loses class open", "still open")
    check(no_gtoast(page), "no toast appears — behaves exactly like Cancel", gtoast(page))


# ── Block F ────────────────────────────────────────────────────────────────

@scenario("QA-F-01")
def f01(page):
    page.click('[data-open="inbox1"]')
    check(has_class(page, "#inbox1", "open"), "#inbox1 gains class open", "not open")
    tabs = page.evaluate(r"""() => [...document.querySelectorAll('#inbox1 .tabs button')].map(b => ({
      txt: b.textContent.replace(/\s+/g, ' ').trim(),
      badge: b.querySelector('.badge-n') ? b.querySelector('.badge-n').textContent.trim() : null,
      on: b.classList.contains('on')}))""")
    check(len(tabs) == 2, "two tabs", tabs)
    check(tabs[0]["txt"].startswith("@ Mentions") and tabs[0]["badge"] == "2",
          "`@ Mentions` tab with badge 2", tabs[0])
    check(tabs[1]["txt"] == "★ Saved", "`★ Saved` tab", tabs[1])
    check(tabs[0]["on"] and not tabs[1]["on"], "`@ Mentions` carries class on", tabs)


@scenario("QA-F-02")
def f02(page):
    page.click('[data-open="inbox1"]')
    hdr = page.evaluate(r"""() => {
      const h = document.querySelector('#inbox1 [data-pane="mentions"] .paneheader');
      const c = h.cloneNode(true); const s = c.querySelector('small');
      const small = s ? s.textContent.replace(/\s+/g, ' ').trim() : ''; if (s) s.remove();
      return {txt: c.textContent.replace(/\s+/g, ' ').trim(), small};
    }""")
    check(hdr["txt"] == "Comments mentioning me · Click to open the order",
          "mentions pane header reads `Comments mentioning me · Click to open the order` (HUB-1)", hdr["txt"])
    check(hdr["small"] == "Mark all read", "action `Mark all read` (HUB-4)", hdr["small"])
    its = page.evaluate(r"""() => [...document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')].map(it => ({
      unread: it.classList.contains('unread'),
      b: it.querySelector('b') ? it.querySelector('b').textContent.trim() : null,
      txt: it.textContent.replace(/\s+/g, ' ').trim(),
      time: it.querySelector('time') ? it.querySelector('time').textContent.trim() : null}))""")
    check(len(its) == 2, "exactly two mentions-pane .it entries", len(its))
    check(all(i["unread"] for i in its), "both carry class unread", its)
    check([i["b"] for i in its] == ["202607130002", "202607120004"],
          "bold entity labels 202607130002 and 202607120004", [i["b"] for i in its])
    check('Dean: "@Yongwon when is the tracking number for this wholesale one coming?"' in its[0]["txt"]
          and its[0]["time"] == "11:20",
          "first entry Dean quote at 11:20", its[0])
    check('Miranti: "@Yongwon the partnership stock\'s expected arrival slipped by a day"' in its[1]["txt"]
          and its[1]["time"] == "Yesterday",
          "second entry Miranti quote at Yesterday", its[1])


@scenario("QA-F-03")
def f03(page):
    page.click('[data-open="inbox1"]')
    star = page.locator('#inbox1 [data-pane="mentions"] .it').first.locator(".star")
    before = star.evaluate("el => el.classList.contains('on')")
    star.click()
    after = star.evaluate("el => el.classList.contains('on')")
    check(after != before, "★ toggles class on", f"before={before} after={after}")
    page.click('#inbox1 .tabs button[data-tab="saved"]')
    hdr = page.evaluate(r"""() => {
      const h = document.querySelector('#inbox1 [data-pane="saved"] .paneheader');
      const c = h.cloneNode(true); const s = c.querySelector('small');
      const small = s ? s.textContent.replace(/\s+/g, ' ').trim() : ''; if (s) s.remove();
      return {txt: c.textContent.replace(/\s+/g, ' ').trim(), small,
              visible: getComputedStyle(h.closest('.tabpane')).display !== 'none'};
    }""")
    check(hdr["visible"], "saved pane visible after tab click", hdr)
    check(hdr["txt"] == "Saved comments · Click to open the order",
          "saved pane header `Saved comments · Click to open the order` (HUB-2)", hdr["txt"])
    check(hdr["small"] == "Unstar to remove from the list",
          "hint `Unstar to remove from the list` (HUB-3)", hdr["small"])


@scenario("QA-F-04", nav="N3")
def f04(page):
    r = s3_row_sel(page, "202607130002")
    page.click(f"{r} .comment-btn")
    st = page.evaluate(r"""(sel) => {
      const tr = document.querySelector(sel);
      const p = tr.nextElementSibling;
      if (!p || !p.classList.contains('cpanel-ir')) return null;
      const td = p.querySelector('td');
      const items = [...p.querySelectorAll('.c-item')].map(ci => ({
        who: ci.querySelector('.who') ? ci.querySelector('.who').textContent.trim() : null,
        txt: ci.textContent.replace(/\s+/g, ' ').trim(),
        time: ci.querySelector('time') ? ci.querySelector('time').textContent.trim() : null,
        at: ci.querySelector('.at') ? ci.querySelector('.at').textContent.trim() : null}));
      const inp = p.querySelector('.cwrite input');
      const btn = p.querySelector('.cwrite button');
      return {colspan: td.getAttribute('colspan'), items,
              ph: inp ? inp.placeholder : null, btn: btn ? btn.textContent.trim() : null};
    }""", r)
    check(st is not None, "a tr.cpanel-ir is inserted directly below the row", "no panel")
    check(st["colspan"] == "12", "spanning all 12 columns", st["colspan"])
    check(len(st["items"]) == 2, "listing two comments", st["items"])
    check(st["items"][0]["who"] == "Dean" and "Wholesale PO confirmed — expected arrival 07-18" in st["items"][0]["txt"]
          and st["items"][0]["time"] == "09:12",
          "Dean / `Wholesale PO confirmed — expected arrival 07-18` / 09:12", st["items"][0])
    check(st["items"][1]["who"] == "Yongwon" and "@Dean got it. I'll keep location row B open" in st["items"][1]["txt"]
          and st["items"][1]["time"] == "09:30",
          "Yongwon / `@Dean got it. I'll keep location row B open` / 09:30", st["items"][1])
    check(st["items"][1]["at"] == "@Dean", "`@Dean` wrapped in a .at span", st["items"][1]["at"])
    check(st["ph"] == "Write a comment — @name tags trigger a Slack alert",
          "input placeholder `Write a comment — @name tags trigger a Slack alert`", st["ph"])
    check(st["btn"] == "Post", "button labelled `Post`", st["btn"])


@scenario("QA-F-05", nav="N3")
def f05(page):
    r = s3_row_sel(page, "202607130002")
    page.click(f"{r} .comment-btn")
    n1 = count(page, "#s3 .cpanel-ir")
    page.click(f"{r} .comment-btn")
    n2 = count(page, "#s3 .cpanel-ir")
    check(n1 == 1 and n2 == 0, "second click removes the tr.cpanel-ir — the panel is a toggle", f"open:{n1} after:{n2}")


@scenario("QA-F-06", nav="N3")
def f06(page):
    r = s3_row_sel(page, "202607120001")
    page.click(f"{r} .comment-btn")
    st = page.evaluate(r"""(sel) => {
      const p = document.querySelector(sel).nextElementSibling;
      if (!p || !p.classList.contains('cpanel-ir')) return null;
      return {txt: p.textContent.replace(/\s+/g, ' ').trim(), write: !!p.querySelector('.cwrite input')};
    }""", r)
    check(st is not None, "panel injected", "no panel")
    check("No comments yet" in st["txt"], "panel renders `No comments yet`", st["txt"])
    check(st["write"], "plus the write box", st)


# ── Block G ────────────────────────────────────────────────────────────────

@scenario("QA-G-10", nav="self")
def g10(page):
    page.goto("about:blank")
    page.goto(URL)
    page.click('.wf-tab[data-state="s2"]')
    page.click('.wf-tab[data-state="s3"]')
    page.click('.wf-tab[data-modal="m-invoice"]')
    st = page.evaluate(r"""() => {
      const printCtl = [...document.querySelectorAll('button, a, input')]
        .filter(e => /print/i.test((e.textContent || '') + ' ' + (e.title || '') + ' ' + (e.value || ''))).length;
      const scripts = [...document.querySelectorAll('script')].map(s => s.textContent).join('\n');
      const audio = /\bAudio\b|\bAudioContext\b|\bspeechSynthesis\b/.test(scripts);
      const media = document.querySelectorAll('audio, video').length;
      const autof = document.querySelectorAll('input[autofocus]').length;
      const scanPh = [...document.querySelectorAll('input')]
        .filter(i => /scan|barcode|바코드/i.test(i.placeholder || '')).length;
      return {printCtl, audio, media, autof, scanPh};
    }""")
    check(st["printCtl"] == 0, "no button/a/input whose label or title contains `Print`", st["printCtl"])
    check(not st["audio"], "no Audio / AudioContext / speechSynthesis in the page script", st["audio"])
    check(st["media"] == 0, "no media element", st["media"])
    check(st["autof"] == 0, "no input autofocused for barcode capture", st["autof"])
    check(st["scanPh"] == 0, "no scan-oriented placeholder (scan / barcode / 바코드)", st["scanPh"])


@scenario("QA-G-16", nav="self")
def g16(page):
    page.goto("about:blank")
    page.goto(URL)
    page.click('.wf-tab[data-state="s2"]')
    page.click('.wf-tab[data-state="s3"]')
    page.click('.wf-tab[data-modal="m-invoice"]')
    st = page.evaluate(r"""() => {
      const strip = e => { const c = e.cloneNode(true); c.querySelectorAll('.dot').forEach(d => d.remove());
                           return c.textContent.replace(/\s+/g, ' ').trim(); };
      const dataModals = [...document.querySelectorAll('[data-modal]')].map(e => e.getAttribute('data-modal'));
      const inbLabels = [...document.querySelectorAll('.formcard label')].filter(l => l.textContent.includes('Inbound No.')).length
        + [...document.querySelectorAll('.formcard input, .formcard select')]
            .filter(i => ((i.placeholder || '') + (i.name || '')).includes('Inbound No.')).length;
      const foc = [...document.querySelectorAll('input[type=checkbox]')]
        .filter(c => /free of charge|FOC/i.test(((c.closest('label') || {}).textContent) || '')).length;
      const shipped = [...document.querySelectorAll('.chip, .tag, .pill, option, button')]
        .filter(e => e.textContent.includes('SHIPPED')).length;
      const sizeCarrier = [...document.querySelectorAll('th, label, td')]
        .filter(e => ['Size', 'Carrier'].includes(strip(e))).length
        + [...document.querySelectorAll('input, select, textarea')]
            .filter(i => ['Size', 'Carrier'].includes(i.placeholder || '') || ['Size', 'Carrier'].includes(i.name || '')).length;
      const reg1 = [...document.querySelectorAll('#s1 button')].filter(b => b.textContent.trim() === 'Register Inbound Request').length;
      const reg2 = [...document.querySelectorAll('#s2 button')].filter(b => b.textContent.trim() === 'Register Inbound Request').length;
      const regAll = [...document.querySelectorAll('button')].filter(b => b.textContent.trim() === 'Register Inbound Request').length;
      const rows = [...document.querySelectorAll('#s3 .tbl > tbody > tr')].filter(r => !r.classList.contains('cpanel-ir'));
      const inb = rows.filter(r => ['202607100005', '202607090002'].includes(r.children[1].textContent.trim()));
      const addOnInb = inb.reduce((a, r) => a + [...r.querySelectorAll('button')]
        .filter(b => b.textContent.trim() === 'Add tracking').length, 0);
      return {dataModals: [...new Set(dataModals)], inbLabels, foc, shipped, sizeCarrier, reg1, reg2, regAll, addOnInb};
    }""")
    check(st["dataModals"] == ["m-invoice"], "no element with data-modal other than m-invoice", st["dataModals"])
    check(st["inbLabels"] == 0, "no input/label containing `Inbound No.` inside a .formcard", st["inbLabels"])
    check(st["foc"] == 0, "no checkbox bound to a free-of-charge behavior", st["foc"])
    check(st["shipped"] == 0, "no .chip/.tag/.pill/<option>/<button> reading SHIPPED", st["shipped"])
    check(st["sizeCarrier"] == 0, "no th/label/form control/table cell labelled Size or Carrier", st["sizeCarrier"])
    check(st["reg1"] == 1 and st["reg2"] == 1 and st["regAll"] == 2,
          "exactly one `Register Inbound Request` button per state, no second submit button", st)
    check(st["addOnInb"] == 0, "no `Add tracking` button on rows 202607100005 / 202607090002", st["addOnInb"])


# ── main ───────────────────────────────────────────────────────────────────

def main():
    passed, failed, errored = [], [], []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()
        for sid, nav, fn in SCENARIOS:
            try:
                if nav != "self":
                    nav_to(page, nav)
                fn(page)
                passed.append(sid)
            except Fail as f:
                failed.append({"id": sid, "expected": f.expected, "actual": f.actual})
            except Exception:
                errored.append({"id": sid, "error": traceback.format_exc(limit=3)})
        browser.close()
    out = {
        "total": len(SCENARIOS),
        "passed": len(passed),
        "failed": failed,
        "errored": errored,
        "passed_ids": passed,
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
    return 0 if not failed and not errored else 1


if __name__ == "__main__":
    sys.exit(main())
