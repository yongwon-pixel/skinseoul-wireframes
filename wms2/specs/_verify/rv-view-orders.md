# RV — Independent Re-Verification: `view-orders.md` (post-remediation)

**Target spec** `wms2/specs/view-orders.md` (v1.2, 2,226 lines) · **Wireframe** `wms2/view-orders/index.html` (1,847 lines)
**Prior findings** `_verify/m1-view-orders.md` (1 MAJOR + 6 MINOR) · `_verify/m2-view-orders.md` (S-0…S-12; 29 FAIL / 2 AMBIGUOUS / 1 UNRUNNABLE)
**Verifier:** independent (did not author the spec, the wireframe, or the remediation). All counts re-derived by script (`rv_counts_vo.py`); all QA re-runs executed with Playwright headless Chromium 1280×900 against `file://…/view-orders/index.html` implementing the **remediated** §8.0 rules only. **Date:** 2026-08-03.

---

## 1. Count re-derivation — spec's stated numbers vs my extraction

| Metric | Spec §8.14 / prose claims | My independent derivation | Match |
|---|---|---|---|
| Total QA scenarios | 277 | **277** bold `**QA-***` definitions, 0 duplicates | ✓ |
| `[WF]` | 135 | **135** | ✓ |
| `[ADMIN]` | 142 | **142** (135+142=277) | ✓ |
| DEFERRED | 1, inside the 142 | **1** — `QA-CV-22 [ADMIN] — DEFERRED` (line 1977), tagged, counted in ADMIN | ✓ |
| Negatives | 91 (32.9 %) | **91** rows carry an explicit `*negative*` tag on the header line. (A looser rule that also counts QA-M4-07's body-prose `*(negative half)*` gives 92; §8.14's metric is "explicitly **tagged**", and 91 is the header-tag count — consistent.) | ✓ |
| DC range | 47 | **DC-1…47**, 47 distinct, no gaps | ✓ |
| E IDs / entries | 93 IDs / 92 entries | **E-1…93 cited, no gaps; 92 §7 table rows**, one merged row `**E-18 = E-51**` | ✓ |
| BR range | 1…57 | **BR-1…57**, no gaps | ✓ |
| L-units | 69 | **69** = 61 `####` unit headings (incl. `[L-F1]`–`[L-F8]`) + 8 modal units as `###` §3.10–3.16 headings (M3/M3b share one heading). Sub-keys `Fa/Fb/Fc` declared non-units in §2.1 | ✓ |
| PD citations | 151→161, zero removals, +8 PD-49 +2 PD-80 | `git diff HEAD`: tagged-citation net = **PD-49 +8, PD-80 +2, all others 0; zero negative nets**. Absolute: 161 `[PD-n · OWNER-PENDING]` citations, 33 distinct PDs (§9.2 says 33) | ✓ |
| §8 coverage guarantee | 0 unreferenced | Machine-checked: **0** DC, **0** E, **0** BR, **0** L-units unreferenced in §8 | ✓ |

**Counts verdict: all stated numbers verified true by independent extraction.**

---

## 2. Resolution table — every prior defect

### M1 (coverage audit) defects

| Defect | Status | Evidence (current file) |
|---|---|---|
| **D1 MAJOR — `[E-6]` plan collision** | **RESOLVED** (option b) | §7 preamble, line 969: *"**`E-6` differs from the plan's `E-6` — read this before cross-referencing.** `_plans/view-orders.B.md` assigns E-6 = Coupang `[V1]`… on this page `E-6` is the occupied-location rejection… It is **not repaired by renumbering** — `_review.md` §3.2 forbids renumbering an assigned ID… Anyone reconciling this spec against the plan must map plan-E-6 → `[BR-2]`."* E-6's row (line 980) unchanged in meaning; renumbering correctly refused per rule 5 / `_review.md` §3.2. |
| **D2 MINOR — BR-33/34/35/36 restate G-rule bodies** | **RESOLVED** | Lines 717–720: BR-33 *"**No page delta on `[G-7]`'s append-only clause.**…"*, BR-34 *"**No page delta on `[G-9]`.** This page's scope… is enumerated once, at `[E-13]`…"*, BR-35 *"**No page delta on `[G-15]`:** no control on this page is role-gated…"*, BR-36 now a real page delta (*"brand-in-bold prefix applies to **both** … columns"*). No rule body restated. |
| **D3 MINOR — `[L-S1-F(a)]` key format** | **RESOLVED** | §2.1 line 81 declares `[L-S1-Fa]`/`[L-S1-Fb]`/`[L-S1-Fc]` ("holds **three** rules" — the remediator found one more than M1 assumed), sub-keys declared non-units, `F(a)` form explicitly retired. 12 `Fa/Fb/Fc` uses; the only 2 remaining `F(a)` strings are the retirement declarations themselves (lines 81, 2194). |
| **D4 MINOR — shorthand date `07-09`** | **RESOLVED** | §10.1 line 2114: `proposed 2026-07-09 → **adopted 2026-08-03**`. No shorthand dates remain in spec prose. |
| **D5 MINOR — QA-CV-22 no tier tag** | **RESOLVED** | Line 1977: `**QA-CV-22 [ADMIN] — DEFERRED**`; §8.0 Tags paragraph defines the third marker: *"**`— DEFERRED`** … counted in the totals but is never executed and never fails."* §8.14 books it inside the 142. |
| **D6 MINOR — QA-S6-07 `[WF]` expected-to-fail unprotocolled** | **RESOLVED** | §8.0: *"Before filing any `[WF]` failure, read §2.3 **and** §2.4… Exactly **one** `[WF]` scenario … is therefore **expected to fail today**: **QA-S6-07** (defect **WF-1**…)."* |
| **D7 MINOR — "8 slash-groups" miscount** | **RESOLVED** | §5 preamble line 749: *"**9 groups covering 11 literal names**… (9 groups; the two slash-groups contribute two literal names each)"*. |

### M2 (adversarial QA) findings

| Finding | Status | Evidence |
|---|---|---|
| **S-0** byte-for-byte unsatisfiable | **RESOLVED** | §8.0 rule 6: whitespace-collapsed equality (`s.replace(/\s+/g,' ').trim()`); byte comparison explicitly declared *"**not** a valid reading"*. |
| **S-1** annotation chrome (21 FAILs) | **RESOLVED** | §8.0 rule 6b: strip every `.dot` descendant + modal `header` trailing `button.x` before comparison and when locating controls. All 21 previously-failing scenarios re-run PASS (§3 below). |
| **S-2** Deleo legend self-falsification | **RESOLVED** | QA-S1-09 / QA-NG-08 now sweep `document.body.innerText` *"**after excluding every `.legend` subtree**"* with in-row rationale. Both re-run PASS. |
| **S-3** `#s2 tbody tr` wrong selector | **RESOLVED** | §8.0 rule 5 two-table clause (log header inside `<tbody>`, "State 2 returns 9 rows, not 4"); QA-S2-01 now `#s2 table.tbl tbody tr`. Re-run: 4 rows, PASS (bare selector still returns 9, as documented). |
| **S-4** QA-S1-12 class on wrong node | **RESOLVED** | Row asserts the **`span`** (`<td><span class="qty qty-warn">2</span></td>`) and warns the cell-level assertion *"fails on a correct page"*. Re-run PASS. |
| **S-5** QA-NG-10 vs QA-S6-02 | **RESOLVED** | QA-NG-10 carves out *"the cross-page deep links required by `[G-12]` — today exactly one"*. Re-run PASS. |
| **S-6** QA-CV-18 uppercase | **RESOLVED** | Now "bold text on a transparent background … canonical casing"; explicitly forbids `text === text.toUpperCase()`. Re-run PASS (6 `JIT (Coupang)` labels, 0 violations). |
| **S-7** QA-S6-14 mis-quoted fragment | **RESOLVED** | Fragment now `The request list qty cell shows the edit history (300→120).` with capital `T` and period, annotated sentence-initial. Re-run: all 4 fragments found, PASS. |
| **S-8** QA-S6-10 `[WF]`/L-13 conflict | **RESOLVED** | QA-S6-10 is now a `[WF]` **negative** documenting L-13 (expects **0** visible `.flsave`) + new `**QA-S6-45 [ADMIN]**` positive twin (line 1598). Re-run: 0 visible `.flsave`, PASS. Totals rebooked in §8.14. |
| **S-9** QA-GL-02 unobservable | **RESOLVED** | Asserts three verbatim substrings against concatenated inline `<script>` source. Re-run: all three present, PASS. |
| **S-10** QA-CV-11 no quoted strings | **RESOLVED** | Both legend sentences now quoted verbatim. Re-run: both found as substrings of `#s4` text, PASS. |
| **S-11** "visible" undefined | **RESOLVED** | §8.0 rule 7b: `getClientRects().length > 0`; `offsetParent` declared invalid with the three `position:fixed` culprits named. |
| **S-12** footer element unnamed | **RESOLVED** | §8.0 rule 7c: `.foot`, `.tabpane[data-pane="mentions"|"saved"]`, `.ordercard`, `.bulkbar`, `.cnt`. |

### M3a cross-page items naming this page (spot-verified)

| Item | Status | Evidence |
|---|---|---|
| D1 Cancel-Inbound three-way contract | **RESOLVED** on this page | `[BR-57]` (line 741) books `ADJUST(−remainder)` under `[DC-39]` `origin=cancel_inbound_remainder` in the same transaction/idempotency key; `[E-93]` blocks `Yes + qty 0`; §3.10 Persists updated (line 559); PD-49 adopted with §9.2 page-list extension note (line ~2036); QA-M1-09 `[ADMIN]` asserts it; §9.5 **CP-1** states the residual (order-detail). |
| D5→CP-2, D6→CP-3, D7→CP-4, D10→CP-6, D3→CP-5, D14/15/16→CP-7/9/8 | **RESOLVED** as declared | §9.5 holds **CP-1…CP-9**, each with this page's position + remaining fix located off-page. CP-6: `[L-S5-F]` (§3, line 445) and §9.1 now say **OMS / Order Detail only**; QA-CV-08 kept `[WF]` on the shipped (stale) string with the supersession stated in-row, corrected sentence at `**QA-CV-23 [ADMIN]**`. CP-4/WF-VO-1: §2.4 row lists the six minority strings; shipped strings stay `[WF]`, contract `[ADMIN]` (QA-C-18). CP-8: deep-link normalized to `index.html#reqlist` in `[L-S0-2]`, `[L-S6-2]`, §6.2, QA-S6-02 (verified consistent). |
| `_wireframe-fixes.md` append | **RESOLVED** | `[WF-VO-1]` entry present (line 127) with the page-scoped-ID rationale (three concurrent passes claimed `WF-15`). |

**Note (report accuracy, not a spec defect):** the remediator's claim "all 14 citations in the spec use `WF-VO-1`" over-counts — the spec contains **12** `WF-VO-1` citations. Nothing depends on the number.

---

## 3. QA re-run (Playwright, remediated §8.0 rules)

**Sample: 34 scenarios** — all 21 S-1 casualties represented, plus every other previous FAIL/AMBIGUOUS/UNRUNNABLE, plus 4 previously-passing regression anchors. Runner: `scratchpad/rv_qa_vo.py`, results `rv_qa_vo_results.json`.

| Scenario | Prev (m2) | Now | Note |
|---|---|---|---|
| QA-S1-01 | FAIL (S-1) | **PASS** | `sku="100005104"` after rule-6b strip |
| QA-S1-03 | FAIL (S-1) | **PASS** | `["Inbound + Outbound"]` |
| QA-S1-09 | FAIL (S-2) | **PASS** | Deleo outside `.legend` = 0 |
| QA-S1-12 | FAIL (S-4) | **PASS** | span `qty qty-warn` on the `2`; no `qty-warn` on any `1` |
| QA-S1-13 | FAIL (S-1) | **PASS** | 14 headers, clean after strip |
| QA-S2-01 | FAIL (S-3) | **PASS** | `table.tbl` → 4 rows (bare selector still 9, as rule 5 says) |
| QA-S2-03 | FAIL (S-1) | **PASS** | header `Cancel Inbound — 100038120` |
| QA-S3-01 / QA-S3-02(btn) | FAIL (S-1) | **PASS** | `✓ Outbounded`, `Cancel Outbound` clean |
| QA-S3-03 | FAIL (S-1) | **PASS** | 4× `Cancel Inbound`, all greyed |
| QA-S4-01 | FAIL (S-1) | **PASS** | banner ends `Tracking 10322198837710` |
| QA-S4-06 | FAIL (S-1) | **PASS** | `Warehouse Restock — Order 412990` |
| QA-S5-01 | FAIL (S-1) | **PASS** | ends `…07-13 09:20` |
| QA-S5-02 | FAIL (S-1) | **PASS** | `Outbound` present, `btn-gray` |
| QA-S6-04 | FAIL (S-1) | **PASS** | scannote exact after strip |
| QA-S6-05 | FAIL (S-1) | **PASS** | 7 headers exact |
| QA-S6-07 | FAIL (WF-1) | **FAIL — EXPECTED** | `Carrier recorded automatically` still present; spec §8.0 names this the one expected failure; file against wireframe (WF-1) |
| QA-S6-10 | UNRUNNABLE (S-8) | **PASS** | 0 visible `.flsave` — now the asserted (negative) outcome |
| QA-S6-12 | FAIL (S-1) | **PASS** | M6 header exact |
| QA-S6-14 | FAIL (S-7) | **PASS** | all 4 fragments incl. capitalised 4th; `.foot` = `Save Qty Edit` |
| QA-S6-15 | FAIL (S-1) | **PASS** | M5 header exact |
| QA-S6-19 | FAIL (S-1) | **PASS** | note exact after strip |
| QA-M1-01 | FAIL (S-1) | **PASS** | M1 header exact, `Yes` checked |
| QA-M2-01 | FAIL (S-1) | **PASS** | `Barcode Not Recognized` |
| QA-M2-10 | FAIL (S-1) | **PASS** | `Send to Missing Tracking List` |
| QA-M4-01 | FAIL (S-1) | **PASS** | M4 header exact; 6 `.cchip`, `CJ대한통운` on |
| QA-CV-11 | AMBIGUOUS (S-10) | **PASS** | both verbatim sentences found; search value `10322198837710` |
| QA-CV-12 | FAIL (S-1) | **PASS** | print button + 4 clean `Cancel Inbound` |
| QA-CV-18 | FAIL (S-6) | **PASS** | 0 violations; `JIT (Coupang)` mixed case accepted |
| QA-GL-02 | AMBIGUOUS (S-9) | **PASS** | all 3 source substrings present in inline `<script>` |
| QA-NG-08 | FAIL (S-2) | **PASS** | 0 Deleo outside `.legend`, 0 file inputs, no `.seg`, no hold buttons |
| QA-NG-10 | FAIL (S-5) | **PASS** | only anchor = the carved-out `../inbound-request/index.html#reqlist` |
| QA-S0-01 · QA-S6-02 · QA-S1-17(partial) | PASS | **PASS** | regression anchors — no drift |

**Result: 33 PASS · 0 unexplained FAIL · 0 AMBIGUOUS · 0 UNRUNNABLE · 1 expected-fail (QA-S6-07 = WF-1, exactly as §8.0 declares).** Three intermediate FAILs during the run were traced to my own harness selectors (first-`<td>` checkbox cell for SKU; `.chip` vs the page's `.cchip`) — the spec text names the right targets; corrected, all three PASS. This matches m2's projection ("131 PASS / 1 FAIL") on the sampled subset.

---

## 4. Regression checks

- **Legend coverage:** all 69 units present as §3 headings; §8 references every one (0 missing, incl. `[L-S1-F]` via sub-keys). ✓
- **No ID renumbering:** `git diff HEAD` shows **zero** E/BR/DC row definitions removed without re-add; the only new rows are **BR-57** and **E-93** (both declared as remediation additions in §7's preamble and §4). No E-row changed topic (situation-cell drift scan: none). E-6 kept its assigned meaning. ✓
- **No new global-rule restatements:** BR-33/34/35 are explicit no-delta rows, BR-36 now carries a real delta; the only added BR (57) is page-specific behavior. ✓
- **PD discipline:** zero net tag removals; 161 tagged citations, 33 distinct (§9.2 list matches). ✓
- **Internal consistency:** §2.1 (69) = §8.14 (69); §8.14's 277/135/142/91 all machine-true; `[L-S1-F(a)]` survives only inside its own retirement notices. ✓

---

## 5. Verdict

**READY-WITH-NOTES.**

The spec's stated counts are all machine-true; every M1 MAJOR/MINOR defect and every M2 S-finding is genuinely resolved in the current file with the fix text verified in place; the re-run QA sample produces zero false failures and exactly the one declared expected failure. Notes that do not block this page:

1. **QA-S6-07 fails by design** until wireframe defect WF-1 (carrier clause in `#s6b .donebanner`) is fixed — §8.0 documents this; do not re-file.
2. **Cross-page residuals CP-1…CP-9** are stated with this page's position but their other halves live in `_global-rules.md`, `order-detail`, `ready-to-outbound`, `closing`, `order-management` — in particular CP-2's warning *"Do not implement RTO's write against this spec as it stands"* is a live inter-spec conflict that must be closed before RTO's outbound write ships.
3. Cosmetic: the remediator's completion report says "14 citations" of WF-VO-1; the file has 12. No content impact.
