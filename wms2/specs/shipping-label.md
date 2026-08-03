# Shipping Labels — Specification (supplement)

> Companion to the 8 screen specs — covers the printed paperwork, not an admin screen.
> **Wireframe SST:** `wms2/shipping-label/index.html` · **Live:** https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/shipping-label/
> **Spec version:** 1.2 · **Written:** 2026-08-03 · **Global rules:** cited as `[G-n]`, never restated.
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

### 3.3 Item table columns
`No · 상품명 · 사이즈 · 로케이션 · 수량` — **column headers are Korean** (the invoice is a warehouse-floor document; continuity with the current prints) **[CONFIRMED 2026-08-03]**.
- **상품명** — Korean product name (label content is data and stays Korean `[G-6]`).
- **사이즈** — from the Order page line-items **Size** column (e.g. `50ml`). *(added 2026-08-03)*
- **로케이션** — the SKU's registered warehouse location at print time (mono bold, e.g. `A-01-07`); products without one (JIT sourcing etc.) show `—`. *(added 2026-08-03)*
- **수량** — bold, larger than body text (mispick prevention).
- **Sample set row** `[G-13]`: when the order has a sample assignment, one amber-tinted row rendered as exactly `sample set` (no type, no per-type qty — PD-51), location = sample shelf. **The sample set counts toward `총수량` and `합계`** — the invoice verifies what is physically in the box, so paper and box must agree (e.g. `9 = 8 products + 1 sample set`) **[CONFIRMED 2026-08-03]**. Carrier-facing rendering is different — §3.5.

### 3.5 Sample set — internal vs carrier-facing rendering **[CONFIRMED 2026-08-03]**
Two renderings of the same sample assignment, and they must never be mixed up:
| Surface | Rendering |
|---|---|
| **Internal invoice (this document)** | Own table row `sample set`, counted in `총수량`/`합계` |
| **Data sent to the carrier** | **No separate line item.** Only the string `(+ sample set)` appended to the **last product name** (tax handling) — the carrier never receives a sample line, a sample qty, or a sample price `[G-13]` |

### 3.4 Typography (measured from the current prints, 2026-08-03)
Measured glyph heights on the photographed labels, at the wireframe's 1mm = 5px scale:

| Element | Physical | Wireframe |
|---|---|---|
| Body / table text | ≈ 3.6–3.8mm | 18–19px |
| Qty (bold) | ≈ 4.2mm | 21px |
| `PACKING` title | ≈ 5.2–5.5mm | 26–28px |
| `총수량` | ≈ 4.4mm | 22px |
| Footer | ≈ 2.7mm | 13.5px |

**Floor:** the unified format must never render body text smaller than the current DELEO internal invoice (≈3.6mm). Capacity at these sizes ≈ 9 item rows per page.

## 4. Data sources
Order number & barcode = the order record · 사이즈 = line-items Size · 로케이션 = SKU's registered location at print time (one location per SKU `[G-14]`) · quantities & totals = order line quantities + sample assignment.

## 5. Print behavior
`[G-4]` instant print (no dialog, no preview, correct carrier automatically) from every Print surface that emits the internal invoice: View Orders (order Print, single-item auto-print), RTO (row Print, Bulk Print Labels), Order Detail (Print).

## 6. Open items (owner)
1. ~~Column header language~~ — **DECIDED 2026-08-03: Korean** (`사이즈`/`로케이션`), as mocked (§3.3).
2. ~~Multi-page totals~~ — **DECIDED 2026-08-03: last page only**; earlier pages read `계속 →`, top-right `총수량` on every page (§3.2).
3. ~~Sample set in totals~~ — **DECIDED 2026-08-03: counted** (`9 = 8 products + 1 sample set`), §3.3/§3.5.

**All items decided — this spec is fully confirmed and frozen for the pre-handoff review.**

## Change history
| Version | Date | Changes |
|---|---|---|
| 1.0 | 2026-08-03 | Initial spec from the owner's Phase 3-1 direction: taxonomy split, carrier-default policy confirmed, unified internal invoice (landscape 150×100 · Size/Location columns · minimal margins · bottom 합계 · corner layout), photo-measured typography, 3 open items. |
| 1.1 | 2026-08-03 | Owner decisions: column headers **Korean** (open item 1) · multi-page totals **last page only, `계속 →` on earlier pages** (open item 2). Open item 3 (sample set in totals) remains. |
| 1.2 | 2026-08-03 | Owner decision: **sample set counts toward `총수량`/`합계`** (open item 3 — last one). §3.5 added: internal row vs carrier-facing `(+ sample set)`-on-last-product-name rendering, explicitly separated. Spec fully confirmed. |
