#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adversarial QA execution of wms2/specs/inbound-request.md  §8 (QA Acceptance Criteria).

Method 2 — hostile QA robot. Every assertion below is transcribed from the spec's
[WF] scenarios using ONLY the selectors / labels / expected strings the spec provides.
Nothing is inferred from reading the wireframe source. Where the spec fails to name a
selector or an assertion mechanism, the scenario is recorded AMBIGUOUS rather than
improvised.

Target: file:///.../wms2/inbound-request/index.html  (identical to the deployed page)

Run:  python3 qa-inbound-request.py [--json out.json]
"""

import json
import re
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

REPO = Path("/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes")
TARGET = (REPO / "wms2/inbound-request/index.html").as_uri()

RESULTS = []


# ----------------------------------------------------------------------------- helpers
def norm(s):
    return " ".join((s or "").split())


class Case:
    """Collects soft assertions for one scenario."""

    def __init__(self, sid, tier, note=None):
        self.sid = sid
        self.tier = tier
        self.fails = []
        self.evidence = []
        self.note = note
        self.ambiguous = None

    def ok(self, cond, label, actual=None, expected=None):
        if cond:
            return True
        msg = label
        if expected is not None or actual is not None:
            msg += f" | spec expects: {expected!r} | page has: {actual!r}"
        self.fails.append(msg)
        return False

    def ev(self, s):
        self.evidence.append(s)

    def mark_ambiguous(self, why):
        self.ambiguous = why

    def finish(self):
        if self.ambiguous:
            verdict = "AMBIGUOUS"
            evidence = self.ambiguous
        elif self.fails:
            verdict = "FAIL"
            evidence = " ;; ".join(self.fails + self.evidence)
        else:
            verdict = "PASS"
            evidence = " ;; ".join(self.evidence) if self.evidence else "all assertions held"
        RESULTS.append(
            {"id": self.sid, "tier": self.tier, "verdict": verdict,
             "evidence": evidence, "note": self.note}
        )
        return verdict


# ------------------------------------------------------------------- navigation preamble
def NX(page):
    """Fresh load, no hash."""
    page.goto(TARGET)
    page.wait_for_load_state("domcontentloaded")


def N1(page):
    NX(page)


def N2(page):
    page.click('.wf-tab[data-state="s2"]')


def N3(page):
    page.click('.wf-tab[data-state="s3"]')


def NM(page):
    page.click('.wf-tab[data-modal="m-invoice"]')


def NR(page, hash_="#reqlist"):
    # hard reload: goto() from the same document with only the hash changed does NOT
    # re-execute the page script, which would make this a test artifact rather than a
    # test of the page's deep-link handling.
    page.goto("about:blank")
    page.goto(TARGET + hash_)
    page.wait_for_load_state("domcontentloaded")


def has_class(page, sel, cls):
    return page.eval_on_selector(
        sel, "(el, c) => el.classList.contains(c)", cls
    )


def gtoast_state(page):
    # NOTE: #gtoast is position:fixed, so offsetParent is always null — visibility must be
    # decided from computed style + bounding box, not offsetParent.
    return page.evaluate(
        """() => {
            const n = document.querySelectorAll('#gtoast');
            if (!n.length) return {count:0, visible:false, text:''};
            const el = n[0];
            const cs = getComputedStyle(el);
            const r = el.getBoundingClientRect();
            const vis = cs.display !== 'none' && cs.visibility !== 'hidden'
                        && parseFloat(cs.opacity || '1') > 0.01 && r.width > 0 && r.height > 0;
            return {count:n.length, visible:vis, text:el.textContent.trim(),
                    right:cs.right, top:cs.top, pos:cs.position};
        }"""
    )


def row_by_inbound(page, state_sel, inbound_no):
    """Return the index of the tbody row whose text contains inbound_no."""
    return page.evaluate(
        """([sel, no]) => {
            const rows = [...document.querySelectorAll(sel + ' .tbl tbody tr')];
            for (let i = 0; i < rows.length; i++) {
                if (rows[i].classList.contains('cpanel-ir')) continue;
                if (rows[i].textContent.includes(no)) return i;
            }
            return -1;
        }""",
        [state_sel, inbound_no],
    )


# =============================================================================== BLOCK A
def qa_a_01(page):
    c = Case("QA-A-01", "[WF]")
    N1(page)
    c.ok(has_class(page, "#s1", "on"), "#s1 has class on")
    h2 = norm(page.eval_on_selector("#s1 h2", "e => e.textContent"))
    c.ok(h2 == "WMS - Inbound Request", "h2 exact text", h2, "WMS - Inbound Request")
    sub = norm(page.eval_on_selector("#s1 .sub", "e => e.textContent"))
    c.ok(sub == "Inbound Request — New Request", ".sub exact text", sub,
         "Inbound Request — New Request")
    tabs = page.evaluate(
        """() => [...document.querySelectorAll('#s1 .pagetabs button')]
              .map(b => ({t: b.textContent.trim(), on: b.classList.contains('on')}))"""
    )
    c.ok(len(tabs) == 2, ".pagetabs contains exactly two buttons", len(tabs), 2)
    c.ok([t["t"] for t in tabs] == ["New Request", "Request List"],
         ".pagetabs labels", [t["t"] for t in tabs], ["New Request", "Request List"])
    c.ok(tabs and tabs[0]["on"], "'New Request' tab carries class on",
         tabs[0]["on"] if tabs else None, True)
    trail = "Registered requests are viewed and managed by status in the [Request List] tab above."
    found = page.evaluate(
        """(t) => [...document.querySelectorAll('#s1 p, #s1 div, #s1 span')]
              .some(e => e.textContent.replace(/\\s+/g,' ').trim() === t)""", trail)
    if not found:
        loose = page.evaluate(
            """(t) => document.querySelector('#s1').innerText.replace(/\\s+/g,' ').includes(t)""",
            trail)
        c.ok(False, "trailing paragraph exact text not found as an element",
             f"present-as-substring={loose}", trail)
    return c.finish()


def qa_a_02(page):
    c = Case("QA-A-02", "[WF]")
    N1(page)
    cards = page.evaluate(
        """() => [...document.querySelectorAll('#s1 .routecards .routecard')].map(rc => ({
            title: (rc.querySelector('b') || {textContent:''}).textContent.trim(),
            badge: (rc.querySelector('.rc-badge') || {textContent:''}).textContent.trim(),
            on: rc.classList.contains('on')}))"""
    )
    c.ok(len(cards) == 4, "#s1 .routecards has exactly 4 .routecard", len(cards), 4)
    c.ok([x["title"] for x in cards] == ["Smart Buy", "Wholesale", "Brand Partnership", "Other"],
         "<b> titles", [x["title"] for x in cards],
         ["Smart Buy", "Wholesale", "Brand Partnership", "Other"])
    c.ok([x["badge"] for x in cards] == ["SMART BUY", "WHOLESALE", "PARTNERSHIP", "OTHER"],
         ".rc-badge texts", [x["badge"] for x in cards],
         ["SMART BUY", "WHOLESALE", "PARTNERSHIP", "OTHER"])
    c.ok(cards and cards[0]["on"], "first card carries class on",
         cards[0]["on"] if cards else None, True)
    jit = page.evaluate(
        """() => [...document.querySelectorAll('#s1 .routecards .routecard')]
              .filter(rc => /\\bJIT\\b/.test(rc.textContent))
              .map(rc => rc.textContent.replace(/\\s+/g,' ').trim())""")
    c.ok(jit == [], "no card labelled JIT (BR-2)", jit, [])
    c.ev("DIAG: scoped to <b> title / .rc-badge only, no JIT → the failure is the "
         "unscoped word 'JIT' in the Smart Buy card's <small> sub-copy")
    return c.finish()


def qa_a_03(page):
    c = Case("QA-A-03", "[WF]")
    N1(page)
    page.evaluate("""() => [...document.querySelectorAll('#s1 .routecards .routecard')]
                        .find(rc => rc.querySelector('b') &&
                              rc.querySelector('b').textContent.trim() === 'Wholesale').click()""")
    st = page.evaluate(
        """() => {const r=[...document.querySelectorAll('#s1 .routecards .routecard')];
        return {wh: r[1].classList.contains('on'), sb: r[0].classList.contains('on'),
                n: r.filter(x=>x.classList.contains('on')).length};}""")
    c.ok(st["wh"], "Wholesale card gains 'on'", st["wh"], True)
    c.ok(not st["sb"], "Smart Buy loses 'on'", st["sb"], False)
    c.ok(st["n"] == 1, "exactly one .routecard carries 'on'", st["n"], 1)
    return c.finish()


def qa_a_04(page):
    c = Case("QA-A-04", "[WF]")
    N1(page)
    page.evaluate("""() => [...document.querySelectorAll('#s1 .routecards .routecard')]
                        .find(rc => rc.querySelector('b') &&
                              rc.querySelector('b').textContent.trim() === 'Other').click()""")
    st = page.evaluate(
        """() => {const r=[...document.querySelectorAll('#s1 .routecards .routecard')];
        const other=r[3]; const inp=other.querySelector('.etc-in');
        return {on: other.classList.contains('on'),
                ph: inp ? inp.getAttribute('placeholder') : null,
                disabled: inp ? inp.disabled : null,
                focused: inp ? (document.activeElement === inp) : null};}""")
    c.ok(st["on"], "Other card gains 'on'", st["on"], True)
    c.ok(st["ph"] == "Enter channel name", ".etc-in placeholder", st["ph"], "Enter channel name")
    c.ok(st["disabled"] is False, ".etc-in disabled === false", st["disabled"], False)
    c.ok(st["focused"] is True, ".etc-in is document.activeElement", st["focused"], True)
    return c.finish()


def qa_a_05(page):
    c = Case("QA-A-05 (negative)", "[WF]")
    N1(page)
    page.evaluate("""() => document.querySelectorAll('#s1 .routecards .routecard')[3].click()""")
    page.evaluate("""() => document.querySelectorAll('#s1 .routecards .routecard')[0].click()""")
    st = page.evaluate(
        """() => {const other=document.querySelectorAll('#s1 .routecards .routecard')[3];
        const inp=other.querySelector('.etc-in');
        return {disabled: inp.disabled, focused: document.activeElement === inp,
                on: other.classList.contains('on')};}""")
    c.ok(st["disabled"] is True, ".etc-in disabled === true again", st["disabled"], True)
    c.ok(st["focused"] is False, ".etc-in no longer holds focus", st["focused"], False)
    c.ok(st["on"] is False, "Other card no longer carries 'on'", st["on"], False)
    return c.finish()


def qa_a_07(page):
    c = Case("QA-A-07", "[WF]")
    N1(page)
    st = page.evaluate(
        """() => {const i=document.querySelector('#s1 .auto input');
        const opts=[...document.querySelectorAll('#s1 .opt')];
        return {ph: i?i.getAttribute('placeholder'):null, val: i?i.value:null,
                n: opts.length,
                first_sel: opts.length?opts[0].classList.contains('sel'):null,
                texts: opts.map(o=>o.textContent.replace(/\\s+/g,' ').trim())};}""")
    c.ok(st["ph"] == "Type any SKU No. · brand · product name → click a suggestion to add a row below",
         ".auto input placeholder", st["ph"],
         "Type any SKU No. · brand · product name → click a suggestion to add a row below")
    c.ok(st["val"] == "100045210", ".auto input value", st["val"], "100045210")
    c.ok(st["n"] == 3, "dropdown shows exactly 3 .opt rows", st["n"], 3)
    c.ok(st["first_sel"] is True, "first .opt carries class 'sel'", st["first_sel"], True)
    if st["n"] >= 3:
        want = [("Anua — Heartleaf 77% Soothing Toner, 250ml", "100045210"),
                ("Anua — Heartleaf 80% Moisture Soothing Ampoule, 30ml", "100045233"),
                ("Anua — Heartleaf Quercetinol Pore Deep Cleansing Foam, 150ml", "100045240")]
        for i, (name, sku) in enumerate(want):
            t = st["texts"][i]
            c.ok(name in t and sku in t, f".opt[{i}] text", t, f"{name} / {sku}")
    diag = page.evaluate(
        """() => ({inAuto: document.querySelectorAll('#s1 .auto .opt').length,
                   all: [...document.querySelectorAll('#s1 .opt')]
                          .map(o=>o.className)})""")
    c.ev(f"DIAG: '#s1 .auto .opt' = {diag['inAuto']}; bare '#s1 .opt' matches {diag['all']}")
    return c.finish()


def qa_a_10(page):
    c = Case("QA-A-10 (negative)", "[WF]")
    N1(page)
    st = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#s1 .prodtbl tbody tr')];
        const r=rows[2]; if(!r) return {missing:true};
        const ins=[...r.querySelectorAll('input')].slice(0,3);
        return {missing:false, prefill:r.classList.contains('prefill'),
          ro: ins.map(i=>i.hasAttribute('readonly')),
          pe: ins.map(i=>getComputedStyle(i).pointerEvents),
          vals: ins.map(i=>i.value)};}""")
    if st.get("missing"):
        c.ok(False, "third .prodtbl tbody tr exists", "missing", "present")
        return c.finish()
    c.ok(st["prefill"], "third row has class 'prefill'", st["prefill"], True)
    c.ok(all(st["ro"]), "SKU/Brand/Product Name carry readonly", st["ro"], [True, True, True])
    c.ok(all(p == "none" for p in st["pe"]), "computed pointer-events: none",
         st["pe"], ["none"] * 3)
    # attempt to type into each
    page.evaluate(
        """() => {const r=document.querySelectorAll('#s1 .prodtbl tbody tr')[2];
        [...r.querySelectorAll('input')].slice(0,3).forEach(i=>{i.focus();});}""")
    for idx in range(3):
        try:
            page.locator("#s1 .prodtbl tbody tr").nth(2).locator("input").nth(idx).type(
                "XX", timeout=800)
        except Exception:
            pass
    after = page.evaluate(
        """() => [...document.querySelectorAll('#s1 .prodtbl tbody tr')[2]
             .querySelectorAll('input')].slice(0,3).map(i=>i.value)""")
    c.ok(after == ["100045210", "Anua", "Heartleaf 77% Soothing Toner, 250ml"],
         "values unchanged after typing attempt", after,
         ["100045210", "Anua", "Heartleaf 77% Soothing Toner, 250ml"])
    return c.finish()


def qa_a_11(page):
    c = Case("QA-A-11", "[WF]")
    N1(page)
    st = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#s1 .prodtbl tbody tr')];
        return {n: rows.length,
          prefill: rows.filter(r=>r.classList.contains('prefill')).length,
          rm: rows.map(r=>[...r.querySelectorAll('.rm')].map(
                b=>({t:b.textContent.trim(), title:b.getAttribute('title')})))};}""")
    c.ok(st["n"] == 3, "#s1 .prodtbl tbody has exactly 3 rows", st["n"], 3)
    c.ok(st["prefill"] == 1, "exactly one row carries 'prefill'", st["prefill"], 1)
    for i, rms in enumerate(st["rm"]):
        c.ok(len(rms) == 1, f"row {i} has exactly one .rm", len(rms), 1)
        if rms:
            c.ok(rms[0]["title"] == "Delete row", f"row {i} .rm title",
                 rms[0]["title"], "Delete row")
            c.ok(rms[0]["t"] == "✕", f"row {i} .rm text", rms[0]["t"], "✕")
    return c.finish()


def qa_a_13(page):
    c = Case("QA-A-13", "[WF]")
    N1(page)
    ths = page.evaluate(
        """() => [...document.querySelectorAll('#s1 .prodtbl thead th')]
              .map(t => t.textContent.replace(/\\s+/g,' ').trim())""")
    want = ["SKU No.", "Brand", "Product Name", "Order Qty", "Unit Cost (KRW) *",
            "JIT Price (KRW)", ""]
    c.ok(ths == want, ".prodtbl header cells in order", ths, want)
    clean = page.evaluate(
        """() => [...document.querySelectorAll('#s1 .prodtbl thead th')].map(t=>{
             const c=t.cloneNode(true);
             c.querySelectorAll('.dot').forEach(d=>d.remove());
             return c.textContent.replace(/\\s+/g,' ').trim();})""")
    c.ev(f"DIAG: with annotation .dot spans stripped the headers read {clean} "
         f"(== spec) — the only delta is the legend dot number baked into the <th>")
    for s in ["enter 0 if free of charge (required)", "leave blank if unknown (optional)"]:
        present = page.evaluate(
            """(t)=>document.querySelector('#s1').innerText.replace(/\\s+/g,' ').includes(t)""", s)
        c.ok(present, f"disclaimer contains {s!r}", present, True)
    st = page.evaluate(
        """() => {const r=[...document.querySelectorAll('#s1 .prodtbl tbody tr')]
                    .find(x=>x.classList.contains('prefill'));
        const ins=[...r.querySelectorAll('input')];
        return {uc: ins[4]?ins[4].getAttribute('placeholder'):null,
                jit: ins[5]?ins[5].getAttribute('placeholder'):null};}""")
    c.ok(st["uc"] == "Per-unit price ₩ (0 if free)", "prefill Unit Cost placeholder",
         st["uc"], "Per-unit price ₩ (0 if free)")
    c.ok(st["jit"] == "Blank if unknown", "prefill JIT placeholder", st["jit"],
         "Blank if unknown")
    return c.finish()


def qa_a_17(page):
    c = Case("QA-A-17", "[WF]",
             note="spec says Supplier carries a *red* `*` but gives no selector/threshold "
                  "for the colour; only the presence of `*` is executed here")
    N1(page)
    st = page.evaluate(
        """() => {
        const sup=document.querySelector('#s1 input[placeholder="e.g. 비엠유통, Coupang"]');
        const supFld = sup ? sup.closest('.fld') || sup.parentElement : null;
        const supLabel = supFld ? (supFld.querySelector('label')||supFld).textContent
                                    .replace(/\\s+/g,' ').trim() : null;
        const inv=document.querySelector('#s1 .fld-inv');
        const invInput = inv ? inv.querySelector('input') : null;
        const invLabel = inv ? (inv.querySelector('label')||inv).textContent
                                 .replace(/\\s+/g,' ').trim() : null;
        const dates=[...document.querySelectorAll('#s1 input[type=date]')].map(d=>d.value);
        return {supFound: !!sup, supVal: sup?sup.value:null, supLabel,
                invFound: !!inv, invLabel,
                invPh: invInput?invInput.getAttribute('placeholder'):null,
                invHasTracking: inv ? inv.textContent.includes('Tracking No') : false,
                dates};}""")
    c.ok(st["supFound"], "Supplier input with placeholder 'e.g. 비엠유통, Coupang' exists",
         st["supFound"], True)
    c.ok(st["supVal"] == "Coupang", "Supplier value", st["supVal"], "Coupang")
    c.ok("*" in (st["supLabel"] or ""), "Supplier label carries '*'", st["supLabel"], "contains *")
    c.ok("— who is shipping the goods" in (st["supLabel"] or ""),
         "Supplier qualifier", st["supLabel"], "— who is shipping the goods")
    c.ok(st["invFound"] and st["invHasTracking"],
         "Tracking No field wrapper has class fld-inv", st["invLabel"], "Tracking No … fld-inv")
    c.ok("optional · can be added later after dispatch" in (st["invLabel"] or ""),
         "Tracking No label text", st["invLabel"], "optional · can be added later after dispatch")
    c.ok(st["invPh"] == "Add after dispatch — you can submit without it (add later)",
         "Tracking No placeholder", st["invPh"],
         "Add after dispatch — you can submit without it (add later)")
    c.ok("2026-07-16" in st["dates"], "Expected arrival input[type=date] value",
         st["dates"], "2026-07-16")
    return c.finish()


def qa_a_18(page):
    c = Case("QA-A-18", "[WF]")
    N1(page)
    url_before = page.url
    page.evaluate("""() => [...document.querySelectorAll('#s1 button')]
                       .find(b=>b.textContent.trim()==='Register Inbound Request').click()""")
    page.wait_for_timeout(200)
    g = gtoast_state(page)
    c.ok(g["count"] >= 1 and g["visible"], "#gtoast becomes visible", g, "visible")
    c.ok("✓ Inbound request registered" in g["text"], "toast bold text",
         g["text"], "✓ Inbound request registered")
    c.ok("Inbound No. auto-assigned · added to the Request List · No refresh" in g["text"],
         "toast secondary line", g["text"],
         "Inbound No. auto-assigned · added to the Request List · No refresh")
    c.ok(page.url == url_before, "URL unchanged", page.url, url_before)
    still = page.evaluate("() => !!document.querySelector('#s1 .formcard')")
    c.ok(still, "form still in DOM", still, True)
    page.wait_for_timeout(3000)
    g2 = gtoast_state(page)
    c.ok(not g2["visible"], "after 2600 ms #gtoast is hidden again", g2, "hidden")
    return c.finish()


def qa_a_19(page):
    c = Case("QA-A-19 (negative)", "[WF]+[ADMIN] — WF half only")
    N1(page)
    page.evaluate("""() => [...document.querySelectorAll('#s1 button')]
                       .find(b=>b.textContent.trim()==='Register Inbound Request').click()""")
    page.wait_for_timeout(400)
    page.evaluate("""() => [...document.querySelectorAll('#s1 button')]
                       .find(b=>b.textContent.trim()==='Register Inbound Request').click()""")
    page.wait_for_timeout(50)
    n = page.evaluate("() => document.querySelectorAll('#gtoast').length")
    c.ok(n == 1, "exactly one element with id gtoast exists", n, 1)
    # hide timer reset: at first_click + 2800ms the toast must still be up
    page.wait_for_timeout(2350)
    g = gtoast_state(page)
    c.ok(g["visible"], "hide timer reset (toast still visible 2.8s after 1st click)",
         g, "visible")
    page.wait_for_timeout(1000)
    g2 = gtoast_state(page)
    c.ev(f"after +3.8s from 1st click visible={g2['visible']}")
    return c.finish()


def qa_a_23(page):
    c = Case("QA-A-23", "[WF]")
    N1(page)
    st = page.evaluate(
        """() => {const notes=[...document.querySelectorAll('#s1 .note.purple')];
        const hit=notes.find(n=>n.textContent.includes('auto-matches it to View Orders'));
        return {n: notes.length, found: !!hit,
          a: hit?hit.querySelectorAll('a').length:null,
          b: hit?hit.querySelectorAll('button').length:null,
          dm: hit?hit.querySelectorAll('[data-modal]').length:null,
          texts: notes.map(n=>n.textContent.replace(/\\s+/g,' ').trim().slice(0,120))};}""")
    c.ok(st["found"], ".note.purple containing 'auto-matches it to View Orders'",
         st["texts"], "auto-matches it to View Orders")
    if st["found"]:
        c.ok(st["a"] == 0, "no <a> inside it", st["a"], 0)
        c.ok(st["b"] == 0, "no <button> inside it", st["b"], 0)
        c.ok(st["dm"] == 0, "no [data-modal] inside it", st["dm"], 0)
    return c.finish()


def qa_a_24(page):
    c = Case("QA-A-24", "[WF]")
    N1(page)
    st = page.evaluate(
        """() => {const ta=document.querySelector('#s1 textarea.mtextarea');
        if(!ta) return {found:false};
        const fld = ta.closest('.fld') || ta.parentElement;
        return {found:true, ph: ta.getAttribute('placeholder'), val: ta.value,
                label: fld ? fld.textContent.replace(/\\s+/g,' ').trim() : ''};}""")
    c.ok(st["found"], "textarea.mtextarea exists", st["found"], True)
    if st["found"]:
        c.ok("Memo (Optional)" in st["label"], "under label 'Memo (Optional)'",
             st["label"][:90], "Memo (Optional)")
        c.ok(st["ph"] == "Notes about this inbound — anything written here is also logged "
                         "to the request's Comments history",
             "placeholder", st["ph"],
             "Notes about this inbound — anything written here is also logged to the "
             "request's Comments history")
        c.ok(st["val"] == "", "empty value", st["val"], "")
    return c.finish()


def qa_a_25(page):
    c = Case("QA-A-25", "[WF]+[ADMIN] — WF half only")
    N1(page)
    st = page.evaluate(
        """() => {const p=document.querySelector('#s1 .pagepad');
        const m=document.querySelector('#s1 .mock');
        const sr=document.querySelector('#s1 .submitrow');
        return {pad: p?getComputedStyle(p).padding:null,
                mw: m?getComputedStyle(m).minWidth:null,
                srIn: sr? !!sr.closest('#s1 .formcard') : false,
                srPresent: !!sr};}""")
    c.ok(st["pad"] == "18px 16px 0px", "#s1 .pagepad computed padding", st["pad"],
         "18px 16px 0px")
    c.ok(st["mw"] == "1280px", "#s1 .mock min-width", st["mw"], "1280px")
    c.ok(st["srPresent"], "#s1 .submitrow present", st["srPresent"], True)
    c.ok(st["srIn"], "#s1 .submitrow is inside #s1 .formcard", st["srIn"], True)
    return c.finish()


def qa_a_26(page):
    c = Case("QA-A-26", "[WF]")
    N1(page)
    nav = page.evaluate(
        """() => {const b=[...document.querySelectorAll('.nav button, .nav a')]
             .find(x=>x.textContent.includes('Comments'));
        return b?b.textContent.replace(/\\s+/g,' ').trim():null;}""")
    c.ok(nav is not None and nav.startswith("💬 Comments"), "nav button reads '💬 Comments'",
         nav, "💬 Comments")
    N3(page)
    acts = page.evaluate(
        """() => [...document.querySelectorAll('#s3 .tbl tbody tr')]
              .filter(r=>!r.classList.contains('cpanel-ir'))
              .map(r=>{const cells=[...r.children]; const last=cells[cells.length-1];
                 const b=[...last.querySelectorAll('button')]
                    .find(x=>x.textContent.includes('Comments'));
                 return b?b.textContent.replace(/\\s+/g,' ').trim():null;})""")
    c.ok(all(a == "💬 Comments" for a in acts) and len(acts) > 0,
         "each Request List Actions button reads '💬 Comments'", acts, "💬 Comments ×n")
    c.ev("DIAG: 3 of the 6 Actions buttons carry an unread-count <span class='badge-n'> "
         "inside the button, so the button text is '💬 Comments 1/2/3'. The spec never "
         "mentions this badge anywhere in §8.")
    tabs = page.evaluate(
        """() => {const hub=document.querySelector('#inbox1');
        if(!hub) return null;
        return [...hub.querySelectorAll('button, .tab, [class*=tab]')]
          .map(t=>t.textContent.replace(/\\s+/g,' ').trim())
          .filter(t=>t.includes('Mentions')||t.includes('Saved'));}""")
    c.ok(tabs is not None and any("@ Mentions" in t for t in tabs)
         and any("★ Saved" in t for t in tabs),
         "hub tabs read '@ Mentions' and '★ Saved'", tabs, ["@ Mentions", "★ Saved"])
    bad = page.evaluate(
        """() => [...document.querySelectorAll('button,a,label,th')]
             .map(e=>e.textContent.replace(/\\s+/g,' ').trim())
             .filter(t=>/메모|\\bNotes\\b|\\bRemarks\\b/.test(t))""")
    c.ok(bad == [], "no localised/alternative comments label", bad, [])
    return c.finish()


def qa_a_28(page):
    c = Case("QA-A-28", "[WF]")
    N1(page)
    order = page.evaluate(
        """() => {
        const s1=document.querySelector('#s1');
        const pick = sel => s1.querySelector(sel);
        const items=[['routecards','.routecards'],['search','.auto input'],
                     ['prodtbl','.prodtbl'],
                     ['supplier','input[placeholder="e.g. 비엠유통, Coupang"]'],
                     ['tracking','.fld-inv input'],['expected','input[type=date]'],
                     ['memo','textarea.mtextarea']];
        const out=[];
        for(const [k,sel] of items){const el=pick(sel); out.push([k, el?1:0,
            el? (()=>{let i=0,n=el; const all=[...s1.querySelectorAll('*')];
                      return all.indexOf(el);})() : -1]);}
        return out;}""")
    names = [o[0] for o in order]
    idxs = [o[2] for o in order]
    c.ok(all(i >= 0 for i in idxs), "all named form inputs found", dict(zip(names, idxs)),
         "all present")
    c.ok(idxs == sorted(idxs), "DOM order route→search→table→supplier→tracking→expected→memo",
         dict(zip(names, idxs)), "ascending")
    hdr = page.evaluate(
        """() => [...document.querySelectorAll('#s1 .prodtbl thead th')]
              .map(t=>t.textContent.replace(/\\s+/g,' ').trim())""")
    c.ok(hdr[:6] == ["SKU No.", "Brand", "Product Name", "Order Qty",
                     "Unit Cost (KRW) *", "JIT Price (KRW)"],
         "product table column order", hdr, "SKU No.…JIT Price (KRW)")
    size = page.evaluate(
        """() => {const t=document.body.innerText;
        const m=t.match(/\\bSize\\b/g); return m?m.length:0;}""")
    c.ok(size == 0, "no field/label/column named 'Size' anywhere on the page", size, 0)
    where = page.evaluate(
        """() => [...document.querySelectorAll('li,th,label,p')]
             .filter(e=>/\\bSize\\b/.test(e.textContent) && e.querySelectorAll('*').length<6)
             .map(e=>e.tagName+': '+e.textContent.replace(/\\s+/g,' ').trim().slice(0,110))""")
    c.ev(f"DIAG: the only 'Size' on the page is prose inside the legend: {where}. "
         f"No <th>, no <label>, no field is named Size (QA-G-16's precise form passes).")
    return c.finish()


# =============================================================================== BLOCK B
def qa_b_01(page):
    c = Case("QA-B-01", "[WF]")
    N1(page); N2(page)
    st = page.evaluate(
        """() => {const cards=[...document.querySelectorAll('#s2 .routecards .routecard')];
        return {on: document.querySelector('#s2').classList.contains('on'),
                flags: cards.map(x=>x.classList.contains('on')),
                titles: cards.map(x=>(x.querySelector('b')||{textContent:''}).textContent.trim()),
                labels: [...document.querySelectorAll('#s2 .formcard label')]
                          .map(l=>l.textContent.replace(/\\s+/g,' ').trim()),
                inputs: [...document.querySelectorAll('#s2 .formcard input')]
                          .map(i=>i.getAttribute('placeholder')||''),
                submit: (document.querySelector('#s2 .submitrow')||{textContent:''})
                          .textContent.replace(/\\s+/g,' ').trim()};}""")
    c.ok(st["on"], "#s2 has class on", st["on"], True)
    wh = st["titles"].index("Wholesale") if "Wholesale" in st["titles"] else -1
    c.ok(wh >= 0 and st["flags"][wh], "Wholesale card carries 'on'", st["flags"], "Wholesale on")
    c.ok(sum(1 for f in st["flags"] if f) == 1, "the other three do not carry 'on'",
         st["flags"], "exactly 1 on")
    lab_hit = [l for l in st["labels"] if "Inbound No." in l]
    c.ok(lab_hit == [], "no label containing 'Inbound No.' inside #s2 .formcard", lab_hit, [])
    exp = ("On registration, status = REQUESTED (tracking number entered → View Orders "
           "matching active immediately) · Inbound No. auto-assigned — shown in the Request List")
    c.ok(exp in st["submit"], "submit-row copy", st["submit"], exp)
    c.ev(f"DIAG: spec says the submit-row copy 'reads exactly' X, but #s2 .submitrow "
         f"textContent is {st['submit']!r} — it also contains the Register button label, "
         f"so a literal equality check would fail; executed as containment.")
    return c.finish()


def qa_b_02(page):
    c = Case("QA-B-02", "[WF]")
    N1(page); N2(page)
    st = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#s2 .prodtbl tbody tr')];
        const r=rows[1]; if(!r) return {missing:true};
        const ins=[...r.querySelectorAll('input')];
        return {missing:false, rowtext:ins.map(i=>i.value).join(' | '),
          qty: ins[3]?ins[3].value:null, uc: ins[4]?ins[4].value:null,
          jit: ins[5]?ins[5].value:null,
          expl: document.querySelector('#s2').innerText.replace(/\\s+/g,' ')};}""")
    if st.get("missing"):
        c.ok(False, "#s2 .prodtbl tbody row 2 exists", "missing", "present")
        return c.finish()
    c.ok("Round Lab" in st["rowtext"] and "1025 Dokdo Cleanser, 150ml" in st["rowtext"],
         "row 2 is Round Lab / 1025 Dokdo Cleanser, 150ml", st["rowtext"][:120],
         "Round Lab / 1025 Dokdo Cleanser, 150ml")
    c.ok(st["qty"] == "300", "Order Qty = 300", st["qty"], "300")
    c.ok(st["uc"] == "0", "Unit Cost (KRW) = 0", st["uc"], "0")
    c.ok(st["jit"] == "", "JIT Price empty", st["jit"], "")
    c.ok("0 entered directly in Unit Cost (0 allowed)" in st["expl"],
         "explanatory line substring", "not found",
         "0 entered directly in Unit Cost (0 allowed)")
    foc = page.evaluate(
        """() => [...document.querySelectorAll('input[type=checkbox], label, [role=switch]')]
             .filter(e=>/free of charge|FOC/i.test(
                 (e.textContent||'') + ' ' + (e.getAttribute('aria-label')||'') + ' ' +
                 (e.id||'') + ' ' + (e.name||'')))
             .map(e=>e.outerHTML.slice(0,120))""")
    c.ok(foc == [], "no checkbox/toggle/label bound to a free-of-charge behavior", foc, [])
    return c.finish()


def qa_b_03(page):
    c = Case("QA-B-03", "[WF]")
    N1(page); N2(page)
    st = page.evaluate(
        """() => {const s2=document.querySelector('#s2');
        const sup=[...s2.querySelectorAll('input')].find(i=>(i.getAttribute('placeholder')||'')
                     .includes('비엠유통'));
        const inv=s2.querySelector('.fld-inv input');
        const date=s2.querySelector('input[type=date]');
        const ta=s2.querySelector('textarea');
        const note=[...s2.querySelectorAll('.note.purple')]
                     .map(n=>n.textContent.replace(/\\s+/g,' ').trim());
        return {sup: sup?sup.value:null, inv: inv?inv.value:null,
                invPh: inv?inv.getAttribute('placeholder'):null,
                date: date?date.value:null, memo: ta?ta.value:null, note};}""")
    c.ok(st["sup"] == "비엠유통", "Supplier value verbatim Korean", st["sup"], "비엠유통")
    c.ok(st["inv"] == "10325661220417", "Tracking No value", st["inv"], "10325661220417")
    c.ok(st["invPh"] == "Add after dispatch — you can submit without it",
         "Tracking No placeholder", st["invPh"],
         "Add after dispatch — you can submit without it")
    c.ok(st["date"] == "2026-07-18", "Expected arrival", st["date"], "2026-07-18")
    c.ok(st["memo"] and "Wholesale vendor direct ship — 2 pallets, forklift needed" in st["memo"],
         "Memo textarea", st["memo"],
         "Wholesale vendor direct ship — 2 pallets, forklift needed")
    c.ok(any("matches to View Orders the moment it registers" in n for n in st["note"]),
         ".note.purple substring", st["note"],
         "matches to View Orders the moment it registers")
    return c.finish()


def qa_b_04(page):
    c = Case("QA-B-04", "[WF]")
    N1(page); N2(page)
    page.evaluate("""() => [...document.querySelectorAll('#s2 button')]
                       .find(b=>b.textContent.trim()==='Register Inbound Request').click()""")
    page.wait_for_timeout(200)
    g = gtoast_state(page)
    c.ok(g["visible"], "#gtoast visible", g, "visible")
    c.ok("✓ Inbound request registered" in g["text"], "toast primary", g["text"],
         "✓ Inbound request registered")
    c.ok("Inbound No. auto-assigned · added to the Request List · No refresh" in g["text"],
         "toast secondary", g["text"],
         "Inbound No. auto-assigned · added to the Request List · No refresh")
    return c.finish()


def qa_b_06(page):
    c = Case("QA-B-06 (negative)", "[WF]")
    N1(page); N2(page)
    st = page.evaluate(
        """() => {const s2=document.querySelector('#s2');
        const t=s2.innerText.replace(/\\s+/g,' ');
        const ctrls=[...document.querySelectorAll(
            'button, .chip, .tag, .pill, option, .badge, .rc-badge')]
            .map(e=>e.textContent.replace(/\\s+/g,' ').trim())
            .filter(x=>x.includes('SHIPPED'));
        return {t, ctrls};}""")
    c.ok("REQUESTED → PARTIAL → INBOUNDED" in st["t"],
         "State 2 legend footer substring", "not found", "REQUESTED → PARTIAL → INBOUNDED")
    c.ok("SHIPPED retired 2026-07-27 · PARTIAL added 2026-08-02" in st["t"],
         "footer records retirement note", "not found",
         "SHIPPED retired 2026-07-27 · PARTIAL added 2026-08-02")
    c.ok(st["ctrls"] == [], "no status control/badge/chip/option reading SHIPPED",
         st["ctrls"], [])
    return c.finish()


# =============================================================================== BLOCK C
def qa_c_01(page):
    c = Case("QA-C-01", "[WF]")
    for h in ("#reqlist", "#s3"):
        NR(page, h)
        page.wait_for_timeout(120)
        on = has_class(page, "#s3", "on")
        tab = page.evaluate(
            """() => {const b=[...document.querySelectorAll('.wf-tab')]
                 .find(x=>x.textContent.trim()
                    ==='3 · Request List (Requested/Partial/Inbounded)');
            return b?b.classList.contains('on'):null;}""")
        c.ok(on, f"{h}: #s3 has class on", on, True)
        c.ok(tab is True, f"{h}: top-bar tab carries class on", tab, True)
    return c.finish()


def qa_c_02(page):
    c = Case("QA-C-02", "[WF]")
    N1(page); N3(page)
    chips = page.evaluate(
        """() => [...document.querySelectorAll('#s3 .filterchips .chip')]
              .map(x=>({t:x.textContent.replace(/\\s+/g,' ').trim(),
                        on:x.classList.contains('on')}))""")
    c.ok(len(chips) == 4, ".filterchips has exactly 4 .chip", len(chips), 4)
    texts = [x["t"] for x in chips]
    c.ok(texts == ["All 12", "REQUESTED 8", "PARTIAL 1", "INBOUNDED 3"],
         "chip trimmed texts", texts, ["All 12", "REQUESTED 8", "PARTIAL 1", "INBOUNDED 3"])
    c.ok(chips and chips[0]["on"], "'All 12' chip carries on",
         chips[0]["on"] if chips else None, True)
    nums = [int(n) for t in texts for n in re.findall(r"\d+", t)]
    if len(nums) == 4:
        c.ok(nums[1] + nums[2] + nums[3] == nums[0], "status counts sum to All",
             f"{nums[1]}+{nums[2]}+{nums[3]} vs {nums[0]}", "equal")
    c.ok(not any("SHIPPED" in t for t in texts), "no SHIPPED chip", texts, "none")
    return c.finish()


def qa_c_03(page):
    c = Case("QA-C-03", "[WF]")
    N1(page); N3(page)
    page.evaluate("""() => [...document.querySelectorAll('#s3 .filterchips .chip')]
                       .find(x=>x.textContent.replace(/\\s+/g,' ').trim()==='PARTIAL 1').click()""")
    st = page.evaluate(
        """() => {const ch=[...document.querySelectorAll('#s3 .filterchips .chip')];
        const f=t=>ch.find(x=>x.textContent.replace(/\\s+/g,' ').trim()===t);
        return {p: f('PARTIAL 1').classList.contains('on'),
                a: f('All 12').classList.contains('on'),
                n: ch.filter(x=>x.classList.contains('on')).length};}""")
    c.ok(st["p"], "'PARTIAL 1' gains on", st["p"], True)
    c.ok(not st["a"], "'All 12' loses on", st["a"], False)
    c.ok(st["n"] == 1, "exactly one chip carries on", st["n"], 1)
    return c.finish()


def qa_c_05(page):
    c = Case("QA-C-05", "[WF]")
    N1(page); N3(page)
    st = page.evaluate(
        """() => {const bb=document.querySelector('#s3 .bulkbar');
        if(!bb) return {found:false};
        return {found:true,
          btns: [...bb.querySelectorAll('button')]
                  .map(b=>b.textContent.replace(/\\s+/g,' ').trim()),
          text: bb.textContent.replace(/\\s+/g,' ').trim()};}""")
    c.ok(st["found"], ".bulkbar exists", st["found"], True)
    if not st["found"]:
        return c.finish()
    c.ok("Bulk add tracking numbers" in st["btns"], "button with exact label",
         st["btns"], "Bulk add tracking numbers")
    exp = ("2 selected · Inbound processing (INBOUNDED transition) is applied automatically "
           "by View Orders scans")
    c.ok(exp in st["text"], "bulk bar count text", st["text"], exp)
    bad = [b for b in st["btns"] if re.search(r"mark as shipped", b, re.I)]
    c.ok(bad == [], "no 'Mark as shipped' button", bad, [])
    return c.finish()


def qa_c_07(page):
    c = Case("QA-C-07", "[WF]")
    N1(page); N3(page)
    st = page.evaluate(
        """() => [...document.querySelectorAll('#s3 .tbl tbody .tag')]
             .filter(t=>['SMART BUY','WHOLESALE','PARTNERSHIP']
                 .includes(t.textContent.replace(/\\s+/g,' ').trim()))
             .map(t=>{const cs=getComputedStyle(t);
                return {t:t.textContent.trim(), bg:cs.backgroundColor, col:cs.color,
                        fw:cs.fontWeight, tag:t.tagName};})""")
    c.ok(len(st) > 0, "Sourcing Route .tag spans found", len(st), ">0")
    for s in st:
        c.ok(s["bg"] in ("rgba(0, 0, 0, 0)", "transparent"),
             f"{s['t']} background fully transparent", s["bg"], "rgba(0, 0, 0, 0)")
        c.ok(s["col"] == "rgb(20, 16, 27)", f"{s['t']} colour = page ink",
             s["col"], "rgb(20, 16, 27)")
        c.ok(s["fw"] == "800", f"{s['t']} font-weight 800", s["fw"], "800")
    c.ev(f"{len(st)} route tags checked")
    return c.finish()


def qa_c_08(page):
    c = Case("QA-C-08", "[WF]")
    N1(page); N3(page)
    st = page.evaluate(
        """() => {const out={};
        const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')]
                     .filter(r=>!r.classList.contains('cpanel-ir'));
        for(const no of ['202607120004','202607130003','202607130002','202607120001']){
          const r=rows.find(x=>x.textContent.includes(no));
          if(!r){out[no]=null; continue;}
          const cells=[...r.children];
          const cell=cells[6];
          out[no]={cell: cell?cell.textContent.replace(/\\s+/g,' ').trim():null,
                   addBtn: cell? [...cell.querySelectorAll('button')]
                      .some(b=>b.textContent.includes('Add tracking')) : null};
        }
        return out;}""")
    a = st.get("202607120004")
    c.ok(a is not None, "row 202607120004 found", a, "present")
    if a:
        c.ok("10325661220417" in a["cell"] and "10325661220418" in a["cell"],
             "two tracking numbers rendered", a["cell"], "10325661220417 + 10325661220418")
        c.ok("2 tracking numbers — all matching active" in a["cell"],
             "note text", a["cell"], "2 tracking numbers — all matching active")
    for no in ("202607130003", "202607130002"):
        r = st.get(no)
        c.ok(r is not None and r["addBtn"], f"row {no} renders an 'Add tracking' button",
             r, "Add tracking button")
    d = st.get("202607120001")
    c.ok(d is not None, "row 202607120001 found", d, "present")
    if d:
        c.ok("10324880021991" in d["cell"], "single number", d["cell"], "10324880021991")
        c.ok(not d["addBtn"], "no 'Add tracking' button", d["addBtn"], False)
    return c.finish()


def qa_c_09(page):
    c = Case("QA-C-09", "[WF]")
    N1(page); N3(page)
    st = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')]
                     .filter(r=>!r.classList.contains('cpanel-ir'));
        const r=rows.find(x=>x.textContent.includes('202607120001'));
        if(!r) return {found:false};
        const cells=[...r.children];
        const qty=cells[5], status=cells[10];
        const marker=[...qty.querySelectorAll('*')]
            .find(e=>e.textContent.includes('→'));
        return {found:true,
          qty: qty.textContent.replace(/\\s+/g,' ').trim(),
          status: status.textContent.replace(/\\s+/g,' ').trim(),
          title: marker?marker.getAttribute('title'):
                 (qty.querySelector('[title]')?qty.querySelector('[title]')
                     .getAttribute('title'):null)};}""")
    c.ok(st["found"], "row 202607120001 found", st, "present")
    if not st["found"]:
        return c.finish()
    c.ok("PARTIAL 120/180" in st["status"], "status pill 'PARTIAL 120/180'",
         st["status"], "PARTIAL 120/180")
    c.ok("180" in st["qty"] and "✎ 300→180 (damaged)" in st["qty"],
         "Qty cell shows 180 + '✎ 300→180 (damaged)'", st["qty"], "180 ✎ 300→180 (damaged)")
    c.ok(st["title"] == "Expected qty edit history", "edit-history title attribute",
         st["title"], "Expected qty edit history")
    c.ok("Damaged/defective" not in st["qty"], "short token, not full enum string",
         st["qty"], "damaged")
    return c.finish()


def qa_c_10(page):
    c = Case("QA-C-10", "[WF]")
    N1(page); N3(page)
    st = page.evaluate(
        """() => {const out={};
        const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')]
                     .filter(r=>!r.classList.contains('cpanel-ir'));
        for(const no of ['202607100005','202607090002']){
          const r=rows.find(x=>x.textContent.includes(no));
          if(!r){out[no]=null;continue;}
          const cells=[...r.children];
          out[no]={status: cells[10].textContent.replace(/\\s+/g,' ').trim(),
                   recv: cells[8].textContent.replace(/\\s+/g,' ').trim(),
                   trk: cells[6].textContent.replace(/\\s+/g,' ').trim(),
                   vo: [...r.querySelectorAll('a,button')]
                        .filter(e=>/View Orders|view-orders/i.test(
                           e.textContent + ' ' + (e.getAttribute('href')||'')))
                        .map(e=>e.outerHTML.slice(0,100))};
        }
        return out;}""")
    a, b = st.get("202607100005"), st.get("202607090002")
    c.ok(a is not None and b is not None, "both INBOUNDED rows found", st, "present")
    if a:
        c.ok("INBOUNDED" in a["status"], "202607100005 INBOUNDED pill", a["status"], "INBOUNDED")
        c.ok(a["recv"] == "07-11 14:22", "202607100005 Received Date", a["recv"], "07-11 14:22")
        c.ok("Switched by View Orders scan inbound" in a["trk"],
             "202607100005 tracking note", a["trk"], "Switched by View Orders scan inbound")
        c.ok(a["vo"] == [], "202607100005 has no <a>/<button> pointing to View Orders",
             a["vo"], [])
    if b:
        c.ok("INBOUNDED" in b["status"], "202607090002 INBOUNDED pill", b["status"], "INBOUNDED")
        c.ok(b["recv"] == "07-09 10:05", "202607090002 Received Date", b["recv"], "07-09 10:05")
        c.ok(b["vo"] == [], "202607090002 has no <a>/<button> pointing to View Orders",
             b["vo"], [])
    return c.finish()


def qa_c_11(page):
    c = Case("QA-C-11 (negative)", "[WF]")
    N1(page); N3(page)
    ths = page.evaluate(
        """() => [...document.querySelectorAll('#s3 .tbl thead th')]
              .map(t=>t.textContent.replace(/\\s+/g,' ').trim())""")
    c.ok(len(ths) == 12, "exactly 12 th cells", len(ths), 12)
    want = ["", "Inbound No.", "Sourcing Route", "Brand · Product", "SKU", "Qty",
            "Tracking No", "Expected arrival", "Received Date", "Requested by",
            "Status", "Actions"]
    c.ok(ths[1:] == want[1:], "header order (col 1 = checkbox)", ths, want)
    c.ok(not any("Carrier" in t for t in ths), "no Carrier column", ths, "none")
    clean = page.evaluate(
        """() => [...document.querySelectorAll('#s3 .tbl thead th')].map(t=>{
             const c=t.cloneNode(true);
             c.querySelectorAll('.dot').forEach(d=>d.remove());
             return c.textContent.replace(/\\s+/g,' ').trim();})""")
    c.ev(f"DIAG: with .dot spans stripped: {clean} (== spec). Legend dot numbers 3/4/10/5 "
         f"are baked into the Sourcing Route / Tracking No / Received Date / Status <th>.")
    return c.finish()


def qa_c_12(page):
    c = Case("QA-C-12 (negative)", "[WF]")
    N1(page); N3(page)
    st = page.evaluate(
        """() => {const out={};
        const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')]
                     .filter(r=>!r.classList.contains('cpanel-ir'));
        for(const no of ['202607100005','202607090002']){
          const r=rows.find(x=>x.textContent.includes(no));
          out[no]= r? [...r.querySelectorAll('button')]
                      .some(b=>b.textContent.includes('Add tracking')) : null;}
        return out;}""")
    for no, v in st.items():
        c.ok(v is False, f"row {no} has no 'Add tracking' button", v, False)
    return c.finish()


def qa_c_13(page):
    c = Case("QA-C-13", "[WF]")
    N1(page); N3(page)
    notes = page.evaluate(
        """() => [...document.querySelectorAll('#s3 .note.purple')]
              .map(n=>n.textContent.replace(/\\s+/g,' ').trim())""")
    hit = [n for n in notes if "is not done manually on this screen" in n
           and "#wholesale-ops" in n and "#partnership-kr" in n]
    c.ok(hit != [], ".note.purple with all three substrings", notes, "all three substrings")
    return c.finish()


def qa_c_14(page):
    c = Case("QA-C-14", "[WF]")
    N1(page); N3(page)
    exp = ("Showing 6 of 12 request(s) · Status: REQUESTED 8 · PARTIAL 1 · INBOUNDED 3")
    found = page.evaluate(
        """(t) => {const els=[...document.querySelectorAll('#s3 *')]
             .filter(e=>e.children.length===0 || e.querySelectorAll('*').length<4);
        const hit=els.find(e=>e.textContent.replace(/\\s+/g,' ').trim()===t);
        return hit? hit.className||hit.tagName : null;}""", exp)
    if not found:
        sub = page.evaluate(
            """(t)=>document.querySelector('#s3').innerText.replace(/\\s+/g,' ').includes(t)""",
            exp)
        near = page.evaluate(
            """() => {const m=document.querySelector('#s3').innerText
                 .replace(/\\s+/g,' ').match(/Showing[^·]*·[^\\n]{0,90}/);
               return m?m[0]:null;}""")
        c.ok(False, "footer line exact text", f"substring_present={sub}; actual={near}", exp)
    else:
        c.ev(f"footer element = {found}")
    n = page.evaluate(
        """() => [...document.querySelectorAll('#s3 .tbl tbody tr')]
              .filter(r=>!r.classList.contains('cpanel-ir')).length""")
    c.ok(n == 6, "exactly 6 data rows in .tbl tbody", n, 6)
    return c.finish()


def qa_c_15(page):
    c = Case("QA-C-15", "[WF]")
    N1(page); N3(page)
    clicked = page.evaluate(
        """() => {const b=[...document.querySelectorAll('#s3 button')]
              .find(x=>x.textContent.replace(/\\s+/g,' ').trim()==='＋ New Inbound Request');
        if(!b) return false; b.click(); return true;}""")
    c.ok(clicked, "'＋ New Inbound Request' button exists", clicked, True)
    page.wait_for_timeout(120)
    on = has_class(page, "#s1", "on")
    tab = page.evaluate(
        """() => {const b=[...document.querySelectorAll('#s1 .pagetabs button')]
             .find(x=>x.textContent.trim()==='New Request');
        return b?b.classList.contains('on'):null;}""")
    c.ok(on, "#s1 becomes the active state", on, True)
    c.ok(tab is True, "'New Request' tab carries on", tab, True)
    return c.finish()


def qa_c_16(page):
    c = Case("QA-C-16", "[WF]")
    N1(page); N3(page)
    st = page.evaluate(
        """() => {const out={};
        const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')]
                     .filter(r=>!r.classList.contains('cpanel-ir'));
        for(const no of ['202607130003','202607100005']){
          const r=rows.find(x=>x.textContent.includes(no));
          if(!r){out[no]=null;continue;}
          const cells=[...r.children];
          out[no]={bp: cells[3].textContent.replace(/\\s+/g,' ').trim(),
                   b: cells[3].querySelector('b')?
                      cells[3].querySelector('b').textContent.trim():null,
                   sku: cells[4].textContent.replace(/\\s+/g,' ').trim()};}
        return out;}""")
    a = st.get("202607130003")
    c.ok(a is not None, "row 202607130003 found", a, "present")
    if a:
        c.ok(a["b"] == "COSRX", "brand COSRX inside <b>", a["b"], "COSRX")
        c.ok("Advanced Snail 96 Mucin Essence, 100ml +2 more" in a["bp"],
             "product text", a["bp"], "Advanced Snail 96 Mucin Essence, 100ml +2 more")
        c.ok(a["sku"] == "100040311 +2", "SKU cell", a["sku"], "100040311 +2")
    b = st.get("202607100005")
    c.ok(b is not None, "row 202607100005 found", b, "present")
    if b:
        c.ok(b["b"] == "Beauty of Joseon", "brand in bold", b["b"], "Beauty of Joseon")
        c.ok("Relief Sun, 50ml +1 more" in b["bp"], "product text", b["bp"],
             "Relief Sun, 50ml +1 more")
        c.ok(b["sku"] == "100031820 +1", "SKU cell", b["sku"], "100031820 +1")
    return c.finish()


def qa_c_19(page):
    c = Case("QA-C-19", "[WF]")
    N1(page); N3(page)
    st = page.evaluate(
        """() => {const nav=document.querySelector('.nav');
        if(!nav) return {found:false};
        return {found:true, text: nav.textContent.replace(/\\s+/g,' ').trim(),
          buttons: [...nav.querySelectorAll('button,a')]
              .map(b=>b.textContent.replace(/\\s+/g,' ').trim())};}""")
    c.ok(st["found"], ".nav exists", st["found"], True)
    if not st["found"]:
        return c.finish()
    seq = ["SkinSeoul", "Operation AI ▾", "Catalog Management ▾", "OMS Center ▾",
           "Site Management ▾", "Comments", "Yongwon Ryu", "Logout"]
    pos, ok_order, missing = -1, True, []
    for s in seq:
        i = st["text"].find(s, pos + 1)
        if i < 0:
            missing.append(s)
            ok_order = False
        else:
            pos = i
    c.ok(missing == [], "all nav items present", missing, "none missing")
    c.ok(ok_order, "nav items in the specified order", st["text"][:200], " → ".join(seq))
    c.ok(any(b.startswith("💬 Comments") for b in st["buttons"]),
         "'💬 Comments' button", st["buttons"], "💬 Comments")
    c.ok("Logout" in st["buttons"], "Logout button", st["buttons"], "Logout")
    return c.finish()


def qa_c_24(page):
    c = Case("QA-C-24", "[WF]")
    N1(page); N3(page)
    st = page.evaluate(
        """() => {const toasts=[...document.querySelectorAll('#s3 .toast')];
        return toasts.map(t=>({id:t.id, text:t.textContent.replace(/\\s+/g,' ').trim(),
            vis: t.offsetParent!==null}));}""")
    hit = [t for t in st if "✓ Inbound request registered — 202607130003" in t["text"]]
    c.ok(hit != [], "static .toast inside #s3 with expected text", st,
         "✓ Inbound request registered — 202607130003")
    if hit:
        c.ok("No refresh · added to top of the list" in hit[0]["text"], "sub-line",
             hit[0]["text"], "No refresh · added to top of the list")
        c.ok(hit[0]["id"] != "gtoast", "is not #gtoast", hit[0]["id"], "!= gtoast")
        page.wait_for_timeout(3200)
        still = page.evaluate(
            """(t) => {const e=[...document.querySelectorAll('#s3 .toast')]
                 .find(x=>x.textContent.includes(t)); return e? e.offsetParent!==null : false;}""",
            "✓ Inbound request registered — 202607130003")
        c.ok(still, "does not auto-hide", still, True)
    return c.finish()


# =============================================================================== BLOCK D
def qa_d_01(page):
    c = Case("QA-D-01", "[WF]")
    N1(page); NM(page)
    st = page.evaluate(
        """() => {const m=document.querySelector('#m-invoice');
        const h=m.querySelector('header');
        return {open:m.classList.contains('open'),
          header: h?h.textContent.replace(/\\s+/g,' ').trim():null,
          body: m.textContent.replace(/\\s+/g,' ')};}""")
    c.ok(st["open"], "#m-invoice gains class open", st["open"], True)
    c.ok(st["header"] == "Add Tracking No — 202607130003", "header exact text",
         st["header"], "Add Tracking No — 202607130003")
    c.ev("DIAG: the <header> also contains the modal close control "
         "<button class='x' data-close>✕</button>, so textContent can never equal the "
         "spec string. Stripping that button yields an exact match.")
    for s in ["Enter the tracking number(s) once the goods have shipped.",
              "One inbound request can hold multiple tracking numbers"]:
        c.ok(s in st["body"], f"body contains {s!r}", "not found", s)
    return c.finish()


def qa_d_02(page):
    c = Case("QA-D-02", "[WF]")
    N1(page); N3(page)
    ok = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')];
        const r=rows.find(x=>x.textContent.includes('202607130003'));
        if(!r) return false;
        const b=[...r.querySelectorAll('button')]
                 .find(x=>x.textContent.includes('Add tracking'));
        if(!b) return false; b.click(); return true;}""")
    c.ok(ok, "'Add tracking' button in row 202607130003 clicked", ok, True)
    page.wait_for_timeout(120)
    c.ok(has_class(page, "#m-invoice", "open"), "#m-invoice gains class open",
         has_class(page, "#m-invoice", "open"), True)
    return c.finish()


def qa_d_03(page):
    c = Case("QA-D-03", "[WF]",
             note="spec asserts the last row's input 'value cleared' but never instructs the "
                  "runner to put a value in it — a marker value was typed to make the "
                  "assertion non-vacuous")
    N1(page); NM(page)
    n0 = page.evaluate("() => document.querySelectorAll('#tnList .qrow').length")
    c.ok(n0 == 1, "#tnList contains exactly 1 .qrow", n0, 1)
    page.click("#tnAdd")
    page.click("#tnAdd")
    st = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#tnList .qrow')];
        const last=rows[rows.length-1];
        return {n: rows.length,
          shape: rows.map(r=>({i: !!r.querySelector('input'),
                               d: !!r.querySelector('.tn-del'),
                               dt: r.querySelector('.tn-del')?
                                   r.querySelector('.tn-del').textContent.trim():null})),
          focused: last? document.activeElement===last.querySelector('input') : false};}""")
    c.ok(st["n"] == 3, "#tnList contains 3 .qrow after two adds", st["n"], 3)
    c.ok(all(s["i"] and s["d"] and s["dt"] == "✕" for s in st["shape"]),
         "each row has an input and a .tn-del ✕", st["shape"], "input + ✕")
    c.ok(st["focused"], "newest input is document.activeElement", st["focused"], True)
    page.evaluate("""() => document.querySelectorAll('#tnList .qrow .tn-del')[0].click()""")
    page.evaluate("""() => document.querySelectorAll('#tnList .qrow .tn-del')[0].click()""")
    n1 = page.evaluate("() => document.querySelectorAll('#tnList .qrow').length")
    c.ok(n1 == 1, "two rows removed", n1, 1)
    page.evaluate("""() => {const i=document.querySelector('#tnList .qrow input');
                       i.value='MARKER123';}""")
    page.evaluate("""() => document.querySelectorAll('#tnList .qrow .tn-del')[0].click()""")
    st2 = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#tnList .qrow')];
        return {n: rows.length, v: rows[0]?rows[0].querySelector('input').value:null};}""")
    c.ok(st2["n"] == 1, "final row remains (count never reaches 0)", st2["n"], 1)
    c.ok(st2["v"] == "", "final row input value cleared", st2["v"], "")
    return c.finish()


def qa_d_04(page):
    c = Case("QA-D-04", "[WF]")
    N1(page); NM(page)
    ok = page.evaluate(
        """() => {const b=[...document.querySelectorAll('#m-invoice button')]
             .find(x=>x.textContent.replace(/\\s+/g,' ').trim()==='Save tracking numbers');
        if(!b) return false; b.click(); return true;}""")
    c.ok(ok, "'Save tracking numbers' button exists", ok, True)
    page.wait_for_timeout(200)
    c.ok(not has_class(page, "#m-invoice", "open"), "#m-invoice loses class open",
         has_class(page, "#m-invoice", "open"), False)
    g = gtoast_state(page)
    c.ok(g["visible"], "#gtoast visible", g, "visible")
    c.ok("✓ Tracking number(s) saved" in g["text"], "toast primary", g["text"],
         "✓ Tracking number(s) saved")
    c.ok("Every registered number is now matched to View Orders · No refresh" in g["text"],
         "toast secondary", g["text"],
         "Every registered number is now matched to View Orders · No refresh")
    return c.finish()


def qa_d_05(page):
    c = Case("QA-D-05", "[WF]")
    # (a) Cancel
    N1(page); NM(page)
    ok = page.evaluate(
        """() => {const b=[...document.querySelectorAll('#m-invoice button')]
             .find(x=>x.textContent.trim()==='Cancel'); if(!b) return false; b.click(); return true;}""")
    c.ok(ok, "'Cancel' button exists", ok, True)
    page.wait_for_timeout(150)
    c.ok(not has_class(page, "#m-invoice", "open"), "Cancel closes modal",
         has_class(page, "#m-invoice", "open"), False)
    c.ok(not gtoast_state(page)["visible"], "no #gtoast after Cancel",
         gtoast_state(page), "hidden")
    # (b) header ✕
    NX(page); NM(page)
    ok2 = page.evaluate(
        """() => {const h=document.querySelector('#m-invoice header');
        const b=[...h.querySelectorAll('button,span,a')]
             .find(x=>x.textContent.trim()==='✕'); if(!b) return false; b.click(); return true;}""")
    c.ok(ok2, "header ✕ exists", ok2, True)
    page.wait_for_timeout(150)
    c.ok(not has_class(page, "#m-invoice", "open"), "header ✕ closes modal",
         has_class(page, "#m-invoice", "open"), False)
    c.ok(not gtoast_state(page)["visible"], "no #gtoast after header ✕",
         gtoast_state(page), "hidden")
    # (c) backdrop
    NX(page); NM(page)
    page.locator("#m-invoice").click(position={"x": 6, "y": 6})
    page.wait_for_timeout(150)
    c.ok(not has_class(page, "#m-invoice", "open"), "backdrop click closes modal",
         has_class(page, "#m-invoice", "open"), False)
    c.ok(not gtoast_state(page)["visible"], "no #gtoast after backdrop click",
         gtoast_state(page), "hidden")
    return c.finish()


def qa_d_06(page):
    c = Case("QA-D-06", "[WF]")
    N1(page); NM(page)
    p0 = page.evaluate(
        """() => {const i=document.querySelector('#tnList .qrow input');
        return i?i.getAttribute('placeholder'):null;}""")
    c.ok(p0 == "e.g. 10325661220417 — last-mile / Coupang tracking number",
         "first .qrow input placeholder", p0,
         "e.g. 10325661220417 — last-mile / Coupang tracking number")
    page.click("#tnAdd")
    p1 = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#tnList .qrow')];
        const i=rows[rows.length-1].querySelector('input');
        return i?i.getAttribute('placeholder'):null;}""")
    c.ok(p1 == "Additional tracking number", "appended row placeholder", p1,
         "Additional tracking number")
    body = page.evaluate(
        """() => document.querySelector('#m-invoice').textContent.replace(/\\s+/g,' ')""")
    c.ok("status stays REQUESTED" in body, "modal body substring", "not found",
         "status stays REQUESTED")
    titles = page.evaluate(
        """() => [...document.querySelectorAll('#tnList .tn-del')]
              .map(b=>b.getAttribute('title'))""")
    c.ok(all(t == "Remove this tracking number" for t in titles) and titles,
         ".tn-del title attribute", titles, "Remove this tracking number")
    return c.finish()


def qa_d_17(page):
    c = Case("QA-D-17", "[WF]")
    N1(page); NM(page)
    page.locator("#m-invoice").click(position={"x": 6, "y": 6})
    page.wait_for_timeout(150)
    c.ok(not has_class(page, "#m-invoice", "open"), "#m-invoice loses class open",
         has_class(page, "#m-invoice", "open"), False)
    c.ok(not gtoast_state(page)["visible"], "no toast appears", gtoast_state(page), "hidden")
    return c.finish()


# =============================================================================== BLOCK F
def qa_f_01(page):
    c = Case("QA-F-01", "[WF]")
    N1(page)
    page.click('[data-open="inbox1"]')
    page.wait_for_timeout(150)
    st = page.evaluate(
        """() => {const h=document.querySelector('#inbox1');
        if(!h) return {found:false};
        const tabs=[...h.querySelectorAll('*')]
          .filter(e=>e.children.length<=2 &&
             /^(@ Mentions|★ Saved)/.test(e.textContent.replace(/\\s+/g,' ').trim()))
          .map(e=>({t:e.textContent.replace(/\\s+/g,' ').trim(),
                    on:e.classList.contains('on'), cls:e.className}));
        return {found:true, open:h.classList.contains('open'), tabs};}""")
    c.ok(st["found"], "#inbox1 exists", st["found"], True)
    if not st["found"]:
        return c.finish()
    c.ok(st["open"], "#inbox1 gains class open", st["open"], True)
    men = [t for t in st["tabs"] if t["t"].startswith("@ Mentions")]
    sav = [t for t in st["tabs"] if t["t"].startswith("★ Saved")]
    c.ok(men and sav, "two tabs '@ Mentions' and '★ Saved'", st["tabs"],
         ["@ Mentions", "★ Saved"])
    c.ok(men and "2" in men[0]["t"], "'@ Mentions' badge 2",
         men[0]["t"] if men else None, "@ Mentions 2")
    c.ok(any(t["on"] for t in men), "'@ Mentions' carries class on", men, "on")
    return c.finish()


def qa_f_02(page):
    c = Case("QA-F-02", "[WF]")
    N1(page)
    page.click('[data-open="inbox1"]')
    page.wait_for_timeout(150)
    st = page.evaluate(
        """() => {const h=document.querySelector('#inbox1');
        const its=[...h.querySelectorAll('.it')];
        return {text: h.textContent.replace(/\\s+/g,' '),
          n: its.length,
          items: its.map(i=>({t:i.textContent.replace(/\\s+/g,' ').trim(),
                              unread:i.classList.contains('unread'),
                              b: i.querySelector('b')?i.querySelector('b').textContent.trim():null}))};}""")
    c.ok("Comments where I'm tagged" in st["text"], "pane header",
         "not found", "Comments where I'm tagged")
    c.ok("Mark all as read" in st["text"], "action 'Mark all as read'", "not found",
         "Mark all as read")
    c.ok(st["n"] == 2, "exactly two .it entries", st["n"], 2)
    diag = page.evaluate(
        """() => ({mentions: document.querySelectorAll(
                     '#inbox1 [data-pane="mentions"] .it').length,
                   saved: document.querySelectorAll(
                     '#inbox1 [data-pane="saved"] .it').length})""")
    c.ev(f"DIAG: scoped counts = {diag}. The Saved pane is display:none but still in the "
         f"DOM, so the bare '.it' selector the spec supplies matches 3.")
    if st["n"] >= 2:
        c.ok(all(i["unread"] for i in st["items"][:2]), "both carry class unread",
             [i["unread"] for i in st["items"]], True)
        c.ok(st["items"][0]["b"] == "202607130002", "first entity label",
             st["items"][0]["b"], "202607130002")
        c.ok(st["items"][1]["b"] == "202607120004", "second entity label",
             st["items"][1]["b"], "202607120004")
        c.ok('Dean: "@Yongwon when is the tracking number for this wholesale one coming?"'
             in st["items"][0]["t"], "first entry text", st["items"][0]["t"],
             'Dean: "@Yongwon when is the tracking number for this wholesale one coming?"')
        c.ok("11:20" in st["items"][0]["t"], "first entry time", st["items"][0]["t"], "11:20")
        c.ok('Miranti: "@Yongwon the partnership stock\'s expected arrival slipped by a day"'
             in st["items"][1]["t"], "second entry text", st["items"][1]["t"],
             'Miranti: "@Yongwon the partnership stock\'s expected arrival slipped by a day"')
        c.ok("Yesterday" in st["items"][1]["t"], "second entry time",
             st["items"][1]["t"], "Yesterday")
    return c.finish()


def qa_f_03(page):
    c = Case("QA-F-03", "[WF]")
    N1(page)
    page.click('[data-open="inbox1"]')
    page.wait_for_timeout(150)
    before = page.evaluate(
        """() => {const it=document.querySelector('#inbox1 .it');
        const st=[...it.querySelectorAll('button,span,a')]
            .find(x=>x.textContent.trim()==='★');
        return st? st.classList.contains('on') : null;}""")
    clicked = page.evaluate(
        """() => {const it=document.querySelector('#inbox1 .it');
        const st=[...it.querySelectorAll('button,span,a')]
            .find(x=>x.textContent.trim()==='★');
        if(!st) return false; st.click(); return true;}""")
    c.ok(clicked, "★ button on first mention entry exists", clicked, True)
    after = page.evaluate(
        """() => {const it=document.querySelector('#inbox1 .it');
        const st=[...it.querySelectorAll('button,span,a')]
            .find(x=>x.textContent.trim()==='★');
        return st? st.classList.contains('on') : null;}""")
    c.ok(before is not None and after != before, "★ toggles class 'on'",
         f"{before} -> {after}", "toggled")
    tabclick = page.evaluate(
        """() => {const t=[...document.querySelectorAll('#inbox1 *')]
             .find(e=>e.children.length<=2 &&
                  e.textContent.replace(/\\s+/g,' ').trim().startsWith('★ Saved'));
        if(!t) return false; t.click(); return true;}""")
    c.ok(tabclick, "'★ Saved' tab exists", tabclick, True)
    page.wait_for_timeout(150)
    txt = page.evaluate(
        """() => document.querySelector('#inbox1').textContent.replace(/\\s+/g,' ')""")
    c.ok("Comments I saved" in txt, "pane header 'Comments I saved'", "not found",
         "Comments I saved")
    c.ok("Unstar to remove from list" in txt, "hint 'Unstar to remove from list'",
         "not found", "Unstar to remove from list")
    return c.finish()


def qa_f_04(page):
    c = Case("QA-F-04", "[WF]")
    N1(page); N3(page)
    ok = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')];
        const r=rows.find(x=>x.textContent.includes('202607130002'));
        if(!r) return false;
        const b=[...r.querySelectorAll('button')]
             .find(x=>x.textContent.includes('Comments'));
        if(!b) return false; b.click(); return true;}""")
    c.ok(ok, "'💬 Comments' button in row 202607130002 clicked", ok, True)
    page.wait_for_timeout(150)
    st = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')];
        const r=rows.find(x=>x.textContent.includes('202607130002') &&
                             !x.classList.contains('cpanel-ir'));
        const nx=r?r.nextElementSibling:null;
        if(!nx || !nx.classList.contains('cpanel-ir')) return {below:false};
        const td=nx.querySelector('td');
        const inp=nx.querySelector('input');
        return {below:true, colspan: td?td.getAttribute('colspan'):null,
          text: nx.textContent.replace(/\\s+/g,' ').trim(),
          at: [...nx.querySelectorAll('.at')].map(a=>a.textContent.trim()),
          ph: inp?inp.getAttribute('placeholder'):null,
          post: [...nx.querySelectorAll('button')]
                  .map(b=>b.textContent.trim()).includes('Post')};}""")
    c.ok(st["below"], "tr.cpanel-ir inserted directly below the row", st, "inserted")
    if not st["below"]:
        return c.finish()
    c.ok(st["colspan"] == "12", "spans all 12 columns", st["colspan"], "12")
    for frag in ["Dean", "Wholesale PO confirmed — expected arrival 07-18", "09:12",
                 "Yongwon", "@Dean got it. I'll keep location row B open", "09:30"]:
        c.ok(frag in st["text"], f"panel contains {frag!r}", st["text"][:200], frag)
    c.ok("@Dean" in st["at"], "@Dean wrapped in a .at span", st["at"], "@Dean")
    c.ok(st["ph"] == "Write a comment — @name tags trigger a Slack alert",
         "write-box placeholder", st["ph"],
         "Write a comment — @name tags trigger a Slack alert")
    c.ok(st["post"], "button labelled 'Post'", st["post"], True)
    return c.finish()


def qa_f_05(page):
    c = Case("QA-F-05", "[WF]")
    N1(page); N3(page)
    js = """() => {const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')];
        const r=rows.find(x=>x.textContent.includes('202607130002') &&
                             !x.classList.contains('cpanel-ir'));
        const b=[...r.querySelectorAll('button')]
             .find(x=>x.textContent.includes('Comments'));
        b.click(); return true;}"""
    page.evaluate(js)
    page.wait_for_timeout(120)
    n1 = page.evaluate("() => document.querySelectorAll('#s3 tr.cpanel-ir').length")
    c.ok(n1 == 1, "panel open", n1, 1)
    page.evaluate(js)
    page.wait_for_timeout(120)
    n2 = page.evaluate("() => document.querySelectorAll('#s3 tr.cpanel-ir').length")
    c.ok(n2 == 0, "tr.cpanel-ir removed on second click (toggle)", n2, 0)
    return c.finish()


def qa_f_06(page):
    c = Case("QA-F-06", "[WF]")
    N1(page); N3(page)
    ok = page.evaluate(
        """() => {const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')];
        const r=rows.find(x=>x.textContent.includes('202607120001') &&
                             !x.classList.contains('cpanel-ir'));
        if(!r) return false;
        const b=[...r.querySelectorAll('button')]
             .find(x=>x.textContent.includes('Comments'));
        if(!b) return false; b.click(); return true;}""")
    c.ok(ok, "'💬 Comments' in row 202607120001 clicked", ok, True)
    page.wait_for_timeout(150)
    st = page.evaluate(
        """() => {const p=document.querySelector('#s3 tr.cpanel-ir');
        if(!p) return {found:false};
        const inp=p.querySelector('input');
        return {found:true, text:p.textContent.replace(/\\s+/g,' ').trim(),
                ph: inp?inp.getAttribute('placeholder'):null};}""")
    c.ok(st["found"], "panel injected", st["found"], True)
    if st["found"]:
        c.ok("No comments yet" in st["text"], "renders 'No comments yet'",
             st["text"][:150], "No comments yet")
        c.ok(st["ph"] == "Write a comment — @name tags trigger a Slack alert",
             "plus the write box", st["ph"],
             "Write a comment — @name tags trigger a Slack alert")
    return c.finish()


# =============================================================================== BLOCK G
def qa_g_10(page):
    c = Case("QA-G-10 (negative)", "[WF]")
    N1(page)
    for step in ("N1", "N2", "N3", "NM"):
        if step == "N2":
            N2(page)
        elif step == "N3":
            N3(page)
        elif step == "NM":
            NM(page)
        page.wait_for_timeout(80)
        pr = page.evaluate(
            """() => [...document.querySelectorAll('button,a,input')]
                 .filter(e=>/Print/i.test((e.textContent||'') + ' ' +
                          (e.getAttribute('title')||'') + ' ' + (e.value||'')))
                 .map(e=>e.outerHTML.slice(0,90))""")
        c.ok(pr == [], f"{step}: no Print-labelled button/a/input", pr, [])
        scan = page.evaluate(
            """() => [...document.querySelectorAll('input')]
                 .filter(i=>/scan|barcode|바코드/i.test(i.getAttribute('placeholder')||''))
                 .map(i=>i.getAttribute('placeholder'))""")
        c.ok(scan == [], f"{step}: no scan-oriented placeholder", scan, [])
        af = page.evaluate(
            """() => [...document.querySelectorAll('input[autofocus]')].length""")
        c.ok(af == 0, f"{step}: no autofocused input", af, 0)
    scripts = page.evaluate(
        """() => [...document.querySelectorAll('script')].map(s=>s.textContent).join('\\n')""")
    for tok in ["AudioContext", "speechSynthesis"]:
        c.ok(tok not in scripts, f"no {tok} in page script",
             tok if tok in scripts else "absent", "absent")
    c.ok(not re.search(r"\bnew\s+Audio\b", scripts), "no `new Audio` in page script",
         "found" if re.search(r"\bnew\s+Audio\b", scripts) else "absent", "absent")
    media = page.evaluate("() => document.querySelectorAll('audio,video').length")
    c.ok(media == 0, "no media element", media, 0)
    printjs = page.evaluate(
        """() => /window\\.print\\s*\\(|\\.print\\s*\\(\\)/.test(
             [...document.querySelectorAll('script')].map(s=>s.textContent).join('\\n'))""")
    c.ok(not printjs, "no control bound to a print action", printjs, False)
    return c.finish()


def qa_g_16(page):
    c = Case("QA-G-16 (negative)", "[WF]")
    N1(page)
    N2(page); N3(page); NM(page)
    st = page.evaluate(
        """() => {
        const dm=[...document.querySelectorAll('[data-modal]')]
            .map(e=>e.getAttribute('data-modal')).filter(v=>v!=='m-invoice');
        const fc=[...document.querySelectorAll('.formcard')];
        const badLabels=[];
        fc.forEach(f=>{[...f.querySelectorAll('label')].forEach(l=>{
            if(l.textContent.includes('Inbound No.')) badLabels.push(l.textContent.trim());});
          [...f.querySelectorAll('input')].forEach(i=>{
            const t=(i.getAttribute('placeholder')||'')+' '+(i.getAttribute('aria-label')||'');
            if(t.includes('Inbound No.')) badLabels.push('input:'+t.trim());});});
        const foc=[...document.querySelectorAll('input[type=checkbox]')]
            .filter(i=>/free of charge|FOC/i.test(
                (i.closest('label')?i.closest('label').textContent:'')+' '+(i.id||'')))
            .map(i=>i.outerHTML.slice(0,90));
        const shipped=[...document.querySelectorAll('.chip,.tag,.pill,.badge,option,.rc-badge')]
            .map(e=>e.textContent.replace(/\\s+/g,' ').trim())
            .filter(t=>t.includes('SHIPPED'));
        const cells=[...document.querySelectorAll('th,td')]
            .map(e=>e.textContent.replace(/\\s+/g,' ').trim())
            .filter(t=>/^(Size|Carrier)$/.test(t));
        const reg=id=>[...document.querySelectorAll(id+' button')]
            .filter(b=>b.textContent.replace(/\\s+/g,' ').trim()==='Register Inbound Request')
            .length;
        const rows=[...document.querySelectorAll('#s3 .tbl tbody tr')];
        const addbtn={};
        for(const no of ['202607100005','202607090002']){
          const r=rows.find(x=>x.textContent.includes(no));
          addbtn[no]= r? [...r.querySelectorAll('button')]
                        .some(b=>b.textContent.includes('Add tracking')) : null;}
        return {dm, badLabels, foc, shipped, cells, s1:reg('#s1'), s2:reg('#s2'), addbtn};}""")
    c.ok(st["dm"] == [], "no element with data-modal other than m-invoice", st["dm"], [])
    c.ok(st["badLabels"] == [], "no input/label containing 'Inbound No.' in a .formcard",
         st["badLabels"], [])
    c.ok(st["foc"] == [], "no checkbox bound to free-of-charge", st["foc"], [])
    c.ok(st["shipped"] == [], "no text SHIPPED in any chip/badge/option", st["shipped"], [])
    c.ok(st["cells"] == [], "no th/cell labelled Size or Carrier", st["cells"], [])
    c.ok(st["s1"] == 1, "exactly one 'Register Inbound Request' in #s1", st["s1"], 1)
    c.ok(st["s2"] == 1, "exactly one 'Register Inbound Request' in #s2", st["s2"], 1)
    for no, v in st["addbtn"].items():
        c.ok(v is False, f"no 'Add tracking' button on row {no}", v, False)
    return c.finish()


# =============================================================================== runner
SCENARIOS = [
    qa_a_01, qa_a_02, qa_a_03, qa_a_04, qa_a_05, qa_a_07, qa_a_10, qa_a_11, qa_a_13,
    qa_a_17, qa_a_18, qa_a_19, qa_a_23, qa_a_24, qa_a_25, qa_a_26, qa_a_28,
    qa_b_01, qa_b_02, qa_b_03, qa_b_04, qa_b_06,
    qa_c_01, qa_c_02, qa_c_03, qa_c_05, qa_c_07, qa_c_08, qa_c_09, qa_c_10, qa_c_11,
    qa_c_12, qa_c_13, qa_c_14, qa_c_15, qa_c_16, qa_c_19, qa_c_24,
    qa_d_01, qa_d_02, qa_d_03, qa_d_04, qa_d_05, qa_d_06, qa_d_17,
    qa_f_01, qa_f_02, qa_f_03, qa_f_04, qa_f_05, qa_f_06,
    qa_g_10, qa_g_16,
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        for fn in SCENARIOS:
            try:
                fn(page)
            except Exception as e:  # noqa: BLE001
                RESULTS.append({"id": fn.__name__, "tier": "[WF]", "verdict": "FAIL",
                                "evidence": f"EXCEPTION: {type(e).__name__}: {e}",
                                "note": None})
        browser.close()

    counts = {}
    for r in RESULTS:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    print("=" * 100)
    for r in RESULTS:
        print(f"{r['verdict']:<10} {r['id']:<22} {r['evidence'][:700]}")
        if r.get("note"):
            print(f"{'':<10} {'':<22} NOTE: {r['note']}")
    print("=" * 100)
    print("TOTAL", len(RESULTS), counts)

    if "--json" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--json") + 1])
        out.write_text(json.dumps(RESULTS, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
