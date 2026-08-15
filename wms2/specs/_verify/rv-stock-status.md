# RV — Independent Re-verification · `stock-status.md`

**Target:** `wms2/specs/stock-status.md` (1410 lines, v1.1 · 2026-08-03, post-remediation)
**SUT:** `file:///…/wms2/stock-status/index.html` (662 lines — unchanged since commit `d09fe79`; remediation touched the spec + `_wireframe-fixes.md` §H only, wireframe fixes remain *proposed*)
**Method:** all counts re-derived by own script (`rv_ss_counts.py`, not the remediator's); prior-version diff against git `60d58ec`; 17 `[WF]` scenarios re-run with an independently written Playwright harness (`rv_ss_qa.py` / `rv_ss_qa2.py` — `qa-stock-status.py` was not reused). Verifier wrote neither the spec nor the fixes.

---

## 1. Count re-derivation (question 1)

Every stated number was recomputed from the file. **All match.**

| Claim in spec | Independently derived | Verdict |
|---|---|---|
| 200 scenarios = 75 [WF] · 125 [ADMIN] | 200 rows, 75/125 | MATCH |
| 85 negative/boundary = 42.5 % | 85 rows tagged NEGATIVE/BOUNDARY = 42.5 % | MATCH |
| Per block NAV 12 · CS 18 · LOC 18 · AUD 44 · LOG 9 · RES 26 · HIS 18 · FRM 20 · COM 15 · EXP 6 · GLB 14 | identical, block by block | MATCH |
| 36 BR · 34 DC · 13 NE · 98 E | BR 1–36, DC 1–34, NE 1–13, E 1–98 — all contiguous, no gaps, no dupes | MATCH |
| 21 units = 16 legend + 5 furniture | §3 has exactly 21 sections (3.1–3.21); `[L-F1]`–`[L-F5]` all present; DOM census 16 `span.dot` / 12 legend `li` / 6 `.overlay` / 4 `.pane` unchanged | MATCH |
| All 34 `[DC-n]` keyed in ≥1 QA scenario | 0 unkeyed | MATCH |
| 0 dangling QA refs | 0 (in §8.1 and document-wide) | MATCH |
| No blank line splits a QA table; tables column-consistent | 0 blank-line splits; 0 pipe-count-inconsistent tables | MATCH |

Notes (not count mismatches): the only `[L-F8]` occurrence is a §10 citation of the sibling `ready-to-outbound` spec, not a page key. `[E-59]` is carried in §7 and cited in the §8.0 demo-limitations paragraph but by no scenario row — identical in the pre-remediation version (M1 accepted it), so **pre-existing, not a regression**.

---

## 2. Resolution table (question 2)

### M1 defects (0 BLOCKER · 2 MAJOR · 7 MINOR)

| Defect | Verdict | Evidence (current file) |
|---|---|---|
| **D1 MAJOR** — global nav specified nowhere | **RESOLVED** | §3.21 `[L-F5] Global nav and signed-in identity` exists (line 578); §2.1 footnote map keys it (line 70); §2.2 row (line 107); §5.3 `[NE-13]` (line 723); `QA-NAV-11` [WF] + `QA-NAV-12` [ADMIN]; unit total raised to 21. §3.21 covers nav census, actor-of-record (`[G-8]`/`[G-15]`/`[PD-1]`), NON-event clicks, and Logout-during-audit (`[E-57]`). **QA-NAV-11 re-run: PASS** (brand/6 categories/4 navlinks/badge 3/avatar Y/Yongwon Ryu/Logout all verified in DOM) |
| **D2 MAJOR** — `BR-35` widens PD-47 untagged | **RESOLVED** (in-page scope) | `BR-35` (line 642) now carries `[PD-47 · OWNER-PENDING]` + *"this **extends** the register's wording and the owner must be asked for the extension"*, with a mechanical reversal list; same tag+flag on `[E-81]` (850), §3.11 bullet (342), `QA-AUD-40` (1090, incl. "if the owner declines the extension the expected value becomes `9`"), and the §9.2 PD-47 index entry (1306) now lists `[BR-35]`. The register file itself is binding-unchanged (fix option (a)'s register amendment / option (b)'s `PD-87` were out of the task's write scope — declared in-spec at every point of use, which satisfies the reversal contract) |
| D3 MINOR — silent BR renumbering | **RESOLVED** | §4 header note (declared once, 2026-08-03) with the full A-plan mapping `A-2→3 · A-7→13 · A-8→16 · A-9→10 · A-10→20 · A-12→9 · A-13→25 · A-16→19; A-11/14/15 absorbed` + "Do not renumber again" |
| D4 MINOR — `[E-11]` unreferenced | **RESOLVED** | `QA-AUD-07` (line 1057) now ends `` `[E-11]` `[PD-47 · OWNER-PENDING]` `` |
| D5 MINOR — `[E-69]`/`[E-70]` unreferenced | **RESOLVED** | New `QA-GLB-13` [WF] (`[E-70]`, 900×800 body-scroll assertion — **re-run: PASS**) + `QA-GLB-14` [ADMIN] (`[E-69]` `[E-70]`); §9.2 layout row updated (line 1326) |
| D6 MINOR — four/five/sixth option contradiction | **RESOLVED** | §3.1 item 3 (line 165) rewritten: wireframe carries **five `<option>` elements**, production adds `OTHER` as sixth, plus an explicit counting convention ("always counts `<option>` elements, including the `All …` placeholder — QA-CS-05 asserts five, QA-CS-06 asserts six") |
| D7 MINOR — unread-badge zero state contradiction | **RESOLVED** | `QA-COM-06` (1198): "removed or hidden — **never rendered as `0`** `[E-93]`" + cross-note naming QA-COM-13; the two scenarios now agree |
| D8 MINOR — 5 BR rows restate G-bodies | **RESOLVED** | Version diff confirms exactly BR-5/6/9/26/28 rewritten, all now "Page delta on `[G-n]`" citation form; no other BR row changed; no new restatement introduced elsewhere |
| D9 MINOR — 3 §8.1 rows cite unkeyed scenarios | **RESOLVED** | `QA-RES-10` carries `[DC-5]` (1123), `QA-AUD-38` carries `[DC-9]` (1088), `QA-LOC-15` carries `[DC-15]` (1042); §8.1 rows now consistent |

### M2 FAIL / AMBIGUOUS / fix items (4 FAIL · 3 AMBIGUOUS · 0 UNRUNNABLE · 13 fixes)

| Item | Verdict | Evidence |
|---|---|---|
| FAIL QA-RES-02 (`innerText` flex/✕) | **RESOLVED** | §8.0 step 3b `norm()` added (NBSP→space · whitespace collapse · trailing `✕` strip · trim — raw bytes verified: first replace is `/\xA0/g`); scenario restates the raw value. **Re-run: PASS** (normalised header strictly equals spec string) |
| FAIL QA-RES-05 | **RESOLVED** | Same step 3b; raw value quoted in-row. **Re-run: PASS** (header + 4 steps + radios + qty 3 + hint + memo placeholder all byte-exact) |
| FAIL QA-LOC-08 (`.bcin` count false) | **RESOLVED** | Rewritten to `#p-current tbody tr:not(.audrow) .bcin === 1` + do-not-assert-unscoped warning; §3.8 selector warning (289) + §3.9 note (297) + §9.2 selectors row record the class collision. **Re-run: PASS** (scoped 1; unscoped 2 exactly as documented) |
| FAIL QA-COM-05 ("exactly" over-tight) | **RESOLVED** | Scoped to the `.empty` node + separate `.paneheader` assertion (1197). **Re-run: PASS** (`No matching comments` + `0 results · newest first · click to open the order`; tabs restored on clear). *First harness attempt flagged FAIL — traced to this verifier's own selector grabbing the Mentions pane's header; corrected harness passes* |
| AMBIG QA-LOG-09 (colour words) | **RESOLVED** | §8.0 colour-token table (6 tokens with hex + rgb). **Re-run: PASS** — computed colours exactly `rgb(180,83,9)` / `rgb(220,53,69)` / `rgb(25,135,84)`; `· target met` suffix confirmed |
| AMBIG QA-GLB-08 (clause 3 unrunnable) | **PARTIAL** | Clause 3 now names the input, the gesture, and the observable — but its literal assert (*"assert `document.activeElement` is **not** that input and **not** any other `.bcin`"*) is **false on the shipped file**: with no keydown handler, Enter leaves focus on the input (empirically: activeElement === the `.bcin` after Enter; same for `#auSearch`). The row's own closing sentence (*"a plain input merely retaining focus is not a scan loop and is not what this test forbids"*) contradicts the assert. Definition-based probe passes (after forced blur, focus stays on `BODY` — no programmatic refocus), so **no product defect**, but a literal tester still files a false FAIL. **Re-run verdict: AMBIGUOUS** (clauses 1–2 PASS) |
| AMBIG QA-GLB-09 (KR partition invented) | **RESOLVED** | §8.0 enumerates the 17-string allow-list (11 KR product names + 5 catalogue names + `신규`). **Re-run: PASS** — every Hangul run in `.mock` + all 6 overlays is allow-listed; 0 Hangul in `th/label/button/h2/h4/.paneheader/.form-note` |
| Fix 4 (reads vs reads exactly + visibility) | **RESOLVED** | §8.0 binding convention table: strict equality vs containment, `offsetParent !== null` visibility, visible-count default |
| Fix 5 (AUD-23 "3 new additions" contradiction) | **RESOLVED** | Charged to the **wireframe**: `_wireframe-fixes.md` §H `[INV-WFX-1 · proposed]` (page-scoped token — §F collision warning honoured; bare WF-15/16 verified claimed by other pages in §H's own preamble); `QA-AUD-23` retagged **STALE-FIXTURE CENSUS** (**re-run: PASS** — shipped string still says "3"); new `QA-AUD-44` [ADMIN] asserts the templatised `{n}` contract; §3.13 callout (388) |
| Fix 9 (NAV-07 scope) | **RESOLVED** — **re-run: PASS** (scoped to `.subtabs button` + `.wf-tab`, 0 matches for `/^Audit Log/`) |
| Fix 10 (LOC-18 "types" into prefilled) | **RESOLVED** — "clears the field … sets its value to" wording; **re-run: PASS** (`A-02-13` → cleared → `A-02-14`, no navigation) |
| Fix 11 (AUD-22 `18 → 17` vs separate columns) | **RESOLVED** — cell-by-cell wording, `System`/`Counted` as separate columns, normalised header. **Re-run: PASS** (3 rows, one `[NEW]`, footer button `Confirm — record 3 ADJUST events`) |
| Fix 12 (GLB-11 bare `₩` in header) | **RESOLVED** — money value defined as `₩` immediately followed by a digit, header excluded. **Re-run: PASS** (10-value census byte-exact, no `$`/`USD`) |
| Fix 13 (blank line in AUD table) | **RESOLVED** — 0 blank-line splits in any QA table (script-verified) |

### M3a / M3b rows naming this page (spot-checked)

| Item | Verdict | Evidence |
|---|---|---|
| M3a D9 — retired `Request Inbound` | **RESOLVED** | §3.18 stale-copy callout (524) + `[INV-WFX-2 · proposed]` in `_wireframe-fixes.md` §H; `QA-FRM-03` retagged STALE-COPY CENSUS (**re-run: PASS** — shipped note matches byte-exact) + new `QA-FRM-20` [ADMIN] with corrected copy + `Request Inbound`-nowhere negative |
| M3a D1 — Cancel-Inbound three-way contract | **RESOLVED** | §3.16 "Cross-page contract conflict — declared, not resolved here" table (Inventory vs View Orders `[L-M1]` vs Order Detail `[L-2]`); Inventory keeps its remainder-booking contract, reconciliation owed by the other two |
| M3a D7 / D12 / D13 | **RESOLVED** | §3.12 comment-search capture disagreement + six hub strings declared (Decision Log 1401); §3.18 glyph contract (534) fixes `＋` U+FF0B / `－` U+FF0D vs `[G-3]`'s `−` U+2212; `GD-7` citation names `_plans/_review.md` §4 as source (BR-1) |
| M3a D14 — event names | **RESOLVED** | Version diff: exactly **20** DC names normalised dotted→`entity.action` (DC-1,2,4,6,7,8,9,10,16,17,18,20,24,25,27,30,31,32,33,34), **0 IDs changed**; `comment.search_executed` now matches View Orders; §5 normalisation note (653) declares it |
| M3a D20 — `[G-3a]` vs `[G-3](a)` | **NOT FIXED (declared, accepted)** | Corpus-wide normalisation + `_review.md` convention amendment out of single-page scope; the page's `(a)/(b)/(c)` form matches `_global-rules.md`'s own sub-rule labelling |
| M3b consequence 6 — real unit count | **RESOLVED** | 21 stated and derived (16+5) |
| `_wireframe-fixes.md` §H | **VERIFIED** | Both `INV-WFX` entries present, append-only, deploy-gated; the `Unstar to remove from this list` factual correction checked against the HTML — the string occurs exactly once, with `this`, as §H claims |

---

## 3. QA re-run results (question 3)

17 `[WF]` scenarios executed against the local file with a fresh Playwright harness, §8.0 preflight + `norm()` applied verbatim, reload between scenarios. Prioritised: all 4 previous FAILs, all 3 previous AMBIGUOUS, the highest-risk tie-break rewrites, and the 4 new/retagged `[WF]` rows.

| Scenario | Prior (M2) | Now | Note |
|---|---|---|---|
| QA-RES-02 | FAIL | **PASS** | normalised header strict-equals spec |
| QA-RES-05 | FAIL | **PASS** | all legs byte-exact |
| QA-LOC-08 | FAIL | **PASS** | scoped count 1 (unscoped 2, as documented) |
| QA-COM-05 | FAIL | **PASS** | `.empty` + `0 results` header exact |
| QA-LOG-09 | AMBIGUOUS | **PASS** | rgb triples exact per token table |
| QA-GLB-09 | AMBIGUOUS | **PASS** | 17-string allow-list holds; 0 chrome Hangul |
| QA-GLB-08 | AMBIGUOUS | **AMBIGUOUS** | clauses 1–2 PASS; clause 3 assert contradicts its own definition on the shipped file (see §2) |
| QA-NAV-07 | PASS (tie-break) | **PASS** | now deterministic |
| QA-LOC-18 | PASS (tie-break) | **PASS** | now deterministic |
| QA-AUD-22 | PASS (tie-break) | **PASS** | cell-by-cell, strict header |
| QA-AUD-23 | PASS (contradiction) | **PASS** | as declared stale-fixture census |
| QA-GLB-11 | PASS (tie-break) | **PASS** | ₩+digit definition; census exact |
| QA-LOG-03 | PASS (tie-break) | **PASS** | strict equality under norm() |
| QA-LOG-04 | PASS (tie-break) | **PASS** | strict equality under norm() |
| QA-NAV-11 | — (new) | **PASS** | full nav census |
| QA-GLB-13 | — (new) | **PASS** | body never h-scrolls @900px; `.mockwrap` overflow-x:auto scrolls; 11 visible th incl. Available |
| QA-FRM-03 | PASS (retagged) | **PASS** | stale note byte-exact |

**16 PASS · 0 FAIL · 1 AMBIGUOUS.** Every previously failing scenario passes; the only residue is the QA-GLB-08 clause-3 self-contradiction.

---

## 4. Regression checks (question 4)

- **Legend coverage:** intact — 16 `span.dot` (`16,10,5,6,14,8,9,7,15,12,11,13,M2,M3,M4,M1`), 12 legend `li`, 6 overlays, 4 panes; wireframe file untouched by remediation (git-verified); all 21 units have §3 sections.
- **No ID renumbering:** version diff vs `60d58ec` — QA: 0 removed, 6 added (`NAV-11/12`, `AUD-44`, `FRM-20`, `GLB-13/14` = 194→200); BR: same 36 IDs, only the 5 de-restated rows changed; DC: same 34 IDs (names normalised only); NE 1–12 untouched + NE-13 appended; E 1–98 descriptions unchanged.
- **No new global-rule restatements:** the 5 D8 rows now cite-and-delta; §3.21 and the §3.18 glyph contract cite `[G-8]`/`[G-15]`/`[G-3]` without reproducing rule bodies (the `[G-3]` quotation is a declared glyph-disambiguation, not a behavior restatement).
- **Binding files:** `_provisional-decisions.md`, `_global-rules.md`, `_review.md` unmodified by this remediation; `_wireframe-fixes.md` changed by append-only §H as claimed.

---

## 5. Residual findings

1. **MINOR — QA-GLB-08 clause 3 is internally contradictory** (M2 fix item 7 only PARTIAL). The literal assert fails on the shipped wireframe (Enter leaves focus on the input — no handler exists), while the same row's definition sentence says focus *retention* is not forbidden. Suggested one-line fix: replace the assert with the definition's own observable, e.g. *"blur the input programmatically; assert focus does not return to any barcode-class input within 500 ms without a user gesture"* (this passes on the shipped file: after blur, `activeElement` stays `BODY`).
2. **NOTE — `[E-59]`** is cited by the §8.0 demo-limitations paragraph but keyed in no scenario row. Pre-existing in the M1-audited version and not counted as a hole there; recorded for completeness only.

---

## 6. Verdict

**READY-WITH-NOTES.**

Both MAJORs and all seven MINORs from M1 are resolved with in-file evidence; all four M2 FAILs were spec-side and now pass under the codified §8.0 rules; two of three AMBIGUOUS rows are fully deterministic. Counts are true to the file, nothing regressed, and the two stale-wireframe facts are correctly quarantined as census assertions with proposed fixes in the backlog. The single residue (QA-GLB-08 clause 3) affects one clause of one scenario, has a known one-line fix, and cannot produce a wrong product decision — only a false test FAIL by an overly literal runner.
