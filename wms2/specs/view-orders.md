# View Orders — Screen Specification

> **Decision status update (2026-08-03)** — PD-1 through PD-8, 51, 55, 66, 71, 74, 79 are now **OWNER-DECIDED** (PD-6 confirmed 2026-08-03 — the owner decision round is fully closed); any inline `[PD-{these} · OWNER-PENDING]` or `[PD-{these} · NO-DEFAULT]` tags below are superseded — see `_provisional-decisions.md` for the decisions.

**Page slug:** `view-orders` · **Wireframe SST:** `wms2/view-orders/index.html` (v21, 1,854 lines)
**Live wireframe:** https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/view-orders/
**Spec version:** 1.3 (owner review — M1 restock location) · **Written:** 2026-08-03 · **Template:** `_inputs/spec-template.md` v1
**Global rules:** `_global-rules.md` v1.0 — cited as `[G-n]`; this document states **page deltas only** and never restates a rule body.
**Provisional decisions:** `_plans/_provisional-decisions.md` — behaviors resting on an unapproved decision are tagged `[PD-n · OWNER-PENDING]` in the sentence where they appear.
**Known wireframe defects:** `_plans/_wireframe-fixes.md` — this spec describes the **correct** behavior; where the shipped wireframe text disagrees, the defect is named inline (`WF-n`).
**Review adjudications:** `_plans/_review.md` — conflicts C-1…C-12 and the binding writing conventions of §3 are applied throughout.
**Cross-page disagreements:** where another screen spec contradicts this page, the item is listed in **§9.5** with this page's position and what must change where. Nothing in §3–§8 depends on their resolution.

---

## 1. Purpose & Users

### 1.1 What this screen is

View Orders is the **single scan hub** of WMS 2.0. Every barcode that enters the warehouse — a customer order's courier tracking label, a product's own EAN barcode, a supplier's inbound-shipment tracking label, a returned parcel's last-mile barcode, a Coupang QR sticker — is typed into one input on this page, and the page decides on its own what the operator is holding and switches to the matching screen. There is no mode selector, no dropdown, no "what kind of number is this?" question. The operator scans; the screen follows.

The page serves five operational moments in one surface:

| Moment | States | What the operator is physically doing |
|---|---|---|
| Customer-order goods receipt → shipment | 1, 1b, 2, 3 | Opening courier boxes at the receiving table, scanning each product into its order, then releasing the order to the outbound lane |
| Customer return intake | 4 | A returned parcel came back; deciding what physically goes back on the shelf and what is written off |
| Held order | 5 | A parcel is on the table but CS has frozen it; the operator must be stopped before it ships |
| Internal stock intake (supplier / wholesale / partnership / smart-buy pallets) | 6, 6b | Standing in front of a pallet or a stack of boxes, counting units into the warehouse against an Inbound Request |
| Exception handling | Modals M1–M6 | Something is wrong: unknown barcode, damaged goods, short delivery, wrong quantity, supplier return |

### 1.2 Users

- **Warehouse operators** (primary; Dean, Miranti, Aldo in the wireframe data) — hands on boxes, scanner in the dominant hand, packing tape and a cutter in the other. They spend >90 % of their time on this page.
- **Order team / fulfilment leads** — use States 1–3 to unblock JIT orders and States 6/6b to reconcile inbound requests they raised.
- **CS** — do not operate this page; they apply Hold elsewhere (see §9) and read its effect here (State 5) and through comments.
- **Permissions:** v1 has a single admin role — no per-action gating anywhere on this page; the actor is recorded on every mutation `[G-15]` `[PD-1 · OWNER-PENDING]`.

### 1.3 The operator's physical reality (this is what shaped the design)

These are not preferences. Each one forced a specific decision that appears in §3 and §4.

1. **The scanner types and presses Enter by itself.** The operator never touches the keyboard between scans. `[G-1]` exists because of this: a single lost focus event means the next scan is typed into a comment box, a shelf field, or nowhere — and the operator does not notice until several boxes later. Focus discipline is the number-one field bug class for this page, which is why `[BR-30]` states the invariants as testable rules rather than leaving them to implementation.

2. **The eyes are on the box, not on the monitor.** During continuous scanning the operator is reading a shipping label 20 cm from their face while the screen is 60–100 cm away and often at an angle. They cannot read a toast while scanning. This is why acceptance is confirmed **by ear**: outbound-class buttons play a rising sweep `[G-3a]` `[PD-2 · OWNER-PENDING]`, and State 6 plays a **different, harsher warning tone** when a scanned product does not belong to the open inbound request `[G-3c]` — the operator hears "wrong pallet" without looking up.

3. **Attention is bought in one glance from ~2 m.** Colour therefore carries meaning at a distance, not decoration: amber = "look, quantity is not 1" (`.qty-warn`, `[L-S1-7]`), red banner = customer return (`[L-S4-1]`), amber banner = hold (`[L-S5-1]`), purple banner = internal inbound, not a customer order (`[L-S6-2]`), green = done. Sourcing routes are deliberately **not** coloured — four coloured pills would compete with those five signals, so routes render as plain black bold text `[G-5]`.

4. **Horizontal scrolling is impossible with a scanner in one hand.** The page's side padding was reduced on 2026-07-09 specifically so that all 14 table columns and every action button fit one 1280 px-class screen `[L-S1-4]`. A developer who re-adds padding, or adds a column, breaks the operator's workflow — see the column-set rule `[BR-39]`.

5. **The last box of an order is the busy moment.** When only one item remains uninbounded, the operator will inbound it and immediately want it gone. That is why the row button *becomes* `Inbound + Outbound` at exactly that moment `[L-S1-8]` and why a full inbound auto-triggers outbound in the scan/bulk flow `[BR-6]` — it removes a click, a mouse travel, and a decision from the busiest second of the day.

6. **Single-item orders are the volume driver.** They are picked, packed, and labelled in one motion, so their label prints the instant the barcode is scanned, with no click at all `[L-S1-Fa]` — which is the reason this page is a `[G-4]` print surface at all.

7. **Pickers read Korean faster than English.** Supplier-return labels printed from M4 carry the **Korean** product name, the Korean carrier name, size and quantity `[G-6]` — the label is a physical object handled by a Korean courier driver, so its content is data, not UI copy, and is never translated.

8. **Gloves, tape, and speed make destructive clicks cheap.** Every quantity-changing modal therefore ships with a safe default (restock qty defaults to **0** in M3, cancel-restock defaults to the exact inbounded qty in M1) so that a mis-click costs nothing, and every confirming action ends in a stated confirmation `[G-2]`.

9. **Two people work the same pallet.** State 6 counting is a running total, so concurrent scans from two stations must **merge** server-side rather than fight over a version number `[PD-7 · OWNER-PENDING]`.

10. **Labels arrive destroyed.** Bulk boxes come in with the tracking label torn, soaked, or covered by another sticker. The Expected Inbound badge on State 0 exists purely so that an operator with an unreadable label can open the reconciliation screen by clicking a row instead of scanning `[L-S0-2]`.

---

## 2. Screen Inventory & Wireframe Map

### 2.1 Declared unit count

This page's spec covers **69 units**:

- **58 wireframe legend dots** — the implementation units. Counted directly from the shipped HTML: State 0: 2 · State 1: 21 · State 1b: 1 · State 2: 2 · State 3: 4 · State 4: 6 · State 5: 3 · State 6: 9 · State 6b: 2 (**50 state dots**) + **8 modal dots** (`M1`, `M2`, `M2b`, `M3`, `M3b`, `M4`, `M5`, `M6`).
- **3 off-screen normative footer blocks** — legend paragraphs that carry rules but have no dot: `[L-S1-F]`, `[L-S5-F]`, `[L-S6-F]`. They are keyed and specced because losing them loses real rules. (Only these three legends have trailing paragraphs; States 0, 1b, 2, 3, 4, 6b have none.)
- **8 page-furniture units** `[L-F1]`–`[L-F8]` — on-screen controls with no legend dot, keyed per `_review.md` §3.1 so that nothing rendered on the screen is unspecified: global nav, page heading/section labels, order header card, order `🖨 Print` button, `🔍 Search` button, State 0 waiting placeholder, row checkboxes, result counter.

> **Delta from spec v1.0:** v1.0 declared 67 units with 6 furniture keys. The audit found two rendered, rule-bearing elements with no key — the page heading/section labels (`WMS - View Orders` / `Search Orders` / `Search Results`) and State 0's `Waiting for scan` placeholder panel. They are now `[L-F7]` and `[L-F8]`; the total is **69**.

**Numbering gaps and quirks (declared so coverage checks do not flag phantom holes):**

- State 1's dots run 1–20 **and 22**; there is no dot 21 in State 1. Dot **21 lives in State 1b** (the "plain Inbound button" rule). This is intentional: 1b is a variant of State 1 and continues its numbering. In the shipped HTML the State 1 legend list renders in the order 1…19, **22**, **20** — a source-order artefact, not a missing item.
- Legend numbers **repeat across states** (every state has its own "1"). Spec keys are therefore always state-qualified: `[L-S3-1]` ≠ `[L-S2-1]` ≠ `[L-S6-1]`.
- State 4 dots **3** and **4** describe rules that render inside modal M3 and have **no on-screen dot in State 4**; the legend text says so explicitly ("see modal M3 — no on-screen dot"). State 4 therefore shows 4 dots on screen (1, 2, 5, 6) for 6 legend entries. Dots 3 and 4 are specced under State 4 and cross-referenced from `[L-M3]`.
- Modal M3b is a sub-dot of M3 (the shared memo field) and is keyed `[L-M3b]`; M2b is a sub-dot of the unrecognized flow and is keyed `[L-M2b]` — both per the `[L-M{n}{letter}]` convention.
- **`[L-S1-F]` holds three rules and is sub-keyed** `[L-S1-Fa]` (single-item auto-print), `[L-S1-Fb]` (unrecognized-scan routing) and `[L-S1-Fc]` (inbound-request tracking → State 6), per `_review.md` §2c-4's "suffix a/b/c when a footer holds multiple rules". The sub-keys are **not additional units** — `[L-S1-F]` remains one unit of the 69. `[L-S5-F]` and `[L-S6-F]` each carry a single rule set and are not sub-keyed. The parenthesised form `[L-S1-F(a)]` used in spec v1.1 is retired; it was a third key format and is not a convention.
- There is no modal "M7" and no dot numbered above 22 anywhere on this page.

### 2.2 State map

Reach every state from the purple wireframe chrome bar at the top of the live page. Button labels below are byte-exact.

| # | State / modal | DOM id | Reach it by clicking | Legend keys | §3 anchor |
|---|---|---|---|---|---|
| 0 | Waiting (before scan) | `#s0` | `0 · Waiting (Before Scan)` (default on load) | `[L-S0-1]` `[L-S0-2]` | §3.1 |
| 1 | Scan result — last item remaining | `#s1` | `1 · Scan Result (Last Item Remaining)` | `[L-S1-1]`…`[L-S1-20]`, `[L-S1-22]`, `[L-S1-F]` | §3.2 |
| 1b | Scan result — normal (2 remaining) | `#s1b` | `1b · Scan Result (Normal — 2 Remaining)` | `[L-S1b-21]` | §3.3 |
| 2 | All inbounded | `#s2` | `2 · All Inbounded` | `[L-S2-1]` `[L-S2-2]` | §3.4 |
| 3 | Outbound complete | `#s3` | `3 · Outbound Complete` | `[L-S3-1]`…`[L-S3-4]` | §3.5 |
| 4 | Customer return mode | `#s4` | `4 · Customer Return Mode` | `[L-S4-1]`…`[L-S4-6]` | §3.6 |
| 5 | Hold order | `#s5` | `5 · Hold Order` | `[L-S5-1]`…`[L-S5-3]`, `[L-S5-F]` | §3.7 |
| 6 | Internal inbound (inbound request) | `#s6` | `6 · Internal Inbound (Inbound Request)` | `[L-S6-1]`…`[L-S6-9]`, `[L-S6-F]` | §3.8 |
| 6b | Internal inbound complete | `#s6b` | `6b · Internal Inbound Complete` | `[L-S6b-1]` `[L-S6b-2]` | §3.9 |
| M1 | Cancel Inbound (restock confirm) | `#m-cancel` | `Modal: Cancel Inbound`, or any row `Cancel Inbound` button | `[L-M1]` | §3.10 |
| M2 | Unrecognized barcode — order-number lookup | `#m-unrec` | `Modal: Unrecognized Barcode` | `[L-M2]` | §3.11 |
| M2b | Send to Missing Tracking List | `#m-unrec2` | `Modal: Send to Missing Tracking List`, or M2 → `No order number` / `Send to Missing Tracking List` | `[L-M2b]` | §3.12 |
| M3 | Customer return restock | `#m-restock` | `Modal: Customer Return Restock`, or State 4 → `Restock Selected to Warehouse (3)` | `[L-M3]` `[L-M3b]` | §3.13 |
| M4 | Print return labels (supplier return) | `#m-retlabel` | `Modal: Return Label`, or States 1/1b/2/3 → `🖨 Print Return Labels (2)` | `[L-M4]` | §3.14 |
| M5 | Save partial inbound | `#m-partial` | `Modal: Save Partial Inbound`, or State 6 → `Save Partial Inbound` | `[L-M5]` | §3.15 |
| M6 | Edit expected qty | `#m-qtyedit` | `Modal: Edit Expected Qty`, or State 6 → any `✎` (`button.qedit`) | `[L-M6]` | §3.16 |
| — | Page furniture (all states) | — | — | `[L-F1]`…`[L-F8]` | §3.17 |

State visibility is `.state{display:none}` / `.state.on{display:block}`; overlays are `.overlay{display:none}` / `.overlay.open{display:flex}`. The chrome bar's `Hide annotations` button (`#annoToggle`) toggles `body.no-anno`, hiding all dots and legends. The chrome bar is **wireframe chrome only** and must not exist in the admin.

### 2.3 Wireframe demo limitations (not defects; QA must tag these `[ADMIN]`)

These are artefacts of a static HTML mock. They are listed so that an automated QA agent does not file them as bugs, and so that no `[WF]` scenario is written against behavior the mock cannot produce.

- **L-1** No state actually transitions on scan. Typing in the search input does nothing; states are switched only by the chrome tabs. All resolution/branching assertions are `[ADMIN]`.
- **L-2** Disabled buttons are styled `.btn-gray` (`cursor:not-allowed`) but carry **no `disabled` attribute** and **no `pointer-events:none`**, so they remain clickable. In the admin, a disabled control must produce **no** sound, **no** request, and **no** state change. *(Candidate addition to the `_wireframe-fixes` backlog.)*
- **L-3** The floating Live Barcode Feed (`#scanfloat`) exists only inside `#s1` markup, so it disappears with the state despite being `position:fixed`. It is specified as present on States 1–6b.
- **L-4** The Inbound/Outbound Log (`.logsec`) is rendered in States 1, 2, 3, 4, 5 but **not** 1b. It is specified as present on States 1–5 including 1b.
- **L-5** Modal demo data is scaffolding: M6's header reads `Inbound No. 202607120002` while State 6's banner reads `202607120001`. This is **intended renumbering**, not a contradiction (`_review.md` adjudicated non-issue).
- **L-6** Toasts are static markup in States 1, 3, 6b; they do not appear in response to actions. Only `#unrecToast` (M2 match) and `#gtoast` (M2b send) are behaviourally wired.
- **L-7** Checkboxes, `🔍 Search`, `🖨 Print`, `Export by date`, `Post`, and `Mark all read` are inert.
- **L-8** The scanned row is **not** sorted to the top in the mock: `#s1`'s `.row-hit` (SKU `100005104`) is rendered as the **second** `tbody` row. `[L-S1-5]`'s sort-to-top half is therefore `[ADMIN]`; only the highlight half is `[WF]`.
- **L-9** Clicking an Expected Inbound row switches `#s6` on but does **not** update the chrome bar — the tab `0 · Waiting (Before Scan)` keeps class `on`. Assert the `section`, never the tab, in that scenario.
- **L-10** Both `button.qedit` rows open the **same** hardcoded M6 (SKU `1025 Dokdo Cleanser`, `Inbound No. 202607120002`) regardless of which row was clicked. In the admin, M6 is bound to the clicked row.
- **L-11** The send-sound handler is bound by button **text match** (`/Outbound/ && !/Cancel/ && !/Outbounded/`), so it also binds to the greyed `Outbound` in States 1/5 and the greyed `Inbound + Outbound All Remaining` in States 2/3/4. This is the mechanism behind **L-2**; sound-gating assertions are `[ADMIN]`.
- **L-12** `#m-restock`'s `Confirm Restock (2)` is a static label with no `disabled` attribute; the qty and location gates are not wired. All M3 gate assertions are `[ADMIN]`.
- **L-13** The floating-save button (`.flsave`) is attached only to `.shelf input` and `.locin`. It is **not** attached to `.qtyin`, `.bcin`, or any modal field. The spec applies the pattern to `.qtyin` as well `[L-S6-6]`, so that assertion is `[ADMIN]`.
- **L-14** State 6's first row (`.row-done`) renders its `input.qtyin` as `readonly` with a green border. That is demo styling for "this SKU is complete"; the spec keeps the field **editable at every stage** `[BR-56]`, so the editability assertion for a completed row is `[ADMIN]`.
- **L-15** The expanded Expected Inbound table's footer sentence `Full list: Inbound Request → Request List` is plain text, not an anchor. The spec requires it to be a real link `[G-12]`; the `[WF]` assertion covers the text only, and the anchor assertion is made against `#s6`'s banner, which **is** a real anchor.

### 2.4 Wireframe defects relevant to this page

| ID | Where | Stale text | Correct behavior specced here |
|---|---|---|---|
| **WF-1** ✅ **FIXED 2026-08-03** | `#s6b` completion banner | *(was)* `Received Date 07-26 14:02 · Carrier recorded automatically` | Received Date is auto-recorded; **Carrier is not recorded at all** — no field, no column, no capture `[BR-24]` `[PD-9 · OWNER-PENDING]`. The wireframe was edited on 2026-08-03 and the banner now reads `Received Date 07-26 14:02 · Carrier is not recorded` — the replacement clause this spec offered in §3.9 `[L-S6b-1]`. **QA-S6-07 passes**; it is no longer an expected failure. The row is kept for provenance, not as an open defect |
| **WF-3** | State 3 legend #4 | `— proposal` qualifier on the Cancel-Inbound lockout | The lockout is a rule `[BR-10]` `[PD-10 · OWNER-PENDING]`; the qualifier is removed once the owner confirms |
| **WF-13** | State 1 legend #16 | `shows at most 10–20 on screen` | The cap is **exactly 20 rows** `[BR-37]`; the panel footer already says `Max 20 on screen · full history in backend` |
| **WF-VO-1** ✅ **APPLIED 2026-08-03** | Comments hub `.paneheader` / search results / empty state / search placeholder, all nine states | *(was)* `Comments where I'm tagged · Click to open the order page` · `Comments I saved · Click to open the order page` · `Unstar to remove from list` · `Mark all as read` · `{n} results · newest first · click to open the order page` · `No matching Comments` · `🔍 Search all Comments — order no · author · text` | The hub is **one control on all eight screens** `[G-7]`, so its copy is a byte-exact cross-page contract. This page held the minority form on all seven strings. `[G-7]` v1.2 published the canonical set (HUB-1…HUB-7) on 2026-08-03 and all nine `.inboxdd` blocks on this page were moved to it in the same commit, together with QA-C-03 / QA-C-05 / QA-C-06 / QA-C-07 / QA-C-10 / QA-C-11. The two entity-scoped headers that read `· Click to open the item` (`#inbox6`, `#inbox6b`) were canonicalized too — `[G-7]` reading rule 2 fixes the word `order` for every entity type. §9.5 CP-4 is closed |

---

## 3. Functional Specification

Conventions used in every block: **Trigger** (what starts it) · **Behavior** (what happens, exactly) · **Validation** · **Server** (semantic action; literal endpoint naming is a developer decision) · **Persists** (the `[DC-n]` events from §5) · **Feedback** (what the operator sees/hears). Idempotency applies to every confirming action `[G-9]`; it is restated per block only where the key scope is non-obvious.

### 3.1 State 0 — Waiting (before scan)

#### `[L-S0-1]` Empty unified search box with auto-focus

- **Trigger:** page load, or return from any completed action in any state.
- **Behavior:** the page renders a single text input (`.search-input input`, placeholder `Tracking No / Inbound Order No / Product Order No / Last-mile barcode — scan any number`) with an empty value and **keyboard focus already in it**. No type selector, no segmented control, no "matched field" badge — all removed 2026-07-09 `[BR-46]`. The operator scans; the scanner types the digits and sends Enter; the page resolves the value and switches to the matching state. Page delta on `[G-1]`: the input is the page's default focus target in **every** state, not only State 0.
- **Inputs accepted (4 number classes + 1 wrapper):** customer-order **Tracking No**, **Inbound Order No** (the per-line purchase reference, e.g. `24101467541797`), **Product Order No**, **last-mile (return) barcode**, and a **product EAN barcode**. Coupang QR scans arrive wrapped as `[V1]{barcode}` and must match the same as the bare barcode `[BR-2]`.
- **Validation:** an empty submit is a no-op — no request, no state change, no toast, focus stays put `[E-10]`.
- **Server:** one resolution call returning `{resolution, entity_id, candidates[]}` where `resolution ∈ {customer_order, inbound_request, return, product_in_order, unrecognized, multi_match}`.
- **Persists:** `[DC-1]` on every submit including unresolved ones; `[DC-2]` when the value was typed rather than scanned.
- **Feedback:** the resolved state renders in place. A plain search is **not** a confirming action, so it raises no toast — a page delta on `[G-2]`, whose scope is confirming actions.

#### `[L-S0-2]` Expected Inbound summary badge

- **Trigger:** rendering State 0 (decision 2026-08-02, option C).
- **Behavior:** a single collapsed line-button (`#inexpToggle`) reads `▸ Expected Inbound {n} — {a} with tracking · {b} Partial Inbound` (wireframe: `▸ Expected Inbound 4 — 2 with tracking · 1 Partial Inbound`). Clicking expands `#inexpTable` inline and flips the caret to `▾`; clicking again collapses. **Collapsed is the default** so State 0 stays a scan hub, not a dashboard.
- **Table contents:** columns `Inbound No.` · `Sourcing Route` · `Supplier` · `Items` · `Tracking No` · `Status`. Rows are **sorted with tracking-bearing rows first**; rows without a tracking number show `—`. Status renders `REQUESTED` (amber) or `PARTIAL {received}/{expected}` (amber, `.row-part` tint). Route renders as black bold text `[G-5]`; an OTHER-route request renders `OTHER ({channel})` `[PD-80 · OWNER-PENDING]`. Supplier and product names keep their Korean forms verbatim (`(주)뷰티서플라이`, `비엠유통`) `[G-6]`.
- **Scope:** only unfinished requests appear — `REQUESTED` and `PARTIAL`. An `INBOUNDED` request is never listed `[E-84]`.
- **Row click:** opens **State 6** for that inbound request **without scanning**. This is the damaged-label path: bulk boxes whose tracking label is unreadable. The screen must function with no tracking context `[E-47]`.
- **Empty state:** with zero open inbound requests the badge renders `▸ Expected Inbound 0` and expands to `No open inbound requests`; it is never hidden, so its absence always means a render failure `[E-42]`.
- **Integrity:** the number in the badge and the number of rows in the expanded table are the **same query**; they may never disagree `[E-83]`.
- **Deep link:** the expanded table's footer carries `Rows with tracking sorted to top · Click a row = open its reconciliation screen (State 6) without scanning (for bulk boxes with damaged labels) · Full list: Inbound Request → Request List`; the final clause is a real link to `../inbound-request/index.html#reqlist` `[G-12]` (in the wireframe it is plain text — demo limitation **L-15**). **Path form:** this page writes the deep link in the `index.html#anchor` form everywhere — `[L-S6-2]`, §6.2 and QA-S6-02 — because that is the shipped `href` the `[WF]` assertion reads. `[G-12]`'s illustrative directory form (`../inbound-request/#reqlist`) is a cross-page inconsistency, not a second permitted form on this page (§9.5 CP-8).
- **Persists:** expanding/collapsing is a declared **NON-event** (§5.9). The row click persists `[DC-5]` with `entry_method=badge_row_click`.
- **Feedback:** none beyond the expansion; entering State 6 is its own render.

### 3.2 State 1 — Scan result, last item remaining

State 1 is the canonical customer-order screen. Everything in §3.2 except `[L-S1-8]` also applies to States 1b, 2, 3, 4 and 5 unless a later block says otherwise.

#### `[L-S1-1]` Unified search auto-detection

- **Trigger:** submit (scanner Enter, `🔍 Search` click, or manual Enter).
- **Behavior — resolution precedence (fixed order, first match wins):**
  1. **Inbound-request tracking number of a matching-active request** → **State 6**, always, never a customer-order state. Every tracking number registered on the request matches, including the 2nd and 3rd of a split shipment `[G-10]`. **A number registered on a `CANCELLED` request does not match here** — cancellation deactivates matching `[G-10]`, so the scan falls through to rule 5 (unrecognized) `[E-95]` (owner-decided 2026-08-03).
  2. **Last-mile / return barcode** → **State 4** (customer return mode).
  3. **Customer-order tracking no. / Inbound Order No. / Product Order No.** → States 1/1b/2/3/5 depending on the order's inbound completeness and status.
  4. **Product EAN barcode** resolved inside the currently open order → highlights and sorts that row `[L-S1-5]`.
  5. Otherwise → **unrecognized**, open M2 `[L-S1-Fb]`.
- **`[V1]` normalization:** before matching, strip a leading `[V1]` wrapper; match on the remainder. A bare barcode and its `[V1]`-prefixed form must resolve identically `[BR-2]`. The rule text is **behavior only and is never rendered on screen** (tidied off-screen 2026-07-23).
- **Multi-match:** when one number matches more than one entity (e.g. the same digits exist as a product order no. and as a tracking no.), the page shows a **selection list** of all candidates with enough context to choose (entity type, order/inbound no., status, product summary) and picks nothing automatically `[E-7]`. Layout of that list is a developer decision.
- **In-flight scans:** a submit that arrives while a previous resolution is still outstanding is **queued and processed in order** — never dropped, never interleaved `[BR-54]` `[E-66]`.
- **Validation:** whitespace trimmed; input is never silently truncated; case-insensitive.
- **Server:** resolve → fetch. Read-only.
- **Persists:** `[DC-1]` (raw value, normalized value, resolution, resolved entity); `[DC-3]` when a candidate was picked from a multi-match list.
- **Feedback:** the target state renders. Focus returns to the input with the value selected `[L-S1-14]`.

#### `[L-S1-2]` Shelf input with floating Save

- **Trigger:** typing into the order card's `Shelf` input (`.shelf input`).
- **Behavior:** while the value differs from the last saved value, a floating purple `Save` button (`.flsave`) appears beside the field. Clicking it, or pressing **Enter** in the field, saves instantly; the button turns green and reads `✓ Saved`, then disappears after ~0.9 s. Re-entering the identical value shows no button and produces no event `[E-45]`. The State 6 `Location` inputs (`.locin`) use exactly this pattern.
- **Confirmation delta on `[G-2]`:** the green `✓ Saved` chip **is** the confirmation for this micro-action, rendered in place beside the field the operator is already looking at rather than in the top-right slot `[BR-51]`. Failure still uses the standard red top-right toast. This is a rendering-position delta, never a removal of the confirmation.
- **Lifecycle:** a shelf value persists while the order is open and is **cleared automatically on Outbound** (old → new captured) `[PD-18 · OWNER-PENDING]`. Temporary shelves must be reusable, and a stale shelf on a shipped order misdirects the next picker.
- **Validation:** free text, trimmed; a whitespace-only entry is treated as empty and clears the shelf `[E-89]`; an empty value clears the shelf (also an event).
- **Server:** `set order shelf`.
- **Persists:** `[DC-14]` (order, shelf old→new, actor, ts); `[DC-15]` on auto-clear at outbound.

#### `[L-S1-3]` Comments hub (top-right)

- **Trigger:** clicking `💬 Comments` in the global nav (`button[data-open^="inbox"]`, badge = unread mention count).
- **Behavior:** opens a dropdown (`.inboxdd`) with a search box on top and two tabs: `@ Mentions` (comments where the current user is tagged, badge count) and `★ Saved` (comments the user starred). Each entry shows entity, author, text and time; clicking an entry **opens that entity's page**. The `★` button toggles save/unsave; unsaving removes the entry from Saved immediately. `Mark all read` clears the badge.
- **Full-text search (added 2026-07-29):** typing in the search box searches **every comment on every entity**, not just the two tabs — matching **entity no. · author · text** — results **newest first**, matched substrings highlighted in `<mark>`. The results header reads `{n} results · newest first · click to open the order` `[G-7]` HUB-5. Clearing the input restores the tabs and the previously active pane. An empty result renders `No matching comments` HUB-6.
- **Copy is a cross-page contract, not a page decision — now published.** The hub is one control replicated on all eight screens `[G-7]`, so its user-visible strings must be byte-identical everywhere. `[G-7]` v1.2 (2026-08-03) publishes them as **HUB-1…HUB-7**: `Comments mentioning me · Click to open the order` · `Saved comments · Click to open the order` · `Unstar to remove from the list` · `Mark all read` · `{n} results · newest first · click to open the order` · `No matching comments` · `🔍 Search all comments — order no. · author · text`. This page previously shipped the minority form on all seven (**WF-VO-1**); the wireframe and every `[WF]` assertion here were moved to the canonical set in the same commit, closing §9.5 CP-4. This page states no local variant — the strings above are quoted from `[G-7]`, not owned here.
- **Entity types:** orders **and inbound requests** (State 6/6b's hub shows `Inbound 202607120001`) **and unrecognized-pool items** `[G-7]`. Clicking a pool-item entry opens the tracking-missing page focused on that row, or the matched order if it was already resolved `[PD-67 · OWNER-PENDING]`.
- **Paging:** result sets larger than one page are paged or virtualized — the hub never truncates silently `[E-73]`; page size is a developer decision.
- **Persists:** `[DC-21]` star/unstar, `[DC-22]` read / mark-all-read, `[DC-24]` search executed (query, hit count, actor).
- **Feedback:** badge decrements on read; no toast (reading is not a confirming action).

#### `[L-S1-4]` Reduced side padding — one-screen fit

- **Behavior:** page padding is `18px 16px 0` (`.pagepad`). All 14 table columns plus the bulk bar and every action button must fit inside a 1280 px-wide viewport with **no horizontal scrolling of the page body**. The table may scroll inside its own container only if a future column addition is approved; the current column set must not require it `[BR-39]`.
- **Rationale:** an operator holding a scanner cannot scroll horizontally (2026-07-09).

#### `[L-S1-5]` Scanned product highlighted and sorted to top

- **Trigger:** a product barcode resolves inside the open order.
- **Behavior:** that row receives class `row-hit` (yellow `--hl` background, amber top and bottom borders) **and is moved to the top of the table**, so the operator's eye lands on it without searching. Only one row carries `row-hit` at a time; a new scan moves it. Rows sourced from existing warehouse stock keep their blue tint (`row-exist`) underneath.
- **Wireframe note:** the mock renders `.row-hit` in place as the second row — demo limitation **L-8**, not a rule change.
- **Persists:** covered by `[DC-1]`; no separate event. The sort/highlight itself is a declared NON-event (§5.9-7).
- **Pointer — this is where `[DC-6].method=scan` comes from.** `[DC-6]`'s `method` enum is `{row_button, combined_button, bulk, scan}`; the first three are the controls of `[L-S1-8]` and `[L-S1-9]`, and `scan` is **this** path — a line the operator reached by scanning its product barcode inside the open order records `method=scan` when it is inbounded. Noted here because §5 was otherwise the only place the value appeared, leaving a reader unable to tell which screen action produces it.

#### `[L-S1-6]` Sourcing Route column

- **Behavior:** renders the order line's sourcing route as **black bold text, never a coloured pill** `[G-5]`. Four order-facing values: `SMART BUY` · `JIT ({channel})` · `WHOLESALE` · `PARTNERSHIP`. Route labels render in their canonical casing — `JIT (Coupang)` is mixed case and is **not** upper-cased by CSS or by the renderer.
- **Page delta on `[G-5]` — a fifth label on order-facing rows:** an order line whose stock originated on an **OTHER**-route inbound request renders `OTHER ({channel})` in this column, and the same label appears in State 0's Expected Inbound table `[L-S0-2]`. `[G-5]` states the order-facing badge set as "exactly 4"; this page renders a fifth **display** value because the route is inherited from the Inbound Request by tracking number `[BR-5]` and OTHER is a legal origin route there — suppressing it would render a blank cell or a false route. It is a rendering pass-through, never a fifth *selectable* route: nothing on this page can assign OTHER. Declared as a delta rather than an exception because Order Detail reads `[G-5]` the opposite way (§9.5 CP-3). 2026-08-03 `[PD-80 · OWNER-PENDING]`.
- **JIT channel:** the parenthesis carries the purchase channel the order handler picked in the live admin dropdown — `JIT (Coupang)` / `JIT (Naver)` / `JIT (Other retail)` (2026-08-03).
- **Existing-inventory exception:** when the handler picked **Existing inventory**, warehouse stock is deducted and the line shows **that stock's own sourcing route**, not JIT. The row additionally carries the `row-exist` blue tint and shows a `Location` value.
- **Only JIT can be PENDING.** Smart Buy, Wholesale and Partnership lines arrive already inbounded `[BR-4]`.
- **Source of truth:** the route is assigned on the **Inbound Request** and matched to the order line **by tracking number** `[BR-5]`.
- **Persists:** display only; no event.

#### `[L-S1-7]` Quantity ≠ 1 amber highlight

- **Behavior:** a `Qty` cell whose value is not 1 renders with class `qty-warn` (amber fill, amber border). It is an attention cue for multi-unit picks, not a warning state; nothing is blocked `[BR-38]`.

#### `[L-S1-8]` Combined `Inbound + Outbound` button

- **Trigger:** the row is the **last uninbounded line** of the order (uninbounded count == 1) and the order is not on hold and not already outbounded.
- **Behavior:** the row's action button label changes from `Inbound` to `Inbound + Outbound` (green). Clicking it performs, as one server transaction: inbound of that line → completion check → outbound of the order (`processing` → `prepare shipment`).
- **Validation / disable matrix:** if the order is on hold the button stays `Inbound` and outbound is refused `[BR-7]`. If the order status forbids outbound `[BR-9]`, the button stays `Inbound`.
- **Server:** single call, single idempotency key covering both effects — a double click must produce exactly one inbound and one outbound `[G-9]` `[E-13]`.
- **Persists:** `[DC-6]` then `[DC-8]` with `trigger=combined_last_item`, plus `[DC-9]` status old→new.
- **Feedback:** send sound `[G-3a]` `[PD-2 · OWNER-PENDING]`; green confirmation toast; focus returns to the search input `[G-1]`.

#### `[L-S1-9]` Bulk bar above the table

- **Behavior:** a bar sits directly above the table and is **always visible in every state**, with buttons disabled (`.btn-gray`) rather than hidden when not applicable `[BR-47]` (2026-07-09). Two buttons plus a live counter:
  - `Bulk Inbound (Selected)` — inbounds every checked, still-PENDING line. Disabled with 0 selected `[E-19]`.
  - `Inbound + Outbound All Remaining` — inbounds **all** remaining lines and, because that completes the order, **auto-outbounds** it `[BR-6]`.
  - Counter text, byte-exact per state: State 1 `1 selected · Processing all triggers auto Outbound (Hold orders: Inbound only)` · State 1b `2 not yet inbounded — processing all triggers auto Outbound (Hold orders: Inbound only)` · States 2/3 `Nothing left to bulk-process — all items inbounded` · State 4 `Opens the restock confirmation modal — confirm qty · location · memo per item, then process in bulk` · State 5 `Hold order — Inbound allowed, Outbound blocked (ship after Hold release)`.
- **Hold exception:** on a held order `Bulk Inbound (Selected)` stays enabled (`.btn-green-line`) and `Inbound + Outbound All Remaining` is disabled `[L-S5-3]`.
- **Batch reporting:** one batched call with one idempotency key for the whole batch; **per-line results are returned and surfaced**. A batch in which some lines failed is reported as partial with the failing lines named — never as an unqualified success — and the successful lines are not rolled back `[BR-55]` `[E-72]`.
- **Persists:** `[DC-46]` (bulk invocation, selection scope, resulting line list), `[DC-7]` batch parent, one `[DC-6]` per line, and `[DC-8]` + `[DC-9]` when the batch completes the order.
- **Feedback:** send sound on `Inbound + Outbound All Remaining`; one toast summarising the batch.

#### `[L-S1-10]` Button label is `Outbound`

- **Behavior:** the order-card action is labelled exactly `Outbound`. The former label `Outbound to Deleo Baroship` was removed on 2026-07-09's carrier-agnostic pass — no carrier name appears in any button label on this page `[G-4]`. After outbound the same control becomes `✓ Outbounded` `[L-S3-1]`.

#### `[L-S1-11]` Order Comments button

- **Trigger:** clicking `💬 Comments` on the order card (badge = comment count on this order).
- **Behavior:** toggles the results-area comment panel `[L-S1-19]`. Writing a comment and clicking `Post` appends it; `@name` inside the text notifies that person through Slack `[G-7]`. Comments are **append-only — no edit, no delete** `[PD-3 · OWNER-PENDING]`.
- **Validation:** empty comment cannot be posted; unresolvable `@name` posts as plain text and raises no notification (the composer resolves mentions from the system user list).
- **Persists:** `[DC-19]`; `[DC-20]` per mentioned user; `[DC-43]` for the Slack dispatch result.
- **Feedback:** the comment appears at the bottom of the panel with author and timestamp; green confirmation toast `[G-2]`.

#### `[L-S1-12]` Search input value persists after inbound

- **Behavior:** after an inbound/outbound action the search input **keeps** the value that produced the current screen (State 1 shows `10323775316153`). The operator can visually verify what they last scanned. Combined with `[L-S1-14]`, the value is also **selected**, so the next scan overwrites it in one keystroke — persistence never costs a keystroke `[G-1]`.
- **Exception:** State 6b clears the input `[L-S6b-2]`, because the next scan there is a new tracking number, not a re-verification of the last one.

#### `[L-S1-13]` Actor Log (Inbound / Outbound Log)

- **Behavior:** a table at the bottom of States 1, 1b, 2, 3, 4, 5 headed `Inbound / Outbound Log` with columns `Time · Action · SKU · Qty · Worker · Memo`, newest first. Action values seen in the wireframe: `INBOUND` (green), `OUTBOUND` (blue), `INBOUND Cancelled (Restocked)` (red), `Return Restock (Stock added)` (green), `HOLD Applied` (red). The Memo column is populated from the modal that produced the row (M1's memo, M3's shared memo).
- **Doctrine:** this table is a **view over persisted events**, never the only copy `[G-8]`. Hiding, filtering, or paginating it must not affect the events. Events created elsewhere (Hold applied by CS in another screen) appear here read-only.
- **Ordering:** rows are ordered by the **server** timestamp, never by client clock, so a station with a skewed clock cannot reorder history `[E-90]`.
- **Persists:** nothing of its own.

#### `[L-S1-14]` Focus return with select-all

- **Trigger:** (a) any click anywhere on the page that is not inside another input, and (b) completion of any inbound/outbound/confirming action, and (c) closing any modal, and (d) completion of State 6b.
- **Behavior:** the unified search input regains focus **with its content selected**, so the next scan overwrites it `[G-1]`. There is **no on-screen text** for this rule.
- **Exclusion (critical):** auto-refocus must **not** fire while the operator is typing inside another field — comment composer, memo textarea, barcode cell input, shelf input, location input, or any modal field. Hijacking focus there causes scans to be typed into comments and quantities `[E-12]`. Implementation mechanism is a developer decision; the rule is normative.
- **Persists:** none (declared NON-event, §5.9-6).

#### `[L-S1-15]` No refresh + confirmation toast + send sound

- **Page delta on `[G-2]` — refresh:** View Orders has **zero** refresh exceptions. The product's single designed exception (RTO Bulk Outbound) does not exist on this page, so no action here, in any state, may reload `[BR-31]`.
- **Page delta on `[G-2]` — toast copy:** the byte-exact strings this page uses are `✓ Inbound complete — {SKU}` with sub-line `No refresh · ready for the next scan`; `✓ Outbound complete — Order {id}` with `Status: prepare shipment`; `✓ Inbound complete — Inbound No. {n}` with `Inventory updated · Request list INBOUNDED · ready for the next tracking scan`; `✓ Tracking No {n} matched and registered`; `✓ Sent to Missing Tracking List`. Failure toasts use the same slot with `.err` styling and must name the cause.
- **Page delta on `[G-3a]` — sound scope:** on this page the send sound fires on exactly three controls — the order-card `Outbound`, the row `Inbound + Outbound`, and the bulk `Inbound + Outbound All Remaining` `[PD-2 · OWNER-PENDING]`. It must **not** play on `Cancel Outbound`, on the disabled `✓ Outbounded`, on a disabled `Outbound`, on `Inbound`, on `Bulk Inbound (Selected)`, or on any modal confirm. The reference synthesis is in the wireframe (`sndOutbound()`, sine 340 → 940 Hz + triangle 1,250 Hz tail); exact parameters are a developer decision.
- **Toast burst policy** under rapid scanning (stacking vs single-slot replacement, duration) is a developer decision; the requirement is that a toast is never the only record of an outcome `[G-8]` and never blocks the next scan `[E-48]`.
- **Audio blocked:** if the browser's autoplay policy suppresses audio before the first gesture, the action still processes — sound is an enhancement, never a gate `[E-41]`.

#### `[L-S1-16]` Floating Live Barcode Feed

- **Behavior:** a floating panel pinned bottom-left (`#scanfloat`), **collapsed by default** into a pill reading `📡 Live Barcode Feed {n}`. Clicking the header expands it to a list of recent scans — `worker · barcode · time` — newest first; the collapse chevron flips `▾` → `–`. Footer reads `Max 20 on screen · full history in backend` with an `Export by date` button.
- **Cap:** exactly **20** rows on screen `[BR-37]`. (State 1 legend #16 still says "10–20" — defect **WF-13**; the panel footer is already correct.)
- **Backend:** the full scan history is retained server-side without truncation and is exportable by date range (§5.10). Export file format and the date-range picker are developer decisions.
- **Scope:** present on States 1–6b, including the internal-inbound states where it shows the product scans counted against the request. (The wireframe renders it only inside State 1 — demo limitation **L-3**.)
- **Persists:** the feed is a view over `[DC-1]`; the export action persists `[DC-47]` `scan_feed.exported` with actor, requested range, row count and format.

#### `[L-S1-17]` Location column

- **Behavior:** a `Location` column sits immediately right of `Sourcing Route` and shows the **current warehouse location** of products held as existing inventory (e.g. `A-03-2`). Lines sourced JIT or not yet in the warehouse render `–`. Present on States 1–5 with identical placement `[BR-39]`.

#### `[L-S1-18]` Brand-prefixed product names

- **Behavior:** the English `Product Name` always begins with the **brand in bold** (`**COSRX** Pomegranate & Collagen Volume Lifting Cream, 100ml`). `Product Name KR` also carries the EN brand in bold (`**Dr.Jart+** 포어레미디 리뉴잉 폼 클렌저`) `[G-6]`. Korean names are data and are never translated.
- **Upstream dependency:** products whose brand is missing require a product-name logic fix in the catalog, not a UI workaround `[E-59]` (§9.1).

#### `[L-S1-19]` Results-area Comments panel

- **Behavior:** the panel (`.cpanel`) under the order card is **expanded by default** and collapsible via `[L-S1-11]`. Each comment shows author, text with `@mentions` in blue (`.at`), timestamp, and a `★` toggle. Starring aggregates into the hub's `★ Saved` tab `[L-S1-3]`. The composer placeholder is `Write a comment — @name sends an automatic Slack alert (order no · text · time · author)`.
- **Persists:** `[DC-19]`, `[DC-21]`.

#### `[L-S1-20]` Barcode input for barcode-less products

- **Trigger:** a product line whose SKU has no barcode in the product master.
- **Behavior:** the `Barcode` cell renders an **always-visible dashed input** (`input.bcin`, placeholder `Enter barcode`) in **every state**, not only when scanning. Entering a value and confirming writes it to the **product master**, so the SKU is recognized from the next scan onward. Lines that already have a barcode render it prefixed with `✓` (e.g. `✓ 8801051283860`).
- **Validation:** the value must not already belong to a **different** SKU — that is blocked with an inline error naming the conflicting SKU `[E-44]`. Re-entering the same barcode for the same SKU is a no-op. Checksum validation (EAN-13) and lookup debounce are developer decisions.
- **Server:** `register product barcode` (product-master write, not an order-scoped write).
- **Persists:** `[DC-17]` `product.barcode_registered` — canonical cross-page name — with SKU, barcode `null → value`, actor, ts, source screen. Rejections persist `[DC-18]`.
- **Feedback:** green confirmation toast `[G-2]`; the cell switches to `✓ {barcode}`.

#### `[L-S1-22]` `🖨 Print Return Labels (n)` — supplier return

- **Trigger:** bottom-right button in **work states 1, 1b, 2, 3** (not 4, not 5, not 6/6b). Label shows the count of selected products.
- **Behavior:** opens **M4**. This is the **supplier-return** concept — sending wrong or damaged goods *back to the supplier* (e.g. a Coupang seller) after they were found during inbound scanning. It is a **different concept** from Customer Return mode (State 4, customer → us) and the two must never share a flow or a label template.
- **Validation:** with zero rows selected the button is disabled `[E-76]`.
- **Persists:** opening is a NON-event; printing persists `[DC-28]` / `[DC-29]`.

#### `[L-S1-F]` State-1 off-screen behavior rules (no dot — normative)

This one footer carries three rules; they are sub-keyed `[L-S1-Fa]`, `[L-S1-Fb]` and `[L-S1-Fc]` per `_review.md` §2c-4 and are **not** counted as extra units (§2.1).

**`[L-S1-Fa]` Single-item auto-print.** When a scan resolves to an order containing **exactly one line item**, the shipping label prints **the instant the barcode is scanned**, with no click — but **only** if the order has **no inbound history**. Stock taken from **Existing Inventory does not count as inbound history**, so a single-item order fulfilled from warehouse stock still auto-prints on its first scan. The print itself follows `[G-4]`; a print failure never blocks or rolls back the inbound `[PD-19 · OWNER-PENDING]` `[E-39]`. Persists `[DC-30]` (precondition evaluation + trigger scan id), `[DC-28]`, `[DC-29]`.

**`[L-S1-Fb]` Unrecognized barcode → M2 → M2b.** A barcode that resolves to nothing opens **M2** (order-number lookup). A successful lookup lets the operator **register the tracking number on the spot**; confirming a match writes the tracking number **directly onto that order's product line**, so **rescanning the same barcode then resolves normally**. With no order number, or a failed lookup, the item is sent to the **Missing Tracking List** through **M2b**. Persists `[DC-4]`, `[DC-40]`, `[DC-41]`, `[DC-42]`.

**`[L-S1-Fc]` Inbound-request tracking → State 6.** Scanning the tracking number of an **Inbound Request** switches to the dedicated **Internal Inbound** screen and never to a customer-order state. That screen has **no Outbound step** `[L-S6-1]`.

### 3.3 State 1b — Scan result, normal

#### `[L-S1b-21]` Plain `Inbound` button when the last-item condition is not met

- **Behavior:** while **two or more** lines are uninbounded, every PENDING row's action button reads exactly `Inbound` (green) and performs an inbound only. The moment the uninbounded count reaches **exactly 1**, that row's button becomes `Inbound + Outbound` `[L-S1-8]`. The order-card `Outbound` stays disabled (`.btn-gray`) until **every** line is INBOUNDED `[BR-9]`.
- **State machine (line) — exhaustive:** a line has exactly **two** inbound states, `PENDING` and `INBOUNDED`. `PENDING → INBOUNDED` on inbound; `INBOUNDED → PENDING` on Cancel Inbound (M1). There is **no `OUTBOUNDED` line state**: outbound is an order-level fact, which is why `Cancel Outbound` touches no line state at all `[L-S3-2]` `[BR-11]`. A third line value would make every `Inbound Status` cell on this page and on Order Detail render an unmapped badge (§9.5 CP-2).
- **Persists:** `[DC-6]`.
- **Feedback:** green toast; **no send sound** — `Inbound` is not an outbound-class button `[G-3a]`.
- **Wireframe note:** the Actor Log is missing from `#s1b` in the mock — demo limitation **L-4**; the spec requires it here as in every customer-order state `[L-S1-13]`.

### 3.4 State 2 — All inbounded

#### `[L-S2-1]` `Outbound` activates

- **Trigger:** the last line reaches INBOUNDED (by row button, bulk, or a Cancel-Inbound reversal that leaves everything inbounded).
- **Behavior:** the order-card button switches from `.btn-gray` to `.btn-green` and becomes clickable. Enable predicate `[BR-9]`: *all lines INBOUNDED* **and** *at least one line exists* **and** *status ∈ {processing, pending}* **and** *not on hold* **and** *not already outbounded*.
- **Effect on click:** order status `processing → prepare shipment`; the outbound is recorded for the whole order (all SKUs, total qty).
- **Server:** `outbound order`, idempotent per order + version.
- **Persists:** `[DC-8]` `order.outbounded` (canonical) with `trigger=manual`, `[DC-9]` `order.status_changed` (canonical) old→new.
- **Feedback:** send sound; green toast `✓ Outbound complete — Order {id}` / `Status: prepare shipment`; State 3 renders in place.

#### `[L-S2-2]` `Cancel Inbound` → restock popup

- **Trigger:** clicking a row's `Cancel Inbound` (`.btn-red-line`) while the order is **not** outbounded.
- **Behavior:** opens **M1**. Nothing is cancelled until M1's `Confirm` — the button alone never mutates. Destructive actions on this page always carry a confirm step and a stated confirmation `[PD-5 · OWNER-PENDING]` `[G-2]`.

### 3.5 State 3 — Outbound complete

#### `[L-S3-1]` `✓ Outbounded` (disabled)

- **Behavior:** after outbound the order-card button reads exactly `✓ Outbounded`, is grey and non-interactive, plays no sound, and issues no request. The order status pill reads `Prepare Shipment` (`.st-prepare`).

#### `[L-S3-2]` `Cancel Outbound`

- **Trigger:** clicking `Cancel Outbound` (`.btn-red-line`) on an outbounded order.
- **Behavior:** rolls the order status back **`prepare shipment` → `processing`**. Line-level inbound state is untouched — every line stays INBOUNDED. The card returns to State 2 shape (`Outbound` re-enabled). The wireframe demonstrates the transition with `alert('Status rollback: prepare shipment → processing')`.
- **Validation:** rejected if the order has already left prepare-shipment (shipped/completed) — red toast naming the current status `[PD-6 · OWNER-PENDING]` `[E-56]`.
- **Cross-page parity:** Order Detail carries the same `Cancel Outbound` with the same rollback semantics `[PD-26 · OWNER-PENDING]`; that control is specced on Order Detail, not here, but the two must never diverge.
- **Server:** `cancel order outbound`, idempotent.
- **Persists:** `[DC-12]`, `[DC-9]` status old→new.
- **Feedback:** green toast; **no send sound** (`Cancel` is excluded from the outbound class).

#### `[L-S3-3]` Completion toast, no refresh

- **Behavior:** the completion toast is the only visible change; the operator can scan the next barcode immediately. Focus is already back in the search input `[L-S1-14]`.

#### `[L-S3-4]` Individual `Cancel Inbound` disabled after outbound

- **Behavior:** once an order is outbounded, **every** row's `Cancel Inbound` renders `.btn-gray` and is inert. To reverse a line, the operator must run `Cancel Outbound` first, which returns the order to State 2 where Cancel Inbound is live again. This ordering guard keeps inventory arithmetic reversible and prevents an order in `prepare shipment` from containing a PENDING line `[BR-10]` `[PD-10 · OWNER-PENDING]`.
- **Wireframe defect WF-3:** legend #4 still carries the `— proposal` qualifier; it is a rule here.
- **Server:** even with a forged request, the server rejects a line-level cancel on an outbounded order and persists the rejection `[DC-44]` `[E-55]`.

### 3.6 State 4 — Customer return mode

#### `[L-S4-1]` Customer Return banner

- **Trigger:** the scanned value resolves as a **last-mile / return barcode**.
- **Behavior:** a red banner (`.retbanner`) renders above the order card: `⟲ Customer Return Order` followed by `A returned tracking barcode was scanned — Order {id} · Tracking {no}`. The order card in this state shows Order ID, status, Total Quantity, Shelf and Comments — and **no `Outbound` button and no `🖨 Print` button**: a returned order is never shipped or re-labelled from this screen.
- **Row actions:** every line's action button reads `Cancel Inbound → Add Stock` (`.btn-red-line`) and opens M1 — the same cancel/restock path, labelled for the return context.
- **Persists:** `[DC-25]` (return barcode, order, **order status at scan time**, actor, ts).

#### `[L-S4-2]` `Restock Selected to Warehouse (n)`

- **Trigger:** clicking the green bulk-bar button; `n` = checked rows.
- **Behavior:** opens **M3**. Quantity and location columns were deliberately removed from the table and moved **into the modal** (2026-07-09) so the decision is made once, in one place, with a confirm step.

#### `[L-S4-3]` M3 defaults (rule lives in M3; no dot in State 4)

- **Behavior:** in M3 each line's **Restock Qty defaults to 0**. The operator enters only the quantity that physically came back; **0 means excluded**. There are no checkboxes — the quantity *is* the selection. `Location` is auto-filled for SKUs that already have warehouse stock (one location per SKU `[G-14]`); JIT-only SKUs have an empty, amber-outlined `required` field. The confirm button's count equals the number of lines with qty > 0 (`Confirm Restock (2)`).

#### `[L-S4-4]` Location gate (rule lives in M3; no dot in State 4)

- **Behavior:** if any line has restock qty > 0 **and** no location, `Confirm Restock` is disabled. Assigning the location enables it. Lines with qty 0 need no location `[E-29]`.

#### `[L-S4-5]` Last-mile barcode is searchable

- **Behavior:** the unified search auto-detects return barcodes; no separate return-lookup screen exists `[L-S1-1]` precedence rule 2.

#### `[L-S4-6]` There is no "returned" status — detection is by scan

- **Rule (critical):** the system has exactly **8 order statuses**: `pending`, `processing`, `on-hold`, `completed`, `refunded`, `failed`, `shipped`, `prepare-shipment`. **There is no `returned` status and none may be invented.** A returned parcel is usually `refunded` (collected after refund), sometimes `failed` (delivery failure), and — for refused deliveries and customs returns that come back before any refund — can still be `completed`. **All three must route to State 4.** Return mode is entered by **scanning the last-mile return barcode**, never by reading a status `[BR-12]`.
- **Consequence for QA:** a test that asserts "State 4 only for refunded orders" is wrong by construction.

### 3.7 State 5 — Hold order

#### `[L-S5-1]` Hold banner

- **Behavior:** an amber banner (`.holdbanner`) renders instantly on scan: `⏸ Hold Shipment` + the reason sentence + `Order {id} · Requested by {name}({team}) {date} {time}` (wireframe: `CS team put this order on Hold per customer request (address change) — Order 414102 · Requested by Sara(CS) 07-13 09:20`). The hold reason is optional free text captured where the hold was applied and is rendered here verbatim `[PD-20 · OWNER-PENDING]`.
- **Also visible:** the Actor Log shows a `HOLD Applied` row with the requester and memo, because the hold event is persisted wherever it was raised and this page is a view over it `[G-8]`.

#### `[L-S5-2]` `Outbound` disabled while on hold

- **Behavior:** the order-card `Outbound` renders `.btn-gray`, is inert, plays **no** sound, and issues no request. Status pill reads `On Hold` (`.st-hold`).
- **Server guard:** a stale client that posts an outbound on a now-held order is rejected with an explicit hold error; the rejection persists `[DC-44]` and surfaces as a red toast `[E-34]`.

#### `[L-S5-3]` Bulk behavior on hold

- **Behavior:** `Bulk Inbound (Selected)` stays **enabled** — intake is never blocked, because the goods are physically here and must be recorded. `Inbound + Outbound All Remaining` is **disabled**. Completing the inbound of a held order therefore stops at INBOUNDED and does **not** auto-outbound — the single exception to `[BR-6]`.
- **Persists:** when a full inbound completes on a held order, `[DC-10]` `order.outbound_suppressed_hold` records that the auto-outbound was deliberately suppressed — the absence of an outbound must be explainable later `[E-57]`.

#### `[L-S5-F]` Hold origin (no dot — normative)

- **Rule:** the hold itself is applied and released **elsewhere** — the `Hold Shipment` action in **OMS / Order Detail** (`Change Status → on-hold`), by CS. **View Orders only displays the resulting status and blocks outbound.** This page must offer no apply-hold and no release-hold affordance (§9.1).
- **Correction (2026-08-03):** the shipped legend paragraph reads `… in OMS/Order detail or Order Management (CS team)`. **Order Management is no longer a hold origin** — that screen removed every hold control on 2026-08-03 and its spec forbids one existing (`order-management` `BR-10`, §3.8). The legend clause is stale wireframe copy: `[WF]` QA (QA-CV-08) asserts the shipped sentence because that is what the page renders today; the corrected sentence is asserted `[ADMIN]` (QA-CV-23). Recorded in §9.5 CP-6 rather than in §2.4 because the fix is a wireframe edit owned by the cross-page pass, not a behavior of this page.

### 3.8 State 6 — Internal Inbound (inbound-request scan)

#### `[L-S6-1]` Automatic branch on tracking scan

- **Trigger:** the scanned number is a tracking number **registered on an Inbound Request**.
- **Behavior:** this screen opens instead of States 1–5, unconditionally. The branch separates two different physical processes: customer orders (receive → ship immediately) and internal inbound (stock intake into the warehouse).
- **Multi-tracking:** one inbound request may carry several tracking numbers (split shipments). **Every** registered number matches and enters this screen; partial arrivals accumulate against the same request until fully received `[G-10]` (2026-08-03).
- **Namespace note:** inbound (supplier → warehouse) and outbound (warehouse → customer) tracking numbers are **separate namespaces and may coincide**; when a scanned number exists in both, inbound-request tracking wins `[PD-8 · OWNER-PENDING]` `[PD-86 · OWNER-PENDING]` `[E-8]`.
- **Context switching:** scanning a *different* request's tracking while a count is in progress **saves nothing implicitly**. The page warns that the open request has uncommitted receipts and requires an explicit choice — continue here, or save partial (M5) and switch `[E-68]`. A customer-order number scanned in State 6 behaves the same way `[E-69]`.
- **Persists:** `[DC-5]` with `entry_method=tracking_scan`.

#### `[L-S6-2]` Internal Inbound banner

- **Behavior:** a large purple-bordered banner (`.intbanner`) with:
  - Title `📦 Internal Inbound — Inbound Request`
  - Warning line `Not a customer order · Goes into Inventory · No Outbound step`
  - Key/value row: `Inbound No. {n}` · `Channel {route badge}` · `Supplier {name, Korean verbatim}` · `Requested by {name} · {date}` · `Expected arrival {date}` · link `View in Inbound Request List →` pointing at `../inbound-request/index.html#reqlist` `[G-12]`. In the production admin this deep-links to the **specific Inbound No.**, filtered.
- **Route rendering:** black bold text `[G-5]`; OTHER renders `OTHER ({channel})` `[PD-80 · OWNER-PENDING]`.

#### `[L-S6-3]` Progress tiles

- **Behavior:** four computed tiles: `Expected Qty (Total)` = Σ expected across SKUs · `Received (scanned)` = Σ received (green, `.tile.ok`) · `Remaining` = expected − received, floored at 0 for display but the true signed value drives gating (amber, `.tile.warn`) · `SKU` = `{n} SKUs ({m} done)` where done = received == expected. Tiles recompute live on every scan and every manual edit, with **no page refresh**.
- **Zero-line request:** a request with no SKU lines renders all tiles at 0 and keeps `Confirm Full Inbound` disabled — an empty request can never be confirmed `[E-79]`.

#### `[L-S6-4]` Continuous product-barcode scanning

- **Trigger:** scanning a product barcode while State 6 is open.
- **Behavior:** each scan adds **+1** to that SKU's `Received Qty`; the cursor auto-returns to the search input with the value selected `[G-1]`. On-screen note: `Now scan product barcodes — each scan adds +1 to that product's received qty (continuous scanning · cursor auto-return · warning sound for products not in the request)`.
- **Wrong product:** scanning a barcode that is **not in this request** plays a **distinct warning tone** — not the send sound, not TTS `[G-3c]` — increments nothing anywhere, and shows an amber toast naming the scanned product. This is the wrong-delivery detector: the operator hears it while looking into the box `[E-16]`.
- **Over-scan:** scanning past `Expected Qty` **warns and still counts** — received may exceed expected; the excess blocks `Confirm Full Inbound` until it is resolved through M6 (edit expected) or M5 (save partial) `[PD-12 · OWNER-PENDING]` `[E-15]`.
- **Already-complete SKU:** scanning a SKU that already reached its expected quantity is an over-scan and follows the same rule.
- **Duplicate emission:** a scanner that emits the same barcode twice inside the device debounce window still produces **two** counted units — the counter is a physical tally, and a silent de-duplication would under-count genuine identical units. Correction is by editing `Received Qty` `[E-67]`.
- **Persists:** `[DC-31]` per scan (`received old → new`, `method=scan`), `[DC-33]` on wrong product, `[DC-34]` on over-scan.

#### `[L-S6-5]` Reconciliation table

- **Behavior:** the table is **request-scoped, never parcel-scoped**: it always lists **every SKU line of the inbound request**, regardless of which of the request's (possibly several `[G-10]`) tracking numbers was scanned to enter this screen — the operator sees the whole request's progress, and a parcel that contains only one of the SKUs still shows all lines. Columns `SKU No. · Brand · Product Name · Expected Qty · Received Qty · Location · Status`. SKU, Brand and Product Name come **straight from the Inbound Request** (they mirror the Procurement Hub sheet's columns) and are not re-derived from the catalog, so the operator compares like with like. Row tints: `.row-done` (green) when received == expected, `.row-part` (amber) while in progress. Status pill: `✓ INBOUNDED` (`.tag-done`) or `In progress · {n} remaining` (`.tag-part`).
- **There is no Carrier column and no Carrier field anywhere on this screen** `[BR-24]`.

#### `[L-S6-6]` `Received Qty` is directly editable

- **Trigger:** typing into a row's `Received Qty` input (`.qtyin`).
- **Behavior:** the operator may type the count instead of scanning it — this is how full boxes are received (`120` typed once beats 120 scans). The typed value **replaces** the running total; tiles and gating recompute immediately. The field stays editable at **every** stage, including after the SKU reaches its expected quantity, so a mis-count can always be corrected `[BR-56]` `[E-92]`.
- **Validation:** integer ≥ 0; non-numeric, negative and fractional values are rejected inline with the previous value restored `[E-53]`.
- **Persists:** `[DC-32]` with `method=manual` and `old → new` — deliberately a **different event** from `[DC-31]`, so "counted by hand" and "counted by scanner" stay distinguishable forever.
- **Feedback:** same floating-save pattern as `[L-S1-2]`; `✓ Saved` chip `[BR-51]`. (The wireframe attaches `.flsave` only to `.shelf input` and `.locin` — demo limitation **L-13**.)

#### `[L-S6-7]` `Location` = inventory intake position

- **Behavior:** each received SKU must be given the warehouse location it is being put into. A SKU that already exists in inventory **auto-suggests its current location** (one location per SKU `[G-14]`); a new SKU requires manual entry. Input is `.locin` with the floating-save pattern.
- **Validation:** a location already occupied by a **different** SKU is rejected with an error naming the occupying SKU — one location holds one SKU `[PD-46 · OWNER-PENDING]` `[E-6]`. A value that does not parse as a location code is rejected inline `[E-78]`. Location-code format and the line-derivation parsing are developer decisions.
- **Gate:** `Confirm Full Inbound` is disabled while any received SKU lacks a location `[PD-13 · OWNER-PENDING]` `[E-46]`. Stock may not enter Inventory location-less.
- **Persists:** `[DC-16]` (request, SKU, location old→new, `suggested` flag, actor, ts).

#### `[L-S6-8]` `Confirm Full Inbound` — exact-match gate

- **Enable predicate:** for **every** SKU in the request, `received == expected` (not ≥, not ≤), **and** the request has at least one SKU line, **and** every received SKU has a location `[PD-13 · OWNER-PENDING]`. While the predicate is false the button renders `.btn-gray` with the remaining count in its label, byte-exact in the wireframe: `Confirm Full Inbound (180 remaining)`.
- **Rationale:** this is the same gating class as the Closing page — an exact match is the only state that proves the physical count equals the record. Over-scan does **not** satisfy it `[PD-12 · OWNER-PENDING]`.
- **Alternative path:** while mismatched, the operator uses `Save Partial Inbound` (M5).
- **Sole confirm path:** State 6 (with the Inbound Request lifecycle) is the **only** place a PENDING inbound event is confirmed. Inventory displays PENDING inbound rows read-only and offers no confirm affordance — two confirm paths for one fact is the double-entry failure the design exists to avoid `[PD-41 · OWNER-PENDING]` `[BR-52]`.
- **On confirm:** see `[L-S6-F]`.
- **Server:** `confirm full inbound`, idempotent per request + version; the server revalidates the whole predicate at confirm time and rejects a stale confirm with a red toast + view refresh `[PD-6 · OWNER-PENDING]`.
- **Persists:** `[DC-37]`, `[DC-38]`, `[DC-39]`; blocked attempts persist `[DC-45]` with the blocking reason.

#### `[L-S6-9]` `✎ Edit Expected Qty`

- **Trigger:** clicking `✎` (`button.qedit`) in a row's `Expected Qty` cell (decided 2026-08-02).
- **Behavior:** opens **M6** bound to the clicked row. Saving recalculates remaining and the full-confirm gate, auto-posts a comment on the Inbound Request, and raises a Slack alert to the **requester** `[G-11]` `[G-7]`.
- **Wireframe note:** both rows open the same hardcoded modal in the mock — demo limitation **L-10**.
- **Detail:** §3.16.

#### `[L-S6-F]` State-6 off-screen behavior rules (no dot — normative)

On `Confirm Full Inbound`:
1. The received units are reflected in **Inventory (Current Stocks)** with their locations.
2. The Inbound Request's status auto-switches **`REQUESTED` / `PARTIAL` → `INBOUNDED`** `[G-11]`.
3. **Received Date is recorded automatically** (this exists for the sheet sync). **Automatic Carrier recording is NOT supported** — confirmed 2026-08-03. There is no Carrier field, no Carrier column, and no carrier capture on this page or on the Inbound Request `[PD-9 · OWNER-PENDING]`. *(State 6b's banner used to claim otherwise — defect **WF-1**, fixed in the wireframe on 2026-08-03; it now reads `· Carrier is not recorded`. §2.4.)*
4. Focus returns to the search box for the next tracking scan `[G-1]`.

The on-screen helper beside the buttons states the same contract byte-exactly: `On confirm: reflected in Inventory (Current Stocks) · Inbound Request List switches to INBOUNDED · Received Date recorded automatically`.

Unlike States 1–5, **this screen has no Outbound of any kind**. There is no bulk bar, no order card, and no `🖨 Print Return Labels` button.

### 3.9 State 6b — Internal inbound complete

#### `[L-S6b-1]` Completion banner

- **Behavior:** a green banner (`.donebanner`) reading `✓ Full Inbound Complete — Inbound No. {n}` with a key/value row: `Received {received} / {expected} ({n} SKUs)` · `Inventory updated ({loc} · {loc})` · `Inbound Request List switched to INBOUNDED` · `Received Date {date} {time} · Carrier is not recorded`.
- **Correction — applied 2026-08-03 (defect WF-1, closed).** The shipped wireframe used to append `· Carrier recorded automatically`. That clause was **wrong** and must not be implemented. Two endings were offered: stop at the Received Date, or state `Carrier is not recorded`. The wireframe took the second, so the banner now ends `Received Date 07-26 14:02 · Carrier is not recorded` and either ending remains conformant — what must never return is any wording that claims the carrier **is** recorded `[BR-24]`.
- The reconciliation table re-renders read-only with every row `.row-done` and `✓ INBOUNDED`.

#### `[L-S6b-2]` Focus returns immediately

- **Behavior:** on completion the search input is re-focused and **emptied** (its placeholder becomes `Scan a tracking barcode — continue with the next one`), ready for the next tracking scan `[G-1]`. The note under the table states: `Cursor returns to the search box immediately on completion — scan the next tracking number with no refresh. This stock is visible in Inventory (Current Stocks) with its locations.`
- **Re-entry:** scanning the tracking number of an already fully-INBOUNDED request re-opens this **read-only** completion view plus an info toast `Already inbounded — Inbound No. {n}` — because the operator's real question is "did this arrive?", which a read-only view answers `[PD-15 · OWNER-PENDING]` `[E-17]`.

### 3.10 `[L-M1]` Modal — Cancel Inbound (restock confirm)

- **Trigger:** a row's `Cancel Inbound` (`.btn-red-line`) in States 1, 1b, 2, or 4 (labelled `Cancel Inbound → Add Stock` in State 4). Disabled in State 3 `[L-S3-4]`.
- **Header:** `Cancel Inbound — {SKU}`.
- **Fields:**
  1. `1. Restock this inventory?` — radio `Yes — restock` (default) / `No`.
  2. `2. Restock Qty` — number, **default = the quantity that was inbounded**, editable, with the helper `Default = qty that was inbounded (editable) · disabled when "No" is selected`. Selecting `No` **disables and clears** the field; selecting `Yes` restores the previous value.
  3. `3. Location (Optional)` — text input `#restockLoc`, helper `Default = the SKU's registered location (editable · updates the SKU's location) · required if the SKU has none · disabled when "No" is selected`. **Default = the SKU's registered location**, auto-filled and editable; an edit relocates the SKU — one location per SKU `[G-14]` — and persists `old → new`. Selecting `No` **disables and clears** the field (same toggle as Restock Qty); `Yes` restores the previous value. The field is optional **only while the SKU already has a location**: for a SKU with no registered location (typically JIT residual stock entering the warehouse for the first time — the modal's own use case) the field is **required** and `Confirm` stays disabled until one is entered, because stock may not enter Inventory location-less `[BR-58]` `[E-94]` (added 2026-08-03, owner).
  4. `4. Memo (Optional)` — textarea, placeholder `Cancellation reason or notes — also recorded in the order's Comments history`.
- **Note block (normative):** `The SKU's Reserved Quantity → Available updates automatically.` Use cases named on screen: `mid-order cancellation, or a JIT order placed by mistake when warehouse stock exists` — the latter is the origin of the **JIT residual stock** that Inventory must display (cross-page).
- **Footer:** `Close` (`.btn-line`) and `Confirm` (`.btn-blue`).
- **Validation:** restock qty may be **lower** than the inbounded qty (partial damage) and is accepted `[E-27]`. Restock qty **above** the inbounded qty is rejected `[E-52]`. A location already occupied by a **different** SKU is rejected with an error naming the occupying SKU — one location holds one SKU, same rule as `[L-S6-7]` `[PD-46 · OWNER-PENDING]`; a value that does not parse as a location code is rejected inline. Restock qty **`0` while `Yes — restock` is selected** is blocked — zero restock is expressed by selecting `No`, so that the two paths never produce two different records of the same decision `[E-93]`. With `No` selected, no stock is added and the reservation is released.
- **The under-restock remainder is an inventory event, never a memo `[BR-57]`:** when restock qty < inbounded qty, the difference is **auto-recorded as an inventory adjustment** `ADJUST(−remainder)` carrying the same memo, in the same transaction as the cancel `[PD-49 · OWNER-PENDING]`. The memo explains the adjustment; it is not the accounting record for it. A memo string is not a stock event and cannot satisfy `[G-8]`, so leaving the difference memo-only would silently drop units from the ledger. This matches Inventory's M4 release path, which books the identical adjustment for the identical physical fact — the server must produce **one** reversal and **one** remainder adjustment per line no matter which screen raised it (§9.5 CP-1).
- **Server:** `cancel item inbound` with `{restock: bool, qty, location, memo}`; idempotent per line + version. The remainder adjustment shares the cancel's idempotency key — a retry never books it twice.
- **Persists:** `[DC-11]` — order, SKU, cancelled qty, restock yes/no, restock qty, restock location `old → new` (null old = first assignment), memo, actor, ts, and the stock delta `Reserved → Available` old→new. An under-restock additionally persists `[DC-39]` with `origin=cancel_inbound_remainder` and `qty_delta = −(inbounded − restocked)`. The memo is **dual-persisted**: into the Actor Log row's Memo cell and into the order's comment history `[G-7]`.
- **Feedback:** green toast; line returns to `PENDING`; Actor Log gains `INBOUND Cancelled (Restocked)`.

### 3.11 `[L-M2]` Modal — Unrecognized barcode (order-number lookup)

- **Trigger:** a scan resolves to nothing `[L-S1-Fb]`.
- **Header:** `Barcode Not Recognized`; body opens with `No order matches the scanned barcode {barcode}.` and the instruction `Enter the Coupang purchase order number to find matching products and register the tracking number on the spot.`
- **Fields / controls:** `Order No` text input (`#unrecNo`) + `🔍 Look up` (`#unrecSearch`); footer buttons `No order number` (`#unrecNoNum`) and `Cancel`. Focus lands in the order-number field on open `[E-1]`.
- **Match found:** `#unrecFound` renders `Order number {no} matched {n} products — click the match button on the scanned product's row` and a table with columns `Image · Product Name · Order · Qty · Tracking No` and a green `Match Tracking No` button (`.trkmatch`) per row. Product names carry the brand in bold with the Korean name underneath `[G-6]`. The block closes with the note `Clicking match registers the tracking number on that line and closes this window — rescanning the same barcode is then recognized normally.`
- **On `Match Tracking No`:** the tracking number is written **directly onto that order's product line**; the modal closes; a toast appears (`#unrecToast`): `✓ Tracking No {no} matched and registered` with sub-line `Order {id} · {product} — rescanning the same barcode is now recognized`. Rescanning the original barcode then resolves normally `[BR-27]`.
- **Auto-comment + Slack:** an on-the-spot match here fires the **same** match-confirmed auto-comment and Slack route as a resolution made on the tracking-missing page — one match pipeline, one audit trail. The `@mention` is **suppressed when resolver == registrant** (no self-notification) `[PD-16 · OWNER-PENDING]`.
- **No match:** `#unrecNone` renders `No products match the entered order number (possible typo or a number from another channel). Send it to the Missing Tracking List.` with a `Send to Missing Tracking List` button (`#unrecToSend`) that opens **M2b carrying the failed order number**.
- **`No order number`:** opens M2b **without** a carried number.
- **Must NOT exist:** any photo-capture control. Photo upload on this modal was removed 2026-07-21 and **permanently deleted** in the 2026-08-03 review — not deferred `[PD-63 · OWNER-PENDING]` `[BR-41]`.
- **Persists:** `[DC-4]` on open, `[DC-40]` per lookup (entered number, result, candidate count), `[DC-41]` on match (order, product line, tracking `null → value`, actor, ts) plus `[DC-23]` auto-comment and `[DC-20]`/`[DC-43]` for the notification.

### 3.12 `[L-M2b]` Modal — Send to Missing Tracking List

- **Trigger:** M2 → `No order number`, or M2 → `Send to Missing Tracking List` after a failed lookup, or directly from the chrome tab.
- **Header:** `Send to Missing Tracking List`; body opens `Barcode {barcode} — send it to the Missing Tracking List?`
- **Carried number:** when a failed lookup preceded it, the line `The looked-up order number {no} (match failed) is recorded together.` is shown (`#unrecCarried`, number in `#unrecCarriedNo`).
- **Fields:**
  - Product autocomplete — prompt `Enter the product name (English — autocomplete · Korean name shown alongside)`. Each option shows `Brand — English name` with the Korean name in the sub-line `[G-6]`. A product **must** be chosen from the list; free text alone cannot be sent `[E-74]`.
  - `Qty` — positive integer, default `1`; 0, negative and non-integer values are rejected `[E-75]`.
  - `Memo (Optional)` — textarea, placeholder `e.g. Box label damaged, looks like a 1+1 set — shown in the Missing Tracking List and the Slack alert`.
- **On-screen contract:** `On send, the #unrecognized-tracking channel gets an "Unrecognized product added" alert (product name · barcode · qty · memo · order number if lookup failed) and @mentions every suspected PIC (once per person) so handlers are pushed, not polled → shown in the unrecognized pool on the Missing Tracking List page.`
- **On `Send to Missing Tracking List`:** the item enters the shared unrecognized pool, the modal closes, and a green fixed toast (`#gtoast`) shows `✓ Sent to Missing Tracking List` with sub-line `PIC notified via #unrecognized-tracking · No refresh`.
- **Decided (`[PD-66]`, owner 2026-08-03):** the no-identifier case does not exist — either a tracking number or an order number is always present. The registration contract stands: an identifier is required, and M2b never accepts a pool entry without one (see §9.2 OQ-1, resolved).
- **Persists:** `[DC-42]` (barcode, chosen product, qty, memo, carried failed order no., registrant, ts, suspected orders computed downstream), `[DC-43]` Slack dispatch result.
- **Failure:** a Slack failure never blocks the send — the pool entry commits, the failure is persisted and retried `[PD-4 · OWNER-PENDING]` `[E-40]`.

### 3.13 `[L-M3]` / `[L-M3b]` Modal — Customer return restock

- **Trigger:** State 4 → `Restock Selected to Warehouse (n)`.
- **Header:** `Warehouse Restock — Order {id}`.
- **Lead copy (normative):** `Confirm the products, quantities, and locations to restock. Products with existing stock get their current location auto-filled. Restock qty defaults to 0 — enter only the qty actually returned (0 = excluded).`
- **Table:** `Product · Ordered Qty · Restock Qty · Location`. Restock Qty inputs default to `0`; Location auto-fills from existing stock (`A-03-2`) or renders an amber `required` placeholder for JIT-only SKUs (`.loc-need`). A SKU that has neither existing stock nor a JIT origin also renders the `required` field — the operator assigns a location like any new SKU `[E-88]`.
- **Warning block:** `{Brand} has restock qty 0 → excluded.` + `Entering a qty requires a location; if qty > 0 with no location, confirm stays disabled.`
- **Completion note:** `On completion, Current Stocks quantities and locations update automatically.`
- **`[L-M3b]` Memo (Optional):** one shared textarea for the whole restock, placeholder `Return reason · condition (visible damage etc.) · notes — also recorded in the order's Comments history and the inbound log`. It is **dual-persisted** — order comment history **and** the inbound log — never one or the other.
- **Validation:**
  - `Confirm Restock ({n})` where `n` = lines with qty > 0. With every line at 0 the button reads `Confirm Restock (0)` and is **disabled** `[E-28]`.
  - qty > 0 with empty location → disabled `[L-S4-4]` `[E-29]`.
  - qty > ordered qty → rejected inline (over-restock) `[E-30]`.
- **Server:** `confirm return restock`, idempotent per order + version, one transaction for all lines.
- **Persists:** `[DC-26]` with the **complete per-line array** — `{SKU, ordered qty, restock qty, location old→new}` — plus `[DC-27]` for every line left at 0. Zero-quantity lines are persisted **explicitly** inside the restock record; no disposition field is added in v1 `[PD-17 · OWNER-PENDING]`. Stock deltas persist `[DC-39]`.
- **Feedback:** green toast; Actor Log gains `Return Restock (Stock added)` rows; Current Stocks updates.

### 3.14 `[L-M4]` Modal — Print Return Labels (supplier return)

- **Trigger:** `🖨 Print Return Labels ({n})` in States 1, 1b, 2, 3.
- **Header:** `Print Return Labels — {n} Selected Products (Supplier Return)`.
- **Carrier picker:** chips `CJ대한통운` · `롯데택배` · `한진택배` · `우체국택배` · `로젠택배` · `✎ Custom`. Exactly one is active (`.cchip.on`). Choosing `✎ Custom` reveals a free-text carrier input (`#rlCarrierCustom`) and focuses it; typing updates the preview live. Korean carrier names are **data** and are never translated `[G-6]`.
- **Item table:** `Product Name KR · Size (optional) · Qty (optional)`. Empty size or qty is **omitted from the printed label**, not printed as blank or zero (the empty Size field carries the placeholder `omitted if empty`).
- **Live preview:** a bordered block showing the carrier in large bold on the first line (`#rlPreviewCarrier`), then one line per item: `{Brand} {Korean product name} · {size} · {qty}개`. Long Korean names wrap in the preview and are truncated on the physical label only by the label template, never silently in the data `[E-77]`.
- **Purpose note (normative):** `Use case: during inbound scanning, return items to the supplier (e.g. Coupang seller) when wrong/damaged items are found. Printing puts carrier name + product name (KR) + size + qty on the label — size/qty omitted if empty; attach it to the return box.`
- **Validation:** with `✎ Custom` selected and the name empty, `🖨 Print` is blocked with an inline error and the placeholder `Carrier name` is never printed `[E-31]`.
- **On `🖨 Print`:** the label is produced through the local print agent per `[G-4]` — this page adds no dialog, no preview step and no new tab of its own.
- **Persists:** `[DC-28]` with `surface=return_labels` and the full composed content (carrier, per-item Korean name, size, qty, with omitted fields recorded as omitted); `[DC-29]` `print.job_result` (canonical) with agent, printer, success/failure and error text.
- **Failure:** print-agent or printer failure raises a **red** toast naming the agent/printer `[G-2]`; nothing is rolled back `[E-39]`.
- **Out of scope:** the label's physical layout — that is Phase 3-1 (§9.1).

### 3.15 `[L-M5]` Modal — Save Partial Inbound

- **Trigger:** State 6 → `Save Partial Inbound`.
- **Header:** `Save Partial Inbound — Inbound No. {n}`.
- **Body:** the shortfall stated in words — `Only {received} of the {expected} expected units have been received ({remaining} remaining).` — then the per-SKU line `{product} — expected {e} / received {r} / remaining {rem}`.
- **Fields:** `Reason` select (**required**, exactly these three options, byte-exact): `Split shipment — remainder arriving later` · `Short delivery (needs supplier confirmation)` · `Partially damaged — will be returned to supplier`. Then `Memo (Optional)` textarea, placeholder `e.g. Remaining 180 units arriving Friday — also recorded in the request's Comments`.
- **Contract note (normative):** `On save — the {received} received units are added to Inventory immediately, and the Inbound Request List switches to Partial Inbound ({received}/{expected}) (3 stages: REQUESTED → PARTIAL → INBOUNDED). When the remainder arrives, rescan the same tracking number to continue in State 6.`
- **Behavior:** received units enter Inventory **immediately** — they are physically in the warehouse and must be sellable. The request moves to `PARTIAL` with an amber `{received}/{expected}` badge visible in the State 0 Expected Inbound table and in the Inbound Request list `[G-11]`.
- **Resume:** rescanning the same tracking number re-opens State 6 **from the current received totals**, never from zero `[E-22]`.
- **Server:** `save partial inbound`, idempotent per request + version.
- **Persists:** `[DC-36]` (per-SKU received, reason enum, memo, actor, ts), `[DC-38]` status old→`PARTIAL`, `[DC-39]` inventory deltas, `[DC-19]`/`[DC-23]` memo into the request's comments.
- **Feedback:** green toast; State 6 re-renders with the saved totals; focus back to search.

### 3.16 `[L-M6]` Modal — Edit Expected Qty

- **Trigger:** State 6 → `✎` on a row's `Expected Qty` (decided 2026-08-02).
- **Header:** `Edit Expected Qty — Inbound No. {n}`.
- **Body:** `{product} — current Expected Qty {n}`; `New Expected Qty` number input with a live delta helper (`300 → 120 (−180)`); `Reason (required)` select with **exactly** these three option labels, byte-exact from the wireframe and canonical per `_review.md` C-11: `Damaged/defective — cannot accept` · `Supplier qty change` · `Other`. `[G-11]` names the third option "Other (memo)" — that phrasing describes the obligation to explain in the memo, not the option string `[BR-53]`. Then `Memo` textarea (prefilled example: `1 box damaged — 180 units rejected, returned to supplier`).
- **Contract note (normative):** `On save — Expected Qty updates {old} → {new}, and the remaining / full-confirm gating recalculates (current received {r} = {r}/{new} → Confirm Full Inbound enabled). The edit is auto-posted as a Comment on this Inbound Request and the requester (@{name}) gets a Slack alert. The request list qty cell shows the edit history ({old}→{new}).`
- **Validation:**
  - Reason is **mandatory** — `Save Qty Edit` is blocked without it `[E-25]`.
  - New expected qty **may not be lower than the already-received qty**; attempting it is a hard block with inline validation `New expected qty cannot be lower than the received qty ({n})` `[PD-14 · OWNER-PENDING]` `[E-24]`. Allowing it would create a permanent over-receipt no screen can clear.
  - New qty must be a positive integer; `0` is rejected — removing a line is an Inbound Request operation, not a quantity edit `[E-80]`.
  - The modal carries the row's version; if the line changed server-side while the modal was open, the save is rejected with a red toast and the modal reloads `[E-81]` `[PD-6 · OWNER-PENDING]`.
- **Gate effect:** lowering expected to exactly the received quantity **re-enables** `Confirm Full Inbound` — it does **not** auto-confirm. A human still presses the button `[PD-84 · OWNER-PENDING]`.
- **Origin rule:** expected-qty edits originate **only here**. The Inbound Request list *displays* the resulting history and offers no edit control `[G-11]`.
- **Server:** `patch inbound-request expected qty`, idempotent per request + SKU + version.
- **Persists:** `[DC-35]` (request, SKU, expected old→new, reason enum, memo, editor, ts) → emits `[DC-23]` auto-comment (`source=system`) and `[DC-20]`/`[DC-43]` Slack to the requester.
- **Feedback:** green toast; tiles, `Remaining`, row status and the confirm gate all recompute in place.

### 3.17 Page furniture (no legend dots)

#### `[L-F1]` Global navigation bar and session identity
Renders `SkinSeoul` brand, the section menus (`Operation AI ▾`, `Catalog Management ▾`, `OMS Center ▾`, `Site Management ▾`), the Comments hub button `[L-S1-3]`, the signed-in user (avatar + name) and `Logout`. The signed-in user is the **actor** recorded on every event in §5 `[G-8]`. The exact production nav differs per page and is applied from each screen's real capture (2026-07-21 decision); the wireframe's four menus are illustrative. A session that expires mid-action fails the action with an explicit re-authentication prompt and never silently drops the mutation `[E-70]`.

#### `[L-F2]` Order header card
`Order ID: {id}` (blue) · `Order Status:` + status pill · `Total Quantity: {n}` · then the action controls. Status pill classes: `.st-processing`, `.st-prepare`, `.st-hold`, and a red variant for `refunded`. Present in States 1–5, absent in 6/6b.

#### `[L-F3]` `🖨 Print` (order label) — `[G-4]` print surface
Present in States 1, 1b, 2, 3, 5; **absent in State 4** (a returned order is not re-labelled). Clicking prints the order's shipping label through the local print agent per `[G-4]`. Persists `[DC-28]` `surface=order_label` and `[DC-29]`. Failure → red toast, nothing rolled back `[E-39]`.

#### `[L-F4]` `🔍 Search` button
An explicit submit (`.btn-blue`, label `🔍 Search`) alongside the scanner's Enter. Identical behavior and identical persistence to `[L-S0-1]`; it exists for keyboard-free manual lookups. Empty submit is a no-op `[E-10]`.

#### `[L-F5]` Row checkboxes and header select-all
The header checkbox toggles all **currently rendered** rows; per-row checkboxes drive `Bulk Inbound (Selected)` and `Restock Selected to Warehouse (n)`. Selection state is **ephemeral client state and a declared NON-event** (§5.9-1) — only the resulting bulk invocation persists `[DC-46]`.

#### `[L-F6]` Result counter
`Found {n} item(s) in this order · Found {m} order(s)` under the table. Purely derived; it must reflect the rendered rows exactly, so a mismatch is a visible integrity failure.

#### `[L-F7]` Page heading and section labels
`WMS - View Orders` (`h2`) with the section labels `Search Orders` above the search row and `Search Results` above the results area. These are the operator's only orientation cues when several admin tabs are open, so the heading text is fixed and must not be replaced by an order number or a state name. Present in every state including 6/6b.

#### `[L-F8]` State 0 waiting placeholder
A dashed panel between the search row and the Expected Inbound badge reading `📡` / `Waiting for scan` / `Scan a tracking/product barcode or type a number to switch to that order's screen instantly`. It exists so an idle station reads as *ready*, never as *broken*, from across the room. It is replaced by the results area the moment a scan resolves and is never shown together with an order card.

---

## 4. Business Rules

Every rule carries a rationale and a decision date. Rules that reverse an earlier decision also appear in §10.2. Global rules are cited, never restated.

| ID | Rule | Rationale | Decided |
|---|---|---|---|
| **BR-1** | Search resolution follows one fixed precedence: inbound-request tracking → return last-mile → customer order → product-in-order → unrecognized. Ambiguity never resolves silently; it renders a candidate list. | Internal inbound and customer fulfilment are different physical processes; guessing between them would put stock in the wrong ledger. | 2026-07-09, extended 2026-08-02 |
| **BR-2** | A Coupang QR scan arriving as `[V1]{barcode}` matches identically to the bare barcode. The rule text is never rendered on screen. | The scanner emits the wrapper; operators cannot strip it. Showing the rule on screen wasted a line the operator never reads. | 2026-07-13, text moved off-screen 2026-07-23 |
| **BR-3** | A multi-match never auto-picks. | A wrong silent pick is invisible until the wrong parcel ships. | 2026-07-09 |
| **BR-4** | Sourcing routes render as colourless black bold text; only **JIT** can be `PENDING`; JIT always shows its purchase channel in parentheses; an Existing-inventory pick shows **that stock's own route**, not JIT. Order-facing values are the four of `[G-5]`; OTHER-origin renders `OTHER ({channel})` `[PD-80 · OWNER-PENDING]`. | Colour is reserved for the five attention states (§1.3-3). Smart Buy / Wholesale / Partnership goods are already in the warehouse, so a PENDING badge on them would be a data error. | 2026-07-13; JIT channel parenthesis 2026-08-03 |
| **BR-5** | The sourcing route displayed on an order line is the route assigned on the **Inbound Request**, matched **by tracking number**. View Orders never invents a route. | One origin for the route means Inventory, Order Detail and this page can never disagree. | 2026-07-13 |
| **BR-6** | Inbounding the **last** remaining line completes the order and therefore **auto-triggers Outbound** — in the scan flow (`Inbound + Outbound`) and the bulk flow (`Inbound + Outbound All Remaining`) **only**. A held order stops at INBOUNDED. Order Detail never auto-outbounds `[PD-21 · OWNER-PENDING]`. | Removes a click from the busiest second of the day (§1.3-5). Order Detail is a desk screen for exception handling; silent shipping from an inspection screen is the wrong default. | 2026-07-09; Order Detail boundary 2026-08-03 |
| **BR-7** | A held order accepts Inbound and refuses Outbound, in the UI and on the server. | The goods are physically present and must be recorded; only the shipment is frozen. | 2026-07-13 |
| **BR-8** | The row action button is `Inbound` while ≥2 lines are uninbounded and becomes `Inbound + Outbound` when exactly 1 remains. | The label states the consequence of the click at the moment of the click. | 2026-07-09 |
| **BR-9** | `Outbound` is enabled **iff** the order has ≥1 line **and** every line is INBOUNDED **and** status ∈ {`processing`, `pending`} **and** not on hold **and** not already outbounded. Blocked from `on-hold`, `refunded`, `failed`, `completed`, `shipped`, `prepare-shipment` `[PD-29 · OWNER-PENDING]`. | Makes the gate a pure function of status + inbound completeness, so client and server can compute it identically. | 2026-08-03 |
| **BR-10** | After Outbound, every per-line `Cancel Inbound` is disabled; `Cancel Outbound` must run first. **(State 3 only** — State 4 return mode's `Cancel Inbound → Add Stock` `[L-S4-1]` is a separate trigger into `[L-M1]` and is outside this lockout; that is why a returned, already-outbounded order still offers live per-line buttons.**)** | Keeps inventory arithmetic reversible and prevents an order in `prepare shipment` from holding a PENDING line. | proposed 2026-07-09, adopted 2026-08-03 `[PD-10 · OWNER-PENDING]` (defect **WF-3**); State-4 scope note added 2026-08-03 |
| **BR-11** | `Cancel Outbound` rolls status `prepare shipment → processing` and touches **no** line-level inbound state. | Outbound is an order-level fact; reversing it must not silently reverse goods receipt. | 2026-07-09 |
| **BR-12** | There is **no `returned` status**. The 8 statuses are `pending`/`processing`/`on-hold`/`completed`/`refunded`/`failed`/`shipped`/`prepare-shipment`. Return mode is entered by **scanning the last-mile return barcode**, never by status. Returns may arrive as `refunded`, `failed`, or `completed`. | Refused deliveries and customs returns come back before any refund; a status-driven detector would miss them entirely. | 2026-07-13 |
| **BR-13** | Return restock quantity defaults to **0**; 0 means excluded; there are no checkboxes. Any line with qty > 0 requires a location before confirm. | Only the physically returned units may re-enter stock. Defaulting to the ordered quantity would silently restock goods that never came back. | 2026-07-09 |
| **BR-14** | Single-item orders auto-print the shipping label the instant the barcode is scanned — **only** when the order has no inbound history. **Existing Inventory stock does not count as inbound history.** | Single-item orders are the volume driver and are picked in one motion; requiring a click would cost more than the print. | 2026-07-09 |
| **BR-15** | Printing never gates goods movement. A print-agent or printer failure raises a red toast and persists a job result; the inbound/outbound/restock still commits. | Blocking goods receipt on a printer is a stop-the-line risk. | 2026-08-03 `[PD-19 · OWNER-PENDING]` |
| **BR-16** | A barcode entered on a barcode-less product line writes to the **product master** and is recognized from the next scan. A barcode already bound to a different SKU is rejected. | One barcode must resolve to one SKU or every future scan is ambiguous. | 2026-07-13 |
| **BR-17** | A tracking number registered on a **matching-active** Inbound Request always opens State 6, and **every** tracking number of a split shipment matches the same request; partial arrivals accumulate. A number whose request has been **cancelled** no longer matches — it resolves as an unrecognized barcode `[E-95]`. | Split shipments are normal; one request must survive several boxes `[G-10]`. A cancelled request is dead: letting its number still open State 6 would let it swallow a live scan and re-animate a terminal request (`inbound-request` `BR-34`). | 2026-08-03 · cancellation clause **owner-decided 2026-08-03** |
| **BR-18** | `Confirm Full Inbound` requires `received == expected` for **every** SKU (exact match — over is as wrong as under) **and** a location on every received SKU **and** at least one SKU line. | Exact match is the only state that proves the count. This is deliberately the same gating class as the Closing page. | 2026-07-27; location gate 2026-08-03 `[PD-13 · OWNER-PENDING]` |
| **BR-19** | Over-scan in State 6 **warns and counts**; it does not cap. The excess blocks full confirm until resolved via M6 or M5. | Capping would make the exact-match gate trivially satisfiable and would hide real over-deliveries. | 2026-08-03 `[PD-12 · OWNER-PENDING]` |
| **BR-20** | Stock may not enter Inventory without a location. | `[G-14]` one-location-per-SKU means a location-less unit is unfindable. | 2026-08-03 `[PD-13 · OWNER-PENDING]` |
| **BR-21** | One location holds one SKU (1:1). Assigning an occupied location is blocked with an error naming the occupant. | The audit walking order and Inventory's "By Location" card both assume 1:1. | 2026-08-03 `[PD-46 · OWNER-PENDING]` |
| **BR-22** | Expected-qty edits require a reason from the fixed enum, may never go below the already-received quantity, may not be `0`, originate **only** in M6, and **never auto-transition** the request to INBOUNDED. | A reason makes the change auditable; a floor prevents an unclearable over-receipt; gating enables, it never commits. | 2026-08-02; floor + no-auto-transition 2026-08-03 `[PD-14 · OWNER-PENDING]` `[PD-84 · OWNER-PENDING]` |
| **BR-23** | `Save Partial Inbound` applies the received units to Inventory **immediately**, sets the request to `PARTIAL ({received}/{expected})`, and rescanning the same tracking resumes from the saved totals. | The goods are in the building and must be sellable; forcing a full match before any stock lands would strand them. | 2026-08-02 |
| **BR-24** | **Received Date is recorded automatically. Carrier is not recorded at all** — no field, no column, no capture, on this page or on the Inbound Request. | Reverses the 2026-07-09/2026-07-27 "Received Date + Carrier automatic" note. Carrier is not reliably derivable at scan time and a wrong carrier is worse than none. | 2026-08-03 `[PD-9 · OWNER-PENDING]` (defect **WF-1** — fixed in the wireframe 2026-08-03) |
| **BR-25** | Rescanning the tracking of a fully INBOUNDED request opens the **read-only** State 6b view plus an info toast. | The operator's question is "did this arrive?"; a read-only answer is correct, an error toast is not. | 2026-08-03 `[PD-15 · OWNER-PENDING]` |
| **BR-26** | Rescanning an already-INBOUNDED product barcode inside a customer order shows an amber warning toast `Already inbounded — {SKU}`, performs no second inbound, and plays no send sound. | A silent no-op reads as a failed scan and makes the operator scan again; an error state would break the scan loop. | 2026-08-03 `[PD-11 · OWNER-PENDING]` |
| **BR-27** | Confirming an unrecognized match writes the tracking number **onto the order's product line**, so rescanning the same barcode resolves normally. | The fix must survive the operator's next physical action, which is to scan the same box again. | 2026-08-03 |
| **BR-28** | An on-the-spot match in M2 fires the same match-confirmed auto-comment and Slack route as a tracking-missing resolution; the `@mention` is suppressed when resolver == registrant. | One match pipeline, one audit trail, regardless of which screen resolved it — and nobody should be notified about their own action. | 2026-08-03 `[PD-16 · OWNER-PENDING]` |
| **BR-29** | A Shelf value persists while the order is open and **auto-clears on Outbound**, with old→new captured. | Temporary shelves must be reusable; a stale shelf on a shipped order misdirects the next picker. | 2026-08-03 `[PD-18 · OWNER-PENDING]` |
| **BR-30** | Focus invariants: after every action, every modal close, and every completion, the search input is focused with its content selected — **except** while the operator is typing in another field, where auto-refocus must not fire. | The scanner types blind; a stolen focus silently writes barcodes into comments and quantities. | `[G-1]`, exclusion 2026-08-03 |
| **BR-31** | **No page refresh, ever, on this page.** View Orders has zero refresh exceptions. | The scan loop cannot survive a reload — focus, the current order, and the operator's place in the box are all lost `[G-2]`. | 2026-08-03 |
| **BR-32** | Send sound plays on exactly three controls (`Outbound`, `Inbound + Outbound`, `Inbound + Outbound All Remaining`) and never on cancel, disabled, or inbound-only controls. State 6's wrong-product tone is a **different** sound and is not TTS. | Two sounds must mean two different things or neither means anything. | 2026-08-03 `[G-3]` `[PD-2 · OWNER-PENDING]` |
| **BR-33** | **No page delta on `[G-7]`'s append-only clause.** Every comment surface on this page inherits it unchanged: the order comment panel `[L-S1-19]`, the order Comments button `[L-S1-11]`, the Comments hub `[L-S1-3]`, and State 6/6b request comments. The negative is recorded at §9.4-11. | Stated as a no-delta row so a reader does not look for a page-local exception that does not exist. | 2026-08-03 `[PD-3 · OWNER-PENDING]` |
| **BR-34** | **No page delta on `[G-9]`.** This page's scope of "confirming action" is enumerated once, at `[E-13]`, and the rejected duplicate persists `[DC-13]` so the fix is provable. | `[G-9]` fixes the rule; the page owes the list of controls it applies to and the evidence trail, nothing more. | 2026-07-21 (handoff note A), scope enumerated 2026-08-03 |
| **BR-35** | **No page delta on `[G-15]`:** no control on this page is role-gated, and no state, modal or bulk action varies by user. | Recorded because six screens raised the question; the answer here is "nothing page-specific". | 2026-08-03 `[PD-1 · OWNER-PENDING]` |
| **BR-36** | **Page delta on `[G-6]`:** the brand-in-bold prefix applies to **both** the `Product Name` and `Product Name KR` columns of this page's tables `[L-S1-18]`, and to the product lists inside M2, M2b and M4. No delta on the never-translate clause — Korean product, carrier and supplier names pass through verbatim. | The two-column repetition is page-specific: pickers read whichever column their eye lands on first, so the brand must anchor both. | 2026-07-13 |
| **BR-37** | The Live Barcode Feed shows **exactly 20** rows; the full history is retained backend-side and exportable by date. | The legend's "10–20" is unassertable in QA; the panel footer already says 20 (defect **WF-13**). | 2026-08-03 |
| **BR-38** | A `Qty` cell ≠ 1 renders amber. It blocks nothing. | Multi-unit picks are the most common picking error; the cue costs nothing. | 2026-07-09 |
| **BR-39** | The customer-order table's column set is **identical in every state** (States 1–5, 14 columns). Per-state column reduction is forbidden, and adding a column requires re-checking the one-screen fit `[L-S1-4]`. | Operators build muscle memory on column positions; a shifting table costs a glance per row. | 2026-07-09 |
| **BR-40** | The **Deleo Tracking No** column must **NOT** exist on this page. It lives on Order Detail only. | Deliberate asymmetry: the warehouse works from the courier tracking number, the desk works from the carrier reference. | 2026-07-22 |
| **BR-41** | **No photo capture anywhere on this page** — not in M2, not in M2b, not on a product line. Removed, not deferred. | Leaving it "deferred" invites re-implementation from stale docs. | 2026-07-21 hold → 2026-08-03 deletion `[PD-63 · OWNER-PENDING]` |
| **BR-42** | A Slack delivery failure never blocks and never rolls back the primary action; it is persisted and retried. | Notification is a side effect, not part of the transaction. | 2026-08-03 `[PD-4 · OWNER-PENDING]` |
| **BR-43** | The server revalidates the entity at confirm time; on mismatch it rejects with a red toast and refreshes the affected view, with **no partial writes**. | A stale client is normal in a warehouse with several stations open on the same order. | 2026-08-03 `[PD-6 · OWNER-PENDING]` |
| **BR-44** | Concurrency: order-level edits use an optimistic version check → 409 → reload the row + non-green toast. **State 6 counting merges server-side** instead, because the value is a running total. | Last-write-wins would destroy counted units; merge is correct only where the value accumulates. | 2026-08-03 `[PD-7 · OWNER-PENDING]` |
| **BR-45** | An inbound tracking number is unique system-wide. Inbound and outbound tracking numbers are **separate namespaces** and may coincide; when they do, inbound-request tracking wins the resolution. | Matching integrity needs one owner per number; carriers reuse number ranges across directions. | 2026-08-03 `[PD-8 · OWNER-PENDING]` `[PD-86 · OWNER-PENDING]` |
| **BR-46** | The unified search has **no type toggle** and shows **no "matched field" badge**. Both were removed. | The operator does not know what kind of number is on the label; asking them costs a decision per scan. | 2026-07-09 |
| **BR-47** | The bulk bar is always rendered in every state; unavailable actions are **disabled, not hidden**. | A control that vanishes teaches the operator it does not exist; a greyed one teaches when it applies. | 2026-07-09 |
| **BR-48** | An unrequested arrival (goods with no matching inbound request) routes to the **shared unrecognized pool**, not to an ad-hoc registration path on this page. | A dedicated intake path was explicitly rejected — it would create a second, unaudited way for stock to appear `[G-11]`. | 2026-08-02 |
| **BR-49** | Existing-inventory lines are distinguished by the **Sourcing Route badge plus the row tint** — never by a duplicate label under the product name. | The duplicate label was removed as visual noise. | 2026-07-09 |
| **BR-50** | This page never applies or releases a Hold, never edits an order's status directly, and never creates an Inbound Request. It only displays and acts within those facts. | Single ownership of each mutation; the owning screens are Order Detail / Order Management / Inbound Request. | 2026-07-13 |
| **BR-51** | The floating-save `✓ Saved` chip is the `[G-2]` confirmation for shelf, location and received-qty micro-saves — rendered in place beside the field instead of the top-right slot. Failures still use the red top-right toast. | The operator's eye is already on the field; a top-right toast per keystroke-save would be noise during continuous editing. This is a rendering-position delta, never a removal of the confirmation. | 2026-08-03 (page delta on `[G-2]`, `_review.md` C-6) |
| **BR-52** | View Orders State 6 (with the Inbound Request lifecycle) is the **only** path that confirms a PENDING inbound event. Inventory shows PENDING rows read-only and offers no confirm affordance. | Two confirm paths for one fact is the double-entry failure the whole design avoids. | 2026-08-03 `[PD-41 · OWNER-PENDING]` |
| **BR-53** | M6's third reason option label is exactly `Other`. `[G-11]`'s "Other (memo)" phrasing names the memo obligation, not the option string. | The wireframe M6 strings are canonical (`_review.md` C-11); a QA assertion needs one exact string. | 2026-08-03 |
| **BR-54** | A submit that arrives while a previous resolution is still in flight is queued and processed in order. Scans are never dropped and never interleave. | A fast operator out-runs the network; a dropped scan is an uncounted box. | 2026-08-03 |
| **BR-55** | A bulk action returns per-line results. A batch in which some lines failed is reported as **partial**, naming the failing lines; the successful lines are not rolled back. | An unqualified "success" toast over a partial batch is how stock silently goes missing. | 2026-08-03 |
| **BR-56** | State 6's `Received Qty` input stays editable at every stage, including after a SKU reaches its expected quantity. | An over-count discovered one row later must be correctable without cancelling the whole receipt. | 2026-08-03 (demo limitation **L-14**) |
| **BR-57** | A **cancel-inbound under-restock books its remainder as an inventory adjustment** — `ADJUST(−remainder)` with the same memo, in the same transaction and under the same idempotency key as the cancel `[DC-39]` `origin=cancel_inbound_remainder`. A memo never accounts for stock. Restock qty `0` with `Yes` selected is blocked; `No` is the zero path. | Spec v1.1 said the difference was "accounted for by the memo", which is not an event and loses the units from the ledger — a `[G-8]` violation, and a divergence from Inventory's M4 release path, which books the same adjustment for the same physical fact. | 2026-08-03 (cross-page audit) `[PD-49 · OWNER-PENDING]` |
| **BR-58** | **Restocked stock never enters Inventory location-less.** M1 pre-fills the SKU's registered location (editable — an edit relocates the SKU, one location per SKU `[G-14]`); when the SKU has no registered location, a location is **required** and `Confirm` stays disabled until one is entered. | Same doctrine as State 6's `[L-S6-7]` gate `[PD-13 · OWNER-PENDING]`: a JIT-residual restock is warehouse stock being born, and stock without a position cannot be picked. | 2026-08-03 (owner) |

---

## 5. Data Capture

**Doctrine `[G-8]`:** the UI logs on this page — the Actor Log `[L-S1-13]`, the Live Barcode Feed `[L-S1-16]`, the comment panels — are **views over persisted events, never the only copy**. Deleting or filtering a UI row never deletes an event. Anything operator-initiated that is not listed in §5.9 as a NON-event **must** persist.

Names below are lowercase `entity.action` semantic names. The canonical cross-page names — **9 groups covering 11 literal names** — must be byte-identical wherever they appear and are marked ⓒ: `comment.posted` · `comment.mention_notified` · `comment.starred` / `comment.unstarred` · `comment.read` / `comment.mark_all_read` · `comment.auto_posted` · `product.barcode_registered` · `order.status_changed` · `order.outbounded` · `print.job_result` (9 groups; the two slash-groups contribute two literal names each). Literal API/endpoint naming is a developer decision.

**Five names below are page-scoped, not canonical.** `[DC-13]` `idempotency.duplicate_rejected`, `[DC-39]` `inventory.stock_applied`, `[DC-24]` `comment.search_executed`, `[DC-43]` `slack.dispatch_result` and `[DC-6]` `item.inbounded` describe concepts that other screens also persist under different names. They are **not** in `[G-8]`'s canonical list, so no cross-page byte-identity is claimed for them; the reconciliation is §9.5 CP-7. Until `[G-8]` adopts one name per concept, a consumer joining events across screens must map them, and this spec says so rather than pretending the divergence does not exist.

Every event carries this envelope unless stated otherwise: `event_id` · `actor_id` (the signed-in user of `[L-F1]`) · `occurred_at` (server time, displayed KST) · `source_screen = view-orders` · `source_state` (s0/s1/s1b/s2/s3/s4/s5/s6/s6b/m1…m6) · `idempotency_key` where the event came from a confirming action · `client_request_id`.

### 5.1 Scan, search and entry

| ID | Event | Entity | Payload (beyond envelope) | Surfaced in UI |
|---|---|---|---|---|
| **DC-1** | `scan.submitted` | — | `raw_value`, `normalized_value` (after `[V1]` strip), `input_method` ∈ {scanner, manual, search_button}, `resolution` ∈ {customer_order, inbound_request, return, product_in_order, unrecognized, multi_match, empty}, `resolved_entity_type`, `resolved_entity_id`, `candidate_count`, `latency_ms` | Live Barcode Feed `[L-S1-16]` (20 rows) |
| **DC-2** | `search.manual_query` | — | `query`, `result_count`, `typed=true` | no |
| **DC-3** | `search.multi_match_selected` | resolved entity | `candidates[]` (type + id + label as shown), `chosen_entity_type`, `chosen_entity_id`, `position_in_list` | no |
| **DC-4** | `scan.unrecognized` | — | `barcode`, `opened_modal=M2` | no |
| **DC-5** | `scan.entry_state6` | inbound_request | `inbound_no`, `entry_method` ∈ {tracking_scan, badge_row_click}, `tracking_no` (null on badge click), `request_status_at_entry` | no |

`[DC-5]`'s `entry_method` exists so the damaged-label path is measurable: a rising share of `badge_row_click` is direct evidence that supplier labels are arriving unreadable.

### 5.2 Customer-order lifecycle

| ID | Event | Entity | Payload | Old → new |
|---|---|---|---|---|
| **DC-6** | `item.inbounded` | order line | `order_id`, `sku`, `qty`, `method` ∈ {row_button, combined_button, bulk, scan}, `sourcing_route`, `tracking_no` | line status `PENDING → INBOUNDED` |
| **DC-7** | `item.bulk_inbound_batch` | order | `order_id`, `sku_list[]`, `line_count`, `child_event_ids[]`, `failed_line_ids[]` `[BR-55]` | — (parent of `[DC-6]` children) |
| **DC-8** ⓒ | `order.outbounded` | order | `order_id`, `sku_set[]`, `total_qty`, `trigger` ∈ {manual, combined_last_item, bulk_all_remaining} | — |
| **DC-9** ⓒ | `order.status_changed` | order | `order_id`, `reason` ∈ {outbound, cancel_outbound, external} | `processing → prepare shipment` / `prepare shipment → processing` |
| **DC-10** | `order.outbound_suppressed_hold` | order | `order_id`, `hold_requester`, `hold_reason`, `inbound_completed_at` | — |
| **DC-11** | `item.inbound_cancelled` | order line | `order_id`, `sku`, `cancelled_qty`, `restock` ∈ {true,false}, `restock_qty`, `restock_location` old→new, `memo` | line `INBOUNDED → PENDING`; stock `Reserved {n} → Available {m}` |
| **DC-12** | `order.outbound_cancelled` | order | `order_id` | (emits `[DC-9]`) |
| **DC-13** | `idempotency.duplicate_rejected` | any | `original_event_id`, `idempotency_key`, `action`, `arrival_delta_ms` | — |
| **DC-44** | `order.mutation_rejected` | order / line | `attempted_action`, `reason` ∈ {on_hold, status_forbids_outbound, already_outbounded, line_locked_after_outbound, stale_version, no_lines, session_expired}, `server_state_snapshot` | — |
| **DC-46** | `bulk.action_invoked` | order | `button` ∈ {bulk_inbound_selected, inbound_outbound_all_remaining, restock_selected}, `selected_line_ids[]`, `visible_row_count`, `excluded_line_ids[]` + reasons | — |

`[DC-10]` and `[DC-44]` exist because **the absence of an expected action must be explainable**. Without them, "why was this order never outbounded?" is unanswerable six weeks later. `[DC-13]` exists to **prove** the double-click bug is fixed `[BR-34]`.

### 5.3 Shelf, location, barcode master

| ID | Event | Entity | Payload | Old → new |
|---|---|---|---|---|
| **DC-14** | `order.shelf_assigned` | order | `order_id`, `save_method` ∈ {click, enter} | `shelf {old} → {new}` (either may be null) |
| **DC-15** | `order.shelf_cleared` | order | `order_id`, `trigger` ∈ {outbound, manual_clear} | `shelf {old} → null` |
| **DC-16** | `inbound_request.location_assigned` | request line | `inbound_no`, `sku`, `suggested` ∈ {true,false} | `location {old} → {new}` |
| **DC-17** ⓒ | `product.barcode_registered` | product (master) | `sku`, `barcode`, `source_screen`, `source_state` | `barcode null → {value}` |
| **DC-18** | `product.barcode_register_rejected` | product | `sku`, `attempted_barcode`, `reason` ∈ {duplicate_other_sku, invalid_format}, `conflicting_sku` | — |

`[DC-17]` is a **product-master** write raised from a warehouse screen; that is exactly why `source_screen` and `source_state` are mandatory on it.

### 5.4 Comments `[G-7]`

| ID | Event | Entity | Payload | Notes |
|---|---|---|---|---|
| **DC-19** ⓒ | `comment.posted` | order · inbound_request · unrecognized_pool_item | `entity_type`, `entity_id`, `text`, `mentioned_user_ids[]`, `source` = `user` | append-only `[BR-33]` |
| **DC-20** ⓒ | `comment.mention_notified` | comment | `comment_id`, `mentioned_user_id`, `channel`, `slack_message_ts`, `deep_link` | one per mentioned user |
| **DC-21** ⓒ | `comment.starred` / `comment.unstarred` | comment | `comment_id`, `entity_id` | drives the hub's ★ Saved tab |
| **DC-22** ⓒ | `comment.read` / `comment.mark_all_read` | comment(s) | `comment_ids[]` | badge integrity |
| **DC-23** ⓒ | `comment.auto_posted` | inbound_request · order | `source = system`, `kind` ∈ {expected_qty_edit, match_confirmed, partial_saved, cancel_inbound_memo, return_restock_memo}, structured `old`/`new` payload | system-authored, same pipeline |
| **DC-24** | `comment.search_executed` | — | `query`, `hit_count`, `scope=all_comments` | analytics-tier retention (§5.10) |

Memos are **dual-persisted, never single-homed**: M1's memo lands in `[DC-11].memo` **and** as a `[DC-23]` comment on the order; M3b's shared memo lands in `[DC-26].memo`, in the Actor Log row, **and** as a `[DC-23]` comment; M5's memo lands in `[DC-36].memo` **and** as a comment on the request.

### 5.5 Customer return

| ID | Event | Entity | Payload | Old → new |
|---|---|---|---|---|
| **DC-25** | `return.scan_detected` | order | `return_barcode`, `order_id`, `order_status_at_scan` ∈ {refunded, failed, completed, …}, `was_outbounded` ∈ {true,false} | — |
| **DC-26** | `return.restock_confirmed` | order | `order_id`, `lines[] = {sku, ordered_qty, restock_qty, location_old, location_new}`, `memo` | per SKU `stock {old} → {new}` |
| **DC-27** | `return.line_excluded` | order line | `order_id`, `sku`, `ordered_qty`, `restock_qty = 0` | — |

`[DC-27]` is deliberate: the lines that did **not** come back are the damage/loss signal, and they are persisted explicitly inside the restock record. No disposition field is added in v1 `[PD-17 · OWNER-PENDING]`.

`[DC-25].order_status_at_scan` is what proves `[BR-12]` in production — it will show returns arriving as `completed`. `was_outbounded` catches the impossible-looking case of a return for an order that never shipped `[E-87]`.

### 5.6 Printing `[G-4]`

| ID | Event | Entity | Payload |
|---|---|---|---|
| **DC-28** | `print.requested` | order / order lines | `surface` ∈ {order_label, auto_single_item, return_labels}, `order_id`, `carrier` (chip label or free-text custom), `composed_content` (for return labels: per-item Korean name, size, qty — omitted fields recorded as omitted), `job_id` |
| **DC-29** ⓒ | `print.job_result` | print job | `job_id`, `agent_id`, `printer_id`, `status` ∈ {success, pending, agent_offline, printer_unreachable, timeout, rejected}, `error_text`, `duration_ms` |
| **DC-30** | `print.auto_single_item_evaluated` | order | `order_id`, `line_count`, `has_inbound_history` ∈ {true,false}, `existing_inventory_lines`, `decision` ∈ {printed, skipped}, `trigger_scan_event_id` |

`[DC-30]` records the **precondition evaluation, not only the outcome** — `[BR-14]`'s "Existing Inventory does not count as inbound history" clause is subtle enough that a wrong implementation would otherwise be invisible. `[DC-29].printer_id` is what exposes a job that succeeded on the wrong device `[E-91]`.

### 5.7 Internal inbound (States 6/6b, M5, M6)

| ID | Event | Entity | Payload | Old → new |
|---|---|---|---|---|
| **DC-31** | `inbound_request.scan_counted` | request line | `inbound_no`, `sku`, `barcode`, `method = scan` | `received {n} → {n+1}` |
| **DC-32** | `inbound_request.received_qty_edited` | request line | `inbound_no`, `sku`, `method = manual` | `received {old} → {new}` |
| **DC-33** | `inbound_request.wrong_product_scanned` | request | `inbound_no`, `scanned_barcode`, `resolved_sku` (nullable), `warning_tone_played` | nothing incremented |
| **DC-34** | `inbound_request.over_scan_warned` | request line | `inbound_no`, `sku`, `expected`, `received_after`, `excess` | — |
| **DC-35** | `inbound_request.expected_qty_edited` | request line | `inbound_no`, `sku`, `reason` (enum, verbatim string), `memo`, `editor` | `expected {old} → {new}` |
| **DC-36** | `inbound_request.partial_saved` | request | `inbound_no`, `lines[] = {sku, expected, received, remaining, location}`, `reason` (enum, verbatim), `memo` | request `{REQUESTED / PARTIAL} → PARTIAL` |
| **DC-37** | `inbound_request.fully_inbounded` | request | `inbound_no`, `lines[] = {sku, expected, received, location}`, `received_date` (auto), **no carrier field** `[BR-24]` | — |
| **DC-38** | `inbound_request.status_changed` | request | `inbound_no`, `trigger` ∈ {partial_save, full_confirm} | `REQUESTED → PARTIAL → INBOUNDED` |
| **DC-39** | `inventory.stock_applied` | inventory | `origin` ∈ {full_inbound, partial_inbound, return_restock, cancel_inbound_restock, **cancel_inbound_remainder**}, `lines[] = {sku, location, qty_delta}`, `source_event_id` | per SKU `on_hand {old} → {new}`, `reserved {old} → {new}` |
| **DC-45** | `inbound_request.confirm_blocked` | request | `inbound_no`, `reason` ∈ {qty_mismatch, missing_location, over_scan, no_lines}, `blocking_skus[]` | — |

`[DC-45]` turns a disabled button into data: a request that is blocked repeatedly on `missing_location` is telling you the location scheme is failing at the shelf.

### 5.8 Unrecognized flow and dispatch

| ID | Event | Entity | Payload |
|---|---|---|---|
| **DC-40** | `unrecognized.lookup_executed` | — | `barcode`, `entered_order_no`, `result` ∈ {matched, no_match}, `candidate_count` |
| **DC-41** | `unrecognized.tracking_matched` | order line | `order_id`, `sku`, `product_line_id`, `tracking_no null → {value}`, `barcode`, `resolver`, `registrant` (null for on-the-spot matches), `mention_suppressed` ∈ {true,false} `[PD-16 · OWNER-PENDING]` |
| **DC-42** | `unrecognized.sent_to_pool` | pool item | `barcode`, `chosen_product_sku`, `chosen_product_name_en`, `qty`, `memo`, `carried_failed_order_no`, `registrant`, `suspected_orders[]` |
| **DC-43** | `slack.dispatch_result` | notification | `route` ∈ {unrecognized_pool, comment_mention, expected_qty_edit, match_confirmed}, `channel`, `payload_digest`, `status` ∈ {delivered, failed, retrying}, `attempt`, `slack_ts`, `error` |

### 5.9 Explicit NON-events

The following are **ephemeral client-local state and must NOT persist**, per `[G-8]`'s non-event doctrine. Anything not on this list and operator-initiated must persist.

1. Row checkbox toggles and header select-all `[L-F5]` — only the resulting `[DC-46]` bulk invocation persists.
2. Expected Inbound badge expand/collapse `[L-S0-2]`.
3. Live Barcode Feed panel expand/collapse `[L-S1-16]`.
4. Comments panel expand/collapse `[L-S1-11]` and hub tab switching between `@ Mentions` and `★ Saved`.
5. Modal open/close where nothing was confirmed — an abandoned M1/M3/M4/M5/M6 writes nothing. (Opening **M2** is the deliberate exception: it persists `[DC-4]`, because a barcode that failed to resolve is itself the finding.)
6. Keystrokes and focus movements, including auto-refocus `[L-S1-14]`; only the submitted value persists.
7. Sorting and `row-hit` highlighting of the scanned row `[L-S1-5]`.
8. Live label preview re-rendering in M4 and the carrier-chip selection **before** Print is pressed.
9. Typing in a shelf/location/qty field **before** save — only the saved value persists (`[DC-14]`, `[DC-16]`, `[DC-32]`). Unsaved text abandoned when the state changes is discarded silently `[E-90]`.
10. Chrome-bar state switching and `Hide annotations` — wireframe-only controls that do not exist in the admin.

### 5.10 Retention and export

- **Scan history `[DC-1]`:** retained in full, without truncation, indefinitely. The Live Barcode Feed shows the last **20** on screen `[BR-37]`; the backend keeps everything and exposes **export by date range** (`Export by date` button). Every export persists `[DC-47]` `scan_feed.exported` with `actor_id`, `range_from`, `range_to`, `row_count`, `format` and `delivery` ∈ {download, email} — the feed carries operator identity, so an export is a data-egress event and must itself be auditable (governance question: §9.2 OQ-2). Export file format and the date-range picker are developer decisions.
- **Actor-log-class events (`[DC-6]`–`[DC-12]`, `[DC-25]`–`[DC-27]`, `[DC-31]`–`[DC-39]`):** permanent, append-only, queryable by order · inbound no. · SKU · actor · date. Never hard-deleted; corrections are new events. Ordering is by **server** timestamp `[E-90]`.
- **Comments (`[DC-19]`–`[DC-23]`):** permanent and append-only — an explicit AI-training and audit asset `[G-7]` `[PD-3 · OWNER-PENDING]`.
- **`[DC-24]` comment search and `[DC-2]` manual queries:** analytics-tier, minimum 90 days.
- **Print jobs (`[DC-28]`–`[DC-30]`):** permanent; job results are the only evidence of a print-agent outage.
- **Slack dispatch (`[DC-43]`):** permanent, including every retry attempt and the final failure.
- **Every UI log on this page is a projection.** Removing a row from the Actor Log, the feed, or a comment list is not offered by this page at all, and if it were, it would never delete the underlying event.

### 5.11 Late-added event

| ID | Event | Entity | Payload |
|---|---|---|---|
| **DC-47** | `scan_feed.exported` | scan history | `actor_id`, `range_from`, `range_to`, `row_count`, `format`, `delivery` ∈ {download, email} |

> **Delta from spec v1.0:** v1.0 declared 46 events but described the feed export as persisting unnamed "export metadata". The export is an operator-initiated action over operator-identifying data and therefore needs its own ID. `[DC-47]` closes that gap; the register is now **DC-1 … DC-47** with no numbering gaps.

---

## 6. Integrations

### 6.1 Slack routing

Channels are cited with their ID on first mention where `_slack-routing.md` publishes one. Payload fields are verbatim from `_slack-routing.md` (CONFIRMED 2026-08-03).

| # | Trigger on this page | Channel | Payload | Mention target |
|---|---|---|---|---|
| 1 | **M2b** `Send to Missing Tracking List` `[L-M2b]` | `#unrecognized-tracking` (no channel ID is published in `_slack-routing.md`; it is resolved at wiring time) | tracking no., product, qty, memo, registrant, suspected orders | **@mention every suspected PIC** — once per person even when several of their orders match `[G-7]` (owner-decided 2026-08-03; `tracking-missing`'s push-not-poll design depends on it) |
| 2 | **Comment `@mention`** on any comment surface of this page — order comment panel `[L-S1-19]`, order Comments button `[L-S1-11]`, State 6/6b request comments, Comments hub `[L-S1-3]` | `#fulfillment-admin-comments` (`C0BMGEWM5QA`) | entity no., comment text, time, author, @mentioned user, deep link | the mentioned person, **in the message body** — Slack raises a personal notification while the channel doubles as a team-visible archive |
| 3 | **Expected-qty edit** in M6 `[L-M6]` (auto-comment, `source=system`) | `#fulfillment-admin-comments` (`C0BMGEWM5QA`) | old→new qty, reason, editor | **@requester** of the inbound request |
| 4 | **Unrecognized match confirmed** in M2 `[L-M2]` (auto-comment, `source=system`) | `#fulfillment-admin-comments` (`C0BMGEWM5QA`) | tracking no., matched product line, resolver | **@registrant** — suppressed when resolver == registrant `[PD-16 · OWNER-PENDING]` |

**Not routed from this page** (stated so nobody adds them):

- The morning no-tracking check → `#wholesale-ops` / `#partnership-kr` belongs to the **inbound-request** screen, not here.
- `Save Partial Inbound` (M5) raises a **comment on the request** but **no separate Slack route** — the requester learns of it through the comment pipeline if they are mentioned.
- Outbound, cancel-outbound, cancel-inbound, return restock, print failures and barcode registration raise **no Slack message** at all in v1. Inventing a channel for them would create an unowned alert stream.
- Closing's "unknown order" flow is a **different, disjoint** concept from this page's "unrecognized product" flow. A closing unknown does **not** route to `#unrecognized-tracking`.

**Failure semantics:** delivery failures are persisted `[DC-43]` and retried; the primary action always commits and is never rolled back `[PD-4 · OWNER-PENDING]` `[BR-42]`. Retry policy and dead-letter handling are developer decisions.

### 6.2 Cross-page links and deep links `[G-12]`

| From | Link | To | Note |
|---|---|---|---|
| `[L-S6-2]` banner | `View in Inbound Request List →` → `../inbound-request/index.html#reqlist` | Inbound Request → Request List tab | In production this deep-links to the **specific Inbound No.**, filtered |
| `[L-S0-2]` expanded table footer | `Full list: Inbound Request → Request List` | same | Must be a real link; plain text in the mock (**L-15**) |
| `[L-S0-2]` table row click | (in-page) | State 6 for that request | The no-scan path for damaged labels; persists `[DC-5]` |
| `[L-S1-3]` hub entry click | entity page | order page · inbound request · tracking-missing pool row | Resolved pool items open the **matched order** instead `[PD-67 · OWNER-PENDING]` |
| `[L-M2b]` send | tracking-missing pool | Unrecognized Tracking page | The pool is shared; this page is one of two writers |
| `[L-M2]` match | order product line | the order itself | Writes `tracking_no` onto the line; rescanning then resolves `[BR-27]` |

**Inbound cross-page effects this page causes** (the receiving screens must reflect them without a manual step):

- `Confirm Full Inbound` / `Save Partial Inbound` → **Inventory (Current Stocks)** quantities and locations; **Inbound Request** status and Received Date. This page is the **sole** confirm path for those events `[BR-52]` `[PD-41 · OWNER-PENDING]`.
- `Cancel Inbound` with restock → **Inventory** `Reserved → Available`; a mistaken-JIT cancel-restock is the origin of the **JIT residual stock** that Inventory must display.
- `Return restock` (M3) → **Inventory** Current Stocks.
- `Outbound` → **Ready to be Outbounded** (the order leaves the ready list) and the order's status everywhere. → **Inventory**: on-hand is decremented and the reservation is closed against the shipment. Those two events are owned by `ready-to-outbound` §5 — `ready-to-outbound` `[DC-10]` `inventory.stock_decremented` and `ready-to-outbound` `[DC-20]` `inventory.reservation_consumed` — and are **not** this page's `[DC-10]` / `[DC-20]`, which are unrelated events (`order.outbound_suppressed_hold` and `comment.mention_notified`). `[DC-*]` numbering is per-spec, so the owning document must be named when citing them across pages.
- `[DC-17]` barcode registration → **product master**, visible to every screen and to every future scan.

**Deliberate non-links:** there is no link to a separate internal-inbound page — that page (`inbound-receiving`) was **killed on 2026-07-27** and merged into States 6/6b; any link to it would 404. There is no Procurement Hub link from this page (Procurement Hub is out of scope for this spec set, 2026-08-02).

### 6.3 Sheet and BI handoffs

- **Received Date auto-record** `[L-S6-F]` exists specifically **for the sheet sync** — the Inbound Request list feeds the Procurement Hub sheet, which reads the Received Date column. This is the reason the field is automatic at all. **Carrier is not part of that sync and is not captured** `[BR-24]`.
- **Inbound Request → Procurement Hub sheet pull:** the request's route, supplier, SKU, expected qty, unit cost and Received Date are pulled by the Procurement Hub pipeline. An **OTHER**-route request carries its free-text channel into the sheet `[PD-80 · OWNER-PENDING]`.
- **Live Barcode Feed export** `[L-S1-16]`: operator-triggered CSV-class export by date range, itself persisted as `[DC-47]`; encoding and column set are developer decisions.
- **No BI push from this page.** All analytics are read downstream from the persisted events in §5; this page never writes to a sheet directly.

### 6.4 Print pipeline `[G-4]`

Three print surfaces on this page, all governed by `[G-4]`:

1. **Order label** — `🖨 Print` on the order card `[L-F3]` (States 1, 1b, 2, 3, 5; absent in State 4).
2. **Single-item auto-print** — fired by the scan itself, no click `[L-S1-Fa]`, gated by `[BR-14]`. This is the page's only print trigger that is not a button.
3. **Supplier return labels** — M4's `🖨 Print` `[L-M4]`, carrier chosen from the chip row or free text.

Page deltas on `[G-4]`: this page adds no print affordance beyond those three, adds no confirmation step in front of any of them, and treats a failure as non-blocking `[BR-15]` `[PD-19 · OWNER-PENDING]`. Failure surfaces as a **red** toast naming the agent/printer and persists `[DC-29]`. A job that returns neither success nor error is held as `pending` and converted to a failure on timeout — silence is never reported as success `[E-58]`.

Label **layout and content design** — what is physically on the DELEO A4 picking sheet and the YUN 4×6 carrier label, including the sample-set dual view `[G-13]` — is **out of scope** for this spec and is handled in Phase 3-1 with the owner (§9.1).

### 6.5 Audio pipeline `[G-3]`

- **Send sound** — Web Audio synthesis, no external files. Reference implementation in the wireframe (`sndOutbound()`): sine 340 Hz → 940 Hz exponential sweep over 160 ms with a triangle 1,250 Hz tail at +140 ms. Fires on exactly the three outbound-class controls of `[BR-32]`.
- **State 6 wrong-product warning tone** — a **distinct** synthesized tone, audibly different from the send sound and **not** speech `[G-3c]`. Exact parameters are a developer decision; the requirement is discriminability at 2 m over warehouse noise.
- **No TTS on this page.** The spoken `Please check this order` alert `[G-3b]` belongs to the Closing screen only.
- AudioContext resume-after-gesture handling and synth parameters are developer decisions; a blocked AudioContext never blocks an action `[E-41]`.

---

## 7. Edge Cases & Error States

IDs are page-scoped and stable, and are **never renumbered**. Where two candidates merged, both IDs are kept on the merged entry. `E-1 … E-65` are unchanged from spec v1.0; `E-66 … E-92` were added by the audit pass to close failure modes the first draft named only implicitly; `E-93` was added by the 2026-08-03 cross-page remediation; `E-94` by the 2026-08-03 owner review (M1 restock location).

**Inventory: 93 IDs across 92 entries** (`E-18 = E-51` is one merged entry carrying two IDs).

> **`E-6` differs from the plan's `E-6` — read this before cross-referencing.** `_plans/view-orders.B.md` assigns **E-6 = "a Coupang QR scan arrives as `[V1]{barcode}` and matches as if unprefixed"**; on this page **`E-6` is the occupied-location rejection** below. The other 47 B-plan edge cases carry over at identical IDs, so this one is an accidental divergence, not a design. It is **not repaired by renumbering** — `_review.md` §3.2 forbids renumbering an assigned ID, and the fix would silently invalidate any downstream citation of "view-orders E-6". The `[V1]` behavior itself is not lost: it is specified at `[L-S1-1]`, ruled by `[BR-2]`, and asserted by QA-SC-02 — it simply has no `[E-*]` ID on this page. Anyone reconciling this spec against the plan must map plan-E-6 → `[BR-2]`.

### 7.1 Scan and search

| ID | Situation | Expected behavior |
|---|---|---|
| **E-1** | Fully unrecognized barcode scanned | M2 opens with no error state and no crash; focus lands in `Order No` (`#unrecNo`); the scan persists `[DC-1]` with `resolution=unrecognized` and `[DC-4]`. The page behind stays exactly as it was. |
| **E-2** | M2 lookup matches; operator clicks `Match Tracking No` | Tracking is written onto that order's product line; modal closes; toast `✓ Tracking No {no} matched and registered`; rescanning the same barcode now resolves normally `[BR-27]`; auto-comment + Slack fire `[PD-16 · OWNER-PENDING]`. |
| **E-3** | M2 lookup returns no match | `#unrecNone` renders the no-match copy and a `Send to Missing Tracking List` button; opening M2b **carries the failed order number** and renders it in `#unrecCarriedNo`. |
| **E-4** | Operator has no order number at all | `No order number` opens M2b **without** a carried number; the carried-number line stays hidden. |
| **E-5** | M2b send succeeds | Pool entry created; green toast `✓ Sent to Missing Tracking List` / `PIC notified via #unrecognized-tracking · No refresh`; Slack posted; focus returns to the search input. |
| **E-6** | State 6 location entry names a location already holding a **different** SKU | Blocked with an inline error naming the occupying SKU `[BR-21]` `[PD-46 · OWNER-PENDING]`. Nothing saved, nothing persisted except the rejection. |
| **E-7** | One number matches multiple entities (same digits as a product order no. and a tracking no.) | Candidate selection list renders; nothing is auto-picked; the choice persists `[DC-3]` `[BR-3]`. |
| **E-8** | An inbound-request tracking number is scanned that also exists as a customer-order (outbound) tracking number | **State 6 wins** — inbound-request tracking has resolution precedence `[BR-45]` `[PD-8 · OWNER-PENDING]` `[PD-86 · OWNER-PENDING]`. The collision itself is not an error. |
| **E-9** | Return last-mile barcode scanned for an order whose status is `refunded` / `failed` / `completed` | **All three** route to State 4 with the return banner `[BR-12]`. `[DC-25].order_status_at_scan` records which one. |
| **E-10** | Empty search submitted | Complete no-op: no request, no state change, no toast, focus unchanged. |
| **E-11** | Immediately after an inbound | The input **keeps** its value `[L-S1-12]` **and** the content is selected `[L-S1-14]`, so the very next scan overwrites it with no keystroke in between. |
| **E-12** | Operator is typing in a comment / memo / barcode / shelf / location / modal field when an auto-refocus trigger fires | Auto-refocus **must not** fire. The typed field keeps focus and its content. Violating this writes scanned barcodes into comments and quantities `[BR-30]`. |
| **E-49** | A scan arrives while a modal is open | The modal owns the keyboard; the scan goes into the modal's focused field if one is focused, otherwise it is ignored. Auto-refocus to the page's search input must not steal it `[E-12]`. |
| **E-50** | Scanner emits a partial read (truncated digits) | Resolves to nothing → M2 opens `[E-1]`. The **raw** value is persisted in `[DC-1].raw_value` so truncation patterns are diagnosable per scanner device. |
| **E-66** | A second submit arrives while the previous resolution is still in flight | The second submit is **queued**, not dropped and not raced. Resolutions apply in submission order; the screen never renders a state derived from the older scan after the newer one `[BR-54]`. Both scans persist `[DC-1]`. |
| **E-68** | A *different* inbound request's tracking is scanned while State 6 has uncommitted receipts | No implicit save and no silent switch. A blocking prompt names the open request and its uncommitted count and offers `Save Partial Inbound` or `Stay here`; the scan is held until the operator chooses. Persists `[DC-1]` with the resolution and a `blocked_by_open_request` flag on `[DC-5]`. |
| **E-69** | A customer-order number is scanned while State 6 has uncommitted receipts | Same guard as `[E-68]`. Leaving State 6 never discards counted units silently. |
| **E-85** | An order line's SKU has been removed from the catalog | The line still renders with its stored SKU, name and qty (order lines are historical records, not catalog joins) and is fully workable; the missing catalog row is flagged as an upstream data defect, never hidden. |

### 7.2 Quantities, partials and damage

| ID | Situation | Expected behavior |
|---|---|---|
| **E-13** | Double-click on `Inbound`, `Inbound + Outbound`, `Outbound`, `Confirm Full Inbound`, `Confirm Restock`, `Save Partial Inbound`, `Save Qty Edit`, or `Confirm` (M1) | Exactly **one** server mutation. The second is an idempotent no-op that persists `[DC-13]`. This is the known production bug and must not be reproduced `[BR-34]` `[G-9]`. |
| **E-14** | Rescanning an already-INBOUNDED product barcode inside a customer order | **Amber warning toast** `Already inbounded — {SKU}`; no second inbound; **no send sound** `[BR-26]` `[PD-11 · OWNER-PENDING]`. |
| **E-15** | State 6 scan exceeds `Expected Qty` for a SKU | Warns **and counts**. Received may exceed Expected. `Confirm Full Inbound` stays disabled until resolved via M6 or M5 `[BR-19]` `[PD-12 · OWNER-PENDING]`. Persists `[DC-34]`. |
| **E-16** | State 6 scan of a product that is **not** in the request | Distinct **warning tone** `[G-3c]`, amber toast naming the scanned product, **nothing incremented anywhere**, suggested action shown (`this product is not on Inbound No. {n} — check the box`). Persists `[DC-33]`. |
| **E-17** | Rescanning the tracking of a **fully INBOUNDED** request | Opens the **read-only** State 6b completion view plus an info toast `Already inbounded — Inbound No. {n}` `[BR-25]` `[PD-15 · OWNER-PENDING]`. No mutation is possible from that view. |
| **E-18 = E-51** | One barcode is shared by two SKUs (a 1+1 set and its single) | The scan must **disambiguate** — a candidate list of the matching SKUs — never an arbitrary +1 on the first match. Registering a barcode that already belongs to another SKU is blocked upstream `[E-44]`. |
| **E-19** | `Bulk Inbound (Selected)` clicked with 0 rows selected | Button is disabled (`.btn-gray`); a forced invocation returns a red toast `Select at least one item` and persists nothing but the rejection. |
| **E-20** | `Inbound + Outbound All Remaining` clicked twice rapidly | One inbound batch, one outbound, **one label print**. The second click persists `[DC-13]`. |
| **E-21** | `Save Partial Inbound` on 620 of 800 | The 620 units enter Inventory **immediately**; the request becomes `PARTIAL 620/800`; State 0's Expected Inbound table shows the amber `PARTIAL 620/800` row `[BR-23]`. |
| **E-22** | Rescanning the same tracking after a partial save | State 6 resumes **from the saved totals** (620), never from zero; the remaining count is 180. |
| **E-23** | M6 edits expected 300 → 120 with 120 already received | Remaining recomputes to 0 and `Confirm Full Inbound` becomes **enabled** — but does **not** auto-confirm; a human presses it `[BR-22]` `[PD-84 · OWNER-PENDING]`. |
| **E-24** | M6 new expected qty **below** the already-received qty (e.g. 120 received, edit to 100) | **Hard block** with inline validation `New expected qty cannot be lower than the received qty (120)`. Nothing saved `[PD-14 · OWNER-PENDING]`. |
| **E-25** | M6 saved with no reason selected | `Save Qty Edit` blocked; the reason select is marked required; no event, no comment, no Slack. |
| **E-26** | M1 cancel with `No` selected | The restock qty **and location** fields are disabled **and cleared**; no stock is added; the reservation is released; `[DC-11].restock=false` with `restock_qty` and `restock_location` null. |
| **E-27** | M1 restock qty edited **below** the inbounded qty (partial damage) | **Allowed**, and the shortfall is **booked, not narrated**: the restocked units return to Available, and the remainder is auto-recorded in the same transaction as an inventory adjustment `ADJUST(−remainder)` carrying the same memo — `[DC-39]` with `origin=cancel_inbound_remainder` `[BR-57]` `[PD-49 · OWNER-PENDING]`. The memo is still dual-persisted `[L-M1]`, but it explains the adjustment rather than replacing it; units never leave the ledger with only a memo behind them `[G-8]`. |
| **E-52** | M1 restock qty edited **above** the inbounded qty | Rejected inline — restocking more than was taken creates phantom stock. |
| **E-28** | M3 with every line at qty 0 | Button reads `Confirm Restock (0)` and is **disabled**; nothing to restock. |
| **E-29** | M3 line with qty > 0 and empty location | `Confirm Restock` disabled until a location is filled; lines at 0 need no location `[L-S4-4]`. |
| **E-30** | M3 restock qty greater than the ordered qty | Rejected inline (over-restock block). |
| **E-31** | M4 `✎ Custom` carrier selected with an empty name | `🖨 Print` blocked with an inline error; the preview shows the placeholder `Carrier name` and must never print it. Empty size/qty fields are **omitted** from the label, never printed blank or as `0`. |
| **E-53** | State 6 `Received Qty` typed as a non-integer, negative, or non-numeric value | Rejected inline; the previous value is restored; tiles do not move; nothing persists. |
| **E-54** | State 6 `Received Qty` manually reduced below the number of scans already counted | **Allowed** — the operator is correcting a mis-scan. `[DC-32]` records `old → new` with `method=manual`, so the correction is distinguishable from the scans it overrides. |
| **E-67** | The scanner emits the same product barcode twice inside its own debounce window (double-Enter) | **Both are counted.** The counter is a physical tally and silent de-duplication would under-count genuine identical units. Both persist `[DC-31]`; correction is by editing `Received Qty` `[E-54]`. This is deliberately the opposite of `[E-13]`, which de-duplicates *button* submissions of one intent. |
| **E-80** | M6 sets the new expected qty to `0` | Rejected inline. Removing a line from a request is an Inbound Request operation, not a quantity edit `[BR-22]`. |
| **E-92** | `Received Qty` is corrected downward on a SKU that already reached its expected qty (row was `.row-done`) | **Allowed.** The row leaves `.row-done`, its status returns to `In progress · {n} remaining`, the SKU-done tile decrements, and `Confirm Full Inbound` re-disables `[BR-56]`. Persists `[DC-32]`. |
| **E-93** | M1 restock qty set to `0` while `Yes — restock` is selected | **Blocked** inline with `Select "No" to cancel without restocking`; `Confirm` stays disabled. `Yes + 0` and `No` would otherwise record the same physical decision two different ways — one with `restock=true, restock_qty=0`, one with `restock=false` — and no later reader could tell them apart `[BR-57]`. Nothing is persisted except the rejection. |
| **E-94** | M1 restock on a SKU with **no registered location** (JIT residual entering warehouse stock for the first time) | The location field renders empty with no default; `Confirm` stays **disabled** until a location is entered `[BR-58]`. Entering one assigns the SKU's location (`old=null → new`) inside the same `[DC-11]` transaction. A location occupied by a different SKU is rejected naming the occupier `[PD-46 · OWNER-PENDING]`. |
| **E-95** | A tracking number is scanned whose **inbound request was cancelled** (matching deactivated `[G-10]`) | It does **not** open State 6 and does not match any customer order: resolution falls through to rule 5 and the scan is treated as an unrecognized barcode — `[L-M2]` opens, and the operator routes it to the unrecognized pool `[L-M2b]` so a person decides what the arrived goods are. The cancelled request is **never** re-opened, re-activated or written to. Mirrors `inbound-request` `[E-96]` / `BR-34`; the two pages now describe one behaviour. **Owner-decided 2026-08-03.** |

### 7.3 Gating and state guards

| ID | Situation | Expected behavior |
|---|---|---|
| **E-32** | Two operators both see "last item" on the same order and both click `Inbound + Outbound` | The server serializes. One wins; the other receives a non-green toast and a refreshed row. **No double outbound, no double label print** `[BR-44]` `[PD-7 · OWNER-PENDING]`. |
| **E-33** | Two stations receive the same inbound request in State 6 simultaneously | Counts **merge server-side** — running totals, not last-write-wins. Tiles refresh on both stations without a page reload `[BR-44]`. |
| **E-34** | CS applies Hold while an operator has the order open with `Outbound` enabled (stale client) | The server rejects the outbound with an explicit hold error; red toast; the banner and the disabled button render on refresh of that view; persists `[DC-44]` with `reason=on_hold`. |
| **E-35** | Order is refunded or cancelled mid-flow, then outbound is attempted | Rejected with the reason named in the toast; persists `[DC-44]` with `reason=status_forbids_outbound` `[BR-9]`. |
| **E-36** | Another user posts a comment while the panel is open | The count and the panel update without a page refresh (poll or push — transport is a developer decision) `[BR-31]`. |
| **E-46** | `Confirm Full Inbound` pressed while a received SKU has no location | Button is disabled; a forced invocation is rejected server-side and persists `[DC-45]` with `reason=missing_location` `[BR-20]`. |
| **E-55** | `Cancel Inbound` attempted on a line of an **outbounded** order | Button is `.btn-gray` and inert; a forced request is rejected with `Cancel Outbound first` and persists `[DC-44]` with `reason=line_locked_after_outbound` `[BR-10]`. |
| **E-56** | `Cancel Outbound` attempted on an order that has already shipped/completed | Rejected with a red toast naming the current status; no rollback `[PD-6 · OWNER-PENDING]`. |
| **E-57** | A held order's last line is inbounded via bulk | Inbound completes; **no** outbound; **no** send sound; the suppression persists `[DC-10]` `[BR-7]`. |
| **E-72** | A bulk inbound in which one line fails mid-batch | The successful lines stay inbounded and are **not** rolled back; the toast reports the batch as **partial** and names the failing line(s); `[DC-7].failed_line_ids[]` records them. An unqualified success toast over a partial batch is forbidden `[BR-55]`. |
| **E-79** | An inbound request with **zero** SKU lines is opened in State 6 | Tiles render 0/0/0 and `SKU 0 SKUs (0 done)`; `Confirm Full Inbound` stays disabled with `reason=no_lines`; `Save Partial Inbound` is also disabled. An empty request can never be confirmed `[DC-45]`. |
| **E-81** | M6 is open when another user edits the same request line | On save the version check fails: red toast, the modal reloads with the current values, nothing is written `[PD-6 · OWNER-PENDING]`. |
| **E-82** | Legacy data already violates the 1:1 SKU↔location rule (two SKUs on one location) | The page **displays** the data as it is and does not auto-fix it, but any *new* assignment to that location is blocked `[E-6]`. The violation is reported to Inventory as a data-quality finding, never silently corrected `[BR-21]`. |
| **E-84** | An Expected Inbound row is clicked for a request that became `INBOUNDED` after the page rendered | The read-only 6b view opens with the info toast of `[E-17]`; the stale row is removed from the badge table on the next render. No mutation is possible. |
| **E-86** | An order in `pending` status is scanned and fully inbounded | `Outbound` enables — `pending` is an allowed source status `[BR-9]`. The status transition recorded is `pending → prepare shipment` `[DC-9]`. |
| **E-87** | A return barcode is scanned for an order that was **never outbounded** | State 4 still opens (detection is by scan, not by status `[BR-12]`), and `[DC-25].was_outbounded=false` is recorded so the impossible-looking case is visible in data. Restock is allowed; the anomaly is reported, not blocked. |
| **E-88** | An M3 return line's SKU has neither existing warehouse stock nor a JIT origin | Its `Location` renders as the amber `required` field like any new SKU; the qty>0 location gate applies unchanged `[L-S4-4]`. |
| **E-90** | Unsaved text is left in a `.bcin`, shelf, or location field when the state changes, **or** a station's clock is skewed | Unsaved text is discarded silently (§5.9-9) — only saved values persist. Actor Log and feed ordering use the **server** timestamp, so a skewed station cannot reorder history `[L-S1-13]`. |

### 7.4 Network, printer and integration failures

| ID | Situation | Expected behavior |
|---|---|---|
| **E-37** | Network drops mid-inbound (request never reached the server) | Red error toast; the line does **not** show INBOUNDED optimistically; retrying with the same idempotency key is safe. |
| **E-38** | Network drops **after** the server committed but before the response | The retry returns success-idempotent; the UI reconciles to the committed state; **no duplicate Actor Log row** and no duplicate `[DC-6]`. |
| **E-39** | Print agent offline or printer unreachable — any of the three surfaces | Explicit **red** toast naming the agent/printer; the inbound/outbound/restock is **not** rolled back; single-item auto-print failure never blocks the inbound; persists `[DC-29]` with the failure status `[BR-15]` `[PD-19 · OWNER-PENDING]`. |
| **E-40** | Slack delivery fails (mention, unrecognized send, qty-edit auto-comment, match-confirm) | The primary action still commits; the comment still exists; the failure persists `[DC-43]` and is retried `[BR-42]` `[PD-4 · OWNER-PENDING]`. The operator is not blocked and is not shown a red toast for a notification failure alone. |
| **E-41** | Browser autoplay policy blocks audio before the first user gesture | The action still processes; sound is enhancement only. No error is shown. |
| **E-48** | Toast burst during rapid continuous scanning | Toasts must remain readable (stacking or single-slot replacement — developer decision) and must never block the input or delay the next scan. The send sound must not overlap into distortion. |
| **E-58** | The local print agent is reachable but the job silently never prints (no error returned) | The job stays `pending` and is surfaced as such in `[DC-29]`; a timeout converts it to a failure with a red toast. Silence is never treated as success. |
| **E-70** | The session expires or the auth token becomes invalid mid-action | The action fails with an explicit re-authentication prompt; **nothing is silently dropped and nothing is optimistically applied**; the rejection persists `[DC-44]` with `reason=session_expired`. After re-auth the operator resubmits with the same idempotency key, so a commit that did land is not duplicated. |
| **E-71** | The browser tab is backgrounded while a bulk batch runs | The batch completes server-side regardless of tab visibility. On return the UI reconciles from the server, shows the batch result (including a partial result `[E-72]`), and does not re-issue the batch. |
| **E-91** | The print agent reports success but routed the job to a different printer | `[DC-29].printer_id` records the device that actually accepted the job, so a mis-routed label is discoverable. The UI reports success — it cannot know better — but the mismatch between the requested and the reported printer is an alertable condition for operations. |

### 7.5 Empty states, data integrity and boundaries

| ID | Situation | Expected behavior |
|---|---|---|
| **E-42** | State 0 with zero open inbound requests | The badge renders `▸ Expected Inbound 0`; expanding shows `No open inbound requests`. The badge is **never hidden**, so absence always means a render failure. |
| **E-43** | Comments hub with empty Mentions / Saved, or a search with no hits | Explicit empty-state copy per tab; search renders `No matching comments` `[G-7]` HUB-6. Never a blank dropdown. |
| **E-44** | A barcode entered in `[L-S1-20]` already belongs to a different SKU | Blocked with an error naming the conflicting SKU; persists `[DC-18]`. Entering the same barcode for the same SKU is a silent no-op. |
| **E-45** | Shelf or location re-entered with the identical value | The floating `Save` button never appears; pressing Enter is a no-op; **no phantom event** is persisted. |
| **E-47** | State 6 opened from the Expected Inbound badge for a request with **no** tracking number registered (destroyed-label path) | Allowed. The screen functions fully without tracking context; `[DC-5].tracking_no` is null and `entry_method=badge_row_click`. |
| **E-59** | An order line's product has no brand in the catalog | The name renders without the brand prefix and the line is still workable; this is an **upstream catalog data defect**, fixed in the product-name logic, never patched in this UI `[BR-36]` (§9.1). |
| **E-60** | An order arrives with 0 line items | The table renders empty with `Found 0 item(s) in this order · Found 1 order(s)`; `Outbound` stays disabled — `[BR-9]` requires ≥1 line, so "all lines INBOUNDED" being vacuously true is not enough. |
| **E-61** | A single-item order that already has inbound history is scanned again | **No auto-print.** `[DC-30]` records `decision=skipped` with `has_inbound_history=true` `[BR-14]`. |
| **E-62** | A single-item order fulfilled entirely from Existing Inventory is scanned for the first time | **Auto-print fires** — existing inventory is not inbound history `[BR-14]`. `[DC-30]` records `existing_inventory_lines=1, has_inbound_history=false, decision=printed`. |
| **E-63** | An unrecognized-pool item has **no** tracking number (label destroyed) | **Decided — the case does not exist** (`[PD-66]` owner-decided 2026-08-03): either a tracking number or an order number is always present, so the identifier-required registration contract stands. Registration without an identifier is rejected by M2b validation; the rescan-resolves loop `[BR-27]` depends on is preserved. |
| **E-64** | The same tracking number is registered on two different inbound requests | Prevented upstream at Inbound Request save `[PD-82 · OWNER-PENDING]`; if it ever occurs, this page's resolution is non-deterministic and must fail loudly with a candidate list rather than pick one `[BR-45]`. |
| **E-65** | An operator opens a modal and closes it without confirming | Nothing persists (§5.9-5). The single exception is M2, whose opening persists `[DC-4]`. |
| **E-73** | A Comments-hub search matches more results than one page holds | Results are paged or virtualized and the header states the true total (`{n} results · newest first · click to open the order`, `[G-7]` HUB-5). The hub never silently truncates. Page size is a developer decision. |
| **E-74** | M2b sent with free text typed but **no** product chosen from the autocomplete | Send is blocked with an inline error — the pool row must carry a real SKU or the downstream suspected-order matching has nothing to work with. |
| **E-75** | M2b `Qty` set to 0, negative, or non-integer | Rejected inline; send blocked. |
| **E-76** | `🖨 Print Return Labels` reached with 0 products selected | The button is disabled and its label reads `🖨 Print Return Labels (0)`; M4 cannot be opened with an empty item table. |
| **E-77** | A very long Korean product name in the M4 preview / on the physical label | The preview wraps; the label template decides physical truncation. The **data** in `[DC-28].composed_content` is stored in full and is never truncated to fit `[G-6]`. |
| **E-78** | A State 6 `Location` value that does not parse as a location code | Rejected inline with a format error; nothing saved. The regex is a developer decision `[G-14]`. |
| **E-83** | The Expected Inbound badge count disagrees with the number of rows in the expanded table | Impossible by construction — badge and table read the **same** query result. If it occurs it is a render integrity failure and must be reported, not reconciled client-side. |
| **E-89** | Shelf saved with whitespace only | Trimmed to empty; treated as *clear the shelf*; persists `[DC-14]` with `shelf {old} → null` (or `[DC-15]` with `trigger=manual_clear`), never a whitespace value. |

---

## 8. QA Acceptance Criteria

### 8.0 How to run

**Target:** `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/view-orders/`

**Tags.** **[WF]** = executable against the live wireframe **today**, using only the selectors and strings written in the scenario, with no further instruction needed. **[ADMIN]** = asserts behavior a static mock cannot produce (persistence, server rejection, sound gating on disabled controls, real state transitions) and is deferred to the real admin. A third marker, **`— DEFERRED`**, means the scenario carries **no assertion** because it is blocked on an owner decision; it is counted in the totals but is never executed and never fails.

**Before filing any `[WF]` failure, read §2.3 *and* §2.4.** §2.3 lists demo limitations — artefacts of a static mock that are not bugs and never become bugs. §2.4 lists **wireframe defects** — real, logged faults where the spec states the corrected behavior and the page may not have been fixed yet. **As of 2026-08-03 there are zero expected failures: every `[WF]` scenario is expected to pass, so any `[WF]` failure is a genuine finding.** *(History: **QA-S6-07** — defect **WF-1**, the carrier clause in the State 6b banner — was the single spec-declared expected failure. The wireframe was fixed on 2026-08-03, the banner now reads `Received Date 07-26 14:02 · Carrier is not recorded`, and a full `[WF]` re-run on that date returned **136/136 PASS**. Should a §2.4 row ever return to an unfixed state, the rule is unchanged: that scenario's failure is the intended signal and is filed against the wireframe, never against this spec.)*

**Execution protocol for [WF] scenarios** (an agent can follow this literally):

1. **Switch state:** click the chrome-bar button whose exact text is the state label, e.g.
   `[...document.querySelectorAll('.wf-tab')].find(b => b.textContent === '1 · Scan Result (Last Item Remaining)').click()`.
   The active state is `document.querySelector('section.state.on')`; assert its `id`.
2. **Open a modal:** either click the chrome-bar button whose exact text is the `Modal: …` label, or click the in-page control the scenario names. An open modal is `.overlay.open`; assert by `id`.
3. **Close a modal:** click any `[data-close]` inside it, or click the `.overlay` element itself (backdrop). `Escape` is **not** wired.
4. **Reset between scenarios:** reload the page. On load, `#s0` is `on`, all overlays are closed, `#inexpTable` is `display:none`, `#scanfloat` has class `collapsed`, and all `.star` states return to their markup defaults.
5. **Scope every query to the active state** — the same class names exist in nine sections. Use `#s1 .bulkbar`, not `.bulkbar`. **States 1–5 contain two tables:** the product grid is `table.tbl` and the Actor Log is `table.logtbl`, and the log table puts its **header row inside `<tbody>`**. A bare `#sN tbody tr` therefore matches both tables and over-counts (State 2 returns 9 rows, not 4). Always address the product grid as `#sN table.tbl tbody tr`; count log rows as `#sN table.logtbl tbody tr` **having ≥ 1 `<td>`**. States 6 and 6b have one table each (`table.tbl`) and no log.
6. **Text assertions** are on `textContent` with **runs of whitespace collapsed on both sides** (`s.replace(/\s+/g,' ').trim()`). **exactly** means the two collapsed strings are equal — including `·`, `—`, `→`, `✓`, `⟲`, `⏸`, `📦`, `🖨`, `▸`, `▾` and all Korean characters. Byte-for-byte comparison of raw `textContent` is **not** a valid reading of this rule: any element with child nodes carries the source file's newlines and indentation, so a literal byte comparison fails on nearly every banner, note and counter even when the visible text is identical.
6b. **Strip the wireframe annotation chrome before every text comparison, and when locating a control by its text.** The page injects `<span class="dot">` markers inside buttons, `<th>`, `<td>`, banners and notes, and every modal `<header>` ends with `<button class="x">✕</button>`. Both land in `textContent` (`Inbound + Outbound8`, `Product Name18`, `Cancel Inbound — 100038120✕`). Normalize with: remove every `.dot` descendant, and inside a modal `<header>` remove the trailing `button.x`; then apply rule 6. This chrome is annotation, not asserted content — do **not** use `Hide annotations` to remove it (rule 8).
7. **Colour assertions** use `getComputedStyle(el).backgroundColor`; "transparent" is the literal string `rgba(0, 0, 0, 0)`.
7b. **"Visible" means `el.getClientRects().length > 0`.** `offsetParent !== null` is **not** a valid visibility test on this page: `#scanfloat`, `#unrecToast` and `#gtoast` are `position:fixed`, for which `offsetParent` is always null. "Not visible" means `getClientRects().length === 0` or the element is absent.
7c. **Named elements that scenarios refer to by role.** Modal footer = `.foot` (not `footer`, not `.mfoot`). Comments-hub mentions pane = `.tabpane[data-pane="mentions"]`; saved pane = `.tabpane[data-pane="saved"]`. Order-card = `.ordercard`; bulk bar = `.bulkbar`; result counter = `.cnt`.
8. **Do not** click `Hide annotations` (`#annoToggle`) unless a scenario says so — several assertions read legend text, which `body.no-anno` hides.
9. **Toast timing:** `#unrecToast` auto-hides after ~4,000 ms; `#gtoast` after ~2,600 ms; `.flsave`'s `✓ Saved` after ~900 ms. Assert inside those windows.

**Totals.** See §8.14 for the machine-verified counts and the coverage guarantee.

### 8.1 State 0 and the Expected Inbound badge

**QA-S0-01 [WF]** `[L-S0-1]` `[L-F7]`
Given the page is freshly loaded, Then `document.querySelector('section.state.on').id` is `s0`, the chrome tab `0 · Waiting (Before Scan)` has class `on`, the `#s0 h2` text is exactly `WMS - View Orders`, the first `#s0 .sub` is exactly `Search Orders`, and `#s0 .search-input input` has `value === ''` with placeholder exactly `Tracking No / Inbound Order No / Product Order No / Last-mile barcode — scan any number`.

**QA-S0-02 [ADMIN]** `[L-S0-1]` `[G-1]`
Given the admin's View Orders page is loaded, Then `document.activeElement` is the unified search input, with no click required.

**QA-S0-03 [WF]** `[L-S0-1]` `[BR-46]` — *negative*
Given `#s0` is active, Then `#s0 .seg` returns null (no segmented type-selector) and no element inside `#s0` has text containing `Matched field`.

**QA-S0-04 [WF]** `[L-F8]`
Given `#s0` is active, Then a dashed panel is present whose text contains exactly the strings `Waiting for scan` and `Scan a tracking/product barcode or type a number to switch to that order's screen instantly`, and `#s0 .ordercard` returns null (the placeholder and an order card are never shown together).

**QA-S0-05 [WF]** `[L-F4]`
Given `#s0` is active, Then a `button.btn-blue` with text exactly `🔍 Search` sits inside `#s0 .searchrow`.

**QA-S0-06 [WF]** `[L-S0-2]`
Given `#s0` is active, Then `#inexpToggle` is visible with text exactly `▸ Expected Inbound 4 — 2 with tracking · 1 Partial Inbound`, and `#inexpTable` has inline `display:none`.

**QA-S0-07 [WF]** `[L-S0-2]`
When I click `#inexpToggle`, Then `#inexpTable` becomes visible, `#inexpToggle` text begins with `▾`, and `#inexpTable tbody tr` has length 4 with first-cell values in this order: `202608020001`, `202607120001`, `202608020002`, `202608010004` — the two tracking-bearing rows first. When I click `#inexpToggle` again, Then `#inexpTable` returns to `display:none` and the text begins with `▸`.

**QA-S0-08 [WF]** `[L-S0-2]` `[G-5]` `[BR-4]`
Given `#inexpTable` is expanded, Then its header cells are exactly `Inbound No.`, `Sourcing Route`, `Supplier`, `Items`, `Tracking No`, `Status`; row 2 contains `.tag-wholesale` with text `WHOLESALE`, supplier `비엠유통`, and a `.tag-part` badge reading exactly `PARTIAL 620/800`; rows 3 and 4 render `—` in the `Tracking No` cell.

**QA-S0-09 [WF]** `[G-5]` — *negative*
Given `#inexpTable` is expanded, Then for every `.tag-smartbuy`, `.tag-jit`, `.tag-wholesale`, `.tag-partnership` element on the page, `getComputedStyle(el).backgroundColor === 'rgba(0, 0, 0, 0)'` — routes are black bold text, never coloured pills.

**QA-S0-10 [WF]** `[L-S0-2]` (see demo limitation **L-9**)
When I click the `.row-part` row inside `#inexpTable`, Then `document.querySelector('section.state.on').id` becomes `s6` and `#s0` no longer has class `on`. Do **not** assert the chrome tab here — the mock leaves `0 · Waiting (Before Scan)` highlighted.

**QA-S0-11 [WF]** `[L-S0-2]` `[G-12]`
Given `#inexpTable` is expanded, Then its footer paragraph text contains exactly `Rows with tracking sorted to top`, `Click a row = open its reconciliation screen (State 6) without scanning` and `Full list: Inbound Request → Request List`.

**QA-S0-12 [ADMIN]** `[E-42]` — *negative*
Given an account with zero open inbound requests, Then the badge still renders (`▸ Expected Inbound 0`) and expanding it shows `No open inbound requests`; it is never hidden.

**QA-S0-13 [ADMIN]** `[L-S0-2]` `[DC-5]`
When I click an Expected Inbound row, Then a `scan.entry_state6` event persists with `entry_method=badge_row_click`, the inbound no., `tracking_no=null`, the actor and a server timestamp.

**QA-S0-14 [ADMIN]** `[E-47]`
Given an inbound request with **no** registered tracking number, When I open it from the badge, Then State 6 renders and is fully operable, and `[DC-5].tracking_no` is null.

**QA-S0-15 [ADMIN]** `[E-83]` — *negative*
Given a seeded mismatch between the badge count and the row set, Then the page reports a render integrity failure and does **not** reconcile the two client-side; badge and table are proven to read one query.

**QA-S0-16 [ADMIN]** `[E-84]` — *negative*
Given a badge row for a request that reached `INBOUNDED` after render, When the row is clicked, Then the read-only 6b view opens with the info toast `Already inbounded — Inbound No. {n}` and no mutation control is offered.

### 8.2 Unified search, scan protocol and focus

**QA-SC-01 [ADMIN]** `[L-S1-1]` `[BR-1]`
Given a number registered as an inbound-request tracking number, When it is submitted, Then State 6 opens — never States 1–5 — and `[DC-1].resolution = inbound_request`.

**QA-SC-02 [ADMIN]** `[L-S1-1]` `[BR-2]`
When the value `[V1]8801051283860` is submitted, Then it resolves identically to `8801051283860`, and `[DC-1]` records `raw_value=[V1]8801051283860` and `normalized_value=8801051283860`.

**QA-SC-03 [ADMIN]** `[E-7]` `[BR-3]` — *negative*
Given one number matching two entities, When it is submitted, Then a candidate list renders, **nothing is auto-selected**, and no mutation occurs until a candidate is clicked; the click persists `[DC-3]` with `position_in_list`.

**QA-SC-04 [ADMIN]** `[E-9]` `[BR-12]`
Given three return parcels whose orders are `refunded`, `failed` and `completed` respectively, When each last-mile barcode is scanned, Then **all three** open State 4 with the `⟲ Customer Return Order` banner, and each persists `[DC-25].order_status_at_scan` with its real status.

**QA-SC-05 [ADMIN]** `[E-10]` — *negative*
When the search is submitted empty, Then no request is issued, no state changes, no toast appears, and focus does not move.

**QA-SC-06 [WF]** `[L-S1-12]`
Given tab `1 · Scan Result (Last Item Remaining)` is active, Then `#s1 .search-input input` has `value` exactly `10323775316153` — the value persists after the inbound that produced this state.

**QA-SC-07 [WF]** `[L-S1-12]`
Given each of tabs `1b`, `2`, `3`, `4`, `5`, `6`, Then the search input's value is non-empty in every one of them: `10323775317888`, `10323775316153`, `10323775316153`, `10322198837710`, `10324880021991`, `10325661220417` respectively.

**QA-SC-08 [WF]** `[L-S6b-2]` `[L-S1-12]`
Given tab `6b · Internal Inbound Complete` is active, Then the search input's `value` is empty and its placeholder is exactly `Scan a tracking barcode — continue with the next one` — the documented exception to value persistence.

**QA-SC-09 [ADMIN]** `[L-S1-14]` `[E-11]` `[G-1]`
After any inbound/outbound action, Then the search input is focused **and** its content is fully selected (`selectionStart === 0 && selectionEnd === value.length`), so a subsequent scan replaces it; no click was required.

**QA-SC-10 [ADMIN]** `[E-12]` `[BR-30]` — *negative*
Given the caret is inside the comment composer, When an auto-refocus trigger fires (page click elsewhere, background action completes), Then focus **stays** in the composer and the typed text is unchanged.

**QA-SC-11 [ADMIN]** `[E-49]` — *negative*
Given modal M6 is open with focus in `New Expected Qty`, When a barcode is scanned, Then the digits go to the focused modal field and the page's search input is **not** refocused.

**QA-SC-12 [ADMIN]** `[BR-31]` `[G-2]` — *negative*
For every action on this page (inbound, outbound, cancel, restock, confirm, save, print, comment post), Then no full-page reload occurs — no navigation entry is added and no `beforeunload` fires.

**QA-SC-13 [ADMIN]** `[E-50]`
Given a truncated scanner read, Then M2 opens and `[DC-1].raw_value` stores the truncated string verbatim for device diagnosis.

**QA-SC-14 [ADMIN]** `[E-66]` `[BR-54]`
Given a resolution request is deliberately delayed by 2 s, When a second barcode is submitted 200 ms later, Then both persist `[DC-1]`, the rendered state derives from the **second** scan, and the first result never overwrites it.

**QA-SC-15 [ADMIN]** `[E-68]` — *negative*
Given State 6 is open with uncommitted receipts, When a different request's tracking is scanned, Then a blocking prompt names the open request and its uncommitted count, offers `Save Partial Inbound` / `Stay here`, and **nothing is saved implicitly**.

**QA-SC-16 [ADMIN]** `[E-69]` — *negative*
Same as QA-SC-15 but with a customer-order number scanned; the guard behaves identically.

**QA-SC-17 [WF]** `[L-S1-1]`
Given every one of the nine states, Then the search input's placeholder is the same string in all of them except `#s6b` (see QA-SC-08), proving the input is a single unified control and not a per-state variant.

**QA-SC-18 [ADMIN]** `[DC-2]`
When a number is **typed** rather than scanned and submitted, Then `search.manual_query` persists with `typed=true`, the query and the result count.

### 8.3 States 1 / 1b — rows, buttons, columns

**QA-S1-01 [WF]** `[L-S1-5]` (highlight half only; see **L-8**)
Given `1 · Scan Result (Last Item Remaining)` is active, Then `#s1 table.tbl tbody tr.row-hit` has length exactly 1 and its SKU cell reads `100005104` (after rule 6b annotation-stripping — the raw `textContent` is `1000051045`); its `Inbound Status` badge is `.tag-pending` with text `PENDING`.

**QA-S1-02 [ADMIN]** `[L-S1-5]` (sort half)
When a product barcode resolves inside the open order, Then its row moves to index 0 of the table body and carries `row-hit`; a subsequent scan of a different line moves the class and the row.

**QA-S1-03 [WF]** `[L-S1-8]` `[BR-8]`
Given State 1, Then the `#s1 table.tbl tbody tr.row-hit` row's action button text is exactly `Inbound + Outbound` (rule 6b) and it has class `btn-green`.

**QA-S1-04 [WF]** `[L-S1b-21]` `[BR-8]`
Given tab `1b · Scan Result (Normal — 2 Remaining)` is active, Then `#s1b table.tbl tbody tr.row-hit` action button text is exactly `Inbound` (not `Inbound + Outbound`), and `#s1b .ordercard button` with text `Outbound` has class `btn-gray`.

**QA-S1-05 [WF]** `[L-S1b-21]`
Given State 1b, Then exactly 2 rows carry `.tag-pending` (`100005104`, `100038120`) — the "two remaining" condition that keeps the button as plain `Inbound`.

**QA-S1-06 [WF]** `[L-S1-9]` `[BR-47]`
Given State 1, Then `#s1 .bulkbar` contains buttons with texts exactly `Bulk Inbound (Selected)` and `Inbound + Outbound All Remaining`, and `#s1 .bulkbar .cnt` text is exactly `1 selected · Processing all triggers auto Outbound (Hold orders: Inbound only)`.

**QA-S1-07 [WF]** `[L-S1-9]`
Given State 1b, Then `#s1b .bulkbar .cnt` reads exactly `2 not yet inbounded — processing all triggers auto Outbound (Hold orders: Inbound only)`.

**QA-S1-08 [WF]** `[L-S1-9]` `[BR-47]`
Given every one of States 1, 1b, 2, 3, 4, 5, Then a `.bulkbar` exists in each — it is never hidden, only disabled.

**QA-S1-09 [WF]** `[L-S1-10]` `[BR-40]` — *negative*
Given every state, Then the `.ordercard` action button's text is exactly `Outbound` (or `✓ Outbounded` in State 3) after rule 6b stripping, and the string `Deleo` appears **0** times in `document.body.innerText` **after excluding every `.legend` subtree**. The exclusion is required, not a convenience: State 1's legend entry 10 documents the removal by name (`Label changed from "Outbound to Deleo Baroship" to "Outbound"`), so an unscoped sweep finds 1 hit in `#s1` and 0 everywhere else. The rule being asserted is that no *rendered UI control or data cell* names the carrier `[BR-40]`; the legend is documentation of that removal and must keep saying it.

**QA-S1-10 [WF]** `[L-S1-6]` `[BR-4]` `[BR-5]`
Given State 1, Then the four route badges present are `SMART BUY`, `JIT (Coupang)`, `WHOLESALE`, `PARTNERSHIP`; the only row whose `Inbound Status` is `PENDING` carries the `JIT (Coupang)` badge.

**QA-S1-11 [WF]** `[L-S1-6]` `[BR-4]` — *negative*
Given States 1, 1b, 2, 3, 4, 5, Then **no** row shows `PENDING` together with a `SMART BUY`, `WHOLESALE` or `PARTNERSHIP` badge — only JIT can be PENDING.

**QA-S1-12 [WF]** `[L-S1-7]` `[BR-38]`
Given State 1, Then in `#s1 table.tbl` the `Qty` cell's **`span`** showing `2` (row SKU `100038120`) has classes `qty qty-warn`, and every `Qty` cell's `span` showing `1` has class `qty` **without** `qty-warn`. The classes live on the `<span>` inside the `<td>` (`<td><span class="qty qty-warn">2</span></td>`); the `<td>` itself carries `class=""` or `class="anno"`, so asserting against the cell element fails on a correct page.

**QA-S1-13 [WF]** `[L-S1-17]` `[L-S1-6]` `[BR-39]`
Given each of States 1, 1b, 2, 3, 4, 5, Then that state's `table.tbl thead th` count is **14** and the header texts, in order, are: `` (checkbox), `SKU`, `Image`, `Product Name`, `Product Name KR`, `Size`, `Qty`, `Barcode`, `Inbound Order No`, `Tracking No`, `Inbound Status`, `Sourcing Route`, `Location`, `Actions` — identical in all six, **after rule 6b stripping** (State 1 carries annotation dots inside three of these headers, whose raw text reads `Product Name18`, `Sourcing Route6`, `Location17`).

**QA-S1-14 [WF]** `[L-S1-17]` `[BR-49]`
Given State 1, Then in `#s1 table.tbl tbody tr` the `.row-exist` row (SKU `100024743`) shows Location `A-03-2` while every non-warehouse row shows `–`.

**QA-S1-15 [WF]** `[L-S1-18]` `[G-6]` `[BR-36]`
Given State 1, Then in `#s1 table.tbl tbody tr` every `Product Name` cell begins with a `<b>` brand element (`COSRX`, `Dr.Jart+`, `The Face Shop`, `Medicube`) and every `Product Name KR` cell also begins with the same bold EN brand followed by the Korean name (e.g. `Dr.Jart+` + `포어레미디 리뉴잉 폼 클렌저`).

**QA-S1-16 [WF]** `[L-S1-20]`
Given States 1, 1b, 2 and 3, Then within `#sN table.tbl tbody` the row for SKU `100024743` renders `input.bcin` with placeholder exactly `Enter barcode` in the `Barcode` column, while rows with a known barcode render text beginning `✓ ` (e.g. `✓ 8801051283860`).

**QA-S1-17 [WF]** `[L-S1-2]` `[BR-51]`
Given State 1, When I set `#s1 .shelf input` value to `9` and dispatch an `input` event, Then a `button.flsave` becomes visible with text `Save`; When I press `Enter` in that field, Then the button text becomes `✓ Saved`, it gains class `ok`, and it is hidden again within ~1 s. **No page reload occurs.**

**QA-S1-18 [WF]** `[E-45]` — *negative*
Given State 1, When I set `#s1 .shelf input` to its existing value `3` and dispatch `input`, Then no `button.flsave` becomes visible.

**QA-S1-19 [WF]** `[L-S1-13]`
Given State 1, Then a `.logsec` headed exactly `Inbound / Outbound Log` renders with header cells `Time`, `Action`, `SKU`, `Qty`, `Worker`, `Memo`, **3 data rows** — counted as `#s1 table.logtbl tbody tr` having ≥ 1 `<td>`, because this table's header row also sits inside `<tbody>` and a bare row count returns 4 (rule 5) — and a row whose memo is exactly `1 box damaged — restocked, needs inspection`.

**QA-S1-20 [WF]** `[L-S1-13]` (see **L-4**) — *negative*
Given State 1b, Then `#s1b .logsec` returns null. **This documents demo limitation L-4** — the spec requires the log here, so the corresponding admin assertion is QA-S1-21, and this `[WF]` result must not be filed as a product bug.

**QA-S1-21 [ADMIN]** `[L-S1-13]`
Given the admin's State 1b equivalent, Then the Inbound / Outbound Log is present with the same six columns as States 1–5.

**QA-S1-22 [ADMIN]** `[DC-14]` `[BR-51]`
When a shelf value is saved, Then `order.shelf_assigned` persists with `order_id`, `shelf old → new`, `save_method`, actor and server timestamp, and the in-place `✓ Saved` chip is the confirmation (no top-right toast on success; a failure does raise the red top-right toast).

**QA-S1-23 [ADMIN]** `[BR-29]` `[DC-15]` `[PD-18 · OWNER-PENDING]`
When the order is outbounded, Then the shelf auto-clears and `order.shelf_cleared` persists with `shelf {old} → null` and `trigger=outbound`.

**QA-S1-24 [ADMIN]** `[E-89]`
When a shelf is saved with `"   "`, Then it is trimmed to empty, treated as a clear, and no whitespace value is ever persisted.

**QA-S1-25 [ADMIN]** `[E-19]` — *negative*
When `Bulk Inbound (Selected)` is invoked with 0 rows selected, Then no mutation occurs and a red toast `Select at least one item` appears.

**QA-S1-26 [ADMIN]** `[DC-6]`
When a row's `Inbound` is clicked, Then `item.inbounded` persists with order id, SKU, qty, actor, timestamp and `method=row_button`, and the line status moves `PENDING → INBOUNDED`.

**QA-S1-27 [ADMIN]** `[L-S1-8]` `[DC-6]` `[DC-8]` `[DC-9]` `[BR-6]` `[BR-34]`
When `Inbound + Outbound` is clicked on the last remaining line, Then `item.inbounded` **and** `order.outbounded` (with `trigger=combined_last_item`) **and** `order.status_changed` (`processing → prepare shipment`) all persist under one idempotency key.

**QA-S1-28 [ADMIN]** `[E-14]` `[BR-26]` `[PD-11 · OWNER-PENDING]` — *negative*
When an already-INBOUNDED product barcode is rescanned inside a customer order, Then an amber toast `Already inbounded — {SKU}` appears, no second `item.inbounded` persists, and **no send sound plays**.

**QA-S1-29 [ADMIN]** `[E-72]` `[DC-7]` `[BR-55]` — *negative*
Given a bulk inbound over 3 lines where line 2 fails server-side, Then lines 1 and 3 stay INBOUNDED (no rollback), the toast reports a **partial** result naming line 2, and `[DC-7].failed_line_ids[]` contains line 2.

**QA-S1-30 [ADMIN]** `[E-85]`
Given an order line whose SKU was deleted from the catalog, Then the line renders from the stored order data and remains fully workable; the missing catalog row is reported, not hidden.

### 8.4 States 2 / 3 — outbound and cancels

**QA-S2-01 [WF]** `[L-S2-1]`
Given tab `2 · All Inbounded` is active, Then all four `#s2 table.tbl tbody tr` show `.tag-inbounded` with text `INBOUNDED`, and the `.ordercard` button with text `Outbound` (rule 6b) has class `btn-green` (not `btn-gray`). The `table.tbl` scope is required — a bare `#s2 tbody tr` also matches the Actor Log and returns 9 (rule 5).

**QA-S2-02 [WF]** `[L-S2-1]` `[L-S1-9]`
Given State 2, Then both `#s2 .bulkbar button` elements have class `btn-gray` and `#s2 .bulkbar .cnt` reads exactly `Nothing left to bulk-process — all items inbounded`.

**QA-S2-03 [WF]** `[L-S2-2]`
Given State 2, When I click the first `#s2 table.tbl tbody tr` row's `Cancel Inbound` button (located by rule-6b-normalized text — its raw text is `Cancel Inbound2`), Then `#m-cancel` gains class `open` and its header text is exactly `Cancel Inbound — 100038120` (rule 6b removes the trailing `✕` close button). **No row state changes from the button alone.**

**QA-S2-04 [WF]** `[L-S2-2]` — *negative*
Given State 2 and `#m-cancel` open, When I click the footer `Close`, Then `#m-cancel` loses class `open` and the underlying table is byte-identical to before (no row changed status, no log row appeared).

**QA-S2-05 [ADMIN]** `[L-S2-1]` `[DC-8]` `[DC-9]` `[BR-9]`
When `Outbound` is clicked while enabled, Then `order.outbounded` persists with `trigger=manual` and the full SKU set, `order.status_changed` persists `processing → prepare shipment`, and State 3 renders in place with no reload.

**QA-S2-06 [ADMIN]** `[E-60]` `[BR-9]` — *negative*
Given an order with 0 line items, Then `Outbound` is disabled and the counter reads `Found 0 item(s) in this order · Found 1 order(s)`; a forced outbound is rejected with `[DC-44].reason=no_lines`.

**QA-S3-01 [WF]** `[L-S3-1]`
Given tab `3 · Outbound Complete` is active, Then the `.ordercard` button text is exactly `✓ Outbounded` with class `btn-gray` (rule 6b — its raw text is `✓ Outbounded1`), and the status pill text is exactly `Prepare Shipment` with class `st-prepare`.

**QA-S3-02 [WF]** `[L-S3-2]`
Given State 3, Then a `button.btn-red-line` whose rule-6b-normalized text is exactly `Cancel Outbound` is present on the `.ordercard` (its raw text is `Cancel Outbound2`); When I click it, Then a browser alert with text exactly `Status rollback: prepare shipment → processing` is raised (wireframe stand-in for the real transition).

**QA-S3-03 [WF]** `[L-S3-4]` `[BR-10]` — *negative*
Given State 3, Then **every** `#s3 table.tbl tbody tr` action button has rule-6b-normalized text `Cancel Inbound` (the first row's raw text is `Cancel Inbound4`) and class `btn-gray`; `#s3 table.tbl tbody .btn-red-line` returns an empty list.

**QA-S3-04 [WF]** `[L-S3-3]` `[G-2]`
Given State 3, Then a `.toast` element is present whose text contains exactly `✓ Outbound complete — Order 413865` and whose `small` sub-line is exactly `Status: prepare shipment`.

**QA-S3-05 [WF]** `[L-S3-1]` `[L-S1-13]`
Given State 3, Then the Actor Log's newest row has action `OUTBOUND`, SKU `All (4 SKU)` and qty `5`, and the log has **5 data rows** — `#s3 table.logtbl tbody tr` having ≥ 1 `<td>`; the bare row count is 6 because the header row sits inside `<tbody>` (rule 5).

**QA-S3-06 [ADMIN]** `[L-S3-2]` `[DC-12]` `[DC-9]` `[BR-11]`
When `Cancel Outbound` is confirmed, Then status persists `prepare shipment → processing`, **all line inbound states are unchanged**, and `order.outbound_cancelled` + `order.status_changed` persist.

**QA-S3-07 [ADMIN]** `[E-55]` `[DC-44]` — *negative*
When a line-level cancel is forced (API) on an outbounded order, Then the server rejects it with `Cancel Outbound first` and persists `order.mutation_rejected` with `reason=line_locked_after_outbound`.

**QA-S3-08 [ADMIN]** `[E-56]` `[PD-6 · OWNER-PENDING]` — *negative*
When `Cancel Outbound` is attempted on an order already `shipped`, Then it is rejected with a red toast naming the current status and nothing is rolled back.

**QA-S3-09 [ADMIN]** `[E-32]` `[BR-44]` `[PD-7 · OWNER-PENDING]` — *negative*
Given two sessions both showing the last-item state, When both click `Inbound + Outbound` within 200 ms, Then exactly one `order.outbounded` persists, exactly one label print is requested, and the loser sees a non-green toast with a refreshed row.

**QA-S3-10 [ADMIN]** `[E-13]` `[G-9]` `[DC-13]` — *negative*
When `Outbound` is double-clicked, Then exactly one mutation occurs and `idempotency.duplicate_rejected` persists for the second click with `original_event_id` and `arrival_delta_ms`.

**QA-S3-11 [ADMIN]** `[E-35]` `[DC-44]` — *negative*
When outbound is attempted on a `refunded` order, Then it is rejected, the toast names the reason, and `[DC-44].reason=status_forbids_outbound`.

**QA-S3-12 [ADMIN]** `[E-86]` `[BR-9]`
Given an order in `pending` status with every line INBOUNDED, Then `Outbound` is enabled and the recorded transition is `pending → prepare shipment`.

**QA-S3-13 [ADMIN]** `[BR-32]` — *negative*
When `Cancel Outbound` or `✓ Outbounded` is clicked, Then **no** send sound plays.

**QA-S3-14 [ADMIN]** `[E-70]` `[DC-44]` — *negative*
Given the session expired, When `Outbound` is clicked, Then an explicit re-authentication prompt appears, no optimistic state change is shown, and `[DC-44].reason=session_expired` persists; after re-auth, resubmitting with the same idempotency key produces exactly one outbound.

### 8.5 State 4 — customer return and M3

**QA-S4-01 [WF]** `[L-S4-1]`
Given tab `4 · Customer Return Mode` is active, Then `#s4 .retbanner` is present, its bold lead is exactly `⟲ Customer Return Order`, and its body text is exactly `A returned tracking barcode was scanned — Order 412990 · Tracking 10322198837710` **after rule 6b** (the banner carries a trailing `.dot`, so the raw text ends `… 10322198837710 1`).

**QA-S4-02 [WF]** `[L-S4-6]` `[BR-12]` — *negative*
Given State 4, Then the order-card status pill text is exactly `refunded`, and the token `returned` does **not** appear as a status value anywhere in `#s4` (the legend text may discuss it; assert against `.status` elements only).

**QA-S4-03 [WF]** `[L-S4-1]` `[L-F3]` — *negative*
Given State 4, Then `#s4 .ordercard` contains **no** button with text `Outbound` and **no** button with text `🖨 Print` — a returned order is never shipped or re-labelled from this screen.

**QA-S4-04 [WF]** `[L-S4-2]`
Given State 4, Then `#s4 .bulkbar` contains, in order, a `btn-gray` `Bulk Inbound (Selected)`, a `btn-gray` `Inbound + Outbound All Remaining`, and a `btn-green` button with text exactly `Restock Selected to Warehouse (3)`; the counter reads exactly `Opens the restock confirmation modal — confirm qty · location · memo per item, then process in bulk`.

**QA-S4-05 [WF]** `[L-S4-1]`
Given State 4, Then every `#s4 table.tbl tbody tr` action button text is exactly `Cancel Inbound → Add Stock` with class `btn-red-line`, and the result counter reads exactly `Found 3 item(s) in this order · Found 1 order(s)`.

**QA-S4-06 [WF]** `[L-S4-2]` `[L-M3]`
When I click `Restock Selected to Warehouse (3)`, Then `#m-restock` gains class `open` and its header text is exactly `Warehouse Restock — Order 412990` (rule 6b removes the trailing `✕`).

**QA-S4-07 [WF]** `[L-M3]` `[L-S4-3]`
Given `#m-restock` is open, Then its lead paragraph is exactly `Confirm the products, quantities, and locations to restock. Products with existing stock get their current location auto-filled. Restock qty defaults to 0 — enter only the qty actually returned (0 = excluded).`, the table has header cells `Product`, `Ordered Qty`, `Restock Qty`, `Location` and 3 body rows.

**QA-S4-08 [WF]** `[L-M3]` `[L-S4-3]` `[L-S4-4]` `[BR-13]`
Given `#m-restock` is open, Then the `Anua` row's `Restock Qty` input value is `0` and its `Location` input is empty with placeholder `required` inside a `.loc-need` wrapper; the other two rows' locations are `A-03-2` and `B-01-4`; the footer button text is exactly `Confirm Restock (2)`.

**QA-S4-09 [WF]** `[L-M3]`
Given `#m-restock` is open, Then the amber note contains exactly `Anua has restock qty 0 → excluded.` and `if qty > 0 with no location, confirm stays disabled`, and the blue note is exactly `On completion, Current Stocks quantities and locations update automatically.`

**QA-S4-10 [WF]** `[L-M3b]`
Given `#m-restock` is open, Then a `textarea.mtextarea` is present whose placeholder is exactly `Return reason · condition (visible damage etc.) · notes — also recorded in the order's Comments history and the inbound log`.

**QA-S4-11 [ADMIN]** `[E-29]` `[L-S4-4]` — *negative* (see **L-12**)
Given a line with restock qty `1` and an empty location, Then `Confirm Restock` is disabled; filling the location enables it.

**QA-S4-12 [ADMIN]** `[E-28]` — *negative*
Given every line at qty `0`, Then the button reads `Confirm Restock (0)` and is disabled.

**QA-S4-13 [ADMIN]** `[E-30]` — *negative*
Given a line with ordered qty `1` and restock qty `2`, Then the input is rejected inline and confirm is blocked.

**QA-S4-14 [ADMIN]** `[E-88]`
Given a return line whose SKU has neither existing stock nor a JIT origin, Then its Location renders as the amber `required` field and the qty>0 gate applies unchanged.

**QA-S4-15 [ADMIN]** `[DC-26]` `[DC-27]` `[DC-39]` `[PD-17 · OWNER-PENDING]`
When `Confirm Restock (2)` is confirmed, Then `return.restock_confirmed` persists **every** line including the qty-0 one, each with `{sku, ordered_qty, restock_qty, location_old, location_new}`; a separate `return.line_excluded` persists for the qty-0 line; `inventory.stock_applied` persists with `origin=return_restock`; and the memo persists into `[DC-26].memo` **and** as an order comment.

**QA-S4-16 [ADMIN]** `[DC-25]` `[BR-12]`
When a return barcode is scanned, Then `return.scan_detected` persists with `order_status_at_scan` set to the real status at that instant.

**QA-S4-17 [ADMIN]** `[E-87]` `[DC-25]`
Given a return barcode for an order that was never outbounded, Then State 4 still opens and `[DC-25].was_outbounded=false` is recorded; restock is allowed and the anomaly is reported, not blocked.

### 8.6 State 5 — hold

**QA-S5-01 [WF]** `[L-S5-1]`
Given tab `5 · Hold Order` is active, Then `#s5 .holdbanner` bold lead is exactly `⏸ Hold Shipment` and its body is exactly `CS team put this order on Hold per customer request (address change) — Order 414102 · Requested by Sara(CS) 07-13 09:20` **after rule 6b** (the banner carries a trailing `.dot`); the status pill text is exactly `On Hold` with class `st-hold`. The `07-13 09:20` fragment is quoted wireframe demo data, not spec prose, and is asserted verbatim.

**QA-S5-02 [WF]** `[L-S5-2]` — *negative*
Given State 5, Then the `.ordercard` button whose rule-6b-normalized text is `Outbound` (raw: `Outbound2`) has class `btn-gray`.

**QA-S5-03 [WF]** `[L-S5-3]`
Given State 5, Then `Bulk Inbound (Selected)` has class `btn-green-line` (enabled) while `Inbound + Outbound All Remaining` has class `btn-gray`, and `#s5 .bulkbar .cnt` reads exactly `Hold order — Inbound allowed, Outbound blocked (ship after Hold release)`.

**QA-S5-04 [WF]** `[L-S1-13]` `[L-S5-1]`
Given State 5, Then the Actor Log contains a row with action exactly `HOLD Applied`, worker exactly `Sara (CS)` and memo exactly `Customer address change request — shipment held`.

**QA-S5-05 [WF]** `[L-S5-2]` `[L-F3]`
Given State 5, Then a `🖨 Print` button **is** present on the order card (State 5 is a print surface; State 4 is not — cf. QA-S4-03).

**QA-S5-06 [WF]** `[L-S5-F]` `[BR-50]` — *negative*
Given every state, Then no `button` on the page has text `Hold Shipment` or `Release Hold` — this page never applies or releases a hold.

**QA-S5-07 [ADMIN]** `[L-S5-2]` `[E-34]` `[DC-44]` — *negative*
Given a stale client whose `Outbound` was enabled before CS applied the hold, When outbound is posted, Then the server rejects it with an explicit hold error, a red toast appears, and `order.mutation_rejected` persists with `reason=on_hold`.

**QA-S5-08 [ADMIN]** `[BR-32]` `[L-S5-2]` — *negative*
Given the disabled `Outbound` on a held order, When it is clicked, Then **no** send sound plays, no request is issued, and no state changes. *(In the wireframe the sound does fire — demo limitations **L-2** / **L-11**.)*

**QA-S5-09 [ADMIN]** `[E-57]` `[DC-10]` `[BR-7]`
When the last line of a held order is inbounded via bulk, Then the inbound commits, **no** outbound occurs, and `order.outbound_suppressed_hold` persists with the hold requester and reason.

**QA-S5-10 [ADMIN]** `[L-S5-1]` `[PD-20 · OWNER-PENDING]`
Given a hold applied with a free-text reason, Then that reason renders verbatim in the banner and is present on the persisted hold event read by this page.

### 8.7 States 6 / 6b and modals M5 / M6

**QA-S6-01 [WF]** `[L-S6-2]`
Given tab `6 · Internal Inbound (Inbound Request)` is active, Then `#s6 .intbanner .big` is exactly `📦 Internal Inbound — Inbound Request`, `.warnline` is exactly `Not a customer order · Goes into Inventory · No Outbound step`, and the `.kv` row contains `Inbound No. 202607120001`, `WHOLESALE`, `비엠유통`, `Requested by Dean · 07-12`, `Expected arrival 07-18`.

**QA-S6-02 [WF]** `[L-S6-2]` `[G-12]`
Given State 6, Then `#s6 .intbanner a` has text exactly `View in Inbound Request List →` and its `href` ends with `../inbound-request/index.html#reqlist`.

**QA-S6-03 [WF]** `[L-S6-3]`
Given State 6, Then `#s6 .tile` has length 4, reading `Expected Qty (Total)` = `800`, `Received (scanned)` = `620`, `Remaining` = `180`, `SKU` = `2 SKUs (1 done)`; the received tile has class `ok` and the remaining tile has class `warn`.

**QA-S6-04 [WF]** `[L-S6-4]`
Given State 6, Then `#s6 .scannote` text is exactly `Now scan product barcodes — each scan adds +1 to that product's received qty (continuous scanning · cursor auto-return · warning sound for products not in the request)` **after rule 6b** (the note opens with a `.dot`, so its raw text begins `4 Now scan…`).

**QA-S6-05 [WF]** `[L-S6-5]`
Given State 6, Then `#s6 table.tbl thead th` reads exactly `SKU No.`, `Brand`, `Product Name`, `Expected Qty`, `Received Qty`, `Location`, `Status` **after rule 6b** (raw: `Expected Qty9`, `Received Qty6`, `Location7`); `#s6 table.tbl tbody tr` row 1 has class `row-done` with a `.tag-done` badge `✓ INBOUNDED`; row 2 has class `row-part` with a `.tag-part` badge `In progress · 180 remaining`.

**QA-S6-06 [WF]** `[L-S6-5]` `[BR-24]` **WF-1** — *negative*
Given States 6 and 6b, Then no `th` and no `label` in `#s6` or `#s6b` has text containing `Carrier`, and no input in either state is a carrier field.

**QA-S6-07 [WF]** `[L-S6b-1]` `[BR-24]` **WF-1 (fixed 2026-08-03)** — *negative*
Given State 6b, Then `#s6b .donebanner` must **NOT** contain the string `Carrier recorded automatically`. **This assertion passes** — the banner reads `Received Date 07-26 14:02 · Carrier is not recorded` since the WF-1 fix of 2026-08-03. *(History: until that fix this was the document's one spec-declared expected failure; a failure here is now a genuine regression of the wireframe, not an expected signal.)*

**QA-S6-08 [WF]** `[L-S6-8]`
Given State 6, Then the primary button's text is exactly `Confirm Full Inbound (180 remaining)` with class `btn-gray`, and a sibling button with text exactly `Save Partial Inbound` has class `btn-line`.

**QA-S6-09 [WF]** `[L-S6-F]` `[BR-24]`
Given State 6, Then the helper text beside those buttons reads exactly `On confirm: reflected in Inventory (Current Stocks) · Inbound Request List switches to INBOUNDED · Received Date recorded automatically` — with **no** mention of Carrier.

**QA-S6-10 [WF]** `[L-S6-6]` (see **L-13**) — *negative, documents demo limitation L-13*
Given State 6, When I set `#s6 table.tbl tbody tr:nth-child(2) input.qtyin` value to `130` and dispatch `input`, Then **no** visible `button.flsave` appears (`getClientRects().length > 0` count is `0`). **This documents demo limitation L-13** — the wireframe binds the floating-save handler only to `.shelf input` and `.locin`, never to `.qtyin`. The spec requires the pattern on `.qtyin` `[L-S6-6]` `[BR-51]`, so the positive assertion is QA-S6-45 `[ADMIN]`, and this `[WF]` result must not be filed as a product bug. Contrast QA-S6-11, the `.locin` twin, which is wired and passes.

**QA-S6-11 [WF]** `[L-S6-7]`
Given State 6, Then in `#s6 table.tbl tbody tr` row 1's `input.locin` value is `A-05-11` and row 2's is `B-02-07`; When I change row 2's value to `B-02-08` and dispatch `input`, Then a visible `button.flsave` appears (rule 7b); pressing `Enter` turns it into `✓ Saved`.

**QA-S6-12 [WF]** `[L-S6-9]` `[L-M6]` (see **L-10**)
Given State 6, When I click `document.querySelectorAll('#s6 button.qedit')[1]` (the row containing SKU `100052124`), Then `#m-qtyedit` gains class `open` with header text exactly `Edit Expected Qty — Inbound No. 202607120002` (rule 6b removes the trailing `✕`; the `…0002` vs State 6's `…0001` difference is intended demo renumbering — **L-5**), a `New Expected Qty` input valued `120`, helper text exactly `300 → 120 (−180)`, and a required `Reason` select whose three option labels are exactly `Damaged/defective — cannot accept`, `Supplier qty change`, `Other`.

**QA-S6-13 [WF]** `[L-M6]` `[BR-53]`
Given `#m-qtyedit` is open, Then its `select` has exactly 3 options and the third option's text is exactly `Other` — not `Other (memo)` `[G-11]`.

**QA-S6-14 [WF]** `[L-M6]`
Given `#m-qtyedit` is open, Then its memo `textarea` has value exactly `1 box damaged — 180 units rejected, returned to supplier`, its note contains, as case-sensitive substrings, `Confirm Full Inbound enabled`, `auto-posted as a Comment on this Inbound Request`, `the requester (@Dean) gets a Slack alert` and `The request list qty cell shows the edit history (300→120).` — that fourth fragment is **sentence-initial in the modal**, so it is quoted here with its capital `T` and closing period, and the `.foot` button text is exactly `Save Qty Edit`.

**QA-S6-15 [WF]** `[L-M5]`
Given State 6, When I click `Save Partial Inbound`, Then `#m-partial` opens with header exactly `Save Partial Inbound — Inbound No. 202607120001` (rule 6b removes the trailing `✕`), body lead exactly `Only 620 of the 800 expected units have been received (180 remaining).`, the per-SKU line exactly `1025 Dokdo Cleanser, 150ml — expected 300 / received 120 / remaining 180`, and a `Reason` select whose three option labels are exactly `Split shipment — remainder arriving later`, `Short delivery (needs supplier confirmation)`, `Partially damaged — will be returned to supplier`.

**QA-S6-16 [WF]** `[L-M5]`
Given `#m-partial` is open, Then its note contains exactly the strings `added to Inventory immediately`, `Partial Inbound (620/800)`, `3 stages: REQUESTED → PARTIAL → INBOUNDED` and `rescan the same tracking number to continue in State 6`; its memo placeholder is exactly `e.g. Remaining 180 units arriving Friday — also recorded in the request's Comments`; the footer button text is exactly `Save Partial Inbound`.

**QA-S6-17 [WF]** `[L-S6b-1]`
Given tab `6b · Internal Inbound Complete` is active, Then `#s6b .donebanner .big` is exactly `✓ Full Inbound Complete — Inbound No. 202607120001` and the `.kv` row contains exactly `Received 800 / 800 (2 SKUs)`, `Inventory updated (A-05-11 · B-02-07)` and `Inbound Request List switched to INBOUNDED`.

**QA-S6-18 [WF]** `[L-S6b-1]`
Given State 6b, Then both `#s6b table.tbl tbody tr` have class `row-done` with `✓ INBOUNDED` badges and Received Qty values `500` and `300`, and no input element exists anywhere in `#s6b table.tbl tbody` (the completed table is read-only).

**QA-S6-19 [WF]** `[L-S6b-2]`
Given State 6b, Then the `.note` block text is exactly `Cursor returns to the search box immediately on completion — scan the next tracking number with no refresh. This stock is visible in Inventory (Current Stocks) with its locations.` **after rule 6b** (the block opens with a `.dot`, so its raw text begins `2 Cursor returns…`).

**QA-S6-20 [WF]** `[L-S6-F]` — *negative*
Given `#s6` and `#s6b`, Then neither contains a button with text `Outbound`, nor a `.bulkbar`, nor an `.ordercard`, nor a button with text starting `🖨 Print Return Labels`.

**QA-S6-21 [WF]** `[G-2]`
Given State 6b, Then a `.toast` element is present containing exactly `✓ Inbound complete — Inbound No. 202607120001` with sub-line exactly `Inventory updated · Request list INBOUNDED · ready for the next tracking scan`.

**QA-S6-22 [ADMIN]** `[L-S6-4]` `[DC-31]`
When a product barcode belonging to the open request is scanned, Then that SKU's `Received Qty` increments by exactly 1, the tiles recompute without a reload, and `inbound_request.scan_counted` persists with `received {n} → {n+1}` and `method=scan`.

**QA-S6-23 [ADMIN]** `[E-16]` `[G-3c]` `[DC-33]` — *negative*
When a barcode **not** in the request is scanned, Then a distinct warning tone plays (not the send sound, not TTS), no counter anywhere changes, an amber toast names the scanned product, and `inbound_request.wrong_product_scanned` persists.

**QA-S6-24 [ADMIN]** `[E-15]` `[DC-34]` `[BR-19]` `[PD-12 · OWNER-PENDING]`
When a SKU is scanned beyond its expected quantity, Then the count **increases past expected**, a warning is shown, `Confirm Full Inbound` remains disabled, and `inbound_request.over_scan_warned` persists with the excess.

**QA-S6-25 [ADMIN]** `[E-67]` `[DC-31]`
When the scanner emits the same product barcode twice inside its debounce window, Then the count increases by **2** and two `inbound_request.scan_counted` events persist — the tally is physical and is never silently de-duplicated.

**QA-S6-26 [ADMIN]** `[E-46]` `[DC-45]` `[PD-13 · OWNER-PENDING]` — *negative*
Given a received SKU with no location, Then `Confirm Full Inbound` is disabled; a forced confirm is rejected and `inbound_request.confirm_blocked` persists with `reason=missing_location`.

**QA-S6-27 [ADMIN]** `[E-6]` `[BR-21]` `[PD-46 · OWNER-PENDING]` — *negative*
When a location already occupied by a different SKU is entered, Then it is rejected with an error naming the occupying SKU and nothing is saved.

**QA-S6-28 [ADMIN]** `[E-78]` — *negative*
When a `Location` value that does not parse as a location code is entered, Then it is rejected inline with a format error and nothing is saved.

**QA-S6-29 [ADMIN]** `[DC-16]`
When a `Location` value is saved, Then `inbound_request.location_assigned` persists with `location {old} → {new}` and `suggested=true|false` reflecting whether it was auto-suggested.

**QA-S6-30 [ADMIN]** `[E-23]` `[DC-35]` `[DC-23]` `[DC-20]` `[BR-22]` `[PD-84 · OWNER-PENDING]`
When M6 lowers expected 300 → 120 with 120 received, Then `Remaining` becomes 0, `Confirm Full Inbound` becomes **enabled but is not auto-pressed**, `inbound_request.expected_qty_edited` persists with old/new/reason/memo/editor, a `comment.auto_posted` (`source=system`) appears on Inbound Request `202607120001`, and a Slack message posts to `#fulfillment-admin-comments` (`C0BMGEWM5QA`) @mentioning the requester with old→new qty and reason.

**QA-S6-31 [ADMIN]** `[E-24]` `[PD-14 · OWNER-PENDING]` — *negative*
When M6 sets a new expected qty below the already-received qty, Then it is hard-blocked with inline validation `New expected qty cannot be lower than the received qty (120)` and nothing persists.

**QA-S6-32 [ADMIN]** `[E-25]` — *negative*
When `Save Qty Edit` is pressed with no reason selected, Then the save is blocked and no event, comment or Slack message is produced.

**QA-S6-33 [ADMIN]** `[E-80]` — *negative*
When M6 sets the new expected qty to `0`, Then it is rejected inline; removing a line is an Inbound Request operation.

**QA-S6-34 [ADMIN]** `[E-81]` `[PD-6 · OWNER-PENDING]` — *negative*
Given M6 is open and another user edits the same line, When `Save Qty Edit` is pressed, Then the version check fails, a red toast appears, the modal reloads with current values, and nothing is written.

**QA-S6-35 [ADMIN]** `[E-21]` `[E-22]` `[DC-36]` `[DC-38]` `[DC-39]` `[BR-23]`
When a partial inbound of 620/800 is saved, Then the 620 units appear in Inventory immediately, `inbound_request.partial_saved` and `inbound_request.status_changed` persist, the State 0 badge shows `PARTIAL 620/800`, and rescanning the same tracking resumes State 6 at 620 — not at zero.

**QA-S6-36 [ADMIN]** `[L-S6-8]` `[DC-37]` `[DC-38]` `[DC-39]` `[BR-18]` `[BR-20]` `[BR-24]`
When `Confirm Full Inbound` is pressed at an exact match with all locations set, Then stock lands in Inventory with locations, the request becomes `INBOUNDED`, `received_date` is auto-set, **no carrier value is written anywhere in `[DC-37]`**, and State 6b renders.

**QA-S6-37 [ADMIN]** `[E-17]` `[BR-25]` `[PD-15 · OWNER-PENDING]`
When the tracking of a fully INBOUNDED request is rescanned, Then the read-only 6b view opens with an info toast `Already inbounded — Inbound No. {n}`, and no mutation control is available.

**QA-S6-38 [ADMIN]** `[E-8]` `[G-10]` `[BR-17]`
Given an inbound request with three registered tracking numbers, When each is scanned in turn, Then all three open the same request's State 6 and receipts accumulate against one request.

**QA-S6-39 [ADMIN]** `[E-33]` `[BR-44]` `[PD-7 · OWNER-PENDING]`
Given two stations scanning the same request, When both scan concurrently, Then counts **merge** server-side (no lost updates) and both stations' tiles converge without a reload.

**QA-S6-40 [ADMIN]** `[E-54]` `[E-92]` `[DC-32]` `[BR-56]`
When `Received Qty` is manually reduced below the scanned total — including on a SKU already at its expected quantity — Then it is accepted, the row leaves `.row-done`, the SKU-done tile decrements, `Confirm Full Inbound` re-disables, and `inbound_request.received_qty_edited` persists with `method=manual` and `old → new`.

**QA-S6-41 [ADMIN]** `[E-53]` — *negative*
When `Received Qty` is set to a non-integer, a negative number or text, Then it is rejected inline, the previous value is restored, the tiles do not move, and nothing persists.

**QA-S6-42 [ADMIN]** `[E-79]` `[DC-45]` — *negative*
Given an inbound request with zero SKU lines, Then all tiles read 0, both `Confirm Full Inbound` and `Save Partial Inbound` are disabled, and a forced confirm persists `[DC-45].reason=no_lines`.

**QA-S6-43 [ADMIN]** `[BR-52]` `[PD-41 · OWNER-PENDING]` — *negative*
Given a PENDING inbound event, Then no confirm affordance exists on the Inventory screen; the only path that transitions it is View Orders State 6 / the Inbound Request lifecycle.

**QA-S6-44 [ADMIN]** `[E-82]` — *negative*
Given legacy data with two SKUs on one location, Then the page displays it unchanged, blocks any **new** assignment to that location, and reports the violation as a data-quality finding rather than auto-fixing it.

**QA-S6-45 [ADMIN]** `[L-S6-6]` `[BR-51]` `[DC-32]` (the `[WF]` half is QA-S6-10 / **L-13**)
Given the admin's State 6, When a row's `Received Qty` value is changed, Then the floating `Save` button appears beside that field exactly as it does for `Shelf` `[L-S1-2]` and `Location` `[L-S6-7]`; clicking it or pressing `Enter` saves, the button turns green reading `✓ Saved` and auto-hides, no page reload occurs, and `inbound_request.received_qty_edited` persists with `method=manual` and `old → new`. Re-entering the identical value shows no button and persists nothing `[E-45]`.

### 8.8 Modals M1, M2, M2b, M4

**QA-M1-01 [WF]** `[L-M1]`
When I open `#m-cancel` (chrome tab `Modal: Cancel Inbound`), Then the header text is exactly `Cancel Inbound — 100038120` (rule 6b removes the trailing `✕` close button; the raw text is `Cancel Inbound — 100038120✕`), the radio `input[name="restock"][value="yes"]` is checked, `#restockQty` has value `2`, and the note contains exactly `The SKU's Reserved Quantity → Available updates automatically.`

**QA-M1-02 [WF]** `[L-M1]`
Given `#m-cancel` is open, When I check `input[name="restock"][value="no"]` and dispatch `change`, Then `#restockQty.disabled === true` and `#restockQty.value === ''`; When I re-check `Yes — restock`, Then `#restockQty.disabled === false` and its value is restored to `2`.

**QA-M1-03 [WF]** `[L-M1]`
Given `#m-cancel` is open, Then the qty helper text is exactly `Default = qty that was inbounded (editable) · disabled when "No" is selected`, the memo textarea placeholder is exactly `Cancellation reason or notes — also recorded in the order's Comments history`, and the note names the use case `a JIT order placed by mistake when warehouse stock exists`.

**QA-M1-04 [WF]** `[L-M1]`
Given `#m-cancel` is open, Then `#m-cancel .foot` (rule 7c) has exactly two buttons with texts `Close` and `Confirm`; clicking the `.overlay` backdrop also closes it.

**QA-M1-10 [WF]** `[L-M1]` `[BR-58]`
Given `#m-cancel` is open, Then a field labelled exactly `3. Location (Optional)` sits between `2. Restock Qty` and `4. Memo (Optional)`, `#restockLoc` has value `B-01-4`, and its helper text is exactly `Default = the SKU's registered location (editable · updates the SKU's location) · required if the SKU has none · disabled when "No" is selected`. When I check `input[name="restock"][value="no"]` and dispatch `change`, Then `#restockLoc.disabled === true` and `#restockLoc.value === ''`; re-checking `Yes — restock` restores `B-01-4`.

**QA-M1-11 [ADMIN]** `[E-94]` `[BR-58]` — *negative*
Given a Cancel Inbound on a SKU with **no registered location**, When the modal opens with `Yes — restock` selected, Then the location field is empty with no default and `Confirm` is disabled; entering a location occupied by a different SKU is rejected naming the occupying SKU; entering a free location enables `Confirm`, and on confirm `[DC-11]` carries `restock_location old=null → new` in the same transaction as the stock delta.

**QA-M1-05 [ADMIN]** `[DC-11]` `[DC-39]`
When `Confirm` is pressed with restock `Yes` and qty `2`, Then `item.inbound_cancelled` persists with cancelled qty, `restock=true`, restock qty, restock location `old → new`, memo, actor and timestamp, plus the stock delta `Reserved → Available` old→new; `inventory.stock_applied` persists with `origin=cancel_inbound_restock`; the line returns to `PENDING`; the Actor Log gains `INBOUND Cancelled (Restocked)`; the memo also appears as an order comment `[DC-23]`.

**QA-M1-06 [ADMIN]** `[E-26]` — *negative*
When restock `No` is confirmed, Then no stock is added, the reservation is released, and `[DC-11].restock=false` with a null restock qty.

**QA-M1-07 [ADMIN]** `[E-27]` `[BR-57]` `[DC-39]` `[PD-49 · OWNER-PENDING]`
Given a line inbounded at qty `2`, When restock qty is reduced to `1` (partial damage) and confirmed, Then the cancel is accepted, `[DC-11].restock_qty` records `1`, **and** an `inventory.stock_applied` event persists with `origin=cancel_inbound_remainder` and `qty_delta = −1` carrying the same memo, written in the same transaction and under the same idempotency key as the cancel; the memo is additionally dual-persisted into the Actor Log and the order's comments. A run in which only `[DC-11]` appears — the memo standing in for the missing unit — is a failure.

**QA-M1-08 [ADMIN]** `[E-52]` — *negative*
When restock qty is set above the inbounded qty, Then it is rejected inline and confirm is blocked.

**QA-M1-09 [ADMIN]** `[E-93]` `[BR-57]` `[PD-49 · OWNER-PENDING]` — *negative*
Given `#m-cancel` with `Yes — restock` selected, When restock qty is set to `0`, Then `Confirm` is disabled with the inline message `Select "No" to cancel without restocking`, and no `item.inbound_cancelled` event is written; When `No` is selected instead, Then confirm is enabled and persists `[DC-11].restock=false` with a null restock qty — the two paths never both produce a zero-restock record.

**QA-M2-01 [WF]** `[L-M2]`
When I click the chrome tab `Modal: Unrecognized Barcode`, Then `#m-unrec` gains class `open`, its header is exactly `Barcode Not Recognized` (rule 6b removes the trailing `✕`), its lead is exactly `No order matches the scanned barcode 8809110223344.`, the instruction line is exactly `Enter the Coupang purchase order number to find matching products and register the tracking number on the spot.`, and `#unrecNo` has value `12101316464794`.

**QA-M2-02 [WF]** `[L-M2]`
Given `#m-unrec` is open, When I click `#unrecSearch` (`🔍 Look up`), Then `#unrecFound` becomes visible with exactly 2 `tbody tr`; the header cells are `Image`, `Product Name`, `Order`, `Qty`, `Tracking No`, ``; the first row's product name contains `Pore Remedy Renewing Foam Cleanser` with the Korean sub-line `포어레미디 리뉴잉 폼 클렌저`, order `414230`, qty `1`, tracking `10323100835644`; and `#unrecNone` stays hidden.

**QA-M2-03 [WF]** `[L-M2]` `[BR-27]`
Given `#unrecFound` is visible, Then the note under the table is exactly `Clicking match registers the tracking number on that line and closes this window — rescanning the same barcode is then recognized normally.`

**QA-M2-04 [WF]** `[L-M2]` `[E-2]` `[BR-28]` `[G-2]`
Given `#unrecFound` is visible, When I click the first row's `Match Tracking No` (`.trkmatch`), Then `#m-unrec` loses class `open` and `#unrecToast` becomes visible containing exactly `✓ Tracking No 10323100835644 matched and registered` with sub-line containing `Order 414230` and `rescanning the same barcode is now recognized`; it hides after ~4 s.

**QA-M2-05 [WF]** `[E-3]` — *negative*
Given `#m-unrec` is open, When I set `#unrecNo.value = '99999999999999'` and click `#unrecSearch`, Then `#unrecFound` is hidden and `#unrecNone` is visible containing exactly `No products match` and `possible typo or a number from another channel`.

**QA-M2-06 [WF]** `[E-3]`
Given `#unrecNone` is visible, When I click `#unrecToSend` (`Send to Missing Tracking List`), Then `#m-unrec` closes, `#m-unrec2` gains class `open`, `#unrecCarried` is visible and `#unrecCarriedNo` text is exactly `99999999999999`.

**QA-M2-07 [WF]** `[E-4]`
Given `#m-unrec` is open, When I click `#unrecNoNum` (`No order number`), Then `#m-unrec2` opens and `#unrecCarried` has `display:none` — no carried number.

**QA-M2-08 [WF]** `[L-M2]` `[BR-41]` — *negative*
Given any state and any modal, Then `document.querySelectorAll('input[type=file]').length === 0`, and no element text contains `Photo`, `사진`, `Upload` or `Camera` — photo capture is permanently deleted `[PD-63 · OWNER-PENDING]`.

**QA-M2-09 [WF]** `[L-M2]`
Given `#m-unrec` is open, Then `#m-unrec .foot` (rule 7c) holds exactly the buttons `No order number` and `Cancel`, and the demo hint line reads exactly `Demo: look up with this value = match-found path · change the value = no-match path` (wireframe scaffolding — the admin has no such line).

**QA-M2-10 [WF]** `[L-M2b]`
Given `#m-unrec2` is open, Then the header is exactly `Send to Missing Tracking List` (rule 6b removes the trailing `✕`), the lead is exactly `Barcode 8809110223344 — send it to the Missing Tracking List?`, the prompt is exactly `Enter the product name (English — autocomplete · Korean name shown alongside)`, the `.auto input` value is `glow ser`, there are 3 `.opt` options whose first has class `sel` and text `Beauty of Joseon — Glow Serum : Propolis + Niacinamide, 30ml` with the Korean sub-line `프로폴리스 나이아신아마이드 글로우 세럼`, the `Qty` input value is `1`, and a memo textarea is present with placeholder exactly `e.g. Box label damaged, looks like a 1+1 set — shown in the Missing Tracking List and the Slack alert`.

**QA-M2-11 [WF]** `[L-M2b]` `[G-7]`
Given `#m-unrec2` is open, Then its note is exactly `On send, the #unrecognized-tracking channel gets an "Unrecognized product added" alert (product name · barcode · qty · memo · order number if lookup failed) and @mentions every suspected PIC (once per person) so handlers are pushed, not polled → shown in the unrecognized pool on the Missing Tracking List page.`

**QA-M2-12 [WF]** `[L-M2b]` `[G-2]`
Given `#m-unrec2` is open, When I click `#unrec2Send`, Then `#gtoast` becomes visible containing exactly `✓ Sent to Missing Tracking List` and sub-line exactly `PIC notified via #unrecognized-tracking · No refresh`, `#m-unrec2` closes, and the toast hides after ~2.6 s. **No page reload occurs.**

**QA-M2-13 [ADMIN]** `[DC-40]`
When an order number is entered and `🔍 Look up` is pressed, Then `unrecognized.lookup_executed` persists with the barcode, the entered order no., `result` and `candidate_count`.

**QA-M2-14 [ADMIN]** `[DC-41]` `[DC-23]` `[PD-16 · OWNER-PENDING]`
When a match is confirmed in M2, Then `unrecognized.tracking_matched` persists with `tracking_no null → value` on the order line, `comment.auto_posted` (`source=system`) is written, and a Slack message routes to `#fulfillment-admin-comments` (`C0BMGEWM5QA`) @mentioning the registrant — **suppressed** when the resolver is the registrant (`mention_suppressed=true`).

**QA-M2-15 [ADMIN]** `[BR-27]`
After a successful match, When the original barcode is rescanned, Then it resolves normally to the order line and M2 does **not** open.

**QA-M2-16 [ADMIN]** `[E-5]` `[DC-42]` `[DC-43]` `[BR-48]`
When M2b's send is confirmed, Then `unrecognized.sent_to_pool` persists with barcode, chosen product SKU + EN name, qty, memo, carried failed order no. and registrant; `slack.dispatch_result` persists with `route=unrecognized_pool` and `channel=#unrecognized-tracking`; and the pool row is visible on the Unrecognized Tracking page.

**QA-M2-17 [ADMIN]** `[E-74]` — *negative*
When M2b is sent with free text typed but no autocomplete option chosen, Then send is blocked with an inline error and no pool row is created.

**QA-M2-18 [ADMIN]** `[E-75]` — *negative*
When M2b's `Qty` is `0`, negative, or non-integer, Then send is blocked inline.

**QA-M2-19 [ADMIN]** `[E-1]` `[DC-4]`
When a fully unrecognized barcode is scanned, Then M2 opens with focus in `#unrecNo`, the page behind is unchanged, and both `scan.submitted` (`resolution=unrecognized`) and `scan.unrecognized` persist.

**QA-M4-01 [WF]** `[L-M4]`
When I click the chrome tab `Modal: Return Label`, Then `#m-retlabel` opens with header exactly `Print Return Labels — 2 Selected Products (Supplier Return)` (rule 6b removes the trailing `✕`) and carrier chips in this order: `CJ대한통운`, `롯데택배`, `한진택배`, `우체국택배`, `로젠택배`, `✎ Custom`, with exactly one `.cchip.on` and it being `CJ대한통운`.

**QA-M4-02 [WF]** `[L-M4]` `[G-6]`
Given `#m-retlabel` is open, Then the item table's header cells are exactly `Product Name KR`, `Size (optional)`, `Qty (optional)`; row 1 shows bold `Dr.Jart+` + `포어레미디 리뉴잉 폼 클렌저` with size `150ml` and qty `1`; row 2 shows bold `Medicube` + `제로 모공 패드 2.0` with an empty size and qty `2`.

**QA-M4-03 [WF]** `[L-M4]`
Given `#m-retlabel` is open, Then `#rlPreviewCarrier` text is exactly `CJ대한통운`, the preview's first item line is exactly `Dr.Jart+ 포어레미디 리뉴잉 폼 클렌저 · 150ml · 1개` and its second is exactly `Medicube 제로 모공 패드 2.0 · 2개` — the empty size is **omitted**, not rendered blank.

**QA-M4-04 [WF]** `[L-M4]`
Given `#m-retlabel` is open, When I click `#cchipCustom` (`✎ Custom`), Then `#rlCustomRow` becomes visible, `document.activeElement === document.getElementById('rlCarrierCustom')`, `#rlPreviewCarrier` reads exactly `Carrier name`, and `.cchip.on` is now only `✎ Custom`; When I set `#rlCarrierCustom.value = '대신택배'` and dispatch `input`, Then `#rlPreviewCarrier` reads exactly `대신택배`.

**QA-M4-05 [WF]** `[L-M4]`
Given `#m-retlabel` is open, Then row 2's `Size` input is empty with placeholder exactly `omitted if empty`, and the note is exactly `Use case: during inbound scanning, return items to the supplier (e.g. Coupang seller) when wrong/damaged items are found. Printing puts carrier name + product name (KR) + size + qty on the label — size/qty omitted if empty; attach it to the return box.`

**QA-M4-06 [WF]** `[L-M4]`
Given `#m-retlabel` is open, Then `#m-retlabel .foot` (rule 7c) holds exactly the buttons `Cancel` and `🖨 Print`.

**QA-M4-07 [WF]** `[L-S1-22]`
Given each of States 1, 1b, 2, 3, Then a button with text exactly `🖨 Print Return Labels (2)` is present and clicking it opens `#m-retlabel`; Given States 4, 5, 6, 6b, Then no such button exists. *(negative half)*

**QA-M4-08 [ADMIN]** `[E-31]` — *negative*
Given `✎ Custom` selected and the carrier name empty, When `🖨 Print` is clicked, Then printing is blocked with an inline error, the placeholder `Carrier name` is never printed, and no print job is created.

**QA-M4-09 [ADMIN]** `[G-4]` `[DC-28]` `[DC-29]`
When `🖨 Print` is clicked in M4, Then the label reaches the printer queue with no new tab, no browser print dialog and no preview step, and `print.requested` (`surface=return_labels`, carrier, per-item Korean name/size/qty with omitted fields recorded as omitted) plus `print.job_result` persist.

**QA-M4-10 [ADMIN]** `[E-76]` — *negative*
When the return-label button is reached with 0 products selected, Then it is disabled, its label reads `🖨 Print Return Labels (0)`, and M4 cannot be opened.

**QA-M4-11 [ADMIN]** `[E-77]`
Given a Korean product name longer than the label line, Then `[DC-28].composed_content` stores the full name; only the physical label template truncates, never the stored data.

**QA-M4-12 [ADMIN]** `[E-91]`
Given the agent reports success but on a different device, Then `[DC-29].printer_id` records the device that accepted the job, making the mis-route discoverable.

### 8.9 Comments — panel, hub and search

**QA-C-01 [WF]** `[L-S1-19]`
Given State 1, Then `#cpanel1` is visible by default and contains exactly 2 `.c-item` comments; the first is by `Dean` with `@Yongwon` rendered inside `span.at`; the composer input placeholder is exactly `Write a comment — @name sends an automatic Slack alert (order no · text · time · author)` and its button text is exactly `Post`.

**QA-C-02 [WF]** `[L-S1-11]`
Given State 1, Then the order-card `💬 Comments` button carries a `.badge-n` reading `2`; When I click it, Then `#cpanel1` toggles to hidden and back to visible with no page reload.

**QA-C-03 [WF]** `[L-S1-3]`
Given State 1, When I click `button[data-open="inbox1"]`, Then `#inbox1` gains class `open` and shows tabs `@ Mentions` (with badge `3`) and `★ Saved`; the mentions pane header is exactly `Comments mentioning me · Click to open the order` with the action `Mark all read`. *(Canonical `[G-7]` HUB-1 / HUB-4 since the 2026-08-03 **WF-VO-1** fix — this page previously shipped `Comments where I'm tagged · Click to open the order page` / `Mark all as read`.)*

**QA-C-04 [WF]** `[L-S1-3]`
Given `#inbox1` is open, Then the mentions pane — `#inbox1 .tabpane[data-pane="mentions"]` (rule 7c) — has exactly 4 `.it` entries, 3 of them with class `unread`, referencing orders `413865`, `413712`, `413650`, `413501`.

**QA-C-05 [WF]** `[L-S1-3]`
Given `#inbox1` is open, When I click the `★ Saved` tab, Then the mentions pane hides, the saved pane — `#inbox1 .tabpane[data-pane="saved"]` — shows exactly 2 entries (orders `413712`, `412990`), both with `button.star.on`, and its header is exactly `Saved comments · Click to open the order` with the action `Unstar to remove from the list`. *(Canonical `[G-7]` HUB-2 / HUB-3 since the 2026-08-03 **WF-VO-1** fix.)*

**QA-C-06 [WF]** `[L-S1-3]`
Given `#inbox1` is open, When I set the `.csearch input` value to `restock` and dispatch `input`, Then the `.tabs` element is hidden, a results pane renders with header exactly `2 results · newest first · click to open the order`, the results are orders `413650` then `412990` (newest first), and every match is wrapped in `<mark>`. *(Canonical `[G-7]` HUB-5 since the 2026-08-03 **WF-VO-1** fix.)*

**QA-C-07 [WF]** `[L-S1-3]` `[E-43]` — *negative*
Given `#inbox1` is open, When I type `zzzznotfound` in the search box, Then the results pane renders exactly `No matching comments` — lower-case `c`. *(Canonical `[G-7]` HUB-6 since the 2026-08-03 **WF-VO-1** fix; this page previously shipped a capitalized `Comments`, the corpus's only instance.)*

**QA-C-08 [WF]** `[L-S1-3]`
Given a search is active in `#inbox1`, When I clear the search input and dispatch `input`, Then `.tabs` becomes visible again and the previously active tab's pane is shown.

**QA-C-09 [WF]** `[L-S1-19]`
Given State 1, When I click the first comment's `★`, Then it gains class `on`; clicking again removes it.

**QA-C-10 [WF]** `[L-S1-3]` `[G-7]`
Given tab `6 · Internal Inbound (Inbound Request)` is active, When I open `#inbox6`, Then the badge reads `2`, the entries reference **inbound requests** (`Inbound 202607120001`, `Inbound 202607100005`), and the pane header is `Comments mentioning me · Click to open the order` — the canonical `[G-7]` HUB-1 string, which is deliberately **not** re-worded per entity type (`[G-7]` reading rule 2), while the entries themselves reference inbound requests, proving they are a first-class commentable entity.

**QA-C-11 [WF]** `[L-S1-3]`
Given each of States 0, 1, 1b, 2, 3, 4, 5, Then a `.inboxdd` with a `.csearch input` whose placeholder is exactly `🔍 Search all comments — order no. · author · text` (`[G-7]` HUB-7) exists — the hub is present on every state, not only State 1.

**QA-C-12 [ADMIN]** `[DC-19]` `[DC-20]` `[DC-43]` `[G-7]`
When a comment containing `@Dean` is posted, Then `comment.posted` persists with the text and `mentioned_user_ids`, `comment.mention_notified` persists per mentioned user, `slack.dispatch_result` persists with `route=comment_mention`, and a Slack message posts to `#fulfillment-admin-comments` (`C0BMGEWM5QA`) with entity no., comment text, time, author, @mentioned user and a deep link.

**QA-C-13 [ADMIN]** `[BR-33]` `[PD-3 · OWNER-PENDING]` — *negative*
Given any posted comment, Then no edit and no delete affordance exists, and no API path mutates or removes a comment.

**QA-C-14 [ADMIN]** `[E-40]` `[BR-42]` `[PD-4 · OWNER-PENDING]` — *negative*
Given Slack is unreachable, When a mention comment is posted, Then the comment still commits, `slack.dispatch_result` persists with `status=failed`, a retry is scheduled, and the operator is neither blocked nor shown a red toast for the notification failure alone.

**QA-C-15 [ADMIN]** `[E-36]` `[BR-31]`
Given the comment panel is open, When another user posts on the same order, Then the count and panel update **without a page refresh**.

**QA-C-16 [ADMIN]** `[DC-21]` `[DC-22]` `[DC-24]` `[E-73]`
When a comment is starred, Then `comment.starred` persists; unstarring persists `comment.unstarred`; opening the hub persists `comment.read` for the entries shown and `Mark all read` persists `comment.mark_all_read`; running a hub search persists `comment.search_executed` with the query and hit count; and a result set larger than one page is paged with the true total in the header — never truncated silently.

**QA-C-17 [ADMIN]** `[PD-67 · OWNER-PENDING]`
Given a hub entry whose entity is an unrecognized-pool item, When it is clicked, Then the tracking-missing page opens focused on that pool row; if the item was already resolved, the **matched order** opens instead.

**QA-C-18 [ADMIN]** `[L-S1-3]` `[G-7]` **WF-VO-1** (the `[WF]` half is QA-C-03 / QA-C-05 / QA-C-06 / QA-C-07 / QA-C-10 / QA-C-11, which now assert the same canonical strings)
Given the admin's Comments hub on any screen, Then its user-visible strings are byte-identical to the `[G-7]` canonical set and identical on all eight screens: `Comments mentioning me · Click to open the order` (HUB-1) · `Saved comments · Click to open the order` (HUB-2) · `Unstar to remove from the list` (HUB-3) · `Mark all read` (HUB-4) · `{n} results · newest first · click to open the order` (HUB-5) · `No matching comments` (HUB-6) · `🔍 Search all comments — order no. · author · text` (HUB-7). *(Since `[G-7]` v1.2 published the set on 2026-08-03 this scenario has assertable literals, and the `[WF]` tier asserts the same values — the two tiers no longer diverge on this page.)* Also asserted unconditionally: a per-screen difference is a failure, whichever screen holds it.

### 8.10 Logs, feed and data capture

**QA-LG-01 [WF]** `[L-S1-16]`
Given State 1, Then `#scanfloat` exists with class `collapsed` and its header text contains `📡 Live Barcode Feed` with the count badge `4`; its `ul` and `footer` are hidden while collapsed.

**QA-LG-02 [WF]** `[L-S1-16]` `[BR-37]`
Given State 1, When I click `#scanfloat header`, Then the class `collapsed` is removed, the `.x` button text becomes `–`, the list shows exactly 4 `li` rows each with a worker, a barcode and a time, and the footer text is exactly `Max 20 on screen · full history in backend` with a button `Export by date`.

**QA-LG-03 [WF]** `[L-S1-16]` (see **L-3**) — *negative*
Given States 1b, 2, 3, 4, 5, 6, 6b, Then `#scanfloat` is not visible in any of them. **This documents demo limitation L-3**; the spec requires the feed on States 1–6b, asserted by QA-LG-04.

**QA-LG-04 [ADMIN]** `[L-S1-16]`
Given the admin, Then the Live Barcode Feed is present on States 1–6b, and in State 6 it shows the product scans counted against the open request.

**QA-LG-05 [ADMIN]** `[L-S1-16]` `[DC-1]` `[BR-37]`
Given 25 scans in a session, Then the panel shows the newest **20** and the backend query returns all 25.

**QA-LG-06 [ADMIN]** `[DC-47]` `[L-S1-16]`
When `Export by date` is used, Then `scan_feed.exported` persists with `actor_id`, `range_from`, `range_to`, `row_count`, `format` and `delivery`, and the exported rows match the requested range exactly.

**QA-LG-07 [ADMIN]** `[G-8]`
Given any Actor Log row is hidden or filtered in the UI, Then the underlying event remains queryable — the UI log is a projection and can never be the only copy.

**QA-LG-08 [ADMIN]** `[E-90]` `[L-S1-13]`
Given two stations with a 3-minute clock skew, Then the Actor Log and the feed order rows by **server** timestamp; a skewed client cannot reorder history.

**QA-LG-09 [ADMIN]** `[DC-46]` `[L-F5]` `§5.9-1` — *negative half*
When rows are checked and `Bulk Inbound (Selected)` is invoked, Then `bulk.action_invoked` persists with `selected_line_ids[]`, `visible_row_count` and any `excluded_line_ids[]` with reasons; **and no event of any kind persists for the checkbox toggles themselves** (declared NON-event).

**QA-LG-10 [ADMIN]** `[DC-7]` `[DC-6]`
When `Bulk Inbound (Selected)` completes over 3 lines, Then one `item.bulk_inbound_batch` parent persists carrying `child_event_ids[]`, and exactly 3 `item.inbounded` children persist with `method=bulk`.

### 8.11 Global protocols — toast, audio, print, no-refresh, layout

**QA-GL-01 [WF]** `[G-2]` `[L-S1-15]`
Given State 1, Then a `.toast` element is present containing exactly `✓ Inbound complete — 100040311` with sub-line exactly `No refresh · ready for the next scan`.

**QA-GL-02 [WF]** `[L-S1-15]` `[G-3a]` `[BR-32]` (see **L-11**)
Given the loaded page, let `src` be the concatenated `textContent` of every inline `<script>` element in the document. Then `src` contains all three of these substrings, verbatim:
`function sndOutbound()` · `if(/Outbound/.test(tx) && !/Cancel/.test(tx) && !/Outbounded/.test(tx))` · `b.addEventListener('click',sndOutbound)`.
The binding must be asserted against the **source text**, not by enumerating listeners: handlers added with `addEventListener` are not readable from page script, and the wireframe exposes no attribute, class or marker for them. This scenario proves only the **selection rule** — that the send sound is bound by outbound-class text and excluded on `Cancel` / `Outbounded`. It deliberately does **not** prove the gating rule: the wireframe also binds the greyed `Outbound` in States 1/5 and the greyed `Inbound + Outbound All Remaining` in States 2/3/4 (**L-2** / **L-11**), which the admin must not do — that is QA-GL-04 / QA-GL-05 `[ADMIN]`.

**QA-GL-03 [ADMIN]** `[G-2]` `[BR-31]`
For every confirming action on this page, Then a top-right toast appears (green success / red failure) naming what happened, and no page reload occurs. Shelf/location/qty micro-saves use the in-place `✓ Saved` chip instead on success `[BR-51]`.

**QA-GL-04 [ADMIN]** `[G-3a]` `[BR-32]` `[PD-2 · OWNER-PENDING]`
When `Outbound`, `Inbound + Outbound`, or `Inbound + Outbound All Remaining` is clicked **while enabled**, Then the rising send sweep plays exactly once per click.

**QA-GL-05 [ADMIN]** `[BR-32]` — *negative*
When `Cancel Outbound`, `✓ Outbounded`, `Inbound`, `Bulk Inbound (Selected)`, a disabled `Outbound`, a disabled `Inbound + Outbound All Remaining`, or any modal confirm is clicked, Then **no** send sound plays.

**QA-GL-06 [ADMIN]** `[G-3c]` — *negative*
When State 6's wrong-product tone plays, Then it is measurably distinct from the send sound (different frequency envelope) and is **not** speech; no TTS is ever produced on this page.

**QA-GL-07 [ADMIN]** `[E-41]` — *negative*
Given the AudioContext is blocked by autoplay policy, When an outbound-class button is clicked, Then the action still completes and no error is shown.

**QA-GL-08 [ADMIN]** `[G-4]` `[E-39]` `[BR-15]` — *negative*
Given the print agent is offline, When `🖨 Print` is clicked, Then a **red** toast names the agent/printer, `print.job_result` persists the failure, and the order's state is unchanged and not rolled back.

**QA-GL-09 [ADMIN]** `[E-58]` — *negative*
Given a print job that returns neither success nor error, Then it is held as `pending` in `[DC-29]` and converted to a failure with a red toast on timeout — silence is never reported as success.

**QA-GL-10 [ADMIN]** `[BR-14]` `[E-61]` `[E-62]` `[DC-30]`
Given a single-item order with no inbound history, When its barcode is scanned, Then the label prints with **zero clicks** and `print.auto_single_item_evaluated` records `decision=printed`; Given the same order after an inbound, Then a rescan records `decision=skipped, has_inbound_history=true`; Given a single-item order fulfilled entirely from Existing Inventory, Then the first scan records `existing_inventory_lines=1, has_inbound_history=false, decision=printed`.

**QA-GL-11 [WF]** `[L-S1-4]`
Given each of States 1, 1b, 2, 3, 4, 5 at a 1280 px-wide viewport, Then `document.body.scrollWidth <= document.documentElement.clientWidth` — the page body itself never scrolls horizontally. (The mock wraps each state in `.mockwrap{overflow-x:auto}` around a `.mock{min-width:1280px}`, so this asserts the wrapper absorbs nothing at 1280 px.)

**QA-GL-12 [ADMIN]** `[L-S1-4]` `[BR-39]`
Given the admin at a 1280 px viewport with no demo wrapper, Then all 14 columns, the bulk bar and every action button are visible without horizontal scrolling of the page body or of the table container.

**QA-GL-13 [WF]** `[L-F1]` `[L-F7]`
Given State 1, Then the nav renders `SkinSeoul`, the four section menus (`Operation AI ▾`, `Catalog Management ▾`, `OMS Center ▾`, `Site Management ▾`), the `💬 Comments` button, the user block `Yongwon Ryu` with avatar `Y`, and `Logout`; and `#s1 h2` is exactly `WMS - View Orders` with the section labels `Search Orders` and `Search Results`.

**QA-GL-14 [WF]** `[L-F2]`
Given State 1, Then the order card shows `Order ID: 413865` in blue, a `.status.st-processing` pill reading exactly `Processing`, and `Total Quantity: 5`; Given States 6 and 6b, Then `.ordercard` returns null.

### 8.12 Idempotency, concurrency and cross-cutting negatives

**QA-NG-01 [ADMIN]** `[G-9]` `[E-13]` `[DC-13]` `[BR-34]` — *negative*
For each of `Inbound`, `Inbound + Outbound`, `Outbound`, `Cancel Inbound → Confirm`, `Cancel Outbound`, `Confirm Restock`, `Confirm Full Inbound`, `Save Partial Inbound`, `Save Qty Edit`: a double click within 300 ms produces exactly one mutation and one `idempotency.duplicate_rejected`.

**QA-NG-02 [ADMIN]** `[E-20]` — *negative*
When `Inbound + Outbound All Remaining` is double-clicked, Then exactly one outbound and exactly one label print occur.

**QA-NG-03 [ADMIN]** `[E-37]` `[E-38]` — *negative*
Given the network drops before the server receives the inbound, Then a red toast appears and the line is **not** optimistically marked INBOUNDED; Given it drops after commit, Then the retry is success-idempotent and no duplicate log row or event appears.

**QA-NG-04 [ADMIN]** `[E-44]` `[DC-18]` — *negative*
When a barcode already bound to another SKU is entered in `[L-S1-20]`, Then it is blocked with an error naming the conflicting SKU and `product.barcode_register_rejected` persists with `reason=duplicate_other_sku`.

**QA-NG-05 [ADMIN]** `[DC-17]` `[BR-16]`
When a new barcode is registered on a barcode-less SKU, Then `product.barcode_registered` persists with `barcode null → value`, `source_screen=view-orders` and `source_state`, and the SKU resolves on the next scan.

**QA-NG-06 [ADMIN]** `[E-18]` `[E-51]` — *negative*
Given one barcode mapped to two SKUs, When it is scanned in State 6, Then a disambiguation list appears and **no** counter increments until a SKU is chosen.

**QA-NG-07 [ADMIN]** `[BR-43]` `[PD-6 · OWNER-PENDING]` — *negative*
Given an entity changed server-side after the page rendered, When a confirm is submitted, Then the server rejects it, a red toast appears, the affected view refreshes, and **no partial write** occurred.

**QA-NG-08 [WF]** `[BR-41]` `[BR-40]` `[BR-46]` — *negative, removed-feature sweep*
Across all nine states and seven modals: `input[type=file]` count is 0; `Deleo` appears 0 times in `document.body.innerText` **after excluding every `.legend` subtree** (State 1's legend entry 10 documents the rename by name — see QA-S1-09 for why the exclusion is part of the rule, not a loophole); `document.querySelector('.seg')` is null; no `button` text equals `Hold Shipment` or `Release Hold`.

**QA-NG-09 [WF]** — *negative, dead-link sweep*
Across the page, Then no anchor's `href` contains `inbound-receiving` (that page was deleted 2026-07-27 and would 404) and none contains `procurement-hub`.

**QA-NG-10 [WF]** `[BR-31]` — *negative*
Across all nine states and seven modals, Then no element has an `onclick` or `href` that triggers a full navigation of the current document, **except the cross-page deep links required by `[G-12]`** — today exactly one: `#s6 .intbanner a` with `href` ending `../inbound-request/index.html#reqlist`, which QA-S6-02 requires to exist. Without that carve-out this scenario and QA-S6-02 cannot both pass. The rule being asserted is that no *action* on this page navigates away: an inbound, outbound, cancel, save, confirm, print or comment post must never produce a document navigation `[BR-31]`.

**QA-NG-11 [ADMIN]** `[BR-35]` `[G-15]` `[PD-1 · OWNER-PENDING]`
Given the single admin role, Then every mutating action on this page succeeds regardless of user, and every one records the actor.

**QA-NG-12 [ADMIN]** `[E-64]` `[BR-45]` `[PD-82 · OWNER-PENDING]` — *negative*
Given (through a data defect) the same tracking number on two inbound requests, When it is scanned, Then resolution fails loudly with a candidate list; it never silently picks one request.

**QA-NG-13 [ADMIN]** `[E-65]` `§5.9-5` — *negative*
When M1, M3, M4, M5 or M6 is opened and closed without confirming, Then **no** event persists; when M2 is opened, `scan.unrecognized` persists — the single deliberate exception.

**QA-NG-14 [ADMIN]** `[E-48]` — *negative*
During rapid continuous scanning, Then toasts remain readable, never block the input and never delay the next scan, and the send sound never overlaps into distortion.

**QA-NG-15 [ADMIN]** `[E-71]`
Given the tab is backgrounded while a bulk batch runs, Then the batch completes server-side, the UI reconciles from the server on return (including a partial result), and the batch is not re-issued.

**QA-NG-16 [ADMIN]** `[DC-44]` — *negative*
For each `reason` value of `order.mutation_rejected` (`on_hold`, `status_forbids_outbound`, `already_outbounded`, `line_locked_after_outbound`, `stale_version`, `no_lines`, `session_expired`), Then a rejection scenario exists that produces exactly that value with a `server_state_snapshot` and no mutation.

### 8.13 Coverage completion — furniture, remaining events, remaining edge cases

This block exists so that **every** `[L-*]` key, **every** `[DC-*]` event and **every** `[E-*]` case has at least one keyed scenario.

**QA-CV-01 [ADMIN]** `[L-F1]` `[G-8]`
For every event in §5, Then `actor_id` equals the signed-in user shown in `[L-F1]`, and no event is ever written with a null actor.

**QA-CV-02 [WF]** `[L-F3]` `[G-4]` — *negative half*
Given States 1, 1b, 2, 3 and 5, Then a `🖨 Print` button is present on the order card; Given State 4, Then it is **absent**.

**QA-CV-03 [ADMIN]** `[L-F3]` `[DC-28]` `[DC-29]` `[G-4]`
When the order-card `🖨 Print` is clicked, Then the label reaches the printer queue with no dialog and no new tab, and `print.requested` persists with `surface=order_label` followed by `print.job_result`.

**QA-CV-04 [ADMIN]** `[L-F4]` `[E-10]` — *negative*
When `🔍 Search` is clicked with an empty input, Then nothing is requested, nothing changes, and no toast appears.

**QA-CV-05 [WF]** `[L-F5]`
Given State 1, Then `#s1 table.tbl` has a header `input[type=checkbox]` and one per `tbody tr`; the `.row-hit` row's checkbox is `checked` in the markup, and in `#s4 table.tbl` the header checkbox plus all three row checkboxes are `checked`.

**QA-CV-06 [WF]** `[L-F6]`
Given State 1, Then the counter under the table reads exactly `Found 4 item(s) in this order · Found 1 order(s)` and `#s1 table.tbl tbody tr` has exactly 4 rows; Given State 5, Then it reads exactly `Found 2 item(s) in this order · Found 1 order(s)` with 2 `#s5 table.tbl tbody tr` rows — the counter and the rendered product rows always agree. Count the product grid only; the Actor Log is a second table (rule 5).

**QA-CV-07 [WF]** `[L-S1-F]`
Given State 1, Then the legend's off-screen behavior paragraph contains, verbatim, all four rules: `single-item orders auto-print the label the moment the barcode is scanned`, `Existing Inventory stock does not count as inbound history`, `Confirming a match writes the tracking number directly onto that order's product line`, and `Scanning the tracking number of an Inbound Request (I) switches to the dedicated Internal Inbound screen`.

**QA-CV-08 [WF]** `[L-S5-F]` — *asserts shipped copy that the spec supersedes; see QA-CV-23*
Given State 5, Then the legend's off-screen paragraph is exactly `The Hold itself is applied via the "Hold Shipment" button in OMS/Order detail or Order Management (CS team). View Orders only displays the resulting status and blocks outbound.` **This is the string the page renders today and the assertion passes.** Its `or Order Management` clause is stale: Order Management removed every hold control on 2026-08-03 and forbids one existing (`order-management` `BR-10`). The corrected sentence is asserted `[ADMIN]` as QA-CV-23; this row is kept `[WF]` so the stale copy stays visible until the wireframe is edited (§9.5 CP-6), exactly as QA-S1-20 and QA-LG-03 keep L-4 and L-3 visible.

**QA-CV-09 [WF]** `[L-S6-F]` `[BR-24]`
Given State 6, Then the legend's off-screen paragraph contains `Received Date recorded automatically`, `automatic Carrier recording is not supported, confirmed 2026-08-03`, `Inbound Request List status auto-switches REQUESTED / PARTIAL → INBOUNDED`, and `this screen has no Outbound`.

**QA-CV-10 [WF]** `[L-S6-1]` `[G-10]`
Given State 6, Then the legend for dot 1 states that an inbound request `may have multiple tracking numbers registered (split shipments) — every registered number matches and enters this screen (2026-08-03)`.

**QA-CV-11 [WF]** `[L-S4-4]` `[L-S4-5]`
Given State 4, Then `#s4` contains, as verbatim substrings of the legend text (rule 6 collapse), both of these sentences:
(i) `If any item has restock qty > 0 but no location, the confirm button is disabled — assign a location to enable (see modal M3 — no on-screen dot)` — legend entry 4, the qty-without-location confirm block `[L-S4-4]`;
(ii) `Searchable by last-mile (return) barcode too — the unified search auto-detects return barcodes` — legend entry 5 `[L-S4-5]`.
And `#s4 .search-input input` has `value` exactly `10322198837710` — the return barcode that produced this state. Quote the sentences rather than indexing "legend entry N": the legend exposes no addressable index, and an unquoted paraphrase is not assertable (this is how QA-CV-07/08/09/10 are written).

**QA-CV-12 [WF]** `[L-S1-22]` `[L-S3-4]` — *negative half*
Given State 3, Then a `🖨 Print Return Labels (2)` button is present (supplier return is still available after outbound) **and** every `#s3 table.tbl tbody tr` action button is `btn-gray` with rule-6b-normalized text `Cancel Inbound` (the first row's raw text is `Cancel Inbound4`) — the two facts that make State 3 distinct.

**QA-CV-13 [ADMIN]** `[DC-2]` `[DC-3]`
When a number is typed and submitted, Then `search.manual_query` persists with `typed=true`; when a multi-match candidate is chosen, Then `search.multi_match_selected` persists the candidate list, the chosen entity and its position.

**QA-CV-14 [ADMIN]** `[DC-15]` `[E-89]`
When a shelf is cleared manually, Then `order.shelf_cleared` persists with `trigger=manual_clear`; when it is cleared by outbound, `trigger=outbound`.

**QA-CV-15 [ADMIN]** `[DC-23]`
For each `kind` of `comment.auto_posted` (`expected_qty_edit`, `match_confirmed`, `partial_saved`, `cancel_inbound_memo`, `return_restock_memo`), Then a scenario exists in which that system comment is written with `source=system` and a structured old/new payload.

**QA-CV-16 [ADMIN]** `[DC-45]`
For each `reason` of `inbound_request.confirm_blocked` (`qty_mismatch`, `missing_location`, `over_scan`, `no_lines`), Then a blocked confirm persists exactly that reason with `blocking_skus[]`.

**QA-CV-17 [ADMIN]** `[E-59]` `[BR-36]`
Given a catalog product with no brand, Then the line renders without a brand prefix and remains fully workable; the defect is reported upstream and is **not** patched in this UI.

**QA-CV-18 [WF]** `[G-5]` `[PD-80 · OWNER-PENDING]`
Given `#inexpTable` expanded and States 1–5, Then every route label renders as **bold text on a transparent background** (`getComputedStyle(el).backgroundColor === 'rgba(0, 0, 0, 0)'`), in its **canonical casing** — `SMART BUY`, `WHOLESALE` and `PARTNERSHIP` are upper-case because that is how the value is written, while `JIT (Coupang)` is mixed case and must stay mixed case. Do **not** assert `text === text.toUpperCase()`: the page applies no `text-transform`, and six `JIT (Coupang)` labels across States 1, 1b, 2, 3, 5 would fail it while being exactly what `[L-S1-6]` and QA-S1-10 require. **And** an `OTHER ({channel})` label, when present in the admin, must render with the same treatment (asserted in the admin as QA-CV-19).

**QA-CV-19 [ADMIN]** `[PD-80 · OWNER-PENDING]` `[G-5]`
Given an inbound request whose origin route is OTHER with channel `무신사`, Then View Orders renders `OTHER (무신사)` as black bold text in the Sourcing Route column and in the Expected Inbound table, and the channel text is carried into the Procurement Hub sheet.

**QA-CV-20 [WF]** — *negative, annotation sweep*
When I click `#annoToggle`, Then `body` gains class `no-anno`, every `.dot` and every `.legend` is hidden, and the button text becomes `Show annotations`. Clicking again restores them. **This control is wireframe chrome and must not exist in the admin** — asserted as QA-CV-21.

**QA-CV-21 [ADMIN]** — *negative*
Given the admin's View Orders page, Then no annotation dots, no legend block and no `Hide annotations` control exist.

**QA-CV-22 [ADMIN]** `[E-63]` `[PD-66]` *(formerly DEFERRED — un-deferred when the owner answered `[PD-66]` on 2026-08-03)*
The owner decided the no-identifier case does not exist: either a tracking number or an order number is always present, and the identifier-required registration contract stands. Assertion: Given the M2b registration form with both the tracking-number and order-number fields empty, Then registration is refused with a validation error, no pool row is created, and no event persists.

**QA-CV-23 [ADMIN]** `[L-S5-F]` `[BR-50]` (the `[WF]` half is QA-CV-08)
Given the admin's State 5, Then the hold-origin statement names **OMS / Order Detail only** and does **not** name Order Management as a place Hold is applied or released; and no apply-hold or release-hold control exists anywhere on this page. Order Management removed every hold control on 2026-08-03 (`order-management` `BR-10`, §3.8), so a sentence sending an operator there sends them to a button that does not exist.

### 8.14 Counts and coverage guarantee

| Metric | Value |
|---|---|
| Total scenarios | **279** |
| `[WF]` (runnable on the live wireframe today) | **136** |
| `[ADMIN]` (real-admin only) | **143** |
| — of which DEFERRED | **0** — QA-CV-22 was un-deferred when the owner answered `[PD-66]` (2026-08-03) |
| Explicitly tagged negative / failure-path scenarios | **92 (33.0 %)** — above the 25 % floor |

136 `[WF]` + 143 `[ADMIN]` = 279; the DEFERRED row is one of the 143, not a third tier. (v1.3 delta: **QA-M1-10 [WF]** and **QA-M1-11 [ADMIN, negative]** added for the owner-requested M1 restock location.)

**ID-collision correction, 2026-08-03.** The two v1.3 additions above were first issued as `QA-M1-06 [WF]` / `QA-M1-07 [ADMIN]`, which **duplicated the existing** `QA-M1-06 [ADMIN]` `[E-26]` and `QA-M1-07 [ADMIN]` `[E-27]`. The 279 / 136 / 143 totals were never wrong — they count scenario headers, and there were 279 headers — but the document held only **277 distinct IDs**, and that gap is what a machine census surfaced. Per the ID-immutability rule the two **pre-existing** scenarios keep `06` and `07`; the two v1.3 arrivals were renumbered to the next free values. They are `10` / `11`, not `08` / `09`, because `QA-M1-08` `[E-52]` and `QA-M1-09` `[E-93]` were already taken. The renumbered pair stays in place between QA-M1-04 and QA-M1-05 so the section's `[WF]`-block-then-`[ADMIN]`-block grouping is preserved; ID order and reading order diverge here by design. No assertion text changed. QA-M1 IDs are scoped to this document — `tracking-missing.md` has its own unrelated QA-M1-01…13.

**Coverage guarantee (machine-checked against this document):**

- All **69** `[L-*]` legend units are referenced by ≥ 1 scenario.
- All **47** `[DC-*]` events have ≥ 1 scenario with a Then-clause asserting persistence.
- All **93** `[E-*]` IDs are referenced by ≥ 1 scenario (`E-63` by the DEFERRED row).
- All **57** `[BR-*]` rules are referenced by ≥ 1 scenario.
- Counts above are machine-derived from this document, not asserted by hand.
- Every scenario carries at least one `[L-*]`, `[E-*]`, `[DC-*]`, `[BR-*]` or `[G-*]` key, except the two wireframe-chrome sweeps (QA-CV-20/21) and the dead-link sweep (QA-NG-09), which are deliberately key-free page-wide assertions.

---

## 9. Out of Scope & Open Questions

### 9.1 Explicitly out of scope for this screen

| Area | Owning screen / phase | Note |
|---|---|---|
| Applying or releasing **Hold** | OMS / Order Detail (CS) — `Change Status → on-hold` | This page displays the hold and blocks outbound; it offers no apply/release control `[L-S5-F]` `[BR-50]`. **Not Order Management** — that screen removed every hold control on 2026-08-03 and forbids one existing (`order-management` `BR-10`); the wireframe legend's stale `or Order Management` clause is §9.5 CP-6 |
| Changing an order's **status** directly, Reset Order, Clone Order, Change Tracking #, PIC edit, line-item add/delete | Order Detail | Those controls exist there and must not be duplicated here. Order Detail's `Cancel Outbound` is a deliberate parity control, not a duplicate `[PD-26 · OWNER-PENDING]` |
| **Creating** an inbound request, editing its route/supplier/unit cost, registering tracking numbers on it | Inbound Request | This page only *receives against* a request. The one exception is the **expected-qty edit**, which originates here in M6 by design `[G-11]` |
| Resolving items in the **unrecognized pool** (suspected-order matching, removal with reason, pool aging) | Unrecognized Tracking (`tracking-missing`) | This page *writes into* the pool (M2b) and can resolve a match on the spot (M2); pool management lives there |
| Confirming or adjusting a **PENDING inbound event from Inventory** | Inventory is display-only for PENDING | State 6 / the Inbound Request lifecycle is the sole confirm path `[BR-52]` `[PD-41 · OWNER-PENDING]` |
| **Sample assignment** (ON/OFF, periods, exactly-one-set rule) | Order Management `[G-13]` | Referenced only where it affects printed artifacts |
| **Label and invoice layout content** — what is physically printed on the DELEO A4 picking sheet and the YUN 4×6 carrier label, including the sample dual view | **Phase 3-1** (separate owner session, after Phase 3) | This spec defines print *behavior* `[G-4]` and *content fields* for M4's return label, never a layout |
| Inventory screens — location filter by line, stock audit mode, JIT residual stock display | Inventory (`stock-status`) `[G-14]` | This page is an *origin* of JIT residual stock via M1 cancel-restock; displaying it is Inventory's job |
| Ready-to-Outbound list, bulk outbound batches, picking lists | `ready-to-outbound` | Outbounding from this page removes the order from that list; the list itself is not specced here |
| **Procurement Hub** | excluded from this spec set entirely (owner decision, 2026-08-02) | No link, no reference, no dependency |
| Product-name / brand-prefix **catalog data fix** | Catalog Management (upstream) | Products missing a brand render without the prefix; the fix is in product-name logic, never a UI workaround `[E-59]` |
| Role and permission model | post-v1 owner decision `[G-15]` `[PD-1 · OWNER-PENDING]` | v1 is a single admin role |

### 9.2 Open questions — owner input required, no default assumed

| ID | Question | Why it is not decided here | Blocking |
|---|---|---|---|
| **OQ-1** `[PD-66]` `[E-63]` | **RESOLVED — OWNER-DECIDED 2026-08-03.** May an item enter the unrecognized pool with **no tracking number at all** (label destroyed)? Answer: **the case does not exist** — either a tracking number or an order number is always present; the identifier-required registration contract of M2b stands unchanged. | (was: an identifier-less pool item would break the rescan-resolves loop `[BR-27]` and the M2 flow depend on) | Nothing — QA-CV-22 is un-deferred |
| **OQ-2** | Should the **Live Barcode Feed export** be restricted, approved, or merely logged as a data-egress event? | The feed carries a full scan history including operator identity, so an export is personal-activity data leaving the system. No input document addresses export governance. The spec persists the export as `[DC-47]` and states no restriction, because inventing an approval flow would invent an owner for it. | `Export by date` implementation; retention policy |

Owner questions that **do** have a provisional default are **not** repeated here — they live in the PD register and are tagged inline in §3/§4/§5/§7 where the behavior appears. This page rests on **33** of them: `PD-1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 26, 29, 41, 46, 49, 63, 67, 80, 82, 84, 86`, plus `PD-66` (owner-decided 2026-08-03, above) — **33 PDs in total**. Reversing any one means editing only the sentences carrying its tag on this page.

> **Delta from spec v1.0:** v1.0 cited 30 PDs. The audit added `PD-26` (Order Detail's parity `Cancel Outbound`, cross-referenced at `[L-S3-2]`) and `PD-41` (Inventory is display-only for PENDING; State 6 is the sole confirm path, `[BR-52]`), both of which name View Orders in the PD register but were absent from the draft.

> **Delta from spec v1.1:** the cross-page remediation added `PD-49` — "restock qty edited **below** the released qty is allowed and the remainder is auto-recorded as `ADJUST(−remainder)` carrying the same memo". The register scopes it to Inventory's M4, but the physical fact is identical in this page's M1 `[L-M1]` `[BR-57]` `[E-27]`, and the two screens must not book the same reversal differently (§9.5 CP-1). **Citing it here extends its page list to View Orders**; if the owner answers PD-49 for Inventory only, this page's `[BR-57]` must be re-decided rather than silently inheriting the answer.

### 9.3 Decisions delegated to development (not owner questions)

Each has a stated default; the developer chooses the mechanism.

| Area | Item | Default / constraint stated by this spec |
|---|---|---|
| Idempotency `[G-9]` | Key format, TTL, client debounce interval, how a rejected duplicate surfaces | Must be double-click safe end-to-end; the rejection **must** persist `[DC-13]`. Note the deliberate asymmetry with `[E-67]`: button submissions de-duplicate, physical scans do not |
| Toasts `[G-2]` | Duration, stacking vs single-slot replacement, exact failure copy | Must never block the input or delay the next scan `[E-48]`; must name the cause on failure |
| Print `[G-4]` | Agent product (PrintNode-class), timeout, retry policy, job polling | Failure never gates goods movement `[BR-15]`; a silent job becomes a failure on timeout `[E-58]` |
| Audio `[G-3]` | Synth parameters, the exact separation between send tone and State 6 warning tone, AudioContext resume strategy | The two must be discriminable at 2 m over warehouse noise; blocked audio never blocks an action |
| Focus | Mechanism of the auto-refocus exclusion list `[E-12]` | The rule is normative; which elements suppress refocus is implementation |
| Live feed | Backend retention horizon beyond "unlimited", export file format and columns, date-range picker UI | On-screen cap is fixed at **20** `[BR-37]`; every export persists `[DC-47]` |
| Barcode master | EAN-13 checksum validation, lookup debounce, duplicate-error copy | Duplicate-across-SKU **must** be blocked `[E-44]` |
| Multi-match | Selection list layout | Must show enough context to choose; must never auto-pick `[BR-3]` |
| Comment search | Debounce, page size, index scope limits | Scope is fixed: all comments on all entities, newest first, matching entity no./author/text; never truncated silently `[E-73]` |
| Slack | Retry/backoff schedule, dead-letter handling | Failure never blocks; every attempt persists `[DC-43]` |
| Sync | Transport and latency for multi-operator live sync in State 6 and for comment freshness (poll vs push) | State 6 counts **must merge** server-side `[BR-44]` |
| Location | Location-code regex and the line-derivation parsing | 1:1 SKU↔location enforcement is normative `[BR-21]`; a non-parsing code is rejected `[E-78]` |
| Batching | Batch chunk size, per-line result payload shape | A partial batch must be reported as partial and must not roll back successful lines `[BR-55]` |
| Scan queueing | Queue depth and back-pressure strategy for in-flight submits | Scans are never dropped and never interleave `[BR-54]` |
| Event naming | Literal API/endpoint names | The canonical cross-page event names in §5 must be byte-identical `[G-8]` |

### 9.4 Features that must NOT exist on this page

Recorded explicitly so nobody re-implements them from a stale document. Each has a Decision Log row in §10.

1. **Search type toggle / segmented control** and the **"matched field" badge** — removed 2026-07-09 `[BR-46]`.
2. **Photo upload / photo capture** in M2, M2b, or on a product line — held 2026-07-21, **permanently deleted** 2026-08-03 `[BR-41]` `[PD-63 · OWNER-PENDING]`.
3. **Deleo Tracking No column** — removed from this page 2026-07-22; lives on Order Detail only `[BR-40]`.
4. **A separate internal-inbound page** (`inbound-receiving`) and any link to it — killed 2026-07-27, merged into States 6/6b. Such a link would 404.
5. **A dedicated "unrequested arrival" registration path** — rejected 2026-08-02; unrequested arrivals reuse the shared unrecognized pool `[BR-48]`.
6. **A duplicate "Existing Inventory" label under the product name** — removed 2026-07-09; the Sourcing Route badge plus the row tint carry it `[BR-49]`.
7. **A `Carrier` field or column** in State 6 / 6b or on the Inbound Request — auto carrier recording is **not supported** 2026-08-03 `[BR-24]`.
8. **A `returned` order status** — does not exist and may not be invented `[BR-12]`.
9. **Per-state column reduction** in the customer-order table `[BR-39]`.
10. **A browser print dialog, a print preview step, or a new-tab print** on any print surface `[G-4]`.
11. **Comment edit or comment delete** `[BR-33]`.
12. **Any page refresh after an action** `[BR-31]`.
13. **A confirm affordance for PENDING inbound events on Inventory** — State 6 is the sole confirm path `[BR-52]` `[PD-41 · OWNER-PENDING]`.
14. **An `Outbound`, bulk bar, order card, or return-label button on States 6 / 6b** `[L-S6-F]`.
15. **A `Hold Shipment` or `Release Hold` control** anywhere on this page `[L-S5-F]`.
16. **Annotation dots, the legend block, and the `Hide annotations` toggle** — wireframe chrome only.

### 9.5 Cross-page disagreements involving this page

Raised by the 2026-08-03 cross-page consistency pass over all eight specs plus `_global-rules.md`. Each row states **this page's position**, what it changed here, and where the remaining fix lands. None of them blocks implementation of this screen; all of them would produce two incompatible implementations if left unstated. Rows are `CP-n`, page-scoped and stable.

| ID | Disagreement | This page's position | Remaining fix (not on this page) |
|---|---|---|---|
| **CP-1** | **Cancel-Inbound restock had three incompatible contracts** — this page left the under-restock remainder to the memo, Order Detail hard-codes `restock=true` with no qty input, Inventory books `ADJUST(−remainder)`. | **Changed here.** This page now books the remainder as an inventory event `[BR-57]` `[E-27]` `[DC-39]` `origin=cancel_inbound_remainder`, matching Inventory `[PD-49 · OWNER-PENDING]`. `Yes + qty 0` is blocked `[E-93]`. | `order-detail` must either gain the Yes/No + qty controls or state in §3 that it always restocks the full line qty and why. All three specs must agree the server produces **one** reversal and **one** remainder adjustment per line. |
| **CP-2** | **`ready-to-outbound` writes a third line status `OUTBOUNDED`**; neither this page nor Order Detail has one, and Order Detail's rendering contract is exhaustive. | Outbound is **order-level only**. The line machine is exhaustively `PENDING ↔ INBOUNDED` `[L-S1b-21]`, which is why `Cancel Outbound` touches no line state `[BR-11]`. | `ready-to-outbound` `BR-22` / `DC-9` must drop the `line_status` transition — or, if the owner makes outbound line-level, this page and Order Detail both add `OUTBOUNDED` **and** its `Cancel Outbound` reversal. Do not implement RTO's write against this spec as it stands. |
| **CP-3** | **`OTHER (channel)` on order-facing rows** — `[G-5]` says the order-facing badge set is "exactly 4"; this page renders a fifth value, `ready-to-outbound` says Order Detail renders it, Order Detail says it never does. | **Declared here** as an explicit page delta on `[G-5]` with rationale `[L-S1-6]`: the label is a rendering pass-through of the route inherited from the Inbound Request `[BR-5]`, never a fifth selectable route. | `[G-5]` must state which surfaces may render `OTHER (channel)` on order-facing rows; then whichever of `ready-to-outbound` §1.4/§4.2 or `order-detail` `[L-4]` disagrees is corrected. `[PD-80 · OWNER-PENDING]`. |
| **CP-4** ✅ **RESOLVED 2026-08-03** | **Comments-hub copy was not byte-identical across the eight specs**, although all eight asserted it byte-exactly and all eight stated the hub is one control. This page held the minority form on all seven strings. | **Resolved at the right level.** `[G-7]` v1.2 published the canonical set HUB-1…HUB-7; all eight wireframes and all eight QA suites were moved to it in one commit (**WF-VO-1** applied here). `[WF]` and `[ADMIN]` now assert the same literals. | Closed. Any future hub-copy difference is a regression against `[G-7]`, not a new page defect. |
| **CP-5** | **`closing` uses `Cancelled` as an order status** in its verdict matrix, `BR-20`, `[E-5]` and PD-76's title. | The vocabulary is **exactly 8 statuses** and `cancelled` is not among them `[BR-12]` `[L-S4-6]` §9.4-8. Unchanged. | `closing` must render the underlying status plus a cancellation marker (Order Detail treats cancellation as an action, not a status) — or, if the owner makes it a 9th status, `BR-12` here and on Order Detail changes and Order Detail's status dropdown gains it. |
| **CP-6** | **Hold origin** — this page's legend names Order Management; `order-management` removed all hold controls on 2026-08-03 and forbids one existing. | **Changed here.** `[L-S5-F]` and §9.1 now say **OMS / Order Detail only**; the stale legend clause is asserted `[WF]` (QA-CV-08) and the corrected sentence `[ADMIN]` (QA-CV-23). | The wireframe legend paragraph is edited to drop `or Order Management`, after which QA-CV-08's quoted string is updated in the same pass. |
| **CP-7** | **Five shared concepts carry a different event name on every page** — idempotent duplicate suppressed, stock moved, comment search executed, Slack dispatch outcome, line received. The 10 **canonical** names are byte-identical everywhere; this is the tier below them. | **Stated, not silently claimed.** §5's preamble now marks this page's five names as page-scoped and not canonical, so nobody joins events across screens assuming identity. Names unchanged — renaming them here would only move the divergence. | `[G-8]` promotes one name per concept (or publishes a second "shared, non-canonical" list); all specs adopt it in one pass. Also unresolved: Order Detail declares comment-search a NON-event while three pages persist it — a `[G-8]` disagreement, not a naming one. |
| **CP-8** | **Deep-link path form** — `[G-12]` and some specs write `../{slug}/#anchor`; this page, `tracking-missing` and this page's `[WF]` QA write `../{slug}/index.html#anchor`. This page previously used **both** forms internally. | **Fixed here.** One form throughout: `../inbound-request/index.html#reqlist` in `[L-S0-2]`, `[L-S6-2]`, §6.2 and QA-S6-02 — the shipped `href` the `[WF]` assertion reads. | `[G-12]` fixes one form corpus-wide. If the directory form wins, the wireframe `href`, §3/§6.2 and QA-S6-02 change together — never the spec alone, or the `[WF]` assertion starts failing against a correct page. |
| **CP-9** | **What counts as a `[G-2]` confirming action** — this page says the confirmation always exists and may move position; `ready-to-outbound` says in-place feedback replaces it for a named class of actions. | Position delta only `[BR-51]`: the `✓ Saved` chip **is** the confirmation, failures still use the red top-right toast. Unchanged — it is a declared, dated delta. | `[G-2]` states the boundary once (state-changing actions always confirm; pure view-state changes — expand, tab, checkbox, modal open, Cancel — are not confirming actions), after which both pages cite it instead of each defining it. |
| **CP-10** | **A cancelled inbound request's tracking number** — this page used to say *every* registered number opens State 6; `inbound-request` v1.3 (PD-79) says cancellation deactivates matching so the number falls to the unrecognized pool. | **Resolved 2026-08-03 (owner): `inbound-request` is right.** `[G-10]` now carries the deactivation rule and `[G-11]` the `CANCELLED` terminal branch; this page's rule 1, `[BR-17]` and `[E-95]` follow them. Both specs now describe one behaviour. | Closed — kept here as the record of a conflict that existed between v1.2 and the owner decision. |

---

## 10. Decision Log

Every decision that shaped this screen, 2026-07-09 → 2026-08-03, including reversals and removals. Sources: the 2026-07-09 and 2026-08-02 decision ledgers, the wireframe legends (dated in-place), `_review.md` adjudications C-1…C-12, the PD register, and the owner's 2026-08-03 emphasis pass.

### 10.1 Chronological log

| Date | Decision | Effect on this page | Status |
|---|---|---|---|
| 2026-07-09 | Unified search: **remove the number-type toggle**, auto-detect instead; **remove the "matched field" badge** | `[L-S1-1]` `[BR-46]`; §9.4-1 | active |
| 2026-07-09 | Bulk bar sits **above the table, always visible**, disabled rather than hidden when unavailable | `[L-S1-9]` `[BR-47]` | active |
| 2026-07-09 | Inbounding everything **completes the order and auto-outbounds**; Hold orders stop at Inbound | `[BR-6]` `[BR-7]` | active |
| 2026-07-09 | Existing-inventory lines are marked by the **Sourcing Route badge + row tint**, never a duplicate label under the product name | `[L-S1-6]` `[BR-49]`; §9.4-6 | active |
| 2026-07-09 | `Location` column sits **right of Sourcing Route**, warehouse-held products only, common to all states | `[L-S1-17]` | active |
| 2026-07-09 | **Brand always shown** at the front of the product name | `[L-S1-18]` `[BR-36]` | active |
| 2026-07-09 | Returns: **quantity input for partial returns** defaulting to 0, location auto-filled, confirm blocked when a qty>0 line is unassigned | `[L-S4-3]` `[L-S4-4]` `[BR-13]` | active |
| 2026-07-09 | **Cancel Inbound disabled after outbound** — Cancel Outbound first | `[L-S3-4]` `[BR-10]` | proposed 2026-07-09 → **adopted 2026-08-03** `[PD-10 · OWNER-PENDING]` (**WF-3**) |
| 2026-07-09 | **Deleo Tracking No removed from View Orders**, retained on Order Detail | `[BR-40]`; §9.4-3 | active (reaffirmed 2026-07-22) |
| 2026-07-09 | Live barcode floating panel **collapsed by default** | `[L-S1-16]` | active |
| 2026-07-09 | **Identical table columns in every state** — per-state column reduction forbidden | `[BR-39]`; §9.4-9 | active |
| 2026-07-09 | Search/focus-return disclaimers are **common to all states** and are **behavior only, not on-screen text** | `[L-S1-14]` `[BR-30]` | active |
| 2026-07-09 | Button renamed **`Outbound to Deleo Baroship` → `Outbound`** | `[L-S1-10]` | active |
| 2026-07-09 | Reduced side padding so every column and button fits one screen | `[L-S1-4]` | active |
| 2026-07-09 | Single-item orders **auto-print on scan**, only when the order has no inbound history | `[L-S1-Fa]` `[BR-14]` | active |
| 2026-07-13 | **v20**: sourcing-route badges, **Hold State 5**, return last-mile lookup, Comments wording unified + ★ save + top-right Mentions/Saved hub | `[L-S1-3]` `[L-S1-6]` `[L-S1-19]` `[L-S4-5]` `[L-S5-1..3]` | active |
| 2026-08-03 | **v21**: M1 Cancel Inbound gains `3. Location (Optional)` — pre-filled with the SKU's registered location, required when the SKU has none (owner request) | `[L-M1]` `[BR-58]` `[E-94]` `[DC-11]` | active |
| 2026-07-13 | Coupang small QR arrives as `[V1]{barcode}` and **must match the barcode after the prefix** | `[BR-2]` | active |
| 2026-07-13 | **No `returned` status exists**; returns are detected by scanning the last-mile barcode, not by status | `[L-S4-6]` `[BR-12]`; §9.4-8 | active |
| 2026-07-13 | Sourcing routes extended to **4** (SMART BUY / JIT / WHOLESALE / PARTNERSHIP) as part of the I + J scope expansion | `[L-S1-6]` `[G-5]` | active |
| 2026-07-13 | Barcode entered on a barcode-less line writes to the **product master** | `[L-S1-20]` `[BR-16]` | active |
| 2026-07-14 | Capture-based rework of the other nine screens; **View Orders was already capture-based and stays authoritative** | context only | — |
| 2026-07-21 | **Photo upload on the unrecognized modal removed** (owner) and the double-click bug moved to the developer handoff note rather than the wireframe | `[BR-41]` `[BR-34]` | photo → **permanently deleted 2026-08-03** |
| 2026-07-21 | Global-nav mass replacement abandoned — each screen uses its own real capture | `[L-F1]` | active |
| 2026-07-21 | Instant printing requires a **local print agent** (browser cannot push to a queue) — developer handoff note B | §6.4 `[G-4]` | active |
| 2026-07-22 | Deleo tracking column removal reaffirmed as a deliberate asymmetry with Order Detail | `[BR-40]` | active |
| 2026-07-23 | Coupang `[V1]` rule text **moved off-screen** (behavior only) | `[L-S1-1]` | active |
| 2026-07-23 | Unrecognized-pool UX inverted on the tracking-missing page (system proposes suspected orders) | affects the downstream half of M2b's output | active |
| 2026-07-27 | **Internal inbound merged into View Orders as States 6 / 6b**; the separate `inbound-receiving` page is deleted (404) | `[L-S6-*]` `[L-S6b-*]`; §9.4-4 | active |
| 2026-07-27 | State 6 design set: purple "not a customer order · no Outbound" banner, progress tiles, continuous +1 product scanning with manual correction, Location = inventory intake position, **exact-match gating** for full confirm, `Save Partial Inbound` with reason | `[L-S6-2..8]` `[L-M5]` `[BR-18]` | active |
| 2026-07-29 | **Comments hub full-comment search** — every comment on every order, newest first, purple highlight, click opens the order, clearing returns to tabs | `[L-S1-3]` | active |
| 2026-07-29 | **Shelf / location floating Save button** — appears only on change, click or Enter saves instantly with no refresh, `✓ Saved` then auto-hides | `[L-S1-2]` `[L-S6-6]` `[L-S6-7]` `[BR-51]` | active |
| 2026-08-02 | **Expected Inbound badge, option C** — summary badge + click-to-expand table on State 0, tracking rows sorted first, **row click enters State 6 without scanning** | `[L-S0-2]` | active |
| 2026-08-02 | Inbound request lifecycle extended to **3 stages**: `REQUESTED → PARTIAL → INBOUNDED`; rescanning the same tracking resumes from the remainder | `[L-M5]` `[BR-23]` | active |
| 2026-08-02 | **Edit Expected Qty (M6)** added — new qty + mandatory reason, gating recalculation, auto-comment on the request, Slack to the requester | `[L-S6-9]` `[L-M6]` `[BR-22]` | active |
| 2026-08-02 | Unrequested arrivals **reuse the existing unrecognized pool**; a dedicated temporary-registration path is **rejected** | `[BR-48]`; §9.4-5 | active |
| 2026-08-02 | Procurement Hub excluded from this whole spec set | §9.1 | active |
| 2026-08-03 | **Outbound send sound** added (Web Audio synthesis, no external files) to the outbound-class buttons | `[L-S1-15]` `[BR-32]` `[G-3a]` `[PD-2 · OWNER-PENDING]` | active |
| 2026-08-03 | **JIT purchase channel shown in parentheses** — JIT (Coupang) / (Naver) / (Other retail); an Existing-inventory pick shows that stock's own route | `[L-S1-6]` `[BR-4]` | active |
| 2026-08-03 | **Multiple tracking numbers per inbound request** — every registered number matches and enters State 6; partial arrivals accumulate | `[L-S6-1]` `[BR-17]` `[G-10]` | active |
| 2026-08-03 | **Automatic Carrier recording is NOT supported.** Received Date stays automatic (for the sheet sync); no Carrier field, column, or capture | `[L-S6-F]` `[BR-24]` `[PD-9 · OWNER-PENDING]`; **WF-1**; §9.4-7 | active — **reversal, see 10.2 R-1** |
| 2026-08-03 | **Match writes the tracking number onto the order's product line**, so rescanning the same barcode resolves normally | `[L-M2]` `[BR-27]` | active |
| 2026-08-03 | Comment `@mention` channel **confirmed: `#fulfillment-admin-comments` (`C0BMGEWM5QA`)** — body @mention gives a personal notification while the channel archives for the team | §6.1 row 2 `[G-7]` | active (owner) |
| 2026-08-03 | **Scanner protocol** made a global rule with owner emphasis: cursor resident in the scan input, never refresh, zero clicks between scans | `[G-1]` `[BR-30]` `[BR-31]` | active |
| 2026-08-03 | **Global confirmation toast** on every confirming action, owner emphasis | `[G-2]` `[BR-51]` | active |
| 2026-08-03 | **Instant carrier-agnostic print** reconfirmed — the Print button alone must produce the label, via a local print agent | `[G-4]` §6.4 | active |
| 2026-08-03 | Sample assignment **retained as simple ON/OFF** (review item 1) | cross-page only; no control on this page | active — **reversal, see 10.2 R-7** |
| 2026-08-03 | Photo column deletion carried through (review item 15) | `[BR-41]`; §9.4-2 | active |
| 2026-08-03 | Carrier not added; narrative corrected (review item 16) | `[BR-24]` | active |
| 2026-08-03 | Demo renumbering of inbound numbers accepted as intentional (review item 14) | §2.3 L-5 | active |
| 2026-08-03 | Live barcode feed on-screen cap fixed at **20** (the legend's "10–20" is unassertable) | `[BR-37]`; **WF-13** | active |
| 2026-08-03 | M6 reason enum aligned to the **wireframe M6 strings** (`_review.md` C-11); the third option label is exactly `Other` | `[L-M6]` `[BR-53]` `[G-11]` | active |
| 2026-08-03 | `Confirm Full Inbound` additionally requires **a location on every received SKU** | `[BR-20]` `[PD-13 · OWNER-PENDING]` | provisional |
| 2026-08-03 | State 6 over-scan **warns and counts**; it does not cap | `[BR-19]` `[PD-12 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Rescanning an already-INBOUNDED product barcode → **amber warning toast**, no second inbound, no sound | `[BR-26]` `[PD-11 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Rescanning a fully INBOUNDED request's tracking → **read-only 6b view + info toast** | `[BR-25]` `[PD-15 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Expected-qty edit may **not** go below the received qty and may not be 0; lowering it to the received qty **enables but never auto-presses** Confirm | `[BR-22]` `[PD-14 · OWNER-PENDING]` `[PD-84 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Shelf **auto-clears on Outbound** | `[BR-29]` `[PD-18 · OWNER-PENDING]` | provisional |
| 2026-08-03 | An on-the-spot M2 match fires the **same** auto-comment + Slack route; self-mention suppressed | `[BR-28]` `[PD-16 · OWNER-PENDING]` | provisional |
| 2026-08-03 | qty-0 return lines are **persisted explicitly**; no disposition field in v1 | `[DC-27]` `[PD-17 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Print failure never blocks the inbound; auto-print failure is not a gate | `[BR-15]` `[PD-19 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Auto-outbound is a **View Orders scan/bulk behavior only** — Order Detail is always manual | `[BR-6]` `[PD-21 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Order Detail carries a **parity `Cancel Outbound`** with the same rollback as this page | `[L-S3-2]` `[PD-26 · OWNER-PENDING]` | provisional (cross-page) |
| 2026-08-03 | Outbound is allowed only from `processing` or `pending` with every line INBOUNDED | `[BR-9]` `[PD-29 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Inventory is **display-only for PENDING** inbound events; State 6 / the Inbound Request lifecycle is the sole confirm path | `[BR-52]` `[L-S6-8]` `[PD-41 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Locations are **1:1** — one location per SKU **and** one SKU per location | `[BR-21]` `[PD-46 · OWNER-PENDING]` | provisional |
| 2026-08-03 | OTHER-origin routes render as black bold `OTHER ({channel})` downstream | `[L-S1-6]` `[L-S0-2]` `[PD-80 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Inbound and outbound tracking numbers are **separate namespaces** and may coincide; inbound-request tracking wins resolution | `[BR-45]` `[PD-8 · OWNER-PENDING]` `[PD-86 · OWNER-PENDING]` | provisional |
| 2026-08-03 | A tracking number is unique across inbound requests; a duplicate is blocked at Inbound Request save | `[E-64]` `[PD-82 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Comments-hub entries for unrecognized-pool items open the pool row, or the matched order once resolved | `[L-S1-3]` `[PD-67 · OWNER-PENDING]` | provisional |
| 2026-08-03 | v1 ships a **single admin role**; no role gating on this page | `[BR-35]` `[G-15]` `[PD-1 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Comments are **append-only** | `[BR-33]` `[PD-3 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Destructive actions get a confirm step, a reason where an enum exists, and a stated confirmation | `[L-S2-2]` `[PD-5 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Slack failure never blocks or rolls back the primary action | `[BR-42]` `[PD-4 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Stale entities are revalidated at confirm; concurrency uses optimistic versioning, **except State 6 counting which merges** | `[BR-43]` `[BR-44]` `[PD-6 · OWNER-PENDING]` `[PD-7 · OWNER-PENDING]` | provisional |
| 2026-08-03 | Hold reason is optional free text, captured where the hold is applied and rendered verbatim here | `[L-S5-1]` `[PD-20 · OWNER-PENDING]` | provisional |
| **2026-08-03 (audit pass)** | Two rendered elements had no legend key — the page heading/section labels and State 0's waiting placeholder. Keyed as `[L-F7]` / `[L-F8]`; unit total 67 → **69** | §2.1 | active |
| **2026-08-03 (audit pass)** | The Live Barcode Feed **export** is an operator action over operator-identifying data and now has its own event `[DC-47]`; register 46 → **47** events, and export governance is raised as §9.2 OQ-2 | `[L-S1-16]` §5.10/§5.11 | active |
| **2026-08-03 (audit pass)** | The floating-save `✓ Saved` chip is declared a **rendering-position delta** on `[G-2]`, not an exemption; failures still raise the red top-right toast | `[BR-51]`; `_review.md` C-6 | active |
| **2026-08-03 (audit pass)** | Physical scan de-duplication is explicitly **rejected** — a double scanner emission counts twice, unlike a double button click | `[E-67]` vs `[E-13]` | active |
| **2026-08-03 (audit pass)** | A partial bulk batch must be reported as partial with the failing lines named; successful lines are never rolled back | `[BR-55]` `[E-72]` | active |
| **2026-08-03 (audit pass)** | In-flight scan submits are queued in order, never dropped and never interleaved | `[BR-54]` `[E-66]` | active |
| **2026-08-03 (audit pass)** | `Received Qty` stays editable after a SKU reaches its expected quantity; the wireframe's `readonly` on the completed row is demo styling | `[BR-56]` `[E-92]`; §2.3 L-14 | active |
| **2026-08-03 (remediation)** | **A cancel-inbound under-restock books its remainder as an inventory adjustment.** Spec v1.1's "accounted for by the memo" is reversed: a memo is not a stock event and lost the units from the ledger `[G-8]`, and it diverged from Inventory's M4 release path. `Yes + qty 0` is blocked; `No` is the zero path | `[BR-57]` `[E-27]` `[E-93]` `[DC-39]`; §9.5 CP-1 | active — **reversal, see 10.2 R-13** `[PD-49 · OWNER-PENDING]` |
| **2026-08-03 (remediation)** | **`OTHER ({channel})` on order rows declared a page delta on `[G-5]`**, not an unstated fifth badge: it is a rendering pass-through of the Inbound Request's route, never selectable here | `[L-S1-6]`; §9.5 CP-3 `[PD-80 · OWNER-PENDING]` | active |
| **2026-08-03 (remediation)** | **Hold origin corrected to OMS / Order Detail only** — Order Management removed all hold controls the same day; the wireframe legend's `or Order Management` clause is now stale copy, kept visible by a `[WF]` assertion with an `[ADMIN]` twin | `[L-S5-F]` §9.1; QA-CV-08 / QA-CV-23; §9.5 CP-6 | active — **reversal, see 10.2 R-14** |
| **2026-08-03 (remediation)** | **§8.0 made mechanically executable**: annotation chrome (`.dot`, modal `button.x`) is stripped before every text comparison; "exactly" means whitespace-collapsed equality, not raw byte equality; the two-table trap in States 1–5 is named; "visible" is defined; `.foot` and the hub panes are named. An adversarial run of all 135 `[WF]` scenarios produced 28 false failures against a correct wireframe, every one traceable to a missing rule here | §8.0 rules 5, 6, 6b, 7b, 7c | active |
| **2026-08-03 (remediation)** | **Comments-hub copy declared a `[G-7]` cross-page contract**, and this page's shipped strings recorded as the minority form (**WF-VO-1**) rather than silently asserted as correct | `[L-S1-3]`; §2.4; QA-C-18; §9.5 CP-4 | superseded the same day — see next row |
| **2026-08-03 (owner-approved batch)** | **`[G-7]` v1.2 published the canonical hub set HUB-1…HUB-7 and WF-VO-1 was applied**: all nine `.inboxdd` blocks on this page moved to the canonical strings, and QA-C-03 / QA-C-05 / QA-C-06 / QA-C-07 / QA-C-10 / QA-C-11 re-baselined in the same commit. CP-4 closed | `_global-rules.md` `[G-7]`; §2.4 WF-VO-1; §9.5 CP-4 | active |
| **2026-08-03 (remediation)** | Footer sub-keys normalized to `[L-S1-Fa]` / `[L-S1-Fb]` / `[L-S1-Fc]` (the parenthesised `[L-S1-F(a)]` form is retired) and declared in §2.1; `[E-6]`'s divergence from the plan's E-6 documented instead of renumbered; QA-CV-22 given its `[ADMIN]` tier tag; the `[G-*]`-restating rows `BR-33`…`BR-36` reduced to page deltas | §2.1, §4, §7, §8.13 | active |

### 10.2 Reversals and removals — the "nothing was silently dropped" record

| # | Chain | Where it lands |
|---|---|---|
| **R-1** | **Carrier auto-record.** 2026-07-09 / 2026-07-27: "Received Date **and Carrier** are recorded automatically on confirm" → **2026-08-03: automatic Carrier recording is NOT supported.** Received Date remains automatic (it feeds the sheet sync); Carrier has no field, no column, no capture anywhere. The State 6b banner carried the stale clause — defect **WF-1**, **fixed in the wireframe 2026-08-03** (it now reads `· Carrier is not recorded`); the State 6 legend footer was already correct. | `[BR-24]` `[L-S6-F]` `[L-S6b-1]` `[PD-9 · OWNER-PENDING]`; `_review.md` C-1 |
| **R-2** | **Cancel-Inbound lockout.** 2026-07-09: written as a *proposal* → **2026-08-03: adopted as a rule.** The wireframe legend still shows the `— proposal` qualifier — defect **WF-3**. | `[BR-10]` `[L-S3-4]` `[PD-10 · OWNER-PENDING]` |
| **R-3** | **Photo capture on unrecognized items.** 2026-07-21: removed from the View Orders modal and marked *deferred* → **2026-08-03: permanently removed**, with no phase pointer, so nobody re-implements it from the stale note. | `[BR-41]`; §9.4-2; `[PD-63 · OWNER-PENDING]` |
| **R-4** | **Separate internal-inbound page.** A dedicated `inbound-receiving` screen was built → **2026-07-27: deleted (404) and merged into View Orders States 6 / 6b**, because it had to connect to the other states. Any surviving link would 404. | `[L-S6-*]`; §9.4-4; QA-NG-09 |
| **R-5** | **Unrequested-arrival intake.** A dedicated temporary-registration path was proposed → **2026-08-02: rejected**; unrequested arrivals reuse the existing unrecognized pool, and the handler creates the inbound request and registers the tracking number, after which a rescan enters State 6 normally. | `[BR-48]`; §9.4-5 |
| **R-6** | **Search type toggle and "matched field" badge.** Both existed in the first draft → **2026-07-09: removed** — the operator does not know what kind of number is on the label. | `[BR-46]`; §9.4-1 |
| **R-7** | **Sample assignment.** 2026-07-22 note said "removed" → **2026-07-23: reinstated as simple ON/OFF with multiple, possibly overlapping periods** → **2026-08-03: reconfirmed and retained**. It has **no control on this page** — it is Order Management's — but it changes what printed artifacts contain, which is why it is recorded here. | `[G-13]`; §9.1 |
| **R-8** | **Live-feed cap.** Legend said "10–20 rows" while the panel footer said "Max 20" → **2026-08-03: fixed at 20**, because a range cannot be asserted in QA. | `[BR-37]`; **WF-13** |
| **R-9** | **Deleo naming.** The outbound button once read `Outbound to Deleo Baroship` and the table once carried a Deleo Tracking No column → **2026-07-09 / 2026-07-22: both removed** from this page, in favour of carrier-agnostic wording; Order Detail keeps the Deleo reference deliberately. | `[L-S1-10]` `[BR-40]`; §9.4-3; QA-S1-09 |
| **R-10** | **Comment mention channel.** Drafts recorded the channel as "pending owner decision" → **2026-08-03: confirmed `#fulfillment-admin-comments` (`C0BMGEWM5QA`)**, created by the owner. No spec may say "pending" for this row. | §6.1; `_review.md` C-2 |
| **R-11** | **M6 reason enum wording.** The `[G-11]` draft read "supplier change / damaged / other" and later "Other (memo)" → **2026-08-03: the wireframe M6 strings are canonical** (`_review.md` C-11); the third option label is exactly `Other`, and the "(memo)" phrasing survives only as the obligation to explain in the memo field. | `[BR-53]` `[L-M6]` |
| **R-12** | **Unit and event counts (audit pass).** Spec v1.0 declared 67 legend units and 46 data-capture events → **v1.1: 69 units and 47 events.** Nothing was removed; two unkeyed rendered elements (`[L-F7]`, `[L-F8]`) and one unnamed persisted action (`[DC-47]`, feed export) were added. Recorded here so a reader comparing the two versions does not read the change as scope creep. | §2.1, §5.11 |
| **R-13** | **Cancel-Inbound under-restock remainder.** 2026-07-09 → v1.1: "the remainder is accounted for by the memo" → **2026-08-03 (v1.2): the remainder is booked as `ADJUST(−remainder)`**, an inventory event carrying the same memo, in the same transaction and under the same idempotency key. The reversal is not a preference: a memo is not a stock event, so the old wording lost units from the ledger `[G-8]` and contradicted Inventory's M4 release path, which books the identical adjustment for the identical physical fact. `Yes + qty 0` also became a blocked state, because it duplicates `No`. | `[BR-57]` `[E-27]` `[E-93]` `[DC-39]`; §9.5 CP-1; `[PD-49 · OWNER-PENDING]` |
| **R-14** | **Hold origin.** The wireframe legend (2026-07-13) named `OMS/Order detail or Order Management` and v1.1 adopted it verbatim → **2026-08-03: Order Management removed every hold control and forbids one existing**, so the origin is **OMS / Order Detail only**. The legend clause is now stale wireframe copy, treated exactly as WF-1/WF-3/WF-13 are: the shipped string keeps a `[WF]` assertion (QA-CV-08) and the corrected sentence gets an `[ADMIN]` twin (QA-CV-23), so nothing is silently rewritten and nothing silently rots. | `[L-S5-F]` §9.1; §9.5 CP-6 |
| **R-15** | **Comments-hub copy.** v1.1 asserted this page's hub strings as correct, byte-exactly, without noticing that five other specs assert a different form for the same single control → **2026-08-03: recorded as divergence WF-VO-1**, resolution assigned to `[G-7]` rather than taken here → **same day: `[G-7]` v1.2 published HUB-1…HUB-7 and the fix was applied corpus-wide**, so this page's wireframe and `[WF]` assertions now carry the canonical strings. The lesson holds: the divergence was invisible for as long as each spec only read itself. | `[L-S1-3]`; §2.4 **WF-VO-1**; QA-C-18; §9.5 CP-4 |

### 10.3 Traceability

- **Legend units covered: 69** — 58 wireframe dots (independently counted from `wms2/view-orders/index.html`: 50 state dots + 8 modal dots) + 3 off-screen footer blocks (`[L-S1-F]`, `[L-S5-F]`, `[L-S6-F]`) + 8 page-furniture units (`[L-F1]`…`[L-F8]`). Numbering quirks declared in §2.1: State 1 runs 1–20 **and** 22 (dot 21 lives in State 1b); State 4 legend entries 3 and 4 have no on-screen dot; legend numbers repeat per state, so every key is state-qualified; `[L-S1-F]`'s sub-keys `[L-S1-Fa]`/`[L-S1-Fb]`/`[L-S1-Fc]` are addressing, not units.
- **Business rules: BR-1 … BR-57**, each with rationale and date (BR-51…BR-56 added by the audit pass; BR-57 by the cross-page remediation).
- **Data-capture events: DC-1 … DC-47**, no gaps, plus 10 declared NON-events and per-class retention/export terms.
- **Edge cases: E-1 … E-94** across 93 entries (`E-18 = E-51` merged, both IDs retained per the never-renumber rule; `[E-6]`'s divergence from the plan's E-6 is documented in §7's preamble rather than repaired by renumbering, which the same rule forbids).
- **QA scenarios: 279** — 136 `[WF]` / 143 `[ADMIN]`; QA-CV-22, formerly DEFERRED, was un-deferred when `[PD-66]` was owner-decided (2026-08-03); 92 negatives (33.0 %). Coverage: 0 uncovered legend units, 0 uncovered DC events, 0 uncovered edge cases, 0 uncovered business rules. *(This line read `277 — 135 / 142`, 91 negatives, until 2026-08-03: it was the pre-v1.3 count and had not been advanced when QA-M1-10 / QA-M1-11 were added. §8.14 is the authoritative census and always was; the two now agree.)*
- **Provisional decisions relied upon: 33** — the 32 of §9.2 plus `PD-49` (the cancel-inbound remainder adjustment, `[BR-57]`), adopted by the 2026-08-03 remediation.
- **Wireframe defects named: WF-1 (fixed 2026-08-03), WF-3, WF-13, WF-VO-1 (applied 2026-08-03)**; 15 demo limitations declared (§2.3 L-1…L-15), of which L-2/L-8/L-9/L-10/L-11/L-12/L-13/L-14/L-15 are candidates for the `_wireframe-fixes` backlog.
- **Owner-pending gaps: 1** — §9.2 OQ-2 (feed-export governance). OQ-1 (`PD-66`, pool entry without a tracking number) was owner-decided 2026-08-03: the case does not exist, identifier required.
- **Cross-page disagreements: 9** — §9.5 CP-1…CP-9. Four are now resolved (CP-1, CP-3, CP-6 on this page — plus CP-8's internal normalization — and **CP-4 closed 2026-08-03** by the `[G-7]` v1.2 hub-copy canonicalization); the rest are stated with this page's position and the fix assigned to `_global-rules` or the disagreeing spec.
