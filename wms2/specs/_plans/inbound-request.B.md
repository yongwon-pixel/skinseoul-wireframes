# Inbound Request — Spec Plan, LENS B (Developer & QA)

Planner: B (functional precision · edge cases · QA acceptance criteria).
Wireframe SST: `wms2/inbound-request/index.html` (851 lines, read in full) · live `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/inbound-request/`.
Legend key proposal for the spec: `[L-S1-n]` (State 1), `[L-S2-n]` (State 2), `[L-S3-n]` (State 3), `[L-M1]` (modal). State 1 numbering **skips 13** (dot retired with the removed "View Orders link info" modal, 2026-08-03) — the spec will state the gap explicitly so nobody hunts for a missing item.

---

## 1. LEGEND INVENTORY (28 items — every dot on the page)

### State 1 — New Request (Smart Buy) · 15 items
| # | What it is | Spec treatment |
|---|---|---|
| S1-1 | New Inbound Request screen = single intake gateway for ALL warehouse inbound | §1 Purpose + §3 intro; §4 rule "no inbound path bypasses this form" |
| S1-2 | Sourcing Route radio cards ×4 (Smart Buy / Wholesale / Brand Partnership / Other+free-text) | §3: selection behavior, exactly-one invariant, Other enables+focuses `.etc-in`; validation (Other ⇒ channel name required); cite [G-5] + page delta ("Other" is a form-level 4th option feeding the same 4-route taxonomy) |
| S1-3 | Inbound No. auto-assign YYYYMMDDNNNN (0001–9999/day), no form field, shown only in Request List | §3: server action at registration, uniqueness under concurrency, [G-9] idempotency (double submit ⇒ ONE number); maps to PH sheet col A |
| S1-4 | Field set aligned to PH sheet column order; SKU·Brand·Name locked from search; no Size | §3 field table (name, type, required, source, editable?) + §6 sheet handoff |
| S1-5 | Single unified search box (SKU No. · brand · EN product name autocomplete) | §3: input→suggestion→row-append flow, keyboard behavior (Enter must NOT submit the form — G-1-adjacent delta), debounce, no-result state (→E-11) |
| S1-6 | Picked product appended as blue-tinted row; SKU/Brand/Name readonly; fix = delete row (✕) + re-search | §3: row lifecycle, readonly enforcement, ✕ delete; duplicate-SKU policy (→OQ-2) |
| S1-7 | Tracking No field — optional, dashed border, single unified Register button | §3: registers as REQUESTED with/without tracking; if provided ⇒ View Orders matching active immediately [G-10] |
| S1-8 | Expected arrival date | §3: optional/required?, format, past-date policy (→E-17/OQ-8) |
| S1-9 | Purple note: tracking entry auto-matches View Orders, scans show route badge | §3 informational element + §6 cross-page contract (link modal removed 08-03 — do not spec one) |
| S1-10 | Unit Cost (KRW) REQUIRED, 0 allowed (FOC); disclaimer text position moved 08-03 | §3 validation (required, ≥0, numeric w/ comma display); §4 rationale = FIFO costing basis; §10 decision 07-26 (FOC checkbox retired → direct 0) |
| S1-11 | JIT Price (KRW) OPTIONAL — "leave blank if unknown" | §3 validation (blank allowed, numeric if present); §10 decision 07-26 (all channels, optional) |
| S1-12 | Supplier REQUIRED ("who is shipping the goods") | §3 validation + settlement rationale [§4] |
| S1-14 | Top-right Comments hub (@Mentions / ★Saved / full search, unread badge) | §3 cite [G-7]; page delta = entities are inbound requests; QA on tab switch/star toggle |
| S1-15 | Reduced side margins — whole form fits one screen w/o scrolling | §3 one-liner (layout constraint, QA visual check) |
| S1-16 | In-admin page tabs [New Request \| Request List] (≠ wireframe purple state tabs) | §2 map + §3 navigation behavior; deep-link target of `#reqlist` [G-12] |

Off-legend behavior paragraph (State 1 footer) — MUST be specced: Received Date + Carrier recorded automatically at inbound, shown in Request List only (but see S3-10: Carrier column dropped 08-03 — footer sentence is partially stale, spec follows S3-10); Request List = the data Procurement Hub sheet will scrape as-is (sheet design deferred, §6/§9); label always "Comments".

### State 2 — New Request (Wholesale / Partnership) · 2 items
| # | What it is | Spec treatment |
|---|---|---|
| S2-1 | Direct routes get the same auto Inbound No. (list-only) | §3 delta row: identical to S1-3 — spec as "no behavioral difference by route" |
| S2-2 | Same product-entry spec; row 2 demonstrates FOC = Unit Cost 0 typed directly | §3: confirms 0-allowed path; QA positive test |
Footer: 3-stage status REQUESTED→PARTIAL→INBOUNDED (SHIPPED retired 07-27, PARTIAL added 08-02) — cite [G-11], dates to §10.

### State 3 — Request List · 10 items
| # | What it is | Spec treatment |
|---|---|---|
| S3-1 | Status filter chips All/REQUESTED/PARTIAL/INBOUNDED with counts; tracking presence is NOT a status | §3: filter semantics, count computation, single-select chips |
| S3-2 | Bulk bar pinned above table — "Bulk add tracking numbers" for selected rows; no manual INBOUNDED button (retired) | §3: selection model, enabled/disabled conditions (→E-25/26), opens M1-per-request or batch flow (define!) |
| S3-3 | Sourcing Route column — black bold badges [G-5] | §3 render rule only |
| S3-4 | Tracking No column — "Add tracking" button (→M1) when empty; number list (multiple) + match status when filled | §3: cell state machine (empty/filled/auto-switched) |
| S3-5 | Status column 3 stages; PARTIAL auto-switch on partial inbound save with n/m remaining; rescan resumes from remainder; qty-edit history shown in Qty cell (300→180) + Slack to requester | §3 + §4; state transitions diagram; [G-11]; qty edits originate in View Orders M6 (this page only DISPLAYS history — no edit affordance here) |
| S3-6 | REQUESTED + no tracking ⇒ morning Slack check (WHOLESALE·SMART BUY→#wholesale-ops / PARTNERSHIP→#partnership-kr; Other = TBD at dev) | §6 Slack table rows (CONFIRMED, daily 1×) + §9 open item for Other |
| S3-7 | Multiple tracking numbers per request (split shipments, 08-03) — every number is a match/scan target; badge stays REQUESTED | §3 [G-10] primary landing; QA cross-check with M1 |
| S3-8 | INBOUNDED = auto-switched by View Orders scan (link modal + result link removed 08-03) | §3: no manual transition on this page — negative QA (assert absence of any "mark inbounded" control) |
| S3-9 | Automation note (INBOUNDED via scans; scans surface route badge) | §3 informational; §6 cross-page contract |
| S3-10 | Received Date column auto-recorded at INBOUNDED (scan time); "–" before; **no Carrier column** (auto carrier recording unsupported, 08-03) | §3 + §5 (timestamp capture) + §10 decision |

### Modal · 1 item
| # | What it is | Spec treatment |
|---|---|---|
| M1 | Add Tracking No modal — multi-row input, ＋ Add tracking number, per-row ✕ (last row clears instead of removes), Save activates matching for EVERY number, status stays REQUESTED | §3 full functional contract: open triggers (row button, bulk bar), row add/remove semantics, save validation (→E-27/28/29), toast, [G-9] double-save safety |

Also spec-visible but not numbered: registration success toast (static `.toast` in S3 + live `#gtoast` behavior, [G-2]), per-row 💬 Comments expand panel (`.cpanel-ir`, IR_COMMENTS demo data), deep link `#reqlist`/`#s3` [G-12]. These get [L-x] sub-entries under S3-1/S1-14 or their own "unnumbered behaviors" block in §3 — planner A should mirror.

---

## 2. SECTION OUTLINES (10 template sections)

1. **Purpose & Users** — Single intake gateway claim (S1-1); users: order team/admins create requests (Yongwon, Dean, Miranti in demo data), warehouse center never transitions status here (scans in View Orders do); operator context: request creation is desk work (no scanner), so no G-1 surface — but Enter-key discipline still needed in the search box.
2. **Screen Inventory & Wireframe Map** — 4 rows: S1 (wf-tab "1 · New Request (Smart Buy)"), S2 ("2 · New Request (Wholesale / Partnership)"), S3 ("3 · Request List (Requested/Partial/Inbounded)", also `#reqlist`), M1 (wf-tab "Modal: Add Tracking No" or any "Add tracking" row button). Legend↔section 1:1 table incl. the S1-13 gap note and the two footer paragraphs.
3. **Functional Specification** — per the 28 items above. Deepest cuts (Lens B ownership):
   - **Registration server action**: input payload (route, channel-name-if-other, rows[{sku, qty, unit_cost, jit_price?}], supplier, tracking[]?, expected_arrival?, memo?), validation order, response (inbound_no), idempotency key = client-generated per form session [G-9]; success = toast `✓ Inbound request registered` + small `Inbound No. auto-assigned · added to the Request List · No refresh` [G-2], form reset policy (define), NO page refresh.
   - **M1 save action**: payload (request_id, tracking_numbers[]), dedupe/trim rules, response, toast `✓ Tracking number(s) saved` + small `Every registered number is now matched to View Orders · No refresh`; matching activation is atomic with save.
   - **State machine**: REQUESTED →(View Orders partial save) PARTIAL(n/m) →(exact-match full receipt) INBOUNDED; no reverse transitions on this page; expected-qty edit recomputes gating and can trigger PARTIAL→INBOUNDED if received==new expected (owner confirm, OQ-6).
   - **Numeric input contract**: comma-grouped display, integer parse; qty ≥1; unit_cost ≥0; jit_price blank or ≥0.
   - Buttons table: exact labels `Register Inbound Request` / `＋ New Inbound Request` / `Bulk add tracking numbers` / `Add tracking` / `＋ Add tracking number` / `Save tracking numbers` / `Cancel` / `✕` / `💬 Comments` / `Post`, each with enabled-conditions + effect + feedback.
4. **Business Rules** — Unit Cost required incl. 0 (FIFO basis, sheet consistency); Supplier required (settlement); no manual INBOUNDED (protects inventory truth — scans are the only transition); tracking optional at creation but morning-checked (S3-6); Request List is the sheet-scrape source (write nothing here that the sheet can't scrape); route taxonomy [G-5]; status ≠ tracking presence (S3-1).
5. **Data Capture** — Lens A owns depth; B contributes the event↔QA join: request_created, tracking_added(each number, actor, ts), tracking_removed(if allowed — OQ-5), expected_qty_edited(old/new/reason/actor — origin View Orders M6, displayed here), status_changed(auto, cause=scan ref), received_date_set, comment_posted/mention, memo_copied_to_comments, morning_check_fired, bulk_selection actions. Every event needs actor+ts+entity+old/new [G-8].
6. **Integrations** — Slack table (4 rows landing here: morning check ×2 CONFIRMED, @mention → #fulfillment-admin-comments `C0BMGEWM5QA` CONFIRMED, expected-qty edit auto-comment+@requester CONFIRMED); deep links: inbound `#reqlist` from View Orders State 6 banner [G-12], outbound = none (result link removed 08-03); PH sheet scrape (design deferred — §9); no print pipeline on this page (state explicitly: G-4 N/A).
7. **Edge Cases & Error States** — full [E-n] catalog below (§3 of this plan).
8. **QA Acceptance Criteria** — plan below, with wireframe-executable vs real-admin-only tagging (critical: the wireframe's filter chips/checkboxes are visual-only; QA doc must assert only what the wireframe actually does, and mark deferred assertions `[REAL-ADMIN]`).
9. **Out of Scope & Open Questions** — sheet integration design; label/print (none here); request edit/cancel/delete (absent from wireframe — OQ-1); Procurement Hub page; OQ list below.
10. **Decision Log** — dated: 07-23 page tabs + Inbound No. auto-assign + sheet-alignment + Received Date col; 07-26 preview panel removed, 4th route "Other", FOC checkbox→0, JIT all-channels-optional; 07-27 unified search box, single register button, SHIPPED retired, morning Slack spec; 08-02 PARTIAL added, qty-edit (M6) + history display, unrecognized pool reuse; 08-03 multi-tracking confirmed [G-10], link modal + result link removed, no Carrier column, disclaimer moved, M1 save toast added, EN pass (commit 890e909).

---

## 3. LENS-B DEEP INVENTORY

### 3a. Edge-case candidate list (46 candidates — final spec will confirm/merge)

**Form validation (New Request)**
- E-1 Submit with zero product rows → blocked, inline error, no server call
- E-2 Row with empty Order Qty → blocked, row highlighted
- E-3 Row with empty Unit Cost → blocked (required); E-4 Unit Cost = 0 → accepted (FOC)
- E-5 JIT Price blank → accepted; E-6 negative/non-numeric qty·cost·jit → rejected on input or submit
- E-7 Comma-grouped input ("15,000") → parsed as 15000; paste with spaces trimmed
- E-8 Route "Other" selected + empty channel name → blocked with focus to `.etc-in`
- E-9 Route switch after rows added → rows retained (route is request-level, not row-level)
- E-10 Supplier empty → blocked
- E-11 Search box: no autocomplete match → "no results" affordance, no row added, no crash
- E-12 Same SKU picked twice → policy TBD (OQ-2): merge qty vs second row vs block
- E-13 Attempt to type into readonly SKU/Brand/Name → no edit possible; only ✕+re-search
- E-14 All rows deleted after adding → returns to empty-table state, submit blocked (=E-1)
- E-15 Expected arrival in the past → policy TBD (OQ-8)
- E-16 Memo empty → no auto-comment created (memo→Comments copy only when non-empty)

**Registration & idempotency**
- E-17 Double-click `Register Inbound Request` → exactly ONE request + ONE Inbound No. [G-9]
- E-18 Network failure mid-registration → error state, form values retained, safe retry (same idempotency key ⇒ no dupe)
- E-19 Concurrent registrations (two operators, same second) → distinct sequential NNNN, no collision
- E-20 Daily sequence overflow (NNNN > 9999) → defined failure (practically unreachable; dev decides behavior, must not silently wrap)
- E-21 Tracking number provided at creation that already exists on ANOTHER request → duplicate policy TBD (OQ-4) — matching ambiguity in View Orders is the hazard
- E-22 Tracking number colliding with a customer-order (outbound) tracking number → scan disambiguation contract with View Orders

**Request List**
- E-23 Empty list / chip filter with 0 results → empty state text, chip count shows 0
- E-24 Bulk bar with 0 rows selected → `Bulk add tracking numbers` disabled (or no-op with message)
- E-25 Bulk selection including INBOUNDED rows → those rows excluded/blocked from tracking add
- E-26 New registration arrives while a status filter is active → appears only under matching chip; toast still fires
- E-27 Row with tracking: numbers render as list (S3-7 shows 2) + "all matching active" note; no Add button dupe
- E-28 INBOUNDED row → no "Add tracking" button; adding more numbers post-INBOUNDED policy TBD (OQ-7)
- E-29 Qty-edit history render (✎ 300→180 (damaged)) when an M6 edit exists; absent otherwise
- E-30 PARTIAL badge shows remaining n/m (e.g., PARTIAL 120/180) and updates after each View Orders partial save
- E-31 Deep link `#reqlist` (and `#s3`) → Request List tab active on load [G-12]

**M1 modal**
- E-32 Save with all inputs empty → blocked
- E-33 Same number entered twice within the modal → deduped or blocked with message
- E-34 Number already saved on this request re-entered → idempotent (no dupe row)
- E-35 Number already on a DIFFERENT request → cross-request duplicate policy (=E-21/OQ-4)
- E-36 Whitespace/hyphen handling → trim; charset validation must be carrier-agnostic (no single-carrier regex — carriers differ; cf. company lesson "no single-vocabulary parser")
- E-37 ✕ on the last remaining row → clears the value, row persists (wireframe behavior — spec as intended)
- E-38 Removing an already-saved number that ALREADY has scans against it → must be blocked or audit-logged (OQ-5)
- E-39 Two operators open M1 for the same request and save different sets → concurrency rule (server merge vs last-write-wins + stale warning)
- E-40 Network failure on save → modal stays open, values retained, retry safe [G-9]
- E-41 Double-click `Save tracking numbers` → one save, one toast [G-9]

**Cross-page & lifecycle**
- E-42 Expected-qty edit BELOW already-received qty → must be rejected in M6 (View Orders owns; this page must render whatever history results)
- E-43 Expected-qty edit to exactly the received qty → gating recompute; auto-INBOUNDED? (OQ-6)
- E-44 Same tracking rescanned after PARTIAL → reconciliation resumes from remainder, no double-count [G-11]
- E-45 Unrequested arrival (no matching request) → unrecognized pool route [G-11] — cross-ref tracking-missing spec, not owned here
- E-46 Toast overlap: two confirming actions within 2.6s → single toast element re-used, latest message wins, timer resets (wireframe `gtoastShow` behavior)

**Comments (page-delta of G-7)**
- (folded into QA rather than separate E-ns): empty comment post blocked; @mention of unknown name → no Slack fire; unread badge decrement on "Mark all as read".

### 3b. QA scenario plan (Given/When/Then, keyed [L-*]/[E-*])

Execution target = live wireframe first. Every scenario tagged `[WF]` (executable on the static wireframe: clicks, class toggles, toasts, modal DOM, deep link) or `[REAL-ADMIN]` (assertable only against the real build: persistence, filtering, Slack, idempotent server effects). Wireframe reality check (from script read): route cards toggle `.on` + enable `.etc-in`; filter chips toggle visually but do NOT filter rows; checkboxes are inert; `Register Inbound Request` fires `#gtoast`; M1 `＋ Add tracking number` appends rows and last-row ✕ clears; comment buttons inject `.cpanel-ir` panels from `IR_COMMENTS`. QA text must not over-assert beyond this.

Estimated counts by spec §8 subsection (total ≈ 55, of which ≈ 34 [WF] / ≈ 21 [REAL-ADMIN]; ≈ 18 negative):
- A. New Request form (S1/S2): 16 — route cards ×3, unified search/row-append ×4, validation negatives ×6 (E-1..E-10 subset), register+toast+idempotency ×3
- B. State 2 deltas: 4 — preselected WHOLESALE card, FOC 0 row, tracking-at-creation note, same-register behavior
- C. Request List: 14 — chips ×4, column renders (badges, multi-tracking cell, PARTIAL n/m, ✎ history, Received "–") ×5, bulk bar ×2, deep link ×1, empty/negative ×2
- D. M1 modal: 10 — open paths ×2, row add/remove ×3 (incl. E-37), save/cancel/toast ×3, negatives ×2 (E-32/33)
- E. Lifecycle cross-page (with View Orders): 6 — PARTIAL auto-switch, resume-from-remainder, INBOUNDED auto-switch + Received Date, qty-edit propagation, no-manual-transition negative (all [REAL-ADMIN] except the negative absence check)
- F. Comments hub + row panels: 5 — tabs, star toggle, panel open/data, post placeholder, mention→Slack ([REAL-ADMIN])

Three fully-worked examples (format the spec will use):

**QA-A-14** `[WF]` (covers [L-S1-3][L-S1-7][G-2][G-9]/E-17)
Given the live wireframe with top-bar tab `1 · New Request (Smart Buy)` active
When I click the blue button with exact label `Register Inbound Request`
Then a toast `#gtoast` becomes visible at top-right with bold text `✓ Inbound request registered` and secondary line `Inbound No. auto-assigned · added to the Request List · No refresh`, and the page does NOT navigate or reload (URL unchanged, form still in DOM)
And when I click the same button twice within 500ms, only one `#gtoast` element exists in the DOM (timer resets; no stacked toasts). `[REAL-ADMIN]` addendum: exactly one request row and one Inbound No. are created for the double-click (server idempotency key).

**QA-D-03** `[WF]` (covers [L-M1][G-10]/E-37)
Given the modal opened via top-bar tab `Modal: Add Tracking No` (header reads `Add Tracking No — 202607130003`)
When I click `＋ Add tracking number` twice
Then `#tnList` contains 3 rows each with an input and a `✕` button
When I click `✕` on two rows, then `✕` on the last remaining row
Then two rows are removed and the final row REMAINS with its input value cleared (row count never reaches 0)
When I click `Save tracking numbers`
Then the modal closes and `#gtoast` shows `✓ Tracking number(s) saved` with secondary line `Every registered number is now matched to View Orders · No refresh`.

**QA-A-06 (negative)** `[WF+REAL-ADMIN]` (covers [L-S1-2]/E-8)
Given State 1 with the `Other` route card clicked
Then the card gains class `on` and its inline input (placeholder `Enter channel name`) becomes enabled and focused `[WF]`
When I leave the channel-name input empty and click `Register Inbound Request`
Then registration is blocked with an inline error on the channel-name field, no request is created, and no success toast fires `[REAL-ADMIN]` (wireframe limitation: the static page always toasts — the QA doc must mark this assertion REAL-ADMIN so the adversarial QA runner does not flag a false failure).

---

## 4. MANDATORY-INCLUSION MAP (of the 12)

| # | Item | Lands here? | Where |
|---|---|---|---|
| 2 | Confirmation toast [G-2] | YES | §3 register + M1 save toasts (exact texts above), §8 QA-A-14/QA-D-03 |
| 7 | Multiple tracking numbers [G-10] | YES — **primary landing page** | §3 [L-S3-7][L-M1], §7 E-33..E-39, §8 section D |
| 12 | Comment @mention Slack routing [G-7] | YES | §6 table (#fulfillment-admin-comments `C0BMGEWM5QA` CONFIRMED — the "pending owner decision" in decision-sources is resolved per slack-routing.md), §3 [L-S1-14] |
| 6 | Unrecognized matching | Cross-ref only | §7 E-45 → tracking-missing + view-orders specs own it |
| 1,3,4,5,8,9,10,11 | Scanner/audio/print/sample/RTO-KR/Inventory items | NO | §6/§9 state explicitly N/A (no scan surface, no Print button on this page); G-1 delta = Enter in unified search must not submit the form |

Plus non-numbered mandatory context landing here: [G-11] lifecycle (core of this page), morning no-tracking Slack checks (slack-routing rows 2–3, CONFIRMED), [G-12] `#reqlist` deep link, [G-8] data-capture doctrine.

## 5. OPEN QUESTIONS

**Owner must decide (do not invent):**
- OQ-1 Request edit/cancel/delete after registration — the wireframe has NO affordance. Is a registered request immutable except tracking/qty-edit/comments? What happens to a request that will never arrive (supplier cancelled)?
- OQ-2 Duplicate SKU picked twice in one request — merge quantities, allow two rows, or block?
- OQ-4 Duplicate tracking number across different requests (and vs customer-order tracking) — block, warn, or allow? Directly affects View Orders matching integrity.
- OQ-5 Removing a saved tracking number in M1 after scans exist against it — blocked, or allowed with audit event?
- OQ-6 Expected-qty edited down to exactly the already-received qty — auto-transition PARTIAL→INBOUNDED, or require a closing scan action in View Orders?
- OQ-7 Adding tracking numbers to an already-INBOUNDED request (late extra split shipment) — allowed?
- OQ-3 Who may add/bulk-add tracking and see the Request List (role/permission matrix is undefined across the 8 specs — needs one owner answer globally).

**Developer decides at build time (flag in §9, no owner block):**
- OQ-8 Expected-arrival past-date handling (allow with warning suggested); date min/max.
- OQ-9 Slack channel for "Other"-route morning check (legend S3-6 + slack-routing both defer to dev time).
- OQ-10 Request List pagination/sort ("Showing 6 of 12" — page size, default sort newest-first assumed), search within list (none in wireframe).
- OQ-11 NNNN overflow behavior (>9999/day) — hard-fail with alert acceptable.
- OQ-12 Tracking-number charset/length validation breadth (carrier-agnostic; no single-carrier regex).
- OQ-13 Form reset-vs-persist after successful registration (toast says "added to the Request List"; does the form clear for the next request?).
- OQ-14 Idempotency key mechanics (per-form-session UUID suggested) — [G-9] mandates existence, not mechanism.
