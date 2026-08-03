# M3a — Cross-Page Consistency Verification (8 specs + `_global-rules`)

**Method:** VERIFICATION METHOD 3a. All eight screen specs plus `_global-rules.md` v1.0 read as one corpus and diffed on six axes: (1) shared behavior described twice, (2) canonical event names, (3) undeclared G-rule deltas, (4) PD interpretation drift, (5) cross-references, (6) terminology.
**Date:** 2026-08-03 · **Scope:** `wms2/specs/{view-orders, order-detail, ready-to-outbound, stock-status, order-management, tracking-missing, closing, inbound-request}.md` + `_global-rules.md`
**Corpus size:** 14,878 lines / ~1.66 MB.

Page codes: **VO**=view-orders · **OD**=order-detail · **RTO**=ready-to-outbound · **INV**=stock-status · **OM**=order-management · **TM**=tracking-missing · **CL**=closing · **IR**=inbound-request · **GR**=`_global-rules.md`.

**Result: 20 defects — 10 HIGH · 7 MEDIUM · 3 LOW.**
The specs are internally rigorous and cite each other heavily; every defect below is a *cross-document* disagreement, not a gap inside one file. Nine of the ten HIGH defects are **undeclared** contradictions (no delta, no rationale, no date); the tenth (D4) is declared on one side only.

---

## Defect table

| # | Sev | Axis | Pages | Defect |
|---|---|---|---|---|
| D1 | HIGH | shared behavior | VO · OD · INV | Cancel Inbound (restock) has three incompatible contracts |
| D2 | HIGH | shared behavior / undeclared delta | CL · VO · OD | Closing M1 outbounds an order without the "every line INBOUNDED" gate |
| D3 | HIGH | terminology | CL · VO · OD | `Cancelled` used as an order status where the 8-status rule forbids it |
| D4 | HIGH | terminology / G-rule | GR · VO · IR | `[G-11]` reason enum third option: `Other` vs `Other (memo)` |
| D5 | HIGH | terminology | RTO · VO · OD | RTO invents a third line status `OUTBOUNDED` |
| D6 | HIGH | PD usage | RTO · OD | PD-80 `OTHER (channel)`: RTO says it renders on Order Detail, OD says it never does |
| D7 | HIGH | terminology | all 8 | Comments hub copy is not byte-identical across the eight specs |
| D8 | HIGH | shared behavior | RTO · OD · VO | `@mention` Slack fan-out: one message per mention vs one message total |
| D9 | HIGH | cross-reference | INV · OD · VO | INV quotes the retired control name **Request Inbound** as normative |
| D10 | HIGH | cross-reference | VO · OM | VO names Order Management as a place Hold is applied; OM removed all hold controls |
| D11 | MED | G-rule delta | GR · CL | `[G-3](a)` scope list omits Closing's outbound-class button |
| D12 | MED | terminology | GR · INV | `−`/`＋` glyph mismatch on `Record Outbound` / `Record Inbound` (U+2212 vs U+FF0D/U+FF0B) |
| D13 | MED | cross-reference | GR + 5 specs | `[GD-n]` global-delta IDs are cited but defined nowhere in the corpus |
| D14 | MED | event names | all 8 | Same cross-page action, five different event names (idempotency, inventory movement, comment search, Slack dispatch, line inbound) |
| D15 | MED | G-rule delta | VO · RTO | Two incompatible resolutions of "what counts as a `[G-2]` confirming action" |
| D16 | MED | cross-reference | VO · TM · OM · RTO · CL · IR | Deep-link path form inconsistent (`/#reqlist` vs `/index.html#reqlist`) |
| D17 | MED | terminology | GR · VO · IR | `[G-11]` status pill: GR says `PARTIAL (n/m remaining)`, pages render `PARTIAL {received}/{expected}` |
| D18 | LOW | cross-reference | RTO | "removed from … respectively" maps 5 features to 3 pages and does not resolve |
| D19 | LOW | terminology | CL · OD | Order-status casing (`Prepare Shipment` vs `prepare-shipment`) never reconciled as label-vs-value |
| D20 | LOW | terminology | GR + all | `[G-3a]` vs `[G-3](a)` sub-rule citation form is inconsistent |

---

## HIGH

### D1 — Cancel Inbound (restock) has three incompatible contracts
**Pages:** VO `[L-M1]` §3.10 + `[E-27]`/`[E-52]` · OD `[L-2]` §3 + `DC-11` · INV `[L-M4]` §3.16 + `BR-20`

> **VO §3.10:** "`2. Restock Qty` — number, **default = the quantity that was inbounded**, editable … **Validation:** restock qty may be **lower** than the inbounded qty (partial damage) and is accepted; **the remainder is accounted for by the memo** `[E-27]`. Restock qty **above** the inbounded qty is rejected `[E-52]`."

> **OD §3 `[L-2]` Cancel Inbound:** "2. Confirm step (destructive action) `[PD-5 · OWNER-PENDING]`, with an **optional free-text note**. … 4. Persist `DC-11 line_item.inbound_cancelled` (SKU, qty, INBOUNDED→PENDING, **`restock=true`**, note, actor, ts)"

> **INV §3.16 `[L-M4]`:** "Editing **below** the released quantity is **allowed**; **the remainder is auto-recorded as `ADJUST(−remainder)`** carrying the same memo `[PD-49 · OWNER-PENDING]`. … Setting it to `0` while `Yes` is selected is **blocked**"

Three different outcomes for one physical reversal:
- **restock decision**: VO/INV offer Yes/No radios; OD has none and hard-codes `restock=true`.
- **quantity**: VO/INV expose an editable Restock Qty; OD reverses the full line qty with no input ("Per-line inbound is all-or-nothing", BR-41 — stated for *inbound*, never extended to *cancel*).
- **the shortfall**: VO leaves an under-restock unaccounted ("accounted for by the memo" — no stock event); INV books `ADJUST(−remainder)` (`DC-6`, `source=m4-remainder`). VO's path silently loses units from the ledger that INV's path books.

OD's §6.5 even asserts these paths converge — "Inventory's M4 release path can reverse the same reservation this page's Cancel Inbound reverses `[PD-45]` — the server must guarantee one reversal per line" — while specifying a different write.

**Required fix:** adopt one contract (recommend INV's, because it is the only one that books the remainder) and restate the other two as explicit page deltas with rationale + date. Minimum: (a) VO `[E-27]` must say what happens to the un-restocked units — memo text is not an inventory event and violates `[G-8]`; (b) OD `[L-2]` must state in §3 that it always restocks the full line qty and why, or gain the Yes/No + qty controls; (c) all three must agree on the `0`-with-`Yes` case, which only INV specifies.

---

### D2 — Closing M1 outbounds an order without the "every line INBOUNDED" gate
**Pages:** CL §3.21 `[L-M1]` + `BR-7` · VO `BR-9` · OD `BR-1` / `[L-9]`

> **VO `BR-9`:** "`Outbound` is enabled **iff** the order has ≥1 line **and** every line is INBOUNDED **and** status ∈ {`processing`, `pending`} **and** not on hold **and** not already outbounded."

> **OD `[L-9]`:** "`enabled == every(line.inbound_status == INBOUNDED) && line_count >= 1 && order.status ∈ { processing, pending }`"

> **CL §3.21:** "**Gate.** `[Process Outbound → resolve warning]` is **disabled until the Zero Packing checkbox is ticked** `[PD-77 · OWNER-PENDING]`. … **On confirm.** … 2. **A real order-status mutation** `Processing → Prepare Shipment` … **Persisted.** DC-13 `order.status_changed` … **DC-14 `order.outbounded`** (canonical action event, same correlation id)"

Closing's gate is *only* Zero Packing + `status == Processing`. Inbound completeness is never mentioned in §3.21, in `BR-7`, or in Closing's edge cases. A `Processing` order with PENDING lines scanned at closing therefore emits the canonical `order.outbounded` through a path that both other specs declare impossible. Closing declares no delta on the outbound gate anywhere (its §3.23 negative inventory lists nine "must not exist" items; the gate is not among them).

**Required fix:** either (a) CL §3.21 enforces the same predicate and adds an edge case for "Processing order with non-INBOUNDED lines scanned at closing" (verdict stays `⚠ Not outbounded`, `[Process this order]` disabled with the reason), or (b) CL declares an explicit, dated delta on `BR-9`/`BR-1` with the rationale for why a physically packed parcel may ship with un-received lines, and VO/OD add the reciprocal note so their gate is not stated as absolute.

---

### D3 — `Cancelled` used as an order status where the 8-status rule forbids it
**Pages:** CL §3.6 verdict matrix + `BR-20` + `[E-5]` + `[PD-76]` · VO `BR-12` / `[L-S4-6]` · OD `BR-12` / `[L-8]`

> **VO `[L-S4-6]`:** "the system has exactly **8 order statuses**: `pending`, `processing`, `on-hold`, `completed`, `refunded`, `failed`, `shipped`, `prepare-shipment`. **There is no `returned` status and none may be invented.**"

> **OD `BR-12`:** "**Status vocabulary is exactly 8 WooCommerce statuses**… **`cancelled` is not among them** — cancelling is `✕ Cancel Order`."

> **CL §3.6 verdict matrix, row 6:** "Order status ∈ {`Pending`, `On Hold`, `Shipped`, `Completed`, **`Cancelled`**, `Refunded`, `Failed`} | `not_outbounded`"
> **CL `BR-20`:** "Non-`Processing` abnormal statuses (`Pending`/`On Hold`/`Shipped`/`Completed`/**`Cancelled`**/`Refunded`/`Failed`) share the `⚠ Not outbounded` pill, with the actual status shown…"

The PD register propagates the error: **PD-76** is titled "Verdict labels for non-Processing abnormal statuses (**Cancelled** / Hold / Shipped / Completed / Refunded)". A cancelled order in the 8-status model carries some *other* status value; Closing's `Order Status` column is specified to render a value the model does not produce.

**Required fix:** decide whether cancellation is a status or a separate flag (OD says flag). If flag: CL must render the underlying status plus a cancellation marker, and `BR-20` / `[E-5]` / the verdict matrix / PD-76's title must drop `Cancelled` from the status set. If status: VO `BR-12` and OD `BR-12` must be amended to 9 statuses and OD's `[L-8]` dropdown must list it.

---

### D4 — `[G-11]` reason enum third option: `Other` vs `Other (memo)`
**Pages:** GR `[G-11]` · VO `BR-53` / `[L-M6]` / QA · IR §3.3.5 / `BR-30` / QA

> **GR `[G-11]`:** "exact enum: \"Damaged/defective — cannot accept\" / \"Supplier qty change\" / **\"Other (memo)\"**."

> **VO `BR-53`:** "M6's third reason option label is exactly `Other`. `[G-11]`'s \"Other (memo)\" phrasing names the memo obligation, not the option string." — and VO's QA asserts it byte-exactly: "the third option's text is exactly `Other` — **not** `Other (memo)`".

> **IR §3.3.5 mapping table:** "| `Other (memo)` | `other` — the operator's memo text is **not** inlined…" — and IR's QA: "When an M6 edit uses reason `Supplier qty change`, then a second edit uses **`Other (memo)`**…"

VO declares its delta properly (rationale + date + `_review.md` C-11 citation). IR does not declare anything — it simply uses the global string. The two QA suites contain byte-exact assertions that cannot both pass against one implementation, and GR was never amended even though `_review.md` GD-4 called for exactly that alignment.

**Required fix:** amend GR `[G-11]` to the wireframe M6 strings (`Damaged/defective — cannot accept` / `Supplier qty change` / `Other`), rewrite IR's mapping-table left column and its QA scenarios to `Other`, and keep VO `BR-53` as the historical note.

---

### D5 — RTO invents a third line status `OUTBOUNDED`
**Pages:** RTO §3.4 step 5 / `BR-22` / `DC-9` / QA-DC-09 · VO `[L-S1b-21]` · OD `[L-10]`

> **VO `[L-S1b-21]`:** "**State machine (line):** `PENDING → INBOUNDED` on inbound; `INBOUNDED → PENDING` on Cancel Inbound (M1)."
> **OD `[L-10]`:** "**`Inbound Status`** renders exactly `INBOUNDED` (`.tag.tag-inbounded`, green solid) or `PENDING` (`.tag.tag-pending`, amber)."

> **RTO `BR-22`:** "Bulk Outbound sets each order's status to **`prepare-shipment`** and each `INBOUNDED` line to **`OUTBOUNDED`**."
> **RTO `DC-9`:** "per line: `line_status` `INBOUNDED` → `OUTBOUNDED`"

Neither VO nor OD has an `OUTBOUNDED` line state, and OD's rendering contract is exhaustive ("renders exactly … or …"). If RTO's write is implemented, every OD row for an outbounded order renders an unmapped status. RTO does not declare this as a delta.

**Required fix:** decide whether outbound is order-level only (then RTO must drop the line transition and `DC-9`'s `line_status` field) or line-level too (then VO `[L-S1b-21]` and OD `[L-10]` must add `OUTBOUNDED`, with the Cancel Outbound reversal `OUTBOUNDED → INBOUNDED` specified in both). Note OD `BR-19` / VO `[L-S3-2]` both say Cancel Outbound "touches **no** line-level inbound state", which favors order-level only.

---

### D6 — PD-80 `OTHER (channel)`: RTO says it renders on Order Detail, OD says it never does
**Pages:** RTO §1.4 + §4.2 · OD `[L-4]` + §2.6 `[C-3]`

> **RTO §1.4:** "[G-5] route labels (SMART BUY · JIT (channel) · WHOLESALE · PARTNERSHIP · **OTHER (channel)** `[PD-80 · OWNER-PENDING]`) are rendered on View Orders, Inventory, **and Order Detail** — not here."
> **RTO §4.2:** "No SMART BUY / JIT (channel) / WHOLESALE / PARTNERSHIP / **OTHER** label on this page; those render on View Orders, Inventory, **and Order Detail** [G-5]"

> **OD `[L-4]`:** "**`OTHER ({channel})` does not appear on Order Detail line items.** OTHER is an *inbound-origin* route offered by the Inbound Request form; the order-facing badge set stays at four `[G-5]` `[C-3]` `[PD-80 · OWNER-PENDING]`. If a future order-side consumer needs it, that is a change to `[G-5]`, not to this page."

Same PD, opposite readings. GR `[G-5]` supports OD ("Order-facing badges (4)" excludes OTHER; "consumers = View Orders badges, Inventory, Order Detail" is a *page* list, not a *value* list) — but VO `[L-S1-6]` and `[L-S0-2]` **do** render `OTHER ({channel})` on order rows, so the "order-facing badges are exactly 4" rule is itself already violated on VO.

**Required fix:** state, in GR `[G-5]`, exactly which surfaces may render `OTHER (channel)` on order-facing rows. Then correct whichever of RTO §1.4/§4.2 or OD `[L-4]` disagrees, and reconcile VO `[L-S1-6]`'s `OTHER ({channel})` badge with the "exactly 4 order-facing badges" clause.

---

### D7 — Comments hub copy is not byte-identical across the eight specs
**Pages:** all 8. RTO §3.10 states the premise: "The hub is **identical on all eight screens**; only the entry points differ." Every spec asserts its strings byte-exactly in QA.

| String | Variants found |
|---|---|
| Mentions pane header | `Comments mentioning me · Click to open the order` (OD, OM, RTO, INV) · `Comments mentioning me` (TM) · `Comments where I'm tagged` (CL, IR) |
| Saved pane header | `Saved comments · Click to open the order` (OD, OM, RTO, INV) · `Saved comments` (TM) · `Comments I saved` (CL, IR) · `Comments I saved · Click to open the order page` (VO) |
| Unstar hint | `Unstar to remove` (OD) · `Unstar to remove from the list` (RTO, TM) · `Unstar to remove from this list` (INV, CL) · `Unstar to remove from list` (OM, IR) |
| Read-all action | `Mark all read` (43 occurrences: OD, OM, RTO, INV, TM, CL) · `Mark all as read` (8: VO, IR) |
| Search results header | `{n} results · newest first · click to open the order` (16 occurrences) · `… click to open the **order page**` (3, VO only) |
| Empty search state | `No matching comments` (13) · `No matching **C**omments` (3, VO only) |

VO is the outlier on four of the six; CL and IR are the outliers on the two pane headers.

**Required fix:** pick one canonical string per row (recommend the 4-page majority: `Comments mentioning me · Click to open the order`, `Saved comments · Click to open the order`, `Unstar to remove from the list`, `Mark all read`, `… click to open the order`, `No matching comments`), publish the six strings in `_global-rules` `[G-7]` as byte-exact contract, and rewrite the divergent specs **and their QA assertions**.

---

### D8 — `@mention` Slack fan-out: one message per mention vs one message total
**Pages:** RTO §3.9 + QA-L9-11 · OD §3 `[L-1]` step 7 + §6.1 + `[E-80]` · VO `DC-20`

> **OD §3 `[L-1]`:** "7. For **each distinct** resolved mention, dispatch **one Slack message** `[G-7]` and persist `DC-27 comment.mention_notified`…"
> **OD §6.1:** "**One message per distinct mention.** Two `@Dean` tokens in one comment produce one Slack message `[E-80]`."
> **VO `DC-20`:** "`comment.mention_notified` … | **one per mentioned user**"

> **RTO §3.9:** "**Multiple mentions in one comment produce exactly one Slack message naming every mentioned user**, not one message per user [E-75]." (asserted by QA-L9-11: "negative — Three mentions produce one Slack message")

GR `[G-7]`'s payload field is singular ("@mentioned user"), which favours OD/VO. RTO's negative QA scenario would fail an OD-conformant implementation and vice versa.

**Required fix:** fix the fan-out rule in GR `[G-7]` ("one message per distinct resolved mention; the same user mentioned twice in one body yields one message"), then rewrite RTO §3.9 and QA-L9-11. Note the downstream `DC-*` shapes differ too (per-user rows vs one row) and must be aligned.

---

### D9 — INV quotes the retired control name **Request Inbound** as normative
**Pages:** INV `[L-F2]` §3.18 + QA-FRM-03 · OD `BR-4` / `BR-40` / QA · VO

> **INV §3.18 `[L-F2]`, "Purpose note, **verbatim**":** "Record a warehouse inbound directly… For order-linked inbound, use **Request Inbound** on View Orders / the order detail."
> **INV QA-FRM-03 `[WF]`:** "**Then** the `.form-note` reads **exactly** `… For order-linked inbound, use Request Inbound on View Orders / the order detail.`"

> **OD `BR-4`:** "The name **\"Request Inbound\" is retired and must not reappear.**"
> **OD `BR-40`** lists it among "Removed features must NOT be re-implemented", and OD QA asserts: "the string `Request Inbound` appears **nowhere** in the rendered page in either state, including the legend".

The control does not exist on either named page: VO uses row `Inbound` / `Inbound + Outbound` / `Bulk Inbound (Selected)`; OD uses per-row `Inbound` + `Bulk Inbound Selected Items`. INV promotes stale wireframe copy to a byte-exact QA contract, which will send an operator to a button that no longer exists.

**Required fix:** register the note as a wireframe defect (page-scoped ID, in the same style as `[RTO-WFX-n]`), respec the correct copy (e.g. "For order-linked inbound, use the row `Inbound` buttons on View Orders or Order Detail"), and split INV QA-FRM-03 into a `[WF]` assertion on the shipped stale string and an `[ADMIN]` assertion on the corrected string.

---

### D10 — VO names Order Management as a place Hold is applied; OM removed all hold controls
**Pages:** VO `[L-S5-F]` §3.7 + §9.1 + QA (byte-exact legend assertion) · OM `[L-3]` §3.8 + `BR-10` + QA-LST-04

> **VO `[L-S5-F]`:** "the hold itself is applied and released **elsewhere** — the `Hold Shipment` action in OMS / Order Detail, **or in Order Management**, by CS."
> **VO §9.1:** "Applying or releasing **Hold** | **OMS / Order Detail, or Order Management (CS)**"
> **VO QA** asserts the legend paragraph byte-exactly: "…in OMS/Order detail **or Order Management** (CS team)."

> **OM `BR-10` (2026-08-03):** "**Bulk Hold Shipment must not exist on this screen.** Hold is `Change Status → on-hold` on **Order Detail**."
> **OM §3.8 `[L-3]`:** "**A bulk \"Hold Shipment\" control must NOT exist on this screen.** There is no button, no menu item, no keyboard shortcut, and no bulk action that places orders on hold from the Order Management Dashboard."
> **OM QA-LST-04 (neg)** searches the whole document for `Hold Shipment` / `Bulk Hold` and requires zero hits outside the legend's negative entry.

The 2026-08-03 removal on OM is dated later than VO's wireframe legend text, and VO adopts the stale text as normative without flagging it.

**Required fix:** correct VO `[L-S5-F]` and §9.1 to "OMS / Order Detail" only, and re-tier the VO QA legend assertion as a `[WF]`-only assertion on stale wireframe copy with an `[ADMIN]` assertion on the corrected sentence (same treatment VO already gives WF-1 / WF-3 / WF-13).

---

## MEDIUM

### D11 — `[G-3](a)` scope list omits Closing's outbound-class button
**Pages:** GR `[G-3]` · CL §3.21 step 5 · `_plans/_provisional-decisions.md` PD-2

> **GR `[G-3](a)`:** "Scope: every outbound-class button on every page — View Orders (…), RTO (Bulk Outbound), Order Detail (Outbound), Inventory (− Record Outbound)."
> **CL §3.21 step 5:** "**Audio.** This is an outbound-class button, so it plays the `[G-3a]` send sound … PD-2's enumeration names View Orders, RTO, Order Detail and Inventory and does **not** name closing, while adjudication C-5's verdict is scope-by-button-class … This spec applies the rule by class. Reversal impact if the owner scopes PD-2 by page instead: delete this clause; nothing else changes."

Closing handles this correctly — it declares the delta, states both readings, and gives the reversal impact. The defect is that **GR and PD-2 were never updated**, so the global rule's own enumeration is now known-incomplete and a reader who trusts it will build the wrong scope.

**Required fix:** amend GR `[G-3](a)`'s scope list to include Closing's `[Process Outbound → resolve warning]` (with CL's "audibly distinct from the `[G-3b]` warning voice" constraint), and update PD-2's page list in the register. Keep CL's tension paragraph as the rationale.

---

### D12 — `−`/`＋` glyph mismatch on `Record Outbound` / `Record Inbound`
**Pages:** GR `[G-3]` · INV `[L-F2]`/`[L-F3]` + QA-FRM-03/08/11/12 + `DC-1`/`DC-2`

GR writes `− Record Outbound` with **U+2212 MINUS SIGN**; INV writes `－ Record Outbound` with **U+FF0D FULLWIDTH HYPHEN-MINUS** and `＋ Record Inbound` with **U+FF0B FULLWIDTH PLUS** (verified by codepoint). INV's QA-FRM-08 asserts "the button reads `－ Record Outbound`" byte-exactly, so a developer copying GR's glyph fails INV's QA.

**Required fix:** make GR quote INV's shipped glyphs (`＋`/`－`), since the wireframe is SST for button labels, and add a note that both are byte-exact contract characters.

---

### D13 — `[GD-n]` global-delta IDs are cited but defined nowhere in the corpus
**Pages:** GR line 19 (`[GD-5]`) · OD `[BR-39]`/§3.0.1 · TM `[BR-9]`/§5.2/§10 · CL §3.10/§6.5/§10 · INV `[BR-1]`/§10 · IR §10

`GD-1` … `GD-10` are defined only in `_plans/_review.md` §4, which is not part of the 8-spec + `_global-rules` deliverable. `_global-rules.md` itself cites `[GD-5]` in the body of `[G-2]` — so even the rules document has a dangling reference. A reader of the corpus cannot resolve `[GD-1]`, `[GD-2]`, `[GD-5]`, `[GD-6]`, `[GD-7]`, `[GD-8]`, `[GD-9]`.

**Required fix:** either (a) fold the ten GD deltas into `_global-rules.md` as a short "Amendment log" section so every `[GD-n]` resolves inside the corpus, or (b) strip `[GD-n]` citations from the shipped specs and replace them with the resulting rule text plus a date.

---

### D14 — Same cross-page action, five different event names
**Axis:** canonical event names. GR fixes 10 names; the 10 are used correctly everywhere (verified: `comment.posted`, `comment.mention_notified`, `comment.starred`/`unstarred`, `comment.read`/`mark_all_read`, `comment.auto_posted`, `product.barcode_registered`, `order.status_changed`, `order.outbounded`, `print.job_result` — **zero divergences**). The defect is the tier below: shared *concepts* with per-page names, which `_review.md` §3.3's "one canonical name per shared event" convention was meant to prevent.

| Shared concept | Names in use |
|---|---|
| Idempotent duplicate suppressed | `idempotency.duplicate_rejected` (VO, RTO) · `idempotency.duplicate_suppressed` (OM) · `action.idempotency_suppressed` (OD) · `inbound_request.idempotent_replay_suppressed` (IR) · `unrecognized_item.match_duplicate_suppressed` (TM) |
| Stock moved | `inventory.stock_applied` (VO) · `inventory.movement` (OD) · `inventory.stock_decremented` + `inventory.reservation_consumed` (RTO) · `stock.inbound.recorded` / `stock.outbound.recorded` (INV) |
| Comment search executed | `comment.search_executed` (VO) · `comment.search.executed` (INV) · `comment.searched` (TM) · declared NON-event `NE-8` (OD) · optional telemetry `DC-17` (RTO) |
| Slack dispatch outcome | `slack.dispatch_result` (VO) · `slack_notification.sent` (IR) · `slack.registration_notified` / `slack.aging_digest_sent` / `notification.retry_result` (TM) · folded into `comment.mention_notified` (OD) |
| Line received | `item.inbounded` (VO) · `line_item.inbounded` (OD) |

Also: INV uses three-segment dotted names (`audit.session.confirmed`, `stock.reserve.released`, `comment.search.executed`) against the corpus-wide "lowercase `entity.action`" form.

**Required fix:** promote the five concepts above into GR's canonical list (or a second "shared, non-canonical" list) with one name each, normalize INV's three-segment names to two segments, and reconcile the comment-search case: OD declares it a NON-event while three pages persist it, which is a `[G-8]` disagreement, not just a naming one.

---

### D15 — Two incompatible resolutions of "what counts as a `[G-2]` confirming action"
**Pages:** VO `BR-51` · RTO `BR-34` + §4.1

> **VO `BR-51`:** "The floating-save `✓ Saved` chip is the `[G-2]` confirmation for shelf, location and received-qty micro-saves — rendered in place beside the field instead of the top-right slot. … This is a **rendering-position delta, never a removal** of the confirmation."

> **RTO `BR-34`:** "Actions whose result *is* immediately and unambiguously visible in place — the star glyph filling, a panel expanding, a modal opening, a checkbox toggling, `Cancel` — are confirmed by that in-place change and **do not additionally toast**."

VO's model: the confirmation always exists, only its position moves. RTO's model: in-place feedback *replaces* the confirmation entirely for a named class of actions. Both are declared deltas with rationale, so neither is a rule violation — but the corpus now teaches two rules for the same question, and RTO's own `BR-34` notes the owner may read `[G-2]` literally instead.

**Required fix:** state the boundary once in GR `[G-2]` — e.g. "state-changing actions always confirm; the confirmation may render in place instead of the toast slot; pure view-state changes (expand, tab, checkbox, modal open, Cancel) are not confirming actions" — and have VO and RTO cite it rather than each defining it.

---

### D16 — Deep-link path form is inconsistent
**Pages:** GR `[G-12]` · VO §3.1 vs §3.8/§6.2/QA · TM §6.3 · OM §6 · RTO §3.20 · CL §3.7

- Inbound Request: `../inbound-request/#reqlist` (GR `[G-12]`, IR §6, OM §6, VO §3.1 `[L-S0-2]`) vs `../inbound-request/index.html#reqlist` (VO §3.8 `[L-S6-2]`, VO §6.2, VO QA, TM §6.3). VO uses **both forms internally**.
- Order Detail: `../order-detail/#{orderNo}` (OM) vs `../order-detail/index.html#{order_no}` (TM) vs `../order-detail/` (RTO, CL).

QA scenarios assert the href suffix (VO: "its `href` ends with `../inbound-request/index.html#reqlist`"), so the divergence is testable and will fail.

**Required fix:** fix one form in GR `[G-12]` (recommend the directory form `../{slug}/#anchor`, which is what the live wireframe URLs use) and normalize all six specs plus their QA assertions.

---

### D17 — `[G-11]` status pill: GR says "n/m remaining", pages render received/expected
**Pages:** GR `[G-11]` · VO `[L-S0-2]` / `[L-M5]` / `BR-23` · IR `[E-30]` / `BR-10`

> **GR `[G-11]`:** "`REQUESTED → PARTIAL (n/m **remaining**, amber) → INBOUNDED`."
> **VO `[L-S0-2]`:** "Status renders `REQUESTED` (amber) or **`PARTIAL {received}/{expected}`**"
> **IR `[E-30]`:** "Status pill renders `PARTIAL {received}/{expected}` (e.g. **`PARTIAL 120/180`**)"

`120/180` is received-of-expected, not remaining. GR's parenthetical is semantically wrong and would produce `PARTIAL 60/180` if implemented literally.

**Required fix:** GR `[G-11]` → "`PARTIAL ({received}/{expected}, amber)`".

---

## LOW

### D18 — RTO's "removed … respectively" does not resolve
**Page:** RTO §4.2, last row.

> "**Order search bar, pagination controls, per-PIC row grouping, Bulk Hold, a scan input, a resolved log** | … they were removed from `tracking-missing`, `order-management`, and `closing` **respectively** …"

Six features, three pages, "respectively" — the mapping is unrecoverable. Verified true: Bulk Hold → order-management (`BR-10`), resolved log + per-PIC grouping → tracking-missing. The other three have no named origin.

**Required fix:** replace with an explicit per-feature attribution, or drop "respectively".

---

### D19 — Order-status casing never reconciled as label-vs-value
**Pages:** CL §3.6/§3.7/`BR-20` · OD `[L-8]`/`BR-1` · VO `[L-S4-6]`

CL renders `Prepare Shipment`, `Processing`, `On Hold`, `Pending` (title case, spaces) in its `Order Status` column and verdict prose; OD and VO use `prepare-shipment`, `on-hold`, `processing` (lowercase, hyphens) as the vocabulary. CL's own `DC-13` uses the lowercase form (`processing → prepare-shipment`), so the split is presumably label-vs-value — but no spec says so, and CL's `BR-20` mixes both registers in one sentence.

**Required fix:** state once (GR, or CL §3.7's column contract) that the 8 statuses are lowercase-hyphenated *values* rendered as title-case *labels*, and give the label mapping.

---

### D20 — `[G-3a]` vs `[G-3](a)` citation form is inconsistent
**Pages:** GR `[G-3]` uses `(a)` / `(b)` / `(c)`. Specs cite `[G-3a]` (VO, RTO, CL), `[G-3](a)` (OD, INV), `[G-3b]`/`[G-3](b)`, `[G-3c]`/`[G-3](c)` interchangeably.

Cosmetic, but it defeats a mechanical `[G-n]` coverage grep and inflates the citation counts unevenly.

**Required fix:** pick `[G-3a]` or `[G-3](a)` and normalize; add the sub-rule citation form to `_review.md` §3's binding conventions.

---

## What was checked and found clean

Recorded so a re-run does not re-open them:

- **The 10 canonical event names** (`comment.posted` · `comment.mention_notified` · `comment.starred`/`unstarred` · `comment.read`/`mark_all_read` · `comment.auto_posted` · `product.barcode_registered` · `order.status_changed` · `order.outbounded` · `print.job_result`) are **byte-identical in all 8 specs**. Zero divergences.
- **Slack channel names and IDs** — `#fulfillment-admin-comments` (`C0BMGEWM5QA`), `#unrecognized-tracking`, `#wholesale-ops`, `#partnership-kr` — are consistent everywhere; no spec writes "pending" for the comment-mention row (R-10 honored).
- **`[G-4]` print-surface registry** matches GR exactly: VO (3 surfaces), RTO (3), OD (1); INV, OM, TM, IR, CL all declare N/A explicitly, with CL carrying the PD-68 rationale and reversal impact.
- **`[G-2]` refresh exception** — RTO Bulk Outbound is the sole exception in every spec; VO, OD, OM and IR each state they have none.
- **`[G-1]` scanner scope** — VO and CL are the two scan surfaces; OD, RTO, INV, OM, TM, IR each declare N/A explicitly (IR with its Enter-must-not-submit delta).
- **`[G-13]` sample dual view** — OM is the primary home; OD (display), RTO (picking list) and the `(+ sample set)` carrier-facing string agree across all three.
- **`[G-10]` multi-tracking** — IR is the primary home; VO, TM agree that every registered number matches and that partial arrivals accumulate.
- **PD-60 / PD-64** removal reason enum and Inbound No. capture — TM's implementation matches the register exactly.
- **PD-3 (append-only comments)** — all 8 specs agree, with negative QA on 6 of them.
- **PD-46 (1:1 location)** — VO, INV, RTO agree, including the legacy-violation case (VO `[E-82]`).
