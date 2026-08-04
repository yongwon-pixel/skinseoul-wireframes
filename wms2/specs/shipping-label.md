# Shipping Labels — Specification (supplement)

> Companion to the 8 screen specs — covers the printed paperwork, not an admin screen.
> **Wireframe SST:** `wms2/shipping-label/index.html` · **Live:** https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/shipping-label/
> **Spec version:** 1.4 · **Written:** 2026-08-03, amended 2026-08-04 · **Global rules:** cited as `[G-n]`, never restated.
> **Status:** **fully CONFIRMED** (owner, 2026-08-03) — carrier-label policy, unified internal invoice, and all three §6 items are decided. No open questions.

## 1. Document taxonomy

Two different documents print at dispatch. They must never be confused:

| Document | Owner | Purpose | Policy |
|---|---|---|---|
| **Internal invoice ("PACKING")** | Ours (WMS-generated) | In-warehouse pick/pack verification, then discarded (`[검수 후 폐기]`) | **Redesigned** — §3 |
| **Carrier label** | The carrier (YUN Express · DELEO) | Transport / customs / last-mile | **Carrier default, verbatim** — §2 |

## 2. Carrier labels — carrier defaults, unchanged **[CONFIRMED 2026-08-03]**

- Both carrier labels use **the carrier's existing default output as-is**: YUN Express (4×6 in) and DELEO. **No custom layout is designed, requested, or built** for either; the admin's only job is to print them unchanged.
- This rule is **carrier-agnostic and forward-binding**: any carrier added later (e.g. **FedEx**) also ships with its own default label, untouched.
- Printing follows `[G-4]` — any Print button outputs the correct carrier's paperwork immediately on click, and `print.job_result` persists `[G-8]`.

## 3. Unified internal invoice **[CONFIRMED direction 2026-08-03]**

One internal-invoice format for **all** carriers. YUN switches from portrait to landscape; DELEO keeps landscape; a future carrier (FedEx etc.) inherits the format with zero changes.

### 3.1 Stock & orientation
- 100×150mm thermal label, printed **landscape (150×100mm)**.
- **Minimal margins** — ~2–3mm on all sides (the current prints waste large borders; the photographed 9-unit order drops from 2 pages to 1).

### 3.2 Fixed layout (corners kept from the current format)
| Position | Content |
|---|---|
| Top-left | `PACKING` + order number (`#428204`) |
| Top-center | Order barcode |
| Top-right | `총수량: {n}` |
| Body | Item table (§3.3) |
| Table bottom | `합계` row — total qty repeated so the packer verifies without looking back up |
| Bottom-left | `[검수 후 폐기]` |
| Bottom-right | Page `n/m` |

**Multi-page rule [CONFIRMED 2026-08-03]:** the `합계` row prints on the **last page only**; earlier pages end with `계속 →` in its place. The top-right `총수량` repeats on **every** page.

**Worked two-page example — mocked, not just described.** *(added 2026-08-04)* The wireframe carries a second, longer order (`#431902`, 17 units over 14 product lines plus a sample set) rendered across both of its pages, because three rules of this section are only observable when a label overflows and were previously stated in prose alone:
- **`총수량` repeats.** Both pages print `총수량: 17` top-right. A packer who picks up page 2 alone still knows the parcel's true total.
- **`계속 →` occupies the `합계` row's slot** on every page but the last: same row position, spanning the label columns and **right-aligned**, with the 수량 cell left **empty**. It is a continuation marker, not a subtotal — printing a running subtotal there would be read as the parcel total and is forbidden.
- **The sample-set row sorts last**, so on a multi-page invoice it always lands on the **final** page, immediately above `합계`.
Page count and rows-per-page are derived at render time (§3.5), so this example is a rendering of the rule at the current type sizes — **not** a fixed 9-rows-then-break constant.

### 3.3 Item table columns
`No · 바코드 뒤4 · 상품명 · 사이즈 · 로케이션 · 수량` — **column headers are Korean** (the invoice is a warehouse-floor document; continuity with the current prints) **[CONFIRMED 2026-08-03]**.
- **바코드 뒤4** — the **last 4 digits of the product's EAN barcode**, printed immediately **left of 상품명**. **CONFIRMED 2026-08-04 (owner).** *(added 2026-08-04)*
  - **Source: the product EAN, already collected in the current admin** — never the internal SKU. The column exists so the packer can verify against the code **physically printed on the box**; an internal SKU fragment matches nothing on the product and would make the check unperformable.
  - Rendered mono bold, right-aligned with `font-variant-numeric: tabular-nums` so digits line up down the column.
  - **Always exactly 4 digits — the column never widens. CONFIRMED 2026-08-04 (owner).** The last 4 of an EAN-13 are 3 data digits plus the check digit and are therefore **not unique**, so two lines on one invoice can share them. That is accepted: the column is a quick confirmation aid, not a unique key, and the packer already has the product name and size to tell two lines apart. Do not implement a widening, padding or disambiguation rule.
  - A line whose product has **no EAN registered** renders the unknown marker `—`, the same convention 로케이션 uses. The **sample-set row carries no value** (`[G-13]`: it is a set, not a catalogue product).
- **상품명** — Korean product name (label content is data and stays Korean `[G-6]`).
  - **Overflow (name wider than the column):** the cell renders on **one line only**, clipped at the column edge with a trailing ellipsis (`…`) — this is a **display** truncation; it never wraps to a second line and the underlying data is never shortened to fit, per the same doctrine `view-orders` `[E-77]` assigns to this template ("only the physical label template truncates, never the stored data"). *(added 2026-08-03)*
- **사이즈** — from the Order page line-items **Size** column (e.g. `50ml`). *(added 2026-08-03)*
- **로케이션** — the SKU's registered warehouse location at print time (mono bold, e.g. `A-01-07`); products without one (JIT sourcing etc.) show `—`. *(added 2026-08-03)*
- **수량** — bold, larger than body text (mispick prevention).
- **Sample set row** `[G-13]`: when the order has a sample assignment, one amber-tinted row rendered as exactly `sample set` (no type, no per-type qty — PD-51). **No location is printed on it — 로케이션 renders the `—` marker. CONFIRMED 2026-08-04 (owner).** A sample set is not stocked as a located SKU, so printing a shelf for it would invite the packer to verify against a location the system does not maintain. **The sample set counts toward `총수량` and `합계`** — the invoice verifies what is physically in the box, so paper and box must agree (e.g. `9 = 8 products + 1 sample set`) **[CONFIRMED 2026-08-03]**. Carrier-facing rendering is different — §3.4.

### 3.4 Sample set — internal vs carrier-facing rendering **[CONFIRMED 2026-08-03]**
Two renderings of the same sample assignment, and they must never be mixed up:
| Surface | Rendering |
|---|---|
| **Internal invoice (this document)** | Own table row `sample set`, counted in `총수량`/`합계` |
| **Data sent to the carrier** | **No separate line item.** Only the string `(+ sample set)` appended to the **last product name** (tax handling) — the carrier never receives a sample line, a sample qty, or a sample price `[G-13]` |

### 3.5 Typography (measured from the current prints, 2026-08-03)
Measured glyph heights on the photographed labels, at the wireframe's 1mm = 5px scale:

| Element | Physical | Wireframe |
|---|---|---|
| Body / table text | ≈ 3.6–3.8mm | 18–19px |
| Qty (bold) | ≈ 4.2mm | 21px |
| `PACKING` title | ≈ 5.2–5.5mm | 26–28px |
| `총수량` | ≈ 4.4mm | 22px |
| Footer | ≈ 2.7mm | 13.5px |

**Floor:** the unified format must never render body text smaller than the current DELEO internal invoice (≈3.6mm). Capacity at these sizes ≈ 9 item rows per page.

**Rows per page is derived at render time, not a fixed constant. *(added 2026-08-03)*** Pagination computes the count as *(usable body height) ÷ (rendered row height)* — usable body height = the printed sheet height (§3.1) minus the §3.1 margins and the fixed §3.2 furniture (top corner block, table header, and the bottom `합계` / `계속 →` row); rendered row height follows from the type sizes in this section. The `≈ 9` above is the **measured outcome** at the current sizes and margins, quoted as a reference value — it is not a number to hard-code, and any change to type size, margin, or fixed furniture changes it. Whatever count the calculation yields is what the §3.2 multi-page rule and the bottom-right page `n/m` report.

## 4. Data sources
Order number & barcode = the order record · 바코드 뒤4 = the product's registered **EAN** (existing admin field), truncated to the last 4 at print time, never widened (§3.3) · 사이즈 = line-items Size · 로케이션 = SKU's registered location at print time (one location per SKU `[G-14]`) · quantities & totals = order line quantities + sample assignment.

## 5. Print behavior
`[G-4]` instant print (no dialog, no preview, correct carrier automatically) from every Print surface that emits the internal invoice: View Orders (order Print, single-item auto-print), RTO (row Print, Bulk Print Labels), Order Detail (Print).

## 6. Open items (owner)
1. ~~Column header language~~ — **DECIDED 2026-08-03: Korean** (`사이즈`/`로케이션`), as mocked (§3.3).
2. ~~Multi-page totals~~ — **DECIDED 2026-08-03: last page only**; earlier pages read `계속 →`, top-right `총수량` on every page (§3.2).
3. ~~Sample set in totals~~ — **DECIDED 2026-08-03: counted** (`9 = 8 products + 1 sample set`), §3.3/§3.4.

**All items decided — this spec is fully confirmed and frozen for the pre-handoff review.**

## Change history
| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-08-03 | Initial spec from the owner's Phase 3-1 direction: taxonomy split, carrier-default policy confirmed, unified internal invoice (landscape 150×100 · Size/Location columns · minimal margins · bottom 합계 · corner layout), photo-measured typography, 3 open items. |
| 1.1 | 2026-08-03 | Owner decisions: column headers **Korean** (open item 1) · multi-page totals **last page only, `계속 →` on earlier pages** (open item 2). Open item 3 (sample set in totals) remains. |
| 1.4 | 2026-08-04 | **Two-page worked example added to the wireframe** (§3.2): the multi-page rule was specified but never drawn, so `총수량` repeating, `계속 →` occupying the `합계` slot right-aligned with an empty 수량 cell, and the sample-set row landing on the final page were prose-only. Order `#431902` now renders both pages. No rule changed — the example is a rendering of the existing rule, and rows-per-page stays derived (§3.5), not a constant. |
| 1.3 | 2026-08-04 | Owner decision: **new `바코드 뒤4` column**, left of 상품명 — last 4 digits of the product **EAN** (not the internal SKU), so the packer verifies against the code on the box. **Always exactly 4 digits — no widening on collision** (owner, same day): the column is a confirmation aid, not a unique key, and the product name distinguishes any two lines that share the last 4. Sample-set row carries none; missing EAN renders `—`. Mockup updated in the same commit (legend item 8). |
| 1.2 | 2026-08-03 | Owner decision: **sample set counts toward `총수량`/`합계`** (open item 3 — last one). §3.4 added: internal row vs carrier-facing `(+ sample set)`-on-last-product-name rendering, explicitly separated. Spec fully confirmed. |
