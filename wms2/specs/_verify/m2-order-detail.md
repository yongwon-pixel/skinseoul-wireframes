# M2 — Adversarial QA execution · `specs/order-detail.md` §8

**Method 2 (hostile QA robot).** The executing agent did not author the spec, was given no
knowledge of the page beyond what §8 states, and was forbidden from improvising selectors or
expected strings.

- **Date:** 2026-08-03
- **Spec under test:** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-detail.md` §8
- **System under test:** `file:///Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/order-detail/index.html` (identical to the deployed GitHub Pages target named in §8.0)
- **Runner:** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_verify/qa-order-detail.py` (Playwright, headless Chromium, viewport 1680×1000)
- **Cross-check for culprit assignment:** `specs/_plans/_wireframe-fixes.md`

---

## 1. Methodology

### 1.1 Scope

§8 declares 147 scenarios, 68 of them `[WF]`. **All 68 `[WF]` scenarios were executed** — not a
sample — because a 25-scenario sample would have let the spec's failure modes hide in the
unexecuted tail. The 79 `[ADMIN]` scenarios were not attempted: every one of them requires a
backend (persistence, toasts, Web Audio, Slack, print agent), which §8.0 and §2.5 D correctly
declare out of reach for the wireframe. **None of the 68 `[WF]` scenarios turned out to be
`[ADMIN]`-in-disguise**, so the `[WF]`/`[ADMIN]` split itself is sound with exactly one exception
(QA-STA-4, below).

### 1.2 Execution rules

1. Every step used **only** the selector, label or string the spec supplies. Where the spec named
   a selector (`#st-normal .cmt-new textarea`), that selector was used verbatim.
2. §8.0's **state-scoping mandate** was obeyed: every assertion is prefixed with `#st-normal`,
   `#st-hold` or `#m-del`. This mandate is genuinely load-bearing and the spec is right to shout
   about it — unscoped `.c-item` returns 4, scoped returns 2.
3. §8.3's **execution order** was followed (MAP → REN → SUB → per-legend renders → HUB → CMT →
   DEL), with a fresh `page.goto()` before each mutating scenario as §8.3 step 6 instructs.
4. §8.0's **precondition** was honoured: annotations left visible (`Hide annotations` state).
5. Where the spec gives no instruction, the scenario is **AMBIGUOUS** and nothing was invented.

### 1.3 The one convention the runner had to invent (and why that is a spec defect)

§8 mixes two string registers and never defines them:

| Spec phrasing | Treated as |
|---|---|
| `reads exactly X` · `text is exactly X` · `value is X` | strict equality |
| `reading X` · `contains X` · `containing exactly X` | substring |

Text was normalised (`<br>` → space, whitespace collapsed, trimmed) because four `.litable`
headers are `Latest<br>Inventory Count`-style and `textContent` would otherwise yield
`LatestInventory Count`.

**This convention is not in the spec, and it changes verdicts.** Under a strict reading of
"reads exactly", eight further scenarios flip to FAIL — see §4 finding F-1.

### 1.4 Verdict definitions

- **PASS** — every Then-clause held.
- **FAIL** — spec asserts X, page does Y (both quoted).
- **AMBIGUOUS** — the spec does not say what to click or how to compare; not executable as written.
- **UNRUNNABLE** — impossible in a static mock and not tagged `[ADMIN]`. **Zero occurrences.**

---

## 2. Results

| Verdict | Count | Share of 68 |
|---|---|---|
| **PASS** | 63 | 92.6% |
| **FAIL** | 4 | 5.9% |
| **AMBIGUOUS** | 1 | 1.5% |
| **UNRUNNABLE** | 0 | 0% |

**Culprit split for the 4 FAILs: spec 4 · wireframe 0 · test-instruction 0.**
`_wireframe-fixes.md` registers no defect against `wms2/order-detail/index.html` (WF-1…WF-14 all
target other pages), and §2.5 A says so explicitly. Every failure is therefore an assertion the
spec got wrong about a page that is behaving as drawn — with one nuance on QA-STA-4, where the
spec asserts behaviour the wireframe never had and which is registered nowhere.

Notably, **not one scenario failed because a selector or label was missing or misspelled.** The
§8.0 claim that "every `[WF]` step uses a label or selector that exists on that page today" holds
for all 68. Every byte-level string in the spec that the runner could compare strictly — the
placeholder, `.liinfo`, the hold banner copy, the Actor Log's four rows, the 8 status values, the
14 column headers, the 5 edit-mode input values, the search result headers — matched the page
exactly.

---

## 3. Scenario table

Verdict · evidence quoted from the live run. Trailing digits in quoted text (e.g. `Inventory10`)
are annotation dots inside the asserted element — see finding F-1.

<!-- BEGIN GENERATED TABLE -->
| Scenario | Verdict | Evidence |
|---|---|---|
| `QA-MAP-1` | **PASS** | #st-normal .dot=13 #st-hold .dot=14 #m-del .dot=['M3'] .dot=28 legend .n=['1', '2', '3', '4', '5', '6', '12', '10', '11', '14', '13', '9', '7', '8'] |
| `QA-MAP-2` | **PASS** | h1='WMS 2.0 · Order Detail Wireframe' tabs=['Modal: Delete Line', '1 · Processing (default)', '2 · On Hold'] toggle='Hide annotations' |
| `QA-MAP-3` | **PASS** | load(norm,hold)=(True, False); after tab2 (hold,norm)=(True, False) scrollY=0 tabOn=[False, True]; after tab1=(True, False) |
| `QA-MAP-4` | **PASS** | toggled='Show annotations' no-anno=True anyDotVisible=False legendVisible=False; back='Hide annotations' dotsBack=True |
| `QA-MAP-5` | **PASS** | h3='Order Detail — Changes (specs 0 · A · C applied)' item9=True item14=True item10=True |
| `QA-MAP-6` | **PASS** | §2.3 maps 15/15 dots; §3 headings present for all=True; missing=[] |
| `QA-REN-1` | **PASS** | row1 rowspans/colspans ok=True (['', 'SKU', 'Image', 'Product Information (WooCommerce)', 'Inventory10', 'Actions']); row2=['Product Name11', 'Product Name KR', 'Size', 'Qty', 'Subtotal', 'Total', 'Latest Inventory Count', 'Inbound Status', 'Sourcing Route', 'Order Number', 'Order Date', 'Product Cost 🤖', 'Tracking Number', 'CP Link']; td counts=[18, 18, 18, 18] |
| `QA-REN-2` | **PASS** | forbidden header cells found=[] |
| `QA-REN-3` | **PASS** | LatestInventoryCount by SKU={'100005088': '12', '100005104': '0', '100012534': '0', '100043697': '0'} |
| `QA-REN-4` | **PASS** | sourcing tags=[{'cls': 'tag tag-jit', 'bg': 'rgba(0, 0, 0, 0)', 'fg': 'rgb(20, 16, 27)', 't': 'JIT (Coupang)'}, {'cls': 'tag tag-jit', 'bg': 'rgba(0, 0, 0, 0)', 'fg': 'rgb(20, 16, 27)', 't': 'JIT (Coupang)'}, {'cls': 'tag tag-wholesale', 'bg': 'rgba(0, 0, 0, 0)', 'fg': 'rgb(20, 16, 27)', 't': 'WHOLESALE'}, {'cls': 'tag tag-jit', 'bg': 'rgba(0, 0, 0, 0)', 'fg': 'rgb(20, 16, 27)', 't': 'JIT (Coupang)'}] |
| `QA-REN-5` | **PASS** | route cells=['JIT (Coupang)', 'JIT (Coupang)', 'WHOLESALE', 'JIT (Coupang)'] |
| `QA-REN-6` | **PASS** | <b> prefixes=[('Dr.Jart+', 'Dr.Jart+'), ('Dr.Jart+', 'Dr.Jart+'), ('Dr.Jart+', 'Dr.Jart+'), ('Dr.Jart+', 'Dr.Jart+')]; 닥터자르트 on page=False |
| `QA-REN-7` | **PASS** | sku/qty asterisks ok=True; .liinfo match=True |
| `QA-REN-8` | **PASS** | h4='Inbound / Outbound Actor Log — New' th=['Time', 'Action', 'SKU', 'Qty', 'Operator', 'Note'] rows_match=True |
| `QA-REN-9` | **PASS** | thead=['Provider Order ID', 'Tracking Number', 'Status', 'Status Description', 'Created At', 'Updated At'] row=['YT2618100709331860', '34YEM055929401000910906', 'DELIVERED', 'Shipment information received', '6/30/2026, 8:55:53 PM', '7/13/2026, 10:10:32 AM'] lastmile='Last mile: AustraliaPost' minih=['SHIPMENT DETAILS', 'TRACKING HISTORY (synced 7/16/2026, 4:51:40 AM)6'] nodes=['DELIVERED', 'DELIVERY_ATTEMPT', 'IN_TRANSIT_CARRIER', 'ORDER_CREATION'] |
| `QA-REN-10` | **PASS** | line tracking='10323100835456' shipment tracking='34YEM055929401000910906' (separate tables/headers) |
| `QA-REN-11` | **PASS** | carrier='YUN' buttons=['✎ Change Tracking #', 'Reset Order'] |
| `QA-REN-12` | **PASS** | OrderDate='2026-06-30 SGT' CreatedAt='30/06/2026 19:55:28 SGT' log=['07-01 09:32', '07-01 09:10', '07-01 08:58', '06-30 20:15'] cmt=['07-13 10:42', '07-13 10:55'] ship=['6/30/2026, 8:55:53 PM', '7/13/2026, 10:10:32 AM'] |
| `QA-SUB-1` | **PASS** | st-normal=[('← Back to Orders', 'back'), ('↻ Audit History', 'link-btn'), ('↗ View in WP', 'link-btn blue'), ('⧉ Clone Order', 'link-btn blue'), ('✕ Cancel Order', 'link-btn red')]; st-hold match=True |
| `QA-SUB-2` | **PASS** | h2='Order # 407847' carrier='YUN' buttons=['View Label', '🖨 Print', 'Change Status ▾'] |
| `QA-SUB-3` | **PASS** | PIC='Egita ✎ Edit5' button='✎ Edit' borderStyle=solid |
| `QA-SUB-4` | **PASS** | PIC controls per state=[[{'btn': '✎ Edit', 'bareSpan': False}], [{'btn': '✎ Edit', 'bareSpan': False}]] |
| `QA-SUB-5` | **PASS** | headings=[{'h': '📋 Order Information', 'edit': None}, {'h': '👤 Billing Address ✎', 'edit': '✎'}, {'h': '🚚 Shipping Address ✎', 'edit': '✎'}] TaxID='–' ShortAddr='–' Email='m.saltoon@gmail.com' |
| `QA-SUB-6` | **PASS** | st-normal tq='Total Quantity: 4' st-hold tq='Total Quantity: 4' addBtn=['+ Add Line Item'] |
| `QA-SUB-7` | **PASS** | nav={'brand': 'SkinSeoul', 'spans': ['Operation AI ▾', 'Catalog Management ▾', 'OMS Center ▾', 'Site Management ▾', 'Customer Management ▾', 'SkinSeoul WP Admin'], 'cmt': '💬 Comments2', 'user': 'YYongwon Ryu', 'avatar': 'Y', 'logout': 'Logout', 'order': ['brand', 'SPAN', 'SPAN', 'SPAN', 'SPAN', 'SPAN', 'SPAN', 'sp', 'SPAN', 'user', 'logout', 'inboxdd']} |
| `QA-SUB-19` | **PASS** | discount='AUD 13.11' amount='AUD 129.8' costs=['', '₩17,100', '₩22,425', '₩30,630'] USD-on-page=False |
| `QA-INB-1` | **PASS** | rows=4 tags=['INBOUNDED', 'INBOUNDED', 'INBOUNDED', 'INBOUNDED'] row1cls='row-edit' row1acts=['✓', '✕'] |
| `QA-INB-2` | **PASS** | 100043697='PENDING' acts=['Inbound', '✎', '🗑']; 100005088/100012534 INBOUNDED+CancelInbound ok |
| `QA-INB-3` | **FAIL** | 'Request Inbound' found in: ['legend']; legend text: '2Inbound buttons reworked — per-row Inbound / Cancel Inbound (same grammar as View Orders, per product) + bottom Bulk Inbound Selected Items (checkbox'; forbidden header cells=[] |
| `QA-INB-4` | **PASS** | st-normal footer order=['Total Quantity: 4', 'Bulk Inbound Selected Items2', '📦 Outbound9', '+ Add Line Item']; st-hold=['Total Quantity: 4', 'Bulk Inbound Selected Items2', '📦 Outbound9', '+ Add Line Item'] (trailing digits = annotation dots) |
| `QA-INB-5` | **PASS** | select-all=1 row checkboxes=4 |
| `QA-OUT-1` | **PASS** | #obBtn={'t': '📦 Outbound', 'c': 'btn btn-green btn-sm', 'dis': False} |
| `QA-OUT-2` | **PASS** | grayBtn={'t': '📦 Outbound', 'dis': True, 'op': '0.55', 'cur': 'not-allowed', 'rawStyle': 'opacity:.55;cursor:not-allowed', 'id': ''}; banner text (incl. dot)='⏸ On Hold by urgent CS request — inbound still allowed, but Outbound disabled. Release the hold (Change Status) to ship14'; pending row={'tag': 'PENDING', 'btn': ['Inbound\|btn btn-green btn-sm', '✎\|edit', '🗑\|del']} |
| `QA-OUT-3` | **FAIL** | 'Outbound to Deleo BaroShip' found in: ['legend']; legend #9 = '9"Outbound to Deleo BaroShip" → relabeled to "Outbound" (non-Deleo cases are the majority). Enabled only when every item'; footer labels=['📦 Outbound', '📦 Outbound'] |
| `QA-STA-1` | **PASS** | visible=True items=['pending', 'processing', 'on-hold', 'completed', 'refunded', 'failed', 'shipped', 'prepare-shipment'] processing.on=True |
| `QA-STA-2` | **PASS** | forbidden dropdown items=[]; ✕ Cancel Order class='link-btn red' |
| `QA-STA-3` | **PASS** | visible=True on-hold.on / processing.on = [('processing', False), ('on-hold', True)] |
| `QA-STA-4` | **FAIL** | dropdown visible before background click=True, after=True; badge='Processing'; page has document-level click handler=False |
| `QA-STA-5` | **PASS** | state1={'t': 'Processing', 'c': 'status st-processing', 'banner': False}; state2={'t': 'On Hold', 'c': 'status st-hold'}; banner visible=True |
| `QA-STA-6` | **AMBIGUOUS** | spec says the listed blocks are 'identical' but never states the comparison basis (DOM? text? attributes?). Text-level result: {'nav': True, 'subbar': True, 'info3': True, 'cmt': True, 'ft': True, 'log': True, 'rows': True, 'row2differs': True}. Undeclared 6th diff at DOM level: ids ['inbox1', 'ordStatus', 'statusdd', 'addCmt', 'obBtn'] vs ['inbox1H', 'statusddH', 'holdBannerH', 'addCmtH'] (inbox1/inbox1H, statusdd/statusddH, addCmt/addCmtH) — the spec's enumeration of 5 diffs omits them even though other [WF] scenarios depend on those very ids. |
| `QA-EDIT-1` | **PASS** | inputs=5 values match=True; Today btn={'t': 'Today', 'below': True} |
| `QA-EDIT-2` | **PASS** | {'ok': '✓', 'no': '✕', 'cancel': False, 'edit': False, 'del': False} |
| `QA-EDIT-3` | **PASS** | input count per commerce cell={'SKU': 0, 'Product Name': 0, 'Product Name KR': 0, 'Size': 0, 'Qty': 0, 'Subtotal': 0, 'Total': 0, 'Latest Inventory Count': 0, 'Inbound Status': 0, 'Sourcing Route': 0} |
| `QA-EDIT-4` | **PASS** | cells=['0', 'INBOUNDED', 'JIT (Coupang)', '12101316464794', '2026-06-30', '₩17,100', '10323100835456', 'coupang…7923'] inputs=0 |
| `QA-EDIT-5` | **PASS** | [{'edit': '✎', 'del': '🗑', 'modal': 'm-del'}, {'edit': '✎', 'del': '🗑', 'modal': 'm-del'}, {'edit': '✎', 'del': '🗑', 'modal': 'm-del'}] |
| `QA-PRT-1` | **PASS** | 🖨 Print present=True carrier='YUN' forbidden strings=[] |
| `QA-PRT-2` | **PASS** | otitle buttons per state=[['View Label', '🖨 Print', 'Change Status ▾'], ['View Label', '🖨 Print', 'Change Status ▾']] |
| `QA-HUB-1` | **PASS** | open=True placeholder ok=True tabs=['@ Mentions 2', '★ Saved'] (note: tab 1 text is '@ Mentions 2', not bare '@ Mentions') paneheader='Comments mentioning me · Click to open the order Mark all read' |
| `QA-HUB-2` | **PASS** | navBadge='2' tabBadge='2' unread=2 third unread=False ('Order 407790 · Kai: "Resolved" Yesterday★') |
| `QA-HUB-3` | **PASS** | saved display=block header='Saved comments · Click to open the order Unstar to remove' items=['Order 407812 · Miranti: "@Yongwon 1 JIT item not yet inbounded" 09:15★'] star.on=True mentions display=none |
| `QA-HUB-4` | **PASS** | tabs display on search=none; header='1 results · newest first · click to open the order'; hits=['Order 407812 · Miranti: "@Yongwon 1 JIT item not yet inbounded" Today 09:15']; marks=['Miranti']; zzzz pane='0 results · newest first · click to open the orderNo matching comments' its=0; restore: tabs=flex activeTab=mentions pane=block |
| `QA-HUB-5` | **PASS** | header='1 results · newest first · click to open the order' item=['Order 407301 · Dean: "Repacked and shipped" 7/26 14:10'] |
| `QA-HUB-6` | **PASS** | sachet: '1 results · newest first · click to open the order' ['Order 407688 · Aldo: "Customer note checked — sachet included" Yesterday 09:40'] marks=['sachet']; dean: '2 results · newest first · click to open the order' order=['Order 407847 · Dean: "', 'Order 407301 · Dean: "'] |
| `QA-HUB-7` | **PASS** | pane='0 results · newest first · click to open the orderNo matching comments' child tags=['DIV', 'DIV'] |
| `QA-HUB-8` | **PASS** | open=True placeholder ok=True tabs=['@ Mentions 2', '★ Saved'] badge='2' mentionItems=3 |
| `QA-CMT-1` | **PASS** | placeholder match=True addBtn='Add Comment' hideBtn='Hide Comments' |
| `QA-CMT-2` | **PASS** | [{'who': 'Dean', 'at': '@Yongwon', 'body': '@Yongwon Please pack this order with extra care — repeat-purchase VIP customer.', 'time': '07-13 10:42', 'star': False}, {'who': 'Yongwon', 'at': '@Dean', 'body': "@Dean Got it. I'll add extra bubble wrap.", 'time': '07-13 10:55', 'star': True}] |
| `QA-CMT-3` | **PASS** | rows=3 last={'who': 'Yongwon', 'body': 'Checked the sachet count', 'time': 'Just now'} textarea='' st-normal.on=True tab.on=True st-hold rows=2 |
| `QA-CMT-4` | **PASS** | after empty click=2; after 3 spaces=2 |
| `QA-CMT-5` | **PASS** | {'at': '@Dean', 'rest': 'please double-bag this', 'restInAt': ['@Dean']} |
| `QA-CMT-6` | **PASS** | initial on=False after click1=True after click2=False |
| `QA-CMT-7` | **PASS** | placeholder same=True addCmtH='Add Comment' rows=[['Dean', '07-13 10:42'], ['Yongwon', '07-13 10:55']] |
| `QA-DEL-1` | **FAIL** | open=True; header text is 'Are you sure?✕' (spec: exactly 'Are you sure?') — the .x button lives inside <header>; .x='✕'; body match=True; foot=['Cancel', 'Delete'] |
| `QA-DEL-2` | **PASS** | open=True row2 SKU='100043697(100043697*)' same copy=True |
| `QA-DEL-3` | **PASS** | #m-del open from st-hold row = True; single shared modal (count of #m-del = 1) |
| `QA-DEL-4` | **PASS** | open after Cancel=False rows=4 |
| `QA-DEL-5` | **PASS** | open after ✕=False rows=4 |
| `QA-DEL-6` | **PASS** | clicked overlay at (8,8) inside modal=False; open=False rows=4 |
<!-- END GENERATED TABLE -->

---

## 4. Findings

### F-1 · Annotation dots poison every "reads exactly" assertion (systemic, 8 scenarios)

**Severity: high — this is the one defect that would make an unaided AI file false bugs at scale.**

§8.0 mandates "annotations visible" as a precondition for every `[WF]` scenario. But the purple
`.dot` spans live **inside** the very elements the spec asserts exact text on. Measured:

| Scenario | Spec says | Page renders |
|---|---|---|
| `QA-DEL-1` | header "text is exactly `Are you sure?`" | `Are you sure?✕` — **FAIL** |
| `QA-REN-1` | second header row "reads, in order: `Product Name`, …" | `Product Name11` |
| `QA-REN-1` | "a `th[colspan="8"]` reading `Inventory`" | `Inventory10` |
| `QA-OUT-2` / `QA-STA-5` | `#holdBannerH` "containing exactly `⏸ On Hold … to ship`" | `…to ship14` |
| `QA-REN-9` | "the tracking heading reads `TRACKING HISTORY (synced 7/16/2026, 4:51:40 AM)`" | `…4:51:40 AM)6` |
| `QA-SUB-3` | "`PIC` = `Egita` followed by a bordered button" | `Egita ✎ Edit5` |
| `QA-INB-4` | footer contains "a button labelled exactly `Bulk Inbound Selected Items`" | sibling text `Bulk Inbound Selected Items2` |
| `QA-HUB-1` | "`#inbox1 .tabs button` returns 2 buttons reading `@ Mentions` and `★ Saved`" | `@ Mentions 2` (badge is a child) |

Seven of these pass **only** because the runner chose substring matching. A different agent
choosing equality — which the words "reads exactly" invite — reports 8 failures against a
correct wireframe. The spec must either (a) state the normalisation contract in §8.0, or (b)
scope the assertions (`header` text node, `th` minus `.dot`), or (c) change the precondition to
`Show annotations` for exact-string scenarios.

### F-2 · `QA-OUT-3` and `QA-MAP-5` directly contradict each other (blocking)

- `QA-MAP-5` **requires**: "the legend item numbered `9` contains the strings
  `"Outbound to Deleo BaroShip"`, `Outbound`, and `Enabled only when every item is INBOUNDED`".
- `QA-OUT-3` **requires**: "the string `Outbound to Deleo BaroShip` appears **nowhere** in the
  rendered page in either state or the legend body text describing the current label".

Measured legend #9: `"Outbound to Deleo BaroShip" → relabeled to "Outbound" (non-Deleo cases are
the majority). Enabled only when every item is INBOUNDED`.

Both are `[WF]`. Both cannot pass. The trailing qualifier in QA-OUT-3 ("or the legend body text
describing the current label") is not parseable as an exemption — it reads as an *extension* of
the prohibition. An AI running §8 top-to-bottom finds QA-MAP-5 green and QA-OUT-3 red on the same
sentence and has no way to resolve it without asking.

### F-3 · `QA-INB-3` forbids a string the spec's own §10.2 requires (blocking)

`QA-INB-3`: "the string `Request Inbound` appears **nowhere** in the rendered page in either
state, **including the legend**."

Measured legend #2: `…"Request Inbound" name retired; unclickable-button bug fixed…`

§10.2's removed-features table names `QA-INB-3` as the assertion for the retired "Request Inbound"
button — but the legend's job is precisely to *say* the name was retired. The prohibition must
target the **rendered control set** (button labels and `.litable` header cells), not page text.
Its second clause already does this correctly ("no header cell of `.litable` reads
`Inbound Request`") and passes.

### F-4 · `QA-STA-4` is mis-tagged `[WF]` — the behaviour does not exist on this page

`QA-STA-4`: "**Given** `#statusdd` is open · **When** I click the page background · **Then** the
dropdown is no longer visible."

Measured: dropdown visible before background click = `True`, **after = `True`**. The wireframe has
**no** document-level click handler — verified by grep across all ten `wms2/*/index.html` files:
only `ready-to-outbound/index.html` has one. `order-detail/index.html` has zero.

This is not a registered wireframe defect (§2.5 A: "No `_wireframe-fixes` entry … targets
`wms2/order-detail/index.html`"), and §2.5 D's demo-limitation list does not mention it either —
that list covers *handlers that do nothing*, not *dismissal that does not happen*. The status
badge and the "no toast" clauses of QA-STA-4 both hold; only the dismissal fails.

Three fixes are acceptable and the spec must pick one: retag `[ADMIN]`, register a new
`[WF-15] order-detail — status dropdown does not close on outside click` and keep the scenario
red until the wireframe is patched, or add the handler.

*(Interesting contrast: the modal's three dismissal paths — footer `Cancel`, header `✕`, backdrop
click — all work and all three scenarios QA-DEL-4/5/6 pass. The wireframe implements
`overlay.addEventListener('click', e => {if(e.target===o)…})` for the modal but nothing equivalent
for the dropdown. The spec assumed symmetry that the drawing does not have.)*

### F-5 · `QA-STA-6` states no comparison basis (AMBIGUOUS)

"the nav, subbar, address panels, comments thread, Fulfillment Tracking block, Actor Log rows and
the other three line rows are **identical** between `#st-normal` and `#st-hold`" — identical how?
Text? DOM? Attributes?

Under **text** comparison every enumerated block is identical (`nav:True subbar:True info3:True
cmt:True ft:True log:True rows:True`) and row 2 correctly differs. Under **DOM** comparison there
is an undeclared **sixth** diff the spec's list of five omits:

```
#st-normal ids: inbox1, ordStatus, statusdd, addCmt, obBtn
#st-hold  ids: inbox1H, statusddH, holdBannerH, addCmtH
```

`inbox1`/`inbox1H`, `statusdd`/`statusddH`, `addCmt`/`addCmtH` are systematically renamed, and
§8's own scenarios (QA-HUB-8, QA-STA-3, QA-CMT-7) depend on exactly those renames. So the
sentence "nothing else changes" is false at the level the rest of §8 operates on. Also note
`#ordStatus` exists only in State 1 — State 2's badge has no id, which QA-STA-5 quietly
accommodates by switching selector to `#st-hold .status` without saying why.

### F-6 · Minor: `QA-MAP-3`'s scroll assertion is vacuous as written

"the window scroll position is `0`" after clicking the tab. On a fresh load the page is already at
0, so the assertion passes without testing anything. The runner scrolled to y=600 first to make it
meaningful (and it then passed — `window.scrollTo({top:0})` fires). The spec should say "scroll
down, then switch tabs".

### F-7 · Minor: `QA-REN-3`'s third clause is not an assertion

"a `0` on a JIT line **must not** be reported as a defect — it is the expected value" is guidance
to the human reading the report, not a machine-checkable Then-clause. Harmless, but it inflates
the clause count. Same pattern in `QA-REN-8`'s closing parenthetical (which is, in fairness, the
single most useful sentence in §8 — it pre-empts exactly the three false bugs an AI would file
against the Actor Log demo data).

---

## 5. Spec fixes required

Ordered by damage.

| # | Fix | Location | Why |
|---|---|---|---|
| **1** | Resolve the `Outbound to Deleo BaroShip` contradiction. Rewrite QA-OUT-3's first clause as: "no **button label** in either state reads `Outbound to Deleo BaroShip`; the legend's historical reference in item 9 is expected and is asserted by QA-MAP-5." | §8 QA-OUT-3 | Two `[WF]` scenarios currently cannot both pass. F-2 |
| **2** | Rewrite QA-INB-3's first clause to target controls, not page text: "no button label and no `.litable` header cell in either state reads `Request Inbound`. The legend's 'name retired' sentence is expected." | §8 QA-INB-3 | Spec forbids a string §10.2 requires. F-3 |
| **3** | Fix QA-STA-4: either retag `[ADMIN]`, or register `[WF-15]` in `_wireframe-fixes.md` and add the outside-click handler to `order-detail/index.html`. Then update §2.5 A, which currently asserts no wireframe defect touches this page. | §8 QA-STA-4 · §2.5 A · `_wireframe-fixes.md` | Asserts behaviour the page has never had. F-4 |
| **4** | Add a **text-normalisation contract** to §8.0, mirroring the state-scoping table: `<br>` → space; collapse whitespace; **annotation `.dot` text is excluded from every string assertion**; "reads exactly" = equality after normalisation, "reading" = substring. | §8.0 | Without it, 8 scenarios flip verdict on the runner's private convention. F-1 |
| **5** | Fix QA-DEL-1's header clause: "`#m-del .modal header`'s first text node is exactly `Are you sure?`" (the `.x` button is a child of `header`, which the same clause acknowledges). | §8 QA-DEL-1 | Only FAIL that is a pure wording slip. F-1 |
| **6** | Give QA-STA-6 a comparison basis, and extend its diff list from 5 to 6 by adding: "(6) the state-suffixed ids — `inbox1`/`inbox1H`, `statusdd`/`statusddH`, `addCmt`/`addCmtH` — plus `#ordStatus`, which exists only in State 1." | §8 QA-STA-6 | Currently not executable; "nothing else changes" is false. F-5 |
| **7** | QA-MAP-3: prepend "scroll the page down" before the tab click. | §8 QA-MAP-3 | Vacuous assertion. F-6 |
| **8** | QA-HUB-1: change "2 buttons reading `@ Mentions` and `★ Saved`" to "…whose labels **begin with** `@ Mentions` and `★ Saved` (the Mentions tab carries an inline `.badge-n`, asserted by QA-HUB-2)". | §8 QA-HUB-1 | Removes the last exact/contains trap. F-1 |

**Not fixes — confirmed correct and worth protecting:**

- The §8.0 **state-scoping table** is the single highest-value paragraph in the section. Without it
  every count assertion would have been silently wrong.
- §2.5 B (Actor Log demo-data inconsistencies) and §2.5 D (demo limitations) successfully
  suppressed roughly a dozen false bug reports the runner would otherwise have filed.
- §8.3's execution order is real: QA-CMT-3 and QA-CMT-5 do permanently append rows, and QA-HUB's
  `[data-pane="csr"]` element does persist once created. Both warnings are accurate.
- Every byte-accurate string claim that could be tested strictly held — including the 89-character
  composer placeholder, the 213-character `.liinfo` note, the hold banner, all 8 status values,
  all 14 column headers, all 5 edit-input values and all three search-result headers.

---

## 6. Verdict — can an AI run this spec's QA unaided?

**yes-with-caveats.**

63 of 68 `[WF]` scenarios executed to a clean PASS with **zero questions asked** — no missing
selector, no missing label, no unresolvable string. That is the bar §8.0 sets, and the section
very nearly clears it.

The caveats are real but bounded and all editorial:

- An unaided agent files **4 false bug reports** (QA-INB-3, QA-OUT-3, QA-DEL-1 and, more
  defensibly, QA-STA-4) against a wireframe that is behaving as drawn.
- It **deadlocks** on QA-MAP-5 vs QA-OUT-3 — the same sentence is simultaneously required and
  forbidden — and must escalate.
- It **must ask one question** to run QA-STA-6 ("identical how?").
- Depending on how it reads "reads exactly", it files **up to 8 more** false reports from
  annotation-dot pollution.

None of these needs product knowledge to fix; all eight fixes in §5 are text edits to §8 plus one
one-line decision on QA-STA-4. After them, the answer becomes an unqualified yes.
