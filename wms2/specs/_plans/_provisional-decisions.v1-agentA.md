# Provisional Decisions Register — WMS 2.0 Specs

> **ALL PROVISIONAL — owner review pending 2026-08-03.**
> Every decision below was made by the spec team so P3-3 could write unambiguous specs while the owner was unavailable. None is owner-approved. Each is written into the specs as normal behavior tagged `[PD-n · OWNER-PENDING]`; reversing one means editing the tagged sentences on the listed pages and nothing else.
> Entries marked **NO-DEFAULT** were NOT decided — they appear in the specs' §9 Open Questions only, with no behavior specified.

Source: all 16 P3-1 plans (OWNER open questions, deduplicated). Supervisor rulings in `_supervisor-state.md` are applied as-is (PD-9 carrier, PD-10/PD-11-class "proposal" items adopted provisionally). Format: **question · provisional decision · rationale · affected pages**.

Page codes: VO=view-orders · OD=order-detail · RTO=ready-to-outbound · INV=stock-status · OM=order-management · TM=tracking-missing · CL=closing · IR=inbound-request.

---

## A. Cross-cutting (raised independently by 3+ pages)

**[PD-1] Role/permission model — who may perform destructive or high-trust actions?**
Provisional: **v1 ships a single admin role. No role gating on any screen; every mutating action records the actor [G-8]. A role matrix is a post-v1 owner decision.**
Rationale: no role model exists in any input document, and inventing per-page gates would create eight inconsistent models.
Pages: all 8 (RTO OQ-B6 · INV Q8 · CL OQ-O3 · TM Q6 · IR O-5/OQ-3 · OM Q-D5).

**[PD-2] Does the [G-3a] send sound apply beyond View Orders / RTO?**
Provisional: **Yes — every outbound-class button on every page plays it** (VO outbound family, RTO Bulk Outbound, OD Outbound, INV "− Record Outbound").
Rationale: G-3(a) is written by button class, not by page; the mandatory-item list names examples, not scope.
Pages: VO, RTO, OD, INV (OD OQ-2/Q-A6 · INV 3b-7).

**[PD-3] Can comments be edited or deleted?**
Provisional: **No — append-only, permanent. Corrections are posted as new comments.**
Rationale: [G-7] declares comments an AI-training asset; mutability would silently rewrite the corpus.
Pages: all 8 (OD OQ-5).

**[PD-4] What happens when a Slack notification fails?**
Provisional: **The primary action always commits. Delivery failure is persisted and retried; it never blocks the UI and never rolls anything back.**
Rationale: notification is a side effect, not part of the transaction (all four raising plans reached the same shape).
Pages: all 8 (VO E-40 · OD E-29 · TM E-26 · RTO E-16).

**[PD-5] Do removals/deletions need a confirmation and a toast?**
Provisional: **Yes — every destructive action gets a confirm step, a reason where a reason enum already exists in the flow, and a [G-2] toast.**
Rationale: [G-2] (owner emphasis 2026-08-03) says EVERY confirming action toasts; wireframe omissions are gaps, not decisions.
Pages: TM (✕), CL (Cancel Closing, delete row), OD (M3), INV (M4).

**[PD-6] Stale entity at confirm time (candidate left Processing, order outbounded elsewhere, reservation already released).**
Provisional: **Server revalidates at confirm; on mismatch it rejects with a red toast and refreshes the affected view. No partial writes.**
Rationale: identical shape independently proposed by 5 plans.
Pages: VO, OD, RTO, INV, TM, CL.

**[PD-7] Two operators edit the same entity concurrently.**
Provisional: **Optimistic version check → 409 → reload the row + non-green toast. Counting flows (State 6 receive, closing scans) merge server-side instead.**
Rationale: last-write-wins would silently destroy field data; merge is correct only where the value is a running total.
Pages: all 8 (OD Q-B2 · INV E-7 · CL E-32 · IR E-39).

**[PD-8] Tracking-number uniqueness across the system.**
Provisional: **An inbound tracking number is unique system-wide; registering one that already exists on another inbound request is blocked. Inbound (supplier→warehouse) and outbound (warehouse→customer) tracking numbers are separate namespaces and may coincide; View Orders resolution precedence puts inbound-request tracking first (State 6).**
Rationale: View Orders matching integrity depends on a single owner per number; the two namespaces never resolve to the same screen.
Pages: IR (O-3/OQ-4), VO (E-22 class), TM.

---

## B. view-orders

**[PD-9] Carrier auto-record contradiction (S6b banner vs S6 footer).**
Provisional: **Automatic Carrier recording is NOT supported** (2026-08-03 legend wins). Received Date is auto-recorded at scan time; no Carrier field, no Carrier column.
Rationale: supervisor ruling; the dated 08-03 note supersedes older banner copy → wireframe fix WF-1/WF-2.
Pages: VO, IR.

**[PD-10] "Cancel Inbound disabled after Outbound — Cancel Outbound first" is still marked *proposal* (2026-07-09).**
Provisional: **Adopted as a rule.** Individual Cancel Inbound is disabled once the order is outbounded; Cancel Outbound must run first.
Rationale: supervisor ruling (proposal items = provisionally adopted); it is the only ordering that keeps inventory arithmetic reversible.
Pages: VO (S3-4/Q1/OQ-8), OD (Q-A8/E-10) → WF-3.

**[PD-11] Rescanning an already-INBOUNDED product barcode in a customer order.**
Provisional: **Amber warning toast "Already inbounded — {SKU}", no second inbound, no send sound.**
Rationale: silent no-op would read as a failed scan; an error state would break the scan loop.
Pages: VO (OQ-1/E-14).

**[PD-12] State 6 over-scan: cap at expected, or warn and count?**
Provisional: **Warn and count.** Received may exceed Expected; the excess blocks Confirm Full Inbound until resolved via Edit Expected Qty (M6) or Save Partial (M5).
Rationale: capping would make the exact-match gate trivially satisfiable and hide real over-deliveries.
Pages: VO (OQ-7/E-15).

**[PD-13] Is a Location required for every SKU before Confirm Full Inbound?**
Provisional: **Yes — required for every SKU (existing auto-suggested, new manual). Confirm is disabled while any received SKU lacks a location.**
Rationale: [G-14] one-location-per-SKU means stock cannot enter Inventory location-less.
Pages: VO (OQ-2/E-46), INV.

**[PD-14] M6 sets new Expected Qty below the already-received qty.**
Provisional: **Hard block with inline validation** ("New expected qty cannot be lower than the received qty ({n})").
Rationale: allowing it would create a permanent over-receipt that no screen can clear.
Pages: VO (OQ-3/E-24), IR.

**[PD-15] Rescanning the tracking of a fully INBOUNDED request.**
Provisional: **Opens the read-only State 6b completion view + an info toast** ("Already inbounded — Inbound No. {n}").
Rationale: the operator's question is "did this arrive?", which a read-only view answers; an error toast does not.
Pages: VO (OQ-5/E-17).

**[PD-16] Does an on-the-spot M2 match in View Orders also fire the "match confirmed" auto-comment + Slack?**
Provisional: **Yes, same auto-comment and route; the @mention is suppressed when resolver == registrant (no self-notification).**
Rationale: one match pipeline, one audit trail, regardless of which screen resolved it.
Pages: VO (Q3), TM, OD.

**[PD-17] Returned items NOT restocked (M3 qty 0) — is explicit persistence with disposition required?**
Provisional: **The qty-0 lines are persisted explicitly inside the restock record (SKU, ordered qty, restock qty 0). No disposition field is added in v1.**
Rationale: satisfies [G-8] without inventing UI the wireframe does not have.
Pages: VO (Q4/DC-22).

**[PD-18] Shelf value lifecycle — does it persist after outbound?**
Provisional: **Shelf persists while the order is open and auto-clears on Outbound** (old→new captured).
Rationale: temporary shelves must be reusable; a stale shelf on a shipped order misdirects the next picker.
Pages: VO (Q5/S1-2).

**[PD-19] Single-item auto-print fails (print agent offline).**
Provisional: **The inbound still commits; a red toast names the printer/agent; printing is never a gate.**
Rationale: blocking goods receipt on a printer is an operational stop-the-line risk.
Pages: VO (OQ-6/E-39), RTO, OD.

---

## C. order-detail

**[PD-20] Is a Hold reason required and persisted?**
Provisional: **Optional free-text reason captured when the status changes to on-hold, persisted with the event and rendered in the banner** (banner already shows reason-shaped copy).
Rationale: the banner text implies a reason exists; making it mandatory would block urgent CS.
Pages: OD (OQ-1), VO (S5-1 display).

**[PD-21] Does full inbound on Order Detail auto-trigger Outbound (as View Orders bulk does)?**
Provisional: **No. Outbound on Order Detail is always a manual click.** Auto-outbound is a View Orders scan/bulk-flow behavior only.
Rationale: Order Detail is a desk screen used for exception handling; silent shipping from an inspection screen is the wrong default.
Pages: OD (Q-A2), VO.

**[PD-22] ✕ Cancel Order on an order with INBOUNDED lines.**
Provisional: **Blocked** with an explicit message ("Cancel Inbound (restock) on {n} line(s) first").
Rationale: consistent with PD-10's ordering-guard doctrine; auto-restock would move stock without an operator decision on damage/loss.
Pages: OD (OQ-3/Q-A3/E-47), INV (JIT residual origin).

**[PD-23] Deleting an INBOUNDED line (M3).**
Provisional: **Blocked** — Cancel Inbound first. Deletion is allowed only on PENDING lines.
Rationale: same as PD-22; a deleted line cannot carry a restock decision.
Pages: OD (Q-A3/E-22).

**[PD-24] Deleting the only remaining line.**
Provisional: **Allowed** — a 0-line order is permitted; the Outbound gate additionally requires ≥1 INBOUNDED line, so it cannot ship.
Rationale: blocking would strand orders created in error.
Pages: OD (E-23).

**[PD-25] + Add Line Item on an outbounded/completed order.**
Provisional: **Blocked** after outbound.
Rationale: post-shipment line changes desynchronize the shipped contents from the record.
Pages: OD (E-25).

**[PD-26] Is there a Cancel Outbound on Order Detail?**
Provisional: **Yes — present, with the same rollback as View Orders (prepare shipment → processing).**
Rationale: parity; otherwise a correction started on Order Detail has to be finished on another screen.
Pages: OD (OQ-4), VO (S3-2).

**[PD-27] Should Order Detail line items show sample-set assignment?**
Provisional: **Yes — internal view [G-13]: the assigned sample and quantity are shown on the line-items area** (carrier-facing "(+ sample set)" appending stays a label/export concern).
Rationale: Order Detail is an internal screen; hiding the sample makes disputes unresolvable.
Pages: OD (Q-A7), OM, RTO.

**[PD-28] Change Status: transition matrix and confirm on destructive values.**
Provisional: **All 8 statuses selectable from any state; refunded / failed / completed require a confirm dialog; every other pick applies instantly with a toast.**
Rationale: mirrors live admin freedom while protecting the three values that have financial effects.
Pages: OD (Q-A1/L-8).

**[PD-29] Which statuses block Outbound besides on-hold?**
Provisional: **Outbound is allowed only from `processing` or `pending` with every line INBOUNDED. Blocked from on-hold, refunded, failed, completed, shipped, prepare-shipment.**
Rationale: makes the gate a pure function of status + inbound completeness.
Pages: OD (Q-A12/E-16), VO.

**[PD-30] Reset Order scope.**
Provisional: **Clears fulfillment/shipment state only (tracking, label, shipment record) — never line-item inbound/outbound state. Requires confirm; old/new snapshot captured. Allowed at any time.**
Rationale: mirrors live semantics without letting a "reset" silently reverse inventory movements.
Pages: OD (OQ-4/Q-A4/E-48).

**[PD-31] ⧉ Clone Order — what is copied?**
Provisional: **Line items (SKU/qty) + billing/shipping addresses. NOT copied: comments, actor log, tracking numbers, agent-tracking fields (Order Number/Date/Cost/CP Link), PIC, status.**
Rationale: a clone is a new purchase, not a duplicated history.
Pages: OD (Q-A9/E-50).

**[PD-32] ✎ Change Tracking # — duplicate check and label side effect.**
Provisional: **Warn on a duplicate across orders and allow with confirm; the label is NOT auto-regenerated or invalidated.**
Rationale: legitimate duplicates exist (combined boxes); silent label regeneration would print without operator intent [G-4].
Pages: OD (Q-A10/E-49).

**[PD-33] PIC edit — free text or user picker, and is the new PIC notified?**
Provisional: **System-user picker; no automatic Slack notification** (use an @mention comment to notify).
Rationale: PIC feeds filters and mention routing, so it must resolve to a real user; auto-notifying every reassignment would be noise.
Pages: OD (Q-A11/L-5), OM (custom-PIC exception, PD-51 area).

---

## D. ready-to-outbound

**[PD-34] "No failure case" (2026-07-22) vs real per-order failures mid-batch.**
Provisional: **The batch-completion UI stays all-success as designed. Infrastructure failures (print agent offline, stale/invalid order) raise a separate red toast, the affected orders remain in the list, and per-order results are always persisted (DC-16).**
Rationale: keeps the 07-22 decision intact while refusing to report success for work that did not happen.
Pages: RTO (Q2/OQ-B1).

**[PD-35] Bulk Outbound eligibility for orders with non-inbounded lines (MKT "Not inbounded", partial orders) and for JIT "Fully Inbounded" rows.**
Provisional: **Orders with any non-INBOUNDED line are auto-excluded from the batch and reported in the toast subtext ("{n} excluded — items not inbounded"). Fully-inbounded JIT rows ARE eligible for Bulk Outbound.**
Rationale: partial outbound would ship incomplete orders; JIT rows are complete and only awaiting the click.
Pages: RTO (Q1/Q4/OQ-B2/E-21).

**[PD-36] Should the picking list (M1 / printed) include sample-set lines?**
Provisional: **Yes — internal picking artifacts list WHICH sample and HOW MANY per [G-13].**
Rationale: G-13 explicitly assigns sample detail to the internal picking artifact; otherwise the picker cannot pick it → conditional wireframe fix WF-9.
Pages: RTO (Q3/OQ-B5), OM.

**[PD-37] Do Total Items and the bulk-button item counts include non-inbounded units?**
Provisional: **All units of the order** (MKT-40233 showing Total 3 with one item not inbounded is the precedent).
Rationale: the count is an order-size indicator for the desk operator, not a pick count.
Pages: RTO (OQ-B3/L-13).

**[PD-38] "Select all" scope vs view tabs.**
Provisional: **Select-all applies to the currently visible (filtered) rows only; per-order selection persists across tab switches.**
Rationale: selecting invisible rows is the classic bulk-action accident.
Pages: RTO (OQ-B4/E-2).

**[PD-39] Is there a sequence gate between the 3 bulk actions?**
Provisional: **No — the three actions are fully independent** (only one may run at a time, which is a lockout, not a sequence).
Rationale: reprints and re-picks are normal; forcing an order would block recovery paths.
Pages: RTO (Q5).

---

## E. stock-status (Inventory)

**[PD-40] Counted Qty prefill in audit mode (prefilled system qty vs blank).**
Provisional: **Keep the prefill** (wireframe is SST). The confirmation-bias risk is recorded in §9 for the owner.
Rationale: the wireframe encodes a speed decision; reversing it silently would change audit behavior without an owner call.
Pages: INV (OQ-1/Q2).

**[PD-41] Who confirms a PENDING inbound event?**
Provisional: **Inventory is display-only for PENDING. Confirmation happens only through View Orders State 6 / the Inbound Request lifecycle. No confirm affordance is added here.**
Rationale: two confirm paths for one fact is exactly the double-entry failure the design avoids.
Pages: INV (OQ-2/E-39), VO, IR.

**[PD-42] Add "Barcode" as a Stock History search key?**
Provisional: **Yes — Barcode becomes a 5th search key (SKU / Product Name / Order ID / Tracking No / Barcode).**
Rationale: an operator holding a product must be able to look it up; every other key requires typing from memory.
Pages: INV (OQ-3/L-F1).

**[PD-43] Is Loss (₩) / product cost visible to all warehouse staff in audit mode?**
Provisional: **Visible to whoever runs the audit** (wireframe behavior); no admin-only split in v1 (ties to PD-1).
Rationale: the loss total is the audit's own KPI; hiding it would make the audit screen unusable to the auditor.
Pages: INV (OQ-4).

**[PD-44] Audit session concurrency.**
Provisional: **Exactly one active audit session per warehouse, with a single auditor of record. A second Start is blocked with a message naming the active session.**
Rationale: the wireframe's session schema (one auditor, one loss total) has no merge semantics.
Pages: INV (OQ-5/Q4/E-23).

**[PD-45] Cancel Inbound (release reservation) on an ACTIVE (processing) order.**
Provisional: **Allowed, with an extra confirmation naming the live order** ("Order {id} is still processing — release anyway?").
Rationale: the wireframe deliberately shows the button on processing rows; blocking it would strand genuine over-reservations.
Pages: INV (Q1/E-29).

**[PD-46] Location exclusivity — may two SKUs share one location?**
Provisional: **No — one location per SKU AND one SKU per location (1:1). Assigning an occupied location is blocked with an error naming the occupying SKU.**
Rationale: the audit walking order and the "By Location" card both assume a 1:1 mapping → global rule delta GD-7.
Pages: INV (Q7/E-6), VO (S6-7), RTO (pick locations).

**[PD-47] May an audit be confirmed while filters restrict the list, and what does "SKUs Checked" mean?**
Provisional: **Yes — partial/filtered audits are allowed. The session records its scope (the filtered set at session start), and "SKUs Checked" = rows in that scope.**
Rationale: full-catalog-only audits are impractical; recording the scope keeps the number honest.
Pages: INV (Q3/E-11).

**[PD-48] What unlocks Confirm after the Reserved-shortage gate fires?**
Provisional: **An explicit acknowledgement checkbox in M1 ("Reviewed with the order team"), persisted with the session.**
Rationale: forcing every shortage to be resolved before confirm would stall the audit at the shelf; a recorded acknowledgement keeps accountability.
Pages: INV (Q5/E-14).

**[PD-49] M4 Restock Qty edited BELOW the released qty.**
Provisional: **Allowed — the remainder is auto-recorded as ADJUST(−remainder) carrying the same memo.**
Rationale: partial damage is the exact use case; blocking it would force a second manual adjustment.
Pages: INV (Q6/E-31).

**[PD-50] M4 Restock Qty edited ABOVE the reserved/inbounded qty.**
Provisional: **Blocked** (validation cap at the originally inbounded qty).
Rationale: restocking more than was taken creates phantom stock.
Pages: INV (E-30).

---

## F. order-management

**[PD-51] Where is "WHICH sample and HOW MANY" configured, and by whom? — NO-DEFAULT**
The Sample Assignment ON flow deliberately has no sample-type selection, but [G-13] requires the internal invoice and picking label to show the sample kind and quantity. No input document names the source of that definition. **Not decided — specs state the dual-view output requirement and list the definition source as an open question.**
Pages: OM (OQ-1), RTO, OD.

**[PD-52] Sample ON with a backdated start datetime — retroactive?**
Provisional: **Not retroactive. Only orders created after the ON action (and inside the window) receive a set.**
Rationale: retroactive assignment would change orders already picked or shipped.
Pages: OM (OQ-2/Q-O1/E-25).

**[PD-53] What does the period govern for target = "Selected orders only"?**
Provisional: **Immediate assignment to the selected orders; the period is informational/audit metadata only.**
Rationale: the orders already exist, so a window has nothing left to gate.
Pages: OM (OQ-3/E-33).

**[PD-54] Is there a revert path for a confirmed import made from the wrong file?**
Provisional: **No batch revert in v1. Cleanup is per order via ✕ Cancel Order on Order Detail.**
Rationale: a batch revert on orders that may already be picked is a larger feature than the wireframe encodes.
Pages: OM (OQ-4), OD.

**[PD-55] "Not connected — contact the Fulfillment Center" orders: what unblocks them, and who owns it? — NO-DEFAULT**
The order is created and appears in RTO, but no screen offers a manual carrier assignment and no Slack route exists for the follow-up. Deciding this would invent both a UI affordance and an owner. **Not decided — specs state the flagged state and its persistence, and list the unblocking path as an open question.**
Pages: OM (OQ-5/Q-O6), RTO.

**[PD-56] Does an active sample period also match MKT- marketing orders?**
Provisional: **No — sales orders only.**
Rationale: seeding/giveaway orders carry their own campaign contents; adding a sample set would distort settlement separation.
Pages: OM (Q-O2/E-35).

**[PD-57] Import file with some invalid rows — block the file, or import the valid rows?**
Provisional: **Block the whole file.** Preview shows "· {n} errors" and Confirm stays disabled until a clean re-upload.
Rationale: partial imports leave marketing unable to tell which rows landed; the file is the unit of intent.
Pages: OM (Q-O3/E-19).

**[PD-58] Duplicate-batch protection beyond double-click (same file re-uploaded).**
Provisional: **Warn on a matching file hash with an explicit "Import anyway" confirm; do not hard-block.**
Rationale: re-importing a corrected file with the same name is common; a hard block would strand it.
Pages: OM (Q-O4/E-10).

**[PD-59] May Merge Orders combine an MKT- order with a regular sales order?**
Provisional: **Blocked.**
Rationale: the purple/MKT split exists for settlement and volume separation; merging destroys it.
Pages: OM (Q-O5/E-37).

---

## G. tracking-missing (Unrecognized Tracking)

**[PD-60] ✕ removal has no confirm, no reason, no toast.**
Provisional: **Add all three: a confirm dialog, a mandatory reason enum (mis-registration / routed to inbound request / no action needed), and a [G-2] toast.** Removal stays a soft delete with the full row snapshot persisted.
Rationale: [G-2] + [G-8] + the [G-11] reason precedent; the button sits next to the primary action at speed → wireframe gap WF-6.
Pages: TM (Q1/E-16).

**[PD-61] Pool aging — any escalation for items sitting unresolved?**
Provisional: **A once-daily re-notification into #unrecognized-tracking listing pool items open >24h** (same shape as the morning no-tracking check).
Rationale: the 07-23 simplification removed the wait chips, leaving no age signal anywhere; a daily digest restores it without re-adding UI.
Pages: TM (Q2).

**[PD-62] What does the UI tell the operator when Suspected Orders is empty?**
Provisional: **An explicit empty state: "No Processing order contains this product — check the order data upstream, or remove with a reason." No search affordance is re-introduced.**
Rationale: BR-4 says an empty candidate list means the data is wrong; the UI should say exactly that.
Pages: TM (Q3/E-5).

**[PD-63] Photo column — permanently removed or deferred?**
Provisional: **Permanently removed.** Specs state "no photo capture on this page" with no phase pointer.
Rationale: the 07-21 hold was resolved by deletion in the 08-03 review (item 15); leaving it "deferred" invites re-implementation.
Pages: TM (Q4), VO (M2b).

**[PD-64] Unrequested-inbound handoff — should removal capture the Inbound Request no.?**
Provisional: **Yes — when the removal reason is "routed to inbound request", the dialog takes the Inbound No. as a structured field on the removal event.** No hard guard blocks removal without it.
Rationale: the memo convention is unqueryable; a structured link makes the recovery loop auditable.
Pages: TM (Q5/Q4-B/E-17), IR.

**[PD-65] Qty mismatch at match time (pool qty 2 vs candidate line ×1).**
Provisional: **Allow the match regardless of qty.** The difference is recorded on the match event and stated in the auto-comment ("registered qty 2 against a ×1 line").
Rationale: 1+1 sets and combined boxes make mismatches normal; blocking would strand real matches.
Pages: TM (Q2/E-12).

**[PD-66] Can an item enter the pool with NO tracking number (label destroyed)? — NO-DEFAULT**
If allowed, "match" has nothing to write onto the product line, which breaks the rescan-resolves loop that the whole flow depends on. Deciding either way changes the registration contract on View Orders. **Not decided — specs state the dependency and list it as an open question.**
Pages: TM (Q5/E-3), VO (M2b).

**[PD-67] Comments-hub entries whose entity is "Unrecognized pool" — where does a click go?**
Provisional: **Opens the tracking-missing page focused on that pool row; if the item is already resolved, it opens the matched order instead.**
Rationale: the click must land where the operator can act; resolved items have no row left.
Pages: TM (Q7/L-5).

---

## H. closing

**[PD-68] Closing report: CSV only, or also an instant-print surface [G-4]?**
Provisional: **CSV only.** No Print button on closing; [G-4] does not land on this page.
Rationale: the wireframe (SST, 2026-07-23 rework) ships CSV download and no print affordance; decision-sources' mention is the older artifact → conflict C-4, global delta GD-9.
Pages: CL (OQ-O1/OQ-5).

**[PD-69] How is a duplicate warning cleared toward "0 warnings"?**
Provisional: **✕-delete the duplicate row after logging the combined-box reason as an order comment. Deleted warning rows still count in History's "warnings raised → resolved".**
Rationale: matches State 4's 3→3 display and keeps the raised count honest.
Pages: CL (OQ-O2/E-8).

**[PD-70] Same-day re-closing and how History represents sessions.**
Provisional: **After a confirmed closing, no second session is allowed the same calendar day. History shows one row per date. Cancelled sessions are retained backend-side [G-8] and are not displayed.**
Rationale: the History table's schema (one row, always "Match") assumes uniqueness.
Pages: CL (OQ-O4/OQ-2/OQ-8/E-42/E-45).

**[PD-71] Daily Shipping Status auto-update contract — which sheet and column mapping? — NO-DEFAULT**
The target artifact ("SS Daily Shipping Status") is external and not described in any input. **Not decided — specs state that confirmation triggers the update, that failure must surface and never invalidate the closing, and list the mapping as an open question.**
Pages: CL (OQ-O5/E-38).

**[PD-72] Should closing confirmation (or unresolved warnings at end of day) notify Slack?**
Provisional: **No Slack route in v1** (routing table's "decide per feature at dev time" row stays unused here).
Rationale: inventing a channel would create an unowned alert stream.
Pages: CL (OQ-O6).

**[PD-73] Is scanning locked after Confirm Closing?**
Provisional: **Yes — the scan input is disabled in State 4.**
Rationale: a confirmed closing is an immutable record; live input on it would produce scans belonging to no session.
Pages: CL (OQ-1/E-10).

**[PD-74] Correction path when an extra parcel is found AFTER confirmation — NO-DEFAULT**
No reopen/amend affordance exists anywhere in the wireframe, and inventing one changes the immutability model chosen in PD-73/PD-70. **Not decided — specs state the lock and list the correction path as an open question.**
Pages: CL (OQ-1).

**[PD-75] The original OK row of a duplicate pair is deleted (M2) — is the surviving duplicate re-judged?**
Provisional: **No auto-re-judgment.** The operator deletes the duplicate row and rescans.
Rationale: retro-judging a past row would rewrite the scan sequence's meaning; a rescan produces a clean, timestamped verdict.
Pages: CL (OQ-3/E-8).

**[PD-76] Verdict labels for non-Processing abnormal statuses (Cancelled / Hold / Shipped / Completed / Refunded).**
Provisional: **Same "⚠ Not outbounded" pill, with the actual status rendered in the Status column. [Process this order] (M1) appears only for `Processing`.**
Rationale: M1 is a Processing→Prepare Shipment transition; offering it elsewhere would produce an invalid mutation.
Pages: CL (OQ-4/E-5).

**[PD-77] Is the M1 Zero Packing checkbox mandatory?**
Provisional: **Mandatory — [Process Outbound → resolve warning] stays disabled until it is checked.**
Rationale: it is step 6 of the current process; an unchecked attestation would make the resolution meaningless.
Pages: CL (OQ-6/E-22).

**[PD-78] A session spanning midnight (start 23:50, confirm 00:10).**
Provisional: **The snapshot belongs to the session's START date.**
Rationale: the target count and the parcels are the start date's work.
Pages: CL (OQ-7/E-41).

---

## I. inbound-request

**[PD-79] Post-registration correction / cancellation of a request — NO-DEFAULT**
The wireframe has no edit, cancel, or void affordance; only tracking additions, View Orders qty edits, and comments. A wrong SKU/route/supplier, or a purchase cancelled before dispatch, has no defined path. Adding a cancel/void status is a new feature with its own Slack/comment trail. **Not decided — specs state the current immutability and list this as an open question.**
Pages: IR (O-1/OQ-1).

**[PD-80] OTHER route downstream rendering (G-5 says exactly 4 routes).**
Provisional: **OTHER renders as black bold "OTHER ({channel name})" wherever routes are shown** (Request List, View Orders scan badge, Inventory route filter), and the free-text channel is carried into the Procurement Hub sheet.
Rationale: the form has offered Other since 2026-07-26; the badge must render something, and the channel text is the only meaningful content → global delta GD-2.
Pages: IR (O-4/S1-2), VO, INV.

**[PD-81] Deleting or editing a SAVED tracking number.**
Provisional: **Deletable/editable only while no scan has matched it. Once matched, blocked** (correction goes through a comment and, if needed, a new request).
Rationale: removing a matched number would orphan the State 6 reconciliation that used it.
Pages: IR (O-2/OQ-5/E-38).

**[PD-82] The same tracking number entered on two different requests.**
Provisional: **Blocked at save** with an error naming the other Inbound No. (page-level application of PD-8).
Rationale: View Orders resolves a scan to exactly one request; two owners make the scan non-deterministic.
Pages: IR (O-3/OQ-4/E-21/E-35).

**[PD-83] The same SKU picked twice in one request.**
Provisional: **Blocked with an inline notice** ("Already added — edit the quantity on the existing row").
Rationale: two rows for one SKU would double-count in the reconciliation table and in the PH sheet.
Pages: IR (OQ-2/E-12).

**[PD-84] Expected qty edited down to exactly the already-received qty — auto-INBOUNDED?**
Provisional: **No auto-transition.** The edit re-enables Confirm Full Inbound in View Orders State 6; a human presses it.
Rationale: consistent with the closing/State-6 doctrine that gating enables, never auto-commits.
Pages: IR (OQ-6/E-43), VO (M6).

**[PD-85] Adding tracking numbers to an already-INBOUNDED request (late split shipment).**
Provisional: **Blocked.** A late shipment is registered as a new inbound request.
Rationale: INBOUNDED is terminal; reopening it would invalidate the Received Date and the completed reconciliation.
Pages: IR (OQ-7/E-28).

**[PD-86] An inbound tracking number that collides with a customer-order (outbound) tracking number.**
Provisional: **Allowed — separate namespaces. View Orders resolution precedence puts inbound-request tracking first (State 6), per S6-1.**
Rationale: carriers reuse number ranges across directions; the precedence rule already exists in the wireframe.
Pages: IR (E-22), VO (S6-1/E-8).

---

## J. Appendix — decisions explicitly left to development (no owner input needed)

Specs must state a default and mark it dev-owned; these are NOT owner questions and are not tracked as PDs.

| Area | Items |
|---|---|
| Idempotency [G-9] | key format/TTL, client debounce interval, how rejected duplicates surface (all 8 pages) |
| Toasts [G-2] | duration, stacking vs single-slot replacement, exact failure copy |
| Print [G-4] | agent product choice, timeout, retry policy, job polling |
| Audio [G-3] | synth parameters, warning-vs-send tone separation, TTS voice fallback chain, AudioContext resume |
| Data | live-feed retention horizon + export format, CSV encoding/columns, pagination page sizes, audit draft autosave, location-code regex and line-derivation parsing |
| Costing | audit Loss product-cost source (FIFO lot cost recommended; deferred 2026-07-22) |
| Sync | multi-operator live-sync transport and latency (closing, State 6), comment freshness (poll vs push), candidate recompute trigger (tracking-missing) |
| Import | max rows/file size, header-matching policy, MKT- numbering scheme, uploaded-file retention |
| Misc | sticky columns on the 1680px table, multi-match selection layout, comment search debounce/index scope, batch chunk size, "Other"-route morning-check channel |
