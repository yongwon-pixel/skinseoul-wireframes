# RV — Independent re-verification of the `closing.md` remediation

Re-verifier role: independent — did not author the spec, the m1/m2/m3 findings, or the remediation. Date: 2026-08-03.
Spec under test: `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md` (v1.2, 2,388 lines; HEAD baseline v1.1 = 2,219 lines, diff +303/−67 confined to the spec — `wms2/closing/index.html` has **zero diff** against HEAD, confirming no wireframe edits were smuggled in).
Every count below was re-derived by my own extraction scripts; every QA verdict comes from my own Playwright runner (`scratchpad/rv2_qa_closing.py`), written from the current spec text only.

---

## 1. Counts — re-derived vs claimed

| Claim (spec v1.2 / remediator) | My extraction | Verdict |
|---|---|---|
| 177 QA scenarios | 177 `**QA-` headers | **TRUE** |
| 68 `[WF]` / 109 `[ADMIN]` | 68 / 109, 0 double-tagged, 0 untagged | **TRUE** |
| 71 negative (40.1%) | 71 → 40.11% | **TRUE** |
| 0 duplicate IDs, 0 numbering gaps | 177 unique IDs; every block continuous 1..max | **TRUE** |
| §8.16 per-block rows sum to totals | all 15 rows match my per-block (WF, ADMIN, Total, Neg) tallies exactly; columns sum 68/109/177/71 | **TRUE** |
| E-1…E-78 continuous, all mapped | 78 ids, no holes; §7 defines all 78 as table rows; §8.18 two-column table maps all 78 | **TRUE** |
| BR-1…BR-38 continuous | 38 ids, no holes (BR-38 new) | **TRUE** |
| DC-1…DC-25, each with ≥1 asserting scenario | 25 ids; every §8.17 row names ≥1 QA id | **TRUE** |
| §8.18 cells name scenario IDs only | 0 `§`/`DQ-` pointers inside mapping cells (both appear once, in the preamble prose stating the rule) | **TRUE** |
| All cited QA ids exist | 0 ghost citations (every `QA-*-n` in the file resolves to a defined header) | **TRUE** |
| 22 legend units + 4 furniture keys | 22 `### 3.x [L-…]` anchors; DOM re-count 19 `.legend ol > li` + 2 modal dots + 1 `#s1 .legend > p` = 22 (QA-CHROME-04 re-run) | **TRUE** |
| 17 distinct `· OWNER-PENDING` PDs, PD-71/74 never tagged | 17 distinct {1–8, 68–70, 72, 73, 75–78}; 71 and 74 absent, §9.2-only | **TRUE** |

---

## 2. Resolution table

### m1-closing.md (MAJOR + minors)

| Defect | Status | Evidence (quoted from v1.2) |
|---|---|---|
| **M1-1 MAJOR** — §8.18 claim false for E-37/52/60/66/74/77 (+ E-51 partial) | **RESOLVED** | 7 new `[ADMIN]` scenarios exist with on-point assertions: QA-CONFIRM-16 (l.1896) "When the client retries with the **same idempotency key** / Then exactly **one** … (**DC-21**) … (**DC-23**) … (**DC-24**)"; QA-VERDICT-15 (l.1380) "`Items` cell renders exactly `0`"; QA-COUNT-13 (l.1593) "**400** scan rows … the append never steals focus"; QA-VERDICT-16 (l.1386) "`MKT-` prefix … no prefix-based exclusion"; QA-HIST-11 (l.1960) "opens in a **new browsing context** and the closing tab is **not** navigated"; QA-SCAN-17 (l.1299) "submit is **deferred to `compositionend`** … no partial string"; QA-TARGET-14 (l.1673) covers E-51's "processed normally" clause. §8.18 rows remapped to them; all 78 E-ids covered; block totals/grand total/negative share updated consistently (verified column-wise). |
| M1-2 minor — §8.0 traceability pointers off by one | **RESOLVED** | §8.0: "§8.17 proves every event in §5.1 … and §8.18 does the same for every `[E-n]`." |
| M1-3 minor — U-a under-scopes the `79` | **RESOLVED** | §2.3 U-a: "**The same `79` also appears in the Confirm Closing button label** (`index.html:397`) … demo data, not a worked example"; §3.9 (l.429): "> **Not a worked example.** That `79` is the same bad demo datum … formula in §3.5 gives `remaining = 81`". |
| M1-4 minor — malformed `[L-S4-1..3]` | **RESOLVED** (note) | §8.11 heading and §8.16 row now enumerate `[L-S4-1]` `[L-S4-2]` `[L-S4-3]`. Sole surviving occurrence is the §11 changelog row (l.2385) quoting the old form in backticks *as the thing that was fixed* — historical reference, but a naive mechanical key-checker will still flag it. |
| M1-5 minor — PD citations in §8 lack `· OWNER-PENDING` | **RESOLVED** | Fixed via the audit's option 2: new **R10** — "A `[PD-n]` in a QA heading points at the behavior's defining sentence in §3 or §7, which carries the full `[PD-n · OWNER-PENDING]` tag … `[PD-71]` and `[PD-74]` are NO-DEFAULT (§9.2) and are never asserted". |
| M1-6 minor — §1.3 restates [G-1] body | **RESOLVED** | §1.3 now: "Hence the three [G-1] invariants, which this page inherits unchanged (deltas in §3.2)." (The pre-existing "page-local expression of [G-1]" at l.514 is unchanged from v1.1 and was not flagged by m1 — not a regression.) |
| M1-7 minor — §8.16 vs §8.18 key-list disagreement (E-35 / E-74) | **RESOLVED** | §8.16 QA-PERSIST row: "E-30…34/36/38/41/53/59/62/71" (E-35 excluded, with the rationale spelled out below the table); QA-HIST row now carries E-74. |

### m2-closing.md (3 FAILs + ambiguous clauses F2–F9)

| Item | Status | Evidence |
|---|---|---|
| **F1 / QA-DEL-01 FAIL** | **RESOLVED** | Now: "its `header` R2-normalized text **starts with** "Delete Scan Row" (the header's `✕` close button is nested inside it — R2b; same shape as QA-M1-02)". Re-run: **PASS**. |
| **F1 / QA-HUB-01 FAIL ×2** | **RESOLVED** | Both clauses now `starts with` with R2b callouts ("💬 Comments" / "Comments where I'm tagged"); v1.2 adds the honest tiering clause "these two pane strings are stale demo copy `[WF-15]`; the canonical `[G-7]` strings are asserted in QA-HUB-09". Re-run: **PASS**. |
| **F1 / QA-HUB-02 FAIL** | **RESOLVED** | "`.paneheader` R2-normalized text **starts with** "Comments I saved"". Re-run: **PASS**. |
| F2 — assertion verbs unbound | **RESOLVED** | New **R6b** fixes `reads`/`reads exactly`/`is exactly` = strict equality, `starts with`, `contains`, `yields N`, plus "Never relax `reads` to *contains*". |
| F3 — nested controls beyond `.dot` | **RESOLVED** | New **R2b** table lists all four polluters incl. the latent `span.user`/`.avatar` ("YYongwon Ryu") and sanctions an extended strip-helper. |
| F4 — QA-CHROME-04 "23" unverifiable | **RESOLVED** | Scenario now gives the three DOM counts (19+2+1=22), asserts `.wf-tab` = 10 and `[data-modal]` = 3, and derives 23 only as the named trap. Re-run: **PASS** (all counts as stated). |
| F5 — state activation undefined | **RESOLVED** | New **R9**: "to activate a state, click its `.wf-tab[data-state="sX"]`; to open a modal … `.wf-tab[data-modal="m-…"]`". |
| F6 — `p.sub` not unique | **RESOLVED** | QA-CHROME-02: "the **first** `p.sub` — address it as `#sX .pagepad > p.sub:first-of-type`". Re-run: **PASS** across all 7 states. |
| F7 — S0-01 "card heading" selector-less | **RESOLVED** | Exact filter expression given, with match-count-of-1 requirement. Re-run: **PASS**. |
| F8 — HIST-03 "green highlight" unassertable | **RESOLVED** | "inline `style` attribute is exactly `background:var(--green-soft)`, and its computed `background-color` differs from every other data row's". Re-run: **PASS**. |
| F9 — §8.18 non-scenario pointers | **RESOLVED** | Absorbed by M1-1; mapping cells are scenario-only (verified mechanically). |

### m3a / m3b (spot-checked against remediator claims)

| Item | Status | Evidence |
|---|---|---|
| D2 — closing bypasses the inbound-completeness outbound gate | **RESOLVED** | New **BR-38** (l.798) "every line is `INBOUNDED`… in addition to the Zero Packing attestation"; §3.21 predicate list (l.675 `AND not order.cancelled` block); E-78 row (l.1037); QA-M1-14 asserts the disabled button + reason string + no DC-13/14/11. |
| D3 — `Cancelled` treated as a status | **RESOLVED** | §3.6 (l.318): "**`Cancelled` is not an order status.** The vocabulary is exactly the 8 WooCommerce statuses … a separate flag"; verdict matrix renders underlying status + `Cancelled` marker; QA-VERDICT-07 asserts "never the literal `cancelled`" in DC-7; the PD-76 register-title mismatch is explicitly flagged for the owner rather than silently patched. |
| D7 — hub copy divergence | **RESOLVED (closing side)** | §3.8 (l.399–401) canonical `[G-7]` strings vs wireframe strings in a two-column table; QA-HUB-01/02 tier the wireframe strings `[WF]`, QA-HUB-09 asserts the canonical `[ADMIN]` strings. Corpus-wide string unification remains open in `_wireframe-fixes.md` (correctly marked "conditional and corpus-wide — do not edit this page alone"). |
| D11 — `[G-3a]`/PD-2 scope | **NOT RESOLVED — out of file scope (accepted)** | Requires amending `_global-rules.md`/PD register. closing.md already carries the by-class application + owner tension + reversal impact (§3.21 step 5, l.688; §6.6 table l.958). Nothing further is fixable from this file. |
| D13 (`[GD-n]` declared), D16 (deep link `../order-detail/#{order_id}`), D19 (status value↔label register note l.372), D20 (`[G-3a]` citation form l.134) | **RESOLVED** | Each verified present at the quoted location. |
| M3b §2.2 — silent-N/A rows | **RESOLVED** | §9.1 carries the 3 new rows (location filter `[G-14]`, audit-mode-only visibility, JIT residual stock) plus the closing sentence naming M3b §2.2 as the reason. |
| `[WF-15]` registration | **RESOLVED** | Present in `_wireframe-fixes.md` §D (l.140, closing entry) and in closing.md §2.3 (l.106). |

---

## 3. QA re-run (Playwright, chromium headless 1440×900)

Runner: `/private/tmp/claude-501/-Users-yongwon-yongwon-sync/635405b8-dea2-4665-89c5-efd98bf60282/scratchpad/rv2_qa_closing.py` · Results JSON: `rv2_qa_results.json` (same dir).
Target: `file:///Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/closing/index.html`.
18 `[WF]` scenarios, prioritising every prior FAIL and every prior ambiguous clause. R2/R2b/R4/R5/R6b/R9 implemented as written in v1.2 §8.0.

| Scenario | Prior (m2) | RV verdict |
|---|---|---|
| QA-DEL-01 | **FAIL** | **PASS** (header `starts with` holds; `#scandelInfo` byte-exact) |
| QA-HUB-01 | **FAIL** (2 clauses) | **PASS** (both `starts with` clauses hold; badge, 3 labels, unread flags hold) |
| QA-HUB-02 | **FAIL** | **PASS** |
| QA-CHROME-04 | PASS ⚠ (unassertable clause) | **PASS** — every count assertable as written (2 dup tabs, 19+2+1=22, `.wf-tab`=10, `[data-modal]`=3) |
| QA-CHROME-02 | PASS ⚠ | **PASS** — `p.sub:first-of-type` unique in all 7 states |
| QA-S0-01 | PASS ⚠ | **PASS** — heading filter matches exactly 1 element |
| QA-HIST-03 | PASS ⚠ | **PASS** — inline style token byte-exact; computed bg differs from all 4 other rows |
| QA-S0-02 / QA-S0-03 / QA-SCAN-01 / QA-VERDICT-01 / QA-VERDICT-02 / QA-COUNT-01 / QA-CONFIRM-01 / QA-M1-02 / QA-HUB-03 / QA-VOICE-01 / QA-TARGET-04 | PASS | **PASS** (regression sample — all held, incl. byte-exact strings, `en-US` utterances ×3 states, star toggle, cancel-to-s0) |

**18 / 18 PASS · 0 FAIL · 0 AMBIGUOUS · 0 UNRUNNABLE.** No scenario required improvisation beyond the spec text; the two runner defects encountered during development (wrong column index, header row picked from the thead-less `logtbl`) were my own selector errors, corrected against the page, not spec gaps.

---

## 4. Regression check

- **Legend coverage:** intact — 22 anchors in §3, 22 DOM units re-counted, §8.16 unit table lists all 22 + `[L-F1]`…`[L-F4]`, and the new scenarios were added to the unit rows (e.g. `[L-S1-6]` now lists QA-HIST-11).
- **No ID renumbering:** E-37/52/60/66/74/77/78 conditions in §7 match the m1-quoted conditions verbatim in meaning; E/BR/DC ranges continuous; QA blocks extend at the tail only (…-15/-16/-17 style), no reuse of existing numbers.
- **No new global-rule restatements:** §1.3 fixed; remaining [G-1] mentions are citation-plus-delta form; l.514 phrasing pre-exists in v1.1 (verified via `git show HEAD`).
- **Wireframe untouched:** `git diff` for `wms2/closing/index.html` is empty — the M2 FAILs were fixed in the spec, exactly as attributed.
- **Notes (non-blocking):** (1) changelog l.2385 quotes the retired `[L-S4-1..3]` composite in backticks — historical reference; a naive key-existence checker must whitelist §11. (2) QA-HUB-01/02 now assert wireframe strings that are simultaneously declared stale (`[WF-15]`) — intentional two-tier design, but when the corpus-wide `[G-7]` string unification lands, these two `[WF]` scenarios and the wireframe must change in the same pass.

---

## 5. Final readiness verdict

**READY-WITH-NOTES.**

The single MAJOR (false §8.18 traceability claim) and all three M2 FAILs are genuinely fixed and empirically re-verified; every count the spec asserts about itself reproduces exactly; the QA corpus is now runnable clean (18/18 on the adversarially-chosen sample, including every previously failing or ambiguous scenario) with the verb/normalization/activation rules (R2b/R6b/R9/R10) closing the silent-divergence hazards m2 identified. The notes: (a) D11 (PD-2/[G-3a] scope) and the `[G-7]` canonical-string unification are **cross-file** work that this spec correctly stages but cannot complete — they must land in `_global-rules.md`/`_provisional-decisions.md` and a corpus-wide pass respectively; (b) the two cosmetic items in §4 above. Nothing in this file blocks handing `closing.md` v1.2 to developers or to a QA agent.
