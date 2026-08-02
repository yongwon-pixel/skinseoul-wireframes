# Closing — Spec Plan, LENS B (Developer & QA)

Planner: B (functional precision · edge cases · QA acceptance criteria). Page slug: `closing`.
Wireframe SST: `wms2/closing/index.html` · Live: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/closing/
Complementary plan: `closing.A.md` (Operator & Data lens). Overlap intended; nothing here depends on A.

---

## 1. LEGEND INVENTORY (every legend/dot number — 21 items + 1 off-screen behavior block)

Key format `[L-{state}.{n}]`. "→ §" = which template section carries the main spec load; every item also gets a §3 functional entry per template rule.

| Key | What it is | Spec treatment |
|---|---|---|
| [L-0.1] | State 0 pre-start screen: only the manual-count input is exposed; Start Closing requires the hand-counted parcel number; switches to State 1; count editable + closing cancellable later; history via tab. (Simplified 2026-07-23) | §3 full functional entry (validation of count input, Start action, server session create, idempotency); §4 rule "physical count is the baseline"; §8 scenarios QA-S0 |
| [L-1.1] | Closing-dedicated large barcode scan input; scanner auto-Enter submits → instant verdict → focus returns with text selected; page never refreshes between scans [G-1] | §3: input contract, submit trigger (Enter OR Scan button), normalization, server scan action + idempotency key, focus lifecycle; §7 E-1/2/12/48; §8 QA-SCAN |
| [L-1.2] | OK scan = compact one-line green bar (seq · order · tracking · status · time · worker); large panel reserved for warnings only (2026-07-23, Dean) | §3: exact render fields + when it appears/replaces; §8 expected text pattern "✓ #N Outbounded" |
| [L-1.3] | Voice alert toggle (default ON) — auto-plays "Please check this order" on warnings; Test voice button [G-3b] | §3: toggle states, test button behavior (plays regardless of toggle — per wireframe JS), persistence question → DQ-3; §7 E-39/46; §8 QA-VOICE |
| [L-1.4] | Progress counts: target (manual) / OK / Warnings / Remaining + green·red progress bar | §3: exact formulas (Remaining = target − OK, floor 0; bar % = OK/target, warn/target), recompute triggers (scan, delete, M1, count edit); §8 QA-COUNT |
| [L-1.5] | Verdict rule: ONLY status = Prepare Shipment → green "Outbounded"; every other status = warning | §3 + §4 core business rule; §7 E-4/5 (non-Processing abnormal statuses → OQ-4); §8 QA-VERDICT incl. negative tests |
| [L-1.6] | Scan list table: # = scan sequence (cumulative from 1, lowest first, append at bottom); duplicate Notes cite colliding # (e.g., #3 ↔ #2); ✕ per row = delete scan row via confirm modal (M2); deleted rows excluded from counts | §3: column contract (10 cols incl. empty 44px action col), sequencing rules (deleted # not reused — to confirm as DQ), Notes content per verdict; §7 E-26–29; §8 QA-LIST |
| [L-1.7] | Comments hub in top bar: @Mentions + ★Saved + full comment search, newest first, unread badge [G-7] | §3 delta-only (cite G-7): closing-specific payload = closing-exception comment trail; §6 Slack row (#fulfillment-admin-comments, C0BMGEWM5QA); §8 QA-HUB (tab switch, star toggle — wireframe-runnable) |
| [L-1.8] | Confirm Closing button — enabled ONLY at OK == target exact match AND 0 warnings; over-scan re-disables; enabled ≠ auto-confirm (human click required); confirming saves closing record + auto-updates Daily Shipping Status | §3: enable predicate (pure function of counts), disabled label format "Confirm Closing (N remaining · M warnings)", server confirm action, idempotency [G-9]; §7 E-11/17/31/37/38; §8 QA-CONFIRM |
| [L-1.9] | Reduced side margins — all columns + status fit one screen without horizontal scroll | §3 one-liner (layout constraint); §8 single viewport assertion |
| [L-1.10] | Target banner in State 1: locked value + started-at/by; [↺ Edit count] and [✕ Cancel Closing]; cancel returns to pre-start, discarding scans requires confirmation | §3: edit toggle → Save flow + validation; cancel flow + confirm dialog (dialog NOT in wireframe — spec must define copy → flagged); §7 E-15–21; §8 QA-TARGET |
| [L-1.11] | Top tabs [Closing \| Closing History] — history is a separate page (not modal), daily snapshots + CSV | §3 nav behavior ("Closing" returns to the state you were viewing — `lastState` behavior in JS); §8 QA-NAV |
| [L-1.BR] | Off-screen behavior-rules paragraph (State 1 legend footer): scan input disabled until closing starts; click-anywhere auto-focus w/ select-all; verdict toast top-right, no reload; Prepare Shipment = OK silent, all else / duplicate = red + voice; exact-match + 0-warnings gate; over-scan = mismatch; M1 = real status change on every screen; unknown order excluded from count; **closing progress stored server-side** (refresh/navigation-safe; nothing clears until confirmed or explicitly restarted); continuous-scan focus/select loop | §3 as its own keyed block (it is normative, not decorative); §4 (persistence rule); §7 E-33/36/48; §8 QA-FOCUS + QA-PERSIST (persist = ADMIN-ONLY) |
| [L-2.1] | Processing scan = red row + "⚠ Not outbounded" + auto voice; handled in-list via [Process this order] → M1; large warning panel/action banner removed 2026-07-23 | §3: row render, button placement in Notes col; §8 QA-VERDICT |
| [L-2b.1] | Tracking number with no matching order = "⚠ Unknown order" (Order/Items/Status = "–"), auto voice, NOT counted toward closing; recheck label → rescan → escalate; distinct from View Orders unrecognized (product-barcode) flow (added 2026-07-23) | §3 + §4 (exclusion rule); §7 E-3/13; §8 QA-UNKNOWN incl. count non-increment assertion |
| [L-3.1] | Duplicate scan = red row + "⚠ Duplicate scan" + voice; Notes cite first scan # + time + worker (combined-box judgment); duplicates never double-counted; combined-box reasons logged in order Comments | §3: dedupe key = tracking no. within active session; §7 E-6/7/8/30; §8 QA-DUP |
| [L-4.1] | State 4 requires pressing [Confirm Closing] at exact match + 0 warnings; no auto-close; confirmer + time recorded; snapshot saved to Closing History (legend says "(M2)" — STALE ref, history is now a page; normalize in spec) | §3: confirm success render (bigstatus bs-ok, exact copy), toast "✓ Today's closing confirmed — 84/84 orders" + "Daily Shipping Status auto-updated"; §10 decision log entry; stale-ref note |
| [L-4.2] | Closing Report CSV download — replaces manual copy/paste + formula-stripping into SS Daily Shipping Status; snapshot auto-saved on confirmation | §3: export contents (full scan list incl. deleted-row disposition → DQ-5), trigger button "Download Closing Report (CSV)"; §6 sheet handoff; §7 E-40 |
| [L-4.3] | Warning Resolution Summary — aggregates today's warnings and their resolutions (Processing→resolved via Outbound; duplicates→combined-box confirmed in Comments) | §3: aggregation source = scan/warning event log; §5 pointer; §8 text-content assertion |
| [L-H.1] | Closing History = separate page via top tabs; daily snapshot row: date · target · OK · warnings raised→resolved · match · closed by · confirmed at; per-day CSV per row (full scan list); "Closing" tab returns to prior state; footer: records always saved as Match (mismatch cannot be confirmed) | §3: table contract + per-row CSV action; §7 E-42–45 (multi-session/day, empty state); §8 QA-HIST |
| [L-M1] | Modal: Process Processing Order — Zero Packing checkbox + optional memo (memo → order Comments + closing log); [Process Outbound → resolve warning] = REAL status change Processing → Prepare Shipment reflected on every screen; row re-judged green; if packing incomplete, handle separately and rescan | §3: full modal contract (checkbox gating → OQ-6, memo routing, close paths ✕/Close/backdrop), server action + idempotency [G-9], cross-screen propagation; §7 E-22–25; §8 QA-M1 |
| [L-M2] | Modal: Delete Scan Row — "Remove this scan?" + row identity (#N · tracking); Yes removes from list AND counts; deletion history kept in backend; No/✕/backdrop = no-op | §3: modal contract with dynamic `#scandelInfo` text; §5 deletion event; §7 E-26–29; §8 QA-DEL |

Wireframe defects to normalize in spec (not silently fix): (a) wf-bar has the "Modal: Process Processing Order" tab twice (lines 215/217) — cosmetic, note only; (b) [L-4.1] "(M2)" stale cross-ref to the pre-07-23 history modal.

---

## 2. SECTION OUTLINES (what B plans to write per template section)

**§1 Purpose & Users** — End-of-day closing operator (warehouse staff: Dean, Miranti in mock data; confirmer may be a manager — Yongwon in mock). Physical context that shaped decisions: scanner in hand, eyes on parcels not monitor (→ voice alerts, L-1.3), distance recognition (→ large red warning styling only, L-1.2), speed pressure (→ never-refresh scan loop [G-1], click-anywhere refocus). Operational moment: after packing, before carrier handover; ground truth = hand-counted physical parcels, not a system figure.

**§2 Screen Inventory & Wireframe Map** — 7 states + 2 modals table: s0 Before Start / s1 OK Scan / s2 Warning·Processing / s2b Warning·Unknown Order / s3 Warning·Duplicate / s4 Closing Complete / shist Closing History (page) / M1 Process Processing Order / M2 Delete Scan Row. Reach-how column = wf-bar tab labels exactly as rendered ("0 · Before Start (manual count)" etc.), plus in-page routes (pagetabs, [Process this order] button, row ✕). 1:1 map legend key ↔ §3 anchor.

**§3 Functional Specification** — One block per key in §1 inventory. Per block: Trigger / Exact behavior / Inputs+Outputs / Validation / Server action (proposed endpoint name + payload + idempotency key) / State transitions / User-visible feedback (toast text, sound, row tint). Named server actions I will spec: `closing.start(target)`, `closing.editTarget(new)`, `closing.cancel(confirm)`, `closing.scan(tracking, scanId)` → verdict {OK | NOT_OUTBOUNDED | DUPLICATE(of #n) | UNKNOWN}, `closing.deleteScan(rowId)`, `closing.processOutbound(orderId, zeroPackingChecked, memo)`, `closing.confirm()`, `closing.history.list()`, `closing.report.csv(date)`. State machine: `IDLE → IN_PROGRESS → (CONFIRMED | CANCELLED→IDLE)`; Confirm-enable predicate `ok == target && warnings == 0` evaluated server-side and mirrored client-side. Every confirming action gets a [G-2] toast with exact copy. Idempotency [G-9] called out per action (see E-25/29/31/35/37).

**§4 Business Rules** — (dated, rationale): single-OK-status rule (Prepare Shipment only, 07-23); manual physical count is the gate baseline, exact match incl. over-scan (07-23); no auto-confirm — human press required (07-23, protects against premature closing); unknown orders excluded from counts (07-23); duplicates not double-counted (digital replacement of Excel column-A dup check); server-side session persistence — refresh/navigation safe (encoded in L-1.BR); deletion history retained despite UI removal [G-8]; M1 is a real order-status mutation, not a closing-local flag; history rows are always "Match" by construction. Global cites: G-1, G-2, G-3b, G-7, G-8, G-9; page deltas only.

**§5 Data Capture** — (Lens A owns depth; B lists what QA/audit requires so nothing is droppable): scan event (every scan incl. duplicates/unknown/later-deleted: tracking, verdict, seq #, worker, ts), row deletion (actor, ts, deleted row snapshot), session lifecycle (start actor/ts/target; target edits old→new; cancel with discarded-scan snapshot; confirm actor/ts), M1 transitions (order, old→new status, checkbox state, memo, actor, ts) + auto-comment, voice-toggle changes (nice-to-have), CSV export events (who/when/which day), warning resolution linkage (warning → resolving event). Retention: history forever + per-day CSV reproducible.

**§6 Integrations** — Slack table rows landing on closing: comment @mention → #fulfillment-admin-comments (C0BMGEWM5QA) with entity no./text/time/author/deep link [CONFIRMED 08-03]; M1 memo → order Comments (thus mention-capable). Sheet/BI: Confirm → **Daily Shipping Status auto-update** (replaces manual paste; failure semantics → E-38/DQ-6); CSV export both from State 4 and per-history-row. Cross-page: Order ID cells (rendered blue) → order-detail deep link [G-12] — must be spec'd as real links; M1 status change propagates to View Orders/Order Detail. Print pipeline: **no Print button on this page** — G-4 mandate names "Closing report" as a surface but wireframe ships CSV-only → OQ-5.

**§7 Edge Cases & Error States** — full E-list below (Section 3 of this plan), each with expected behavior + verdict/toast/voice.

**§8 QA Acceptance Criteria** — Given/When/Then keyed to [L]/[E]; split **WF-RUN** (executable on live wireframe today — exact selectors exist) vs **ADMIN-ONLY** (needs real backend: persistence, concurrency, idempotency, Slack, sheet update). Counts + 3 worked examples below.

**§9 Out of Scope & Open Questions** — Out: label/invoice layouts (Phase 3-1), Zero Packing physical procedure, View Orders scan flows (referenced), Procurement Hub. Open questions: OQ/DQ lists below.

**§10 Decision Log** — 2026-07-13 initial wireframe (batch, 19-agent workflow); 2026-07-23 rework: OK = Prepare Shipment single criterion · box/size columns removed · manual-count target input introduced · exact-match + 0-warnings gate (over-scan = mismatch) · large OK panel removed (Dean) · large warning panel + action banner removed · Unknown Order state added · Closing History modal → separate page · pre-start screen simplified to count-only; 2026-08-03: scanner protocol elevated to global [G-1] with never-refresh emphasis · voice = en-US TTS "Please check this order" confirmed [G-3b] · global confirmation toast mandate [G-2] · @mention channel confirmed #fulfillment-admin-comments · instant-print mandate [G-4] reconfirmed (closing impact = OQ-5 only). No reversals specific to this page other than history modal→page (record it; State 4 "(M2)" text is the fossil).

---

## 3. LENS-B DEEP INVENTORY

### 3a. Edge-case candidate list [E-n] (exhaustive; grouped)

**Scan input & verdict**
- E-1 Empty submit: Enter/Scan with empty input → no row, no count change; define feedback (silent vs err toast).
- E-2 Malformed/truncated barcode (partial read): treated as unknown-order path or rejected client-side? Define min-length rule.
- E-3 Valid-format tracking with no matching order → "⚠ Unknown order", Order/Items/Status "–", voice, excluded from counts [L-2b.1].
- E-4 Order in Processing → "⚠ Not outbounded" + [Process this order] button in Notes [L-2.1].
- E-5 Order in any other non-Prepare-Shipment status (Shipped / Completed / Cancelled / Hold / Refunded) → warning per L-1.5; verdict label + whether M1 button appears is undefined → OQ-4.
- E-6 Duplicate scan (2nd scan of same tracking) → "⚠ Duplicate scan", Notes "Duplicate of #n — first scanned {time} ({worker})", not double-counted [L-3.1].
- E-7 Triple+ scan of same tracking → each repeat is its own warning row; Notes reference the FIRST OK scan (#n), not the previous duplicate.
- E-8 Duplicate whose original OK row was deleted: is the surviving/subsequent scan re-judged OK, or stays duplicate until rescan? → OQ-3.
- E-9 Scan attempt in State 0 (before start): input disabled [L-1.BR]; keyboard wedge input must go nowhere.
- E-10 Scan after Confirm Closing (State 4): input appears active in wireframe — locked or live? → OQ-1.
- E-11 Over-scan: OK count exceeds target (85th parcel) → mismatch, Confirm re-disabled, banner copy per L-1.8; resolution = edit count (↺) or delete extra rows.
- E-12 Scanner artifacts: trailing CR/LF/Tab, leading/trailing spaces, case — normalization rule → DQ-1.
- E-13 Wrong barcode type scanned (product EAN 8809…, order ID, Deleo no.) → unknown-order verdict; spec cross-note: this page matches tracking numbers ONLY (distinct from View Orders unified search).
- E-14 Same tracking number attached to 2+ orders (data anomaly / carrier reuse): which order is judged? Define deterministic rule (error verdict recommended) → DQ-2.
- E-50 Very long tracking string display: no truncation of the identifying tail; table stays one-screen [L-1.9].

**Manual count & session lifecycle**
- E-15 Target validation: 0, negative, non-numeric, non-integer, absurd (e.g., 10000) → block Start with visible error (wireframe silently no-ops — spec must define copy).
- E-16 Start Closing with empty input → blocked + error feedback (wireframe: silent return).
- E-17 Edit count below current OK (OK=10, target→8) → instant over-scan mismatch state; Confirm disabled.
- E-18 Edit count to exactly OK with 0 warnings → Confirm enables without any new scan.
- E-19 Edit-count Save with invalid value → reject, keep old value, error feedback.
- E-20 Cancel Closing with scans present → confirmation required; define dialog copy + whether discarded scans persist in backend (presumed yes per G-8) → OQ-8.
- E-21 Cancel Closing with 0 scans → returns to State 0 (confirm dialog still shown? define).
- E-41 Session spans midnight (start 23:50, confirm 00:10) → snapshot date attribution → OQ-7.
- E-42 Second session same day after a confirmed closing → allowed? History uniqueness → OQ-2.

**Warning resolution & row deletion**
- E-22 M1 with Zero Packing checkbox unchecked → is [Process Outbound] enabled? → OQ-6.
- E-23 M1 success: order status Processing → Prepare Shipment globally; closing row re-judged green in place (same seq #); warnings −1; memo (if any) → order Comments + closing log; [G-2] toast.
- E-24 M1 on order already transitioned by another operator (View Orders race): no double transition; row re-judges from current status; idempotent success or explicit "already outbounded" notice.
- E-25 M1 [Process Outbound] double-click → exactly one transition [G-9].
- E-26 M2 delete: Yes → row removed, ALL tiles/progress/gating recompute; No/✕/backdrop → zero change.
- E-27 Deleting an OK row breaks an exact match → Confirm re-disables immediately.
- E-28 Deleting a warning row (duplicate or unknown) → warnings −1; may newly satisfy gate.
- E-29 M2 Yes double-click / repeat delete of same row → single deletion, no error.

**Concurrency (ADMIN-ONLY)**
- E-30 Two operators scan the same tracking near-simultaneously → exactly one OK + one duplicate (server-arbitrated order), both feeds consistent.
- E-31 Two operators press Confirm simultaneously → exactly one closing record + one sheet update [G-9].
- E-32 Count edit by A while B scans → gate recomputed on one consistent state; no lost update.
- E-33 Session open on two devices → shared server state; both see same seq numbers/counts (sync latency → DQ-4).
- E-34 A cancels session while B mid-scan → B's next scan gets "no active closing session" error, not a silent new session.

**Network / device / environment**
- E-35 Network failure mid-scan (no response): retry must not double-append (per-scan idempotency key); UI must show unconfirmed state, not fake OK.
- E-36 Refresh / navigate away / crash mid-session → full state restored (target, list, counts, warnings) [L-1.BR]; nothing clears.
- E-37 Network failure on Confirm → retry must not create duplicate closing record or double sheet update.
- E-38 Daily Shipping Status update fails after confirm succeeds → closing stays confirmed; error surfaced + retry path → DQ-6.
- E-39 TTS unavailable (no voices / unsupported / muted): visual warning unaffected; no JS error; Test voice degrades gracefully.
- E-40 CSV download failure / zero-scan report → well-formed file or explicit error; never silent empty success.
- E-49 Printer offline: N/A on this page (no Print button) — state explicitly so QA doesn't invent it; CSV ≠ print [G-4 note, OQ-5].

**Focus & UI**
- E-48 Auto-refocus exceptions: click-anywhere refocus must NOT hijack typing in M1 memo, M2 modal, comment inputs, target edit field, or Comments hub search; refocus resumes when modal closes.
- E-46 Voice toggle OFF → warnings render red + toast but silent; toggle scope/persistence → DQ-3; toggling ON plays confirmation utterance (wireframe behavior).
- E-47 Comments hub: mark-all-read idempotent; unread badge count consistency; star/unstar reflected across Mentions/Saved panes.
- E-43 Day with no closing → no history row (gap is legitimate; no fabricated rows).
- E-44 History empty state (first use) → defined empty copy, CSV buttons absent.
- E-45 History never shows mismatch rows (footer rule); cancelled sessions not shown (data retained backend-side) → confirm under OQ-2/OQ-8.

**Count: 50 edge cases** (E-1…E-50).

### 3b. QA scenario plan (Given/When/Then, keyed to [L]/[E])

Runbook split: **WF-RUN** = executable now against the live wireframe (selectors below exist in the HTML); **ADMIN-ONLY** = spec'd now, executable only against the real admin (persistence, server, Slack, sheet, concurrency). Every warning-state scenario asserts BOTH the visual verdict pill text and the voice utterance ("Please check this order", en-US). Negative tests included in each block.

| QA block | Keyed to | WF-RUN | ADMIN-ONLY | Total |
|---|---|---|---|---|
| QA-S0 pre-start & start gating | L-0.1, E-9/15/16 | 4 | 2 | 6 |
| QA-SCAN input protocol & focus | L-1.1, L-1.BR, E-1/2/12/48 | 5 | 7 | 12 |
| QA-VERDICT engine (OK/Processing/other-status) | L-1.5, L-2.1, E-4/5 | 5 | 5 | 10 |
| QA-UNKNOWN | L-2b.1, E-3/13 | 4 | 2 | 6 |
| QA-DUP | L-3.1, E-6/7/8 | 4 | 3 | 7 |
| QA-VOICE | L-1.3, E-39/46 | 5 | 1 | 6 |
| QA-COUNT tiles/progress/gating math | L-1.4, L-1.8, E-11/17/18 | 4 | 4 | 8 |
| QA-TARGET edit & cancel | L-1.10, E-17–21 | 4 | 3 | 7 |
| QA-M1 process order | L-M1, E-22–25 | 4 | 4 | 8 |
| QA-DEL row deletion | L-M2, L-1.6, E-26–29 | 5 | 2 | 7 |
| QA-CONFIRM & State 4 | L-1.8, L-4.1/2/3, E-10/31/37/38/40 | 4 | 6 | 10 |
| QA-HIST history page | L-H.1, L-1.11, E-42–45 | 4 | 3 | 7 |
| QA-HUB comments hub | L-1.7, E-47 | 4 | 1 | 5 |
| QA-PERSIST & concurrency | L-1.BR, E-30–37 | 0 | 8 | 8 |
| **Totals** | | **56** | **51** | **107** |

(Target for the written spec: ≥100 scenarios; trim only exact duplicates during P3-3.)

### 3c. Three fully worked example scenarios

**QA-S0-02 (WF-RUN, negative) — Start Closing blocked on empty count [L-0.1][E-16]**
- Given: live wireframe loaded, wf-bar tab "0 · Before Start (manual count)" active (section `#s0` has class `state on`)
- And: input `#targetIn0` (placeholder "Hand-counted qty") is empty
- When: click button `#startBtn0` (label "Start Closing")
- Then: section `#s0` still has class `on`; section `#s1` does NOT have class `on` (no state switch)
- And: no scan input is visible in the active state (State 0 exposes only the count input per L-0.1)
- Real-admin extension (ADMIN-ONLY twin QA-S0-02b): a visible validation error is shown (copy TBD in spec, e.g., red toast "Enter the hand-counted parcel count first") — wireframe currently no-ops silently; spec will make the error explicit.

**QA-DEL-01 (WF-RUN) — Delete Scan Row modal: identity text, Yes removes row, No is a no-op [L-M2][L-1.6][E-26]**
- Given: wf-bar tab "1 · OK Scan (outbounded)" clicked → section `#s1` visible; its scan table shows 5 rows (#1–#5)
- When: click the ✕ button (`button.scandel`, title "Delete scan row") on row #3 (tracking YT2618100710184356, verdict pill `.cs-dup` text "⚠ Duplicate scan")
- Then: overlay `#m-scandel` gains class `open`; header text = "Delete Scan Row"; body bold text = "Remove this scan?"; `#scandelInfo` text = "#3 · YT2618100710184356"; note text contains "Deletion history is kept in the backend."
- When: click button "No" (`[data-close]` in `#m-scandel .foot`)
- Then: overlay loses class `open`; table still has 5 rows (row #3 present)
- When: click ✕ on row #3 again, then click `#scandelYes` (label "Yes — remove", red background)
- Then: overlay closes; row #3 is removed from the DOM; remaining rows #1, #2, #4, #5 keep their original sequence numbers (no renumbering)
- Real-admin extension (ADMIN-ONLY twin QA-DEL-01b): Warnings tile decrements 2→1, progress bar red segment shrinks, deletion event persisted with actor+timestamp [G-8]; second Yes on same row is a no-op [E-29][G-9]. (Wireframe does not recompute tiles — assert DOM removal only.)

**QA-VOICE-02 (WF-RUN) — Warning state auto-plays voice; toggle OFF silences; Test voice overrides [L-1.3][E-46][G-3b]**
- Given: live wireframe loaded, browser with Web Speech API available
- When: click wf-bar tab "2 · Warning · Processing (not outbounded)"
- Then: section `#s2` becomes active; `speechSynthesis.speak` is invoked with utterance text exactly "Please check this order", `lang` "en-US" (hook `window.speechSynthesis` to capture; section carries `data-voice="Please check this order"`)
- And: the row for tracking YT2618100710223471 has class `row-bad` and verdict pill `.cs-processing` with text "⚠ Not outbounded"; Notes cell contains button "Process this order"
- When: return to tab "1 · OK Scan (outbounded)" and click the voice toggle `#voiceToggle`
- Then: `#voiceState` text becomes "Off"; `.vtrack` gains class `off`
- When: click wf-bar tab "3 · Warning · Duplicate Scan"
- Then: NO new `speak` call occurs (voiceOn=false) while the row still shows `.cs-dup` "⚠ Duplicate scan" — visual warning is never suppressed [E-46]
- When: back on State 1, click `#voiceTest` (label "🔊 Test voice")
- Then: exactly one `speak` call with "Please check this order" fires even though the toggle is Off (test button temporarily overrides), and `#voiceState` still reads "Off" afterward.

---

## 4. MANDATORY-INCLUSION MAP (of the 12 owner-flagged items)

| # | Mandatory item | Lands on closing? | Where in this spec |
|---|---|---|---|
| 1 | Scanner protocol [G-1] | YES (named surface) | §3 L-1.1 + L-1.BR; §8 QA-SCAN (never-refresh, focus residency, select-all loop) |
| 2 | Global confirmation toast [G-2] | YES (all screens) | §3 per confirming action (Start, Save count, Cancel, Process Outbound, Delete row, Confirm Closing, CSV) with exact toast copies; §8 every block asserts toasts |
| 3 | Audio feedback [G-3] — voice branch | YES (named surface: Closing voice) | §3 L-1.3; §8 QA-VOICE; utterance text + en-US locale pinned |
| 4 | Instant carrier-agnostic print [G-4] | PARTIAL/AMBIGUOUS — decision-sources names "Closing report" as a print surface, wireframe has CSV download only | §6 print pipeline note + OQ-5; E-49 states printer edge is N/A unless OQ-5 adds a print button |
| 5 | Sample dual-view [G-13] | NO (Order Management) | — |
| 6 | Unrecognized matching behavior | NO (View Orders + Unrecognized Tracking) — but §4/§7 carry the L-2b.1 distinction note (tracking-not-found ≠ product-barcode unrecognized) with cross-link | §4, E-3/E-13 |
| 7 | Multiple tracking nos per inbound request [G-10] | NO (Inbound Request + View Orders); indirect only — closing scans carrier tracking, no delta | — |
| 8 | RTO Korean item names [G-6] | NO | — |
| 9 | Line-based location filter [G-14] | NO | — |
| 10 | Audit-mode-only visibility [G-14] | NO | — |
| 11 | JIT residual stock | NO | — |
| 12 | Comment @mention Slack routing [G-7] | YES (all screens; channel CONFIRMED #fulfillment-admin-comments `C0BMGEWM5QA`) | §6 Slack table; §3 L-1.7 delta; M1 memo → Comments path noted |

Landing on closing: **5 of 12** (items 1, 2, 3, 4*, 12; * = flagged ambiguous via OQ-5) + item 6 as a cross-reference note.

---

## 5. OPEN QUESTIONS (do not invent — flag)

### Owner must decide
- OQ-1 Post-confirmation scanning: State 4 still renders an active-looking scan input. After [Confirm Closing], is scanning locked? If an extra parcel is found after confirmation, what is the correction path (no "reopen closing" exists in the wireframe)?
- OQ-2 Is a second closing session on the same calendar day allowed (e.g., after a confirmed closing)? How does Closing History represent multiple sessions or cancelled sessions for one date (current table implies one row per date, always "Match")?
- OQ-3 If the original OK row of a duplicate pair is deleted (M2), is the surviving duplicate row auto-re-judged to OK, or must the operator delete it and rescan?
- OQ-4 Verdict labels for non-Processing abnormal statuses (Cancelled / Hold / Shipped / Completed / Refunded): same "⚠ Not outbounded" or distinct labels? Does [Process this order] (M1 is Processing→Prepare Shipment specific) appear for them, and what is the prescribed handling?
- OQ-5 G-4 mandatory item lists "Closing report" as a print surface, but the wireframe ships CSV download only — is a physically printed closing report required (making the local print agent relevant here), or is CSV the complete deliverable?
- OQ-6 M1 Zero Packing checkbox: mandatory gate for [Process Outbound → resolve warning] (button disabled until checked), or optional attestation?
- OQ-7 Session spanning midnight (start 23:50, confirm 00:10): which date does the history snapshot belong to — start date or confirmation date?
- OQ-8 Cancel Closing "discards" scan records from the UI — confirm they are still persisted in the backend (G-8 doctrine implies yes), and whether cancelled sessions should ever be visible anywhere in admin.

### Developer decides at build time
- DQ-1 Barcode input normalization: trim whitespace, strip scanner suffix chars (CR/LF/Tab), case handling, min/max length before lookup.
- DQ-2 Per-scan idempotency mechanism (client-generated scan UUID vs server dedupe window) and the deterministic rule for the same tracking number matching multiple orders (E-14; recommend explicit error verdict).
- DQ-3 Voice-toggle persistence scope (localStorage per device vs user profile) and default-ON restore per session.
- DQ-4 Multi-operator live-sync transport (polling vs WebSocket/SSE) and acceptable propagation latency for counts/rows.
- DQ-5 CSV format: encoding, column order, whether deleted rows appear with a `deleted` flag column ("all rows stored in the backend, fully included in the closing report export" implies inclusion — mark disposition).
- DQ-6 Daily Shipping Status update failure semantics: retry/queue, error toast copy, manual re-trigger affordance (closing record must stand regardless — E-38).
- DQ-7 Spec-side normalization of wireframe fossils: State 4 legend "(M2)" stale history-modal ref; duplicated "Modal: Process Processing Order" wf-bar tab. No behavior change — documentation hygiene.
- DQ-8 TTS voice selection fallback chain (wireframe: "Samantha" → any en-US → browser default) and behavior when zero voices are available (E-39).
