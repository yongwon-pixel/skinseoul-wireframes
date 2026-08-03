# RV — Independent re-verification of the v1.2 remediation · `order-detail.md`

Verifier: independent (neither authored the spec nor the remediation). Nothing in the
remediator's report was trusted; every number below was re-derived by script over
`specs/order-detail.md` (2,450 lines, v1.2) and every QA verdict re-measured with Playwright
(headless Chromium, 1680×1000) against
`file:///Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/order-detail/index.html`.

- **Date:** 2026-08-03
- **Inputs:** `_verify/m1-order-detail.md` (3 MAJOR · 11 MINOR), `_verify/m2-order-detail.md`
  (4 FAIL · 1 AMBIGUOUS · 0 UNRUNNABLE), remediator's claim summary
- **Re-run script:** scratchpad `rv-qa-order-detail.py` (16 `[WF]` scenarios + 1 premise probe)

---

## 1. Count re-derivation (own extraction vs spec §8.1 vs remediator's claims)

| Metric | Spec asserts | My extraction | Verdict |
|---|---|---|---|
| Total QA scenarios | 161 | **161** (0 untagged, 0 duplicate ids) | MATCH |
| `[WF]` / `[ADMIN]` | 68 / 93 | **68 / 93** | MATCH |
| `[WF]` share | 42.2 % | **42.2 %** | MATCH |
| Negative (heading) | 79 (49.1 %) | **79 (49.1 %)** | MATCH |
| Negative (any clause) | 118 (73.3 %) | **118 (73.3 %)** | MATCH |
| Per-block §8.1 rows | 13 rows | all 13 rows **match cell-for-cell** (Scenarios · WF · ADMIN · neg-heading · neg-any) | MATCH |
| BR range | 1–50, never renumbered | **BR-1…BR-50, 0 gaps** | MATCH |
| DC range | 1–37 | **DC-1…DC-37, 0 gaps** | MATCH |
| NE range | 1–16 | **NE-1…NE-16, 0 gaps** | MATCH |
| E range | 1–92, no gaps | **E-1…E-92, 0 gaps** | MATCH |
| `[E-n]` referenced in §8 | all 92 (E-69 via §8.4 exclusion row) | **92/92** — unreferenced set is empty | MATCH |
| `[L-F*]` keyed in §8 | all 17 | **F1–F17 all present** (F2 on QA-SUB-1/QA-DC-7, F16 on QA-CMT-1/QA-DC-3) | MATCH |
| `reason_code` values | §5.1 enum (10 values) | 9 distinct values used in `reason_code=` form + `status_blocks_outbound` in set form — **all ∈ §5.1 enum, none invented** | MATCH |

**All counts the remediator stated are true.**

---

## 2. Resolution table — M1 (BLOCKER/MAJOR first, then MINOR)

| # | Defect (m1) | Verdict | Evidence (current file) |
|---|---|---|---|
| D1 | MAJOR — `QA-INB-3` guaranteed-fail (forbade legend text) | **RESOLVED** | Line 1445: "the string `Request Inbound` appears in **no** button label, **no** header cell and **no** body text inside `#st-normal` or `#st-hold`" + inline note scoping the legend out (`annotation chrome NE-13 … required by QA-MAP-5's sibling assertion`). Playwright: PASS (0 product-surface hits; legend mention present as expected). |
| D2 | MAJOR — `QA-DC-9` asserted 8 distinct codes where mappings yield 7 | **RESOLVED** | Line 2184: "**eight** `order.action_rejected` events persist … **seven distinct codes across eight events**" with the codes listed in trigger order (`order_outbounded` ×2) and a guard note "Do **not** assert eight distinct codes". Matches m1's own option (a). |
| D3 | MAJOR — 19 of 92 `[E-n]` had no QA scenario | **RESOLVED** | Script: unreferenced-in-§8 set = **∅**. 14 new scenarios exist (`QA-INB-17/18`, `QA-CMT-16`, `QA-OUT-13`, `QA-REN-17`–`20`, `QA-SUB-20`, `QA-NET-1`–`5`); §8.4 (line 2262) is the demanded exclusion table — sole full exclusion is `E-69` (org-policy statement; its machine-checkable half asserted by `QA-SUB-20`), exactly what m1's fix proposed. New `[WF]` scenario `QA-REN-17` re-run: PASS. |
| D4 | MINOR — "Four furniture keys" lists three | **RESOLVED** | Line 140: "**Three** furniture keys are specified inside the legend entry … 14 + 3 = all 17". |
| D5 | MINOR — bare `MM-DD` decision dates | **RESOLVED** | Regex sweep for `MM-DD` not preceded by `2026-`: every remaining hit is a quoted wireframe demo timestamp (`07-01 09:32`, `07-13 10:42` …), which are verbatim page strings, not decision dates. §2.1 now reads "the 2026-07-22 and 2026-07-23 edits"; compounds `2026-07-22/23` count = 0. |
| D6 | MINOR — BR-28 cited `[PD-19]` as support | **RESOLVED** (note) | Line 793 rationale now *disclaims* it: "(No PD governs the surface set — `[PD-19 · OWNER-PENDING]` decides only that an offline print agent never gates the inbound, and is cited where it belongs, in `[L-13]` and `[E-39]`.)" The misattribution is gone; the token still appears in the cell, so a purely mechanical PD-citation counter will still count BR-28 — semantically correct, mechanically visible. |
| D7 | MINOR — self-mention suppression unregistered | **RESOLVED** (via m1's own alternative) | `[L-1]` step 9 (line 303) rewords to "By analogy with `[PD-16 · OWNER-PENDING]` … Suppression is therefore the **dev default**, recorded in §9.4 D-19"; §9.4 row D-19 exists (line 2339). Register entry remains owner work — the report explicitly offered this path. |
| D8 | MINOR — `E-40` silently resolved Q-A5 | **RESOLVED** (same pattern) | `E-40` (line 1132): "**Dev default, not a PD** … recorded in §9.4 D-20"; §9.4 row D-20 exists (line 2340); `[L-13]` and `[L-F7]` carry the same reference. PD registration remains owner work, as allowed. |
| D9 | MINOR — `[L-F2]`/`[L-F16]` unkeyed in §8 | **RESOLVED** | Headings: `QA-SUB-1 [L-F1] [L-F2] …` (1976), `QA-DC-7 … [L-F2]` (2169), `QA-CMT-1 [L-1] [L-F16]` (1260), `QA-DC-3 … [L-F16]` (2146). |
| D10 | MINOR — two-line headers break byte-accuracy | **RESOLVED** | §8.0 rule 2 (line 1205): `<br>` → space, collapse, trim, naming the four two-line headers. Playwright QA-REN-1 with that contract: PASS. |
| D11 | MINOR — §2.1 provenance map incomplete | **RESOLVED** | Line 75: "…specified under `[L-1]` (Operator Comments position), `[L-6]`, `[L-10]`, `[L-F8]`, `[L-F9]`, `[L-F12]` and `[L-F17]` — with the 1680px Line Items horizontal scroll specified in §1.3 and `[L-10]`." |
| D12 | MINOR — sample-set clone exclusion presented as PD-31 content | **RESOLVED** | `[L-F4]` (line 716): "**an extension beyond PD-31's registered list** … follows from `[G-13]`'s period rules … Recorded as an extension rather than as PD-31 content"; BR-21 (786) and E-83 (1174) restate the same split. Register append remains owner work (register is binding-unchanged). |
| D13 | MINOR — `QA-OUT-3` ambiguous scope | **RESOLVED** | Line 1556: "**no button label** in either state reads `Outbound to Deleo BaroShip`, and the string appears in **no** body text inside `#st-normal` or `#st-hold`" + explicit legend carve-out. Playwright: PASS, and PASS **in the same run** as QA-MAP-5 (contradiction gone). |
| D14 | MINOR — tracking-sync cadence specified nowhere | **RESOLVED** | §9.4 D-18 (line 2338): cadence + scheduling owner as a dev decision, observable via `DC-23`, marker = last successful sync, `[E-43]` no fabricated time. |

## 3. Resolution table — M2 (4 FAIL · 1 AMBIGUOUS)

| Finding | Verdict | Evidence |
|---|---|---|
| F-2 / QA-OUT-3 ↔ QA-MAP-5 deadlock (FAIL) | **RESOLVED** | Rescoped text above; empirically both PASS in one run (`legend historical quote present=True` while product surface clean). |
| F-3 / QA-INB-3 (FAIL) | **RESOLVED** | Rescoped text above; PASS. §10.2 scope note added (line 2419): forbids the item "as a rendered control", never the legend's retirement sentence. |
| F-1+Fix5 / QA-DEL-1 (FAIL) | **RESOLVED** | Line 1766: "`#m-del .modal header`'s **first text node** is exactly `Are you sure?`", `.x` child acknowledged, flattened text `Are you sure?✕` pre-stated. Playwright first-text-node probe: PASS. |
| F-4 / QA-STA-4 mis-tagged `[WF]` (FAIL) | **RESOLVED** | Retagged `[ADMIN]` (line 1641) with a one-line tier reason; registered as `[OD-WFX-1 · proposed]` in `_wireframe-fixes.md` §I (line 248) — deliberately **not** `WF-15`, which the register's §F collision warning shows was claimed by three concurrent passes; token cross-referenced from §2.5 A (line 147), §8.3 step 4 (2253), §9.5 (2352). **Premise re-measured:** status dropdown stays visible after a background click (`True→True`), zero `document.addEventListener` in the wireframe source, while the modal's backdrop click closes it (`open→False`) — the asymmetry is real, so keeping the spec behavior and blaming the drawing is the factually correct resolution. |
| F-5 / QA-STA-6 no comparison basis (AMBIGUOUS) | **RESOLVED** | Line 1654: mandatory comparison basis (normalized visible text, §8.0 rules 1–2, not DOM/attributes) + diff (6) added: state-suffixed ids `inbox1/inbox1H`, `statusdd/statusddH`, `addCmt/addCmtH`, `#ordStatus`/`#obBtn` State-1-only, `#holdBannerH` State-2-only. Playwright: text-identical blocks all True, row 2 differs, id sets exactly as enumerated — PASS with no invented convention. |
| F-1 systemic / Fix 4 (§8.0 contract) | **RESOLVED** | §8.0 four-rule "MANDATORY — text extraction and string comparison" table (lines 1200–1209): `.dot` strip, `<br>`/whitespace normalization, `reads exactly` vs `reads` registers, node scoping; names the 8 verdict-flipping scenarios. All 8 named scenarios that are `[WF]` were in my re-run sample; all PASS under the published contract. |
| Fix 7 / QA-MAP-3 vacuous scroll | **RESOLVED** | Scenario now scrolls to y=600 before the tab click and says why; PASS (scrollY 600 → 0). |
| Fix 8 / QA-HUB-1 exact/contains trap | **RESOLVED** | "2 buttons whose labels **begin with** `@ Mentions` and `★ Saved`" + badge-child note; PASS. |
| F-7 / QA-REN-3 non-assertion clause | **RESOLVED** | Line 1871: "*(Runner guidance, not a machine-checkable clause: it constrains the report, not the page …)*". |

**M1: 14/14 RESOLVED · M2: 9/9 RESOLVED · 0 PARTIAL · 0 NOT RESOLVED · 0 REGRESSED.**

---

## 4. QA re-run (Playwright, 16 `[WF]` scenarios + 1 premise probe)

Sample prioritised every previously-failed/ambiguous scenario, its contradiction partner, all
runnable §8.0-contract-affected scenarios, one new v1.2 scenario, and the legend census as a
regression guard.

| Scenario | Prior (m2) | Now | Note |
|---|---|---|---|
| QA-INB-3 | FAIL | **PASS** | 0 product-surface hits; legend mention expected |
| QA-OUT-3 | FAIL | **PASS** | passes alongside QA-MAP-5 in the same run |
| QA-DEL-1 | FAIL | **PASS** | first text node `Are you sure?`, `.x`=`✕` |
| QA-STA-6 | AMBIGUOUS | **PASS** | basis published; 6-diff id sets exact |
| QA-MAP-5 | PASS | **PASS** | still requires the legend item 9 strings |
| QA-MAP-1 | PASS | **PASS** | 13/14/M3/28/14 census unchanged (regression guard) |
| QA-MAP-3 | PASS (runner-invented scroll) | **PASS** | scroll step now in the spec |
| QA-HUB-1 | PASS (convention-dependent) | **PASS** | prefix semantics now in the spec |
| QA-REN-1 | PASS (convention-dependent) | **PASS** | 18 columns, `<br>` normalization per §8.0 |
| QA-REN-9 | PASS (convention-dependent) | **PASS** | dot-stripped synced heading exact |
| QA-SUB-3 | PASS (convention-dependent) | **PASS** | `Egita` + bordered `✎ Edit` after dot-strip |
| QA-INB-4 | PASS (convention-dependent) | **PASS** | footer order + exact labels after dot-strip |
| QA-OUT-2 | PASS (convention-dependent) | **PASS** | banner byte-exact after dot-strip |
| QA-STA-5 | PASS | **PASS** | badge/class/banner per state |
| QA-CMT-1 | PASS | **PASS** | 89-char placeholder byte-exact |
| QA-REN-17 | — (new in v1.2) | **PASS** | 4 `–` cells, 0 `<a>`, cost `₩22,425` |
| QA-STA-4 premise | FAIL as `[WF]` | **CONFIRMED `[ADMIN]`** | dropdown stays open on bg click; modal backdrop closes; no document-level handler in source |

**16 PASS / 0 FAIL / 0 AMBIGUOUS.** Every scenario executed with only the spec's selectors,
strings and the §8.0 contract — no private conventions needed.

## 5. Regression checks

- **Legend coverage:** intact. Dot census 13/14/M3/28/14 with `.n` order `1,2,3,4,5,6,12,10,11,14,13,9,7,8` matches §2.1 exactly (QA-MAP-1 PASS); §3 headings `[L-1]`–`[L-14]`, `[L-M3]` all present.
- **No ID renumbering:** BR-1…50, DC-1…37, NE-1…16, E-1…92 all contiguous; §4 note "IDs are never renumbered" now covers the v1.2 additions (`BR-49`/`BR-50` appended, none moved); v1.2 delta (line 2214) states no scenario renumbered or deleted — per-block arithmetic (147 + 14 new = 161; 68 WF = −QA-STA-4 +QA-REN-17) checks out.
- **No new global-rule body restatements:** §3.0.1 remains delta-only (every row cites `[G-n]` and states this page's delta; the one quoted sentence is the `[GD-5]` amendment citation from `_review.md` §4, not a rule body). §2.7 and §8.0 additions are page-scoped.
- **`_wireframe-fixes.md` discipline:** the new entry uses the page-scoped token `[OD-WFX-1 · proposed]`, avoiding the three-way `WF-15` number collision the register's §F warns about; deploy rule (`/wf-deploy order-detail`, do not apply now) carried.
- **M3a/M3b spot-checks:** §2.7 `[X-1]`–`[X-9]` table present with per-row reversal impact; `BR-49`/`BR-50` state the Cancel-Inbound and no-`OUTBOUNDED` positions with `[X-1]`/`[X-4]` cross-references; `Unstar to remove` deliberately kept (`[X-6]`, wireframe SST — confirmed as the shipped string by QA-HUB-3's prior PASS); §9.1 carries the explicit out-of-scope rows; §3.0.1 records both notation notes (G-3 sub-rule form; `_review.md` §2b `Δ`-coding staleness).

## 6. Readiness verdict

**READY-WITH-NOTES.**

All 14 M1 defects and all 5 M2 FAIL/AMBIGUOUS findings (plus the 3 minor M2 fixes) are
genuinely resolved in the file, the spec's self-reported counts are all reproducible, and the
re-run QA sample is 16/16 PASS with zero invented conventions. The notes are open work the spec
itself correctly declares, not defects:

1. `[OD-WFX-1 · proposed]` is unapplied — `QA-STA-4` stays `[ADMIN]` until the wireframe gains
   the outside-click handler (ship via `/wf-deploy order-detail`).
2. Three register additions remain owner work (PD for self-@mention → D-19, PD for Q-A5 → D-20,
   sample-set append to PD-31) — each currently carried as an explicit dev default, which is the
   m1 report's own sanctioned alternative.
3. Nine open cross-page conflicts `[X-1]`–`[X-9]` await owner adjudication; this spec's positions
   are recorded with reversal impact and none blocks this page.
4. Cosmetic: BR-28's rationale still *contains* the `[PD-19]` token (as a disclaimer), so a
   mechanical PD-citation count includes it; the semantic misattribution m1 flagged is gone.
