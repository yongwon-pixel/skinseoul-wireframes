# RV — Independent Re-Verification · `order-management.md` v1.2

**Method:** independent re-verification of the remediation pass. The verifier neither wrote the spec nor performed the remediation. Every count was re-derived by direct extraction (Python) over the spec and the wireframe; every resolved defect was confirmed by quoting the current file; 16 `[WF]` scenarios were re-executed with Playwright (headless Chromium, viewport 1500×1000) against `file:///Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/order-management/index.html`. The remediator's report was treated as claims, not evidence.
**Spec:** `wms2/specs/order-management.md` (1975 lines, "Spec version 1.2 · 2026-08-03" in header; §10 carries the v1.2 row)
**Prior findings:** `_verify/m1-order-management.md` (1 MAJOR + 8 MINOR) · `_verify/m2-order-management.md` (4 FAIL + 1 AMBIGUOUS, S-1…S-11)
**Harness:** `scratchpad/rv-qa-om.py` + `rv-qa-om.results.json` (session scratchpad)
**Date:** 2026-08-03

---

## 1. Count re-derivation — all claims verified true

| Quantity | Remediator claims | Independently derived | Match |
|---|---|---|---|
| QA scenarios | 171 | **171** (definition lines and distinct ids agree) | ✓ |
| `[WF]` / `[ADMIN]` | 77 / 94 | **77 / 94** | ✓ |
| Negative tests | 77 = 45.0 % | **77 = 45.0 %** (`(neg)` markers) | ✓ |
| Per block | IMP 62 · SMP 50 · LST 17 · CMT 24 · GBL 18 | **62 · 50 · 17 · 24 · 18**, each contiguous 1..n, 0 dups, 0 gaps | ✓ |
| §8.0 self-declaration | — | declares exactly the derived numbers (171 / 77 / 94 / 77=45.0 % / per-block) | ✓ |
| E ids | E-1…E-100 contiguous, 0 uncovered | **100 distinct, 1..100, no gaps**; scenario-**body** citation leaves exactly `E-9` and `E-42` at zero — both declared unasserted in §8.0 with reasons | ✓ |
| DC ids | DC-1…DC-29 all in §8.6, 0 phantom | **29 distinct, 1..29; §8.6 cites 1..29 exactly, no phantom id** | ✓ |
| BR ids | BR-1…BR-34 | **1..34 contiguous, no gaps** | ✓ |
| `[G-n]` citations | all 15 cited | **G-1…G-15 all cited** | ✓ |
| §3 legend keys | 16 `### 3.x [L-…]` | **16**: `1, M1, M1b, 2a, 2b, M2, M3, 3, 4, 5, F1…F6` (identical to M1's v1.1 list — no renumber) | ✓ |
| `MM-DD` shorthand | 0 | **0** | ✓ |
| Korean characters | 0 | **0** (`재고` gone from QA-IMP-19) | ✓ |
| Tags outside `[WF]`/`[ADMIN]` | 0 | **0** | ✓ |

---

## 2. Resolution table

### M1 (coverage audit)

| # | Defect | Verdict | Evidence (current file) |
|---|---|---|---|
| M1-1 MAJOR | 20 E-ids with no QA scenario | **RESOLVED** | All 18 assertable ids now covered by exactly the claimed new `[ADMIN]` scenarios: E-4→QA-IMP-53, E-6→54, E-8→55, E-16→56, E-17→57, E-55→58, E-58→59, E-65→60, E-78→61, E-79→62 · E-26→QA-SMP-44, E-31→45, E-34→46, E-44→47, E-60→48, E-66→49, E-86→50 · E-50→QA-CMT-24. E-34 is the required `[ADMIN]` cross-reference ("Dual-view divergence `[E-34]` `[G-13]` (BR-8) — cross-reference"). §8.0 declares E-9/E-42 "intentionally left unasserted (declared, not silent)" with per-id reasons. Zero-body-citation set = {9, 42} exactly. |
| M1-2 MINOR | 7 E-ids uncited outside their §7 row | **RESOLVED** | §3 now cites each: E-4 ×2, E-6 ×3, E-31 ×1, E-34 ×1, E-55 ×1, E-78 ×1, E-79 ×1 (counted inside `## 3` only). |
| M1-3 MINOR | 42 scenarios missing a `When` | **RESOLVED** | Scan of all 171 scenario blocks: **0** blocks lack a `When` clause. |
| M1-4 MINOR | 3 §8.6 cells over-claim (DC-9/10/14) | **RESOLVED** | QA-IMP-33 body now contains `[DC-9]`; QA-IMP-52 body contains `[DC-10]`; §8.6 DC-14 row reads `QA-SMP-10, QA-SMP-12, QA-SMP-13 (absence), QA-SMP-43, QA-SMP-45, QA-SMP-49, QA-SMP-50` — the `(absence)` marker applied as prescribed. |
| M1-5 MINOR | `[G-7]` body restated in §6.1/§10 | **RESOLVED** | Phrase "personal notification while the channel doubles" absent from spec; 11-word shingle diff of the G-7 body vs spec returns **0** hits. §10 row now says "notification semantics are `[G-7]`'s and are not restated here." |
| M1-6 MINOR | BR-31/33/34 bypass the PD register | **RESOLVED (sanctioned alternative)** | §9.1 now carries explicit rows for **BR-31**, **BR-33**, **BR-34** as spec-level defaults with reversal impact ("It changes *which orders get sampled*…" etc.). M1's fix offered "Alternatively, list them in §9.1" — that alternative was taken; the PD register itself is unedited. |
| M1-7 MINOR | QA-IMP-19 dead pointer + Korean token | **RESOLVED** | Then clause now reads "…the only occurrence of `stock` in `#m-import` is inside `.note.mkt` (§3.2.7), in the phrase `regardless of stock or inbound status`"; the Korean probe is dropped with an explicit parenthetical explaining why. Playwright re-run PASS. |
| M1-8 MINOR | QA-LST-12 nav labels vs `<br>` DOM | **RESOLVED** | See M2 S-3 below. |
| M1-9 MINOR | §9.1 PD list omits PD-9 | **RESOLVED** | §9.1 closing paragraph: "One further PD id appears in this document without being a dependency: **`[PD-9]`** is cited once, untagged, in §10's… row purely as a **non-applicable cross-reference**…" |

### M2 (adversarial QA)

| # | Defect | Verdict | Evidence |
|---|---|---|---|
| S-1 (F-3) | QA-GBL-14 focus contradiction | **RESOLVED** | Clause now scanner-scoped: "no code path returns focus to a **scan field** after an action… the document's only two `.focus()` call sites are the custom-input affordances on `#otCustom` (§3.2.2) and `#picCustomIn` (§3.2.3), which QA-IMP-06 and QA-IMP-09 require… their presence is **not** a `[G-1]` violation." Playwright: source has exactly 2 `.focus()` sites (lines 356, 418) resolving to `otCustom`/`picCustomIn` → **PASS**. |
| S-2 (F-1) | QA-IMP-12 `M1b` dot | **RESOLVED** | When clause reads via §8.0 rule 5c (`th.firstChild.textContent`); an explicit And-clause states raw `textContent` of the 7th cell is `Carrier (auto)M1b` and "is **not** a defect". Playwright: own-text = the 7 expected headers, raw7 = `Carrier (auto)M1b` → **PASS**. |
| S-3 (F-2) | QA-LST-12 `<br>` quick links | **RESOLVED** | Scenario now joins across `<br>` per §8.0 rule 5a **and** states the raw `textContent` values (`AgentTelemetry`, `RoleAssets`, `Shared AssetHealth`, `SkinSeoulWP Admin`). Playwright: both forms match exactly → **PASS**. |
| S-4 (F-4) | QA-CMT-05 "contains exactly" unsatisfiable | **RESOLVED** | Now asserts `.empty` = `No matching comments`, `.it` length 0, `.paneheader` = `0 results · newest first · click to open the order` separately, with a parenthetical warning "never the pane as one string". Playwright: all three hold → **PASS**. |
| S-5 (A-1) | QA-CMT-21 no concrete input | **RESOLVED** | When clause: "I type `4` into `#inbox1 .csearch input`", with the empty-query trap documented. Playwright: 5 rows in the exact expected order → **PASS**. |
| S-6 | Rule-5 whitespace normalisation | **RESOLVED** | §8.0 rules **(5a)** `<br>` → one space (QA-LST-12), **(5b)** `<label>` text trimmed (QA-SMP-02/03, QA-LST-07), **(5c)** trailing `.dot` excluded, all present. Playwright: QA-SMP-02, QA-SMP-03, QA-LST-07 → **PASS**. |
| S-7 | QA-CMT-02 right-aligned probe | **RESOLVED** | Geometric probe specified (`h.right - s.right <= 20`, `s.left - h.left >= 100`) with the `marginLeft:'auto'` trap explicitly forbidden. Playwright: 14 px / 291 px → **PASS**. |
| S-8 | CSSOM hex re-serialisation | **RESOLVED** | §8.0: "an authored `#EBE1FF` comes back as `rgb(235, 225, 255)`. Either form satisfies a stylesheet-rule assertion"; QA-LST-02 restates it inline. Playwright: CSSOM returns the rgb form, accepted → **PASS**. |
| S-9 | QA-IMP-11 selector | **RESOLVED** | Located as `document.querySelector('#m-import table.tbl').previousElementSibling`. Playwright: `<b>` with the exact string → **PASS**. |
| S-10 | "identical content" basis | **RESOLVED** | §8.0 rule 6 fixes the basis: `…querySelector('.modal').innerHTML` string equality, "No other basis is permitted." Playwright: QA-IMP-02 and QA-SMP-28 innerHTML-identical across entry paths → **PASS**. |
| S-11 | WF-15…21 not in the register | **RESOLVED (with open orchestrator item)** | `_plans/_wireframe-fixes.md` **§F** ("Appended 2026-08-03 — found while writing `specs/order-management.md`") carries `[WF-15 · proposed]` … `[WF-21 · proposed]`; §8.0 rule 7 defines the `· proposed` suffix and points at §F. The bare-number collision with concurrent passes is explicitly documented in §F (key on full token + file), and §F records the factual correction that this page renders `Unstar to remove from list` (index.html:187), which matches §3.10/QA-CMT-03. Resolution of the number collision is correctly left to the orchestrator — no spec renumbering occurred. |

### M3a / M3b rows naming this page

| Item | Verdict | Evidence |
|---|---|---|
| D7 hub strings | **RESOLVED (declared divergence)** | §3.10 carries "**Declared cross-page string divergence (cross-page defect M3a D7)**" naming the 2/2/2/1 no-majority split; `Unstar to remove from list` is byte-exact to the wireframe (verified line 187) and kept per `_review` §3.9. |
| D10 stale VO cross-ref | **RESOLVED (flagged)** | §3.8: "**Stale cross-reference elsewhere (cross-page defect M3a D10):** `view-orders`'s State-5 legend footer… predates this removal…" |
| D14 DC-28 naming | **RESOLVED (declared)** | §5: "**Declared name divergence on a shared *concept* (cross-page defect M3a D14)**… named `idempotency.duplicate_rejected` on View Orders…" — no unilateral rename. |
| D16 directory link form | **RESOLVED** | §6.3 uses `../order-detail/#{orderNo}`-style directory forms. |
| M3b silent N/A | **RESOLVED** | New **§6.7** ("Mandatory-inclusion items with no `[G-n]` anchor — explicit N/A, never silent") covers items 9, 10, 11; §9.2 has the matching "**JIT and JIT residual stock**… **JIT never appears on this screen**" row. `JIT` now appears 11× where it was previously absent. |

**Totals: 25 defects/fix-items checked → 25 RESOLVED · 0 PARTIAL · 0 NOT RESOLVED · 0 REGRESSED.**

---

## 3. QA re-run — 16 `[WF]` scenarios, Playwright, fresh page + `__qaSentinel` per scenario

Priority given to the five previously FAIL/AMBIGUOUS, then every scenario a hardening fix (S-6…S-10) touches, then two controls.

| Scenario | Prior state | RV verdict | Evidence |
|---|---|---|---|
| QA-IMP-12 | FAIL (F-1) | **PASS** | own-text 7 headers exact · raw7 `Carrier (auto)M1b` |
| QA-LST-12 | FAIL (F-2) | **PASS** | joined = 4 expected strings · raw = 4 declared `textContent` values · brand/menus/badge/chip/Logout present |
| QA-GBL-14 | FAIL (F-3) | **PASS** | 0 scan fields · 0 autofocus · activeElement=body · exactly 2 `.focus()` sites (lines 356/418 → `otCustom`, `picCustomIn`) |
| QA-CMT-05 | FAIL (F-4) | **PASS** | `.empty`=`No matching comments` · `.it`=0 · `.paneheader`=`0 results · newest first · click to open the order` |
| QA-CMT-21 | AMBIGUOUS (A-1) | **PASS** | query `4` → 5 rows `MKT-40233, MKT-40218, 421771, MKT-40191, 421502` |
| QA-CMT-02 | latent trap (S-7) | **PASS** | geometric probe: right gap 14 px ≤ 20 · left gap 291 px ≥ 100 |
| QA-LST-02 | latent trap (S-8) | **PASS** | `--mkt #7C3AED` · CSSOM hover rule `rgb(235, 225, 255)` accepted per rule |
| QA-SMP-02 | latent trap (S-6/5b) | **PASS** | trimmed labels exact · first radio checked |
| QA-SMP-03 | latent trap (S-6/5b) | **PASS** | `2026-07-23`/`10:00` · placeholders `End date`/`Time` · `forever (no end date)` checked |
| QA-LST-07 | latent trap (S-6/5b) | **PASS** | full inventory exact (dates/inputs/selects/checkboxes/buttons in order) |
| QA-IMP-11 | latent trap (S-9) | **PASS** | `previousElementSibling` is `<b>` `Preview — mkt_seeding_batch3.xlsx · 12 rows parsed · 0 errors` |
| QA-IMP-02 | latent trap (S-10) | **PASS** | `.modal` innerHTML identical across wf-bar vs filter-bar entry (4226 chars) |
| QA-SMP-28 | latent trap (S-10) | **PASS** | `.modal` innerHTML identical across wf-bar vs action-row entry |
| QA-LST-01 | control | **PASS** | placeholder text + dot `4` |
| QA-IMP-19 | reworded (M1-7) | **PASS** | 0 forbidden substrings · `stock` ×1 inside `.note.mkt` |
| QA-IMP-35 | defect-doc control | **PASS** | `colspan=6` vs 7 `<th>` reproduced — defect-documenting scenario kept verbatim and still true |

**16 / 16 PASS · 0 FAIL · 0 AMBIGUOUS.** Two first-run FAILs (QA-GBL-14, QA-LST-07) were traced to this harness's own extraction errors (a regex mis-capture of the second `.focus()` receiver; `input[type="date"]`/`input[type="text"]` attribute selectors against markup that uses `class="date" type="text"` and type-less `class="inp"`), repaired, and disclosed here — the spec was correct in both cases.

---

## 4. Regression checks

| Check | Result |
|---|---|
| Legend coverage | **intact** — §3 carries the same 16 `[L-…]` heading keys as v1.1; §2's 9-unit accounting unchanged |
| ID renumbering | **none** — E-1…100, DC-1…29, BR-1…34 all contiguous; QA additions are block-tail appends (IMP 52→62, SMP 43→50, CMT 23→24; LST/GBL unchanged); spot-check QA-IMP-35 carries its v1.1 meaning verbatim |
| New global-rule restatements | **none** — full 11-word shingle diff of `_global-rules.md` against the spec returns exactly **1** hit ("internal invoice and picking artifacts show which sample and how many"), located in §10's decision-log row `Sample dual-view confirmed` — a `_review` §3.11 decision-record paraphrase that already existed in v1.1 and that M1 itself classed as acceptable. The G-7 cluster M1 flagged is gone. |
| §8.6 matrix | DC-1…29 complete, 0 phantom scenario ids |
| Unasserted-edge declaration | E-9/E-42 declared in §8.0 with reasons; body-citation extraction confirms these are the only two zero-cited ids |

---

## 5. Notes (non-blocking)

1. **QA-LST-07 wording "a date input valued `2026-06-01`"** — the wireframe authors these as `<input class="date" type="text">`. A runner who reads "date input" as `input[type="date"]` finds nothing (this harness did, first run). Same family as the traps S-6…S-9 closed; a five-word clarification ("`input.date`, authored `type="text"`") would finish the set. Does not block: the element is findable by value and the assertion passes.
2. **WF register bare-number collision** (`WF-15`/`WF-16` claimed by concurrent passes) is documented, not resolved — resolution is explicitly an orchestrator/owner call per `_wireframe-fixes` §F. The spec cites only the collision-proof full tokens (`[WF-15 · proposed]` + file), so it is not blocked by the outcome.
3. §F's factual correction (order-management renders `Unstar to remove from list`, not `…from the list`) was independently confirmed against `index.html:187`.

---

## 6. Verdict

**READY-WITH-NOTES.**

Every count the spec asserts about itself is true under independent re-derivation. All 9 M1 defects, all 5 M2 blockers, all 6 M2 hardening items, and the M3a/M3b items naming this page are resolved in the current file, with zero regressions in legend coverage, ID stability or global-rule hygiene. The re-run sample — deliberately concentrated on every scenario that previously failed or carried a latent trap — passes 16/16 with byte-exact evidence. The two notes above (one residual selector-wording nicety, one cross-file register collision owned by the orchestrator) are the only reason this is not an unqualified READY; neither blocks implementation or QA execution of this spec.
