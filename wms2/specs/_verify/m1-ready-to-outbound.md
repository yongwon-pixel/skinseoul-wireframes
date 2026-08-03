# M1 — Coverage Audit · `ready-to-outbound.md`

**Method:** Verification Method 1 (independent coverage audit). Auditor did not write the spec.
**Date:** 2026-08-03
**Target:** `wms2/specs/ready-to-outbound.md` (1813 lines, v1.1)
**Wireframe (SST):** `wms2/ready-to-outbound/index.html` (486 lines)
**References:** `_global-rules.md` · `_plans/_review.md` (§3 binding) · `_plans/_provisional-decisions.md` · `_plans/_wireframe-fixes.md` · `_plans/ready-to-outbound.A.md` · `_plans/ready-to-outbound.B.md`

All counts below were **derived by the auditor** with scripted extraction over the HTML and the markdown. No count asserted by the spec was accepted on trust; every one was recomputed.

---

## 1. PASS / FAIL table

| # | Check | Verdict | Derived evidence |
|---|---|---|---|
| 1 | **Legend coverage** | **PASS** | HTML: `class="dot"` occurrences = **15** (`1`–`14` + `M1`); legend `<ol><li>` = **14**; `.n` order = `1 2 3 4 5 6 7 8 14 13 12 9 10 11`; one off-screen normative `<p>` footnote below the `<ol>`. Spec §2.1 declares 15 legend units + 8 furniture units = 23; §3 contains exactly 23 subsections (§3.1–§3.23). Every dot maps to a `[L-n]`/`[L-M1]` subsection; the footnote's 8 rules map to `[L-F1]`, `[L-F7]`, [BR-2], [BR-6], [BR-10], [BR-12], [BR-14]. **No unit is specified nowhere.** |
| 2 | **Plan coverage** | **PASS** | A-plan DC-1…DC-18: all 18 present in §5.1 with preserved semantics and IDs. A-plan BR-1…BR-14: all 14 present in §4 at the same numbers. A-plan Q1–Q5 → PD-35/PD-34/PD-36/PD-35/PD-39; A-plan D1–D7 → §9.3 D-1/D-2/D-3/D-4/D-5/D-6/D-17. B-plan E-1…E-30: all 30 present in §7 (spec expands to 80, `E-1`…`E-79` + `E-15b`, **no gaps**). B-plan OQ-B1…OQ-B6 all adjudicated and named in §9's preamble. B-plan dev-decision list: all 10 items land in §9.3. **Nothing silently dropped.** |
| 3 | **QA integrity** | **FAIL** | Counts recomputed exactly: **201** scenarios (134 prose + 67 table), **93 `[WF]` / 108 `[ADMIN]`**, **97 negative = 48.3 %** — every per-block figure in §8.0 matches to the unit, no duplicate IDs, no numbering gaps in any block. DC coverage: **28/28** DC ids have a QA-DC row asserting persistence (1:1). `[L-*]` keys used in §8: all 23 exist; **0** phantom keys. NE: 12 defined, 12 used. **Single failure:** `[E-49]` (§7.2, line 864) is referenced by **no** scenario in §8, while §8.19 claims "Every `[E-n]` edge case is referenced by ≥1 scenario" (all other 79 are covered). |
| 4 | **PD discipline** | **FAIL** | 30 distinct PD ids cited, 154 tagged occurrences; all 30 exist in the register. Spot-checked 14 (see §3 below) — 12 match exactly, 1 mis-tagged, 1 meaning mismatch. `[PD-71]` is **NO-DEFAULT** in the register but is written `[PD-71 · OWNER-PENDING]` twice (lines 792, 1680) — contradicting the spec's own §9.2 statement that only PD-51 and PD-55 are NO-DEFAULT entries naming this page. `[PD-16]` is cited to justify a behavior its register entry does not decide. PD-51 and PD-55 are correctly tagged `· NO-DEFAULT` and no behavior rests on them. |
| 5 | **Convention compliance** (`_review.md` §3) | **FAIL** | Keys: single-state page → plain `[L-n]`, `[L-M1]`, `[L-Fn]` ✓ (conv. 1). ID continuity: BR 1–37 + `BR-9b`, no gaps, no renumbering; DC 1–28 contiguous; E 1–79 + `E-15b` contiguous ✓ (conv. 2). Canonical cross-page event names byte-identical (`comment.posted`, `comment.mention_notified`, `comment.starred`/`unstarred`, `comment.read`/`mark_all_read`, `order.status_changed`, `order.outbounded`, `print.job_result`) ✓ (conv. 3). QA tiers `[WF]`/`[ADMIN]` only — 201/201 matched, no stray tier ✓ (conv. 4). Slack notation with channel ID on **first** mention (line 676) ✓ (conv. 6). Korean strings verbatim — all 5 product names + `07-21 09:40` byte-match the HTML ✓ (conv. 9). Removals as explicit "must NOT exist" §4.2 ✓ (conv. 10). Reversal chains §10.1 ✓ (conv. 11). **Failure:** conv. 7 (`YYYY-MM-DD` everywhere, "no `07-23` shorthand") violated at lines 1759, 1771, 1813. |
| 6 | **Global-rule hygiene** | **PASS** | 17 distinct `[G-n]` citations, 124 occurrences; **0** cited-but-undefined; only G-11 uncited (correctly — inbound lifecycle does not touch this page). All three real deviations are declared as page deltas with rationale **and** date: G-2 no-refresh exception ([BR-8], 2026-07-09 / 07-22 / 08-03), G-2 "every confirming action toasts" narrowed to an enumerated table ([BR-34] + §4.1, 2026-08-03, with adjudication C-6 cited), G-1 declared N/A ([BR-25], 2026-08-03). §6.4's three print surfaces match GD-9's RTO registry exactly. Minor body-restatement noise flagged as D-8 below, not treated as a deviation. |
| 7 | **Adjudication compliance** | **PASS** | Every `_review.md` C-item touching this page is honored with a §10 Decision Log row: **C-1** → §4.2 no Carrier field/column + `[PD-9]`; **C-2** → §6.1 `#fulfillment-admin-comments` (`C0BMGEWM5QA`), never "pending"; **C-3** → §1.4 `OTHER (channel)` `[PD-80]`; **C-5** → [BR-11] `[PD-2]`; **C-6** → [BR-34] + `[RTO-WFX-6]`/`[RTO-WFX-7]`; **C-7** → §3.19 + §6.2 `[PD-21]`; **C-8** → [BR-21] + WF-9 `[PD-36]`; **C-9** → [BR-9]/[BR-9b] `[PD-34]`; **C-12** → canonical event names verified byte-identical. C-4, C-10, C-11 are other pages. **No stale wireframe text is specified as truth:** WF-9 (the only `_wireframe-fixes.md` item for this page) is carried in §2.4 as a defect and §3.15 specifies the *correct* behavior; the `Outbonded` spelling non-fix (§E of the register) is honored at §3.16; the "does not lock bulk buttons / does not recompute counts" demo limitations are listed in §2.4 as `[ADMIN]`, not filed as bugs. |

**Independent wireframe cross-checks that PASSED** (spot-verified against the HTML, since the spec quotes ~40 byte-exact strings): all 36 sampled UI strings present in both HTML and spec; `sndOutbound.ac` assignment and the sound-binding predicate `/Outbound/ && !/Cancel/ && !/Outbounded/` exist as described; synth parameters (sine 340→940 Hz over 0.16 s, triangle 1250 Hz at +0.14 s, stop +0.36 s) match the JS exactly; `.tbl tbody tr[data-view]:not(.crow)` = 5; `#crow4` is the JIT panel and `#crow5` the MKT panel; `.wf-tab` has **no** CSS rule; `.cb-ready` **is** defined and **unused**; `.picktbl td.num` has no rule; `.oid` is a `<span>` with no `href`; `.pagepad{padding:16px 14px 0}`; `.toast{top:54px;right:16px}`; search seeds produce exactly 4 hits for `422`, 1 for `Aldo`, 5 for `4`, 0 for `zzzz`. All nine `[RTO-WFX-n]` defect claims are **true**.

---

## 2. Defect list

### D-1 · MAJOR — The "reconciliation invariant" is provably false for the page's own normal case

**Location:** §3.13 `[L-13]`, line 446 — "**Reconciliation invariant (QA-assertable).** `Σ(Total Items of selected rows)` **must equal** the `{items}` figure in the `[L-2]` button label **and** the `{units}` figure in the M1 header." Asserted again as unconditional at **QA-L13-04** (line 1479, "in every case") and **QA-L13-05** (line 1485).

**Why it is wrong:** the same spec states three mutually incompatible things.
- §3.1.6 + [BR-16] + `[PD-37]`: `{items}` and `Total Items` count **all** units of the order, including non-inbounded ones.
- §3.15 line 490: "Only **pickable** lines appear: lines that are not inbounded have no location and are **excluded** from the picking list."
- **E-13** (line 843) and **QA-E-13** (line 1587): for an order with 2 inbounded + 1 non-inbounded line, `Total Items` = 3 while "the picking list contains 2 rows for it".

The M1 header's `{units}` is the picking-list unit total (wireframe: 4 rows, 5+1+1+1 = `8 units total`). Therefore whenever a selection contains a partially-inbounded order — which [BR-3] makes a **routine** state, since MKT orders are always listed regardless of inbound status — `Σ(Total Items)` > `{units}`, and the invariant fails. The wireframe only appears to satisfy it because its default selection excludes `MKT-40233`.

**Consequence:** QA-L13-04 will fail against a correct implementation, and a developer implementing §3.13 literally must put non-inbounded units into the picking-list total, sending pickers after goods that are not in the building.

**Fix:** rewrite §3.13's invariant as two statements — (a) `Σ(Total Items of selected rows) == {items}` in `[L-2]` **always**; (b) `{units}` in the M1 header equals `Σ(qty of pickable lines only)` and equals `{items}` **only when every selected order is fully inbounded**, differing otherwise by exactly the non-inbounded unit count. Rewrite QA-L13-04 to assert (a) unconditionally and (b) conditionally, and add the divergence to QA-E-13's Then-clause.

---

### D-2 · MAJOR — One hard-coded exclusion subtext is used for five different exclusion reasons, and QA asserts the misleading copy

**Location:** §3.4 step 6 (line 272), §3.6 (line 314), [DC-21] (line 695), E-53 (line 865), **QA-L4-08** (line 1202), **QA-L6-08** (line 1287).

**The defect:** the only exclusion copy defined is `{n} excluded — items not inbounded`. But §3.4.4 and [DC-21] define **five** exclusion reasons: `lines_not_inbounded`, `status_forbids_outbound`, `already_outbounded`, `left_ready_pool`, `empty_order`. QA-L4-08 makes the mismatch explicit and normative:

> "**Given** a selection containing `MKT-40233` (one line not inbounded), **one on-hold order**, and two fully-inbounded orders … **Then** … the toast reads `✓ Bulk Outbound complete — 2 orders` with subtext `2 excluded — items not inbounded`"

The on-hold order's items **were** inbounded (E-33 line 850: "A Hold order carries inbounded lines and therefore appears in the pool"). The operator is told a false reason for the exclusion of the one order they can actually act on, and will look for a receiving problem instead of releasing a hold.

**Secondary gap in the same defect:** §3.3 (line 235) and **QA-L3-07** (line 1162) both promise that a no-carrier order "is reported in the toast subtext" for Bulk Print Labels, but no Bulk Print Labels subtext string is defined anywhere in §3.6 or §4.1 — the subtext slot is specified only for the default sentence and the Bulk Outbound exclusion.

**Fix:** replace the single string with a reason-aware contract — either a neutral head plus a breakdown (`{n} excluded — {a} items not inbounded · {b} status blocks outbound · {c} already shipped …`) or one string per `exclusion_reason` enum value; add the corresponding string for the Bulk Print Labels `no_carrier` exclusion; update §4.1, [DC-21], E-53, QA-L4-08, QA-L4-10, QA-L6-08 and QA-L3-07 to the new copy.

---

### D-3 · MINOR — A NO-DEFAULT PD is presented with the OWNER-PENDING tag

**Location:** §6.3 line 792 — "its column mapping is an open question owned by the closing spec `[PD-71 · OWNER-PENDING]`"; §9.1 line 1680 — "`closing.md` (`[PD-71 · OWNER-PENDING]` owns the sheet mapping)".

**Why it matters:** `_provisional-decisions.md` line 390 marks PD-71 **NO-DEFAULT** ("Not decided"). Per `_review.md` §3 convention 8, `[PD-n · OWNER-PENDING]` means *a provisional behavior was adopted and written as normal behavior* — the exact opposite. The spec contradicts itself: §9.2 line 1694 states "Only two NO-DEFAULT register entries name this page" and lists PD-51 and PD-55.

**Fix:** change both occurrences to `[PD-71 · NO-DEFAULT]`.

---

### D-4 · MINOR — `[E-49]` is defined but referenced by no QA scenario, while §8.19 claims full E coverage

**Location:** `[E-49]` defined at §7.2 line 864 ("First user gesture of the session is the Bulk Outbound click itself"); coverage claim at §8.19 line 1661 ("Every `[E-n]` edge case is referenced by ≥1 scenario").

**Derived:** of the 80 edge cases (`E-1`…`E-79` + `E-15b`), 79 appear somewhere in §8; `E-49` appears only at lines 256, 820 and 1721 — all outside §8.

**Fix:** add `[E-49]` to the key list of **QA-E-02** (which already stubs `AudioContext` to throw) or to **QA-L4-01** (which already asserts `sndOutbound.ac` is constructed inside the click gesture); otherwise strike the §8.19 claim.

---

### D-5 · MINOR — `[PD-16]` is cited for a behavior its register entry does not decide

**Location:** §6.1 line 748 — "**Self-mention.** When the author @mentions themselves the Slack notification is suppressed, consistent with the no-self-notification principle established for match confirmation `[PD-16 · OWNER-PENDING]`."

**Mismatch:** register PD-16 (line 94) decides *"Does an on-the-spot M2 match in View Orders also fire the 'match confirmed' auto-comment + Slack? — Yes, same auto-comment and route; the @mention is suppressed when resolver == registrant."* Its scope line reads `Pages: VO (Q3), TM, OD` — **not RTO**, and its subject is the system auto-comment, not an operator's free-text comment. The spec generalises it into a new rule (suppress Slack on operator self-mention) and tags that new rule with a PD number that does not cover it.

**Fix:** either raise a new PD ("does an operator self-mention notify Slack?") and tag the sentence with it, or drop the behavior from §6.1 and record the question in §9.3 as a developer decision constrained by [BR-30].

---

### D-6 · MINOR — Shorthand dates violate `_review.md` §3 convention 7

**Location (3 lines, §10):**
- line 1759 — "Superseded the **07-13** RTO draft entirely"
- line 1771 — "Not this page — recorded because it is the same **07-22** decision batch"
- line 1813 — "redrawn from the live admin capture on **2026-07-21/22**. No behavior from the **07-13** draft survives."

Convention 7 is explicit: "`YYYY-MM-DD` everywhere (Decision Logs, BR rationale, conflict citations). No `07-23` shorthand in final specs." (The `07-21 09:40` string at line 1347 is a verbatim wireframe `<time>` value = data, and is **not** a violation.)

**Fix:** expand to `2026-07-13`, `2026-07-22`, and `2026-07-21 / 2026-07-22`.

---

### D-7 · MINOR — Mandatory item #11 (JIT residual stock) is coded `n` for this page but never stated

**Location:** absent from §9.1 (lines 1675–1691) and from the whole document — `grep -i residual` returns zero hits.

**Why it matters:** `_review.md` §2b codes item 11 as `n` for RTO, and defines `n` as "**explicit N/A (stated in spec, not silent)**", concluding "every N/A cell is an explicit statement". Items 1, 6, 7, 9 and 10 are indeed stated explicitly ([BR-25]/§1.4; §6.1 non-routes; §9.1 inbound-flows row; §9.1 stock-status row). Item 11 is the only silent one, so the review's own 0-holes result is not actually satisfied by this spec.

**Fix:** add one §9.1 row — "**JIT residual stock** (stock left over from cancelled JIT orders) | `stock-status.md`. This page shows only orders that are ready to ship; residual stock never surfaces here."

---

### D-8 · MINOR — Global-rule bodies restated instead of cited (convention 5)

**Locations:**
- §6.5 line 820 — "Web Audio synthesis only, no external audio files [G-3]" restates G-3(a)'s parenthetical "(Web Audio, no external files)".
- §1.5 line 60 and [BR-26] line 617 — "v1 ships a single admin role: no role gating … every mutating action records the actor" is G-15's body nearly verbatim.
- [BR-10] line 601 — "outputs the correct carrier's label **instantly on click**" restates G-4's opening sentence before reaching the actual delta.

Convention 5: "cite `[G-n]` and write page **deltas only** — never restate the rule body."

**Fix:** trim each to the delta and let the citation carry the body — e.g. §6.5 → "The send sound fires on `[L-4]` at click time [G-3a]; no TTS and no warning tone on this page [G-3b] [G-3c]."

---

### D-9 · MINOR — The M1 header's `{skus}` figure is never defined, and E-14 creates the case where the two readings diverge

**Location:** §3.15 line 481 — "`Print Pick Locations — Picking List ({orders} orders selected · {skus} SKUs · {units} units total)`", with no definition of `{skus}` anywhere in §3.15, §3.13 or §4.

**Why it matters:** [BR-19] / **E-14** state that the same SKU in two selected orders produces **two** rows. `{skus}` is therefore ambiguous between *distinct SKUs* (1) and *picking-list rows* (2). QA-M1-01 asserts `4 SKUs` from the wireframe, where the two readings happen to coincide (4 rows, 4 distinct SKUs), so the ambiguity is untested.

**Fix:** add one line to §3.15 — "`{skus}` is the count of **distinct SKUs** across the selection, which is ≤ the number of table rows when the same SKU appears in two orders [E-14]" (or the row-count reading, whichever the owner wants) — and add the divergent case to QA-M1-07's Then-clause.

---

### D-10 · MINOR — The §4.2 carrier removal row is unscoped and appears to forbid a concept the spec depends on

**Location:** §4.2 line 656 — "| **Carrier column / automatic carrier recording** | Any Carrier field or column on this page. Automatic carrier recording is **not supported** anywhere in WMS 2.0 (adjudication C-1, `[PD-9 · OWNER-PENDING]`) |".

**Why it matters:** adjudication C-1 concerns the **inbound** carrier captured at scan time on View Orders / Inbound Request. This page nevertheless resolves an **outbound** carrier per order ([BR-10], §6.4 delta 1), stores it on [DC-7], and defines a "no carrier assigned" refusal path ([E-61], [DC-28]). A reader taking §4.2 at face value would delete the very field §3.3 requires.

**Fix:** scope the row — "Any **inbound** Carrier field or column on this page; automatic capture of the *receiving* carrier is not supported anywhere in WMS 2.0 (adjudication C-1). The order's **shipping** carrier is a separate field, resolved per order for label printing [BR-10]."

---

### D-11 · MINOR — `[NE-2]`'s coverage-map entry points at a scenario that does not assert it

**Location:** §8.19 line 1663 — "`[NE-2]` QA-L5-02".

**QA-L5-02** (line 1233) asserts only that `#pfill.style.width` samples start at `0%`, never decrease, and end at `100%`. It makes no claim about progress ticks **not** being persisted, which is what `[NE-2]` declares. Every other NE mapping in that row is sound (`NE-1`→QA-DC-18, `NE-3`→QA-DC-17, `NE-4`→QA-M1-12, `NE-9`→QA-E-02, `NE-12`→QA-L1-08).

**Fix:** add an `[ADMIN]` negative rider to QA-L5-02 — "**· negative:** no per-tick event exists in the audit stream for the run; only [DC-8]'s start and finish `[NE-2]`" — or remove `[NE-2]` from the coverage map.

---

### D-12 · MINOR — QA-E-04's `th` assertion uses an unqualified selector that resolves to 14, not 9

**Location:** §8.17 line 1578 — "**QA-E-04** … narrowing the window produces horizontal scrolling and **the 9 `th` cells remain 9**."

**Derived:** the document contains **14** `<th>` elements — 9 in `.tbl` and 5 in `#m-pick .picktbl` (`Location`, `SKU`, `Product`, `Qty`, `Order`). An agent running `document.querySelectorAll('th').length` gets 14 and files a false failure. QA-F-05 (line 1541) gets this right with `.tbl thead th`.

**Fix:** change to "`.tbl thead th` remains 9".

---

## 3. PD spot-check (14 checked, 12 exact)

| PD | Register meaning | Spec usage | Verdict |
|---|---|---|---|
| PD-1 | Single admin role, no gating, actor recorded | §1.5, [BR-26], E-27, QA-E-19 | match |
| PD-2 | Send sound on every outbound-class button, every page | §1.2, §3.4.1, [BR-11] | match |
| PD-3 | Comments append-only, corrections are new comments | §3.9, [BR-27], [DC-1] | match |
| PD-4 | Notification failure never blocks or rolls back | §6.1, [BR-30], E-16 | match |
| PD-6 | Server revalidates at confirm, no partial writes | [BR-28], E-7, E-44, QA-M1-15 | match |
| PD-7 | Optimistic version check → 409 → non-green toast | [BR-29], E-8, [DC-23] | match |
| PD-16 | Mention suppressed when **resolver == registrant** on a match-confirm auto-comment; pages VO/TM/OD | §6.1 uses it for operator **self-mention** on any comment, on RTO | **mismatch → D-5** |
| PD-18 | Shelf persists while open, auto-clears on Outbound (old→new) | §3.4.5, [DC-9], QA-L4-12 | match |
| PD-26 | Cancel Outbound exists on OD, rolls back `prepare shipment → processing` | [BR-22] | match |
| PD-33 | System-user picker, no auto Slack notification | §3.8 "PIC resolves to a system user" | match |
| PD-35 | Non-inbounded lines auto-excluded + subtext; JIT eligible | §3.4.4, [BR-15], E-3/E-4/E-21 | match (copy defect = D-2) |
| PD-37 | All units of the order, MKT-40233 = 3 precedent | §3.13, [BR-16], QA-L13-02 | match |
| PD-59 | MKT/regular merge blocked | §3.8, E-59 | match |
| PD-71 | **NO-DEFAULT** — Daily Shipping Status mapping not decided | tagged `· OWNER-PENDING` twice | **mis-tagged → D-3** |

---

## 4. Severity roll-up

| Severity | Count | IDs |
|---|---|---|
| BLOCKER | 0 | — |
| MAJOR | 2 | D-1, D-2 |
| MINOR | 10 | D-3 … D-12 |

**Overall:** the spec is unusually well-verified against its own sources — legend coverage is complete, every plan item survives, and all 201 QA scenarios, both tier splits, the negative share, and the DC 1:1 mapping reproduce exactly under independent recomputation. The two MAJOR defects are internal contradictions in *derived* numbers and *operator-facing copy*, both fixable inside one section each; the ten MINOR defects are tagging, coverage-claim and convention hygiene.
