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

**[WF-14] stock-status — two modals have no legend dots.**
File: `wms2/stock-status/index.html` · `m-auditlog` (Past Audit Logs list — currently covered by legend 15) and `m-adjlog6` (06-30 ADJUST detail — a second instance of M2).
Not a coverage gap (both plans account for them), but a legend annotation would make the 1:1 map self-evident.
Fix (optional): annotate both in the legend, or leave and rely on the spec's §2 note.
Raised by: stock-status.A / stock-status.B (§1 inventory notes).

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
