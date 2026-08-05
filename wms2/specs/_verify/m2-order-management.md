# M2 — Adversarial QA Execution · `order-management.md` §8

**Method:** Verification Method 2 (hostile QA robot; the executor did not write the spec).
**Spec under test:** `wms2/specs/order-management.md` §8 (QA Acceptance Criteria)
**System under test:** `wms2/order-management/index.html` (identical to the deployed page)
**Harness:** Playwright 1.58.0 · headless Chromium · viewport 1500×1000 · `_verify/qa-order-management.py` (re-runnable)
**Raw results:** `_verify/qa-order-management.results.json`
**Date:** 2026-08-03

---

## 1. Methodology

1. **Extraction.** All `[WF]`-tagged scenarios were parsed out of §8. The population is **77** — matching the spec's own §8.0 declaration exactly. Rather than sample the required minimum of 25, **all 77 were executed**, so the result is a census, not an estimate. Adversarial weighting was applied to the *depth* of each check instead: every negative test, every toast/sound assertion, every modal chain, every cross-state flow and every exact-string assertion was executed literally rather than approximated.
2. **Literalism.** Only selectors, labels and expected strings supplied by the spec were used. Where the spec supplies a selector, that selector was used verbatim. Where it supplies only a string (e.g. "read the preview header"), the node was located by that string alone. Where it supplies neither a locator nor an assertable value, the scenario was recorded **AMBIGUOUS** and *not* improvised from knowledge of the page.
3. **§8.0 rule 5 enforced literally.** "Text assertions are byte-exact." No normalisation, trimming or whitespace collapsing was applied to any assertion the spec words as an exact read. Where a literal read failed but a lenient read passed, **both** results are recorded so blame can be assigned.
4. **State isolation.** Every scenario runs against a freshly loaded page with `window.__qaSentinel = 'om'` re-set, per §8.0 rule 1. No scenario inherits a toast node, a modal state or a checkbox state from its predecessor. This matters: `QA-SMP-30` and `QA-GBL-04` both have a "no `.gtoast` node exists" precondition that any shared-page runner would silently violate.
5. **Culprit attribution.** Every FAIL was cross-checked against `_plans/_wireframe-fixes.md`. A defect listed there makes the wireframe the culprit and the spec correct. A defect *not* listed there, where the wireframe behaves as intentionally built, makes the spec the culprit.
6. **Self-audit of the executor.** The first run produced 7 FAILs. Three were traced to defects in *this script*, not the spec — disclosed in §5 — and were repaired before the final run. The four surviving FAILs are reproducible and are spec faults.

### Tag-integrity checks run alongside

| Check | Result |
|---|---|
| Declared vs. actual scenario count | spec says 153 → **153** ✓ |
| `[WF]` / `[ADMIN]` split | spec says 77 / 76 → **77 / 76** ✓ |
| Per-block counts (IMP 52 · SMP 43 · LST 17 · CMT 23 · GBL 18) | **all five exact** ✓ |
| Negative-test count | spec says 64 = 41.8 % → **64 = 41.8 %** ✓ |
| Duplicate scenario ids | **none** ✓ |
| Numbering gaps within a block | **none** (1..n contiguous in all five blocks) ✓ |
| §8.6 matrix cites a non-existent scenario id | **none** ✓ |
| `[DC-n]` declared in §5 vs. covered by §8.6 | DC-1..DC-29 complete, **0 uncovered** ✓ |
| `[WF]` scenarios that turned out to be unrunnable in a static mock | **0** — no mis-tagging found in this direction |

The bookkeeping is the strongest part of this spec. Everything it counts about itself is true.

---

## 2. Results

**77 attempted · 72 PASS · 4 FAIL · 1 AMBIGUOUS · 0 UNRUNNABLE**

Culprit split for the 4 FAILs: **spec 4 · wireframe 0 · test-instruction 0.**
(Zero wireframe faults is itself a finding: all seven scenarios written to *document* a known wireframe defect — `QA-IMP-35`, `QA-SMP-30`, `QA-SMP-31`, `QA-SMP-33`, `QA-CMT-20`, `QA-GBL-09`, `QA-GBL-10` — reproduced the defect exactly as predicted, down to the `colspan="6"` value and the two-node toast overlap.)

| Scenario | Title | Verdict | Evidence |
|---|---|---|---|
| `QA-CMT-01` | Hub opens and closes from its trigger | **PASS** | open → badge 3 → close |
| `QA-CMT-02` | Tabs and pane headers | **PASS** | tabs=['@ Mentions 3', '★ Saved'] · header ok · action='Mark all read' flush right (left gap 291px, right gap 14px). NOTE: spec supplies no probe for 'right-aligned'; getComputedStyle(...).marginLeft returns '0… |
| `QA-CMT-03` | Saved tab | **PASS** | ['Order MKT-40218'] · header/hint byte-exact · mentions hidden |
| `QA-CMT-04` | Search hides the tabs and renders a result header | **PASS** | tabs=none · csr shown · header='3 results · newest first · click to open the order' |
| `QA-CMT-05` | (neg) Search with no hits [E-38] | **FAIL** | literal read of "[data-pane=\"csr\"] contains exactly the text 'No matching comments'": pane textContent is '0 results · newest first · click to open the orderNo matching comments' — the result header is also … |
| `QA-CMT-06` | Clearing the search restores the tabs | **PASS** | {'tabs': 'flex', 'csr': 'none', 'onTab': 'mentions', 'onPane': 'block'} |
| `QA-CMT-07` | Star toggle | **PASS** | initial class='star' → on/rgb(245, 158, 11) → off/rgb(187, 186, 190) |
| `QA-CMT-08` | (neg) Search input cannot inject markup [E-48] | **PASS** | empty state · 0 <b> nodes — query escaped |
| `QA-CMT-15` | Numeric-order search returns sales orders only | **PASS** | {'ph': '2 results · newest first · click to open the order', 'rows': ['Order 421771', 'Order 421502']} |
| `QA-CMT-16` | Author search and `<mark>` highlighting | **PASS** | header ok · rows=['Order MKT-40233', 'Order MKT-40191'] · marks fw700 |
| `QA-CMT-17` | Results are ordered newest-first | **PASS** | ['Order MKT-40233', 'Order MKT-40218', 'Order 421771', 'Order MKT-40191', 'Order 421502'] |
| `QA-CMT-18` | (neg) `Mark all read` is inert in the mock | **PASS** | 3 unread before and after · badge still '3' |
| `QA-CMT-19` | Unread and saved states in the demo data | **PASS** | [{'o': 'Order MKT-40233', 'unread': True, 'star': False}, {'o': 'Order MKT-40218', 'unread': True, 'star': True}, {'o': 'Order 421771', 'unread': True, 'star': False}] · saved=['Order MKT-40218'] |
| `QA-CMT-20` | (neg) The hub does not close on an outside click — documents [WF-21 · proposed] | **PASS** | hub stays open on outside click · no document-level handler — defect reproduced as specified |
| `QA-CMT-21` | Corpus mixes marketing and sales entities | **AMBIGUOUS** | When-clause is 'search for an empty-adjacent common term and read the full dataset via QA-CMT-17'. No concrete query string is given ('empty-adjacent common term' is undefined; the empty query hides the csr pa… |
| `QA-GBL-01` | Legend closing paragraph [L-F1] | **PASS** | both sentences present byte-exact |
| `QA-GBL-02` | Toast placement and styling [L-F5] | **PASS** | {'pos': 'fixed', 'top': '16px', 'right': '16px', 'z': '200', 'bg': 'rgb(25, 135, 84)', 'color': 'rgb(255, 255, 255)', 'fw': '700', 'fs': '13.5px', 'smfs': '11.5px', 'smop': '0.9'} |
| `QA-GBL-03` | (neg) No reload after any action [E-43] [G-2] | **PASS** | 3 modals opened+closed · #mktConfirm · #sampCancelBtn · hub open/close · #annoToggle → sentinel intact |
| `QA-GBL-04` | (neg) Every dismissal path creates nothing | **PASS** | backdrop / ✕ / Cancel all close · .gtoast stays 0 |
| `QA-GBL-09` | (neg) Two independent toast nodes — documents [WF-18 · proposed] [E-62] | **PASS** | [{'id': 'gtoast', 'disp': 'block', 'top': '16px', 'right': '16px'}, {'id': 'gtoast2', 'disp': 'block', 'top': '16px', 'right': '16px'}] — overlap defect reproduced as specified |
| `QA-GBL-10` | (neg) `Esc` does not dismiss anything — documents [WF-20 · proposed] [E-97] | **PASS** | all four surfaces survive Escape · no 'keydown' string in the file — defect reproduced as specified |
| `QA-GBL-11` | (neg) Wireframe-only chrome inventory (must not ship) | **PASS** | wf-bar 4 buttons exact · 9 .dot · 1 .legend |
| `QA-GBL-12` | Annotation toggle | **PASS** | toggle both directions verified |
| `QA-GBL-13` | (neg) No audio anywhere [G-3] | **PASS** | 0 of 5 tokens present |
| `QA-GBL-14` | (neg) No scanner surface [G-1] | **FAIL** | code paths that return focus to an input after an action (.focus() call sites): spec says 0 · page has 2 |
| `QA-GBL-15` | Layout minimums [E-96] | **PASS** | {'mock': '1240px', 'tbl': ['1180px', '1180px'], 'wrap': 'auto'} |
| `QA-IMP-01` | Open the import modal from the filter bar | **PASS** | open=True · header='Marketing Order Import✕' · gtoast=0 · sentinel held |
| `QA-IMP-02` | Open the import modal from the wf-bar | **PASS** | wf-bar opens #m-import; modal innerHTML byte-identical to filter-bar entry |
| `QA-IMP-03` | Step 1 copy | **PASS** | bold='1. Template' · btn='⬇ Download Template (.xlsx)' class='btn btn-line btn-sm' · helper byte-exact |
| `QA-IMP-05` | Order Type default state | **PASS** | seed=on/'Influencer Seeding' · custom='✎ Custom' no .on · #otCustom display:none |
| `QA-IMP-06` | Order Type custom toggle and focus | **PASS** | chip swap ok · display=inline-block · placeholder exact · activeElement=#otCustom |
| `QA-IMP-07` | Toggling back hides the custom input but keeps its value | **PASS** | display=none · seed=on · value retained 'Pop-up event giveaway' |
| `QA-IMP-08` | PIC defaults and helper copy | **PASS** | options/selected/btn/placeholder/helper all byte-exact |
| `QA-IMP-09` | PIC custom toggle and focus | **PASS** | toggle inline-block → focus → none |
| `QA-IMP-10` | Upload step copy | **PASS** | '4. Upload' bold present · dropzone text byte-exact |
| `QA-IMP-11` | Preview header format | **PASS** | 'Preview — mkt_seeding_batch3.xlsx · 12 rows parsed · 0 errors' (NOTE: spec gives no selector for 'the preview header') |
| `QA-IMP-12` | Preview table headers | **FAIL** | the seven headers (byte-exact per §8.0 rule 5): spec says ['Recipient', 'Country', 'SKU', 'Product Name', 'Qty', 'Campaign', 'Carrier (auto)'] · page has ['Recipient', 'Country', 'SKU', 'Product Name', 'Qty', … |
| `QA-IMP-13` | Brand-bold product names [G-6] | **PASS** | rows 1-3 innerHTML byte-exact with <b> brand wrapper |
| `QA-IMP-14` | Connected-carrier rendering [L-M1b] | **PASS** | 3 GB rows · all 'YunExpress' / rgb(25, 135, 84) / 700 |
| `QA-IMP-15` | (neg) Unconnected carrier does not block [L-M1b] [E-7] | **PASS** | PE row copy/colour/weight exact · #mktConfirm disabled=False aria-disabled=None |
| `QA-IMP-16` | Confirm button label format | **PASS** | label byte-exact · class contains btn-mkt |
| `QA-IMP-17` | Confirm toast text, colour, dismissal and no reload [E-43] [E-45] | **PASS** | toast text/colour/geometry exact · hidden after 2.9s · sentinel held |
| `QA-IMP-18` | Modal note copy (BR-1 operator-visible) | **PASS** | byte-exact incl. preserved 'Outbonded' |
| `QA-IMP-19` | (neg) No stock-error copy anywhere in the modal [E-20] | **PASS** | 0 forbidden substrings · 1× 'stock' in 'marketing view) regardless of stock or inbound status.\n \n \n ' |
| `QA-IMP-20` | (neg) No print, scan or carrier-picker affordance in the modal | **PASS** | buttons=['✕', '⬇ Download Template (.xlsx)', 'Influencer Seeding', '✎ Custom', '✎ Custom', 'Cancel', 'Confirm Import (12 orders)'] · inputs=[{'t': 'text', 'r': None}, {'t': 'text', 'r': None}] · 1 select = PIC |
| `QA-IMP-35` | (neg) Preview collapse row under-spans — documents [WF-15 · proposed] | **PASS** | 1 colspan cell · text exact · colspan=6 vs 7 headers — defect reproduced as specified |
| `QA-IMP-36` | Preview row arithmetic matches the header count | **PASS** | 4 named + '⋯ +8 more rows' → 4+8=12 consistent with header |
| `QA-IMP-37` | (neg) The dropzone is inert in the mock | **PASS** | no filechooser event · 0 file inputs · preview innerHTML unchanged |
| `QA-IMP-38` | Modal geometry and dismissal controls | **PASS** | class='modal wide anno' · max-width=720px · ✕ present · foot=['Cancel', 'Confirm Import (12 orders)'] |
| `QA-IMP-39` | (neg) Repeated confirms reuse one toast node | **PASS** | 1 node, id='gtoast', reused across two confirms |
| `QA-LST-01` | Placeholder contract text | **PASS** | dot='4' display='inline-flex'; strings present (NOTE: literal 'reads' fails — textContent starts with the dot glyph '4') |
| `QA-LST-02` | MKT style tokens exist | **PASS** | --mkt=#7C3AED --mkt-soft=#F3EEFF · 4 rules present |
| `QA-LST-03` | Header and count [L-F2] | **PASS** | byte-exact |
| `QA-LST-04` | (neg) Bulk Hold Shipment must not exist [L-3] | **PASS** | 0 control hits · legend 3 retains the negative entry · document-wide occurrences=1 (all in the legend) |
| `QA-LST-05` | (neg) No print or scan surface anywhere on the page | **PASS** | 32 buttons, none 'Print' · no file/scan input · 0 <audio> |
| `QA-LST-06` | Action-row inventory [L-F4] | **PASS** | ['⧉ Merge Orders', 'Sample Assignment ON', 'Cancel Sample Assignment'] · .sel-info='2 selected' rgb(88, 45, 181) fw700 |
| `QA-LST-07` | Filter-bar inventory [L-F3] | **PASS** | {'dates': ['2026-06-01', '2026-07-14'], 'inps': ['Search (order / product)', 'Search PIC'], 'sels': ['All Status', 'Country: AU', '15'], 'cbs': [{'l': 'Order #', 'c': True}, {'l': 'Tracking #', 'c': False}], '… |
| `QA-LST-12` | Global navigation shell [L-F6] | **FAIL** | quick links (byte-exact per §8.0 rule 5): spec says ['Agent Telemetry', 'Role Assets', 'Shared Asset Health', 'SkinSeoul WP Admin'] · page has ['AgentTelemetry', 'RoleAssets', 'Shared AssetHealth', 'SkinSeoulW… |
| `QA-LST-13` | (neg) No pagination is rendered in the mock | **PASS** | 0 .pager elements |
| `QA-LST-17` | (neg) No MKT row is rendered in the mock | **PASS** | 0 tr.mkt elements |
| `QA-SMP-01` | ON button opens M2 | **PASS** | open=True · header='Sample Assignment ON✕' · sentinel held |
| `QA-SMP-02` | Target radios | **PASS** | 2 radios · first checked · labels ok (trimmed). Literal byte-exact label match=False (DOM has leading space ' All new orders in this period') |
| `QA-SMP-03` | Period fields and `forever` default | **PASS** | 2026-07-23 / 10:00 / ~ / 'End date' / 'Time' / forever checked — all present |
| `QA-SMP-04` | (neg) Modal note and absence of any sample-type picker | **PASS** | note contains both phrases · 0 <select> in #m-sampleon |
| `QA-SMP-05` | Footer buttons | **PASS** | [{'t': 'Cancel', 'c': 'btn btn-gray btn-sm'}, {'t': 'Start Assignment (ON)', 'c': 'btn btn-green btn-sm'}] |
| `QA-SMP-15` | Cancel button opens M3 | **PASS** | open=True · header='Cancel Sample Assignment — Current Assignment Periods✕' |
| `QA-SMP-16` | M3 table content | **PASS** | headers + all 3 rows byte-exact; row1 'forever' in <b> |
| `QA-SMP-17` | (neg) Ended row has no checkbox element [E-27] | **PASS** | [{'status': 'Active', 'cb': 1}, {'status': 'Active', 'cb': 1}, {'status': 'Ended', 'cb': 0}] |
| `QA-SMP-18` | M3 note copy | **PASS** | byte-exact |
| `QA-SMP-19` | Cancel toast text and no reload | **PASS** | btn bg=rgb(220, 53, 69) · toast text byte-exact · sentinel held |
| `QA-SMP-28` | M2 opens from the wf-bar | **PASS** | wf-bar opens M2; innerHTML identical to action-row entry |
| `QA-SMP-29` | M3 opens from the wf-bar | **PASS** | wf-bar opens M3; innerHTML identical to action-row entry |
| `QA-SMP-30` | (neg) `Start Assignment (ON)` is silent — documents [WF-16 · proposed] | **PASS** | modal closed · 0 toasts · button has no id — defect reproduced as specified |
| `QA-SMP-31` | (neg) Cancel toasts at zero selection — documents [WF-17 · proposed] | **PASS** | disabled=False · no dialog · #gtoast2 shown — defect reproduced as specified |
| `QA-SMP-32` | M3 default checkbox states | **PASS** | {'per': [[True], [False], []], 'total': 2} |
| `QA-SMP-33` | (neg) `forever` does not disable the end fields — documents [WF-19 · proposed] | **PASS** | [{'p': 'End date', 'd': False}, {'p': 'Time', 'd': False}] · typed input accepted — defect reproduced as specified |
| `QA-SMP-34` | Cancel toast uses its own node | **PASS** | ids=['gtoast2'] · gtoast2.class='gtoast' |

---

## 3. FAIL analysis — all four culprits are the spec

### F-1 · `QA-IMP-12` — the annotation dot is inside the `<th>` the spec asserts byte-exact

*Spec says:* "the seven headers are `Recipient`, `Country`, `SKU`, `Product Name`, `Qty`, `Campaign`, `Carrier (auto)`, and `#m-import thead th` has length `7`."
*Page does:* `['Recipient','Country','SKU','Product Name','Qty','Campaign','Carrier (auto)M1b']`

The seventh header is `<th class="anno">Carrier (auto)<span class="dot">M1b</span></th>`. §8.0 fixes the precondition as "annotations **shown** (the default)", and §8.0 rule 5 makes text assertions byte-exact — so the spec's own harness rules guarantee this assertion cannot pass. The count assertion (`length 7`) passes.

**Culprit: spec.** Not the wireframe. `_wireframe-fixes.md` §E explicitly protects annotation dots as intentional chrome, and `QA-GBL-11` *requires* `.dot` elements to exist. The wireframe is behaving as designed and as two other scenarios demand.
**Damage:** an unaided AI runner reports a false defect against a correct wireframe, on the single most-cited table in the spec.

### F-2 · `QA-LST-12` — `<br>` inside the nav quick links

*Spec says:* quick links `Agent Telemetry`, `Role Assets`, `Shared Asset Health`, `SkinSeoul WP Admin`.
*Page does:* `['AgentTelemetry','RoleAssets','Shared AssetHealth','SkinSeoulWP Admin']`

The markup is `<span class="navlink">Agent<br>Telemetry</span>` — a deliberate two-line rendering that mirrors the live admin nav. `textContent` drops the `<br>` without substituting a space; `innerText` substitutes `\n`. Neither yields the spec's string, so there is no reading under which the byte-exact assertion passes.

**Culprit: spec.** No entry in `_wireframe-fixes.md` treats the two-line quick links as a defect, and the rest of `QA-LST-12` (brand, six `▾` menus, badge `3`, user chip, `Logout`) passes exactly as written.
**Damage:** same false-defect failure mode as F-1, on the global nav shell — a component shared by all eight screens, so the same error will propagate into every other spec that asserts `.navlink` text.

### F-3 · `QA-GBL-14` — the spec contradicts itself about focus

*Spec says (`QA-GBL-14`):* "…and **no code path returns focus to an input after an action** — the `[G-1]` invariants have no surface here."
*Spec also says (`QA-IMP-06`):* "…and `document.activeElement === document.getElementById('otCustom')`."
*Spec also says (`QA-IMP-09`):* "…and `document.activeElement === document.getElementById('picCustomIn')`."
*Page does:* exactly 2 `.focus()` call sites, both firing after a click. `QA-IMP-06` and `QA-IMP-09` **PASS**; `QA-GBL-14`'s fourth clause therefore **FAILS**.

These three `[WF]` scenarios cannot all hold against any implementation. The intent of `QA-GBL-14` is plainly scanner refocus (`[G-1]`, BR-28), but as written the clause is unscoped and catches the two legitimate custom-input focus moves. Its other three clauses (no `autofocus`, nothing focused on load, no select-on-focus) pass cleanly.

**Culprit: spec.** This is the most damaging of the four because it is not a transcription slip — it is a **logical contradiction inside §8** that no amount of care by the runner can resolve, and whichever way the runner resolves it, one scenario is falsely reported.

### F-4 · `QA-CMT-05` — "contains exactly" is unsatisfiable as worded

*Spec says:* "Then `[data-pane="csr"]` contains exactly the text `No matching comments` and zero result rows."
*Page does:* `[data-pane="csr"]` textContent = `'0 results · newest first · click to open the orderNo matching comments'`

The empty state is rendered *inside* the same pane as the result header, which the search routine always writes (`'<div class="paneheader">'+hits.length+' results …'`). The zero-rows half of the assertion passes; the "contains exactly" half cannot pass for any input. Under the lenient reading — a `.empty` node whose text is exactly `No matching comments` — the scenario passes.

**Culprit: spec.** The wireframe's empty state is correct and `QA-CMT-08` depends on the same rendering.
**Damage:** lower than F-1..F-3 (a careful runner will pick the lenient reading), but it still forces an interpretive decision the spec promised not to require.

---

## 4. AMBIGUOUS

### A-1 · `QA-CMT-21` — no input is specified

> "**When** I search for an empty-adjacent common term and read the full dataset via QA-CMT-17"

"An empty-adjacent common term" names no string. The literal empty query is not it — an empty query hides the `csr` pane and restores the tabs (`QA-CMT-06`), so the corpus cannot be read at all. The cross-reference to `QA-CMT-17` supplies the only concrete input in scope (`4`), and under that reading the Then-clause holds: rows are `MKT-40233`, `MKT-40218`, `421771`, `MKT-40191`, `421502` — 3 marketing + 2 sales entities in one list, exactly as claimed.

Recorded AMBIGUOUS rather than PASS because the scenario requires the runner to *infer* its own input, which is the specific failure mode this verification exists to detect. The fix is one word: replace the phrase with `4`.

---

## 5. Executor self-disclosure — defects in *this* script, not the spec

Run 1 produced 7 FAILs. Three were mine and were repaired before the final run. They are listed because they are exactly the traps a future re-runner will hit:

| Case | My defect | Repair |
|---|---|---|
| `QA-CMT-02` | Probed "right-aligned" via `getComputedStyle(small).marginLeft`, expecting `auto`. Chromium resolves auto flex margins to `0px` in the computed-value stage, so the obvious probe reports a false failure. | Switched to `getBoundingClientRect()` — left gap 291 px vs right gap 14 px. **PASS.** *The spec supplies no probe for "right-aligned", so this trap is latent for any runner.* |
| `QA-IMP-19` | Context window around the `stock` hit was 28 chars, truncating the phrase it was asserting. | Widened the window. **PASS** — 0 forbidden substrings, exactly 1 occurrence of `stock`, inside the BR-1 note. |
| `QA-LST-02` | Asserted the literal hex `#EBE1FF` against `cssRules[].cssText`, which the CSSOM re-serialises as `rgb(235, 225, 255)`. | Accept either form. **PASS.** *The spec quotes stylesheet rules in authored-hex form; a runner reading them literally out of the CSSOM will fail on every hex colour.* |

Two of these three (`QA-CMT-02`, `QA-LST-02`) are latent traps created by spec wording and are carried into §6 as fixes.

---

## 6. Spec fixes required

Ordered by damage. F-numbers refer to §3.

**S-1 (blocker, F-3) — resolve the focus contradiction in `QA-GBL-14`.**
Replace "no code path returns focus to an input after an action" with a scanner-scoped clause, e.g. "no code path returns focus to a **scan** field after an action — the two `.focus()` calls on `#otCustom` and `#picCustomIn` are custom-input affordances asserted by QA-IMP-06 and QA-IMP-09, not `[G-1]` surfaces." As written, §8 contains three mutually unsatisfiable `[WF]` scenarios.

**S-2 (blocker, F-1) — make `QA-IMP-12` executable under its own preconditions.**
Either scope the selector (`#m-import thead th` → read `firstChild.textContent`, or exclude `.dot`) or state the expected seventh value as `Carrier (auto)M1b` with a note that the suffix is the annotation dot. The current wording is unsatisfiable while annotations are shown, which §8.0 mandates.

**S-3 (blocker, F-2) — fix the nav quick-link strings in `QA-LST-12`.**
The four `.navlink` spans contain `<br>`. Either give the expected `textContent` verbatim (`AgentTelemetry`, `RoleAssets`, `Shared AssetHealth`, `SkinSeoulWP Admin`) or instruct the runner to normalise `<br>` to a space before comparing. This wording is shared with the other seven screen specs and should be fixed in all of them at once.

**S-4 (blocker, F-4) — reword `QA-CMT-05`.**
"`[data-pane="csr"]` contains exactly the text `No matching comments`" → "`[data-pane="csr"] .empty` reads exactly `No matching comments`, `[data-pane="csr"] .it` has length `0`, and the pane header reads `0 results · newest first · click to open the order`."

**S-5 (blocker, A-1) — give `QA-CMT-21` a concrete input.**
"an empty-adjacent common term" → "`4`".

**S-6 (high) — amend §8.0 rule 5 to say how whitespace is handled.**
Three scenarios (`QA-SMP-02`, `QA-SMP-03`, `QA-LST-07`) assert label text that the DOM carries with a leading space, because the `<input>` precedes the text inside the `<label>`. They pass only if the runner trims — which rule 5, read literally, forbids. Add: "label text is compared after trimming leading/trailing whitespace; all other text is byte-exact."

**S-7 (high) — give `QA-CMT-02` a probe for "right-aligned".**
The natural probe (`marginLeft === 'auto'`) returns `0px` in Chromium. Specify the geometric check, or drop the adjective and assert only that the action is the `<small>` in the pane header.

**S-8 (medium) — quote stylesheet rules in `QA-LST-02` in CSSOM-serialised form, or say which form to expect.**
`#EBE1FF` comes back from `cssRules[].cssText` as `rgb(235, 225, 255)`. Same trap will recur in every spec that quotes a hex colour out of a stylesheet rule.

**S-9 (medium) — supply a selector for "the preview header" in `QA-IMP-11`.**
Currently locatable only by searching all `<b>` nodes in `#m-import` for one starting `Preview`. Suggest `#m-import b` filtered, or add an id.

**S-10 (medium) — define "identical content" in `QA-IMP-02`, `QA-SMP-28`, `QA-SMP-29`.**
Three scenarios assert a modal opened from the wf-bar has "identical content" to the same modal opened from the page, without saying what to compare. This run used `.modal` `innerHTML` equality and all three passed, but the comparison basis is the runner's invention.

**S-11 (low) — `[WF-15]`..`[WF-21]` do not exist in `_plans/_wireframe-fixes.md`.**
Seven `[WF]` scenarios (`QA-IMP-35`, `QA-SMP-30`, `QA-SMP-31`, `QA-SMP-33`, `QA-CMT-20`, `QA-GBL-09`, `QA-GBL-10`) cite defect ids `WF-15` through `WF-21`; the backlog file contains only `WF-1`..`WF-14`. The spec self-labels each as "· proposed", so this is not a contradiction — but a QA runner instructed to cross-check the backlog finds nothing, and the wireframe-edit pass has no ticket to work from. Either append the seven proposals to `_wireframe-fixes.md` or state in §8.0 that "· proposed" means "not yet in the backlog file".

### Not a fix — confirmed correct

The seven defect-documenting scenarios reproduced their defects exactly: `colspan="6"` against 7 headers; `Start Assignment (ON)` silent and id-less; `#sampCancelBtn` toasting at zero selection with no dialog; `forever` leaving the end fields enabled and writable; the hub surviving an outside click with no document-level handler; two toast nodes at identical fixed coordinates; `Escape` dismissing nothing with no `keydown` string anywhere in the file. All toast text, all modal copy, all colour tokens (`rgb(25,135,84)`, `rgb(180,83,9)`, `rgb(245,158,11)`, `rgb(187,186,190)`, `rgb(88,45,181)`), all layout minimums and the full comment-search corpus behaviour (5 entries, recency ordering, `<mark>` highlighting, HTML escaping) matched byte-for-byte.

---

## 7. Verdict — can an AI run this spec's QA unaided?

**Yes, with caveats.**

72 of 77 `[WF]` scenarios executed and passed on the first literal reading, with no questions asked and no page knowledge beyond what §8 supplies. Selector coverage is genuinely high, the exact strings are right down to `·`, `—`, `→`, `⋯` and the preserved misspelling `Outbonded`, the colour reference table in §8.0 is accurate, the reload-sentinel and dual-toast-node harness rules are necessary and correct, and every number the spec asserts about itself is true. That is well above what a spec normally delivers.

The caveats are real but narrow and all mechanical: **four scenarios cannot pass as worded** (three because a byte-exact assertion collides with markup the spec elsewhere requires; one because of a logical contradiction with two other scenarios in the same document), and **one requires the runner to invent its own test input**. An unaided AI would file 4 false defects against a correct wireframe and would have to guess once. None of the five is a judgement call about product behaviour — each is fixed by editing one clause.

After S-1 through S-5, this spec reaches zero-question QA. S-6 through S-11 are hardening.
