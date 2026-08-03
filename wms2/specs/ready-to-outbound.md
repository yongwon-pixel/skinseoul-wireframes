# Ready to be Outbounded — Screen Specification

> **Decision status update (2026-08-03)** — PD-1 through PD-8, 51, 55, 66, 71, 74, 79 are now **OWNER-DECIDED** (PD-6 confirmed 2026-08-03 — the owner decision round is fully closed); any inline `[PD-{these} · OWNER-PENDING]` or `[PD-{these} · NO-DEFAULT]` tags below are superseded — see `_provisional-decisions.md` for the decisions.

**Slug:** `ready-to-outbound` · **Wireframe (SST):** `wms2/ready-to-outbound/index.html` · **Live:** https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/ready-to-outbound/
**Spec version:** 1.2 · **Date:** 2026-08-03 · **Template:** `_inputs/spec-template.md` (10 sections, in order)
**Global rules:** `_global-rules.md` — cited as `[G-n]`; this document writes **page deltas only** and never restates a rule body.
**Provisional decisions:** `_plans/_provisional-decisions.md` — any behavior resting on one is tagged `[PD-n · OWNER-PENDING]` in the sentence where it appears.
**Wireframe defects:** `_plans/_wireframe-fixes.md` — this spec describes the **correct** behavior; stale wireframe text is never specified, only cited as a defect.
**Binding conventions:** `_plans/_review.md` §3 (legend keys, ID stability, QA tiers, dates, Slack notation, removals).

---

## 1. Purpose & Users

### 1.1 What this screen is

**Ready to be Outbounded** is the outbound launch pad. It lists every order that has at least one line item in `INBOUNDED` status and is therefore physically pickable today, and it gives one desk operator three batch levers over a single selection of those orders:

1. **Print Pick Locations** — produce the paper picking list the picker walks with.
2. **Bulk Print Labels** — produce the shipping labels the packer sticks on boxes.
3. **Bulk Outbound** — commit the shipment: flip the orders out of the fulfilment queue and decrement stock.

It is a **list-and-batch** screen, not a scan screen and not an inspection screen. Anything requiring per-order judgement (holds, line edits, cancellations, tracking corrections) happens on **Order Detail**; anything requiring a barcode happens on **View Orders** or **Closing**. This screen's entire job is to turn "N orders are ready" into "N orders are picked, labelled, and shipped" with the fewest possible clicks and the fewest possible reasons to look at the monitor.

### 1.2 Who uses it, and where their body is

Three people touch one wave, and almost every design decision on this page exists because two of them are **not standing at the monitor**.

**(a) Desk operator (order team).** Sits at the admin screen. Owns the selection and fires the three bulk actions. This is the only person who reads the table. Everything they need to sanity-check a wave — order count, unit count, per-order Total Items, the picking-modal header totals — must reconcile numerically without arithmetic, because they are checking it in the ten seconds before they start the wave, not auditing it.

**(b) Picker (warehouse staff).** Takes the printed picking list and **walks away from the monitor** into the rack aisles. From that moment the paper is the only interface. Consequences that are written into this spec as hard rules:

- **Korean product names** on the picking list and in *Ready Item Details* [G-6]. The physical bottles and cartons on the shelf carry Korean front-of-pack text; an English name forces the picker to translate at the shelf. The English name with bold brand stays on the order-facing pages, which are read at a desk. (2026-08-03)
- **Location-ascending sort** on the picking list [BR-7]. The rack aisles are walked in one direction; a list sorted by order or by SKU makes the picker cross the same aisle three times. `A-02-13 → A-03-02 → B-01-07 → B-02-11 → Shelf 3` is a route, not a report.
- **Total Items = unit sum, not SKU count** [BR-5]. The old admin counted SKUs, so an order of one SKU × 5 units displayed "1". Pickers under-picked. The number on the screen and the number on the paper are now the number of physical objects to put in the box.
- **Bold quantity on multi-unit lines.** A `5` that looks like every other digit is a `1` at arm's length under warehouse lighting.
- **Every pick cell resolves to something** [BR-23]. Rack stock shows the location code, staged JIT stock shows `Shelf N`, and a line that is not inbounded shows the amber `Not inbounded` pill. A blank cell is a picker standing still.

**(c) Packer.** Works at the pack bench with the label printer within arm's reach and **hands on boxes**. Consequences:

- **Instant printing** [G-4]. A browser print dialog requires the packer to put the box down, take the mouse, and confirm. This is why the local print agent is mandatory infrastructure on this page and not an optimisation.
- **Eyes-free completion feedback.** The desk operator fires Bulk Outbound and immediately turns to the boxes. The completion signal is therefore **both** a top-right toast [G-2] **and** an audible send sound [G-3a] `[PD-2 · OWNER-PENDING]`. Neither replaces the other: the toast is for the operator who is looking, the sound is for the operator who has already turned away.
- **Per-row reprint.** Labels get smudged, torn, and stuck to the wrong box. The row `🖨` button is the reprint path; reprinting is normal operations, never an error, and is always recorded [BR-32].

### 1.3 The operational moment

This screen is used in a **morning wave**: one selection, three actions, in order, within a few minutes. The load-bearing consequence is that **selection survives both print actions and dies only on the outbound refresh** [BR-8]. If printing cleared the selection, the operator would have to re-select the same orders three times, and on the third pass would select a different set — which is exactly how an order ships without a label.

The second consequence is the shared progress bar [L-5]: one bar, one action at a time. Firing a second batch while one is running would produce two overlapping progress states and an ambiguous toast, so the three buttons lock while any batch runs [BR-18].

### 1.4 What this screen deliberately is not

- **No scanner surface.** [G-1] does **not** apply to this page — there is no scan input, no focus-retention requirement, and no scan feed. This is stated explicitly so that automated QA does not report a missing scanner protocol as a defect. (2026-08-03) [BR-25]
- **No inspection.** No line-item editing, no status changes, no cancellation, no tracking entry. Those live on Order Detail; the Order ID link is the doorway [L-F5].
- **No search over orders.** The pool is a day's worth of ready orders, filtered by four view tabs. An order search bar was never part of this screen and must not be added. (The Comments hub's full-text search is a comment search, not an order search [L-10].)
- **No pagination.** Not present in the wireframe; large-selection behavior is handled by chunking, not paging (§9.3 D-2).
- **No sourcing-route badge column.** [G-5] route labels (SMART BUY · JIT (channel) · WHOLESALE · PARTNERSHIP, plus `OTHER (channel)` `[PD-80 · OWNER-PENDING]`) render on View Orders, Inventory, and Order Detail — **not here**. **Which of those surfaces may carry `OTHER (channel)` on an order-facing row is owned by [G-5], not by this page**: `order-detail.md` `[L-4]` states it never appears there while View Orders does render it, so that disagreement is recorded for [G-5] resolution (2026-08-03) and does not reach this page, which renders no route label of any kind. The only badges on this page are the state badge `Fully Inbounded` [L-7] and the origin badge `MKT` [L-8]. This is why the JIT badge was renamed on 2026-08-03 [BR-4].

### 1.5 Permissions

[G-15] applies unchanged `[PD-1 · OWNER-PENDING]`. The only page delta worth stating: **Bulk Outbound carries no gate of its own** — it is not restricted more tightly than the two print actions.

---

## 2. Screen Inventory & Wireframe Map

### 2.1 Declared unit count (mandatory declaration)

- **Legend units: 15** — numbered dots **1–14** (all present, no gaps) plus **one modal, M1**. Independently verified against the wireframe source: the legend `<ol>` contains exactly **14** `<li>` elements, and the document contains exactly **15** elements with class `dot` (14 inside `.mock`, 1 inside `#m-pick`). This matches the reconciled count in `_review.md` §2a (Lens A 15 / Lens B 15 / match).
- **Page-furniture units: 8** — `[L-F1]`…`[L-F8]`, unnumbered elements inherited from the actual admin capture (2026-07-21) that are normative but carry no legend dot. Keyed per `_review.md` §3 convention 1 and the `stock-status` precedent (§2c item 3).
- **Total specified implementation units: 23.** Every one of the 23 has its own subsection in §3 (§3.1–§3.23).
- **Key style:** this is a **single-state page**, so legend keys are plain `[L-n]`; the modal is `[L-M1]`; furniture is `[L-Fn]`. (Per `_review.md` §3 convention 1 — `[L-{state}-{n}]` is reserved for multi-state pages, and `[L-{state}-F]` off-screen footer keys do not apply because this page's legend footnote is folded into `[L-F7]`/`[L-F1]`.)

**Declared numbering artifacts (not coverage gaps):**

| Artifact | Statement |
|---|---|
| Legend render order | The legend renders in the order **1, 2, 3, 4, 5, 6, 7, 8, 14, 13, 12, 9, 10, 11**. This is a presentation order chosen to group the new bulk-action block first; it is not a numbering gap and not a defect. All 14 numbers exist exactly once. Machine-checkable: QA-F-08. |
| No `[L-M2]`+ | This page has exactly one modal. The Comments hub (`#inbox1`) is a dropdown owned by `[L-10]`, not a modal, and is not counted as `M2`. |
| Duplicate wireframe chrome | The demo `wf-bar` contains **two** buttons that both open `#m-pick` (`Modal: Print Pick Locations (Picking List)` and `Modal: Print Pick Locations`). Counted **once**. Demo-chrome duplication only — see `[RTO-WFX-2]` in §2.4. |
| View tabs are filters, not states | All / Inventory / Marketing / JIT are client-side filters over one table in one state. They are enumerated below as *view states* for QA reachability, but they do not multiply the legend keying. |
| Legend footnote paragraph | The paragraph below the legend `<ol>` is normative (base structure, Korean names, instant print, sort order, Actions column). It carries no dot; its rules are specified in `[L-F7]`, `[L-F1]`, [BR-2], [BR-6], [BR-10], [BR-12], [BR-14]. |

### 2.2 Reachability map — legend ↔ spec ↔ how to reach

Live base URL for every row: `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/ready-to-outbound/`

| Legend | Element | Spec key | State / how to reach it |
|---|---|---|---|
| 1 | Per-row checkboxes + `Select all`; the three bulk buttons carry live selected-order and item counts | `[L-1]` → §3.1 | Default view. Bulk bar (`.bulkbar`) directly under the view tabs. Wireframe checkboxes are inert (see §2.4 `[RTO-WFX-1]`). |
| 2 | `🖨 Print Pick Locations (3 orders · 8 items)` — opens the Picking List modal | `[L-2]` → §3.2 | Default view; click the button, or the `wf-bar` demo button `Modal: Print Pick Locations (Picking List)`. |
| 3 | `🖨 Bulk Print Labels (3 orders)` | `[L-3]` → §3.3 | Default view; click runs the progress + toast demo. |
| 4 | `📦 Bulk Outbound (3 orders)` — the sole designed refresh exception + send sound | `[L-4]` → §3.4 | Default view; click runs progress + toast + `sndOutbound()`. |
| 5 | Shared 0–100 % progress bar (`#pfill` / `#pbarLabel`) | `[L-5]` → §3.5 | Visible at rest with the wireframe's static 60 % fill; animates on any bulk action. |
| 6 | Completion notice = top-right toast (`#toast`), auto-dismiss, no failure case | `[L-6]` → §3.6 | Appears at 100 % of any bulk action; hides after ~3 s. |
| 7 | JIT order fully inbounded, Outbound not clicked = yellow tint + `Fully Inbounded` badge, always bottom | `[L-7]` → §3.7 | Row `422164` in the default view; or view tab `JIT`. |
| 8 | Manually imported Marketing order = purple tint + `MKT` badge, PIC line, amber `Not inbounded` pill | `[L-8]` → §3.8 | Row `MKT-40233` in the default view; or view tab `Marketing`. |
| 9 | Per-row Comments button → inline comment panel under the row | `[L-9]` → §3.9 | Click any `.cmtbtn` (`💬`) in the Comments column; panels are `#crow1`…`#crow5`. |
| 10 | Top-right Comments hub — `@ Mentions` / `★ Saved` + full-text search | `[L-10]` → §3.10 | Click `💬 Comments` in the global nav (`.icon-btn[data-open="inbox1"]`, badge `2`). |
| 11 | Reduced side padding — full-width layout | `[L-11]` → §3.11 | Always on (`.pagepad`). |
| 12 | **Pick Locations** column — per-item locators at the same eye level as Ready Item Details | `[L-12]` → §3.12 | Always on; 7th table column. |
| 13 | **Total Items** = total quantity sum | `[L-13]` → §3.13 | Always on; 5th table column (`.cntbadge.cb-total`). |
| 14 | **View tabs** All / Inventory / Marketing / JIT bound to the Found count | `[L-14]` → §3.14 | Always on (`.viewtabs`); click any `.vtab`. |
| M1 | `Print Pick Locations — Picking List` modal | `[L-M1]` → §3.15 | Open via `[L-2]` or either `wf-bar` demo button; overlay id `#m-pick`. |

### 2.3 Page furniture (unnumbered, normative)

| Key | Element | Spec |
|---|---|---|
| `[L-F1]` | Page title `WMS - Ready to be Outbonded` + section heading `Ready to be Outbonded Orders` — misspelling preserved from the live admin | §3.16 |
| `[L-F2]` | `Refresh` button (blue, top-right of the section heading row) | §3.17 |
| `[L-F3]` | `Found N order(s) with items ready for outbound` (`#foundTxt`) | §3.18 |
| `[L-F4]` | `How to use:` block — 5 bullets; bullet 2 is the normative page-inclusion rule | §3.19 |
| `[L-F5]` | Order ID link → Order Detail deep link [G-12] | §3.20 |
| `[L-F6]` | Per-row `🖨` Print button (Print column) — single-order instant label print [G-4] | §3.21 |
| `[L-F7]` | Table contract: 9 columns, one row per order, global sort regular → MKT → JIT, cell formats | §3.22 |
| `[L-F8]` | Global nav + signed-in identity (`Yongwon Ryu`) — the actor source for every event in §5 [G-8] | §3.23 |

### 2.4 View states, sub-states, and wireframe defects observed on this page

**View states (all reachable today, all `[WF]`-testable):**

| # | State | Reach | Expected row set | `#foundTxt` |
|---|---|---|---|---|
| V-1 | **All** (default) | Page load, or `.vtab[data-view="all"]` | 5 order rows: `422221`, `422176`, `422165`, `MKT-40233`, `422164` | `Found 5 order(s) with items ready for outbound` |
| V-2 | **Inventory** | `.vtab[data-view="inv"]` | `422221`, `422176`, `422165` | `Found 3 order(s) with items ready for outbound` |
| V-3 | **Marketing** | `.vtab[data-view="mkt"]` | `MKT-40233` | `Found 1 order(s) with items ready for outbound` |
| V-4 | **JIT** | `.vtab[data-view="jit"]` | `422164` | `Found 1 order(s) with items ready for outbound` |
| V-5 | **Inline comment panel expanded** | Click any `.cmtbtn` | The matching `#crowN` becomes a visible table row | unchanged |
| V-6 | **Comments hub open** | Click `.icon-btn[data-open="inbox1"]` | `#inbox1` gains `.open`; Mentions pane active | unchanged |
| V-7 | **Comments hub search results** | Type into `#inbox1 .csearch input` | Tabs hide; `[data-pane="csr"]` renders hits | unchanged |
| V-8 | **Batch running** | Click `[L-3]`, `[L-4]`, or M1 `🖨 Print` | `#pfill` animates 0→100 %, `#pbarLabel` shows the action + mode | unchanged |
| V-9 | **Completion toast** | Any batch reaching 100 % | `#toast` visible top-right for ~3 s | unchanged |
| V-10 | **Modal M1 open** | `[L-2]` | `#m-pick` gains `.open` | unchanged |
| V-11 | **Annotations hidden** | Click `#annoToggle` (`Hide annotations`) | `body` gains `no-anno`; all `.dot` and `.legend` hidden; button text becomes `Show annotations` | unchanged |

**Registered wireframe defects that touch this page:**

| ID | Defect | Correct behavior specified in |
|---|---|---|
| **WF-9** | M1 picking list has no sample-set rows, while [G-13] requires internal picking artifacts to show **which** sample and **how many**. Fix is **conditional** on owner approval of PD-36 *and* an answer to PD-51. | §3.15 (`[L-M1]`), [BR-21] `[PD-36 · OWNER-PENDING]` |
| **`[RTO-WFX-9]`** | The bulk demo sets `#pfill`'s inline width synchronously on click but rewrites `#pbarLabel` only on the first 250 ms `setInterval` tick, so every run displays the **previous** action's label — including its mode string — for its opening ~250 ms. Appended to `_wireframe-fixes.md` §B on 2026-08-03; fix is one line (write the label once before starting the interval). *(Page-scoped ID: the register's next numeric ID was claimed concurrently by three other pages' remediation passes, so this entry continues this page's own `[RTO-WFX-n]` series — it is nonetheless a **registered** item, not a candidate.)* | §3.5 (`[L-5]`) specifies the correct behavior — the mode string is the contract from the moment the run starts. Until the fix lands, §8.0's running-label reading rule bounds every "during the run" assertion and QA-L5-04 samples only from the first tick. |

**New defect candidates found while writing and auditing this spec** — `[RTO-WFX-1]`…`[RTO-WFX-8]`, none of them yet in `_wireframe-fixes.md`; page-scoped IDs are used to avoid colliding with the `WF-n` register. (`[RTO-WFX-9]` continues the same series but **is** registered — see the row above.)

| ID | Defect | Why it matters | Correct behavior in |
|---|---|---|---|
| `[RTO-WFX-1]` | All checkboxes are inert — the header checkbox, the bulk-bar `Select all`, and the five row checkboxes have no handler. The three bulk-button counts and `3 selected` are static text. | A naive QA run would report the selection model as broken; conversely a developer could ship static labels. Also: **two** select-all controls exist (header cell and bulk bar) with no defined relationship. | §3.1 `[L-1]` |
| `[RTO-WFX-2]` | `wf-bar` contains two buttons opening the same modal (`Modal: Print Pick Locations (Picking List)` with class `wf-toggle`, and `Modal: Print Pick Locations` with class `wf-tab`, which has no CSS rule and renders unstyled). | Same class of defect as **WF-12** on `closing`; a naive coverage check double-counts M1. | §2.1 artifacts table |
| `[RTO-WFX-3]` | The Order ID is a `<span class="oid">` styled to look like a link, not an anchor — there is no `href`, so [G-12] deep linking is not actually wired. | A developer copying the markup ships a dead link on the one navigation path this page has. | §3.20 `[L-F5]` |
| `[RTO-WFX-4]` | Dead CSS class `.cb-ready` (green count badge) survives from the **removed** *Ready Items* column; `.picktbl td.num` also has no rule. | Exactly the WF-10 failure mode: a developer reading the stylesheet re-implements the column that was deliberately deleted on 2026-07-22. | §3.13, §4.1 removals table |
| `[RTO-WFX-5]` | Korean-name rule violated in two places: (a) M1 product cells render the Korean name **without** the bold EN brand prefix (`마데카 크림 타이트닝`), while the main table renders `<b>Centellian24</b> 마데카 크림 타이트닝`; (b) order `422221` renders an **English, elided** product name `AtoBarrier365 Body …` in *Ready Item Details* **and** in M1 row 1, where [BR-6] requires the Korean name. | [G-6] requires the bold EN brand on Korean names everywhere, and [BR-6] requires Korean names in exactly these two surfaces. Near-identical Korean names exist in the catalogue (`마데카 크림 타이트닝` vs `마데카 크림 타임 리버스`), so the brand prefix is the disambiguator. | §3.15 `[L-M1]`, §3.22 `[L-F7]` |
| `[RTO-WFX-6]` | The per-row `🖨` Print button produces **no toast**. [G-2] requires a confirmation on every confirming action, and a label emerging from a printer the operator may not be facing is precisely the case the rule exists for. | Without it, the operator cannot tell a successful reprint from a dead button. | §3.21 `[L-F6]`, [BR-34] |
| `[RTO-WFX-7]` | The comment `Post` button produces **no toast** and the wireframe never appends the posted comment to the panel. | Same [G-2] gap; posting is a persisted state change whose result is not visible in place until the panel re-renders. | §3.9 `[L-9]`, [BR-34] |
| `[RTO-WFX-8]` | Demo-data inconsistencies: `#crow4` belongs to the **JIT** row and `#crow5` to the **MKT** row, so the panel ids run out of document order; and the same seeded comment is rendered as `Please double-check the ×5 quantity.` (inline panel, trailing period) and `@Yongwon Please double-check the ×5 quantity` (hub, no period). | A QA agent asserting "panel id order == row order" or comparing the two renderings will file false bugs. Declared here so the strings below are trusted as-is. | §8.10, §8.11 |

**Demo limitations that are NOT defects** (per `_wireframe-fixes.md` §E — QA must tag these `[ADMIN]`, never file them as bugs): the wireframe does not lock the bulk buttons while a batch runs; it does not recompute the tiles/counts after row or selection changes; `Refresh` is inert; `Mark all read` is inert; `.printbtn` is inert; `Post` is inert; Bulk Outbound does not actually reload the page. Also **not** a defect: the browser `<title>` and the demo `wf-bar` heading spell `Outbounded` correctly while the admin surface preserves `Outbonded` — the wf-bar is wireframe chrome, not product UI `[L-F1]`. Also **not** a defect: **legend item 7 quotes the superseded badge wording** (`wording changed from "JIT (channel) completed" on 2026-08-03 …`). A dated changelog entry cannot record a rename without naming the string it replaced, and the legend is annotation chrome that ships in no admin build (QA-F-09). The [BR-4] "must not appear anywhere" rule is scoped to the **shipping surface** — see §4.2 and QA-L7-02.

**Wireframe timing artifact (not a defect, but QA must know it).** The demo script sets `#pfill.style.width='0%'` **synchronously** on click but rewrites `#pbarLabel` only inside the 250 ms `setInterval` callback, so for the opening ~250 ms of every run the label still carries the **previous** action's copy — including its mode string. Every "during the run" assertion in §8 is therefore valid only from the first tick onward; the reading rule is stated in §8.0 and the underlying wireframe issue is registered as **`[RTO-WFX-9]`** in `_wireframe-fixes.md` §B.

---

## 3. Functional Specification

Conventions used throughout this section: **Trigger → Behavior → Inputs/Outputs → Validation → Server action → State transitions → Idempotency → User-visible feedback.** Exact UI strings are quoted byte-accurately from the wireframe; strings that this spec *defines* because the wireframe has no copy are marked **(spec-defined)**. Endpoint names, key formats, and debounce intervals are developer decisions [G-9]; the *contract* is not.

### 3.1 `[L-1]` — Selection model and bulk-button counts

**Trigger.** Any change to a row checkbox, the `Select all` control, or the active view tab.

**Elements.** A `Select all` checkbox in the bulk bar (`label` text `Select all`), a checkbox in the table header cell, one checkbox per order row, and the trailing counter `3 selected` (`.bulkbar .cnt`).

**Behavior.**

1. **One selection state, two select-all controls.** The header-cell checkbox and the bulk-bar `Select all` checkbox are two views over the *same* boolean and must stay in sync in both directions. Checking either checks the other. Resolving this is required because the wireframe ships both with no stated relationship `[RTO-WFX-1]`.
2. **Select-all scope = currently visible (filtered) rows only** `[PD-38 · OWNER-PENDING]`. On the `Marketing` tab, `Select all` selects `MKT-40233` and nothing else. Selecting rows the operator cannot see is the classic bulk-action accident.
3. **Per-order selection persists across view-tab switches** `[PD-38 · OWNER-PENDING]`. Selecting three Inventory rows, switching to `JIT`, and switching back leaves those three selected. Switching tabs is a filter, not a reset.
4. **Select-all state is derived, never stored.** After a tab switch, `Select all` renders checked only if *every currently visible row* is selected, indeterminate if some are, unchecked if none are. **Clicking it when it is indeterminate selects the remaining visible rows; it never deselects** [E-50]. Clicking it when it is fully checked clears the visible set only, leaving off-tab selections intact.
5. **Counts recompute synchronously on every selection change** and drive four labels at once:
   - `[L-2]` `🖨 Print Pick Locations ({orders} orders · {items} items)`
   - `[L-3]` `🖨 Bulk Print Labels ({orders} orders)`
   - `[L-4]` `📦 Bulk Outbound ({orders} orders)`
   - `.bulkbar .cnt` → `{orders} selected`
   All four count **every selected order across all tabs**, not only the visible ones — the batch acts on the selection, so the labels must describe the selection.
6. **Item count semantics.** `{items}` is the sum of **all units of every selected order**, identical to the sum of the selected rows' `Total Items` badges — *not* only the inbounded units `[PD-37 · OWNER-PENDING]` [BR-16]. Precedent: `MKT-40233` displays `Total Items 3` while one of its two lines is not inbounded.
7. **Zero selection.** All three bulk buttons are **disabled** (not hidden, not silently no-op). `.cnt` reads `0 selected`; `[L-2]` reads `🖨 Print Pick Locations (0 orders · 0 items)`. Disabled styling is a developer decision; the disabled *state* is not.

**Inputs.** Client-held set of order IDs. **Outputs.** Button labels, counter text, select-all tri-state.

**Validation.** A row whose order has left the ready pool since load (outbounded, cancelled, all lines cancel-inbounded elsewhere) remains rendered and remains selected until `Refresh` or a bulk action; the server rejects it at execute time [BR-28] `[PD-6 · OWNER-PENDING]` [E-51], and it is never silently dropped from the client set.

**Server action.** None. Selection is client-local.

**Idempotency.** N/A.

**Data capture.** Individual checkbox toggles are an explicit **NON-event** `[NE-1]`; the *resolved selection set* is embedded in the payload of every bulk event (DC-5, DC-6, DC-8) [DC-18].

**Feedback.** Label text updates only; no toast for selection [BR-34].

**Wireframe delta.** `[RTO-WFX-1]` — in the live wireframe all checkboxes are inert and the counts are static (`3 orders · 8 items`, `3 selected`). QA asserts the *static* strings today and the *dynamic* behavior against the real admin.

---

### 3.2 `[L-2]` — Print Pick Locations

**Trigger.** Click `🖨 Print Pick Locations ({orders} orders · {items} items)`.

**Behavior.** Opens modal `[L-M1]` populated from the current selection. **This button does not print.** Printing happens from the modal's own `🖨 Print`. The two-step shape is deliberate: the picking list is the one artifact the operator visually verifies before committing paper, because a wrong picking list sends a person on a wrong walk.

**Inputs.** Selected order IDs. **Outputs.** Modal with header totals, aggregated pick table, note block.

**Validation.** Disabled at zero selection [E-1]; therefore the `0 orders selected · 0 SKUs · 0 units total` header is unreachable through the UI [E-25].

**Server action.** Modal content may be composed client-side from already-loaded rows **or** fetched fresh. If fetched, a mismatch against the loaded rows must re-render the table rather than warn [BR-28].

**State transitions.** None. No order state changes when the modal opens.

**Idempotency.** N/A (read-only).

**Feedback.** Modal appears; no toast, no sound [BR-34].

---

### 3.3 `[L-3]` — Bulk Print Labels

**Trigger.** Click `🖨 Bulk Print Labels ({orders} orders)`.

**Behavior.**

1. Client debounces the click; the three bulk buttons and the M1 `🖨 Print` lock for the duration of the batch [BR-18] [E-19]. `Refresh` is also locked [E-57].
2. The server fans out one label job per selected order, each resolved to that order's own carrier — Deleo, YUN, or any carrier added later. **Carrier resolution is per order, never per batch** — this is the page delta on [G-4]; a single batch may emit two carriers' templates.
3. Each job is pushed to the local print agent's printer queue per [G-4].
4. Progress reports through the shared bar `[L-5]` with mode text `No refresh · selection kept`.
5. On completion: green toast `✓ Bulk Print Labels complete — {N} orders` [G-2].
6. **The page does not refresh and the selection is preserved** — this is what makes the three-beat wave possible [BR-8].

**Inputs.** `{ orderIds[], idempotencyKey }`. **Outputs.** Per-order label job results; toast.

**Validation.** Disabled at zero selection. Orders that left the ready pool since load are revalidated server-side and rejected `[PD-6 · OWNER-PENDING]`. An order with **no carrier assigned** (the "Not connected — contact the Fulfillment Center" state) cannot produce a label: it is excluded from the batch, reported in the toast subtext, and persisted with `no_carrier` [E-61] — unblocking such an order is **manual coordination: contact the fulfillment person in charge via Slack** (`[PD-55]` owner-decided 2026-08-03); v1 ships no in-admin release UI (§9.2 OQ-2, resolved).

**Exclusion subtext (spec-defined), reason-aware.** The Bulk Print Labels toast uses the same shape as `[L-4]`'s (§3.4 step 6) over the [DC-28] refusal enum, in this fixed order: `no_carrier` → `no carrier assigned`; `no_template` → `no label template`; `order_not_printable` → `order not printable`. One reason across all exclusions ⇒ `{n} excluded — {phrase}` (e.g. `1 excluded — no carrier assigned`); two or more ⇒ `{n} excluded — {a} {phrase A} · {b} {phrase B}`. Clause counts are **not pluralised** [BR-35]. With zero exclusions the subtext keeps the wireframe copy `Disappears automatically after a few seconds`.

**Server action.** Batch label dispatch. Chunk size and job polling are developer decisions.

**State transitions.** **None.** Printing a label never changes order status and never gates outbound [BR-33]. Reprinting is always allowed [BR-32] [E-29].

**Idempotency.** One idempotency key per batch **and** one per order-label job, so a retried batch after a lost response does not double-print [G-9] [E-10]. The known current-admin double-click bug must be fixed, not reproduced [BR-13].

**Infrastructure failure.** Print agent offline or printer unreachable does **not** turn the completion UI into a failure UI [BR-9]. It raises a **separate red toast** and the affected orders stay in the list `[PD-34 · OWNER-PENDING]`; every job result is persisted regardless [DC-6] [DC-12] [DC-24].

**Feedback.** Progress bar → green toast. **No send sound** — this is not an outbound-class button [G-3a].

---

### 3.4 `[L-4]` — Bulk Outbound

**Trigger.** Click `📦 Bulk Outbound ({orders} orders)`.

**Behavior.**

1. **Send sound fires on click**, at execution start, before the batch resolves [G-3a] `[PD-2 · OWNER-PENDING]`. The wireframe's `sndOutbound()` is the reference implementation: a sine sweep 340 Hz → 940 Hz over 0.16 s with an exponential gain envelope, plus a 1250 Hz triangle ping at +0.14 s, total ~0.36 s. Exact synth parameters are a developer decision [G-3]; the *class* of feedback is not.
2. Audio failure is swallowed. A blocked, suspended, or unavailable `AudioContext` must never prevent, delay, or abort the outbound [E-24] [E-49]. The wireframe's `try{…}catch(e){}` wrapper is normative.
3. Buttons lock; the shared progress bar runs with mode text `refreshes after completion`.
4. **Eligibility filter runs server-side before execution** `[PD-35 · OWNER-PENDING]` [BR-15]:
   - Orders where **every** line is `INBOUNDED` → eligible.
   - Orders with **any** non-`INBOUNDED` line (including `MKT-40233`, whose second line shows the amber `Not inbounded` pill) → **auto-excluded**, never partially outbounded.
   - Fully-inbounded **JIT** orders → **eligible**. Their yellow tint means "nobody clicked Outbound yet", not "do not ship".
   - Orders whose status forbids outbound (`on-hold`, `refunded`, `failed`, `completed`, `shipped`, `prepare-shipment`) → **auto-excluded**, mirroring the Order Detail gate `[PD-29 · OWNER-PENDING]` [E-33] [E-34].
   - Orders with zero line items → **auto-excluded** with `empty_order` [E-60].
   - Orders with **no carrier assigned** (the "Not connected — contact the Fulfillment Center" state set by the Order Management import) → **eligible**. A missing carrier refuses the *label*, never the outbound [E-61]: `no_carrier` is a [DC-28] refusal reason and is deliberately **absent** from the [DC-21] `exclusion_reason` enum, so such an order outbounds like any other — it is not excluded, it writes no [DC-21] record, and it contributes no clause to the completion-toast subtext (step 6). The goods can leave the building before the carrier record resolves. **Where the operator sees the missing carrier at all:** only on the label beat of the same wave — the Bulk Print Labels toast subtext `1 excluded — no carrier assigned` (§3.3), or for a single row the `🖨` red toast; both persist [DC-28]. No Slack alert is raised (§6.1), and unblocking stays manual coordination with the fulfillment person in charge (`[PD-55]` owner-decided 2026-08-03, §9.2 OQ-2). `order-detail.md` `[E-86]` disables its own `📦 Outbound` control on this same state — recorded as open cross-page conflict `[RTO-X-1]`, §9.5.
   - Every exclusion is persisted with its reason [DC-21] and counted in the toast subtext.
5. For each eligible order the server, atomically per order:
   - transitions the **order status to `prepare-shipment`** — the single status Closing treats as normal, and the exact state that Cancel Outbound rolls back to `prepare-shipment → processing` `[PD-26 · OWNER-PENDING]` [BR-22];
   - records every shipped line (`sku`, `qty`, `location`) inside the order-level outbound event [DC-9]. **Outbound is order-level and writes no line-level status.** The line vocabulary stays exactly `INBOUNDED` / `PENDING` — the set `view-orders.md` `[L-S1b-21]` and `order-detail.md` `[L-10]` render exhaustively — so a third value would make every Order Detail row of a shipped order render an unmapped status, and it is also what keeps Cancel Outbound's "touches no line-level inbound state" contract (`order-detail.md` BR-19, `view-orders.md` `[L-S3-2]`) true. Corrected 2026-08-03; §10 [BR-22];
   - decrements on-hand stock at each line's location and consumes the corresponding reservation [DC-10] [DC-20];
   - clears the temporary shelf value if one is set, capturing old→new `[PD-18 · OWNER-PENDING]`.
6. On completion: green toast `✓ Bulk Outbound complete — {N} orders`, where `{N}` is the number of orders **actually outbounded**, not the number selected.
   - **`{N}` is never pluralised.** The literal template is `— {N} orders` for every value of `{N}`, including `1` and `0`. This is pinned because the wireframe's own template is unpluralised and because `Found N order(s)` [L-F3] uses a *different*, equally verbatim form; a developer must not harmonise the two [E-54].
   - If any order was excluded, the subtext slot carries a **reason-aware** exclusion line **(spec-defined)** `[PD-35 · OWNER-PENDING]`. The phrase per [DC-21] `exclusion_reason` is fixed: `lines_not_inbounded` → `items not inbounded` · `status_forbids_outbound` → `status blocks outbound` · `already_outbounded` → `already outbounded` · `left_ready_pool` → `no longer ready` · `empty_order` → `no line items`. When every exclusion shares one reason the subtext is `{n} excluded — {phrase}` (e.g. `2 excluded — items not inbounded`); when two or more reasons are present it is `{n} excluded — {a} {phrase A} · {b} {phrase B} …` with the clauses in the enum order just listed (e.g. `2 excluded — 1 items not inbounded · 1 status blocks outbound`). Clause counts are **not pluralised**, exactly like `{N}` [BR-35]. One hard-coded `items not inbounded` for all five reasons is forbidden: it sends the operator hunting for a receiving problem when the real cause is a hold they could release in one click. With zero exclusions the subtext keeps the wireframe copy `Disappears automatically after a few seconds`.
   - If **every** selected order was excluded, the toast still renders as `✓ Bulk Outbound complete — 0 orders` with the exclusion subtext; it is not suppressed and not recoloured. Nothing shipped, nothing was written, and the operator is told exactly that [E-53].
7. **The page then refreshes.** This is the **sole designed exception** named in [G-2], established 2026-07-09 and deliberately kept through every subsequent rework. Ordering is fixed: sound → progress → toast → refresh, and the toast must survive the refresh (re-rendered after reload) so the operator who looked up late still sees the result [E-37]. Outbounded orders are gone from the list after the refresh; the selection is cleared.

**Inputs.** `{ orderIds[], idempotencyKey }`. **Outputs.** Per-order results, batch envelope, toast, refreshed list.

**Validation.** Disabled at zero selection. Server revalidates every order at commit; stale orders are rejected without partial writes `[PD-6 · OWNER-PENDING]` [E-7]. Two operators submitting overlapping selections concurrently: each order outbounds exactly once; the losing batch receives a conflict result for the overlapping IDs and a non-green toast `[PD-7 · OWNER-PENDING]` [E-8] [DC-23].

**Idempotency.** Batch-level key plus per-order keys [G-9]. A retried batch after a lost response must not double-outbound and must not double-decrement stock [E-10]. Rejected duplicates are persisted [DC-11].

**Feedback.** Sound + progress + toast + refresh. Failure of the **notification** side effects (Slack, sheet) never rolls back the outbound `[PD-4 · OWNER-PENDING]` [BR-30].

---

### 3.5 `[L-5]` — Shared progress bar

**Trigger.** Start of any of the three batch actions (`[L-3]`, `[L-4]`, and `[L-M1]`'s `🖨 Print`).

**Behavior.**

- **One bar, one instance, shared by all three actions.** There is never a second bar.
- The label (`#pbarLabel`) states, in order: the action name, `in progress`, the percentage, the **mode**, and `toast on completion`. Wireframe-canonical pattern: `{Action} in progress — {p}% · {mode} · toast on completion`.
- **Mode string is the contract**, not decoration:
  - `Print Pick Locations` and `Bulk Print Labels` → `No refresh · selection kept`
  - `Bulk Outbound` → `refreshes after completion`
  This is how the operator learns, mid-run, whether their selection is about to disappear.
- Progress runs 0 → 100 monotonically, including across chunk boundaries. Granularity (per-order increments vs smoothed percentage) and chunk size are developer decisions [E-22].
- **Concurrent-start lockout.** While a batch runs, all three bulk buttons, the M1 `🖨 Print`, and `Refresh` are disabled [BR-18] [E-19] [E-57]. Keyboard activation (Enter/Space) is subject to the same lock [E-62]. The wireframe does not implement the lockout — an `[ADMIN]`-only assertion.
- At rest (no batch running) the bar shows the last completed run or an idle state; the wireframe ships a static 60 % fill with the label `Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion` as a demo snapshot. **That literal `3/5` fraction appears in no other state and is demo copy only** — the live pattern uses a percentage.

**Data capture.** Progress ticks are a **NON-event** `[NE-2]`; batch start and completion are persisted [DC-8] [DC-9] [DC-10].

---

### 3.6 `[L-6]` — Completion toast

**Trigger.** Any batch reaching 100 %.

**Behavior.**

- Top-right toast [G-2], green, auto-dismissing after a few seconds (wireframe: 3000 ms; exact duration is a developer decision).
- **Exact success text:** `✓ {Action} complete — {N} orders`, where `{Action}` is one of `Print Pick Locations`, `Bulk Print Labels`, `Bulk Outbound`, and `{N}` is unpluralised [E-54].
- Subtext slot: `Disappears automatically after a few seconds` by default; **replaced** — never appended to — by the reason-aware exclusion line when Bulk Outbound excluded orders (§3.4 step 6) or when Bulk Print Labels refused orders (§3.3) `[PD-35 · OWNER-PENDING]`.
- **No failure case in the completion UI** [BR-9]. This was decided on 2026-07-22 and is deliberately kept: the completion toast is an all-success artifact.
- **Boundary against [G-4] failure surfacing** (adjudication C-9): infrastructure failures — print agent offline, printer unreachable, stale order rejected — do not corrupt the completion toast. They raise a **separate red toast**, the affected orders remain in the list, and per-order results are persisted regardless `[PD-34 · OWNER-PENDING]` [DC-16] [DC-24]. The all-success promise applies to the *completion notice*, not to the system's honesty about work that did not happen. When both fire, the red toast wins the slot and the green toast is rendered first and replaced [E-79].
- **Single-slot replacement.** Consecutive actions replace the toast rather than stacking [E-18]; stacking vs replacement is a developer decision, but the wireframe behavior (single slot) is the default.

---

### 3.7 `[L-7]` — JIT row: `Fully Inbounded`

**Condition (all three must hold).** The order's sourcing route is **JIT** [G-5] ∧ every line is `INBOUNDED` ∧ the order has not been outbounded.

**Rendering.**

- Row tint: yellow (`.row-jit`, `--jit-soft #FFFBD6`).
- Badge immediately after the Order ID: `Fully Inbounded` (amber background). **Exact string.** The former wording `JIT (channel) completed` **must not appear anywhere** — it was renamed on 2026-08-03 because a route-shaped label clashed with the colorless black-bold Sourcing Route text mandated by [G-5] [BR-4].
- Pick Locations cell shows the staging shelf, e.g. `Shelf 3`, not a rack code — JIT goods are staged on arrival, not put away into rack locations [L-12].
- **Always sorted to the bottom** of the list regardless of order date [BR-2]. Rationale: the picker's rack walk covers warehouse stock; JIT items are a separate, shorter trip to the staging shelves. Interleaving them doubles the walk.

**Eligibility.** Fully-inbounded JIT rows **are** eligible for Bulk Outbound `[PD-35 · OWNER-PENDING]` — they are complete and merely awaiting the click.

**Classification precedence.** An order that is both MKT-imported and JIT-sourced renders as **MKT** (tint, badge, tab, sort group), because the MKT origin governs settlement separation while the JIT route only governs where the goods physically sit; its Pick Locations cell still shows `Shelf N` [E-70].

**Data capture.** The moment the last line became `INBOUNDED` is persisted [DC-15], which is what makes "how long do finished JIT orders sit unshipped?" answerable.

---

### 3.8 `[L-8]` — Marketing (MKT) row

**Condition.** Order created by the Order Management manual import (MKT- number series).

**Rendering.**

- Row tint: purple (`.row-mkt`, `--mkt-soft #F3EEFF`).
- Badge after the Order ID: `MKT`.
- Customer cell carries a second line `PIC: {name}` (wireframe: `PIC: Harshit`), sourced from the import. PIC resolves to a system user `[PD-33 · OWNER-PENDING]`; if unset, render an explicit `PIC: —` rather than an empty line [E-42]; if the user was deactivated, render the stored display name unchanged plus a neutral marker rather than dropping the line [E-71].
- Sorted **between** regular Ready orders and JIT orders [BR-2].

**Visibility rule (page-level exception).** MKT orders appear **immediately on import, regardless of stock or inbound status** [BR-3] — this is the one documented exception to the "≥1 INBOUNDED line" inclusion rule [BR-1]. Decided 2026-07-23; this **reversed** the original planning text requiring an import-time stock error when the product is not in the warehouse (struck through in the planning doc). Import first, inbound later is now the supported order of operations.

**Not-inbounded lines.** Each line without inbound shows the amber pill `Not inbounded` in the Pick Locations column instead of a location [L-12]. The pill is a locator substitute, never a blank cell [BR-23].

**Bulk Outbound.** An MKT order with any non-inbounded line is auto-excluded from the batch and reported in the toast subtext `[PD-35 · OWNER-PENDING]` [E-3] [E-21].

**Merging.** Merging an MKT order with a regular sales order is blocked on Order Management `[PD-59 · OWNER-PENDING]`; nothing on this page may create such a mix. If a selected order was merged away on Order Management between load and execute, the batch rejects it as stale [E-59].

---

### 3.9 `[L-9]` — Per-row inline comments

Deltas over [G-7] only.

**Trigger.** Click the row's `💬` button (`.cmtbtn`); an unread count renders as a red superscript badge on the button (rows `422221` and `422165` show `1`).

**Behavior.**

- Expands an **inline panel as a table row directly under the order row** — no navigation, no modal. The packer reads a VIP or care note without leaving the wave.
- Panel content: existing comments as `{author} {@mention} {text} {time} {★}`, newest at the bottom, plus a write row.
- **Exact placeholder strings** (they are part of the contract because they are how the operator learns that @mention notifies Slack):
  - `#crow1`: `Write a comment — @mention sends an automatic Slack notification (order no. · text · time · author)`
  - `#crow2`…`#crow5`: `Write a comment — @mention sends an automatic Slack notification`
  The real admin uses the **long form everywhere**; the short form is a wireframe abbreviation.
- Empty state: `No comments yet` in muted text.
- `Post` button (blue, small). Empty or whitespace-only comment: **blocked**, no server call [E-16].
- On a successful post the comment is appended to the panel in place **and** a green toast `✓ Comment posted` **(spec-defined)** confirms it [G-2] [BR-34]. The wireframe does neither — `[RTO-WFX-7]`.
- Comment bodies are **rendered as text, never as markup**. A comment containing `<script>` or any HTML is escaped in the inline panel, in the hub list, and in search highlighting [E-74].
- Comment mutability follows [G-7] `[PD-3 · OWNER-PENDING]`: corrections are posted as new comments.
- `★` toggles saved state for the current user [DC-3]. The filled star is the confirmation; no toast [BR-34].
- **Panels collapse when the view tab changes** (wireframe behavior, normative) [E-17].
- A comment posted from here is the same entity as one posted from Order Detail or the hub; only `source` differs [E-45].
- A comment may be posted on an order in any status, including one that has left the ready pool [E-43] [E-77].

**@mention.** Routes to Slack per §6.1. Delivery failure never blocks the post `[PD-4 · OWNER-PENDING]`; the comment persists and delivery is retried [DC-2]. Mentioning an unknown or deactivated user produces defined inline feedback and no Slack send [E-16] [E-39]. **One Slack message per distinct resolved mention**: a comment naming three different people produces three messages; the same person named twice in one body produces one [E-75]. This is [G-7]'s corpus-wide contract — its payload field is a single mentioned user, and `order-detail.md` §6.1 and `view-orders.md` `DC-20` implement it per user. Corrected here 2026-08-03 from an earlier "one message naming everyone" reading; §10.

**Refresh interaction.** Bulk Outbound refreshes the page and therefore discards an unposted draft [E-20]. The chosen mitigation is a developer decision (warn-on-unload or preserve-draft); the *behavior must be documented in the build*, not left to chance.

---

### 3.10 `[L-10]` — Comments hub

Deltas over [G-7] only. The hub is identical on all eight screens; only the entry points differ.

**Trigger.** Click `💬 Comments` in the global nav (`.icon-btn[data-open="inbox1"]`). Badge = unread mention count (wireframe: `2`).

**Behavior.**

- Dropdown anchored top-right; **closes on outside click**, stays open on clicks inside (normative).
- Two tabs: `@ Mentions` (with its own count badge) and `★ Saved`.
- Mentions pane header: `Comments mentioning me · Click to open the order` (`[G-7]` HUB-1) with a right-aligned `Mark all read` action (HUB-4) [DC-4]. On use it shows the green toast `✓ All mentions marked as read` **(spec-defined)** because the change spans rows the operator may not be looking at [G-2] [BR-34]. (Inert in the wireframe — `[ADMIN]`.)
- Saved pane header: `Saved comments · Click to open the order` (`[G-7]` HUB-2) with `Unstar to remove from the list` (HUB-3). *(All seven hub strings on this page already matched the `[G-7]` v1.2 canonical set published 2026-08-03 — no edit was needed here.)*
- **Full-text search across ALL comments** — not a filter within the active tab. Placeholder: `🔍 Search all comments — order no. · author · text`. Typing hides the tab bar and renders a results pane headed `{n} results · newest first · click to open the order`; clearing the box restores the previously active tab. Matches are highlighted (`<mark>`, purple). Ordering is **newest first**. Empty result: `No matching comments`. A whitespace-only query is treated as empty and restores the tabs.
- Search scope spans orders that are **not** in the current ready list (the wireframe's seed data includes `422108` and `421990`, neither of which is a table row) [E-38]. Clicking such a result still navigates to that order.
- Click on any hub entry opens the order (Order Detail) [G-12].
- Unread counts on the hub badge and on per-row `💬` badges must reconcile after any read action [E-26].
- If the hub is open when the Bulk Outbound refresh fires, it closes with the reload; unread state is server-held so nothing is lost [E-76].

**Data capture.** Search queries are read-only telemetry [DC-17], not a [G-8] state change; logging them is a developer decision.

---

### 3.11 `[L-11]` — Reduced side padding

Full-width layout (`.pagepad` = `16px 14px 0`), matching View Orders. Rationale: the table carries 9 columns including two stacked-content columns (Ready Item Details, Pick Locations); default page gutters push the Pick Locations column off the visible area at 1240–1440 px, which is the width the desk operator actually has. The table's container (`.mockwrap`) scrolls horizontally below the 1240 px minimum rather than dropping or wrapping columns [E-73]. Cosmetic rule with no data events.

---

### 3.12 `[L-12]` — Pick Locations column

**Position.** Seventh column, immediately right of *Ready Item Details*.

**Alignment contract (load-bearing).** Each locator line renders at the **same vertical eye level** as its corresponding item line. Row `422165` has two item lines and two location lines; the first location belongs to the first item. This 1:1 vertical pairing is the whole point of the column — a picker scanning across the row must not have to count lines to match a product to a shelf. Implementations must not sort, deduplicate, or collapse the locator list independently of the item list [E-15b].

**Cell variants** [BR-23]:

| Variant | Renders | When |
|---|---|---|
| Rack location | `.locpill` with the location code, e.g. `A-02-13` | Warehouse stock, one location per SKU [G-14] `[PD-46 · OWNER-PENDING]` |
| Staging shelf | `.locpill` with `Shelf N`, e.g. `Shelf 3` | Fully-inbounded JIT goods staged on arrival |
| Not inbounded | Amber `.locpill` (`--amber-soft` background, `--amber-line` border, `--amber` text) reading `Not inbounded` | MKT (or any) line without inbound |
| Unknown | Explicit fallback marker (developer-chosen glyph or `—`) plus the line remaining visible | Location deleted or unassigned in Inventory [E-15]; JIT staged with no shelf recorded [E-41]. **Never render blank** — a blank cell reads as "no pick needed". |

**Removed column.** The former *Ready Items* column was removed on 2026-07-22 as a duplicate of *Total Items* and **must NOT exist**. Its dead stylesheet class `.cb-ready` still ships `[RTO-WFX-4]` and must be deleted so nobody re-implements it.

---

### 3.13 `[L-13]` — Total Items

**Value.** `Σ(quantity)` over **all** line items of the order — the count of physical units to put in the box.

**Not** the number of SKUs. The live admin counted SKUs, so an order for one SKU × 5 units displayed `1`; pickers read `1`, picked one, and the order shipped short. This is the single highest-value change on the page [BR-5] (2026-07-22).

**Mixed orders.** For an order with non-inbounded lines, `Total Items` counts **all** units, not only ready units `[PD-37 · OWNER-PENDING]` [BR-16]. Precedent in the wireframe: `MKT-40233` renders `3` (2 inbounded + 1 not inbounded). Rationale: this badge is an order-size indicator for the desk operator, not a pick count — the pick count lives on the picking list, which contains only pickable lines.

**Reconciliation invariants (QA-assertable) — two statements, not one.** They are separated because the page has two legitimate denominators and conflating them would put non-inbounded units on the picker's paper:

- **(a) Unconditional.** `Σ(Total Items of selected rows)` **always equals** the `{items}` figure in the `[L-2]` button label. Both count **all** units of every selected order `[PD-37 · OWNER-PENDING]` [BR-16].
- **(b) Conditional.** The `{units}` figure in the M1 header equals `Σ(qty of pickable — i.e. inbounded — lines only)` §3.15. It equals `{items}` **only when every selected order is fully inbounded**; otherwise it is lower by exactly the selected non-inbounded unit count. Since [BR-3] makes partially-inbounded MKT orders a routine member of the pool, that divergence is a **normal state, never a defect**.

Wireframe (default selection, all three orders fully inbounded, so both statements coincide): rows `5 + 1 + 2 = 8` = `(3 orders · 8 items)` = `8 units total`. Worked divergent case: adding `MKT-40233` (Total Items `3`, one line not inbounded) gives `{items} = 11` and `{units} = 10`. Both statements hold even in the presence of a defective zero/negative-quantity line [E-46].

**Rendering.** Grey `.cntbadge.cb-total` pill, tabular numerals.

---

### 3.14 `[L-14]` — View tabs

**Tabs.** `All` (default, active on load) · `Inventory` · `Marketing` · `JIT`, each with a parenthesised count.

**Filter predicates:**

| Tab | Shows |
|---|---|
| All | every ready order |
| Inventory | warehouse-stock ready orders (regular, non-MKT, non-JIT) |
| Marketing | manually imported MKT orders |
| JIT | JIT orders with every line inbounded and Outbound not yet clicked |

The four predicates are **mutually exclusive and exhaustive** over the pool — `Inventory + Marketing + JIT` always equals `All`, which is why the wireframe reads `3 + 1 + 1 = 5`. Classification precedence when an order matches two routes is fixed in `[L-7]` [E-70].

**Behavior.**

- Exactly one tab is active (`.vtab.on`, dark fill).
- Switching rewrites `[L-F3]`: `Found {n} order(s) with items ready for outbound`, where `{n}` is the **visible** row count.
- **All expanded inline comment panels collapse** on switch (normative wireframe behavior) [E-17].
- Selection persists per order across switches; `Select all` scope follows the visible set `[PD-38 · OWNER-PENDING]` [E-2].
- Tab counts in the labels must recompute from the same source as the rows; a tab whose count is `0` still renders and shows an empty table with `Found 0 order(s) with items ready for outbound` [E-5].
- Tab switching is locked while a batch runs, like every other control [E-52] [BR-18]; the filter is client-side but a mid-batch reflow would desynchronise the row set the operator is watching.
- Tab switching is a **NON-event** for [G-8] purposes `[NE-3]`; optional telemetry only [DC-17].

---

### 3.15 `[L-M1]` — Picking List modal

**Title bar.** `Print Pick Locations — Picking List ({orders} orders selected · {skus} SKUs · {units} units total)` with a `✕` close button inside the same `<header>` element (so a naive `textContent` read returns the title **plus** `✕` — QA must read the header's first text node).

**Header figures — all three defined:**

| Figure | Definition |
|---|---|
| `{orders}` | The number of selected orders, identical to the `{orders}` in the `[L-2]` button label. |
| `{skus}` | The count of **distinct SKUs** across the pickable lines of the selection — **not** the row count. Because the same SKU in two orders produces **two** rows and no merge [BR-19] [E-14], `{skus}` ≤ the number of table rows, and the two diverge exactly when a SKU is shared. Wireframe: 4 rows, 4 distinct SKUs, so both readings coincide there and the ambiguity had to be pinned here instead. |
| `{units}` | `Σ(qty)` over the **pickable (inbounded) lines only** — the same set the table renders. It equals the `{items}` figure in `[L-2]` only when every selected order is fully inbounded; see §3.13 invariant (b). |

**Table columns.** `Location · SKU · Product · Qty · Order`.

**Row generation.**

- **One row per order × SKU. No cross-order merge** [BR-19]. Two orders needing the same SKU from the same location produce **two** rows, because the `Order` column would otherwise be ambiguous and the picker could not split the pick between the two boxes [E-14].
- Only **pickable** lines appear: lines that are not inbounded have no location and are excluded from the picking list (they are already reported on the row as the amber `Not inbounded` pill) [E-3].
- `Qty` renders **bold** when greater than 1 — the anti-under-picking affordance. Non-positive quantities are rendered and flagged, never hidden [E-46].

**Sort — the route rule** [BR-7] [BR-20]:

1. All rack-coded locations first, ascending lexicographically (`A-02-13` → `A-03-02` → `B-01-07` → `B-02-11`).
2. Then the `Shelf N` group, ascending numerically by `N`.
3. **Ties break on order id ascending, then SKU ascending**, so that reprinting the same selection produces a byte-identical list [E-65].

Rack locations are walked as one pass; the staging shelves are a separate short trip at the end. A selection consisting only of JIT orders yields a list entirely inside group 2 and is still deterministic [E-64]. The comparator detail is a developer decision; the **two-group ordering and the tie-break** are not.

**Product name.** Korean product name with the **EN brand in bold** [G-6] [BR-6]. The wireframe renders M1 product cells without the brand prefix, and renders order `422221` with an elided English name — defect `[RTO-WFX-5]`; the specified behavior is brand-prefixed Korean, identical to *Ready Item Details*.

**Sample lines.** Internal picking artifacts render the sample as a single **"sample set"** line per [G-13] `[PD-36 · OWNER-PENDING]` [BR-21] — **v1: "sample set" only**, no sample type and no per-type quantity (`[PD-51]` owner-decided 2026-08-03; distinguishing which sample and how many is follow-up work for when sample types are introduced). **WF-9 was applied to the wireframe on 2026-08-03** (owner-approved batch): M1 now renders one amber-tinted `sample set` row for order `422165`, carrying a `Sample` marker in place of a location and `×1` as the quantity. `[PD-36]` is thereby settled in the affirmative for the modal; `[PD-51]` fixed the content (the line reads "sample set"). A sample SKU with no registered location follows the unknown-marker rule rather than being dropped [E-66].

**Note block (exact copy).** `Sorted by location (ascending) (A-02-13 → B-01-07 → Shelf 3) — pick everything in one pass along the route. Printing: no refresh · selection kept; progress bar, then a top-right completion toast.`

**Footer actions.**

- `Cancel` (grey) — closes the modal, prints nothing, changes nothing. Explicit **NON-event** `[NE-4]`, and explicitly **no toast**: nothing was confirmed [BR-34].
- `🖨 Print` (blue) — closes the modal **and** starts the batch: instant print via the local agent [G-4], shared progress bar with mode `No refresh · selection kept`, then `✓ Print Pick Locations complete — {N} orders`. **Selection is preserved.**

**Also closes on:** the `✕` button and a click on the overlay backdrop. Backdrop-close prints nothing.

**Snapshot semantics.** The printed list is a **snapshot**. The full line set (location, SKU, Korean name, bold-brand prefix, qty, order, and — once PD-36 lands — sample lines) is persisted with the print event [DC-5] so the exact paper a picker walked with can be reproduced during a dispute; a later product rename does not rewrite the snapshot [E-67]. If the underlying data changed between opening the modal and pressing Print, the server revalidates and re-renders rather than printing silently stale paper [E-30] [E-36] `[PD-6 · OWNER-PENDING]`.

**Stale-selection interaction.** Printing the picking list does not bind the selection. If the operator then changes the selection and presses Bulk Print Labels, labels are produced for the **current** selection, not for the printed snapshot [E-40]. A sample assigned after printing is likewise not on the picker's paper [E-31].

---

### 3.16 `[L-F1]` — Page title

`WMS - Ready to be Outbonded` (page `h2`) and `Ready to be Outbonded Orders` (section `h3`). **The misspelling "Outbonded" is intentional and preserved** — it is the live admin's own spelling, and matching it prevents operators from believing they are on a different screen. Recorded as an explicit non-fix in `_wireframe-fixes.md` §E. Do not correct it. The browser `<title>` and the demo `wf-bar` heading use the corrected spelling `Outbounded`; that is wireframe chrome and is not part of the admin surface.

### 3.17 `[L-F2]` — Refresh

Blue `Refresh` button at the right of the section heading row. Re-queries the dedicated `readyToBeOutbonded` list source and re-renders the table. Poll cadence vs manual-only is a developer decision [D-6]. Refresh behavior for **selection** and **open comment panels** must be chosen and documented [E-6]; the recommended default is: selection preserved for orders still present, dropped for orders that left the pool, open panels collapsed. `Refresh` is locked while a batch runs [E-57]. A refresh persists a list-load snapshot [DC-25]. Inert in the wireframe — `[ADMIN]`.

### 3.18 `[L-F3]` — Found count

`Found {n} order(s) with items ready for outbound` (`#foundTxt`), verbatim from the live admin **including the `order(s)` pluralisation form**, which is deliberately different from the toast's unpluralised `{N} orders` [E-54]. Bound to the visible row count and rewritten on every view-tab switch [L-14].

### 3.19 `[L-F4]` — How to use

Five bullets, verbatim from the live admin:

1. `Click "Refresh" to load the latest orders ready for outbound`
2. `Orders shown here have at least one line item with "INBOUNDED" status` — **normative**: this is the page-inclusion rule [BR-1], with the MKT exception [BR-3].
3. `Click the Order ID link to see full order details and process outbound`
4. `Only items marked as INBOUNDED are ready for outbound processing`
5. `This page uses the dedicated readyToBeOutbonded API for optimized results`

Bullet 3's phrase "and process outbound" describes Order Detail's manual Outbound button, which is **always manual** `[PD-21 · OWNER-PENDING]` — it is not a second bulk path.

### 3.20 `[L-F5]` — Order ID link

The Order ID (`422221`, `MKT-40233`, …) is a link to Order Detail [G-12]. In the wireframe it is a styled `<span class="oid">` with no `href` — defect `[RTO-WFX-3]`. In production it must be a real anchor deep-linking to the specific order (`../order-detail/` in the wireframe corpus; the filtered entity URL in the real admin). It is the **only** navigation affordance on the row, because the Actions column was reduced to Print on 2026-07-22 [BR-12]. A link to an order cancelled or deleted after load must resolve to Order Detail's own missing-entity handling, never a 500 [E-23]; a duplicated order id in the list is a data defect that must not collapse two rows into one link [E-68].

### 3.21 `[L-F6]` — Per-row Print

`🖨` button in the Print column, one per order row (5 in the wireframe). Prints **that order's** shipping label instantly via the local print agent, resolved to that order's carrier [G-4]. This is the reprint path: labels are damaged, mis-stuck, and lost as normal operations, so reprinting is always allowed and always recorded with a reprint sequence number [BR-32] [DC-7] [E-29].

On success it shows the green toast `✓ Label printed — order {orderId}` **(spec-defined)**; on print-agent or printer failure, a red toast naming the agent or printer [G-2] [BR-34]. The wireframe shows neither — `[RTO-WFX-6]`.

Printing never changes order status and never gates outbound [BR-31] [BR-33]. Reprinting does **not** auto-post a comment; the wireframe's seeded `Reprinted the shipping label` comment is a *manual* operator note, not system output. An order with no carrier assigned cannot print and is refused with a red toast [E-61]; unblocking it is manual Slack coordination with the fulfillment person in charge (`[PD-55]` owner-decided 2026-08-03 — no in-admin release UI in v1). Inert in the wireframe — `[ADMIN]`.

### 3.22 `[L-F7]` — Table contract

**Nine columns, fixed order:** `☐ · Order ID · Order Date · Customer · Total Items · Ready Item Details · Pick Locations · Comments · Print`. Columns are never reduced or reordered per view tab, and never dropped at narrow widths — the container scrolls instead [E-73].

**One row per order** [BR-24]. Multi-line orders stack their lines *inside* the Ready Item Details and Pick Locations cells; they never produce multiple table rows.

**Global sort:** regular Ready orders → MKT orders → fully-inbounded JIT orders [BR-2]. Within-group ordering is a developer decision (order date descending recommended) and must be **stable across refreshes**, so that a wave prepared before a background refresh is still the same wave after it [D-6].

**Cell formats:**

| Column | Format |
|---|---|
| Order ID | Link [L-F5], followed by the `MKT` or `Fully Inbounded` badge where applicable |
| Order Date | Rendered in the live admin's own form `2026. 7. 21.` (year, dot, month, dot, day, dot). The value is the order-creation date in the warehouse's local timezone; the field is display-only and is never used as a sort key by itself [E-72] |
| Customer | Customer name; for MKT rows a second muted line `PIC: {name}` [L-8] |
| Total Items | Grey `.cntbadge.cb-total` unit sum [L-13] |
| Ready Item Details | One `.item-line` per line item: `{SKU pill} {**EN brand in bold**} {Korean product name} {×qty pill}` [G-6] [BR-6]. A SKU that no longer resolves in the catalogue renders the stored SKU and name from the order line, never a blank [E-69] |
| Pick Locations | One `.locline` per item line, 1:1 vertically [L-12] |
| Comments | `.cmtbtn` with unread badge [L-9] |
| Print | `.printbtn` [L-F6] |

### 3.23 `[L-F8]` — Nav and identity

The global admin nav and the signed-in user (`Yongwon Ryu` in the wireframe) are the **actor source** for every event in §5 [G-8]; no event on this page may be written with a null or system actor when a person initiated it. Nav item behavior belongs to the admin shell, not to this spec. The `💬 Comments` control in the nav is `[L-10]`. If the session expires mid-batch the server rejects the request rather than attributing it to a stale identity [E-55].

---

## 4. Business Rules

Every rule carries its rationale and its decision date. Reversals are recorded here **and** as dated rows in §10. Global rules are cited, never restated. IDs are page-scoped and are never renumbered; `BR-9b` is a boundary rule attached to `BR-9` and keeps its suffixed id permanently.

| ID | Rule | Rationale | Decided |
|---|---|---|---|
| **BR-1** | An order appears on this page when **at least one line item is `INBOUNDED`**. The source is the dedicated `readyToBeOutbonded` list API. | Matches the live admin's own inclusion rule and the normative How-to bullet; anything narrower would hide partially-picked orders that still need a box. | 2026-07-21 (captured from live admin) |
| **BR-2** | Global sort: **regular Ready → MKT → fully-inbounded JIT (always bottom)**. | Route logic, not aesthetics. Warehouse rack stock is one walk; MKT orders are mixed and often partly un-inbounded; JIT goods sit on staging shelves. Interleaving them makes the picker cross the floor repeatedly. | 2026-07-22 |
| **BR-3** | MKT orders are shown **immediately on import, regardless of stock or inbound status**. Import-time stock validation is **dropped**. | Marketing imports run before goods arrive; blocking the import stranded campaigns. **Reverses** the original planning text ("error if the product is not in the warehouse"), which is struck through in the planning doc. | 2026-07-23 (owner) |
| **BR-4** | The JIT badge reads exactly **`Fully Inbounded`**. The former wording `JIT (channel) completed` must not appear on **any shipping surface** — not in the table, not in a badge, not in the modal, not in printed output. The wireframe's annotation legend is **exempt**: item 7 records the rename by quoting the superseded string, and annotations ship in no admin build (QA-F-09). | A route-shaped badge collided visually with the colorless black-bold Sourcing Route labels [G-5]; operators read it as a route, not a state. Resolved item #11 of the 17-item judgment list. | 2026-08-03 (owner) |
| **BR-5** | `Total Items` = **sum of unit quantities**, never the SKU count. | The live admin's SKU count displayed `1` for a ×5 order; pickers under-picked. This is the page's highest-value correction. | 2026-07-22 |
| **BR-6** | Korean product names in *Ready Item Details* and in the M1 picking list, with the **EN brand in bold** [G-6]. English names remain on order-facing pages. | Pickers match Korean front-of-pack text at the shelf; translating at the shelf is the slow step. | 2026-08-03 (owner) |
| **BR-7** | The picking list is sorted **by location ascending**, so the route is a single pass. | The picker walks with paper, away from the monitor; any other sort order makes them re-cross aisles. | 2026-07-22 |
| **BR-8** | **Print actions never refresh and always preserve the selection. Bulk Outbound refreshes after completion** — the sole designed exception named in [G-2]. | The morning wave is three actions on **one** selection; clearing it between prints would force re-selection and produce divergent sets. The outbound refresh is correct because the outbounded orders must leave the list. | 2026-07-09 (exception established) · 2026-07-22 (reworked) · 2026-08-03 (reconfirmed) |
| **BR-9** | The bulk **completion UI has no failure case** — all-success is the normal path. | Deliberate simplification; failure-state UI was removed from the design. | 2026-07-22 |
| **BR-9b** | Boundary to BR-9: **infrastructure failures surface separately**. Print agent offline, printer unreachable, or an order rejected at revalidation raises a **red toast**, leaves the affected orders in the list, and is always persisted per order. `[PD-34 · OWNER-PENDING]` | Keeps the 2026-07-22 decision intact while refusing to report success for work that did not happen (adjudication C-9). | 2026-08-03 |
| **BR-10** | [G-4] governs all three print surfaces on this page unchanged. Page delta: **carrier resolution is per order, never per batch**. | The packer's hands are on boxes. The per-order delta matters because one batch legitimately mixes Deleo and YUN. Requires a local print agent (developer handoff note B). | 2026-08-03 (reconfirmed) |
| **BR-11** | Bulk Outbound plays the **send sound** [G-3a]. `[PD-2 · OWNER-PENDING]` | Eyes-free confirmation for an operator who fires the batch and turns to the boxes. G-3(a) is written by button class, not by page (adjudication C-5). | 2026-08-03 (owner) |
| **BR-12** | The Actions column contains **Print only**; the former `View Order` button is removed. Order details open through the Order ID link. | Two navigation affordances on one row is one too many at speed. | 2026-07-22 |
| **BR-13** | All three bulk actions and both print paths are **double-click safe**: client debounce **and** server idempotency key [G-9]. | The current admin processes double clicks twice (developer handoff note A). This is a bug to fix, never to reproduce. | 2026-07-21 (logged) |
| **BR-14** | Base structure, column set, page-title spelling `Ready to be Outbonded`, `Refresh`, `Found N order(s)…`, and the How-to block follow the actual admin capture verbatim; only *Ready Items* was removed and *Pick Locations* added. | Operators must recognise the screen. Divergence from the live admin is the change, not the baseline. | 2026-07-21 |
| **BR-15** | **Bulk Outbound eligibility**: orders with any non-`INBOUNDED` line are **auto-excluded** and reported in the toast subtext; fully-inbounded JIT orders **are eligible**; orders in a status that forbids outbound, and orders with zero lines, are excluded. Partial outbound of an order is never performed. `[PD-35 · OWNER-PENDING]` `[PD-29 · OWNER-PENDING]` | Partial outbound ships incomplete boxes; JIT rows are complete and merely awaiting a click. | 2026-08-03 |
| **BR-16** | `Total Items` and the `[L-2]` item count include **all** units of the order, not only inbounded units. `[PD-37 · OWNER-PENDING]` | The badge is an order-size indicator for the desk operator; the pick count lives on the picking list. Wireframe precedent: `MKT-40233` = `3`. | 2026-08-03 |
| **BR-17** | `Select all` applies to **currently visible (filtered) rows only**; per-order selection **persists across tab switches**; an indeterminate `Select all` click adds, never removes. `[PD-38 · OWNER-PENDING]` | Selecting invisible rows is the classic bulk-action accident. | 2026-08-03 |
| **BR-18** | The three bulk actions are **fully independent — no sequence gate** — but **only one may run at a time**. During a run, all three bulk buttons, the M1 `🖨 Print`, `Refresh`, and the view tabs are locked. `[PD-39 · OWNER-PENDING]` | Reprints and re-picks are normal recovery paths; forcing an order would block them. One shared progress bar cannot represent two runs, and a mid-batch filter change desynchronises the row set. | 2026-08-03 |
| **BR-19** | Picking-list rows are **one per order × SKU; no cross-order merge**. | The `Order` column would be ambiguous, and the picker could not split a merged pick between two boxes. | 2026-07-22 (wireframe) |
| **BR-20** | Mixed-location sort: **all rack-coded locations ascending first, then the `Shelf N` group ascending by N**, ties broken by order id then SKU. | Two physically separate areas, one pass each; the tie-break makes a reprint byte-identical to the original. | 2026-07-22 · 2026-08-03 |
| **BR-21** | Internal picking artifacts (M1 and the printed picking list) render a single **"sample set"** line — v1: "sample set" only, no type/qty breakdown (`[PD-51]` owner-decided 2026-08-03) [G-13]. `[PD-36 · OWNER-PENDING]` | The carrier-facing label only appends `(+ sample set)`; the internal line tells the picker a sample set must be picked. Wireframe gap **WF-9** — **applied 2026-08-03**; M1 renders the sample-set row. | 2026-08-03 |
| **BR-22** | Bulk Outbound sets each order's status to **`prepare-shipment`**. The transition is **order-level and writes no line-level status** — the line vocabulary stays exactly `INBOUNDED` / `PENDING`; the shipped lines are recorded inside [DC-9]'s payload (`sku`, `qty`, `location`), not as a new line state. | `prepare-shipment` is the single status Closing treats as normal, and the exact state Cancel Outbound rolls back from `[PD-26 · OWNER-PENDING]`. The **order-level** correction: `view-orders.md` `[L-S1b-21]` and `order-detail.md` `[L-10]` define the line vocabulary exhaustively as `INBOUNDED` / `PENDING`, so an invented `OUTBOUNDED` line value would render unmapped on every Order Detail row of a shipped order, and it would contradict Cancel Outbound's "touches no line-level inbound state" contract (`order-detail.md` BR-19, `view-orders.md` `[L-S3-2]`). | 2026-07-23 (closing rework) · 2026-08-03 · 2026-08-03 (corrected to order-level) |
| **BR-23** | Every Pick Locations line resolves to a visible locator: rack code, `Shelf N`, amber `Not inbounded`, or an explicit unknown marker. **Never blank.** | A blank cell reads as "nothing to pick" and the unit ships short. | 2026-07-22 · 2026-08-03 |
| **BR-24** | **One table row per order.** Multi-line orders stack lines inside the cells. | The page is an order-level batch surface; line-level work happens on View Orders and Order Detail. | 2026-07-22 |
| **BR-25** | **The scanner protocol [G-1] does not apply to this page.** There is no scan input, no focus-retention requirement, and no scan feed. | Stated explicitly so automated QA does not report a missing scanner surface as a defect. | 2026-08-03 |
| **BR-26** | [G-15] applies unchanged. Page delta: **no control here adds a gate of its own**, Bulk Outbound included. `[PD-1 · OWNER-PENDING]` | No role model exists in any input document; inventing per-page gates would create eight inconsistent models. | 2026-08-03 |
| **BR-27** | Comments follow [G-7]'s append-only contract; corrections are new comments. `[PD-3 · OWNER-PENDING]` | The comment corpus is an AI-training and audit asset. | 2026-08-03 |
| **BR-28** | The server **revalidates every order at execute time**; on mismatch it rejects with a red toast and refreshes the affected view. **No partial writes.** `[PD-6 · OWNER-PENDING]` | The list is a snapshot; orders move on other screens while a wave is being prepared. | 2026-08-03 |
| **BR-29** | Concurrency: optimistic version check → `409` → reload the row and show a non-green toast. Each order outbounds **exactly once** across concurrent batches. `[PD-7 · OWNER-PENDING]` | Last-write-wins would double-decrement stock. | 2026-08-03 |
| **BR-30** | Slack (and any notification) failure **never blocks the primary action and never rolls anything back**; it is persisted and retried. `[PD-4 · OWNER-PENDING]` | Notification is a side effect, not part of the transaction. | 2026-08-03 |
| **BR-31** | **Print never gates outbound**, and outbound never requires a prior print. | Blocking goods movement on a printer is a stop-the-line risk (same doctrine as `[PD-19 · OWNER-PENDING]` on View Orders). | 2026-08-03 |
| **BR-32** | **Reprinting is always allowed**, from the row button or Bulk Print Labels, and every print is recorded with a reprint sequence. | Damaged and mis-stuck labels are normal operations, not exceptions. | 2026-08-03 |
| **BR-33** | A reprint does **not** auto-post a comment. Print events are event-only. | The wireframe's `Reprinted the shipping label` is a manual operator note; auto-comments would flood the corpus that [G-7] treats as a training asset. | 2026-08-03 |
| **BR-34** | **[G-2] confirmation surfaces on this page are enumerated, not inferred.** Actions whose result is *not* visible in place — a label leaving a printer the operator is not facing, a comment persisting server-side, a batch completing, a read-state change spanning rows — get a toast. Actions whose result *is* immediately and unambiguously visible in place — the star glyph filling, a panel expanding, a modal opening, a checkbox toggling, `Cancel` — are confirmed by that in-place change and do not additionally toast. Full table below. **Shared boundary with `view-orders.md` BR-51**, stated so the corpus teaches one rule: a **state-changing** action always confirms, and its confirmation may render *in place* (View Orders' `✓ Saved` chip; this page's filling `★`) instead of in the top-right slot — while a pure **view-state** change (panel expand, tab switch, checkbox, modal open, `Cancel`) is not a confirming action at all and has nothing to confirm. That sentence belongs in [G-2] itself; until it lands there, both pages carry it. | [G-2] (owner emphasis) says every confirming action toasts; adjudication C-6 says wireframe omissions are gaps, not decisions. Two omissions are therefore gaps (`[RTO-WFX-6]`, `[RTO-WFX-7]`) and the rest are in-place confirmations. If the owner reads [G-2] literally, adding a toast to `★` and to modal-open is one line each and changes nothing else. | 2026-08-03 |
| **BR-35** | Toast counts are **never pluralised**: the literal template is `— {N} orders` for every `{N}` including `0` and `1`. `Found {n} order(s)` keeps its own verbatim form and the two must not be harmonised. | Both strings are captured artifacts; "fixing" either breaks byte-level QA against the live admin. | 2026-08-03 |
| **BR-36** | **Classification precedence:** an order that is both MKT-imported and JIT-sourced renders and sorts as **MKT**; its locators still show `Shelf N`. | The MKT origin governs settlement separation, which is the reason the split exists; the JIT route only governs where the goods sit. | 2026-08-03 |
| **BR-37** | Comment bodies are **rendered as text, never as markup**, in the inline panel, the hub list, and search highlighting. | The corpus is operator-authored free text; an unescaped body is a stored-XSS vector on every screen that carries the hub [G-7]. | 2026-08-03 |

### 4.1 [G-2] confirmation-surface table (companion to BR-34)

| Action | Confirmation | Toast copy |
|---|---|---|
| `[L-M1]` `🖨 Print` (picking list) | Toast | `✓ Print Pick Locations complete — {N} orders` |
| `[L-3]` Bulk Print Labels | Toast | `✓ Bulk Print Labels complete — {N} orders` (+ reason-aware refusal subtext, §3.3) |
| `[L-4]` Bulk Outbound | Toast **+ send sound** | `✓ Bulk Outbound complete — {N} orders` (+ reason-aware exclusion subtext, §3.4 step 6) |
| `[L-F6]` row `🖨` Print | Toast **(spec-defined)** | `✓ Label printed — order {orderId}` |
| `[L-9]` comment `Post` | Toast **(spec-defined)** + in-place append | `✓ Comment posted` |
| `[L-10]` `Mark all read` | Toast **(spec-defined)** + badge clears | `✓ All mentions marked as read` |
| Any print/agent/printer failure | **Red** toast | names the agent or printer; copy is a developer decision [D-4] |
| Stale-order rejection at execute | **Red** toast | reports the rejected count |
| Concurrent-batch conflict | **Non-green** toast | reports the conflicting count |
| `[L-9]` `★` star / unstar | In-place: glyph fills / empties | none |
| `[L-9]` panel expand / collapse | In-place: row appears / disappears | none |
| `[L-2]` modal open · M1 `Cancel` / `✕` / backdrop | In-place: modal opens / closes | none |
| `[L-1]` checkbox / `Select all` | In-place: counts update | none |
| `[L-14]` view tab | In-place: rows filter, `#foundTxt` rewrites | none |

### 4.2 Removed features — these must NOT exist

Recorded so nobody re-implements them from stale documents or leftover CSS. Each has a dated row in §10.

| Removed | Must not appear as | Removed on |
|---|---|---|
| **Ready Items column** | Any second count column beside `Total Items`; any use of the surviving `.cb-ready` green badge class `[RTO-WFX-4]` | 2026-07-22 |
| **`View Order` button in the Actions column** | Any second navigation button on the row; the Actions column is Print only | 2026-07-22 |
| **Failure-state UI in the bulk completion notice** | Any red/partial variant of the completion toast; failures surface as a *separate* toast [BR-9b] | 2026-07-22 |
| **Badge wording `JIT (channel) completed`** | Anywhere on the **shipping surface** — table, badges, modal, printed output. The badge is `Fully Inbounded`. The wireframe's annotation legend is exempt: its dated changelog entry must quote the superseded string to record the rename, and annotations ship in no admin build (QA-F-09, QA-L7-02) | 2026-08-03 |
| **Import-time stock-error validation for MKT orders** | Any block, warning, or hidden state for MKT orders whose products are not in stock | 2026-07-23 |
| **Inbound Carrier column / automatic carrier recording** | Any **inbound** Carrier field or column on this page. Automatic capture of the *receiving* carrier is **not supported** anywhere in WMS 2.0 (adjudication C-1, `[PD-9 · OWNER-PENDING]`). **Scope note:** the order's **shipping** carrier is a different field entirely — it is resolved per order for label printing [BR-10] §6.4, stored on [DC-7], and its absence is a defined refusal path [E-61] [DC-28]. Do not delete that | 2026-08-03 |
| **Photo capture** | No photo column, no upload affordance on this page. Photo capture is **permanently removed** program-wide, not deferred `[PD-63 · OWNER-PENDING]` | 2026-08-03 |
| **Sourcing-route badge column** | No SMART BUY / JIT (channel) / WHOLESALE / PARTNERSHIP / OTHER label on this page; those render on View Orders, Inventory, and Order Detail [G-5] | 2026-08-03 (clarified) |
| **Order search bar, pagination controls, per-PIC row grouping, Bulk Hold, a scan input, a resolved log** | None of these ever existed on this page and must not be added by analogy from another screen. Per-feature attribution, since "respectively" cannot carry six features across three pages: **per-PIC row grouping** and the **resolved log** were removed from `tracking-missing` (2026-07-23, `_wireframe-fixes.md` WF-10); **Bulk Hold** was removed from `order-management` (2026-08-03, its BR-10). The remaining three — **order search bar**, **pagination controls**, **scan input** — have no removal origin at all: they never existed here and are named only so nobody imports them from a screen that does have them (`view-orders` and `closing` are the scan surfaces [G-1]) | n/a (see §10, 2026-07-23 row) |

---

## 5. Data Capture

**Doctrine [G-8]:** UI surfaces (comment history, hub badges) are **views over persisted events**, never the only copy. Anything operator-initiated that is not explicitly declared a NON-event below **must** persist.

**Common envelope on every event.** Unless stated otherwise, every event below carries: `event_id` · `event_name` · `occurred_at` (**server clock**, ISO-8601 with timezone — client clocks are never trusted for ordering [E-63]) · `actor` (system user id + display name, resolved from the signed-in session `[L-F8]`) · `actor_source` (`ui.ready_to_outbound`) · `session_id` · `client_request_id` / `idempotency_key` where applicable · `entity_type` + `entity_id` · `batch_id` where the event belongs to a batch. Event names use the canonical cross-page spellings where one exists (`_review.md` §3 convention 3); all other names are lowercase `entity.action`. Literal API/table naming is a developer decision.

**ID stability.** `DC-1`…`DC-18` preserve the numbering and semantics of the Lens-A plan for this page. `DC-19`…`DC-28` are additions made while writing and auditing this spec. IDs are page-scoped and are never renumbered.

### 5.1 Persisted events

| ID | Event name | Actor | Entity | Payload — old → new / quantities | Surfaced in UI? |
|---|---|---|---|---|---|
| **DC-1** | `comment.posted` | operator | order | `text` (stored raw, rendered escaped [BR-37]), `mentions[]` (resolved user ids), `source` = `rto_inline_panel` / `rto_comments_hub`, `parent_entity` = order no. Append-only — no update/delete events exist for comments `[PD-3 · OWNER-PENDING]` | Yes — inline panel `[L-9]` + toast, hub `[L-10]`, Order Detail comment history |
| **DC-2** | `comment.mention_notified` | system | comment | `channel` = `#fulfillment-admin-comments` (`C0BMGEWM5QA`), `mentioned_user` — **one event and one Slack message per distinct resolved mention**; the same user named twice in one body yields one [E-75], matching `view-orders.md` `DC-20` and `order-detail.md` `DC-27` — `slack_ts`, `delivery_result` ∈ {`delivered`,`failed`,`retrying`}, `attempt_no` old → new, `deep_link`. Failure never rolls back DC-1 `[PD-4 · OWNER-PENDING]` | No (silent) — failures visible only in admin logs |
| **DC-3** | `comment.starred` / `comment.unstarred` | operator | comment | `saved` false → true / true → false, `starred_by` | Yes — `★ Saved` tab, row star glyph (in-place, no toast [BR-34]) |
| **DC-4** | `comment.read` / `comment.mark_all_read` | operator | comment(s) | `unread` → `read`; for mark-all: the full list of comment ids transitioned, `unread_count` old → new | Yes — hub badge, per-row `💬` badge, toast on mark-all |
| **DC-5** | `pickinglist.printed` | operator | batch | `batch_id`, `order_ids[]`, **full line snapshot** `[{location, sku, brand_en, product_name_kr, qty, order_id, sample_set_id?, sample_qty?}]`, `totals {orders, skus, units}`, `sort` = `location_asc`, `printer_target`. The snapshot is the reproducible copy of the paper the picker walked with and is immutable against later renames [E-67]. Sample lines are included once `[PD-36 · OWNER-PENDING]` lands | Toast `[L-6]`; snapshot itself silent |
| **DC-6** | `label.batch_printed` | operator | batch | `batch_id`, `order_ids[]`, `requested_count`, `dispatched_count`, `excluded_order_ids[]` with reason (`no_carrier` [E-61]), per-order job refs → DC-7 | Toast `[L-6]` |
| **DC-7** | `label.printed` | operator | order | `carrier` (Deleo / YUN / …), `label_id`, `source` ∈ {`row_button`, `bulk`}, `reprint_seq` old → new (0 → 1 on first print, n → n+1 on reprint), `job_id` → DC-12 | Toast (row print, `[L-F6]`); reprint count silent |
| **DC-8** | `outbound.batch_executed` | operator | batch | `batch_id`, `order_ids_requested[]`, `order_ids_eligible[]`, `order_ids_excluded[]`, `started_at` → `finished_at`, `idempotency_key`, per-order result refs → DC-16 | Progress `[L-5]` + toast `[L-6]` + sound `[G-3a]` |
| **DC-9** | `order.outbounded` *(canonical)* | operator | order | order `status` old → `prepare-shipment`; per shipped line the detail `{sku, qty, location}` — **no line-status field, because outbound writes no line-level status** [BR-22]; `shelf` old → `null` (auto-clear on outbound) `[PD-18 · OWNER-PENDING]` | Yes — the row leaves the list after the refresh |
| **DC-10** | `inventory.stock_decremented` | system | SKU @ location | `on_hand_qty` old → new, `delta` (negative), `ref` = DC-9 | Silent here; feeds Inventory → Stock History → Outbound tab |
| **DC-11** | `idempotency.duplicate_rejected` | operator | action + key | `action` ∈ {`pickinglist.print`,`label.print`,`outbound.bulk`}, `idempotency_key`, `original_event_id`, `rejected_at`. Persisted even though nothing else happens [G-9] | Silent (dev-chosen surfacing) |
| **DC-12** | `print.job_result` *(canonical)* | system | print job | `job_id`, `agent_id`, `printer_id`, `state` `queued` → `sent` → `done` / `failed`, `failure_reason` (agent unreachable / printer offline / timeout), `artifact_type` ∈ {`shipping_label`,`picking_list`}, `ref` = DC-5/6/7. `done` means the agent accepted and released the job — it cannot prove paper came out [E-78] | Red toast on failure `[G-2]`; lifecycle silent |
| **DC-13** | `order.entered_ready_pool` | system | order | `ready_at` timestamp, `trigger` = first line reaching `INBOUNDED` (or MKT import for MKT orders). Opens the dwell-time interval closed by DC-26 | Silent |
| **DC-14** | `order.mkt_surfaced` | system | order | `import_batch_ref` (Order Management), `pic_user`, `rto_visible_at`, `inbound_state_at_surface` (may be "none inbounded" per [BR-3]) | Silent — the import itself is logged on Order Management |
| **DC-15** | `order.jit_fully_inbounded` | system | order | `fully_inbounded_at`, `line_count`, `staging_shelf`. Drives the `Fully Inbounded` badge and answers "how long do finished JIT orders sit?" | Badge `[L-7]`; timestamp silent |
| **DC-16** | `outbound.batch_item_result` | system | batch item (order) | `batch_id`, `order_id`, `result` ∈ {`success`,`excluded`,`rejected_stale`,`conflict`,`error`}, `reason`, `sequence_no`. **Persisted for every requested order even though the completion UI shows no failure case** [BR-9] [BR-9b] `[PD-34 · OWNER-PENDING]` | Silent |
| **DC-17** | `ui.telemetry` *(dev-flagged, optional)* | operator | — | Read-only interactions: view-tab switch, comment search query, `Refresh` click, M1 `Cancel`. **Not a [G-8] state change.** Logging is a developer decision (§9.3 D-1); if logged, it is analytics-tier with its own retention | No |
| **DC-18** | *(rule, not an event)* | — | — | The **resolved selection set** is embedded in the payload of DC-5, DC-6, and DC-8. Individual checkbox toggles are never logged `[NE-1]` | — |
| **DC-19** | `order.status_changed` *(canonical)* | operator | order | `status` old → new (`processing` / `pending` → `prepare-shipment`), `reason` = `bulk_outbound`, `batch_id`. Emitted alongside DC-9, not instead of it — the canonical name is required wherever a status moves [BR-22] | Silent here; visible on Order Detail actor log |
| **DC-20** | `inventory.reservation_consumed` | system | reservation | `reserved_qty` old → new (released against the shipment rather than back to free stock), `order_id`, `sku`, `location`, `ref` = DC-9. Distinct from DC-10: one moves on-hand, the other closes the reservation | Silent; feeds Inventory Reserved views |
| **DC-21** | `outbound.order_excluded` | system | order | `batch_id`, `order_id`, `exclusion_reason` ∈ {`lines_not_inbounded`, `status_forbids_outbound`, `already_outbounded`, `left_ready_pool`, `empty_order`}, `non_inbounded_line_count`. Feeds the **reason-aware** toast subtext (§3.4 step 6): every enum value has its own phrase, and the subtext may never report one reason for another `[PD-35 · OWNER-PENDING]` | Toast subtext only |
| **DC-22** | `outbound.rejected_stale` | system | order | `batch_id`, `order_id`, `expected_version` → `actual_version`, `changed_fields[]`, `rejected_at`. No partial write occurred `[PD-6 · OWNER-PENDING]` | Red toast; detail silent |
| **DC-23** | `outbound.batch_conflict` | system | batch | `batch_id`, `conflicting_batch_id`, `overlapping_order_ids[]`, `winner_batch_id`. Guarantees the audit trail for "who shipped it" when two operators overlap `[PD-7 · OWNER-PENDING]` | Non-green toast |
| **DC-24** | `print.batch_infrastructure_failure` | system | batch | `batch_id`, `artifact_type`, `agent_id`, `failed_job_count`, `failure_class`. The batch-level companion to DC-12 that drives the **separate red toast** while the completion toast stays all-success `[PD-34 · OWNER-PENDING]` [BR-9b] | Red toast |
| **DC-25** | `rto.list_loaded` | operator | list view | `trigger` ∈ {`page_load`,`refresh`}, `view_tab`, `order_ids_served[]`, `count`, `served_at`. Reproduces exactly what the operator saw, which is the only way to adjudicate "that order was not in my list". Retention may be shorter than the rest (developer decision) | Silent |
| **DC-26** | `order.left_ready_pool` | system | order | `left_at`, `reason` ∈ {`outbounded`,`cancelled`,`all_lines_cancel_inbounded`,`status_change`,`merged`}, `dwell_seconds` computed against DC-13. Closes the ready→outbound dwell-time metric | Silent — the row disappears on the next load |
| **DC-27** | `outbound.batch_aborted` | system | batch | `batch_id`, `aborted_at`, `last_completed_sequence_no`, `cause` ∈ {`network_lost`,`session_expired`,`session_ended`,`server_error`}, `orders_committed[]`, `orders_not_attempted[]`. Prevents a half-run batch from being invisible [E-10] [E-27] [E-55] | Recovery surfaces on next load |
| **DC-28** | `label.print_refused` | system | order | `reason` ∈ {`no_carrier`,`no_template`,`order_not_printable`}, `source` ∈ {`row_button`,`bulk`}, `batch_id?`. The audit record behind the red toast when a label cannot be produced at all — distinct from DC-12 `failed`, which means the job existed and the hardware refused it [E-61] `[PD-55 · NO-DEFAULT]` | Red toast |

### 5.2 Explicit NON-events

Declared per [G-8]: these are ephemeral client-local states and are **not** persisted. Anything not on this list and operator-initiated must persist.

| ID | Non-event | Why |
|---|---|---|
| `[NE-1]` | Individual checkbox toggle / `Select all` toggle | The resolved selection set is captured on the batch event [DC-18]; per-toggle logging would bury the batch record in noise |
| `[NE-2]` | Progress-bar ticks and percentage updates | Client display over a server batch; start and finish are persisted [DC-8] |
| `[NE-3]` | View-tab switch | Pure client-side filter; optional telemetry only [DC-17] |
| `[NE-4]` | M1 `Cancel`, `✕`, or backdrop close | Nothing was printed and nothing changed |
| `[NE-5]` | Comments hub open/close and tab switch | Read-only UI state |
| `[NE-6]` | Comment search keystrokes and results rendering | Read-only; optional telemetry [DC-17] |
| `[NE-7]` | Inline comment panel expand/collapse | Read-only UI state |
| `[NE-8]` | Unposted comment draft text (including loss on the Bulk Outbound refresh) | Never left the client [E-20] |
| `[NE-9]` | Send-sound playback success or failure | Client audio state; must never affect the outbound [E-24] |
| `[NE-10]` | Client-side debounce suppression of a double click | Only the *server-side* rejection is persisted [DC-11] |
| `[NE-11]` | Hover, focus, scroll, column resize, horizontal-scroll position | Presentation only |
| `[NE-12]` | Disabled-button clicks at zero selection or during a batch lockout | No action was attempted |

### 5.3 Retention, export, and downstream consumption

- **Retention.** Comment events (DC-1…DC-4) are retained **indefinitely** — [G-7] designates the comment corpus an AI-training and audit asset, and [BR-27] makes it append-only, so the record is the only copy. Outbound, stock, and print events (DC-5…DC-12, DC-16, DC-19…DC-24, DC-26, DC-27, DC-28) are retained indefinitely as operational-audit records. `DC-25` list snapshots and `DC-17` telemetry may use a shorter horizon (developer decision, §9.3 D-1).
- **Export.** Every batch must be reproducible from its `batch_id`: the picking-list snapshot [DC-5] regenerates the exact printed paper; the label batch [DC-6] + per-order jobs [DC-7] regenerate what was printed for whom; the outbound batch [DC-8] + per-order results [DC-16] reconstruct which orders shipped, which were excluded, and why. CSV encoding and column sets are developer decisions.
- **Downstream consumers.**
  - `DC-9` / `DC-19` → **Closing**: outbounded orders (status `prepare-shipment`) become the closing scan population for that day.
  - `DC-10` / `DC-20` → **Inventory**: Stock History *Outbound* tab and Reserved views.
  - `DC-13` / `DC-15` / `DC-26` → dwell-time and JIT-latency metrics (ready→outbound, fully-inbounded→shipped).
  - `DC-1` → the shared comment corpus surfaced on Order Detail and on every screen's Comments hub.
  - `DC-7` / `DC-28` → the per-order label history read by CS when a customer disputes a shipment.

---

## 6. Integrations

### 6.1 Slack routing

Exactly **one** Slack route originates on this page. Payload fields are verbatim from `_slack-routing.md` (CONFIRMED 2026-08-03).

| Trigger | Channel | Payload | Mention target |
|---|---|---|---|
| Comment `@mention` posted from the inline row panel `[L-9]` or the Comments hub `[L-10]` | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) | order no., comment text, time, author, @mentioned user, deep link to the order | the mentioned user — the message **body** @mentions them, so Slack raises a personal notification while the channel doubles as a team-visible archive [G-7] |

**Delivery contract.** The comment commits first; Slack delivery is a side effect that is retried and persisted [DC-2] and never blocks the UI or rolls anything back `[PD-4 · OWNER-PENDING]` [BR-30]. Retry policy is a developer decision [D-12]. **Fan-out: one message per distinct resolved mention** — three different people named in one comment produce three messages; the same person named twice produces one [E-75] [DC-2].

**Self-mention.** Whether an operator @mentioning **themselves** suppresses the Slack notification is **not decided by any register entry**: `[PD-16]`, previously cited here, decides only that the *system* match-confirm auto-comment suppresses the mention when `resolver == registrant`, and its scope line names View Orders / Tracking Missing / Order Detail — not this page, and not operator free text. That citation is withdrawn (2026-08-03). The behavior is therefore a **developer decision [D-18]** bounded by [BR-30]: the comment persists either way and delivery never blocks the post.

**Explicit non-routes from this page** — stated so nobody wires them by analogy:

| Channel | Why it does not fire here |
|---|---|
| `#unrecognized-tracking` | Unrecognized-barcode registration happens on View Orders and Unrecognized Tracking. This page has no scan surface [BR-25] and no unrecognized pool. |
| `#wholesale-ops` | The morning no-tracking check runs against Inbound Requests, not ready orders. |
| `#partnership-kr` | Same. |
| — | **Bulk Outbound completion does not notify Slack.** No channel owns "a wave shipped"; inventing one would create an unowned alert stream. Consistent with the closing-page reasoning `[PD-72 · OWNER-PENDING]`. |
| — | **Print failures do not notify Slack.** They surface as a red toast [BR-9b] and persist as `print.job_result` [DC-12] / `print.batch_infrastructure_failure` [DC-24] / `label.print_refused` [DC-28]. |
| — | **"Not connected — contact the Fulfillment Center" orders raise no Slack alert.** No route and no owner exist for that follow-up — that is precisely the gap recorded as `[PD-55 · NO-DEFAULT]` (§9.2 OQ-2). |

Future routes are decided per feature at development time (`_slack-routing.md` last row).

### 6.2 Cross-page links and deep links [G-12]

| From | To | Behavior |
|---|---|---|
| Order ID `[L-F5]` | Order Detail — `../order-detail/` in the wireframe corpus; the filtered entity URL in production | Real anchor, not decoration. Currently a non-anchor `<span>` — defect `[RTO-WFX-3]` |
| Comments hub entry `[L-10]` | The order the comment belongs to | Opens Order Detail, including for orders **not** present in the current ready list [E-38] |
| Inline comment `@mention` → Slack message | Back into the admin at the mentioned order | The `deep link` payload field carries this |

**Inbound links (where the rows on this page come from):**

| Origin | What arrives |
|---|---|
| **View Orders** State 6 / State 1 inbound flow | An order's lines reach `INBOUNDED`, so the order enters this pool [DC-13]. Full inbound on View Orders can auto-outbound the order, which means it may never appear here at all — auto-outbound is a View Orders scan/bulk behavior only `[PD-21 · OWNER-PENDING]` (adjudication C-7) |
| **Order Management** manual import | MKT orders appear immediately, regardless of stock [BR-3] [DC-14], carrying their PIC `[PD-33 · OWNER-PENDING]` |
| **Order Management** sample assignment [G-13] | The order's sample set, which internal picking artifacts must render `[PD-36 · OWNER-PENDING]`; Order Detail shows the same detail on its line items `[PD-27 · OWNER-PENDING]` |
| **Inventory** | Location codes and staging shelves rendered in `[L-12]`; one location per SKU and one SKU per location `[PD-46 · OWNER-PENDING]` |

**Outbound links (where this page's work lands):**

| Destination | What it consumes |
|---|---|
| **Closing** | Orders moved to `prepare-shipment` become the day's scan population [BR-22]. Closing treats `prepare-shipment` as the sole normal status |
| **Inventory** | Stock History *Outbound* tab and Reserved views [DC-10] [DC-20] |
| **Order Detail** | Actor log and status history [DC-9] [DC-19]; label history [DC-7] [DC-28] |

### 6.3 Sheet and BI handoffs

**This page has no direct sheet handoff.** Stated explicitly because two adjacent screens do:

- The **Daily Shipping Status** sheet is updated by **Closing** on confirmation, not by this page; its column mapping is an open question owned by the closing spec `[PD-71 · NO-DEFAULT]` — the register marks it *not decided*, so it carries no provisional behavior and must not be tagged `OWNER-PENDING`.
- The **Procurement Hub** sheet is fed by **Inbound Request**, not by this page.

Outbound events from this page reach BI only through the persisted event stream (§5.3), never through a spreadsheet written from the browser.

### 6.4 Print pipeline [G-4]

**Three print surfaces on this page** — and exactly three:

| Surface | Artifact | Scope |
|---|---|---|
| `[L-F6]` row `🖨` | Shipping label | One order (the reprint path) |
| `[L-3]` `🖨 Bulk Print Labels` | Shipping labels | Every selected order, one job each |
| `[L-M1]` `🖨 Print` | Picking list | One aggregated document for the whole selection |

**Page deltas on [G-4]** (the rule itself is not restated):

1. **Carrier resolution is per order, not per batch.** A single Bulk Print Labels run may emit Deleo and YUN labels in the same batch; each job carries its own carrier and template [BR-10].
2. **A local print agent (PrintNode-class) is mandatory infrastructure for this page**, not an optimisation (developer handoff note B, 2026-08-02).
3. **Job lifecycle is persisted** `queued → sent → done|failed` with agent id and printer id [DC-12]; a refusal that never became a job is [DC-28].
4. **Failures never corrupt the completion toast** [BR-9b]; affected orders stay in the list `[PD-34 · OWNER-PENDING]`.
5. **Printing never gates outbound** and outbound never requires a prior print [BR-31].
6. **Label layout content is out of scope** — Phase 3-1. This spec covers *when* a label prints, *which* carrier's label, *what is captured*, and *what happens when it fails*, not what is drawn on it.
7. **Picking-list layout** follows §3.15: Location / SKU / Product (Korean + bold EN brand) / Qty / Order, location-ascending with the [BR-20] tie-break, with sample lines once `[PD-36 · OWNER-PENDING]` lands.
8. **The picking list is not a label.** It is an A4-class internal document; it is never routed to the label printer queue, and the two artifact types are distinguished on every job [DC-12 `artifact_type`].

### 6.5 Audio

The send sound fires on `[L-4]` Bulk Outbound at click time [G-3a] `[PD-2 · OWNER-PENDING]`. **No TTS and no warning tone on this page** [G-3b] [G-3c] — the spoken `Please check this order` alert belongs to Closing and the wrong-product warning tone to View Orders State 6. Audio failure is swallowed and never affects the transaction [E-24] [E-49] `[NE-9]`. Exactly one control on this page is sound-bound; QA-L4-04 asserts it.

---

## 7. Edge Cases & Error States

`E-1`…`E-30` preserve the numbering and semantics of the Lens-B plan for this page. `E-31`…`E-79` (plus `E-15b`) are additions made while writing and auditing this spec. IDs are page-scoped and are **never renumbered**; they are grouped topically below, so numeric order does not run continuously inside a table. Each row states the **expected behavior**, not the wireframe's current behavior; wireframe divergences are noted so QA tags them `[ADMIN]` instead of filing bugs.

**Total: 80 edge cases** (`E-1`…`E-79` + `E-15b`).

### 7.1 Selection and filtering

| ID | Situation | Expected behavior |
|---|---|---|
| **E-1** | **Zero selection.** No rows checked. | All three bulk buttons **disabled**. Labels read `🖨 Print Pick Locations (0 orders · 0 items)`, `🖨 Bulk Print Labels (0 orders)`, `📦 Bulk Outbound (0 orders)`; `.cnt` reads `0 selected`. No toast, no sound, no server call. Disabled-button clicks are `[NE-12]`. |
| **E-2** | **Select-all scope vs view tabs.** Select all on `Inventory`, then switch to `All`. | Only the three Inventory rows remain selected; `MKT-40233` and `422164` are **not** selected. Selection persists per order across switches; `Select all` re-renders as unchecked (not all visible rows selected) `[PD-38 · OWNER-PENDING]`. |
| **E-3** | **Selection contains an MKT order with a `Not inbounded` line.** | Picking list excludes the non-inbounded line entirely (it has no location); the order still contributes its inbounded lines. Bulk Outbound **auto-excludes the whole order** and reports it in the toast subtext `[PD-35 · OWNER-PENDING]` [DC-21]. |
| **E-4** | **Selection contains a fully-inbounded JIT order.** | M1 renders its `Shelf N` row and sorts it **after** every rack-coded location [BR-20]. Bulk Outbound treats it as **eligible** `[PD-35 · OWNER-PENDING]`. |
| **E-5** | **Empty pool.** Zero ready orders. | Table renders with headers and no rows; `Found 0 order(s) with items ready for outbound`; bulk bar disabled; `Select all` is a no-op and must not throw. Same for a view tab with zero matches. |
| **E-6** | **`Refresh` with an active selection and/or an open comment panel.** | Wireframe is silent — a developer decision that **must be chosen and documented** [D-7]. Recommended: preserve selection for orders still present, drop it for orders that left the pool, collapse open panels, and persist [DC-25]. |
| **E-50** | **`Select all` clicked while it is indeterminate** (some visible rows already selected). | It **adds** the remaining visible rows. It never deselects. Clicking it again, now fully checked, clears the **visible** set only and leaves selections on other tabs intact [BR-17]. |
| **E-51** | **A selected order leaves the pool, then the operator switches tabs.** | The row and its selection survive on the client until `Refresh` or execute; the server rejects it at execute time [E-7]. The client never silently drops a selected id, because a silently shrinking selection is indistinguishable from a mis-click. |
| **E-52** | **Rapid view-tab switching while a batch is running.** | Tabs are locked for the duration [BR-18]; a mid-batch reflow would desynchronise the row set the operator is watching from the set the server is processing. |
| **E-48** | **A line was deleted from a selected order by another operator**, so `Total Items` no longer matches the button label. | The batch executes against the **server's** current line set, not the client's count. The completion toast reports orders, not units, so no mismatch is shown; the discrepancy is recoverable from [DC-8] + [DC-16]. |

### 7.2 Bulk execution

| ID | Situation | Expected behavior |
|---|---|---|
| **E-7** | **Stale row.** An order was outbounded or cancelled on another screen between list load and batch execute. | Server rejects that order at revalidation; no partial write; the order is reported as `rejected_stale` [DC-22] and a red toast names the count. The remaining eligible orders still execute `[PD-6 · OWNER-PENDING]`. |
| **E-8** | **Two operators run Bulk Outbound with overlapping selections concurrently.** | Each order is outbounded **exactly once**. The losing batch receives `conflict` results for the overlapping ids [DC-16] [DC-23] and a non-green toast naming the count `[PD-7 · OWNER-PENDING]`. Stock is never double-decremented. |
| **E-9** | **Double-click on any bulk button** [G-9]. | Exactly one batch executes: client debounce plus a server idempotency key. The duplicate is persisted [DC-11]. **The known current-admin bug processes double clicks twice — this is a mandatory regression test, not a feature to reproduce** [BR-13]. |
| **E-10** | **Network failure mid-batch** (request sent, response lost). | A retry with the same idempotency key must not double-outbound or double-print. The UI must show an **unresolved** state, never a false success toast. If the batch is genuinely incomplete, `outbound.batch_aborted` [DC-27] records the last completed sequence so the next load can reconcile. |
| **E-11** | **Print agent offline / unreachable** [G-4]. | No silent success, no browser-dialog fallback, no queueing that looks like success. Red toast [G-2] names the printer or agent; the job result is persisted [DC-12] and the batch-level failure as [DC-24]. Affected orders remain in the list `[PD-34 · OWNER-PENDING]`. |
| **E-12** | **Print agent fails mid-batch** (labels 1–2 printed, 3 fails). | Partial physical output is real and must not be denied. The completion toast stays all-success [BR-9]; a **separate** red toast reports the failed count; per-order job results are persisted so the operator can reprint exactly the failed orders from the row buttons `[PD-34 · OWNER-PENDING]`. |
| **E-13** | **Order with mixed line statuses** (some `INBOUNDED`, some not). | It appears on the page (≥1 rule, [BR-1]). `Total Items` counts **all** units `[PD-37 · OWNER-PENDING]`; the picking list contains **only** the inbounded lines; Bulk Outbound **excludes the order** `[PD-35 · OWNER-PENDING]`. Three different denominators, each stated. **Consequence on the header figures:** with such an order selected, the M1 `{units}` total is **lower** than the `[L-2]` `{items}` figure by exactly that order's non-inbounded unit count — §3.13 invariant (b). That gap is the correct output, not a reconciliation failure. |
| **E-19** | **Second bulk action started while the progress bar is running.** | All three bulk buttons, the M1 `🖨 Print`, `Refresh`, and the view tabs are locked for the duration [BR-18]. **The wireframe does not lock them** — `[ADMIN]`-only assertion. |
| **E-21** | **MKT order with ZERO inbounded lines selected for Bulk Outbound.** | Auto-excluded (nothing to outbound); counted in the toast subtext; persisted with `exclusion_reason = lines_not_inbounded` [DC-21]. It is **not** an error and does not abort the batch. |
| **E-22** | **Large selection (100+ orders).** | The batch is chunked; progress remains monotonic 0→100 across chunks; there is no pagination on this page, so the whole ready pool can legitimately be selected. Chunk size and progress granularity are developer decisions [D-2]. |
| **E-27** | **Permission edge.** No role model exists in any input document. | v1 ships a single admin role; no gating [G-15] `[PD-1 · OWNER-PENDING]`. Do not invent per-action gates. |
| **E-32** | **Every line of a listed order was cancel-inbounded elsewhere** between load and execute. | The order is no longer ready: excluded with `left_ready_pool` [DC-21], and [DC-26] records its exit. No stock movement. |
| **E-33** | **A Hold order carries inbounded lines and therefore appears in the pool.** | It renders in the list (it satisfies [BR-1]) but is **auto-excluded** from Bulk Outbound with `exclusion_reason = status_forbids_outbound` `[PD-29 · OWNER-PENDING]` [DC-21]. Releasing the hold is Order Detail's job. |
| **E-34** | **An order already in `prepare-shipment` / `shipped` is still listed** (outbounded elsewhere since load). | Auto-excluded with `already_outbounded`; the row disappears on the next load [DC-26]. Never outbounded twice. |
| **E-44** | **Browser tab left open overnight**; the list is a day stale. | Every order fails revalidation. The batch commits nothing, a single red toast reports the count, and the view refreshes `[PD-6 · OWNER-PENDING]`. The operator must not be able to ship yesterday's snapshot. |
| **E-49** | **First user gesture of the session is the Bulk Outbound click itself.** | The `AudioContext` is created inside the gesture, so the sound plays. If the context is suspended or the device is muted, the outbound proceeds identically and silently [E-24] `[NE-9]`. |
| **E-53** | **Every selected order is excluded** (e.g. all three are MKT rows with non-inbounded lines). | The green completion toast still renders as `✓ Bulk Outbound complete — 0 orders` with the reason-aware exclusion subtext (§3.4 step 6) — here, one shared reason, so `3 excluded — items not inbounded`; had one of the three been on hold instead, `3 excluded — 2 items not inbounded · 1 status blocks outbound`. It is not suppressed and not recoloured: nothing shipped, nothing was written, and the operator is told exactly that. The page still refreshes [BR-8]. |
| **E-54** | **`{N}` is 1, or 0, in a completion toast.** | The template is not pluralised: `✓ Bulk Outbound complete — 1 orders`. `Found {n} order(s)` keeps its own verbatim form [BR-35]. Neither string may be "corrected" — both are captured artifacts and both are asserted byte-for-byte by QA. |
| **E-55** | **Session expires (401) mid-batch.** | The server rejects the remaining work rather than attributing it to a stale identity [L-F8]; committed orders stay committed; `outbound.batch_aborted` [DC-27] records `cause = session_expired` with the committed and not-attempted id lists; the UI surfaces a red toast and sends the operator to re-authenticate. No silent partial success. |
| **E-56** | **Browser is offline when a bulk button is clicked.** | The request never leaves; the UI shows a red toast and **no** progress run and **no** completion toast. The send sound may still have played (it fires on click) — that is acceptable and is exactly why the sound is not a success signal, only a receipt-of-click signal [G-3a]. |
| **E-57** | **`Refresh` clicked while a batch is running.** | Locked with the same lockout as the bulk buttons [BR-18]. Re-querying mid-batch would replace rows the server is still writing. |
| **E-58** | **Browser Back / bfcache after the Bulk Outbound refresh.** | The restored page must not present already-shipped orders as selectable. The list source is re-queried on `pageshow` when the page is restored from bfcache, or the page is marked no-store. Shipping the same wave twice because the operator pressed Back is not an acceptable failure mode. |
| **E-59** | **A selected order was merged into another on Order Management** between load and execute. | Rejected as stale [DC-22]; `order.left_ready_pool` records `reason = merged` [DC-26]. The surviving order is not silently substituted — the operator re-selects it `[PD-59 · OWNER-PENDING]` context. |
| **E-60** | **An order with zero line items appears in the pool** (upstream data defect). | It renders with `Total Items 0` and an empty item cell, and is auto-excluded from Bulk Outbound with `empty_order` [DC-21]. It is never hidden — a hidden broken order is an order nobody fixes. |
| **E-61** | **A selected order has no carrier assigned** ("Not connected — contact the Fulfillment Center"). | Bulk Print Labels excludes it and reports it in the toast subtext with its own reason phrase — one such order gives `1 excluded — no carrier assigned` (§3.3); the row `🖨` refuses with a red toast; both persist `label.print_refused` [DC-28]. Bulk Outbound is **not** blocked by the missing carrier — the goods can leave the building before the carrier record resolves; the eligibility filter states this positively (§3.4 step 4) and the [DC-21] `exclusion_reason` enum carries no `no_carrier` value, so the outbound beat says nothing about the order at all. **Unblocking is manual Slack coordination with the fulfillment person in charge** (`[PD-55]` owner-decided 2026-08-03, §9.2 OQ-2); v1 ships no in-admin affordance on this page. `order-detail.md` `[E-86]` takes the opposite position for its own `📦 Outbound` control — open cross-page conflict `[RTO-X-1]`, §9.5. |
| **E-62** | **Keyboard activation.** A bulk button focused and activated with Enter or Space; Enter held down producing key auto-repeat. | Identical to a click, including debounce and the lockout: exactly one batch. Auto-repeat must not queue batches [E-9] [BR-18]. |
| **E-63** | **Client clock skew** — the operator's machine is minutes off. | Every persisted timestamp is the **server** clock (§5 envelope). Client time is never used for event ordering, dwell-time arithmetic, or the closing-day boundary. |

### 7.3 Picking list (M1)

| ID | Situation | Expected behavior |
|---|---|---|
| **E-14** | **Same SKU in multiple selected orders, same location.** | **Two rows**, one per order × SKU — no merge [BR-19]. The `Order` column must remain unambiguous so the picker can split the pick between boxes. |
| **E-15** | **Warehouse item with no registered location** (location deleted or unassigned in Inventory). | The Pick Locations cell renders an explicit unknown marker and the picking-list row still appears with that marker. **Never a blank cell and never a silently dropped row** [BR-23]. |
| **E-25** | **M1 opened with 0 selected.** | Unreachable through the UI because `[L-2]` is disabled at zero selection [E-1]. If reached programmatically, the header must read `0 orders selected · 0 SKUs · 0 units total` and `🖨 Print` must be disabled. |
| **E-28** | **Sample-set order in the picking flow** [G-13]. | The picking list renders a single **"sample set"** line — v1: "sample set" only, no type/qty breakdown (`[PD-51]` owner-decided 2026-08-03) `[PD-36 · OWNER-PENDING]` [BR-21]. Wireframe gap **WF-9** — **applied 2026-08-03**; M1 renders the sample-set row, asserted by QA-M1-03/04/05/06. |
| **E-30** | **M1 open while underlying data changes** (another session outbounds one of the selected orders). | On `🖨 Print`, the server revalidates; on mismatch it re-renders the table rather than printing stale paper `[PD-6 · OWNER-PENDING]`. Printing stale paper sends a person to a shelf for a box that already shipped. |
| **E-31** | **A sample set is assigned (Order Management) after the picking list was printed.** | The printed snapshot [DC-5] is authoritative for what the picker was told; the newly assigned sample is not on their paper. The operator must reprint. No automatic reprint, no silent amendment. |
| **E-36** | **A location code changed in Inventory between list load and M1 print.** | Same as E-30: revalidate and re-render. The snapshot always records the location that was actually printed. |
| **E-40** | **Picking list printed, then the selection is changed, then Bulk Print Labels.** | Labels are produced for the **current** selection, not for the printed snapshot. The two artifacts are independent [BR-18]; there is no sequence gate `[PD-39 · OWNER-PENDING]`. |
| **E-41** | **JIT order staged but with no shelf recorded.** | Pick Locations renders the unknown marker rather than an empty cell [BR-23]; the M1 row sorts into the `Shelf` group at the end with the marker visible. |
| **E-46** | **A ready line has quantity 0 or a negative quantity** (upstream data defect). | The row is rendered with the raw value and flagged visually rather than hidden, and it does not corrupt the unit totals arithmetic: `Σ(Total Items)` must still equal the `[L-2]` item count exactly (§3.13 invariant (a)), and the M1 `units total` must still equal the pickable-unit sum with its usual non-inbounded offset (invariant (b)). A hidden bad row is a silent short-ship. |
| **E-64** | **Every selected order is JIT**, so every picking-list row is in the `Shelf N` group. | The list is still produced and still deterministic: group 1 is empty, group 2 sorts numerically by `N`, ties by order id then SKU [BR-20]. The note block's illustrative example (`A-02-13 → B-01-07 → Shelf 3`) is fixed copy and does not change with the data. |
| **E-65** | **Two different orders need the same location code.** | Both rows render; the tie is broken by order id ascending, then SKU ascending, so **reprinting the same selection produces a byte-identical list** [BR-20]. An unstable sort would make a reprint disagree with the paper already in the picker's hand. |
| **E-66** | **A sample set is assigned whose sample SKU has no registered location.** | The sample line still appears on the picking list with the unknown marker, once `[PD-36 · OWNER-PENDING]` lands. Dropping it would silently un-promise something the carrier-facing label already promised [G-13]. |
| **E-67** | **A product is renamed in the catalogue after the picking list was printed.** | The snapshot [DC-5] keeps the printed name. Reproducing the paper must reproduce what the picker actually read, not today's catalogue. |

### 7.4 Row rendering

| ID | Situation | Expected behavior |
|---|---|---|
| **E-15b** | **A row's item-line count and locator-line count disagree** (data defect). | Render every item line and pad the locator column with the unknown marker so the 1:1 vertical pairing in `[L-12]` is never silently broken. |
| **E-23** | **Order ID link points to an order cancelled or deleted after load.** | Order Detail handles the missing/cancelled entity; this page keeps showing the stale row until the next `Refresh` or bulk revalidation. The link itself never 500s. |
| **E-42** | **MKT order with no PIC set.** | Render `PIC: —` explicitly. An absent second line reads as "regular order" and loses the marketing-ownership signal. |
| **E-47** | **Very long Korean product name** in *Ready Item Details*. | `.item-line` uses `white-space:nowrap`, so long names extend the cell and the table scrolls horizontally rather than wrapping mid-name. Truncation, if any, must preserve the **brand prefix and the trailing `×qty` pill** — those are the two tokens the picker reads [D-15]. |
| **E-68** | **The same order id appears twice in the list** (upstream data defect). | Both rows render. They are never collapsed, and selecting one must not select the other, because a collapsed duplicate hides the fact that the upstream list is broken. A batch containing the id twice deduplicates server-side and reports one result. |
| **E-69** | **A ready line's SKU no longer resolves in the catalogue.** | Render the SKU and product name stored on the order line, never a blank and never `undefined`. The order shipped against that line; the catalogue's later state does not change what is in the box. |
| **E-70** | **An order is both MKT-imported and JIT-sourced.** | It renders and sorts as **MKT** (purple tint, `MKT` badge, `Marketing` tab, middle sort group) [BR-36]; its Pick Locations cell still shows `Shelf N`. It appears in exactly one tab, preserving the `Inventory + Marketing + JIT = All` invariant [L-14]. |
| **E-71** | **The PIC user was deactivated after the import.** | Render the stored display name unchanged with a neutral inactive marker. Blanking the line would erase accountability for a campaign that already shipped. |
| **E-72** | **Order Date rendering and timezone.** | Displayed in the live admin's own form `2026. 7. 21.` in the warehouse's local timezone. It is display-only; it is never the sole sort key, and it never participates in the closing-day boundary, which is Closing's own rule. |
| **E-73** | **Viewport narrower than the 1240 px table minimum.** | The `.mockwrap` container scrolls horizontally. Columns are never dropped, never reordered, and never wrapped onto a second line [L-F7] — a picker's row must stay one row. |

### 7.5 Comments

| ID | Situation | Expected behavior |
|---|---|---|
| **E-16** | **Comment failures.** Empty `Post`; `@mention` of an unknown user; Slack delivery failure. | Empty/whitespace-only: blocked client-side, no server call, no toast. Unknown user: no Slack send, defined inline feedback, comment still posts with the literal text. Slack failure: the comment persists, delivery is retried and persisted [DC-2], nothing rolls back `[PD-4 · OWNER-PENDING]`. |
| **E-17** | **Comment panel open, then the view tab is switched.** | All open panels collapse (normative wireframe behavior). `[WF]`-testable today. |
| **E-20** | **Bulk Outbound refresh destroys an unsaved comment draft.** | Draft text is `[NE-8]` and is genuinely lost. The mitigation (warn on unload, or preserve the draft across the refresh) is a developer decision that **must be chosen and documented** [D-7], not left implicit. |
| **E-26** | **Unread badge desync** between the hub badge, the per-row `💬` badges, and `Mark all read`. | All three read from the same persisted unread state [DC-4]. After `Mark all read` the hub badge is `0`, every per-row badge clears in the same render pass, and the toast `✓ All mentions marked as read` confirms it [BR-34]. |
| **E-38** | **Hub search matches a comment on an order that is not in the ready list.** | The result still renders and clicking it opens that order. Search scope is **all comments**, not the current table [G-7]. |
| **E-39** | **`@mention` of a deactivated or off-boarded user.** | No Slack send; the comment persists with the literal mention text; defined inline feedback. Never a silent success. |
| **E-43** | **Another operator posts a comment on a row while it is being outbounded.** | The comment persists against the order regardless of the order's status; the outbound is unaffected. Comments are never blocked by order state [BR-27]. |
| **E-45** | **Comment posted from the hub for an order also open in an inline panel.** | One entity, two views. Both surfaces render the new comment on their next refresh; no duplicate is created. |
| **E-74** | **Comment text contains HTML or a script tag.** | Stored raw, rendered **escaped** everywhere it appears — inline panel, hub list, and search highlighting [BR-37]. The highlight implementation must escape before inserting `<mark>`, never after. |
| **E-75** | **One comment mentions three people; and one comment names the same person twice.** | Three distinct mentions ⇒ **three** Slack messages and three [DC-2] events, one per distinct resolved user — the [G-7] contract, whose payload names a single mentioned user, and the shape `view-orders.md` `DC-20` and `order-detail.md` §6.1 implement. The same user named twice in one body ⇒ **one** message and one event; duplicates collapse on the resolved user, never on the comment. (This spec previously said one message named everyone; corrected 2026-08-03 §10.) |
| **E-76** | **The Comments hub is open when the Bulk Outbound refresh fires.** | The hub closes with the reload. Unread and saved state are server-held, so nothing is lost; the operator reopens it. |
| **E-77** | **A comment is posted on an order that has already left the ready pool.** | Accepted and persisted against the order. The comment corpus is order-scoped, not list-scoped; refusing it would lose exactly the post-hoc note ("shipped short, see photo") that disputes depend on. |

### 7.6 Feedback surfaces

| ID | Situation | Expected behavior |
|---|---|---|
| **E-18** | **Consecutive bulk actions before the previous toast dismisses.** | Single-slot replacement: the new toast replaces the old one (wireframe behavior, default) [D-8]. Stacking is a developer decision; whichever is chosen must be consistent across all three actions. |
| **E-24** | **Web Audio blocked, suspended, or unavailable** (autoplay policy, silent mode, unsupported browser). | The sound is skipped and the outbound proceeds unchanged. The wireframe's `try{…}catch(e){}` is normative: an audio exception must never surface to the operator or abort the batch. |
| **E-29** | **Reprint** — row `🖨` or Bulk Print Labels on an already-printed order. | Always allowed [BR-32]. Every print is captured with an incrementing `reprint_seq` [DC-7]. No confirmation dialog, no warning — reprinting is normal operations. |
| **E-35** | **Two lines of the same order carry the same SKU at the same location** (duplicate line). | Rendered as the data says: two item lines, two locator lines, two picking-list rows. The page never silently merges lines it did not create. |
| **E-37** | **Bulk Outbound toast vs the refresh.** | Ordering is fixed: sound → progress → toast → refresh, and the toast is re-rendered after the reload so it survives long enough to be read. A toast destroyed by its own refresh is an invisible confirmation [G-2]. |
| **E-78** | **The print agent reports `done` but no paper came out** (out of paper, jam, wrong tray). | The software cannot know. `done` means the agent accepted and released the job [DC-12], and the spec claims nothing more. The remedy is the row `🖨` reprint path [BR-32], which is why per-order reprint exists as a first-class affordance rather than a recovery hack. |
| **E-79** | **A green completion toast and a red infrastructure-failure toast are due at the same moment.** | With single-slot replacement the green toast renders first and the red toast replaces it, so the operator's last-read state is the problem, not the success [BR-9b]. Both are persisted ([DC-6]/[DC-8] and [DC-24]) regardless of what the slot showed. |

---

## 8. QA Acceptance Criteria (machine-runnable)

### 8.0 How to run this section

**Target for `[WF]` scenarios:** `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/ready-to-outbound/` — executable **today**, against the live wireframe, using the exact selectors and strings below. No `[WF]` scenario requires a question to be answered before it can run.
**Target for `[ADMIN]` scenarios:** the real admin once built. These assert server behavior, persistence, concurrency, physical print output, Slack delivery, and the dynamic selection model that the wireframe does not implement.

**Tagging.** Every scenario is tagged `[WF]` or `[ADMIN]` (no other tiers, per `_review.md` §3 convention 4). `[ADMIN]` scenarios are deferred rows, not failures.
**Negatives.** Scenarios that assert something must *not* happen, must be blocked, or must be absent are marked **· negative**. The mark may sit in the header tag (`[WF] · negative`) **or** appear as an inline `**· negative:**` clause inside the body; **either form makes the whole scenario a negative** for the count table below. Counting header tags alone undercounts by 2 and is wrong.

**Preconditions unless stated otherwise.** Fresh page load, annotations visible, default view `All`, rows `422221` / `422176` / `422165` checked and `MKT-40233` / `422164` unchecked, no modal open, no comment panel open, hub closed. **Reset between scenarios by reloading the page** — the wireframe holds no persistent state.

**Reading the progress bar correctly (applies to every progress assertion).** `#pfill` has **no inline width** on load; its `60 %` comes from the CSS rule `.pbar .fill{width:60%}`. The demo script sets an **inline** `style.width` when a batch runs. Therefore:
- "no batch has run" ⇒ `document.getElementById('pfill').style.width === ''`
- "a batch completed" ⇒ `style.width === '100%'`
Never assert `getComputedStyle(...).width`, which returns pixels.

**Reading `#pbarLabel` correctly.** The element contains a text node **and** the legend dot `6`. The demo script rewrites `childNodes[0]` only. Assert on `#pbarLabel.childNodes[0].textContent`, or on `#pbarLabel.textContent` with the trailing `6` tolerated.

**Reading the M1 header correctly.** `#m-pick .modal > header` contains the title text **and** the `✕` button, so `textContent` returns `…units total)✕`. Assert on the header's **first child text node**, or on `textContent` with a trailing `✕` stripped.

**Reading a running-state label correctly (applies to every "during the run" assertion).** The demo script sets `#pfill`'s inline width **synchronously** on click but rewrites `#pbarLabel` only on the first `setInterval` tick, 250 ms later. For the opening ~250 ms of a run the label therefore still shows the **previous** action's copy — on a fresh load, the idle demo copy — including that action's mode string. **Every "during the run" assertion below is valid only from the first tick onward: sample after `#pfill.style.width` has reached `20%` or later, never before.** This is a wireframe demo artifact (registered `[RTO-WFX-9]`), not a defect to file, and not a licence to weaken the assertion — from the first tick on, the label is exact.

**String assertions: equality vs containment.** The two readings are never interchangeable, so each scenario says which it uses:
- *"element E has textContent `X`"* / *"equals `X`"* ⇒ **strict equality** on that one element's `textContent`.
- *"contains no occurrence of `X` in S"* / *"contains `X`"* ⇒ **substring scan** over the named subtree `S`. A containment assertion always names its subtree; a bare `document.body` scan is used only where the scenario says `document.body`.
When a scenario asserts the absence of a string, the subtree it names is the whole scope of the claim — the annotation layer (`.legend`, `.dot`, `.wf-bar`) is **outside** every product-string claim unless explicitly included, because it ships in no admin build (QA-F-09).

**Known wireframe artifacts QA must not file as bugs** (§2.4): inert checkboxes / `Refresh` / `Post` / `Mark all read` / `.printbtn`; no button lockout during a batch; no actual page reload after Bulk Outbound; `#crow4` belongs to the JIT row and `#crow5` to the MKT row (ids out of document order); the seeded comment carries a trailing period inline and none in the hub; the browser `<title>` and `wf-bar` heading spell `Outbounded` correctly while the admin surface preserves `Outbonded`; **legend item 7 quotes the superseded badge wording `JIT (channel) completed` inside its dated rename changelog** — a changelog cannot record a rename without naming the old string, and the legend is annotation chrome ([BR-4] is scoped to the shipping surface); **the first ~250 ms of every progress run still carries the previous action's label copy** (`[RTO-WFX-9]`, see the reading rule above).

**Scenario counts** (coverage map in §8.19):

| Block | Scenarios | `[WF]` | `[ADMIN]` | negative |
|---|---|---|---|---|
| QA-L1 selection & counts | 9 | 4 | 5 | 4 |
| QA-L2 Print Pick Locations entry | 5 | 3 | 2 | 3 |
| QA-M1 picking-list modal | 15 | 12 | 3 | 7 |
| QA-L3 Bulk Print Labels | 8 | 4 | 4 | 5 |
| QA-L4 Bulk Outbound | 13 | 5 | 8 | 7 |
| QA-L5 progress bar | 7 | 5 | 2 | 5 |
| QA-L6 completion toast | 8 | 5 | 3 | 5 |
| QA-L7 JIT row | 5 | 3 | 2 | 2 |
| QA-L8 MKT row | 7 | 4 | 3 | 3 |
| QA-L9 inline comments | 11 | 6 | 5 | 5 |
| QA-L10 comments hub | 12 | 10 | 2 | 5 |
| QA-L11 layout | 2 | 2 | 0 | 1 |
| QA-L12 Pick Locations column | 6 | 4 | 2 | 3 |
| QA-L13 Total Items | 5 | 3 | 2 | 2 |
| QA-L14 view tabs | 8 | 7 | 1 | 3 |
| QA-F page furniture | 13 | 10 | 3 | 7 |
| QA-E edge cases | 39 | 6 | 33 | 29 |
| QA-DC persistence assertions | 28 | 0 | 28 | 6 |
| **Total** | **201** | **93** | **108** | **102** |

Negative scenarios: **102 of 201 = 50.7 %** (requirement: ≥ 25 %). Counted under the rule stated above — a header tag **or** an inline `**· negative:**` clause makes the scenario a negative. Recomputed for v1.2: the v1.1 table counted header tags only and undercounted QA-M1, QA-F and QA-DC; v1.2 also adds negative riders to QA-L4-06, QA-L5-02 and QA-DC-09.

---

### 8.1 QA-L1 — Selection model and counts `[L-1]`

**QA-L1-01 `[WF]` — Default selection state is exactly three Inventory rows**
- **Given** the page is loaded in view `All`.
- **When** no interaction has occurred.
- **Then** `.tbl tbody tr[data-view]:not(.crow)` contains **5** rows; the checkboxes in rows `422221`, `422176`, `422165` are `checked`; the checkboxes in rows `MKT-40233` and `422164` are **not** checked; `.bulkbar .cnt` textContent equals `3 selected`.

**QA-L1-02 `[WF]` — The three bulk button labels carry the selection counts**
- **Given** the default state.
- **When** the three `.bulkbar button` elements are read in document order.
- **Then** their textContents equal exactly `🖨 Print Pick Locations (3 orders · 8 items)`, `🖨 Bulk Print Labels (3 orders)`, `📦 Bulk Outbound (3 orders)`.

**QA-L1-03 `[WF]` — The item count reconciles with the visible badges**
- **Given** the default state.
- **When** the `Total Items` badges of the three checked rows are summed (`5` + `1` + `2`).
- **Then** the sum is `8`, which equals the `8 items` in the `[L-2]` label (§3.13 invariant (a), unconditional) **and** the `8 units total` in the M1 header — the latter only because all three default-selected orders are fully inbounded, which is invariant (b)'s equality case. Selecting `MKT-40233` as well would make `{items}` `11` and `{units}` `10`, and that divergence is correct, not a failure [BR-16] [L-13] [E-13].

**QA-L1-04 `[WF]` · negative — Two select-all controls exist and neither is wired**
- **Given** the default state.
- **When** the `Select all` checkbox in `.bulkbar` is clicked, and then the header-cell checkbox `.tbl thead input[type=checkbox]` is clicked.
- **Then** the five row checkboxes are unchanged, `.bulkbar .cnt` still reads `3 selected`, and the three button labels are unchanged. This documents wireframe defect `[RTO-WFX-1]`; the real-admin behavior is asserted by QA-L1-05…09.

**QA-L1-05 `[ADMIN]` — Select all applies to visible rows only and syncs both controls**
- **Given** the real admin with view tab `Marketing` active and one MKT order visible.
- **When** `Select all` is clicked.
- **Then** exactly the visible MKT order is selected; the header checkbox renders checked; switching to `All` shows every other row **unselected**; the button labels read `(1 orders …)` `[PD-38 · OWNER-PENDING]`.

**QA-L1-06 `[ADMIN]` — Per-order selection persists across tab switches**
- **Given** three Inventory rows selected on the `All` tab.
- **When** the operator switches to `JIT`, then back to `All`.
- **Then** the same three orders are still selected and the counts are unchanged [E-2].

**QA-L1-07 `[ADMIN]` · negative — Indeterminate select-all adds, never removes**
- **Given** the `Inventory` tab with 1 of its 3 rows selected, so `Select all` renders indeterminate.
- **When** `Select all` is clicked once.
- **Then** all 3 visible rows are selected — the already-selected row is **not** deselected. **When** it is clicked a second time, **then** all 3 visible rows clear while any selection on other tabs remains [E-50] [BR-17].

**QA-L1-08 `[ADMIN]` · negative — Zero selection disables all three bulk buttons**
- **Given** the real admin with no rows selected.
- **When** the bulk bar is read and each bulk button is clicked.
- **Then** all three buttons expose a disabled state; labels read `(0 orders · 0 items)` / `(0 orders)` / `(0 orders)`; `.cnt` reads `0 selected`; **no** progress starts, **no** toast appears, **no** sound plays, and **no** request is sent [E-1].

**QA-L1-09 `[ADMIN]` · negative — A selected order that leaves the pool is not silently dropped**
- **Given** three orders selected and one of them cancelled on Order Detail by another operator.
- **When** the operator switches view tabs and returns without pressing `Refresh`.
- **Then** the row is still rendered and still selected, and the count still reads `3 selected`; the order is only removed when `Refresh` runs or the batch rejects it [E-51] [E-7].

---

### 8.2 QA-L2 — Print Pick Locations entry point `[L-2]`

**QA-L2-01 `[WF]` — The bulk-bar button opens M1**
- **Given** the default state and `#m-pick` without class `open`.
- **When** the button labeled `🖨 Print Pick Locations (3 orders · 8 items)` is clicked.
- **Then** `#m-pick` gains class `open` and is visible.

**QA-L2-02 `[WF]` · negative — Opening M1 starts no batch and shows no toast**
- **Given** a fresh load, so `document.getElementById('pfill').style.width === ''` and `#toast` has `display:none`.
- **When** `🖨 Print Pick Locations (3 orders · 8 items)` is clicked and 2 s elapse.
- **Then** `#pfill.style.width` is still `''`, `#pbarLabel.childNodes[0].textContent` still equals `Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion`, and `#toast` is still `display:none`. Opening the modal must never print and never toast [BR-34].

**QA-L2-03 `[WF]` — Both `wf-bar` demo buttons reach the same modal**
- **Given** the default state.
- **When** `Modal: Print Pick Locations (Picking List)` is clicked, the modal is closed with `✕`, and `Modal: Print Pick Locations` is clicked.
- **Then** `#m-pick` opens both times. Documents duplicate demo chrome `[RTO-WFX-2]`; only one entry point ships in the admin.

**QA-L2-04 `[ADMIN]` · negative — Disabled at zero selection**
- **Given** no rows selected.
- **When** the Print Pick Locations button is clicked.
- **Then** the modal does not open [E-25] [E-1].

**QA-L2-05 `[ADMIN]` · negative — The entry button never prints**
- **Given** any non-zero selection.
- **When** `🖨 Print Pick Locations` is clicked.
- **Then** no `pickinglist.printed` [DC-5] event is created and no print job is queued. Printing occurs only from the modal's own `🖨 Print` (QA-M1-11).

---

### 8.3 QA-M1 — Picking List modal `[L-M1]`

**QA-M1-01 `[WF]` — Header totals**
- **Given** M1 is open.
- **When** the header's first text node is read (per §8.0).
- **Then** it equals exactly `Print Pick Locations — Picking List (3 orders selected · 4 SKUs · 8 units total)`, and the three numbers reconcile: `8` equals the sum of the selected rows' `Total Items` badges (`5 + 1 + 2`) and equals the `8 items` in the `[L-2]` button label — an equality that holds here because every default-selected order is fully inbounded (§3.13 invariant (b)); `4 SKUs` is the distinct-SKU count of **product** lines; since the `WF-9` fix the table also carries a sample-set row, so `{skus}` no longer coincides with the row count and must never be recomputed from it §3.15 [L-13] [BR-21].

**QA-M1-02 `[WF]` — Column set**
- **Then** `#m-pick .picktbl thead th` textContents are, in order, `Location`, `SKU`, `Product`, `Qty`, `Order`.

**QA-M1-03 `[WF]` — Row count, location-ascending sort, and the trailing sample row**
- **Then** `#m-pick .picktbl tbody tr` has exactly **5** rows: four product rows whose first-column values, in document order, are `A-02-13`, `A-03-02`, `B-01-07`, `B-02-11` — strictly ascending [BR-7] — followed by the sample-set row, whose first cell is a `.locpill` reading `Sample` rather than a location code.
- **And** the sample row is **last** and is excluded from the location ordering: it carries no location, so it cannot participate in the ascending sort [G-13] [BR-21]. *(Re-baselined 2026-08-03: `WF-9` added the sample line; before that this scenario asserted 4 rows.)*

**QA-M1-04 `[WF]` — SKU column values**
- **Then** the second-column values of the four product rows, in document order, are `100039958`, `100039420`, `100035912`, `100013286`, and each matches the `.skupill` of the corresponding main-table item line; the fifth (sample) row's SKU cell reads `—`, because v1 assigns no SKU to the sample set [G-13] [BR-21].

**QA-M1-05 `[WF]` — Korean product names and bold multi-unit quantity**
- **Then** row 2 `Product` equals `마데카 크림 타이트닝`, row 3 equals `세라마이드 아토 컨센트레이트 크림`, row 4 equals `마데카 크림 타임 리버스`; row 1 `Qty` is `5` rendered inside a `<b>` element and its `Order` cell reads `422221`; rows 2–4 `Qty` are `1` and not bold [G-6] [BR-5]; row 5 `Product` reads exactly `sample set` — no sample type and no per-type quantity — and its `Qty` reads `×1` inside a `<b>` element [G-13] `[PD-51]` [BR-21].

**QA-M1-06 `[WF]` — Order column values**
- **Then** the fifth-column values, in document order, are `422221`, `422165`, `422176`, `422165`, `422165` — i.e. the list is ordered by location, **not** grouped by order [BR-7]; the trailing `422165` is the sample-set row, which names the order its sample belongs to [BR-21].

**QA-M1-07 `[WF]` · negative — One row per order × SKU, no merge**
- **Then** the two **product** rows whose `Order` is `422165` (`A-03-02` and `B-02-11`) are **separate**; there is **no** row that aggregates a SKU across two orders, and no `Order` cell contains more than one order number [BR-19] [E-14]. The third row naming `422165` is the sample-set row and is not a product line — exactly one sample row exists for that order, never one per product line [G-13]. **· `[ADMIN]` rider — the `{skus}` divergence this creates:** when two selected orders need the **same** SKU, the picking table gains two rows while the header's `{skus}` stays at the distinct-SKU count, so `{skus}` < row count. The header must not be recomputed from the row count §3.15 [E-14].

**QA-M1-08 `[WF]` · negative — The un-inbounded MKT line is absent**
- **Then** no picking-list row carries SKU `100012534` (the `Dr.Jart+ 시카페어 슬리페어 마스크` line that shows `Not inbounded`), and no row's `Location` cell reads `Not inbounded`. Non-pickable lines never reach the picker's paper [E-3].

**QA-M1-09 `[WF]` · negative — Missing brand prefix is the known defect, not the spec**
- **Then** row 2 `Product` does **not** contain `Centellian24`, while the main-grid row for order `422165` does render `<b>Centellian24</b>`; and row 1 `Product` reads the elided English `AtoBarrier365 Body …` rather than a Korean name. This records `[RTO-WFX-5]`; the specified behavior is Korean name **with** bold EN brand in M1 as well [BR-6].

**QA-M1-10 `[WF]` — Note block copy**
- **Then** `#m-pick .note` textContent equals `Sorted by location (ascending) (A-02-13 → B-01-07 → Shelf 3) — pick everything in one pass along the route. Printing: no refresh · selection kept; progress bar, then a top-right completion toast.`

**QA-M1-11 `[WF]` — Print closes the modal and runs the batch in print mode**
- **Given** M1 is open on a fresh load.
- **When** `🖨 Print` is clicked.
- **Then** `#m-pick` loses class `open`; `#pfill.style.width` progresses to `100%`; **from the first progress tick onward** (sample only once `#pfill.style.width` is `20%` or greater — §8.0 running-label rule) `#pbarLabel.childNodes[0].textContent` contains `Print Pick Locations in progress` **and** `No refresh · selection kept` and does **not** contain `refreshes after completion`; at 100 % `#toast` becomes visible with `#toast b` textContent `✓ Print Pick Locations complete — 3 orders`; the five order rows are still present and the three checkboxes are still checked (selection kept) [BR-8].

**QA-M1-12 `[WF]` · negative — Cancel, `✕`, and backdrop all close without printing**
- **Given** a fresh load and M1 open.
- **When** `Cancel` is clicked; then M1 is reopened and the overlay backdrop (`#m-pick` itself, outside `.modal`) is clicked; then M1 is reopened and `✕` is clicked.
- **Then** each time `#m-pick` loses class `open`, and after all three `#pfill.style.width` is still `''` and `#toast` is still hidden `[NE-4]` [BR-34].

**QA-M1-13 `[ADMIN]` — Print output and snapshot**
- **When** `🖨 Print` is clicked in the real admin.
- **Then** the picking list emerges from the configured printer with **no browser dialog and no new tab** [G-4]; a `pickinglist.printed` event [DC-5] persists with the full line snapshot, `sort = location_asc`, and totals matching the header; a `print.job_result` [DC-12] with `artifact_type = picking_list` reaches `done`. **· negative:** no `order.status_changed` and no stock event is emitted by printing [BR-31].

**QA-M1-14 `[ADMIN]` · negative — Reprint of the same selection is byte-identical**
- **Given** a selection whose two orders need the same location code.
- **When** the picking list is printed twice with no data change in between.
- **Then** the two snapshots [DC-5] have identical row order — ties broken by order id then SKU [BR-20] [E-65].

**QA-M1-15 `[ADMIN]` · negative — Stale data is re-rendered, not printed**
- **Given** M1 is open and another session outbounds one of the selected orders.
- **When** `🖨 Print` is clicked.
- **Then** the modal re-renders against current data and **no** stale paper is produced [E-30] [E-36] `[PD-6 · OWNER-PENDING]`.

---

### 8.4 QA-L3 — Bulk Print Labels `[L-3]`

**QA-L3-01 `[WF]` — Progress mode text is the print mode**
- **Given** a fresh load.
- **When** `🖨 Bulk Print Labels (3 orders)` is clicked.
- **Then** **from the first progress tick onward** (sample only once `#pfill.style.width` is `20%` or greater — §8.0 running-label rule) `#pbarLabel.childNodes[0].textContent` contains `Bulk Print Labels in progress` and `No refresh · selection kept`, and does **not** contain `refreshes after completion` [BR-8].

**QA-L3-02 `[WF]` — Completion toast text and subtext**
- **Then** at 100 % `#toast b` textContent equals `✓ Bulk Print Labels complete — 3 orders` and `#toast small` textContent equals `Disappears automatically after a few seconds`.

**QA-L3-03 `[WF]` · negative — No refresh, no sound, selection kept**
- **Given** a sentinel property is set on `window` before the click and `sndOutbound.ac` is `undefined`.
- **When** `🖨 Bulk Print Labels (3 orders)` is clicked and the run completes.
- **Then** the sentinel still exists (the page did not reload); `sndOutbound.ac` is **still** `undefined` (no outbound sound was played); and the three row checkboxes are still checked [BR-8] [G-3a].

**QA-L3-04 `[WF]` · negative — The button is not sound-bound**
- **Then** the Bulk Print Labels button's textContent contains no `Outbound` substring, so it cannot satisfy the wireframe's sound-binding predicate; only `📦 Bulk Outbound (3 orders)` does (QA-L4-04).

**QA-L3-05 `[ADMIN]` — Carrier-agnostic fan-out**
- **Given** a selection mixing a Deleo order and a YUN order.
- **When** Bulk Print Labels runs.
- **Then** each order's label is produced with **its own** carrier template, one `label.printed` [DC-7] per order carrying that carrier, one `label.batch_printed` [DC-6] envelope, and `print.job_result` [DC-12] per physical job [G-4] [BR-10].

**QA-L3-06 `[ADMIN]` · negative — Print agent offline**
- **Given** the local print agent is unreachable.
- **When** Bulk Print Labels runs.
- **Then** a **red** toast names the agent/printer; the completion toast does **not** claim success for the failed orders; the orders remain in the list; `print.job_result` = `failed` [DC-12] and `print.batch_infrastructure_failure` [DC-24] persist; **no** browser print dialog is ever shown as a fallback [E-11] `[PD-34 · OWNER-PENDING]`.

**QA-L3-07 `[ADMIN]` · negative — An order with no carrier is excluded, not silently skipped**
- **Given** a selection containing one "Not connected — contact the Fulfillment Center" order.
- **When** Bulk Print Labels runs.
- **Then** that order produces no label; `#toast small` reads exactly `1 excluded — no carrier assigned` (§3.3 reason-aware subtext), **not** the default sentence and **not** the Bulk Outbound copy `items not inbounded`; `label.print_refused` persists with `reason = no_carrier` [DC-28]; the other orders print normally [E-61] `[PD-55 · NO-DEFAULT]`.

**QA-L3-08 `[ADMIN]` · negative — Printing changes no order state**
- **When** Bulk Print Labels completes for 3 orders.
- **Then** no `order.status_changed` [DC-19], no `order.outbounded` [DC-9], and no stock event [DC-10] exists for any of them; the three rows are still present and still ready [BR-31] [BR-33].

---

### 8.5 QA-L4 — Bulk Outbound `[L-4]`

**QA-L4-01 `[WF]` — Send sound path executes on click**
- **Given** a fresh load, so `sndOutbound.ac` is `undefined`.
- **When** `📦 Bulk Outbound (3 orders)` is clicked.
- **Then** **no uncaught exception** is raised, and — in any environment where `window.AudioContext` (or `webkitAudioContext`) is constructible — `sndOutbound.ac` is an `AudioContext` instance **constructed inside this click gesture**, proving both that the sound path ran and that the first user gesture of the session may itself be the Bulk Outbound click [G-3a] [E-49]. In an environment without Web Audio the scenario still passes on the no-exception clause alone, which is the normative half [E-24].

**QA-L4-02 `[WF]` — Progress mode text is the refresh mode**
- **Then** **from the first progress tick onward** (sample only once `#pfill.style.width` is `20%` or greater — §8.0 running-label rule) `#pbarLabel.childNodes[0].textContent` contains `Bulk Outbound in progress` **and** `refreshes after completion`, and does **not** contain `No refresh · selection kept` [BR-8].

**QA-L4-03 `[WF]` — Completion toast text**
- **Then** at 100 % `#toast` is visible with inline `display:flex`, positioned top-right, and `#toast b` textContent equals `✓ Bulk Outbound complete — 3 orders`; the toast returns to `display:none` within **3–4 s of becoming visible** — the window is measured from the toast appearing, **not** from the click that started the batch (measured reference: visible at ~1.25 s after the click, hidden ~3.0 s later).

**QA-L4-04 `[WF]` · negative — Exactly one control on the page is sound-bound**
- **Given** the page is loaded.
- **When** every `button` element is tested against the wireframe's binding predicate (`/Outbound/` matches the textContent, `/Cancel/` does not, `/Outbounded/` does not).
- **Then** exactly **one** button qualifies: `📦 Bulk Outbound (3 orders)`. Neither print button, no view tab, no row button, and no modal button plays the send sound [G-3a] §6.5.

**QA-L4-05 `[WF]` · negative — The page title's `Outbonded` does not create a second sound binding**
- **Then** no element whose text contains `Ready to be Outbonded` is a `button`, so the misspelled title cannot accidentally satisfy the predicate. (Confirms the binding is text-based but safely scoped `[L-F1]`.)

**QA-L4-06 `[ADMIN]` — State transition and stock movement**
- **When** Bulk Outbound runs on three fully-inbounded orders.
- **Then** each order's status becomes `prepare-shipment` [BR-22]; `order.outbounded` [DC-9], `order.status_changed` [DC-19], `inventory.stock_decremented` [DC-10] and `inventory.reservation_consumed` [DC-20] persist with old→new values; the three rows are gone after the refresh; the orders appear in Closing's scan population. **· negative:** **no line-level status is written** — every line's `inbound_status` still reads `INBOUNDED`, no `OUTBOUNDED` line value exists anywhere in the store or on the Order Detail rendering of these orders, and the shipped-line detail lives only inside [DC-9]'s payload [BR-22].

**QA-L4-07 `[ADMIN]` · negative — Idempotent double click**
- **When** `📦 Bulk Outbound` is double-clicked.
- **Then** exactly one batch executes; stock is decremented **once**; the duplicate is persisted as `idempotency.duplicate_rejected` [DC-11]; the completion toast appears once [E-9] [G-9]. **This is the mandatory regression test for the known current-admin double-processing bug** [BR-13].

**QA-L4-08 `[ADMIN]` · negative — Ineligible orders are excluded, not partially shipped**
- **Given** a selection containing `MKT-40233` (one line not inbounded), one on-hold order, and two fully-inbounded orders.
- **When** Bulk Outbound runs.
- **Then** only the two fully-inbounded orders are outbounded; the toast reads `✓ Bulk Outbound complete — 2 orders` with subtext exactly `2 excluded — 1 items not inbounded · 1 status blocks outbound` — **two reasons, so two clauses in enum order; the single-phrase form `2 excluded — items not inbounded` is a FAIL here**, because it tells the operator to chase a receiving problem for an order that only needs its hold released (§3.4 step 6); **no** line of `MKT-40233` is outbounded (no partial outbound); `outbound.order_excluded` [DC-21] persists with `lines_not_inbounded` and `status_forbids_outbound` respectively [E-3] [E-21] [E-33] `[PD-35 · OWNER-PENDING]` `[PD-29 · OWNER-PENDING]`.

**QA-L4-09 `[ADMIN]` — Fully-inbounded JIT rows are eligible**
- **Given** a selection containing only the JIT row `422164` (`Fully Inbounded`).
- **When** Bulk Outbound runs.
- **Then** the order is outbounded normally; it is **not** excluded `[PD-35 · OWNER-PENDING]` [E-4].

**QA-L4-10 `[ADMIN]` · negative — All orders excluded still toasts, with zero**
- **Given** a selection of three orders that are all excluded **for the same reason** (three MKT rows with non-inbounded lines).
- **Then** the toast reads exactly `✓ Bulk Outbound complete — 0 orders` with subtext exactly `3 excluded — items not inbounded` (one shared reason ⇒ the single-phrase form); it is green, not red; no stock event and no `order.outbounded` exists; the page still refreshes [E-53] [BR-35].

**QA-L4-11 `[ADMIN]` · negative — Counts are never pluralised**
- **Given** a batch that outbounds exactly one order.
- **Then** the toast reads `✓ Bulk Outbound complete — 1 orders`, **not** `1 order`; and `#foundTxt` on the refreshed page still uses its own `order(s)` form [E-54] [BR-35].

**QA-L4-12 `[ADMIN]` — Shelf is cleared on outbound**
- **Given** an order carrying a temporary shelf value.
- **When** it is outbounded.
- **Then** `order.outbounded` [DC-9] records `shelf` old→`null`, and the next screen that reads the order shows no shelf `[PD-18 · OWNER-PENDING]`.

**QA-L4-13 `[ADMIN]` — Ordering of sound, progress, toast, refresh**
- **When** Bulk Outbound completes.
- **Then** the observed sequence is send sound → progress 0→100 → completion toast → page refresh, and the toast is re-rendered after the reload so it is still readable [E-37] [G-2].

---

### 8.6 QA-L5 — Shared progress bar `[L-5]`

**QA-L5-01 `[WF]` — One bar, shared by all three actions**
- **Then** the document contains exactly one `.pbar` and one `#pfill`; running `🖨 Bulk Print Labels`, then M1 `🖨 Print`, then `📦 Bulk Outbound` animates the same `#pfill` each time.

**QA-L5-02 `[WF]` — Monotonic 0 → 100**
- **Given** a fresh load.
- **When** any bulk action runs and `#pfill.style.width` is sampled every 100 ms.
- **Then** the samples begin at `0%`, never decrease, and end at `100%`. **· negative:** `[ADMIN]` rider — in the real admin the same run leaves **no per-tick row** in the [G-8] audit stream; only [DC-8]'s batch start and finish are persisted `[NE-2]`.

**QA-L5-03 `[WF]` — Label pattern**
- **Then** in any run, **from the first progress tick onward** (`#pfill.style.width` ≥ `20%` — §8.0 running-label rule), `#pbarLabel.childNodes[0].textContent` matches `{Action} in progress — {p}% · {mode} · toast on completion`, where `{Action}` ∈ {`Print Pick Locations`, `Bulk Print Labels`, `Bulk Outbound`} and `{mode}` is that action's mode string.

**QA-L5-04 `[WF]` · negative — Mode strings never cross over**
- **Given** a fresh load.
- **When** each of the three actions is run in turn and `#pbarLabel.childNodes[0].textContent` is sampled continuously, **discarding every sample taken before `#pfill.style.width` reaches `20%`** (§8.0 running-label rule — before the first tick the label still holds the previous action's copy — `[RTO-WFX-9]`).
- **Then** across the retained samples a `Bulk Outbound` run **never** renders `No refresh · selection kept`, and neither print run **ever** renders `refreshes after completion` [BR-8]. *(Asserted absolutely without the first-tick bound, this scenario is unsatisfiable against the wireframe — the crossover it would report is the demo artifact, not a mode-string defect.)*

**QA-L5-05 `[WF]` · negative — The idle label is demo copy, not a live state**
- **Given** a fresh load with no batch run.
- **Then** `#pbarLabel.childNodes[0].textContent` equals `Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion`, and the `3/5` fraction appears in **no** running state — the live pattern is a percentage only [L-5].

**QA-L5-06 `[ADMIN]` · negative — Concurrent-start lockout**
- **When** a second bulk button is clicked while a batch is running.
- **Then** the click is rejected: no second batch starts, no second progress state appears, and no second toast is queued [BR-18] [E-19]. *(The wireframe does not lock — admin-only.)*

**QA-L5-07 `[ADMIN]` · negative — Refresh and view tabs are locked too**
- **When** `Refresh` or a view tab is clicked during a running batch.
- **Then** neither takes effect until the batch completes [E-52] [E-57] [BR-18].

---

### 8.7 QA-L6 — Completion toast `[L-6]`

**QA-L6-01 `[WF]` — Position and auto-dismiss**
- **When** any bulk action completes.
- **Then** `#toast` has inline `display:flex`, is anchored top-right (CSS `top:54px; right:16px` within `.mock`), and returns to `display:none` within **3–4 s of becoming visible** — anchored to the toast appearing, never to the click that started the batch.

**QA-L6-02 `[WF]` — Text pattern per action**
- **Then** running each of the three actions produces, in turn, `✓ Print Pick Locations complete — 3 orders`, `✓ Bulk Print Labels complete — 3 orders`, `✓ Bulk Outbound complete — 3 orders` in `#toast b`.

**QA-L6-03 `[WF]` · negative — Single-slot replacement**
- **When** `🖨 Bulk Print Labels` is clicked and, before its toast dismisses, `📦 Bulk Outbound` is clicked.
- **Then** at most one `#toast` element is visible at any moment and its text is the most recent action's [E-18].

**QA-L6-04 `[WF]` · negative — No failure variant exists in the completion notice**
- **Then** all four clauses hold, each mechanically:
  1. `document.querySelectorAll('.toast').length === 1` — there is exactly one toast element, so no second, differently-styled completion toast exists.
  2. `getComputedStyle(document.getElementById('toast')).backgroundColor === 'rgb(25, 135, 84)'` — the `--green` value `#198754`.
  3. Scanning every rule in `document.styleSheets` whose `selectorText` contains `toast`, **none** has a `cssText` containing `--red` or `--red-soft`; and no element in the document carries a class matching `/toast/` other than `#toast` itself.
  4. After each of the three actions, neither `#toast b` nor `#toast small` contains `failed`, `error`, or `partial` [BR-9] §4.2.

**QA-L6-05 `[WF]` · negative — The subtext is the default copy when nothing is excluded**
- **Then** after any wireframe batch `#toast small` equals `Disappears automatically after a few seconds` and never the exclusion subtext, because the wireframe has no exclusion path [L-6].

**QA-L6-06 `[ADMIN]` — Infrastructure failure raises a separate red toast**
- **Given** the print agent is offline during Bulk Print Labels.
- **Then** the completion toast stays green and all-success, **and** a distinct red toast reports the failure; both outcomes are persisted ([DC-6]/[DC-24]) [BR-9b] `[PD-34 · OWNER-PENDING]`.

**QA-L6-07 `[ADMIN]` · negative — When both toasts are due, the red one is what remains**
- **Given** single-slot replacement and a batch that completes with an infrastructure failure.
- **Then** the green toast renders first and is replaced by the red one, so the operator's last-read state is the problem [E-79]. Both events persist regardless of what the slot showed.

**QA-L6-08 `[ADMIN]` · negative — Exclusion subtext replaces, not appends**
- **Given** a Bulk Outbound with 2 exclusions that share the reason `lines_not_inbounded`.
- **Then** `#toast small` reads exactly `2 excluded — items not inbounded` and the default sentence `Disappears automatically after a few seconds` is **absent**, not appended after it. **When** the same batch instead excludes one order per reason, **then** the subtext is the multi-clause form of §3.4 step 6 and still **replaces** the default sentence `[PD-35 · OWNER-PENDING]`.

---

### 8.8 QA-L7 — JIT row `[L-7]`

**QA-L7-01 `[WF]` — Badge text is exactly `Fully Inbounded`**
- **Then** the row containing Order ID `422164` has a `.jit-badge` whose textContent equals `Fully Inbounded`.

**QA-L7-02 `[WF]` · negative — The old wording is absent from every shipping surface**
- **Then** `document.querySelector('.mock').textContent` and `document.querySelector('#m-pick').textContent` contain **no** occurrence of `JIT (channel) completed` — not in the table, not in any row badge, not in the modal [BR-4] §4.2.
- **The `.legend` and `.wf-bar` are exempt and must not be scanned:** they are wireframe chrome that ships in no admin build (QA-F-09), and legend item 7 deliberately records the 2026-08-03 rename by quoting the superseded string — a dated changelog cannot name a rename without it. Asserting over `document.body` instead would file a bug against a correct wireframe (§8.0 known artifacts).

**QA-L7-03 `[WF]` — Yellow tint and bottom sort**
- **Then** the `422164` row carries class `row-jit`; and in view `All` it is the **last** order row in document order, after `MKT-40233` [BR-2].

**QA-L7-04 `[ADMIN]` — Badge condition is a conjunction**
- **Given** a JIT order with one line still not inbounded.
- **Then** the row shows **no** `Fully Inbounded` badge and is **not** forced to the bottom group; the badge appears only when every line is inbounded and the order is not yet outbounded [DC-15].

**QA-L7-05 `[ADMIN]` · negative — MKT wins the classification when an order is both**
- **Given** an order that is MKT-imported and JIT-sourced.
- **Then** it renders purple with the `MKT` badge, appears under the `Marketing` tab only, and sorts in the middle group — while its Pick Locations cell still reads `Shelf N` [E-70] [BR-36]. It must **not** appear in two tabs.

---

### 8.9 QA-L8 — Marketing row `[L-8]`

**QA-L8-01 `[WF]` — Purple tint and MKT badge**
- **Then** the row containing `MKT-40233` carries class `row-mkt` and contains a `.mkt-badge` with textContent `MKT`.

**QA-L8-02 `[WF]` — PIC line**
- **Then** the Customer cell of that row contains `Influencer @glowwithjade` and a second line reading exactly `PIC: Harshit`.

**QA-L8-03 `[WF]` — Amber `Not inbounded` pill replaces a location**
- **Then** the Pick Locations cell of that row contains two `.locpill` elements; the first reads `A-01-04`, the second reads `Not inbounded` and is styled amber (background `--amber-soft`, border `--amber-line`, colour `--amber`) [BR-23].

**QA-L8-04 `[WF]` — Sort position between Ready and JIT**
- **Then** in view `All` the order-row sequence is `422221`, `422176`, `422165`, `MKT-40233`, `422164` [BR-2].

**QA-L8-05 `[ADMIN]` · negative — MKT visibility is not gated on stock**
- **Given** a freshly imported MKT order whose products have zero stock and no inbound.
- **Then** it appears in this list immediately with every line showing `Not inbounded`; **no** import error, **no** hidden state, **no** stock validation blocks it [BR-3] [DC-14].

**QA-L8-06 `[ADMIN]` · negative — Missing PIC renders a placeholder, never a blank line**
- **Given** an MKT order with no PIC.
- **Then** the Customer cell renders `PIC: —` [E-42] [D-11].

**QA-L8-07 `[ADMIN]` · negative — A deactivated PIC keeps its name**
- **Given** the PIC user was deactivated after the import.
- **Then** the stored display name still renders with a neutral inactive marker; the line is never removed [E-71].

---

### 8.10 QA-L9 — Inline comments `[L-9]`

**QA-L9-01 `[WF]` — Panel expands under the row**
- **When** the `.cmtbtn` in row `422221` (`💬 1`) is clicked.
- **Then** `#crow1` changes from `display:none` to `display:table-row` and is the row immediately below the `422221` row.

**QA-L9-02 `[WF]` — Existing comment renders author, mention, text, time**
- **Then** `#crow1` contains `Egita`, an `.at` element reading `@Yongwon`, the text `Please double-check the ×5 quantity.` (**with** the trailing period — the hub renders the same comment without it, see `[RTO-WFX-8]`), and a `time` element reading `07-21 09:40`.

**QA-L9-03 `[WF]` — Placeholder copy is exact**
- **Then** `#crow1 input` `placeholder` equals `Write a comment — @mention sends an automatic Slack notification (order no. · text · time · author)`, and `#crow2 input` placeholder equals `Write a comment — @mention sends an automatic Slack notification`. The admin ships the long form everywhere.

**QA-L9-04 `[WF]` — Empty state**
- **When** the `.cmtbtn` in row `422176` is clicked.
- **Then** `#crow2` shows `No comments yet` in muted text and still offers the write row with a `Post` button.

**QA-L9-05 `[WF]` — Unread badges on row buttons**
- **Then** the `.cmtbtn` in rows `422221` and `422165` each contain a `.badge-n` with textContent `1`; the buttons in `422176`, `MKT-40233`, `422164` contain none.

**QA-L9-06 `[WF]` · negative — Panel ids are out of document order and the star is per-comment**
- **Then** `#crow4` belongs to the **JIT** row `422164` and `#crow5` to the **MKT** row `MKT-40233`; clicking `.cmtbtn[data-open="crow5"]` opens the panel under the MKT row, not under the JIT row. Documents `[RTO-WFX-8]`; the id numbering carries no meaning.

**QA-L9-07 `[ADMIN]` · negative — Empty post is blocked**
- **When** `Post` is clicked with an empty or whitespace-only input.
- **Then** no request is sent, no comment is created, **no toast appears**, and inline feedback explains the block [E-16] [BR-34].

**QA-L9-08 `[ADMIN]` — A successful post appends in place and toasts**
- **When** a non-empty comment is posted from the inline panel.
- **Then** it appears at the bottom of that panel without a page navigation, a green toast `✓ Comment posted` shows [BR-34], and `comment.posted` [DC-1] persists with `source = rto_inline_panel`. *(The wireframe does neither — `[RTO-WFX-7]`.)*

**QA-L9-09 `[ADMIN]` · negative — Comments cannot be edited or deleted**
- **Then** no edit affordance and no delete affordance exists on any comment, and no `comment.updated` / `comment.deleted` event type exists [BR-27] `[PD-3 · OWNER-PENDING]`.

**QA-L9-10 `[ADMIN]` · negative — Comment bodies are escaped, not executed**
- **When** a comment whose text is `<img src=x onerror=alert(1)>` is posted and then viewed in the inline panel, the hub list, and a hub search result that highlights part of it.
- **Then** the literal text is displayed in all three surfaces, **no** script executes, and the `<mark>` wrapper is inserted around escaped text [E-74] [BR-37].

**QA-L9-11 `[ADMIN]` · negative — One Slack message per distinct mention, and duplicates collapse**
- **When** (a) a comment mentioning three **different** users is posted, and (b) a second comment naming the **same** user twice is posted.
- **Then** (a) **three** messages reach `#fulfillment-admin-comments` and three `comment.mention_notified` [DC-2] events persist, one per distinct resolved user — matching `view-orders.md` `DC-20` and `order-detail.md` §6.1; and (b) the duplicate-mention comment produces **exactly one** message and one event, **not** two [E-75] [G-7].

---

### 8.11 QA-L10 — Comments hub `[L-10]`

**QA-L10-01 `[WF]` — Opens from the nav with an unread badge**
- **When** `.icon-btn[data-open="inbox1"]` (`💬 Comments`) is clicked.
- **Then** `#inbox1` gains class `open`; the button's `.badge-n` reads `2`.

**QA-L10-02 `[WF]` — Mentions pane content**
- **Then** the `[data-pane="mentions"]` pane contains exactly 2 `.it.unread` entries: `Order 422165 · Dean: "@Yongwon Please take extra care packing this order"` at `10:12`, and `Order 422221 · Egita: "@Yongwon Please double-check the ×5 quantity"` at `09:40`; the pane header reads `Comments mentioning me · Click to open the order` with a `Mark all read` action.

**QA-L10-03 `[WF]` — Tab switch to Saved**
- **When** the `★ Saved` tab is clicked.
- **Then** the mentions pane hides, the saved pane shows exactly 1 entry (`Order 422221 · Egita`), and its header reads `Saved comments · Click to open the order` with `Unstar to remove from the list`.

**QA-L10-04 `[WF]` — Star toggle is confirmed in place**
- **When** the `★` on the first mentions entry is clicked.
- **Then** it gains class `on`; clicking again removes it; **no toast is shown at any point** — the glyph is the confirmation [BR-34].

**QA-L10-05 `[WF]` — Search hides tabs and renders results newest-first with highlight**
- **When** `422` is typed into `#inbox1 .csearch input`.
- **Then** `.tabs` is hidden (`display:none`); a `[data-pane="csr"]` pane appears whose header reads `4 results · newest first · click to open the order`; the results are ordered `422165` (Today 10:12), `422221` (Today 09:40), `422176` (Today 08:52), `422108` (Yesterday 16:45); each matched substring is wrapped in `<mark>`.

**QA-L10-06 `[WF]` — Search matches author text too**
- **When** `Aldo` is typed.
- **Then** exactly 1 result renders, for `Order 421990` — an order that is **not** a row in this table [E-38].

**QA-L10-07 `[WF]` · negative — No-match empty state**
- **When** `zzzz` is typed.
- **Then** the results pane header reads `0 results · newest first · click to open the order` and the body shows `No matching comments`.

**QA-L10-08 `[WF]` · negative — Clearing the box restores the previously active tab**
- **Given** the `★ Saved` tab was active before typing.
- **When** the query is cleared to an empty string.
- **Then** `.tabs` is visible again and the **Saved** pane is the one displayed, not Mentions.

**QA-L10-09 `[WF]` · negative — Outside click closes, inside click does not**
- **When** the hub is open and a click lands inside `#inbox1` (e.g. on the search input), then a click lands on the page background.
- **Then** the hub stays open for the inside click and loses class `open` for the outside click.

**QA-L10-10 `[WF]` · negative — Search spans all five seeded comments, not just the table's orders**
- **When** `4` is typed (a substring of every seeded order number).
- **Then** 5 results render, including `422108` and `421990`, neither of which is a table row — proving the scope is the comment corpus, not the current list [G-7] [E-38].

**QA-L10-11 `[ADMIN]` · negative — Badge reconciliation after Mark all read**
- **When** `Mark all read` is clicked.
- **Then** the nav badge reads `0`, every per-row `💬` badge clears in the same render, a green toast `✓ All mentions marked as read` shows [BR-34], and `comment.mark_all_read` [DC-4] persists with the full transitioned id list [E-26]. *(Inert in the wireframe.)*

**QA-L10-12 `[ADMIN]` — Clicking a hub entry opens that order**
- **When** any hub entry is clicked, including one for an order absent from the ready list.
- **Then** Order Detail opens for that order [G-12] [E-38].

---
### 8.12 QA-L11 — Layout `[L-11]`

**QA-L11-01 `[WF]` — Reduced side padding**
- **Then** `getComputedStyle(document.querySelector('.pagepad')).padding` equals `16px 14px 0px` — full-width layout, no wide gutters `[L-11]`.

**QA-L11-02 `[WF]` · negative — Columns scroll, they do not collapse**
- **Then** `.mockwrap` has `overflow-x: auto` and `.mock` has `min-width: 1240px`, so narrowing the viewport produces a horizontal scrollbar rather than dropped or wrapped columns [E-73] [L-F7].

---

### 8.13 QA-L12 — Pick Locations column `[L-12]`

**QA-L12-01 `[WF]` — Column position and header**
- **Then** the table's 7th `th` textContent starts with `Pick Locations`, positioned immediately after `Ready Item Details`.

**QA-L12-02 `[WF]` — Line-for-line vertical pairing**
- **Then** for row `422165` the Ready Item Details cell contains 2 `.item-line` elements and the Pick Locations cell contains 2 `.locline` elements; the first locator is `A-03-02` (pairing with `마데카 크림 타이트닝`) and the second is `B-02-11` (pairing with `마데카 크림 타임 리버스`).

**QA-L12-03 `[WF]` — Shelf pill for JIT**
- **Then** row `422164`'s Pick Locations cell contains a single `.locpill` reading `Shelf 3`.

**QA-L12-04 `[WF]` · negative — No cell is empty on any of the five rows**
- **Then** every `.locline` on every order row contains a non-empty `.locpill`; no Pick Locations cell renders as whitespace [BR-23].

**QA-L12-05 `[ADMIN]` · negative — Missing location never renders blank**
- **Given** a ready line whose SKU has no registered location.
- **Then** the cell renders an explicit unknown marker and the corresponding picking-list row still appears with the same marker; the cell is never empty and the row is never dropped [E-15] [BR-23] [D-11].

**QA-L12-06 `[ADMIN]` · negative — Locator list is never re-sorted independently of the item list**
- **Given** an order whose lines would sort differently by location than by line order.
- **Then** the locator column preserves the item column's order so the vertical pairing holds; a data-level mismatch pads with the unknown marker instead of shifting rows [E-15b].

---

### 8.14 QA-L13 — Total Items `[L-13]`

**QA-L13-01 `[WF]` — Unit sum, not SKU count**
- **Then** the `Total Items` badge of row `422221` reads `5` (one SKU × 5 units), row `422176` reads `1`, and row `422165` reads `2` (two SKUs × 1 unit each) [BR-5].

**QA-L13-02 `[WF]` — Mixed order counts all units**
- **Then** row `MKT-40233` reads `3`, even though only 2 of its 3 units are inbounded [BR-16] `[PD-37 · OWNER-PENDING]`.

**QA-L13-03 `[WF]` · negative — The removed Ready Items column does not exist**
- **Then** `document.querySelectorAll('.tbl thead th').length` is exactly **9** (qualified selector — a bare `th` count returns 14) and there is no second count column; **no element in the document uses the class `cb-ready`**, even though the stylesheet still defines it — recorded as `[RTO-WFX-4]`, and the class itself must be deleted §4.2.

**QA-L13-04 `[ADMIN]` — Reconciliation invariants: one unconditional, one conditional**
- **Given** any selection.
- **Then (a), unconditionally:** `Σ(Total Items of selected rows)` equals the `{items}` figure in the `[L-2]` label, in **every** case including selections containing partially-inbounded orders [BR-16] `[PD-37 · OWNER-PENDING]`.
- **And (b), conditionally:** the `{units}` figure in the M1 header equals `Σ(qty of inbounded lines only)`. It equals `{items}` **only when every selected order is fully inbounded**; with a partially-inbounded order selected it is lower by exactly that order's non-inbounded unit count. **Asserting (b) unconditionally is itself the defect** — it would force non-inbounded units onto the picking list and send pickers after goods that are not in the building §3.13 [E-13].

**QA-L13-05 `[ADMIN]` · negative — A defective quantity does not break the arithmetic**
- **Given** a ready line with quantity `0`.
- **Then** the line is rendered and visually flagged rather than hidden, and **both** invariants above still hold — (a) exactly, and (b) with the same non-inbounded offset it had before [E-46].

---

### 8.15 QA-L14 — View tabs `[L-14]`

**QA-L14-01 `[WF]` — Default tab and counts in labels**
- **Then** `.vtab[data-view="all"]` has class `on`; the four tab labels read `All (5)`, `Inventory (3)`, `Marketing (1)`, `JIT (1)`; and `3 + 1 + 1 = 5`, confirming the predicates are mutually exclusive and exhaustive [L-14].

**QA-L14-02 `[WF]` — Inventory tab**
- **When** `Inventory` is clicked.
- **Then** exactly rows `422221`, `422176`, `422165` are visible and `#foundTxt` textContent equals `Found 3 order(s) with items ready for outbound`.

**QA-L14-03 `[WF]` — Marketing tab**
- **When** `Marketing` is clicked.
- **Then** exactly `MKT-40233` is visible and `#foundTxt` equals `Found 1 order(s) with items ready for outbound`.

**QA-L14-04 `[WF]` — JIT tab**
- **When** `JIT` is clicked.
- **Then** exactly `422164` is visible, it shows the `Fully Inbounded` badge, carries class `row-jit`, its Pick Locations cell reads `Shelf 3`, and `#foundTxt` equals `Found 1 order(s) with items ready for outbound`.

**QA-L14-05 `[WF]` · negative — Comment panels collapse on tab switch and stay collapsed**
- **Given** `#crow1` has been expanded by clicking the `💬 1` button on row `422221`.
- **When** the `JIT` tab is clicked, then the `All` tab is clicked.
- **Then** `#crow1` is `display:none` after the first switch **and remains hidden** after returning to `All`, while all 5 order rows are visible and `#foundTxt` equals `Found 5 order(s) with items ready for outbound` [E-17].

**QA-L14-06 `[WF]` · negative — Exactly one tab is ever active**
- **When** the tabs are clicked in the order `Inventory` → `Marketing` → `JIT` → `All`.
- **Then** after each click exactly one `.vtab` carries class `on`, and the final state shows all 5 order rows.

**QA-L14-07 `[WF]` · negative — `order(s)` is never pluralised away**
- **Then** on the `Marketing` tab `#foundTxt` reads `Found 1 order(s) with items ready for outbound` — the literal `order(s)` form is preserved even when the count is 1 [BR-35] [L-F3].

**QA-L14-08 `[ADMIN]` — Tab counts recompute from the row source**
- **Given** an MKT order is outbounded elsewhere and the list is refreshed.
- **Then** the `Marketing` tab label and `#foundTxt` both fall by one, from the same source; a tab that reaches `0` still renders and shows `Found 0 order(s) with items ready for outbound` [E-5].

---

### 8.16 QA-F — Page furniture `[L-F1]`…`[L-F8]`

**QA-F-01 `[WF]` · negative — Title spelling is preserved**
- **Then** `.ptitle h2` textContent equals `WMS - Ready to be Outbonded` and `.psub h3` equals `Ready to be Outbonded Orders`; **the string `Outbounded` must not appear in either element**. The browser `<title>` and the `wf-bar` `h1` *do* spell it `Outbounded` — that is wireframe chrome and must **not** be filed as a defect `[L-F1]`.

**QA-F-02 `[WF]` — Refresh button present**
- **Then** a `button.btn.btn-blue` with textContent `Refresh` exists in the `.psub` heading row `[L-F2]`.

**QA-F-03 `[WF]` — Found line**
- **Then** `#foundTxt` textContent equals `Found 5 order(s) with items ready for outbound` on load `[L-F3]`.

**QA-F-04 `[WF]` — How-to block is verbatim**
- **Then** `.howto` contains a bold `How to use:` and exactly 5 `li` elements whose textContents equal, in order: `Click "Refresh" to load the latest orders ready for outbound` · `Orders shown here have at least one line item with "INBOUNDED" status` · `Click the Order ID link to see full order details and process outbound` · `Only items marked as INBOUNDED are ready for outbound processing` · `This page uses the dedicated readyToBeOutbonded API for optimized results` `[L-F4]` [BR-1].

**QA-F-05 `[WF]` — Table contract**
- **Then** `.tbl thead th` has exactly 9 elements; the first contains an `input[type=checkbox]` and has empty textContent; the remaining eight textContents start with `Order ID`, `Order Date`, `Customer`, `Total Items`, `Ready Item Details`, `Pick Locations`, `Comments`, `Print` (the annotated headers carry a trailing dot number). There are exactly 5 order rows and 5 `.printbtn` buttons `[L-F7]`.

**QA-F-06 `[WF]` · negative — The removed `View Order` button is absent**
- **Then** `[...document.querySelectorAll('*')].filter(e => e.textContent === 'View Order').length === 0` — **strict equality**, per §8.0's equality-vs-containment rule — and every element inside each row's Print cell carries class `printbtn` [BR-12] §4.2.
- **Not in scope:** the legend footer's prose `… View Order button removed …`. It is annotation chrome and a substring scan of `document.body` would flip this scenario's verdict; the claim here is that no **control** named `View Order` exists.

**QA-F-07 `[WF]` — Order Date format**
- **Then** every order row's third cell textContent equals `2026. 7. 21.` — the live admin's own date form, preserved verbatim [E-72] `[L-F7]`.

**QA-F-08 `[WF]` — Legend unit count is exactly 15**
- **Then** `.legend ol > li` has **14** elements whose `.n` textContents are, in document order, `1 2 3 4 5 6 7 8 14 13 12 9 10 11`; and `document.querySelectorAll('.dot')` has **15** elements — 14 inside `.mock` plus the `M1` dot inside `#m-pick`. This is the machine-checkable form of the §2.1 declaration.

**QA-F-09 `[WF]` · negative — Annotation toggle hides every dot and the legend**
- **When** `#annoToggle` (`Hide annotations`) is clicked.
- **Then** `document.body` gains class `no-anno`, every `.dot` and the `.legend` compute to `display:none`, and the button textContent becomes `Show annotations`; clicking again restores all of it. Annotations are wireframe chrome and ship in no admin build.

**QA-F-10 `[ADMIN]` · negative — Order ID must be a real link**
- **Then** each Order ID is an `<a>` with an `href` deep-linking to that order on Order Detail [G-12]. *(The wireframe ships a `<span class="oid">` with no href — defect `[RTO-WFX-3]`; asserting the span today is the `[WF]` counterpart in QA-F-11.)*

**QA-F-11 `[WF]` · negative — Today the Order ID is not a link**
- **Then** `.oid` elements are `SPAN` nodes with no `href` attribute and no ancestor `<a>`; there are exactly 5 of them, reading `422221`, `422176`, `422165`, `MKT-40233`, `422164`. Documents `[RTO-WFX-3]`.

**QA-F-12 `[ADMIN]` — Row print is an instant single-order reprint that toasts**
- **When** a row `🖨` is clicked in the real admin.
- **Then** that order's carrier label prints immediately with no dialog [G-4]; a green toast `✓ Label printed — order {orderId}` appears [BR-34] `[RTO-WFX-6]`; `label.printed` [DC-7] persists with `source = row_button` and `reprint_seq` incremented. **· negative:** no status change, no stock movement, no auto-comment [BR-31] [BR-33] [E-29].

**QA-F-13 `[ADMIN]` — The signed-in user is the actor on every event**
- **Given** the session belongs to a known admin user.
- **When** any mutating action on this page runs.
- **Then** every resulting event in §5.1 carries that user as `actor` with `actor_source = ui.ready_to_outbound`; **· negative:** no operator-initiated event is written with a null or system actor `[L-F8]` [G-8].

---

### 8.17 QA-E — Edge-case scenarios

| ID | Edge case | Tier | Given / When / Then |
|---|---|---|---|
| **QA-E-01** | `[E-5]` | `[WF]` · negative | **Given** the `Marketing` tab and its single order row removed from the DOM (`document.querySelector('tr[data-view="mkt"]:not(.crow)').remove()`), simulating an empty pool. **When** `Marketing` is clicked. **Then** no exception is thrown, the tbody shows no order row, and `#foundTxt` equals `Found 0 order(s) with items ready for outbound`. |
| **QA-E-02** | `[E-24]` | `[WF]` · negative | **Given** `window.AudioContext` and `window.webkitAudioContext` are stubbed to throw. **When** `📦 Bulk Outbound (3 orders)` is clicked. **Then** no uncaught exception reaches the console, `#pfill.style.width` still reaches `100%`, and `#toast b` still reads `✓ Bulk Outbound complete — 3 orders`. Audio never gates the action. |
| **QA-E-03** | `[E-47]` | `[WF]` · negative | **Then** `getComputedStyle(document.querySelector('.item-line')).whiteSpace` equals `nowrap`, so a long Korean name extends the cell instead of wrapping mid-name; the row's `×qty` pill remains the last element of its line. |
| **QA-E-04** | `[E-73]` | `[WF]` | **Then** `.mockwrap` computes `overflow-x: auto` and `.mock` computes `min-width: 1240px`; narrowing the window produces horizontal scrolling and `document.querySelectorAll('.tbl thead th').length` remains **9**. (Use the qualified selector: a bare `th` count returns **14**, because `#m-pick .picktbl` contributes 5 more.) |
| **QA-E-05** | `[E-62]` | `[WF]` | **Given** a fresh load. **When** `📦 Bulk Outbound (3 orders)` is focused and activated with the keyboard (Enter). **Then** exactly one progress run occurs and exactly one toast appears — identical to a mouse click. **· negative:** holding Enter to auto-repeat must not produce a second overlapping run in the admin [BR-18]. |
| **QA-E-06** | `[E-35]` | `[WF]` · negative | **Then** row `422165`'s two item lines (`100039420` and `100013286`) render as two separate `.item-line` elements with two separate `.locline` locators, and M1 renders them as two separate rows — the page never merges lines it did not create. |
| **QA-E-07** | `[E-6]` | `[ADMIN]` | **Given** an active selection and an open comment panel. **When** `Refresh` is clicked. **Then** the documented behavior occurs — selection preserved for orders still present, dropped for orders that left the pool, panels collapsed — and `rto.list_loaded` [DC-25] persists with `trigger = refresh` [D-7]. |
| **QA-E-08** | `[E-7]` | `[ADMIN]` · negative | **Given** an order outbounded on Order Detail after this list loaded. **When** Bulk Outbound runs including it. **Then** it is rejected at revalidation, no partial write occurs, a red toast names the count, `outbound.rejected_stale` [DC-22] persists, and the remaining orders still ship. |
| **QA-E-09** | `[E-8]` | `[ADMIN]` · negative | **Given** two operators submit overlapping selections within the same second. **Then** every overlapping order is outbounded exactly once; the loser receives `conflict` results [DC-16] [DC-23] and a non-green toast; stock is decremented once. |
| **QA-E-10** | `[E-10]` | `[ADMIN]` · negative | **Given** the response to a Bulk Outbound is lost. **When** the client retries with the same idempotency key. **Then** nothing is outbounded twice, no stock is double-decremented, the UI shows an unresolved state rather than a success toast, and `outbound.batch_aborted` [DC-27] records the last completed sequence if the batch was genuinely incomplete. |
| **QA-E-11** | `[E-11]` | `[ADMIN]` · negative | **Given** the print agent is unreachable. **When** M1 `🖨 Print` runs. **Then** a red toast names the agent/printer, `print.job_result` = `failed` [DC-12] and `print.batch_infrastructure_failure` [DC-24] persist, the orders stay in the list, and **no** browser print dialog appears as a fallback. |
| **QA-E-12** | `[E-12]` | `[ADMIN]` · negative | **Given** the print agent dies after 2 of 3 labels. **Then** the completion toast stays all-success, a separate red toast reports 1 failure, per-order results are persisted [DC-16], and reprinting only the failed order from its row button succeeds. |
| **QA-E-13** | `[E-13]` | `[ADMIN]` | **Given** an order with 2 inbounded and 1 non-inbounded line, selected alongside two fully-inbounded orders. **Then** `Total Items` = 3; the picking list contains 2 rows for it; Bulk Outbound excludes it. All three denominators verified in one run. **And the header figures diverge, correctly:** the `[L-2]` `{items}` count includes all 3 units while the M1 `{units}` total includes only the 2 pickable ones, so `{items} − {units} = 1` for this selection — §3.13 invariant (b), QA-L13-04(b). A run that reports these two as equal has put a non-inbounded unit on the picker's paper and **fails**. |
| **QA-E-14** | `[E-15]` `[E-15b]` | `[ADMIN]` · negative | **Given** a ready SKU whose location was deleted in Inventory, and an order whose item-line and locator-line counts disagree. **Then** the Pick Locations cell shows the unknown marker (never blank), the picking-list row is present with the same marker, and the locator column is padded so the 1:1 pairing holds. |
| **QA-E-15** | `[E-20]` | `[ADMIN]` | **Given** an unposted comment draft in an open inline panel. **When** Bulk Outbound completes and the page refreshes. **Then** the documented behavior occurs (warn on unload, or preserve the draft) — and it is the behavior written in the build docs, not an accident [D-7] `[NE-8]`. |
| **QA-E-16** | `[E-21]` | `[ADMIN]` · negative | **Given** an MKT order with zero inbounded lines in the batch. **Then** it is auto-excluded with `exclusion_reason = lines_not_inbounded` [DC-21], counted in the toast subtext, and the batch is **not** aborted. |
| **QA-E-17** | `[E-22]` | `[ADMIN]` | **Given** 120 orders selected. **When** Bulk Outbound runs. **Then** progress advances monotonically across chunks to 100 %, one batch envelope [DC-8] and 120 per-order results [DC-16] persist, and the toast reports the exact number outbounded. |
| **QA-E-18** | `[E-23]` | `[ADMIN]` · negative | **Given** an order cancelled or deleted after list load. **When** its Order ID link is clicked. **Then** Order Detail renders its own missing/cancelled handling; the link never 500s and this page keeps showing the stale row until the next `Refresh`. |
| **QA-E-19** | `[E-27]` | `[ADMIN]` · negative | **Given** any signed-in admin user. **Then** every control on this page — including Bulk Outbound — is available with no role check, and every mutation records the actor [G-15] `[PD-1 · OWNER-PENDING]`. No per-action gate exists. |
| **QA-E-20** | `[E-28]` | `[ADMIN]` · negative | **Given** an order carrying an assigned sample set. **Then** the picking list contains exactly one `sample set` row for that order — **unblocked 2026-08-03** when `WF-9` was applied and `[PD-51]` answered the content question; the `[WF]` half is now covered by QA-M1-03/04/05/06, and this `[ADMIN]` scenario asserts the production behavior. On unblocking it asserts one row naming the sample set and its quantity [BR-21] [G-13]. |
| **QA-E-21** | `[E-29]` `[E-40]` | `[ADMIN]` | **When** the same order's label is printed three times, and when a picking list is printed and then the selection is changed before Bulk Print Labels. **Then** three `label.printed` events persist with `reprint_seq` 0→1→2→3 and no warning dialog appears; and the labels are produced for the **current** selection, not the printed snapshot. |
| **QA-E-22** | `[E-31]` `[E-67]` | `[ADMIN]` · negative | **Given** a picking list was printed, after which a sample set was assigned and a product was renamed. **Then** the [DC-5] snapshot still reproduces the paper the picker actually carried — no sample row is retro-added and no name is rewritten. Reprinting is the only way to give the picker the new instruction. |
| **QA-E-23** | `[E-32]` `[E-34]` | `[ADMIN]` · negative | **Given** one order whose lines were all cancel-inbounded elsewhere and one already in `prepare-shipment`. **Then** both are excluded with `left_ready_pool` and `already_outbounded` respectively [DC-21], `order.left_ready_pool` [DC-26] records the exit, and neither moves stock. |
| **QA-E-24** | `[E-33]` | `[ADMIN]` · negative | **Given** a Hold order with inbounded lines is listed and selected. **Then** it renders in the list but is excluded from Bulk Outbound with `status_forbids_outbound` [DC-21] `[PD-29 · OWNER-PENDING]`. |
| **QA-E-25** | `[E-36]` | `[ADMIN]` · negative | **Given** a location code changed in Inventory after the list loaded. **When** M1 `🖨 Print` runs. **Then** the modal revalidates and re-renders rather than printing the old code, and the snapshot records the location actually printed. |
| **QA-E-26** | `[E-39]` | `[ADMIN]` · negative | **Given** a comment mentioning a deactivated user. **Then** no Slack message is sent, the comment persists with the literal mention text, and inline feedback names the problem — never a silent success. |
| **QA-E-27** | `[E-41]` `[E-66]` | `[ADMIN]` · negative | **Given** a JIT order staged with no shelf recorded, and a sample SKU with no registered location. **Then** both render the unknown marker and both still appear on the picking list; neither is dropped [BR-23]. |
| **QA-E-28** | `[E-43]` `[E-77]` | `[ADMIN]` | **Given** an order being outbounded, and an order that already left the pool. **When** comments are posted on each. **Then** both persist against their orders, neither is blocked by order state, and the outbound is unaffected [BR-27]. |
| **QA-E-29** | `[E-44]` | `[ADMIN]` · negative | **Given** a day-old open tab. **When** Bulk Outbound runs. **Then** every order fails revalidation, nothing commits, and one red toast reports the count. |
| **QA-E-30** | `[E-45]` | `[ADMIN]` · negative | **Given** an inline panel open for order `422221`. **When** a comment for `422221` is posted from the Comments hub. **Then** both surfaces render the same single comment on their next refresh; **no** duplicate entity is created. |
| **QA-E-31** | `[E-48]` | `[ADMIN]` | **Given** a line was deleted from a selected order after load, so the client's `Total Items` is stale. **Then** the batch executes against the server's current line set, the completion toast reports orders (not units), and the discrepancy is reconstructable from [DC-8] + [DC-16]. |
| **QA-E-32** | `[E-55]` `[E-56]` | `[ADMIN]` · negative | **Given** (a) the session expires mid-batch and (b) the browser is offline at click time. **Then** (a) committed orders stay committed, `outbound.batch_aborted` [DC-27] records `cause = session_expired`, and the operator is sent to re-authenticate; (b) no request leaves, a red toast shows, and **no** progress run and **no** completion toast occur — even though the send sound may already have played. |
| **QA-E-33** | `[E-58]` | `[ADMIN]` · negative | **Given** the page was refreshed by Bulk Outbound. **When** the operator presses Back and the page is restored from bfcache. **Then** the list is re-queried on `pageshow` (or the page is no-store), so already-shipped orders are not presented as selectable and the same wave cannot ship twice. |
| **QA-E-34** | `[E-59]` | `[ADMIN]` · negative | **Given** a selected order was merged into another on Order Management. **Then** it is rejected as stale [DC-22], `order.left_ready_pool` records `reason = merged` [DC-26], and the surviving order is **not** silently substituted into the batch. |
| **QA-E-35** | `[E-60]` `[E-68]` `[E-69]` | `[ADMIN]` · negative | **Given** three upstream data defects — an order with zero lines, the same order id listed twice, and a line whose SKU no longer resolves in the catalogue. **Then** the empty order renders with `Total Items 0` and is excluded with `empty_order` [DC-21]; the duplicate rows both render and are never collapsed, and a batch containing the id twice deduplicates server-side to one result; the dead SKU renders the stored SKU and name from the order line, never blank or `undefined`. Nothing is hidden. |
| **QA-E-36** | `[E-63]` `[E-72]` | `[ADMIN]` · negative | **Given** a client whose clock is 10 minutes fast. **Then** every persisted timestamp uses the server clock, event ordering and `dwell_seconds` are unaffected, and the `Order Date` cell still renders `2026. 7. 21.` from the stored order date rather than from client time. |
| **QA-E-37** | `[E-64]` | `[ADMIN]` | **Given** a selection consisting only of fully-inbounded JIT orders. **Then** the picking list is produced with every row in the `Shelf N` group, sorted numerically by `N` with the [BR-20] tie-break; the note block's fixed example copy is unchanged. |
| **QA-E-38** | `[E-76]` | `[ADMIN]` | **Given** the Comments hub is open. **When** the Bulk Outbound refresh fires. **Then** the hub closes with the reload and no unread or saved state is lost, because both are server-held [DC-3] [DC-4]. |
| **QA-E-39** | `[E-78]` | `[ADMIN]` · negative | **Given** the print agent reports `done` while the printer was out of paper. **Then** `print.job_result` = `done` [DC-12] and the spec claims nothing more; the operator's remedy is the row `🖨` reprint path, which must remain available with no confirmation dialog [BR-32]. |

---

### 8.18 QA-DC — Persistence assertions (one per §5.1 entry)

All `[ADMIN]`. Each scenario's **Then** asserts that the named event exists in the admin data store with the stated fields. This block exists to make the [G-8] requirement mechanically checkable: **every DC id in §5.1 appears exactly once here, DC-1 through DC-28.**

| ID | Event | Given / When / Then |
|---|---|---|
| **QA-DC-01** `[ADMIN]` | `comment.posted` [DC-1] | **When** a comment is posted from the inline panel of order `422221`. **Then** `comment.posted` persists with actor, server timestamp, entity = order `422221`, `text`, `mentions[]`, `source = rto_inline_panel`. |
| **QA-DC-02** `[ADMIN]` | `comment.mention_notified` [DC-2] | **When** that comment contains `@Yongwon`. **Then** one `comment.mention_notified` persists with `channel = #fulfillment-admin-comments`, `mentioned_user` = that user, `delivery_result`, and a `deep_link`. **When** a comment names three different users, **then** three such events persist — one per distinct resolved mention, not one carrying a list [E-75]. |
| **QA-DC-03** `[ADMIN]` | `comment.starred` / `comment.unstarred` [DC-3] | **When** `★` is toggled on and off. **Then** two events persist with `saved` false→true and true→false, both carrying `starred_by`. |
| **QA-DC-04** `[ADMIN]` | `comment.read` / `comment.mark_all_read` [DC-4] | **When** `Mark all read` is clicked with 2 unread. **Then** the event persists with both comment ids and `unread_count` 2→0. |
| **QA-DC-05** `[ADMIN]` | `pickinglist.printed` [DC-5] | **When** M1 `🖨 Print` runs for 3 orders. **Then** the event persists with `order_ids[]`, a 4-line snapshot including `brand_en` and `product_name_kr`, `totals {3,4,8}`, and `sort = location_asc`. |
| **QA-DC-06** `[ADMIN]` | `label.batch_printed` [DC-6] | **When** Bulk Print Labels runs for 3 orders, one of which has no carrier. **Then** the envelope persists with `requested_count = 3`, `dispatched_count = 2`, 2 per-order job refs, and the third in `excluded_order_ids[]` with `no_carrier`. |
| **QA-DC-07** `[ADMIN]` | `label.printed` [DC-7] | **When** a row `🖨` is clicked twice on one order. **Then** two events persist with `source = row_button` and `reprint_seq` 0→1 then 1→2. |
| **QA-DC-08** `[ADMIN]` | `outbound.batch_executed` [DC-8] | **When** Bulk Outbound runs. **Then** the envelope persists with requested / eligible / excluded id lists, `started_at`→`finished_at`, and the idempotency key. |
| **QA-DC-09** `[ADMIN]` | `order.outbounded` [DC-9] | **Then** per order the event records the order `status` old→`prepare-shipment`, the shipped-line detail `{sku, qty, location}` for every line, and `shelf` old→`null`. **· negative:** the payload carries **no** line-status field and no `OUTBOUNDED` value — outbound is order-level [BR-22]. |
| **QA-DC-10** `[ADMIN]` | `inventory.stock_decremented` [DC-10] | **Then** each SKU@location records `on_hand_qty` old→new with a negative delta referencing the outbound event. |
| **QA-DC-11** `[ADMIN]` | `idempotency.duplicate_rejected` [DC-11] | **When** a bulk button is double-clicked. **Then** the rejected attempt persists with the key and the original event id. **· negative:** no second batch event exists. |
| **QA-DC-12** `[ADMIN]` | `print.job_result` [DC-12] | **When** a label prints and, separately, a printer is offline. **Then** the first job records `queued→sent→done` with agent id, printer id, and `artifact_type = shipping_label`; the second records `failed` with a reason. |
| **QA-DC-13** `[ADMIN]` | `order.entered_ready_pool` [DC-13] | **When** an order's first line reaches `INBOUNDED` on View Orders. **Then** `ready_at` persists for that order with `trigger` set. |
| **QA-DC-14** `[ADMIN]` | `order.mkt_surfaced` [DC-14] | **When** an MKT order is imported on Order Management with no stock. **Then** the event persists with the import ref, PIC, `rto_visible_at`, and `inbound_state_at_surface` reflecting "none inbounded". |
| **QA-DC-15** `[ADMIN]` | `order.jit_fully_inbounded` [DC-15] | **When** the last line of a JIT order is inbounded. **Then** `fully_inbounded_at` and `staging_shelf` persist and the badge appears. |
| **QA-DC-16** `[ADMIN]` | `outbound.batch_item_result` [DC-16] | **When** a batch of 5 yields 3 success and 2 excluded. **Then** **5** per-order results persist — one for every requested order, including the ones the all-success UI never mentions. **· negative:** none is omitted. |
| **QA-DC-17** `[ADMIN]` | `ui.telemetry` [DC-17] | **When** telemetry logging is enabled. **Then** tab switches and search queries land in the analytics tier and **not** in the [G-8] audit stream. **· negative:** with logging disabled, no audit-stream row is created and nothing else changes. |
| **QA-DC-18** `[ADMIN]` | selection rule [DC-18] | **When** 3 rows are selected via 7 checkbox clicks and a batch runs. **Then** exactly **one** event carries the resolved 3-order selection and **zero** toggle events exist `[NE-1]`. **· negative.** |
| **QA-DC-19** `[ADMIN]` | `order.status_changed` [DC-19] | **Then** each outbounded order records `processing`→`prepare-shipment` with `reason = bulk_outbound` and the batch id, alongside (not instead of) [DC-9]. |
| **QA-DC-20** `[ADMIN]` | `inventory.reservation_consumed` [DC-20] | **Then** each reservation records `reserved_qty` old→new against the shipment, distinct from the on-hand decrement [DC-10]. |
| **QA-DC-21** `[ADMIN]` | `outbound.order_excluded` [DC-21] | **When** the batch contains an MKT order with a non-inbounded line, a hold order, and an empty order. **Then** three exclusions persist with `lines_not_inbounded`, `status_forbids_outbound`, and `empty_order`, and the toast subtext reproduces them clause-for-clause in enum order — `3 excluded — 1 items not inbounded · 1 status blocks outbound · 1 no line items` — so the persisted reasons and the operator-visible reasons cannot drift apart §3.4 step 6. |
| **QA-DC-22** `[ADMIN]` | `outbound.rejected_stale` [DC-22] | **When** a stale order is submitted. **Then** the rejection persists with `expected_version`→`actual_version` and `changed_fields[]`, and no write occurred for that order. |
| **QA-DC-23** `[ADMIN]` | `outbound.batch_conflict` [DC-23] | **When** two batches overlap. **Then** the conflict persists with both batch ids, the overlapping order ids, and the winner. |
| **QA-DC-24** `[ADMIN]` | `print.batch_infrastructure_failure` [DC-24] | **When** the print agent is offline for a batch. **Then** the batch-level failure persists with `failed_job_count` and drives the separate red toast. |
| **QA-DC-25** `[ADMIN]` | `rto.list_loaded` [DC-25] | **When** `Refresh` is clicked on the `JIT` tab. **Then** the snapshot persists with `trigger = refresh`, `view_tab = jit`, and the served order ids. |
| **QA-DC-26** `[ADMIN]` | `order.left_ready_pool` [DC-26] | **When** an order is outbounded. **Then** `left_at`, `reason = outbounded`, and `dwell_seconds` (against [DC-13]) persist. |
| **QA-DC-27** `[ADMIN]` | `outbound.batch_aborted` [DC-27] | **Given** the session dies mid-batch. **Then** the abort persists with the last completed sequence, `cause`, the committed order ids, and the not-attempted ids. |
| **QA-DC-28** `[ADMIN]` | `label.print_refused` [DC-28] | **When** a row `🖨` is clicked on an order with no carrier. **Then** the refusal persists with `reason = no_carrier` and `source = row_button`, and it is distinguishable from a [DC-12] `failed` job because no job was ever created. **· negative:** no `label.printed` event exists for that order. |

---

### 8.19 Coverage map

| Requirement | Where satisfied |
|---|---|
| Every legend unit `[L-1]`…`[L-14]`, `[L-M1]` has ≥1 scenario | QA-L1…QA-L14, QA-M1 (§8.1–§8.15) |
| Every furniture unit `[L-F1]`…`[L-F8]` has ≥1 scenario | `[L-F1]` QA-F-01 · `[L-F2]` QA-F-02 · `[L-F3]` QA-F-03 · `[L-F4]` QA-F-04 · `[L-F5]` QA-F-10/11 · `[L-F6]` QA-F-12 · `[L-F7]` QA-F-05/07 · `[L-F8]` QA-F-13 |
| The §2.1 legend-unit declaration is machine-checkable | QA-F-08 (14 `li` + 15 `.dot`) |
| Every `[E-n]` edge case is referenced by ≥1 scenario | QA-E block (§8.17) plus inline `[E-n]` citations across QA-L/QA-M/QA-F. All 80 (`E-1`…`E-79` + `E-15b`) are covered; `[E-49]` is carried by QA-L4-01, which asserts the `AudioContext` is constructed inside the click gesture |
| Every `[DC-n]` event has a Then-clause asserting persistence | QA-DC-01…QA-DC-28, 1:1 with §5.1 |
| Every `[NE-n]` non-event is asserted as absent where testable | `[NE-1]` QA-DC-18 · `[NE-2]` QA-L5-02 · `[NE-3]` QA-DC-17 · `[NE-4]` QA-M1-12 · `[NE-9]` QA-E-02 · `[NE-12]` QA-L1-08 |
| Negative tests ≥ 25 % | see the §8.0 count table |
| Both tiers present, with exact selectors and strings for every `[WF]` | §8.0 count table |

---

## 9. Out of Scope & Open Questions

Per `_review.md` §3 convention 8, this section lists **only**: (a) what this screen explicitly does not do, (b) **NO-DEFAULT** owner questions where no behavior was specified, and (c) decisions delegated to development. Owner questions that already carry a provisional default live in `_provisional-decisions.md` and are tagged inline throughout this document — they are **not** re-listed here as open. In particular, the six open questions raised in this page's Lens-B plan (OQ-B1…OQ-B6) were all adjudicated and are **not** open: OQ-B1 → C-9 / `[PD-34]`, OQ-B2 → `[PD-35]`, OQ-B3 → `[PD-37]`, OQ-B4 → `[PD-38]`, OQ-B5 → `[PD-36]`, OQ-B6 → `[PD-1]` / [G-15].

§9.4 (wireframe fixes owed) and §9.5 (open cross-page conflicts) sit alongside those three lists without widening them: §9.4 is a backlog, and §9.5 is a **registry of disagreements with another screen's spec** — not open questions on this page, and not owner questions with provisional defaults. `order-detail.md` keeps the same registry as its §2.7.

### 9.1 Explicitly out of scope

| Topic | Where it belongs |
|---|---|
| **Label and invoice layout content** — what is drawn on a Deleo or YUN label, field placement, barcode position, sample-row rendering on the printed artifact | **Phase 3-1**, a separate owner session after Phase 3. This spec covers *when* a label prints, *which* carrier, *what is captured*, and *what happens on failure* — never the layout [G-4] |
| **Order-level inspection and mutation** — status changes, line edits, cancellations, tracking corrections, holds, clone, reset | `order-detail.md` |
| **Inbound flows** — receiving, scanning, expected-quantity edits, partial inbound, multi-tracking [G-10] | `view-orders.md`, `inbound-request.md` |
| **The closing/scan lifecycle** and the Daily Shipping Status sheet | `closing.md` (`[PD-71 · NO-DEFAULT]` owns the sheet mapping — undecided, and nothing here depends on it) |
| **Sample-set configuration** (ON/OFF, overlapping periods, targets) | `order-management.md` [G-13] |
| **Stock audit, location registration, Reserved views, line-based location filtering, audit-mode-only visibility** | `stock-status.md` [G-14] |
| **JIT residual stock** — stock left over from cancelled or short-shipped JIT orders, and any view of it | `stock-status.md`. This page lists only orders that are **ready to ship**; residual stock is not an order and never surfaces here. Stated explicitly rather than left silent, because the mandatory-item matrix codes this item `n` for this page and `n` means *explicit N/A* |
| **Unrecognized-tracking pool and matching** | `tracking-missing.md` |
| **Sourcing-route badges** [G-5] | `view-orders.md`, `stock-status.md`, `order-detail.md`. This page renders no route label §1.4 |
| **Pagination** | Not present on this page and not planned. Large selections are handled by request chunking, not paging [E-22] |
| **Order search** | Never existed on this page. The four view tabs are the only order-filter surface [L-14]; the hub's search is a comment search [L-10] |
| **A scan surface** | [G-1] is explicitly N/A here [BR-25] |
| **Import template specification** (recipient, contact, address, country, SKU, qty, campaign name) | Produced by the development team; the import itself is an Order Management concern |
| **Procurement Hub** | Excluded from this planning round entirely (2026-08-02 owner decision) |
| **Role/permission matrix** | Post-v1 owner decision. v1 behavior is specified: single admin role [G-15] `[PD-1 · OWNER-PENDING]` |

### 9.2 Open questions — NO-DEFAULT (owner)

Three NO-DEFAULT items are **owned by** this page: OQ-1 and OQ-2 were **owner-decided on 2026-08-03** and are recorded below with their answers; **OQ-3 (added 2026-08-04) is open** and is the order-level half of `stock-status.md`'s `OQ-2`. (A third NO-DEFAULT entry, `[PD-71]` — the Daily Shipping Status sheet mapping — is cited in §6.3 as context but is **owned by `closing.md`**, and no behavior on this page rests on it; PD-71 remains open.)

**OQ-1 — Where is "WHICH sample and HOW MANY" defined, and by whom?** `[PD-51]` — **RESOLVED, OWNER-DECIDED 2026-08-03**
- **The answer.** v1 makes no sample distinction: internal invoice and picking artifacts render **"sample set" only** — no sample type, no per-type quantity. Distinguishing which sample and how many is follow-up work for the moment sample types are introduced. [G-13] was amended accordingly (`_global-rules.md` v1.1).
- **Effect on this page.** The picking list's sample line reads "sample set" [BR-21]; wireframe fix **WF-9** (adding sample rows to M1) is no longer gated on a definition source — only owner approval of `[PD-36]` remains. QA-E-20 unblocks once PD-36 lands. Snapshot and unknown-location behavior [E-66] [E-31] unchanged.
- **Owner:** decided by the product owner 2026-08-03. **Also affects:** `order-management.md`, `order-detail.md`, `shipping-label` (Phase 3-1).

**OQ-3 — How is an *order* classified as JIT when its lines carry different sourcing routes?** — **OPEN (raised 2026-08-04 by the final readiness audit)**
- **The question.** §3.7 `[L-7]` conditions the JIT badge and tint on "**the order's** sourcing route is JIT", and the JIT view tab filters on the same predicate. But a sourcing route is a **line-level** fact (`[G-5]`; `inbound-request.md`: "Route is request-level, not row-level"), so an order whose lines mix JIT and non-JIT rows has no defined classification. Candidates: any-line-is-JIT / all-lines-are-JIT / a stored order-level attribute set at import.
- **Why it is not decided here.** This is the **order-level half of the same unresolved axis** as `stock-status.md` `OQ-2` (which single route a multi-route SKU row resolves to). Both are schema decisions about where the route lives and how many-to-one collapses; answering one without the other would fork the model. Nothing in this spec set fixes either, so no behavior is invented here.
- **Blocking.** `[L-7]` badge/tint, the JIT view tab's result set, and the sort order that places JIT-complete rows last.
- **Owner:** owner + development, together with `stock-status.md` `OQ-2` — **needed before the data model is fixed**, because a later change forces a re-model rather than a re-render.

**OQ-2 — "Not connected — contact the Fulfillment Center" orders: what unblocks them, and who owns it?** `[PD-55]` — **RESOLVED, OWNER-DECIDED 2026-08-03**
- **The answer.** Unblocking is **manual coordination — contact the fulfillment person in charge via Slack**. v1 ships no in-admin release/carrier-assignment UI and no automated Slack route.
- **What this spec does (unchanged mechanics).** The flagged state is rendered and persisted; the order behaves like any other row for selection, picking, and Bulk Outbound; **label printing alone** is refused and audited [E-61] [DC-28]. No unblocking action exists on this page — by decision, not by gap.
- **Owner:** decided by the product owner 2026-08-03. **Also affects:** `order-management.md`.

### 9.3 Decisions delegated to development

These are **not** owner questions and are not tracked as provisional decisions. Each must be chosen and written into the build documentation; leaving one implicit is a defect.

| ID | Decision | Constraint the choice must satisfy |
|---|---|---|
| **D-1** | Whether read-only telemetry is logged (view-tab switch, comment search, `Refresh`, M1 `Cancel`) [DC-17], and its retention horizon | Must not enter the [G-8] audit stream; `[NE-3]`, `[NE-4]`, `[NE-6]` remain non-events regardless |
| **D-2** | Batch chunk size and progress granularity (per-order increments vs smoothed percentage) [E-22] | Progress must stay monotonic 0→100 across chunks |
| **D-3** | Idempotency key format, TTL, client debounce interval, and how a rejected duplicate surfaces [G-9] | Double-click and keyboard auto-repeat must produce exactly one batch [E-9] [E-62]; rejections persist [DC-11] |
| **D-4** | Print-agent product, job polling, timeout, retry policy, queue naming, and the red-toast failure copy [G-4] | Failures surface as a red toast and persist [DC-12] [DC-24] [DC-28]; never a browser-dialog fallback |
| **D-5** | Default checkbox state on page load | The wireframe's 3 pre-checked Inventory rows are **illustrative**, not normative. Recommended default: none selected, which makes [E-1] the load state |
| **D-6** | `readyToBeOutbonded` refresh cadence — manual `Refresh` only vs background poll; and the stable within-group sort key | A background poll must not reorder or deselect rows mid-wave; within-group order must be stable across refreshes [L-F7] |
| **D-7** | `Refresh` semantics for selection and open comment panels [E-6]; unposted-draft handling across the Bulk Outbound refresh [E-20] | Whatever is chosen must be documented and consistent; silent data loss is not acceptable |
| **D-8** | Toast auto-dismiss duration and stacking vs single-slot replacement [E-18] | Consistent across all three actions; the Bulk Outbound toast must survive its own refresh [E-37]; a red toast must be able to supersede a green one [E-79] |
| **D-9** | Send-sound synth parameters and `AudioContext` resume handling [G-3] | Audio failure must never block or delay the outbound [E-24] [E-49] |
| **D-10** | Mixed-location sort comparator detail (lexicographic rule for rack codes, numeric parse for `Shelf N`) | The two-group ordering **and** the order-id/SKU tie-break in [BR-20] are fixed; only the comparator internals are open [E-65] |
| **D-11** | Fallback glyph/text for a missing location [E-15], a shelf-less JIT order [E-41], and a missing PIC [E-42] | Never blank [BR-23] |
| **D-12** | Slack retry policy on delivery failure [DC-2] | Never blocks or rolls back [BR-30]; multiple mentions stay one message [E-75] |
| **D-13** | Comment-search debounce, index scope, and result cap [L-10] | Scope is all comments, newest first, with highlight inserted **after** escaping — those are fixed [BR-37] [E-74] |
| **D-14** | Stale-snapshot revalidation trigger for M1 `Print` [E-30] and for batch execute [E-7] | Revalidation must exist; its trigger point is open |
| **D-15** | Sticky columns / horizontal-scroll behavior at the 1240 px minimum width [E-47] [E-73] | The brand prefix and the `×qty` pill must remain reachable; columns are never dropped |
| **D-16** | bfcache / `pageshow` handling after the Bulk Outbound refresh [E-58] | A restored page must not present already-shipped orders as selectable |
| **D-17** | Whether a reprint auto-posts a comment | **Already decided against** [BR-33]; recorded here only so it is not re-opened. Event-only. |
| **D-18** | Whether an operator @mentioning **themselves** suppresses the Slack notification §6.1 | No register entry decides it — `[PD-16]` covers only the *system* match-confirm auto-comment on View Orders / Tracking Missing / Order Detail, and that citation was withdrawn on 2026-08-03. Whichever way it goes, the comment persists and delivery never blocks or rolls back the post [BR-30]; and the choice must not change the per-distinct-mention fan-out [E-75] |

### 9.4 Wireframe fixes owed on this page

Tracked in `_wireframe-fixes.md` (register) and §2.4 (page-local candidates). Not open questions — backlog items for the post-spec wireframe-edit pass, deployed through `/wf-deploy ready-to-outbound`.

| Item | Status |
|---|---|
| **WF-9** — add sample rows to the M1 picking table | **Conditional** — blocked on `[PD-36]` approval **and** OQ-1 (`[PD-51]`) |
| `[RTO-WFX-9]` — write `#pbarLabel` once **before** `setInterval` starts, mirroring the existing synchronous `fill.style.width='0%'` line, so a run never displays the previous action's mode string for its first 250 ms | **Registered** 2026-08-03 in `_wireframe-fixes.md` §B (page-scoped ID — see §2.4). Until it lands, §8.0's running-label reading rule bounds every "during the run" assertion |
| `[RTO-WFX-1]` — wire the selection model, or annotate the static counts as demo-only; define the two select-all controls as one state | New candidate |
| `[RTO-WFX-2]` — remove the duplicate `wf-bar` modal button (and the unstyled `.wf-tab` class) | New candidate |
| `[RTO-WFX-3]` — make the Order ID a real anchor | New candidate |
| `[RTO-WFX-4]` — delete the dead `.cb-ready` class and the unused `.picktbl td.num` rule | New candidate |
| `[RTO-WFX-5]` — render the bold EN brand prefix on M1 product names; replace the elided English name on order `422221` in both *Ready Item Details* and M1 with the Korean name | New candidate |
| `[RTO-WFX-6]` — add the row-print success/failure toast | New candidate ([G-2] gap) |
| `[RTO-WFX-7]` — add the comment-post toast and in-place append | New candidate ([G-2] gap) |
| `[RTO-WFX-8]` — normalise demo data: `#crow4`/`#crow5` id order, and the trailing period on the seeded `×5 quantity` comment | New candidate (cosmetic; QA is written to tolerate both) |

### 9.5 Open cross-page conflicts that touch this page `[RTO-X-n]` (2026-08-03)

Disagreements between this spec and another screen's spec, found by the 2026-08-03 pre-handoff cross-page pass. They are recorded — not silently harmonised — so that a reader who meets the other spec's sentence does not "fix" this page by hand, and so the owner has one place to adjudicate. **IDs are page-scoped** and prefixed `RTO-` for the same reason `[RTO-WFX-n]` is (§2.4): `order-detail.md` runs its own `[X-1]`…`[X-9]` series in its §2.7, and the two series are unrelated. Each row states where this page holds its position and what would have to move if the owner rules the other way. **Nothing here is decided by this spec.**

| ID | Conflict | This page's position (and where) | Resolution owner / what changes if reversed |
|---|---|---|---|
| **`[RTO-X-1]`** | **Outbound gate on a carrier-less order.** On an order flagged "Not connected — contact the Fulfillment Center", `order-detail.md` `[E-86]` disables **both** 📦 Outbound and 🖨 Print and persists a `reason_code = no_carrier` attempt, asserted by its `QA-OUT-11`. This page ships the order and refuses only the label. One implementation cannot satisfy both: the same order is outboundable here and not outboundable there. | §3.4 step 4 (carrier-less orders are **eligible**) + [E-61] + §3.3 Validation + [DC-21] `exclusion_reason` (no `no_carrier` value) + [DC-28] + QA-L3-07. The pre-handoff pass reads **this page** as the operationally-grounded side — the goods are packed and leaving, and the carrier record is a downstream data gap — but that is a recommendation, not an owner ruling. | Cross-page. Both pages cite the same `[PD-55]` decision, which answered **who unblocks** such an order (manual Slack coordination with the fulfillment person in charge) and **not** whether outbound is blocked — so neither page is contradicting a ruling, and the ruling owed is a new one. **If a missing carrier blocks outbound everywhere:** the §3.4 step-4 bullet flips from eligible to auto-excluded, `no_carrier` joins the [DC-21] enum with its own subtext phrase in §3.4 step 6 and §3.3's phrase order, [E-61]'s Bulk Outbound sentence is rewritten, and a QA-L4 scenario is owed. **If this page's reading stands:** `order-detail.md` `[E-86]` / `QA-OUT-11` drop the outbound half of the block and keep the print half. |

---

## 10. Decision Log

Every dated decision that shaped this screen, 2026-07-09 → 2026-08-03, including reversals and removals. Nothing here was silently dropped.

| Date | Decision | Rationale / source | Effect on this spec |
|---|---|---|---|
| 2026-07-09 | WMS 2.0 wireframe programme opens; **Ready to be Outbounded** is screen 3 of the set. Design decisions established on View Orders are declared to apply across screens: bulk-action bar pinned at the top of the table and always visible (disabled when not actionable); brand name always shown; column sets kept identical across states. | Planning ledger `2026-07-09-wms2-wireframes.md` | `[L-1]`, `[L-F7]`, [BR-14] |
| 2026-07-09 | **Bulk Outbound refreshes after completion** is accepted as the sole designed exception to the no-refresh rule. | Same ledger; carried verbatim into [G-2] | [BR-8], `[L-4]`, `[L-5]` |
| 2026-07-09 | Deleo Tracking No. is **removed from View Orders** but retained on Order Detail. | Deliberate asymmetry, reconfirmed 2026-07-21/22 | Context only — this page never had a tracking column |
| 2026-07-13 | Batch generation of 9 draft screens from planning text alone; RTO draft produced without a capture of the live admin. | Ledger | Superseded on 2026-07-21 |
| 2026-07-14 | **Real-capture pivot.** Nine screens are found to diverge from the live admin and are queued for redrawing from captures. | Ledger | Superseded the 2026-07-13 RTO draft entirely |
| 2026-07-21 | **Live admin captured.** Base structure, the column set, the page-title spelling `Ready to be Outbonded`, `Refresh`, `Found N order(s) with items ready for outbound`, the `Order Date` form `2026. 7. 21.`, and the `How to use` block are adopted **verbatim**. | Capture | [BR-14], `[L-F1]`…`[L-F4]`, `[L-F7]` |
| 2026-07-21 | **Double-click double-processing bug** on inbound/outbound buttons is logged to the developer handoff note rather than drawn in the wireframe. | Owner instruction; handoff note A | [BR-13], [G-9], [E-9], QA-L4-07 |
| 2026-07-21 | **Instant print requires a local print agent** (PrintNode-class) — a browser alone cannot push to a printer queue. | Handoff note B | [BR-10], §6.4 |
| 2026-07-21 | Unrecognized-barcode **photo upload put on hold** and removed from the View Orders modal. | Owner decision | Context; this page never had photo capture. See the 2026-08-03 permanent-removal row |
| 2026-07-22 | **Full rework of this page from the capture.** Order-level rows (5 samples); global sort regular → MKT → JIT; picking-list modal with location-ascending sort; shared progress bar; completion toast; inline per-row comment panels. | Ledger | `[L-1]`…`[L-6]`, `[L-M1]`, [BR-2], [BR-7] |
| 2026-07-22 | **`Total Items` changed from SKU count to unit sum.** The live admin displayed `1` for a ×5 order and pickers under-picked. | Ledger (D picking) | [BR-5], `[L-13]`, QA-L13-01 |
| 2026-07-22 | **`Pick Locations` column added.** | Ledger (D picking) | `[L-12]`, [BR-23] |
| 2026-07-22 | **REMOVED: `Ready Items` column** — a duplicate of `Total Items`. | Ledger | §4.2; must NOT exist; dead class `.cb-ready` still ships `[RTO-WFX-4]`, asserted absent by QA-L13-03 |
| 2026-07-22 | **REMOVED: `View Order` button from the Actions column.** Actions reduced to Print; details open through the Order ID link. | Ledger | [BR-12], §4.2, `[L-F5]`, QA-F-06 |
| 2026-07-22 | **REMOVED: failure-state UI from the bulk completion notice.** All-success is the normal path. | Ledger | [BR-9], `[L-6]`, §4.2, QA-L6-04 |
| 2026-07-22 | Print actions keep the selection and never refresh; only Bulk Outbound refreshes. | Ledger | [BR-8], QA-M1-11, QA-L3-03 |
| 2026-07-22 | ~~Audit loss valuation set to `Diff × cost`, with the cost source deferred to development (FIFO lot cost recommended).~~ **REVERSED 2026-08-04 — the owner removed loss-amount from the stock audit outright. The audit reports count differences only (`−1` / `+1`) and carries no monetary figure, so there is no valuation rule and no cost source to defer.** | Handoff note E; owner decision 2026-08-04 | Not this page. Kept struck-through rather than deleted so the reversal is visible and the rule does not silently reappear from a stale copy of this log |
| 2026-07-23 | **REVERSAL — MKT import stock validation dropped.** Import first, inbound later is allowed; MKT orders appear in this list immediately regardless of stock or inbound status. This reverses the original planning text ("error if the product is not in the warehouse"), now struck through. | Owner decision; ledger + handoff note G | [BR-3], `[L-8]`, QA-L8-05 |
| 2026-07-23 | **REVERSAL — sample assignment reinstated as simple ON/OFF** with multiple, possibly overlapping periods and no sample-type selection. The 2026-07-22 "removed" note was stale within a day and is superseded. | Owner decision; handoff note G corrected 2026-08-03 | Reaches this page through [G-13] → [BR-21] → M1 sample rows `[PD-36 · OWNER-PENDING]` |
| 2026-07-23 | Closing reworked: the **single normal status is `prepare-shipment`**; everything else raises a warning. | Ledger | [BR-22] — fixes the target status of Bulk Outbound |
| 2026-07-23 | **REMOVED on neighbouring screens: per-PIC row grouping, the bulk bar, the Slack column, the resolved log (tracking-missing) and Bulk Hold Shipment (order-management).** | Ledger; `_wireframe-fixes.md` WF-10 | Recorded here because the deliberate absence of all five on this page is a decision, not an oversight §4.2 |
| 2026-07-27 | Internal inbound scanning folded into View Orders States 6/6b; the standalone `inbound-receiving` page is retired. | Owner instruction | Context: JIT rows reach this page from View Orders State 6 |
| 2026-07-29 | **Comments hub full-text search** added across all comments (newest first, purple highlight, click opens the order), on every screen carrying the hub. | Ledger | `[L-10]`, QA-L10-05…10 |
| 2026-08-02 | Developer handoff note published in Notion with 6 implementation notes; the two conflicting planning-doc items are struck through at source. | Ledger | [BR-10], [BR-13], [BR-3] |
| 2026-08-02 | **Procurement Hub excluded** from this planning round entirely. | Owner decision | §9.1 |
| 2026-08-02 | Phase 2 (English conversion) opens; specs will be English, one document per screen, with QA criteria an AI can execute. | Ledger | This document's form |
| 2026-08-03 | **RTO English conversion** (81 replacements). Korean survives only as data: product names, carrier names, company names [G-6]. | Ledger | §3, QA-M1-05 |
| 2026-08-03 | **`Ready Item Details` and the M1 picking list switch to Korean product names**, with a legend footnote; the EN name with bold brand remains on order-facing pages. Pickers locate items faster by the Korean name. | Owner decision | [BR-6], [G-6], `[L-M1]`, `[L-F7]`, `[RTO-WFX-5]` |
| 2026-08-03 | **REVERSAL of badge wording — `JIT (channel) completed` → `Fully Inbounded`.** This was item #11 of the 17-item judgment list, the last one to be answered. The old wording read as a sourcing route and collided with the colorless black-bold route labels [G-5]. | Owner decision | [BR-4], `[L-7]`, §4.2, QA-L7-02 |
| 2026-08-03 | **Outbound send sound added** (Web Audio synthesis, no external files) and bound to outbound-class buttons across View Orders (11 buttons) and this page's Bulk Outbound. | Owner request | [BR-11], [G-3a], `[PD-2 · OWNER-PENDING]`, QA-L4-01/04 |
| 2026-08-03 | **Global confirmation-toast doctrine emphasised** — every confirming action toasts, top-right, green for success and red for failure, across all eight screens. | Owner emphasis | [G-2], `[L-6]`, and the page's enumerated confirmation surfaces [BR-34] §4.1 |
| 2026-08-03 | **Instant carrier-agnostic printing reconfirmed** — the Print button alone must produce the label, for any carrier. | Owner emphasis | [BR-10], [G-4], §6.4 |
| 2026-08-03 | **Comment @mention channel confirmed: `#fulfillment-admin-comments` (`C0BMGEWM5QA`).** Supersedes the "pending owner decision" wording in the draft global rules and in `decision-sources.md` item 12. | Owner; `_slack-routing.md`; adjudication C-2 | §6.1, [G-7] |
| 2026-08-03 | **Scanner protocol declared N/A on this page** — no scan surface exists, stated explicitly to preempt QA confusion. | Ledger | [BR-25], [G-1] |
| 2026-08-03 | **Automatic carrier recording is NOT supported** anywhere in WMS 2.0; only Received Date is auto-recorded at scan time. | Adjudication C-1; `[PD-9 · OWNER-PENDING]` | §4.2 — this page has no Carrier field or column |
| 2026-08-03 | **REMOVED permanently — photo capture.** The 2026-07-21 hold is resolved by deletion, not deferral, so nobody re-implements it. | `[PD-63 · OWNER-PENDING]` | §4.2 |
| 2026-08-03 | Adjudication **C-5**: the send sound is scoped by **button class, not by page** — every outbound-class button on every page plays it. | `_review.md` §1; `[PD-2 · OWNER-PENDING]` | [BR-11] |
| 2026-08-03 | Adjudication **C-7**: auto-outbound on full inbound is a **View Orders** scan/bulk behavior only; Order Detail is always manual. | `_review.md` §1; `[PD-21 · OWNER-PENDING]` | §6.2 — explains why some ready orders never appear here |
| 2026-08-03 | Adjudication **C-8**: [G-13] doctrine wins — internal picking artifacts list which sample and how many, so the picking list gets sample lines. | `_review.md` §1; `[PD-36 · OWNER-PENDING]` | [BR-21], **WF-9** (conditional), QA-E-20 (blocked) |
| 2026-08-03 | Adjudication **C-9**: the 2026-07-22 "no failure case" decision is **kept**, bounded by a new rule — infrastructure failures raise a *separate* red toast, affected orders stay in the list, and per-order results always persist. | `_review.md` §1; `[PD-34 · OWNER-PENDING]` | [BR-9], [BR-9b], [DC-16], [DC-24] |
| 2026-08-03 | Adjudication **C-6** applied to this page: [G-2] beats wireframe omissions, so the missing row-print and comment-post confirmations are **gaps**, and every confirming action on the page is enumerated with its confirmation surface. | `_review.md` §1 | [BR-34], §4.1, `[RTO-WFX-6]`, `[RTO-WFX-7]` |
| 2026-08-03 | **Bulk Outbound eligibility fixed**: orders with any non-inbounded line are auto-excluded and reported in the toast subtext; fully-inbounded JIT rows are eligible. | `[PD-35 · OWNER-PENDING]` | [BR-15], QA-L4-08/09 |
| 2026-08-03 | **Count semantics fixed**: `Total Items` and the bulk-button item count include **all** units of the order, not only ready units. Precedent: `MKT-40233` = 3 with one line not inbounded. | `[PD-37 · OWNER-PENDING]` | [BR-16], QA-L13-02 |
| 2026-08-03 | **Select-all scope fixed**: visible (filtered) rows only; per-order selection persists across tab switches. | `[PD-38 · OWNER-PENDING]` | [BR-17], QA-L1-05/06/07 |
| 2026-08-03 | **No sequence gate between the three bulk actions**; only one may run at a time (a lockout, not a sequence), extended in this spec to `Refresh` and the view tabs. | `[PD-39 · OWNER-PENDING]` | [BR-18], QA-L5-06/07 |
| 2026-08-03 | Cross-cutting provisional decisions adopted and tagged inline: single admin role [PD-1]; send-sound scope [PD-2]; append-only comments [PD-3]; notification failure never blocks [PD-4]; destructive actions confirm + toast [PD-5]; stale-entity revalidation [PD-6]; optimistic concurrency [PD-7]. | `_provisional-decisions.md` §A | [BR-26]…[BR-30]. [PD-5] has no destructive action to govern on this page — the page has no delete affordance at all |
| 2026-08-03 | Adjacent provisional decisions consumed by this page: shelf auto-clear on outbound [PD-18]; manual-only outbound on Order Detail [PD-21]; Cancel Outbound parity [PD-26]; sample display on internal views [PD-27]; outbound status gate [PD-29]; PIC as a system-user picker [PD-33]; location 1:1 exclusivity [PD-46]; MKT/sales-order merge block [PD-59]; photo removal [PD-63]; Daily Shipping Status mapping [PD-71 — **NO-DEFAULT**, cited as context only, owned by `closing.md`]; no Slack route for batch completion [PD-72]; OTHER-route rendering [PD-80]. | `_provisional-decisions.md` | §3, §4, §6 |
| 2026-08-03 | **Spec v1.0 written**, then **v1.1 audited and finalised**: §7 expanded from 50 to 80 edge cases; §8 rewritten to 201 machine-runnable scenarios (93 `[WF]` / 108 `[ADMIN]`; the negative share stated here was recomputed in v1.2 — see the §8.0 table) with wireframe-accurate selectors (inline `style.width`, `childNodes[0]`, header-first-text-node); [G-2] confirmation surfaces enumerated as [BR-34] with two newly found gaps; toast pluralisation, classification precedence, and comment escaping pinned as [BR-35]…[BR-37]; `label.print_refused` added as [DC-28]. Nine page-local wireframe defect candidates registered (`[RTO-WFX-1]`…`[RTO-WFX-8]` plus the conditional WF-9). | This document | — |
| 2026-08-03 | **Spec v1.2 — remediation of three independent verification passes** (coverage audit, adversarial QA execution, cross-page consistency). Behavior corrections: Bulk Outbound is **order-level** and writes no `OUTBOUNDED` line status [BR-22]; @mention Slack fan-out is **one message per distinct resolved mention** [E-75]; the exclusion subtext is **reason-aware** for all five [DC-21] reasons and gains a Bulk Print Labels counterpart §3.3. Contract clarifications: the §3.13 reconciliation invariant split into an unconditional (a) and a conditional (b); M1's `{skus}` defined as distinct SKUs; [BR-4]'s "anywhere" scoped to the shipping surface so the legend's dated changelog is exempt; §4.2's carrier-removal row scoped to the *inbound* carrier. QA runnability: §8.0 gains a running-label reading rule (`[RTO-WFX-9]`), an equality-vs-containment rule, and a negative-counting rule; QA-L5-04, QA-L6-04, QA-F-06, QA-E-04, QA-L13-03/04/05, QA-L7-02 rewritten to be executable with zero interpretation. Hygiene: `[PD-71]` retagged NO-DEFAULT; the `[PD-16]` self-mention citation withdrawn and re-homed as dev decision **D-18**; `[E-49]` given QA coverage; `[NE-2]` given a real assertion; three shorthand dates expanded; three restated global-rule bodies trimmed to deltas; a JIT-residual-stock out-of-scope row added so no mandatory-item N/A cell is silent. | `_verify/m1-ready-to-outbound.md` · `_verify/m2-ready-to-outbound.md` · `_verify/m3a-cross-page.md` · `_verify/m3b-review-audit.md` | §3, §4, §5, §6, §7, §8, §9, §10.1 |
| 2026-08-03 | **Carrier-less orders stated positively in the eligibility filter, and the disagreement with Order Detail registered.** No behavior changed: a missing carrier already refused the label only ([E-61], [DC-28]) and was already absent from the [DC-21] exclusion enum, but the rule lived in an edge-case row while §3.4 step 4 was silent — so a developer reading the filter alone could not tell whether the omission was deliberate. Step 4 now names carrier-less orders as **eligible** and states where the missing carrier surfaces (label beat only). `order-detail.md` `[E-86]`, which disables its own 📦 Outbound on the same state, is recorded as `[RTO-X-1]` in the new §9.5 registry rather than reconciled by hand — the `[PD-55]` decision covered who unblocks the order, not whether outbound is blocked. | Pre-handoff cross-page pass (`_plans/_prehandoff/ledger.md`) | §3.4, §7.2 [E-61], §9 preamble, §9.5 |

### 10.1 Reversal chains recorded verbatim

Kept as chains, not as end-states, so nobody re-derives a superseded step from a stale document.

1. **Sample assignment** — designed → noted as *removed* on 2026-07-22 → **reinstated as simple ON/OFF on 2026-07-23** (the removal note was stale within one day) → **reconfirmed on 2026-08-03**, with the source documents (Notion section G and the developer handoff note) corrected on 2026-08-03. Reaches this page as [BR-21] / WF-9 / QA-E-20.
2. **MKT import stock validation** — originally specified as an import-time error when the product is not in the warehouse → **dropped 2026-07-23**; import first, inbound later; MKT orders always visible here. Original text struck through at source.
3. **JIT badge wording** — `JIT (channel) completed` → **`Fully Inbounded` (2026-08-03)**. The old string must not appear anywhere [QA-L7-02].
4. **Bulk failure UI** — failure states existed in the pre-07-22 design → **removed 2026-07-22** → **bounded, not restored, on 2026-08-03**: the completion notice stays all-success while infrastructure failures surface separately and every per-order result persists.
5. **RTO item names** — English with bold brand → **Korean with bold EN brand in `Ready Item Details` and M1 (2026-08-03)**, while order-facing pages keep the English name. The wireframe still carries one English remnant (`AtoBarrier365 Body …`) — `[RTO-WFX-5]`.
6. **This page's own draft** — 2026-07-13 wireframe drawn from planning text alone → **discarded and redrawn from the live admin capture on 2026-07-21 / 2026-07-22**. No behavior from the 2026-07-13 draft survives.
7. **Bulk Outbound's line-level write** — specified as `INBOUNDED → OUTBOUNDED` per line (v1.0/v1.1) → **corrected on 2026-08-03 to an order-level transition that writes no line status**, because `view-orders.md` `[L-S1b-21]` and `order-detail.md` `[L-10]` define the line vocabulary exhaustively as `INBOUNDED` / `PENDING`. The shipped-line detail moved into [DC-9]'s payload; [BR-22], §3.4 step 5, QA-L4-06, QA-DC-09.
8. **Comment @mention Slack fan-out** — specified as one message naming every mentioned user (v1.0/v1.1) → **corrected on 2026-08-03 to one message per distinct resolved mention**, the [G-7] contract already implemented by `view-orders.md` `DC-20` and `order-detail.md` §6.1; duplicates of the same user in one body still collapse to one. [E-75], [DC-2], §3.9, §6.1, QA-L9-11, QA-DC-02.
