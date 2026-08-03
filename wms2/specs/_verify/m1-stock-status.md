# M1 — Coverage Audit · `stock-status.md`

Method: independent verification. Nothing in the spec's own counts was trusted; every number below was re-derived by script over `wms2/stock-status/index.html`, `specs/stock-status.md`, and the four `_plans/` registers. Auditor did not write the spec.

Target: `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/stock-status.md` (1302 lines, v1.1, 2026-08-03)
Wireframe: `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/stock-status/index.html` (662 lines)

---

## 1. Verdict table

| # | Check | Verdict | Basis (independently derived) |
|---|---|---|---|
| 1 | **Legend coverage** | **FAIL** | 16 `span.dot` found (`16,10,5,6,14,8,9,7,15,12,11,13,M2,M3,M4,M1` in source order), 12 legend `<li>`, 6 `.overlay`, 4 `.pane`, 1 off-screen normative footer `<p>`. §2.1 declares 16 legend + 4 furniture = 20; §3.1–§3.20 = 20 sections, all keys mapped, every DOM id/class cited in the spec exists in the HTML (0 dangling selectors). **But** the normative footer names *five* carried-over units and only four are keyed — **Global nav (`.nav`) is specified nowhere.** |
| 2 | **Plan coverage** | **FAIL** | A-plan `DC-1`–`DC-23` → spec `DC-1`–`DC-23`, same IDs and semantics (canonical renames applied per C-12). B-plan `E-1`–`E-50` → spec `E-1`–`E-50`, ID-for-ID, zero renumbering. All 5 A-plan OQs + all 8 B-plan OQs land as `PD-40`–`PD-50` / `PD-1`. All B-plan dev-time decisions carried into §9.2. All 9 A-plan operator-flow notes present. **One silent drop: "global nav", named in *both* plans' baseline-unit lists** (A §1 tail; B §1 "must still be functionally specified in §3"). |
| 3 | **QA integrity** | **FAIL** | 194 scenarios, 0 duplicate IDs. `[WF]`/`[ADMIN]` = **73/121** — matches the claim exactly. Per-block NAV 10 · CS 18 · LOC 18 · AUD 43 · LOG 9 · RES 26 · HIS 18 · FRM 19 · COM 15 · EXP 6 · GLB 12 — matches exactly. Negative/boundary = 81 `NEGATIVE` + 1 `BOUNDARY` = **82 = 42.3 %** (≥ 25 %) — matches exactly. All 34 `[DC-n]` have ≥ 1 persistence-asserting scenario; all §8.1-referenced QA IDs exist; every `[L-*]` used in QA is declared and every declared key is used; no `[WF]` scenario asserts a server-only effect. **But 3 of 98 `[E-n]` are referenced by no scenario: `E-11`, `E-69`, `E-70`.** |
| 4 | **PD discipline** | **FAIL** | 31 distinct PDs cited. Every behavior sentence carries the full `[PD-n · OWNER-PENDING]` tag; the only bare `[PD-n]` forms are inside the §9.2 reversal index and one Decision-Log cross-reference. NO-DEFAULT items `PD-51/55/66/71/74/79` appear only as "owned by other screens" pointers — no behavior specified. Spot-checked 15 against the register (PD-2, 8, 9, 13, 22, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 80): 14 match. **`PD-47` does not match: the register fixes `"SKUs Checked" = rows in that scope`; the spec widens it.** |
| 5 | **Convention compliance** | **FAIL** | Key formats correct (`[L-{n}]` plain + `[L-M{n}]`/`[L-M2b]`/`[L-F{n}]`, style declared with rationale in §2.1); `E`/`DC`/`BR` all contiguous with no gaps; dates are `YYYY-MM-DD` everywhere (the 17 `MM-DD` occurrences are all byte-accurate wireframe fixture strings, which convention 9 requires); Slack notation carries `#fulfillment-admin-comments` (`C0BMGEWM5QA`) at first mention; Korean data strings kept verbatim (`— (신규)`, KR product names, `힣` sentinel); 15 removed features carried as explicit "must NOT exist" rows in §9.1, each with a §10 row and an asserting scenario. **But the `BR-n` family was silently renumbered off the A-plan.** |
| 6 | **Global-rule hygiene** | **PASS** | `[G-1]`–`[G-15]` all cited by ID; no rule body is reproduced as page behavior. Deviations are declared as page deltas with rationale + date: §6.4 (`G-4` does not land here, 2026-08-03, `BR-27`), §6.5 (`G-3(a)` yes / `G-3(b)(c)` no), §9.1 #11 (`G-1` scoped away, 2026-08-03). Minor hygiene slip only — 5 `BR` rows paraphrase G-bodies instead of citing (D8). |
| 7 | **Adjudication compliance** | **PASS** | All 6 applicable `C-*` honored: C-1 → `BR-33` (boundary, not removal — carrier column and both selects stay as manual values); C-2 → §6.1 channel + ID + payload verbatim; C-3/`PD-80` → `BR-8`, §3.1 filter, §6.2; C-5/`PD-2` → §6.5; C-6/`PD-5` → §3.3 exit dialog + §3.16 guard; C-12 → canonical `product.barcode_registered` / `comment.mention_notified`. All four "adjudicated non-issues" declared, not re-flagged (dots start at 5; `m-auditlog`/`m-adjlog6` dotless; `WF-14` cited as optional). No stale wireframe text is specced as truth — the M1 note's hard-coded `"the 3 new additions"` is templatized to `{n}` in §3.13 and quoted verbatim only inside a `[WF]` assertion. |

**Independent spot-verification of `[WF]` fixture claims (all confirmed against the DOM):** 11 data rows in `Available`-desc order `82,61,55,34,23,16,11,6,4,2,1`; `.loc-in` values in default order `B-02-03, A-03-02, B-01-07, A-02-13, C-01-05, A-01-04, A-01-05, A-02-20, C-02-01, (empty), B-03-02`; audit prefill census — exactly two non-matching rows (`100005104` 17/18, `100012534` 11/9), other nine equal; `−15,000 + 61,260 = +46,260` reconciles with `#auditSummary`; 3 Past-Audit-Log rows; 6 Stock-History rows in the stated order; 3 unread comment entries (`409112`, `407847`, `407506`); 10 `.wf-tab` + 1 `.wf-toggle`; `힣` sentinel present in the sort comparator; `print` = 0 occurrences, `sample` = 0, `photo` = 0, `input[type=file]` = 0.

---

## 2. Defect list

**0 BLOCKER · 2 MAJOR · 7 MINOR**

---

### D1 · MAJOR · Global nav is an implementation unit that is specified nowhere

**Location:** §2.1, line 64 — *"**Plus 4 page-furniture units** carried over from the live admin screen (legend footnote: *"Global nav · Export Stock Status · Search dropdown · Inbound/Outbound forms · event columns … stay as on the live screen"*). These are **not** legend units but **are** implementation units and are keyed `[L-F1]` – `[L-F4]`."*

The quoted footer names **five** carried-over units. Four get keys (`[L-F1]` search, `[L-F2]` inbound form, `[L-F3]` outbound form, `[L-F4]` export) and "event columns" is covered under `[L-8]` §3.4. **Global nav gets no key and no §3 section.** Derived evidence: the spec contains 0 occurrences of `Logout`, `Operation AI`, `Catalog Management`, `OMS Center`, `Yongwon Ryu`, `avatar`, or `.navlink`; the wireframe's `.nav` renders `SkinSeoul` brand + 6 category dropdowns + 4 `.navlink` tiles (`Agent Telemetry`, `Role Assets`, `Shared Asset Health`, `SkinSeoul WP Admin`) + the user chip + `Logout`. Only the `💬 Comments` button inside that nav is specified (as `[L-16]`).

This is not a program convention — it is an outlier. Sibling specs all key it: `view-orders.md` line 644 `[L-F1] Global navigation bar and session identity`; `order-detail.md` line 726 `[L-F17] Global nav + Logout`; `closing.md` line 135 `[L-F1] Global nav`; `ready-to-outbound.md` line 116 `[L-F8] Global nav + signed-in identity`. Both plans required it: `stock-status.A.md` §1 tail ("Also present but not legend-numbered (spec must still cover): … global nav") and `stock-status.B.md` §1 ("Baseline carried-over units (legend footnote — must still be functionally specified in §3): global nav · …").

**Fix:** add `[L-F5] Global nav + signed-in identity` to §2.1 (raise the furniture count to 5 and the §3 unit total to 21), add a §3.21 specifying the nav items verbatim, the actor source for `[G-8]` (`Yongwon Ryu` / the signed-in user), `Logout` behavior, and a `NON-event` declaration for navigation clicks (§5.3); add one `[WF]` scenario under `QA-NAV` asserting the nav item census. Follow the `ready-to-outbound.md [L-F8]` pattern (nav = the actor source for every §5 event), which is the closest match to this page's needs.

---

### D2 · MAJOR · `BR-35` widens `PD-47`'s pending definition of `SKUs Checked` and is untagged

**Location:** §4, line 586 — *"| **BR-35** | **`SKUs Checked` = rows in the recorded scope + rows added via `[L-13]` during the session.** | … | 2026-08-03 |"* · propagates to `QA-AUD-40` (line 994, *"a scope of 9 rows and 2 rows added via `[L-13]`, **Then** `[L-15]` `SKUs Checked` reads `11`"*).

`_provisional-decisions.md` `[PD-47]` reads: *"The session records its scope (the filtered set at session start), and **'SKUs Checked' = rows in that scope**."* `[L-13]` additions are, by construction, **not** in the scope recorded at start, so `BR-35` produces a different number than the register the owner will be asked to approve. §3.11 (line 327) does tag this sentence `[PD-47 · OWNER-PENDING]`, but the canonical rule row `BR-35`, its scenario `QA-AUD-40`, and the §9.2 reversal index (line 1207: *"`[PD-47]` filtered audits and scope (`[BR-15]`, `[BR-34]`)"* — `BR-35` absent) all omit it. That breaks the spec's own reversal contract: *"Reversing any one means editing the sentences tagged with that ID on this page and nothing else."*

**Fix:** either (a) tag `BR-35` and `QA-AUD-40` `[PD-47 · OWNER-PENDING]` and add `[BR-35]` to the §9.2 PD-47 index entry, **and** amend the `PD-47` register entry to state the extension explicitly; or (b) raise a new register entry (`PD-87`) for "do `[L-13]` additions count toward `SKUs Checked`?", tag `BR-35`/`QA-AUD-40`/§3.11 with it, and list it in §9.2. Option (b) is preferred — it is a distinct owner question, not a restatement of PD-47.

---

### D3 · MINOR · `BR-n` IDs silently renumbered off the A-plan ("never renumber")

**Location:** §4 (whole `BR-1`–`BR-36` table) vs `_plans/stock-status.A.md` §"Business rules" (`BR-1`–`BR-16`).

`_review.md` §3 item 2 is binding: *"business rules `[BR-{n}]` — all page-scoped, stable once assigned … **Never renumber.**"* The spec preserved the other two ID families verbatim (`E-1`–`E-50` from lens B, `DC-1`–`DC-23` from lens A) but remapped the third with no note: A `BR-2`→spec `BR-3` (ADJUST = book correction), A `BR-7`→`BR-13` (reserved-shortage gate), A `BR-8`→`BR-16` (outbound > Available), A `BR-9`→`BR-10` (sort), A `BR-10`→`BR-20` (restock default), A `BR-12`→`BR-9` (colorless routes), A `BR-13`→`BR-25` (name autocomplete), A `BR-16`→`BR-19` (phantom predicate). A `BR-11`/`BR-14`/`BR-15` were absorbed into `[L-10]` / `[G-9]` / `[G-2]`.

**Fix:** add a one-line note under the §4 heading: *"`BR` IDs were re-assigned from `stock-status.A.md` on 2026-08-03 to accommodate 20 new rules; mapping: A-2→3, A-7→13, A-8→16, A-9→10, A-10→20, A-12→9, A-13→25, A-16→19; A-11/14/15 absorbed into `[L-10]`/`[G-9]`/`[G-2]`."* Do not renumber again.

---

### D4 · MINOR · `[E-11]` is carried in §7 but referenced by no QA scenario

**Location:** §7.2, line 769 — *"| `[E-11]` | **Audit started while filters are active** | Allowed. The session records the filtered scope `[PD-47 · OWNER-PENDING]`. `[L-15]` must therefore never be read as 'the whole catalog was counted' |"*

`_review.md` §3 item 4 requires QA scenarios "keyed to `[L-*]`/`[E-*]`". `QA-AUD-07` asserts the behavior (*"an `audit.session.started` event `[DC-7]` persists with … the filter state in force, and the scope row count. `[PD-47 · OWNER-PENDING]`"*) but does not carry the `[E-11]` key, so an agent running edge-case traceability finds a hole.

**Fix:** append `` `[E-11]` `` to the `QA-AUD-07` key list.

---

### D5 · MINOR · `[E-69]` and `[E-70]` are referenced by no QA scenario

**Location:** §7.1, lines 758–759 (`E-69` long product name / location truncation; `E-70` narrow viewport / horizontal scroll). Both appear only once more, in the §9.2 developer-decision row *"| Layout | Sticky-header implementation and truncation/tooltip behavior on the wide table `[E-69]` `[E-70]` |"* (line 1227).

**Fix:** either add two `[ADMIN]` layout scenarios under `QA-GLB` (assert `overflow-x` on the table container and `title`/ellipsis on a long value), or mark both edge cases explicitly `— deferred to the layout dev decision, no scenario` in §7.1 so the absence is declared rather than accidental. The first is preferred; `E-70` ("the page body itself must never scroll horizontally") is testable on the shipped wireframe today.

---

### D6 · MINOR · Internal contradiction: route filter option count ("four" vs "five" vs "sixth")

**Location:** §3.1 item 3, line 154 — *"The shipped wireframe's filter predates this decision and **lists only four options** — spec wins"* vs `QA-CS-06`, line 914 — *"the same select additionally offers `OTHER` as a **sixth option** … **The wireframe's five-option list** predates this decision"*.

Derived ground truth: the second `select.sel` in `.cs-controls` holds exactly 5 `<option>`s — `All Sourcing Routes`, `SMART BUY`, `JIT`, `WHOLESALE`, `PARTNERSHIP`. `QA-CS-05` (line 913) asserts exactly that and is correct. Line 154 counts route values only while the QA rows count DOM options; the two readings collide inside one document.

**Fix:** rewrite line 154 to *"The shipped wireframe's filter carries five options (`All Sourcing Routes` + the four routes) and predates this decision; production adds `OTHER` as a sixth option — spec wins; this is a page delta, not a wireframe defect to reproduce."*

---

### D7 · MINOR · Internal contradiction: unread-badge zero state

**Location:** `QA-COM-06`, line 1101 — *"**Then** the nav badge **drops to `0` (or hides)**"* vs `[E-93]` (line 857) and `QA-COM-13` (line 1108) — *"the nav badge is **hidden**, not rendered as `0`"* / *"**NEGATIVE.** … the nav badge is **hidden** rather than rendered as `0`"*, and §3.12 line 339 — *"With zero unread mentions the badge is **hidden**, not rendered as `0` `[E-93]`."*

`QA-COM-06` permits the exact rendering that `QA-COM-13` files as a defect. An agent running both gets a contradictory pass/fail on the same DOM.

**Fix:** change `QA-COM-06` to *"**Then** the nav `.badge-n` is removed/hidden (never rendered as `0`, `[E-93]`), the three entries lose their unread styling, and `comment.mark_all_read` `[DC-23]` persists per user."*

---

### D8 · MINOR · Five `BR` rows restate `[G-n]` bodies instead of citing them

**Location:** §4 — `BR-5` (line 556, restates `G-14` audit-mode-only bullet), `BR-6` (line 557, restates `G-14` dynamic-line bullet), `BR-9` (line 560, restates `G-5`'s *"colorless black bold text, never colored pills"*), `BR-26` (line 577, restates the `G-8` doctrine sentence *"actor + timestamp + entity + old→new + quantity"*), `BR-28` (line 579, restates `G-15`'s single-admin-role body).

`_review.md` §3 item 5 is binding: *"cite `[G-n]` and write page **deltas only** — never restate the rule body."* Each row does cite the G-rule, so the intent is right, but the duplicated text is a silent-divergence path: amend `_global-rules.md` and these five rows keep the old wording with no signal.

**Fix:** reduce each to its page delta and cite. E.g. `BR-5` → *"On this page the audit-mode-only set is exactly `Counted Qty`, `Diff`, `Loss (₩)`, `#auditSummary`, and `.audrow` `[G-14]`."*; `BR-9` → *"Route cells on this page follow `[G-5]`; the page adds no route styling of its own."*; `BR-26` → *"Page delta on `[G-8]`: rejections (`[DC-20]`, `[DC-27]`, `[DC-28]`, `[DC-29]`, `[DC-31]`, `[DC-32]`) are operator-initiated and therefore persist."*; `BR-28` → cite `[G-15]` + `[PD-1]` and keep only the page-specific enumeration (audit start/confirm, reservation release, cost visibility).

---

### D9 · MINOR · Three §8.1 traceability rows cite scenarios that do not carry the `[DC-n]` key

**Location:** §8.1 — line 1150 *"| DC-5 | QA-RES-07, QA-RES-10 |"*, line 1154 *"| DC-9 | QA-AUD-25, QA-AUD-38 |"*, line 1160 *"| DC-15 | QA-LOC-09, QA-LOC-15 |"*.

Derived: `QA-RES-10` cites `[DC-6]` only; `QA-AUD-38` cites `[E-79]` only; `QA-LOC-15` cites `[E-74]` only. (The two other apparent mismatches, `DC-3 → QA-RES-03` and `DC-16 → QA-HIS-07`, are explicitly annotated in the table as *"(view)"* and *"(never emitted here)"* and are correct as written.) No `[DC-n]` loses coverage — each still has a properly keyed scenario — so this is traceability noise, not a hole.

**Fix:** add the missing keys to the three scenarios (`QA-RES-10` → `` `[DC-5]` ``; `QA-AUD-38` → `` `[DC-9]` ``; `QA-LOC-15` → `` `[DC-15]` ``), or annotate the three §8.1 cells the way the `DC-3` / `DC-16` cells already are.

---

## 3. What was verified clean (no defect)

- Unit enumeration, dot→section mapping, and the "no dots 1–4" / dotless-modal declarations (§2.1) — exact against the DOM and against `_wireframe-fixes.md` §E.
- Every DOM id and class cited anywhere in the spec exists in the wireframe (0 dangling selectors, checked mechanically).
- Every closing-summary count is true: 20 units · 36 BR · 34 DC + 12 NE · 98 E · 194 QA (73/121, 82 negative = 42.3 %) · 25 PDs applied · 1 NO-DEFAULT.
- All 12 mandatory matrix items land or are explicitly N/A (`G-1` §9.1 #11, `G-4` §6.4, `G-13` §9.1 #10).
- `[G-8]` non-event doctrine honored (12 declared `NE-*`, each with a reason).
- No `[WF]`-tier scenario asserts a server-only effect; the §8.0 preflight correctly handles the three annotation dots rendered inside content nodes.
