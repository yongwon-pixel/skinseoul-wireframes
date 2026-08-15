# RV — Independent Re-Verification · `inbound-request` v1.2

**Verifier role:** independent re-verifier. I neither wrote the spec, nor the wireframe, nor the remediation. Nothing in the remediator's report was taken on trust — every count was re-derived by my own extraction, every claimed fix was located and quoted from the current file, and the QA re-run was coded fresh (not reusing `qa-inbound-request.py`).
**Target:** `wms2/specs/inbound-request.md` (v1.2, 2,045 lines) · SUT `file:///…/wms2/inbound-request/index.html` (850 lines, unchanged — remediation was spec-only, consistent with M2's "culprit spec 8 / wireframe 0")
**Prior findings:** `_verify/m1-inbound-request.md` (3 MAJOR + 9 MINOR) · `_verify/m2-inbound-request.md` (8 FAIL / 0 AMBIGUOUS / 0 UNRUNNABLE)
**Runner:** `(internal scratch path, not published)` — Playwright, headless chromium, 1440×900
**Date:** 2026-08-03

---

## 1. Count re-derivation (own extraction vs spec claims)

| Quantity | Spec (v1.2) claims | RV measures | Match |
|---|---|---|---|
| QA scenarios | 123 — A36 B7 C24 D18 E11 F11 G16 | **123** (A36 B7 C24 D18 E11 F11 G16), no gaps, no duplicate IDs | yes |
| Tier split | 51 `[WF]`-only · 70 `[ADMIN]`-only · 2 dual (A-19, A-25) → 53 WF / 72 ADMIN | **51 / 70 / 2**, dual = QA-A-19, QA-A-25; 0 untagged | yes |
| Negative tests | 56 (45.5 %) | **56 / 123 = 45.5 %** | yes |
| `[E-n]` | 92 (`E-1`…`E-92`, no gaps, no letter-suffixed keys) | **92 numeric IDs, no gaps** — 91 §7 rows / 90 distinct entries via merges `E-1`=`E-14` (row 905) and `E-21`=`E-35` (rows 944/982); zero live letter-suffixed keys | yes |
| `E-18b` | retired, `[E-59]` sole key | 5 occurrences, **all** inside retirement notes (§7 preamble :897, E-59 row :946, §8.3 note :1895, Decision Log :2018) — none is a live key; QA-G-08 keys only `[E-59]` | yes |
| `[DC-n]` | 23 | **23** (`DC-1`…`DC-23`), no refs beyond 23 | yes |
| §8.3 edge-case map | every `[E-n]` ≥ 1 scenario | **exists (line 1842); 92/92 mapped; independently re-parsed scenario bodies also give 92/92 keyed** | yes |
| Ghost scenario refs §8.1–§8.3 | 0 | **0** (every referenced `QA-*` ID is defined) | yes |
| Wireframe | 850 lines · 28 dots · 27 legend rows | `wc -l` = **850**; `.dot` = **28** (S1 15 = {1–12, 14–16, no 13} · S2 2 · S3 10 · modal `M1`); legend `<li>` = **27** (15+2+10) | yes |
| Spec header | "850 lines, v1" | line 3 reads `850 lines` | yes |

Every number the remediator reported is reproduced exactly. No count in the spec is now false against the SST.

---

## 2. Resolution table — M1 defects

| ID | Sev | Verdict | Evidence (quoted from current file) |
|---|---|---|---|
| D1 §2.1 false SST claim | MAJOR | **RESOLVED** | §2.1:83 "carries exactly **28** on-screen `.dot` elements … 27 legend rows"; :89 "**The modal dot `M1` is an orphan dot** — 28 dots vs 27 legend rows. Intentional, not a coverage hole"; :85 retracts the v1.1 claim explicitly ("That claim was false against the SST and is corrected here"); Decision-Log row :2016. Matches my measurement (28/27, `M1` in no legend block). |
| D2 15 unkeyed edge cases | MAJOR | **RESOLVED** | Independent re-parse: **all 92 `E-n` now carry ≥1 scenario key** (merge-aliases credited). The 15 named by M1: E-2→QA-A-31, E-9→A-32, E-11→A-29, E-15/E-54→A-33, E-16→A-20/A-24, E-18→A-34, E-27→C-08, E-31/E-50→C-01, E-56→A-35, E-57/E-63/E-85→A-36, E-90→A-08/A-09. Six new `[ADMIN]` scenarios QA-A-31…36 exist; §8.3 map complete with the invariant stated. |
| D3 bulk→M1 unwired | MAJOR | **RESOLVED** | §2.2 M1 row :105 "or — **`[ADMIN]` only** — `Bulk add tracking numbers` (that button carries no `data-moda[l]`…"; §3.4 :581 "(b) **in the real admin only** … carries no `data-modal` in the wireframe and opens nothing there"; §2.4 demo-limitation list :169 and §8.0 baseline :1049 both name it. Wireframe re-checked: button at :548 still has no `data-modal`. |
| D4 date shorthand §10 | MINOR | **RESOLVED** | All 8 reversal chains (:2034–2041) now use full dates, e.g. "manual PO matching (pre-2026-07-23) → … (2026-07-26, current)". Zero shorthand remains outside wireframe-verbatim demo data (`07-11 14:22` etc., which is data, exempt). *Nit: Decision-Log row :1993 "REVERSAL of the 07-27 reduction" keeps a shorthand back-reference — pre-existing in v1.1 (confirmed in git `60d58ec`) and inside the block M1 itself called compliant; not a regression, not in D4's stated scope.* |
| D5 `E-18b` alias | MINOR | **RESOLVED** | §7:899 "**Total: 92 edge cases** (`E-1` … `E-92`, no numbering gaps, no letter-suffixed keys)"; retirement note :897 "the merge-alias notation `E-18b = E-59` is withdrawn … not a renumbering". §6.4 clean; QA-G-08 keys `[E-59]` only. |
| D6 [G-7] restatement | MINOR | **RESOLVED** | §3.1.13 now: "exactly as specified in [G-7] — its search scope, sort order and click-to-open behavior are the global rule and **are not restated here**", followed by page delta only (entity type, demo entries, badge value, pane-string divergence). |
| D7 PD-63 untagged | MINOR | **RESOLVED** | §9.1:1913 "Provisionally removed **permanently** — not deferred … (2026-08-03, `[PD-63 · OWNER-PENDING]`)" — tag added and claim softened per M1's suggested wording. Decision-Log citations (:2010) remain bare, correctly (citations, not behavior statements). |
| D8 PD scope excludes IR | MINOR | **PARTIAL** | Register **not** edited — verified: `_provisional-decisions.md` still reads PD-12 "Pages: VO (OQ-7/E-15)", PD-16 "Pages: VO (Q3), TM, OD", PD-63 "Pages: TM (Q4), VO (M2b)" (no IR). Instead the spec's Decision-Log row :2028 records the gap and names the exact register edit needed. The remediator declared this deliberately ("register-side only … binding-unchanged reference"), so it is a documented deferral, not a silent miss — but M1's actual fix (add `IR` to three `Pages:` lines) remains outstanding at the register. |
| D9 M1 keyboard contract | MINOR | **RESOLVED** | §3.4 :597–602: "`Enter` in a `.qrow` input **appends a new row and focuses it** … It **never** fires `Save tracking numbers`"; empty-after-trim no-op; wireframe limitation declared, whole contract `[ADMIN]` via **QA-D-18** (:1550), keyed to `BR-24`. |
| D10 E-78/E-79 unregistered | MINOR | **RESOLVED** | §9.3 rows **D-22** (:1962, grouping comparison key) and **D-23** (:1963, escape-at-render policy); §3.1.2 :204 cross-references them; Decision-Log row :2027. |
| D11 851 vs 850 | MINOR | **RESOLVED** | Header line 3: "`wms2/inbound-request/index.html` (850 lines, v1)". `wc -l` = 850. |
| D12 channel-ID placement | MINOR | **RESOLVED** | First mention §3.3.6 :528–529 now carries the annotations ("`_slack-routing.md` publishes no ID for it — that is an unpublished ID, not a pending decision" / "same: name confirmed, ID not published"); §6.1 :840 states the first-mention convention. |

**M1 tally: 11 RESOLVED · 1 PARTIAL (D8, documented deferral) · 0 NOT RESOLVED · 0 REGRESSED.**

---

## 3. Resolution table — M2 FAILs (spec-side fixes + empirical re-run)

§8.0a exists (:1051) with exactly the four binding rules S-1 promised (dot-stripping, selector scoping, controls-scoped negatives, declared trailing elements). Per-scenario:

| ID | Prior failure | Spec fix verified | Re-run |
|---|---|---|---|
| QA-A-02 | unscoped "no card labelled `JIT`" | scoped to "`no .routecard <b>` title and no `.rc-badge` text" + Precision note naming the `<small>` JIT sub-copy | **PASS** |
| QA-A-07 | `.opt` matched 4 | selector now **`#s1 .auto .opt`** + note explaining the `fld opt fld-inv` collision | **PASS** (scoped = 3; bare `#s1 .opt` = 4, exactly as the note states) |
| QA-A-13 | `.dot` inside `<th>` | "normalised per §8.0a rule 1" + note quoting raw `Unit Cost (KRW) *10` / `JIT Price (KRW)11` | **PASS** (raw values match the note byte-for-byte) |
| QA-A-26 | undeclared `.badge-n` | "label **begins with**" + declared-trailing-element note listing the exact 6-element array | **PASS** (measured array identical: `['💬 Comments 1','💬 Comments 2','💬 Comments 3','💬 Comments','💬 Comments','💬 Comments']`) |
| QA-A-28 | "no `Size` anywhere" | scoped to `<th>`/`<label>`/control/cell + note naming the legend-prose `… no Size` occurrence | **PASS** (0 scoped hits; prose occurrence present) |
| QA-C-11 | `.dot` inside 4 `<th>` | normalised + note quoting `Sourcing Route3` / `Tracking No4` / `Received Date10` / `Status5` | **PASS** (12 columns, exact order, no Carrier) |
| QA-D-01 | header `✕` | "excluding the `.x` close control, reads exactly …" + raw-text note | **PASS** (norm = `Add Tracking No — 202607130003`, raw = `…✕`) |
| QA-F-02 | `.it` matched 3 | selector now **`#inbox1 [data-pane="mentions"] .it`** + note | **PASS** (scoped = 2, bare = 3 as the note states) |
| QA-A-17 (caveat S-7) | "red `*`" unexecutable | now "computed `color` is exactly `rgb(220, 53, 69)` (the page's `--red`, `#DC3545`)" | **PASS** (computed color measured `rgb(220, 53, 69)`; `--red:#DC3545` confirmed in CSS) |
| QA-B-01 (caveat S-5) | `.submitrow` equality impossible | scoped to **`#s2 .submitrow .mut`**, normalised, + scoping note | **PASS** (exact-string equality holds on the scoped element) |
| QA-D-03 (caveat S-6) | "value cleared" vacuous | "**type the marker value `TEST123`** … Execution note: the marker value is mandatory" | **PASS** (typed `TEST123`, final `✕` → row survives, value `''`) |
| QA-B-06 (S-3 SHIPPED) | latent full-text trap | negative scoped to `.chip,.tag,.pill,option,button` + Precision note | **PASS** (0 control hits). *Nit: the note says `SHIPPED` appears "3 times in legend and footer prose" — rendered prose has **2** (index.html:512, :660); the third is a CSS comment (:90), not prose. Cosmetic; no assertion depends on it.* |

Prior M2 AMBIGUOUS/UNRUNNABLE: none existed; nothing to re-verify there.

**M2 tally: 8/8 FAILs RESOLVED (spec-side, as claimed — 0 wireframe edits needed or made).**

---

## 4. QA re-run results

16 `[WF]` scenarios executed fresh against the file URL — the 8 prior FAILs, the 4 prior caveats (A-17, B-01, D-03, B-06), and 4 regression picks that previously passed (A-18, C-14, F-04, G-16):

**16 PASS · 0 FAIL · 0 AMBIGUOUS.**

Self-audit disclosure (M2 discipline): my first run produced 3 failures, all **runner** defects, fixed before judging — (a) I asserted a `show` class on `#gtoast` when the wireframe toggles `style.display` (the spec's "becomes visible / is hidden" wording is correct and mechanism-neutral); (b)/(c) my `#s3 button` selector caught the state-mock's own nav hub button instead of the six table `.comment-btn` Actions buttons — the spec's wording ("Request List Actions button", "click `💬 Comments` **in row** `202607130002`") already disambiguates this; sloppy transcription, not spec ambiguity. Zero spec-attributable failures remained.

---

## 5. Regression checks

| Check | Result |
|---|---|
| Legend coverage | **Intact.** 51 distinct `[L-*]` keys: S1-1…12, 14…16, S1-F · S2-1, 2, F · S3-1…10 · M1 · F1–F9 · R1–R12 — matches the wireframe dot sets exactly (S1 has no 13, declared; `M1` declared orphan). No legend unit specified nowhere. |
| ID renumbering | **None.** E range still 1–92 with the same merges; DC still 1–23; QA additions are appends only (A-31…36, D-18, F-11) — all pre-existing IDs untouched; no `E>92` / `DC>23` references anywhere. |
| Global-rule restatement | **None new.** The one M1 found (§3.1.13/[G-7]) is reduced to citation + delta; no other rule-body reproduction introduced in the remediation-pass diffs (Decision-Log rows :2016–2030 all cite, never restate). |
| Wireframe untouched | 850 lines, 28 dots, 27 legend rows, bulk button still inert — consistent with "0 wireframe fixes" claim. `_wireframe-fixes.md` §G carries **`[IR-WFX-1 · proposed]`** (:208–212), page-scoped token with the collision rationale, conditional on `[G-7]`, marked do-not-apply-now. |
| M3b N/A rows | Present: §1.5 rows for JIT residual stock, [G-14] location filter, [G-14] audit-mode visibility, [G-6] Korean picking names (:61–66 area) **and** §9.1 ownership rows (:1913–1917 area); Decision-Log row :2026. |

---

## 6. Readiness verdict

**READY-WITH-NOTES.**

All 3 MAJOR M1 defects and all 8 M2 FAILs are empirically resolved; every count the spec asserts about itself and about the SST is now true by independent re-derivation; the full 16-scenario adversarial re-run (all prior failure surface included) is clean. Three non-blocking notes:

1. **D8 residual (the only PARTIAL):** `_provisional-decisions.md` still lacks `IR` on the `Pages:` lines of PD-12 / PD-16 / PD-63. The spec's Decision-Log row :2028 names the exact edit; apply it in the next register pass or the register's reverse-impact list stays incomplete for this page.
2. **QA-B-06 precision-note miscount:** "3 times in … prose" should be "2 in prose (+1 in a CSS comment)". No assertion depends on it; fix opportunistically.
3. **Line 1993 `07-27` back-reference** in the Decision Log — pre-existing v1.1 text outside D4's scope; expand to `2026-07-27` opportunistically.

None of the three blocks implementation or unaided AI QA execution of §8.
