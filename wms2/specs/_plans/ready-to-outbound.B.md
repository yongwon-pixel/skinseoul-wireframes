# Plan — ready-to-outbound (Ready to be Outbounded) · LENS B: Developer & QA

Planner: B (functional precision · edge cases · QA acceptance criteria). Complements Lens A (operator/data).
Sources read: spec-template.md · global-rules-draft.md · slack-routing.md · decision-sources.md · `wms2/ready-to-outbound/index.html` (SST, legend = implementation units) · decision ledgers 2026-07-09 / 2026-08-02.
Live wireframe: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/ready-to-outbound/

---

## 1. LEGEND INVENTORY (15 units: dots 1–14 + M1 — all present on this page)

| # | What it is | Spec treatment (template section · what must be specified) |
|---|---|---|
| 1 | Per-row checkboxes + "Select all"; the 3 bulk buttons display live counts of selected orders AND items | §3 [L-1]: selection model (per-row, select-all scope, count recomputation feeding button labels 2/3/4), enabled/disabled conditions of bulk buttons at 0 selected; §7 selection×tab-filter edge cases; §8 selection scenarios |
| 2 | "🖨 Print Pick Locations (N orders · M items)" — opens Picking List modal M1; Print → progress → toast; location-ascending | §3 [L-2]: trigger, count derivation (orders/items), modal open, print pipeline [G-4], no-refresh + selection kept [G-2 delta]; §6 print pipeline; §8 modal + sort assertions |
| 3 | "🖨 Bulk Print Labels (N orders)" — prints shipping labels for all selected orders in one go | §3 [L-3]: batch print server action, carrier-agnostic instant output [G-4], per-order label job fan-out, idempotency [G-9], no refresh, selection kept; label LAYOUT itself deferred to Phase 3-1 (reference only) |
| 4 | "📦 Bulk Outbound (N orders)" — outbounds selected orders; **refreshes after completion** (designed exception to no-refresh) + **send sound on execution** [G-3a] | §3 [L-4]: state transition INBOUNDED→OUTBOUNDED per line, server action, idempotency key [G-9], the G-2 exception, sound spec (Web Audio synth, wireframe JS `sndOutbound()` is the reference implementation); §5 outbound events; §8 sound+refresh+toast scenarios |
| 5 | 0–100% progress bar **shared by buttons 2/3/4**; label text states mode ("No refresh · selection kept" vs "refreshes after completion") | §3 [L-5]: progress semantics (client display over batch execution), which action owns the bar, concurrent-start lockout; §7 double-start edge; §8 label-text assertions |
| 6 | Completion notice = top-right green toast, auto-dismiss after a few seconds; **no failure case in wireframe (all-success normal, 07-22 decision)** | §3 [L-6]: toast text pattern "✓ {Action} complete — {N} orders" [G-2]; §7/§9: real-admin partial-failure behavior is an OPEN QUESTION (wireframe removed failure UI by design — do not invent) |
| 7 | JIT order fully inbounded but Outbound not yet clicked = yellow row tint + **"Fully Inbounded"** badge (wording changed 2026-08-03), always sorted to bottom | §3 [L-7]: badge trigger condition (all lines inbounded ∧ not outbounded ∧ JIT), sort invariant; §4 business rule with 08-03 date; §8 tint/badge/sort scenarios |
| 8 | Manually imported Marketing order = purple tint + MKT badge; sorted between regular Ready and JIT; **shown immediately on import regardless of stock/inbound status**; non-inbounded items show amber "Not inbounded" pill instead of location; shows PIC | §3 [L-8]: visibility rule delta vs "≥1 INBOUNDED line" page rule, pill rendering, PIC field source (Order Management import); §7 MKT-with-zero-inbounded-items in bulk actions; §8 scenarios |
| 9 | Per-row Comments button → inline comment panel under the row; @mention → Slack | §3 [L-9]: expand/collapse, Post action, @mention payload [G-7], unread badge on button; §5 comment events; §6 Slack routing → **#fulfillment-admin-comments** (CONFIRMED); §8 scenarios incl. panel-vs-tab-filter behavior |
| 10 | Top-right Comments hub — @ Mentions / ★ Saved tabs + full-text search (order no./author/text, newest first), badge = unread count | §3 [L-10]: [G-7] with page deltas only (search behavior, mark-all-read, outside-click close, click→open order); §8 search/highlight/ordering scenarios |
| 11 | Reduced side padding — full-width layout (same principle as View Orders) | §3 [L-11]: one-line layout rule; §8 single presence check |
| 12 | **Pick Locations column** (new) — per-item locations stacked at same eye level as Ready Item Details; warehouse stock = location pill, fully-inbounded JIT = shelf number; Ready Items column removed as duplicate | §3 [L-12]: row-to-row alignment contract with Ready Item Details lines, pill variants (location / "Shelf N" / amber "Not inbounded"); §7 missing-location edge; §8 alignment scenarios |
| 13 | **Total Items = total quantity sum** (was SKU count; ×5 order must read 5, not 1) | §3 [L-13]: computation = Σ(qty of ready lines) — must state whether non-inbounded MKT lines count (see OQ-B2); §8 exact-value assertions per sample row |
| 14 | **View tabs** All / Inventory / Marketing / JIT — filter by order type, linked to "Found N order(s)" count | §3 [L-14]: filter predicate per tab, count text update, comment-row collapse on switch (wireframe behavior), default = All; §8 per-tab scenarios |
| M1 | Modal "Print Pick Locations — Picking List" — header with (N orders · N SKUs · N units), table Location/SKU/Product/Qty/Order sorted location-ascending (A-02-13 → B-01-07 → Shelf 3), Korean product names [G-6], note block, Cancel + 🖨 Print | §2 modal row; §3 [L-M1]: row generation (one row per order×SKU — no cross-order merge, per wireframe), mixed-scheme sort rule (line locations before "Shelf N"), Print = [G-4] + progress + toast + modal close; §8 full modal scenario set |

Page furniture kept from actual admin (not numbered, must still be specified in §3 as fixed elements): page title spelling "Ready to be Outbonded" (deliberately preserved, legend footnote), Refresh button, "Found N order(s) with items ready for outbound" text, "How to use" block, Order ID link → order-detail [G-12], global sort regular Ready → MKT → JIT, one row per order, `readyToBeOutbonded` API mention.

---

## 2. SECTION OUTLINES (10 template sections — concrete content planned)

### §1 Purpose & Users
- Warehouse pickers/packers as primary users; morning batch flow: select → print picking list → pick along ascending route → bulk print labels → pack → bulk outbound.
- Physical context that shaped decisions: pickers navigate by KOREAN product names [G-6]; single-pass route drives location-ascending sort; distance-from-monitor drives toast + send sound [G-2][G-3a].

### §2 Screen Inventory & Wireframe Map
- Rows: main list (default), 4 view-tab states (All/Inventory/Marketing/JIT), modal M1, inline comment panel state, comments hub dropdown (mentions/saved/search states), progress-running state, completion-toast state.
- Each row: legend #s ↔ spec §3 anchor, live URL + how to reach (e.g., M1 via wf-bar button or legend-2 button; JIT view via tab click).

### §3 Functional Specification (per [L-n], Lens B core — see inventory table above)
For every L-item: trigger · exact behavior · inputs/outputs · validation · server action · state transitions · idempotency · user-visible feedback. Highlights beyond the table:
- [L-1] selection state machine: counts in three button labels recompute on every checkbox change; buttons disabled at 0 selected (exact disabled styling TBD by dev); select-all scope = currently visible (filtered) rows — flagged OQ-B4 for owner confirmation.
- [L-2/L-3/L-4] each defines: request payload (order IDs array + idempotency key), per-order execution order, progress reporting, completion toast text template, and G-4 print-agent handshake for the two print actions.
- [L-4] Bulk Outbound: transitions every INBOUNDED line of each selected order to OUTBOUNDED; the ONLY full-refresh action on this page (G-2 names this exception explicitly); send sound fires on click (execution start), reference synth params from wireframe JS (340→940Hz sine sweep + 1250Hz triangle ping, ~0.36s).
- [L-9/L-10] deltas only over [G-7]; exact placeholder text ("Write a comment — @mention sends an automatic Slack notification (order no. · text · time · author)") is part of the contract.
- Fixed elements: Refresh reload semantics (resets selection? → OQ-D flagged), Order ID deep link target `../order-detail/` [G-12].

### §4 Business Rules
- Page inclusion rule: order appears when ≥1 line is INBOUNDED (How-to text is normative) — EXCEPT MKT orders, which appear immediately on import regardless (2026-07-22 D+G decision).
- Sort invariant: regular Ready → MKT → fully-inbounded JIT (bottom), stable within groups (within-group order flagged as dev-decide).
- "Fully Inbounded" badge wording (2026-08-03, replaced "JIT (channel) completed" to avoid clash with colorless Sourcing Route labels [G-5]).
- Total Items = unit sum not SKU count (2026-07-22, picking accuracy rationale).
- Korean names in Ready Item Details + M1 (2026-08-03) [G-6]; EN+brand remains on order pages.
- No failure case in bulk-completion UI (2026-07-22) — wireframe-level decision; real-system failure policy = open question, not silently invented.
- G-2 exception: Bulk Outbound refreshes after completion (by design).

### §5 Data Capture [G-8]
(Lens A owns depth; B contributes the event list QA will assert against.) Minimum events: bulk_outbound_executed (actor, ts, order IDs, per-line old/new status), label_printed / labels_bulk_printed (actor, ts, order IDs, carrier, reprint flag), picking_list_printed (actor, ts, order set, SKU/qty snapshot), comment_posted (+@mention target), comment_starred/unstarred, mention_read/mark_all_read, refresh/view-tab usage optional. Reprint events must be distinguishable (comment sample "Reprinted the shipping label" shows reprints are normal ops).

### §6 Integrations
- Slack: comment @mention → **#fulfillment-admin-comments** (CONFIRMED 2026-08-03) with order no., text, time, author, @mentioned user, deep link. No other RTO-specific routes.
- Print pipeline [G-4]: local print agent (PrintNode-class), 3 print surfaces (row Print, Bulk Print Labels, M1 Print), carrier-agnostic (Deleo/YUN/future), zero browser dialogs.
- Cross-page: Order ID → order-detail; comments hub click → order; MKT rows originate from Order Management import (PIC field); JIT inbound status originates from View Orders State 6 flow.
- Closing linkage: outbounded orders become Closing's scan population (reference only).

### §7 Edge Cases & Error States → full candidate list in section 3 below (30 items E-1…E-30).

### §8 QA Acceptance Criteria → scenario plan + counts + 3 worked examples in section 3 below. Scenarios tagged [WF] (executable on live wireframe today) vs [ADMIN] (real-admin-only: server idempotency, actual print output, Slack delivery, concurrency).

### §9 Out of Scope & Open Questions
- Out of scope: label/invoice layout (Phase 3-1), order-detail outbound flow (own spec), inbound flows, pagination (not in wireframe — flagged), role/permission model (not defined anywhere — flagged, not invented).
- Open questions: section 5 below verbatim.

### §10 Decision Log (dated)
- 2026-07-22: real-capture rework — 5 sample orders; order-level rows; sort regular→MKT→JIT; Total Items=qty sum; Pick Locations column added / Ready Items removed; picking modal ascending; progress+toast with failure case removed; inline comment rows; Actions column reduced to Print (View Order button removed).
- 2026-08-03: JIT badge wording → "Fully Inbounded"; Ready Item Details + M1 → Korean names; send sound on Bulk Outbound; instant-print reconfirmed; scanner protocol N/A on this page (no scan input) — state explicitly to preempt QA confusion; global toast rule emphasized.
- 2026-08-03: comment mention channel #fulfillment-admin-comments confirmed.

---

## 3. LENS-B DEEP INVENTORY

### 3a. Edge-case candidate list (exhaustive, [E-n])

Selection & filtering
- **E-1** Zero selection: all 3 bulk buttons must be disabled (or no-op with explanatory state); counts read "(0 orders · 0 items)". Negative test.
- **E-2** Select-all scope vs view tabs: select-all on "Inventory" tab then switch to "All" — do MKT/JIT rows become selected? Expected: selection applies to visible rows only and persists per order across tab switches (pending OQ-B4).
- **E-3** Selection contains MKT order with an amber "Not inbounded" item: Print Pick Locations — that item has no location (excluded from M1? shown with "Not inbounded" row?); Bulk Outbound — eligibility (OQ-B2).
- **E-4** Selection contains fully-inbounded JIT order: M1 must render "Shelf N" rows and sort them AFTER line-based locations (A-… → B-… → Shelf 3).
- **E-5** Empty state: 0 ready orders — table empty, "Found 0 order(s)…", bulk bar disabled, no crash on select-all.
- **E-6** Refresh clicked with active selection and/or open comment panel: does selection/panel survive? (Wireframe silent — dev-decide, spec must state chosen behavior.)
- **E-7** Stale row: order outbounded/cancelled by another operator (from order-detail or concurrent RTO session) between load and bulk execute — server must reject/skip stale IDs; client behavior on mismatch.
- **E-8** Two operators run Bulk Outbound with overlapping selections concurrently — each order outbounded exactly once; loser gets defined feedback.
- **E-9** Double-click any of the 3 bulk buttons [G-9]: exactly one batch executes (client debounce + server idempotency key). Known current bug: double-click processes twice — regression test mandatory.
- **E-10** Network failure mid-bulk (request sent, response lost): retry with same idempotency key must not double-outbound/double-print; UI shows unresolved state, not false success toast.
- **E-11** Print agent offline/unreachable [G-4]: no silent success, no browser-dialog fallback; defined error surface (real-admin behavior pending OQ-B1 failure policy).
- **E-12** Print agent fails mid-batch (labels 1–2 printed, 3 fails): partial physical output vs all-success toast — reconciliation behavior (OQ-B1).
- **E-13** Order with mixed line statuses (some INBOUNDED, some not): appears on page (≥1 rule); M1 and Total Items must count ONLY ready lines vs all lines — spec must pin one (OQ-B2/OQ-B3).
- **E-14** Same SKU in multiple selected orders (same location): M1 keeps one row per order×SKU (no merge, per wireframe — Order column would be ambiguous otherwise); QA asserts two rows, not one summed row.
- **E-15** Warehouse item with no registered location (location deleted/unassigned in Inventory): Pick Locations cell fallback — must not render blank silently.
- **E-16** Comment failures: empty comment Post (blocked), @mention of unknown user (no Slack send, defined feedback), Slack delivery failure (comment persists; notification retry policy dev-decide).
- **E-17** Comment panel open, then view tab switched: panel rows collapse (wireframe behavior — crows forced hidden). QA-testable today.
- **E-18** Consecutive bulk actions before previous toast dismisses: toast replaced/stacked — define single-slot replacement (wireframe behavior).
- **E-19** Second bulk action started while progress bar is running: buttons must lock during execution (wireframe does not lock — real admin must; negative test on admin).
- **E-20** Bulk Outbound refresh destroys unsaved comment draft text: acceptable by design? Spec must warn or block — dev-decide with note.
- **E-21** MKT order with ZERO inbounded items selected for Bulk Outbound: must be blocked/excluded (nothing to outbound) — exact behavior OQ-B2.
- **E-22** Large selection (100+ orders): progress granularity, request chunking, no pagination exists on this page — scalability note + dev-decide chunk size.
- **E-23** Order ID link to an order that was cancelled/deleted after load: order-detail must handle; RTO shows stale row until Refresh.
- **E-24** Web Audio blocked/suspended (first user gesture, silent mode): sound failure must never block the outbound action (wireframe try/catch — normative).
- **E-25** M1 opened with 0 selected: header would read "0 orders selected · 0 SKUs · 0 units" — should be prevented by E-1 disable; negative test.
- **E-26** Unread badge desync: hub badge (2) vs per-row badges vs Mark-all-read — counts must reconcile after read actions.
- **E-27** Permission edge: no role model is defined anywhere in inputs — flag as open (owner), do not invent gating.
- **E-28** Sample-set order [G-13] in picking flow: internal picking artifacts must show WHICH sample and HOW MANY — does M1 include a sample row? (OQ-B5; shipping-label DELEO improvement includes a sample row, RTO M1 currently does not.)
- **E-29** Reprint (row Print or Bulk Print Labels on already-printed order): allowed; every print event captured with reprint flag [G-8].
- **E-30** M1 open while underlying data changes (another session outbounds order 422176): Print executes against stale snapshot — server-side revalidation on print? (ties to E-7; dev-decide with stated rule).

### 3b. QA scenario plan (Given/When/Then, keyed [L-n]/[E-n]) — estimated counts

| Spec area | Est. scenarios | Coverage notes |
|---|---|---|
| L-1 selection & counts | 6 | select one/all/none, 3-button label count sync, disabled-at-zero (E-1, E-25 negative) |
| L-2 + M1 picking modal | 9 | open (both entry points), header counts, column set, ascending sort incl. Shelf-after-lines (E-4), Korean names, per-order rows (E-14), Cancel, Print→progress→toast→no refresh→selection kept |
| L-3 Bulk Print Labels | 4 | label text, progress label "No refresh · selection kept", toast text, selection preserved after completion |
| L-4 Bulk Outbound | 6 | send sound fires, progress label "refreshes after completion", toast, refresh occurs (wireframe: demo semantics), idempotent double-click (E-9 [ADMIN]), state transition [ADMIN] |
| L-5 progress bar | 4 | shared by all 3 actions, 0→100 monotonic, per-action label text, single bar instance |
| L-6 completion toast | 3 | exact text "✓ {name} complete — 3 orders", top-right position, auto-dismiss ~3s (E-18 replacement) |
| L-7 JIT row | 3 | yellow tint class, badge text = "Fully Inbounded" (not old wording — negative), bottom sort position |
| L-8 MKT row | 5 | purple tint, MKT badge, PIC line "PIC: Harshit", amber "Not inbounded" pill in Pick Locations, sort between Ready and JIT |
| L-9 inline comments | 6 | expand/collapse, existing comment render (author/@/time), Post button present, placeholder text exact, unread badge on button, star toggle |
| L-10 comments hub | 7 | open/close (outside click), badge=2, tab switch Mentions/Saved, search match+highlight+newest-first, no-match empty state, Mark all read affordance |
| L-11 layout | 1 | full-width padding presence |
| L-12 Pick Locations column | 3 | per-item vertical pills, line alignment with Ready Item Details, Shelf pill for JIT |
| L-13 Total Items | 2 | 422221 shows 5 (not 1), 422165 shows 2 |
| L-14 view tabs | 5 | each tab → exact row set + "Found N order(s)…" text (All=5/Inv=3/Mkt=1/JIT=1), comment rows collapse on switch (E-17) |
| Page fixed elements | 4 | title spelling, Refresh present, How-to text, Order ID link + sort order of the 5 sample rows |
| Edge negatives (E-keyed, mostly [ADMIN]) | 12 | E-5, E-7, E-8, E-10, E-11, E-12, E-15, E-16, E-19, E-21, E-24, E-29 |
| **Total** | **≈80** | ~55 executable on live wireframe today [WF], ~25 real-admin-only [ADMIN] |

### 3c. Three fully-worked example scenarios

**QA-L2-01 [WF] — Picking List modal opens sorted ascending with Korean names**
- Given: live wireframe loaded at `…/wms2/ready-to-outbound/`, default state (3 Inventory rows pre-checked).
- When: click the button labeled `🖨 Print Pick Locations (3 orders · 8 items)` in the bulk action bar.
- Then: overlay `#m-pick` gains class `open` (visible); modal header text equals `Print Pick Locations — Picking List (3 orders selected · 4 SKUs · 8 units total)`; the `.picktbl` tbody has exactly 4 rows; column 1 values in order are `A-02-13`, `A-03-02`, `B-01-07`, `B-02-11` (ascending); row 2 Product cell reads `마데카 크림 타이트닝` (Korean, [G-6]); row 1 Qty is bold `5` with Order `422221`; the note block contains `Sorted by location (ascending)`.
- Negative rider: header must NOT read a SKU count in place of unit count (4 SKUs ≠ 8 units distinction).

**QA-L4-01 [WF] — Bulk Outbound: sound + progress mode text + completion toast**
- Given: default state, 3 orders selected.
- When: click `📦 Bulk Outbound (3 orders)`.
- Then: (a) a send sound is triggered on click (wireframe proxy: click listener bound via `sndOutbound`; agent asserts an `AudioContext` is created after click, and asserts NO uncaught exception if audio is blocked — E-24); (b) `#pfill` width animates 0%→100%; (c) `#pbarLabel` text during run contains `Bulk Outbound in progress` AND `refreshes after completion` (NOT `No refresh · selection kept`); (d) at 100%, toast `#toast` becomes visible top-right with bold text `✓ Bulk Outbound complete — 3 orders`; (e) toast auto-hides within ~3–4s. [ADMIN rider: page then reloads and the 3 orders are gone from the list; re-clicking with the same idempotency key does not re-outbound (E-9).]

**QA-L14-02 [WF] — JIT tab filter + Found count + comment-row collapse (E-17)**
- Given: default state; first expand comment panel of order 422221 by clicking its row button `💬 1` (row `#crow1` becomes visible showing author `Egita`, mention `@Yongwon`, time `07-21 09:40`).
- When: click view tab `JIT`.
- Then: only the row with Order ID `422164` is visible; that row shows badge text `Fully Inbounded` and a yellow row tint (`row-jit`); its Pick Locations cell shows pill `Shelf 3`; `#foundTxt` text equals exactly `Found 1 order(s) with items ready for outbound`; `#crow1` is hidden (comment panels collapse on tab switch). Clicking tab `All` restores 5 order rows and `Found 5 order(s) with items ready for outbound`.

---

## 4. MANDATORY-INCLUSION MAP (of the 12, these land on this page)

| # | Item | Lands where in this spec |
|---|---|---|
| 2 | Global confirmation toast [G-2] | §3 L-6 (+ documented exception: Bulk Outbound refresh); §8 toast assertions |
| 3 | Audio feedback [G-3a] send sound | §3 L-4 (Bulk Outbound); §8 QA-L4-01; E-24 |
| 4 | **Instant carrier-agnostic print [G-4]** | §3 L-2/L-3/L-M1 + per-row Print button; §6 print pipeline; E-11/E-12 |
| 8 | **RTO Korean item names [G-6]** | §3 Ready Item Details + M1; §8 QA-L2-01 |
| 12 | Comment @mention Slack routing [G-7] | §3 L-9/L-10; §6 → #fulfillment-admin-comments (CONFIRMED 2026-08-03); E-16 |
| 5 | Sample dual-view [G-13] | Reference-only touchpoint: picking artifacts must expose sample kind+qty; M1 sample-row question raised as OQ-B5; layout deferred Phase 3-1 |

Not on this page: 1 (scanner — no scan surface here; spec states this explicitly), 6 (unrecognized matching), 7 (multi-tracking), 9/10/11 (Inventory items).

---

## 5. OPEN QUESTIONS

### Owner must decide
- **OQ-B1 (failure policy)**: Wireframe deliberately has no failure case for bulk actions (07-22). In the real admin, what happens when a bulk action partially fails (print agent dies mid-batch E-11/E-12, one order fails validation E-7)? Halt-and-report vs skip-and-continue with per-order result list? This decision gates §7 behaviors and several [ADMIN] QA scenarios.
- **OQ-B2 (Bulk Outbound eligibility)**: For orders with non-inbounded lines (MKT "Not inbounded" E-3/E-21, partial orders E-13) — is Bulk Outbound blocked for the whole order, allowed for inbounded lines only (partial outbound), or are such orders auto-excluded from the batch with a notice?
- **OQ-B3 (count semantics on mixed orders)**: Do Total Items [L-13] and the bulk-button item counts [L-1] count ONLY inbounded (ready) units or ALL units of the order? (Wireframe samples are unambiguous per-row but never mix; MKT-40233 shows Total 3 while one item is not inbounded — implies ALL units. Needs one-line confirmation.)
- **OQ-B4 (select-all scope)**: "Select all" = all rows in the current view tab only, or all ready orders regardless of filter? Does selection persist across tab switches?
- **OQ-B5 (sample rows in picking list)**: Should M1 / printed picking list include sample-set lines (which sample, how many) per [G-13] internal-view rule? Wireframe M1 has no sample row; shipping-label DELEO improvement does.
- **OQ-B6 (permissions)**: Is there any role gating on Bulk Outbound (vs print)? No role model exists in any input — needs an explicit "single admin role for now" or a gate.

### Developer decides at build time
- Toast auto-dismiss duration (wireframe ≈3s "a few seconds"); toast replacement on consecutive actions (E-18).
- Progress granularity (per-order increments vs smoothed %), batch chunk size for large selections (E-22), button lockout during a running batch (E-19 — must exist; mechanism is dev's).
- Idempotency key format + client debounce interval [G-9] (behavior is mandatory; format is dev's).
- Mixed-location sort comparator detail (line-based `A-02-13` lexicographic, `Shelf N` group sorted after all line locations, numeric N ascending).
- Refresh semantics for selection/open panels (E-6) and comment-draft loss on outbound refresh (E-20) — pick and document.
- Fallback rendering for missing location (E-15), Slack retry policy on delivery failure (E-16), AudioContext resume handling (E-24).
- Comments search debounce and result cap; stale-snapshot revalidation rule on M1 Print (E-30).
