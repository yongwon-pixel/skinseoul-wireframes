# view-orders — Spec Plan, LENS B (Developer & QA)

Planner: Lens B (functional precision · edge cases · QA acceptance criteria). Wireframe SST: `wms2/view-orders/index.html` (v20), live `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/view-orders/`. Legend numbers repeat per state, so the spec MUST key items as `[L-{state}-{n}]` (e.g. `[L-S1-8]`) and modals as `[L-M1]..[L-M6]`. Every key below maps 1:1 to a wireframe dot.

---

## 1. LEGEND INVENTORY (58 units: 50 state dots + 8 modal dots — none may be missing from spec §3)

### State 0 — Waiting (2)
- **[L-S0-1]** Empty unified search box, auto-focus. → §3: input contract (4 number types), auto-detect, references S1-1/12/14 rules; rule text NOT rendered on screen. QA: focus assertion on load.
- **[L-S0-2]** Expected Inbound summary badge (decided 2026-08-02): collapsed one-liner → inline table (tracking-first sort, route badges, PARTIAL n/m); **row click = enter State 6 without scanning** (damaged-label path). → §3 + §7 empty-list case + deep link to `../inbound-request/#reqlist` [G-12].

### State 1 — Scan result, last item remaining (21)
- **[L-S1-1]** Unified search auto-detect, multi-match → selection list; **Coupang QR `[V1]barcode` prefix must match**. → §3 parse/normalize algorithm + server lookup order; §8 prefix tests.
- **[L-S1-2]** Shelf input + floating Save (input→show, click/Enter→instant save, "✓ Saved", no refresh). Same pattern as S6 Location inputs. → §3 with server action + [G-8] event.
- **[L-S1-3]** Comments hub (Mentions/Saved tabs, ★ toggle, click→open order, **full-text search across ALL comments**, newest-first, clear→tabs). → §3; [G-7] deltas only.
- **[L-S1-4]** Reduced side padding — one-screen fit, no horizontal scroll. → §3 layout constraint; QA viewport check.
- **[L-S1-5]** Scanned product row highlighted + sorted to top. → §3 sort rule (`row-hit` class).
- **[L-S1-6]** Sourcing Route column: 4 routes [G-5], black bold text; JIT purchase channel in parens; Existing-inventory pick shows the stock's own route, not JIT; route matched from Inbound Request by tracking no. → §3 + §4.
- **[L-S1-7]** Qty ≠ 1 → amber highlight (`qty-warn`). → §3 render rule.
- **[L-S1-8]** Last-remaining-item ⇒ combined **Inbound + Outbound** button. → §3 exact enable condition (uninbounded count == 1) + state transition + [G-9].
- **[L-S1-9]** Bulk bar above table: **Bulk Inbound (Selected)** / **Inbound + Outbound All Remaining** (full inbound completes order ⇒ auto-outbound; Hold stops at Inbound). Always visible, disabled when N/A. → §3 + §4.
- **[L-S1-10]** Button label is "Outbound" (renamed from "Outbound to Deleo Baroship"). → §3 label contract.
- **[L-S1-11]** Order Comments button (badge count) toggles panel; @tag → Slack. → §3; routing in §6.
- **[L-S1-12]** Search input value persists after inbound. → §3 + QA.
- **[L-S1-13]** Actor Log (Inbound/Outbound Log): time·action·SKU·qty·worker·memo; shown States 1–5. → §3 + §5 (view over persisted events, [G-8]).
- **[L-S1-14]** Click-anywhere + post-action ⇒ search box auto-focus with select-all. → §3 focus-return contract (+ exclusion list while typing in other inputs — see OQ/DQ).
- **[L-S1-15]** No refresh + top-right toast, all states [G-2]; outbound-class buttons play send sound [G-3a]. → §3 toast/audio contract.
- **[L-S1-16]** Floating live barcode feed: collapsed default, max 10–20 rows on screen, full history backend, export by date. → §3 + §5 retention/export.
- **[L-S1-17]** Location column right of Sourcing Route; shows current location for warehouse-stored items; States 1–5 common. → §3.
- **[L-S1-18]** Brand always prefixed in Product Name [G-6]; missing-brand products = product-name logic fix. → §4.
- **[L-S1-19]** Results-area Comments panel expanded by default; ★ aggregates to hub Saved. → §3.
- **[L-S1-20]** Barcode-less product: always-visible input in Barcode column (all states); saved value writes to product master, recognized from next scan. → §3 validation (duplicate barcode) + §5 event.
- **[L-S1-22]** **Print Return Labels** (states 1·1b·2·3) → opens M4; supplier-return concept, distinct from State 4. → §3 + [G-4].
- **[L-S1-offscreen]** Behavior-rules paragraph: (a) single-item orders auto-print label on scan — only when no inbound history; Existing Inventory ≠ inbound history; (b) unrecognized barcode → M2 → match writes tracking onto order line, rescan resolves; else M2b; (c) inbound-request tracking scan → State 6 branch. → each gets its own §3 sub-item; MUST NOT be lost because it has no dot.

### State 1b (1)
- **[L-S1b-21]** Non-last item ⇒ plain **Inbound** button; flips to Inbound + Outbound when exactly 1 uninbounded remains; Outbound stays disabled until all inbounded. → §3 button state machine.

### State 2 — All inbounded (2)
- **[L-S2-1]** Outbound button activates (green) when every item INBOUNDED. → §3 enable condition.
- **[L-S2-2]** Cancel Inbound → restock popup (M1). → §3.

### State 3 — Outbound complete (4)
- **[L-S3-1]** Button becomes "✓ Outbounded", disabled. → §3.
- **[L-S3-2]** **Cancel Outbound** rolls status prepare shipment → processing. → §3 transition + [G-8] event + [G-9].
- **[L-S3-3]** Completion toast, no refresh ⇒ next scan immediately. → §3.
- **[L-S3-4]** Individual Cancel Inbound disabled post-outbound (must Cancel Outbound first — ordering guard; ledger marks this "proposal": spec states it as adopted unless owner objects). → §4.

### State 4 — Customer return mode (6)
- **[L-S4-1]** Return banner on scanning returned tracking barcode. → §3 detection rule.
- **[L-S4-2]** **Restock Selected to Warehouse (n)** → opens M3. → §3.
- **[L-S4-3]** M3 rules: restock qty default 0 (0 = excluded), location auto-fill for existing stock, memo; confirm count = items qty>0. → §3 (under M3).
- **[L-S4-4]** qty>0 with no location ⇒ Confirm disabled. → §3 validation (under M3).
- **[L-S4-5]** Last-mile (return) barcode searchable via unified search. → §3.
- **[L-S4-6]** No "returned" status exists — 8 real statuses; returns usually `refunded`, sometimes `failed`, can arrive `completed`; detection is by scan, not status. → §4 (critical business rule).

### State 5 — Hold order (3 + note)
- **[L-S5-1]** Hold banner: requester · reason · time, instant on scan. → §3.
- **[L-S5-2]** Outbound disabled while On Hold. → §3.
- **[L-S5-3]** Bulk: Inbound allowed, Inbound+Outbound-All blocked. → §3.
- **[L-S5-offscreen]** Hold applied in OMS/Order detail/Order Management; View Orders display+block only. → §9 out-of-scope boundary.

### State 6 — Internal inbound (9 + note)
- **[L-S6-1]** Auto-branch: inbound-request tracking ⇒ this screen, never States 1–5; multiple tracking nos per request all match [G-10]. → §3 routing precedence table.
- **[L-S6-2]** Internal Inbound banner (Inbound No·channel·supplier·requester·expected arrival + link `../inbound-request/#reqlist` [G-12]). → §3.
- **[L-S6-3]** Progress tiles: Expected / Received / Remaining / SKU (n done). → §3 computed fields.
- **[L-S6-4]** Continuous product-barcode scanning: each scan +1 to that SKU's Received; cursor auto-return [G-1]; **warning sound for product not in request**. → §3 + §7.
- **[L-S6-5]** Reconciliation table columns come straight from the Inbound Request. → §3 data source.
- **[L-S6-6]** Received Qty editable (manual box-level entry). → §3 + [G-8] old/new capture.
- **[L-S6-7]** Location = Inventory intake position; existing SKU auto-suggest (one-location-per-SKU [G-14]); new SKUs manual. → §3.
- **[L-S6-8]** **Confirm Full Inbound** gated on exact match per SKU; else **Save Partial Inbound (M5)**; over-scan warns. → §3 gating formula + §7.
- **[L-S6-9]** **Edit Expected Qty (✎ → M6)** (decided 2026-08-02): new qty + required reason; recomputes gating; auto-comment on request + Slack @requester. → §3 + §6.
- **[L-S6-offscreen]** On confirm: ① Inventory (Current Stocks) reflects with locations ② Request status REQUESTED/PARTIAL → INBOUNDED ③ Received Date auto (Carrier auto-record NOT supported — 2026-08-03) ④ focus → search box. No Outbound on this screen. → §3.
  - ⚠ Wireframe contradiction: 6b banner still says "Carrier recorded automatically" — legend note (dated 2026-08-03) wins; flag banner text for fix (see OQ-4).

### State 6b (2)
- **[L-S6b-1]** Completion banner: exact-match result, inventory locations, INBOUNDED, auto Received Date. → §3.
- **[L-S6b-2]** Focus returns to search box on completion, no refresh. → §3.

### Modals (8)
- **[L-M1]** Cancel Inbound: restock yes/no radio (No ⇒ qty disabled+cleared), restock qty default = inbounded qty, optional memo (also into Comments history); Reserved→Available auto-update. → §3 full I/O + [G-9].
- **[L-M2]** Unrecognized Barcode step 1: order-no lookup → match table → "Match Tracking No" writes tracking onto that order line, closes, toast; rescan recognized. → §3 (mandatory inclusion #6).
- **[L-M2b]** Send to Missing Tracking List: product autocomplete (EN, KR shown), qty, memo, carried failed order-no; on send → green toast + #unrecognized-tracking Slack. → §3 + §6.
- **[L-M3]** Customer Return Restock table (qty default 0 / location / per-modal memo) + confirm-count logic. → §3.
- **[L-M3b]** M3 memo field — recorded in order Comments history AND inbound log. → §5.
- **[L-M4]** Print Return Labels: carrier chips + Custom input, per-item optional size/qty (omitted if empty), live preview, print = instant [G-4]. → §3.
- **[L-M5]** Save Partial Inbound: reason select, memo; received units added to Inventory immediately; request → PARTIAL (n/m); rescan resumes. → §3.
- **[L-M6]** Edit Expected Qty: new qty, required reason select, memo; recompute; auto-comment + Slack @requester; history shown in request list qty cell. → §3. (Demo header shows Inbound No. …0002 vs state …0001 — wireframe demo inconsistency, QA note only.)

---

## 2. SECTION OUTLINES (10 template sections)

**§1 Purpose & Users** — Warehouse staff scan hub: one screen for customer-order inbound/outbound, customer returns, hold display, and internal stock intake (States 6/6b). Physical context that shaped decisions: scanner-in-hand continuous flow (G-1 focus residency), audio confirmation because eyes are on boxes not monitor (G-3a, S6-4 warning sound), one-screen fit (S1-4), Korean names as picker-facing data (G-6).

**§2 Screen Inventory & Wireframe Map** — Table: 9 states (s0, s1, s1b, s2, s3, s4, s5, s6, s6b) + 7 modals (M1, M2, M2b, M3, M4, M5, M6) ↔ `[L-*]` keys ↔ how to reach (top wf-tab labels exactly as rendered: "0 · Waiting (Before Scan)" … "Modal: Edit Expected Qty"). Note the wireframe's per-state legend numbering and the spec's `[L-{state}-{n}]` remap.

**§3 Functional Specification** — Per `[L-*]` above. Lens-B must-haves per item: trigger · exact behavior · inputs/outputs · validation · server action (name the endpoint semantically, e.g. `POST /wms/inbound-item`, `POST /wms/outbound-order`, `POST /wms/inbound-request/{id}/receive-scan`, `PATCH …/expected-qty`) · state transitions (item: PENDING→INBOUNDED→(cancel)→PENDING; order: processing→prepare-shipment⇄(cancel outbound); request: REQUESTED→PARTIAL→INBOUNDED) · idempotency [G-9] on every confirming action (client debounce + server key; retry-safe) · UI feedback (exact toast texts from wireframe: "✓ Inbound complete — {SKU}", "✓ Outbound complete — Order {id}" + "Status: prepare shipment", "✓ Inbound complete — Inbound No. {n}", "✓ Tracking No {n} matched and registered", "✓ Sent to Missing Tracking List"; sounds). Buttons: exact labels + enable matrices (Outbound enabled iff all items INBOUNDED ∧ not On Hold ∧ not already outbounded; Inbound+Outbound iff exactly-1 uninbounded; bulk-bar matrix per state incl. gray states in s2/s3). Search resolution precedence: inbound-request tracking → State 6; return last-mile → State 4; else customer order states; `[V1]` prefix strip; multi-match selection.

**§4 Business Rules** — Route taxonomy [G-5] + JIT channel parens + existing-inventory display rule (S1-6, dated per ledger); auto-outbound on full inbound, Hold exception (S1-9, F-Hold); no-auto-carrier-record (2026-08-03); return detection by scan not status (S4-6, 8-status list); single-item auto-print precondition (no inbound history; existing inventory excluded); Cancel-Inbound-after-outbound lockout (S3-4); brand-prefix naming [G-6]; exact-match gating for full confirm (S6-8, same doctrine as Closing); one location per SKU [G-14 delta]; barcode-master write from S1-20.

**§5 Data Capture [G-8]** — Full event list is Lens-A's deep inventory; Lens-B contributes the contract each event must satisfy for QA: actor+ts+entity+old/new for — inbound, outbound, cancel inbound (restock y/n, qty, memo), cancel outbound, hold display (applied elsewhere, logged there), return restock per-SKU qty+location+memo, shelf save, location save, received-qty manual edit, expected-qty edit (old→new+reason), partial-inbound save (reason), full-inbound confirm, barcode-master write, comment post/★/read, unrecognized send (all M2b fields), match-confirm, every raw scan (live feed, max 20 on screen, full history backend, export-by-date). Retention: scans and logs are append-only; UI views never the only copy.

**§6 Integrations** — Slack table (CONFIRMED per `_slack-routing`): M2b send → `#unrecognized-tracking`; @mention + qty-edit auto-comment + match-confirm auto-comment → `#fulfillment-admin-comments` with in-body @mention (NOTE: G-7 draft says "pending" — superseded, routing file is CONFIRMED 2026-08-03; spec cites the confirmed channel). Deep links: S0-2 table & S6-2 banner → `../inbound-request/#reqlist` [G-12]; comments-hub click → order page. Cross-page: match-confirm ↔ tracking-missing M1; restock stock ↔ Inventory Current Stocks; Received Date → sheet sync. Print pipeline [G-4]: order-card Print, single-item auto-print, M4 return labels — all instant, carrier-agnostic, local print agent.

**§7 Edge Cases & Error States** — see deep inventory below (≈48 `[E-n]`).

**§8 QA Acceptance Criteria** — see plan below (≈100 scenarios, machine-runnable against live wireframe: exact wf-tab labels to click, DOM anchors like `.btn-gray`, `#m-unrec`, `.gtoast`, `.qedit`, exact toast strings).

**§9 Out of Scope & Open Questions** — Hold application (OMS/Order detail), label layout content (Phase 3-1), Deleo Tracking No (removed here, lives in Order Detail — 07-09 ledger), photo upload on unrecognized (deferred 2026-07-21), Procurement Hub (excluded 2026-08-02). Open questions from section 5 below.

**§10 Decision Log** — dated: v20 route badges+Hold+return last-mile+hub (07-13); internal inbound merged into view-orders as 6/6b, separate page killed (07-27); expected-inbound badge C-option + 3-stage request status + unrecognized-pool reuse (08-02 ledger block, commit 960f5cf); Edit Expected Qty (08-02); photo upload deferred (07-21); multi-tracking [G-10] + carrier-auto-record NOT supported + send sound + toast doctrine + scanner protocol + instant print (08-03); comment channel confirmed #fulfillment-admin-comments (08-03); "[V1]" rule text tidied off-screen (07-23); reversal record: 07-09 "Received Date/Carrier 자동" → 08-03 carrier auto-record dropped.

---

## 3. LENS-B DEEP INVENTORY

### 3a. Edge-case candidates `[E-n]` (exhaustive; spec §7 keeps IDs stable)

Scan & search
- **E-1** Fully unrecognized barcode → M2 opens (no crash, focus in order-no field).
- **E-2** M2 lookup match → match button writes tracking, closes, toast; rescan same barcode resolves normally.
- **E-3** M2 lookup no-match → M2b with carried order-no line visible.
- **E-4** M2 "No order number" → M2b without carried number.
- **E-5** M2b send → green toast + #unrecognized-tracking payload (product, barcode, qty, memo, failed order-no).
- **E-6** Coupang QR scan arrives as `[V1]8801051283860` → matches as if unprefixed.
- **E-7** Number matches multiple entities (e.g. same digits as product-order and tracking) → selection list, no silent pick.
- **E-8** Inbound-request tracking scanned → State 6 always (never customer states), incl. 2nd/3rd tracking of same request [G-10].
- **E-9** Return last-mile barcode → State 4 banner; status may be refunded/failed/completed (all three must route to S4).
- **E-10** Empty search submit → no-op or inline error; no state change.
- **E-11** After inbound: input keeps value (S1-12) AND next click/action re-focuses with select-all (S1-14) so next scan overwrites.
- **E-12** Focus-return must NOT hijack while user is typing in comment/memo/barcode/shelf inputs (else scans corrupt comments).

Duplicates & over-scan
- **E-13** Double-click Inbound / Outbound / Confirm (known prod bug, G-9) → exactly one server mutation; second is idempotent no-op.
- **E-14** Rescanning an already-INBOUNDED item's product barcode in a customer order → defined response (warn toast? see OQ-1), never a second inbound.
- **E-15** State 6: scan beyond Expected Qty → warning (S6-8); define whether count is capped (OQ-8).
- **E-16** State 6: scan product not in the request → warning sound + no count anywhere + suggested action (S6-4).
- **E-17** Rescanning tracking of a fully INBOUNDED request → defined behavior (read-only 6b view vs toast; OQ-5).
- **E-18** Barcode shared by 2 SKUs (e.g. 1+1 set vs single) → disambiguation, not arbitrary +1.
- **E-19** Bulk Inbound with 0 rows selected → button disabled or error toast.
- **E-20** "Inbound + Outbound All Remaining" clicked twice fast → one outbound, one label print.

Partial / damaged / qty edits
- **E-21** M5 partial save → 620 units in Inventory immediately, request → PARTIAL 620/800, State 0 badge reflects it.
- **E-22** Rescan same tracking after PARTIAL → State 6 resumes from remaining (not from zero).
- **E-23** M6 qty edit down to received (300→120 with 120 received) → Confirm Full Inbound enables without further scans.
- **E-24** M6 new expected < already received (e.g. 120 received, edit to 100) → validation (OQ-3).
- **E-25** M6 with reason unselected → Save blocked (reason required).
- **E-26** M1 cancel with restock=No → qty input disabled+cleared; stock NOT re-added; reserved released per rule.
- **E-27** M1 restock qty edited below inbounded qty (partial damage) → allowed; remainder accounted (memo).
- **E-28** M3: all rows qty 0 → Confirm shows (0) and is disabled (nothing to restock).
- **E-29** M3: qty>0 + empty location → Confirm disabled until location filled (S4-4).
- **E-30** M3: qty > ordered qty → validation (over-restock block).
- **E-31** M4: Custom carrier chip with empty name → Print blocked or placeholder rejected; size/qty empty → omitted on label.

Concurrency
- **E-32** Two operators, same order: both see "last item" and click Inbound+Outbound → server serializes; one wins, other gets error/refresh toast; no double outbound.
- **E-33** Two stations receiving same inbound request (State 6) → counts merge server-side, no lost updates; tiles refresh.
- **E-34** CS applies Hold while operator has order open → Outbound attempt server-rejected with hold toast even though button was enabled (stale client).
- **E-35** Order refunded/cancelled mid-flow → outbound rejected with explicit reason.
- **E-36** Comment posted by another user while panel open → badge/count update without refresh (or on next fetch — define).

Network / printer / integrations
- **E-37** Network drop mid-inbound → red error toast, no optimistic INBOUNDED tag; retry with same idempotency key safe.
- **E-38** Network drop after server commit, before response → retry returns success-idempotent; UI reconciles (no dup log row).
- **E-39** Print agent offline [G-4] → explicit failure toast naming the printer/agent; inbound/outbound commit is NOT rolled back; single-item auto-print failure does not block inbound (OQ-6 confirm).
- **E-40** Slack delivery failure (mention / unrecognized) → primary action still commits; failure logged/retried (DQ-7).
- **E-41** Audio blocked (browser autoplay policy before first gesture) → action still processes; sound is enhancement only.

Empty states & data
- **E-42** State 0 with zero pending inbound requests → badge hidden or "0" collapsed state defined.
- **E-43** Comments hub: empty Mentions/Saved tabs → empty-state text; search with no hits → "No matching Comments".
- **E-44** S1-20 barcode entry duplicates a barcode already on another SKU → block with error (master integrity).
- **E-45** Shelf/location floating save: same value re-entered → button stays hidden (no phantom event); Enter with hidden button → no-op.
- **E-46** State 6 new-SKU location left empty at Confirm Full Inbound → gating (OQ-2).
- **E-47** S0-2 row click into State 6 for a request with NO tracking registered (Coupang QR damaged path) → allowed; screen functions without tracking context.
- **E-48** Toast burst during rapid continuous scanning → readable stacking/replacement policy (DQ-2); send-sound never overlaps into distortion.

### 3b. QA scenario plan (Given/When/Then, keyed `[L-*]`/`[E-n]`, executable on live wireframe; real-admin-only assertions tagged `@admin-only`)

Estimated counts per §8 subsection (total ≈ 100):
| §8 block | scope | est. scenarios |
|---|---|---|
| 8.1 State 0 & expected-inbound badge | L-S0-1/2, E-42, E-47 | 7 |
| 8.2 Unified search & scan protocol | L-S1-1/12/14, G-1, E-1..E-12 | 13 |
| 8.3 States 1/1b buttons & rows | L-S1-5..10, S1b-21, E-13/14/19/20 | 12 |
| 8.4 States 2/3 outbound & cancels | L-S2-*, L-S3-*, E-32/35 | 9 |
| 8.5 State 4 returns + M3 | L-S4-*, M3/M3b, E-9/28/29/30 | 9 |
| 8.6 State 5 hold | L-S5-*, E-34 | 4 |
| 8.7 States 6/6b + M5/M6 | L-S6-*, S6b-*, E-15/16/17/21..25/33/46 | 16 |
| 8.8 Modals M1/M2/M2b/M4 | L-M1/M2/M2b/M4, E-1..5, E-26/27/31 | 12 |
| 8.9 Comments (panel + hub + search) | L-S1-3/11/19, E-36/43 | 8 |
| 8.10 Logs, feed, data capture | L-S1-13/16, §5 contract | 5 |
| 8.11 Global: toast/audio/print/no-refresh | G-2/3/4, L-S1-15, E-39/41/48 | 7 |
| 8.12 Negative & idempotency/concurrency | G-9, E-13/32/33/37/38/44 | 8 |

Three fully-worked examples (format the spec will use):

**QA-8.7-05 — Expected-qty edit re-enables full confirm** `[L-S6-9][L-M6][E-23]`
Given the live wireframe with top tab `6 · Internal Inbound (Inbound Request)` active,
When I click the `✎` button (element `button.qedit`) on the row containing SKU `100052124`,
Then overlay `#m-qtyedit` is visible with header text `Edit Expected Qty — Inbound No. 202607120002`, a `New Expected Qty` input valued `120`, helper text `300 → 120 (−180)`, and a required Reason select whose first option is `Damaged/defective — cannot accept`;
When I click `Save Qty Edit`, Then the overlay closes. `@admin-only`: expected qty persists 300→120 with actor/old/new/reason event [G-8]; Remaining tile recomputes to 0; button `Confirm Full Inbound` becomes enabled; an auto-comment appears on Inbound Request 202607120001 and a Slack message posts to `#fulfillment-admin-comments` @mentioning Dean with old→new qty and reason.

**QA-8.8-03 — Unrecognized barcode happy path** `[L-M2][E-2]`
Given top tab `Modal: Unrecognized Barcode` clicked so `#m-unrec` is open, and input `#unrecNo` has value `12101316464794`,
When I click `🔍 Look up`, Then `#unrecFound` becomes visible showing exactly 2 rows, first row product name contains `Pore Remedy Renewing Foam Cleanser` with tracking `10323100835644`;
When I click that row's `Match Tracking No`, Then `#m-unrec` closes and toast `#unrecToast` is displayed containing `✓ Tracking No 10323100835644 matched and registered` and hides within ~4s. Negative twin (QA-8.8-04): change `#unrecNo` to any other value, click `🔍 Look up` → `#unrecNone` visible with `No products match`, button `Send to Missing Tracking List` present; clicking it opens `#m-unrec2` with the carried number rendered in `#unrecCarriedNo`.

**QA-8.6-02 — Hold order blocks outbound (negative)** `[L-S5-2][L-S5-3][E-34]`
Given top tab `5 · Hold Order` active,
Then the banner contains `⏸ Hold Shipment` and `Order 414102 · Requested by Sara(CS) 07-13 09:20`; the order-card `Outbound` button has class `btn-gray` (disabled semantics — click produces no state change and no send sound); in the bulk bar, `Bulk Inbound (Selected)` is enabled (`btn-green-line`) while `Inbound + Outbound All Remaining` has `btn-gray`; helper text equals `Hold order — Inbound allowed, Outbound blocked (ship after Hold release)`. `@admin-only`: server rejects a forced outbound POST on an on-hold order with an explicit hold error, and the rejection is logged [G-8].

---

## 4. MANDATORY-INCLUSION MAP (owner's 12)

| # | Item | Lands here? | Where in this spec |
|---|---|---|---|
| 1 | Scanner protocol [G-1] | YES | §3 L-S0-1/S1-14/S6-4/S6b-2; QA 8.2 |
| 2 | Confirmation toast [G-2] | YES | §3 L-S1-15 + every confirming action; QA 8.11 |
| 3 | Audio feedback [G-3a send sound] | YES | §3 L-S1-15 (outbound-class buttons) + S6-4 warning sound; QA 8.11 (TTS voice = Closing page, not here) |
| 4 | Instant carrier-agnostic print [G-4] | YES | §3 order-card Print · single-item auto-print (S1-offscreen) · M4; §6 print pipeline; E-39 |
| 5 | Sample dual-view [G-13] | NO (Order Management) | cross-ref only in §6/§9 |
| 6 | Unrecognized matching behavior | YES | §3 M2/M2b + off-screen rule; §6 Slack; QA 8.8 |
| 7 | Multi-tracking per request [G-10] | YES | §3 L-S6-1; E-8; QA 8.7 |
| 8 | RTO Korean names [G-6] | NO (RTO page) | G-6 naming deltas only (Product Name KR column, KR names on M4 labels) |
| 9 | Line-based location filter [G-14] | NO (Inventory) | one-location-per-SKU delta cited at L-S6-7 |
| 10 | Audit-mode-only visibility | NO (Inventory) | — |
| 11 | JIT residual stock in Inventory | PARTIAL (origin side) | §3 L-M1 note ("JIT ordered by mistake" restock creates the residual stock Inventory must show) + §6 cross-ref |
| 12 | Comment @mention Slack routing [G-7] | YES | §3 L-S1-3/11/19; §6 routing table (channel CONFIRMED #fulfillment-admin-comments — supersedes G-7 "pending" note) |

---

## 5. OPEN QUESTIONS

### Owner must decide (do not invent)
- **OQ-1** (E-14) Rescanning an already-INBOUNDED product barcode in a customer order: warn-and-ignore toast, or something else? Wireframe is silent.
- **OQ-2** (E-46) State 6 Confirm Full Inbound: is a Location required for every (new) SKU before confirm, or can stock enter Inventory location-less? Wireframe gates only on qty match; G-14 implies one-location-per-SKU.
- **OQ-3** (E-24) M6 edit where new Expected Qty < already-received qty: hard block, or allow and treat excess as over-receipt?
- **OQ-4** Carrier auto-record contradiction: S6 legend (2026-08-03) says NOT supported, but S6b banner text still reads "Carrier recorded automatically". Confirm banner text is stale and should be corrected in wireframe + spec (spec will follow the dated legend unless overruled).
- **OQ-5** (E-17) Rescanning tracking of an already fully-INBOUNDED request: open a read-only 6b view, or error toast?
- **OQ-6** (E-39) Single-item auto-print failure (agent offline): confirm inbound still commits with red toast (proposed), vs. blocking the inbound.
- **OQ-7** (E-15/OQ-8) State 6 over-scan: warn-but-count (received may exceed expected, blocking full confirm) vs. cap at expected? "Over-scanning warns" is ambiguous.
- **OQ-8** (S3-4) Cancel-Inbound lockout after outbound is marked "proposal" in the 07-09 ledger — confirm adoption as a rule.

### Developer decides at build time
- **DQ-1** Idempotency key format/TTL and client debounce interval [G-9].
- **DQ-2** Toast duration/stacking policy under rapid scans (E-48).
- **DQ-3** Live-feed backend retention horizon, export file format (CSV assumed), date-range picker UI.
- **DQ-4** Focus-return exclusion implementation (which focused elements suppress auto-refocus, E-12) — rule itself is spec'd; mechanism is dev's.
- **DQ-5** Multi-match selection list layout (E-7).
- **DQ-6** Duplicate-barcode master-write error copy and lookup debounce (E-44, S1-20).
- **DQ-7** Slack failure retry/backoff and dead-letter logging (E-40).
- **DQ-8** Canonical event/endpoint names for §5 data-capture events (semantic names given in §3; literal API naming free).
