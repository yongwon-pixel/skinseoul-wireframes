# QA scenario export — `scenarios.csv` / `scenarios.json`

Every QA scenario in the eight screen specs, in structured form, so nobody retypes one by hand.

**Regenerate:** `python3 _verify/export_scenarios.py` — reads the specs, writes both files next to itself. Re-run it after any §8 edit; the files are generated artefacts and are not hand-edited.

## What is in it

| Field | Meaning |
|---|---|
| `id` | Scenario id, e.g. `QA-IMP-15`. Unique per page, **not** globally — `QA-M1-03` exists on several pages, so key on `(page, id)`. |
| `page` | Spec slug (`order-management`, `stock-status` = the Inventory screen, …). |
| `tier` | `WF` = runnable against the wireframe today · `ADMIN` = acceptance criteria for the built admin. |
| `negative` | True when the scenario asserts something must **not** happen. |
| `block` | The §8 block the scenario belongs to (`IMP`, `SMP`, `E`, `DC`, …). |
| `refs` | The `[E-n]` / `[BR-n]` / `[G-n]` / `[L-*]` ids the scenario is anchored to, `;`-separated. |
| `title` | The scenario's own headline, where it has one. |
| `given` / `when` / `then` | The three clauses. `And` / `But` continuations stay attached to the clause they extend, and any preamble before the first keyword is kept on `given` so no wording is dropped. |
| `section` | The §8 sub-heading it sits under. |
| `source_line` | Line number in the spec — open the source when the prose matters more than the fields. |
| `form` | `table` or `prose`. The specs use both; the parser handles both. |

`scenarios.csv` is UTF-8 with BOM so Excel opens the Korean strings correctly.

## Census (2026-08-04)

| Page | Total | `[WF]` | `[ADMIN]` |
|---|---|---|---|
| view-orders | 279 | 136 | 143 |
| order-detail | 161 | 69 | 92 |
| ready-to-outbound | 201 | 93 | 108 |
| stock-status (Inventory) | 200 | 75 | 125 |
| order-management | 171 | 77 | 94 |
| tracking-missing | 168 | 66 | 102 |
| closing | 193 | 74 | 119 |
| inbound-request | 130 | 57 | 73 |
| **Total** | **1,503** | **647** | **856** |

## Why you can trust the numbers

Two checks run against the source, not against the export:

1. **Nothing is dropped.** Every id defined in a §8 of every spec appears in the export — 1,503 defined, 1,503 extracted, **0 missing**.
2. **The tier column reconciles with what actually runs.** The `[WF]` set is compared id-for-id against the eight runners in `_verify/prehandoff/`. All eight pages match exactly, and the total is **647 = the number the runners execute**.

One known artefact: `qa-view-orders.py` still holds a dead line, `JS["QA-S6-03b"] = ""  # placeholder removed`. It is not a scenario, is never executed, and is correctly absent from the export.

Tier detection reads only a **tier field** — the dedicated table cell, or the bracket in a prose header — never the body. A scenario that merely *mentions* another tier in its prose (RTO's `QA-E-20` says "the `[WF]` half is covered by QA-M1-03") is not mis-tiered by it.
