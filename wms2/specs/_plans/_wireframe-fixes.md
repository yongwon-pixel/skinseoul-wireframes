# Wireframe Fix List — found during P3-1 planning

> **Do not apply these now.** This is a backlog for a separate wireframe-edit pass (after P3-3/P3-4), so spec writing and wireframe editing never race on the same files. The specs are written against the **decided behavior** (see `_provisional-decisions.md`), not against the stale wireframe text below.
> Deploy rule reminder: any wireframe edit must go out through `/wf-deploy {slug}` (3-channel sync), never by editing the published copy.

Source: all 16 plans. Repo root for paths below: `~/yongwon-sync/claude/repos/skinseoul-wireframes/`.

> **Batch status — 2026-08-03 (owner-approved).** Every entry in this register is now **APPLIED**. The last open cluster was the Comments-hub copy fork (`[WF-VO-1]` · `[WF-15] closing` · `[WF-NEW-E]` · `[IR-WFX-1]` and the §F / §H factual corrections), which was blocked on `_global-rules.md` `[G-7]` publishing the canonical strings. `[G-7]` **v1.2** now publishes them as **HUB-1…HUB-7**, and all eight wireframes plus all eight spec QA suites were moved to them in one commit — the condition every one of those entries attached to its own fix. Verified with headless Chromium across all eight pages: **82 assertions PASS / 0 FAIL**, 0 `pageerror` per page. Two of this register's own corpus tallies were wrong and are corrected in place (see `[WF-15] closing` and `[IR-WFX-1]`): both omitted `view-orders`, so the unstar hint split is **3 / 2 / 2 / 1**, not 2 / 2 / 2 / 1 and not a four-page majority.

---

## A. Stale text that contradicts a dated decision (fix required)

**[WF-1] view-orders — State 6b completion banner says "Carrier recorded automatically".**
File: `wms2/view-orders/index.html` · State 6b (`s6b`) completion banner.
Contradicts the State 6 legend footer and the 2026-08-03 decision that automatic Carrier recording is NOT supported (`_review.md` C-1, PD-9).
Fix: remove the carrier clause from the banner. Keep the rest (exact-match result, locations, INBOUNDED, Received Date). Suggested text: "… · Received Date recorded automatically · Carrier is not recorded".
Raised by: view-orders.A Q2 / view-orders.B OQ-4 / supervisor memo.
**APPLIED 2026-08-03** — banner clause replaced with the spec's exact wording `Carrier is not recorded` (view-orders.md §3.9 `[L-S6b-1]`).

**[WF-2] inbound-request — State 1 legend footer says "Received Date + Carrier are recorded automatically".**
File: `wms2/inbound-request/index.html` · State 1 footer behavior paragraph (rule a).
Same contradiction: legend S3-10 already states there is no Carrier column and no auto carrier capture (2026-08-03).
Fix: drop "+ Carrier" from the footer sentence.
Raised by: inbound-request.A S1-F / inbound-request.B (State 1 off-legend paragraph).
**APPLIED 2026-08-03 (owner-approved batch)** — verified in the drawing: the footer now reads `Received Date is recorded automatically at inbound and shown in the Request List (not a form input) — automatic Carrier recording is not supported and there is no Carrier column (confirmed 2026-08-03)`. Stronger than the requested edit: the clause is negated explicitly rather than merely dropped. Playwright-asserted (positive + negative on the stale string).

**[WF-3] view-orders — State 3 legend item 4 still labelled "proposal".**
File: `wms2/view-orders/index.html` · State 3 legend #4 (Cancel Inbound disabled after outbound).
Now adopted as a rule (PD-10, supervisor ruling on proposal-state items).
Fix: remove the "(proposal)" qualifier once the owner confirms PD-10.
Raised by: view-orders.A Q1 / view-orders.B OQ-8.
**APPLIED 2026-08-03** — PD-10 is provisionally adopted, so the qualifier reads `— adopted provisionally (2026-08-03, owner review pending)` rather than being removed outright.

**[WF-4] closing — State 4 legend references "(M2)" for closing history.** ✅ **Applied 2026-08-03** (closing wireframe edit pass, owner-approved batch; Playwright-verified).
File: `wms2/closing/index.html` · State 4 legend #1.
Fossil from the pre-2026-07-23 design when history was a modal; history is now a separate page (`shist`), and M2 is the Delete Scan Row modal — so the reference is not just stale, it points at the wrong modal.
Fix: replace "(M2)" with "Closing History page".
Raised by: closing.A OQ-D6 / closing.B DQ-7.

**[WF-5] closing — State 1 legend #2 contradicts the removal of the large warning panel.** ✅ **Applied 2026-08-03** (same pass as WF-4).
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
**APPLIED 2026-08-03 (owner-approved batch)** — verified in the drawing: `.xdel` now opens `#m-remove` (M2) carrying `#rmReason` (mandatory, gates `#rmConfirm`), the conditional `#rmInbound` field with 12-digit validation per PD-64, `#rmMemo` (mandatory on `Other`), and the green toast on confirm. One-click removal is retired. Playwright-asserted: modal opens, confirm disabled at empty reason, toast fires.

**[WF-7] closing — Cancel Closing has no confirmation dialog.** ✅ **Applied 2026-08-03** (`#m-cancel` with the `closing.md` §3.11 copy).
File: `wms2/closing/index.html` · State 1 target banner, `✕ Cancel Closing`.
The legend says cancelling "discards scan records", but the wireframe cancels immediately.
Fix: add the confirm dialog (copy to come from the spec) before returning to State 0.
Raised by: closing.B L-1.10 ("dialog NOT in wireframe — spec must define copy").

**[WF-8] closing — Start Closing with an empty/invalid count silently no-ops.** ✅ **Applied 2026-08-03** (red toasts, §3.1 copy; >9999 advisory stays [ADMIN]).
File: `wms2/closing/index.html` · `#startBtn0` / `#targetIn0`.
No error copy, no visual feedback — indistinguishable from a broken button.
Fix: add an inline/red-toast validation error for empty, 0, negative, and non-integer input.
Raised by: closing.B E-15/E-16, QA-S0-02.

**[WF-9] ready-to-outbound — picking list modal (M1) has no sample-set lines.**
File: `wms2/ready-to-outbound/index.html` · `#m-pick` `.picktbl`.
[G-13] requires internal picking artifacts to show WHICH sample and HOW MANY (PD-36).
Fix: **conditional on owner approval of PD-36 and on PD-51 (the sample-set definition source) being answered** — add sample rows to the picking table. Do not add until both land.
Raised by: ready-to-outbound.A Q3 / ready-to-outbound.B OQ-B5 + E-28.
**APPLIED 2026-08-03** — owner approved the pass; per PD-51 v1 single label, one amber-tinted `sample set ×1` row added to `#m-pick` (order 422165, no-location marker pill). **Spec debt settled 2026-08-03 (owner-approved batch):** `ready-to-outbound.md` QA-M1-01 (the `{skus}` ≠ row-count clause), QA-M1-03 (4 → 5 rows, sample row last and excluded from the location sort), QA-M1-04 (sample SKU `—`), QA-M1-05 (`sample set`, `×1` bold), QA-M1-06 (order column tail), QA-M1-07 (third `422165` row is the sample, not a product line), §3 sample-lines paragraph, `BR-21`, `[E-28]` and QA-E-20 (unblocked) all re-baselined. Playwright-asserted.

**[WF-NEW-D · tracking-missing] — `.xdel` double-click removes one row but decrements both counters twice.**
*(Page-scoped ID on purpose: the next free numeric ID was claimed concurrently by the closing, ready-to-outbound and order-management passes. This is the same defect the `tracking-missing.md` spec cites as `WF-NEW-D`, so the two references resolve to each other.)*
File: `wms2/tracking-missing/index.html` · lines 400–404, the `.xdel` click handler.
`document.querySelectorAll('.xdel').forEach(b=>b.addEventListener('click',e=>{e.stopPropagation(); b.closest('tr').remove(); poolDec();}))` — no guard, no debounce. After the first click the `<tr>` is detached but the button is still its descendant, so `b.closest('tr')` still resolves, `.remove()` silently no-ops, and `poolDec()` fires a second time: one row removed, `#poolCount` / `#poolCountBottom` decremented twice. Counters and rendered rows diverge.
Violates [G-9] (every confirming action must be double-click safe) and the count invariant the tracking-missing spec states as `[BR-33]` / `[BR-41]`.
Note the asymmetry that makes it easy to miss: the sibling handler `finishMatch()` **does** guard (`const row=document.getElementById('poolrow1'); if(row){…}`); `.xdel` does not.
Fix: mirror `finishMatch()`'s guard — resolve the row first and call `poolDec()` only when a row was actually attached and removed.
**APPLIED 2026-08-03 (owner-approved batch)** — the defect is gone twice over. `.xdel` no longer removes anything (WF-6 moved removal behind `#m-remove`), and the confirm handler carries the explicit guard `if(rmRow && rmRow.isConnected){ … rmRow.remove(); poolDec(); }`. Playwright-asserted by double-firing `#rmConfirm`: `#poolCount` goes 3→2 exactly once and `#poolCountBottom` agrees, so the count invariant `[BR-33]`/`[BR-41]` holds under a double click `[G-9]`.
Raised by: `_verify/m2-tracking-missing.md` F3 · `_verify/m1-tracking-missing.md` D-2. Filed in `tracking-missing.md` §2.4.10 / §2.5 as **WF-NEW-D**; current behavior asserted by QA-WFQ-07, correct behavior by QA-NEG-03 `[ADMIN]`.

**[WF-NEW-E · tracking-missing] — Comments-hub pane headers diverge from the corpus-canonical strings.**
*(Page-scoped ID, same reason as above; cited as `WF-NEW-E` in `tracking-missing.md`. Related: the closing pass filed the same class of divergence for its own page — a single `[G-7]` amendment publishing the six hub strings closes both.)*
File: `wms2/tracking-missing/index.html` · `#inbox1` `.paneheader`, lines 227 and 234.
Ships `Comments mentioning me` and `Saved comments`; four of the eight pages (order-detail, order-management, ready-to-outbound, stock-status) ship `Comments mentioning me · Click to open the order` and `Saved comments · Click to open the order`. [G-7] states the hub is identical on all eight screens but does not yet publish the pane strings as byte-exact contract, so six QA suites assert mutually incompatible strings.
This page's `Unstar to remove from the list` and `Mark all read` are **already canonical — do not change them.**
Fix: adopt the two majority header strings here, and publish the six hub strings in `_global-rules.md` [G-7] so the other divergent pages can be corrected against one source.
**APPLIED 2026-08-03 (owner-approved batch) — both halves.** The page half had already landed (headers now read `Comments mentioning me · Click to open the order` / `Saved comments · Click to open the order`; the unstar hint and `Mark all read` were untouched, as instructed). The corpus half landed in this batch: **`_global-rules.md` `[G-7]` v1.2 publishes HUB-1…HUB-7**, and all eight wireframes plus all eight QA suites were moved to it in one commit. Cross-page defect D7 is closed.
Raised by: `_verify/m3a-cross-page.md` D7. Filed in `tracking-missing.md` §2.5 as **WF-NEW-E**; `[WF]` assertions QA-CMT-03 / QA-CMT-05, `[ADMIN]` assertion QA-CMT-15.

**[RTO-WFX-9 · ready-to-outbound] — the progress label lags the run by one tick, so it shows the previous action's mode string.**
*(Page-scoped ID on purpose: `_verify/m2-ready-to-outbound.md` S-2 proposed "WF-15", but that numeric ID was claimed concurrently by the closing, tracking-missing and order-management passes. This spec already keys its page-local defects `[RTO-WFX-1]`…`[RTO-WFX-8]`, so this one continues that series and the two references resolve to each other.)*
File: `wms2/ready-to-outbound/index.html` · `.bulk-run` click handler (approx. lines 404–411).
The handler sets `fill.style.width='0%'` **synchronously** on click, but assigns `label.childNodes[0].textContent` only inside the 250 ms `setInterval` callback. For the opening ~250 ms of every run the label therefore still carries the *previous* action's copy — on a fresh load, the idle demo copy `Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion`. Measured on 2026-08-03: 7 of 38 in-flight samples of a Bulk Outbound run read the print mode string, and 6 of 38 samples of the following print run read `refreshes after completion`. [BR-8]/`[L-5]` make the mode string a contract ("this is how the operator learns, mid-run, whether their selection is about to disappear"), so a crossed-over mode string is wrong from the first frame, not just from the first tick.
Fix: write the label once immediately before `setInterval` starts, mirroring the existing synchronous `fill.style.width='0%'` line.
Raised by: `_verify/m2-ready-to-outbound.md` S-2 (adversarial QA execution, 2026-08-03). Until it lands, `ready-to-outbound.md` §8.0 carries a reading rule bounding every "during the run" assertion to the first tick onward.
**APPLIED 2026-08-03** — label now written synchronously (`0%` + correct mode string) before `setInterval` starts, mirroring the `fill.style.width='0%'` line.

---

## C. Dead code / leftovers (cleanup, no behavior change)

**[WF-10] tracking-missing — v1 CSS/JS leftovers from the 2026-07-23 simplification.**
File: `wms2/tracking-missing/index.html`.
Unused selectors and script blocks for features that were removed: `.trk` inline inputs, `.shelf`, `.wait` chips, `.slack-pill`, per-PIC group classes (`.picava`, `.picname`, `.cntchip`), `.logsec` (resolved log), the trk-input script block, and the "Resolved button" JS.
Risk if left: a developer reading the file re-implements per-PIC groups, the bulk bar, the Slack column, the resolved log, or the search bar — all deliberately removed.
Fix: delete. Both plans already exclude them from the spec.
Raised by: tracking-missing.A (non-legend note) / tracking-missing.B (§1 dead-artifact list).
**APPLIED 2026-08-03 (owner-approved batch)** — verified by grep: `.trk`, `.shelf`, `.wait`, `.slack-pill`, `.picava`, `.picname`, `.cntchip` and `.logsec` return **0 occurrences** in `wms2/tracking-missing/index.html`, as do the trk-input and Resolved-button script blocks.

**[WF-11] inbound-request — HTML comment for the removed "View Orders link info" modal.**
File: `wms2/inbound-request/index.html` · around line 701.
The modal was removed 2026-08-03; the commented block remains.
Fix: delete the comment block so coverage checks and future readers don't resurrect it.
Raised by: inbound-request.A (removed-modal entry).
**APPLIED 2026-08-03 (owner-approved batch)** — verified by grep: `View Orders link info` returns 0 occurrences in `wms2/inbound-request/index.html`. Playwright-asserted against the served page source.

**[WF-12] closing — wf-bar lists "Modal: Process Processing Order" twice.** ✅ **Applied 2026-08-03** (duplicate removed; a "Modal: Amend Closing" tab was added in the same pass, `.wf-tab` stays 10).
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
**APPLIED 2026-08-03** — legend #16 now reads `shows at most 20 rows on screen`, matching `[BR-37]` (exactly 20) and the panel footer.

**[WF-VO-1] view-orders — Comments-hub copy is the corpus-minority form on six strings.**
> Page-scoped ID on purpose: three concurrent remediation passes each claimed `WF-15` in this file, so this entry uses the page-scoped form (precedent: `[RTO-WFX-n]`). It is cited as `WF-VO-1` throughout `view-orders.md`.
File: `wms2/view-orders/index.html` · `.paneheader` in all nine `.inboxdd` blocks + the search-results header and empty state built in the inline script (`… results · newest first · click to open the order page` / `No matching Comments`).
[G-7] makes the hub one control replicated on all eight screens, so its copy is a byte-exact cross-page contract. This page ships: `Comments where I'm tagged · Click to open the order page` · `Comments I saved · Click to open the order page` · `Unstar to remove from list` · `Mark all as read` · `{n} results · newest first · click to open the order page` · `No matching Comments`. Five other specs use: `Comments mentioning me · Click to open the order` · `Saved comments · Click to open the order` · `Unstar to remove from the list` · `Mark all read` · `… click to open the order` · `No matching comments`. Every spec asserts its own form byte-exactly, so no single implementation can satisfy all eight QA suites.
Fix: **conditional and corpus-wide — do not edit this page alone.** `[G-7]` must first publish the six canonical strings; then all eight wireframes and all eight QA suites change in one pass. Editing only view-orders would break `view-orders.md`'s [WF] assertions (QA-C-03/05/06/07) without fixing the divergence.
**APPLIED 2026-08-03 (owner-approved batch)** — the precondition was met first: `[G-7]` v1.2 published HUB-1…HUB-7, then all eight wireframes and all eight QA suites moved in one commit. On this page all **nine** `.inboxdd` blocks were canonicalized, including `#inbox6` / `#inbox6b`, whose headers read `· Click to open the item`; `[G-7]` reading rule 2 fixes the word `order` for every entity type, so no seventh string survives. QA-C-03 / QA-C-05 / QA-C-06 / QA-C-07 / QA-C-10 / QA-C-11 re-baselined; QA-C-18 now has assertable literals; §9.5 CP-4 closed. **Scope note:** this page was also the sole outlier on the search placeholder, which the register's six-string list did not cover — it was canonicalized as HUB-7 (majority 4/5) rather than left as the last fork.
Raised by: M3a cross-page verification 2026-08-03 (D7) · `view-orders.md` §2.4 / §9.5 CP-4 / QA-C-18.

**[WF-14] stock-status — two modals have no legend dots.**
File: `wms2/stock-status/index.html` · `m-auditlog` (Past Audit Logs list — currently covered by legend 15) and `m-adjlog6` (06-30 ADJUST detail — a second instance of M2).
Not a coverage gap (both plans account for them), but a legend annotation would make the 1:1 map self-evident.
Fix (optional): annotate both in the legend, or leave and rely on the spec's §2 note.
Raised by: stock-status.A / stock-status.B (§1 inventory notes).
**APPLIED 2026-08-03** — both modals annotated with new dots **17** (`m-auditlog`) and **18** (`m-adjlog6`) plus matching legend entries; no existing number reused.

**[WF-15] closing — Comments hub copy diverges from the cross-page `[G-7]` contract.**
File: `wms2/closing/index.html` · `#inbox1` `.paneheader` in both panes.
The hub is one component on all eight screens, so its strings are a byte-exact contract. Closing renders "Comments where I'm tagged" / "Comments I saved" / "Unstar to remove from this list"; the four-page majority (order-detail · order-management · ready-to-outbound · stock-status) renders "Comments mentioning me · Click to open the order" / "Saved comments · Click to open the order" / "Unstar to remove from the list". Closing and inbound-request are the two outliers.
Fix: replace the two pane headers and the unstar hint with the canonical strings. "Mark all read" is already canonical and must not change. Inbound-request needs the identical edit.
Risk if left: the spec's `[ADMIN]` copy (closing.md §3.8) and the wireframe's `[WF]` copy stay permanently forked, and two QA suites assert strings that cannot both pass one implementation.
**APPLIED 2026-08-03 (owner-approved batch)** — `#inbox1`'s two pane headers and the unstar hint now read `[G-7]` HUB-1 / HUB-2 / HUB-3; `Mark all read` was already canonical and was not touched. `closing.md` §2 defect table, §3.8 (now quoting `[G-7]` instead of owning a local table), the §8.0 R2-normalization rows, QA-HUB-01, QA-HUB-02 and QA-HUB-09 were updated in the same commit, so the `[WF]` and `[ADMIN]` tiers no longer diverge on the four elements this wireframe builds. **Correction to this entry's own premise:** it claimed a "four-page majority" rendering `Unstar to remove from the list`. That was wrong — see the §F and §H corrections below; the true split was 3/2/2/1 with no majority, which is why `[G-7]` resolved the hint on standard-English grounds instead of by vote.
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
> **Outcome 2026-08-03.** The owner-approved batch keyed every item on the full token plus the named file, as instructed, and **renumbered nothing**. All three `WF-15`s and both `WF-16`s were dispatched to their correct files, which the Playwright run confirms page by page. The collision is therefore inert for the remainder of this register — every entry is APPLIED — but the warning stays because the ids are still cited by shipped specs and a future editor reading a bare `[WF-15]` would still be reading an ambiguous reference.
>
> **⚑ Factual correction for any hub-copy fix that names this page — RESOLVED 2026-08-03.** `[WF-15] closing` stated that the four-page majority (including order-management) renders `Unstar to remove from the list`. Verified against `wms2/order-management/index.html:187`, **this page rendered `Unstar to remove from list`** (no `the`) — which `order-management.md` §3.10 and QA-CMT-03 asserted byte-exactly, and which §3.10 declared a knowingly-kept divergence because the wireframe is SST for UI copy (`_review` §3.9) and the corpus had no majority on that string. This correction was right and its reasoning was honoured: nothing was edited toward a string no wireframe contained until `[G-7]` published one. **`[G-7]` v1.2 published HUB-1…HUB-7 on 2026-08-03** and this page moved to HUB-3 `Unstar to remove from the list` in the same commit as the other seven, with §3.10 and QA-CMT-03 re-baselined together. *(One number in this correction was itself off: the split is **3 / 2 / 2 / 1**, not 2 / 2 / 2 / 1 — `view-orders` also rendered `… from list` and was omitted from the tally. The conclusion is unchanged: no majority existed.)*

**[WF-15 · proposed] order-management — M1 preview collapse row under-spans the table by one cell.**
The collapse row `⋯ +8 more rows` uses `colspan="6"` while the preview `<thead>` has **7** `<th>` (`Recipient · Country · SKU · Product Name · Qty · Campaign · Carrier (auto)`).
Fix: `colspan="7"`.
Documented by QA-IMP-35; spec §3.2.4.
**APPLIED 2026-08-03** — `colspan="7"`.

**[WF-16 · proposed] order-management — M2 `Start Assignment (ON)` closes silently.**
The footer button carries `data-close` but has **no `id`** and **no toast handler**, so a confirming action produces no confirmation. Contradicts `[G-2]`, which `_review.md` C-6 rules wins over wireframe omissions.
Fix: add an `id` and the green toast defined in the spec's §3.6.5.
Documented by QA-SMP-30; behaviour asserted by QA-SMP-06.
**APPLIED 2026-08-03** — button id `sampStartBtn`; green toast per §3.6.5 byte-exact copy (`✓ Sample assignment started` + target-dependent subtext), node `#gtoast3`.

**[WF-17 · proposed] order-management — M3 `Cancel Selected Periods` fires at zero selection and has no confirm step.**
`#sampCancelBtn` toasts unconditionally, including when no checkbox is checked, and no confirm dialog precedes a cancellation that can switch off a company-wide `forever` campaign.
Fix: disable at zero selection, and add the confirm dialog defined in the spec's §3.7.5 (`[PD-5 · OWNER-PENDING]`).
Documented by QA-SMP-31; behaviour asserted by QA-SMP-20 / QA-SMP-21.
**APPLIED 2026-08-03** — disabled at zero selection; confirm dialog `#m-sampcancel-confirm` per §3.7.5 byte-exact copy (`Cancel {n} assignment period(s)?` / `Keep periods` / `Cancel periods`); the green toast now fires only after confirmation.

**[WF-18 · proposed] order-management — two independent toast nodes can overlap.**
`#mktConfirm` creates `#gtoast` and `#sampCancelBtn` creates `#gtoast2`, both fixed at `top:16px; right:16px`, so two toasts can occupy the same coordinates simultaneously.
Fix: one toast slot (replace) or an explicit stack.
Documented by QA-GBL-09; spec `[L-F5]`, [E-62].
**APPLIED 2026-08-03** — explicit-stack option: per-action nodes (`#gtoast`/`#gtoast2`/`#gtoast3`) kept for QA identity, shared `stackToasts()` repositions visible toasts so they never overlap.

**[WF-19 · proposed] order-management — M2 `forever` leaves the end fields enabled.**
The `forever (no end date)` checkbox ships **checked** while `End date` and `Time` remain enabled and editable, contradicting the specified mechanic (`forever` wins; end fields cleared and disabled).
Fix: clear **and** disable the end fields while `forever` is checked.
Documented by QA-SMP-33; spec §3.6.3, [E-23].
**APPLIED 2026-08-03** — end fields (`#sampEndDate`/`#sampEndTime`) cleared and disabled while `#sampForever` is checked, synced on load and on change.

**[WF-20 · proposed] order-management — no modal responds to `Esc`.**
There is no `keydown` listener anywhere in the file, yet `Esc` is a specified dismissal path.
Fix: add `Esc` dismissal to all three overlays.
Documented by QA-GBL-10; spec §3.2.6, [E-97].
**APPLIED 2026-08-03** — `keydown` handler: Esc closes the topmost open overlay (all four, including the new WF-17 confirm), else the Comments hub.

**[WF-21 · proposed] order-management — the Comments hub does not close on an outside click, and carries dead guards for the behaviour.**
`onclick="event.stopPropagation()"` on `.csearch` and `e.stopPropagation()` on the hub button, the tab buttons and the stars were written to protect a `document`-level close handler that was never added. The guards are dead code and the hub can only be closed by clicking its own trigger again.
Fix: add the outside-click close (and `Esc`, with WF-20).
Documented by QA-CMT-20; spec §3.10, [E-97].
**APPLIED 2026-08-03** — document-level outside-click close added (guarded by `closest('.inboxdd')`, so the formerly dead `stopPropagation` guards are now live); Esc covered with WF-20.

---

## G. Appended 2026-08-03 — found while remediating `specs/inbound-request.md`

> Page-scoped ID deliberately, not a `WF-n`: this remediation round produced three independent `[WF-15]` entries on three different files (see section F's collision warning), so a new number would compound the problem. `inbound-request.md` cites this entry by the full token `[IR-WFX-1 · proposed]`, which cannot collide. Same deploy rule as the rest of this file — do not apply now; ship through `/wf-deploy inbound-request`.

**[IR-WFX-1 · proposed] inbound-request — Comments-hub pane strings diverge from the rest of the corpus.**
File: `wms2/inbound-request/index.html` · `#inbox1` `.paneheader` in both panes (lines 244 and 249).
This page renders `Comments where I'm tagged` / `Mark all as read` / `Comments I saved` / `Unstar to remove from list`. Across the eight screens the same four strings have 3, 2, 4 and 4 variants respectively, so only two of them have a majority at all: the mentions header (`Comments mentioning me · Click to open the order`, 4 pages) and the read-all action (`Mark all read`, 6 pages — this page and view-orders are the two that say `Mark all as read`). The saved header and the unstar hint have **no** majority (`Unstar to remove` 1 · `… from the list` 2 · `… from this list` 2 · `… from list` 2, this page and order-management).
Risk if left: the hub is one component on all eight screens and every spec asserts its strings byte-exactly in QA, so the eight QA suites cannot all pass against a single implementation.
Fix: **conditional on `_global-rules` `[G-7]` publishing the six shared hub strings as byte-exact contract.** Do not edit before that — for two of the four strings there is no majority to converge on, and editing toward a string no wireframe contains would just move the fork. Once `[G-7]` publishes, apply the canonical strings here, re-baseline `inbound-request.md` QA-F-02 / QA-F-03, and retire QA-F-11 (the `[ADMIN]` half that currently carries the "follow `[G-7]`" contract).
Related, same root cause, do not fix independently: `[WF-15] closing`, `[WF-16] tracking-missing`, and section F's factual correction for `order-management`.
**APPLIED 2026-08-03 (owner-approved batch)** — the stated precondition was met first: `[G-7]` v1.2 published HUB-1…HUB-7, then every related entry was fixed in the **same commit** (`[WF-VO-1]`, `[WF-15] closing`, `[WF-NEW-E]`, this entry, and the §F / §H factual corrections). This page's `#inbox1` now renders HUB-1…HUB-4; `inbound-request.md` §2.4 obs. 3, §3.1.13, `DC-13`, QA-F-02 and QA-F-03 were re-baselined and QA-F-11 became runnable rather than deferred. **Correction to this entry's own tally:** it counted the unstar hint as `Unstar to remove` 1 / `… from the list` 2 / `… from this list` 2 / `… from list` 2 — seven pages, omitting `view-orders`, which also renders `… from list`. The corrected split is 3/2/2/1; still no majority, so the conclusion (do not converge on a string no wireframe contains) held, and `[G-7]` resolved it on standard-English grounds.
Raised by: M3a cross-page verification D7 (2026-08-03) · specced position in `inbound-request.md` §2.4 obs. 3 / §3.1.13 / §9.1 / QA-F-11.

---

## H. Appended 2026-08-03 — found while remediating `specs/stock-status.md`

> Page-scoped IDs deliberately, not `WF-n`: by the time this pass ran, `WF-15` had been claimed independently by the ready-to-outbound, closing and order-management passes and `WF-16` by closing/tracking-missing and order-management (see section F's collision warning). `stock-status.md` cites these two by the full tokens `[INV-WFX-1 · proposed]` / `[INV-WFX-2 · proposed]`, which cannot collide. Same deploy rule as the rest of this file — do not apply now; ship through `/wf-deploy stock-status`. File for both: `wms2/stock-status/index.html`.
>
> **⚑ Factual correction for any hub-copy fix that names this page — RESOLVED 2026-08-03.** `[WF-15] closing` listed stock-status inside the "four-page majority" said to render `Unstar to remove from the list`. Verified against `wms2/stock-status/index.html` (`#inbox1`, saved pane `.paneheader`), **this page rendered `Unstar to remove from this list`** (with `the` → `this`), which `stock-status.md` §3.12 stated and its `[WF]` tier asserted. On the unstar hint the corpus had no majority; stock-status sat in the `… from this list` pair with closing, not in the `… from the list` pair. The other hub strings on this page already matched the majority. The prescribed order was followed exactly: **`[G-7]` v1.2 published HUB-1…HUB-7 first**, then all eight pages were edited in one commit, so this page's hint became HUB-3 `Unstar to remove from the list` alongside §3.12 and its QA. *(Tally correction: the split is **3 / 2 / 2 / 1**, not 1 / 2 / 2 / 2 — `view-orders` was missing from the count. No majority either way, which is why HUB-3 was resolved on standard-English grounds rather than by vote.)*

**[INV-WFX-1 · proposed] stock-status — M1 total note hard-codes "the 3 new additions" against a single `[NEW]` row.**
File: `wms2/stock-status/index.html` · `#m-adjust` `.note` (approx. line 521).
The note reads `Total stock loss: +₩46,260 (target 0) · the 3 new additions are not losses — on confirm, Current Stocks · Available update immediately; monthly audit logs retained.` The same modal renders exactly **one** `[NEW]` row (SKU `100048201`, `0 → 3`), and `#m-auditlog` records `New Additions 1` for the 2026-07-22 session. The fixture states the count in three places and `3` is the odd one out — it is the added *quantity*, not the number of additions.
Risk if left: the sentence is a byte-exact `[WF]` QA contract, so a developer either hard-codes `3` or infers the wrong formula (adjustments + additions). `stock-status.md` §3.13 specifies the templatised form `the {n} new addition(s) are not losses`.
Fix: change `the 3 new additions are not losses` → `the 1 new addition is not a loss`, and update `stock-status.md` `QA-AUD-23`'s expected string in the same commit (`QA-AUD-44` already carries the `[ADMIN]`-tier contract and needs no change).
Raised by: adversarial QA execution of `stock-status.md` §8 (2026-08-03, item 5) · specced position in `stock-status.md` §3.13, QA-AUD-23, QA-AUD-44.
**APPLIED 2026-08-03** — wireframe note now reads `the 1 new addition is not a loss`. **Spec debt settled:** `stock-status.md` `QA-AUD-23` already carries the corrected byte-exact string (verified 2026-08-03) and `QA-AUD-44` keeps the templatised `[ADMIN]` contract. Playwright-asserted, including the negative on the stale `the 3 new additions are not losses`. *Residual, not a defect but worth naming:* `QA-AUD-23` (`[WF]`) asserts the singular-agreement copy the drawing renders while `QA-AUD-44` (`[ADMIN]`) asserts the templatised `the {n} new addition(s) are not losses`, so at n = 1 the two tiers read differently by design. Whether production should render true singular agreement is a copy decision for the spec author, not a wireframe fix.

**[INV-WFX-2 · proposed] stock-status — Inbound Form note points at the retired control "Request Inbound".**
File: `wms2/stock-status/index.html` · `#p-inbound` `.form-note`.
Final sentence reads `For order-linked inbound, use Request Inbound on View Orders / the order detail.` **`Request Inbound` is a retired control name** — `order-detail.md` `BR-4` states it "is retired and must not reappear", `BR-40` lists it among removed features, and that page's QA asserts the string appears nowhere. Neither named screen has such a control: View Orders uses row `Inbound` / `Inbound + Outbound` / `Bulk Inbound (Selected)`; Order Detail uses per-row `Inbound` + `Bulk Inbound Selected Items`.
Risk if left: the note is a byte-exact `[WF]` QA contract, so the retired name propagates into the build and the note sends an operator to a button that does not exist — the exact failure `BR-4` was written to prevent.
Fix: replace the final sentence with `For order-linked inbound, use the row Inbound buttons on View Orders or Order Detail.`, and update `stock-status.md` `QA-FRM-03` in the same commit (`QA-FRM-20` already carries the `[ADMIN]`-tier corrected copy and the negative assertion, and needs no change).
Raised by: M3a cross-page verification D9 (2026-08-03) · specced position in `stock-status.md` §3.18, QA-FRM-03, QA-FRM-20.
**APPLIED 2026-08-03** — final sentence replaced with the corrected copy exactly as specified. **Spec debt settled:** `stock-status.md` `QA-FRM-03` already asserts the corrected string and `QA-FRM-20` keeps the `[ADMIN]` negative (verified 2026-08-03). Playwright-asserted, including the negative that `Request Inbound` appears nowhere in the note.

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
**APPLIED 2026-08-03** — document-level outside-click handler closes `#statusdd`/`#statusddH` with no status change (mirrors the modal backdrop pattern; trigger toggle intact). **Spec debt settled 2026-08-03 (owner-approved batch):** `QA-STA-4` is `[WF]` again, the §8.1 split reads 69 `[WF]` / 92 `[ADMIN]`, and the two places that still described the fix as pending — the §8.3 step-4 run list (which excluded QA-STA-4 from the `[WF]` run) and the §9.5 `[OD-WFX-1]` entry — were corrected. Playwright-asserted: `#statusdd` visible before an outside click, hidden after.
