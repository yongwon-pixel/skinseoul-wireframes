# RV — Independent re-verification of the `closing.md` remediation

Re-verifier role: independent — did not author the spec, the m1/m2/m3 findings, or the remediation. Date: 2026-08-03 (second pass; a prior rv-closing.md existed in this directory and was **not trusted** — every count, quote and QA verdict below was re-derived from scratch with fresh extraction scripts and a fresh Playwright runner. The prior file's conclusions were independently reproduced, which corroborates them, but the evidence here is my own).

- Spec under test: `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md` (v1.2, 2,388 lines)
- Wireframe: `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/closing/index.html` (909 lines)
- My runner: `scratchpad/rv3_qa_closing.py` · results: `scratchpad/rv3_qa_results.json` (Playwright · headless chromium · 1440×900 · R1/R2/R2b/R3/R4/R5/R6b/R9 implemented from v1.2 §8.0 as written)

---

## 1. Counts — re-derived vs claimed

| Claim (spec v1.2 / remediator) | My extraction | Verdict |
|---|---|---|
| 177 QA scenarios | 177 `**QA-` header lines | **TRUE** |
| 68 `[WF]` / 109 `[ADMIN]`, 0 untagged | 68 / 109 / 0 | **TRUE** |
| 71 negative (40.1%) | 71 → 40.11% | **TRUE** |
| 0 duplicate IDs, 0 numbering gaps | 177 unique; all 15 blocks continuous 1..max (S0 11, SCAN 17, VERDICT 16, UNKNOWN 7, DUP 10, VOICE 9, COUNT 13, TARGET 14, M1 14, DEL 10, CONFIRM 16, HIST 11, HUB 9, PERSIST 14, CHROME 6) | **TRUE** |
| §8.16 per-block rows sum to totals | all 15 rows match my per-block (WF, ADMIN, Total, Negative) tallies cell-for-cell; columns sum 68/109/177/71 | **TRUE** |
| E-1…E-78 continuous, all mapped in §8.18 | 78 ids, no holes; §8.18's two-column table maps all 78; every mapping cell names only scenario IDs (0 `§`/`DQ-` pointers inside cells), every cited ID resolves to a defined header | **TRUE** |
| BR-1…BR-38 continuous | 38 ids, no holes (BR-38 new, l.798) | **TRUE** |
| DC-1…DC-25, each with ≥1 asserting scenario | 25 §8.17 rows, every row cites ≥1 existing scenario (shorthand `QA-SCAN-03, 05, …` expands to existing IDs) | **TRUE** |
| 22 legend units + 4 furniture keys | §2.1 declares 22 = 19 `.legend ol > li` + 2 modal dots + 1 `#s1 .legend > p`; my DOM re-count in the QA-CHROME-04 run returns exactly 19/2/1 | **TRUE** |
| 17 distinct `· OWNER-PENDING` tags; PD-71/74 never tagged | 17 distinct {1–8, 68–70, 72, 73, 75–78}; PD-71/PD-74 carry the tag 0 times and live only in §9.2 | **TRUE** |

**Counts verdict: every count the remediator and the spec assert about the file reproduces exactly.**

---

## 2. Resolution table

### m1-closing.md (1 MAJOR, 0 BLOCKER; minors included for completeness)

| Defect | Status | Evidence (current file) |
|---|---|---|
| **M1-1 MAJOR** — §8.18 claim "every `[E-n]` has an asserting scenario" false for E-37/52/60/66/74/77 + E-51 partial | **RESOLVED** | Seven new `[ADMIN]` scenarios exist with on-point assertions: QA-CONFIRM-16 (l.1896) "When the client retries with the **same idempotency key** · Then exactly **one** `closing.confirmed` (**DC-21**), exactly **one** … (**DC-23**) and exactly **one** … (**DC-24**)"; QA-VERDICT-15 (l.1380) "`Items` cell renders exactly `0` (not `–`, not blank)"; QA-COUNT-13 (l.1593) "**400** scan rows … the append never steals focus … if paginated, the **latest** page"; QA-VERDICT-16 (l.1386) "`MKT-` prefix … no prefix-based exclusion"; QA-HIST-11 (l.1960) "opens in a **new browsing context** and the closing tab is **not** navigated"; QA-SCAN-17 (l.1299) "submit is **deferred to `compositionend`** … no partial string … no **DC-7** for any partial prefix"; QA-TARGET-14 (l.1673) "scan … processed normally … counters recompute against the **saved** target `84`" (E-51's missing clauses). §8.18 remaps those rows to the new IDs and its preamble names each repair; block totals, grand total (168→177) and negative share (40.5%→40.1%) updated consistently (§1 above). |
| M1-2 minor — §8.0 pointers off by one | **RESOLVED** | §8.0 "Reading a scenario": "§8.17 proves every event in §5.1 has at least one asserting scenario and §8.18 does the same for every `[E-n]`." |
| M1-3 minor — U-a under-scopes the `79` | **RESOLVED** | §2.3 U-a (l.110): "**The same `79` also appears in the Confirm Closing button label** (`index.html:397` …) … **demo data, not a worked example** of the label formula"; §3.9 (l.429): "> **Not a worked example.** … the formula in §3.5 gives `remaining = 81` … `remaining` is **never** `target − ok − warnings`". |
| M1-4 minor — malformed `[L-S4-1..3]` | **RESOLVED** (note) | §8.11 heading (l.1821) and the §8.16 QA-CONFIRM row now enumerate `[L-S4-1]` `[L-S4-2]` `[L-S4-3]`. Sole survival of the composite is the §11 changelog row (l.2385) quoting it in backticks *as the retired form* — historical, but a naive key-checker must whitelist §11. |
| M1-5 minor — PD citations in §8 lack `· OWNER-PENDING` | **RESOLVED** | New **R10** (l.1140), the audit's option 2: "A `[PD-n]` in a QA heading points at the behavior's defining sentence in §3 or §7, which carries the full tag … **`[PD-71]` and `[PD-74]` are NO-DEFAULT (§9.2) and are never asserted by any scenario**." |
| M1-6 minor — §1.3 restates the [G-1] body | **RESOLVED** | §1.3 now: "Hence the three [G-1] invariants, which this page inherits unchanged (deltas in §3.2)." |
| M1-7 minor — §8.16 vs §8.18 disagree on E-35 / E-74 ownership | **RESOLVED** | §8.16 QA-PERSIST row: "E-30…34/36/38/41/53/59/62/71" (E-35 excluded; rationale sentence under the table: "`E-35` is owned by **QA-SCAN** (QA-SCAN-10) and is deliberately absent from QA-PERSIST's range"); QA-HIST row now carries E-74. |

### m2-closing.md (3 FAIL; 0 whole-scenario AMBIGUOUS; 0 UNRUNNABLE; F2–F9 clause fixes)

| Item | Status | Evidence |
|---|---|---|
| **QA-DEL-01 FAIL** ("Delete Scan Row" vs `"Delete Scan Row✕"`) | **RESOLVED** | Spec now: "its `header` R2-normalized text **starts with** "Delete Scan Row" (the header's `✕` close button is nested inside it — R2b; same shape as QA-M1-02)". My re-run: **PASS** (header normalizes to `"Delete Scan Row✕"`, starts-with holds; `#scandelInfo` byte-exact `"#3 · YT2618100710184356"`). |
| **QA-HUB-01 FAIL ×2** (button `"💬 Comments2"`, pane header + `Mark all read`) | **RESOLVED** | Both clauses now `starts with`, each with the R2b callout naming the nested `.badge-n` / `<small>`; plus the new tiering clause "these two pane strings are stale demo copy `[WF-15]`; the canonical `[G-7]` strings are asserted in QA-HUB-09". My re-run: **PASS** (badge `"2"`, 3 entity labels, first two `unread` all hold). |
| **QA-HUB-02 FAIL** (saved pane header) | **RESOLVED** | "`.paneheader` R2-normalized text **starts with** "Comments I saved"". My re-run: **PASS** (tab `on`, saved visible, mentions hidden, exactly one entry `"Order 413498"`). |
| F2 — `reads`/`reads exactly` verb ambiguity | **RESOLVED** | New **R6b** (l.1127) binds every verb: strict equality for `reads`/`reads exactly`/`is exactly`/byte-exact, `startsWith`, substring for `contains`, `yields N` = count; "Never relax `reads` to *contains* … a mismatch is a FAIL to be reported, not normalized away." |
| F3 — nested controls beyond `.dot` | **RESOLVED** | New **R2b** (l.1100) tables all four polluters incl. the latent `span.user`/`.avatar` (`"YYongwon Ryu"`) and sanctions the extended strip-helper as equivalent. |
| F4 — QA-CHROME-04's "23" unverifiable | **RESOLVED** | Scenario now derives 22 from three named DOM counts (19+2+1), asserts `.wf-tab` = 10 and `.wf-tab[data-modal]` = 3, and reconstructs 23 only as the named trap (19+1+3). My re-run: **PASS** — every count assertable as written. |
| F5 — state activation undefined | **RESOLVED** | New **R9** (l.1138): click `.wf-tab[data-state="sX"]` / `.wf-tab[data-modal="m-…"]`; `[ADMIN]` equivalent stated. |
| F6 — `p.sub` not unique | **RESOLVED** | QA-CHROME-02: "the **first** `p.sub` — address it as `#sX .pagepad > p.sub:first-of-type`" + the reason (second `p.sub` = "Scan list …" caption). My re-run: **PASS** in all 7 states, and the second `p.sub` exists in s1/s2/s2b/s3 exactly as the spec states. |
| F7 — QA-S0-01 "card heading" selector-less | **RESOLVED** | Exact filter expression with a match-count-of-1 requirement now in the scenario. My re-run: **PASS** (count === 1). |
| F8 — QA-HIST-03 "green highlight" unassertable | **RESOLVED** | "its inline `style` attribute is exactly `background:var(--green-soft)`, and its computed `background-color` differs from every other data row's … (the other four carry no inline background)". My re-run: **PASS**. |
| F9 — §8.18 non-scenario pointers (E-60/74/77 rows) | **RESOLVED** | Absorbed by M1-1; mechanically verified — 0 `§`/`DQ-` tokens inside mapping cells. |

### m3a / m3b items the remediator claims (spot-checked)

| Item | Status | Evidence |
|---|---|---|
| D2 — closing bypassed the inbound-completeness outbound gate | **RESOLVED** | **BR-38** (l.798): "enabled only when the order has ≥1 line, **every line is `INBOUNDED`**, the status is `processing`, and the order is not cancelled — in addition to the Zero Packing attestation"; §3.21 step 2 carries the gate + reason string; E-78 row (l.1037); QA-M1-14 (l.1757) asserts disabled button, reason, "no **DC-13**, no **DC-14**, no **DC-11**", and names VO `BR-9` / OD L-9 parity. |
| D3 — `Cancelled` treated as a ninth status | **RESOLVED** | §3.6: "**`Cancelled` is not an order status.** The vocabulary is exactly the 8 WooCommerce statuses … cancellation is a separate flag"; verdict-matrix row renders underlying status + `Cancelled` marker; BR-20 restated in flag terms; QA-VERDICT-07 (l.1344) asserts DC-7 `order_status_at_scan` is "never the literal `cancelled`"; the PD-76 register-title mismatch is explicitly flagged for the owner, not silently patched. |
| D7 — Comments-hub copy divergence | **RESOLVED (closing side)** | §3.8 canonical-vs-wireframe two-column string table with `[WF]`/`[ADMIN]` tiering; QA-HUB-01/02 assert wireframe strings, QA-HUB-09 (l.2020) asserts canonical strings; `[WF-15]` registered in §2.3 (l.106) and in `_wireframe-fixes.md` §D (l.140). |
| D11 — `[G-3a]`/PD-2 scope conflict | **NOT RESOLVED — out of file scope (accepted)** | Fixing it requires `_global-rules.md`/PD-register edits. closing.md already carries the by-class application, the owner tension spelled out, and the reversal impact (§3.21 step 5, §6.6) — nothing further is fixable from this file, matching the remediator's claim. |
| D13 / D16 / D19 / D20 | **RESOLVED** | D13: §3.0 (l.133) declares `[GD-n]` resolvable via `_plans/_review.md` §4 with rule text carried inline. D16: §6.3 + QA-HIST-11 use the directory form `../order-detail/#{order_id}`, "never `../order-detail/index.html#…`". D19: §3.7 (l.359–370) value↔label mapping stated once, values in `DC-*` payloads. D20: §3.0 (l.134) fixes the `[G-3a]`/`[G-3b]` citation form. |
| M3b §2.2 — silent-N/A rows | **RESOLVED** | §9.1 carries the 3 new rows (line-based location filter `[G-14]` · audit-mode-only visibility · JIT residual stock) plus the closing sentence naming M3b §2.2 as the trigger. |

**Tally: 1 MAJOR resolved · 3 M2 FAILs resolved · 8 clause/rule fixes (F2–F9) resolved · 6 m1 minors resolved · 7 m3a/m3b items resolved · 1 accepted out-of-scope (D11) · 0 partial · 0 unresolved-in-scope · 0 regressed.**

---

## 3. QA re-run (my own runner, written from v1.2 §8 only)

17 `[WF]` scenarios — every prior FAIL, every prior ambiguous-clause scenario, plus a 10-scenario regression sample. Runner: `scratchpad/rv3_qa_closing.py`.

| Scenario | Prior (m2) | RV verdict |
|---|---|---|
| QA-DEL-01 | **FAIL** | **PASS** |
| QA-HUB-01 | **FAIL** (2 clauses) | **PASS** |
| QA-HUB-02 | **FAIL** | **PASS** |
| QA-CHROME-04 | PASS ⚠ | **PASS** — all counts assertable as written (2/19/2/1/10/3) |
| QA-CHROME-02 | PASS ⚠ | **PASS** — `:first-of-type` unique in all 7 states |
| QA-S0-01 | PASS ⚠ | **PASS** — heading filter matches exactly 1 |
| QA-HIST-03 | PASS ⚠ | **PASS** — inline token byte-exact, computed bg unique |
| QA-M1-02 · QA-COUNT-01 · QA-CONFIRM-01 · QA-SCAN-01 · QA-VERDICT-05 · QA-VOICE-01 (×3 states, `en-US`) · QA-HUB-03 · QA-TARGET-04 · QA-DEL-03 · QA-S0-02 | PASS | **PASS** (all byte-exact strings, raw-`textContent` R2-necessity check `"#6"`/`"Closing Verdict5"`, star toggle, cancel-to-s0, no-renumber delete all held) |

**17 / 17 PASS · 0 FAIL · 0 AMBIGUOUS · 0 UNRUNNABLE.** One interim failure during development was my own selector bug (I read the history table's header `<tr>` as a data row — `.logtbl` has no `<thead>`); the spec's wording "the first **data** row" is unambiguous and the page carries `style="background:var(--green-soft)"` on the true first data row (`index.html`, `07-13 (today)` row), so this was runner error, not a spec or page defect.

---

## 4. Regression check

- **Legend coverage intact:** §2.1 still declares 22 units with the same 19+2+1 recipe; DOM re-count matches; §8.16's unit table lists all 22 + `[L-F1]`…`[L-F4]` with ≥1 scenario each, and new scenarios were folded into the unit rows (e.g. `[L-S1-6]` gained QA-HIST-11, `[L-S1-8]` gained QA-CONFIRM-16).
- **No ID renumbering:** E-1…78 / BR-1…38 / DC-1…25 all continuous; QA blocks extended at the tail only (…-14/-15/-16/-17); §7 preamble documents E-78 as the sole addition; sequence-number and gap explanations unchanged.
- **No new global-rule restatements:** §1.3 fixed; §3.8's canonical-string table is *new page-corpus content* (the strings), not a restatement of the [G-7] body — `_global-rules.md` [G-7] defines hub behavior, not these strings.
- **Wireframe untouched by the remediation:** `git status` clean; last commit touching `wms2/closing/index.html` (d09fe79, 02:03) predates the audits, while `closing.md` was committed at 09:51 — the M2 FAILs were fixed spec-side only, exactly as attributed.
- **Notes (non-blocking):**
  1. Changelog l.2385 quotes the retired `[L-S4-1..3]` composite in backticks — a mechanical key-checker must whitelist §11.
  2. `_wireframe-fixes.md` (l.167–169) records a **number collision**: three concurrent passes each claimed a bare `WF-15`; closing's entry must always be keyed as "`[WF-15]` closing", never by the bare number.
  3. The same file's l.169 **factually disputes** the "four-page majority" provenance for the unstar hint: `order-management` actually renders `Unstar to remove from list` (no "the"), corpus split 2/2/2/1 — so QA-HUB-09's canonical string `"Unstar to remove from the list"` rests on a disputed majority claim, and the six canonical hub strings still need publishing into `_global-rules.md` [G-7] before any wireframe edit. Cross-file coordination work; closing's `[WF]`/`[ADMIN]` tiering itself is sound.

---

## 5. Final readiness verdict

**READY-WITH-NOTES.**

The single MAJOR (false §8.18 traceability claim) and all three M2 FAILs are genuinely fixed and empirically re-verified with an independently written runner; every count the spec asserts about itself reproduces exactly; the QA corpus runs clean (17/17 on the adversarially chosen sample, including every previously failing or ambiguous scenario) under the new R2b/R6b/R9/R10 rules, which close m2's silent-divergence hazards. The notes: (a) D11 and the [G-7] canonical-string unification (including the disputed unstar-hint majority) are **cross-file** work this spec correctly stages but cannot complete — they must land in `_global-rules.md` / `_provisional-decisions.md` and a corpus-wide pass; (b) two cosmetic tooling caveats (§4 notes 1–2). Nothing in this file blocks handing `closing.md` v1.2 to developers or a QA agent.
