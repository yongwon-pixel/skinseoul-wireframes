# Order Detail — Spec Plan (LENS B: Developer & QA)

Page slug: `order-detail` · Wireframe SST: `wms2/order-detail/index.html` · Live: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/order-detail/
Planner lens: functional precision per legend item, Edge Cases section, machine-runnable QA criteria. Overlap with Lens A (operator/data) is intentional.

Wireframe surface map: 2 states (`#st-normal` "1 · Processing", `#st-hold` "2 · On Hold", switched by `.wf-tab[data-ostate]`) + 1 modal (`#m-del`, opened by wf-bar button "Modal: Delete Line" or any 🗑 row button). Legend dots: 1–14 + M3. **15 implementation units total.**

---

## 1. LEGEND INVENTORY (all 15 — missing one = planning failure)

| # | What it is | Spec treatment |
|---|---|---|
| L-1 | Operator Comments section — @mention→Slack, per-order history, ★ save to hub | §3 full functional spec (input validation, empty-guard, @parse, Slack payload per `_slack-routing` row 4 → #fulfillment-admin-comments); §5 persist events; §8 ~10 scenarios |
| L-2 | Per-row **Inbound / Cancel Inbound** + bottom **Bulk Inbound Selected Items** (checkbox-linked); "Request Inbound" name retired; unclickable-button bug fixed | §3: trigger/enabled-conditions/server action/state transition PENDING↔INBOUNDED; idempotency [G-9] (this is THE double-click-bug surface); §7 largest edge cluster; §8 ~12 scenarios |
| L-3 | Inbound/Outbound **Actor Log** (new) — Time·Action·SKU·Qty·Operator·Note table | §3: read-only view over persisted events [G-8]; row grammar incl. `CANCEL INBOUND (Restock)` + aggregate `All (4 SKU)` outbound row; §5 primary anchor; §7 empty state; §8 ~4 scenarios |
| L-4 | Line Items sourcing routes — 4 routes plain black bold [G-5], `JIT (Coupang)` purchase-channel parens; Order Number = per-product purchase order no., linked | §3 rendering rules + link behavior; delta only vs [G-5]; §8 ~3 render assertions |
| L-5 | PIC field with explicit "✎ Edit" button (replaces tiny pencil) | §3: exact label, edit affordance, save→toast [G-2], persist old/new [G-8]; §9 open Q (picker vs free text, notify?) |
| L-6 | Fulfillment Tracking + TRACKING HISTORY — identical to live admin, wireframe abbreviates rows only | §3 as "no change" with explicit note that real screen lists all events to ORDER_CREATION; sync timestamp display; §7 empty/no-shipment state |
| L-7 | Top-right Comments hub — [@ Mentions]+[★ Saved]+all-comments search (order no./author/text, newest first), unread badge | §3: search behavior incl. highlight `<mark>`, tab restore on clear, badge decrement rules, click→open order [G-12]; §8 ~8 scenarios incl. no-match empty state |
| L-8 | Change Status dropdown — 8 values (pending/processing/on-hold/completed/refunded/failed/shipped/prepare-shipment), applied instantly, no refresh [G-2]; on-hold disables Outbound | §3: per-value effect table, toast, idempotency on rapid re-select; §7 concurrency; §9 open Q (transition matrix, confirm on destructive values) |
| L-9 | **Outbound** button (relabeled from "Outbound to Deleo BaroShip") — enabled ONLY when every line INBOUNDED AND not On Hold | §3: gate = AND of two independent conditions; disabled rendering (`btn-gray`, `disabled`, opacity .55); send sound [G-3a — scope question flagged]; toast [G-2]; idempotency [G-9]; §8 the core gating matrix (~8 scenarios) |
| L-10 | Inventory column cleanup — Delivery Company·Comments removed; **Latest Inventory Count kept** (restored 2026-07-23; JIT shows 0 = no warehouse stock) | §3 column contract (8 Inventory cols); §4 rationale + date; §8 render assertions incl. JIT=0 is NOT an error [E-40] |
| L-11 | Product Name EN·KR — brand always bold-first [G-6]; missing-brand products need naming-logic fix | §3 delta on [G-6]; §9 note the naming-fix dependency |
| L-12 | Line edit/delete UX — ✎ turns agent-tracking fields (Order Number·Order Date+Today·Product Cost·Tracking Number·CP Link) into inputs; Actions→ ✓ Save / ✕ Cancel; 🗑 opens M3 | §3: per-field validation (date format, numeric cost, URL), Today button, Save server action + old/new capture [G-8], Cancel restores; §7 conflict/validation cluster; §8 ~8 scenarios |
| L-13 | Print button — label just "Print" (no carrier suffix; carrier badge adjacent) | §3: instant carrier-agnostic print [G-4], no dialog/new tab; §7 printer-offline, no-label-yet; §8 ~4 scenarios |
| L-14 | **On Hold state view** — amber badge, Hold banner, Outbound disabled, per-row Inbound still allowed; demo is COMBINED Hold + 3/4 inbounded (releasing hold alone must not enable Outbound) | §3 state contract: what changes vs Processing (5 diffs: badge, banner, dropdown highlight, Outbound disabled, row-2 PENDING+Inbound button); §8 combined-cause scenarios |
| M3 | Delete-line confirmation modal — "Are you sure?" / "This action cannot be undone. This will permanently delete the line item." / Cancel·Delete | §3: exact texts, both dismiss paths (✕, backdrop, Cancel), Delete server action + idempotency; §7 delete-of-inbounded-line, last-line; §9 open Q (restock on delete?) |

Non-legend but on-page (spec must still cover in §3/§7): subbar buttons (← Back to Orders · ↻ Audit History · ↗ View in WP · ⧉ Clone Order · ✕ Cancel Order), View Label, ✎ Change Tracking #, Reset Order, + Add Line Item, Billing/Shipping ✎ edits, select-all checkbox. These get functional stubs + open questions — several have no decided behavior (see §5 below).

## 2. SECTION OUTLINES (10 template sections)

1. **Purpose & Users** — single-order control room: order team (status/PIC/comments/line edits), warehouse staff (inbound/outbound execution, actor log), admin (audit). Physical context: this page is mouse-driven (NO scan input here — [G-1] does not apply; state that explicitly to prevent QA misapplication).
2. **Screen Inventory & Wireframe Map** — table: st-normal (L-1..13, reach: default tab "1 · Processing"), st-hold (L-14 + deltas, tab "2 · On Hold"), M3 (wf-bar "Modal: Delete Line" or any 🗑). Legend↔section 1:1 map incl. M3.
3. **Functional Specification** — per L-n as in table above. Cross-cutting: every confirming action → green top-right toast [G-2], exact toast strings proposed per action; all mutating buttons double-click-safe [G-9] (client debounce + server idempotency key — cite handoff note A: known live bug, double-click processes twice); no full-page refresh anywhere [G-2]. Buttons table: exact label, enabled-when, effect, feedback.
4. **Business Rules** — Outbound gate rule (all-INBOUNDED AND not-on-hold; two independent causes, 2026-07-14/08-03); Hold semantics: inbound allowed, outbound blocked (F Hold); no auto-outbound while On Hold (July ledger: full-inbound⇒auto-outbound applies to View Orders bulk — whether it applies here = open Q); JIT holds no warehouse stock ⇒ Latest Inventory Count 0 by design (2026-07-23 restore); sourcing routes [G-5]; brand-first naming [G-6]; comments doctrine [G-7]; status dropdown values fixed at 8 (cancel is NOT a dropdown value — separate Cancel Order button).
5. **Data Capture** — Lens A owns depth; B contributes the transactional set that QA asserts: INBOUND / CANCEL_INBOUND(+restock flag+note) / OUTBOUND(aggregate) / BULK_INBOUND(per-SKU rows) / STATUS_CHANGE(old→new) / HOLD_SET·RELEASE / LINE_EDIT(field-level old/new) / LINE_DELETE / LINE_ADD / PIC_CHANGE / TRACKING_CHANGE / RESET_ORDER / COMMENT_POST(+mentions) / STAR·UNSTAR / PRINT_REQUESTED(+agent result). Each: actor, ts, entity, old/new [G-8]. Actor log UI = view over events, never the only copy.
6. **Integrations** — Slack: comment @mention → #fulfillment-admin-comments (CONFIRMED 2026-08-03, payload: order no., text, time, author, @mentioned user, deep link); no other confirmed routes on this page. Cross-page: Back to Orders → view-orders; hub comment click → order deep link [G-12]; CP Link → external Coupang URL (new tab); View in WP → WP admin. Print pipeline: local print agent [G-4]. WooCommerce sync boundary for line edits/deletes (flag).
7. **Edge Cases & Error States** — full [E-n] inventory below (§3 of this plan).
8. **QA Acceptance Criteria** — plan below (§3): ~72 scenarios, each tagged `[WF]` (executable on static wireframe now) or `[ADMIN]` (assertable only on real admin; kept in runbook as deferred), keyed to L-n/E-n.
9. **Out of Scope** — label layout (Phase 3-1), scanner protocol (not this page), Procurement Hub, WP-side behavior, sample assignment UI (lives on Order Management; only dual-view [G-13] downstream effects noted). Open questions split below (§5).
10. **Decision Log** — 2026-07-14 real-capture rework (commit 9844fe0, Order #407847); 2026-07-21 full capture + double-click bug moved to handoff notes (not annotated in wireframe); 2026-07-22 Hold state view added; 2026-07-23 Latest Inventory Count restored / Delivery Company+Comments columns removed; 2026-08-03 English pass (90 replacements), global toast rule, instant print reconfirmation, comments channel confirmed, "Request Inbound" retired, Print label de-suffixed, Outbound relabel + gate.

## 3. LENS-B DEEP INVENTORY

### 3a. Edge-case candidates [E-n] (exhaustive; §7 will keep all, marking expected behavior or OPEN)

Idempotency & double-action [G-9]:
- E-1 Double-click per-row Inbound → exactly one INBOUND event (known live bug — regression anchor)
- E-2 Double-click Outbound → one OUTBOUND event, one send sound
- E-3 Double-click Bulk Inbound → selected set processed once
- E-4 Double-click M3 Delete → one deletion, modal closes once
- E-5 Rapid re-select same status in Change Status dropdown → no duplicate STATUS_CHANGE events
- E-6 Double-click Print → one print job at agent [G-4]

Inbound/Outbound gating & state:
- E-7 Bulk Inbound with 0 checkboxes selected → button disabled or error toast (decide: disabled preferred)
- E-8 Bulk Inbound selection includes already-INBOUNDED lines → idempotent skip, toast reports n processed / m skipped
- E-9 Inbound on a line concurrently inbounded by another operator (stale row) → server rejects, row re-renders INBOUNDED, non-green toast
- E-10 Cancel Inbound after order already outbounded → blocked with error state (OPEN: allowed with restock?)
- E-11 Outbound clicked in the same moment another operator cancels an inbound → server re-validates gate, rejects with reason
- E-12 Full inbound reached while On Hold → Outbound stays disabled; no auto-outbound fires
- E-13 Hold released while only 3/4 inbounded → Outbound still disabled (combined-cause, L-14 demo case)
- E-14 Hold set (on-hold selected) while Outbound request in flight → server decides atomically; spec the winner
- E-15 Cancel Inbound requires/records restock + optional note (actor log shows `CANCEL INBOUND (Restock)`) — behavior when note empty
- E-16 Outbound on order whose status is refunded/failed → blocked (OPEN: which statuses block outbound besides on-hold?)

Line edit / delete / add (L-12, M3):
- E-17 Save with malformed Order Date (non `YYYY-MM-DD`) → inline validation, no server call
- E-18 Save with non-numeric or negative Product Cost → reject
- E-19 Save with invalid CP Link URL → reject or warn (decide)
- E-20 Edit Cancel (✕) → all 5 fields restore originals, zero events persisted
- E-21 Two operators edit same line; second Save → conflict behavior (last-write-wins vs 409 — DEV default: server version check + reload toast)
- E-22 Delete INBOUNDED line → inventory/restock implication (OPEN — owner)
- E-23 Delete the only remaining line → 0-item order allowed? (OPEN — owner)
- E-24 M3 dismiss via ✕ / backdrop / Cancel → no deletion, no event
- E-25 Add Line Item on outbounded/completed order → blocked? (OPEN — owner)
- E-26 Today button sets today's date in the row's Order Date input only

Comments & hub (L-1, L-7):
- E-27 Add Comment with empty/whitespace textarea → no-op (wireframe already guards)
- E-28 @mention of nonexistent user → posts as plain text, no Slack (decide + OPEN autocomplete)
- E-29 Slack delivery failure → comment still persists; retry/queue note; never blocks UI
- E-30 Very long comment / HTML·script chars → escaped (wireframe search already escapes; real input must too)
- E-31 Hub search with no matches → "No matching comments" empty state
- E-32 Clearing search input → tabs reappear, previously active tab restored
- E-33 Mark all read → badge clears everywhere (nav badge + tab badge), unread styling removed
- E-34 Star toggle races / double-toggle → final state consistent, Saved tab syncs
- E-35 Comment posted on this order by someone else while page open → list freshness (poll/push or on-action refresh — DEV)

Network & infra:
- E-36 Network failure mid-Inbound (response lost) → retry with same idempotency key; no double stock movement; row state resolves on reload
- E-37 Network failure mid-Outbound → same contract; actor log is ground truth
- E-38 Network failure posting comment → no duplicate on retry
- E-39 Print agent offline/unreachable → explicit error toast within timeout; NO silent success, NO browser dialog fallback [G-4]
- E-40 Print when order has no label/tracking yet → button disabled or error (OPEN — owner)

Display & empty states:
- E-41 JIT line Latest Inventory Count = 0 → expected, not an error (regression guard for QA misreading)
- E-42 Actor log empty (new order) → empty-state row, section still renders
- E-43 Tracking history absent (pre-shipment order) → SHIPMENT DETAILS/HISTORY empty states
- E-44 WHOLESALE line has no purchase Order Number/Date/Tracking → renders "–" (as wireframe row 3)
- E-45 Missing-brand product name → rendering until naming fix lands (L-11)
- E-46 Status dropdown open, click elsewhere → closes with no change

Header/subbar actions (functional stubs):
- E-47 Cancel Order on order with INBOUNDED JIT lines → restock chain (OPEN — owner)
- E-48 Reset Order semantics/scope (OPEN — owner); Reset on DELIVERED shipment
- E-49 Change Tracking # to a number already on another order → duplicate check (OPEN)
- E-50 Clone Order — what is copied (lines? PIC? comments excluded?) (OPEN — owner)

### 3b. QA scenario plan (template §8)

Format: Given/When/Then, keyed `[L-n]/[E-n]`, each tagged **[WF]** (runnable on the static wireframe today via exact labels/selectors) or **[ADMIN]** (needs real backend; kept as deferred rows so the runbook survives into the real admin). Negative tests included. Estimated counts:

| Runbook section | Scenarios | WF-runnable |
|---|---|---|
| Comments post + @mention + star (L-1) | 10 | 7 |
| Comments hub tabs/search/badge (L-7) | 8 | 8 |
| Per-row + bulk Inbound (L-2, E-1,3,7,8,9) | 12 | 4 |
| Outbound gating matrix (L-9, L-14, E-2,12,13,16) | 8 | 5 |
| Change Status + Hold view (L-8, L-14, E-5,46) | 10 | 7 |
| Line edit ✓/✕ + validation (L-12, E-17..21,26) | 8 | 4 |
| Delete modal M3 (E-4,22,23,24) | 5 | 3 |
| Print (L-13, E-6,39,40) | 4 | 1 |
| Actor log + rendering contracts (L-3,4,10,11, E-41..45) | 7 | 7 |
| **Total** | **~72** | **~46** |

Three fully worked examples (final spec will use exactly this shape):

**QA-OUT-3 [L-9][L-14][E-13] — Releasing hold alone must not enable Outbound. [WF]**
- Given: the live wireframe, wf-bar tab "2 · On Hold" clicked; section `#st-hold` is visible
- When: I inspect the footer of the Line Items section
- Then: the button labeled "📦 Outbound" has the `disabled` attribute and gray styling (class `btn-gray`), AND the amber banner containing the exact text "On Hold by urgent CS request — inbound still allowed, but Outbound disabled. Release the hold (Change Status) to ship" is visible, AND row SKU 100043697 shows tag "PENDING" with a green "Inbound" button — proving the disable has two independent causes (hold AND 3/4 inbound). [ADMIN continuation: changing status to processing with the line still PENDING keeps Outbound disabled; inbounding the last line then enables it and one click plays the send sound [G-3a] and shows a green top-right toast.]

**QA-DEL-1 [M3][E-24] — Delete confirmation is explicit and dismissible without effect. [WF]**
- Given: wireframe state "1 · Processing"; I click the 🗑 button in the Actions cell of the row with SKU 100043697
- When: the overlay `#m-del` opens
- Then: header text is exactly "Are you sure?", body text is exactly "This action cannot be undone. This will permanently delete the line item.", footer has buttons "Cancel" and "Delete"; clicking "Cancel" (and separately: the ✕, and the backdrop) closes the overlay and the row still exists with 4 rows total in the table. [ADMIN: clicking "Delete" removes the line, decrements Total Quantity, appends a LINE_DELETE actor-log event, and shows a green toast.]

**QA-HUB-4 [L-7][E-31][E-32] — All-comments search: match, highlight, no-match, restore. [WF]**
- Given: I click the "💬 Comments" button in the top nav (badge shows "2") and the dropdown opens with tab "@ Mentions" active
- When: I type "miranti" into the input with placeholder "🔍 Search all comments — order no. · author · text"
- Then: the tab bar hides; a results pane shows header "1 results · newest first · click to open the order" and one item containing "Order 407812" with "Miranti" wrapped in `<mark>` highlight
- When: I replace the query with "zzzz"
- Then: the pane shows exactly "No matching comments"
- When: I clear the input
- Then: the tab bar reappears with "@ Mentions" still active and its pane restored.

## 4. MANDATORY-INCLUSION MAP (of the 12)

| # | Item | Lands here? | Where in this spec |
|---|---|---|---|
| 1 | Scanner protocol [G-1] | **No** — no scan surface on Order Detail | §1 explicit exclusion note (prevents QA misapplication) |
| 2 | Global confirmation toast [G-2] | Yes (all screens) | §3 cross-cutting + every mutating L-n; §8 toast assertions |
| 3 | Audio feedback [G-3] | Partial — (a) send sound on the Outbound button (outbound-class); (b) voice N/A | §3 L-9; scope flagged in §5 Q-A6 (mandatory list names View Orders/RTO only, but G-3a says "outbound-class buttons") |
| 4 | Instant carrier-agnostic print [G-4] | **Yes — Order Detail explicitly named** | §3 L-13, §7 E-6/E-39/E-40, §8 print scenarios |
| 5 | Sample dual-view [G-13] | No (Order Management page) | §9 out-of-scope pointer; note if line items ever display "(+ sample set)" → Q-A7 |
| 6 | Unrecognized matching writes tracking onto product line | Display side only — the written Tracking Number appears in this page's Inventory columns | §3 L-4/L-12 note + §6 cross-page reference to tracking-missing spec |
| 7 | Multiple tracking numbers per request [G-10] | No (Inbound Request + View Orders) | §9 pointer |
| 8 | RTO Korean names [G-6] | No | — (KR name column here already specced under L-11/[G-6]) |
| 9 | Line-based location filter [G-14] | No (Inventory) | — |
| 10 | Audit-mode-only visibility [G-14] | No (Inventory) | ↻ Audit History link noted in §3 stub |
| 11 | JIT residual stock | No (Inventory) | E-47 cancel-restock touches its origin; cross-ref only |
| 12 | Comment @mention Slack routing [G-7] | Yes — channel now CONFIRMED #fulfillment-admin-comments | §3 L-1/L-7, §6 routing table |

Net: 4 land materially (2, 3-partial, 4, 12), 1 display-side (6), rest are explicit exclusions/pointers so the coverage audit (P3-4 ①) can tick them.

## 5. OPEN QUESTIONS (do not invent — flag)

**Owner must decide:**
- Q-A1: Change Status transition matrix — are all 8 statuses selectable from any state? Do destructive picks (refunded / failed / completed) need a confirm step, given "applied instantly"? (L-8)
- Q-A2: Does full inbound on THIS page auto-trigger Outbound (as View Orders bulk does per 2026-07 ledger "전체 인바운드=오더 완결이므로 자동 아웃바운드"), or is Outbound always manual here? Interacts with the hold exception. (L-2/L-9)
- Q-A3: Deleting an INBOUNDED line (M3) — restock inventory or not? Same for ✕ Cancel Order on an order with inbounded JIT items (restock chain into Inventory residual stock). (M3, E-22, E-47)
- Q-A4: Reset Order (Fulfillment Tracking) — exact scope: clears shipment + tracking only, or also outbound state? Allowed after DELIVERED? (E-48)
- Q-A5: Print with no label yet — disabled vs error toast? And View Label when label missing. (L-13, E-40)
- Q-A6: Does the send sound [G-3a] apply to Order Detail's Outbound button? (G-3a says "outbound-class buttons"; mandatory item 3 names only View Orders/RTO.)
- Q-A7: Should Order Detail line items display sample-set assignment ("(+ sample set)") when Order Management assigned one? Not in wireframe.
- Q-A8: Cancel Inbound after order outbounded — hard-block, or allowed as correction with restock? (E-10)
- Q-A9: Clone Order — copied fields (lines? PIC? comments? agent tracking fields?). (E-50)
- Q-A10: Change Tracking # — duplicate-tracking check across orders, and does it re-generate/invalidate the label? (E-49)
- Q-A11: PIC edit — free text or user picker; is the new PIC notified (Slack)? (L-5)
- Q-A12: Which order statuses besides on-hold block Outbound (refunded/failed/completed)? (E-16)

**Developer decides at build time (spec will state defaults):**
- Q-B1: Debounce interval + idempotency-key format/TTL for [G-9] (default: key = action+order+line+client-uuid, server dedupe window ≥24h)
- Q-B2: Concurrent line-edit conflict: default optimistic version check → 409 → reload row + non-green toast (E-21)
- Q-B3: Exact toast copy strings and duration (green success, red/amber failure), consistent across 8 pages
- Q-B4: Comments freshness mechanism (poll vs push) and hub search index/debounce (E-35)
- Q-B5: Actor-log ordering/pagination beyond first N events
- Q-B6: Print-agent timeout value and retry policy surface (E-39)
- Q-B7: CP Link validation strictness (URL parse only vs domain allowlist) (E-19)
