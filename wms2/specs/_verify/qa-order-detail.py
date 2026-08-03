#!/usr/bin/env python3
"""
Adversarial QA execution of wms2/specs/order-detail.md §8 [WF] scenarios.

METHOD (hostile QA robot — did not author the spec):
  - Every [WF] scenario in §8 is executed EXACTLY as written, using only the
    selectors / labels / expected strings the spec supplies.
  - Where the spec does not say what to click or what to assert, the scenario is
    recorded AMBIGUOUS. Nothing is improvised from knowledge of the page.

STRING-MATCH CONVENTION (forced on us — the spec mixes two registers):
  - "reads exactly X" / "text is exactly X" / "value is X"  -> strict equality
  - "reading X" / "contains X" / "containing exactly X"     -> substring
  Text is normalised: <br> -> space, all whitespace collapsed, trimmed.
  Annotation dots ARE included in text, because §8.0 preconditions require
  annotations visible.

Run:  python3 qa-order-detail.py [--md]      (--md prints the results table)
"""
import re
import sys
import pathlib
from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[2]
PAGE = (ROOT / "order-detail" / "index.html").as_uri()
SPEC = ROOT / "specs" / "order-detail.md"

RESULTS = []  # (id, verdict, evidence)


def rec(sid, verdict, evidence):
    RESULTS.append((sid, verdict, evidence))


NTXT = """([sel, root]) => {
  const scope = root ? document.querySelector(root) : document;
  const el = scope ? scope.querySelector(sel) : null;
  if (!el) return null;
  const c = el.cloneNode(true);
  c.querySelectorAll('br').forEach(b => b.replaceWith(document.createTextNode(' ')));
  return c.textContent.replace(/\\s+/g, ' ').trim();
}"""

NTXT_ALL = """([sel, root]) => {
  const scope = root ? document.querySelector(root) : document;
  if (!scope) return null;
  return [...scope.querySelectorAll(sel)].map(el => {
    const c = el.cloneNode(true);
    c.querySelectorAll('br').forEach(b => b.replaceWith(document.createTextNode(' ')));
    return c.textContent.replace(/\\s+/g, ' ').trim();
  });
}"""

# Full page text EXCLUDING <script>/<style> (both states, hidden included).
PAGETEXT = """() => {
  const c = document.body ? document.body.cloneNode(true) : document.documentElement.cloneNode(true);
  c.querySelectorAll('script,style').forEach(e => e.remove());
  return c.textContent;
}"""


class P:
    def __init__(self, page):
        self.p = page

    def load(self):
        self.p.goto(PAGE)
        self.p.wait_for_timeout(60)

    def t(self, sel, root=None):
        return self.p.evaluate(NTXT, [sel, root])

    def ts(self, sel, root=None):
        return self.p.evaluate(NTXT_ALL, [sel, root])

    def n(self, sel, root=None):
        return len(self.ts(sel, root) or [])

    def has_class(self, sel, cls):
        return self.p.evaluate(
            "([s,c])=>{const e=document.querySelector(s);return e?e.classList.contains(c):null;}",
            [sel, cls])

    def visible(self, sel):
        return self.p.evaluate(
            "(s)=>{const e=document.querySelector(s);if(!e)return null;"
            "const r=e.getBoundingClientRect();const st=getComputedStyle(e);"
            "return st.display!=='none'&&st.visibility!=='hidden'&&(r.width>0||r.height>0);}", sel)

    def disp(self, sel):
        return self.p.evaluate(
            "(s)=>{const e=document.querySelector(s);return e?getComputedStyle(e).display:null;}", sel)

    def attr(self, sel, a):
        return self.p.evaluate("([s,a])=>{const e=document.querySelector(s);return e?e.getAttribute(a):null;}",
                               [sel, a])

    def click(self, sel):
        self.p.click(sel)
        self.p.wait_for_timeout(60)

    def tab(self, label):
        self.p.click(f'.wf-tab:text-is("{label}")')
        self.p.wait_for_timeout(80)


def ok(cond, good, bad):
    return (good if cond else bad), cond


# ---------------------------------------------------------------- QA-MAP
def qa_map(d):
    d.load()
    # QA-MAP-1
    n_norm = d.ts('.dot', '#st-normal')
    n_hold = d.ts('.dot', '#st-hold')
    n_mdel = d.ts('.dot', '#m-del')
    n_all = d.n('.dot')
    legend_n = d.ts('.legend ol li .n')
    conds = [
        len(n_norm) == 13 and sorted(int(x) for x in n_norm) == list(range(1, 14)),
        len(n_hold) == 14 and sorted(int(x) for x in n_hold) == list(range(1, 15)),
        n_mdel == ['M3'],
        n_all == 28,
        len(legend_n) == 14 and legend_n == ['1', '2', '3', '4', '5', '6', '12', '10', '11', '14', '13', '9', '7', '8'],
    ]
    ev = f"#st-normal .dot={len(n_norm)} #st-hold .dot={len(n_hold)} #m-del .dot={n_mdel} .dot={n_all} legend .n={legend_n}"
    rec('QA-MAP-1', 'PASS' if all(conds) else 'FAIL', ev)

    # QA-MAP-2
    h1 = d.t('.wf-bar h1')
    hint = d.t('.wf-bar .hint')
    tabs = d.ts('.wf-bar .wf-tab')
    tog = d.t('.wf-bar .wf-toggle')
    c = (h1 == 'WMS 2.0 · Order Detail Wireframe'
         and hint == 'v1 — Based on the live admin (Order #407847) · Purple numbers = new/changed annotations'
         and tabs == ['Modal: Delete Line', '1 · Processing (default)', '2 · On Hold']
         and tog == 'Hide annotations'
         and d.p.evaluate('()=>document.querySelectorAll(".wf-tab")[1].classList.contains("on")'))
    rec('QA-MAP-2', 'PASS' if c else 'FAIL', f"h1={h1!r} tabs={tabs} toggle={tog!r}")

    # QA-MAP-3
    d.load()
    a1 = d.has_class('#st-normal', 'on'), d.has_class('#st-hold', 'on')
    d.p.evaluate('()=>window.scrollTo(0,600)')
    d.tab('2 · On Hold')
    sy = d.p.evaluate('()=>Math.round(window.scrollY)')
    a2 = (d.has_class('#st-hold', 'on'), d.has_class('#st-normal', 'on'))
    ton = d.p.evaluate('()=>[...document.querySelectorAll(".wf-tab")].map(b=>b.classList.contains("on"))')
    d.tab('1 · Processing (default)')
    a3 = (d.has_class('#st-normal', 'on'), d.has_class('#st-hold', 'on'))
    c = a1 == (True, False) and a2 == (True, False) and sy == 0 and ton[1:3] == [False, True] and a3 == (True, False)
    rec('QA-MAP-3', 'PASS' if c else 'FAIL',
        f"load(norm,hold)={a1}; after tab2 (hold,norm)={a2} scrollY={sy} tabOn={ton[1:3]}; after tab1={a3}")

    # QA-MAP-4
    d.load()
    d.click('#annoToggle')
    txt = d.t('#annoToggle')
    nb = d.has_class('body', 'no-anno')
    dotvis = d.p.evaluate('()=>[...document.querySelectorAll(".dot")].some(e=>getComputedStyle(e).display!=="none")')
    legvis = d.visible('.legend')
    d.click('#annoToggle')
    txt2 = d.t('#annoToggle')
    dotvis2 = d.p.evaluate('()=>[...document.querySelectorAll("#st-normal .dot")].some(e=>getComputedStyle(e).display!=="none")')
    c = txt == 'Show annotations' and nb and not dotvis and not legvis and txt2 == 'Hide annotations' and dotvis2
    rec('QA-MAP-4', 'PASS' if c else 'FAIL',
        f"toggled={txt!r} no-anno={nb} anyDotVisible={dotvis} legendVisible={legvis}; back={txt2!r} dotsBack={dotvis2}")

    # QA-MAP-5
    d.load()
    h3 = d.t('.legend h3')
    items = {}
    for i, n in enumerate(d.ts('.legend ol li .n')):
        items[n] = d.ts('.legend ol li')[i]
    c9 = all(s in items.get('9', '') for s in ['"Outbound to Deleo BaroShip"', 'Outbound', 'Enabled only when every item is INBOUNDED'])
    c14 = 'combined case of Hold + incomplete inbound (3/4)' in items.get('14', '')
    c10 = 'Latest Inventory Count kept' in items.get('10', '')
    c = h3 == 'Order Detail — Changes (specs 0 · A · C applied)' and c9 and c14 and c10
    rec('QA-MAP-5', 'PASS' if c else 'FAIL', f"h3={h3!r} item9={c9} item14={c14} item10={c10}")

    # QA-MAP-6 — document lint (spec says: not a browser action)
    md = SPEC.read_text(encoding='utf-8')
    sec23 = md.split('### 2.3 Legend ↔ spec map')[1].split('### 2.4')[0]
    rows = re.findall(r'^\|\s*([0-9]{1,2}|M3)\s*\|.*\|\s*§3 `\[(L-[0-9M]+[0-9]*)\]`\s*\|', sec23, re.M)
    want = [str(i) for i in range(1, 15)] + ['M3']
    heads = set(re.findall(r'^### `\[(L-[0-9M]+[0-9]*)\]`', md, re.M))
    missing = [(k, v) for k, v in rows if v not in heads]
    c = [k for k, _ in rows] == want and not missing
    rec('QA-MAP-6', 'PASS' if c else 'FAIL',
        f"§2.3 maps {len(rows)}/15 dots; §3 headings present for all={not missing}; missing={missing}")


# ---------------------------------------------------------------- QA-REN
def qa_ren(d):
    d.load()
    # QA-REN-1
    r1 = d.p.evaluate("""()=>{const tr=document.querySelector('#st-normal .litable thead tr:nth-child(1)');
      return [...tr.children].map(th=>({rs:th.getAttribute('rowspan'),cs:th.getAttribute('colspan'),
        t:(()=>{const c=th.cloneNode(true);c.querySelectorAll('br').forEach(b=>b.replaceWith(document.createTextNode(' ')));return c.textContent.replace(/\\s+/g,' ').trim();})()}));}""")
    r2 = d.ts('.litable thead tr:nth-child(2) th', '#st-normal')
    tds = d.p.evaluate("()=>[...document.querySelectorAll('#st-normal .litable tbody tr')].map(tr=>tr.children.length)")
    want2 = ['Product Name', 'Product Name KR', 'Size', 'Qty', 'Subtotal', 'Total', 'Latest Inventory Count',
             'Inbound Status', 'Sourcing Route', 'Order Number', 'Order Date', 'Product Cost 🤖',
             'Tracking Number', 'CP Link']
    c1 = ([x['rs'] for x in r1] == ['2', '2', '2', None, None, '2']
          and r1[3]['cs'] == '6' and 'Product Information (WooCommerce)' in r1[3]['t']
          and r1[4]['cs'] == '8' and 'Inventory' in r1[4]['t'] and r1[5]['t'] == 'Actions')
    c2 = len(r2) == 14 and all(w in got for w, got in zip(want2, r2))
    c3 = tds == [18, 18, 18, 18]
    rec('QA-REN-1', 'PASS' if (c1 and c2 and c3) else 'FAIL',
        f"row1 rowspans/colspans ok={c1} ({[x['t'] for x in r1]}); row2={r2}; td counts={tds}")

    # QA-REN-2
    ths = (d.ts('.litable th', '#st-normal') or []) + (d.ts('.litable th', '#st-hold') or [])
    bad = [t for t in ths if t in ('Delivery Company', 'Comments', 'Inbound Request')]
    rec('QA-REN-2', 'PASS' if not bad else 'FAIL', f"forbidden header cells found={bad}")

    # QA-REN-3
    inv = d.p.evaluate("""()=>Object.fromEntries([...document.querySelectorAll('#st-normal .litable tbody tr')]
      .map(tr=>[tr.children[1].textContent.trim().split('\\n')[0].replace(/\\(.*/,'').trim(),
                tr.children[9].textContent.trim()]))""")
    c = (inv.get('100005104') == '0' and inv.get('100043697') == '0'
         and inv.get('100012534') == '0' and inv.get('100005088') == '12')
    rec('QA-REN-3', 'PASS' if c else 'FAIL', f"LatestInventoryCount by SKU={inv}")

    # QA-REN-4
    st = d.p.evaluate("""()=>[...document.querySelectorAll('#st-normal .litable tbody tr')].map(tr=>{
        const s=tr.children[11].querySelector('span.tag'); if(!s) return null;
        const cs=getComputedStyle(s); return {cls:s.className,bg:cs.backgroundColor,fg:cs.color,t:s.textContent.trim()};})""")
    c = all(x and x['bg'] == 'rgba(0, 0, 0, 0)' and x['fg'] == 'rgb(20, 16, 27)' for x in st) \
        and sorted({x['t'] for x in st}) == ['JIT (Coupang)', 'WHOLESALE'] \
        and all(('tag-jit' in x['cls']) or ('tag-wholesale' in x['cls']) for x in st)
    rec('QA-REN-4', 'PASS' if c else 'FAIL', f"sourcing tags={st}")

    # QA-REN-5
    routes = [x['t'] for x in st]
    c = all(r in ('JIT (Coupang)', 'WHOLESALE') for r in routes) and 'JIT' not in routes and \
        not any('OTHER (' in r for r in routes)
    rec('QA-REN-5', 'PASS' if c else 'FAIL', f"route cells={routes}")

    # QA-REN-6
    bs = d.p.evaluate("""()=>[...document.querySelectorAll('#st-normal .litable tbody tr')].map(tr=>
        [tr.children[3].querySelector('b')?.textContent, tr.children[4].querySelector('b')?.textContent,
         tr.children[4].textContent.trim()])""")
    kr = 'Dr.Jart+' if True else ''
    body_has = '닥터자르트' in d.p.evaluate(PAGETEXT)
    c = all(a == 'Dr.Jart+' and b == 'Dr.Jart+' for a, b, _ in bs) and not body_has
    rec('QA-REN-6', 'PASS' if c else 'FAIL', f"<b> prefixes={[ (a,b) for a,b,_ in bs ]}; 닥터자르트 on page={body_has}")

    # QA-REN-7
    sk = d.p.evaluate("""()=>[...document.querySelectorAll('#st-normal .litable tbody tr')].map(tr=>({
        sku:tr.children[1].childNodes[0].textContent.trim(), skubot:tr.children[1].querySelector('.bot').textContent.trim(),
        qty:tr.children[6].childNodes[0].textContent.trim(), qtybot:tr.children[6].querySelector('.bot').textContent.trim()}))""")
    liinfo = d.t('.liinfo', '#st-normal')
    want = ('Edit a line via the Edit button. Use checkboxes to select items for bulk Inbound. '
            '* = WooCommerce original before variation-pack recalculation · 🤖 = auto-filled by Agent · '
            'Scroll right to see the Inventory fields.')
    c = all(r['skubot'] == f"({r['sku']}*)" and r['qty'] == '1' and r['qtybot'] == '(1*)' for r in sk) and liinfo == want
    rec('QA-REN-7', 'PASS' if c else 'FAIL', f"sku/qty asterisks ok={all(r['skubot']==f'({r['sku']}*)' for r in sk)}; .liinfo match={liinfo == want}")

    # QA-REN-8
    h4 = d.t('.logsec h4', '#st-normal')
    th = d.ts('.logtbl th', '#st-normal')
    rows = d.p.evaluate("""()=>[...document.querySelectorAll('#st-normal .logtbl tr')].slice(1).map(tr=>
        ({cells:[...tr.children].map(td=>td.textContent.trim()), cls:tr.children[1].className}))""")
    want_rows = [
        (['07-01 09:32', 'OUTBOUND', 'All (4 SKU)', '4', 'Dean', '–'], 'act-out'),
        (['07-01 09:10', 'INBOUND', '100012534', '1', 'Miranti', '–'], 'act-in'),
        (['07-01 08:58', 'INBOUND', '100043697', '1', 'Miranti', '–'], 'act-in'),
        (['06-30 20:15', 'CANCEL INBOUND (Restock)', '100005104', '1', 'Dean', 'Corrected duplicate inbound'], 'act-cancel'),
    ]
    c = (h4.startswith('Inbound / Outbound Actor Log') and '— New' in h4
         and th == ['Time', 'Action', 'SKU', 'Qty', 'Operator', 'Note']
         and [(r['cells'], r['cls']) for r in rows] == want_rows)
    rec('QA-REN-8', 'PASS' if c else 'FAIL', f"h4={h4!r} th={th} rows_match={[(r['cells'],r['cls']) for r in rows]==want_rows}")

    # QA-REN-9
    thd = d.ts('.tbl thead th', '#st-normal')
    row = d.ts('.tbl tbody td', '#st-normal')
    lm = d.t('.lastmile', '#st-normal')
    head = d.ts('.minih', '#st-normal')
    tsh = d.ts('.trackscroll thead th', '#st-normal')
    nodes = d.ts('.trackscroll .node', '#st-normal')
    c = (thd == ['Provider Order ID', 'Tracking Number', 'Status', 'Status Description', 'Created At', 'Updated At']
         and row == ['YT2618100709331860', '34YEM055929401000910906', 'DELIVERED', 'Shipment information received',
                     '6/30/2026, 8:55:53 PM', '7/13/2026, 10:10:32 AM']
         and lm == 'Last mile: AustraliaPost'
         and any('TRACKING HISTORY (synced 7/16/2026, 4:51:40 AM)' in h for h in head)
         and tsh == ['Time (local)', 'Node', 'Description', 'Location', 'UTC']
         and set(['DELIVERED', 'DELIVERY_ATTEMPT', 'IN_TRANSIT_CARRIER', 'ORDER_CREATION']) <= set(nodes))
    rec('QA-REN-9', 'PASS' if c else 'FAIL', f"thead={thd} row={row} lastmile={lm!r} minih={head} nodes={nodes}")

    # QA-REN-10
    lt = d.p.evaluate("""()=>{const tr=[...document.querySelectorAll('#st-normal .litable tbody tr')]
        .find(t=>t.children[1].textContent.includes('100043697')); return tr.children[15].textContent.trim();}""")
    ft = d.ts('.tbl tbody td', '#st-normal')[1]
    hdr_li = d.ts('.litable thead tr:nth-child(2) th', '#st-normal')
    c = lt == '10323100835456' and ft == '34YEM055929401000910906' and 'Tracking Number' in hdr_li
    rec('QA-REN-10', 'PASS' if c else 'FAIL', f"line tracking={lt!r} shipment tracking={ft!r} (separate tables/headers)")

    # QA-REN-11
    fb = d.t('.ftbadge', '#st-normal')
    btns = d.ts('.ftbadge button', '#st-normal')
    car = d.t('.ftbadge .carrier', '#st-normal')
    c = car == 'YUN' and '✎ Change Tracking #' in btns and 'Reset Order' in btns
    rec('QA-REN-11', 'PASS' if c else 'FAIL', f"carrier={car!r} buttons={btns}")

    # QA-REN-12
    kv = {k: v for k, v in zip(d.ts('.info3 .kv .k', '#st-normal'), d.ts('.info3 .kv .v', '#st-normal'))}
    logtimes = d.p.evaluate("()=>[...document.querySelectorAll('#st-normal .logtbl tr')].slice(1).map(tr=>tr.children[0].textContent.trim())")
    cmttimes = d.ts('.cmt-list time', '#st-normal')
    ship = d.ts('.tbl tbody td', '#st-normal')[4:6]
    tsh = d.ts('.trackscroll thead th', '#st-normal')
    rx_log = re.compile(r'^\d{2}-\d{2} \d{2}:\d{2}$')
    rx_ship = re.compile(r'^\d{1,2}/\d{1,2}/\d{4}, \d{1,2}:\d{2}:\d{2} (AM|PM)$')
    c = (kv.get('Order Date') == '2026-06-30 SGT' and kv.get('Order Created At') == '30/06/2026 19:55:28 SGT'
         and all(rx_log.match(t) for t in logtimes) and all(rx_log.match(t) for t in cmttimes)
         and all(rx_ship.match(t) for t in ship)
         and 'Time (local)' in tsh and 'UTC' in tsh)
    rec('QA-REN-12', 'PASS' if c else 'FAIL',
        f"OrderDate={kv.get('Order Date')!r} CreatedAt={kv.get('Order Created At')!r} log={logtimes} cmt={cmttimes} ship={ship}")


# ---------------------------------------------------------------- QA-SUB
def qa_sub(d):
    d.load()
    # QA-SUB-1
    def subbar(root):
        return d.p.evaluate("""(r)=>[...document.querySelectorAll(r+' .subbar button')].map(b=>({t:b.textContent.trim(),c:b.className}))""", root)
    a, b = subbar('#st-normal'), subbar('#st-hold')
    want = [('← Back to Orders', 'back'), ('↻ Audit History', 'link-btn'), ('↗ View in WP', 'link-btn blue'),
            ('⧉ Clone Order', 'link-btn blue'), ('✕ Cancel Order', 'link-btn red')]
    c = [(x['t'], x['c']) for x in a] == want and [(x['t'], x['c']) for x in b] == want
    rec('QA-SUB-1', 'PASS' if c else 'FAIL', f"st-normal={[(x['t'],x['c']) for x in a]}; st-hold match={[(x['t'],x['c']) for x in b]==want}")

    # QA-SUB-2
    h2 = d.t('.otitle h2', '#st-normal')
    seq = d.p.evaluate("""()=>{const o=document.querySelector('#st-normal .otitle');
      return {status:!!o.querySelector('.status'),carrier:o.querySelector('.carrier')?.textContent.trim(),
              btns:[...o.querySelectorAll('button')].map(b=>b.textContent.trim())};}""")
    c = h2 == 'Order # 407847' and seq['status'] and seq['carrier'] == 'YUN' and \
        seq['btns'] == ['View Label', '🖨 Print', 'Change Status ▾']
    rec('QA-SUB-2', 'PASS' if c else 'FAIL', f"h2={h2!r} carrier={seq['carrier']!r} buttons={seq['btns']}")

    # QA-SUB-3
    kv = {k: v for k, v in zip(d.ts('.info3 .kv .k', '#st-normal'), d.ts('.info3 .kv .v', '#st-normal'))}
    picbtn = d.t('.info3 .kv .v button', '#st-normal')
    picborder = d.p.evaluate("()=>{const b=document.querySelector('#st-normal .info3 .kv .v button');"
                             "return getComputedStyle(b).borderStyle;}")
    c = (kv.get('Order Date') == '2026-06-30 SGT' and kv.get('Order Created At') == '30/06/2026 19:55:28 SGT'
         and kv.get('Total Items') == '4' and kv.get('Total Discount') == 'AUD 13.11'
         and kv.get('Total Amount') == 'AUD 129.8' and kv.get('PIC', '').startswith('Egita')
         and picbtn == '✎ Edit')
    rec('QA-SUB-3', 'PASS' if c else 'FAIL', f"PIC={kv.get('PIC')!r} button={picbtn!r} borderStyle={picborder}")

    # QA-SUB-4
    for st in ('#st-normal', '#st-hold'):
        pass
    bare = d.p.evaluate("""()=>['#st-normal','#st-hold'].map(r=>{
        const rows=[...document.querySelectorAll(r+' .info3 .kv')].filter(k=>k.querySelector('.k')?.textContent.trim()==='PIC');
        return rows.map(k=>({btn:k.querySelector('button')?.textContent.trim(),
                             bareSpan:!!k.querySelector('span.edit')}));});""")
    c = all(x[0]['btn'] and 'Edit' in x[0]['btn'] and not x[0]['bareSpan'] for x in bare)
    rec('QA-SUB-4', 'PASS' if c else 'FAIL', f"PIC controls per state={bare}")

    # QA-SUB-5
    heads = d.ts('.info3 h3', '#st-normal')
    edits = d.p.evaluate("""()=>[...document.querySelectorAll('#st-normal .info3 h3')].map(h=>
        ({h:h.textContent.trim(),edit:h.querySelector('span.edit')?.textContent.trim()}))""")
    c = (any(e['h'].startswith('👤 Billing Address') and e['edit'] == '✎' for e in edits)
         and any(e['h'].startswith('🚚 Shipping Address') and e['edit'] == '✎' for e in edits)
         and kv.get('Tax ID') == '–' and kv.get('Short Address Code') == '–'
         and kv.get('Email') == 'm.saltoon@gmail.com' and kv.get('Phone') == '+61415999051')
    rec('QA-SUB-5', 'PASS' if c else 'FAIL', f"headings={edits} TaxID={kv.get('Tax ID')!r} ShortAddr={kv.get('Short Address Code')!r} Email={kv.get('Email')!r}")

    # QA-SUB-6
    tqn = d.t('.li-foot .tq', '#st-normal')
    tqh = d.t('.li-foot .tq', '#st-hold')
    addn = [x for x in d.ts('.li-foot button', '#st-normal') if x == '+ Add Line Item']
    c = tqn == 'Total Quantity: 4' and tqh == 'Total Quantity: 4' and addn
    rec('QA-SUB-6', 'PASS' if c else 'FAIL', f"st-normal tq={tqn!r} st-hold tq={tqh!r} addBtn={addn}")

    # QA-SUB-7
    nav = d.p.evaluate("""()=>{const n=document.querySelector('#st-normal .nav');
      const links=[...n.children].filter(e=>e.tagName==='SPAN'&&!e.className&&e.children.length===0)
                                 .map(e=>e.textContent.trim()).filter(t=>t);
      return {brand:n.querySelector('.brand')?.textContent.trim(), spans:links,
              cmt:n.querySelector('.icon-btn')?.textContent.trim(),
              user:n.querySelector('.user')?.textContent.trim(),
              avatar:n.querySelector('.avatar')?.textContent.trim(),
              logout:n.querySelector('.logout')?.textContent.trim(),
              order:[...n.children].map(e=>e.className||e.tagName)};}""")
    want_links = ['Operation AI \u25be', 'Catalog Management \u25be', 'OMS Center \u25be', 'Site Management \u25be',
                  'Customer Management \u25be', 'SkinSeoul WP Admin']
    c = (nav['brand'] == 'SkinSeoul' and nav['spans'] == want_links
         and nav['cmt'].startswith('\U0001f4ac Comments') and 'Yongwon Ryu' in nav['user']
         and nav['avatar'] == 'Y' and nav['logout'] == 'Logout')
    rec('QA-SUB-7', 'PASS' if c else 'FAIL', f"nav={nav}")

    # QA-SUB-19
    costs = d.p.evaluate("()=>[...document.querySelectorAll('#st-normal .litable tbody tr')].map(tr=>tr.children[14].textContent.trim())")
    usd = bool(re.search(r'USD|\$\s?\d', d.p.evaluate(PAGETEXT)))
    c = (kv.get('Total Discount') == 'AUD 13.11' and kv.get('Total Amount') == 'AUD 129.8'
         and set(['₩17,100', '₩22,425', '₩30,630']) <= set(costs) and not usd)
    rec('QA-SUB-19', 'PASS' if c else 'FAIL',
        f"discount={kv.get('Total Discount')!r} amount={kv.get('Total Amount')!r} costs={costs} USD-on-page={usd}")


# ---------------------------------------------------------------- QA-INB / OUT / STA / EDIT / PRT
def qa_group4(d):
    d.load()
    # QA-INB-1
    rows = d.p.evaluate("""()=>[...document.querySelectorAll('#st-normal .litable tbody tr')].map(tr=>({
        cls:tr.className, tag:tr.querySelector('.tag-inbounded,.tag-pending')?.textContent.trim(),
        acts:[...tr.querySelectorAll('td:last-child button')].map(b=>({t:b.textContent.trim(),c:b.className}))}))""")
    c = (len(rows) == 4 and all(r['tag'] == 'INBOUNDED' for r in rows)
         and all(any(a['t'] == 'Cancel Inbound' and 'btn-red-line' in a['c'] for a in r['acts']) for r in rows[1:])
         and 'row-edit' in rows[0]['cls'] and not any(a['t'] == 'Cancel Inbound' for a in rows[0]['acts']))
    rec('QA-INB-1', 'PASS' if c else 'FAIL', f"rows={len(rows)} tags={[r['tag'] for r in rows]} row1cls={rows[0]['cls']!r} row1acts={[a['t'] for a in rows[0]['acts']]}")

    # QA-INB-2
    d.tab('2 · On Hold')
    h = d.p.evaluate("""()=>Object.fromEntries([...document.querySelectorAll('#st-hold .litable tbody tr')].map(tr=>[
        tr.children[1].childNodes[0].textContent.trim(),
        {tag:tr.querySelector('.tag-inbounded,.tag-pending')?.textContent.trim(),
         tagcls:tr.querySelector('.tag-inbounded,.tag-pending')?.className,
         acts:[...tr.querySelectorAll('td:last-child button')].map(b=>({t:b.textContent.trim(),c:b.className}))}]))""")
    r = h['100043697']
    c = (r['tag'] == 'PENDING' and 'tag-pending' in r['tagcls']
         and any(a['t'] == 'Inbound' and 'btn-green' in a['c'] for a in r['acts'])
         and not any(a['t'] == 'Cancel Inbound' for a in r['acts'])
         and h['100005088']['tag'] == 'INBOUNDED' and any(a['t'] == 'Cancel Inbound' for a in h['100005088']['acts'])
         and h['100012534']['tag'] == 'INBOUNDED' and any(a['t'] == 'Cancel Inbound' for a in h['100012534']['acts']))
    rec('QA-INB-2', 'PASS' if c else 'FAIL', f"100043697={r['tag']!r} acts={[a['t'] for a in r['acts']]}; 100005088/100012534 INBOUNDED+CancelInbound ok")

    # QA-INB-3  (spec: string must appear NOWHERE, "including the legend")
    d.load()
    where = d.p.evaluate("""()=>{const out=[];
      const scan=(sel,name)=>{const e=document.querySelector(sel); if(e&&e.textContent.includes('Request Inbound')) out.push(name);};
      scan('#st-normal','st-normal'); scan('#st-hold','st-hold'); scan('.legend','legend');
      return out;}""")
    hdrbad = [t for t in (d.ts('.litable th', '#st-normal') or []) + (d.ts('.litable th', '#st-hold') or []) if t == 'Inbound Request']
    legend_quote = d.p.evaluate("""()=>{const li=[...document.querySelectorAll('.legend ol li')].find(l=>l.textContent.includes('Request Inbound'));
        return li? li.textContent.replace(/\\s+/g,' ').trim().slice(0,150):null;}""")
    c = not where and not hdrbad
    rec('QA-INB-3', 'PASS' if c else 'FAIL',
        f"'Request Inbound' found in: {where}; legend text: {legend_quote!r}; forbidden header cells={hdrbad}")

    # QA-INB-4
    def foot(root):
        return d.p.evaluate("""(r)=>[...document.querySelector(r+' .li-foot').children].map(e=>e.textContent.trim()).filter(t=>t)""", root)
    fn, fh = foot('#st-normal'), foot('#st-hold')
    want = ['Total Quantity: 4', 'Bulk Inbound Selected Items2', '📦 Outbound9', '+ Add Line Item']
    want_clean = ['Total Quantity: 4', 'Bulk Inbound Selected Items', '📦 Outbound', '+ Add Line Item']
    def clean(l):
        return [re.sub(r'\d+$', '', x) if x not in ('Total Quantity: 4',) else x for x in l]
    c = clean(fn) == want_clean and clean(fh) == want_clean
    rec('QA-INB-4', 'PASS' if c else 'FAIL', f"st-normal footer order={fn}; st-hold={fh} (trailing digits = annotation dots)")

    # QA-INB-5
    sa = d.n('.litable thead input[type=checkbox][title="Select all"]', '#st-normal')
    rb = d.n('.litable tbody tr td:first-child input[type=checkbox]', '#st-normal')
    rec('QA-INB-5', 'PASS' if (sa == 1 and rb == 4) else 'FAIL', f"select-all={sa} row checkboxes={rb}")

    # QA-OUT-1
    ob = d.p.evaluate("""()=>{const b=document.querySelector('#st-normal #obBtn');
        return {t:b.textContent.trim(),c:b.className,dis:b.hasAttribute('disabled')};}""")
    c = ob['t'] == '📦 Outbound' and 'btn-green' in ob['c'] and not ob['dis']
    rec('QA-OUT-1', 'PASS' if c else 'FAIL', f"#obBtn={ob}")

    # QA-OUT-2
    d.tab('2 · On Hold')
    g = d.p.evaluate("""()=>{const b=document.querySelector('#st-hold .li-foot button.btn-gray');
        return {t:b.textContent.trim(),dis:b.hasAttribute('disabled'),op:b.style.opacity,cur:b.style.cursor,
                rawStyle:b.getAttribute('style'),id:b.id};}""")
    banner = d.t('#holdBannerH')
    bantxt = '⏸ On Hold by urgent CS request — inbound still allowed, but Outbound disabled. Release the hold (Change Status) to ship'
    pend = d.p.evaluate("""()=>{const tr=[...document.querySelectorAll('#st-hold .litable tbody tr')]
        .find(t=>t.children[1].textContent.includes('100043697'));
        return {tag:tr.querySelector('.tag')?.textContent.trim(),
                btn:[...tr.querySelectorAll('td:last-child button')].map(b=>b.textContent.trim()+'|'+b.className)};}""")
    c = (g['t'] == '📦 Outbound' and g['dis'] and 'opacity:.55' in g['rawStyle'] and g['cur'] == 'not-allowed' and not g['id']
         and d.visible('#holdBannerH') and bantxt in banner
         and pend['tag'] == 'PENDING' and any(x.startswith('Inbound|') and 'btn-green' in x for x in pend['btn']))
    rec('QA-OUT-2', 'PASS' if c else 'FAIL',
        f"grayBtn={g}; banner text (incl. dot)={banner!r}; pending row={pend}")

    # QA-OUT-3  (spec: string appears NOWHERE in either state or the legend)
    d.load()
    hits = d.p.evaluate("""()=>{const out=[];
      [['#st-normal','st-normal'],['#st-hold','st-hold'],['.legend','legend']].forEach(([s,n])=>{
        const e=document.querySelector(s); if(e&&e.textContent.includes('Outbound to Deleo BaroShip')) out.push(n);});
      return out;}""")
    labels = d.p.evaluate("""()=>['#st-normal','#st-hold'].map(r=>{
        const b=document.querySelector(r+' .li-foot button.btn-green, '+r+' .li-foot button.btn-gray');
        return b.textContent.trim();})""")
    c = not hits and labels == ['📦 Outbound', '📦 Outbound']
    leg9 = d.p.evaluate("""()=>{const li=[...document.querySelectorAll('.legend ol li')].find(l=>l.textContent.includes('Deleo BaroShip'));
        return li?li.textContent.replace(/\\s+/g,' ').trim().slice(0,120):null;}""")
    rec('QA-OUT-3', 'PASS' if c else 'FAIL',
        f"'Outbound to Deleo BaroShip' found in: {hits}; legend #9 = {leg9!r}; footer labels={labels}")

    # QA-STA-1
    d.load()
    d.click('#st-normal button[data-open="statusdd"]')
    vis = d.visible('#statusdd')
    items = d.p.evaluate("""()=>[...document.querySelectorAll('#statusdd div')].map(e=>({t:e.textContent.trim(),on:e.classList.contains('on')}))""")
    want = ['pending', 'processing', 'on-hold', 'completed', 'refunded', 'failed', 'shipped', 'prepare-shipment']
    c = vis and [i['t'] for i in items] == want and items[1]['on']
    rec('QA-STA-1', 'PASS' if c else 'FAIL', f"visible={vis} items={[i['t'] for i in items]} processing.on={items[1]['on']}")

    # QA-STA-2
    bad = [i['t'] for i in items if i['t'] in ('cancelled', 'cancel')]
    co = d.p.evaluate("""()=>{const b=[...document.querySelectorAll('#st-normal .subbar button')].find(x=>x.textContent.trim()==='✕ Cancel Order');
        return b?b.className:null;}""")
    c = not bad and co == 'link-btn red'
    rec('QA-STA-2', 'PASS' if c else 'FAIL', f"forbidden dropdown items={bad}; ✕ Cancel Order class={co!r}")

    # QA-STA-3
    d.load()
    d.tab('2 · On Hold')
    d.click('#st-hold button[data-open="statusddH"]')
    it = d.p.evaluate("""()=>[...document.querySelectorAll('#statusddH div')].map(e=>({t:e.textContent.trim(),on:e.classList.contains('on')}))""")
    c = d.visible('#statusddH') and next(x for x in it if x['t'] == 'on-hold')['on'] and \
        not next(x for x in it if x['t'] == 'processing')['on']
    rec('QA-STA-3', 'PASS' if c else 'FAIL', f"visible={d.visible('#statusddH')} on-hold.on / processing.on = {[ (x['t'],x['on']) for x in it if x['t'] in ('on-hold','processing')]}")

    # QA-STA-4  — click outside must close
    d.load()
    d.click('#st-normal button[data-open="statusdd"]')
    before = d.visible('#statusdd')
    d.p.mouse.click(5, 400)          # page background
    d.p.wait_for_timeout(80)
    after = d.visible('#statusdd')
    badge = d.t('#st-normal #ordStatus')
    handlers = d.p.evaluate("()=>document.documentElement.outerHTML.includes(\"document.addEventListener('click'\")")
    c = (not after) and badge == 'Processing'
    rec('QA-STA-4', 'PASS' if c else 'FAIL',
        f"dropdown visible before background click={before}, after={after}; badge={badge!r}; "
        f"page has document-level click handler={handlers}")

    # QA-STA-5
    d.load()
    st = d.p.evaluate("""()=>{const s=document.querySelector('#st-normal #ordStatus');
        return {t:s.textContent.trim(),c:s.className,banner:!!document.querySelector('#st-normal [id^=holdBanner]')};}""")
    d.tab('2 · On Hold')
    sh = d.p.evaluate("""()=>{const s=document.querySelector('#st-hold .status');
        return {t:s.textContent.trim(),c:s.className};}""")
    bn = d.t('#holdBannerH')
    bantxt = '⏸ On Hold by urgent CS request — inbound still allowed, but Outbound disabled. Release the hold (Change Status) to ship'
    c = (st['t'] == 'Processing' and 'st-processing' in st['c'] and not st['banner']
         and sh['t'] == 'On Hold' and 'st-hold' in sh['c'] and d.visible('#holdBannerH') and bantxt in bn)
    rec('QA-STA-5', 'PASS' if c else 'FAIL', f"state1={st}; state2={sh}; banner visible={d.visible('#holdBannerH')}")

    # QA-STA-6 — spec gives no comparison method for "identical"
    d.load()
    diffs = d.p.evaluate("""()=>{
      const T=e=>{if(!e)return null;const c=e.cloneNode(true);
        c.querySelectorAll('br').forEach(b=>b.replaceWith(document.createTextNode(' ')));
        return c.textContent.replace(/\\s+/g,' ').trim();};
      const pairs={nav:'.nav',subbar:'.subbar',info3:'.info3',cmt:'.cmt-list',ft:'.sec:nth-of-type(3)',log:'.logsec'};
      const out={};
      for(const [k,s] of Object.entries(pairs))
        out[k]=T(document.querySelector('#st-normal '+s))===T(document.querySelector('#st-hold '+s));
      const rows=r=>[...document.querySelectorAll(r+' .litable tbody tr')].map(T);
      const a=rows('#st-normal'),b=rows('#st-hold');
      out.rows=[0,2,3].every(i=>a[i]===b[i]); out.row2differs=a[1]!==b[1];
      const ids=r=>[...document.querySelectorAll(r+' [id]')].map(e=>e.id);
      out.idsNormal=ids('#st-normal'); out.idsHold=ids('#st-hold');
      return out;}""")
    rec('QA-STA-6', 'AMBIGUOUS',
        "spec says the listed blocks are 'identical' but never states the comparison basis (DOM? text? attributes?). "
        f"Text-level result: {dict((k,v) for k,v in diffs.items() if k not in ('idsNormal','idsHold'))}. "
        f"Undeclared 6th diff at DOM level: ids {diffs['idsNormal']} vs {diffs['idsHold']} "
        "(inbox1/inbox1H, statusdd/statusddH, addCmt/addCmtH) — the spec's enumeration of 5 diffs omits them "
        "even though other [WF] scenarios depend on those very ids.")

    # QA-EDIT-1
    d.load()
    vals = d.p.evaluate("()=>[...document.querySelectorAll('#st-normal tr.row-edit input.ed-in')].map(i=>i.value)")
    today = d.p.evaluate("""()=>{const b=document.querySelector('#st-normal tr.row-edit button.ed-today');
        if(!b)return null;const inp=b.parentElement.querySelector('input.ed-in');
        const rb=b.getBoundingClientRect(),ri=inp.getBoundingClientRect();
        return {t:b.textContent.trim(),below:rb.top>=ri.bottom-1};}""")
    want = ['12101316464794', '2026-06-30', '15000', '10323100835644',
            'https://www.coupang.com/vp/products/7055479133?itemId=17506867787']
    c = vals == want and today and today['t'] == 'Today' and today['below']
    rec('QA-EDIT-1', 'PASS' if c else 'FAIL', f"inputs={len(vals)} values match={vals==want}; Today btn={today}")

    # QA-EDIT-2
    e2 = d.p.evaluate("""()=>{const td=document.querySelector('#st-normal tr.row-edit td:last-child');
        return {ok:td.querySelector('.act-ic button.ok')?.textContent.trim(),
                no:td.querySelector('.act-ic button.no')?.textContent.trim(),
                cancel:[...td.querySelectorAll('button')].some(b=>b.textContent.trim()==='Cancel Inbound'),
                edit:!!td.querySelector('button.edit'), del:!!td.querySelector('button.del')};}""")
    c = e2['ok'] == '✓' and e2['no'] == '✕' and not e2['cancel'] and not e2['edit'] and not e2['del']
    rec('QA-EDIT-2', 'PASS' if c else 'FAIL', f"{e2}")

    # QA-EDIT-3
    idx = {'SKU': 1, 'Product Name': 3, 'Product Name KR': 4, 'Size': 5, 'Qty': 6, 'Subtotal': 7, 'Total': 8,
           'Latest Inventory Count': 9, 'Inbound Status': 10, 'Sourcing Route': 11}
    e3 = d.p.evaluate("""(idx)=>{const tr=document.querySelector('#st-normal tr.row-edit');
        const o={};for(const [k,i] of Object.entries(idx)) o[k]=tr.children[i].querySelectorAll('input').length;return o;}""",
                      idx)
    c = all(v == 0 for v in e3.values())
    rec('QA-EDIT-3', 'PASS' if c else 'FAIL', f"input count per commerce cell={e3}")

    # QA-EDIT-4
    e4 = d.p.evaluate("""()=>{const tr=[...document.querySelectorAll('#st-normal .litable tbody tr')]
        .find(t=>t.children[1].textContent.includes('100043697'));
        const cells=[...tr.children].slice(9,17);
        return {vals:cells.map(c=>c.textContent.trim()),inputs:cells.reduce((a,c)=>a+c.querySelectorAll('input').length,0)};}""")
    want = ['0', 'INBOUNDED', 'JIT (Coupang)', '12101316464794', '2026-06-30', '₩17,100', '10323100835456', 'coupang…7923']
    c = e4['vals'] == want and e4['inputs'] == 0
    rec('QA-EDIT-4', 'PASS' if c else 'FAIL', f"cells={e4['vals']} inputs={e4['inputs']}")

    # QA-EDIT-5
    e5 = d.p.evaluate("""()=>[...document.querySelectorAll('#st-normal .litable tbody tr:not(.row-edit)')].map(tr=>{
        const td=tr.querySelector('td:last-child');
        const e=td.querySelector('button.edit'),dl=td.querySelector('button.del');
        return {edit:e?.textContent.trim(),del:dl?.textContent.trim(),modal:dl?.getAttribute('data-modal')};})""")
    c = len(e5) == 3 and all(x['edit'] == '✎' and x['del'] == '🗑' and x['modal'] == 'm-del' for x in e5)
    rec('QA-EDIT-5', 'PASS' if c else 'FAIL', f"{e5}")

    # QA-PRT-1
    prt = d.p.evaluate("""()=>{const o=document.querySelector('#st-normal .otitle');
        return {print:[...o.querySelectorAll('button')].map(b=>b.textContent.trim()).includes('🖨 Print'),
                carrier:o.querySelector('.carrier')?.textContent.trim()};}""")
    bad = d.p.evaluate("()=>['Print (YUN)','Print (DELEO)'].filter(s=>document.body.textContent.includes(s))")
    c = prt['print'] and prt['carrier'] == 'YUN' and not bad
    rec('QA-PRT-1', 'PASS' if c else 'FAIL', f"🖨 Print present={prt['print']} carrier={prt['carrier']!r} forbidden strings={bad}")

    # QA-PRT-2
    p2 = d.p.evaluate("""()=>['#st-normal','#st-hold'].map(r=>[...document.querySelectorAll(r+' .otitle button')].map(b=>b.textContent.trim()))""")
    c = all('View Label' in x and '🖨 Print' in x for x in p2)
    rec('QA-PRT-2', 'PASS' if c else 'FAIL', f"otitle buttons per state={p2}")


# ---------------------------------------------------------------- QA-HUB
def qa_hub(d):
    d.load()
    d.click('#st-normal .icon-btn[data-open="inbox1"]')
    opened = d.has_class('#inbox1', 'open')
    ph = d.attr('#inbox1 .csearch input', 'placeholder')
    tabs = d.ts('.tabs button', '#inbox1')
    tabon = d.p.evaluate("()=>[...document.querySelectorAll('#inbox1 .tabs button')].map(b=>b.classList.contains('on'))")
    pheader = d.t('[data-pane="mentions"] .paneheader', '#inbox1')
    c = (opened and ph == '🔍 Search all comments — order no. · author · text'
         and len(tabs) == 2 and tabs[0].startswith('@ Mentions') and tabs[1] == '★ Saved' and tabon[0]
         and 'Comments mentioning me · Click to open the order' in pheader and 'Mark all read' in pheader)
    rec('QA-HUB-1', 'PASS' if c else 'FAIL',
        f"open={opened} placeholder ok={ph=='🔍 Search all comments — order no. · author · text'} "
        f"tabs={tabs} (note: tab 1 text is {tabs[0]!r}, not bare '@ Mentions') paneheader={pheader!r}")

    # QA-HUB-2
    nb = d.t('.icon-btn[data-open="inbox1"] .badge-n', '#st-normal')
    tb = d.t('.tabs button.on .badge-n', '#inbox1')
    un = d.n('[data-pane="mentions"] .it.unread', '#inbox1')
    third = d.p.evaluate("()=>document.querySelectorAll('#inbox1 [data-pane=\"mentions\"] .it')[2].classList.contains('unread')")
    thirdtxt = d.ts('[data-pane="mentions"] .it', '#inbox1')[2]
    c = nb == '2' and tb == '2' and un == 2 and not third
    rec('QA-HUB-2', 'PASS' if c else 'FAIL', f"navBadge={nb!r} tabBadge={tb!r} unread={un} third unread={third} ({thirdtxt!r})")

    # QA-HUB-3
    d.click('#inbox1 .tabs button[data-tab="saved"]')
    sv = d.disp('#inbox1 [data-pane="saved"]')
    sph = d.t('[data-pane="saved"] .paneheader', '#inbox1')
    items = d.ts('[data-pane="saved"] .it', '#inbox1')
    star_on = d.p.evaluate("()=>document.querySelector('#inbox1 [data-pane=\"saved\"] .it .star').classList.contains('on')")
    mh = d.disp('#inbox1 [data-pane="mentions"]')
    c = (sv != 'none' and 'Saved comments · Click to open the order' in sph and 'Unstar to remove' in sph
         and len(items) == 1 and 'Order 407812' in items[0] and 'Miranti' in items[0]
         and '@Yongwon 1 JIT item not yet inbounded' in items[0] and star_on and mh == 'none')
    rec('QA-HUB-3', 'PASS' if c else 'FAIL', f"saved display={sv} header={sph!r} items={items} star.on={star_on} mentions display={mh}")

    # QA-HUB-4
    d.load()
    d.click('#st-normal .icon-btn[data-open="inbox1"]')
    d.p.fill('#inbox1 .csearch input', 'miranti')
    d.p.wait_for_timeout(80)
    tdisp = d.disp('#inbox1 .tabs')
    csr = d.t('[data-pane="csr"] .paneheader', '#inbox1')
    hits = d.ts('[data-pane="csr"] .it', '#inbox1')
    mark = d.ts('[data-pane="csr"] mark', '#inbox1')
    d.p.fill('#inbox1 .csearch input', 'zzzz')
    d.p.wait_for_timeout(80)
    empty = d.t('[data-pane="csr"]', '#inbox1')
    nhits = d.n('[data-pane="csr"] .it', '#inbox1')
    d.p.fill('#inbox1 .csearch input', '')
    d.p.wait_for_timeout(80)
    tdisp2 = d.disp('#inbox1 .tabs')
    on2 = d.p.evaluate("()=>document.querySelector('#inbox1 .tabs button.on').dataset.tab")
    mdisp = d.disp('#inbox1 [data-pane="mentions"]')
    c = (tdisp == 'none' and csr == '1 results · newest first · click to open the order'
         and len(hits) == 1 and 'Order 407812' in hits[0] and 'Miranti' in mark
         and 'No matching comments' in empty and nhits == 0
         and tdisp2 != 'none' and on2 == 'mentions' and mdisp != 'none')
    rec('QA-HUB-4', 'PASS' if c else 'FAIL',
        f"tabs display on search={tdisp}; header={csr!r}; hits={hits}; marks={mark}; "
        f"zzzz pane={empty!r} its={nhits}; restore: tabs={tdisp2} activeTab={on2} pane={mdisp}")

    # QA-HUB-5
    d.p.fill('#inbox1 .csearch input', '407301')
    d.p.wait_for_timeout(80)
    h = d.t('[data-pane="csr"] .paneheader', '#inbox1')
    it = d.ts('[data-pane="csr"] .it', '#inbox1')
    c = h == '1 results · newest first · click to open the order' and len(it) == 1 and \
        'Order 407301' in it[0] and 'Dean' in it[0] and 'Repacked and shipped' in it[0]
    rec('QA-HUB-5', 'PASS' if c else 'FAIL', f"header={h!r} item={it}")

    # QA-HUB-6
    d.p.fill('#inbox1 .csearch input', 'sachet')
    d.p.wait_for_timeout(80)
    h1 = d.t('[data-pane="csr"] .paneheader', '#inbox1')
    i1 = d.ts('[data-pane="csr"] .it', '#inbox1')
    m1 = d.ts('[data-pane="csr"] mark', '#inbox1')
    d.p.fill('#inbox1 .csearch input', 'dean')
    d.p.wait_for_timeout(80)
    h2 = d.t('[data-pane="csr"] .paneheader', '#inbox1')
    i2 = d.ts('[data-pane="csr"] .it', '#inbox1')
    c = (h1 == '1 results · newest first · click to open the order' and len(i1) == 1
         and 'Order 407688' in i1[0] and 'Aldo' in i1[0] and 'sachet' in m1
         and h2 == '2 results · newest first · click to open the order'
         and 'Order 407847' in i2[0] and 'Order 407301' in i2[1])
    rec('QA-HUB-6', 'PASS' if c else 'FAIL', f"sachet: {h1!r} {i1} marks={m1}; dean: {h2!r} order={[x[:22] for x in i2]}")

    # QA-HUB-7
    d.p.fill('#inbox1 .csearch input', '<')
    d.p.wait_for_timeout(80)
    pane = d.t('[data-pane="csr"]', '#inbox1')
    kids = d.p.evaluate("""()=>{const p=document.querySelector('#inbox1 [data-pane="csr"]');
        return [...p.querySelectorAll('*')].map(e=>e.tagName);}""")
    c = 'No matching comments' in pane and set(kids) <= {'DIV'}
    rec('QA-HUB-7', 'PASS' if c else 'FAIL', f"pane={pane!r} child tags={kids}")

    # QA-HUB-8
    d.load()
    d.tab('2 · On Hold')
    d.click('#st-hold .icon-btn[data-open="inbox1H"]')
    o = d.has_class('#inbox1H', 'open')
    ph = d.attr('#inbox1H .csearch input', 'placeholder')
    tabs = d.ts('.tabs button', '#inbox1H')
    bn = d.t('.icon-btn[data-open="inbox1H"] .badge-n', '#st-hold')
    its = d.ts('[data-pane="mentions"] .it', '#inbox1H')
    c = (o and ph == '🔍 Search all comments — order no. · author · text' and len(tabs) == 2
         and bn == '2' and len(its) == 3)
    rec('QA-HUB-8', 'PASS' if c else 'FAIL', f"open={o} placeholder ok={ph is not None} tabs={tabs} badge={bn!r} mentionItems={len(its)}")


# ---------------------------------------------------------------- QA-CMT
def qa_cmt(d):
    d.load()
    ph = d.attr('#st-normal .cmt-new textarea', 'placeholder')
    add = d.t('#addCmt', '#st-normal')
    hide = d.p.evaluate("""()=>{const h=[...document.querySelectorAll('#st-normal .sec > h3')].find(x=>x.textContent.includes('Operator Comments'));
        return h?.querySelector('button')?.textContent.trim();}""")
    want_ph = ('Write a comment — @name to notify via Slack (order no. · text · time · author included). '
               'Per-order history accumulates here.')
    c = ph == want_ph and add == 'Add Comment' and hide == 'Hide Comments'
    rec('QA-CMT-1', 'PASS' if c else 'FAIL', f"placeholder match={ph==want_ph} addBtn={add!r} hideBtn={hide!r}")

    # QA-CMT-2
    d.load()
    rows = d.p.evaluate("""()=>[...document.querySelectorAll('#st-normal .cmt-list .c-item')].map(r=>({
        who:r.querySelector('.who').textContent.trim(), at:r.querySelector('.at')?.textContent.trim(),
        body:r.querySelectorAll('span')[1]?.textContent.trim(), time:r.querySelector('time').textContent.trim(),
        star:r.querySelector('.star').classList.contains('on')}))""")
    c = (len(rows) == 2 and rows[0]['who'] == 'Dean' and rows[0]['at'] == '@Yongwon'
         and 'Please pack this order with extra care — repeat-purchase VIP customer.' in rows[0]['body']
         and rows[0]['time'] == '07-13 10:42' and not rows[0]['star']
         and rows[1]['who'] == 'Yongwon' and rows[1]['at'] == '@Dean' and rows[1]['time'] == '07-13 10:55'
         and rows[1]['star'])
    rec('QA-CMT-2', 'PASS' if c else 'FAIL', f"{rows}")

    # QA-CMT-3
    d.load()
    d.p.fill('#st-normal .cmt-new textarea', 'Checked the sachet count')
    d.click('#st-normal #addCmt')
    n = d.n('.cmt-list .c-item', '#st-normal')
    last = d.p.evaluate("""()=>{const r=[...document.querySelectorAll('#st-normal .cmt-list .c-item')].pop();
        return {who:r.querySelector('.who').textContent.trim(),body:r.querySelectorAll('span')[1].textContent.trim(),
                time:r.querySelector('time').textContent.trim()};}""")
    ta = d.p.evaluate("()=>document.querySelector('#st-normal .cmt-new textarea').value")
    still_on = d.has_class('#st-normal', 'on')
    tabon = d.p.evaluate("()=>document.querySelectorAll('.wf-tab')[1].classList.contains('on')")
    hold_n = d.n('.cmt-list .c-item', '#st-hold')
    c = (n == 3 and last['who'] == 'Yongwon' and last['body'] == 'Checked the sachet count'
         and last['time'] == 'Just now' and ta == '' and still_on and tabon and hold_n == 2)
    rec('QA-CMT-3', 'PASS' if c else 'FAIL', f"rows={n} last={last} textarea={ta!r} st-normal.on={still_on} tab.on={tabon} st-hold rows={hold_n}")

    # QA-CMT-4
    d.load()
    d.click('#st-normal #addCmt')
    n1 = d.n('.cmt-list .c-item', '#st-normal')
    d.p.fill('#st-normal .cmt-new textarea', '   ')
    d.click('#st-normal #addCmt')
    n2 = d.n('.cmt-list .c-item', '#st-normal')
    rec('QA-CMT-4', 'PASS' if (n1 == 2 and n2 == 2) else 'FAIL', f"after empty click={n1}; after 3 spaces={n2}")

    # QA-CMT-5
    d.load()
    d.p.fill('#st-normal .cmt-new textarea', '@Dean please double-bag this')
    d.click('#st-normal #addCmt')
    r = d.p.evaluate("""()=>{const r=[...document.querySelectorAll('#st-normal .cmt-list .c-item')].pop();
        const at=r.querySelector('.at');
        return {at:at?.textContent.trim(), rest:r.querySelectorAll('span')[1].textContent.replace(at.textContent,'').trim(),
                restInAt:[...r.querySelectorAll('.at')].map(x=>x.textContent.trim())};}""")
    c = r['at'] == '@Dean' and r['rest'] == 'please double-bag this' and r['restInAt'] == ['@Dean']
    rec('QA-CMT-5', 'PASS' if c else 'FAIL', f"{r}")

    # QA-CMT-6
    d.load()
    sel = '#st-normal .cmt-list .c-item:nth-child(1) .star'
    b0 = d.has_class(sel, 'on')
    d.click(sel)
    b1 = d.has_class(sel, 'on')
    d.click(sel)
    b2 = d.has_class(sel, 'on')
    c = (not b0) and b1 and (not b2)
    rec('QA-CMT-6', 'PASS' if c else 'FAIL', f"initial on={b0} after click1={b1} after click2={b2}")

    # QA-CMT-7
    d.load()
    d.tab('2 · On Hold')
    ph = d.attr('#st-hold .cmt-new textarea', 'placeholder')
    add = d.t('#addCmtH', '#st-hold')
    rows = d.p.evaluate("""()=>[...document.querySelectorAll('#st-hold .cmt-list .c-item')].map(r=>
        [r.querySelector('.who').textContent.trim(), r.querySelector('time').textContent.trim()])""")
    c = ph == want_ph and add == 'Add Comment' and rows == [['Dean', '07-13 10:42'], ['Yongwon', '07-13 10:55']]
    rec('QA-CMT-7', 'PASS' if c else 'FAIL', f"placeholder same={ph==want_ph} addCmtH={add!r} rows={rows}")


# ---------------------------------------------------------------- QA-DEL
def qa_del(d):
    d.load()
    d.click('.wf-tab[data-modal="m-del"]')
    op = d.has_class('#m-del', 'open')
    hdr = d.t('#m-del .modal header')
    x = d.t('#m-del .modal header .x')
    body = d.t('#m-del .modal .body')
    foot = d.ts('.modal .foot button', '#m-del')
    c_strict = hdr == 'Are you sure?'
    c = (op and c_strict and x == '✕'
         and body == 'This action cannot be undone. This will permanently delete the line item.'
         and foot == ['Cancel', 'Delete'])
    rec('QA-DEL-1', 'PASS' if c else 'FAIL',
        f"open={op}; header text is {hdr!r} (spec: exactly 'Are you sure?') — the .x button lives inside <header>; "
        f".x={x!r}; body match={body=='This action cannot be undone. This will permanently delete the line item.'}; foot={foot}")

    # QA-DEL-2
    d.load()
    d.click('#st-normal .litable tbody tr:nth-child(2) .act-ic .del')
    op = d.has_class('#m-del', 'open')
    sku = d.p.evaluate("()=>document.querySelector('#st-normal .litable tbody tr:nth-child(2)').children[1].textContent.trim()")
    same = (d.t('#m-del .modal .body') == 'This action cannot be undone. This will permanently delete the line item.'
            and d.t('#m-del .modal header .x') == '✕' and 'Are you sure?' in d.t('#m-del .modal header'))
    rec('QA-DEL-2', 'PASS' if (op and same) else 'FAIL', f"open={op} row2 SKU={sku.splitlines()[0]!r} same copy={same}")

    # QA-DEL-3
    d.load()
    d.tab('2 · On Hold')
    d.click('#st-hold .litable tbody .act-ic .del')
    rec('QA-DEL-3', 'PASS' if d.has_class('#m-del', 'open') else 'FAIL',
        f"#m-del open from st-hold row = {d.has_class('#m-del','open')}; single shared modal (count of #m-del = "
        f"{d.n('#m-del')})")

    # QA-DEL-4
    d.load()
    d.click('.wf-tab[data-modal="m-del"]')
    d.click('#m-del .foot button:text-is("Cancel")')
    c = (not d.has_class('#m-del', 'open')) and d.n('.litable tbody tr', '#st-normal') == 4
    rec('QA-DEL-4', 'PASS' if c else 'FAIL', f"open after Cancel={d.has_class('#m-del','open')} rows={d.n('.litable tbody tr','#st-normal')}")

    # QA-DEL-5
    d.load()
    d.click('.wf-tab[data-modal="m-del"]')
    d.click('#m-del .modal header .x')
    c = (not d.has_class('#m-del', 'open')) and d.n('.litable tbody tr', '#st-normal') == 4
    rec('QA-DEL-5', 'PASS' if c else 'FAIL', f"open after ✕={d.has_class('#m-del','open')} rows={d.n('.litable tbody tr','#st-normal')}")

    # QA-DEL-6
    d.load()
    d.click('.wf-tab[data-modal="m-del"]')
    box = d.p.evaluate("""()=>{const o=document.querySelector('#m-del'),m=o.querySelector('.modal');
        const ro=o.getBoundingClientRect(),rm=m.getBoundingClientRect();
        return {x:ro.left+8,y:ro.top+8,inModal:(ro.left+8>=rm.left&&ro.left+8<=rm.right)};}""")
    d.p.mouse.click(box['x'], box['y'])
    d.p.wait_for_timeout(80)
    c = (not d.has_class('#m-del', 'open')) and d.n('.litable tbody tr', '#st-normal') == 4
    rec('QA-DEL-6', 'PASS' if c else 'FAIL',
        f"clicked overlay at ({box['x']:.0f},{box['y']:.0f}) inside modal={box['inModal']}; open={d.has_class('#m-del','open')} rows=4")


def main():
    with sync_playwright() as pw:
        br = pw.chromium.launch()
        pg = br.new_page(viewport={'width': 1680, 'height': 1000})
        d = P(pg)
        for fn in (qa_map, qa_ren, qa_sub, qa_group4, qa_hub, qa_cmt, qa_del):
            try:
                fn(d)
            except Exception as e:
                rec(fn.__name__, 'ERROR', f"{type(e).__name__}: {e}")
        br.close()

    order = {'PASS': 0, 'FAIL': 1, 'AMBIGUOUS': 2, 'UNRUNNABLE': 3, 'ERROR': 4}
    tally = {}
    for sid, v, ev in RESULTS:
        tally[v] = tally.get(v, 0) + 1
    if '--md' in sys.argv:
        print('| Scenario | Verdict | Evidence |')
        print('|---|---|---|')
        for sid, v, ev in RESULTS:
            print(f"| `{sid}` | **{v}** | {ev.replace('|', '\\|')} |")
    else:
        for sid, v, ev in RESULTS:
            print(f"{v:10} {sid}  {ev[:190]}")
    print('\nTOTAL', len(RESULTS), tally)


if __name__ == '__main__':
    main()
