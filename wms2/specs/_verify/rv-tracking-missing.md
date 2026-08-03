# RV — Re-verification of the Remediation: `tracking-missing.md` (spec v1.2)

**Method:** independent re-verification. The auditor neither wrote the spec nor performed the remediation. Every count was re-derived by scripted extraction over the edited spec; every defect fix was checked against the current file text; QA scenarios were re-executed with a freshly written Playwright suite (`file://…/wms2/tracking-missing/index.html`, Chromium 1280×800, not the m2 script).
**Date:** 2026-08-03. **Wireframe integrity:** `wms2/tracking-missing/index.html` is unchanged since commit `8beb374` (predates all three verifications) — only the spec was edited, as required.

---

## 1. Count re-derivation (scripted, not trusted)

| Claim (spec §8.0 / remediator) | Re-derived | Match |
|---|---|---|
| 168 scenarios | 168 | ✓ |
| 66 `[WF]` / 102 `[ADMIN]` | 66 / 102 | ✓ |
| 61 negatives = 36.3 % | 61 = 36.3 % | ✓ |
| Per-block totals LOAD 12 · ROW 16 · SUS 13 · M1 13 · MATCH 10 · XDEL 12 · CMT 15 · FURN 10 · NEG 15 · VAL 12 · EMPTY 6 · XPG 9 · DATA 13 · A11Y 5 · WFQ 7 | identical, sum 168 | ✓ |
| Per-block `[WF]` 11·9·5·9·5·3·7·5·1·0·2·0·0·2·7 | identical, sum 66 | ✓ |
| Per-block neg 4·4·4·3·0·3·3·3·15·10·2·4·3·0·3 | identical, sum 61 | ✓ |
| Duplicate QA IDs: zero | zero | ✓ |
| QA-VAL-10 the only BLOCKED, inside the 168/102 | confirmed | ✓ |
| DC-1…28, BR-1…44, E-1…72, N-1…12 — no gaps, no renumbering | all four ranges continuous, max = declared max, nothing beyond | ✓ |
| §8.18 cites no non-existent QA ID | 75 distinct QA IDs cited, phantom = 0 | ✓ |
| Every `[E-n]` except `[E-4]` referenced in §8 | only E-4 uncited in scenario bodies (declared exception) | ✓ (one token nit — RV-2) |

## 2. Resolution table

### m1 defects

| ID | Sev | Verdict | Evidence (current file) |
|---|---|---|---|
| D-1 | BLOCKER | **RESOLVED** | §3.3 now carries a two-surface rendering table + dated delta: "the badge contract lands on M1's `Channel` cell only; the pool cell's route is muted running text (`--ink-3`, non-bold)… **Decided 2026-08-03**", with reversal impact stated. `[BR-15]` rewritten to the same two-surface delta. QA-SUS-02 and QA-SUS-05 are now mutually consistent (both assert `.mut` gray on the pool cell); both **PASS** in the re-run. Decision-log row present. |
| D-2 | MAJOR | **RESOLVED** | QA-NEG-03 re-tagged `[ADMIN]` with the reason in its body; counterpart QA-WFQ-07 added (re-run **PASS**: 2 rows remain, counters read `1`); §2.4.10 added incl. the `finishMatch()`-guards/`.xdel`-doesn't asymmetry; WF-NEW-D filed in §2.5 **and** appended to `_wireframe-fixes.md` §B (verified at lines 70–77 with cross-references both ways). |
| D-3 | MAJOR | **RESOLVED** | §8.18 E→QA map exists with 72 rows; scripted check: every E-1…72 except E-4 is cited by ≥1 scenario body; E-4 is the declared exception with the view-orders pointer. 16 new scenarios present (ROW-13…16, SUS-13, M1-13, XDEL-12, CMT-14/15, FURN-09/10, NEG-14/15, VAL-12, XPG-09, DATA-13). |
| D-4 | MINOR | **RESOLVED** | QA-NEG-02 now cites `[DC-10]`, `[DC-11]`, `[DC-12]`; QA-VAL-05 now cites `[DC-13]`. §8.16 rows agree. |
| D-5 | MINOR | **RESOLVED** | `[BR-19]` opens "Page-level extension of `[PD-8]`, declared as such" with a delete-path if the owner declines; `[L-1]` column 1 defines the pool item's namespace ("stored with the namespace the scan originated in") and names the `[E-33]` blind spot ("the namespace check is silent there by design"); §9.1 carries the PD-8 note. |
| D-6 | MINOR | **RESOLVED** | BR-23 reduced to the two key shapes; BR-27 framed as a page extension (memo immutability); BR-34 is a negative registry entry; BR-15 is the delta table pointer. Reading-contract item 1 reworded to "restates a global rule body **only where the page narrows or extends it**". |
| D-7 | MINOR | **PARTIAL (accepted alternative)** | No `GD-11` was raised — `_global-rules.md`/`_review.md` are outside the remediator's write scope. Instead `[BR-44]` is reclassified "Candidate global amendment, stated locally under protest", marked do-not-copy, and reading-contract item 7 inventories all three such locals. The cross-page divergence risk D-7 named remains open until the global amendment lands; the page-side statement is the best available containment. |
| D-8 | MINOR | **RESOLVED** | §9.3 renders `[PD-51 · OWNER-PENDING]`; §9.1's cross-referenced list now contains PD-51 (5 entries) and the 16+5+1=22 arithmetic is stated. |
| D-9 | MINOR | **RESOLVED** | QA-XPG-05 re-tagged `[ADMIN]` with the three-of-four-clauses reason in its body; §8.0 now states "Every `[WF]` scenario in this document runs against that one URL". No `[WF-XPG]` marker invented (correct — `_review.md` §3.4 binds tags to two values). |
| D-10 | MINOR | **RESOLVED** | §8.0 reads "Of these, **one** (QA-VAL-10) is `BLOCKED` … counted inside the 168 and inside the 102 `[ADMIN]`". |

### m2 findings (FAIL / AMBIGUOUS / UNRUNNABLE)

| ID | Was | Verdict | Evidence |
|---|---|---|---|
| F1 (QA-LOAD-04) | FAIL | **RESOLVED** | §8.0 rule 1 (strip `.dot` before every text comparison) + amended scenario text. Re-run: **PASS** — 12 headers exact after strip. |
| F2 (QA-M1-01) | FAIL | **RESOLVED** | Scenario now asserts the header's **leading text node** (§8.0 rule 5). Re-run: **PASS** — leading text node `Review & Match — Unrecognized Product`, `button.x[data-close]` = `✕`. |
| F3 (QA-NEG-03) | FAIL | **RESOLVED** | See D-2. QA-NEG-01 (the guarded sibling) re-run **PASS**; QA-WFQ-07 re-run **PASS**. |
| F4 (QA-SUS-05) | AMBIGUOUS | **RESOLVED** | Scenario now names the exact element set ("the **four** trailing `span.mut` … ×2 and ×2"), exact computed values, and warns the `.tag-*` sweep passes vacuously. Re-run: **PASS** — 4 elements, all `rgba(0,0,0,0)` / `none` / `0px` / `rgb(126,124,131)`. |
| F5 (QA-XPG-05) | UNRUNNABLE | **RESOLVED** | Re-tagged `[ADMIN]`; the Closing-side clause is delegated to the closing spec. See D-9. |
| m2 §5/§6 secondary | — | **RESOLVED** | §8.0 rules 2 (`table.tbl` ×2), 3 (nested `.mockwrap`), 4 (`.it` positional), 6 (CDP probe) all present; QA-NEG-01 quantified (one display cycle, 6 s bound — re-run PASS); QA-ROW-08 CDP fallback stated. QA-EMPTY-01's quantification is the one item that went wrong — see RV-1. |

### m3a / m3b items claimed

| Item | Verdict | Evidence |
|---|---|---|
| m3a D7 (hub pane strings) | **RESOLVED** | WF-NEW-E filed in §2.5 + `_wireframe-fixes.md` §B (lines 79–85); §3.6 string table `[WF]`/`[ADMIN]`; QA-CMT-03/05 assert wireframe strings (re-run **PASS**), QA-CMT-15 asserts canonical strings `[ADMIN]`. `[G-7]` amendment itself is out of scope, stated as pending. |
| m3a D13 (GD-n resolution) | **RESOLVED** | Reading-contract item 6. |
| m3a D14 (event-name scope) | **RESOLVED** | §5.1 scope note with the four shared-concept rows; global amendment halves recorded as pending. |
| m3a D16 (deep-link form) | **RESOLVED** | §6.2 normalized to `../{slug}/#{anchor}`; the only `index.html` strings left in the spec are the SST file path references. |
| m3b 5.3 (WF-9 vs WF-10) | **RESOLVED** | §2.5 register-citation warning present; spec cites WF-10 throughout. |
| Register appends | **VERIFIED** | `_wireframe-fixes.md` §B carries `[WF-NEW-D · tracking-missing]` and `[WF-NEW-E · tracking-missing]` with the number-collision rationale (the file's own ⚑ note confirms WF-15 was claimed three times concurrently — page-scoped IDs were the right call). |

## 3. QA re-run (28 `[WF]` scenarios, fresh Playwright suite)

Previously failed/ambiguous scenarios prioritised. **27 PASS · 1 FAIL · 0 AMBIGUOUS.**

PASS: QA-LOAD-04, QA-LOAD-05, QA-LOAD-07, QA-SUS-02, QA-SUS-05, QA-M1-01, QA-M1-09, QA-M1-10, QA-MATCH-01…05, QA-NEG-01, QA-WFQ-07, QA-XDEL-01, QA-XDEL-03, QA-EMPTY-05, QA-CMT-03, QA-CMT-05, QA-CMT-06, QA-CMT-11, QA-A11Y-05, QA-WFQ-01, QA-WFQ-02, QA-WFQ-03, QA-WFQ-04.

FAIL: **QA-EMPTY-01** — see RV-1.

Methodological note that validates §8.0's hardening: the auditor's first pass coded 4 scenarios (NEG-01, WFQ-07, XDEL-01, EMPTY-05) with an unscoped `table.tbl tbody tr` selector and got false FAILs from the modal's candidate rows — exactly the trap §8.0 rule 2 documents. Re-coding per the rule turned all four into clean PASSes. The rules are load-bearing and correct.

## 4. Regression checks

- **Legend coverage:** intact — §2.1 still declares 7+6=13 units, §8.17 maps all 13; wireframe re-verified 7 `.dot` / 6 legend `<li>`.
- **ID renumbering:** none — DC/BR/E/N ranges continuous to their declared maxima; all m2-era QA IDs still exist with the same semantics; new scenarios were appended at block ends only.
- **Global-rule restatement:** none reintroduced — BR-15/23/27/34 are delta-only; BR-44 is quarantined as a candidate amendment; reading contract items 1/6/7 are internally consistent.
- **Wireframe untouched:** `index.html` unchanged since `8beb374`; no spec fix leaked into the SST.

## 5. New findings from this pass

### RV-1 — QA-EMPTY-01's quantification anchors the wrong `.mockwrap` — deterministic false FAIL · the one remaining defect

§8.11: *"the **inner** `.mockwrap`'s bounding-box height is **> 300 px**"*. §8.0 rule 3 defines inner = the 1457 px table wrapper. That element wraps **only the pool table**, and with the tbody emptied it collapses to **42 px** (measured); the element that stays at **520 px** is the **outer** `.mockwrap`. m2's original proxy measured the outer (`mockH: 520`); the remediation transcribed the threshold onto the wrong element. As written, this `[WF]` scenario fails on the live wireframe every time — the exact false-FAIL class the spec exists to prevent. The other two clauses (12 `<th>` rendered; `#poolCountBottom` below `<thead>`) pass. **Fix: one word — "inner" → "outer" (or "the outer `.mockwrap`'s height > 300 px and the pool `<thead>` still rendered").**

### RV-2 — §8.18's E-16 row credits scenarios that do not cite the ID · MINOR (map-token nit)

The map's preamble says rows were re-derived by searching §8 for each ID, but E-16's row credits QA-XDEL-04 / QA-WFQ-03, whose bodies cite `[PD-60]`/`WF-6`, not `[E-16]`; the token appears only in block 8.6's heading. Coverage is substantively real (both scenarios assert exactly E-16's content — accidental-✕ protection and its wireframe gap), so this is the D-4 class at map-integrity level, not a hole. Fix: add `[E-16]` to either scenario body, or note the heading-level citation in the map row.

## 6. Verdict

**READY-WITH-NOTES.**

All 10 m1 defects and all 5 m2 findings are resolved (D-7 by a documented, reasonable alternative pending the out-of-scope global amendment). Counts reproduce exactly from the file; no ID was renumbered; no regression found in legend coverage, PD discipline, or rule hygiene; the register appends are in place with a sound collision rationale. Two notes stand between this and unqualified READY: **RV-1** (a one-word fix to QA-EMPTY-01, without which one `[WF]` scenario false-FAILs deterministically) and **RV-2** (a map-token cosmetic). Neither blocks implementation; RV-1 should be fixed before the QA suite is run unattended.
