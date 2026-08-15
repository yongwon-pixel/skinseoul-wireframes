# Plan — Inventory (`stock-status`) — LENS B: Developer & QA

Planner: Lens B (functional precision · edge cases · QA acceptance criteria).
Wireframe SST: `wms2/stock-status/index.html` · live `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/stock-status/`
Page identity: renamed "Stock Status" → "Inventory" (2026-07-22). Default landing = Current Stocks tab. Four sub-tabs (Current Stocks / Stock History / Inbound Stock / Outbound Stock) + 6 modals.

---

## 1. LEGEND INVENTORY

Numbered dots on this page run **5–16** (1–4 are not used on this page — the shipped legend starts at 5; not a coverage gap) plus modal dots **M1–M4**. Two additional modals exist without their own dot: `m-auditlog` (owned by legend 15) and `m-adjlog6` (June variant of M2). Total implementation units: **16** (12 numbered + M1–M4).

| # | What it is | Spec treatment (template section · what must be specified) |
|---|---|---|
| 5 | New **Current Stocks tab, default landing**; full stock list + Location(line)/Sourcing Route filters; **JIT included** in route filter (2026-08-03 — JIT residual stock from cancellations/mis-delivery returns is listed & filterable); line list derived dynamically from registered locations [G-14] | §3 [L-5]: tab routing, default-landing rule, filter semantics (line grouping algorithm, JIT match incl. "JIT (Coupang)" channel suffix), search box behavior; §4 JIT-residual rule; QA in §8 |
| 6 | Click Reserved Qty → **allocated orders modal (M3)**; SUSPECTED PHANTOM flag when order cancelled/refunded but reservation remains; per-row Cancel Inbound (M4) | §3 [L-6]: click trigger (dotted-underline link), modal contents (Order ID/Date/Customer/Status/Reserved Qty/Reserved At/Action), phantom detection predicate, row highlight; server read; §7 phantom edge cases |
| 7 | **Stock Audit mode** — Start re-sorts by location ascending (walking path), exit restores Available desc; Counted Qty inputs → Diff auto-calc → Loss column (diff × product cost) → total loss footer (target 0) → confirm opens summary modal M1 | §3 [L-7]: mode entry/exit state machine, column show/hide (`.audcol`), sort transitions, diff computation, loss cost source ref (dev-time decision, 07-22), audit-mode-only visibility [G-14]; §5 audit session events; §7+§8 heavy |
| 8 | **Stock History Events** — Type/Status badges (INBOUND/OUTBOUND/RESERVE/ADJUST × CONFIRMED/PENDING), pending rows amber-highlighted, filter chips All/Confirmed/Pending confirm | §3 [L-8]: chip filter behavior (exclusive select), badge taxonomy, pending semantics + who confirms (cross-page, §6/§9); columns fixed as live screen |
| 9 | **History pagination** — resolves live screen "More data available (pagination not implemented)" | §3 [L-9]: pagination control spec, page size (dev-time), filter×pagination reset rule; §7 boundary cases |
| 10 | **Page rename Stock Status → Inventory**; legacy references ("Export Stock Status") mapped during development | §2 naming note + §3 [L-10]: nav label, page title, legacy-route redirect/mapping requirement |
| 11 | **Default sort = Available descending**; re-sortable by clicking column headers | §3 [L-11]: sort keys per column, direction toggle, interaction with audit-mode sort override; §8 sort assertions |
| 12 | **Location = editable input on every row**; Unassigned rows (amber placeholder) listed & assignable in place; barcode-less products get Barcode input (same rule as View Orders) | §3 [L-12]: inline-edit trigger (blur/Enter), validation, save action + toast [G-2], old→new capture [G-8], one-location-per-SKU [G-14]; §7 concurrency/invalid-format |
| 13 | **Add unregistered product** (audit mode only) — product-name autocomplete (name·size·SKU, barcode not required) → Location·Qty → Add inserts new row at top (system 0 → Diff +qty) → merged as ADJUST(+) on confirm; no catalog match → Unrecognized flow (F) | §3 [L-13]: autocomplete contract (min chars, fields matched, selection required), Add validation, row insertion state, merge-on-confirm; §6 cross-link to tracking-missing; §7 no-match/free-text/duplicate |
| 14 | **Single location per SKU** (2026-07-22) — By Location card always shows the one current location; returns merged into same location after inspection (RETURN-BIN dropped) | §3 [L-14]: By Location card render rule; §4 business rule + RETURN-BIN reversal in §10 Decision Log |
| 15 | **Past Audit Logs modal** (`m-auditlog`) — monthly sessions (date·auditor·SKUs checked·adjustments·new additions·total loss, target 0) + per-session link to ADJUST detail | §3 [L-15]: open trigger (button beside Start Stock Audit), table contract, "View ADJUST events" → M2/M2b; §5 session record schema |
| 16 | **Comments hub** (top-right, shared across all screens) — @ Mentions + ★ Saved + full-text search, unread badge | §3 [L-16]: cite [G-7] and spec only page deltas (Inventory-context comment examples, deep link opens order); Slack routing in §6 |
| M1 | **Confirm Audit Differences modal** (`m-adjust`) — Diff≠0 items as ADJUST events (book correction, NOT inbound/outbound), Reserved-shortage check blocks confirm, total loss, "Confirm — record N ADJUST events" | §3 [M1]: gating (shortage check), atomic batch commit, idempotency [G-9], post-confirm effects (Current Stocks/Available update immediately, session logged, toast); §7 partial-failure |
| M2 | **ADJUST events detail modal 07-22** (`m-adjlog`, + un-dotted 06-30 variant `m-adjlog6`) — per-event Time/SKU/Product(KR)/Location/System→Counted/Adjustment/Loss; NEW ADDITION rows tinted | §3 [M2]: read-only session detail contract; rule "each event also appears as ADJUST in that SKU's Stock History" (dual-view over one persisted event, [G-8]) |
| M3 | **Reserved Orders modal** (`m-reserved`) — see legend 6; includes note linking phantom investigation to Pending-confirm filter | §3 [M3]: full column/flag contract + footer note behavior |
| M4 | **Cancel Inbound modal** (`m-resrelease`) — 4-part flow: 1) release reservation 2) Restock yes/no (no = ADJUST(−n) loss) 3) Restock Qty (default = originally inbounded, editable) 4) optional memo (also posted to order Comments) | §3 [M4]: exact behavior per input, arithmetic (Reserved 8→5, Available 34→37 on Yes), RESERVE-release event to Stock History, memo→Comments write, idempotency [G-9]; §7 heavy (double-click, mid-action failure, active-order guard) |

Baseline carried-over units (legend footnote — must still be functionally specified in §3): global nav · **Export Stock Status button** · Stock History search dropdown (SKU/Product Name/Order ID/Tracking No) + result cards (Stock Status / By Location / Product Information incl. Sourcing Route tag [G-5]) · **Inbound Form** (`p-inbound`: SKU*, Qty*, Tracking No, Carrier, Order ID optional → "＋ Record Inbound") · **Outbound Form** (`p-outbound`: same fields → "－ Record Outbound", block when qty > Available) · event table columns (Type/Quantity/Status/Tracking No/Carrier/Location/Order ID/Created At/Auditor). I will key these `[L-F1]`(search), `[L-F2]`(inbound form), `[L-F3]`(outbound form), `[L-F4]`(export) in §3 so QA can reference them.

---

## 2. SECTION OUTLINES (10 template sections)

**§1 Purpose & Users** — Inventory = single source of current stock truth + movement history + monthly stock-take. Users: warehouse staff (audit counting, location assignment — walking the lines with a cart, hence location-ascending audit sort), order/ops team (reserved investigation, phantom cleanup — Dean's report), admin/center manager (loss target 0, monthly audit review). Physical context that shaped decisions: audit walks the racks in location order (legend 7); KR product names in audit/product contexts [G-6].

**§2 Screen Inventory & Wireframe Map** — Table of 4 panes + 6 modals ↔ legend numbers ↔ how to reach on live wireframe (wf-bar buttons: "Current Stocks (default)", "Stock History Search", "Inbound Form", "Outbound Form", "Modal: Reserved Orders", "Modal: Cancel Inbound (Release Reservation)", "Modal: Past Audit Logs", "Modal: ADJUST Events (07-22)", "Modal: ADJUST Events (06-30)", "Modal: Confirm Audit Differences"; in-page: subtabs, `#toggleAudit`, Reserved "8" link). Note: wf-bar modal shortcuts open the modal without changing pane state (2026-08-03 behavior) — QA precondition.

**§3 Functional Specification** — per unit above. Lens-B emphasis per item: trigger · inputs/outputs · validation · server action (named, e.g. `POST /inventory/audit-sessions/{id}/confirm`, `PATCH /inventory/{sku}/location`, `POST /inventory/reservations/{id}/release`, `POST /inventory/movements` for forms) · state transitions · idempotency [G-9] for every confirming action (audit confirm, cancel-inbound confirm, record inbound/outbound, location save) · exact toast copy per action [G-2] (to be fixed in spec, e.g. "Inbound recorded — SKU 100004819 +6", "Reservation released — Order 409112", "Stock audit confirmed — 3 ADJUST events recorded"). Buttons with exact labels & enable/disable conditions: `Start Stock Audit`/`Exit Stock Audit`, `📋 Past Audit Logs`, `Confirm Audit Differences (ADJUST log)` (visible only in audit mode), `Confirm — record N ADJUST events` (disabled while Reserved-shortage unresolved), `Add` (disabled until autocomplete selection), `Cancel Inbound`, `Confirm` (M4), `＋ Record Inbound`, `－ Record Outbound`, `⬇ Export Stock Status`, `⬇ Export`, `🔍 Search`, filter chips, `Mark all read`.

**§4 Business Rules** — ADJUST = book correction, never Inbound/Outbound (keeps logistics history clean; M1 text). Loss = Diff × product cost, target 0 (design fixed 07-22; cost source dev-time). One location per SKU [G-14]; RETURN-BIN dropped (07-22). JIT residual stock listed (08-03). Audit-only UI hidden outside audit mode [G-14]. Reserved-shortage gate blocks audit confirm. Outbound > Available blocked. Phantom predicate: order status ∈ {cancelled, refunded} ∧ reservation not released. Default sort Available desc; audit sort location asc. Restock=No records ADJUST(−n). Sourcing routes exactly 4, black bold text [G-5].

**§5 Data Capture** [G-8] — (Lens A owns depth; I contribute the per-action event contracts): stock movement events (INBOUND/OUTBOUND/RESERVE/RESERVE-RELEASE/ADJUST) each with actor, ts, SKU, qty ±, old/new totals, location, tracking no, carrier, order id, status (PENDING/CONFIRMED); audit session entity (session id, auditor, start/end ts, SKUs checked, per-SKU system→counted, diffs, new additions, loss per line + total, confirm ts); location change events (old→new, actor); cancel-inbound composite event (release + restock decision + qty + memo); memo → order Comments history; export events (who exported, when, filter state); UI logs (Stock History table, audit log modals) are views over these persisted events, never the only copy.

**§6 Integrations** — Slack: comment @mention → `#fulfillment-admin-comments` with personal @mention (CONFIRMED 2026-08-03, `_slack-routing`); no page-specific confirmed routes beyond that — any new route (e.g. audit-confirmed notification) is "decide per feature at dev time" per routing table and goes to §9. Cross-page: [L-13] no-catalog-match → Unrecognized flow on `tracking-missing` (deep link [G-12]); M3 note → Stock History Pending filter (in-page deep link); comments deep-link to order; PENDING inbound events originate from View Orders State 6 / Inbound Request lifecycle [G-10][G-11] — this page only displays/filters them. Sheet/BI: Export Stock Status (file download; format dev-time). No print pipeline on this page — [G-4] not applicable (no Print button; state this explicitly to close the mandatory-item audit trail).

**§7 Edge Cases & Error States** — full candidate list below (Lens-B deep inventory), IDs [E-1]…[E-50].

**§8 QA Acceptance Criteria** — plan below: ~96 Given/When/Then scenarios keyed [L-n]/[E-n], each tagged **[WF]** (executable on the live wireframe today — DOM/class assertions) or **[ADMIN]** (real build only — server effects, toasts, idempotency; wireframe has no toast/server layer, so these are spec-level expected texts the agent asserts later). Selector conventions fixed in spec: `#toggleAudit`, `.audcol`, `#auditSummary`, `.reslink`, `#m-reserved`, `#m-resrelease`, `#m-adjust`, `#auSearch/#auLoc/#auQty/#auAdd`, `.loc-in`, `.qty-in`, `.filterchip`, `.subtabs button`, `.wf-tab`, `#inbox1`.

**§9 Out of Scope & Open Questions** — Procurement Hub excluded entirely (2026-08-02); label/invoice layouts (Phase 3-1); PENDING-confirm surface lives on other pages; open questions listed in section 5 of this plan.

**§10 Decision Log** — dated entries: 07-22 rename Stock Status→Inventory · 07-22 single location per SKU + RETURN-BIN dropped (reversal) · 07-22 loss = Diff×cost fixed, cost source deferred to dev · 08-03 JIT included in route filter (residual stock) · 08-03 line-based dynamic location filter [G-14] · 08-03 audit-summary visible only in audit mode · 08-03 global toast emphasis [G-2] · 08-03 comments channel confirmed `#fulfillment-admin-comments` · pagination added vs live screen (legend 9) · Current Stocks tab as new default landing (legend 5).

---

## 3. LENS-B DEEP INVENTORY

### 3a. Edge-case candidate list [E-n] (exhaustive; §7 will carry these IDs)

**Current Stocks — list, filters, sort**
- [E-1] Empty inventory (no SKUs registered) — empty state copy + Export/audit buttons disabled behavior.
- [E-2] Search/filter combination yields zero rows — empty result state; audit start on empty filtered list.
- [E-3] Unassigned-location rows (amber "Unassigned" placeholder): how the line filter treats them (own "Unassigned" bucket vs excluded) and audit walking-sort placement (wireframe sorts them last via sentinel).
- [E-4] Barcode-less product — Barcode column renders input; entering a barcode = data-capture event; duplicate barcode entry.
- [E-5] Location edited to invalid format (free text, lowercase, wrong pattern) — validation + no save.
- [E-6] Location edited to a location already used by another SKU — allowed or blocked? (owner Q5-7) — behavior must be deterministic either way.
- [E-7] Two operators edit the same SKU's location concurrently — last-write-wins vs conflict; old→new audit trail must show both events.
- [E-8] Network failure mid location-save — input reverts? retry? no silent divergence between UI and server.
- [E-9] Column-header re-sort then audit start/exit — audit forces location-asc, exit must restore Available-desc (not the user's custom sort? or the user's last sort — spec must pick; wireframe restores original order).
- [E-10] Location edited to a new line (e.g. first "D-…" location) — dynamic line list [G-14] must include Line D without reload.

**Stock Audit mode**
- [E-11] Audit started while filters active — is the session scoped to the filtered subset? "SKUs Checked" count semantics (owner Q3).
- [E-12] Untouched Counted Qty rows — wireframe prefills system qty (diff 0). Risk: uncounted rows indistinguishable from counted-and-matching (owner Q2).
- [E-13] Counted Qty non-numeric / negative / blank — reject with inline error, Diff not computed.
- [E-14] Counted Qty < Reserved for that SKU — Reserved-shortage check: affected order list shown in M1, Confirm disabled until reviewed (definition of "reviewed" = owner Q5).
- [E-15] Unregistered product with no autocomplete match — "No match — register manually via Unrecognized flow (F)" row; deep link behavior.
- [E-16] Add clicked without an autocomplete selection (free-typed text) — blocked, focus returns to `#auSearch` (wireframe behavior).
- [E-17] Add with blank Qty (defaults 1) or blank Location (defaults "Unassigned") — confirm defaults are intended, capture in spec.
- [E-18] Unregistered product added twice / product already in the visible list — duplicate guard.
- [E-19] "Confirm — record N ADJUST events" double-click — exactly one session, one ADJUST batch [G-9].
- [E-20] Network failure mid audit-commit — batch must be atomic: no partial ADJUST set, no session row without events (or vice versa).
- [E-21] Exit Stock Audit with unsaved counts — discard warning vs silent drop; counts are client-side until confirm.
- [E-22] Stock moves during audit (outbound confirmed after count entered) — system qty stale; recompute diff at confirm vs snapshot at entry — must be specified.
- [E-23] Two auditors start audit simultaneously — session lock or merge (owner Q4).
- [E-24] Audit with zero diffs — Confirm allowed, session recorded with 0 adjustments (precedent: 2026-05-31 session, "₩0 · target met").
- [E-25] SKU missing product cost — Loss renders "—" (new additions do); rule for existing SKUs without cost + total-loss arithmetic excludes them.

**Reserved modal (M3) / Cancel Inbound (M4)**
- [E-26] Reserved Qty = 0 — link disabled (not clickable) vs empty modal; spec must pick.
- [E-27] Sum of modal rows ≠ header Reserved count — data-integrity error state (display + alert?).
- [E-28] Partially-refunded order holding a reservation — phantom predicate boundary.
- [E-29] Cancel Inbound clicked on an ACTIVE (processing) order — wireframe shows the button on processing rows; guard level undecided (owner Q1).
- [E-30] Restock Qty edited above the reserved/inbounded qty — validation cap.
- [E-31] Restock Qty edited below released qty — remainder handling (auto ADJUST(−) vs blocked; owner Q6).
- [E-32] M4 Confirm double-click — single release event [G-9]; second click no-ops with feedback.
- [E-33] Network failure between release and restock application — two effects must be one atomic composite event; no "released but not restocked" limbo.
- [E-34] Two operators release the same reservation concurrently — second gets "already released" error, counts not double-adjusted.
- [E-35] Order state changes (outbounded/uncancelled) while M3 open — stale row action must fail safe with re-fetch message.
- [E-36] Memo written in M4 — must also appear in the order's Comments history; memo with @mention triggers Slack route [G-7].

**Stock History tab**
- [E-37] Search for unknown SKU / no events — empty results state for cards + table.
- [E-38] Search-type dropdown (SKU / Product Name / Order ID / Tracking No) — each type's match behavior + placeholder switch; Product Name partial match.
- [E-39] PENDING event displayed — row amber, chip filter isolates it; this page cannot confirm it (read-only here) — assert no confirm affordance.
- [E-40] Pagination boundaries — exactly one page of rows, last page, filter change resets to page 1, page survives event append.

**Inbound / Outbound forms**
- [E-41] Inbound with unknown SKU — reject before server write.
- [E-42] Qty 0 / negative / non-numeric on either form — blocked with inline validation.
- [E-43] Inbound for SKU with no registered location — location auto-apply impossible; row lands Unassigned + prompt.
- [E-44] Outbound qty > Available — blocked (form-note rule); exact error copy; boundary: qty = Available allowed → Available 0.
- [E-45] Outbound must check Available (Total − Reserved), not Total — negative test with reserved stock.
- [E-46] Double-submit on Record Inbound/Outbound [G-9] — one movement event.
- [E-47] Network failure on form submit — no phantom movement; retry idempotent.
- [E-48] Order ID entered that doesn't exist — reject or warn (link integrity).
- [E-49] Tracking No duplicating an existing event — warn (possible double entry).

**Comments hub / cross-cutting**
- [E-50] Comment search with no matches — "No matching comments" empty state; clearing query restores tab panes; unread badge decrements on "Mark all read"; star/unstar syncs Mentions↔Saved.
- Cross-cutting negative frame applied to all confirming actions: missing toast = test failure [G-2]; page refresh after any action = failure [G-2]; permission/session expiry mid-modal = safe error, no partial write.

### 3b. QA scenario plan (Given/When/Then, keyed to [L-n]/[E-n]) — per-section counts

| QA section | Coverage | Est. scenarios |
|---|---|---|
| QA-NAV: tabs, default landing, wf-map | L-5, L-10, pane-state-on-modal rule | 6 (5 WF / 1 ADMIN) |
| QA-CS: Current Stocks list, sort, filters, JIT | L-5, L-11, E-1..E-2, E-9 | 12 (10 WF) |
| QA-LOC: location editing + line filter dynamics | L-12, L-14, E-3, E-5..E-10 | 8 (4 WF) |
| QA-AUD: audit mode lifecycle + unregistered add + M1 confirm | L-7, L-13, M1, E-11..E-25 | 18 (11 WF) |
| QA-LOG: past audit logs + ADJUST detail modals | L-15, M2/M2b | 6 (6 WF) |
| QA-RES: Reserved modal + Cancel Inbound | L-6, M3, M4, E-26..E-36 | 14 (7 WF) |
| QA-HIS: Stock History search, chips, pagination | L-8, L-9, L-F1, E-37..E-40 | 10 (6 WF) |
| QA-FRM: Inbound/Outbound forms | L-F2, L-F3, E-41..E-49 | 10 (3 WF) |
| QA-COM: Comments hub | L-16, E-50 | 6 (6 WF) |
| QA-GLB: global-rule negatives (toast presence, no-refresh, idempotency double-click) | G-2, G-9 across all confirming actions | 6 (0 WF) |
| **Total** | | **~96** |

Negative tests ≥ 25% of total (every validation edge gets one). Each scenario states: exact element (selector or visible label), exact expected text/class/count, and tier tag [WF]/[ADMIN].

### 3c. Three fully-worked example scenarios

**QA-AUD-01 [WF] — Audit mode entry re-sorts by location and reveals audit-only UI (L-7, mandatory #10)**
- Given: live wireframe loaded, Current Stocks pane active (default), button `#toggleAudit` reads exactly `Start Stock Audit`, and no `.audcol` cell is visible, and `#auditSummary` is hidden.
- When: the agent clicks `#toggleAudit`.
- Then: button text becomes `Exit Stock Audit`; table header gains visible columns `Counted Qty`, `Diff`, `Loss (₩)`; the first data row's `.loc-in` value is `A-01-04` and row order by `.loc-in` is ascending (`A-01-04, A-01-05, A-02-13, A-02-20, A-03-02, B-01-07, B-02-03, B-03-02, C-01-05, C-02-01`, Unassigned last); the purple row "＋ Unregistered product found during audit" is visible; footer `#auditSummary` shows text starting `Total stock loss (sum of diff × product cost):` with value `+₩46,260`; and When the agent clicks `#toggleAudit` again Then audit columns hide, `#auditSummary` hides, and the first row returns to SKU `100031877` (Available-descending restored) [E-9].

**QA-RES-04 [WF UI / ADMIN effects] — Cancel Inbound with Restock = No records loss as ADJUST (M4, E-31 boundary excluded, negative-path)**
- Given: Reserved modal open (click the dotted-underlined `8` under `Reserved Qty` in the Stock Status card on Stock History pane, or wf-tab `Modal: Reserved Orders`); the amber row for Order `409112` shows badge `SUSPECTED PHANTOM` and status `cancelled`.
- When: the agent clicks that row's `Cancel Inbound` button, and in modal `#m-resrelease` (header `Cancel Inbound — Order 409112 · Dongkook 마데카솔 크림 × 3`) selects radio `No — exclude from stock (damaged · lost etc., record the loss as ADJUST(−3))`, leaves Restock Qty `3`, types memo `Damaged in storage`, and clicks `Confirm`.
- Then [WF]: the modal closes.
- Then [ADMIN]: top-right green toast appears (exact copy fixed in §3, e.g. `Reservation released — Order 409112 · ADJUST(−3) recorded`); Reserved decreases 8→5 and Available stays 34 (no restock); Stock History for SKU `100004819` gains a RESERVE-release event AND an `ADJUST(−3)` event with actor + timestamp; the memo appears in Order 409112's Comments history; a second click of `Confirm` (double-click) produces exactly one release and one ADJUST [G-9, E-32]; the page does not reload [G-2].

**QA-FRM-05 [ADMIN] — Outbound exceeding Available is blocked, boundary passes (L-F3, E-44/E-45, negative test)**
- Given: Outbound Stock pane active (subtab `Outbound Stock`); SKU `100004819` has Total 42, Reserved 8, Available 34.
- When: the agent enters SKU `100004819`, Quantity `35`, Carrier `Deleo`, clicks `－ Record Outbound`.
- Then: submission is rejected with an inline/toast error naming Available (expected copy fixed in §3, e.g. `Outbound blocked — exceeds Available Qty (34)`); no OUTBOUND event is created; Total/Reserved/Available unchanged.
- When: the agent corrects Quantity to `34` and clicks `－ Record Outbound`.
- Then: green toast confirms the outbound; Available becomes 0, Total 8 (Reserved intact); exactly one OUTBOUND event (qty −34, actor, ts, carrier `Deleo`, location `A-02-13`) exists even if the button was double-clicked [G-9, E-46]; no page refresh [G-2].

---

## 4. MANDATORY-INCLUSION MAP (of the 12 owner-flagged items)

| # | Item | Lands on this page? | Where in spec |
|---|---|---|---|
| 2 | Global confirmation toast [G-2] | YES (all screens) | §3 per confirming action (exact copies), §8 QA-GLB |
| 9 | Line-based location filter, dynamic lines [G-14] | YES — core | §3 [L-5], §7 [E-10], §8 QA-CS/QA-LOC |
| 10 | Audit-mode-only summary visibility [G-14] | YES — core | §3 [L-7], §8 QA-AUD-01 |
| 11 | JIT residual stock in Inventory | YES — core | §3 [L-5], §4 rule, §8 QA-CS (filter `JIT` returns Anua row `JIT (Coupang)`) |
| 12 | Comment @mention Slack routing [G-7] | YES (all screens; channel CONFIRMED `#fulfillment-admin-comments`) | §3 [L-16], §6 routing table, [E-36] |
| 1 | Scanner protocol [G-1] | NO (scoped View Orders + Closing) — §6/§9 states explicitly; barcode column input is manual entry, not a continuous-scan surface | §9 note |
| 4 | Instant print [G-4] | NO — no Print button on Inventory (Export = file download) | §6 states explicitly |
| 3, 5, 6, 7, 8 | Audio / sample / unrecognized-matching / multi-tracking / RTO KR names | Not this page's owner; touched only via cross-refs (E-15 → Unrecognized flow; PENDING events originate from [G-10]/[G-11] flows) | §6 cross-page links |

---

## 5. OPEN QUESTIONS

### Owner must decide (do not invent)
1. **Cancel Inbound on ACTIVE orders** — M3 shows the button on `processing` rows, not just phantoms. Is releasing a live order's reservation allowed, and with what guard (extra confirmation? role restriction? blocked)?
2. **Counted Qty prefill policy** — wireframe prefills system qty, so an uncounted row is indistinguishable from counted-and-matching (silent diff-0). Keep prefill, or blank-until-entered with untouched rows excluded from "SKUs Checked"?
3. **Partial/filtered audits** — may an audit be confirmed while Location/Route filters restrict the list, and does "SKUs Checked" mean rows visible, rows touched, or full catalog?
4. **Concurrent audit sessions** — single active session lock per warehouse, or parallel auditors allowed (and if so, how do sessions merge)?
5. **Reserved-shortage "reviewed"** — M1 disables Confirm "until reviewed": what unlocks it (acknowledgement checkbox, mandatory Cancel Inbound resolution, or mandatory comment)?
6. **Restock Qty edited below released qty (M4)** — is the remainder auto-recorded as ADJUST(−remainder), or is under-restocking blocked?
7. **Location exclusivity** — [G-14] fixes one location per SKU; may two SKUs share one location (affects location-edit validation [E-6] and audit walking order)?
8. **Audit permissions** — who may Start/Confirm a stock audit (any warehouse staff vs manager only)? Auditor field implies identity matters.

### Developer decides at build time (flag in §9, no owner block)
- Audit loss **product-cost source** — FIFO lot cost (recommended, Procurement Hub FIFO COGS) vs latest purchase price; design Diff×cost fixed 2026-07-22, source explicitly deferred to dev (ledger + dev handoff note).
- Stock History **pagination page size** and server-side paging mechanics [L-9].
- **Location code format** validation regex and the line-derivation parsing rule (prefix before first `-`).
- **Export** file format/columns for both Export buttons; whether audit columns are included when audit mode is on [E-54-class]; legacy "Export Stock Status" label mapping (legend 10).
- **Carrier dropdown** sources for Inbound (Coupang/Deleo/Direct) vs Outbound (Deleo/YUN/Coupang) forms — fixed lists vs carrier registry.
- **Idempotency key scheme** per action [G-9] and toast exact-copy finalization [G-2] (spec proposes copies; dev confirms feasibility).
- **Deep-link URL formats**: comments → order, [E-15] → tracking-missing Unrecognized flow [G-12].
- **PENDING→CONFIRMED wiring** — which surface confirms pending inbound events (View Orders State 6 / Inbound Request); this page is display-only for PENDING.
