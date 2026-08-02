# Inbound Request — Screen Specification

Slug: `inbound-request` · Wireframe SST: `wms2/inbound-request/index.html` (851 lines, v1) · Live: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/inbound-request/
Spec version 1.1 · 2026-08-03 · Companion: `_global-rules.md` (cited as `[G-n]`), `_plans/_provisional-decisions.md` (cited as `[PD-n · OWNER-PENDING]`), `_plans/_wireframe-fixes.md` (cited as `WF-n`), `_plans/_review.md` (adjudications `C-n`, conventions §3).

Reading contract: this document is written to be executed end-to-end by an AI QA agent and implemented by a developer with zero ambiguity. Global rules are **cited, never restated** — only this page's deltas appear here. Korean strings (product names, supplier names) are **data** and appear verbatim [G-6]. All UI copy in backticks is byte-accurate to the wireframe.

---

## 1. Purpose & Users

### 1.1 What this screen is

**Inbound Request is the single intake gateway for everything that enters the warehouse** (legend `[L-S1-1]`). Every physical arrival — Smart Buy stock replenishment, bulk Wholesale shipments, Brand Partnership sponsorship stock, and anything else — is declared here *before* it arrives. There is no second creation path: an arrival with no matching request does not get registered ad hoc, it falls into the shared unrecognized pool on the Unrecognized Tracking screen (`tracking-missing`) and is recovered by creating a request here (2026-08-02 decision; `[BR-19]`).

The screen has two halves that mirror the two halves of the physical inbound loop:

| Half | Screen | Who | Physical situation |
|---|---|---|---|
| Declaration (desk) | **This page** | Order team / procurement staff | Seated, keyboard + mouse, supplier PO or quote open on a second screen or on paper |
| Reception (floor) | View Orders **State 6 / 6b** | Warehouse center staff | Standing at the receiving bench, barcode scanner in hand, gloves on, 40–60 cm from the monitor, several boxes deep in a queue |

The desk half **declares intent and identity** (what is coming, from whom, how much, at what cost, under which tracking numbers). The floor half **records physical fact** (what actually arrived, when, into which location). This spec owns the desk half and the *display* of whatever the floor half writes back.

### 1.2 Users

- **Requester** — order team / procurement staff (demo actors: Yongwon, Dean, Miranti). Creates requests, adds tracking numbers after dispatch, chases missing tracking numbers, comments.
- **Warehouse center staff** — never operate this screen. They appear here only as the *cause* of status transitions written from View Orders scans. There is no control on this page that a center operator needs.
- **Everyone with admin access** — v1 ships a single admin role with no gating on any control on this page; every mutating action records the actor `[PD-1 · OWNER-PENDING]` [G-15] [G-8].

### 1.3 Operational moments served

1. **Before dispatch** — a purchase is placed; the requester declares it (route, SKUs, quantities, unit cost, JIT price, supplier, expected arrival). Tracking number is usually unknown at this point.
2. **At dispatch** — the supplier's dispatch email arrives, often with **several tracking numbers pasted in one block** (split shipments). The requester opens `[L-M1]` and enters them; matching activates immediately.
3. **In transit** — requests still in `REQUESTED` with no tracking number are chased **by push, not by poll**: a once-a-morning automated Slack check posts them into the channel where the responsible team already lives (`[L-S3-6]`).
4. **On arrival** — the center scans the tracking barcode in View Orders. Status flips to `PARTIAL` or `INBOUNDED` here **automatically**. The desk observes; it never asserts.
5. **After arrival** — quantity disputes, damage, arrival slips and forklift notes travel as comments on the request, with `@mention` Slack pushes [G-7], so the request stays the single thread of record.

### 1.4 Physical reality that shaped specific decisions

Write these into the implementation; each one exists because of a body at a desk or a body on a floor.

- **One focus point for batch entry** `[L-S1-5]`. The requester is transcribing a supplier PO line by line while looking away from the screen. Per-row search boxes (the pre-2026-07-27 design) forced a mouse trip per line. A **single unified search box above the table** means the loop is: type → click a suggestion → type Qty → type Unit Cost → back to the box. **Focus must return to the search box after a row is appended**, and Tab order inside a new row is Order Qty → Unit Cost → JIT Price (`[BR-24]`).
- **Enter must never submit** `[L-S1-5]`. The requester's hands live on the keyboard and the search box is the most-typed field on the page. An accidental Enter that registers a half-filled request would create a live inbound record and burn an Inbound No. This is the page's only [G-1]-adjacent delta — there is no scanner here, but the Enter-key discipline is the same discipline.
- **Locked catalog cells** `[L-S1-6]`. SKU No., Brand and Product Name are rendered as borderless plain text and cannot be typed into. A mistyped SKU would poison FIFO costing, the Procurement Hub sheet, and View Orders matching simultaneously. Correction is delete-the-row-and-search-again, which is deliberately a bit slower than editing.
- **One screen, no scrolling** `[L-S1-15]`. Side margins were reduced so the whole form — route cards, product table, supplier/tracking/expected-arrival row, memo, Register button — fits one viewport. A requester cross-checking a paper PO must never lose the Register button below the fold.
- **The desk cannot claim goods arrived** `[L-S3-9]`, `[BR-11]`. There is no manual "mark as INBOUNDED" control anywhere on this page and there must never be one. If the desk could tidy the list, the list would stop describing the warehouse. Status is a physical fact and only a physical scan may write it.
- **Zero numbering coordination** `[L-S1-3]`. Inbound No. is assigned by the server at registration and is not previewed on the form. Two requesters registering in the same second get different numbers without talking to each other.
- **Paste-a-block-of-tracking-numbers** `[L-M1]`. `＋ Add tracking number` appends a row **and focuses its input**, so n numbers can be entered without touching the mouse. A dispatch email pasted as a multi-line block must not silently become one malformed number (`[E-72]`).
- **0 vs blank is a real distinction** `[L-S1-10]`, `[L-S1-11]`. Unit Cost `0` means *free of charge* (partnership/promotional stock) and is a meaningful, required value. JIT Price blank means *unknown* and must never be silently coerced to 0 — that would poison downstream JIT price data. The placeholders carry the semantics: `Per-unit price ₩ (0 if free)` and `Blank if unknown`.
- **Korean supplier names are typed as data** `[L-S1-12]`. The Supplier placeholder is literally `e.g. 비엠유통, Coupang` and State 2 carries the value `비엠유통`. Never transliterate, never translate [G-6]. Korean IME input also means full-width digits can reach numeric fields (`[E-71]`).

### 1.5 Global surfaces that are explicitly NOT on this page

Stated so QA does not import behavior that does not apply, and so a developer does not build it.

| Global rule | Status here | Note |
|---|---|---|
| [G-1] Scanner protocol | **N/A** — no scan surface | Delta retained: Enter in the unified search box must not submit `[L-S1-5]` |
| [G-3] Audio feedback | **N/A** — no send sound, no TTS | No outbound-class button exists here, so `[PD-2]` does not reach this page |
| [G-4] Instant printing | **N/A** — no Print button | No label, no picking artifact, no report is produced here |
| [G-13] Sample assignment | **N/A** | Sample sets attach to customer orders, never to inbound requests |
| [G-14] Location scheme | **N/A** | Locations are assigned during reception in View Orders State 6, not declared here |

---

## 2. Screen Inventory & Wireframe Map

### 2.1 Declared unit count

**Total legend units covered by this spec: 39.**

- **28 numbered legend dots** (State 1: 15 · State 2: 2 · State 3: 10 · Modal M1: 1)
- **2 off-screen normative footer rule blocks** (`[L-S1-F]`, `[L-S2-F]`)
- **9 page-furniture units** (`[L-F1]` … `[L-F9]`) — unnumbered on the wireframe but normative

Plus **12 negative entries** (`[L-R1]` … `[L-R12]`) recording removed or rejected features that **must NOT exist** in the build. Negative entries are not legend units and are not counted in the 39.

**Verification.** The wireframe carries exactly 28 on-screen `.dot` elements and exactly 28 legend `<li>` rows (State 1: `1,2,3,4,5,10,11,12,6,7,8,9,14,15,16`; State 2: `1,2`; State 3: `1`–`10`; Modal: `M1`) — a perfect 1:1 dot↔legend mapping with no orphan dot and no legend row lacking a dot. State 3's legend carries **no** trailing footer paragraph; States 1 and 2 each carry exactly one.

**Declared numbering gaps and artifacts** (so coverage checks do not flag phantom holes):

- **State 1 has no dot 13.** The dot was vacated by the 2026-08-03 renumbering when the "View Orders link info" modal was removed. Intentional (`_wireframe-fixes.md` §E, supervisor ruling 14). State 1 dots run 1–12, 14, 15, 16.
- **State 1's legend renders out of numeric order** (`… 5, 10, 11, 12, 6, 7, 8, 9, 14 …`). This is a render-order artifact of the CSS grid, not a missing item. Coverage is by key, not by position.
- **State 2 restarts numbering at 1.** Its dots 1 and 2 are page-local and unrelated to State 1's dots 1 and 2.
- **State 3 restarts numbering at 1.** Same.
- **The modal carries a single dot labelled `M1`**, not a number.

### 2.2 State / modal map

Live URL for all rows: `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/inbound-request/`

| Key | Wireframe surface | DOM id | How to reach it | Spec home |
|---|---|---|---|---|
| S1 | `1 · New Request (Smart Buy)` | `#s1` | Default on load; or click top-bar `.wf-tab[data-state="s1"]` | §3.1 |
| S2 | `2 · New Request (Wholesale / Partnership)` | `#s2` | Top-bar `.wf-tab[data-state="s2"]` | §3.2 |
| S3 | `3 · Request List (Requested/Partial/Inbounded)` | `#s3` | Top-bar `.wf-tab[data-state="s3"]`; or the in-page tab `Request List`; or load with `#reqlist` / `#s3` | §3.3 |
| M1 | `Modal: Add Tracking No` | `#m-invoice` | Top-bar `.wf-tab[data-modal="m-invoice"]`; or any `Add tracking` button in the Request List; or `Bulk add tracking numbers` | §3.4 |

**S1 and S2 are one functional surface.** They are the same New Request form rendered with different demo data (S1 = Smart Buy route with a mid-entry blue prefill row; S2 = Wholesale route with a tracking number already known and a free-of-charge row). The spec treats them as a single form with route-parametrised examples; State 2's two dots are deltas, not a second screen.

**In-admin page tabs vs wireframe state tabs.** The purple top bar (`.wf-bar`) is wireframe chrome and does not exist in the admin. The real navigation is the in-page `.pagetabs` pair `New Request` | `Request List` (`[L-S1-16]`). The `Hide annotations` toggle (`#annoToggle`) is likewise wireframe chrome and is not a product feature.

### 2.3 Legend ↔ spec 1:1 map

| Key | Legend text anchor | Spec section |
|---|---|---|
| `[L-S1-1]` | New Inbound Request screen = single intake gateway | §3.1.1 |
| `[L-S1-2]` | Sourcing Route — 4 radio cards incl. Other + free text | §3.1.2 |
| `[L-S1-3]` | Inbound No. auto-assigned, no input or preview | §3.1.3 |
| `[L-S1-4]` | Field set aligned to PH sheet column order, no Size | §3.1.4 |
| `[L-S1-5]` | Single unified search box | §3.1.5 |
| `[L-S1-6]` | Picked product = blue-tinted row, locked cells | §3.1.6 |
| `[L-S1-7]` | Tracking No optional + single Register button | §3.1.7 |
| `[L-S1-8]` | Expected arrival | §3.1.8 |
| `[L-S1-9]` | View Orders link note | §3.1.9 |
| `[L-S1-10]` | Unit Cost (KRW) required, 0 allowed | §3.1.10 |
| `[L-S1-11]` | JIT Price (KRW) optional | §3.1.11 |
| `[L-S1-12]` | Supplier required | §3.1.12 |
| `[L-S1-14]` | Comments hub (top right) | §3.1.13 |
| `[L-S1-15]` | Reduced side margins — one-screen form | §3.1.14 |
| `[L-S1-16]` | In-admin page tabs [New Request \| Request List] | §3.1.15 |
| `[L-S1-F]` | State 1 off-screen footer rule block | §3.1.16 |
| `[L-S2-1]` | Direct routes get the same auto Inbound No. | §3.2.1 |
| `[L-S2-2]` | Same product-entry spec; Unit Cost 0 typed directly | §3.2.2 |
| `[L-S2-F]` | State 2 off-screen footer rule block (3-stage status) | §3.2.3 |
| `[L-S3-1]` | Status filter chips with counts | §3.3.1 |
| `[L-S3-2]` | Bulk bar — bulk add tracking numbers | §3.3.2 |
| `[L-S3-3]` | Sourcing Route column | §3.3.3 |
| `[L-S3-4]` | Tracking No column | §3.3.4 |
| `[L-S3-5]` | Status column, 3 stages + qty-edit history | §3.3.5 |
| `[L-S3-6]` | No tracking → morning Slack check | §3.3.6 |
| `[L-S3-7]` | Multiple tracking numbers per request | §3.3.7 |
| `[L-S3-8]` | INBOUNDED auto-switched by View Orders scan | §3.3.8 |
| `[L-S3-9]` | Inbound automation note | §3.3.9 |
| `[L-S3-10]` | Received Date column; no Carrier column | §3.3.10 |
| `[L-M1]` | Add Tracking No modal | §3.4 |
| `[L-F1]` | Registration confirmation toast | §3.5.1 |
| `[L-F2]` | Per-row `💬 Comments` button + inline panel | §3.5.2 |
| `[L-F3]` | `＋ New Inbound Request` button | §3.5.3 |
| `[L-F4]` | Result count footer line | §3.5.4 |
| `[L-F5]` | Deep link `#reqlist` / `#s3` | §3.5.5 |
| `[L-F6]` | Memo (Optional) textarea | §3.5.6 |
| `[L-F7]` | Admin top navigation bar (inherited chrome) | §3.5.7 |
| `[L-F8]` | Page title block | §3.5.8 |
| `[L-F9]` | Request List undotted columns | §3.5.9 |
| `[L-R1]`…`[L-R12]` | Removed / rejected — must NOT exist | §3.6 |

### 2.4 Known wireframe defects affecting this page

| Defect | What is stale | Spec position |
|---|---|---|
| **WF-2** | State 1 off-screen footer says "Received Date **and Carrier** are recorded automatically" | The spec follows `[L-S3-10]` and the 2026-08-03 decision (review **C-1**): **Received Date only. No Carrier capture, no Carrier column** `[PD-9 · OWNER-PENDING]`. The footer text is stale and must be fixed in the wireframe (drop "+ Carrier"). Never implement carrier capture from this footer. |
| **WF-11** | An HTML comment for the removed "View Orders link info" modal remains at ~line 701 | Tombstone `[L-R1]`. The modal must not be built. The comment block is to be deleted in the wireframe-fix pass. |

**Two further stale-text observations found while writing this spec.** They are **not** in the `WF-1`…`WF-14` backlog; they are proposed additions to it, recorded here so the behavior is unambiguous even if the wireframe is never edited:

1. **State 1 purple note lists only three routes.** The note ends `… sourcing route shows as a badge (SMART BUY / WHOLESALE / PARTNERSHIP)` — it predates the 2026-07-26 addition of `OTHER`. The **correct behavior is four**: an `OTHER`-route request renders `OTHER ({channel name})` on the scan screen exactly like the other three `[PD-80 · OWNER-PENDING]` (§3.1.9, §3.3.3). The parenthetical is illustrative, not an exhaustive list.
2. **A Tracking No cell that already holds a number offers no inline add affordance.** In the wireframe, `Add tracking` renders only when the cell is empty. Since `[G-10]` requires that numbers can keep arriving for a still-open request, the **specified path** for adding to a request that already has numbers is the bulk bar (§3.3.2, §3.3.4). Whether to add an inline `＋` to a filled cell is a UX question for the owner, not a licence to invent one now (§9.2 OQ-3).

**Wireframe demo limitations that are not defects** (QA must tag assertions about them `[ADMIN]`, not file bugs): filter chips toggle visually but do not filter rows; row checkboxes are inert and the `2 selected` count never changes; `Register Inbound Request` always fires the success toast regardless of validation; the M1 header is static (`Add Tracking No — 202607130003`) whichever row opened it; the Comments hub dropdown is wired only in State 1 (`data-open="inbox1"`), so States 2 and 3 render the button without a dropdown; the demo autocomplete list is static and does not respond to typing.

---

## 3. Functional Specification

Conventions used below: **Trigger** → what starts it · **Behavior** → exact effect · **Validation** → blocking rules · **Server** → persisted action · **Feedback** → what the operator sees.

### 3.1 State 1 / State 2 — New Request form

#### 3.1.1 `[L-S1-1]` Single intake gateway

**Behavior.** The New Request form is the only creation path for warehouse inbound. The section label reads `Sourcing Route` followed by the muted qualifier `— the single intake gateway for everything entering the warehouse`.

**Contract.** No other screen may create an inbound request. Arrivals with no matching request route to the shared unrecognized pool on `tracking-missing` [G-11]; recovery is: create the request here → add its tracking number → remove the pool row with reason `routed to inbound request` and the Inbound No. captured as a structured field `[PD-64 · OWNER-PENDING]` → the next scan of that barcode enters View Orders State 6 normally (`[E-53]`).

#### 3.1.2 `[L-S1-2]` Sourcing Route — 4 radio cards

**Trigger.** Click anywhere on a `.routecard` (the whole card is a `<label>` wrapping the radio).

**The four cards, verbatim:**

| Card title | Sub-copy | Badge | Stored value |
|---|---|---|---|
| `Smart Buy` | `Stock replenishment · Coupang JIT sourcing (via PH)` | `SMART BUY` | `SMART_BUY` |
| `Wholesale` | `Bulk wholesale inbound (direct request)` | `WHOLESALE` | `WHOLESALE` |
| `Brand Partnership` | `Brand sponsorship · marketing stock (direct request)` | `PARTNERSHIP` | `PARTNERSHIP` |
| `Other` | `Any other channel — type it in` + inline text input, placeholder `Enter channel name` | `OTHER` | `OTHER` + `other_channel_text` |

**Behavior.** Exactly one route is selected at all times; `Smart Buy` is preselected in State 1, `Wholesale` in State 2. Selecting a card adds class `on` to it and removes it from its siblings. Selecting `Other` **enables and focuses** the `.etc-in` input; selecting any other card disables `.etc-in` (its value is retained client-side but is ignored on submit).

**Route is request-level, not row-level.** Switching route after product rows exist retains every row and every entered value (`[E-9]`).

**Validation.** `Other` requires a non-blank `other_channel_text` (trimmed). Submitting with `Other` selected and an empty or whitespace-only channel name is blocked with an inline error on the field and focus moved to `.etc-in` (`[E-8]`, `[E-47]`).

**Channel-text normalisation.** `other_channel_text` is stored trimmed and whitespace-collapsed. Case is preserved for display but the value is compared case-insensitively when grouping channels downstream, so `Gmarket`, `gmarket` and `GMARKET ` do not become three channels (`[E-78]`). Characters that would break a Slack message or the sheet are escaped at render time, never stripped from storage (`[E-79]`).

**Rendering [G-5] delta.** All four badges render as **colorless black bold text**, never coloured pills. `OTHER` renders downstream — Request List route column, View Orders scan badge, Inventory route filter — as black bold `OTHER ({channel name})`, and the free-text channel is carried into the Procurement Hub sheet `[PD-80 · OWNER-PENDING]`. JIT is deliberately absent from this form: JIT is an order-side sourcing outcome and is never a requestable inbound route [G-5] (review **C-3**).

**Accessibility.** The cards are real radios inside labels, so keyboard operation is arrow-key selection within the group and `Space` to pick. Selection by keyboard must produce the same `on` class, the same `.etc-in` enablement, and the same focus move as a mouse click (`[E-90]`).

**Server.** The chosen route and, for `OTHER`, the channel text are persisted on the request (`DC-1`).

#### 3.1.3 `[L-S1-3]` Inbound No. — auto-assigned, never previewed

**Behavior.** There is **no Inbound No. field and no preview panel on the form** (panel removed 2026-07-26 → `[L-R2]`). At registration the server allocates `YYYYMMDDNNNN`, where `YYYYMMDD` is the registration date and `NNNN` is a per-day sequence `0001`–`9999`. The number is surfaced **only in the Request List** and in the M1 modal header.

**Server.** Allocation is a distinct persisted event (`DC-2`) so collisions and sequence exhaustion are auditable. Allocation is atomic with request creation: a double submit protected by the idempotency key produces **exactly one** number (`[E-17]`, [G-9]).

**Date bucket.** `YYYYMMDD` is resolved from a **single declared server timezone**, not from the client clock. A form opened at 23:58 and submitted at 00:02 receives the *submission* date's bucket, and the sequence for the new day starts at `0001` (`[E-74]`). The declared timezone is a dev decision (§9.3, D-20) but must be one value for the whole system.

**Concurrency.** Two operators registering in the same second receive distinct sequential `NNNN` values; the sequence is server-side, never client-derived (`[E-19]`).

**Exhaustion.** `NNNN > 9999` on one calendar day must fail loudly — block registration with a red toast [G-2] and persist the attempt. It must never silently wrap or reuse a number (`[E-20]`; mechanism is a dev decision, §9.3).

**Sheet mapping.** Inbound No. maps to Procurement Hub sheet column A `PO No. (=Order ID)`. It is named "Inbound No." rather than "PO No." because partnership and other non-purchase inbounds have no PO.

#### 3.1.4 `[L-S1-4]` Field set aligned to the PH sheet column order

**Behavior.** The form's field order mirrors the Procurement Hub sheet column order exactly:

`Inbound No. (auto)` → `Channel` → `SKU No.` → `Brand` → `Product Name` → `Order Qty` → `Unit Cost (KRW)` → `JIT Price (KRW)` → `Supplier`

**There is no Size field** (removed 2026-07-23 → `[L-R7]`). Quantity alone describes the line.

**Field contract:**

| Field | Type | Required | Source | Editable | Notes |
|---|---|---|---|---|---|
| Sourcing Route | radio ×4 | Yes | operator | Yes | `[L-S1-2]` |
| Other channel name | text | Only when route = `OTHER` | operator | Yes | placeholder `Enter channel name` |
| SKU No. | text | Yes | search selection | **No** (readonly) | `[L-S1-6]` |
| Brand | text | Yes | search selection | **No** (readonly) | |
| Product Name | text | Yes | search selection | **No** (readonly) | EN name, brand-prefixed in bold when rendered elsewhere [G-6] |
| Order Qty | integer | Yes, ≥ 1 | operator | Yes | placeholder `Qty` |
| Unit Cost (KRW) | integer | Yes, ≥ 0 | operator | Yes | header `Unit Cost (KRW) *`, placeholder `Per-unit price ₩ (0 if free)` |
| JIT Price (KRW) | integer | No (blank allowed) | operator | Yes | header `JIT Price (KRW)`, placeholder `Blank if unknown` |
| Supplier | text | Yes | operator | Yes | placeholder `e.g. 비엠유통, Coupang` |
| Tracking No | text | No | operator | Yes | `[L-S1-7]` |
| Expected arrival | date | No | operator | Yes | `[L-S1-8]` |
| Memo | textarea | No | operator | Yes | `[L-F6]` |

**Numeric contract.** Values are displayed comma-grouped (`15,000`) and stored as integers. Input parsing strips commas, currency symbols and surrounding whitespace, and normalises full-width digits (`１５０００` → `15000`) before validation (`[E-7]`, `[E-71]`). Non-numeric, negative and fractional values are rejected (`[E-6]`, `[E-55]`). An `Order Qty` above the declared per-line maximum is rejected rather than truncated or overflowed (`[E-69]`). Storage is integer KRW; formatting is presentation-level (dev decision, §9.3).

#### 3.1.5 `[L-S1-5]` Single unified search box

**Trigger.** Typing in the `.auto input` above the product table. Placeholder: `Type any SKU No. · brand · product name → click a suggestion to add a row below`.

**Behavior.** One box searches **three fields at once** — SKU No., brand, and English product name — so the requester types whichever identifier they happen to know. Matches render as `.opt` rows in the format `{Brand} — {Product Name}` with the SKU in a trailing `<small>`; the first match carries class `sel`. Clicking a suggestion **appends a prefilled row** to the product table (`[L-S1-6]`) and **returns focus to the search box with its value selected**, so the next product can be typed immediately.

**Keyboard contract (page delta of the [G-1] discipline).** `Enter` inside the search box **must NOT submit the form**. `Enter` selects the highlighted suggestion if the suggestion list is open; if the list is empty or closed, `Enter` is a no-op. `Escape` closes the suggestion list without clearing the query. Arrow keys move the `sel` highlight. Keyboard selection must append a row exactly as a click does (`[E-90]`).

**Catalog scope.** The search resolves against the live product catalog. A SKU that is inactive or discontinued is either excluded or shown with an explicit inactive marker — never shown as an ordinary match (`[E-68]`; which of the two is a dev decision, §9.3). If the catalog returns two entries for one SKU, the search must surface the ambiguity rather than silently pick one (`[E-67]`).

**No results.** An explicit no-result affordance renders inside the dropdown; no row is appended and nothing is submitted (`[E-11]`).

**Retired predecessor.** Per-row search boxes and the separate "add row" button were retired 2026-07-27 → `[L-R5]`. Do not re-introduce either.

**Non-event.** Autocomplete queries and keystrokes are **not persisted** (§5.4).

#### 3.1.6 `[L-S1-6]` Picked product row — blue prefill, locked cells

**Behavior.** A selected product is appended as a row with class `prefill` (blue tint) containing readonly `SKU No.`, `Brand`, `Product Name` and empty `Order Qty`, `Unit Cost (KRW)`, `JIT Price (KRW)` inputs plus a `✕` delete button (`.rm`, title `Delete row`).

**Locked cells.** The three catalog cells are `readonly` and styled borderless plain text (`pointer-events:none`, transparent border and background, bold ink). They cannot be typed into, pasted into, or edited by any UI path (`[E-13]`). The only correction is `✕` on the row followed by a fresh search.

**Multiple SKUs.** Keep selecting in the search box; each selection appends one more row. There is no add-row button.

**Duplicate SKU.** Picking a SKU that already has a row is **blocked with an inline notice** — `Already added — edit the quantity on the existing row` — and no second row is appended `[PD-83 · OWNER-PENDING]` (`[E-12]`). Rationale: two rows for one SKU would double-count in the View Orders State 6 reconciliation table and in the PH sheet.

**Catalog drift.** If a product is deleted or renamed in the catalog between selection and submit, the request is registered against the **snapshot captured at selection time** (SKU, brand, name are copied onto the line, not referenced), and the mismatch is recorded on `DC-1`; registration is not blocked (`[E-66]`).

**Empty table.** Deleting every row returns the table to its empty state and blocks submission (`[E-14]` = `[E-1]`).

**Non-event.** Row add/delete before submission is client-side draft state and is not persisted (§5.4).

#### 3.1.7 `[L-S1-7]` Tracking No — optional, one Register button

**Behavior.** The `Tracking No` field is optional. It is rendered with a **dashed border** (`.fld-inv`) to signal optionality at a glance. Label: `Tracking No — optional · can be added later after dispatch`. Placeholder in State 1: `Add after dispatch — you can submit without it (add later)`; in State 2: `Add after dispatch — you can submit without it`.

**Single register button.** There is exactly one submit control, `Register Inbound Request` (unified 2026-07-27 → `[L-R6]`). Whether a tracking number is present or not, the request registers with status `REQUESTED`. If a number is present, **View Orders matching activates immediately** at save time (`DC-6`).

**Multiple numbers at creation.** The creation form accepts a single number; additional numbers are added through `[L-M1]` [G-10]. A number entered here is subject to the same uniqueness rule as M1 (`[BR-9]`, `[BR-15]`, `[PD-82 · OWNER-PENDING]`). Re-entering the same number in M1 afterwards is idempotent, not a duplicate (`[E-88]`).

**Registration server action.**

1. Client debounce + idempotency key generated per form session [G-9]. A suppressed replay is persisted (`DC-23`).
2. Validate in this order: ≥ 1 product row → each row's Order Qty is an integer ≥ 1 → each row's Unit Cost present and ≥ 0 → JIT Price blank or ≥ 0 → Supplier non-blank after trimming → route selected → if `OTHER`, channel text non-blank after trimming → tracking number (if present) not already registered on another request.
3. On any failure: **no server write**, inline errors on every offending field, focus moved to the first offending field, **no success toast**, and the rejection is persisted (`DC-18`).
4. On success: allocate Inbound No. (`DC-2`), persist the request (`DC-1`), persist tracking numbers if any (`DC-3`) and their matching activation (`DC-6`), materialise a non-empty Memo as a system comment (`DC-11`), then return.
5. **No full-page refresh** — this page is not the single named [G-2] exception. The new row is inserted at the top of the Request List in place.

**Feedback.** Green top-right toast [G-2]:
`✓ Inbound request registered` with secondary line `Inbound No. auto-assigned · added to the Request List · No refresh`.
(The Request List also carries a **static** demo toast reading `✓ Inbound request registered — 202607130003` / `No refresh · added to top of the list` — see `[L-F1]`; the two must not be confused.)

**Partial-success rule.** Memo materialisation, Slack dispatch and telemetry are **after-commit side effects**. If any of them fails, the request still exists and the toast still fires; the failure is persisted and retried (`[E-83]`, `[PD-4 · OWNER-PENDING]`).

**Form reset after success** is a dev decision (§9.3); whichever is chosen must be consistent and must not leave a half-cleared form.

#### 3.1.8 `[L-S1-8]` Expected arrival

**Behavior.** A native `date` input labelled `Expected arrival`, optional (no asterisk). Its purpose is forward visibility for the warehouse: it feeds the View Orders **"Expected Inbound N"** summary badge (2026-08-02 decision) so the center can see what is coming before it arrives. Demo values: `2026-07-16` (S1), `2026-07-18` (S2). The Request List renders it as `MM-DD`.

**Past dates** are allowed with a non-blocking warning (a request can legitimately be created after the fact); min/max bounds are a dev decision (`[E-15]`, §9.3). Blank is allowed, renders as an empty Expected arrival cell, and excludes the request from the "Expected Inbound" badge (`[E-54]`).

#### 3.1.9 `[L-S1-9]` View Orders link note

**Behavior.** A purple informational note under the form, verbatim:
`Entering a tracking number auto-matches it to View Orders — when the center scans that tracking barcode, this request's sourcing route shows as a badge (SMART BUY / WHOLESALE / PARTNERSHIP).`

It is **display only** — no control, no link, no `data-modal`. The "View Orders link info" modal that used to sit behind it was removed 2026-08-03 → `[L-R1]`. Do not build a modal, a button, or a hyperlink here.

**Route-list correction.** The parenthetical names three routes because it predates `OTHER` (2026-07-26). The correct badge set is **four**; an `OTHER`-route scan shows `OTHER ({channel name})` `[PD-80 · OWNER-PENDING]`. See §2.4 observation 1.

#### 3.1.10 `[L-S1-10]` Unit Cost (KRW) — required, 0 allowed

**Behavior.** Column header `Unit Cost (KRW) *`. Required on every row. `0` is a valid, meaningful value meaning free-of-charge stock.

**Explanatory copy.** The disclaimer sits at the **table's top right** (position moved 2026-08-03), verbatim:
`Unit Cost (KRW) = actual per-unit purchase price from the supplier — enter 0 if free of charge (required) · JIT Price (KRW) = per-unit price when buying this product via Coupang JIT — leave blank if unknown (optional) · keep selecting in the search box above to add more SKU rows (delete a row = ✕)`
The row placeholder repeats the rule: `Per-unit price ₩ (0 if free)`.

**Validation.** Blank is blocked (`[E-3]`); `0` is accepted (`[E-4]`); negative, fractional and non-numeric are rejected (`[E-6]`, `[E-55]`).

**Rationale.** Unit Cost is the basis of FIFO costing and of Procurement Hub sheet consistency, so it must always exist. The FOC checkbox that used to lock the field to ₩0 was retired 2026-07-26 in favour of typing `0` directly → `[L-R3]`.

#### 3.1.11 `[L-S1-11]` JIT Price (KRW) — optional

**Behavior.** Column header `JIT Price (KRW)` (no asterisk). Per-unit price of buying the same product through Coupang JIT. Placeholder `Blank if unknown`.

**Validation.** Blank is accepted (`[E-5]`). If present it must be a non-negative integer.

**Hard rule.** A blank JIT Price **must never be coerced to 0** on save, on export, or in the sheet handoff. Blank means *unknown*; `0` would mean *free through JIT*, which is a different and almost always false claim (`[BR-6]`).

**Scope.** Optional for **all four routes** (widened 2026-07-26 from the 2026-07-23 design where it applied to Smart Buy and Wholesale only).

#### 3.1.12 `[L-S1-12]` Supplier — required

**Behavior.** Label `Supplier *` with the qualifier `— who is shipping the goods`; placeholder `e.g. 비엠유통, Coupang`. Required, free text, trimmed. Demo values: `Coupang` (S1), `비엠유통` (S2).

**Rationale.** Supplier is the settlement counterparty and the party whose dispatch produces the inbound tracking number; both settlement and the tracking chase depend on it. Blank — and whitespace-only, which trims to blank — is blocked (`[E-10]`, `[E-70]`).

**Data note.** Korean supplier names are stored and displayed verbatim [G-6]. Never transliterate, never translate.

#### 3.1.13 `[L-S1-14]` Comments hub (top right)

**Behavior.** The shared admin-wide Comments hub [G-7], identical to the component on every other screen. Button `💬 Comments` with an unread-mention count badge (demo: `2`). The dropdown carries two tabs — `@ Mentions` (with its own count badge) and `★ Saved` — plus full-text search across **all** comments (entity no. / author / text), newest first; clicking an entry opens the entity.

**Page delta.** On this page the commentable entity type is the **inbound request** (`Inbound No.`), and hub entries render the Inbound No. as the entity label (demo entries: `202607130002 · Dean: "@Yongwon when is the tracking number for this wholesale one coming?"` at `11:20`; `202607120004 · Miranti: "@Yongwon the partnership stock's expected arrival slipped by a day"` at `Yesterday`).

**Pane headers.** `Comments where I'm tagged` with the action `Mark all as read`; `Comments I saved` with the hint `Unstar to remove from list`.

**Star toggle.** `★` toggles saved state per user (`DC-12`). `Mark all as read` clears the unread badge (`DC-13`).

**Dead targets.** A hub entry whose request can no longer be resolved must render a non-crashing "entity unavailable" state rather than a broken navigation (`[E-86]`).

**Comments are append-only** — no edit, no delete; corrections are posted as new comments `[PD-3 · OWNER-PENDING]`.

**Wireframe limitation.** The dropdown is wired only in State 1 (`data-open="inbox1"`). In the real admin the hub is present on every state of every screen.

#### 3.1.14 `[L-S1-15]` Reduced side margins — one-screen form

**Behavior.** Page padding is reduced (`.pagepad{padding:18px 16px 0}`) so the complete New Request form — route cards, product table, supplier/tracking/expected-arrival row, memo, purple note and the `Register Inbound Request` button — fits one viewport at the target admin width (the mock declares `min-width:1280px`) without vertical scrolling.

**Contract.** This is a hard layout constraint, not a preference: the Register button must remain reachable while the requester is reading a paper PO. Any future field addition must be traded against this constraint, and any change that pushes `.submitrow` below the fold at the target width is a regression.

#### 3.1.15 `[L-S1-16]` In-admin page tabs `[New Request | Request List]`

**Behavior.** Two in-page tabs (`.pagetabs`) added 2026-07-23: `New Request` and `Request List`. Exactly one is active (class `on`). They are the real admin navigation, distinct from the wireframe's purple state tabs.

**Navigation.** `Request List` switches to the list **without a page reload**; `New Request` returns to the form. `#reqlist` / `#s3` deep-links land directly on `Request List` (`[L-F5]`, [G-12]).

**Unsaved draft on tab switch** is a dev decision — either warn or persist the draft client-side, but the choice must be consistent and must never silently discard entered rows (`[E-57]`, `[E-85]`, §9.3).

#### 3.1.16 `[L-S1-F]` State 1 off-screen footer rules

Three normative rules printed under the State 1 legend. They are binding except where superseded:

**(a) Automatic capture at inbound.** **Received Date** is recorded automatically at inbound and shown in the Request List; it is never a form input. **The footer's "and Carrier" clause is stale** — automatic Carrier recording is **not supported** and there is **no Carrier column** (2026-08-03; `[L-S3-10]`, `[PD-9 · OWNER-PENDING]`, defect **WF-2**, review **C-1**). Implement Received Date only.

**(b) The Request List is the scrape source.** The Request List is the dataset the Procurement Hub Google Sheet will scrape **as-is**. Nothing may be written into the list that the sheet cannot represent. The sheet integration is designed **separately, as the last step** (agreed 2026-07-23) — see §6.4 and §9.1.

**(c) Label standardisation.** The label is always `Comments`, in every state, every modal and every row. It is never localised and never renamed (`[BR-22]`).

### 3.2 State 2 — Wholesale / Brand Partnership variant

#### 3.2.1 `[L-S2-1]` Direct routes get the same auto Inbound No.

**Behavior.** Wholesale, Brand Partnership and Other are "direct request" routes (no Procurement Hub purchase leg), yet they behave **identically** to Smart Buy: the Inbound No. is auto-assigned at registration, is not shown on the form, and appears only in the Request List. The State 2 submit-row copy reads `On registration, status = REQUESTED (tracking number entered → View Orders matching active immediately) · Inbound No. auto-assigned — shown in the Request List`.

**Contract.** There is **no route-conditional behavior anywhere in this form** other than (i) which card is preselected and (ii) whether `Other`'s channel text is required. Every validation, every field requirement, and every server action is route-invariant. QA must run the form suite parametrised across all four routes (`QA-B-05`).

#### 3.2.2 `[L-S2-2]` Same product-entry spec; Unit Cost `0` typed directly

**Behavior.** Identical product entry: single search box, appended rows, Order Qty and Unit Cost required, JIT Price optional. State 2's demo row 2 (`Round Lab` `1025 Dokdo Cleanser, 150ml`, qty `300`) carries `Unit Cost = 0` with a blank JIT Price, demonstrating free promotional stock. The explanatory line under the table reads:
`Row 2 = free promotional stock — 0 entered directly in Unit Cost (0 allowed). JIT Price = per-unit price when buying via Coupang JIT, blank if unknown (optional)`

**Contract.** `0` is entered by typing it. There is no checkbox, no toggle, and no control labelled "free of charge" → `[L-R3]`. (The *phrase* "free of charge" does legitimately appear in State 1's explanatory disclaimer; the prohibition is on the **control**, not the words.)

#### 3.2.3 `[L-S2-F]` State 2 off-screen footer rules

**(a) Status has exactly three stages:** `REQUESTED → PARTIAL → INBOUNDED`. `SHIPPED` was retired 2026-07-27 → `[L-R4]`; `PARTIAL` was added 2026-08-02. No fourth status exists, and no status may be set from this page [G-11].

**(b) Tracking timing.** If the tracking number is already known, enter it now and View Orders matching activates the moment the request registers. Otherwise leave it blank and add it later from the Request List via `[L-M1]`.

**Demo evidence.** State 2 carries tracking `10325661220417` at creation and its purple note reads:
`A tracking number is already entered, so the request matches to View Orders the moment it registers — scans show the WHOLESALE badge.`

### 3.3 State 3 — Request List

#### 3.3.1 `[L-S3-1]` Status filter chips

**Behavior.** Four single-select chips above the table, each showing a live count:
`All 12` · `REQUESTED 8` · `PARTIAL 1` · `INBOUNDED 3`
The `REQUESTED` / `PARTIAL` / `INBOUNDED` chips render the status pill inline followed by the count. Exactly one chip is active (class `on`); clicking a chip filters the table to that status and moves `on`. `All` is the default.

**Counts** are computed over the full request set, not the current page, and are recomputed after every status change and every new registration. The three status counts must always sum to the `All` count.

**Tracking presence is not a status.** Whether a request has a tracking number is read from the **Tracking No column**, never from the status chip. A `REQUESTED` request may have zero, one, or many tracking numbers (`[BR-10]`).

**Empty result.** A chip with no matching rows shows an explicit empty state and a count of `0` (`[E-23]`); a first-run list with no requests at all shows the same empty state (`[E-61]`).

**Live insert under a filter.** A newly registered request appears at the top of the list only if it matches the active chip; the success toast fires regardless, and the chip counts update either way (`[E-26]`). On a paginated list, a live insert must not silently push a row off the visible page without the count line reflecting it (`[E-84]`).

**Non-event.** Chip clicks and list sorts are client-local and are not persisted (§5.4).

**Wireframe limitation.** In the wireframe the chips toggle `on` visually but do **not** filter rows — filtering assertions are `[ADMIN]`.

#### 3.3.2 `[L-S3-2]` Bulk bar

**Behavior.** A bar pinned above the table containing the button `Bulk add tracking numbers` and a count line, verbatim:
`2 selected · Inbound processing (INBOUNDED transition) is applied automatically by View Orders scans`

**Selection model.** A header checkbox selects all **currently visible (filtered) rows only**; per-row checkboxes toggle individually. Selecting rows that are not on screen is the classic bulk-action accident, so it is forbidden (`[BR-29]`). Per-row selection persists across chip switches within a session. Selection is client-local (§5.4).

**Enabled conditions.** `Bulk add tracking numbers` is **disabled at 0 selected** (`[E-24]`). Rows in `INBOUNDED` are excluded from the operation and reported in the result toast, because adding tracking to a terminal request is blocked `[PD-85 · OWNER-PENDING]` (`[E-25]`, `[E-28]`).

**This is also the add-more-numbers path.** Because the Tracking No cell offers `Add tracking` only when it is empty (§3.3.4), the bulk bar is the **specified path** for adding a further number to a `REQUESTED` or `PARTIAL` request that already has one: select the row → `Bulk add tracking numbers` → the same `[L-M1]` contract applies to that request (§2.4 observation 2).

**Effect.** Opens the tracking-entry flow for the selected requests. The exact shape — one modal iterating the selection versus a per-request sequence — is a dev decision (§9.3); either way each request receives its own set of numbers, each number is validated for system-wide uniqueness `[PD-8 · OWNER-PENDING]`, and the same number must not be applied to two different requests in one batch (`[E-60]`).

**Server.** `DC-5` with a batch id, plus one `DC-3` per request/number pair and one `DC-6` per number.

**Feedback.** Green toast [G-2] naming how many requests received how many numbers, and how many were excluded and why.

**No manual INBOUNDED.** The "mark as shipped" bulk button was retired 2026-07-27 → `[L-R4]`, and no bulk status control exists → `[L-R12]`.

**Wireframe limitation.** Checkboxes are inert and the `2 selected` text is static — selection assertions are `[ADMIN]`.

#### 3.3.3 `[L-S3-3]` Sourcing Route column

**Behavior.** Renders the request's route as **black bold, colorless text** — `SMART BUY` / `WHOLESALE` / `PARTNERSHIP` / `OTHER ({channel name})` — matching the View Orders badge convention exactly [G-5]. Never a coloured pill, never an icon. `OTHER` rendering is `[PD-80 · OWNER-PENDING]`.

#### 3.3.4 `[L-S3-4]` Tracking No column

**Cell state machine:**

| Cell state | Render | Action available |
|---|---|---|
| No numbers | `Add tracking` button (`.btn-purple-line.btn-sm`) | Opens `[L-M1]` for that request |
| One number | The number in blue tabular-numeral text | none inline — use the bulk bar to add more (§3.3.2) |
| Two or more | Every number, one per line, plus the note `{n} tracking numbers — all matching active` | none inline — use the bulk bar |
| INBOUNDED | The number(s) plus the note `Switched by View Orders scan inbound` | **No `Add tracking` button** `[PD-85 · OWNER-PENDING]` |

**Contract.** The cell never truncates the number list — a split shipment with four numbers shows four numbers. All registered numbers are match/scan targets simultaneously [G-10].

**Demo evidence.** Row `202607120004` renders `10325661220417` and `10325661220418` with the note `2 tracking numbers — all matching active`. Rows `202607130003` and `202607130002` render the `Add tracking` button.

#### 3.3.5 `[L-S3-5]` Status column — three stages + quantity-edit history

**Behavior.** The status pill renders exactly one of:

| Status | Pill | Meaning |
|---|---|---|
| `REQUESTED` | amber fill, dark-amber text | Declared; nothing received yet |
| `PARTIAL n/m` | orange fill, white text, e.g. `PARTIAL 120/180` | Partially received; `n` received of `m` expected |
| `INBOUNDED` | green fill, white text | Fully received; terminal |

**Transitions (all written from View Orders, never from here):**

```
REQUESTED ──(View Orders State 6 "Save Partial")──▶ PARTIAL (n/m)
REQUESTED ──(View Orders State 6 "Confirm Full Inbound")──▶ INBOUNDED
PARTIAL   ──(rescan of any registered number, remainder reconciled)──▶ PARTIAL (n'/m) or INBOUNDED
```

No reverse transition exists on this page. `INBOUNDED` is terminal (`[BR-14]`). A request may go `REQUESTED → INBOUNDED` directly when the first receipt is complete; `PARTIAL` is not a required stop (`[E-89]`).

**Rescan resumes from the remainder.** Scanning any registered tracking number of a `PARTIAL` request re-enters View Orders State 6 with the running totals restored; received counts accumulate against the same request and are never double-counted (`[E-44]`, [G-10]).

**Over-receipt.** View Orders warns and counts rather than capping, so `n` may exceed `m`; the excess blocks full confirmation until it is resolved by an expected-qty edit or a partial save `[PD-12 · OWNER-PENDING]`. This page renders whatever `n/m` results, **including `n > m`** — the pill must not clamp, hide, or re-order the numbers (`[E-92]`).

**Expected-qty edit history.** When View Orders M6 edits an expected quantity, this page renders the history inline in the **Qty cell**, in the format `✎ {old}→{new} ({reason token})` as a `.route-note` with `title="Expected qty edit history"`. Demo row `202607120001` renders `✎ 300→180 (damaged)` beneath the new expected quantity `180`.

**Reason-token render contract** (`[BR-30]`). The parenthetical is a **short token**, not the full [G-11] enum string — the wireframe shows `(damaged)`, not `(Damaged/defective — cannot accept)`, because the cell is narrow. The mapping is fixed so the token is never ambiguous:

| [G-11] enum value | Token rendered in the Qty cell |
|---|---|
| `Damaged/defective — cannot accept` | `damaged` |
| `Supplier qty change` | `supplier qty change` |
| `Other (memo)` | `other` — the operator's memo text is **not** inlined; it is readable in the auto-comment and in the cell's `title` (`[E-80]`) |

**Multiple edits.** When a line has been edited more than once, the Qty cell renders the **most recent** edit as `✎ {previous}→{current} ({token})` and the full chain is available in the request's comment thread; the cell never grows unbounded (`[E-81]`). On a multi-line request, the Qty cell shows the request's **total** expected quantity and the marker indicates that at least one line was edited; per-line detail lives in View Orders and in the comments (`[E-82]`).

**Edits originate only in View Orders M6.** There is **no edit affordance on this page** — this page displays history [G-11].

**Side effects of an edit** (owned by View Orders, surfaced here): remaining quantity and the full-confirm gate are recomputed, an auto-comment is posted on this request (`DC-11`), and the requester is notified by Slack `@mention` (§6.1 row 5).

**Guardrails inherited from View Orders M6:** a new expected quantity **below the already-received quantity is hard-blocked** with `New expected qty cannot be lower than the received qty ({n})` `[PD-14 · OWNER-PENDING]` (`[E-42]`); an edit down to **exactly** the received quantity re-enables `Confirm Full Inbound` but **does not auto-transition** to `INBOUNDED` — a human presses the button `[PD-84 · OWNER-PENDING]` (`[E-43]`).

#### 3.3.6 `[L-S3-6]` No tracking number → automatic morning Slack check

**Behavior.** Once per morning an automated job collects every request that is still `REQUESTED` **and has zero tracking numbers**, and posts them to Slack split by route:

- `WHOLESALE` and `SMART BUY` → **#wholesale-ops**
- `PARTNERSHIP` → **#partnership-kr**
- `OTHER` → channel deferred to development (§9.3, D-1)

Payload per row: Inbound No., supplier, requested-by, age.

**Design intent.** The chase loop is **push, not poll**. Nobody is expected to read the Request List looking for gaps; the gap comes to the team that owns it, in the channel they already sit in.

**The OTHER gap must not be silent** (`[BR-31]`). Until a channel is named, `OTHER`-route requests are **still collected and still written into `DC-14`** with `channel=unrouted`. The run record therefore proves how many requests went unchased, and turning the channel on later is a routing change, not a data-recovery exercise (`[E-75]`). Inventing a channel now is forbidden — it would create an unowned alert stream.

**Scope guards.** `PARTIAL` and `INBOUNDED` requests are never included (they have tracking by definition). Requests with at least one number are never included. The job runs **once per calendar day**; a scheduler retry must be idempotent per date and must not double-post (`[E-52]`). A run that finds nothing posts nothing but **still records the run** (`[E-76]`).

**Server.** Execution is persisted with the flagged request ids per channel and the Slack message ts (`DC-14`) so a silent scheduler failure is detectable; each dispatch result is persisted separately (`DC-15`). A partial failure — one channel delivered, one not — is recorded per channel and retried per channel (`[E-77]`). Slack delivery failure never blocks or alters request state `[PD-4 · OWNER-PENDING]` (`[E-51]`).

**In-page restatement.** The State 3 purple note repeats the rule verbatim: `Requests missing a tracking number are checked automatically every morning with a Slack alert (WHOLESALE·SMART BUY → #wholesale-ops / PARTNERSHIP → #partnership-kr).`

#### 3.3.7 `[L-S3-7]` Multiple tracking numbers per request — **primary home of [G-10]**

**Behavior.** One inbound request may hold **any number** of tracking numbers, because one purchase frequently ships as several parcels. Every registered number is an independent View Orders match/scan target, and partial arrivals accumulate against the same request until it is fully received [G-10]. The status badge **stays `REQUESTED`** no matter how many numbers are registered — numbers are not progress.

**Uniqueness.** A tracking number is unique **system-wide across inbound requests**: registering one that already exists on another request is blocked at save with an error naming the other Inbound No. `[PD-8 · OWNER-PENDING]` `[PD-82 · OWNER-PENDING]` (`[E-21]`, `[E-35]`). Rationale: View Orders must resolve a scan to exactly one request; two owners make the scan non-deterministic.

**Exact-match only.** Uniqueness and matching are **whole-string equality after normalisation** — never prefix, substring or fuzzy matching. A number that is a strict prefix or superset of another number is a *different* number and both may coexist (`[E-73]`).

**Namespace separation.** Inbound (supplier → warehouse) and outbound (warehouse → customer) tracking numbers are **separate namespaces and may legitimately coincide**; carriers reuse number ranges across directions. View Orders resolution precedence puts inbound-request tracking first (State 6) `[PD-86 · OWNER-PENDING]` (`[E-22]`).

**Deleting or editing a saved number.** Allowed only while **no scan has matched it**. Once any scan has matched, deletion and edit are blocked; the correction path is a comment and, if necessary, a new request `[PD-81 · OWNER-PENDING]` (`[E-38]`). A permitted deletion persists the old value (`DC-4`) and, per [G-2] / [GD-5], requires a confirm step and a toast `[PD-5 · OWNER-PENDING]`.

#### 3.3.8 `[L-S3-8]` INBOUNDED is auto-switched by a View Orders scan

**Behavior.** The `INBOUNDED` transition is performed by the View Orders scan flow when the exact-match full-receipt gate is satisfied. This page reflects it: the status pill turns green and the Tracking No cell gains the note `Switched by View Orders scan inbound`.

**Negative contract.** There is **no link, no button and no modal** back to View Orders from an INBOUNDED row — the separate link modal and the result link were both removed 2026-08-03 because the badge alone answers the question "did it arrive?" → `[L-R1]`, `[L-R10]`. QA asserts their **absence**.

#### 3.3.9 `[L-S3-9]` Inbound automation note

**Behavior.** A purple note below the table, verbatim:
`Inbound processing (the INBOUNDED transition) is not done manually on this screen — when the goods arrive, the center scans the tracking barcode in View Orders → processing the inbound automatically switches the request to INBOUNDED, and the scan screen shows this request's sourcing route badge. Requests missing a tracking number are checked automatically every morning with a Slack alert (WHOLESALE·SMART BUY → #wholesale-ops / PARTNERSHIP → #partnership-kr).`

It is display only. It exists to stop anyone from looking for the manual control that must never exist (`[BR-11]`, `[L-R12]`).

#### 3.3.10 `[L-S3-10]` Received Date column — and the absence of a Carrier column

**Behavior.** The `Received Date` column records the **View Orders scan time** automatically at the moment the request becomes `INBOUNDED`. Before that it renders an en-dash `–` in muted grey. Demo values: `07-11 14:22`, `07-09 10:05`.

**Mapping.** Feeds the Procurement Hub sheet's Received Date column (§6.4).

**Partial requests.** A `PARTIAL` request still shows `–`; Received Date marks completion, not first contact. Per-arrival timestamps live on the View Orders reception events, not in this column.

**No Carrier.** Automatic Carrier recording is **not supported**, and there is **no Carrier column** on this page (confirmed 2026-08-03, review **C-1**) `[PD-9 · OWNER-PENDING]`. QA asserts the column's absence and the absence of a carrier field on `DC-9`. The State 1 footer's contrary sentence is defect **WF-2** and must not be implemented → `[L-R9]`.

### 3.4 `[L-M1]` Modal — Add Tracking No

**Open triggers.** (a) an `Add tracking` button in a Request List row; (b) `Bulk add tracking numbers` in the bulk bar; (c) in the wireframe only, the top-bar `Modal: Add Tracking No` tab. DOM: `#m-invoice`.

**Header.** `Add Tracking No — {Inbound No.}` (demo: `Add Tracking No — 202607130003`), with an `✕` close control. *Wireframe limitation: the header is static regardless of which row opened it.*

**Body copy, verbatim.**
`Enter the tracking number(s) once the goods have shipped.`
`One inbound request can hold multiple tracking numbers (for split shipments) — every registered number becomes a View Orders match/scan target.`
`Saving activates View Orders matching for every number immediately — status stays REQUESTED; any tracking number can be scanned in at the center (full receipt switches the request to INBOUNDED)`
Purple note: `Saved numbers auto-match to View Orders — when the center scans one of these tracking barcodes, the SMART BUY sourcing route badge is shown and the scan is linked to this Inbound No. (202607130003).` — the badge shown is **the request's own route**, not always `SMART BUY`; the demo value is illustrative.

**Row model.** `#tnList` holds one or more `.qrow` rows, each an input plus a `✕` button (`.tn-del`, title `Remove this tracking number`). The first row's placeholder is `e.g. 10325661220417 — last-mile / Coupang tracking number`; appended rows use `Additional tracking number`.

**`＋ Add tracking number`** (`#tnAdd`) appends a row **and focuses its input**, so a block of numbers can be entered without touching the mouse.

**Multi-line paste.** Pasting several numbers separated by newlines, tabs, commas or semicolons into a single input **splits them across rows** rather than storing one malformed value; the split happens on paste so the operator can see and correct the result before saving (`[E-72]`).

**`✕` semantics.** Removing a row is allowed while more than one row exists. **On the last remaining row, `✕` clears the input value instead of removing the row** — the list never reaches zero rows. This is intended behavior, not a bug (`[E-37]`).

**Save validation** (`Save tracking numbers`):

1. Trim whitespace and internal formatting artifacts from every value; drop rows that are empty after trimming (`[E-58]`).
2. If **all** rows are empty after trimming → blocked, nothing saved, no toast (`[E-32]`).
3. De-duplicate within the modal: the same number entered twice saves once (`[E-33]`).
4. A number already saved on **this** request is idempotent — no duplicate row is created, no error (`[E-34]`, `[E-88]`).
5. A number already saved on **another** request is blocked with an error naming the other Inbound No. `[PD-82 · OWNER-PENDING]` (`[E-35]`); the rejection is persisted (`DC-19`).
6. Charset/length validation must be **carrier-agnostic**. Do not write a single-carrier regex — carriers differ and a single-vocabulary parser is a known failure mode. Breadth is a dev decision (§9.3) (`[E-36]`).
7. Saving to an `INBOUNDED` request is blocked; a late split shipment is registered as a **new** inbound request `[PD-85 · OWNER-PENDING]` (`[E-28]`).

**Server.** Persist `DC-3` (one entry per number, with `source=M1`), then `DC-6` (matching activation per number) **atomically with the save** — a number must never be visible in the list before it is a live match target (`[E-62]`). Double-click safe [G-9]: one save, one toast, one set of numbers (`[E-41]`); a suppressed replay persists `DC-23`.

**Concurrency.** Two operators saving different sets for the same request resolve by **server-side merge of the number set** (numbers are additive, not a replaced field), with a version check on the request itself; a genuine conflict returns 409, reloads the row, and shows a non-green toast `[PD-7 · OWNER-PENDING]` (`[E-39]`, `DC-22`).

**Network failure.** The modal stays open with values retained; retry is safe under the same idempotency key (`[E-40]`).

**Stale entity.** If the request transitioned to `INBOUNDED` between opening and saving, the server rejects with a red toast and refreshes the row — no partial write `[PD-6 · OWNER-PENDING]` (`[E-28]`).

**Feedback.** Modal closes; green top-right toast [G-2]:
`✓ Tracking number(s) saved` with secondary line `Every registered number is now matched to View Orders · No refresh`.

**Cancel.** `Cancel`, the header `✕`, and a click on the overlay backdrop all close the modal and discard unsaved rows with no server call and no event (§5.4). Only the primary `Save tracking numbers` button toasts.

**Status.** Saving numbers **never** changes status — the request stays `REQUESTED` (or `PARTIAL`).

### 3.5 Page furniture (unnumbered but normative)

#### 3.5.1 `[L-F1]` Registration confirmation toast

Two artifacts represent the same behavior. The live toast is `#gtoast`, a single reused element pinned top-right, created on demand, auto-hidden after **2600 ms** with its timer reset on each new message — so two confirming actions within 2.6 s show one toast carrying the latest message, never a stack (`[E-46]`). The Request List also carries a **static** `.toast` mock reading `✓ Inbound request registered — 202607130003` / `No refresh · added to top of the list`; it is illustration only and QA must not confuse it with `#gtoast` (`QA-C-24`).

Toast semantics are [G-2]; the page delta is the **single-slot reuse** described above. Duration, stacking policy and failure copy are dev decisions (§9.3).

#### 3.5.2 `[L-F2]` Per-row `💬 Comments` button and inline panel

**Trigger.** `💬 Comments` in a row's Actions cell (`.comment-btn`), optionally with an unread count badge (demo: `1`, `2`, `3`).

**Behavior.** Toggles an inline panel row (`.cpanel-ir`) directly beneath the request row, spanning all columns. Clicking again collapses it. The panel lists the request's comments oldest-first as `{author} · {text} · {time}`, with `@name` fragments highlighted in blue (`.at`). Rows with no comments render `No comments yet` (`[E-64]`).

**Write box.** An input with placeholder `Write a comment — @name tags trigger a Slack alert` and a `Post` button.

**Post behavior.** Empty or whitespace-only comments are blocked with no server call (`[E-65]`). A successful post appends the comment, persists `DC-10`, and for each resolved `@mention` fires the Slack route in §6.1 row 4 (`DC-17`, `DC-15`). An `@mention` that resolves to no system user posts the comment but fires no Slack notification, and the unmatched token is recorded on the event (`[E-48]`). Mention tokens adjacent to punctuation and mentions of non-ASCII display names must resolve by the same rule as elsewhere in the admin (`[E-87]`).

**Terminal requests stay commentable.** A comment may be posted on an `INBOUNDED` request; comments are the correction channel precisely when the record itself is frozen (`[E-49]`).

**Append-only** `[PD-3 · OWNER-PENDING]` — no edit control, no delete control, on any comment, ever.

#### 3.5.3 `[L-F3]` `＋ New Inbound Request` button

A blue small button at the top-left of the Request List that navigates to the `New Request` tab. No confirmation, no server call, no event.

#### 3.5.4 `[L-F4]` Result count footer line

Verbatim: `Showing 6 of 12 request(s) · Status: REQUESTED 8 · PARTIAL 1 · INBOUNDED 3`
It reports (i) rows rendered on this page of results, (ii) total rows in the current filter, (iii) the full status breakdown. The status breakdown is over all requests and must always agree with the chip counts in `[L-S3-1]`. Page size, default sort (newest-first assumed) and pagination controls are dev decisions (§9.3).

#### 3.5.5 `[L-F5]` Deep link `#reqlist` / `#s3`

Loading the page with hash `#reqlist` or `#s3` activates the **Request List** tab directly [G-12]. This is the target of the View Orders State 6 banner link. In the production admin the link resolves to the **filtered entity** — the specific Inbound No. — not just the tab (`[E-31]`, `[E-50]`). An unknown or already-satisfied hash is a no-op, never an error (`[E-50]`). Entry via deep link may be recorded as optional telemetry (`DC-16`).

#### 3.5.6 `[L-F6]` Memo (Optional)

A textarea labelled `Memo (Optional)`. State 1 placeholder: `Notes about this inbound — anything written here is also logged to the request's Comments history`. State 2 placeholder `Notes about this inbound` with demo content `Wholesale vendor direct ship — 2 pallets, forklift needed`.

**Behavior.** A non-empty memo is **materialised as the request's first comment** at registration, authored as the requester with the registration timestamp (`DC-11`, trigger `memo_materialization`). An empty memo creates nothing (`[E-16]`). Materialisation is an after-commit side effect: if it fails the request still exists and the failure is retried (`[E-83]`). Exact rendering of the auto-comment is a dev decision (§9.3).

**Rationale.** The memo and the comment thread must not diverge into two places where the same operational note might live.

#### 3.5.7 `[L-F7]` Admin top navigation bar

Inherited admin chrome, byte-accurate: brand `SkinSeoul`, menus `Operation AI ▾` `Catalog Management ▾` `OMS Center ▾` `Site Management ▾`, the Comments hub button `💬 Comments` with its unread badge (`[L-S1-14]`), the current user `Yongwon Ryu` with avatar initial `Y`, and `Logout`. No page delta on the chrome itself. A session that expires mid-form must not silently discard entered data (`[E-63]`).

#### 3.5.8 `[L-F8]` Page title block

`WMS - Inbound Request` (h2) with the sub-title `Inbound Request — New Request` on the form and `Inbound Request — Request List` on the list. Byte-accurate, including the hyphen spacing in the h2 and the em dash in the sub-title. State 1 additionally carries the tail line `Registered requests are viewed and managed by status in the [Request List] tab above.`

#### 3.5.9 `[L-F9]` Request List undotted columns

The columns not carried by a legend dot are still normative. Header order is exactly:

| # | Column | Content | Notes |
|---|---|---|---|
| 1 | (checkbox) | Row selection | Bulk bar scope, `[L-S3-2]`, `[BR-29]` |
| 2 | `Inbound No.` | `YYYYMMDDNNNN`, tabular numerals | `[L-S1-3]`; the entity key everywhere else |
| 3 | `Sourcing Route` | `[L-S3-3]` | dotted (3) |
| 4 | `Brand · Product` | Brand in **bold** + EN product name; `+N more` when the request has more lines | [G-6] brand-prefix rule |
| 5 | `SKU` | First SKU + `+N` | Mirrors the `+N more` collapse |
| 6 | `Qty` | Total expected quantity across lines; carries the `✎ old→new (token)` history when an M6 edit exists | `[L-S3-5]`, `[BR-30]` |
| 7 | `Tracking No` | `[L-S3-4]` | dotted (4) |
| 8 | `Expected arrival` | `MM-DD` | `[L-S1-8]` |
| 9 | `Received Date` | `[L-S3-10]` | dotted (10) |
| 10 | `Requested by` | Actor display name | From `DC-1` |
| 11 | `Status` | `[L-S3-5]` | dotted (5) |
| 12 | `Actions` | `💬 Comments` | `[L-F2]` |

**There is no 13th column, and specifically no `Carrier` column** (`[L-R9]`).

### 3.6 Removed / rejected — must NOT exist

Each entry has a dated Decision Log row in §10. These are recorded so no one re-implements them from a stale document or a leftover code comment.

| Key | Must not exist | Removed / rejected |
|---|---|---|
| `[L-R1]` | "View Orders link info" modal (and any link/button that would open it) | 2026-08-03 · HTML comment leftover = defect **WF-11** |
| `[L-R2]` | Inbound No. input field or preview panel on the form | 2026-07-26 |
| `[L-R3]` | FOC ("free of charge") checkbox that locks Unit Cost to ₩0 | 2026-07-26 → type `0` directly |
| `[L-R4]` | `SHIPPED` status, and any "mark as shipped" row or bulk button | 2026-07-27 |
| `[L-R5]` | Per-row product search boxes, and the separate "add row" button | 2026-07-27 → single unified search box |
| `[L-R6]` | A second submit button (register-only vs register-and-dispatch) | 2026-07-27 → one `Register Inbound Request` |
| `[L-R7]` | `Size` field on product rows | 2026-07-23 |
| `[L-R8]` | PO matching panel | 2026-07-23 → auto Inbound No. |
| `[L-R9]` | `Carrier` column, and any automatic carrier capture | 2026-08-03 `[PD-9 · OWNER-PENDING]` |
| `[L-R10]` | Result link to View Orders on an INBOUNDED row | 2026-08-03 |
| `[L-R11]` | Ad-hoc inbound registration path for unrequested arrivals | 2026-08-02 → unrecognized pool reuse |
| `[L-R12]` | Any manual status control on this page (set INBOUNDED / PARTIAL / revert) | Standing rule; reaffirmed 2026-08-02 |

---

## 4. Business Rules

Page-scoped, stable IDs. Every rule carries its rationale and its decision date. Reversals are recorded in §10.

| ID | Rule | Rationale | Decided |
|---|---|---|---|
| **BR-1** | This form is the **single intake gateway**: every warehouse inbound is declared here first. No other screen creates an inbound request. | One creation path means one place where cost, supplier and route are asserted; a second path would fork the FIFO costing basis and the sheet. | 2026-07-13 |
| **BR-2** | The origin form offers **exactly four routes**: `SMART BUY` / `WHOLESALE` / `PARTNERSHIP` / `OTHER` + free-text channel. JIT is never requestable here. | JIT is an order-side sourcing outcome, not something you request in advance; `OTHER` exists because real inbounds arrive through channels the taxonomy did not anticipate [G-5]. | 2026-07-26 |
| **BR-3** | Inbound No. is **auto-assigned `YYYYMMDDNNNN`** (`NNNN` = `0001`–`9999` per day), never entered, never previewed, shown only in the Request List. The date bucket comes from one declared server timezone. | Zero numbering coordination between requesters; maps to PH sheet column A `PO No. (=Order ID)`; named "Inbound No." so non-PO inbounds fit. | 2026-07-23 (scheme) · 2026-07-26 (preview removed) |
| **BR-4** | Field set and field order **mirror the Procurement Hub sheet columns**; there is no `Size` field. | The Request List is scraped as-is; a field the sheet cannot hold is a field that will be lost. | 2026-07-23 |
| **BR-5** | **Unit Cost is required on every row and `0` is a valid value.** | Unit Cost is the FIFO costing basis and a sheet-consistency requirement, so it must always exist; `0` is the honest value for free-of-charge stock. | 2026-07-23 (required) · 2026-07-26 (FOC checkbox retired → direct `0`) · 2026-08-03 (disclaimer repositioned) |
| **BR-6** | **JIT Price is optional for all routes, and blank must never be coerced to `0`.** | Blank means *unknown*; `0` would assert *free via JIT*. Coercion would poison downstream JIT pricing data. | 2026-07-26 (widened from Smart Buy · Wholesale only) |
| **BR-7** | **Supplier is required** (whitespace-only trims to blank and is rejected). | It is the settlement counterparty and the party whose dispatch produces the inbound tracking number. | 2026-07-23 |
| **BR-8** | **Tracking No is optional at creation** and there is exactly **one** register button; presence of a number does not change which button is used. | Purchases are usually declared before dispatch; two buttons made operators choose a workflow branch they could get wrong. | 2026-07-27 |
| **BR-9** | **One request may hold many tracking numbers**, and every registered number is an independent View Orders match/scan target. Partial arrivals accumulate against the same request. | Split shipments are normal; forcing one number per request would fragment one purchase into several inbound records [G-10]. | 2026-08-03 (confirmed) |
| **BR-10** | Status has **exactly three stages** — `REQUESTED` → `PARTIAL (n/m)` → `INBOUNDED` — and **tracking presence is not a status**. `PARTIAL` is not a mandatory stop. | `SHIPPED` duplicated information the Tracking No column already carried; `PARTIAL` was needed because real deliveries arrive in pieces. | `SHIPPED` retired 2026-07-27 · `PARTIAL` added 2026-08-02 |
| **BR-11** | **No manual status transition exists on this page.** `INBOUNDED` and `PARTIAL` are written only by View Orders scans. | Status is a physical fact. If the desk could set it, the list would stop describing the warehouse — and the "tidy the list early" failure mode would be structurally available. | Standing · reaffirmed 2026-08-02 |
| **BR-12** | **Received Date is captured automatically at the View Orders scan time on `INBOUNDED`**; pre-inbound and `PARTIAL` rows show `–`. **No Carrier is captured and no Carrier column exists.** | Received Date is a by-product of a scan that already happens; carrier data has no reliable automatic source, so capturing it would mean typing it, which nobody would do accurately `[PD-9 · OWNER-PENDING]`. | 2026-08-03 |
| **BR-13** | **Expected-quantity edits originate only in View Orders M6**, carry a mandatory reason from the [G-11] enum, recompute remaining quantity and the full-confirm gate, auto-post a comment on the request, and notify the requester on Slack. This page **displays** the resulting history and offers no edit control. | The person who can see the damaged carton is the person at the bench, not the person at the desk; one edit origin means one audit trail [G-11]. | 2026-08-02 |
| **BR-14** | `INBOUNDED` is **terminal**. Tracking numbers may not be added to an INBOUNDED request; a late split shipment becomes a new inbound request `[PD-85 · OWNER-PENDING]`. | Reopening a completed request would invalidate its Received Date and its completed reconciliation. | 2026-08-03 |
| **BR-15** | A **tracking number is unique system-wide across inbound requests**; a duplicate is blocked at save with an error naming the other Inbound No. `[PD-8 · OWNER-PENDING]` `[PD-82 · OWNER-PENDING]`. Comparison is whole-string equality after normalisation — never prefix or fuzzy matching. | View Orders must resolve a scan to exactly one request; two owners make the scan non-deterministic, and prefix matching would create phantom collisions between unrelated carriers. | 2026-08-03 |
| **BR-16** | Inbound and outbound tracking numbers are **separate namespaces and may coincide**; View Orders resolution precedence puts inbound-request tracking first `[PD-86 · OWNER-PENDING]`. | Carriers reuse number ranges across directions; the precedence rule already exists in View Orders State 6. | 2026-08-03 |
| **BR-17** | A **saved** tracking number is deletable/editable **only while no scan has matched it**; once matched it is frozen `[PD-81 · OWNER-PENDING]`. Any permitted deletion requires a confirm step and a toast `[PD-5 · OWNER-PENDING]` and persists the old value. | Removing a matched number would orphan the State 6 reconciliation that used it. | 2026-08-03 |
| **BR-18** | **The same SKU may not appear twice in one request**; a repeat pick is blocked inline with `Already added — edit the quantity on the existing row` `[PD-83 · OWNER-PENDING]`. | Two rows for one SKU double-count in the reconciliation table and in the PH sheet. | 2026-08-03 |
| **BR-19** | **Unrequested arrivals do not get an ad-hoc registration path.** They route to the shared unrecognized pool (`tracking-missing`); recovery is create-request → add tracking → remove pool row with a reason and the Inbound No. `[PD-64 · OWNER-PENDING]` → rescan enters View Orders State 6. | An ad-hoc path would be a second creation gateway with none of this form's cost/supplier/route discipline (BR-1). | 2026-08-02 |
| **BR-20** | **The Request List is the dataset the Procurement Hub sheet scrapes as-is.** Sheet integration is designed separately, as the last step. | The sheet is an existing operational artifact; the admin adapts to it, not the reverse. | 2026-07-23 |
| **BR-21** | **Morning no-tracking check** runs once per calendar day over `REQUESTED` requests with zero tracking numbers, routed by sourcing route to `#wholesale-ops` / `#partnership-kr` (`OTHER` deferred to dev). | Push beats poll: the gap reaches the owning team without anyone reading the list. | 2026-07-27 |
| **BR-22** | The label is always **`Comments`**, in every state, row and modal; never localised, never renamed. | Cross-screen consistency — the same feature must be findable by the same word everywhere. | 2026-07-13 (standardised) |
| **BR-23** | **A non-empty Memo is materialised as the request's first comment** (`source=system`), authored as the requester at the registration timestamp. | Operational notes must live in one thread, not split between a form field and a comment log. | 2026-07-27 |
| **BR-24** | After a product row is appended, **focus returns to the unified search box** with its value selected; Tab order within a new row is Order Qty → Unit Cost → JIT Price; **Enter in the search box never submits the form**. | Batch entry is a head-down keyboard loop; a stray Enter would burn an Inbound No. on a half-filled request (the same discipline [G-1] enforces on scan surfaces). | 2026-07-27 (single box) · 2026-08-03 (Enter discipline specced) |
| **BR-25** | **Comments are append-only** on this page's entities `[PD-3 · OWNER-PENDING]`; corrections are new comments. Comments may be posted on requests in any status, including `INBOUNDED`. | The comment corpus is a deliberate audit and AI-training asset [G-7]; mutability would rewrite it silently. | 2026-08-03 |
| **BR-26** | **Every mutating action on this page records the actor**, and v1 applies **no role gating** to any control here `[PD-1 · OWNER-PENDING]` [G-15]. | Six screens independently raised the same permission question; inventing per-page gates would create eight inconsistent models. Actor capture makes a later role model retrofittable. | 2026-08-03 |
| **BR-27** | **Slack delivery is never part of the transaction.** The primary action always commits; delivery failure is persisted and retried and never blocks the UI or rolls anything back `[PD-4 · OWNER-PENDING]`. The same holds for memo materialisation and telemetry. | Notification is a side effect. A failed webhook must not prevent goods from being declared. | 2026-08-03 |
| **BR-28** | **This page is not the single named [G-2] refresh exception**: no action here triggers a full-page reload, and every confirming action on it (register, M1 save, bulk add, comment post, permitted deletion) toasts. | Owner emphasis 2026-08-03 across all eight screens; a refresh here would discard an in-progress form. | 2026-08-03 |
| **BR-29** | **Select-all covers only the currently visible (filtered) rows.** Off-screen rows are never selected by a select-all, and per-row selection persists across chip switches within a session. | Selecting rows the operator cannot see is the classic bulk-action accident; the same doctrine governs bulk selection on Ready to be Outbounded. | 2026-08-03 |
| **BR-30** | **The Qty-cell edit marker renders a short reason token**, not the full [G-11] enum string, on the fixed mapping in §3.3.5. `Other (memo)` renders `other`; the memo text is never inlined into the cell. | The wireframe's `(damaged)` is narrower than the enum string it stands for; an ad-hoc abbreviation per developer would make the marker unreadable and untestable. | 2026-08-03 |
| **BR-31** | **`OTHER`-route requests with no tracking are still collected by the morning check and written to `DC-14` with `channel=unrouted`,** even though no channel receives them yet. | Without this, an entire route's chase gap is invisible: the requests would be silently skipped and nobody could measure the cost of the missing channel decision. | 2026-08-03 |

---

## 5. Data Capture

Doctrine [G-8]. This page's dataset is also the Procurement Hub scrape source (`BR-20`), so persistence here is doubly load-bearing.

Shared cross-page event names are **byte-identical** to the canonical list in `_global-rules` and must not be renamed locally (review **C-12**). All other names follow lowercase `entity.action`; literal API naming is a developer decision.

### 5.1 Events owned by this page

| ID | Event | Trigger | Actor | Payload (beyond actor + ts) | Surfaced |
|---|---|---|---|---|---|
| **DC-1** | `inbound_request.created` | `Register Inbound Request` succeeds | requester | `inbound_no`; `route` ∈ `SMART_BUY\|WHOLESALE\|PARTNERSHIP\|OTHER`; `other_channel_text` (required iff `OTHER`); `lines[]{sku, brand, product_name, order_qty, unit_cost_krw, jit_price_krw\|null, catalog_snapshot_at}`; `supplier`; `tracking_nos[]` (0..n at creation); `expected_arrival\|null`; `memo\|null`; `source` ∈ `manual\|from_unrecognized`; `idempotency_key` | Request List row + toast `[L-F1]` |
| **DC-2** | `inbound_no.allocated` | Server sequence allocation inside registration | system | `inbound_no`, `date_bucket`, `sequence_n`, `request_id` | none (silent) |
| **DC-3** | `tracking_no.added` | Number saved from the creation form, M1, or bulk | actor who saved | `request_id`, `tracking_no` (normalised), `raw_input`, `source` ∈ `create_form\|M1\|bulk`, `batch_id\|null` | Tracking No column `[L-S3-4]` |
| **DC-4** | `tracking_no.removed` | Permitted deletion/edit of a saved number `[PD-81 · OWNER-PENDING]` | actor | `request_id`, `old_value`, `new_value\|null`, `reason`, `had_matches=false` | Tracking No column; confirm + toast `[PD-5 · OWNER-PENDING]` |
| **DC-5** | `tracking_no.bulk_added` | `Bulk add tracking numbers` completes | actor | `batch_id`, `request_ids[]`, per-request `numbers[]`, `excluded_request_ids[]` + exclusion reason | Bulk result toast |
| **DC-6** | `tracking_match.activated` | Atomic with each number's save | system | `request_id`, `tracking_no`, `activated_at` | Note `{n} tracking numbers — all matching active` |
| **DC-10** | `comment.posted` | `Post` in a row panel or the hub | author | `entity_type=inbound_request`, `inbound_no`, `text`, `mentions[]`, `unresolved_mention_tokens[]` | Panel + hub `[L-F2]` `[L-S1-14]` |
| **DC-11** | `comment.auto_posted` (`source=system`) | Memo materialisation at registration; expected-qty edit; unrecognized match confirmed | system (on behalf of the causing actor) | `inbound_no`, `text`, `trigger` ∈ `memo_materialization\|expected_qty_edit\|unrecognized_match_confirmed`, `caused_by_event_id` | Comment thread |
| **DC-12** | `comment.starred` / `comment.unstarred` | `★` toggle in the hub | user | `comment_id`, per-user saved state | `★ Saved` tab |
| **DC-13** | `comment.read` / `comment.mark_all_read` | Opening a mention; `Mark all as read` | user | `comment_ids[]` | Unread badge |
| **DC-17** | `comment.mention_notified` | A resolved `@mention` is dispatched | system | `comment_id`, `mentioned_user`, `channel`, `deep_link` | none (drives §6.1 row 4) |
| **DC-14** | `morning_check.executed` | Daily no-tracking sweep runs | system (scheduler) | `run_date`, `flagged[]{inbound_no, route, supplier, requested_by, age_hours, channel}` (`channel=unrouted` for `OTHER`, `BR-31`), `per_channel_counts`, `slack_message_ts[]`, `suppressed_duplicate_run` | none (silent-failure guard) |
| **DC-15** | `slack_notification.sent` | Every outbound Slack dispatch from this page | system | `trigger_event_id`, `channel`, `payload_hash`, `result` ∈ `ok\|failed`, `attempt_n`, `error` | none |
| **DC-18** | `inbound_request.registration_rejected` | Server-side validation rejects a registration | requester | `reason_codes[]`, `field_errors[]`, submitted payload snapshot | Inline errors; no success toast |
| **DC-19** | `tracking_no.duplicate_blocked` | A save is blocked by `BR-15` | actor | `attempted_number`, `owning_inbound_no`, `attempt_source` ∈ `create_form\|M1\|bulk` | Inline error |
| **DC-22** | `inbound_request.stale_conflict_rejected` | Optimistic version check fails (`PD-6` / `PD-7`) | actor | `request_id`, `client_version`, `server_version`, `attempted_action` | Non-green toast + row reload |
| **DC-23** | `inbound_request.idempotent_replay_suppressed` | A duplicate submit is absorbed by the idempotency key [G-9] | actor | `idempotency_key`, `original_event_id`, `action` ∈ `create\|m1_save\|bulk_add` | none |
| **DC-16** | `inbound_request.viewed_via_deeplink` | Page loaded with `#reqlist` / `#s3` or an entity deep link | user | `entry_source`, `target_inbound_no\|null` | none — **dev-optional telemetry**, not doctrine-mandatory |
| **DC-20** | `inbound_request.sheet_scraped` | Procurement Hub sheet pull reads the Request List | system (integration job) | `run_ts`, `row_count`, `inbound_nos[]` or a range descriptor, `result` | none — contract stated now, mapping design deferred (§9.1) |

### 5.2 Events written elsewhere, displayed here (read-only on this page)

These are **not** this page's writes, but this page is their primary display surface and QA asserts the rendering.

| ID | Event | Written by | Payload | Surfaced here |
|---|---|---|---|---|
| **DC-7** | `inbound_request.status_changed` | View Orders State 6 (scan flow) | `request_id`, `old_status` → `new_status`, `received_so_far`, `expected_total`, `causing_scan_event_id`, operator | Status pill `[L-S3-5]`, chips `[L-S3-1]` |
| **DC-8** | `inbound_request.expected_qty_edited` | View Orders M6 | `request_id`, `line_id`, `old_qty` → `new_qty`, `reason` ∈ `damaged_defective\|supplier_qty_change\|other`, `reason_memo\|null`, editor | `✎ 300→180 (damaged)` in the Qty cell, per the `BR-30` token map |
| **DC-9** | `inbound_request.received_date_recorded` | View Orders State 6 at full receipt | `request_id`, `received_at` (= scan time). **No carrier field** `[PD-9 · OWNER-PENDING]` | Received Date column `[L-S3-10]` |
| **DC-21** | `unrecognized_pool.linked_to_request` | Unrecognized Tracking removal with reason `routed to inbound request` `[PD-64 · OWNER-PENDING]` | `pool_item_id`, `inbound_no`, `tracking_no`, resolver | Provenance on `DC-1` (`source=from_unrecognized`); closes the recovery loop (`BR-19`) |

### 5.3 Retention and export

- **Requests, lines, tracking numbers, status history, expected-qty edit history, Received Dates, and comments: retained indefinitely.** The Request List *is* the dataset the Procurement Hub sheet scrapes (`BR-20`), so truncation would break an external operational artifact.
- **Comments are an AI-training and audit asset** [G-7] and are append-only `[PD-3 · OWNER-PENDING]`; they are never purged with the request.
- **`DC-14` / `DC-15` automation logs** are retained for automation audit: they are the only evidence that the morning check actually fired on a day when it found nothing, and the only place the unrouted `OTHER` backlog is visible (`BR-31`).
- **`DC-18` / `DC-19` / `DC-22` / `DC-23` rejection records** are retained as an operational-quality signal (broken forms, training gaps, concurrency pressure, and proof that the known double-processing bug [G-9] is fixed rather than reproduced).
- **Export format** is deferred to the separate sheet-integration design (§9.1). CSV encoding and column set, if a manual export is added, are dev decisions (§9.3).

### 5.4 Explicit NON-events

Declared so developers do not over-build and so QA does not assert persistence that must not exist [G-8]:

1. Autocomplete queries and keystrokes in the unified search box.
2. Product-row add / `✕`-delete **before** submission (client draft state).
3. Field typing and route re-picks before submission.
4. Cancelled registrations (navigating away, closing the tab) — nothing is written until `Register Inbound Request` reaches the server.
5. M1 row add / `✕`-remove, modal `Cancel`, header `✕`, and backdrop dismissal — pre-save rows are client-only.
6. Filter-chip clicks, column sorts, and pagination moves.
7. Row checkbox toggles and select-all (bulk **selection** is ephemeral; only the bulk **submission** `DC-5` persists).
8. Page-tab switches (`New Request` ↔ `Request List`) and comment-panel expand/collapse.
9. Blocked client-side comment posts (empty text never reaches the server, so there is nothing to record).
10. Wireframe demo counters and static demo values — not data.

Anything operator-initiated that is not on this list **must** persist.

---

## 6. Integrations

### 6.1 Slack routing

Payload fields are verbatim from `_slack-routing.md` (CONFIRMED 2026-08-03). Channel IDs are given on first mention where the routing file publishes one; where it does not, that is recorded as an unpublished ID, not as a pending decision — the channel **names** are confirmed.

| # | Trigger (this page) | Channel | Payload fields | Mention target | Status |
|---|---|---|---|---|---|
| 1 | Morning check — request still `REQUESTED` with **no tracking number**, route `WHOLESALE` or `SMART BUY` | **#wholesale-ops** (ID not published in `_slack-routing.md`) | Inbound No., supplier, requested-by, age | none (channel-wide) | CONFIRMED 2026-07-27 · daily 1× |
| 2 | Same, route `PARTNERSHIP` | **#partnership-kr** (ID not published) | Inbound No., supplier, requested-by, age | none (channel-wide) | CONFIRMED 2026-07-27 · daily 1× |
| 3 | Same, route `OTHER` | **no channel yet** — deferred to development (§9.3 D-1). Rows are still collected and persisted with `channel=unrouted` (`BR-31`) | same | — | Open, dev-owned |
| 4 | Comment `@mention` on an inbound request (row panel or hub) | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) | entity no. (Inbound No.), comment text, time, author, @mentioned user, deep link to the request | the mentioned person, `@`-tagged in the message body | CONFIRMED by owner 2026-08-03 (review **C-2**) |
| 5 | **Expected-qty edit** auto-comment (originating in View Orders M6, landing on this request) | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) | old→new qty, reason, editor | **@requester** of this inbound request | CONFIRMED 2026-08-03 |
| 6 | **Unrecognized match confirmed** where the resolution routes to an inbound request | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) | tracking no., matched product line, resolver | @registrant (suppressed when resolver == registrant `[PD-16 · OWNER-PENDING]`) | CONFIRMED 2026-08-03 · owned by `tracking-missing`, referenced here for the recovery loop |

**Adjacent route, not fired from this page:** unrecognized barcode registration → **#unrecognized-tracking** (ID not published), owned by the `tracking-missing` spec. It appears here only because `BR-19`'s recovery loop begins there.

**Delivery semantics.** The `@mention` sits **in the message body**, so Slack raises a personal notification while the channel doubles as a team-visible archive [G-7]. Dispatch results are persisted (`DC-15`); failures are retried and never block or roll back the primary action `[PD-4 · OWNER-PENDING]` (`BR-27`). Retry policy is a dev decision.

**No other Slack route exists on this page.** Registration, M1 save, bulk add, and status transitions do **not** notify Slack. Adding one would create an unowned alert stream.

### 6.2 Cross-page links and deep links

| Direction | Link | Contract |
|---|---|---|
| **Inbound** | View Orders **State 6** banner → `../inbound-request/#reqlist` | Opens the **Request List** tab [G-12]. In the production admin it deep-links to the **filtered entity** (the specific Inbound No.), not just the tab. `[L-F5]` |
| **Inbound** | Comments hub entries (any screen) whose entity is an inbound request | Click opens this page focused on that request; an unresolvable target renders an "entity unavailable" state (`[E-86]`) |
| **Outbound** | **none** | The "View Orders link info" modal and the INBOUNDED result link were both removed 2026-08-03 → `[L-R1]`, `[L-R10]`. QA asserts their absence. |

### 6.3 Cross-page data contracts

| Consumer | What this page supplies | Where it is consumed |
|---|---|---|
| **View Orders** — scan resolution | The registry of live tracking numbers per request (`DC-3` + `DC-6`) | A scanned barcode matching a registered inbound number enters **State 6** (internal inbound), not the customer-order view. Inbound-request tracking takes **precedence** over customer-order tracking `[PD-86 · OWNER-PENDING]` |
| **View Orders** — badges | Sourcing route (incl. `OTHER ({channel})` `[PD-80 · OWNER-PENDING]`) | Rendered as a black bold badge on the scan screen [G-5] |
| **View Orders** — State 0 | `Expected arrival` dates of open requests | Feeds the **"Expected Inbound N"** summary badge and its expandable table (2026-08-02) |
| **View Orders** — State 6 / M5 / M6 | Expected quantities per line | Drives the exact-match full-confirm gate, `Save Partial`, and the expected-qty edit that writes back `DC-8` |
| **Inventory** (`stock-status`) | Sourcing route (incl. `OTHER` channel text) | Route filter values |
| **Unrecognized Tracking** (`tracking-missing`) | Inbound No. as the structured target of removal reason `routed to inbound request` `[PD-64 · OWNER-PENDING]` | Closes the `BR-19` recovery loop (`DC-21`) |

### 6.4 Sheet handoff — Procurement Hub

- **Target:** the Procurement Hub Google Sheet. Spreadsheet id `18YIbjsKXmFW6rWhkBByv-x5g0sAsZgcqmnzcKCZKhPY`, gid `986511981`. *(Provenance note: this identifier comes from the operational Procurement Hub project, not from any `_inputs/` document — the developer must re-confirm it against the live artifact before wiring anything to it.)*
- **Direction:** the sheet **scrapes the Request List as-is** (`BR-20`). This admin does not write into the sheet in v1.
- **Known mapping:** Inbound No. → sheet column A `PO No. (=Order ID)`. The form's field order (`Inbound No. → Channel → SKU No. → Brand → Product Name → Order Qty → Unit Cost (KRW) → JIT Price (KRW) → Supplier`) mirrors the sheet's column order by design, and `Received Date` maps to the sheet's Received Date column.
- **Deferred:** the full column mapping, scrape cadence, authentication and failure handling are the separate sheet-integration design, agreed 2026-07-23 to be the **last** step (§9.1). The `DC-20` event contract is stated now so the integration is auditable when it lands.
- **Consistency requirement:** the scrape must read a committed snapshot; a half-written registration is never visible to it (`[E-18b]` = `[E-59]`).
- **Out of scope:** the **Procurement Hub admin page** itself is excluded from this plan entirely (2026-08-02).

### 6.5 Print pipeline

**N/A on this page** [G-4]. There is no Print button, no label, no picking artifact and no printable report on Inbound Request. The print surfaces are View Orders, Ready to be Outbounded, and Order Detail. QA asserts the absence of any print control here (`QA-G-10`).

---

## 7. Edge Cases & Error States

IDs are page-scoped and stable. `[E-1]`–`[E-46]` are inherited from the planning catalogue and keep their original meanings; `[E-47]`–`[E-92]` extend it. Merged entries keep both IDs and are listed under both.

> **Retired ID.** The draft of this spec carried a key `E-c1` merged onto `[E-16]`. That merge was wrong — `[E-16]` is *empty Memo*, while `E-c1` was *empty comment post*, an unrelated case — and `E-c1` also violated the `[E-{n}]` key convention. `E-c1` is **retired and must not be reused**; the empty-comment case is now `[E-65]`. `[E-16]` is unchanged.

**Total: 93 edge cases** (`E-1` … `E-92`, plus the merged alias `E-18b`; no numbering gaps).

### 7.1 New Request — form validation

| ID | Situation | Expected behavior |
|---|---|---|
| **E-1** = **E-14** | Submit with zero product rows (never added, or all deleted) | Blocked before any server call; inline error on the product section; no success toast; `DC-18` persisted |
| **E-2** | A row has an empty `Order Qty` | Blocked; the offending row is highlighted and its Qty input focused |
| **E-3** | A row has an empty `Unit Cost (KRW)` | Blocked (required) with an inline error; `0` is the value for free stock, blank is not |
| **E-4** | `Unit Cost = 0` | **Accepted.** Free-of-charge stock. No warning, no extra confirmation |
| **E-5** | `JIT Price` blank | **Accepted.** Stored as `null`, never `0` (`BR-6`) |
| **E-6** | Negative, fractional, or non-numeric value in Qty / Unit Cost / JIT Price | Rejected at input or at submit; inline error naming the field |
| **E-7** | Comma-grouped or space-padded numeric input (`" 15,000 "`) | Parsed as `15000`; display re-formats to `15,000` |
| **E-8** | Route `Other` selected with an empty channel name | Blocked; inline error; focus moved to `.etc-in` |
| **E-9** | Route switched **after** product rows exist | All rows and all entered values retained (route is request-level) |
| **E-10** | `Supplier` empty | Blocked with an inline error |
| **E-11** | Unified search returns no match | Explicit no-result affordance in the dropdown; no row appended; no crash; no submit |
| **E-12** | The same SKU is picked twice | Blocked with the inline notice `Already added — edit the quantity on the existing row`; no second row `[PD-83 · OWNER-PENDING]` |
| **E-13** | Operator attempts to type/paste into `SKU No.` / `Brand` / `Product Name` | Impossible — cells are `readonly` with `pointer-events:none`; the only correction is `✕` + re-search |
| **E-15** | `Expected arrival` in the past | Allowed with a non-blocking warning (back-dated requests are legitimate) |
| **E-16** | `Memo` empty | No auto-comment is created |
| **E-47** | `Other` channel name is whitespace-only or exceeds the field length | Whitespace-only trims to empty → blocked (`E-8`); length cap is a dev decision |
| **E-54** | `Expected arrival` left blank | Accepted; the Request List cell renders empty; the request is excluded from the "Expected Inbound" badge |
| **E-55** | `Unit Cost` entered with a currency symbol or decimals (`₩15,000.00`) | Symbol and grouping stripped; a non-zero fractional part is rejected with an inline error (KRW is integral) |
| **E-56** | A single request with a very large number of lines (e.g. 200 SKUs) | Must not break the form or the Request List row rendering; the `Brand · Product` cell collapses to `+N more`; paging/perf handling is a dev decision |
| **E-57** | Switching page tabs with an unsaved draft, or browser back/forward | Either warn or persist the draft client-side — never silently discard entered rows (dev decision, §9.3 D-6) |
| **E-63** | Session expires / user logged out mid-form | The form's entered data must not be silently lost; re-authentication returns to the populated form or the draft is preserved |
| **E-66** | The picked catalog product is deleted or renamed between selection and submit | Registration proceeds against the **snapshot captured at selection** (SKU / brand / name are copied onto the line); the divergence is recorded on `DC-1`. Registration is never blocked by a catalog edit |
| **E-67** | The catalog returns two entries for one SKU | The search surfaces the ambiguity (both entries, distinguishable) instead of silently picking one; if only one can be resolved server-side the registration is blocked with an explicit message |
| **E-68** | A matched SKU is inactive or discontinued | Either excluded from results or shown with an explicit inactive marker — never presented as an ordinary match (choice is a dev decision, §9.3 D-21) |
| **E-69** | `Order Qty` above the declared per-line maximum, or large enough to overflow | Rejected with an inline error; never truncated, wrapped, or stored as a clamped value |
| **E-70** | `Supplier` contains only whitespace | Trims to empty → blocked exactly as `E-10` |
| **E-71** | Full-width or IME-composed digits in a numeric field (`１５０００`) | Normalised to ASCII digits before validation and stored as `15000`; a value that is still non-numeric after normalisation is rejected |
| **E-78** | Two requests use `Other` channel names differing only by case or padding (`Gmarket` / `gmarket ` ) | Stored trimmed with case preserved for display, but treated as one channel when grouped downstream — they must not become two channels |
| **E-79** | `Other` channel name contains Slack or markdown control characters | Stored verbatim; escaped at render time in Slack payloads, in the Request List, and in the sheet handoff. Never stripped from storage |
| **E-90** | Keyboard-only operation of the route cards and the search box | Arrow-key selection + `Space` produce the same `on` class, the same `.etc-in` enable/focus, and the same appended row as a mouse click; `Enter` in the search box still never submits (`BR-24`) |

### 7.2 Registration, idempotency and concurrency

| ID | Situation | Expected behavior |
|---|---|---|
| **E-17** | `Register Inbound Request` double-clicked | Exactly **one** request and **one** Inbound No. Client debounce + server idempotency key [G-9]; the suppressed replay persists `DC-23`. The known current-admin double-processing bug must be fixed, not reproduced |
| **E-18** | Network failure mid-registration | Error state, form values retained, retry safe under the same idempotency key; no orphan Inbound No. that maps to no request |
| **E-19** | Two operators register in the same second | Distinct sequential `NNNN`; no collision; server-side sequence only |
| **E-20** | Daily sequence overflow (`NNNN` > 9999) | Loud failure: registration blocked, red toast [G-2], attempt persisted. Must never wrap or reuse |
| **E-21** = **E-35** | Tracking number supplied at creation already exists on **another** request | Blocked at save with an error naming the other Inbound No. `[PD-82 · OWNER-PENDING]`; `DC-19` persisted |
| **E-22** | Inbound tracking number collides with a **customer-order (outbound)** tracking number | **Allowed** — separate namespaces. View Orders resolves inbound-request tracking first `[PD-86 · OWNER-PENDING]` |
| **E-18b** = **E-59** | The Procurement Hub scrape runs while a registration is in flight | The scrape reads a consistent committed snapshot; a half-written request is never visible |
| **E-74** | A form opened at 23:58 is submitted at 00:02 | The Inbound No. date bucket is the **submission** date, resolved from the declared server timezone; the new day's sequence starts at `0001`. The client clock is never authoritative |
| **E-83** | Registration commits but memo materialisation (or telemetry) fails afterwards | The request exists, the toast fires, the failure is persisted and retried. After-commit side effects never roll back the request (`BR-27`) |
| **E-88** | A number entered at creation is later re-entered in M1 on the **same** request | Idempotent — no duplicate `DC-3`, no error, no second match activation |

### 7.3 Request List

| ID | Situation | Expected behavior |
|---|---|---|
| **E-23** | A status chip yields 0 results | Explicit empty state; the chip's count reads `0`; the footer line reflects the filtered totals |
| **E-24** | Bulk bar with 0 rows selected | `Bulk add tracking numbers` disabled |
| **E-25** | Bulk selection includes `INBOUNDED` rows | Those rows are excluded from the operation and reported in the result toast (`BR-14`) |
| **E-26** | A new registration arrives while a status filter is active | The row appears only under a matching chip; the success toast fires regardless; chip counts update |
| **E-27** | A row already has tracking numbers | Numbers render as a list with the `{n} tracking numbers — all matching active` note; **no duplicate `Add tracking` button** appears. Adding more goes through the bulk bar (§3.3.2) |
| **E-28** | An `INBOUNDED` row | No `Add tracking` button; adding numbers is blocked; a late split shipment becomes a **new** request `[PD-85 · OWNER-PENDING]` |
| **E-29** | An M6 expected-qty edit exists | The Qty cell renders `✎ {old}→{new} ({token})`, e.g. `✎ 300→180 (damaged)`; absent when no edit exists |
| **E-30** | Partial receipt recorded | Status pill renders `PARTIAL {received}/{expected}` (e.g. `PARTIAL 120/180`) and updates after each View Orders partial save |
| **E-31** | Deep link `#reqlist` or `#s3` | Request List tab is active on load [G-12] |
| **E-50** | Deep link when the target tab is already active, or an unknown hash | No-op; no error; the page renders normally |
| **E-60** | A bulk add would apply the same number to two or more requests in one batch | Blocked for the second and subsequent requests, named in the result toast; `DC-19` per rejection (`BR-15`) |
| **E-61** | First-run list with zero requests ever created | Explicit empty state; `All 0` chip; the `＋ New Inbound Request` button remains the obvious next action |
| **E-80** | An M6 edit used reason `Other (memo)` | The Qty-cell token renders `other`; the memo text is **not** inlined into the cell — it is readable in the `title` attribute and in the auto-comment (`BR-30`) |
| **E-81** | A line has been expected-qty-edited more than once | The Qty cell renders only the **most recent** edit as `✎ {previous}→{current} ({token})`; the full chain lives in the comment thread. The cell never grows unbounded |
| **E-82** | An expected-qty edit lands on one line of a **multi-line** request | The Qty cell shows the request's **total** expected quantity with the edit marker present; per-line attribution lives in View Orders and in the auto-comment |
| **E-84** | Bulk selection spans more than one page of results | Select-all covers only the visible page (`BR-29`); a selection carried across pages must be shown in the bulk-bar count, and a live insert must not push a selected row off-page without the count line reflecting it |
| **E-85** | `#reqlist` deep link arrives while an unsaved New Request draft exists | Same rule as a tab switch (`E-57`): warn or preserve — never silently discard |
| **E-89** | A request goes `REQUESTED → INBOUNDED` with no intermediate `PARTIAL` | Fully supported; Received Date fills at that moment; the `PARTIAL` stage is optional, not mandatory (`BR-10`) |
| **E-92** | Over-receipt: `n > m` (e.g. `PARTIAL 200/180`) | The pill renders the true numbers **unclamped and unre-ordered**; full confirmation stays blocked until resolved by an M6 edit or a partial save `[PD-12 · OWNER-PENDING]` |

### 7.4 M1 — Add Tracking No modal

| ID | Situation | Expected behavior |
|---|---|---|
| **E-32** | Save with all inputs empty | Blocked; modal stays open; no server call; no success toast |
| **E-33** | The same number entered twice **within** the modal | De-duplicated to one saved number (or blocked with a message); never two identical rows persisted |
| **E-34** | A number already saved on **this** request re-entered | Idempotent — no duplicate persisted, no error |
| **E-35** = **E-21** | A number already on a **different** request | Blocked, error names the other Inbound No.; `DC-19` |
| **E-36** | Whitespace, hyphens, or carrier-specific formatting | Trimmed and normalised; validation must be **carrier-agnostic** — no single-carrier regex |
| **E-37** | `✕` on the **last remaining** row | The value is cleared and the row **remains**; the list never reaches 0 rows (intended behavior) |
| **E-38** | Attempt to remove a saved number that already has scans against it | **Blocked** `[PD-81 · OWNER-PENDING]`; correction goes through a comment and, if needed, a new request |
| **E-39** | Two operators open M1 on the same request and save different sets | Server-side **merge** of the number set (numbers are additive); a genuine version conflict returns 409, reloads the row, and shows a non-green toast `[PD-7 · OWNER-PENDING]`; `DC-22` persisted |
| **E-40** | Network failure on save | Modal stays open, values retained, retry safe [G-9] |
| **E-41** | `Save tracking numbers` double-clicked | One save, one toast, one set of numbers; `DC-23` persisted |
| **E-58** | Two entered numbers differ only by leading/trailing whitespace | Normalised to one number before the duplicate check |
| **E-62** | A number is scanned in View Orders before its M1 save transaction commits | The scan does not match (the number is not yet a live target); after commit the rescan matches. Save and match activation are atomic (`DC-3` + `DC-6`) |
| **E-72** | A dispatch email block of several numbers is pasted into one input | Split across rows on paste using newline / tab / comma / semicolon separators, so the operator can verify before saving. It must never be stored as one concatenated value |
| **E-73** | A number that is a strict prefix or superset of an existing number (`1032566122041` vs `10325661220417`) | Treated as a **different** number; both may coexist. Uniqueness and matching are whole-string equality after normalisation only (`BR-15`) |

### 7.5 Cross-page lifecycle

| ID | Situation | Expected behavior |
|---|---|---|
| **E-42** | M6 sets a new expected qty **below** the already-received qty | Hard-blocked in View Orders with `New expected qty cannot be lower than the received qty ({n})` `[PD-14 · OWNER-PENDING]`; this page renders no history for a blocked edit |
| **E-43** | M6 edits expected qty **down to exactly** the received qty | Gating recomputes and `Confirm Full Inbound` re-enables; **no auto-transition** to `INBOUNDED` `[PD-84 · OWNER-PENDING]`; the pill stays `PARTIAL` until a human confirms |
| **E-44** | The same tracking number is rescanned after a `PARTIAL` save | Reconciliation resumes from the remainder; no double-count; the `n/m` badge advances |
| **E-45** | An arrival with **no** matching request | Routes to the unrecognized pool on `tracking-missing`; **not** an ad-hoc registration here `[L-R11]` (`BR-19`). Owned by the `tracking-missing` and View Orders specs |
| **E-46** | Two confirming actions within 2.6 s | A single `#gtoast` element is reused; the latest message wins; the hide timer resets; toasts never stack |
| **E-53** | A request created as pool recovery (`source=from_unrecognized`) while the pool row still exists | Both must be reconcilable: `DC-1` carries the provenance, `DC-21` links the pool item, and the pool row is removed with reason `routed to inbound request` carrying this Inbound No. `[PD-64 · OWNER-PENDING]` |
| **E-91** | A request's catalog line is deleted from the catalog **after** registration | The request keeps rendering its stored snapshot; the Request List and the sheet scrape never show a blank product. Reconciliation in View Orders State 6 uses the stored SKU |

### 7.6 Comments, Slack and automation

| ID | Situation | Expected behavior |
|---|---|---|
| **E-48** | `@mention` of a name that resolves to no system user | The comment posts; **no** Slack notification fires; the unmatched token is recorded on `DC-10` |
| **E-49** | Comment posted on an `INBOUNDED` (terminal) request | **Allowed** — comments are the correction channel for frozen records (`BR-25`) |
| **E-64** | Comment panel opened on a request with no comments | Panel renders `No comments yet` plus the write box |
| **E-65** | Empty or whitespace-only comment post attempted *(was `E-c1`, retired)* | Blocked client-side; `Post` performs no action; no server call, so no event (§5.4 item 9) |
| **E-51** | Slack dispatch fails (morning check or `@mention`) | The primary action stands; failure persisted (`DC-15`, `result=failed`) and retried; nothing is rolled back `[PD-4 · OWNER-PENDING]` |
| **E-52** | The morning check job runs twice on one calendar day (scheduler retry) | Idempotent per `run_date` — no second post; the suppressed execution is recorded on `DC-14` |
| **E-75** | An `OTHER`-route request has no tracking and no channel is configured | The request is still collected and written to `DC-14` with `channel=unrouted`; **no Slack post is invented**. The unchased backlog is measurable from the run record (`BR-31`) |
| **E-76** | The morning check finds zero qualifying requests | No Slack post; `DC-14` is still written with an empty `flagged[]` so the run is provably alive |
| **E-77** | The morning check delivers to one channel and fails on the other | Per-channel results on `DC-15`; only the failed channel is retried; the successful post is never duplicated |
| **E-86** | A Comments-hub entry points at a request that no longer resolves | Non-crashing "entity unavailable" state; navigation does not dead-end or throw |
| **E-87** | `@mention` token adjacent to punctuation, or of a non-ASCII display name | Resolved by the same admin-wide mention rule as every other screen; a token that cannot be resolved falls to `E-48` |

### 7.7 Permissions

Under v1's single admin role `[PD-1 · OWNER-PENDING]` [G-15] there are **no permission-denied states** on this page. Every authenticated admin may create requests, add tracking numbers, bulk add, and comment; every such action records the actor (`BR-26`). A future role model would gate creation and tracking entry separately — that is a post-v1 owner decision.

---

## 8. QA Acceptance Criteria

**How to run.** The target for `[WF]` scenarios is the live wireframe `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/inbound-request/`, exactly as published today. `[ADMIN]` scenarios are deferred until the real admin exists; they are written now so nothing is lost. An agent executing the `[WF]` set needs no information beyond this section.

**Tier definitions.**
- **[WF]** — executable on the live wireframe now, with the exact selector/label and the exact expected string given.
- **[ADMIN]** — assertable only against the real build (persistence, filtering, Slack dispatch, server idempotency, validation blocking).

### 8.0 Navigation preamble (referenced by every scenario)

| Step | Action | Post-condition |
|---|---|---|
| **N1** | Load the live URL with **no hash** | `#s1` has class `on`; top-bar `.wf-tab` labelled `1 · New Request (Smart Buy)` has class `on` |
| **N2** | Click the top-bar button labelled `2 · New Request (Wholesale / Partnership)` (`.wf-tab[data-state="s2"]`) | `#s2` has class `on` |
| **N3** | Click the top-bar button labelled `3 · Request List (Requested/Partial/Inbounded)` (`.wf-tab[data-state="s3"]`) | `#s3` has class `on` |
| **NM** | Click the top-bar button labelled `Modal: Add Tracking No` (`.wf-tab[data-modal="m-invoice"]`) | `#m-invoice` has class `open` |
| **NR** | Load the live URL with hash `#reqlist` (or `#s3`) | `#s3` has class `on` on first paint |
| **NX** | Reload the page | All state resets; `#gtoast` is absent or hidden; `#m-invoice` is closed |

Unless a scenario names a different step, every `[WF]` scenario begins from **N1** on a freshly loaded page (**NX**).

**Wireframe reality baseline** (assert nothing beyond this in `[WF]` scenarios): route cards toggle `.on` and `Other` enables + focuses `.etc-in`; filter chips toggle `.on` but do **not** filter rows; row checkboxes are inert; `Register Inbound Request` **always** fires `#gtoast` regardless of input; the M1 header is static; `＋ Add tracking number` appends rows and last-row `✕` clears instead of removing; `.comment-btn` injects a `.cpanel-ir` row from the static `IR_COMMENTS` map; the Comments hub dropdown is wired only in State 1; the autocomplete list is static and does not respond to typing.

**Counts.** **115 scenarios** — Block A 30 · B 7 · C 24 · D 17 · E 11 · F 10 · G 16.
Tier split: **51 `[WF]`-only · 62 `[ADMIN]`-only · 2 dual-tier** (`QA-A-19`, `QA-A-25`) — so 53 scenarios carry a `[WF]` assertion and 64 carry an `[ADMIN]` assertion.
**50 negative tests (43.5 %)**, well above the 25 % floor.

### Block A — New Request form `[L-S1-1]`…`[L-S1-16]`, `[L-S1-F]`, `[L-F6]`, `[L-F8]`

**QA-A-01** `[WF]` — covers `[L-F8]`, `[L-S1-16]`
Given **N1**
Then `#s1` has class `on`, the `h2` reads exactly `WMS - Inbound Request`, and the `.sub` reads exactly `Inbound Request — New Request`
And `.pagetabs` contains exactly two buttons labelled `New Request` and `Request List`, with `New Request` carrying class `on`
And the trailing paragraph reads exactly `Registered requests are viewed and managed by status in the [Request List] tab above.`

**QA-A-02** `[WF]` — covers `[L-S1-2]`
Given **N1**
Then `#s1 .routecards` contains exactly **4** `.routecard` elements whose `<b>` titles are `Smart Buy`, `Wholesale`, `Brand Partnership`, `Other`
And their `.rc-badge` texts are exactly `SMART BUY`, `WHOLESALE`, `PARTNERSHIP`, `OTHER`
And the first card carries class `on`
And **no card is labelled `JIT`** — JIT is never a requestable inbound route (`BR-2`).

**QA-A-03** `[WF]` — covers `[L-S1-2]`
Given **N1**
When I click the `.routecard` containing the title `Wholesale`
Then that card gains class `on`, the `Smart Buy` card loses it, and exactly one `.routecard` in `#s1 .routecards` carries `on`.

**QA-A-04** `[WF]` — covers `[L-S1-2]`
Given **N1**
When I click the `.routecard` containing the title `Other`
Then that card gains class `on`, its `.etc-in` input (placeholder `Enter channel name`) has `disabled === false`, and it is `document.activeElement`.

**QA-A-05 (negative)** `[WF]` — covers `[L-S1-2]`
Given **N1** and I have clicked `Other`
When I then click `Smart Buy`
Then the `Other` card's `.etc-in` has `disabled === true` again and no longer holds focus, and the `Other` card no longer carries `on`.

**QA-A-06 (negative)** `[ADMIN]` — covers `[L-S1-2]` / `[E-8]`, `[E-47]`
Given route `Other` is selected and the channel name is empty or whitespace-only
When I click `Register Inbound Request`
Then registration is blocked, an inline error appears on the channel-name field, focus moves to it, **no request is created**, and **no success toast fires**
And `inbound_request.registration_rejected` (`DC-18`) is persisted with the field error.
*Wireframe limitation: the static page always toasts — do not assert the block on the wireframe.*

**QA-A-07** `[WF]` — covers `[L-S1-5]`
Given **N1**
Then the `#s1 .auto input` placeholder reads exactly `Type any SKU No. · brand · product name → click a suggestion to add a row below` and its value is `100045210`
And the dropdown shows exactly 3 `.opt` rows, the first carrying class `sel` and reading `Anua — Heartleaf 77% Soothing Toner, 250ml` with `100045210`
And the remaining two read `Anua — Heartleaf 80% Moisture Soothing Ampoule, 30ml` / `100045233` and `Anua — Heartleaf Quercetinol Pore Deep Cleansing Foam, 150ml` / `100045240`.

**QA-A-08** `[ADMIN]` — covers `[L-S1-5]`, `[L-S1-6]`, `BR-24`
When I type a brand name and click a suggestion
Then one new row is appended to `.prodtbl tbody` with class `prefill`, its SKU / Brand / Product Name prefilled and `readonly`, and its Qty / Unit Cost / JIT inputs empty
And **focus returns to the unified search box** with its value selected
And tabbing from Order Qty moves to Unit Cost, then to JIT Price.

**QA-A-09 (negative)** `[ADMIN]` — covers `[L-S1-5]`, `BR-24`
Given the cursor is in the unified search box and the suggestion list is closed
When I press `Enter`
Then the form is **not** submitted, no request is created, no toast fires, and the page does not navigate.

**QA-A-10 (negative)** `[WF]` — covers `[L-S1-6]` / `[E-13]`
Given **N1** and the third `.prodtbl tbody tr` (class `prefill`)
Then its SKU, Brand and Product Name `input` elements each carry the `readonly` attribute and resolve to computed `pointer-events: none`
When I attempt to type into any of them
Then their values are unchanged (`100045210`, `Anua`, `Heartleaf 77% Soothing Toner, 250ml`).

**QA-A-11** `[WF]` — covers `[L-S1-6]`
Given **N1**
Then `#s1 .prodtbl tbody` contains exactly 3 rows, exactly one of which carries class `prefill`
And every row contains exactly one `.rm` button with `title="Delete row"` and text `✕`.

**QA-A-12 (negative)** `[ADMIN]` — covers `[L-S1-6]` / `[E-12]`
Given a row for SKU `100040311` already exists
When I select the same SKU from the search box again
Then no second row is appended and the inline notice `Already added — edit the quantity on the existing row` appears `[PD-83 · OWNER-PENDING]`.

**QA-A-13** `[WF]` — covers `[L-S1-10]`, `[L-S1-11]`, `[L-S1-4]`
Given **N1**
Then the `#s1 .prodtbl` header cells read exactly, in order: `SKU No.`, `Brand`, `Product Name`, `Order Qty`, `Unit Cost (KRW) *`, `JIT Price (KRW)`, and one empty cell
And the disclaimer paragraph above the table contains the exact substrings `enter 0 if free of charge (required)` and `leave blank if unknown (optional)`
And the `prefill` row's Unit Cost placeholder is `Per-unit price ₩ (0 if free)` and its JIT placeholder is `Blank if unknown`.

**QA-A-14 (negative)** `[ADMIN]` — covers `[L-S1-10]` / `[E-3]`, `[E-4]`
When I submit a row with `Unit Cost` empty
Then registration is blocked with an inline error on that cell
And when I set the same cell to `0` and resubmit, registration **succeeds** and the persisted line carries `unit_cost_krw = 0`.

**QA-A-15 (negative)** `[ADMIN]` — covers `[L-S1-11]` / `[E-5]`, `BR-6`
When I submit a row with `JIT Price` left blank
Then registration succeeds and the persisted line carries `jit_price_krw = null`
And the value is **not** `0` in the record, in any export, or in the sheet handoff.

**QA-A-16 (negative)** `[ADMIN]` — covers `[L-S1-4]` / `[E-6]`, `[E-7]`, `[E-55]`, `[E-71]`
When I enter, across five attempts, `-5`, `abc`, `15,000`, `₩15,000.00`, and the full-width string `１５０００` in Unit Cost
Then `-5`, `abc` and `₩15,000.00` are rejected with an inline error naming the field
And `15,000` and `１５０００` are both accepted and persisted as the integer `15000`.

**QA-A-17** `[WF]` — covers `[L-S1-7]`, `[L-S1-12]`, `[L-S1-8]`
Given **N1**
Then the `Supplier` field carries a red `*`, the qualifier `— who is shipping the goods`, placeholder `e.g. 비엠유통, Coupang`, and value `Coupang`
And the `Tracking No` field's wrapper has class `fld-inv`, its label contains `optional · can be added later after dispatch`, and its placeholder is `Add after dispatch — you can submit without it (add later)`
And `Expected arrival` is an `input[type=date]` with value `2026-07-16`.

**QA-A-18** `[WF]` — covers `[L-S1-7]`, `[L-F1]`, `[G-2]`
Given **N1**
When I click the button with exact label `Register Inbound Request`
Then `#gtoast` becomes visible at the top right containing the exact bold text `✓ Inbound request registered` and the secondary line `Inbound No. auto-assigned · added to the Request List · No refresh`
And the URL is unchanged and the form is still in the DOM (no navigation, no reload)
And after 2600 ms `#gtoast` is hidden again.

**QA-A-19 (negative)** `[WF]` + `[ADMIN]` — covers `[L-S1-3]`, `[G-9]` / `[E-17]`, `[E-46]`
Given **N1**
When I click `Register Inbound Request` twice within 500 ms
Then exactly **one** element with id `gtoast` exists in the DOM and its hide timer has been reset — toasts never stack `[WF]`
And exactly **one** request and **one** Inbound No. are created, and `inbound_request.idempotent_replay_suppressed` (`DC-23`) is persisted `[ADMIN]`.

**QA-A-20** `[ADMIN]` — covers `[L-S1-3]`, `[L-F6]`, `DC-1`, `DC-2`, `DC-11`
When a registration succeeds with a non-empty Memo
Then `inbound_request.created` (`DC-1`) is persisted carrying actor, timestamp, `inbound_no` matching `^\d{12}$`, route, all lines with `unit_cost_krw`, supplier, and `source=manual`
And `inbound_no.allocated` (`DC-2`) is persisted with the same `inbound_no`
And `comment.auto_posted` (`DC-11`) is persisted with `trigger=memo_materialization`, authored as the requester at the registration timestamp.

**QA-A-21 (negative)** `[ADMIN]` — covers `[L-S1-1]` / `[E-1]`, `[E-14]`
When I click `Register Inbound Request` with zero product rows
Then no server call is made, an inline error appears on the product section, no toast fires, and `DC-18` is persisted.

**QA-A-22 (negative)** `[ADMIN]` — covers `[L-S1-12]` / `[E-10]`, `[E-70]`
When I clear `Supplier`, and separately when I fill it with spaces only, and submit each time
Then registration is blocked with an inline error on `Supplier` in both cases.

**QA-A-23** `[WF]` — covers `[L-S1-9]`, `[L-R1]`
Given **N1**
Then a `.note.purple` element exists containing the exact substring `auto-matches it to View Orders`
And **no `<a>`, no `<button>`, and no element carrying a `data-modal` attribute exists inside it** — the "View Orders link info" modal must not be reachable from this page.

**QA-A-24** `[WF]` — covers `[L-F6]`
Given **N1**
Then a `textarea.mtextarea` under the label `Memo (Optional)` exists with placeholder `Notes about this inbound — anything written here is also logged to the request's Comments history` and an empty value.

**QA-A-25** `[WF]` + `[ADMIN]` — covers `[L-S1-15]`
Given **N1** `[WF]`
Then `#s1 .pagepad` resolves to computed padding `18px 16px 0px`, `#s1 .mock` declares `min-width: 1280px`, and `#s1 .submitrow` (containing `Register Inbound Request`) is present in the DOM inside `#s1 .formcard`
And `[ADMIN]` at the target admin viewport width the complete form from the route cards through the `Register Inbound Request` button is visible without vertical scrolling — a build in which `.submitrow` falls below the fold is a regression.

**QA-A-26** `[WF]` — covers `[L-S1-F]`(c), `BR-22`
Given **N1**, then **N3**
Then every comments affordance on the page is labelled with the exact word `Comments`: the nav button reads `💬 Comments`, each Request List Actions button reads `💬 Comments`, and the hub tabs read `@ Mentions` and `★ Saved`
And no localised or alternative label (e.g. `메모`, `Notes`, `Remarks`) appears on any comments control.

**QA-A-27 (negative)** `[ADMIN]` — covers `[L-S1-F]`(a), `[L-R9]`, `[PD-9 · OWNER-PENDING]`
Then the New Request form exposes **no Carrier input, select, or hidden field**
And `inbound_request.created` (`DC-1`) and `inbound_request.received_date_recorded` (`DC-9`) carry **no carrier attribute**
And nothing in the build reads the stale State 1 footer clause "and Carrier" as a requirement (defect **WF-2**).

**QA-A-28** `[WF]` — covers `[L-S1-4]`, `[L-R7]`
Given **N1**
Then the DOM order of the form's data inputs is: route cards → unified search → product table (`SKU No.`, `Brand`, `Product Name`, `Order Qty`, `Unit Cost (KRW) *`, `JIT Price (KRW)`) → `Supplier` → `Tracking No` → `Expected arrival` → `Memo (Optional)`
And **no column, field or label named `Size` exists anywhere on the page**.

**QA-A-29 (negative)** `[ADMIN]` — covers `[E-66]`, `[E-67]`, `[E-68]`
When the picked catalog product is deleted or renamed between selection and submit
Then registration still succeeds against the snapshot captured at selection, and the divergence is recorded on `DC-1`
And when the catalog holds two entries for one SKU, the search surfaces both rather than silently picking one
And an inactive or discontinued SKU is either excluded from results or shown with an explicit inactive marker.

**QA-A-30 (negative)** `[ADMIN]` — covers `[E-69]`, `[E-78]`, `[E-79]`
When `Order Qty` exceeds the declared per-line maximum
Then it is rejected with an inline error — never truncated, wrapped, or clamped
And when two requests use `Other` channel names differing only by case or padding, they group as one channel downstream
And an `Other` channel name containing Slack or markdown control characters is stored verbatim and escaped only at render time.

### Block B — State 2 route variant `[L-S2-1]`, `[L-S2-2]`, `[L-S2-F]`

**QA-B-01** `[WF]` — covers `[L-S2-1]`, `[L-R2]`
Given **N2**
Then `#s2` has class `on`, the `Wholesale` card carries class `on`, and the other three do not
And the form contains **no Inbound No. input, no preview panel, and no element whose label contains `Inbound No.`** anywhere inside `#s2 .formcard`
And the submit-row copy reads exactly `On registration, status = REQUESTED (tracking number entered → View Orders matching active immediately) · Inbound No. auto-assigned — shown in the Request List`.

**QA-B-02** `[WF]` — covers `[L-S2-2]`, `[L-R3]`
Given **N2**
Then `#s2 .prodtbl tbody` row 2 (`Round Lab` / `1025 Dokdo Cleanser, 150ml`) has `Order Qty = 300`, `Unit Cost (KRW) = 0`, and an empty `JIT Price`
And the explanatory line below the table contains the exact substring `0 entered directly in Unit Cost (0 allowed)`
And **no `input[type=checkbox]`, toggle, or `<label>` control anywhere on the page is bound to a "free of charge" / FOC behavior**.
*Precision note: the words "free of charge" DO legitimately appear in State 1's explanatory disclaimer text. This assertion is about the absence of a **control**, not the absence of the phrase — a naive full-text search for "free of charge" will produce a false failure.*

**QA-B-03** `[WF]` — covers `[L-S2-2]`, `[G-6]`
Given **N2**
Then the `Supplier` input value is exactly `비엠유통` (Korean preserved verbatim as data, never transliterated)
And the `Tracking No` input value is exactly `10325661220417` with placeholder `Add after dispatch — you can submit without it`
And `Expected arrival` is `2026-07-18`, and the Memo textarea contains `Wholesale vendor direct ship — 2 pallets, forklift needed`
And the `.note.purple` contains the substring `matches to View Orders the moment it registers`.

**QA-B-04** `[WF]` — covers `[L-S2-1]`, `[L-F1]`
Given **N2**
When I click `Register Inbound Request`
Then `#gtoast` shows text identical to State 1 — `✓ Inbound request registered` with `Inbound No. auto-assigned · added to the Request List · No refresh` — proving registration feedback is route-invariant.

**QA-B-05** `[ADMIN]` — covers `[L-S2-1]`, `BR-2`
When the full Block A validation suite is re-run with route set to `WHOLESALE`, then `PARTNERSHIP`, then `OTHER` (with a channel name)
Then every result is identical to the `SMART_BUY` run except that `OTHER` additionally requires the channel name — proving route-invariance.

**QA-B-06 (negative)** `[WF]` — covers `[L-S2-F]`, `[L-R4]`
Given **N2**
Then the State 2 legend footer paragraph contains the exact substring `REQUESTED → PARTIAL → INBOUNDED`
And it records `SHIPPED retired 2026-07-27 · PARTIAL added 2026-08-02`
And **no status control, badge, chip or option reading `SHIPPED` exists anywhere in the document**.

**QA-B-07** `[ADMIN]` — covers `[L-S1-14]`
Then the Comments hub is present and operable on **every** state of this page, not only the New Request form.
*Wireframe limitation: `data-open="inbox1"` is wired only in State 1, so States 2 and 3 render the button without a dropdown. That is a demo gap, not a product requirement — do not file it as a bug.*

### Block C — Request List `[L-S3-1]`…`[L-S3-10]`, `[L-F3]`, `[L-F4]`, `[L-F5]`, `[L-F7]`, `[L-F9]`

**QA-C-01** `[WF]` — covers `[L-F5]`, `[G-12]`
Given **NR**
Then `#s3` has class `on` and the top-bar tab `3 · Request List (Requested/Partial/Inbounded)` carries class `on`
And the same holds when the page is loaded with `#s3` instead of `#reqlist`.

**QA-C-02** `[WF]` — covers `[L-S3-1]`, `[L-R4]`
Given **N3**
Then `.filterchips` contains exactly 4 `.chip` buttons whose trimmed texts are `All 12`, `REQUESTED 8`, `PARTIAL 1`, `INBOUNDED 3`
And the `All 12` chip carries class `on`
And the three status counts sum to the `All` count (8 + 1 + 3 = 12)
And **no chip labelled `SHIPPED` exists**.

**QA-C-03** `[WF]` — covers `[L-S3-1]`
Given **N3**
When I click the chip whose text is `PARTIAL 1`
Then it gains class `on`, `All 12` loses it, and exactly one chip in `.filterchips` carries `on`.

**QA-C-04 (negative)** `[ADMIN]` — covers `[L-S3-1]` / `[E-23]`, `[E-26]`, `[E-61]`
When I select a chip whose status has no rows
Then the table renders an explicit empty state, the chip count reads `0`, and the footer line reflects the filtered totals
And when a new request is registered while a non-matching filter is active, the row does **not** appear but the success toast still fires and the chip counts update
And a first-run list with no requests at all renders the same empty state with `All 0`.

**QA-C-05** `[WF]` — covers `[L-S3-2]`, `[L-R4]`, `[L-R12]`
Given **N3**
Then `.bulkbar` contains a button with the exact label `Bulk add tracking numbers` and the count text `2 selected · Inbound processing (INBOUNDED transition) is applied automatically by View Orders scans`
And **no button labelled "Mark as shipped" and no manual status control of any kind exists in the bulk bar**.

**QA-C-06 (negative)** `[ADMIN]` — covers `[L-S3-2]` / `[E-24]`, `[E-25]`
When 0 rows are selected
Then `Bulk add tracking numbers` is disabled
And when the selection includes an `INBOUNDED` row, that row is excluded from the operation and named in the result toast with its exclusion reason.

**QA-C-07** `[WF]` — covers `[L-S3-3]`, `[G-5]`
Given **N3**
Then the Sourcing Route cells render `SMART BUY`, `WHOLESALE`, `PARTNERSHIP` as `.tag` spans whose computed `background-color` is fully transparent and whose computed `color` equals the page ink colour `rgb(20, 16, 27)`, with `font-weight` 800 — **black bold text, not coloured pills**.

**QA-C-08** `[WF]` — covers `[L-S3-4]`, `[L-S3-7]`, `[G-10]`
Given **N3**
Then row `202607120004` renders two tracking numbers `10325661220417` and `10325661220418` in the Tracking No cell with the note `2 tracking numbers — all matching active`
And rows `202607130003` and `202607130002` render an `Add tracking` button instead of numbers
And row `202607120001` renders the single number `10324880021991` with no `Add tracking` button.

**QA-C-09** `[WF]` — covers `[L-S3-5]`, `BR-30`
Given **N3**
Then row `202607120001` shows the status pill `PARTIAL 120/180`
And its Qty cell shows `180` followed by the edit-history note `✎ 300→180 (damaged)` whose `title` attribute is exactly `Expected qty edit history`
And the parenthetical is the short token `damaged`, **not** the full enum string `Damaged/defective — cannot accept`.

**QA-C-10** `[WF]` — covers `[L-S3-8]`, `[L-S3-10]`, `[L-R10]`
Given **N3**
Then rows `202607100005` and `202607090002` show the `INBOUNDED` pill and Received Dates `07-11 14:22` and `07-09 10:05`
And row `202607100005`'s Tracking No cell carries the note `Switched by View Orders scan inbound`
And **neither INBOUNDED row contains any `<a>` or `<button>` pointing to View Orders**.

**QA-C-11 (negative)** `[WF]` — covers `[L-S3-10]`, `[L-F9]`, `[L-R9]`, `[PD-9 · OWNER-PENDING]`
Given **N3**
Then the Request List header row contains exactly 12 `th` cells in this order: (checkbox), `Inbound No.`, `Sourcing Route`, `Brand · Product`, `SKU`, `Qty`, `Tracking No`, `Expected arrival`, `Received Date`, `Requested by`, `Status`, `Actions`
And **no `Carrier` column exists anywhere in the table**, and no 13th column exists.

**QA-C-12 (negative)** `[WF]` — covers `[L-S3-4]`, `[E-28]`, `[PD-85 · OWNER-PENDING]`
Given **N3**
Then neither `INBOUNDED` row (`202607100005`, `202607090002`) contains an `Add tracking` button.

**QA-C-13** `[WF]` — covers `[L-S3-9]`, `[L-S3-6]`
Given **N3**
Then a `.note.purple` below the table contains the exact substrings `is not done manually on this screen`, `#wholesale-ops`, and `#partnership-kr`.

**QA-C-14** `[WF]` — covers `[L-F4]`
Given **N3**
Then the footer line reads exactly `Showing 6 of 12 request(s) · Status: REQUESTED 8 · PARTIAL 1 · INBOUNDED 3`
And the three counts in it match the chip counts asserted in `QA-C-02`
And exactly 6 data rows are rendered in `.tbl tbody` (excluding any injected `.cpanel-ir` row).

**QA-C-15** `[WF]` — covers `[L-F3]`
Given **N3**
When I click the button labelled `＋ New Inbound Request`
Then `#s1` becomes the active state and, within `#s1 .pagetabs`, the `New Request` tab carries class `on`.

**QA-C-16** `[WF]` — covers `[L-F9]`, `[G-6]`
Given **N3**
Then row `202607130003`'s `Brand · Product` cell renders the brand `COSRX` inside a `<b>` followed by `Advanced Snail 96 Mucin Essence, 100ml +2 more`, and its SKU cell reads `100040311 +2`
And row `202607100005` renders `Beauty of Joseon` in bold with `Relief Sun, 50ml +1 more` and SKU `100031820 +1`.

**QA-C-17 (negative)** `[ADMIN]` — covers `[L-S3-5]`, `[L-R12]`, `BR-11`
Then no control anywhere in the Request List — row menu, bulk bar, status cell, context menu, or keyboard shortcut — can set a request's status
And any direct API attempt to set `INBOUNDED` or `PARTIAL` from a source other than the View Orders scan flow is rejected.

**QA-C-18** `[ADMIN]` — covers `[L-S3-1]`, `DC-7`
When View Orders records a partial receipt against a `REQUESTED` request
Then `inbound_request.status_changed` (`DC-7`) is persisted with `old_status=REQUESTED`, `new_status=PARTIAL`, the received/expected totals and the causing scan event id
And this page's pill and chip counts reflect it **without a page refresh**.

**QA-C-19** `[WF]` — covers `[L-F7]`
Given **N3**
Then the `.nav` bar contains, in order: brand `SkinSeoul`, the menu labels `Operation AI ▾`, `Catalog Management ▾`, `OMS Center ▾`, `Site Management ▾`, a `💬 Comments` button with a red count badge, the user block `Yongwon Ryu` with avatar initial `Y`, and a `Logout` button.

**QA-C-20 (negative)** `[ADMIN]` — covers `BR-29` / `[E-84]`
Given a status filter is active and more rows exist than are rendered on the page
When I click the header select-all checkbox
Then **only the currently visible (filtered) rows** are selected — no off-screen or filtered-out row is included
And per-row selections persist across chip switches within the session
And the bulk-bar count always equals the number of actually selected rows.

**QA-C-21** `[ADMIN]` — covers `[L-S3-5]`, `BR-30` / `[E-80]`, `[E-81]`, `[E-82]`
When an M6 edit uses reason `Supplier qty change`, then a second edit uses `Other (memo)` with memo text
Then the Qty cell renders the **most recent** edit only, as `✎ {previous}→{current} (other)`
And the memo text is not inlined into the cell but is readable in the cell's `title` and in the auto-comment
And on a multi-line request the Qty cell shows the request total with the marker present, and per-line attribution is available in the comment thread.

**QA-C-22 (negative)** `[ADMIN]` — covers `[E-92]`, `[PD-12 · OWNER-PENDING]`
Given a request expecting 180 units against which 200 have been received
Then the status pill renders `PARTIAL 200/180` — unclamped, with the numbers in received/expected order
And full confirmation stays blocked until the excess is resolved by an M6 edit or a partial save.

**QA-C-23 (negative)** `[ADMIN]` — covers `[E-26]`, `[E-84]`
When a new request is registered while the list is paginated and a filter is active
Then the visible page does not silently drop a row without the `Showing X of Y` line changing to match
And no selected row is deselected by the insert.

**QA-C-24** `[WF]` — covers `[L-F1]`
Given **N3** on a freshly loaded page (**NX**)
Then a **static** `.toast` element is present inside `#s3` reading `✓ Inbound request registered — 202607130003` with the sub-line `No refresh · added to top of the list`
And this element is **not** `#gtoast`: it exists before any click, it is not created by `gtoastShow`, and it does not auto-hide. QA must never treat its presence as evidence that a registration fired.

### Block D — M1 Add Tracking No modal `[L-M1]`

**QA-D-01** `[WF]` — covers `[L-M1]`
Given **NM**
Then `#m-invoice` gains class `open` and its `header` reads exactly `Add Tracking No — 202607130003`
And the body contains the exact substrings `Enter the tracking number(s) once the goods have shipped.` and `One inbound request can hold multiple tracking numbers`.

**QA-D-02** `[WF]` — covers `[L-M1]`, `[L-S3-4]`
Given **N3**
When I click the `Add tracking` button in row `202607130003`
Then the same `#m-invoice` overlay gains class `open`.
*Wireframe limitation: the header stays `202607130003` regardless of which row opened it — the per-row header binding is `[ADMIN]` (`QA-D-13`).*

**QA-D-03** `[WF]` — covers `[L-M1]`, `[G-10]` / `[E-37]`
Given **NM**
Then `#tnList` contains exactly 1 `.qrow`
When I click `＋ Add tracking number` (`#tnAdd`) twice
Then `#tnList` contains 3 `.qrow` rows, each with an `input` and a `.tn-del` `✕` button, and the newest input is `document.activeElement`
When I click `✕` on two rows, then `✕` on the last remaining row
Then two rows are removed and the final row **remains** with its input value cleared — the row count never reaches 0.

**QA-D-04** `[WF]` — covers `[L-M1]`, `[L-F1]`, `[G-2]`
Given **NM**
When I click `Save tracking numbers`
Then `#m-invoice` loses class `open` and `#gtoast` shows `✓ Tracking number(s) saved` with the secondary line `Every registered number is now matched to View Orders · No refresh`.

**QA-D-05** `[WF]` — covers `[L-M1]`
Given **NM**
When I click `Cancel`
Then `#m-invoice` loses class `open` and **no `#gtoast` appears**
And the same holds for the header `✕` and for a click on the overlay backdrop (`#m-invoice` itself, outside `.modal`).

**QA-D-06** `[WF]` — covers `[L-M1]`
Given **NM**
Then the first `.qrow` input's placeholder is exactly `e.g. 10325661220417 — last-mile / Coupang tracking number`
And after clicking `＋ Add tracking number` the appended row's placeholder is exactly `Additional tracking number`
And the modal body contains the exact substring `status stays REQUESTED`
And each `.tn-del` button carries `title="Remove this tracking number"`.

**QA-D-07 (negative)** `[ADMIN]` — covers `[L-M1]` / `[E-32]`
When I click `Save tracking numbers` with every input empty or whitespace-only
Then the save is blocked, the modal stays open, no server call is made, and no success toast fires.

**QA-D-08 (negative)** `[ADMIN]` — covers `[L-M1]` / `[E-33]`, `[E-34]`, `[E-58]`, `[E-88]`
When I enter the same number twice, a number already saved on this request, a number already entered at creation on this request, and two numbers differing only by surrounding whitespace
Then exactly one instance of each distinct trimmed number is persisted and no duplicate `tracking_no.added` row exists for this request.

**QA-D-09 (negative)** `[ADMIN]` — covers `[L-M1]`, `BR-15` / `[E-21]`, `[E-35]`
When I save a number already registered on a different inbound request
Then the save is blocked with an error naming the other Inbound No.
And `tracking_no.duplicate_blocked` (`DC-19`) is persisted with `attempted_number` and `owning_inbound_no`.

**QA-D-10** `[ADMIN]` — covers `[L-M1]`, `DC-3`, `DC-6`
When a save of two numbers succeeds
Then two `tracking_no.added` events (`DC-3`, `source=M1`) and two `tracking_match.activated` events (`DC-6`) are persisted with actor and timestamp
And both numbers immediately resolve to this request when scanned in View Orders
And the request's status is still `REQUESTED`.

**QA-D-11 (negative)** `[ADMIN]` — covers `[L-M1]`, `[G-9]` / `[E-41]`
When I double-click `Save tracking numbers`
Then exactly one save is applied, one toast is shown, and `DC-23` is persisted.

**QA-D-12 (negative)** `[ADMIN]` — covers `[L-M1]`, `BR-17` / `[E-38]`
When I attempt to remove a saved tracking number that already has a matched scan
Then the removal is **blocked** with an explanatory message `[PD-81 · OWNER-PENDING]` and no `tracking_no.removed` event is written
And when I remove a saved number with **no** matches, a confirm dialog appears, a toast fires, and `tracking_no.removed` (`DC-4`) is persisted with the old value `[PD-5 · OWNER-PENDING]`.

**QA-D-13 (negative)** `[ADMIN]` — covers `[L-M1]`, `BR-14` / `[E-28]`
When M1 is opened for a request that is already `INBOUNDED`, or which transitions to `INBOUNDED` between opening and saving
Then the save is rejected with a red toast, the row is refreshed, no partial write occurs `[PD-6 · OWNER-PENDING]`, and the operator is directed to create a new request `[PD-85 · OWNER-PENDING]`
And the modal header reflects the request that actually opened it, not a fixed demo value.

**QA-D-14 (negative)** `[ADMIN]` — covers `[L-M1]` / `[E-39]`, `[E-40]`, `[E-62]`
When two operators save different number sets for the same request concurrently
Then the server **merges** the sets (numbers are additive) and no number is lost; a genuine version conflict returns 409 with a non-green toast and persists `DC-22`
And when the network fails mid-save, the modal stays open with values retained and a retry under the same idempotency key produces no duplicates
And a number scanned in View Orders **before** the save commits does not match, while the same scan after commit does.

**QA-D-15 (negative)** `[ADMIN]` — covers `[E-72]`
When I paste a block of three tracking numbers separated by newlines into a single M1 input
Then the block is split across three rows before saving, visible to the operator for correction
And no single concatenated value is ever persisted
And the same holds for tab-, comma- and semicolon-separated blocks.

**QA-D-16 (negative)** `[ADMIN]` — covers `BR-15` / `[E-73]`, `[E-36]`
Given request A holds `10325661220417`
When I save `1032566122041` (a strict prefix) on request B
Then the save **succeeds** — they are different numbers; uniqueness is whole-string equality after normalisation, never prefix or fuzzy matching
And validation applies no carrier-specific regex, so numbers from any carrier format are accepted.

**QA-D-17** `[WF]` — covers `[L-M1]`
Given **NM**
When I click on the overlay (`#m-invoice`) outside the `.modal` box
Then `#m-invoice` loses class `open` and no toast appears — backdrop dismissal behaves exactly like `Cancel`.

### Block E — Cross-page lifecycle (with View Orders)

**QA-E-01** `[ADMIN]` — covers `[L-S3-5]`, `DC-7` / `[E-30]`
Given a `REQUESTED` request expecting 180 units
When View Orders State 6 saves a partial inbound of 120
Then this page's status pill becomes `PARTIAL 120/180` without a page refresh, and `DC-7` is persisted.

**QA-E-02** `[ADMIN]` — covers `[L-S3-7]`, `[G-10]` / `[E-44]`
When any registered tracking number of that `PARTIAL` request is rescanned
Then View Orders State 6 resumes from the remainder (60 outstanding), the received count accumulates against the same request, and no unit is double-counted.

**QA-E-03** `[ADMIN]` — covers `[L-S3-8]`, `[L-S3-10]`, `DC-7`, `DC-9`
When the full-receipt gate is confirmed in View Orders
Then the status pill becomes `INBOUNDED`, the Received Date cell fills with the **scan time**, and `DC-7` and `DC-9` are persisted
And `DC-9` carries **no carrier field** `[PD-9 · OWNER-PENDING]`.

**QA-E-04** `[ADMIN]` — covers `[L-S3-5]`, `DC-8`, `DC-11` / `[E-29]`
When View Orders M6 edits an expected quantity from 300 to 180 with reason `Damaged/defective — cannot accept`
Then `DC-8` is persisted with `old_qty=300`, `new_qty=180`, `reason=damaged_defective`, and the editor
And this page's Qty cell renders `✎ 300→180 (damaged)` per the `BR-30` token map
And `comment.auto_posted` (`DC-11`, `trigger=expected_qty_edit`) appears in the request's comment thread
And a Slack message reaches `#fulfillment-admin-comments` (`C0BMGEWM5QA`) `@`-mentioning the requester.

**QA-E-05 (negative)** `[ADMIN]` — covers `[E-42]`, `[PD-14 · OWNER-PENDING]`
When M6 attempts to set a new expected qty **below** the already-received qty
Then the edit is hard-blocked with `New expected qty cannot be lower than the received qty ({n})` and this page renders no new history entry.

**QA-E-06 (negative)** `[ADMIN]` — covers `[E-43]`, `[PD-84 · OWNER-PENDING]`
When M6 edits the expected qty down to exactly the received qty
Then `Confirm Full Inbound` re-enables in View Orders but the request's status on this page remains `PARTIAL` until a human confirms — **no auto-transition**.

**QA-E-07** `[ADMIN]` — covers `BR-19`, `DC-1`, `DC-21` / `[E-45]`, `[E-53]`
Given a parcel arrived with no matching request and its barcode sits in the unrecognized pool
When an operator creates an inbound request here, adds that tracking number, and removes the pool row with reason `routed to inbound request` carrying this Inbound No.
Then `DC-1` records `source=from_unrecognized` and `DC-21` links the pool item to the Inbound No. `[PD-64 · OWNER-PENDING]`
And rescanning the same barcode now enters View Orders **State 6** normally.

**QA-E-08 (negative)** `[ADMIN]` — covers `BR-16`, `[E-22]`, `[PD-86 · OWNER-PENDING]`
Given an inbound tracking number identical to an existing customer-order (outbound) tracking number
Then registration is **allowed** — separate namespaces
And scanning that number in View Orders resolves to the **inbound request** (State 6), not the customer order.

**QA-E-09 (negative)** `[ADMIN]` — covers `BR-3` / `[E-74]`
Given a New Request form opened at 23:58 server time
When it is submitted at 00:02 the next day
Then the allocated Inbound No. carries the **submission** date bucket and the new day's sequence begins at `0001`
And a client whose clock is wrong does not influence the bucket.

**QA-E-10 (negative)** `[ADMIN]` — covers `[E-91]`
When a product is deleted from the catalog after a request referencing it was registered
Then the Request List, the request detail and the sheet scrape all still render the stored SKU / brand / product-name snapshot — never a blank cell
And View Orders State 6 reconciliation still resolves against the stored SKU.

**QA-E-11** `[ADMIN]` — covers `[L-S3-10]`, `BR-12` / `[E-89]`
Given a `PARTIAL` request
Then its Received Date cell still renders `–` — Received Date marks completion, not first contact
And a request that goes `REQUESTED → INBOUNDED` directly, with no `PARTIAL` stage, fills Received Date at that moment.

### Block F — Comments hub and row panels `[L-S1-14]`, `[L-F2]`

**QA-F-01** `[WF]` — covers `[L-S1-14]`
Given **N1**
When I click the nav button `💬 Comments` (`[data-open="inbox1"]`)
Then `#inbox1` gains class `open` and shows two tabs labelled `@ Mentions` (with badge `2`) and `★ Saved`, with `@ Mentions` carrying class `on`.

**QA-F-02** `[WF]` — covers `[L-S1-14]`, `DC-13`
Given **N1** and `#inbox1` open
Then the `@ Mentions` pane header reads `Comments where I'm tagged` with the action `Mark all as read`
And the pane lists exactly two `.it` entries, both carrying class `unread`, whose bold entity labels are `202607130002` and `202607120004`
And the first reads `Dean: "@Yongwon when is the tracking number for this wholesale one coming?"` at `11:20`, and the second `Miranti: "@Yongwon the partnership stock's expected arrival slipped by a day"` at `Yesterday`.

**QA-F-03** `[WF]` — covers `[L-S1-14]`, `DC-12`
Given **N1** and `#inbox1` open
When I click the `★` button on the first mention entry
Then that button toggles class `on`
When I click the `★ Saved` tab
Then the pane header reads `Comments I saved` with the hint `Unstar to remove from list`.

**QA-F-04** `[WF]` — covers `[L-F2]`
Given **N3**
When I click `💬 Comments` in row `202607130002`
Then a `tr.cpanel-ir` is inserted directly below that row spanning all 12 columns, listing two comments — `Dean` / `Wholesale PO confirmed — expected arrival 07-18` / `09:12` and `Yongwon` / `@Dean got it. I'll keep location row B open` / `09:30` — with `@Dean` wrapped in a `.at` span
And the panel contains an input with placeholder `Write a comment — @name tags trigger a Slack alert` and a button labelled `Post`.

**QA-F-05** `[WF]` — covers `[L-F2]`
Given **N3** and the panel for row `202607130002` is open
When I click the same `💬 Comments` button again
Then the `tr.cpanel-ir` is removed — the panel is a toggle.

**QA-F-06** `[WF]` — covers `[L-F2]` / `[E-64]`
Given **N3**
When I click `💬 Comments` in row `202607120001` (which has no entry in the demo comment map)
Then the injected panel renders the text `No comments yet` plus the write box.

**QA-F-07** `[ADMIN]` — covers `[L-F2]`, `DC-10`, `DC-17`, `DC-15`, §6.1 row 4
When I post a comment containing `@Dean` on request `202607130003`
Then `comment.posted` (`DC-10`) is persisted with author, timestamp, `entity_type=inbound_request`, `inbound_no`, text and `mentions=[Dean]`
And `comment.mention_notified` (`DC-17`) and `slack_notification.sent` (`DC-15`) are persisted for `#fulfillment-admin-comments` (`C0BMGEWM5QA`)
And the Slack message body `@`-mentions Dean and carries the Inbound No., text, time, author and a deep link to the request.

**QA-F-08 (negative)** `[ADMIN]` — covers `BR-25`, `[PD-3 · OWNER-PENDING]` / `[E-48]`, `[E-49]`, `[E-65]`
Then no edit or delete control exists on any posted comment, on any request, in any status
And posting an empty or whitespace-only comment performs no action and makes no server call, so no event is written
And a comment mentioning a name that resolves to no system user posts successfully but fires **no** Slack notification, with the unmatched token recorded on `DC-10`
And a comment may be posted on an `INBOUNDED` request.

**QA-F-09 (negative)** `[ADMIN]` — covers `[L-S1-14]`, §6.2 / `[E-86]`
When a Comments-hub entry points at an inbound request that can no longer be resolved
Then the UI renders a non-crashing "entity unavailable" state
And the click does not dead-end, throw, or navigate to a broken route.

**QA-F-10 (negative)** `[ADMIN]` — covers `[L-F2]` / `[E-87]`
When a comment contains `@Dean,` (mention followed by punctuation) and a mention of a non-ASCII display name
Then both resolve by the same admin-wide mention rule used on every other screen
And any token that cannot be resolved falls through to the `[E-48]` behavior — comment posts, no Slack fires, token recorded.

### Block G — Automation, integrations and data-capture assertions

**QA-G-01** `[ADMIN]` — covers `[L-S3-6]`, §6.1 rows 1–2, `DC-14`, `DC-15`
Given requests in `REQUESTED` with zero tracking numbers across routes `SMART_BUY`, `WHOLESALE` and `PARTNERSHIP`
When the morning check runs
Then one message reaches `#wholesale-ops` listing the `SMART_BUY` and `WHOLESALE` requests, and one reaches `#partnership-kr` listing the `PARTNERSHIP` ones, each row carrying Inbound No., supplier, requested-by and age
And `morning_check.executed` (`DC-14`) is persisted with the flagged ids per channel and the Slack message ts
And `slack_notification.sent` (`DC-15`) is persisted per dispatch.

**QA-G-02 (negative)** `[ADMIN]` — covers `[L-S3-6]`, `BR-21` / `[E-52]`
Then requests with at least one tracking number are **not** included, and `PARTIAL` / `INBOUNDED` requests are **never** included
And running the job a second time on the same calendar date produces no second post and records a suppressed execution on `DC-14`.

**QA-G-03 (negative)** `[ADMIN]` — covers `BR-27`, `[PD-4 · OWNER-PENDING]` / `[E-51]`, `[E-77]`, `[E-83]`
When the Slack webhook fails during a mention dispatch or the morning check
Then the underlying comment/registration still stands, `DC-15` records `result=failed` with the attempt number, a retry is scheduled, and nothing is rolled back
And when one channel succeeds and the other fails, only the failed channel is retried and the successful post is never duplicated
And a registration whose memo materialisation fails afterwards keeps the request and the success toast.

**QA-G-04** `[ADMIN]` — covers `[L-S3-2]`, `DC-5`
When `Bulk add tracking numbers` completes for 3 selected requests (one of them `INBOUNDED`)
Then `tracking_no.bulk_added` (`DC-5`) is persisted with a `batch_id`, the request ids, per-request numbers, and the excluded `INBOUNDED` id with its exclusion reason
And a toast reports how many requests received numbers and how many were excluded.

**QA-G-05 (negative)** `[ADMIN]` — covers `BR-15` / `[E-60]`
When one bulk batch would apply the same tracking number to two requests
Then the second application is blocked and named in the result toast, with `DC-19` persisted per rejection.

**QA-G-06 (negative)** `[ADMIN]` — covers `[L-S1-3]` / `[E-19]`, `[E-20]`
When two registrations commit within the same second
Then their `NNNN` sequences differ and neither reuses the other's number
And when the day's sequence would exceed `9999`, registration is blocked with a red toast and the attempt is persisted — never wrapped, never reused.

**QA-G-07** `[ADMIN]` — covers §6.2, `[G-12]`, `DC-16`
When the View Orders State 6 banner link is followed
Then this page opens on the Request List **filtered to the referenced Inbound No.**
And, if telemetry is enabled, `inbound_request.viewed_via_deeplink` (`DC-16`) records the entry source. *(`DC-16` is dev-optional; its absence is not a failure.)*

**QA-G-08** `[ADMIN]` — covers §6.4, `BR-20`, `DC-20` / `[E-18b]`, `[E-59]`
When the Procurement Hub sheet scrape runs
Then it reads a consistent committed snapshot of the Request List (Inbound No. → sheet column A, plus Channel, SKU, Brand, Product Name, Order Qty, Unit Cost, JIT Price, Supplier, Received Date)
And a half-written registration is never visible to the scrape
And `inbound_request.sheet_scraped` (`DC-20`) records the run.

**QA-G-09 (negative)** `[ADMIN]` — covers §5.4
Then **no** event is persisted for: autocomplete keystrokes; pre-submit row add/delete; route re-picks before submit; an abandoned form; M1 `Cancel`, header `✕` or backdrop dismissal; filter-chip clicks; column sorts; row checkbox toggles or select-all; page-tab switches; comment-panel expand/collapse; or a blocked empty comment post.

**QA-G-10 (negative)** `[WF]` — covers §6.5, `[G-4]`, `[G-3]`, `[G-1]`
Given **N1**, then **N2**, then **N3**, then **NM**
Then in no state does the document contain a `<button>`, `<a>` or input whose visible label or `title` contains `Print`, nor any control bound to a print action
And no control on the page produces audio — there is no `Audio`, `AudioContext`, `speechSynthesis` or media element in the page script
And no scan-input surface exists: no input is autofocused for barcode capture, and no input carries a scan-oriented placeholder (`scan`, `barcode`, `바코드`).

**QA-G-11** `[ADMIN]` — covers `BR-26`, `[G-15]`, `[PD-1 · OWNER-PENDING]`
Then every mutating action on this page (`DC-1`, `DC-3`, `DC-4`, `DC-5`, `DC-10`) records a resolvable actor identity
And no control on this page is hidden or disabled on the basis of a role in v1 — there are no permission-denied states.

**QA-G-12 (negative)** `[ADMIN]` — covers `[L-R1]`…`[L-R12]`
Then none of the following exists anywhere in the built page: a View Orders link-info modal or link; an Inbound No. input or preview panel; an FOC checkbox; a `SHIPPED` status or "mark as shipped" control; per-row product search boxes or an add-row button; a second submit button; a `Size` field; a PO matching panel; a `Carrier` column; a result link on an INBOUNDED row; an ad-hoc inbound registration path; any manual status control.

**QA-G-13 (negative)** `[ADMIN]` — covers `BR-31`, §6.1 row 3 / `[E-75]`
Given `OTHER`-route requests in `REQUESTED` with zero tracking numbers, and no channel configured for `OTHER`
When the morning check runs
Then **no Slack channel is invented and no post is sent for them**
And they are nonetheless present in `morning_check.executed` (`DC-14`) with `channel=unrouted`, so the unchased backlog is measurable from the run record.

**QA-G-14 (negative)** `[ADMIN]` — covers `BR-21` / `[E-76]`
When the morning check runs on a day when no request qualifies
Then no Slack post is sent
And `DC-14` is still written with an empty `flagged[]`, proving the scheduler fired.

**QA-G-15** `[ADMIN]` — covers §5.3
Then requests, lines, tracking numbers, status history, expected-qty edit history, Received Dates and comments are all still retrievable after the retention window used by any other subsystem — none of them is purged
And `DC-14` / `DC-15` automation logs and `DC-18` / `DC-19` / `DC-22` / `DC-23` rejection records are retained and queryable.

**QA-G-16 (negative)** `[WF]` — covers `[L-R1]`…`[L-R12]` (wireframe-runnable half of `QA-G-12`)
Given **N1**, then **N2**, then **N3**, then **NM**
Then across all four surfaces the document contains: no element with `data-modal` other than `m-invoice`; no input or label whose text contains `Inbound No.` inside a `.formcard`; no checkbox bound to a free-of-charge behavior; no text `SHIPPED` in any chip, badge or option; no `<th>` or cell labelled `Size` or `Carrier`; no second submit button (exactly one button reads `Register Inbound Request` per state); and no `Add tracking` button on rows `202607100005` or `202607090002`.

### 8.1 Data-capture coverage map

Every event in §5 has at least one QA scenario whose Then-clause asserts its persistence.

| Event | Asserted by |
|---|---|
| `DC-1` `inbound_request.created` | QA-A-20, QA-A-29, QA-E-07, QA-G-11 |
| `DC-2` `inbound_no.allocated` | QA-A-20, QA-E-09, QA-G-06 |
| `DC-3` `tracking_no.added` | QA-D-08, QA-D-10, QA-G-11 |
| `DC-4` `tracking_no.removed` | QA-D-12 |
| `DC-5` `tracking_no.bulk_added` | QA-G-04 |
| `DC-6` `tracking_match.activated` | QA-D-10, QA-D-14 |
| `DC-7` `inbound_request.status_changed` | QA-C-18, QA-E-01, QA-E-03 |
| `DC-8` `inbound_request.expected_qty_edited` | QA-E-04 |
| `DC-9` `inbound_request.received_date_recorded` | QA-A-27, QA-E-03 |
| `DC-10` `comment.posted` | QA-F-07, QA-F-08, QA-F-10 |
| `DC-11` `comment.auto_posted` | QA-A-20, QA-E-04 |
| `DC-12` `comment.starred` / `comment.unstarred` | QA-F-03 |
| `DC-13` `comment.read` / `comment.mark_all_read` | QA-F-02 |
| `DC-14` `morning_check.executed` | QA-G-01, QA-G-02, QA-G-13, QA-G-14 |
| `DC-15` `slack_notification.sent` | QA-F-07, QA-G-01, QA-G-03 |
| `DC-16` `inbound_request.viewed_via_deeplink` | QA-G-07 (dev-optional) |
| `DC-17` `comment.mention_notified` | QA-F-07 |
| `DC-18` `inbound_request.registration_rejected` | QA-A-06, QA-A-21 |
| `DC-19` `tracking_no.duplicate_blocked` | QA-D-09, QA-G-05 |
| `DC-20` `inbound_request.sheet_scraped` | QA-G-08 |
| `DC-21` `unrecognized_pool.linked_to_request` | QA-E-07 |
| `DC-22` `inbound_request.stale_conflict_rejected` | QA-D-14 |
| `DC-23` `inbound_request.idempotent_replay_suppressed` | QA-A-19, QA-D-11 |
| **NON-events** (§5.4) | QA-G-09 |
| **Retention** (§5.3) | QA-G-15 |

### 8.2 Legend-unit coverage map

Every one of the 39 legend units and all 12 negative entries carry at least one scenario.

| Unit | Scenarios |
|---|---|
| `[L-S1-1]` | QA-A-21 |
| `[L-S1-2]` | QA-A-02, A-03, A-04, A-05, A-06 |
| `[L-S1-3]` | QA-A-19, A-20, E-09, G-06 |
| `[L-S1-4]` | QA-A-13, A-16, A-28 |
| `[L-S1-5]` | QA-A-07, A-08, A-09 |
| `[L-S1-6]` | QA-A-08, A-10, A-11, A-12 |
| `[L-S1-7]` | QA-A-17, A-18 |
| `[L-S1-8]` | QA-A-17 |
| `[L-S1-9]` | QA-A-23 |
| `[L-S1-10]` | QA-A-13, A-14 |
| `[L-S1-11]` | QA-A-13, A-15 |
| `[L-S1-12]` | QA-A-17, A-22 |
| `[L-S1-14]` | QA-F-01, F-02, F-03, F-09, B-07 |
| `[L-S1-15]` | QA-A-25 |
| `[L-S1-16]` | QA-A-01 |
| `[L-S1-F]` | QA-A-26 (c), QA-A-27 (a), QA-G-08 (b) |
| `[L-S2-1]` | QA-B-01, B-04, B-05 |
| `[L-S2-2]` | QA-B-02, B-03 |
| `[L-S2-F]` | QA-B-06 |
| `[L-S3-1]` | QA-C-02, C-03, C-04, C-18 |
| `[L-S3-2]` | QA-C-05, C-06, C-20, G-04 |
| `[L-S3-3]` | QA-C-07 |
| `[L-S3-4]` | QA-C-08, C-12, D-02 |
| `[L-S3-5]` | QA-C-09, C-17, C-21, C-22, E-01, E-04 |
| `[L-S3-6]` | QA-C-13, G-01, G-02, G-13, G-14 |
| `[L-S3-7]` | QA-C-08, D-03, E-02 |
| `[L-S3-8]` | QA-C-10, E-03 |
| `[L-S3-9]` | QA-C-13 |
| `[L-S3-10]` | QA-C-10, C-11, E-03, E-11 |
| `[L-M1]` | QA-D-01 … D-17 |
| `[L-F1]` | QA-A-18, B-04, C-24, D-04 |
| `[L-F2]` | QA-F-04, F-05, F-06, F-07, F-08, F-10 |
| `[L-F3]` | QA-C-15 |
| `[L-F4]` | QA-C-14 |
| `[L-F5]` | QA-C-01, G-07 |
| `[L-F6]` | QA-A-20, A-24 |
| `[L-F7]` | QA-C-19 |
| `[L-F8]` | QA-A-01 |
| `[L-F9]` | QA-C-11, C-16 |
| `[L-R1]`…`[L-R12]` | QA-G-12 (all, `[ADMIN]`), QA-G-16 (all, `[WF]`), plus targeted: R1 QA-A-23 · R2 QA-B-01 · R3 QA-B-02 · R4 QA-B-06, C-02, C-05 · R7 QA-A-28 · R9 QA-A-27, C-11 · R10 QA-C-10 · R12 QA-C-05, C-17 |

---

## 9. Out of Scope & Open Questions

Per the writing convention, owner questions that already carry a provisional default live in the PD register and are tagged inline where they appear — they are **not** re-listed here. This section carries only: out-of-scope pointers, **NO-DEFAULT** open questions (nothing decided, no behavior specified), and development-time decisions.

### 9.1 Explicitly out of scope for this screen

| Item | Owner / where it lives |
|---|---|
| **Procurement Hub admin page** | Excluded from this plan entirely (2026-08-02). Not specced, not wireframed, not swept |
| **Procurement Hub sheet integration design** (column mapping beyond column A, cadence, auth, failure handling) | A separate design, agreed 2026-07-23 to be the **last** step. §6.4 states the contract; the design is not this document |
| **Warehouse-side reception mechanics** — scan loop, product-barcode counting, location assignment, exact-match full-confirm gate, `Save Partial`, expected-qty edit modal (M6) | The **View Orders** spec, States 6 / 6b and modals M5 / M6. This spec owns only the status, quantity-history and Received Date those flows write back |
| **Unrecognized pool UI and matching mechanics** | The **tracking-missing** and **View Orders** specs. Referenced here only for the `BR-19` recovery loop |
| **Label / invoice layout content** | Deferred to the Phase 3-1 session with the owner. No print surface exists on this page anyway ([G-4] N/A, §6.5) |
| **Automatic Carrier recording** | **Rejected** 2026-08-03 `[PD-9 · OWNER-PENDING]` → `[L-R9]`. Not deferred — rejected |
| **Photo capture on inbound artifacts** | Permanently removed from the WMS 2.0 flows (2026-08-03, `[PD-63]`). No photo affordance on this page, and no phase pointer |
| **Role / permission matrix** | Post-v1 owner decision `[PD-1 · OWNER-PENDING]` [G-15]. v1 is a single admin role with actor capture (`BR-26`) |

### 9.2 NO-DEFAULT open questions (owner must decide — no behavior is specified)

**OQ-1 · Post-registration correction, cancellation or voiding of a request** `[PD-79]`
The wireframe has **no** edit, cancel, or void affordance. Once registered, a request can only receive tracking numbers (`[L-M1]`), have its expected quantity edited from View Orders M6, and accumulate comments. A request created with the wrong SKU, wrong route, or wrong supplier — or a purchase cancelled before dispatch — therefore has **no defined path**.
*Current specified behavior:* requests are immutable except for the three channels above; a wrong request stays in the list and is annotated by comment.
*What deciding it would add:* a cancel/void status (a fourth status, contradicting `BR-10`), its own Slack and comment trail, its effect on the chip counts, on the morning check, and on the Procurement Hub sheet scrape.
**Blocking:** the sheet integration design and any future request-editing feature. **Owner decision required.**

**OQ-2 · May an item enter the unrecognized pool with NO tracking number (label destroyed)?** `[PD-66]`
Cross-page dependency owned by `tracking-missing`, listed here because `BR-19`'s recovery loop depends on the answer: if a pool item can exist with no number, then "match" has nothing to write onto the product line and the rescan-resolves loop this page relies on does not close.
*No behavior is specified on either side.* **Owner decision required.**

**OQ-3 · Should a Tracking No cell that already holds a number offer an inline add affordance?**
Raised by this spec, not previously registered. The wireframe renders `Add tracking` only on empty cells, so the **specified** path for adding a further number to an already-numbered `REQUESTED` / `PARTIAL` request is the bulk bar (§3.3.2). That works but costs three clicks at a moment (a dispatch email arriving) when the operator is in a hurry. Adding an inline `＋` is a new affordance and is therefore **not invented here**.
*Current specified behavior:* bulk bar only; no inline control.
**Owner decision required** if the inline affordance is wanted; otherwise the current behavior stands and §2.4 observation 2 is closed as "working as intended".

### 9.3 Development-time decisions (no owner input needed — state a default and own it)

| # | Decision | Note / recommended default |
|---|---|---|
| D-1 | Slack channel for the `OTHER`-route morning check | Deferred by `_slack-routing.md` and legend `[L-S3-6]`. Until it exists, rows are collected with `channel=unrouted` (`BR-31`). Surface to the owner **only** if a new channel must be created |
| D-2 | `NNNN` overflow behavior (> 9999/day) | Hard-fail with a red toast and a persisted attempt (`[E-20]`). Practically unreachable; must never wrap |
| D-3 | Bulk-add UX shape | One modal iterating the selection, or a per-request sequence. Wireframe encodes only the button + count (`[L-S3-2]`) |
| D-4 | `Expected arrival` default and bounds | No asterisk ⇒ optional. Recommend blank default, past dates allowed with a warning (`[E-15]`, `[E-54]`) |
| D-5 | Memo → comment rendering | Exact text template for the materialised auto-comment (`[L-F6]`, `DC-11`) |
| D-6 | Page-tab switch / deep-link arrival with an unsaved draft | Warn, or persist the draft client-side — never silently discard (`[E-57]`, `[E-85]`) |
| D-7 | `DC-5` event shape | Batch event with a `batch_id` plus per-request `DC-3` rows (recommended), versus a single aggregate |
| D-8 | Numeric formatting | Store integers, format with commas on render (`[E-7]`); normalise full-width digits on input (`[E-71]`) |
| D-9 | Form reset after successful registration | Clear for the next request, or retain values. Must be consistent and must not half-clear |
| D-10 | Tracking-number charset and length validation breadth | **Carrier-agnostic.** No single-carrier regex — carriers differ (`[E-36]`, `[E-73]`) |
| D-11 | Request List pagination, page size and default sort | `Showing 6 of 12` implies paging; newest-first assumed (`[L-F4]`) |
| D-12 | Idempotency key mechanics | Per-form-session UUID recommended; [G-9] mandates existence, not mechanism |
| D-13 | Toast duration, stacking policy and failure copy | Wireframe uses a single reused slot with a 2600 ms timer (`[L-F1]`, `[E-46]`) |
| D-14 | Comment search debounce and index scope | Hub full-text search across all comments [G-7] |
| D-15 | Slack retry policy | Retries persisted per `DC-15`; policy is dev's |
| D-16 | Export format for the Request List, if a manual export is added | Otherwise deferred entirely to the sheet-integration design |
| D-17 | Very-large-request handling (hundreds of lines) | Rendering and paging strategy (`[E-56]`); `Order Qty` per-line maximum (`[E-69]`) |
| D-18 | Session-expiry handling mid-form | Must not silently discard entered data (`[E-63]`) |
| D-19 | Multi-line paste separators in M1 | Newline / tab / comma / semicolon at minimum; split visibly before save (`[E-72]`) |
| D-20 | The single declared server timezone for the Inbound No. date bucket | One value system-wide; the client clock is never authoritative (`[E-74]`) |
| D-21 | Inactive / discontinued SKUs in the unified search | Exclude, or show with an explicit inactive marker — never show as an ordinary match (`[E-68]`) |

---

## 10. Decision Log

Every decision that shaped this screen, 2026-07-09 → 2026-08-03, including reversals and removals. Nothing is silently dropped.

| Date | Decision | Effect on this page | Evidence |
|---|---|---|---|
| 2026-07-09 | WMS 2.0 wireframe batch scoped; `inbound-request` created as screen 9 | Screen exists | commit `1bbba3a` |
| 2026-07-13 | Notion section **I. Inbound Request** added to scope: a single gateway for all sourcing routes, tracking number entered later, View Orders linkage. Section J (Procurement Hub) split off as a separate layer | `BR-1`, `[L-S1-1]` | Planning ledger 2026-07-09, §Notion scope |
| 2026-07-13 | Sourcing-route badges standardised as **black bold, colorless text** matching View Orders; the label `Comments` standardised everywhere | `[L-S3-3]`, `BR-22` | Ledger, View Orders v20 |
| 2026-07-23 | **Sheet-parity redesign.** In-page tabs `[New Request \| Request List]` added | `[L-S1-16]` | commit `592d583` |
| 2026-07-23 | **PO matching panel scrapped** → Inbound No. auto-assigned `YYYYMMDDNNNN` (`0001`–`9999`/day), PH sheet column A scheme | `BR-3`, `[L-R8]` | commit `15cdc2e` |
| 2026-07-23 | Product picked by SKU No. / Product Name search; **`Size` field removed**, quantity only | `[L-S1-6]`, `[L-R7]` | commit `15cdc2e` |
| 2026-07-23 | **Unit Cost required + FOC checkbox** (locking the field to ₩0) introduced; JIT Price optional for **Smart Buy · Wholesale only**; Supplier required | `BR-5`, `BR-6`, `BR-7` | commit `15cdc2e` |
| 2026-07-23 | `Received Date` column added to the Request List (auto at inbound, `–` before) | `[L-S3-10]`, `BR-12` | commit `15cdc2e` |
| 2026-07-23 | **The Request List is the dataset the Procurement Hub sheet scrapes as-is**; sheet integration designed separately as the **last** step | `BR-20`, `[L-S1-F]`(b), §6.4 | Ledger |
| 2026-07-26 | **REVERSAL:** Inbound No. **preview panel removed** — no input, no preview; visible only in the Request List | `[L-S1-3]`, `[L-R2]` | commit `5dd21ae` |
| 2026-07-26 | Channels widened to **4 with `Other` + free text** | `BR-2`, `[L-S1-2]` | commit `5dd21ae` |
| 2026-07-26 | Unified search widened to match **brand** as well as SKU and product name | `[L-S1-5]` | commit `5dd21ae` |
| 2026-07-26 | **REVERSAL:** **FOC checkbox retired** → type `0` directly in Unit Cost | `BR-5`, `[L-R3]` | commit `5dd21ae` |
| 2026-07-26 | **REVERSAL:** JIT Price redefined as the Coupang-JIT per-unit purchase price and made optional for **all** channels (was Smart Buy · Wholesale only) | `BR-6`, `[L-S1-11]` | commit `5dd21ae` |
| 2026-07-26 | Search-locked cells (SKU / Brand / Product Name) rendered as borderless plain text, not editable | `[L-S1-6]` | commit `0c860ea` |
| 2026-07-27 | **REVERSAL:** per-row search boxes and the separate "add row" button retired → **one unified search box** above the table; picked product appended as a blue-tinted row | `[L-S1-5]`, `[L-S1-6]`, `[L-R5]` | commit `ea0a4b0` |
| 2026-07-27 | Inline field help added to Unit Cost / JIT Price / Supplier ("leave blank if unknown") | `[L-S1-10]`, `[L-S1-11]`, `[L-S1-12]` | commit `ea0a4b0` |
| 2026-07-27 | **REVERSAL:** two register buttons unified into **one** `Register Inbound Request` (tracking presence no longer selects a branch) | `BR-8`, `[L-S1-7]`, `[L-R6]` | commit `ea0a4b0` |
| 2026-07-27 | **REVERSAL:** `SHIPPED` status retired and the "mark as shipped" bulk button removed — status reduced to 2 stages | `BR-10`, `[L-R4]` | commit `002f2bd` |
| 2026-07-27 | **Morning no-tracking Slack check specified**: `WHOLESALE`·`SMART BUY` → `#wholesale-ops`, `PARTNERSHIP` → `#partnership-kr`, `OTHER` deferred to development; once daily | `BR-21`, `[L-S3-6]`, §6.1 | commit `002f2bd` |
| 2026-08-02 | **REVERSAL of the 07-27 reduction:** status expanded to **3 stages** with `PARTIAL (n/m)` added between `REQUESTED` and `INBOUNDED`; rescan of the same tracking resumes reconciliation from the remainder | `BR-10`, `[L-S3-5]`, `[L-S2-F]` | commit `960f5cf` |
| 2026-08-02 | **Expected-qty edit** introduced in View Orders M6 with a mandatory reason, gate recomputation, `✎ old→new (reason)` history rendered in this page's Qty cell, and a Slack alert to the requester | `BR-13`, `[L-S3-5]`, `DC-8` | commit `960f5cf` |
| 2026-08-02 | **Unrequested arrivals reuse the existing unrecognized pool** — a dedicated ad-hoc registration path was **rejected** | `BR-19`, `[L-R11]` | commit `960f5cf` |
| 2026-08-02 | `Expected arrival` confirmed as the feed for the View Orders "Expected Inbound N" badge | `[L-S1-8]`, §6.3 | Ledger 2026-08-02 |
| 2026-08-02 | **Procurement Hub excluded from this plan entirely** (sweep, English pass and spec all out of scope) | §9.1 | Ledger 2026-08-02 |
| 2026-08-03 | **Multiple tracking numbers per request confirmed** [G-10]; every registered number is an independent match/scan target; badge stays `REQUESTED` | `BR-9`, `[L-S3-7]`, `[L-M1]` | Legend `[L-S3-7]`, commit `890e909` |
| 2026-08-03 | **REMOVED:** the "View Orders link info" modal and the INBOUNDED-row result link — the status badge alone is sufficient | `[L-R1]`, `[L-R10]`, `[L-S1-9]`, `[L-S3-8]` · leftover HTML comment = **WF-11** | commit `890e909` |
| 2026-08-03 | **REJECTED:** automatic Carrier recording; **no Carrier column** anywhere on this page | `BR-12`, `[L-S3-10]`, `[L-R9]`, `[PD-9]` · stale State 1 footer = **WF-2** · review **C-1** | Legend `[L-S3-10]` |
| 2026-08-03 | Unit Cost disclaimer repositioned to the product table's top right | `[L-S1-10]` | commit `890e909` |
| 2026-08-03 | **M1 save toast added** and the `gtoast` element-reuse bug fixed; registration toast added; per-row Comments panels added | `[L-F1]`, `[L-F2]`, `[L-M1]`, `[G-2]` | commit `890e909` |
| 2026-08-03 | Full English pass on this page (389 lines replaced, 30/30 checks); Korean product, carrier and supplier names deliberately preserved as **data** | `[G-6]`, `[L-S1-12]` | commit `890e909` |
| 2026-08-03 | State 1 legend **renumbered — dot 13 vacated** by the modal removal (intentional gap) | §2.1 | Legend, supervisor ruling 14 |
| 2026-08-03 | **Comment `@mention` channel CONFIRMED by the owner: `#fulfillment-admin-comments` (`C0BMGEWM5QA`)**, superseding the "pending" wording in the older drafts; expected-qty-edit and match-confirmed auto-comments route the same way | §6.1 rows 4–6, `[G-7]` · review **C-2** | `_slack-routing.md` |
| 2026-08-03 | Global rules v1.0 issued (`[G-1]`…`[G-15]`), including: `[G-5]` amended so the inbound-origin form's fourth route is `OTHER` + free text while order-facing badges stay the original four; `[G-11]` reason enum aligned to the M6 strings; new `[G-15]` single admin role | `BR-2`, `BR-13`, `BR-26` · review **C-3** / **C-11** / **GD-8** | `_global-rules.md` |
| 2026-08-03 | Owner emphasis re-confirmed across all eight screens: **no page refresh** and **a confirmation toast on every confirming action**, with removals counted as confirming actions | `BR-28`, `[G-2]`, `[GD-5]` · review **C-6** | `_global-rules.md` |
| 2026-08-03 | Provisional decisions adopted for this page pending owner review — `[PD-1]` single role · `[PD-3]` comments append-only · `[PD-4]` Slack failure never blocks · `[PD-5]` removals confirm + toast · `[PD-6]` stale-entity revalidation · `[PD-7]` concurrency (merge for additive sets) · `[PD-8]`/`[PD-82]` tracking uniqueness · `[PD-9]` no carrier · `[PD-12]` over-receipt warn-and-count · `[PD-14]` new expected qty ≥ received · `[PD-16]` match auto-comment · `[PD-64]` pool removal captures the Inbound No. · `[PD-80]` `OTHER (channel)` rendering · `[PD-81]` frozen matched numbers · `[PD-83]` no duplicate SKU · `[PD-84]` no auto-transition on qty edit · `[PD-85]` `INBOUNDED` terminal · `[PD-86]` separate tracking namespaces. `[PD-2]` (send sound) is explicitly **N/A** here | Each tagged `[PD-n · OWNER-PENDING]` inline throughout §3–§8 | `_provisional-decisions.md` |
| 2026-08-03 | **NOT decided, no default written:** post-registration correction/cancellation `[PD-79]`; pool entry without a tracking number `[PD-66]` | §9.2 OQ-1, OQ-2 | `_provisional-decisions.md` |
| 2026-08-03 | **Photo capture confirmed permanently removed** (not deferred) across the WMS 2.0 inbound flows | §9.1 | `[PD-63]` |
| 2026-08-03 (audit pass) | **Qty-cell reason token formalised** — the wireframe renders `(damaged)`, a short token, not the full [G-11] enum string; the mapping is now fixed so the marker is testable | `BR-30`, `[L-S3-5]`, `[E-80]`, `[E-81]`, `[E-82]` | Wireframe row `202607120001`; audit finding |
| 2026-08-03 (audit pass) | **Select-all scope fixed to visible/filtered rows** and promoted from an unstated assumption to a page rule | `BR-29`, `[L-S3-2]`, `[E-84]` | Audit finding; parallels the Ready-to-Outbound selection doctrine |
| 2026-08-03 (audit pass) | **`OTHER`-route chase gap made auditable** — with no channel assigned, those requests are still collected into `DC-14` as `channel=unrouted` rather than silently skipped | `BR-31`, `[L-S3-6]`, `[E-75]`, §6.1 row 3 | Audit finding |
| 2026-08-03 (audit pass) | **Edge-case key `E-c1` retired.** It had been merged onto `[E-16]` (empty Memo), which is an unrelated case, and it violated the `[E-{n}]` key convention. The empty-comment case is now `[E-65]`; `[E-16]` is unchanged and `E-c1` must never be reused | §7 preamble, `[E-65]` | Audit finding |
| 2026-08-03 (audit pass) | **Two stale-text observations recorded** as proposed additions to the wireframe-fix backlog (not assigned `WF-` numbers, since that register is closed at `WF-14`): the State 1 purple note lists only three routes though four exist; a filled Tracking No cell offers no inline add affordance | §2.4, §9.2 OQ-3 | Audit finding |

**Reversal chains at a glance** (so nobody re-implements a superseded state):

1. **Inbound No.** manual PO matching (pre-07-23) → auto-assign **with** a preview panel (07-23) → auto-assign **without** any preview (07-26, current).
2. **Free-of-charge stock:** FOC checkbox locking ₩0 (07-23) → checkbox retired, type `0` directly (07-26, current).
3. **JIT Price scope:** Smart Buy + Wholesale only (07-23) → optional on **all** routes (07-26, current).
4. **Product search:** per-row search boxes + add-row button (07-23) → single unified search box, no add-row button (07-27, current).
5. **Submit:** two register buttons (07-23) → one `Register Inbound Request` (07-27, current).
6. **Status stages:** `REQUESTED` / `SHIPPED` / `INBOUNDED` (07-23) → `SHIPPED` retired, 2 stages (07-27) → `PARTIAL` added, 3 stages (08-02, current).
7. **View Orders linkage UI:** link-info modal + INBOUNDED result link (07-23 → 08-02) → both removed, badge only (08-03, current).
8. **Carrier:** footer promised automatic capture (07-23 era) → automatic capture **rejected**, no column (08-03, current; the footer text is stale defect **WF-2**).

---

*End of specification — `inbound-request` v1.1, 2026-08-03.*
