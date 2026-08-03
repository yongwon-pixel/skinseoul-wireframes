# Wireframe Fix List — found during P3-1 planning

> **Do not apply these now.** This is a backlog for a separate wireframe-edit pass (after P3-3/P3-4), so spec writing and wireframe editing never race on the same files. The specs are written against the **decided behavior** (see `_provisional-decisions.md`), not against the stale wireframe text below.
> Deploy rule reminder: any wireframe edit must go out through `/wf-deploy {slug}` (3-channel sync), never by editing the published copy.

Source: all 16 plans. Repo root for paths below: `~/yongwon-sync/claude/repos/skinseoul-wireframes/`.

---

## A. Stale text that contradicts a dated decision (fix required)

**[WF-1] view-orders — State 6b completion banner says "Carrier recorded automatically".**
File: `wms2/view-orders/index.html` · State 6b (`s6b`) completion banner.
Contradicts the State 6 legend footer and the 2026-08-03 decision that automatic Carrier recording is NOT supported (`_review.md` C-1, PD-9).
Fix: remove the carrier clause from the banner. Keep the rest (exact-match result, locations, INBOUNDED, Received Date). Suggested text: "… · Received Date recorded automatically · Carrier is not recorded".
Raised by: view-orders.A Q2 / view-orders.B OQ-4 / supervisor memo.

**[WF-2] inbound-request — State 1 legend footer says "Received Date + Carrier are recorded automatically".**
File: `wms2/inbound-request/index.html` · State 1 footer behavior paragraph (rule a).
Same contradiction: legend S3-10 already states there is no Carrier column and no auto carrier capture (2026-08-03).
Fix: drop "+ Carrier" from the footer sentence.
Raised by: inbound-request.A S1-F / inbound-request.B (State 1 off-legend paragraph).

**[WF-3] view-orders — State 3 legend item 4 still labelled "proposal".**
File: `wms2/view-orders/index.html` · State 3 legend #4 (Cancel Inbound disabled after outbound).
Now adopted as a rule (PD-10, supervisor ruling on proposal-state items).
Fix: remove the "(proposal)" qualifier once the owner confirms PD-10.
Raised by: view-orders.A Q1 / view-orders.B OQ-8.

**[WF-4] closing — State 4 legend references "(M2)" for closing history.**
File: `wms2/closing/index.html` · State 4 legend #1.
Fossil from the pre-2026-07-23 design when history was a modal; history is now a separate page (`shist`), and M2 is the Delete Scan Row modal — so the reference is not just stale, it points at the wrong modal.
Fix: replace "(M2)" with "Closing History page".
Raised by: closing.A OQ-D6 / closing.B DQ-7.

**[WF-5] closing — State 1 legend #2 contradicts the removal of the large warning panel.**
File: `wms2/closing/index.html` · State 1 legend #2 ("the large panel is used only in warning states") vs State 2 legend ("large warning panel + action banner removed 2026-07-23").
Net truth: no large red panel remains; the only large panel is State 4's green completion status.
Fix: reword State 1 legend #2 to "large panel appears only on the State 4 completion screen".
Raised by: closing.A L-1.2 note / closing.B (§1 inventory note).

---

## B. Wireframe gaps vs. global rules (add missing affordance)

**[WF-6] tracking-missing — ✕ row removal has no confirmation, no reason, and no toast.**
File: `wms2/tracking-missing/index.html` · `.xdel` button in each pool row.
[G-2] requires a toast on every confirming action; [G-8] wants the "why"; the button sits next to the primary action at scan speed.
Fix (per PD-60): add a confirm dialog + mandatory reason select (mis-registration / routed to inbound request / no action needed; the second option takes an Inbound No. field per PD-64) + green toast.
Raised by: tracking-missing.A Q1 / tracking-missing.B Q1 + E-16.

**[WF-7] closing — Cancel Closing has no confirmation dialog.**
File: `wms2/closing/index.html` · State 1 target banner, `✕ Cancel Closing`.
The legend says cancelling "discards scan records", but the wireframe cancels immediately.
Fix: add the confirm dialog (copy to come from the spec) before returning to State 0.
Raised by: closing.B L-1.10 ("dialog NOT in wireframe — spec must define copy").

**[WF-8] closing — Start Closing with an empty/invalid count silently no-ops.**
File: `wms2/closing/index.html` · `#startBtn0` / `#targetIn0`.
No error copy, no visual feedback — indistinguishable from a broken button.
Fix: add an inline/red-toast validation error for empty, 0, negative, and non-integer input.
Raised by: closing.B E-15/E-16, QA-S0-02.

**[WF-9] ready-to-outbound — picking list modal (M1) has no sample-set lines.**
File: `wms2/ready-to-outbound/index.html` · `#m-pick` `.picktbl`.
[G-13] requires internal picking artifacts to show WHICH sample and HOW MANY (PD-36).
Fix: **conditional on owner approval of PD-36 and on PD-51 (the sample-set definition source) being answered** — add sample rows to the picking table. Do not add until both land.
Raised by: ready-to-outbound.A Q3 / ready-to-outbound.B OQ-B5 + E-28.

**[WF-NEW-D · tracking-missing] — `.xdel` double-click removes one row but decrements both counters twice.**
*(Page-scoped ID on purpose: the next free numeric ID was claimed concurrently by the closing, ready-to-outbound and order-management passes. This is the same defect the `tracking-missing.md` spec cites as `WF-NEW-D`, so the two references resolve to each other.)*
File: `wms2/tracking-missing/index.html` · lines 400–404, the `.xdel` click handler.
`document.querySelectorAll('.xdel').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation(); b.closest('tr').remove(); poolDec();}))` — no guard, no debounce. After the first click the `<tr>` is detached but the button is still its descendant, so `b.closest('tr')` still resolves, `.remove()` silently no-ops, and `poolDec()` fires a second time: one row removed, `#poolCount` / `#poolCountBottom` decremented twice. Counters and rendered rows diverge.
Violates [G-9] (every confirming action must be double-click safe) and the count invariant the tracking-missing spec states as `[BR-33]` / `[BR-41]`.
Note the asymmetry that makes it easy to miss: the sibling handler `finishMatch()` **does** guard (`const row=document.getElementById('poolrow1'); if(row){…}`); `.xdel` does not.
Fix: mirror `finishMatch()`'s guard — resolve the row first and call `poolDec()` only when a row was actually attached and removed.
Raised by: `_verify/m2-tracking-missing.md` F3 · `_verify/m1-tracking-missing.md` D-2. Filed in `tracking-missing.md` §2.4.10 / §2.5 as **WF-NEW-D**; current behavior asserted by QA-WFQ-07, correct behavior by QA-NEG-03 `[ADMIN]`.

**[WF-NEW-E · tracking-missing] — Comments-hub pane headers diverge from the corpus-canonical strings.**
*(Page-scoped ID, same reason as above; cited as `WF-NEW-E` in `tracking-missing.md`. Related: the closing pass filed the same class of divergence for its own page — a single `[G-7]` amendment publishing the six hub strings closes both.)*
File: `wms2/tracking-missing/index.html` · `#inbox1` `.paneheader`, lines 227 and 234.
Ships `Comments mentioning me` and `Saved comments`; four of the eight pages (order-detail, order-management, ready-to-outbound, stock-status) ship `Comments mentioning me · Click to open the order` and `Saved comments · Click to open the order`. [G-7] states the hub is identical on all eight screens but does not yet publish the pane strings as byte-exact contract, so six QA suites assert mutually incompatible strings.
This page's `Unstar to remove from the list` and `Mark all read` are **already canonical — do not change them.**
Fix: adopt the two majority header strings here, and publish the six hub strings in `_global-rules.md` [G-7] so the other divergent pages can be corrected against one source.
Raised by: `_verify/m3a-cross-page.md` D7. Filed in `tracking-missing.md` §2.5 as **WF-NEW-E**; `[WF]` assertions QA-CMT-03 / QA-CMT-05, `[ADMIN]` assertion QA-CMT-15.

**[RTO-WFX-9 · ready-to-outbound] — the progress label lags the run by one tick, so it shows the previous action's mode string.**
*(Page-scoped ID on purpose: `_verify/m2-ready-to-outbound.md` S-2 proposed "WF-15", but that numeric ID was claimed concurrently by the closing, tracking-missing and order-management passes. This spec already keys its page-local defects `[RTO-WFX-1]`…`[RTO-WFX-8]`, so this one continues that series and the two references resolve to each other.)*
File: `wms2/ready-to-outbound/index.html` · `.bulk-run` click handler (approx. lines 404–411).
The handler sets `fill.style.width='0%'` **synchronously** on click, but assigns `label.childNodes[0].textContent` only inside the 250 ms `setInterval` callback. For the opening ~250 ms of every run the label therefore still carries the *previous* action's copy — on a fresh load, the idle demo copy `Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion`. Measured on 2026-08-03: 7 of 38 in-flight samples of a Bulk Outbound run read the print mode string, and 6 of 38 samples of the following print run read `refreshes after completion`. [BR-8]/`[L-5]` make the mode string a contract ("this is how the operator learns, mid-run, whether their selection is about to disappear"), so a crossed-over mode string is wrong from the first frame, not just from the first tick.
Fix: write the label once immediately before `setInterval` starts, mirroring the existing synchronous `fill.style.width='0%'` line.
Raised by: `_verify/m2-ready-to-outbound.md` S-2 (adversarial QA execution, 2026-08-03). Until it lands, `ready-to-outbound.md` §8.0 carries a reading rule bounding every "during the run" assertion to the first tick onward.

---

## C. Dead code / leftovers (cleanup, no behavior change)

**[WF-10] tracking-missing — v1 CSS/JS leftovers from the 2026-07-23 simplification.**
File: `wms2/tracking-missing/index.html`.
Unused selectors and script blocks for features that were removed: `.trk` inline inputs, `.shelf`, `.wait` chips, `.slack-pill`, per-PIC group classes (`.picava`, `.picname`, `.cntchip`), `.logsec` (resolved log), the trk-input script block, and the "Resolved button" JS.
Risk if left: a developer reading the file re-implements per-PIC groups, the bulk bar, the Slack column, the resolved log, or the search bar — all deliberately removed.
Fix: delete. Both plans already exclude them from the spec.
Raised by: tracking-missing.A (non-legend note) / tracking-missing.B (§1 dead-artifact list).

**[WF-11] inbound-request — HTML comment for the removed "View Orders link info" modal.**
File: `wms2/inbound-request/index.html` · around line 701.
The modal was removed 2026-08-03; the commented block remains.
Fix: delete the comment block so coverage checks and future readers don't resurrect it.
Raised by: inbound-request.A (removed-modal entry).

**[WF-12] closing — wf-bar lists "Modal: Process Processing Order" twice.**
File: `wms2/closing/index.html` · wf-tab bar (approx. lines 215 and 217).
Demo chrome duplication; would be double-counted by a naive coverage check.
Fix: remove the duplicate tab.
Raised by: closing.A (chrome note) / closing.B (§1 defect note).

---

## D. Minor / optional

**[WF-13] view-orders — live barcode feed cap stated as a range ("max 10–20 rows").**
File: `wms2/view-orders/index.html` · State 1 legend #16.
Ambiguous for QA assertions; the spec must fix one number.
Fix: pick a single value (20 recommended) in both the legend and the spec.
Raised by: view-orders.A (dev question) / view-orders.B DQ-3.

**[WF-VO-1] view-orders — Comments-hub copy is the corpus-minority form on six strings.**
> Page-scoped ID on purpose: three concurrent remediation passes each claimed `WF-15` in this file, so this entry uses the page-scoped form (precedent: `[RTO-WFX-n]`). It is cited as `WF-VO-1` throughout `view-orders.md`.
File: `wms2/view-orders/index.html` · `.paneheader` in all nine `.inboxdd` blocks + the search-results header and empty state built in the inline script (`… results · newest first · click to open the order page` / `No matching Comments`).
[G-7] makes the hub one control replicated on all eight screens, so its copy is a byte-exact cross-page contract. This page ships: `Comments where I'm tagged · Click to open the order page` · `Comments I saved · Click to open the order page` · `Unstar to remove from list` · `Mark all as read` · `{n} results · newest first · click to open the order page` · `No matching Comments`. Five other specs use: `Comments mentioning me · Click to open the order` · `Saved comments · Click to open the order` · `Unstar to remove from the list` · `Mark all read` · `… click to open the order` · `No matching comments`. Every spec asserts its own form byte-exactly, so no single implementation can satisfy all eight QA suites.
Fix: **conditional and corpus-wide — do not edit this page alone.** `[G-7]` must first publish the six canonical strings; then all eight wireframes and all eight QA suites change in one pass. Editing only view-orders would break `view-orders.md`'s [WF] assertions (QA-C-03/05/06/07) without fixing the divergence.
Raised by: M3a cross-page verification 2026-08-03 (D7) · `view-orders.md` §2.4 / §9.5 CP-4 / QA-C-18.

**[WF-14] stock-status — two modals have no legend dots.**
File: `wms2/stock-status/index.html` · `m-auditlog` (Past Audit Logs list — currently covered by legend 15) and `m-adjlog6` (06-30 ADJUST detail — a second instance of M2).
Not a coverage gap (both plans account for them), but a legend annotation would make the 1:1 map self-evident.
Fix (optional): annotate both in the legend, or leave and rely on the spec's §2 note.
Raised by: stock-status.A / stock-status.B (§1 inventory notes).

**[WF-15] closing — Comments hub copy diverges from the cross-page `[G-7]` contract.**
File: `wms2/closing/index.html` · `#inbox1` `.paneheader` in both panes.
The hub is one component on all eight screens, so its strings are a byte-exact contract. Closing renders "Comments where I'm tagged" / "Comments I saved" / "Unstar to remove from this list"; the four-page majority (order-detail · order-management · ready-to-outbound · stock-status) renders "Comments mentioning me · Click to open the order" / "Saved comments · Click to open the order" / "Unstar to remove from the list". Closing and inbound-request are the two outliers.
Fix: replace the two pane headers and the unstar hint with the canonical strings. "Mark all read" is already canonical and must not change. Inbound-request needs the identical edit.
Risk if left: the spec's `[ADMIN]` copy (closing.md §3.8) and the wireframe's `[WF]` copy stay permanently forked, and two QA suites assert strings that cannot both pass one implementation.
Raised by: M3a cross-page verification D7 (2026-08-03) · specced in `closing.md` §3.8 with the `[WF]`/`[ADMIN]` split already in place (QA-HUB-01/02 vs QA-HUB-09).

---

## E. Explicit NON-fixes — do not "correct" these

Recorded so a later agent doesn't treat an intentional artifact as a defect.

- **view-orders M6 demo header "Inbound No. 202607120002" vs State 6 banner "…0001"** — intended renumbering (supervisor 판단 14). Not a contradiction.
- **ready-to-outbound page title "Ready to be Outbonded"** — the actual admin's spelling, deliberately preserved (legend footnote).
- **inbound-request State 1 has no dot 13** — vacated by the 2026-08-03 renumbering; declared in the spec's §2.
- **stock-status legend starts at 5 (no dots 1–4)** — page-local numbering; declared in the spec's §2.
- **order-management legend 3 has no on-screen dot** — it marks a *removed* feature (Bulk Hold Shipment) and must stay in the legend as a negative entry.
- **Deleo Tracking No. absent from View Orders but present on Order Detail** — deliberate asymmetry (2026-07-21/22).
- **Wireframe demo limitations that are not defects** (QA must tag these `[ADMIN]`, not file bugs): inbound-request filter chips and checkboxes are inert; inbound-request always toasts on Register regardless of validation; ready-to-outbound does not lock the bulk buttons while a batch runs and does not recompute tiles after row changes; closing does not recompute tiles after a row deletion; order-management preview data is static.

---

## F. Appended 2026-08-03 — found while writing `specs/order-management.md`

> These seven were raised by the `order-management` spec (§2.4) and are registered here so a QA runner cross-checking the backlog finds them. Each keeps the `· proposed` suffix in its ID because that suffix **is** its status: the wireframe-edit pass has not yet adjudicated them, and the spec cites them by the full token `[WF-n · proposed]`. Same deploy rule as the rest of this file — do not apply now; ship through `/wf-deploy order-management`. File for all seven: `wms2/order-management/index.html`.
>
> **⚑ Number collision across this whole 2026-08-03 remediation round — do not key on a bare number.** Several agents appended to this file in the same round and independently reused the next free numbers. As of this writing the bare-numbered new entries are `[WF-15] ready-to-outbound` (progress label) and `[WF-15] closing` (hub copy), alongside this section's `[WF-15 · proposed]` … `[WF-21 · proposed]` for order-management; the tracking-missing pass sidestepped the clash by re-keying its two entries as `[WF-NEW-D]` / `[WF-NEW-E]`. These are all **different defects on different files**. This section's ids never collide as *tokens* — they always carry the `· proposed` suffix, and `order-management.md` cites only that form — but they do collide as *numbers*, and none may be renumbered unilaterally: each is already cited by a shipped spec, and rule "never renumber existing IDs" binds every one of them. **A wireframe-edit pass must key on the full token plus the named file, never on the bare number.** Re-issuing the round's new entries into a clean, non-overlapping range (with redirect notes and same-commit citation updates in every affected spec) is an owner/orchestrator call.
>
> **⚑ Factual correction for any hub-copy fix that names this page.** `[WF-15] closing` states that the four-page majority (including order-management) renders `Unstar to remove from the list`. Verified against `wms2/order-management/index.html:187`, **this page renders `Unstar to remove from list`** (no `the`) — which is what `order-management.md` §3.10 and QA-CMT-03 assert byte-exactly, and which §3.10 declares as a knowingly-kept divergence because the wireframe is SST for UI copy (`_review` §3.9) and the corpus has no majority on that string (2 / 2 / 2 / 1). The six canonical hub strings still need publishing in `_global-rules` `[G-7]`; until they are, no page's `[WF]` copy should be edited toward a string that no wireframe actually contains.

**[WF-15 · proposed] order-management — M1 preview collapse row under-spans the table by one cell.**
The collapse row `⋯ +8 more rows` uses `colspan="6"` while the preview `<thead>` has **7** `<th>` (`Recipient · Country · SKU · Product Name · Qty · Campaign · Carrier (auto)`).
Fix: `colspan="7"`.
Documented by QA-IMP-35; spec §3.2.4.

**[WF-16 · proposed] order-management — M2 `Start Assignment (ON)` closes silently.**
The footer button carries `data-close` but has **no `id`** and **no toast handler**, so a confirming action produces no confirmation. Contradicts `[G-2]`, which `_review.md` C-6 rules wins over wireframe omissions.
Fix: add an `id` and the green toast defined in the spec's §3.6.5.
Documented by QA-SMP-30; behaviour asserted by QA-SMP-06.

**[WF-17 · proposed] order-management — M3 `Cancel Selected Periods` fires at zero selection and has no confirm step.**
`#sampCancelBtn` toasts unconditionally, including when no checkbox is checked, and no confirm dialog precedes a cancellation that can switch off a company-wide `forever` campaign.
Fix: disable at zero selection, and add the confirm dialog defined in the spec's §3.7.5 (`[PD-5 · OWNER-PENDING]`).
Documented by QA-SMP-31; behaviour asserted by QA-SMP-20 / QA-SMP-21.

**[WF-18 · proposed] order-management — two independent toast nodes can overlap.**
`#mktConfirm` creates `#gtoast` and `#sampCancelBtn` creates `#gtoast2`, both fixed at `top:16px; right:16px`, so two toasts can occupy the same coordinates simultaneously.
Fix: one toast slot (replace) or an explicit stack.
Documented by QA-GBL-09; spec `[L-F5]`, [E-62].

**[WF-19 · proposed] order-management — M2 `forever` leaves the end fields enabled.**
The `forever (no end date)` checkbox ships **checked** while `End date` and `Time` remain enabled and editable, contradicting the specified mechanic (`forever` wins; end fields cleared and disabled).
Fix: clear **and** disable the end fields while `forever` is checked.
Documented by QA-SMP-33; spec §3.6.3, [E-23].

**[WF-20 · proposed] order-management — no modal responds to `Esc`.**
There is no `keydown` listener anywhere in the file, yet `Esc` is a specified dismissal path.
Fix: add `Esc` dismissal to all three overlays.
Documented by QA-GBL-10; spec §3.2.6, [E-97].

**[WF-21 · proposed] order-management — the Comments hub does not close on an outside click, and carries dead guards for the behaviour.**
`onclick="event.stopPropagation()"` on `.csearch` and `e.stopPropagation()` on the hub button, the tab buttons and the stars were written to protect a `document`-level close handler that was never added. The guards are dead code and the hub can only be closed by clicking its own trigger again.
Fix: add the outside-click close (and `Esc`, with WF-20).
Documented by QA-CMT-20; spec §3.10, [E-97].

---

## G. Appended 2026-08-03 — found while remediating `specs/inbound-request.md`

> Page-scoped ID deliberately, not a `WF-n`: this remediation round produced three independent `[WF-15]` entries on three different files (see section F's collision warning), so a new number would compound the problem. `inbound-request.md` cites this entry by the full token `[IR-WFX-1 · proposed]`, which cannot collide. Same deploy rule as the rest of this file — do not apply now; ship through `/wf-deploy inbound-request`.

**[IR-WFX-1 · proposed] inbound-request — Comments-hub pane strings diverge from the rest of the corpus.**
File: `wms2/inbound-request/index.html` · `#inbox1` `.paneheader` in both panes (lines 244 and 249).
This page renders `Comments where I'm tagged` / `Mark all as read` / `Comments I saved` / `Unstar to remove from list`. Across the eight screens the same four strings have 3, 2, 4 and 4 variants respectively, so only two of them have a majority at all: the mentions header (`Comments mentioning me · Click to open the order`, 4 pages) and the read-all action (`Mark all read`, 6 pages — this page and view-orders are the two that say `Mark all as read`). The saved header and the unstar hint have **no** majority (`Unstar to remove` 1 · `… from the list` 2 · `… from this list` 2 · `… from list` 2, this page and order-management).
Risk if left: the hub is one component on all eight screens and every spec asserts its strings byte-exactly in QA, so the eight QA suites cannot all pass against a single implementation.
Fix: **conditional on `_global-rules` `[G-7]` publishing the six shared hub strings as byte-exact contract.** Do not edit before that — for two of the four strings there is no majority to converge on, and editing toward a string no wireframe contains would just move the fork. Once `[G-7]` publishes, apply the canonical strings here, re-baseline `inbound-request.md` QA-F-02 / QA-F-03, and retire QA-F-11 (the `[ADMIN]` half that currently carries the "follow `[G-7]`" contract).
Related, same root cause, do not fix independently: `[WF-15] closing`, `[WF-16] tracking-missing`, and section F's factual correction for `order-management`.
Raised by: M3a cross-page verification D7 (2026-08-03) · specced position in `inbound-request.md` §2.4 obs. 3 / §3.1.13 / §9.1 / QA-F-11.

---

## H. Appended 2026-08-03 — found while remediating `specs/stock-status.md`

> Page-scoped IDs deliberately, not `WF-n`: by the time this pass ran, `WF-15` had been claimed independently by the ready-to-outbound, closing and order-management passes and `WF-16` by closing/tracking-missing and order-management (see section F's collision warning). `stock-status.md` cites these two by the full tokens `[INV-WFX-1 · proposed]` / `[INV-WFX-2 · proposed]`, which cannot collide. Same deploy rule as the rest of this file — do not apply now; ship through `/wf-deploy stock-status`. File for both: `wms2/stock-status/index.html`.
>
> **⚑ Factual correction for any hub-copy fix that names this page.** `[WF-15] closing` lists stock-status inside the "four-page majority" said to render `Unstar to remove from the list`. Verified against `wms2/stock-status/index.html` (`#inbox1`, saved pane `.paneheader`), **this page renders `Unstar to remove from this list`** (with `the` → `this`), which is what `stock-status.md` §3.12 states and what its `[WF]` tier asserts. On the unstar hint the corpus splits 1 / 2 / 2 / 2 with no majority; stock-status is in the `… from this list` pair together with closing, not in the `… from the list` pair. The other five hub strings on this page **do** match the recommended majority. Same conclusion as the order-management and inbound-request corrections: publish the six strings in `_global-rules` `[G-7]` first, then edit every page in one commit — never edit one page toward a string no wireframe contains.

**[INV-WFX-1 · proposed] stock-status — M1 total note hard-codes "the 3 new additions" against a single `[NEW]` row.**
File: `wms2/stock-status/index.html` · `#m-adjust` `.note` (approx. line 521).
The note reads `Total stock loss: +₩46,260 (target 0) · the 3 new additions are not losses — on confirm, Current Stocks · Available update immediately; monthly audit logs retained.` The same modal renders exactly **one** `[NEW]` row (SKU `100048201`, `0 → 3`), and `#m-auditlog` records `New Additions 1` for the 2026-07-22 session. The fixture states the count in three places and `3` is the odd one out — it is the added *quantity*, not the number of additions.
Risk if left: the sentence is a byte-exact `[WF]` QA contract, so a developer either hard-codes `3` or infers the wrong formula (adjustments + additions). `stock-status.md` §3.13 specifies the templatised form `the {n} new addition(s) are not losses`.
Fix: change `the 3 new additions are not losses` → `the 1 new addition is not a loss`, and update `stock-status.md` `QA-AUD-23`'s expected string in the same commit (`QA-AUD-44` already carries the `[ADMIN]`-tier contract and needs no change).
Raised by: adversarial QA execution of `stock-status.md` §8 (2026-08-03, item 5) · specced position in `stock-status.md` §3.13, QA-AUD-23, QA-AUD-44.

**[INV-WFX-2 · proposed] stock-status — Inbound Form note points at the retired control "Request Inbound".**
File: `wms2/stock-status/index.html` · `#p-inbound` `.form-note`.
Final sentence reads `For order-linked inbound, use Request Inbound on View Orders / the order detail.` **`Request Inbound` is a retired control name** — `order-detail.md` `BR-4` states it "is retired and must not reappear", `BR-40` lists it among removed features, and that page's QA asserts the string appears nowhere. Neither named screen has such a control: View Orders uses row `Inbound` / `Inbound + Outbound` / `Bulk Inbound (Selected)`; Order Detail uses per-row `Inbound` + `Bulk Inbound Selected Items`.
Risk if left: the note is a byte-exact `[WF]` QA contract, so the retired name propagates into the build and the note sends an operator to a button that does not exist — the exact failure `BR-4` was written to prevent.
Fix: replace the final sentence with `For order-linked inbound, use the row Inbound buttons on View Orders or Order Detail.`, and update `stock-status.md` `QA-FRM-03` in the same commit (`QA-FRM-20` already carries the `[ADMIN]`-tier corrected copy and the negative assertion, and needs no change).
Raised by: M3a cross-page verification D9 (2026-08-03) · specced position in `stock-status.md` §3.18, QA-FRM-03, QA-FRM-20.

---

## I. Appended 2026-08-03 — found while remediating `specs/order-detail.md`

> Page-scoped ID deliberately, not a `WF-n`: by the time this pass ran, `WF-15` had already been claimed independently by the ready-to-outbound, closing and order-management passes (see section F's collision warning). `order-detail.md` cites this entry by the full token `[OD-WFX-1 · proposed]`, which cannot collide. Same deploy rule as the rest of this file — do not apply now; ship through `/wf-deploy order-detail`.

**[OD-WFX-1 · proposed] order-detail — the Change Status dropdown does not close on an outside click.**
File: `wms2/order-detail/index.html` · `#statusdd` (State 1) and `#statusddH` (State 2); the `data-open` toggle handler.
Measured 2026-08-03 with headless Chromium: with `#statusdd` open, a click on the page background leaves it open (`visible before = true`, `after = true`). The page has **no** document-level click handler — a grep across all ten `wms2/*/index.html` files finds one only in `ready-to-outbound/index.html`. The asymmetry that makes this easy to miss: the delete modal **does** implement dismissal (`overlay.addEventListener('click', e => { if (e.target === o) … })`), and all three of its dismissal paths pass QA (`QA-DEL-4/5/6`). The spec assumed the dropdown had the same symmetry; the drawing does not.
This is a **missing affordance, not stale text**: the specified behavior is correct and unchanged — `order-detail.md` `[L-8]` step 1 and `[E-46]` state that clicking elsewhere closes the dropdown with no status change and no event (`NE-2`).
Risk if left: `QA-STA-4` was tagged `[WF]` and fails against a wireframe that is otherwise behaving as drawn, so an unaided QA agent files a false bug. It has therefore been retagged `[ADMIN]` in `order-detail.md` §8 with the tier reason stated inline, and the page's §2.5 A now lists this entry — previously that section asserted that no `_wireframe-fixes` entry targets this file.
Fix: add an outside-click handler that closes the open dropdown (both `#statusdd` and `#statusddH`) without changing the status, mirroring the modal's backdrop pattern. In the same commit, flip `QA-STA-4` back to `[WF]` in `order-detail.md` §8 (the scenario body needs no edit), restore it to §8.3's step-4 run list, and update the §8.1 counts (`[WF]` 68 → 69, `[ADMIN]` 93 → 92).
Raised by: `_verify/m2-order-detail.md` F-4 (adversarial QA execution, 2026-08-03) · specced position in `order-detail.md` §2.5 A, §9.5, `[L-8]`, `[E-46]`, QA-STA-4.
