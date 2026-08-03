# M1 — Coverage Audit: `closing.md`

Independent verification (auditor did not author the spec). Date: 2026-08-03.
Target: `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md` (2,219 lines)
Wireframe: `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/closing/index.html` (910 lines)

Every count below was derived by running extraction scripts over the HTML and the markdown. No count asserted by the spec was accepted on its face.

---

## Verdict table

| # | Check | Verdict | Evidence (derived independently) |
|---|---|---|---|
| 1 | **Legend coverage** | **PASS** | Regex over `index.html` yields **21** `span.dot` elements — s0:1 · s1:11 (`7,9,11,10,1,3,2,4,6,5,8`) · s2:1 · s2b:1 · s3:1 · s4:3 · shist:1 · `#m-process`:`M1` · `#m-scandel`:`M2` — plus exactly **1** normative `.legend > p` footer inside `#s1` = **22 units**. §2.1 declares 22 with the same distribution. All 22 have a `### 3.x [L-…]` anchor (22 anchors extracted); the 4 furniture keys `[L-F1]`…`[L-F4]` are specified in §3.0.1 and correctly declared as *not* part of the 22. Nothing is specified nowhere. |
| 2 | **Plan coverage** | **PASS** | closing.A §3a lists 18 data-capture events; all 18 map 1:1 onto DC-1/3/5/7/10/20/12/13/15/11/21/24/25/17/18/19/9/6, with 7 additions (DC-2/4/8/14/16/22/23). A's "explicitly NOT persisted" trio (voice-test plays, TTS playback, focus/refocus) all appear in §5.3. closing.B §3a lists 50 edge cases (E-1…E-50); all 50 exist in §7 as table rows with **matching conditions and unchanged IDs** (E-41/E-42/E-46…E-50 keep their out-of-reading-order positions, declared in §7's preamble). 0 silent drops. |
| 3 | **QA integrity** | **FAIL** | Counts verified exactly: **168 scenarios**, **68 `[WF]` / 100 `[ADMIN]`** (0 untagged, 0 duplicate IDs, no numbering gaps in any block), **68 negative = 40.5 %** (≥25 % required). Per-block tallies match §8.16 row-for-row. All **25** DC events have ≥1 scenario body naming them. All QA IDs cited in §8.16–8.18 exist. All `[L-*]` keys used in §8 are declared (one malformed composite, defect 4). **But** §8.18's heading claim "every `[E-n]` has an asserting scenario" is false for 6 edge cases (defect 1). |
| 4 | **PD discipline** | **PASS (minor)** | 20 PDs cited: 1,2,3,4,5,6,7,8,60,68,69,70,71,72,73,74,75,76,77,78. Spot-checked 12 against `_provisional-decisions.md` — PD-1 (single admin role), PD-2 (send sound by button class), PD-3 (append-only comments), PD-4 (Slack failure never rolls back), PD-5 (destructive → confirm+toast), PD-6 (server revalidate at confirm), PD-7 (merge for counting flows), PD-8 (separate tracking namespaces), PD-68 (CSV-only), PD-70 (one session per confirmed date), PD-73 (scan locked after confirm), PD-77 (Zero Packing mandatory) — **all 12 match meaning exactly**. Also verified PD-60 (a tracking-missing PD) is cited only as a deliberate contrast in §3.22/§3.23, not as closing behavior. The two NO-DEFAULT PDs (71, 74) are **never** presented as decided: both appear untagged, are stated as open in §6.4/§3.17/§3.23, and are the only two rows in §9.2. Minor: §8 cites PDs without the `· OWNER-PENDING` suffix (defect 5). |
| 5 | **Convention compliance** | **PASS (minor)** | Key format normalized to the `_review.md` §2c standard: `[L-S1-8]` (not `[L-1.8]`), `[L-S1-F]` (not `[L-1.B]`), `[L-SH-1]`, `[L-M1]`/`[L-M2]`, `[L-F1]`…`[L-F4]`. QA tier tags are `[WF]`/`[ADMIN]` only — 168/168, zero `WF-RUN`/`ADMIN-ONLY`/`[REAL-ADMIN]` survivals. IDs continuous and non-renumbered: E-1…E-77 (77 rows, 0 missing), BR-1…BR-37, DC-1…DC-25, all gaps explained in §7's preamble and §2.1. Dates are `YYYY-MM-DD` everywhere; the only `MM-DD` strings are 6 backticked byte-exact assertions of wireframe demo data (`07-13 (today)`, `07-12`…) — required by convention 9, not a violation. Slack: `#fulfillment-admin-comments` (`C0BMGEWM5QA`) carries its ID at every mention; `#unrecognized-tracking` has no ID in `_slack-routing.md` to carry. Korean-as-data rule cited [G-6] §10. Removed features carry 22 explicit "must NOT exist" rows in §3.23, each dated. Minor: one malformed key (defect 4). |
| 6 | **Global-rule hygiene** | **PASS (minor)** | 13 G-rules cited ([G-1,2,3,4,6,7,8,9,10,11,12,13,15]); [G-5] and [G-14] correctly absent (no sourcing-route or location surface on this page). Deltas are written as deltas — §3.2 "Closing deltas to [G-1] (the three [G-1] invariants are untouched)", §3.4 "page delta to [G-3b]", §3.8 "Behavior is global [G-7]; only the closing deltas are specified here". Every deviation is declared with rationale and date: [G-4] non-landing → §6.5 + BR-24 + §3.23, dated 2026-08-03, PD-68/GD-9; [G-3a] scope-by-class → §6.6 + §3.21 step 5, dated 2026-08-03, PD-2, with the reversal impact stated. Minor: one paraphrase of the [G-1] body in §1.3 (defect 6). |
| 7 | **Adjudication compliance** | **PASS** | Every `_review.md` C-item touching closing is honored: **C-4** (CSV-only, [G-4] off this page) → §6.5, BR-24, §3.23, §9.1, §10; **C-5** (send sound by button class) → §6.6, §3.21 step 5, with PD-2's page-enumeration tension surfaced for the owner rather than silently resolved; **C-6** (Start-with-invalid-input gets an explicit error) → §3.1 validation table + WF-8; **C-10** (no large red panel anywhere) → §3.3, §3.14, §3.23, and QA-CONFIRM-03 asserts `.bs-warn` count === 0 document-wide; **C-12** (canonical event names) → §5.1 uses `order.status_changed`, `order.outbounded`, `comment.posted`/`auto_posted`/`mention_notified`/`starred`/`unstarred`/`read`/`mark_all_read` byte-identically, and declares `print.job_result` + `product.barcode_registered` as NON-events; adjudicated non-issue (closing "unknown" ≠ unrecognized pool, non-route stated explicitly) → BR-23, §3.15 boundary table, §6.1 non-routes, QA-UNKNOWN-05. `_review.md` §2c items 1, 4 and 5 all applied. All 5 wireframe defects touching this page (`WF-4/5/7/8/12`) are registered in §2.3 and each points at the §3 section carrying the correct behavior — **no stale wireframe text is specced as truth** (State 1 legend #2 and State 4's "(M2)" are both explicitly contradicted, not inherited). |

---

## Defect list

### 1. `[MAJOR]` §8.18 heading claim "every `[E-n]` has an asserting scenario" is false for 6 edge cases

**Location:** §8.18 heading (line 2070) — "*Edge-case traceability (every `[E-n]` has an asserting scenario)*" — and the mapping rows for E-37, E-52, E-60, E-66, E-74, E-77.

**Evidence.** Twelve E-ids are never named inside any scenario body (E-4, 6, 26, 37, 47, 49, 51, 52, 60, 66, 74, 77). Six of those are nevertheless covered semantically by the mapped scenario (E-4 → QA-VERDICT-03; E-6 → QA-DUP-01/04; E-26 → QA-DEL-02/03/05 + QA-COUNT-05; E-47 → QA-HUB-05/06; E-49 → QA-CONFIRM-05 asserts no "Print" text anywhere). **Six are not.** Keyword scan of the whole of §8 returns zero hits for `idempotency`, `MKT`, `marketing`, `new tab`, `_blank`, `autofill`, `composition`, `several hundred`, `virtualiz`, `paginat`, `zero-line`:

| E | Condition (§7) | Mapped scenario | What that scenario actually asserts |
|---|---|---|---|
| E-37 | Network failure on **Confirm**; retry with the same idempotency key → exactly one closing record + one sheet update | QA-PERSIST-04, QA-CONFIRM-14 | QA-PERSIST-04 = **simultaneous** confirms (that is E-31); QA-CONFIRM-14 = CSV export + its failure mode. Neither tests retry-after-timeout. |
| E-52 | Order found but zero line items → `Items` renders `0`, still OK if `Prepare Shipment` | QA-VERDICT-06 | asserts only that `Prepare Shipment` → `verdict=ok`. No zero-item assertion. |
| E-60 | Scan list grows to several hundred rows; latest row stays visible; pagination default | QA-COUNT-12 "(scale behavior)" | QA-COUNT-12 deletes 12 rows and checks counters go to zero. Unrelated to scale. |
| E-66 | A marketing / `MKT-` order's tracking is scanned → no special handling | QA-VERDICT-07 | asserts abnormal *statuses* (`Shipped`/`Cancelled`/…). Marketing orders never appear. |
| E-74 | Order ID deep link opens in a **new tab**; the closing session survives | QA-HUB-08 "(focus survival), §6.3" | asserts the Comments hub does not break the scan loop. No link/new-tab assertion anywhere in §8. |
| E-77 | Autofill / spell-check / IME composition intercepts a wedge burst; submit waits for composition end | QA-SCAN-15 "(terminator handling), §3.2" | asserts Tab-terminated and unterminated reads. No composition/autofill assertion. |

E-51 (a scan lands while a target edit is open) is **partially** covered: QA-SCAN-12 covers the refocus-exclusion clause, but nothing asserts "the scan is processed normally" or "counters recompute against the **saved** target".

**Why it matters.** E-37 is the only guard against a double closing record and a double SS Daily Shipping Status append. The behavior is specced (§3.9 step 1, §6.4 clause 2) but untested, and the traceability table asserts otherwise — a QA agent trusting §8.18 will ship without that test.

**Fix required.** Add 6 `[ADMIN]` scenarios (and 1 clause to a `QA-TARGET` scenario for E-51), then update §8.16's per-block E lists, the block totals, the grand total and the negative-test share:
- `QA-CONFIRM-16 [ADMIN] (negative)` `[E-37]` — Given a confirm whose response is lost; When the client retries with the same idempotency key; Then exactly one **DC-21**, one **DC-23** and one **DC-24** exist and the second call returns the confirmed state.
- `QA-VERDICT-15 [ADMIN]` `[E-52]` — a `Prepare Shipment` order with zero line items scans `ok` and its `Items` cell renders `0`.
- `QA-COUNT-13 [ADMIN]` `[E-60]` — with 400 rows the newest row stays visible, focus is not stolen, and (if paginated) the latest page is the default.
- `QA-VERDICT-16 [ADMIN]` `[E-66]` — an `MKT-` order is judged purely on status, with no exclusion.
- `QA-HIST-11 [ADMIN]` `[E-74]` — clicking an `Order ID` while `IN_PROGRESS` opens a new tab; the closing tab keeps focus, scan input and session.
- `QA-SCAN-17 [ADMIN] (negative)` `[E-77]` — a composition event during a wedge burst defers the submit to composition end; no partial string is submitted and no **DC-7** is written.
- Extend `QA-TARGET-04` (or add `QA-TARGET-14`) with `[E-51]`: a scan submitted while the edit field is open is processed normally and counters recompute against the saved target.

Alternatively, if these are deliberately deferred, weaken the §8.18 heading to "*every `[E-n]` is mapped; rows marked ⊘ are specified but not yet scenario-covered*" and mark the six rows — but silent over-claim is not acceptable.

---

### 2. `[MINOR]` §8.0 points at the wrong traceability tables

**Location:** §8.0, "Reading a scenario" paragraph (line ~1073):
> "§8.16 proves every event in §5.1 has at least one asserting scenario and §8.17 does the same for every `[E-n]`."

**Evidence.** §8.16 is the coverage summary + legend-unit table; §8.17 is the data-capture traceability table; §8.18 is the edge-case traceability table. Both pointers are off by one.

**Fix required.** Replace with "…§8.17 proves every event in §5.1 has at least one asserting scenario and §8.18 does the same for every `[E-n]`."

---

### 3. `[MINOR]` Divergence U-a under-scopes the bad demo number `79`

**Location:** §2.3, bullet **U-a** (line ~107) — names only the "Remaining scans" tile and the `.proglab` sentence.

**Evidence.** `index.html:397` renders the Confirm button as `Confirm Closing (79 remaining · 2 warnings)`. §3.9 quotes exactly that string as "wireframe example, **byte-exact**" and QA-CONFIRM-01 asserts it byte-exact — while §3.5's own formula gives `remaining = max(0, 84 − 3) = 81`. The same bad datum therefore appears in three places, only two of which are flagged. A developer reading §3.9's worked example will infer `remaining = target − ok − warnings`.

**Fix required.** Extend U-a to: "…the same `79` also appears in the Confirm Closing button label (`index.html:397`); §3.5's formula (81) is authoritative and §3.9's quoted string is demo data, not a worked example." Add a one-line note under §3.9's byte-exact quote pointing at U-a.

---

### 4. `[MINOR]` Malformed legend key `[L-S4-1..3]`

**Location:** §8.11 block heading (line 1702) and the §8.16 coverage-table row for QA-CONFIRM.

**Evidence.** Extracting every `[L-…]` token from §8 yields one key that is not in the declared set of 26: `S4-1..3`. `_review.md` §3 convention 1 fixes the format as `[L-{state}-{n}]`; a range composite defeats a mechanical key-existence check (my own extractor flagged it).

**Fix required.** Replace both occurrences with the enumerated keys `[L-S4-1]` `[L-S4-2]` `[L-S4-3]`.

---

### 5. `[MINOR]` PD citations in §8 drop the `· OWNER-PENDING` tag

**Location:** 14 QA scenario headings — QA-VERDICT-07 `[PD-76]`, QA-VERDICT-11 `[PD-8]`, QA-DUP-07 `[PD-75]`, QA-DUP-08 `[PD-69]`, QA-TARGET-05 `[PD-5]`, QA-M1-05 `[PD-77]`, QA-M1-13 `[PD-2]`, QA-CONFIRM-11 `[PD-6]`, QA-CONFIRM-12 `[PD-73]`, QA-HIST-09 `[PD-70]`, QA-PERSIST-09 `[PD-78]`, QA-PERSIST-10 `[PD-70]`, QA-PERSIST-11 `[PD-4]`, plus §9.2/§9.3 pointers.

**Evidence.** `_review.md` §3 convention 8 requires PD-resting behavior to be tagged `[PD-{n} · OWNER-PENDING]` at the sentence; a QA scenario asserts behavior. The bare form is also the form the spec correctly uses for the two **NO-DEFAULT** PDs (`[PD-71]`, `[PD-74]`), so the two states are indistinguishable at a glance in §8 — a reader cannot tell "provisionally adopted, will be tested" from "deliberately unspecified".

**Fix required.** Either append `· OWNER-PENDING` to all 14 provisional citations in §8, or add one line to §8.0: "PD references in scenario headings are shorthand; the owner-pending status is carried at the §3/§7 sentence that defines the behavior. `[PD-71]` and `[PD-74]` are NO-DEFAULT and are never asserted."

---

### 6. `[MINOR]` §1.3 restates a global-rule body

**Location:** §1.3, line 39:
> "Hence [G-1]: the cursor lives in the scan input, the page never refreshes, and no click is ever required between scans."

**Evidence.** That sentence is a paraphrase of all three [G-1] invariants. `_global-rules` header and `_review.md` §3 convention 5 both require specs to "cite these by ID and describe page deltas only — they never restate a rule body". §3.2 handles [G-1] correctly ("the three [G-1] invariants are untouched"); §1.3 is the sole lapse.

**Fix required.** Reduce to "Hence the three [G-1] invariants, which this page inherits unchanged (deltas in §3.2)."

---

### 7. `[MINOR]` E-35 double-keyed and E-74 omitted in the §8.16 block table

**Location:** §8.16 coverage table, rows QA-SCAN and QA-PERSIST and QA-HUB.

**Evidence.** QA-SCAN's "Keyed to" column lists `E-35`, and QA-PERSIST's lists `E-30…38` which swallows the same `E-35`; §8.18 maps E-35 to QA-SCAN-10 only. Conversely QA-HUB's row lists only `E-47/75` while §8.18 maps `E-74` to QA-HUB-08. The two tables disagree about which block owns which edge case.

**Fix required.** Change QA-PERSIST's key list to `E-30…34/36/38/41/53/59/62/71` and add `E-74` to QA-HUB's list once defect 1 is resolved (or move E-74 to whichever block gains its new scenario).

---

## Defect counts

| Severity | Count |
|---|---|
| BLOCKER | 0 |
| MAJOR | 1 |
| MINOR | 6 |
