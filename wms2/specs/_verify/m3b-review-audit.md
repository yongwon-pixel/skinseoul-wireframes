# M3b — Audit of `_review.md`'s own claims

Method 3b (supervisor mandate): treat every factual assertion in
`wms2/specs/_plans/_review.md` as a hypothesis. Evidence re-derived from the 16 plans,
the 8 wireframes, the two registers and `_global-rules.md`. No claim was accepted on the
review's own authority; `_xref_check.py`'s green exit was itself treated as a claim.

Auditor: fresh-context verification agent · 2026-08-03.
Sources of truth: `wms2/specs/_plans/{slug}.{A,B}.md` (16) · `wms2/{slug}/index.html` (8) ·
`_provisional-decisions.md` (86 entries) · `_wireframe-fixes.md` (14 entries) ·
`_global-rules.md` v1.0 · `_inputs/{global-rules-draft,decision-sources,slack-routing}.md` ·
the 8 written specs `wms2/specs/{slug}.md`.

---

## 0. Scoreboard

| Group | Claims | CONFIRMED | PARTLY | REFUTED |
|---|---|---|---|---|
| §2a legend-count reconciliation | 6 | 4 | 2 | 0 |
| §2b mandatory 12 × 8 matrix | 4 | 1 | 1 | 2 |
| §1 adjudications C-1…C-12 | 12 | 12 | 0 | 0 |
| §4 global-rule deltas GD-1…GD-10 | 10 | 9 | 1 | 0 |
| Cross-reference correction note | 5 | 1 | 1 | 3 |
| **Total** | **37** | **27** | **5** | **5** |

---

## 1. §2a — A/B legend-count reconciliation

Method: parsed every `<div class="legend">` block in each wireframe and counted `<li>`
units per block; separately counted `<span class="dot">` markers per state/modal container;
separately extracted the §1 key list from all 16 plans (bullet form and table form).

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 1.1 | **"Result: 0 count mismatches"** — Lens A and Lens B agree on all 8 pages | **CONFIRMED** | Key sets compared item-by-item, not just totals. VO A=58+3 footers / B=58+3 offscreen (identical 58 keys). OD A `1..14+M3` / B `L-1..L-14+M3`. RTO both `1..14+M1`. INV both `5..16+M1..M4`. OM both `{1,2,3,4,5,M1,M1b,M2,M3}`. TM both `0..5+M1`. CL both 22 rows. IR both 28 keys. |
| 1.2 | Per-page unit counts (58/15/15/16/9/7/22/28) | **CONFIRMED** | HTML legend `<li>` counts: VO 50 (+8 modal keys = 58) · OD 14 (+M3) · RTO 14 (+M1) · INV 12 (+M1–M4) · OM 5 (+M1/M1b/M2/M3) · TM 6 (+M1) · CL 19 (+M1/M2 = 21, +`L-1.B` = 22) · IR 27 (+M1 = 28). Every figure reproduces the review's table. |
| 1.3 | VO per-state breakdown `S0 2 · S1 21 · S1b 1 · S2 2 · S3 4 · S4 6 · S5 3 · S6 9 · S6b 2` | **CONFIRMED** | Legend blocks in `view-orders/index.html` yield exactly 2/21/1/2/4/6/3/9/2 = 50. (On-canvas `dot` spans give S4 = 4, because `S4-3`/`S4-4` are modal-internal and carry no dot — both plans state this, so it is not a discrepancy.) |
| 1.4 | "Total ≈ 169 legend units + 6 off-screen normative blocks" | **CONFIRMED** | 58+15+15+16+9+7+**21**+28 = 169 (closing counted at 21, its 22nd key being the off-screen block). Off-screen blocks = VO 3 (`S1`,`S5`,`S6` footers) + CL 1 (`L-1.B`) + IR 2 (`S1`,`S2` footers) = 6. IR's third un-numbered entry is an "un-dotted on-screen" group, correctly not counted as a footer. |
| 1.5 | stock-status row **"16 \| 16 \| OK"** | **PARTLY** | The two §1 tables do both hold 16 rows, so "no mismatch" is defensible. But `stock-status.B.md:32` additionally keys `[L-F1]`(history search) `[L-F2]`(inbound form) `[L-F3]`(outbound form) `[L-F4]`(export) and references them in its QA map (`:137`, `:138`, `:158`); `stock-status.A.md` contains **zero** `L-F` strings. B's true inventory is 20 units, A's is 16. The review flags this in Notes/§2c-3 but the table cell and the 169 total both carry 16. |
| 1.6 | closing row "OK" | **PARTLY** | Counts match (22 = 22). But A keys the off-screen block `[L-1.B]` (`closing.A.md:11,27`) and B keys it `[L-1.BR]` (`closing.B.md:27,50,79`). §2c enumerates 5 keying discrepancies to normalize and this one is absent from the list. No downstream damage: the written `closing.md` resolved it to `[L-S1-F]`. |

---

## 2. §2b — mandatory 12 × 8 matrix

Method: for each **n** cell the spec was searched for an explicit statement (rule ID, N/A
row, out-of-scope row). Counting was done against the written specs, not the plans.

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 2.1 | **"every item has a primary home"** | **REFUTED** | Rows 2 (`[G-2]` toast), 3 (`[G-3]` audio), 4 (`[G-4]` print) and 12 (`[G-7]` comments) contain **no `P` cell anywhere** — only Y/Δ/n/⚑. 4 of 12 mandatory items have no primary home in the matrix as drawn. (Defensible in spirit — these are all-pages global rules — but the sentence is false as written and cannot be cited as proof of completeness.) |
| 2.2 | **"every N/A cell is an explicit statement (stated in spec, not silent)" / "0 holes"** | **REFUTED** | `closing.md` contains **0** occurrences of `G-14` and **0** of `JIT` (2219 lines). Matrix items 9 (line-based location filter), 10 (audit-mode-only visibility) and 11 (JIT residual stock) are coded **n** for CL but are *silent*, not explicit — `closing.md` §9.1 "Explicitly out of scope" has no row for any of the three. Same failure for item 11 on `order-management.md` (**0** `JIT` hits), `ready-to-outbound.md` (no JIT-residual N/A row; its out-of-scope table covers only "Stock audit, location registration, Reserved views, line-based location filtering") and `inbound-request.md` (no residual-stock statement; its §2 N/A table covers G-1/G-3/G-4/G-13/G-14 only). **≥ 6 silent cells.** Counter-examples that *do* satisfy the rule: `tracking-missing.md` §2.6 rows 9/10/11 and `:1300`; `view-orders.md:1980`; `order-detail.md:2115`; `order-management.md` §6.6 grid. |
| 2.3 | Individual P/Y/Δ/n codes | **PARTLY** | Spot-checked all 96 cells against the specs; two mis-codings and one undefined symbol. **(a)** Item 3 for OD and INV is coded `Δ³` = "delta/cross-ref only", but `order-detail.md:38` and `stock-status.md:522,722,1082` specify the send sound as page behavior *with* a QA scenario — these are `Y`, not `Δ`. **(b)** Item 4/CL uses `⚑`, a symbol absent from the P/Y/Δ/n legend. Everything else reproduces. |
| 2.4 | Footnotes 1–6 | **CONFIRMED** | ¹ IR Enter-must-not-submit → `inbound-request.md:59`, `BR-24:734`. ² RTO Bulk Outbound sole refresh exception → `ready-to-outbound.md:274`, `BR-8:594`. ³ PD-2 → both specs (2.3a). ⁴ PD-68 → `closing.md:568,687,737,899`. ⁵ PD-27/PD-36 → `order-detail.md`, `ready-to-outbound.md:140,501`. ⁶ unknown ≠ unrecognized boundary → `closing.md:507–516`. |

---

## 3. §1 — the 12 adjudications C-1…C-12

Every adjudication was checked twice: (i) do the cited sources actually say what the review
says they say, and (ii) did the written spec adopt the verdict.

| ID | Grounded in cited sources? | Honored by the specs? | Evidence |
|---|---|---|---|
| **C-1** Carrier auto-record NOT supported | **Yes** | **Yes** | `view-orders/index.html:1401` (inside `#s6b`, which opens at :1355) "Carrier recorded automatically" vs `:1350` S6 footer "automatic Carrier recording is not supported, confirmed 2026-08-03"; `inbound-request/index.html:396` footer "Received Date and Carrier are recorded automatically" vs `:669` S3-10 "Automatic Carrier recording is not supported — no Carrier column". Specs: `view-orders.md:132,479`, `inbound-request.md:153,380,565`. |
| **C-2** Routing file beats "pending" | **Yes** | **Yes** | `global-rules-draft.md` G-7 ends "(one item pending owner decision)"; `decision-sources.md` item 12 "(channel decision pending owner)"; `slack-routing.md` row 4 "CONFIRMED (owner, 2026-08-03)". "All 16 plans already agree" verified: all 16 contain `fulfillment-admin-comments` (2–6 hits each). All 8 specs cite `C0BMGEWM5QA` (3–10 hits); no spec writes "pending" for that row (`order-detail.md:180`). |
| **C-3** G-5 must be amended for OTHER | **Yes** | **Yes** | `inbound-request/index.html:381` legend 2 = "4 radio cards (Smart Buy / Wholesale / Brand Partnership / Other — type the channel name)"; OTHER badge at `:284`, `:435`. Spec: `inbound-request.md:158,198,314,453,847` all `[PD-80 · OWNER-PENDING]`. |
| **C-4** Closing = CSV only | **Yes** | **Yes** | `decision-sources.md` mandatory item 4 lists "Closing report"; `closing/index.html:692` `Download Closing Report (CSV)`, zero Print buttons on the page. Spec: `closing.md:568,687,737,817,899`. |
| **C-5** Send sound = every outbound-class button | **Yes** | **Yes** | `global-rules-draft.md` G-3(a) "Outbound-class buttons"; `decision-sources.md` item 3 "View Orders/RTO"; `order-detail/index.html:398` `<button id="obBtn">📦 Outbound`; `stock-status/index.html:322` `－ Record Outbound`. Specs: `order-detail.md:38,182`; `stock-status.md:522,722,1082,1269`. |
| **C-6** G-2 beats wireframe omissions | **Yes** | **Yes** | `tracking-missing/index.html:400-404` — `.xdel` handler is `b.closest('tr').remove(); poolDec();` with no confirm, no reason, no toast. `closing/index.html:869-870` — `if(!targetIn0.value.trim()) return;` silent no-op. Specs: `tracking-missing.md` BR-9 `:533`; `closing.md` E-16 `:960` (red toast copy specified), `:104`, `:2191`. |
| **C-7** Auto-outbound is VO-only | **Yes** | **Yes** | `view-orders/index.html:557` legend 9 "inbounding everything completes the order, so it auto-outbounds too"; `order-detail/index.html:657` legend 9 "Enabled only when every item is INBOUNDED" (gate, not trigger). Spec: `order-detail.md:184,322,525`, BR-5 `:740`, QA `:1509`, decision log `:2227`. |
| **C-8** G-13 beats RTO M1 | **Yes** | **Yes** | `global-rules-draft.md` G-13 "internal invoice & picking label show WHICH sample and HOW MANY"; `ready-to-outbound/index.html` `#m-pick` table holds 4 product rows and no sample row. Spec: `ready-to-outbound.md:140` (WF-9 conditional), `:501` `[PD-36 · OWNER-PENDING]`. |
| **C-9** Both retained with a boundary | **Yes** | **Yes** | `ready-to-outbound/index.html:335` legend 6 "No failure case (all-success is the normal behavior)"; the 2026-07-22 date is carried by both plans (`ready-to-outbound.A.md:16,45`, `.B.md:18,57`); `E-39` exists at `view-orders.B.md:168,196,225,245`. Spec: `ready-to-outbound.md:243,316` — separate red toast, per-order results persisted `[DC-16]`/`[DC-24]`. |
| **C-10** 07-23 wins; no large red panel | **Yes** | **Yes** | `closing/index.html` State-1 legend #2 "The large colored panel is used only in warning states (red)" vs State-2 legend #1 "The large warning panel and action banner were removed 2026-07-23". Spec: `closing.md:41,102,235,542,685`. |
| **C-11** Wireframe M6 strings canonical | **Yes** | **Yes** | `view-orders/index.html` `#m-qtyedit` options are exactly `Damaged/defective — cannot accept` · `Supplier qty change` · `Other`; draft G-11 said "supplier change / damaged / other". Spec: `view-orders.md:629` + BR-53 + byte-exact QA at `:1480`. `_global-rules.md` G-11 aligned. |
| **C-12** Event-name divergence, resolved by convention | **Yes** | **Yes** | Divergence real: `view-orders.A.md:142` `product_barcode_register` vs `stock-status.A.md:87` `barcode.registered`. All 8 written specs now use the canonical `product.barcode_registered` / `comment.*` / `order.status_changed` / `order.outbounded` / `print.job_result`; a grep for the legacy variants across the 8 specs returns **0** hits. |

**Adjudicated non-issues** (§1 tail) were also spot-checked and hold: `_wireframe-fixes.md` §E
records all six of them as explicit NON-fixes, and both closing and tracking-missing specs
state the disjointness (`closing.md:507–516`).

---

## 4. §4 — GD-1…GD-10 against `_global-rules.md` v1.0

Baseline for "delta" = `_inputs/global-rules-draft.md`.

| Delta | Landed? | Evidence in `_global-rules.md` |
|---|---|---|
| **GD-1** G-7 channel + system auto-comments + entity types | **CONFIRMED** | `:46` channel + `C0BMGEWM5QA` + "CONFIRMED by owner 2026-08-03"; `:47` `source=system`; `:48` "orders **and** inbound requests **and** unrecognized-pool items". |
| **GD-2** G-5 amend "Exactly 4" | **CONFIRMED** | `:33-35` order-facing badges (4) / inbound form (4 incl. OTHER free-text) / `[PD-80]` / "JIT is never a requestable inbound route". |
| **GD-3** G-3 scope + warning tone | **CONFIRMED** | `:23` "every outbound-class button on every page — View Orders …, RTO …, Order Detail …, Inventory (− Record Outbound)" `[PD-2]`; `:25` (c) distinct warning tone. |
| **GD-4** G-11 enum + edit origin | **CONFIRMED** | `:64` exact enum `"Damaged/defective — cannot accept" / "Supplier qty change" / "Other (memo)"` + "originate **only** in View Orders M6". |
| **GD-5** G-2 removals are confirming actions | **CONFIRMED** | `:19` "Removal/deletion confirmations count as confirming actions [GD-5]"; `:18` RTO sole exception retained. |
| **GD-6** G-8 explicit NON-events | **CONFIRMED** | `:54` verbatim doctrine paragraph. |
| **GD-7** G-14 1:1 pending owner | **CONFIRMED** (reworded) | `:76` "One location per SKU. Whether two SKUs may share one location is `[PD-46 · OWNER-PENDING]` (provisional: 1:1…)". Meaning preserved; phrasing turned into a pending question rather than the asserted extension. |
| **GD-8** new G-15 Permissions | **CONFIRMED** | `:80-81` G-15, single admin role, actor recorded, `[PD-1]`, "six screens independently raised the same question". |
| **GD-9** G-4 surface registry shrinks | **CONFIRMED** | `:29` print-surface list matches GD-9 word for word; closing = CSV only `[PD-68]`. |
| **GD-10** G-10/G-12 unchanged; G-1 closing deltas page-spec only, **no global text change** | **PARTLY** | G-10 (`:60`) and G-12 (`:68`) are unchanged ✓. But G-1 **did** take a global text change: `:15` now reads "Page deltas may add local behavior (e.g. Closing disables the input before the count is entered), never remove the three invariants above." Benign and consistent with intent, but it contradicts the delta's own "no global text change" instruction. |

**Dropped deltas: none.** All ten are present in v1.0.

---

## 5. Cross-reference correction note (end of `_review.md`)

Method: `diff _review.v1-agentA.md _review.md` — the note itself designates the `.v1-agentA`
files as the pre-correction baseline, so that diff *is* the ground truth for "what was remapped".

| # | Claim | Verdict | Evidence |
|---|---|---|---|
| 5.1 | "All citations in this document have been mechanically remapped … PD 16→21, 20→27, 28→34, 29→36, 43→46, 53→5, 61→68, 75→80; WF 6→5, 7→10, 10→9" | **REFUTED** | The diff between the pre-correction copy and the current file contains exactly **one** content change: line 45, `WF-10` → `WF-9`. Nothing else changed except the appended note itself. The pre-correction copy already cited `PD-1, PD-2, PD-21, PD-27, PD-34, PD-36, PD-46, PD-60, PD-68, PD-80` and `WF-1, WF-2, WF-5, WF-9, WF-10`; it never contained `PD-16/20/28/29/43/53/61/75` or `WF-6/7`. **10 of the 11 listed remaps never happened and were never needed.** |
| 5.2 | Specifically "PD 53→5" | **REFUTED** | `PD-5` appears **nowhere** in `_review.md` (grep of all `PD-\d+` yields 1, 2, 21, 27, 34, 36, 46, 60, 68, 80). The removal/confirm/toast citation in C-6 and GD-5 is `PD-60`, which is register-correct (`[PD-60] ✕ removal has no confirm, no reason, no toast`). `[PD-53]` in the register is "What does the period govern for target = 'Selected orders only'?" — unrelated, and never cited. |
| 5.3 | The one remap that *was* applied (`WF-10` → `WF-9`) | **REFUTED — regression** | §2a tracking-missing Notes now reads "Dead v1 CSS/JS excluded by both → **WF-9**". Register: `[WF-9]` = "ready-to-outbound — picking list modal (M1) has no sample-set lines"; `[WF-10]` = "tracking-missing — v1 CSS/JS leftovers from the 2026-07-23 simplification". The pre-correction file had `WF-10`, which was **correct**. The correction pass broke a citation that was already right. |
| 5.4 | Every remapped ID now points at a register entry with the matching meaning | **PARTLY** | 13 of 14 citations are semantically correct: PD-1 (permissions) · PD-2 (sound) · PD-21 (OD auto-outbound) · PD-27 (OD sample display) · PD-34 (batch failure) · PD-36 (picking-list samples) · PD-46 (location exclusivity) · PD-60 (removal) · PD-68 (closing CSV) · PD-80 (OTHER) · WF-1 (VO carrier banner) · WF-2 (IR carrier footer) · WF-5 (closing panel) · WF-9 **in C-8 only** (RTO picking list). The 14th — WF-9 in §2a — is wrong per 5.3. Independent corroboration that "6→5, 7→10" were never real: the written specs cite the register directly and correctly, `tracking-missing.md:59` → `WF-6`, `closing.md:103` → `WF-7`. |
| 5.5 | "Verified by `_xref_check.py`" | **PARTLY** | The script does exit 0 (`PD entries: 86 · WF entries: 14 · review cites PD 10 / WF 4 … XREF OK`), so the literal claim holds. But the verification is vacuous for the only change made: the script matches a keyword inside a 600-character window of the register entry and never checks the *citation site*, so `WF-9` in a sentence about tracking-missing dead code passes because the WF-9 entry contains "picking"/"sample". Worse, its `EXPECT` table asserts `PD-5` — an ID the review does not cite at all — while `WF-10` silently dropped out of `cited_wf` when the bad edit removed it. A green run here is not evidence of citation correctness. |

---

## 6. Consequences of the refuted claims

1. **[from 5.3 — highest priority] `_review.md` §2a line 45 mis-points the tracking-missing dead-code cleanup at WF-9.**
   Any wireframe-edit pass driven off the review rather than off `_wireframe-fixes.md` will look for
   dead CSS in `ready-to-outbound/index.html` (there is none) and will leave the real leftovers in
   `tracking-missing/index.html` — `.trk`, `.shelf`, `.wait`, `.slack-pill`, `.picava`, `.picname`,
   `.cntchip`, `.logsec`, the trk-input script block and the Resolved-button JS. That is exactly the
   "developer re-implements per-PIC groups / bulk bar / Slack column / resolved log" risk WF-10 was
   filed to prevent. **Fix: revert line 45 to `WF-10`.** One-character class of change; no other
   artifact depends on it.

2. **[from 2.2] §2b's "0 holes" is the gate that closed the mandatory-inclusion audit, and it is not true.**
   `closing.md` has no explicit N/A for mandatory items 9, 10 and 11; `order-management.md`,
   `ready-to-outbound.md` and `inbound-request.md` have none for item 11. A P3-4 coverage check that
   trusts §2b will certify a spec set containing silent cells — the precise failure mode the
   "explicit N/A, never silent" rule exists to prevent, and the reason `tracking-missing.md` §2.6 and
   `order-management.md` §6.6 were written. **Fix: add one out-of-scope row to `closing.md` §9.1
   ("Location scheme, line-based location filter, audit-mode-only visibility `[G-14]`, JIT residual
   stock → stock-status") and one JIT-residual row each to the RTO / OM / IR out-of-scope tables.**
   No behavior changes; four table rows.

3. **[from 2.1] "every item has a primary home" cannot be used as evidence of matrix completeness.**
   Items 2, 3, 4 and 12 have no `P` cell. Nothing is actually missing from the specs — these are
   all-pages global rules — but a downstream agent asked to prove coverage from this sentence will be
   proving something false. **Fix: either add `P` markers (G-2 → VO; G-3 → CL; G-4 → RTO; G-7 → the
   hub is identical everywhere, so mark it "no single home, by design") or reword the sentence.**

4. **[from 2.3] Coding OD and INV audio as `Δ` under-reports two specs.**
   `order-detail.md:38` and `stock-status.md:522/722/1082` carry the full send-sound contract plus a
   QA scenario — that is `Y`. A reader using the matrix to locate the audio contract will skip both.

5. **[from 5.1 / 5.5] The correction note overstates the work performed, and the checker that
   "verified" it cannot detect the one real defect.**
   Anyone re-auditing "was the cross-reference corrected?" gets a green script and a note describing
   eleven remaps, of which one occurred and was wrong. **Fix: rewrite the note to state what actually
   changed, and tighten `_xref_check.py` to test the citation *context* (the ±200 chars around each
   `PD-n`/`WF-n` occurrence in the review) against the register entry, not merely the entry's own text.**

6. **[from 1.5] stock-status's real unit count is 20, not 16.**
   `[L-F1..F4]` exist in Lens B only and are absent from both the §2a cell and the 169 total. A P3-4
   count of `stock-status.md` against "16" will read 4 units as phantom extras — or, worse, will not
   notice if the four baseline-furniture units were dropped. The written `stock-status.md` does key
   `[L-F1..F4]`, so the spec is fine; the review's number is what is stale.

7. **[from 1.6 — informational, no action] closing's off-screen block is `[L-1.B]` in A and
   `[L-1.BR]` in B**, a keying divergence §2c does not list. Already resolved in the written spec as
   `[L-S1-F]`, so nothing downstream is broken.

---

## 7. What this audit did **not** find

- No fabricated adjudication. All 12 C-rulings are traceable to real text in the wireframes,
  `_inputs/`, or the plans, and all 12 are honored by the written specs.
- No dropped global-rule delta. GD-1…GD-10 are all present in `_global-rules.md` v1.0.
- No A/B count mismatch. The "0 mismatches" headline survives an independent recount.
- No PD citation with the wrong meaning. All 10 PD IDs in the review resolve correctly.
- The §2c keying-normalization instructions were followed by the written specs: `closing.md` uses
  `[L-S1-8]`/`[L-SH-1]`/`[L-S1-F]` (not `[L-1.8]`), and QA tier tags are `[WF]`/`[ADMIN]` only —
  `WF-RUN`, `REAL-ADMIN` and `ADMIN-ONLY` return 0 hits across all 8 specs.
