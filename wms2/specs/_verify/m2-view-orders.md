# Method 2 — Adversarial QA Execution: `view-orders.md` §8

**Target spec** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/view-orders.md` §8 (QA Acceptance Criteria)
**System under test** `file:///Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/view-orders/index.html` (identical to the deployed page)
**Runner** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_verify/qa-view-orders.py` (Playwright, headless Chromium, 1280×900, `file://`, page reloaded between every scenario)
**Date** 2026-08-03 · **Posture** hostile QA robot; did not author the spec; executed only what §8 literally says.

---

## 1. Methodology

1. **Extraction.** Every scenario in §8.1–§8.13 tagged **[WF]** was extracted. Count = **135**, which matches the spec's own §8.14 claim of 135 `[WF]`. **All 135 were attempted** — not a sample. (The 137 `[ADMIN]` and 1 DEFERRED scenarios were correctly excluded as out of scope for a static mock.)
2. **Execution.** Each scenario was implemented from the spec text alone: the chrome-tab labels, element IDs, class names, and expected strings written in §8, plus the eight execution rules in §8.0. Where §8 does not name a control or an assertion, the scenario was recorded **AMBIGUOUS** and nothing was improvised from independent knowledge of the page.
3. **Isolation.** `page.goto()` before every scenario (§8.0 rule 4). State switching by exact chrome-tab `textContent` (§8.0 rule 1). Queries scoped per §8.0 rule 5.
4. **Two harness passes.** v1 executed §8 with the most literal possible reading. v1 produced 42 FAIL + 2 ERROR. Triage of those failures against the DOM separated **spec defects** from **harness defects of my own** (wrong visibility predicate for `position:fixed` elements, `.mfoot,footer` guess where the page uses `.foot`, counting the log table's in-`tbody` header row as data). v2 fixed only the harness defects and re-ran; every remaining failure is reproducible and attributable. The committed script is v2.
5. **Text-comparison convention — and the first thing that broke.** §8.0 rule 6 says a scenario saying *exactly* means "compare the trimmed string byte-for-byte." That rule is not satisfiable for any element with child nodes: source indentation newlines land inside `textContent`. This harness therefore grades on **whitespace-collapsed** equality (the only workable reading) and reports byte-for-byte separately. Grading on the literal rule would have added ~40 further false FAILs. **This is itself finding S-0.**
6. **Culprit assignment.** For every FAIL: cross-checked `_plans/_wireframe-fixes.md`. A failure that matches a listed WF defect is a **wireframe** fault (spec correct). Everything else was traced to the exact spec sentence that cannot be executed as written.

### Verdict definitions used
- **PASS** — the Then-clause held, using only what the spec supplied.
- **FAIL** — the page did something other than what the spec asserts; both quoted.
- **AMBIGUOUS** — §8 does not say what to click or what to assert precisely enough to run.
- **UNRUNNABLE** — the assertion is impossible in a static mock and the scenario is **not** tagged `[ADMIN]`.

---

## 2. Results

| Verdict | Count | % of 135 |
|---|---|---|
| **PASS** | **103** | 76.3 % |
| **FAIL** | **29** | 21.5 % |
| **AMBIGUOUS** | **2** | 1.5 % |
| **UNRUNNABLE** | **1** | 0.7 % |

### Culprit split for the 29 FAILs

| Culprit | Count | Detail |
|---|---|---|
| **(a) Spec** | **28** | 21 × annotation-chrome pollution (S-1) · 2 × `Deleo` legend sweep (S-2) · 1 × wrong selector `#s2 tbody tr` (S-3) · 1 × class-on-span vs "cell" (S-4) · 1 × self-contradiction with QA-S6-02 (S-5) · 1 × self-contradiction with QA-S1-10 (S-6) · 1 × mis-quoted fragment (S-7) |
| **(b) Wireframe** | **1** | QA-S6-07 — defect **WF-1**, already logged in `_wireframe-fixes.md`. The spec *predicts* this failure verbatim. Spec is right, wireframe is wrong. |
| **(c) Test-instruction defect (mine)** | **0** | 4 harness defects existed in v1 and were fixed in v2; none remain. |

Plus 1 UNRUNNABLE (S-8) and 2 AMBIGUOUS (S-9, S-10) — all three are spec faults.

**Net: 32 of 135 [WF] scenarios (23.7 %) cannot be executed to a correct verdict from the spec alone.**

---

## 3. Findings — spec fixes required

Ordered by blast radius.

### S-1 — §8.0 has no rule for wireframe annotation chrome. Breaks 21 scenarios. **Most damaging.**
The page injects `<span class="dot">` annotation markers *inside* buttons, `<th>`, `<td>`, banners and notes, and every modal `<header>` ends with `<button class="x">✕</button>`. Both land in `textContent`. §8.0 rule 8 explicitly forbids the workaround (`Do not click Hide annotations`).

Result: an assertion whose content is 100 % correct still fails.

| Spec says | Page returns |
|---|---|
| QA-S1-01: SKU cell reads `100005104` | `1000051045` |
| QA-S1-03: button text is exactly `Inbound + Outbound` | `Inbound + Outbound8` |
| QA-S1-13: header `Product Name`, `Sourcing Route`, `Location` | `Product Name18`, `Sourcing Route6`, `Location17` (State 1 only) |
| QA-S6-04: `.scannote` is exactly `Now scan product barcodes — …` | `4 Now scan product barcodes — …` |
| QA-S6-05: header `Expected Qty` / `Received Qty` / `Location` | `Expected Qty9` / `Received Qty6` / `Location7` |
| QA-M1-01: header is exactly `Cancel Inbound — 100038120` | `Cancel Inbound — 100038120✕` |
| QA-M4-01: header is exactly `Print Return Labels — 2 Selected Products (Supplier Return)` | same + `✕` |
| QA-S4-01 / QA-S5-01: banner body ends `… Tracking 10322198837710` | `… Tracking 10322198837710 1` |
| QA-S6-19: `.note` is exactly `Cursor returns to the search box …` | `2 Cursor returns to the search box …` |

Affected: QA-S1-01, S1-03, S1-13, S2-03, S3-01, S3-02, S3-03, S4-01, S4-06, S5-01, S5-02, S6-04, S6-05, S6-12, S6-15, S6-19, M1-01, M2-01, M2-10, M4-01, CV-12. **Every one passes once `.dot` and `header > button.x` are stripped.**

**Fix:** add to §8.0 as rule 6b — *"Before any text comparison, remove every `.dot` descendant and, inside a modal `<header>`, the trailing `button.x`. This is wireframe annotation chrome and is not part of the asserted string. Locate controls by this normalized text too."*

### S-0 — §8.0 rule 6's "byte-for-byte" is not satisfiable. Would break ~40 more.
`textContent` of any multi-node element carries the source's newlines and indentation. Byte-for-byte trimmed comparison therefore fails on almost every banner, note and `.cnt` string even when the visible text is identical.
**Fix:** rule 6 should read *"collapse runs of whitespace on both sides; `exactly` means the collapsed strings are equal, including `·`, `—`, `→`, `✓`, `⟲`, `⏸`, `📦`, `🖨`, `▸`, `▾` and Korean characters."* The parenthetical shows this was the intent; the wording says otherwise.

### S-2 — the `Deleo` sweeps are falsified by the spec's own legend. Breaks QA-S1-09 and QA-NG-08.
Both assert `Deleo` appears **0** times in `document.body.innerText`. State 1's legend contains, visibly: `Label changed from "Outbound to Deleo Baroship" to "Outbound" — C Behavior`. `innerText` sees it (verified: 1 hit in `s1`, 0 in all other states). It disappears only under `body.no-anno`, which §8.0 rule 8 forbids.
**Fix:** scope the sweep — *"…`Deleo` appears 0 times in `document.body.innerText` after excluding `.legend` subtrees (the legend documents the removal by name)."*

### S-3 — `#s2 tbody tr` is the wrong selector. Breaks QA-S2-01.
Spec: *"all four `#s2 tbody tr`"*. Actual: **9**, because States 1–5 render two tables (`table.tbl` + `table.logtbl`) and the log table's header row also lives inside `<tbody>`. Scoped to `#s2 table.tbl tbody tr` the count is 4 and the assertion passes.
Same latent trap in QA-S1-14/15/16, QA-S3-03, QA-CV-05, QA-CV-06 — those scenarios don't quote a selector, so a QA agent will guess, and the naive guess is wrong.
**Fix:** replace every bare `#sN tbody tr` with `#sN table.tbl tbody tr`, and add to §8.0 rule 5: *"States 1–5 contain two tables. The product grid is `table.tbl`; the Actor Log is `table.logtbl` and puts its header row inside `<tbody>` — count log rows as `tbody tr` having ≥1 `<td>`."*

### S-4 — QA-S1-12 asserts a class on the wrong node.
Spec: *"the `Qty` cell showing `2` … has class `qty-warn`, and every cell showing `1` has class `qty`."* The `<td>` carries `class=""` or `class="anno"`. The classes live on a child `<span>`: `<td><span class="qty qty-warn">2</span></td>`. The assertion is true of the span, false of the cell.
**Fix:** *"the `Qty` cell's `span` showing `2` has class `qty qty-warn`…"*

### S-5 — QA-NG-10 contradicts QA-S6-02.
QA-NG-10: *"no element has an `onclick` or `href` that triggers a full navigation of the current document."* QA-S6-02 **requires** `#s6 .intbanner a` to have `href` ending `../inbound-request/index.html#reqlist` — a cross-document navigation, and the page's only anchor. The two cannot both pass.
**Fix:** carve out the cross-page deep links `[G-12]`: *"…except the cross-page links required by QA-S6-02 and `[G-12]`."*

### S-6 — QA-CV-18 contradicts QA-S1-10.
QA-CV-18: *"every route label renders as bold uppercase text with a transparent background."* QA-S1-10 requires the badge text to be exactly `JIT (Coupang)` — mixed case, and the page applies no `text-transform`. Transparent-background and bold both hold; **uppercase** fails on 6 elements across States 1, 1b, 2, 3, 5.
**Fix:** drop "uppercase" or restate as *"bold text on a transparent background (route labels are rendered in their canonical casing, e.g. `JIT (Coupang)`)."*

### S-7 — QA-S6-14 mis-quotes the wireframe.
Spec quotes the fragment `the request list qty cell shows the edit history (300→120)`. The modal says `The request list qty cell shows the edit history (300→120).` — sentence-initial capital. Literal substring match fails; case-insensitive passes. The other three quoted fragments in the same scenario match exactly.
**Fix:** capitalize the quoted fragment.

### S-8 — QA-S6-10 is tagged [WF] but §2.3 L-13 says it is [ADMIN]. → UNRUNNABLE.
§2.3 **L-13**: *"The floating-save button (`.flsave`) is attached only to `.shelf input` and `.locin`. It is **not** attached to `.qtyin` … so that assertion is `[ADMIN]`."* But QA-S6-10 is tagged **[WF]** and asserts precisely that: set `#s6 tbody tr:nth-child(2) input.qtyin` to `130`, dispatch `input`, expect `button.flsave` with text `Save`. Verified: **0** visible `.flsave` appears. QA-S6-11 (the `.locin` twin) passes.
**Fix:** retag QA-S6-10 as `[ADMIN]`, or split it into a `[WF]` negative documenting L-13 (as QA-S1-20 does for L-4 and QA-LG-03 does for L-3) plus an `[ADMIN]` positive. Note this also breaks the §8.14 counts: 135/137 becomes 134/138.

### S-9 — QA-GL-02 gives no observable assertion. → AMBIGUOUS.
*"the send-sound handler is bound to every `button` whose text matches `/Outbound/` … Assert the binding rule only."* Listeners added via `addEventListener` are not enumerable from page script, and the spec names no attribute, class or marker to check.
**Fix:** either retag `[ADMIN]`, or make it inspectable — e.g. *"every such button carries `data-sound="send"`"* (requires a wireframe change), or assert against the inline `<script>` source text.

### S-10 — QA-CV-11 asserts legend semantics with no quoted string and no index. → AMBIGUOUS.
*"legend entry 4 states the qty-without-location confirm block, legend entry 5 states that the unified search auto-detects return barcodes."* No verbatim string, and no selector for addressing "legend entry N". Only the third clause (search input value `10322198837710`) is executable — it passes. QA-CV-07/08/09/10 do this correctly by quoting the text; CV-11 should follow them.
**Fix:** quote the two legend sentences verbatim, as CV-07/08/09/10 do.

### S-11 — "visible" is never defined (advisory; no FAIL, but cost a full harness pass).
~15 scenarios say "becomes visible" / "is not visible". `#scanfloat`, `#unrecToast` and `#gtoast` are `position:fixed`, for which the natural `offsetParent !== null` test is always false — a QA agent will get three false FAILs (QA-LG-03, QA-M2-04, QA-M2-12) before working this out. §8.0 defines conventions for text (rule 6) and colour (rule 7) but not visibility.
**Fix:** add rule 7b — *"'visible' means `el.getClientRects().length > 0`; `offsetParent` is not a valid test on this page because three elements are `position:fixed`."*

### S-12 — the footer element is never named (advisory).
QA-M1-04, QA-M2-09, QA-M4-06 assert "its footer has exactly two buttons." The page uses `.foot`. Guessing `footer` or `.mfoot` yields the whole modal and a false FAIL. Same for "the mentions pane" in QA-C-04.
**Fix:** name `.foot` (and the mentions pane) once in §8.0 or §2.2.

---

## 4. What the run proves about the wireframe

Only **one** genuine product defect surfaced, and the spec had already called it: **QA-S6-07 / WF-1** — `#s6b .donebanner` still reads `… Received Date 07-26 14:02 · Carrier recorded automatically`, contradicting `[BR-24]`. §8.7 states this assertion "is expected to FAIL on the live wireframe today," and it does. The spec's handling of this is exemplary and should be the template for the other known-defect cases.

Two demo limitations were confirmed exactly as §2.3 documents them, via the `[WF]` negatives the spec wrote for that purpose: **L-4** (QA-S1-20 — `#s1b .logsec` is null) and **L-3** (QA-LG-03 — `#scanfloat` invisible outside State 1). This pattern works and is the right one.

Everything else that failed is a spec-execution problem, not a page problem.

---

## 5. Verdict on the owner's goal

> *"an AI can run QA from it with ZERO questions"*

**No — not yet.** 103 of 135 [WF] scenarios (76 %) ran clean with zero external knowledge, which is a genuinely high bar for a spec of this size. But 32 scenarios (24 %) either fail on correct behavior, cannot be executed, or produce a verdict a reviewer would have to overturn — and an AI following §8 literally would file **28 false bugs against a correct wireframe** while surfacing only 1 real one. That ratio inverts the value of the run.

The gap is narrow and mechanical, not conceptual. S-1 alone accounts for 21 of the 29 failures; S-0, S-1, S-2, S-3, S-11 and S-12 are all single-sentence additions to §8.0. **With S-0 through S-4 and S-11/S-12 applied, the projected result is 131 PASS / 1 FAIL (the real WF-1 defect) / 3 requiring a retag or a quoted string** — at which point "zero questions" is true.

Priority order: **S-1 → S-0 → S-3 → S-2 → S-11 → S-4 → S-8 → S-5/S-6/S-7 → S-9/S-10/S-12.**

---

## 6. Scenario table

All 135 [WF] scenarios, in execution order. Evidence is the harness's own output, truncated to 300 chars.

| # | Scenario | Verdict | Culprit | Evidence (page actual vs spec expected) |
|---|---|---|---|---|
| 1 | QA-S0-01 | PASS | — | `active=s0 tabOn="0 · Waiting (Before Scan)" h2="WMS - View Orders" sub="Search Orders" value="" placeholderMatch=true` |
| 2 | QA-S0-03 | PASS | — | `#s0 .seg=null elementsContaining"Matched field"=[]` |
| 3 | QA-S0-04 | PASS | — | `hasWaitingForScan=true hasScanSentence=true dashedPanel=true ordercard=null literal="Scan a tracking/product barcode or type a number to switch to that order's screen instantly 2 ▸ Expected Inbound 4 — 2 with tracking "` |
| 4 | QA-S0-05 | PASS | — | `btn-blue in #s0 .searchrow with text "🔍 Search" -> found; buttons in searchrow=["🔍 Search"]` |
| 5 | QA-S0-06 | PASS | — | `visible=true toggleText="▸ Expected Inbound 4 — 2 with tracking · 1 Partial Inbound" expected="▸ Expected Inbound 4 — 2 with tracking · 1 Partial Inbound" inexpTable.style.display="none"` |
| 6 | QA-S0-07 | PASS | — | `afterClick visible=true arrow▾=true rowCount=4 firstCells=["202608020001","202607120001","202608020002","202608010004"] want=["202608020001","202607120001","202608020002","202608010004"] \| afterSecondClick display="none" arrow▸=true` |
| 7 | QA-S0-08 | PASS | — | `headers=["Inbound No.","Sourcing Route","Supplier","Items","Tracking No","Status"] want=["Inbound No.","Sourcing Route","Supplier","Items","Tracking No","Status"] row2.tag-wholesale="WHOLESALE" supplier비엠유통=true row2.tag-part="PARTIAL 620/800" row3.TrackingNo="—" row4.TrackingNo="—"` |
| 8 | QA-S0-09 | PASS | — | `checked=26 nonTransparent=[]` |
| 9 | QA-S0-10 | PASS | — | `activeState=s6 #s0.hasClass('on')=false` |
| 10 | QA-S0-11 | PASS | — | `sortedToTop=true clickRow=true fullList=true` |
| 11 | QA-SC-06 | PASS | — | `#s1 .search-input input value="10323775316153" expected="10323775316153"` |
| 12 | QA-SC-07 | PASS | — | `got={"s1b":"10323775317888","s2":"10323775316153","s3":"10323775316153","s4":"10322198837710","s5":"10324880021991","s6":"10325661220417"} want={"s1b":"10323775317888","s2":"10323775316153","s3":"10323775316153","s4":"10322198837710","s5":"10324880021991","s6":"10325661220417"}` |
| 13 | QA-SC-08 | PASS | — | `value="" placeholder="Scan a tracking barcode — continue with the next one" expectedPlaceholder="Scan a tracking barcode — continue with the next one"` |
| 14 | QA-SC-17 | PASS | — | `s0..s6 identical=true s6b differs=true s6b="Scan a tracking barcode — continue with the next one"` |
| 15 | QA-S1-01 | FAIL | spec (S-1) | `row-hit count=1 skuCell literal="1000051045" dotStripped="100005104" tag-pending="PENDING"` |
| 16 | QA-S1-03 | FAIL | spec (S-1) | `row-hit buttons literal=["Inbound + Outbound8"] dotStripped=["Inbound + Outbound"] class="btn btn-green btn-sm anno"` |
| 17 | QA-S1-04 | PASS | — | `row-hit buttons=["Inbound"] ordercard Outbound class="btn btn-gray btn-sm"` |
| 18 | QA-S1-05 | PASS | — | `pendingRows=2 skus=["100005104","100038120"]` |
| 19 | QA-S1-06 | PASS | — | `bulkbar buttons=["Bulk Inbound (Selected)","Inbound + Outbound All Remaining"] .cnt="1 selected · Processing all triggers auto Outbound (Hold orders: Inbound only)" expected="1 selected · Processing all triggers auto Outbound (Hold orders: Inbound only)"` |
| 20 | QA-S1-07 | PASS | — | `actual="2 not yet inbounded — processing all triggers auto Outbound (Hold orders: Inbound only)" expected="2 not yet inbounded — processing all triggers auto Outbound (Hold orders: Inbound only)"` |
| 21 | QA-S1-08 | PASS | — | `bulkbar present per state={"s1":true,"s1b":true,"s2":true,"s3":true,"s4":true,"s5":true}` |
| 22 | QA-S1-09 | FAIL | spec (S-2) | `literal={"s0":"no .ordercard","s1":["Outbound10"],"s1b":["Outbound"],"s2":["Outbound1"],"s3":["✓ Outbounded1","Cancel Outbound2"],"s4":[],"s5":["Outbound2"],"s6":"no .ordercard","s6b":"no .ordercard"} dotStripped={"s0":"no .ordercard","s1":["Outbound"],"s1b":["Outbound"],"s2":["Outbound"],"s3":["✓ O …` |
| 23 | QA-S1-10 | PASS | — | `routeBadges=["SMART BUY","JIT (Coupang)","WHOLESALE","PARTNERSHIP",null,null,null,null] pendingRowRoutes=["JIT (Coupang)"]` |
| 24 | QA-S1-11 | PASS | — | `PENDING+non-JIT rows=[]` |
| 25 | QA-S1-12 | FAIL | spec (S-4) | `SPEC SAYS "cell" (td): tdQtyCells=[{"t":"100040311","cls":"num"},{"t":"1","cls":""},{"t":"24101467541797","cls":"num"},{"t":"10323775316153","cls":"num"},{"t":"100005104","cls":"num anno"},{"t":"1","cls":""},{"t":"24101467541797","cls":"num"},{"t":"10323775316153","cls":"num"},{"t":"100024743","cls" …` |
| 26 | QA-S1-13 | FAIL | spec (S-1) | `literal={"s1":["","SKU","Image","Product Name18","Product Name KR","Size","Qty","Barcode","Inbound Order No","Tracking No","Inbound Status","Sourcing Route6","Location17","Actions"],"s1b":["","SKU","Image","Product Name","Product Name KR","Size","Qty","Barcode","Inbound Order No","Tracking No","Inbo …` |
| 27 | QA-S1-14 | PASS | — | `scopedTo #s1 table.tbl (spec's bare "#s1 tbody" also matches the .logtbl). rows=[{"cls":"(none)","sku":"100040311","loc":"–"},{"cls":"row-hit","sku":"100005104","loc":"–"},{"cls":"row-exist","sku":"100024743","loc":"A-03-2"},{"cls":"(none)","sku":"100038120","loc":"–"}]` |
| 28 | QA-S1-15 | PASS | — | `rows=[{"enB":"COSRX","krB":"COSRX","krTxt":"COSRX 석류 엔 콜라겐 볼륨탄력 크림"},{"enB":"Dr.Jart+","krB":"Dr.Jart+","krTxt":"Dr.Jart+ 포어레미디 리뉴잉 폼 클렌저"},{"enB":"The Face Shop","krB":"The Face Shop","krTxt":"The Face Shop 미감수 브라이트 클렌징 티슈"},{"enB":"Medicube","krB":"Medicube","krTxt":"Medicube 제로 모공 패드 2.0 (1+1)"}] …` |
| 29 | QA-S1-16 | PASS | — | `{"s1":{"bcinPlaceholders":["Enter barcode"],"row100024743HasBcin":true,"barcodeCellsWithoutInput":["✓ 8801051283860","✓ 8809571501234","✓ 8809894261234"]},"s1b":{"bcinPlaceholders":["Enter barcode"],"row100024743HasBcin":true,"barcodeCellsWithoutInput":["✓ 8801051283860","✓ 8809571501234","–"]},"s2" …` |
| 30 | QA-S1-17 | PASS | — | `afterInput visible=1 text='Save'; afterEnter text='✓ Saved' class='flsave ok'; visibleAfter~1.1s=0; navigationEntries=1` |
| 31 | QA-S1-18 | PASS | — | `shelf input original value="3" set to "3"; visible button.flsave count=0` |
| 32 | QA-S1-19 | PASS | — | `heading="Inbound / Outbound Log" found=true headers=["Time","Action","SKU","Qty","Worker","Memo"] dataRows(td-bearing)=3 bare "tbody tr" count=4 (header row lives INSIDE tbody) memos=["–","1 box damaged — restocked, needs inspection","–"]` |
| 33 | QA-S1-20 | PASS | — | `#s1b .logsec = null (spec: this WF result documents demo limitation L-4)` |
| 34 | QA-S2-01 | FAIL | spec (S-3) | `SPEC SELECTOR "#s2 tbody tr" returns 9 rows (it also matches the .logtbl); scoped to table.tbl it returns 4. tags=["INBOUNDED","INBOUNDED","INBOUNDED","INBOUNDED"] Outbound class="btn btn-green btn-sm anno"` |
| 35 | QA-S2-02 | PASS | — | `buttons=[{"t":"Bulk Inbound (Selected)","c":"btn btn-gray btn-sm"},{"t":"Inbound + Outbound All Remaining","c":"btn btn-gray btn-sm"}] .cnt="Nothing left to bulk-process — all items inbounded" expected="Nothing left to bulk-process — all items inbounded"` |
| 36 | QA-S2-03 | FAIL | spec (S-1) | `literal button match=false (row button textContent="Cancel Inbound2") open=true header literal="Cancel Inbound — 100038120✕" dotAndCloseStripped="Cancel Inbound — 100038120" expected="Cancel Inbound — 100038120" tbodyUnchanged=true` |
| 37 | QA-S2-04 | PASS | — | `openAfterClose=false tbodyByteIdentical=true` |
| 38 | QA-S3-01 | FAIL | spec (S-1) | `ordercard buttons literal=["🖨 Print","Save","✓ Outbounded1","Cancel Outbound2","💬 Comments 2"] dotStripped=["🖨 Print","Save","✓ Outbounded","Cancel Outbound","💬 Comments 2"] class="btn btn-gray btn-sm anno" pill="Prepare Shipment"/status st-prepare` |
| 39 | QA-S3-02 | FAIL | spec (S-1) | `button literal-text match=False (literal buttons=['🖨 Print', 'Save', '✓ Outbounded1', 'Cancel Outbound2', '💬 Comments 2'], dot-stripped=['🖨 Print', 'Save', '✓ Outbounded', 'Cancel Outbound', '💬 Comments 2']); dialogs=['Status rollback: prepare shipment → processing'] expected='Status rollback: prepa …` |
| 40 | QA-S3-03 | FAIL | spec (S-1) | `literal=[{"t":"Cancel Inbound4","g":true},{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbound","g":true}] dotStripped=[{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbound","g":true}] tbody .btn-red-line …` |
| 41 | QA-S3-04 | PASS | — | `toastTexts=["✓ Inbound complete — 100040311No refresh · ready for the next scan15","✓ Outbound complete — Order 413865Status: prepare shipment3","✓ Inbound complete — Inbound No. 202607120001Inventory updated · Request list INBOUNDED · ","✓ Tracking No 10323100835644 matched and registeredOrder 4142 …` |
| 42 | QA-S3-05 | PASS | — | `dataRows(td-bearing)=5 bare "tbody tr"=6 newest=["07-09 11:47","OUTBOUND","All (4 SKU)","5","Dean","–"]` |
| 43 | QA-S4-01 | FAIL | spec (S-1) | `lead="⟲ Customer Return Order" bodyLiteral="A returned tracking barcode was scanned — Order 412990 · Tracking 10322198837710 1" bodyDotStripped="A returned tracking barcode was scanned — Order 412990 · Tracking 10322198837710" expected="A returned tracking barcode was scanned — Order 412990 · Tracki …` |
| 44 | QA-S4-02 | PASS | — | `statusPills=["refunded"]` |
| 45 | QA-S4-03 | PASS | — | `#s4 .ordercard buttons=["Save","💬 Comments 1"]` |
| 46 | QA-S4-04 | PASS | — | `buttons=[{"t":"Bulk Inbound (Selected)","c":"btn btn-gray btn-sm"},{"t":"Inbound + Outbound All Remaining","c":"btn btn-gray btn-sm"},{"t":"Restock Selected to Warehouse (3)","c":"btn btn-green"}] .cnt="Opens the restock confirmation modal — confirm qty · location · memo per item, then process in bu …` |
| 47 | QA-S4-05 | PASS | — | `rowButtons=[{"t":"Cancel Inbound → Add Stock","c":"btn btn-red-line btn-sm"},{"t":"Cancel Inbound → Add Stock","c":"btn btn-red-line btn-sm"},{"t":"Cancel Inbound → Add Stock","c":"btn btn-red-line btn-sm"}] counter="Found 3 item(s) in this order · Found 1 order(s)"` |
| 48 | QA-S4-06 | FAIL | spec (S-1) | `open=true header literal="Warehouse Restock — Order 412990✕" (contains the ✕ close button) stripped="Warehouse Restock — Order 412990" expected="Warehouse Restock — Order 412990"` |
| 49 | QA-S4-07 | PASS | — | `leadParagraphFound=true headers=["Product","Ordered Qty","Restock Qty","Location"] want=["Product","Ordered Qty","Restock Qty","Location"] bodyRows=3 \| nearestLead="Confirm the products, quantities, and locations to restock. Products with existing stock get their current location auto-filled. Resto …` |
| 50 | QA-S4-08 | PASS | — | `rows=[{"name":"Beauty of Joseon Glow Serum, 30ml","qty":"1","loc":"A-03-2","locPh":"","locNeed":false},{"name":"Medicube Zero Pore Pad 2.0, 1+1","qty":"1","loc":"B-01-4","locPh":"","locNeed":false},{"name":"Anua Heartleaf 77% Soothing Toner, 250ml","qty":"0","loc":"","locPh":"required","locNeed":tru …` |
| 51 | QA-S4-09 | PASS | — | `amber1=true amber2=true blueNote=true \| modalText="M3 Warehouse Restock — Order 412990✕ Confirm the products, quantities, and locations to restock. Products with existing stock get their current location auto-filled. Restock qty defaults to 0 — enter only the qty actually returned (0 = excluded). P …` |
| 52 | QA-S4-10 | PASS | — | `textarea.mtextarea=true placeholder="Return reason · condition (visible damage etc.) · notes — also recorded in the order's Comments history and the inbound log"` |
| 53 | QA-S5-01 | FAIL | spec (S-1) | `lead="⏸ Hold Shipment" bodyLiteral="CS team put this order on Hold per customer request (address change) — Order 414102 · Requested by Sara(CS) 07-13 09:20 1" bodyDotStripped="CS team put this order on Hold per customer request (address change) — Order 414102 · Requested by Sara(CS) 07-13 09:20" exp …` |
| 54 | QA-S5-02 | FAIL | spec (S-1) | `ordercard buttons literal=["🖨 Print","Save","Outbound2","💬 Comments 1"] dotStripped=["🖨 Print","Save","Outbound","💬 Comments 1"] class="btn btn-gray btn-sm anno"` |
| 55 | QA-S5-03 | PASS | — | `BulkInbound class="btn btn-green-line btn-sm" AllRemaining class="btn btn-gray btn-sm" .cnt="Hold order — Inbound allowed, Outbound blocked (ship after Hold release)" expected="Hold order — Inbound allowed, Outbound blocked (ship after Hold release)"` |
| 56 | QA-S5-04 | PASS | — | `rows=[[],["07-13 09:20","HOLD Applied","All","–","Sara (CS)","Customer address change request — shipment held"],["07-13 08:55","INBOUND","100040311","1","Miranti","–"]]` |
| 57 | QA-S5-05 | PASS | — | `#s5 .ordercard buttons=["🖨 Print","Save","Outbound2","💬 Comments 1"]` |
| 58 | QA-S5-06 | PASS | — | `matches=[]` |
| 59 | QA-S6-01 | PASS | — | `big="📦 Internal Inbound — Inbound Request" warnline="Not a customer order · Goes into Inventory · No Outbound step" kv="Inbound No. 202607120001 Channel WHOLESALE Supplier 비엠유통 Requested by Dean · 07-12 Expected arrival 07-18 View in Inbound Request List →" missingFromKv=[]` |
| 60 | QA-S6-02 | PASS | — | `text="View in Inbound Request List →" href="../inbound-request/index.html#reqlist"` |
| 61 | QA-S6-03 | PASS | — | `tileCount=4 tiles=[{"txt":"Expected Qty (Total)800","cls":"tile"},{"txt":"Received (scanned)620","cls":"tile ok"},{"txt":"Remaining180","cls":"tile warn"},{"txt":"SKU2 SKUs (1 done)","cls":"tile"}]` |
| 62 | QA-S6-04 | FAIL | spec (S-1) | `literal="4 Now scan product barcodes — each scan adds +1 to that product's received qty (continuous scanning · cursor auto-return · warning sound for products not in the request)" dotStripped="Now scan product barcodes — each scan adds +1 to that product's received qty (continuous scanning · cursor  …` |
| 63 | QA-S6-05 | FAIL | spec (S-1) | `headers literal=["SKU No.","Brand","Product Name","Expected Qty9","Received Qty6","Location7","Status"] dotStripped=["SKU No.","Brand","Product Name","Expected Qty","Received Qty","Location","Status"] want=["SKU No.","Brand","Product Name","Expected Qty","Received Qty","Location","Status"] rowsOK=tr …` |
| 64 | QA-S6-06 | PASS | — | `th/label containing "Carrier"=[]` |
| 65 | QA-S6-07 | FAIL | **wireframe (WF-1)** | `#s6b .donebanner text="1 ✓ Full Inbound Complete — Inbound No. 202607120001 Received 800 / 800 (2 SKUs) Inventory updated (A-05-11 · B-02-07) Inbound Request List switched to INBOUNDED Received Date 07-26 14:02 · Carrier recorded automatically" containsCarrierClause=true` |
| 66 | QA-S6-08 | PASS | — | `confirmBtn="btn btn-gray" partialBtn="btn btn-line" allS6Buttons=["💬 Comments2","Logout","@ Mentions 2","★ Saved","★","★","★","🔍 Search","✎","Save","✎","Save","Confirm Full Inbound (180 remaining)","Save Partial Inbound"]` |
| 67 | QA-S6-09 | PASS | — | `exactMatchFound=true nearest="On confirm: reflected in Inventory (Current Stocks) · Inbound Request List switches to INBOUNDED · Received Date recorded automatically" expected="On confirm: reflected in Inventory (Current Stocks) · Inbound Request List switches to INBOUNDED · Received Date recorded a …` |
| 68 | QA-S6-10 | UNRUNNABLE | spec (S-8) | `visible button.flsave count=0 text="null" (spec §2.3 L-13 says .flsave is NOT wired to .qtyin, but this scenario is tagged [WF])` |
| 69 | QA-S6-11 | PASS | — | `locinValues=["A-05-11","B-02-07"] flsaveVisibleAfterInput=1` |
| 70 | QA-S6-12 | FAIL | spec (S-1) | `qedit[1] rowContainsSKU100052124=true header literal="Edit Expected Qty — Inbound No. 202607120002✕" stripped="Edit Expected Qty — Inbound No. 202607120002" inputs=["120"] helperFound=true options=["Damaged/defective — cannot accept","Supplier qty change","Other"]` |
| 71 | QA-S6-13 | PASS | — | `optionCount=3 options=["Damaged/defective — cannot accept","Supplier qty change","Other"]` |
| 72 | QA-S6-14 | FAIL | spec (S-7) | `textarea="1 box damaged — 180 units rejected, returned to supplier" quotedFragments=[{"q":"Confirm Full Inbound enabled","found":true},{"q":"auto-posted as a Comment on this Inbound Request","found":true},{"q":"the requester (@Dean) gets a Slack alert","found":true},{"q":"the request list qty cell s …` |
| 73 | QA-S6-15 | FAIL | spec (S-1) | `header literal="Save Partial Inbound — Inbound No. 202607120001✕" stripped="Save Partial Inbound — Inbound No. 202607120001" leadFound=true perSkuLineFound=true options=["Split shipment — remainder arriving later","Short delivery (needs supplier confirmation)","Partially damaged — will be returned t …` |
| 74 | QA-S6-16 | PASS | — | `notes={inv:true,partial:true,stages:true,rescan:true} placeholder="e.g. Remaining 180 units arriving Friday — also recorded in the request's Comments" buttons=["✕","Cancel","Save Partial Inbound"]` |
| 75 | QA-S6-17 | PASS | — | `big="✓ Full Inbound Complete — Inbound No. 202607120001" kv="Received 800 / 800 (2 SKUs) Inventory updated (A-05-11 · B-02-07) Inbound Request List switched to INBOUNDED Received Date 07-26 14:02 · Carrier recorded automatically" missing=[]` |
| 76 | QA-S6-18 | PASS | — | `rows=[{"cls":"row-done","done":true,"tag":"✓ INBOUNDED","cells":["100052117","Round Lab","1025 Dokdo Toner, 200ml","500","500","A-05-11","✓ INBOUNDED"]},{"cls":"row-done","done":true,"tag":"✓ INBOUNDED","cells":["100052124","Round Lab","1025 Dokdo Cleanser, 150ml","300","300","B-02-07","✓ INBOUNDED" …` |
| 77 | QA-S6-19 | FAIL | spec (S-1) | `literal="2 Cursor returns to the search box immediately on completion — scan the next tracking number with no refresh. This stock is visible in Inventory (Current Stocks) with its locations." dotStripped="Cursor returns to the search box immediately on completion — scan the next tracking number with …` |
| 78 | QA-S6-20 | PASS | — | `violations=[]` |
| 79 | QA-S6-21 | PASS | — | `toasts=["✓ Inbound complete — 100040311No refresh · ready for the next scan15","✓ Outbound complete — Order 413865Status: prepare shipment3","✓ Inbound complete — Inbound No. 202607120001Inventory updated · Request list INBOUNDED · ready for the next t","✓ Tracking No 10323100835644 matched and regi …` |
| 80 | QA-M1-01 | FAIL | spec (S-1) | `header literal="Cancel Inbound — 100038120✕" stripped="Cancel Inbound — 100038120" yesChecked=true restockQty="2" noteFound=true` |
| 81 | QA-M1-02 | PASS | — | `afterNo={"disabled":true,"value":""} afterYes={"disabled":false,"value":"2"}` |
| 82 | QA-M1-03 | PASS | — | `helperFound=true memoPlaceholder="Cancellation reason or notes — also recorded in the order's Comments history" useCaseFound=true` |
| 83 | QA-M1-04 | PASS | — | `(spec never names the footer element; used .foot) buttons=["Close","Confirm"] closedByBackdrop=true` |
| 84 | QA-M2-01 | FAIL | spec (S-1) | `header literal="Barcode Not Recognized✕" stripped="Barcode Not Recognized" leadFound=true instructionFound=true unrecNo="12101316464794"` |
| 85 | QA-M2-02 | PASS | — | `visible=true rows=2 headers=["Image","Product Name","Order","Qty","Tracking No",""] want=["Image","Product Name","Order","Qty","Tracking No",""] row1Cells=["IMG","Dr.Jart+ Pore Remedy Renewing Foam Cleanser, 150mlDr.Jart+ — 포어레미디 리뉴잉 폼 클렌저","414230","1","10323100835644","Match Tracking No"] unrecNon …` |
| 86 | QA-M2-03 | PASS | — | `exactNoteFound=true nearest="Clicking match registers the tracking number on that line and closes this window — rescanning the same barcode is then recognized normally."` |
| 87 | QA-M2-04 | PASS | — | `btnText='Match Tracking No' modalOpenAfter=False toastVisible=True toastText='✓ Tracking No 10323100835644 matched and registeredOrder 414230 · Dr.Jart+ 포어레미디 폼 — rescanning the same barcode is now recognized' sub='Order 414230 · Dr.Jart+ 포어레미디 폼 — rescanning the same barcode is now recognized' visi …` |
| 88 | QA-M2-05 | PASS | — | `unrecFoundHidden=true unrecNoneVisible=true unrecNoneText="No products match the entered order number (possible typo or a number from another channel). Send it to the Missing Tracking List. Send to Missing Tracking List"` |
| 89 | QA-M2-06 | PASS | — | `m-unrec.open=false m-unrec2.open=true unrecCarriedVisible=true unrecCarriedNo="99999999999999"` |
| 90 | QA-M2-07 | PASS | — | `m-unrec2.open=true #unrecCarried style.display="none" computed="none"` |
| 91 | QA-M2-08 | PASS | — | `input[type=file]=0 forbiddenWordHits=[]` |
| 92 | QA-M2-09 | PASS | — | `(spec never names the footer element; used .foot) footButtons=["No order number","Cancel"] demoHintExact=true` |
| 93 | QA-M2-10 | FAIL | spec (S-1) | `header literal="Send to Missing Tracking List✕" stripped="Send to Missing Tracking List" checks={"lead":true,"prompt":true,"autoVal":"glow ser","optCount":3,"firstSel":true,"firstHasEN":true,"firstHasKR":true,"qtyInputValues":["glow ser","1"],"memoPh":"e.g. Box label damaged, looks like a 1+1 set —  …` |
| 94 | QA-M2-11 | PASS | — | `exactNoteFound=true nearest="On send, the #unrecognized-tracking channel gets an "Unrecognized product added" alert (product name · barcode · qty · memo · order number if lookup failed) → shown in the unrecognized pool on the Missing Tracking List page."` |
| 95 | QA-M2-12 | PASS | — | `gtoastVisible=True text='✓ Sent to Missing Tracking ListPIC notified via #unrecognized-tracking · No refresh' sub='PIC notified via #unrecognized-tracking · No refresh' m-unrec2.open=False visibleAfter2.8s=False navigationEntries=1` |
| 96 | QA-M4-01 | FAIL | spec (S-1) | `header literal="Print Return Labels — 2 Selected Products (Supplier Return)✕" stripped="Print Return Labels — 2 Selected Products (Supplier Return)" chips=["CJ대한통운","롯데택배","한진택배","우체국택배","로젠택배","✎ Custom"] onChips=["CJ대한통운"]` |
| 97 | QA-M4-02 | PASS | — | `headers=["Product Name KR","Size (optional)","Qty (optional)"] want=["Product Name KR","Size (optional)","Qty (optional)"] rows=[{"brand":"Dr.Jart+","name":"Dr.Jart+ 포어레미디 리뉴잉 폼 클렌저","inputs":["150ml","1"]},{"brand":"Medicube","name":"Medicube 제로 모공 패드 2.0","inputs":["","2"]}]` |
| 98 | QA-M4-03 | PASS | — | `#rlPreviewCarrier="CJ대한통운" line1Exact=true line2Exact=true previewLines=["Dr.Jart+ 포어레미디 리뉴잉 폼 클렌저 Medicube 제로 모공 패드 2.0","Dr.Jart+ 포어레미디 리뉴잉 폼 클렌저","Dr.Jart+ 포어레미디 리뉴잉 폼 클렌저","Medicube 제로 모공 패드 2.0"]` |
| 99 | QA-M4-04 | PASS | — | `rlCustomRowVisible=true activeElementIsCustomInput=true previewAfterChipClick="Carrier name" onChips=["✎ Custom"] previewAfterTyping="대신택배"` |
| 100 | QA-M4-05 | PASS | — | `row2 sizeInput value="" placeholder="omitted if empty" noteExact=true nearestNote="Use case: during inbound scanning, return items to the supplier (e.g. Coupang seller) when wrong/damaged items are found. Printing puts carrier name + product name (KR) + size + qty on the label — size/qty omitted if  …` |
| 101 | QA-M4-06 | PASS | — | `(spec never names the footer element; used .foot) footButtons=["Cancel","🖨 Print"]` |
| 102 | QA-M4-07 | PASS | — | `presentIn={"s1":true,"s1b":true,"s2":true,"s3":true} presentInStatesThatShouldNotHaveIt={"s4":false,"s5":false,"s6":false,"s6b":false} clickOpensM4=true` |
| 103 | QA-C-01 | PASS | — | `visible=true cItemCount=2 firstAuthorHasDean=true span.at="@Yongwon" composerPlaceholder="Write a comment — @name sends an automatic Slack alert (order no · text · time · author)" buttons=["★","★","Post"]` |
| 104 | QA-C-02 | PASS | — | `badge="2" visibleBefore=true afterClick1=false afterClick2=true` |
| 105 | QA-C-03 | PASS | — | `open=true tabTexts=["@ Mentions 3","3","★ Saved"] headerFound=true markAllAsRead=true` |
| 106 | QA-C-04 | PASS | — | `(spec says "the mentions pane" but names no selector; used visible .it) allItInDropdown=6 visible=4 unread=3 orders=["413865","413712","413650","413501"]` |
| 107 | QA-C-05 | PASS | — | `visibleEntries=2 orders=["413712","412990"] starClasses=["star on","star on"] headerFound=true` |
| 108 | QA-C-06 | PASS | — | `tabsHidden=true headerFound=true markCount=2 visibleResultOrders=["413650","412990"]` |
| 109 | QA-C-07 | PASS | — | `panelText="@ Mentions 3 ★ Saved Comments where I'm tagged · Click to open the order page Mark all as read Order 413865 · Dean: "@Yongwon Only 1 of 2 JIT items has arrived. Please check"10:42★ Order 413712 · Miranti: "@Yongwon Pleas"` |
| 110 | QA-C-08 | PASS | — | `tabsVisible=true panes=[]` |
| 111 | QA-C-09 | PASS | — | `class before="star" afterClick1="star on" afterClick2="star"` |
| 112 | QA-C-10 | PASS | — | `badge="2" hasReq1=true hasReq2=true headerFound=true paneHeader="Comments where I'm tagged · Click to open the item Mark all as read Inbound 202607120001 "` |
| 113 | QA-C-11 | PASS | — | `perState={"s0":"🔍 Search all Comments — order no · author · text","s1":"🔍 Search all Comments — order no · author · text","s1b":"🔍 Search all Comments — order no · author · text","s2":"🔍 Search all Comments — order no · author · text","s3":"🔍 Search all Comments — order no · author · text","s4":"🔍 S …` |
| 114 | QA-LG-01 | PASS | — | `collapsed=true header="📡 Live Barcode Feed 4▾" badge4Found=true ulHidden=true footerHidden=true` |
| 115 | QA-LG-02 | PASS | — | `collapsedRemoved=true .x="–" liCount=4 footerText="Max 20 on screen · full history in backendExport by date" footerButtons=["Export by date"]` |
| 116 | QA-LG-03 | PASS | — | `#scanfloat visible per state (getClientRects) = {"s1b":false,"s2":false,"s3":false,"s4":false,"s5":false,"s6":false,"s6b":false}; it lives inside #s1 so it hides with the state (documents demo limitation L-3)` |
| 117 | QA-GL-01 | PASS | — | `toasts=["✓ Inbound complete — 100040311No refresh · ready for the next scan15"] sub="No refresh · ready for the next scan"` |
| 118 | QA-GL-02 | AMBIGUOUS | spec (S-9/S-10) | `Scenario says "assert the binding rule only" for the send-sound handler. No DOM-observable assertion is given (no attribute, no class, no marker); event listeners added via addEventListener are not enumerable from page script. Spec provides no instruction for how to observe the binding.` |
| 119 | QA-GL-11 | PASS | — | `{"s1":{"bodyScrollWidth":1280,"clientWidth":1280,"ok":true},"s1b":{"bodyScrollWidth":1280,"clientWidth":1280,"ok":true},"s2":{"bodyScrollWidth":1280,"clientWidth":1280,"ok":true},"s3":{"bodyScrollWidth":1280,"clientWidth":1280,"ok":true},"s4":{"bodyScrollWidth":1280,"clientWidth":1280,"ok":true},"s5 …` |
| 120 | QA-GL-13 | PASS | — | `navMissing=[] h2="WMS - View Orders" subs=["Search Orders","Search Results"]` |
| 121 | QA-GL-14 | PASS | — | `orderIdFound=true pill="Processing" totalQty=true s6.ordercard=null s6b.ordercard=null` |
| 122 | QA-NG-08 | FAIL | spec (S-2) | `input[type=file]=0 .seg=null violations=["s1:Deleo"]` |
| 123 | QA-NG-09 | PASS | — | `allHrefs=["../inbound-request/index.html#reqlist"] offending=[]` |
| 124 | QA-NG-10 | FAIL | spec (S-5) | `document-navigating anchors=["../inbound-request/index.html#reqlist"] navigating onclick=[]` |
| 125 | QA-CV-02 | PASS | — | `{"s1":true,"s1b":true,"s2":true,"s3":true,"s5":true,"s4":false}` |
| 126 | QA-CV-05 | PASS | — | `s1 headerCheckbox=true s1 rows=[{"has":true,"checked":false,"hit":false},{"has":true,"checked":true,"hit":true},{"has":true,"checked":false,"hit":false},{"has":true,"checked":false,"hit":false}] s4 headerChecked=true s4 rowChecked=[true,true,true]` |
| 127 | QA-CV-06 | PASS | — | `{"s1":{"counter":"Found 4 item(s) in this order · Found 1 order(s)","rows":4},"s5":{"counter":"Found 2 item(s) in this order · Found 1 order(s)","rows":2}}` |
| 128 | QA-CV-07 | PASS | — | `missingVerbatimRules=[]` |
| 129 | QA-CV-08 | PASS | — | `exactParagraphFound=true nearest="The Hold itself is applied via the "Hold Shipment" button in OMS/Order detail or Order Management (CS team). View Orders only displays the resulting status and blocks outbound."` |
| 130 | QA-CV-09 | PASS | — | `missing=[]` |
| 131 | QA-CV-10 | PASS | — | `found=true \| s6 legend excerpt="tock intake) at the view level. An inbound request may have multiple tracking numbers registered (split shipments) — every registered number matches and enters this screen (2026-08-03) — I + C Search 2Internal Inbound banner "` |
| 132 | QA-CV-11 | AMBIGUOUS | spec (S-9/S-10) | `searchValue="10322198837710" (checkable) BUT legend entries 4/5 are asserted only as "states the qty-without-location confirm block" / "states that the unified search auto-detects return barcodes" with no quoted string and no selector for indexing legend entries. legendChildren=["State 4 — Changes:  …` |
| 133 | QA-CV-12 | FAIL | spec (S-1) | `printReturnLabels=true rowButtons literal=[{"t":"Cancel Inbound4","g":true},{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbound","g":true}] dotStripped=[{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbound","g":true},{"t":"Cancel Inbou …` |
| 134 | QA-CV-18 | FAIL | spec (S-6) | `violations=["s1 notUppercase=\"JIT (Coupang)\"","s1b notUppercase=\"JIT (Coupang)\"","s1b notUppercase=\"JIT (Coupang)\"","s2 notUppercase=\"JIT (Coupang)\"","s3 notUppercase=\"JIT (Coupang)\"","s5 notUppercase=\"JIT (Coupang)\""]` |
| 135 | QA-CV-20 | PASS | — | `no-annoAdded=true dotsHidden=true legendsHidden=true textAfter="Show annotations" restored=true textRestored="Hide annotations"` |

---

*Re-run with:* `python3 /Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_verify/qa-view-orders.py --json out.json`
