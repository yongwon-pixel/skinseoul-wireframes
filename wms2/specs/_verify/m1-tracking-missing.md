# M1 — Coverage Audit: `tracking-missing.md`

**Method:** independent verification. Every count below was re-derived from the source files with scripted extraction over `wms2/tracking-missing/index.html` and `wms2/specs/tracking-missing.md`; no number asserted by the spec was accepted on trust.
**Auditor:** verification agent (did not author the spec). **Date:** 2026-08-03.
**Artifacts audited:** spec 1377 lines / 179 KB · wireframe 410 lines · `_global-rules.md` v1.0 · `_review.md` (§3 conventions binding) · `_provisional-decisions.md` · `_wireframe-fixes.md` · `_plans/tracking-missing.A.md` · `_plans/tracking-missing.B.md`.

---

## Verdict table

| # | Check | Verdict | Independently derived evidence |
|---|---|---|---|
| 1 | Legend coverage | **PASS** | HTML contains exactly **7** `.dot` elements (`0,1,2,3,4,5,M1`), **6** legend `<li>`, **2** normative `<p>` after the `<ol>`. Spec §2.1 declares 7 legend + 6 non-legend = **13** units; §3.1–§3.13 specify exactly those 13 (`L-0…L-5, L-M1, L-M2, L-F1…L-F3, L-S1-Fa, L-S1-Fb`). §8.17 maps all 13 to scenarios. Zero units specified nowhere. |
| 2 | Plan coverage | **PASS** | A-plan events **E1–E18** all land (E1→DC-1, E2→DC-3, E3→DC-5, E4→DC-6, E5→DC-4, E6→DC-8, E7→DC-9, E8→DC-10, E9→DC-11, E10→DC-14, E11→DC-17, E12→DC-20, E13→DC-11, E14→DC-22, E15→DC-21, E16→DC-12, E17→DC-13, E18→DC-15). B-plan edge cases **E-1…E-31** are preserved **at their original numbers with matching semantics** (verified case by case). A-OQ1–5 → PD-60/61/62/63/64; B-Q1–Q7 → PD-60/65/62/64/66/1/67; all 11 A-dev + 6 B-dev items land in §9.2 D-1…D-13. Nothing dropped silently. |
| 3 | QA integrity | **FAIL** | Counts are **exactly** as claimed (re-derived: 151 scenarios; 67 `[WF]` / 84 `[ADMIN]`; per-block 12·12·12·12·10·11·13·8·13·11·6·8·12·5·6 = 151; negatives 48 = **31.8 %** ≥ 25 %; zero duplicate IDs; all 13 `[L-*]` keys used in §8 exist; all 28 `[DC-n]` referenced by ≥1 `[ADMIN]` Then-clause). **But: 16 of 72 `[E-n]` are referenced by zero scenarios**, there is no E→QA coverage map, one `[WF]` scenario asserts behavior the wireframe cannot exhibit, and two §8.16 map rows overclaim. See D-2, D-3, D-4. |
| 4 | PD discipline | **PASS** (2 minor exceptions) | 22 distinct PDs cited; **all 22 exist in the register** (`PD-1,2,3,4,5,6,7,8,16,22,51,60,61,62,63,64,65,66,67,68,80,85`) — zero phantom IDs. Spot-checked ≥8 against register text: **PD-1, PD-3, PD-4, PD-6, PD-8, PD-16, PD-60, PD-62, PD-64, PD-65, PD-66, PD-67** — all 12 match in meaning. NO-DEFAULT `PD-66` is correctly left unspecified (§9.1, `[E-3]`, QA-VAL-10 `BLOCKED`); no NO-DEFAULT PD is presented as decided. Every behavior-bearing citation carries `· OWNER-PENDING`; the only untagged occurrences sit in §9.1 (the question itself), §9.3 (one pointer, D-8) and §10 under an explicitly declared notation. |
| 5 | Convention compliance | **PASS** | Key formats per `_review` §3.1: plain `[L-{n}]` on this single-state page, `[L-M{n}]` modals, `[L-F{n}]` furniture, `[L-S1-F{a\|b}]` footers (justified in §2.1). ID continuity re-derived: **BR-1…44, DC-1…28, E-1…72, N-1…12 — zero gaps, zero duplicates, zero renumbering** (B-plan E-numbers preserved). Dates are `YYYY-MM-DD` throughout; the only `MM-DD` strings are byte-quoted wireframe data (`07-13 10:12`), which §3.9 of the conventions permits. Slack notation correct: `#fulfillment-admin-comments` (`C0BMGEWM5QA`) on first mention (§1.3); `#unrecognized-tracking` has no published ID and the spec says so rather than writing "pending". Korean strings verbatim. Removed features carry explicit "must NOT exist" entries (§3.12 table + §9.4). QA tier tags are `[WF]`/`[ADMIN]` only. |
| 6 | Global-rule hygiene | **FAIL** | All 15 `[G-n]` cited resolve to `_global-rules.md`; zero phantom citations. **But** the reading contract's claim "this document never restates a global rule body" is falsified by BR-15, BR-23, BR-27 and BR-34, and — more seriously — the page carries an **undeclared deviation from `[G-5]`**: the pool cell renders route labels in `.mut` gray non-bold while `[G-5]` and BR-15 require colorless **bold black** text, with no page-delta declaration or date. BR-44 also narrows `[G-2]`'s scope page-locally without a corresponding global delta. See D-1, D-6, D-7. |
| 7 | Adjudication compliance | **PASS** | `_review` C-6 honored (✕ gets confirm + mandatory reason + toast → `[BR-9]`, `[L-M2]`, `[PD-60]`, decision-log row cites C-6). C-2 honored (channel + ID, never "pending"). C-3 honored (`[BR-15]`, OTHER via PD-80). C-12 honored: the shared events are byte-identical (`comment.posted`, `comment.mention_notified`, `comment.starred`/`unstarred`, `comment.read`/`mark_all_read`, `comment.auto_posted` with `source=system`) and §5.3 declares the four canonical events this page does **not** emit. The adjudicated non-issue (Closing "unknown order" ≠ this pool) is stated explicitly in both directions (`[BR-32]`, QA-XPG-05). No stale wireframe text is specced as truth: WF-6 and WF-10 are specced as *gaps* with correct behavior stated, §2.4 lists 9 demo limitations, §8.15 asserts the current quirks as `[WF]` so QA cannot false-fail, and three new defects (WF-NEW-A/B/C) are filed. |

**Wireframe facts independently verified against the HTML** (each was asserted by the spec and each is true): 7 `.dot`; 6 legend `<li>`; 2 footer `<p>`; **0** `<a>` elements (WF-NEW-B); **0** `<input>` elements (QA-LOAD-09); 12 `<th>` in the exact order quoted; `.toast.err` defined but unused; Order-No dash is **U+2013**, modal header dash is **U+2014**, remove glyph is **U+2715** — all three match the spec's byte-level claims.

---

## Defect list

### D-1 — BLOCKER · `[L-2]` route-label rendering is self-contradictory, and one side is an undeclared `[G-5]` deviation

**Location:** §3.3 `[L-2]`, spec lines 250–260 (the "Rendering, per candidate, exact format" block vs. the "Route label rendering" paragraph); propagated into §8.3 as **QA-SUS-02** (line 934) and **QA-SUS-05** (line 941), and into `[BR-15]` (line 539).

§3.3 specifies the same element twice, incompatibly:

> `{PIC in <b>} · {"Order " + order_no, blue …} · {route (channel), .mut} · {status, .mut}`

> **Route label rendering.** Route + channel is colorless bold black text `[G-5]` …

`.mut` is `color:var(--ink-3)` → `rgb(126,124,131)`, non-bold. `[G-5]`/`[BR-15]` require `--ink` → `rgb(20,16,27)`, bold. The wireframe renders the pool-cell route inside `<span class="mut">JIT (Naver) · Processing</span>`, i.e. gray and non-bold; only the M1 modal uses the neutralized `.tag-jit`.

The contradiction is encoded as two mutually exclusive `[WF]` assertions in one block:
- **QA-SUS-02** asserts "the trailing `JIT (Naver) · Processing` in the `.mut` gray";
- **QA-SUS-05 (neg)** asserts "Given **any** route/channel label **on the page** … its colour resolves to the ink colour `rgb(20, 16, 27)`".

Both cannot pass. QA-SUS-05 will FAIL on the live wireframe today, and a developer has no way to resolve which rendering is normative.

**Fix required:** decide one rendering and make §3.3, `[BR-15]` and §8.3 agree.
(a) If `[G-5]` governs the pool cell: change the format line to `{route (channel), bold, --ink}`, file a new wireframe defect against the `.mut` span in all three pool rows, and re-tag QA-SUS-02's colour clause `[ADMIN]` with a `[WF]` counterpart in §8.15.
(b) If the gray `.mut` rendering is intended: declare it in §3.3 and `[BR-15]` as an explicit page delta on `[G-5]` with rationale and date ("the candidate line is a compound sentence, not a badge — 2026-08-03"), and rescope QA-SUS-05 to route labels rendered with `.tag-*` classes (M1 only), which is what QA-M1-10 already covers correctly.

### D-2 — MAJOR · **QA-NEG-03** is tagged `[WF]` but asserts idempotency the wireframe cannot exhibit — guaranteed false FAIL

**Location:** §8.9, line 1082. Quoted: *"**QA-NEG-03 [WF] (neg)** — Given the baseline, When I dispatch two `click` events on the same `.xdel` within 200 ms, Then exactly one row is removed And both counters decrement by exactly 1 `[G-9]`."*

The wireframe handler (`index.html` lines 400–404) is:

```js
document.querySelectorAll('.xdel').forEach(b=>b.addEventListener('click',e=>{
  e.stopPropagation(); b.closest('tr').remove(); poolDec(); }));
```

There is no debounce. On the second dispatch, `b.closest('tr')` still resolves (the button is a descendant of the now-detached `<tr>`), `.remove()` is a silent no-op, and **`poolDec()` runs a second time**: counters go `3 → 2 → 1` while **2** rows remain rendered. The scenario's Then-clause is false, and it simultaneously violates the count invariant `[BR-33]` that QA-LOAD-05 asserts. This is exactly the class of false failure §8.15 exists to prevent, and §2.4 does not list it among the 9 demo limitations (§2.4.7 covers only the `finishMatch()` guard, not `.xdel`).

**Fix required:** re-tag **QA-NEG-03 as `[ADMIN]`**; add the counterpart `[WF]` quirk to §8.15 (e.g. QA-WFQ-07: "two dispatches on the same `.xdel` remove one row but decrement the counters twice — §2.4.x") and add the matching demo-limitation bullet to §2.4. Note that QA-NEG-01 is safe as `[WF]` only because `finishMatch()` happens to guard on `#poolrow1` existence — that asymmetry should be stated.

### D-3 — MAJOR · 16 of 72 `[E-n]` are referenced by zero QA scenarios, and no E→QA coverage map exists

**Location:** §7 (all 72 cases) vs. §8; §8.16 and §8.17 provide DC→QA and legend→QA maps but there is **no** E→QA map.

Re-derived: §8 references 56 distinct `[E-n]`. Unreferenced in any form (searched for both `[E-n]` and bare `E-n`):

`E-4, E-14, E-22, E-26, E-29, E-30, E-31, E-33, E-36, E-44, E-45, E-58, E-59, E-64, E-65, E-69`

Only **E-4** is defensibly excluded (§7.1 states the negative test lives in the View Orders spec). The remaining 15 carry real regression risk and several are directly testable today:

- `[E-44]` (missing KR name renders `–`, never falls back to English) and `[E-45]`/`[E-64]` (long memo/name wrapping, never truncated) are `[WF]`-adjacent rendering rules with no assertion;
- `[E-26]` (comment/Slack failure **after** the line write must not roll back the match) is the single most dangerous behavior on the page and has no scenario — QA-NEG-13 only covers dead-lettering `[E-61]`;
- `[E-58]` (`no-store` so Back cannot resurrect a resolved row — the stated default for D-13), `[E-59]` (two-tab convergence), `[E-36]` (removal dialog cancelled → zero side effects), `[E-29]` (any operator may match and remove), `[E-30]` (>20 rows: no pagination, no search), `[E-31]` (pool-entity comment click target), `[E-33]` (unrequested-inbound matched to a customer order — memo must never be truncated), `[E-14]`, `[E-65]`, `[E-69]` all have specified behavior and no acceptance criterion.

**Fix required:** add an **§8.18 Edge-case → QA coverage map** on the model of §8.16, and add the missing scenarios (≈10–15, mostly `[ADMIN]`) so every `[E-n]` except the explicitly cross-referenced `[E-4]` has ≥1 Then-clause. Where a case is deliberately untestable on this page, say so in the map row rather than leaving it absent.

### D-4 — MINOR · §8.16 DC→QA map overclaims two rows

**Location:** §8.16, the `DC-10` and `DC-13` rows (lines 1220 and 1223).

The map credits `DC-10 | … QA-NEG-02` and `DC-13 | … QA-VAL-05`, but neither scenario cites the ID it is credited with: QA-NEG-02 (line 1076) asserts comment/Slack uniqueness and cites only `[DC-12]`; QA-VAL-05 (line 1114) asserts `item_not_open` and cites only `[E-43]`, `[BR-33]`. Both events remain covered elsewhere (DC-10 by QA-MATCH-06/10, DC-13 by seven others), so this is a map-accuracy defect, not a coverage hole — but the map is the artifact a reviewer trusts.

**Fix required:** either add the `[DC-10]` / `[DC-13]` citations to the two scenario bodies, or drop those two entries from the map rows.

### D-5 — MINOR · `[BR-19]` / `[E-11]` / QA-VAL-04 extend `[PD-8]` beyond the register's text while tagging it as decided

**Location:** `[BR-19]` (line 543), `[E-11]` (§7.2), §3.4.3 step 1, QA-VAL-03/04 (§8.10).

`[PD-8]` decides: *"An **inbound** tracking number is unique system-wide; registering one that already exists on another **inbound request** is blocked. Inbound … and outbound … are separate namespaces and may coincide."* The spec extends this to *"a tracking number may not be bound to two **order lines** within one namespace"* and tags it `[PD-8 · OWNER-PENDING]`, presenting an unadopted extension as register-backed. Compounding it, the spec never classifies which namespace a **pool item's** number belongs to — yet the same pool deliberately holds supplier parcels (`[BR-11]`), whose numbers are inbound. Under QA-VAL-04 the uniqueness guard is therefore switched off in precisely the scenario `[E-33]` warns about (an unrequested-inbound parcel matched to a customer order).

**Fix required:** state in `[BR-19]` that order-line uniqueness is a page-level extension of `[PD-8]` (or raise it as its own PD), and add one sentence to `[L-1]` column 1 defining the namespace a pool item's tracking number is treated as belonging to, with the `[E-33]` interaction named.

### D-6 — MINOR · Global-rule bodies are restated despite the reading contract's claim

**Location:** reading contract item 1 (line 8) vs. `[BR-15]` (line 539), `[BR-23]` (line 547), `[BR-27]` (line 551), `[BR-34]` (line 558).

`_review` §3.5 requires citation plus page deltas only. `[BR-23]` restates `[G-9]`'s mechanism ("client debounce **and** a server idempotency key"); `[BR-27]` restates `[G-7]`/`[PD-3]`'s append-only body; `[BR-15]` restates `[G-5]`'s "colorless black bold text, never coloured pills"; `[BR-34]` restates `[G-2]`'s no-refresh body. Each does add a genuine page delta (key semantics, memo immutability, `OTHER` form, "not the RTO exception"), so the fix is trimming, not deletion.

**Fix required:** reduce each to its delta — e.g. `[BR-23]` → "Idempotency keys `[G-9]`: match = `pool_item_id + line_id`; removal = `pool_item_id + "remove"`. Suppressed duplicates are logged `[DC-12]`/`[DC-16]`." — or amend the reading contract to say "restates a rule body only where the page narrows or extends it, always with the delta named".

### D-7 — MINOR · `[BR-44]` narrows `[G-2]`'s scope page-locally without a global-rules delta

**Location:** `[BR-44]` (line 568), `[E-57]` (§7.5), QA-FURN-07 (§8.8).

`[G-2]` reads "No full-page refresh after any action. **Sole designed exception:** RTO Bulk Outbound." `[BR-44]` reinterprets it as prohibiting only *programmatic* refresh, so a user-initiated F5 is permitted. The reasoning is sound and QA needs it, but the reading applies identically to all eight pages; settling it inside one page spec is how eight specs diverge. `_review` §4 is the mechanism for exactly this (`GD-1…GD-10`).

**Fix required:** raise it as a global delta (`GD-11`: "`[G-2]` prohibits programmatic post-action refresh; a user-initiated reload is outside its scope") and reduce `[BR-44]` to a citation.

### D-8 — MINOR · `[PD-51]` is cited untagged and is absent from §9.1's PD inventory

**Location:** §9.3, sample-assignment row (line 1298); §9.1 carried/cross-referenced lists (line 1267).

`[PD-51]` (a **NO-DEFAULT** register entry owned by order-management / RTO / order-detail) is cited bare as `` `[PD-51]` `` while `[PD-85]` in the same table carries `· OWNER-PENDING`. It also appears in neither of §9.1's two lists ("carried by this page" / "cross-referenced only"), so the spec's own PD inventory is incomplete by one.

**Fix required:** tag it `[PD-51 · OWNER-PENDING]` for consistency with `[PD-85]`, and add it to §9.1's "cross-referenced only" list alongside PD-2/PD-22/PD-68/PD-85.

### D-9 — MINOR · **QA-XPG-05** is tagged `[WF]` but executes against a different page's wireframe

**Location:** §8.12, line 1149. §8.0 defines `[WF]` as *"executable today against the live wireframe at `…/wms2/tracking-missing/`"*; QA-XPG-05 opens `…/wms2/closing/` instead.

**Fix required:** either widen the `[WF]` definition in §8.0 to "any published wireframe in this set, named in the scenario", or introduce a `[WF-XPG]` marker. The scenario itself is correct and should be kept.

### D-10 — MINOR · §8.0's totals sentence implies QA-VAL-10 sits outside the 151

**Location:** §8.0, line 874: *"Totals: 151 scenarios — 67 [WF], 84 [ADMIN]. Negative scenarios: 48 (31.8 %) … **One further scenario (QA-VAL-10)** is `BLOCKED`…"*

Re-derived, QA-VAL-10 is inside the 151 (VAL block = 11 including it) and inside the 84 `[ADMIN]`. "One further" reads as an addition and invites a downstream reader to reconcile 152.

**Fix required:** reword to "**Of these, one** (QA-VAL-10) is `BLOCKED` and carries no verdict."

---

## Summary

| Severity | Count | IDs |
|---|---|---|
| BLOCKER | 1 | D-1 |
| MAJOR | 2 | D-2, D-3 |
| MINOR | 7 | D-4, D-5, D-6, D-7, D-8, D-9, D-10 |

Checks 1, 2, 4, 5, 7 pass. Check 3 fails on edge-case→QA coverage and one mis-tagged scenario (all counts, tier splits and the negative-test floor are otherwise exactly as claimed). Check 6 fails on an undeclared `[G-5]` deviation plus rule-body restatement.

The spec is unusually strong on the two dimensions that are normally weakest — data-capture completeness (28 events, 12 declared non-events, all mapped to `[ADMIN]` assertions) and byte-level fidelity to the wireframe (every dash codepoint, colour, selector and count re-verified true). The blocker is a single unreconciled rendering decision that leaked into two contradictory QA rows; everything else is trimming.
