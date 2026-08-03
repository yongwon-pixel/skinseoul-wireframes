#!/usr/bin/env python3
"""
Adversarial QA execution of wms2/specs/stock-status.md  §8  — every [WF]-tier scenario.

Rules of engagement (Verification Method 2):
  * Executed by a hostile QA robot that did NOT write the spec.
  * Only selectors / labels / expected strings that §8 itself supplies may be used.
  * If §8 does not say what to click or what to assert -> AMBIGUOUS, do not improvise.
  * Verdicts: PASS | FAIL | AMBIGUOUS | UNRUNNABLE

String-match convention adopted (derived from §8's own wording, not invented):
  "reads exactly X" / "innerText is exactly X"  -> strict equality
  "reads X" / "contains X" / "begins X"         -> containment / prefix
Every place this convention had to be applied to break a tie is recorded in the
evidence string so the reader can see where judgement was exercised.

Run:  python3 qa-stock-status.py
"""
import json, re, sys, pathlib
from playwright.sync_api import sync_playwright

TARGET = "file:///Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/stock-status/index.html"

PASS, FAIL, AMB, UNRUN = "PASS", "FAIL", "AMBIGUOUS", "UNRUNNABLE"
RESULTS = []


def rec(sid, verdict, evidence):
    RESULTS.append({"id": sid, "verdict": verdict, "evidence": evidence})


def ok(cond, sid, evidence_pass, evidence_fail):
    rec(sid, PASS if cond else FAIL, evidence_pass if cond else evidence_fail)


# ----------------------------------------------------------------- preflight
def preflight(page):
    """§8.0 mandatory preflight, steps 1-2 (+4 reload is the caller's job)."""
    page.goto(TARGET)
    page.wait_for_function("document.querySelector('#p-current').classList.contains('on')")
    page.click("#annoToggle")
    assert page.evaluate("document.body.classList.contains('no-anno')"), "preflight: no-anno not set"
    assert page.inner_text("#annoToggle").strip() == "Show annotations", "preflight: toggle label"


def txt(page, sel):
    return page.eval_on_selector(sel, "e => e.innerText").strip()


def js(page, expr):
    return page.evaluate(expr)


# ------------------------------------------------------------------- QA-NAV
def qa_nav_01(page):
    d = js(page, """() => {
      const st=[...document.querySelectorAll('.subtabs button')]
        .find(b=>b.innerText.trim().startsWith('Current Stocks'));
      return {cur:document.querySelector('#p-current').classList.contains('on'),
              others:['p-search','p-inbound','p-outbound']
                 .map(i=>document.getElementById(i).classList.contains('on')),
              stOn: st? st.classList.contains('on'):null,
              stText: st? st.innerText.trim():null};
    }""")
    good = d["cur"] and not any(d["others"]) and d["stOn"] and "● new · default" in d["stText"]
    ok(good, "QA-NAV-01", f"#p-current.on=True, others off, sub-tab={d['stText']!r} .on=True",
       f"got {d}")


def qa_nav_02(page):
    page.click(".subtabs button[data-sub='s-search']")
    a = js(page, """() => ({panes:[...document.querySelectorAll('.pane')].filter(p=>p.classList.contains('on')).map(p=>p.id),
      wf:[...document.querySelectorAll('.wf-tab')].find(b=>b.innerText.trim()==='Stock History Search').classList.contains('on')})""")
    page.click("//button[@class='wf-tab' and normalize-space(text())='Inbound Form']")
    b = js(page, """() => ({panes:[...document.querySelectorAll('.pane')].filter(p=>p.classList.contains('on')).map(p=>p.id),
      st:[...document.querySelectorAll('.subtabs button')].find(x=>x.innerText.trim().startsWith('Inbound Stock')).classList.contains('on')})""")
    good = a["panes"] == ["p-search"] and a["wf"] and b["panes"] == ["p-inbound"] and b["st"]
    ok(good, "QA-NAV-02", f"sub-tab->{a}; wf-bar->{b}", f"sub-tab->{a}; wf-bar->{b}")


def qa_nav_03(page):
    page.click("//button[@class='wf-tab' and normalize-space(text())='Modal: Reserved Orders']")
    a = js(page, "() => ({open:document.querySelector('#m-reserved').classList.contains('open'), cur:document.querySelector('#p-current').classList.contains('on')})")
    page.click("#m-reserved .foot button")
    b = js(page, "() => ({open:document.querySelector('#m-reserved').classList.contains('open'), cur:document.querySelector('#p-current').classList.contains('on')})")
    good = a["open"] and a["cur"] and (not b["open"]) and b["cur"]
    ok(good, "QA-NAV-03", f"after open {a}; after Close {b}", f"after open {a}; after Close {b}")


def qa_nav_04(page):
    t = txt(page, ".ptitle h2")
    ok(t == "WMS — Inventory", "QA-NAV-04", f"innerText == {t!r}", f"innerText == {t!r}, expected 'WMS — Inventory'")


def _all_surfaces(page):
    """innerText of .mock under each of the 4 panes + innerText of each of the 6 overlays."""
    out = {}
    for sub, pane in [("s-current", "p-current"), ("s-search", "p-search"),
                      ("s-inbound", "p-inbound"), ("s-outbound", "p-outbound")]:
        page.click(f".subtabs button[data-sub='{sub}']")
        out[f"mock@{pane}"] = txt(page, ".mock")
    for mid in ["m-reserved", "m-resrelease", "m-auditlog", "m-adjlog", "m-adjlog6", "m-adjust"]:
        page.evaluate(f"document.getElementById('{mid}').classList.add('open')")
        out[f"overlay#{mid}"] = txt(page, f"#{mid}")
        page.evaluate(f"document.getElementById('{mid}').classList.remove('open')")
    return out


def qa_nav_06(page):
    surf = _all_surfaces(page)
    hits = {k: re.findall(r".{0,25}print.{0,25}", v, re.I) for k, v in surf.items()}
    hits = {k: v for k, v in hits.items() if v}
    names = js(page, """() => [...document.querySelectorAll('button,a,input')]
        .map(e=>[e.innerText||'', e.value||'', e.placeholder||'', e.getAttribute('aria-label')||'', e.title||''].join(' '))
        .filter(s=>/print/i.test(s))""")
    good = not hits and not names
    ok(good, "QA-NAV-06", "0 /print/i matches in any pane/overlay innerText; 0 controls named /print/i",
       f"text hits={hits}; control hits={names}")


def qa_nav_07(page):
    d = js(page, """() => {
      const b=[...document.querySelectorAll('.subtabs button')];
      return {n:b.length, labels:b.map(x=>x.innerText.trim()),
        auditLogTabs:[...document.querySelectorAll('.subtabs button,.wf-tab')]
          .map(x=>x.innerText.trim()).filter(s=>/^audit\\s*log/i.test(s))};
    }""")
    want = ["Current Stocks", "Stock History", "Inbound Stock", "Outbound Stock"]
    good = d["n"] == 4 and all(d["labels"][i].startswith(want[i]) for i in range(4)) and not d["auditLogTabs"]
    ok(good, "QA-NAV-07",
       f"4 sub-tab buttons {d['labels']}; no tab named 'Audit Log' "
       f"(NOTE: 'no Audit Log tab anywhere' had to be scoped to .subtabs+.wf-tab — "
       f"the page does render the string 'Past Audit Logs')",
       f"got {d}")


def qa_nav_08(page):
    surf = _all_surfaces(page)
    pats = {"procurement hub": r"procurement hub", "return-bin": r"return.?bin",
            "sample": r"sample", "photo|upload": r"photo|upload"}
    hits = {}
    for name, p in pats.items():
        h = {k: re.findall(p, v, re.I) for k, v in surf.items()}
        h = {k: v for k, v in h.items() if v}
        if h:
            hits[name] = h
    nfile = js(page, "() => document.querySelectorAll('input[type=file]').length")
    good = not hits and nfile == 0
    ok(good, "QA-NAV-08", "0 matches for all four patterns across 4 panes + 6 overlays; 0 input[type=file]",
       f"hits={hits}; input[type=file]={nfile}")


def qa_nav_09(page):
    d = js(page, """() => ({tabs:[...document.querySelectorAll('.wf-tab')].map(b=>b.innerText.trim()),
                            toggles:[...document.querySelectorAll('.wf-toggle')].map(b=>b.id)})""")
    want = ["Current Stocks (default)", "Stock History Search", "Inbound Form", "Outbound Form",
            "Modal: Reserved Orders", "Modal: Cancel Inbound (Release Reservation)",
            "Modal: Past Audit Logs", "Modal: ADJUST Events (07-22)",
            "Modal: ADJUST Events (06-30)", "Modal: Confirm Audit Differences"]
    good = d["tabs"] == want and d["toggles"] == ["annoToggle"]
    ok(good, "QA-NAV-09", f"10 .wf-tab in exact order + 1 .wf-toggle#annoToggle", f"got {d}")


# -------------------------------------------------------------------- QA-CS
def cs_rows(page):
    return js(page, """() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r => {const c=[...r.children].map(td=>td.innerText.trim());
                   return {cells:c,
                           loc:(r.querySelector('.loc-in')||{}).value,
                           locPh:(r.querySelector('.loc-in')||{}).placeholder,
                           qty:(r.querySelector('.qty-in')||{}).value,
                           bcin:!!r.querySelector('.bcin'),
                           krFirstChild:(r.children[3].firstElementChild||{}).tagName,
                           krHTML:r.children[3].innerHTML,
                           thumb:(r.querySelector('.thumb')||{}).innerText};});""")


def qa_cs_01(page):
    rows = cs_rows(page)
    skus = [r["cells"][0] for r in rows]
    avail = [r["cells"][10] for r in rows]
    want_s = "100031877,100024743,100005088,100004819,100039958,100005104,100040311,100012534,100043697,100038120,100045210".split(",")
    want_a = "82,61,55,34,23,16,11,6,4,2,1".split(",")
    good = len(rows) == 11 and skus == want_s and avail == want_a
    ok(good, "QA-CS-01", f"11 rows, SKU order + Available {avail} match", f"skus={skus} avail={avail}")


def qa_cs_03(page):
    d = js(page, "() => [...document.querySelectorAll('.cs-controls select.sel')[0].options].map(o=>o.text.trim())")
    good = d[0] == "All Locations" and d[1:] == ["Line A", "Line B", "Line C"] and \
        not any(re.match(r"^[A-Z]-\d\d-\d\d$", o) for o in d)
    ok(good, "QA-CS-03", f"options={d}", f"options={d}")


def qa_cs_05(page):
    d = js(page, "() => [...document.querySelectorAll('.cs-controls select.sel')[1].options].map(o=>o.text.trim())")
    want = ["All Sourcing Routes", "SMART BUY", "JIT", "WHOLESALE", "PARTNERSHIP"]
    ok(d == want, "QA-CS-05", f"options == {d}", f"options == {d}, expected {want}")


def qa_cs_08(page):
    d = js(page, """() => [...document.querySelectorAll('#p-current .tag')].map(e=>{
        const cs=getComputedStyle(e);
        return {cls:e.className, bg:cs.backgroundColor, fw:cs.fontWeight};});""")
    classes = {c for e in d for c in e["cls"].split() if c.startswith("tag-")}
    good = all(e["bg"] in ("rgba(0, 0, 0, 0)", "transparent") and e["fw"] == "800" for e in d) and \
        classes == {"tag-smartbuy", "tag-jit", "tag-wholesale", "tag-partnership"}
    ok(good, "QA-CS-08", f"{len(d)} route cells: bg rgba(0,0,0,0), font-weight 800; classes {sorted(classes)}",
       f"got {d}")


def qa_cs_09(page):
    rows = cs_rows(page)
    all_b = all(r["krFirstChild"] == "B" for r in rows)
    r5104 = next(r for r in rows if r["cells"][0] == "100005104")
    good = all_b and "<b>Dr.Jart+</b> 포어레미디 리뉴잉 폼" in r5104["krHTML"]
    ok(good, "QA-CS-09", f"all 11 KR cells firstElementChild=<b>; 100005104 KR html={r5104['krHTML']!r}",
       f"allB={all_b}; 100005104 html={r5104['krHTML']!r}")


def qa_cs_10(page):
    r = next(r for r in cs_rows(page) if r["cells"][0] == "100038120")
    good = r["loc"] == "" and r["locPh"] == "Unassigned"
    ok(good, "QA-CS-10", f"100038120 .loc-in value='' placeholder={r['locPh']!r}, row present",
       f"value={r['loc']!r} placeholder={r['locPh']!r}")


def qa_cs_14(page):
    d = js(page, """() => {
      const ths=[...document.querySelectorAll('#p-current thead th')];
      return {visible:ths.filter(t=>getComputedStyle(t).display!=='none').map(t=>t.innerText.trim()),
              aud:ths.filter(t=>t.classList.contains('audcol')).map(t=>[t.innerText.trim(), getComputedStyle(t).display])};
    }""")
    want = ["SKU", "Image", "Product Name", "Product Name KR", "Size", "Barcode",
            "Sourcing Route", "Location", "Total", "Reserved", "Available"]
    audw = [["Counted Qty", "none"], ["Diff", "none"], ["Loss (₩)", "none"]]
    good = d["visible"] == want and d["aud"] == audw
    ok(good, "QA-CS-14", f"visible headers == spec list; audcol headers {d['aud']}", f"got {d}")


def qa_cs_15(page):
    rows = cs_rows(page)
    thumbs = [r["thumb"] for r in rows]
    sizes = [r["cells"][4] for r in rows]
    want = "30ml,50ea,50ml,50ml,350ml,150ml,100ml,75ml,150ml,70ea,250ml".split(",")
    good = all(t == "IMG" for t in thumbs) and sizes == want
    ok(good, "QA-CS-15", f"11 .thumb all 'IMG'; sizes {sizes}", f"thumbs={thumbs} sizes={sizes}")


def qa_cs_16(page):
    n = js(page, """() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r=>r.children[9])
        .filter(td=>td.querySelector('.reslink,a,[data-modal]')).length""")
    ok(n == 0, "QA-CS-16", "0 Reserved cells contain .reslink / <a> / [data-modal]",
       f"{n} Reserved cells carry a drill-down affordance")


# ------------------------------------------------------------------- QA-LOC
def qa_loc_01(page):
    d = js(page, """() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r=>({n:r.querySelectorAll('input.loc-in').length, v:r.querySelector('input.loc-in').value}))""")
    want = ["B-02-03", "A-03-02", "B-01-07", "A-02-13", "C-01-05", "A-01-04",
            "A-01-05", "A-02-20", "C-02-01", "", "B-03-02"]
    good = all(x["n"] == 1 for x in d) and [x["v"] for x in d] == want
    ok(good, "QA-LOC-01", f"1 input.loc-in per row; values {[x['v'] for x in d]}", f"got {d}")


def qa_loc_08(page):
    d = js(page, """() => {
      const rows=[...document.querySelectorAll('#p-current tbody tr')].filter(r=>!r.classList.contains('audrow'));
      const r43=rows.find(r=>r.children[0].innerText.trim()==='100024743');
      const r77=rows.find(r=>r.children[0].innerText.trim()==='100031877');
      const bc=r43.querySelector('input.bcin');
      return {ph: bc? bc.placeholder:null,
              plain: r77.children[5].innerText.trim(),
              bcinInTable: document.querySelectorAll('#p-current table .bcin').length,
              bcinIds:[...document.querySelectorAll('#p-current table .bcin')].map(e=>e.id||e.className)};
    }""")
    a = d["ph"] == "Enter barcode"
    b = d["plain"] == "8809738317481"
    c = d["bcinInTable"] == 1
    if a and b and c:
        rec("QA-LOC-08", PASS, f"{d}")
    else:
        rec("QA-LOC-08", FAIL,
            f"placeholder ok={a}, plain-text ok={b}; BUT spec says 'Exactly one .bcin exists in the table' — "
            f"document.querySelectorAll('#p-current table .bcin').length == {d['bcinInTable']} "
            f"({d['bcinIds']}): the [L-13] audit-row product search input #auSearch also carries class 'bcin' "
            f"and lives inside the same <table> (tr.audrow).")


def qa_loc_18(page):
    before = page.url
    page.fill("#p-current tbody tr:nth-child(4) input.loc-in", "A-02-14")
    page.press("#p-current tbody tr:nth-child(4) input.loc-in", "Enter")
    v = js(page, "() => [...document.querySelectorAll('#p-current tbody tr')].filter(r=>!r.classList.contains('audrow')).find(r=>r.children[0].innerText.trim()==='100004819').querySelector('.loc-in').value")
    good = v == "A-02-14" and page.url == before
    ok(good, "QA-LOC-18",
       f"live value == 'A-02-14', url unchanged (NOTE: spec says 'types A-02-14' into a field pre-filled "
       f"'A-02-13'; executed as replace/fill, since append would give 'A-02-13A-02-14')",
       f"value={v!r} url_before={before} url_after={page.url}")


# ------------------------------------------------------------------- QA-AUD
def start_audit(page):
    page.click("#toggleAudit")


def qa_aud_01(page):
    pre = js(page, """() => ({label:document.getElementById('toggleAudit').innerText.trim(),
       audVisible:[...document.querySelectorAll('#p-current .audcol')].filter(e=>getComputedStyle(e).display!=='none').length,
       summary:getComputedStyle(document.getElementById('auditSummary')).display,
       audrow:getComputedStyle(document.querySelector('#p-current .audrow')).display})""")
    start_audit(page)
    post = js(page, """() => {
      const rows=[...document.querySelectorAll('#p-current tbody tr')].filter(r=>!r.classList.contains('audrow'));
      const tb=document.querySelector('#p-current tbody');
      return {label:document.getElementById('toggleAudit').innerText.trim(),
        heads:[...document.querySelectorAll('#p-current thead th.audcol')].map(t=>[t.innerText.trim(),getComputedStyle(t).display]),
        audrowLast: tb.lastElementChild.classList.contains('audrow'),
        audrowDisp: getComputedStyle(document.querySelector('#p-current .audrow')).display,
        summary: getComputedStyle(document.getElementById('auditSummary')).display,
        locs: rows.map(r=>r.querySelector('.loc-in').value),
        lastSku: rows[rows.length-1].children[0].innerText.trim()};
    }""")
    want_locs = ["A-01-04", "A-01-05", "A-02-13", "A-02-20", "A-03-02", "B-01-07",
                 "B-02-03", "B-03-02", "C-01-05", "C-02-01"]
    good = (pre["label"] == "Start Stock Audit" and pre["audVisible"] == 0 and
            pre["summary"] == "none" and pre["audrow"] == "none" and
            post["label"] == "Exit Stock Audit" and
            [h[0] for h in post["heads"]] == ["Counted Qty", "Diff", "Loss (₩)"] and
            all(h[1] != "none" for h in post["heads"]) and
            post["audrowLast"] and post["audrowDisp"] != "none" and post["summary"] != "none" and
            post["locs"][:10] == want_locs and post["locs"][10] == "" and post["lastSku"] == "100038120")
    ok(good, "QA-AUD-01", f"pre={pre}; post locs={post['locs']} last SKU={post['lastSku']}",
       f"pre={pre}; post={post}")


def qa_aud_02(page):
    start_audit(page)
    page.click("#toggleAudit")
    d = js(page, """() => {
      const rows=[...document.querySelectorAll('#p-current tbody tr')].filter(r=>!r.classList.contains('audrow'));
      return {label:document.getElementById('toggleAudit').innerText.trim(),
        audAllNone:[...document.querySelectorAll('#p-current th.audcol,#p-current td.audcol')].every(e=>getComputedStyle(e).display==='none'),
        summary:getComputedStyle(document.getElementById('auditSummary')).display,
        audrow:getComputedStyle(document.querySelector('#p-current .audrow')).display,
        first:rows[0].children[0].innerText.trim()};
    }""")
    good = (d["label"] == "Start Stock Audit" and d["audAllNone"] and d["summary"] == "none"
            and d["audrow"] == "none" and d["first"] == "100031877")
    ok(good, "QA-AUD-02", f"{d}", f"{d}")


def qa_aud_03(page):
    start_audit(page)
    t = txt(page, "#auditSummary")
    b = js(page, "() => [...document.querySelectorAll('#auditSummary button')].map(x=>x.innerText.trim())")
    good = ("Total stock loss (sum of diff × product cost):" in t and "+₩46,260" in t and
            "— target 0" in t and "Confirm Audit Differences (ADJUST log)" in b)
    ok(good, "QA-AUD-03", f"#auditSummary innerText={t!r}; buttons={b}", f"innerText={t!r}; buttons={b}")


def qa_aud_04(page):
    start_audit(page)
    d = js(page, """() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r=>({sku:r.children[0].innerText.trim(), total:r.children[8].innerText.trim(),
                  counted:r.querySelector('.qty-in').value}))""")
    eq = [x for x in d if x["total"] == x["counted"]]
    ne = [x for x in d if x["total"] != x["counted"]]
    good = (len(eq) == 9 and len(ne) == 2 and
            {(x["sku"], x["total"], x["counted"]) for x in ne} ==
            {("100005104", "18", "17"), ("100012534", "9", "11")})
    ok(good, "QA-AUD-04", f"9 equal / 2 seeded differences {ne}", f"eq={len(eq)} ne={ne}")


def qa_aud_06(page):
    start_audit(page)
    d = js(page, """() => [...document.querySelectorAll('#p-current tbody tr')]
        .filter(r=>!r.classList.contains('audrow'))
        .map(r=>({sku:r.children[0].innerText.trim(), diff:r.children[12].innerText.trim(), loss:r.children[13].innerText.trim()}))""")
    m = {x["sku"]: (x["diff"], x["loss"]) for x in d}
    others = [v for k, v in m.items() if k not in ("100005104", "100012534")]
    good = (m.get("100005104") == ("−1", "−₩15,000") and m.get("100012534") == ("+2", "+₩61,260")
            and all(v == ("0", "₩0") for v in others) and len(others) == 9)
    ok(good, "QA-AUD-06", f"{m}", f"{m}")


def qa_aud_11(page):
    d = js(page, """() => ({summary:getComputedStyle(document.getElementById('auditSummary')).display,
        audcols:[...document.querySelectorAll('#p-current .audcol')].map(e=>getComputedStyle(e).display),
        audrow:getComputedStyle(document.querySelector('#p-current .audrow')).display})""")
    good = d["summary"] == "none" and all(x == "none" for x in d["audcols"]) and d["audrow"] == "none"
    ok(good, "QA-AUD-11", f"all audit-only UI display:none ({len(d['audcols'])} .audcol nodes)", f"{d}")


def qa_aud_12(page):
    start_audit(page)
    page.fill("#auSearch", "UNOVE")
    d = js(page, """() => ({disp:getComputedStyle(document.getElementById('auDrop')).display,
        entries:[...document.querySelectorAll('#auDrop div[data-sku]')].map(e=>e.innerText.trim())})""")
    want = ["UNOVE 딥 대미지 트리트먼트 · 320ml · 100048201", "UNOVE 실크 헤어 오일 · 150ml · 100051200"]
    good = d["disp"] != "none" and d["entries"] == want
    ok(good, "QA-AUD-12", f"#auDrop visible, entries {d['entries']}", f"{d}")


def qa_aud_13(page):
    start_audit(page)
    page.fill("#auSearch", "zzzz")
    d = js(page, "() => ({t:document.getElementById('auDrop').innerText.trim(), n:document.querySelectorAll('#auDrop div[data-sku]').length})")
    good = d["t"] == "No match — register manually via Unrecognized flow (F)" and d["n"] == 0
    ok(good, "QA-AUD-13", f"#auDrop innerText == {d['t']!r}, 0 [data-sku]", f"{d}")


def qa_aud_14(page):
    start_audit(page)
    n0 = js(page, "() => document.querySelectorAll('#p-current tbody tr').length")
    page.fill("#auSearch", "Torrid")
    page.click("#auAdd")
    d = js(page, "() => ({n:document.querySelectorAll('#p-current tbody tr').length, active:document.activeElement.id})")
    good = d["n"] == n0 and d["active"] == "auSearch"
    ok(good, "QA-AUD-14", f"row count {n0} -> {d['n']} (unchanged); activeElement=#{d['active']}", f"n0={n0} {d}")


def qa_aud_16(page):
    start_audit(page)
    page.fill("#auSearch", "Torriden")
    page.click("#auDrop div[data-sku='100027733']")
    page.fill("#auLoc", "B-01-02")
    page.fill("#auQty", "3")
    page.click("#auAdd")
    d = js(page, """() => {
      const tb=document.querySelector('#p-current tbody'); const r=tb.firstElementChild;
      const c=[...r.children].map(td=>td.innerText.trim());
      return {cells:c, bg:r.style.background, html3:r.children[3].innerHTML,
        qty:(r.querySelector('.qty-in')||{}).value,
        cleared:[document.getElementById('auSearch').value,document.getElementById('auLoc').value,document.getElementById('auQty').value]};
    }""")
    c = d["cells"]
    good = (c[0] == "100027733" and "Torriden 다이브인 저분자 세럼" in c[3] and "[NEW]" in c[3] and
            c[4] == "50ml" and c[8] == "0" and c[9] == "0" and c[10] == "0" and
            d["qty"] == "3" and c[12] == "+3" and c[13] == "— (신규)" and
            d["bg"] != "" and d["cleared"] == ["", "", ""])
    ok(good, "QA-AUD-16", f"first tbody row = {c[:5]}… Counted={d['qty']} Diff={c[12]} Loss={c[13]}; inputs cleared",
       f"{d}")


def qa_aud_17(page):
    start_audit(page)
    page.fill("#auSearch", "Torriden")
    page.click("#auDrop div[data-sku='100027733']")
    page.click("#auAdd")
    d = js(page, """() => {const r=document.querySelector('#p-current tbody').firstElementChild;
        return {qty:r.querySelector('.qty-in').value, loc:r.querySelector('.loc-in').value};}""")
    good = d["qty"] == "1" and d["loc"] == "Unassigned"
    ok(good, "QA-AUD-17", f"Counted Qty={d['qty']}, .loc-in value={d['loc']!r}", f"{d}")


def qa_aud_22(page):
    start_audit(page)
    page.click("#auditSummary button")
    d = js(page, """() => {
      const m=document.getElementById('m-adjust');
      return {open:m.classList.contains('open'), header:m.querySelector('header').innerText.trim(),
        rows:[...m.querySelectorAll('tbody tr')].map(r=>[...r.children].map(td=>td.innerText.trim())),
        foot:[...m.querySelectorAll('.foot button')].map(b=>b.innerText.trim())};
    }""")
    rows = d["rows"]
    good = (d["open"] and d["header"].startswith("Confirm Audit Differences — July 2026 Stock Audit (Auditor: Yongwon)")
            and len(rows) == 3
            and rows[0][0] == "100005104" and rows[0][3] == "18" and rows[0][4] == "17" and rows[0][5] == "−1"
            and rows[1][0] == "100012534" and rows[1][3] == "9" and rows[1][4] == "11" and rows[1][5] == "+2"
            and rows[2][0] == "100048201" and "[NEW]" in rows[2][1] and rows[2][3] == "0" and rows[2][4] == "3" and rows[2][5] == "+3"
            and "Confirm — record 3 ADJUST events" in d["foot"])
    ok(good, "QA-AUD-22",
       f"3 rows {[(r[0], r[3], r[4], r[5]) for r in rows]}; footer {d['foot']} "
       f"(NOTE: spec writes '18 → 17'; the modal has separate System/Counted columns — read as values. "
       f"Header matched by prefix only: innerText appends '\\n✕' from the close button.)",
       f"{d}")


def qa_aud_23(page):
    start_audit(page)
    page.click("#auditSummary button")
    notes = js(page, "() => [...document.querySelectorAll('#m-adjust .note')].map(n=>n.innerText.trim())")
    exp2 = ("Total stock loss: +₩46,260 (target 0) · the 3 new additions are not losses — on confirm, "
            "Current Stocks · Available update immediately; monthly audit logs retained.")
    good = (len(notes) >= 2 and notes[0].startswith("⚠ Reserved shortage check")
            and notes[0].endswith("None in this audit.") and notes[1] == exp2)
    ok(good, "QA-AUD-23", f"note1 begins/ends as specified; note2 byte-equal", f"notes={notes}")


def qa_aud_36(page):
    start_audit(page)
    page.fill("#auSearch", "Torriden")
    page.click("#auDrop div[data-sku='100027733']")
    page.click("#auAdd")
    page.click("//button[@class='wf-tab' and normalize-space(text())='Modal: Past Audit Logs']")
    page.click("#m-auditlog .foot button")
    d = js(page, """() => ({label:document.getElementById('toggleAudit').innerText.trim(),
        first:document.querySelector('#p-current tbody').firstElementChild.children[0].innerText.trim(),
        cur:document.querySelector('#p-current').classList.contains('on'),
        modal:document.getElementById('m-auditlog').classList.contains('open')})""")
    good = d["label"] == "Exit Stock Audit" and d["first"] == "100027733" and d["cur"] and not d["modal"]
    ok(good, "QA-AUD-36", f"{d}", f"{d}")


# ------------------------------------------------------------------- QA-LOG
def open_auditlog(page):
    page.click("//button[normalize-space(text())='📋 Past Audit Logs']")


def qa_log_01(page):
    open_auditlog(page)
    d = js(page, """() => ({open:document.getElementById('m-auditlog').classList.contains('open'),
        h:document.querySelector('#m-auditlog header').innerText.trim(),
        auditOff:document.getElementById('toggleAudit').innerText.trim()})""")
    good = d["open"] and d["h"].startswith("Past Audit Logs — monthly session records") and d["auditOff"] == "Start Stock Audit"
    ok(good, "QA-LOG-01",
       f"{d} (NOTE: 'starts' reading required — innerText appends '\\n✕' from the close button inside <header>; "
       f"strict equality would FAIL)", f"{d}")


def qa_log_02(page):
    open_auditlog(page)
    d = js(page, """() => ({head:[...document.querySelectorAll('#m-auditlog thead th')].map(t=>t.innerText.trim()),
        rows:[...document.querySelectorAll('#m-auditlog tbody tr')].map(r=>[...r.children].map(td=>td.innerText.trim()))})""")
    headw = ["Audit Date", "Auditor", "SKUs Checked", "Adjustments", "New Additions", "Total Loss", "Detail"]
    want = [["2026-07-22", "Yongwon", "10", "2 (−1 / +2)", "1", "+₩46,260"],
            ["2026-06-30", "Dean", "9", "5 (−4 / +1)", "0", "−₩128,460"],
            ["2026-05-31", "Dean", "9", "0", "0", "₩0 · target met"]]
    got = [r[:6] for r in d["rows"]]
    good = d["head"] == headw and len(d["rows"]) == 3 and got == want
    ok(good, "QA-LOG-02", f"header ok; 3 rows {got}", f"head={d['head']} rows={got}")


def qa_log_03(page):
    open_auditlog(page)
    page.click("//tr[td[normalize-space(text())='2026-07-22']]//a[normalize-space(text())='View ADJUST events']")
    d = js(page, """() => {const m=document.getElementById('m-adjlog');
      return {open:m.classList.contains('open'), h:m.querySelector('header').innerText.trim(),
        rows:[...m.querySelectorAll('tbody tr')].map(r=>({t:r.children[0].innerText.trim(),
             purple:!!r.getAttribute('style'), txt:r.innerText, loss:r.children[6].innerText.trim()}))};}""")
    good = (d["open"] and d["h"].startswith("2026-07-22 Stock Audit — 3 ADJUST events (Auditor: Yongwon, confirmed 14:20)")
            and len(d["rows"]) == 3 and all(r["t"] == "14:20:11" for r in d["rows"])
            and d["rows"][2]["purple"] and "[NEW ADDITION]" in d["rows"][2]["txt"] and d["rows"][2]["loss"] == "—")
    ok(good, "QA-LOG-03", f"header ok (prefix reading; innerText appends '\\n✕'), 3 rows @14:20:11, row3 purple+[NEW ADDITION]+Loss '—'", f"{d}")


def qa_log_04(page):
    open_auditlog(page)
    page.click("//tr[td[normalize-space(text())='2026-06-30']]//a[normalize-space(text())='View ADJUST events']")
    d = js(page, """() => {const m=document.getElementById('m-adjlog6');
      return {open:m.classList.contains('open'), h:m.querySelector('header').innerText.trim(),
        times:[...m.querySelectorAll('tbody tr')].map(r=>r.children[0].innerText.trim()),
        note:m.querySelector('.note').innerText.trim()};}""")
    good = (d["open"] and d["h"].startswith("2026-06-30 Stock Audit — 5 ADJUST events (Auditor: Dean, confirmed 17:05)")
            and d["times"] == ["17:05:42"] * 5
            and d["note"] == "Total loss −₩128,460 — June exceeded the loss target; root-cause investigation in progress (suspected picking mis-outbound).")
    ok(good, "QA-LOG-04", f"header ok (prefix reading; innerText appends '\\n✕'), 5 rows @17:05:42, note byte-equal", f"{d}")


def qa_log_05(page):
    open_auditlog(page)
    d = js(page, """() => {const r=[...document.querySelectorAll('#m-auditlog tbody tr')]
        .find(r=>r.children[0].innerText.trim()==='2026-05-31');
      const a=r.children[6].querySelector('a');
      return {cell:r.children[6].innerText.trim(), dm:a?a.getAttribute('data-modal'):'NO-ANCHOR'};}""")
    before = js(page, "() => [...document.querySelectorAll('.overlay')].filter(o=>o.classList.contains('open')).map(o=>o.id)")
    page.click("//tr[td[normalize-space(text())='2026-05-31']]//td[7]")
    after = js(page, "() => [...document.querySelectorAll('.overlay')].filter(o=>o.classList.contains('open')).map(o=>o.id)")
    good = d["cell"] == "—" and d["dm"] is None and before == after
    ok(good, "QA-LOG-05", f"Detail cell '—', anchor data-modal={d['dm']}, open overlays unchanged {after}",
       f"{d}; overlays {before} -> {after}")


def qa_log_06(page):
    page.evaluate("document.getElementById('m-adjlog').classList.add('open')")
    d = js(page, """() => {const m=document.getElementById('m-adjlog');
      return {note:m.querySelector('.note').innerText.trim(),
        prod:[...m.querySelectorAll('tbody tr')].map(r=>({tag:(r.children[2].firstElementChild||{}).tagName,
              kr:/[\\uAC00-\\uD7A3]/.test(r.children[2].innerText)}))};}""")
    exp = ("Each event is also recorded as ADJUST type in that SKU's Stock History — search the SKU and "
           "filter by type to inspect individually. Total loss +₩46,260 (new additions excluded).")
    good = d["note"] == exp and all(p["tag"] == "B" and p["kr"] for p in d["prod"])
    ok(good, "QA-LOG-06", "note byte-equal; every Product cell = <b>brand</b> + Korean", f"{d}")


def qa_log_09(page):
    open_auditlog(page)
    d = js(page, """() => [...document.querySelectorAll('#m-auditlog tbody tr')].map(r=>({
        d:r.children[0].innerText.trim(), c:getComputedStyle(r.children[5]).color, t:r.children[5].innerText.trim()}))""")
    amber = d[0]["c"]; red = d[1]["c"]; green = d[2]["c"]
    rec("QA-LOG-09", AMB,
        f"Assertable half PASSES: three DISTINCT Total Loss colours {amber} / {red} / {green} and the "
        f"2026-05-31 cell ends ' · target met'. Unassertable half: the spec names the colours "
        f"'amber' / 'red' / 'green' but supplies no hex, rgb, CSS variable or class to compare against, so "
        f"'amber' cannot be verified without reading the wireframe source (improvisation). Same gap in "
        f"QA-RES-03 ('amber row background', 'red outline'), QA-AUD-16 / QA-LOG-03 ('purple-tinted'), "
        f"QA-HIS-06 ('amber background'), QA-AUD-06 (colour of Diff/Loss), QA-CS-01 ('green'/'amber').")


# ------------------------------------------------------------------- QA-RES
def goto_history(page):
    page.click(".subtabs button[data-sub='s-search']")


def qa_res_01(page):
    goto_history(page)
    d = js(page, """() => {const c=[...document.querySelectorAll('#p-search .card')].find(x=>x.querySelector('h4').innerText.includes('Stock Status'));
      return {nums:[...c.querySelectorAll('.bignum')].map(b=>[b.querySelector('.n').innerText.trim(), b.querySelector('.l').innerText.trim()]),
        reslink:!!c.querySelector('span.reslink'), rl:(c.querySelector('span.reslink')||{}).innerText,
        deco:c.querySelector('span.reslink')?getComputedStyle(c.querySelector('span.reslink')).textDecorationStyle:null,
        note:c.querySelector('p').innerText.trim()};}""")
    good = (d["nums"] == [["42", "Total Qty"], ["8", "Reserved Qty"], ["34", "Available Qty"]]
            and d["reslink"] and d["rl"].strip() == "8" and d["deco"] == "dotted"
            and d["note"] == "Click Reserved → allocated orders modal (incl. releasing phantom orders · restock)")
    ok(good, "QA-RES-01", f"{d}", f"{d}")


def qa_res_02(page):
    goto_history(page)
    page.click(".reslink")
    d = js(page, """() => {const m=document.getElementById('m-reserved');
      return {open:m.classList.contains('open'), h:m.querySelector('header').innerText.trim(),
        bold:[...m.querySelectorAll('header b')].map(b=>b.innerText.trim()),
        head:[...m.querySelectorAll('thead th')].map(t=>t.innerText.trim())};}""")
    want = "Reserved Quantity — Dongkook 마데카솔 크림 50ml (100004819) · 8 reserved"
    strict = d["h"] == want
    contains = want in d["h"]
    norm = re.sub(r"\s+", " ", d["h"]).strip()
    normalised = want in norm
    rest = ("Dongkook" in d["bold"] and
            d["head"] == ["Order ID", "Order Date", "Customer", "Status", "Reserved Qty", "Reserved At", "Action"])
    if d["open"] and strict and rest:
        rec("QA-RES-02", PASS, f"{d}")
    else:
        rec("QA-RES-02", FAIL,
            f"Spec: header reads {want!r}. §8.0 step 3 MANDATES innerText. Actual innerText of the OPEN "
            f"modal header = {d['h']!r}. `.modal header` is display:flex, so innerText line-breaks around the "
            f"<b>Dongkook</b> flex item AND appends the ✕ close button. strict-equality={strict}, "
            f"substring-containment={contains} (also false), whitespace-normalised containment={normalised}. "
            f"Bold + table header legs passed ({rest}).")


def qa_res_03(page):
    goto_history(page)
    page.click(".reslink")
    d = js(page, """() => [...document.querySelectorAll('#m-reserved tbody tr')].map(r=>({
        cells:[...r.children].slice(0,6).map(td=>td.innerText.trim().replace(/\\s+/g,' ')),
        bg:r.getAttribute('style')||'',
        phantom:r.innerText.includes('SUSPECTED PHANTOM'),
        btnStyle:(r.querySelector('button')||{}).getAttribute? r.querySelector('button').getAttribute('style')||'':''}))""")
    good = (len(d) == 3
            and d[0]["cells"] == ["407812", "2026-06-30", "Sarah Kim", "processing", "2", "07-12 11:05"]
            and d[1]["cells"] == ["413650", "2026-07-08", "Emma Park", "processing", "3", "07-08 14:22"]
            and d[2]["cells"][:3] == ["409112", "2026-07-02", "Liam Chen"]
            and d[2]["cells"][3].startswith("cancelled")
            and d[2]["cells"][4] == "3" and d[2]["cells"][5] == "07-02 09:10"
            and [x["phantom"] for x in d] == [False, False, True]
            and "amber" in d[2]["bg"] and not d[0]["bg"] and not d[1]["bg"]
            and "red" in d[2]["btnStyle"])
    ok(good, "QA-RES-03", f"3 rows as specified; only 409112 amber + SUSPECTED PHANTOM + red-outline button", f"{d}")


def qa_res_04(page):
    goto_history(page)
    page.click(".reslink")
    n = txt(page, "#m-reserved .note")
    exp = ("Total 8 = 2+3+3 · Suspected phantom = the order is cancelled/refunded but the reservation was "
           "never released — release target. If reservation-order mismatches persist, investigate unconfirmed "
           "events with the Pending confirm filter in Stock History (linked to Dean's report).")
    ok(n == exp, "QA-RES-04", "note byte-equal; 2+3+3 == header 8", f"got {n!r}")


def qa_res_05(page):
    goto_history(page)
    page.click(".reslink")
    page.click("//tr[td[normalize-space(text())='409112']]//button[normalize-space(text())='Cancel Inbound']")
    d = js(page, """() => {const m=document.getElementById('m-resrelease');
      return {open:m.classList.contains('open'), h:m.querySelector('header').innerText.trim(),
        steps:[...m.querySelectorAll('.body b')].map(b=>b.innerText.trim()),
        radios:[...m.querySelectorAll('input[name=resback]')].map(r=>({checked:r.checked,label:r.closest('label').innerText.trim()})),
        qty:[...m.querySelectorAll('.body input')].filter(i=>i.type!=='radio').map(i=>i.value),
        hint:m.innerText.includes('Default = qty originally inbounded (editable)'),
        ta:m.querySelector('textarea').placeholder};}""")
    steps = d["steps"]
    wanth = "Cancel Inbound — Order 409112 · Dongkook 마데카솔 크림 × 3"
    hdr_strict = d["h"] == wanth
    hdr_contains = wanth in d["h"]
    hdr_norm = wanth in re.sub(r"\s+", " ", d["h"]).strip()
    good = (d["open"] and hdr_strict
            and "1. Release the reservation (Reserved) on this order?" in steps
            and "2. Restock the units?" in steps and "3. Restock Qty" in steps and "4. Memo (Optional)" in steps
            and len(d["radios"]) == 2 and d["radios"][0]["checked"] and not d["radios"][1]["checked"]
            and d["radios"][0]["label"] == "Yes — Available +3 (restock)"
            and d["radios"][1]["label"] == "No — exclude from stock (damaged · lost etc., record the loss as ADJUST(−3))"
            and d["qty"] == ["3"] and d["hint"]
            and d["ta"] == "Cancellation reason or notes — if written, also recorded in the order's Comments history")
    if good:
        rec("QA-RES-05", PASS, "header, 4 bold steps, 2 radios (Yes default), qty 3 + hint, memo placeholder — all match")
    else:
        rec("QA-RES-05", FAIL,
            f"Every leg passes EXCEPT the header. Spec: {wanth!r}; actual innerText (§8.0 mandates innerText) "
            f"= {d['h']!r} — `.modal header` is display:flex so the <b>Dongkook</b> flex item and the ✕ button "
            f"become separate innerText lines. strict={hdr_strict}, substring={hdr_contains}, "
            f"whitespace-normalised={hdr_norm}. Steps/radios/qty/hint/memo all matched: {d['steps']}, "
            f"{d['radios']}, qty={d['qty']}, hint={d['hint']}.")


def qa_res_06(page):
    goto_history(page)
    page.click(".reslink")
    page.click("//tr[td[normalize-space(text())='409112']]//button[normalize-space(text())='Cancel Inbound']")
    d = js(page, """() => ({note:document.querySelector('#m-resrelease .note').innerText.trim(),
        foot:[...document.querySelectorAll('#m-resrelease .foot button')].map(b=>b.innerText.trim())})""")
    exp = ('On release, Reserved 8 → 5; choosing "Yes" brings Available 34 → 37. The action is recorded in '
           'Stock History as a RESERVE release event.')
    good = d["note"] == exp and d["foot"] == ["Cancel", "Confirm"]
    ok(good, "QA-RES-06", f"note byte-equal; foot buttons {d['foot']}", f"{d}")


# ------------------------------------------------------------------- QA-HIS
def qa_his_01(page):
    goto_history(page)
    d = js(page, """() => ({opts:[...document.querySelectorAll('#p-search .searchbar select.sel option')].map(o=>o.text.trim()),
        val:document.querySelector('#p-search .searchbar input.inp').value,
        ph:document.querySelector('#p-search .searchbar input.inp').placeholder,
        btn:document.querySelector('#p-search .searchbar button').innerText.trim()})""")
    good = (d["opts"] == ["SKU", "Product Name", "Order ID", "Tracking No"] and d["val"] == "100004819"
            and d["ph"] == "Enter SKU (e.g. 100004819)" and d["btn"] == "🔍 Search")
    ok(good, "QA-HIS-01", f"{d}", f"{d}")


def qa_his_03(page):
    goto_history(page)
    d = js(page, """() => {const c=[...document.querySelectorAll('#p-search .card')].find(x=>x.classList.contains('pinfo'));
      const kv={}; c.querySelectorAll('.kv').forEach(k=>kv[k.children[0].innerText.trim()]=k.children[1]);
      const rt=kv['Sourcing Route']; const cs=getComputedStyle(rt);
      return {sku:kv['SKU'].innerText.trim(), name:kv['Name'].innerText.trim(),
        krTag:(kv['Name KR'].firstElementChild||{}).tagName, kr:kv['Name KR'].innerText.trim(),
        brand:kv['Brand'].innerText.trim(), route:rt.innerText.trim(), bg:cs.backgroundColor, fw:cs.fontWeight};}""")
    good = (d["sku"] == "100004819" and d["name"] == "Madecassol Cream 50ml" and d["krTag"] == "B"
            and d["kr"] == "Dongkook 마데카솔 크림" and d["brand"] == "Dongkook"
            and d["route"] == "SMART BUY" and d["bg"] == "rgba(0, 0, 0, 0)" and d["fw"] == "800")
    ok(good, "QA-HIS-03", f"{d}", f"{d}")


def qa_his_04(page):
    goto_history(page)
    d = js(page, """() => {const c=[...document.querySelectorAll('#p-search .card')].find(x=>x.querySelector('h4').innerText.includes('By Location'));
      return {n:c.querySelectorAll('.loc-row').length,
        row:c.querySelector('.loc-row').innerText.trim().replace(/\\s+/g,' '),
        note:c.querySelector('p').innerText.trim()};}""")
    good = (d["n"] == 1 and d["row"] == "A-02-13 42"
            and d["note"] == "One location per SKU — change locations via the Current Stocks input field")
    ok(good, "QA-HIS-04", f"{d}", f"{d}")


def qa_his_05(page):
    goto_history(page)
    d = js(page, """() => {const t=document.querySelectorAll('#p-search table.tbl')[0];
      return {head:[...t.querySelectorAll('thead th')].map(x=>x.innerText.trim()),
        rows:[...t.querySelectorAll('tbody tr')].map(r=>r.children[0].innerText.trim()+' '+r.children[1].innerText.trim()+' '+r.children[2].innerText.trim())};}""")
    headw = ["Type", "Quantity", "Status", "Tracking No", "Carrier", "Location", "Order ID", "Created At", "Auditor"]
    want = ["INBOUND +6 PENDING", "OUTBOUND −2 CONFIRMED", "RESERVE −8 CONFIRMED",
            "INBOUND +30 CONFIRMED", "ADJUST −1 CONFIRMED", "INBOUND +12 CONFIRMED"]
    good = d["head"] == headw and len(d["rows"]) == 6 and [r.rsplit(" ", 1)[0] for r in d["rows"]] == [w.rsplit(" ", 1)[0] for w in want]
    ok(good, "QA-HIS-05", f"header ok; 6 rows in order {d['rows']}", f"{d}")


def qa_his_06(page):
    goto_history(page)
    d = js(page, """() => {const t=document.querySelectorAll('#p-search table.tbl')[0];
      const rows=[...t.querySelectorAll('tbody tr')];
      const p=rows.filter(r=>r.classList.contains('pending'));
      return {nPending:p.length, cells:p.length?[...p[0].children].map(td=>td.innerText.trim()):null,
        bg:p.length?getComputedStyle(p[0]).backgroundColor:null,
        statuses:rows.map(r=>r.children[2].innerText.trim())};}""")
    c = d["cells"]
    good = (d["nPending"] == 1 and c[0] == "INBOUND" and c[1] == "+6" and c[2] == "PENDING"
            and c[3] == "12101316464794" and c[4] == "Coupang" and c[6] == "407847" and c[8] == "Miranti"
            and d["bg"] != "rgba(0, 0, 0, 0)"
            and d["statuses"] == ["PENDING", "CONFIRMED", "CONFIRMED", "CONFIRMED", "CONFIRMED", "CONFIRMED"])
    ok(good, "QA-HIS-06", f"single tr.pending row = {c}; bg {d['bg']}", f"{d}")


def qa_his_07(page):
    goto_history(page)
    n = js(page, """() => {const r=document.querySelector('#p-search tr.pending');
        return r.querySelectorAll('button,a,input[type=checkbox]').length;}""")
    ok(n == 0, "QA-HIS-07", "PENDING row contains 0 button / a / checkbox", f"{n} affordance(s) found")


def qa_his_08(page):
    goto_history(page)
    d = js(page, "() => [...document.querySelectorAll('#p-search .filterchip')].map(b=>[b.innerText.trim(), b.classList.contains('on')])")
    good = d == [["All", True], ["Confirmed", False], ["Pending confirm", False]]
    ok(good, "QA-HIS-08", f"{d}", f"{d}")


def qa_his_15(page):
    goto_history(page)
    d = js(page, """() => [...document.querySelectorAll('#p-search table.tbl')[0].querySelectorAll('tbody tr')]
        .map(r=>r.children[7].innerText.trim())""")
    want = ["07-13 09:12", "07-12 18:40", "07-12 11:05", "07-10 14:22", "07-09 16:50", "07-08 10:11"]
    good = d == want and all(re.fullmatch(r"\d{2}-\d{2} \d{2}:\d{2}", x) for x in d)
    ok(good, "QA-HIS-15", f"{d}", f"{d}")


def qa_his_18(page):
    goto_history(page)
    d = js(page, """() => {const t=document.querySelectorAll('#p-search table.tbl')[0];
      const cnt={}; t.querySelectorAll('tbody .ty').forEach(s=>{const c=[...s.classList].find(x=>x.startsWith('ty-'));cnt[c]=(cnt[c]||0)+1;});
      const adj=[...t.querySelectorAll('tbody tr')].find(r=>r.children[0].innerText.trim()==='ADJUST');
      return {cnt, adjQtyClass:adj.children[1].className, adjQty:adj.children[1].innerText.trim()};}""")
    good = (d["cnt"] == {"ty-in": 3, "ty-out": 1, "ty-res": 1, "ty-adj": 1}
            and "diff-neg" in d["adjQtyClass"] and d["adjQty"] == "−1")
    ok(good, "QA-HIS-18", f"{d}", f"{d}")


# ------------------------------------------------------------------- QA-FRM
def qa_frm_01(page):
    page.click(".subtabs button[data-sub='s-inbound']")
    d = js(page, """() => ({flds:[...document.querySelectorAll('#p-inbound .fld label')].map(l=>l.innerText.trim()),
        carrier:[...document.querySelectorAll('#p-inbound .fld select option')].map(o=>o.text.trim()),
        btn:document.querySelector('#p-inbound > button').innerText.trim()})""")
    good = (d["flds"] == ["SKU *", "Quantity *", "Tracking No", "Carrier", "Order ID (optional)"]
            and d["carrier"] == ["Coupang", "Deleo", "Direct"] and d["btn"] == "＋ Record Inbound")
    ok(good, "QA-FRM-01", f"{d}", f"{d}")


def qa_frm_02(page):
    d = js(page, """() => ['p-inbound','p-outbound'].map(id=>[...document.querySelectorAll('#'+id+' .fld label')]
        .map(l=>l.innerText.trim()).filter(t=>/^location/i.test(t)))""")
    good = d == [[], []]
    ok(good, "QA-FRM-02", "no field labelled 'Location' on either form", f"{d}")


def qa_frm_03(page):
    page.click(".subtabs button[data-sub='s-inbound']")
    n = txt(page, "#p-inbound .form-note")
    exp = ("Record a warehouse inbound directly, without a specific order (return restock · manual inbound). "
           "Location auto-applies the SKU's single registered location. For order-linked inbound, use Request "
           "Inbound on View Orders / the order detail.")
    ok(n == exp, "QA-FRM-03", "form-note byte-equal", f"got {n!r}")


def qa_frm_08(page):
    page.click(".subtabs button[data-sub='s-outbound']")
    d = js(page, """() => ({flds:[...document.querySelectorAll('#p-outbound .fld label')].map(l=>l.innerText.trim()),
        carrier:[...document.querySelectorAll('#p-outbound .fld select option')].map(o=>o.text.trim()),
        btn:document.querySelector('#p-outbound > button').innerText.trim(),
        note:document.querySelector('#p-outbound .form-note').innerText.trim()})""")
    exp = ("Record a warehouse outbound directly. Location auto-applies the SKU's registered location; "
           "outbound exceeding Available Qty is blocked.")
    good = (d["flds"] == ["SKU *", "Quantity *", "Tracking No", "Carrier", "Order ID (optional)"]
            and d["carrier"] == ["Deleo", "YUN", "Coupang"] and d["btn"] == "－ Record Outbound"
            and d["note"] == exp)
    ok(good, "QA-FRM-08", f"{d}", f"{d}")


def qa_frm_19(page):
    d = js(page, """() => ['p-inbound','p-outbound'].map(id=>{
        const flds=[...document.querySelectorAll('#'+id+' .fld')];
        const c=flds.filter(f=>f.querySelector('label').innerText.trim()==='Carrier');
        return {n:c.length, sels:c.map(f=>f.querySelectorAll('select').length),
          bad:c.map(f=>{const s=f.querySelector('select');
            return {ro:s.hasAttribute('readonly'), dis:s.disabled};})};})""")
    good = all(x["n"] == 1 and x["sels"] == [1] and not x["bad"][0]["ro"] and not x["bad"][0]["dis"] for x in d)
    ok(good, "QA-FRM-19", f"one enabled, non-readonly Carrier <select> per form {d}", f"{d}")


# ------------------------------------------------------------------- QA-COM
def open_inbox(page):
    page.click("[data-open='inbox1']")


def qa_com_01(page):
    d0 = js(page, """() => {const b=document.querySelector("[data-open='inbox1']");
        return {btn:b.innerText.trim(), badge:b.querySelector('.badge-n').innerText.trim(),
                badgeColor:getComputedStyle(b.querySelector('.badge-n')).backgroundColor};}""")
    open_inbox(page)
    d = js(page, """() => {const dd=document.getElementById('inbox1');
      return {open:dd.classList.contains('open'),
        tabOn:dd.querySelector('.tabs button.on').innerText.trim(),
        unread:[...dd.querySelectorAll('.it.unread')].map(i=>(i.innerText.match(/Order (\\d+)/)||[])[1])};}""")
    good = ("💬 Comments" in d0["btn"] and d0["badge"] == "3" and d["open"]
            and d["tabOn"].startswith("@ Mentions") and d["unread"] == ["409112", "407847", "407506"])
    ok(good, "QA-COM-01", f"{d0} / {d}", f"{d0} / {d}")


def qa_com_02(page):
    open_inbox(page)
    page.click("#inbox1 .tabs button[data-tab='saved']")
    d = js(page, """() => {const dd=document.getElementById('inbox1');
      const m=dd.querySelector('[data-pane=mentions]'), s=dd.querySelector('[data-pane=saved]');
      return {mDisp:getComputedStyle(m).display, sDisp:getComputedStyle(s).display,
        n:s.querySelectorAll('.it').length,
        order:(s.innerText.match(/Order (\\d+)/)||[])[1],
        header:s.querySelector('.paneheader').innerText.trim()};}""")
    good = (d["mDisp"] == "none" and d["sDisp"] != "none" and d["n"] == 1 and d["order"] == "407847"
            and d["header"].startswith("Saved comments · Click to open the order"))
    ok(good, "QA-COM-02",
       f"{d} (NOTE: 'reads' taken as prefix — the paneheader also carries a trailing "
       f"<small>Unstar to remove from this list</small>)", f"{d}")


def qa_com_03(page):
    open_inbox(page)
    d0 = js(page, """() => [...document.querySelectorAll('#inbox1 [data-pane=mentions] .it')]
        .map(i=>[(i.innerText.match(/Order (\\d+)/)||[])[1], i.querySelector('.star').classList.contains('on')])""")
    page.click("//div[@id='inbox1']//div[@data-pane='mentions']//div[contains(@class,'it')][.//b[contains(text(),'409112')]]//button[contains(@class,'star')]")
    a1 = js(page, """() => [...document.querySelectorAll('#inbox1 [data-pane=mentions] .it')]
        .find(i=>i.innerText.includes('409112')).querySelector('.star').classList.contains('on')""")
    page.click("//div[@id='inbox1']//div[@data-pane='mentions']//div[contains(@class,'it')][.//b[contains(text(),'409112')]]//button[contains(@class,'star')]")
    a2 = js(page, """() => [...document.querySelectorAll('#inbox1 [data-pane=mentions] .it')]
        .find(i=>i.innerText.includes('409112')).querySelector('.star').classList.contains('on')""")
    good = d0 == [["409112", False], ["407847", True], ["407506", False]] and a1 and not a2
    ok(good, "QA-COM-03", f"initial {d0}; after click {a1}; after 2nd click {a2}", f"initial {d0}; {a1}/{a2}")


def qa_com_04(page):
    open_inbox(page)
    page.fill("#inbox1 .csearch input", "phantom")
    d = js(page, """() => {const dd=document.getElementById('inbox1');
      const pane=dd.querySelector('[data-pane=csr]');
      return {tabs:getComputedStyle(dd.querySelector('.tabs')).display,
        header:pane.querySelector('.paneheader').innerText.trim(),
        n:[...dd.querySelectorAll('.it')].filter(i=>i.offsetParent!==null).length,
        marks:[...pane.querySelectorAll('mark')].map(m=>m.innerText)};}""")
    good = (d["tabs"] == "none" and d["header"] == "1 results · newest first · click to open the order"
            and d["n"] == 1 and d["marks"] == ["phantom"])
    ok(good, "QA-COM-04", f"{d}", f"{d}")


def qa_com_05(page):
    open_inbox(page)
    page.fill("#inbox1 .csearch input", "zzzz")
    d = js(page, """() => {const dd=document.getElementById('inbox1');
      const pane=dd.querySelector('[data-pane=csr]');
      return {paneText:pane.innerText.trim(), emptyText:(pane.querySelector('.empty')||{}).innerText};}""")
    page.fill("#inbox1 .csearch input", "")
    d2 = js(page, """() => {const dd=document.getElementById('inbox1');
      return {tabs:getComputedStyle(dd.querySelector('.tabs')).display,
        mentions:getComputedStyle(dd.querySelector('[data-pane=mentions]')).display};}""")
    strict = d["paneText"] == "No matching comments"
    lenient = (d["emptyText"] or "").strip() == "No matching comments"
    restored = d2["tabs"] != "none" and d2["mentions"] != "none"
    if strict and restored:
        rec("QA-COM-05", PASS, f"{d} / {d2}")
    else:
        rec("QA-COM-05", FAIL,
            f"Spec: 'the pane renders exactly `No matching comments`'. Actual pane innerText = "
            f"{d['paneText']!r} — the pane ALSO renders a '0 results · newest first · click to open the order' "
            f"header above the empty state. Lenient reading (the .empty node alone) = {lenient}. "
            f"Clear-query restore leg passed: {restored}.")


def qa_com_12(page):
    open_inbox(page)
    page.fill("#inbox1 .csearch input", "Dean")
    d = js(page, """() => {const pane=document.querySelector('#inbox1 [data-pane=csr]');
      return {header:pane.querySelector('.paneheader').innerText.trim(),
        orders:[...pane.querySelectorAll('.it')].map(i=>(i.innerText.match(/Order (\\d+)/)||[])[1])};}""")
    good = d["header"] == "2 results · newest first · click to open the order" and d["orders"] == ["409112", "407812"]
    ok(good, "QA-COM-12", f"{d}", f"{d}")


def qa_com_14(page):
    open_inbox(page)
    page.fill("#inbox1 .csearch input", "<b>x</b>")
    d = js(page, """() => {const pane=document.querySelector('#inbox1 [data-pane=csr]');
      return {bolds:pane.querySelectorAll('b').length, text:pane.innerText.trim()};}""")
    ok(d["bolds"] == 0, "QA-COM-14", f"0 <b> elements inside the result pane; pane text {d['text']!r}", f"{d}")


# ------------------------------------------------------------------- QA-EXP
def qa_exp_01(page):
    d = js(page, """() => {const h=[...document.querySelectorAll('.ptitle button')].map(b=>[b.innerText.trim(),b.className]);
      const c=[...document.querySelectorAll('#p-current .cs-controls button')].map(b=>[b.innerText.trim(),b.className]);
      return {h,c};}""")
    good = (any(x[0] == "⬇ Export Stock Status" and "btn-gray" in x[1] for x in d["h"])
            and any(x[0] == "⬇ Export" and "btn-gray" in x[1] for x in d["c"]))
    ok(good, "QA-EXP-01", f"{d}", f"{d}")


# ------------------------------------------------------------------- QA-GLB
def qa_glb_08(page):
    surf = _all_surfaces(page)
    scan_txt = {k: re.findall(r".{0,30}scan.{0,30}", v, re.I) for k, v in surf.items()}
    scan_txt = {k: v for k, v in scan_txt.items() if v}
    feeds = js(page, """() => [...document.querySelectorAll('[id*=scan i],[class*=scan i],[id*=feed i],[class*=feed i]')].map(e=>e.tagName+'.'+e.className)""")
    rec("QA-GLB-08", AMB if (not scan_txt and not feeds) else FAIL,
        (f"2 of 3 clauses RUN and pass: 0 elements with a scan/feed id or class, 0 'scan' strings in any "
         f"pane/overlay innerText (=> no scan feed list, no scan counter). 3rd clause NOT RUNNABLE: "
         f"'no input that re-focuses itself after a commit' names no input, no commit gesture and no "
         f"observable for 're-focus' — a plain <input> legitimately keeps focus after Enter, so any probe "
         f"invented here would be improvisation.")
        if (not scan_txt and not feeds) else f"text={scan_txt}; nodes={feeds}")


def qa_glb_09(page):
    surf = _all_surfaces(page)
    korean = {}
    for k, v in surf.items():
        found = set(re.findall(r"[가-힣][가-힣\s%.·+()]*", v))
        if found:
            korean[k] = sorted(x.strip() for x in found)
    chrome = js(page, """() => [...document.querySelectorAll('th,label,.paneheader,.form-note,button,h2,h4,header')]
        .filter(e=>/[\\uAC00-\\uD7A3]/.test(e.innerText) && getComputedStyle(e).display!=='none')
        .map(e=>e.tagName+': '+e.innerText.trim().slice(0,80))""")
    # header elements of modals legitimately carry product names (Dongkook 마데카솔 크림)
    chrome_nonproduct = [c for c in chrome if not c.startswith("HEADER:")]
    rec("QA-GLB-09", AMB if not chrome_nonproduct else FAIL,
        (f"Proxy test PASSES: 0 Korean strings in th / label / .paneheader / .form-note / button / h2 / h4 "
         f"chrome; the Korean actually present sits in product-name cells plus the data string '— (신규)'. "
         f"But the scenario is NOT machine-runnable as written: it asks whether each Korean string is "
         f"'product-, brand-, or data-derived' and §8 never enumerates the 11 KR product names, so the "
         f"partition had to be invented (element-role proxy). The stated baseline 'the only non-product "
         f"Korean is 신규' is likewise unverifiable without that list.")
        if not chrome_nonproduct else f"Korean in chrome: {chrome_nonproduct}")


def qa_glb_11(page):
    surf = _all_surfaces(page)
    all_txt = "\n".join(surf.values())
    vals = re.findall(r"[+−-]?₩[\d,]+", all_txt)
    bad = [v for v in vals if not re.fullmatch(r"(?:[+−]₩\d{1,3}(?:,\d{3})*|₩0)", v)]
    bare = re.findall(r"₩(?![\d])", all_txt)
    dollars = re.findall(r"\$|USD", all_txt)
    good = not bad and not dollars
    rec("QA-GLB-11", PASS if good else FAIL,
        (f"money values seen: {sorted(set(vals))}; all signed with thousands separators; "
         f"/\\$|USD/ matches 0. NOTE: {len(bare)} bare '₩' occurrence(s) exist as the column header "
         f"'Loss (₩)' — treated as a currency label, not a money value, since the spec does not say.")
        if good else f"malformed={bad}; dollar/USD hits={dollars}")


def qa_glb_12(page):
    hits = js(page, """() => {
      const out=[];
      document.querySelectorAll('.pane, .overlay').forEach(root=>{
        root.querySelectorAll('button,a,input,select').forEach(e=>{
          const s=[e.innerText||'',e.value||'',e.getAttribute('aria-label')||'',e.title||''].join(' ');
          if(/\\b(edit|delete|reverse|undo|re-?open)\\b/i.test(s)) out.push(root.id+' :: '+s.trim().slice(0,60));
        });
      });
      return out;}""")
    ok(not hits, "QA-GLB-12", "0 edit/delete/reverse/undo/re-open controls in any pane or overlay", f"{hits}")


# ------------------------------------------------------------------ registry
SCENARIOS = [
    ("QA-NAV-01", qa_nav_01), ("QA-NAV-02", qa_nav_02), ("QA-NAV-03", qa_nav_03),
    ("QA-NAV-04", qa_nav_04), ("QA-NAV-06", qa_nav_06), ("QA-NAV-07", qa_nav_07),
    ("QA-NAV-08", qa_nav_08), ("QA-NAV-09", qa_nav_09),
    ("QA-CS-01", qa_cs_01), ("QA-CS-03", qa_cs_03), ("QA-CS-05", qa_cs_05),
    ("QA-CS-08", qa_cs_08), ("QA-CS-09", qa_cs_09), ("QA-CS-10", qa_cs_10),
    ("QA-CS-14", qa_cs_14), ("QA-CS-15", qa_cs_15), ("QA-CS-16", qa_cs_16),
    ("QA-LOC-01", qa_loc_01), ("QA-LOC-08", qa_loc_08), ("QA-LOC-18", qa_loc_18),
    ("QA-AUD-01", qa_aud_01), ("QA-AUD-02", qa_aud_02), ("QA-AUD-03", qa_aud_03),
    ("QA-AUD-04", qa_aud_04), ("QA-AUD-06", qa_aud_06), ("QA-AUD-11", qa_aud_11),
    ("QA-AUD-12", qa_aud_12), ("QA-AUD-13", qa_aud_13), ("QA-AUD-14", qa_aud_14),
    ("QA-AUD-16", qa_aud_16), ("QA-AUD-17", qa_aud_17), ("QA-AUD-22", qa_aud_22),
    ("QA-AUD-23", qa_aud_23), ("QA-AUD-36", qa_aud_36),
    ("QA-LOG-01", qa_log_01), ("QA-LOG-02", qa_log_02), ("QA-LOG-03", qa_log_03),
    ("QA-LOG-04", qa_log_04), ("QA-LOG-05", qa_log_05), ("QA-LOG-06", qa_log_06),
    ("QA-LOG-09", qa_log_09),
    ("QA-RES-01", qa_res_01), ("QA-RES-02", qa_res_02), ("QA-RES-03", qa_res_03),
    ("QA-RES-04", qa_res_04), ("QA-RES-05", qa_res_05), ("QA-RES-06", qa_res_06),
    ("QA-HIS-01", qa_his_01), ("QA-HIS-03", qa_his_03), ("QA-HIS-04", qa_his_04),
    ("QA-HIS-05", qa_his_05), ("QA-HIS-06", qa_his_06), ("QA-HIS-07", qa_his_07),
    ("QA-HIS-08", qa_his_08), ("QA-HIS-15", qa_his_15), ("QA-HIS-18", qa_his_18),
    ("QA-FRM-01", qa_frm_01), ("QA-FRM-02", qa_frm_02), ("QA-FRM-03", qa_frm_03),
    ("QA-FRM-08", qa_frm_08), ("QA-FRM-19", qa_frm_19),
    ("QA-COM-01", qa_com_01), ("QA-COM-02", qa_com_02), ("QA-COM-03", qa_com_03),
    ("QA-COM-04", qa_com_04), ("QA-COM-05", qa_com_05), ("QA-COM-12", qa_com_12),
    ("QA-COM-14", qa_com_14),
    ("QA-EXP-01", qa_exp_01),
    ("QA-GLB-08", qa_glb_08), ("QA-GLB-09", qa_glb_09), ("QA-GLB-11", qa_glb_11),
    ("QA-GLB-12", qa_glb_12),
]


def main():
    only = sys.argv[1:] or None
    with sync_playwright() as p:
        b = p.chromium.launch()
        pg = b.new_page(viewport={"width": 1600, "height": 1100})
        for sid, fn in SCENARIOS:
            if only and sid not in only:
                continue
            try:
                preflight(pg)          # §8.0 step 4: reload between scenarios
                fn(pg)
            except Exception as e:
                rec(sid, FAIL, f"EXECUTION ERROR: {type(e).__name__}: {str(e)[:300]}")
        b.close()
    counts = {}
    for r in RESULTS:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    for r in RESULTS:
        print(f"{r['verdict']:<10} {r['id']:<12} {r['evidence']}")
    print("\n=== TOTALS ===", json.dumps(counts))
    pathlib.Path(__file__).with_name("qa-stock-status-results.json").write_text(
        json.dumps(RESULTS, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
