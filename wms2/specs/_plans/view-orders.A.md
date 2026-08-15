# PLAN — view-orders (LENS A: Operator & Data)

Planner A of 2. Sources read: spec-template.md, global-rules-draft.md, slack-routing.md, decision-sources.md, full wireframe `wms2/view-orders/index.html` (v20, 1848 lines, all 9 states + 7 modals), decision ledgers 2026-07-09 + 2026-08-02.

---

## 1. LEGEND INVENTORY (58 items — every dot on every state/modal)

Notation: `S{state}-{n}` / `M{n}`. Spec keys will be `[L-S1-6]` style. Template section (§) each lands in: §3 Functional always; extra targets noted.

### State 0 — Waiting (2)
- **S0-1** Empty unified search box, auto-focus; scan/typing switches instantly to the matched order's state screen. Rule texts (auto-detect, Coupang `[V1]` QR, focus-return) live in spec, not on screen. → §3 + §4 (G-1 delta) + §5 (scan event).
- **S0-2** Expected Inbound summary badge (decided 2026-08-02) — collapsed one-liner; expand = inline table (tracking rows sorted top, route badges, PARTIAL n/m); **row click = open State 6 without scanning** (damaged-label bulk boxes). → §3 + §4 (rationale/date) + §5 (entry-method event) + §6 (cross-link Inbound Request).

### State 1 — Scan result, last item remaining (21)
- **S1-1** Unified search auto-detect (Tracking / Inbound Order / Product Order / Last-mile); multi-match → selection list; Coupang QR `[V1]barcode` suffix-match. → §3, §4, §7 (multi-match, prefix edge).
- **S1-2** Shelf input + floating [Save] (click/Enter, no refresh, "✓ Saved"); same pattern as State 6 Location inputs. → §3 + §5 (shelf_assign old/new).
- **S1-3** Comments hub (top-right): [@ Mentions]/[★ Saved] tabs + full-text search across ALL comments (order no/author/text, newest first); click opens the order; badge = unread. [G-7] → §3 + §5.
- **S1-4** Reduced side padding — all columns + buttons fit one screen (no horizontal scroll for operator). → §1 (physical context) + §3.
- **S1-5** Scanned product highlighted + sorted to top. → §3 (operator eye-path rationale in §1).
- **S1-6** Sourcing Route column — 4 routes [G-5], black bold text; only JIT can be PENDING; JIT shows purchase channel in parentheses (Coupang/Naver/Other retail); "Existing inventory" pick deducts warehouse stock and shows that stock's own route, not JIT; route matched from Inbound Request by tracking no. → §3 + §4.
- **S1-7** Qty ≠ 1 → amber highlight (multi-pick attention cue). → §3 + §1.
- **S1-8** Last remaining item → combined **Inbound + Outbound** button. → §3 + §4 + §5 (auto-outbound event trigger recorded).
- **S1-9** Bulk bar above table, always visible: Bulk Inbound (Selected) / Inbound + Outbound All Remaining; full inbound = order complete = auto outbound; Hold orders stop at Inbound. → §3 + §4.
- **S1-10** Button label "Outbound" (was "Outbound to Deleo Baroship" — carrier-agnostic). → §3 + §10 (decision log).
- **S1-11** Order Comments button — expand/collapse; @tag → Slack. → §3 + §6.
- **S1-12** Barcode input value persists after inbound (operator can verify last scan). → §3 + §4 (G-1 delta).
- **S1-13** Actor Log (Inbound/Outbound Log): time·action·SKU·qty·worker·memo; bottom of States 1–5; memo populated from e.g. cancel modal. → §5 (UI view over persisted events, never the only copy [G-8]).
- **S1-14** Click-anywhere + post-action → search box auto-focus with select-all. Behavior only, no on-screen text. → §3 + §4 (G-1 delta) + §8 (negative test: focus never lost).
- **S1-15** No refresh after processing; top-right success/failure toast [G-2]; Outbound-family buttons play send sound [G-3a] (added 2026-08-03) — ear-confirmation during continuous scanning. → §3 + §4.
- **S1-16** Floating Live Barcode Feed (bottom-left, collapsed by default): worker + barcode + time, max 10–20 on screen, **full history in backend, export by date**. → §5 (retention/export statement) + §3.
- **S1-17** Location column (right of Sourcing Route) — current location of warehouse-stored (Existing Inventory) products; States 1–5 common. → §3.
- **S1-18** Brand always prefixed bold in Product Name [G-6]; missing-brand products = product-name logic fix. → §3 + §9 (upstream data dependency).
- **S1-19** Results-area Comments panel expanded by default; per-comment ★ save → aggregates in hub Saved tab. → §3 + §5.
- **S1-20** No-barcode products show an always-visible Barcode input (all states); entered value saved to **product master**, recognized from next scan. → §3 + §5 (barcode_register old null→new) + §7 (bad/duplicate barcode).
- **S1-22** Print Return Labels (supplier return; work states 1·1b·2·3) → opens M4. Distinct concept from Customer Return (State 4). → §3 + §6 (print pipeline [G-4]).
- **S1 footer rules (un-numbered, MUST be specced as [L-S1-F])**: (a) single-item orders auto-print label on scan — only orders with no inbound history; Existing Inventory doesn't count as inbound history; (b) unrecognized barcode → M2 order-number lookup → match registers tracking on the spot / no match → M2b Missing Tracking List; match writes tracking no. **onto the order's product line**, rescan then resolves; (c) Inbound Request tracking scan → State 6, never a customer-order screen. → §3, §4, §5, §7.

### State 1b — Scan result, normal (1)
- **S1b-21** Not-last-item → plain **Inbound** button; becomes Inbound + Outbound only when exactly 1 uninbounded remains; Outbound stays disabled until all inbounded. → §3 + §8.

### State 2 — All inbounded (2)
- **S2-1** Outbound button activates (green) once every item inbounded. → §3.
- **S2-2** Cancel Inbound → restock popup (M1) confirm. → §3.

### State 3 — Outbound complete (4)
- **S3-1** Button → "✓ Outbounded", gray/disabled. → §3.
- **S3-2** Cancel Outbound — status rollback prepare shipment → processing. → §3 + §5 (status old/new).
- **S3-3** Completion toast, no refresh → next scan immediately. → §3.
- **S3-4** Individual Cancel Inbound disabled after outbound — Cancel Outbound first (ordering guard). **Wireframe still marks this "proposal"** → §4 + §9 (owner confirm).

### State 4 — Customer return mode (6)
- **S4-1** Return banner on scanning a returned tracking barcode. → §3.
- **S4-2** "Restock Selected to Warehouse" → M3 (qty·location moved into modal). → §3.
- **S4-3** M3 defaults: restock qty **0** (enter only actually-returned qty; 0 = excluded; no checkboxes); location auto-filled for existing stock, JIT-only SKUs need assignment; confirm button count = items with qty > 0. (No on-screen dot; lives in M3.) → §3 + §4.
- **S4-4** qty > 0 with no location → confirm disabled. (No on-screen dot.) → §3 + §7.
- **S4-5** Unified search auto-detects last-mile (return) barcodes. → §3.
- **S4-6** No "returned" status exists — 8 real statuses (pending/processing/on-hold/completed/refunded/failed/shipped/prepare-shipment); returns usually refunded, sometimes failed, sometimes still completed; **detection = scanning the return barcode, not status**. → §4 (critical rule + rationale).

### State 5 — Hold order (3)
- **S5-1** Hold banner (requester·reason·time), applied from OMS/Order detail or Order Management by CS. → §3 + §6 (cross-page).
- **S5-2** Outbound disabled while on Hold. → §3 + §4.
- **S5-3** Bulk: Inbound allowed, "Inbound + Outbound All Remaining" blocked. → §3.
- **S5 footer**: Hold applied/released elsewhere; View Orders displays + blocks only. → §9 scope.

### State 6 — Internal Inbound (9)
- **S6-1** Auto-branch: tracking of an Inbound Request opens this screen instead of States 1–5; multiple tracking numbers per request all match [G-10] (2026-08-03). → §3 + §4.
- **S6-2** Internal Inbound banner — "Not a customer order · Goes into Inventory · No Outbound"; Inbound No.·channel·supplier·requester·expected arrival + link → `../inbound-request/#reqlist` [G-12]. → §3 + §6.
- **S6-3** Progress tiles: Expected / Received / Remaining / per-SKU done count. → §3.
- **S6-4** Continuous product-barcode scanning, +1 per scan, cursor auto-return [G-1]; **warning sound** for products not in the request (wrong-delivery detection) — page delta of [G-3]. → §3 + §4 + §5.
- **S6-5** Reconciliation table — SKU/Brand/Product Name straight from Inbound Request (sheet columns). → §3.
- **S6-6** Received Qty = scan cumulative + directly editable (box-level bulk). → §3 + §5 (manual edit vs scan distinguished in event).
- **S6-7** Location = Inventory intake position; existing SKU auto-suggests its one location [G-14]; new SKU manual. → §3 + §4.
- **S6-8** Confirm Full Inbound gated on **exact match every SKU** (same gating class as Closing); mismatch → Save Partial (M5); over-scan warns. → §3 + §4.
- **S6-9** Edit Expected Qty ✎ → M6 (decided 2026-08-02); recalculates remaining + gating; auto comment on request + Slack @requester [G-11]. → §3 + §5 + §6.
- **S6 footer**: on confirm ① Inventory (Current Stocks) + locations ② Request list REQUESTED/PARTIAL → INBOUNDED ③ Received Date auto (**automatic Carrier recording NOT supported, confirmed 2026-08-03**) ④ focus → search box. No Outbound on this screen. → §3, §4, §6.

### State 6b — Internal Inbound complete (2)
- **S6b-1** Completion banner — exact-match result (800/800), locations, list INBOUNDED, Received Date. ⚠ banner text says "Carrier recorded automatically" — contradicts S6 footer (08-03). See Open Questions. → §3.
- **S6b-2** Focus returns to search box immediately, no refresh, next tracking scan. → §3 + §8.

### Modals (8)
- **M1** Cancel Inbound: restock? yes/no → restock qty (default = inbounded qty, disabled on "No") → memo (also recorded in order Comments); Reserved → Available auto-update; use cases incl. mistaken JIT when warehouse stock exists (→ JIT residual stock, cross-ref Inventory mandatory item 11). → §3 + §5.
- **M2** Unrecognized barcode step 1 — Coupang purchase order-number lookup; match table (per-line Match Tracking No); match registers tracking on that line + closes + green toast; rescan recognized. Demo values are wireframe scaffolding only. → §3 + §5 + §7.
- **M2b** Send to Missing Tracking List — product autocomplete (EN with KR alongside), qty, memo, carried failed order no; Slack **#unrecognized-tracking**; green confirm toast, no refresh. → §3 + §5 + §6.
- **M3** Customer Return Restock — per-item restock qty (default 0) + location + shared memo (M3b); qty>0-without-location disables confirm; Current Stocks auto-update. → §3 + §5.
- **M3b** Memo field of M3 — also recorded in order Comments history AND inbound log (dual persistence). → §5.
- **M4** Print Return Labels (supplier return) — carrier chips (CJ대한통운/롯데/한진/우체국/로젠/✎ Custom) + per-item size·qty optional + live label preview; prints carrier + KR product name + size + qty [G-4][G-6]. → §3 + §6.
- **M5** Save Partial Inbound — reason enum (split shipment / short delivery / partially damaged) + memo; received units added to Inventory **immediately**; list → PARTIAL (n/m); rescan same tracking resumes State 6 [G-11]. → §3 + §4 + §5.
- **M6** Edit Expected Qty — new qty + required reason (damaged·defective / supplier qty change / other) + memo; gating recalc (e.g. 300→120 enables full confirm at 120/120); auto comment + Slack @requester; list qty cell shows history (300→120). → §3 + §5 + §6.

**Count check: S0 2 + S1 21 + S1b 1 + S2 2 + S3 4 + S4 6 + S5 3 + S6 9 + S6b 2 + modals 8 = 58** (plus 3 un-numbered footer rule blocks S1/S5/S6 specced as F-items).

---

## 2. SECTION OUTLINES (what I will actually write, per template §)

**§1 Purpose & Users** — Scan hub for warehouse staff + order team: (a) customer-order inbound→outbound (States 1–3), (b) customer returns (4), (c) hold handling (5), (d) internal stock intake (6/6b). Physical context that shaped decisions: scanner-in-hand with auto-Enter [G-1]; operator often NOT watching monitor → send sound [G-3] + State 6 warning sound; gloves/speed → zero-click loop (auto-focus select-all S1-14, value persistence S1-12, single-item auto-print, combined Inbound+Outbound S1-8); one-screen layout S1-4; amber multi-qty cue S1-7; KR product names on supplier-return labels M4 [G-6].

**§2 Screen Inventory & Wireframe Map** — 9 states + 7 modals table: legend keys ↔ spec §3 anchors 1:1; live URL `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/view-orders/` + wf-bar tab names to reach each state/modal (exact button labels as in v20).

**§3 Functional Specification** — one block per legend key above (58 + 3 footer blocks). For each: trigger, exact behavior, inputs/outputs, validation, server action, state transition, idempotency [G-9], and operator-visible feedback (toast text, sound, highlight). Buttons with exact labels + enable/disable matrices: Outbound (all-inbounded ∧ not-Hold ∧ not-outbounded), Inbound vs Inbound+Outbound (remaining-count = 1 switch), bulk pair, Confirm Full Inbound (exact-match gate), Confirm Restock (count = qty>0 items; location gate), Cancel Inbound (disabled post-outbound), Cancel Outbound.

**§4 Business Rules** — dated, with rationale (list in Lens-A inventory below, BR-1..BR-18).

**§5 Data Capture** — the full event catalog DC-1..DC-35 below, each with actor/timestamp/entity/old→new; UI-log vs silent flagged; retention/export statements (feed full history + export-by-date; comments retained as AI-training asset [G-7]; actor log = view over events [G-8]).

**§6 Integrations** — Slack routing table (4 rows, below); deep links (S6-2 → `../inbound-request/#reqlist` [G-12]; Comments hub/list click → order page; S0-2 row → State 6); sheet handoffs (Received Date auto-record exists **for sheet sync** → Procurement Hub / request-list sheet pull; carrier NOT auto); print pipeline [G-4]: order Print, M4 return labels, single-item auto-print — all via local print agent, no dialog, carrier-agnostic.

**§7 Edge Cases** — Lens B owns enumeration; my §5/§3 will still name the data-capture edges: duplicate-scan idempotency rejection event, over-scan warning event, wrong-product-scan event, unrecognized-scan event, multi-match selection event, printer-offline print-job failure record.

**§8 QA Acceptance Criteria** — Lens B owns; I will supply the event-assertion halves (e.g. "Then an `item_inbound` record exists with actor, qty, order id" style Then-clauses) so QA verifies persistence, not just UI.

**§9 Out of Scope & Open Questions** — Hold apply/release (OMS/Order detail); Order Management import/sample config; label layout content (Phase 3-1); product-name/brand-prefix data fix (upstream); + Open Questions below.

**§10 Decision Log** — dated entries: 07-09 v1 rules set (auto-outbound, bulk bar, unified search, label rename S1-10); 07-13 v20 sourcing routes/Hold/return lookup/Comments hub; 07-21 photo-upload removed (deferred), double-click bug → handoff note; 07-22 Deleo tracking column removed from this page; 07-23 Coupang `[V1]` note tidied; unrecognized-pool UX inversion (tracking-missing); 07-27 State 6/6b merged in (separate `inbound-receiving` page killed, 404); 07-29 comments full-search + floating save; 08-02 Expected Inbound badge (C안), 3-stage request lifecycle, Edit Expected Qty, unrequested arrivals → existing unrecognized pool (dedicated intake path rejected); 08-03 send sound, JIT purchase-channel parenthesis, multiple tracking per request, carrier auto-record NOT supported, match-writes-tracking-onto-line footnote, #fulfillment-admin-comments confirmed.

---

## 3. LENS-A DEEP INVENTORY

### 3a. Data Capture event list (35 events, [G-8] doctrine — actor + timestamp + entity + old/new on every one)

**Scan & search (silent + feed UI)**
- DC-1 `barcode_scan` — every scan/submit: raw value, normalized value (post-`[V1]` strip), actor, ts, resolution result (customer_order / inbound_request / return / unrecognized / multi_match), resolved entity id. Feeds Live Barcode Feed (S1-16); full history backend; export by date.
- DC-2 `search_manual` — typed (non-scanner) query + result count. Silent.
- DC-3 `multi_match_selection` — candidates shown, choice made, actor, ts. Silent.
- DC-4 `unrecognized_scan` — barcode, actor, ts (M2 opened). Silent.

**Customer-order inbound/outbound (Actor Log UI = view)**
- DC-5 `item_inbound` — order id, SKU, qty, actor, ts, method (scan / row button / bulk).
- DC-6 `bulk_inbound` — order id, SKU list, actor, ts (emits per-SKU DC-5 children).
- DC-7 `order_outbound` — order id, SKU set + total qty, actor, ts, trigger (manual / combined-last-item / bulk-all), status old→new (processing→prepare shipment).
- DC-8 `outbound_auto_trigger` — records that outbound was auto-fired by full-inbound completion (distinct trigger field on DC-7; Hold-blocked case records `outbound_suppressed_hold`).
- DC-9 `inbound_cancel` — order id, SKU, qty, restock yes/no, restock qty, memo, actor, ts; stock delta Reserved→Available old/new (M1).
- DC-10 `outbound_cancel` — order id, actor, ts, status rollback old/new (S3-2).
- DC-11 `idempotency_reject` — server-side rejected duplicate submit (double-click bug [G-9]): original event id, actor, ts. Silent; required to prove the fix.

**Shelf / location / barcode master**
- DC-12 `shelf_assign` — order id, shelf old→new, actor, ts (S1-2 floating save).
- DC-13 `location_edit_internal` — request id, SKU, location old→new, actor, ts (S6-7).
- DC-14 `product_barcode_register` — SKU, barcode null→value, actor, ts, source screen (S1-20; product-master write).

**Comments [G-7]**
- DC-15 `comment_post` — entity type (order / inbound_request), entity id, text, author, ts, mentioned users[].
- DC-16 `comment_mention_notify` — Slack delivery record: channel #fulfillment-admin-comments, mentioned user, message ts, deep link. Silent.
- DC-17 `comment_star` / `comment_unstar` — comment id, actor, ts.
- DC-18 `comment_read` / `mark_all_read` — comment ids, actor, ts (badge integrity).
- DC-19 `comment_autopost_system` — system-authored comments (M6 qty edit, unrecognized match confirm) flagged `source=system`, carrying structured old/new payload.

**Customer return (State 4 / M3)**
- DC-20 `return_scan_detected` — return barcode, order id, order status at scan (refunded/failed/completed), actor, ts.
- DC-21 `return_restock_confirm` — order id, per-item {SKU, ordered qty, restock qty (0 = excluded, still recorded), location old→new}, memo, actor, ts; Current Stocks deltas. Actor Log "Return Restock (Stock added)".
- DC-22 `return_item_excluded` — qty-0 lines persisted explicitly (damage/loss signal; see Q5).

**Supplier return labels (M4) & print [G-4]**
- DC-23 `return_label_print` — selected items {KR name, size?, qty?}, carrier (chip or custom text), actor, ts, print job id.
- DC-24 `order_label_print` — order id, carrier, actor, ts, print job id (order-card Print).
- DC-25 `auto_label_print_single_item` — order id, trigger scan id, actor, ts (S1 footer a).
- DC-26 `print_job_result` — job id, agent, printer, success/failure + error, ts (printer-offline evidence).

**Internal inbound (State 6/6b)**
- DC-27 `internal_scan_increment` — request id, SKU, received qty old→new (+1), actor, ts, method=scan.
- DC-28 `received_qty_manual_edit` — request id, SKU, old→new, actor, ts, method=manual (S6-6; distinguishable from DC-27).
- DC-29 `wrong_product_scan` — request id, offending barcode/SKU, actor, ts (warning sound fired). Silent + sound.
- DC-30 `over_scan_warning` — request id, SKU, attempted qty > expected, actor, ts.
- DC-31 `expected_qty_edit` — request id, SKU, expected old→new, reason enum, memo, editor, ts (M6) → also emits DC-19 + DC-16.
- DC-32 `partial_inbound_save` — request id, per-SKU received, reason enum, memo, actor, ts; inventory deltas applied; request status old→PARTIAL (M5).
- DC-33 `full_inbound_confirm` — request id, per-SKU {expected, received, location}, actor, ts; status →INBOUNDED; Received Date auto-set; inventory deltas (S6-8/6b).
- DC-34 `state6_entry` — request id, entry method (tracking scan / S0-2 row click), actor, ts (damaged-label analytics for the no-scan path).

**Unrecognized (M2/M2b)**
- DC-35 `order_lookup` + `tracking_match_register` + `missing_tracking_send` — (a) lookup: barcode, entered order no, result; (b) match: order id, product line, tracking null→value, actor, ts (→ rescan resolves); (c) send: barcode, picked product, qty, memo, carried failed order no, registrant, ts → Slack #unrecognized-tracking.

**Retention/export statements to write in §5**: barcode feed = unlimited backend retention + export-by-date (format = dev); actor log & all DC events = permanent, queryable by order/request/SKU/actor; comments = permanent (AI-training asset, G-7); every UI log is a projection of these events, deleting a UI row never deletes the event.

### 3b. Operator-flow notes (what §1/§3 must preserve)
- The loop is *scan → hear sound / glance toast → scan*; anything demanding mouse travel or reading is an exception path. All confirming actions reachable from keyboard/scan flow.
- Focus discipline is the #1 field bug class: spec will state focus invariants as testable rules (after every action, after modal close, after State 6b completion → search input focused, content selected).
- Sound semantics: send sound = accepted outbound-family action (S1-15); warning sound = wrong product in State 6 (S6-4); Closing's TTS voice is NOT on this page (delta note vs G-3b).
- Attention colors: amber = qty>1 / partial; red = return; purple = internal inbound; green = done — one glance from 2m distance.
- Modal typing is the slow path — M2b autocomplete, M3 auto-filled locations, M1 default qty all exist to minimize keystrokes; spec keeps defaults exact.

---

## 4. MANDATORY-INCLUSION MAP (owner's 12)

| # | Item | Lands here? | Where |
|---|---|---|---|
| 1 | Scanner protocol [G-1] | YES | §3 S0-1, S1-1/12/14, S6-4, S6b-2; §4 delta |
| 2 | Confirmation toast [G-2] | YES | §3 S1-15, S3-3, M2b toast, S6b toast; every confirming action |
| 3 | Audio [G-3] | YES (delta) | send sound S1-15 (11 buttons); State 6 wrong-product warning sound S6-4; TTS voice = Closing only |
| 4 | Instant carrier-agnostic print [G-4] | YES | order Print, M4 return labels, single-item auto-print (S1 footer a); §6 print pipeline |
| 5 | Sample dual-view [G-13] | cross-ref only | Print behavior references G-13; owned by order-management (+ Phase 3-1 label layouts) |
| 6 | Unrecognized matching | YES | M2/M2b + S1 footer b + match toast; tracking written onto product line, rescan resolves |
| 7 | Multiple tracking per request [G-10] | YES | S6-1; §4 |
| 8 | RTO Korean names [G-6] | not this page | (M4 labels DO use KR names — G-6 delta noted here) |
| 9 | Line-based location filter [G-14] | not this page | Inventory |
| 10 | Audit-mode-only visibility [G-14] | not this page | Inventory |
| 11 | JIT residual stock in Inventory | cross-ref | M1 cancel-restock of mistaken JIT creates residual stock → Inventory spec |
| 12 | Comment @mention Slack routing [G-7] | YES | §6 table below — channel CONFIRMED |

**Slack routing rows this page uses (CONFIRMED per `_inputs/slack-routing.md`, 2026-08-03):**
1. Unrecognized barcode sent to Missing Tracking List → **#unrecognized-tracking** (payload: tracking no., product via autocomplete, qty, memo, registrant, suspected orders) — fired from M2b.
2. Comment @mention (any comment surface on this page: order cpanel, State 6 request comments) → **#fulfillment-admin-comments** (body @mentions the tagged person → Slack personal mention notification; channel doubles as team-visible archive; payload: order/entity no., text, time, author, @mentioned user, deep link).
3. Expected-qty edit (M6) → auto comment on the request + @requester, routed to **#fulfillment-admin-comments** with @mention (payload: old→new qty, reason, editor).
4. Match confirmed (unrecognized resolution) → auto comment + @registrant → **#fulfillment-admin-comments** (payload: tracking no., matched product line, resolver) — primary surface is tracking-missing; view-orders M2 on-the-spot match relation = Open Q3.
Not this page: morning no-tracking checks → #wholesale-ops / #partnership-kr (inbound-request spec).

---

## 5. OPEN QUESTIONS

### Owner must decide
- **Q1 (S3-4)** "Cancel Inbound disabled after outbound; Cancel Outbound first" is still labeled *proposal* in the wireframe (since 07-09). Confirm as a rule, or drop?
- **Q2 (S6b-1 vs S6 footer)** Contradiction in the wireframe: State 6b banner says "Carrier recorded automatically" but State 6 legend footer says "automatic Carrier recording is not supported (confirmed 2026-08-03)". Presume 08-03 wins (NOT supported) → banner text needs a wireframe fix; owner confirm.
- **Q3 (M2 vs routing row 4)** When a match is confirmed on-the-spot in View Orders M2 (scanner = resolver = registrant), does it also fire the "match confirmed" auto-comment + Slack @registrant, or is that route only for resolutions made on the tracking-missing page?
- **Q4 (DC-22 / M3)** Returned items NOT restocked (qty 0 — damaged/discarded): is explicit persistence of the excluded lines + disposition (discard/inspect) required, or is qty-0-in-the-confirm-record enough? Data doctrine suggests capturing disposition; not in wireframe.
- **Q5 (S1-2)** Shelf value lifecycle: does Shelf auto-clear on Outbound / order completion, or persist? (Wireframe silent; affects reuse of temp shelves.)

### Developer decides at build time
- Idempotency key format + client debounce interval [G-9]; how DC-11 rejects are surfaced (silent vs toast).
- Live Barcode Feed export file format/columns; feed on-screen cap exact value (10 vs 20 — wireframe says "10–20", pick one).
- Barcode validation on S1-20 master write (EAN-13 checksum? duplicate-barcode-across-SKU conflict handling) — behavior specced, algorithm dev's.
- Multi-match selection UI layout (S1-1) — behavior + data captured specced; presentation dev's.
- Comment search: debounce, pagination, index scope limits (spec fixes: all orders, newest first, order-no/author/text match).
- Print agent product choice (PrintNode-class) and printer-offline retry policy — failure event DC-26 + red toast specced; retry policy dev's.
- Web Audio synth parameters (reference implementation already in wireframe JS) and warning-sound tone distinct from send sound.
