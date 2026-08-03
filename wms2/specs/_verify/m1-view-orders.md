# M1 — Coverage Audit: `view-orders.md`

**Method:** independent. Every count below was re-derived from source with scripted extraction over
`wms2/view-orders/index.html` (1,847 lines) and `wms2/specs/view-orders.md` (2,159 lines). No count asserted
by the spec was taken on trust; each was recomputed and then compared to the spec's claim.
**Auditor:** verification agent (did not author the spec). **Date:** 2026-08-03.

---

## 1. Verdict table

| # | Check | Verdict | Derived evidence |
|---|---|---|---|
| 1 | Legend coverage | **PASS** | 9 `.legend` blocks → 50 `<li>` units (S0 2 · S1 21 · S1b 1 · S2 2 · S3 4 · S4 6 · S5 3 · S6 9 · S6b 2) + 8 modal dots (`M1 M2 M2b M3 M3b M4 M5 M6`) = **58**; 3 trailing normative `<p>` footers (HTML lines 571, 1230, 1350) = **61** normative units. Spec §3 defines **69** unit headings = the 61 + 8 furniture keys. Set difference in both directions is **empty**. |
| 2 | Plan coverage | **PASS** | A-plan `DC-1…DC-35`: all 35 map onto spec `DC-1…DC-47` (1:1 or split, e.g. A-DC-35 → spec DC-40/41/42; A-DC-23/24/25 → spec DC-28 `surface` enum + DC-30). B-plan `E-1…E-48`: 47 present at identical IDs; 1 (`E-6`) reassigned — situation still covered by `[BR-2]`, `[L-S1-1]` line 180 and QA-SC-02, so no behavioral hole. See Defect 1. |
| 3 | QA integrity | **PASS** | 273 scenarios derived (272 tagged + 1 DEFERRED) vs spec's 273 ✓; `[WF]` 135 ✓; `[ADMIN]` 137 ✓. `DC-1…47` each have ≥1 scenario whose Then-clause asserts persistence (0 misses). `E-1…92` each referenced ≥1× (0 misses). `BR-1…56` each referenced ≥1× (0 misses). Zero `[L-*]` keys used in QA that §3 does not define; zero §3 units unreferenced. Negative share **89/273 = 32.6 %** (independently recomputed; matches spec claim exactly) — above the 25 % floor. §7 re-counted: 91 entries / 92 IDs / 1 merged (`E-18 = E-51`) ✓. |
| 4 | PD discipline | **PASS** | 32 distinct PDs cited. All 31 behavior-bearing PDs carry `[PD-n · OWNER-PENDING]` in **every** occurrence (185 tagged citations, 0 untagged). `PD-66` is the only bare citation and is correctly bare: it is **NO-DEFAULT** in the register (line 362) and appears only as §9.2 OQ-1, `E-63` ("No behavior is specified here") and DEFERRED row QA-CV-22 — no behavior rests on it. Spot-checked 14 against the register (PD-5, 9, 10, 12, 14, 16, 18, 21, 26, 29, 41, 46, 63, 67, 80, 84, 86): meanings match. |
| 5 | Convention compliance (`_review.md` §3) | **FAIL** | Key formats, Slack notation (`#fulfillment-admin-comments` (`C0BMGEWM5QA`) ×8; the other three channels publish no ID, correctly stated), Korean-verbatim (19 Korean-bearing quoted strings checked; all resolve byte-exact against HTML source or rendered `textContent`), and removed-feature negatives (§9.4, 16 entries) all pass. Fails on **ID continuity** (Defect 1), **footer key format** (Defect 4) and **date format** (Defect 5); plus QA tier-tag deviation (Defect 6). |
| 6 | Global-rule hygiene | **FAIL** | Every deviation *is* declared as a page delta with rationale + date (§3.1 `[G-1]` default-focus delta; §3.2 `[G-2]` non-confirming-search delta; `[L-S1-15]` three `[G-2]`/`[G-3a]` deltas; `[BR-51]` `[G-2]` rendering-position delta, dated, cites `_review.md` C-6). But four `[BR-*]` rows restate G-rule bodies verbatim-equivalent with no delta, contradicting `_review.md` §3.5 and the spec's own line-6 claim. See Defect 3. |
| 7 | Adjudication compliance | **PASS** | C-1 → `[BR-24]` + §2.4 WF-1 + §10.2 R-1 + QA-S6-07/08 (stale banner explicitly specced as *wrong*). C-2 → §6.1 confirmed channel + ID, no "pending" anywhere. C-3 → `[BR-4]`/`[PD-80]`. C-5 → `[BR-32]`/`[PD-2]`. C-6 → `[BR-51]`/`[PD-5]`. C-7 → `[BR-6]`/`[PD-21]`. C-9 → `E-39`/`[BR-15]` boundary intact (PD-34 correctly left to RTO). C-11 → `[BR-53]` (M6 strings verified byte-exact vs HTML lines 1652–1654). C-12 → all 11 canonical event names present byte-identical. Adjudicated non-issues honored: M6 `…0002` vs `…0001` renumbering = §2.3 L-5; Deleo asymmetry = `[BR-40]`. **No stale wireframe text is specced as truth** — WF-1/WF-3/WF-13 are each listed in §2.4 with the corrected behavior and a rule ID. |

**Defect counts:** BLOCKER **0** · MAJOR **1** · MINOR **6**.

---

## 2. Defect list

### 1. `[E-6]` ID reassigned — collides with `view-orders.B.md` — **MAJOR**

**Location:** §7.1, line 966 — `| **E-6** | State 6 location entry names a location already holding a **different** SKU | …`
(also `[E-6]` cited at line 492 and line 1026, and QA-S6-27 at line 1524).

**Finding.** `_plans/view-orders.B.md` line 127 assigns **E-6 = "Coupang QR scan arrives as `[V1]8801051283860` → matches as if unprefixed."** The spec's E-6 is a completely different situation (occupied-location rejection). Verified mechanically: of B-plan's 48 edge-case IDs, **47 are preserved at identical IDs and identical meaning** — E-6 is the single divergence, which proves the numbering was intended to be carried over and this is an accident, not a design. `_review.md` §3.2 is binding: *"edge cases `[E-{n}]` … page-scoped, stable once assigned … Never renumber."*

The Coupang `[V1]` behavior itself is **not lost** — it is specced at `[L-S1-1]` (line 180), `[BR-2]` (line 677) and asserted by QA-SC-02 (line 1155) — but it exists nowhere in §7 as an edge case, and §7 carries no note explaining the reassignment. Anyone cross-referencing the plan (or a downstream page citing "view-orders E-6") resolves to the wrong situation.

**Fix (either is acceptable, the first is preferred):**
(a) Move the occupied-location entry to a free ID (`E-93`) and restore `E-6` in §7.1 as the Coupang `[V1]` entry, wording: *"A Coupang QR scan arrives wrapped as `[V1]{barcode}` | The wrapper is stripped before matching; the bare and wrapped forms resolve identically `[BR-2]`; `[DC-1]` records both `raw_value` and `normalized_value`."* Update the three `[E-6]` citations (lines 492, 1026, 1524) to `[E-93]`, and add QA-SC-02's key list `[E-6]`. Update §7's preamble inventory to "93 IDs across 92 entries".
(b) If renumbering is refused, add one line to §7's preamble: *"`E-6` differs from `view-orders.B.md`'s E-6 (Coupang `[V1]` normalization), which was absorbed into `[BR-2]` and QA-SC-02 rather than kept as an edge case."*

---

### 2. `[G-*]` rule bodies restated in four `[BR-*]` rows — **MINOR**

**Location:** §4, lines 708–711 — `BR-33`, `BR-34`, `BR-35`, `BR-36`.

**Finding.** Line 6 of the spec claims *"this document states **page deltas only** and never restates a rule body"*; `_review.md` §3.5 makes that binding. Four rules break it with no delta content:

- `BR-33` "Comments on this page are **append-only** — no edit, no delete." ← `[G-7]` bullet 1 verbatim-equivalent.
- `BR-34` "Every confirming action is double-click safe (client debounce **and** server idempotency key). The known current-admin bug … **must be fixed, not reproduced**" ← `[G-9]` verbatim-equivalent.
- `BR-35` "v1 has a single admin role; no action on this page is role-gated; the actor is recorded on every mutation." ← `[G-15]` verbatim-equivalent.
- `BR-36` "Korean product, carrier, and supplier names are **data** and are never translated." ← `[G-6]` bullet 4 verbatim-equivalent.

(Contrast `BR-30`, `BR-31`, `BR-51`, `BR-32`, which each cite a G-rule *and* add a real page delta — those are correct.)

**Fix:** reduce each of the four to its page-scoped delta plus the citation, or delete the row and cite `[G-n]` at the §3 blocks that depend on it. Minimum acceptable: `BR-35` → *"No page delta on `[G-15]`: no control on this page is role-gated."*; `BR-33` → *"No page delta on `[G-7]`'s append-only clause; every comment surface here (`[L-S1-11]`, `[L-S1-19]`, `[L-S1-3]`, State 6 request comments) inherits it."*; same shape for `BR-34`/`BR-36`.

---

### 3. `[L-S1-F(a)]` / `[L-S1-F(b)]` key format deviates and is undeclared — **MINOR**

**Location:** lines 50, 179, 555, 935, 2064 (five uses of `[L-S1-F(a)]`/`[L-S1-F(b)]`); §2.1 line 71 declares only `[L-S1-F]`, `[L-S5-F]`, `[L-S6-F]`.

**Finding.** `_review.md` §2c-4 fixes the standard as `[L-{state}-F]` **"(suffix a/b/c when a footer holds multiple rules)"** — i.e. `[L-S1-Fa]`, not `[L-S1-F(a)]`. Parenthesised sub-keys are a third form. Compounding it, §2.1's unit declaration lists only the three bare footer keys, so the sub-keys are used in five places but never declared — exactly the phantom-hole condition §2.1 exists to prevent.

**Fix:** rename all five occurrences to `[L-S1-Fa]` / `[L-S1-Fb]` and add to §2.1: *"`[L-S1-F]` holds two rules and is sub-keyed `[L-S1-Fa]` (single-item auto-print) and `[L-S1-Fb]` (unrecognized-scan routing); the sub-keys are not additional units."*

---

### 4. Shorthand date `07-09` in §10.1 status cell — **MINOR**

**Location:** §10.1, line 2057 — `… | proposed 07-09 → **adopted 2026-08-03** \`[PD-10 · OWNER-PENDING]\` (**WF-3**) |`

**Finding.** `_review.md` §3.7: *"Dates: `YYYY-MM-DD` everywhere (Decision Logs, BR rationale, conflict citations). No `07-23` shorthand in final specs."* This is the only shorthand date in spec prose — the 11 other `MM-DD` matches in the file are all inside byte-quoted wireframe UI copy (`Received Date 07-26 14:02`, `Requested by Sara(CS) 07-13 09:20`, `Expected arrival 07-18`) or location codes (`A-05-11`, `B-02-07`), which are data and correctly left verbatim. `BR-10` (line 688) already writes the same fact correctly as *"proposed 2026-07-09, adopted 2026-08-03"*, so the two rows disagree in style on identical content.

**Fix:** change to `proposed 2026-07-09 → **adopted 2026-08-03**`.

---

### 5. `QA-CV-22` carries no tier tag — **MINOR**

**Location:** §8.13, line 1943 — `**QA-CV-22 — DEFERRED** \`[E-63]\` \`[PD-66]\``

**Finding.** `_review.md` §2c-5: *"QA tier tags … standard is **[WF] / [ADMIN]** only."* Every one of the other 272 scenarios carries exactly one. QA-CV-22 carries neither, so a tag-driven runner either skips it silently or errors. The row's *content* is right (a NO-DEFAULT PD must not get an assertion), and §8.14 counts it honestly as a separate DEFERRED line — this is purely a tagging gap.

**Fix:** `**QA-CV-22 [ADMIN] — DEFERRED**` and add one clause to §8.0's Tags paragraph: *"A third marker, `— DEFERRED`, means the scenario has no assertion because it is blocked on an owner decision; it is counted but never executed."*

---

### 6. `QA-S6-07` tagged `[WF]` but declared expected-to-fail — **MINOR**

**Location:** §8.7, line 1465 — `**QA-S6-07 [WF]** \`[L-S6b-1]\` \`[BR-24]\` **WF-1** — *negative, known wireframe defect*`

**Finding.** §8.0 defines `[WF]` as *"executable against the live wireframe **today**"*, and §8.0-step-note points a runner to **§2.3** for known non-bugs. This scenario asserts `#s6b .donebanner` must NOT contain `Carrier recorded automatically` — verified against the wireframe (HTML line 1401 contains exactly that string), so the assertion **will fail today**. Its failure is defect **WF-1**, which lives in **§2.4**, not §2.3, so a runner following §8.0 literally files a false bug against the spec. The scenario body does say so in prose, but the tag and the §8.0 protocol do not.

**Fix:** either retag `[ADMIN]` until WF-1 is applied, or extend §8.0's Tags paragraph: *"Read §2.3 **and §2.4** before filing any `[WF]` failure. One `[WF]` scenario (QA-S6-07) asserts the corrected behavior of a known wireframe defect and is expected to fail until WF-1 ships."*

---

### 7. `"8 slash-groups covering 11 literal names"` — count is 9, not 8 — **MINOR**

**Location:** §5 preamble, line 739.

**Finding.** The sentence then lists the groups: `comment.posted` · `comment.mention_notified` · `comment.starred`/`comment.unstarred` · `comment.read`/`comment.mark_all_read` · `comment.auto_posted` · `product.barcode_registered` · `order.status_changed` · `order.outbounded` · `print.job_result` = **9 groups**, 11 literal names. Independently confirmed: **9** DC rows carry the ⓒ marker (DC-8, 9, 17, 19, 20, 21, 22, 23, 29 — 10 total `ⓒ` glyphs, one of which is in this preamble). The "11 literal names" half is correct; only the group count is wrong.

**Fix:** `**9 groups covering 11 literal names**`.

---

## 3. What was verified and found clean (no action)

Recorded so a later pass does not re-derive these.

- **Legend enumeration.** 56 rendered `.dot` spans (48 state + 8 modal) + 2 dot-less legend entries (`S4-3`, `S4-4`, which say so on screen) = 50 state legend units; matches §2.1 exactly, including the declared quirks (no dot 21 in S1; dot 21 lives in S1b; S1 source order renders `…19, 22, 20`).
- **Off-screen footers.** Exactly 3 legends carry a trailing `<p>` (S1/S5/S6); S0, S1b, S2, S3, S4, S6b carry none — §2.1's parenthetical is literally true.
- **Demo limitations §2.3.** L-3 (`#scanfloat` only inside `#s1`) ✓ · L-4 (`.logsec` in s1/s2/s3/s4/s5, absent in s1b) ✓ · L-8 (`.row-hit` is the **second** `tbody` row) ✓ · L-11 (sound bound by `/Outbound/.test(tx) && !/Cancel/ && !/Outbounded/`) ✓ · L-13 (`.flsave` attached to `.shelf input, .locin` only) ✓ · L-14 (`.row-done` `input.qtyin` is `readonly`) ✓ · L-15 (`Full list: Inbound Request → Request List` is plain text, not an anchor) ✓.
- **Byte-exact UI copy.** Search placeholder, `Waiting for scan` panel, `▸ Expected Inbound 4 — 2 with tracking · 1 Partial Inbound`, badge row order (`202608020001`, `202607120001`, `202608020002`, `202608010004`), `Max 20 on screen · full history in backend`, `Found {n} item(s) in this order · Found {m} order(s)`, M5's three reason options, M6's three reason options, M1's `Default = qty that was inbounded (editable) · disabled when "No" is selected`, M4's carrier chips and preview lines (`Dr.Jart+ 포어레미디 리뉴잉 폼 클렌저 · 150ml · 1개`) — all match the shipped HTML.
- **`[L-F3]` scope claim.** Order `🖨 Print` verified present in s1, s1b, s2, s3, s5 and **absent in s4** — exactly as specced.
- **§2.2 state map.** All 16 chrome-bar button labels byte-exact against HTML lines 265–280.
- **§8.14 key-free exceptions.** Exactly 3 scenarios have no key in their header: QA-NG-09, QA-CV-20, QA-CV-21 — precisely the three §8.14 names.
- **Delta-from-v1.0 notes.** §2.1 (67→69 units), §5.11 (46→47 events), §9.2 (30→32 PDs) are internally consistent with the derived totals.
