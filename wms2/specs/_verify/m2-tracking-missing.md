# M2 — Adversarial QA Execution: `tracking-missing.md` §8

**Method:** Verification Method 2 (hostile QA robot). The executing agent did not write this spec and
consulted no source outside §8 while building the tests.
**Target spec:** `wms2/specs/tracking-missing.md` §8 (QA Acceptance Criteria)
**System under test:** `file://…/wms2/tracking-missing/index.html` (identical to the deployed page)
**Runner:** Playwright / Python / headless Chromium, viewport 1280×800
**Script:** `wms2/specs/_verify/qa-tracking-missing.py` (re-runnable: `python3 qa-tracking-missing.py [--json]`)
**Run date:** 2026-08-03

---

## 1. Methodology

1. **Extraction.** Every scenario tagged `[WF]` in §8 was extracted. The spec claims **67 [WF]**
   (§8.0: "151 scenarios — 67 [WF], 84 [ADMIN]"). Independent count from the block bodies:
   LOAD 11 · ROW 9 · SUS 5 · M1 9 · MATCH 5 · XDEL 3 · CMT 7 · FURN 5 · NEG 2 · VAL 0 · EMPTY 2 ·
   XPG 1 · DATA 0 · A11Y 2 · WFQ 6 = **67**. The declared total is correct.
   Rather than sample the required minimum of 25, **all 67 were attempted** — a superset that
   removes selection bias from the verdict.
2. **Execution discipline.** Each scenario was coded from its own sentence only, using the IDs,
   classes and literal strings §8.0 supplies. Where §8 states an exact string, the test asserts
   equality, not containment. Where §8 says "contains", the test asserts containment. No selector
   was invented from reading the HTML first; the HTML was consulted only afterwards, to *explain*
   an already-recorded failure.
3. **Baseline.** §8.0's reset procedure (full page reload) runs before every scenario, and the
   declared baseline was asserted once at start-up. It held exactly:
   `{"poolCount":"3","poolCountBottom":"3","rowHits":3,"row1":true,"mOpen":false,"inboxOpen":false,"toast":"none","anno":true}`
4. **Verdicts.** `PASS` · `FAIL` (spec says X, page does Y — both quoted) · `AMBIGUOUS`
   (instructions insufficient to write the assertion) · `UNRUNNABLE` (assertion impossible in a
   static mock and not tagged `[ADMIN]`).
5. **Culprit assignment for FAILs.** Cross-checked against `specs/_plans/_wireframe-fixes.md`
   (WF-1…WF-14) and the spec's own §2.4 / §2.5 defect registers. A *known* wireframe defect makes
   the wireframe the culprit and the spec right; anything else falls on the spec or on the test
   instruction.
6. **Self-correction.** Three first-pass failures were traced to defects in *my own* test code
   (`.it:nth-of-type(1)` — `.paneheader` is also a `<div>`; `span:first-child` — `<b>` precedes the
   order-number span; scrolling only the outer `.mockwrap`). All three were fixed and re-run; none
   are reported as spec faults. They are listed in §5 because two of them expose real ambiguity in
   the spec's selector guidance.

---

## 2. Result summary

| Verdict | Count | Share |
|---|---:|---:|
| PASS | 62 | 92.5 % |
| FAIL | 3 | 4.5 % |
| AMBIGUOUS | 1 | 1.5 % |
| UNRUNNABLE | 1 | 1.5 % |
| **Attempted** | **67** | 100 % |

**Culprit split for the 3 FAILs:** spec wrong **3** · wireframe wrong **0** · test-instruction defect **0**.

No FAIL traced to a known wireframe defect. Notably, every scenario in block **WFQ** (§8.15) —
the block whose whole job is to pin the wireframe's quirks so an agent does not file false bugs —
passed. §2.4's nine demo limitations and §2.5's WF-NEW-A/B were all confirmed accurate against the
live file. The spec's factual model of the wireframe is sound; the three failures are failures of
**assertion phrasing**, not of understanding.

---

## 3. Scenario table

| ID | Verdict | Evidence / quote |
|---|---|---|
| `QA-LOAD-01` | PASS | <h2> textContent = 'WMS - Unrecognized Tracking List' |
| `QA-LOAD-02` | PASS | .sub='Unrecognized & missing-tracking status · Coupang creates the order number immediately but generates the tracking number a few hours later → unrecognized items are tracked here' |
| `QA-LOAD-03` | PASS | {"bg": "rgb(255, 251, 214)", "bc": "rgb(245, 158, 11)", "b": "⚠ Unrecognized product pool · 3 items"} |
| `QA-LOAD-04` | FAIL | spec: 'Product Name'/'Suspected Orders (Auto-matched)'/'Action'; page: 'Product Name4'/'Suspected Orders (Auto-matched)2'/'Action3' -- passes only after removing the annotation .dot children (spec gives no such instruction); strip … |
| `QA-LOAD-05` | PASS | {"pc": "3", "pcb": "3", "n": 3, "allHit": true, "nTbodies": 2}  [note: 2 'table.tbl tbody' exist; spec says 'the <tbody>' -- scoped to the pool table] |
| `QA-LOAD-06` | PASS | rendered matches = [] |
| `QA-LOAD-07` | PASS | {"li": 6, "ns": ["0", "1", "2", "3", "4", "5"], "dots": 7, "m1dot": true} |
| `QA-LOAD-08` | PASS | 2 <p> after legend <ol>; first60='2026-07-23 simplification decision: removed the per-PIC grou' |
| `QA-LOAD-09` | PASS | <input> count = 0 |
| `QA-LOAD-10` | PASS | {"printText": false, "audio": 0, "ac": false, "greens": ["Match to this product", "Match to this product"]} |
| `QA-LOAD-11` | PASS | {"h1": "WMS 2.0 · Unrecognized Tracking Wireframe", "tab": ["Modal: Match Review (M1)"], "anno": "Hide annotations"} |
| `QA-ROW-01` | PASS | {"c0": "10323100841207", "c1": "–", "c1col": "rgb(126, 124, 131)", "c1cp": 8211} |
| `QA-ROW-02` | PASS | {"b": "COSRX", "rest": " Advanced Snail 96 Mucin Power Essence, 100ml"} |
| `QA-ROW-03` | PASS | {"b": "COSRX", "rest": " 어드밴스드 스네일 96 뮤신 에센스"} |
| `QA-ROW-04` | PASS | {"en": "medicube", "kr": "Medicube", "krRest": " 제로 모공 패드 2.0 (1+1)"} |
| `QA-ROW-05` | PASS | size=['100ml', '250ml', '70ea'] barcode=['8809416470726', '8809640733458', '8809894261234'] qty=['1', '1', '2'] |
| `QA-ROW-06` | PASS | memos=['Box label damaged', '–', 'Looks like a 1+1 set'] |
| `QA-ROW-07` | PASS | registrant=['Miranti', 'Dean', 'Dean'] at=['07-13 10:12', '07-13 09:48', '07-13 09:30'] |
| `QA-ROW-08` | PASS | desc order OK; sort glyphs=0; onclick attrs=0; CDP getEventListeners on all th = [] |
| `QA-ROW-09` | PASS | tr[id] = ['poolrow1'] |
| `QA-SUS-01` | PASS | candidate <div> count = 2 |
| `QA-SUS-02` | PASS | {"text": "Dean · Order 414230 · JIT (Naver) · Processing", "b": "Dean", "ordText": "Order 414230", "ordColor": "rgb(13, 110, 253)", "ordWeight": "700", "mutText": "JIT (Naver) · Processing", "mutColor": "rgb(126, 124, 131)"} |
| `QA-SUS-03` | PASS | 'Egita · Order 413871 · JIT (Official Mall) · Processing' |
| `QA-SUS-04` | PASS | [{"n": 1, "t": "Harshit · Order 414102 · JIT (Naver) · Processing"}, {"n": 1, "t": "Miranti · Order 413998 · JIT (Official Mall) · Processing"}] |
| `QA-SUS-05` | AMBIGUOUS | spec gives no selector for 'route/channel label'. Reading A (.tag-jit etc, modal-only, n=2): satisfies the assertion. Reading B (pool-cell route text '.mut' in the Suspected Orders column, n=4): VIOLATES -- e.g. {"t": "JIT (Naver) … |
| `QA-M1-01` | FAIL | open=True; spec: <header> text is EXACTLY 'Review & Match — Unrecognized Product'; page: 'Review & Match — Unrecognized Product✕' -- the header also contains the close button '✕' (text node alone = 'Review & Match — Unrecognized P … |
| `QA-M1-02` | PASS | wf-bar demo button opens #m-match |
| `QA-M1-03` | PASS | {"b": "COSRX", "rest": " Advanced Snail 96 Mucin Power Essence, 100ml", "mut": "Barcode 8809416470726 · Tracking 10323100841207 · No order number · 1 unit · Registered by: Miranti (Center) 07-13 10:12 · Memo \"Box label damaged\"" … |
| `QA-M1-04` | PASS | {"b": "Suspected orders (auto-matched)", "mut": "— only Processing orders containing this product are shown as candidates (multiple possible). Match by selecting a product line, not the order"} |
| `QA-M1-05` | PASS | ['Order', 'PIC', 'Channel', 'Included Product', ''] |
| `QA-M1-06` | PASS | [{"cells": ["414230", "Dean", "JIT (Naver)", "COSRX Snail 96 Essence ×1"], "bold": "COSRX", "btn": "Match to this product"}, {"cells": ["413871", "Egita", "JIT (Official Mall)", "COSRX Snail 96 Essence ×1"], "bold": "COSRX", "btn" … |
| `QA-M1-07` | PASS | all 3 fragments present |
| `QA-M1-09` | PASS | {"footBtns": ["Cancel"], "bad": []} |
| `QA-M1-10` | PASS | [{"t": "JIT (Naver)", "bg": "rgba(0, 0, 0, 0)", "pad": "0px", "color": "rgb(20, 16, 27)"}, {"t": "JIT (Official Mall)", "bg": "rgba(0, 0, 0, 0)", "pad": "0px", "color": "rgb(20, 16, 27)"}] |
| `QA-MATCH-01` | PASS | #m-match class list no longer contains 'open' |
| `QA-MATCH-02` | PASS | #poolrow1 removed from DOM |
| `QA-MATCH-03` | PASS | counters = ['2', '2'] |
| `QA-MATCH-04` | PASS | {"display": "flex", "bg": "rgb(25, 135, 84)", "text": "\n  ✓ Matched to Order 414230 · COSRX Snail 96Tracking 10323100841207 registered · removed from pool · @Miranti notified via Slack\n", "span": "✓ Matched to Order 414230 · COS … |
| `QA-MATCH-05` | PASS | {"display": "none", "unloaded": false, "beforeunload": 0, "sameHref": true} |
| `QA-XDEL-01` | PASS | {"rows": 2, "trk": ["10323100841207", "10323100836690"], "pc": "2", "pcb": "2"} |
| `QA-XDEL-02` | PASS | {"ov": false, "toast": false, "now": "none"} |
| `QA-XDEL-03` | PASS | counters after 3 removals = ['0', '0'] |
| `QA-CMT-01` | PASS | {"found": true, "text": "💬 Comments3", "badge": "3"} |
| `QA-CMT-02` | PASS | {"open": true, "tabs": ["@ Mentions 3", "★ Saved"], "badge": "3"} |
| `QA-CMT-03` | PASS | {"hdr": "Comments mentioning me Mark all read", "small": "Mark all read", "smallML": "134.75px", "items": 4, "unread": 3} |
| `QA-CMT-04` | PASS | {"entity": "Unrecognized pool", "body": "Unrecognized pool · Miranti: \"@Yongwon Left a memo on the Snail essence (box label damaged). Please check whose order this is\"10:12", "time": "10:12"} |
| `QA-CMT-05` | PASS | {"mentionsDisplay": "none", "savedDisplay": "block", "hdr": "Saved comments Unstar to remove from the list", "items": 1, "entity": "Unrecognized pool"} |
| `QA-CMT-06` | PASS | initial on=False -> after 1st click on=True -> after 2nd click on=False |
| `QA-CMT-11` | PASS | open after outside click=True; open after Esc=True |
| `QA-FURN-01` | PASS | 'Unrecognized pool · 3 items' |
| `QA-FURN-02` | PASS | {"position": "fixed", "top": "18px", "right": "18px", "z": "50", "intersects": 0, "toast": [18, 1262, 57.5, 483.296875], "actions": [[381, 1081.78125], [467, 1081.78125]]} |
| `QA-FURN-03` | PASS | {"alive": true, "hist0": 2, "hist": 2, "bu": 0} |
| `QA-FURN-04` | PASS | {"brand": "SkinSeoul", "menus": ["Operation AI ▾", "Catalog Management ▾", "OMS Center ▾", "Site Management ▾"], "user": "YYongwon Ryu", "avatar": "Y", "logout": "Logout"} |
| `QA-FURN-05` | PASS | baseline #matchToast computed display = none |
| `QA-NEG-01` | PASS | {"rows": 2, "pc": "2", "pcb": "2", "toast": "flex"}  [double-click guarded by finishMatch()'s `if(row)` check] |
| `QA-NEG-03` | FAIL | spec: 'exactly one row is removed And both counters decrement by exactly 1'; page: {"rowsRemaining": 2, "pc": "1", "pcb": "1"} -- the row is removed once but poolDec() runs twice, because `.xdel`'s handler calls `b.closest('tr')`  … |
| `QA-EMPTY-01` | PASS | {"pc": "0", "pcb": "0", "poolheadRendered": true, "poolheadH": 123, "mockH": 520}  ['layout has not collapsed' has no spec-given metric; asserted mock height > 300px] |
| `QA-EMPTY-05` | PASS | {"Cancel": {"open": false, "rows": 3, "pc": "3", "pcb": "3", "toast": "none"}, "header X": {"open": false, "rows": 3, "pc": "3", "pcb": "3", "toast": "none"}, "backdrop": {"open": false, "rows": 3, "pc": "3", "pcb": "3", "toast":  … |
| `QA-XPG-05` | UNRUNNABLE | Tagged [WF] but three of its four clauses are unobservable in a static wireframe and it targets a DIFFERENT system under test (the closing page). 'no pool row ... is produced' and 'no #unrecognized-tracking message is produced' ar … |
| `QA-A11Y-01` | PASS | tab order inside #poolrow1 = ['Review & Match', '✕'] (spec: Review & Match, then .xdel) |
| `QA-A11Y-05` | PASS | {"outerMockwrap": {"sw": 1280, "cw": 900, "scrollable": true}, "innerMockwrap": {"sw": 1457, "cw": 1248, "scrollable": true}, "headersIntactInOrder": true, "actionReachable": {"outerOnlyVisible": false, "left": 836.03125, "right": … |
| `QA-WFQ-01` | PASS | {"open": true, "mut": "Barcode 8809416470726 · Tracking 10323100841207 · No order number · 1 unit · Registered by: Miranti (Center) 07-13 10:12 · Memo \"Box label damaged\""} |
| `QA-WFQ-02` | PASS | {"toast": "flex", "pc": "2"} |
| `QA-WFQ-03` | PASS | {"dialog": false, "toast": false, "overlays": 0} |
| `QA-WFQ-04` | PASS | <a> count = 0; candidate order-number tags = {'SPAN'} |
| `QA-WFQ-05` | PASS | {"open": true, "inputs": 0, "placeholders": 0} |
| `QA-WFQ-06` | PASS | after 1st={"noAnno": true, "dotsVisible": 0, "legendVisible": 0, "btn": "Show annotations"} after 2nd={"noAnno": false, "dotsVisible": 7, "legendVisible": 1, "btn": "Hide annotations"} |

---

## 4. Findings in detail

### F1 — `QA-LOAD-04` · exact `<th>` text assertion collides with the spec's own annotation dots · **FAIL · culprit: spec**

> **Spec:** "the pool table's `<th>` texts are exactly, in order: `Tracking No`, `Order No`, `Product Name`, … `Suspected Orders (Auto-matched)`, `Action` — 12 headers, no more, no fewer."

Three of those `<th>` elements contain an annotation `.dot` as a child:

```html
<th class="anno">Product Name<span class="dot" style="top:-11px;left:96px">4</span></th>
```

Read literally against the declared baseline (§8.0: "annotations are visible"), the page yields
`'Product Name4'`, `'Suspected Orders (Auto-matched)2'`, `'Action3'`. The assertion fails on 3 of 12
headers. Strip the `.dot` children and all 12 match exactly.

This is a spec fault, not a wireframe fault: §2.3 already declares `.dot` markup to be demo chrome
that "must not be built", so the spec knows the dots are noise — it just never tells the QA agent to
exclude them from a text assertion. An AI cannot resolve this without either reading §2.3 and making
a judgement call, or inspecting the DOM and reverse-engineering the intent. Both are exactly the
"further questions" §8.0 promises are unnecessary.

The same trap is latent in `QA-LOAD-03` (`.poolhead`'s `<b>` contains `<span id="poolCount">`) and
`QA-CMT-01` — but those two pass, because there the child's text is *part of* the expected string.
The spec is therefore inconsistent rather than uniformly wrong, which makes the trap harder to spot.

### F2 — `QA-M1-01` · modal `<header>` "exactly" assertion ignores the close button inside it · **FAIL · culprit: spec**

> **Spec:** "Then `#m-match` gains class `open` And its `<header>` text is exactly `Review & Match — Unrecognized Product` (em dash U+2014)."

**Page:** `'Review & Match — Unrecognized Product✕'`

```html
<header>Review &amp; Match — Unrecognized Product<button class="x" data-close>✕</button></header>
```

The `open` half of the assertion passes. The text half fails because `<header>` also holds the `✕`
close button — the same button `QA-EMPTY-05` separately instructs QA to click ("Repeat for the
header `✕`"), so the spec is demonstrably aware the button lives there. The em-dash guidance
(U+2014) is correct and was verified byte-wise; the failure is purely the trailing glyph.
Isolating the header's first text node gives an exact match.

### F3 — `QA-NEG-03` · double-click on `.xdel` double-decrements the counters · **FAIL · culprit: spec (mis-tagged `[WF]`); underlying new wireframe defect**

> **Spec:** "Given the baseline, When I dispatch two `click` events on the same `.xdel` within 200 ms, Then exactly one row is removed And both counters decrement by exactly 1 `[G-9]`."

**Page:** one row is removed (correct) but **both counters decrement by 2** —
`{"rowsRemaining": 2, "poolCount": "1", "poolCountBottom": "1"}`. The spec demands `2`; the page shows `1`.

Root cause (`index.html` L400–404):

```js
document.querySelectorAll('.xdel').forEach(b=>b.addEventListener('click',e=>{
  e.stopPropagation();
  b.closest('tr').remove();
  poolDec();
}));
```

After the first click the `<tr>` is detached, but the button is still a descendant of that detached
`<tr>`, so `b.closest('tr')` still resolves, `.remove()` is a silent no-op, and `poolDec()` runs a
second time. The counters and the rendered row count diverge — which is precisely what `[BR-41]` /
`QA-FURN-08` say must never happen ("counters are derived from rendered rows").

The sibling scenario `QA-NEG-01` (double-click on `Match to this product`) **passes**, because
`finishMatch()` guards with `const row=document.getElementById('poolrow1'); if(row){…}`. The guard
exists in one handler and is missing in the other.

**Culprit reasoning.** This defect is in neither `_wireframe-fixes.md` (WF-6 covers only the *missing*
confirm dialog / reason / toast on `✕`, not idempotency) nor §2.4 (limitation 6 covers `poolDec()`
flooring at 0, not double-firing) nor §2.5 (WF-NEW-A/B/C). Under the stated rule — a *known* WF defect
makes the wireframe the culprit — this is not known, so the fault is the spec's: it asserts as `[WF]`
a behavior the wireframe does not have. Fix either by re-tagging to `[ADMIN]` or by adding a WFQ
counterpart. Either way the wireframe defect should be filed as **WF-NEW-D**.

### F4 — `QA-SUS-05` · "any route/channel label on the page" has no selector · **AMBIGUOUS**

> **Spec:** "Given any route/channel label on the page, Then its computed `background-color` is transparent, it has no border, and its colour resolves to the ink colour `rgb(20, 16, 27)` (`#14101B`) — route labels are never coloured pills."

§8.0 promises "an AI agent must be able to run these with no further questions", but no selector,
class or label text identifies a "route/channel label". Both available readings were executed:

| Reading | Elements | Result |
|---|---|---|
| **A** — the four CSS route classes (`.tag-jit`, `.tag-smartbuy`, `.tag-wholesale`, `.tag-partnership`) | 2, both inside `#m-match` | **satisfies** the assertion |
| **B** — the route text rendered in the pool's Suspected Orders column (`JIT (Naver) · Processing`) | 4 | **violates** it: computed colour `rgb(126, 124, 131)` (`--ink-3`), not `rgb(20, 16, 27)` |

Reading A is also self-defeating as a page-level test: on the main page there are **zero** matching
elements, so a naive `all()` over an empty set passes vacuously and asserts nothing. Reading B is the
more natural sense of "on the page" — the pool grid is where an operator actually reads the route —
and under it the scenario FAILs on the colour clause. The verdict is recorded as AMBIGUOUS because
the spec does not let a QA agent choose. Note that `QA-M1-10` covers the modal case explicitly and
passes, which makes reading A largely redundant and reading B the probable intent.

### F5 — `QA-XPG-05` · tagged `[WF]` but only one of four clauses is wireframe-assertable · **UNRUNNABLE**

> **Spec:** "Given the closing wireframe at `…/wms2/closing/`, When a scan produces the unknown-order warning, Then the warning stays on the Closing page, no navigation to this page occurs, and no pool row or `#unrecognized-tracking` message is produced."

Three problems, none of which an AI can resolve unaided:
1. It targets a **different system under test** (the closing page) inside this page's `[WF]` block.
2. "no pool row … is produced" and "no `#unrecognized-tracking` message is produced" are server and
   Slack state. §8.0 defines `[ADMIN]` as exactly that — "server state, persistence, Slack delivery,
   cross-page navigation". These clauses are `[ADMIN]` wearing a `[WF]` tag.
3. The trigger has no click path: "When a scan produces the unknown-order warning" names no selector,
   button or input on the closing page, and §8.0's selector conventions cover only this page's IDs.

The single assertable clause — the warning stays put, no navigation — cannot carry the scenario's verdict.

---

## 5. Secondary observations (not verdict-bearing, but they cost an agent time)

- **`table.tbl` is not unique.** §8.0's selector convention addresses rows 2 and 3 as
  `table.tbl tbody tr:nth-of-type(2)`, but **two** `table.tbl` elements exist (the pool table and the
  candidate table inside `#m-match`), so that selector matches two rows. It works today only because
  the pool table precedes the modal in document order and an agent taking `.first` happens to land
  right. `QA-LOAD-05` has the same exposure with "the `<tbody>`" (2 match).
- **`.mockwrap` is not unique either.** `QA-A11Y-05` says "`.mockwrap` scrolls horizontally … the
  `Action` column's buttons remain reachable by scrolling". Two `.mockwrap` elements **nest**, and at
  900 px both overflow (outer 1280→900, inner 1457→1248). Scrolling only the outer one leaves the
  `✕` button at `left: 1045 px` in a 900 px viewport — still off-screen. Scrolling both makes it
  visible at `left: 836 px`. The scenario passes, but only for an agent that guesses to scroll both.
- **First `.it` is not `:first-of-type`.** `QA-CMT-06` says "click the `.star` button on the first
  item". `.paneheader` is also a `<div>`, so `.it:nth-of-type(1)` selects nothing. Positional
  addressing is required. §8.0's conventions do not mention this.
- **Unquantified assertions.** `QA-EMPTY-01`'s "the page layout has not collapsed" and `QA-NEG-01`'s
  "exactly one `#matchToast` display cycle occurs" have no measurable definition. Both were given a
  defensible proxy (mock height > 300 px; toast continuously `flex` then `none`) and passed, but the
  proxy is the tester's invention, not the spec's.
- **`QA-ROW-08`'s "no `<th>` click handler"** is not assertable from the DOM alone; it needed a CDP
  `DOMDebugger.getEventListeners` probe (result: `[]` on every `<th>`, so PASS). A QA agent without
  CDP access would have to downgrade this to AMBIGUOUS.
- **Correct and verified byte-wise:** every colour token (`#FFFBD6`, `#F59E0B`, `#0D6EFD`, `#198754`,
  `#7E7C83`, `#14101B`), the U+2013 en-dash in `QA-ROW-01`/`06`, the U+2014 em-dash in `QA-M1-01`,
  the straight ASCII quotes in `QA-M1-07`'s auto-comment string, the 4000 ms toast timeout
  (`QA-MATCH-05`'s 4.5 s bound), the 7-dot / 6-`<li>` legend count, and the 12-header inventory.
  This part of the spec is unusually precise.

---

## 6. Spec fixes required

Ordered by damage.

1. **`QA-NEG-03` — re-tag or re-baseline.** The wireframe double-decrements `#poolCount` /
   `#poolCountBottom` when `.xdel` is clicked twice. Either move the scenario to `[ADMIN]` and add a
   `[WF]` WFQ counterpart ("…both counters decrement by **2**; `[ADMIN]` counterpart asserts 1"), or
   fix the wireframe. File the underlying bug as **WF-NEW-D** in §2.5 and in
   `_plans/_wireframe-fixes.md`: *`.xdel`'s handler resolves `b.closest('tr')` on a detached row, so
   `poolDec()` fires again while `.remove()` no-ops (`index.html` L400–404); `finishMatch()` has the
   `if(row)` guard, `.xdel` does not.*
2. **`QA-LOAD-04` — say how to handle annotation dots.** Amend to: "…the pool table's `<th>` texts,
   **with any `.dot` annotation child removed**, are exactly, in order: …". Better still, add a global
   line to §8.0's selector conventions: *"All text assertions are made against the element's text with
   `.dot` descendants removed; `.dot` is demo chrome (§2.3)."* That single sentence also future-proofs
   `QA-LOAD-03`, `QA-LOAD-11` and any later header assertion.
3. **`QA-M1-01` — scope the header assertion.** Change to "its `<header>`'s leading text node is
   exactly `Review & Match — Unrecognized Product` (em dash U+2014), followed by the `✕` close
   button", or simply "its `<header>` text **starts with**…" — the phrasing `QA-CMT-01` already uses
   correctly for the badge case.
4. **`QA-SUS-05` — name the elements.** Replace "any route/channel label on the page" with an explicit
   selector set, and state which colour applies where. As written the pool-column route text is
   `--ink-3` gray, so if that text is in scope the expected colour must be
   `rgb(126, 124, 131)`, not `rgb(20, 16, 27)`. If only the modal's `.tag-*` spans are in scope, say so
   and note that the scenario is then a duplicate of `QA-M1-10`.
5. **`QA-XPG-05` — re-tag to `[ADMIN]`, or split.** Keep a `[WF]` clause for "the warning stays on the
   closing page, no navigation occurs" (and give it a concrete click path on that page), and move
   "no pool row / no `#unrecognized-tracking` message" to `[ADMIN]`. Also note in §8.0 that one `[WF]`
   scenario runs against a different URL — the current wording implies all `[WF]` runs hit this page.
6. **Disambiguate the shared selectors in §8.0.** State that `table.tbl` and `.mockwrap` each match two
   elements and that `[WF]` assertions are scoped to the **first** (the pool table / the outer scroller)
   unless the scenario names `#m-match`; and that `.it` items must be addressed positionally, not with
   `:nth-of-type`. Add that `QA-A11Y-05` requires scrolling **both** nested `.mockwrap` elements.
7. **Quantify the soft assertions.** Give `QA-EMPTY-01`'s "layout has not collapsed" and
   `QA-NEG-01`'s "exactly one display cycle" measurable definitions, and note that `QA-ROW-08`'s
   "no `<th>` click handler" needs a CDP listener probe (or drop that clause and keep the observable
   half: no sort glyph, no `onclick` attribute).

---

## 7. Verdict — can an AI run this spec's QA unaided?

**Yes, with caveats.**

62 of 67 `[WF]` scenarios (92.5 %) executed to a clean, unambiguous PASS straight from the spec text,
with no access to the HTML and no questions asked. That is a high bar cleared: the colour values,
Unicode dashes, timings, counts and literal strings are accurate to the byte, and the WFQ block did
its job perfectly — a hostile agent produced zero false bug reports against the wireframe's known
quirks, which is the failure mode this spec was clearly engineered to prevent.

The caveats are narrow and mechanical, not conceptual. Three scenarios fail on assertion *phrasing*
(embedded child elements defeating "exactly" comparisons) and would be fixed by one sentence in §8.0
plus two local edits. One scenario (`QA-SUS-05`) cannot be run without a decision from the author.
One (`QA-XPG-05`) is mis-tagged and points at another page. Left as-is, an unattended agent would
file three false defects against a correct wireframe (F1, F2) and miss a real one (F3) — the
`QA-NEG-03` FAIL is the only case where the page is genuinely wrong and the spec's tag hides it.

Fix items 1–3 in §6 and this spec reaches "zero questions" for practical purposes.
