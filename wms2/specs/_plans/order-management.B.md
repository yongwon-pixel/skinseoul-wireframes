# PLAN — Order Management (slug `order-management`) — LENS B: Developer & QA
Planner: LENS B (functional precision · edge cases · QA acceptance criteria). Complements LENS A (data capture / operator flow). Sources read: spec-template.md, global-rules-draft.md, slack-routing.md, decision-sources.md, wireframe `wms2/order-management/index.html` (SST), ledgers 2026-07-09 / 2026-08-02.

---

## 1. LEGEND INVENTORY

Legend numbers 1–5 plus modal markers M1 / M1b / M2 / M3 (9 implementation units total; every one lands in template §3 keyed `[L-n]`).

| # | What it is | Spec treatment |
|---|---|---|
| **1** (dot on `⬆ Import` button) | Manual Marketing Order Import (M1, confirmed 07-23; PIC custom + carrier auto-assign + toast confirmed 08-03) | §3 `[L-1]`: full flow spec — template download → upload → parse/preview → Order Type → PIC → Confirm; validation matrix (what blocks vs what never blocks — **no stock validation**, dropped 07-23); server action = atomic batch create of MKT- orders; idempotency [G-9]; toast [G-2]; §6 RTO cross-link; §7/§8 heavy coverage |
| **M1** (modal marker) | Marketing Order Import modal — 4 numbered steps (Template / Order Type / PIC / Upload) + Preview table + note + footer buttons | §2 map row; §3 sub-spec of `[L-1]`: exact labels ("Download Template (.xlsx)", chips "Influencer Seeding"/"✎ Custom", PIC select + "✎ Custom" free-text, dropzone, "Confirm Import (N orders)"), enabled/disabled conditions per step |
| **M1b** (dot on Preview "Carrier (auto)" column) | Per-row carrier auto-assignment by country at confirm; unconnected country → amber "Not connected — contact the Fulfillment Center" (confirmed 08-03) | §3 `[L-1b]`: assignment rule (country → connected-carrier lookup), non-blocking amber state, toast subtext counts; §7 unconnected/all-unconnected cases; §8 exact expected cell texts/colors |
| **2** (dots on both action-row buttons) | Sample Assignment ON/OFF (redesigned 07-23 as simple ON/OFF; exactly-1-set + dual-view confirmed 08-03) [G-13] | §3 `[L-2]`: two buttons ("Sample Assignment ON" green / "Cancel Sample Assignment" gray), period model (multi-period, overlap allowed, forever flag), exactly-1-set-per-order invariant, dual-view output rule (carrier vs internal) with label layout deferred to Phase 3-1 |
| **M2** (modal marker) | Sample Assignment ON modal — target radio ("All new orders in this period" / "Selected orders only (N)"), start date+time, end date+time or "forever (no end date)" | §3 sub-spec of `[L-2]`: field validation (start<end, forever XOR end), selected-count binding, "Start Assignment (ON)" action, toast; §7 boundary cases |
| **M3** (modal marker) | Cancel Sample Assignment modal — period list table (checkbox / Assignment Period / Target / Status Active·Ended), "Cancel Selected Periods" (red) | §3 sub-spec of `[L-2]`: Ended rows = record-only (no checkbox), cancel semantics = stop NEW assignments only, already-assigned orders kept; toast text; idempotency |
| **3** (no on-screen dot — removed item) | Bulk Hold Shipment button removed; Hold now = Change Status (on-hold) on Order Detail (F) | §3 `[L-3]` one-paragraph negative spec ("must NOT exist on this screen") + §10 decision-log entry + §6 cross-link to order-detail spec. QA gets an absence assertion |
| **4** (dot on omitted-table placeholder) | Order list table identical to current admin (omitted from wireframe) EXCEPT MKT- rows: purple tint + MKT badge + PIC column value | §3 `[L-4]`: delta-only spec (tint `--mkt-soft`, MKT badge, PIC display); unchanged inventory enumerated by reference (filter bar, Columns toggle, Merge Orders, Export/Yun Export, count, pagination); §7 MKT-row interaction cases (merge, filter, export) |
| **5** (dot next to Comments button) | Top-right Comments hub — shared pattern [G-7]: @Mentions / ★ Saved tabs, full-text search, unread badge, click-opens-order | §3 `[L-5]`: cite [G-7], page deltas only (badge=3 demo, search dataset); §6 Slack routing row (#fulfillment-admin-comments — CONFIRMED, see §4 note); §8 hub scenarios reusable across pages |

Missing-number check: dots seen in wireframe = 1, 2 (×2 buttons), 4, 5, M1, M1b, M2, M3; legend list = 1–5 with 3 explicitly "no on-screen dot". Complete.

---

## 2. SECTION OUTLINES (template §1–§10)

**§1 Purpose & Users** — Order team + marketing (Harshit/EuJin per wireframe comments) create non-sales MKT- orders and control sample-set attachment; admin context = desk work (no scanner on this page — [G-1] does NOT apply here, state explicitly). Settlement & volume separation of MKT vs sales is the operational reason for the visual split.

**§2 Screen Inventory & Wireframe Map** — table: default dashboard state, M1 (Import), M2 (Sample ON), M3 (Cancel Sample), Comments hub open state; each row = legend ids ↔ §3 anchor, live URL `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/order-management/` + how to open (top wf-bar buttons "Modal: Marketing Import" / "Modal: Sample Assignment ON" / "Modal: Cancel Sample Assignment"; in-mock triggers = "⬆ Import", "Sample Assignment ON", "Cancel Sample Assignment", "💬 Comments").

**§3 Functional Specification** — per legend item, LENS B precision:
- `[L-1]` Import: trigger (⬆ Import, always enabled); step gating (Confirm disabled until file parsed with 0 blocking errors; Order Type required — Custom chip requires non-empty text; PIC required — select default "logged-in user (me)" or non-empty custom text); parse contract for the dev-team template (columns: Recipient · Contact · Address · Country · SKU · Qty · Campaign name); Preview header format "`{filename}` · `{n}` rows parsed · `{e}` errors"; server action `POST import batch` — **atomic** (all-or-nothing), returns batch id, order ids `MKT-#####`; state transition: rows → created MKT- orders visible immediately in list + RTO Marketing view regardless of stock; idempotency [G-9]: client debounce + idempotency key = file hash + operator + monotonic nonce, re-click returns same batch; validation matrix: BLOCKS confirm = unparseable file, schema mismatch, missing required field, unknown SKU (owner-check, see §9), qty ≤ 0/non-numeric, invalid country; NEVER blocks = zero stock (decision 07-23), unconnected carrier (amber flag only); toast exact text "✓ Confirmed — {n} orders imported" + subtext with carrier-assignment summary [G-2].
- `[L-1b]` Carrier auto-assign: rule = per-row country → connected-carrier mapping resolved at confirm time (not upload time); unconnected → order still created, flagged state "Not connected — contact the Fulfillment Center"; output surfaced in preview column and toast subtext count.
- `[L-2]` Sample ON: inputs (target radio; "Selected orders only" radio shows live count and is disabled at 0 selected; start datetime required; end datetime XOR forever); behavior = creates an assignment period entity; assignment applies to qualifying orders at order-creation time within [start, end); exactly-1-set invariant: an order matched by ≥2 active periods gets one set, attributed once; dual-view output rule [G-13] cited, label layout NOT specced (Phase 3-1). Cancel (M3): only Active periods selectable; effect = period stops matching new orders immediately; already-assigned orders unchanged; Ended rows read-only. Both actions: toast texts as in wireframe, [G-9] double-click-safe.
- `[L-3]` Removed Bulk Hold: absence requirement + pointer to Order Detail Change Status.
- `[L-4]` MKT row rendering deltas + explicit "everything else unchanged" enumeration.
- `[L-5]` Comments hub: cite [G-7] wholesale; page delta = none beyond demo data; badge/unread/mark-all-read/search/star behavior by reference.

**§4 Business Rules** — no-stock-validation rule (07-23, rationale: import precedes inbound); MKT settlement/volume separation (purple tint exists for finance reasons); exactly-1-set (08-03); cancel-keeps-assigned (wireframe note); dual-view tax rationale (carrier sees "(+ sample set)" only); PIC recorded per entire import batch; correction of decision-sources stale note: @mention channel is **CONFIRMED** #fulfillment-admin-comments `C0BMGEWM5QA` (slack-routing 2026-08-03) — spec cites routing table, not "pending".

**§5 Data Capture** — LENS A owns depth; LENS B contributes the event↔action mapping needed for QA oracles: import_batch_created (actor, file name/hash, n rows, order type, PIC, per-row carrier result), mkt_order_created ×n, sample_period_created / sample_period_cancelled (old/new status), sample_set_assigned (order, period id), comment_posted / mention_sent, plus [G-8] actor+timestamp+old/new on all.

**§6 Integrations** — Slack: comment @mention → #fulfillment-admin-comments (payload per routing table). No other confirmed routes on this page (import/sample events have NO Slack route today — "decide per feature at dev time" row; do not invent one). Cross-page: Confirm Import → RTO Marketing view (deep link in real admin [G-12]); L-3 → order-detail Change Status; sample dual-view → internal invoice & picking label (shipping-label content deferred to Phase 3-1); template .xlsx from dev team. Print pipeline [G-4]: **not on this page** (no Print buttons) — state explicitly to close the mandatory-inclusion audit.

**§7 Edge Cases & Error States** — full candidate list below (§3 of this plan), IDs E-1…E-45.

**§8 QA Acceptance Criteria** — plan below: ~44 Given/When/Then scenarios keyed [L-n]/[E-n], each tagged `[WF]` (executable against live wireframe today) or `[ADMIN]` (real-admin-only: persistence, concurrency, Slack); exact selectors from wireframe ids (`#mktConfirm`, `#sampCancelBtn`, `#otChipCustom`, `#picCustomBtn`, `#picCustomIn`, `[data-modal]`, `[data-open]`, `.gtoast`).

**§9 Out of Scope & Open Questions** — label/invoice layouts (Phase 3-1); order list table internals (unchanged); Procurement Hub (excluded 08-02); plus open questions listed in §5 of this plan.

**§10 Decision Log** — dated entries: 07-22 sample assignment removed → 07-23 reinstated as simple ON/OFF (stale-note reversal, reconfirmed 08-03); 07-23 M1 import confirmed + stock-validation dropped (Notion G contradiction noted, ledger 07-09 line 111); 08-03 PIC custom input; 08-03 carrier auto-assign + unconnected copy; 08-03 exactly-1-set; 08-03 dual-view; 08-03 confirm toast global; Bulk Hold removal; 08-03 @mention channel confirmed.

---

## 3. LENS-B DEEP INVENTORY

### 3a. Edge-case candidate list [E-n] (exhaustive; final spec may merge but must not drop silently)

Import — file & parse:
- **E-1** Non-.xlsx upload (csv/renamed/xls) → rejected with error, no rows parsed.
- **E-2** Valid file, 0 data rows → preview "0 rows parsed", Confirm disabled.
- **E-3** Row missing a required field (each of Recipient/Contact/Address/Country/SKU/Qty/Campaign) → row error, counted in "· N errors".
- **E-4** Unknown SKU (not in catalog) → error behavior (block file vs skip row — open question Q-D3/Q-O3).
- **E-5** Qty = 0 / negative / non-numeric / absurdly large → row error (large-qty threshold = dev).
- **E-6** Invalid or unsupported country code → row error.
- **E-7** Country valid but no connected carrier → row OK, amber "Not connected — contact the Fulfillment Center", Confirm still enabled (confirmed 08-03).
- **E-8** ALL rows unconnected-carrier → import still confirmable; toast subtext reflects count.
- **E-9** Duplicate rows within one file (same recipient+SKU) → allowed or warned? (dev default: allow — marketing may intend multiples; document).
- **E-10** Re-upload of an already-imported file (same hash) → duplicate-batch guard (open question Q-O4).
- **E-11** Double-click "Confirm Import" → exactly one batch [G-9].
- **E-12** Network failure mid-confirm → atomic: either full batch exists or none; retry with same idempotency key safe.
- **E-13** Close modal (✕ / Cancel / overlay click) after upload, before confirm → nothing created, staged file discarded.
- **E-14** "✎ Custom" Order Type chip active but input empty → Confirm blocked.
- **E-15** PIC custom input empty/whitespace with custom mode active → Confirm blocked.
- **E-16** File over row/size limit → rejected with explicit limit message (limit value = dev).
- **E-17** Template schema mismatch (columns renamed/reordered/extra) → parse policy (header-name matching; extra cols ignored — dev).
- **E-18** Mixed-country file → per-row carrier assignment (GB→YunExpress, PE→Not connected in demo data).
- **E-19** Preview shows errors > 0 → Confirm disabled (or blocked with message) until fixed re-upload.
- **E-20** SKU with zero stock → NOT an error; rows import and appear in RTO Marketing view (negative test guarding the dropped stock validation).

Sample assignment:
- **E-21** ON modal opened with 0 orders selected → "Selected orders only (0)" radio disabled or Start blocked.
- **E-22** End datetime ≤ start datetime → Start blocked with validation message.
- **E-23** "forever" checked while end date filled → forever wins; end fields cleared/disabled (exact UI rule = dev).
- **E-24** Two overlapping active periods, order qualifies for both → exactly 1 sample set (invariant test).
- **E-25** Backdated start datetime → retroactive application to existing orders? (open question Q-O1; QA scenario parked until decided).
- **E-26** Period ends while assigned order still unshipped → order keeps its sample set (assignment at creation-time, not outbound-time — spec must state).
- **E-27** Ended period row → no checkbox, cannot be cancelled (record only).
- **E-28** Cancel modal with 0 periods checked → "Cancel Selected Periods" disabled.
- **E-29** Double-click "Cancel Selected Periods" → single cancellation [G-9].
- **E-30** Cancel an Active period → already-assigned orders keep sets; only future matching stops (wireframe note).
- **E-31** Order cancelled/refunded after sample assigned → sample handling on internal docs (dev default: follows order lifecycle; document).
- **E-32** Two operators create overlapping ON periods concurrently → both persist; invariant E-24 still holds.
- **E-33** "Selected orders only" where a selected order already holds a set from another period → skipped, no duplicate, surfaced count in toast? (dev detail).
- **E-34** Dual-view divergence check: carrier-facing export shows only "(+ sample set)" appended to LAST product name; internal invoice/picking shows sample type + qty [G-13] (verified on the consuming pages; cross-ref).
- **E-35** Sample ON interaction with MKT- orders (does ON match MKT orders?) → open question Q-O2; both-direction tests parked.

List, comments, global:
- **E-36** MKT- row rendering: purple tint + MKT badge + PIC populated; hover state distinct; regular rows unaffected.
- **E-37** Merge Orders across MKT- + regular order → allowed? (open question Q-O5; settlement separation at risk).
- **E-38** Comments search with no hits → "No matching comments" empty state.
- **E-39** "Mark all read" → unread rows lose highlight, badge count clears.
- **E-40** Slack delivery failure on @mention → comment persists; notification retried/queued (never blocks posting) [ADMIN].
- **E-41** Two operators import simultaneously → distinct batches, no MKT id collision [ADMIN].
- **E-42** Permission edge: user without order-management write → Import / Sample buttons hidden or disabled (policy = dev per existing admin RBAC).
- **E-43** Toast behavior: appears top-right, green, auto-dismisses (~2.6s in wireframe); no full-page refresh after any confirm [G-2].
- **E-44** Network failure mid "Start Assignment (ON)" → no partial/ghost period; retry-safe.
- **E-45** After import, header order count increments (2,818 → 2,818+n) and new MKT rows appear without page refresh [G-2].

### 3b. QA scenario plan (Given/When/Then, keyed to [L-n]/[E-n])

Per-section estimated counts (total ≈ **44**):
| Block | Scenarios | Notes |
|---|---|---|
| [L-1]/[L-1b] Import happy paths | 6 | open modal, template download, chip toggle, PIC select/custom, preview render, confirm+toast |
| [L-1] Import negative/validation (E-1…E-20) | 12 | at least one per blocking rule + E-20 no-stock negative + E-11 idempotency |
| [L-2] Sample ON (M2) | 6 | target radios, period fields, forever toggle, E-21/22/23, confirm toast |
| [L-2] Cancel (M3) | 5 | list render, Ended read-only (E-27), E-28, cancel+toast, E-30 keep-assigned [ADMIN] |
| [L-2] Invariants (E-24/26/32/33) | 4 | [ADMIN] — exactly-1-set battery |
| [L-3] Absence assertion | 1 | no "Hold Shipment" bulk button anywhere on page |
| [L-4] MKT rows (E-36, E-45) | 3 | [ADMIN] for post-import row; [WF] for styling tokens |
| [L-5] Comments hub (E-38/39 + search + tabs + star) | 5 | [WF] |
| Global G-2/G-9/network (E-12/43/44) | 2 | toast contract + refresh ban |

Three fully-worked examples (executable against live wireframe today):

**QA-EX-1 [L-1][E-43] Import confirm toast** `[WF]`
- Given the live wireframe is open and I click the filter-bar button labeled "⬆ Import" (purple, `.btn-mkt`)
- When the modal titled "Marketing Order Import" is visible and I click the footer button "Confirm Import (12 orders)" (`#mktConfirm`)
- Then the modal closes AND a green toast (`.gtoast`) appears top-right with text "✓ Confirmed — 12 orders imported" and subtext "Carrier auto-assigned per country · 1 not connected — flagged to contact Fulfillment Center" AND the toast auto-dismisses within ~3s AND the page does not reload [G-2].

**QA-EX-2 [L-1b][E-7][E-18] Carrier auto-assign column** `[WF]`
- Given the "Marketing Order Import" modal is open
- When I inspect the Preview table (header "Preview — mkt_seeding_batch3.xlsx · 12 rows parsed · 0 errors")
- Then the last column header reads "Carrier (auto)" AND every GB row (e.g. recipient "Svetlana Jaloba") shows green bold "YunExpress" AND the PE row (recipient "Lucia Ramos") shows amber bold "Not connected — contact the Fulfillment Center" AND the Confirm button remains enabled despite the unconnected row.

**QA-EX-3 [L-2][E-27][E-30] Cancel sample period** `[WF]`
- Given I click the action-row button "Cancel Sample Assignment" (gray) and the modal "Cancel Sample Assignment — Current Assignment Periods" is visible
- When I verify the row "2026-06-01 00:00 → 2026-06-30 23:59" with status chip "Ended"
- Then that row has NO checkbox (record-only), while both "Active" rows have checkboxes
- And when I click the red footer button "Cancel Selected Periods" (`#sampCancelBtn`)
- Then a green toast appears with text "✓ Assignment period cancelled" and subtext "New assignments stopped for the selected period · already-assigned orders kept".

Negative-test policy: every blocking validation gets a paired positive ("does block") and boundary ("just passes") scenario; E-20 is written as a MUST-NOT-block negative to prevent regression toward the dropped Notion-G stock error.

---

## 4. MANDATORY-INCLUSION MAP (decision-sources items 1–12)

| # | Item | Lands here? | Where |
|---|---|---|---|
| 2 | Global confirmation toast [G-2] | YES | §3 all confirming actions; §8 QA-EX-1/3; E-43/45 |
| 5 | Sample dual-view + exactly-1-set [G-13] | YES (primary page) | §3 [L-2], §4, E-24/34; label details deferred Phase 3-1, noted in §9 |
| 12 | Comment @mention Slack routing [G-7] | YES | §3 [L-5], §6 routing row (#fulfillment-admin-comments C0BMGEWM5QA — CONFIRMED 08-03; spec corrects the stale "pending" note) |
| 1,3,4,6–11 | Scanner / audio / print / unrecognized / multi-tracking / RTO KR names / location filter / audit / JIT residual | NO | §6 states explicitly that [G-1]/[G-3]/[G-4] do not apply on this page (no scan surface, no outbound-class button, no Print button) so the audit trail is closed, not silent |

---

## 5. OPEN QUESTIONS (flagged, not decided)

**Owner must decide:**
1. **Q-O1 (E-25)** Sample ON with a backdated start datetime — does it retroactively assign existing unshipped orders created inside the period, or only orders created after the ON action? Wireframe copy "All new orders in this period" is ambiguous when start is in the past.
2. **Q-O2 (E-35)** Does an active sample period also match MKT- marketing orders, or sales orders only?
3. **Q-O3 (E-4/E-19)** Import file with some invalid rows: block the whole file until clean, or allow partial import of valid rows? (Wireframe only shows the 0-errors state.)
4. **Q-O4 (E-10)** Duplicate-batch protection beyond double-click [G-9]: should re-importing the same file (same hash / same recipient+SKU+campaign set) warn or block?
5. **Q-O5 (E-37)** May Merge Orders combine an MKT- order with a regular sales order? (Purple separation exists for settlement — merging could break it.)
6. **Q-O6 (E-7 downstream)** "Not connected — contact the Fulfillment Center" orders: what un-blocks them for outbound (carrier connected later? manual carrier pick on RTO/Order Detail?) and who owns the follow-up? No Slack route exists for this today — add one or keep manual?

**Developer decides at build time:**
1. **Q-D1 (E-16/E-17)** Max rows/file size; header-matching policy for extra or reordered columns.
2. **Q-D2 (E-23)** UI mechanics of forever-vs-end-date conflict (disable fields vs clear on check).
3. **Q-D3 (E-24 attribution)** Which period is recorded as the assigner when two active periods overlap (first-match by start datetime recommended) — affects audit rows only, not the 1-set invariant.
4. **Q-D4 (E-9/E-33)** Whether within-file duplicate recipient+SKU rows warn, and whether skipped already-assigned orders are surfaced in the ON confirmation toast.
5. **Q-D5 (E-42)** RBAC surface for Import/Sample buttons (hide vs disable) following existing admin convention.
6. **Q-D6** Idempotency-key construction for import (file hash + operator + nonce recommended) and toast dedup on retry.
