#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pre-handoff [WF] QA runner — order-detail (WMS 2.0)
Spec: specs/order-detail.md (v1.2 body, v1.3 §8.1 delta, 2026-08-03) — §8 [WF] scenarios only.
Target: wms2/order-detail/index.html loaded via file:// (== review-baseline-20260803).

§8.0 contract implemented here:
  - state scoping (#st-normal / #st-hold / #m-del) on every selector
  - rule 1: strip .dot descendants before text comparison
  - rule 2: <br> -> space, collapse whitespace, trim
  - rule 3: "reads exactly"/"text is exactly"/"value is" = strict equality;
            "reads"/"contains"/"begins with" = substring/prefix
  - rule 4: element-scoped assertions (first text node, named child controls)
  - fresh page load per scenario (§8.0 preconditions; §8.3 reload guidance)

QA-MAP-6 is executed as a document lint on the spec file (per its own note),
not as a browser action.

Output: JSON summary on stdout. Never mutates the wireframe or the spec.
"""
import json
import re
import sys
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


WMS2 = Path(__file__).resolve().parents[3]          # .../wms2
PAGE_URL = (WMS2 / "order-detail" / "index.html").as_uri()
SPEC = WMS2 / "specs" / "order-detail.md"

HELPERS = r"""
() => {
  window.qaText = (el) => {
    if (!el) return null;
    const c = el.cloneNode(true);
    c.querySelectorAll('.dot').forEach(d => d.remove());
    c.querySelectorAll('br').forEach(b => b.replaceWith(document.createTextNode(' ')));
    return (c.textContent || '').replace(/\s+/g, ' ').trim();
  };
  window.qaAll = (sel, root) =>
    [...(root || document).querySelectorAll(sel)].map(e => window.qaText(e));
}
"""

BANNER = ("⏸ On Hold by urgent CS request — inbound still allowed, "
          "but Outbound disabled. Release the hold (Change Status) to ship")
CMT_PLACEHOLDER = ("Write a comment — @name to notify via Slack "
                   "(order no. · text · time · author included). "
                   "Per-order history accumulates here.")
LIINFO = ("Edit a line via the Edit button. Use checkboxes to select items for bulk "
          "Inbound. * = WooCommerce original before variation-pack recalculation · "
          "🤖 = auto-filled by Agent · Scroll right to see the Inventory fields.")
HUB_SEARCH_PLACEHOLDER = "🔍 Search all comments — order no. · author · text"


class Fail(Exception):
    def __init__(self, expected, actual):
        super().__init__(f"expected={expected!r} actual={actual!r}")
        self.expected = str(expected)
        self.actual = str(actual)


def chk(cond, expected, actual):
    if not cond:
        raise Fail(expected, actual)


def eq(value, expected, label):
    if value != expected:
        raise Fail(f"{label} is exactly {expected!r}", repr(value))


# ---------------------------------------------------------------- page helpers

def fresh(page):
    page.goto(PAGE_URL)
    page.evaluate(HELPERS)


def T(page, sel):
    return page.evaluate("sel => qaText(document.querySelector(sel))", sel)


def TA(page, sel):
    return page.evaluate("sel => qaAll(sel)", sel)


def N(page, sel):
    return page.evaluate("sel => document.querySelectorAll(sel).length", sel)


def go_hold(page):
    page.click('.wf-tab[data-ostate="st-hold"]')


# ---------------------------------------------------------------- QA-MAP

def qa_map_1(page):
    fresh(page)
    n = TA(page, "#st-normal .dot")
    chk(len(n) == 13 and sorted(n, key=lambda s: int(s)) == [str(i) for i in range(1, 14)],
        "#st-normal .dot = 13 elements, texts exactly 1–13 (no 14)", n)
    h = TA(page, "#st-hold .dot")
    chk(len(h) == 14 and sorted(h, key=lambda s: int(s)) == [str(i) for i in range(1, 15)],
        "#st-hold .dot = 14 elements, texts exactly 1–14", h)
    m = TA(page, "#m-del .dot")
    eq(m, ["M3"], "#m-del .dot texts")
    eq(N(page, ".dot"), 28, ".dot (unscoped) count")
    eq(N(page, ".legend ol li"), 14, ".legend ol li count")
    order = TA(page, ".legend ol li .n")
    eq(order, ["1", "2", "3", "4", "5", "6", "12", "10", "11", "14", "13", "9", "7", "8"],
       ".legend .n DOM order")


def qa_map_2(page):
    fresh(page)
    eq(T(page, ".wf-bar h1"), "WMS 2.0 · Order Detail Wireframe", ".wf-bar h1")
    eq(T(page, ".wf-bar .hint"),
       "v1 — Based on the live admin (Order #407847) · Purple numbers = new/changed annotations",
       ".wf-bar .hint")
    tabs = TA(page, ".wf-tabs .wf-tab")
    eq(tabs, ["Modal: Delete Line", "1 · Processing (default)", "2 · On Hold"],
       "wf-tab buttons in DOM order")
    eq(T(page, ".wf-tabs .wf-toggle"), "Hide annotations", "toggle label")
    chk(page.evaluate(
        "() => document.querySelector('.wf-tab[data-ostate=\"st-normal\"]').classList.contains('on')"),
        "`1 · Processing (default)` carries class on", "class on missing")


def qa_map_3(page):
    fresh(page)
    st = page.evaluate("() => [document.querySelector('#st-normal').classList.contains('on'),"
                       " document.querySelector('#st-hold').classList.contains('on')]")
    eq(st, [True, False], "on load: #st-normal on / #st-hold not")
    page.evaluate("() => window.scrollTo(0, 600)")
    chk(page.evaluate("() => window.scrollY") > 0, "scrollY > 0 before the tab click", "still 0")
    go_hold(page)
    after = page.evaluate("""() => [
        document.querySelector('#st-hold').classList.contains('on'),
        document.querySelector('#st-normal').classList.contains('on'),
        document.querySelector('.wf-tab[data-ostate="st-hold"]').classList.contains('on'),
        document.querySelector('.wf-tab[data-ostate="st-normal"]').classList.contains('on'),
        window.scrollY]""")
    eq(after, [True, False, True, False, 0],
       "after tab 2: st-hold on, st-normal off, tab2 on, tab1 off, scrollY 0")
    page.click('.wf-tab[data-ostate="st-normal"]')
    back = page.evaluate("() => [document.querySelector('#st-normal').classList.contains('on'),"
                         " document.querySelector('#st-hold').classList.contains('on')]")
    eq(back, [True, False], "classes swap back")


def qa_map_4(page):
    fresh(page)
    page.click("#annoToggle")
    eq(T(page, "#annoToggle"), "Show annotations", "toggle text after click")
    chk(page.evaluate("() => document.body.classList.contains('no-anno')"),
        "body gains class no-anno", "missing")
    hidden = page.evaluate("""() =>
        [...document.querySelectorAll('.dot')].every(d => getComputedStyle(d).display === 'none')
        && getComputedStyle(document.querySelector('.legend')).display === 'none'""")
    chk(hidden, "no .dot and no .legend visible", "still visible")
    page.click("#annoToggle")
    eq(T(page, "#annoToggle"), "Hide annotations", "toggle text after second click")
    visible = page.evaluate("""() =>
        [...document.querySelectorAll('.dot')].every(d => getComputedStyle(d).display !== 'none')
        && getComputedStyle(document.querySelector('.legend')).display !== 'none'""")
    chk(visible, "dots and legend visible again", "still hidden")


def qa_map_5(page):
    fresh(page)
    eq(T(page, ".legend h3"), "Order Detail — Changes (specs 0 · A · C applied)", ".legend h3")
    items = page.evaluate("""() => {
        const out = {};
        [...document.querySelectorAll('.legend ol li')].forEach(li => {
            out[li.querySelector('.n').textContent.trim()] = qaText(li);
        });
        return out;
    }""")
    for needle in ['"Outbound to Deleo BaroShip"', "Outbound",
                   "Enabled only when every item is INBOUNDED"]:
        chk(needle in items["9"], f"legend item 9 contains {needle!r}", items["9"][:200])
    chk("combined case of Hold + incomplete inbound (3/4)" in items["14"],
        "legend item 14 contains the combined-case string", items["14"][:200])
    chk("Latest Inventory Count kept" in items["10"],
        "legend item 10 contains 'Latest Inventory Count kept'", items["10"][:200])


def qa_map_6(page):
    # Document lint per the scenario's own note — not a browser action.
    text = SPEC.read_text(encoding="utf-8")
    sec23 = text.split("### 2.3")[1].split("### 2.4")[0]
    for n in range(1, 15):
        chk(re.search(rf"^\|\s*{n}\s*\|.*\[L-{n}\]", sec23, re.M),
            f"§2.3 table row mapping dot {n} to [L-{n}]", "row missing")
        chk(f"### `[L-{n}]`" in text, f"§3 heading `[L-{n}]` exists", "heading missing")
    chk(re.search(r"^\|\s*M3\s*\|.*\[L-M3\]", sec23, re.M),
        "§2.3 table row mapping M3 to [L-M3]", "row missing")
    chk("### `[L-M3]`" in text, "§3 heading `[L-M3]` exists", "heading missing")


# ---------------------------------------------------------------- QA-CMT

def qa_cmt_1(page):
    fresh(page)
    ph = page.get_attribute("#st-normal .cmt-new textarea", "placeholder")
    eq(ph, CMT_PLACEHOLDER, "composer placeholder")
    eq(T(page, "#st-normal #addCmt"), "Add Comment", "#addCmt label")
    hdr = page.evaluate("""() => {
        const h = [...document.querySelectorAll('#st-normal .sec > h3')]
            .find(x => qaText(x).includes('Operator Comments'));
        const b = h && h.querySelector('button');
        return b ? qaText(b) : null;
    }""")
    eq(hdr, "Hide Comments", "Operator Comments header button")


def qa_cmt_2(page):
    fresh(page)
    rows = page.evaluate("""() => [...document.querySelectorAll('#st-normal .cmt-list .c-item')]
        .map(r => ({who: qaText(r.querySelector('.who')),
                    at: qaAll('span.at', r),
                    text: qaText(r),
                    time: qaText(r.querySelector('time')),
                    star_on: r.querySelector('.star').classList.contains('on')}))""")
    chk(len(rows) == 2, "#st-normal .cmt-list .c-item returns exactly 2 rows", len(rows))
    r1, r2 = rows
    eq(r1["who"], "Dean", "row 1 .who")
    eq(r1["at"], ["@Yongwon"], "row 1 span.at")
    chk("Please pack this order with extra care — repeat-purchase VIP customer." in r1["text"],
        "row 1 body text", r1["text"])
    eq(r1["time"], "07-13 10:42", "row 1 <time>")
    chk(not r1["star_on"], "row 1 .star does NOT carry class on", "on present")
    eq(r2["who"], "Yongwon", "row 2 .who")
    eq(r2["at"], ["@Dean"], "row 2 span.at")
    eq(r2["time"], "07-13 10:55", "row 2 <time>")
    chk(r2["star_on"], "row 2 .star carries class on", "on missing")


def qa_cmt_3(page):
    fresh(page)
    page.fill("#st-normal .cmt-new textarea", "Checked the sachet count")
    page.click("#st-normal #addCmt")
    n = N(page, "#st-normal .cmt-list .c-item")
    chk(n == 3, "3 rows after posting", n)
    last = page.evaluate("""() => {
        const r = [...document.querySelectorAll('#st-normal .cmt-list .c-item')].pop();
        return {who: qaText(r.querySelector('.who')), text: qaText(r),
                time: qaText(r.querySelector('time'))};
    }""")
    eq(last["who"], "Yongwon", "last row .who")
    chk("Checked the sachet count" in last["text"], "last row body", last["text"])
    eq(last["time"], "Just now", "last row <time>")
    eq(page.input_value("#st-normal .cmt-new textarea"), "", "composer cleared")
    ok = page.evaluate("""() =>
        document.querySelector('#st-normal').classList.contains('on')
        && document.querySelector('.wf-tab[data-ostate="st-normal"]').classList.contains('on')""")
    chk(ok, "no navigation/reload (state 1 and tab 1 still on)", "state changed")
    nh = N(page, "#st-hold .cmt-list .c-item")
    chk(nh == 2, "#st-hold thread still 2 rows (append is state-local)", nh)


def qa_cmt_4(page):
    fresh(page)
    page.click("#st-normal #addCmt")
    n = N(page, "#st-normal .cmt-list .c-item")
    chk(n == 2, "empty comment is a no-op (2 rows)", n)
    page.fill("#st-normal .cmt-new textarea", "   ")
    page.click("#st-normal #addCmt")
    n = N(page, "#st-normal .cmt-list .c-item")
    chk(n == 2, "whitespace-only comment is a no-op (2 rows)", n)


def qa_cmt_5(page):
    fresh(page)
    page.fill("#st-normal .cmt-new textarea", "@Dean please double-bag this")
    page.click("#st-normal #addCmt")
    res = page.evaluate("""() => {
        const r = [...document.querySelectorAll('#st-normal .cmt-list .c-item')].pop();
        return {ats: qaAll('span.at', r), text: qaText(r)};
    }""")
    eq(res["ats"], ["@Dean"], "new comment span.at")
    chk("please double-bag this" in res["text"], "remaining text present", res["text"])
    chk(all("please" not in a for a in res["ats"]),
        "remaining text NOT inside span.at", res["ats"])


def qa_cmt_6(page):
    fresh(page)
    sel = "#st-normal .cmt-list .c-item:nth-child(1) .star"
    chk(not page.evaluate(f"() => document.querySelector('{sel}').classList.contains('on')"),
        "star initially without class on", "on present")
    page.click(sel)
    chk(page.evaluate(f"() => document.querySelector('{sel}').classList.contains('on')"),
        "star gains class on after click", "on missing")
    page.click(sel)
    chk(not page.evaluate(f"() => document.querySelector('{sel}').classList.contains('on')"),
        "class on removed after second click", "on still present")


def qa_cmt_7(page):
    fresh(page)
    go_hold(page)
    ph = page.get_attribute("#st-hold .cmt-new textarea", "placeholder")
    eq(ph, CMT_PLACEHOLDER, "State 2 composer placeholder")
    eq(T(page, "#st-hold #addCmtH"), "Add Comment", "#addCmtH label")
    rows = page.evaluate("""() => [...document.querySelectorAll('#st-hold .cmt-list .c-item')]
        .map(r => [qaText(r.querySelector('.who')), qaText(r.querySelector('time'))])""")
    eq(rows, [["Dean", "07-13 10:42"], ["Yongwon", "07-13 10:55"]],
       "State 2 thread: 2 rows, same authors and times")


# ---------------------------------------------------------------- QA-HUB

def open_hub(page):
    page.click('#st-normal .icon-btn[data-open="inbox1"]')


def qa_hub_1(page):
    fresh(page)
    open_hub(page)
    chk(page.evaluate("() => document.querySelector('#inbox1').classList.contains('open')"),
        "#inbox1 gains class open", "not open")
    eq(page.get_attribute("#inbox1 .csearch input", "placeholder"),
       HUB_SEARCH_PLACEHOLDER, "hub search placeholder")
    tabs = TA(page, "#inbox1 .tabs button")
    chk(len(tabs) == 2 and tabs[0].startswith("@ Mentions") and tabs[1].startswith("★ Saved"),
        "2 tab buttons beginning with '@ Mentions' and '★ Saved'", tabs)
    chk(page.evaluate(
        "() => document.querySelector('#inbox1 .tabs button[data-tab=\"mentions\"]')"
        ".classList.contains('on')"),
        "@ Mentions tab carries class on", "on missing")
    hdr = T(page, '#inbox1 [data-pane="mentions"] .paneheader')
    chk("Comments mentioning me · Click to open the order" in hdr
        and "Mark all read" in hdr,
        "mentions paneheader reads the header and contains Mark all read", hdr)


def qa_hub_2(page):
    fresh(page)
    open_hub(page)
    eq(T(page, '#st-normal .icon-btn[data-open="inbox1"] .badge-n'), "2", "nav badge")
    eq(T(page, '#inbox1 .tabs button[data-tab="mentions"] .badge-n'), "2", "tab badge")
    n = N(page, '#inbox1 [data-pane="mentions"] .it.unread')
    chk(n == 2, "exactly 2 unread items", n)
    third = page.evaluate("""() => {
        const it = document.querySelectorAll('#inbox1 [data-pane="mentions"] .it')[2];
        return {text: qaText(it), unread: it.classList.contains('unread')};
    }""")
    chk("Order 407790" in third["text"] and "Resolved" in third["text"]
        and "Yesterday" in third["text"], "third item is Order 407790 · Kai: Resolved · Yesterday",
        third["text"])
    chk(not third["unread"], "third item does NOT carry class unread", "unread present")


def qa_hub_3(page):
    fresh(page)
    open_hub(page)
    page.click('#inbox1 .tabs button[data-tab="saved"]')
    vis = page.evaluate("""() => ({
        saved: getComputedStyle(document.querySelector('#inbox1 [data-pane="saved"]')).display,
        mentions: getComputedStyle(document.querySelector('#inbox1 [data-pane="mentions"]')).display})""")
    chk(vis["saved"] != "none", '[data-pane="saved"] is visible', vis)
    chk(vis["mentions"] == "none", '[data-pane="mentions"] is hidden', vis)
    hdr = T(page, '#inbox1 [data-pane="saved"] .paneheader')
    chk("Saved comments · Click to open the order" in hdr
        and "Unstar to remove from the list" in hdr, "saved paneheader copy", hdr)
    items = page.evaluate("""() => [...document.querySelectorAll('#inbox1 [data-pane="saved"] .it')]
        .map(it => ({text: qaText(it), star_on: it.querySelector('.star').classList.contains('on')}))""")
    chk(len(items) == 1, "exactly 1 saved item", len(items))
    chk("Order 407812" in items[0]["text"]
        and 'Miranti: "@Yongwon 1 JIT item not yet inbounded"' in items[0]["text"],
        "saved item is Order 407812 · Miranti", items[0]["text"])
    chk(items[0]["star_on"], "saved item's star carries class on", "on missing")


def qa_hub_4(page):
    fresh(page)
    open_hub(page)
    page.fill("#inbox1 .csearch input", "miranti")
    st = page.evaluate("""() => ({
        tabs: getComputedStyle(document.querySelector('#inbox1 .tabs')).display,
        csr: getComputedStyle(document.querySelector('#inbox1 [data-pane="csr"]')).display,
        hdr: qaText(document.querySelector('#inbox1 [data-pane="csr"] .paneheader')),
        items: qaAll('#inbox1 [data-pane="csr"] .it'),
        marks: qaAll('#inbox1 [data-pane="csr"] mark')})""")
    chk(st["tabs"] == "none", "#inbox1 .tabs has display:none", st["tabs"])
    chk(st["csr"] != "none", "csr pane visible", st["csr"])
    eq(st["hdr"], "1 results · newest first · click to open the order", "results header")
    chk(len(st["items"]) == 1 and "Order 407812" in st["items"][0], "one item, Order 407812",
        st["items"])
    chk("Miranti" in st["marks"], "text Miranti wrapped in <mark>", st["marks"])
    page.fill("#inbox1 .csearch input", "zzzz")
    nores = page.evaluate("""() => ({
        empty: qaText(document.querySelector('#inbox1 [data-pane="csr"] .empty')),
        items: document.querySelectorAll('#inbox1 [data-pane="csr"] .it').length})""")
    eq(nores["empty"], "No matching comments", "no-match copy")
    eq(nores["items"], 0, "zero .it elements")
    page.fill("#inbox1 .csearch input", "")
    restored = page.evaluate("""() => ({
        tabs: getComputedStyle(document.querySelector('#inbox1 .tabs')).display,
        on: document.querySelector('#inbox1 .tabs button[data-tab="mentions"]').classList.contains('on'),
        pane: getComputedStyle(document.querySelector('#inbox1 [data-pane="mentions"]')).display})""")
    chk(restored["tabs"] != "none" and restored["on"] and restored["pane"] != "none",
        "tabs visible again, @ Mentions on, its pane visible", restored)


def qa_hub_5(page):
    fresh(page)
    open_hub(page)
    seeded = page.evaluate("""() =>
        qaText(document.querySelector('#inbox1 [data-pane="mentions"]'))
        + ' ' + qaText(document.querySelector('#inbox1 [data-pane="saved"]'))""")
    chk("407301" not in seeded, "407301 appears in neither Mentions nor Saved tab", seeded)
    page.fill("#inbox1 .csearch input", "407301")
    st = page.evaluate("""() => ({
        hdr: qaText(document.querySelector('#inbox1 [data-pane="csr"] .paneheader')),
        items: qaAll('#inbox1 [data-pane="csr"] .it')})""")
    eq(st["hdr"], "1 results · newest first · click to open the order", "results header")
    chk(len(st["items"]) == 1 and "Order 407301" in st["items"][0]
        and 'Dean: "Repacked and shipped"' in st["items"][0],
        "item is Order 407301 · Dean: Repacked and shipped", st["items"])


def qa_hub_6(page):
    fresh(page)
    open_hub(page)
    page.fill("#inbox1 .csearch input", "sachet")
    st = page.evaluate("""() => ({
        hdr: qaText(document.querySelector('#inbox1 [data-pane="csr"] .paneheader')),
        items: qaAll('#inbox1 [data-pane="csr"] .it'),
        marks: qaAll('#inbox1 [data-pane="csr"] mark')})""")
    eq(st["hdr"], "1 results · newest first · click to open the order", "sachet header")
    chk(len(st["items"]) == 1 and "Order 407688" in st["items"][0]
        and 'Aldo: "Customer note checked — sachet included"' in st["items"][0],
        "single item Order 407688 · Aldo", st["items"])
    chk("sachet" in st["marks"], "sachet inside <mark>", st["marks"])
    page.fill("#inbox1 .csearch input", "dean")
    st2 = page.evaluate("""() => ({
        hdr: qaText(document.querySelector('#inbox1 [data-pane="csr"] .paneheader')),
        items: qaAll('#inbox1 [data-pane="csr"] .it')})""")
    eq(st2["hdr"], "2 results · newest first · click to open the order", "dean header")
    chk(len(st2["items"]) == 2 and "Order 407847" in st2["items"][0]
        and "Order 407301" in st2["items"][1],
        "items in order: 407847 first, 407301 second", st2["items"])


def qa_hub_7(page):
    fresh(page)
    open_hub(page)
    page.fill("#inbox1 .csearch input", "<")
    st = page.evaluate("""() => {
        const pane = document.querySelector('#inbox1 [data-pane="csr"]');
        return {empty: qaText(pane.querySelector('.empty')),
                its: pane.querySelectorAll('.it').length,
                marks: pane.querySelectorAll('mark').length,
                tags: [...pane.querySelectorAll('*')].map(e => e.tagName)};
    }""")
    eq(st["empty"], "No matching comments", "no-match copy for '<'")
    eq(st["its"], 0, "zero .it elements")
    chk(st["marks"] == 0 and set(st["tags"]) <= {"DIV"},
        "no raw < injected as markup — pane contains no unexpected element", st["tags"])


def qa_hub_8(page):
    fresh(page)
    go_hold(page)
    page.click('#st-hold .icon-btn[data-open="inbox1H"]')
    st = page.evaluate("""() => ({
        open: document.querySelector('#inbox1H').classList.contains('open'),
        ph: document.querySelector('#inbox1H .csearch input').getAttribute('placeholder'),
        tabs: qaAll('#inbox1H .tabs button'),
        badge: qaText(document.querySelector('#st-hold .icon-btn[data-open="inbox1H"] .badge-n')),
        items: qaAll('#inbox1H [data-pane="mentions"] .it')})""")
    chk(st["open"], "#inbox1H opens", "not open")
    eq(st["ph"], HUB_SEARCH_PLACEHOLDER, "State 2 hub placeholder")
    chk(len(st["tabs"]) == 2 and st["tabs"][0].startswith("@ Mentions")
        and st["tabs"][1].startswith("★ Saved"), "same two tabs", st["tabs"])
    eq(st["badge"], "2", "State 2 .badge-n")
    chk(len(st["items"]) == 3
        and "Order 407847" in st["items"][0]
        and "Order 407812" in st["items"][1]
        and "Order 407790" in st["items"][2], "same three mention items", st["items"])


# ---------------------------------------------------------------- QA-INB

def line_rows(page, state):
    return page.evaluate("""(state) =>
        [...document.querySelectorAll(state + ' .litable tbody tr')].map(tr => ({
            cls: tr.className,
            sku: qaText(tr.querySelector('td:nth-child(2)')),
            tags: [...tr.querySelectorAll('.tag')].map(t => ({cls: t.className, text: qaText(t)})),
            act_buttons: [...tr.querySelectorAll('td:last-child button')]
                         .map(b => ({cls: b.className, text: qaText(b)})),
            tds: qaAll('td', tr)}))""", state)


def qa_inb_1(page):
    fresh(page)
    rows = line_rows(page, "#st-normal")
    chk(len(rows) == 4, "#st-normal .litable tbody tr returns exactly 4 rows", len(rows))
    for i, r in enumerate(rows):
        inb = [t for t in r["tags"] if "tag-inbounded" in t["cls"]]
        chk(inb and inb[0]["text"] == "INBOUNDED",
            f"row {i+1} shows .tag.tag-inbounded reading exactly INBOUNDED", r["tags"])
    for i in (1, 2, 3):
        ci = [b for b in rows[i]["act_buttons"] if b["text"] == "Cancel Inbound"]
        chk(ci and "btn-red-line" in ci[0]["cls"],
            f"row {i+1} Actions contains `Cancel Inbound` with class btn-red-line",
            rows[i]["act_buttons"])
    chk("row-edit" in rows[0]["cls"], "row 1 carries class row-edit", rows[0]["cls"])
    chk(rows[0]["sku"].startswith("100005104"), "row 1 SKU 100005104", rows[0]["sku"])
    chk(all(b["text"] != "Cancel Inbound" for b in rows[0]["act_buttons"]),
        "row 1 contains NO Cancel Inbound button", rows[0]["act_buttons"])


def qa_inb_2(page):
    fresh(page)
    go_hold(page)
    rows = line_rows(page, "#st-hold")
    by_sku = {r["sku"].split(" ")[0]: r for r in rows}
    r = by_sku["100043697"]
    pend = [t for t in r["tags"] if "tag-pending" in t["cls"]]
    chk(pend and pend[0]["text"] == "PENDING",
        "SKU 100043697 shows .tag.tag-pending reading exactly PENDING", r["tags"])
    inb_btn = [b for b in r["act_buttons"] if b["text"] == "Inbound"]
    chk(inb_btn and "btn-green" in inb_btn[0]["cls"],
        "its Actions cell contains `Inbound` with class btn-green", r["act_buttons"])
    chk(all(b["text"] != "Cancel Inbound" for b in r["act_buttons"]),
        "and NO button labelled Cancel Inbound", r["act_buttons"])
    for sku in ("100005088", "100012534"):
        rr = by_sku[sku]
        chk(any("tag-inbounded" in t["cls"] and t["text"] == "INBOUNDED" for t in rr["tags"])
            and any(b["text"] == "Cancel Inbound" for b in rr["act_buttons"]),
            f"SKU {sku} still INBOUNDED with Cancel Inbound", rr["tags"] + rr["act_buttons"])


def qa_inb_3(page):
    fresh(page)
    for state in ("#st-normal", "#st-hold"):
        txt = T(page, state)
        chk("Request Inbound" not in txt,
            f"'Request Inbound' appears nowhere inside {state}", "string found")
        headers = TA(page, f"{state} .litable th")
        chk(all(h != "Inbound Request" for h in headers),
            f"no {state} .litable header cell reads 'Inbound Request'", headers)


def qa_inb_4(page):
    fresh(page)
    for state in ("#st-normal", "#st-hold"):
        foot = page.evaluate("""(state) => {
            const f = document.querySelector(state + ' .li-foot');
            const tq = f.querySelector('.tq');
            const btns = [...f.querySelectorAll('button')].map(b => qaText(b));
            const tq_first = !!(tq.compareDocumentPosition(f.querySelector('button'))
                                & Node.DOCUMENT_POSITION_FOLLOWING);
            return {tq: qaText(tq), btns, tq_first};
        }""", state)
        chk("Total Quantity: 4" in foot["tq"], f"{state} footer contains 'Total Quantity: 4'",
            foot["tq"])
        eq(foot["btns"], ["Bulk Inbound Selected Items", "📦 Outbound", "+ Add Line Item"],
           f"{state} footer buttons left to right")
        chk(foot["tq_first"], f"{state} Total Quantity precedes the buttons", "order wrong")


def qa_inb_5(page):
    fresh(page)
    n1 = N(page, '#st-normal .litable thead input[type=checkbox][title="Select all"]')
    chk(n1 == 1, "exactly 1 select-all checkbox in the header", n1)
    n2 = N(page, "#st-normal .litable tbody tr td:first-child input[type=checkbox]")
    chk(n2 == 4, "exactly 4 per-row checkboxes", n2)


# ---------------------------------------------------------------- QA-OUT

def qa_out_1(page):
    fresh(page)
    st = page.evaluate("""() => {
        const b = document.querySelector('#st-normal #obBtn');
        return {text: qaText(b), cls: b.className, disabled: b.hasAttribute('disabled')};
    }""")
    eq(st["text"], "📦 Outbound", "#obBtn visible label")
    chk("btn-green" in st["cls"], "#obBtn carries class btn-green", st["cls"])
    chk(not st["disabled"], "#obBtn does NOT carry the disabled attribute", "disabled present")


def qa_out_2(page):
    fresh(page)
    go_hold(page)
    st = page.evaluate("""() => {
        const b = document.querySelector('#st-hold .li-foot button.btn-gray');
        return {text: qaText(b), disabled: b.hasAttribute('disabled'),
                style: b.getAttribute('style') || '',
                copacity: getComputedStyle(b).opacity, ccursor: getComputedStyle(b).cursor,
                id: b.getAttribute('id')};
    }""")
    eq(st["text"], "📦 Outbound", "hold footer button label")
    chk(st["disabled"], "carries the disabled attribute", "missing")
    chk("opacity:.55" in st["style"].replace(" ", "") and st["copacity"] == "0.55",
        "inline opacity:.55", st["style"])
    chk("cursor:not-allowed" in st["style"].replace(" ", "") and st["ccursor"] == "not-allowed",
        "inline cursor:not-allowed", st["style"])
    chk(st["id"] is None, "carries NO id", st["id"])
    ban = page.evaluate("""() => {
        const b = document.querySelector('#holdBannerH');
        return {vis: getComputedStyle(b).display !== 'none', text: qaText(b)};
    }""")
    chk(ban["vis"], "#holdBannerH is visible", "hidden")
    eq(ban["text"], BANNER, "#holdBannerH copy")
    rows = line_rows(page, "#st-hold")
    r = [x for x in rows if x["sku"].startswith("100043697")][0]
    chk(any("tag-pending" in t["cls"] and t["text"] == "PENDING" for t in r["tags"])
        and any(b["text"] == "Inbound" and "btn-green" in b["cls"] for b in r["act_buttons"]),
        "SKU 100043697 shows PENDING with a green Inbound button (both gates block)",
        r["tags"] + r["act_buttons"])


def qa_out_3(page):
    fresh(page)
    labels = page.evaluate("""() =>
        [...document.querySelectorAll('#st-normal button, #st-hold button')].map(b => qaText(b))""")
    chk(all(l != "Outbound to Deleo BaroShip" for l in labels),
        "no button label reads 'Outbound to Deleo BaroShip'", "label found")
    for state in ("#st-normal", "#st-hold"):
        txt = T(page, state)
        chk("Outbound to Deleo BaroShip" not in txt,
            f"the string appears in no body text inside {state}", "string found")
    eq(T(page, "#st-normal #obBtn"), "📦 Outbound", "State 1 footer label")
    eq(T(page, "#st-hold .li-foot button.btn-gray"), "📦 Outbound", "State 2 footer label")


# ---------------------------------------------------------------- QA-STA

def qa_sta_1(page):
    fresh(page)
    page.click('#st-normal button[data-open="statusdd"]')
    st = page.evaluate("""() => {
        const dd = document.querySelector('#statusdd');
        return {vis: getComputedStyle(dd).display !== 'none',
                items: qaAll(':scope > div', dd),
                on: qaText(dd.querySelector('div.on'))};
    }""")
    chk(st["vis"], "#statusdd becomes visible", "hidden")
    eq(st["items"], ["pending", "processing", "on-hold", "completed",
                     "refunded", "failed", "shipped", "prepare-shipment"],
       "8 statuses in this exact order")
    eq(st["on"], "processing", "the processing item carries class on")


def qa_sta_2(page):
    fresh(page)
    items = page.evaluate("() => qaAll(':scope > div', document.querySelector('#statusdd'))")
    chk(all("cancel" not in i.lower() for i in items),
        "#statusdd contains no item reading cancelled/cancel", items)
    btn = page.evaluate("""() => {
        const b = [...document.querySelectorAll('#st-normal .subbar button')]
            .find(x => qaText(x) === '✕ Cancel Order');
        return b ? b.className : null;
    }""")
    chk(btn is not None and "link-btn" in btn and "red" in btn,
        "separate subbar button `✕ Cancel Order` with class link-btn red", btn)


def qa_sta_3(page):
    fresh(page)
    go_hold(page)
    page.click('#st-hold button[data-open="statusddH"]')
    st = page.evaluate("""() => {
        const dd = document.querySelector('#statusddH');
        const items = [...dd.querySelectorAll(':scope > div')];
        return {vis: getComputedStyle(dd).display !== 'none',
                on_hold_on: items.some(d => qaText(d) === 'on-hold' && d.classList.contains('on')),
                processing_on: items.some(d => qaText(d) === 'processing' && d.classList.contains('on'))};
    }""")
    chk(st["vis"], "#statusddH is visible", "hidden")
    chk(st["on_hold_on"], "its on-hold item carries class on", "missing")
    chk(not st["processing_on"], "its processing item does NOT carry class on", "on present")


def qa_sta_4(page):
    # Re-tiered to [WF] 2026-08-03 after [OD-WFX-1] was applied to the wireframe.
    fresh(page)
    page.click('#st-normal button[data-open="statusdd"]')
    chk(page.evaluate("() => getComputedStyle(document.querySelector('#statusdd')).display !== 'none'"),
        "#statusdd is open", "not open")
    page.click("#st-normal .otitle h2")   # page background — outside the dropdown
    closed = page.evaluate("() => getComputedStyle(document.querySelector('#statusdd')).display === 'none'")
    chk(closed, "the dropdown is no longer visible after an outside click", "still open")
    eq(T(page, "#st-normal #ordStatus"), "Processing", "status badge unchanged")
    # "no toast appears": the wireframe has no toast layer at all — assert none materialized.
    chk(N(page, ".toast") == 0, "no toast appears", "toast element found")


def qa_sta_5(page):
    fresh(page)
    b = page.evaluate("""() => {
        const e = document.querySelector('#st-normal #ordStatus');
        return {text: qaText(e), cls: e.className};
    }""")
    eq(b["text"], "Processing", "#ordStatus")
    chk("st-processing" in b["cls"], "#ordStatus carries class st-processing", b["cls"])
    chk(N(page, "#st-normal [id^=holdBanner]") == 0
        and "⏸ On Hold by urgent CS request" not in T(page, "#st-normal"),
        "#st-normal contains NO hold banner element", "banner found")
    go_hold(page)
    h = page.evaluate("""() => {
        const e = document.querySelector('#st-hold .status');
        const ban = document.querySelector('#holdBannerH');
        return {text: qaText(e), cls: e.className,
                ban_vis: getComputedStyle(ban).display !== 'none', ban_text: qaText(ban)};
    }""")
    eq(h["text"], "On Hold", "#st-hold .status")
    chk("st-hold" in h["cls"], "status carries class st-hold", h["cls"])
    chk(h["ban_vis"], "#holdBannerH visible", "hidden")
    eq(h["ban_text"], BANNER, "#holdBannerH exact banner copy")


def qa_sta_6(page):
    fresh(page)
    data = page.evaluate("""() => {
        const S = (root) => {
            const q = (sel) => root.querySelector(sel);
            const secs = [...root.querySelectorAll('.sec')];
            const ft = secs.find(s => s.querySelector('h3')
                                 && qaText(s.querySelector('h3')).includes('Fulfillment Tracking'));
            const rows = [...root.querySelectorAll('.litable tbody tr')];
            const ob = [...root.querySelectorAll('.li-foot button')]
                       .find(b => qaText(b) === '📦 Outbound');
            const badge = q('.otitle .status');
            return {
                nav: qaText(q('.nav')), subbar: qaText(q('.subbar')), info3: qaText(q('.info3')),
                cmtlist: qaText(q('.cmt-list')), ft: qaText(ft),
                logrows: [...root.querySelectorAll('.logtbl tr')].map(r => qaText(r)),
                rows_other: [0, 2, 3].map(i => qaText(rows[i])),
                row2: qaText(rows[1]),
                row2_btns: [...rows[1].querySelectorAll('td:last-child button')].map(b => qaText(b)),
                badge: {text: qaText(badge), cls: badge.className, id: badge.getAttribute('id')},
                dd_on: qaText(q('.statusdd div.on')),
                ob: {cls: ob.className, disabled: ob.hasAttribute('disabled'),
                     id: ob.getAttribute('id')},
                banner: !!root.querySelector('#holdBannerH'),
                ids: [...root.querySelectorAll('[id]')].map(e => e.id).sort()};
        };
        return {n: S(document.querySelector('#st-normal')),
                h: S(document.querySelector('#st-hold'))};
    }""")
    n, h = data["n"], data["h"]
    # NEGATIVE half: the named blocks are textually identical
    for key in ("nav", "subbar", "info3", "cmtlist", "ft", "logrows", "rows_other"):
        chk(n[key] == h[key], f"{key} textually identical between states",
            f"differs: {n[key]!r} vs {h[key]!r}"[:400])
    # Diff (1) status badge
    chk(n["badge"]["text"] == "Processing" and "st-processing" in n["badge"]["cls"]
        and h["badge"]["text"] == "On Hold" and "st-hold" in h["badge"]["cls"],
        "diff 1: badge Processing/st-processing vs On Hold/st-hold",
        (n["badge"], h["badge"]))
    # Diff (2) hold banner presence
    chk(not n["banner"] and h["banner"], "diff 2: #holdBannerH only in State 2",
        (n["banner"], h["banner"]))
    # Diff (3) statusdd .on
    chk(n["dd_on"] == "processing" and h["dd_on"] == "on-hold",
        "diff 3: dropdown on-item processing vs on-hold", (n["dd_on"], h["dd_on"]))
    # Diff (4) footer Outbound
    chk("btn-green" in n["ob"]["cls"] and not n["ob"]["disabled"] and n["ob"]["id"] == "obBtn"
        and "btn-gray" in h["ob"]["cls"] and h["ob"]["disabled"] and h["ob"]["id"] is None,
        "diff 4: Outbound btn-green/#obBtn vs btn-gray+disabled+no id", (n["ob"], h["ob"]))
    # Diff (5) row 2 tag + Actions button
    chk("INBOUNDED" in n["row2"] and "Cancel Inbound" in n["row2_btns"]
        and "PENDING" in h["row2"] and "Inbound" in h["row2_btns"]
        and "Cancel Inbound" not in h["row2_btns"],
        "diff 5: row 2 INBOUNDED/Cancel Inbound vs PENDING/Inbound",
        (n["row2_btns"], h["row2_btns"]))
    # Diff (6) explicit id-set comparison
    eq(n["ids"], sorted(["inbox1", "statusdd", "addCmt", "ordStatus", "obBtn"]),
       "State 1 id set")
    eq(h["ids"], sorted(["inbox1H", "statusddH", "addCmtH", "holdBannerH"]),
       "State 2 id set")


# ---------------------------------------------------------------- QA-EDIT

def qa_edit_1(page):
    fresh(page)
    vals = page.evaluate("""() =>
        [...document.querySelectorAll('#st-normal tr.row-edit input.ed-in')].map(i => i.value)""")
    eq(vals, ["12101316464794", "2026-06-30", "15000", "10323100835644",
              "https://www.coupang.com/vp/products/7055479133?itemId=17506867787"],
       "5 whitelisted inputs, values in DOM order")
    today = page.evaluate("""() => {
        const b = document.querySelector('#st-normal tr.row-edit button.ed-today');
        if (!b) return null;
        const date = [...document.querySelectorAll('#st-normal tr.row-edit input.ed-in')]
                     .find(i => i.value === '2026-06-30');
        return {text: qaText(b), same_cell: b.closest('td') === date.closest('td'),
                after_date: !!(date.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING)};
    }""")
    chk(today and today["text"] == "Today", "button.ed-today exists with text exactly Today", today)
    chk(today["same_cell"] and today["after_date"],
        "Today is positioned under (same cell, after) the date input", today)


def qa_edit_2(page):
    fresh(page)
    st = page.evaluate("""() => {
        const cell = document.querySelector('#st-normal tr.row-edit td:last-child');
        return {ok: qaText(cell.querySelector('.act-ic button.ok')),
                no: qaText(cell.querySelector('.act-ic button.no')),
                labels: [...cell.querySelectorAll('button')].map(b => qaText(b)),
                edit: cell.querySelectorAll('.edit').length,
                del_: cell.querySelectorAll('.del').length};
    }""")
    eq(st["ok"], "✓", "button.ok")
    eq(st["no"], "✕", "button.no")
    chk("Cancel Inbound" not in st["labels"], "no Cancel Inbound in the edit-mode Actions cell",
        st["labels"])
    chk(st["edit"] == 0 and st["del_"] == 0, "no .edit and no .del button", st)


def qa_edit_3(page):
    fresh(page)
    # named read-only cells (1-based td positions): SKU 2 · PN 4 · PN KR 5 · Size 6 · Qty 7
    # · Subtotal 8 · Total 9 · Latest Inventory Count 10 · Inbound Status 11 · Sourcing Route 12
    bad = page.evaluate("""() => {
        const tds = [...document.querySelectorAll('#st-normal tr.row-edit td')];
        return [2, 4, 5, 6, 7, 8, 9, 10, 11, 12]
            .filter(i => tds[i - 1].querySelector('input')).map(i => i);
    }""")
    eq(bad, [], "commerce cells containing an input element")


def qa_edit_4(page):
    fresh(page)
    st = page.evaluate("""() => {
        const tr = [...document.querySelectorAll('#st-normal .litable tbody tr')]
            .find(r => qaText(r.querySelector('td:nth-child(2)')).startsWith('100043697'));
        const tds = [...tr.querySelectorAll('td')];
        const inv = tds.slice(9, 17);
        return {vals: inv.map(td => qaText(td)),
                inputs: inv.filter(td => td.querySelector('input')).length,
                link: inv[7].querySelector('a') ? qaText(inv[7].querySelector('a')) : null};
    }""")
    eq(st["vals"], ["0", "INBOUNDED", "JIT (Coupang)", "12101316464794", "2026-06-30",
                    "₩17,100", "10323100835456", "coupang…7923"],
       "Inventory cells of SKU 100043697 in order")
    eq(st["link"], "coupang…7923", "CP Link renders as a link")
    eq(st["inputs"], 0, "cells containing an input")


def qa_edit_5(page):
    fresh(page)
    rows = page.evaluate("""() =>
        [...document.querySelectorAll('#st-normal .litable tbody tr:not(.row-edit)')].map(tr => {
            const cell = tr.querySelector('td:last-child');
            const e = cell.querySelector('button.edit'), d = cell.querySelector('button.del');
            return {edit: e ? qaText(e) : null, del_: d ? qaText(d) : null,
                    dm: d ? d.getAttribute('data-modal') : null};
        })""")
    chk(len(rows) == 3, "3 non-edit rows", len(rows))
    for i, r in enumerate(rows):
        chk(r["edit"] == "✎" and r["del_"] == "🗑" and r["dm"] == "m-del",
            f"non-edit row {i+1} has ✎ and 🗑 (data-modal=m-del)", r)


# ---------------------------------------------------------------- QA-DEL

M3_BODY = "This action cannot be undone. This will permanently delete the line item."


def assert_modal_strings(page):
    st = page.evaluate("""() => {
        const hdr = document.querySelector('#m-del .modal header');
        return {open: document.querySelector('#m-del').classList.contains('open'),
                first_text_node: hdr.childNodes[0].nodeValue,
                x: qaText(hdr.querySelector('.x')),
                body: qaText(document.querySelector('#m-del .modal .body')),
                foot: qaAll('#m-del .modal .foot button')};
    }""")
    chk(st["open"], "#m-del gains class open", "not open")
    eq(st["first_text_node"], "Are you sure?", "header first text node")
    eq(st["x"], "✕", "header .x control text")
    eq(st["body"], M3_BODY, "modal body text")
    eq(st["foot"], ["Cancel", "Delete"], "footer buttons in order")


def qa_del_1(page):
    fresh(page)
    page.click('.wf-tab[data-modal="m-del"]')
    assert_modal_strings(page)


def qa_del_2(page):
    fresh(page)
    page.click("#st-normal .litable tbody tr:nth-child(2) .act-ic .del")
    assert_modal_strings(page)


def qa_del_3(page):
    fresh(page)
    go_hold(page)
    page.click("#st-hold .litable tbody .act-ic .del")
    chk(page.evaluate("() => document.querySelector('#m-del').classList.contains('open')"),
        "#m-del gains class open from a State 2 🗑 (shared modal)", "not open")


def qa_del_4(page):
    fresh(page)
    page.click('.wf-tab[data-modal="m-del"]')
    page.click("#m-del .modal .foot button:has-text('Cancel')")
    chk(not page.evaluate("() => document.querySelector('#m-del').classList.contains('open')"),
        "#m-del loses class open after footer Cancel", "still open")
    eq(N(page, "#st-normal .litable tbody tr"), 4, "table still 4 rows")


def qa_del_5(page):
    fresh(page)
    page.click('.wf-tab[data-modal="m-del"]')
    page.click("#m-del .modal header .x")
    chk(not page.evaluate("() => document.querySelector('#m-del').classList.contains('open')"),
        "#m-del loses class open after ✕", "still open")
    eq(N(page, "#st-normal .litable tbody tr"), 4, "table still 4 rows")


def qa_del_6(page):
    fresh(page)
    page.click('.wf-tab[data-modal="m-del"]')
    page.click("#m-del", position={"x": 8, "y": 8})   # inside overlay, outside .modal
    chk(not page.evaluate("() => document.querySelector('#m-del').classList.contains('open')"),
        "#m-del loses class open after a backdrop click", "still open")
    eq(N(page, "#st-normal .litable tbody tr"), 4, "table still 4 rows")


# ---------------------------------------------------------------- QA-PRT

def qa_prt_1(page):
    fresh(page)
    labels = TA(page, "#st-normal .otitle button")
    chk("🖨 Print" in labels, "a button in .otitle labelled exactly 🖨 Print", labels)
    whole = page.evaluate("() => qaText(document.documentElement)")
    chk("Print (YUN)" not in whole and "Print (DELEO)" not in whole,
        "'Print (YUN)' / 'Print (DELEO)' appear nowhere on the page", "found")
    eq(T(page, "#st-normal .otitle .carrier"), "YUN", ".carrier badge in the title row")


def qa_prt_2(page):
    fresh(page)
    for state in ("#st-normal", "#st-hold"):
        labels = TA(page, f"{state} .otitle button")
        chk("View Label" in labels and "🖨 Print" in labels,
            f"{state} .otitle has distinct View Label and 🖨 Print buttons", labels)


# ---------------------------------------------------------------- QA-REN

def qa_ren_1(page):
    fresh(page)
    st = page.evaluate("""() => {
        const tr1 = [...document.querySelectorAll('#st-normal .litable thead tr')][0];
        const tr2 = [...document.querySelectorAll('#st-normal .litable thead tr')][1];
        const ths = [...tr1.querySelectorAll('th')];
        return {tr1: ths.map(th => ({rs: th.getAttribute('rowspan'), cs: th.getAttribute('colspan'),
                                     text: qaText(th), has_cb: !!th.querySelector('input[type=checkbox]')})),
                tr2: qaAll('th', tr2),
                td_counts: [...document.querySelectorAll('#st-normal .litable tbody tr')]
                           .map(r => r.querySelectorAll('td').length)};
    }""")
    t = st["tr1"]
    chk(len(t) == 6, "first header row has 6 th cells", len(t))
    chk(t[0]["rs"] == "2" and t[0]["has_cb"], "th1 rowspan=2 select-all checkbox", t[0])
    chk(t[1]["rs"] == "2" and t[1]["text"] == "SKU", "th2 rowspan=2 SKU", t[1])
    chk(t[2]["rs"] == "2" and t[2]["text"] == "Image", "th3 rowspan=2 Image", t[2])
    chk(t[3]["cs"] == "6" and t[3]["text"] == "Product Information (WooCommerce)",
        "th4 colspan=6 Product Information (WooCommerce)", t[3])
    chk(t[4]["cs"] == "8" and t[4]["text"] == "Inventory", "th5 colspan=8 Inventory", t[4])
    chk(t[5]["rs"] == "2" and t[5]["text"] == "Actions", "th6 rowspan=2 Actions", t[5])
    eq(st["tr2"], ["Product Name", "Product Name KR", "Size", "Qty", "Subtotal", "Total",
                   "Latest Inventory Count", "Inbound Status", "Sourcing Route", "Order Number",
                   "Order Date", "Product Cost 🤖", "Tracking Number", "CP Link"],
       "second header row in order")
    eq(st["td_counts"], [18, 18, 18, 18], "each tbody tr renders 18 td cells")


def qa_ren_2(page):
    fresh(page)
    for state in ("#st-normal", "#st-hold"):
        headers = TA(page, f"{state} .litable th")
        for banned in ("Delivery Company", "Comments", "Inbound Request"):
            chk(all(h != banned for h in headers),
                f"no {state} .litable header cell reads {banned!r}", headers)


def qa_ren_3(page):
    fresh(page)
    rows = line_rows(page, "#st-normal")
    lic = {r["sku"].split(" ")[0]: r["tds"][9] for r in rows}
    for sku in ("100005104", "100043697", "100012534"):
        eq(lic[sku], "0", f"Latest Inventory Count of JIT SKU {sku}")
    eq(lic["100005088"], "12", "Latest Inventory Count of WHOLESALE SKU 100005088")
    # A 0 on a JIT line is the expected value — never reported as a defect (runner guidance).


def qa_ren_4(page):
    fresh(page)
    tags = page.evaluate("""() =>
        [...document.querySelectorAll('#st-normal .litable span.tag-jit, #st-normal .litable span.tag-wholesale')]
        .map(t => {
            const cs = getComputedStyle(t);
            return {cls: t.className, text: qaText(t), bg: cs.backgroundColor, color: cs.color};
        })""")
    chk(len(tags) == 4, "4 sourcing-route tag spans", len(tags))
    for t in tags:
        chk(t["bg"] == "rgba(0, 0, 0, 0)", "computed background fully transparent", t)
        chk(t["color"] == "rgb(20, 16, 27)", "computed color #14101B (var(--ink))", t)
        chk(t["text"] in ("JIT (Coupang)", "WHOLESALE"),
            "visible strings exactly JIT (Coupang) / WHOLESALE", t)


def qa_ren_5(page):
    fresh(page)
    cells = page.evaluate("""() =>
        [...document.querySelectorAll('#st-normal .litable tbody tr, #st-hold .litable tbody tr')]
        .map(tr => qaText([...tr.querySelectorAll('td')][11]))""")
    for c in cells:
        chk(c != "JIT", "bare JIT with no parenthetical in no Sourcing Route cell", cells)
        chk("OTHER (" not in c, "'OTHER (' in no Sourcing Route cell", cells)
        chk(c in ("JIT (Coupang)", "WHOLESALE"),
            "every JIT cell reads exactly JIT (Coupang)", cells)


def qa_ren_6(page):
    fresh(page)
    rows = page.evaluate("""() =>
        [...document.querySelectorAll('#st-normal .litable tbody tr')].map(tr => {
            const tds = [...tr.querySelectorAll('td')];
            const first_b = (td) => {
                const b = td.querySelector('b');
                return b && td.firstElementChild === b ? qaText(b) : null;
            };
            return [first_b(tds[3]), first_b(tds[4])];
        })""")
    for i, (en, kr) in enumerate(rows):
        chk(en == "Dr.Jart+", f"row {i+1} Product Name begins with <b>Dr.Jart+</b>", en)
        chk(kr == "Dr.Jart+", f"row {i+1} Product Name KR begins with <b>Dr.Jart+</b>", kr)
    whole = page.evaluate("() => document.documentElement.textContent")
    chk("닥터자르트" not in whole, "닥터자르트 appears nowhere on the page", "found")


def qa_ren_7(page):
    fresh(page)
    rows = page.evaluate("""() =>
        [...document.querySelectorAll('#st-normal .litable tbody tr')].map(tr => {
            const tds = [...tr.querySelectorAll('td')];
            return {sku: qaText(tds[1]), sku_bot: qaText(tds[1].querySelector('span.bot')),
                    qty: qaText(tds[6]),
                    qty_bot: qaText(tds[6].querySelector('span.bot'))};
        })""")
    for r in rows:
        base = r["sku"].split(" ")[0]
        eq(r["sku_bot"], f"({base}*)", f"SKU {base} span.bot")
        eq(r["qty_bot"], "(1*)", "Qty span.bot")
        chk(r["qty"].startswith("1"), "Qty cell shows 1 followed by (1*)", r["qty"])
    eq(T(page, "#st-normal .liinfo"), LIINFO, "#st-normal .liinfo")


def qa_ren_8(page):
    fresh(page)
    st = page.evaluate("""() => {
        const rows = [...document.querySelectorAll('#st-normal .logtbl tr')];
        return {h4: qaText(document.querySelector('#st-normal .logsec h4')),
                ths: qaAll('#st-normal .logtbl th'),
                data: rows.slice(1).map(r => qaAll('td', r)),
                action_cls: rows.slice(1).map(r => r.querySelectorAll('td')[1].className)};
    }""")
    chk(st["h4"].startswith("Inbound / Outbound Actor Log")
        and st["h4"].endswith("— New"), "h4 begins with the heading followed by — New", st["h4"])
    eq(st["ths"], ["Time", "Action", "SKU", "Qty", "Operator", "Note"], "Actor Log columns")
    eq(st["data"], [
        ["07-01 09:32", "OUTBOUND", "All (4 SKU)", "4", "Dean", "–"],
        ["07-01 09:10", "INBOUND", "100012534", "1", "Miranti", "–"],
        ["07-01 08:58", "INBOUND", "100043697", "1", "Miranti", "–"],
        ["06-30 20:15", "CANCEL INBOUND (Restock)", "100005104", "1", "Dean",
         "Corrected duplicate inbound"]], "Actor Log rows newest first")
    eq(st["action_cls"], ["act-out", "act-in", "act-in", "act-cancel"], "Action cell classes")
    # Grammar/ordering only — demo-data inconsistency with row tags is §2.5 B, never a bug.


def qa_ren_9(page):
    fresh(page)
    st = page.evaluate("""() => ({
        thead: qaAll('#st-normal .tbl thead th'),
        row: qaAll('#st-normal .tbl tbody td'),
        chip: qaText(document.querySelector('#st-normal .tbl .st-delivered')),
        lastmile: qaText(document.querySelector('#st-normal .lastmile')),
        heading: qaText([...document.querySelectorAll('#st-normal .minih')]
                        .find(m => qaText(m).startsWith('TRACKING HISTORY'))),
        track_thead: qaAll('#st-normal .trackscroll thead th'),
        nodes: qaAll('#st-normal .trackscroll .node')})""")
    eq(st["thead"], ["Provider Order ID", "Tracking Number", "Status", "Status Description",
                     "Created At", "Updated At"], "SHIPMENT DETAILS columns")
    eq(st["row"], ["YT2618100709331860", "34YEM055929401000910906", "DELIVERED",
                   "Shipment information received", "6/30/2026, 8:55:53 PM",
                   "7/13/2026, 10:10:32 AM"], "SHIPMENT DETAILS row")
    eq(st["chip"], "DELIVERED", ".st-delivered chip")
    eq(st["lastmile"], "Last mile: AustraliaPost", ".lastmile")
    eq(st["heading"], "TRACKING HISTORY (synced 7/16/2026, 4:51:40 AM)", "tracking heading")
    eq(st["track_thead"], ["Time (local)", "Node", "Description", "Location", "UTC"],
       "TRACKING HISTORY columns")
    for node in ("DELIVERED", "DELIVERY_ATTEMPT", "IN_TRANSIT_CARRIER", "ORDER_CREATION"):
        chk(node in st["nodes"], f".node chips include {node}", st["nodes"])


def qa_ren_10(page):
    fresh(page)
    st = page.evaluate("""() => {
        const tr = [...document.querySelectorAll('#st-normal .litable tbody tr')]
            .find(r => qaText(r.querySelector('td:nth-child(2)')).startsWith('100043697'));
        const li_tn = qaText([...tr.querySelectorAll('td')][15]);
        const ft_tn = qaText(document.querySelector('#st-normal .tbl tbody td:nth-child(2)'));
        const li_in_litable = true;
        return {li_tn, ft_tn,
                different_tables: !document.querySelector('#st-normal .tbl')
                    .contains(tr)};
    }""")
    eq(st["li_tn"], "10323100835456", "line-item Tracking Number (SKU 100043697)")
    eq(st["ft_tn"], "34YEM055929401000910906", "Fulfillment Tracking Tracking Number")
    chk(st["li_tn"] != st["ft_tn"] and st["different_tables"],
        "the two namespaces render in different sections — never the same field", st)


def qa_ren_11(page):
    fresh(page)
    st = page.evaluate("""() => ({
        carrier: qaText(document.querySelector('#st-normal .ftbadge .carrier')),
        btns: qaAll('#st-normal .ftbadge button')})""")
    eq(st["carrier"], "YUN", ".ftbadge .carrier")
    chk("✎ Change Tracking #" in st["btns"], "button labelled exactly ✎ Change Tracking #",
        st["btns"])
    chk("Reset Order" in st["btns"], "button labelled exactly Reset Order", st["btns"])


def qa_ren_12(page):
    fresh(page)
    st = page.evaluate("""() => {
        const kv = {};
        [...document.querySelectorAll('#st-normal .info3 .kv')].forEach(k => {
            kv[qaText(k.querySelector('.k'))] = qaText(k.querySelector('.v'));
        });
        return {order_date: kv['Order Date'], created: kv['Order Created At'],
                log_times: [...document.querySelectorAll('#st-normal .logtbl tr')].slice(1)
                    .map(r => qaText(r.querySelector('td'))),
                cmt_times: qaAll('#st-normal .cmt-list time'),
                ship_times: qaAll('#st-normal .tbl tbody td').slice(4, 6),
                track_cols: qaAll('#st-normal .trackscroll thead th')};
    }""")
    eq(st["order_date"], "2026-06-30 SGT", "Order Date (zone printed)")
    eq(st["created"], "30/06/2026 19:55:28 SGT", "Order Created At (zone printed)")
    mmdd = re.compile(r"^\d{2}-\d{2} \d{2}:\d{2}$")
    for tcell in st["log_times"]:
        chk(mmdd.match(tcell), "Actor Log Time matches MM-DD HH:mm with no zone suffix",
            st["log_times"])
    for tcell in st["cmt_times"]:
        chk(mmdd.match(tcell), "comment time matches MM-DD HH:mm", st["cmt_times"])
    us = re.compile(r"^\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} (AM|PM)$")
    for tcell in st["ship_times"]:
        chk(us.match(tcell), "SHIPMENT DETAILS times match M/D/YYYY, h:mm:ss AM/PM",
            st["ship_times"])
    chk("Time (local)" in st["track_cols"] and "UTC" in st["track_cols"],
        "TRACKING HISTORY exposes both Time (local) and UTC", st["track_cols"])


def qa_ren_17(page):
    fresh(page)
    st = page.evaluate("""() => {
        const tr = [...document.querySelectorAll('#st-normal .litable tbody tr')]
            .find(r => qaText(r.querySelector('td:nth-child(2)')).startsWith('100005088'));
        const tds = [...tr.querySelectorAll('td')];
        const pick = [12, 13, 15, 16].map(i => ({text: qaText(tds[i]),
                                                 has_a: !!tds[i].querySelector('a')}));
        return {pick, cost: qaText(tds[14])};
    }""")
    for cell in st["pick"]:
        eq(cell["text"], "–", "absent agent-tracking value renders –")
        chk(not cell["has_a"], "– is plain text, never a link", cell)
    eq(st["cost"], "₩22,425", "Product Cost 🤖 of the WHOLESALE row")


# ---------------------------------------------------------------- QA-SUB

def qa_sub_1(page):
    fresh(page)
    for state in ("#st-normal", "#st-hold"):
        btns = page.evaluate("""(state) =>
            [...document.querySelectorAll(state + ' .subbar button')]
            .map(b => ({text: qaText(b), cls: b.className}))""", state)
        eq([b["text"] for b in btns],
           ["← Back to Orders", "↻ Audit History", "↗ View in WP", "⧉ Clone Order",
            "✕ Cancel Order"], f"{state} subbar labels in order")
        chk(btns[0]["cls"] == "back", "Back has class back", btns[0])
        chk(btns[1]["cls"] == "link-btn", "Audit History class link-btn", btns[1])
        chk(btns[2]["cls"] == "link-btn blue", "View in WP class link-btn blue", btns[2])
        chk(btns[3]["cls"] == "link-btn blue", "Clone Order class link-btn blue", btns[3])
        chk(btns[4]["cls"] == "link-btn red", "Cancel Order class link-btn red", btns[4])


def qa_sub_2(page):
    fresh(page)
    st = page.evaluate("""() => ({
        h2: qaText(document.querySelector('#st-normal .otitle h2')),
        badge: qaText(document.querySelector('#st-normal .otitle .status')),
        carrier: qaText(document.querySelector('#st-normal .otitle .carrier')),
        btns: qaAll('#st-normal .otitle button')})""")
    eq(st["h2"], "Order # 407847", ".otitle h2")
    chk(st["badge"] == "Processing", "followed by a status badge", st["badge"])
    eq(st["carrier"], "YUN", ".carrier badge")
    for label in ("View Label", "🖨 Print", "Change Status ▾"):
        chk(label in st["btns"], f"title-row button labelled exactly {label}", st["btns"])


def qa_sub_3(page):
    fresh(page)
    st = page.evaluate("""() => {
        const panel = [...document.querySelectorAll('#st-normal .info3 > div')]
            .find(d => d.querySelector('h3') && qaText(d.querySelector('h3')).includes('Order Information'));
        const kv = {};
        [...panel.querySelectorAll('.kv')].forEach(k => {
            kv[qaText(k.querySelector('.k'))] = qaText(k.querySelector('.v'));
        });
        const pic_btn = panel.querySelector('.kv:last-child .v button');
        return {kv, pic_btn: pic_btn ? qaText(pic_btn) : null};
    }""")
    kv = st["kv"]
    eq(kv["Order Date"], "2026-06-30 SGT", "Order Date")
    eq(kv["Order Created At"], "30/06/2026 19:55:28 SGT", "Order Created At")
    eq(kv["Total Items"], "4", "Total Items")
    eq(kv["Total Discount"], "AUD 13.11", "Total Discount")
    eq(kv["Total Amount"], "AUD 129.8", "Total Amount")
    chk(kv["PIC"].startswith("Egita"), "PIC = Egita", kv["PIC"])
    eq(st["pic_btn"], "✎ Edit", "PIC bordered button")


def qa_sub_4(page):
    fresh(page)
    for state in ("#st-normal", "#st-hold"):
        st = page.evaluate("""(state) => {
            const pic = [...document.querySelectorAll(state + ' .info3 .kv')]
                .find(k => qaText(k.querySelector('.k')) === 'PIC');
            const btn = pic.querySelector('.v button');
            const bare = [...pic.querySelectorAll('.v *')]
                .filter(e => e.tagName !== 'BUTTON' && qaText(e) === '✎').length;
            return {btn: btn ? qaText(btn) : null, tag: btn ? btn.tagName : null, bare};
        }""", state)
        chk(st["tag"] == "BUTTON" and "Edit" in (st["btn"] or ""),
            f"{state} PIC control is a bordered button whose text includes Edit", st)
        chk(st["bare"] == 0, f"{state} has no standalone bare ✎ glyph as the PIC control", st)


def qa_sub_5(page):
    fresh(page)
    st = page.evaluate("""() => {
        const panels = [...document.querySelectorAll('#st-normal .info3 > div')];
        const by = (name) => panels.find(d => d.querySelector('h3')
                                       && qaText(d.querySelector('h3')).includes(name));
        const kvmap = (p) => {
            const kv = {};
            [...p.querySelectorAll('.kv')].forEach(k => {
                kv[qaText(k.querySelector('.k'))] = qaText(k.querySelector('.v'));
            });
            return kv;
        };
        const bill = by('Billing Address'), ship = by('Shipping Address');
        return {bill_edit: qaText(bill.querySelector('h3 span.edit')),
                ship_edit: qaText(ship.querySelector('h3 span.edit')),
                bill: kvmap(bill), ship: kvmap(ship)};
    }""")
    eq(st["bill_edit"], "✎", "Billing heading span.edit")
    eq(st["ship_edit"], "✎", "Shipping heading span.edit")
    eq(st["ship"]["Tax ID"], "–", "Tax ID")
    eq(st["ship"]["Short Address Code"], "–", "Short Address Code")
    eq(st["bill"]["Email"], "m.saltoon@gmail.com", "Billing Email")
    eq(st["bill"]["Phone"], "+61415999051", "Billing Phone")


def qa_sub_6(page):
    fresh(page)
    eq(T(page, "#st-normal .li-foot .tq"), "Total Quantity: 4", "#st-normal .tq")
    labels = TA(page, "#st-normal .li-foot button")
    chk("+ Add Line Item" in labels, "+ Add Line Item exists in the same footer", labels)
    eq(T(page, "#st-hold .li-foot .tq"), "Total Quantity: 4", "#st-hold .tq")


def qa_sub_7(page):
    fresh(page)
    st = page.evaluate("""() => {
        const nav = document.querySelector('#st-normal .nav');
        return {brand: qaText(nav.querySelector('.brand')),
                spans: [...nav.querySelectorAll(':scope > span:not(.sp)')]
                    .map(s => qaText(s)).filter(t => t),
                icon: qaText(nav.querySelector('.icon-btn')),
                user: qaText(nav.querySelector('.user')),
                avatar: qaText(nav.querySelector('.avatar')),
                logout: qaText(nav.querySelector('.logout'))};
    }""")
    eq(st["brand"], "SkinSeoul", "brand")
    for item in ("Operation AI ▾", "Catalog Management ▾", "OMS Center ▾",
                 "Site Management ▾", "Customer Management ▾", "SkinSeoul WP Admin"):
        chk(item in st["spans"], f"nav shows {item}", st["spans"])
    chk(st["icon"].startswith("💬 Comments"), "💬 Comments button present", st["icon"])
    chk("Yongwon Ryu" in st["user"], "user chip Yongwon Ryu", st["user"])
    eq(st["avatar"], "Y", "Y avatar")
    eq(st["logout"], "Logout", "Logout button")


def qa_sub_19(page):
    fresh(page)
    kv = page.evaluate("""() => {
        const kv = {};
        [...document.querySelectorAll('#st-normal .info3 .kv')].forEach(k => {
            kv[qaText(k.querySelector('.k'))] = qaText(k.querySelector('.v'));
        });
        return kv;
    }""")
    eq(kv["Total Discount"], "AUD 13.11", "Total Discount")
    eq(kv["Total Amount"], "AUD 129.8", "Total Amount")
    body_text_1 = page.evaluate("() => document.body.innerText")
    for cost in ("₩17,100", "₩22,425", "₩30,630"):
        chk(cost in body_text_1, f"product cost {cost} renders in purchase currency", "missing")
    chk("USD" not in body_text_1 and "$" not in body_text_1,
        "no USD figure and no converted amount anywhere (State 1)", "found")
    go_hold(page)
    body_text_2 = page.evaluate("() => document.body.innerText")
    chk("USD" not in body_text_2 and "$" not in body_text_2,
        "no USD figure and no converted amount anywhere (State 2)", "found")


# ---------------------------------------------------------------- registry / main

SCENARIOS = [
    # §8.3 group 1 — map
    ("QA-MAP-1", qa_map_1), ("QA-MAP-2", qa_map_2), ("QA-MAP-3", qa_map_3),
    ("QA-MAP-4", qa_map_4), ("QA-MAP-5", qa_map_5), ("QA-MAP-6", qa_map_6),
    # group 2 — pure render
    ("QA-REN-1", qa_ren_1), ("QA-REN-2", qa_ren_2), ("QA-REN-3", qa_ren_3),
    ("QA-REN-4", qa_ren_4), ("QA-REN-5", qa_ren_5), ("QA-REN-6", qa_ren_6),
    ("QA-REN-7", qa_ren_7), ("QA-REN-8", qa_ren_8), ("QA-REN-9", qa_ren_9),
    ("QA-REN-10", qa_ren_10), ("QA-REN-11", qa_ren_11), ("QA-REN-12", qa_ren_12),
    ("QA-REN-17", qa_ren_17),
    # group 3 — furniture render
    ("QA-SUB-1", qa_sub_1), ("QA-SUB-2", qa_sub_2), ("QA-SUB-3", qa_sub_3),
    ("QA-SUB-4", qa_sub_4), ("QA-SUB-5", qa_sub_5), ("QA-SUB-6", qa_sub_6),
    ("QA-SUB-7", qa_sub_7), ("QA-SUB-19", qa_sub_19),
    # group 4 — per-legend render and state tabs (QA-STA-4 back at [WF], v1.3)
    ("QA-INB-1", qa_inb_1), ("QA-INB-2", qa_inb_2), ("QA-INB-3", qa_inb_3),
    ("QA-INB-4", qa_inb_4), ("QA-INB-5", qa_inb_5),
    ("QA-OUT-1", qa_out_1), ("QA-OUT-2", qa_out_2), ("QA-OUT-3", qa_out_3),
    ("QA-STA-1", qa_sta_1), ("QA-STA-2", qa_sta_2), ("QA-STA-3", qa_sta_3),
    ("QA-STA-4", qa_sta_4), ("QA-STA-5", qa_sta_5), ("QA-STA-6", qa_sta_6),
    ("QA-EDIT-1", qa_edit_1), ("QA-EDIT-2", qa_edit_2), ("QA-EDIT-3", qa_edit_3),
    ("QA-EDIT-4", qa_edit_4), ("QA-EDIT-5", qa_edit_5),
    ("QA-PRT-1", qa_prt_1), ("QA-PRT-2", qa_prt_2),
    # group 5 — hub dropdown interactions (reload per scenario)
    ("QA-HUB-1", qa_hub_1), ("QA-HUB-2", qa_hub_2), ("QA-HUB-3", qa_hub_3),
    ("QA-HUB-4", qa_hub_4), ("QA-HUB-5", qa_hub_5), ("QA-HUB-6", qa_hub_6),
    ("QA-HUB-7", qa_hub_7), ("QA-HUB-8", qa_hub_8),
    # group 6 — thread mutations (reload per scenario)
    ("QA-CMT-1", qa_cmt_1), ("QA-CMT-2", qa_cmt_2), ("QA-CMT-3", qa_cmt_3),
    ("QA-CMT-4", qa_cmt_4), ("QA-CMT-5", qa_cmt_5), ("QA-CMT-6", qa_cmt_6),
    ("QA-CMT-7", qa_cmt_7),
    # group 7 — modal interactions
    ("QA-DEL-1", qa_del_1), ("QA-DEL-2", qa_del_2), ("QA-DEL-3", qa_del_3),
    ("QA-DEL-4", qa_del_4), ("QA-DEL-5", qa_del_5), ("QA-DEL-6", qa_del_6),
]


def main():
    results = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={"width": 1760, "height": 1100})
        for sid, fn in SCENARIOS:
            try:
                fn(page)
                results.append({"id": sid, "status": "pass"})
            except Fail as f:
                results.append({"id": sid, "status": "fail",
                                "expected": f.expected, "actual": f.actual})
            except Exception as e:  # runner/infrastructure error — not a spec verdict
                results.append({"id": sid, "status": "error",
                                "expected": "(runner error)", "actual": repr(e)[:500]})
        browser.close()
    passed = sum(1 for r in results if r["status"] == "pass")
    failed = [r for r in results if r["status"] == "fail"]
    errors = [r for r in results if r["status"] == "error"]
    # HANDOFF.md §4 documents `python3 qa-<screen>.py [--json out.json]` for all eight
    # runners. Without this the flag is accepted, nothing is written, and the run still
    # exits 0 — a pass rate with no artefact behind it.
    if "--json" in sys.argv:
        _out = sys.argv[sys.argv.index("--json") + 1]
        _p = pathlib.Path(_out)
        _p.parent.mkdir(parents=True, exist_ok=True)
        with open(_p, "w", encoding="utf-8") as _f:
            json.dump({"slug": "order-detail", "executed": len(results), "passed": passed,
                       "failed": failed, "errors": errors}, _f, ensure_ascii=False, indent=1)
        print("wrote", _p)
    print(json.dumps({"slug": "order-detail", "executed": len(results), "passed": passed,
                      "failed": failed, "errors": errors}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
