# RV — Re-verification of the Remediation: `tracking-missing.md` (spec v1.2)

**Method:** independent re-verification. The auditor neither wrote the spec, nor performed the remediation, nor reused the m2 runner. Counts were re-derived with fresh scripted extraction over the edited spec; every m1 MAJOR/BLOCKER and every m2 FAIL/AMBIGUOUS/UNRUNNABLE was checked against the current file text; 20 `[WF]` QA scenarios were re-executed with a freshly written Playwright suite against `file:///…/wms2/tracking-missing/index.html` (headless Chromium, 1280×800).
**Date:** 2026-08-03. **Scripts:** scratchpad `rv_tm_counts.py` / `rv_tm_counts2.py` / `rv_tm_qa.py` (+ 2 targeted re-runs). Wireframe untouched — only the spec was edited, as the remediation claims.

---

## 1. Count re-derivation (Q1)

| Claim (spec §8.0 / remediator) | Independently re-derived | Match |
|---|---|---|
| 168 scenarios | 168 definition lines (`**QA-… [WF\|ADMIN]**`) | YES |
| 66 `[WF]` : 102 `[ADMIN]` | 66 : 102 | YES |
| 61 negatives = 36.3 % (≥ 25 % floor) | 61 = 36.3 % | YES |
| Per-block totals `12·16·13·13·10·12·15·10·15·12·6·9·13·5·7 = 168` | identical, block by block | YES |
| Per-block `[WF]` `11·9·5·9·5·3·7·5·1·0·2·0·0·2·7 = 66` | identical | YES |
| Per-block negatives `4·4·4·3·0·3·3·3·15·10·2·4·3·0·3 = 61` | identical | YES |
| Zero duplicate QA IDs | zero | YES |
| DC 28 · BR 44 · E 72 · N 12 — no gaps, unchanged | DC 1–28, BR 1–44, E 1–72 continuous; N 1–12 (N-2/N-11 defined unbracketed in the §5.2 table, all 12 present) | YES |
| §8.18 cites no non-existent QA ID | phantom QA citations in §8.18 = 0; whole-document phantom = 0 | YES |
| Every `[E-n]` except `[E-4]` carries ≥ 1 Then-clause | scenario bodies (§8.1–§8.15) cite 71 of 72; the only uncited is **E-4**, the declared exception | YES (one token nit → §4 note 1) |

The WF-count movement is exactly the remediation's arithmetic: 67 → 66 = −1 (QA-NEG-03 → `[ADMIN]`) −1 (QA-XPG-05 → `[ADMIN]`) +1 (QA-WFQ-07 new).

## 2. Resolution table (Q2)

### m1 defects

| ID | Sev | Verdict | Evidence (quoted from the current file) |
|---|---|---|---|
| D-1 | BLOCKER | **RESOLVED** | §3.3 now has a two-surface rendering table and a dated delta: *"Route label rendering — declared page delta on `[G-5]` (decided 2026-08-03)"* … *"the badge contract lands on M1's `Channel` cell only; the pool cell's route is muted running text (`--ink-3`, non-bold), and the never-a-pill prohibition holds on both"*, with reversal impact spelled out ("change the format line… split the `.mut` span… re-tag QA-SUS-05's colour clause `[ADMIN]`"). `[BR-15]` rewritten to the same two-surface delta ("**Page delta on `[G-5]`, two surfaces**… pool-cell delta 2026-08-03"). QA-SUS-02 and QA-SUS-05 are now mutually consistent (both assert `rgb(126, 124, 131)` on the pool cell; QA-M1-10 keeps the ink badge). Both **PASS** in the live re-run. Decision-log rows present. |
| D-2 | MAJOR | **RESOLVED** | QA-NEG-03 is `[ADMIN] (neg)` with the reason inline: *"the wireframe cannot exhibit this — its `.xdel` handler removes one row but runs `poolDec()` twice (defect `WF-NEW-D`, §2.4.10)"*. Counterpart QA-WFQ-07 `[WF]` added and **PASSes live** (rows 2, counters `1`/`1`). §2.4 limitation 10 added, naming the `finishMatch()`-guards/`.xdel`-doesn't asymmetry verbatim. WF-NEW-D filed in §2.5 **and** appended to `_wireframe-fixes.md` §B (line 70, `[WF-NEW-D · tracking-missing]`). |
| D-3 | MAJOR | **RESOLVED** | §8.18 "Edge-case → QA coverage map" exists with all 72 rows; scripted check: every `[E-n]` except the declared `[E-4]` is cited by ≥ 1 scenario body. The previously-orphaned dangerous case `[E-26]` now has QA-NEG-14 (*"step 4 comment post or step 5 Slack dispatch then fails, Then the match is **not** rolled back"*); E-58→QA-FURN-10, E-29→QA-VAL-12, E-30→QA-ROW-13, E-33→QA-M1-13/QA-ROW-15, E-44→QA-ROW-14, E-45→QA-ROW-15/16 etc. all land. |
| D-4 | MINOR | **RESOLVED** | QA-NEG-02 body now cites `[DC-10]`; QA-VAL-05 now cites `[DC-13]` (scripted: True/True). Decision-log row names m1 D-4. |
| D-5 | MINOR | **RESOLVED** | `[BR-19]`: *"**Page-level extension of `[PD-8]`, declared as such.** … The extension is **not** register-backed — if the owner declines it, delete this rule, `[E-11]`, QA-VAL-03 and step 1's `tracking_in_use` check"*. `[L-1]` column 1 now defines the namespace (*"stored with the namespace the scan originated in — `outbound` for a customer parcel, `inbound` for an unrequested supplier arrival"*) and names the `[E-33]` blind spot (*"the namespace check is silent there by design, so `[E-33]`'s only defence remains the memo"*). |
| D-6 | MINOR | **RESOLVED** | Reading-contract item 1 reworded: *"restates a global rule body **only where the page narrows or extends it**, and in that case the delta, its rationale, and its date are named"*. BR-23 trimmed to the two key shapes, BR-27 framed as *"Page extension of `[G-7]`'s append-only property"*, BR-34 as *"Stated as a negative registry entry, not as a restatement"*, BR-15 as the §3.3 delta pointer. |
| D-7 | MINOR | **NOT RESOLVED as prescribed — reasoned alternative, accepted** | No `GD-11` was raised (out of the remediator's write scope: `_global-rules.md`/`_review.md` binding). Instead `[BR-44]` is *"**Candidate global amendment, stated locally under protest**… **Do not copy this row into another spec**… deletes this row the day the global text lands"*, and reading-contract item 7 lists all three such locals (BR-44, §5.1 event-name note, §3.6 hub strings). The divergence risk is contained, not eliminated; the follow-up belongs to the global-rules owner. |
| D-8 | MINOR | **RESOLVED** | §9.3 row now reads `[PD-51 · OWNER-PENDING]` with "NO-DEFAULT and owned by order-management / RTO / order-detail, cross-referenced from here only"; §9.1 cross-referenced list now includes PD-51 (5 entries) and the PD arithmetic (16 + 5 + PD-66 = 22) is stated and checks out. |
| D-9 | MINOR | **RESOLVED** | QA-XPG-05 re-tagged `[ADMIN] (neg)` with the reason inline (three of four clauses are server/Slack state; trigger on another page). §8.0 `[WF]` definition hardened: *"**Every `[WF]` scenario in this document runs against that one URL** — no `[WF]` scenario targets another page's wireframe."* No `[WF-XPG]` tag invented — consistent with `_review.md` §3.4's two-tag scheme. |
| D-10 | MINOR | **RESOLVED** | §8.0: *"Of these, **one** (QA-VAL-10) is `BLOCKED` and carries no verdict; it is counted inside the 168 and inside the 102 `[ADMIN]`."* No 152/169 reconciliation trap remains. |

### m2 FAIL / AMBIGUOUS / UNRUNNABLE

| ID | m2 verdict | Verdict now | Evidence |
|---|---|---|---|
| F1 QA-LOAD-04 | FAIL | **RESOLVED** | §8.0 rule 1 (*"Annotation dots are stripped before any text comparison"*) + scenario amended (*"each taken with its `.dot` annotation child removed… Without the strip the raw texts are `Product Name4`…"*). Re-run: **PASS** — stripped headers match the 12 exactly. |
| F2 QA-M1-01 | FAIL | **RESOLVED** | Scenario now asserts the *"`<header>`'s **leading text node**"* and declares the full `textContent` is `Review & Match — Unrecognized Product✕` (§8.0 rule 5). Re-run: **PASS** (leading text node exact, `button.x[data-close]` present). |
| F3 QA-NEG-03 | FAIL | **RESOLVED** | = m1 D-2 above. QA-NEG-03 `[ADMIN]`; QA-WFQ-07 **PASSes live** with the exact divergence the spec states (1 row removed, counters read `1`). |
| F4 QA-SUS-05 | AMBIGUOUS | **RESOLVED** | Scenario now names *"the **four** trailing `span.mut` elements in the pool's `Suspected Orders (Auto-matched)` cells"* with exact computed values (`rgba(0, 0, 0, 0)` / `border none` / `padding 0px` / `rgb(126, 124, 131)`) and warns the badge form lives in M1 only. Re-run: **PASS** on all 4 elements — no reading ambiguity left; a `.tag-*` sweep would indeed pass vacuously on the main page, and the spec now says so. |
| F5 QA-XPG-05 | UNRUNNABLE | **RESOLVED** | = m1 D-9 above. Out of the `[WF]` tier entirely; the closing-side half is delegated to the closing spec. |
| m2 §5/§6-6 shared selectors | secondary | **RESOLVED (one residual nit)** | §8.0 rules 2–4 now cover `table.tbl` ×2, nested `.mockwrap` (both must be scrolled), positional `.it`. Residual: see §4 note 2. |
| m2 §6-7 soft assertions | secondary | **RESOLVED** | QA-EMPTY-01 quantified (*"inner `.mockwrap` bounding-box height **> 300 px**, `<thead>` still rendered with its 12 `<th>`, `#poolCountBottom` below the `<thead>`"*); QA-NEG-01's toast cycle got a measurable definition (continuously `flex` then `none`, no return within 6 s — re-run **PASS**); listener probes routed through §8.0 rule 6 (CDP; not-run, never FAIL, without it). |

**Remediator's two "not fixed, with reason" items** (m1 D-7 / m3a global-rules halves; m3b silent-N/A rows): both verified as described — the alternatives are recorded page-side (reading-contract items 6–7, §2.5 register-citation warning naming WF-9→WF-10, §2.6 rows 9/10/11 explicit `n`) and the refusals are scope-correct, not evasions.

**Register appends:** `_wireframe-fixes.md` §B carries `[WF-NEW-D · tracking-missing]` (line 70) and `[WF-NEW-E · tracking-missing]` (line 79), each cross-citing the spec, with the number-collision note explaining why the IDs are page-scoped letters (three concurrent passes claimed WF-15/16). Verified in the register file itself.

## 3. QA re-run (Q3)

20 `[WF]` scenarios executed (priority: every previously non-PASS scenario, plus a regression sample). Fresh Playwright suite; §8.0 reset (full reload) before each.

| Scenario | Verdict | Note |
|---|---|---|
| QA-LOAD-04, QA-M1-01, QA-SUS-05 | **PASS** | the three previously FAIL/AMBIGUOUS — all clean under the amended text |
| QA-WFQ-07 (new) | **PASS** | rows 2 · `#poolCount`/`#poolCountBottom` = `1`/`1`, exactly as pinned |
| QA-LOAD-01, -05, -06, -07 | **PASS** | baseline, counters, removed-features negative, legend 6 li / 7 dots |
| QA-SUS-02, QA-M1-10 | **PASS** | both halves of the reconciled `[G-5]` delta hold live |
| QA-MATCH-02, -03, QA-XDEL-01 | **PASS** | happy-path removal + counters |
| QA-NEG-01 | **PASS** | double-dispatch guarded; exactly one toast cycle (flex → none, no return ≤ 6 s) |
| QA-WFQ-03, QA-WFQ-06 | **PASS** | no dialog/toast on `✕`; annotation toggle both directions |
| QA-CMT-03, QA-CMT-05 | **PASS** | positional `.it` (4 items / 3 unread); Saved tab (1 item, `Unrecognized pool`) |
| QA-EMPTY-05 | **PASS** | Cancel / header `✕` / backdrop — all three close with zero side effects |
| QA-A11Y-01 | **PASS** | tab order `Review & Match` → `.xdel` |

**20 / 20 PASS · 0 FAIL · 0 AMBIGUOUS.** Four interim failures during the run were all traced to this auditor's own harness (Playwright locator re-resolution between dispatches; `:first-of-type` matching both tables; counting the closed modal's hidden dot) — none is a spec or wireframe fault; all four scenarios pass under a correct reading of the spec text. QA-NEG-03 and QA-XPG-05 were confirmed absent from the `[WF]` tier.

## 4. Regression check (Q4) — none found, two cosmetic notes

- **Legend coverage intact:** §8.17 still maps all **13** declared units (`L-0…L-5, L-M1, L-M2, L-F1…F3, L-S1-Fa/Fb`).
- **No ID renumbering:** all 66 scenario IDs from the m2 run still exist under their original IDs; DC/BR/E/N ranges continuous at the same maxima; new scenarios only append (ROW-13…16, NEG-14/15, WFQ-07, CMT-12…15, …).
- **No new global-rule body restatements:** the four flagged BRs were trimmed, not expanded; the three deliberate local statements are declared in reading-contract item 7 with do-not-copy markers.
- Note 1 (cosmetic): **E-16**'s literal `[E-16]` citation inside §8 sits only in the §8.6 block heading; the §8.18 row (`E-16 → QA-XDEL-04, QA-WFQ-03`) is semantically accurate — those two scenarios assert exactly the `[ADMIN]` dialog and `[WF]` no-dialog halves E-16's own row prescribes — but neither body carries the token. Harmless; a future sweep keyed on scenario bodies will flag it.
- Note 2 (cosmetic): §8.0 rule 2's example selector `table.tbl:first-of-type` does not implement its own prose. Both tables are `:first-of-type` within their respective parents, so the literal selector matches rows in **both** (empirically: 17 `<th>`, 12 + 5). The prose ("`table.tbl` means the **first** — the pool table") is unambiguous and is what every scenario's wording relies on; only the illustrative selector string is a CSS footgun. Suggested one-word fix at leisure: address the pool table as `document.querySelectorAll('table.tbl')[0]` or scope by ancestor.

## 5. Verdict

**READY-WITH-NOTES.**

All 1 BLOCKER + 2 MAJOR from m1 and all 5 non-PASS items from m2 are genuinely resolved in the current file, with live re-run evidence; the two items the remediator declined to fix are scope-correct refusals with the alternative recorded page-side. Counts, tier splits, the negative floor, and both coverage maps reproduce exactly under independent extraction. The two residual notes are cosmetic (a citation-token placement and an illustrative selector string) and neither can produce a false QA verdict under the spec's prose. Remaining external dependencies — the `[G-2]`/`GD` promotion (BR-44), the `[G-7]` hub-string amendment (WF-NEW-E), and the `[PD-66]` owner ruling (QA-VAL-10 BLOCKED) — are tracked outside this spec by design and do not gate implementation of this page.
