# M1 — Coverage Audit · `inbound-request`

Method: **Verification Method 1 (independent coverage audit).** The auditor did not author the spec.
Target: `wms2/specs/inbound-request.md` (1,859 lines, v1.1, 2026-08-03)
Wireframe SST: `wms2/inbound-request/index.html` (**850** lines, `wc -l`, file terminates with a newline)
References: `_global-rules.md` v1.0 · `_plans/_review.md` (§3 conventions binding) · `_plans/_provisional-decisions.md` · `_plans/_wireframe-fixes.md` · `_plans/inbound-request.A.md` · `_plans/inbound-request.B.md`
Date: 2026-08-03

**No count asserted by the spec was taken on trust.** Every number below was re-derived by parsing the HTML and the markdown (regex extraction over `.dot` spans, legend `<li>` rows, `QA-[A-G]-nn` headings, `[E-n]` / `[DC-n]` / `[L-*]` / `[PD-n]` keys). Where the audit's number and the spec's number agree, that is recorded as verified, not as accepted.

---

## 1. PASS / FAIL table

| # | Check | Verdict | Basis |
|---|---|---|---|
| 1 | Legend coverage | **FAIL** | 30 wireframe units enumerated (28 `.dot` + 2 off-screen footers); **0 are specified nowhere** — the failure is that §2.1's "Verification" paragraph asserts a fact about the SST that is false, and the wireframe's one orphan dot is unacknowledged (D1). Also D3, D11. |
| 2 | Plan coverage | **PASS** | All 16 A-plan `DC-n` events land in §5 (spec carries 23, a strict superset). All 46 B-plan `E-n` candidates land in §7. All A-plan `O-1…O-5` / `D-1…D-8` and all B-plan `OQ-1…OQ-14` are routed to a PD, §9.2 or §9.3. One non-list item dropped silently → D9 (outside this check's stated scope, still reported). |
| 3 | QA integrity | **FAIL** | Counts, tier split and negative share are **exactly as claimed** (verified independently). All 23 `DC-n` are asserted by ≥1 scenario. All `[L-*]` keys used in QA exist. **But 15 of 93 `[E-n]` are referenced by zero scenario** (D2). |
| 4 | PD discipline | **FAIL** | 23 of 23 cited PDs spot-checked against the register — all exist, all meanings match. No NO-DEFAULT PD presented as decided. **But** one provisional written as settled and untagged (D7), and three PDs cited whose register `Pages:` scope excludes IR (D8). |
| 5 | Convention compliance | **FAIL** | Key formats, ID continuity, merge-alias discipline, Slack notation, Korean-verbatim and the 12 "must NOT exist" negative entries all hold. **But** `_review.md` §3.7 date rule violated in §10 (D4), and the `E-18b` key violates the very `[E-{n}]` convention the spec invokes to retire `E-c1` (D5). Also D12. |
| 6 | Global-rule hygiene | **FAIL** | Cites `[G-1]`…`[G-15]` correctly; no undeclared deviation from any G-rule; `[G-1]`/`[G-3]`/`[G-4]`/`[G-13]`/`[G-14]` N/A declared in §1.5. **But** §3.1.13 restates `[G-7]`'s hub body near-verbatim (D6). |
| 7 | Adjudication compliance | **PASS** | C-1, C-2, C-3, C-6, C-11, C-12 all honored; the three adjudicated non-issues touching this page (dot-13 gap, inert chips/checkboxes, always-toasts-on-Register) are all declared, not "fixed"; WF-2 and WF-11 are carried as defects and their stale text is never specced as truth. |

### Derived numbers (auditor's own extraction)

| Quantity | Spec claims | Audit measures | Match |
|---|---|---|---|
| On-screen `.dot` elements | 28 | **28** (S1 15 · S2 2 · S3 10 · M1 1) | yes |
| Legend `<li>` rows | 28 | **27** (15 + 2 + 10) | **no** |
| Off-screen normative footer blocks | 2 | **2** (index.html:396, :512) | yes |
| State 1 dot set | 1–12, 14, 15, 16 (no 13) | `{1..12, 14, 15, 16}` | yes |
| QA scenarios | 115 (A30 B7 C24 D17 E11 F10 G16) | **115** (A30 B7 C24 D17 E11 F10 G16), no gaps, no duplicate IDs | yes |
| Tier split | 51 `[WF]`-only · 62 `[ADMIN]`-only · 2 dual | **51 / 62 / 2** (dual = QA-A-19, QA-A-25); 0 untagged | yes |
| Negative tests | 50 (43.5 %) | **50 / 115 = 43.48 %** — above the 25 % floor | yes |
| `[E-n]` defined | 93 (`E-1`…`E-92` + alias `E-18b`) | **93**, numeric range 1–92, **no gaps** | yes |
| `[DC-n]` defined | 23 | **23** (`DC-1`…`DC-23`), all referenced by ≥1 scenario | yes |
| Wireframe line count | 851 | **850** | **no** |

Byte-accuracy spot-check: 60 UI strings the spec quotes as byte-accurate were matched against the wireframe (after tag-stripping). **59/60 present verbatim.** The single absentee — `Already added — edit the quantity on the existing row` — is a spec-invented string correctly tagged `[PD-83 · OWNER-PENDING]` and asserted only in an `[ADMIN]` scenario. Not a defect.

`[WF]`-tier executability spot-check (17 scenarios traced to DOM/CSS/JS): QA-A-02/04/05/07/10/11/13/17/18/23/24/25/28, QA-B-01/02/03, QA-C-02/07/08/09/10/11/14/15/16/19/24, QA-D-01/03/04/05/06/17, QA-F-01/02/04/06, QA-G-10/16 all resolve against real selectors, real classes and real script behavior — including `--ink: #14101B` = `rgb(20, 16, 27)` for QA-C-07, `.pagepad{padding:18px 16px 0}` and `.mock{min-width:1280px}` for QA-A-25, `title="Expected qty edit history"` at index.html:610 for QA-C-09, `IR_COMMENTS` key coverage for QA-F-04/F-06, and the `2600` ms `gtoastShow` timer for QA-A-18/A-19. One `[WF]`-adjacent path is unexecutable → D3.

---

## 2. Defect list

### D1 — §2.1 asserts a false verification of the SST *(MAJOR · check 1)*

**Location.** §2.1, line 79, "**Verification.**" paragraph:
> "The wireframe carries exactly 28 on-screen `.dot` elements and exactly **28 legend `<li>` rows** … a perfect 1:1 dot↔legend mapping with **no orphan dot** and no legend row lacking a dot."

**Fact.** The wireframe carries 28 `.dot` elements and **27** legend `<li>` rows — 15 (State 1, index.html:380-394) + 2 (State 2, :509-510) + 10 (State 3, :660-669). The `M1` dot at index.html:677 sits on the modal and has **no legend row in any of the three `<div class="legend">` blocks**. It is precisely an orphan dot. The claim is not a rounding slip; it is the one sentence in the document that asserts an independent check was performed, and the check it reports did not hold.

**Why it matters.** A downstream coverage checker that trusts this sentence will conclude the legend↔spec map is self-proving and stop looking. The orphan is benign (M1 *is* specced at §3.4 and covered by QA-D-01…D-17), which is exactly why it must be declared rather than denied — §2.1's own stated purpose is "so coverage checks do not flag phantom holes".

**Fix.** Replace the sentence with the measured truth and add the orphan to the "Declared numbering gaps and artifacts" list:
> "The wireframe carries exactly 28 on-screen `.dot` elements and 27 legend `<li>` rows (State 1: 15 · State 2: 2 · State 3: 10). The 28th dot, `M1`, is annotated directly on the modal and deliberately carries **no legend row** — it is an intentional orphan dot, specified in full at §3.4. Every legend row has a dot; exactly one dot has no legend row."

---

### D2 — 15 edge cases carry no QA scenario *(MAJOR · check 3)*

**Location.** §8 (Blocks A–G) vs §7.1–§7.6.

**Fact.** Parsing every `QA-[A-G]-nn` body for `E-n` tokens (scenario IDs stripped first), these 15 of 93 defined edge cases are referenced by **zero** scenario:

`E-2` (empty Order Qty) · `E-9` (route switched after rows exist) · `E-11` (search no-match) · `E-15` (past Expected arrival) · `E-16` (empty Memo) · `E-18` (network failure mid-registration) · `E-27` (row already holds numbers) · `E-31` (deep link `#reqlist`) · `E-50` (unknown/no-op hash) · `E-54` (blank Expected arrival) · `E-56` (200-line request) · `E-57` (tab switch with unsaved draft) · `E-63` (session expiry mid-form) · `E-85` (deep link with unsaved draft) · `E-90` (keyboard-only route cards + search box).

Several are *behaviourally* covered but not *keyed* — QA-C-01 exercises `E-31`/`E-50`, QA-C-08 exercises `E-27`, QA-A-07 exercises `E-11`, QA-A-24/A-20 exercise `E-16`, QA-A-04/A-05/A-09 exercise `E-90`. Others have no scenario at all: `E-2`, `E-15`, `E-18`, `E-54`, `E-56`, `E-57`, `E-63`, `E-85`. `E-2` is an ordinary required-field block on the page's most-typed numeric input and is untested.

**Why it matters.** §8.1 and §8.2 provide a `DC-n`→scenario map and an `[L-*]`→scenario map, and both are complete. There is **no `[E-n]`→scenario map**, so the gap is invisible from inside the document and an executing QA agent silently under-runs §7.

**Fix.** (a) Add the missing `[E-n]` keys to the seven scenarios that already exercise the behavior. (b) Add `[ADMIN]` scenarios for `E-2`, `E-15`/`E-54`, `E-18`, `E-56`, `E-57`/`E-85`, `E-63` (six new rows; Block A and Block C). (c) Add a **§8.3 Edge-case coverage map** in the same shape as §8.1/§8.2 so the invariant is checkable, and state the invariant explicitly ("every `[E-n]` carries ≥1 scenario").

---

### D3 — M1 open trigger (b) is unwired in the wireframe and absent from the demo-limitation list *(MAJOR · check 1 / 7)*

**Location.** §2.2 table, M1 row — "How to reach it: … or `Bulk add tracking numbers`"; and §3.4 "**Open triggers.** … (b) `Bulk add tracking numbers` in the bulk bar".

**Fact.** index.html:548 is
`<button class="btn btn-purple-line btn-sm">Bulk add tracking numbers</button>`
— **no `data-modal` attribute**, and the only modal-opening handler in the script binds `document.querySelectorAll('[data-modal]')`. The button is inert. §2.2 is explicitly a *wireframe* map (its columns are "Wireframe surface / DOM id / How to reach it"), so it states a navigation path that does not exist in the artifact it maps. §2.4's list of "wireframe demo limitations that are not defects" — which enumerates inert chips, inert checkboxes, the unconditional Register toast, the static M1 header, the State-1-only hub dropdown and the static autocomplete — **omits this one**, and §3.4 marks trigger (c) as "in the wireframe only" while leaving (b) unqualified.

**Why it matters.** §2.4's stated function is to stop QA filing false bugs. A QA agent following §2.2/§3.4 will click `Bulk add tracking numbers`, observe nothing, and either file a bug or fail the M1 block.

**Fix.** (a) Append to §2.4's demo-limitation sentence: "`Bulk add tracking numbers` carries no `data-modal` and does not open `#m-invoice` in the wireframe — the bulk→M1 path is `[ADMIN]`-only." (b) In §2.2's M1 row, mark the bulk path `[ADMIN]`. (c) In §3.4, qualify trigger (b) the same way trigger (c) is qualified.

---

### D4 — Banned date shorthand in §10 *(MINOR · check 5)*

**Location.** §10, "**Reversal chains at a glance**", lines 1848-1855 — all eight chain entries, e.g. line 1848:
> "manual PO matching (pre-**07-23**) → auto-assign **with** a preview panel (**07-23**) → auto-assign **without** any preview (**07-26**, current)."

**Fact.** `_review.md` §3.7 is binding and unambiguous: "**Dates**: `YYYY-MM-DD` everywhere (Decision Logs, BR rationale, conflict citations). **No `07-23` shorthand in final specs.**" The Decision Log table itself (lines 1802-1844) is fully compliant; only the summary block below it regresses. 27 shorthand dates across 8 lines.

**Fix.** Expand every occurrence to `2026-MM-DD` in lines 1848-1855.

---

### D5 — `E-18b` violates the key convention the spec invokes to retire `E-c1` *(MINOR · check 5)*

**Location.** §7 preamble line 872 (retirement note) and line 874 ("plus the merged alias `E-18b`"); §7.2 line 921 (`| **E-18b** = **E-59** |`); QA-G-08 line 1612 (`[E-18b]`, `[E-59]`); §6.4 line 859.

**Fact.** The spec retires `E-c1` and gives two reasons, the second being that "`E-c1` **also violated the `[E-{n}]` key convention**". `E-18b` violates the same convention (`_review.md` §3.2: "edge cases `[E-{n}]`") in the same way — a letter-suffixed key — and unlike `E-c1` it has a fully conforming alias already in use (`E-59`). The document therefore applies its own stated rule inconsistently within eleven lines.

**Fix.** Drop `E-18b` from §7.2's key cell, §7 preamble line 874, §6.4 line 859 and QA-G-08; keep `[E-59]` as the sole key. If the `E-18b` label must remain traceable, record it in the same retired-ID note as `E-c1` rather than as a live alias. Update the §7 total to "92 edge cases (`E-1`…`E-92`, no gaps)".

---

### D6 — §3.1.13 restates `[G-7]`'s rule body *(MINOR · check 6)*

**Location.** §3.1.13, line 348:
> "…plus **full-text search across all comments (entity no. / author / text), newest first; clicking an entry opens the entity**."

vs `_global-rules.md` line 49:
> "…+ full-text search across **all** comments (entity no. / author / text), newest first, click opens the entity. Badge = unread mention count."

**Fact.** Near-verbatim reproduction, including the parenthetical field list and the sort order. `_review.md` §3.5 is binding: "cite `[G-n]` and write page **deltas only** — never restate the rule body." This is the only such restatement found; the `[G-11]` reason-enum reproduction in §3.3.5 is *not* one (it exists to anchor the new `BR-30` token map and is therefore delta material), and §6.1's payload fields are reproduced under the explicit instruction of `_review.md` §3.6.

**Fix.** Reduce line 348 to a citation plus the page delta: keep the byte-accurate `💬 Comments` label, the demo badge value `2`, the entity-type delta (inbound request / Inbound No.) and the State-1-only wireframe limitation; delete the re-description of search scope, sort order and click behavior, replacing it with "[G-7]".

---

### D7 — A provisional decision written as settled and untagged *(MINOR · check 4)*

**Location.** §9.1, line 1748:
> "| **Photo capture on inbound artifacts** | Permanently removed from the WMS 2.0 flows (2026-08-03, `[PD-63]`). No photo affordance on this page, and no phase pointer |"

**Fact.** `_provisional-decisions.md` opens with "**ALL PROVISIONAL — owner review pending 2026-08-03. … None is owner-approved.**" PD-63's own entry reads "Provisional: **Permanently removed.**" The spec presents it as an accomplished fact with a bare `[PD-63]` citation and no `· OWNER-PENDING` suffix, contrary to `_review.md` §3.8. The adjacent row in the same table handles PD-9 correctly (`[PD-9 · OWNER-PENDING]`), so this is an isolated slip rather than a policy.

**Fix.** `…(2026-08-03, `[PD-63 · OWNER-PENDING]`)`. Optionally soften "Permanently removed" to "Provisionally removed permanently (not deferred)" to preserve the anti-re-implementation intent without over-claiming owner assent.

*(Note: the untagged `[PD-9]`, `[PD-79]`, `[PD-66]`, `[PD-63]` occurrences at lines 1829, 1838-1839 are Decision-Log **citations**, not behavior statements, and are correct as written. `[PD-2]` at line 60 is a scope exclusion, likewise correct.)*

---

### D8 — Three PDs cited outside their registered page scope *(MINOR · check 4)*

**Location.** Spec: `[PD-12 · OWNER-PENDING]` at §3.3.5 line 492, `[E-92]` line 948, QA-C-22 line 1348 · `[PD-16 · OWNER-PENDING]` at §6.1 row 6 line 826 · `[PD-63]` at §9.1 line 1748. Register: `_provisional-decisions.md`.

**Fact.** Register `Pages:` lines read — PD-12: "VO (OQ-7/E-15)"; PD-16: "VO (Q3), TM, OD"; PD-63: "TM (Q4), VO (M2b)". None names IR. The spec's use of each is defensible (PD-12 governs what `n/m` values this page must render unclamped; PD-16 governs the auto-comment that lands on an inbound request; PD-63 governs an absence on this page), and the **meanings match exactly** — so this is a traceability defect, not a semantic one. Its practical cost: if the owner reverses PD-12/PD-16/PD-63, the register's own impact list will not point the editor at `inbound-request.md`, which is the register's stated purpose ("reversing one means editing the tagged sentences on the listed pages and nothing else").

**Fix.** Add `IR` to the `Pages:` lines of PD-12, PD-16 and PD-63 in `_provisional-decisions.md`. No change to the spec.

**Verified PDs (23 spot-checked, all present with matching meaning):** PD-1 single admin role · PD-2 send-sound scope (correctly declared N/A here) · PD-3 comments append-only · PD-4 Slack failure never blocks · PD-5 removals confirm + toast · PD-6 stale-entity revalidation · PD-7 concurrency 409 / merge for additive sets · PD-8 tracking uniqueness + namespace split · PD-9 no carrier · PD-12 over-receipt warn-and-count · PD-14 new expected qty ≥ received · PD-16 match auto-comment + self-suppression · PD-63 photo removed · PD-64 pool removal captures Inbound No. · **PD-66 NO-DEFAULT** (correctly presented as undecided, §9.2 OQ-2) · **PD-79 NO-DEFAULT** (correctly presented as undecided, §9.2 OQ-1) · PD-80 `OTHER (channel)` rendering · PD-81 matched numbers frozen · PD-82 duplicate number blocked · PD-83 no duplicate SKU · PD-84 no auto-transition on qty edit · PD-85 INBOUNDED terminal · PD-86 separate tracking namespaces.

---

### D9 — M1 keyboard contract silently dropped from the A-plan *(MINOR · check 2)*

**Location.** §3.4 (`[L-M1]`) — no `Enter` / keyboard clause anywhere in the section. Source: `inbound-request.A.md` §3b, "M1 under time pressure":
> "dispatch emails arrive with several tracking numbers; ＋-row + focus-new-input + **Enter-to-save** should be specced so a user can paste n numbers without touching the mouse (B to turn into QA scenario)."

**Fact.** The spec adopts two of the three requested behaviors — `＋ Add tracking number` appends and focuses (§3.4, verified against index.html:812-819), and multi-line paste splits across rows (`[E-72]`) — but says nothing about `Enter`. The omission is conspicuous because §3.1.5 and `BR-24` elevate Enter-key discipline to a named page rule ("Enter must never submit") for the search box, and §1.4 calls it "the page's only [G-1]-adjacent delta". A developer reading only §3.4 has no guidance on whether `Enter` in a `.qrow` input appends a row, saves the modal, or does nothing — and the wireframe's own `.qrow` inputs sit inside no `<form>`, so browser defaults will not settle it either.

**Fix.** Add to §3.4 a one-line keyboard contract (recommended: `Enter` in a `.qrow` input appends a new row and focuses it, mirroring `＋`; it never fires `Save tracking numbers`; `Escape` is a no-op, dismissal is `Cancel`/`✕`/backdrop only) and key it to `BR-24`. If the choice is genuinely open, register it as §9.3 `D-22` rather than leaving it unstated.

---

### D10 — Two invented normative behaviors carry no PD, no decision-log row and no dev-decision entry *(MINOR · check 4)*

**Location.** §3.1.2, "**Channel-text normalisation**", line 196:
> "…the value is compared **case-insensitively when grouping channels downstream**, so `Gmarket`, `gmarket` and `GMARKET ` do not become three channels (`[E-78]`). Characters that would break a Slack message or the sheet are **escaped at render time, never stripped from storage** (`[E-79]`)."

**Fact.** Neither rule appears in any plan, in `_provisional-decisions.md`, in `_global-rules.md`, in §9.3's dev-decision table, or in §10's Decision Log. They are sensible engineering defaults, but they are new normative constraints on a field the owner introduced (2026-07-26 `Other` + free text) and they bind downstream consumers (View Orders badge, Inventory route filter, the Procurement Hub sheet) that this spec does not own. The spec demonstrates elsewhere that it knows how to register its own inventions — §9.2 OQ-3 and `BR-30`/`BR-29`/`BR-31` are all raised as audit findings with Decision-Log rows — so the inconsistency is in the handling, not the substance.

**Fix.** Either add `D-22`/`D-23` rows to §9.3 (recommended — both are dev-time choices with an obvious default) or, if the downstream grouping semantics are an owner question, raise them with PD-80 as its unresolved second half. Add a `2026-08-03 (audit pass)` Decision-Log row either way.

---

### D11 — Wireframe line count off by one *(MINOR · check 1)*

**Location.** Header line 3: "Wireframe SST: `wms2/inbound-request/index.html` (**851 lines**, v1)".

**Fact.** `wc -l wms2/inbound-request/index.html` → **850**; the file ends with a newline (`… </script>\n`, hexdump-confirmed), so 850 is the true line count. The error is inherited from both plans (`inbound-request.A.md` line 3, `inbound-request.B.md` line 4 both say 851) and is therefore a propagated number rather than an independent one.

**Why it matters at all.** §2.4 and the WF-11 entry locate a defect by line ("an HTML comment … remains at ~line 701" — correct, index.html:701). Line-anchored references and a wrong total in the same document invite the reader to trust one and distrust the other.

**Fix.** `850 lines` in the spec header; correct both plans in the same pass, or drop the count entirely and cite the commit instead.

---

### D12 — Slack channel IDs annotated on second mention, not first *(MINOR · check 5)*

**Location.** First mention of both channels is §3.3.6, lines 516-517:
> "- `WHOLESALE` and `SMART BUY` → **#wholesale-ops**
> - `PARTNERSHIP` → **#partnership-kr**"

The qualifier "(ID not published in `_slack-routing.md`)" / "(ID not published)" appears only later, at §6.1 rows 1-2 (lines 821-822).

**Fact.** `_review.md` §3.6: "`#channel-name` with ID in parentheses **on first mention per spec**." Verified against `_inputs/slack-routing.md`: only `#fulfillment-admin-comments` publishes an ID (`C0BMGEWM5QA`), so the spec's "ID not published" annotation is factually correct and honest — the defect is placement only. `#fulfillment-admin-comments` is handled correctly (ID given at every occurrence, §6.1 rows 4-6, QA-E-04, QA-F-07). No confirmed row is ever written as "pending".

**Fix.** Move the parenthetical to the §3.3.6 first mention; §6.1 may then carry the bare channel name.

---

## 3. Summary

| Severity | Count | IDs |
|---|---|---|
| BLOCKER | 0 | — |
| MAJOR | 3 | D1, D2, D3 |
| MINOR | 9 | D4, D5, D6, D7, D8, D9, D10, D11, D12 |

**What the audit did not find.** No legend unit specified nowhere. No renumbering. No dropped A-plan data-capture event or B-plan edge case. No mis-stated QA count, tier split or negative-test share. No NO-DEFAULT PD presented as decided. No fabricated PD. No stale wireframe text specced as truth. No unhonored `C-*` adjudication. No undeclared deviation from a G-rule. The document's substantive engineering is sound; every defect above is a bookkeeping or traceability failure, and D1 is the only one that misrepresents the artifact it describes.
