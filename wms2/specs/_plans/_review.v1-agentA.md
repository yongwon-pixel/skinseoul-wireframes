# P3-2 Consolidated Review — WMS 2.0 Spec Plans

Reviewer: consolidation agent (supervisor-assist). Date: 2026-08-03.
Inputs: all 16 plans (`{slug}.{A|B}.md` × 8 pages), `_supervisor-state.md` (rulings applied as-is), `_inputs/` 4 files.
Companion documents: `_provisional-decisions.md` (PD register), `_wireframe-fixes.md`.

---

## 1. Cross-page conflicts (adjudicated)

Verdict rule (per supervisor): **2026-08-03 decisions always win**; wireframe legend notes dated 08-03 beat older wireframe body text; `_slack-routing.md` (CONFIRMED 08-03) beats the "pending" wording in `global-rules-draft.md` / `decision-sources.md`.

- **[C-1] Carrier auto-record.** view-orders S6b banner ("Carrier recorded automatically") and inbound-request State-1 footer (a) ("Received Date + Carrier are recorded automatically") contradict view-orders S6 footer + inbound-request S3-10 ("automatic Carrier recording NOT supported, confirmed 2026-08-03"). **Verdict: NOT supported** (2026-08-03; supervisor-confirmed). Banner/footer texts are stale → WF-1, WF-2. Specs state: Received Date auto-recorded at scan time; no Carrier capture, no Carrier column.
- **[C-2] Comment-mention channel.** `global-rules-draft.md` G-7 says channel "pending"; decision-sources item 12 says "channel decision pending owner". `_slack-routing.md` says **CONFIRMED: #fulfillment-admin-comments (C0BMGEWM5QA), owner, 2026-08-03**. **Verdict: routing file wins.** All 16 plans already agree. Specs cite the confirmed channel + ID; G-7 text amended (§5 below).
- **[C-3] Route taxonomy vs OTHER route.** G-5 says "Exactly 4: SMART BUY / JIT / WHOLESALE / PARTNERSHIP", but the inbound-request form's 4 radio cards are Smart Buy / Wholesale / Brand Partnership / **Other + free-text channel** (JIT is not a requestable route; OTHER badge appears in the wireframe). **Verdict: G-5 must be amended** — order-facing sourcing badges remain the 4; inbound-origin routes are SMART_BUY / WHOLESALE / PARTNERSHIP / OTHER(free text); downstream rendering of OTHER = provisional "OTHER (channel)" black bold → PD-80. (inbound-request O-4; 2026-07-26 form decision.)
- **[C-4] Closing report print.** decision-sources mandatory item 4 lists "Closing report" as a [G-4] instant-print surface; the closing wireframe (SST) ships **CSV download only, no Print button** (2026-07-23 rework). **Verdict: wireframe wins provisionally — CSV-only, G-4 does not land on closing** → PD-68 (OWNER-PENDING; both closing plans flagged it).
- **[C-5] Send-sound scope.** G-3(a) says "Outbound-class buttons"; decision-sources item 3 maps audio only to View Orders/RTO. Order Detail has an Outbound button; Inventory has "− Record Outbound". **Verdict: global rule text wins — sound on every outbound-class button on every page** → PD-2. (order-detail OQ-2/Q-A6; stock-status A already assumed this.)
- **[C-6] G-2 "EVERY confirming action toasts" vs wireframe omissions.** tracking-missing ✕ removal has no toast/confirm; closing Start-with-invalid-input no-ops silently. **Verdict: G-2 (2026-08-03 owner emphasis) wins over wireframe omissions** — removal gets confirm+reason+toast (PD-60), closing start gets explicit validation error (spec-level; wireframe demo limitation noted).
- **[C-7] Auto-outbound on full inbound.** View Orders: full inbound ⇒ auto outbound (S1-8/9). Order Detail wireframe implies manual Outbound (gate-enabled button only). **Verdict: auto-outbound is a View Orders scan/bulk-flow behavior only; Order Detail is always manual** → PD-21. (order-detail Q-A2.)
- **[C-8] G-13 internal picking artifacts vs RTO picking list.** G-13: internal invoice & picking label show WHICH sample and HOW MANY. RTO M1 picking-list modal has no sample lines. **Verdict: G-13 doctrine wins provisionally — picking list/printed picking artifacts include sample lines** → PD-36 (OWNER-PENDING), WF-9 conditional.
- **[C-9] RTO "no failure case" (2026-07-22) vs explicit print-failure surfacing (G-4 doctrine, view-orders E-39, 2026-08-03).** **Verdict: both retained with a boundary** — batch-completion UI stays all-success (07-22 decision protected); infrastructure failures (print agent offline, stale order) surface as a separate red toast and per-order results are always persisted (DC-16) → PD-34 (OWNER-PENDING).
- **[C-10] Closing internal legend contradiction.** State-1 legend #2 says the large panel "is used only in warning states" while State-2 legend says the large warning panel was removed 2026-07-23. **Verdict: 07-23 wins — no large red panel remains anywhere; the only big panel is State 4's green completion status.** → WF-5; spec normalizes (both closing plans, OQ-D6/DQ-7).
- **[C-11] G-11 reason-enum wording.** G-11 draft: "supplier change / damaged / other". Wireframe M6: "Damaged/defective — cannot accept / Supplier qty change / Other". **Verdict: wireframe M6 strings are canonical**; G-11 wording aligned (§5).
- **[C-12] Event-name divergence for shared cross-page events.** Same event named differently across lens-A files (e.g., view-orders `product_barcode_register` vs stock-status `barcode.registered`; comment events in 4 shapes). Not a behavioral conflict — **resolved by convention** (§4): one canonical name per shared event, table below.

**Adjudicated non-issues (do not "fix" in P3-3/P3-4):**
- M6 demo header "Inbound No. 202607120002" vs State-6 banner "…0001" — **intended renumbering** (supervisor 판단 14). Not a contradiction, not a wireframe defect.
- Deleo Tracking No removed from View Orders but retained on Order Detail — deliberate asymmetry (2026-07-21/22 decisions), both plans agree.
- stock-status legend numbering starting at 5 (no dots 1–4) and inbound-request State-1 missing dot 13 — page-local numbering artifacts, declared in each spec's §2, not coverage gaps.
- Closing "unknown order" ≠ tracking-missing "unrecognized product" — confirmed disjoint flows; closing unknown does NOT route to #unrecognized-tracking (both pages agree; state the non-route explicitly in both specs).

---

## 2. Coverage audit

### 2a. A/B legend-count reconciliation (per page)

| Page | Lens A | Lens B | Match | Notes |
|---|---|---|---|---|
| view-orders | 58 (50 dots + 8 modal) + 3 footer blocks | 58 + 3 offscreen blocks | OK | S0 2 · S1 21 · S1b 1 · S2 2 · S3 4 · S4 6 · S5 3 · S6 9 · S6b 2 · M1/M2/M2b/M3/M3b/M4/M5/M6 |
| order-detail | 15 (14 + M3) + unnumbered live-admin controls | 15 + non-legend stubs | OK | Both enumerate the same subbar/baseline controls |
| ready-to-outbound | 15 (1–14 + M1) | 15 | OK | Legend render order 1–8,14,13,12,9,10,11 noted by A |
| stock-status | 16 (dots 5–16 + M1–M4) | 16 | OK | B additionally keys baseline furniture [L-F1..F4] — adopt (2c) |
| order-management | 9 (1,2,3-removed,4,5 + M1/M1b/M2/M3) | 9 | OK | Keying variants to standardize (2c) |
| tracking-missing | 7 (0–5 + M1) | 7 | OK | Dead v1 CSS/JS excluded by both → WF-10 |
| closing | 21 dots + L-1.B block = 22 keys | 21 + 1 offscreen = 22 keys | OK | Key style must be normalized (2c) |
| inbound-request | 28 + 2 footer blocks | 28 (+ footer coverage) | OK | Both declare the dot-13 gap |

**Result: 0 count mismatches.** Total ≈ 169 legend units + 6 off-screen normative blocks across 8 pages.

### 2b. Mandatory 12 × 8 matrix

Codes: **P** = primary home · **Y** = lands materially · **Δ** = delta/cross-ref only · **n** = explicit N/A (stated in spec, not silent). Pages: VO=view-orders, OD=order-detail, RTO, INV=stock-status, OM=order-management, TM=tracking-missing, CL=closing, IR=inbound-request.

| # | Mandatory item | VO | OD | RTO | INV | OM | TM | CL | IR |
|---|---|---|---|---|---|---|---|---|---|
| 1 | Scanner protocol [G-1] | **P** | n | n | n | n | n | **P** | n¹ |
| 2 | Confirmation toast [G-2] | Y | Y | Y² | Y | Y | Y | Y | Y |
| 3 | Audio [G-3] | Y(a+warn) | Δ³ | Y(a) | Δ³ | n | n | Y(b) | n |
| 4 | Instant print [G-4] | Y | Y | Y | n | n | n | ⚑⁴ | n |
| 5 | Sample dual-view [G-13] | Δ | Δ⁵ | Δ⁵ | n | **P** | n | n | n |
| 6 | Unrecognized matching | Y(shared) | Δ | n | Δ | n | **P** | Δ⁶ | Δ |
| 7 | Multi-tracking [G-10] | Y | Δ | n | Δ | n | Δ | n | **P** |
| 8 | RTO Korean names [G-6] | Δ | Δ | **P** | n | n | n | n | n |
| 9 | Line-based location filter [G-14] | n | n | n | **P** | n | n | n | n |
| 10 | Audit-mode-only visibility [G-14] | n | n | n | **P** | n | n | n | n |
| 11 | JIT residual stock | Δ | n | n | **P** | n | n | n | n |
| 12 | Comment @mention routing [G-7] | Y | Y | Y | Y | Y | Y | Y | Y |

¹ IR delta: Enter in the unified search box must NOT submit the form (G-1-adjacent). ² RTO Bulk Outbound refresh = the sole designed G-2 exception. ³ PD-2 (sound on OD Outbound / INV Record Outbound). ⁴ PD-68 (CSV-only provisional; conflicts decision-sources). ⁵ PD-27 (OD display) / PD-36 (RTO picking-list sample rows). ⁶ boundary note only (unknown ≠ unrecognized).

**Result: 0 holes** — every item has a primary home and every N/A cell is an explicit statement. 2 flagged ambiguities (items 3, 4) resolved provisionally via PD-2 / PD-68.

### 2c. Keying discrepancies to normalize (P3-3 must follow §4 conventions)

1. **closing** uses `[L-1.8]` dot style → normalize to `[L-S1-8]` standard (supervisor: view-orders.B convention is the all-page standard).
2. **order-management** A keys `[L-2a]/[L-2b]` for the two legend-2 buttons and `[L-M1b]`; B keys `[L-2]` and `[L-1b]` → use `[L-2a]/[L-2b]` and `[L-M1b]`.
3. **stock-status** baseline furniture: adopt B's `[L-F1]`(history search) `[L-F2]`(inbound form) `[L-F3]`(outbound form) `[L-F4]`(export); A must key its equivalents identically.
4. **view-orders / inbound-request / closing** off-screen footer blocks: A uses `[L-S1-F]`, B uses `[L-S1-offscreen]`, closing uses `[L-1.B]` → standard is `[L-{state}-F]` (suffix a/b/c when a footer holds multiple rules).
5. QA tier tags: plans use `[WF]`, `WF-RUN`, `[ADMIN]`, `ADMIN-ONLY`, `[REAL-ADMIN]` → standard is **[WF] / [ADMIN]** only.

---

## 3. Writing conventions (binding for P3-3 authors)

1. **Legend keys**: `[L-{state}-{n}]` on multi-state pages (`[L-S1-8]`, `[L-S2b-1]`, `[L-SH-1]` for closing history); plain `[L-{n}]` on single-state pages (order-detail, RTO, OM, TM); modals `[L-M{n}]` (+ letter for sub-dots: `[L-M1b]`); off-screen normative footer paragraphs `[L-{state}-F]`; unnumbered page furniture `[L-F{n}]`. §2 of every spec declares the page's total unit count and any numbering gaps (no dot 13; dots start at 5) so P3-4 coverage checks don't flag phantom holes.
2. **IDs**: edge cases `[E-{n}]`, data-capture events `[DC-{n}]`, business rules `[BR-{n}]` — all page-scoped, stable once assigned; if two candidates merge, keep both IDs on the merged entry ("E-7 = E-18"). Never renumber.
3. **Shared cross-page event names** (canonical, must be byte-identical wherever they appear): `comment.posted` · `comment.mention_notified` · `comment.starred` / `comment.unstarred` · `comment.read` / `comment.mark_all_read` · `comment.auto_posted` (`source=system`) · `product.barcode_registered` · `order.status_changed` · `order.outbounded` · `print.job_result`. Other events use lowercase `entity.action` semantic names; literal API names are dev's.
4. **QA scenarios**: `QA-{block}-{n}`, Given/When/Then, keyed to `[L-*]`/`[E-*]`, tagged **[WF]** (executable on the live wireframe now — exact selectors/labels/toast strings) or **[ADMIN]** (real-admin-only; kept as deferred rows). Negative tests ≥ 25% per page. Every §5 event gets ≥1 Then-clause asserting the persisted event.
5. **G-rule citation**: cite `[G-n]` and write page **deltas only** — never restate the rule body. When a plan supersedes stale draft text (G-7 channel, G-5 OTHER), cite the source + date ("per `_slack-routing`, 2026-08-03"), not the draft.
6. **Slack notation**: `#channel-name` with ID in parentheses on first mention per spec — `#fulfillment-admin-comments` (`C0BMGEWM5QA`), `#unrecognized-tracking`, `#wholesale-ops`, `#partnership-kr`. Payload fields verbatim from `_slack-routing.md`. Never write "pending" for confirmed rows.
7. **Dates**: `YYYY-MM-DD` everywhere (Decision Logs, BR rationale, conflict citations). No `07-23` shorthand in final specs.
8. **Provisional decisions**: where a spec adopts a PD, write the behavior normally and tag it `[PD-{n} · OWNER-PENDING]` at the sentence. §9 lists ONLY: NO-DEFAULT open questions, dev-time decisions, and out-of-scope pointers — owner questions with provisional defaults live in the PD register, not re-listed as open.
9. **Tone/language**: English, imperative present ("The button disables when…"). Korean strings (product names, carrier names, 비엠유통 등) are data — keep verbatim, never translate [G-6]. Exact UI copy, toast strings, and button labels in quotes, byte-accurate to the wireframe.
10. **Removed/dead items**: removed features (Bulk Hold, per-PIC groups, resolved log, SHIPPED status, link-info modal, photo upload) get explicit negative entries ("must NOT exist") + Decision Log rows — never silently dropped, so nobody re-implements from stale docs.
11. **Decision Logs (§10)**: record reversal chains verbatim (sample assignment 07-22 removed → 07-23 reinstated → 08-03 reconfirmed; history modal → page; Latest Inventory Count removed → restored).

---

## 4. Global-rules deltas (changes required to `_global-rules` before/during P3-3)

- **[GD-1] G-7**: replace "one item pending owner decision" → "Mention channel: **#fulfillment-admin-comments** (`C0BMGEWM5QA`), CONFIRMED by owner 2026-08-03; message body @mentions the tagged person (personal notification); channel doubles as team-visible archive." Add: system auto-comments (expected-qty edit, unrecognized match-confirm) route through the same comment-mention pipeline with `source=system`; pool items (tracking-missing) are a first-class commentable entity type.
- **[GD-2] G-5**: amend "Exactly 4" — order-facing sourcing badges remain SMART BUY / JIT (channel) / WHOLESALE / PARTNERSHIP; the Inbound Request origin form offers SMART BUY / WHOLESALE / PARTNERSHIP / **OTHER (free-text channel)**; OTHER renders downstream as black bold "OTHER (channel)" [PD-80, OWNER-PENDING]. JIT is never a requestable inbound route (it arises order-side).
- **[GD-3] G-3**: clarify (a) scope = **every outbound-class button on every page** (View Orders outbound family, RTO Bulk Outbound, Order Detail Outbound, Inventory "− Record Outbound") [PD-2, OWNER-PENDING]; add note: View Orders State 6 wrong-product **warning tone** is a distinct sound from the send sound (page delta, not TTS).
- **[GD-4] G-11**: align reason enum to wireframe M6 strings: "Damaged/defective — cannot accept" / "Supplier qty change" / "Other (memo)". Also state: expected-qty edits originate ONLY in View Orders M6; inbound-request displays history.
- **[GD-5] G-2**: add "removal/deletion confirmations are confirming actions" (covers tracking-missing ✕ per PD-60); keep RTO Bulk Outbound as the sole named refresh exception (confirmed unique across all 16 plans).
- **[GD-6] G-8**: add explicit non-event doctrine: "Specs may declare explicit NON-events (ephemeral client-local state: checkbox toggles, filter clicks, edit-cancel). Anything not declared a non-event and operator-initiated must persist." (All 8 A-lens plans already practice this.)
- **[GD-7] G-14**: after PD-46, extend: "One location per SKU **and one SKU per location** (1:1)" — pending owner.
- **[GD-8] New G-15 (Permissions)**: "v1 ships a single admin role; no role gating on any screen; every mutating action records the actor [G-8]. Role model is a post-v1 owner decision." [PD-1, OWNER-PENDING] — closes the identical open question raised independently by 6 pages.
- **[GD-9] G-4**: no text change, but the surface registry cited from decision-sources shrinks: closing report = CSV-only provisional [PD-68]; print surfaces = View Orders (order Print, single-item auto-print, M4 return labels), RTO (row Print, Bulk Print Labels, M1 picking list), Order Detail (Print).
- **[GD-10] G-10/G-12**: no changes needed — plans consistent. G-1: add closing deltas as page-spec material only (input disabled pre-start; select-all on focus return), no global text change.
