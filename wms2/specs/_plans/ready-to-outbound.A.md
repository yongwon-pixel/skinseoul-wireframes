# PLAN — Ready to be Outbounded (`ready-to-outbound`) — LENS A (Operator & Data)

Planner A of 2. Lens: field usability (operator flow), Data Capture [G-8], business rules with dates, Slack routing. Wireframe SST: `wms2/ready-to-outbound/index.html` (live: `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/ready-to-outbound/`).

---

## 1. LEGEND INVENTORY (14 numbered + M1 = 15 units; legend renders in order 1–8, 14, 13, 12, 9, 10, 11)

| # | What it is | Spec treatment |
|---|---|---|
| 1 | Per-row checkboxes + Select all; the 3 bulk buttons display selected order count AND item count | §3 [L-1]: selection model, count computation (orders vs units), enabled/disabled states of bulk buttons at 0 selected; §5: selection set embedded in every bulk event payload (no per-toggle logging) |
| 2 | Print Pick Locations button → opens Picking List modal (M1); print → progress → toast | §3 [L-2]: trigger, count label source, modal open; §5 DC-5; §6 print pipeline [G-4] |
| 3 | Bulk Print Labels — prints shipping labels for all selected orders in one go | §3 [L-3]: carrier-agnostic per-order label dispatch [G-4], no refresh + selection kept; §5 DC-6; §4 reprint rule |
| 4 | Bulk Outbound — outbounds selected orders; **refreshes after completion (sole [G-2] exception) + send sound (2026-08-03) [G-3a]** | §3 [L-4]: status transition, stock decrement, idempotency [G-9]; §5 DC-8/9/10; §4 BR |
| 5 | 0–100% progress bar **shared by all 3 bulk buttons**; print = no refresh + selection kept, outbound = refresh after | §3 [L-5]: progress semantics, which action owns the bar, concurrent-click lockout; §7 (B) mid-batch failure |
| 6 | Completion notice = top-right toast, auto-dismiss; **no failure case (all-success is normal behavior)** | §3 [L-6] per [G-2]; §4 BR (failure-case removal 2026-07-22); §9 open question Q2 (server-side partial failure vs all-success UI) |
| 7 | JIT order fully inbounded but Outbound not clicked = yellow tint + **"Fully Inbounded" badge** (renamed 2026-08-03 from "JIT (channel) completed" to avoid clash with colorless Sourcing Route labels [G-5]); always sorted to bottom | §3 [L-7]: badge condition, sort rule; §4 BR with both dates; §5 DC-15 |
| 8 | Manually imported Marketing order = purple tint + MKT badge; sorted between regular Ready and JIT; **always shown immediately on import regardless of stock/inbound status** (not-inbounded items show amber "Not inbounded" pill instead of a location); shows PIC | §3 [L-8]; §4 BR (2026-07-23 stock-error validation dropped); §5 DC-14; §9 Q1 (bulk-outbound eligibility) |
| 9 | Per-row Comments button → inline comment panel under the row (no page navigation); @mention → automatic Slack notification | §3 [L-9] per [G-7]; §5 DC-1/2; §6 Slack row (#fulfillment-admin-comments) |
| 10 | Top-right Comments hub — @ Mentions / ★ Saved tabs + full-text search across ALL comments (order no./author/text, newest first), unread badge, click opens order | §3 [L-10] per [G-7] (deltas only); §5 DC-3/4 (+DC-17 flag for search telemetry) |
| 11 | Reduced side padding — full-width layout (same principle as View Orders) | §3 [L-11] one-liner (cosmetic, ref C/D); no data events |
| 12 | **New Pick Locations column** — per-item locations listed vertically at same eye level as Ready Item Details (warehouse stock = location code; fully-inbounded JIT = shelf number e.g. "Shelf 3"; MKT not-inbounded = amber pill). Ready Items column removed as duplicate of Total Items | §3 [L-12]: rendering rules per row type; §4 BR (one-location-per-SKU [G-14] consumed here) |
| 13 | Total Items = **total quantity sum** (old admin counted SKUs, so a ×5 order read "1" → picking error source; now shows actual units, e.g. 5 for order 422221) | §3 [L-13]; §4 BR with rationale (operator counts units, not SKUs) |
| 14 | View tabs — All (default) / Inventory / Marketing / JIT; filters by order type, linked to the "Found N order(s)" count | §3 [L-14]: filter semantics, count binding, interaction with selection (§9 D5); §5 DC-17 flag |
| M1 | Picking List modal — aggregated pick table (Location / SKU / Product [Korean, G-6] / Qty / Order), **sorted by location ascending** for a one-pass route; header shows orders · SKUs · units; Cancel / Print | §3 [L-M1]: aggregation rules (same SKU across orders = separate rows keyed by order? spec must fix), sort, print pipeline [G-4]; §5 DC-5 snapshot |

Non-legend base elements to spec in §3 anyway: Refresh button; "Found N order(s)…" line; How to use block (Ready definition = ≥1 INBOUNDED line item; dedicated `readyToBeOutbonded` API); Order ID link → order-detail; per-row Print button (🖨, instant [G-4]); page title spelling "Ready to be Outbonded" preserved from the actual admin; footnote sort order regular → MKT → JIT; Actions column simplified to Print only (2026-07-22, View Order button removed).

---

## 2. SECTION OUTLINES (10 template sections)

1. **Purpose & Users** — Morning outbound wave for the order team + warehouse pickers/packers. Two personas: (a) desk operator who selects orders and fires the 3 bulk actions, (b) picker who walks the printed picking list route (paper in hand, away from monitor — this is why: Korean names [G-6], location-ascending sort, unit-sum Total Items [13], instant print [G-4], sound on outbound [G-3a]). Physical context sentence per template.
2. **Screen Inventory & Wireframe Map** — 1 main state + M1 modal + Comments hub dropdown + inline comment rows (crow1–5) + 4 view-tab states. Table: legend # ↔ §3 key ↔ how to reach (top wf-bar "Modal: Print Pick Locations" button; bulk buttons run the progress demo; view tabs filter live).
3. **Functional Spec** — Per legend item as in §1 above. Extra precision items Lens A will supply: selection→count recomputation on every toggle/tab; bulk button labels update with counts; the demo behaviors that ARE the spec (progress → toast text "✓ {action} complete — N orders"; sound on Outbound-class buttons only, Cancel excluded); per-row Print = single-order label reprint path.
4. **Business Rules** (Lens A owns; each with rationale + date):
   - BR-1 Ready definition: order appears when ≥1 line item is INBOUNDED; source = dedicated readyToBeOutbonded API (actual admin, captured 2026-07-21).
   - BR-2 Sort order: regular Ready → MKT → fully-inbounded JIT, JIT always bottom — keeps warehouse-stock picking separate from staged JIT shelf goods (2026-07-22 rework).
   - BR-3 MKT orders visible immediately on import regardless of stock/inbound; stock-error validation on import explicitly dropped (2026-07-23 owner decision, Notion G struck through; import-first-inbound-later allowed).
   - BR-4 JIT badge wording "Fully Inbounded" (2026-08-03 rename; was the last open judgment item #11 of the 17-item review — resolved).
   - BR-5 Total Items = unit sum, not SKU count (D picking; ×5 misread as "1" caused under-picking).
   - BR-6 Korean product names in Ready Item Details + M1 picking list; EN+bold-brand stays on order pages [G-6] (2026-08-03).
   - BR-7 Picking list sorted by location ascending — single pass along the route (D, 2026-07-22).
   - BR-8 Print actions never refresh and keep selection; Bulk Outbound refreshes after completion — the one designed [G-2] exception (2026-07-22/2026-08-03).
   - BR-9 No failure case in bulk UI — all-success is the normal path (failure states removed 2026-07-22).
   - BR-10 Instant print, no browser dialog, any carrier [G-4] (2026-08-03 reconfirmed, local print agent per handoff note B).
   - BR-11 Outbound-class buttons play send sound [G-3a] (2026-08-03).
   - BR-12 Actions column = Print only; details via Order ID link (2026-07-22).
   - BR-13 Double-click safety on Bulk Outbound / prints [G-9] (known current bug, handoff note A, 2026-07-21).
   - BR-14 Base structure/columns/title spelling follow the actual admin capture 2026-07-21; only Ready Items removed, Pick Locations added.
5. **Data Capture** — the full event table from §3-A below (owner-priority section; doctrine [G-8]: if staff did it, admin recorded it; UI logs are views over persisted events). Retention: indefinite (AI-training asset per [G-7]); export: picking-list snapshots reproducible per batch; outbound events feed Stock History (Outbound tab) and Closing counts.
6. **Integrations** — Slack table (§3-A routing below, 1 confirmed row); cross-page links: Order ID → `../order-detail/`, Comments-hub click → order, outbounded orders become the Closing scan population (cross-ref closing spec), stock decrement → stock-status Outbound history; print pipeline: local print agent, carrier-agnostic [G-4], PrintNode-class per handoff note.
7. **Edge Cases** — Lens B owns; Lens A contributes operator-driven candidates: MKT not-inbounded row in a bulk selection; JIT row in Select all; outbound of an order whose item was concurrently cancelled/inbound-cancelled on View Orders; printer/agent offline mid-batch [G-4]; double-click [G-9]; empty pool ("Found 0"); comment posted while another operator outbounds the row.
8. **QA Acceptance** — Lens B owns; Lens A supplies data-capture assertions: after each bulk run, assert persisted event exists with actor/ts/order set (in real admin); on wireframe, assert toast text, progress label mode string ("No refresh · selection kept" vs "refreshes after completion"), sound handler binding on Outbound buttons only, view-tab Found-count updates.
9. **Out of Scope / Open Questions** — label layout content (Phase 3-1, per decision-sources); scanner protocol [G-1] N/A (no scan surface on RTO); import template spec (dev team, per handoff note G); + questions in §5 below.
10. **Decision Log** — dated entries: 2026-07-21 actual-admin capture base + double-click bug to handoff; 2026-07-22 full rework (5 rows, sort order, Total Items=sum, Pick Locations col, ascending picking modal, progress+toast, failure cases removed, Actions→Print only); 2026-07-23 MKT import stock-validation dropped; 2026-08-03 Korean item names + footnote, "Fully Inbounded" badge rename, outbound send sound, instant-print reconfirm, toast doctrine [G-2], #fulfillment-admin-comments confirmed.

---

## 3-A. LENS-A DEEP INVENTORY

### Data Capture event list (18 entries: 16 mandatory + 2 dev-flagged) — each with actor · timestamp · entity · old/new
| ID | Event | Actor | Entity | Old → New / payload | UI or silent |
|---|---|---|---|---|---|
| DC-1 | comment_posted | operator | order | text, mentions[], source=RTO inline panel or hub | UI (comment history) |
| DC-2 | comment_mention_slack_delivered | system | comment | channel=#fulfillment-admin-comments, slack ts, mentioned user, delivery result | silent |
| DC-3 | comment_star_toggled | operator | comment | saved false↔true | UI (★ Saved tab) |
| DC-4 | mention_read / mark_all_read | operator | comment(s) | unread→read | UI (badge count) |
| DC-5 | picking_list_printed | operator | batch | batch id, order ids[], full line snapshot {location, sku, name_kr, qty, order}, totals {3 orders · 4 SKUs · 8 units}, sort=loc-asc | UI (toast) + snapshot silent |
| DC-6 | bulk_labels_printed | operator | batch + per order | order ids[], per-order carrier, label id, reprint_count old→new | UI (toast) |
| DC-7 | single_label_printed (row 🖨) | operator | order | same as DC-6, source=row | UI |
| DC-8 | bulk_outbound_batch | operator | batch | order ids[], started/finished ts, per-order result refs | UI (progress+toast+sound) |
| DC-9 | order_outbounded | operator | order | status READY/INBOUNDED→OUTBOUNDED, line items [sku, qty, location] | UI (row leaves list after refresh) |
| DC-10 | stock_decrement | system | SKU@location | qty old→new, ref=DC-9 | silent (feeds Stock History Outbound) |
| DC-11 | idempotency_duplicate_rejected | operator | action+key | rejected attempt recorded [G-9] | silent |
| DC-12 | print_job_lifecycle | system | print job | queued→sent→done/failed, agent id, printer [G-4] | silent |
| DC-13 | order_ready_at | system | order | entered RTO pool ts (enables ready→outbound dwell-time metric) | silent |
| DC-14 | mkt_order_surfaced | system | order | import ref (OM screen), RTO-visible ts, PIC | silent (import itself logged on OM) |
| DC-15 | jit_fully_inbounded_at | system | order | last item inbounded ts → badge shown | silent |
| DC-16 | batch per-order result | system | batch item | success/fail per order — persisted even though UI shows no failure case | silent (see Q2) |
| DC-17 | (flag) read-only telemetry: view-tab switch, comment search, Refresh click, modal cancel | operator | — | analytics only, not [G-8] state changes | dev decides (D1) |
| DC-18 | (rule) selection set embedded in every bulk event payload; individual checkbox toggles NOT logged | — | — | — | spec statement |

### Operator-flow notes (field usability)
1. Flow is a 3-beat morning wave on ONE selection: select → Print Pick Locations (paper to picker) → Bulk Print Labels (labels to packer) → Bulk Outbound (close the wave). Selection persistence across the two print steps is load-bearing — spec must state selection survives prints and dies only on the outbound refresh.
2. Picker is away from the monitor: Korean names (faster shelf reading), location-ascending single-pass route, unit-sum quantities, bold qty ("5") on multi-unit lines — every one exists to prevent under-picking; spec ties each to its rationale.
3. Instant print [G-4]: operator stands at the printer station; a browser dialog = broken cadence. Per-row 🖨 is the reprint path when a label is damaged (demo comment "Reprinted the shipping label" shows the practice — reprint is an event DC-6/7, not an auto-comment).
4. Eyes-free confirmation: toast [G-2] + send sound [G-3a] on outbound; progress bar is the single shared indicator — spec must forbid firing a second bulk action while one runs.
5. Sort order = route logic: warehouse rows first (rack locations), MKT next (mixed/not-inbounded), JIT last (shelf-staged, no rack walk). Pick Locations column shows the right locator per type (rack code / "Shelf N" / amber "Not inbounded").
6. Comments inline expansion lets the packer read a VIP/care note without leaving the table; @mention pulls absent teammates in via Slack.
7. Total Items badge is the desk operator's sanity check against the picking modal header (orders · SKUs · units) — numbers must reconcile; QA assertion candidate.

### Slack routing rows used by this page (channels CONFIRMED, `_inputs/slack-routing.md` 2026-08-03)
| Trigger | Channel | Payload | Mention |
|---|---|---|---|
| Comment @mention (inline panel [9] or hub [10]) | **#fulfillment-admin-comments** (ID C0BMGEWM5QA; body @mentions the tagged person → personal notification; channel doubles as team-visible archive) | order no., comment text, time, author, @mentioned user, deep link to order | mentioned user |
No other routes originate on RTO (unrecognized/morning-check routes belong to tracking-missing and inbound-request). Future routes: per-feature at dev time per routing doc.

---

## 4. MANDATORY-INCLUSION MAP (of the 12)
- **#2 [G-2] toast** → §3 [L-6] + every confirming action; Bulk Outbound refresh documented as the designed exception.
- **#3 [G-3a] send sound** → §3 [L-4] (Outbound-class buttons only; Cancel/“Outbounded” excluded per wireframe binding).
- **#4 [G-4] instant print** → §3 [L-2]/[L-3]/[L-M1]/per-row Print; §6 print pipeline.
- **#8 [G-6] RTO Korean item names** → §3 [L-12 area]/[L-M1] + BR-6.
- **#12 [G-7] comment @mention routing with named channel** → §3 [L-9]/[L-10] + §6 table (channel now CONFIRMED — spec cites #fulfillment-admin-comments, superseding "pending" note in decision-sources).
- **#5 [G-13] sample dual-view** → cross-reference only: internal picking artifacts show which sample/how many; M1 currently shows no sample lines → raised as Q3; label layout deferred to Phase 3-1.
- Not on this page: #1 [G-1] (no scan surface — state N/A explicitly), #6, #7 [G-10], #9/#10 [G-14] (except one-location-per-SKU consumed by Pick Locations), #11.

---

## 5. OPEN QUESTIONS (do not invent — flag)

**Owner must decide:**
- Q1: Can a Marketing order with "Not inbounded" items be included in Bulk Outbound / Select all, or is it blocked (excluded, error, or partial outbound of inbounded lines only)? Wireframe shows MKT+JIT rows unchecked and "Only items marked as INBOUNDED are ready" — the always-visible MKT rule [8] leaves the gating ambiguous.
- Q2: "No failure case" [6] is a UI promise — when the server hits a real per-order failure mid-batch (concurrent cancel, print agent offline), does the UI stay all-success with silent logging (DC-16), or is a failure surface allowed? This changes the owner's all-success doctrine, so it is not a dev call.
- Q3: Should the M1 Picking List include sample-set lines (G-13 internal view: WHICH sample, HOW MANY)? Modal currently lists products only. (Content question only — label layouts stay in Phase 3-1.)
- Q4: Are JIT "Fully Inbounded" rows meant to be outbounded via Bulk Outbound here, or individually from the order page (their final-Outbound-not-clicked framing suggests a deliberate manual step)?
- Q5: Is there an intended sequence gate between the 3 bulk actions (e.g., Outbound allowed only after labels printed), or are they fully independent?

**Developer decides at build time:**
- D1: Whether read-only telemetry (DC-17: tab switch, search, Refresh, modal cancel) is logged — [G-8] does not require it.
- D2: Batch chunk size and progress granularity (per-order vs percent) for the shared progress bar.
- D3: Idempotency key scheme (per batch vs per order) [G-9].
- D4: Print-agent job polling/retry mechanics and queue naming [G-4].
- D5: Default checkbox state on load and whether selection survives a view-tab switch (demo shows 3 Inventory rows pre-checked — treat as illustrative unless owner says otherwise).
- D6: readyToBeOutbonded API refresh cadence (manual Refresh only vs background poll).
- D7: Whether a label reprint auto-posts a comment or is event-only (demo shows a manual comment; recommend event-only).
