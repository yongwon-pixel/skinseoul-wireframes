# RV — Independent Re-Verification · `order-management.md` v1.2

**Method:** independent empirical re-verification of the remediation pass; the verifier neither wrote the spec nor performed the remediation, and treated the remediator's report as claims, not evidence. Every count re-derived by direct Python extraction over the spec; every defect resolution confirmed by quoting the current file; 16 `[WF]` scenarios re-executed with Playwright (headless Chromium, 1500×1000, fresh page + `window.__qaSentinel='om'` per scenario) against `wms2/order-management/index.html`; regression checked by shingle-diffing v1.2 against the **git v1.1 baseline** (`60d58ec`) and `_global-rules.md`.
**Spec:** `wms2/specs/order-management.md` (1975 lines; header `Spec version 1.2 · 2026-08-03`; §10 carries the v1.2 row)
**Prior findings:** `_verify/m1-order-management.md` (1 MAJOR + 8 MINOR) · `_verify/m2-order-management.md` (4 FAIL + 1 AMBIGUOUS + S-6…S-11)
**Harness:** scratchpad `rv_qa_om.py` + `rv_qa_om.results.json` (session scratchpad; re-runnable)
**Date:** 2026-08-03 · A prior RV pass existed at this path (same date); this file supersedes it — its conclusions were independently reproduced here, not reused.

---

## 1. Count re-derivation — every remediator claim verified true

| Quantity | Claimed | Independently derived | Match |
|---|---|---|---|
| QA scenarios | 171 | **171** definition lines (`**QA-… [WF|ADMIN]( (neg))?**`), 171 distinct ids, 0 duplicates | ✓ |
| `[WF]` / `[ADMIN]` | 77 / 94 | **77 / 94** | ✓ |
| Negative tests | 77 = 45.0 % | **77 `(neg)` = 45.03 %** (floor 25 %) | ✓ |
| Per block | IMP 62 · SMP 50 · LST 17 · CMT 24 · GBL 18 | **62 · 50 · 17 · 24 · 18**, each contiguous 1..n | ✓ |
| §8.0 self-declaration | — | §8.0 declares exactly these numbers | ✓ |
| E ids | E-1…E-100, 0 uncovered | **100 distinct, 1..100, contiguous.** Scenario-body citation (§8.1–8.5) leaves exactly **{E-9, E-42}** at zero — both declared "intentionally left unasserted (declared, not silent)" in §8.0 with per-id reasons | ✓ |
| DC ids | DC-1…DC-29 all in §8.6, 0 phantom | **1..29 contiguous; §8.6 cites all 29; 0 phantom scenario ids** | ✓ |
| BR ids | BR-1…BR-34 | **1..34 contiguous** | ✓ |
| §3 legend keys | 16 `### 3.x [L-…]` | **16**: `1, M1, M1b, 2a, 2b, M2, M3, 3, 4, 5, F1…F6` — identical key set to v1.1 | ✓ |
| `[G-n]` citations | all 15 | **G-1…G-15 all cited** | ✓ |
| `MM-DD` shorthand · Korean · non-WF/ADMIN tags | 0 · 0 · 0 | **0 · 0 · 0** (the `재고` token is gone from QA-IMP-19) | ✓ |
| New scenarios | QA-IMP-53…62, QA-SMP-44…50, QA-CMT-24 | all 18 present, all `[ADMIN]`, appended at block tails (no renumbering) | ✓ |

---

## 2. Resolution table

### M1 (coverage audit) — 1 MAJOR + 8 MINOR

| # | Defect | Verdict | Evidence (current file) |
|---|---|---|---|
| M1-1 **MAJOR** | 20 E-ids with no QA scenario | **RESOLVED** | 18 assertable ids now each cited from ≥1 scenario body; extraction over §8.1–8.5 leaves exactly {E-9, E-42} uncited, and §8.0 declares both with reasons ("within-file duplicate `recipient + SKU` rows — … no assertable artifact either way until dev picks a warning"; "a user without write access — v1 adds no gating at all"). E-34 got the required `[ADMIN]` cross-reference: **QA-SMP-46** "Dual-view divergence `[E-34]` `[G-13]` (BR-8) — cross-reference … the carrier-facing document shows **only** `(+ sample set)` … the internal invoice and the picking artifacts **do** state which sample and how many". |
| M1-2 MINOR | 7 E-ids uncited outside their §7 row | **RESOLVED** | §3 back-references present: `E-4`/`E-6`/`E-55`/`E-78`/`E-79` inside §3.2, `E-31`/`E-34` inside §3.6, `E-34` also in §6.5. |
| M1-3 MINOR | 42 scenarios without a `When` | **RESOLVED** | Block scan of all 171 scenarios: **0** lack a `When` line. |
| M1-4 MINOR | 3 §8.6 cells over-claim (DC-9/10/14) | **RESOLVED** | QA-IMP-33 gained "And the 12 rows now visible are exactly the 12 orders written by that batch's `[DC-9] order.created` events"; QA-IMP-52 gained "And one `[DC-10] order.carrier_assigned` persists per connected row"; §8.6 DC-14 row now reads `QA-SMP-10, QA-SMP-12, QA-SMP-13 (absence), QA-SMP-43, QA-SMP-45, QA-SMP-49, QA-SMP-50` — the `(absence)` marker applied exactly as M1 prescribed (DC-25 precedent). |
| M1-5 MINOR | `[G-7]` body restated in §6.1/§10 | **RESOLVED** | The phrase `personal notification while the channel doubles` occurs **0** times in v1.2 (was present in v1.1 per git `60d58ec`). §6.1's Mention-target cell no longer carries the rule body. See §4 for the full shingle diff. |
| M1-6 MINOR | BR-31/33/34 bypass the PD register | **RESOLVED (sanctioned alternative)** | §9.1 carries explicit rows for **BR-31** ("One operating timezone…"), **BR-33** ("resolves its order set **at submit time**… It changes *which orders get sampled*…"), **BR-34** as spec-level defaults awaiting owner sign-off, with reversal impact. M1 offered "Alternatively, list them in §9.1" — that alternative was taken; the PD register is unedited (it is a binding shared reference). |
| M1-7 MINOR | QA-IMP-19 dead pointer + unreachable Korean token | **RESOLVED** | Then clause now reads "…the only occurrence of `stock` in `#m-import` is inside `.note.mkt` (§3.2.7), in the phrase `regardless of stock or inbound status`"; the Korean probe is dropped with an explicit parenthetical ("§2.2 declares that no Korean string exists anywhere on this page, so a Korean 'stock' probe could never match"). |
| M1-8 MINOR | QA-LST-12 nav labels vs `<br>` DOM | **RESOLVED** | Same fix as M2 S-3 below; Playwright PASS. |
| M1-9 MINOR | §9.1 PD enumeration omits PD-9 | **RESOLVED** | §9.1: "One further PD id appears in this document without being a dependency: **`[PD-9]`** is cited once, untagged, in §10's … row purely as a **non-applicable cross-reference** … Reversing PD-9 changes nothing here. A `[PD-n` token extraction over this document therefore yields 26 distinct ids: 23 + 2 [+1]". |

### M2 (adversarial QA) — 4 FAIL + 1 AMBIGUOUS (S-1…S-5) + hardening (S-6…S-11)

| # | Defect | Verdict | Evidence (spec quote + Playwright re-run) |
|---|---|---|---|
| S-1 (F-3) | QA-GBL-14 focus contradiction with QA-IMP-06/09 | **RESOLVED** | Clause is now scanner-scoped: "**no code path returns focus to a scan field after an action**… the document's only two `.focus()` call sites are the custom-input affordances on `#otCustom` (§3.2.2) and `#picCustomIn` (§3.2.3), which QA-IMP-06 and QA-IMP-09 require… their presence is **not** a `[G-1]` violation. A runner must not read 'no focus is ever moved' into this scenario." Re-run: 2 `.focus()` sites (`otCustom`, `picCustomIn` toggle), 0 autofocus, activeElement=body, 0 scan-like inputs → **PASS**. |
| S-2 (F-1) | QA-IMP-12 `M1b` dot in 7th `<th>` | **RESOLVED** | When clause reads cells "per §8.0 rule 5c — `th.firstChild.textContent`, which excludes the `<span class="dot">`"; And-clause: "the raw `textContent` of the seventh cell is `Carrier (auto)M1b` … the dot is intentional chrome … **not** a defect." Re-run: own-text = the 7 exact headers, raw7 = `Carrier (auto)M1b` → **PASS**. |
| S-3 (F-2) | QA-LST-12 `<br>` quick links | **RESOLVED** | Now asserts both forms: "joining across its `<br>` with a single space — `Agent Telemetry`, `Role Assets`, `Shared Asset Health`, `SkinSeoul WP Admin`" and "their raw `textContent` values are `AgentTelemetry`, `RoleAssets`, `Shared AssetHealth`, `SkinSeoulWP Admin` … deliberate and … **not** a defect." Re-run: both forms match byte-exact → **PASS**. |
| S-4 (F-4) | QA-CMT-05 "contains exactly" unsatisfiable | **RESOLVED** | Now asserts three nodes separately: "`[data-pane="csr"] .empty` reads exactly `No matching comments`, `[data-pane="csr"] .it` has length `0`, and `[data-pane="csr"] .paneheader` reads exactly `0 results · newest first · click to open the order`", with the warning "assert the two nodes separately, never the pane as one string." Re-run: all three hold → **PASS**. |
| S-5 (A-1) | QA-CMT-21 no concrete input | **RESOLVED** | "When I type `4` into `#inbox1 .csearch input` — the query that matches every row in the demo corpus", empty-query trap documented. Re-run: 5 rows in the exact declared order (3 `MKT-` + 2 numeric) → **PASS**. |
| S-6 | Whitespace normalisation for label text | **RESOLVED** | §8.0 rule 5 now: "Byte-exactness is applied … **after** exactly three declared normalisations, and after no others" — **(5a)** `<br>` → one space, **(5b)** `<label>` text trimmed, **(5c)** trailing `.dot` excluded. Re-run QA-SMP-02, QA-SMP-03, QA-LST-07 → **PASS** (trimmed labels byte-exact). |
| S-7 | QA-CMT-02 "right-aligned" probe | **RESOLVED** | Geometric probe specified: "`h.right - s.right <= 20` and `s.left - h.left >= 100`. (Do **not** assert `getComputedStyle(small).marginLeft === 'auto'` …)". Re-run: right gap 14 px, left gap 291 px → **PASS**. |
| S-8 | CSSOM hex re-serialisation | **RESOLVED** | QA-LST-02: "read back out of `cssRules[].cssText` the CSSOM re-serialises `#EBE1FF` as `rgb(235, 225, 255)`, and either form satisfies this assertion." Re-run: CSSOM returned the rgb form, accepted → **PASS**. |
| S-9 | QA-IMP-11 no selector | **RESOLVED** | "located as `document.querySelector('#m-import table.tbl').previousElementSibling` (the `<b>` immediately preceding the preview table)". Re-run: `<b>` with the exact string → **PASS**. |
| S-10 | "identical content" undefined | **RESOLVED** | §8.0 rule 6: "the comparison basis is `document.getElementById(id).querySelector('.modal').innerHTML` string equality between the two entry paths. No other basis is permitted." Re-run QA-IMP-02 / QA-SMP-28 / QA-SMP-29: innerHTML string-identical across entry paths → **PASS ×3**. |
| S-11 | `WF-15…21` absent from the backlog file | **RESOLVED (open orchestrator item, non-blocking)** | `_plans/_wireframe-fixes.md` **§F** now carries `[WF-15 · proposed]` … `[WF-21 · proposed]`; §8.0 rule 7 defines the `· proposed` suffix and states "A runner cross-checking the backlog will find all seven in §F" — verified true. §F documents the bare-number collision with concurrent passes (key on full token + file) and records the factual correction that this page renders `Unstar to remove from list` — independently confirmed at `wms2/order-management/index.html:187`. No renumbering on either side. |

### M3a / M3b rows naming this page (spot-checked)

| Item | Verdict | Evidence |
|---|---|---|
| D7 hub strings | **RESOLVED (declared divergence)** | §3.10 "**Declared cross-page string divergence (cross-page defect M3a D7)**" — 5 of 6 shared strings are corpus-majority; the Saved-pane hint `Unstar to remove from list` is byte-exact to the binding wireframe (line 187) and the corpus has no majority. QA-CMT-03 re-run **PASS** byte-exact. |
| §6.7 silent N/A | **RESOLVED** | New §6.7 "Mandatory-inclusion items with no `[G-n]` anchor — explicit N/A, never silent" states items 9 (line-based location filter), 10 (audit-mode visibility), 11 (JIT residual stock) as explicit N/A; `JIT` now appears 11× in the spec. |
| D14 / D16 / D10 | **RESOLVED (declared, not renamed)** | §5 declares the `[DC-28]` name divergence; §6.3 pins the directory deep-link form; §3.8 flags the stale View-Orders cross-reference. No unilateral cross-file edits. |

**Totals: 23 defect/fix items checked → 23 RESOLVED · 0 PARTIAL · 0 NOT RESOLVED · 0 REGRESSED.**

---

## 3. QA re-run — 16 `[WF]` scenarios (Playwright), prioritising prior FAIL/AMBIGUOUS + every hardened scenario

| Scenario | Prior state | RV verdict | Evidence |
|---|---|---|---|
| QA-IMP-12 | FAIL (F-1) | **PASS** | own-text = 7 exact headers · raw7 `Carrier (auto)M1b` |
| QA-LST-12 | FAIL (F-2) | **PASS** | `<br>`-joined = 4 declared strings · raw `textContent` = 4 declared values · brand/6 menus/badge `3`/chip/Logout all present |
| QA-GBL-14 | FAIL (F-3) | **PASS** | exactly 2 `.focus()` sites (`otCustom`, `picCustomIn` toggle) · 0 autofocus · activeElement=body · 0 scan-like inputs · 0 `.select()` |
| QA-CMT-05 | FAIL (F-4) | **PASS** | `.empty`=`No matching comments` · `.it`=0 · `.paneheader`=`0 results · newest first · click to open the order` |
| QA-CMT-21 | AMBIGUOUS (A-1) | **PASS** | query `4` → 5 rows: `MKT-40233, MKT-40218, 421771, MKT-40191, 421502` |
| QA-SMP-02 | latent (S-6/5b) | **PASS** | 2 radios, first checked, trimmed labels `All new orders in this period` / `Selected orders only (2)` |
| QA-SMP-03 | latent (S-6/5b) | **PASS** | `2026-07-23` / `10:00` / `~` / `End date` / `Time` / `forever (no end date)` checked |
| QA-LST-07 | latent (S-6/5b) | **PASS** | full inventory exact: dates `2026-06-01`/`2026-07-14`, both search placeholders, selects `All Status`/`Country: AU`/`15`, `Order #` ✓ / `Tracking #` ✗, buttons `▦ Columns, ⬇ Export, ⬇ Yun Export, ⬆ Import` |
| QA-CMT-02 | latent (S-7) | **PASS** | `firstChild.textContent` = `Comments mentioning me · Click to open the order ` (trailing space, byte-exact) · geometric probe 14 px ≤ 20 / 291 px ≥ 100 |
| QA-LST-02 | latent (S-8) | **PASS** | `--mkt #7C3AED` · `--mkt-soft #F3EEFF` · hover rule read back as `rgb(235, 225, 255)`, accepted per the either-form clause |
| QA-IMP-11 | latent (S-9) | **PASS** | `previousElementSibling` is `<b>` `Preview — mkt_seeding_batch3.xlsx · 12 rows parsed · 0 errors` |
| QA-IMP-02 | latent (S-10) | **PASS** | `.modal` innerHTML string-identical across filter-bar vs wf-bar entry (4,226 chars) · sentinel held |
| QA-SMP-28 | latent (S-10) | **PASS** | innerHTML identical across entry paths (2,143 chars) |
| QA-SMP-29 | latent (S-10) | **PASS** | innerHTML identical across entry paths (1,552 chars) |
| QA-CMT-03 | control (D7 string) | **PASS** | saved pane shown, mentions hidden, hint `Unstar to remove from list` byte-exact, 1 row `Order MKT-40218` |
| QA-LST-01 | control (5c) | **PASS** | dashed placeholder text present, inline dot `4`, dot excluded per rule 5c |

**16 / 16 PASS · 0 FAIL · 0 AMBIGUOUS.** Executor self-disclosure: one first-run FAIL (QA-LST-07) was this harness's own probe defect — it queried `input[type="date"]` while the wireframe authors `<input class="date" type="text">`; repaired and re-run. The spec was correct; see note 1.

---

## 4. Regression checks

| Check | Result |
|---|---|
| Legend coverage | **intact** — §3 carries the identical 16 `[L-…]` heading keys as v1.1; §2's 9-unit / 9-dot / 10-key / 16-total accounting unchanged |
| ID renumbering | **none** — E-1…100, DC-1…29, BR-1…34 contiguous; all five QA blocks contiguous 1..n; the 18 new scenarios are block-tail appends (IMP 52→62, SMP 43→50, CMT 23→24; LST 17 and GBL 18 unchanged) |
| Global-rule body restatements | **none new — decisively clean.** 11-word shingle diff (punctuation-stripped) of the spec against `_global-rules.md`, run on both the git v1.1 baseline (`60d58ec`) and v1.2: v1.1 shared 29 shingles, v1.2 shares 23, **new-in-v1.2 = 0**, removed = exactly the 6 shingles of the `[G-7]` cluster M1 flagged. The 23 residual overlaps are the pre-existing §10 decision-log paraphrases (`_review` §3.11, classed acceptable by M1) and canonical event-name enumerations (licensed by `_review` §3.6 / C-12). |
| §8.6 matrix | DC-1…29 complete, 0 phantom scenario ids, over-claim cells repaired |
| Unasserted edges | declared, not silent: §8.0 names {E-9, E-42} with reasons; extraction confirms these are the only zero-cited ids |
| Wireframe | untouched by the remediation (spec-side fixes only); the 7 defect-documenting scenarios' targets still reproduce (`colspan="6"` at line 334 vs 7 `<th>` re-confirmed in passing) |

---

## 5. Notes (non-blocking)

1. **QA-LST-07 wording "a date input valued `2026-06-01`"** — authored as `<input class="date" type="text">`; a runner reading "date input" as `input[type="date"]` finds nothing (this harness did on first run). The element is findable by value and the scenario passes, but a five-word clarification (`input.date`, authored `type="text"`) would close the last latent selector trap of the S-6…S-9 family.
2. **WF register bare-number collision** (`WF-15`/`WF-16` claimed by concurrent remediation passes in `_wireframe-fixes.md`) is documented in §F, not resolved — resolution is an orchestrator/owner call. This spec cites only the collision-proof full tokens (`[WF-15 · proposed]` + file), so nothing here is blocked by the outcome.
3. §F's factual correction — this page renders `Unstar to remove from list`, not `…from the list` — was independently confirmed against `index.html:187` and by the byte-exact QA-CMT-03 PASS.

---

## 6. Verdict

**READY-WITH-NOTES.**

Every count the spec asserts about itself is true under independent re-derivation. The M1 MAJOR and all eight M1 MINORs, all five M2 blockers (S-1…S-5), all six M2 hardening items (S-6…S-11), and the M3a/M3b items naming this page are resolved in the current file — 23/23, with zero PARTIAL, zero NOT RESOLVED, zero REGRESSED. The re-run sample, deliberately concentrated on every scenario that previously failed, was ambiguous, or carried a latent trap, passes 16/16 with byte-exact evidence. The git-baseline shingle diff proves the remediation removed the one flagged rule-body restatement and introduced none. The two residual notes (a selector-wording nicety in QA-LST-07; the cross-file WF-number collision owned by the orchestrator) do not block implementation handoff or unaided QA execution of this spec.
