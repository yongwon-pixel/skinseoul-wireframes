# M1 — Coverage Audit · `order-management.md`

Method: independent coverage audit (Verification Method 1). The auditor did **not** write the spec. Every count below was derived by direct extraction (Python/grep) over `wms2/order-management/index.html` and `wms2/specs/order-management.md`; no count asserted by the spec was trusted before it was re-derived.

Target: `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/order-management.md` (1781 lines, spec v1.1, 2026-08-03)
Wireframe (SST): `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/order-management/index.html` (435 lines)
Date: 2026-08-03

---

## Verdict table

| # | Check | Verdict | Evidence (derived, not quoted from the spec) |
|---|---|---|---|
| 1 | **Legend coverage** | **PASS** | HTML yields 9 unique units: legend `<li>` = 5 (`1,2,3,4,5`), `.dot` elements = 9 (`5,1,2,2,4,M2,M3,M1,M1b`) — dot `2` rendered twice, legend `3` dotless, so unique units = 9. Off-screen normative blocks in the legend: **1** (`.legend > p`). Overlay modals: 3 (`m-sampleon`, `m-sampleoff`, `m-import`). §2 declares 9 units → 10 spec keys + 6 furniture keys = 16 §3-addressable units; §3 carries exactly 16 `### 3.x [L-…]` headings (`1, M1, M1b, 2a, 2b, M2, M3, 3, 4, 5, F1…F6`). Every unit — including the legend closing paragraph (`[L-F1]`, §3.11) and the dotless removed item (`[L-3]`, §3.8) — is specified. **0 units specified nowhere.** |
| 2 | **Plan coverage** | **PASS** | A-plan §3a data-capture list (18 event types incl. the explicit NON-captured clause) → all 18 land as `[DC-1]`…`[DC-29]` + §5.4; nothing dropped. A-plan legend inventory (9 units + gtoast + no-refresh + chrome exclusion) → all present. A-plan BR-1…BR-11 → spec BR-1…BR-11 with matching meanings. A-plan OQ-1…OQ-5 → PD-51/52/53/54/55; OQ-D1…OQ-D5 → §6.2 + §9.3. B-plan edge list **E-1…E-45** → all 45 present in §7 with their original meanings and no renumbering (E-22 split with the new E-82 boundary partner, both retained). B-plan Q-O1…Q-O6 → PD-52/56/57/58/59/55; Q-D1…Q-D6 → §9.3 rows. **0 silent drops.** |
| 3 | **QA integrity** | **FAIL** | Counts re-derived and **exact**: 153 scenarios, 77 `[WF]` / 76 `[ADMIN]`, per block IMP 52 · SMP 43 · LST 17 · CMT 23 · GBL 18, negatives 64 = **41.83 %** (floor 25 %). No duplicate or gapped QA ids in any block. Every `[DC-1]`…`[DC-29]` is named in ≥1 scenario body and in §8.6; every `[L-*]` used in §8 exists in §3; no tag outside `[WF]`/`[ADMIN]`. **But 20 of the 100 `[E-n]` ids are referenced by zero QA scenario** (D1), and 3 §8.6 matrix cells cite scenarios that never name the event (D4). |
| 4 | **PD discipline** | **PASS** | 26 distinct PDs cited. All PD-backed behaviours carry `[PD-n · OWNER-PENDING]`; the only 4 untagged citations are defensible (`PD-51`, `PD-55` = NO-DEFAULT, correctly presented as *undecided* in §3.3, §3.6.4 and §9.1; `PD-2` cited as the *reason no sound applies*; `PD-9` cited as not-applicable in §10). Spot-checked ≥8 against the register — **PD-1** (single admin role → BR-22), **PD-3** (append-only comments → BR-23), **PD-4** (Slack side-effect → BR-24), **PD-5** (destructive confirm → §3.7.5/BR-25), **PD-6** (confirm-time revalidation → §3.2.5 step 2/BR-26), **PD-52** (not retroactive → BR-15), **PD-53** (selected = immediate → BR-16), **PD-56** (sales orders only → BR-17), **PD-57** (block whole file → BR-12), **PD-58** (warn + `Import anyway` → BR-13), **PD-59** (merge blocked → BR-18), **PD-36/PD-27** (dual-view → BR-8) — all meanings match. Three PDs applied beyond their register page list (PD-5, PD-6, PD-63) are declared with reversal impact in §9.1. No NO-DEFAULT PD is presented as decided. One discipline gap noted as D6. |
| 5 | **Convention compliance** (`_review` §3) | **PASS** | Key format `[L-{n}]` on a single-state page ✓, `[L-M{n}]` + sub-dot `[L-M1b]` ✓, `[L-2a]`/`[L-2b]` exactly as `_review` §2c.2 rules ✓, unnumbered furniture `[L-F{n}]` ✓ (with the `[L-{state}-F]` non-use argued in §2.1 against `_review` §2a, which records no off-screen block for this page — verified: the 6 off-screen blocks belong to VO/IR/CL). ID continuity: E-1…E-100 contiguous, no duplicates, no renumbering; DC-1…DC-29 (DC-29 appended, not renumbered); BR-1…BR-34 contiguous. Dates: **0** `MM-DD` shorthand tokens outside full `YYYY-MM-DD` (regex-verified). Slack notation: `#fulfillment-admin-comments` (`C0BMGEWM5QA`) with ID on first mention (line 456) and every mention; the other three channels have no ID in `_slack-routing`, and §6.2 says so explicitly. Korean: none on this page, declared in §2.2 (so `[G-6]`'s verbatim clause has nothing to violate). Removed features present as explicit "must NOT exist" entries: Bulk Hold (§3.8), plus 9 further negative contracts in §3.8.1. QA tags `[WF]`/`[ADMIN]` only. One deviation noted as D3. |
| 6 | **Global-rule hygiene** | **PASS** | All 15 `[G-n]` rules are cited (111 citations); §6.6 is an explicit applicability grid closing the mandatory-inclusion audit for every rule, including the six declared **No** (`G-1`, `G-3`, `G-4`, `G-10`, `G-11`, `G-14`) with a page reason. An 11-word shingle diff against `_global-rules.md` finds **one** genuine body restatement cluster (the `[G-7]` mention-target sentence) — D5. No behaviour on this page deviates from a G-rule; the two places the spec goes *beyond* the wireframe (M2 toast, M3 confirm) are `[G-2]` + `_review` C-6 applications, dated 2026-08-03, with rationale. |
| 7 | **Adjudication compliance** | **PASS** | C-* items touching this page all honoured: **C-2** (channel confirmed, cites `_slack-routing` 2026-08-03, never "pending") · **C-3** (`OTHER (channel)` reaches this page only via the unchanged table, `[PD-80 · OWNER-PENDING]`, §6.6) · **C-5** (send sound defined by button class → this page has none, BR-28/§6.6/QA-GBL-13) · **C-6** (G-2 beats wireframe omissions → §3.6.5 toast + §3.7.5 confirm) · **C-8** (G-13 picking artifacts, `[PD-36]`, BR-8/§6.5) · **C-12** (canonical event names, §5 header). Adjudicated non-issue "order-management legend 3 has no on-screen dot" is honoured as an intentional artifact (§2.2) and kept as a negative entry. **No WF-1…WF-14 entry names this page** (independently verified against `_wireframe-fixes`), and §2.4 says so; no stale wireframe text is specced as truth — the 7 newly-found artifacts are labelled `[WF-15 · proposed]`…`[WF-21 · proposed]`, kept out of the register, and each is documented by a defect-documentation QA scenario. Spot-verified in the HTML: WF-15 (`colspan="6"` at line 334 vs 7 `<th>` at line 329) ✓, WF-16 (`Start Assignment (ON)` has no `id`, no handler) ✓, WF-17 (`#sampCancelBtn` unconditional) ✓, WF-18 (`#gtoast` + `#gtoast2`) ✓, WF-19 (`forever` checked, end inputs enabled) ✓, WF-20 (no `keydown` anywhere) ✓, WF-21 (`stopPropagation` guards with no document-level closer) ✓. |

**Summary: 6 PASS · 1 FAIL (check 3).**

---

## Defect list

### 1. MAJOR — 20 of 100 edge cases have no QA scenario

**Location:** §7 (all four sub-tables) vs §8.1–§8.5.
**Evidence:** extracting every `E-n` token from `## 8. QA Acceptance Criteria` … `## 9.` yields 80 distinct ids. The following 20 defined edge cases appear **nowhere** in §8:

`E-4` (unknown SKU) · `E-6` (invalid country code) · `E-8` (every row unconnected) · `E-9` (within-file duplicate rows) · `E-16` (row/byte limit) · `E-17` (template schema mismatch) · `E-26` (period ends while an assigned order is unshipped) · `E-31` (order cancelled/refunded after a sample was assigned) · `E-34` (dual-view divergence) · `E-42` (no write access) · `E-44` (network failure mid `Start Assignment (ON)`) · `E-50` (Slack channel archived/renamed) · `E-55` (tab closed mid-upload) · `E-58` (export during a commit) · `E-60` (period ends while `[L-M3]` is open) · `E-65` (carrier mapping changes between preview and confirm) · `E-66` (period cancelled in the same second as an order creation) · `E-78` (over-length recipient/address) · `E-79` (contact without dialling code) · `E-86` (selection above the batch ceiling).

Several are load-bearing behaviour, not dev trivia: **E-34 is the `[G-13]` dual-view divergence check on the page that §6.6 declares the "primary home" for `[G-13]`**; **E-4 and E-6 are two of the five blocking validation rules** behind BR-12; **E-65 and E-66 are the two race conditions** the spec invents (advisory-vs-authoritative carrier resolution, cancel-vs-create ordering); **E-44** is the sample-side twin of E-12, which *is* covered.

**Fix required:** add at least one Given/When/Then scenario per uncovered id — `[ADMIN]` for E-4, E-6, E-8, E-16, E-17, E-26, E-31, E-44, E-50, E-55, E-58, E-60, E-65, E-66, E-78, E-79, E-86; `[WF]` is not possible for any of them. E-34 must be an `[ADMIN]` cross-reference scenario asserting the carrier-facing/internal split, since this spec is G-13's primary home. For the genuinely unassertable ones (E-9, E-42, both pure `§9.3` dev decisions), add an explicit line to §8.0 naming them as intentionally unasserted with the reason, so the gap is declared rather than silent — the same discipline §2.2 already applies to numbering gaps.

---

### 2. MINOR — 7 edge cases are referenced nowhere outside their own §7 row

**Location:** §7.1 (`E-4`, `E-6`), §7.2 (`E-55`, `E-78`, `E-79`), §7.3 (`E-31`, `E-34`).
**Evidence:** `grep -n "\[E-n\]"` returns exactly one hit each — the §7 table row itself. They are not cited from the §3 clause they constrain, nor from §4, nor from §8. Every other E-id is cited from at least one of §3/§4/§6/§8.
**Fix required:** cite each from the clause it qualifies — `E-4`/`E-6` from §3.2.4 "Row errors" and §3.2.5 gate 2; `E-31` from §3.6.6; `E-34` from §3.6.5 / §6.5 (BR-8); `E-55` from §3.2.6; `E-78`/`E-79` from §3.2.4's parse contract. (Fixing D1 will incidentally clear most of these, but the §3 back-reference is the part that makes the rule findable from the behaviour.)

---

### 3. MINOR — 42 of 153 QA scenarios have no `When` clause

**Location:** §8.1–§8.5.
**Evidence:** scanning each scenario block for `^(And )?(Given|When|Then)` shows 42 blocks with `Given` + `Then` only: `QA-IMP-22, -23, -24, -25, -26, -29, -40, -41, -42, -43, -44, -45, -46, -49, -51, -52` · `QA-SMP-07, -08, -21, -24, -25, -27, -35, -36, -38, -40, -41, -42` · `QA-LST-08, -14, -15, -16` · `QA-CMT-11, -12, -13, -14, -23` · `QA-GBL-06, -07, -08, -17, -18`.
Example, `QA-CMT-11`: *"Given a comment `@Yongwon please check` is posted on order `MKT-40233` / Then `[DC-19] comment.posted` persists…"* — the action ("a comment is posted") is folded into the Given, so the scenario is still unambiguous, but `_review` §3.4 binds authors to **Given/When/Then**.
**Fix required:** split the action out of the Given into a `When` for each of the 42 (e.g. QA-CMT-11 → *Given I am viewing order `MKT-40233` / When I post the comment `@Yongwon please check` / Then …*). No behavioural change; this is a form fix so the block is uniformly machine-parsable.

---

### 4. MINOR — three §8.6 matrix cells over-claim

**Location:** §8.6, rows `DC-9`, `DC-10`, `DC-14`.
**Evidence:** cross-checking every matrix pair against the cited scenario's body, three cited scenarios never name the event they are credited with:
- `DC-9 | QA-IMP-27, QA-IMP-33` — QA-IMP-33 asserts *"12 new purple `MKT-` rows are present"*, a UI read, with no `[DC-9]` clause.
- `DC-10 | QA-IMP-27, QA-IMP-52` — QA-IMP-52 asserts *"each order carries its own row's carrier"*, with no `[DC-10]` clause.
- `DC-14 | QA-SMP-10, QA-SMP-12, QA-SMP-13, QA-SMP-43` — **QA-SMP-13 asserts the *absence* of an assignment** (*"none receives a sample set"*), which is the opposite of an asserting Then-clause for `DC-14`.

No `[DC-n]` is left uncovered — each of the three has another citation that does name the event — so the section heading's promise still holds, but the matrix is the artifact a QA lead will trust.
**Fix required:** delete the three cells, or add the explicit `[DC-n]` Then-clause to QA-IMP-33, QA-IMP-52 and QA-SMP-13; if QA-SMP-13 is kept under DC-14, mark it `(absence)` the way `DC-25 | QA-LST-09 (absence)` already is.

---

### 5. MINOR — `[G-7]`'s rule body is restated verbatim in the normative text

**Location:** §6.1, Slack routing table, "Mention target" column: *"the message body `@mentions` the tagged person, so Slack raises a personal notification while the channel doubles as a team-visible archive"* — and again in §10, row `2026-08-03 | Comment @mention channel confirmed`.
**Evidence:** an 11-word shingle diff against `_global-rules.md` returns this sentence as the only genuine restatement cluster (`_global-rules` G-7: *"the message body @mentions the person, so Slack raises a personal notification while the channel doubles as a team-visible archive"*). `_review` §3.5 and the spec's own header line ("page deltas only — rule bodies are never restated in this document") forbid it. `_review` §3.6's "payload fields verbatim" licence covers the payload column, not this one.
**Fix required:** replace the cell with `per [G-7]` (the channel + ID + payload columns already carry everything this page needs). The §10 row may keep a short paraphrase as a decision record, but drop the verbatim clause. (§10's `[G-2]` and `[G-15]` rows also paraphrase their bodies; those are decision-log entries required by `_review` §3.11 and are acceptable as-is.)

---

### 6. MINOR — three spec-invented normative rules bypass the PD register

**Location:** §4, `BR-31`, `BR-33`, `BR-34` (added in v1.1 per §10's last row).
**Evidence:** all three are dated `2026-08-03` and written as decided behaviour, but none appears in `_provisional-decisions.md`, none carries `[PD-n · OWNER-PENDING]`, and none is listed in §9.1. Only the *value* behind BR-31 reaches §9.3 ("the concrete operating-timezone value") — the policy itself (*"No per-user timezone rendering in v1"*) is asserted as settled. BR-31 has company-wide consequence by the spec's own rationale (*"a sample period is a company-wide switch"*), and BR-33 changes which orders get sampled (open-time vs submit-time set resolution).
**Fix required:** register BR-31, BR-33 and BR-34 as PDs in `_provisional-decisions.md` §F and tag their sentences `[PD-n · OWNER-PENDING]`, with the same reversal-impact note §9.1 already gives for PD-5/PD-6/PD-63. Alternatively, list them in §9.1 as spec-level defaults awaiting owner sign-off. As written, an owner reviewing §9.1 will never see them.

---

### 7. MINOR — `QA-IMP-19` points at a scenario id instead of the artifact, and carries a dead token

**Location:** §8.1, QA-IMP-19, Then clause: *"the only occurrence of `stock` is inside the QA-IMP-18 note where it appears in the phrase `regardless of stock or inbound status`"*.
**Evidence:** there is no "QA-IMP-18 note" — the artifact is `.note.mkt` (§3.2.7), which QA-IMP-18 happens to assert. An executor following §8.0's "executable without asking a question" contract has to reverse-resolve a scenario id to a selector. Separately, the same When clause searches `#m-import` for the Korean substring `재고`, while §2.2 declares that no Korean string exists anywhere on this page — the token can never match and contradicts the spec's own declaration.
**Fix required:** change the Then clause to *"…is inside `.note.mkt` (§3.2.7), in the phrase `regardless of stock or inbound status`"*, and drop `재고` from the search list (or move it to an `[ADMIN]` scenario if the real admin can render Korean error copy).

---

### 8. MINOR — `QA-LST-12` asserts nav labels that the DOM does not produce as written

**Location:** §8.1–§8.5 harness rule 5 (*"Text assertions are byte-exact"*) applied to §8.3, QA-LST-12: *"the quick links `Agent Telemetry`, `Role Assets`, `Shared Asset Health`, `SkinSeoul WP Admin`"*.
**Evidence:** the wireframe renders these as `<span class="navlink">Agent<br>Telemetry</span>` (index.html line 166), so `textContent` is `AgentTelemetry`, `RoleAssets`, `SharedAssetHealth`, `SkinSeoulWP Admin`. A byte-exact `[WF]` assertion on the quoted strings fails. Every other `[WF]` literal in §8 was machine-checked against the wireframe and resolves correctly (including the runtime-generated comment-search headers — `MKT` → `3 results`, `421` → `2 results`, `Harshit` → `2 results`, `4` → `5 results`, all independently recomputed from `CSEARCH_DATA` and confirmed).
**Fix required:** state the assertion against the two-line markup — e.g. *"four `.navlink` spans whose `<br>`-joined text is `Agent Telemetry`, `Role Assets`, `Shared Asset Health`, `SkinSeoul WP Admin`"* — or add a normalisation clause to §8.0 harness rule 5 for `<br>`-broken labels.

---

### 9. MINOR — §9.1's PD dependency list is presented as complete but omits a cited PD

**Location:** §9.1, closing paragraph: *"This page depends on **PD-1, PD-2, …, PD-80**"* (23 ids) vs §10, row `2026-08-03 | Program-wide item 16: Carrier is not auto-recorded on inbound … ([PD-9])`.
**Evidence:** extracting every `[PD-n` token from the document yields 26 distinct ids; subtracting the two NO-DEFAULT entries listed separately leaves 24, one more than the 23 enumerated. The extra is `PD-9`, cited untagged.
**Fix required:** either drop the `[PD-9]` citation (the row's point — "do not confuse inbound carrier auto-record with import-side carrier auto-assign" — survives without it) or footnote the enumeration as "behaviour-bearing dependencies; `PD-9` is cited in §10 as a non-applicable cross-reference".

---

## Counts

| Severity | Count |
|---|---|
| BLOCKER | 0 |
| MAJOR | 1 |
| MINOR | 8 |
| **Total** | **9** |
