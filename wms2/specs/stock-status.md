# Inventory (`stock-status`) — Screen Specification

Version 1.1 · 2026-08-03 · Page slug `stock-status` · Screen name **Inventory** (renamed from "Stock Status" 2026-07-22).
Wireframe SST: `wms2/stock-status/index.html` · live https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/stock-status/
Global rules: `_global-rules.md` — cited as `[G-n]`, never restated. Provisional decisions: `_provisional-decisions.md` — cited inline as `[PD-n · OWNER-PENDING]`. Known wireframe defects: `_wireframe-fixes.md` — cited as `[WF-n]` for the original numbered backlog and as the **page-scoped token** `[INV-WFX-n · proposed]` for entries this spec raised (bare numbers `WF-15` / `WF-16` were claimed concurrently by other pages in the 2026-08-03 round; see that file's §F collision warning). This spec always states the **correct** behavior, never the stale wireframe text — where a `[WF]`-tier scenario pins a stale string, it is labelled a census of the shipped file, not a contract.

Audience: (1) AI agents executing QA end-to-end against this document, (2) developers implementing with zero ambiguity, (3) reviewers.

---

## 1. Purpose & Users

Inventory is the single source of truth for **what stock exists right now, where it physically sits, and every movement that produced it**. It also hosts the monthly stock-take (Stock Audit). It is the only screen in WMS 2.0 that lets an operator move stock **without an order** — the return restock, the damage write-off, the count correction.

### 1.1 The three users and their moments

**A. Warehouse staff — monthly stock audit (primary design driver).**
The auditor walks the racks with the product physically in hand. The screen is on a cart-mounted laptop or a small monitor at arm's length, one-handed operation, often gloved. Everything about the audit UI is shaped by that:

- **Walking-path sort.** Starting the audit re-sorts the whole list by **location ascending** (A-01-04 → A-01-05 → A-02-13 → … → C-02-01, Unassigned last) so the auditor walks lines A → B → C exactly once and never backtracks. Exiting restores Available-descending. `[L-7]`
- **Count entry order = physical shelf order.** Because the sort matches the walk, `Enter`/`Tab` must advance focus to the **next row's** `Counted Qty` input. No mouse between shelves. Reaching for a trackpad on a moving cart is the failure mode this removes.
- **Prefilled counts.** Each `Counted Qty` box is prefilled with the system quantity, so a matching shelf is one keystroke (`Tab`) instead of typing a number. This is a deliberate speed decision recorded in the wireframe; the confirmation-bias risk (an auditor tabbing through without counting) is recorded, not silently reversed `[PD-40 · OWNER-PENDING]`.
- **No refresh, ever.** During an audit, dozens of counted values live only in the DOM until Confirm. A page refresh destroys the walk. `[G-2]` is load-bearing here, not cosmetic.
- **Korean product names.** The auditor identifies the bottle on the shelf by the Korean text printed on the package, so the `Product Name KR` column, the ADJUST detail modals, and the audit summary all carry Korean names with the EN brand in bold `[G-6]`.
- **One number at the bottom.** The audit summary is a single bottom bar (`Total stock loss (sum of diff × product cost): …  — target 0`) rather than a per-row rollup, because at arm's length on a cart only one number is readable at a glance. It is the centre manager's KPI.
- **Loss in ₩ is visible on the floor.** Product cost is exposed to whoever runs the audit — the loss total is the audit's own KPI and hiding it would make the screen useless to the person using it `[PD-43 · OWNER-PENDING]`.
- **On-the-spot fixes.** Unassigned-location rows are **listed, not hidden**, and every row's Location is an editable input, precisely so staff standing at the shelf can fix the data at the moment they see the problem `[L-12]`. Barcode-less products get an inline Barcode input for the same reason.
- **Scanner in hand, but not a scan loop.** Staff usually carry the barcode gun. The Barcode input and the search boxes must tolerate keyboard-wedge input (digits + automatic Enter) without breaking. This page is nonetheless **not** a `[G-1]` surface — there is no scan feed and no auto-advance-on-scan loop; `[G-1]` is scoped to View Orders and Closing. See §9.1 #11.
- **Unregistered items found on a shelf.** Items discovered mid-audit often have no scannable or known barcode, so `[L-13]` searches the **product name** (Korean) with autocomplete and shows the size in the dropdown, because 150ml and 320ml of the same product are visually identical from two metres away.

**B. Order / ops team — reservation and phantom investigation (desk work).**
Sitting at a full monitor, not under speed pressure. They open a SKU, click the amber **Reserved Qty** number, and read which orders hold the units (`[L-M3]`). Cancelled or refunded orders that still hold a reservation are flagged **SUSPECTED PHANTOM** — these are the release targets, and releasing them (`[L-M4]`) is the recovery path that puts sellable stock back. This flow exists because of a recurring field report ("Dean's report") that Reserved counts drifted away from real allocations.

**C. Centre manager / admin — monthly review.**
Opens **Past Audit Logs** (`[L-15]`), reads one row per month, and tracks total loss toward **0**. June 2026 (−₩128,460) exceeded the target and is under root-cause investigation (suspected picking mis-outbound) — that row is the reason the loss column exists at all.

### 1.2 Operational moments served

1. **Monthly stock-take** (audit mode, walking the lines).
2. **SKU lookup during CS / order investigation** (Stock History tab: totals, location, movement history).
3. **Manual in/outbound with no order** — return restock, damage removal, supplier direct receipt (Inbound Stock / Outbound Stock tabs).
4. **Reservation cleanup** — phantom release, restock decision.

### 1.3 What this screen is not

It is not an order screen. It never creates, edits, ships, or cancels an order. It never confirms a PENDING inbound (that belongs to View Orders State 6 / the Inbound Request lifecycle) `[PD-41 · OWNER-PENDING]`. It prints nothing — `[G-4]` does not land here, see §6.4. It never captures a carrier automatically — see `[BR-33]`.

---

## 2. Screen Inventory & Wireframe Map

### 2.1 Declared unit count and numbering gaps

**Total legend units on this page: 16** = 12 numbered dots (**5 – 16**) + 4 modal markers (**M1 – M4**).

Independently verified against the wireframe DOM: sixteen `span.dot` elements exist, carrying `16, 10, 5, 6, 14, 8, 9, 7, 15, 12, 11, 13, M2, M3, M4, M1` in source order, and the legend `<ol>` carries twelve `<li>` entries (one per numbered dot).

Declared numbering artifacts — these are **not** coverage gaps and P3-4 must not flag them:

- **No dots 1 – 4 exist on this page.** The shipped legend's numbering is page-local and starts at 5 (`_wireframe-fixes.md` §E, explicit non-fix).
- **`m-auditlog` (Past Audit Logs list) carries no own dot** — it is the body of legend 15 and is specified under `[L-15]`.
- **`m-adjlog6` (2026-06-30 ADJUST detail) carries no own dot** — it is a second instance of M2 and is keyed `[L-M2b]`. `[WF-14]` proposes annotating both in the legend; optional, no behavior change.

**Plus 5 page-furniture units** carried over from the live admin screen (legend footnote: *"Global nav · Export Stock Status · Search dropdown · Inbound/Outbound forms · event columns … stay as on the live screen"*). These are **not** legend units but **are** implementation units and are keyed `[L-F1]` – `[L-F5]` per the binding convention (`_review.md` §2c item 3).

Footnote item → key map. The footnote names five items; four of them yield the five furniture units above (`Inbound/Outbound forms` is one item covering two), and the fifth is not a unit at all. Nothing in the footnote is left unaccounted for:

| Footnote item | Key | Spec section |
|---|---|---|
| Global nav | `[L-F5]` | §3.21 — **added 2026-08-03**; it was the one carried-over unit with no key and no section |
| Export Stock Status | `[L-F4]` | §3.20 |
| Search dropdown | `[L-F1]` | §3.17 |
| Inbound/Outbound forms | `[L-F2]` / `[L-F3]` | §3.18 / §3.19 |
| event columns | — | Not a separate unit: it is the column contract of `[L-8]` (§3.4) |

**Total implementation units specified in §3: 21** (16 legend + 5 furniture). `[L-M2b]` is a sub-key of `[L-M2]` and adds no unit.

Key style: this page uses plain `[L-{n}]` — the legend dots are numbered once across all four panes, not per pane, so there is no `{state}` segment to key on. Modals are `[L-M{n}]`, the sub-instance is `[L-M2b]`, page furniture is `[L-F{n}]`.

### 2.2 Panes, modals and how to reach each state

Live wireframe: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/stock-status/

| Unit | Screen element | DOM id / selector | How to reach it on the live wireframe | Spec section |
|---|---|---|---|---|
| `[L-5]` | **Current Stocks** pane — default landing | `#p-current` / sub-tab `Current Stocks` | Loads by default. Also wf-bar `Current Stocks (default)` or sub-tab `Current Stocks` | §3.1 |
| `[L-6]` | Reserved Qty → allocated-orders link | `.reslink` (the dotted-underlined `8`) | Sub-tab `Stock History` → `📊 Stock Status` card → click `8` | §3.2 |
| `[L-7]` | **Stock Audit mode** | `#toggleAudit` (`Start Stock Audit` / `Exit Stock Audit`), `.audcol`, `#auditSummary`, `.audrow` | Current Stocks pane → click `Start Stock Audit` | §3.3 |
| `[L-8]` | Stock History Events table + Type/Status badges + filter chips | `.tbl` under `🧾 Stock History Events`, `.filterchip` | Sub-tab `Stock History` or wf-bar `Stock History Search` | §3.4 |
| `[L-9]` | History pagination | not rendered in the wireframe; only the `.morewarn` notice | Sub-tab `Stock History` → bottom notice | §3.5 |
| `[L-10]` | Page rename → **Inventory** | `.ptitle h2` = `WMS — Inventory` | Any pane (page header) | §3.6 |
| `[L-11]` | Default sort = Available descending | `Available` column header | Current Stocks pane | §3.7 |
| `[L-12]` | Editable Location on every row + inline Barcode input | `.loc-in`, `.bcin` | Current Stocks pane, every row | §3.8 |
| `[L-13]` | Add unregistered product (audit mode only) | `.audrow`, `#auSearch`, `#auDrop`, `#auLoc`, `#auQty`, `#auAdd` | Current Stocks pane → `Start Stock Audit` → purple row at the bottom of the table body | §3.9 |
| `[L-14]` | Single location per SKU — By Location card | `📍 By Location` card | Sub-tab `Stock History` | §3.10 |
| `[L-15]` | **Past Audit Logs** modal | `#m-auditlog` | Current Stocks pane → `📋 Past Audit Logs`; or wf-bar `Modal: Past Audit Logs` | §3.11 |
| `[L-16]` | Comments hub | `#inbox1`, `[data-open="inbox1"]` (`💬 Comments`, badge `3`) | Top nav, any pane | §3.12 |
| `[L-M1]` | **Confirm Audit Differences** modal | `#m-adjust` | Audit mode → `Confirm Audit Differences (ADJUST log)`; or wf-bar `Modal: Confirm Audit Differences` | §3.13 |
| `[L-M2]` | Audit session detail — 2026-07-22 (3 ADJUST events) | `#m-adjlog` | `#m-auditlog` → row `2026-07-22` → `View ADJUST events`; or wf-bar `Modal: ADJUST Events (07-22)` | §3.14 |
| `[L-M2b]` | Audit session detail — 2026-06-30 (5 ADJUST events) | `#m-adjlog6` | `#m-auditlog` → row `2026-06-30` → `View ADJUST events`; or wf-bar `Modal: ADJUST Events (06-30)` | §3.14 |
| `[L-M3]` | **Reserved Quantity** modal | `#m-reserved` | Click `.reslink` on the Stock History pane; or wf-bar `Modal: Reserved Orders` | §3.15 |
| `[L-M4]` | **Cancel Inbound (Release Reservation)** modal | `#m-resrelease` | `#m-reserved` → any row's `Cancel Inbound`; or wf-bar `Modal: Cancel Inbound (Release Reservation)` | §3.16 |
| `[L-F1]` | Stock History search bar + 3 result cards | `.searchbar` (`select` + `.inp` + `🔍 Search`), `.cards` | Sub-tab `Stock History` | §3.17 |
| `[L-F2]` | Inbound Form | `#p-inbound`, `＋ Record Inbound` | Sub-tab `Inbound Stock` or wf-bar `Inbound Form` | §3.18 |
| `[L-F3]` | Outbound Form | `#p-outbound`, `－ Record Outbound` | Sub-tab `Outbound Stock` or wf-bar `Outbound Form` | §3.19 |
| `[L-F4]` | Export buttons | `⬇ Export Stock Status` (page header), `⬇ Export` (Current Stocks toolbar) | Page header / Current Stocks pane | §3.20 |
| `[L-F5]` | Global nav + signed-in identity | `.nav` (`.brand`, 6 category labels, 4 `.navlink` tiles, `.user`/`.avatar`, `button.logout`) | Top of every pane | §3.21 |

### 2.3 Navigation contract

- **Four sub-tabs**, left to right: `Current Stocks` (marked `● new · default`) · `Stock History` · `Inbound Stock` · `Outbound Stock`. Exactly one pane is visible at a time.
- **Default landing = Current Stocks.** Decided 2026-07-22 (page rename commit). A direct page load, a nav click, and a legacy `stock-status` route all land on Current Stocks.
- **wf-bar (purple demo bar) is wireframe chrome only** and must NOT be implemented. It holds 10 `.wf-tab` buttons plus the `.wf-toggle` annotation switch. Its four pane buttons mirror the sub-tabs; its six `Modal: …` buttons open a modal **without changing pane state** (2026-08-03 behavior, implemented via `stopImmediatePropagation`). QA uses these as shortcuts and must therefore assert pane state is unchanged after a wf-bar modal shortcut.
- Sub-tab clicks and wf-bar pane clicks stay in sync (the sub-tab handler forwards to the matching wf-tab).
- **Audit mode is a property of the Current Stocks pane.** Switching sub-tabs away and back must not silently end an open audit session — see `[E-52]`.

### 2.4 Annotation layer (QA-critical)

The wireframe renders purple annotation dots. **Three of them are inline inside content nodes**, not absolutely positioned beside them:

- dot `12` inside the `Location` `<th>`
- dot `11` inside the `Available` `<th>`
- dot `13` inside the `.audrow` `<td>`

`body.no-anno` (toggled by the wf-bar button `Hide annotations`, `#annoToggle`) sets `.dot, .legend { display: none !important }`. Because `display:none` nodes are still present in `textContent`, **every text assertion in §8 must use `innerText`, or strip `span.dot` descendants first, after hiding annotations.** This is stated once in §8.0 and assumed by every `[WF]` scenario. Annotations are demo chrome and do not ship.

---

## 3. Functional Specification

Conventions for this section: `[G-2]` and `[G-9]` apply to **every** confirming action on this page and are not repeated per button; `[G-15]` applies to every mutating action. A violation of any of them is a defect against the cited global rule, not against this section. Server revalidates entity state at confirm time and rejects stale writes `[PD-6 · OWNER-PENDING]`; concurrent edits resolve by optimistic version check → 409 → reload the row, except counting flows which merge server-side `[PD-7 · OWNER-PENDING]`.

Toast copies below are **specified**, not suggested. The wireframe has no toast layer, so all toast assertions are `[ADMIN]`-tier in §8.

### 3.1 `[L-5]` Current Stocks tab — default landing, list and filters

**Trigger.** Page load (default), sub-tab `Current Stocks`, nav entry to Inventory, or a legacy route mapped per `[L-10]`.

**Content.** One row per SKU held in the warehouse. Columns, left to right, exactly:
`SKU` · `Image` · `Product Name` · `Product Name KR` · `Size` · `Barcode` · `Sourcing Route` · `Location` · `Total` · `Reserved` · `Available` — plus three audit-only columns `Counted Qty` · `Diff` · `Loss (₩)` that are hidden outside audit mode `[G-14]`.

Per-column render contract:

| Column | Contract |
|---|---|
| `SKU` | Numeric string, tabular numerals, never truncated. It is the join key for every event in §5 |
| `Image` | A fixed 32×32 thumbnail. When a product has no image the cell renders the placeholder box reading `IMG` (the wireframe uses that placeholder on all 11 fixture rows). Never an empty cell, never a broken-image icon `[E-68]` |
| `Product Name` | English, prefixed with the **brand in bold** `[G-6]` (e.g. **Beauty of Joseon** Glow Serum) |
| `Product Name KR` | Korean name, also prefixed with the **EN brand in bold** (e.g. **Dr.Jart+** 포어레미디 리뉴잉 폼). Korean strings are data and are never translated `[G-6]`. The bold-brand prefix on this column was applied 2026-08-03. A product with no Korean name renders `—`, never the English name duplicated `[E-68]` |
| `Size` | Free-form unit string exactly as catalogued (`30ml`, `50ea`, `350ml`, `4g`). It is the disambiguator the auditor reads in `[L-13]`, so it is never abbreviated or hidden |
| `Barcode` | The registered barcode as plain text; a product with none renders the inline `.bcin` input `[L-12]` |
| `Sourcing Route` | **Colorless black bold text, never a colored pill** `[G-5]` `[BR-9]`. JIT carries its purchase channel in parentheses (`JIT (Coupang)`); OTHER carries its free-text channel (`OTHER (channel)`) `[PD-80 · OWNER-PENDING]` |
| `Location` | Editable input on every row `[L-12]` |
| `Total` | All units held |
| `Reserved` | Units allocated to open orders, rendered amber. **Plain text on this table — it is NOT a link.** The reserved drill-down `[L-6]` exists only on the Stock History `📊 Stock Status` card; a second entry point would need a second phantom predicate `[E-97]` |
| `Available` | `Total − Reserved`, rendered green. The sellable number and the default sort key `[L-11]` |

**Filters (toolbar `.cs-controls`), left to right:**

1. **Free-text search**, placeholder `Search SKU / product name`. Matches `SKU`, `Product Name`, and `Product Name KR` as a case-insensitive substring. Debounced; filtering is client-visible and does not reload the page `[G-2]`.
2. **Location filter**, first option `All Locations`. Options after the first are **lines**, one per distinct line letter, derived **dynamically from currently registered locations** — never a hard-coded list `[G-14]` (2026-08-03). The line key is the segment before the first `-` in the location code (`B-02-03` → line `B`); the exact regex and normalization are a developer decision (§9.2). The wireframe ships `Line A` / `Line B` / `Line C` only because those are the lines present in its sample data; registering the first `D-…` location must make `Line D` appear without a reload `[E-10]`. Rows with no location are grouped under an explicit **`Unassigned`** bucket, never dropped `[E-3]`.
3. **Sourcing Route filter**, first option `All Sourcing Routes`, then `SMART BUY` · `JIT` · `WHOLESALE` · `PARTNERSHIP` · `OTHER`.
   - **JIT is included** (confirmed 2026-08-03). Order cancellations and mis-delivery returns leave JIT units physically in the warehouse; that residual stock is listed and filterable like any other route. See `[BR-7]`.
   - Selecting `JIT` matches every JIT row **regardless of purchase-channel suffix** — the sample row renders `JIT (Coupang)` and must match the base route `JIT` `[E-53]` `[G-5]`.
   - **`OTHER` must be present in this filter** and matches rows whose inbound origin was the Inbound Request form's OTHER route; the row label renders as black bold `OTHER ({channel name})` `[PD-80 · OWNER-PENDING]`. The shipped wireframe's filter carries **five `<option>` elements** (`All Sourcing Routes` + the four routes above) and predates this decision; production adds `OTHER` as a **sixth option**. Spec wins — this is a page delta, not a wireframe defect to reproduce. (Counting convention: this document always counts `<option>` elements, including the `All …` placeholder — `QA-CS-05` asserts five, `QA-CS-06` asserts six.)
4. Spacer, then **`⬇ Export`** `[L-F4]`.

**Filter semantics.** Filters are AND-combined with each other and with the search box. Filter state is client-local and is a declared **NON-event** (§5.3, `[NE-3]`). Filter state **is** captured as part of an export event (`[DC-19]`) and as the scope of an audit session (`[DC-7]`). Changing a filter while an audit session is open changes what is visible but never what is in scope `[BR-34]` `[E-66]`.

**Server action.** `GET` a paginated current-stock projection with `q`, `line`, `route`, `sort`, `dir`. Literal endpoint naming is a developer decision.

**Empty states.** No SKUs at all → `[E-1]`. Filter yields zero rows → `[E-2]`.

### 3.2 `[L-6]` Reserved Qty → allocated-orders modal

**Trigger.** Click the `Reserved Qty` value in the `📊 Stock Status` card on the **Stock History** pane. It renders as a dotted-underlined blue link (`.reslink`). Value `8` in the wireframe sample (SKU 100004819).

**Behavior.** Opens `[L-M3]` for that SKU. Read-only fetch; opening the modal mutates nothing.

**Disabled condition.** When `Reserved = 0` the number is **not** a link — plain text, no pointer cursor, no modal `[E-26]`.

**Persistence.** Opening is recorded as a low-signal read event `[DC-30]` so that a later release can be traced to who was looking at what; dev may sample (§9.2).

### 3.3 `[L-7]` Stock Audit mode

The single most operationally sensitive block on this page. Read §1.1 A for the physical context that produced each rule.

**Entry.** Click `#toggleAudit`, label exactly `Start Stock Audit`. On entry, atomically:

1. A new **audit session** is created server-side and `[DC-7]` is persisted with: session id, auditor (actor), start timestamp, and the **scope** — the set of SKU rows visible under the filters in force at that instant `[PD-47 · OWNER-PENDING]`. Filtered/partial audits are allowed; the recorded scope is what makes `SKUs Checked` honest.
2. If another audit session is already active for this warehouse, entry is **blocked** with a red toast naming the active session and its auditor: `Stock audit already in progress — started {HH:MM} by {auditor}` `[PD-44 · OWNER-PENDING]` `[E-23]`. The block itself persists as `[DC-32]`.
3. Button label changes to exactly `Exit Stock Audit`.
4. The three `.audcol` columns (`Counted Qty`, `Diff`, `Loss (₩)`) become visible in header and every body row `[G-14]`.
5. The purple `.audrow` (`＋ Unregistered product found during audit`, `[L-13]`) becomes visible as the last row of the table body.
6. `#auditSummary` becomes visible. It carries class `audcol`, i.e. it is audit-mode-only UI (`display:none` outside audit mode) — this visibility rule was confirmed 2026-08-03 `[G-14]`.
7. The list **re-sorts by Location ascending** (string comparison on the location code). Rows with no location sort **last** (the wireframe uses the `힣` sentinel for this).

**Counted Qty input.** Every row gets a `.qty-in` numeric input, **prefilled with that row's system `Total`** `[PD-40 · OWNER-PENDING]`. Behavior:

- `Enter` or `Tab` commits the value and moves focus to the **next row's** `Counted Qty` (walking order). `Shift+Tab` moves to the previous.
- On commit, `Diff = Counted − Total` renders in the `Diff` column: `0` (neutral), `+n` green, `−n` red.
- `Loss (₩) = Diff × product cost`, rendered `+₩n` green / `−₩n` red / `₩0` grey `[BR-31]`. Product cost source is a **developer decision** (FIFO lot cost recommended, per the Procurement Hub FIFO COGS ledger, vs latest purchase price); the *design* `Loss = Diff × cost` was fixed 2026-07-22 and the source explicitly deferred (§9.2 OQ-1). A SKU with no cost renders `—` and is excluded from the total `[E-25]`.
- Validation: blank, negative, and non-integer values are rejected inline; `Diff` is not computed and the row is treated as not-yet-counted `[E-13]`.
- Counts are **client-side until Confirm**. The page must not refresh `[G-2]`. Draft autosave of in-progress counts is recommended for crash recovery and is a developer decision (§9.2); when implemented it persists as `[DC-24]`.

> **Wireframe fixture note (not a defect).** The shipped wireframe pre-seeds **two** rows with a non-matching count so the Diff/Loss columns have something to demonstrate: SKU `100005104` shows `Counted Qty 17` against `Total 18`, and SKU `100012534` shows `Counted Qty 11` against `Total 9`. The other nine rows are prefilled equal to `Total`. QA asserts this census exactly (`QA-AUD-04`) and must not report it as a prefill bug.

**`#auditSummary` bar.** Text: `Total stock loss (sum of diff × product cost): {total} — target 0`, followed by the button `Confirm Audit Differences (ADJUST log)`. The total is the sum of the `Loss (₩)` column across rows with `Diff ≠ 0`, **excluding new additions** `[L-13]` and excluding SKUs with no cost. It recomputes on every committed count. Wireframe fixture value: `+₩46,260` ( `−₩15,000` + `+₩61,260` ).

**Confirm.** `Confirm Audit Differences (ADJUST log)` opens `[L-M1]`. It never commits anything by itself.

**Exit.** Click `#toggleAudit` (now `Exit Stock Audit`):

- If any count differs from its prefilled/system value, or any row was added via `[L-13]`, a confirm dialog is required: title `Exit stock audit?`, body `{n} entered count(s) will be discarded. The session will be recorded as abandoned.`, buttons `Keep counting` / `Exit and discard` `[PD-5 · OWNER-PENDING]` `[E-21]`.
- On exit: audit columns hide, `#auditSummary` hides, `.audrow` hides, sort restores to **Available descending** `[L-11]`, and `[DC-17]` (`audit.session_abandoned`) persists with the count snapshot.
- Green toast on a clean exit (no entered counts): `Stock audit closed — no adjustments recorded`.

**Session date.** A session belongs to its **start** date, even if it is confirmed after midnight `[BR-36]` `[E-80]`.

### 3.4 `[L-8]` Stock History Events table

**Location.** Stock History pane, below the three result cards. Header `🧾 Stock History Events`.

**Columns, exactly:** `Type` · `Quantity` · `Status` · `Tracking No` · `Carrier` · `Location` · `Order ID` · `Created At` · `Auditor`. This column set is carried from the live admin screen unchanged (legend footnote).

**Type badges** (`.ty`): `INBOUND` (green) · `OUTBOUND` (blue) · `RESERVE` (purple) · `ADJUST` (red). A reservation **release** renders as a `RESERVE` type row and is described in `[L-M4]`.

**Status badges** (`.stt`): `CONFIRMED` (green) · `PENDING` (amber). **Rows with `PENDING` status are highlighted amber** (`tr.pending`).

**Carrier column.** The carrier is whatever the originating movement recorded — an operator's choice on `[L-F2]` / `[L-F3]`, or the carrier already stored on an order-linked movement. It is **never captured automatically**; automatic carrier recording is not supported anywhere in WMS 2.0 `[BR-33]` `[PD-9 · OWNER-PENDING]`. A movement with no carrier renders `–`.

**Created At.** KST, `YYYY-MM-DD HH:MM` in production `[BR-32]`. The wireframe fixture uses the compact `MM-DD HH:MM` form (`07-13 09:12`) for width; that is a fixture, not the contract `[E-71]`.

**Filter chips** (`.filterchip`), exclusive single-select, default `All`: `All` · `Confirmed` · `Pending confirm`. Selecting a chip filters the table; chip state is a declared NON-event (§5.3 `[NE-4]`).

**PENDING semantics — critical boundary.** This page is **display-only for PENDING events**. There is no confirm affordance here, and none may be added. A PENDING inbound is confirmed exclusively through **View Orders State 6** or the **Inbound Request lifecycle** `[G-10]` `[G-11]` `[PD-41 · OWNER-PENDING]`. Two confirm paths for one fact is the double-entry failure this design exists to avoid. The corresponding event `[DC-16]` is therefore rendered here but **never originated here** — see §5.2. When another screen confirms it, this row's badge flips to `CONFIRMED` and the amber highlight clears on the next fetch, with no affordance ever appearing `[E-89]`.

**Auditor column** carries the actor of the event (`Miranti`, `Dean`, `Yongwon`, or `System` for system-generated reservations).

**The table is a view over persisted events, never the only copy** `[G-8]`.

### 3.5 `[L-9]` History pagination

**Problem being fixed.** The live admin screen shows `⚠ More data available (live screen: pagination not implemented)` and simply truncates. The wireframe reproduces that notice with the instruction `→ add pagination`; the **notice must not ship** — pagination replaces it (§9.1 #13).

**Required behavior.**

- Server-side pagination on the Stock History event list. Page size is a developer decision (§9.2).
- Controls render below the table: first / previous / page indicator / next / last, with the total row count.
- Changing any filter chip `[L-8]`, the search key, or the search term **resets to page 1** `[E-40]`.
- Appending a new event while a page is open does not silently reshuffle the current page; the page indicator and total update on the next fetch.
- Boundaries: exactly one page → controls render disabled, not hidden. Last page → `next`/`last` disabled. Zero results → `[E-37]` empty state, no controls.

### 3.6 `[L-10]` Page rename → Inventory

- Page title renders exactly `WMS — Inventory` (`.ptitle h2`).
- Nav label and browser title use **Inventory**.
- The name covers the whole inventory domain: current stock · history · in/outbound.
- **Legacy references must be mapped during development**, not left dangling: the `⬇ Export Stock Status` button label, the `stock-status` route/slug, and any bookmark or deep link from another admin screen. Mapping strategy (redirect vs alias) is a developer decision (§9.2). The button label itself stays `⬇ Export Stock Status` in v1 — it is the live screen's label and is carried over verbatim `[L-F4]`.

### 3.7 `[L-11]` Sorting

- **Default sort: `Available` descending** — most sellable stock first. Wireframe order: `100031877` (82) · `100024743` (61) · `100005088` (55) · `100004819` (34) · `100039958` (23) · `100005104` (16) · `100040311` (11) · `100012534` (6) · `100043697` (4) · `100038120` (2) · `100045210` (1).
- Every column header is clickable to re-sort; first click sorts descending for numeric columns and ascending for text columns, second click reverses.
- **Audit mode overrides the sort** to Location ascending `[L-7]`. Exiting audit mode restores **Available descending** — the default, not the user's last custom sort (the wireframe restores the original order; this spec fixes that as the rule) `[E-9]`.
- Sort state is client-local, a declared NON-event (§5.3 `[NE-3]`).

### 3.8 `[L-12]` Editable Location on every row + inline Barcode input

**Location input (`.loc-in`).** Every row — including audit mode — renders its location as an editable text input, width ~92px, centered, bold. Rows with no location render an **empty input with the amber placeholder `Unassigned`**. Unassigned rows are **listed, never hidden**, so staff at the shelf can assign on the spot.

**Commit semantics.**

- Commit on `Enter` or on blur when the value changed. Committing an unchanged value is a no-op and shows no toast (nothing happened) `[NE-10]`.
- Green toast on success: `Location updated — {SKU} {old} → {new}`; for a first assignment: `Location assigned — {SKU} → {new}`.
- **Clearing** a location to empty is allowed: the row returns to the `Unassigned` bucket, toast `Location cleared — {SKU} {old} → Unassigned`, and `[DC-13]` records `old → null` `[E-76]`.
- **No page refresh** `[G-2]`; the row updates in place, and the Location line filter's option list re-derives so a brand-new line appears immediately `[E-10]`.
- Persists `[DC-13]` (`location.changed`) or `[DC-14]` (`location.assigned`) with old → new. **This is the biggest silent-capture gap on the page today: nothing in Stock History shows location moves.** Persistence is mandatory regardless of UI surfacing; surfacing location moves as a Stock History row type is recommended but not required in v1.

**Validation.**

- Format must match the registered location-code pattern; free text, lowercase, and malformed codes are rejected inline with `Invalid location code` and **nothing is saved** `[E-5]`. The regex is a developer decision (§9.2). A scanned barcode typed into this field fails the pattern and is rejected like any other malformed value `[E-73]`.
- **Location exclusivity is 1:1**: one location per SKU **and** one SKU per location. Assigning a location already held by another SKU is **blocked** with an error naming the occupant: `Location {code} is already assigned to SKU {sku}` `[PD-46 · OWNER-PENDING]` `[E-6]`. The rejection persists as `[DC-28]`.
- Concurrent edits: optimistic version check → 409 → row reloads with a non-green toast; both events remain in the audit trail `[PD-7 · OWNER-PENDING]` `[E-7]`.
- Network failure mid-save: the input reverts to the server value and a red toast names the failure. UI and server must never diverge silently `[E-8]`.

**Barcode input (`.bcin`).** A product with no registered barcode renders a dashed-border input with placeholder `Enter barcode` in the `Barcode` column (same rule as View Orders). Commit on `Enter`/blur, green toast `Barcode registered — {SKU} {barcode}`, persists `[DC-15]` using the canonical cross-page event name `product.barcode_registered`. A barcode already registered to a different SKU is rejected: `Barcode {value} already belongs to SKU {sku}` — persists as `[DC-29]` `[E-4]`. Keyboard-wedge scanner input (digits + automatic Enter) must commit correctly; leading/trailing whitespace and scanner-appended control characters are trimmed before validation `[E-74]`.

> **Selector warning — `.bcin` is not barcode-only in the shipped wireframe.** The wireframe reuses `class="bcin"` for `#auSearch`, the `[L-13]` unregistered-product search box (§3.9), which lives inside the same `<table>` (`tr.audrow`). A `.bcin` query scoped to the table therefore returns **two** nodes, in audit mode and out of it, because `display:none` does not remove the node. QA must scope barcode assertions to the eleven data rows (`tbody tr:not(.audrow) .bcin`) — see `QA-LOC-08`. In production the barcode input and the audit search box must not share a class; the selector for the barcode input is a developer decision (§9.2), but it must be disjoint from the autocomplete input.

### 3.9 `[L-13]` Add unregistered product (audit mode only)

**Visibility.** The `.audrow` exists **only while audit mode is active**. Outside audit mode it is `display:none` and must not be reachable `[G-14]`.

**Row contents, left to right:** the label `＋ Unregistered product found during audit` · `#auSearch` (placeholder `Search product name (autocomplete — barcode not required)`) · `#auLoc` (placeholder `Location`) · `#auQty` (placeholder `Qty`) · `#auAdd` (label `Add`) · the hint `Search by product name, verify the size, then select → Add inserts a new row at the top (Diff = +qty) → merged as ADJUST(+) on confirm`.

> **Shipped-wireframe selector note.** `#auSearch` carries `class="bcin"` — the same class as the `[L-12]` barcode input — and sits inside `tr.audrow`, i.e. inside the Current Stocks `<table>`. That is a class collision, not a functional link: this input never registers a barcode. See the selector warning in §3.8 and the scoping rule in `QA-LOC-08`.

**Autocomplete contract.**

- Typing in `#auSearch` queries the product catalog on **product name (Korean) and SKU**. Barcode is deliberately **not required** — items found on a shelf frequently have no scannable or known barcode.
- Each dropdown entry renders `{Korean name}` in bold, then `· {size} · {SKU}` in grey. **Size must be shown** so the operator can disambiguate visually identical variants (150ml vs 320ml) `[E-15]`.
- Minimum characters before querying and the debounce interval are developer decisions (§9.2). The wireframe queries from the first character against a 5-item fixture (`UNOVE 딥 대미지 트리트먼트` 320ml 100048201 · `UNOVE 실크 헤어 오일` 150ml 100051200 · `Round Lab 자작나무 수분 크림` 80ml 100032911 · `Torriden 다이브인 저분자 세럼` 50ml 100027733 · `AMUSE 듀 틴트` 4g 100044120) and matches case-insensitively against `{name} {sku}`.
- Selecting an entry fills `#auSearch` with `{Korean name} · {size}` and closes the dropdown.
- **No match** renders exactly `No match — register manually via Unrecognized flow (F)`. This is a dead end on this page by design: the operator is handed off to the Unrecognized Tracking flow (§6.2). The handoff itself persists as `[DC-26]` so that "a physical item existed that our catalog does not know" is never lost.

**Add.**

- In production, `Add` is **disabled until an autocomplete entry is selected**. *(Wireframe delta: the shipped `#auAdd` is always enabled and silently no-ops with `focus()` when nothing is selected. QA asserts the wireframe no-op at `[WF]` tier and the disabled state at `[ADMIN]` tier — `QA-AUD-13`.)* `[E-16]`
- Blank `Qty` defaults to `1`; blank `Location` defaults to `Unassigned`. Both defaults are intended `[E-17]`. A non-numeric, zero, or negative `Qty` is rejected inline and no row is inserted `[E-77]`.
- `#auLoc` obeys the same validation and the same 1:1 exclusivity rule as `[L-12]`; an occupied location blocks the Add `[PD-46 · OWNER-PENDING]` `[E-78]`.
- On Add, a new row is inserted **at the top of the table body**, tinted purple, with: SKU, Korean name + a purple `[NEW]` marker, size, `Total 0`, `Reserved 0`, `Available 0`, `Counted Qty = entered qty`, `Diff = +qty` green, `Loss (₩) = — (신규)` (new additions are never losses; the Korean string is data `[G-6]`).
- The inputs clear and the selection resets, ready for the next find.
- Adding a SKU that is already a visible row, or adding the same SKU twice in one session, is **blocked** with an inline notice `Already in this audit — edit the Counted Qty on the existing row` `[E-18]`.
- The added row stays at the top and is **not** re-sorted into the walking order (it was found off-path). It survives an audit-mode toggle within the same session.

**Commit.** New rows merge into `[L-M1]` as `ADJUST(+qty)` and persist as `[DC-9]` (`audit.new_item_added`) with `system 0 → counted n`, location, and a NEW-ADDITION flag. New additions are **excluded from the total loss** and **included in `SKUs Checked`** `[BR-35]` `[E-81]`.

### 3.10 `[L-14]` Single location per SKU — By Location card

- **One SKU has exactly one location.** Confirmed 2026-07-22. The `📍 By Location` card therefore always renders **exactly one row**: `{location pill} {qty}` — in the sample, `A-02-13` / `42`, matching `Total`.
- Card note, verbatim: `One location per SKU — change locations via the Current Stocks input field`. The card is read-only; editing happens on `[L-12]`.
- **Returns merge into the same location** after inspection. The **RETURN-BIN concept was removed 2026-07-22** — there is no separate returns location, no second By Location row, and no RETURN-BIN filter anywhere. See §10 (reversal) and §9.1 #3.
- Multi-row By Location output is a defect.

### 3.11 `[L-15]` Past Audit Logs modal

**Trigger.** Button `📋 Past Audit Logs`, placed **next to** `Start Stock Audit` inside the audit banner. It is visible **outside** audit mode as well (it is history, not audit-only UI). Opens `#m-auditlog`.

**Header.** `Past Audit Logs — monthly session records`.

**Table columns, exactly:** `Audit Date` · `Auditor` · `SKUs Checked` · `Adjustments` · `New Additions` · `Total Loss` · `Detail`.

Wireframe rows (fixtures, byte-accurate for QA):

| Audit Date | Auditor | SKUs Checked | Adjustments | New Additions | Total Loss | Detail |
|---|---|---|---|---|---|---|
| 2026-07-22 | Yongwon | 10 | 2 (−1 / +2) | 1 | +₩46,260 (amber) | `View ADJUST events` → `[L-M2]` |
| 2026-06-30 | Dean | 9 | 5 (−4 / +1) | 0 | −₩128,460 (red) | `View ADJUST events` → `[L-M2b]` |
| 2026-05-31 | Dean | 9 | 0 | 0 | ₩0 · target met (green) | `—` (no link) |

- `SKUs Checked` = rows in the session's recorded scope **plus** rows added via `[L-13]` during the session `[PD-47 · OWNER-PENDING]` `[BR-35]`. The fixture numbers are illustrative, not a formula to reverse-engineer.
- `Adjustments` renders as `{count} ({negative} / {positive})`.
- `Total Loss` colouring: positive = amber, negative = red, zero = green with the suffix ` · target met`.
- A session with zero adjustments still gets a row and renders `—` in Detail (no modal to open) `[E-24]`.
- Note, verbatim: `The center manager's goal is to bring the total loss to 0. Use "View ADJUST events" for each session's adjustment detail — individual events are also recorded as ADJUST type in each SKU's Stock History.`
- **Rows are a view over `[DC-10]`** (`audit.session_confirmed`) `[G-8]`. Monthly sessions are retained indefinitely (§5.4).
- Read-only. No edit, no delete, no re-open `[BR-24]`.

### 3.12 `[L-16]` Comments hub

Behavior is global — cite `[G-7]`. **Page deltas only:**

- Entry point: top-nav button `💬 Comments` with a red unread-count badge (`3` in the wireframe). Opens `#inbox1`. With zero unread mentions the badge is **hidden**, not rendered as `0` `[E-93]`.
- Two tabs: `@ Mentions` (with the unread count) and `★ Saved`. `@ Mentions` pane header: `Comments mentioning me · Click to open the order`, with `Mark all read` on the right. `★ Saved` pane header: `Saved comments · Click to open the order`, with `Unstar to remove from this list`.
- Full-text search box at the top, placeholder `🔍 Search all comments — order no. · author · text`. Typing hides the tab bar and renders a result pane headed `{n} results · newest first · click to open the order`, with the matched substring wrapped in `<mark>`. Clearing the query restores the tabs and the previously active pane. No matches renders `No matching comments` `[E-50]`. Search terms are HTML-escaped before rendering — a term containing markup characters is never interpreted as markup `[E-94]`. Korean terms match Korean comment text without normalization that breaks Hangul `[E-95]`.
- Inventory-context comment examples that must round-trip through this hub (they are the operational reason the hub is on this page): Dean's phantom report on Order 409112, Miranti's PENDING-inbound request on Order 407847, Aldo's ADJUST review request on Order 407506.
- Clicking an entry opens the referenced entity. When the entity is an **unrecognized-pool item**, the click opens the Unrecognized Tracking page focused on that pool row; if the item has already been resolved, it opens the matched order instead `[PD-67 · OWNER-PENDING]` `[E-56]`.
- **This page adds no comment edit or delete affordance**, in the hub or anywhere else `[G-7]` `[PD-3 · OWNER-PENDING]` `[BR-23]`.
- Star/unstar and read-state changes persist per user (`[DC-22]`, `[DC-23]`) using the canonical event names `comment.starred` / `comment.unstarred` / `comment.read` / `comment.mark_all_read`.
- Comment search persists as `[DC-33]`.
- **Cross-page copy variance (declared, 2026-08-03).** `[G-7]` states the hub is identical on all eight screens, but the eight specs do not yet carry byte-identical strings. This page matches the four-page majority on five of the six contested strings (`Comments mentioning me · Click to open the order` · `Saved comments · Click to open the order` · `Mark all read` · `{n} results · newest first · click to open the order` · `No matching comments`). The sixth — the unstar hint — reads `Unstar to remove from this list` here because that is the string the shipped wireframe renders (§8's `[WF]` tier asserts the shipped file); two sibling specs write `Unstar to remove from the list`. **This is a corpus-level defect, not a page decision**: canonicalising the six strings requires publishing them in `_global-rules.md` `[G-7]` and rewriting every divergent spec *and* its QA assertions in one pass. Until that lands, do not "fix" this string on this page alone — that would only move the divergence.
- **Comment-search capture disagreement (declared).** This page persists the hub search as `[DC-33]`; `order-detail` declares the same action a NON-event. That is a `[G-8]` disagreement to be settled corpus-wide, not silently on one page. This page keeps capture, because the search is how an investigator finds the phantom report that precedes a `[L-M4]` release (same reasoning as `[DC-30]`); a reversal means deleting `[DC-33]` and adding an `[NE-*]` row here and nothing else.

### 3.13 `[L-M1]` Confirm Audit Differences modal

**Trigger.** `Confirm Audit Differences (ADJUST log)` in `#auditSummary` (audit mode only).

**Header.** `Confirm Audit Differences — {Month} {Year} Stock Audit (Auditor: {name})` — wireframe: `Confirm Audit Differences — July 2026 Stock Audit (Auditor: Yongwon)`.

**Intro paragraph, verbatim:** `Only items with Diff ≠ 0 are recorded as ADJUST events — a book correction, not Inbound/Outbound (keeps logistics history clean). Auditor · time · audit session are recorded together, and Stock History can filter by ADJUST type.`

**Table columns, exactly:** `SKU` · `Product` · `Location` · `System` · `Counted` · `Diff` · `Action` · `Loss`.

- **Only rows with `Diff ≠ 0`** appear, plus every `[L-13]` new addition. A zero-diff row must never appear.
- Product renders the **Korean** name with the EN brand in bold `[G-6]`.
- New-addition rows are tinted purple, carry a purple `[NEW]` marker, show `System 0` → `Counted n`, `Action` = `ADJUST(+n) added`, and `Loss` = `— (신규)` (Korean string retained as data `[G-6]`).

**Reserved-shortage gate.** Amber note, verbatim: `⚠ Reserved shortage check — if any SKU's counted qty is below Reserved (allocated orders), the affected order list appears here and confirmation is disabled until reviewed. None in this audit.`

- The gate fires when, for any row, `Counted < Reserved` for that SKU. Physically: the shelf holds fewer units than orders have already claimed.
- On fire: the affected orders are listed inside this modal (Order ID, customer, reserved qty, status) and the Confirm button is **disabled**.
- **What unlocks it:** an explicit acknowledgement checkbox in this modal, labelled `Reviewed with the order team`, persisted with the session `[PD-48 · OWNER-PENDING]`. Forcing every shortage to be resolved before confirm would strand the auditor at the shelf; a recorded acknowledgement keeps accountability without stopping the walk.
- The gate firing persists as `[DC-18]`; the acknowledgement persists as `[DC-25]` `[E-14]`. Exiting the audit with the gate fired and unacknowledged persists `[DC-18]` and `[DC-17]` but never `[DC-25]` `[E-84]`.

**Total note, verbatim:** `Total stock loss: {total} (target 0) · the {n} new addition(s) are not losses — on confirm, Current Stocks · Available update immediately; monthly audit logs retained.`

> **`[INV-WFX-1 · proposed]` — the shipped wireframe hard-codes `3` here.** Its note reads *"the **3** new additions are not losses"* while the same modal renders exactly **one** `[NEW]` row and `[L-15]` records `New Additions 1` for the 2026-07-22 session. `{n}` is the contract; `3` is a stale fixture number. `QA-AUD-23` asserts the stale string at `[WF]` tier so the defect stays visible, and `QA-AUD-44` asserts the templatised contract at `[ADMIN]` tier.

**Buttons.** `Cancel` (closes; the session stays open and counts survive — a declared NON-event, §5.3 `[NE-6]`) and `Confirm — record {N} ADJUST events` (wireframe: `Confirm — record 3 ADJUST events`). `{N}` = adjustment rows + new additions.

**Confirm effects — one atomic batch:**

1. One `ADJUST` movement per row → `[DC-8]` (`audit.adjust_confirmed`) with `system qty → counted qty`, diff, the loss, and **the product-cost value actually applied**; each also materializes as an `ADJUST` row in that SKU's Stock History `[L-8]`.
2. Each new addition → `[DC-9]`.
3. The session closes → `[DC-10]` (`audit.session_confirmed`) with audit date, auditor, SKUs checked, adjustment counts (± breakdown), new additions, total loss, confirm timestamp. This is the `[L-15]` row.
4. `Current Stocks` `Total` and `Available` update **immediately**, in place, with no page refresh `[G-2]`.
5. Audit mode exits and the sort restores to Available descending.
6. Green toast: `Stock audit confirmed — {N} ADJUST events recorded · total loss {total}`.

**Atomicity.** All-or-nothing. A partial ADJUST set, or a session row without its events (or the reverse), is a defect `[E-20]`. Double-click produces exactly one batch `[G-9]` `[E-19]`.

**Recompute at confirm.** System quantities and product costs are re-read at confirm time. If stock moved during the walk, `Diff` is recomputed against the **current** system quantity and the modal re-renders with a non-green toast `Stock changed during the audit — differences recalculated` before Confirm can proceed `[PD-6 · OWNER-PENDING]` `[E-22]` `[E-61]`. A scope row deleted or merged system-wide mid-session is dropped from the batch and named in the same toast `[E-82]`.

### 3.14 `[L-M2]` / `[L-M2b]` Audit session detail

Read-only per-session ADJUST list. Opened from `[L-15]` → `View ADJUST events`, or via the wf-bar shortcuts.

**`[L-M2]` header:** `2026-07-22 Stock Audit — 3 ADJUST events (Auditor: Yongwon, confirmed 14:20)`.
**`[L-M2b]` header:** `2026-06-30 Stock Audit — 5 ADJUST events (Auditor: Dean, confirmed 17:05)`.

**Columns, exactly:** `Time` · `SKU` · `Product` · `Location` · `System → Counted` · `Adjustment` · `Loss`.

- All events in one session share the confirm timestamp (`14:20:11`, `17:05:42`) — they are one atomic batch. Session detail renders seconds `[BR-32]`.
- Product renders the **Korean** name with EN brand bold `[G-6]`.
- `Adjustment` renders as an `ADJUST(±n)` badge. New additions are tinted purple and carry `[NEW ADDITION]`, with `Loss` = `—`.
- `[L-M2]` note, verbatim: `Each event is also recorded as ADJUST type in that SKU's Stock History — search the SKU and filter by type to inspect individually. Total loss +₩46,260 (new additions excluded).`
- `[L-M2b]` note, verbatim: `Total loss −₩128,460 — June exceeded the loss target; root-cause investigation in progress (suspected picking mis-outbound).`

**Doctrine.** These modals and the SKU-level Stock History are **two views over one persisted event** `[G-8]`. There is no second copy and no separate audit-only ledger.

**No mutation.** No edit, no reversal, no delete. A wrong adjustment is corrected by a new adjustment `[BR-24]`.

### 3.15 `[L-M3]` Reserved Quantity modal

**Header:** `Reserved Quantity — {KR product name} {size} ({SKU}) · {n} reserved` — wireframe: `Reserved Quantity — **Dongkook** 마데카솔 크림 50ml (100004819) · 8 reserved`.

**Columns, exactly:** `Order ID` · `Order Date` · `Customer` · `Status` · `Reserved Qty` · `Reserved At` · `Action`.

Wireframe rows:

| Order ID | Order Date | Customer | Status | Reserved Qty | Reserved At | Action |
|---|---|---|---|---|---|---|
| 407812 | 2026-06-30 | Sarah Kim | `processing` (green) | 2 | 07-12 11:05 | `Cancel Inbound` (grey) |
| 413650 | 2026-07-08 | Emma Park | `processing` (green) | 3 | 07-08 14:22 | `Cancel Inbound` (grey) |
| 409112 | 2026-07-02 | Liam Chen | `cancelled` (red) + `SUSPECTED PHANTOM` (amber) | 3 | 07-02 09:10 | `Cancel Inbound` (red outline) |

- **Order ID is a deep link** to that order's detail screen `[G-12]`.
- **Phantom predicate:** order status ∈ {`cancelled`, `refunded`} **AND** the reservation was never released. Matching rows get an amber row background and the `SUSPECTED PHANTOM` badge, and their `Cancel Inbound` button is rendered in red outline — these are the release targets. A **partially refunded** order is a boundary case: it is flagged only if the reservation exceeds the still-live line quantity `[E-28]`.
- Note, verbatim: `Total 8 = 2+3+3 · Suspected phantom = the order is cancelled/refunded but the reservation was never released — release target. If reservation-order mismatches persist, investigate unconfirmed events with the Pending confirm filter in Stock History (linked to Dean's report).` The phrase `Pending confirm filter` is an in-page link that switches to the Stock History pane with the `Pending confirm` chip active.
- **Integrity checks:** the sum of row `Reserved Qty` must equal the header count `[E-27]`, and the header count must not exceed the SKU's `Total` `[E-87]`. Either mismatch renders an explicit red data-integrity banner inside the modal rather than silently displaying a wrong total; rows still render so cleanup remains possible.
- A row whose order record is unreadable or hard-deleted renders `Order unavailable` in place of the link and still exposes `Cancel Inbound` — the stock must remain recoverable `[E-86]`.
- Read-only apart from the per-row `Cancel Inbound` action.

### 3.16 `[L-M4]` Cancel Inbound (Release Reservation) modal

The most destructive action available on this page. Four explicit steps.

**Header:** `Cancel Inbound — Order {id} · {KR product name} × {qty}` — wireframe: `Cancel Inbound — Order 409112 · **Dongkook** 마데카솔 크림 × 3`.

**Step 1 — Release.** Bold line `1. Release the reservation (Reserved) on this order?` with the grey explainer `A phantom reservation left on a cancelled order — releasing it unlinks this order.`

**Step 2 — Restock decision.** Bold line `2. Restock the units?`, two radios (`name="resback"`), default = first:

- `Yes — Available +{n} (restock)` — units go back into sellable stock.
- `No — exclude from stock (damaged · lost etc., record the loss as ADJUST(−{n}))` — units are written off.

**Step 3 — Restock Qty.** Bold line `3. Restock Qty`, numeric input, **default = the quantity originally inbounded for this reservation**, editable, with the grey hint `Default = qty originally inbounded (editable)`.

- Editing **above** the reserved/inbounded quantity is **blocked** with inline validation `Restock qty cannot exceed the inbounded qty ({n})` — restocking more than was taken creates phantom stock `[PD-50 · OWNER-PENDING]` `[E-30]`.
- Editing **below** the released quantity is **allowed**; the remainder is auto-recorded as `ADJUST(−remainder)` carrying the same memo. Partial damage is the exact use case `[PD-49 · OWNER-PENDING]` `[E-31]`.
- Setting it to `0` while `Yes` is selected is **blocked** with `Choose "No" to write the whole quantity off` — a zero-quantity restock is a mislabelled write-off `[E-85]`.

**Step 4 — Memo (optional).** Textarea, placeholder `Cancellation reason or notes — if written, also recorded in the order's Comments history`.

- A written memo **dual-writes**: it is stored on the release event **and** posted to the order's Comments history `[DC-11]` with `source=m4-memo`.
- A memo containing an `@mention` routes to Slack exactly like any other comment `[G-7]` → §6.1, persisting `[DC-12]`.
- An empty memo produces **no** comment.

**Note, verbatim:** `On release, Reserved 8 → 5; choosing "Yes" brings Available 34 → 37. The action is recorded in Stock History as a RESERVE release event.`

**Buttons.** `Cancel` (closes, nothing written — declared NON-event `[NE-7]`) · `Confirm`.

**Confirm effects — one atomic composite event:**

| Restock | Effects |
|---|---|
| **Yes** | `[DC-4]` reserve released (Reserved 8 → 5) **+** `[DC-5]` restocked (Available 34 → 37). Stock History gains a `RESERVE` release row. Toast: `Reservation released — Order {id} · restocked +{n}` |
| **No** | `[DC-4]` reserve released (Reserved 8 → 5, Available unchanged) **+** `[DC-6]` `ADJUST(−n)` loss with classification `damaged \| lost`. Stock History gains a `RESERVE` release row **and** an `ADJUST(−n)` row. Toast: `Reservation released — Order {id} · ADJUST(−{n}) recorded` |
| **Yes, qty below released** | `[DC-4]` + `[DC-5]` for the entered qty + `[DC-6]` `ADJUST(−remainder)` with the same memo `[PD-49 · OWNER-PENDING]` |

**Guards.**

- **Cancel Inbound on an ACTIVE (`processing`) order is allowed**, with an extra confirmation naming the live order: `Order {id} is still processing — release anyway?`. The wireframe deliberately shows the button on `processing` rows; blocking it would strand genuine over-reservations `[PD-45 · OWNER-PENDING]` `[E-29]`.
- Stale row (already released, order state changed while the modal was open) → server rejects with a red toast `Reservation already released` and `[L-M3]` re-fetches; counts are never double-adjusted. The rejection persists as `[DC-31]` `[PD-6 · OWNER-PENDING]` `[E-34]` `[E-35]`.
- Release and restock are **one atomic composite**. A "released but not restocked" limbo state is a defect `[E-33]`.
- Double-click Confirm produces exactly one release and one adjustment `[G-9]` `[E-32]`.
- Destructive action → confirm step + toast, both mandatory `[PD-5 · OWNER-PENDING]`.

**Cross-page contract conflict — declared, not resolved here (2026-08-03).** Three screens can reverse the same inbound and they do not currently agree:

| Screen | Restock decision | Quantity | The un-restocked remainder |
|---|---|---|---|
| **Inventory `[L-M4]` (this page)** | Yes / No radios | editable, capped above at the inbounded qty | booked as `ADJUST(−remainder)` `[DC-6]`, `source = m4-remainder` |
| View Orders `[L-M1]` | Yes / No radios | editable | "accounted for by the memo" — **no stock event** |
| Order Detail `[L-2]` | none; hard-codes `restock=true` | none; reverses the whole line | n/a |

This page's contract is the only one that keeps the ledger closed: a memo is not an inventory event, and `[G-8]` requires the units to land somewhere. **Inventory therefore does not change its behavior**; the reconciliation is owed by the other two specs (and, if the owner picks a different winner, by a dated delta here). Order Detail's §6.5 already asserts the paths converge on "one reversal per line" — that guarantee is what makes the divergence a defect rather than three legitimate variants. `[PD-45 · OWNER-PENDING]` `[PD-49 · OWNER-PENDING]` `[PD-50 · OWNER-PENDING]`

### 3.17 `[L-F1]` Stock History search bar and result cards

**Search bar (`.searchbar`).**

- **Key dropdown**, options: `SKU` · `Product Name` · `Order ID` · `Tracking No` · **`Barcode`**. Barcode is a **5th key added by this spec** so that an operator holding a physical product can scan-to-look-up instead of typing from memory `[PD-42 · OWNER-PENDING]`; the shipped wireframe lists only the first four.
- **Term input**, placeholder switches with the key (`Enter SKU (e.g. 100004819)` for SKU). `Product Name` matches partially and case-insensitively across EN and KR names. `SKU`, `Order ID`, `Tracking No`, and `Barcode` match exactly.
- **`🔍 Search`** button; `Enter` in the input submits the same query.
- Each executed search persists `[DC-21]` (key type + term + result count). Dev may sample (§9.2).
- Tracking numbers: inbound (supplier → warehouse) and outbound (warehouse → customer) tracking numbers are **separate namespaces and may coincide**; a `Tracking No` search here returns movement events from both and labels each by movement type `[PD-8 · OWNER-PENDING]` `[E-63]`.
- A `Barcode` search that matches more than one catalogue product (pre-existing duplicate data) returns all matches with SKU and size for disambiguation rather than silently picking one `[E-75]`.

**Result cards (`.cards`), three, left to right:**

1. **`📊 Stock Status`** — `Total Qty` (neutral) · `Reserved Qty` (amber, the `[L-6]` link) · `Available Qty` (green). Note: `Click Reserved → allocated orders modal (incl. releasing phantom orders · restock)`.
2. **`📍 By Location`** — see `[L-14]`.
3. **`🧴 Product Information`** — key/value rows: `SKU` · `Name` (EN) · `Name KR` (Korean with EN brand bold) · `Brand` · `Sourcing Route` (black bold `[G-5]`). Wireframe sample: `100004819` / `Madecassol Cream 50ml` / **Dongkook** 마데카솔 크림 / `Dongkook` / `SMART BUY`.

**Empty result.** Unknown SKU / no events → all three cards render an explicit empty state and the events table renders its own empty state; no partial or stale card content `[E-37]`.

### 3.18 `[L-F2]` Inbound Form (Inbound Stock tab)

**Purpose note.**

- **Correct copy — this is what ships:** `Record a warehouse inbound directly, without a specific order (return restock · manual inbound). Location auto-applies the SKU's single registered location. For order-linked inbound, use the row Inbound buttons on View Orders or Order Detail.`
- **Shipped wireframe string (stale — `[INV-WFX-2 · proposed]`):** its final sentence still reads `For order-linked inbound, use Request Inbound on View Orders / the order detail.` **`Request Inbound` is a retired control name.** Neither named page has such a button — View Orders uses row `Inbound` / `Inbound + Outbound` / `Bulk Inbound (Selected)`, Order Detail uses per-row `Inbound` + `Bulk Inbound Selected Items` — and Order Detail's spec forbids the name reappearing anywhere. Promoting the stale sentence to a byte-exact production contract would send an operator to a button that does not exist. `QA-FRM-03` asserts the shipped string at `[WF]` tier (wireframe census only); `QA-FRM-20` asserts the corrected string, and the total absence of `Request Inbound`, at `[ADMIN]` tier.

**Fields — exactly five, in this order:** `SKU *` (placeholder `100004819`) · `Quantity *` (number, placeholder `0`) · `Tracking No` (placeholder `Optional`) · `Carrier` (select: `Coupang` · `Deleo` · `Direct`) · `Order ID (optional)` (placeholder `If linked`).

**There is no Location field.** It was **removed 2026-07-22** under the single-location-per-SKU principle — location auto-applies from the SKU's registered location. Re-adding it is a defect (§9.1 #2).

**Carrier is operator-selected.** The select is a manual choice and must never be auto-populated from a scan or a tracking-number lookup `[BR-33]` `[PD-9 · OWNER-PENDING]`. Whether the option list stays fixed or reads a carrier registry is a developer decision (§9.2).

**Button:** `＋ Record Inbound` (green).

> **Glyph contract (2026-08-03).** The leading characters are **fullwidth**: `＋` is U+FF0B FULLWIDTH PLUS SIGN and `－` (on `[L-F3]`) is U+FF0D FULLWIDTH HYPHEN-MINUS. They are byte-exact contract characters — the wireframe is SST for button labels, and §8 asserts these labels literally. `_global-rules.md` `[G-3]` writes the same Inventory button as `− Record Outbound` with U+2212 MINUS SIGN; that is a typographic variant in a prose enumeration, **not** a second button and not a different label. An implementer must copy the glyphs from this section, never from the `[G-3]` scope sentence.

**Behavior.**

- Validation before any server write: SKU must resolve to a catalog product (`Unknown SKU — {value}`, persists `[DC-27]`) `[E-41]`; Quantity must be a positive integer (`Quantity must be a positive whole number`) `[E-42]`.
- Location auto-applies. If the SKU has **no** registered location, the movement is still accepted and the resulting row lands `Unassigned` with a prompt toast `Inbound recorded — {SKU} +{n} · location unassigned, please assign it` `[E-43]`. (The mandatory-location gate of `[PD-13 · OWNER-PENDING]` is a **View Orders State 6** rule; it does not gate this manual form.)
- Success → green toast `Inbound recorded — SKU {sku} +{n}`, `[DC-1]` persists, and a new `INBOUND` row appears in that SKU's Stock History with status `CONFIRMED`. Totals update in place, no refresh `[G-2]`.
- An `Order ID` that does not exist is rejected before write (link integrity) `[E-48]`. A `Tracking No` already present on another movement raises a non-blocking warning `Tracking {no} already recorded on {date} — record anyway?` `[E-49]`.
- A movement recorded for a SKU inside an open audit session's scope is **not blocked**; the audit recomputes that row's diff at confirm `[E-22]` `[E-90]`.
- Double-submit produces exactly one movement `[G-9]` `[E-46]`. Network failure produces no phantom movement; retry is idempotent `[E-47]`.
- **No send sound** — `＋ Record Inbound` is not an outbound-class button `[G-3]`.

### 3.19 `[L-F3]` Outbound Form (Outbound Stock tab)

**Purpose note, verbatim:** `Record a warehouse outbound directly. Location auto-applies the SKU's registered location; outbound exceeding Available Qty is blocked.`

**Fields — exactly five, same order as `[L-F2]`**, with `Carrier` options `Deleo` · `YUN` · `Coupang`. **No Location field** (removed 2026-07-22). Carrier is operator-selected and never auto-captured `[BR-33]`.

**Button:** `－ Record Outbound` (blue).

**Behavior.**

- **`－ Record Outbound` is an outbound-class button and therefore carries the `[G-3](a)` send sound** `[PD-2 · OWNER-PENDING]`. There is **no TTS** on this page; `[G-3](b)` is Closing-only, and `[G-3](c)` is a View Orders page delta.
- **Availability gate:** the quantity is checked against **`Available` (`Total − Reserved`), never `Total`** `[E-45]`. Exceeding it is blocked before any write with the red toast `Outbound blocked — exceeds Available Qty ({available})`; the attempt persists as `[DC-20]` (repeated rejections are a count-drift signal) `[E-44]`. A SKU whose `Available` is already `0` blocks every quantity with `{available}` rendered as `0` `[E-91]`.
- **Boundary:** `qty = Available` is allowed and drives Available to 0 while leaving Reserved intact.
- Success → green toast `Outbound recorded — SKU {sku} −{n}`, `[DC-2]` persists, a new `OUTBOUND` row appears with status `CONFIRMED`, totals update in place `[G-2]`.
- Same validation, link-integrity, idempotency, and network-failure rules as `[L-F2]` `[E-41]` `[E-42]` `[E-46]` `[E-47]` `[E-48]` `[E-49]`.

### 3.20 `[L-F4]` Export

Two buttons, both grey, both file downloads:

- **`⬇ Export Stock Status`** — page header, top right. Exports the **whole current-stock projection**, ignoring the Current Stocks toolbar filters. The label is a legacy name retained verbatim from the live screen and is mapped during development `[L-10]`.
- **`⬇ Export`** — Current Stocks toolbar, right side. Exports **the currently filtered view** (search term + line filter + route filter + sort).

Rules for both:

- Each export persists `[DC-19]` with: which export, the full filter state, the sort, the row count, actor, timestamp — *who took stock data out of the building*.
- Whether the three audit-only columns are included when audit mode is active is a **developer decision**; the recommended default is to include them with the session id in the filename `[E-54]` (§9.2).
- File format, encoding, and column set are developer decisions (§9.2).
- Zero rows → the export is still produced with headers only, plus a non-green toast `Exported 0 rows`.
- A large export runs asynchronously behind a non-green `Preparing export…` toast and **never** refreshes the page `[G-2]`; rapid repeat clicks produce exactly one job each `[G-9]` `[E-92]`.
- Export is not a print surface. There is no Print button on this page `[G-4]` — see §6.4.

### 3.21 `[L-F5]` Global nav and signed-in identity

Carried over from the live admin screen unchanged (legend footnote). It is page furniture, not a legend unit, but it is the **actor source for every `[G-8]` event on this page**, so it is specified rather than assumed.

**Contents, left to right, exactly as shipped:**

1. Brand wordmark `SkinSeoul`.
2. Six category dropdown labels: `Operation AI ▾` · `Catalog Management ▾` · `OMS Center ▾` · `Site Management ▾` · `System Management ▾` · `Customer Management ▾`. Their menu contents belong to the platform shell and are out of scope here.
3. Four `.navlink` quick tiles: `Agent Telemetry` · `Role Assets` · `Shared Asset Health` · `SkinSeoul WP Admin`.
4. The Comments hub entry point `💬 Comments` with its unread badge — specified separately as `[L-16]` (§3.12).
5. The signed-in user chip (`.user`): a round `.avatar` initial followed by the display name — `Y` / `Yongwon Ryu` in the wireframe.
6. `Logout`.

**Rules.**

- **The user chip is the actor of record.** Every event in §5 records the signed-in identity rendered here; a mutating action with no resolved actor is a defect `[G-8]` `[G-15]` `[PD-1 · OWNER-PENDING]` (asserted by `QA-GLB-04`). v1 ships a single admin role, so the nav renders no role switcher and no permission chip `[BR-28]`.
- **Nav clicks are navigation, not intent** — a declared NON-event `[NE-13]` (§5.3). Leaving Inventory through a category dropdown or a `.navlink` tile persists nothing.
- **`Logout` ends the platform session** and returns to the sign-in screen. Its audit record is owned by the platform auth layer, not by Inventory: this page neither emits nor renders a session event (§9.1, "Also out of scope"). Logging out while an audit session is open does **not** confirm it and does **not** abandon it — the session stays open server-side and remains recoverable by the same auditor `[E-57]`.
- The nav is identical on all eight screens; only the active category and the hub entry point differ. **This spec declares no delta on it** — a change here is a change to the platform shell, not to Inventory.

---

## 4. Business Rules

Page-specific rules. Global rules are cited, never restated. Every rule carries a rationale and a decision date. Reversals appear in §10.

> **`BR` ID re-assignment note (declared once, 2026-08-03).** The `[E-n]` and `[DC-n]` families were carried ID-for-ID from the two `_plans/stock-status.{A,B}.md` lenses. The `[BR-n]` family was **not**: it was re-assigned on 2026-08-03 to accommodate 20 new rules. Mapping from `stock-status.A.md`: A-2→3 · A-7→13 · A-8→16 · A-9→10 · A-10→20 · A-12→9 · A-13→25 · A-16→19; A-11 / A-14 / A-15 were absorbed into `[L-10]` / `[G-9]` / `[G-2]` and have no `BR` row here. This is recorded because `_review.md` §3 item 2 says **never renumber** — the re-assignment already happened, so it is declared rather than hidden. **Do not renumber again.**

| ID | Rule | Rationale | Decided |
|---|---|---|---|
| **BR-1** | **One location per SKU, and one SKU per location (1:1).** The `📍 By Location` card always shows exactly one row. Assigning an occupied location is blocked, naming the occupant. `[G-14]` `[PD-46 · OWNER-PENDING]` | The audit walking order and the By Location card both assume a 1:1 mapping; a many-to-many scheme makes the walk non-deterministic and the card meaningless. | 2026-07-22 (one location per SKU) · 1:1 exclusivity provisional 2026-08-03 (global-rule delta **GD-7**, defined in `_plans/_review.md` §4 — the `[GD-n]` deltas are not defined inside `_global-rules.md`, so every `GD` citation in this spec names its source file) |
| **BR-2** | **Returns merge into the SKU's normal location** after inspection. There is no RETURN-BIN. | One physical place to look. A separate returns bin created a second source of truth that nobody reconciled. | 2026-07-22 (RETURN-BIN removed — reversal, §10) |
| **BR-3** | **ADJUST is a book correction, never an Inbound or an Outbound.** Audit differences and write-offs are recorded as `ADJUST(±n)`, not as movements. | Keeps the logistics history clean: `INBOUND`/`OUTBOUND` mean goods physically crossed the dock. Mixing corrections into them destroys throughput analysis. | 2026-07-22 (M1 copy) |
| **BR-4** | **Loss = Diff × product cost**; the session total targets **0** and is the centre manager's KPI. New additions are excluded from the loss total. Product-cost source is a developer decision (FIFO lot cost recommended). | A count difference is only meaningful in money. New stock found is not a loss and would flatter the number. | Design fixed 2026-07-22; cost source explicitly deferred to dev the same day |
| **BR-5** | **Page delta on `[G-14]`:** on this page the audit-mode-only set is exactly `Counted Qty`, `Diff`, `Loss (₩)`, `#auditSummary`, and `.audrow`. Nothing else is gated on audit mode. `[G-14]` | The daily user of this screen is not an auditor. Permanently visible count boxes invite accidental edits and make the table unreadable at cart distance. | 2026-08-03 |
| **BR-6** | **Page delta on `[G-14]`:** the dynamically derived list on this page is the **Location filter's line list**, and the line key is the segment before the first `-` in the location code. `[G-14]` | The warehouse adds racks. A hard-coded list silently hides new stock the day a line is added. | 2026-08-03 |
| **BR-7** | **JIT residual stock is listed and filterable.** `JIT` is an option in the Sourcing Route filter and JIT rows appear in Current Stocks like any other route. Channel-suffixed labels (`JIT (Coupang)`) match the base route `JIT`. | JIT is buy-on-demand, so in theory nothing rests in the warehouse — but order cancellations and mis-delivery returns leave units behind, and stock you cannot filter for is stock you cannot sell. Origin path: an order cancelled after its lines were inbounded, then Cancel Inbound with restock `[PD-22 · OWNER-PENDING]`. | 2026-08-03 |
| **BR-8** | **`OTHER` is a sourcing-route value on this page** and renders as black bold `OTHER ({channel})`. `[G-5]` `[PD-80 · OWNER-PENDING]` | The Inbound Request form has offered a free-text OTHER channel since 2026-07-26; stock arriving through it must render and filter somewhere. | 2026-07-26 (form) · downstream rendering provisional 2026-08-03 |
| **BR-9** | **Route cells on this page follow `[G-5]` and this page adds no route styling of its own** — not in the Current Stocks `Sourcing Route` column, not in the `🧴 Product Information` card, not in the filter. `[G-5]` | Colour is reserved for state (amber = reserved, green = available, red = loss). Spending it on a static attribute makes the state colours unreadable. | Carried from View Orders; reconfirmed 2026-08-03 |
| **BR-10** | **Sort: `Available` descending by default; `Location` ascending in audit mode; exit restores `Available` descending.** | Available-desc answers the desk question ("what can I sell"). Location-asc answers the floor question ("what do I walk past next"). Exit restores the default rather than a stale custom sort so two auditors see the same screen. | 2026-07-22 (Available desc) · 2026-07-22 (audit re-sort) |
| **BR-11** | **Rows with no location are listed, never hidden**, are grouped in an explicit `Unassigned` filter bucket, and sort **last** in the audit walking order. | They are the rows most in need of a human standing at a shelf. Hiding them guarantees they stay broken. | 2026-07-22 |
| **BR-12** | **Counted Qty is prefilled with the system quantity.** `[PD-40 · OWNER-PENDING]` | A matching shelf becomes one keystroke. The confirmation-bias risk is recorded for the owner rather than reversed silently — the wireframe is the SST. | Wireframe behavior 2026-07-22; adopted provisionally 2026-08-03 |
| **BR-13** | **The Reserved-shortage gate blocks audit confirmation.** When any `Counted < Reserved`, Confirm is disabled until the auditor ticks `Reviewed with the order team`. `[PD-48 · OWNER-PENDING]` | Counting fewer units than orders have claimed means someone's order cannot ship. Confirming past it silently converts a fulfilment failure into a book adjustment. An acknowledgement keeps the walk moving while fixing accountability to a person. | Gate 2026-07-22 (M1) · unlock mechanism provisional 2026-08-03 |
| **BR-14** | **Exactly one active audit session per warehouse, with a single auditor of record.** A second Start is blocked naming the active session. `[PD-44 · OWNER-PENDING]` | The session schema has one auditor and one loss total and therefore no merge semantics. Parallel sessions would produce two truths for one shelf. | Provisional 2026-08-03 |
| **BR-15** | **Partial / filtered audits are allowed.** The session records its scope (the filtered row set at session start). `[PD-47 · OWNER-PENDING]` | Full-catalog-only audits are impractical at this volume. Recording the scope keeps the number honest instead of pretending a line-A walk covered the warehouse. | Provisional 2026-08-03 |
| **BR-16** | **Outbound is blocked when the quantity exceeds `Available`** (`Total − Reserved`), never merely `Total`. `qty = Available` is allowed. | Shipping into reserved stock steals units from an order that is already promised. | Live-screen rule, carried 2026-07-14 |
| **BR-17** | **The Inbound and Outbound forms have no Location field**; location auto-applies from the SKU's single registered location. | Direct consequence of BR-1 — a second place to type a location is a second place to get it wrong. | 2026-07-22 (field removed — §9.1 #2) |
| **BR-18** | **Inventory is display-only for `PENDING` events.** No confirm affordance exists or may be added here; confirmation happens only in View Orders State 6 / the Inbound Request lifecycle. `[G-10]` `[G-11]` `[PD-41 · OWNER-PENDING]` | Two confirm paths for one fact is the double-entry failure the whole design avoids. | Provisional 2026-08-03 |
| **BR-19** | **Suspected phantom = order status ∈ {cancelled, refunded} AND the reservation was never released.** Such rows are flagged and are the release targets. | Field-reported drift between Reserved counts and real allocations ("Dean's report"). A predicate makes the drift findable instead of anecdotal. | 2026-07-23 (M3) |
| **BR-20** | **M4 Restock Qty defaults to the quantity originally inbounded and is editable**, capped above at that quantity and open below it, with the remainder auto-recorded as `ADJUST(−remainder)`. `[PD-49 · OWNER-PENDING]` `[PD-50 · OWNER-PENDING]` | The default is right in the common case. Restocking more than was taken creates phantom stock; restocking less is the partial-damage case and must not need a second manual adjustment. | 2026-07-23 (default) · bounds provisional 2026-08-03 |
| **BR-21** | **Cancel Inbound on an ACTIVE (`processing`) order is allowed with an extra confirmation naming the order.** `[PD-45 · OWNER-PENDING]` | The wireframe deliberately exposes the button on processing rows. Blocking it would strand genuine over-reservations with no recovery path on any screen. | Provisional 2026-08-03 |
| **BR-22** | **An M4 memo dual-writes** to the release event and to the order's Comments history; an `@mention` inside it routes to Slack like any other comment. `[G-7]` | The reason a reservation was killed belongs on the order, where CS reads it — not only in a stock ledger nobody opens. | 2026-07-23 |
| **BR-23** | **This page adds no comment edit or delete affordance**, in the hub or anywhere else. `[G-7]` `[PD-3 · OWNER-PENDING]` | The comment corpus is an audit and AI-training asset; a per-page mutation path would silently rewrite it. | Provisional 2026-08-03 |
| **BR-24** | **Audit sessions and their ADJUST events are immutable.** No edit, no reversal, no delete on `[L-15]` / `[L-M2]`. A wrong adjustment is corrected by a new adjustment. | A retro-edited count destroys the meaning of the loss KPI it was measured against. | 2026-07-22 |
| **BR-25** | **Unregistered products are found by product name, not by barcode**, and the size is always shown in the dropdown. Items with no catalog match are handed to the Unrecognized flow, not registered ad hoc here. | Shelf-found items usually have no scannable or known barcode; and two sizes of one product are visually identical at reading distance. Ad-hoc catalog creation from an audit screen would let anyone mint SKUs. | 2026-07-23 |
| **BR-26** | **Page delta on `[G-8]`: rejections persist too.** The six rejection events on this page — `[DC-20]`, `[DC-27]`, `[DC-28]`, `[DC-29]`, `[DC-31]`, `[DC-32]` — are operator-initiated and therefore in scope of `[G-8]`, even though nothing changed. `[G-8]` | Rejections (blocked outbounds, blocked locations, blocked concurrent audits) are the drift signal; discarding them discards the diagnosis. | 2026-08-03 (owner doctrine) |
| **BR-27** | **This page has no Print surface.** `[G-4]` does not land here; Export produces files only. | Nothing on this screen is a physical artifact a picker carries. Adding a print path would require the local print agent for no operational gain. | 2026-08-03 |
| **BR-28** | **Page delta on `[G-15]`: this page adds no gate of its own.** The three actions an implementer would most plausibly gate — audit start/confirm `[L-7]` `[L-M1]`, reservation release `[L-M4]`, and product-cost / `Loss (₩)` visibility — are **ungated in v1**. `[G-15]` `[PD-1 · OWNER-PENDING]` | Six screens independently raised the same question; inventing per-page gates would produce eight inconsistent models. | Provisional 2026-08-03 |
| **BR-29** | **Loss (₩) and product cost are visible to whoever runs the audit** — no admin-only split in v1. `[PD-43 · OWNER-PENDING]` | The loss total is the audit's own KPI. Hiding it makes the audit screen unusable to the auditor. | Provisional 2026-08-03 |
| **BR-30** | **A Slack delivery failure never blocks or rolls back the primary action.** It is persisted and retried. `[PD-4 · OWNER-PENDING]` | Notification is a side effect, not part of the transaction. | Provisional 2026-08-03 |
| **BR-31** | **All money on this page is KRW (`₩`)**, thousands-separated and signed: `+₩61,260` · `−₩15,000` · `₩0`. A value with no cost basis renders `—`. No `$`, no `USD`, no currency selector. | The warehouse, the product costs, and the loss KPI are Korean-domiciled operational figures. The company's USD reporting currency governs sales reporting, not this ledger — stating it here stops a well-meaning "currency fix". | Wireframe 2026-07-22; declared explicitly 2026-08-03 |
| **BR-32** | **All timestamps render in KST (Asia/Seoul)**: `YYYY-MM-DD HH:MM` in list columns, `HH:MM:SS` in audit-session detail. No relative times ("2 hours ago") anywhere. | Warehouse staff reconcile against paper and against carrier portals, both of which are wall-clock KST. Relative times cannot be reconciled at all. | 2026-08-03 |
| **BR-33** | **Carrier is always operator-selected or carried from the originating movement, and is never auto-captured.** The `Carrier` column and both form selects are not an exception to the program-wide decision that automatic carrier recording is NOT supported. `[PD-9 · OWNER-PENDING]` | Review conflict C-1 resolved against auto-capture. Without this sentence an implementer reading C-1 either strips this page's manual carrier fields or, worse, wires scan-time capture into them. | 2026-08-03 (review C-1) |
| **BR-34** | **Audit scope is frozen at session start.** Changing a filter mid-session changes what is visible, never what is in scope; rows filtered out of view keep their entered counts and are still committed at Confirm. `[PD-47 · OWNER-PENDING]` | Otherwise an accidental filter click silently drops counted shelves out of the batch — a data-loss path with no error message. | 2026-08-03 |
| **BR-35** | **`SKUs Checked` = rows in the recorded scope + rows added via `[L-13]` during the session.** `[PD-47 · OWNER-PENDING]` — **this extends the register's wording and the owner must be asked for the extension, not just the base rule.** `_provisional-decisions.md` `[PD-47]` currently reads *"'SKUs Checked' = rows in that scope"*; a `[L-13]` addition is by construction **not** in the scope recorded at session start, so this rule produces a different number than the register as written. Reversing it means changing this row, `[E-81]`, §3.11's `SKUs Checked` bullet, and `QA-AUD-40` — and nothing else. | A shelf-found item was checked. Excluding it would understate the walk and make the number un-auditable. | 2026-08-03 |
| **BR-36** | **An audit session belongs to its START date.** A session opened 23:50 and confirmed 00:10 files under the start date in `[L-15]`. | The shelves counted are the start date's work, and `[L-15]` is a one-row-per-session monthly record. | 2026-08-03 |

---

## 5. Data Capture

This section applies `[G-8]`. UI tables on this screen — Stock History `[L-8]`, Past Audit Logs `[L-15]`, ADJUST detail `[L-M2]` / `[L-M2b]`, the Comments hub `[L-16]` — are **views over the events below**, never the only copy. Anything not explicitly declared a NON-event in §5.3 and operator-initiated **must** persist.

Canonical cross-page event names are byte-identical wherever they appear (`_review.md` §3.3). The ones this page uses: `comment.posted` · `comment.mention_notified` · `comment.starred` / `comment.unstarred` · `comment.read` / `comment.mark_all_read` · `product.barcode_registered`. All other names below use lowercase `entity.action` semantics; literal API/endpoint naming is a developer decision.

> **Event-name normalisation (2026-08-03).** The page-local names below were re-written from three dotted segments to the two-segment `entity.action` form required by `_review.md` §3 item 3 (`audit.session.confirmed` → `audit.session_confirmed`, `stock.reserve.released` → `stock.reserve_released`, `comment.search.executed` → `comment.search_executed`, and 17 more of the same shape). **No `[DC-n]` ID changed** — the IDs, not the names, are this document's stable handles, and `_review.md` §3 item 2's "never renumber" is therefore untouched. The rename also brings the hub-search event into byte-agreement with View Orders' `comment.search_executed`. Three cross-page *concepts* still carry per-page names across the corpus (idempotent-duplicate suppression, stock movement, Slack dispatch outcome); resolving those requires promoting one name each into `_global-rules.md`, which is a corpus-level change, not a page delta.

**34 persisted events (`[DC-1]` – `[DC-34]`), 13 declared NON-events (`[NE-1]` – `[NE-13]`).**

### 5.1 UI-surfaced events

These are rendered somewhere in this screen's UI. The UI rendering is a projection; the event is the record.

| ID | Event | Trigger (`[L-n]`) | Actor | Entity | Old → New / payload | Surfaced in |
|---|---|---|---|---|---|---|
| **DC-1** | `stock.inbound_recorded` | `＋ Record Inbound` `[L-F2]` | operator | SKU | total `before → after`; `+qty`; tracking no?; carrier (operator-selected `[BR-33]`); order id?; location (auto-applied, or `Unassigned`); status `CONFIRMED` | Stock History `INBOUND` row; Current Stocks totals |
| **DC-2** | `stock.outbound_recorded` | `－ Record Outbound` `[L-F3]` | operator | SKU | total `before → after`; `−qty`; tracking no?; carrier; order id?; location (auto); status `CONFIRMED` | Stock History `OUTBOUND` row; Current Stocks totals |
| **DC-3** | `stock.reserved` | order allocation (originates off-page) | `System` | SKU + order id | reserved `before → after`; `−qty` from Available; reserved-at timestamp; order status at reservation | Stock History `RESERVE` row; `Reserved` column; `[L-M3]` rows |
| **DC-4** | `stock.reserve_released` | `[L-M4]` step 1 on Confirm | operator | SKU + order id + reservation id | reserved `before → after` (8 → 5); released qty; release reason (`phantom` \| `manual`); order status at release; memo id? | Stock History `RESERVE` release row; `[L-M3]` row disappears |
| **DC-5** | `stock.restocked` | `[L-M4]` restock = **Yes** | operator | SKU | available `before → after` (34 → 37); **both** the default (originally-inbounded) qty **and** the entered qty are captured | Current Stocks `Available`; Stock History |
| **DC-6** | `stock.adjust_loss` | `[L-M4]` restock = **No**, or the auto-remainder of an under-restock | operator | SKU | `ADJUST(−n)`; classification `damaged \| lost`; loss amount ₩; source `m4-writeoff` \| `m4-remainder`; memo id? | Stock History `ADJUST` row |
| **DC-7** | `audit.session_started` | `Start Stock Audit` `[L-7]` | auditor | audit session | session id; start ts; **scope** = the filtered SKU-row set at start (`[PD-47 · OWNER-PENDING]`); scope row count; filter state (search/line/route); sort switched to location-asc | `[L-15]` after confirm |
| **DC-8** | `audit.adjust_confirmed` (one per SKU with `Diff ≠ 0`) | `Confirm — record N ADJUST events` `[L-M1]` | auditor | SKU + session id | `system qty → counted qty`; diff `±n`; loss = diff × product cost; **the cost value actually applied, not just the diff**; location at count time | `[L-M2]` row **and** the same SKU's Stock History `ADJUST` row (one event, two views) |
| **DC-9** | `audit.new_item_added` | `[L-13]` Add, committed at `[L-M1]` Confirm | auditor | SKU + session id | `system 0 → counted n`; location; `NEW ADDITION` flag; loss **excluded** from the session total; counted toward `SKUs Checked` `[BR-35]` | `[L-M2]` purple row; SKU's Stock History `ADJUST(+n)` |
| **DC-10** | `audit.session_confirmed` | `[L-M1]` Confirm | auditor | audit session | audit date (= session **start** date `[BR-36]`); auditor; SKUs checked; adjustments count with ± breakdown; new-additions count; total loss ₩; confirm ts; the acknowledgement flag from `[DC-25]` if the gate fired | `[L-15]` row |
| **DC-11** | `comment.posted` | `[L-M4]` memo (dual-write to the order's Comments) | author | order + SKU | text; ts; `source = m4-memo`; linked release event id | Order Comments history; `[L-16]` hub |
| **DC-12** | `comment.mention_notified` | an `@mention` inside a `[DC-11]` memo, or any comment authored from this page | `System` | comment id | channel `#fulfillment-admin-comments` (`C0BMGEWM5QA`); mentioned user; delivery ts; delivery result (`ok` \| `failed` \| `retrying`) + failure reason (e.g. `unknown_user`) | `[L-16]`; Slack — see §6.1 |

### 5.2 Events persisted without a UI surface on this page

No table on this screen renders these today. They persist anyway `[G-8]`.

| ID | Event | Trigger (`[L-n]`) | Actor | Entity | Old → New / payload | Note |
|---|---|---|---|---|---|---|
| **DC-13** | `location.changed` | `.loc-in` edit `[L-12]` | operator | SKU | `old location → new location` (`new` may be `null` when cleared `[E-76]`); ts | **The largest silent-capture gap on this page.** Nothing in Stock History shows location moves today. Persistence is mandatory; adding a `LOCATION` event type for later surfacing is recommended |
| **DC-14** | `location.assigned` | first assignment on an `Unassigned` row `[L-12]` | operator | SKU | `null → location`; ts | Subtype of DC-13; kept distinct so "never had a location" is queryable |
| **DC-15** | `product.barcode_registered` | `.bcin` commit `[L-12]` | operator | SKU | `null → barcode`; ts | **Canonical cross-page name** — byte-identical with View Orders |
| **DC-16** | `inbound.pending_confirmed` | **not originated here** | operator (other screen) | movement event id | status `PENDING → CONFIRMED`; ts; actor; confirming screen | Rendered on `[L-8]` as a status change; **Inventory never emits it** `[PD-41 · OWNER-PENDING]` `[BR-18]`. Listed so nobody adds an emitter here `[E-89]` |
| **DC-17** | `audit.session_abandoned` | `Exit Stock Audit` without confirming `[L-7]`, or a stale-session sweeper | auditor \| `System` | session id | entered-count snapshot; rows touched; abandon ts; reason `operator-exit` \| `timeout` \| `crash` \| `force-closed` | Draft retention is a dev decision; the abandonment itself is not optional `[E-83]` |
| **DC-18** | `audit.blocked_reserved_shortage` | the `[L-M1]` gate fires | `System` | session id + SKU list | per-SKU `counted` vs `reserved`; affected order ids; block ts | Operational signal for phantom hunting. Persists even if the auditor then exits without acknowledging `[E-84]` |
| **DC-19** | `export.generated` | `⬇ Export Stock Status` / `⬇ Export` `[L-F4]` | operator | export | which export; full filter state; sort; row count; audit-mode flag; ts | *Who took stock data out of the building* |
| **DC-20** | `stock.outbound_rejected` | Outbound qty > Available `[L-F3]` | operator | SKU | attempted qty vs Available at that moment; ts | Repeated rejections on one SKU signal count drift — a leading indicator for the next audit |
| **DC-21** | `search.executed` | `🔍 Search` / Enter on `[L-F1]` | operator | query | key type (`SKU`\|`Product Name`\|`Order ID`\|`Tracking No`\|`Barcode`); term; result count; ts | Doctrine default = capture; low signal, dev may sample (§9.2) |
| **DC-22** | `comment.starred` / `comment.unstarred` | `★` in `[L-16]` | user | comment id | per-user saved state `on → off`; ts | Canonical names |
| **DC-23** | `comment.read` / `comment.mark_all_read` | opening a mention / `Mark all read` `[L-16]` | user | comment id(s) | per-user read state; ts | The unread badge derives from this |
| **DC-24** | `audit.count_entered` | committing a `.qty-in` value `[L-7]` | auditor | SKU + session id | `previous entered value → new value` (first commit records `prefill → entered`); ts | Draft/autosave record; at minimum the final pre-confirm snapshot must exist so a crashed session is reconstructable `[E-58]`. Also the only way to distinguish an untouched prefilled row from a counted-and-matching one `[E-12]` |
| **DC-25** | `audit.shortage_acknowledged` | ticking `Reviewed with the order team` in `[L-M1]` | auditor | session id | acknowledged SKU list; ts | `[PD-48 · OWNER-PENDING]` — this is the accountability record the gate exists to produce |
| **DC-26** | `audit.no_catalog_match` | `[L-13]` autocomplete returns `No match — register manually via Unrecognized flow (F)` | auditor | session id | search term; ts; whether the operator followed the handoff link | "A physical item existed that our catalog does not know" must never be lost just because the screen dead-ends |
| **DC-27** | `stock.inbound_rejected` | `[L-F2]` validation failure (unknown SKU, bad qty, unknown order id) | operator | SKU? | attempted payload; rejection reason; ts | Mirror of DC-20 |
| **DC-28** | `location.assign_blocked` | assigning an occupied location `[L-12]` / `[L-13]` | operator | SKU + attempted location | attempted location; occupying SKU; ts | `[PD-46 · OWNER-PENDING]` — collision frequency is the evidence for or against the 1:1 rule |
| **DC-29** | `product.barcode_register_rejected` | barcode already registered to another SKU `[L-12]` | operator | SKU + attempted barcode | attempted barcode; owning SKU; ts | |
| **DC-30** | `inventory.reserved_orders_opened` | `.reslink` click `[L-6]` / wf-bar shortcut | operator | SKU | reserved qty at open; phantom-flagged order ids; ts | Read event. Makes a later release traceable to the investigation that preceded it. Dev may sample (§9.2) |
| **DC-31** | `stock.reserve_release_blocked` | stale or concurrent release rejected at `[L-M4]` Confirm | operator | reservation id | rejection reason (`already_released` \| `stale_order_state` \| `version_conflict`); competing actor if known; ts | Concurrency forensics `[PD-6 · OWNER-PENDING]` `[PD-7 · OWNER-PENDING]` |
| **DC-32** | `audit.session_blocked_concurrent` | second `Start Stock Audit` while a session is active `[L-7]` | operator | warehouse + active session id | blocked actor; active session id + auditor; ts | `[PD-44 · OWNER-PENDING]` — evidence for or against the single-session rule |
| **DC-33** | `comment.search_executed` | typing in the `[L-16]` search box | user | query | term; result count; ts | Parallel to DC-21; dev may sample |
| **DC-34** | `audit.scope_changed` | a Current Stocks filter is changed while a session is open `[L-5]` `[L-7]` | auditor | session id | previous filter state → new filter state; count of scope rows now hidden from view; count of hidden rows carrying entered counts; ts | `[BR-34]` `[E-66]`. Scope itself does **not** change — this records that the auditor's *view* diverged from the batch, which is the precondition for a "why was that shelf adjusted?" question later |

### 5.3 Declared NON-events

Ephemeral, client-local state, declared per `[G-8]`. A developer who persists these is not wrong about the doctrine but is adding noise the owner did not ask for. Anything **not** on this list and operator-initiated must persist.

| ID | Non-event | Why |
|---|---|---|
| `[NE-1]` | Sub-tab switching (Current Stocks / Stock History / Inbound Stock / Outbound Stock) | Navigation, not intent |
| `[NE-2]` | wf-bar demo-chrome clicks, including the `Hide annotations` toggle | Wireframe chrome; does not ship |
| `[NE-3]` | Filter selection (search box, line filter, route filter) and column-header sorting on Current Stocks | Client-local view state. Captured where it matters: as `[DC-19]` export scope, `[DC-7]` audit scope, and `[DC-34]` mid-session divergence |
| `[NE-4]` | Stock History filter-chip selection (`All` / `Confirmed` / `Pending confirm`) | Same reason |
| `[NE-5]` | Pagination page changes `[L-9]` | Same reason |
| `[NE-6]` | Opening or cancelling `[L-M1]` without confirming | The session is still open and nothing changed. Confirming persists `[DC-8]`–`[DC-10]`; exiting persists `[DC-17]` |
| `[NE-7]` | Opening or cancelling `[L-M4]` without confirming | Nothing was released |
| `[NE-8]` | Opening `[L-M2]` / `[L-M2b]` / `[L-15]` | Read-only history views. (Contrast `[DC-30]`: `[L-M3]` **is** captured because it precedes a destructive action) |
| `[NE-9]` | Typing in `#auSearch` before a selection is made, and dropdown navigation | Only the `No match` outcome `[DC-26]` and the committed Add `[DC-9]` matter |
| `[NE-10]` | Committing a `.loc-in` or `.bcin` value identical to the stored one | Nothing changed; no toast, no event |
| `[NE-11]` | `[L-16]` tab switching between `@ Mentions` and `★ Saved` | Client-local |
| `[NE-12]` | Audit-mode toggle *rendering* effects (column show/hide, re-sort, `.audrow` visibility) | Presentation of `[DC-7]` / `[DC-17]`, not separate facts |
| `[NE-13]` | Global-nav clicks `[L-F5]` — the brand wordmark, the six category dropdown labels, the four `.navlink` tiles, and navigating away from Inventory through any of them | Navigation, not intent. (`Logout` is **not** on this list because it is not this page's event at all: the platform auth layer owns the session record — §3.21) |

### 5.4 Retention and export

- **`[DC-1]` – `[DC-10]` are retained indefinitely.** They are the movement ledger and the audit trail, and they are the corpus the comment/audit doctrine `[G-7]` `[G-8]` exists to build.
- **Monthly audit sessions are never pruned.** The wireframe deliberately shows May, June, and July 2026 side by side because the loss trend only means something across months.
- **Silent events `[DC-13]` – `[DC-34]` are retained on the same horizon as the movement ledger.** `[DC-21]`, `[DC-30]`, and `[DC-33]` are the only events a developer may sample rather than capture in full, and sampling must be a documented configuration, not an omission.
- **Live-list retention horizon** (how many events the UI holds before paging to cold storage) is a developer decision (§9.2).
- **Exports** reproduce the scope stated in `[L-F4]`. All events are exportable to BI on request; the export action itself is captured `[DC-19]`.
- **No event on this page is ever hard-deleted.** There is no delete affordance anywhere on this screen — not for movements, not for audit sessions, not for comments `[BR-23]` `[BR-24]`.

---

## 6. Integrations

### 6.1 Slack routing

Channels are CONFIRMED 2026-08-03 per `_slack-routing.md`. Payload fields are verbatim from that file.

| Trigger on this page | Channel | Payload | Mention target |
|---|---|---|---|
| Comment `@mention` — posted from the `[L-16]` Comments hub, or contained in an `[L-M4]` memo, or on any Inventory-context comment | **`#fulfillment-admin-comments`** (`C0BMGEWM5QA`) | entity no., comment text, time, author, @mentioned user, deep link | the @mentioned user, per `[G-7]` |

**Rules.**

- This is the **only** confirmed Slack route originating from Inventory.
- An `[L-M4]` memo **without** an `@mention` produces **no** Slack message. It is written to the order's Comments history only (`[DC-11]`).
- Delivery failures are persisted (`[DC-12]` with `result = failed`) and retried. **A failed notification never blocks the release, the audit confirm, or any other primary action, and never rolls anything back** `[PD-4 · OWNER-PENDING]` `[E-65]`. An `@mention` naming someone who is not in the workspace resolves to `result = failed`, reason `unknown_user`; the comment still posts `[E-88]`. Retry policy is a developer decision.

**Explicit non-routes (stated so nobody wires them by analogy):**

- **`#unrecognized-tracking` is never posted to from this page.** The `[L-13]` no-match path *navigates the operator* to the Unrecognized Tracking screen; the registration — and its Slack send — happen there, under that page's spec. Inventory records only the handoff (`[DC-26]`).
- **`#wholesale-ops` / `#partnership-kr`** carry the morning no-tracking check for inbound requests. Neither is triggered by anything on this page.
- **Audit confirmation sends no Slack message in v1**, and neither does an unresolved Reserved-shortage gate. Inventing a channel would create an unowned alert stream; the routing table's "future routes: decide per feature at dev time" row stays unused here. Listed in §9.2, not specified.

### 6.2 Cross-page links and deep links `[G-12]`

| From | To | Behavior |
|---|---|---|
| `[L-M3]` `Order ID` (e.g. `407812`, `413650`, `409112`) | Order Detail | Opens that order. Rendered blue and bold |
| `[L-M3]` note → `Pending confirm filter` | This page, Stock History pane | Switches pane and activates the `Pending confirm` chip, scoped to the SKU in context |
| `[L-13]` `No match — register manually via Unrecognized flow (F)` | `../tracking-missing/` (Unrecognized Tracking) | Opens the Unrecognized registration flow. The matching behavior itself is specified on `tracking-missing` / `view-orders`, not here |
| `[L-16]` comment entry | The referenced entity (order, inbound request, or unrecognized-pool item) | Pool-item entries open the tracking-missing row; already-resolved pool items open the matched order instead `[PD-67 · OWNER-PENDING]` |
| `[L-8]` `PENDING` rows | `view-orders` State 6 / `inbound-request` | **Inbound direction only** — the events *originate* there `[G-10]` `[G-11]`. This page renders and filters them and offers no confirm affordance `[BR-18]` |
| `[L-F1]` `Sourcing Route` value | Inbound Request | The route is *assigned* at the Inbound Request origin form `[G-5]`; Inventory is a consumer, including of the `OTHER (channel)` free text `[PD-80 · OWNER-PENDING]` |

### 6.3 Sheet / BI handoffs

- **No live sheet handoff is specified for this page.** Both Export buttons produce files the operator downloads `[L-F4]`.
- **Procurement Hub is excluded from this program entirely** (owner decision 2026-08-02: no sweep, no English conversion, no spec). The one place it touches Inventory is a **read dependency**: FIFO lot cost is the recommended source for the audit `Loss (₩)` calculation `[BR-4]` `[OQ-1]`. That is a costing lookup, not an integration this spec defines.
- All persisted events are exportable to BI on request `[G-8]`; the export action itself is captured `[DC-19]`.

### 6.4 Print pipeline

**`[G-4]` does not land on this page.** There is no Print button on Inventory and none may be added `[BR-27]`. The two Export buttons are file downloads, not print surfaces. No local print agent, no `print.job_result` event, and no printer-offline error state is in scope here — see `[E-98]` for the negative assertion and §9.1 #5 for the must-NOT-exist entry.

### 6.5 Audio

- `－ Record Outbound` `[L-F3]` is an outbound-class button and therefore carries the `[G-3](a)` send sound `[PD-2 · OWNER-PENDING]`.
- `＋ Record Inbound` does **not**.
- There is **no TTS on this page** — `[G-3](b)` is Closing-only — and no warning tone — `[G-3](c)` is a View Orders State 6 page delta.
- Synth parameters and `AudioContext` resume handling are developer decisions (§9.2).

---

## 7. Edge Cases & Error States

IDs are page-scoped and stable. `[E-1]` – `[E-50]` are carried unchanged from the Lens-B plan; `[E-51]` – `[E-65]` were added at consolidation; `[E-66]` – `[E-98]` were added at audit. **98 edge cases total. Never renumber.**

Every entry states the **expected behavior**, not just the failure. An entry with no stated behavior is a defect in this spec.

### 7.1 Current Stocks — list, filters, sort, rendering

| ID | Case | Expected behavior |
|---|---|---|
| `[E-1]` | **Empty inventory** — no SKUs registered at all | Table renders an empty state `No stock records yet`. `Start Stock Audit` is disabled with tooltip `Nothing to audit`. Both Export buttons remain enabled and produce a headers-only file |
| `[E-2]` | **Filter/search yields zero rows** | Empty state `No products match these filters` + a `Clear filters` action. `Start Stock Audit` is **disabled** while the visible scope is empty (an audit whose scope is the empty set is meaningless) `[PD-47 · OWNER-PENDING]` |
| `[E-3]` | **Unassigned-location rows** | Listed, never hidden. The Location filter gets an explicit `Unassigned` bucket (not excluded, not folded into a line). In the audit walking sort they sort **last** (the wireframe uses the `힣` sentinel) `[BR-11]` |
| `[E-4]` | **Barcode-less product** | `Barcode` cell renders a dashed `.bcin` input with placeholder `Enter barcode`. Committing persists `[DC-15]`. A barcode already owned by another SKU is rejected: `Barcode {value} already belongs to SKU {sku}`, persists `[DC-29]`, nothing saved |
| `[E-5]` | **Location edited to an invalid format** (free text, lowercase, wrong pattern) | Inline error `Invalid location code`, input keeps focus, **no save**, no event. Regex is a dev decision |
| `[E-6]` | **Location already used by another SKU** | **Blocked** — `Location {code} is already assigned to SKU {sku}`. 1:1 exclusivity `[PD-46 · OWNER-PENDING]`. Persists `[DC-28]` |
| `[E-7]` | **Two operators edit the same SKU's location concurrently** | Optimistic version check → 409 → the row reloads with a non-green toast `Location was changed by {actor} — reloaded`. Both attempts remain in the audit trail; no last-write-wins overwrite `[PD-7 · OWNER-PENDING]` |
| `[E-8]` | **Network failure mid location-save** | Input reverts to the server value, red toast `Could not save location — check your connection`. UI and server must never diverge silently. Retry is idempotent `[G-9]` |
| `[E-9]` | **Custom sort → audit start → audit exit** | Audit forces location-asc. Exit restores **Available descending** (the default), not the operator's pre-audit custom sort `[BR-10]` |
| `[E-10]` | **Location edited to a brand-new line** (first `D-…` code) | The Location filter's option list re-derives immediately and now contains `Line D`, without a page reload `[G-14]` `[BR-6]` |
| `[E-51]` | **wf-bar modal shortcut used while audit mode is active** | The modal opens; the Current Stocks pane, the audit columns, and every entered count remain exactly as they were (2026-08-03 behavior). Closing the modal returns to the same state |
| `[E-52]` | **Sub-tab switched away and back during an open audit** | The audit session stays open server-side. Returning to Current Stocks restores audit mode, the location-asc sort, and all entered counts. If counts are held client-side only, leaving the pane must not drop them; if that cannot be guaranteed, the sub-tab switch requires the same confirm as `[E-21]` |
| `[E-53]` | **Route filter `JIT` and channel-suffixed labels** | Selecting `JIT` returns the `JIT (Coupang)` row. Matching is on the base route, never on the rendered label string. Same rule for `OTHER (channel)` `[BR-7]` `[BR-8]` |
| `[E-54]` | **Export while audit mode is on** | The three audit columns are included by default and the session id is carried in the filename. Persists `[DC-19]` with `audit-mode = true`. Final column policy is a dev decision (§9.2) |
| `[E-55]` | **The last location on a line is removed or reassigned** | `Line X` disappears from the Location filter option list on the next derivation. If it was the active filter, the filter resets to `All Locations` with a non-green toast rather than silently showing zero rows |
| `[E-62]` | **Data-integrity: `Available` negative, or `Reserved > Total`** | The value renders in red with a warning marker and the row is excluded from `Start Stock Audit` prefill (the `Counted Qty` box starts blank for that row). An integrity banner names the affected SKUs. Never silently render a nonsense number as if it were a count |
| `[E-64]` | **Location code whose line segment is multi-character or lowercase** (`AA-01-02`, `b-01-01`) | The derivation rule and the validation regex must agree. Codes that pass validation must produce a line; codes that cannot be parsed into a line are rejected at `[E-5]`, never silently bucketed into `Unassigned` |
| `[E-67]` | **The same SKU appears twice in the current-stock projection** (upstream data fault) | Both rows render, an integrity banner names the SKU, and `Start Stock Audit` is blocked with `Duplicate SKU rows detected — resolve before auditing`. Counting one of two rows would produce an ADJUST against an ambiguous quantity |
| `[E-68]` | **Product with no image and/or no Korean name** | `Image` renders the `IMG` placeholder box (never an empty cell, never a broken-image glyph). `Product Name KR` renders `—` — never the English name duplicated into the KR column, which would corrupt the picker's Korean lookup `[G-6]` |
| `[E-69]` | **Very long product name or location code** | The cell truncates with an ellipsis and exposes the full value on hover/`title`. Truncation never changes the value sent on save, and the `Location` input still accepts and submits the full code |
| `[E-70]` | **Narrow viewport / horizontal scroll** | The table container scrolls horizontally (the wireframe's mock is `min-width: 1140px` inside `overflow-x: auto`); the page body itself must never scroll horizontally. The sticky table header stays pinned while scrolling vertically. No column is dropped responsively — a hidden `Available` column is a wrong decision at a glance |
| `[E-71]` | **Timestamp rendering** | KST, `YYYY-MM-DD HH:MM` in list columns and `HH:MM:SS` in audit-session detail `[BR-32]`. The wireframe's compact `MM-DD HH:MM` fixture is a width artifact, not the contract. No relative times anywhere |
| `[E-72]` | **Money rendering** | `₩` with thousands separators and an explicit sign for non-zero values (`+₩61,260`, `−₩15,000`, `₩0`, `— (신규)`) `[BR-31]`. No `$`, no `USD`, no locale-switched currency |
| `[E-76]` | **A location is cleared to empty** (deliberate un-assignment) | **Allowed.** The row returns to the `Unassigned` bucket and to the end of the audit walking sort `[E-3]`. Green toast `Location cleared — {SKU} {old} → Unassigned`; `[DC-13]` persists with `new = null`. The freed location becomes assignable to another SKU under the 1:1 rule `[E-6]`. Clearing is never silently treated as "no change" |
| `[E-97]` | **A user tries to drill into `Reserved` from the Current Stocks table** | There is no drill-down there — `Reserved` is plain text on that table. The reservation drill-down `[L-6]` exists only on the Stock History `📊 Stock Status` card. Adding a second entry point would require a second phantom predicate and a second read event `[DC-30]`; do not add one |

### 7.2 Stock Audit mode

| ID | Case | Expected behavior |
|---|---|---|
| `[E-11]` | **Audit started while filters are active** | Allowed. The session records the filtered scope `[PD-47 · OWNER-PENDING]`. `[L-15]` must therefore never be read as "the whole catalog was counted" |
| `[E-12]` | **Untouched `Counted Qty` rows** (prefilled, never visited) | Indistinguishable from counted-and-matching *in the UI* by design `[PD-40 · OWNER-PENDING]`. `[DC-24]` records the first commit as `prefill → entered`, so a never-committed row **is** distinguishable in the data. Reporting on "rows actually touched" reads `[DC-24]`, never the diff |
| `[E-13]` | **`Counted Qty` non-numeric, negative, or blank** | Rejected inline (`Enter a whole number of 0 or more`); `Diff` is not computed; the row is treated as not counted and is excluded from `[L-M1]` |
| `[E-14]` | **`Counted Qty < Reserved`** | The Reserved-shortage gate fires: affected orders are listed inside `[L-M1]`, Confirm is disabled, `[DC-18]` persists. The acknowledgement checkbox `Reviewed with the order team` unlocks Confirm and persists `[DC-25]` `[PD-48 · OWNER-PENDING]` |
| `[E-15]` | **Unregistered product with no autocomplete match** | Dropdown renders exactly `No match — register manually via Unrecognized flow (F)`, which is a link to `../tracking-missing/`. `Add` stays disabled. Persists `[DC-26]` |
| `[E-16]` | **`Add` clicked with free-typed text and no selection** | Nothing is added; focus returns to `#auSearch`; no error toast (the operator simply has not finished). In production `Add` is disabled until a selection exists; the shipped wireframe leaves it enabled and no-ops — see §3.9 |
| `[E-17]` | **`Add` with blank Qty or blank Location** | Qty defaults to `1`, Location defaults to `Unassigned`. Both defaults are intended and must be preserved |
| `[E-18]` | **The same product added twice, or added while already visible in the list** | Blocked with the inline notice `Already in this audit — edit the Counted Qty on the existing row` |
| `[E-19]` | **`Confirm — record N ADJUST events` double-clicked** | Exactly one session close, one ADJUST batch. Client debounce + server idempotency key `[G-9]` |
| `[E-20]` | **Network failure mid audit-commit** | Atomic: either every ADJUST event **and** the session row exist, or none do. A partial ADJUST set, or a session row without events, is a defect. Red toast `Audit not recorded — nothing was changed. Try again`, modal stays open with counts intact |
| `[E-21]` | **`Exit Stock Audit` with unsaved counts** | Confirm dialog `Exit stock audit?` / `{n} entered count(s) will be discarded. The session will be recorded as abandoned.` / `Keep counting` \| `Exit and discard`. On discard, `[DC-17]` persists with the count snapshot `[PD-5 · OWNER-PENDING]` |
| `[E-22]` | **Stock moves during the audit** (an outbound is confirmed after a count was entered) | System quantities are **re-read at confirm**. `Diff` is recomputed against the current system quantity, `[L-M1]` re-renders, and a non-green toast `Stock changed during the audit — differences recalculated` appears **before** Confirm can proceed `[PD-6 · OWNER-PENDING]` |
| `[E-23]` | **Two auditors start an audit simultaneously** | The second is blocked: `Stock audit already in progress — started {HH:MM} by {auditor}`. Exactly one active session per warehouse `[PD-44 · OWNER-PENDING]`. Persists `[DC-32]` |
| `[E-24]` | **Audit with zero differences** | Confirm is allowed. The session is recorded with 0 adjustments and 0 new additions, and appears in `[L-15]` with `₩0 · target met` and `—` in the Detail column (no ADJUST modal exists). Precedent: the 2026-05-31 session |
| `[E-25]` | **SKU has no product cost** | `Loss (₩)` renders `—`; the SKU still produces an `ADJUST` event with its diff; it is **excluded from the total-loss arithmetic**, and `[L-M1]`'s total note states the exclusion. New additions always render `— (신규)` |
| `[E-60]` | **A SKU created system-wide after the session started** | It is **outside the recorded scope** and does not appear in the audit list mid-session, does not affect `SKUs Checked`, and is not silently adjusted. It is picked up by the next session |
| `[E-61]` | **Product cost changes between count entry and confirm** | The cost **at confirm time** is used, and the cost value actually applied is stored on `[DC-8]` so the loss figure is reproducible later even if the cost changes again |
| `[E-66]` | **A Location or Route filter is changed while the audit session is open** | Scope does **not** change `[BR-34]`. Rows filtered out of view keep their entered counts and are still committed at Confirm. A persistent warning chip renders above the table: `{n} counted row(s) hidden by the current filter`. `[DC-34]` persists the divergence. Clearing the filter restores the full walk with counts intact |
| `[E-77]` | **`#auQty` is `0`, negative, or non-numeric on Add** | Rejected inline (`Enter a whole number of 1 or more`), no row inserted, focus stays in `#auQty`. Blank is a different case and defaults to `1` `[E-17]` |
| `[E-78]` | **`#auLoc` names a location already occupied by another SKU** | The Add is **blocked** with the same message as `[E-6]` (`Location {code} is already assigned to SKU {sku}`); no row is inserted; `[DC-28]` persists `[PD-46 · OWNER-PENDING]` |
| `[E-79]` | **A session whose only non-zero rows are `[L-13]` new additions** | Confirm is allowed. `{N}` in the button counts the new additions; total loss is `₩0` because new additions are excluded `[BR-4]`; `[L-15]` shows `Adjustments 0`, `New Additions N`, `Total Loss ₩0 · target met` |
| `[E-80]` | **A session spanning midnight** (started 23:50, confirmed 00:10) | The session and its `[L-15]` row belong to the **start** date `[BR-36]`. The confirm timestamp is recorded separately on `[DC-10]` and is what `[L-M2]` renders |
| `[E-81]` | **`SKUs Checked` when rows were added via `[L-13]`** | `SKUs Checked` = recorded scope rows + rows added during the session `[BR-35]` `[PD-47 · OWNER-PENDING]` (this **extends** the register's PD-47 wording — see `[BR-35]`). The `[L-15]` fixture numbers are illustrative and must not be reverse-engineered into a different formula |
| `[E-82]` | **A scope row is deleted or merged system-wide mid-session** | It is dropped from the batch, named in the recalculation toast (`{n} row(s) no longer exist and were removed from this audit`), and never adjusted against a dead SKU. The session still confirms |
| `[E-83]` | **The session is force-closed** by an administrator or a stale-session sweeper | `[DC-17]` persists with reason `force-closed` or `timeout`. The lock is released so the next `Start Stock Audit` succeeds. An orphan session that blocks all future audits is a defect `[E-58]` |
| `[E-84]` | **The shortage gate fires, then the auditor exits without acknowledging** | `[DC-18]` persists (the shortage was detected) and `[DC-17]` persists (the session was abandoned). `[DC-25]` must **not** exist — an unacknowledged shortage must never look acknowledged |
| `[E-90]` | **An inbound or outbound is recorded for a SKU inside an open session's scope** | Not blocked. The movement commits normally; the audit's stale system quantity is recomputed at Confirm `[E-22]`. Blocking warehouse movement for the duration of a walk is an operational stop-the-line risk |

### 7.3 Reserved modal `[L-M3]` and Cancel Inbound `[L-M4]`

| ID | Case | Expected behavior |
|---|---|---|
| `[E-26]` | **`Reserved Qty = 0`** | The number is plain text, not a link — no pointer cursor, no modal. An empty modal is not an acceptable alternative |
| `[E-27]` | **Sum of modal rows ≠ header Reserved count** | A red data-integrity banner renders inside the modal naming both numbers (`Header 8 · rows total 5 — reservation data is inconsistent`). The rows still render; `Cancel Inbound` stays available so the operator can clean up |
| `[E-28]` | **Partially refunded order holding a reservation** | Phantom-flagged **only** if the reservation exceeds the still-live line quantity. A reservation matching the un-refunded remainder is legitimate and must not be flagged `[BR-19]` |
| `[E-29]` | **`Cancel Inbound` on an ACTIVE (`processing`) order** | Allowed, with an extra confirmation naming the order: `Order {id} is still processing — release anyway?` `[PD-45 · OWNER-PENDING]` |
| `[E-30]` | **Restock Qty edited above the reserved/inbounded qty** | **Blocked** — `Restock qty cannot exceed the inbounded qty ({n})`. Restocking more than was taken creates phantom stock `[PD-50 · OWNER-PENDING]` |
| `[E-31]` | **Restock Qty edited below the released qty** | **Allowed.** The remainder is auto-recorded as `ADJUST(−remainder)` carrying the same memo. Both `[DC-5]` and `[DC-6]` persist `[PD-49 · OWNER-PENDING]` |
| `[E-32]` | **`Confirm` double-clicked in `[L-M4]`** | Exactly one release and one adjustment. The second click no-ops with feedback rather than silently succeeding `[G-9]` |
| `[E-33]` | **Network failure between release and restock** | One atomic composite event. A "released but not restocked" limbo state is a defect. Red toast, nothing committed, modal stays open |
| `[E-34]` | **Two operators release the same reservation concurrently** | The second gets `Reservation already released`; counts are **not** double-adjusted; `[L-M3]` re-fetches. Persists `[DC-31]` |
| `[E-35]` | **Order state changes while `[L-M3]` is open** (outbounded, un-cancelled) | The stale row's action fails safe on confirm with `Order state changed — reloading` and the modal re-fetches. No partial write `[PD-6 · OWNER-PENDING]` |
| `[E-36]` | **Memo written in `[L-M4]`** | Appears in the order's Comments history (`[DC-11]`, `source = m4-memo`). A memo containing an `@mention` additionally routes to `#fulfillment-admin-comments` (`[DC-12]`) `[G-7]` |
| `[E-59]` | **`[L-M4]` opened via the wf-bar shortcut with no row context** | Wireframe-only artifact (the shortcut opens the modal with the Order 409112 fixture). In the real admin the modal is unreachable without a reservation context; QA tags any wf-bar-opened `[L-M4]` assertion as wireframe-scoped and never files it as a product bug |
| `[E-85]` | **Restock Qty set to `0` while `Yes` is selected** | **Blocked** — `Choose "No" to write the whole quantity off`. A zero-quantity restock is a mislabelled write-off and would produce a `[DC-5]` event with no effect |
| `[E-86]` | **The reservation's order record is unreadable or hard-deleted** | The row renders `Order unavailable` in place of the deep link and **still exposes `Cancel Inbound`** — the stock must remain recoverable. `[DC-4]` records the dangling order id verbatim |
| `[E-87]` | **`[L-M3]` header Reserved exceeds the SKU's `Total`** | Red integrity banner inside the modal, companion to `[E-62]` on the list side. Rows still render; release remains possible so the operator can correct the count downward |
| `[E-88]` | **`@mention` of a user who is not in the Slack workspace** | The comment still posts (`[DC-11]`). `[DC-12]` records `result = failed`, reason `unknown_user`. No block, no rollback, no silent drop `[PD-4 · OWNER-PENDING]` |

### 7.4 Stock History tab

| ID | Case | Expected behavior |
|---|---|---|
| `[E-37]` | **Search for an unknown SKU / a SKU with no events** | All three result cards render an explicit empty state; the events table renders `No stock events for this product`; no stale card content from the previous search |
| `[E-38]` | **Each search key type** | `SKU` / `Order ID` / `Tracking No` / `Barcode` match exactly; `Product Name` matches partially and case-insensitively across EN and KR names. The input placeholder switches with the key |
| `[E-39]` | **A `PENDING` event is displayed** | Row is amber (`tr.pending`); the `Pending confirm` chip isolates it. **There is no confirm affordance on this page and QA asserts its absence** `[BR-18]` `[PD-41 · OWNER-PENDING]` |
| `[E-40]` | **Pagination boundaries** | Exactly one page → controls render **disabled**, not hidden. Last page → next/last disabled. Any filter or search change resets to page 1. A new event appended while a page is open does not reshuffle the visible page mid-view |
| `[E-63]` | **A `Tracking No` search matching both an inbound and an outbound movement** | Both are returned and each is labelled by movement type. Inbound and outbound tracking numbers are separate namespaces and may legitimately coincide `[PD-8 · OWNER-PENDING]` |
| `[E-75]` | **A `Barcode` search matching more than one catalogue product** (pre-existing duplicate data) | All matches are returned with SKU and size for disambiguation; the page never silently picks one. Registering a *new* duplicate remains blocked `[E-4]` |
| `[E-89]` | **A `PENDING` event is confirmed on another screen while this page is open** | On the next fetch the row's badge flips to `CONFIRMED` and the amber highlight clears. `[DC-16]` is rendered, never emitted here. No confirm affordance appears at any point `[BR-18]` |

### 7.5 Inbound / Outbound forms

| ID | Case | Expected behavior |
|---|---|---|
| `[E-41]` | **Unknown SKU** | Rejected **before** any server write: `Unknown SKU — {value}`. Persists `[DC-27]` |
| `[E-42]` | **Qty 0, negative, or non-numeric** | Blocked with inline validation `Quantity must be a positive whole number`. No event |
| `[E-43]` | **Inbound for a SKU with no registered location** | Accepted. The row lands `Unassigned` and the toast prompts assignment: `Inbound recorded — {SKU} +{n} · location unassigned, please assign it`. The `[PD-13 · OWNER-PENDING]` mandatory-location gate belongs to View Orders State 6, not to this manual form |
| `[E-44]` | **Outbound qty > Available** | Blocked before write: `Outbound blocked — exceeds Available Qty ({available})`. No `OUTBOUND` event. Totals unchanged. Persists `[DC-20]` |
| `[E-45]` | **Outbound checked against `Total` instead of `Available`** | Defect. With `Total 42 / Reserved 8 / Available 34`, a quantity of `35` must be rejected. Negative test |
| `[E-46]` | **Double-submit on either form** | Exactly one movement event `[G-9]` |
| `[E-47]` | **Network failure on form submit** | No phantom movement. Red toast. Retry is idempotent |
| `[E-48]` | **`Order ID` that does not exist** | Rejected before write (link integrity): `Order {id} not found` |
| `[E-49]` | **`Tracking No` duplicating an existing movement** | Non-blocking warning `Tracking {no} already recorded on {date} — record anyway?` with explicit confirm. Legitimate duplicates exist (combined boxes) |
| `[E-73]` | **A barcode is scanned into a `.loc-in` field** (wrong field, scanner in hand) | The value fails the location pattern and is rejected exactly like any other malformed code `[E-5]`. Nothing is saved, focus is retained, and the operator can retype. Never coerce a numeric string into a location |
| `[E-74]` | **Barcode value with leading/trailing whitespace or scanner control characters** (`\r`, `\n`, `\t`) | Trimmed before validation and before storage. `  8809738317481\r` and `8809738317481` are the same value and must not create two barcode records |
| `[E-91]` | **Outbound submitted for a SKU whose `Available` is already `0`** | Blocked for every quantity ≥ 1, with `{available}` rendered as `0`: `Outbound blocked — exceeds Available Qty (0)`. Persists `[DC-20]` |

### 7.6 Comments hub, export, and cross-cutting

| ID | Case | Expected behavior |
|---|---|---|
| `[E-50]` | **Comment search with no matches** | `No matching comments` empty state. Clearing the query restores the tab bar and the previously active pane. `Mark all read` decrements the unread badge to `0`. Star/unstar keeps `@ Mentions` and `★ Saved` in sync |
| `[E-56]` | **A hub entry whose entity is an unrecognized-pool item** | Click opens the tracking-missing page focused on that pool row; if the item is already resolved, it opens the matched order instead `[PD-67 · OWNER-PENDING]` |
| `[E-57]` | **Session expiry or permission revoked mid-modal / mid-audit** | The pending action fails safe with a red toast and a re-auth prompt. **No partial write.** An open audit session is not confirmed and is not abandoned by the expiry alone; it remains recoverable by the same auditor `[BR-28]` |
| `[E-58]` | **Browser refresh, tab close, or crash mid-audit** | Client-held counts are lost. The session remains open server-side and is recoverable from `[DC-24]` draft records where draft autosave is implemented; otherwise re-entry shows an empty (prefilled) walk and the previous session must be explicitly abandoned or resumed. Never leave an orphan session that blocks all future audits `[E-23]` `[E-83]` |
| `[E-65]` | **Slack delivery fails for a comment posted from this page** | The comment is committed and visible; `[DC-12]` records `result = failed`; retry runs in the background; the UI never rolls back and never blocks `[PD-4 · OWNER-PENDING]` |
| `[E-92]` | **Export clicked repeatedly, or a very large export** | Each click produces exactly one job and exactly one `[DC-19]` `[G-9]`. A long-running export runs asynchronously behind a non-green `Preparing export…` toast and delivers the file when ready. The page never refreshes `[G-2]` |
| `[E-93]` | **Comments hub with zero unread mentions** | The nav badge is **hidden**, not rendered as `0`. The `@ Mentions` pane renders an explicit empty state |
| `[E-94]` | **Comment search term containing markup characters** (`<b>`, `&`, `"`) | The term and every rendered result are HTML-escaped; markup is never interpreted. The `<mark>` highlight wraps the escaped substring, never raw input (the wireframe's `esc()` helper encodes this intent) |
| `[E-95]` | **Comment search term in Korean** | Matches Korean comment text. No normalization or case-folding that decomposes Hangul and breaks the match |
| `[E-96]` | **Another operator commits an audit or a movement while this page is open** | The viewer's totals update within the sync interval; no silent stale display beyond it. Transport (poll vs push) and latency are developer decisions (§9.2). A stale value must never be the basis of a write — the server revalidates at confirm `[PD-6 · OWNER-PENDING]` |
| `[E-98]` | **A print attempt** (browser `Ctrl+P`, or a developer adding a Print button) | There is no print pipeline on this page. No `print.job_result` event is emitted, no print agent is contacted, and no Print affordance exists `[G-4]` `[BR-27]` §9.1 #5. Browser-native printing of the page is not a supported artifact and is not styled for |

**Cross-cutting negative frame applied to every confirming action on this page:** a missing toast is a test failure `[G-2]`; a page refresh after any action is a test failure `[G-2]`; a double-click producing two effects is a test failure `[G-9]`; a mutating action with no recorded actor is a test failure `[G-8]` `[G-15]`; a rejection that persists no event is a test failure `[BR-26]`.

---

## 8. QA Acceptance Criteria (machine-runnable)

### 8.0 How to run this section

**Tiers.**

- **[WF]** — executable **today** against the live wireframe (https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/stock-status/) using the exact selectors, labels, and strings given. A [WF] failure is a real defect in the wireframe or in this spec, and must be reported.
- **[ADMIN]** — requires the real admin (server effects, toasts, sounds, persistence, idempotency, working filters/sort/pagination/Export). These are deferred rows the agent runs after implementation. Running an [ADMIN] scenario against the wireframe and reporting a failure is itself an error.

**Mandatory preflight — perform before every [WF] scenario.**

1. Load the live URL and wait until `document.querySelector('#p-current').classList.contains('on')` is true.
2. **Click the wf-bar button labelled `Hide annotations`** (`#annoToggle`). Assert `document.body.classList.contains('no-anno')` and that the button now reads `Show annotations`. This hides `.dot` and `.legend`.
3. **Use `innerText`, never `textContent`, for text assertions** — or strip `span.dot` descendants first. Three annotation dots are rendered *inside* content nodes (`12` in the `Location` `<th>`, `11` in the `Available` `<th>`, `13` in the `.audrow` `<td>`); `display:none` removes them from `innerText` but **not** from `textContent`. See §2.4. Ignoring this makes `QA-CS-14`, `QA-LOC-01`, and `QA-AUD-14` fail spuriously.
3b. **Normalise before comparing.** `innerText` is layout-sensitive, so every string comparison in this section runs on the normalised form:
   ```
   norm(s) = s.replace(/ /g, ' ').replace(/\s+/g, ' ').replace(/\s*✕\s*$/, '').trim()
   ```
   Two mechanical reasons, both provable against the shipped file: (a) `.modal header` is `display:flex`, so `innerText` inserts a line break around each inline `<b>` run — `#m-reserved`'s header returns `'Reserved Quantity —\nDongkook\n마데카솔 크림 50ml (100004819) · 8 reserved\n✕'`, which matches the specified string neither by equality **nor** by substring; (b) the `✕` close button is a **child of `<header>`**, so its label is appended to every modal header. Without this step `QA-RES-02` and `QA-RES-05` are unpassable by any reading, and `QA-LOG-01` / `QA-LOG-03` / `QA-LOG-04` / `QA-AUD-22` are unpassable under strict equality. **Every modal-header string given in §8 is the normalised form.**
4. **Reset between scenarios by reloading the page.** The wireframe holds no server state: audit mode, `[L-13]`-added rows, star toggles, comment-search state, and open modals all reset on reload and none of them persist.
5. Close a modal with its `[data-close]` button (`Close` / `Cancel`) or by clicking the overlay backdrop.
6. wf-bar `Modal: …` buttons open a modal **without** changing the active pane; wf-bar pane buttons and the sub-tabs do change it. Never assume the default pane — every scenario below states its required pane.

**String-match convention (binding — two testers must not read these differently).**

| Wording used in a scenario | Assertion |
|---|---|
| *"reads **exactly** X"* / *"is exactly X"* | `norm(node.innerText) === norm(X)` — strict equality after step 3b |
| *"reads X"* / *"contains X"* / *"begins X"* / *"starts X"* / *"ends X"* | containment / prefix / suffix on `norm(node.innerText)`. Used deliberately where the node carries extra children (e.g. a `<small>` hint inside a `.paneheader`) |
| *"renders"* / *"is visible"* / *"exists"* used of a node | `el.offsetParent !== null`. Hidden tab panes and `display:none` rows keep their nodes in the DOM, so a bare `querySelectorAll` count is **not** the same assertion |
| *"exactly N `<selector>`"* | the count is over **visible** nodes unless the scenario names a container scope (e.g. `tbody tr:not(.audrow)`) |

**Colour tokens (so a colour word is never a judgement call).** The scenarios below name colours; these are the values to compare against `getComputedStyle`:

| Word used in §8 | CSS custom property | Hex | `rgb()` |
|---|---|---|---|
| amber | `--amber` | `#B45309` | `rgb(180, 83, 9)` |
| red | `--red` | `#DC3545` | `rgb(220, 53, 69)` |
| green | `--green` | `#198754` | `rgb(25, 135, 84)` |
| purple (text / marker) | `--ss-purple` | `#582DB5` | `rgb(88, 45, 181)` |
| purple-tinted (row background) | `--ss-purple-50` | `#F7F3FF` | `rgb(247, 243, 255)` |
| amber row background | `--amber-soft` | `#FFF3E0` | `rgb(255, 243, 224)` |

Where a scenario says a value is "rendered green/amber/red", assert its computed `color`; where it says a row is "tinted" or "highlighted", assert the computed `background-color`. Structural fallbacks (*"the only row with a non-default background"*) remain acceptable and are noted per scenario.

**Korean allow-list (for `QA-GLB-09`).** Every Hangul run on this page — all four panes and all six modals — must be a substring of one of these 17 strings and nothing else:

- **The 11 Current Stocks `Product Name KR` values:** `글로우 세럼` · `미감수 클렌징 티슈` · `바이탈 하이드라 워터크림` · `마데카솔 크림` · `시카페어 젠틀 클렌징 폼` · `포어레미디 리뉴잉 폼` · `시카페어 슬리페어 마스크` · `제로 모공 패드 2.0` · `석류 콜라겐 탄력 크림` · `바디로션` · `하트리프 77% 수딩 토너`
- **The 5 `[L-13]` autocomplete catalogue names:** `딥 대미지 트리트먼트` · `실크 헤어 오일` · `자작나무 수분 크림` · `다이브인 저분자 세럼` · `듀 틴트`
- **The one data string:** `신규` (rendered as `— (신규)` and `[신규]`)

Anything outside this set is Korean UI chrome and a `[G-6]` failure. EN brand prefixes (`Dongkook`, `UNOVE`, …) are not Hangul and are not part of the check.

**Wireframe demo limitations — QA must tag these `[ADMIN]`, never file them as bugs.** The Current Stocks search box, the Location and Sourcing Route selects, the `.filterchip` buttons, the column headers, both Export buttons, and the `🔍 Search` button are **inert**. Typing into a `.qty-in` does **not** recompute `Diff`, `Loss (₩)`, or `#auditSummary` — those are static fixtures. `[L-M4]` `Confirm` only closes the modal. No toasts, no sounds, and no pagination controls exist anywhere. Any `Cancel Inbound` button opens the same Order-409112 fixture modal `[E-59]`.

**Totals: 200 scenarios — 75 [WF] · 125 [ADMIN] · 85 negative/boundary tests (42.5%).**
Per block: NAV 12 · CS 18 · LOC 18 · AUD 44 · LOG 9 · RES 26 · HIS 18 · FRM 20 · COM 15 · EXP 6 · GLB 14.

### QA-NAV — navigation, page identity, page-level negatives

| ID | Tier | Scenario |
|---|---|---|
| **QA-NAV-01** | [WF] | **Given** the live wireframe is loaded fresh and preflight is done, **When** nothing else is clicked, **Then** `#p-current` has class `on`, `#p-search` / `#p-inbound` / `#p-outbound` do not, the sub-tab whose `innerText` starts `Current Stocks` has class `on`, and it carries the marker text `● new · default`. `[L-5]` |
| **QA-NAV-02** | [WF] | **Given** the page is loaded, **When** the agent clicks the sub-tab `Stock History`, **Then** `#p-search` becomes the only `.pane` with class `on` **and** the wf-bar button `Stock History Search` gains class `on`; **When** the agent then clicks the wf-bar button `Inbound Form`, **Then** `#p-inbound` is the only active pane and the sub-tab `Inbound Stock` gains class `on`. Sub-tabs and wf-bar stay in sync in both directions. |
| **QA-NAV-03** | [WF] | **Given** `#p-current` is the active pane, **When** the agent clicks the wf-bar button `Modal: Reserved Orders`, **Then** `#m-reserved` gains class `open` **and** `#p-current` still has class `on` (pane state unchanged, 2026-08-03 behavior); **When** the agent clicks `Close`, **Then** `#m-reserved` loses class `open` and `#p-current` is still active. `[E-51]` §2.3 |
| **QA-NAV-04** | [WF] | **Given** any pane, **Then** `.ptitle h2` has `innerText` exactly `WMS — Inventory`. `[L-10]` |
| **QA-NAV-05** | [ADMIN] | **Given** the production admin, **When** a legacy `stock-status` route or bookmark is opened, **Then** it resolves to Inventory on the Current Stocks tab (redirect or alias) and the browser title reads `Inventory`. `[L-10]` |
| **QA-NAV-06** | [WF] | **NEGATIVE.** **Given** each of the four panes and each of the six modals is opened in turn, **Then** `/print/i` matches nothing in the `innerText` of `.mock` or of any `.overlay`, and no `button`, `a`, or `input` has an accessible name matching `/print/i`. Baseline: the shipped wireframe contains zero occurrences of the string. `[BR-27]` `[G-4]` `[E-98]` |
| **QA-NAV-07** | [WF] | **NEGATIVE.** **Given** the page is loaded, **Then** `.subtabs` contains exactly four `button` elements whose `innerText` begins `Current Stocks`, `Stock History`, `Inbound Stock`, `Outbound Stock`; **and** no element in `.subtabs button` or in `.wf-tab` has an `innerText` matching `/^Audit Log/` after normalisation (created and abolished 2026-07-22; Past Audit Logs is a modal). *Scope is `.subtabs` + `.wf-tab` only — the substring `Audit Log` legitimately appears on the page inside the button `📋 Past Audit Logs` and the wf-bar shortcut `Modal: Past Audit Logs`, so an unscoped document search is the wrong test and will always fail.* `[L-15]` §9.1 #1 |
| **QA-NAV-08** | [WF] | **NEGATIVE.** **Given** every pane and modal, **Then** `/procurement hub/i`, `/return.?bin/i`, `/sample/i`, and `/photo\|upload/i` match nothing in `innerText`, and no `input[type=file]` exists. Baseline: the shipped wireframe contains zero occurrences of `sample` and zero of `print`. `[BR-2]` §9.1 #3 #7 #8 #10 |
| **QA-NAV-09** | [WF] | **Given** the page is loaded, **Then** `.wf-tab` returns exactly 10 buttons, labelled `Current Stocks (default)`, `Stock History Search`, `Inbound Form`, `Outbound Form`, `Modal: Reserved Orders`, `Modal: Cancel Inbound (Release Reservation)`, `Modal: Past Audit Logs`, `Modal: ADJUST Events (07-22)`, `Modal: ADJUST Events (06-30)`, `Modal: Confirm Audit Differences`; plus one `.wf-toggle` (`#annoToggle`). §2.3 |
| **QA-NAV-10** | [ADMIN] | **NEGATIVE.** **Given** the production admin, **Then** no `.wf-bar`, `.wf-tab`, `.wf-toggle`, `.dot`, or `.legend` element exists — the annotation and demo layers are wireframe chrome and must not ship. §2.3 §2.4 |
| **QA-NAV-11** | [WF] | **Given** the page is loaded and preflight is done, **Then** `.nav` renders, in this order: `.brand` with `innerText` exactly `SkinSeoul`; six category labels reading exactly `Operation AI ▾`, `Catalog Management ▾`, `OMS Center ▾`, `Site Management ▾`, `System Management ▾`, `Customer Management ▾`; exactly four `.navlink` elements whose normalised `innerText` is `Agent Telemetry`, `Role Assets`, `Shared Asset Health`, `SkinSeoul WP Admin`; one `[data-open="inbox1"]` button reading `💬 Comments` with a `.badge-n` of `3`; one `.user` containing a `.avatar` reading `Y` followed by `Yongwon Ryu`; and one `button.logout` reading exactly `Logout`. `[L-F5]` §3.21 |
| **QA-NAV-12** | [ADMIN] | **NEGATIVE.** **Given** the production admin, **When** the operator clicks the brand wordmark, any category dropdown label, or any `.navlink` tile, **Then** **no** event row is written for the click `[NE-13]`; **and** the identity rendered in `.user` is the same actor value stored on the next mutating event performed on this page (`[G-8]` `[G-15]`); **and** clicking `Logout` while an audit session is open ends the session **without** confirming or abandoning the audit — re-authenticating as the same auditor finds the session still open. `[L-F5]` `[E-57]` `[PD-1 · OWNER-PENDING]` §3.21 |

### QA-CS — Current Stocks list, sort, filters, routes, column contracts

| ID | Tier | Scenario |
|---|---|---|
| **QA-CS-01** | [WF] | **Given** `#p-current` active and audit mode off, **Then** the eleven `tbody tr` data rows (excluding `.audrow`) appear in `Available`-descending order with SKU column values exactly `100031877, 100024743, 100005088, 100004819, 100039958, 100005104, 100040311, 100012534, 100043697, 100038120, 100045210` and `Available` values `82, 61, 55, 34, 23, 16, 11, 6, 4, 2, 1`. `[L-11]` `[BR-10]` |
| **QA-CS-02** | [ADMIN] | **Given** the default sort, **When** the agent clicks the `Total` column header, **Then** rows re-sort by `Total` descending; **When** clicked again, ascending. No page reload `[G-2]`, and no event is persisted for the sort `[NE-3]`. `[L-11]` |
| **QA-CS-03** | [WF] | **Given** `#p-current` active, **Then** the first `select.sel` in `.cs-controls` has option 1 `All Locations` and the remaining options are line entries only — `Line A`, `Line B`, `Line C` in the fixture. No full location code (e.g. `A-02-13`) appears as an option. `[L-5]` `[BR-6]` |
| **QA-CS-04** | [ADMIN] | **Given** no `D-…` location exists, **When** an operator saves location `D-01-01` on any row, **Then** without any page reload the Location filter's option list contains `Line D`. `[E-10]` `[G-14]` |
| **QA-CS-05** | [WF] | **Given** `#p-current` active, **Then** the second `select.sel` in `.cs-controls` contains exactly, in this order: `All Sourcing Routes`, `SMART BUY`, `JIT`, `WHOLESALE`, `PARTNERSHIP`. `[L-5]` |
| **QA-CS-06** | [ADMIN] | **NEGATIVE (spec-vs-wireframe delta).** **Given** the production admin, **Then** the same select additionally offers `OTHER` as a sixth option, and selecting it returns rows whose route cell renders black bold `OTHER ({channel})`. The wireframe's five-option list predates this decision and must not be reproduced. `[PD-80 · OWNER-PENDING]` `[BR-8]` |
| **QA-CS-07** | [ADMIN] | **Given** the route filter, **When** `JIT` is selected, **Then** the result set includes SKU `100045210` whose route cell reads `JIT (Coupang)` — matching is on the base route, not on the rendered label string. `[E-53]` `[BR-7]` |
| **QA-CS-08** | [WF] | **Given** any route cell, **Then** its computed `background-color` is fully transparent and its computed `font-weight` is `800`. Applies to all four fixture classes `.tag-smartbuy`, `.tag-jit`, `.tag-wholesale`, `.tag-partnership`. Routes are black bold text, never colored pills. `[G-5]` `[BR-9]` |
| **QA-CS-09** | [WF] | **Given** `#p-current`, **Then** every `Product Name KR` cell's first element child is a `<b>` carrying the brand — e.g. the row for SKU `100005104` renders `<b>Dr.Jart+</b> 포어레미디 리뉴잉 폼` — and the Korean text is present verbatim, never translated. `[G-6]` |
| **QA-CS-10** | [WF] | **Given** `#p-current`, **Then** the row for SKU `100038120` renders an `input.loc-in` whose `value` is the empty string and whose `placeholder` is `Unassigned`; the row is present in the list, not hidden. `[E-3]` `[BR-11]` |
| **QA-CS-11** | [ADMIN] | **NEGATIVE.** **Given** an inventory with zero SKUs, **Then** the table shows `No stock records yet`, `Start Stock Audit` is disabled with tooltip `Nothing to audit`, and `⬇ Export` still produces a headers-only file. `[E-1]` |
| **QA-CS-12** | [ADMIN] | **NEGATIVE.** **Given** filters that match nothing, **Then** `No products match these filters` renders with a `Clear filters` action **and** `Start Stock Audit` is disabled. `[E-2]` |
| **QA-CS-13** | [ADMIN] | **NEGATIVE.** **Given** a SKU whose stored `Reserved` exceeds its `Total`, **Then** the value renders in red with a warning marker, an integrity banner names the SKU, and entering audit mode leaves that row's `Counted Qty` **blank** rather than prefilled. `[E-62]` |
| **QA-CS-14** | [WF] | **Given** `#p-current` and preflight step 2 done, **Then** reading the header row with `innerText` yields exactly `SKU, Image, Product Name, Product Name KR, Size, Barcode, Sourcing Route, Location, Total, Reserved, Available` for the visible headers, plus three `th.audcol` headers `Counted Qty`, `Diff`, `Loss (₩)` whose computed `display` is `none`. *(Reading with `textContent` instead yields `Location12` and `Available11` — that is the annotation dot, not a defect. See §2.4.)* `[L-5]` `[G-14]` |
| **QA-CS-15** | [WF] | **Given** `#p-current`, **Then** all eleven data rows render a `.thumb` element whose `innerText` is `IMG`, and every `Size` cell is non-empty (`30ml, 50ea, 50ml, 50ml, 350ml, 150ml, 100ml, 75ml, 150ml, 70ea, 250ml` in default order). `[E-68]` §3.1 |
| **QA-CS-16** | [WF] | **NEGATIVE.** **Given** `#p-current`, **Then** no `Reserved` cell in the Current Stocks table contains a `.reslink`, an `<a>`, or a `[data-modal]` attribute — the reservation drill-down exists only on the Stock History `📊 Stock Status` card. `[E-97]` `[L-6]` |
| **QA-CS-17** | [ADMIN] | **Given** the production admin, **When** `wholesale` is chosen in the route filter **and** `Dr.Jart` is typed in the search box, **Then** only SKU `100005088` remains (filters are AND-combined across search + line + route), and no event is persisted for the filter change. `[L-5]` `[NE-3]` |
| **QA-CS-18** | [ADMIN] | **NEGATIVE.** **Given** the projection returns the same SKU twice, **Then** both rows render, an integrity banner names the SKU, and `Start Stock Audit` is blocked with `Duplicate SKU rows detected — resolve before auditing`. `[E-67]` |

### QA-LOC — location editing, barcode registration, line dynamics

| ID | Tier | Scenario |
|---|---|---|
| **QA-LOC-01** | [WF] | **Given** `#p-current`, **Then** each of the eleven data rows contains exactly one `input.loc-in`, and their `value` attributes in default row order are `B-02-03, A-03-02, B-01-07, A-02-13, C-01-05, A-01-04, A-01-05, A-02-20, C-02-01, (empty string), B-03-02`. `[L-12]` |
| **QA-LOC-02** | [ADMIN] | **Given** SKU `100004819` at `A-02-13`, **When** the operator types `A-02-14` and presses `Enter`, **Then** a green toast reads `Location updated — 100004819 A-02-13 → A-02-14`, the page does not reload `[G-2]`, and a `location.changed` event `[DC-13]` is persisted with actor, timestamp, `old = A-02-13`, `new = A-02-14`. |
| **QA-LOC-03** | [ADMIN] | **Given** SKU `100038120` with no location, **When** the operator enters `C-03-01` and blurs, **Then** the amber placeholder is replaced by the value, a green toast reads `Location assigned — 100038120 → C-03-01`, and `location.assigned` `[DC-14]` persists with `old = null`. |
| **QA-LOC-04** | [ADMIN] | **NEGATIVE.** **When** the operator enters `shelf 3` (free text) into any `.loc-in` and presses `Enter`, **Then** an inline error `Invalid location code` appears, focus stays in the input, the stored value is unchanged, and **no** `[DC-13]` event exists. `[E-5]` |
| **QA-LOC-05** | [ADMIN] | **NEGATIVE.** **Given** `A-02-20` belongs to SKU `100012534`, **When** the operator assigns `A-02-20` to SKU `100040311`, **Then** the save is blocked with `Location A-02-20 is already assigned to SKU 100012534`, nothing changes, and `location.assign_blocked` `[DC-28]` persists with the attempted location and the occupying SKU. `[E-6]` `[PD-46 · OWNER-PENDING]` |
| **QA-LOC-06** | [ADMIN] | **NEGATIVE.** **Given** two operators open the same SKU row, **When** both save a different location, **Then** the second receives a 409, the row reloads with a non-green toast naming the other actor, and **two** `[DC-13]` events exist (no silent overwrite). `[E-7]` `[PD-7 · OWNER-PENDING]` |
| **QA-LOC-07** | [ADMIN] | **NEGATIVE.** **Given** the network drops during a location save, **Then** the input reverts to the server value, a red toast appears, no `[DC-13]` event is written, and retrying the same save produces exactly one event. `[E-8]` `[G-9]` |
| **QA-LOC-08** | [WF] | **Given** `#p-current`, **Then** the row for SKU `100024743` renders `input.bcin` with placeholder `Enter barcode` in the `Barcode` column, while the row for SKU `100031877` renders the plain text `8809738317481`; **and** `document.querySelectorAll('#p-current tbody tr:not(.audrow) .bcin').length === 1` — exactly one `.bcin` among the eleven data rows. *Do **not** assert `.bcin` unscoped: the shipped wireframe reuses `class="bcin"` for `#auSearch`, the `[L-13]` autocomplete input, which lives inside `tr.audrow` in the same `<table>`, so a table-wide count is **2** both in and out of audit mode (`display:none` does not remove the node). See §3.8's selector warning — in production the two inputs must not share a class.* `[L-12]` `[E-4]` |
| **QA-LOC-09** | [ADMIN] | **Given** the barcode input on SKU `100024743`, **When** the operator scans a new barcode (keyboard-wedge: digits + automatic Enter), **Then** the value commits, a green toast reads `Barcode registered — 100024743 {barcode}`, and an event named **exactly** `product.barcode_registered` `[DC-15]` persists with `old = null`. The event name is byte-identical with View Orders. |
| **QA-LOC-10** | [ADMIN] | **NEGATIVE.** **When** the operator enters `8809738317481` (already owned by SKU `100031877`) on SKU `100024743`, **Then** the save is rejected with `Barcode 8809738317481 already belongs to SKU 100031877`, nothing is stored, and `[DC-29]` persists. `[E-4]` |
| **QA-LOC-11** | [ADMIN] | **NEGATIVE.** **When** an unchanged location value is re-committed, **Then** no toast appears and **no** `[DC-13]` event is written. `[NE-10]` |
| **QA-LOC-12** | [ADMIN] | **Given** `Line C` has exactly one location and it is reassigned to a `B-…` code, **Then** `Line C` disappears from the Location filter options; if `Line C` was the active filter it resets to `All Locations` with a non-green toast, rather than silently showing zero rows. `[E-55]` |
| **QA-LOC-13** | [ADMIN] | **NEGATIVE.** **When** a location code whose line segment cannot be parsed is saved, **Then** it is rejected at validation `[E-5]` and is never bucketed into `Unassigned`. `[E-64]` |
| **QA-LOC-14** | [ADMIN] | **NEGATIVE.** **When** a barcode is scanned into a `.loc-in` (wrong field), **Then** the numeric string fails the location pattern and is rejected exactly as `[E-5]`; nothing is saved and the value is never coerced into a location. `[E-73]` |
| **QA-LOC-15** | [ADMIN] | **Given** a scanner that appends `\r`, **When** `  8809738317481\r` is committed into a `.bcin`, **Then** the stored barcode is `8809738317481` (trimmed), exactly one `product.barcode_registered` `[DC-15]` event persists carrying the trimmed value, and re-scanning the same code produces **no** second barcode record. `[E-74]` `[DC-15]` |
| **QA-LOC-16** | [ADMIN] | **Given** SKU `100004819` at `A-02-13`, **When** the operator clears the `.loc-in` to empty and blurs, **Then** the row returns to the `Unassigned` bucket, a green toast reads `Location cleared — 100004819 A-02-13 → Unassigned`, and `[DC-13]` persists with `new = null`. `[E-76]` |
| **QA-LOC-17** | [ADMIN] | **NEGATIVE.** **Given** two catalogue products already share one barcode (pre-existing data), **When** that barcode is searched on `[L-F1]`, **Then** both are returned with SKU and size for disambiguation and the page does not silently pick one; **and** registering that barcode onto a third SKU is still blocked `[E-4]`. `[E-75]` |
| **QA-LOC-18** | [WF] | **Given** `#p-current`, **When** the agent focuses the `.loc-in` of SKU `100004819`, **clears the field** (the input ships pre-filled with `A-02-13`), **sets its value to** `A-02-14`, and presses `Enter`, **Then** the input's live value is exactly `A-02-14`, the document is **not** re-navigated, and no form submission occurs. *Append-without-clearing yields `A-02-13A-02-14` and fails — clear first.* *(The wireframe has no persistence layer — the toast and the event are asserted at [ADMIN] tier by `QA-LOC-02`.)* `[G-2]` |

### QA-AUD — audit lifecycle, counting, unregistered add, confirm gate

| ID | Tier | Scenario |
|---|---|---|
| **QA-AUD-01** | [WF] | **Given** `#p-current` active, `#toggleAudit` `innerText` is exactly `Start Stock Audit`, no `.audcol` cell is visible, `#auditSummary` is hidden, and `.audrow` is hidden — **When** the agent clicks `#toggleAudit` — **Then** the button `innerText` becomes exactly `Exit Stock Audit`; the headers `Counted Qty`, `Diff`, `Loss (₩)` become visible; `.audrow` becomes visible as the last `tbody` row; `#auditSummary` becomes visible; and the data rows re-sort by `.loc-in` value ascending — `A-01-04, A-01-05, A-02-13, A-02-20, A-03-02, B-01-07, B-02-03, B-03-02, C-01-05, C-02-01` — with the empty-location row (SKU `100038120`) **last**. `[L-7]` `[G-14]` `[BR-11]` |
| **QA-AUD-02** | [WF] | **Given** audit mode is on, **When** the agent clicks `#toggleAudit` again, **Then** the button reads `Start Stock Audit`, every `.audcol` cell computes to `display: none`, `#auditSummary` hides, `.audrow` hides, and the first data row is SKU `100031877` again (Available-descending restored, not the pre-audit custom sort). `[E-9]` `[BR-10]` |
| **QA-AUD-03** | [WF] | **Given** audit mode is on, **Then** `#auditSummary` `innerText` contains `Total stock loss (sum of diff × product cost):` followed by `+₩46,260` and the qualifier `— target 0`, and it contains a button whose `innerText` is exactly `Confirm Audit Differences (ADJUST log)`. `[L-7]` `[BR-4]` `[BR-31]` |
| **QA-AUD-04** | [WF] | **FIXTURE CENSUS — do not report as a prefill bug.** **Given** audit mode is on, **Then** exactly **nine** of the eleven rows have an `input.qty-in` whose value equals that row's `Total` cell, and exactly **two** deliberately differ: SKU `100005104` has `Total 18` / `Counted Qty 17`, and SKU `100012534` has `Total 9` / `Counted Qty 11`. These two seed the Diff/Loss demo. The prefill rule itself `[PD-40 · OWNER-PENDING]` is asserted at [ADMIN] tier by `QA-AUD-05`. `[E-12]` |
| **QA-AUD-05** | [ADMIN] | **Given** a freshly started audit in the production admin, **Then** **every** row's `Counted Qty` is prefilled with that row's current system `Total`, with no seeded differences. `[PD-40 · OWNER-PENDING]` `[BR-12]` |
| **QA-AUD-06** | [WF] | **Given** audit mode is on, **Then** the `Diff` / `Loss (₩)` cells read `−1` / `−₩15,000` on SKU `100005104`, `+2` / `+₩61,260` on SKU `100012534`, and `0` / `₩0` on the other nine rows; `−15,000 + 61,260 = +46,260` reconciles with `#auditSummary`. `[L-7]` `[BR-4]` |
| **QA-AUD-07** | [ADMIN] | **Given** an audit is started **while a Location or Route filter is active**, **Then** entry is allowed and an `audit.session_started` event `[DC-7]` persists with session id, auditor, start timestamp, the filter state in force, and the scope row count — so `[L-15]` can never be misread as "the whole catalog was counted". `[E-11]` `[PD-47 · OWNER-PENDING]` |
| **QA-AUD-08** | [ADMIN] | **NEGATIVE.** **Given** auditor A has an active session, **When** auditor B clicks `Start Stock Audit`, **Then** entry is blocked with a red toast `Stock audit already in progress — started {HH:MM} by {auditor}`, no second session exists, and `[DC-32]` persists. `[E-23]` `[PD-44 · OWNER-PENDING]` |
| **QA-AUD-09** | [ADMIN] | **Given** audit mode and the row for SKU `100005104` (`Total 18`), **When** the operator types `17` and presses `Tab`, **Then** `Diff` renders `−1` in red, `Loss (₩)` renders `−₩15,000` in red, `#auditSummary` recomputes, focus moves to the **next row's** `Counted Qty` in walking order, and `[DC-24]` persists `prefill 18 → entered 17`. `[L-7]` |
| **QA-AUD-10** | [ADMIN] | **NEGATIVE.** **When** the operator enters `abc`, `−3`, or clears a count to blank, **Then** an inline error `Enter a whole number of 0 or more` appears, `Diff` is **not** computed, the row is excluded from `[L-M1]`, and no `[DC-24]` value is committed. `[E-13]` |
| **QA-AUD-11** | [WF] | **NEGATIVE.** **Given** audit mode is **off**, **Then** `#auditSummary`, every `.audcol` element, and `.audrow` all compute to `display: none` — audit-only UI is invisible to the non-auditor who uses this screen daily. `[G-14]` `[BR-5]` |
| **QA-AUD-12** | [WF] | **Given** audit mode is on, **When** the agent types `UNOVE` into `#auSearch`, **Then** `#auDrop` becomes visible and contains exactly two `div[data-sku]` entries whose `innerText` is `UNOVE 딥 대미지 트리트먼트 · 320ml · 100048201` and `UNOVE 실크 헤어 오일 · 150ml · 100051200` — the **size is shown** in every entry. `[L-13]` `[BR-25]` |
| **QA-AUD-13** | [WF] | **NEGATIVE.** **When** the agent types `zzzz` into `#auSearch`, **Then** `#auDrop` `innerText` is exactly `No match — register manually via Unrecognized flow (F)` and it contains zero `div[data-sku]` elements. `[E-15]` |
| **QA-AUD-14** | [WF] | **NEGATIVE.** **Given** `#auSearch` contains free-typed text (`Torrid`) with no dropdown entry clicked, **When** the agent clicks `#auAdd`, **Then** the `tbody` row count is unchanged and `document.activeElement` is `#auSearch`. *(In production `#auAdd` is disabled in this state — asserted by `QA-AUD-15`. The wireframe leaves it enabled and no-ops; that difference is a known spec-vs-wireframe delta, not a bug.)* `[E-16]` §3.9 |
| **QA-AUD-15** | [ADMIN] | **Given** the production admin in audit mode with no autocomplete selection made, **Then** `#auAdd` is rendered disabled. `[E-16]` |
| **QA-AUD-16** | [WF] | **Given** audit mode is on, **When** the agent types `Torriden`, clicks the dropdown entry, enters Location `B-01-02` and Qty `3`, and clicks `Add`, **Then** a new purple-tinted `tr` is inserted as the **first** child of the `tbody`, showing SKU `100027733`, the Korean name `Torriden 다이브인 저분자 세럼` with a `[NEW]` marker, size `50ml`, `Total 0`, `Reserved 0`, `Available 0`, `Counted Qty 3`, `Diff +3`, `Loss — (신규)`; and `#auSearch`, `#auLoc`, `#auQty` are all cleared to empty. `[L-13]` |
| **QA-AUD-17** | [WF] | **Given** a dropdown selection has been made, **When** `Add` is clicked with `#auQty` and `#auLoc` left blank, **Then** the inserted row shows `Counted Qty 1` and its `.loc-in` value is `Unassigned`. `[E-17]` |
| **QA-AUD-18** | [ADMIN] | **NEGATIVE.** **When** the operator adds a product already visible in the list, or adds the same product twice in one session, **Then** the inline notice `Already in this audit — edit the Counted Qty on the existing row` appears and no duplicate row is inserted. `[E-18]` |
| **QA-AUD-19** | [ADMIN] | **NEGATIVE.** **When** `Add` is attempted with `#auQty` set to `0`, `−2`, or `abc`, **Then** inline validation `Enter a whole number of 1 or more` blocks it and no row is inserted. Blank remains a valid default of `1`. `[E-77]` `[E-17]` |
| **QA-AUD-20** | [ADMIN] | **NEGATIVE.** **When** `Add` is attempted with `#auLoc` set to a location already held by another SKU, **Then** it is blocked with `Location {code} is already assigned to SKU {sku}`, no row is inserted, and `[DC-28]` persists. `[E-78]` `[PD-46 · OWNER-PENDING]` |
| **QA-AUD-21** | [ADMIN] | **Given** the `No match` result, **When** the operator follows the link, **Then** the Unrecognized Tracking page opens **and** `audit.no_catalog_match` `[DC-26]` persists with the search term. `[E-15]` |
| **QA-AUD-22** | [WF] | **Given** audit mode is on, **When** the agent clicks `Confirm Audit Differences (ADJUST log)`, **Then** `#m-adjust` gains class `open`; its header reads exactly `Confirm Audit Differences — July 2026 Stock Audit (Auditor: Yongwon)` (normalised per §8.0 step 3b — the raw `innerText` appends `✕`); its table body has exactly three rows, asserted **cell by cell** because `#m-adjust` carries `System` and `Counted` as **separate columns** (the `System → Counted` single-cell form belongs to `[L-M2]`, not here) — row 1 `SKU 100005104 · System 18 · Counted 17 · Diff −1`, row 2 `SKU 100012534 · System 9 · Counted 11 · Diff +2`, row 3 `SKU 100048201 · [NEW] · System 0 · Counted 3 · Diff +3`; exactly one row carries the `[NEW]` marker; no zero-diff row appears; and the primary footer button `innerText` is exactly `Confirm — record 3 ADJUST events`. `[L-M1]` |
| **QA-AUD-23** | [WF] | **STALE-FIXTURE CENSUS — asserts the shipped wireframe, not the contract.** **Given** `#m-adjust` is open, **Then** the amber note begins `⚠ Reserved shortage check` and ends `None in this audit.`, and the second note reads exactly `Total stock loss: +₩46,260 (target 0) · the 3 new additions are not losses — on confirm, Current Stocks · Available update immediately; monthly audit logs retained.` — **the `3` in that string is a wireframe defect `[INV-WFX-1 · proposed]`**: the modal contains exactly **one** `[NEW]` row (`QA-AUD-22`) and `[L-15]` records `New Additions 1` for this session (`QA-LOG-02`). The spec's contract is the templatised form in §3.13 (`the {n} new addition(s) are not losses`), asserted at `[ADMIN]` tier by `QA-AUD-44`. Report the mismatch against the wireframe backlog, never against this spec. `[L-M1]` |
| **QA-AUD-24** | [ADMIN] | **NEGATIVE.** **Given** SKU `100004819` has `Reserved 8`, **When** the auditor enters `Counted 5` and opens `[L-M1]`, **Then** the affected orders (`407812`, `413650`, `409112`) are listed inside the modal, `Confirm — record N ADJUST events` is **disabled**, and `[DC-18]` persists. **When** the auditor ticks `Reviewed with the order team`, **Then** Confirm enables and `[DC-25]` persists. `[E-14]` `[PD-48 · OWNER-PENDING]` `[BR-13]` |
| **QA-AUD-25** | [ADMIN] | **Given** `[L-M1]` with 3 rows, **When** `Confirm — record 3 ADJUST events` is clicked, **Then** a green toast reads `Stock audit confirmed — 3 ADJUST events recorded · total loss +₩46,260`; audit mode exits and the sort restores to Available-descending; `Total`/`Available` update in place with **no page reload** `[G-2]`; two `[DC-8]` events and one `[DC-9]` event persist; one `[DC-10]` session event persists; and searching SKU `100005104` on Stock History shows a new `ADJUST` row with quantity `−1`, auditor `Yongwon`, and the confirm timestamp. |
| **QA-AUD-26** | [ADMIN] | **NEGATIVE.** **When** `Confirm — record 3 ADJUST events` is double-clicked inside the debounce window, **Then** exactly one session and exactly three ADJUST events exist. `[E-19]` `[G-9]` |
| **QA-AUD-27** | [ADMIN] | **NEGATIVE.** **Given** the network fails mid-commit, **Then** neither the ADJUST events nor the session row exist (all-or-nothing), the modal stays open with counts intact, and a red toast reads `Audit not recorded — nothing was changed. Try again`. `[E-20]` |
| **QA-AUD-28** | [ADMIN] | **NEGATIVE.** **Given** counts have been entered, **When** `Exit Stock Audit` is clicked, **Then** a confirm dialog titled `Exit stock audit?` appears reading `{n} entered count(s) will be discarded. The session will be recorded as abandoned.` with buttons `Keep counting` and `Exit and discard`; on discard, `[DC-17]` persists with the count snapshot and **no** ADJUST events are created. `[E-21]` `[PD-5 · OWNER-PENDING]` |
| **QA-AUD-29** | [ADMIN] | **Given** an audit with no entered counts, **When** `Exit Stock Audit` is clicked, **Then** no confirm dialog appears and a green toast reads `Stock audit closed — no adjustments recorded`. `[L-7]` |
| **QA-AUD-30** | [ADMIN] | **NEGATIVE.** **Given** a count was entered for SKU `100004819`, **When** an outbound of 2 units is confirmed elsewhere before the auditor presses Confirm, **Then** `[L-M1]` re-renders with `Diff` recomputed against the new system quantity and a non-green toast reads `Stock changed during the audit — differences recalculated` **before** Confirm can proceed. `[E-22]` `[PD-6 · OWNER-PENDING]` |
| **QA-AUD-31** | [ADMIN] | **Given** an audit where every `Diff` is 0, **When** Confirm is pressed, **Then** the session is recorded with `0` adjustments and `0` new additions and appears in `[L-15]` with `₩0 · target met` and `—` in the Detail column. `[E-24]` |
| **QA-AUD-32** | [ADMIN] | **Given** a SKU with no product cost and `Diff = −2`, **Then** its `Loss (₩)` renders `—`, an ADJUST event `[DC-8]` is still created, and the session total excludes it. `[E-25]` |
| **QA-AUD-33** | [ADMIN] | **Given** the product cost changes between count entry and confirm, **Then** the cost **at confirm time** is used and the applied cost value is stored on `[DC-8]`, so the loss figure remains reproducible after a later cost change. `[E-61]` |
| **QA-AUD-34** | [ADMIN] | **NEGATIVE.** **Given** a SKU is created system-wide after the session started, **Then** it does not appear in the audit list mid-session, does not change `SKUs Checked`, and receives no adjustment. `[E-60]` |
| **QA-AUD-35** | [ADMIN] | **NEGATIVE.** **Given** an audit is in progress with entered counts, **When** the browser is refreshed, **Then** the session is still open server-side, no orphan lock blocks a later `Start Stock Audit`, and where draft autosave exists the counts are restored from `[DC-24]`. `[E-58]` |
| **QA-AUD-36** | [WF] | **Given** audit mode is on and a `[L-13]` row has been added, **When** the agent clicks the wf-bar `Modal: Past Audit Logs` and then `Close`, **Then** `#toggleAudit` still reads `Exit Stock Audit`, the added row is still the first `tbody` child, and `#p-current` is still the active pane. `[E-51]` `[E-52]` |
| **QA-AUD-37** | [ADMIN] | **NEGATIVE.** **Given** an open session with counts entered on `Line A` rows, **When** the operator switches the Location filter to `Line C`, **Then** the session scope is unchanged, the `Line A` counts are retained and still committed at Confirm, a warning chip reads `{n} counted row(s) hidden by the current filter`, and `[DC-34]` persists the divergence. `[E-66]` `[BR-34]` |
| **QA-AUD-38** | [ADMIN] | **Given** a session whose only non-zero rows are `[L-13]` new additions, **When** Confirm is pressed, **Then** it succeeds, total loss is `₩0`, one `audit.new_item_added` `[DC-9]` event persists per added row (each carrying `system 0 → counted n`, the location, and the NEW-ADDITION flag), and `[L-15]` shows `Adjustments 0` / `New Additions {n}` / `₩0 · target met`. `[E-79]` `[DC-9]` |
| **QA-AUD-39** | [ADMIN] | **Given** a session started `23:50` and confirmed `00:10` the next day, **Then** its `[L-15]` `Audit Date` is the **start** date, while `[DC-10]` separately records the confirm timestamp that `[L-M2]` renders. `[E-80]` `[BR-36]` |
| **QA-AUD-40** | [ADMIN] | **Given** a session with a scope of 9 rows and 2 rows added via `[L-13]`, **Then** `[L-15]` `SKUs Checked` reads `11` — scope rows **plus** shelf-found additions. *This is the `[BR-35]` extension of `[PD-47]`, not the register's base wording (which counts scope rows only); if the owner declines the extension the expected value becomes `9`.* `[E-81]` `[BR-35]` `[PD-47 · OWNER-PENDING]` |
| **QA-AUD-41** | [ADMIN] | **NEGATIVE.** **Given** a row in the session scope is deleted or merged system-wide mid-session, **When** Confirm is pressed, **Then** that row is dropped from the batch, the recalculation toast names it (`{n} row(s) no longer exist and were removed from this audit`), no ADJUST is written against the dead SKU, and the session still confirms. `[E-82]` |
| **QA-AUD-42** | [ADMIN] | **Given** an open session is force-closed by an administrator or a stale-session sweeper, **Then** `[DC-17]` persists with reason `force-closed` or `timeout`, the warehouse lock is released, and the next `Start Stock Audit` succeeds without an administrator intervention. `[E-83]` |
| **QA-AUD-43** | [ADMIN] | **NEGATIVE.** **Given** the Reserved-shortage gate has fired, **When** the auditor exits the audit without ticking `Reviewed with the order team`, **Then** `[DC-18]` and `[DC-17]` both persist and **no** `[DC-25]` exists — an unacknowledged shortage must never look acknowledged. `[E-84]` |
| **QA-AUD-44** | [ADMIN] | **Given** the production admin with a session holding **one** `[L-13]` new addition and a total loss of `+₩46,260`, **When** `[L-M1]` is opened, **Then** its total note reads exactly `Total stock loss: +₩46,260 (target 0) · the 1 new addition(s) are not losses — on confirm, Current Stocks · Available update immediately; monthly audit logs retained.` — the count is templatised from the actual number of `[NEW]` rows in the modal and is never a literal. Re-run with three additions and the same note reads `the 3 new addition(s) …`. *(The shipped wireframe hard-codes `3` regardless — `[INV-WFX-1 · proposed]`, asserted at `[WF]` tier by `QA-AUD-23`.)* `[L-M1]` §3.13 |

### QA-LOG — Past Audit Logs and ADJUST detail modals

| ID | Tier | Scenario |
|---|---|---|
| **QA-LOG-01** | [WF] | **Given** `#p-current` active with audit mode **off**, **When** the agent clicks `📋 Past Audit Logs`, **Then** `#m-auditlog` gains class `open` and its header `innerText` starts `Past Audit Logs — monthly session records`. The button is reachable outside audit mode (history is not audit-only UI). `[L-15]` |
| **QA-LOG-02** | [WF] | **Given** `#m-auditlog` is open, **Then** the header row reads `Audit Date, Auditor, SKUs Checked, Adjustments, New Additions, Total Loss, Detail` and exactly three body rows exist: `2026-07-22 / Yongwon / 10 / 2 (−1 / +2) / 1 / +₩46,260`, `2026-06-30 / Dean / 9 / 5 (−4 / +1) / 0 / −₩128,460`, `2026-05-31 / Dean / 9 / 0 / 0 / ₩0 · target met`. `[L-15]` |
| **QA-LOG-03** | [WF] | **Given** `#m-auditlog` is open, **When** the agent clicks `View ADJUST events` in the `2026-07-22` row, **Then** `#m-adjlog` gains class `open` and its header's **normalised** `innerText` (§8.0 step 3b — the raw value appends `✕` from the close button) is exactly `2026-07-22 Stock Audit — 3 ADJUST events (Auditor: Yongwon, confirmed 14:20)`, and three body rows all timestamped `14:20:11`, the third tinted purple and carrying `[NEW ADDITION]` with `Loss` `—`. `[L-M2]` |
| **QA-LOG-04** | [WF] | **Given** `#m-auditlog` is open, **When** the agent clicks `View ADJUST events` in the `2026-06-30` row, **Then** `#m-adjlog6` opens and its header's **normalised** `innerText` (§8.0 step 3b) is exactly `2026-06-30 Stock Audit — 5 ADJUST events (Auditor: Dean, confirmed 17:05)`, five body rows all timestamped `17:05:42`, and the note `Total loss −₩128,460 — June exceeded the loss target; root-cause investigation in progress (suspected picking mis-outbound).` `[L-M2b]` |
| **QA-LOG-05** | [WF] | **NEGATIVE.** **Given** `#m-auditlog` is open, **Then** the `2026-05-31` row's `Detail` cell contains the literal `—` and its anchor carries **no** `data-modal` attribute; clicking it opens no modal. A zero-adjustment session has no ADJUST detail. `[E-24]` |
| **QA-LOG-06** | [WF] | **Given** `#m-adjlog` is open, **Then** its note reads exactly `Each event is also recorded as ADJUST type in that SKU's Stock History — search the SKU and filter by type to inspect individually. Total loss +₩46,260 (new additions excluded).` and every `Product` cell renders a Korean name whose first element child is a `<b>` brand. `[G-6]` `[G-8]` |
| **QA-LOG-07** | [ADMIN] | **NEGATIVE.** **Given** any `[L-15]` session row or any `[L-M2]` / `[L-M2b]` ADJUST row, **Then** no edit, delete, reverse, or re-open control exists anywhere in those three views. `[BR-24]` §9.1 #12 |
| **QA-LOG-08** | [ADMIN] | **Given** a session confirmed via `[L-M1]`, **Then** a matching `[L-15]` row appears without a page reload, and its values are read from the persisted `[DC-10]` event — not from a separate audit-only store. `[G-8]` |
| **QA-LOG-09** | [WF] | **Given** `#m-auditlog` is open, **Then** the computed `color` of the `Total Loss` cell is `rgb(180, 83, 9)` (`--amber`) on the `2026-07-22` row, `rgb(220, 53, 69)` (`--red`) on the `2026-06-30` row, and `rgb(25, 135, 84)` (`--green`) on the `2026-05-31` row — three distinct values, per the §8.0 colour-token table — and the `2026-05-31` cell's normalised `innerText` ends ` · target met`. `[L-15]` `[BR-31]` |

### QA-RES — Reserved modal and Cancel Inbound

| ID | Tier | Scenario |
|---|---|---|
| **QA-RES-01** | [WF] | **Given** the agent has clicked the sub-tab `Stock History` so `#p-search` is active, **Then** the `📊 Stock Status` card shows `42` / `Total Qty`, `8` / `Reserved Qty`, `34` / `Available Qty`; the `8` is wrapped in `span.reslink` with a dotted underline; and the card note reads `Click Reserved → allocated orders modal (incl. releasing phantom orders · restock)`. `[L-6]` `[L-F1]` |
| **QA-RES-02** | [WF] | **Given** `#p-search` is the active pane, **When** the agent clicks `.reslink`, **Then** `#m-reserved` gains class `open`; its header's **normalised** `innerText` (§8.0 step 3b — the raw value is `'Reserved Quantity —\nDongkook\n마데카솔 크림 50ml (100004819) · 8 reserved\n✕'`) is exactly `Reserved Quantity — Dongkook 마데카솔 크림 50ml (100004819) · 8 reserved`, with `Dongkook` inside a `<b>`; and its table header reads `Order ID, Order Date, Customer, Status, Reserved Qty, Reserved At, Action`. `[L-M3]` |
| **QA-RES-03** | [WF] | **Given** `#m-reserved` is open, **Then** exactly three body rows exist — `407812 / 2026-06-30 / Sarah Kim / processing / 2 / 07-12 11:05`, `413650 / 2026-07-08 / Emma Park / processing / 3 / 07-08 14:22`, `409112 / 2026-07-02 / Liam Chen / cancelled / 3 / 07-02 09:10` — and **only** the `409112` row carries a non-default computed `background-color` (`rgb(255, 243, 224)`, `--amber-soft`) **and** the badge `SUSPECTED PHANTOM`, and it is the only row whose `Cancel Inbound` button has a visible border colour of `rgb(220, 53, 69)` (`--red`, red outline). Structural fallback if the token values drift: exactly one of the three rows differs from the other two on both properties. `[BR-19]` |
| **QA-RES-04** | [WF] | **Given** `#m-reserved` is open, **Then** its note reads exactly `Total 8 = 2+3+3 · Suspected phantom = the order is cancelled/refunded but the reservation was never released — release target. If reservation-order mismatches persist, investigate unconfirmed events with the Pending confirm filter in Stock History (linked to Dean's report).` and `2+3+3` reconciles with the header count `8`. `[L-M3]` `[E-27]` |
| **QA-RES-05** | [WF] | **Given** `#m-reserved` is open, **When** the agent clicks the `409112` row's `Cancel Inbound`, **Then** `#m-resrelease` gains class `open` and its header's **normalised** `innerText` (§8.0 step 3b — the raw value is `'Cancel Inbound — Order 409112 ·\nDongkook\n마데카솔 크림 × 3\n✕'`) is exactly `Cancel Inbound — Order 409112 · Dongkook 마데카솔 크림 × 3`; four bold numbered steps are present (`1. Release the reservation (Reserved) on this order?`, `2. Restock the units?`, `3. Restock Qty`, `4. Memo (Optional)`); two `input[name=resback]` radios exist with `Yes — Available +3 (restock)` checked by default and `No — exclude from stock (damaged · lost etc., record the loss as ADJUST(−3))` second; the Restock Qty input holds `3` with the hint `Default = qty originally inbounded (editable)`; and the memo textarea placeholder is `Cancellation reason or notes — if written, also recorded in the order's Comments history`. `[L-M4]` |
| **QA-RES-06** | [WF] | **Given** `#m-resrelease` is open, **Then** its note reads exactly `On release, Reserved 8 → 5; choosing "Yes" brings Available 34 → 37. The action is recorded in Stock History as a RESERVE release event.` and its footer contains exactly two buttons, `Cancel` and `Confirm`. `[L-M4]` |
| **QA-RES-07** | [ADMIN] | **Given** `[L-M4]` with `Yes` selected and Restock Qty `3`, **When** `Confirm` is clicked, **Then** a green toast reads `Reservation released — Order 409112 · restocked +3`; `Reserved` goes `8 → 5` and `Available` goes `34 → 37`; a `RESERVE` release row appears in SKU `100004819`'s Stock History; `[DC-4]` and `[DC-5]` both persist with actor and timestamp, `[DC-5]` capturing both the default and the entered qty; and the page does **not** reload `[G-2]`. |
| **QA-RES-08** | [ADMIN] | **Given** `[L-M4]` with `No` selected, Restock Qty `3`, memo `Damaged in storage`, **When** `Confirm` is clicked, **Then** the toast reads `Reservation released — Order 409112 · ADJUST(−3) recorded`; `Reserved` goes `8 → 5` and `Available` stays `34`; Stock History gains **both** a `RESERVE` release row **and** an `ADJUST(−3)` row; `[DC-4]` and `[DC-6]` (classification `damaged`, source `m4-writeoff`) persist; and the memo appears in Order 409112's Comments history via `[DC-11]` with `source = m4-memo`. |
| **QA-RES-09** | [ADMIN] | **NEGATIVE.** **When** Restock Qty is set to `5` (above the inbounded `3`), **Then** inline validation blocks it with `Restock qty cannot exceed the inbounded qty (3)` and `Confirm` does not commit. `[E-30]` `[PD-50 · OWNER-PENDING]` |
| **QA-RES-10** | [ADMIN] | **Given** Restock Qty is edited to `1` with `Yes` selected and memo `2 units water-damaged`, **When** `Confirm` is clicked, **Then** `Available` goes `34 → 35`, a `stock.restocked` event `[DC-5]` persists capturing **both** the default (originally-inbounded) qty `3` **and** the entered qty `1`, an `ADJUST(−2)` event `[DC-6]` with `source = m4-remainder` carrying the same memo is created, and both appear in Stock History. `[E-31]` `[DC-5]` `[DC-6]` `[PD-49 · OWNER-PENDING]` |
| **QA-RES-11** | [ADMIN] | **Given** a memo containing `@Dean`, **When** `Confirm` is clicked, **Then** a Slack message is delivered to `#fulfillment-admin-comments` (`C0BMGEWM5QA`) whose body @mentions Dean and carries entity no., comment text, time, author, and a deep link; `[DC-12]` persists with `result = ok`. `[G-7]` `[E-36]` §6.1 |
| **QA-RES-12** | [ADMIN] | **NEGATIVE.** **Given** Slack is unreachable, **Then** the release still commits, `[DC-12]` records `result = failed`, a retry is scheduled, and no UI rollback or block occurs. `[E-65]` `[PD-4 · OWNER-PENDING]` |
| **QA-RES-13** | [ADMIN] | **NEGATIVE.** **When** `Confirm` is double-clicked in `[L-M4]`, **Then** exactly one release event and exactly one adjustment event exist. `[E-32]` `[G-9]` |
| **QA-RES-14** | [ADMIN] | **NEGATIVE.** **Given** the network fails between the release write and the restock write, **Then** neither effect is persisted (atomic composite), a red toast appears, and `Reserved`/`Available` are unchanged. A "released but not restocked" state must not be observable. `[E-33]` |
| **QA-RES-15** | [ADMIN] | **NEGATIVE.** **Given** two operators open `[L-M4]` on reservation `409112`, **When** both click `Confirm`, **Then** the second receives `Reservation already released`, `Reserved` is decremented exactly once, `[L-M3]` re-fetches, and `[DC-31]` persists with reason `already_released`. `[E-34]` |
| **QA-RES-16** | [ADMIN] | **NEGATIVE.** **Given** `[L-M3]` is open and order `413650` is outbounded elsewhere, **When** its `Cancel Inbound` is confirmed, **Then** the write is rejected with `Order state changed — reloading`, the modal re-fetches, and nothing partial is written. `[E-35]` `[PD-6 · OWNER-PENDING]` |
| **QA-RES-17** | [ADMIN] | **Given** the `407812` row (status `processing`), **When** `Cancel Inbound` → `Confirm` is used, **Then** an extra confirmation appears reading `Order 407812 is still processing — release anyway?` before anything commits; declining commits nothing. `[E-29]` `[PD-45 · OWNER-PENDING]` `[BR-21]` |
| **QA-RES-18** | [ADMIN] | **NEGATIVE.** **Given** a SKU whose `Reserved` is `0`, **Then** the number in the `📊 Stock Status` card is plain text with no `.reslink` class, no pointer cursor, and clicking it opens nothing (an empty modal is not acceptable). `[E-26]` |
| **QA-RES-19** | [ADMIN] | **NEGATIVE.** **Given** stored reservations summing to `5` while the header says `8`, **Then** a red integrity banner inside `[L-M3]` names both numbers (`Header 8 · rows total 5 — reservation data is inconsistent`) and the rows still render so cleanup remains possible. `[E-27]` |
| **QA-RES-20** | [ADMIN] | **Given** `.reslink` is clicked, **Then** `inventory.reserved_orders_opened` `[DC-30]` persists with the SKU, the reserved qty at open, the phantom-flagged order ids, actor, and timestamp. |
| **QA-RES-21** | [ADMIN] | **NEGATIVE.** **Given** an order refunded for only part of its line, **Then** the reservation is flagged `SUSPECTED PHANTOM` **only** if it exceeds the still-live line quantity; a reservation matching the un-refunded remainder is not flagged. `[E-28]` `[BR-19]` |
| **QA-RES-22** | [ADMIN] | **Given** an order allocation created off-page, **Then** `stock.reserved` `[DC-3]` persists with actor `System`, SKU, order id, reserved `before → after`, the reserved-at timestamp, and the order status at reservation; and both the `Reserved` column and every `[L-M3]` row are rendered **from** that event, with no second reservation store. `[G-8]` |
| **QA-RES-23** | [ADMIN] | **NEGATIVE.** **When** Restock Qty is set to `0` while `Yes` is selected, **Then** it is blocked with `Choose "No" to write the whole quantity off` and no `[DC-5]` event is created. `[E-85]` |
| **QA-RES-24** | [ADMIN] | **Given** a reservation whose order record is unreadable or hard-deleted, **Then** the `[L-M3]` row renders `Order unavailable` instead of the deep link, `Cancel Inbound` is **still** available, and a successful release records the dangling order id verbatim on `[DC-4]`. `[E-86]` |
| **QA-RES-25** | [ADMIN] | **NEGATIVE.** **Given** a SKU whose `[L-M3]` header Reserved exceeds its `Total`, **Then** a red integrity banner renders inside the modal and release remains possible so the operator can correct downward. `[E-87]` `[E-62]` |
| **QA-RES-26** | [ADMIN] | **NEGATIVE.** **Given** an `[L-M4]` memo `@mention`ing a user who is not in the Slack workspace, **Then** the comment still posts `[DC-11]`, `[DC-12]` records `result = failed` with reason `unknown_user`, and nothing is blocked or rolled back. `[E-88]` `[PD-4 · OWNER-PENDING]` |

### QA-HIS — Stock History search, cards, badges, chips, pagination

| ID | Tier | Scenario |
|---|---|---|
| **QA-HIS-01** | [WF] | **Given** `#p-search` is the active pane, **Then** the search `select.sel` contains exactly `SKU`, `Product Name`, `Order ID`, `Tracking No`; the term `input.inp` holds `100004819` with placeholder `Enter SKU (e.g. 100004819)`; and the button reads `🔍 Search`. `[L-F1]` |
| **QA-HIS-02** | [ADMIN] | **Given** the production admin, **Then** the same `select` additionally offers `Barcode` as a fifth key, and scanning a product barcode into the term input returns that SKU's history. `[PD-42 · OWNER-PENDING]` |
| **QA-HIS-03** | [WF] | **Given** `#p-search`, **Then** the `🧴 Product Information` card shows `SKU 100004819`, `Name Madecassol Cream 50ml`, `Name KR` rendering `Dongkook` in `<b>` followed by `마데카솔 크림`, `Brand Dongkook`, and `Sourcing Route SMART BUY` as transparent-background bold text. `[L-F1]` `[G-5]` `[G-6]` |
| **QA-HIS-04** | [WF] | **Given** `#p-search`, **Then** the `📍 By Location` card contains **exactly one** `.loc-row` (`A-02-13` / `42`, matching `Total Qty`) and the note `One location per SKU — change locations via the Current Stocks input field`. More than one row is a defect. `[L-14]` `[BR-1]` |
| **QA-HIS-05** | [WF] | **Given** `#p-search`, **Then** the events table header reads `Type, Quantity, Status, Tracking No, Carrier, Location, Order ID, Created At, Auditor` and six body rows exist in this order: `INBOUND +6 PENDING`, `OUTBOUND −2`, `RESERVE −8`, `INBOUND +30`, `ADJUST −1`, `INBOUND +12`. `[L-8]` |
| **QA-HIS-06** | [WF] | **Given** the events table, **Then** the only `tr.pending` row is the `INBOUND +6` row (tracking `12101316464794`, carrier `Coupang`, order `407847`, auditor `Miranti`), it renders an amber background, and its status badge reads `PENDING` while all five others read `CONFIRMED`. `[L-8]` `[E-39]` |
| **QA-HIS-07** | [WF] | **NEGATIVE.** **Given** the `PENDING` row, **Then** it contains **no** `button`, `a`, `input[type=checkbox]`, or any other confirm affordance — Inventory is display-only for PENDING. `[BR-18]` `[PD-41 · OWNER-PENDING]` §9.1 #6 |
| **QA-HIS-08** | [WF] | **Given** the events header, **Then** exactly three `.filterchip` buttons exist reading `All`, `Confirmed`, `Pending confirm`, and only `All` has class `on`. `[L-8]` |
| **QA-HIS-09** | [ADMIN] | **Given** the production admin, **When** `Pending confirm` is clicked, **Then** only PENDING rows remain, `All` loses class `on`, pagination resets to page 1, and **no** event is persisted for the chip click. `[NE-4]` `[E-40]` |
| **QA-HIS-10** | [ADMIN] | **NEGATIVE.** **Given** the wireframe's `.morewarn` notice `⚠ More data available (live screen: pagination not implemented) → add pagination`, **Then** in the production admin that notice does **not** exist and pagination controls render in its place. `[L-9]` §9.1 #13 |
| **QA-HIS-11** | [ADMIN] | **NEGATIVE.** **Given** a result set fitting on one page, **Then** pagination controls render **disabled**, not hidden; on the last page, next/last are disabled; a new event appended while a page is open does not reshuffle the visible page. `[E-40]` |
| **QA-HIS-12** | [ADMIN] | **NEGATIVE.** **Given** a search for a SKU with no events, **Then** all three cards and the events table render explicit empty states and no stale content from the previous search remains anywhere. `[E-37]` |
| **QA-HIS-13** | [ADMIN] | **Given** each search key in turn, **Then** `SKU` / `Order ID` / `Tracking No` / `Barcode` match exactly, `Product Name` matches partially and case-insensitively across EN and KR names, the placeholder switches with the key, and each executed search persists `[DC-21]` with key type, term, and result count. `[E-38]` |
| **QA-HIS-14** | [ADMIN] | **Given** a tracking number used by both an inbound and an outbound movement, **Then** both are returned and each is labelled by movement type — the two namespaces may legitimately coincide. `[E-63]` `[PD-8 · OWNER-PENDING]` |
| **QA-HIS-15** | [WF] | **Given** the events table, **Then** every `Created At` cell matches the fixture's compact form `MM-DD HH:MM` (`07-13 09:12`, `07-12 18:40`, `07-12 11:05`, `07-10 14:22`, `07-09 16:50`, `07-08 10:11`). This is a wireframe width fixture, not the production contract — see `QA-HIS-16`. `[E-71]` |
| **QA-HIS-16** | [ADMIN] | **Given** the production admin, **Then** every list timestamp renders KST as `YYYY-MM-DD HH:MM`, audit-session detail renders `HH:MM:SS`, and no relative time ("2 hours ago") appears anywhere on the page. `[BR-32]` `[E-71]` |
| **QA-HIS-17** | [ADMIN] | **Given** the `INBOUND +6` PENDING row is open on this page, **When** it is confirmed on View Orders State 6, **Then** on the next fetch its badge reads `CONFIRMED` and the amber highlight clears, `[DC-16]` is rendered here but was emitted by the other screen, and **at no point** does a confirm affordance appear on this page. `[E-89]` `[BR-18]` |
| **QA-HIS-18** | [WF] | **Given** the events table, **Then** the `Type` badge census is `INBOUND` ×3 (class `ty-in`), `OUTBOUND` ×1 (`ty-out`), `RESERVE` ×1 (`ty-res`), `ADJUST` ×1 (`ty-adj`), and the `ADJUST −1` row carries the `diff-neg` class on its quantity. `[L-8]` |

### QA-FRM — Inbound and Outbound forms

| ID | Tier | Scenario |
|---|---|---|
| **QA-FRM-01** | [WF] | **Given** the sub-tab `Inbound Stock` is clicked so `#p-inbound` is active, **Then** exactly five `.fld` fields exist labelled `SKU *`, `Quantity *`, `Tracking No`, `Carrier`, `Order ID (optional)`; the `Carrier` select offers `Coupang`, `Deleo`, `Direct`; and the submit button reads `＋ Record Inbound`. `[L-F2]` |
| **QA-FRM-02** | [WF] | **NEGATIVE.** **Given** `#p-inbound` and `#p-outbound`, **Then** **no** field labelled `Location` exists on either form (removed 2026-07-22 under one-location-per-SKU). `[BR-17]` §9.1 #2 |
| **QA-FRM-03** | [WF] | **STALE-COPY CENSUS — asserts the shipped wireframe, not the contract.** **Given** `#p-inbound`, **Then** the `.form-note` reads exactly `Record a warehouse inbound directly, without a specific order (return restock · manual inbound). Location auto-applies the SKU's single registered location. For order-linked inbound, use Request Inbound on View Orders / the order detail.` — **the final sentence is a wireframe defect `[INV-WFX-2 · proposed]`**: `Request Inbound` is a retired control name and exists on neither named page. The production copy is asserted by `QA-FRM-20`. Report the mismatch against the wireframe backlog, never against this spec. `[L-F2]` §3.18 |
| **QA-FRM-04** | [ADMIN] | **Given** SKU `100004819` (location `A-02-13`), **When** the operator enters Quantity `6`, Carrier `Coupang`, and clicks `＋ Record Inbound`, **Then** a green toast reads `Inbound recorded — SKU 100004819 +6`; `Total` goes `42 → 48`; a `CONFIRMED` `INBOUND` row appears with location `A-02-13` auto-applied and carrier `Coupang`; `[DC-1]` persists with `total 42 → 48`, actor, and timestamp; and the page does not reload `[G-2]`. |
| **QA-FRM-05** | [ADMIN] | **NEGATIVE.** **When** an unknown SKU is submitted, **Then** it is rejected before any write with `Unknown SKU — {value}`, no movement exists, and `[DC-27]` persists with the attempted payload. `[E-41]` |
| **QA-FRM-06** | [ADMIN] | **NEGATIVE.** **When** Quantity is `0`, `−3`, or `abc`, **Then** inline validation blocks submission with `Quantity must be a positive whole number` and no event is written. `[E-42]` |
| **QA-FRM-07** | [ADMIN] | **Given** SKU `100038120` (no registered location), **When** an inbound of `4` is recorded, **Then** it succeeds, the row remains `Unassigned`, and the toast reads `Inbound recorded — 100038120 +4 · location unassigned, please assign it`. The View Orders location gate `[PD-13 · OWNER-PENDING]` does not apply to this form. `[E-43]` |
| **QA-FRM-08** | [WF] | **Given** the sub-tab `Outbound Stock` is clicked so `#p-outbound` is active, **Then** five fields exist in the same order as `[L-F2]`, the `Carrier` select offers `Deleo`, `YUN`, `Coupang`, the button reads `－ Record Outbound`, and the `.form-note` reads exactly `Record a warehouse outbound directly. Location auto-applies the SKU's registered location; outbound exceeding Available Qty is blocked.` `[L-F3]` |
| **QA-FRM-09** | [ADMIN] | **NEGATIVE.** **Given** SKU `100004819` with `Total 42 / Reserved 8 / Available 34`, **When** Quantity `35` is submitted, **Then** submission is rejected with `Outbound blocked — exceeds Available Qty (34)`, no `OUTBOUND` event is created, `Total`/`Reserved`/`Available` are unchanged, and `[DC-20]` persists `attempted 35 vs available 34`. Checking against `Total` instead of `Available` is the defect this test exists to catch. `[E-44]` `[E-45]` `[BR-16]` |
| **QA-FRM-10** | [ADMIN] | **BOUNDARY.** **When** the quantity is corrected to `34` and submitted, **Then** a green toast confirms, `Available` becomes `0`, `Total` becomes `8`, `Reserved` stays `8`, and exactly one `[DC-2]` event exists (qty `−34`, carrier `Deleo`, location `A-02-13`). |
| **QA-FRM-11** | [ADMIN] | **Given** the Outbound form, **When** `－ Record Outbound` is clicked, **Then** the `[G-3](a)` send sound plays. `[PD-2 · OWNER-PENDING]` §6.5 |
| **QA-FRM-12** | [ADMIN] | **NEGATIVE.** **When** `＋ Record Inbound` is clicked, **Then** **no** send sound plays, and no TTS utterance occurs anywhere on this page. `[G-3]` §6.5 |
| **QA-FRM-13** | [ADMIN] | **NEGATIVE.** **When** either submit button is double-clicked within the debounce window, **Then** exactly one movement event exists. `[E-46]` `[G-9]` |
| **QA-FRM-14** | [ADMIN] | **NEGATIVE.** **Given** the network fails on submit, **Then** no phantom movement is created and an idempotent retry produces exactly one event. `[E-47]` |
| **QA-FRM-15** | [ADMIN] | **NEGATIVE.** **When** a non-existent `Order ID` is entered, **Then** the submission is rejected with `Order {id} not found` before any write. `[E-48]` |
| **QA-FRM-16** | [ADMIN] | **NEGATIVE.** **When** a `Tracking No` already present on another movement is entered, **Then** a non-blocking warning `Tracking {no} already recorded on {date} — record anyway?` requires explicit confirmation before the write proceeds. `[E-49]` |
| **QA-FRM-17** | [ADMIN] | **NEGATIVE.** **Given** a SKU whose `Available` is `0`, **When** any outbound quantity ≥ 1 is submitted, **Then** it is blocked with `Outbound blocked — exceeds Available Qty (0)` and `[DC-20]` persists. `[E-91]` |
| **QA-FRM-18** | [ADMIN] | **Given** an audit session is open and SKU `100004819` is in its scope, **When** an inbound of `6` is recorded on `[L-F2]`, **Then** the movement is **not** blocked, `[DC-1]` persists, and at `[L-M1]` Confirm that row's `Diff` is recomputed against the new system quantity with the recalculation toast. `[E-90]` `[E-22]` |
| **QA-FRM-19** | [WF] | **NEGATIVE.** **Given** both form panes, **Then** each exposes exactly one `Carrier` `<select>` that the operator chooses from, and neither form contains any read-only, disabled, or auto-populated carrier control. Automatic carrier capture is not supported anywhere in WMS 2.0. `[BR-33]` `[PD-9 · OWNER-PENDING]` |
| **QA-FRM-20** | [ADMIN] | **NEGATIVE.** **Given** the production admin on the Inbound Stock tab, **Then** the `.form-note` reads exactly `Record a warehouse inbound directly, without a specific order (return restock · manual inbound). Location auto-applies the SKU's single registered location. For order-linked inbound, use the row Inbound buttons on View Orders or Order Detail.`; **and** the string `Request Inbound` appears **nowhere** in the rendered page in any pane or modal — it is a retired control name. Following the note must land the operator on a control that exists. `[L-F2]` `[INV-WFX-2 · proposed]` §3.18 |

### QA-COM — Comments hub

| ID | Tier | Scenario |
|---|---|---|
| **QA-COM-01** | [WF] | **Given** the page is loaded, **Then** the nav button reads `💬 Comments` and carries a red `.badge-n` reading `3`; **When** clicked, **Then** `#inbox1` gains class `open`, the `@ Mentions` tab has class `on`, and exactly three `.it.unread` entries render for orders `409112`, `407847`, `407506`. `[L-16]` |
| **QA-COM-02** | [WF] | **Given** `#inbox1` is open, **When** the agent clicks the `★ Saved` tab, **Then** the mentions pane hides, the saved pane shows exactly one entry (Order `407847`), and its pane header reads `Saved comments · Click to open the order`. `[NE-11]` |
| **QA-COM-03** | [WF] | **Given** `#inbox1` is open on `@ Mentions`, **Then** the Order `407847` entry's `.star` already carries class `on` while the `409112` and `407506` stars do not; **When** the agent clicks the `409112` entry's `★`, **Then** it gains class `on`; **When** clicked again, **Then** it loses it. |
| **QA-COM-04** | [WF] | **Given** `#inbox1` is open, **When** the agent types `phantom` into the search input, **Then** the `.tabs` bar is hidden, a result pane appears whose header reads exactly `1 results · newest first · click to open the order`, exactly one `.it` renders (Order `409112`), and the substring `phantom` is wrapped in `<mark>`. |
| **QA-COM-05** | [WF] | **NEGATIVE.** **When** the agent types `zzzz` into the comment search, **Then** the result pane's `.empty` node reads **exactly** `No matching comments`, and immediately above it the `.paneheader` reads exactly `0 results · newest first · click to open the order`. *Do not assert "exactly" on the whole pane: the wireframe's `cSearch()` always emits the results header and then either the hits or the empty state, so the pane's own `innerText` is two lines.* **When** the query is cleared, **Then** the `.tabs` bar reappears and the previously active pane is restored. `[E-50]` |
| **QA-COM-06** | [ADMIN] | **When** `Mark all read` is clicked, **Then** the nav `.badge-n` is **removed or hidden — never rendered as `0`** `[E-93]`, the three entries lose their unread styling, and `comment.mark_all_read` `[DC-23]` persists per user. *(This is the same rendering `QA-COM-13` files as a defect; the two scenarios must not disagree.)* `[E-93]` `[DC-23]` |
| **QA-COM-07** | [ADMIN] | **When** a `★` is toggled, **Then** `comment.starred` or `comment.unstarred` `[DC-22]` persists per user, and the `★ Saved` list reflects it on reopen. |
| **QA-COM-08** | [ADMIN] | **Given** a hub entry whose entity is an unrecognized-pool item, **When** it is clicked, **Then** the tracking-missing page opens focused on that pool row; **Given** the item is already resolved, **Then** the matched order opens instead. `[E-56]` `[PD-67 · OWNER-PENDING]` |
| **QA-COM-09** | [ADMIN] | **When** a comment search is executed, **Then** `comment.search_executed` `[DC-33]` persists with the term and result count. |
| **QA-COM-10** | [ADMIN] | **NEGATIVE.** **Given** any comment in the hub or in an order's history reached from this page, **Then** no edit and no delete control exists. `[BR-23]` `[PD-3 · OWNER-PENDING]` §9.1 #12 |
| **QA-COM-11** | [ADMIN] | **Given** a comment authored from this page containing an `@mention`, **Then** `comment.posted` `[DC-11]` and `comment.mention_notified` `[DC-12]` both persist — names byte-identical to the canonical list — and the Slack payload carries entity no., text, time, author, mentioned user, and a deep link. `[G-7]` §6.1 |
| **QA-COM-12** | [WF] | **Given** `#inbox1` is open, **When** the agent types `Dean` into the search input, **Then** the header reads `2 results · newest first · click to open the order` and the entries appear newest-first: Order `409112` then Order `407812`. |
| **QA-COM-13** | [ADMIN] | **NEGATIVE.** **Given** a user with zero unread mentions, **Then** the nav badge is **hidden** rather than rendered as `0`, and the `@ Mentions` pane shows an explicit empty state. `[E-93]` |
| **QA-COM-14** | [WF] | **NEGATIVE.** **When** the agent types `<b>x</b>` into the comment search, **Then** no bold element is created inside the result pane — the term is HTML-escaped and rendered as literal text. `[E-94]` |
| **QA-COM-15** | [ADMIN] | **Given** a comment whose text is Korean, **When** a Korean substring is searched, **Then** it matches; no normalization decomposes Hangul and breaks the match. `[E-95]` |

### QA-EXP — Export

| ID | Tier | Scenario |
|---|---|---|
| **QA-EXP-01** | [WF] | **Given** the page header, **Then** a `button` reads exactly `⬇ Export Stock Status`; **Given** `#p-current`'s `.cs-controls`, **Then** a `button` reads exactly `⬇ Export`. Both are grey (`btn-gray`). `[L-F4]` |
| **QA-EXP-02** | [ADMIN] | **Given** filters `line = B` and `route = WHOLESALE`, **When** `⬇ Export` is clicked, **Then** the downloaded file contains only the matching rows and `export.generated` `[DC-19]` persists with the full filter state, the sort, the row count, actor, and timestamp. |
| **QA-EXP-03** | [ADMIN] | **Given** audit mode is active, **When** `⬇ Export` is clicked, **Then** the three audit columns are included, the session id appears in the filename, and `[DC-19]` records `audit-mode = true`. `[E-54]` |
| **QA-EXP-04** | [ADMIN] | **NEGATIVE.** **Given** a filter matching zero rows, **When** an export is run, **Then** a headers-only file is produced and a non-green toast reads `Exported 0 rows`. `[E-1]` `[E-2]` |
| **QA-EXP-05** | [ADMIN] | **NEGATIVE.** **When** an export button is clicked three times in rapid succession, **Then** exactly three jobs and exactly three `[DC-19]` events exist — never six from double-firing `[G-9]` — and a long-running export shows a non-green `Preparing export…` toast without refreshing the page `[G-2]`. `[E-92]` |
| **QA-EXP-06** | [ADMIN] | **Given** filters restricting Current Stocks to one row, **When** `⬇ Export Stock Status` (page header) is clicked, **Then** the file contains the **whole** projection, not the filtered row — the header export ignores the toolbar filters while `⬇ Export` honours them. `[L-F4]` |

### QA-GLB — global-rule negatives applied across the page

| ID | Tier | Scenario |
|---|---|---|
| **QA-GLB-01** | [ADMIN] | **Given** each confirming action in turn — location save, location clear, barcode register, `＋ Record Inbound`, `－ Record Outbound`, `[L-M1]` Confirm, `[L-M4]` Confirm, `Start Stock Audit`, `Exit Stock Audit`, `Mark all read`, both Exports — **Then** each produces a top-right toast, green on success and red on failure. A missing toast is a failure. `[G-2]` |
| **QA-GLB-02** | [ADMIN] | **NEGATIVE.** **Given** each of the same actions, **Then** no full-page refresh occurs — the document is not re-navigated, scroll position survives, and any in-progress audit counts survive. `[G-2]` |
| **QA-GLB-03** | [ADMIN] | **NEGATIVE.** **Given** each confirming action, **When** its control is double-clicked within the debounce window, **Then** exactly one server-side effect exists — client debounce **and** server idempotency key, both present. `[G-9]` |
| **QA-GLB-04** | [ADMIN] | **Given** every mutating action on this page, **Then** the persisted event carries a resolved actor identity — never `null`, never a shared service account. `[G-8]` `[G-15]` `[PD-1 · OWNER-PENDING]` |
| **QA-GLB-05** | [ADMIN] | **NEGATIVE.** **Given** Slack is unreachable, **Then** no primary action anywhere on this page is blocked or rolled back. `[PD-4 · OWNER-PENDING]` `[BR-30]` |
| **QA-GLB-06** | [ADMIN] | **NEGATIVE.** **Given** the session expires while `[L-M1]` or `[L-M4]` is open, **When** Confirm is pressed, **Then** the action fails safe with a red toast and a re-auth prompt, nothing partial is written, and an open audit session remains recoverable by the same auditor. `[E-57]` |
| **QA-GLB-07** | [ADMIN] | **NEGATIVE.** **Given** each declared NON-event `[NE-1]` – `[NE-13]` performed in turn — sub-tab switch, wf-bar click, filter/sort change, chip select, page change, `[L-M1]` cancel, `[L-M4]` cancel, opening `[L-M2]`/`[L-M2b]`/`[L-15]`, typing in `#auSearch` without selecting, re-committing an unchanged `.loc-in`, hub tab switch, audit render toggle, global-nav click `[L-F5]` — **Then** **no** event row is written for it. |
| **QA-GLB-08** | [WF] | **NEGATIVE.** **Given** every pane, **Then** all three clauses hold. **(1)** No live scan-feed list: zero elements whose `id` or `class` matches `/scan\|feed/i`. **(2)** No scan counter: zero occurrences of `/scan/i` in the normalised `innerText` of any `.pane` or `.overlay`. **(3)** No self-refocusing input: focus the `.bcin` of SKU `100024743`, type `8809738317481`, press `Enter` — then assert `document.activeElement` is **not** that input and **not** any other `.bcin`; repeat with `#auSearch` in audit mode (type `zzzz`, press `Enter`) and assert the same. A scan loop is defined here as *focus returning to a barcode-class input without a user gesture*; a plain input merely **retaining** focus is not a scan loop and is not what this test forbids. `[G-1]` is scoped to View Orders and Closing; the `.bcin` and search inputs accept keyboard-wedge input but are not a scan loop. §9.1 #11 |
| **QA-GLB-09** | [WF] | **NEGATIVE.** **Given** the whole page including all six modals, **Then** every Hangul run in the normalised `innerText` is a substring of one of the **17 allow-listed strings enumerated in §8.0** (11 Current Stocks `Product Name KR` values + 5 `[L-13]` catalogue names + the data string `신규`), and nothing else. Any Hangul appearing inside a `th`, `label`, `button`, `h2`, `h4`, `.paneheader`, or `.form-note` is Korean UI chrome and fails this test outright. Baseline: the shipped wireframe's only non-product Korean is `신규`. `[G-6]` |
| **QA-GLB-10** | [ADMIN] | **Given** operator B has Current Stocks open, **When** operator A confirms an audit, **Then** B's `Total`/`Available` update within the configured sync interval and B cannot commit a write based on the stale value — the server revalidates at confirm and rejects. `[E-96]` `[PD-6 · OWNER-PENDING]` |
| **QA-GLB-11** | [WF] | **NEGATIVE.** **Given** every **money value** rendered on the page and in all six modals — defined as every `₩` **immediately followed by a digit**, which excludes the bare `₩` in the `Loss (₩)` column header (a currency *label*, not a value) — **Then** each matches `₩` with thousands separators and an explicit sign for non-zero values, and `/\$\|USD/` matches nothing anywhere. Expected census on the shipped file: `+₩15,000` · `+₩46,260` · `+₩61,260` · `₩0` · `−₩15,000` · `−₩17,800` · `−₩28,400` · `−₩36,000` · `−₩61,260` · `−₩128,460`, plus the non-money data string `— (신규)`. `[BR-31]` `[E-72]` |
| **QA-GLB-12** | [WF] | **NEGATIVE.** **Given** every pane and every modal, **Then** no control offers edit, delete, reverse, undo, or re-open on a stock movement, an audit session, an ADJUST event, or a comment. Corrections are always new events. `[BR-23]` `[BR-24]` §9.1 #12 |
| **QA-GLB-13** | [WF] | **NEGATIVE.** **Given** the page loaded at a viewport of `900 × 800` with preflight done, **Then** the **page body never scrolls horizontally** — `document.documentElement.scrollWidth <= document.documentElement.clientWidth` — while the mock's own container does: `.mockwrap` computes `overflow-x: auto` and its `scrollWidth` exceeds its `clientWidth` (`.mock` is `min-width: 1140px`). **And** no column is dropped responsively: the Current Stocks header still exposes all eleven visible `th` from `QA-CS-14`'s census, `Available` among them. `[E-70]` |
| **QA-GLB-14** | [ADMIN] | **Given** the production admin at a narrow viewport with a product whose `Product Name KR` and whose location code both exceed their column width, **Then** each cell truncates with an ellipsis and exposes the untruncated value on hover via `title` (or an equivalent tooltip); the value **sent on save is the untruncated one**; the `Location` input still accepts and submits the full code; and the sticky table header stays pinned during vertical scroll. `[E-69]` `[E-70]` |

### 8.1 Data-capture traceability

Every `[DC-n]` in §5 has at least one scenario whose **Then** clause asserts the persisted event (not merely its rendering).

| DC | Asserted by | DC | Asserted by |
|---|---|---|---|
| DC-1 | QA-FRM-04, QA-FRM-18 | DC-18 | QA-AUD-24, QA-AUD-43 |
| DC-2 | QA-FRM-10 | DC-19 | QA-EXP-02, QA-EXP-03, QA-EXP-05 |
| DC-3 | **QA-RES-22** (persistence), QA-RES-03 (view) | DC-20 | QA-FRM-09, QA-FRM-17 |
| DC-4 | QA-RES-07, QA-RES-08, QA-RES-24 | DC-21 | QA-HIS-13 |
| DC-5 | QA-RES-07, QA-RES-10 | DC-22 | QA-COM-07 |
| DC-6 | QA-RES-08, QA-RES-10 | DC-23 | QA-COM-06 |
| DC-7 | QA-AUD-07 | DC-24 | QA-AUD-09, QA-AUD-35 |
| DC-8 | QA-AUD-25, QA-AUD-32, QA-AUD-33 | DC-25 | QA-AUD-24 (present), QA-AUD-43 (absent) |
| DC-9 | QA-AUD-25, QA-AUD-38 | DC-26 | QA-AUD-21 |
| DC-10 | QA-AUD-25, QA-AUD-39, QA-LOG-08 | DC-27 | QA-FRM-05 |
| DC-11 | QA-RES-08, QA-COM-11, QA-RES-26 | DC-28 | QA-LOC-05, QA-AUD-20 |
| DC-12 | QA-RES-11, QA-RES-12, QA-RES-26, QA-COM-11 | DC-29 | QA-LOC-10 |
| DC-13 | QA-LOC-02, QA-LOC-06, QA-LOC-16 | DC-30 | QA-RES-20 |
| DC-14 | QA-LOC-03 | DC-31 | QA-RES-15 |
| DC-15 | QA-LOC-09, QA-LOC-15 | DC-32 | QA-AUD-08 |
| DC-16 | QA-HIS-17 (emitted elsewhere, rendered here), QA-HIS-07 (never emitted here) | DC-33 | QA-COM-09 |
| DC-17 | QA-AUD-28, QA-AUD-42, QA-AUD-43 | DC-34 | QA-AUD-37 |
| NON-events `[NE-1]`–`[NE-13]` | QA-GLB-07 (all thirteen), QA-HIS-09, QA-LOC-11, QA-CS-02, QA-CS-17, QA-NAV-12 (`[NE-13]`) | | |

---

## 9. Out of Scope & Open Questions

### 9.1 Explicitly out of scope — and features that must NOT exist

Each entry below was **removed or excluded by a dated decision**. They are recorded here so nobody re-implements them from a stale document, a leftover CSS class, or an older Notion revision. Every one has a matching row in §10 and at least one asserting QA scenario.

| # | Must NOT exist on this page | Removed / excluded | Why | Asserted by |
|---|---|---|---|---|
| 1 | **An `Audit Log` sub-tab.** Past Audit Logs is a **modal** opened from the button beside `Start Stock Audit`. | 2026-07-22 (created and abolished the same day) | UX flow consolidation — the auditor is already looking at the audit banner; a separate tab put history two clicks away from the person who needed it | QA-NAV-07 |
| 2 | **A `Location` field on the Inbound Form or the Outbound Form.** | 2026-07-22 | Direct consequence of one-location-per-SKU `[BR-1]`; location auto-applies. A second place to type a location is a second place to get it wrong | QA-FRM-02 |
| 3 | **The RETURN-BIN concept** — no returns location, no second `By Location` row, no RETURN-BIN filter value. | 2026-07-22 | Returns merge into the SKU's normal location after inspection `[BR-2]` | QA-NAV-08, QA-HIS-04 |
| 4 | **Multiple locations per SKU / a multi-row `By Location` card.** | 2026-07-22 | `[BR-1]` | QA-HIS-04 |
| 5 | **Any Print button, print preview, or print-agent integration.** | 2026-08-03 | `[G-4]` does not land here `[BR-27]`; Export produces files only | QA-NAV-06 |
| 6 | **Any confirm affordance for `PENDING` events** — no button, no link, no checkbox, no context menu. | Provisional 2026-08-03 `[PD-41 · OWNER-PENDING]` | Two confirm paths for one fact `[BR-18]` | QA-HIS-07, QA-HIS-17 |
| 7 | **Photo capture / photo column / image upload.** (The `IMG` thumbnail placeholder is a *display* cell, not an upload control.) | 2026-07-21 deferred → 2026-08-03 resolved by deletion program-wide `[PD-63 · OWNER-PENDING]` | Leaving it "deferred" invites re-implementation; there is no photo capture on Inventory | QA-NAV-08 |
| 8 | **Procurement Hub links, tabs, or embedded views.** | 2026-08-02 (owner: excluded from this program entirely) | Separate future workstream. The only touchpoint is a costing **read** for `[BR-4]` | QA-NAV-08 |
| 9 | **Colored sourcing-route pills.** | Carried from View Orders; reconfirmed 2026-08-03 | `[G-5]` `[BR-9]` | QA-CS-08 |
| 10 | **Sample-set assignment UI or sample columns.** | 2026-07-23 design; reconfirmed 2026-08-03 | `[G-13]` lives on Order Management; Inventory never assigns or displays sample sets | QA-NAV-08 |
| 11 | **A continuous-scan surface** — no scan feed, no auto-focus-return scan loop, no scan counter. | 2026-08-03 | `[G-1]` is scoped to View Orders and Closing. The Barcode and search inputs accept keyboard-wedge scanner input but are not a scan loop | QA-GLB-08 |
| 12 | **Edit / delete / reverse / undo / re-open controls** on audit sessions, ADJUST events, stock movements, or comments. | 2026-07-22 (audit) · 2026-08-03 (comments, `[PD-3 · OWNER-PENDING]`) | `[BR-23]` `[BR-24]` — corrections are new events, never mutations | QA-GLB-12, QA-LOG-07, QA-COM-10 |
| 13 | **The `⚠ More data available (live screen: pagination not implemented)` notice.** | 2026-07-22 (legend 9) | It is the *problem statement*; pagination replaces it `[L-9]` | QA-HIS-10 |
| 14 | **Automatic Carrier capture** on any inbound or outbound event, and any read-only/auto-populated carrier control. | 2026-08-03 (review conflict C-1, `[PD-9 · OWNER-PENDING]`) | Automatic carrier recording is not supported anywhere in WMS 2.0. Stating it here also protects this page's **manual** carrier fields from being stripped by an implementer who reads C-1 as "no carrier anywhere" `[BR-33]` | QA-FRM-19 |
| 15 | **A `Reserved` drill-down on the Current Stocks table.** The reservation modal `[L-6]` opens only from the Stock History `📊 Stock Status` card. | Wireframe design 2026-07-23; stated explicitly 2026-08-03 | A second entry point needs a second phantom predicate and a second read event `[DC-30]`, which is how two divergent phantom definitions get built `[E-97]` | QA-CS-16 |

**Also out of scope (not removals — simply owned elsewhere):** order-linked inbound (View Orders / Order Detail — the Inbound Form note says so explicitly); label and invoice layouts (Phase 3-1, discussed with the owner after Phase 3); unrecognized-barcode matching behavior (specified on `tracking-missing` and `view-orders`; this page only hands off); the inbound-request lifecycle and multi-tracking `[G-10]` `[G-11]`; the role/permission matrix (post-v1, `[G-15]`); the wf-bar demo chrome and the annotation layer (§2.3, §2.4); the **platform session and auth layer** — the global nav's category menus, `Logout`, sign-in, and the session audit record belong to the admin shell, not to Inventory (`[L-F5]` §3.21), which is why no `[DC-n]` on this page describes a session.

### 9.2 Open questions

Per the binding convention (`_review.md` §3 item 8), owner questions that already carry a provisional default live in the PD register and are **not** re-listed as open. This section carries only: NO-DEFAULT items, developer-time decisions, and traceability pointers.

**NO-DEFAULT — no behavior is specified anywhere in this document.**

| ID | Question | Owner | Blocking |
|---|---|---|---|
| **OQ-1** | **Where is the audit `Loss (₩)` product cost sourced from?** The *design* (`Loss = Diff × cost`) was fixed 2026-07-22 and the source explicitly deferred the same day. FIFO lot cost (via the Procurement Hub FIFO COGS ledger) is recommended over latest purchase price, but no decision exists. | Development, with owner sign-off on the costing basis | Blocks the **numeric correctness** of `[L-7]`, `[L-M1]`, `[L-M2]`, `[L-15]`, and `[DC-8]`. Every other behavior in the audit flow can ship without it; the loss column would render `—` until it lands `[E-25]` |

*(No other NO-DEFAULT item belongs to this page. `[PD-51]`, `[PD-55]`, `[PD-66]`, `[PD-71]`, `[PD-74]`, and `[PD-79]` are NO-DEFAULT items owned by other screens and are named here only so a reader does not go looking for them.)*

**Traceability index — owner questions already answered provisionally inside this spec.** Listed so a reversal is mechanical, not re-opened here. Reversing any one means editing the sentences tagged with that ID **on this page** and nothing else.

`[PD-1]` role model (`[BR-28]`) · `[PD-2]` send sound on `－ Record Outbound` (§6.5) · `[PD-3]` append-only comments (`[BR-23]`) · `[PD-4]` Slack failure handling (`[BR-30]`) · `[PD-5]` destructive-action confirms (§3.3 exit, §3.16) · `[PD-6]` stale-entity revalidation (§3 preamble) · `[PD-7]` concurrency (`[E-7]`) · `[PD-8]` tracking namespaces (`[E-63]`) · `[PD-9]` no automatic carrier capture (`[BR-33]`) · `[PD-13]` location-before-inbound boundary (`[E-43]`) · `[PD-22]` JIT residual origin (`[BR-7]`) · `[PD-40]` counted-qty prefill (`[BR-12]`) · `[PD-41]` PENDING display-only (`[BR-18]`) · `[PD-42]` Barcode search key (`[L-F1]`) · `[PD-43]` cost visibility on the floor (`[BR-29]`) · `[PD-44]` single audit session (`[BR-14]`) · `[PD-45]` release on an active order (`[BR-21]`) · `[PD-46]` location 1:1 exclusivity (`[BR-1]`) · `[PD-47]` filtered audits and scope (`[BR-15]`, `[BR-34]`, **`[BR-35]`**, `[E-11]`, `[E-81]`, §3.11 — note that `[BR-35]` **extends** the register's wording, which counts scope rows only; the owner must be asked for the extension, and reversing it changes `SKUs Checked` from scope+additions to scope-only) · `[PD-48]` shortage acknowledgement (`[BR-13]`) · `[PD-49]` under-restock remainder (`[BR-20]`) · `[PD-50]` over-restock cap (`[BR-20]`) · `[PD-63]` photo removal (§9.1 #7) · `[PD-67]` pool-entity comment routing (`[E-56]`) · `[PD-80]` `OTHER` route rendering (`[BR-8]`).

**Developer decisions (no owner input needed).** Each states a default and is dev-owned.

| Area | Decision |
|---|---|
| Costing | The lookup mechanics for OQ-1 once the basis is chosen; a missing cost renders `—` and is excluded from totals (already fixed by `[E-25]`) |
| Pagination | Stock History page size and server-side paging mechanics `[L-9]` |
| Location codes | Validation regex, normalization (case, separators), and the line-derivation parse rule (prefix before the first `-`); the `Unassigned` sort sentinel (the wireframe uses `힣`) |
| Audit drafts | Whether in-progress counts autosave, at what interval, and their retention `[DC-24]` `[E-58]`; the stale-session sweep interval `[E-83]` |
| Export | File format, encoding, and column set for both buttons; whether audit columns are included in audit mode (recommended: yes, with the session id in the filename) `[E-54]`; async threshold for large exports `[E-92]`; the legacy `Export Stock Status` label/route mapping `[L-10]` |
| Autocomplete | Minimum characters, debounce, and result cap for `#auSearch` `[L-13]`; the same for the comments-hub search `[L-16]` |
| Carrier lists | Whether the Inbound (`Coupang`/`Deleo`/`Direct`) and Outbound (`Deleo`/`YUN`/`Coupang`) selects stay fixed lists or read a carrier registry. **Not** whether carrier is auto-captured — that is decided `[BR-33]` |
| Idempotency `[G-9]` | Key format, TTL, client debounce interval, and how a rejected duplicate surfaces |
| Toasts `[G-2]` | Duration, stacking vs single-slot replacement; this spec fixes the copy, dev confirms feasibility |
| Audio `[G-3]` | Synth parameters for the send sound and `AudioContext` resume handling |
| Event capture | Whether `[DC-21]`, `[DC-30]`, `[DC-33]` are captured in full or sampled — sampling must be a documented configuration, never an omission |
| Retention | The UI's live-list retention horizon before paging to cold storage (§5.4) |
| Deep links | URL formats for `[L-M3]` → Order Detail, `[L-13]` → tracking-missing, and comment → entity `[G-12]` |
| Sync | Multi-operator live-sync transport and latency for Current Stocks while an audit is open `[E-96]`; comment freshness (poll vs push) |
| Layout | Sticky-header implementation and truncation/tooltip behavior on the wide table `[E-69]` `[E-70]` — the invariants are asserted (`QA-GLB-13` at `[WF]` tier, `QA-GLB-14` at `[ADMIN]`); only the mechanism is dev's |
| Selectors | The production selector for the `[L-12]` barcode input. It must be **disjoint from** the `[L-13]` autocomplete input — the shipped wireframe gives both `class="bcin"`, which is a class collision, not a contract (§3.8, §3.9, `QA-LOC-08`) |
| Slack | Retry policy for failed deliveries `[PD-4 · OWNER-PENDING]`; whether an audit-confirmed notification is ever added (currently **no route in v1** — inventing one would create an unowned alert stream) |

---

## 10. Decision Log

Every decision that shaped this screen, 2026-07-09 → 2026-08-03, including reversals and removals. Nothing is silently dropped.

| Date | Decision | Type | Source / evidence |
|---|---|---|---|
| 2026-07-09 | WMS 2.0 wireframe program opens. The Stock screen is slated for rework from live-admin captures against Notion planning section **E**. | Scope | Plan ledger `2026-07-09-wms2-wireframes.md` |
| 2026-07-13 | `stock-status` created in the initial nine-screen batch. | Build | commit `1bbba3a` |
| 2026-07-14 | Reworked from **real admin captures**: the live screen is `Stock History` with Search / Inbound / Outbound tabs plus result cards. Those tabs, the event columns, and the search dropdown are carried over verbatim — the origin of `[L-F1]` – `[L-F4]`. | Build | commit `9844fe0`; legend footnote |
| 2026-07-14 | **Outbound is blocked above `Available`, not above `Total`** — carried from the live screen's form note. | Rule | Live screen; `[BR-16]` |
| 2026-07-22 | **Page renamed `Stock Status` → `Inventory`**, and **default landing set to Current Stocks**. "Inventory" is the standard name covering current stock · history · in/outbound. Legacy references (`Export Stock Status`, the `stock-status` route) are mapped during development. | Rename | commit `b19e7de`; legend 10 → `[L-10]` |
| 2026-07-22 | **Current Stocks tab introduced** as a full-list view with Location and Sourcing Route filters — the live screen was lookup-centric (one SKU at a time). Expanded to 10 sample rows. | Feature | commit `e485538`; legend 5 → `[L-5]` |
| 2026-07-22 | **Default sort = `Available` descending** — most sellable stock first; headers re-sortable. | Rule | commit `e485538`; legend 11 → `[L-11]` `[BR-10]` |
| 2026-07-22 | **Current Stocks column set fixed**: SKU / Image / Product Name / Product Name KR / Size / Barcode / Sourcing Route / Location (editable input on every row) / Total / Reserved / Available. | Design | commit `28f0834`; legend 12 → `[L-12]` |
| 2026-07-22 | **REVERSAL — the RETURN-BIN concept is removed.** Returns go to the SKU's normal location after inspection; `By Location` reconciles as `32 + 10 = 42` into one location. | **Reversal / removal** | commit `7da0323`; legend 14 → `[BR-2]`, §9.1 #3 |
| 2026-07-22 | **One location per SKU confirmed.** `By Location` renders a single row; the event history is reconciled to match. | Rule | commit `d8ab95c`; legend 14 → `[L-14]` `[BR-1]` |
| 2026-07-22 | **REMOVAL — the `Location` field is deleted from the Inbound and Outbound forms.** Location auto-applies from the SKU's registered location. | **Removal** | commit `6846738` → `[BR-17]`, §9.1 #2 |
| 2026-07-22 | **Stock Audit mode strengthened**: start re-sorts by location ascending (the walking path, per Notion E "display in location order"); an unregistered-product row is added; a total-loss footer is added. | Feature | commit `b8e1aa4`; legend 7 → `[L-7]` |
| 2026-07-22 | **`Loss = Diff × product cost` fixed as the design; the total targets 0** as the centre manager's KPI. **The cost source is explicitly deferred to development** (FIFO lot cost recommended vs latest purchase price). | Rule + deferral | Plan ledger item E → `[BR-4]`, §9.2 OQ-1 |
| 2026-07-22 | **`[L-M1]` Confirm Audit Differences modal** created: ADJUST list, new additions, Reserved-shortage check, total loss. ADJUST is declared a **book correction, never Inbound/Outbound**. | Feature + rule | commit `7e242db` → `[L-M1]` `[BR-3]` |
| 2026-07-22 | **`Audit Log` created as a sub-tab** — monthly session log with auditor, adjustments, new additions, total loss. | Feature | commit `abd1661` |
| 2026-07-22 | **REVERSAL, same day — the `Audit Log` tab is abolished** and becomes the **Past Audit Logs modal** opened from the button beside `Start Stock Audit`, consolidating the UX flow. | **Reversal / removal** | commit `bea89ec`; legend 15 → `[L-15]`, §9.1 #1 |
| 2026-07-22 | **`[L-M2]` audit-session detail modal** (ADJUST event list: system → counted, adjustment, loss), linked from the session log. | Feature | commit `aff6ff7` |
| 2026-07-22 | **`[L-M2b]` June session variant wired** — 5 ADJUST events (−4 / +1), total `−₩128,460`, reconciled. It exists to show a session that **missed** the loss target. | Feature | commit `0411b6c` |
| 2026-07-22 | Legend dots 11 and 12 moved inline into the table header (they were being clipped by the sticky header + overflow). **Consequence for QA:** those two dots now live *inside* content nodes — see §2.4 and §8.0 preflight. | Presentational | commit `09e3e52` |
| 2026-07-23 | **`[L-13]` unregistered-product autocomplete**: search by **product name**, barcode not required, size shown for disambiguation; no catalog match → hand off to the Unrecognized flow (F). | Feature + rule | commit `d7a5728`; legend 13 → `[BR-25]` |
| 2026-07-23 | **`[L-M3]` Reserved Quantity detail modal** (allocated orders, `SUSPECTED PHANTOM` flag) and **`[L-M4]` Cancel Inbound confirmation** (release + restock yes/no + qty + memo) created. Phantom predicate defined. | Feature + rule | commit `f747346`; legend 6 → `[L-6]` `[BR-19]` `[BR-20]` `[BR-22]` |
| 2026-08-02 | **Comments hub added to this page** — shared across all screens, `@ Mentions` + `★ Saved` + full-text search. | Feature | commit `d88673c`; legend 16 → `[L-16]` `[G-7]` |
| 2026-08-02 | **Procurement Hub excluded from this program entirely** (owner) — no sweep, no English conversion, no spec. | Scope | Handoff ledger; §9.1 #8 |
| 2026-08-03 | **JIT added to the Sourcing Route filter, and a JIT row added to the list.** Order cancellations and mis-delivery returns leave JIT stock behind, so JIT residual stock is listed and filterable. Sample row: `Anua` 하트리프 77% 수딩 토너, route `JIT (Coupang)`. | **Reversal of scope** (routes on this page went 3 → 4) | commit `f8c4bae` (owner judgment items 2 and 10); legend 5 → `[BR-7]` |
| 2026-08-03 | **Korean product names carry the EN brand in bold** across all 72 affected cells. Korean names, carrier names, and company names stay Korean — they are data. | Rule | commit `f8c4bae` (item 5) → `[G-6]` |
| 2026-08-03 | **Location filter groups by line (A / B / C …), and the line list is derived dynamically from registered locations** — never hard-coded. | Rule | commit `d09fe79`; legend 5 → `[BR-6]` `[G-14]` |
| 2026-08-03 | **The audit summary bar is visible only in audit mode** (`#auditSummary` gains class `audcol`), joining the three audit-only columns and the unregistered-product row. | Rule | commit `d09fe79` → `[BR-5]` `[G-14]` |
| 2026-08-03 | **wf-bar modal shortcut buttons added for all six modals**, and they open the modal **without changing pane state**. Wireframe chrome only — must not ship — but it is the QA entry path. | Wireframe behavior | commit `d09fe79` → §2.3, `[E-51]` |
| 2026-08-03 | **Full English conversion** of this page (123 replacements). Korean remains only in product names and the `— (신규)` data string. | Localization | commit `8beb374` |
| 2026-08-03 | **Global: every confirming action shows a top-right toast and nothing refreshes the page** (owner emphasis, all 8 screens). | Global rule | `[G-2]`; applied per-action in §3 |
| 2026-08-03 | **Comment `@mention` channel CONFIRMED: `#fulfillment-admin-comments` (`C0BMGEWM5QA`)**, message body @mentions the person. Supersedes the "pending" wording in the earlier global-rules draft. | Global rule | `_slack-routing.md`; review conflict C-2 → §6.1 |
| 2026-08-03 | **The `[G-3](a)` send sound applies to every outbound-class button on every page**, which brings `－ Record Outbound` on this page into scope. | Global rule (provisional) | `[PD-2 · OWNER-PENDING]`; review conflict C-5 → §6.5 |
| 2026-08-03 | **`[G-4]` instant printing does not land on Inventory** — no Print button; Export produces files only. | Scope | `[BR-27]`, global-rule delta GD-9 (`_plans/_review.md` §4) → §6.4, §9.1 #5 |
| 2026-08-03 | **Automatic Carrier recording is NOT supported anywhere in WMS 2.0.** On this page the consequence is a **boundary, not a removal**: the `Carrier` column and both form selects stay, as manual/carried values, and must never be wired to scan-time capture. | Rule (boundary) | Review conflict C-1, `[PD-9 · OWNER-PENDING]` → `[BR-33]`, §9.1 #14 |
| 2026-08-03 | **v1 ships a single admin role**; no role gating on audit start/confirm, reservation release, or cost visibility; every mutating action records the actor. | Global rule (provisional) | `[G-15]` `[PD-1 · OWNER-PENDING]` → `[BR-28]` |
| 2026-08-03 | **Inventory is display-only for `PENDING` events**; confirmation belongs to View Orders State 6 / the Inbound Request lifecycle. No confirm affordance may be added here. | Rule (provisional) | `[PD-41 · OWNER-PENDING]` → `[BR-18]`, §9.1 #6 |
| 2026-08-03 | **Location exclusivity extended to 1:1** — one location per SKU **and** one SKU per location; assigning an occupied location is blocked naming the occupant. | Rule (provisional) | `[PD-46 · OWNER-PENDING]`, global-rule delta GD-7 (`_plans/_review.md` §4) → `[BR-1]` |
| 2026-08-03 | **Exactly one active audit session per warehouse**, single auditor of record; a second Start is blocked. | Rule (provisional) | `[PD-44 · OWNER-PENDING]` → `[BR-14]` |
| 2026-08-03 | **Filtered / partial audits are allowed**; the session records its scope, and the scope is **frozen at start** — a mid-session filter change never changes what is committed. | Rule (provisional) + page rule | `[PD-47 · OWNER-PENDING]` → `[BR-15]`, `[BR-34]`, `[E-66]` |
| 2026-08-03 | **`SKUs Checked` = scope rows + rows added via `[L-13]`.** | Rule | `[BR-35]`, `[E-81]` |
| 2026-08-03 | **An audit session belongs to its START date**, even when confirmed after midnight. | Rule | `[BR-36]`, `[E-80]` |
| 2026-08-03 | **The Reserved-shortage gate is unlocked by an acknowledgement checkbox** (`Reviewed with the order team`), persisted with the session — not by resolving every shortage. | Rule (provisional) | `[PD-48 · OWNER-PENDING]` → `[BR-13]` |
| 2026-08-03 | **Restock Qty bounds fixed**: capped above at the inbounded qty (blocked); open below it, with the remainder auto-recorded as `ADJUST(−remainder)`; `0` with `Yes` selected is blocked as a mislabelled write-off. | Rule (provisional) | `[PD-49]` / `[PD-50 · OWNER-PENDING]` → `[BR-20]`, `[E-85]` |
| 2026-08-03 | **Cancel Inbound is allowed on an ACTIVE (`processing`) order** with an extra confirmation naming the order. | Rule (provisional) | `[PD-45 · OWNER-PENDING]` → `[BR-21]` |
| 2026-08-03 | **`Counted Qty` prefill is kept** (wireframe is SST); the confirmation-bias risk is recorded for the owner rather than silently reversed, and `[DC-24]` makes an untouched row distinguishable in the data even though the UI does not mark it. | Rule (provisional) | `[PD-40 · OWNER-PENDING]` → `[BR-12]`, `[E-12]` |
| 2026-08-03 | **`Loss (₩)` and product cost stay visible to whoever runs the audit** — no admin-only split in v1. | Rule (provisional) | `[PD-43 · OWNER-PENDING]` → `[BR-29]` |
| 2026-08-03 | **`Barcode` added as a 5th Stock History search key**, so an operator holding a product can scan to look it up. | Feature (provisional) | `[PD-42 · OWNER-PENDING]` → `[L-F1]` |
| 2026-08-03 | **`OTHER` becomes a sourcing-route value downstream**, rendered black bold as `OTHER ({channel})` — including in this page's route filter. The Inbound Request form has offered the free-text OTHER channel since 2026-07-26. | Rule (provisional) | `[PD-80 · OWNER-PENDING]`, global-rule delta GD-2 (`_plans/_review.md` §4) → `[BR-8]` |
| 2026-08-03 | **Comments are append-only** program-wide; this page adds no edit or delete affordance. | Rule (provisional) | `[PD-3 · OWNER-PENDING]` → `[BR-23]` |
| 2026-08-03 | **Photo capture is permanently removed**, not deferred — no photo column, no upload, on this page or any other. The `IMG` thumbnail is a display placeholder, not an upload control. | **Removal** (provisional) | `[PD-63 · OWNER-PENDING]` → §9.1 #7 |
| 2026-08-03 | **`[G-1]` scanner protocol is scoped to View Orders and Closing.** Inventory accepts keyboard-wedge scanner input on its barcode and search fields but is not a continuous-scan surface. | Scope | Mandatory-item matrix, `_review.md` §2b → §9.1 #11 |
| 2026-08-03 | **Money on this page is KRW (`₩`)** and timestamps are **KST**, `YYYY-MM-DD HH:MM` (seconds in session detail), with no relative times. Declared explicitly so the org-wide USD reporting convention is not applied to this operational ledger. | Rule | `[BR-31]` `[BR-32]`, `[E-71]` `[E-72]` |
| 2026-08-03 | **The `Reserved` drill-down has exactly one entry point** — the Stock History `📊 Stock Status` card. The Current Stocks `Reserved` cell is plain text. | Rule | `[E-97]`, §9.1 #15 |
| 2026-08-03 | **Wireframe defect `[WF-14]` logged**: `m-auditlog` and `m-adjlog6` carry no legend dots. Optional annotation only; declared in §2.1 so coverage checks do not flag a phantom hole. | Wireframe backlog | `_wireframe-fixes.md` |
| 2026-08-03 | **Audit finding recorded**: the wireframe deliberately seeds two non-matching `Counted Qty` values (SKU `100005104` `17`/`18`, SKU `100012534` `11`/`9`) to demonstrate Diff and Loss. A blanket "every count equals Total" assertion is wrong against the shipped file; `QA-AUD-04` states the census exactly and `QA-AUD-05` carries the production rule. | QA correction | §3.3 fixture note, §8 |
| 2026-08-03 | **Audit finding recorded**: legend dots `11`, `12`, `13` are rendered inside content nodes, so `textContent` assertions read `Location12` / `Available11`. §8.0 preflight now mandates `Hide annotations` + `innerText`. | QA correction | §2.4, §8.0 |
| 2026-08-03 | **`[L-F5]` Global nav + signed-in identity added as the fifth page-furniture unit.** The legend footnote names five carried-over units; four were keyed and the nav was silent. It is the actor source for every `[G-8]` event, so it is now specified (§3.21) with a NON-event declaration `[NE-13]` and two scenarios. Unit total 20 → 21. | Coverage fix | Coverage audit D1; sibling pattern `ready-to-outbound [L-F8]` |
| 2026-08-03 | **`BR` ID re-assignment declared, not hidden.** The `BR` family was remapped off `stock-status.A.md` when 20 rules were added; the mapping is now stated under the §4 heading so the "never renumber" convention is auditable. No further renumbering. | Convention correction | `_review.md` §3 item 2 |
| 2026-08-03 | **Page-local event names normalised to two-segment `entity.action`** (20 renames, e.g. `audit.session.confirmed` → `audit.session_confirmed`, `comment.search.executed` → `comment.search_executed`). No `[DC-n]` ID changed. The hub-search name now matches View Orders byte for byte. | Convention correction | `_review.md` §3 item 3; cross-page audit D14 |
| 2026-08-03 | **`[BR-35]` flagged as an extension of `[PD-47]`, not a restatement.** The register's PD-47 defines `SKUs Checked` as scope rows only; this page counts scope rows **plus** `[L-13]` additions. Tagged at `[BR-35]`, `[E-81]`, §3.11, `QA-AUD-40` and indexed in §9.2 so the owner is asked for the extension, and so reversal stays mechanical. | Provisional-decision hygiene | `[PD-47 · OWNER-PENDING]`; coverage audit D2 |
| 2026-08-03 | **Wireframe defect `[INV-WFX-1 · proposed]` logged**: `#m-adjust`'s total note hard-codes *"the 3 new additions"* while the modal holds one `[NEW]` row and `[L-15]` records `New Additions 1`. Spec contract is templatised `{n}`; `QA-AUD-23` pins the stale string at `[WF]` tier, `QA-AUD-44` the contract at `[ADMIN]`. | Wireframe backlog | `_wireframe-fixes.md`; adversarial QA item 5 |
| 2026-08-03 | **Wireframe defect `[INV-WFX-2 · proposed]` logged**: the Inbound Form note sends the operator to **`Request Inbound`**, a retired control that exists on neither View Orders nor Order Detail. Corrected copy specified in §3.18; `QA-FRM-03` pins the stale string at `[WF]` tier, `QA-FRM-20` the corrected copy at `[ADMIN]`. | Wireframe backlog | `_wireframe-fixes.md`; cross-page audit D9 |
| 2026-08-03 | **QA determinism pass.** §8.0 gained the `innerText` normalisation rule (step 3b), the *reads* vs *reads exactly* convention, a DOM-visibility definition, a colour-token table with rgb values, and the 17-string Korean allow-list; `QA-LOC-08`, `QA-COM-05`, `QA-COM-06`, `QA-NAV-07`, `QA-LOC-18`, `QA-AUD-22`, `QA-GLB-08`, `QA-GLB-09`, `QA-GLB-11` were rewritten to remove every judgement call. | QA correction | Adversarial QA execution, items 1–13 |
| 2026-08-03 | **Cross-page conflicts declared without changing this page's behavior**: the three incompatible Cancel Inbound contracts (§3.16), the six non-identical Comments-hub strings and the comment-search capture disagreement (§3.12), the `＋`/`－` fullwidth glyph contract vs `[G-3]`'s `−` (§3.18), and the `[GD-n]` citations' source file (`[BR-1]`, §10). Each names the owed reconciliation instead of silently diverging. | Cross-page hygiene | Cross-page audit D1 / D7 / D12 / D13 / D14 |

---

*End of specification. 21 implementation units (16 legend + 5 page furniture) · 36 business rules · 34 data-capture events + 13 declared non-events · 98 edge cases · 200 QA scenarios (75 [WF] / 125 [ADMIN], 85 negative/boundary = 42.5%) · 25 provisional decisions applied · 1 NO-DEFAULT open question · 2 wireframe defects raised (`[INV-WFX-1 · proposed]`, `[INV-WFX-2 · proposed]`).*





