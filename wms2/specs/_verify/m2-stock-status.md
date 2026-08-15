# M2 — Adversarial QA Execution: `stock-status.md` §8

**Target spec:** `wms2/specs/stock-status.md` v1.1 (2026-08-03), §8 *QA Acceptance Criteria (machine-runnable)*
**System under test:** `wms2/stock-status/index.html` (byte-identical to the deployed page)
**Runner:** `wms2/specs/_verify/qa-stock-status.py` (Playwright, headless Chromium, Python 3.13) — re-runnable
**Raw output:** `wms2/specs/_verify/qa-stock-status-results.json`
**Date:** 2026-08-03 · Executed as a hostile QA robot with no authorship of the spec.

---

## 1. Methodology

1. **Scenario extraction.** §8 declares *"Totals: 194 scenarios — 73 [WF] · 121 [ADMIN]"*. I enumerated every `[WF]`-tagged row independently and got **exactly 73**, distributed NAV 8 · CS 9 · LOC 3 · AUD 14 · LOG 7 · RES 6 · HIS 9 · FRM 5 · COM 7 · EXP 1 · GLB 4. The declared per-block totals (NAV 10 · CS 18 · LOC 18 · AUD 43 · LOG 9 · RES 26 · HIS 18 · FRM 19 · COM 15 · EXP 6 · GLB 12) sum to 194 and reconcile. **The spec's own arithmetic is correct** — that is not a common outcome and is worth recording.
2. **Sample.** The brief asked for ≥25 adversarially chosen scenarios. I ran **all 73**, so the sample cannot be accused of cherry-picking; the weighting requirement (negatives, toasts, modal chains, cross-state flows, exact strings) is satisfied by construction — 17 of the 73 are `NEGATIVE`-tagged and 41 assert an exact string.
3. **Execution discipline.** Only selectors, labels and expected strings that §8 itself supplies were used. Where §8 did not say what to click or what to observe, the scenario was recorded **AMBIGUOUS** rather than improvised from my own reading of the page.
4. **Preflight.** §8.0 steps 1–5 applied verbatim before **every** scenario: load → wait for `#p-current.on` → click `#annoToggle` → assert `body.no-anno` + button reads `Show annotations` → reload between scenarios.
5. **String-match convention (a tie I had to break).** §8 distinguishes *"reads **exactly** X"* from *"reads X"*. I read the former as strict equality and the latter as containment/prefix. §8.0 never states this convention. It is applied consistently and every place it changed a verdict is called out in the evidence column.
6. **Verdicts.** PASS · FAIL (spec says X, page does Y) · AMBIGUOUS (instructions insufficient) · UNRUNNABLE (impossible in a static mock and not tagged `[ADMIN]`).
7. **Culprit rule.** A FAIL is charged to the wireframe only if `_plans/_wireframe-fixes.md` already knows about it. That file's only stock-status entry is **`[WF-14]`** (two modals lack legend dots — explicitly optional, no behaviour change) and §E's non-fix *"stock-status legend starts at 5"*. Neither is touched by any FAIL below, so **no FAIL is chargeable to the wireframe**.

---

## 2. Results

**66 PASS · 4 FAIL · 3 AMBIGUOUS · 0 UNRUNNABLE** (73 attempted, 100 % of the `[WF]` tier).

### 2.1 Failures and ambiguities (full evidence)

| ID | Verdict | Evidence |
|---|---|---|
| **QA-RES-02** | **FAIL** | Spec: header reads `Reserved Quantity — Dongkook 마데카솔 크림 50ml (100004819) · 8 reserved`. §8.0 step 3 **mandates `innerText`**. Actual `innerText` of the **open** modal header: `'Reserved Quantity —\nDongkook\n마데카솔 크림 50ml (100004819) · 8 reserved\n✕'`. `.modal header` is `display:flex`, so `innerText` inserts a line break around the `<b>Dongkook</b>` flex item **and** appends the `✕` close button. strict-equality = false, **substring containment = false**, whitespace-normalised containment = true. The bold-check and table-header legs both passed. |
| **QA-RES-05** | **FAIL** | Identical root cause. Spec: `Cancel Inbound — Order 409112 · Dongkook 마데카솔 크림 × 3`; actual `innerText` = `'Cancel Inbound — Order 409112 ·\nDongkook\n마데카솔 크림 × 3\n✕'`. strict = false, substring = false, normalised = true. **Every other leg of this scenario passed**: the four bold numbered steps, both `input[name=resback]` radios with `Yes — Available +3 (restock)` checked, Restock Qty `3` + hint, memo placeholder — all byte-exact. |
| **QA-LOC-08** | **FAIL** | Legs 1–2 pass (`100024743` renders `input.bcin` placeholder `Enter barcode`; `100031877` renders plain `8809738317481`). Leg 3 fails: spec says *"Exactly one `.bcin` exists in the table"*; `document.querySelectorAll('#p-current table .bcin').length === 2`. The second is `#auSearch` — the `[L-13]` unregistered-product search box — which carries `class="bcin"` and lives inside `tr.audrow`, i.e. **inside the same `<table>`**. The count is 2 in audit mode and out of it, since `display:none` does not remove the node. |
| **QA-COM-05** | **FAIL** | Spec: *"the pane renders **exactly** `No matching comments`"*. Actual pane `innerText` = `'0 results · newest first · click to open the order\nNo matching comments'` — the search pane also renders the results header above the empty state (`cSearch()` always emits `.paneheader` then either hits or `.empty`). Lenient reading (assert on the `.empty` node alone) passes. The second leg — clearing the query restores `.tabs` and the previously active pane — passed. |
| **QA-LOG-09** | **AMBIGUOUS** | Assertable half passes: three **distinct** `Total Loss` colours (`rgb(180,83,9)` / `rgb(220,53,69)` / `rgb(25,135,84)`) and the `2026-05-31` cell ends ` · target met`. Unassertable half: the spec names the colours `amber` / `red` / `green` and supplies **no hex, rgb, CSS variable or class** to compare against, so "this cell is amber" cannot be decided from the spec — only by reading the wireframe's CSS, which is improvisation. |
| **QA-GLB-08** | **AMBIGUOUS** | 2 of 3 clauses ran and passed (0 nodes with a scan/feed id or class; 0 occurrences of `scan` in any pane or overlay `innerText` ⇒ no scan-feed list, no scan counter). Clause 3 — *"no input that re-focuses itself after a commit"* — names no input, no commit gesture and no observable for "re-focus". A plain `<input>` legitimately retains focus after `Enter`, so any probe invented here would produce a false positive or a false negative at the tester's whim. |
| **QA-GLB-09** | **AMBIGUOUS** | Proxy test passes (0 Korean strings in `th` / `label` / `.paneheader` / `.form-note` / `button` / `h2` / `h4`; the Korean present sits in product-name cells plus the data string `— (신규)`). But the scenario asks whether each Korean string is *"product-, brand-, or data-derived"* and §8 **never enumerates the 11 KR product names**, so the partition had to be invented. The stated baseline *"the shipped wireframe's only non-product Korean is `신규`"* is likewise unverifiable without that list. |

### 2.2 Passes (66)

| Block | IDs | Note |
|---|---|---|
| QA-NAV | 01, 02, 03, 04, 06, 07, 08, 09 | 8/8. NAV-03 confirms the 2026-08-03 `stopImmediatePropagation` behaviour (wf-bar modal shortcut leaves `#p-current.on` intact). NAV-06/08 baselines verified: **0** occurrences of `print`, `sample`, `photo`, `upload`, `procurement hub`; `RETURN-BIN` appears only inside `.legend`, which preflight step 2 hides. |
| QA-CS | 01, 03, 05, 08, 09, 10, 14, 15, 16 | 9/9. CS-01 SKU + Available census exact; CS-14 header `innerText` exact with the three `th.audcol` at `display:none`; CS-08 all 11 route cells `rgba(0,0,0,0)` / `font-weight:800`; CS-16 zero drill-down affordances in the Reserved column. |
| QA-LOC | 01, 18 | 2/3 (08 failed). LOC-01 all eleven `.loc-in` values exact including the empty one. |
| QA-AUD | 01, 02, 03, 04, 06, 11, 12, 13, 14, 16, 17, 22, 23, 36 | 14/14. AUD-01 walking-path sort exact incl. `100038120` last; AUD-04 fixture census 9 equal / 2 seeded; AUD-14 wireframe no-op + `activeElement === #auSearch`; AUD-16 full inserted-row contract; AUD-23 second note byte-equal; AUD-36 audit + added row survive a wf-bar modal round-trip. |
| QA-LOG | 01, 02, 03, 04, 05, 06 | 6/7 (09 ambiguous). LOG-05 confirmed: the `2026-05-31` Detail anchor has **no** `data-modal` and opens nothing. |
| QA-RES | 01, 03, 04, 06 | 4/6 (02, 05 failed). RES-04 and RES-06 notes byte-equal; RES-03 phantom row isolation exact. |
| QA-HIS | 01, 03, 04, 05, 06, 07, 08, 15, 18 | 9/9. HIS-07 confirmed: the PENDING row carries zero `button` / `a` / `checkbox`. |
| QA-FRM | 01, 02, 03, 08, 19 | 5/5. Both `.form-note` strings byte-equal; no `Location` field on either form; exactly one enabled, non-readonly Carrier `<select>` per form. |
| QA-COM | 01, 02, 03, 04, 12, 14 | 6/7 (05 failed). COM-14 confirms HTML escaping (`<b>x</b>` produces zero `<b>` nodes). |
| QA-EXP | 01 | 1/1. |
| QA-GLB | 11, 12 | 2/4 (08, 09 ambiguous). GLB-11 money census: `+₩15,000 · +₩46,260 · +₩61,260 · ₩0 · −₩128,460 · −₩15,000 · −₩17,800 · −₩28,400 · −₩36,000 · −₩61,260`; `/\$|USD/` matches nothing. |

### 2.3 Where I had to break a tie to reach PASS

These passed, but only because I chose a reading the spec does not state. Each is a latent inter-tester disagreement.

| ID | Tie broken |
|---|---|
| QA-LOG-01 / 03 / 04, QA-AUD-22 | Modal headers were matched by **prefix**, not equality — `innerText` appends `'\n✕'` from the close button that lives inside `<header>`. Under strict equality all four would FAIL alongside QA-RES-02/05. |
| QA-COM-02 | *"its pane header reads `Saved comments · Click to open the order`"* — the node also carries `<small>Unstar to remove from this list</small>`. Matched by prefix per the *reads* vs *reads exactly* convention. |
| QA-COM-04 | *"exactly one `.it` renders"* — hidden tab panes keep their `.it` nodes in the DOM. Counted `offsetParent !== null`; the spec gives no visibility definition. |
| QA-AUD-22 | Spec writes `18 → 17`, but `#m-adjust` has **separate** `System` and `Counted` columns. Read as values, not as a literal cell string. |
| QA-LOC-18 | *"types `A-02-14`"* into a field pre-filled `A-02-13`. Executed as replace; literal append yields `A-02-13A-02-14` and fails. |
| QA-NAV-07 | *"no `Audit Log` tab exists **anywhere**"* — scoped to `.subtabs button` + `.wf-tab`. Unscoped, the page does contain the string via `📋 Past Audit Logs` and `Modal: Past Audit Logs`. |
| QA-GLB-11 | The `Loss (₩)` column header contains a bare `₩`. Treated as a currency **label**, not a money **value**; the spec does not draw that line. |
| QA-AUD-16, QA-LOG-03, QA-RES-03, QA-HIS-06, QA-CS-01, QA-AUD-06 | Colour words (`purple-tinted`, `amber row background`, `red outline`, `rendered green`) with no values. Verified structurally (only-row-with-a-background, only-button-with-a-border) rather than by colour. |

---

## 3. Culprit split for the 4 FAILs

| Culprit | Count | IDs |
|---|---|---|
| (a) **Spec wrong** | **4** | QA-RES-02, QA-RES-05, QA-LOC-08, QA-COM-05 |
| (b) Wireframe wrong (known defect in `_wireframe-fixes.md`) | 0 | — |
| (c) Test-instruction defect on my side | 0 | — |

Justification for charging all four to the spec:

- **QA-RES-02 / QA-RES-05.** The wireframe renders correctly; `.modal header{display:flex}` exists so the `✕` right-aligns. Nothing in `_wireframe-fixes.md` calls it a defect. The failure is entirely a **QA-methodology defect in §8.0**: it mandates `innerText` (rightly, to defeat the annotation dots described in §2.4) but never accounts for `innerText`'s layout sensitivity, and then hands the tester single-line header strings that `innerText` provably cannot return.
- **QA-LOC-08.** The spec asserts a *fact about the shipped wireframe* — "exactly one `.bcin` in the table" — that is false. Whether the wireframe *should* reuse `bcin` for `#auSearch` is a separate question; as a QA assertion the sentence is simply wrong about the SUT and no fix list covers it.
- **QA-COM-05.** The spec's "exactly" is over-tight for a pane that, by the wireframe's own always-on results header, renders two nodes.

---

## 4. Spec fixes required

Ordered by damage.

1. **[P0] §8.0 — add a text-normalisation rule for `innerText`, and re-state the six modal headers.**
   §8.0 step 3 correctly forces `innerText` (annotation dots) but stops there. Add a step 3b:
   > *Normalise whitespace before comparing (`s.replace(/\s+/g,' ').trim()`), and strip a trailing `✕` — the close button is a child of `<header>` and `.modal header` is a flex container, so `innerText` inserts line breaks around inline `<b>` runs and appends the button label.*
   Without this, **QA-RES-02 and QA-RES-05 are unpassable by any reading**, and QA-LOG-01/03/04 + QA-AUD-22 are unpassable under strict equality. Six of 73 `[WF]` scenarios (8 %) hinge on one unstated rule. This is the single highest-yield fix in the document.

2. **[P0] QA-LOC-08 — delete or rewrite the third clause.**
   Replace *"Exactly one `.bcin` exists in the table"* with either *"exactly one `.bcin` exists among the eleven data rows (`tbody tr:not(.audrow)`)"* or *"exactly two `.bcin` exist in the table — the SKU `100024743` barcode input and the `[L-13]` `#auSearch` box, which shares the class"*. As written it is false against the SUT. §3.8 and §3.9 should also record that the wireframe reuses `class="bcin"` for `#auSearch`, otherwise a developer will treat `.bcin` as a barcode-only selector.

3. **[P1] QA-COM-05 — scope the "exactly" to the empty-state node.**
   Rewrite as *"…the result pane's `.empty` node reads exactly `No matching comments`, above it the header `0 results · newest first · click to open the order`."* Also worth asserting explicitly, since it is currently untested, that the pluralisation is `1 results` (QA-COM-04 already locks that in — the wireframe never says `1 result`).

4. **[P1] §8.0 — state the *reads* vs *reads exactly* convention.**
   The document already uses both forms deliberately (QA-COM-02 vs QA-COM-04). Say so in §8.0, otherwise two AI testers will disagree on ~15 scenarios. Add the DOM-visibility definition at the same time (*"'renders' means `offsetParent !== null`"*) — QA-COM-04's "exactly one `.it`" needs it.

5. **[P1] QA-AUD-23 / QA-AUD-22 / QA-LOG-02 — the fixture is internally contradictory and the spec canonises it.**
   QA-AUD-22 asserts `#m-adjust` has exactly **one** `[NEW]` row (`100048201`); QA-LOG-02 asserts the `2026-07-22` session has `New Additions = 1`; QA-AUD-23 asserts the note reads *"the **3 new additions** are not losses"*. All three pass, because the wireframe string really does say "3". The number is wrong in both spec and wireframe. Fix the wireframe note to *"the 1 new addition is not a loss"* (this belongs in `_wireframe-fixes.md`, which currently has no such entry) and update QA-AUD-23's expected string in lockstep.

6. **[P2] Colour assertions need values.** QA-LOG-09 is the worst case (three cells identified only as amber/red/green), but QA-RES-03, QA-HIS-06, QA-AUD-16, QA-LOG-03, QA-AUD-06 and QA-CS-01 share it. Either give the CSS custom-property names (`--amber` / `--red` / `--green` / `--ss-purple-50`) or the computed rgb triples, or restate the assertion structurally (*"exactly one row carries a non-default background"*).

7. **[P2] QA-GLB-08 clause 3 is not machine-runnable.** *"no input that re-focuses itself after a commit"* needs a named input, a named gesture and an observable, e.g. *"focus `.bcin`, type digits, press Enter; assert `document.activeElement` is not that input and is not another `.bcin`."* Otherwise drop the clause to `[ADMIN]`.

8. **[P2] QA-GLB-09 needs the KR product-name allow-list.** Enumerate the 11 Current Stocks KR names + the 5 `[L-13]` catalogue names (they already exist verbatim in §3.9 and QA-AUD-12) and state the test as *"every Hangul run on the page is a member of this set, or the string `신규`."*

9. **[P3] QA-NAV-07** — scope *"no `Audit Log` tab exists anywhere"* to `.subtabs` + `.wf-tab`; the page legitimately renders `Past Audit Logs`.

10. **[P3] QA-LOC-18** — say *"clears the field and types"* / *"sets the value to"*, not *"types"*, since the field is pre-filled.

11. **[P3] QA-AUD-22** — write `System 18 · Counted 17` rather than `18 → 17`; `#m-adjust` has separate columns (the `→` form belongs to `[L-M2]`, where it is a single cell).

12. **[P3] QA-GLB-11** — exclude the `Loss (₩)` column header from the money-value scan, or say *"every `₩` followed by a digit"*.

13. **[P3] Document defect, not a scenario defect.** §8 line 995 is a **blank line inside the QA-AUD table**, between `QA-AUD-40` and `QA-AUD-41`. Every Markdown renderer will terminate the table there and re-open a second, header-less one for AUD-41/42/43. Delete the blank line.

---

## 5. Verdict — can an AI run this spec's QA unaided?

**Yes, with caveats.**

The document is far above the norm for machine-runnability: 73 of 73 `[WF]` scenarios were locatable, launchable and — apart from one unstated normalisation rule — decidable. The preflight is real and load-bearing (§2.4's annotation-dot warning is genuinely necessary; without step 2 the header assertions in QA-CS-14 and QA-LOC-01 would fail spuriously, exactly as the spec predicts). Scenario counts reconcile. The `[WF]` / `[ADMIN]` tiering is honest — nothing tagged `[WF]` turned out to require a server, so **UNRUNNABLE = 0**, and the "Wireframe demo limitations" paragraph correctly pre-empted every inert-control trap. Fixture censuses (SKU order, Available values, sizes, locations, count prefills, event rows, session rows) are exact to the character.

The caveats are narrow and mechanical, not conceptual:

- One missing sentence (`innerText` whitespace normalisation) accounts for **half the failures** and would silently split two testers on six more scenarios.
- One assertion (QA-LOC-08) states a false fact about the page.
- Colour words without values, and two prose-only negatives (GLB-08 clause 3, GLB-09), are the only places where the agent must invent a test rather than execute one.

Fix items 1–4 and an unattended agent reaches 71/73 deterministic verdicts with no judgement calls; fix 1–8 and it reaches 73/73.
