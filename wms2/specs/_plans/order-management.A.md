# PLAN — Order Management (slug: order-management) — LENS A: OPERATOR & DATA

Planner: A (operator flow · data capture · business rules · Slack routing). Complementary lens B covers developer/QA precision.
Sources read: wireframe `wms2/order-management/index.html` (SST, 435 lines), spec-template.md, global-rules-draft.md, slack-routing.md, decision-sources.md, ledgers 2026-07-09 / 2026-08-02 (order-management + 스펙 필수 반영 bullets).

---

## 1. LEGEND INVENTORY (complete — 9 implementation units)

| # | What it is | Spec treatment |
|---|---|---|
| **1** | Filter-bar `⬆ Import` button → opens Marketing Order Import (M1). Confirmed 2026-07-23 (M1) + 2026-08-03 (carrier auto-assign, PIC custom, confirm toast). | §3 `[L-1]` full flow trigger; §4 no-stock-validation rule; §5 import event chain; §8 QA open-modal + confirm scenarios. |
| **2** | Action-row pair: `Sample Assignment ON` (green, → M2) and `Cancel Sample Assignment` (gray, → M3). Redesigned 2026-07-23 as simple ON/OFF; reconfirmed 2026-08-03. One legend number, two buttons — spec keys them `[L-2a]` ON / `[L-2b]` Cancel. | §3 both buttons: enabled conditions (Cancel always enabled? ON requires selection only for "Selected orders" target — B to pin), effects; §4 [G-13] deltas; §5 period lifecycle events. |
| **3** | **Removed item, no on-screen dot**: Bulk Hold Shipment button deleted — hold now via Change Status (on-hold) on Order Detail (spec F). | §3 `[L-3]` as explicit REMOVED entry + cross-ref to order-detail spec; §10 decision-log entry (cleanup, 2026-08-03 review round). Must not be silently dropped. |
| **4** | Order list table — identical to current admin, omitted from wireframe (default columns ↔ Columns toggle, 2,818 count, pagination all unchanged). Delta: imported MKT- rows get purple tint + `MKT` badge + PIC column value. | §3 `[L-4]` as "no-change contract" + MKT row-treatment delta; §4 settlement/volume separation rationale; §8 QA asserts MKT styling only (table itself not testable in wireframe — note). |
| **5** | Top-right Comments hub (💬 badge=unread count) — shared pattern [G-7]: @ Mentions tab, ★ Saved tab, full-text search (order no./author/text, newest first), click opens order, Mark all read. | §3 `[L-5]` cites [G-7], page deltas only (badge=3 mock, MKT- order ids appear in comments); §5 comment events; §6 Slack row. |
| **M1** | Marketing Order Import modal: 1. Download Template (.xlsx, dev-team standard: Recipient·Contact·Address·Country·SKU·Qty·Campaign) → 2. Order Type (Influencer Seeding preset chip / ✎ Custom free text) → 3. PIC (dropdown default = logged-in user / ✎ Custom free text, applies to entire import) → 4. Upload dropzone → Preview table → `Confirm Import (12 orders)`. | §3 `[L-M1]` step-by-step; §5 every step persisted; §7 parse-error / partial-connect cases (B leads, A lists capture needs). |
| **M1b** | `Carrier (auto)` preview column: on confirm each row's country gets its connected carrier auto-assigned (e.g., GB→YunExpress); unconnected country shows amber "Not connected — contact the Fulfillment Center" and does NOT block the batch (toast still fires, flagged count in toast small-text). Confirmed 2026-08-03. | §3 `[L-M1b]`; §4 rule + rationale; §5 per-row assignment event incl. not-connected outcome; §9 open question on downstream handling of carrier-less orders. |
| **M2** | Sample Assignment ON modal: Target = "All new orders in this period" / "Selected orders only (n)"; Period = start date+time ~ end date+time or `forever` checkbox; NO sample-type selection; note: overlapping periods allowed, exactly 1 sample set per order. Footer: Cancel / `Start Assignment (ON)`. | §3 `[L-M2]`; §4 [G-13] + exactly-1-set dedup; §5 period-created + per-order assignment events. |
| **M3** | Cancel Sample Assignment modal: table of periods (checkbox · period incl. `forever` · target · status Active/Ended). Ended = record-only, not cancellable. `Cancel Selected Periods` (red) → toast "Assignment period cancelled — new assignments stopped · already-assigned orders kept". | §3 `[L-M3]`; §4 keep-already-assigned rule; §5 cancellation event; §8 QA toast text assertion. |

Also global on this page (not legend-numbered, spec must cover): green top-right `gtoast` element ([G-2] — two instances wired: import confirm, period cancel), no-refresh behavior, annotation toggle (wireframe-only chrome, excluded from spec).

---

## 2. SECTION OUTLINES (10 template sections — concrete content)

**§1 Purpose & Users** — Order/marketing team screen (desk context, NOT scanner-in-hand — state explicitly: no scan surface, [G-1] not applicable, contrast with View Orders/Closing). Operational moments: (a) marketing ops bulk-imports seeding/giveaway orders ahead of warehouse inbound; (b) CRM/marketing toggles sample-set campaigns; (c) order team monitors mixed sales+MKT list. Users: order team, marketing (Harshit/EuJin-type PICs), admin. Physical-context note that DID shape decisions: warehouse picker downstream consumes the dual-view picking label — which is why sample info is split (G-13) and MKT rows are purple (visual sort at a glance).

**§2 Screen Inventory & Wireframe Map** — table: main dashboard state (1 state), 3 modals (M1/M2/M3), Comments dropdown (2 tabs + search state). Legend 1,2,3(removed),4,5 + M1/M1b/M2/M3 ↔ [L-n] 1:1. Live URL + how to open each modal (wf-bar buttons `Modal: Marketing Import` / `Modal: Sample Assignment ON` / `Modal: Cancel Sample Assignment`, and in-page Import / action-row buttons).

**§3 Functional Specification** — per [L-n] above. Key behaviors A will write: import 4-step flow with exact labels; Order Type chip toggle (custom input appears + focus); PIC custom toggle; preview row count + error count line ("12 rows parsed · 0 errors"); confirm → toast `✓ Confirmed — 12 orders imported` + small `Carrier auto-assigned per country · 1 not connected — flagged to contact Fulfillment Center`; MKT- order id prefix; orders appear immediately in RTO Marketing view regardless of stock; M2 target radio + period inputs + forever checkbox semantics; M3 selectable Active rows only; both toasts [G-2]; idempotency of Confirm Import and Cancel Selected Periods [G-9]. Unchanged features listed as contracts: Merge Orders, Columns, Export, Yun Export, filters (dates/Search/PIC/Status/Order#-Tracking# checkboxes/Country/page size), pagination, Select all.

**§4 Business Rules** (Lens A owns — full list with rationale + date):
- BR-1 **No stock validation on marketing import** (2026-07-23, user decision; Notion G stock-error item struck) — import may precede inbound; MKT orders always visible in RTO Marketing view regardless of stock/inbound. Rationale: seeding campaigns run ahead of warehouse arrivals.
- BR-2 **MKT separation** — purple tint + MKT badge + PIC on list rows; rationale: settlement & volume separation from sales orders (spec G).
- BR-3 **Carrier auto-assignment per country on confirm** (2026-08-03) — operator never picks carrier; unconnected country flags the row without blocking the batch; resolution path = contact Fulfillment Center (manual, no auto-Slack — see §9).
- BR-4 **PIC default = logged-in user, custom free text allowed** (2026-08-03); one PIC per entire import; shown in order list & RTO.
- BR-5 **Order Type = Influencer Seeding preset + custom** (2026-07-23) — free-text types allowed (e.g., "Pop-up event giveaway").
- BR-6 **Sample assignment is simple ON/OFF, no product-type selection** (2026-07-23 redesign; 2026-07-22 'removal' was stale and replaced within a day; 2026-08-03 존치 reconfirmed + Notion G corrected) — record the reversal chain verbatim in §10.
- BR-7 **Exactly 1 sample set per order even with overlapping periods** (2026-08-03) — dedup guard, no double assignment.
- BR-8 **Dual-view [G-13]** (2026-08-03) — carrier-facing data appends only "(+ sample set)" to last product name (tax reasons); internal invoice & picking label show WHICH sample and HOW MANY. Label layout itself deferred to Phase 3-1 — spec references behavior only.
- BR-9 **Cancel stops new assignments only; already-assigned orders kept; Ended periods are record-only** (wireframe M3 note) — protects in-flight picking from mid-stream changes.
- BR-10 **Bulk Hold removed from this page** (2026-08-03 review) — hold = Change Status (on-hold) on Order Detail; OMS dashboard stays the live screen.
- BR-11 **Order list table = no-change contract vs current admin** (2026-08-03) — including Columns toggle and pagination.
- Global cites: [G-2] toasts, [G-7] comments, [G-8] capture, [G-9] idempotency, [G-12] deep links (comment click → order), [G-13].

**§5 Data Capture** — full event enumeration below (Lens A deep inventory). Retention: import batches + source files retained for audit; comment history retained indefinitely (AI-training asset per [G-7]/[G-8]); all events exportable.

**§6 Integrations** — Slack table (1 confirmed row, below); cross-page: RTO Marketing view (MKT orders appear immediately), Order Detail (hold status change; comment deep link), shipping-label/invoice dual-view consumers; Export/Yun Export sheet handoffs unchanged. No Print button on this page — [G-4] applies only via downstream label pages (state explicitly to close the mandatory-item question).

**§7 Edge Cases** — A contributes capture-relevant cases (parse errors >0, duplicate file re-upload, unconnected-country rows, overlapping-period dedup, cancel of forever period, custom PIC not a system user); B owns exhaustive [E-n] list.

**§8 QA Acceptance Criteria** — A supplies the assertion targets (exact toast texts incl. small-text line, chip toggle behavior, M3 Ended row not selectable, badge count) — B owns Given/When/Then authoring.

**§9 Out of Scope & Open Questions** — Procurement Hub excluded (2026-08-02); label layouts Phase 3-1; order list column spec (unchanged contract); open questions listed below.

**§10 Decision Log** — dated: 07-22 sample removal (stale) → 07-23 ON/OFF redesign + import-no-stock-validation + M1 confirm; 08-03 carrier auto-assign + PIC custom + confirm toast + exactly-1-set + dual-view reconfirm + Notion G correction + Hold cleanup wording; 08-03 #fulfillment-admin-comments channel confirmed (ID C0BMGEWM5QA, user-created).

---

## 3. LENS-A DEEP INVENTORY

### 3a. Data Capture event list (per [G-8]: actor + timestamp + entity + old/new values; U = surfaced in UI, S = silent)

Import chain:
1. `mkt_template_downloaded` (S) — actor, ts, template version.
2. `mkt_import_file_uploaded` (S) — actor, ts, filename, size, row count, parse outcome (n parsed / n errors); persist even when preview abandoned.
3. `mkt_import_preview_generated` (S) — batch draft id, per-row parse result, per-row carrier resolution outcome (carrier | not-connected), error rows with reason.
4. `mkt_import_confirmed` (U: toast) — actor, ts, batch id, source filename, order count, order type (preset|custom + value), PIC (user-ref | custom text), counts: carriers assigned / not-connected.
5. `mkt_order_created` ×N (U: list rows) — per order: MKT- order no., recipient, country, SKU(s), qty, campaign, order type, PIC, batch id, carrier (or null + not_connected flag).
6. `carrier_auto_assigned` ×N (S, may fold into #5) — entity=order, old=null → new=carrier, rule source (country→carrier mapping version).
7. `mkt_import_abandoned` (S, optional — dev decides) — upload without confirm.

Sample assignment chain:
8. `sample_period_created` (U: M3 list row) — actor, ts, target type (`all_new_in_period` | `selected_orders` + order-id list + count), start dt, end dt | forever.
9. `sample_assigned_to_order` ×N (S — surfaced only downstream on internal invoice/picking label) — order id, period id, ts, sample-set ref.
10. `sample_assignment_deduped` (S) — order already has a set from an overlapping period → suppression recorded (proves BR-7 held; audit answer to "why only 1 set").
11. `sample_period_cancelled` (U: toast + M3 status) — actor, ts, period id(s), old status Active → new Cancelled/Ended; note: no unassignment events follow (already-assigned kept — assert absence).

Comments ([G-7], this page's instances):
12. `comment_posted` — actor, ts, entity (order no., incl. MKT-), text, @mentions[].
13. `comment_mention_notified` (S) — Slack delivery record: channel, ts, target user, success/fail.
14. `comment_read` / `comments_mark_all_read` — actor, ts, comment id(s) (badge is a view over this).
15. `comment_starred` / `comment_unstarred` — actor, ts, comment id.

Existing-screen actions (unchanged features still fall under [G-8]):
16. `orders_merged` — actor, ts, source order ids → merged result.
17. `orders_exported` / `yun_exported` (S) — actor, ts, filter context, row count (data-egress audit).
18. Explicit NON-captured list (state in spec so devs don't guess): filter changes, pagination, column toggle, comment search queries, modal open/close.

Total: **18 event types** (7 import + 4 sample + 4 comment + 2 existing-action + 1 explicit-exclusion clause).

### 3b. Operator-flow notes (field usability — where the wireframe encodes an operational decision)
- Desk screen, no scanner: [G-1]/[G-3] explicitly N/A — spec must say so to stop QA from testing scan focus here.
- Import-before-inbound (BR-1) exists because marketing timing beats warehouse timing; the operator must never be blocked by stock state; RTO Marketing view is the downstream pressure valve.
- Not-connected carrier row does not block the other 11 rows — batch keeps moving under speed pressure; the amber text IS the resolution instruction (contact Fulfillment Center), no modal dead-end.
- Toast + no refresh ([G-2]) — operator fires import and moves on; confirmation is glanceable top-right, small-text carries the exception count so failures aren't silent.
- Purple MKT rows: the order team scans the mixed list visually; settlement/volume separation happens at a glance, not via filter.
- PIC on the row = accountability channel: warehouse/CS knows who to ping (feeds comment @mention flow → Slack).
- Sample ON without product selection: removes a decision from the operator entirely; "which sample" lives elsewhere (see OQ-1 — genuine gap).
- Cancel keeps already-assigned: pickers mid-batch never see a sample disappear from a picking label they already printed.

---

## 4. MANDATORY-INCLUSION MAP (12 items → this page)

| # | Item | Lands here? | Where |
|---|---|---|---|
| 2 | Global toast [G-2] | YES | §3 [L-M1] confirm toast, [L-M3] cancel toast; QA exact texts |
| 5 | Sample dual-view + exactly-1-set [G-13] | YES — **primary home** | §3 [L-M2/M3], §4 BR-7/BR-8; label details deferred Phase 3-1 note in §9 |
| 12 | Comment @mention Slack routing [G-7] | YES | §5 events 12–15, §6 Slack row (#fulfillment-admin-comments — decision-sources' "pending owner" is superseded: CONFIRMED 2026-08-03, ID C0BMGEWM5QA) |
| 4 | Instant print [G-4] | Cross-ref only | §6 states no Print button on this page; dual-view consumed by label pages |
| 1,3,6,7,8,9,10,11 | Scanner / audio / unrecognized / multi-tracking / RTO KR / inventory items | NO | §1/§9 state N/A explicitly (prevents QA false negatives) |

## SLACK ROUTING ROWS THIS PAGE USES (all CONFIRMED in `_inputs/slack-routing.md`)

| Trigger | Channel | Payload | Mention |
|---|---|---|---|
| Comment @mention (this screen's Comments hub / order comments) | **#fulfillment-admin-comments** | order/entity no., comment text, time, author, @mentioned user, deep link | message body @mentions tagged person (personal notification + team-visible archive) |

No other confirmed row touches this page. Import-confirm / not-connected-carrier notifications = "future routes, decide per feature at dev time" per routing doc — not invented here (see OQ-D1).

---

## 5. OPEN QUESTIONS (flagged, not decided)

### Owner must decide
- **OQ-1**: Sample ON selects no product type — **where is "which sample and how many" configured**, and by whom (Fulfillment Center? admin setting?), so the internal invoice/picking label can render it? The wireframe defines the dual-view output but not the sample-set definition source.
- **OQ-2**: "All new orders in this period" with a start datetime in the past — does assignment apply **retroactively** to orders created between start and now, or only to orders created after ON is pressed?
- **OQ-3**: For target "Selected orders only", what does the **period** govern — immediate assignment to those orders (period informational), or scheduled/conditional assignment within the window?
- **OQ-4**: Confirmed import with a wrong file — is there a **batch revert/cancel path**, or is cleanup per-order (cancel each MKT order on Order Detail)?
- **OQ-5**: Rows flagged "Not connected — contact the Fulfillment Center": the order is still created — what is its downstream state in RTO (blocked from outbound until a carrier is connected/assigned manually? by whom?).

### Developer decides at build time
- OQ-D1: Whether import-confirm / not-connected events also post to a Slack channel (routing doc: future routes decided per feature at dev time).
- OQ-D2: Import idempotency key mechanics [G-9] (double-click on Confirm Import), duplicate-file re-upload detection, max row count, template versioning.
- OQ-D3: MKT- order numbering scheme/sequence source (wireframe shows MKT-40233 style).
- OQ-D4: Custom (free-text) PIC is not a system user — representation in PIC field and behavior when @mentioned/filtered (Search PIC).
- OQ-D5: Retention duration/location of uploaded xlsx source files and whether `mkt_import_abandoned` is logged.
