# PLAN — inbound-request (LENS A: Operator & Data)

Planner A of 2. Sources read: spec-template.md, global-rules-draft.md, slack-routing.md, decision-sources.md, full wireframe `wms2/inbound-request/index.html` (v1, 851 lines, 3 states + 1 modal + 1 removed modal), decision ledgers 2026-07-09 + 2026-08-02.

Page identity: the **single intake gateway for everything entering the warehouse** (legend S1-1). No scan surface, no print button, no audio on this page — the desk-side half of the inbound loop; the warehouse half lives in View Orders State 6. Primary owner of mandatory item #7 (multi-tracking [G-10]).

---

## 1. LEGEND INVENTORY (28 numbered items + 2 un-numbered footer rule blocks)

Notation: `S{state}-{n}` / `M1`. Spec keys `[L-S1-2]` style. Every item lands in §3 Functional; extra target sections noted. NOTE: State 1 has **no dot 13** (renumbered 2026-08-03, judgment item 14) — the spec's §2 map must state this so coverage checks don't flag a phantom gap.

### State 1 — New Request, Smart Buy (15 dots: 1–12, 14–16)
- **S1-1** New Inbound Request screen = single intake gateway (Smart Buy restock + Wholesale + Partnership + Other all requested here). → §1 + §3 + §4 (BR-1).
- **S1-2** Sourcing route selection — 4 radio cards: Smart Buy / Wholesale / Brand Partnership / **Other with free-text channel name** (enabled+focused on select, per script). Badge styling = View Orders convention (black bold, no colors) [G-5]. → §3 + §4 (BR-2; G-5 delta/tension — see Open Q O-4) + §5 (route stored on request).
- **S1-3** **Inbound No. auto-assigned, no input or preview** (panel removed 2026-07-26) — YYYYMMDDNNNN, NNNN 0001–9999 per day, shown only in Request List; maps to PH sheet column A "PO No. (=Order ID)". → §3 + §4 (BR-3) + §5 (DC-2 silent allocation event).
- **S1-4** Field set aligned to PH sheet column order (Inbound No → Channel → SKU → Brand → Product Name → Order Qty → Unit Cost → JIT Price → Supplier); no Size field. → §3 + §4 (BR-4) + §6 (sheet handoff).
- **S1-5** **Single unified search box** above the table (2026-07-27 — per-row search retired): type any of SKU No. · brand · EN product name → autocomplete → click adds a row. → §3 + §1 (operator flow: head-down repeated entry, one focus point).
- **S1-6** Picked product = blue-tinted prefill row; SKU·Brand·Product Name **locked read-only** (borderless plain text); wrong pick = ✕ delete + re-search; more SKUs = keep selecting (add-row button retired). → §3 + §1 (mis-edit prevention) + §7 (candidate: edit-locked-cell attempts).
- **S1-7** Tracking No field **optional** (dashed border), addable later; **single register button** (unified 2026-07-27) — registers as REQUESTED with or without tracking; if provided, View Orders matching activates immediately. → §3 + §4 (BR-8) + §5 (DC-3/DC-6).
- **S1-8** Expected arrival date — advance visibility for the center (feeds View Orders "Expected Inbound N" badge, decided 2026-08-02). → §3 + §6 (cross-page).
- **S1-9** View Orders link note — tracking number auto-matches; scans show sourcing route badge (link-info modal removed 2026-08-03). → §3 + §10 (decision log).
- **S1-10** **Unit Cost (KRW) required, 0 allowed** (free-of-charge stock; FOC checkbox retired 2026-07-26 → direct 0). Definition text "actual per-unit purchase price from the supplier"; disclaimer position moved 2026-08-03. Rationale: FIFO costing basis + sheet consistency. → §3 (validation) + §4 (BR-5) + §5.
- **S1-11** **JIT Price (KRW) optional** — per-unit Coupang-JIT purchase price, "leave blank if unknown", all channels (widened 2026-07-26). → §3 + §4 (BR-6).
- **S1-12** **Supplier required** — "who is shipping the goods" (e.g. 비엠유통, Coupang); settlement + inbound-tracking basis. → §3 + §4 (BR-7).
- **S1-14** Top-right Comments hub — @Mentions/★Saved tabs + full comment search, newest first; same component as View Orders [G-7]. → §3 + §5 (DC-10..12) + §6 (Slack).
- **S1-15** Reduced side margins — whole form fits one screen without scrolling. → §1 + §3.
- **S1-16** In-admin page tabs **[New Request | Request List]** (added 2026-07-23) — distinct from wireframe purple state tabs; spec must define tab-switch behavior (no data loss? see Open Q D-6). → §2 + §3.
- **S1 footer rules (un-numbered → spec as [L-S1-F])**: (a) Received Date + Carrier are recorded automatically at inbound, shown in Request List, never form inputs (Carrier later dropped entirely 2026-08-03 — see S3-10); (b) **Request List = the data the Procurement Hub Google Sheet scrapes as-is** — sheet integration designed separately as the last step (agreed 2026-07-23); (c) all labels standardized to "Comments". → §4 + §5 (retention) + §9.

### State 2 — New Request, Wholesale / Partnership variant (2 dots)
- **S2-1** Direct-request routes (Wholesale·Partnership·Other) get the **same automatic Inbound No.** — assigned at registration, visible only in the list. → §3 (route-invariant behavior) + §8 (parametrized test across routes).
- **S2-2** Same product-entry spec across routes — single search box, Order Qty·Unit Cost required (**0 entered directly for free promotional stock**), JIT Price optional. → §3 + §4.
- **S2 footer (un-numbered → [L-S2-F])**: status = 3 stages REQUESTED → PARTIAL → INBOUNDED (SHIPPED retired 2026-07-27 · PARTIAL added 2026-08-02); tracking known now → enter now, matching immediate; else add later from list. → §4 (BR-10).

### State 3 — Request List (10 dots)
- **S3-1** Status filter chips — All / REQUESTED / PARTIAL / INBOUNDED with live counts; tracking presence is read from the Tracking No column, **not** a status. → §3 + §4 (BR-10).
- **S3-2** Bulk bar pinned above table — "Bulk add tracking numbers" for selected rows; mark-shipped button retired; INBOUNDED transitions only via View Orders scans. → §3 + §5 (DC-5) + §7 (candidate: 0 selected).
- **S3-3** Sourcing Route column — black bold badges, View Orders styling [G-5]. → §3.
- **S3-4** Tracking No column — empty → "Add tracking" button (M1); filled → number list (multiple) + matching-status note. → §3.
- **S3-5** Status column — REQUESTED → **PARTIAL (auto-switch on View Orders partial save, remaining n/m shown)** → INBOUNDED (confirmed 2026-08-02); same-tracking rescan resumes reconciliation from remainder; **expected-qty edits (View Orders M6) render history in the Qty cell (✎ 300→180 (damaged)) + Slack alert to requester** [G-11]. → §3 + §4 (BR-13) + §5 (DC-7/DC-8).
- **S3-6** REQUESTED + no tracking → add later via M1; **automatic once-a-morning check flags them on Slack**: WHOLESALE·SMART BUY → #wholesale-ops, PARTNERSHIP → #partnership-kr; Other-route channel decided during development (2026-07-27 alert spec). → §4 (BR-16) + §5 (DC-13) + §6 (Slack rows 1–2).
- **S3-7** **Multiple tracking numbers per request (split shipments, confirmed 2026-08-03)** [G-10] — every registered number is a View Orders match/scan target; badge stays REQUESTED. Mandatory item #7 anchor. → §3 + §4 (BR-9) + §5 (DC-3/DC-6).
- **S3-8** INBOUNDED = auto-switched by View Orders scan inbound (separate link modal + result link removed 2026-08-03 — badge is enough). → §3 + §10.
- **S3-9** Inbound-automation note — no manual INBOUNDED here; scans surface the route badge; morning Slack check restated. → §4 (BR-11).
- **S3-10** **Received Date column** — View Orders scan time recorded automatically on INBOUNDED (maps to sheet Received Date); pre-inbound rows show "–". **Automatic Carrier recording NOT supported — no Carrier column (confirmed 2026-08-03)**. → §3 + §4 (BR-12) + §5 (DC-9) + §10.
- **S3 un-dotted but must be specced**: registration toast ("✓ Inbound request registered — {no}" · "No refresh · added to top of the list") [G-2]; per-row 💬 Comments button + inline comment panel (IR_COMMENTS pattern: author, @mention highlight, time, write box "@name tags trigger a Slack alert", Post button); footer count line "Showing 6 of 12 · Status: …"; ＋ New Inbound Request button → New Request tab. → §3 + §5 + §8.

### Modal M1 — Add Tracking No (1 dot)
- **M1** Multi-row tracking entry: initial row + "＋ Add tracking number" (focus lands in new input), per-row ✕ (last remaining row clears instead of removing — wireframe script behavior), Save → green toast "✓ Tracking number(s) saved · Every registered number is now matched to View Orders · No refresh" [G-2]; status stays REQUESTED; full receipt via scans → INBOUNDED. → §3 + §4 (BR-9) + §5 (DC-3/DC-4) + §7 (dupes/blank rows) + §8 (selectors: `#tnAdd`, `#tnList`, `.tn-del`).

### Removed modal (0 dots, must appear in §10)
- "View Orders link info" modal — **removed 2026-08-03** (HTML comment remains at line 701). Decision-log entry so coverage checks don't resurrect it.

---

## 2. SECTION OUTLINES (10 template sections)

### §1 Purpose & Users
- Who: order team / procurement staff (mock actors: Yongwon, Dean, Miranti) creating requests at a **desk, keyboard, no scanner** — the one WMS page whose primary user is NOT the scanner-in-hand operator. Warehouse staff never transition status here; they act in View Orders State 6.
- Operational moment: before goods ship (create request), at dispatch (add tracking), while goods are in transit (morning chase), after arrival (read-only observation of auto PARTIAL/INBOUNDED).
- Physical-context decisions to narrate: single search box = one focus point for batch SKU entry (S1-5); locked cells = no accidental overwrite of catalog data (S1-6); one-screen form (S1-15); auto Inbound No = zero numbering coordination (S1-3); status auto-flow = desk and warehouse never double-enter the same fact (S3-9).

### §2 Screen Inventory & Wireframe Map
- Table: s1 New Request (Smart Buy sample) · s2 New Request (Wholesale/Partnership sample — same form, data variant; spec treats s1+s2 as ONE functional surface with route-parametrized examples) · s3 Request List · M1 modal · removed link-info modal (tombstone row). Live URL + wf-bar buttons to reach each; in-admin tabs vs wireframe tabs distinction (S1-16).
- Deep link **`#reqlist` / `#s3` opens Request List tab** [G-12] — linked from View Orders State 6 banner; real admin = filtered-entity deep link.
- Note "no dot 13 in State 1" explicitly.

### §3 Functional Specification
- Per legend item as inventoried above. Named specifics to write out: route-card click behavior incl. Other free-text enable/focus/required-when-selected; autocomplete matching fields (SKU no. / brand / EN name) and row-add semantics; numeric validation for Order Qty (required, ≥1), Unit Cost (required, ≥0, comma display), JIT Price (optional, blank ≠ 0); Supplier required; register action = validate → persist → assign Inbound No → toast [G-2] → row appears at top of Request List without refresh → matching activation if tracking present; register is double-click-safe [G-9]; M1 add/remove/save incl. last-row-clears rule; bulk add tracking flow; filter chips; comment panel post flow; ＋ New Inbound Request navigation.
- Explicit "not on this page" list: no scanner protocol surface [G-1], no print [G-4], no audio [G-3] — prevents QA from importing global behaviors that don't apply.

### §4 Business Rules (with rationale + dates — full list in this plan's DNA, keyed BR-1..BR-20)
- BR-1 single intake gateway (all inbound flows originate here) — 2026-07-13 scope addition (section I).
- BR-2 4 selectable channels incl. Other free-text — 2026-07-26.
- BR-3 Inbound No auto YYYYMMDDNNNN (0001–9999/day), list-only visibility — 2026-07-23 scheme, 2026-07-26 preview panel removed; named "Inbound No." to fit non-PO inbounds.
- BR-4 PH-sheet column alignment, no Size — 2026-07-23.
- BR-5 Unit Cost required, 0 allowed (FIFO costing + sheet consistency; FOC checkbox retired 2026-07-26; wording/position fixed 2026-08-03).
- BR-6 JIT Price optional, all channels — 2026-07-26 (was smartbuy·wholesale-only per 07-23 design).
- BR-7 Supplier required (settlement + inbound tracking).
- BR-8 tracking optional at creation; single register button — 2026-07-27.
- BR-9 multiple tracking numbers per request; every number a match/scan target [G-10] — confirmed 2026-08-03.
- BR-10 status = exactly 3 (REQUESTED/PARTIAL/INBOUNDED); SHIPPED retired 2026-07-27, PARTIAL added 2026-08-02; tracking presence ≠ status; rescan resumes from remainder.
- BR-11 no manual INBOUNDED on this page — transition owned by View Orders scans (mark-shipped retired 2026-07-27).
- BR-12 Received Date = scan time, auto; **no Carrier column** — 2026-08-03.
- BR-13 expected-qty edits only via View Orders M6, mandatory reason (supplier change/damaged/other), gating recompute, history in Qty cell, comment + Slack @requester [G-11] — user-added 2026-08-02.
- BR-14 unrequested arrivals → shared unrecognized pool (tracking-missing) — ad-hoc registration path rejected 2026-08-02; recovery: create request + tracking, remove pool row, rescan enters State 6.
- BR-15 Request List = sheet-scrape source of truth; integration designed separately, last step — 2026-07-23.
- BR-16 morning no-tracking check, daily 1×, REQUESTED-only, route-split channels — 2026-07-27.
- BR-17 form Memo also logged to the request's Comments history (form note, S1 memo label).
- BR-18 Inbound No/link-modal minimalism — link modal + result link removed 2026-08-03.
- BR-19 "Comments" label standardization (never localized).
- BR-20 [G-2] toasts on register + M1 save; no refresh anywhere on this page.

### §5 Data Capture — see full event list in Part 3 (this is the Lens-A centerpiece).

### §6 Integrations
- Slack routing table — 4 confirmed rows (Part 4 below) + 1 dev-time row (Other-route morning check) + adjacent cross-page row (#unrecognized-tracking, owned by tracking-missing spec, referenced for BR-14).
- Cross-page: View Orders State 6 banner → `#reqlist` [G-12]; tracking match registry consumed by View Orders unified search; Expected-arrival feeds View Orders Expected Inbound badge; tracking-missing pool ↔ request-creation recovery loop; PH sheet scrape (design deferred).
- Print pipeline: N/A on this page (explicit).

### §7 Edge Cases & Error States (A-lens candidates for B to absorb/extend)
- Register double-click [G-9]; register with zero product rows; Order Qty blank/0; Unit Cost blank (blocked) vs 0 (allowed) vs JIT blank (allowed) — the 0-vs-blank trap; Other selected with empty channel text; duplicate SKU rows in one request; duplicate tracking number (same request / different request / already-INBOUNDED request); M1 all-blank rows saved; M1 open on a row that just auto-switched to INBOUNDED (stale view); bulk add with 0 selected; >9999 requests/day; tracking added → scanned → then user tries to remove it; concurrent M1 edits on same request; comment post on renumbered/old entity; deep-link `#reqlist` with an applied filter.

### §8 QA Acceptance Criteria (A provides anchors; B owns scenarios)
- Exact strings/selectors to hand B: button "Register Inbound Request"; toast texts "✓ Inbound request registered" / "✓ Tracking number(s) saved"; chips "All 12 / REQUESTED 8 / PARTIAL 1 / INBOUNDED 3"; badge "PARTIAL 120/180"; qty history "✎ 300→180 (damaged)"; M1 ids `#tnAdd` `#tnList` `.tn-del`; page tabs; `#reqlist` hash behavior; comment placeholder "Write a comment — @name tags trigger a Slack alert".

### §9 Out of Scope & Open Questions
- Out: Procurement Hub admin page (excluded 2026-08-02); sheet-scrape integration design (separate, last step, 2026-07-23); label/print; carrier auto-record (rejected 2026-08-03); the warehouse-side scan/reconciliation mechanics (View Orders spec §State 6 owns them — this spec only owns the status/columns they write back).
- Open questions: Part 5 below.

### §10 Decision Log (dated skeleton)
- 07-13 section I added to scope (single gateway; routes later widened to 4 incl. JIT globally) · 07-23 form redesign to sheet parity + page tabs + Received Date column + sheet-scrape agreement + Unit Cost required/FOC + JIT optional (SB·WS) · 07-26 Inbound No preview removed + 4 channels (+Other) + brand-inclusive unified search + FOC checkbox → direct 0 + JIT all-channels · 07-27 single search box + inline field help + single register button + SHIPPED retired + morning-alert spec · 08-02 PARTIAL status added + rescan-resume + expected-qty edit (M6) w/ reason+notify + unrecognized-pool reuse decision (ad-hoc path rejected) · 08-03 multi-tracking per request confirmed + link-info modal & result link removed + Carrier column rejected + Unit Cost disclaimer repositioned + M1 save toast added + registration toast + comment panels + EN pass (commit 890e909) + #fulfillment-admin-comments confirmed (C0BMGEWM5QA) + State-1 renumbering (dot 13 vacated).

---

## 3. LENS-A DEEP INVENTORY

### 3a. Data Capture — full event list (22 events, keyed DC-n; each specs actor · ts · entity · old/new)

**UI-surfaced events**
- **DC-1 `inbound_request.created`** — actor(requester), ts, inbound_no, route(enum SMART_BUY|WHOLESALE|PARTNERSHIP|OTHER + other_channel_text), lines[]{sku, brand, product_name, order_qty, unit_cost_krw, jit_price_krw|null}, supplier, tracking_nos[] (0..n at creation), expected_arrival|null, memo|null, source(manual|from_unrecognized — provenance when created to resolve a pool row, BR-14). Surfaced: Request List row + registration toast.
- **DC-3 `tracking_no.added`** — actor, ts, request, numbers[], source(create_form|M1|bulk). Surfaced: Tracking No column.
- **DC-5 `tracking_no.bulk_added`** — actor, ts, request_ids[], per-request numbers (bulk bar). May reuse DC-3 with batch_id; spec must say which.
- **DC-7 `request.status_changed`** — system-actor(=scanning operator from View Orders), ts, request, old→new (REQUESTED→PARTIAL→INBOUNDED, incl. REQUESTED→INBOUNDED direct), received_so_far n/m on PARTIAL. Written by View Orders; READ here. Surfaced: Status badge.
- **DC-8 `request.expected_qty_edited`** — editor, ts, request+line, old_qty→new_qty, reason(enum supplier_change|damaged|other + free text), origin=View Orders M6. Surfaced: ✎ history in Qty cell; side effects: gating recompute + auto-comment + Slack @requester [G-11].
- **DC-9 `request.received_date_recorded`** — ts = View Orders scan time, on INBOUNDED. Surfaced: Received Date column ("–" until then). No carrier captured (BR-12).
- **DC-10 `comment.posted`** — author, ts, entity=inbound_no, text, mentions[]. Surfaced: row panel + hub; AI-training asset per [G-7].
- **DC-11 `comment.auto_posted`** — system comments: expected-qty edit (old→new, reason, editor) and any future auto-posts; same store as DC-10 with `auto=true`.
- **DC-12 `comment.starred` / `comment.unstarred`** — per-user saved list (hub ★).
- **DC-13 `comment.read` / `mentions.mark_all_read`** — per-user unread state driving hub badge count.

**Silent events (no UI, must still persist [G-8])**
- **DC-2 `inbound_no.allocated`** — server sequence allocation ts (collision/exhaustion audit for 0001–9999/day).
- **DC-4 `tracking_no.removed`** — actor, ts, old value — ONLY if a persisted number can be removed (Open Q O-2); pre-save M1 row deletion is client-only and NOT an event.
- **DC-6 `tracking_match.activated`** — system, ts, request, tracking_no — the moment a number becomes a View Orders match target (one per number; proves matching latency and coverage; QA anchor for "matching activates immediately").
- **DC-14 `morning_check.executed`** — system, ts, flagged request_ids per channel, Slack message ts — audit that the daily sweep actually fired (silent-failure guard).
- **DC-15 `slack_notification.sent`** — system, ts, route(channel), payload hash, trigger(DC-8|DC-10 mention|DC-14) — delivery record for every outbound Slack event on this page.
- **DC-16 `request.viewed_via_deeplink`** — optional; entry source (#reqlist from View Orders banner) — LOW priority, mark as dev-optional telemetry, not doctrine-mandatory.

**Explicit non-events (spec must state, so devs don't over-build)**
- Pre-submit form edits (row add/✕, field typing, route re-picks) = client draft, not persisted; autocomplete queries not logged; filter-chip clicks and list sorts not persisted; wireframe demo counters not data.

**Retention / export**
- Requests + lines + tracking numbers + status history + comments: retain indefinitely — the Request List **is** the dataset Procurement Hub's Google Sheet scrapes as-is (BR-15); export format = deferred to the separate sheet-integration design; comments retained as AI-training asset [G-7]; morning-check + notification logs retained for automation audit.

### 3b. Operator-flow notes (field-usability findings to write into §1/§3/§4)
- **One-focus batch entry**: requester holds a supplier PO/quote; flow = search → click → type qty → type cost → back to search. The single box + auto-row keeps hands on keyboard; spec should require that after a row is added, focus RETURNS to the search box (wireframe implies, must be stated) and that Tab order within a new row is Qty → Unit Cost → JIT.
- **0-vs-blank discipline**: Unit Cost 0 = free stock (meaningful), JIT blank = unknown (meaningful). Placeholders carry the semantics; spec must forbid silently coercing blank JIT to 0 (would poison JIT price data downstream).
- **No status levers at the desk**: the desk user can never claim goods arrived; only warehouse scans move status. This kills the "desk marks INBOUNDED early to tidy the list" failure mode — write as rationale under BR-11.
- **Chase loop is push, not poll**: missing tracking is surfaced by the morning Slack check into the channel where the responsible team lives (route-split), not by someone reading the list — BR-16 rationale.
- **Desk↔warehouse async channel = Comments**: qty disputes, arrival slips, forklift notes (S2 memo sample) travel as comments with @mention Slack pushes, keeping the request the single thread of record.
- **M1 under time pressure**: dispatch emails arrive with several tracking numbers; ＋-row + focus-new-input + Enter-to-save should be specced so a user can paste n numbers without touching the mouse (B to turn into QA scenario).

---

## 4. MANDATORY-INCLUSION MAP (of the 12)

| # | Item | Lands here? | Where |
|---|---|---|---|
| 2 | Global confirmation toast [G-2] | YES | §3 register toast + M1 save toast; no-refresh page-wide (BR-20) |
| 7 | **Multiple tracking numbers per request [G-10]** | YES — this page is the primary owner (with View Orders) | §3 S3-7 + M1, §4 BR-9, §5 DC-3/5/6, §8 anchors |
| 12 | Comment @mention Slack routing [G-7] | YES — channel now CONFIRMED `#fulfillment-admin-comments` (C0BMGEWM5QA) | §3 S1-14 + row panels, §5 DC-10..13/15, §6 table |
| 6 | Unrecognized matching behavior | Secondary (cross-ref) | §4 BR-14 recovery loop + §6 cross-links; authoritative spec = view-orders + tracking-missing |
| 1,3,4,5,8,9,10,11 | Scanner / audio / print / sample / RTO KR / location / audit / JIT-residual | NO | §3 carries an explicit "not on this page" note so the coverage matrix shows deliberate N/A, not omission |

---

## 5. OPEN QUESTIONS

### Owner must decide
- **O-1 Post-registration correction path**: the wireframe has NO edit or cancel/void for a registered request (only tracking add + qty edit via View Orders M6). What happens when a request has the wrong SKU/route/supplier, or the purchase is cancelled before dispatch? A cancel/void status (and its Slack/comment trail) is currently undefined.
- **O-2 Persisted tracking-number deletion/edit**: M1 rows can be removed pre-save; can a SAVED number be deleted or corrected (typo) — and what if it has already been scanned/matched?
- **O-3 Duplicate tracking across requests**: same number on two requests (one physical parcel serving two POs is plausible in wholesale) — reject, warn, or allow with shared-scan semantics? Directly affects View Orders match integrity.
- **O-4 OTHER route downstream rendering**: [G-5] says exactly 4 routes (SMART BUY/JIT/WHOLESALE/PARTNERSHIP) consumed by View Orders badges, but this form offers Other + free text (OTHER badge shown in wireframe). What badge does a View Orders scan show for an Other-route request, and does the free-text channel surface anywhere downstream (Inventory, sheet)?
- **O-5 Permissions**: who may create requests / add tracking / bulk add — any admin login, or role-limited? (No gating encoded anywhere.)

### Developer decides at build time
- **D-1 Other-route morning-check channel** — explicitly deferred to development in legend S3-6 / slack-routing "future routes" row (surface to owner if a new channel must be created).
- **D-2 Inbound No exhaustion (>9999/day)** — practically unreachable; define fail-safe (block + error toast) at build.
- **D-3 Bulk-add UX shape** — per-row sequential entry vs one modal iterating selected rows; wireframe encodes only the button + count.
- **D-4 Expected-arrival optionality** — no asterisk → optional; confirm default (blank vs today).
- **D-5 Memo→Comments materialization** — authored-as-requester at registration ts; exact rendering of the auto-comment.
- **D-6 Page-tab switch draft handling** — warn on unsaved New Request form when switching to Request List, or persist draft client-side.
- **D-7 DC-5 event shape** — batch event vs per-request DC-3 with batch_id.
- **D-8 Numeric input formatting** — comma display vs raw digits storage (store integers, format on render — recommend, but presentation-level).
