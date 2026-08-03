# Order Detail — Screen Specification (WMS 2.0)

Page slug: `order-detail` · Spec version 1.2 · 2026-08-03
Wireframe (SST): `wms2/order-detail/index.html` · Live: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/order-detail/
Global rules: `_global-rules.md` (cited as `[G-n]`). This document writes **page deltas only** and never restates a global rule body.
Adjudications: `_plans/_review.md` §1 (cited as `[C-n]`) — see §2.6 for the ones that bind this page.
Provisional decisions: `_plans/_provisional-decisions.md` (cited inline as `[PD-n · OWNER-PENDING]`).
Known wireframe defects: `_plans/_wireframe-fixes.md` (cited as `[WF-n]`). Where the wireframe text is stale, this spec states the **decided** behavior, not the wireframe text.

---

## 1. Purpose & Users

### 1.1 What this screen is

Order Detail is the **single-order command center**. It is the one screen that shows, for one order, everything the fulfillment operation knows: WooCommerce commerce data, the per-line sourcing/purchase record, live inventory counts, the carrier shipment and its tracking history, the operator comment thread, and the Inbound/Outbound Actor Log. It is the screen people open when something is wrong, when someone must decide, or when someone must be held accountable.

The live-admin capture it reproduces is Order **#407847** (customer Maytal Saltoon, AU, carrier YUN, 4 line items). All demo values in the wireframe are that real order.

### 1.2 Who uses it

| Role | What they come here to do |
|---|---|
| Order team (desk, dual monitor) | Change status, place/release hold, edit PIC, correct addresses, fill or verify the agent-tracking fields per line (Order Number · Order Date · Product Cost · Tracking Number · CP Link), post comments, clone/cancel/reset orders |
| Warehouse lead / handler (arrives mid-flow) | Inbound a specific product that just arrived, cancel a wrong inbound with a restock note, read the Actor Log to settle "who did this", print the label |
| Admin / auditor | Read the Actor Log and comment history, reconcile inventory movements against the order, open Audit History |
| CS-driven interrupts | Place the order On Hold for a cancellation or address change; release the hold when CS clears it |

Permissions in v1: a **single admin role** — no role gating on any control on this page `[G-15]` `[PD-1 · OWNER-PENDING]`.

### 1.3 The operator's physical reality (this shaped the design)

- **This is not a scan surface.** There is no scan input and there must never be one. `[G-1]` does not apply to Order Detail: scanner-in-hand work happens on View Orders and Closing. Order Detail is where an operator *stops moving and thinks* — usually at a desk, mouse in hand, with the order open because something already went wrong. Developers must not add a scan input, an autofocus trap, or a focus-return loop here; QA must not apply the `[G-1]` invariants to this page. See §9.1 `[BR-30]`.
- **The PIC pencil failed on the floor.** The live admin used a bare `✎` glyph, ~12px, grey-on-white, no border. Under warehouse lighting, at monitor arm's length, staff could not tell it was a control — they reported "PIC cannot be changed". It was replaced with a bordered button labelled **"✎ Edit"** on 2026-07-21 `[L-5]`. The same lesson governs every other affordance on this page: **if it is clickable, it has a border and a word.**
- **The unclickable Inbound button caused the double-processing bug.** In the live admin the inbound control was intermittently non-responsive; operators clicked it two or three times and the server processed every click. That is the origin of the double-click bug in the developer handoff notes (2026-07-21) and of `[G-9]`. On this page the page delta is that the fix is mandatory on **every** mutating control — per-row Inbound, Cancel Inbound, Bulk Inbound, Outbound, Cancel Outbound, Save, Delete, Add Line, Print and Add Comment — and that suppressed duplicates are themselves persisted (`DC-36`), so the fix is provable rather than merely claimed `[BR-32]`.
- **The line-items table is 1680px wide and scrolls horizontally** (`.litable{min-width:1680px}`). The Actions cell — where per-row Inbound / Cancel Inbound / ✎ / 🗑 live — sits at the far right after 18 columns. An operator who wants to inbound one product must scroll right; an operator who wants to ship the whole order must not have to. That is why **order-level actions (Bulk Inbound Selected Items, 📦 Outbound, + Add Line Item) live in the footer below the table**, reachable without any horizontal scroll, while per-product actions stay on the row `[L-2]` `[L-9]`. Whether the Actions/SKU columns should be sticky is a dev-time decision (§9.4 D-5).
- **Confirmations must be visible peripherally.** Operators glance, they do not read. The page delta on `[G-2]` is the toast-string registry in §3.0.2 — every confirming action on this page has a fixed success string, so an operator learns one vocabulary and QA can assert byte-exact text.
- **The Outbound button plays a sound.** Outbound is the last irreversible step before a parcel leaves; the page delta on `[G-3]`(a) is that Order Detail's `📦 Outbound` is in scope for the send sound and that this page has **no** TTS and **no** warning tone — neither `[G-3]`(b) nor `[G-3]`(c) has an analogue here `[PD-2 · OWNER-PENDING]` `[BR-29]`.
- **Comments are the packing-floor coordination channel.** "Pack this with extra care — repeat-purchase VIP" is not metadata, it is an instruction to a human who may be nowhere near a monitor. `@mention` is the reach mechanism into **#fulfillment-admin-comments** (`C0BMGEWM5QA`) `[G-7]`.
- **The Actor Log ends disputes at the shelf.** "Who inbounded this?" used to be unanswerable. The log answers it in one glance with Time · Action · SKU · Qty · Operator · Note `[L-3]`.

### 1.4 Operational moments this screen serves

1. **JIT purchase bookkeeping** — a handler who bought the item on Coupang after the customer ordered enters the purchase Order Number, Order Date, Product Cost, purchase Tracking Number and CP Link on that line `[L-12]`.
2. **Per-product inbound exception handling** — one of four items arrived; inbound just that one, or cancel a wrong inbound with a note `[L-2]`.
3. **Hold management for urgent CS** — customer wants to cancel or change the address; the order goes On Hold, goods receipt continues, shipping stops `[L-14]`.
4. **Dispute resolution** — Actor Log + comment history `[L-3]` `[L-1]`.
5. **Shipment correction** — change tracking number, reset the shipment, reprint the label `[L-F10]` `[L-F11]` `[L-13]`.

---

## 2. Screen Inventory & Wireframe Map

### 2.1 Declared unit count (for coverage audits)

- **Numbered legend dots: 14** (`1`–`14`), contiguous, **no numbering gaps**.
- **Modal keys: 1** (`M3`, delete-line confirmation).
- **Total legend units: 15.** This matches both planning lenses (order-detail.A: "14 dots + 1 modal = 15 units"; order-detail.B: "15 implementation units total") and the `_review.md` §2a coverage row for this page.
- **Page-furniture units (unnumbered on-screen controls that carry normative behavior): 17**, keyed `[L-F1]`–`[L-F17]` per `_review.md` §3.1.
- **Grand total specified units: 32.**

**Machine-checkable restatement of the above** (an auditor or QA agent can verify these five numbers against the live wireframe without reading a word of prose — asserted by `QA-MAP-1`):

| Assertion | Selector | Expected |
|---|---|---|
| Dots in State 1 | `#st-normal .dot` | 13 (`1`–`13`; no `14`) |
| Dots in State 2 | `#st-hold .dot` | 14 (`1`–`14`) |
| Dots in the modal | `#m-del .dot` | 1 (`M3`) |
| Total dot elements on the page | `.dot` | 28 |
| Legend list entries | `.legend ol li` | 14 |

Numbering notes an auditor must not flag as holes:
- The legend `<ol>` renders in DOM order **1, 2, 3, 4, 5, 6, 12, 10, 11, 14, 13, 9, 7, 8**. This is a render-order artifact of the 2026-07-22 and 2026-07-23 edits, not a gap. Every dot 1–14 exists on screen.
- Dot **14** exists only in State 2 (On Hold). Dots 1–13 exist identically in both states, which is why the total dot-element count is 28 and not 15.
- There are no `[L-{state}-F]` off-screen footer blocks on this page. The legend's closing paragraph ("Global nav · address fields · Operator Comments position · Fulfillment Tracking (SHIPMENT DETAILS + TRACKING HISTORY) · Line Items horizontal scroll are identical to the live admin (full capture 2026-07-21) — TRACKING HISTORY abbreviated here (the real screen shows all events, unchanged). Live data from Order #407847 (Maytal Saltoon).") is a provenance note; its content is specified under `[L-1]` (Operator Comments position), `[L-6]`, `[L-10]`, `[L-F8]`, `[L-F9]`, `[L-F12]` and `[L-F17]` — with the 1680px Line Items horizontal scroll specified in §1.3 and `[L-10]`.
- Per `_review.md` §3.1, Order Detail is keyed as a **single-state page**: `[L-n]`, not `[L-S1-n]`. The two tabs are a wireframe demo device, not two product screens `[BR-45]`.

### 2.2 States, modals and how to reach them

The wf-bar (`.wf-bar`) renders its controls in this DOM order — note that the modal button comes **first**, before the state tabs:

`Modal: Delete Line` · `1 · Processing (default)` · `2 · On Hold` · `Hide annotations`

| Key | Surface | DOM anchor | How to reach it | Legend dots present |
|---|---|---|---|---|
| **State 1** | Processing (default) | `section#st-normal` | Loads by default; or click the wf-bar button **`1 · Processing (default)`** | 1,2,3,4,5,6,7,8,9,10,11,12,13 |
| **State 2** | On Hold | `section#st-hold` | Click the wf-bar button **`2 · On Hold`** | 1–13 **+ 14** |
| **M3** | Delete-line confirmation modal | `div.overlay#m-del` | Click the wf-bar button **`Modal: Delete Line`**, or any `🗑` (`.act-ic .del`) in an Actions cell in **either** state | M3 |
| Sub-surface | Comments hub dropdown | `#inbox1` (State 1) / `#inbox1H` (State 2) | Click **`💬 Comments`** in the top nav of that state | 7 |
| Sub-surface | Change Status dropdown | `#statusdd` (State 1) / `#statusddH` (State 2) | Click **`Change Status ▾`** in that state | 8 |
| Sub-surface | Row edit mode | `tr.row-edit` | Pre-rendered on row 1 (SKU `100005104`) in both states as the worked example; in the real admin, click the row's `✎` (`.act-ic .edit`) | 12 |
| Chrome | Annotation toggle | `#annoToggle` | Click **`Hide annotations`** / **`Show annotations`** | — (wireframe chrome, not a product feature) |

**Both states are present in the DOM at all times.** `.ostate{display:none}` / `.ostate.on{display:block}` — switching tabs only moves the `on` class and scrolls to top (`window.scrollTo({top:0})`). This is the single most important fact for automated QA on this page: **any selector not scoped to `#st-normal` or `#st-hold` matches twice.** See §8.0.

State 2 is a **full duplicate of the page**, not a partial render (2026-07-22, commit `c17df7c`). Every `[L-n]` behavior specified below applies identically in both states except where the `[L-14]` diff list says otherwise.

### 2.3 Legend ↔ spec map (1:1)

| Dot | Legend headline (wireframe) | Spec section |
|---|---|---|
| 1 | Operator Comments upgraded — @mention → Slack, per-order history, ★ save to hub | §3 `[L-1]` |
| 2 | Inbound buttons reworked — per-row Inbound / Cancel Inbound + Bulk Inbound Selected Items | §3 `[L-2]` |
| 3 | Inbound/Outbound Actor Log (new) | §3 `[L-3]` |
| 4 | Line Items sourcing routes — 4 routes, black bold; JIT (channel); Order Number linked | §3 `[L-4]` |
| 5 | PIC edit made explicit — bordered "✎ Edit" button | §3 `[L-5]` |
| 6 | Fulfillment Tracking + TRACKING HISTORY — identical to live admin | §3 `[L-6]` |
| 7 | Top-right Comments hub — @ Mentions + ★ Saved + all-orders search | §3 `[L-7]` |
| 8 | Change Status dropdown — 8 WC statuses, applied instantly | §3 `[L-8]` |
| 9 | "Outbound" (relabeled) — enabled only when every item INBOUNDED | §3 `[L-9]` |
| 10 | Inventory columns cleaned — Delivery Company + Comments removed; Latest Inventory Count kept | §3 `[L-10]` |
| 11 | Product Name EN·KR — brand always bold-prefixed | §3 `[L-11]` |
| 12 | Line edit/delete UX — ✎ → inputs, ✓ Save / ✕ Cancel, 🗑 → M3 | §3 `[L-12]` |
| 13 | Print button — label just "Print" | §3 `[L-13]` |
| 14 | On Hold state view — amber badge + banner, Outbound disabled, Inbound allowed | §3 `[L-14]` |
| M3 | Delete-line confirmation modal | §3 `[L-M3]` |

### 2.4 Page furniture map (unnumbered, normative)

| Key | Control / block | Location | Specified in |
|---|---|---|---|
| `[L-F1]` | **← Back to Orders** (`.back`) | subbar, left | §3 furniture |
| `[L-F2]` | **↻ Audit History** (`.link-btn`) | subbar, right | §3 furniture |
| `[L-F3]` | **↗ View in WP** (`.link-btn.blue`) | subbar, right | §3 furniture |
| `[L-F4]` | **⧉ Clone Order** (`.link-btn.blue`) | subbar, right | §3 furniture |
| `[L-F5]` | **✕ Cancel Order** (`.link-btn.red`) | subbar, right | §3 furniture |
| `[L-F6]` | Order header block — `Order # 407847` + status badge + carrier badge (`YUN`) | title row | §3 furniture |
| `[L-F7]` | **View Label** | title row | §3 `[L-13]` |
| `[L-F8]` | 📋 Order Information panel (Order Date · Order Created At · Total Items · Total Discount · Total Amount · PIC) | info3 col 1 | §3 furniture |
| `[L-F9]` | 👤 Billing Address ✎ / 🚚 Shipping Address ✎ edit | info3 cols 2–3 | §3 furniture |
| `[L-F10]` | **✎ Change Tracking #** | Fulfillment Tracking | §3 furniture |
| `[L-F11]` | **Reset Order** | Fulfillment Tracking | §3 furniture |
| `[L-F12]` | SHIPMENT DETAILS table + `Last mile: AustraliaPost` chip | Fulfillment Tracking | §3 `[L-6]` |
| `[L-F13]` | Select-all checkbox (table header, `title="Select all"`) + per-row checkboxes | Line Items | §3 furniture |
| `[L-F14]` | **+ Add Line Item** | Line Items footer | §3 furniture |
| `[L-F15]` | **Total Quantity: 4** footer counter (`.tq`) | Line Items footer | §3 furniture |
| `[L-F16]` | **Hide Comments** toggle | Operator Comments header | §3 `[L-1]` |
| `[L-F17]` | Global nav (SkinSeoul · Operation AI ▾ · Catalog Management ▾ · OMS Center ▾ · Site Management ▾ · Customer Management ▾ · SkinSeoul WP Admin) + user chip + **Logout** | top nav | §3 furniture |

Three furniture keys are specified inside the legend entry they physically belong to rather than in §3's furniture block, because splitting them would separate a control from its behavior: **`[L-F7]` View Label** under `[L-13]`, **`[L-F12]` SHIPMENT DETAILS** under `[L-6]`, **`[L-F16]` Hide Comments** under `[L-1]`. The other **14** (F1, F2, F3, F4, F5, F6, F8, F9, F10, F11, F13, F14, F15, F17) are in §3's furniture block. 14 + 3 = **all 17 furniture keys have a normative spec paragraph in §3**.

### 2.5 Wireframe defects, demo artifacts and non-defects

**A. Registered wireframe defects touching this page**

- **`[WF-3]` (cross-page).** View Orders State 3 legend #4 still carries the "(proposal)" qualifier on "Cancel Inbound disabled after Outbound". That rule is adopted `[PD-10 · OWNER-PENDING]` and **binds Order Detail too** — see `[BR-14]`. Spec and QA use the adopted rule; the "proposal" wording is stale text and must not be specced.
- **`[OD-WFX-1 · proposed]` (this page, registered 2026-08-03).** The Change Status dropdown **does not close on an outside click**: `order-detail/index.html` has no document-level click handler (the modal has one — `overlay.addEventListener('click', …)` — the dropdown does not). The specified behavior is unchanged and correct: clicking elsewhere closes the dropdown with no status change `[L-8]` step 1 `[E-46]` `NE-2`. Until the drawing is patched, the assertion is not runnable against the wireframe, so `QA-STA-4` is tagged `[ADMIN]` — **this is a missing wireframe affordance, not a spec change and not a bug to file against the spec**. Backlog entry in §9.5; register entry in `_wireframe-fixes.md` §I.

No other `_wireframe-fixes` entry (WF-1, WF-2, WF-4 … WF-14) targets `wms2/order-detail/index.html`.

**B. Demo-data artifacts — illustrative, not behavioral (do not derive rules, do not file bugs)**

The wireframe's Actor Log is a **grammar sample**, assembled to show every row type at once. It is deliberately not a consistent order history. Three specific inconsistencies exist and an AI QA agent will find all three:

1. **State 1 shows an `OUTBOUND · All (4 SKU)` row (`07-01 09:32`) while the status badge reads `Processing` and `📦 Outbound` is still enabled.** A real order in that condition would be `prepare-shipment` with Outbound already spent and replaced by `Cancel Outbound` `[BR-19]`.
2. **State 1's oldest row is `CANCEL INBOUND (Restock)` for SKU `100005104` (`06-30 20:15`) with no later `INBOUND` row for that SKU**, yet the row renders `INBOUNDED`.
3. **State 2 renders the identical Actor Log**, including the `OUTBOUND · All (4 SKU)` row, while row 2 (SKU `100043697`) is `PENDING` and `📦 Outbound` is disabled.

The binding rules are `[BR-1]`, `[BR-19]`, `[E-66]` and `[L-3]`'s row grammar. QA asserts the Actor Log's **columns, row grammar, ordering and colour classes** (`QA-REN-8`), never its consistency with the line-item states. Not currently registered in `_wireframe-fixes`; candidate for a demo-data correction in the wireframe-edit pass (§9.5).

**C. Planning-document correction made by this spec**

Both planning lenses describe a "20-column" line-items table. The wireframe renders **18 columns**: 3 fixed (select-all checkbox · `SKU` · `Image`) + 6 `Product Information (WooCommerce)` + 8 `Inventory` + 1 `Actions`. Verified against the header markup (three `rowspan="2"` cells + `colspan="6"` + `colspan="8"` + one `rowspan="2"` Actions cell). This spec states **18** everywhere and expresses the `DC-15` snapshot requirement as "every field of the line record", which is the durable form `[BR-42]`.

**D. Wireframe demo limitations that are NOT defects** (QA tags these `[ADMIN]`, never files bugs)

Order Detail's wireframe has no server and therefore: no toast implementation, no Web Audio, no working handler on the status-dropdown items, `Mark all read`, per-row `Inbound` / `Cancel Inbound`, `Bulk Inbound Selected Items`, `📦 Outbound`, `🖨 Print`, `View Label`, `✓` / `✕` row save-cancel, `Today`, `M3 Delete`, `+ Add Line Item`, or any subbar button. Everything below the render layer is `[ADMIN]`-tier.

**E. Adjudicated non-issues — do not "fix"**

- **Deleo Tracking No. is absent from View Orders but present on Order Detail.** Deliberate asymmetry (2026-07-21, restated 2026-07-22), recorded in `_review.md` §1 as an adjudicated non-issue and here as `[BR-9]`.
- **Row 1 is pre-rendered in edit mode in both states.** It is the worked example for `[L-12]`, not a stuck row.
- **The wf-bar, legend, purple dots and `#annoToggle`** are wireframe chrome. They do not exist in the production admin `NE-13`.

### 2.6 Cross-page adjudications that bind this page `[C-n]`

`_review.md` §1 adjudicated twelve conflicts. Six bind Order Detail; the rest resolve on other pages. Recorded so a reviewer can tick them without re-reading the review.

| ID | Adjudication | How this spec honors it |
|---|---|---|
| **`[C-2]`** | Comment-mention channel is **#fulfillment-admin-comments** (`C0BMGEWM5QA`), CONFIRMED 2026-08-03 — the routing file beats the "pending" draft wording | §6.1 rows 1–2 name the channel and ID; "pending" is never written for this row `[BR-11]` §10.3 chain 4 |
| **`[C-3]`** | Order-facing sourcing badges stay at **4**; `OTHER (channel)` is an **inbound-origin** route only | `[L-4]` states `OTHER` does not appear on Order Detail line items, and that adding it would be a change to `[G-5]`, not to this page `[PD-80 · OWNER-PENDING]` |
| **`[C-5]`** | Send-sound scope = every outbound-class button on every page, including Order Detail's Outbound | `[L-9]` step 2, `[BR-29]` `[PD-2 · OWNER-PENDING]` |
| **`[C-6]`** | `[G-2]` beats wireframe omissions — removals get confirm + toast even where the wireframe is silent | `[BR-39]`; applied to Cancel Inbound, Cancel Outbound, M3 Delete, Cancel Order, Reset, Clone `[PD-5 · OWNER-PENDING]` |
| **`[C-7]`** | Auto-outbound on full inbound is a **View Orders scan/bulk behavior only**; Order Detail is always manual | `[L-9]`, `[BR-5]`, `[E-12]`, `QA-OUT-6` `[PD-21 · OWNER-PENDING]` |
| **`[C-12]`** | One canonical name per shared cross-page event | §5 naming paragraph; `comment.*`, `order.status_changed`, `order.outbounded`, `print.job_result` are byte-identical to `_global-rules` |

Not binding here: `[C-1]` (carrier auto-record — View Orders / Inbound Request), `[C-4]` and `[C-10]` (Closing), `[C-8]` and `[C-9]` (RTO), `[C-11]` (G-11 reason enum — View Orders M6 / Inbound Request).

### 2.7 Open cross-page conflicts that touch this page `[X-n]` (2026-08-03)

The 2026-08-03 cross-page consistency pass (`_verify/m3a-cross-page.md`) found **nine** disagreements between this spec and another screen's spec. **None is a defect in this page's behavior** — in every row this spec's position is either the one the global rule supports or the one that cannot be changed without editing the wireframe (SST). They are recorded here so a reader who finds the other spec's sentence does not "harmonize" this page by hand, and so the owner has one list to adjudicate. Each row names where this page states its position and what would have to change if the owner rules the other way.

| ID | Conflict | This page's position (and where) | Resolution owner / what changes if reversed |
|---|---|---|---|
| **`[X-1]`** | **Cancel Inbound contract.** View Orders M1 and Inventory M4 expose a restock Yes/No + an editable Restock Qty; this page has neither and hard-codes `restock=true` on the full line qty. | `[L-2]` Cancel Inbound + `[BR-49]` + `DC-11` | Cross-page. If the owner adopts the M1/M4 form here, `[L-2]` gains the two controls and `DC-11` gains `restock` (bool) + `restock_qty`; `[BR-49]` is deleted. Nothing else on this page moves. |
| **`[X-2]`** | **Outbound gate scope.** Closing `[L-M1]` emits the canonical `order.outbounded` behind a Zero-Packing gate that does **not** require every line `INBOUNDED`. | `[L-9]` enable predicate + `[BR-1]` — scoped to **this page's control**, see the note under the predicate | Closing owns the reconciliation. If the owner rules the gate is system-wide, Closing adds the predicate; this page is unchanged. |
| **`[X-3]`** | **`Cancelled` as a status value.** Closing renders `Cancelled` in an `Order Status` column; the 8-status vocabulary has no such value. | `[L-8]` + `[BR-12]` — cancellation is a **flag**, not a ninth status | Cross-page. If the owner makes it a status, `[L-8]`'s list becomes 9 values and `[BR-12]` is amended; `✕ Cancel Order` `[L-F5]` would then be a status pick. |
| **`[X-4]`** | **`OUTBOUNDED` line status.** RTO's Bulk Outbound writes each line `INBOUNDED → OUTBOUNDED`; this page's rendering contract is exhaustive at two values. | `[L-10]` `Inbound Status` + `[BR-50]` | Cross-page. If line-level outbound is adopted, `[L-10]` gains the third tag, `[BR-50]` is deleted, and Cancel Outbound `[BR-19]` must specify `OUTBOUNDED → INBOUNDED`. |
| **`[X-5]`** | **`OTHER (channel)` badge.** RTO §1.4/§4.2 states OTHER renders on Order Detail; this page states it never does. `[G-5]` supports this page. | `[L-4]` + `[C-3]` `[PD-80 · OWNER-PENDING]` | `[G-5]` amendment. If OTHER becomes order-facing, `[L-4]` and `QA-REN-5` change together. |
| **`[X-6]`** | **Comments-hub copy.** Six hub strings are not byte-identical across the eight specs; this page is the outlier on one of them (`Unstar to remove`). | `[L-7]` — the strings specified here are the **shipped wireframe strings**, asserted byte-exactly by `QA-HUB-1`/`QA-HUB-3` | `[G-7]` amendment + a wireframe edit. **Not changed unilaterally here**: rewriting the string in the spec alone would make a `[WF]` assertion fail against the SST wireframe. |
| **`[X-7]`** | **`@mention` Slack fan-out.** RTO §3.9 sends one message naming every mentioned user; this page sends one per distinct mention. `[G-7]`'s singular payload field supports this page. | `[L-1]` step 7 + §6.1 + `[E-80]` + `DC-27` | `[G-7]` amendment. If fan-out is collapsed, `DC-27` becomes one row per comment instead of one per target user. |
| **`[X-8]`** | **Shared-concept event names.** Five cross-page concepts carry a different name per page (idempotency suppression, stock movement, comment search, Slack dispatch outcome, line inbound). The **10 canonical names are byte-identical everywhere** `[C-12]`; this is the tier below them. | §5 Naming paragraph + `DC-36` / `DC-21` / `NE-8` / `DC-27` / `DC-10` | `_global-rules` promotion. Renaming a page-scoped event is a find-and-replace here; `NE-8` (comment search declared a **non**-event while three pages persist it) is the only row that is a `[G-8]` disagreement rather than a naming one. |
| **`[X-9]`** | **Order-status casing.** Closing renders `Prepare Shipment` / `On Hold` / `Processing` (title case, spaces) where this page and View Orders use `prepare-shipment` / `on-hold` / `processing` as the vocabulary. No spec previously said which register is the value and which the label. | `[L-8]` "Value vs label" — the 8 lowercase-hyphenated strings are the **values**; the badge renders a title-cased **label** of the same value, with the mapping given | Corpus-wide. This page now states the mapping; if `_global-rules` states it instead, `[L-8]`'s paragraph becomes a citation. No behavior changes either way. |

---

## 3. Functional Specification

### 3.0.1 Cross-cutting contracts (page deltas — the rule bodies live in `_global-rules`)

| Global rule | Page delta on Order Detail |
|---|---|
| `[G-1]` Scanner protocol | **Does not apply.** No scan surface exists here and none may be added `[BR-30]`. |
| `[G-2]` No refresh + confirmation toast | This page has **no** refresh exception of any kind, and its success strings are fixed in §3.0.2 so they are byte-assertable. Removals and deletions count as confirming actions — `[GD-5]`, i.e. the 2026-08-03 amendment to `[G-2]` recorded in `_review.md` §4, which reads *"removal/deletion confirmations count as confirming actions"* `[PD-5 · OWNER-PENDING]`. |
| `[G-3]` Audio | Only (a) applies, on `📦 Outbound` `[PD-2 · OWNER-PENDING]`. (b) TTS and (c) the wrong-product warning tone have no analogue here and must not be implemented `[BR-29]`. This is **page behavior**, not a cross-reference: the trigger, the once-per-commit rule and the "sound is never proof" limit are all specified in `[L-9]` and asserted by `QA-OUT-4` / `QA-OUT-5`. |
| `[G-4]` Instant printing | Print surfaces on this page: `🖨 Print` only. `View Label` is a preview, not a print surface. Failure copy is fixed in §3.0.2. |
| `[G-5]` Sourcing routes | Order-facing badge set only (4). `OTHER (channel)` never renders on this page `[C-3]`. |
| `[G-6]` Product naming | This is the only screen showing EN **and** KR names side by side, so brand-bold applies to both columns `[L-11]`. |
| `[G-7]` Comments | Order Detail is the primary per-order comment surface and hosts the shared hub `[L-1]` `[L-7]`. |
| `[G-8]` Data capture | §5. Page delta: blocked attempts also persist (`DC-9`), and suppressed duplicates persist (`DC-36`). |
| `[G-9]` Idempotency | Applies to every mutating control listed in §3.0.2. Page delta: the suppression is itself an event, so the fix is provable `[BR-32]`. |
| `[G-12]` Deep links | §6.2. Page delta: arrival path is persisted (`DC-34`). |
| `[G-13]` Sample assignment | Display only; no assignment UI here `[L-10]` `[PD-27 · OWNER-PENDING]`. |
| `[G-15]` Permissions | No control on this page is role-gated in v1 `[PD-1 · OWNER-PENDING]`. |

Additional cross-cutting behavior that is **not** in any global rule:

- **Server revalidation at confirm.** On a mismatch the server rejects with a red toast, re-renders the affected row or block, and writes no partial state `[PD-6 · OWNER-PENDING]`. Concurrent edits use an optimistic version check → 409 → reload the row + non-green toast `[PD-7 · OWNER-PENDING]` `[BR-37]`.
- **Slack is a side effect, never part of the transaction** `[PD-4 · OWNER-PENDING]` `[BR-38]`.
- **Every guard that disables a control renders its reason next to the control**, not only in a tooltip `[BR-46]`. A disabled control that does not say why generates support tickets against working logic — that is the lesson `[BR-3]` was written from.
- **Every blocked attempt persists `DC-9`** with a `reason_code` `[BR-47]`. Guards are measured, not silent.

**Two notation notes, so a mechanical audit does not read them as gaps:**

- **Sub-rule citation form.** This spec writes `` `[G-3]`(a) `` / `(b)` / `(c)`, matching `_global-rules`' own labelling of the sub-rules. Three other specs write `[G-3a]`. Both forms are in use corpus-wide; no binding source picks one, so a corpus-wide `[G-n]` grep must accept both until `_review.md` §3 fixes a convention.
- **`_review.md` §2b codes this page's audio row `Δ` (cross-reference only). That coding is stale** — the send-sound contract is specified here as page behavior with its own QA scenario, so the correct code is `Y` (`_verify/m3b-review-audit.md` §6.4). Nothing in this spec changes; the matrix is what is wrong.

### 3.0.2 Toast-string registry (normative content; one vocabulary for the whole page)

Green = success, red = failure `[G-2]`. Braces are runtime substitutions. Duration, stacking and the generic failure wording are dev-time (§9.4 D-2), but these success strings are the assertable contract.

| Control | Success toast | Named failure toast |
|---|---|---|
| `[L-2]` per-row **Inbound** | `Inbounded — {SKU}` | red, names the rejection reason |
| `[L-2]` **Cancel Inbound** | `Inbound cancelled — {SKU} restocked` | red |
| `[L-2]` **Bulk Inbound Selected Items** | `Inbounded {n} item(s) · {m} already inbounded` | red |
| `[L-9]` **📦 Outbound** | `Outbound sent — {n} item(s)` | red, names the failing line or status |
| `[L-9]` **Cancel Outbound** | `Outbound cancelled` | red |
| `[L-8]` status pick | `Status changed to {status}` | red |
| `[L-5]` PIC | `PIC changed to {name}` | red |
| `[L-12]` `✓` Save | `Line item updated` | non-green: `Line changed by {user} — reloaded` `[E-21]` |
| `[L-M3]` Delete | `Line item deleted` | red |
| `[L-F14]` + Add Line Item | `Line item added` | red |
| `[L-1]` Add Comment | `Comment added` | red |
| `[L-13]` 🖨 Print | `Label sent to printer` | `Print agent unreachable — label not printed` |
| `[L-F10]` ✎ Change Tracking # | `Tracking number updated` | red |
| `[L-F9]` address ✎ | `Billing address updated` / `Shipping address updated` | inline field error, no toast `[E-54]` |
| `[L-F4]` ⧉ Clone Order | `Order cloned — {new order no.}` (with a link) | red |
| `[L-F5]` ✕ Cancel Order | `Order cancelled` | red, or the guard message `Cancel Inbound (restock) on {n} line(s) first` |
| `[L-F11]` Reset Order | `Order reset — shipment data cleared` | red |

### 3.0.3 Timestamp and timezone rendering contract `[BR-43]`

One page shows four different time formats. That is **as-live and deliberate**; harmonizing them would break parity with the admin the team already reads. The contract fixes which format belongs where, so nobody "cleans it up" and nobody guesses a timezone.

| Block | Format | Zone | Source |
|---|---|---|---|
| `[L-F8]` `Order Date` | `YYYY-MM-DD SGT` (`2026-06-30 SGT`) | SGT, printed | WooCommerce |
| `[L-F8]` `Order Created At` | `DD/MM/YYYY HH:mm:ss SGT` (`30/06/2026 19:55:28 SGT`) | SGT, printed | WooCommerce |
| `[L-3]` Actor Log `Time` | `MM-DD HH:mm` (`07-01 09:32`), year omitted | **warehouse local (SGT)**, not printed | persisted event |
| `[L-1]` comment `time` | `MM-DD HH:mm`; `Just now` for an in-session append | warehouse local | persisted event |
| `[L-7]` hub item `time` | relative (`10:42`, `Yesterday`) | warehouse local | persisted event |
| `[L-F12]` SHIPMENT DETAILS `Created At` / `Updated At` | `M/D/YYYY, h:mm:ss AM/PM` | carrier feed locale | carrier |
| `[L-6]` TRACKING HISTORY | two explicit columns, `Time (local)` and `UTC` | both, labelled | carrier |
| `[L-6]` sync marker | `(synced M/D/YYYY, h:mm:ss AM/PM)` | carrier feed locale | `DC-23` |

**Invariant:** every persisted event stores UTC **and** the display timezone (§5 envelope). The UI never infers a zone from the browser, and a rendered time that omits its zone (Actor Log, comments) is warehouse local by definition, never browser local. An operator in another timezone sees warehouse time `[E-89]`.

---

### `[L-1]` Operator Comments (per-order thread)

**Surface.** Section header `💬 Operator Comments` with a `Hide Comments` button `[L-F16]`. Two-column layout: the thread on the left (`.cmt-list`), the composer on the right (`.cmt-new`).

**Thread rendering.** Newest at the bottom (append order — the wireframe appends with `list.appendChild`). Each entry (`.c-item`): author name (`.who`, bold), body with `@name` tokens in `span.at` (blue bold), timestamp (`<time>`), and a `★` toggle (`.star`, gaining class `on` when saved). Seed entries in the wireframe:
- `Dean` — `@Yongwon Please pack this order with extra care — repeat-purchase VIP customer.` — `07-13 10:42`
- `Yongwon` — `@Dean Got it. I'll add extra bubble wrap.` — `07-13 10:55` (starred)

**Composer.** A `textarea` with placeholder exactly:
`Write a comment — @name to notify via Slack (order no. · text · time · author included). Per-order history accumulates here.`
and a primary button labelled exactly **`Add Comment`** (`#addCmt` in State 1, `#addCmtH` in State 2).

**Trigger → behavior.**
1. Operator types text; `@` opens a user autocomplete against system users (autocomplete presence and debounce are dev-time; the parse contract is not).
2. Click **Add Comment** (or the dev-chosen keyboard shortcut).
3. **Validation:** if the trimmed value is empty, the action is a no-op — no server call, no event, no toast `[E-27]`. The button is not disabled; the guard is on submit. (The wireframe already implements this: `const txt=(ta.value||'').trim(); if(!txt) return;`)
4. **Server action:** persist `DC-26 comment.posted` with order id, raw body, parsed `mentions[]`, author, timestamp.
5. The new comment appends to the thread immediately, without a page refresh; the composer clears.
6. Green toast: `Comment added`.
7. For each **distinct** resolved mention, dispatch one Slack message `[G-7]` and persist `DC-27 comment.mention_notified` with the delivery result. Mentioning the same user twice in one body produces **one** message, not two `[E-80]`. Dispatch is asynchronous to the commit.
8. A mention token that does not resolve to a system user posts as **plain text** — stored in the body, absent from `mentions[]`, recorded in `unresolved_mention_tokens[]`, no Slack message `[E-28]`.
9. Self-mention (author == mentioned user) posts normally but suppresses the dispatch — no self-notification, recorded as `DC-27.suppressed_reason=self_mention`. **By analogy with `[PD-16 · OWNER-PENDING]`, which decides only the match-pipeline auto-comment (resolver == registrant); no owner decision exists for a human `@self` in a free-text comment.** Suppression is therefore the **dev default**, recorded in §9.4 D-19, not a registered provisional decision `[E-60]`.
10. A body consisting of nothing but a resolved `@mention` is valid and posts normally — the mention *is* the message ("@Dean" = "look at this order") `[E-81]`.

**Comments are append-only.** There is no edit control and no delete control, and none may be added. Corrections are posted as new comments. The corpus is a deliberate AI-training and audit asset `[G-7]` `[PD-3 · OWNER-PENDING]` `[BR-11]`.

**Escaping.** Comment bodies are untrusted input. HTML and script characters are escaped on render (`&`, `<`, `>`, `"`) in the thread, in the hub list and in hub search results `[E-30]`. Storage is verbatim; escaping is a render concern.

**Commentability is not gated by order state.** A cancelled, completed or outbounded order still accepts comments — the thread is the audit conversation, and the moment people most need to write on an order is after something went wrong `[E-79]`.

**★ Star.** Toggling writes `DC-28 comment.starred` / `DC-29 comment.unstarred` — **per-user** state, not order state. The starred comment appears in the hub's `★ Saved` tab `[L-7]`.

**System comments.** Comments arriving from another screen's pipeline (unrecognized-match confirmation) render in this same thread and persist with `source=system` (`DC-32 comment.auto_posted`) so the human/system split survives into the corpus. They are visually distinguishable from human comments (rendering treatment is a dev decision; the persisted flag is not) `[BR-35]`.

**`[L-F16]` Hide Comments** collapses the section. Client-local view state — explicit non-event `NE-3`.

---

### `[L-2]` Inbound controls — per-row Inbound / Cancel Inbound + Bulk Inbound Selected Items

The 2026-07-14 rework retired the name **"Request Inbound"** and replaced one order-level control with the View Orders grammar: **inbound is per product, outbound is per order** `[BR-4]`.

**Per-row control (Actions cell, far right of the 1680px table).** Exactly one of two buttons renders per line, driven by that line's inbound status:

| Line status | Button label | Class in wireframe | Effect |
|---|---|---|---|
| `PENDING` | **`Inbound`** (green solid) | `.btn.btn-green.btn-sm` | PENDING → INBOUNDED |
| `INBOUNDED` | **`Cancel Inbound`** (red outline) | `.btn.btn-red-line.btn-sm` | INBOUNDED → PENDING + restock |

A row in edit mode (`tr.row-edit`) shows neither: its Actions cell holds `✓` and `✕` only `[L-12]`.

**Per-line inbound is all-or-nothing.** There is **no quantity input** on this page. Clicking `Inbound` receives the line's full ordered quantity. A line of qty 5 of which 3 arrived is **not** an Order Detail operation — partial receipt against an expected quantity is View Orders State 6 / the inbound-request lifecycle `[G-10]` `[G-11]`, which owns the PARTIAL state, the remaining-quantity arithmetic and the expected-qty edit with its mandatory reason. Adding a quantity field here would create a second partial-receipt path that diverges from the request reconciliation `[BR-41]` `[E-71]`.

**Inbound — trigger → behavior.**
1. Click **Inbound** on the row.
2. Server revalidates that the line is still `PENDING`, still exists, and the order is not cancelled. Stale row → reject, re-render the row as `INBOUNDED`, non-green toast `[E-9]` `[PD-6 · OWNER-PENDING]`.
3. Persist `DC-10 line_item.inbounded` (SKU, qty, PENDING→INBOUNDED, actor, ts) **and** the inventory ledger row `DC-21 inventory.movement`.
4. Row re-renders: status tag `PENDING` → `INBOUNDED`, button `Inbound` → `Cancel Inbound`. No page refresh.
5. `Latest Inventory Count` for that SKU refreshes from Inventory in the same response `[E-90]`.
6. Green toast: `Inbounded — {SKU}`.
7. The Actor Log gains an `INBOUND` row `[L-3]`.
8. **Inbound is allowed while the order is On Hold** `[BR-2]`.
9. **No auto-outbound.** Reaching full inbound on this page never triggers Outbound; the Outbound button merely becomes enabled `[PD-21 · OWNER-PENDING]` `[BR-5]` `[C-7]`.

**Cancel Inbound — trigger → behavior.**
1. Click **Cancel Inbound**.
2. Confirm step (destructive action) `[PD-5 · OWNER-PENDING]`, with an **optional free-text note**. The Actor Log's Note column exists for it (demo value: `Corrected duplicate inbound`). An empty note is valid `[E-15]`.
3. **Guard:** once the order has been outbounded, per-row Cancel Inbound renders **disabled** with the reason `Cancel Outbound first`. Cancel Outbound must run before any individual inbound can be reversed `[PD-10 · OWNER-PENDING]` `[BR-14]` `[E-10]` `[WF-3]`.
4. Persist `DC-11 line_item.inbound_cancelled` (SKU, qty, INBOUNDED→PENDING, `restock=true`, note, actor, ts) + `DC-21` with the positive restock delta.
5. Row re-renders to `PENDING` + `Inbound`. Green toast: `Inbound cancelled — {SKU} restocked`.
6. The Actor Log gains a row rendered exactly `CANCEL INBOUND (Restock)`.
7. **Cross-page integrity:** Inventory's M4 release path can also reverse a reservation `[PD-45 · OWNER-PENDING]`. Both paths write `DC-21`; the server must ensure one line's receipt is reversed **once** — the second attempt is a stale-entity rejection `[PD-6 · OWNER-PENDING]`, not a second movement.

**Cancel Inbound on this page always restocks the full line quantity** `[BR-49]` `[X-1]`. There is **no restock Yes/No choice and no Restock Qty input** on Order Detail — the symmetric counterpart of "per-line inbound is all-or-nothing" `[BR-41]`: a receipt taken in full is reversed in full. The partial reversal cases — restock **less** than was received (partial damage), or decline the restock entirely — are **View Orders `[L-M1]`** and **Inventory `[L-M4]`** operations, which own the Yes/No radio, the editable quantity and the remainder accounting. Adding those controls here would create a second, unreconciled partial-restock path, exactly as a quantity field on inbound would create a second partial-receipt path. `DC-11` therefore always carries `restock=true` and the full line qty; a developer implementing the M1/M4 form on this page is implementing a different rule.

**Bulk Inbound Selected Items (footer).** Label exactly **`Bulk Inbound Selected Items`**, green outline (`.btn.btn-green-line.btn-sm`), positioned in `.li-foot` immediately left of **📦 Outbound**.
1. **Enabled only when ≥1 line checkbox is checked.** With zero selected it renders disabled — not an error toast `[E-7]`.
2. Click → server processes the selected set as one submission.
3. Lines already `INBOUNDED` in the selection are **skipped idempotently**, not failed. One toast reports both numbers: `Inbounded {n} item(s) · {m} already inbounded` `[E-8]`.
4. Persist one parent `DC-12 line_item.bulk_inbound_submitted` (selection set, counts, skipped ids) **plus one child `DC-10` per SKU actually transitioned**, plus `DC-21` per movement. The parent proves the operator's intent; the children are what Inventory reads.
5. All affected rows re-render in place. No refresh. One toast for the batch, never one per line.
6. Double-click processes the selection exactly once `[G-9]` `[E-3]`.
7. **A line deleted by another operator between selection and submit** is skipped and reported in the same toast subtext; it does not fail the batch `[E-72]`.
8. **If the server cannot commit part of the batch**, the committed children stand, the failures are named in a red toast, and `DC-12` records both sets. A batch is not atomic — refusing the whole batch because one line moved would strand the other nine `[E-73]`.

**Checkbox selection** (`[L-F13]`) is ephemeral client state — explicit non-event `NE-1`.

---

### `[L-3]` Inbound / Outbound Actor Log

**Surface.** Bottom of the order (`.logsec`), heading `Inbound / Outbound Actor Log` followed by a grey `— New` marker. Table (`.logtbl`) columns, in order: **Time · Action · SKU · Qty · Operator · Note**.

**This log is a view over persisted events, never a separate store** `[G-8]` `[BR-36]`. It is a query over `DC-10`, `DC-11`, `DC-12`, `DC-19`, `DC-20`. If the log and the event store ever disagree, the event store is ground truth.

**Row grammar (exact strings).**

| Source event | Action cell | SKU cell | Qty cell | Colour class |
|---|---|---|---|---|
| `DC-10` line inbound | `INBOUND` | the SKU | line qty | `.act-in` (green) |
| `DC-11` cancel inbound | `CANCEL INBOUND (Restock)` | the SKU | restocked qty | `.act-cancel` (red) |
| `DC-19` order outbound | `OUTBOUND` | `All ({n} SKU)` | total units | `.act-out` (blue) |
| `DC-20` cancel outbound | `CANCEL OUTBOUND` | `All ({n} SKU)` | total units | `.act-cancel` (red) |

`DC-12` (bulk submission) does not get its own row; its children render as individual `INBOUND` rows, which is what the operator needs to see. The parent event remains queryable.

**Ordering.** Newest first. Wireframe demo rows, newest→oldest: `07-01 09:32 OUTBOUND All (4 SKU) 4 Dean –` · `07-01 09:10 INBOUND 100012534 1 Miranti –` · `07-01 08:58 INBOUND 100043697 1 Miranti –` · `06-30 20:15 CANCEL INBOUND (Restock) 100005104 1 Dean Corrected duplicate inbound`. (These rows are a grammar sample, not a consistent history — §2.5 B.)

**Time format** is `MM-DD HH:mm` in warehouse local time §3.0.3. The full timestamp lives on the event and in the export.

**Operator column** renders the actor's display name at the time of the event, resolved from the persisted `actor` id. A user removed from the directory afterwards still renders their historical name — never `Unknown`, never blank `[E-88]`.

**Empty state.** A new order with no inbound/outbound history still renders the section, the heading and the header row, with a single empty-state row (`No inbound or outbound activity yet`) `[E-42]`. The section is never hidden — its absence would read as "the feature is missing".

**Note column.** Free text, `–` when absent. Capture is required; content is optional.

**Truncation.** Where a display cap applies, it is explicit (`showing latest {N}`) and the full history is reachable through `↻ Audit History` `[L-F2]`. Silent truncation is forbidden `[E-65]`. Pagination mechanics are dev-time (§9.4 D-7).

---

### `[L-4]` Line Items — sourcing routes, JIT channel, linked purchase Order Number

**Route rendering.** The **Sourcing Route** column renders one of the four order-facing route labels as colorless black bold text `[G-5]`:
`SMART BUY` · `JIT ({channel})` · `WHOLESALE` · `PARTNERSHIP`.

- JIT always carries the purchase channel in parentheses: `JIT (Coupang)`, `JIT (Naver)`, `JIT (Other retail)`. The channel is the value the handler picked from the dropdown at purchase time; it is provenance, not a category `[BR-6]`.
- JIT semantics: **the item was purchased after the customer's order was placed.** That is why JIT lines show `Latest Inventory Count = 0` — no warehouse stock backs them `[BR-7]`.
- The wireframe implements the colorlessness in CSS: `.tag-smartbuy,.tag-jit,.tag-wholesale,.tag-partnership{background:transparent;color:var(--ink);padding:0}` (`var(--ink)` = `#14101B` = `rgb(20, 16, 27)`).
- **`OTHER ({channel})` does not appear on Order Detail line items.** OTHER is an *inbound-origin* route offered by the Inbound Request form; the order-facing badge set stays at four `[G-5]` `[C-3]` `[PD-80 · OWNER-PENDING]`. If a future order-side consumer needs it, that is a change to `[G-5]`, not to this page. **Cross-page note:** RTO's §1.4 and §4.2 assert the opposite — that OTHER renders on Order Detail. `[G-5]`'s "order-facing badges (4)" clause supports this page; the disagreement is open as `[X-5]` and is not a licence to add a fifth badge here.

**Order Number column.** The **per-product purchase order number** (e.g. Coupang order `12101316464794`), not the SkinSeoul order number and not a shipment identifier. It renders as a link for lookup; clicking opens the purchase-side lookup in a new tab and persists `DC-33 order.external_link_opened` with `target=order_number_lookup`. When absent (WHOLESALE, PARTNERSHIP lines) it renders `–` and is not a link `[E-44]` `[E-59]`.

**Tracking-number disambiguation (mandatory — prevents a real conceptual collision).** Two different tracking numbers appear on this page and they belong to different namespaces `[PD-8 · OWNER-PENDING]`:

| Where | What it is | Direction | Example in wireframe |
|---|---|---|---|
| Line Items → `Tracking Number` (Inventory group) | the **purchase/inbound** parcel from the retailer or supplier to the warehouse | supplier → warehouse | `10323100835456` |
| Fulfillment Tracking → `Tracking Number` | the **outbound carrier** parcel to the customer | warehouse → customer | `34YEM055929401000910906` |

They may legally coincide; they never resolve to the same screen. Labels, exports and API field names must keep them distinct.

**CP Link column.** The Coupang product URL for that line. Renders as a shortened link (`coupang…7923`); click opens the external URL in a new tab and persists `DC-33` with `target=cp_link`. Absent → `–`, not a link.

---

### `[L-5]` PIC field with explicit "✎ Edit" button

**Surface.** In 📋 Order Information: label `PIC`, current value (`Egita`), and a bordered button labelled exactly **`✎ Edit`**. The bare pencil glyph it replaced must **not** exist as the PIC control anywhere on this page (2026-07-21).

**Trigger → behavior.**
1. Click **✎ Edit** → a **system-user picker** opens (not a free-text field). PIC feeds order filters and mention routing, so it must resolve to a real user `[PD-33 · OWNER-PENDING]` `[BR-23]`.
2. Pick a user → Save.
3. Persist `DC-6 order.pic_changed` with `old_pic → new_pic`, actor, ts.
4. Value updates in place; green toast `PIC changed to {name}`. No refresh.
5. **No automatic Slack notification** to the new PIC. Notifying every reassignment would be noise; to notify, post an `@mention` comment `[PD-33 · OWNER-PENDING]`.
6. Selecting the same user is a no-op — no event, no toast.
7. A deactivated user is not selectable. If the currently stored PIC was deactivated after assignment, the value still renders (historical truth) with a muted `(inactive)` marker `[E-53]`.

---

### `[L-6]` Fulfillment Tracking + TRACKING HISTORY

**Declared unchanged from the live admin.** No behavior is redesigned here; this entry exists so developers do not "improve" a screen that ships as-is, and so QA knows what is intentionally identical.

**SHIPMENT DETAILS** (`[L-F12]`) — columns exactly: `Provider Order ID` · `Tracking Number` · `Status` · `Status Description` · `Created At` · `Updated At`. Wireframe row: `YT2618100709331860` / `34YEM055929401000910906` / `DELIVERED` / `Shipment information received` / `6/30/2026, 8:55:53 PM` / `7/13/2026, 10:10:32 AM`. Below it, the last-mile chip: `Last mile: AustraliaPost`.

**TRACKING HISTORY** — header renders the sync timestamp: `TRACKING HISTORY (synced 7/16/2026, 4:51:40 AM)`. Scrollable table (`.trackscroll`) with columns `Time (local)` · `Node` · `Description` · `Location` · `UTC`. Node values render as chips (`.node`): `DELIVERED`, `DELIVERY_ATTEMPT`, `IN_TRANSIT_CARRIER`, `ORDER_CREATION`.

**Wireframe abbreviation is deliberate:** the wireframe shows 4 representative events; **the real screen lists every event down to `ORDER_CREATION`** and must not be truncated in implementation.

**Sync is a silent system event.** Each carrier sync persists `DC-23 shipment.tracking_synced` with `actor=system`, the sync timestamp, the appended event set and a result. The displayed `(synced …)` value reads from that event. A **failed** sync leaves the last successful timestamp visible and persists its failure result; it never blanks the table and never shows a fabricated time `[E-43]`.

**Empty states.** A pre-shipment order renders both blocks with explicit empty states (`No shipment yet` / `No tracking events yet`), never a collapsed or missing section, and omits the `(synced …)` marker entirely rather than printing a fake time `[E-43]`.

---

### `[L-7]` Comments hub (top-right, shared across all screens)

**Surface.** Nav button **`💬 Comments`** (`.icon-btn`) with a red unread badge (`.badge-n`, wireframe: `2`). Clicking toggles the dropdown (`#inbox1` in State 1, `#inbox1H` in State 2) by adding/removing class `open`.

**Structure, top to bottom:**
1. **Search box** (`.csearch input`) — placeholder exactly `🔍 Search all comments — order no. · author · text`.
2. **Tab bar** (`.tabs`) — `@ Mentions` (with its own count badge, wireframe `2`) and `★ Saved`; the active tab carries class `on`.
3. **Pane header** (`.paneheader`) — Mentions: `Comments mentioning me · Click to open the order` + a `Mark all read` action. Saved: `Saved comments · Click to open the order` + `Unstar to remove`.
4. **Items** (`.it`) — `Order {no} · {author}: "{text}"` + relative time + `★` toggle. Unread items carry class `unread` (blue tint).

**Hub copy is the shipped wireframe copy, and it is not yet byte-identical across the eight screens** `[X-6]`. The strings above (`Comments mentioning me · Click to open the order`, `Saved comments · Click to open the order`, `Unstar to remove`, `Mark all read`, `{n} results · newest first · click to open the order`, `No matching comments`) are what `order-detail/index.html` renders today, and `QA-HUB-1`/`QA-HUB-3`/`QA-HUB-4` assert them byte-exactly against the wireframe as SST. Four of the six already match the corpus majority; `Unstar to remove` is this page's outlier against a proposed canonical `Unstar to remove from the list`. **Harmonizing is a `[G-7]` amendment plus a wireframe edit, executed together** — changing the string in this spec alone would make a `[WF]` assertion fail against a correct drawing, so it is deliberately not done here.

**Badge semantics.** The nav badge equals the number of **unread mentions for the current user** — not unread comments, not all comments `[BR-44]`. With zero unread mentions the badge is absent (not `0`), and the Mentions pane renders its own empty state `[E-92]`.

**Search behavior (all-orders, not a tab filter).**
- Scope: **every comment on every order**, regardless of mention or star state.
- On non-empty input: the tab bar hides, all tab panes hide, and a results pane renders with the header `{n} results · newest first · click to open the order`, sorted newest first, with the matched substring wrapped in `<mark>`.
- Zero matches render exactly `No matching comments` `[E-31]`.
- Clearing the input restores the tab bar with the **previously active tab still active** and its pane visible `[E-32]`.
- Result text is HTML-escaped **before** highlighting `[E-30]`.
- Search is a read action — explicit non-event `NE-8`. If search telemetry is ever wanted it is a **new** event, not a silent change to this one.

**Clicking an item opens the entity** `[G-12]`:
- comment on an order → that order's Order Detail page;
- comment on an **unrecognized-pool item** → the tracking-missing page focused on that pool row; if the pool item has already been resolved, it opens the matched order instead `[PD-67 · OWNER-PENDING]`;
- comment on an inbound request → the Inbound Request list deep-linked to that request.

**Read state.** Opening a mention marks it read (`DC-30 comment.read`); `Mark all read` clears every unread mention in one action (`DC-31 comment.mark_all_read`), and both the nav badge and the tab badge drop to zero with the unread styling removed `[E-33]`.

**Star toggles from the hub** write the same `DC-28`/`DC-29` events as the in-thread star; the Saved tab and the thread stay consistent after rapid double-toggles (last write wins on a per-user, per-comment key) `[E-34]`.

**Freshness.** Whether new comments arrive by poll or push, and the search index scope/debounce, are dev-time decisions (§9.4 D-6) `[E-35]`.

---

### `[L-8]` Change Status dropdown

**Surface.** Button **`Change Status ▾`** opens a dropdown (`.statusdd`) listing exactly **8 WooCommerce statuses in this order**:
`pending` · `processing` · `on-hold` · `completed` · `refunded` · `failed` · `shipped` · `prepare-shipment`.
The current status carries class `on`. The order's status badge renders next to the title: `Processing` (`.st-processing`, green), `On Hold` (`.st-hold`, amber) etc.

**Value vs label.** The eight strings above are the **stored values** — lowercase, hyphenated — and every event payload uses them verbatim (`DC-1 old_status → new_status`, `processing → prepare-shipment`). The **badge renders a title-cased label** of the same value: `pending` → `Pending`, `processing` → `Processing`, `on-hold` → `On Hold`, `completed` → `Completed`, `refunded` → `Refunded`, `failed` → `Failed`, `shipped` → `Shipped`, `prepare-shipment` → `Prepare Shipment`. The dropdown items render the **values**, which is why `QA-STA-1` asserts lowercase strings while `QA-STA-5` asserts `Processing` / `On Hold` on the badge. Neither register is a second vocabulary `[X-9]`.

**Cancel is NOT a status value.** Cancelling an order is the separate `✕ Cancel Order` control `[L-F5]`. Do not add `cancelled` to this list `[BR-12]`. **Cancellation is a flag on the order, not a ninth status:** a cancelled order keeps whatever status value it carried and gains a cancellation marker (`DC-4` records `previous_status`), which is why `[L-F5]` persists `order.cancelled` rather than a `DC-1` status transition, and why a cancelled order still renders read-only with its history `[E-56]`. A screen that needs to *display* "cancelled" renders the underlying status plus that marker `[X-3]`.

**Trigger → behavior.**
1. Click the button → dropdown opens. Clicking elsewhere closes it with no change `[E-46]` `NE-2`.
2. Pick a value.
3. **Destructive values require a confirm dialog** before applying: `refunded`, `failed`, `completed`. Every other value applies immediately `[PD-28 · OWNER-PENDING]` `[BR-13]`. Dismissing the dialog changes nothing and persists nothing `NE-15`.
4. **All 8 statuses are selectable from any current state** — this mirrors the live admin's freedom deliberately `[PD-28 · OWNER-PENDING]`.
5. Persist `DC-1 order.status_changed` (`old_status → new_status`, actor, ts, `source=detail-dropdown`). This is the highest-value audit event on the page.
6. Additionally persist `DC-2 order.hold_placed` when the new value is `on-hold`, and `DC-3 order.hold_released` when moving off `on-hold`. These are first-class events even though derivable from `DC-1`, because hold is an operational state people ask questions about.
7. **Hold reason:** when `on-hold` is selected, an **optional free-text reason** is captured, persisted on `DC-2`, and rendered in the hold banner `[L-14]`. Optional so urgent CS is never blocked `[PD-20 · OWNER-PENDING]` `[BR-24]`.
8. Apply instantly, no refresh; badge, banner and the Outbound gate all re-render in place.
9. Green toast: `Status changed to {status}`.
10. Re-selecting the current value is a no-op — no event, no toast `NE-11`. Rapid re-selection produces no duplicate events `[E-5]` `[G-9]`.
11. Selecting `on-hold` disables **📦 Outbound** immediately `[L-9]`; per-row Inbound stays enabled `[BR-2]`.
12. `shipped` / `prepare-shipment` are selectable manually even with no outbound event on record. The status change is persisted; **no shipment and no inventory movement are fabricated**, and no Actor Log `OUTBOUND` row appears. The log's silence is the honest record `[E-66]`.

**Wireframe demo limitation:** the dropdown items have no click handler; selecting a value changes nothing on the static page. `[ADMIN]`-tier.

---

### `[L-9]` 📦 Outbound

Relabeled from "Outbound to Deleo BaroShip" (2026-07-22) because non-Deleo carriers are the majority. The carrier is already shown by the badge next to the order title.

**Position.** Line Items footer (`.li-foot`), right of `Bulk Inbound Selected Items`. Order-level, therefore not on any row `[BR-4]`. In State 1 it carries `id="obBtn"`.

**Enable predicate — a pure AND of independent conditions:**

```
enabled  ==  every(line.inbound_status == INBOUNDED)
         &&  line_count >= 1
         &&  order.status ∈ { processing, pending }
```

- Blocked from `on-hold`, `refunded`, `failed`, `completed`, `shipped`, `prepare-shipment` `[PD-29 · OWNER-PENDING]` `[BR-1]` `[E-16]`.
- A 0-line order can never ship: the `line_count >= 1` term exists because deleting the last line is allowed `[PD-24 · OWNER-PENDING]` `[E-55]`.
- **Releasing the hold alone does not enable the button** when inbound is incomplete, and completing inbound alone does not enable it while on hold. The causes are independent and both must clear `[BR-3]` `[E-12]` `[E-13]`.
- **Scope of the predicate.** It governs **this control**, on this page, and the View Orders row control that shares its grammar `[BR-4]`. It is not asserted as the only path that can ever emit `order.outbounded`: Closing's `[L-M1]` scan flow emits the same canonical event behind a **Zero Packing** gate that does not evaluate inbound completeness. That divergence is an open cross-page conflict `[X-2]` owned by Closing, not a licence to relax the gate here. Stated so nobody reads "enabled iff …" as a system-wide invariant it currently is not.

**Disabled rendering.** `disabled` attribute + class `btn-gray` + `opacity:.55` + `cursor:not-allowed` (State 2 wireframe). Disabled is not enough on its own: the UI must **say which gate is blocking** `[BR-46]` — the hold banner names the hold `[L-14]`, and the per-row `PENDING` tags name the incomplete inbound. When both apply, both are visible simultaneously; that is exactly what the State 2 demo shows.

**Trigger → behavior (enabled path).**
1. Click **📦 Outbound**.
2. **Send sound** plays `[G-3]`(a) `[PD-2 · OWNER-PENDING]` `[C-5]`. This page has no TTS and no warning tone `[BR-29]`.
3. Server revalidates the full gate at commit. If any line was cancelled back to `PENDING` or the status changed in the interim, it rejects with a red toast naming the reason and re-renders `[E-11]` `[PD-6 · OWNER-PENDING]`; nothing partial is written.
4. Persist `DC-19 order.outbounded` with all SKUs + quantities, carrier, actor, ts, and a **gate snapshot** (inbound completeness, order status and line count as evaluated at commit). The snapshot is what makes a later dispute answerable.
5. Persist `DC-21 inventory.movement` for the outbound deltas.
6. Order status transitions to `prepare-shipment`; badge re-renders. No page refresh.
7. Green toast: `Outbound sent — {n} item(s)`.
8. Actor Log gains one aggregate row: `OUTBOUND · All ({n} SKU) · {total qty}`.
9. Double-click yields exactly one outbound event and one sound `[G-9]` `[E-2]`.
10. **The sound is feedback, never proof.** It may play on a request that later fails; only `DC-19` proves an outbound `[E-37]`.

**Auto-outbound does not exist on this page** `[PD-21 · OWNER-PENDING]` `[BR-5]` `[C-7]`.

**Cancel Outbound.** Order Detail carries a **Cancel Outbound** control with the same rollback semantics as View Orders (`prepare-shipment` → `processing`), so a correction started here can be finished here `[PD-26 · OWNER-PENDING]` `[BR-19]`. It **replaces** `📦 Outbound` in the footer once the order is outbounded. Clicking it: confirm step → persist `DC-20 order.outbound_cancelled` (all SKUs/qty, prior status → `processing`, actor, ts, optional reason) + `DC-21` reversal movements → green toast `Outbound cancelled` → Actor Log gains `CANCEL OUTBOUND · All ({n} SKU)`. Per-row **Cancel Inbound** becomes enabled again only after this runs `[BR-14]`. This control is not drawn in the wireframe — §9.5.

**No carrier assigned.** An order flagged "Not connected — contact the Fulfillment Center" by the Order Management import reaches this page with no carrier. Outbound and Print both surface that state as the blocking reason rather than failing at the carrier API. **What unblocks such an order, and who owns it, is undecided** `[PD-55 · NO-DEFAULT]` — this page states the display and the block, and invents no manual carrier-assignment affordance `[E-86]`.

---

### `[L-10]` Inventory column group (8 columns) and the 18-column table contract

**Exact column contract — 18 rendered columns** `[BR-42]`:

| Group | Columns (in order) | Count |
|---|---|---|
| (fixed) | select-all checkbox · `SKU` · `Image` | 3 |
| `Product Information (WooCommerce)` | `Product Name` · `Product Name KR` · `Size` · `Qty` · `Subtotal` · `Total` | 6 |
| `Inventory` | `Latest Inventory Count` · `Inbound Status` · `Sourcing Route` · `Order Number` · `Order Date` · `Product Cost 🤖` · `Tracking Number` · `CP Link` | 8 |
| (fixed) | `Actions` | 1 |

**Removed — must NOT exist** (2026-07-22, commit `9c1f2a7`):
- **`Delivery Company` column** — removed.
- **`Comments` column** — removed; order comments are consolidated into the Operator Comments section `[L-1]`, one home only.
- **`Inbound Request` header column** — replaced by the select-all checkbox `[L-F13]`.
Re-adding any of them is a regression. A developer reading an old capture will find them; they are gone on purpose `[BR-8]` `[BR-40]`.

**`Latest Inventory Count` was removed and then restored** (restored 2026-07-23, commit `bbaa96f`) at the live screen's position — first column of the Inventory group. It shows the live warehouse stock for that SKU.
- **JIT lines show `0` and that is correct, not an error.** JIT holds no warehouse stock by definition `[BR-7]` `[E-41]`. QA must never flag a `0` on a JIT line as a defect.
- Warehouse-kept routes (WHOLESALE, PARTNERSHIP, SMART BUY) show current stock — wireframe row 3 shows `12` on a WHOLESALE line.
- After a JIT line is inbounded the count reflects the transient receipt and returns to `0` once the order is outbounded. A JIT line that shows a persistent non-zero count after outbound is a genuine reconciliation signal, not a display bug `[E-90]`.

**`Product Cost 🤖`** carries the robot marker in the header because the value is normally auto-filled by the purchasing agent. Agent-filled values remain human-editable `[L-12]` and the actor type is always recorded `[BR-27]` `[DC-14]`.

**`*` asterisk provenance.** SKU and Qty cells render the WooCommerce original in parentheses with an asterisk (`100005104` / `(100005104*)`, `1 (1*)`) in a `.bot` span. This is the pre-variation-pack-recalculation value. **Both copies are permanent** — the original is never overwritten `[BR-26]` `[DC-17]`. The inline note (`.liinfo`) states it: `Edit a line via the Edit button. Use checkboxes to select items for bulk Inbound. * = WooCommerce original before variation-pack recalculation · 🤖 = auto-filled by Agent · Scroll right to see the Inventory fields.`

**`Inbound Status`** renders exactly `INBOUNDED` (`.tag.tag-inbounded`, green solid) or `PENDING` (`.tag.tag-pending`, amber). **These two values are the whole vocabulary — there is no `OUTBOUNDED` line status** `[BR-50]`. Outbound is order-level `[BR-4]`: it moves the *order* to `prepare-shipment` and writes `DC-19` + `DC-21`, and it touches no line-level inbound state, which is exactly why Cancel Outbound `[BR-19]` needs no line-state reversal. RTO's Bulk Outbound spec writes `INBOUNDED → OUTBOUNDED` per line; if that write reaches the same record, every row here renders an unmapped status. Open as `[X-4]` — until it is adjudicated, a third tag must not be added to this contract.

**Sample-set display.** When Order Management has assigned a sample set to this order, the internal view shows **which** sample and **how many** in the line-items area `[G-13]` `[PD-27 · OWNER-PENDING]` `[BR-34]`. The carrier-facing `(+ sample set)` appending is a label/export concern and does **not** change what this page displays. The source that defines which sample and how many is an unresolved owner question `[PD-51 · NO-DEFAULT]` (§9.2) — the display requirement stands regardless of where the definition comes from. Order Detail **never edits** the assignment `[E-57]`.

**Catalog drift.** A line whose SKU was merged, retired or deleted from the catalog after the order was placed keeps its historical SKU and names — the order record is historical truth. `Latest Inventory Count` resolves against the surviving SKU where a mapping exists, otherwise renders `–` with a muted `SKU retired` marker. The line is never auto-rewritten `[E-62]` `[E-91]`.

---

### `[L-11]` Product Name (EN · KR) — brand always bold-prefixed

Both name columns render the **brand in bold as the first token** `[G-6]`:
- EN: **Dr.Jart+** Pore Remedy Renewing Foam Cleanser
- KR: **Dr.Jart+** 포어레미디 리뉴잉 폼 클렌저

**Page delta:** this is the only screen showing EN and KR names side by side, so the brand rule applies to **both** columns. The KR cells originally carried the Korean brand form (`닥터자르트`); on 2026-08-03 all 72 KR brand cells across the wireframe set were normalized to the **EN brand form in bold** followed by the Korean product name (commit `f8c4bae`). Korean product names themselves are **data** — never translated `[G-6]` `[BR-10]`.

A product whose catalog record has no brand renders without the prefix. That is a **product-data fix in the catalog, not a UI workaround** — the UI must not synthesize or guess a brand `[E-45]`.

RTO's Korean-name rule (`[G-6]`: Ready Item Details and the picking list use Korean names) is a different page's delta and does not change this page's EN-primary column order.

---

### `[L-12]` Line edit / delete UX

**Editable-field whitelist — exactly 5 fields, all agent-tracking fields:**
`Order Number` · `Order Date` (+ **Today** shortcut) · `Product Cost` · `Tracking Number` (purchase-side) · `CP Link`.

**Not editable here:** `SKU`, `Product Name`, `Product Name KR`, `Size`, `Qty`, `Subtotal`, `Total`, `Latest Inventory Count`, `Inbound Status`, `Sourcing Route`. WooCommerce commerce values are not edited from this screen `[BR-25]`.

**Trigger → behavior.**
1. Click the row's `✎` (`.act-ic .edit`) → the 5 cells become inputs (`input.ed-in`), the row gets the edit tint (`tr.row-edit`), and the Actions cell switches to **`✓`** (`.act-ic .ok`, green solid, Save) and **`✕`** (`.act-ic .no`, red outline, Cancel). Row 1 (SKU `100005104`) is pre-rendered in edit mode in both wireframe states as the worked example.
2. The **`Today`** button (`.ed-today`) under Order Date sets **only that input** to the current local warehouse date in `YYYY-MM-DD`. It does not save `[E-26]`.
3. **Validation on Save, client-side first, no server call on failure:**
   - `Order Date` must match `YYYY-MM-DD` `[E-17]`.
   - `Product Cost` must be a non-negative number; `0` is valid (FOC purchases exist) `[E-18]`.
   - `CP Link` must parse as an absolute `http(s)` URL; message on failure: `Enter a valid http(s) URL`. Strictness beyond URL parsing (domain allowlist) is dev-time `[E-19]` (§9.4 D-9).
   - `Order Number` and `Tracking Number` are free text; empty is allowed (renders `–`).
4. Click **`✓`** → persist `DC-13 line_item.edited` with a **field-level old→new map covering only changed fields**, actor, ts. Unchanged fields are not written.
5. Row exits edit mode and re-renders with the saved values. Green toast: `Line item updated`. No refresh.
6. Click **`✕`** → all 5 inputs restore their original values, the row exits edit mode, and **zero events are persisted** `[E-20]` `NE-4`.
7. **Concurrency:** a second operator saving the same line after someone else already saved gets an optimistic-version 409 → the row reloads with the winning values and a non-green toast `Line changed by {user} — reloaded`. The rejected operator's typed values are shown in the conflict message, never silently discarded `[E-21]` `[PD-7 · OWNER-PENDING]`.
8. **Agent autofill** writes the same fields with `actor_type=agent` and persists `DC-14 line_item.autofilled` — a **distinct event type** from `DC-13`. The human/agent distinction is a hard requirement: product-cost provenance depends on it `[BR-27]`.

**Delete.** Clicking `🗑` (`.act-ic .del`) opens **M3** `[L-M3]`.

---

### `[L-13]` 🖨 Print

**Label is exactly `🖨 Print`** — no carrier suffix. The carrier is shown by the badge (`YUN`) to its left (2026-07-21, commit `ce3eb96`). `Print (YUN)` and `Print (DELEO)` must **not** exist `[BR-40]`.

**Page deltas on `[G-4]`:**
- Print surfaces on this page: `🖨 Print` only.
- Persist `DC-24 print.requested` (actor, ts, order, carrier) at click, then `DC-25 print.job_result` (canonical name) with the agent's job id and result.
- Success → green toast `Label sent to printer`.
- **Agent offline / printer unreachable** → red toast `Print agent unreachable — label not printed` within the dev-chosen timeout. There is no silent success and no browser-dialog fallback `[E-39]` `[PD-19 · OWNER-PENDING]`.
- Double-click yields one print job `[E-6]` `[G-9]`.
- **Printing is never a gate** on any other action.
- **Reprints are a normal recovery path.** Clicking Print again while an earlier job for the same order is still queued is allowed; each click is its own `DC-24`/`DC-25` pair with its own job id, so duplicate labels are attributable `[E-63]`. This is not the same as `[E-6]`, which is one click delivered twice.
- Print with no label/tracking yet: disabled with the reason `No label yet`, rather than producing an empty print job `[E-40]`. **This answers a plan-raised owner question (`order-detail.B` Q-A5, "disabled vs error toast — and View Label when the label is missing") that has no entry in `_provisional-decisions.md`.** It is therefore *not* a `[PD-n]`: it is a dev default recorded in §9.4 D-20, chosen for consistency with `[BR-46]` (a guard renders its reason) and `[E-7]` (disabled beats an error toast, because a disabled control teaches the precondition). If the owner later registers it, `[E-40]`, this bullet and `[L-F7]` take the tag together.
- Print on a cancelled order: disabled with the reason `Order cancelled` — a label for a cancelled order is a picking error waiting to happen `[E-85]`.
- **`DC-25 result=success` proves the job reached the agent, not that paper came out.** A printer that is online but out of paper reports success. That limit is stated so nobody treats the event as physical proof `[E-84]`.
- **Label layout content is out of scope** — Phase 3-1. This section specifies print *behavior* only.

**`[L-F7]` View Label** opens a read-only preview of the existing label. Read action, explicit non-event `NE-5`. Disabled with `No label yet` when no label exists — same dev default as Print, §9.4 D-20 `[E-40]`.

---

### `[L-14]` On Hold state view

**Reach:** wf-bar tab `2 · On Hold`. The page is duplicated in full (2026-07-22, commit `c17df7c`). The tab strip is a wireframe device; the production page renders one state driven by the order's status `[BR-45]`.

**Exact diffs vs State 1 — five, and only five:**

| # | What changes |
|---|---|
| 1 | Status badge renders `On Hold` (`.st-hold`, amber) instead of `Processing` (`.st-processing`, green) |
| 2 | The hold banner (`#holdBannerH`) appears directly under the title row |
| 3 | The Change Status dropdown highlights `on-hold` instead of `processing` |
| 4 | **📦 Outbound** is disabled: `disabled` attribute, `.btn-gray`, `opacity:.55`, `cursor:not-allowed`, and it loses the `id="obBtn"` |
| 5 | Row 2 (SKU `100043697`) renders `PENDING` with a green **`Inbound`** button instead of `INBOUNDED` + `Cancel Inbound` |

Everything else — nav, hub, addresses, comments, Fulfillment Tracking, Actor Log, footer controls, dots 1–13 — is byte-identical between the two sections.

**Banner copy (exact, wireframe):**
`⏸ On Hold by urgent CS request — inbound still allowed, but Outbound disabled. Release the hold (Change Status) to ship`
When a hold reason was captured `[PD-20 · OWNER-PENDING]`, it is rendered in place of the "by urgent CS request" clause. The banner is the surface that tells the operator **why** the button is dead `[BR-46]`.

**The demo is deliberately a combined case: Hold + incomplete inbound (3/4).** This clause was added to the legend on 2026-08-03 (commit `f8c4bae`) precisely because operators and QA kept assuming one cause. Releasing the hold alone leaves Outbound disabled because SKU `100043697` is still `PENDING`; inbounding that line alone leaves it disabled because the order is still on hold `[BR-3]` `[E-12]` `[E-13]`.

**What does NOT change on hold:** per-row Inbound and Cancel Inbound stay available, Bulk Inbound stays available, line edits stay available, comments stay available, Print stays available. **Goods receipt must never stop because CS is negotiating with a customer** `[BR-2]`.

**Hold on an already-outbounded order** is allowed as a status change but changes nothing downstream — the parcel has left. It persists `DC-1` + `DC-2` and shows the banner; no shipment is recalled `[E-67]`.

**A hold placed mid-batch** by another operator does not roll back a running Bulk Inbound; only the Outbound gate is affected `[E-61]`.

---

### `[L-M3]` Delete-line confirmation modal

**Exact copy.**
- Header: `Are you sure?` with a `✕` close control (`.modal header .x`).
- Body: `This action cannot be undone. This will permanently delete the line item.`
- Footer: `Cancel` (grey) and `Delete` (red).

**Dismiss paths — three, all equivalent, all no-ops:** the `✕`, the `Cancel` button, and a click on the backdrop (`.overlay` outside `.modal`). None deletes anything, none persists an event `[E-24]` `NE-6` `NE-16`.

**Delete path.**
1. **Guard:** deleting an `INBOUNDED` line is **blocked** — the modal states `Cancel Inbound (restock) on this line first` and `Delete` is disabled. Deletion is permitted only on `PENDING` lines `[PD-23 · OWNER-PENDING]` `[BR-16]` `[E-22]`. A deleted line cannot carry a restock decision — the same doctrine as `[BR-14]` / `[BR-15]`.
2. Click `Delete` → persist `DC-15 line_item.deleted` with the **full line snapshot — every field of the line record, all 18 rendered columns plus the non-rendered ids and timestamps** — plus actor and ts. The UI action is irreversible; **the data is not lost** `[G-8]`.
3. The row disappears, `Total Quantity` `[L-F15]` decrements, the Outbound gate re-evaluates, and the Actor Log is unaffected (deletion is not an inbound/outbound movement).
4. Green toast: `Line item deleted`.
5. Double-click on `Delete` deletes once and closes the modal once; the second click produces no "row not found" error `[E-4]` `[G-9]`.
6. **Deleting the only remaining line is allowed.** A 0-line order is permitted; it simply cannot ship, because the Outbound gate additionally requires ≥1 line `[PD-24 · OWNER-PENDING]` `[BR-17]` `[E-23]` `[E-55]`.

---

### Page furniture — functional contracts

**`[L-F1]` ← Back to Orders.** Navigates to View Orders. Client navigation; non-event `NE-7`.

**`[L-F2]` ↻ Audit History.** Opens the order's audit-history surface — the queryable view over all persisted events for this order (§5.5). Navigation; non-event `NE-7`.

**`[L-F3]` ↗ View in WP.** Opens the WooCommerce admin page for this order in a new tab. Persists `DC-33` with `target=wp`. WP-side behavior is out of scope (§9.1).

**`[L-F4]` ⧉ Clone Order.** Creates a new order from this one.
- **Copied:** line items (SKU + qty) and the billing and shipping addresses.
- **NOT copied:** comments, actor log, tracking numbers, the agent-tracking fields (`Order Number`, `Order Date`, `Product Cost`, `CP Link`), PIC and status — this list is exactly `[PD-31 · OWNER-PENDING]` `[BR-21]` `[E-50]`. A clone is a new purchase, not duplicated history.
- **Also not copied: any assigned sample set.** This is an **extension beyond PD-31's registered list**, which does not name sample assignment; it follows from `[G-13]`'s period rules — the clone is evaluated against the sample rules in force when *it* is created, by Order Management, so carrying the source order's set forward would bypass them. Recorded as an extension rather than as PD-31 content so the register and this spec do not appear to disagree; if the owner adds it to PD-31, this bullet merges into the one above `[E-83]`.
- Cloning a 0-line order is allowed and produces a 0-line order `[E-82]`.
- Confirm step → persist `DC-5 order.cloned` (`source_order_id → new_order_id`, `copied_fields[]`, `excluded_fields[]`, actor, ts) → green toast `Order cloned — {new order no.}` with a link to the new order.

**`[L-F5]` ✕ Cancel Order.**
- **Blocked when any line is `INBOUNDED`**, with the explicit message `Cancel Inbound (restock) on {n} line(s) first`. Auto-restocking on cancel would move stock without an operator decision about damage or loss `[PD-22 · OWNER-PENDING]` `[BR-15]` `[E-47]`.
- Otherwise: confirm step → persist `DC-4 order.cancelled` (prior status → cancelled, line count, actor, ts) → green toast `Order cancelled`.
- A blocked attempt persists `DC-9` with `reason_code=inbounded_lines_present`.
- A cancelled order still renders read-only with its full history, and still accepts comments `[E-56]` `[E-79]`.

**`[L-F6]` Order header block.** `Order # {no}`, status badge, carrier badge. Read-only render.

**`[L-F8]` 📋 Order Information.** Read-only fields: `Order Date` (`2026-06-30 SGT`), `Order Created At` (`30/06/2026 19:55:28 SGT`), `Total Items` (`4`), `Total Discount` (`AUD 13.11`), `Total Amount` (`AUD 129.8`), `PIC` `[L-5]`. Amounts render in the order's own currency with its code; this page performs **no** FX conversion and must never display a converted figure `[BR-48]` `[E-68]`.

**`[L-F9]` Billing / Shipping Address ✎.** Opens field-level editing of the address block. Save persists `DC-7 order.address_edited` with `scope=billing|shipping` and a field-level old→new diff map, actor, ts. Green toast `Billing address updated` / `Shipping address updated`. Country and postcode are validated against the carrier's requirements; a failure blocks save with an inline field-level message and persists nothing `[E-54]`. Address edits after outbound are allowed — the record must stay truthful — but never regenerate the label `[BR-22]` doctrine.

**`[L-F10]` ✎ Change Tracking #.**
- Opens an input for the **outbound carrier** tracking number (never the line-item purchase tracking number `[L-4]`).
- **Duplicate check across orders:** if the number already exists on another order, warn naming that order and allow the change with an explicit confirm. Legitimate duplicates exist (combined boxes) `[PD-32 · OWNER-PENDING]` `[BR-22]` `[E-49]`.
- **The label is NOT auto-regenerated and NOT invalidated.** Silent regeneration would print without operator intent `[G-4]`.
- Persist `DC-22 shipment.tracking_changed` (`old → new`, carrier, `duplicate_warning_shown`, actor, ts). If a duplicate warning was accepted, additionally persist `DC-35 shipment.tracking_duplicate_acknowledged` with the colliding order id.
- Green toast `Tracking number updated`.
- **Clearing the field to empty is allowed** and is a real correction (a wrongly attached number must be removable). It persists `DC-22` with `new=""`, and Print / View Label then fall back to their `No label yet` disabled state `[E-77]`.
- **Saving the identical current value is a no-op** — no event, no toast `[E-78]`.

**`[L-F11]` Reset Order.**
- **Scope: fulfillment/shipment state only** — tracking number, provider order id, label reference, shipment record. It **never** touches line-item inbound/outbound state and never reverses an inventory movement `[PD-30 · OWNER-PENDING]` `[BR-20]` `[E-48]`.
- Requires a confirm step; allowed at any time, including on a `DELIVERED` shipment.
- Persist `DC-8 order.reset` with an old→new snapshot of every cleared field.
- Green toast `Order reset — shipment data cleared`.
- A print job already queued at the agent is **not** recalled — the agent has it. The reset is recorded and the operator is told in the confirm dialog that a queued label may still print `[E-84]`.

**`[L-F13]` Select-all / row checkboxes.** The header checkbox (`title="Select all"`) toggles every row checkbox in the table — **every row, not only visible rows**, since this table has no pagination. Selection drives `Bulk Inbound Selected Items` only. Ephemeral client state; non-event `NE-1`.

**`[L-F14]` + Add Line Item.**
- **Blocked after outbound.** Post-shipment line changes desynchronize the shipped contents from the record `[PD-25 · OWNER-PENDING]` `[BR-18]` `[E-25]`. The button renders disabled with the reason; an attempt persists `DC-9` with `reason_code=order_outbounded`.
- Otherwise: pick a SKU + qty → persist `DC-16 line_item.added` (SKU, qty, initial values, `inbound_status=PENDING`, actor, ts) → the row appends as `PENDING`, `Total Quantity` increments, the Outbound gate re-evaluates → green toast `Line item added`.

**`[L-F15]` Total Quantity.** Renders `Total Quantity: {sum of line qty}` (wireframe: `4`). Recomputed on every add/delete/edit; a derived display, never a stored counter.

**`[L-F17]` Global nav + Logout.** Identical to the live admin. Items: `SkinSeoul` · `Operation AI ▾` · `Catalog Management ▾` · `OMS Center ▾` · `Site Management ▾` · `Customer Management ▾` · `SkinSeoul WP Admin`, then the Comments hub `[L-7]`, the user chip (`Y` avatar + `Yongwon Ryu`) and `Logout`. Navigation is a non-event `NE-7`.

---

## 4. Business Rules

Every rule carries a rationale and a decision date. Global rules are cited, never restated — where a rule row names a global rule, the row states this page's **delta**. Reversals appear in §10.3. IDs `[BR-1]`–`[BR-40]` are stable from spec v1.0; `[BR-41]`–`[BR-48]` were added in v1.1 and `[BR-49]`–`[BR-50]` in v1.2. IDs are never renumbered.

| ID | Rule | Rationale | Decided |
|---|---|---|---|
| **BR-1** | **Outbound gate.** 📦 Outbound is enabled only when every line is `INBOUNDED`, the order has ≥1 line, and the status is `processing` or `pending`. Blocked from `on-hold`, `refunded`, `failed`, `completed`, `shipped`, `prepare-shipment`. | Ship-incomplete prevention: an order that leaves with 3 of 4 items becomes a CS case and a refund. Making the gate a pure function of status + inbound completeness removes judgement from a speed-pressured moment. `[PD-29 · OWNER-PENDING]` | 2026-07-14 (completeness); status set 2026-08-03 |
| **BR-2** | **Hold blocks Outbound but never Inbound.** While `on-hold`, per-row Inbound, Bulk Inbound, line edits, comments and Print all stay available. | Hold exists for urgent CS (cancellation, address change). Goods keep arriving at the dock regardless of what CS is negotiating; stopping receipt would strand physical stock in an unrecorded state. | 2026-07-14, restated 2026-07-22 |
| **BR-3** | **The two Outbound gates are independent.** Releasing the hold alone does not enable Outbound; completing inbound alone does not either. The UI must always show which gate is blocking. | Operators filed "button broken" tickets against a working gate. The combined 3/4 + hold demo exists to make the multi-cause case impossible to miss. | 2026-07-22; legend clause added 2026-08-03 |
| **BR-4** | **Inbound is per product; Outbound is order-level.** Per-row Inbound / Cancel Inbound on each line; Bulk Inbound and Outbound in the table footer. The name "Request Inbound" is retired and must not reappear. | Matches the View Orders grammar so one mental model covers both screens; physically, items arrive one at a time while a parcel ships once. **Cross-page note:** Inventory's `[L-F2]` form note still sends operators to "Request Inbound on View Orders / the order detail" and asserts that string byte-exactly in its QA. The control does not exist on either page; that is stale copy on Inventory, not a reason to reinstate the name here. | 2026-07-14 (rework), per-row buttons 2026-07-23 |
| **BR-5** | **No auto-outbound on Order Detail.** Reaching full inbound enables the button; a human clicks it. | Order Detail is a desk screen for exception handling. Silent shipping from an inspection screen is the wrong default. Auto-outbound on full inbound is a View Orders scan/bulk behavior only. `[C-7]` `[PD-21 · OWNER-PENDING]` | 2026-08-03 |
| **BR-6** | **Sourcing routes render as the 4 order-facing labels**; JIT carries the purchase channel in parentheses, chosen by the handler at purchase time. Rendering rule per `[G-5]`. | Colour coding was tried and rejected — the table already carries two status colours and a third scheme made the row unreadable. The channel is provenance for cost reconciliation. | 2026-07-13 (4 routes), 2026-07-14 (colorless), 2026-07-23 (channel parenthetical) |
| **BR-7** | **`Latest Inventory Count = 0` on a JIT line is correct, not an error.** | JIT items are purchased after the order; no warehouse stock backs them. Without this rule written down, every audit re-raises it as a bug. | 2026-07-23 (restore) |
| **BR-8** | **`Delivery Company` and `Comments` columns must NOT exist in Line Items.** Order comments live only in Operator Comments `[L-1]`. | One home per fact. Two comment surfaces on one order guarantees that half the instructions are missed. | 2026-07-22 |
| **BR-9** | **Deleo Tracking No. is retained on Order Detail** even though it was removed from View Orders. | Deliberate asymmetry: View Orders is a speed surface where the column was noise; Order Detail is the reconciliation surface where it is evidence. Adjudicated as a non-issue in `_review.md` §1 so nobody "harmonizes" the two screens. | 2026-07-21 |
| **BR-10** | **Brand is bold-prefixed on both the EN and the KR product name** — page delta on `[G-6]`, which this page applies to two columns instead of one. | Pickers and CS both identify products brand-first; the KR column is read by the same people as the EN one. | `[G-6]` baseline; KR cells normalized 2026-08-03 |
| **BR-11** | **Comments are append-only and permanent.** No edit, no delete. Corrections are new comments. | `[G-7]` declares the comment history an AI-training and audit asset; mutability silently rewrites the corpus. `[PD-3 · OWNER-PENDING]` | 2026-08-03 |
| **BR-12** | **Status vocabulary is exactly 8 WooCommerce statuses**, applied instantly. `cancelled` is not among them — cancelling is `✕ Cancel Order`, and cancellation is a **flag on the order**, not a ninth status value: the order keeps its status and gains a marker (`DC-4` records `previous_status`). The 8 strings are stored **values**; the badge renders a title-cased **label** of the same value `[L-8]`. | Mirrors the live admin exactly; inventing a ninth value would desynchronize WooCommerce. The flag-vs-status and value-vs-label clauses were added 2026-08-03 because another screen renders `Cancelled` in a status column and a third mixes both casing registers in one sentence `[X-3]` `[X-9]`. | as-live, restated 2026-07-22; flag/label clauses 2026-08-03 |
| **BR-13** | **`refunded`, `failed` and `completed` require a confirm dialog**; all other status picks apply immediately. | These three have financial effects. Everything else is reversible by picking again. `[PD-28 · OWNER-PENDING]` | 2026-08-03 |
| **BR-14** | **Per-row Cancel Inbound is disabled once the order is outbounded — Cancel Outbound must run first.** | The only ordering that keeps inventory arithmetic reversible: reversing a receipt underneath a shipment produces stock that exists in neither place. `[PD-10 · OWNER-PENDING]`; the View Orders legend still labels this "(proposal)" `[WF-3]` | 2026-07-09 (proposed), adopted 2026-08-03 |
| **BR-15** | **✕ Cancel Order is blocked while any line is `INBOUNDED`** — `Cancel Inbound (restock) on {n} line(s) first`. | Auto-restock would move stock without an operator decision on damage or loss. Same ordering-guard doctrine as BR-14. `[PD-22 · OWNER-PENDING]` | 2026-08-03 |
| **BR-16** | **Deleting an `INBOUNDED` line is blocked**; deletion is allowed only on `PENDING` lines. | A deleted line cannot carry a restock decision. `[PD-23 · OWNER-PENDING]` | 2026-08-03 |
| **BR-17** | **Deleting the only remaining line is allowed.** A 0-line order is legal and cannot ship. | Blocking would strand orders created in error, with no way to clean them up. `[PD-24 · OWNER-PENDING]` | 2026-08-03 |
| **BR-18** | **+ Add Line Item is blocked after outbound.** | Post-shipment line changes desynchronize the shipped contents from the record. `[PD-25 · OWNER-PENDING]` | 2026-08-03 |
| **BR-19** | **Cancel Outbound exists on Order Detail**, with the same rollback as View Orders (`prepare-shipment` → `processing`), replacing 📦 Outbound in the footer once outbounded. | Parity: a correction started on Order Detail must be finishable here, or the operator has to hunt for another screen mid-correction. `[PD-26 · OWNER-PENDING]` | 2026-08-03 |
| **BR-20** | **Reset Order clears fulfillment/shipment state only** — never line-item inbound/outbound state, never an inventory movement. | Mirrors live semantics without letting a button labelled "reset" silently reverse physical stock movements. `[PD-30 · OWNER-PENDING]` | 2026-08-03 |
| **BR-21** | **Clone copies line items + addresses only.** Comments, actor log, tracking, agent-tracking fields, PIC and status are not copied `[PD-31 · OWNER-PENDING]`; **sample assignment is additionally excluded as a `[G-13]` extension**, not as PD-31 content `[L-F4]`. | A clone is a new purchase, not duplicated history; copying a purchase record would double-count cost, and copying a sample set would bypass Order Management's period rules. PD-31's registered list does not name sample assignment, so the exclusion is carried here as an extension with its own `[G-13]` rationale. | 2026-08-03; sample-set extension recorded separately 2026-08-03 |
| **BR-22** | **Change Tracking # warns on a cross-order duplicate and allows it with confirm; the label is never auto-regenerated or invalidated.** | Combined boxes make duplicates legitimate. Silent label regeneration would print without operator intent, violating `[G-4]`. `[PD-32 · OWNER-PENDING]` | 2026-08-03 |
| **BR-23** | **PIC is a system-user picker, not free text, and the new PIC is not auto-notified.** | PIC feeds filters and mention routing, so it must resolve to a real user; auto-notifying every reassignment would be noise. Use an @mention comment to notify. `[PD-33 · OWNER-PENDING]` | 2026-08-03 |
| **BR-24** | **Hold reason is optional free text, persisted with the hold event, and rendered in the banner.** | The banner already reads like a reason exists. Mandatory would block urgent CS at the exact moment speed matters. `[PD-20 · OWNER-PENDING]` | 2026-08-03 |
| **BR-25** | **Only the 5 agent-tracking fields are editable inline.** WooCommerce commerce fields (Qty, Subtotal, Total, names, size) are not editable on this screen. | Those values are owned by the storefront; editing them here would fork the source of truth. | 2026-07-14 |
| **BR-26** | **WooCommerce originals (`*`) are preserved beside recalculated values, permanently.** | Variation-pack recalculation changes SKU and qty; without the original, cost and settlement reconciliation is impossible. Provenance is never overwritten. | 2026-07-14 |
| **BR-27** | **Agent-autofilled (🤖) fields remain human-editable, and the actor type (human / agent / system) is always recorded and always distinguishable.** | Product-cost provenance drives margin analysis; "who put this number here" must survive. `[G-8]` | 2026-07-14 |
| **BR-28** | **Print surfaces on this page are `🖨 Print` only; `View Label` is a preview, not a print surface.** Failure copy is fixed in §3.0.2. Label layout is out of scope (Phase 3-1). | Page delta on `[G-4]`: naming the surface set prevents a developer wiring the preview into the agent, which would print on every glance. (No PD governs the surface set — `[PD-19 · OWNER-PENDING]` decides only that an offline print agent never gates the inbound, and is cited where it belongs, in `[L-13]` and `[E-39]`.) | 2026-07-21 (label de-suffixed), reconfirmed 2026-08-03 |
| **BR-29** | **Of `[G-3]`, only (a) applies here, on `📦 Outbound`.** No TTS `(b)`, no warning tone `(c)`. | `[G-3]`(a) is written by button class, not by page. The closing voice alert and the View Orders warning tone are scan-loop mechanisms and have no analogue on a desk screen. `[C-5]` `[PD-2 · OWNER-PENDING]` | 2026-08-03 |
| **BR-30** | **No scan input exists on this page and none may be added.** `[G-1]` does not apply. | Scanning is View Orders / Closing work. A scan field here would create a second, unreconciled inbound path. | 2026-08-03 |
| **BR-31** | **This page has no refresh exception**, and every confirming action's success string is fixed in §3.0.2. | Page delta on `[G-2]`: refreshing loses the operator's scroll position in an 18-column horizontally scrolled table and their place in the thread; fixed strings make the toast an assertable contract rather than a developer's improvisation. | 2026-08-03 |
| **BR-32** | **Suppressed duplicate submissions are persisted (`DC-36`).** | Page delta on `[G-9]`: this page is where the live double-click bug was found, so the fix must be provable with data, not asserted. | 2026-07-21 (bug logged), telemetry added 2026-08-03 |
| **BR-33** | **No control on this page is role-gated in v1; every mutation records the actor.** | `[G-15]` `[PD-1 · OWNER-PENDING]` — six screens independently raised the same question; eight ad-hoc models would be worse than one deferred decision. | 2026-08-03 |
| **BR-34** | **The internal view shows which sample set and how many** when Order Management assigned one; the carrier-facing "(+ sample set)" appending is a label concern and does not change this display. Order Detail never edits the assignment. | `[G-13]` dual view. Order Detail is an internal screen; hiding the sample makes a customer dispute unresolvable. `[PD-27 · OWNER-PENDING]` | 2026-08-03 |
| **BR-35** | **Order Detail is a receiving surface for unrecognized matching, never a resolution surface.** A confirmed match elsewhere writes the tracking number onto this order's product line and posts an auto-comment @registrant; there is no match UI here. | One match pipeline, one audit trail, regardless of which screen resolved it. `[PD-16 · OWNER-PENDING]` | 2026-07-23, reconfirmed 2026-08-03 |
| **BR-36** | **The Actor Log is a view over persisted events, never the only copy.** | `[G-8]`. A UI-only log is lost on the first schema change and cannot be queried for disputes. | 2026-07-14 |
| **BR-37** | **The server revalidates at confirm; stale entities are rejected with a red toast and no partial write. Concurrent edits use an optimistic version check → 409 → reload + non-green toast.** | Last-write-wins silently destroys field data. `[PD-6 · OWNER-PENDING]` `[PD-7 · OWNER-PENDING]` | 2026-08-03 |
| **BR-38** | **Slack delivery failure never blocks the UI and never rolls anything back**; it is persisted and retried. | Notification is a side effect, not part of the transaction. `[PD-4 · OWNER-PENDING]` | 2026-08-03 |
| **BR-39** | **Every removal or deletion gets a confirm step and a toast**, and a reason where a reason enum already exists in the flow. | `[GD-5]` `[C-6]` `[PD-5 · OWNER-PENDING]`; the wireframe's silent removals are gaps, not decisions. | 2026-08-03 |
| **BR-40** | **Removed features must NOT be re-implemented** (full list in §10.2): the "Request Inbound" label, the "Outbound to Deleo BaroShip" label, carrier-suffixed Print labels, the `Delivery Company` column, the line-item `Comments` column, the `Inbound Request` header column, the bare `✎` PIC pencil, the @tag modal on Add Comment, and photo upload. | Every one of them exists in a capture or an old doc that a developer will find. Silence invites re-implementation. | various, see §10.2 |
| **BR-41** | **Per-line inbound on Order Detail is all-or-nothing; there is no quantity input.** Partial receipt against an expected quantity belongs to View Orders State 6 / the inbound-request lifecycle. | A quantity field here would create a second partial-receipt path with no PARTIAL state, no remaining-quantity arithmetic and no mandatory-reason edit — it would silently diverge from the request reconciliation `[G-10]` `[G-11]`. | 2026-08-03 |
| **BR-42** | **The line-items table has exactly 18 rendered columns** (3 fixed + 6 WooCommerce + 8 Inventory + Actions). The `DC-15` delete snapshot covers every field of the line record, not only the rendered ones. | The column contract is what BR-8's removal rules and the snapshot requirement are measured against. Both planning lenses said "20 columns"; the wireframe renders 18 (§2.5 C). Stating the number wrong makes an auditor chase a phantom. | 2026-08-03 (corrected in spec v1.1) |
| **BR-43** | **Four time formats coexist on this page by design** (§3.0.3), and every persisted event stores UTC plus the display timezone. Times rendered without a zone are warehouse local, never browser local. | Harmonizing the formats would break parity with the live admin the team already reads; leaving the zone implicit would silently mis-time an operator in another country. | 2026-08-03 |
| **BR-44** | **The hub unread badge counts unread @mentions for the current user** — not unread comments, not all comments. With zero, the badge is absent rather than `0`. | The badge is a personal call-to-action. Counting everything would make it permanently non-zero and therefore ignored. | 2026-08-02 (badge normalized 3 → 2) |
| **BR-45** | **The two-state tab strip is a wireframe demo device, not a product feature.** Production renders one state driven by the order's status. | A developer copying the wireframe would build a tab strip that lets an operator "switch" an order's status by clicking a tab. | 2026-07-22 |
| **BR-46** | **Every guard that disables a control renders its reason next to the control**, not only in a tooltip or a hover. | Generalization of BR-3: a silent disabled button produces support tickets against working logic, and on a 1680px table the operator may never see a tooltip anchored off-screen. | 2026-08-03 |
| **BR-47** | **Every blocked attempt persists `DC-9 order.action_rejected` with a `reason_code`.** | Guards must be measured. Without this, nobody can tell whether a guard is protecting the operation or fighting it, and the first complaint becomes an argument instead of a query. | 2026-08-03 |
| **BR-48** | **No FX conversion on this page.** Order totals render in the order's currency (`AUD 129.8`), product costs in the purchase currency (`₩17,100`). | Mixing a converted figure into a settlement screen invites someone to reconcile against a rate the page never states. Conversion belongs to BI, not to the operational record. | 2026-08-03 |
| **BR-49** | **Cancel Inbound on this page always restocks the full line quantity.** No restock Yes/No choice and no Restock Qty input exists here; `DC-11` always carries `restock=true` and the full line qty. Partial restock and declined restock are View Orders `[L-M1]` / Inventory `[L-M4]` operations. | Symmetric counterpart of `[BR-41]`: a receipt taken in full is reversed in full. Two partial-restock paths with different remainder accounting would put the same physical reversal in the ledger twice, differently. Open cross-page conflict `[X-1]` — the other two screens expose the controls; this one deliberately does not. | 2026-08-03 |
| **BR-50** | **There is no `OUTBOUNDED` line status.** `Inbound Status` is exactly `INBOUNDED` or `PENDING`; outbound is order-level and moves the order to `prepare-shipment` without touching line state. | `[BR-4]`'s grammar taken to its conclusion, and the reason Cancel Outbound `[BR-19]` needs no line-state reversal. RTO's spec writes a per-line `OUTBOUNDED`; if that write lands on this record every row renders an unmapped tag `[X-4]`. | 2026-08-03 |

---

## 5. Data Capture

**Doctrine.** `[G-8]` governs. Order Detail's deltas on it are three: (a) **blocked attempts persist** (`DC-9`) so guards are measurable; (b) **suppressed duplicates persist** (`DC-36`) so the double-click fix is provable; (c) **arrival path persists** (`DC-34`) so the owner can see how people reach an order. Order Detail is the densest audit surface in the system — it is where "who did this and why" gets answered.

**Naming.** Cross-page shared events use the canonical byte-identical names from `_global-rules` `[C-12]`: `comment.posted`, `comment.mention_notified`, `comment.starred` / `comment.unstarred`, `comment.read` / `comment.mark_all_read`, `comment.auto_posted`, `order.status_changed`, `order.outbounded`, `print.job_result`. All other names are page-scoped lowercase `entity.action`. Literal API/endpoint naming is a developer decision.

**Below the canonical ten, five shared *concepts* carry a different name on each page** — idempotent duplicate suppressed (`action.idempotency_suppressed` here), stock moved (`inventory.movement` here), comment search executed (declared a **non**-event here, `NE-8`), Slack dispatch outcome (folded into `comment.mention_notified` here), line received (`line_item.inbounded` here). This spec keeps its names because renaming one page unilaterally would break the other page's QA; promoting the five into `_global-rules` is the fix, tracked as `[X-8]`. The `NE-8` row is the one that is more than cosmetic: three other screens **persist** a comment-search event, so it is a `[G-8]` disagreement, and this page's position is stated as a deliberate non-event with an owner-optional upgrade path (§5.4).

**Envelope.** Every event carries this in addition to its own payload: `event_id`, `event_name`, `order_id`, `actor` (`user_id` + display name, or `system` / `agent`), `actor_type` ∈ {`human`, `agent`, `system`}, `occurred_at` (**UTC**) + `display_timezone` `[BR-43]`, `source_screen = order-detail`, `idempotency_key`, `client_request_id`.

### 5.1 Persisted events (37 — `DC-1` … `DC-37`)

IDs are page-scoped and stable. `DC-35` appears in group D and `DC-36`/`DC-37` in group F for semantic grouping; the numbering is complete 1–37 and is never renumbered.

#### A. Order lifecycle

| ID | Event | Trigger | Payload (beyond envelope) | UI surface |
|---|---|---|---|---|
| **DC-1** | `order.status_changed` | `[L-8]` status pick | `old_status → new_status`, `source=detail-dropdown`, `confirm_required` (bool), `confirmed_at` when destructive | status badge; Audit History |
| **DC-2** | `order.hold_placed` | status → `on-hold` | `previous_status`, `hold_reason` (optional free text) `[PD-20 · OWNER-PENDING]` | hold banner `[L-14]` |
| **DC-3** | `order.hold_released` | status off `on-hold` | `new_status`, `hold_duration_seconds` | banner disappears |
| **DC-4** | `order.cancelled` | `[L-F5]` ✕ Cancel Order | `previous_status`, `line_count`, `confirm_acknowledged=true` | status badge |
| **DC-5** | `order.cloned` | `[L-F4]` ⧉ Clone Order | `source_order_id → new_order_id`, `copied_fields[]` (lines, billing, shipping), `excluded_fields[]` | toast link to the new order |
| **DC-6** | `order.pic_changed` | `[L-5]` ✎ Edit | `old_pic_user_id/name → new_pic_user_id/name` | PIC field |
| **DC-7** | `order.address_edited` | `[L-F9]` ✎ | `scope=billing\|shipping`, `field_diff{field:{old,new}}` | address panel |
| **DC-8** | `order.reset` | `[L-F11]` Reset Order | `cleared_snapshot{tracking_number, provider_order_id, label_ref, shipment_status …}` old→new, `confirm_acknowledged=true`, `queued_print_jobs[]` (not recalled, `[E-84]`) | Fulfillment Tracking block |
| **DC-9** | `order.action_rejected` | any guard-blocked attempt `[BR-47]` | `attempted_action`, `reason_code` ∈ {`inbounded_lines_present`, `order_outbounded`, `line_inbounded`, `status_blocks_outbound`, `hold_blocks_outbound`, `no_lines`, `stale_entity`, `no_label`, `order_cancelled`, `no_carrier`}, `entity_ref` | red toast / disabled-reason text |

`DC-9` is deliberate: a blocked attempt is operational signal. It tells the owner which guards fire, how often, and on which orders — the data that decides whether a guard is protecting the operation or fighting it.

#### B. Line items

| ID | Event | Trigger | Payload | UI surface |
|---|---|---|---|---|
| **DC-10** | `line_item.inbounded` | `[L-2]` per-row Inbound, or a child of a bulk submission | `line_id`, `sku`, `sku_original` (`*`), `qty` (always the full line qty `[BR-41]`), `PENDING → INBOUNDED`, `parent_event_id` when from bulk | Actor Log `INBOUND` row |
| **DC-11** | `line_item.inbound_cancelled` | `[L-2]` Cancel Inbound | `line_id`, `sku`, `qty` (**always the full line qty**), `INBOUNDED → PENDING`, `restock=true` (**always — no Yes/No and no qty input on this page** `[BR-49]` `[X-1]`), `note` (free text, may be empty) | Actor Log `CANCEL INBOUND (Restock)` |
| **DC-12** | `line_item.bulk_inbound_submitted` | `[L-2]` Bulk Inbound Selected Items | `selected_line_ids[]`, `processed_count`, `skipped_already_inbounded_count`, `skipped_line_ids[]`, `skipped_deleted_line_ids[]`, `failed_line_ids[]` | one batch toast; children render as rows |
| **DC-13** | `line_item.edited` | `[L-12]` ✓ Save | `line_id`, `field_diff{}` limited to the 5 whitelisted fields, **changed fields only** | row re-render |
| **DC-14** | `line_item.autofilled` | purchasing agent writes a field | `line_id`, `fields{}`, `values{}`, `source`, `actor_type=agent` | 🤖 marker |
| **DC-15** | `line_item.deleted` | `[L-M3]` Delete | **full line snapshot — every field of the line record** (all 18 rendered columns plus ids/timestamps) `[BR-42]`, `line_id`, `sku`, `qty`, `inbound_status_at_delete=PENDING` | row disappears |
| **DC-16** | `line_item.added` | `[L-F14]` + Add Line Item | `line_id`, `sku`, `qty`, `initial_values{}`, `inbound_status=PENDING` | row appends |
| **DC-17** | `line_item.wc_recalculated` | variation-pack recalculation | `wc_original{sku, qty}` → `recalculated{sku, qty}`, `actor_type=system`. **Both copies retained permanently** | `*` values in SKU/Qty cells |
| **DC-18** | `line_item.tracking_written` | cross-page: an unrecognized-pool match resolved onto this order | `line_id`, `sku`, `tracking_number`, `resolver`, `source_screen=tracking-missing\|view-orders`, `qty_mismatch` note when present `[PD-65 · OWNER-PENDING]` | Tracking Number cell + auto-comment |

#### C. Order fulfillment & inventory

| ID | Event | Trigger | Payload | UI surface |
|---|---|---|---|---|
| **DC-19** | `order.outbounded` | `[L-9]` 📦 Outbound | `lines[]{sku, qty}`, `total_qty`, `carrier`, **`gate_snapshot{all_lines_inbounded, order_status, line_count}` evaluated at commit**, resulting status `prepare-shipment` | Actor Log `OUTBOUND · All ({n} SKU)` |
| **DC-20** | `order.outbound_cancelled` | Cancel Outbound `[BR-19]` | `lines[]{sku, qty}`, `prepare-shipment → processing`, `reason` (optional) | Actor Log `CANCEL OUTBOUND` |
| **DC-21** | `inventory.movement` | emitted by DC-10 / DC-11 / DC-19 / DC-20 | `sku`, `location` (when warehouse-kept), `delta` (signed), `movement_type` ∈ {`inbound`, `cancel_inbound_restock`, `outbound`, `cancel_outbound_reversal`}, `source_event_id`, `balance_after` | `Latest Inventory Count` refresh; Inventory page |

`DC-21` is the ledger row the Inventory screen reads. It is a separate event from the line-item transition on purpose: the line-item event records the *decision*, the movement records the *stock consequence*, and a reconciliation must be able to compare them.

#### D. Shipment & print

| ID | Event | Trigger | Payload | UI surface |
|---|---|---|---|---|
| **DC-22** | `shipment.tracking_changed` | `[L-F10]` ✎ Change Tracking # | `old_tracking → new_tracking` (`new` may be empty `[E-77]`), `carrier`, `duplicate_warning_shown` (bool) | SHIPMENT DETAILS |
| **DC-23** | `shipment.tracking_synced` | carrier sync (silent, system) | `actor=system`, `synced_at`, `appended_events[]`, `result` ∈ {`ok`, `failed`}, `failure_reason` | `TRACKING HISTORY (synced …)` |
| **DC-24** | `print.requested` | `[L-13]` 🖨 Print | `carrier`, `label_ref`, `requested_at` | — |
| **DC-25** | `print.job_result` | print agent responds / times out | `job_id`, `result` ∈ {`success`, `agent_unreachable`, `printer_error`, `timeout`}, `printer_name`, `latency_ms`, `request_event_id` | green or red toast |
| **DC-35** | `shipment.tracking_duplicate_acknowledged` | operator confirms a cross-order duplicate `[BR-22]` | `tracking_number`, `colliding_order_id`, `acknowledged_by` | confirm dialog |

#### E. Comments

| ID | Event | Trigger | Payload | UI surface |
|---|---|---|---|---|
| **DC-26** | `comment.posted` | `[L-1]` Add Comment | `comment_id`, `body_raw` (verbatim), `mentions[]` (resolved, deduplicated user ids `[E-80]`), `unresolved_mention_tokens[]`, `source=human` | thread |
| **DC-27** | `comment.mention_notified` | per distinct resolved mention (silent) | `comment_id`, `channel=#fulfillment-admin-comments`, `channel_id=C0BMGEWM5QA`, `target_user`, `slack_message_ts`, `delivery_result`, `attempt_no`, `suppressed_reason` (`self_mention`) | — |
| **DC-28** | `comment.starred` | ★ toggle on (thread or hub) | `comment_id`, `user_id`, `false → true` | ★ + Saved tab |
| **DC-29** | `comment.unstarred` | ★ toggle off (thread or hub) | `comment_id`, `user_id`, `true → false` | ★ + Saved tab |
| **DC-30** | `comment.read` | opening a mention (silent) | `comment_id`, `user_id`, `unread → read` | badge decrement |
| **DC-31** | `comment.mark_all_read` | hub `Mark all read` | `user_id`, `comment_ids[]`, `count` | badge → absent |
| **DC-32** | `comment.auto_posted` | system comment lands on this order | `comment_id`, `source=system`, `origin` ∈ {`unrecognized_match_confirmed`, `expected_qty_edit`}, `origin_ref`, `mentions[]` | thread, flagged system |

`DC-28`–`DC-31` are **per-user** state on a comment that may belong to any order — the hub is cross-order. They are captured from this screen because the hub renders here.

#### F. Navigation provenance & integrity

| ID | Event | Trigger | Payload | UI surface |
|---|---|---|---|---|
| **DC-33** | `order.external_link_opened` | `[L-F3]` ↗ View in WP, `[L-4]` Order Number link, `[L-4]` CP Link | `target` ∈ {`wp`, `order_number_lookup`, `cp_link`}, `url`, `line_id` when line-scoped | new tab |
| **DC-34** | `order.detail_viewed` | page load | `entry_path` ∈ {`direct`, `view_orders_row`, `comments_hub`, `slack_deep_link`, `tracking_missing_match`, `clone_link`, `order_management_row`, `rto_row`} | — |
| **DC-36** | `action.idempotency_suppressed` | server dedupes a duplicate submission `[G-9]` `[BR-32]` | `suppressed_action`, `idempotency_key`, `original_event_id`, `delta_ms` | nothing (the user sees the original result) |
| **DC-37** | `entity.version_conflict` | optimistic version check fails `[PD-7 · OWNER-PENDING]` | `entity_type` ∈ {`order`, `line_item`}, `entity_id`, `client_version`, `server_version`, `attempted_action`, `winning_actor` | non-green toast + row reload |

`DC-34` gives the owner the arrival-path distribution that decides where to invest next (how many people reach an order from a Slack mention vs from View Orders). `DC-36` is the proof-of-fix telemetry for the double-click bug — without it, nobody can show the bug is gone. `DC-37` distinguishes "two people worked on the same order" from a server error, which otherwise look identical in support tickets.

### 5.2 Events explicitly NOT emitted by this page

Stated so a coverage audit does not look for them here:

- `product.barcode_registered` — barcode registration happens on View Orders / Inventory, never here.
- `order.sample_assignment_changed` — sample ON/OFF and its periods are owned by Order Management `[G-13]`. Order Detail **displays** the assignment `[PD-27 · OWNER-PENDING]` and emits nothing `[BR-34]`.
- Inbound-request lifecycle events (`REQUESTED` / `PARTIAL` / `INBOUNDED`, expected-qty edits) `[G-10]` `[G-11]` — owned by View Orders M6 and Inbound Request. Order Detail's inbound is per-line all-or-nothing and never produces a PARTIAL state `[BR-41]`.
- Closing session events — owned by Closing.
- Unrecognized-pool registration, match-confirm and removal events — owned by tracking-missing / View Orders. This page only **receives** `DC-18` and `DC-32` `[BR-35]`.
- No search/telemetry event for the comments hub `NE-8`.

### 5.3 Cross-page events that LAND on this order

| Origin | Landing artifact on Order Detail | Persisted as |
|---|---|---|
| tracking-missing / View Orders M2 — match confirmed | the purchase tracking number is written onto the matched product line; an auto-comment appears in the thread @mentioning the registrant (suppressed when resolver == registrant) | `DC-18` + `DC-32` (`origin=unrecognized_match_confirmed`) `[PD-16 · OWNER-PENDING]` |
| View Orders M6 — expected-qty edit on a related inbound request | **no** line-item change on this order; the auto-comment lands on the **inbound request**, not here | — (explicit non-landing; stated to prevent a false expectation) |
| Order Management — sample set assigned | the assigned sample and quantity render in the line-items area | display only, no event `[BR-34]` |
| Inventory M4 — reservation released on a line of this order `[PD-45 · OWNER-PENDING]` | the line returns to `PENDING` and `Latest Inventory Count` refreshes | `DC-21` written by Inventory; Order Detail renders the result and must not write a second movement |

### 5.4 Explicit NON-events (16)

Declared per `[G-8]` so developers do not over-log noise and QA does not look for rows that must not exist.

| ID | Action | Why it is not persisted |
|---|---|---|
| **NE-1** | Line checkbox toggle / select-all `[L-F13]` | Ephemeral client selection; the intent is captured by `DC-12` when the operator actually submits. |
| **NE-2** | Change Status dropdown open/close without picking `[E-46]` | No state changed. |
| **NE-3** | `Hide Comments` toggle `[L-F16]` | Client-local view state. |
| **NE-4** | Row edit `✕` cancel `[L-12]` `[E-20]` | The operator explicitly abandoned the change; persisting it would pollute the field-diff corpus. |
| **NE-5** | `View Label` preview `[L-F7]` | Read-only preview, no side effect. |
| **NE-6** | M3 dismissal via `✕`, `Cancel` or backdrop `[E-24]` | Nothing was deleted. |
| **NE-7** | In-app navigation: `← Back to Orders`, `↻ Audit History`, nav menu, `Logout`, state-tab switching | Navigation, not an action on the entity. (Arrival at the page is captured once as `DC-34`.) |
| **NE-8** | Comments-hub search typing / clearing `[L-7]` | A read query, not an operator action on an entity. **Owner-optional:** if search telemetry is ever wanted, it is a new event, not a silent change to this one. |
| **NE-9** | Comments-hub tab switch (`@ Mentions` ↔ `★ Saved`) | View state. Reading a mention is captured separately as `DC-30`. |
| **NE-10** | Horizontal scroll of the line-items table | View state. |
| **NE-11** | Re-selecting the already-current status `[L-8]`, or saving an unchanged PIC / tracking number `[E-78]` | No old→new delta exists. |
| **NE-12** | Empty/whitespace-only comment submit `[E-27]` | Guarded before the server call; nothing happened. |
| **NE-13** | Wireframe chrome: `Hide annotations`, the wf-bar, the legend, the purple dots | Does not exist in the real admin. |
| **NE-14** | Hovering / expanding tracking-history rows | Read-only. |
| **NE-15** | **Dismissing a confirm dialog** for a destructive action (destructive status, Cancel Order, Cancel Outbound, Cancel Inbound, Reset, Clone, Delete) | The operator withdrew before committing. Distinct from a **guard-blocked** attempt, which does persist `DC-9` `[BR-47]`. |
| **NE-16** | Opening any modal or dropdown without acting | View state. |

### 5.5 Retention & export

- **All events are permanent. No TTL, no purge, on any event in §5.1.** The comment corpus in particular is an explicit AI-training asset `[G-7]`; deleting old comments would destroy the thing the doctrine is accumulating.
- **Queryability is a hard requirement**, not an optimization: every event must be filterable by `order_id`, `sku`, `actor`, `actor_type`, `event_name`, `reason_code` and date range. The Actor Log `[L-3]` and `↻ Audit History` `[L-F2]` are two views over the same store `[BR-36]`.
- **Export:** the Audit History surface must be exportable (CSV, following the Closing report's encoding and column precedent). Order Detail itself ships **no export button in v1** — the requirement is on the query/export capability, not on new UI. Encoding, column set and pagination sizes are dev-time (§9.4 D-11).
- **Snapshot completeness:** `DC-15` (line deleted) and `DC-8` (order reset) must persist full snapshots, because both actions remove data from the UI permanently. UI-irreversible must never mean data-lost.
- **Actor-type fidelity:** `human` / `agent` / `system` must be distinguishable forever. Collapsing them into one "user" field breaks cost provenance `[BR-27]` and pollutes the comment corpus `[DC-32]`.
- **Historical name fidelity:** an actor removed from the user directory still renders their name on historical events `[E-88]`; the event stores the id and the display name at write time.

---

## 6. Integrations

### 6.1 Slack routing

Channels below are CONFIRMED by the owner on 2026-08-03 per `_slack-routing` `[C-2]`. Never write "pending" for these rows.

| # | Trigger (on this page) | Channel | Payload fields | Mention target |
|---|---|---|---|---|
| 1 | A comment containing one or more resolved `@mentions` is posted `[L-1]` `[DC-26]` | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) | order no., comment text, time, author, @mentioned user, deep link to this order | the mentioned user, @-ed in the message body so Slack raises a personal notification; the channel doubles as a team-visible archive `[G-7]` |
| 2 | A system auto-comment lands on this order — unrecognized match confirmed `[DC-32]` | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) | tracking no., matched product line, resolver, order no., deep link | the original **registrant**; suppressed when resolver == registrant `[PD-16 · OWNER-PENDING]` |

**One message per distinct mention.** Two `@Dean` tokens in one comment produce one Slack message `[E-80]`. A self-mention produces none `[E-60]`. Three *different* users mentioned in one body produce **three** messages, one per target — `[G-7]`'s payload carries a single "@mentioned user" field, and `DC-27` is one row per target user. RTO's spec states the opposite (one message naming everyone); that is open as `[X-7]`, and this page's shape is the one `[G-7]` supports.

**Explicit non-routes from this page** (stated so nobody wires them):
- `#unrecognized-tracking` — triggered by View Orders / tracking-missing registration only.
- `#wholesale-ops` and `#partnership-kr` — the morning no-tracking check on inbound requests only.
- **PIC change does not notify Slack** `[BR-23]` `[PD-33 · OWNER-PENDING]`.
- **Status change, hold, cancel, outbound, cancel-outbound, print, reset, clone and line edits do not notify Slack** in v1. Adding an alert stream nobody owns is worse than no alert.

**Failure handling.** Dispatch is asynchronous and never part of the transaction: the comment commits, delivery is retried, and every attempt's result is persisted on `DC-27` `[PD-4 · OWNER-PENDING]` `[E-29]` `[BR-38]`. Retry policy (backoff, attempt cap) is dev-time.

### 6.2 Deep links

**Inbound (how operators arrive here) — all must land on this page, with `DC-34.entry_path` set accordingly:**

| From | Link | `entry_path` |
|---|---|---|
| View Orders — order row click | order detail for that order | `view_orders_row` |
| Comments hub item click (any screen) `[L-7]` `[G-12]` | the order the comment belongs to | `comments_hub` |
| Slack `#fulfillment-admin-comments` message | the `deep link` payload field → this order | `slack_deep_link` |
| tracking-missing — after a match is confirmed | the matched order | `tracking_missing_match` |
| Order Management row link | this order | `order_management_row` |
| RTO row link | this order | `rto_row` |
| Clone toast link | the newly created order | `clone_link` |
| Typed URL / bookmark | this order | `direct` |

In the production admin these deep links resolve to the **specific entity**, not to a filtered list `[G-12]`. A deep link to a deleted or non-existent order renders an explicit not-found state; a cancelled order renders read-only with its history intact — never a blank page and never a JS error `[E-56]`.

**Outbound (links leaving this page):**

| Control | Target | Event |
|---|---|---|
| `[L-F1]` ← Back to Orders | View Orders list | `NE-7` |
| `[L-F2]` ↻ Audit History | this order's audit-history surface | `NE-7` |
| `[L-F3]` ↗ View in WP | WooCommerce admin, new tab | `DC-33` (`target=wp`) |
| `[L-4]` Order Number | purchase-side order lookup, new tab | `DC-33` (`target=order_number_lookup`) |
| `[L-4]` CP Link | Coupang product page, new tab | `DC-33` (`target=cp_link`) |
| `[L-7]` hub item → unrecognized-pool entity | tracking-missing focused on that row, or the matched order if already resolved `[PD-67 · OWNER-PENDING]` | `NE-7` |
| `[L-7]` hub item → inbound request | Inbound Request list deep-linked to that request | `NE-7` |
| `[L-F4]` toast link after clone | the newly created order | `NE-7` (the arrival persists `DC-34`) |

A cell rendering `–` is plain text, never a link, and produces no `DC-33` `[E-59]`.

### 6.3 Print pipeline `[G-4]`

Page deltas only; the instant-print doctrine itself is `[G-4]`.

- **Path:** `🖨 Print` click → server resolves the order's carrier (`YUN` in the wireframe; `Deleo` and any future carrier are equivalent) → renders that carrier's label → pushes the job to the local print agent → the agent pushes it to the printer queue.
- `DC-24` is written at request; `DC-25 print.job_result` at the agent's response or timeout.
- Failure copy on this page is fixed: `Print agent unreachable — label not printed` §3.0.2.
- `result=success` proves the job reached the agent, not that paper came out `[E-84]`.
- An order with **no carrier** cannot print; the disabled reason names that state `[E-86]` `[PD-55 · NO-DEFAULT]`.
- Agent product choice, timeout value, retry policy and job polling are dev-time (§9.4 D-3).
- **Label layout content is out of scope** (Phase 3-1).

### 6.4 Sheet / BI handoffs

**None originate on this page.** Stated explicitly so an integration audit does not go looking:
- The Procurement Hub sheet is fed from the **Inbound Request** list.
- The SS Daily Shipping Status sheet is updated from **Closing** `[PD-71 · NO-DEFAULT]`.
- FIFO COGS consumes `DC-21 inventory.movement` and the line-level `Product Cost` downstream of this page; Order Detail publishes the events, it never writes to a sheet.

### 6.5 System boundaries

- **WooCommerce.** Commerce fields (`Product Name`, `Product Name KR`, `Size`, `Qty`, `Subtotal`, `Total`, order totals, addresses at source) originate in WooCommerce. This page edits only the 5 agent-tracking fields `[BR-25]`, plus addresses, status and PIC. `↗ View in WP` is the escape hatch to the storefront admin; WP-side behavior is out of scope (§9.1). **Whether a line delete or add propagates back to WooCommerce must be settled before build** — either answer is acceptable, an undefined answer creates a silent divergence (§9.4 D-10).
- **Carrier tracking sync.** Inbound-only from the carrier/aggregator, persisted as `DC-23`; this page never pushes tracking events outward. `✎ Change Tracking #` changes the number the sync follows, not the carrier's data.
- **Inventory.** Consumes `DC-21`; `Latest Inventory Count` reads the current balance `[L-10]`. Inventory's M4 release path can reverse the same reservation this page's Cancel Inbound reverses `[PD-45 · OWNER-PENDING]` — the server must guarantee one reversal per line, the second attempt being a stale-entity rejection, not a second movement.
- **Purchasing agent (🤖).** Writes `DC-14` into the 5 tracking fields; its writes are human-overridable and its `actor_type` is permanent `[BR-27]`.
- **Order Management.** Owns sample assignment; this page renders it and emits nothing `[BR-34]`. Owns the marketing-order import that can produce the "Not connected — contact the Fulfillment Center" state this page must display `[E-86]`.

---

## 7. Edge Cases & Error States

IDs `[E-1]`–`[E-50]` are inherited unchanged from the order-detail.B plan and are referenced by the PD register; they are never renumbered. `[E-51]`–`[E-70]` were added in spec v1.0, `[E-71]`–`[E-92]` in v1.1. **92 cases total**, complete with no gaps.

Every case states the **expected behavior**, not a question. Where a case has no decided answer it names the open question and specifies nothing (§9.2).

### 7.1 Idempotency & double-action `[G-9]`

| ID | Situation | Expected behavior |
|---|---|---|
| **E-1** | Double-click per-row **Inbound** (the known live-admin bug) | Exactly one `DC-10` + one `DC-21`. The second submission is deduped server-side and persisted as `DC-36`. One toast. Primary regression anchor for the double-click bug. |
| **E-2** | Double-click **📦 Outbound** | Exactly one `DC-19`, one set of `DC-21` movements, **one** send sound. Second click suppressed → `DC-36`. |
| **E-3** | Double-click **Bulk Inbound Selected Items** | The selected set is processed once: one `DC-12`, one `DC-10` per line. Second submission → `DC-36`. |
| **E-4** | Double-click **Delete** in M3 | One `DC-15`; the modal closes once; no "row not found" error on the second click. |
| **E-5** | Rapidly re-select the same status in `[L-8]` | No duplicate `DC-1`. Re-selecting the current value is a no-op `NE-11`; re-selecting a different value twice within the debounce window yields one event. |
| **E-6** | Double-click **🖨 Print** | One `DC-24` and one print job at the agent; the second is suppressed → `DC-36`. Never two labels. |
| **E-70** | A replayed request arrives **after** the server dedupe window has expired | Treated as a new, genuine action and processed. The window length is dev-time; the spec requires ≥24h and requires `DC-36` to record `delta_ms` so the window can be tuned against real data. |

### 7.2 Inbound / Outbound gating & state

| ID | Situation | Expected behavior |
|---|---|---|
| **E-7** | Click **Bulk Inbound Selected Items** with **zero** checkboxes selected | The button is **disabled** — preferred over an error toast, because a disabled control teaches the precondition. No server call, no event. |
| **E-8** | Bulk selection includes lines that are already `INBOUNDED` | Idempotent skip. `DC-12` records `skipped_already_inbounded_count`; the single toast reports both numbers: `Inbounded {n} item(s) · {m} already inbounded`. No error. |
| **E-9** | Inbound a line that another operator inbounded a second earlier (stale row) | Server rejects, the row re-renders as `INBOUNDED` with `Cancel Inbound`, and a **non-green** toast states it was already inbounded. `DC-37` persisted; no second `DC-10`, no second stock movement `[PD-6 · OWNER-PENDING]` `[PD-7 · OWNER-PENDING]`. |
| **E-10** | **Cancel Inbound after the order was already outbounded** | Blocked. The per-row button renders disabled with the reason `Cancel Outbound first`. Attempt persists `DC-9` (`reason_code=order_outbounded`) `[BR-14]` `[PD-10 · OWNER-PENDING]`. |
| **E-11** | Operator A clicks **Outbound** in the same moment operator B cancels an inbound | The server re-evaluates the full gate at commit. Whoever commits second is rejected with a red toast naming the reason (`Line {sku} is no longer inbounded`); no partial outbound is written. `DC-9` (`reason_code=stale_entity`) + `DC-37` persisted. |
| **E-12** | Full inbound is reached **while the order is On Hold** | 📦 Outbound stays disabled; no auto-outbound fires. The hold banner remains the visible reason `[BR-3]` `[BR-5]` `[C-7]`. |
| **E-13** | The hold is released while only 3 of 4 lines are inbounded (the wireframe's demo case) | 📦 Outbound stays disabled. The banner disappears but the `PENDING` tag on SKU `100043697` remains the visible reason. Two independent causes, cleared independently `[BR-3]`. |
| **E-14** | Status is set to `on-hold` while an Outbound request is already in flight | The server resolves atomically. If the outbound commits first it wins and the hold applies to an outbounded order `[E-67]`. If the hold commits first the outbound is rejected with `reason_code=hold_blocks_outbound` (`DC-9`). Both outcomes are fully persisted; neither is a partial write. |
| **E-15** | Cancel Inbound submitted with an **empty note** | Valid. `DC-11` persists with `note=""`; the Actor Log Note cell renders `–`. Capture is required, content is optional `[L-3]`. |
| **E-16** | Click **Outbound** on an order whose status is `refunded` / `failed` / `completed` / `shipped` / `prepare-shipment` | Blocked — the button is disabled for all five, and for `on-hold`. Outbound is allowed only from `processing` or `pending` `[PD-29 · OWNER-PENDING]` `[BR-1]`. |
| **E-51** | **Cancel Outbound** clicked on an outbounded order | Confirm → `DC-20` + reversal `DC-21` movements → status `prepare-shipment` → `processing` → green toast `Outbound cancelled` → Actor Log gains `CANCEL OUTBOUND · All ({n} SKU)`. Per-row `Cancel Inbound` becomes enabled again `[BR-19]` `[BR-14]`. |
| **E-52** | **Cancel Outbound** on an order whose parcel was already scanned at Closing | Still allowed at the data layer — the record must be correctable — and the reversal is fully persisted (`DC-20`) so the Closing session's snapshot and this order disagree **visibly** rather than silently. Reconciling a confirmed closing is a Closing concern and is out of scope here `[PD-74 · NO-DEFAULT]`. |
| **E-55** | The order has **0 lines** (all deleted) | 📦 Outbound is disabled (`line_count >= 1` term of the gate). The table renders an empty state; `Total Quantity: 0`. The order is legal, it just cannot ship `[BR-17]`. |
| **E-61** | The order is put On Hold by another operator **mid-batch** during Bulk Inbound | The batch completes — inbound is allowed on hold `[BR-2]`. Only the Outbound gate is affected. No lines are rolled back. |
| **E-66** | Status is set manually to `shipped` or `prepare-shipment` with **no outbound event on record** | The status change is persisted (`DC-1`) and applied. **No shipment, no inventory movement and no Actor Log `OUTBOUND` row are fabricated.** The log's silence is the honest record; a later audit sees the status moved without an outbound. |
| **E-67** | Hold placed on an **already-outbounded** order | Allowed. `DC-1` + `DC-2` persist and the banner renders. Nothing downstream is recalled — the parcel has left. Outbound is already spent, so the gate is moot. |
| **E-71** | A line of qty > 1 where only part of the quantity physically arrived | **Not an Order Detail operation.** Per-line inbound is all-or-nothing here `[BR-41]`; the operator either receives the line in full or leaves it `PENDING` and handles the partial through View Orders State 6 / the inbound request, which owns PARTIAL, remaining-qty arithmetic and the expected-qty edit `[G-10]` `[G-11]`. No quantity input is added here. |
| **E-72** | A line in the bulk selection was **deleted by another operator** between selection and submit | Skipped, reported in the toast subtext, recorded on `DC-12.skipped_deleted_line_ids[]`. The batch does not fail. |
| **E-73** | The server can commit only **part** of a bulk submission | Committed children stand; failures are named in a red toast and recorded on `DC-12.failed_line_ids[]`. A batch is not atomic — refusing ten lines because one moved would strand the nine that were fine. |
| **E-86** | The order has **no carrier** ("Not connected — contact the Fulfillment Center", set by the Order Management import) | 📦 Outbound and 🖨 Print are disabled with that state as the visible reason `[BR-46]`; attempts persist `DC-9` (`reason_code=no_carrier`). **What unblocks the order and who owns it is undecided `[PD-55 · NO-DEFAULT]`** — this page invents no manual carrier-assignment affordance. |

### 7.3 Line edit / delete / add (`[L-12]`, `[L-M3]`, `[L-F14]`)

| ID | Situation | Expected behavior |
|---|---|---|
| **E-17** | Save with a malformed `Order Date` (not `YYYY-MM-DD`) | Inline validation error on that input, no server call, no event. Focus moves to the offending input. |
| **E-18** | Save with a non-numeric or negative `Product Cost` | Rejected inline; no server call. `0` is valid (FOC purchases exist). |
| **E-19** | Save with an unparseable `CP Link` | Rejected inline with `Enter a valid http(s) URL`. Whether to additionally enforce a domain allowlist is dev-time (§9.4 D-9). |
| **E-20** | Click `✕` in edit mode | All 5 inputs restore their original values, the row exits edit mode, **zero events persisted** `NE-4`. |
| **E-21** | Two operators edit the same line; the second saves | Optimistic version check → 409 → the row reloads with the winning values and a **non-green** toast `Line changed by {user} — reloaded`. `DC-37` persisted. The rejected operator's typed values are shown in the conflict message, never silently discarded `[PD-7 · OWNER-PENDING]`. |
| **E-22** | Delete an `INBOUNDED` line via M3 | **Blocked.** M3 renders `Cancel Inbound (restock) on this line first` and `Delete` is disabled. `DC-9` (`reason_code=line_inbounded`) `[BR-16]` `[PD-23 · OWNER-PENDING]`. |
| **E-23** | Delete the **only remaining** line | **Allowed.** The order becomes a 0-line order and cannot ship `[E-55]` `[BR-17]` `[PD-24 · OWNER-PENDING]`. |
| **E-24** | Dismiss M3 via `✕`, `Cancel`, or a backdrop click | All three close the modal with no deletion and no event `NE-6`. |
| **E-25** | **+ Add Line Item** on an outbounded or completed order | **Blocked.** The button renders disabled with the reason; an attempt persists `DC-9` (`reason_code=order_outbounded`) `[BR-18]` `[PD-25 · OWNER-PENDING]`. |
| **E-26** | Click **Today** under `Order Date` | Sets **only that row's** Order Date input to the current local warehouse date in `YYYY-MM-DD`. It does not save; the operator must still click `✓`. |
| **E-62** | A line whose SKU was merged or retired in the catalog after the order was placed | The line keeps its historical SKU and names (the order record is historical truth). `Latest Inventory Count` resolves against the surviving SKU where a mapping exists, otherwise renders `–` with a muted `SKU retired` marker. No auto-rewrite. |
| **E-64** | Operator uses the browser Back button after a status change | The page re-renders from the server on return; it never restores a cached pre-change state. Because no action on this page depends on a full-page refresh `[G-2]`, Back is always safe. |
| **E-91** | A line whose **product record was deleted** from the catalog entirely (not merged) | The line still renders with its stored SKU, names, size and prices from the order record. `Latest Inventory Count` renders `–` with the `SKU retired` marker. The line remains deletable and inbound-able — the order is the truth, not the catalog `[E-62]`. |

### 7.4 Comments & hub (`[L-1]`, `[L-7]`)

| ID | Situation | Expected behavior |
|---|---|---|
| **E-27** | Submit an empty or whitespace-only comment | No-op: no server call, no event, no toast, textarea keeps focus `NE-12`. (The wireframe already guards this: `const txt=(ta.value||'').trim(); if(!txt) return;`) |
| **E-28** | `@mention` of a name that is not a system user | The comment posts; the token stays plain text in the body; it is **not** added to `mentions[]`; no Slack message is sent. The unresolved token is recorded on `DC-26.unresolved_mention_tokens[]` so bad-mention frequency is measurable. |
| **E-29** | Slack delivery fails | The comment is already committed and visible. Delivery is retried; every attempt result persists on `DC-27`. The UI is never blocked and nothing is rolled back `[PD-4 · OWNER-PENDING]` `[BR-38]`. |
| **E-30** | A very long comment, or one containing HTML/script characters | Stored verbatim; **escaped on render** in the thread, the hub list and search results (escape before highlight). Long bodies wrap; they are never truncated in storage. A max length, if any, is dev-time (§9.4 D-13). |
| **E-31** | Hub search with no matches | The results pane renders exactly `No matching comments` and nothing else. |
| **E-32** | Clearing the hub search input | The tab bar reappears and the **previously active tab** is restored with its pane visible. |
| **E-33** | `Mark all read` | Every unread mention for the current user flips to read (`DC-31`); the nav badge and the tab badge both clear and the unread styling is removed from every item. |
| **E-34** | Rapid double star-toggle, or starring the same comment from the thread and the hub simultaneously | Final state is consistent (last write wins per user+comment key); the Saved tab and the thread agree after the round trip. Both `DC-28` and `DC-29` persist in order — the corpus keeps the flip-flop. |
| **E-35** | Someone else comments on this order while the page is open | The thread must not silently go stale. Poll vs push is dev-time (§9.4 D-6); at minimum the thread refreshes on any operator action on the page. |
| **E-60** | `@mention` where the mentioned user is the author (self-mention) | The comment posts normally; the Slack dispatch is **suppressed** and recorded as `DC-27.suppressed_reason=self_mention`. Same doctrine as suppressing the match auto-comment when resolver == registrant `[PD-16 · OWNER-PENDING]`. |
| **E-79** | Comment posted on a **cancelled, completed or outbounded** order | Allowed. Commentability is never gated by order state — the moment people most need to write on an order is after something went wrong. `DC-26` persists normally. |
| **E-80** | One comment body mentions the **same user twice** | One `DC-27` and **one** Slack message. `mentions[]` is deduplicated. |
| **E-81** | A comment body that is **only** an `@mention` and no other text | Valid; posts normally and notifies. The mention is the message. |
| **E-92** | The current user has **zero** unread mentions | The nav badge is **absent**, not `0` `[BR-44]`; the `@ Mentions` pane renders an explicit empty state rather than an empty box. |

### 7.5 Network & infrastructure

| ID | Situation | Expected behavior |
|---|---|---|
| **E-36** | Network failure mid-Inbound (the response is lost, the write may have landed) | The client retries with the **same idempotency key**. Exactly one stock movement results. If the operator reloads instead, the row's true state is whatever the server holds; the Actor Log is ground truth `[G-9]`. |
| **E-37** | Network failure mid-Outbound | Same contract as E-36. The send sound may have played without a commit — **the sound is feedback, never proof.** Only `DC-19` is proof. |
| **E-38** | Network failure while posting a comment | Retry with the same key produces no duplicate comment. |
| **E-39** | Print agent offline or printer unreachable | Explicit **red** toast `Print agent unreachable — label not printed` within the configured timeout. **No silent success. No browser print-dialog fallback.** `DC-25` persists the failure result. The failure never blocks any other action `[G-4]` `[PD-19 · OWNER-PENDING]`. |
| **E-40** | Print (or View Label) when the order has no label/tracking yet | Disabled with the reason `No label yet` rather than producing an empty job. A forced request persists `DC-9` (`reason_code=no_label`). **Dev default, not a PD:** the plan raised "disabled vs error toast" as an owner question (`order-detail.B` Q-A5) and no entry exists in `_provisional-decisions.md`; the answer here follows `[BR-46]` and `[E-7]` and is recorded in §9.4 D-20 `[L-13]` `[L-F7]`. |
| **E-58** | The same operator has the same order open in two browser tabs | Both tabs are live. The second mutation from the stale tab hits the version check → 409 → that tab reloads the row `[E-21]`. No cross-tab locking is required. |
| **E-63** | Print clicked while a previous job for the same order is still queued at the agent | Allowed — reprints are a normal recovery path. Each click is its own `DC-24`/`DC-25` pair with its own job id, so duplicate labels are attributable. Distinct from `[E-6]`, which is one click delivered twice. |
| **E-74** | The server returns 5xx on any mutating action | Red toast naming the action (`Could not {action} — try again`), the UI state is **not** optimistically advanced, and the client keeps the idempotency key for the retry. No event is written client-side; whether the server wrote one is resolved by the retry, not guessed. |
| **E-75** | The browser is fully offline when the operator clicks a mutating control | The action is refused immediately with a red toast (`No connection — action not sent`); nothing is queued silently. A warehouse operator must never believe a receipt landed because the UI looked hopeful. |
| **E-76** | The session expires or auth is lost mid-action | The action is rejected with a red toast and a re-authentication prompt; on re-auth the operator returns to **this order**, not to a list, and the un-sent action is not auto-replayed. |
| **E-84** | `DC-25` reports `success` but nothing physically printed (printer online, out of paper/toner) | Expected limit of the contract: `success` proves the job reached the agent, not that paper came out. The operator's recovery is a reprint `[E-63]`. Stated so nobody treats the event as physical proof. Related: a print job already queued when `Reset Order` runs is **not** recalled, and the reset confirm dialog says so `[L-F11]`. |

### 7.6 Display, empty and boundary states

| ID | Situation | Expected behavior |
|---|---|---|
| **E-41** | A JIT line shows `Latest Inventory Count = 0` | **Expected and correct** — not an error, not an empty state, not a data problem `[BR-7]`. Explicit regression guard against QA "fixing" it. |
| **E-42** | Actor Log is empty (new order, nothing inbounded yet) | The section, heading and header row still render, with one empty-state row (`No inbound or outbound activity yet`). The section is never hidden. |
| **E-43** | No shipment / no tracking events yet (pre-shipment order) | SHIPMENT DETAILS and TRACKING HISTORY each render an explicit empty state; the `(synced …)` marker is **omitted** rather than showing a fake time. A failed sync keeps the last successful timestamp instead of blanking the table. |
| **E-44** | A WHOLESALE or PARTNERSHIP line has no purchase Order Number / Order Date / Tracking Number / CP Link | Every absent value renders `–` (as wireframe row 3, SKU `100005088`). `–` is not a link and not an error. |
| **E-45** | A product whose catalog record has no brand | The name renders without a bold brand prefix. This is a **catalog data fix**, not a UI workaround — the UI must never synthesize a brand `[L-11]`. |
| **E-46** | The Change Status dropdown is open and the operator clicks elsewhere | The dropdown closes with no status change and no event `NE-2`. |
| **E-53** | PIC edit where the target user has been deactivated | Deactivated users are not selectable in the picker. If the order's stored PIC was deactivated after assignment, the historical name still renders with a muted `(inactive)` marker. |
| **E-54** | Address edit with an invalid country / postcode for the carrier | Save is blocked with an inline field-level error; nothing is persisted, no toast. Validation rules follow the carrier's requirements. |
| **E-56** | Arriving via a deep link to an order that has been cancelled, deleted, or never existed | An explicit not-found / cancelled state, never a blank page or a JS error. Cancelled orders render read-only with their history intact and still accept comments `[E-79]`. |
| **E-57** | Order Management has assigned a sample set to this order | The line-items area shows **which** sample and **how many** `[G-13]` `[PD-27 · OWNER-PENDING]`. The carrier-facing `(+ sample set)` string is a label concern and does not appear as a line item here. Order Detail never edits the assignment. The definition source is an open question `[PD-51 · NO-DEFAULT]`. |
| **E-59** | Clicking a cell whose value is `–` (Order Number, CP Link) | Nothing happens — `–` is plain text, never a link. No `DC-33`. |
| **E-65** | The Actor Log has more events than the display cap | Ordering stays newest-first and the cap is explicit (`showing latest {N}`), with the full history reachable through `↻ Audit History`. Pagination mechanics are dev-time. **Truncation must never be silent.** |
| **E-68** | Currency and locale rendering | Order totals render in the order's own currency with its code (`AUD 129.8`, `AUD 13.11`); product costs render in the purchase currency (`₩17,100`). This page performs **no** FX conversion and must not display a converted figure `[BR-48]`. |
| **E-69** | An operator without fulfillment training opens the page | v1 has a **single admin role**: every control is visible and enabled subject only to its business gate `[G-15]` `[PD-1 · OWNER-PENDING]`. The mitigation is that every mutation records the actor and every destructive action confirms. A role matrix is a post-v1 owner decision (§9.3). |
| **E-87** | A very large order (100+ lines) | The table renders every line — this table has no pagination, so select-all covers **all** rows `[L-F13]`. Bulk Inbound chunking is dev-time and invisible to the operator: one submission, one `DC-12`, one toast. The Actor Log applies its display cap `[E-65]`. |
| **E-88** | An Actor Log row whose operator was removed from the user directory | The historical display name still renders. Never `Unknown`, never blank — the event stored both the id and the name at write time `[BR-27]`. |
| **E-89** | An operator in a different timezone reads the page | Times rendered without a zone (Actor Log, comments, hub) are **warehouse local**, never browser local; times with a printed zone (`SGT`) render as printed; TRACKING HISTORY shows both local and UTC columns §3.0.3 `[BR-43]`. |
| **E-90** | `Latest Inventory Count` on a JIT line across its lifecycle | `0` before inbound (correct `[E-41]`), transiently positive between inbound and outbound, back to `0` after outbound. A JIT line still showing a positive count after outbound is a genuine reconciliation signal, not a display bug. |

### 7.7 Header / subbar actions (`[L-F4]`, `[L-F5]`, `[L-F10]`, `[L-F11]`)

| ID | Situation | Expected behavior |
|---|---|---|
| **E-47** | **✕ Cancel Order** on an order with `INBOUNDED` JIT lines | **Blocked** with `Cancel Inbound (restock) on {n} line(s) first`. `DC-9` (`reason_code=inbounded_lines_present`). The operator must decide, per line, whether the stock is good (restock) or damaged — a decision the system must not make silently `[BR-15]` `[PD-22 · OWNER-PENDING]`. |
| **E-48** | **Reset Order** — scope, and Reset on a `DELIVERED` shipment | Clears shipment/tracking/label state only; never line inbound/outbound state; never an inventory movement. Allowed at any time including after delivery. Confirm required; full old→new snapshot on `DC-8` `[BR-20]` `[PD-30 · OWNER-PENDING]`. |
| **E-49** | **✎ Change Tracking #** to a number already on another order | Warn, naming the other order; allow with an explicit confirm (combined boxes are legitimate). The label is **not** regenerated or invalidated. `DC-22` + `DC-35` `[BR-22]` `[PD-32 · OWNER-PENDING]`. |
| **E-50** | **⧉ Clone Order** — what ends up on the new order | Line items (SKU + qty) and both addresses. **Not** comments, actor log, tracking numbers, agent-tracking fields, PIC, status or sample assignment. The clone starts clean `[BR-21]` `[PD-31 · OWNER-PENDING]`. |
| **E-77** | **✎ Change Tracking #** cleared to empty | Allowed — a wrongly attached number must be removable. `DC-22` persists with `new=""`; Print and View Label fall back to their `No label yet` disabled state `[E-40]`. |
| **E-78** | **✎ Change Tracking #** (or PIC) saved with the identical current value | No-op: no event, no toast `NE-11`. |
| **E-82** | **⧉ Clone Order** on an order with 0 lines | Allowed; produces a 0-line order which cannot ship until lines are added `[E-55]`. |
| **E-83** | **⧉ Clone Order** on an order carrying an assigned sample set | The sample set is **not** copied. The clone is evaluated against the sample rules in force when it is created, by Order Management `[G-13]` `[BR-21]`. |
| **E-85** | **🖨 Print** on a cancelled order | Disabled with the reason `Order cancelled`; a forced request persists `DC-9` (`reason_code=order_cancelled`). A label for a cancelled order is a picking error waiting to happen. |

---

## 8. QA Acceptance Criteria (machine-runnable)

### 8.0 How to run this section

**Target for `[WF]` scenarios:** `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/order-detail/`
Every `[WF]` step uses a label or selector that exists on that page today, and every expected string is byte-accurate to the wireframe. An agent must be able to execute every `[WF]` scenario without asking a question.

**`[ADMIN]` scenarios** need the real backend (persistence, toasts, sounds, printing, Slack) and are kept here as deferred runbook rows so this document survives into the production admin unchanged.

**MANDATORY — state scoping.** Both states are always present in the DOM (`.ostate{display:none}` / `.ostate.on{display:block}`). Every selector in a `[WF]` scenario **must** be prefixed with its state root, or it matches twice and the assertion is meaningless:

| State | Root selector | Visible when |
|---|---|---|
| State 1 · Processing | `#st-normal ` | `document.querySelector('#st-normal').classList.contains('on')` |
| State 2 · On Hold | `#st-hold ` | `document.querySelector('#st-hold').classList.contains('on')` |
| M3 modal | `#m-del ` | `document.querySelector('#m-del').classList.contains('open')` |

Example of the trap: `document.querySelectorAll('.c-item')` returns **4** (two per state); `document.querySelectorAll('#st-normal .c-item')` returns **2**. Where a scenario below says "the thread contains exactly 2 rows", the assertion is against the state-scoped selector.

**Preconditions for every `[WF]` scenario:** fresh page load, annotations visible (the wf-bar button reads `Hide annotations`), active tab `1 · Processing (default)` unless the scenario says otherwise. Switching state tabs scrolls to top and moves the `on` class; treat each scenario as starting from a fresh load.

**MANDATORY — text extraction and string comparison.** §8's assertions are byte-level, so how the text is extracted decides the verdict. These four rules are part of the contract, not the runner's private convention; a runner that skips them reports failures against a correct wireframe.

| Rule | Contract |
|---|---|
| **1 · Strip annotation text** | The purple `.dot` spans live **inside** asserted elements. Remove every `.dot` descendant's text before comparing (`clone = el.cloneNode(true); clone.querySelectorAll('.dot').forEach(d => d.remove())`). Without this, `Are you sure?` reads `Are you sure?✕`-style pollution: measured examples are `Product Name` → `Product Name11`, `Inventory` → `Inventory10`, `…to ship` → `…to ship14`, `…4:51:40 AM)` → `…4:51:40 AM)6`, `Egita` → `Egita ✎ Edit5`, `Bulk Inbound Selected Items` → `Bulk Inbound Selected Items2`. |
| **2 · Normalize whitespace** | Replace `<br>` with a single space, collapse runs of whitespace, trim: `.replace(/\s+/g,' ').trim()`. Four `.litable` headers are two-line markup (`Latest<br>Inventory Count`, `Inbound<br>Status`, `Sourcing<br>Route`, `Product<br>Cost 🤖`) and raw `textContent` yields `LatestInventory Count`. |
| **3 · Two string registers, explicitly** | **`reads exactly` / `text is exactly` / `value is`** = strict equality after rules 1–2. **`reads` / `contains` / `begins with`** = substring (or prefix) after rules 1–2. Every clause in §8 uses one of these verbs deliberately. |
| **4 · Element-scoped, not subtree-scoped, where a clause says so** | Where a clause names a child (`its first text node`, `the `.x` control`), assert against that node, not the parent's flattened text. |

*(These rules affect `QA-DEL-1`, `QA-REN-1`, `QA-REN-9`, `QA-SUB-3`, `QA-INB-4`, `QA-HUB-1`, `QA-OUT-2` and `QA-STA-5` — eight scenarios that flip verdict on the extraction method alone. Rule 1 is a **text-extraction** rule, not a precondition change: annotations stay visible for the whole run, exactly as the precondition above requires, and `QA-MAP-1` / `QA-MAP-4` still assert the dots as elements.)*

**Wireframe demo limitations — never file these as bugs** (they are *why* a scenario is `[ADMIN]`): no toasts, no Web Audio, no server, and no working handler on the status-dropdown items, `Mark all read`, per-row `Inbound` / `Cancel Inbound`, `Bulk Inbound Selected Items`, `📦 Outbound`, `🖨 Print`, `View Label`, `✓` / `✕` row save-cancel, `Today`, `M3 Delete`, `+ Add Line Item`, or any subbar button. Also never file the three Actor Log demo-data inconsistencies listed in §2.5 B.

Scenarios marked **· NEGATIVE** assert that something must *not* happen.

---

### QA-MAP — wireframe map, annotations and state switching `[G-12]` §2.1 §2.2

**QA-MAP-1 §2.1 — the declared unit count is verifiable on the page. [WF]**
- **Given** a fresh load with annotations visible
- **Then** `#st-normal .dot` returns **13** elements whose texts are exactly `1`–`13` (no `14`)
- **And** `#st-hold .dot` returns **14** elements whose texts are exactly `1`–`14`
- **And** `#m-del .dot` returns **1** element whose text is exactly `M3`
- **And** `.dot` (unscoped) returns **28**
- **And** `.legend ol li` returns **14**, whose `.n` values in DOM order are exactly `1, 2, 3, 4, 5, 6, 12, 10, 11, 14, 13, 9, 7, 8`
- *(These five numbers are the machine form of the §2.1 declaration: 14 numbered units + M3 = 15 legend units.)*

**QA-MAP-2 §2.2 — the wf-bar renders four controls in DOM order. [WF]**
- **Then** `.wf-bar h1` reads exactly `WMS 2.0 · Order Detail Wireframe`
- **And** `.wf-bar .hint` reads exactly `v1 — Based on the live admin (Order #407847) · Purple numbers = new/changed annotations`
- **And** the wf-tab buttons, in DOM order, read exactly `Modal: Delete Line`, `1 · Processing (default)`, `2 · On Hold`, followed by the toggle `Hide annotations`
- **And** `1 · Processing (default)` carries class `on`.

**QA-MAP-3 §2.2 — exactly one state is visible at a time. [WF]**
- **Then** on load, `#st-normal` carries class `on` and `#st-hold` does not
- **When** I scroll the window down to `y = 600` (so the scroll assertion below is not vacuous — on a fresh load `scrollY` is already `0`), **then** click the wf-tab `2 · On Hold`
- **Then** `#st-hold` carries class `on`, `#st-normal` does **not** · NEGATIVE, the tab `2 · On Hold` carries class `on`, `1 · Processing (default)` does not, and `window.scrollY` is `0`
- **When** I click `1 · Processing (default)`
- **Then** the classes swap back. *(No event is persisted for any of this — `NE-7`, `NE-13`.)*

**QA-MAP-4 §2.5 — the annotation layer is chrome, not product. · NEGATIVE [WF]**
- **When** I click `#annoToggle`
- **Then** its text becomes exactly `Show annotations`, `body` gains class `no-anno`, and **no** `.dot` and **no** `.legend` is visible
- **When** I click it again
- **Then** the text returns to `Hide annotations` and the dots and legend are visible again. *(The wf-bar, legend and dots do not exist in the production admin — `NE-13`.)*

**QA-MAP-5 §2.3 — the legend text matches the spec's headline map. [WF]**
- **Then** `.legend h3` reads exactly `Order Detail — Changes (specs 0 · A · C applied)`
- **And** the legend item numbered `9` contains the strings `"Outbound to Deleo BaroShip"`, `Outbound`, and `Enabled only when every item is INBOUNDED`
- **And** the legend item numbered `14` contains the string `combined case of Hold + incomplete inbound (3/4)`
- **And** the legend item numbered `10` contains the string `Latest Inventory Count kept`.

**QA-MAP-6 §2.2 — every legend dot has a spec section. [WF]**
- **Then** for each of the 14 legend numbers and for `M3`, this spec's §2.3 table contains a row mapping it to a `§3 [L-n]` heading, and each of those 15 headings exists in §3. *(Static cross-check of the 1:1 map; run as a document lint, not a browser action.)*

---

### QA-CMT — Operator Comments `[L-1]`

**QA-CMT-1 `[L-1]` `[L-F16]` — the composer renders with the exact placeholder and buttons. [WF]**
- **Given** state `1 · Processing`
- **Then** `#st-normal .cmt-new textarea` has placeholder exactly `Write a comment — @name to notify via Slack (order no. · text · time · author included). Per-order history accumulates here.`
- **And** `#st-normal #addCmt` is labelled exactly `Add Comment`
- **And** the `💬 Operator Comments` section header contains a button labelled exactly `Hide Comments`.

**QA-CMT-2 `[L-1]` — the seeded thread renders author, @mention highlight, timestamp and star. [WF]**
- **Then** `#st-normal .cmt-list .c-item` returns exactly **2** rows
- **And** row 1 has `.who` = `Dean`, a `span.at` reading exactly `@Yongwon`, body text `Please pack this order with extra care — repeat-purchase VIP customer.`, and `<time>` = `07-13 10:42`
- **And** row 2 has `.who` = `Yongwon`, `span.at` = `@Dean`, `<time>` = `07-13 10:55`, and its `.star` carries class `on`
- **And** row 1's `.star` does **not** carry class `on` · NEGATIVE.

**QA-CMT-3 `[L-1]` — posting a comment appends it without a page refresh. [WF]**
- **When** I type `Checked the sachet count` into `#st-normal .cmt-new textarea` and click `#st-normal #addCmt`
- **Then** `#st-normal .cmt-list .c-item` returns **3** rows, and the **last** row has `.who` = `Yongwon`, body `Checked the sachet count`, `<time>` = `Just now`
- **And** `#st-normal .cmt-new textarea` value is empty
- **And** the page did not navigate or reload (`#st-normal` still carries class `on`, the wf-tab `1 · Processing (default)` is still `on`)
- **And** `#st-hold .cmt-list .c-item` still returns **2** — the append is state-local, not global · NEGATIVE.

**QA-CMT-4 `[L-1]` `[E-27]` — an empty comment is a no-op. · NEGATIVE [WF]**
- **Given** `#st-normal .cmt-new textarea` is empty
- **When** I click `#st-normal #addCmt`
- **Then** `#st-normal .cmt-list .c-item` still returns exactly **2** rows
- **When** I type three space characters and click `#addCmt` again
- **Then** it still returns exactly **2** rows. *(No `DC-26` may be persisted in either case — `NE-12`.)*

**QA-CMT-5 `[L-1]` — @mention tokens are parsed and highlighted on post. [WF]**
- **When** I type `@Dean please double-bag this` and click `#st-normal #addCmt`
- **Then** the new `.c-item` contains a `span.at` whose text is exactly `@Dean`, and the remaining text `please double-bag this` is **not** inside a `span.at` · NEGATIVE.

**QA-CMT-6 `[L-1]` — the star toggles in the thread. [WF]**
- **Given** `#st-normal .cmt-list .c-item:nth-child(1) .star` without class `on`
- **When** I click it → it gains class `on`
- **When** I click it again → class `on` is removed.

**QA-CMT-7 `[L-1]` — the composer exists identically in the On Hold state. [WF]**
- **Given** the wf-tab `2 · On Hold`
- **Then** `#st-hold .cmt-new textarea` has the same placeholder, `#st-hold #addCmtH` is labelled `Add Comment`, and `#st-hold .cmt-list .c-item` returns exactly **2** rows with the same authors and times as State 1.

**QA-CMT-8 `[L-1]` `[DC-26]` `[DC-27]` — posting a mention persists the comment and dispatches Slack. [ADMIN]**
- **Given** a real order and a comment body containing `@Dean`
- **When** I click `Add Comment`
- **Then** a green top-right toast reads exactly `Comment added`
- **And** a `comment.posted` event is persisted with `order_id`, `body_raw`, `mentions[]` containing Dean's user id, author and timestamp (`DC-26`)
- **And** a `comment.mention_notified` event is persisted carrying `channel_id=C0BMGEWM5QA`, the Slack `message_ts` and `delivery_result` (`DC-27`)
- **And** the Slack message body @mentions Dean and contains the order no., the comment text, the time, the author and a deep link to this order.

**QA-CMT-9 `[L-1]` `[E-28]` — an unresolved mention posts as plain text and sends nothing. · NEGATIVE [ADMIN]**
- **When** I post `@NotAUser check this`
- **Then** `DC-26` persists with `mentions[]` **empty** and `unresolved_mention_tokens[]` containing `NotAUser`
- **And no** `comment.mention_notified` event exists for it, **and no** Slack message is sent.

**QA-CMT-10 `[L-1]` `[E-60]` — a self-mention suppresses the Slack dispatch. · NEGATIVE [ADMIN]**
- **Given** I am logged in as Yongwon
- **When** I post `@Yongwon reminder to myself`
- **Then** the comment persists normally (`DC-26`), **and** `DC-27` persists with `suppressed_reason=self_mention`, **and no** Slack message is delivered.

**QA-CMT-11 `[L-1]` `[E-80]` `[E-81]` — duplicate mentions notify once; a mention-only body is valid. [ADMIN]**
- **When** I post `@Dean @Dean please check`
- **Then** `DC-26.mentions[]` contains Dean **once**, exactly **one** `DC-27` is persisted and exactly **one** Slack message is delivered · NEGATIVE
- **When** I post a body consisting only of `@Dean`
- **Then** the comment persists and notifies normally — an empty-body guard must not reject it.

**QA-CMT-12 `[L-1]` `[E-29]` — a Slack failure never rolls back the comment. · NEGATIVE [ADMIN]**
- **Given** the Slack integration is unreachable
- **When** I post a comment containing a valid `@mention`
- **Then** the comment is visible in the thread and persisted (`DC-26`), **and** `DC-27` records the failed `delivery_result` with `attempt_no`, **and** no error dialog blocks the UI, **and** the comment is **not** removed or rolled back.

**QA-CMT-13 `[L-1]` `[E-30]` — comment bodies are escaped, never executed. · NEGATIVE [ADMIN]**
- **When** I post `<img src=x onerror=alert(1)> & "quoted"`
- **Then** the stored `body_raw` is verbatim, the rendered thread shows the literal characters, **no** script executes, and the same escaping holds in the Comments hub list and in hub search results.

**QA-CMT-14 `[L-1]` `[DC-28]` `[DC-29]` — starring persists per user and syncs to the hub. [ADMIN]**
- **When** I click the `★` on a thread comment
- **Then** `comment.starred` persists with `comment_id`, my `user_id` and `false → true` (`DC-28`), **and** that comment appears in the hub's `★ Saved` tab
- **When** I click it again
- **Then** `comment.unstarred` persists (`DC-29`) and the comment leaves the Saved tab
- **And** another user's Saved tab is unaffected by either action · NEGATIVE.

**QA-CMT-15 `[L-1]` `[E-79]` `[BR-11]` — comments are append-only and never gated by order state. · NEGATIVE [ADMIN]**
- **Then** no comment in the thread exposes an edit control or a delete control, in any order state · NEGATIVE
- **When** I open a **cancelled** order and post a comment
- **Then** it persists normally (`DC-26`) — commentability is not gated by order state.

**QA-CMT-16 `[L-1]` `[L-7]` `[E-34]` `[E-35]` `[DC-28]` `[DC-29]` — star races settle consistently and the thread never goes stale. [ADMIN]**
- **When** I toggle the same comment's `★` rapidly from the thread and from the hub's `★ Saved` pane in an interleaved sequence
- **Then** the final state is the same in both surfaces (last write wins on the `user_id` + `comment_id` key), **and** every toggle persisted in order as `DC-28` / `DC-29` — the corpus keeps the flip-flop rather than collapsing it · NEGATIVE
- **And** another user's Saved tab is unaffected · NEGATIVE
- **Given** another operator posts a comment on this order while my page is open
- **Then** the thread does **not** stay stale: at minimum it refreshes on my next action on the page, and the new comment appears without a full-page reload `[G-2]`. *(Poll vs push is dev-time, §9.4 D-6; the minimum above is the assertable contract.)*

---

### QA-HUB — Comments hub `[L-7]`

**QA-HUB-1 `[L-7]` — the hub opens with the expected chrome. [WF]**
- **When** I click `#st-normal .icon-btn[data-open="inbox1"]` (visible label `💬 Comments`)
- **Then** `#inbox1` gains class `open`
- **And** `#inbox1 .csearch input` has placeholder exactly `🔍 Search all comments — order no. · author · text`
- **And** `#inbox1 .tabs button` returns 2 buttons whose labels **begin with** `@ Mentions` and `★ Saved`, with the `@ Mentions` button carrying class `on` (the Mentions tab carries an inline `.badge-n` child, so its flattened label is `@ Mentions 2`; the badge value is asserted by `QA-HUB-2`)
- **And** `#inbox1 [data-pane="mentions"] .paneheader` reads `Comments mentioning me · Click to open the order` and contains a `Mark all read` action.

**QA-HUB-2 `[L-7]` `[BR-44]` — the unread badge and unread styling. [WF]**
- **Then** `#st-normal .icon-btn[data-open="inbox1"] .badge-n` reads exactly `2`
- **And** the `@ Mentions` tab's inline `.badge-n` reads exactly `2`
- **And** `#inbox1 [data-pane="mentions"] .it.unread` returns exactly **2**
- **And** the third item (`Order 407790 · Kai: "Resolved"`, time `Yesterday`) does **not** carry class `unread` · NEGATIVE
- *(A badge of `3` is a regression — corrected 2026-08-02, §10.3 chain 6.)*

**QA-HUB-3 `[L-7]` — the Saved tab shows only starred comments. [WF]**
- **When** I click the `★ Saved` tab
- **Then** `#inbox1 [data-pane="saved"]` is visible, its `.paneheader` reads `Saved comments · Click to open the order` with `Unstar to remove`
- **And** it contains exactly **1** `.it`: `Order 407812 · Miranti: "@Yongwon 1 JIT item not yet inbounded"`, whose `.star` carries class `on`
- **And** `#inbox1 [data-pane="mentions"]` is hidden · NEGATIVE.

**QA-HUB-4 `[L-7]` `[E-31]` `[E-32]` — all-orders search: match, highlight, no-match, restore. [WF]**
- **Given** `#inbox1` is open with `@ Mentions` active
- **When** I type `miranti` into `#inbox1 .csearch input`
- **Then** `#inbox1 .tabs` has `display:none`, **and** a pane `[data-pane="csr"]` is visible whose `.paneheader` reads exactly `1 results · newest first · click to open the order`, containing one `.it` with `Order 407812` and the text `Miranti` wrapped in `<mark>`
- **When** I replace the query with `zzzz`
- **Then** the pane contains exactly `No matching comments` and zero `.it` elements · NEGATIVE
- **When** I clear the input
- **Then** `#inbox1 .tabs` is visible again, `@ Mentions` still carries class `on`, and its pane is visible.

**QA-HUB-5 `[L-7]` — the search scope is all orders, not the current tab. [WF]**
- **When** I type `407301` into `#inbox1 .csearch input`
- **Then** the results header reads exactly `1 results · newest first · click to open the order` and the item shows `Order 407301 · Dean: "Repacked and shipped"` — an order that appears in **neither** the Mentions nor the Saved tab, proving the search is cross-order and not a tab filter.

**QA-HUB-6 `[L-7]` — search matches on author and on body, newest first. [WF]**
- **When** I type `sachet`
- **Then** the header reads `1 results · newest first · click to open the order` and the single item is `Order 407688 · Aldo: "Customer note checked — sachet included"` with `sachet` inside `<mark>`
- **When** I type `dean`
- **Then** the header reads `2 results · newest first · click to open the order` and the items appear in this order: `Order 407847` first, `Order 407301` second.

**QA-HUB-7 `[L-7]` `[E-30]` — hub search escapes before it highlights. · NEGATIVE [WF]**
- **When** I type `<` into `#inbox1 .csearch input`
- **Then** the pane renders `No matching comments` (no seeded comment contains `<`) and **no** raw `<` is injected into the DOM as markup — the rendered pane contains no unexpected element. *(The wireframe's `esc()` runs before `hl()`; the production render must keep that order.)*

**QA-HUB-8 `[L-7]` — the hub exists identically in the On Hold state. [WF]**
- **Given** the wf-tab `2 · On Hold`
- **When** I click `#st-hold .icon-btn[data-open="inbox1H"]`
- **Then** `#inbox1H` opens with the same placeholder, the same two tabs, `.badge-n` = `2`, and the same three mention items.

**QA-HUB-9 `[L-7]` `[E-33]` `[DC-31]` — Mark all read clears both badges. [ADMIN]**
- **Given** the hub is open with 2 unread mentions
- **When** I click `Mark all read`
- **Then** `comment.mark_all_read` persists with the affected `comment_ids[]` and `count=2` (`DC-31`)
- **And** the nav badge and the tab badge are both cleared, **and no** item carries the `unread` style · NEGATIVE.

**QA-HUB-10 `[L-7]` `[G-12]` `[DC-30]` `[DC-34]` — clicking an item opens the entity. [ADMIN]**
- **When** I click the item `Order 407812 · Miranti: "@Yongwon 1 JIT item not yet inbounded"`
- **Then** the browser navigates to Order Detail for order `407812`
- **And** `order.detail_viewed` persists with `entry_path=comments_hub` (`DC-34`)
- **And** the mention is marked read (`DC-30`) and the badge decrements by one.

**QA-HUB-11 `[L-7]` `[PD-67 · OWNER-PENDING]` — a pool-entity hub item routes to the right screen. · NEGATIVE [ADMIN]**
- **Given** a hub item whose entity is an unrecognized-pool row
- **When** I click it while the pool row is still open
- **Then** the tracking-missing page opens focused on that row
- **When** the pool item has already been resolved
- **Then** the **matched order** opens instead — never a dead row and never a 404.

**QA-HUB-12 `[L-7]` `[E-92]` `[BR-44]` — zero unread mentions render no badge. · NEGATIVE [ADMIN]**
- **Given** a user with no unread mentions
- **Then** the nav `💬 Comments` button shows **no** `.badge-n` element at all (not a badge reading `0`)
- **And** the `@ Mentions` pane renders an explicit empty state rather than an empty box.

---

### QA-INB — Inbound controls `[L-2]`

**QA-INB-1 `[L-2]` — the per-row control renders by line status (Processing). [WF]**
- **Given** state `1 · Processing`
- **Then** `#st-normal .litable tbody tr` returns exactly **4** rows
- **And** all four rows show a `.tag.tag-inbounded` reading exactly `INBOUNDED`
- **And** rows 2, 3 and 4 each contain in their Actions cell a button labelled exactly `Cancel Inbound` with class `btn-red-line`
- **And** row 1 (SKU `100005104`) carries class `row-edit` and contains **no** `Cancel Inbound` button · NEGATIVE.

**QA-INB-2 `[L-2]` — the per-row control flips to `Inbound` for a PENDING line. [WF]**
- **Given** the wf-tab `2 · On Hold`
- **Then** the row containing SKU `100043697` shows a `.tag.tag-pending` reading exactly `PENDING`
- **And** its Actions cell contains a button labelled exactly `Inbound` with class `btn-green`, and **no** button labelled `Cancel Inbound` · NEGATIVE
- **And** the rows for SKUs `100005088` and `100012534` still show `INBOUNDED` with `Cancel Inbound`.

**QA-INB-3 `[L-2]` `[BR-40]` — the retired labels must not exist. · NEGATIVE [WF]**
- **Then** the string `Request Inbound` appears in **no** button label, **no** header cell and **no** body text inside `#st-normal` or `#st-hold`
- **And no** header cell of `.litable` reads `Inbound Request`
- *(Scope is the product surface only. The legend's item 2 contains the sentence `"Request Inbound" name retired; unclickable-button bug fixed` — that is annotation chrome `NE-13`, it is **expected**, and it is required by `QA-MAP-5`'s sibling assertion on the legend. Asserting against the whole document instead would forbid the one sentence whose job is to record the retirement, and §10.2 names this scenario as the guard for the retired label, not for the legend.)*

**QA-INB-4 `[L-2]` `[L-9]` `[L-F14]` `[L-F15]` — the footer renders four controls in order. [WF]**
- **Then** `#st-normal .li-foot` contains, left to right: the text `Total Quantity: 4`, a button labelled exactly `Bulk Inbound Selected Items`, a button labelled exactly `📦 Outbound`, and (right-aligned) a button labelled exactly `+ Add Line Item`
- **And** the same four controls, in the same order and with the same labels, exist in `#st-hold .li-foot`.

**QA-INB-5 `[L-2]` `[L-F13]` — selection checkboxes exist on every row and in the header. [WF]**
- **Then** `#st-normal .litable thead input[type=checkbox][title="Select all"]` returns exactly **1**
- **And** `#st-normal .litable tbody tr td:first-child input[type=checkbox]` returns exactly **4** — one per row.

**QA-INB-6 `[L-2]` `[DC-10]` `[DC-21]` — per-row Inbound persists the transition and the movement. [ADMIN]**
- **Given** a real order with a `PENDING` line
- **When** I click that row's `Inbound`
- **Then** `line_item.inbounded` persists with SKU, the **full line qty**, `PENDING → INBOUNDED`, actor and timestamp (`DC-10`)
- **And** `inventory.movement` persists with the signed delta, `movement_type=inbound`, `source_event_id` and `balance_after` (`DC-21`)
- **And** the row re-renders as `INBOUNDED` with `Cancel Inbound`, **and** `Latest Inventory Count` for that SKU refreshes
- **And** a green toast reads exactly `Inbounded — {SKU}`
- **And** the page does **not** refresh · NEGATIVE
- **And** the Actor Log gains one `INBOUND` row with class `act-in`.

**QA-INB-7 `[L-2]` `[E-1]` `[DC-36]` — double-click Inbound processes once. · NEGATIVE [ADMIN]**
- **When** I click a row's `Inbound` twice within 300 ms
- **Then** exactly **one** `line_item.inbounded` and **one** `inventory.movement` exist
- **And** `action.idempotency_suppressed` records the second submission with its `idempotency_key` and `delta_ms` (`DC-36`)
- **And** exactly **one** toast is shown and the Actor Log gains exactly **one** row.

**QA-INB-8 `[L-2]` `[DC-11]` — Cancel Inbound restocks and logs with the exact grammar. [ADMIN]**
- **When** I click `Cancel Inbound` on an `INBOUNDED` line, confirm, and leave the note empty
- **Then** `line_item.inbound_cancelled` persists with `INBOUNDED → PENDING`, `restock=true` and `note=""` (`DC-11`)
- **And** `inventory.movement` persists with `movement_type=cancel_inbound_restock` (`DC-21`)
- **And** the Actor Log's newest row reads exactly `CANCEL INBOUND (Restock)` with the SKU, qty, my name and `–` in the Note column, and carries class `act-cancel`
- **And** a green toast reads exactly `Inbound cancelled — {SKU} restocked`.

**QA-INB-9 `[L-2]` `[E-15]` — the note is optional but captured verbatim when given. [ADMIN]**
- **When** I cancel an inbound with the note `Corrected duplicate inbound`
- **Then** `DC-11.note` equals that string exactly and the Actor Log Note cell renders it verbatim.

**QA-INB-10 `[L-2]` `[E-10]` `[BR-14]` `[PD-10 · OWNER-PENDING]` — Cancel Inbound is blocked after outbound. · NEGATIVE [ADMIN]**
- **Given** an order that has already been outbounded
- **Then** every per-row `Cancel Inbound` button carries `disabled` and renders the visible reason `Cancel Outbound first` next to it `[BR-46]`
- **When** I force the request
- **Then** the server rejects it, **no** `line_item.inbound_cancelled` and **no** `inventory.movement` are persisted, and `order.action_rejected` persists with `reason_code=order_outbounded` (`DC-9`).

**QA-INB-11 `[L-2]` `[E-7]` — Bulk Inbound with zero selection is disabled. · NEGATIVE [ADMIN]**
- **Given** no row checkbox is checked
- **Then** `Bulk Inbound Selected Items` carries the `disabled` attribute
- **And** clicking it issues **no** request and persists **no** event.

**QA-INB-12 `[L-2]` `[E-8]` `[DC-12]` — Bulk Inbound skips already-inbounded lines idempotently. [ADMIN]**
- **Given** 3 lines selected, of which 1 is already `INBOUNDED`
- **When** I click `Bulk Inbound Selected Items`
- **Then** one `line_item.bulk_inbound_submitted` persists with `processed_count=2`, `skipped_already_inbounded_count=1` and the skipped line id (`DC-12`)
- **And** exactly **2** `line_item.inbounded` child events persist, each carrying `parent_event_id` (`DC-10`)
- **And** exactly **one** toast reads `Inbounded 2 item(s) · 1 already inbounded`
- **And no** error state is shown · NEGATIVE.

**QA-INB-13 `[L-2]` `[BR-2]` `[E-61]` — inbound stays available while On Hold. [ADMIN]**
- **Given** an order whose status is `on-hold` with a `PENDING` line
- **Then** that row's `Inbound` button is **enabled**
- **When** I click it
- **Then** the inbound commits normally (`DC-10` + `DC-21`), the order remains `on-hold`, **and** `📦 Outbound` remains disabled · NEGATIVE
- **When** another operator sets the hold while a Bulk Inbound is mid-flight
- **Then** the batch completes and **no** line is rolled back.

**QA-INB-14 `[L-2]` `[E-71]` `[BR-41]` — per-line inbound is all-or-nothing. · NEGATIVE [ADMIN]**
- **Given** a line whose ordered `Qty` is `5`
- **Then** the row's Actions cell exposes **no** quantity input and **no** partial-receive affordance · NEGATIVE
- **When** I click `Inbound`
- **Then** `DC-10.qty` equals `5` — the full line quantity — and the line's status becomes `INBOUNDED` with no intermediate PARTIAL state
- **And no** inbound-request lifecycle event is emitted from this page `[G-11]` §5.2 · NEGATIVE.

**QA-INB-15 `[L-2]` `[E-72]` — a line deleted mid-batch is skipped, not fatal. [ADMIN]**
- **Given** 3 lines selected, and another operator deletes one of them before I submit
- **When** I click `Bulk Inbound Selected Items`
- **Then** the batch commits the remaining 2, `DC-12.skipped_deleted_line_ids[]` names the deleted line, the toast subtext reports the skip, **and** the batch does **not** fail · NEGATIVE.

**QA-INB-16 `[L-2]` `[E-73]` — a partially failing batch commits what it can. [ADMIN]**
- **Given** a 10-line bulk submission where the server rejects 1 line
- **Then** 9 `line_item.inbounded` children persist, `DC-12.failed_line_ids[]` names the tenth, a **red** toast names the failed line, **and** the 9 successes are **not** rolled back · NEGATIVE.

**QA-INB-17 `[L-2]` `[E-3]` `[G-9]` `[DC-36]` — double-click Bulk Inbound processes the selection once. · NEGATIVE [ADMIN]**
- **Given** 3 `PENDING` lines selected
- **When** I click `Bulk Inbound Selected Items` twice within 300 ms
- **Then** exactly **one** `line_item.bulk_inbound_submitted` exists (`DC-12`) and exactly **3** `line_item.inbounded` children (`DC-10`) — **not** 6 · NEGATIVE
- **And** exactly **3** `inventory.movement` rows exist (`DC-21`), exactly **one** toast is shown, and the Actor Log gains exactly **3** rows
- **And** `action.idempotency_suppressed` records the second submission with its `idempotency_key` and `delta_ms` (`DC-36`).

**QA-INB-18 `[L-2]` `[E-9]` `[PD-6 · OWNER-PENDING]` `[PD-7 · OWNER-PENDING]` `[DC-37]` — a stale row is rejected, never double-received. · NEGATIVE [ADMIN]**
- **Given** operator B inbounded a line one second before operator A clicks `Inbound` on the same row
- **When** A's request reaches the server
- **Then** it is rejected: **no** second `line_item.inbounded` and **no** second `inventory.movement` are written · NEGATIVE
- **And** `entity.version_conflict` persists with `entity_type=line_item`, both versions and `attempted_action=line_item.inbounded` (`DC-37`)
- **And** A's row re-renders as `INBOUNDED` with `Cancel Inbound`, and a **non-green** toast states the line was already inbounded — never a green success toast.

---

### QA-OUT — Outbound gating `[L-9]` `[L-14]`

**QA-OUT-1 `[L-9]` — enabled rendering when the gate is clear. [WF]**
- **Given** state `1 · Processing`, where all four lines show `INBOUNDED`
- **Then** `#st-normal #obBtn` has visible label exactly `📦 Outbound`, carries class `btn-green`, and does **not** carry the `disabled` attribute · NEGATIVE.

**QA-OUT-2 `[L-9]` `[L-14]` `[E-13]` — disabled rendering, and the disable has two independent causes. [WF]**
- **Given** the wf-tab `2 · On Hold`
- **Then** `#st-hold .li-foot button.btn-gray` has visible label exactly `📦 Outbound`, carries the `disabled` attribute, inline `opacity:.55` and `cursor:not-allowed`, and carries **no** `id` · NEGATIVE
- **And** `#holdBannerH` is visible containing exactly `⏸ On Hold by urgent CS request — inbound still allowed, but Outbound disabled. Release the hold (Change Status) to ship`
- **And** the row with SKU `100043697` shows `PENDING` with a green `Inbound` button — proving both gates (hold **and** 3/4 inbound) block simultaneously `[BR-3]`.

**QA-OUT-3 `[L-9]` `[BR-40]` — the relabel is complete. · NEGATIVE [WF]**
- **Then** **no button label** in either state reads `Outbound to Deleo BaroShip`, and the string appears in **no** body text inside `#st-normal` or `#st-hold`
- **And** both footer buttons' visible label is exactly `📦 Outbound`
- *(The legend's item 9 quotes the old label historically — `"Outbound to Deleo BaroShip" → relabeled to "Outbound"`. That occurrence is **expected** and is explicitly **required** by `QA-MAP-5`; the two scenarios must both pass. Scope this assertion to the product surface, never to the annotation layer `NE-13`.)*

**QA-OUT-4 `[L-9]` `[DC-19]` `[DC-21]` — Outbound persists a gate snapshot and one aggregate log row. [ADMIN]**
- **Given** a real order in `processing` with every line `INBOUNDED`
- **When** I click `📦 Outbound`
- **Then** the send sound plays exactly once `[G-3]`(a) `[PD-2 · OWNER-PENDING]`
- **And** `order.outbounded` persists with all SKUs and quantities, the carrier, and `gate_snapshot{all_lines_inbounded:true, order_status:"processing", line_count:4}` (`DC-19`)
- **And** `inventory.movement` rows persist with `movement_type=outbound` (`DC-21`)
- **And** the status becomes `prepare-shipment`
- **And** a green toast reads exactly `Outbound sent — 4 item(s)`
- **And** the Actor Log gains exactly **one** row reading `OUTBOUND` / `All (4 SKU)` / `4` with class `act-out`
- **And** the page does **not** refresh · NEGATIVE.

**QA-OUT-5 `[L-9]` `[E-2]` `[DC-36]` — double-click Outbound ships once and sounds once. · NEGATIVE [ADMIN]**
- **When** I click `📦 Outbound` twice within 300 ms
- **Then** exactly **one** `order.outbounded` exists, exactly **one** set of movements exists, the send sound plays exactly **once**, exactly **one** Actor Log row is added, and `action.idempotency_suppressed` records the second click (`DC-36`).

**QA-OUT-6 `[L-9]` `[E-12]` `[BR-5]` `[C-7]` — completing inbound never auto-ships. · NEGATIVE [ADMIN]**
- **Given** an order with one `PENDING` line and status `processing`
- **When** I inbound that last line
- **Then** `📦 Outbound` becomes enabled, **and no** `order.outbounded` event is created, **and** the order status stays `processing`, **and no** send sound plays, **and no** Actor Log `OUTBOUND` row appears. Shipping requires an explicit click `[PD-21 · OWNER-PENDING]`.

**QA-OUT-7 `[L-9]` `[E-16]` `[PD-29 · OWNER-PENDING]` — the status-based blocking matrix, all 8 cases. · NEGATIVE [ADMIN]**
- **Given** an order with every line `INBOUNDED` and ≥1 line
- **Then** assert individually: `📦 Outbound` is **enabled** for `processing`; **enabled** for `pending`; **disabled** for `on-hold`; **disabled** for `refunded`; **disabled** for `failed`; **disabled** for `completed`; **disabled** for `shipped`; **disabled** for `prepare-shipment`
- **And** each disabled case renders its blocking reason next to the button `[BR-46]`, and a forced attempt persists `DC-9` with `reason_code` ∈ {`hold_blocks_outbound`, `status_blocks_outbound`}.

**QA-OUT-8 `[L-9]` `[E-11]` — the gate is re-evaluated server-side at commit. · NEGATIVE [ADMIN]**
- **Given** operator A has `📦 Outbound` enabled on screen
- **When** operator B cancels an inbound on that order and operator A then clicks Outbound
- **Then** the server rejects the request, **no** `order.outbounded` and **no** movements are written, a **red** toast names the line that is no longer inbounded, the footer re-renders disabled, and `order.action_rejected` (`DC-9`, `reason_code=stale_entity`) plus `entity.version_conflict` (`DC-37`) are persisted.

**QA-OUT-9 `[L-9]` `[E-55]` `[BR-17]` — a 0-line order cannot ship. · NEGATIVE [ADMIN]**
- **Given** an order whose lines have all been deleted
- **Then** `Total Quantity: 0` renders, the line table shows its empty state, and `📦 Outbound` is disabled; a forced attempt persists `DC-9` with `reason_code=no_lines`.

**QA-OUT-10 `[L-9]` `[BR-19]` `[E-51]` `[DC-20]` — Cancel Outbound rolls back and re-enables per-row cancel. [ADMIN]**
- **Given** an outbounded order (status `prepare-shipment`)
- **Then** the footer offers `Cancel Outbound` **in place of** `📦 Outbound`
- **When** I click it and confirm
- **Then** `order.outbound_cancelled` persists with `prepare-shipment → processing` (`DC-20`), reversal movements persist with `movement_type=cancel_outbound_reversal` (`DC-21`), a green toast reads exactly `Outbound cancelled`, the Actor Log gains `CANCEL OUTBOUND` / `All (4 SKU)`, **and** per-row `Cancel Inbound` buttons become enabled again `[BR-14]`.

**QA-OUT-11 `[L-9]` `[E-86]` `[PD-55 · NO-DEFAULT]` — a carrier-less order blocks outbound and print. · NEGATIVE [ADMIN]**
- **Given** an order flagged "Not connected — contact the Fulfillment Center" with no carrier
- **Then** `📦 Outbound` and `🖨 Print` are both disabled with that state as the visible reason, and forced attempts persist `DC-9` with `reason_code=no_carrier`
- **And** the page exposes **no** manual carrier-assignment control — none is specified until the owner decides `[PD-55 · NO-DEFAULT]` · NEGATIVE.

**QA-OUT-12 `[L-9]` `[E-74]` `[E-75]` — server error and offline both fail loudly, never optimistically. · NEGATIVE [ADMIN]**
- **Given** the server returns 500 on the outbound call
- **Then** a red toast names the failure, the status does **not** advance to `prepare-shipment`, the Actor Log gains **no** row, and the client retains the idempotency key for a retry
- **Given** the browser is offline
- **When** I click `📦 Outbound`
- **Then** the action is refused immediately with a red toast (`No connection — action not sent`) and **nothing** is queued silently.

**QA-OUT-13 `[L-9]` `[L-8]` `[E-14]` `[E-52]` `[E-67]` `[PD-74 · NO-DEFAULT]` — the hold/outbound race and the post-closing reversal both resolve without a partial write. · NEGATIVE [ADMIN]**
- **Given** an Outbound request is in flight and another operator sets the status to `on-hold` in the same moment
- **Then** the server resolves the two atomically and exactly one of these holds, never a mixture · NEGATIVE:
  - if the outbound commits first, it stands and the hold applies to an already-outbounded order (`DC-1` + `DC-2`, nothing recalled `[E-67]`);
  - if the hold commits first, the outbound is rejected with `order.action_rejected`, `reason_code=hold_blocks_outbound` (`DC-9`), and **no** `order.outbounded` and **no** `inventory.movement` are written
- **And** in both branches the persisted record is complete — there is **no** partial outbound and **no** orphaned movement · NEGATIVE
- **Given** an order whose parcel was already scanned at a **confirmed** Closing session
- **When** I click `Cancel Outbound` and confirm
- **Then** the reversal is allowed at the data layer and fully persisted (`DC-20` + reversal `DC-21`), so the Closing snapshot and this order disagree **visibly** rather than silently
- **And** this page offers **no** affordance to amend or reopen the closing session — reconciling it is a Closing concern with no decided path `[PD-74 · NO-DEFAULT]` · NEGATIVE.

---

### QA-STA — Change Status & Hold `[L-8]` `[L-14]`

**QA-STA-1 `[L-8]` — the dropdown lists exactly 8 statuses in order. [WF]**
- **When** I click `#st-normal button[data-open="statusdd"]` (visible label `Change Status ▾`)
- **Then** `#statusdd` becomes visible and its child `div` elements read, in this exact order: `pending`, `processing`, `on-hold`, `completed`, `refunded`, `failed`, `shipped`, `prepare-shipment` — exactly **8**
- **And** the `processing` item carries class `on`.

**QA-STA-2 `[L-8]` `[BR-12]` — `cancelled` is not a status value. · NEGATIVE [WF]**
- **Then** `#statusdd` contains **no** item reading `cancelled` or `cancel`
- **And** a separate subbar button labelled exactly `✕ Cancel Order` exists with class `link-btn red`.

**QA-STA-3 `[L-8]` `[L-14]` — the On Hold state highlights `on-hold`. [WF]**
- **Given** the wf-tab `2 · On Hold`
- **When** I click `#st-hold button[data-open="statusddH"]`
- **Then** `#statusddH` is visible, its `on-hold` item carries class `on`, and its `processing` item does **not** · NEGATIVE.

**QA-STA-4 `[L-8]` `[E-46]` `[OD-WFX-1 · proposed]` — clicking outside closes the dropdown with no change. · NEGATIVE [ADMIN]**
- **Given** `#statusdd` is open
- **When** I click the page background
- **Then** the dropdown is no longer visible, the status badge still reads `Processing`, and no toast appears. *(No event — `NE-2`.)*
- **Tier reason (one line):** `[ADMIN]` because the wireframe has **no document-level click handler** — measured 2026-08-03: the dropdown stays open after a background click, while the modal's three dismissal paths all work. The specified behavior is unchanged and correct; the drawing is missing the affordance, registered as `[OD-WFX-1 · proposed]` in `_wireframe-fixes.md` §I and listed in §2.5 A and §9.5. **Do not file this as a spec bug and do not "fix" the spec to match the drawing.** Once `[OD-WFX-1 · proposed]` is applied, this scenario becomes `[WF]` unchanged.

**QA-STA-5 `[L-14]` — the status badge and hold banner render per state. [WF]**
- **Given** state `1 · Processing`
- **Then** `#st-normal #ordStatus` reads exactly `Processing` with class `st-processing`, and `#st-normal` contains **no** hold banner element · NEGATIVE
- **Given** state `2 · On Hold`
- **Then** `#st-hold .status` reads exactly `On Hold` with class `st-hold`, and `#holdBannerH` is visible with the exact banner copy.

**QA-STA-6 `[L-14]` — the six State-2 diffs and nothing else. [WF]**
- **Comparison basis (mandatory):** compare the **normalized visible text** of each named block (§8.0 rules 1–2: `.dot` text removed, whitespace collapsed), **not** the DOM, **not** attributes. The id diff in item (6) is asserted separately as an explicit id-set comparison, because it is the one structural difference the rest of §8 depends on.
- **Given** both states
- **Then** exactly these differ: (1) the status badge text/class; (2) the presence of `#holdBannerH`; (3) which `.statusdd div` carries class `on`; (4) the footer Outbound button's `disabled`/`btn-gray` state and its missing `id`; (5) row 2's tag (`INBOUNDED` vs `PENDING`) and its Actions button (`Cancel Inbound` vs `Inbound`); **(6) the state-suffixed element ids — `inbox1`/`inbox1H`, `statusdd`/`statusddH`, `addCmt`/`addCmtH` — plus `#ordStatus` and `#obBtn`, which exist only in State 1, and `#holdBannerH`, which exists only in State 2**
- **And** by the comparison basis above, the nav, subbar, address panels, comments thread, Fulfillment Tracking block, Actor Log rows and the other three line rows are textually identical between `#st-normal` and `#st-hold` · NEGATIVE (nothing else changes)
- *(Diff 6 is why `QA-HUB-8`, `QA-STA-3` and `QA-CMT-7` use the `H`-suffixed ids. State 2's status badge has **no** id, which is why `QA-STA-5` switches to `#st-hold .status`.)*

**QA-STA-7 `[L-8]` `[DC-1]` `[DC-2]` — a status change persists old→new and toasts. [ADMIN]**
- **When** I pick `on-hold` from the dropdown
- **Then** `order.status_changed` persists with `old_status=processing`, `new_status=on-hold`, `source=detail-dropdown`, actor and timestamp (`DC-1`)
- **And** `order.hold_placed` persists with `previous_status` and the optional `hold_reason` (`DC-2`)
- **And** a green toast reads exactly `Status changed to on-hold`
- **And** the badge, banner and Outbound gate all update **without a page refresh** · NEGATIVE.

**QA-STA-8 `[L-8]` `[BR-13]` `[PD-28 · OWNER-PENDING]` — destructive statuses require confirmation. · NEGATIVE [ADMIN]**
- **When** I pick `refunded` (then separately `failed`, then separately `completed`)
- **Then** a confirm dialog appears **before** anything is applied, and its copy names the specific consequence
- **When** I dismiss it
- **Then** the status is unchanged and **no** `order.status_changed` event exists `NE-15`
- **When** I pick `pending` (a non-destructive value)
- **Then** it applies immediately with **no** confirm dialog.

**QA-STA-9 `[L-8]` `[E-5]` — re-selecting the current status is a no-op. · NEGATIVE [ADMIN]**
- **Given** the status is `processing`
- **When** I pick `processing`
- **Then** **no** event is persisted, **no** toast appears, and the badge does not flicker `NE-11`.

**QA-STA-10 `[L-8]` `[DC-3]` — releasing the hold persists a first-class event. [ADMIN]**
- **Given** the order is `on-hold`
- **When** I pick `processing`
- **Then** `order.status_changed` (`DC-1`) **and** `order.hold_released` with `hold_duration_seconds` (`DC-3`) both persist, the banner disappears, and the Outbound gate re-evaluates against inbound completeness alone.

**QA-STA-11 `[L-8]` `[E-66]` — manual `shipped` fabricates nothing. · NEGATIVE [ADMIN]**
- **Given** an order with no outbound event
- **When** I set the status to `shipped`
- **Then** `order.status_changed` persists, **and no** `order.outbounded`, **no** `inventory.movement` and **no** Actor Log `OUTBOUND` row are created.

**QA-STA-12 `[L-8]` `[L-14]` `[BR-24]` `[E-67]` — hold reason is optional, persisted and rendered. [ADMIN]**
- **When** I set `on-hold` **without** entering a reason
- **Then** the change commits (`DC-1` + `DC-2` with `hold_reason` absent) and the banner renders its default copy — the reason is never mandatory · NEGATIVE
- **When** I set `on-hold` **with** the reason `Customer requested address change`
- **Then** `DC-2.hold_reason` equals that string and the banner renders it in place of the "by urgent CS request" clause
- **When** I place a hold on an **already-outbounded** order
- **Then** `DC-1` + `DC-2` persist, the banner renders, **and no** shipment is recalled and **no** inventory movement occurs `[E-67]` · NEGATIVE.

---

### QA-EDIT — Line edit `[L-12]`

**QA-EDIT-1 `[L-12]` — edit mode renders exactly the 5 whitelisted inputs. [WF]**
- **Given** state `1 · Processing`, row 1 (SKU `100005104`), which is pre-rendered in edit mode
- **Then** `#st-normal tr.row-edit input.ed-in` returns exactly **5** elements, whose values are, in DOM order: `12101316464794`, `2026-06-30`, `15000`, `10323100835644`, `https://www.coupang.com/vp/products/7055479133?itemId=17506867787`
- **And** `#st-normal tr.row-edit button.ed-today` exists with text exactly `Today`, positioned under the date input.

**QA-EDIT-2 `[L-12]` — Actions switch to ✓ / ✕ in edit mode. [WF]**
- **Then** `#st-normal tr.row-edit .act-ic button.ok` reads exactly `✓` and `#st-normal tr.row-edit .act-ic button.no` reads exactly `✕`
- **And** that Actions cell contains **no** `Cancel Inbound` button, **no** `.edit` button and **no** `.del` button · NEGATIVE.

**QA-EDIT-3 `[L-12]` `[BR-25]` — commerce fields are not editable. · NEGATIVE [WF]**
- **Then** within `#st-normal tr.row-edit`, the cells rendering `SKU`, `Product Name`, `Product Name KR`, `Size`, `Qty`, `Subtotal`, `Total`, `Latest Inventory Count`, `Inbound Status` and `Sourcing Route` contain **no** `input` element — only the 5 agent-tracking cells do.

**QA-EDIT-4 `[L-12]` — non-edit rows render read-only values in the same field order. [WF]**
- **Given** the row with SKU `100043697` in `#st-normal`
- **Then** its Inventory cells read, in order: `0`, `INBOUNDED`, `JIT (Coupang)`, `12101316464794`, `2026-06-30`, `₩17,100`, `10323100835456`, and a link reading `coupang…7923`
- **And** none of those cells contains an `input` · NEGATIVE.

**QA-EDIT-5 `[L-12]` — the edit affordance exists on every non-edit row. [WF]**
- **Then** each of `#st-normal .litable tbody tr:not(.row-edit)` contains, in its Actions cell, a `button.edit` reading `✎` and a `button.del` reading `🗑` with `data-modal="m-del"`.

**QA-EDIT-6 `[L-12]` `[DC-13]` — Save persists only the changed fields. [ADMIN]**
- **When** I change `Product Cost` from `15000` to `16000`, leave the other four untouched, and click `✓`
- **Then** `line_item.edited` persists with `field_diff` containing **only** `product_cost: {old:15000, new:16000}` (`DC-13`) — the four untouched fields are absent from the diff · NEGATIVE
- **And** a green toast reads exactly `Line item updated`, the row exits edit mode showing the new value, and the page does **not** refresh.

**QA-EDIT-7 `[L-12]` `[E-20]` — Cancel restores and persists nothing. · NEGATIVE [ADMIN]**
- **When** I change all 5 inputs and click `✕`
- **Then** every cell shows its original value, the row exits edit mode, and **no** event of any kind is persisted `NE-4`.

**QA-EDIT-8 `[L-12]` `[E-17]` `[E-18]` `[E-19]` — validation blocks before the server. · NEGATIVE [ADMIN]**
- **When** I set `Order Date` to `30/06/2026` and click `✓` → an inline error appears, **no** network request is issued, **no** event is persisted, and focus moves to that input
- **When** I set `Product Cost` to `-5` (and separately `abc`) → same outcome
- **When** I set `Product Cost` to `0` → the save **succeeds** (zero is valid)
- **When** I set `CP Link` to `not a url` → same block, with the message exactly `Enter a valid http(s) URL`.

**QA-EDIT-9 `[L-12]` `[E-26]` — Today writes only that row's date input. · NEGATIVE [ADMIN]**
- **When** I click `Today` in row 1
- **Then** row 1's `Order Date` input equals today's local warehouse date in `YYYY-MM-DD`
- **And no** other row and **no** other field changes, **and nothing** is saved until `✓` is clicked (no `DC-13` yet).

**QA-EDIT-10 `[L-12]` `[E-21]` `[DC-37]` — concurrent edit yields a 409, not a silent overwrite. · NEGATIVE [ADMIN]**
- **Given** operators A and B both open the same line for editing and A saves first
- **When** B clicks `✓`
- **Then** B's save is rejected, `entity.version_conflict` persists with both versions and `attempted_action=line_item.edited` (`DC-37`)
- **And** the row reloads showing A's values with a **non-green** toast `Line changed by {user} — reloaded`
- **And** A's values are **not** overwritten, **and** B's typed values are shown in the conflict message rather than silently discarded.

**QA-EDIT-11 `[L-12]` `[DC-14]` `[BR-27]` — agent autofill is a distinct event type and stays editable. · NEGATIVE [ADMIN]**
- **Given** the purchasing agent has filled `Product Cost` on a line
- **Then** `line_item.autofilled` persists with `actor_type=agent` (`DC-14`) — **not** `line_item.edited`
- **When** a human edits the same field afterwards
- **Then** `line_item.edited` persists with `actor_type=human` (`DC-13`), and both events remain queryable in order with their actor types intact.

**QA-EDIT-12 `[L-12]` `[E-74]` — a server error during Save does not advance the row. · NEGATIVE [ADMIN]**
- **Given** the server returns 500 on the save call
- **Then** a red toast names the failure, the row stays in edit mode with the operator's typed values intact, **no** `DC-13` is persisted, and no value is optimistically rendered as saved.

---

### QA-DEL — Delete-line modal `[L-M3]`

**QA-DEL-1 `[L-M3]` — the modal opens from the wf-bar with exact copy. [WF]**
- **When** I click the wf-bar button `Modal: Delete Line`
- **Then** `#m-del` gains class `open`
- **And** `#m-del .modal header`'s **first text node** is exactly `Are you sure?`, and the same `header` contains a `.x` control whose text is exactly `✕` (the `.x` button is a child of `header`, so the header's flattened text is `Are you sure?✕` — assert the text node, §8.0 rule 4)
- **And** `#m-del .modal .body` text is exactly `This action cannot be undone. This will permanently delete the line item.`
- **And** `#m-del .modal .foot` contains exactly two buttons labelled exactly `Cancel` and `Delete`, in that order.

**QA-DEL-2 `[L-M3]` — the modal also opens from a row 🗑 in State 1. [WF]**
- **When** I click `#st-normal .litable tbody tr:nth-child(2) .act-ic .del` (the `🗑` on SKU `100043697`)
- **Then** `#m-del` gains class `open` with the same three exact strings as QA-DEL-1.

**QA-DEL-3 `[L-M3]` — the modal also opens from a row 🗑 in State 2. [WF]**
- **Given** the wf-tab `2 · On Hold`
- **When** I click any `#st-hold .litable tbody .act-ic .del`
- **Then** `#m-del` gains class `open` — the modal is shared between states, not duplicated per state.

**QA-DEL-4 `[L-M3]` `[E-24]` — Cancel dismisses without effect. · NEGATIVE [WF]**
- **When** I open `#m-del` and click the footer `Cancel`
- **Then** `#m-del` loses class `open` and `#st-normal .litable tbody tr` still returns **4** rows.

**QA-DEL-5 `[L-M3]` `[E-24]` — the ✕ dismisses without effect. · NEGATIVE [WF]**
- **When** I open `#m-del` and click `#m-del .modal header .x`
- **Then** `#m-del` loses class `open` and `#st-normal .litable tbody tr` still returns **4** rows.

**QA-DEL-6 `[L-M3]` `[E-24]` — a backdrop click dismisses without effect. · NEGATIVE [WF]**
- **When** I open `#m-del` and click the overlay background (a point inside `#m-del` but outside `#m-del .modal`)
- **Then** `#m-del` loses class `open`, the table still returns **4** rows, and no event is persisted `NE-6` `NE-16`.

**QA-DEL-7 `[L-M3]` `[DC-15]` `[BR-42]` — Delete persists a full snapshot. [ADMIN]**
- **Given** a `PENDING` line
- **When** I click `Delete`
- **Then** `line_item.deleted` persists carrying **every field of the line record** — all 18 rendered columns plus ids and timestamps — with actor and timestamp (`DC-15`)
- **And** the row disappears, `Total Quantity` decrements by that line's qty, a green toast reads exactly `Line item deleted`, the Outbound gate re-evaluates, **and** the Actor Log is unchanged (deletion is not a stock movement) · NEGATIVE.

**QA-DEL-8 `[L-M3]` `[E-22]` `[BR-16]` `[PD-23 · OWNER-PENDING]` — deleting an INBOUNDED line is blocked. · NEGATIVE [ADMIN]**
- **Given** an `INBOUNDED` line
- **When** I open M3 from its `🗑`
- **Then** the modal states `Cancel Inbound (restock) on this line first`, the `Delete` button carries `disabled`
- **And** forcing the request persists `order.action_rejected` with `reason_code=line_inbounded` (`DC-9`) and deletes **nothing**.

**QA-DEL-9 `[L-M3]` `[E-23]` `[E-55]` `[PD-24 · OWNER-PENDING]` — deleting the last line is allowed and leaves an unshippable order. [ADMIN]**
- **Given** an order with exactly one `PENDING` line
- **When** I delete it
- **Then** the deletion succeeds (`DC-15`), `Total Quantity: 0` renders, the table shows its empty state, and `📦 Outbound` is disabled `[BR-17]`.

**QA-DEL-10 `[L-M3]` `[E-4]` — double-click Delete deletes once. · NEGATIVE [ADMIN]**
- **When** I click `Delete` twice within 300 ms
- **Then** exactly **one** `line_item.deleted` exists, the modal closes once, the second submission is recorded as `DC-36`, and **no** "row not found" error is shown.

---

### QA-PRT — Print `[L-13]`

**QA-PRT-1 `[L-13]` `[BR-40]` — the label is carrier-neutral. · NEGATIVE [WF]**
- **Then** `#st-normal .otitle` contains a button whose visible label is exactly `🖨 Print`
- **And** the strings `Print (YUN)` and `Print (DELEO)` appear **nowhere** on the page
- **And** a `.carrier` badge reading exactly `YUN` renders in the same title row.

**QA-PRT-2 `[L-13]` `[L-F7]` — View Label and Print are separate controls. [WF]**
- **Then** `#st-normal .otitle` contains a button labelled exactly `View Label`, distinct from the `🖨 Print` button, and both exist in `#st-hold .otitle` too.

**QA-PRT-3 `[L-13]` `[G-4]` `[DC-24]` `[DC-25]` — one click produces a label with no browser dialog. · NEGATIVE [ADMIN]**
- **When** I click `🖨 Print`
- **Then** `print.requested` persists with the carrier and `label_ref` (`DC-24`), the job is pushed to the local print agent, and `print.job_result` persists with the job id and `result=success` (`DC-25`)
- **And** a green toast reads exactly `Label sent to printer`
- **And no** new tab opens, **no** browser print dialog appears, and **no** PDF is downloaded.

**QA-PRT-4 `[L-13]` `[E-39]` — an offline agent fails loudly. · NEGATIVE [ADMIN]**
- **Given** the print agent is unreachable
- **When** I click `🖨 Print`
- **Then** a **red** toast reads exactly `Print agent unreachable — label not printed` within the configured timeout
- **And** `print.job_result` persists with `result=agent_unreachable` (`DC-25`)
- **And no** browser print dialog is offered as a fallback, **and no** other action on the page is blocked.

**QA-PRT-5 `[L-13]` `[E-40]` — Print and View Label are disabled with no label. · NEGATIVE [ADMIN]**
- **Given** an order with no label or tracking number
- **Then** both `🖨 Print` and `View Label` carry `disabled` and render the visible reason `No label yet` `[BR-46]`
- **And** a forced request persists `order.action_rejected` with `reason_code=no_label` (`DC-9`).

**QA-PRT-6 `[L-13]` `[E-6]` — double-click prints once. · NEGATIVE [ADMIN]**
- **When** I click `🖨 Print` twice within 300 ms
- **Then** exactly **one** `print.requested` and one job id exist, the second click is recorded as `action.idempotency_suppressed` (`DC-36`), and exactly **one** physical label is produced.

**QA-PRT-7 `[L-13]` `[E-63]` — a deliberate reprint is allowed and attributable. [ADMIN]**
- **Given** a print job for this order is still queued at the agent
- **When** I click `🖨 Print` again (a separate, deliberate click, outside the debounce window)
- **Then** a **second** `print.requested` / `print.job_result` pair persists with a **different** `job_id`, and both labels are attributable to their own click. *(Contrast QA-PRT-6, which is one click delivered twice.)*

**QA-PRT-8 `[L-13]` `[E-85]` `[E-84]` — print on a cancelled order is blocked; success ≠ paper. · NEGATIVE [ADMIN]**
- **Given** a cancelled order
- **Then** `🖨 Print` is disabled with the visible reason `Order cancelled`, and a forced request persists `DC-9` with `reason_code=order_cancelled`
- **And** on a normal order whose printer is online but out of paper, `DC-25.result` is `success` — the contract proves delivery to the agent, **not** physical output; the recovery is a reprint `[E-63]`.

---

### QA-REN — Rendering contracts `[L-3]` `[L-4]` `[L-6]` `[L-10]` `[L-11]`

**QA-REN-1 `[L-10]` `[BR-42]` — the Line Items column contract is exactly 18 columns. [WF]**
- **Then** `#st-normal .litable thead tr:nth-child(1)` contains: three `th[rowspan="2"]` (select-all checkbox, `SKU`, `Image`), a `th[colspan="6"]` reading `Product Information (WooCommerce)`, a `th[colspan="8"]` reading `Inventory`, and one `th[rowspan="2"]` reading `Actions` — **3 + 6 + 8 + 1 = 18 rendered columns**
- **And** `#st-normal .litable thead tr:nth-child(2)` reads, in order: `Product Name`, `Product Name KR`, `Size`, `Qty`, `Subtotal`, `Total`, `Latest Inventory Count`, `Inbound Status`, `Sourcing Route`, `Order Number`, `Order Date`, `Product Cost 🤖`, `Tracking Number`, `CP Link`
- **And** each `tbody tr` renders 18 `td` cells.

**QA-REN-2 `[L-10]` `[BR-8]` `[BR-40]` — removed columns must not exist. · NEGATIVE [WF]**
- **Then** **no** header cell in `.litable` reads `Delivery Company`, **no** header cell reads `Comments`, and **no** header cell reads `Inbound Request` — in either state.

**QA-REN-3 `[L-10]` `[E-41]` `[BR-7]` — Latest Inventory Count is 0 on JIT and a real number on WHOLESALE. · NEGATIVE [WF]**
- **Then** in `#st-normal`, the rows with SKUs `100005104`, `100043697` and `100012534` (all `JIT (Coupang)`) show `Latest Inventory Count` = `0`
- **And** the row with SKU `100005088` (`WHOLESALE`) shows `12`
- **And** a `0` on a JIT line **must not** be reported as a defect — it is the expected value. *(Runner guidance, not a machine-checkable clause: it constrains the report, not the page. Same role as `QA-REN-8`'s closing note.)*

**QA-REN-4 `[L-4]` `[G-5]` — sourcing routes render as colorless black bold text. [WF]**
- **Then** the Sourcing Route cells contain `span.tag` elements with classes `tag-jit` / `tag-wholesale`
- **And** their computed `background-color` is fully transparent (`rgba(0, 0, 0, 0)`) and their computed `color` is `rgb(20, 16, 27)` (= `#14101B` = `var(--ink)`) — never a coloured pill · NEGATIVE
- **And** the visible strings are exactly `JIT (Coupang)` and `WHOLESALE`.

**QA-REN-5 `[L-4]` `[C-3]` — the JIT channel parenthetical is present and OTHER is absent. · NEGATIVE [WF]**
- **Then** every JIT cell reads exactly `JIT (Coupang)`; the bare string `JIT` with no parenthetical appears in **no** Sourcing Route cell
- **And** the string `OTHER (` appears in **no** Sourcing Route cell — `OTHER` is an inbound-origin route and never renders on order line items `[PD-80 · OWNER-PENDING]`.

**QA-REN-6 `[L-11]` `[G-6]` `[BR-10]` — brand is bold-prefixed on both name columns. · NEGATIVE [WF]**
- **Then** each row's `Product Name` cell begins with a `<b>` element reading exactly `Dr.Jart+`
- **And** each row's `Product Name KR` cell also begins with a `<b>` element reading exactly `Dr.Jart+`, followed by the Korean product name (e.g. `포어레미디 리뉴잉 폼 클렌저`)
- **And** the Korean brand form `닥터자르트` appears **nowhere** on the page (normalized 2026-08-03).

**QA-REN-7 `[L-10]` `[BR-26]` — WooCommerce originals render with the asterisk. [WF]**
- **Then** each SKU cell shows the SKU followed by a `span.bot` reading `({sku}*)` — e.g. `100005104` then `(100005104*)`
- **And** each Qty cell shows `1` followed by a `span.bot` reading `(1*)`
- **And** `#st-normal .liinfo` reads exactly `Edit a line via the Edit button. Use checkboxes to select items for bulk Inbound. * = WooCommerce original before variation-pack recalculation · 🤖 = auto-filled by Agent · Scroll right to see the Inventory fields.`

**QA-REN-8 `[L-3]` — the Actor Log renders the exact columns, row grammar and colour classes. [WF]**
- **Then** `#st-normal .logsec h4` begins with `Inbound / Outbound Actor Log` followed by `— New`
- **And** `#st-normal .logtbl th` reads, in order: `Time`, `Action`, `SKU`, `Qty`, `Operator`, `Note`
- **And** the data rows, newest first, are exactly: `07-01 09:32 / OUTBOUND / All (4 SKU) / 4 / Dean / –`; `07-01 09:10 / INBOUND / 100012534 / 1 / Miranti / –`; `07-01 08:58 / INBOUND / 100043697 / 1 / Miranti / –`; `06-30 20:15 / CANCEL INBOUND (Restock) / 100005104 / 1 / Dean / Corrected duplicate inbound`
- **And** their Action cells carry classes `act-out`, `act-in`, `act-in`, `act-cancel` respectively
- *(This scenario asserts **grammar and ordering only.** The demo rows are deliberately inconsistent with the line-item states — §2.5 B. Do **not** assert consistency between this table and the row tags, and do **not** file the inconsistency as a bug.)*

**QA-REN-9 `[L-6]` `[L-F12]` — Fulfillment Tracking renders unchanged from the live admin. [WF]**
- **Then** `#st-normal .tbl thead` reads `Provider Order ID`, `Tracking Number`, `Status`, `Status Description`, `Created At`, `Updated At`
- **And** its single row reads `YT2618100709331860` / `34YEM055929401000910906` / `DELIVERED` (in a `.st-delivered` chip) / `Shipment information received` / `6/30/2026, 8:55:53 PM` / `7/13/2026, 10:10:32 AM`
- **And** `#st-normal .lastmile` reads exactly `Last mile: AustraliaPost`
- **And** the tracking heading reads `TRACKING HISTORY (synced 7/16/2026, 4:51:40 AM)`
- **And** `#st-normal .trackscroll thead` reads `Time (local)`, `Node`, `Description`, `Location`, `UTC`, with `.node` chips including `DELIVERED`, `DELIVERY_ATTEMPT`, `IN_TRANSIT_CARRIER` and `ORDER_CREATION`.

**QA-REN-10 `[L-4]` `[PD-8 · OWNER-PENDING]` — the two tracking-number namespaces are visibly distinct. [WF]**
- **Then** the line-item `Tracking Number` for SKU `100043697` is `10323100835456`
- **And** the Fulfillment Tracking `Tracking Number` is `34YEM055929401000910906`
- **And** they render in different sections with different column headers — never presented as the same field · NEGATIVE.

**QA-REN-11 `[L-F10]` `[L-F11]` — Fulfillment Tracking controls render with exact labels. [WF]**
- **Then** `#st-normal .ftbadge` contains a `.carrier` badge reading `YUN`, a button labelled exactly `✎ Change Tracking #`, and a button labelled exactly `Reset Order`.

**QA-REN-12 `[BR-43]` §3.0.3 — the four time formats render where the contract says. [WF]**
- **Then** `Order Date` reads `2026-06-30 SGT` (zone printed) and `Order Created At` reads `30/06/2026 19:55:28 SGT` (zone printed)
- **And** every `#st-normal .logtbl` Time cell matches `MM-DD HH:mm` with **no** zone suffix (warehouse local by contract)
- **And** every `#st-normal .cmt-list time` matches `MM-DD HH:mm`
- **And** the SHIPMENT DETAILS `Created At` / `Updated At` cells match `M/D/YYYY, h:mm:ss AM/PM`
- **And** the TRACKING HISTORY table exposes **both** a `Time (local)` and a `UTC` column — the only block on the page that states both.

**QA-REN-13 `[L-3]` `[E-42]` — the Actor Log renders an empty state, never disappears. · NEGATIVE [ADMIN]**
- **Given** a brand-new order with no inbound or outbound history
- **Then** the Actor Log section, heading and header row still render, with a single empty-state row reading `No inbound or outbound activity yet`, and the section is **not** hidden.

**QA-REN-14 `[L-6]` `[DC-23]` — a carrier sync persists an event and drives the displayed timestamp. [ADMIN]**
- **When** a carrier sync runs for this order
- **Then** `shipment.tracking_synced` persists with `actor=system`, `synced_at`, the `appended_events[]` set and `result=ok` (`DC-23`)
- **And** the `TRACKING HISTORY (synced …)` marker renders that event's `synced_at`, formatted per §3.0.3
- **When** the next sync fails
- **Then** `DC-23` persists with `result=failed` and a `failure_reason`, the table keeps its previous rows, the marker keeps the **last successful** timestamp, and **no** fabricated time is displayed · NEGATIVE `[E-43]`.

**QA-REN-15 `[L-10]` `[E-62]` `[E-91]` — catalog drift never rewrites the line. · NEGATIVE [ADMIN]**
- **Given** a line whose SKU was retired (and separately: whose product record was deleted) after the order was placed
- **Then** the line still renders its historical SKU, EN name, KR name, size and prices from the order record
- **And** `Latest Inventory Count` renders `–` with a muted `SKU retired` marker where no mapping exists
- **And** the line is **not** auto-rewritten, **not** hidden and **not** removed.

**QA-REN-16 `[L-10]` `[E-57]` `[BR-34]` `[PD-27 · OWNER-PENDING]` — an assigned sample set is displayed, never edited here. · NEGATIVE [ADMIN]**
- **Given** Order Management has assigned a sample set to this order
- **Then** the line-items area shows **which** sample and **how many**
- **And** the page exposes **no** control to add, change or remove the assignment, and emits **no** `order.sample_assignment_changed` event §5.2
- **And** the carrier-facing string `(+ sample set)` does **not** appear as a line item on this page
- *(The source that defines which sample and how many is `[PD-51 · NO-DEFAULT]`; until it is answered this scenario is executable only for the "no control exists" half.)*

**QA-REN-17 `[L-4]` `[E-44]` `[E-59]` — absent agent-tracking values render `–` and are not links. · NEGATIVE [WF]**
- **Given** state `1 · Processing` and the row with SKU `100005088` (the `WHOLESALE` line)
- **Then** its `Order Number`, `Order Date`, `Tracking Number` and `CP Link` cells each read exactly `–`
- **And** none of those four cells contains an `<a>` element — `–` is plain text, never a link · NEGATIVE
- **And** the same row's `Product Cost 🤖` cell reads exactly `₩22,425` — a `–` in the other four is an absent purchase record, **not** an empty row.

**QA-REN-18 `[L-11]` `[E-45]` `[G-6]` — a brandless product renders without a prefix and nothing is synthesized. · NEGATIVE [ADMIN]**
- **Given** a line whose catalog record carries no brand
- **Then** the `Product Name` and `Product Name KR` cells render the product name with **no** leading `<b>` brand element
- **And** the UI **does not** synthesize, guess or back-fill a brand from the SKU, the supplier or another line · NEGATIVE
- **And** no event is emitted and no error state is shown — the fix is a catalog data fix, not a UI workaround.

**QA-REN-19 `[L-3]` `[E-65]` — Actor Log truncation is explicit, never silent. · NEGATIVE [ADMIN]**
- **Given** an order with more inbound/outbound events than the display cap
- **Then** the rendered rows are the newest `{N}` in newest-first order, and the section renders a visible `showing latest {N}` marker
- **And** the full history is reachable from `↻ Audit History` `[L-F2]`
- **And** the table **never** drops rows without the marker — a silently shortened log is a defect, not a display choice · NEGATIVE. *(Cap value and pagination mechanics are dev-time, §9.4 D-7; the explicitness is not.)*

**QA-REN-20 `[L-10]` `[E-90]` `[E-41]` `[BR-7]` — the JIT inventory count across its lifecycle. [ADMIN]**
- **Given** a `JIT (Coupang)` line on an order that has not yet been inbounded
- **Then** `Latest Inventory Count` reads `0` — correct, not an error `[E-41]`
- **When** the line is inbounded
- **Then** the count refreshes to a positive transient value in the same response
- **When** the order is outbounded
- **Then** the count returns to `0`
- **And** a JIT line still showing a positive count after outbound is a **reconciliation signal to raise**, not a display bug to suppress — and this page emits **no** adjustment event of its own to "correct" it · NEGATIVE.

---

### QA-SUB — Page furniture `[L-F1]`–`[L-F17]`

**QA-SUB-1 `[L-F1]` `[L-F2]` `[L-F3]` `[L-F4]` `[L-F5]` — the subbar renders exactly five controls with exact labels. [WF]**
- **Then** `#st-normal .subbar` contains, in order: `← Back to Orders` (class `back`, left), then right-aligned `↻ Audit History` (`link-btn`), `↗ View in WP` (`link-btn blue`), `⧉ Clone Order` (`link-btn blue`), `✕ Cancel Order` (`link-btn red`)
- **And** the same five, with the same labels and classes, exist in `#st-hold .subbar`.

**QA-SUB-2 `[L-F6]` `[L-F7]` — the title row renders order no., status, carrier and three controls. [WF]**
- **Then** `#st-normal .otitle h2` reads exactly `Order # 407847`
- **And** it is followed by a status badge, a `.carrier` badge reading `YUN`, and buttons labelled exactly `View Label`, `🖨 Print` and `Change Status ▾`.

**QA-SUB-3 `[L-F8]` — Order Information renders the six read-only fields. [WF]**
- **Then** the `📋 Order Information` panel shows `Order Date` = `2026-06-30 SGT`, `Order Created At` = `30/06/2026 19:55:28 SGT`, `Total Items` = `4`, `Total Discount` = `AUD 13.11`, `Total Amount` = `AUD 129.8`
- **And** `PIC` = `Egita` followed by a bordered `button` labelled exactly `✎ Edit`.

**QA-SUB-4 `[L-5]` — the bare pencil PIC affordance must not exist. · NEGATIVE [WF]**
- **Then** the PIC row's control is a bordered `button` whose visible text includes the word `Edit`
- **And** a standalone unbordered `✎` glyph is **not** used as the PIC control in either state.

**QA-SUB-5 `[L-F9]` — address panels render with edit affordances. [WF]**
- **Then** the `👤 Billing Address` and `🚚 Shipping Address` headings each carry a `span.edit` reading `✎`
- **And** the shipping panel includes `Tax ID` and `Short Address Code` rows, both rendering `–`
- **And** the billing panel includes `Email` = `m.saltoon@gmail.com` and `Phone` = `+61415999051`.

**QA-SUB-6 `[L-F14]` `[L-F15]` — footer counter and add control. [WF]**
- **Then** `#st-normal .li-foot .tq` reads exactly `Total Quantity: 4` and a button labelled exactly `+ Add Line Item` exists in the same footer
- **And** `#st-hold .li-foot .tq` also reads exactly `Total Quantity: 4`.

**QA-SUB-7 `[L-F17]` — global nav renders the live-admin item set. [WF]**
- **Then** `#st-normal .nav` shows `SkinSeoul` (class `brand`), then `Operation AI ▾`, `Catalog Management ▾`, `OMS Center ▾`, `Site Management ▾`, `Customer Management ▾`, `SkinSeoul WP Admin`, then the `💬 Comments` button, the user chip `Yongwon Ryu` (with a `Y` avatar), and a `Logout` button.

**QA-SUB-8 `[L-F5]` `[E-47]` `[DC-9]` `[BR-15]` `[PD-22 · OWNER-PENDING]` — Cancel Order is blocked while lines are inbounded. · NEGATIVE [ADMIN]**
- **Given** an order with 3 `INBOUNDED` lines
- **When** I click `✕ Cancel Order`
- **Then** the action is blocked with the message exactly `Cancel Inbound (restock) on 3 line(s) first`
- **And no** `order.cancelled` event is persisted, **and no** stock is restocked automatically
- **And** `order.action_rejected` persists with `reason_code=inbounded_lines_present` (`DC-9`).

**QA-SUB-9 `[L-F5]` `[DC-4]` — Cancel Order succeeds when no line is inbounded. [ADMIN]**
- **Given** an order whose every line is `PENDING`
- **When** I click `✕ Cancel Order` and confirm
- **Then** `order.cancelled` persists with `previous_status`, `line_count` and `confirm_acknowledged=true` (`DC-4`)
- **And** a green toast reads exactly `Order cancelled`, the status badge updates, and the page does **not** refresh
- **When** I dismiss the confirm dialog instead
- **Then** **no** `DC-4` is persisted and the status is unchanged `NE-15` · NEGATIVE
- **And** the cancelled order still renders read-only with its full history and still accepts comments `[E-56]` `[E-79]`.

**QA-SUB-10 `[L-F4]` `[E-50]` `[DC-5]` `[PD-31 · OWNER-PENDING]` — Clone copies lines and addresses only. · NEGATIVE [ADMIN]**
- **When** I click `⧉ Clone Order` and confirm
- **Then** `order.cloned` persists with `source_order_id → new_order_id`, `copied_fields[]` = lines + billing + shipping, and `excluded_fields[]` (`DC-5`)
- **And** a green toast reads `Order cloned — {new order no.}` with a link
- **And** the new order has **no** comments, **no** actor-log rows, **no** tracking numbers, **no** `Order Number` / `Order Date` / `Product Cost` / `CP Link` values, **no** PIC and a fresh status — this list is PD-31's registered exclusion set
- **And** the new order carries **no** sample assignment either — the `[G-13]` extension stated in `[L-F4]`, not PD-31 content `[E-83]`
- **When** the source order has 0 lines
- **Then** the clone succeeds and produces a 0-line order `[E-82]`.

**QA-SUB-11 `[L-F11]` `[E-48]` `[DC-8]` `[BR-20]` `[PD-30 · OWNER-PENDING]` — Reset Order clears shipment state only. · NEGATIVE [ADMIN]**
- **When** I click `Reset Order` and confirm on an order with `INBOUNDED` lines and a `DELIVERED` shipment
- **Then** `order.reset` persists with the full cleared-field snapshot (`DC-8`) and a green toast reads exactly `Order reset — shipment data cleared`
- **And** the shipment/tracking/label state is cleared
- **And** every line's `Inbound Status` is **unchanged**, **and no** `inventory.movement` is created
- **And** a print job already queued at the agent is **not** recalled, and the confirm dialog said so `[E-84]`.

**QA-SUB-12 `[L-F10]` `[E-49]` `[DC-22]` `[DC-35]` `[PD-32 · OWNER-PENDING]` — duplicate tracking warns, allows, and does not reprint. · NEGATIVE [ADMIN]**
- **When** I set the tracking number to one that already exists on another order
- **Then** a warning names the other order and requires an explicit confirm
- **And** on confirm, `shipment.tracking_changed` (`DC-22`, `duplicate_warning_shown=true`) and `shipment.tracking_duplicate_acknowledged` with the colliding order id (`DC-35`) both persist
- **And** a green toast reads exactly `Tracking number updated`
- **And no** label is regenerated, **no** label is invalidated, and **no** print job is created.

**QA-SUB-13 `[L-F10]` `[E-77]` `[E-78]` — clearing and no-op tracking edits. · NEGATIVE [ADMIN]**
- **When** I clear the tracking number to empty and save
- **Then** `DC-22` persists with `new=""`, and `🖨 Print` and `View Label` fall back to disabled with `No label yet` `[E-40]`
- **When** I save the identical current value
- **Then** **no** event and **no** toast are produced `NE-11`.

**QA-SUB-14 `[L-F14]` `[E-25]` `[DC-16]` `[BR-18]` `[PD-25 · OWNER-PENDING]` — Add Line Item works before outbound and is blocked after. · NEGATIVE [ADMIN]**
- **Given** an order in `processing` that has not been outbounded
- **When** I click `+ Add Line Item`, pick a SKU and qty, and confirm
- **Then** `line_item.added` persists with SKU, qty, `initial_values{}` and `inbound_status=PENDING` (`DC-16`)
- **And** the row appends as `PENDING`, `Total Quantity` increments, the Outbound gate re-evaluates, and a green toast reads exactly `Line item added`
- **Given** an outbounded order
- **Then** `+ Add Line Item` carries `disabled` with the visible reason, and a forced request persists `order.action_rejected` with `reason_code=order_outbounded` (`DC-9`) and creates **no** `line_item.added`.

**QA-SUB-15 `[L-5]` `[DC-6]` `[BR-23]` `[PD-33 · OWNER-PENDING]` — PIC change uses a picker and does not notify Slack. · NEGATIVE [ADMIN]**
- **When** I click `✎ Edit` on PIC and pick a different system user
- **Then** the control is a user picker — free text is **not** accepted
- **And** `order.pic_changed` persists with `old → new` user id and name (`DC-6`), a green toast reads `PIC changed to {name}`
- **And no** Slack message is sent to the new PIC
- **When** I pick the same user again
- **Then** **no** event and **no** toast are produced
- **And** a deactivated user is not offered in the picker `[E-53]`.

**QA-SUB-16 `[L-F9]` `[DC-7]` `[E-54]` — address edits persist a field-level diff and validate. · NEGATIVE [ADMIN]**
- **When** I change `City` from `Bellevue Hill` to `Bondi` on the shipping address and save
- **Then** `order.address_edited` persists with `scope=shipping` and `field_diff{city:{old:"Bellevue Hill", new:"Bondi"}}` (`DC-7`), and a green toast reads exactly `Shipping address updated`
- **When** I enter a postcode invalid for the carrier's country
- **Then** save is blocked with an inline field-level error, **no** event is persisted, and **no** toast appears.

**QA-SUB-17 `[L-F3]` `[L-4]` `[DC-33]` `[E-59]` — external links open in a new tab and are persisted; `–` is not a link. · NEGATIVE [ADMIN]**
- **When** I click `↗ View in WP`, then a line's `Order Number` link, then a line's `CP Link`
- **Then** three `order.external_link_opened` events persist with `target` = `wp`, `order_number_lookup` and `cp_link` respectively (`DC-33`), each opening a new tab without navigating away from Order Detail
- **When** I click a cell rendering `–` (e.g. the `Order Number` cell of the WHOLESALE row)
- **Then** nothing happens and **no** `DC-33` is persisted.

**QA-SUB-18 `[L-F13]` `[E-87]` — select-all covers every row, including on a large order. [ADMIN]**
- **Given** an order with 120 lines
- **When** I click the header `Select all` checkbox
- **Then** all 120 row checkboxes are checked (this table has no pagination, so there is no invisible-row hazard)
- **When** I click `Bulk Inbound Selected Items`
- **Then** exactly **one** `DC-12` and **one** toast result, regardless of internal chunking.

**QA-SUB-19 `[L-F8]` `[E-68]` `[BR-48]` — no FX conversion anywhere on the page. · NEGATIVE [WF]**
- **Then** `Total Discount` reads exactly `AUD 13.11` and `Total Amount` reads exactly `AUD 129.8`
- **And** product costs render in the purchase currency (`₩17,100`, `₩22,425`, `₩30,630`)
- **And no** USD figure and **no** converted amount appears anywhere on the page.

**QA-SUB-20 `[G-15]` `[E-69]` `[BR-33]` `[PD-1 · OWNER-PENDING]` — v1 is a single admin role, and every mutation still names its actor. · NEGATIVE [ADMIN]**
- **Given** any two authenticated users of the v1 admin
- **Then** both see the identical control set on this page: **no** control is hidden, greyed or removed on account of who is logged in, and the only disabled controls are the business gates named in `[BR-1]`, `[BR-14]`, `[BR-15]`, `[BR-16]`, `[BR-18]` and `[E-40]` / `[E-85]` / `[E-86]` · NEGATIVE
- **And** the high-trust actions (`✕ Cancel Order`, `Reset Order`, M3 `Delete`, `Cancel Outbound`, status → `refunded`) are reachable by both, each behind its confirm step
- **And** every resulting event carries the acting user's `actor` id and display name — the actor record, not a role gate, is the v1 control `[BR-33]`.

---

### QA-NET — Network, session and recovery `[E-36]`–`[E-38]` `[E-58]` `[E-64]` `[E-76]`

Every scenario in this block is `[ADMIN]`: each needs a server to fail against. They exist because the network-failure contract is the part of `[G-9]` that a demo can never demonstrate and a production incident always tests.

**QA-NET-1 `[L-2]` `[E-36]` `[G-9]` — a lost response on Inbound still yields exactly one receipt. · NEGATIVE [ADMIN]**
- **Given** the write lands on the server but the response never reaches the client
- **When** the client retries with the **same idempotency key**
- **Then** exactly **one** `line_item.inbounded` and exactly **one** `inventory.movement` exist — the retry is suppressed as `DC-36`, not applied twice · NEGATIVE
- **When** the operator reloads the page instead of retrying
- **Then** the row renders whatever the server holds, and the Actor Log — not the pre-reload screen — is ground truth.

**QA-NET-2 `[L-9]` `[E-37]` — a lost response on Outbound proves nothing by sound. · NEGATIVE [ADMIN]**
- **Given** the send sound has played and the response is then lost
- **When** the client retries with the same idempotency key
- **Then** exactly **one** `order.outbounded` and one set of movements exist
- **And** if the request never committed, **no** `order.outbounded` exists **despite the sound having played** — the audio is feedback, never proof; only `DC-19` proves an outbound · NEGATIVE.

**QA-NET-3 `[L-1]` `[E-38]` — a lost response on Add Comment creates no duplicate. · NEGATIVE [ADMIN]**
- **Given** a comment write whose response is lost
- **When** the client retries with the same idempotency key
- **Then** exactly **one** `comment.posted` exists (`DC-26`), the thread shows the comment **once**, and at most one `comment.mention_notified` per distinct mention is dispatched (`DC-27`) · NEGATIVE.

**QA-NET-4 `[E-58]` `[E-76]` `[E-21]` `[DC-37]` — two tabs and an expired session both fail safely. · NEGATIVE [ADMIN]**
- **Given** the same operator has this order open in two tabs and mutates from the stale one
- **Then** the version check rejects it (409), that tab reloads the affected row, and **no** cross-tab lock is required · NEGATIVE — `entity.version_conflict` persists (`DC-37`)
- **Given** the session expires mid-action
- **Then** the action is rejected with a red toast and a re-authentication prompt, and on re-auth the operator returns to **this order**, not to a list
- **And** the un-sent action is **not** auto-replayed after re-auth · NEGATIVE.

**QA-NET-5 `[E-64]` `[G-2]` — the browser Back button never restores stale state. · NEGATIVE [ADMIN]**
- **Given** a status change was applied on this page and the operator navigates away and then presses Back
- **Then** the page re-renders from the server showing the **current** status — **no** cached pre-change render is restored · NEGATIVE
- **And** because no action on this page depends on a full-page refresh `[G-2]`, Back is always safe: **no** action is re-submitted and **no** event is duplicated by the navigation · NEGATIVE.

---

### QA-DC — Data-capture sweeps

**QA-DC-1 `[G-8]` `[DC-34]` — the arrival path is captured on every entry. [ADMIN]**
- **When** I open the order from a View Orders row, then from a Comments-hub item, then from a Slack mention link, then by typing the URL
- **Then** four `order.detail_viewed` events persist with `entry_path` = `view_orders_row`, `comments_hub`, `slack_deep_link` and `direct` respectively (`DC-34`).

**QA-DC-2 `[G-8]` `[L-3]` `[BR-36]` — the Actor Log is a view, not a store. [ADMIN]**
- **Given** an order with 4 inbound/outbound events
- **When** I query the event store directly for that order
- **Then** the returned `line_item.inbounded` / `line_item.inbound_cancelled` / `order.outbounded` / `order.outbound_cancelled` events match the Actor Log rows one-for-one in content and order
- **And** rebuilding the log from the store reproduces the rendered table exactly — the UI holds no row the store does not have · NEGATIVE.

**QA-DC-3 `[G-8]` `[L-F16]` §5.4 — declared non-events produce nothing. · NEGATIVE [ADMIN]**
- **When** I toggle row checkboxes, toggle select-all, open and close the status dropdown without picking, toggle `Hide Comments`, type and clear a hub search, switch hub tabs, cancel a row edit, dismiss M3 three ways, open `View Label`, dismiss a destructive confirm dialog, and scroll the line-items table horizontally
- **Then** **zero** events are persisted for any of those actions (`NE-1`–`NE-16`)
- **And** a subsequent real action still persists normally — proving the absence is a guard, not a broken pipeline.

**QA-DC-4 `[G-8]` `[DC-17]` `[BR-26]` — WooCommerce originals survive recalculation. [ADMIN]**
- **Given** a variation-pack line that was recalculated
- **Then** `line_item.wc_recalculated` persists with both `wc_original{sku, qty}` and `recalculated{sku, qty}` and `actor_type=system` (`DC-17`)
- **And** both values remain readable indefinitely — the original is never overwritten · NEGATIVE.

**QA-DC-5 `[G-8]` `[DC-18]` `[DC-32]` `[BR-35]` `[PD-16 · OWNER-PENDING]` — an unrecognized match lands correctly on this order. · NEGATIVE [ADMIN]**
- **Given** a match confirmed on the tracking-missing screen against this order
- **Then** `line_item.tracking_written` persists with the line id, tracking number, resolver and `source_screen` (`DC-18`)
- **And** the tracking number is visible in that line's `Tracking Number` cell
- **And** `comment.auto_posted` persists with `source=system` and `origin=unrecognized_match_confirmed` (`DC-32`), and the auto-comment is visible in the thread @mentioning the registrant
- **And** Order Detail exposes **no** match UI of its own
- **And** a View Orders M6 expected-qty edit produces **no** line-item change and **no** comment on this order §5.3.

**QA-DC-6 `[G-8]` `[DC-21]` — every stock-moving action emits a ledger row and the net is zero. [ADMIN]**
- **When** I inbound a line, cancel that inbound, outbound the order, and cancel that outbound
- **Then** four `inventory.movement` events persist with `movement_type` = `inbound`, `cancel_inbound_restock`, `outbound`, `cancel_outbound_reversal`, each carrying `source_event_id` and `balance_after`
- **And** the net balance change is exactly zero.

**QA-DC-7 `[G-8]` `[L-F2]` §5.5 — retention, queryability and export. [ADMIN]**
- **Given** events older than any plausible retention window
- **Then** **no** event from §5.1 has been purged and **no** comment has been deleted · NEGATIVE
- **And** the store answers filters on `order_id`, `sku`, `actor`, `actor_type`, `event_name`, `reason_code` and a date range
- **And** the `↻ Audit History` surface exports to CSV following the Closing report's encoding and column precedent
- **And** Order Detail itself exposes **no** export button in v1 · NEGATIVE.

**QA-DC-8 `[G-8]` `[BR-27]` `[BR-43]` `[E-88]` `[E-89]` — actor-type and timestamp fidelity survive. · NEGATIVE [ADMIN]**
- **Then** every event carries `actor_type` ∈ {`human`, `agent`, `system`} and the three are distinguishable in every query — they are **never** collapsed into one "user" field
- **And** every event stores `occurred_at` in UTC **plus** a `display_timezone`
- **And** an event whose actor was later removed from the user directory still renders that actor's historical display name in the Actor Log — never `Unknown`, never blank
- **And** with the browser set to a timezone other than the warehouse's, the Actor Log, the comment timestamps and the hub times render **warehouse local** — the browser zone changes **nothing** on this page · NEGATIVE `[E-89]`; the `SGT`-suffixed fields render as printed and TRACKING HISTORY still shows both `Time (local)` and `UTC` §3.0.3.

**QA-DC-9 `[G-9]` `[BR-32]` `[BR-47]` `[DC-9]` `[DC-36]` `[E-70]` — guards and suppressions are measurable. [ADMIN]**
- **When** I trigger each guard once, in this order (cancel-order with inbounded lines, add-line after outbound, delete an inbounded line, cancel-inbound after outbound, outbound from `on-hold`, outbound with 0 lines, print with no label, print on a cancelled order)
- **Then** **eight** `order.action_rejected` events persist (`DC-9`), carrying, in that order, the reason codes `inbounded_lines_present`, `order_outbounded`, `line_inbounded`, `order_outbounded`, `hold_blocks_outbound`, `no_lines`, `no_label`, `order_cancelled` — **seven distinct codes across eight events**, every one drawn from the §5.1 enum
- *(`order_outbounded` legitimately appears twice: add-line-after-outbound `[E-25]` and cancel-inbound-after-outbound `[E-10]` are the same rejection cause. Do **not** assert eight distinct codes; if the owner later wants them separable, that is a change to the `DC-9` enum in §5.1 plus `[E-10]` and `[E-25]`, not to this scenario.)*
- **And** after a double-click on any mutating control, `action.idempotency_suppressed` persists with `suppressed_action`, `idempotency_key`, `original_event_id` and `delta_ms` (`DC-36`) — the double-click fix is provable from data, not asserted
- **And** a replayed request arriving **after** the dedupe window has expired is processed as a new, genuine action rather than suppressed, and its `delta_ms` on the earlier `DC-36` is what makes the window tunable `[E-70]` · NEGATIVE.

---

### 8.1 Scenario counts

| Block | Scenarios | `[WF]` | `[ADMIN]` | Negative (heading) | Negative (any clause) |
|---|---|---|---|---|---|
| QA-MAP | 6 | 6 | 0 | 1 | 2 |
| QA-CMT | 16 | 7 | 9 | 6 | 12 |
| QA-HUB | 12 | 8 | 4 | 3 | 7 |
| QA-INB | 18 | 5 | 13 | 7 | 14 |
| QA-OUT | 13 | 3 | 10 | 9 | 12 |
| QA-STA | 12 | 5 | 7 | 5 | 10 |
| QA-EDIT | 12 | 5 | 7 | 7 | 10 |
| QA-DEL | 10 | 6 | 4 | 5 | 6 |
| QA-PRT | 8 | 2 | 6 | 6 | 6 |
| QA-REN | 20 | 13 | 7 | 10 | 14 |
| QA-SUB | 20 | 8 | 12 | 12 | 13 |
| QA-NET | 5 | 0 | 5 | 5 | 5 |
| QA-DC | 9 | 0 | 9 | 3 | 7 |
| **Total** | **161** | **68** | **93** | **79 (49.1%)** | **118 (73.3%)** |

A scenario counts as negative when it asserts that something must **not** happen. The stricter **heading** count (`· NEGATIVE` in the scenario title) is **49.1%** (79 of 161); counting every scenario that carries at least one negative Then-clause gives **73.3%** (118 of 161). Both are far above the 25% floor required by `_review.md` §3.4.

`[WF]` share is **42.2%** (68 of 161). Every `[WF]` scenario is executable today against the live wireframe with the selectors and strings given; every `[ADMIN]` scenario is written so it becomes executable unchanged the day the real admin exists.

**v1.2 delta, for anyone diffing against v1.0/v1.1 counts:** 14 scenarios were added to close the `[E-n]` coverage gap (`QA-INB-17`, `QA-INB-18`, `QA-CMT-16`, `QA-OUT-13`, `QA-REN-17`–`QA-REN-20`, `QA-SUB-20`, `QA-NET-1`–`QA-NET-5`) and one existing scenario, `QA-STA-4`, moved from `[WF]` to `[ADMIN]` because the wireframe lacks the outside-click handler `[OD-WFX-1 · proposed]`. `[WF]` therefore stays at 68 (−1 retagged, +1 new: `QA-REN-17`) while `[ADMIN]` rises 79 → 93. No scenario was renumbered and none was deleted.

### 8.2 Data-capture → QA coverage map

Every `[DC-n]` in §5.1 has at least one QA scenario whose Then-clause asserts its persistence. Generated from the scenario bodies, not asserted by hand.

| DC | Asserted by | DC | Asserted by |
|---|---|---|---|
| **DC-1** | QA-STA-7, QA-STA-10, QA-STA-12 | **DC-20** | QA-OUT-10 |
| **DC-2** | QA-STA-7, QA-STA-12 | **DC-21** | QA-INB-6, QA-INB-8, QA-INB-13, QA-OUT-4, QA-OUT-10 |
| **DC-3** | QA-STA-10 | **DC-22** | QA-SUB-12, QA-SUB-13 |
| **DC-4** | QA-SUB-9 | **DC-23** | QA-REN-14 |
| **DC-5** | QA-SUB-10 | **DC-24** | QA-PRT-3 |
| **DC-6** | QA-SUB-15 | **DC-25** | QA-PRT-3, QA-PRT-4 |
| **DC-7** | QA-SUB-16 | **DC-26** | QA-CMT-4, QA-CMT-8, QA-CMT-9, QA-CMT-10, QA-CMT-12, QA-CMT-15 |
| **DC-8** | QA-SUB-11 | **DC-27** | QA-CMT-8, QA-CMT-10, QA-CMT-11, QA-CMT-12 |
| **DC-9** | QA-DC-9, QA-DEL-8, QA-INB-10, QA-OUT-7, QA-OUT-8, QA-OUT-9, QA-OUT-11, QA-OUT-13, QA-PRT-5, QA-PRT-8, QA-SUB-8, QA-SUB-14 | **DC-28** | QA-CMT-14, QA-CMT-16 |
| **DC-10** | QA-INB-6, QA-INB-12, QA-INB-13, QA-INB-17, QA-INB-18 (non-creation), QA-NET-1 | **DC-29** | QA-CMT-14, QA-CMT-16 |
| **DC-11** | QA-INB-8, QA-INB-9 | **DC-30** | QA-HUB-10 |
| **DC-12** | QA-INB-12, QA-INB-15, QA-INB-16, QA-INB-17, QA-SUB-18 | **DC-31** | QA-HUB-9 |
| **DC-13** | QA-EDIT-6, QA-EDIT-9, QA-EDIT-11, QA-EDIT-12 | **DC-32** | QA-DC-5 |
| **DC-14** | QA-EDIT-11 | **DC-33** | QA-SUB-17 |
| **DC-15** | QA-DEL-7, QA-DEL-9, QA-DEL-10 | **DC-34** | QA-DC-1, QA-HUB-10 |
| **DC-16** | QA-SUB-14 | **DC-35** | QA-SUB-12 |
| **DC-17** | QA-DC-4 | **DC-36** | QA-DC-9, QA-DEL-10, QA-INB-7, QA-OUT-5, QA-PRT-6 |
| **DC-18** | QA-DC-5 | **DC-37** | QA-EDIT-10, QA-OUT-8 |
| **DC-19** | QA-OUT-4, QA-OUT-5, QA-OUT-6 (non-creation), QA-OUT-13, QA-STA-11 (non-creation), QA-NET-2 | **NE-1 … NE-16** | QA-DC-3 (single sweep enumerating all sixteen) |
| **DC-21** *(also)* | QA-INB-17, QA-NET-1 | **DC-26** *(also)* | QA-NET-3 |
| **DC-36** *(also)* | QA-INB-17, QA-NET-1 | **DC-37** *(also)* | QA-INB-18, QA-NET-4 |

**Positive paths are asserted positively.** `DC-4` (order cancelled) and `DC-16` (line added) have both a guard scenario and a **success** scenario — `QA-SUB-9` and `QA-SUB-14` each run the allowed path first and the blocked path second. A negative-only assertion ("no event exists") is not evidence that the event can be written, so no `[DC-n]` in this spec relies on one.

### 8.3 Execution order for an automated `[WF]` run

Run in this order; each group leaves the page in a known state and the next group re-loads.

1. **QA-MAP-1 … QA-MAP-6** — verify the map before trusting any selector.
2. **QA-REN-1 … QA-REN-12 and QA-REN-17** — pure render assertions, no interaction, no state mutation.
3. **QA-SUB-1 … QA-SUB-7, QA-SUB-19** — furniture render assertions.
4. **QA-INB-1 … QA-INB-5, QA-OUT-1 … QA-OUT-3, QA-STA-1 … QA-STA-3, QA-STA-5, QA-STA-6, QA-EDIT-1 … QA-EDIT-5, QA-PRT-1, QA-PRT-2** — per-legend render and state-tab assertions. **`QA-STA-4` is deliberately absent from the `[WF]` run**: it is `[ADMIN]` until the wireframe gains an outside-click handler `[OD-WFX-1 · proposed]`.
5. **QA-HUB-1 … QA-HUB-8** — dropdown interactions (reload between search scenarios; the search pane persists in the DOM once created).
6. **QA-CMT-1 … QA-CMT-7** — thread mutations. **Reload before each**, because `QA-CMT-3` and `QA-CMT-5` permanently append rows to the in-page thread for the rest of the session.
7. **QA-DEL-1 … QA-DEL-6** — modal interactions; close the modal between scenarios.

`[ADMIN]` scenarios are unordered and each states its own Given.

### 8.4 Edge-case → QA coverage, and the four deliberate exclusions

**Every `[E-n]` in §7 is either referenced by a QA scenario or listed below with the reason it is not machine-assertable.** A coverage checker can therefore treat any unlisted, unreferenced `[E-n]` as a real hole. The v1.2 pass closed **18 of the 19** gaps the 2026-08-03 coverage audit found: `E-3`, `E-9`, `E-14`, `E-34`, `E-35`, `E-36`, `E-37`, `E-38`, `E-44`, `E-45`, `E-52`, `E-58`, `E-64`, `E-65`, `E-70`, `E-76`, `E-89` and `E-90` are now asserted by `QA-INB-17`, `QA-INB-18`, `QA-OUT-13`, `QA-CMT-16`, `QA-NET-1`–`QA-NET-5`, `QA-REN-17`–`QA-REN-20`, `QA-DC-8` and `QA-DC-9`. The nineteenth, `E-69`, is the first row of the table below. Rows 2–4 are cases that *do* have a scenario, listed so nobody reads their **deliberately unasserted half** as an oversight.

| `[E-n]` | Why it has no scenario of its own | Where it is nonetheless honored |
|---|---|---|
| **`E-69`** | It is an **org-policy statement** ("an operator without fulfillment training opens the page"), not a behavior the page performs. Its one machine-checkable consequence — that nothing is role-gated in v1 — **is** asserted. | `QA-SUB-20` asserts the no-role-gating half `[G-15]` `[BR-33]`. |
| **`E-30`** *(partially)* | The max-comment-length half is explicitly dev-time (§9.4 D-13); asserting a number here would invent one. | The escaping half is asserted by `QA-CMT-13` and `QA-HUB-7`. |
| **`E-57`** *(partially)* | The "which sample and how many" half has **no defined source** `[PD-51 · NO-DEFAULT]`; a scenario asserting rendered values would specify behavior the owner has not decided. | `QA-REN-16` asserts the executable half — that no assignment control exists here and no `order.sample_assignment_changed` is emitted. |
| **`E-86`** *(partially)* | What *unblocks* a carrier-less order is undecided `[PD-55 · NO-DEFAULT]`. | `QA-OUT-11` asserts the block, the visible reason, `reason_code=no_carrier` and the absence of any assignment control. |

The three `· partially` rows are not coverage gaps: in each, the unasserted half is a `NO-DEFAULT` owner question or a declared dev-time choice, and asserting it would contradict §9.2 / §9.4.

---

## 9. Out of Scope & Open Questions

Per `_review.md` §3.8, this section lists **only** three things: what this screen does not do, owner questions that have **no** provisional default, and decisions explicitly left to development. Owner questions that already carry a provisional default live in the PD register and are written into the body above as normal behavior tagged `[PD-n · OWNER-PENDING]` — they are **not** repeated here.

### 9.1 Explicitly out of scope for this screen

| Area | Why, and where it lives instead |
|---|---|
| **Scanner protocol `[G-1]`** | Order Detail is not a scan surface and must never gain a scan input `[BR-30]`. Scanning lives in View Orders (all states) and Closing. QA must not apply the `[G-1]` invariants here. |
| **Audio `[G-3]`(b) TTS and (c) warning tone** | (b) is a Closing scan-warning mechanism; (c) is a View Orders State 6 wrong-product signal. Neither has an analogue on a desk screen `[BR-29]`. Only `[G-3]`(a) applies here — and (a) is **in scope as page behavior**, specified in `[L-9]` step 2 with its own QA scenario, not merely cross-referenced (`_review.md` §2b codes this row `Δ`; that coding is stale, §3.0.1). |
| **Label / invoice layout content** | Deferred to **Phase 3-1**, a separate session with the owner. This spec covers print *behavior* `[G-4]` only, never what is printed on the label. |
| **Sample assignment UI** | Order Management is the primary home `[G-13]`. Order Detail only **displays** the assigned sample `[PD-27 · OWNER-PENDING]` `[BR-34]`. Sample-set contents on the picking list are RTO's concern `[PD-36 · OWNER-PENDING]`. |
| **Unrecognized-tracking resolution UI** | tracking-missing (primary) and View Orders M2. Order Detail is a landing surface only `[BR-35]`. |
| **Partial-quantity receipt and the inbound-request lifecycle** (`REQUESTED → PARTIAL → INBOUNDED`, expected-qty edits, multiple tracking numbers `[G-10]` `[G-11]`) | Inbound Request + View Orders State 6 / M6. Order Detail's per-line inbound is all-or-nothing `[BR-41]` `[E-71]`. |
| **Line-based location filter and audit-mode visibility `[G-14]`; JIT residual stock** | Inventory (stock-status). Order Detail shows `Latest Inventory Count` as a read `[L-10]`. Inventory's M4 reservation release is the sibling of this page's Cancel Inbound `[PD-45 · OWNER-PENDING]` — cross-referenced in §6.5, specified there. |
| **Korean-name picking artifacts `[G-6]`** | RTO Ready Item Details and the picking list. Order Detail keeps EN-primary + KR columns `[L-11]`. |
| **Closing sessions, warnings, CSV report** | Closing. Order Detail's Cancel Outbound after a closing scan is noted as a boundary only `[E-52]`. |
| **Procurement Hub** | Excluded from this whole spec programme (owner decision, 2026-08-02). |
| **WordPress / WooCommerce admin behavior behind `↗ View in WP`** | The storefront admin is a separate system; this spec covers only the link and its event `[DC-33]`. |
| **FX conversion** | This page renders each amount in its own currency `[E-68]` `[BR-48]`; no USD conversion is performed or displayed. |
| **Bulk operations across multiple orders** | Order Detail is single-order by definition. Bulk lives on View Orders, RTO and Order Management. |
| **Manual carrier assignment for "Not connected" orders** | No affordance is specified here — the unblocking path is undecided `[PD-55 · NO-DEFAULT]`, §9.2. |
| **"Land scrolled to the relevant section on arrival"** | Raised as an observation in the A-lens plan, which explicitly recorded that **no decision is encoded**. Nothing is specified; the page loads at the top like every other screen. |

### 9.2 Owner questions with NO provisional default

These have **no** specified behavior and none may be invented. One is owned by this page; three are inherited boundaries that this page must display or respect but does not own.

| ID | Question | Owned by this page? | Blocking status here |
|---|---|---|---|
| **`[PD-51 · NO-DEFAULT]`** | **Where is "which sample set and how many" defined, and by whom?** Order Management's sample flow is a deliberate ON/OFF with no sample-type selection, yet `[G-13]` requires internal artifacts — including this page's line-items area `[PD-27]` — to show the sample kind and quantity. No input document names the source of that definition. Deciding it would invent both a UI affordance and an owner. | **Yes** (display requirement lands here) | **Non-blocking for build start, blocking for the sample display.** `[L-10]` states the display requirement; the values it renders have no defined source until this is answered. Order Detail can ship without sample display and gain it later without any other change. `QA-REN-16` is executable today only for its "no control exists" half. |
| **`[PD-55 · NO-DEFAULT]`** | **"Not connected — contact the Fulfillment Center" orders: what unblocks them, and who owns it?** The order is created and appears in RTO, but no screen offers a manual carrier assignment and no Slack route exists for the follow-up. | No — raised on Order Management / RTO | Order Detail must **display** the state and block Outbound and Print against it `[E-86]` `[L-9]`. It invents no assignment affordance. `QA-OUT-11` asserts the block and the absence of a control. |
| **`[PD-74 · NO-DEFAULT]`** | **Correction path when an extra parcel is found AFTER a closing is confirmed.** No reopen/amend affordance exists anywhere, and inventing one changes the immutability model. | No — Closing | Order Detail's Cancel Outbound is allowed at the data layer even after a closing scan, and the divergence is made visible rather than silent `[E-52]`. Reconciling the closing side is out of scope. |
| **`[PD-71 · NO-DEFAULT]`** | **Daily Shipping Status sheet — which sheet and column mapping.** | No — Closing | Stated only as a non-origin in §6.4, so an integration audit does not look for a sheet write here. |

### 9.3 Owner decision deferred beyond v1

- **Role / permission model `[G-15]` `[PD-1 · OWNER-PENDING]`.** v1 ships a single admin role. Order Detail carries several high-trust actions (`✕ Cancel Order`, `Reset Order`, `Delete line`, `Cancel Outbound`, status → `refunded`) that a role model would plausibly gate. The provisional decision is to gate **none** of them and record the actor on every one `[BR-33]` `[E-69]`. If the owner later introduces roles, the affected sentences are `[L-8]` step 3, `[L-F5]`, `[L-F11]`, `[L-M3]` and `[BR-19]` — nothing else changes.
- **Comment edit/delete.** Currently append-only `[PD-3 · OWNER-PENDING]` `[BR-11]`. Reversing it would require deciding what happens to the AI-training corpus's history, which is a doctrine change to `[G-7]`, not a page change.

### 9.4 Decisions explicitly left to development

These are **not** owner questions and are not tracked as PDs. The spec states a default where one is needed; dev may choose freely within it.

| # | Decision | Default / constraint |
|---|---|---|
| D-1 | Idempotency key format and TTL; client debounce interval `[G-9]` | Key = action + order id + line id + client uuid; server dedupe window **≥ 24h**; suppressed duplicates persist as `DC-36` (mandatory, not optional) `[E-70]` |
| D-2 | Toast duration, stacking vs single-slot replacement, generic failure copy `[G-2]` | The success strings in §3.0.2 are the assertable contract; wording may change only if it stays byte-identical across all 8 screens |
| D-3 | Print agent product, timeout value, retry policy, job polling `[G-4]` | Failure must surface as a red toast within the timeout and persist as `DC-25`; no browser-dialog fallback, ever |
| D-4 | Send-sound synthesis parameters and `AudioContext` resume strategy `[G-3]`(a) | Web Audio synthesis only, no external audio files; one sound per **committed** outbound; the sound is never treated as proof `[E-37]` |
| D-5 | Sticky/pinned `Actions` (and `SKU`) column on the 1680px line-items table vs plain horizontal scroll | Usability call; no owner decision is encoded. Whatever is chosen must keep the footer actions reachable **without** horizontal scroll |
| D-6 | Comment freshness mechanism (poll vs push); hub search index scope + debounce `[E-35]` | The thread must refresh on any operator action on the page at minimum |
| D-7 | Actor Log display cap and pagination mechanics `[E-65]` | Newest-first; truncation must be **explicit** (`showing latest {N}`), never silent; full history reachable via `↻ Audit History` |
| D-8 | Storage model for per-user comment read/star state and unread-badge computation `[DC-28]`–`[DC-31]` | Per user + comment key; last write wins on rapid toggles `[E-34]` |
| D-9 | `CP Link` validation strictness `[E-19]` | URL parse minimum; a domain allowlist is optional |
| D-10 | Whether a line delete / add propagates back to WooCommerce | **Must be settled before build.** Either answer is acceptable; an undefined answer creates a silent divergence between WooCommerce and the admin |
| D-11 | Audit-history export encoding and column set; pagination page sizes | Follow the Closing report's CSV precedent |
| D-12 | System-actor naming convention for `DC-14`, `DC-17`, `DC-23`, `DC-32` (`system` / `agent` / `cron`) | Must remain distinguishable from human actors forever `[BR-27]` |
| D-13 | Maximum comment length, if any `[E-30]` | Storage is verbatim; render escapes; no silent truncation |
| D-14 | Confirm-dialog copy for destructive status values, Cancel Outbound, Cancel Inbound, Clone, Reset and Cancel Order | Each must name the specific consequence, not a generic "Are you sure?" — except `[L-M3]`, whose copy is fixed by the wireframe. Reset's dialog must state that a queued print job is not recalled `[E-84]` |
| D-15 | Bulk-inbound chunk size for large orders `[E-87]` | Invisible to the operator: one submission, one `DC-12`, one toast, regardless of chunking |
| D-16 | Autocomplete behavior for `@mention` in the composer | Presence and debounce are free; the **parse contract** (`mentions[]`, `unresolved_mention_tokens[]`, deduplication, self-mention suppression) is not `[E-28]` `[E-60]` `[E-80]` |
| D-17 | Retry policy for Slack dispatch (backoff, attempt cap) | Every attempt's result persists on `DC-27`; the primary action never waits on it `[PD-4 · OWNER-PENDING]` |
| D-18 | **Carrier tracking-sync cadence and scheduling owner** `[L-6]` `[DC-23]` — how often a sync runs and who schedules it is specified nowhere in the input documents (raised as `order-detail.A` OQ-11, only half of which reached D-12) | Cadence is free **provided it is observable in `DC-23`**: the `(synced …)` marker must always reflect the last **successful** sync, a failed sync keeps the previous timestamp and persists its failure result, and a fabricated time is never displayed `[E-43]`. The feed stays inbound-only §6.5 |
| D-19 | **Self-mention Slack suppression** `[L-1]` step 9 `[E-60]` — whether a human's `@self` in a free-text comment notifies the author. `[PD-16]` decides only the match-pipeline auto-comment; no owner decision covers this case | **Default: suppress**, recorded as `DC-27.suppressed_reason=self_mention`, by analogy with the resolver == registrant suppression. The comment itself always posts normally. If the owner later registers the question, `[L-1]` step 9, `[E-60]` and `QA-CMT-10` take the tag together |
| D-20 | **`No label yet` guard style** `[E-40]` `[L-13]` `[L-F7]` — disabled-with-reason vs an error toast when Print / View Label has no label, and the same question on a cancelled order `[E-85]`. Raised as an owner question (`order-detail.B` Q-A5) with no register entry | **Default: disabled with the reason rendered next to the control**, consistent with `[BR-46]` and with `[E-7]`'s "a disabled control teaches the precondition". A forced request still persists `DC-9` so the guard is measured `[BR-47]` |

### 9.5 Wireframe work implied by this spec (backlog — not to be applied during spec writing)

Handled by the wireframe-edit pass after P3-3/P3-4, deployed via `/wf-deploy order-detail`. None of these is a spec gap; each is a drawing the spec is ahead of.

- The **Cancel Outbound** control `[BR-19]` `[PD-26 · OWNER-PENDING]` is specified but not drawn. It replaces `📦 Outbound` in the footer once the order is outbounded.
- The **disabled-with-reason** renderings are specified but not drawn: `Cancel Inbound` after outbound `[E-10]`, `+ Add Line Item` after outbound `[E-25]`, `🖨 Print` / `View Label` with no label `[E-40]` or on a cancelled order `[E-85]`, `Delete` on an inbounded line `[E-22]`, `📦 Outbound` and `🖨 Print` on a carrier-less order `[E-86]`, `Bulk Inbound Selected Items` with zero selection `[E-7]`.
- The **sample-set display** `[PD-27 · OWNER-PENDING]` is specified but not drawn, and is gated on `[PD-51 · NO-DEFAULT]`.
- The **hold-reason input** on the status change `[PD-20 · OWNER-PENDING]` and its rendering inside the banner are specified but not drawn.
- The **Actor Log empty state** `[E-42]` and the explicit **truncation marker** `[E-65]` are specified but not drawn.
- **Demo-data correction (candidate, not registered in `_wireframe-fixes`):** the three Actor Log inconsistencies in §2.5 B — the `OUTBOUND` row on an order rendered `Processing` with Outbound still enabled; the `CANCEL INBOUND` with no later re-inbound on a row rendering `INBOUNDED`; and State 2 carrying the same `OUTBOUND` row while a line is `PENDING`. All three are illustrative, none is a behavioral statement.
- **`[OD-WFX-1 · proposed]` (this page):** the **Change Status dropdown must close on an outside click**. `order-detail/index.html` has a backdrop handler for the modal but no document-level handler for the dropdown, so it stays open (measured 2026-08-03). The specified behavior `[L-8]` step 1 `[E-46]` is unchanged; the drawing is missing it. Until the handler lands, `QA-STA-4` is tagged `[ADMIN]` §8; applying the fix flips it back to `[WF]` with no edit to the scenario. Registered in `_wireframe-fixes.md` §I.
- `[WF-3]` (cross-page): once the owner confirms `[PD-10]`, the View Orders State 3 legend must drop the "(proposal)" qualifier; Order Detail's `[BR-14]` already assumes the adopted rule.

---

## 10. Decision Log

Every decision that shaped this screen, 2026-07-09 → 2026-08-03, including reversals and removals. Commit hashes are from `yongwon-pixel/skinseoul-wireframes`.

### 10.1 Chronological record

| Date | Decision | Source / evidence |
|---|---|---|
| 2026-07-09 | WMS 2.0 wireframe programme opens; 3-channel deploy rule established (repo → artifact → GitHub Pages via `/wf-deploy {slug}`); Order Detail listed as screen 2 | plan `2026-07-09-wms2-wireframes.md` |
| 2026-07-09 | **"Cancel Inbound disabled after Outbound — Cancel Outbound first" recorded as a proposal**, not yet a rule | View Orders design decisions, carried to Order Detail |
| 2026-07-09 | **Deleo Tracking No. removed from View Orders but retained on Order Detail** — deliberate asymmetry, flagged for the developer handoff `[BR-9]` | plan ledger |
| 2026-07-13 | First draft of Order Detail generated in the 9-screen batch; inherits the View Orders v20 design system | commit `1bbba3a` |
| 2026-07-13 | Sourcing routes unified to 4 (`SMART BUY` / `JIT` / `WHOLESALE` / `PARTNERSHIP`) | plan ledger, scope expansion |
| 2026-07-14 | **Real-capture rework** against the live admin, Order #407847: horizontally scrolling Line Items, sourcing-route badges, upgraded comments, **Actor Log introduced (new)**, button enablement rules | commit `9844fe0` |
| 2026-07-14 | Sourcing-route badges made **colorless black bold** on Order Detail + Order Management, matching View Orders | commit `f652a97` |
| 2026-07-14 | **"Request Inbound" retired**; inbound becomes per-product, outbound stays order-level `[BR-4]` | legend 2 |
| 2026-07-14 | Editable-field whitelist fixed at the 5 agent-tracking fields; WooCommerce commerce fields not editable here `[BR-25]` | legend 12 |
| 2026-07-14 | WooCommerce originals (`*`) preserved permanently beside recalculated values `[BR-26]` | line-items inline note |
| 2026-07-21 | **Full live capture** alignment: address fields restored, nav corrected, tracking display simplified | commit `a95e5db` |
| 2026-07-21 | **Print label de-suffixed**: `Print (YUN)` → `Print`; the carrier badge already states the carrier `[L-13]` | commit `ce3eb96` |
| 2026-07-21 | **PIC pencil replaced with a bordered `✎ Edit` button** — the glyph was unreadable as a control on the floor `[L-5]` | commit `2b8ab1d` |
| 2026-07-21 | **Double-click bug moved to the developer handoff notes**, deliberately not annotated in the wireframe; becomes `[G-9]` | plan ledger, handoff note A |
| 2026-07-21 | **Photo upload for unrecognized barcodes put on hold** (removed from the View Orders modal); later confirmed permanently removed `[PD-63]`. Never existed on Order Detail | handoff note F |
| 2026-07-22 | **Line Items column cleanup**: `Delivery Company` and `Comments` columns removed; header rowspan alignment; KR brand notation `[BR-8]` | commit `9c1f2a7` |
| 2026-07-22 | **Outbound relabelled** `Outbound to Deleo BaroShip` → `Outbound`, and its enable rule annotated (dot 9); tracking meta commentary moved to dot 6 | commit `cedd8d5` |
| 2026-07-22 | Edit-mode row, delete-confirmation modal (M3), Change Status dropdown and Print label annotation added | commit `4672ec4` |
| 2026-07-22 | Line-items header `Inbound Request` column **replaced by the select-all checkbox**; `Product Name (EN)` column restored | commit `0ebeb9f` |
| 2026-07-22 | **@tag modal on Add Comment removed** — clicking `Add Comment` now appends to the thread immediately with @-token highlighting | commit `65b7563` |
| 2026-07-22 | `data-open` handler fixed so the Change Status dropdown actually toggles (parity with View Orders) | commit `5244851` |
| 2026-07-22 | **On Hold state view added** (dot 14): amber badge, hold banner, Outbound disabled, per-row Inbound still allowed | commit `a5d9003` |
| 2026-07-22 | Page restructured into **two full state tabs** — `1 · Processing (default)` / `2 · On Hold`. A demo device, not a product feature `[BR-45]` | commit `c17df7c` |
| 2026-07-22 | Comments hub item click defined as "opens the order" across View Orders and Order Detail `[G-12]` | commit `3e251fe` |
| 2026-07-23 | **Per-row Inbound / Cancel Inbound buttons** land in the Actions cell (3-screen rework) `[L-2]` | commit `4eeebc7` |
| 2026-07-23 | JIT sourcing route gains the **purchase-channel parenthetical** — `JIT (Coupang)` / `(Naver)` / `(Other retail)` | commit `7c12bc2` |
| 2026-07-23 | Order Detail section tags restored | commit `d7a5728` |
| 2026-07-23 | **REVERSAL — `Latest Inventory Count` restored** after being removed in the column cleanup; returned to the live screen's position as the first column of the Inventory group, in **both** states. JIT rows legitimately show `0` `[BR-7]` | commit `bbaa96f` |
| 2026-07-23 | **REVERSAL (cross-page, affects `[G-13]` references here) — sample assignment**: the 2026-07-22 note recording sample assignment as "removed" was superseded within a day by the 2026-07-23 ON/OFF redesign, reconfirmed 2026-08-03. The 2026-07-22 note was stale, not a decision | plan ledger, handoff note G |
| 2026-07-29 | **Comments hub all-orders search added** — every comment across every order, newest first, purple `<mark>` highlight, click opens the order, clearing the input restores the previous tab. 8 sites on View Orders + 2 on Order Detail | commit `8e5abeb` |
| 2026-08-02 | Phase 1 consistency sweep: Order Detail's hub badge normalized to unread-count `2` (was `3`) `[BR-44]`, a stale JS comment corrected (`Completed / On Hold` → `Processing / On Hold`), hub search empty-state wording aligned | commit `d88673c` |
| 2026-08-02 | Developer handoff notes published in Notion (6 implementation notes, incl. the double-click bug and the local print agent requirement) | plan ledger |
| 2026-08-02 | Procurement Hub excluded from this spec programme entirely | owner decision |
| 2026-08-03 | **KR brand normalization** — all Korean product-name cells now carry the **EN brand form in bold** (`닥터자르트` → `Dr.Jart+`); 72 cells across the wireframe set `[L-11]` | commit `f8c4bae` |
| 2026-08-03 | **Legend 14 gains the combined-case clause** — the demo is deliberately Hold **+** incomplete inbound (3/4), proving Outbound can be disabled for multiple independent reasons `[BR-3]` | commit `f8c4bae` |
| 2026-08-03 | **Englishization** of Order Detail — 90 substitutions; Korean product names, carrier names and company names kept verbatim as data `[G-6]` | commit `8beb374` |
| 2026-08-03 | **`[G-2]` owner emphasis** — every confirming action shows a top-right toast; no full-page refresh (RTO Bulk Outbound is the sole system-wide exception, not on this page) | owner, plan ledger |
| 2026-08-03 | **`[G-4]` reconfirmed** — every Print button outputs the label instantly, carrier-agnostic, no browser dialog; local print agent required | owner, plan ledger |
| 2026-08-03 | **`#fulfillment-admin-comments` (`C0BMGEWM5QA`) confirmed** as the comment-@mention channel; the owner created it. Supersedes the "channel pending" wording in the earlier drafts `[C-2]` | `_slack-routing`, owner |
| 2026-08-03 | **`[G-3]`(a) scope resolved** — the send sound applies to every outbound-class button on every page, including Order Detail's `📦 Outbound` `[C-5]` `[PD-2 · OWNER-PENDING]` | `_review.md` §1 |
| 2026-08-03 | **Auto-outbound boundary resolved** — full inbound auto-outbounds only in the View Orders scan/bulk flow; Order Detail's Outbound is always a manual click `[C-7]` `[PD-21 · OWNER-PENDING]` `[BR-5]` | `_review.md` §1 |
| 2026-08-03 | **Route taxonomy boundary resolved** — order-facing badges stay at 4; `OTHER (channel)` is inbound-origin only and never renders on Order Detail line items `[C-3]` `[PD-80 · OWNER-PENDING]` | `_review.md` §1 |
| 2026-08-03 | **`[G-2]` beats wireframe omissions** — removals get confirm + toast even where the wireframe is silent `[C-6]` `[PD-5 · OWNER-PENDING]` `[BR-39]` | `_review.md` §1 |
| 2026-08-03 | **"Cancel Inbound after outbound" adopted as a rule** (was a 2026-07-09 proposal) — Cancel Outbound must run first `[PD-10 · OWNER-PENDING]` `[BR-14]`; the View Orders legend still says "(proposal)" `[WF-3]` | supervisor ruling |
| 2026-08-03 | Guard doctrine settled for the destructive actions on this page: Cancel Order blocked with inbounded lines `[PD-22]`, line delete blocked when inbounded `[PD-23]`, last-line delete allowed `[PD-24]`, add-line blocked after outbound `[PD-25]`, Cancel Outbound present `[PD-26]`, Reset scoped to shipment only `[PD-30]`, Clone copies lines + addresses only `[PD-31]`, tracking duplicate warns-and-allows without reprinting `[PD-32]`, PIC is a picker with no auto-notify `[PD-33]`, hold reason optional `[PD-20]`, destructive statuses confirm `[PD-28]`, outbound allowed only from `processing`/`pending` `[PD-29]`, sample shown internally `[PD-27]` — all **OWNER-PENDING** | `_provisional-decisions.md` §C |
| 2026-08-03 | **`[G-15]` created** — v1 ships a single admin role; no role gating on any screen `[PD-1 · OWNER-PENDING]` | `_review.md` §4 GD-8 |
| 2026-08-03 | Spec template fixed at 10 sections; specs are written to be read end-to-end by AI agents running QA | owner, plan ledger |
| 2026-08-03 | **Spec v1.1 audit corrections** (this document): the line-items table is **18 columns, not 20** — both planning lenses were approximate `[BR-42]`; per-line inbound declared all-or-nothing so no second partial-receipt path is invented `[BR-41]`; the four coexisting time formats fixed as a contract with an explicit timezone invariant `[BR-43]`; the three Actor Log demo-data inconsistencies recorded so QA does not derive rules from them (§2.5 B); all `[WF]` QA selectors state-scoped, because both states are always in the DOM (§8.0) | spec audit, 2026-08-03 |
| 2026-08-03 | **Spec v1.2 remediation** (this document), from three independent verification passes — coverage audit, adversarial QA execution against the live wireframe, and the cross-page/`_review` audits. Behavioral additions: Cancel Inbound restocks the full line qty with no Yes/No and no qty input `[BR-49]`; there is no `OUTBOUNDED` line status `[BR-50]`; cancellation is a flag and the 8 statuses are values rendered as title-case labels `[BR-12]`. QA: `QA-INB-3` and `QA-OUT-3` rescoped to the product surface so they stop forbidding legend text that `QA-MAP-5` requires; `QA-DC-9` corrected to seven distinct reason codes across eight guards; a text-extraction contract added to §8.0 (annotation `.dot` text stripped, `<br>` normalized, `reads exactly` vs `reads` defined) because eight scenarios flipped verdict on the runner's private convention; `QA-STA-4` retagged `[ADMIN]` behind the new `[OD-WFX-1 · proposed]`; 14 scenarios added to close 18 of 19 uncovered edge cases, with §8.4 stating the one deliberate exclusion. Bookkeeping: `[PD-19]` dropped from `BR-28`, the sample-set clone exclusion recorded as a `[G-13]` extension rather than PD-31 content, self-mention suppression and the `No label yet` guard recorded as dev defaults (D-19, D-20) because no register entry exists for either, tracking-sync cadence added as D-18, and nine open cross-page conflicts recorded as `[X-1]`–`[X-9]` in §2.7 | `_verify/m1-order-detail.md`, `_verify/m2-order-detail.md`, `_verify/m3a-cross-page.md`, `_verify/m3b-review-audit.md` |

### 10.2 Removed features — must NOT exist

Recorded so nobody re-implements them from a stale capture or an old document `[BR-40]`. Each has a negative QA assertion.

**Scope of those assertions (corrected 2026-08-03).** They forbid the removed item **as a rendered control** — a button label, a header cell, body text in `#st-normal` / `#st-hold`. They do **not** forbid the wireframe legend from *naming* what was retired: legend items 2 and 9 exist precisely to record `"Request Inbound" name retired` and `"Outbound to Deleo BaroShip" → relabeled`, and `QA-MAP-5` requires that text. Asserting against the whole document would put `QA-INB-3` / `QA-OUT-3` in direct contradiction with `QA-MAP-5` — as both did before this correction — and would make an unaided QA agent file two bug reports against a correct drawing.

| Removed item | Replaced by | Removed on | Asserted by |
|---|---|---|---|
| **"Request Inbound"** button name | per-row `Inbound` / `Cancel Inbound` + `Bulk Inbound Selected Items` `[L-2]` | 2026-07-14 | QA-INB-3 |
| **"Outbound to Deleo BaroShip"** button label | `📦 Outbound` `[L-9]` | 2026-07-22 | QA-OUT-3 |
| **`Print (YUN)` / `Print (DELEO)`** carrier-suffixed labels | `🖨 Print` + adjacent carrier badge `[L-13]` | 2026-07-21 | QA-PRT-1 |
| **`Delivery Company` column** in Line Items | nothing — deleted `[L-10]` | 2026-07-22 | QA-REN-2 |
| **`Comments` column** in Line Items | the Operator Comments section, single home `[L-1]` | 2026-07-22 | QA-REN-2 |
| **`Inbound Request` header column** in Line Items | the select-all checkbox `[L-F13]` | 2026-07-22 | QA-INB-3, QA-REN-2 |
| **Bare `✎` pencil glyph** as the PIC control | bordered `✎ Edit` button `[L-5]` | 2026-07-21 | QA-SUB-4 |
| **@tag modal on Add Comment** | immediate append to the thread with @-token highlighting `[L-1]` | 2026-07-22 | QA-CMT-3 |
| **Korean brand form `닥터자르트`** in KR name cells | EN brand form in bold `[L-11]` | 2026-08-03 | QA-REN-6 |
| **Comment edit / delete controls** | append-only; corrections are new comments `[BR-11]` | never existed; stated to prevent addition | QA-CMT-15 |
| **Photo upload / photo column** for unrecognized items | permanently removed system-wide `[PD-63]`; never present on Order Detail | 2026-07-21 hold → 2026-08-03 removal | — (cross-page) |
| **Any scan input** | none — Order Detail is not a scan surface `[BR-30]` `[G-1]` | never existed; stated to prevent addition | — (spec-level `[BR-30]`) |
| **Any per-line quantity input on inbound** | per-line inbound is all-or-nothing `[BR-41]`; partials belong to View Orders State 6 | never existed; stated to prevent addition | QA-INB-14 |
| **`OTHER (channel)` route badge** on order line items | order-facing badge set stays at 4 `[G-5]` `[C-3]` | never existed; stated to prevent addition | QA-REN-5 |

### 10.3 Reversal chains (recorded verbatim so nobody re-litigates them)

1. **`Latest Inventory Count`**: present in the live admin → **removed** during the 2026-07-22 Inventory column cleanup → **restored** 2026-07-23 (commit `bbaa96f`) at the live screen's exact position, in both states, with the explicit note that `0` on a JIT line is correct. Current state: **present** `[L-10]` `[BR-7]`.
2. **Sample assignment** (cross-page, referenced here via `[G-13]` / `[PD-27]`): **removed** 2026-07-22 → **reinstated as simple ON/OFF with multiple overlapping periods** 2026-07-23 → **reconfirmed** 2026-08-03. The 2026-07-22 "removed" note was stale within a day; Notion §G and the handoff note were corrected on 2026-08-03. Current state: **ON/OFF, exactly one sample set per order**.
3. **"Cancel Inbound disabled after Outbound"**: **proposed** 2026-07-09 → left in proposal state through July → **adopted as a rule** 2026-08-03 `[PD-10 · OWNER-PENDING]`. The View Orders legend still carries the "(proposal)" qualifier, which is a wireframe defect `[WF-3]`, not a live ambiguity. Current state: **adopted** `[BR-14]`.
4. **Comment-mention Slack channel**: drafted as "channel pending owner" in `global-rules-draft` and `decision-sources` → **confirmed 2026-08-03** as `#fulfillment-admin-comments` (`C0BMGEWM5QA`), owner-created `[C-2]`. Current state: **confirmed**; "pending" must never be written for this row again.
5. **Comments hub search**: did not exist → **added 2026-07-29** (commit `8e5abeb`) as an all-orders search, not a tab filter → empty-state wording normalized 2026-08-02 and englishized 2026-08-03. Current state: **present, all-orders scope** `[L-7]`.
6. **Hub unread badge value**: rendered `3` in the wireframe demo → **corrected to `2`** on 2026-08-02 so the badge equals the number of unread items actually rendered `[BR-44]`. Current state: **`2`** — QA asserts `2`, and a `3` is a regression (`QA-HUB-2`).
7. **Line-items column count**: described as "20 columns" in both P3-1 planning lenses and in spec v1.0 → **corrected to 18** in spec v1.1 against the wireframe markup (§2.5 C). The `DC-15` snapshot requirement was simultaneously reworded from "all 20 columns" to "every field of the line record", which is the durable form. Current state: **18 rendered columns** `[BR-42]`, asserted by `QA-REN-1`.

---

*End of specification. 15 legend units + 17 page-furniture units = 32 specified units · 50 business rules · 37 persisted events + 16 non-events · 92 edge cases · 161 QA scenarios (68 `[WF]` · 93 `[ADMIN]`) · 9 open cross-page conflicts `[X-1]`–`[X-9]`.*
