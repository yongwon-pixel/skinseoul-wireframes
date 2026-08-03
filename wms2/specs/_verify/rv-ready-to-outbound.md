# RV — Independent Re-Verification · `ready-to-outbound.md` v1.2

**Method:** post-remediation re-verification. The verifier neither wrote the spec nor applied the fixes. Every count re-derived by script; every fix site read in the current file; QA re-run with a freshly written Playwright harness (not M2's).
**Date:** 2026-08-03
**Target:** `wms2/specs/ready-to-outbound.md` (1,853 lines, header reads **Spec version: 1.2 · Date: 2026-08-03**)
**Wireframe:** `wms2/ready-to-outbound/index.html` (486 lines, unchanged)
**Inputs re-checked:** `_verify/m1-ready-to-outbound.md` · `_verify/m2-ready-to-outbound.md` · remediator's claim list
**Harness:** `/private/tmp/claude-501/-Users-yongwon-yongwon-sync/635405b8-dea2-4665-89c5-efd98bf60282/scratchpad/rv_rto_qa.py` (Playwright, headless Chromium, 1440×900, fresh load per scenario)

---

## 1. Count re-derivation (all independent, none trusted)

| Metric | Spec §8.0 / remediator claims | RV derived | Verdict |
|---|---|---|---|
| Total QA scenarios | 201 | **201** (0 duplicates, 0 numbering gaps in any block) | match |
| `[WF]` / `[ADMIN]` | 93 / 108 | **93 / 108**; per-block split matches the §8.0 table row-for-row (e.g. QA-M1 12/3, QA-E 6/33, QA-DC 0/28) | match |
| Negatives | 102 = 50.7 % | **102 = 50.7 %** under §8.0's stated rule (header tag **or** inline `**· negative:**`); per-block negatives match all 18 rows (QA-M1 7, QA-F 7, QA-DC 6, QA-E 29 …) | match |
| DC | 28, 1:1 with QA-DC | **28** register rows, contiguous 1–28; QA-DC ids exactly {1…28} | match |
| BR | 37 + BR-9b | **38 register rows = BR-1…BR-37 + BR-9b**, no renumbering. (BR-29 has no bracketed `[BR-29]` citation outside its own register row — same as v1.1, not a regression.) | match |
| E | 80 = E-1…E-79 + E-15b | **80** defined, contiguous, `15b` present, no gaps | match |
| NE | 12 | **12** (NE-1…NE-12) | match |
| Dev decisions | D-1…D-18 | **D-1…D-18** all present (D-18 = self-mention, new) | match |
| §3 subsections | 23 | **23** (§3.1–§3.23) | match |
| PD tags | 30 distinct; "125 tagged occurrences, only PD-16's removed" | **30 distinct**. Occurrence total is counting-convention-dependent (RV's `\[PD-` regex counts 161; M1 counted 154 on v1.1) — the load-bearing claims hold: 30 distinct ids, PD-16 no longer *justifies* any behavior (see D-5 below), no other PD id lost | match (with counting-convention note) |

**Verdict: every §8.0 figure and every structural range the remediator claimed reproduces exactly under independent extraction.**

---

## 2. Resolution table — M1 defects

| Defect | Severity | Status | Evidence (current file) |
|---|---|---|---|
| **D-1** invariant provably false | MAJOR | **RESOLVED** | §3.13 (line 451): "**Reconciliation invariants (QA-assertable) — two statements, not one**" — (a) unconditional `Σ(Total Items) == {items}`; (b) conditional `{units} = Σ(qty of pickable — i.e. inbounded — lines only)`, equal to `{items}` "**only when every selected order is fully inbounded**"; worked divergent case `{items}=11 / {units}=10` (line 456). QA-L13-04 rewritten "one unconditional, one conditional" with the explicit warning "**Asserting (b) unconditionally is itself the defect**" (line 1511-1514); QA-L13-05 carries "with the same non-inbounded offset" [E-46]. |
| **D-2** one exclusion subtext for five reasons | MAJOR | **RESOLVED** | §3.4 step 6 (line 277): fixed phrase per [DC-21] enum value (`lines_not_inbounded` → `items not inbounded` · `status_forbids_outbound` → `status blocks outbound` · `already_outbounded` · `left_ready_pool` → `no longer ready` · `empty_order` → `no line items`), single- and multi-clause forms in enum order, "One hard-coded `items not inbounded` for all five reasons is forbidden". Bulk Print Labels counterpart added §3.3 (line 240, [DC-28] enum: `no carrier assigned` / `no label template` / `order not printable`). QA-L4-08 now demands `2 excluded — 1 items not inbounded · 1 status blocks outbound` and marks the old single-phrase form "**a FAIL here**" (line 1227); E-53 (883), E-61→QA-L3-07 (`1 excluded — no carrier assigned`, line 1187), QA-L6-08 (1318), QA-DC-21 (1677) all reason-aware. |
| D-3 PD-71 mis-tagged OWNER-PENDING | MINOR | **RESOLVED** | All 3 sites now `[PD-71 · NO-DEFAULT]`: §6.3 line 810 ("must not be tagged `OWNER-PENDING`"), §9.1 line 1714, §9.2 line 1729; decision-log row 1838 says "PD-71 — **NO-DEFAULT**, cited as context only". Zero `PD-71 · OWNER-PENDING` occurrences remain. |
| D-4 E-49 uncovered by QA | MINOR | **RESOLVED** | QA-L4-01 (line 1200) now asserts the `AudioContext` is "**constructed inside this click gesture** … [G-3a] [E-49]"; coverage map line 1695: "`[E-49]` is carried by QA-L4-01". |
| D-5 PD-16 cited beyond its scope | MINOR | **RESOLVED** | §6.1 line 766: "**not decided by any register entry**: `[PD-16]`, previously cited here, decides only that the *system* match-confirm auto-comment suppresses the mention … That citation is withdrawn (2026-08-03). The behavior is therefore a **developer decision [D-18]** bounded by [BR-30]". D-18 row present at line 1765. Remaining `[PD-16]` mentions are the withdrawal record itself, not justifications. |
| D-6 shorthand dates | MINOR | **RESOLVED** | grep for `07-13` / `07-22` / `07-23` outside `2026-` prefixes and the verbatim `07-21 09:40` wireframe string: **0 hits**. |
| D-7 JIT residual item silent | MINOR | **RESOLVED** | §9.1 line 1717: "**JIT residual stock** … `stock-status.md`. This page lists only orders that are **ready to ship**; residual stock is not an order and never surfaces here. Stated explicitly … because the matrix codes this item `n`". |
| D-8 G-body restatements | MINOR | **RESOLVED** | All three flagged phrases return 0 grep hits. §1.5 (line 60) now "[G-15] applies unchanged … Bulk Outbound carries no gate of its own"; BR-26 (631) "[G-15] applies unchanged. Page delta: no control here adds a gate of its own"; BR-10 (615) "[G-4] governs all three print surfaces … Page delta: carrier resolution is per order, never per batch"; §6.5 (838) delta-only with [G-3a]/[G-3b]/[G-3c]. |
| D-9 `{skus}` undefined | MINOR | **RESOLVED** | §3.15 table (line 498): "`{skus}` | The count of **distinct SKUs** across the pickable lines … `{skus}` ≤ the number of table rows, and the two diverge exactly when a SKU is shared". |
| D-10 §4.2 carrier row unscoped | MINOR | **RESOLVED** | §4.2 line 674: row retitled "**Inbound Carrier column**…", body "Any **inbound** Carrier field … **Scope note:** the order's **shipping** carrier is a different field entirely — resolved per order for label printing [BR-10] §6.4, stored on [DC-7] … Do not delete that". |
| D-11 NE-2 mapping unbacked | MINOR | **RESOLVED** | QA-L5-02 (line 1261) gains "**· negative:** `[ADMIN]` rider — … **no per-tick row** in the [G-8] audit stream; only [DC-8]'s batch start and finish are persisted `[NE-2]`". Coverage-map entry `[NE-2]` QA-L5-02 now truthful. |
| D-12 QA-E-04 bare `th` | MINOR | **RESOLVED** | QA-E-04 (line 1612): "`document.querySelectorAll('.tbl thead th').length` remains **9**. (Use the qualified selector: a bare `th` count returns **14** …)". QA-L13-03 (1509) same qualification. RV empirical: `.tbl thead th` = 9, bare `th` = 14. |

## 3. Resolution table — M2 findings

| Finding | Was | Status | Evidence |
|---|---|---|---|
| **S-1 / QA-L7-02** | FAIL (spec-culprit) | **RESOLVED — now PASSES** | Rewritten (line 1327-1329): scan scoped to `document.querySelector('.mock').textContent` and `#m-pick`; "`.legend` and `.wf-bar` are exempt and must not be scanned". DOM check: `.mock` closes at `index.html:325`, `.legend` opens at 327 — sibling, not child, so the scoped scan is structurally sound. §8.0 known-artifacts list (line 988) and §2.4 both carry the legend-7 changelog exemption; §4.2's scope narrowed to the shipping surface. **Playwright: PASS** (`inMock:false, inModal:false, inLegend:true`). |
| **S-2 / QA-L5-04** + flaky family | FAIL (unsatisfiable) + 4 flaky | **RESOLVED — now PASSES** | §8.0 gains the running-label reading rule (line 981: "sample after `#pfill.style.width` has reached `20%` or later, never before"); QA-L5-04 rewritten with "discarding every sample taken before … `20%`" and an explanatory note that the absolute form is unsatisfiable (1264-1268). First-tick bound added to QA-M1-11 (1133), QA-L3-01 (1161), QA-L4-02 (1203), QA-L5-03 (1264). Artifact registered as `[RTO-WFX-9]` in spec §2.4 (line 141/158) **and** in `_wireframe-fixes.md` §B (line 87). **Playwright: QA-L5-04 PASS** (22/25 kept samples per run, 0 crossovers after the bound); pre-tick crossover **empirically confirmed present** (6 pre-tick samples still carried the previous action's copy), proving the bound is necessary, not cosmetic. |
| **S-3 / QA-L6-04** | AMBIGUOUS | **RESOLVED — now PASSES** | Four mechanical clauses (line 1289-1294): `.toast` count === 1; computed `backgroundColor === 'rgb(25, 135, 84)'`; stylesheet scan for `toast` selectors containing `--red`; no `failed`/`error`/`partial` in `#toast b`/`small` after each action. **Playwright: PASS** on all four clauses. |
| **S-4 / QA-F-06** | AMBIGUOUS | **RESOLVED — now PASSES** | §8.0 equality-vs-containment rule stated once (lines 983-986); QA-F-06 rewritten as the literal filter expression `[...document.querySelectorAll('*')].filter(e => e.textContent === 'View Order').length === 0` with the legend-footer prose explicitly out of scope. **Playwright: PASS** (0 elements equal). |
| **S-5** negative count off by 2 | MINOR | **RESOLVED** | §8.0 states the rule (line 968: "either form makes the whole scenario a negative … Counting header tags alone undercounts by 2 and is wrong"); table recomputed to 102/50.7 % — **RV recount confirms 102 and every per-block row**. (v1.2 added riders to QA-L4-06/QA-L5-02/QA-DC-09, which moves the total from M2's measured 99 to 102 — internally consistent.) |
| **S-6** auto-dismiss anchor | MINOR | **RESOLVED — now PASSES** | QA-L4-03 (line 1231): "within **3–4 s of becoming visible** — … **not** from the click"; QA-L6-01 (1287) same anchor. **Playwright: toast visible at ~1.31 s post-click, hidden 2.98-3.01 s later — PASS under the anchored reading, would still FAIL under the old click-anchored one.** |
| UNRUNNABLE retags | 0 in M2 | **N/A — correctly none** | No `[WF]`→`[ADMIN]` retags claimed or needed. |

**m3a spot-checks (RTO-naming rows the remediator claims fixed):** BR-22 now order-level, line vocabulary `INBOUNDED`/`PENDING` only, `OUTBOUNDED` forbidden with negative clauses in QA-L4-06 (1218) and QA-DC-09 (1665) and reversal chain §10.1 item 7 (1852) — confirmed. E-75 fan-out "one message per distinct resolved mention" in §3.9 (390), DC-2 (694), §6.1 (764), QA-DC-02 (1658) — confirmed. §1.4 (56) no longer asserts where `OTHER (channel)` renders (ownership handed to [G-5]) — confirmed. BR-34 states the shared BR-51 boundary (line 649) — confirmed. m3a **D20** (`[G-3a]` bracket form) deliberately not fixed — defensible: normalizing in RTO alone would desynchronize it from sibling specs; the fix belongs in `_review.md` §3, which the remediator may not edit.

**`_wireframe-fixes.md` filing:** the progress-label defect is registered as `[RTO-WFX-9]` (§B line 87) with an explicit note explaining the departure from M2's requested "WF-15" — three sibling passes claimed `WF-15` concurrently (collision warning at §F line 167). The spec's references (§2.4, §8.0, QA-L5-04) all resolve to `[RTO-WFX-9]`. Acceptable; the bare-number collision is an ecosystem-level cleanup owned by the orchestrator, not this spec.

---

## 4. QA re-run (independent harness, 20 scenarios, prioritising prior FAIL/AMBIGUOUS)

| Scenario | Prior | RV verdict | Key evidence |
|---|---|---|---|
| QA-L7-02 | FAIL | **PASS** | string absent from `.mock` and `#m-pick`; present only in `.legend` (exempt) |
| QA-L5-04 | FAIL | **PASS** | 0 mode-string crossovers in 47 post-tick samples across both runs |
| QA-L6-04 | AMBIGUOUS | **PASS** | 1 toast · `rgb(25,135,84)` · 0 red toast rules · clean strings ×3 actions |
| QA-F-06 | AMBIGUOUS | **PASS** | 0 elements with textContent === `View Order` |
| QA-M1-11 | flaky | **PASS** | modal closes, fill 100 %, toast exact, 25 kept samples all correct, 5 rows / 3 checked |
| QA-L3-01 | flaky | **PASS** | 25 kept samples, all `Bulk Print Labels in progress … No refresh · selection kept` |
| QA-L4-02 | flaky | **PASS** | 25 kept samples, all `Bulk Outbound in progress … refreshes after completion` |
| QA-L5-03 | flaky | **PASS** | all kept samples match `{Action} in progress — {p}% · {mode} · toast on completion` |
| QA-L4-03 | ambiguous anchor | **PASS** | visible +1.31 s, hidden 3.01 s after appearing, text exact |
| QA-L6-01 | ambiguous anchor | **PASS** | window 2.98 s from visible; computed `top:54px/right:16px` |
| QA-L1-01 | PASS | **PASS** | 5 rows, checked set exact, `.cnt` = `3 selected` |
| QA-L1-02 | PASS | **PASS** | `.bulkbar button` textContents byte-exact ×3 *(first RV attempt failed on the verifier's own guessed selector; the spec's stated selector passes — spec correct, harness error)* |
| QA-M1-01 | PASS | **PASS** | header first text node byte-exact (`3 orders selected · 4 SKUs · 8 units total`) |
| QA-M1-03 | PASS | **PASS** | `A-02-13 → A-03-02 → B-01-07 → B-02-11` ascending |
| QA-L13-03 | PASS | **PASS** | `.tbl thead th` = 9 (bare `th` = 14 as the spec warns); 0 `.cb-ready` |
| QA-E-04 | PASS | **PASS** | 800 px viewport: `overflow-x:auto`, `min-width:1240px`, scrolls, 9 th |
| QA-F-08 | PASS | **PASS** | 14 legend `li`, `.n` order `1 2 3 4 5 6 7 8 14 13 12 9 10 11`, 15 dots (14 + M1) |
| QA-L14-01 | PASS | **PASS** | tabs `All (5) / Inventory (3) / Marketing (1) / JIT (1)`, `All` on |
| QA-L7-01 | PASS | **PASS** | `.jit-badge` = `Fully Inbounded` |
| QA-L6-02 | PASS | **PASS** | toast strings byte-exact for both bulk actions |

**20 / 20 PASS · 0 FAIL · 0 AMBIGUOUS · 0 UNRUNNABLE.** Both prior FAILs and both prior AMBIGUOUS now execute mechanically and pass. The RTO-WFX-9 timing artifact was independently re-observed (pre-tick label crossover in 6 samples), confirming the spec documents a real artifact rather than papering over a passing case.

---

## 5. Regression checks

| Check | Verdict | Evidence |
|---|---|---|
| Legend coverage still complete | **PASS** | 14 `li` + off-screen footnote; 15 dots; §3 still has exactly 23 subsections; QA-F-08 passes live |
| No ID renumbering | **PASS** | DC 1–28, BR 1–37+9b, E 1–79+15b, NE 1–12 all contiguous; QA blocks have no numbering gaps; no id from v1.1 disappeared (BR-29 uncited-but-defined matches v1.1 state) |
| No new global-rule body restatements | **PASS** | the three M1-flagged phrases return 0 hits; replacement texts are delta-only with `[G-n]` citations |
| PD discipline | **PASS** | 30 distinct PDs; PD-71 NO-DEFAULT at all 3 sites; PD-16 survives only as a withdrawal record; PD-51/PD-55 still `· NO-DEFAULT` with no behavior resting on them |
| Header/versioning | **PASS** | v1.2, 2026-08-03; §10 decision-log row for the remediation (line 1840); §10.1 gains chains 7 (BR-22 order-level) and 8 (E-75 fan-out) |
| Wireframe untouched | **PASS** | `index.html` still 486 lines; all RV assertions ran against it unmodified |

---

## 6. Final verdict

**READY-WITH-NOTES.**

Every M1 MAJOR and MINOR defect and every M2 FAIL/AMBIGUOUS is genuinely resolved in the current file, all recomputed counts match to the unit, the previously failing and ambiguous QA scenarios now pass mechanically against the live wireframe, and no regression was found. The notes are external to this spec's correctness:

1. **`[RTO-WFX-9]` is documented, not fixed** — the one-line wireframe repair (write the label before starting the interval) is still pending in `wms2/ready-to-outbound/index.html`; until it ships via `/wf-deploy`, §8.0's first-tick bound remains load-bearing.
2. **`_wireframe-fixes.md` bare-number collision** — three concurrent passes claimed `WF-15`; this spec is internally consistent (`[RTO-WFX-9]` everywhere), but the register needs the orchestrator-level re-keying its own §F warning calls for.
3. **m3a D20** (`[G-3a]` vs `[G-3](a)` bracket form) deliberately left for `_review.md` §3 — correct call, but it means the corpus-wide normalization is still open elsewhere.
