# WMS 2.0 — Developer Handoff: Start Here

> Read this page first. It tells you what the document set is, in what order to read it, what every bracket notation means, how to run the QA suites, and exactly which decisions are yours to make.
>
> **Status:** specs frozen for handoff, 2026-08-03, with **one owner amendment applied 2026-08-04** — loss-amount removed from the stock audit, which is now counts-only (§6, §7, and `_global-rules.md` `[G-14]`). The scenario census is unchanged at 647 `[WF]`; the Inventory wireframe, spec and runner were re-synchronised in the same pass.

---

## 1. What this is

WMS 2.0 is the warehouse-management layer of the SkinSeoul admin: the screens the fulfillment center actually operates on, from declaring an inbound shipment through receiving, picking, printing, outbounding, and closing the day. It replaces a set of manual rituals — Excel duplicate checks, parcels set aside on a shelf, chasing tracking numbers in Slack — with one system of record.

This repository holds **10 canonical documents**: one global-rules file, eight screen specifications, and one printed-paperwork supplement. Every one of them is normative. Together they are 16,577 lines and they are the contract — not the wireframes, and not Notion (Notion is a mirror of these files).

The eight screens:

| # | Screen | Spec file / page slug | What it does |
|---|---|---|---|
| 3 | **View Orders** | `view-orders.md` | The single scan hub. Every barcode entering the warehouse is typed into one input and the page decides on its own what the operator is holding — customer order, product EAN, supplier inbound label, returned parcel — and switches to the matching state. Nine states, six modals. |
| 4 | **Order Detail** | `order-detail.md` | The single-order command center: line items, statuses, per-line inbound / cancel-inbound, inline edits to the five agent-tracking fields, print, comments. |
| 5 | **Ready to be Outbounded** | `ready-to-outbound.md` | The packing bench queue. Order-level list with pick locations, bulk picking-list and label printing, bulk outbound with progress. |
| 6 | **Inventory** | `stock-status.md` | Current stocks, stock-audit mode (location-ordered walk, **count differences only — no money**, audit log), reserved-stock view and release, stock history. **Note the slug: the screen is called Inventory, the file is `stock-status.md`.** |
| 7 | **Order Management Dashboard** | `order-management.md` | The order team's home screen. The order list itself is unchanged from the current admin and deliberately omitted; what is specified is the marketing-order import (template → preview → assignee) and sample-set assignment. |
| 8 | **Unrecognized Tracking** | `tracking-missing.md` | The desk-side resolution pool for goods that arrived without a resolvable link to an order: suggested candidate orders, two-click matching, removal with reason. Push-driven from Slack, never polled. |
| 9 | **Closing** | `closing.md` | End-of-day reconciliation between what physically left and what the system believes left: hand count, scan every parcel once, instant verdict per scan, confirm only at an exact match with zero warnings. Plus Closing History and post-confirmation amendment. |
| 10 | **Inbound Request** | `inbound-request.md` | The single intake gateway. Every arrival is declared here before it arrives; the warehouse floor records the physical fact later from View Orders State 6. |

Plus `shipping-label.md`, which covers the printed paperwork rather than a screen: the redesigned internal invoice ("PACKING") and the policy that carrier labels are printed as each carrier's own default output, verbatim.

---

## 2. How to read

**Read in this order:**

1. **`_global-rules.md`** (139 lines) — 16 cross-cutting rules `[G-1]`…`[G-16]` that every screen inherits, plus the canonical cross-page event names, the Slack routing table, and the byte-exact Comments-hub copy. Read it completely before any screen spec. Screen specs cite these rules by ID and state **page deltas only** — they never restate a rule body, so a screen spec read alone will look incomplete.
2. **The screen spec you are building.** Each is self-contained for its own screen.
3. **`shipping-label.md`** — read before implementing any Print surface.

**Every screen spec has the same ten sections, in this order:**

| § | Title | What it holds |
|---|---|---|
| 1 | Purpose & Users | What the screen is, who operates it, and the physical reality that shaped the design. Context, not requirements — but it is what makes the requirements make sense. |
| 2 | Screen Inventory & Wireframe Map | The declared unit count, the state/modal map with DOM ids and how to reach each one, **wireframe demo limitations** (§2.3 — artefacts of a static mock, never bugs), and **wireframe defects** (§2.4 — real logged faults where the spec states the corrected behavior). |
| 3 | Functional Specification | The bulk of the document. Per-unit behavior: trigger, behavior, validation, server action, what persists. |
| 4 | Business Rules | `[BR-n]` — the rules with their rationale and decision date. |
| 5 | Data Capture | `[DC-n]` — every persisted event, its payload, and its retention. Plus explicitly declared NON-events. |
| 6 | Integrations | Print, Slack, audio, deep links, cross-screen contracts. |
| 7 | Edge Cases & Error States | `[E-n]` — what happens when it goes wrong. |
| 8 | QA Acceptance Criteria | Executable scenarios. §8.0 is the execution protocol; read it before running anything. |
| 9 | Out of Scope & Open Questions | What this screen deliberately does not do, what must NOT exist on it, open owner questions, and the decisions delegated to you. |
| 10 | Decision Log | Every decision that shaped the screen, dated, including reversals. Use it when a rule looks arbitrary — the reason is almost always here. |

`shipping-label.md` is a supplement and does not follow this structure.

---

## 3. Notation

Every bracketed token in these documents is a stable identifier. **IDs are never renumbered once cited** — if an ID looks like it has a gap or an odd suffix, §2.1 of that spec declares why.

| Token | Means | Where it is defined |
|---|---|---|
| `[G-n]` | **Global rule.** `[G-1]`…`[G-16]`, cross-cutting, inherited by every screen. | `_global-rules.md` |
| `[L-*]` | **Legend / unit key** — one implementation unit of the screen. Forms: `[L-n]` (plain legend dot), `[L-Sx-n]` (state-qualified, e.g. `[L-S6-1]`; legend numbers repeat across states so keys are always state-qualified), `[L-Mn]` (modal), `[L-Fn]` (page furniture — a rendered control with no legend dot), `[L-Sx-F]` (off-screen normative footer block, sub-keyed `a`/`b`/`c` when it holds several rules). | §2 of each spec |
| `[L-Rn]` | **Negative entry** — a removed or rejected feature that must NOT exist in the build. Not a unit; not counted in the unit total. `inbound-request.md` only; other specs express the same thing as a "must NOT exist" table in §9.1. | `inbound-request.md` §2.1 |
| `[BR-n]` | **Business rule**, with rationale and date. | §4 |
| `[DC-n]` | **Data-capture event** — a persisted event with a defined payload. | §5 |
| `[NE-n]` | **Declared NON-event** — ephemeral client-local state that deliberately does not persist (checkbox toggles, tab switches, cancelled edits). Anything operator-initiated and *not* declared a non-event **must** persist `[G-8]`. | §5 |
| `[E-n]` | **Edge case / error state.** | §7 |
| `QA-*` | **QA scenario id**, e.g. `QA-S0-01`, `QA-IMP-35`, `QA-CMT-10`. | §8 |
| `[WF]` / `[ADMIN]` | **QA tier** — see §4 below. | §8.0 |
| `WF-n` | **Wireframe defect** — a logged fault in the drawing. **Do not confuse with the `[WF]` QA tier**: `[WF]` (in brackets, in a QA scenario header) is a test tier; `WF-1`, `WF-15`, `WF-VO-1` (no brackets) are defect ids. | §2.4, and `_plans/_wireframe-fixes.md` |
| `[PD-n]` | **Provisional decision** — see §6 below. | `_plans/_provisional-decisions.md` |
| `[X-n]` | **Open cross-page conflict** where this screen's position disagrees with another screen's. Each row states this page's position and what changes if it is reversed. `order-detail.md` uses `[X-n]`; `ready-to-outbound.md` uses `[RTO-X-n]`. | §2 / §9.5 |
| `CP-n` | Same concept, `view-orders.md`'s naming: **cross-page disagreements** involving that page, §9.5. Rows marked RESOLVED are kept as the record of a conflict that existed. | `view-orders.md` §9.5 |
| `D-n` / `DQ-n` | **Developer decision register entry.** `D-n` in `order-detail`, `ready-to-outbound`, `tracking-missing`, `inbound-request`; `DQ-n` in `closing`; unkeyed tables in the others. See §5 below. | §9.2 / §9.3 / §9.4 |
| `OQ-n` | **Open question with no default** — the owner must decide; no behavior is specified anywhere. Rare: **two remain open, and they are the same axis** — `stock-status.md` **OQ-2** (which single route a multi-route SKU row resolves to) and `ready-to-outbound.md` **OQ-3** (how an order is classified JIT when its lines mix routes). Both are schema decisions about where the sourcing route lives; answer them together, before the data model is fixed. `stock-status.md` OQ-1 (the audit loss-amount cost source) was **retired 2026-08-04** when the owner removed loss-amount from the stock audit — see §6. | §9 |
| `— DEFERRED` | A QA scenario that carries **no assertion** because it is blocked on an owner decision. Counted in the totals, never executed, never fails. | §8.0 |

---

## 4. How to use the QA sections

§8 of each spec is a set of executable acceptance scenarios. Every scenario carries a tier tag.

- **`[WF]`** — executable against the live wireframe **today**, using only the selectors and strings written in the scenario, with no further instruction. These are your regression net for the drawing.
- **`[ADMIN]`** — asserts behavior a static mock cannot produce: persistence, server rejection, real state transitions, sound gating on disabled controls. **These are your build acceptance criteria.** They are the scenarios you make pass.

**Before filing any `[WF]` failure, read §2.3 and §2.4 of that spec.** §2.3 lists demo limitations — artefacts of a static HTML mock that are not bugs and never become bugs (for example: no state actually transitions on scan; disabled buttons carry no `disabled` attribute). §2.4 lists real wireframe defects where the spec states the corrected behavior.

**§8.0 is the execution protocol and it is binding.** It fixes how to switch states, how to open and close modals, how to reset between scenarios, and — most importantly — how text is compared. Text assertions are on `textContent` with runs of whitespace collapsed on both sides, after stripping the wireframe's annotation chrome (`.dot` markers inside buttons and cells, and the trailing `✕` in modal headers). A literal byte comparison of raw `textContent` is explicitly **not** a valid reading of the rule and will fail on nearly every element.

**The runners already exist.** `_verify/prehandoff/` holds eight Python + Playwright runners, one per screen, that execute every `[WF]` scenario against a local copy of the wireframe:

```
_verify/prehandoff/qa-view-orders.py        136 scenarios
_verify/prehandoff/qa-ready-to-outbound.py   93
_verify/prehandoff/qa-order-management.py    77
_verify/prehandoff/qa-stock-status.py        75
_verify/prehandoff/qa-closing.py             74
_verify/prehandoff/qa-order-detail.py        69
_verify/prehandoff/qa-tracking-missing.py    66
_verify/prehandoff/qa-inbound-request.py     57
                                     total  647
```

Run one with `python3 qa-<screen>.py [--json out.json]`. **As of 2026-08-03 the state is 647/647 PASS, zero failures, zero expected failures** — so any `[WF]` failure you see is a genuine regression, either in the wireframe or in your reading of the protocol. Use these as a change-detector when you edit a wireframe: a copy edit that touches an asserted string must be applied to the drawing, the spec, and the runner in the same pass, or the runner will correctly fail.

The `[ADMIN]` scenarios have no runner — they are yours to implement against.

---

## 5. What is deliberately left to you

The specs distinguish three categories, and this is the third: decisions the spec deliberately does not make, where a default or a constraint is stated and the mechanism is yours. They are **not** owner questions and must not be escalated as such. Around 139 sentences across the document set carry an explicit "developer decision" clause; each spec collects its own into a register:

| Spec | Register | Entries |
|---|---|---|
| `view-orders.md` | §9.3 (unkeyed table, by area) | 15 areas |
| `order-management.md` | §9.3 (unkeyed table, by area) | 24 areas |
| `order-detail.md` | §9.4, keyed `D-1`…`D-21` | 21 |
| `ready-to-outbound.md` | §9.3, keyed `D-1`…`D-18` | 18 |
| `stock-status.md` | §9.2 "Developer decisions" (unkeyed table) | 17 areas (`Costing` retired 2026-08-04 — 16 live) |
| `tracking-missing.md` | §9.2, keyed `D-1`…`D-13` | 13 |
| `closing.md` | §9.3, keyed `DQ-1`…`DQ-13` | 13 |
| `inbound-request.md` | §9.3, keyed `D-1`…`D-23` | 23 |
| `_global-rules.md` | inline | 3 |

**Read your screen's register before you start.** The recurring themes, so you know the shape:

- **Idempotency** `[G-9]` — key format, TTL, client debounce interval, and how a rejected duplicate surfaces are all yours. What is *not* yours: every confirming action must be double-click safe end-to-end, and the suppressed duplicate must persist. The current admin processes double clicks twice; that bug must be fixed, not reproduced.
- **Toasts** `[G-2]` — duration, stacking vs single-slot replacement, and failure copy are yours (where the spec does not fix the string). What is not yours: a toast must never block the scan input or delay the next scan, and must name the cause on failure.
- **Print** `[G-4]` — print-agent product, timeout, retry policy, job polling, queue naming are yours. What is not yours: no browser print dialog, ever, and no browser-dialog fallback; failure surfaces as a red toast and persists as `print.job_result`.
- **Audio** `[G-3]` — synthesis parameters, the TTS voice-selection fallback chain, and `AudioContext` resume strategy are yours. What is not yours: the send tone and the View Orders State 6 warning tone must be discriminable at 2 m over warehouse noise, and blocked audio never blocks an action.
- **Slack** — retry/backoff schedule, attempt cap, dead-letter handling are yours. What is not yours: dispatch failure never blocks or rolls back the primary action, and every attempt persists.
- **Sync transport** — poll vs push, and acceptable latency, for multi-operator live sync and comment freshness. Constraint: counting flows merge server-side; the server is authoritative for sequence and counters.
- **Literal API and endpoint naming** — free everywhere. The canonical cross-page **event** names in `_global-rules.md` are byte-identical wherever they appear and are not free.
- **Exports** — file format, encoding, column set, filename convention. UTF-8 with BOM is the recommended default so Korean opens correctly in Excel.
- **Pagination vs virtualization, page sizes, debounce intervals, batch chunk sizes** — all yours, bounded by stated invariants (for example: the View Orders live feed's on-screen cap is fixed at exactly 20; a partial batch must be reported as partial and must not roll back successful lines).

**Two of these are flagged "must be settled before build" rather than merely open:**

- `order-detail.md` **D-10** — whether a line delete or add propagates back to WooCommerce. Either answer is acceptable; an undefined answer creates a silent divergence between WooCommerce and the admin.
- `order-detail.md` **D-21** — the WooCommerce sync direction contract: which admin-side changes are written outward, whether inbound changes arrive by webhook or poll, and which side wins when the same order changes on both sides in the same window. **No default is stated and none may be invented.** The optimistic-version → 409 rule `[G-9]` governs two operators on *this* system's record; it is not the admin ↔ WooCommerce rule.

**Where the answer to both comes from (owner ruling, 2026-08-04):** not from a new design round and not from an owner decision — **the current admin already exchanges data with WooCommerce, so you read the existing behaviour out of that codebase and write it into the spec.** "None may be invented" still holds exactly as written; it means *do not guess*, not *wait for a ruling*. `PREREQUISITES.md` `D2` carries the same framing, owned `Joint`, and prerequisite `0.1` (repository access to the current admin) is what unblocks it. Unchanged either way: the status vocabulary stays at exactly **8 WooCommerce statuses** carried as-is, and a ninth value must NOT be invented `[BR-12]`.

Similarly, `ready-to-outbound.md` **D-7** and `stock-status.md`'s audit-draft entry are choices that **must be chosen and documented in the build** — leaving them implicit is itself a defect, because they decide whether an operator silently loses work.

---

## 6. Provisional decisions — the `[PD-n]` tag

When the specs were written the owner was unavailable for a long stretch, so the spec team made the decisions needed to write unambiguous behavior and recorded every one in `_plans/_provisional-decisions.md`. The register has **86 entries**.

A sentence tagged `[PD-n · OWNER-PENDING]` means exactly this: **a reasonable default is already applied and specified as normal behavior — build it.** The tag is not a blocker and not a gap. It marks the sentence as resting on a decision the owner has not personally ratified, and the register entry for that ID names the question, the provisional answer, the rationale, and **which pages and which sentences would have to change if the owner reverses it**. Reversal is therefore a mechanical edit with a known blast radius, not a re-derivation.

**15 entries are now owner-decided and CONFIRMED:** `PD-1` through `PD-8`, plus `PD-51`, `PD-55`, `PD-66`, `PD-71`, `PD-74`, `PD-79` (all 2026-08-03), and `PD-36` (2026-08-04 — the picking list carries a `sample set` line, ratifying wireframe fix WF-9; its inline tags were **removed** rather than left to be superseded, so `PD-36` is the one decided ID you will not see tagged anywhere). Where an inline `[PD-n · OWNER-PENDING]` tag for one of those IDs still appears in a spec sentence, **the register ruling supersedes it** — this is stated in the status legend of `_global-rules.md` and in the header banner of each spec. What those 15 settled, in short: single admin role for v1 with mandatory actor logging; send sound on every outbound-class button; append-only comments; Slack failure never blocks and retries with backoff; every destructive action takes a confirm + reason + toast; server revalidates at confirm; concurrency by optimistic version check; inbound and outbound tracking numbers are separate namespaces; "sample set" only with no type breakdown in v1, and the internal picking list does carry that line; the SS Daily Shipping Status sheet retired outright; `CANCELLED` as a terminal inbound-request state that deactivates tracking matching.

**One entry is retired (2026-08-04):** `PD-43` asked whether the audit `Loss (₩)` / product cost was visible to all warehouse staff. The owner removed loss-amount from the stock audit, so the question has no subject left — it is **invalidated, not answered**, and it cannot be reversed by reversing a visibility choice; reinstating it would mean reinstating money in the audit, which `stock-status.md` §9.1 records as must-NOT-exist. The ID is kept in the register, not deleted and not reused, so stale cross-references still resolve.

The remaining **70 entries are still provisional**. Build them as written.

**`stock-status.md` OQ-1 no longer exists.** It asked where the audit `Loss (₩)` column's product cost came from, and it was the item this section previously named as the last genuinely open question. **On 2026-08-04 the owner removed loss-amount from the stock audit entirely: the audit reports quantity differences only (`−1` / `+1`) and carries no monetary figure.** OQ-1 was therefore invalidated rather than answered — there is no cost basis to choose, no FIFO-COGS read, and no `Loss (₩)` column for a cost to feed. Do not go looking for a decision on it, and do not reinstate the column: `stock-status.md` §9.1 records it as must-NOT-exist.

**One item is genuinely open with no default anywhere:** `stock-status.md` **OQ-2** — when a SKU has been inbounded through more than one sourcing route, which single value its `Sourcing Route` cell shows. The candidate answers (product-master attribute, first inbound's route, latest inbound's route, or a per-lot route with a display rule) are observably different, no provisional default exists, and the spec defines no `route.*` event and no route field on `[DC-1]`, so a change of the displayed value would today be neither specified nor traceable. It blocks the `Sourcing Route` cell of `[L-5]`, the route filter's result set, the Product Information card's route row, and the route column of both exports — and it reaches View Orders, whose existing-inventory exception renders "that stock's own sourcing route". **This is a schema decision** (product-master attribute vs per-lot attribute) and cannot be deferred past data-model design without a re-model.

---

## 7. v1 scope boundaries

Things deliberately excluded from v1. §9.1 of each spec carries the full list for that screen — including, on several screens, a "**must NOT exist**" table where each row names a feature that was built and removed, or explicitly rejected, with its removal date and the QA scenario that asserts its absence. Those tables exist so nobody re-implements a removed feature from a stale document or a leftover CSS class. Read them.

The program-wide boundaries:

- **No role or permission model.** v1 ships a **single admin role**: no role gating on any screen, no hide-vs-disable question, no RBAC matrix. Every mutating action records the actor instead `[G-15]`, and that logging is mandatory. A role model is a post-v1 owner decision. Six screens independently raised this question, which is why the rule lives in the global file.
- **No sample-type distinction.** Sample assignment is simple ON/OFF with multiple, possibly overlapping periods, and exactly one sample set per order even when periods overlap. v1 renders **"sample set" only** — no sample type, no per-type quantity — on internal invoices and picking labels alike. Distinguishing which sample and how many is follow-up work for the moment sample types are introduced `[G-13]`.
- **No custom carrier-label layout, for any carrier.** Carrier labels are each carrier's existing default output, printed verbatim — YUN, DELEO, and any carrier added later such as FedEx. Only the internal invoice is ours to design `[G-4]`, `shipping-label.md` §2.
- **Label and invoice layout content is Phase 3-1**, a separate owner session. The specs define print *behavior*, *which* carrier, *what is captured*, and *what happens on failure* — never what is drawn on the artifact.
- **Procurement Hub is excluded from this spec set entirely** (owner decision, 2026-08-02). No link, no reference, no dependency — and since 2026-08-04 **without exception**. The one exception used to be a costing **read** for the Inventory audit loss calculation; that calculation no longer exists (owner removed loss-amount from the stock audit; the audit is counts-only), so the read is withdrawn with it.
- **No money in the stock audit.** The Inventory stock audit reports **count differences only** — `−1`, `+1`, `0`. There is no `Loss (₩)` column, no loss total, no `Loss = Diff × cost` rule, no product-cost lookup and no `₩` figure anywhere in the audit flow (owner decision, 2026-08-04). This is a **must NOT exist** boundary, not a deferral: `stock-status.md` §9.1 asserts its absence. It does **not** touch money elsewhere in the set — Inbound Request's `Unit Cost` / `JIT Price` and Order Detail's order amounts are unaffected and remain specified as before.
- **No dedicated failed-dispatch queue screen.** Failed Slack dispatches retry in a background queue with exponential backoff and are flagged in the admin notification log after N retries; there is no UI for it in v1 `[G-2]` routing section.
- **No sheet integration for Closing.** The SS Daily Shipping Status spreadsheet was retired outright; Closing History (daily snapshots plus per-day CSV) replaces it wholesale.
- **No photo capture** anywhere on inbound artifacts or the unrecognized flow — removed permanently, not deferred.
- **No automatic carrier capture** on any inbound or outbound event, on any screen.
- **No FX conversion** on Order Detail; each amount renders in its own currency.

Two structural cautions:

1. **Cross-page disagreements are declared, not hidden.** Each spec's `[X-n]` / `CP-n` / `[RTO-X-n]` list names the places where two screens still describe the same fact differently, states that page's position, and names what must change where. None of them blocks implementing the screen you are on — but implementing one screen's write against another screen's contract will produce two incompatible behaviors. If your work spans two screens, read both lists first. `view-orders.md` §9.5 `CP-2` is the sharpest example: it explicitly tells you **not** to implement `ready-to-outbound`'s per-line `OUTBOUNDED` write against the View Orders / Order Detail contract as it stands.
2. **The order list table on Order Management is unchanged from the current admin** and is deliberately omitted from both the wireframe and the spec. Do not redesign it.

---

## 8. Wireframes

Nine live builds on GitHub Pages, auto-updating on edit:

| Screen | URL |
|---|---|
| View Orders | https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/view-orders/ |
| Order Detail | https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/order-detail/ |
| Ready to be Outbounded | https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/ready-to-outbound/ |
| Inventory | https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/stock-status/ |
| Order Management Dashboard | https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/order-management/ |
| Unrecognized Tracking | https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/tracking-missing/ |
| Closing | https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/closing/ |
| Inbound Request | https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/inbound-request/ |
| Shipping Labels | https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/shipping-label/ |

**How to read a wireframe.** Each drawing reproduces the corresponding current admin screen 1:1, and **the purple numbered annotations mark the new or changed elements** — everything else matches the current admin as-is. The numbered dot on the screen keys into the legend block beneath it, and that legend entry is the `[L-*]` unit the spec specifies. Toggle the annotation layer with the `Hide annotations` button; note that several QA assertions read legend text, so leave annotations on while running `[WF]` scenarios.

**Unrecognized Tracking is a wholly new admin page** — its legend header says so directly (`Unrecognized Tracking — Changes (new admin page)`), and the spec records that before it existed, parcels whose barcode scan failed were physically set aside on a shelf and chased down in Slack and spreadsheets. There is no "current admin" baseline to compare it against; the whole screen is new.

**Closing likewise has no current-admin screen behind it.** It replaces a spreadsheet ritual: paste the day's tracking numbers into Excel, run a conditional-format duplicate check, eyeball each order for outbound status, walk to Zero Packing for anything suspicious, then copy the totals into the SS Daily Shipping Status sheet. Steps 1–2 become the scan verdict, step 3 becomes modal M1, and step 4 is retired outright.

**The purple top bar on every wireframe is chrome, not product.** The `.wf-bar` state-switcher exists so a reviewer can jump between states in a static mock; it must not exist in the admin. Where a screen has real in-page tabs — Closing's `[Closing | Closing History]`, Inbound Request's `[New Request | Request List]` — those are product and are specified as such.

Wireframe demo data is scaffolding. Where a mock value contradicts another mock value, §2.3 of the spec says so explicitly; those are declared artefacts, not contradictions in the contract.

---

## 9. Before you start

- Read `PREREQUISITES.md` in this directory. It lists what SkinSeoul must have in place — print agent, label stock, Slack channels and bot, master data — before parts of this can be built or tested. Several items block whole feature areas. Its §D now holds **one** true owner decision, `D3` (morning-check run time); `D2` (WooCommerce sync direction) was reclassified `Joint` on 2026-08-04 as a read-the-current-admin-and-document task, and `D1` was retired the same day when the audit costing basis died with the loss column. **`A3`** is likewise no longer a procurement item — the current admin's existing carrier-label acquisition path is inherited as-is.
- The findings ledger from the pre-handoff review is at `_plans/_prehandoff/ledger.md` if you want the audit trail: what was checked, what was found, what was refuted, and why.
- **Notion is a mirror, not a source.** The spec pages under the Notion index are republished from these files. If the two ever disagree, this repository wins.
