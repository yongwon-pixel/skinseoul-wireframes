# Closing — Spec Plan, LENS A (Operator & Data)

Planner: A (operator physical flow · data capture · business rules · Slack routing).
SST: `wms2/closing/index.html` (live: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/closing/).
Ledger sources: `2026-07-09-wms2-wireframes.md` (item 7, 07-23 rework line), `2026-08-02-wms2-en-spec-handoff.md` (스펙 필수 반영 bullet, Slack routing block).

---

## 1. LEGEND INVENTORY (every dot on every state/modal — 21 units)

Proposed spec keys: `[L-{state}.{n}]`, modals `[L-M1]`/`[L-M2]`, plus the State-1 off-screen behavior paragraph as `[L-1.B]` (it is normative text, not decoration — it must be specced as its own unit).

| Key | Dot | What it is | Spec treatment |
|---|---|---|---|
| L-0.1 | S0 #1 | Pre-start screen exposes ONLY the manual-count input (simplified 2026-07-23); Start Closing gates everything; count editable + closing cancellable later; history via top tab | §3 full behavior (input validation: positive integer required, Start disabled on empty), §4 BR (manual physical count is the baseline), §5 `closing_session_started` |
| L-1.1 | S1 #1 | Closing-dedicated large scan input; carrier-handover tracking no. (YT… example); auto-Enter submit → verdict → focus returns, all text selected; never refresh | §3 keystroke-level flow citing [G-1] + closing deltas (disabled pre-start; select-all-on-return); §5 `scan_event` |
| L-1.2 | S1 #2 | OK = compact one-line green bar (seq · order · tracking · status · time · worker); large OK panel removed 2026-07-23 | §3 exact content of the line; §4 rationale (only warnings need distance recognition) |
| L-1.3 | S1 #3 | Voice alert toggle, ON by default; auto-plays "Please check this order" on warnings; Test voice button | §3 toggle/test behavior citing [G-3b]; §5 `voice_alert_toggled` (persisted operator action) |
| L-1.4 | S1 #4 | Progress tiles: target (manual) / OK / warnings / remaining + green·red progress bar | §3 computation formulas (remaining = target − OK; deleted rows excluded); §8 tile assertions |
| L-1.5 | S1 #5 | Verdict rule: OK ⇔ order status = Prepare Shipment, everything else = warning | §4 BR-1 (2026-07-23; replaces manual "was it outbound-processed" step); §3 verdict matrix |
| L-1.6 | S1 #6 | Scan list: seq # leftmost, cumulative from 1, append at bottom, lowest first; dup notes cite colliding # ; per-row ✕ delete → M2; deleted rows excluded from counts | §3 column-by-column table spec; §5 `scan_row_deleted`; §7 numbering-after-delete edge |
| L-1.7 | S1 #7 | Comments hub (Mentions/Saved/search) in top bar | Cite [G-7], page delta only: closing-exception comment trail (dup combined-box reasons, M1 memos land here); §6 Slack row |
| L-1.8 | S1 #8 | Confirm Closing button: enabled only at exact OK==target AND warnings==0; over-scan re-disables; enabled ≠ auto-confirm; confirm saves record + auto-updates Daily Shipping Status | §3 enable/disable state machine + button label variants ("Confirm Closing (79 remaining · 2 warnings)"); §4 BR-3/BR-4; §5 `closing_confirmed`; §6 Daily Shipping Status handoff |
| L-1.9 | S1 #9 | Reduced side margins — all columns + status fit one screen without scrolling | §3 layout note (operator context: no horizontal scroll during scanning) |
| L-1.10 | S1 #10 | Locked target banner: started-at + starter shown; [↺ Edit count] and [✕ Cancel Closing] | §3 edit flow (unlock→edit→Save, old/new persisted) + cancel flow (confirm dialog: discards scan records); §5 `closing_target_edited`, `closing_session_cancelled` |
| L-1.11 | S1 #11 | Top tabs [Closing \| Closing History] — history is a separate page, not modal (converted 07-23) | §2 map; §3 tab behavior (returning restores in-progress view) |
| L-1.B | S1 footer ¶ | Off-screen behavior rules: scan input disabled pre-start; click-anywhere auto-focus + select-all; toast without reload; server-side session persistence (nav/refresh safe); over-scan flip; unknown excluded; M1 is a real status change | §3 as a distinct "session & focus behavior" block; §4 BR-8 (server persistence); §5 (server persists every scan at scan time, not at confirm) |
| L-2.1 | S2 #1 | Processing scan = red row + "⚠ Not outbounded" + auto voice; handled in-list via [Process this order] → M1; large warning panel + action banner removed 07-23 | §3 warning row behavior; §7 pairing with E-cases; note stale wording vs L-1.2 (see OQ-D6) |
| L-2b.1 | S2b #1 | Unknown order: tracking matches nothing → red row, Order/status "–", auto voice, NOT counted toward closing; recheck label → rescan → escalate; explicitly distinct from View Orders unrecognized-product flow (added 07-23) | §3 + §4 BR-6; §6 boundary note (does NOT route to #unrecognized-tracking); §5 scan_event verdict=unknown |
| L-3.1 | S3 #1 | Duplicate scan = red row + "⚠ Duplicate scan" + voice; digital replacement of Excel column-A dup check; Notes cite #n ↔ #m with first scan time+worker (combined-box judgment); dups never double-counted; combined-box reason logged in order Comments | §3 + §4 BR-5; §5 dup linkage fields; OQ-O2 (resolution semantics) |
| L-4.1 | S4 #1 | Completion requires the human press at exact match + 0 warnings; confirmer + time recorded; snapshot saved to Closing History (wireframe still says "(M2)" — stale ref, see OQ-D6) | §3 completion screen; §5 `closing_confirmed` payload; §10 reversal entry (history modal → page) |
| L-4.2 | S4 #2 | Closing Report CSV download — replaces manual copy/paste + formula-stripping into SS Daily Shipping Status; snapshot auto-saved on confirm | §3 export behavior; §5 `closing_report_exported`; §6 sheet handoff; OQ-O1 (print vs CSV) |
| L-4.3 | S4 #3 | Warning Resolution Summary — aggregates today's Processing/dup warnings + how each was resolved | §3 content rules; §5 (rendered from persisted warning/resolution events — a UI view per [G-8]) |
| L-H.1 | History #1 | Separate history page: daily snapshot rows (date · target · OK · warnings raised→resolved · match · closed by · confirmed at) + per-day CSV incl. full scan list; always "Match" since mismatch can't confirm | §3 table spec; §5 retention/export; §4 BR-10 |
| L-M1 | Modal M1 | Process Processing Order: Zero Packing verification checkbox (step 6 of current process) + optional memo (→ order Comments + closing log); real status change Processing → Prepare Shipment reflected on every screen; closing row re-judged green | §3 full modal spec (checkbox required to enable action? — see OQ-D7); §5 `order_status_changed` + `warning_resolved`; §6 mention routing if memo tags someone |
| L-M2 | Modal M2 | Delete Scan Row confirm ("Remove this scan? Yes/No"): excluded from list + counts; deletion history kept in backend | §3; §5 `scan_row_deleted` with full original payload retained |

Wireframe chrome note (not a legend item): the wf-tab bar lists "Modal: Process Processing Order" twice (lines 215/217) — demo chrome duplication, not a spec unit; record in §9 so QA doesn't count it.

---

## 2. SECTION OUTLINES (10 template sections — concrete content)

### §1 Purpose & Users
- End-of-day physical verification: hand-counted packed parcels vs system outbound status, one tracking-barcode scan per parcel. Users: warehouse staff (Dean, Miranti — scanning), whoever confirms (may differ from starter: wireframe shows Dean starts 18:02, Yongwon confirms 18:52).
- Physical context that shaped decisions: scanner in hand, eyes on parcels not monitor → voice-only warning channel (Dean's request); OK is deliberately silent+compact; no horizontal scroll (L-1.9); no clicks between scans [G-1].
- Operational moment: replaces the current Excel process (column-A dup check, manual "outbound-processed?" check, manual copy/paste into SS Daily Shipping Status with formula-stripping).

### §2 Screen Inventory & Wireframe Map
- 7 states + 2 modals table: s0 Before Start / s1 OK scan / s2 Warning·Processing / s2b Warning·Unknown / s3 Warning·Duplicate / s4 Complete / shist History page / M1 / M2 — each with wf-tab name, live URL, how to reach, and the L-keys it owns (from §1 inventory above). 1:1, zero orphans.

### §3 Functional Specification
- Per L-key as inventoried. Highlights to write in full:
  - Scan loop state machine (L-1.1 + L-1.B): disabled → armed (session started) → submit on Enter (scanner auto-Enter; on-screen Scan button is fallback only) → server lookup → verdict render (row append + toast + tile update + conditional voice) → focus return with select-all. NEVER a page refresh. Click-anywhere refocus.
  - Verdict matrix (L-1.5): Prepare Shipment → OK(green, silent) · any other status → Not outbounded(red, voice) · already-scanned-today tracking → Duplicate(red, voice, cites #n first-scan time+worker) · no matching order → Unknown(red, voice, excluded from counts).
  - Confirm gating state machine (L-1.8): disabled(label shows remaining+warnings) → enabled(exact match, 0 warnings) → re-disabled on over-scan → confirmed. Idempotent confirm [G-9].
  - Target edit (L-1.10): unlock → numeric edit → Save; recompute remaining/gating instantly; old→new persisted.
  - Cancel closing (L-1.10): confirmation dialog required ("discarding scan records"); returns to State 0.
  - M1: checkbox + memo; action button "Process Outbound → resolve warning"; real cross-screen status change; row re-judged in place (no refresh).
  - M2: Yes/No; row removal; counts recompute.
  - History page (L-H.1): row schema + per-day CSV.
  - Toasts: scan OK toast ("✓ Outbound confirmed — {tracking} / Ready for the next barcode scan"), confirm toast ("✓ Today's closing confirmed — 84/84 orders / Daily Shipping Status auto-updated") [G-2].

### §4 Business Rules (Lens-A owned — with rationale and dates)
- BR-1 OK ⇔ Prepare Shipment only; all else warning. Replaces manual outbound-processed check. (2026-07-23 rework)
- BR-2 Baseline = manually hand-counted physical parcels, never a system figure — closing exists to catch physical/system divergence in both directions. (2026-07-23)
- BR-3 Exact-match gating: OK == target AND warnings == 0; over-scan is also a mismatch. (2026-07-23)
- BR-4 No auto-confirm: match only ENABLES the button; scan input stays live post-match (85th-parcel case); a human presses Confirm. (2026-07-23, copy reconfirmed 2026-08-03)
- BR-5 Duplicates never double-counted; dup row must cite colliding # + first scan time + worker (combined-box judgment); combined-box reason goes to order Comments. (F Dean / current process step 1; 07-23)
- BR-6 Unknown order excluded from closing counts; physical-label recheck → rescan → escalate. Distinct from View Orders unrecognized-product flow. (added 2026-07-23)
- BR-7 M1 outbound = REAL order-status change (Processing → Prepare Shipment) reflected on all screens; Zero Packing verification is current-process step 6 carried over. (2026-07-23)
- BR-8 Server-side session persistence: nav away / refresh / crash keeps count, list, warnings; nothing clears until confirm or explicit cancel/restart. (wireframe behavior ¶, 2026-08-03)
- BR-9 Pre-start gating: scan input (and all tiles) hidden/disabled until manual count entered. (simplified 2026-07-23)
- BR-10 History rows are always "Match" — mismatch cannot be confirmed, by construction. 
- BR-11 Confirm auto-updates Daily Shipping Status (replaces manual copy/paste + formula-stripping). (F Closing current-process)
- BR-12 Scan-row deletion always via confirm modal; deletion history retained in backend forever. (M2)
- BR-13 Voice ON by default; toggle + test provided; OK scans are silent by design. (F Dean; en-US TTS phrase fixed "Please check this order", 2026-08-03 owner confirmation)
- BR-14 Mid-session target edit and full cancel allowed from State 1 banner. (07-23 simplification of State 0)
- BR-15 History = separate page, per-day CSV includes the FULL scan list. (converted from modal M2, 2026-07-23 — log as reversal in §10)

### §5 Data Capture — see Lens-A deep inventory below (full event list lands here verbatim).

### §6 Integrations
- Slack routing rows (see dedicated block below).
- Daily Shipping Status handoff: closing_confirmed → auto-update of SS Daily Shipping Status (sheet/BI contract — mapping is OQ-O5).
- Cross-page: M1 status change propagates to View Orders / Order Detail / Order Management instantly; Order ID cells are links (blue in wireframe) → order detail deep link [G-12].
- Print pipeline: NO print button on this page per wireframe (CSV only) — but decision-sources mandatory item 4 names "Closing report" under [G-4]; discrepancy flagged OQ-O1.

### §7 Edge Cases (Lens B owns; Lens-A contributions to seed)
- Scan while session not started; scan mid-target-edit; two stations scanning the same tracking within the same second (seq atomicity); delete an OK row that was counted (match flips); delete the FIRST scan of a dup pair (does the dup row's "duplicate of #2" reference dangle? re-judge?); cancel closing with unresolved warnings; confirm double-click [G-9]; network loss between scan and verdict; TTS unavailable/muted device; refresh mid-session (BR-8 must hold); same tracking on two different orders (data anomaly); target edited below current OK count (negative remaining).

### §8 QA Acceptance Criteria (Lens B owns counts; Lens-A requirement)
- Every BR above and every §5 event gets at least one G/W/T including the persisted-event assertion (e.g., "Then a scan_event with verdict=duplicate and duplicate_of=#2 exists"). Negative tests for gating (confirm disabled at 83/84, at 85/84, at 84/84+1 warning).

### §9 Out of Scope & Open Questions
- Out: label printing/layouts (Phase 3-1); View Orders product-barcode unrecognized flow; carrier tracking-status sync; box/size columns (removed 07-23 — record so nobody re-adds). Wf-tab duplication chrome note. Open questions: block below.

### §10 Decision Log (dated)
- 07-09 initial closing page (barcode verify, red warnings + voice). 
- 2026-07-23 rework batch: OK=Prepare-Shipment-only · box/size columns removed · manual-count target introduced · exact-match + 0-warnings gating (over-scan = mismatch) · State 0 simplified to count-only · large OK panel removed · large warning panel + action banner removed (list-row handling) · unknown-order state added · history modal (M2) → separate page REVERSAL · daily record schema (target·scans·warnings raised→resolved·closer·time·CSV).
- 2026-08-03 (owner review round): scanner protocol emphasized for closing ([G-1], cursor residency + never refresh) · voice = en-US TTS "Please check this order" confirmed · global confirm-toast [G-2] · #fulfillment-admin-comments channel created (`C0BMGEWM5QA`).

---

## 3. LENS-A DEEP INVENTORY

### 3a. Data Capture event list (per [G-8]: actor + timestamp + entity + old/new values; UI logs are views, never the only copy)

Persistence rule: every event is written server-side AT ACTION TIME (BR-8), not batched at confirm. Retention: indefinite (doctrine: maximize admin accumulation); full per-day scan lists exportable via History CSV.

| # | Event | Actor | Entity | Payload (old/new where applicable) | UI-visible? |
|---|---|---|---|---|---|
| 1 | `closing_session_started` | starter | closing session (date) | target_qty, started_at | Yes (banner "started 18:02 · Dean") |
| 2 | `closing_target_edited` | editor | session | old_qty → new_qty, edited_at | Partially (new value only) — old value is silent capture |
| 3 | `closing_session_cancelled` | canceller | session | scan_row_count discarded, cancelled_at; rows RETAINED in backend (only the session state resets) | Silent after the fact |
| 4 | `scan_event` (every scan, all verdicts) | scanning worker | session + tracking_no (+ order_id nullable) | seq #, scanned_at (hh:mm:ss), tracking_no, order_id/–, item_count/–, order_status_at_scan, verdict ∈ {ok, not_outbounded, duplicate, unknown}, duplicate_of_seq + first_scan_at + first_scan_actor (dup only) | Yes (scan list row) |
| 5 | `warning_raised` | (derived, same actor) | scan row | verdict + reason — may be a facet of #4 rather than a second row; spec must state it feeds History "warnings raised" counter | Yes (red row + tile) |
| 6 | `voice_alert_toggled` | operator | session/device | old on/off → new | Yes (switch) |
| 7 | `scan_row_deleted` | deleter | scan row | seq #, full original scan payload snapshot, deleted_at; "deletion history is kept in the backend" (M2 note — verbatim owner requirement) | Row disappears; event is silent |
| 8 | `order_status_changed` (via M1) | resolver | order | order_id, tracking, old status Processing → new Prepare Shipment, zero_packing_checked (bool), source=closing_m1 | Yes (row re-judged green; cross-screen) |
| 9 | `comment_posted` (M1 memo, dup combined-box notes) | author | order | text, mentions[], source (closing_m1 / manual) — dual-written to order Comments history AND closing log (M1 copy: "also recorded to…the closing log") | Yes (Comments) |
| 10 | `warning_resolved` | resolver | scan row / warning | method ∈ {m1_outbound, row_deleted, …(OQ-O2)}, resolved_at — feeds History "raised→resolved" and State 4 summary | Yes (summary banner) |
| 11 | `closing_confirmed` | confirmer | session | confirmed_at, target, ok_count, warnings_raised, warnings_resolved, match=true, full scan-list snapshot id | Yes (State 4 + toast) |
| 12 | `daily_shipping_status_updated` | system (triggered_by #11) | external sheet/BI row | date, values written, success/failure + retry log — failure must NOT silently pass (toast says it happened) | Toast only |
| 13 | `closing_report_exported` | downloader | session/date | source ∈ {state4_button, history_row_csv}, exported_at | No (silent) |
| 14 | `mention_notification_sent` | system | comment | Slack channel, message ts, mentioned user — delivery record per [G-7] | No (silent) |
| 15 | `comment_saved_toggled` (★) | operator | comment | old/new saved state | Yes (star) |
| 16 | `mentions_marked_read` | operator | comment set | comment ids, read_at (badge count is a view over this) | Yes (badge) |
| 17 | `scan_lookup_failed` (network/server error mid-scan) | worker | tracking_no | error class, retried?, ts — needed so a "lost scan" is diagnosable against a physical parcel | Error toast |
| 18 | `session_restarted` (post-cancel new start, or post-confirm re-open if allowed — OQ-O4) | starter | new session | link to prior session id same day | Yes |

Explicitly NOT persisted (state in spec to prevent gold-plating): voice test-button plays, TTS utterance playback events, focus/refocus events.

### 3b. Operator-flow notes (field usability — every operational decision the wireframe encodes)

1. **Heads-down loop**: parcel → scan → listen. OK is silent; ONLY warnings speak. The operator never needs the monitor between parcels; the compact OK line + toast exist for the occasional glance. Spec must forbid any modal/focus-steal on OK scans.
2. **[G-1] deltas for closing**: input disabled pre-start; after start, click-anywhere auto-focus with select-all so a stray click can't break the loop; scanner auto-Enter = submit (the on-screen Scan button is a fallback, not the path); next scan overwrites selected text. Never refresh.
3. **Verdict latency**: verdict + voice must land before the operator picks up the next parcel — spec should set a budget (dev decides number, OQ-D1) and require the input NOT lock while lookup runs (or define queueing) so scanning speed is never gated by network.
4. **Two-operator reality**: wireframe encodes Dean + Miranti scanning in ONE session (Worker column, dup note "first scanned 18:40:18 (Miranti)" vs dup by Dean). Seq assignment must be server-atomic across stations; both stations' lists must stay live-consistent. Who may Start/Edit/Cancel/Confirm is a permissions gap (OQ-O3).
5. **Physical-count primacy**: the target is a hand count because the whole point is catching what the system doesn't know (85th parcel found on the floor) and what physically isn't there (system row, no parcel). Hence: scan alive after match, over-scan re-disables confirm, edit-count always available.
6. **Warning resolution happens in the list** (07-23: big panels removed) — the operator resolves without leaving the scan loop: [Process this order] inline, ✕ inline. Voice re-play button exists in warning states for "what did it just say".
7. **Duplicate = judgment call, not auto-error**: combined-box is legitimate; the row gives the operator exactly what's needed to judge (which #, when, who) and the paper trail goes to order Comments.
8. **Unknown order = physical action**: instruction text sends the operator to the physical label first (mistype vs foreign parcel), then rescan, then escalate — spec should keep this copy verbatim.
9. **Interrupt-safety**: shift handover / browser crash / walking to Zero Packing mid-closing are normal — BR-8 server persistence is an operator requirement, not a tech nicety.
10. **Confirm is a ceremony**: label carries live counts ("Confirm Closing (79 remaining · 2 warnings)") so the blocker is readable from the button itself.

### 3c. Slack routing rows used by this page (channels CONFIRMED in `_inputs/slack-routing.md`)

| Trigger on this page | Channel | Payload | Notes |
|---|---|---|---|
| Comment @mention — closing-exception comments (dup combined-box notes, M1 memo when it @tags someone, any order comment posted from closing context) | **#fulfillment-admin-comments** (ID `C0BMGEWM5QA`) | order/entity no., comment text, time, author, @mentioned user, deep link | CONFIRMED (owner, 2026-08-03). Message body @mentions the person → personal Slack notification; channel doubles as team-visible archive [G-7] |
| Unknown-order scan (State 2b) | — none — | — | Deliberately NOT #unrecognized-tracking: that channel is the View Orders product-barcode pool; closing's unknown is a tracking no. absent from the system. Spec must state this non-route explicitly |
| Closing confirmed / mismatch / report | — none confirmed — | — | Falls under routing table's "Other-channel notifications: decide per feature at dev time"; do not invent (OQ-O6) |

---

## 4. MANDATORY-INCLUSION MAP (of the 12)

| # | Item | Lands here? | Where in spec |
|---|---|---|---|
| 1 | Scanner protocol [G-1] | YES | §3 L-1.1 + L-1.B (closing named explicitly in the 08-03 owner bullet) |
| 2 | Confirmation toast [G-2] | YES | §3 scan toast + confirm toast + edit/cancel/delete confirmations |
| 3 | Audio feedback [G-3] | YES — (b) voice branch | §3 L-1.3, §4 BR-13 (en-US TTS "Please check this order"; send-sound branch (a) N/A here) |
| 4 | Instant carrier-agnostic print [G-4] | FLAGGED | Decision-sources names "Closing report" under G-4, but wireframe (SST) has CSV download only, no Print button → OQ-O1; spec references G-4 conditionally |
| 6 | Unrecognized matching | Boundary only | §9/§3 L-2b.1: explicit non-overlap statement (closing unknown ≠ unrecognized pool) |
| 12 | Comment @mention routing [G-7] | YES | §6 routing table with #fulfillment-admin-comments `C0BMGEWM5QA` |
| 5,7,8,9,10,11 | — | No | Other pages (OM / inbound-request / RTO / Inventory ×3) |

---

## 5. OPEN QUESTIONS (flagged, not decided)

### Owner must decide
- **OQ-O1** — Decision-sources mandatory item 4 lists "Closing report" under instant print [G-4], but the wireframe (SST) ships CSV download only with no Print button. Is CSV-only final, or does the closing report also need an instant-print button?
- **OQ-O2** — Duplicate-warning resolution semantics: is ✕-delete (after logging the combined-box reason in Comments) the only path that clears a duplicate warning toward "0 warnings"? And do deleted warning rows still count in History's "warnings raised→resolved" (State 4 shows 3→3 including duplicates)?
- **OQ-O3** — Role/permission gating: may any warehouse staff Start / Edit count / Cancel / Confirm closing, or is any of these manager-restricted? (Wireframe shows starter ≠ confirmer, multiple scanners in one session — no restriction is drawn.)
- **OQ-O4** — Same-day re-closing: after Confirm, can closing be re-opened/re-run the same day (behavior ¶ says "until closing is confirmed or explicitly restarted")? If yes, does History show two rows for one date?
- **OQ-O5** — Daily Shipping Status auto-update contract: which exact sheet/system and column mapping does `closing_confirmed` write to (current "SS Daily Shipping Status")?
- **OQ-O6** — Should closing confirmation (or an unresolved-warning end-of-day condition) notify any Slack channel? Routing table defers "other channels" to dev time — confirm none is wanted, or name one.

### Developer decides at build time
- **OQ-D1** — Scan verdict latency budget + behavior while lookup is in flight (input queue vs lock) and on lookup failure (event #17, retry policy).
- **OQ-D2** — Sequence numbers after row deletion: keep gaps, never renumber (default inferred from wireframe #7-after-deletions; also keeps dup cross-references stable).
- **OQ-D3** — Idempotency mechanics [G-9] for scan submit and Confirm Closing (client debounce + server key; known double-click bug in handoff notes).
- **OQ-D4** — TTS implementation details: voice selection fallback (wireframe demo: Samantha → any en-US → default), and rapid-consecutive-warning policy (wireframe demo cancels prior utterance — cancel-and-speak vs queue).
- **OQ-D5** — CSV format: column set (full scan list incl. deleted rows? verdicts? workers?), encoding (UTF-8 BOM for Excel), filename convention for State-4 vs per-day History export.
- **OQ-D6** — Spec-time normalization of stale wireframe text (no behavior change): State 4 legend still says history saves "(M2)" (pre-07-23 modal ref → now the History page); State 1 legend 2 says the large panel "is used only in warning states" while State 2 legend says the large warning panel was removed 07-23 (net truth: no large red panel remains; big panel appears only as State 4's green completion status).
- **OQ-D7** — M1: is the Zero Packing checkbox mandatory to enable [Process Outbound] (wireframe doesn't enforce it)? Default: yes, require it — it is current-process step 6; record as spec default pending no owner objection.
- **OQ-D8** — Voice toggle persistence scope (per user vs per device vs per session; default ON each session start).
