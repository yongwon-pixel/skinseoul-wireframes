# Order Detail — Spec Plan, LENS A (Operator & Data)

Planner: A (field usability · data capture · business rules · Slack routing). Wireframe SST: `wms2/order-detail/index.html` (2 states: Processing / On Hold, modal M3). Live: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/order-detail/

---

## 1. LEGEND INVENTORY (14 dots + 1 modal = 15 units; dots repeat identically in both states, 14 is Hold-only)

| # | What it is | Spec treatment |
|---|---|---|
| 1 | Operator Comments upgraded — @mention → Slack notify, per-order history accumulates, ★ save to hub | §3 [L-1] post/mention/star behavior; §5 comment events (posted, mention-notified, starred); §6 Slack row #fulfillment-admin-comments; §4 retention-as-AI-asset rule [G-7] |
| 2 | Inbound buttons reworked — per-row Inbound / Cancel Inbound + bottom Bulk Inbound Selected Items (checkbox-linked); "Request Inbound" retired; unclickable-button bug fixed | §3 [L-2] enable states, per-row vs bulk semantics, [G-2] toast, [G-9] double-click; §5 inbound/cancel/bulk events with inventory deltas; §4 per-product inbound grammar rule |
| 3 | Inbound/Outbound Actor Log (NEW) — who/when inbounded, outbounded, cancelled; bottom of order | §3 [L-3] columns (Time/Action/SKU/Qty/Operator/Note), ordering; §5 THE core doctrine surface — log = view over persisted events, never the only copy [G-8]; retention/export |
| 4 | Sourcing Route = 4 routes, plain black bold [G-5]; JIT purchase channel in parentheses (Coupang/Naver/Other retail = handler's dropdown pick at purchase time); Order Number = per-product purchase order no., linked | §3 [L-4] rendering + link target; §4 route taxonomy rule + JIT semantics ("purchased after the order"); §5 provenance of route + channel value |
| 5 | PIC edit made explicit — bordered "✎ Edit" button (old pencil unreadable/unclickable) | §3 [L-5] PIC change flow; §5 pic_changed event (old→new, actor, ts); §1 physical-context rationale (small icon failed on the floor) |
| 6 | Fulfillment Tracking + TRACKING HISTORY = identical to live admin, wireframe abbreviates rows only | §3 [L-6] declared unchanged; §5 silent system events (tracking sync, actor=system, synced-at ts); §7 sync-failure edge |
| 7 | Top-right Comments hub — [@ Mentions] + [★ Saved] + all-orders full-text search (order no./author/text, newest first), shared across screens | §3 [L-7] tabs, badge=unread count, search behavior, mark-all-read; §5 per-user read/star state events; §6 deep link: click → opens order |
| 8 | Change Status dropdown — 8 WC statuses, applied instantly, no refresh; on-hold disables Outbound | §3 [L-8] full status list, instant apply + toast [G-2]; §4 hold-gating rule; §5 status_changed event (old→new) — highest-value audit event on the page |
| 9 | "Outbound to Deleo BaroShip" → "Outbound"; enabled ONLY when every item INBOUNDED; disabled when incomplete or On Hold | §3 [L-9] enable predicate (two independent gates), [G-3a] send sound question, [G-9]; §4 order-level outbound rule + rationale; §5 outbound event with gate snapshot |
| 10 | Inventory columns cleaned — Delivery Company + Comments columns removed; Latest Inventory Count KEPT (restored 2026-07-23; JIT shows 0 = no warehouse stock) | §3 [L-10] column set (8 Inventory cols); §4 JIT-shows-0-is-correct rule (prevents false alarms); §10 removal→restore reversal dated |
| 11 | Product Name EN·KR — brand always bold-prefixed [G-6] | §3 [L-11]; §4 cite [G-6], page delta: BOTH EN and KR columns shown here; missing-brand = product-data fix, not UI |
| 12 | Line edit/delete UX (as live) — ✎ turns agent-tracking fields (Order Number · Order Date+Today · Product Cost · Tracking Number · CP Link) into inputs; ✓ Save / ✕ Cancel; 🗑 opens M3 | §3 [L-12] editable field list exact, Today shortcut, save/cancel; §5 field-level old/new event + 🤖-agent-autofill actor distinction; §7 concurrent-edit edge |
| 13 | Print label = just "Print" (no carrier suffix — carrier badge adjacent) | §3 [L-13] instant print [G-4], no dialog/tab; §5 label.printed event (actor, carrier, job id, result); §6 print pipeline; label LAYOUT out of scope (Phase 3-1) |
| 14 | On Hold state view — amber badge + banner; Outbound disabled, per-row Inbound still allowed; demo = combined Hold + incomplete inbound (3/4): releasing hold alone does NOT enable Outbound | §2 state 2 mapping; §3 [L-14] banner content + what changes vs state 1; §4 hold rules with CS rationale; §5 hold place/release events; §7 multi-cause-disable communication edge |
| M3 | Line delete confirmation modal — "cannot be undone", Cancel/Delete | §3 [L-M3] destructive confirm; §5 deleted event MUST persist full line snapshot (UI-irreversible ≠ data loss) [G-8]; §8 negative test (Cancel = no event) |

Unnumbered live-admin controls the spec must still cover (baseline behavior + data capture, flagged "unchanged from live"): ← Back to Orders · ↻ Audit History · ↗ View in WP · ⧉ Clone Order · ✕ Cancel Order · View Label · ✎ Change Tracking # · Reset Order · Billing/Shipping address ✎ · + Add Line Item · select-all checkbox · Hide Comments toggle · Total Quantity footer. Lens A claims their data-capture rows; Lens B covers their interaction detail.

---

## 2. SECTION OUTLINES (10 template sections)

### §1 Purpose & Users
- Single-order command center: order team (desk, monitor) + warehouse leads (mid-flow arrivals from View Orders deep links, comment-hub clicks, Slack mention links). NOT a scan surface — [G-1] explicitly N/A (scan lives in View Orders/Closing); state that to prevent devs adding a scan input here.
- Operational moments: (a) JIT purchase bookkeeping (handler fills Order Number/Date/Cost/Tracking/CP Link per line), (b) inbound exception handling per product, (c) hold management for urgent CS (cancellation·address change), (d) dispute resolution via Actor Log ("who inbounded this?"), (e) packing instructions via comments (VIP care notes).
- Physical context that shaped decisions: PIC pencil too small to read as clickable → [L-5] bordered button; unclickable Inbound button bug → [L-2]; 20-column 1680px table needs horizontal scroll — operator reaches Actions at far right (open dev question: sticky column).

### §2 Screen Inventory & Wireframe Map
- State 1 · Processing (default tab) — dots 1–13; Outbound enabled (4/4 INBOUNDED); row 1 shown in edit mode as [L-12] example.
- State 2 · On Hold (tab 2) — dots 1–14; hold banner [L-14]; Outbound disabled+gray; row 2 shows PENDING + per-row Inbound button variant (deliberate: proves Inbound allowed during hold); Change Status highlights on-hold.
- Modal M3 (wf-bar button "Modal: Delete Line" or any 🗑) — delete confirm.
- Sub-surfaces: Comments hub dropdown (💬, both states), Change Status dropdown, statusdd. Map each legend # ↔ §3 key, with reach path (which tab/button).

### §3 Functional Specification
- Per [L-1]..[L-14]+[L-M3] as inventoried above. Lens A emphasis per item: exact enable predicates ([L-9]: `every(line.inbound_status==INBOUNDED) && order.status != on-hold`), toast copy for every confirming action [G-2], no-refresh guarantee, [G-9] debounce+idempotency on Inbound/Cancel Inbound/Bulk/Outbound/Save/Delete, [L-12] editable-field whitelist (WC commerce fields Qty/Subtotal/Total NOT editable here — only agent-tracking fields), Today button sets local warehouse date.
- Baseline (unchanged-from-live) controls: one row each — behavior reference + required event row in §5. Note Deleo Tracking No stays on Order Detail though removed from View Orders (2026-07-21 handoff decision).

### §4 Business Rules (Lens A owns — full list in Part 3B below)
BR-1..BR-15 with rationale + dates; cite [G-2] [G-3] [G-4] [G-5] [G-6] [G-7] [G-8] [G-9]; page deltas only.

### §5 Data Capture (Lens A owns — full event list in Part 3A below)
D-1..D-26 + explicit non-events + retention/export.

### §6 Integrations
- Slack routing table (2 rows, below Part 4-adjacent).
- Deep links IN: View Orders row click, Comments hub item click ("click opens the order"), Slack mention payload deep link, tracking-missing match → this order. Deep links OUT: ← Back to Orders, ↗ View in WP, CP Link (Coupang product URL), Order Number lookup link, ↻ Audit History.
- Print pipeline [G-4]: local print agent, carrier from order (YUN badge), immediate output.
- Cross-page effects RECEIVED: unrecognized-match writes tracking no. into this order's line + auto comment @registrant (mandatory item 6, primary spec in tracking-missing/view-orders — here spec the landing artifacts).

### §7 Edge Cases & Error States (Lens B primary; Lens A contributes operator-context cases)
Candidates from A lens: multi-cause Outbound disable messaging (hold + 3/4) · inbound while on-hold then hold released · double-click on Inbound (known live bug) · print agent offline · line delete of an INBOUNDED line (inventory already counted — restock?) · concurrent edit of same line by two operators · Slack delivery failure on mention · JIT line with Latest Inventory Count 0 misread as error · Cancel Order with inbounded stock · edit-mode row abandoned (navigate away) · status change race vs Outbound click.

### §8 QA Acceptance Criteria (Lens B primary)
A contributes: every §5 event gets at least one G/W/T asserting the event row exists post-action (even for silent events — assert via Actor Log/audit surface where visible); toast-per-confirming-action sweep; Outbound gate matrix (4 combos: inbounded×hold).

### §9 Out of Scope & Open Questions
Out: label layout (Phase 3-1) · scan input ([G-1] N/A) · WP-side behavior behind ↗ View in WP · sample assignment (Order Management page [G-13]) · Procurement Hub. Open questions: Part 5 below.

### §10 Decision Log (dated)
2026-07-13 sourcing routes unified (→4 routes) · 2026-07-14 real-capture rework, commit 9844fe0 (real Order #407847, 20-col line items, actor log NEW, per-row inbound grammar, button enablement) · ~2026-07-22 Hold state view added (combined-case demo) · 2026-07-21 double-click bug → dev-handoff (not wireframed); Deleo Tracking No kept here, removed from View Orders · 2026-07-23 Latest Inventory Count REVERSAL: removed → restored (same live position; JIT=0) · 2026-07-29 Comments hub all-orders search added (commit 8e5abeb, order-detail 2 spots) · 2026-08-03 englishization (90 substitutions) · 2026-08-03 [G-2] toast owner emphasis, [G-4] instant print reconfirmed, #fulfillment-admin-comments channel confirmed (owner-created) · KR brand-bold 72-cell fix 2026-08-03 [G-6].

---

## 3. LENS-A DEEP INVENTORY

### 3A. Data Capture — full event list (D-n; every row = actor + timestamp + entity + old/new values, per [G-8])

Order lifecycle
- D-1 `order.status_changed` — [L-8]; old_status→new_status, actor, ts, source=detail-dropdown. Includes to/from on-hold.
- D-2 `order.hold_placed` / D-3 `order.hold_released` — derived from D-1 but spec'd as first-class (hold reason field = open question OQ-1); ts, actor.
- D-4 `order.cancelled` — ✕ Cancel Order; prior status, actor, ts (behavior unchanged from live; event still mandatory).
- D-5 `order.cloned` — ⧉; source_order→new_order id, actor, ts.
- D-6 `order.pic_changed` — [L-5]; old PIC→new PIC, actor, ts.
- D-7 `order.address_edited` (billing|shipping) — field-level old/new diff map, actor, ts.
- D-8 `order.reset` — Reset Order; snapshot of cleared shipment state old/new, actor, ts.

Shipment
- D-9 `shipment.tracking_changed` — ✎ Change Tracking #; old→new number, carrier, actor, ts.
- D-10 `shipment.tracking_synced` — SILENT, actor=system; sync ts, appended tracking events ([L-6]).
- D-11 `label.printed` — [L-13]; actor, ts, carrier, print-agent job id, result (success/fail) [G-4].
- (non-event) View Label = read-only preview, no persist required — state explicitly.

Line items / inventory
- D-12 `line_item.inbounded` — per-row Inbound [L-2]; SKU, qty, actor, ts, status PENDING→INBOUNDED, inventory delta.
- D-13 `line_item.inbound_cancelled` — Cancel Inbound; SKU, qty, actor, ts, restock flag (Actor Log shows "CANCEL INBOUND (Restock)"), inventory delta, note.
- D-14 `line_item.bulk_inbounded` — parent event (selection set, count) + child D-12 per SKU; actor, ts.
- D-15 `order.outbounded` — [L-9]; all SKUs+qty, actor, ts, gate snapshot at click (inbound completeness, hold state), carrier.
- D-16 `line_item.edited` — [L-12] ✓ Save; per-field old/new for the 5 agent-tracking fields ONLY; actor, ts.
- D-17 `line_item.autofilled` — SILENT, actor=Agent(🤖); fields, values, source, ts. Actor-type distinction (human vs agent) is a hard requirement — cost provenance.
- D-18 `line_item.deleted` — M3 Delete; FULL line snapshot persisted (all 20 columns), actor, ts. UI-irreversible, data retained.
- D-19 `line_item.added` — + Add Line Item; SKU, qty, initial values, actor, ts.
- D-20 `line_item.wc_recalculated` — SILENT, system; * asterisk provenance: WooCommerce original (SKU*, qty*) retained alongside variation-pack recalculated values — BOTH copies permanent.
- (non-event) checkbox selection, ✕ edit-cancel, Hide Comments toggle — ephemeral/local, no server event; state explicitly so devs don't over-log noise.

Comments (AI-training asset — [G-7])
- D-21 `comment.posted` — [L-1]; order, text, author, ts, mentions[] parsed.
- D-22 `comment.mention_notified` — SILENT; Slack channel, message ts, target user, delivery result (fail → retry/log, edge E-ref).
- D-23 `comment.starred`/`unstarred` — per-user, comment id, old/new, ts.
- D-24 `comment.read` / `mark_all_read` — SILENT per-user read-state change, ts (feeds badge count).
- D-25 `comment.auto_posted` — SYSTEM comments landing on this order (e.g., unrecognized-match "matched this order" with @registrant); flagged `source=system`, distinguishable from human comments in the AI-training corpus.
- (open) comment edit/delete — OQ-5; doctrine implies append-only.

Log/audit surfaces
- D-26 Actor Log render contract — [L-3] table = query over D-12/13/14/15 (and Note from D-13); newest first; never a separate store.
- Retention/export: ALL events permanent (no TTL); comments never deleted (AI asset); export expectation = Audit History surface + CSV precedent (closing page); events queryable by order, SKU, actor, date.

Count: 26 persisted event types (5 silent/system) + 4 explicit non-events.

### 3B. Business Rules (with rationale + dates)
- BR-1 Outbound enabled only when EVERY line INBOUNDED — order completeness gate; ship-incomplete prevention (C Behavior, 2026-07-14; combined demo 2026-07-22).
- BR-2 On-hold: Outbound blocked, Inbound still allowed — urgent CS (cancellation·address change) must not stop goods receipt (F Hold, 2026-07-14/22).
- BR-3 Releasing hold alone ≠ Outbound enabled — gates are independent; UI must communicate which gate blocks (legend 14, 2026-07-22).
- BR-4 Inbound = per-product; Outbound = order-level (legend 2, 2026-07-14; "Request Inbound" name retired).
- BR-5 Sourcing routes: exactly 4, colorless black bold [G-5]; JIT carries purchase channel parenthetical chosen by handler at purchase (2026-07-13→14).
- BR-6 Latest Inventory Count kept; JIT rows legitimately show 0 (no warehouse stock) — not an error state (restored 2026-07-23).
- BR-7 Delivery Company + Comments columns removed from line items; order comments live ONLY in Operator Comments (2026-07-14). Deleo Tracking No retained on this page (2026-07-21).
- BR-8 Brand bold-prefixed on EN and KR names [G-6] (B; KR cells fixed 2026-08-03).
- BR-9 Every confirming action → green top-right toast, zero full-page refresh [G-2] (owner emphasis 2026-08-03).
- BR-10 All mutating buttons double-click-safe [G-9] (live bug logged 2026-07-21).
- BR-11 Print = instant, carrier-agnostic, no dialog [G-4] (reconfirmed 2026-08-03); label layout deferred to Phase 3-1.
- BR-12 Status vocabulary = 8 WC statuses exactly (pending/processing/on-hold/completed/refunded/failed/shipped/prepare-shipment), instant apply (legend 8, as live).
- BR-13 WooCommerce original values (*) preserved beside recalculated values — provenance never overwritten (wireframe liinfo note).
- BR-14 🤖 agent-autofilled fields human-editable; actor type always recorded (legend/liinfo; [G-8]).
- BR-15 Comment history append-only, permanent, AI-training asset [G-7]; per-order accumulation (legend 1).

### 3C. Operator-flow notes (feed §1/§3/§7)
- Arrival paths are interrupt-driven (Slack mention link, hub click) — page must land scrolled-to-relevant? No such decision encoded — do NOT spec; note as B-lens QA observation only.
- Speed-pressure surface = per-row Inbound during goods arrival; large buttons, toast confirms peripheral-vision-friendly (green), no refresh so the row stays put.
- 1680px table: Actions at far right after 20 columns — OQ-6 (sticky column, dev).
- Disabled Outbound must self-explain (banner in hold; 3/4 count visible via Inbound Status tags) — operator should never file "button broken" tickets for a working gate.
- Comments = packing-floor coordination channel; Slack mention is the reach mechanism for staff not at a monitor (#fulfillment-admin-comments).
- Actor Log kills "who did this" disputes on the spot; Note field (e.g., "Corrected duplicate inbound") is free-text — capture required, content optional.

---

## 4. MANDATORY-INCLUSION MAP (of the 12)

| # | Item | Lands here? | Where |
|---|---|---|---|
| 1 | Scanner protocol [G-1] | NO — explicitly N/A; state in §1/§9 (no scan surface on this page) |
| 2 | Global confirmation toast [G-2] | YES | §3 every confirming action, §4 BR-9, §8 toast sweep |
| 3 | Audio feedback [G-3] | PARTIAL/OQ | [G-3a] wording covers "Outbound-class buttons" → Order Detail Outbound [L-9]; mandatory-map lists only View Orders/RTO; wireframe here has no sound. OQ-2 (owner) |
| 4 | Instant carrier-agnostic print [G-4] | YES (named for Order Detail) | §3 [L-13], §6 print pipeline, §5 D-11 |
| 5 | Sample dual-view [G-13] | NO — Order Management page; §9 out-of-scope note only |
| 6 | Unrecognized matching behavior | YES as receiving surface | §6 cross-page effects (tracking written to line + auto comment @registrant = D-25); primary spec in tracking-missing/view-orders |
| 7 | Multiple tracking numbers [G-10] | NO (inbound-request/view-orders) — but §3 [L-4]/[L-12] must disambiguate line-item PURCHASE tracking no. (inbound, JIT) vs shipment tracking no. (outbound carrier) to prevent conceptual collision |
| 8 | RTO Korean names [G-6] | NO — RTO page; here [G-6] applies as brand-bold EN·KR columns (mandatory 12's sibling rule cited via BR-8) |
| 9 | Line-based location filter [G-14] | NO — Inventory page |
| 10 | Audit-mode summary visibility [G-14] | NO — Inventory page |
| 11 | JIT residual stock in Inventory | NO — Inventory page (JIT=0 display here is related context, BR-6) |
| 12 | Comment @mention Slack routing [G-7] | YES — CORE page for it | §3 [L-1]/[L-7], §5 D-21/22, §6 routing table; channel CONFIRMED #fulfillment-admin-comments |

Slack routing rows used by this page (channels CONFIRMED 2026-08-03, `_inputs/slack-routing.md`):
1. Comment @mention (any screen, this page posts them) → **#fulfillment-admin-comments** — payload: order/entity no., comment text, time, author, @mentioned user, deep link; message body @mentions the person (personal notification) + channel doubles as team-visible archive.
2. Match confirmed in Unrecognized Tracking → auto comment on THIS order + @registrant → same route, **#fulfillment-admin-comments** with @mention (this page displays the landed comment; D-25).
(No other rows: #unrecognized-tracking = view-orders/tracking-missing trigger; #wholesale-ops/#partnership-kr morning checks = inbound-request.)

---

## 5. OPEN QUESTIONS

### Owner must decide
- OQ-1 Hold reason: banner reads "On Hold by urgent CS request" — is a reason/note input required when selecting on-hold, and is it persisted (D-2 payload) + shown in the banner? Wireframe shows no input.
- OQ-2 Does [G-3a] send sound apply to Order Detail's Outbound button? Global rule says "Outbound-class buttons"; implementation ledger + mandatory map cover only View Orders/RTO; this wireframe has no Web Audio.
- OQ-3 Cancel Order (✕) with already-INBOUNDED lines: must operator Cancel Inbound (restock) first, or does cancel auto-restock? Not annotated anywhere; encodes a real inventory decision.
- OQ-4 Is there a Cancel Outbound on Order Detail after outbound? View Orders ledger has "Cancel Outbound first, then Cancel Inbound" as 제안 상태 (proposal, 2026-07-x) — never confirmed; this page shows none.
- OQ-5 Comment edit/delete policy: [G-7] AI-asset doctrine implies append-only/no delete — confirm explicitly (affects D-21 immutability).

### Developer decides at build time
- OQ-6 Sticky/pinned Actions (and SKU) column on the 1680px line-items table vs plain horizontal scroll — usability call, no owner decision encoded.
- OQ-7 Idempotency key format + debounce window for D-12/13/14/15/16/18 [G-9].
- OQ-8 Print-agent failure surfacing (toast copy, retry) within the [G-4] no-dialog constraint.
- OQ-9 Storage model for per-user comment read/star state (D-23/24) and unread-badge computation.
- OQ-10 Reset Order exact reset scope — mirror live semantics; capture old/new snapshot (D-8) whatever the scope.
- OQ-11 Tracking-sync cadence + system-actor naming convention for D-10/D-17/D-20/D-25 (`system`, `agent`, `cron` labels).
