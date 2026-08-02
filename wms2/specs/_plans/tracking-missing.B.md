# PLAN — tracking-missing (Unrecognized Tracking) · LENS B (Developer & QA)

Planner: B (functional precision · edge cases · QA acceptance criteria). Sources read: spec-template.md, global-rules-draft.md, slack-routing.md, decision-sources.md, wireframe `wms2/tracking-missing/index.html` (SST, v2 simplified), ledgers 2026-07-09 + 2026-08-02 (grep: tracking-missing / 미인식 / 스펙 필수 반영). Live: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/tracking-missing/

---

## 1. LEGEND INVENTORY

Single state (s1) + one modal (M1). Legend numbers 0–5 + M1 = 7 implementation units. All must appear in template §3.

| # | What it is | Spec treatment |
|---|---|---|
| **0** | New admin page itself — "WMS - Unrecognized Tracking List"; replaces manual set-aside of no-tracking orders. Coupang creates order no. instantly, tracking no. hours later → unrecognized/unentered items collected here. | §1 Purpose (operational moment: barcode scan failed in View Orders, physical product in hand at center) + §2 map row. Spec exact page title/subtitle text (QA anchors). |
| **1** | **Unrecognized product pool** (yellow `row-hit` table) — 12 columns: Tracking No / Order No / Product Name / Product Name KR / Size / Barcode / Qty / Memo / Registrant (Center) / Registered At / Suspected Orders (Auto-matched) / Action. Header card `poolhead` with live count `#poolCount`; bottom count `#poolCountBottom`. Tracking no. auto-collected at scan time; Order No mostly "–" (lookup-matched items never reach pool). Sole entry point = View Orders unrecognized-send popup (in-page register button/modal removed 07-23; also serves unrequested inbound arrivals, confirmed 08-02). | §3 [L-1]: column-by-column data contract (source of each field, "–" semantics, memo optionality), row ordering rule, count sync invariant (top = bottom = row count), read-only vs actionable cells. §5: row-creation event (from View Orders) referenced, not restated. |
| **2** | **Suspected Orders (auto-matched) column** — barcode→product comparison; candidates ONLY when an order (a) contains the product AND (b) is in Processing; multiple possible; mostly non-Coupang JIT (Naver/Official Mall). At registration, #unrecognized-tracking Slack message @mentions the suspected PICs. UX inversion 2026-07-23: system proposes, handler confirms. | §3 [L-2]: exact candidate predicate (product match key = barcode→SKU; status = Processing only; no channel filter but Coupang effectively excluded upstream), rendering format per candidate (`PIC · Order NNNNNN · route (channel) · Processing`), recompute timing (page load + M1 open — dev-decide details), empty-candidate rendering. §6: registration-time Slack payload (owned by view-orders spec; this spec covers the @mention-suspected-PICs delta). |
| **3** | **"Review & Match" button → M1** + row **✕** remove. Match is to a **product line**, not order-level. No manual PIC search (fallback removed 07-23 — "if it is not here, the data is wrong"). On confirm: tracking no. registered onto that order's product line → item removed from pool → auto comment on the order @mentioning the registrant ("Matched the unrecognized product … to this order") → Slack notification. ✕ = remove from list (mis-registrations, no-action items, and the unrequested-inbound handoff step). | §3 [L-3]: two sub-actions specced separately. Match: trigger, server action (write tracking to line — makes rescan resolve, mandatory item 6), state transition (pool→resolved), idempotency [G-9], toast [G-2] exact text, comment/Slack side effects [G-7]. Remove: immediate client removal per wireframe, server soft-delete + audit event [G-8], precondition narrative for the inbound-stock route. §7 carries the concurrency/duplicate cases. |
| **4** | Brand always bold-prefixed on Product Name (EN and KR columns) — inherits View Orders decision B [G-6]. | §3 [L-4] one-liner citing [G-6]; QA checks `<b>` brand render in both name columns. |
| **5** | Comments hub (top-right): [@ Mentions] + [★ Saved] + full-text search, unread badge, click opens order [G-7]. | §3 [L-5]: cite [G-7], page delta only = pool-related mention entries reference "Unrecognized pool" as entity (not an order no.) — click target for pool-entity comments must be defined (this page vs order). Badge/tabs/star behavior by reference. |
| **M1** | Review & Match modal — item summary card (product, barcode, tracking, "No order number", qty, registrant+time, memo), green candidate table (Order / PIC / Channel / Included Product / [Match to this product]), consequence note, Cancel. Overlay-click and ✕ close. | §3 [L-M1]: full I/O spec — every displayed field's source, per-candidate-line match button behavior, close paths (3) all side-effect-free, stale-candidate revalidation on confirm. |

Non-legend UI that still needs §3 coverage (will be attached under nearest legend ID, not new numbers): success toast `#matchToast` (fixed top-right, 4s auto-hide, two-line text) → under [L-3]/[G-2]; pool empty state (0 items — not drawn in wireframe, must be specced) → under [L-1]/§7.

Dead artifacts in the wireframe file that must NOT be specced (flag in §9 so devs don't implement removed v1 features): unused CSS/JS for `.trk` inline inputs, `.wait` chips, `.slack-pill`, per-PIC group classes (`picava`/`picname`/`cntchip`), "Resolved button" JS — all remnants of the pre-07-23 design (group tables, bulk bar, Slack column, resolved log, search bar: all removed 2026-07-23). Photo column deleted (07-21 hold → 08-03 deletion confirmed, sweep item 15).

---

## 2. SECTION OUTLINES (10 template sections)

**§1 Purpose & Users** — Who: order-team PICs (Dean/Egita/Harshit/Miranti as handler personas) resolving matches from desk; center staff (registrants) only as upstream actors. Moment: physical product exists but no order linkage; Coupang tracking-number lag is the root cause; pool is the single shared holding area (also for unrequested inbound stock, 08-02). Explicitly: this page has NO scan surface — scanning lives in View Orders (so [G-1] N/A here, stated to preempt confusion).

**§2 Screen Inventory & Wireframe Map** — 2 rows: s1 (default, no navigation needed) and M1 (reach via any row's "Review & Match" or top-bar "Modal: Match Review (M1)" button). Legend 0–5 + M1 ↔ §3 anchors 1:1. Live URL above.

**§3 Functional Specification** — per §1 inventory table. Key precision items B will enforce in drafting review:
- [L-1] count invariant (`#poolCount` == `#poolCountBottom` == visible rows) after every mutation (match, ✕, new arrival).
- [L-2] candidate predicate written as a testable rule: `order.status == Processing AND order.lines.any(line.product.barcode == pool_item.barcode)`; multiple candidates rendered in registration order; zero candidates → explicit rendering (open Q3).
- [L-3] Match server action sequence (atomic): (1) validate candidate order still Processing + line exists + pool item still open → (2) write tracking no. to product line (same field the View Orders scan path reads, so rescan resolves — mandatory 6) → (3) close pool item → (4) post comment with @registrant → (5) Slack notify. Steps 4–5 are non-blocking side effects (failure never rolls back 1–3, but is recorded). Idempotency key = pool_item_id + line_id [G-9].
- [L-3] ✕: client removes row immediately (wireframe behavior); spec adds server soft-delete + captured actor/timestamp [G-8]; whether reason/confirm is required = open Q1.
- [L-M1] all three close paths (Cancel, header ✕, overlay click) side-effect-free; confirm button exact label "Match to this product".
- Buttons table: "Review & Match" (always enabled while row open), "✕" (always enabled), "Match to this product" (per candidate line), "Cancel". Toast exact strings from wireframe: `✓ Matched to Order {n} · {product}` / `Tracking {trk} registered · removed from pool · @{registrant} notified via Slack`.

**§4 Business Rules** — with dates: single entry point = View Orders popup (07-23); matching UX inversion (07-23); manual PIC search removed (07-23); match target = product line not order (08-03 footnote d09fe79); candidates = contains-product + Processing only (07-23); Coupang items pre-filtered by order-no lookup (07-23); unrequested inbound arrivals reuse this pool, separate register path rejected (08-02); order no. format = Coupang purchase order no. (12101316464794-style, 07-23); no search bar/pagination by design — pool expected to hold only a few items (07-23); photo capture removed (07-21→08-03). Cite [G-2][G-6][G-7][G-8][G-9]; deltas only.

**§5 Data Capture [G-8]** — events this page persists (A-lens owns the full enumeration; B will verify these minimum rows exist): match_confirmed (actor, ts, pool_item_id, tracking_no, order_id, line_id, candidate_set snapshot), pool_item_removed (actor, ts, pool_item snapshot, reason if Q1 approved), match_comment_posted, slack_notify_sent/failed (with retry outcome), M1_opened (optional — dev-decide), candidate recompute results (old/new candidate set when it changes). Resolved-log UI was removed 07-23 but the DATA is retained admin-side (view over persisted events, [G-8]) — UI-less retention stated explicitly.

**§6 Integrations** — Slack routing table (from `_slack-routing`, both CONFIRMED): row 1 registration → #unrecognized-tracking (payload: tracking no., product, qty, memo, registrant, suspected orders; @mentions suspected PICs) — fired by View Orders, displayed-context here; row "Match confirmed" → comment auto-post + @registrant → #fulfillment-admin-comments `C0BMGEWM5QA`. Cross-page links: candidate Order numbers → order page deep link [G-12]; comment click → order page; inbound-stock route → inbound-request page (narrative link). No print pipeline on this page ([G-4] N/A). No sheet/BI handoff.

**§7 Edge Cases & Error States** — full [E-n] catalog below (section 3 of this plan).

**§8 QA Acceptance Criteria** — plan below (section 3): ~48 Given/When/Then scenarios keyed to [L-n]/[E-n], selectors/labels/toast strings from the live wireframe; cross-page scenarios flagged as running against view-orders wireframe.

**§9 Out of Scope & Open Questions** — out: scan surface & registration popup (view-orders spec), print, photo upload (removed), per-PIC group tables/bulk bar/resolved log/search bar (removed 07-23 — listed so nobody re-implements from stale docs), dead CSS/JS inventory. Open questions: section 5 below.

**§10 Decision Log** — dated: 07-09 page conceived (F Tracking Automation); 07-13 v1 (PIC groups etc.); 07-21 photo hold; 07-23 simplification (features removed list) + UX inversion + manual-search removal; 08-02 unrequested-inbound reuse decision (separate path rejected); 08-03 EN conversion (63 replacements), match-footnote = tracking written to product line + rescan resolves (d09fe79), send-confirm toast (d09fe79), photo column deletion confirmed (sweep item 15), #fulfillment-admin-comments channel confirmed.

---

## 3. LENS-B DEEP INVENTORY

### 3a. Edge-case candidate list [E-n] (exhaustive; §7 will keep all unless owner kills)

Registration/arrival (upstream boundary — specced here as pool-side effects):
- **E-1** Duplicate arrival: same tracking no. sent to pool twice (double-click on View Orders send [G-9], or genuine rescan of an unresolved item) → expect single pool row (server dedupe on tracking no.), second attempt gets "already in pool" feedback upstream.
- **E-2** Pool row arrives WITH an order number (registrant typed a Coupang no. but lookup failed, e.g. typo) → column shows the number instead of "–"; does it influence candidates? (display-only; candidates still by barcode predicate).
- **E-3** Tracking number could not be auto-collected (label destroyed) → can a row exist with empty Tracking No, and what would match register? (open Q5).
- **E-4** Product unknown to catalog → cannot happen by design (registration modal forces autocomplete pick); negative test lives in view-orders spec, cross-ref only.

Candidates / matching:
- **E-5** Zero suspected orders (no Processing order contains product) → column + M1 render an explicit empty state; sanctioned resolution path unclear (open Q3).
- **E-6** Candidate went stale: order left Processing (shipped/cancelled) between page load and confirm → M1 recomputes on open; confirm revalidates server-side → error toast `red` + candidate list refresh, no partial writes.
- **E-7** Concurrent handlers: two people open M1 for the same pool item; first confirms; second confirm → server rejects ("already matched"), row disappears on refresh, counts stay consistent.
- **E-8** Match vs ✕ race: handler A confirms match while handler B pressed ✕ → exactly one terminal state wins (server-side state check), loser gets error toast.
- **E-9** Double-click "Match to this product" [G-9] → exactly one line write, one comment, one Slack message (idempotency key).
- **E-10** Target product line already carries a tracking number → block with error (no silent overwrite) — validation rule to state.
- **E-11** Same tracking number already registered on a different order line anywhere in the system → server uniqueness check → error.
- **E-12** Qty mismatch: pool Qty=2 (medicube 1+1 row exists in wireframe) vs candidate line ×1 → allow / block / split? (open Q2 — wireframe silent).
- **E-13** Same SKU on two lines of one candidate order → M1 lists per LINE (grammar "match by product line" implies both lines appear); disambiguation rendering.
- **E-14** Pool item matched, then the matched order is later cancelled → tracking stays on line; out-of-scope here, cross-ref order-detail/View Orders cancel spec; note only.
- **E-15** Rescan after match: scanning the same barcode/tracking in View Orders now resolves normally (mandatory 6) — cross-page test.

Removal (✕):
- **E-16** ✕ with no confirm dialog (wireframe behavior) → accidental-tap risk; audit event must capture full row snapshot [G-8]; confirm/reason = open Q1.
- **E-17** Unrequested-inbound route: ✕ pressed BEFORE inbound request + invoice entry were completed → item vanishes with no recovery path visible; expected order of operations must be stated (create request → enter invoice → ✕ → rescan enters State 6); guard is procedural unless owner wants a hard check (open Q1/Q4).
- **E-18** ✕ on a row another user just matched → E-8 mirror.

UI / state consistency:
- **E-19** Empty pool: 0 items → poolhead shows "0 items", table shows an empty-state row (text TBD by A/B in draft), bottom line "0 items"; no layout collapse.
- **E-20** Count invariant after every mutation: `#poolCount` == `#poolCountBottom` == rendered rows (wireframe already decrements both).
- **E-21** New pool item arrives while page open → appears without full-page refresh [G-2]; mechanism dev-decide (poll/push); counts update.
- **E-22** Toast stacking: two matches < 4s apart → toasts stack or queue, never overwrite silently mid-read (dev-decide pattern, QA asserts both texts appear).
- **E-23** Toast auto-dismiss at 4s (wireframe constant) and is not click-blocking (position fixed, top-right).
- **E-24** Modal close paths (Cancel / header ✕ / overlay click) → zero side effects, pool unchanged.

Network / integration failure:
- **E-25** Network failure mid-match (request sent, no response) → button enters pending state, retry with same idempotency key is safe [G-9]; UI shows error toast on timeout, row NOT removed until server confirms.
- **E-26** Comment post or Slack notify fails after successful line-write → match still stands (steps are non-blocking), failure persisted [G-8] and retried; QA negative asserts row removed + error surfaced in log, not a rollback.
- **E-27** Registrant deactivated (left company / no Slack mapping) → comment posts with plain-text name, Slack mention degrades gracefully, no hard failure.
- **E-28** Pool fetch fails on page load → error state with retry, not a blank page.

Permissions / scale:
- **E-29** Who may match / who may ✕ → any operator per current design; permission gate = open Q6.
- **E-30** Pool unexpectedly large (>20 rows; design assumes "a few") → plain scroll, no pagination/search by 07-23 decision; render performance note; NOT a reason to re-add the search bar.
- **E-31** Comments hub: pool-entity mention ("Unrecognized pool" · Miranti's memo comment) click target — order-less entity; where does click navigate? (open Q7, small).

Printer offline: N/A (no print on page — stated in §9 so the template checklist item is answered, not skipped).

### 3b. QA scenario plan (template §8) — per-section counts, ~48 total

Written for an AI agent against the live wireframe: exact labels ("Review & Match", "Match to this product", "Cancel"), selectors (`#poolCount`, `#poolCountBottom`, `#poolrow1`, `#m-match`, `#matchToast`, `.xdel`, `.row-hit`, `#inbox1`, `.badge-n`), exact toast strings. Cross-page and real-admin-only checks tagged `[wireframe-N/A → admin]`.

| Block | Keyed to | Count | Notes |
|---|---|---|---|
| Page load & inventory | L-0, L-1 | 5 | title "WMS - Unrecognized Tracking List", subtitle text, 12 column headers exact, 3 seed rows, poolhead count 3 = bottom 3 |
| Pool row content | L-1, L-4 | 6 | tracking/barcode tabular values, Order No "–" gray, EN name brand `<b>COSRX</b>`, KR name brand bold, Memo "–" vs text, Registered At format |
| Suspected orders column | L-2 | 4 | 2-candidate row renders both lines (Dean/414230 + Egita/413871), 1-candidate rows, format `PIC · Order n · route (channel) · Processing`, order no. styled blue/bold |
| M1 open & content | L-3, M1 | 7 | opens via row button AND wf-bar button, header text, summary card 6 fields exact, candidate table headers (Order/PIC/Channel/Included Product), JIT tag plain bold black [G-5], consequence note text, Cancel/✕/overlay close → modal closed + row count unchanged (E-24) |
| Match happy path | L-3, E-20 | 6 | click "Match to this product" → modal closes, `#poolrow1` removed, both counts 3→2, toast visible with exact 2-line text, toast gone ≤4.5s, [admin] line-write + comment + Slack asserted via log |
| ✕ removal | L-3, E-16, E-20 | 4 | ✕ removes row, counts decrement, no toast (wireframe) vs [admin: audit event exists], repeat on second row |
| Comments hub | L-5 | 6 | badge "3", Mentions pane 4 items, tab switch to Saved (1 item), star toggle on/off, "Mark all read" present, pool-entity item text renders |
| Idempotency & concurrency (negative) | E-1, E-7, E-8, E-9, E-25 | 5 | double-click match = single removal/single toast; [admin] second-session confirm rejected; match-vs-✕ race; retry-after-timeout no dup |
| Validation negatives | E-6, E-10, E-11, E-12 | 4 | [admin] stale candidate rejected + red toast; occupied line blocked; duplicate tracking blocked; qty-mismatch behavior per Q2 resolution |
| Empty / error states | E-5, E-19, E-28 | 4 | zero-candidate rendering, empty pool after clearing all 3 rows (counts 0, no layout break), load-failure state [admin], no-refresh on all mutations [G-2] |
| Cross-page | E-15, E-17, mandatory 6 | 3 | `[cross-page: view-orders]` rescan of matched barcode resolves; unrecognized-send creates pool row + #unrecognized-tracking; inbound-stock ✕-then-rescan enters State 6 |
| **Total** | | **~48** | negatives ≈ 13 of 48 |

### 3c. Three fully-worked example scenarios

**QA-M1-05 (happy-path match — L-3, E-20, G-2)**
Given the live wireframe is freshly loaded and `#poolCount` reads "3"
When I click the "Review & Match" button in the first pool row (`#poolrow1`)
Then the modal `#m-match` gains class `open` and its header reads "Review & Match — Unrecognized Product"
When I click the first "Match to this product" button (row Order 414230 / Dean)
Then `#m-match` no longer has class `open`
And `#poolrow1` is absent from the DOM
And `#poolCount` reads "2" and `#poolCountBottom` reads "2"
And `#matchToast` is visible with text containing "✓ Matched to Order 414230 · COSRX Snail 96" and "Tracking 10323100841207 registered · removed from pool · @Miranti notified via Slack"
And within 4.5 s `#matchToast` is hidden
And no full-page navigation/refresh occurred [G-2].

**QA-NEG-02 (double-click idempotency — E-9, G-9)**
Given the modal `#m-match` is open for pool item with tracking 10323100841207
When I dispatch two click events on the same "Match to this product" button within 200 ms
Then exactly one pool row is removed and `#poolCount` decrements by exactly 1 (3→2, not 3→1)
And exactly one `#matchToast` display cycle occurs
And [admin] the order's comment history contains exactly one "Matched the unrecognized product" comment and #fulfillment-admin-comments received exactly one message (idempotency key = pool_item_id + line_id).

**QA-XDEL-01 (row removal — L-3, E-16, E-20)**
Given `#poolCount` reads "3"
When I click the "✕" button (`.xdel`, title "Remove from list") in the second pool row (Anua toner, tracking 10323100838455)
Then that row is absent from the DOM without any confirmation dialog (current wireframe behavior — subject to open Q1)
And `#poolCount` and `#poolCountBottom` both read "2"
And no toast is shown (wireframe); [admin] a pool_item_removed audit event exists with actor, timestamp, and full row snapshot [G-8].

---

## 4. MANDATORY-INCLUSION MAP (of 12)

| # | Item | Lands here? | Where |
|---|---|---|---|
| 2 | Global confirmation toast [G-2] | YES | §3 [L-3] match toast (exact strings), §7 E-22/E-23; ✕-removal toast gap flagged in Q1 |
| 6 | **Unrecognized matching behavior** (match writes tracking onto product line; rescan resolves) | YES — primary owner is this page (shared with view-orders) | §3 [L-3] server action seq, §4 rule (08-03 d09fe79), §8 cross-page scenario QA-XPG-01 |
| 12 | Comment @mention Slack routing [G-7] with named channel | YES | §3 [L-5], §6 routing table (#unrecognized-tracking + #fulfillment-admin-comments `C0BMGEWM5QA` — both CONFIRMED, no pending decision remains) |
| 1 (G-1 scanner), 3 (G-3 audio), 4 (G-4 print), 5/13 (samples), 7 (G-10), 8 (RTO KR), 9/10 (G-14), 11 (JIT residual) | — | N/A on this page | §1/§9 state N/A explicitly (no scan surface, no print, no outbound button); [G-10]/unrequested-inbound only as cross-ref narrative to inbound-request spec |

Also applied globally though not in the 12-list: [G-8] data capture (§5), [G-9] idempotency (§3/§7), [G-6] naming (§3 [L-4]), [G-12] deep links (§6).

## 5. OPEN QUESTIONS

**Owner must decide (do not invent):**
- **Q1** — ✕ removal is currently one click, no confirmation, no reason, no toast. Should it require (a) a confirm dialog, (b) a mandatory reason (mirroring [G-11] qty-edit reasons), and/or (c) a [G-2] confirmation toast? Tension: [G-2] says EVERY confirming action toasts; [G-8] wants the "why" captured; wireframe shows none of the three.
- **Q2** — Qty mismatch on match: pool item Qty=2 (medicube row) vs candidate line ×1 — allow match regardless of qty, block, or partial/split? Wireframe is silent; affects [L-3] validation.
- **Q3** — Zero-candidate pool item: manual PIC search was removed ("if it is not here, the data is wrong"). What is the sanctioned resolution path when Suspected Orders is empty — wait for candidate recompute, ✕ remove with memo, or a data-fix escalation route?
- **Q4** — Unrequested-inbound handoff (E-17): keep the order of operations purely procedural (create request → invoice → ✕ → rescan), or add a hard guard (e.g., ✕ warns when memo says "suspected inbound stock" and no matching inbound request exists)?
- **Q5** — Can an item enter the pool with NO tracking number (label destroyed so auto-collection failed)? If yes, what does "match" register on the product line?
- **Q6** — Permissions: may any operator match and ✕, or restrict ✕ (destructive) to admins/registrant?
- **Q7** — Comments-hub entries whose entity is "Unrecognized pool" (not an order): click navigates where — this page, or the pool row?

**Developer decides at build time (flag in §9, no owner input needed):**
- Candidate recompute mechanism/frequency (server query on page load + M1 open; cache policy).
- Pool live-update transport (polling interval vs push) satisfying no-refresh [G-2].
- Idempotency key format and dedupe window [G-9]; Slack/comment retry policy (non-blocking, logged).
- Toast stacking/queueing pattern for rapid successive matches.
- Rendering beyond the expected small pool (plain scroll; NO pagination/search — 07-23 decision stands).
- Cleanup of dead wireframe CSS/JS (`.trk`, `.wait`, `.slack-pill`, PIC-group classes) — do not implement.
