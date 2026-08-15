# Order Management Dashboard — Screen Specification

> **Decision status update (2026-08-03)** — PD-1 through PD-8, 51, 55, 66, 71, 74, 79 are now **OWNER-DECIDED** (PD-6 confirmed 2026-08-03 — that decision round is closed), and **PD-36 was owner-decided 2026-08-04** (the picking list carries a `sample set` line; its inline tags were removed outright, so it is the one decided ID you will not see tagged); any inline `[PD-{these} · OWNER-PENDING]` or `[PD-{these} · NO-DEFAULT]` tags below are superseded — see `_provisional-decisions.md` for the decisions.

Slug: `order-management` · Spec version 1.3 · 2026-08-03
Wireframe (SST): `wms2/order-management/index.html` · Live: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/order-management/
Global rules: `_global-rules` (cited as `[G-n]`; page deltas only — rule bodies are never restated in this document).
Companion registers: `_plans/_provisional-decisions.md` (PD register) · `_plans/_wireframe-fixes.md` (WF register) · `_plans/_review.md` (adjudications C-1…C-12, writing conventions §3).

Reading order for an implementing agent: §2 (what exists) → §3 (what it does) → §4 (why) → §5 (what gets written down) → §7/§8 (how it is proven).

---

## 1. Purpose & Users

### 1.1 What this screen is

The Order Management Dashboard is the **order team's home screen** and the **only place in WMS 2.0 where non-sales orders are created and where sample-set campaigns are switched on and off**. It is the live admin's existing order list with three additions: a Marketing Order Import, a Sample Assignment ON/OFF pair, and the shared Comments hub. Everything else on the page is an explicit no-change contract against the current admin (`[L-4]`, `[L-F1]`…`[L-F6]`).

### 1.2 Who uses it

| User | Why they are here | Frequency |
|---|---|---|
| Order team member | Monitors the mixed sales + marketing order list, merges duplicate orders, exports for carriers/finance | Continuously, all day |
| Marketing / CRM PIC (the wireframe names Harshit, EuJin, Adinda as PIC options) | Bulk-imports influencer-seeding and giveaway orders; sets the PIC of record for the batch | Per campaign, in bursts of 10–100 orders |
| Marketing / CRM owner | Turns a sample-set assignment period ON, cancels one that is running | Rarely, but each action affects every order created afterwards |
| Admin | All of the above. `[G-15]` `[PD-1 · OWNER-PENDING]` applies unchanged — this page adds no role concept of its own (BR-22) | — |

### 1.3 The operator's physical reality (and where it changed a decision)

**This is a desk screen, not a warehouse screen.** The operator is seated, using a mouse and keyboard on a wide monitor (the mock is authored at a 1240 px minimum and the order table at 1180 px minimum — horizontal scroll is expected, not a defect; [E-96]). There is **no barcode scanner in the hand, no glove, no scan input, and no audio feedback on this page.** This is stated as a hard fact rather than an omission so that QA does not test scan-focus retention here and so that a developer does not add a scan surface by analogy with View Orders: `[G-1]` and `[G-3]` have no surface to attach to on this page (see BR-28 and the applicability grid in §6.6).

Three physical realities of *other* people nevertheless shaped what this screen does:

1. **The warehouse picker, downstream, holding a printed picking list at speed.** The picker never reads this screen — but the sample dual-view rule `[G-13]` exists because the picker must be told *which* sample and *how many*, while the carrier-facing data must not be told (tax handling). That asymmetry is decided here, on this screen, by an operator who will never see its consequence. It is therefore written down in full (BR-8) rather than left as "see the label spec".
2. **The order-team member visually sorting a 2,818-row mixed list.** Marketing orders are given a purple row tint (`--mkt-soft` `#F3EEFF`) plus an `MKT` badge plus a populated PIC column *instead of* being hidden behind a filter, because the operator's actual behaviour is to scan the list with their eyes while doing something else, not to construct a filter. Settlement and volume separation happens at a glance (BR-2).
3. **The marketing PIC working ahead of the warehouse.** Seeding campaigns are decided before the goods physically arrive. Blocking an import because stock is not yet inbounded would stop a campaign for a warehouse reason. Stock validation on import was therefore **dropped** on 2026-07-23 (BR-1) — the Ready-to-be-Outbounded Marketing view is the downstream pressure valve, and MKT orders appear there regardless of stock or inbound status.

Two speed-pressure consequences are specified as normative behaviour, not as polish:

- **The import never creates an order that cannot ship.** A country with no connected carrier fails the **whole file**: the offending rows render red, `Confirm Import` is disabled, and the message names the countries and both remedies (BR-20, `[G-17]`). Partial import was the earlier design and was reversed on 2026-08-04 — eleven successes plus one silently dropped recipient is the failure mode that hides, and it left a created order nobody could ship or unblock.
- **Confirmation is a top-right toast and the page never reloads** `[G-2]`. The operator fires an import of 12 orders and immediately switches to Slack or the campaign sheet; the toast is glanceable in peripheral vision and the small-text line carries the exception count, so a partially-flagged batch is never silent.

### 1.4 The operational moments this screen serves

- **M-A — Campaign dispatch.** Marketing has a filled template of recipients. They import it, the orders exist as `MKT-#####`, carriers are assigned by country, and the warehouse sees them in RTO within seconds.
- **M-B — Sample campaign toggle.** Marketing decides "every order from now on ships with a sample set". They press ON, set a start datetime and `forever`, and every qualifying order created afterwards carries exactly one set.
- **M-C — Sample campaign stop.** The campaign ends early. They cancel the period; new orders stop receiving sets, and orders already assigned keep theirs so that picking lists already printed remain true.
- **M-D — Mixed-list supervision.** The order team works the combined list, merges duplicates, exports, and answers `@mention` comments through the hub.

---

## 2. Screen Inventory & Wireframe Map

### 2.1 Declared unit count (for coverage checking)

Counted directly from `wms2/order-management/index.html`, not from the planning documents:

- **Legend-numbered implementation units: 9** — legend list entries `1`, `2`, `3`, `4`, `5` (5 `<li>` items) plus modal markers `M1`, `M1b`, `M2`, `M3` (4 modal dots).
- **Rendered `.dot` elements: 9** — `5`, `1`, `2`, `2`, `4`, `M2`, `M3`, `M1`, `M1b`. Dot `2` is rendered twice (one per button); legend `3` renders no dot at all. The two facts cancel out, which is why the dot count and the unit count coincide at 9.
- **Spec keys derived from the 9 units: 10** — legend `2` covers two distinct buttons and is keyed `[L-2a]` (ON) and `[L-2b]` (Cancel), per `_review` §2c.2.
- **Page-furniture keys: 6** — `[L-F1]`…`[L-F6]`.
- **Total spec-addressable units in §3: 16.**

**Why `[L-F{n}]` and not `[L-{state}-F]`:** `_review` §3.1 reserves `[L-{state}-F]` for off-screen normative *footer paragraphs* on multi-state pages, and `_review` §2a records **no** off-screen normative block for `order-management` (only view-orders, inbound-request and closing carry one). This page has a single state, so it uses plain `[L-{n}]` keys and keys its unnumbered furniture — including the legend's closing paragraph — as `[L-F{n}]`, which is `_review` §3.1's form for unnumbered page furniture.

### 2.2 Declared numbering gaps and rendering artifacts (not coverage holes)

| Artifact | Status |
|---|---|
| Legend `3` has **no on-screen dot** | Deliberate — it marks a *removed* feature (Bulk Hold Shipment). Listed in `_wireframe-fixes` §E as an explicit NON-fix. Specified as a negative contract in `[L-3]` |
| Dot `2` is rendered **twice** (once per button) | One legend number, two controls. Keyed `[L-2a]` / `[L-2b]` |
| `M1b` is a **sub-dot inside M1** | Sub-dot on the `Carrier (auto)` column header of the Import modal's preview table, keyed `[L-M1b]` per `_review` §2c.2 |
| Order list table is **omitted** from the mock (dashed placeholder) | Deliberate — "identical to the current admin". `[L-4]` specifies the deltas only |
| The spelling `Ready to be Outbonded` in the M1 note | The real admin's spelling, deliberately preserved (`_wireframe-fixes` §E). Kept byte-verbatim in this spec and in QA |
| No dot numbered `6` or higher exists | The legend ends at 5; there is no gap |
| No Korean strings appear anywhere on this page | Stated so that `[G-6]`'s "Korean is data, never translated" clause is not looked for here and its absence is not read as a defect |

### 2.3 State / modal map

The page has **one screen state** (the dashboard) plus three modals and one dropdown.

| # | Unit | Wireframe anchor (exact selector) | How to reach it on the live wireframe | Spec section |
|---|---|---|---|---|
| 1 | Marketing Order Import trigger | `.filterbar button[data-modal="m-import"]`, label `⬆ Import` | Click `⬆ Import` at the right end of the filter bar | §3.1 `[L-1]` |
| M1 | Marketing Order Import modal | `#m-import` | `.wf-bar button[data-modal="m-import"]` (`Modal: Marketing Import`), or `[L-1]` | §3.2 `[L-M1]` |
| M1b | `Carrier (auto)` preview column | `#m-import thead th:last-child` + `#m-import tbody tr td:last-child` | Open M1; the column is the rightmost in the Preview table | §3.3 `[L-M1b]` |
| 2 | Sample Assignment ON trigger | `.actionrow button[data-modal="m-sampleon"]` | Click `Sample Assignment ON` in the action row | §3.4 `[L-2a]` |
| 2 | Cancel Sample Assignment trigger | `.actionrow button[data-modal="m-sampleoff"]` | Click `Cancel Sample Assignment` in the action row | §3.5 `[L-2b]` |
| M2 | Sample Assignment ON modal | `#m-sampleon` | `.wf-bar button[data-modal="m-sampleon"]`, or `[L-2a]` | §3.6 `[L-M2]` |
| M3 | Cancel Sample Assignment modal | `#m-sampleoff` | `.wf-bar button[data-modal="m-sampleoff"]`, or `[L-2b]` | §3.7 `[L-M3]` |
| 3 | Bulk Hold Shipment — **removed** | none (no dot, no markup) | Not reachable — absence is the requirement | §3.8 `[L-3]` |
| 4 | Order list table | `div.anno[style*="dashed"]` inside `.pagepad` | Visible on load | §3.9 `[L-4]` |
| 5 | Comments hub | `.nav button[data-open="inbox1"]` → `#inbox1` | Click `💬 Comments` (badge `3`) in the top nav | §3.10 `[L-5]` |
| F1 | Legend closing paragraph (unchanged-furniture contract) | `.legend > p` | Read below the legend list | §3.11 `[L-F1]` |
| F2 | Page header + order count | `.ptitle` | Visible on load | §3.12 `[L-F2]` |
| F3 | Filter bar controls | `.filterbar` | Visible on load | §3.13 `[L-F3]` |
| F4 | Action-row controls other than the sample pair | `.actionrow` | Visible on load | §3.14 `[L-F4]` |
| F5 | Global toast surface | `.gtoast` (injected as `#gtoast` / `#gtoast2`) | Appears after `Confirm Import` / `Cancel Selected Periods` | §3.15 `[L-F5]` |
| F6 | Global navigation shell | `.nav` | Visible on load; hosts `[L-5]` | §3.16 `[L-F6]` |

**Wireframe-only chrome, excluded from the product** (must not ship): the purple `.wf-bar` header and its **five** buttons (`Modal: Marketing Import`, `Modal: Sample Assignment ON`, `Modal: Cancel Sample Assignment`, `Import preview: unconnected row` / `#impPreviewToggle` — added 2026-08-04 by `WF-16b` to carry both `[G-17]` preview states, `Hide annotations` / `#annoToggle`), the `.dot` annotation markers, the `body.no-anno` toggle class, and the `.legend` block. These exist to navigate the mock. They are named here so a developer does not port them (QA-GBL-11).

### 2.4 Wireframe defects observed while writing this spec

**Registered defects that touch this page: none.** None of WF-1…WF-14 is on `order-management`. `_wireframe-fixes` §E names this page twice, and both entries are honoured here: legend 3's missing dot is an intentional artifact (§2.2), and "order-management preview data is static" is a demo limitation, not a bug.

Seven further artifacts were found while auditing the HTML against the decided behaviour. They were **registered** in `_wireframe-fixes` **§F** (appended 2026-08-03) and have since been **APPLIED to the wireframe by the owner-approved wireframe-edit pass on 2026-08-03** — the register records each of the seven as `APPLIED 2026-08-03`, and the live drawing now implements all seven fixes. They keep the `· proposed` suffix inside their ID token only because **IDs are never renumbered or re-tokenised once shipped specs cite them** (`_wireframe-fixes` §F collision warning); the suffix is no longer a status claim. Each bullet below records the defect as found **and** what landed. The spec text stated the correct behaviour throughout, so no requirement moved; the QA scenarios that observed the pre-fix behaviour have been **re-baselined onto the fixed behaviour** (v1.3) and are no longer defect-documentation.

- **[WF-15 · proposed]** M1 preview table: the collapse row `⋯ +8 more rows` used `colspan="6"` while the table has **7** `<th>` (`Recipient · Country · SKU · Product Name · Qty · Campaign · Carrier (auto)`), so the row under-spanned by one cell. Fix: `colspan="7"`. **APPLIED 2026-08-03** — the collapse cell now carries `colspan="7"`. Asserted by QA-IMP-35.
- **[WF-16b]** — **APPLIED 2026-08-04.** The import preview now carries **both** `[G-17]` states from one demo file. Default is the **clean** file: the `PE` row resolves to `YunExpress` (green), no banner, `#mktConfirm` enabled. The wf-bar toggle `#impPreviewToggle` flips it to the **blocked** file: `#mktPECell` renders red `Cannot import — no connected carrier`, the `#mktBlock` banner appears with its byte-exact copy, and `#mktConfirm` gains `disabled` + `aria-disabled="true"`. QA-IMP-15 asserts **both halves**, so the blocked state is now covered where previously nothing tested it; the census is unchanged at 647. The toggle is wireframe-only chrome and must not ship (§2.2). *(Superseded registration text follows.)* **[WF-16b · original]** — **REGISTERED 2026-08-04, not applied.** The M1 import preview still ships the design `[G-17]` superseded: an **amber** `Not connected — contact the Fulfillment Center` cell, `#mktConfirm` **enabled**, and a confirm toast reporting `1 not connected`. Correct behaviour is a **red** `Cannot import — no connected carrier` cell, a `#mktBlock` banner naming the countries and both remedies, a **disabled** `#mktConfirm`, and a toast subtext of just `Carrier auto-assigned per country`. **Deliberately not applied yet:** the shipped demo file contains the blocking `PE` row, so the fix alone would strand the mock in the blocked state and make the success path unreachable — a trial run on 2026-08-04 turned **6 `[WF]` scenarios red**. The mock must carry both states first (a wf-bar preview toggle, or a connected `PE` plus a second blocked-preview state), which is a wireframe-design call. Until it lands, **`[WF]` scenarios assert the shipped amber design and `[ADMIN]` scenarios assert the specified one** — the same split `WF-9` used. Register: `_plans/_wireframe-fixes.md`.
- **[WF-16 · proposed]** M2 footer button `Start Assignment (ON)` carried `data-close` but **no toast handler** and no `id` — it closed the modal silently. This contradicted `[G-2]`, which `_review` C-6 rules wins over wireframe omissions. Fix: add an `id` and the toast defined in §3.6.5. **APPLIED 2026-08-03** — button id `sampStartBtn`; green toast node `#gtoast3` carrying the §3.6.5 byte-exact copy (`✓ Sample assignment started` plus the target-dependent subtext). Asserted by QA-SMP-30.
- **[WF-17 · proposed]** M3 footer button `Cancel Selected Periods` (`#sampCancelBtn`) fired its toast unconditionally — including when zero checkboxes were checked — and there was no confirm step. Fix: disable at zero selection and add the confirm dialog defined in §3.7.5 `[PD-5 · OWNER-PENDING]`. **APPLIED 2026-08-03** — the button is disabled at zero selection, and a click at non-zero selection opens the confirm overlay `#m-sampcancel-confirm` (`Cancel {n} assignment period(s)?` / `Keep periods` / `Cancel periods`); the green toast now fires only after `#sampConfirmGo`. Asserted by QA-SMP-31 (zero selection) and QA-SMP-19 (the confirm-then-toast path).
- **[WF-18 · proposed]** The two confirming actions created **two independent toast nodes** (`#gtoast` from `#mktConfirm`, `#gtoast2` from `#sampCancelBtn`), so two toasts could occupy the same fixed position simultaneously. Fix: a single toast slot (replace) or an explicit stack. See [E-62]. **APPLIED 2026-08-03** — the explicit-stack option: per-action nodes are kept (`#gtoast` / `#gtoast2` / `#gtoast3`, so toast identity stays assertable) and a shared `stackToasts()` repositions every visible toast down the right edge from `top:16px` in `offsetHeight + 8 px` steps, so no two ever overlap. Asserted by QA-GBL-09.
- **[WF-19 · proposed]** In M2 the `forever (no end date)` checkbox ships **checked** while the `End date` and `Time` inputs remained enabled and editable, which contradicted the specified mechanic (`forever` wins; end fields cleared and disabled — §3.6.3, [E-23]). Fix: disable and clear the end fields while `forever` is checked. **APPLIED 2026-08-03** — `#sampEndDate` / `#sampEndTime` are cleared and `disabled` while `#sampForever` is checked, synced on load and on every change. Asserted by QA-SMP-33.
- **[WF-20 · proposed]** No modal responded to the `Esc` key — there was no `keydown` listener anywhere in the file. `Esc` is a specified dismissal path (§3.2.6, [E-97]). Fix: add `Esc` dismissal to all three overlays. **APPLIED 2026-08-03** — a `document` `keydown` listener closes the topmost `.overlay.open` (all four overlays, including the confirm overlay added by WF-17) and, when no overlay is open, the Comments hub. Asserted by QA-GBL-10.
- **[WF-21 · proposed]** The Comments hub did not close on an outside click, yet the code carried the guards written for that behaviour (`onclick="event.stopPropagation()"` on `.csearch`, `e.stopPropagation()` on the hub button, the tab buttons and the stars). The `document`-level close handler those guards protect against was never added, so the guards were dead code and the hub could only be closed by clicking its own trigger again. Fix: add the outside-click (and `Esc`) close. **APPLIED 2026-08-03** — a `document`-level click handler closes every `.inboxdd.open` unless the click landed inside `.inboxdd` (`e.target.closest('.inboxdd')`), which makes the pre-existing guards live rather than dead; `Esc` is covered by WF-20. Asserted by QA-CMT-20.

**Known demo limitations that are NOT defects** and must be tagged `[ADMIN]` in QA rather than filed as bugs (`_wireframe-fixes` §E): the M1 preview data is static and the dropzone parses nothing, `#mktConfirm` toasts regardless of validation state, filter-bar and action-row controls are inert, `Mark all read` has no handler, and the order list table is absent from the mock entirely.
*(Through v1.2 this list also carried "`#sampCancelBtn` toasts regardless of selection". That is no longer true — `[WF-17 · proposed]` was applied on 2026-08-03 and the button is now gated and confirmed. The entry is recorded here as history, not as a live limitation.)*

---

## 3. Functional Specification

Conventions used below: **Trigger** = what the operator does · **Enabled when** = the precise gate · **Effect** = server + client outcome · **Feedback** = what the operator sees · **Persists** = the `[DC-n]` events written · **Idempotency** = the `[G-9]` requirement. All quoted UI copy is byte-accurate to the wireframe unless the line is explicitly marked as added by this spec.

---

### 3.1 `[L-1]` — `⬆ Import` (Marketing Order Import trigger)

- **Label (byte-exact):** `⬆ Import`. Purple fill `--mkt` `#7C3AED`, white text, class `.btn.btn-mkt.btn-sm`, positioned last in the filter bar after `⬇ Yun Export`.
- **Trigger:** click.
- **Enabled when:** always. No list state, selection state, or filter state disables it, and no role gate exists on it (BR-22).
- **Effect:** opens `[L-M1]` as a modal overlay (`#m-import`, `.overlay.open`). The dashboard behind it keeps its filter, selection and pagination state `[G-2]`.
- **Feedback:** the modal appears centred over a `rgba(10,6,20,.55)` scrim.
- **Persists:** nothing. Opening a modal is a declared **NON-event** (§5.4).

---

### 3.2 `[L-M1]` — Marketing Order Import modal

Modal header: `Marketing Order Import`, with a `✕` close control (`#m-import header .x[data-close]`). Width 720 px (`.modal.wide`). Four numbered steps, a preview, a note, and a two-button footer.

#### 3.2.1 Step 1 — Template

- **Copy (byte-exact):** bold label `1. Template`; button `⬇ Download Template (.xlsx)` (outline blue, `.btn.btn-line.btn-sm`); helper text `Standard form from the dev team — Recipient · Contact · Address · Country · SKU · Qty · Campaign name`.
- **Trigger:** click on `⬇ Download Template (.xlsx)`.
- **Enabled when:** always.
- **Effect:** streams the current `.xlsx` template. Its seven columns are the parse contract: **Recipient · Contact · Address · Country · SKU · Qty · Campaign name**. The template is produced and versioned by the dev team; the template carries a version stamp so an outdated file can be detected at parse time ([E-71]). Header-matching policy is a developer decision (§9.3).
- **Feedback:** a browser file download. No toast — a download is not a confirming action.
- **Persists:** `[DC-1] import.template_downloaded` — actor, timestamp, template version.

#### 3.2.2 Step 2 — Order Type

- **Copy (byte-exact):** bold label `2. Order Type`; chip `Influencer Seeding` (`#otChipSeed`, selected by default, `.cchip.on`, purple fill); chip `✎ Custom` (`#otChipCustom`); free-text input `#otCustom`, placeholder `Enter type (e.g. Pop-up event giveaway)`, `display:none` until Custom is chosen.
- **Trigger:** click either chip.
- **Behaviour:** the chips are mutually exclusive. Selecting `✎ Custom` removes `.on` from `Influencer Seeding`, adds it to `✎ Custom`, sets `#otCustom` to `display:inline-block`, and **moves focus into `#otCustom`**. Selecting `Influencer Seeding` again hides `#otCustom`; the typed value is retained in the field but is ignored while the preset chip is active. The persisted order type is always the value of the *active* chip.
- **Validation:** if `✎ Custom` is active and `#otCustom` trimmed is empty, `Confirm Import` is disabled and an inline message reads `Enter an order type.` ([E-14]).
- **Feedback:** chip fill change plus focus move. No toast.
- **Persists:** nothing at selection time — chip toggling is a declared **NON-event** (§5.4). The resolved value is persisted once, on confirm, inside `[DC-6]`.

#### 3.2.3 Step 3 — PIC

- **Copy (byte-exact):** bold label `3. PIC`; a `<select>` whose demo options are `Yongwon Ryu (me)` (selected), `Harshit`, `EuJin`, `Adinda`; button `✎ Custom` (`#picCustomBtn`); free-text input `#picCustomIn`, placeholder `Enter PIC name`, hidden by default; helper text `Default = logged-in user · Recorded as the PIC for this entire import — shown in the order list & RTO`.
- **Behaviour:** the select is populated with system users and defaults to the logged-in user, rendered as `{Full Name} (me)`. `✎ Custom` toggles `#picCustomIn` between hidden and `display:inline-block` and, when showing it, **moves focus into it**. While `#picCustomIn` is visible and non-empty, its text is the PIC of record and the select value is ignored; the select is visibly de-emphasised (exact affordance is a developer decision, §9.3).
- **Validation:** if `#picCustomIn` is visible and its trimmed value is empty, `Confirm Import` is disabled with the inline message `Enter a PIC name.` ([E-15]).
- **Scope:** exactly **one PIC applies to the entire import batch** (BR-21). There is no per-row PIC column in the template.
- **Free-text PIC:** stored as a display string, not a user reference. It renders in the order list PIC column and in RTO, it is matched by the `Search PIC` filter as a case-insensitive substring, and it **cannot be `@mention`-notified** — a free-text PIC resolves to no Slack user ([E-59], [E-93], §6.1). It is never retroactively resolved if a system user with the same display name is created later ([E-93]).
- **Persists:** nothing at toggle time (NON-event). The resolved PIC is persisted inside `[DC-6]` and per order in `[DC-12]`.

#### 3.2.4 Step 4 — Upload and preview

- **Copy (byte-exact):** bold label `4. Upload`; dropzone text `📄 Drag the completed template here or click to upload`.
- **Trigger:** drag-and-drop onto `.dropzone`, or click to open a file picker. (The wireframe's dropzone is inert — QA-IMP-37.)
- **Accepted input:** `.xlsx` only. `.csv`, `.xls`, and files renamed to `.xlsx` that fail to parse as XLSX are rejected inline and no rows are parsed ([E-1]).
- **Effect:** the file is uploaded and parsed server-side. Parsing produces a **draft batch** with a per-row result set: parsed values, row-level errors with reasons, and an advisory carrier resolution per row (§3.3). Only the first worksheet is read; formula cells are read as cached values ([E-70]). Field values are trimmed of leading/trailing whitespace before validation, and a value that is only whitespace is treated as missing ([E-68]).
- **Parse contract — what is *not* validated here:** free-text fields are stored verbatim and are never measured against a carrier's field limits. A Recipient or Address longer than the destination carrier will accept still imports ([E-78]), and a Contact number without a country dialling code still imports ([E-79]); carrier-format validation belongs to the label/export pipeline, not to this parse. Row and byte limits ([E-16]) and template-schema matching ([E-17]) are the two file-level rejections that happen before any row is parsed.
- **Preview render (byte-exact format):** a bold header line `Preview — {filename} · {n} rows parsed · {e} errors` (demo: `Preview — mkt_seeding_batch3.xlsx · 12 rows parsed · 0 errors`), followed by a table with headers `Recipient` · `Country` · `SKU` · `Product Name` · `Qty` · `Campaign` · `Carrier (auto)`. Long files collapse the middle with a single row `⋯ +{m} more rows` (demo: `⋯ +8 more rows`) spanning **all seven** columns (the wireframe under-spanned it at six until [WF-15 · proposed] was applied 2026-08-03; it now renders `colspan="7"`).
- **Product Name rendering:** the brand is bold-prefixed per `[G-6]` — demo rows render `**Dr.Jart+** Cicapair Gentle Cleansing Foam`, `**Dr.Jart+** Cicapair Sleepair Mask`, `**innisfree** Green Tea Seed Hyaluronic Serum`. Product Name is resolved from the SKU by the system; it is not a template column, and a value supplied in an extra column of that name is ignored in favour of the system value ([E-72]).
- **Row errors:** every failing row is counted in `{e}` and shown with its reason. The blocking row validations are exactly five: a missing required field ([E-3]), an **unknown SKU** not present in the catalog ([E-4]), an invalid quantity ([E-5]), an **invalid or unsupported country code** ([E-6]), and a value that fails coercion ([E-69]). [E-6] is a *country* error and is distinct from an unconnected *carrier*, which never blocks ([E-7]). A file with `{e} > 0` **cannot be confirmed** — the whole file is blocked, not partially imported (BR-12, `[PD-57 · OWNER-PENDING]`, [E-19]).
- **Persists:** `[DC-2] import.file_uploaded` on receipt (actor, timestamp, filename, byte size, SHA-256 hash, parse outcome) then `[DC-3] import.file_parsed` (draft batch id, row count, error count, per-row parse result, per-row **advisory** carrier result, parser/template version). Both persist **even if the operator abandons the modal** — an abandoned upload is evidence of an attempt `[G-8]`.

#### 3.2.5 Footer and confirm

- **Copy (byte-exact):** `Cancel` (grey, `data-close`) and `Confirm Import ({n} orders)` (purple, `#mktConfirm`; demo label `Confirm Import (12 orders)`), where `{n}` is the number of parsed data rows.
- **`Confirm Import` is enabled if and only if all of:**
  1. a file has been uploaded and parsed;
  2. `{e} == 0` (no row errors — an unknown SKU [E-4] and an invalid country code [E-6] each keep `{e} > 0` and therefore keep this gate shut) — BR-12;
  3. `{n} >= 1` ([E-2], [E-63]);
  4. Order Type is resolved (preset chip active, or Custom chip active with non-empty text) — [E-14];
  5. PIC is resolved (select value, or visible Custom input with non-empty text) — [E-15].
  Zero stock on any SKU is **never** part of this gate (BR-1, [E-20]). An unconnected carrier on any row is **never** part of this gate (BR-20, [E-7], [E-8]). A discontinued or unpublished SKU is **never** part of this gate ([E-73]).
- **Effect on click:**
  1. Client debounce plus a server idempotency key make the action double-click safe `[G-9]`; a repeated submission returns the *same* batch and does not create a second one ([E-11], [E-75]). Key construction is a developer decision (recommended: file hash + operator id + monotonic nonce) (§9.3).
  2. The server re-validates the draft batch at confirm time `[PD-6 · OWNER-PENDING]`. If the draft is stale (template version changed, SKU withdrawn, carrier mapping changed), the confirm is rejected with a red toast and the preview is refreshed. Nothing partial is written. (PD-6's register entry lists VO/OD/RTO/INV/TM/CL; this page applies the same doctrine to the import draft and the period list — reversing PD-6 reverts both.)
  3. If the file hash matches a previously confirmed batch, the server does **not** create the batch. It returns a duplicate warning and the client shows a confirm dialog: title `This file was already imported`, body `Imported {datetime} as batch {batchId} ({n} orders).`, buttons `Cancel` and `Import anyway`. Choosing `Import anyway` proceeds `[PD-58 · OWNER-PENDING]` ([E-10]).
  4. On success the batch is created **atomically** — either all `{n}` orders exist or none do ([E-12], BR-12). Order numbers are minted as `MKT-#####` from a central collision-safe sequence ([E-41], §9.3); an order-number column supplied in the file is ignored ([E-51]).
  5. Per row, the carrier is resolved and assigned (§3.3).
  6. The modal closes. The dashboard behind it **does not reload** `[G-2]`: the order list refreshes in place, the header count increases by `{n}` (demo: `2,818 orders` → `2,830 orders`), and the new MKT rows appear with the treatment specified in `[L-4]` ([E-45], [E-57]).
- **Feedback:** a green toast top-right `[G-2]`:
  - Title (byte-exact): `✓ Confirmed — {n} orders imported` (demo: `✓ Confirmed — 12 orders imported`)
  - Subtext (byte-exact): `Carrier auto-assigned per country` — **amended 2026-08-04 `[G-17]`.** The former `· {u} not connected — flagged to contact Fulfillment Center` clause is deleted: a confirmed import can no longer contain an unconnected row, so `{u}` is always `0` and the clause can only mislead. The **wireframe still ships the old subtext** — registered as `[WF-16b]`, §2.4; `[WF]` QA asserts the shipped string until the fix lands, `[ADMIN]` QA asserts the string above.
  - When `{u} == 0` the subtext reads `Carrier auto-assigned per country · all rows connected`.
  - Auto-dismiss (the wireframe uses 2 600 ms); duration and stacking policy are developer decisions (§9.3).
  - **Failure** is a **red** toast carrying the server reason `[G-2]`; the modal stays open with its staged file intact so the operator can retry.
- **Persists:** `[DC-4]`/`[DC-5]` (duplicate path), `[DC-6] import.batch_confirmed`, `[DC-9] order.created` ×n, `[DC-10] order.carrier_assigned` ×n, `[DC-12] order.pic_assigned` ×n, `[DC-7] import.batch_rejected` on failure — **including a file with any unconnected row `[G-17]`** — and `[DC-28] idempotency.duplicate_suppressed` on a suppressed repeat. (`[DC-11]` retired 2026-08-04 by `[G-17]`.)

#### 3.2.6 Abandoning the modal

Closing via `✕`, `Cancel`, `Esc`, or a click on the overlay backdrop discards the staged draft batch: **no orders are created** ([E-13]). `[DC-2]` and `[DC-3]` remain persisted, and `[DC-8] import.batch_abandoned` is written with the draft batch id and the reason (`user_closed` / `session_lost`). The same discard path covers an *involuntary* abandonment — a closed tab or a lost browser session mid-upload orphans the staged draft, which is reaped with reason `session_lost` and creates nothing ([E-55]). Uploaded source-file retention is specified in §5.5. The wireframe implements all four paths: `✕`, `Cancel`, backdrop, and — since [WF-20 · proposed] was applied 2026-08-03 — `Esc`, which closes the topmost open overlay ([E-97]).

#### 3.2.7 Modal note (byte-exact, must be present)

`On confirm, orders are created as MKT- orders and appear immediately in Ready to be Outbonded (Marketing view) regardless of stock or inbound status.`

The spelling `Outbonded` is the live admin's and is preserved verbatim (`_wireframe-fixes` §E). This note is the operator-visible statement of BR-1 and must not be edited to add a stock caveat.

---

### 3.3 `[L-M1b]` — `Carrier (auto)` column

- **Column header (byte-exact):** `Carrier (auto)`, rightmost column of the preview table.
- **Rule:** each row's **Country** is resolved against the country → connected-carrier mapping. The mapping resolves to **exactly one** carrier per country; no batch-level carrier exists, so a mixed-country file produces different carriers on different rows ([E-18], [E-81]).
- **Timing:** the preview renders an **advisory** projection using the mapping as of parse time. The **authoritative** assignment happens at confirm time. If the mapping changed in between, the confirm-time value wins and the toast subtext reports confirm-time counts ([E-65]).
- **Connected country:** the cell renders the carrier name in **green bold** (`--green` `#198754`, `font-weight:700`). Demo: every `GB` row shows `YunExpress`.
- **Unconnected country — blocks the file `[G-17]`:** the cell renders, in **red bold** (`--red` `#DC3545`, computed `rgb(220, 53, 69)`, `font-weight:700`), the byte-exact string `Cannot import — no connected carrier`. Demo: the `PE` row (recipient `Lucia Ramos`). **No order is created — not for this row and not for any other row in the file.** `Confirm Import` is **disabled** (`disabled` attribute plus `aria-disabled="true"`) for as long as any row is unconnected, and a blocking banner above the table reads `Cannot import — these countries have no connected carrier: {countries}. Ask the fulfillment team to connect them, or remove those rows and upload again.` with `{countries}` the distinct ISO codes in file order, comma-separated (BR-20, [E-7]). A file where **every** row is unconnected is rejected the same way — there is no all-unconnected exception and no partial import ([E-8]). A country whose mapping exists but whose carrier connection is **disabled** at confirm time is treated identically, with reason `connection_disabled` ([E-80]).
- **Ambiguous mapping:** if configuration yields more than one connected carrier for a country, the confirm fails with a red toast naming the country and **no** orders are created (atomicity, BR-12). This is a configuration error, not an operator error ([E-52]).
- **Downstream:** there is nothing to unblock. `[G-17]` (2026-08-04) rejects the whole file at import, so no flagged order ever exists downstream — this voids `[PD-55]` and the manual-Slack-coordination answer recorded under it on 2026-08-03. The importer contacts the Fulfillment Center, fixes the carrier connection, and re-uploads.
- **Persists:** `[DC-10] order.carrier_assigned` (`old = null → new = {carrier}`, mapping version) per order on success; `[DC-7] import.batch_rejected` (`reason = no_connected_carrier | connection_disabled`, affected countries) for the file on rejection.

---

### 3.4 `[L-2a]` — `Sample Assignment ON` button

- **Label (byte-exact):** `Sample Assignment ON`. Green fill `--green` `#198754`, `.btn.btn-green.btn-sm`, in the action row after `⧉ Merge Orders`.
- **Enabled when:** always — including when zero orders are selected. Selection state gates the *radio inside* `[L-M2]`, not the button ([E-21]).
- **Effect:** opens `[L-M2]` (`#m-sampleon`). The modal reads the current list-selection count at open time and binds it to the second radio's **label**; the order set itself is resolved again at submit time (BR-33, [E-84]).
- **Persists:** nothing (NON-event).

---

### 3.5 `[L-2b]` — `Cancel Sample Assignment` button

- **Label (byte-exact):** `Cancel Sample Assignment`. Neutral outline, `.btn.btn-gray.btn-sm`, immediately right of `[L-2a]`.
- **Enabled when:** always.
- **Effect:** opens `[L-M3]` (`#m-sampleoff`) and loads the full period list (`Scheduled`, `Active`, `Ended`, `Cancelled`) newest-first.
- **Persists:** nothing (NON-event).

---

### 3.6 `[L-M2]` — Sample Assignment ON modal

Header (byte-exact): `Sample Assignment ON`, with `✕`.

#### 3.6.1 Assignment Target

Bold group label `Assignment Target`, then two bordered radio rows (`name="samptarget"`):

1. `All new orders in this period` — **default selected**.
2. `Selected orders only ({n})` — `{n}` is the list-selection count read at open time (demo: `Selected orders only (2)`).

- If `{n} == 0`, radio 2 is **disabled** and its label reads `Selected orders only (0)` ([E-21]).
- The two targets have materially different semantics (BR-15, BR-16) and both are specified in §3.6.5.

#### 3.6.2 Assignment Period

Bold group label `Assignment Period`, then, on one wrapping row:

| Field | Wireframe demo value | Required |
|---|---|---|
| Start date | `2026-07-23` | Yes |
| Start time | `10:00` | Yes |
| separator `~` | — | — |
| End date | placeholder `End date` | Only when `forever` is unchecked |
| End time | placeholder `Time` | Only when `forever` is unchecked |
| Checkbox `forever (no end date)` | **checked** by default | — |

All four datetime fields are entered, evaluated and displayed in the admin's single configured operating timezone (BR-31); storage is UTC.

#### 3.6.3 Validation

- Start date **and** start time are required. Missing either → `Start Assignment (ON)` disabled, inline message `Enter a start date and time.`
- `forever` checked → the end date and end time fields are **cleared and disabled**; `forever` wins over any previously typed end value ([E-23]). The wireframe left them enabled until [WF-19 · proposed] was applied 2026-08-03; it now clears **and** disables both, synced on load and on change. The exact mechanic (clear-on-check vs. disable-and-ignore) remains a developer decision (§9.3) — the wireframe demonstrates the recommended default, it does not narrow the decision.
- `forever` unchecked → both end fields are required ([E-54]) and the end datetime must be **strictly later** than the start datetime; otherwise the button is disabled with `End must be later than start.` ([E-22], [E-82]).
- Start **and** end both already in the past → blocked with `A period that has already ended cannot be created.` No already-`Ended` period may be minted ([E-83]).
- A start datetime in the future is valid and produces a `Scheduled` period ([E-53]).
- A start datetime in the past is valid but is **not retroactive** (BR-15, `[PD-52 · OWNER-PENDING]`, [E-25]).

#### 3.6.4 Modal note (byte-exact, must be present)

`Sample product type is not selected — when ON, "(+ sample set)" is auto-appended to the last product name of target orders and a sample-set row is added at the bottom of the invoice (defined in G). Multiple overlapping periods can be registered — but even with overlapping periods, exactly 1 sample set per order (no duplicate assignment).`

There is **no sample-type selector in this modal and none may be added** (BR-6). The internal-artifact content question is **decided**: v1 makes no sample distinction — internal invoice and picking artifacts print **"sample set" only**, no sample type and no per-type quantity (`[PD-51]` owner-decided 2026-08-03; "which sample and how many" becomes relevant only when sample types are introduced — §9.1, resolved).

#### 3.6.5 `Start Assignment (ON)` — effect

- **Copy (byte-exact):** footer buttons `Cancel` (grey, `data-close`) and `Start Assignment (ON)` (green, `data-close`).
- **Enabled when:** the validation in §3.6.3 passes and a target radio is selected.
- **Effect, target = `All new orders in this period`:**
  - Creates an assignment-period entity with `target_type = all_new_in_period`, the start datetime, and either the end datetime or `forever = true`.
  - Every **sales** order created at or after the start datetime and before the end datetime receives exactly one sample set at creation time. Boundary: start is **inclusive**, end is **exclusive** ([E-61]). Matching is a server-side rule, so orders created by an integration rather than by the admin UI are matched identically ([E-91]).
  - `MKT-` marketing orders are **never** matched (BR-17, `[PD-56 · OWNER-PENDING]`, [E-35], [E-56]).
  - Orders created **before** the ON action are not touched, even if the start datetime is backdated (BR-15).
  - If two or more periods match the same order, the order still receives exactly **one** set (BR-7); suppressed matches are recorded ([DC-15]).
- **Effect, target = `Selected orders only ({n})`:**
  - Resolves the selection **at submit time** (BR-33) and assigns a sample set **immediately** to those orders. The period datetimes are recorded as informational/audit metadata and gate nothing (BR-16, `[PD-53 · OWNER-PENDING]`, [E-33]).
  - Selected orders that already hold a set are **skipped**, not double-assigned (BR-7); the skip count is surfaced in the toast subtext and persisted ([DC-15]).
  - Selected orders that are `MKT-`, cancelled, or otherwise ineligible are skipped and counted separately ([DC-16], [E-85]).
  - If the resolved selection is empty at submit time, the submit is blocked with `No eligible orders are selected.` and nothing is created ([E-84]).
  - Selections above the configured batch ceiling are processed asynchronously and the toast reports the queued count; the ceiling is a developer decision ([E-86], §9.3).
- **What an assigned set prints (dual view, BR-8 `[G-13]`):** every order that receives a set is subject to the same split — carrier-facing data appends only `(+ sample set)` to the **last** product name, while the internal invoice and picking artifacts render a single **"sample set"** line — v1: "sample set" only, no type/qty breakdown (`[PD-51]` owner-decided 2026-08-03) ([E-34], `[PD-36]` owner-decided 2026-08-04). This page decides the split; the divergence itself is asserted against the consuming specs (§6.5).
- **Idempotency:** double-click safe `[G-9]` — one period, one assignment pass ([E-44] covers the network-failure variant: no partial or ghost period).
- **Feedback — the toast this modal must show.** The wireframe omitted it until [WF-16 · proposed] was applied 2026-08-03; it now ships it as node `#gtoast3` on `#sampStartBtn`. `[G-2]` and `_review` C-6 require it:
  - Title (byte-exact): `✓ Sample assignment started`
  - Subtext, target = all-new (byte-exact template): `All new sales orders from {start} → {end|forever} · exactly 1 sample set per order`
  - Subtext, target = selected (byte-exact template): `{a} orders assigned · {s} skipped (already assigned) · {m} skipped (not eligible)`
  - Green; auto-dismiss; no page reload `[G-2]`.
- **Persists:** `[DC-13] sample.period_created`; `[DC-14] sample.assigned_to_order` ×a; `[DC-15] sample.assignment_deduped` ×s; `[DC-16] sample.assignment_skipped_ineligible` ×m.

#### 3.6.6 What a period does **not** do

- It does not modify orders retroactively (BR-15).
- It does not remove a sample set when it ends or is cancelled (BR-19) — an assigned order keeps its set through outbound ([E-26]).
- It does not track the order's own lifecycle. If an order is cancelled or refunded after a set was assigned, the assignment record persists on that order and **no** `sample.unassigned` event is written; sample handling on the internal documents then follows the order's lifecycle, not the period's ([E-31]).
- It does not select a sample product type (BR-6).
- It does not notify Slack. There is **no** Slack route for sample-period changes in v1 (§6.2).

---

### 3.7 `[L-M3]` — Cancel Sample Assignment modal

Header (byte-exact): `Cancel Sample Assignment — Current Assignment Periods`.

#### 3.7.1 Table

Columns (byte-exact headers): `` (empty 30 px checkbox column) · `Assignment Period` · `Target` · `Status`.

Demo rows, byte-exact:

| checkbox | Assignment Period | Target | Status |
|---|---|---|---|
| checked | `2026-07-01 09:00 → forever` | `All new orders` | `Active` |
| unchecked | `2026-07-15 00:00 → 2026-07-20 23:59` | `34 selected orders` | `Active` |
| **none** | `2026-06-01 00:00 → 2026-06-30 23:59` | `All new orders` | `Ended` |

- The period cell renders `{start} → {end}` or `{start} → **forever**` with `forever` in bold, in tabular numerals (`.num`).
- The `Target` cell renders `All new orders` or `{n} selected orders`.

#### 3.7.2 Status vocabulary

The wireframe demo shows only `Active` and `Ended`. The complete vocabulary the implementation must support is:

| Status | Meaning | Checkbox | Row style |
|---|---|---|---|
| `Scheduled` | start datetime is in the future | Yes (cancellable before it starts) | normal |
| `Active` | now ∈ [start, end) and not cancelled | Yes | green pill (`.st.st-processing`) |
| `Ended` | end datetime has passed | **No** — record only | greyed row (`--ink-3`), grey pill |
| `Cancelled` | operator-cancelled | **No** — record only | greyed row, grey pill |

`Scheduled` and `Cancelled` are additions this spec makes to complete the model; they are absent from the wireframe demo data only because the demo has no such rows.

#### 3.7.3 Row rules

- **`Ended` and `Cancelled` rows have no checkbox at all** — not a disabled checkbox, no element. This is the byte-exact wireframe behaviour and a QA assertion ([E-27]).
- Rows are never deleted from this list. The period list is a permanent record (BR-30) `[G-8]`.
- If a period's end datetime passes while the modal is open, the row flips `Active → Ended` on the next refresh and loses its checkbox; if it was checked, the selection is dropped and the operator is told at confirm time ([E-60]).

#### 3.7.4 Modal note (byte-exact, must be present)

`Multiple assignment periods may exist — select the period(s) to cancel, then confirm. Ended periods are for record only (cannot be cancelled). Cancellation immediately stops new assignments for that period (already-assigned orders are kept).`

#### 3.7.5 `Cancel Selected Periods` — effect

- **Copy (byte-exact):** footer buttons `Close` (grey, `data-close`) and `Cancel Selected Periods` (red `--red` `#DC3545`, `#sampCancelBtn`).
- **Enabled when:** at least one `Scheduled` or `Active` row is checked. At zero selection the button is **disabled** ([E-28]) — the wireframe fired regardless until [WF-17 · proposed] was applied 2026-08-03; it now disables the button at zero selection and re-syncs on every checkbox change.
- **Confirm step** `[PD-5 · OWNER-PENDING]`: clicking opens a confirm dialog before anything is written —
  - Title (byte-exact): `Cancel {n} assignment period(s)?`
  - Body (byte-exact): `New assignments stop immediately. Orders already assigned keep their sample set.`
  - Buttons: `Keep periods` (grey, dismisses) and `Cancel periods` (red, proceeds).
  - Rationale for adding a step the wireframe lacked when this clause was written: cancelling a `forever` period silently switches off a company-wide campaign; `_review` C-6 rules that wireframe omissions are gaps, not decisions. This is the only added confirm step on this page. The wireframe caught up on 2026-08-03 ([WF-17 · proposed] applied) and now builds it as the overlay `#m-sampcancel-confirm`, whose confirming button is `#sampConfirmGo`. (PD-5's register entry lists TM/CL/OD/INV; this page extends the same doctrine to period cancellation — reversing PD-5 removes this confirm step and leaves the toast.)
- **Effect:** each selected period's status moves `Scheduled|Active → Cancelled`. New matching stops **immediately** — an order created one second later receives no set ([E-66]). Orders already assigned are **not** touched: no unassignment events are emitted and their sample sets remain (BR-9, BR-19). A period another operator cancelled first is reported and skipped rather than double-written `[PD-6 · OWNER-PENDING]` `[PD-7 · OWNER-PENDING]` ([E-47]).
- **Idempotency:** double-click safe `[G-9]` — one cancellation per period ([E-29]).
- **Feedback:** green toast `[G-2]`, byte-exact:
  - Title: `✓ Assignment period cancelled`
  - Subtext: `New assignments stopped for the selected period · already-assigned orders kept`
  - The modal closes; the dashboard does not reload.
- **Persists:** `[DC-17] sample.period_cancelled` per period (`old = Active|Scheduled → new = Cancelled`, actor, timestamp, period id, target snapshot, confirm-dialog acknowledgement). **No** `sample.unassigned` event exists on this page — its absence is an assertable requirement ([E-30], QA-SMP-14).

---

### 3.8 `[L-3]` — Bulk Hold Shipment — **REMOVED (negative contract)**

**A bulk "Hold Shipment" control must NOT exist on this screen.** There is no button, no menu item, no keyboard shortcut, and no bulk action that places orders on hold from the Order Management Dashboard.

- **Where hold now lives:** Order Detail → `Change Status` → `on-hold` (spec `order-detail`; the status matrix is `[PD-28 · OWNER-PENDING]`, and the hold reason is `[PD-20 · OWNER-PENDING]`).
- **Stale cross-reference elsewhere (cross-page defect M3a D10):** `view-orders`'s State-5 legend footer and its §9.1 still name *Order Management* as a place where a hold is applied by CS. That wireframe text predates this removal (2026-08-03) and is stale; the correction is owed on the View Orders side. It confers no requirement here — no hold control may be added to this page on the strength of that sentence, and QA-LST-04 asserts its absence.
- **Why it was removed:** the OMS dashboard remains the live screen; a bulk hold from a list view sets an exception state on many orders without the per-order context in which a hold decision is actually made. Recorded 2026-08-03 (review round); the control existed in the 2026-07-09 real-capture rework.
- **Legend treatment:** legend item 3 deliberately has **no on-screen dot** and must stay in the legend as a negative entry (`_wireframe-fixes` §E) so nobody re-implements it from a stale capture.
- **QA:** an absence assertion (QA-LST-04).

#### 3.8.1 Other negative contracts on this page

| Must NOT exist | Reason | Decided | Decision-log row |
|---|---|---|---|
| Stock-availability error on import ("product not in the warehouse") | Import legitimately precedes inbound; Notion §G's stock-error item was struck | 2026-07-23 | §10, R-2 |
| Sample **type** selector in `[L-M2]` | Sample assignment is simple ON/OFF by design | 2026-07-23, reconfirmed 2026-08-03 | §10, R-1 |
| Any `Print` button or print affordance | No print surface on this page (BR-29) `[G-4]` | 2026-08-03 | §10 |
| Any scan input or scan-focus behaviour | Desk screen, no scanner (BR-28) `[G-1]` | 2026-08-03 | §10 |
| Any audio feedback (send sound or TTS) | No outbound-class button on this page `[G-3]` `[PD-2 · OWNER-PENDING]`, `_review` C-5 | 2026-08-03 | §10 |
| Photo upload / photo column | Removed program-wide `[PD-63 · OWNER-PENDING]`; recorded here so it is not introduced by analogy (this page never had one) | 2026-08-03 | §10 |
| Batch revert / "undo import" | Cleanup is per order on Order Detail `[PD-54 · OWNER-PENDING]` | 2026-08-03 | §10 |
| Partial import of a file with errors | The file is the unit of intent `[PD-57 · OWNER-PENDING]` | 2026-08-03 | §10 |
| Carrier picker for the operator | Carrier is auto-assigned by country (BR-3) | 2026-08-03 | §10 |
| A second confirm-time stock or inbound gate anywhere in the flow | Same struck check as row 1, re-entering by a different door | 2026-07-23 | §10, R-2 |

---

### 3.9 `[L-4]` — Order list table

The order list table is **identical to the current admin** and is deliberately omitted from the wireframe. The dashed placeholder reads `Order list table — same as the current admin (omitted)` with the sub-line `Default columns ↔ Columns toggle view, 2,818 total, and pagination — all unchanged.` and `However, imported MKT- marketing orders appear in this list with a purple tint + MKT badge + PIC.`

#### 3.9.1 No-change contract (BR-11)

Unchanged, and out of scope for this spec: column set and order, the `▦ Columns` toggle view, sorting, row-level menus (`.rowmenu`), the order-number link style (`.oid`, blue bold), status pills (`.st-completed` / `.st-processing` / `.st-prepare` / `.st-hold`), carrier pills (`.prov-yun` / `.prov-deleo`), sourcing-route rendering (`[G-5]`), pagination (`.pager`), and the `2,818 orders` count semantics.

#### 3.9.2 Deltas this spec does own — MKT row treatment (BR-2)

| Element | Requirement | Token |
|---|---|---|
| Row background | Purple tint on every `MKT-` order row | `tr.mkt { background: var(--mkt-soft) }` = `#F3EEFF` |
| Row hover | Distinct from the regular hover | `tr.mkt:hover { background:#EBE1FF }` vs regular `tr:hover { background: var(--blue-soft) }` = `#E7F1FF` |
| Badge | `MKT` badge immediately after the order number | `.mkt-badge`, background `--mkt` `#7C3AED`, white, 9.5 px, `font-weight:800`, `letter-spacing:.3px`, `margin-left:5px` |
| PIC column | Populated with the batch PIC (system user or free text) | plain text |
| Order number | `MKT-#####` (demo: `MKT-40233`, `MKT-40218`, `MKT-40191`) | `.oid` |

The tint is the settlement/volume separation signal and must not be replaced by a filter-only treatment ([E-36]). `MKT` is an **order class** badge, not a sourcing route, and must never be styled as one — sourcing routes render per `[G-5]` (§6.6).

#### 3.9.3 Post-import behaviour

After a confirmed import the new rows appear **without a page reload** `[G-2]`, the header count increments by `{n}`, and the current filter/sort/pagination state is preserved ([E-45], [E-57]).

#### 3.9.4 Merge Orders and MKT rows

`⧉ Merge Orders` **must block** any selection that mixes an `MKT-` order with a regular sales order, with the message `Marketing orders cannot be merged with sales orders.` (BR-18, `[PD-59 · OWNER-PENDING]`, [E-37]). Merging two `MKT-` orders together, and merging two sales orders together, are unchanged behaviours.

---

### 3.10 `[L-5]` — Comments hub

The hub is the shared cross-screen pattern defined in `[G-7]`; only page deltas are specified here.

- **Trigger (byte-exact):** nav button `💬 Comments` with a red unread badge (`.badge-n`, demo value `3`), `[data-open="inbox1"]` → `#inbox1`. Clicking the trigger again closes the panel.
- **Panel:** 370 px dropdown anchored top-right of the nav (`top:44px; right:150px`).
- **Dismissal:** the panel closes on an outside click and on `Esc`. The wireframe implemented neither — although the guards written for outside-click dismissal were present as dead code — until [WF-21 · proposed] and [WF-20 · proposed] were applied 2026-08-03. It now closes on both: a `document`-level click handler closes `.inboxdd.open` unless the click landed inside `.inboxdd`, which makes those guards live, and the `Esc` handler closes the hub when no overlay is open ([E-97]).
- **Search row (byte-exact placeholder):** `🔍 Search all comments — order no. · author · text`. Typing hides the tab strip and renders a results pane; clearing restores the previously active tab. Result header (byte-exact): `{n} results · newest first · click to open the order`. Matches are wrapped in `<mark>` (purple, `font-weight:700`) and the query is escaped before rendering ([E-48]). Empty state (byte-exact): `No matching comments` ([E-38]).
- **Tabs (byte-exact):** `@ Mentions` (with an inline count badge, demo `3`) and `★ Saved`.
  - Mentions pane header: `Comments mentioning me · Click to open the order` with the right-aligned action `Mark all read`.
  - Saved pane header: `Saved comments · Click to open the order` with the right-aligned hint `Unstar to remove from the list` (`[G-7]` HUB-2 / HUB-3).
- **Cross-page string divergence (M3a D7) — resolved 2026-08-03.** The hub is byte-identical on all eight screens, and `[G-7]` v1.2 now publishes the strings as contract (HUB-1…HUB-7). On six of the seven this page already carried the majority text. It diverged on one — the Saved-pane hint, which read `Unstar to remove from list` here and on `inbound-request`, against `Unstar to remove from the list` (RTO, TM) and `Unstar to remove from this list` (INV, CL), with `Unstar to remove` on order-detail. Earlier revisions of this spec kept the local form because the wireframe is SST for UI copy (`_review` §3.9) and the corpus had **no** majority — a 3 / 2 / 2 / 1 split once `view-orders` is counted, which the first tally missed. `[G-7]` resolved it to the standard English form; this page's wireframe, §3.10 and QA-CMT-03 moved to `Unstar to remove from the list` in the same commit.
- **Rows:** `Order {no} · {author}: "{text}"` plus a `<time>` stamp, with a `★` star toggle. Unread rows carry `.unread` (blue tint `--blue-soft`). Demo dataset: `MKT-40233`, `MKT-40218`, `421771`, `MKT-40191`, `421502` — marketing and sales orders share one corpus.
- **Page delta — cross-entity corpus (BR-32).** `[G-7]` makes orders, inbound requests **and** unrecognized-pool items commentable, and the hub searches **all** comments. A row surfaced here may therefore reference an entity that does not live on this page; the click routes to that entity's own screen, and for an already-resolved pool item it opens the matched order instead `[PD-67 · OWNER-PENDING]` ([E-92]).
- **Click-through:** opens the referenced entity `[G-12]`. If a target order was cancelled after the comment was written, the click still opens it in its cancelled state ([E-49]).
- **Comment mutability:** this page exposes no edit and no delete affordance for a comment `[G-7]` `[PD-3 · OWNER-PENDING]` (BR-23).
- **`@mention` routing:** `#fulfillment-admin-comments` (`C0BMGEWM5QA`) — see §6.1.
- **This page does not compose comments.** Posting happens on the entity screens; the hub is a read/triage surface. `[DC-19]`/`[DC-20]` are listed in §5 because the badge and lists are views over them `[G-8]`, but the events this page *writes* are `[DC-21]`…`[DC-24]`.
- **Badge:** equals the unread mention count; `Mark all read` clears it to zero without a page reload ([E-39]). A count above 99 renders `99+` ([E-64]).
- **Persists:** `[DC-21] comment.starred` / `[DC-22] comment.unstarred` / `[DC-23] comment.read` / `[DC-24] comment.mark_all_read`. Search queries are a declared **NON-event** (§5.4).

---

### 3.11 `[L-F1]` — Legend closing paragraph (unchanged-furniture contract)

Byte-exact source text: `Global nav · filter bar (dates · Search · PIC · Status · Order#/Tracking# checkboxes · Country · page size) · Merge Orders · Export/Yun Export · 2,818 total · pagination all stay as in the live screen. Sample assignment was redesigned 2026-07-23 as a simple ON/OFF (no product-type selection) — see legend item 2.`

Normative reading: everything enumerated is an as-is contract against the live admin. This spec adds exactly four behaviours to that surface: the MKT row treatment (§3.9.2), the Merge Orders MKT guard (§3.9.4), the `Search PIC` behaviour for free-text PICs (§3.13), and the export-egress capture `[DC-26]`/`[DC-27]` (§3.13).

---

### 3.12 `[L-F2]` — Page header and order count

- Title (byte-exact): `Order Management Dashboard`. Count (byte-exact format): `{n,ddd} orders` (demo `2,818 orders`).
- The count reflects the **current filter set**, not the whole database, and updates in place after an import without a reload ([E-45]).
- When the filter set matches nothing the count reads `0 orders` and the list shows its empty state; `⬆ Import` and both sample buttons remain enabled ([E-100]).

---

### 3.13 `[L-F3]` — Filter bar (unchanged, with two deltas)

Controls left-to-right, byte-exact: start date (`2026-06-01`) · `~` · end date (`2026-07-14`) · separator · `Search (order / product)` · `Search PIC` · status select (`All Status` / `Processing` / `Prepare Shipment` / `Completed` / `On Hold`) · checkbox pair `Order #` (checked) and `Tracking #` · country select (`Country: AU` / `All` / `NZ` / `US`) · page-size select (`15` / `30` / `50`) · spacer · `▦ Columns` · `⬇ Export` · `⬇ Yun Export` · `⬆ Import` (`[L-1]`).

- The `Order #` / `Tracking #` checkboxes scope the `Search (order / product)` box; both may be on. Unchanged behaviour.
- **Delta 1:** `Search PIC` must match **both** system-user PICs and free-text PICs recorded by an import, as a case-insensitive substring (BR-4, [E-59]).
- **Delta 2:** `⬇ Export` and `⬇ Yun Export` are unchanged download actions over the current filter set. They are not confirming actions and show no toast, but they **are** persisted as data-egress events (`[DC-26]`, `[DC-27]`). An export that runs while a batch is committing reflects a consistent snapshot — the whole batch or none of it ([E-58]).
- The page loads with the live admin's default filter set and performs no mutating action on load (BR-34).
- Filter, pagination, page-size, sort and column-toggle changes are declared **NON-events** (§5.4).

---

### 3.14 `[L-F4]` — Action-row controls other than the sample pair

Byte-exact: checkbox `Select all` · selection counter `2 selected` (purple bold, `.sel-info`) · `⧉ Merge Orders` (outline blue) · then `[L-2a]` and `[L-2b]`.

- `Select all` applies to the **currently visible (filtered) rows only**; per-order selection persists across filter changes within the session. Selecting rows is a NON-event.
- The counter format is `{n} selected` and is the same `{n}` bound into `[L-M2]`'s second radio label (§3.6.1); the order set itself is re-resolved at submit (BR-33).
- `⧉ Merge Orders`: unchanged behaviour plus the MKT guard (§3.9.4). Persists `[DC-25] orders.merged`.

---

### 3.15 `[L-F5]` — Toast surface

- Element: `.gtoast`, fixed at `top:16px; right:16px`, `z-index:200`, green `--green` `#198754`, white bold 13.5 px, with an optional `<small>` subtext line at 11.5 px / 90 % opacity. `z-index:200` sits above `.overlay`'s `z-index:80`, so a toast is never clipped by an open modal ([E-95]).
- Colour semantics on this page follow `[G-2]` unchanged; the wireframe implements only the success case.
- Auto-dismiss (wireframe: 2 600 ms). Duration, stacking-vs-replacement, and exact failure copy are developer decisions (§9.3). The wireframe created two independent nodes (`#gtoast`, `#gtoast2`) that could overlap at the same fixed coordinates; the product must use a single slot or an explicit stack ([E-62]). [WF-18 · proposed] was applied 2026-08-03 and the wireframe now demonstrates the **explicit-stack** branch: three per-action nodes (`#gtoast` / `#gtoast2` / `#gtoast3`) repositioned by a shared `stackToasts()` from `top:16px` downward in `offsetHeight + 8 px` steps, so visible toasts never overlap. That is a demonstration of one permitted branch, not a narrowing of the §9.3 decision — single-slot replacement remains equally allowed.
- The `[G-2]` refresh exception named for RTO Bulk Outbound does not apply to any action on this page.

---

### 3.16 `[L-F6]` — Global navigation shell

Unchanged contract against the live admin; specified only so the shell is not re-designed and so `[L-5]`'s host is pinned.

- Byte-exact contents left-to-right: brand `SkinSeoul` · menus `Operation AI ▾`, `Catalog Management ▾`, `OMS Center ▾`, `Site Management ▾`, `System Management ▾`, `Customer Management ▾` · two-line quick links `Agent Telemetry`, `Role Assets`, `Shared Asset Health`, `SkinSeoul WP Admin` · spacer · `💬 Comments` with badge (`[L-5]`) · user chip (avatar initial `Y` + `Yongwon Ryu`) · `Logout`.
- Dark bar `--nav` `#1B1F24`, foreground `--nav-fg` `#C7CBD1`.
- No control in the nav is page-specific, and none is added by this spec.

---

## 4. Business Rules

Every rule carries its rationale and decision date. Reversals appear in §10. Rules resting on a provisional decision are tagged in the sentence where the behaviour appears.

| ID | Rule | Rationale | Decided |
|---|---|---|---|
| **BR-1** | **No stock validation on marketing import.** A row whose SKU has zero or negative stock, or which has never been inbounded, imports normally. MKT orders are visible in the RTO Marketing view regardless of stock or inbound status. | Marketing timing beats warehouse timing; seeding campaigns are committed before goods arrive. Blocking the campaign for a warehouse reason is the wrong trade. Notion §G's "error if the product is not in the warehouse" item is struck and must not be surfaced in UI copy. | 2026-07-23 (owner) |
| **BR-2** | **MKT visual separation.** Every `MKT-` order row carries a purple tint, an `MKT` badge, and a populated PIC column. | Settlement and volume separation from sales orders must be readable at a glance by an operator scanning a 2,818-row mixed list, not reachable only via a filter. | 2026-07-09 rework, reconfirmed 2026-08-03 |
| **BR-3** | **Carrier is auto-assigned per country at confirm time.** The operator never picks a carrier during import. | One country resolves to one connected carrier; making the operator choose introduces a per-row decision with no information advantage. | 2026-08-03 |
| **BR-4** | **PIC defaults to the logged-in user and accepts free text.** The select lists system users; `✎ Custom` accepts any string, which `Search PIC` matches as a substring. | The real PIC is sometimes an agency contact or a campaign owner with no admin account; forcing a system user would produce a false record. | 2026-08-03 |
| **BR-5** | **Order Type = `Influencer Seeding` preset plus free-text custom.** | New campaign shapes appear faster than an enum can be maintained (e.g. "Pop-up event giveaway"). | 2026-07-23 |
| **BR-6** | **Sample assignment is a simple ON/OFF with no sample-type selection.** No product picker may be added to `[L-M2]`. | The decision the operator is qualified to make is *whether* samples ship in this period, not *which* SKU the warehouse packs. Removing the choice removes an error class. | 2026-07-23 redesign, reconfirmed 2026-08-03 |
| **BR-7** | **Exactly one sample set per order**, even when overlapping periods match it. | Two sets on one order is a physical packing error and a settlement error; overlaps are explicitly allowed, so the dedup guard must live in the assignment logic. | 2026-08-03 |
| **BR-8** | **Dual view** `[G-13]`. Carrier-facing data appends only `(+ sample set)` to the last product name. Internal invoice and picking artifacts render **"sample set" only** in v1 — no type/qty breakdown (`[PD-51]` owner-decided 2026-08-03). That the internal picking artifact carries the line at all is `[PD-36]`, owner-decided 2026-08-04; Order Detail's display of it is `[PD-27 · OWNER-PENDING]`. | Tax handling on the carrier-facing document, versus a warehouse picker who physically cannot pick an unnamed sample. Label layout itself is Phase 3-1 (§9.2). | 2026-08-03 |
| **BR-9** | **Cancelling a period stops new assignments only.** Orders already assigned keep their sets. | Picking lists already printed must stay true; retroactively stripping a sample would make the paper and the parcel disagree. | 2026-07-23 (wireframe note), reconfirmed 2026-08-03 |
| **BR-10** | **Bulk Hold Shipment must not exist on this screen.** Hold is `Change Status → on-hold` on Order Detail. | A hold is a per-order exception decision; a list-level bulk hold applies it without the context it requires. | 2026-08-03 (review round) |
| **BR-11** | **The order list table is a no-change contract** against the live admin, including the `▦ Columns` toggle, sorting, and pagination. | Re-specifying an unchanged surface invites accidental redesign during implementation. | 2026-08-03 |
| **BR-12** | **Import is atomic and the file is the unit of intent.** Any row error blocks the whole file; a confirmed batch is all-or-nothing. `[PD-57 · OWNER-PENDING]` | A partial import leaves marketing unable to tell which rows landed, and there is no batch revert (BR-14) to recover with. | 2026-08-03 |
| **BR-13** | **Duplicate file warns, does not hard-block.** A matching file hash raises `Import anyway`. `[PD-58 · OWNER-PENDING]` | Re-uploading a corrected file under the same name is normal; a hard block would strand it. | 2026-08-03 |
| **BR-14** | **No batch revert in v1.** Cleanup is per order via `✕ Cancel Order` on Order Detail. `[PD-54 · OWNER-PENDING]` | Reverting a batch whose orders may already be picked is a larger feature than the wireframe encodes. | 2026-08-03 |
| **BR-15** | **Sample periods are not retroactive.** A backdated start does not assign sets to orders that already exist. `[PD-52 · OWNER-PENDING]` | Retroactive assignment would change orders already picked, printed, or shipped. | 2026-08-03 |
| **BR-16** | **Target `Selected orders only` assigns immediately;** its period is informational/audit metadata. `[PD-53 · OWNER-PENDING]` | The orders already exist, so a time window has nothing left to gate. | 2026-08-03 |
| **BR-17** | **Sample periods match sales orders only** — never `MKT-` marketing orders. `[PD-56 · OWNER-PENDING]` | Seeding and giveaway orders carry their own campaign contents; adding a sample set would distort settlement separation. | 2026-08-03 |
| **BR-18** | **`⧉ Merge Orders` may not combine an `MKT-` order with a sales order.** `[PD-59 · OWNER-PENDING]` | The purple/MKT split exists for settlement and volume separation; merging destroys it. | 2026-08-03 |
| **BR-19** | **Sample assignment binds at order-creation time and survives** the period ending or being cancelled. | The set is a fact about the order, not a live query against a period. | 2026-08-03 |
| **BR-20** | **REVERSED 2026-08-04 — an unconnected carrier blocks the entire file** `[G-17]`. No order is created from a file containing any unconnected destination; `Confirm Import` is disabled and the blocking banner names the countries and both remedies. The superseded rule read *"an unconnected carrier never blocks the batch; the order is created and carries a persistent `carrier_unresolved` flag"* — kept here struck rather than deleted so it does not silently return from a stale copy. | An order that exists asserts it can ship, and without a carrier it cannot. The original rationale (time pressure; one country must not stop eleven orders) is preserved differently: removing the rows or connecting the carrier takes ~30 seconds and re-upload is protected by file-hash idempotency, whereas partial import produced a **silently dropped recipient** and a half-created batch with no clean retry. | 2026-08-03, **reversed 2026-08-04** |
| **BR-21** | **One PIC per import batch.** There is no per-row PIC. | The batch is the accountability unit — warehouse and CS need one name to ping. | 2026-08-03 |
| **BR-22** | **This page adds no permission concept of its own.** No control here is role-gated, and every mutating action records the actor `[G-15]` `[PD-1 · OWNER-PENDING]` `[G-8]`. | Inventing per-page gates would produce eight inconsistent models. | 2026-08-03 |
| **BR-23** | **This page exposes no edit and no delete affordance for a comment** `[G-7]` `[PD-3 · OWNER-PENDING]`. | The comment corpus is a deliberate AI-training and audit asset; a mutation path opened on a triage surface would silently rewrite it. | 2026-08-03 |
| **BR-24** | **Slack delivery is a side effect.** The primary action always commits; a delivery failure is persisted and retried and never rolls anything back or blocks the UI. `[PD-4 · OWNER-PENDING]` | Notification is not part of the transaction. | 2026-08-03 |
| **BR-25** | **Cancelling assignment periods requires a confirm step and a toast** `[PD-5 · OWNER-PENDING]` `[G-2]`. | Cancelling a `forever` period switches off a company-wide campaign from a list of checkboxes; `_review` C-6 rules that wireframe omissions are gaps, not decisions. | 2026-08-03 |
| **BR-26** | **The server revalidates at confirm; mismatch → red toast + refreshed view; no partial writes.** `[PD-6 · OWNER-PENDING]` | A draft batch or a period list can go stale between preview and confirm. | 2026-08-03 |
| **BR-27** | **Concurrent edits use an optimistic version check** → `409` → reload the affected row plus a non-green toast. `[PD-7 · OWNER-PENDING]` | Last-write-wins would silently destroy another operator's work. | 2026-08-03 |
| **BR-28** | **No scan surface.** `[G-1]` and `[G-3]` have nothing on this page to attach to: no scan input, no focus-retention rule, no send sound, no TTS. | Desk screen with no outbound-class button and no scan entry point. `_review` C-5 defines the send sound by button class `[PD-2 · OWNER-PENDING]` — this page has none of that class. | 2026-08-03 |
| **BR-29** | **No print surface.** `[G-4]` has no Print button on this page. Print consequences of `[G-13]` land on the label/picking artifacts owned by other specs. | The import and sample flows produce no printable artifact here. | 2026-08-03 |
| **BR-30** | **Assignment periods are a permanent record.** Rows are never deleted; `Ended` and `Cancelled` rows remain listed as record-only. | `[G-8]`: the period list is a view over persisted events and is the audit answer to "why did this order get a sample". | 2026-08-03 |
| **BR-31** | **One operating timezone.** Every datetime entered, evaluated, displayed or reported on this page uses the admin's single configured operating timezone; storage is UTC; period matching evaluates the absolute instant, not the wall-clock string. No per-user timezone rendering in v1. | A sample period is a company-wide switch. If two operators in different timezones read different windows from the same row, the one-set invariant becomes untestable and a campaign silently starts at the wrong hour. **Spec-level default awaiting owner sign-off — see §9.1**; the zone value itself is configuration (§9.3). | 2026-08-03 (spec-level) |
| **BR-32** | **The Comments hub corpus is cross-entity.** Rows surfaced here may reference orders, inbound requests or unrecognized-pool items `[G-7]`; a click routes to that entity's own screen `[PD-67 · OWNER-PENDING]`. | `[G-7]` makes pool items a first-class commentable type and the hub searches all comments, so this page's hub cannot assume every row is an order. | 2026-08-03 |
| **BR-33** | **`Selected orders only` resolves its order set at submit time, not at modal-open time.** The open-time count is a label only. | The list stays interactive behind the modal in the live admin; assigning to a stale set would silently sample the wrong orders. **Spec-level default awaiting owner sign-off — see §9.1.** | 2026-08-03 (spec-level) |
| **BR-34** | **Loading the page mutates nothing.** The page opens with the live admin's default filter set and writes no event on load. | An audit trail whose first row is "someone opened a screen" is noise; `[G-8]` scopes capture to operator-initiated actions. **Spec-level default awaiting owner sign-off — see §9.1.** | 2026-08-03 (spec-level) |

---

## 5. Data Capture

Doctrine: `[G-8]`. Event names use the canonical lowercase `entity.action` form; the shared cross-page names (`comment.posted`, `comment.mention_notified`, `comment.starred`, `comment.unstarred`, `comment.read`, `comment.mark_all_read`, `comment.auto_posted`, `order.status_changed`, `order.outbounded`, `print.job_result`, `product.barcode_registered`) are byte-identical to `_global-rules` and `_review` §3.3. Every event carries actor and timestamp; the table names the additional payload.

**Declared name divergence on a shared *concept* (cross-page defect M3a D14).** `[DC-28] idempotency.duplicate_suppressed` is this page's name for "an idempotent repeat was suppressed". The same concept is named `idempotency.duplicate_rejected` on View Orders and RTO, `action.idempotency_suppressed` on Order Detail, `inbound_request.idempotent_replay_suppressed` on Inbound Request, and `unrecognized_item.match_duplicate_suppressed` on Tracking Missing. The concept is **not** in `_global-rules`' canonical list, so no name is binding yet and no page is in violation. This spec deliberately does **not** rename `[DC-28]` on its own — a unilateral rename moves the divergence instead of closing it. When the canonical name is published (a `_global-rules` / `_review` §3.3 amendment), `[DC-28]` adopts it and keeps its ID.

### 5.1 Import chain

| ID | Event | Actor | Entity | Old → New | Payload | UI |
|---|---|---|---|---|---|---|
| **DC-1** | `import.template_downloaded` | operator | template | — | template version | none (silent) |
| **DC-2** | `import.file_uploaded` | operator | draft batch | `null → uploaded` | filename, byte size, SHA-256 hash, parse outcome (`accepted` / `rejected_format` / `rejected_limit` / `rejected_template_version`) | inline error on rejection |
| **DC-3** | `import.file_parsed` | system (on behalf of actor) | draft batch | `uploaded → parsed` | row count `{n}`, error count `{e}`, per-row parse result (field values + error reason), per-row **advisory** carrier resolution, parser/template version | Preview header + table |
| **DC-4** | `import.duplicate_file_warned` | system | draft batch | — | matching confirmed batch id, its confirm timestamp, file hash | duplicate dialog |
| **DC-5** | `import.duplicate_file_overridden` | operator | draft batch | `warned → override_accepted` | prior batch id, reason `operator_override` | — |
| **DC-6** | `import.batch_confirmed` | operator | import batch | `draft → confirmed` | batch id, source filename + hash, order count `{n}`, order type (`preset / custom` + value), PIC (`user_ref / free_text` + value), carriers-assigned count, unresolved count, idempotency key | green toast |
| **DC-7** | `import.batch_rejected` | system | draft batch | `parsed → rejected` | reason (`stale_draft`, `ambiguous_carrier_mapping`, `server_error`, `validation_failed`, `session_expired`), field detail | red toast |
| **DC-8** | `import.batch_abandoned` | operator/system | draft batch | `parsed → abandoned` | reason (`user_closed`, `session_lost`), staged filename | none |
| **DC-9** | `order.created` ×n | operator (batch actor) | order | `null → MKT-#####` | recipient, contact, address, country, SKU, qty, product-name snapshot, campaign, order type, batch id, order class `marketing` | new list rows |
| **DC-10** | `order.carrier_assigned` ×n | system | order | `null → {carrier}` | country, mapping version, resolution timestamp | preview cell (green) |
| **DC-11** | **RETIRED 2026-08-04 — ID kept so the slot is not a hole and stale cross-references still resolve.** It was `order.carrier_unresolved` ×n, an order-scoped flag. `[G-17]` means no such order is created, so the event has no subject. **The attempt is still recorded**, one level up: `[DC-7] import.batch_rejected` gains `reason = no_connected_carrier` and the distinct country list, so "someone tried to ship to PE on this date" survives even though no order does. | — | — | — | — | Import-level only |
| **DC-12** | `order.pic_assigned` ×n | operator | order | `null → {pic}` | pic type (`user_ref / free_text`), value, batch id | PIC column |

**Declared gap — `[DC-9]` carries no monetary field.** The payload above is complete as specified, and it names no price, order value or currency. That is consistent with the input side: the import template's seven columns are fixed by the dev team and contain no such column either (§3.2.1), so an operator cannot supply one. What an imported `MKT-` order's amount field holds — if it has one at all — is **not decided anywhere in this spec, in `_global-rules`, or in the input documents**, and no default is invented here. Registered as the open question **`[OQ-1]`** in §9.1. Nothing on this page depends on the answer; the payload line is added to `[DC-9]` when the question is answered, and `[DC-9]` keeps its ID when that happens.

### 5.2 Sample-assignment chain

| ID | Event | Actor | Entity | Old → New | Payload | UI |
|---|---|---|---|---|---|---|
| **DC-13** | `sample.period_created` | operator | assignment period | `null → Scheduled / Active` | target type (`all_new_in_period` / `selected_orders` + order-id list + count), start datetime, end datetime or `forever = true`, operating timezone (BR-31), idempotency key | M3 row + toast |
| **DC-14** | `sample.assigned_to_order` ×a | system (attributed to the period's creator) | order | `sample_set = none → assigned` | period id, assignment timestamp, assignment reason (`period_match` / `explicit_selection`) | internal invoice / picking artifacts (other specs) |
| **DC-15** | `sample.assignment_deduped` ×s | system | order | — (no change) | order id, suppressed period id, winning period id | toast subtext count |
| **DC-16** | `sample.assignment_skipped_ineligible` ×m | system | order | — (no change) | order id, period id, reason (`marketing_order` (BR-17) / `order_cancelled` / `order_outbounded`) | toast subtext count |
| **DC-17** | `sample.period_cancelled` | operator | assignment period | `Scheduled / Active → Cancelled` | period id, target snapshot, cancel timestamp, confirm-dialog acknowledgement | M3 status + toast |
| **DC-18** | `sample.period_ended` | system (scheduler) | assignment period | `Active → Ended` | period id, end datetime reached | M3 status |
| **DC-29** | `sample.period_started` | system (scheduler) | assignment period | `Scheduled → Active` | period id, start datetime reached | M3 status |

**Asserted absence:** cancelling or ending a period emits **no** unassignment event. There is no `sample.unassigned` on this page and there must not be one (BR-9, BR-19). QA-SMP-14 asserts the absence.

### 5.3 Comments, list actions, and system events

| ID | Event | Actor | Entity | Old → New | Payload | UI |
|---|---|---|---|---|---|---|
| **DC-19** | `comment.posted` | operator | order / inbound request / pool item | `null → comment` | text, `@mentions[]` | hub rows — **originates off-page**; listed because the hub is a view over it `[G-8]` |
| **DC-20** | `comment.mention_notified` | system | comment | `queued → delivered / failed` | channel `#fulfillment-admin-comments` (`C0BMGEWM5QA`), Slack ts, mentioned user, delivery outcome, retry count | none — **originates off-page** |
| **DC-21** | `comment.starred` | operator | comment | `unstarred → starred` | comment id | `★` fills amber `--star` `#F59E0B` |
| **DC-22** | `comment.unstarred` | operator | comment | `starred → unstarred` | comment id | `★` returns to grey; row leaves the Saved tab |
| **DC-23** | `comment.read` | operator | comment | `unread → read` | comment id | `.unread` tint removed; badge decrements |
| **DC-24** | `comment.mark_all_read` | operator | comment set | `unread → read` ×k | comment ids, count `k` | badge clears to 0 |
| **DC-25** | `orders.merged` | operator | orders | source order ids → merged order id | source ids, merged id, guard outcome (BR-18) | list refresh |
| **DC-26** | `orders.exported` | operator | export | — | filter context (dates, search, status, country, page size, column set), row count, format | file download |
| **DC-27** | `orders.yun_exported` | operator | export | — | as `DC-26` plus export profile `yun` | file download |
| **DC-28** | `idempotency.duplicate_suppressed` | system | any confirming action | — | action name (`import.batch_confirmed` / `sample.period_created` / `sample.period_cancelled`), idempotency key, original result reference | none (the original toast is re-shown — developer decision) |

**Events explicitly NOT emitted by this page** (named so their absence is intentional, not an omission): `order.status_changed` (Hold moved to Order Detail — BR-10), `order.outbounded` (no outbound control here), `print.job_result` (no print surface — BR-29), `product.barcode_registered` (no scan surface — BR-28), `comment.auto_posted` (this page generates no system comments; the hub may *display* them from other screens).

**Cross-page events this page causes but does not own:** RTO Marketing-view visibility of `MKT-` orders is a read of `[DC-9]`; the sample dual-view on internal invoice/picking artifacts is a read of `[DC-14]`.

### 5.4 Declared NON-events

Per `[G-8]`, ephemeral client-local state is explicitly not persisted. Anything not listed here and operator-initiated **must** persist.

1. Opening or closing any modal (`[L-1]`, `[L-2a]`, `[L-2b]`, `✕`, `Cancel`, `Close`, `Esc`, overlay-backdrop click).
2. Order Type chip toggling and typing into `#otCustom` before confirm.
3. PIC `✎ Custom` toggling and typing into `#picCustomIn` before confirm.
4. Filter-bar changes: dates, `Search`, `Search PIC`, status, `Order #` / `Tracking #` checkboxes, country, page size.
5. `▦ Columns` toggle and column-set changes.
6. Pagination and sorting.
7. Row selection, `Select all`, and the `{n} selected` counter.
8. Comments-hub open/close, tab switching, and search queries (including zero-hit queries).
9. Radio and checkbox state inside `[L-M2]` before `Start Assignment (ON)` is pressed.
10. Checkbox state inside `[L-M3]` before `Cancel Selected Periods` is pressed.
11. Toast rendering and dismissal (the underlying event is already persisted).
12. Loading the page and its initial data fetch (BR-34).

### 5.5 Retention and export

| Class | Retention | Export |
|---|---|---|
| Import batch records (`DC-1`…`DC-8`) and the orders they created (`DC-9`…`DC-12`) | Indefinite — the audit answer to "where did this order come from" | Exportable with the order dataset |
| Uploaded source `.xlsx` files | Retained and linked to the batch id so a disputed import can be re-read against the original file. Exact horizon and storage location are developer decisions (§9.3) | Downloadable from the batch record |
| Assignment periods and per-order assignment events (`DC-13`…`DC-18`, `DC-29`) | Indefinite. Rows are never deleted from the M3 list (BR-30) | Exportable |
| Comment corpus (`DC-19`…`DC-24`) | Indefinite — declared an AI-training and audit asset `[G-7]` | Exportable |
| Export/egress records (`DC-26`, `DC-27`) | Indefinite — data-egress audit | — |
| Idempotency suppressions (`DC-28`) | At least as long as the idempotency key TTL; TTL is a developer decision | — |

All events are queryable by actor, by entity (order no. / batch id / period id), and by time range.

---

## 6. Integrations

### 6.1 Slack routing table

Exactly **one** confirmed route fires from this page.

| Trigger | Channel | Payload fields | Mention target |
|---|---|---|---|
| Comment `@mention` on any entity surfaced through this page's Comments hub `[L-5]` `[G-7]` | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) | entity no. (order no. incl. `MKT-`, inbound no., or pool item ref), comment text, time, author, @mentioned user, deep link to the entity | per `[G-7]` |

- Confirmed by the owner on 2026-08-03 (`_slack-routing`); any earlier "channel pending" wording is superseded (`_review` C-2).
- Delivery failures are retried and persisted as `[DC-20]` with the failure outcome; they never block the comment or roll it back (BR-24, `[PD-4 · OWNER-PENDING]`). Retry policy is a developer decision.
- A **free-text PIC** resolves to no Slack user and therefore cannot be `@mention`-notified ([E-59]).
- If the channel is archived or renamed at dispatch time, the comment still commits and the dispatch is persisted as failed ([E-50]).

### 6.2 Routes that deliberately do NOT exist on this page

Naming them closes the audit rather than leaving silence:

- **Import confirmed** → no Slack route. Not invented here; `_slack-routing` classifies further routes as "decide per feature at dev time".
- **File rejected for an unconnected carrier `[G-17]`** → no automated Slack route; the importer sees the rejection on screen and contacts the Fulfillment Center directly. (Supersedes the 2026-08-03 `[PD-55]` answer, which assumed a flagged order existed to unblock.)
- **Sample period created / cancelled** → no Slack route in v1.
- **#unrecognized-tracking**, **#wholesale-ops**, **#partnership-kr** → these three confirmed routes belong to other screens and never fire from Order Management. (`_slack-routing` defines a channel ID only for the comments channel; the other three are named without IDs there.)

### 6.3 Cross-page links and deep links `[G-12]`

| From | To | Form |
|---|---|---|
| Comments-hub row click (order) | Order Detail for that order | `../order-detail/#{orderNo}` (production: deep-links to the specific order) |
| Comments-hub row click (inbound request) | Inbound Request list, focused on that request | `../inbound-request/#reqlist` (production: the specific Inbound No.) |
| Comments-hub row click (unrecognized-pool item) | Unrecognized Tracking, focused on that pool row; if already resolved, the matched order instead `[PD-67 · OWNER-PENDING]` | `../tracking-missing/` |
| Confirmed import | Ready to be Outbonded, Marketing view | `../ready-to-outbound/#marketing` — MKT orders are listed there immediately, regardless of stock (BR-1) |
| MKT order number in the list | Order Detail | `../order-detail/#{orderNo}` |
| `[L-3]` Hold pointer | Order Detail → `Change Status` → `on-hold` | documentation pointer only; no control on this page |

**Path form (cross-page defect M3a D16).** Every row above uses the **directory form** `../{slug}/#anchor` — never `../{slug}/index.html#anchor`. This is the form the live wireframe URLs use and the form `[G-12]` itself writes, and it is the normalisation M3a recommends for the whole corpus; this page is already conformant and must stay so. QA assertions on an `href` therefore assert the directory form.

The wireframe implements none of these as `href`s (the order table is omitted and the hub rows are inert). In production they must be real links, not decoration `[G-12]`.

### 6.4 Sheet / file handoffs

| Artifact | Direction | Notes |
|---|---|---|
| Marketing import template `.xlsx` | out (download) | Produced and versioned by the dev team. Columns: Recipient · Contact · Address · Country · SKU · Qty · Campaign name |
| Completed template `.xlsx` | in (upload) | Retained and linked to the batch (§5.5) |
| `⬇ Export` | out | Order dataset over the current filter set; encoding and column set are developer decisions |
| `⬇ Yun Export` | out | Carrier-profile export for YunExpress; unchanged contract |
| **Procurement Hub sheet** | — | **Out of scope.** Excluded from this planning round entirely on 2026-08-02 (owner). No pull, no push, no reference |
| Daily Shipping Status sheet | — | Belongs to the `closing` spec; not touched here |

### 6.5 Print pipeline `[G-4]`

**This page has no print surface.** There is no Print button, no auto-print, and no `print.job_result` event (BR-29). The instant carrier-agnostic print requirement lands on View Orders, Ready-to-Outbound, and Order Detail. The one print-adjacent decision made *here* is the sample dual-view (BR-8, `[G-13]`): the carrier-facing document receives only the appended `(+ sample set)` string, while internal invoice and picking artifacts print a single **"sample set"** line — v1: "sample set" only, no type/qty breakdown (`[PD-51]` owner-decided 2026-08-03; the picking-list line's existence is `[PD-36]`, owner-decided 2026-08-04). The divergence between the two views is [E-34], and because this page is `[G-13]`'s primary home (§6.6) the check is owned here and asserted by QA-SMP-46 as a cross-reference against the consuming specs (`order-detail` display, `ready-to-outbound` picking list). Label and invoice layouts are Phase 3-1 and are not specified in this document (§9.2).

### 6.6 Global-rule applicability grid (closes the mandatory-inclusion audit)

| Rule | Applies here? | Where / why not |
|---|---|---|
| `[G-1]` Scanner protocol | **No** | No scan surface — desk screen (BR-28) |
| `[G-2]` No refresh + confirmation toast | **Yes** | §3.2.5, §3.6.5, §3.7.5, `[L-F5]` |
| `[G-3]` Audio feedback | **No** | No outbound-class button and no scan warning (BR-28, `_review` C-5, `[PD-2 · OWNER-PENDING]`) |
| `[G-4]` Instant print | **No** | No Print button (BR-29); dual-view consequences only |
| `[G-5]` Sourcing routes | Cross-ref | Route badges render inside the unchanged order table (`[L-4]`); `MKT` is an order **class** badge, not a sourcing route, and must not be styled as one. The `OTHER (channel)` rendering added program-wide `[PD-80 · OWNER-PENDING]` reaches this page only through that table. JIT has no surface here at all — see §6.7 item 11 |
| `[G-6]` Product naming | **Yes** | M1 preview renders brand-bold English names; no Korean strings exist on this page (§2.2) |
| `[G-7]` Comments | **Yes** | `[L-5]`, BR-32, §6.1 |
| `[G-8]` Data capture | **Yes** | §5 |
| `[G-9]` Idempotency | **Yes** | `Confirm Import`, `Start Assignment (ON)`, `Cancel Selected Periods` |
| `[G-10]` Multi-tracking | **No** | No tracking-number entry on this page |
| `[G-11]` Inbound-request lifecycle | **No** | No inbound entity here |
| `[G-12]` Deep links | **Yes** | §6.3 |
| `[G-13]` Sample assignment | **Yes — primary home** | `[L-2a]`/`[L-2b]`/`[L-M2]`/`[L-M3]`, BR-6…BR-9, BR-15…BR-19 |
| `[G-14]` Location scheme | **No** | No location concept on this page |
| `[G-15]` Permissions | **Yes** | BR-22 |

### 6.7 Mandatory-inclusion items with no `[G-n]` anchor — explicit N/A, never silent

`_review` §2b's 12-item mandatory matrix carries three items that are not expressible as a `[G-n]` rule, so §6.6's grid cannot close them. They are stated here explicitly, because an unstated N/A is a hole, not a pass (audit finding M3b §2.2, which names this page for item 11).

| Mandatory item | Applies here? | Statement |
|---|---|---|
| 9 · Line-based location filter | **No** | This page has no line-item view and no location concept. Filtering is by order (§3.13), never by line and never by location. Owned by `stock-status` and `view-orders` `[G-14]` |
| 10 · Audit-mode-only visibility | **No** | There is no audit mode on this page and no control whose visibility depends on one. Owned by `stock-status` |
| 11 · **JIT residual stock** | **No** | **JIT** appears nowhere on this screen. No JIT sourcing route is selectable here, no residual-stock figure is computed, displayed, filtered, exported or reported here, and none may be added. JIT is not a requestable inbound route `[G-5]`, and residual-stock handling is owned by the `stock-status` spec. The only route rendering this page sees at all is inside the unchanged order table (§6.6, `[G-5]` row) |

---

## 7. Edge Cases & Error States

IDs are page-scoped and stable, and are never renumbered. **E-1…E-45** preserve the identifiers assigned during planning (`order-management.B` §3a) with their original meanings. **E-46…E-66** were added in spec v1.0. **E-67…E-100** were added in this audit pass (v1.1). Every ID appears exactly once.

### 7.1 Import — file, parse and validation

| ID | Condition | Expected behaviour |
|---|---|---|
| **E-1** | Non-`.xlsx` upload (`.csv`, `.xls`, or a renamed file that fails XLSX parsing) | Rejected inline: `Unsupported file — upload the .xlsx template.` No rows parsed, no preview, Confirm stays disabled. `[DC-2]` persists with parse outcome `rejected_format` |
| **E-2** | Valid `.xlsx` with 0 data rows | Preview header renders `… · 0 rows parsed · 0 errors`; Confirm disabled (gate 3, §3.2.5) |
| **E-3** | A row missing any required field (Recipient / Contact / Address / Country / SKU / Qty / Campaign) | Row flagged with its reason; counted in `{e}`; whole file blocked (BR-12) |
| **E-4** | Unknown SKU (not in catalog) | Row error `Unknown SKU`; counted in `{e}`; whole file blocked `[PD-57 · OWNER-PENDING]` |
| **E-5** | Qty `0`, negative, non-numeric, or above the configured maximum | Row error; file blocked. The maximum-qty threshold is a developer decision |
| **E-6** | Invalid or unsupported country code | Row error `Invalid country`; file blocked. Distinct from E-7 |
| **E-7** | Country valid but no connected carrier | **Blocking error `[G-17]`.** Red cell `Cannot import — no connected carrier`; the blocking banner names the countries; `Confirm Import` is **disabled**; **no order is created from the file**. Persists `[DC-7] import.batch_rejected` with `reason = no_connected_carrier` and the country list (BR-20 as reversed 2026-08-04). *(Through 2026-08-03 this row read "Not an error" — see BR-20 for the reversal.)* |
| **E-8** | **Every** row unconnected | Same as E-7 — the whole file is rejected and no order is created `[G-17]`. The banner lists every distinct country. *(Through 2026-08-03 this row read "Import still confirmable" — see BR-20 for the reversal.)* |
| **E-9** | Duplicate rows within one file (same recipient + SKU) | Allowed — marketing legitimately sends multiples. Whether a warning is shown is a developer decision |
| **E-10** | Re-upload of an already-confirmed file (matching hash) | Duplicate dialog `This file was already imported` → `Cancel` / `Import anyway` `[PD-58 · OWNER-PENDING]`. `[DC-4]`, and `[DC-5]` on override |
| **E-11** | Double-click on `Confirm Import` | Exactly one batch `[G-9]`; the second submission is suppressed and recorded `[DC-28]` |
| **E-12** | Network failure mid-confirm | Atomic: either the full batch exists or none does. Retry with the same idempotency key is safe. Red toast on the failed attempt; `[DC-7]` |
| **E-13** | Modal closed (`✕` / `Cancel` / `Esc` / backdrop) after upload, before confirm | Nothing created; staged draft discarded; `[DC-8]` reason `user_closed` |
| **E-14** | `✎ Custom` order-type chip active with an empty input | Confirm disabled; inline `Enter an order type.` |
| **E-15** | PIC custom input visible but empty or whitespace-only | Confirm disabled; inline `Enter a PIC name.` |
| **E-16** | File exceeds the row or byte limit | Rejected with an explicit message naming the limit; `[DC-2]` outcome `rejected_limit`. Limit values are developer decisions |
| **E-17** | Template schema mismatch (renamed, reordered, or extra columns) | Header-name matching; extra columns ignored; a missing required header rejects the file. Exact policy is a developer decision |
| **E-18** | Mixed-country file | Per-row assignment (demo: `GB → YunExpress`, `PE → Not connected`) |
| **E-19** | Preview shows `{e} > 0` | Confirm disabled until a clean re-upload; the whole file is blocked (BR-12) |
| **E-20** | SKU with zero stock or never inbounded | **Must NOT be an error.** Rows import and appear in the RTO Marketing view (BR-1). Regression guard against the struck Notion §G stock check |
| **E-67** | Country supplied as a full name (`United Kingdom`) rather than ISO-2 | Normalised to ISO-2 where the name resolves unambiguously; an unresolvable value is a row error `Invalid country` (E-6). The normalisation table is a developer decision |
| **E-68** | Leading/trailing whitespace, non-breaking spaces, or zero-width characters in any field | Trimmed before validation; a value that is only whitespace is treated as missing (E-3) |
| **E-69** | Qty written as `1.5`, `1,000`, or `'2` (text-formatted) | Thousands separators and a leading apostrophe are stripped; a non-integer result is a row error (E-5). Qty is always a positive integer |
| **E-70** | Workbook with several worksheets, merged cells, or formula cells | Only the first worksheet is read; formulas are read as cached values; merged cells that break the header row reject the file with an explicit reason |
| **E-71** | File built from an outdated template version | Rejected with a message naming the required version and pointing back at `⬇ Download Template (.xlsx)`; no partial parse. `[DC-2]` outcome `rejected_template_version` |
| **E-72** | File carries an extra `Product Name` (or `Order No`) column that disagrees with the SKU lookup | The system-resolved value wins; the file's value is ignored and recorded on the parse result. Order numbers are never taken from the file (E-51) |
| **E-73** | SKU exists but is discontinued or unpublished | **Not an error.** The row imports and the product-name snapshot is taken at creation; catalogue status never gates an import (same doctrine as BR-1) |
| **E-74** | Session expires (401) between upload and confirm | Confirm fails with a red toast; nothing is created; `[DC-7]` reason `session_expired`. The staged draft survives re-authentication for its TTL, after which `[DC-8]` reason `session_lost` is written |

### 7.2 Import — batch, carrier and identity

| ID | Condition | Expected behaviour |
|---|---|---|
| **E-41** | Two operators import simultaneously | Distinct batches, no `MKT-` id collision. The numbering source must be a central collision-safe sequence |
| **E-51** | Import file contains an extra column attempting to set order numbers | Ignored — order numbers are minted by the system only |
| **E-52** | A country maps to more than one connected carrier | Configuration error: confirm fails with a red toast naming the country; **no** orders created (atomicity). `[DC-7]` reason `ambiguous_carrier_mapping` |
| **E-55** | Browser/tab closed mid-upload | Staged draft orphaned and reaped; `[DC-8]` reason `session_lost`; nothing created |
| **E-58** | `⬇ Export` runs while a batch is committing | The export reflects a consistent snapshot — it either includes the whole batch or none of it |
| **E-59** | Free-text PIC equal to an existing system user's display name | Stored as free text, not silently resolved to the user. It matches `Search PIC` but cannot be `@mention`-notified. Disambiguation policy is a developer decision |
| **E-63** | All rows removed by validation, leaving 0 eligible orders | Confirm disabled (gate 3); no empty batch is ever created |
| **E-65** | Carrier mapping changes between preview and confirm | Confirm-time resolution wins; toast subtext reports confirm-time counts; the preview's advisory value is superseded (§3.3) |
| **E-75** | The server commits the batch but the response is lost (client timeout) and the operator retries | The retry carries the same idempotency key and returns the committed batch. Exactly `{n}` orders exist; `[DC-28]` records the suppressed repeat; no second batch and no second toast text variant |
| **E-76** | The same operator confirms a second import from another browser tab while this modal is open | Both batches commit independently, each under its own idempotency key; neither draft contaminates the other; both appear in the list |
| **E-77** | Browser Back immediately after a confirmed import | Returns to the dashboard. The batch is **not** undone — there is no revert path (BR-14, `[PD-54 · OWNER-PENDING]`); cleanup is per order on Order Detail |
| **E-78** | Recipient or Address longer than the destination carrier's field limit | The import succeeds. Carrier-side truncation or rejection is a downstream concern and must never block order creation |
| **E-79** | Contact number without a country dialling code, or in a format the carrier will later reject | Not validated at import; the value is stored verbatim. Carrier-format validation belongs to the label/export pipeline |
| **E-80** | Country mapping exists but the carrier connection is disabled at confirm time | Treated exactly as unconnected: amber cell, order created, `[DC-11]` with reason `connection_disabled` |
| **E-81** | Two rows in one file resolve to different carriers | Both assigned per row; there is no batch-level carrier and no attempt to reconcile them |

### 7.3 Sample assignment

| ID | Condition | Expected behaviour |
|---|---|---|
| **E-21** | `[L-M2]` opened with 0 orders selected | `Selected orders only (0)` radio disabled; `All new orders in this period` remains selectable |
| **E-22** | End datetime earlier than start datetime | `Start Assignment (ON)` disabled; inline `End must be later than start.` |
| **E-23** | `forever` checked while end fields hold values | `forever` wins; end fields cleared and disabled. The wireframe left them enabled until [WF-19 · proposed] was applied 2026-08-03; it now clears and disables both. Exact mechanic is a developer decision |
| **E-24** | Two overlapping Active periods both match a new order | Exactly **one** sample set (BR-7). The suppressed match persists as `[DC-15]`. Which period is recorded as the assigner is a developer decision (first match by start datetime recommended) |
| **E-25** | Backdated start datetime | **Not retroactive** — only orders created after the ON action, inside the window, receive a set (BR-15) |
| **E-26** | Period ends while an assigned order is still unshipped | The order keeps its sample set (BR-19); assignment binds at creation time, not at outbound |
| **E-27** | `Ended` (or `Cancelled`) period row | **No checkbox element at all**; cannot be selected or cancelled; record only |
| **E-28** | `Cancel Selected Periods` clicked with 0 rows checked | Button is disabled, so no action occurs. (The wireframe fired regardless until [WF-17 · proposed] was applied 2026-08-03; it now disables the button at zero selection) |
| **E-29** | Double-click on `Cancel Selected Periods` | Single cancellation per period `[G-9]`; the repeat is recorded `[DC-28]` |
| **E-30** | Cancelling an Active period | New matching stops immediately; already-assigned orders keep their sets; **no** unassignment event is emitted (BR-9, BR-19) |
| **E-31** | An order is cancelled or refunded after a sample was assigned | The assignment record persists on the order; sample handling on internal documents follows the order's lifecycle. No `sample.unassigned` event |
| **E-32** | Two operators create overlapping ON periods concurrently | Both periods persist; the exactly-one-set invariant (E-24) still holds for every matched order |
| **E-33** | `Selected orders only` where a selected order already holds a set | Skipped, not double-assigned; counted in the toast subtext as `{s} skipped (already assigned)`; `[DC-15]` |
| **E-34** | Dual-view divergence check | Carrier-facing data shows only `(+ sample set)` appended to the **last** product name; internal invoice and picking artifacts show a **"sample set"** line (v1: no type/qty breakdown, `[PD-51]` owner-decided 2026-08-03) `[G-13]` `[PD-36]` (owner-decided 2026-08-04). Verified on the consuming specs (cross-reference) |
| **E-35** | An active period would match an `MKT-` marketing order | **Not matched** — sales orders only (BR-17). Counted as `{m} skipped (not eligible)`; `[DC-16]` reason `marketing_order` |
| **E-44** | Network failure mid `Start Assignment (ON)` | No partial or ghost period; retry with the same idempotency key is safe |
| **E-46** | A new period is created with parameters identical to an existing Active period | Allowed — overlaps are explicitly permitted. Both periods exist; the exactly-one-set invariant still holds |
| **E-47** | A selected period was already cancelled by another operator | Optimistic version check → the row is reported as already cancelled, skipped, and the list reloads; the remaining selections still process `[PD-7 · OWNER-PENDING]` |
| **E-53** | Start datetime far in the future | Period is created with status `Scheduled`; it is cancellable before it starts; `[DC-29]` fires when it starts |
| **E-54** | `forever` unchecked with both end fields empty | `Start Assignment (ON)` disabled; inline `Enter an end date and time, or choose forever.` |
| **E-56** | Import runs while a period is Active | Imported `MKT-` orders receive **no** sample set (BR-17) |
| **E-60** | A period's end datetime passes while `[L-M3]` is open | Row flips `Active → Ended` on refresh and loses its checkbox; if it was checked the selection is dropped and the confirm dialog reports the adjusted count |
| **E-61** | Order created exactly at a period boundary | Start is **inclusive**, end is **exclusive**: an order created at exactly `start` receives a set; one created at exactly `end` does not |
| **E-66** | A period is cancelled in the same second an order is being created | The server resolves against the period's cancellation timestamp; an order whose creation timestamp precedes the cancellation receives its set, and both facts persist |
| **E-82** | `forever` unchecked with end datetime **equal** to start datetime | Blocked — the comparison is strictly later, so a zero-length period cannot be created (boundary partner of E-22) |
| **E-83** | Both start and end datetimes already in the past | Blocked with `A period that has already ended cannot be created.` No already-`Ended` period may be minted |
| **E-84** | The list selection changes (or empties) between opening `[L-M2]` and pressing `Start Assignment (ON)` | The set is re-resolved at submit (BR-33). The toast reports the number actually assigned. If the resolved set is empty the submit is blocked with `No eligible orders are selected.` and nothing is created |
| **E-85** | A selected order is cancelled between selection and submit | Skipped as ineligible; `[DC-16]` reason `order_cancelled`; counted in `{m} skipped (not eligible)` |
| **E-86** | A selection larger than the configured batch ceiling | Processed asynchronously; the toast reports the queued count and the assignment events land as the batch drains. The ceiling value is a developer decision |
| **E-87** | Cancelling a `Scheduled` period that never started | Allowed; status → `Cancelled`; no `[DC-14]` ever existed for it and none is created |
| **E-88** | Two operators press `Start Assignment (ON)` with identical parameters at the same moment | Two distinct periods exist (E-46). Neither submission is silently merged into the other, and the one-set invariant still holds for every matched order |
| **E-89** | Two operators in different local timezones read the same period row | Both see the same wall-clock string, rendered in the admin's single operating timezone (BR-31). No per-user timezone conversion happens |
| **E-90** | A daylight-saving or clock change falls inside a period | Matching evaluates the absolute instant, not the wall-clock string; no order is double-counted or skipped at the transition |
| **E-91** | A sales order is created by an integration or an API client, not by the admin UI, during an Active period | Still matched and assigned — matching is a server-side rule attached to order creation, not a UI behaviour |

### 7.4 List, comments and global

| ID | Condition | Expected behaviour |
|---|---|---|
| **E-36** | MKT row rendering | Purple tint `#F3EEFF`, `MKT` badge, populated PIC, distinct hover `#EBE1FF`; regular sales rows unaffected |
| **E-37** | `⧉ Merge Orders` with a mixed `MKT-` + sales selection | **Blocked** with `Marketing orders cannot be merged with sales orders.` (BR-18) |
| **E-38** | Comments search with no hits | Empty state `No matching comments`; tabs stay hidden until the query is cleared |
| **E-39** | `Mark all read` | Every unread row loses its `.unread` tint and the nav badge clears to 0, with no page reload; `[DC-24]` |
| **E-40** | Slack delivery failure on an `@mention` | The comment persists; delivery is retried and its failure recorded `[DC-20]`; posting is never blocked (BR-24) |
| **E-42** | A user without write access on this page (post-v1 concern) | v1 adds no gating here `[G-15]` `[PD-1 · OWNER-PENDING]`. A future RBAC surface (hide vs disable) is a developer decision (§9.3) |
| **E-43** | Toast contract | The page's confirming actions follow `[G-2]` unchanged; the surface is `[L-F5]` and no action on this page reloads the page |
| **E-45** | Immediately after a confirmed import | Header count increments by `{n}` (demo `2,818 orders` → `2,830 orders`) and the new MKT rows appear without a page reload |
| **E-48** | Comments search with regex-like or special characters (`"`, `<`, `&`, `%`) | Treated as a literal substring; input escaped before rendering and before highlighting; no markup injection |
| **E-49** | Comments-hub click-through to an order cancelled after the comment was written | Opens the order in its cancelled state; the comment history is intact (append-only, BR-23) |
| **E-50** | Slack channel archived or renamed at dispatch time | The comment commits; dispatch persists as failed with the channel id; retry policy is a developer decision |
| **E-57** | Filter and pagination state after an import | Preserved — the operator's current view is not reset `[G-2]` |
| **E-62** | Two confirming actions in quick succession (import confirm, then period cancel) | A single toast slot replaces, or an explicit stack renders both. The wireframe's overlapping independent nodes ([WF-18 · proposed], applied 2026-08-03) must not be reproduced — the drawing now stacks them explicitly via `stackToasts()`. Policy is a developer decision |
| **E-64** | Unread mention count above 99 | Badge renders `99+` |
| **E-92** | A hub row whose entity is an inbound request or an unrecognized-pool item | Routed to that entity's own screen; a resolved pool item opens the matched order instead `[PD-67 · OWNER-PENDING]` (BR-32). The hub never renders a dead row |
| **E-93** | A system user is created whose display name equals an existing free-text PIC string | Existing orders keep the free-text PIC; no retroactive resolution and no silent re-linking (E-59) |
| **E-94** | Two browser tabs of this page are open and one confirms an import | The other tab's list is stale until its next fetch. No cross-tab push is required in v1; a stale tab must never write from its stale state (BR-26 revalidation catches it) |
| **E-95** | A toast fires while a modal is open | The toast renders above the overlay (`z-index:200` vs `80`) and is not clipped |
| **E-96** | Viewport narrower than the layout minimum (mock 1240 px, table 1180 px) | The page scrolls horizontally. No responsive collapse is specified for v1 and none may be invented |
| **E-97** | `Esc` pressed while a modal or the Comments hub is open | Dismisses it as a non-confirming close; nothing is created. The wireframe implemented no `Esc` handling until [WF-20 · proposed] / [WF-21 · proposed] were applied 2026-08-03; it now closes the topmost open overlay, or the Comments hub when no overlay is open |
| **E-98** | Keyboard-only operation of a modal | Opening moves focus into the modal, focus is trapped while it is open, and closing returns focus to the trigger. Exact implementation is a developer decision |
| **E-99** | Session expires while the Comments hub is open | The hub renders an unauthenticated state and prompts re-authentication rather than showing an empty list and a zero badge — a silent zero would read as "no mentions" |
| **E-100** | The default filter matches no orders | The list shows its empty state, the count reads `0 orders`, and `⬆ Import`, `Sample Assignment ON` and `Cancel Sample Assignment` all stay enabled |

---

## 8. QA Acceptance Criteria

### 8.0 How to run this section

**Target for `[WF]`:** `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/order-management/`, loaded fresh, annotations **shown** (the default; `#annoToggle` reads `Hide annotations`). Every `[WF]` scenario below is executable against that page today with the selectors and strings given, without asking a question.

**Tags.** **[WF]** = runnable now on the live wireframe. **[ADMIN]** = real-admin only — persistence, concurrency, atomicity, Slack, scheduling, RBAC, or a wireframe demo limitation that makes the assertion impossible in the mock.

**Standing harness rules for `[WF]` scenarios:**

1. **Reload detection.** Before the first action of a scenario, set `window.__qaSentinel = 'om'`. "The page did not reload" means `window.__qaSentinel === 'om'` still holds after the action. Do **not** use navigation-entry counts — a reload destroys the script context and the count would be re-created.
2. **Toast identity.** The wireframe injects three separate nodes, one per confirming action: `#gtoast` (created by `#mktConfirm`), `#gtoast2` (created by `#sampConfirmGo`, the confirm-dialog button behind `#sampCancelBtn`) and `#gtoast3` (created by `#sampStartBtn`). `#gtoast3` and the `#sampConfirmGo` indirection arrived with the 2026-08-03 wireframe-edit pass ([WF-16 · proposed], [WF-17 · proposed]); through v1.2 this rule named only the first two. Assert the node named in the scenario. "A toast is visible" means the node exists and `getComputedStyle(node).display !== 'none'`; it is hidden again ~2 600 ms after the click, so assert within that window. Nodes are created lazily on first use, so `document.querySelectorAll('.gtoast')` counts only actions that have already fired. A shared `stackToasts()` places the first visible toast at `top:16px` and each subsequent one `offsetHeight + 8 px` below it ([WF-18 · proposed]), so a `top` assertion is only stable for the **first** visible toast.
3. **Colour assertions** use `getComputedStyle(...).color` / `.backgroundColor` in `rgb()` form. Reference values on this page: green `--green` `#198754` = `rgb(25, 135, 84)` · amber `--amber` `#B45309` = `rgb(180, 83, 9)` · purple `--mkt` `#7C3AED` = `rgb(124, 58, 237)` · star `--star` `#F59E0B` = `rgb(245, 158, 11)`.
4. **Modal state.** "Modal X is open" means `document.getElementById(X).classList.contains('open')`. Close a modal between scenarios by clicking its `[data-close]` control, or by pressing `Esc`, which closes the **topmost** open overlay — through v1.2 this rule said the wireframe does not respond to `Esc`, which stopped being true when [WF-20 · proposed] was applied 2026-08-03. There are now **four** overlays: `#m-import`, `#m-sampleon`, `#m-sampleoff` and the confirm overlay `#m-sampcancel-confirm` added by [WF-17 · proposed]. Because `Esc` unwinds one layer at a time, a scenario that opens the confirm overlay on top of `#m-sampleoff` needs two `Esc` presses, or a `[data-close]` click per layer, to return to a clean state.
5. **Text assertions are byte-exact**, including `·` (U+00B7), `—` (U+2014), `→` (U+2192), `✓`, `⬆`, `⬇`, `⧉`, `▦`, `✎`, `★`, `💬`, `📄`, `⋯`, and the preserved misspelling `Outbonded`. Byte-exactness is applied to the node's text **after** exactly three declared normalisations, and after no others:
   - **(5a) `<br>` → one space.** Four `.navlink` spans and other two-line labels carry a `<br>`, which `textContent` drops without substituting anything. Join across `<br>` with a single space before comparing (QA-LST-12).
   - **(5b) `<label>` text is trimmed.** Where an `<input>` precedes its text inside a `<label>`, the DOM carries a leading space. Leading and trailing whitespace is stripped from `<label>` text before comparison; all other text is compared unstripped (QA-SMP-02, QA-SMP-03, QA-LST-07).
   - **(5c) A trailing `.dot` annotation is excluded.** `[WF]` runs execute with annotations shown, so any element carrying class `anno` also contains a `<span class="dot">` whose text is the legend marker. Read such an element's own text (`firstChild.textContent`, or `textContent` with every descendant `.dot` removed) before comparing (QA-IMP-12, QA-LST-01).
   Colours quoted from a **stylesheet rule** (`cssRules[].cssText`) are re-serialised by the CSSOM: an authored `#EBE1FF` comes back as `rgb(235, 225, 255)`. Either form satisfies a stylesheet-rule assertion; computed-style assertions remain `rgb()`-only per rule 3.
6. **"Identical content"** — where a scenario asserts that a modal opened from the `.wf-bar` has content identical to the same modal opened from the page (QA-IMP-02, QA-SMP-28, QA-SMP-29), the comparison basis is `document.getElementById(id).querySelector('.modal').innerHTML` string equality between the two entry paths. No other basis is permitted.
7. **`[WF-n · proposed]`** — the seven defect ids `[WF-15 · proposed]` … `[WF-21 · proposed]` are registered in `_plans/_wireframe-fixes.md` **§F** (appended 2026-08-03) and are recorded there as **`APPLIED 2026-08-03`**; the owner-approved wireframe-edit pass shipped all seven to `wms2/order-management/index.html` the same day. Through v1.2 this rule read the `· proposed` suffix as a live status meaning "not yet adjudicated, and no wireframe edit may be applied while specs are being written". That reading is **superseded**: the suffix is now nothing but a frozen part of the ID token, kept because shipped specs cite the full token and IDs are never renumbered or re-tokenised (`_wireframe-fixes` §F collision warning — a bare `WF-15` is ambiguous across three files, so always key on the full token **plus** the named file). A runner must therefore expect the **fixed** behaviour on the live wireframe; the eight scenarios that documented the pre-fix behaviour (QA-IMP-35 · QA-SMP-19 / 30 / 31 / 33 · QA-CMT-20 · QA-GBL-09 / 10) were re-baselined onto it in v1.3, keeping their ids. `WF-1` … `WF-14` remain unrelated to this page (§2.4).

**Wireframe demo limitations that force an `[ADMIN]` tag** (`_wireframe-fixes` §E, §2.4): the M1 preview is static and the dropzone parses nothing; `#mktConfirm` toasts regardless of validation; filter-bar and action-row controls are inert; `Mark all read` has no handler; the order list table is absent from the mock.
*(Through v1.2 this list also carried "`#sampCancelBtn` toasts regardless of selection" and "`Start Assignment (ON)` never toasts". Both stopped being true on 2026-08-03 when [WF-17 · proposed] and [WF-16 · proposed] were applied. They are kept here as history. **No scenario is retagged as a result:** QA-SMP-06 and QA-SMP-21 stay `[ADMIN]` because each also asserts a persisted event, which the mock cannot show either way, and the newly observable halves are asserted by the re-baselined QA-SMP-30 and QA-SMP-31 `[WF]`.)*

**Edge cases intentionally left unasserted (declared, not silent).** Two of the 100 `[E-n]` ids carry no QA scenario **by design**, because each resolves to a `§9.3` developer decision with no fixed observable: **`[E-9]`** (within-file duplicate `recipient + SKU` rows — the recommended default is "allow silently", so there is no assertable artifact either way until dev picks a warning) and **`[E-42]`** (a user without write access — v1 adds no gating at all `[G-15]` `[PD-1 · OWNER-PENDING]`, so the only assertable v1 behaviour is QA-GBL-05's "no action is refused for role reasons", which is already covered). Every other `[E-1]` … `[E-100]` id is named in at least one scenario body.

**Counts: 171 scenarios — 77 [WF], 94 [ADMIN]. Negative tests: 73 (42.7 %), well above the 25 % floor.** Negative scenarios are marked **(neg)**. Per block: IMP 62 · SMP 50 · LST 17 · CMT 24 · GBL 18. Every `[DC-n]` in §5 has at least one asserting Then-clause (matrix §8.6).
*(v1.3 delta: the negative count moved 77 → 73 and the share 45.0 % → 42.7 %. No scenario was added, removed, renumbered or retagged; the four that changed class — QA-IMP-35, QA-SMP-30, QA-CMT-20, QA-GBL-10 — were `(neg)` only because they documented a wireframe defect, and re-baselining them onto the applied fix (§8.0 rule 7) turned each into a positive assertion. QA-SMP-19 stayed positive; QA-SMP-31, QA-SMP-33 and QA-GBL-09 stayed `(neg)` because their re-baselined form still asserts a guard or an absence. Scenario total, `[WF]` / `[ADMIN]` split and per-block totals are unchanged.)*

### 8.1 Block IMP — Marketing Order Import `[L-1]` `[L-M1]` `[L-M1b]`

**QA-IMP-01 [WF]** — Open the import modal from the filter bar
Given the live wireframe is loaded and `window.__qaSentinel = 'om'`
When I click `.filterbar button[data-modal="m-import"]` (label `⬆ Import`)
Then `#m-import` has class `open`, its `header` text starts with `Marketing Order Import`, `window.__qaSentinel === 'om'`, and no `.gtoast` node exists yet.

**QA-IMP-02 [WF]** — Open the import modal from the wf-bar
Given the live wireframe is loaded
When I click `.wf-bar button[data-modal="m-import"]` (label `Modal: Marketing Import`)
Then `#m-import` has class `open`, and `document.getElementById('m-import').querySelector('.modal').innerHTML` is string-identical to the value the same expression returns after opening via QA-IMP-01's filter-bar button (§8.0 rule 6).

**QA-IMP-03 [WF]** — Step 1 copy
Given `#m-import` is open
When I read the first step block
Then it contains the bold label `1. Template`, a button labelled `⬇ Download Template (.xlsx)` with class `btn-line`, and the helper text `Standard form from the dev team — Recipient · Contact · Address · Country · SKU · Qty · Campaign name`.

**QA-IMP-04 [ADMIN]** — Template download persists `[DC-1]`
Given the real admin import modal is open
When I click `⬇ Download Template (.xlsx)`
Then an `.xlsx` file downloads **and** `[DC-1] import.template_downloaded` persists with my actor id, the timestamp, and the template version.

**QA-IMP-05 [WF]** — Order Type default state
Given `#m-import` is open
When I read the second step block
Then `#otChipSeed` has class `on` and text `Influencer Seeding`, `#otChipCustom` has text `✎ Custom` and no `on` class, and `#otCustom` has `style.display === 'none'`.

**QA-IMP-06 [WF]** — Order Type custom toggle and focus
Given `#m-import` is open
When I click `#otChipCustom`
Then `#otChipCustom` has class `on`, `#otChipSeed` does not, `#otCustom` has `style.display === 'inline-block'` with placeholder `Enter type (e.g. Pop-up event giveaway)`, and `document.activeElement === document.getElementById('otCustom')`.

**QA-IMP-07 [WF]** — Toggling back hides the custom input but keeps its value
Given `#otChipCustom` is active and I have typed `Pop-up event giveaway` into `#otCustom`
When I click `#otChipSeed`
Then `#otCustom.style.display === 'none'`, `#otChipSeed` has class `on`, and `#otCustom.value === 'Pop-up event giveaway'` (retained but ignored, §3.2.2).

**QA-IMP-08 [WF]** — PIC defaults and helper copy
Given `#m-import` is open
When I read the third step block
Then the PIC `<select>` has `Yongwon Ryu (me)` selected among options `Yongwon Ryu (me)`, `Harshit`, `EuJin`, `Adinda`; `#picCustomBtn` reads `✎ Custom`; `#picCustomIn` has `style.display === 'none'` and placeholder `Enter PIC name`; and the helper text reads `Default = logged-in user · Recorded as the PIC for this entire import — shown in the order list & RTO`.

**QA-IMP-09 [WF]** — PIC custom toggle and focus
Given `#m-import` is open
When I click `#picCustomBtn`
Then `#picCustomIn.style.display === 'inline-block'` and `document.activeElement === document.getElementById('picCustomIn')`
And when I click `#picCustomBtn` again, `#picCustomIn.style.display === 'none'`.

**QA-IMP-10 [WF]** — Upload step copy
Given `#m-import` is open
When I read the fourth step block
Then it contains the bold label `4. Upload` and a `.dropzone` whose text is `📄 Drag the completed template here or click to upload`.

**QA-IMP-11 [WF]** — Preview header format
Given `#m-import` is open
When I read the preview header, located as `document.querySelector('#m-import table.tbl').previousElementSibling` (the `<b>` immediately preceding the preview table)
Then that element is a `<b>` and its `textContent` reads exactly `Preview — mkt_seeding_batch3.xlsx · 12 rows parsed · 0 errors`.

**QA-IMP-12 [WF]** — Preview table headers
Given `#m-import` is open with annotations shown (the §8.0 default)
When I read `#m-import thead th` in order, taking each cell's own text per §8.0 rule 5c — `th.firstChild.textContent`, which excludes the `<span class="dot">` the annotated cell carries
Then `#m-import thead th` has length `7` and the seven values are `Recipient`, `Country`, `SKU`, `Product Name`, `Qty`, `Campaign`, `Carrier (auto)`
And the raw `textContent` of the seventh cell is `Carrier (auto)M1b`, because that cell is `<th class="anno">` and contains the `M1b` annotation dot — the dot is intentional chrome (QA-GBL-11, `_wireframe-fixes` §E) and its presence is **not** a defect.

**QA-IMP-13 [WF]** — Brand-bold product names `[G-6]`
Given `#m-import` is open
When I read the Product Name cells
Then row 1 contains `<b>Dr.Jart+</b>` followed by ` Cicapair Gentle Cleansing Foam`, row 2 contains `<b>Dr.Jart+</b>` followed by ` Cicapair Sleepair Mask`, and row 3 contains `<b>innisfree</b>` followed by ` Green Tea Seed Hyaluronic Serum`.

**QA-IMP-14 [WF]** — Connected-carrier rendering `[L-M1b]`
Given `#m-import` is open
When I read the last cell of every row whose Country cell is `GB`
Then each contains exactly `YunExpress` with computed colour `rgb(25, 135, 84)` and `font-weight` `700`.

**QA-IMP-15 [WF] (neg)** — Unconnected carrier blocks the whole file `[L-M1b]` `[E-7]` `[G-17]` *(rewritten 2026-08-04 — it previously asserted the superseded "does not block" behaviour)*
Given `#m-import` is open in its default state (the **clean** preview)
Then the row whose Recipient is `Lucia Ramos` and whose Country is `PE` carries `YunExpress` with computed colour `rgb(25, 135, 84)`, `#mktBlock` is `display: none`, and `#mktConfirm` has neither `disabled` nor `aria-disabled="true"`
When I close the modal, click the wf-bar toggle `#impPreviewToggle`, and reopen `#m-import` — the **unconnected** preview (`WF-16b`, wireframe-only chrome)
Then `#mktPECell` reads exactly `Cannot import — no connected carrier` with computed colour `rgb(220, 53, 69)` and `font-weight` `700`
And `#mktBlock` is `display: block` and reads exactly `Cannot import — these countries have no connected carrier: PE. Ask the fulfillment team to connect them, or remove those rows and upload again.`
And `#mktConfirm` carries both `disabled` and `aria-disabled="true"` — one unconnected row refuses the entire file, and no order is created `[G-17]`.

**QA-IMP-16 [WF]** — Confirm button label format
Given `#m-import` is open
When I read `#mktConfirm`
Then its text is exactly `Confirm Import (12 orders)` and it carries class `btn-mkt`.

**QA-IMP-17 [WF]** — Confirm toast text, colour, dismissal and no reload `[E-43]` `[E-45]`
Given `#m-import` is open and `window.__qaSentinel = 'om'`
When I click `#mktConfirm`
Then `#m-import` no longer has class `open`
And `#gtoast` exists with `display` not `none`, `position: fixed`, `top: 16px`, `right: 16px`, computed background `rgb(25, 135, 84)`
And its first text node is `✓ Confirmed — 12 orders imported` and its `<small>` reads `Carrier auto-assigned per country · 1 not connected — flagged to contact Fulfillment Center`
And after ~2 600 ms `#gtoast` has `display: none`
And `window.__qaSentinel === 'om'` — the page did not reload `[G-2]`.

**QA-IMP-18 [WF]** — Modal note copy (BR-1 in operator-visible form)
Given `#m-import` is open
When I read `.note.mkt`
Then it reads exactly `On confirm, orders are created as MKT- orders and appear immediately in Ready to be Outbonded (Marketing view) regardless of stock or inbound status.` — including the preserved spelling `Outbonded`.

**QA-IMP-19 [WF] (neg)** — No stock-error copy anywhere in the modal `[E-20]`
Given `#m-import` is open
When I search `#m-import` for the case-insensitive substrings `out of stock`, `not in the warehouse`, `insufficient`
Then none is present, and the only occurrence of `stock` in `#m-import` is inside `.note.mkt` (§3.2.7), in the phrase `regardless of stock or inbound status` (BR-1, R-2).
(No Korean-language token is searched for. §2.2 declares that no Korean string exists anywhere on this page, so a Korean "stock" probe could never match: it would assert nothing and would contradict the spec's own declaration. Korean-copy regression belongs to a page that renders Korean `[G-6]`.)

**QA-IMP-20 [WF] (neg)** — No print, scan, or carrier-picker affordance in the modal
Given `#m-import` is open
When I enumerate `#m-import button`, `#m-import input`, `#m-import select`
Then no button label contains `Print`, no input has `type="file"` or a scan role, and the only `<select>` is the PIC picker — there is no carrier `<select>` anywhere (BR-3, BR-28, BR-29).

**QA-IMP-21 [ADMIN] (neg)** — Non-xlsx upload rejected `[E-1]`
Given the real admin import modal is open
When I upload `orders.csv`
Then an inline error reads `Unsupported file — upload the .xlsx template.`, no preview renders, `Confirm Import` stays disabled, and `[DC-2] import.file_uploaded` persists with parse outcome `rejected_format`.

**QA-IMP-22 [ADMIN] (neg)** — A row error blocks the whole file `[E-3]` `[E-19]`
Given the real admin import modal is open
When I upload a 12-row file where row 4 has an empty `Country`
Then the preview header reads `… · 12 rows parsed · 1 errors`, row 4 shows its reason, `Confirm Import` is **disabled**, and `[DC-3] import.file_parsed` persists the per-row error reason (BR-12, `[PD-57 · OWNER-PENDING]`).

**QA-IMP-23 [ADMIN] (neg)** — Zero-stock SKU must NOT block `[E-20]`
Given the real admin import modal is open
When I upload a file whose every SKU has stock 0 and no inbound history, and then click `Confirm Import`
Then no error was raised, `Confirm Import` was enabled, and after the confirm all orders exist and are listed in the RTO Marketing view (BR-1). Regression guard for R-2.

**QA-IMP-24 [ADMIN] (neg)** — Empty custom order type blocks confirm `[E-14]`
Given a valid file is parsed with 0 errors
When I click `✎ Custom` in Step 2 and leave `#otCustom` empty
Then `Confirm Import` is disabled and the inline message reads `Enter an order type.`

**QA-IMP-25 [ADMIN] (neg)** — Empty custom PIC blocks confirm `[E-15]`
Given a valid file is parsed with 0 errors
When I click `✎ Custom` in Step 3 and type only whitespace into the PIC custom input
Then `Confirm Import` is disabled and the inline message reads `Enter a PIC name.`

**QA-IMP-26 [ADMIN] (neg)** — Zero data rows blocks confirm `[E-2]` `[E-63]`
Given the real admin import modal is open
When I upload a valid template containing headers but no data rows
Then the preview header reads `… · 0 rows parsed · 0 errors`, `Confirm Import` is disabled, and no empty batch is created.

**QA-IMP-27 [ADMIN]** — Confirm persists the whole batch chain `[DC-6]` `[DC-9]` `[DC-10]` `[DC-12]`
Given a valid 12-row file in which **every** row's country has a connected carrier (12 `GB` rows), order type `Influencer Seeding`, PIC `Yongwon Ryu (me)`
When I click `Confirm Import (12 orders)`
Then exactly 12 orders exist with `MKT-` numbers
And `[DC-6] import.batch_confirmed` persists with batch id, filename, file hash, `order_count=12`, order type, PIC, `carriers_assigned=12`, idempotency key
And 12 `[DC-9] order.created` events persist with recipient, contact, address, country, SKU, qty, product-name snapshot, campaign and batch id
And 12 `[DC-10] order.carrier_assigned` events persist with `old=null → new=YunExpress`
And **no** `[DC-11]` event persists — `[G-17]` retired that state; a file containing any unconnected row never reaches Confirm (see QA-IMP-55)
And 12 `[DC-12] order.pic_assigned` events persist with the batch PIC.

**QA-IMP-28 [ADMIN] (neg)** — Double-click creates one batch `[E-11]` `[DC-28]`
Given a valid file is parsed
When I click `Confirm Import` twice within 200 ms
Then exactly one batch exists, exactly `{n}` orders were created, and one `[DC-28] idempotency.duplicate_suppressed` persists naming `import.batch_confirmed` `[G-9]`.

**QA-IMP-29 [ADMIN] (neg)** — Network failure is atomic `[E-12]` `[DC-7]`
Given a valid file is parsed
When I click `Confirm Import` and the network drops after the request is sent
Then either all `{n}` orders exist or none do — never a partial batch
And a **red** toast is shown, and `[DC-7] import.batch_rejected` persists when the server rejected it.

**QA-IMP-30 [ADMIN]** — Duplicate file warns, does not block `[E-10]` `[DC-4]` `[DC-5]`
Given `mkt_seeding_batch3.xlsx` was already confirmed as batch `B-1042`
When I upload the identical file and click `Confirm Import`
Then a dialog titled `This file was already imported` appears with a body naming batch `B-1042` and buttons `Cancel` and `Import anyway`
And `[DC-4] import.duplicate_file_warned` persists
And choosing `Import anyway` creates the batch and persists `[DC-5] import.duplicate_file_overridden` `[PD-58 · OWNER-PENDING]`.

**QA-IMP-31 [ADMIN]** — Abandoning the modal creates nothing `[E-13]` `[DC-8]`
Given a valid file has been uploaded and previewed
When I click `Cancel`
Then no orders are created, `[DC-8] import.batch_abandoned` persists with reason `user_closed`, and `[DC-2]` and `[DC-3]` remain persisted (§3.2.4).

**QA-IMP-32 [ADMIN] (neg)** — Ambiguous carrier mapping aborts the batch `[E-52]`
Given the configuration maps `GB` to two connected carriers
When I click `Confirm Import`
Then no orders are created, a red toast names `GB`, and `[DC-7]` persists with reason `ambiguous_carrier_mapping`.

**QA-IMP-33 [ADMIN]** — Post-import list behaviour `[E-45]` `[E-57]`
Given the header reads `2,818 orders` and a date filter plus page 2 are active
When a 12-order import is confirmed
Then the header reads `2,830 orders`, 12 new purple `MKT-` rows are present, the applied filter and page number are unchanged, and no page reload occurred
And the 12 rows now visible are exactly the 12 orders written by that batch's `[DC-9] order.created` events — the list is a view over them, so their count and their order numbers match one-for-one.

**QA-IMP-34 [ADMIN]** — Export egress is recorded `[DC-26]` `[DC-27]`
Given a filter set is applied
When I click `⬇ Export` and then `⬇ Yun Export`
Then `[DC-26] orders.exported` and `[DC-27] orders.yun_exported` each persist with the filter context and the row count, and neither shows a toast (§3.13).

**QA-IMP-35 [WF]** — Preview collapse row spans the full table — re-baselined on [WF-15 · proposed], applied 2026-08-03
Given `#m-import` is open
When I read `#m-import tbody td[colspan]`
Then exactly one such cell exists, its text is `⋯ +8 more rows`, and its `colspan` attribute is `7`, equal to the length of `#m-import thead th`
And the collapse row therefore spans the full table (§3.2.4).
*(Through v1.2 this scenario was a `(neg)` defect-documentation test asserting `colspan="6"` against 7 headers. The wireframe-edit pass applied `colspan="7"` on 2026-08-03, so the assertion was re-baselined onto the fixed value and the scenario is no longer negative. The id is unchanged.)*

**QA-IMP-36 [WF]** — Preview row arithmetic matches the header count
Given `#m-import` is open
When I count the data rows
Then 4 named rows are rendered (`Svetlana Jaloba`, `Zoe Garner`, `Mariana Maheha`, `Lucia Ramos`) plus one collapse row reading `⋯ +8 more rows`, so 4 + 8 = 12, consistent with the header's `12 rows parsed`.

**QA-IMP-37 [WF] (neg)** — The dropzone is inert in the mock (demo limitation, not a defect)
Given `#m-import` is open
When I click `.dropzone`
Then no file picker opens, no `input[type=file]` exists anywhere in the document, and the preview is unchanged — the preview data is static (`_wireframe-fixes` §E). All parse-behaviour scenarios are therefore `[ADMIN]`.

**QA-IMP-38 [WF]** — Modal geometry and dismissal controls
Given `#m-import` is open
When I inspect `#m-import .modal`
Then it carries classes `modal wide`, its `max-width` computes to `720px`, its header exposes a `✕` control matching `header .x[data-close]`, and its footer contains exactly two buttons, `Cancel` and `Confirm Import (12 orders)`.

**QA-IMP-39 [WF] (neg)** — Repeated confirms reuse one toast node
Given I have clicked `#mktConfirm` once and have not touched `#sampCancelBtn`
When I reopen `#m-import` and click `#mktConfirm` again
Then `document.querySelectorAll('.gtoast').length === 1` and its id is `gtoast` — no second node is created for the same action (contrast [WF-18 · proposed], which is about two *different* actions).

**QA-IMP-40 [ADMIN] (neg)** — Country given as a full name `[E-67]`
Given the real admin import modal is open
When I upload a file containing one row whose Country is `United Kingdom` and one whose Country is `Nowhereland`
Then the first normalises to `GB` and resolves to `YunExpress`, while the second is a row error `Invalid country` that blocks the whole file.

**QA-IMP-41 [ADMIN] (neg)** — Whitespace-only fields count as missing `[E-68]`
Given the real admin import modal is open
When I upload a file containing a row whose Recipient is three spaces and whose SKU has a trailing non-breaking space
Then the SKU is trimmed and resolves normally, while the Recipient is treated as missing and produces a row error that blocks the file.

**QA-IMP-42 [ADMIN] (neg)** — Non-integer quantity `[E-69]` `[E-5]`
Given the real admin import modal is open
When I upload a file containing rows with Qty `1.5`, `1,000` and `'2`
Then `1,000` imports as `1000` and `'2` imports as `2`, while `1.5` is a row error that blocks the file.

**QA-IMP-43 [ADMIN] (neg)** — Multi-sheet workbook and merged header cells `[E-70]`
Given the real admin import modal is open
When I upload a workbook whose second sheet contains extra rows
Then only the first sheet is parsed and the second is ignored
And when I instead upload a workbook whose header row contains a merged cell, the file is rejected with an explicit reason and nothing is parsed.

**QA-IMP-44 [ADMIN] (neg)** — Outdated template rejected `[E-71]`
Given the real admin import modal is open
When I upload a file built from a superseded template version
Then it is rejected with a message naming the required version and pointing back at `⬇ Download Template (.xlsx)`, and `[DC-2]` persists outcome `rejected_template_version`.

**QA-IMP-45 [ADMIN]** — System values win over file-supplied name/number columns `[E-72]` `[E-51]`
Given the real admin import modal is open
When I upload a file with extra `Product Name` and `Order No` columns whose values disagree with the catalogue and with the sequence, and I click `Confirm Import`
Then the created orders carry the system-resolved product name and a system-minted `MKT-#####`, and the file's values are recorded on the parse result but never applied.

**QA-IMP-46 [ADMIN]** — Discontinued SKU still imports `[E-73]`
Given the real admin import modal is open
When I upload a file containing a row whose SKU is discontinued or unpublished
Then no error is raised, the row imports, and the product-name snapshot is taken at creation time (same doctrine as BR-1).

**QA-IMP-47 [ADMIN] (neg)** — Session expiry between upload and confirm `[E-74]`
Given a parsed draft and an expired session
When I click `Confirm Import`
Then a red toast is shown, no orders are created, and `[DC-7]` persists with reason `session_expired`; after the draft TTL elapses `[DC-8]` persists with reason `session_lost`.

**QA-IMP-48 [ADMIN]** — Lost response, safe retry `[E-75]`
Given the server committed the batch but the client timed out
When I retry the confirm with the same idempotency key
Then exactly `{n}` orders exist in total, the committed batch is returned unchanged, and `[DC-28]` records the suppressed repeat — no second batch.

**QA-IMP-49 [ADMIN]** — Two tabs, two batches `[E-76]` `[E-41]`
Given the same operator has this page open in tab A and tab B
When the operator confirms one import in tab A and a different import in tab B
Then two distinct batches exist with distinct `MKT-` ranges, no id collides, and neither draft's Order Type or PIC leaks into the other.

**QA-IMP-50 [ADMIN] (neg)** — Browser Back does not revert `[E-77]`
Given a confirmed import
When I press the browser Back button
Then the dashboard is shown, the batch still exists in full, and no revert or undo affordance is offered anywhere (BR-14, `[PD-54 · OWNER-PENDING]`).

**QA-IMP-51 [ADMIN]** — Disabled carrier connection behaves as unconnected `[E-80]` `[G-17]`
Given `GB` maps to `YunExpress` but that connection is disabled at confirm time
When I upload a file of `GB` rows and click `Confirm Import`
Then the `GB` rows render amber `Not connected — contact the Fulfillment Center`, **the whole file is rejected and no order is created** `[G-17]`, and `[DC-7] import.batch_rejected` persists with reason `connection_disabled`.
And a disabled connection is treated identically to no mapping at all — the two must not diverge into different outcomes.

**QA-IMP-52 [ADMIN]** — Per-row carriers in one batch `[E-81]` `[E-18]`
Given the configuration maps `GB` and `AU` to two different connected carriers and `PE` to none
When I upload a file containing `GB`, `AU` and `PE` rows and click `Confirm Import`
Then each order carries its own row's carrier, no batch-level carrier is recorded, and the toast subtext counts only the `PE` row as unresolved
And one `[DC-10] order.carrier_assigned` persists per connected row, each naming that row's own carrier and mapping version — never a single batch-level assignment.

**QA-IMP-53 [ADMIN] (neg)** — Unknown SKU blocks the whole file `[E-4]`
Given the real admin import modal is open
When I upload a 12-row file in which row 7's SKU is not present in the catalog
Then row 7 shows the reason `Unknown SKU`, the preview header reads `… · 12 rows parsed · 1 errors`, `Confirm Import` is **disabled**, and no order is created for any of the other 11 rows either — the file is the unit of intent (BR-12, `[PD-57 · OWNER-PENDING]`)
And `[DC-3] import.file_parsed` persists the per-row error reason.

**QA-IMP-54 [ADMIN] (neg)** — Invalid country code blocks the file, and is distinct from an unconnected carrier `[E-6]` `[E-7]`
Given the real admin import modal is open
When I upload a file containing one row whose Country is `ZZ` (not a supported code) and one row whose Country is `PE` (supported, no connected carrier)
Then the `ZZ` row shows the reason `Invalid country`, is counted in `{e}`, and blocks the whole file
And the `PE` row is **not** an error: it renders amber `Not connected — contact the Fulfillment Center` and would not have blocked anything on its own — the two conditions must never be merged into one error class.

**QA-IMP-55 [ADMIN] (neg)** — A file where every row is unconnected is rejected in full `[E-8]` `[G-17]`
Given the real admin import modal is open
When I upload a 9-row file in which every row's country has no connected carrier, and I click `Confirm Import`
Then **no order is created** and `[DC-7] import.batch_rejected` persists with the unconnected countries listed `[G-17]`
And the rejection is all-or-nothing — the file is never partially imported, because a silently partial success is the one failure mode nobody notices.

**QA-IMP-56 [ADMIN] (neg)** — Row or byte limit rejects the file `[E-16]` `[DC-2]`
Given the configured maximum row count and maximum file size
When I upload a file that exceeds either limit
Then it is rejected with an explicit message that names the limit value verbatim, no rows are parsed, no preview renders, and `[DC-2] import.file_uploaded` persists with parse outcome `rejected_limit` (limit values are a §9.3 developer decision; the assertion is that the message names whichever value was configured).

**QA-IMP-57 [ADMIN] (neg)** — Template schema mismatch `[E-17]` `[DC-2]`
Given the real admin import modal is open
When I upload a file whose columns have been reordered and which carries one extra column, and then a second file that is missing the required `Country` header
Then the reordered-plus-extra file parses normally — headers are matched by name and the extra column is ignored
And the file missing a required header is rejected with a message naming the missing header, nothing is parsed, and `[DC-2]` persists with parse outcome `rejected_format`.

**QA-IMP-58 [ADMIN] (neg)** — Tab closed mid-upload creates nothing `[E-55]` `[DC-8]`
Given a file is uploading or a parsed draft is staged in the modal
When I close the browser tab before clicking `Confirm Import`
Then no orders are created, the staged draft is orphaned and reaped, and `[DC-8] import.batch_abandoned` persists with reason `session_lost` (§3.2.6).

**QA-IMP-59 [ADMIN]** — Export during a commit is a consistent snapshot `[E-58]`
Given a 12-order batch is committing
When I click `⬇ Export` while that commit is in flight
Then the exported file contains either all 12 of that batch's orders or none of them — never a partial batch — and the row count recorded in `[DC-26]` matches the rows the file actually contains.

**QA-IMP-60 [ADMIN]** — Carrier mapping changes between preview and confirm `[E-65]` `[DC-10]`
Given a file was parsed while `GB` mapped to `YunExpress`, so the preview's advisory `Carrier (auto)` cells read `YunExpress`
When the mapping is changed to a different connected carrier and I then click `Confirm Import`
Then the orders are assigned the **confirm-time** carrier, not the previewed one; `[DC-10] order.carrier_assigned` persists the confirm-time carrier and its mapping version; and the toast subtext reports confirm-time counts (§3.3).

**QA-IMP-61 [ADMIN] (neg)** — Over-length recipient or address never blocks `[E-78]`
Given the real admin import modal is open
When I upload a file containing a Recipient and an Address longer than the destination carrier's field limit
Then no error is raised, the rows import, and the values are stored verbatim — carrier-side truncation or rejection is a downstream concern and must never block order creation (§3.2.4).

**QA-IMP-62 [ADMIN] (neg)** — Contact without a dialling code never blocks `[E-79]`
Given the real admin import modal is open
When I upload a file whose Contact values omit the country dialling code and use a format the carrier will later reject
Then no error is raised at import, the values are stored verbatim, and no format validation runs here — carrier-format validation belongs to the label/export pipeline (§3.2.4).

### 8.2 Block SMP — Sample assignment `[L-2a]` `[L-2b]` `[L-M2]` `[L-M3]`

**QA-SMP-01 [WF]** — ON button opens M2
Given the live wireframe is loaded and `window.__qaSentinel = 'om'`
When I click `.actionrow button[data-modal="m-sampleon"]` (label `Sample Assignment ON`, class `btn-green`)
Then `#m-sampleon` has class `open`, its header text starts with `Sample Assignment ON`, and `window.__qaSentinel === 'om'`.

**QA-SMP-02 [WF]** — Target radios
Given `#m-sampleon` is open
When I read the `Assignment Target` group
Then the bold group label `Assignment Target` is present, `input[name="samptarget"]` has length `2`, the first is `checked` and labelled `All new orders in this period`, and the second is labelled `Selected orders only (2)`.

**QA-SMP-03 [WF]** — Period fields and `forever` default
Given `#m-sampleon` is open
When I read the `Assignment Period` group
Then the bold group label `Assignment Period` is present with a start-date input valued `2026-07-23`, a start-time input valued `10:00`, a `~` separator, inputs placeholdered `End date` and `Time`, and a checkbox labelled `forever (no end date)` whose `checked` is `true`.

**QA-SMP-04 [WF] (neg)** — Modal note and absence of any sample-type picker
Given `#m-sampleon` is open
When I read `.note` and enumerate the modal's form controls
Then the note contains `product type is not selected` and `exactly 1 sample set per order`
And `#m-sampleon` contains **zero** `<select>` elements and no product picker of any kind (BR-6) — a sample-type control must never be added here.

**QA-SMP-05 [WF]** — Footer buttons
Given `#m-sampleon` is open
When I read `#m-sampleon .foot button`
Then there are exactly two: a grey `Cancel` and a green `Start Assignment (ON)`.

**QA-SMP-06 [ADMIN]** — `Start Assignment (ON)` toast, all-new target `[DC-13]`
Given `#m-sampleon` is open with target `All new orders in this period`, start `2026-07-23 10:00`, and `forever` checked
When I click `Start Assignment (ON)`
Then the modal closes and a green toast reads `✓ Sample assignment started` with subtext `All new sales orders from 2026-07-23 10:00 → forever · exactly 1 sample set per order`
And `[DC-13] sample.period_created` persists with `target_type=all_new_in_period`, the start datetime, `forever=true`, the operating timezone (BR-31) and an idempotency key.
(Through v1.2 the live wireframe showed **no** toast here — [WF-16 · proposed] — which was the stated reason for the `[ADMIN]` tag. The toast was applied on 2026-08-03 and the wireframe now renders exactly these two strings, asserted by the re-baselined QA-SMP-30 `[WF]`. This scenario keeps its `[ADMIN]` tag on its second clause: `[DC-13]` persistence cannot be observed in the mock.)

**QA-SMP-07 [ADMIN] (neg)** — End earlier than start blocks `[E-22]`
Given `#m-sampleon` is open with target `All new orders in this period`
When I uncheck `forever`, set start to `2026-07-23 10:00` and set end to `2026-07-23 09:00`
Then `Start Assignment (ON)` is disabled and the inline message reads `End must be later than start.`

**QA-SMP-08 [ADMIN] (neg)** — Missing end with `forever` unchecked blocks `[E-54]`
Given `#m-sampleon` is open with a valid start date and time entered
When I uncheck `forever` and leave both end fields empty
Then `Start Assignment (ON)` is disabled and the inline message reads `Enter an end date and time, or choose forever.`

**QA-SMP-09 [ADMIN] (neg)** — Zero-selection target disabled `[E-21]`
Given no rows are selected in the order list
When I open the ON modal
Then the second radio reads `Selected orders only (0)` and is `disabled`, while the first radio remains selectable.

**QA-SMP-10 [ADMIN]** — Selected-orders target assigns immediately `[E-33]` `[E-35]` `[DC-14]` `[DC-15]` `[DC-16]`
Given 5 orders are selected: 3 plain sales orders, 1 that already holds a sample set, and 1 `MKT-` order
When I confirm with target `Selected orders only (5)`
Then 3 orders receive a set and the toast subtext reads `3 orders assigned · 1 skipped (already assigned) · 1 skipped (not eligible)`
And 3 `[DC-14] sample.assigned_to_order` (reason `explicit_selection`), 1 `[DC-15] sample.assignment_deduped`, and 1 `[DC-16] sample.assignment_skipped_ineligible` (reason `marketing_order`) persist `[PD-53 · OWNER-PENDING]`.

**QA-SMP-11 [ADMIN] (neg)** — Backdated start is not retroactive `[E-25]`
Given 40 sales orders were created on 2026-07-20
When I start a period with start datetime `2026-07-19 00:00` and `forever`
Then none of the 40 existing orders receives a sample set and no `[DC-14]` event references them (BR-15, `[PD-52 · OWNER-PENDING]`).

**QA-SMP-12 [ADMIN]** — Exactly one set with overlapping periods `[E-24]` `[E-46]`
Given two Active periods both match new sales orders
When a new sales order is created
Then it holds exactly one sample set, one `[DC-14]` persists, and one `[DC-15] sample.assignment_deduped` persists naming the suppressed period and the winning period (BR-7).

**QA-SMP-13 [ADMIN] (neg)** — Periods do not match MKT orders `[E-35]` `[E-56]`
Given an Active `all_new_in_period` period
When a marketing import creates 12 `MKT-` orders
Then none receives a sample set and 12 `[DC-16]` events persist with reason `marketing_order` (BR-17, `[PD-56 · OWNER-PENDING]`).

**QA-SMP-14 [ADMIN] (neg)** — Cancelling emits no unassignment `[E-30]` `[DC-17]`
Given an Active period has assigned sets to 34 orders
When I cancel that period
Then all 34 orders still hold their sets, one `[DC-17] sample.period_cancelled` persists with `old=Active → new=Cancelled`, and **zero** events of any unassignment type exist for those orders (BR-9, BR-19). The absence is the assertion.

**QA-SMP-15 [WF]** — Cancel button opens M3
Given the live wireframe is loaded
When I click `.actionrow button[data-modal="m-sampleoff"]` (label `Cancel Sample Assignment`)
Then `#m-sampleoff` has class `open` and its header text starts with `Cancel Sample Assignment — Current Assignment Periods`.

**QA-SMP-16 [WF]** — M3 table content
Given `#m-sampleoff` is open
When I read `#m-sampleoff thead th` and the three `tbody` rows
Then the headers are ``, `Assignment Period`, `Target`, `Status`
And row 1 reads `2026-07-01 09:00 → forever` / `All new orders` / `Active`, with `forever` inside a `<b>`
And row 2 reads `2026-07-15 00:00 → 2026-07-20 23:59` / `34 selected orders` / `Active`
And row 3 reads `2026-06-01 00:00 → 2026-06-30 23:59` / `All new orders` / `Ended`.

**QA-SMP-17 [WF] (neg)** — Ended row has no checkbox element `[E-27]`
Given `#m-sampleoff` is open
When I count `input[type=checkbox]` inside each `tbody` row
Then the row whose Status is `Ended` contains **zero** — not a disabled one, no element at all — while each `Active` row contains exactly one.

**QA-SMP-18 [WF]** — M3 note copy
Given `#m-sampleoff` is open
When I read `#m-sampleoff .note`
Then it reads exactly `Multiple assignment periods may exist — select the period(s) to cancel, then confirm. Ended periods are for record only (cannot be cancelled). Cancellation immediately stops new assignments for that period (already-assigned orders are kept).`

**QA-SMP-19 [WF]** — Confirm dialog precedes the cancel toast; text and no reload — re-baselined on [WF-17 · proposed], applied 2026-08-03
Given `#m-sampleoff` is open with row 1's checkbox checked (its default state) and `window.__qaSentinel = 'om'`
When I click `#sampCancelBtn` (label `Cancel Selected Periods`, red)
Then `#m-sampleoff` still has class `open`, no node with id `gtoast2` exists yet, and the confirm overlay `#m-sampcancel-confirm` gains class `open` with its `header` first text node reading `Cancel 1 assignment period(s)?` (the count follows the selection, §3.7.5)
And when I then click `#sampConfirmGo` (label `Cancel periods`, red), both `#m-sampcancel-confirm` and `#m-sampleoff` lose class `open`
And `#gtoast2` is visible with first text node `✓ Assignment period cancelled` and `<small>` reading `New assignments stopped for the selected period · already-assigned orders kept`
And `window.__qaSentinel === 'om'`.
*(Through v1.2 the wireframe fired the toast straight off `#sampCancelBtn` with no confirm step, and this scenario asserted that shorter path with the note "in the real admin the confirm dialog of QA-SMP-20 precedes this toast". The wireframe-edit pass built the confirm step on 2026-08-03, so the `[WF]` path now matches the specified one. QA-SMP-20 stays `[ADMIN]`: it additionally asserts the `[DC-17]` writes and the `Keep periods` no-write branch, which the mock cannot show.)*

**QA-SMP-20 [ADMIN]** — Confirm step before cancelling `[PD-5 · OWNER-PENDING]`
Given `#m-sampleoff` is open with 2 Active periods checked
When I click `Cancel Selected Periods`
Then a dialog titled `Cancel 2 assignment period(s)?` appears with body `New assignments stop immediately. Orders already assigned keep their sample set.` and buttons `Keep periods` and `Cancel periods`
And choosing `Keep periods` writes nothing — zero `[DC-17]`
And choosing `Cancel periods` writes one `[DC-17]` per period and then shows the QA-SMP-19 toast (BR-25).
(The dialog and both buttons are now built in the wireframe too — [WF-17 · proposed], applied 2026-08-03, overlay `#m-sampcancel-confirm`; this scenario stays `[ADMIN]` for the `[DC-17]` write assertions, which the mock cannot show.)

**QA-SMP-21 [ADMIN] (neg)** — Zero selection disables cancel `[E-28]`
Given `#m-sampleoff` is open with no checkboxes checked
When I attempt to click `Cancel Selected Periods`
Then it is disabled, and the attempted click produces no dialog, no toast and no event.
(The live wireframe fired the toast regardless until [WF-17 · proposed] was applied 2026-08-03; the observable half is now asserted on the wireframe by QA-SMP-31. This scenario stays `[ADMIN]` for the "no event" clause.)

**QA-SMP-22 [ADMIN] (neg)** — Double-click cancels once `[E-29]` `[DC-28]`
Given the confirm dialog is open with 2 periods selected
When I click `Cancel periods` twice within 200 ms
Then each selected period transitions exactly once and one `[DC-28] idempotency.duplicate_suppressed` persists naming `sample.period_cancelled` `[G-9]`.

**QA-SMP-23 [ADMIN]** — Cancelled row becomes record-only `[E-27]` (BR-30)
Given a period was cancelled
When I reopen the Cancel modal
Then its Status reads `Cancelled`, the row is greyed, it contains **zero** checkboxes, and it is never removed from the list.

**QA-SMP-24 [ADMIN]** — Scheduled period `[E-53]`
Given `#m-sampleon` is open
When I create a period whose start datetime is 3 days in the future, then reopen `#m-sampleoff`
Then that period appears with status `Scheduled`, carries a checkbox, and assigns nothing until its start datetime is reached.

**QA-SMP-25 [ADMIN]** — Boundary inclusivity `[E-61]`
Given an Active period `2026-08-05 09:00 → 2026-08-05 17:00`
When one sales order is created at exactly `09:00:00` and another at exactly `17:00:00`
Then the first receives a set and the second does not (start inclusive, end exclusive).

**QA-SMP-26 [ADMIN] (neg)** — Concurrent cancel of the same period `[E-47]`
Given operator A and operator B both have the Cancel modal open with period `P-7` checked
When A cancels and then B cancels
Then B receives a non-green toast reporting that `P-7` was already cancelled, B's list reloads, exactly one `[DC-17]` exists for `P-7`, and B's other selections still process `[PD-6 · OWNER-PENDING]` `[PD-7 · OWNER-PENDING]`.

**QA-SMP-27 [ADMIN]** — Period auto-end persists `[DC-18]`
Given an Active period whose end datetime has not yet been reached
When its end datetime passes
Then its status becomes `Ended`, it loses its checkbox, and `[DC-18] sample.period_ended` persists with `old=Active → new=Ended`.

**QA-SMP-28 [WF]** — M2 opens from the wf-bar
Given the live wireframe is loaded
When I click `.wf-bar button[data-modal="m-sampleon"]` (label `Modal: Sample Assignment ON`)
Then `#m-sampleon` has class `open`, and `document.getElementById('m-sampleon').querySelector('.modal').innerHTML` is string-identical to the value the same expression returns after opening via the action-row button of QA-SMP-01 (§8.0 rule 6) — so the assertions of QA-SMP-02 and QA-SMP-03 hold unchanged from this entry point.

**QA-SMP-29 [WF]** — M3 opens from the wf-bar
Given the live wireframe is loaded
When I click `.wf-bar button[data-modal="m-sampleoff"]` (label `Modal: Cancel Sample Assignment`)
Then `#m-sampleoff` has class `open`, and `document.getElementById('m-sampleoff').querySelector('.modal').innerHTML` is string-identical to the value the same expression returns after opening via the action-row button of QA-SMP-15 (§8.0 rule 6) — so the assertions of QA-SMP-16 hold unchanged from this entry point.

**QA-SMP-30 [WF]** — `Start Assignment (ON)` shows the specified toast — re-baselined on [WF-16 · proposed], applied 2026-08-03
Given `#m-sampleon` is open in its default state (target `All new orders in this period`, start `2026-07-23` `10:00`, `forever` checked) and no `.gtoast` node exists
When I click the green footer button `Start Assignment (ON)` (`#m-sampleon .foot button.btn-green`, which now carries `id="sampStartBtn"`)
Then `#m-sampleon` loses class `open` **and** `#gtoast3` exists, carries class `gtoast`, and is visible
And its first text node reads `✓ Sample assignment started` and its `<small>` reads `All new sales orders from 2026-07-23 10:00 → forever · exactly 1 sample set per order` — the byte-exact copy `[G-2]` and `_review` C-6 require (§3.6.5, the same strings QA-SMP-06 asserts against the real admin).
*(Through v1.2 this was a `(neg)` defect-documentation test asserting that the button closed the modal silently and had no `id`. Both halves were fixed on 2026-08-03, so the assertion was re-baselined onto the shipped toast and the scenario is no longer negative. The id is unchanged.)*

**QA-SMP-31 [WF] (neg)** — Zero selection disables cancel on the wireframe — re-baselined on [WF-17 · proposed], applied 2026-08-03
Given `#m-sampleoff` is open and I uncheck row 1's checkbox so that zero checkboxes are checked
When I attempt to click `#sampCancelBtn`
Then `#sampCancelBtn.disabled === true`, `#m-sampcancel-confirm` does **not** gain class `open`, and no `#gtoast2` node is created
And re-checking row 1 re-enables the button, so the gate tracks the selection rather than the page load ([E-28], §3.7.5; the confirm dialog itself is asserted by QA-SMP-19 and, with its writes, by QA-SMP-20 `[PD-5 · OWNER-PENDING]`).
*(Through v1.2 this scenario documented the opposite — the button was not disabled, no dialog appeared, and the toast fired anyway. The gate and the dialog were both applied on 2026-08-03, so the assertion was re-baselined onto them. It stays `(neg)`: it still asserts that a blocked action produces nothing. The id is unchanged.)*

**QA-SMP-32 [WF]** — M3 default checkbox states
Given `#m-sampleoff` is open
When I read the checkboxes
Then row 1's checkbox is `checked`, row 2's is not, and row 3 has none — a total of exactly 2 checkbox elements in the table body.

**QA-SMP-33 [WF] (neg)** — `forever` clears and disables the end fields — re-baselined on [WF-19 · proposed], applied 2026-08-03
Given `#m-sampleon` is open and the `forever (no end date)` checkbox (`#sampForever`) is `checked`, its shipped default
When I inspect the `End date` and `Time` inputs (`#sampEndDate`, `#sampEndTime`)
Then both are `disabled` and both `value` strings are empty, so neither accepts typed input
And unchecking `#sampForever` re-enables both, while re-checking it clears and disables them again — the sync runs on load and on every change, so `forever` wins over any previously typed end value (§3.6.3, [E-23]).
*(Through v1.2 this scenario documented the opposite — both fields shipped enabled and editable while `forever` was checked. The fix was applied on 2026-08-03 and the assertion was re-baselined onto it. It stays `(neg)`: it asserts a guarded, input-refusing state, in the same shape as QA-SMP-21. The id is unchanged.)*

**QA-SMP-34 [WF]** — Cancel toast uses its own node
Given I have completed at least one cancellation — `#sampCancelBtn` with a period checked, then `#sampConfirmGo` (the confirm step added 2026-08-03 by [WF-17 · proposed]; clicking `#sampCancelBtn` alone no longer creates a toast)
When I inspect the document
Then a node with id `gtoast2` exists carrying class `gtoast`, and the import toast (if it was fired) is a separate node with id `gtoast`, as is the sample-start toast `gtoast3` — the three actions do not share a slot ([WF-18 · proposed], [E-62]).

**QA-SMP-35 [ADMIN] (neg)** — Zero-length period blocked `[E-82]`
Given `#m-sampleon` is open with a start date and time entered
When I uncheck `forever` and set the end datetime equal to the start datetime exactly
Then `Start Assignment (ON)` is disabled with `End must be later than start.` — the comparison is strictly later.

**QA-SMP-36 [ADMIN] (neg)** — A period that has already ended cannot be created `[E-83]`
Given `#m-sampleon` is open
When I enter start `2026-07-01 09:00` and end `2026-07-02 09:00`, both already in the past
Then `Start Assignment (ON)` is disabled with `A period that has already ended cannot be created.` and no `Ended` row is minted.

**QA-SMP-37 [ADMIN]** — Selection resolved at submit `[E-84]` (BR-33)
Given the ON modal is open showing `Selected orders only (5)` and, behind it, 2 of those orders are deselected in the list
When I press `Start Assignment (ON)` with that target
Then 3 orders are assigned and the toast reports `3 orders assigned · …`
And when the resolved selection is empty, the submit is blocked with `No eligible orders are selected.` and nothing is created.

**QA-SMP-38 [ADMIN] (neg)** — Selected order cancelled meanwhile `[E-85]`
Given the ON modal is open with target `Selected orders only`, and one of the selected orders is cancelled behind it
When I press `Start Assignment (ON)`
Then that order is skipped, `[DC-16]` persists with reason `order_cancelled`, and it is counted in `{m} skipped (not eligible)`.

**QA-SMP-39 [ADMIN]** — Cancelling a Scheduled period `[E-87]`
Given a `Scheduled` period that has not started
When I cancel it
Then its status becomes `Cancelled`, `[DC-17]` persists with `old=Scheduled → new=Cancelled`, and no `[DC-14]` has ever existed for it.

**QA-SMP-40 [ADMIN] (neg)** — Concurrent identical Start creates two periods `[E-88]` `[E-32]`
Given operators A and B each have `#m-sampleon` open with identical parameters
When both press `Start Assignment (ON)` at the same moment
Then two distinct periods persist (overlaps are permitted, E-46), neither is silently merged, and every order matched by both still receives exactly one set with a `[DC-15]` recording the suppression.

**QA-SMP-41 [ADMIN]** — Scheduled period activates `[DC-29]`
Given a `Scheduled` period whose start datetime has not yet arrived
When that start datetime arrives
Then its status becomes `Active`, `[DC-29] sample.period_started` persists with `old=Scheduled → new=Active`, and orders created from that instant onward receive sets.

**QA-SMP-42 [ADMIN]** — Timezone and DST `[E-89]` `[E-90]` (BR-31)
Given the admin's operating timezone is configured and an Active period spans a daylight-saving or clock change
When two operators in different local timezones each open `#m-sampleoff` and read that period's row, and sales orders are created either side of the transition
Then both operators read the same wall-clock string on the row, and matching evaluates the absolute instant so no order at the transition is double-assigned or skipped.

**QA-SMP-43 [ADMIN]** — Integration-created orders are matched `[E-91]`
Given an Active `all_new_in_period` period
When a sales order is created through the API rather than the admin UI
Then it receives exactly one sample set and `[DC-14]` persists with reason `period_match`.

**QA-SMP-44 [ADMIN] (neg)** — A period ending does not strip an unshipped order's set `[E-26]`
Given an Active period assigned a sample set to an order that has not yet been outbounded
When that period's end datetime passes and the period becomes `Ended`
Then the order still holds its sample set, its internal invoice and picking artifacts still carry the sample lines, and **zero** unassignment events of any type exist for it — assignment binds at creation time, not at outbound (BR-19, §3.6.6).

**QA-SMP-45 [ADMIN] (neg)** — Order cancelled or refunded after a set was assigned `[E-31]`
Given an order holds a sample set assigned by an Active period
When that order is cancelled, and separately when another such order is refunded
Then the `[DC-14] sample.assigned_to_order` record persists on each order unchanged, **no** `sample.unassigned` event is written, and sample handling on the internal documents follows the order's own lifecycle rather than the period's (§3.6.6).

**QA-SMP-46 [ADMIN] (neg)** — Dual-view divergence `[E-34]` `[G-13]` (BR-8) — cross-reference
Given an order holds exactly one sample set, and this page is `[G-13]`'s primary home (§6.6)
When I read the carrier-facing document produced for that order and the internal invoice and picking artifacts produced for the same order
Then the carrier-facing document shows **only** `(+ sample set)` appended to the **last** product name, and names no sample product and no sample quantity anywhere
And the internal invoice and the picking artifacts **do** carry the "sample set" line (v1: "sample set" only, no type/qty breakdown — `[PD-51]` owner-decided 2026-08-03; existence `[PD-36]` owner-decided 2026-08-04)
And the two views therefore diverge by design; the consuming contracts are the `order-detail` spec (display) and the `ready-to-outbound` spec (picking list), which this scenario cross-references rather than restates (§6.5).

**QA-SMP-47 [ADMIN] (neg)** — Network failure mid `Start Assignment (ON)` `[E-44]` `[DC-13]`
Given `#m-sampleon` is open with a valid target and period
When I click `Start Assignment (ON)` and the network drops after the request is sent
Then either the period exists in full or it does not exist at all — no partial and no ghost period is left in the M3 list
And retrying with the same idempotency key is safe: exactly one `[DC-13] sample.period_created` exists afterwards, and one assignment pass ran `[G-9]` (the sample-side twin of QA-IMP-29).

**QA-SMP-48 [ADMIN]** — A period ends while `[L-M3]` is open `[E-60]` `[DC-18]`
Given `#m-sampleoff` is open with two Active rows checked, one of which is about to reach its end datetime
When that end datetime passes and the list refreshes
Then that row flips `Active → Ended`, loses its checkbox entirely, and `[DC-18] sample.period_ended` persists
And its checked selection is dropped, and the confirm dialog of QA-SMP-20 reports the **adjusted** count — `Cancel 1 assignment period(s)?`, not `Cancel 2 …`.

**QA-SMP-49 [ADMIN]** — Cancel and order creation in the same second `[E-66]` `[DC-14]` `[DC-17]`
Given an Active period and a sales order being created at almost the same instant
When the period is cancelled and an order's creation timestamp precedes the cancellation timestamp, and a second order's creation timestamp follows it
Then the first order receives its set and `[DC-14]` persists for it, the second receives none, and both facts persist alongside the single `[DC-17] sample.period_cancelled` — the server resolves against the cancellation timestamp, never against request arrival order (§3.7.5).

**QA-SMP-50 [ADMIN]** — Selection above the batch ceiling goes asynchronous `[E-86]` `[DC-14]`
Given a `Selected orders only` submission whose resolved selection exceeds the configured batch ceiling
When I press `Start Assignment (ON)`
Then the run is processed asynchronously, the toast reports the **queued** count rather than a completed count, and the `[DC-14]` events land as the batch drains until every eligible order in the resolved selection holds exactly one set (the ceiling value is a §9.3 developer decision; the assertion is the queued-count wording and the eventual completeness).

### 8.3 Block LST — Order list, page furniture and removed features `[L-3]` `[L-4]` `[L-F1]`…`[L-F4]` `[L-F6]`

**QA-LST-01 [WF]** — Placeholder contract text
Given the live wireframe is loaded
When I read `div.anno[style*="dashed"]` inside `.pagepad`
Then it reads `Order list table — same as the current admin (omitted)` with a sub-line containing `Default columns ↔ Columns toggle view, 2,818 total, and pagination — all unchanged.` and `MKT- marketing orders`, and it carries an inline dot rendering `4`.

**QA-LST-02 [WF]** — MKT style tokens exist
Given the live wireframe is loaded
When I read `getComputedStyle(document.documentElement).getPropertyValue('--mkt')` and `--mkt-soft`
Then they are `#7C3AED` and `#F3EEFF`
And the stylesheet defines `.tbl tr.mkt { background: var(--mkt-soft) }`, `.tbl tr.mkt:hover { background:#EBE1FF }`, `.tbl tr:hover { background: var(--blue-soft) }`, and `.mkt-badge { background: var(--mkt); color:#fff; font-weight:800; letter-spacing:.3px; margin-left:5px }`
And per §8.0 rule 5, the hex literals above are the **authored** form: read back out of `cssRules[].cssText` the CSSOM re-serialises `#EBE1FF` as `rgb(235, 225, 255)`, and either form satisfies this assertion.

**QA-LST-03 [WF]** — Header and count `[L-F2]`
Given the live wireframe is loaded
When I read `.ptitle`
Then the `h2` reads `Order Management Dashboard` and `.count` reads `2,818 orders`.

**QA-LST-04 [WF] (neg)** — Bulk Hold Shipment must not exist `[L-3]`
Given the live wireframe is loaded
When I search the entire document — `.filterbar`, `.actionrow`, all three modals, the nav, and every menu — for the case-insensitive substrings `Hold Shipment` and `Bulk Hold`
Then neither appears in any control, and no bulk hold affordance of any kind is present (BR-10)
And legend item 3 nonetheless still contains the sentence `Bulk Hold Shipment button removed` — the negative entry must remain visible in the legend.

**QA-LST-05 [WF] (neg)** — No print or scan surface anywhere on the page
Given the live wireframe is loaded
When I enumerate every `button` and `input` in the document
Then no button label contains `Print`, no input is a scan field or `type="file"`, and the document contains no `<audio>` element (BR-28, BR-29).

**QA-LST-06 [WF]** — Action-row inventory `[L-F4]`
Given the live wireframe is loaded
When I read `.actionrow` left to right
Then it contains a `Select all` checkbox, the text `2 selected` inside `.sel-info` with computed colour `rgb(88, 45, 181)` and `font-weight:700`, then buttons `⧉ Merge Orders`, `Sample Assignment ON`, `Cancel Sample Assignment` in that order.

**QA-LST-07 [WF]** — Filter-bar inventory `[L-F3]`
Given the live wireframe is loaded
When I read `.filterbar` left to right
Then it contains: a date input valued `2026-06-01`, the separator `~`, a date input valued `2026-07-14`, a `.sep`, an input placeholdered `Search (order / product)`, an input placeholdered `Search PIC`, a select whose first option is `All Status`, checkboxes labelled `Order #` (checked) and `Tracking #` (unchecked), a select whose first option is `Country: AU`, a select whose first option is `15`, then buttons `▦ Columns`, `⬇ Export`, `⬇ Yun Export`, `⬆ Import`.

**QA-LST-08 [ADMIN]** — MKT row rendering `[E-36]`
Given a confirmed import created order `MKT-40233`
When I locate its row in the order list and hover it, and hover an adjacent sales row
Then its list row has background `#F3EEFF`, carries an `MKT` badge immediately after the order number, shows the batch PIC in the PIC column, and hovers to `#EBE1FF` while an adjacent sales row hovers to `#E7F1FF`
And the `MKT` badge is rendered as an order-class badge, not with any sourcing-route styling `[G-5]`.

**QA-LST-09 [ADMIN] (neg)** — Merge guard `[E-37]`
Given one `MKT-` order and one sales order are selected
When I click `⧉ Merge Orders`
Then the merge is blocked with `Marketing orders cannot be merged with sales orders.`, **no** `[DC-25] orders.merged` event is written, and the selection is preserved (BR-18, `[PD-59 · OWNER-PENDING]`).

**QA-LST-10 [ADMIN]** — Merge of two sales orders still works `[DC-25]`
Given two sales orders are selected
When I merge them
Then the merge succeeds and `[DC-25] orders.merged` persists with the source ids, the merged id, and the guard outcome.

**QA-LST-11 [ADMIN]** — Free-text PIC is searchable `[E-59]`
Given a batch was imported with the free-text PIC `Agency — Lumi`
When I type `lumi` into `Search PIC`
Then the batch's orders are listed (case-insensitive substring, BR-4) and the PIC value renders as free text rather than resolving to a system user.

**QA-LST-12 [WF]** — Global navigation shell `[L-F6]`
Given the live wireframe is loaded
When I read `.nav` left to right
Then it contains the brand `SkinSeoul`; the menus `Operation AI ▾`, `Catalog Management ▾`, `OMS Center ▾`, `Site Management ▾`, `System Management ▾`, `Customer Management ▾`; the `💬 Comments` button with badge `3`; the user chip `Y` + `Yongwon Ryu`; and `Logout`
And `.nav .navlink` has length `4`, and — reading each span per §8.0 rule 5a, joining across its `<br>` with a single space — the four quick links are `Agent Telemetry`, `Role Assets`, `Shared Asset Health`, `SkinSeoul WP Admin`
And their raw `textContent` values are `AgentTelemetry`, `RoleAssets`, `Shared AssetHealth`, `SkinSeoulWP Admin`, because each span is authored as two lines (`<span class="navlink">Agent<br>Telemetry</span>`) to mirror the live admin nav; `textContent` drops the `<br>` without substituting a space, and `innerText` substitutes `\n`. The two-line markup is deliberate and is **not** a defect.

**QA-LST-13 [WF] (neg)** — No pagination is rendered in the mock (demo limitation)
Given the live wireframe is loaded
When I query `.pager`
Then no element matches — the table and its pagination are deliberately omitted (§2.2). This is not a defect; the product must ship the live admin's pagination unchanged (BR-11), which is asserted only in `[ADMIN]` scenarios.

**QA-LST-14 [ADMIN]** — Empty result set `[E-100]`
Given the Order Management Dashboard is loaded
When I apply a filter set that matches no orders
Then the count reads `0 orders`, the list shows its empty state, and `⬆ Import`, `Sample Assignment ON` and `Cancel Sample Assignment` all remain enabled.

**QA-LST-15 [ADMIN] (neg)** — Free-text PIC is never retroactively resolved `[E-93]`
Given orders carry the free-text PIC `Agency — Lumi`
When a system user with that exact display name is created afterwards
Then those orders still store a free-text PIC, no re-linking event is written, and they still cannot be `@mention`-notified through that field.

**QA-LST-16 [ADMIN] (neg)** — Loading the page writes nothing (BR-34) `[G-8]`
Given I am signed in as any admin user
When I load the Order Management Dashboard and change nothing
Then no persisted event of any kind is created for the page load or its initial data fetch.

**QA-LST-17 [WF] (neg)** — No MKT row is rendered in the mock (guards a QA false negative)
Given the live wireframe is loaded
When I query `tr.mkt` in the page body
Then no element matches, because the order table is omitted — the tokens exist (QA-LST-02) but no row consumes them. A QA run must not report this as a missing MKT treatment; row rendering is asserted by QA-LST-08 `[ADMIN]`.

### 8.4 Block CMT — Comments hub `[L-5]`

**QA-CMT-01 [WF]** — Hub opens and closes from its trigger
Given the live wireframe is loaded
When I click `.nav button[data-open="inbox1"]` (label `💬 Comments`)
Then `#inbox1` has class `open` and the button's `.badge-n` reads `3`
And clicking the same button again removes class `open`.

**QA-CMT-02 [WF]** — Tabs and pane headers
Given `#inbox1` is open
When I read the tab strip and the mentions pane
Then the tabs are `@ Mentions` (class `on`, with an inline badge `3`) and `★ Saved`
And `[data-pane="mentions"] .paneheader` has `firstChild.textContent` equal to `Comments mentioning me · Click to open the order ` and contains exactly one `<small>` whose text is `Mark all read`
And that `<small>` is right-aligned, probed **geometrically** and not by computed margin: with `h = header.getBoundingClientRect()` and `s = small.getBoundingClientRect()`, `h.right - s.right <= 20` and `s.left - h.left >= 100`. (Do **not** assert `getComputedStyle(small).marginLeft === 'auto'` — the rule is authored as `margin-left:auto`, but Chromium resolves auto flex margins to `0px` at the computed-value stage, so that probe reports a false failure.)

**QA-CMT-03 [WF]** — Saved tab
Given `#inbox1` is open
When I click `#inbox1 .tabs button[data-tab="saved"]`
Then the pane `[data-pane="saved"]` is displayed with header `Saved comments · Click to open the order` and hint `Unstar to remove from the list`, containing exactly one row, for `Order MKT-40218`
And the pane `[data-pane="mentions"]` is hidden.

**QA-CMT-04 [WF]** — Search hides the tabs and renders a result header
Given `#inbox1` is open
When I type `MKT` into `#inbox1 .csearch input` (placeholder `🔍 Search all comments — order no. · author · text`)
Then `#inbox1 .tabs` has `display: none`, the pane `[data-pane="csr"]` is displayed, and its header reads exactly `3 results · newest first · click to open the order`.

**QA-CMT-05 [WF] (neg)** — Search with no hits `[E-38]`
Given `#inbox1` is open
When I type `zzzz` into the search input
Then `[data-pane="csr"] .empty` reads exactly `No matching comments`, `[data-pane="csr"] .it` has length `0`, and `[data-pane="csr"] .paneheader` reads exactly `0 results · newest first · click to open the order`.
(The result header is written on every query, hit or miss, so the whole pane's `textContent` is `0 results · newest first · click to open the orderNo matching comments`. The empty state lives *inside* the pane alongside the header; assert the two nodes separately, never the pane as one string.)

**QA-CMT-06 [WF]** — Clearing the search restores the tabs
Given a search query is active
When I clear the input
Then `#inbox1 .tabs` is displayed again, `[data-pane="csr"]` is hidden, and the pane of the tab that carries class `on` is displayed.

**QA-CMT-07 [WF]** — Star toggle
Given `#inbox1` is open on `@ Mentions`
When I click the `★` in the row for `Order MKT-40233`
Then that button gains class `on` and its computed colour is `rgb(245, 158, 11)`; clicking again removes the class and returns it to `rgb(187, 186, 190)`.

**QA-CMT-08 [WF] (neg)** — Search input cannot inject markup `[E-48]`
Given `#inbox1` is open
When I type `<b>x` into the search input
Then `[data-pane="csr"] .empty` reads exactly `No matching comments` and `document.querySelectorAll('[data-pane="csr"] b').length === 0` — the query is escaped, never parsed as HTML.

**QA-CMT-09 [ADMIN]** — Star and unstar persist `[DC-21]` `[DC-22]`
Given a comment is unstarred
When I star it and then unstar it
Then `[DC-21] comment.starred` and `[DC-22] comment.unstarred` persist in that order with my actor id, the comment id, and timestamps.

**QA-CMT-10 [ADMIN]** — Mark all read `[E-39]` `[DC-23]` `[DC-24]`
Given 3 unread mentions
When I click `Mark all read`
Then every `.unread` tint is removed, the nav badge clears to `0` without a page reload, and `[DC-24] comment.mark_all_read` persists with the 3 comment ids and `count=3`
And opening a single unread comment separately persists `[DC-23] comment.read`.

**QA-CMT-11 [ADMIN]** — Mention routing `[DC-19]` `[DC-20]`
Given I am viewing order `MKT-40233`
When I post the comment `@Yongwon please check`
Then `[DC-19] comment.posted` persists with the text and the mention list
And `[DC-20] comment.mention_notified` persists with channel `#fulfillment-admin-comments` (`C0BMGEWM5QA`), the Slack ts, the mentioned user and outcome `delivered`
And the Slack message body carries the entity no., the comment text, the time, the author, the `@mention` and a deep link (§6.1).

**QA-CMT-12 [ADMIN] (neg)** — Slack failure never blocks `[E-40]`
Given a comment carrying an `@mention` is being posted
When Slack returns an error for the mention dispatch
Then the comment still exists and is visible in the hub, `[DC-20]` persists with outcome `failed` and a retry count, and nothing is rolled back (BR-24, `[PD-4 · OWNER-PENDING]`).

**QA-CMT-13 [ADMIN] (neg)** — No edit or delete affordance `[G-7]` `[PD-3 · OWNER-PENDING]`
Given any comment row in the hub or on an entity
When I enumerate that row's controls and every API path this page exposes for that comment
Then no edit control and no delete control is rendered, and no API path exposed by this page mutates or removes an existing comment (BR-23).

**QA-CMT-14 [ADMIN]** — Badge overflow `[E-64]`
Given 120 unread mentions exist for me
When I read the nav badge on `💬 Comments`
Then it renders `99+`.

**QA-CMT-15 [WF]** — Numeric-order search returns sales orders only
Given `#inbox1` is open
When I type `421` into the search input
Then the header reads `2 results · newest first · click to open the order` and the rows are `Order 421771` and `Order 421502`, in that order.

**QA-CMT-16 [WF]** — Author search and `<mark>` highlighting
Given `#inbox1` is open
When I type `Harshit` into the search input
Then the header reads `2 results · newest first · click to open the order`
And each result row contains a `<mark>` element whose text is `Harshit`, with computed `font-weight` `700`
And the rows are `Order MKT-40233` then `Order MKT-40191`.

**QA-CMT-17 [WF]** — Results are ordered newest-first
Given `#inbox1` is open
When I type `4` into the search input
Then the header reads `5 results · newest first · click to open the order` and the rows appear in the order `MKT-40233`, `MKT-40218`, `421771`, `MKT-40191`, `421502` — descending by recency, not by order number.

**QA-CMT-18 [WF] (neg)** — `Mark all read` is inert in the mock (demo limitation)
Given `#inbox1` is open with three `.it.unread` rows
When I click the `Mark all read` control in the mentions pane header
Then nothing changes: the rows keep class `unread` and the nav badge still reads `3`. This is a demo limitation (`_wireframe-fixes` §E), not a defect; the behaviour is asserted by QA-CMT-10 `[ADMIN]`.

**QA-CMT-19 [WF]** — Unread and saved states in the demo data
Given `#inbox1` is open on `@ Mentions`
When I read the three rows
Then all three carry class `unread`, they reference `Order MKT-40233`, `Order MKT-40218` and `Order 421771`, and only the `MKT-40218` row's `★` carries class `on` — matching the single row in the `★ Saved` pane.

**QA-CMT-20 [WF]** — The hub closes on an outside click — re-baselined on [WF-21 · proposed], applied 2026-08-03
Given `#inbox1` is open
When I click on `.pagepad` (anywhere outside the dropdown)
Then `#inbox1` loses class `open`
And a click **inside** the panel — for example on `#inbox1 .csearch input` or on a tab button — leaves it open, because the `document`-level handler bails on `e.target.closest('.inboxdd')` and the pre-existing `stopPropagation` guards (`.csearch` `onclick`, the hub trigger, the tab buttons, the stars) are now live rather than dead code (§3.10, [E-97]).
*(Through v1.2 this was a `(neg)` defect-documentation test asserting that the panel survived an outside click while carrying guards for a handler that did not exist. The handler was added on 2026-08-03, so the assertion was re-baselined onto it and the scenario is no longer negative. The id is unchanged.)*

**QA-CMT-21 [WF]** — Corpus mixes marketing and sales entities
Given `#inbox1` is open
When I type `4` into `#inbox1 .csearch input` — the query that matches every row in the demo corpus (the same input QA-CMT-17 uses)
Then `[data-pane="csr"] .it` has length `5` and the rows read `Order MKT-40233`, `Order MKT-40218`, `Order 421771`, `Order MKT-40191`, `Order 421502` — three `MKT-` order numbers and two plain numeric order numbers in one list, so the hub is not scoped to marketing orders (§3.10).
(The empty query is **not** a valid input here: clearing the box hides `[data-pane="csr"]` and restores the tab strip, so the corpus cannot be read at all — QA-CMT-06.)

**QA-CMT-22 [ADMIN]** — Cross-entity click-through `[E-92]` (BR-32)
Given the hub surfaces a comment whose entity is an inbound request and another whose entity is an unrecognized-pool item
When I click each row
Then the first opens the Inbound Request list focused on that request and the second opens Unrecognized Tracking focused on that pool row — or, if that pool item has already been resolved, the matched order instead `[PD-67 · OWNER-PENDING]`
And a comment on an order cancelled after it was written still opens that order in its cancelled state `[E-49]`.

**QA-CMT-23 [ADMIN] (neg)** — Session expiry while the hub is open `[E-99]`
Given the hub is open
When my session expires and I interact with the hub
Then it renders an unauthenticated state and prompts re-authentication — it must **not** render an empty list with a zero badge, which would read as "no mentions".

**QA-CMT-24 [ADMIN] (neg)** — Slack channel archived or renamed at dispatch time `[E-50]` `[DC-20]`
Given `#fulfillment-admin-comments` (`C0BMGEWM5QA`) has been archived or renamed
When a comment carrying an `@mention` is posted
Then the comment commits and is visible in the hub regardless, the dispatch persists as `[DC-20] comment.mention_notified` with outcome `failed` and the channel id `C0BMGEWM5QA` recorded, and nothing is rolled back or blocked (BR-24, `[PD-4 · OWNER-PENDING]`; retry policy is a §9.3 developer decision).

### 8.5 Block GBL — Global contracts `[L-F1]` `[L-F5]` `[G-2]` `[G-8]` `[G-9]` `[G-15]`

**QA-GBL-01 [WF]** — Legend closing paragraph `[L-F1]`
Given the live wireframe is loaded
When I read `.legend > p`
Then it contains `Global nav · filter bar (dates · Search · PIC · Status · Order#/Tracking# checkboxes · Country · page size) · Merge Orders · Export/Yun Export · 2,818 total · pagination all stay as in the live screen.` and `Sample assignment was redesigned 2026-07-23 as a simple ON/OFF (no product-type selection)`.

**QA-GBL-02 [WF]** — Toast placement and styling `[L-F5]`
Given any confirming action has fired
When I inspect the `.gtoast` node
Then it is `position: fixed` at `top: 16px; right: 16px` with `z-index: 200`, background `rgb(25, 135, 84)`, white text at `font-weight: 700` and `font-size: 13.5px`, and its optional `<small>` renders at `11.5px` with `opacity: .9`.

**QA-GBL-03 [WF] (neg)** — No reload after any action `[E-43]` `[G-2]`
Given the live wireframe is loaded and `window.__qaSentinel = 'om'`
When I open each of the three modals, click `#mktConfirm`, reopen and click `#sampCancelBtn`, open and close the Comments hub, and toggle `#annoToggle`
Then `window.__qaSentinel === 'om'` throughout — no full-page refresh occurs anywhere on this page. The `[G-2]` refresh exception named for RTO Bulk Outbound does not apply here.

**QA-GBL-04 [WF] (neg)** — Every dismissal path creates nothing
Given `#m-import` is open
When I click the overlay backdrop (`#m-import` itself, outside `.modal`), then reopen and click `header .x`, then reopen and click the footer `Cancel`
Then the modal closes each time, `document.querySelectorAll('.gtoast').length` stays `0`, and no confirming behaviour fires — dismissal is not a confirming action (§5.4 items 1).

**QA-GBL-05 [ADMIN]** — Actor recorded on every mutation `[G-8]` `[G-15]`
Given I am signed in as any admin user
When I confirm an import, start a period, cancel a period, merge orders and star a comment
Then every resulting event in §5 carries my actor id and a timestamp, and no action is refused for role reasons in v1 (BR-22, `[PD-1 · OWNER-PENDING]`).

**QA-GBL-06 [ADMIN] (neg)** — Declared NON-events are not written `[G-8]` §5.4
Given I am signed in on the Order Management Dashboard
When I change the date filter, toggle `▦ Columns`, page through the list, sort a column, select and deselect rows, open and close all three modals, switch comment tabs, and type a search query including a zero-hit query
Then **no** persisted event is created for any of these actions.

**QA-GBL-07 [ADMIN]** — Uploaded source file retrievable (§5.5)
Given a confirmed batch
When I open its batch record and download the retained source file
Then the original `.xlsx` is retrievable from the batch record and its SHA-256 matches the hash stored in `[DC-2]`.

**QA-GBL-08 [ADMIN] (neg)** — No Slack route fires for import or sample actions (§6.2)
Given I am signed in on the Order Management Dashboard
When I confirm an import and then start and cancel a sample period
Then no Slack message is dispatched to any channel for these actions, no dispatch event is persisted other than for comment mentions, and in particular nothing reaches `#unrecognized-tracking`, `#wholesale-ops` or `#partnership-kr`.

**QA-GBL-09 [WF] (neg)** — Concurrent toasts are stacked, never overlaid — re-baselined on [WF-18 · proposed], applied 2026-08-03
Given the live wireframe is loaded
When I click `#mktConfirm` and then, within the 2 600 ms window, open `#m-sampleoff`, click `#sampCancelBtn` and confirm with `#sampConfirmGo`
Then `document.querySelectorAll('.gtoast').length === 2` — ids `gtoast` and `gtoast2` — and both compute `display: block`
And they do **not** overlap: `stackToasts()` places the first visible node at `top: 16px` and each later one at `previous.top + previous.offsetHeight + 8px` (in the demo copy that is `16px` and `86px`), so their bounding boxes never intersect while both are visible — the explicit-stack branch `[L-F5]` permits, in place of a single replacing slot `[E-62]`.
*(Through v1.2 this scenario documented the defect: two independent nodes pinned to the same fixed coordinates. The stack was applied on 2026-08-03 and the assertion was re-baselined onto it. It stays `(neg)`: it asserts an absence — that no two toasts occupy the same space. The id is unchanged. The `86px` figure is the demo-copy measurement, not a contract; the contract is the offset formula.)*

**QA-GBL-10 [WF]** — `Esc` dismisses the topmost overlay, else the Comments hub — re-baselined on [WF-20 · proposed], applied 2026-08-03
Given `#m-import` is open
When I dispatch a `keydown` event with `key: 'Escape'` on `document`
Then `#m-import` loses class `open`, and the same holds one at a time for `#m-sampleon`, `#m-sampleoff` and the confirm overlay `#m-sampcancel-confirm`
And with `#m-sampcancel-confirm` open on top of `#m-sampleoff`, one `Escape` closes only the confirm overlay and a second closes `#m-sampleoff` — the handler unwinds the **topmost** `.overlay.open` per press (§8.0 rule 4)
And with no overlay open and `#inbox1` open, one `Escape` closes `#inbox1`
And no dismissal creates anything: `document.querySelectorAll('.gtoast').length` is unchanged throughout (§3.2.6, §3.10, [E-97]).
*(Through v1.2 this was a `(neg)` defect-documentation test asserting that no `keydown` listener existed anywhere in the file. The listener was added on 2026-08-03, so the assertion was re-baselined onto it and the scenario is no longer negative. The id is unchanged.)*

**QA-GBL-11 [WF] (neg)** — Wireframe-only chrome inventory (must not ship)
Given the live wireframe is loaded
When I enumerate the chrome
Then `.wf-bar` exists with the four buttons `Modal: Marketing Import`, `Modal: Sample Assignment ON`, `Modal: Cancel Sample Assignment`, `Hide annotations`; `.dot` elements exist; and `.legend` exists
And all of these are wireframe navigation aids that must be absent from the product (§2.3). A QA run against the real admin must assert their absence.

**QA-GBL-12 [WF]** — Annotation toggle
Given the live wireframe is loaded with annotations shown
When I click `#annoToggle`
Then `document.body` gains class `no-anno`, every `.dot` and `.legend` computes to `display: none`, and the button text becomes `Show annotations`; clicking again restores both and the text returns to `Hide annotations`.

**QA-GBL-13 [WF] (neg)** — No audio anywhere `[G-3]` (BR-28)
Given the live wireframe is loaded
When I search the document for `<audio>`, `AudioContext`, `webkitAudioContext`, `speechSynthesis` and `SpeechSynthesisUtterance`
Then none is present — this page has no outbound-class button and no scan warning, so neither the send sound `[PD-2 · OWNER-PENDING]` nor the TTS alert applies here (`_review` C-5).

**QA-GBL-14 [WF] (neg)** — No scanner surface `[G-1]` (BR-28)
Given the live wireframe is loaded
When I enumerate every `input` and every `.focus()` call site in the document
Then none is a scan field, no element carries `autofocus`, `document.activeElement` on load is `document.body` (nothing is focused), and no input carries select-on-focus behaviour
And **no code path returns focus to a scan field after an action** — the `[G-1]` scan-focus-retention invariant has no surface here (BR-28)
And the document's only two `.focus()` call sites are the custom-input affordances on `#otCustom` (§3.2.2) and `#picCustomIn` (§3.2.3), which QA-IMP-06 and QA-IMP-09 require. They are ordinary text inputs revealed by a chip toggle, not scan surfaces, and their presence is **not** a `[G-1]` violation. A runner must not read "no focus is ever moved" into this scenario: that reading contradicts QA-IMP-06 and QA-IMP-09 and cannot hold against any conformant implementation.

**QA-GBL-15 [WF]** — Layout minimums `[E-96]`
Given the live wireframe is loaded
When I read the computed styles
Then `.mock` has `min-width: 1240px`, `.tbl` has `min-width: 1180px`, and `.mockwrap` has `overflow-x: auto` — horizontal scroll below those widths is the specified behaviour, not a defect.

**QA-GBL-16 [ADMIN] (neg)** — Stale second tab cannot write from stale state `[E-94]`
Given two tabs of this page are open and tab A confirms an import
When tab B, still showing the pre-import list, attempts a confirming action against stale data
Then the server's revalidation rejects it with a non-green toast and reloads the affected view; nothing partial is written (BR-26, `[PD-6 · OWNER-PENDING]`).

**QA-GBL-17 [ADMIN]** — Toast above an open modal `[E-95]`
Given any overlay on this page is open
When a confirming action fires
Then the toast renders above the overlay (`z-index: 200` vs `80`) and is fully visible, not clipped.

**QA-GBL-18 [ADMIN]** — Keyboard operation of the modals `[E-98]`
Given the Order Management Dashboard is loaded
When I open any of the three modals with the keyboard, Tab through it, and then close it
Then focus moves into the modal on open, Tab cycles within it without escaping to the page behind, and closing returns focus to the control that opened it.

### 8.6 Data-capture coverage matrix (every `[DC-n]` has an asserting Then-clause)

| DC | Asserted by | DC | Asserted by |
|---|---|---|---|
Every cell below was re-checked against the cited scenario's **body**: a scenario is listed only if its Then-clause names that `[DC-n]` explicitly. Where a scenario asserts that the event was *not* written, the cell is marked `(absence)`.

| DC | Asserted by | DC | Asserted by |
|---|---|---|---|
| DC-1 | QA-IMP-04 | DC-16 | QA-SMP-10, QA-SMP-13, QA-SMP-38 |
| DC-2 | QA-IMP-21, QA-IMP-31, QA-IMP-44, QA-IMP-56, QA-IMP-57, QA-GBL-07 | DC-17 | QA-SMP-14, QA-SMP-20, QA-SMP-26, QA-SMP-39, QA-SMP-49 |
| DC-3 | QA-IMP-22, QA-IMP-31, QA-IMP-53 | DC-18 | QA-SMP-27, QA-SMP-48 |
| DC-4 | QA-IMP-30 | DC-19 | QA-CMT-11 |
| DC-5 | QA-IMP-30 | DC-20 | QA-CMT-11, QA-CMT-12, QA-CMT-24 |
| DC-6 | QA-IMP-27 | DC-21 | QA-CMT-09 |
| DC-7 | QA-IMP-29, QA-IMP-32, QA-IMP-47 | DC-22 | QA-CMT-09 |
| DC-8 | QA-IMP-31, QA-IMP-47, QA-IMP-58 | DC-23 | QA-CMT-10 |
| DC-9 | QA-IMP-27, QA-IMP-33 | DC-24 | QA-CMT-10 |
| DC-10 | QA-IMP-27, QA-IMP-52, QA-IMP-60 | DC-25 | QA-LST-09 (absence), QA-LST-10 |
| DC-11 | QA-IMP-27, QA-IMP-51, QA-IMP-55 | DC-26 | QA-IMP-34, QA-IMP-59 |
| DC-12 | QA-IMP-27 | DC-27 | QA-IMP-34 |
| DC-13 | QA-SMP-06, QA-SMP-47 | DC-28 | QA-IMP-28, QA-IMP-48, QA-SMP-22 |
| DC-14 | QA-SMP-10, QA-SMP-12, QA-SMP-13 (absence), QA-SMP-43, QA-SMP-45, QA-SMP-49, QA-SMP-50 | DC-29 | QA-SMP-41 |
| DC-15 | QA-SMP-10, QA-SMP-12, QA-SMP-40 | | |

**Asserted absences** (a Then-clause requiring that nothing was written): no unassignment event on cancel or end (QA-SMP-14, QA-SMP-44) · no unassignment event when the order itself is cancelled or refunded (QA-SMP-45) · no sample set on an `MKT-` order (QA-SMP-13) · no Slack route for import or sample actions (QA-GBL-08) · no persistence for any declared NON-event (QA-GBL-06) · no event on page load (QA-LST-16) · no `[DC-25]` when the merge guard fires (QA-LST-09) · no `[DC-17]` when the confirm dialog is dismissed (QA-SMP-20) · no second batch on repeat submission (QA-IMP-28, QA-IMP-48) · no ghost period after a mid-submit network failure (QA-SMP-47) · no order created from any blocked file (QA-IMP-53, QA-IMP-54) · no `order.status_changed` from this page, established by the absence of the control (QA-LST-04).

---

## 9. Out of Scope & Open Questions

### 9.1 Open questions with NO provisional default (owner must decide; no behaviour is specified)

| ID | Question | Why it is not decided | Blocking |
|---|---|---|---|
| **`[PD-51]`** | **RESOLVED — OWNER-DECIDED 2026-08-03.** Where is the sample-set definition configured? Answer: v1 makes no sample distinction — internal invoice and picking artifacts print **"sample set" only** (no type, no per-type quantity); a definition source becomes necessary only when sample types are introduced (follow-up work). `[G-13]` amended in `_global-rules.md` v1.1. | (was: no input document named a source for the sample-set definition) | Nothing on this page. Unblocks the internal-invoice and picking-list *content*. `_wireframe-fixes` WF-9 was applied 2026-08-03 and its last gate, `[PD-36]`, was owner-decided 2026-08-04 — nothing outstanding |
| **`[PD-55]`** | **RESOLVED — OWNER-DECIDED 2026-08-03.** What unblocks a `Not connected — contact the Fulfillment Center` order, and who owns the follow-up? Answer: **manual coordination — contact the fulfillment person in charge via Slack**; v1 ships no in-admin release/carrier-assignment UI and no automated Slack route. | (was: no screen offered a manual carrier assignment and no Slack route existed) | Nothing — the recovery path is defined as manual; the flagged state and its persistence stand (`[DC-11]`, [E-7], [E-80]) |

Owner questions that **do** have a provisional default are not repeated here — they live in `_provisional-decisions.md` and are tagged `[PD-n · OWNER-PENDING]` inline where the behaviour appears. This page's **behaviour-bearing** PD dependencies are **PD-1, PD-2, PD-3, PD-4, PD-5, PD-6, PD-7, PD-20, PD-22, PD-27, PD-28, PD-35, PD-36, PD-52, PD-53, PD-54, PD-56, PD-57, PD-58, PD-59, PD-63, PD-67, PD-80** (23), plus the two NO-DEFAULT entries above. This is a **dependency** list, not a pending list: **PD-1…PD-7** were owner-decided 2026-08-03 and keep their inline tags under the `HANDOFF.md` convention that the register ruling supersedes a stale tag, while **PD-36** was owner-decided 2026-08-04 and had its inline tags **removed**. Both stay in the list because the behaviour still rests on them, so neither count below changes. One further PD id appears in this document without being a dependency: **`[PD-9]`** is cited once, untagged, in §10's 2026-08-03 "Program-wide item 16" row purely as a **non-applicable cross-reference** — it exists to stop a reader confusing inbound-side carrier auto-record (not supported) with this page's import-side carrier auto-assignment (BR-3). Reversing PD-9 changes nothing here. A `[PD-n` token extraction over this document therefore yields 26 distinct ids: 23 + 2 NO-DEFAULT + PD-9.

**Three of those are applied beyond their register page list, deliberately and reversibly:**

| PD | Register lists | Applied here to | Reversal impact if the owner rejects the PD |
|---|---|---|---|
| **PD-5** | TM, CL, OD, INV | The confirm dialog before `Cancel Selected Periods` (§3.7.5, BR-25) | Remove the confirm dialog; the toast and `[DC-17]` stay. QA-SMP-20 is deleted, QA-SMP-21's dialog clause is dropped |
| **PD-6** | VO, OD, RTO, INV, TM, CL | Confirm-time revalidation of the import draft and of the period list (§3.2.5 step 2, BR-26) | Remove the revalidation step; stale drafts then commit as previewed. QA-GBL-16 is deleted |
| **PD-63** | TM, VO | The program-wide "no photo capture" negative contract (§3.8.1) | Nothing changes on this page — it never had a photo affordance; the row exists only to stop reintroduction by analogy |

`[PD-2]` is likewise cited as the *reason no sound applies here* rather than as behaviour: if PD-2 were reversed to "sound on View Orders and RTO only", this page's outcome is unchanged, because it has no outbound-class button either way.

**Spec-level defaults awaiting owner sign-off (not in the PD register).** Three business rules added in v1.1 were authored by this spec rather than adopted from `_provisional-decisions.md`. They are written in §4 as decided behaviour because a spec cannot ship a hole, but no owner has ruled on them and none carries a `[PD-n]` id. They are surfaced here so that an owner reading §9 sees every open question, not only the registered ones. Each becomes a normal `[PD-n · OWNER-PENDING]` citation the moment it is entered in the register.

| Rule | What it decides | Why it needs owner sign-off | Reversal impact |
|---|---|---|---|
| **BR-31** | One operating timezone: every datetime on this page is entered, evaluated and displayed in the admin's single configured zone; storage is UTC; matching evaluates the absolute instant; **no per-user timezone rendering in v1** | It has company-wide consequence by its own rationale — a sample period is a company-wide switch, and two operators reading different windows from one row makes the one-set invariant untestable. Only the *zone value* is a §9.3 dev decision; the *policy* is asserted here | If the owner wants per-user rendering: §3.6.2's timezone sentence, [E-89], [E-90] and QA-SMP-42 change; `[DC-13]`'s `operating timezone` payload field stays either way as the audit anchor |
| **BR-33** | `Selected orders only` resolves its order set **at submit time**, not at modal-open time; the open-time `{n}` is a label only | It changes *which orders get sampled* when the list moves behind the modal. The alternative (freeze the set at open) is defensible and would make [E-84] and QA-SMP-37 assert the opposite | If reversed to open-time freeze: §3.4, §3.6.5, [E-84], QA-SMP-37 and `[DC-13]`'s order-id-list semantics all invert |
| **BR-34** | Loading the page mutates nothing — no event on page load or initial fetch | `[G-8]` scopes capture to operator-initiated actions, but "was this screen opened" is a plausible audit ask that no input document rules on | If reversed: add a page-view event to §5 and delete §5.4 item 12 and QA-LST-16 |

**Open question raised by the 2026-08-03 pre-handoff review (not in the PD register; no PD id issued).** Numbered `OQ-n` in the form the sibling specs use (`stock-status`, `ready-to-outbound`, `view-orders`). It is listed here rather than in §9.2 because §9.2 of this document is the *out-of-scope* list, and this is an undecided question, not a delegation.

| ID | Question | Why it is not decided | Blocking |
|---|---|---|---|
| **`[OQ-1]`** — **RESOLVED, OWNER-DECIDED 2026-08-04** | **What monetary amount, if any, does an order created by the Marketing Order Import carry?** **Answer: `0`, not null.** Null forces every downstream consumer to handle absence and one of them will coalesce it wrongly; a catalogue-derived figure invents revenue that never occurred. **Binding rider: these orders are excluded from sales reporting by their `MKT-` order type, never by `amount = 0`.** An `amount > 0` filter would also drop a fully-discounted real order and would re-admit a marketing order that later carries a nominal value — the same settlement-separation principle already stated in BR-2 / BR-17. Note for finance, not a spec constraint: the **cost is not always 0**. Free-of-charge stock enters at unit cost `0` (`inbound-request.md` `BR-5`), but when a SKU holds both free and paid receipts the FIFO active receipt ([G-5]) decides which is consumed, so a marketing order can draw paid stock at real cost.  Original framing, kept so the question the answer resolves stays legible: The template's seven columns are fixed by the dev team and include **no price, value or currency field** (§3.2.1), so the operator cannot supply one, and `[DC-9] order.created` names no monetary field either (§5.1). Nothing states what the created order's amount holds — zero, null, a catalogue-derived figure, or no such field at all. | No input document, no `_global-rules` clause and no owner decision addresses it, and no default is written here on purpose: these orders are **non-sales** orders (§1.1) kept settlement-separate from sales orders (BR-2, BR-17), so picking a number would be inventing a finance and customs policy this spec has no basis for. | **Nothing on this page** — no control, gate, validation, event or QA scenario reads an amount, and every §3 behaviour is specifiable without one. It blocks the **downstream** readers of an amount: carrier export / customs declaration on physically shipped parcels, and finance settlement separation. Whoever answers it owns the resulting payload line on `[DC-9]`, which keeps its ID. |

### 9.2 Explicitly out of scope for this spec

- **Label and invoice layouts** — the physical rendering of `(+ sample set)` on carrier-facing data and of the sample lines on internal invoice/picking artifacts is **Phase 3-1**, to be discussed with the owner after Phase 3. This spec specifies the *behaviour* (BR-8), never the layout.
- **The order list table's internals** — column set, sorting, row menus, pagination mechanics: unchanged contract (BR-11). Re-specifying them would invite a redesign of a surface that is not changing.
- **Procurement Hub** — excluded from this planning round in full on 2026-08-02 (owner). No sheet pull, no push, no reference.
- **Hold behaviour** — owned by the `order-detail` spec (`Change Status → on-hold`; status matrix `[PD-28 · OWNER-PENDING]`, hold reason `[PD-20 · OWNER-PENDING]`).
- **RTO Marketing-view rendering and Bulk Outbound eligibility** — owned by the `ready-to-outbound` spec (`[PD-35 · OWNER-PENDING]`).
- **`✕ Cancel Order` on an MKT order** — the per-order cleanup path referenced by BR-14 is owned by the `order-detail` spec (`[PD-22 · OWNER-PENDING]`).
- **RBAC / role matrix** — post-v1 owner decision `[G-15]` `[PD-1 · OWNER-PENDING]`.
- **JIT and JIT residual stock** (mandatory-inclusion item 11, stated explicitly rather than left silent — see §6.7) — **JIT never appears on this screen.** No JIT sourcing route is selectable here, and no residual-stock figure is computed, displayed, filtered, exported or reported here. JIT is not a requestable inbound route `[G-5]`, and residual-stock handling is owned by the `stock-status` spec. Nothing on this page may surface a residual figure by analogy with the order table's route badges.
- **Line-based location filtering and audit-mode-only visibility** (mandatory items 9 and 10) — no line-item view, no location concept and no audit mode exists here `[G-14]`; owned by `stock-status` and `view-orders` (§6.7).
- **Wireframe edits** — `[WF-15 · proposed]` … `[WF-21 · proposed]`, registered in `_plans/_wireframe-fixes.md` **§F** (appended 2026-08-03), were backlog items for a separate wireframe-edit pass, deployed via `/wf-deploy order-management`, and were **not** to be applied while specs were being written. That pass ran on 2026-08-03 under owner approval: the register records all seven as `APPLIED 2026-08-03` and the live drawing carries them. This bullet is kept as the record of the sequencing rule, which still binds any *future* wireframe edit raised by this spec. The `· proposed` suffix is now only a frozen part of the ID token — IDs are never renumbered once cited (§8.0 rule 7, §2.4).

### 9.3 Decisions delegated to development (a default is stated; these are NOT owner questions)

| Area | Item | Recommended default |
|---|---|---|
| Import | Idempotency key construction and TTL `[G-9]` | file hash + operator id + monotonic nonce |
| Import | Max row count and max file size, and the message that names the limit `[E-16]` | dev-configured; the limit value appears verbatim in the error |
| Import | Header-matching policy for renamed/reordered/extra columns `[E-17]` | match by header name; ignore extra columns; reject on a missing required header |
| Import | Country-name → ISO-2 normalisation table `[E-67]` | ISO 3166 English short names plus common aliases; anything else is a row error |
| Import | Numeric coercion rules for Qty `[E-69]` | strip thousands separators and a leading apostrophe; reject non-integers |
| Import | `MKT-#####` numbering scheme and its collision-safe source `[E-41]` | central sequence, never per-session |
| Import | Template version stamp and outdated-template detection `[E-71]` | version stamp in a hidden cell of the template |
| Import | Uploaded-file retention horizon and storage location | retained at least as long as the orders it created |
| Import | Whether within-file duplicate `recipient + SKU` rows warn `[E-9]` | allow silently; marketing sends multiples on purpose |
| Import | Draft-batch TTL after a session expires `[E-74]` | long enough for one re-authentication round trip |
| Sample | `forever`-vs-end-date UI mechanic (clear on check vs disable and ignore) `[E-23]` | clear **and** disable |
| Sample | Which period is recorded as the assigner when two overlap `[E-24]` | first match by start datetime — affects audit attribution only, never the one-set invariant |
| Sample | Whether skipped already-assigned orders are surfaced beyond the toast count `[E-33]` | the toast count is sufficient in v1 |
| Sample | Batch ceiling above which a `Selected orders only` run goes asynchronous `[E-86]` | dev-configured; the toast reports the queued count |
| Timezone | The concrete operating-timezone value behind BR-31 | the fulfilment centre's zone, configured once system-wide; never per user in v1 |
| Toasts | Duration, single-slot replacement vs stacking, exact failure copy `[E-62]` | single slot, replace; the wireframe uses 2 600 ms |
| Comments | Search debounce interval and index scope | 250 ms debounce; index entity no., author, text |
| Comments | Freshness of the unread badge (poll vs push) | poll on an interval in v1 |
| List | Sticky columns on a wide table; `Search PIC` prefix vs substring | substring, case-insensitive |
| Egress | CSV/XLSX encoding and column set for `⬇ Export` / `⬇ Yun Export` | UTF-8 with BOM |
| Permissions | Hide vs disable for future role-gated controls `[E-42]` | follow the existing admin convention when RBAC lands |
| Free-text PIC | Disambiguation when the string equals a system user's display name `[E-59]` `[E-93]` | store as free text; never auto-resolve, never retroactively re-link |
| Idempotency | How a suppressed duplicate surfaces to the operator `[DC-28]` | re-show the original toast |
| Accessibility | Focus trap, focus return, and ARIA roles on the three modals `[E-98]` | standard dialog semantics; focus returns to the trigger |

---

## 10. Decision Log

Every decision that shaped this screen, dated, including reversals and removals. Nothing recorded here may be silently dropped in a later round.

| Date | Decision | Detail | Where it lands |
|---|---|---|---|
| 2026-07-09 | Order Management Dashboard entered the WMS 2.0 wireframe programme as page 5 (specs G + F) | Reworked from a real screen capture: real filter bar, default ↔ `▦ Columns` view, MKT rows, and three modals — Import, sample assignment, and **Hold** | §2, `[L-4]` |
| 2026-07-09 | The order list table is treated as unchanged and omitted from the wireframe | Avoids re-specifying a surface that is not changing | BR-11, `[L-4]` |
| 2026-07-21 | Program-wide: the Deleo Tracking No. asymmetry between View Orders and Order Detail settled as deliberate | No effect on this page; recorded because `_review` §1 lists it as an adjudicated non-issue that must not be "fixed" | — |
| 2026-07-22 | **Sample assignment recorded as "removed"** | Stale note — superseded the next day. Recorded verbatim so the reversal chain is legible | R-1 |
| 2026-07-23 | **Sample assignment reinstated and redesigned as a simple ON/OFF** | Multiple, possibly overlapping periods; start datetime + end datetime or `forever`; **no sample-type selection**; ON modal (M2) and Cancel modal (M3) | BR-6, `[L-2a]`, `[L-2b]`, `[L-M2]`, `[L-M3]` |
| 2026-07-23 | **Marketing import stock validation dropped** (owner decision) | Import may precede inbound; MKT orders appear in the RTO Marketing view regardless of stock. Notion §G's "error if the product is not in the warehouse" is struck and must not appear in UI copy | BR-1, §3.8.1, QA-IMP-19, QA-IMP-23, R-2 |
| 2026-07-23 | Marketing Order Import (M1) confirmed as a 4-step flow | Template → Order Type → PIC → Upload, with a preview table and a `Confirm Import (n orders)` footer | `[L-M1]` |
| 2026-07-23 | Order Type = `Influencer Seeding` preset plus free-text custom | Free-text types allowed (e.g. "Pop-up event giveaway") | BR-5 |
| 2026-07-23 | Import template columns fixed by the dev team | Recipient · Contact · Address · Country · SKU · Qty · Campaign name | §3.2.1 |
| 2026-07-23 | Cancelling an assignment period stops new assignments only; already-assigned orders keep their sets; `Ended` periods are record-only | Protects picking lists already printed | BR-9, BR-30 |
| 2026-07-26 | Program-wide: the inbound-origin route form gained **OTHER (free-text channel)** | No route origin exists on this page; recorded because `[G-5]` was amended program-wide (`_review` C-3, `[PD-80 · OWNER-PENDING]`) and the `OTHER (channel)` badge can appear inside the unchanged order table | §6.6 |
| 2026-08-02 | **Procurement Hub excluded from this planning round entirely** (owner) | No sweep, no English pass, no spec — including any sheet handoff from this page | §9.2, §6.4 |
| 2026-08-02 | English spec handoff programme opened for 8 screens; label/invoice layout deferred to Phase 3-1 | This page references print behaviour and dual-view but specifies no layout | §9.2 |
| 2026-08-03 | **PIC gains a `✎ Custom` free-text input**; default remains the logged-in user; one PIC per entire import | Real PICs are sometimes not admin users | BR-4, BR-21, §3.2.3 |
| 2026-08-03 | **Carrier auto-assignment per country on confirm** | Each row's country receives its connected carrier; countries with none show `Not connected — contact the Fulfillment Center` and do **not** block the batch | BR-3, BR-20, `[L-M1b]` |
| 2026-08-03 | **Green confirmation toast on import confirm**, with subtext carrying the carrier-assignment summary | Instance of the global rule below | §3.2.5 |
| 2026-08-03 | **[Global] Every confirming action shows a top-right confirmation toast and the page never refreshes** (owner emphasis, all 8 screens) | Lands here on import confirm, sample-period start, and sample-period cancel | `[G-2]`, `[L-F5]` |
| 2026-08-03 | **Exactly one sample set per order**, even across overlapping periods | Dedup guard; suppressed matches are persisted as the audit answer | BR-7, `[DC-15]` |
| 2026-08-03 | **Sample dual-view confirmed** | Carrier-facing data appends only `(+ sample set)` to the last product name (tax handling); internal invoice and picking artifacts show which sample and how many | BR-8, `[G-13]` |
| 2026-08-03 | **Sample assignment retained** — Notion §G, the developer handoff note, and the plan ledger corrected | Closes the 2026-07-22 → 2026-07-23 reversal | R-1 |
| 2026-08-03 | **Bulk Hold Shipment removed from this screen** | Hold is now `Change Status → on-hold` on Order Detail; the OMS dashboard stays the live screen. Legend item 3 remains as a dotless negative entry | BR-10, `[L-3]`, QA-LST-04, R-3 |
| 2026-08-03 | **Comment `@mention` channel confirmed: `#fulfillment-admin-comments` (`C0BMGEWM5QA`)** (owner) | Channel and ID fixed for this page's one Slack route; notification semantics are `[G-7]`'s and are not restated here. Supersedes every earlier "channel pending" wording | §6.1, `_review` C-2 |
| 2026-08-03 | Photo column / photo upload **removed program-wide** `[PD-63 · OWNER-PENDING]` | Recorded here as a negative contract so it is not reintroduced by analogy; this page never had one | §3.8.1 |
| 2026-08-03 | Program-wide item 16: **Carrier is not auto-recorded on inbound**, and no Carrier column is added (`_review` C-1, `[PD-9]`) | Does not apply to this page (no inbound surface); recorded so the *import-side* carrier auto-assignment (BR-3) is never confused with it | BR-3 note |
| 2026-08-03 | `_global-rules` v1.0 published; `[G-15]` establishes a **single admin role for v1** `[PD-1 · OWNER-PENDING]` | No control on this page is role-gated; every mutation records the actor | BR-22 |
| 2026-08-03 | `_review` **C-5**: the `[G-3a]` send sound is defined by button class, not by page `[PD-2 · OWNER-PENDING]` | This page has **no** outbound-class button, so no sound applies. Stated so the audit is closed, not silent | BR-28, §6.6, QA-GBL-13 |
| 2026-08-03 | `_review` **C-6**: `[G-2]` beats wireframe omissions | Produces the sample-period-start toast the wireframe lacked ([WF-16 · proposed]) and the cancel confirm step ([WF-17 · proposed], `[PD-5 · OWNER-PENDING]`). Both were applied to the wireframe later the same day, so the drawing and the spec now agree | §3.6.5, §3.7.5, BR-25 |
| 2026-08-03 | **No print surface on this page** `[G-4]`; print consequences of `[G-13]` land on other specs' artifacts | Stated explicitly so the mandatory-inclusion audit closes rather than going silent | BR-29, §6.5, QA-LST-05 |
| 2026-08-03 | PD register adopted for this page: import blocks the whole file on any error (PD-57); duplicate file warns rather than blocks (PD-58); no batch revert (PD-54); periods are not retroactive (PD-52); `Selected orders only` assigns immediately (PD-53); periods match sales orders only (PD-56); merging MKT with sales is blocked (PD-59) | All tagged `[PD-n · OWNER-PENDING]` in the sentences where they appear | BR-12…BR-18 |
| 2026-08-03 | PD-51 and PD-55 recorded as **NO-DEFAULT** | The sample-set definition source, and the unblocking path for `carrier_unresolved` orders, are not decided and no behaviour is specified for them | §9.1 |
| 2026-08-03 | Spec v1.0 authored | 9 legend units → 10 spec keys + 5 furniture keys; 30 business rules; 28 data-capture events; 66 edge cases; 94 QA scenarios | superseded by v1.1 |
| 2026-08-03 | **Spec v1.1 — audit and finalisation pass.** Legend units re-counted directly from the HTML (9 units / 9 rendered dots, confirmed). Added `[L-F6]` (global nav shell) so the furniture count is 6 and the spec-addressable total is 16. Added BR-31 (single operating timezone), BR-32 (cross-entity comment corpus, `[PD-67 · OWNER-PENDING]`), BR-33 (selection resolved at submit), BR-34 (page load mutates nothing). Added `[DC-29] sample.period_started`. Extended edge cases to E-100. Rewrote §8 to 153 scenarios with an executable harness contract (§8.0). Proposed four further wireframe defects, [WF-18] … [WF-21]. Removed three inadvertent restatements of `[G-2]`, `[G-7]` and `[G-15]` rule bodies and replaced them with page deltas. Recorded the three PDs applied beyond their register page list (§9.1) | Nothing from v1.0 was dropped; all v1.0 IDs keep their meanings | superseded by v1.2 |
| 2026-08-03 | **Spec v1.2 — remediation pass against three independent verification reports** (coverage audit M1, adversarial QA execution M2, cross-page + review audit M3a/M3b). **QA:** the five scenarios that could not pass as worded were repaired — QA-GBL-14's unscoped focus clause (which contradicted QA-IMP-06/09) is now scanner-scoped; QA-IMP-12 accounts for the `M1b` annotation dot inside the annotated `th`; QA-LST-12 accounts for the `<br>` inside the four `.navlink` spans; QA-CMT-05 asserts `.empty` / `.it` / `.paneheader` separately instead of the whole pane; QA-CMT-21 takes the concrete input `4`. §8.0 gained normalisation rules 5a–5c, an "identical content" definition (rule 6) and the `· proposed` definition (rule 7); QA-CMT-02 gained a geometric right-alignment probe, QA-IMP-11 a deterministic selector, QA-LST-02 the CSSOM colour form, QA-IMP-19 the `.note.mkt` artifact reference (and lost its unreachable Korean token). **Coverage:** 18 scenarios added (QA-IMP-53…62, QA-SMP-44…50, QA-CMT-24) so every previously uncovered edge case is asserted; `[E-9]` and `[E-42]` are declared intentionally unasserted in §8.0 with reasons. 42 scenarios gained an explicit `When` clause per `_review` §3.4. §8.6's three over-claiming cells were repaired. `[E-4]`, `[E-6]`, `[E-31]`, `[E-34]`, `[E-55]`, `[E-78]`, `[E-79]` gained the §3 back-reference from the clause they constrain. **Cross-page:** §6.7 added (explicit N/A for mandatory items 9/10/11, closing the JIT-residual silent cell); §3.10 declares the one Comments-hub string divergence and why the wireframe wins; §5 declares the `[DC-28]` shared-concept name divergence; §3.8 flags the stale View Orders hold cross-reference; §6.3 pins the directory deep-link form. **Registers:** `[WF-15 · proposed]`…`[WF-21 · proposed]` appended to `_wireframe-fixes` §F; `[G-7]`'s body removed from §6.1 and from this log; BR-31/33/34 surfaced in §9.1 as spec-level defaults awaiting owner sign-off; `[PD-9]`'s status as a non-applicable cross-reference stated in §9.1. **Counts recomputed:** 171 QA scenarios (77 `[WF]` / 94 `[ADMIN]`), 77 negatives = 45.0 %, per block IMP 62 · SMP 50 · LST 17 · CMT 24 · GBL 18 | No ID renumbered, no rule reversed, no behaviour changed. Every v1.1 ID keeps its meaning | superseded by v1.3 |
| 2026-08-03 | **Spec v1.3 — re-baseline against the applied wireframe fixes, plus one declared gap.** The owner-approved wireframe-edit pass applied `[WF-15 · proposed]` … `[WF-21 · proposed]` to `wms2/order-management/index.html` on 2026-08-03 (register: `APPLIED 2026-08-03` on all seven), but this spec still described and asserted the **pre-fix** drawing, so a `[WF]` QA run failed eight scenarios against a wireframe that was already correct. **Re-baselined onto the fixed behaviour, ids unchanged:** QA-IMP-35 (`colspan="7"`), QA-SMP-19 (confirm overlay `#m-sampcancel-confirm` → `#sampConfirmGo` → toast), QA-SMP-30 (`#sampStartBtn` → `#gtoast3` with the §3.6.5 copy), QA-SMP-31 (button disabled at zero selection), QA-SMP-33 (`forever` clears **and** disables the end fields), QA-CMT-20 (outside click closes the hub), QA-GBL-09 (`stackToasts()` — visible toasts never overlap), QA-GBL-10 (`Esc` closes the topmost overlay, else the hub). **Status corrected, not deleted:** §2.4 now records each defect as found *and* what landed; §8.0 rule 7 retires the "not yet adjudicated / do not apply" reading of the `· proposed` suffix (it is now only a frozen ID token — `_wireframe-fixes` §F forbids renumbering); rule 4 documents the four-overlay `Esc` unwind; rule 2 adds the third toast node `#gtoast3` and the stack offsets; the two now-fixed items are struck from the `[ADMIN]`-forcing demo-limitation lists with their history kept. **Adjacent staleness repaired:** §3.2.4, §3.2.6, §3.6.3, §3.6.5, §3.7.5, §3.10, §3.15, [E-23], [E-28], [E-62], [E-97], QA-SMP-06, QA-SMP-20, QA-SMP-21, QA-SMP-34 and §9.2's wireframe-edit bullet. **Declared gap:** `[OQ-1]` registers that no monetary amount is defined for an imported `MKT-` order — the template has no price column (§3.2.1) and `[DC-9]` names no monetary field (§5.1); no default is invented, and the payload line is owed once the question is answered. **Counts recomputed:** 171 QA scenarios (77 `[WF]` / 94 `[ADMIN]`) unchanged; negatives 77 → **73 = 42.7 %** because four defect-documentation tests became positive assertions; per-block totals unchanged | No ID renumbered, no scenario added or removed, no scenario retagged `[WF]`↔`[ADMIN]`, no rule reversed, no product requirement changed — every §3 clause already specified the fixed behaviour. Every v1.2 ID keeps its meaning | this document |

### Reversal chains (recorded verbatim so nobody re-litigates them)

- **R-1 — Sample assignment.** 2026-07-22 recorded as **removed** → 2026-07-23 **reinstated and redesigned as a simple ON/OFF** (multi-period, overlaps allowed, no sample-type selection) → 2026-08-03 **retained and reconfirmed**, with Notion §G, the developer handoff note, and the plan ledger corrected. The 2026-07-22 note was stale within a day; it is preserved here only so that a reader who finds it in an old document knows it was superseded.
- **R-2 — Import stock validation.** Notion §G originally specified "error if the product is not in the warehouse" → 2026-07-23 **dropped** by owner decision (import may precede inbound) → 2026-08-03 confirmed that the check must not be surfaced in UI copy at all. QA-IMP-19 and QA-IMP-23 are the regression guards against its return, and §3.8.1's last row blocks it from re-entering as a confirm-time gate.
- **R-3 — Bulk Hold Shipment.** Present in the 2026-07-09 real-capture rework (as a modal on this page) → **removed** 2026-08-03; hold relocated to Order Detail `Change Status → on-hold`. Legend item 3 deliberately keeps a dotless entry so the removal is visible rather than absent, and QA-LST-04 asserts both the absence of the control and the presence of the legend entry.
