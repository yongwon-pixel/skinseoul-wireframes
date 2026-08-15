# Plan — Inventory (`stock-status`) — LENS A (Operator & Data)

Planner: A (field usability / data capture / business rules / Slack routing).
Wireframe SST: `wms2/stock-status/index.html` · live `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/stock-status/`
Screen renamed **"Stock Status" → "Inventory"** (2026-07-22). Default landing = Current Stocks.

---

## 1. LEGEND INVENTORY

This page's dots run **5–16** (no 1–4 on this page — numbering is page-local and starts at 5) plus **4 modal markers M1–M4**. Two modals carry no own dot: `m-auditlog` (Past Audit Logs list) is the body of legend 15; `m-adjlog6` (06-30 session detail) is a second instance of M2. **16 legend units total.**

| # | What it is | Spec treatment |
|---|---|---|
| 5 | New **Current Stocks tab, default landing**; filters: search, Location by **line (A/B/C… dynamically derived)**, Sourcing Route **incl. JIT** (2026-08-03) | §3 [L-5] tab + filter behavior; §4 BR (JIT residual, dynamic lines); mandatory items 9+11 |
| 6 | Click Reserved Qty → **allocated-orders modal (M3)**, marks **SUSPECTED PHANTOM** on cancelled/refunded orders with live reservations; per-row Cancel Inbound (M4) | §3 [L-6]+[M3]; §4 phantom definition; §5 reserve events |
| 7 | **Stock Audit mode** — start re-sorts **location ascending** (walking path), audit columns (Counted/Diff/Loss ₩) appear, bottom total loss (target 0), confirm opens M1; exit restores Available desc | §3 [L-7]; §4 BR sort/loss/gating; §5 audit events; §1 operator physical flow |
| 8 | Stock History Events — Type/Status badges, PENDING rows highlighted, filter chips All/Confirmed/Pending | §3 [L-8]; §5 (the table is a *view over persisted events* per [G-8]); OQ-2 (who confirms PENDING) |
| 9 | **History pagination** (fixes live screen's "pagination not implemented") | §3 [L-9]; page size = dev decision |
| 10 | Page rename → **Inventory**; legacy refs ("Export Stock Status") mapped during dev | §3 [L-10]; §4 BR naming; §9 note |
| 11 | Default sort = **Available descending**; header-click re-sort | §3 [L-11]; §4 BR |
| 12 | **Location = editable input on every row**; "Unassigned" (amber) rows listed for on-the-spot assignment; missing barcode → inline barcode input (same rule as View Orders) | §3 [L-12]; §5 silent events (location change, barcode registration — MUST persist) |
| 13 | **Add unregistered product** (audit mode only) — product-**name autocomplete** (barcode not required), Location+Qty → new row at top (system 0 → Diff +qty) → merged as ADJUST(+); not in catalog → Unrecognized flow (F) | §3 [L-13]; §5 audit.new_item; §6 cross-page link to tracking-missing |
| 14 | **Single location per SKU** (2026-07-22) — By Location card shows the one location; returns merge into same location (RETURN-BIN dropped) | §3 [L-14]; §4 BR-1 |
| 15 | **Past Audit Logs** modal — monthly sessions (date · auditor · adjustments · new additions · total loss, tracking to 0) + link to each session's ADJUST detail | §3 [L-15] (covers `m-auditlog`); §5 audit.session records; retention statement |
| 16 | Top-right **Comments hub** — shared across all screens, @Mentions + ★Saved + full-text search | §3 [L-16] cites [G-7], page deltas only; §6 Slack row |
| M1 | **Confirm Audit Differences** summary modal — ADJUST list, NEW additions, **Reserved-shortage gate** (confirm disabled), total loss, "Confirm — record N ADJUST events" | §3 [M1]; §4 gating BR; §5 audit.adjust.confirmed |
| M2 | **Audit session detail** — ADJUST event list per session (07-22 example; `m-adjlog6` = 06-30 example incl. loss-target-exceeded note) | §3 [M2]; §5 (view over ADJUST events; each also appears in that SKU's Stock History) |
| M3 | **Reserved Quantity** modal — Order ID/Date/Customer/Status/Reserved Qty/Reserved At/Action; phantom row highlighted; note links to Pending-confirm filter investigation | §3 [M3]; §6 deep link Order ID → order detail [G-12] |
| M4 | **Cancel Inbound (Release Reservation)** — 4-step: release? / Restock yes-no (no = ADJUST(−) loss) / Restock Qty (default = originally inbounded, editable) / optional Memo (dual-writes to order Comments) | §3 [M4]; §5 reserve.released + restock/adjust + comment dual-write |

Also present but not legend-numbered (spec must still cover): Export Stock Status (top-right), Export (Current Stocks toolbar), Inbound Form pane, Outbound Form pane (both live-screen carryovers per legend footnote), global nav.

---

## 2. SECTION OUTLINES (10 template sections)

**S1 Purpose & Users** — Warehouse staff: monthly stock audit walking lines A→C with count entry at the shelf (laptop/cart, speed pressure, product in hand); on-the-spot location assignment; Korean product-name column aids physical lookup [G-6]. Order team: Reserved/phantom investigation (Dean's report flow), PENDING inbound follow-up. Center manager/admin: loss target 0, monthly session review. Operational moments: (a) monthly stock-take, (b) SKU lookup during CS/order investigation, (c) manual in/outbound without an order (return restock, damage removal).

**S2 Screen Inventory & Wireframe Map** — 4 sub-tabs (Current Stocks default / Stock History / Inbound Stock / Outbound Stock) + 6 modals (M1 `m-adjust`, M2 `m-adjlog` & `m-adjlog6`, M3 `m-reserved`, M4 `m-resrelease`, `m-auditlog` [L-15]) + Comments hub [L-16]. Table maps each to legend # and wf-bar button used to reach it (wf-bar modal shortcuts open modal only, pane state intact — 2026-08-03).

**S3 Functional Specification** — per [L-n]/[M-n] as mapped above. Concrete items to write: Start/Exit Stock Audit toggle (label swap, column show/hide, re-sort both directions, summary bar visibility); filter chips behavior; Counted Qty input prefill = system qty (per wireframe — see OQ-1); Diff/Loss auto-calc (Loss = Diff × product cost, cost source dev-time per 2026-07-22); [L-13] add flow incl. "No match → register manually via Unrecognized flow (F)" dropdown row; [L-12] location/barcode input commit semantics (Enter/blur + toast [G-2], no refresh); M4 radio + qty + memo validation; M1 confirm button exact label "Confirm — record N ADJUST events"; Record Inbound (green) / Record Outbound (blue) with location auto-apply from SKU's single location and Available-exceeded block; Export buttons; Search bar (key select SKU/Product Name/Order ID/Tracking No). Idempotency on all confirming buttons [G-9].

**S4 Business Rules** — see §"Business rules" list below (BR-1..BR-16 with dates/rationale).

**S5 Data Capture** — the 23-event enumeration below, split UI-logged vs silent, each with actor/timestamp/entity/old-new. Retention: Stock History and audit sessions retained indefinitely (wireframe shows 3+ months of sessions); export expectations stated.

**S6 Integrations** — Slack routing rows used by this page (below); deep links: M3 Order ID → order detail [G-12]; PENDING inbound ↔ View Orders State 6 (internal inbound); [L-13] no-match → `../tracking-missing/` flow F; Sourcing Route origin = Inbound Request [G-5]. Print pipeline: **N/A — no Print button on this page** (Export only; [G-4] does not land here). Sheet/BI: Export file only; no live sheet handoff specced.

**S7 Edge Cases** — Lens B owns; my operator-side candidates handed over: mid-audit stock movement (outbound confirmed while counting), concurrent audit sessions, counted < Reserved gate path, two SKUs claiming one location (one-location-per-SKU is not one-SKU-per-location — clarify), invalid location format, audit-mode exit with unsaved counts, JIT row audited, Unassigned-location row in audit walking sort (sorts last — wireframe uses U+D7A3 sentinel), duplicate Record Inbound double-click [G-9 known bug].

**S8 QA Acceptance Criteria** — Lens B owns counts; my contribution: every event in §5 gets at least one G/W/T asserting (toast appears [G-2]) AND (history/log row materializes without page refresh) AND (old/new values correct) — e.g., audit confirm writes exactly N ADJUST rows visible via SKU search + type filter.

**S9 Out of Scope & Open Questions** — Order-linked inbound (lives in View Orders/order detail — form note says so); label printing; photo upload (deferred 2026-07-21); Procurement Hub (excluded 2026-08-02); open questions per §5 below.

**S10 Decision Log** — 2026-07-09 initial rework from live captures (E); 2026-07-22 rename to Inventory · single location per SKU/RETURN-BIN dropped · Loss = Diff × cost design confirmed (cost source dev-time); 2026-08-03 JIT included in Sourcing Route filter · line filter dynamic derivation · audit-summary visible only in audit mode · global toast emphasis [G-2] · #fulfillment-admin-comments confirmed · wf-bar modal shortcut behavior.

---

## 3. LENS-A DEEP INVENTORY

### 3a. Data Capture — full event list (per [G-8]: actor + timestamp + entity + old/new values; UI logs are views over persisted events, never the only copy)

**UI-surfaced events** (rendered in Stock History table / audit modals / comments hub):

| ID | Event | Actor | Entity | Old → New / payload |
|---|---|---|---|---|
| DC-1 | `stock.inbound.recorded` (Inbound Form) | operator | SKU | total qty before→after; +qty, tracking no?, carrier, order id?, location (auto), status CONFIRMED\|PENDING |
| DC-2 | `stock.outbound.recorded` (Outbound Form) | operator | SKU | total before→after; −qty, tracking no?, carrier, order id?; rejected if qty > Available (rejection itself logged, see DC-20) |
| DC-3 | `stock.reserved` (order allocation) | System | SKU + order id | reserved before→after; −qty to Available |
| DC-4 | `stock.reserve.released` (M4 step 1) | operator | SKU + order id | reserved before→after (e.g. 8→5); release reason implicit (phantom), memo id link |
| DC-5 | `stock.restocked` (M4 restock=Yes) | operator | SKU | available before→after (34→37); restock qty (default = originally-inbounded qty, editable — capture both default and entered value) |
| DC-6 | `stock.adjust.loss` (M4 restock=No) | operator | SKU | ADJUST(−n), classification damaged/lost, loss amount |
| DC-7 | `audit.session.started` | auditor | audit session | session id, start ts, row count in scope, sort switched to location asc |
| DC-8 | `audit.adjust.confirmed` (per SKU, Diff≠0, from M1) | auditor | SKU + session id | system qty → counted qty, diff, loss = diff × product cost; writes ADJUST row into that SKU's Stock History |
| DC-9 | `audit.new_item.added` ([L-13]) | auditor | SKU + session id | system 0 → counted n; location; flagged NEW ADDITION; loss excluded from total |
| DC-10 | `audit.session.confirmed` | auditor | audit session | audit date, auditor, SKUs checked, adjustments count (±breakdown), new additions, total loss, confirm ts — the Past Audit Logs row |
| DC-11 | `comment.posted` (incl. M4 memo dual-write into the order's Comments history) | author | order/entity | text, ts; source=manual\|m4-memo |
| DC-12 | `comment.mention.notified` | System | comment id | Slack channel, mentioned user, delivery ts (see §6) |

**Silent events** (no current UI surface — must still persist per [G-8]):

| ID | Event | Actor | Entity | Old → New / payload |
|---|---|---|---|---|
| DC-13 | `location.changed` ([L-12] loc-in edit) | operator | SKU | old location → new location, ts. **Biggest silent-capture gap on this page — nothing in Stock History shows location moves today; spec must mandate persistence (and recommend a LOCATION type or event attribute for later surfacing)** |
| DC-14 | `location.assigned` (Unassigned → first value) | operator | SKU | null → location (subtype of DC-13) |
| DC-15 | `barcode.registered` ([L-12] bcin) | operator | SKU | null → barcode value, ts (same rule as View Orders — cross-page event name must match) |
| DC-16 | `inbound.pending.confirmed` | operator | history event id | status PENDING → CONFIRMED, ts, actor (mechanism unresolved — OQ-2) |
| DC-17 | `audit.session.abandoned` (Exit without confirm) | auditor | session id | entered counts snapshot? (draft retention = dev decision), abandon ts |
| DC-18 | `audit.blocked.reserved_shortage` (M1 gate fired) | System | session id + SKUs | counted < reserved list, block ts — operational signal for phantom hunting |
| DC-19 | `export.generated` (both Export buttons) | operator | export | which export, filter state, row count, ts — who took stock data out |
| DC-20 | `stock.outbound.rejected` (Available exceeded) | operator | SKU | attempted qty vs Available, ts — repeated rejections signal count drift |
| DC-21 | `search.executed` (Stock History search) | operator | query | key type + term, ts (doctrine-default yes; low-signal — dev may sample) |
| DC-22 | `comment.starred` / `unstarred` | user | comment id | per-user saved state, ts |
| DC-23 | `comment.read` / mark-all-read | user | comment ids | per-user read state (badge count derives from this) |

Retention/export: DC-1..10 retained indefinitely (audit trail + AI-training doctrine); monthly sessions never pruned (wireframe shows May–Jul); exports reproduce current filter view; all events exportable to BI on request.

### 3b. Operator-flow notes (field usability — wireframe-encoded operational decisions)

1. **Walking-path sort** [L-7]: audit re-sort location-ascending exists so the auditor walks A-01→C-xx once. Spec must require count entry order = physical shelf order and Enter/Tab advancing focus to the next row's Counted Qty — no mouse between shelves.
2. **Counted Qty prefill = system qty** (wireframe prefills 88/61/…): fastest for "matches" (tab-through) but invites confirmation bias — auditor may confirm without counting. Wireframe is SST; flagged as OQ-1, not overridden.
3. **No-refresh is load-bearing in audit mode** [G-2]: dozens of counted values live in the DOM before confirm. Any refresh loses the session — spec must state counts survive until Confirm/Exit, and recommend draft autosave (dev, DC-17).
4. **[L-13] name autocomplete, barcode not required**: deliberate — unregistered items found on a shelf often have no scannable/known barcode. Search by Korean name + verify size before select (size shown in dropdown to disambiguate 150ml vs 320ml).
5. **On-the-spot location assignment** [L-12]: Unassigned rows are listed (not hidden) precisely so staff standing at the shelf can fix them; input commit must be blur/Enter + toast, tolerant of scanner-gun keyboard wedge input.
6. **Reserved-shortage gate** [M1] is an at-the-shelf stop: confirm disabled until the order team reviews affected orders — spec must state what the auditor physically does (leave audit open? partial confirm?) → hand to Lens B as edge case, policy in OQ-5.
7. **Audio**: page delta on [G-3](a) — "Record Outbound" is an outbound-class button → plays the send sound. No TTS on this page (Closing-only).
8. **Loss ₩ on the shelf floor**: cost data (₩15,000/unit etc.) is visible in audit mode to warehouse staff — flagged OQ-4.
9. **Lookup with product in hand**: Stock History search keys are SKU/Name/Order ID/Tracking No — no Barcode key, so an operator holding a product cannot scan-to-lookup. Flagged OQ-3.

---

## 4. MANDATORY-INCLUSION MAP (of the 12)

| # | Item | Lands here? | Where |
|---|---|---|---|
| 2 | Confirmation toast [G-2] | Yes (all screens) | §3 every confirming button; §8 every scenario asserts toast |
| 3 | Audio [G-3] | Delta only | §3 Record Outbound = send sound; no TTS |
| 9 | Line-based location filter, dynamic lines [G-14] | **Yes — primary home** | §3 [L-5], §4 BR-5 |
| 10 | Audit-mode-only summary visibility [G-14] | **Yes — primary home** | §3 [L-7], §4 BR-4 |
| 11 | JIT residual stock in Inventory | **Yes — primary home** | §3 [L-5], §4 BR-6 (cancellations · mis-delivery returns, 2026-08-03) |
| 12 | Comment @mention Slack routing [G-7] | Yes (all screens) | §6 routing table — channel CONFIRMED |
| 1/4/5/6/7/8 | Scanner / print / sample / unrecognized-matching / multi-tracking / RTO-KR | No (other pages) | §9 notes: no Print button here (G-4 N/A); [L-13] no-match hands off to Unrecognized flow (F) but matching behavior itself is specced on tracking-missing/view-orders |

## Slack routing rows this page uses (channels CONFIRMED 2026-08-03)

| Trigger | Channel | Payload | Note |
|---|---|---|---|
| Comment @mention (Comments hub, M4 memo containing @mention, audit-related comments) | **#fulfillment-admin-comments** | order/entity no., comment text, time, author, @mentioned user, deep link | Message body @mentions the tagged person → Slack personal notification; channel doubles as team-visible archive |
| M4 memo without @mention | (no Slack) | recorded to order Comments history only | dual-write DC-11 |
| Audit session confirmed → notify? | not confirmed | — | "future routes: decide per feature at dev time" (slack-routing.md last row) — listed in §9, NOT specced |

(#unrecognized-tracking, #wholesale-ops, #partnership-kr rows belong to other pages — not used here.)

## Business rules (§4 content, with rationale + dates)

BR-1 Single location per SKU; returns merge into same location, RETURN-BIN dropped (2026-07-22 — simpler physical truth, one place to look). BR-2 ADJUST = book correction, never Inbound/Outbound (keeps logistics history clean — M1 copy). BR-3 Loss = Diff × product cost, session total targets 0 = center-manager KPI (design 2026-07-22; cost source dev-time: FIFO lot cost recommended vs latest purchase). BR-4 Audit-only UI hidden outside audit mode [G-14] (2026-08-03). BR-5 Line list dynamically derived from registered locations [G-14] (2026-08-03 — no hardcoded lines). BR-6 JIT residual stock listed + filterable (2026-08-03 — cancellations/mis-delivery leave JIT stock behind). BR-7 Reserved-shortage gate blocks audit confirm. BR-8 Outbound > Available blocked. BR-9 Sort: Available desc default / location asc in audit (walking path, Notion E). BR-10 M4 restock qty default = originally-inbounded qty, editable. BR-11 Rename → Inventory, legacy refs mapped in dev (2026-07-22). BR-12 Sourcing routes exactly 4, colorless black bold [G-5]. BR-13 Audit-add by name autocomplete, barcode not required; not-in-catalog → Unrecognized flow (F). BR-14 Idempotency on all confirming actions [G-9]. BR-15 No-refresh, toast on every confirming action [G-2]. BR-16 Suspected phantom = order cancelled/refunded with unreleased reservation → release target.

---

## 5. OPEN QUESTIONS

**Owner must decide:**
- OQ-1: Counted Qty prefill — wireframe prefills the system qty (fast, but auditors can tab through without counting). Keep prefill, or blank-by-default to force blind counts? (accuracy vs speed; wireframe currently encodes prefill)
- OQ-2: Who/where confirms a PENDING inbound event (e.g., Coupang +6, Miranti's comment "Please confirm")? No confirm control exists on this page — is confirmation a Stock History row action here, or does it only resolve via View Orders State 6 scan? Blocks functional spec of [L-8].
- OQ-3: Add "Barcode" as a Stock History search key? Operator holding a physical product cannot scan-to-lookup today (keys: SKU/Name/Order ID/Tracking No).
- OQ-4: Is the Loss (₩) column / product cost visible to all warehouse staff in audit mode, or admin-only? (cost exposure on the floor)
- OQ-5: Audit session concurrency policy — exactly one active session with a single auditor of record (wireframe implies one auditor/session), or multiple operators counting in parallel? Determines DC-7/DC-8 actor model and the Reserved-shortage-gate workflow (who reviews while the auditor waits).

**Developer decides at build time:**
- Product cost source for Loss: FIFO lot cost (recommended, Procurement Hub FIFO COGS link) vs latest purchase price — explicitly deferred 2026-07-22.
- Stock History pagination page size/mechanism [L-9].
- Location format validation/normalization + line-derivation implementation (BR-5); Unassigned sort position.
- Draft autosave of in-progress audit counts (DC-17 crash recovery).
- Export file format/columns; whether DC-19/DC-21 (export/search logging) are full-fidelity or sampled (doctrine default: capture).
- Legacy "Export Stock Status" naming mapping [L-10].
- Idempotency key mechanics for Record Inbound/Outbound/M1/M4 confirms [G-9].
