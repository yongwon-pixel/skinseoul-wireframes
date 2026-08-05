# M1 — Coverage Audit · `order-detail.md`

Method: independent re-derivation. Every count below was extracted from
`wms2/order-detail/index.html` and `wms2/specs/order-detail.md` with scripts (regex over the DOM
markup and over the spec's own tables); no number asserted by the spec was trusted.

- Target spec: `wms2/specs/order-detail.md` (2,269 lines, spec v1.1, 2026-08-03)
- Wireframe (SST): `wms2/order-detail/index.html` (761 lines)
- References: `_global-rules.md`, `_plans/_review.md`, `_plans/_provisional-decisions.md`, `_plans/_wireframe-fixes.md`, `_plans/order-detail.A.md`, `_plans/order-detail.B.md`

---

## Verdict table

| # | Check | Verdict | Basis (independently derived) |
|---|---|---|---|
| 1 | Legend coverage | **PASS** | HTML dot census: `#st-normal` = 13 dots (`1`–`13`), `#st-hold` = 14 (`1`–`14`), `#m-del` = 1 (`M3`), unscoped `.dot` = 28, `.legend ol li` = 14 with `.n` order `1,2,3,4,5,6,12,10,11,14,13,9,7,8`. All five numbers match §2.1 exactly. 15 legend units (14 + M3) all have a §3 heading; 17 `[L-F*]` furniture keys all have a normative paragraph (14 in the furniture block, F7 under `[L-13]`, F12 under `[L-6]`, F16 under `[L-1]`). No off-screen normative footer block exists in the HTML other than the legend's provenance paragraph, which §2.1 accounts for. **Zero units specified nowhere.** One mapping nit → D11. |
| 2 | Plan coverage | **PASS** | All 26 A-plan data-capture events (`D-1`…`D-26`) map 1:1 into `DC-1`…`DC-37`; all 4 A-plan explicit non-events map into `NE-1`/`NE-3`/`NE-4`/`NE-5`. All 50 B-plan edge cases `E-1`…`E-50` are present in §7 with matching situations and no renumbering (side-by-side diff run). All 13 A-plan "unnumbered live-admin controls" are covered by the 17 furniture keys (superset). All A-plan OQ-1…OQ-11 and B-plan Q-A1…Q-A12 / Q-B1…Q-B7 route to a PD or a §9.4 D-item — **except two** → D8, D14. |
| 3 | QA integrity | **FAIL** | Counts verified exact: 147 scenarios, 68 `[WF]` / 79 `[ADMIN]` (0 untagged, 0 double-tagged), per-block split matches §8.1 row-for-row, 67 heading-`NEGATIVE` = **45.6 %** (floor 25 %) — all confirmed. §8.2 DC→QA map is accurate for all 37 events (the two apparent misses assert via the canonical event name `line_item.deleted` / `order.outbounded`). **But:** 19 of 92 `[E-n]` have no scenario (D3); two scenarios are guaranteed-fail as written (D1, D2); two furniture keys are unkeyed (D9). |
| 4 | PD discipline | **FAIL** (all defects MINOR) | 35 distinct PDs cited, 167 citations. Spot-checked 12+ against the register — PD-1, PD-2, PD-3, PD-4, PD-5, PD-6, PD-7, PD-8, PD-10, PD-16, PD-19, PD-20, PD-21, PD-22, PD-23, PD-24, PD-26, PD-27, PD-28, PD-29, PD-30, PD-31, PD-32, PD-33, PD-45, PD-51, PD-55, PD-65, PD-67, PD-74, PD-80. All exist. All four NO-DEFAULT PDs (51, 55, 71, 74) are cited with `· NO-DEFAULT`, given no behavior, and listed in §9.2 — **none is presented as decided**. Every `[PD-n]` outside §9/§10 carries `· OWNER-PENDING`; the 15 bare citations are all inside §9.2/§10.1/§10.2/§10.3 where §10.1 states "all **OWNER-PENDING**" for the block. Failures: PD-19 meaning mismatch (D6), PD-16 stretched (D7), PD-31 extended (D12). |
| 5 | Convention compliance (`_review.md` §3) | **FAIL** (MINOR) | Key formats correct for a single-state page (`[L-n]`, `[L-M3]`, `[L-F{n}]`). ID continuity verified with no gaps: `DC-1…37`, `E-1…92`, `BR-1…48`, `NE-1…16` (my first pass showed phantom gaps only because table-row IDs are not bracketed; re-run confirmed complete). Legend render-order artifact declared (§2.1). Slack notation correct: `#fulfillment-admin-comments` (`C0BMGEWM5QA`) with ID on first mention (§1.3), never "pending". Korean strings verbatim (`포어레미디 리뉴잉 폼 클렌저`, `닥터자르트` only as a removed form). Removed features present as an explicit "must NOT exist" table (§10.2, 14 rows). **Violation: §3.7 date rule** → D5. |
| 6 | Global-rule hygiene | **PASS** | 15 `[G-n]` cited; §3.0.1 states deltas only and never reproduces a rule body. Each G-deviation is a dated page delta: `[G-1]` N/A → BR-30 (2026-08-03); `[G-3]`(b)(c) N/A → BR-29 (2026-08-03); `[G-2]` no refresh exception → BR-31 (2026-08-03); `[G-5]` 4-badge set → BR-6; `[G-13]` display-only → BR-34. The canonical event-name list in §5 and the Slack payload fields in §6.1 are required verbatim reproductions per `_review.md` §3.3/§3.6, not restatements. |
| 7 | Adjudication compliance | **PASS** | `_review.md` §1 has 12 `[C-n]`; §2.6 names 6 as binding (C-2, C-3, C-5, C-6, C-7, C-12) and each is honored at a concrete location (§6.1 rows, `[L-4]`, `[L-9]` step 2 + BR-29, BR-39, BR-5/`QA-OUT-6`, §5 naming). The 6 non-binding (C-1, C-4, C-8, C-9, C-10, C-11) are page-scoped elsewhere — correct. Adjudicated non-issue "Deleo Tracking No. asymmetry" carried as BR-9. `_wireframe-fixes.md` independently confirms **no** WF entry targets `wms2/order-detail/index.html`; only cross-page `[WF-3]` binds, and the spec specs the *adopted* rule (BR-14), not the stale "(proposal)" text. The three Actor-Log demo inconsistencies are quarantined in §2.5 B and excluded from QA assertions. No stale wireframe text is specced as truth. |

**Defect counts — BLOCKER 0 · MAJOR 3 · MINOR 11.**

---

## Defects

### 1. `QA-INB-3` is guaranteed to fail against a correct wireframe — MAJOR

**Location:** §8, `QA-INB-3` (spec line 1393): "the string `Request Inbound` appears **nowhere** in the rendered page in either state, **including the legend**".

**Evidence:** `grep -c 'Request Inbound' order-detail/index.html` → **1**. Legend item 2 (index.html line 646) renders verbatim: `… + bottom <b>Bulk Inbound Selected Items</b> (checkbox-linked). "Request Inbound" name retired; unclickable-button bug fixed.` The legend is part of the rendered page and is explicitly in scope per the scenario's own wording.

**Why it matters:** §8.0 promises "An agent must be able to execute every `[WF]` scenario without asking a question" and that every expected string is byte-accurate. §10.2 names `QA-INB-3` as *the* assertion protecting the retired "Request Inbound" label. As written it produces a false bug report on a wireframe that is correct.

**Fix:** scope the assertion to the product surface, not the annotation layer:
> **Then** the string `Request Inbound` appears in **no** button label, header cell or body text inside `#st-normal` or `#st-hold` (the legend's historical mention of the retired name is annotation chrome — `NE-13` — and is out of scope) · **And no** header cell of `.litable` reads `Inbound Request`.

---

### 2. `QA-DC-9` asserts eight distinct `reason_code`s where the spec's own mappings yield seven — MAJOR

**Location:** §8, `QA-DC-9` (spec line ~2029): "**Then** eight `order.action_rejected` events persist, **each with a distinct `reason_code`** from the §5.1 enum".

**Evidence:** the eight guards the scenario triggers map, per §7 and §3, to:

| guard | `reason_code` per spec |
|---|---|
| cancel-order with inbounded lines (`E-47`, `[L-F5]`) | `inbounded_lines_present` |
| add-line after outbound (`E-25`, `[L-F14]`) | `order_outbounded` |
| delete an inbounded line (`E-22`) | `line_inbounded` |
| cancel-inbound after outbound (`E-10`) | **`order_outbounded`** ← duplicate |
| outbound from `on-hold` (`E-14`) | `hold_blocks_outbound` |
| outbound with 0 lines (`E-55`) | `no_lines` |
| print with no label (`E-40`) | `no_label` |
| print on a cancelled order (`E-85`) | `order_cancelled` |

Seven distinct, not eight. Verified by `grep -o 'reason_code=[a-z_]*'` across the spec (20 occurrences, 9 distinct values used).

**Fix:** either (a) change the clause to "eight `order.action_rejected` events persist, carrying the reason codes `inbounded_lines_present`, `order_outbounded` (×2), `line_inbounded`, `hold_blocks_outbound`, `no_lines`, `no_label`, `order_cancelled`", or (b) split `order_outbounded` into `order_outbounded_add_line` / `order_outbounded_cancel_inbound` in the `DC-9` enum (§5.1 line 811) and update `E-10` and `E-25`. Option (a) is the smaller change; option (b) is better telemetry.

---

### 3. 19 of 92 edge cases have no QA scenario — MAJOR

**Location:** §7 vs §8 (whole-document cross-check).

**Evidence:** scenario bodies reference 73 of the 92 defined `[E-n]`. Unreferenced:

`E-3` · `E-9` · `E-14` · `E-34` · `E-35` · `E-36` · `E-37` · `E-38` · `E-44` · `E-45` · `E-52` · `E-58` · `E-64` · `E-65` · `E-69` · `E-70` · `E-76` · `E-89` · `E-90`

**Why it matters:** the omissions are not the trivial tail. `E-3` (double-click Bulk Inbound processed once) and `E-9` (stale-row inbound rejection) belong to the exact double-click / concurrency family this page's `[BR-32]` / `DC-36` doctrine exists to prove; `E-36`/`E-37`/`E-38` are the entire network-failure contract; `E-65` (silent truncation forbidden) and `E-89`/`E-90` are explicitly written as regression guards. `E-14` and `E-52` are the two cross-boundary races. `_review.md` §3.4 requires scenarios to be "keyed to `[L-*]`/`[E-*]`"; with 21 % of cases unkeyed the runbook cannot be used as an acceptance gate for §7.

**Fix:** add at least one scenario per listed `[E-n]`, or add an explicit §8.x exclusion table stating, per case, why it is not machine-assertable (e.g. `E-69` is an org-policy statement, not a behavior). Minimum set that must become real scenarios: `E-3`, `E-9`, `E-36`, `E-37`, `E-38`, `E-65`, `E-90` — several can be added as extra Then-clauses on existing `[ADMIN]` scenarios (`QA-INB-7`, `QA-INB-15`, `QA-OUT-5`) rather than new rows.

---

### 4. §2.4 says "Four furniture keys" and lists three — MINOR

**Location:** §2.4, paragraph after the furniture table (spec line ~189): "**Four** furniture keys are specified inside the legend entry they physically belong to … **`[L-F7]`** View Label under `[L-13]`, **`[L-F12]`** SHIPMENT DETAILS under `[L-6]`, **`[L-F16]`** Hide Comments under `[L-1]`."

**Evidence:** three keys are named. Independently confirmed: the §3 furniture block contains F1, F2, F3, F4, F5, F6, F8, F9, F10, F11, F13, F14, F15, F17 = 14; the remaining three (F7, F12, F16) live inside legend entries. 14 + 3 = 17, so the *total* claim ("All 17 furniture keys have a normative spec paragraph in §3") is correct — only the word "Four" is wrong.

**Fix:** change "Four furniture keys" → "Three furniture keys".

---

### 5. Bare `MM-DD` decision dates violate `_review.md` §3.7 — MINOR

**Location:** §10.1, row `2026-07-23 | REVERSAL … sample assignment` (spec line 2215) — three occurrences: "the **07-22** note recording sample assignment as 'removed' was superseded within a day by the **07-23** ON/OFF redesign … The **07-22** note was stale, not a decision". Also §10.3 chain 2 (line 2260): "The **07-22** 'removed' note was stale within a day". Compound forms at §2.1 line 73 (`2026-07-22/23`) and §2.5 E line 170 / §2.6 (`2026-07-21/22`).

**Evidence:** `_review.md` §3.7 — "**Dates:** `YYYY-MM-DD` everywhere (Decision Logs, BR rationale, conflict citations). **No `07-23` shorthand in final specs.**"

**Fix:** expand all four bare occurrences to `2026-07-22` / `2026-07-23`; rewrite the two compounds as "the 2026-07-22 and 2026-07-23 edits" and "(2026-07-21, restated 2026-07-22)".

---

### 6. `BR-28` cites `[PD-19]`, whose registered meaning is a different rule — MINOR

**Location:** §4, `BR-28` (spec line 763): "**Print surfaces on this page are `🖨 Print` only; `View Label` is a preview, not a print surface.** … `[PD-19 · OWNER-PENDING]`".

**Evidence:** the register reads — "**[PD-19] Single-item auto-print fails (print agent offline).** Provisional: **The inbound still commits; a red toast names the printer/agent; printing is never a gate.**" That decision is correctly cited at `[L-13]` and `E-39`. It says nothing about which controls are print surfaces or about `View Label` being a preview — BR-28's rule rests on `[G-4]` and the 2026-07-21 label de-suffix, not on PD-19.

**Fix:** drop `[PD-19 · OWNER-PENDING]` from the BR-28 rationale cell (BR-28's own date line already carries the provenance), and keep it on the "printing is never a gate" bullet in `[L-13]` where it belongs.

---

### 7. Comment self-mention suppression is an unregistered provisional decision — MINOR

**Location:** §3 `[L-1]` step 9 (spec line ~289): "Self-mention (author == mentioned user) posts normally but suppresses the dispatch … This mirrors the resolver==registrant suppression in the match pipeline `[PD-16 · OWNER-PENDING]` `[E-60]`." Same tag on `E-60` and on `DC-27.suppressed_reason`.

**Evidence:** the register's PD-16 is "**Does an on-the-spot M2 match in View Orders also fire the 'match confirmed' auto-comment + Slack?** Provisional: Yes, same auto-comment and route; the @mention is suppressed when resolver == registrant." It decides the *auto-comment* pipeline only. Whether a human's `@self` in a free-text comment suppresses a Slack DM is a separate owner question that appears in neither plan nor register, yet the spec specifies behavior for it.

**Fix:** either add a new register entry (e.g. PD-87, "Does a self-@mention in a comment notify the author?" → provisional "suppressed, recorded as `suppressed_reason=self_mention`", pages: all 8) and retag, or reword to "By analogy with PD-16 (no owner decision exists for this case); dev default is to suppress" and list it in §9.4.

---

### 8. `E-40` decides a plan-raised owner question with no PD tag and no §9 entry — MINOR

**Location:** §7.5, `E-40` (spec line 1098): "Print (or View Label) when the order has no label/tracking yet | **Disabled** with the reason `No label yet` rather than producing an empty job."

**Evidence:** `order-detail.B.md` §5 lists this under **Owner must decide** — "Q-A5: Print with no label yet — disabled vs error toast? And View Label when label missing. (L-13, E-40)". It has no entry in `_provisional-decisions.md`. Every other Q-A item (A1→PD-28, A2→PD-21, A3→PD-22/23, A4→PD-30, A6→PD-2, A7→PD-27, A8→PD-10, A9→PD-31, A10→PD-32, A11→PD-33, A12→PD-29) has one. Q-A5 is the sole owner question silently resolved.

**Fix:** register it (provisional: "disabled with a visible reason, consistent with `[BR-46]` and `E-7`") and tag `E-40`, `[L-13]` and `[L-F7]` with the new `[PD-n · OWNER-PENDING]`.

---

### 9. `[L-F2]` and `[L-F16]` are the only furniture keys with no QA scenario keyed to them — MINOR

**Location:** §8 (whole block) vs §2.4.

**Evidence:** `[L-F*]` keys appearing in QA scenario headings/bodies: F1, F3, F4, F5, F6, F7, F8, F9, F10, F11, F12, F13, F14, F15, F17. Missing: **F2** (↻ Audit History), **F16** (Hide Comments). Both controls *are* exercised — F2 by label inside `QA-SUB-1` and `QA-DC-7`, F16 by label inside `QA-CMT-1` and `QA-DC-3` — but neither is keyed, so a key-driven coverage check reports a hole. `_review.md` §3.4 requires scenarios "keyed to `[L-*]`/`[E-*]`".

**Fix:** add `[L-F2]` to the `QA-SUB-1` and `QA-DC-7` key lists and `[L-F16]` to the `QA-CMT-1` and `QA-DC-3` key lists. No new scenarios needed.

---

### 10. Two-line table headers break the "byte-accurate" `[WF]` string contract — MINOR

**Location:** §8, `QA-REN-1` second Then-clause ("`Latest Inventory Count`, `Inbound Status`, `Sourcing Route`, … `Product Cost 🤖`") and `QA-EDIT-3` (`Inbound Status`).

**Evidence:** the wireframe markup is `<th>Latest<br>Inventory Count</th>`, `<th>Inbound<br>Status</th>`, `<th>Sourcing<br>Route</th>`, `<th>Product<br>Cost 🤖</th>` (index.html lines 359 and 581). `textContent` yields `LatestInventory Count`, `InboundStatus`, `SourcingRoute`, `ProductCost 🤖` — no space where the `<br>` sits. A literal string comparison, which §8.0 mandates, fails on four of the fourteen header cells.

**Fix:** add one line to §8.0's preconditions: "Header-cell comparisons normalize `<br>` to a single space and collapse whitespace (`el.textContent.replace(/\s+/g,' ').trim()`); the four two-line Inventory headers are affected." Alternatively quote them as `Latest<br>Inventory Count` in the scenario.

---

### 11. §2.1's mapping of the legend provenance paragraph omits two of its own items — MINOR

**Location:** §2.1, third numbering note (spec line ~76): "…its content is specified under `[L-6]`, `[L-F8]`, `[L-F9]`, `[L-F12]` and `[L-F17]`."

**Evidence:** the paragraph it maps enumerates six things — "Global nav · address fields · **Operator Comments position** · Fulfillment Tracking (SHIPMENT DETAILS + TRACKING HISTORY) · **Line Items horizontal scroll** are identical to the live admin". The Operator Comments placement is specified under `[L-1]` and the 1680px horizontal scroll under §1.3 / `[L-10]`, neither of which is in the list. The content *is* covered; the map is incomplete, which is exactly what a coverage audit reads as a hole.

**Fix:** extend to "`[L-1]`, `[L-6]`, `[L-10]`, `[L-F8]`, `[L-F9]`, `[L-F12]` and `[L-F17]` (§1.3 for the 1680px horizontal scroll)".

---

### 12. `[L-F4]` / `BR-21` / `E-83` extend PD-31 beyond its registered content — MINOR

**Location:** §3 furniture `[L-F4]`, §4 `BR-21`, §7.7 `E-83` — all three exclude "any assigned **sample set**" from a clone and tag the sentence `[PD-31 · OWNER-PENDING]`.

**Evidence:** the register's PD-31 reads — "NOT copied: comments, actor log, tracking numbers, agent-tracking fields (Order Number/Date/Cost/CP Link), PIC, status." Sample assignment is absent from that list. The spec's addition is defensible (it follows `[G-13]`'s period rules) but is presented as if PD-31 decided it.

**Fix:** append "and any assigned sample set (`[G-13]` period rules apply to the clone)" to PD-31 in `_provisional-decisions.md`, so the register and the spec agree; no spec text change needed if the register is updated.

---

### 13. `QA-OUT-3`'s negative scope is ambiguous for the same reason as D1 — MINOR

**Location:** §8, `QA-OUT-3` (spec line ~1487): "the string `Outbound to Deleo BaroShip` appears **nowhere** in the rendered page in either state or the legend body text describing the current label".

**Evidence:** `grep -c 'Outbound to Deleo BaroShip'` → **1** (legend item 9, index.html line 655: `"Outbound to Deleo BaroShip" → relabeled to <b>"Outbound"</b>`). The trailing qualifier ("or the legend body text describing the current label") reads as if it *adds* the legend to the scope rather than carving out its historical mention, so two agents will grade the scenario differently.

**Fix:** apply the D1 wording — restrict the assertion to `#st-normal` / `#st-hold` and state explicitly that the legend's historical quotation of the old label is expected.

---

### 14. Carrier tracking-sync cadence is specified nowhere — MINOR

**Location:** §9.4 `D-12` (spec line ~2157) vs `order-detail.A.md` §5 OQ-11.

**Evidence:** OQ-11 reads "Tracking-sync **cadence** + system-actor naming convention for D-10/D-17/D-20/D-25". §9.4 D-12 covers only "System-actor naming convention for `DC-14`, `DC-17`, `DC-23`, `DC-32`". `grep -c cadence order-detail.md` → **0**. `[L-6]` and `DC-23` describe what a sync persists but never how often one runs or who schedules it, and §6.5 calls the carrier feed "inbound-only" without a frequency.

**Fix:** add to §9.4: "**D-18** — carrier tracking-sync cadence and scheduling owner. Default: the `(synced …)` marker must always reflect the last *successful* sync; a stale marker is a display state, never a fabricated time `[E-43]`. Cadence is dev-time provided it is observable in `DC-23`."

---

*Audit complete. 0 BLOCKER · 3 MAJOR · 11 MINOR. Checks 1, 2, 6, 7 PASS; checks 3, 4, 5 FAIL.*
