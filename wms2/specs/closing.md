# Closing — Screen Specification (WMS 2.0)

> **Decision status update (2026-08-03)** — PD-1 through PD-8, 51, 55, 66, 71, 74, 79 are now **OWNER-DECIDED** (PD-6 confirmed 2026-08-03 — the owner decision round is fully closed); any inline `[PD-{these} · OWNER-PENDING]` or `[PD-{these} · NO-DEFAULT]` tags below are superseded — see `_provisional-decisions.md` for the decisions. (PD-71 and PD-74 are already folded into this spec's body — v1.3.)

Page slug: `closing` · Spec version 1.3 · 2026-08-03 (v1.0 authored · v1.1 audited and completed · v1.2 remediated against the M1 coverage audit, the M2 adversarial QA run, and the M3a/M3b cross-page findings · v1.3 **Amend Closing** added per the owner's PD-74 decision, and the owner-approved wireframe defect batch `[WF-4]`/`[WF-5]`/`[WF-7]`/`[WF-8]`/`[WF-12]` applied to the wireframe)
Wireframe (SST): `wms2/closing/index.html` · Live: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/closing/
Global rules: `_global-rules` (cited as `[G-n]`; this spec writes page deltas only and never restates a rule body).
Provisional decisions: `_provisional-decisions.md` (cited inline as `[PD-n · OWNER-PENDING]`).
Wireframe defects: `_wireframe-fixes.md` (cited as `[WF-n]`). Where the wireframe text is stale, this spec states the **correct** behavior and names the defect; it never specs the stale text. **`[WF-4]` `[WF-5]` `[WF-7]` `[WF-8]` `[WF-12]` were applied to the wireframe on 2026-08-03** (owner-approved batch — §2.3); `[WF-15]` remains open (corpus-wide `[G-7]` fix).

---

## 1. Purpose & Users

### 1.1 What the screen is

Closing is the end-of-day reconciliation between **what physically leaves the warehouse** and **what the system believes left**. After packing is finished and before the carrier collects, an operator counts the packed parcels by hand, enters that number, then scans the carrier-handover tracking barcode on every parcel exactly once. Each scan is judged instantly against the order's status. Closing is confirmed only when the count of OK scans matches the hand count exactly and no warning is outstanding. A confirmed day can later be corrected through **Amend Closing** from the Closing History page (§3.24, owner decision 2026-08-03 resolving `[PD-74]`).

It replaces a spreadsheet ritual that exists today:
1. paste the day's tracking numbers into Excel and run a conditional-format duplicate check on column A,
2. eyeball each order to answer "was this outbound-processed?",
3. walk to Zero Packing to verify packing for anything suspicious (step 6 of the current process),
4. copy/paste the day's totals into the **SS Daily Shipping Status** sheet, stripping formulas on the way.

Steps 1–2 become the scan verdict, step 3 becomes modal M1, and step 4 is **retired outright** — the owner retired the sheet itself on 2026-08-03 (`[PD-71]` resolved): the admin's **Closing History** (daily snapshots + per-day CSV) replaces the SS Daily Shipping Status spreadsheet wholesale, and no sheet integration exists.

### 1.2 Users

| Role | Who (mock data in the wireframe) | What they do here |
|---|---|---|
| Warehouse packing staff | Dean, Miranti | Hand-count parcels, start closing, scan every parcel, resolve warnings in the list |
| Warehouse staff / manager who closes | Yongwon (mock: starts 18:02 Dean → confirms 18:52 Yongwon) | Presses [Confirm Closing]; may differ from the starter |
| Anyone reading the audit trail later | order team, Fulfillment lead | Closing History, per-day CSV, comment trail |

v1 has **no role gating**: any admin user may start, edit the count, cancel, scan, resolve, and confirm; every mutating action records the actor [G-15] `[PD-1 · OWNER-PENDING]`.

### 1.3 The operator's physical reality (this is what shaped the design)

These are not ambience notes — each one is the reason a specific rule below exists.

- **A scanner is in the operator's hand, and a parcel is in the other.** The hands are busy; there is no free hand for a mouse and no patience for a click between parcels. Hence the three [G-1] invariants, which this page inherits unchanged (deltas in §3.2). Hence also the click-anywhere refocus rule in `[L-S1-F]` — a stray click on the table must not silently break the loop.
- **The eyes are on the parcels and the label, not on the monitor.** The operator scans, hears, and moves on. This is why warnings speak (`[G-3b]`, en-US TTS "Please check this order", confirmed 2026-07-23) and why OK scans are deliberately **silent** and rendered as a one-line green bar instead of a large panel (Dean's request, 2026-07-23). If OK also made noise, the audio channel would carry no information — which is why the one non-warning sound on this page (§3.21) must be audibly distinct.
- **The monitor sits at arm's length or further, often across a packing bench.** The only thing that must be readable from that distance is a problem — hence red row tint, a red pill, and the big green completion panel on State 4. The large red panel was removed on 2026-07-23 once the voice channel existed: reading the row is enough when the ear already told you to look.
- **Speed is roughly one parcel every few seconds** across 80–100 parcels, often with two people scanning into the same session from two stations. Hence server-atomic sequence numbers, server-side session state, and the rule that a slow lookup must never lock the input (`[BR-26]`).
- **The count is a physical count, never a system figure.** The whole point is to catch divergence in both directions: an 85th parcel found on the floor after counting 84, and a system row with no parcel behind it. Hence the target is typed by a human, scanning stays alive after the match, over-scan re-disables the gate, and [↺ Edit count] is always available.
- **The unit of the count is a parcel, not an order.** One order can ship in two boxes (two tracking numbers, two OK scans) and two orders can ship in one box (one tracking number, one OK scan plus one duplicate). Both cases still reconcile against the hand count, because the hand count counts boxes (`[BR-33]`).
- **Interruptions are normal**: shift handover, a walk to Zero Packing, a browser crash, a laptop that sleeps. Hence server-side session persistence (`[BR-8]`) — nothing clears until the closing is confirmed or explicitly cancelled.
- **Duplicates are a judgment call, not an error.** Two parcels can legitimately carry one tracking number (combined box). The row therefore hands the operator exactly what a human needs to judge: which sequence number it collides with, when that scan happened, who made it, and what that earlier scan's verdict was — then the reason goes into the order's comment trail.

### 1.4 Operational moment

Late afternoon / early evening (mock data: 18:02 start → 18:52 confirm), after packing, before carrier handover. The closing record is the day's ground truth for the shipping report and the only place where "the system said we shipped it" is checked against "we actually have the box".

---

## 2. Screen Inventory & Wireframe Map

### 2.1 Declared legend-unit count

This page carries **24 legend units**: **23 numbered annotation dots** + **1 off-screen normative behavior block** (the State 1 legend footer paragraph, keyed `[L-S1-F]`).

Distribution: State 0 → 1 · State 1 → 11 (+1 off-screen block) · State 2 → 1 · State 2b → 1 · State 3 → 1 · State 4 → 3 · Closing History → 2 · M1 → 1 · M2 → 1 · M3 → 1.

**How to reproduce the count** (so a coverage checker and this spec never disagree): count `.legend ol > li` elements per `section` (1 + 11 + 1 + 1 + 1 + 3 + 2 = 20), add the three modal dots `#m-process .dot` ("M1"), `#m-scandel .dot` ("M2") and `#m-amend .dot` ("M3") → 23, then add the single `.legend > p` normative paragraph inside `#s1`'s legend → 24. Do **not** count `.wf-tab` buttons and do not count `.dot` elements in the mock (they are 1:1 with the `<li>` items they annotate, except that `#s1`'s dot 9 sits on `.pagepad`, dot 5 on a `<th>`, and Closing History's dot 2 on the history table's action-column `<th>`). The `#m-cancel` confirm dialog (the `[WF-7]` fix) carries **no dot on purpose** — it is specified under `[L-S1-10]` (§3.11), not as a separate legend unit.

**Numbering notes (so a coverage check does not flag phantom holes):**
- There are **no gaps** in this page's dot numbering. State 1 runs 1–11 continuously; every other state carries a single dot numbered 1 **except Closing History, which carries dots 1–2**; the three modals are dotted `M1`, `M2` and `M3`.
- The number `1` legitimately appears once per state — dots are numbered per state, not per page.
- The wireframe's `wf-bar` formerly listed the tab **"Modal: Process Processing Order" twice** — demo chrome duplication `[WF-12]`, **fixed 2026-08-03** (the duplicate tab was removed; a "Modal: Amend Closing" tab was added in the same pass, so `.wf-tab` still counts 10). Tab texts are now unique, but QA still selects by `[data-state]` / `[data-modal]` (§8.0 R3), and a unit count must never be derived from `.wf-tab` (QA-CHROME-04).
- Scan-list sequence numbers in the mock data jump between states (State 1 shows #1–#5, State 2b shows #5 and #7, State 3 shows #2 and #6). This is deliberate demo continuity across a single imagined session, not a numbering gap.

Four additional keys cover page furniture that carries **no legend dot**. They are specified in §3 but are explicitly **not part of the 24**:

| Key | Furniture |
|---|---|
| `[L-F1]` | Global admin nav bar (SkinSeoul brand, Operation AI / Catalog Management / OMS Center / Site Management, Comments entry point, user chip, Logout) |
| `[L-F2]` | Page header — `WMS - Closing` + subtitle "Barcode-scan verification of today's packed orders" |
| `[L-F3]` | Toast slot (top-right, `.toast` / `.toast.err`) [G-2] |
| `[L-F4]` | Wireframe-only chrome: purple `wf-bar`, state tabs, `#annoToggle` ("Hide annotations"), annotation dots and legend blocks. **Must NOT ship to the admin.** |

### 2.2 State / modal map

Live URL for every row: https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/closing/ (single page; states are switched by the purple `wf-bar` tabs — there is no hash routing).

| # | State | DOM id | Reach it by | wf-bar tab label (byte-exact) | Legend keys owned | §3 anchor |
|---|---|---|---|---|---|---|
| 1 | Before Start (manual count) | `#s0` | default on load; or `.wf-tab[data-state="s0"]` | `0 · Before Start (manual count)` | `[L-S0-1]` | §3.1 |
| 2 | OK Scan (outbounded) | `#s1` | `.wf-tab[data-state="s1"]`; or `#startBtn0` with a non-empty `#targetIn0` | `1 · OK Scan (outbounded)` | `[L-S1-1]`…`[L-S1-11]`, `[L-S1-F]` | §3.2–§3.13 |
| 3 | Warning · Processing | `#s2` | `.wf-tab[data-state="s2"]` (auto-plays the voice via `data-voice`) | `2 · Warning · Processing (not outbounded)` | `[L-S2-1]` | §3.14 |
| 4 | Warning · Unknown Order | `#s2b` | `.wf-tab[data-state="s2b"]` (auto-plays the voice) | `2b · Warning · Unknown Order` | `[L-S2b-1]` | §3.15 |
| 5 | Warning · Duplicate Scan | `#s3` | `.wf-tab[data-state="s3"]` (auto-plays the voice) | `3 · Warning · Duplicate Scan` | `[L-S3-1]` | §3.16 |
| 6 | Closing Complete | `#s4` | `.wf-tab[data-state="s4"]` | `4 · Closing Complete` | `[L-S4-1]`, `[L-S4-2]`, `[L-S4-3]` | §3.17–§3.19 |
| 7 | Closing History (page) | `#shist` | `.wf-tab[data-state="shist"]`; or the in-page tab `[data-goto="shist"]` labelled `Closing History`, present in every closing state | `5 · Closing History (page)` | `[L-SH-1]`, `[L-SH-2]` | §3.20, §3.24 |
| 8 | Modal — Process Processing Order | `#m-process` | `[data-modal="m-process"]`: the wf-bar tab, **or** the in-row button "Process this order" in `#s1` row #4 and `#s2` row #4 | `Modal: Process Processing Order` | `[L-M1]` | §3.21 |
| 9 | Modal — Delete Scan Row | `#m-scandel` | `[data-modal="m-scandel"]` wf-bar tab, **or** the per-row `button.scandel` (title "Delete scan row", label "✕") in any scan list | `Modal: Delete Scan Row` | `[L-M2]` | §3.22 |
| 10 | Modal — Amend Closing | `#m-amend` | `[data-modal="m-amend"]` wf-bar tab, **or** the per-row `[Amend]` button (`button.amendbtn`) in `#shist` | `Modal: Amend Closing` | `[L-M3]` | §3.25 |

In the shipping admin, states 1–6 are not tabs — they are the same page rendering the live session; the wf-bar exists only to let a reviewer jump between the possible renderings `[L-F4]`.

### 2.3 Known wireframe defects touching this page

| Defect | Where | Correct behavior specced in |
|---|---|---|
| `[WF-4]` **(fixed 2026-08-03)** State 4 legend #1 said the snapshot is saved to Closing History "(M2)" — a fossil of the pre-2026-07-23 modal; M2 is the Delete Scan Row modal | `#s4` legend | §3.17 — the snapshot is saved to the **Closing History page** (`#shist`); the legend now says exactly that |
| `[WF-5]` **(fixed 2026-08-03)** State 1 legend #2 said the large panel "is used only in warning states", contradicting the 2026-07-23 removal of the large warning panel | `#s1` legend #2 | §3.3 / §3.14 — **no large red panel exists anywhere**; the only large panel is State 4's green completion status; the legend now says exactly that |
| `[WF-7]` **(fixed 2026-08-03)** `#closeCancel` cancelled immediately with no confirmation | `#s1` banner | §3.11 — the confirm dialog `[PD-5 · OWNER-PENDING]` now exists in the wireframe as `#m-cancel` with the §3.11 copy |
| `[WF-8]` **(fixed 2026-08-03)** `#startBtn0` silently no-oped on empty/invalid input | `#s0` | §3.1 — the wireframe now raises the explicit red validation toasts (adjudication C-6); the >9999 advisory confirm remains `[ADMIN]`-only |
| `[WF-12]` **(fixed 2026-08-03)** duplicated "Modal: Process Processing Order" wf-bar tab | wf-bar | §2.1 — chrome only; the duplicate tab was removed |
| `[WF-15]` **(fixed 2026-08-03)** Comments hub pane headers and the unstar hint diverged from the cross-page `[G-7]` contract (shipped "Comments where I'm tagged" / "Comments I saved" / "Unstar to remove from this list") | `#inbox1` `.paneheader` | §3.8 — `[G-7]` v1.2 published the canonical set HUB-1…HUB-7, and all eight wireframes plus all eight QA suites moved to it in one commit, which is the condition the register attached to this fix. `[WF]` and `[ADMIN]` now assert the same strings |

The six `(fixed 2026-08-03)` rows were applied to `wms2/closing/index.html` in the owner-approved wireframe-edit batch of 2026-08-03 (same pass that built the Amend flow); the rows are kept for provenance, and the affected `[WF]` QA scenarios (QA-S0-02, QA-TARGET-04, QA-CHROME-03/04) now assert the fixed behavior.

**Unregistered wireframe divergences found while auditing this spec** (not yet in `_wireframe-fixes.md`; listed so QA classifies them as demo artifacts, not implementation targets):

- **U-a** State 1 "Remaining scans" tile reads **79** while target 84 and OK 3 imply **81**; the `.proglab` sentence on the same screen says "81 short of the manual count". The formula in §3.5 is authoritative (`Remaining = max(0, target − OK)` → 81); the tile value 79 is bad demo data. **The same `79` also appears in the Confirm Closing button label** (`index.html:397`, "Confirm Closing (79 remaining · 2 warnings)"), which §3.9 quotes byte-exactly and QA-CONFIRM-01 asserts byte-exactly: that quoted string is **demo data, not a worked example** of the label formula — `remaining` is never `target − ok − warnings`. States 2, 2b and 3 are internally consistent (84 − 4 = 80).
- **U-b** State 4 renders an enabled-looking scan input. After confirmation the input is **disabled** `[PD-73 · OWNER-PENDING]` (§3.17).
- **U-c** The Comments hub in the DOM has only the `@ Mentions` / `★ Saved` tabs; the full-text comment search required by [G-7] and named in State 1 legend #7 is not built in the wireframe. The search is specced (§3.8) and its QA is `[ADMIN]`.
- **U-d** The warnings tile label differs between states ("Warnings (not outbounded · duplicate)" in S1/S2/S3 vs "Warnings (not outbounded · duplicate · unknown order)" in S2b vs "Warnings (resolved)" in S4). §3.5 fixes the canonical labels.
- **U-e** Only State 1 wires the Comments dropdown (`[data-open="inbox1"]`); the other states render a static "💬 Comments" button with no dropdown. Demo limitation — in the admin the hub is identical on every state.
- **U-f** Order ID cells are styled blue but are plain `<td>` text, not links. They must be real deep links [G-12] (§6.3).
- **U-g** Only State 1 wires the voice controls (`#voiceToggle`, `#voiceState`, `#voiceTest`); States 2/2b/3/4 render a static switch plus a `.sim-voice` button. The toggle is nevertheless a page-global (`voiceOn`), so a toggle set in State 1 governs the other states' auto-play — QA must account for that (§8.0 R7).
- **U-h** The replay button is labelled "🔊 Play again" in States 2/2b/3 and "🔊 Test voice" in States 1 and 4. Canonical label in the admin is **"🔊 Test voice"** at all times; "Play again" is demo copy for a state that has just spoken.
- **U-i** State 4 renders the "🔊 Test voice" control but the voice switch there carries no explanatory suffix ("— plays …") that the other states carry. Cosmetic; the canonical switch copy is in §3.4.
- **U-j** Only State 1 renders the full target banner with `[↺ Edit count]` and `[✕ Cancel Closing]`; States 2/2b/3 render a muted one-line summary ("① Today's outbound target (manual count): **84 orders** — closing started 18:02 (Dean)") instead. In the admin the **full banner with both controls is present in every `IN_PROGRESS` rendering** (§3.11); the muted line is demo shorthand.

---

## 3. Functional Specification

### 3.0 Conventions used in this section

- **Logical server actions** are named `closing.*` for readability (`closing.start`, `closing.scan`, …). Literal endpoint/API naming is a developer decision.
- Every mutating action is **double-click safe** [G-9]: client debounce **and** a server idempotency key. Key format, TTL and debounce window are developer decisions.
- Every confirming action shows a top-right toast [G-2]; green on success, red on failure. Toast strings that exist in the wireframe are quoted as-is; strings marked **(spec-authored)** are new copy this spec defines because the wireframe has none.
- The **session state machine** is `IDLE → IN_PROGRESS → (CONFIRMED | CANCELLED→IDLE)`. `CONFIRMED` is terminal for that calendar date `[PD-70 · OWNER-PENDING]`.
- The confirm predicate is a pure function evaluated **server-side** and mirrored client-side: `ok_count == target AND outstanding_warnings == 0`.
- All rendered times and all date boundaries use the **warehouse's single operating timezone** (`[BR-36]`); storage timezone is a developer decision.
- **`[GD-n]` citation form.** `[GD-n]` is a *global-rule delta* — an amendment already folded into `_global-rules.md` v1.0. The delta log itself is `_plans/_review.md` §4 (`GD-1`…`GD-10`); it is not part of the shipped 8-spec + `_global-rules` corpus, so every `[GD-n]` in this spec is written with the resulting rule text beside it and the ID is a provenance pointer only. This page cites `[GD-5]` (§10) and `[GD-9]` (§3.18, §6.5).
- **Sub-rule citation form.** `[G-3]`'s branches are cited as `[G-3a]` / `[G-3b]` / `[G-3c]` throughout this spec (never `[G-3](a)`), so a mechanical `[G-n]` grep resolves.
- **Foreign keys are never bracketed.** A `[L-…]` in square brackets is always one of **this** page's 24 legend units plus the 4 furniture keys (§2.1, §2.2), so a mechanical key-existence check over this file cannot produce a phantom. Another spec's key is written unbracketed with its file — `order-detail.md` L-9, `view-orders.md` L-S4-6 — and another spec's business rule is written with its page code (VO `BR-9`, OD `BR-12`), never as a bare `[BR-n]`, which on this page always means a closing rule from §4.

### 3.0.1 Page furniture

**`[L-F1]` Global nav.** Standard admin nav (`SkinSeoul` · Operation AI ▾ · Catalog Management ▾ · OMS Center ▾ · Site Management ▾ · Comments · user chip · Logout). Rendered on every state. The Comments button is the entry point for `[L-S1-7]`. No closing-specific behavior.

**`[L-F2]` Page header.** `<h2>WMS - Closing</h2>` and the subtitle "Barcode-scan verification of today's packed orders", present on every state including Closing History. Directly beneath sits the in-page tab strip specified in `[L-S1-11]`.

**`[L-F3]` Toast slot.** Top-right, one slot, green `.toast` / red `.toast.err`, two-part payload (bold headline + muted `small` subtext). All toasts in this spec use that shape. Duration and stacking policy are developer decisions. A toast **never** takes focus and never blocks the scan input.

**`[L-F4]` Wireframe chrome.** The purple `wf-bar`, its state tabs, `#annoToggle` ("Hide annotations" ⇄ "Show annotations"), the purple dots and the `.legend` blocks are review scaffolding. They **must NOT exist** in the shipping admin.

---

### 3.1 `[L-S0-1]` — Pre-start screen (manual count only)

**Trigger.** The operator opens WMS → Closing on a date with no `IN_PROGRESS` and no `CONFIRMED` session.

**What is on screen.** Exactly one blue-outlined card, centered, containing:
- the 🧮 glyph and the heading "① Today's Outbound Target (manual count)";
- the explanatory line "Enter the **hand-counted number** of physically packed parcels and start closing — the OK-scan count must **exactly match** this number to confirm closing";
- a numeric input `#targetIn0`, placeholder "Hand-counted qty", followed by the literal word "orders";
- the primary button `#startBtn0`, label "Start Closing";
- above the card, the in-page tabs [Closing | Closing History].

**Nothing else is exposed** — no scan input, no tiles, no progress bar, no scan list, no Confirm button (simplification of 2026-07-23). This is deliberate: the screen has exactly one possible action, so "enter the number first" needs no instruction.

**Validation** (`[WF-8]`, fixed in the wireframe 2026-08-03 — adjudication C-6 made the error explicit; the wireframe now implements the first two rows as red toasts):

| Input | Result |
|---|---|
| empty / whitespace only | Start blocked · red toast **(spec-authored)** "✕ Enter the hand-counted parcel count first" |
| `0`, negative, decimal, non-numeric, leading `+`/`-` | Start blocked · red toast **(spec-authored)** "✕ The count must be a whole number of 1 or more" |
| integer ≥ 1 | accepted |
| integer > 9999 | accepted, but an amber inline confirm **(spec-authored)** "That is far above a normal day ({n}). Start anyway?" — the absurd-value guard is advisory, never a hard block (a genuine peak day must not be blocked) |

A target of `0` is rejected on purpose (`[BR-34]`): a day on which nothing shipped has nothing to reconcile, so it is simply **not closed** and has no Closing History row — which is exactly what a missing row means (`[BR-10]`, E-43, E-76).

**Server action.** `closing.start(target)` → creates the session for today's date, records actor and `started_at`, transitions `IDLE → IN_PROGRESS`. Idempotent [G-9]: a second click within the debounce window, or a retried request carrying the same key, returns the existing session instead of creating a second one.

**Rejections the server owns** (each persists `closing.start_rejected`, DC-2, and shows a red toast):
- a session is already `IN_PROGRESS` for today, started by another operator → "✕ Closing already in progress — started {hh:mm} by {actor}" **(spec-authored)**; the client then loads that session instead of creating one (E-55).
- today is already `CONFIRMED` → "✕ Today's closing is already confirmed" **(spec-authored)** `[PD-70 · OWNER-PENDING]`.
- an **older date's session is still `IN_PROGRESS`** → "✕ The closing for {date} is still open — confirm or cancel it first" **(spec-authored)**, and the client opens that session (`[BR-35]`, E-72).

**On success.** No page refresh [G-2]. The screen re-renders as State 1, the scan input is armed and focused, and a green toast **(spec-authored)** appears: "✓ Closing started — target {n} orders" / "Scan the tracking barcode of each packed parcel".

**Persisted.** DC-1 `closing.session_started`.

**Wireframe behavior for QA** (post-`[WF-8]`-fix, 2026-08-03). `#startBtn0` now validates before advancing: an empty/whitespace value raises the red toast "✕ Enter the hand-counted parcel count first"; a non-integer, `0`, negative, decimal or signed value raises "✕ The count must be a whole number of 1 or more"; only an unsigned integer ≥ 1 calls `.wf-tab[data-state="s1"].click()`. The demo toasts render as `.toast.err` inside `#s0 .mock` and self-remove after ~2.6 s. The >9999 advisory confirm and the server-side rejections remain `[ADMIN]` (QA-S0-05/09).

---

### 3.2 `[L-S1-1]` — Closing-dedicated scan input

**Purpose.** The single field the whole page exists around: the carrier-handover tracking barcode of a packed parcel (mock values use the YUN Express `YT…` prefix, e.g. `YT2618100710108810`; the field is carrier-agnostic).

**Rendering.** Large (`22px`, bold, tabular numerals, 2px dark border), full-width up to 900px, with a secondary "Scan" button to its right. Placeholder: "Scan the tracking barcode — outbound status is judged instantly on scan".

**Submit triggers.**
1. **The scanner's automatic Enter** — the primary and expected path [G-1].
2. **A Tab-terminated read** — some wedges are configured to append Tab instead of Enter; Tab submits as well and does not move focus out of the input (E-67).
3. The on-screen "Scan" button — a fallback for a manually typed number. It is never the path during continuous scanning.

Nothing else submits. A read that arrives with no terminator stays in the field until the operator presses Enter or "Scan".

**Closing deltas to [G-1]** (the three [G-1] invariants are untouched):
- **Disabled before the session starts.** The input is `disabled` in State 0 and while the session is `IDLE`. Keyboard-wedge input while disabled goes nowhere and records nothing (E-9).
- **Disabled after confirmation** `[PD-73 · OWNER-PENDING]`. A confirmed closing is an immutable record (§3.17, U-b) — re-armed only inside an amendment session (§3.24).
- **Focus returns with the whole value selected** after every verdict, so the next scan overwrites it.
- **Click-anywhere refocus:** a click on any non-interactive part of the page returns focus to the scan input and selects its content — with the exclusions in `[L-S1-F]`.

**Input hygiene.** The field disables browser autofill, spell-check and IME composition (`autocomplete="off"`, `autocapitalize="off"`, `spellcheck="false"`, and an input mode that does not raise an IME) so a wedge burst can never be intercepted by a suggestion popup or a composition buffer (E-77).

**Normalization before lookup** (developer decision on exact rules, DQ-1): trim leading/trailing whitespace, strip scanner suffix control characters (CR / LF / Tab), reject an empty result silently, and apply a minimum-length guard so a partial read is not looked up as a real number. Case handling and the min/max length are developer decisions.

**Multi-value paste.** A paste whose content contains newline separators is treated as **several scans submitted in order**, one row and one verdict each (E-69) — this is what an operator recovering from a handheld batch actually wants. A single-value paste behaves exactly like one scan. A cap on the number of values accepted in one paste is a developer decision.

**Server action.** `closing.scan(tracking, scan_id)` where `scan_id` is a client-generated per-submit identifier used as the idempotency key [G-9]. The server assigns the sequence number atomically (see `[L-S1-6]`), evaluates the verdict (§3.6), appends the row, updates counters, and returns the rendered row + counter deltas.

**Double-Enter vs a genuine duplicate.** Two submits of the same value are two scans and must produce a duplicate warning — that is the feature. A wedge that fires Enter twice on one read is not. The client therefore suppresses a second submit only when the value is identical **and** it arrives inside a short debounce window **and** no `input` event occurred in between; anything else is submitted (E-54). The window length is a developer decision.

**In-flight behavior** (`[BR-26]`): the input must **not** lock while a lookup is in flight. Either scans queue client-side and are submitted in order, or they are submitted concurrently and rendered in server-assigned sequence order — developer decision (DQ-1). Scanning speed is never gated on network latency. A verdict that has not returned yet renders as a pending row; it must never render as an OK.

**Feedback per verdict** — see §3.6 for the matrix, §3.3 for the OK line, §3.4 for the voice.

**Persisted.** DC-7 `closing.scan_recorded` (every verdict), DC-10 `closing.warning_raised` (warning verdicts), DC-9 `closing.scan_lookup_failed` (transport/lookup failure), DC-8 `closing.scan_rejected` (no active session / session already confirmed / session cancelled underneath the operator).

---

### 3.3 `[L-S1-2]` — OK-scan confirmation line

**Trigger.** A scan whose verdict is OK.

**Rendering.** A compact one-line green bar (`.okline`) directly beneath the voice bar, replacing the previous OK line:

`✓ #{seq} Outbounded` · `Order {order_id} · Tracking {tracking} · {status}` · right-aligned `{hh:mm:ss} · {worker}`

Wireframe example, byte-exact: **"✓ #5 Outbounded"** / "Order 413540 · Tracking YT2618100710108810 · Prepare Shipment" / "18:41:07 · Dean".

**And a green toast** [G-2]: "✓ Outbound confirmed — {tracking}" / "Ready for the next barcode scan".

**Silent by design** — no sound on OK `[G-3b]` (§3.4).

**No large panel.** The large OK panel was removed on 2026-07-23 (Dean): only warnings need recognition from a distance. **Net truth: no large red panel exists anywhere on this page; the only large panel is State 4's green completion status** (adjudication C-10). State 1 legend #2 used to claim the large panel is "used only in warning states" — stale text corrected in the wireframe on 2026-08-03 (`[WF-5]` fixed); the legend now states the net truth.

**No modal, no focus steal, no scroll jump** on an OK scan. The operator is not looking at the screen; anything that moves focus breaks the loop.

---

### 3.4 `[L-S1-3]` — Voice alert toggle

**Rendering.** A switch labelled `Voice alert: {On|Off} — plays "Please check this order" automatically on warnings`, plus the button **"🔊 Test voice"**. (The wireframe labels the same control "🔊 Play again" inside the three warning states — demo copy, U-h; the canonical label is "🔊 Test voice" everywhere.)

**Behavior** — page delta to `[G-3b]`:
- **Default ON** at every session start.
- ON: any warning verdict (not outbounded / duplicate / unknown / ambiguous) automatically speaks the fixed utterance **"Please check this order"**, `lang = "en-US"`. The phrase is fixed copy confirmed 2026-07-23 and re-confirmed 2026-08-03; it is never templated with the tracking number (it must be understandable at a distance, not parsed).
- OFF: warnings still render the red row, the red pill and the red toast. **The visual warning is never suppressed** — the toggle governs audio only.
- Turning the toggle **ON** speaks one confirmation utterance immediately (so the operator knows audio works).
- **"🔊 Test voice" plays the utterance regardless of the toggle state** and does not change the toggle. This is deliberate: the operator tests audio without disturbing the setting.
- Rapid consecutive warnings: the wireframe cancels the previous utterance and speaks the new one (`speechSynthesis.cancel()` then `speak`). Cancel-and-speak vs queue, and the voice-selection fallback chain (wireframe: `Samantha` → any `en-US` voice → browser default), are developer decisions (DQ-4/DQ-8).
- **TTS unavailable** (no voices, unsupported browser, muted device): no JS error, no blocking dialog, visual warnings unaffected (E-39).
- The control is rendered on **every** state in the admin; the wireframe wires it only in State 1 while keeping `voiceOn` as a page-global (U-g).

**Persistence scope** of the toggle (per device vs per user profile) is a developer decision (DQ-3); the default is ON at the start of every session regardless of scope, so a colleague's OFF never carries silently into a new day (E-61).

**Persisted.** DC-20 `closing.voice_alert_toggled` (old → new). Test-button plays and TTS utterance events are **NON-events** (§5.3).

---

### 3.5 `[L-S1-4]` — Progress tiles and bar

**Four tiles**, canonical labels (fixing the inconsistency U-d):

| Tile | Label | Value |
|---|---|---|
| 1 | `Today's outbound target (manual input)` | `target` — the hand-counted number |
| 2 | `OK (outbounded)` | `ok_count` — rows whose current verdict is OK and which are not deleted |
| 3 | `Warnings (not outbounded · duplicate · unknown order)` | `outstanding_warnings` |
| 4 | `Remaining scans` | `max(0, target − ok_count)` |

On State 4 tile 3 is relabelled `Warnings (resolved)` and shows `0`.

**Formulas.**
```
ok_count             = |{rows : verdict == OK, deleted == false}|
outstanding_warnings = |{rows : verdict != OK, deleted == false}|
warnings_raised      = |{rows : verdict != OK ever assigned}|   // cumulative, never decremented
remaining            = max(0, target − ok_count)
over_by              = max(0, ok_count − target)
progress_ok_pct      = ok_count / target * 100                  // one decimal
progress_warn_pct    = outstanding_warnings / target * 100      // one decimal
confirm_enabled      = (ok_count == target) AND (outstanding_warnings == 0)
```

These formulas reproduce the wireframe's own rendered percentages exactly: 3/84 → 3.6% and 2/84 → 2.4% (State 1); 4/84 → 4.8% and 3/84 → 3.6% (States 2 and 3); 4/84 → 4.8% twice (State 2b). Only the State 1 "Remaining scans" tile disagrees with them (U-a).

**`outstanding` vs `raised` is a load-bearing distinction** (`[BR-16]`): the gate uses *outstanding*; Closing History and the Warning Resolution Summary use *raised → resolved*. This is why State 4 can show "Warnings 0" in the tiles and "3 warnings today" in the summary, and why History shows `3→3` for the same day.

**Progress bar.** A single 14px track with a green segment (`progress_ok_pct`) followed by a red segment (`progress_warn_pct`). Beneath it, the `.proglab` sentence carries the live numbers and the gate rule, e.g. "Closing progress 3.6% — OK 3/84 (81 short of the manual count) · 2 warnings to resolve — **closing confirms only at an exact OK 84/84 match with 0 warnings; over-scan is also a mismatch**". In the over-scan state the sentence states the excess instead of the shortfall.

**Recompute triggers** (all without a page refresh [G-2]): a scan verdict, a row deletion (M2), an M1 resolution, a target edit, and an inbound sync from another operator's station.

**Wireframe caveat U-a.** State 1's "Remaining scans" tile shows `79` where the formula gives `81`, and the wireframe does not recompute tiles after a row is deleted (documented demo limitation). `[WF]` QA asserts the rendered demo values; `[ADMIN]` QA asserts the formulas.

---

### 3.6 `[L-S1-5]` — Verdict rule

**One rule decides everything** (2026-07-23): a scan is OK **only** when the matched order's status is `Prepare Shipment`. Every other outcome is a warning. This replaces the current process's manual "was it outbound-processed?" check.

**Verdict matrix.**

| Condition (evaluated in this order) | Verdict | Pill (byte-exact) | Row tint | Voice | Counts toward OK | M1 button |
|---|---|---|---|---|---|---|
| Tracking already recorded in this session on a non-deleted row (**whatever that row's verdict**) | `duplicate` | `⚠ Duplicate scan` | red | yes | no | no |
| No order matches the tracking number | `unknown` | `⚠ Unknown order` | red | yes | no | no |
| Tracking matches **more than one** order | `ambiguous` | `⚠ Unknown order` (default) | red | yes | no | no |
| Order status = `Prepare Shipment` | `ok` | `✓ Outbounded` | green | **no** | **yes** | no |
| Order status = `Processing` | `not_outbounded` | `⚠ Not outbounded` | red | yes | no | **yes** |
| Order status ∈ {`Pending`, `On Hold`, `Shipped`, `Completed`, `Refunded`, `Failed`} | `not_outbounded` | `⚠ Not outbounded` | red | yes | no | no |
| Order carries the **cancellation flag** (any underlying status) | `not_outbounded` | `⚠ Not outbounded` | red | yes | no | no |

- **`Cancelled` is not an order status.** The vocabulary is exactly the 8 WooCommerce statuses `pending` · `processing` · `on-hold` · `completed` · `refunded` · `failed` · `shipped` · `prepare-shipment`; cancellation is a separate flag set by `✕ Cancel Order` on Order Detail (OD `BR-12`, `view-orders.md` L-S4-6), not a ninth value. A cancelled order therefore renders its **underlying status** in the Order Status column with a `Cancelled` marker beside it, and the verdict is `not_outbounded` in every case. Corrected 2026-08-03 (cross-page defect M3a-D3); the register title of `[PD-76 · OWNER-PENDING]` still lists "Cancelled" among the statuses and needs the same correction at the owner's next pass — the behavior specified here is the corrected one.
- Duplicate is checked **before** status, so rescanning an already-scanned OK parcel yields a duplicate warning, not a second OK (`[BR-5]`). The check is against any non-deleted row with the same normalized tracking, regardless of that row's verdict — two unknown scans of the same bad label produce one `unknown` and one `duplicate` (E-70).
- The dedupe scope is **the current session only** (`[BR-37]`). A parcel scanned in yesterday's confirmed closing and scanned again today is not a duplicate; its order will normally be `Shipped`/`Completed`, so it warns as `⚠ Not outbounded` — which is the correct signal, because a parcel that already left should not be on today's bench (E-63).
- Abnormal non-`Processing` statuses (and the cancellation flag) share the `⚠ Not outbounded` pill; the **actual status is rendered in the Order Status column**, which is where the operator reads the difference. `[Process this order]` appears **only** for `Processing`, because M1 is specifically a `Processing → Prepare Shipment` transition and offering it elsewhere would produce an invalid mutation `[PD-76 · OWNER-PENDING]`.
- **Ambiguous** (one tracking number on two or more orders — carrier number reuse or a data error, E-14): the server must never silently pick one. The row is a warning, excluded from OK, and the Notes cell lists every colliding Order ID. Reusing the `⚠ Unknown order` pill is the default because it introduces no new UI vocabulary and preserves the count-exclusion semantics; a distinct label is a developer decision (DQ-2).
- **This page matches customer-order (outbound) carrier tracking numbers only.** Inbound-request tracking numbers live in a **separate namespace** and may legitimately collide with outbound ones `[PD-8 · OWNER-PENDING]`; a scan here resolves against outbound tracking and nothing else, so an inbound-request number scanned at closing is `unknown`, never a match (E-13). A product EAN (`8809…`), an Order ID or a Deleo number likewise resolves to `unknown`. There is no unified search on this page.

**Persisted.** DC-7 with `verdict`, `order_status_at_scan`, and (duplicate) `duplicate_of_seq` / `first_scan_at` / `first_scan_actor` / `first_scan_verdict`.

---

### 3.7 `[L-S1-6]` — Scan list

**Ten columns**, in order: `#` · `Scan Time` · `Tracking Barcode` · `Order ID` · `Items` · `Order Status` · `Closing Verdict` · `Worker` · `Notes` · (44px action column, unlabelled).

| Column | Contract |
|---|---|
| `#` | Server-assigned sequence, **cumulative from 1** for the session, ascending, new rows appended at the bottom. Grey, bold. |
| `Scan Time` | `hh:mm:ss`, the server's receipt time in the warehouse timezone, tabular numerals |
| `Tracking Barcode` | the normalized scanned value, never truncated (E-50) |
| `Order ID` | blue, a **real deep link** to the order detail screen [G-12], opened in a **new tab** while a session is `IN_PROGRESS` so the scan loop survives (E-74); `–` when unknown |
| `Items` | total unit count on the order; `0` for a zero-line order; `–` when unknown |
| `Order Status` | the status pill at scan time (`Prepare Shipment` green, `Processing` red-outlined, others per admin palette); `–` when unknown; a cancelled order renders its underlying status label plus a `Cancelled` marker (§3.6) |
| `Closing Verdict` | the verdict pill from §3.6 |
| `Worker` | the scanning actor's display name (mock: Dean / Miranti) |
| `Notes` | verdict-specific, below |
| action | `button.scandel`, label `✕`, title "Delete scan row" → M2 |

**Notes content by verdict** (wireframe strings are canonical where they exist):

| Verdict | Notes |
|---|---|
| `ok`, first scan of a tracking that later gets duplicated | `First scan` — applied **retroactively** to the earlier row the moment a duplicate arrives; it is an annotation, not a verdict change, and it does not touch counters or the sequence number |
| `ok`, otherwise | `–` |
| `duplicate` of an OK row | **`Duplicate of #{n}`** ` — first scanned {hh:mm:ss} ({worker})` (State 3 form). The State 1 mock variant "**Duplicate of #2** — same tracking no. (check for combined box)" is an earlier phrasing; **the canonical string carries the first scan's time and worker**, because those are the three facts a human needs to judge a combined box. |
| `duplicate` of a non-OK row (E-70) | **(spec-authored)** **`Duplicate of #{n}`** ` — first scanned {hh:mm:ss} ({worker}) · that scan was {verdict}` |
| `unknown` | `Mistyped tracking no. or an order from another system — check the physical label` |
| `ambiguous` | **(spec-authored)** `Matches {n} orders — {id1}, {id2}, … — resolve before closing` |
| `not_outbounded`, status `Processing` | the button `[Process this order]` (opens M1) |
| `not_outbounded`, other status | **(spec-authored)** `Order status is {status} — not shipped from this closing` |

**Status label vs status value.** The 8 statuses are stored as **lowercase-hyphenated values** (`pending` · `processing` · `on-hold` · `completed` · `refunded` · `failed` · `shipped` · `prepare-shipment`) and rendered as **title-case labels**. This spec uses the label register in prose and in every rendered string, and the value register in every `DC-*` payload (e.g. DC-13 `processing → prepare-shipment`). Mapping, in order:

| Value | Label |
|---|---|
| `pending` | `Pending` |
| `processing` | `Processing` |
| `on-hold` | `On Hold` |
| `completed` | `Completed` |
| `refunded` | `Refunded` |
| `failed` | `Failed` |
| `shipped` | `Shipped` |
| `prepare-shipment` | `Prepare Shipment` |

There is no `cancelled` value in either register (§3.6). Stated once here (cross-page defect M3a-D19, 2026-08-03) so `[BR-20]`'s mixed registers read unambiguously.

**Sequence-number rules** (`[BR-17]`): numbers are never reused and never renumbered. Deleting row #3 leaves #1, #2, #4, #5 — this keeps every duplicate cross-reference ("Duplicate of #2") stable forever, and keeps the printed/exported record aligned with what the operator saw. Gaps in the sequence are therefore normal and are **not** a defect.

**Deleted rows** disappear from the table and from all counters, and are retained server-side in full (§3.22).

**Footer line beneath the table** (byte-exact): "Sequence (#) = cumulative from 1 after closing starts · lowest first · all rows stored in the backend (fully included in the closing report export)".

**Layout.** No horizontal scroll (`[L-S1-9]`). The table renders inside `.mockwrap` which scrolls at <1280px, but the design constraint is that at the warehouse station resolution every column including the verdict is visible without scrolling.

**Scale.** Several hundred rows must stay usable at scan speed (E-60): the newest row is appended at the bottom and kept visible without stealing focus. Pagination vs virtualization is a developer decision (DQ-9); if paginated, the latest page is the default during an active session.

---

### 3.8 `[L-S1-7]` — Comments hub (top bar)

Behavior is global [G-7]; only the closing deltas are specified here.

**Closing deltas:**
- The hub is the aggregation point for the **closing-exception communication trail**: M1 memos, combined-box duplicate reasons, and any comment posted from a closing context.
- Every comment posted from this page targets an **order** entity (the order behind the scanned tracking number). Closing sessions are **not** a commentable entity type in v1 — there is no "comment on the closing" affordance.
- Clicking a hub entry opens the entity (the order), not the closing row.
- Comments are **append-only** — no edit, no delete `[PD-3 · OWNER-PENDING]`.
- Opening the hub never steals focus from the scan input and is never auto-closed by an arriving verdict (E-75).

**Rendering.** A nav button "💬 Comments" carrying an unread-mention badge (mock `2`), opening a dropdown with tabs `@ Mentions` (badge `2`) and `★ Saved`. Each row shows the entity (`Order 413540`), the author, the comment text, a time, and a `★` toggle. The dropdown is wired only in State 1 in the demo (U-e); in the admin it is identical on every state.

**Hub copy is a cross-page byte-exact contract [G-7]** `[WF-15]`. The hub is the same component on all eight screens, so closing carries no wording of its own — the strings below are quoted from `[G-7]` v1.2, which publishes them as HUB-1…HUB-7:

| Element | `[G-7]` id | Canonical string | Wireframe before the 2026-08-03 fix |
|---|---|---|---|
| Mentions pane header | HUB-1 | `Comments mentioning me · Click to open the order` | `Comments where I'm tagged` |
| Saved pane header | HUB-2 | `Saved comments · Click to open the order` | `Comments I saved` |
| Unstar hint | HUB-3 | `Unstar to remove from the list` | `Unstar to remove from this list` |
| Read-all action | HUB-4 | `Mark all read` | `Mark all read` (already canonical) |
| Search results header | HUB-5 | `{n} results · newest first · click to open the order` | not built (U-c) |
| Empty search state | HUB-6 | `No matching comments` | not built (U-c) |
| Search placeholder | HUB-7 | `🔍 Search all comments — order no. · author · text` | not built (U-c) |

Cross-page defect M3a-D7 found closing and inbound-request to be the two outliers on the pane headers. `[G-7]` v1.2 resolved the whole set on 2026-08-03 and `[WF-15]` was applied to `wms2/closing/index.html` in the same commit, so **`[WF]` (QA-HUB-01/02) and `[ADMIN]` (QA-HUB-09) now assert the same strings** on the four elements this wireframe builds. The last three remain `[ADMIN]`-only because the search pane itself is unbuilt here (U-c).

**Full-text search across all comments** (entity no. / author / text, newest first, click opens the entity) is required by [G-7] but is **not built in this wireframe** (U-c). It ships in the admin; its QA is `[ADMIN]`.

**Persisted.** DC-15 `comment.posted`, DC-16 `comment.auto_posted`, DC-17 `comment.mention_notified`, DC-18 `comment.starred` / `comment.unstarred`, DC-19 `comment.read` / `comment.mark_all_read`.

---

### 3.9 `[L-S1-8]` — Confirm Closing button

**Location.** A green-tinted banner at the bottom of the scan area, containing the label "Confirm Closing", the explanatory sentence, and the button.

**Enable predicate** (server-evaluated, client-mirrored):
```
confirm_enabled = (ok_count == target) AND (outstanding_warnings == 0)
```

**Disabled label carries the blockers**, so the operator reads the reason off the button itself without hunting for it:
`Confirm Closing ({remaining} remaining · {outstanding_warnings} warnings)` — the wireframe's rendered string, byte-exact: **"Confirm Closing (79 remaining · 2 warnings)"**.
> **Not a worked example.** That `79` is the same bad demo datum as State 1's Remaining tile (**U-a**). Against target 84 / OK 3 the formula in §3.5 gives `remaining = 81`, so the shipped label would read "Confirm Closing (81 remaining · 2 warnings)". `remaining` is **never** `target − ok − warnings`; warnings never subtract from Remaining (QA-COUNT-04). The string above is quoted only because QA-CONFIRM-01 asserts it byte-exactly against the demo.
- When only warnings block: `Confirm Closing ({n} warnings)` **(spec-authored)**.
- When only the count blocks: `Confirm Closing ({n} remaining)` **(spec-authored)**.
- **Over-scan** (`ok_count > target`): `Confirm Closing ({n} over target)` **(spec-authored)**. Over-scan is a mismatch, not a pass (`[BR-3]`).
- Enabled: `Confirm Closing`.

**Enabled ≠ confirmed** (`[BR-4]`). Reaching an exact match only enables the button. A human must press it after satisfying themselves that everything was scanned. The scan input **stays live after the match** precisely so that an 85th parcel found on the floor can still be scanned — which flips the state to over-scan and re-disables the button. Resolution paths from over-scan: [↺ Edit count] to the true number, or delete the extra rows.

**On click.**
1. Client debounce; `closing.confirm(session_id, target_at_press, idempotency_key)` [G-9]. Exactly one closing record can exist per session even under a double click or a retried request (E-31, E-37).
2. **Server revalidates** the whole gate against live state before writing `[PD-6 · OWNER-PENDING]`: counts recomputed server-side, the target compared with `target_at_press` (so an edit that landed mid-flight cannot be confirmed against a stale number, E-73), and every OK row's order re-checked for a status that changed since the scan. On mismatch the confirm is **rejected** — red toast **(spec-authored)** "✕ Cannot confirm — {reason}" (e.g. "order 413540 is no longer Prepare Shipment"), the affected rows are re-judged and re-rendered in place, no partial write occurs, and DC-22 `closing.confirm_rejected` is persisted.
3. On success: session → `CONFIRMED`; an immutable snapshot is written (DC-23); Closing History gains the day's row (§3.20) — **there is no external sheet write** (`[PD-71]` resolved 2026-08-03, §6.4); the screen re-renders as State 4 **without a page refresh** [G-2].
4. Green toast (byte-exact from the wireframe): "✓ Today's closing confirmed — 84/84 orders" / "Closing record saved · replaces the retired Daily Shipping Status sheet" → generalized: "✓ Today's closing confirmed — {ok}/{target} orders" / same subtext.

**Persisted.** DC-21 `closing.confirmed`, DC-23 `closing.snapshot_created`, DC-22 on rejection. (DC-24 is retired — §5.1.)

---

### 3.10 `[L-S1-9]` — Reduced side margins / single-screen layout

The page uses reduced side padding so that **all ten scan-list columns including Closing Verdict fit on one screen without horizontal scrolling** at the warehouse station resolution. This is an operator requirement, not cosmetics: during scanning, a horizontal scrollbar means the verdict column can be off-screen, which silently defeats the whole screen.

Implementation constraints: no column may be dropped in any state (the column set is identical across States 1, 2, 2b, 3 and 4); long tracking numbers are never truncated (E-50); if the viewport is genuinely too narrow, the **table** — not the page body — scrolls.

---

### 3.11 `[L-S1-10]` — Locked target banner: Edit count / Cancel Closing

**Rendering.** A blue info banner above the scan input: "① Today's Outbound Target (manual count)" · "Closing in progress (started {hh:mm} · {starter}) — the OK-scan count must **exactly match** this number to confirm closing" · a locked numeric field showing the target · the word "orders" · `[↺ Edit count]` · `[✕ Cancel Closing]`.

The banner is present in **every `IN_PROGRESS` rendering** — States 1, 2, 2b and 3 alike. The wireframe renders the full banner only in State 1 and a muted one-line summary in the warning states (U-j); that is demo shorthand, not a behavior.

The starter's name and start time are shown because the confirmer is often not the starter (mock: started 18:02 Dean, confirmed 18:52 Yongwon).

**Edit count.**
1. `[↺ Edit count]` unlocks the numeric field, focuses it, selects its content; the button label becomes `Save`.
2. Validation is identical to §3.1 (integer ≥ 1). Invalid → the old value is kept, the field stays in edit mode, red toast **(spec-authored)** "✕ The count must be a whole number of 1 or more", DC-4 `closing.target_edit_rejected`.
3. `Save` → `closing.editTarget(new_target)`; the field re-locks, the label returns to `↺ Edit count`.
4. All counters, the progress bar and the confirm gate recompute **instantly** — no refresh. Editing the target to exactly `ok_count` with zero outstanding warnings enables Confirm without any new scan (E-18). Editing it below `ok_count` produces the over-scan state and re-disables Confirm (E-17).
5. Green toast **(spec-authored)**: "✓ Target updated — {old} → {new} orders".
6. Editing is allowed at any time while the session is `IN_PROGRESS`, including after a match has been reached (`[BR-14]`). Scanning continues normally while the edit field is open (E-51).

**Persisted.** DC-3 `closing.target_edited` with `old_qty → new_qty`. The old value is captured even though the UI shows only the new one — this is exactly the kind of silent-capture the data doctrine [G-8] exists for: "the target was quietly raised at 18:49" is the signal an auditor needs.

**Cancel Closing.** `[✕ Cancel Closing]` is destructive and therefore takes a confirm step `[PD-5 · OWNER-PENDING]` — `[WF-7]` fixed 2026-08-03: the wireframe now opens the dialog (`#m-cancel`) with the copy below (the demo renders the scan-count clause with its five mock rows, "5 scans will be removed from this session.").

Confirm dialog (copy now shipped in the wireframe):
> **Cancel today's closing?**
> {n} scans will be removed from this session. The scan records are kept in the audit log and can be reviewed later, but the session will restart from the count entry.
> [ Keep scanning ] [ Yes — cancel closing ]

- Confirmed → `closing.cancel()`; session `IN_PROGRESS → CANCELLED`; the screen returns to State 0 with an empty count input; green toast **(spec-authored)** "✓ Closing cancelled — {n} scans discarded" / "Scan records are kept in the audit log".
- The dialog is shown **even when zero scans exist** (E-21) — with the count clause omitted — because the operator's mental model must be "cancel always asks", never "cancel sometimes asks".
- **Scan rows are never deleted by a cancel.** They are retained server-side with the cancelled session `[PD-70 · OWNER-PENDING]`; only the working session state resets. Cancelled sessions are not displayed in Closing History.
- Starting again the same day after a cancel is allowed and creates a **new** session linked to the cancelled one (DC-6 `closing.session_restarted`).
- A colleague scanning into the session at the moment it is cancelled gets an explicit rejection, never a silent new session (E-34).

**Persisted.** DC-5 `closing.session_cancelled` (with the discarded row count and the retained row ids), DC-6 on the subsequent start.

---

### 3.12 `[L-S1-11]` — Top tabs [Closing | Closing History]

Two in-page tabs beneath the page header: `Closing` (active) and `Closing History`.

- `Closing History` navigates to the **separate history page** (`#shist`), not a modal. This was converted from a modal on 2026-07-23 — see the reversal row in §10.
- Returning via the `Closing` tab restores **the closing view the operator was on** (the wireframe implements this as `lastState`, initialised to `s0`; the admin restores the live session state).
- Tab switching is a navigation, not a mutation: no data is written, the session is untouched, and the scan session survives because it lives server-side (`[BR-8]`).
- Tab switches are **NON-events** (§5.3).

---

### 3.13 `[L-S1-F]` — Off-screen behavior rules (normative)

The State 1 legend footer is a normative paragraph, not decoration. Every clause is binding:

1. **The scan input is disabled until closing starts** (a manual count has been entered). Keyboard-wedge input goes nowhere.
2. **Click-anywhere refocus.** After the session starts, clicking any non-interactive area of the page returns focus to the scan input with the whole value selected. **Exclusions** (E-48): the target-edit field, the M1 memo textarea and its checkbox, the M2 modal, the Comments hub and its search box, and any comment input. Refocus resumes automatically when a modal closes or a field blurs. A refocus must never steal a character the operator is typing into one of those fields.
3. **Verdicts render as a top-right toast with no reload** [G-2].
4. **Verdict semantics**: `Prepare Shipment` = OK (green, silent); anything else, or an already-scanned tracking number, is a warning (red, voice).
5. **Gate**: OK count exactly matches the manual target **and** zero outstanding warnings; **over-scan is also a mismatch**.
6. **Reaching the match only enables the button** — it never auto-closes. The scan input stays alive after a match so an extra parcel flips the state back to mismatch.
7. **M1 is a real order-status change** reflected on every screen, not a closing-local flag.
8. **A tracking number with no matching order is an "unknown order" warning** (State 2b) and is excluded from the closing count.
9. **Closing progress is stored server-side.** Navigating away, refreshing, crashing, or switching devices preserves the target, the scan list, the counters and the warnings. **Nothing clears until the closing is confirmed or explicitly restarted.** Every scan is written at scan time — never batched to confirm time (`[BR-27]`). This is an operator requirement, not a technical nicety: shift handovers and walks to Zero Packing happen mid-closing every day.
10. **Continuous scanning** — the page-local expression of [G-1]: the scanner's automatic Enter substitutes for the Scan button, the cursor returns to the scan input with the text fully selected, the next scan overwrites it, and the page never refreshes between scans.

---

### 3.14 `[L-S2-1]` — Warning · Processing (not outbounded)

**Trigger.** A scan matching an order whose status is `Processing`.

**Render.** Red-tinted row (`.row-bad`), Order Status pill `Processing`, Closing Verdict pill **`⚠ Not outbounded`**, and in the Notes column the button **`Process this order`** (red outline) which opens M1. The voice speaks "Please check this order" if the toggle is ON. A red toast **(spec-authored)**: "⚠ Not outbounded — {tracking}" / "Order {order_id} · {status}".

**Resolution happens in the list.** The large warning panel and the separate action banner were removed on 2026-07-23: verifying and handling in the row is enough, and it keeps the operator inside the scan loop. (`[WF-5]` — the State 1 legend text that contradicted this was corrected 2026-08-03.)

**Counting.** The row counts as an outstanding warning and does not count toward OK. Resolving it via M1 re-judges the row in place to `✓ Outbounded` (green tint), decrements outstanding warnings, and increments OK — **without changing the sequence number and without a page refresh**.

---

### 3.15 `[L-S2b-1]` — Warning · Unknown Order

**Trigger.** A scanned tracking number that matches no order in the system.

**Render.** Red-tinted row; `Order ID`, `Items` and `Order Status` all render `–`; Closing Verdict pill **`⚠ Unknown order`**; Notes: "Mistyped tracking no. or an order from another system — check the physical label"; voice plays. Red toast **(spec-authored)**: "⚠ Unknown order — {tracking}" / "Check the physical label and rescan".

**Counting.** Counts as an outstanding warning; **explicitly excluded from the closing count** — it can never contribute to `ok_count`, and it blocks confirmation until it is resolved.

**Prescribed operator procedure** (keep this copy — it encodes a physical action, not a UI hint): recheck the physical label (mistype vs a parcel from another system) → rescan → if still not found, escalate to a manager. The row is cleared with `✕` (M2) once the operator has decided what it was.

**No retro-judgment.** If the missing order is created in the system later in the session, the unknown row is **not** re-judged (same doctrine as `[BR-22]`); the operator deletes it and rescans the parcel, producing a clean, timestamped OK (E-57).

**Boundary — this is NOT the unrecognized-product flow** (`[BR-23]`, adjudicated non-issue in `_review.md`):

| | Closing "unknown order" | Unrecognized Tracking pool |
|---|---|---|
| What was scanned | a **carrier tracking number** that does not exist in the system | a **product barcode** on an arriving inbound item that maps to no expected line |
| Where it lives | a red row in today's closing scan list | the shared unrecognized pool page |
| Slack | **none** | `#unrecognized-tracking` |
| Resolution | recheck label → rescan → escalate → `✕` | match to a suspected order → writes the tracking number onto the order's product line |

A closing unknown **never** routes to `#unrecognized-tracking` and never creates a pool item.

---

### 3.16 `[L-S3-1]` — Warning · Duplicate Scan

**Trigger.** A tracking number already recorded on a non-deleted row of the current session.

**Render.** Red-tinted row; Order ID / Items / Order Status are populated from the matched order (the order is known — only the scan is a repeat); Closing Verdict pill **`⚠ Duplicate scan`**; Notes: **"Duplicate of #{n}"** followed by " — first scanned {hh:mm:ss} ({worker})"; voice plays. Red toast **(spec-authored)**: "⚠ Duplicate scan — {tracking}" / "First scanned {hh:mm:ss} ({worker}) · #{n}".

**Why the note carries three facts.** This is the digital replacement for the Excel column-A duplicate check, and a duplicate is a **judgment call**, not an error: a combined box legitimately ships two orders' contents under one tracking number. The colliding sequence number, the first scan's time and the first scanner's name are exactly what a human needs to decide "combined box" vs "I scanned the same parcel twice".

**Counting.** Duplicates are **never double-counted** toward OK. Each repeat scan produces its own warning row; a third scan of the same tracking references the **first** scan of that tracking (`#n`), not the previous duplicate (E-7). Because a combined box yields exactly one OK plus one duplicate, the OK count still equals the number of physical parcels, which is what the hand count measured (`[BR-33]`, E-65).

**Resolution** `[PD-69 · OWNER-PENDING]`: the operator logs the combined-box reason as a comment on the order (via the order's comment trail — the mock hub carries exactly this: Miranti's "@Yongwon 3 duplicate scans — combined-box orders, this is fine"), then removes the duplicate row with `✕` (M2). Deleting the row clears the outstanding warning; the **raised** counter is not decremented, which is why History shows `3→3` and State 4's summary says "3 warnings today" while the tiles read 0.

**If the original OK row is deleted instead** (M2 on the first scan), the surviving duplicate row is **not** auto-re-judged `[PD-75 · OWNER-PENDING]`: the operator deletes the duplicate too and rescans the parcel, producing a clean, timestamped OK. Retro-judging a past row would rewrite the meaning of the scan sequence.

---

### 3.17 `[L-S4-1]` — Closing Complete

**Trigger.** A successful `closing.confirm` (§3.9). This state is never reached automatically.

**Render.**
- Green toast: "✓ Today's closing confirmed — 84/84 orders" / "Closing record saved · replaces the retired Daily Shipping Status sheet".
- The **only large panel on the page**: `.bigstatus.bs-ok`, `✓` glyph, headline "Today's closing complete — all orders verified", meta line "Manual count {target} = OK scans {ok}, an **exact match** · {warnings} warnings · closing confirmed {YYYY-MM-DD HH:mm} ({confirmer})" (wireframe mock: "closing confirmed 2026-07-13 18:52 (Yongwon)"), and a right-hand block "Warnings **0** / Remaining scans 0".
- Tiles: target · OK · **`Warnings (resolved)`** · Remaining scans (all four, with the relabelled third tile).
- Progress bar at 100% green; `.proglab`: "Closing progress 100% — OK {ok}/{target} exact match + 0 warnings → closing confirmed · today's record saved to Closing History".
- The target banner's `[↺ Edit count]` and `[✕ Cancel Closing]` are **gone** — a confirmed closing is immutable.
- **The scan input is disabled** `[PD-73 · OWNER-PENDING]`. The wireframe renders an enabled-looking input (U-b); the shipping behavior is disabled, because a live input on a confirmed closing would produce scans belonging to no session. A wedge scan against a confirmed closing is rejected server-side and persisted as DC-8 `closing.scan_rejected` with a red toast **(spec-authored)** "✕ Today's closing is confirmed — scanning is closed".

**Snapshot.** On confirmation an immutable snapshot is written and appears as today's row on the **Closing History page**. (State 4 legend #1 used to say "(M2)" — a fossil of the pre-2026-07-23 history modal, pointing at the wrong artifact; corrected to "the Closing History page" on 2026-08-03, `[WF-4]` fixed.)

**Immutability and the one-session-per-day rule** `[PD-70 · OWNER-PENDING]`: after confirmation no second session may be started on the same calendar date; History carries exactly one row per date. The **correction path for a parcel found after confirmation is Amend Closing** (§3.24) — decided by the owner on 2026-08-03, resolving `[PD-74]`. Amendment reopens the **same** session from Closing History (`CONFIRMED → AMENDING`), so `[PD-70]` is upheld: never a second session, never a second row — the record is updated in place on re-confirm (`[BR-39]`–`[BR-42]`). Outside an amendment the lock stands exactly as written above.

**Session date attribution** `[PD-78 · OWNER-PENDING]`: a session started 23:50 and confirmed 00:10 belongs to the **start date** — the target count and the parcels are the start date's work (E-41). A session left open across a date boundary must be confirmed or cancelled before the next date's closing can start (`[BR-35]`, E-72), and a browser tab still showing a confirmed State 4 the next morning revalidates on its next interaction and can never write into the closed session (E-53).

**Persisted.** DC-21, DC-23.

---

### 3.18 `[L-S4-2]` — Closing Report (CSV)

**Rendering.** A green banner: "Closing Report" · "Exports today's closing result — replaces the manual copy/paste and formula-stripping into **SS Daily Shipping Status** (sheet retired 2026-08-03). A snapshot is saved automatically on closing confirmation." · button **"Download Closing Report (CSV)"**. The "(sheet retired 2026-08-03)" clause records the `[PD-71]` owner decision: the sheet no longer exists to be filled — this CSV **is** the downstream artifact.

**Behavior.** Clicking downloads the day's closing report as a CSV file, immediately, with no dialog. The snapshot itself is created at confirmation time (§3.17); the button re-renders that snapshot and never recomputes from live data — a report downloaded a week later must be byte-identical to one downloaded at 18:52.

**Contents.** The **full scan list**, including rows that were deleted, carrying at minimum: sequence #, scan time, tracking number, order ID, item count, order status at scan, verdict, worker, notes, deleted flag + deletion actor/time, plus a header block with date, target, OK count, warnings raised → resolved, closed-by and confirmed-at. The exact column order, the encoding (UTF-8 with BOM is recommended so Excel opens Korean text correctly), and the filename convention are developer decisions (DQ-5). The wireframe's own footer states the requirement: "all rows stored in the backend (fully included in the closing report export)".

**Failure.** A failed or empty export must never look like a silent success: red toast **(spec-authored)** "✕ Closing report could not be generated — try again" (E-40). A zero-scan day still produces a well-formed file with headers and no data rows.

**Not a print surface.** There is **no Print button on this page**; `[G-4]` instant printing does not land on closing `[PD-68 · OWNER-PENDING]` (adjudication C-4, global delta GD-9). `print.job_result` is therefore a declared NON-event here (§5.3), and "printer offline" is not an edge case on this page (E-49). If the owner reverses PD-68, the delta is exactly one button in this banner plus the [G-4] pipeline — nothing else in this spec changes.

**Persisted.** DC-25 `closing.report_exported` with `source ∈ {state4_button, history_row_csv}`.

---

### 3.19 `[L-S4-3]` — Warning Resolution Summary

**Rendering.** A blue info banner: "Warning Resolution Summary" followed by an aggregate sentence. Wireframe example: "3 warnings today — 1 Processing (413511, resolved after Outbound) · 2 duplicates (combined-box confirmed, logged in Comments). See the log and Comments for details."

**Content rules.** The sentence is generated, never typed:
- total **raised** warnings for the session (cumulative — not the outstanding count, which is 0 by definition here);
- a breakdown per verdict class (`not outbounded` / `duplicate` / `unknown order` / `ambiguous`), each with the count, the affected order IDs where known, and the resolution method (`resolved after Outbound` for M1, `row removed` for a deletion, with the comment reference where one exists);
- a closing pointer to the log and the Comments trail.
- Zero-warning day: **(spec-authored)** "No warnings today."

**This banner is a view over persisted events** [G-8], rendered from DC-10 `closing.warning_raised` joined to DC-11 `closing.warning_resolved` — it is never the only copy of that information.

---

### 3.20 `[L-SH-1]` — Closing History (separate page)

**Reach.** In-page tab `Closing History` from any closing state; the `Closing` tab returns to the closing view the operator was on. Converted from a modal to a page on 2026-07-23 (reversal recorded in §10).

**Intro line.** "Daily snapshots saved automatically on closing confirmation — an audit trail of outbound target (manual count) · OK scans · warning resolution · confirmer".

**Table columns**, byte-exact: `Date` · `Outbound Target (manual)` · `OK Scans` · `Warnings (raised→resolved)` · `Match` · `Closed By` · `Confirmed At` · (per-row action).

| Column | Contract |
|---|---|
| `Date` | the session's **start** date `[PD-78 · OWNER-PENDING]`; today's row is marked "(today)" and tinted green |
| `Outbound Target (manual)` | the target **at confirmation time** (after any edits) |
| `OK Scans` | equals the target on every row, by construction |
| `Warnings (raised→resolved)` | cumulative raised → resolved, e.g. `3→3`; a clean day shows `0` |
| `Match` | always `✓ Match` (`[BR-10]`) |
| `Closed By` | the confirmer |
| `Confirmed At` | `hh:mm` (may be past midnight for a session that crossed the date boundary, E-41) |
| action | buttons `CSV` — downloads that day's full report (§3.18) — and `Amend` (`button.amendbtn`) — opens M3 to start an amendment of that date (§3.24, `[L-SH-2]`) |

**Amended rows.** A row whose closing has been amended (§3.24) carries an **"Amended v{n}" badge** under its Date cell — amber pill, text `Amended v{n} · {amending actor} · {re-confirm MM-DD hh:mm}` (wireframe demo on the 07-12 row: "Amended v2 · Dean · 07-13 09:12"). The row's numbers always show the **latest** confirmed version; earlier versions stay reproducible (`[BR-42]`). While an amendment is open the row instead carries an "Amendment in progress" marker and keeps the v{n} numbers (E-80); rendering of that marker is a developer decision (DQ-13).

**Footer note** (byte-exact): "Closing cannot be confirmed while mismatched, so records are always saved as "Match" — mismatch causes (missed scans · over-scans · unresolved warnings) must be resolved before confirmation."

**What History does not show.** Days with no closing simply have no row — gaps are legitimate and must never be back-filled with fabricated rows (E-43), and a zero-shipment day is one of those gaps (`[BR-34]`, E-76). Cancelled sessions are retained server-side [G-8] but are **not displayed** `[PD-70 · OWNER-PENDING]` (E-45). There is exactly one row per date.

**Empty state** (first use, E-44): **(spec-authored)** "No closing records yet — the first confirmed closing will appear here." No CSV buttons and no Amend buttons are rendered.

**Retention.** Indefinite. Every historical row must remain reproducible as a CSV forever (§5.4).

**Persisted.** Reading History is a NON-event; DC-25 is persisted when a row's CSV is downloaded.

---

### 3.21 `[L-M1]` — Modal: Process Processing Order

**Trigger.** `[Process this order]` in the Notes cell of a `Processing` warning row.

**Header.** "Process Processing Order — Order {order_id}" (wireframe: "…— Order 413511"), with an `✕` close control.

**Body.**
- Bold statement: "This order has not been outbound-processed yet."
- Context line: "Tracking {tracking} · {n} item(s) · Status `Processing`".
- **Zero Packing checkbox**, label: "**Packing status of this order verified at Zero Packing** — check when proper packing is confirmed (step 6 of the current closing process)".
- **Memo (Optional)** textarea, placeholder: "Packing status and actions taken — if written, it is also recorded to the order's Comments history and the closing log".
- Blue note: "Processing Outbound **changes the real order status Processing → Prepare Shipment** (immediately reflected on every screen — order detail, View Orders, etc.). In the closing list this row is re-judged as green **"Outbounded"**. If packing is incomplete, handle it separately and rescan."

**Footer.** `[Close]` (secondary) and `[Process Outbound → resolve warning]` (green primary).

**Gate.** `[Process Outbound → resolve warning]` is enabled **only when both conditions hold**:

```
m1_enabled = zero_packing_checked
             AND every(line.inbound_status == INBOUNDED) AND line_count >= 1
             AND order.status == processing
             AND not order.cancelled
```

1. **Zero Packing attestation** `[PD-77 · OWNER-PENDING]` — the checkbox is step 6 of the current closing process; an unchecked attestation would make the resolution meaningless.
2. **Inbound completeness** (`[BR-38]`) — M1 emits the canonical `order.outbounded` (DC-14), and the outbound predicate is global: View Orders `BR-9` and `order-detail.md` L-9 both state it as **iff every line is INBOUNDED**. Closing may not open a side door through that gate. When the order has any `PENDING` line the button stays disabled and the modal shows the reason **(spec-authored)**: "Cannot outbound — {n} of {m} items are not inbounded yet. Receive them on Order Detail first." The scan row's verdict stays `⚠ Not outbounded` and the warning stays outstanding (E-78). Added 2026-08-03 after cross-page defect M3a-D2; before this the closing gate was Zero Packing alone, which contradicted both other specs.

Neither condition is enforced by the wireframe — both are spec-level requirements, QA `[ADMIN]` (QA-M1-05, QA-M1-14).

**On confirm.**
1. `closing.processOutbound(order_id, zero_packing_verified, memo, idempotency_key)` — double-click safe [G-9] (E-25).
2. **A real order-status mutation** `Processing → Prepare Shipment`, propagated to every screen (View Orders, Order Detail, Order Management, Ready to be Outbounded) — never a closing-local flag (`[BR-7]`).
3. The closing row is **re-judged in place** to `✓ Outbounded`, keeping its original sequence number and scan time; tiles and gate recompute; **no page refresh** [G-2].
4. Green toast **(spec-authored)**: "✓ Order {order_id} outbounded — warning resolved" / "Status changed Processing → Prepare Shipment".
5. **Audio.** This is an outbound-class button, so it plays the `[G-3a]` send sound `[PD-2 · OWNER-PENDING]`. Note the tension the owner is being asked to resolve: PD-2's enumeration names View Orders, RTO, Order Detail and Inventory and does **not** name closing, while adjudication C-5's verdict is scope-by-button-class ("every outbound-class button on every page"), which does reach this button. This spec applies the rule by class. Because closing's audio channel otherwise means "there is a problem", the sweep must be **audibly distinct** from the `[G-3b]` warning voice — a success sound mistakable for a warning would be worse than silence. Reversal impact if the owner scopes PD-2 by page instead: delete this clause; nothing else changes.
6. **Memo routing**: a non-empty memo is dual-written to (a) the order's Comments history and (b) the closing log; `@mentions` inside it route per [G-7] (§6.1). An **empty** memo still produces a system auto-comment on the order recording the closing-driven transition (DC-16, `source=system`), so the order's trail always explains why its status moved at 18:44.

**Stale-state handling** (E-24) `[PD-6 · OWNER-PENDING]`: if the order already left `Processing` (another operator outbounded it from View Orders while the modal was open), the server performs **no second transition**. If it is now `Prepare Shipment`, the call succeeds idempotently, the row is re-judged green, and the toast reads **(spec-authored)** "✓ Order {order_id} was already outbounded — warning resolved". If it moved to any other status, the call is rejected: red toast **(spec-authored)** "✕ Order {order_id} is now {status} — cannot outbound from closing", the row is re-judged against the current status, and nothing is written except the rejection record. If the order was **cancelled** while the modal was open (the cancellation flag, not a status — §3.6), the same rejection applies with the toast **(spec-authored)** "✕ Order {order_id} is cancelled — cannot outbound from closing" (E-56). A line that was un-inbounded meanwhile (Cancel Inbound from another screen) is rejected the same way, with the `[BR-38]` reason string.

**Close paths.** `[Close]`, the header `✕`, and a backdrop click all dismiss with **zero** side effects — no status change, no comment, no event (a dismissed modal is a NON-event). Focus returns to the scan input on close (`[L-S1-F]` clause 2).

**Persisted.** DC-13 `order.status_changed` (old → new, `source=closing_m1`, `zero_packing_verified`), DC-14 `order.outbounded` (canonical action event, same correlation id), DC-11 `closing.warning_resolved` (`method=m1_outbound`), DC-15/DC-16 for the memo or auto-comment, DC-17 if it mentions someone.

---

### 3.22 `[L-M2]` — Modal: Delete Scan Row

**Trigger.** The per-row `✕` (`button.scandel`, title "Delete scan row").

**Body.** Header "Delete Scan Row"; bold question "Remove this scan?"; identity line `#{seq} · {tracking}` (wireframe `#scandelInfo`, e.g. "#7 · YT2618100719984412"); blue note: "Deleting excludes it from the list and the closing counts — for clearing mis-scans, unknown orders, etc. **Deletion history is kept in the backend.**"

**Footer.** `[No]` (secondary) and `[Yes — remove]` (red primary).

**On `[Yes — remove]`.**
1. `closing.deleteScan(row_id, idempotency_key)` — idempotent; a repeat delete of the same row is a no-op success, never an error (E-29, E-58).
2. The row is removed from the table; **all counters, the progress bar and the confirm gate recompute immediately** — deleting an OK row can break an exact match and re-disable Confirm (E-27); deleting a warning row can newly satisfy the gate (E-28); deleting every row leaves the session `IN_PROGRESS` with all counters at zero (E-68).
3. **Sequence numbers are not renumbered** (`[BR-17]`): remaining rows keep their original numbers, so "Duplicate of #2" never dangles.
4. Green toast **(spec-authored)** [G-2] `[PD-5 · OWNER-PENDING]`: "✓ Scan #{seq} removed" / "Deletion history is kept in the backend".
5. **Soft delete only.** The full original row payload is retained server-side forever and appears in the CSV export with a deleted flag. "Deletion history is kept in the backend" is a verbatim owner requirement, not an implementation hint.

**On `[No]` / `✕` / backdrop.** Zero change — modal closes, row stays, no event (NON-event).

**No reason enum.** Unlike the Unrecognized Tracking removal (`[PD-60]`), a closing row deletion takes **no reason field**: it happens at scan speed, mid-loop, and the row's own verdict already records what was removed. The judgment trail for a duplicate lives in the order's comments (§3.16).

**Wireframe caveat.** The demo removes the DOM row but does **not** recompute the tiles (documented limitation) — `[WF]` QA asserts DOM removal only; recomputation is `[ADMIN]`.

**Persisted.** DC-12 `closing.scan_row_deleted` with the complete original scan payload snapshot; DC-11 `closing.warning_resolved` (`method=row_deleted`) when the deleted row was an outstanding warning.

---

### 3.23 Negative inventory — features that must NOT exist on this page

Each line is a decision, not an omission. A developer reading a stale document must not re-implement any of these. Decision Log rows in §10 carry the dates.

| Must NOT exist | Why | Date |
|---|---|---|
| **Box / size columns** in the scan list | removed in the 2026-07-23 rework — irrelevant to the verdict, and they broke the single-screen constraint | 2026-07-23 |
| **Large green OK panel** | removed (Dean): OK is silent and compact; only warnings need distance recognition | 2026-07-23 |
| **Large red warning panel** and the separate **action banner** | removed: warnings are resolved inside the row, which keeps the operator in the scan loop. The only large panel on this page is State 4's green completion status `[WF-5]` | 2026-07-23 |
| **Closing History as a modal** | converted to a separate page; the "(M2)" reference on State 4 is a fossil `[WF-4]` | 2026-07-23 |
| **Print button / print pipeline** | closing is CSV-only; `[G-4]` does not land here `[PD-68 · OWNER-PENDING]` | 2026-08-03 |
| **Auto-confirm on match** | the match only enables the button; a human must press it | 2026-07-23 |
| **Auto-re-judgment of a duplicate whose original was deleted** | `[PD-75 · OWNER-PENDING]` — rescan instead | 2026-08-03 |
| **Auto-re-judgment of an unknown row whose order later appears** | same doctrine (`[BR-22]`, E-57) — rescan instead | 2026-08-03 |
| **A second closing session on a confirmed date** | `[PD-70 · OWNER-PENDING]` — Amend Closing (§3.24) reopens the **same** session, it never creates a second one. (The former "no reopen/amend affordance" row was removed 2026-08-03 when the owner resolved `[PD-74]` — reversal recorded in §10) | 2026-08-03 |
| **Cross-day duplicate detection** | dedupe is session-scoped (`[BR-37]`); a parcel from a previous day surfaces through its order status, not through a duplicate pill | 2026-08-03 |
| **Per-order counting** (one order = one unit) | the target is a parcel count, so counting is per scan (`[BR-33]`) | 2026-08-03 |
| **A closing with target 0** | a day with no parcels is simply not closed (`[BR-34]`) | 2026-08-03 |
| **`#unrecognized-tracking` routing for unknown orders** | disjoint flow (§3.15) | 2026-08-03 |
| **Any Slack notification on closing confirmation or unresolved warnings** | `[PD-72 · OWNER-PENDING]` — no unowned alert stream | 2026-08-03 |
| **Role gating** on start / edit / cancel / confirm | v1 is a single admin role [G-15] `[PD-1 · OWNER-PENDING]` | 2026-08-03 |
| **A unified search box** on this page | closing matches carrier tracking numbers only; the unified search belongs to View Orders | 2026-07-23 |
| **Comment edit / delete** | comments are append-only `[PD-3 · OWNER-PENDING]` | 2026-08-03 |
| **A reason field on scan-row deletion** | deliberate asymmetry with `[PD-60]` (§3.22) | 2026-08-03 |
| **Sample-set assignment UI** | Order Management is the primary home [G-13]; closing has no sample surface | 2026-07-23 |
| **A "comment on the closing session" affordance** | comments target orders only (§3.8) | 2026-08-03 |
| **Wireframe chrome** (`wf-bar`, state tabs, `#annoToggle`, `.dot`, `.legend`) | review scaffolding `[L-F4]` | 2026-08-03 |

---

### 3.24 `[L-SH-2]` — Amend Closing (amendment mode)

> New unit, added 2026-08-03. Owner decision resolving `[PD-74]`, verbatim intent: "수정 누르면 마감하던 게 쭉 뜨고, 맨 위 수동 숫자를 하나 올리면 된다" — press Amend, the closing you confirmed comes back up in full, raise the manual number at the top by one, scan the parcel, re-confirm.

**Entry.** Every **confirmed** row on the Closing History page carries an `[Amend]` button (`button.amendbtn`) beside `CSV`. Clicking it opens the M3 confirm dialog (§3.25). Confirming transitions that date's session `CONFIRMED → AMENDING` and opens **amendment mode**.

**Amendment mode rendering.** The closing screen renders exactly like an `IN_PROGRESS` session (State 1 grammar), with three deltas:

1. **Amber banner** pinned above the target banner, byte-exact from the wireframe: **"AMENDING — {date} closing (confirmed {ok}/{target})"**, plus the explanatory sentence "The confirmed record stays until you re-confirm — raise the target, scan the found parcel, and press **Re-confirm Closing** (exact match + 0 warnings required)" and the button **"✕ Exit amendment"**.
2. **The day's full confirmed scan list is loaded** — every row with its original sequence number, scan time, verdict, worker and notes. Sequence numbering continues from the confirmed session's last number (`[BR-17]` — never renumbered).
3. The Confirm button renders as **"Re-confirm Closing"** with the same blocker-label grammar as §3.9 (e.g. "Re-confirm Closing (1 remaining)").

Everything else behaves as in a live session: the target banner with `[↺ Edit count]` (validation per §3.1, DC-3 on save), the scan input **re-armed** with the full [G-1] protocol, the verdict engine of §3.6 unchanged, M1/M2 available on rows, tiles and gate recomputing live. **Dedupe covers the loaded confirmed rows** — rescanning an already-counted parcel is a `duplicate` warning, so the count can never be inflated by scanning the same box twice (E-85; this is the core protection of the flow).

**The typical amendment** is exactly the owner's sentence: edit the target 84 → 85, scan the found parcel (OK, +1), gate satisfied at 85/85 · 0 warnings, press Re-confirm.

**Re-confirm.** `closing.reconfirm(session_id, target_at_press, idempotency_key)` — gate, server revalidation, double-click safety and rejection semantics are **identical to §3.9** (`[BR-3]`/`[BR-4]`/`[BR-29]` apply unchanged; rejections persist DC-22).

**Scope of the server revalidation** (clarified 2026-08-03). "Identical to §3.9" governs *what is checked and how a rejection behaves*; it does not widen §3.9's row set. The three §3.9 checks are evaluated as follows:

- **Counts** — recomputed server-side over the **whole** amended list (loaded confirmed rows + rows added in this amendment), exactly as in §3.9.
- **Target** — compared with `target_at_press` over that same whole list, so an edit that landed mid-flight still cannot be confirmed against a stale number (E-73, unchanged).
- **Live order-status re-check** — applied to the scan rows **added in this amendment session only**. The rows loaded from the confirmed v{n} snapshot are **not** re-judged against live order state: their status was already certified at the original confirm, and it legitimately advances afterwards (`Prepare Shipment → Shipped`). Re-checking them would reject every amendment of any date whose parcels have since moved — including the owner's canonical case, the past-date correction (E-83) — so the snapshot rows keep the verdict they carried at v{n} (`[BR-42]`: earlier versions are never re-written).

Everything the operator does *inside* the amendment stays under the full §3.9 discipline: a newly scanned parcel is verdicted live by §3.6 at scan time and re-checked at re-confirm, and if its order left `Prepare Shipment` in between, the re-confirm is rejected with the §3.9 red toast and DC-22.

On success:

- the session returns to `CONFIRMED`, now at **version v{n+1}**;
- the History row is updated **in place** — same date, same single row (`[PD-70]` upheld), latest numbers, plus the **"Amended v{n+1}" badge** (version · actor · timestamp — §3.20);
- a **new immutable snapshot version** is written (DC-23; the v{n} snapshot is never touched, `[BR-42]`);
- **Closing History itself carries the correction** — there is no external sheet write (`[PD-71]` resolved 2026-08-03, §6.4): the row's figures update in place and the new snapshot version serves the CSV;
- green toast **(spec-authored)**: "✓ Closing amended — {ok}/{target} orders (v{n+1})" / "Closing History updated in place";
- the screen renders State 4 for that date with the amended meta.
- **Persisted:** DC-28 `closing.amended` with `old_target → new_target`, the added/removed scan rows, actor, timestamp and both snapshot ids.

**Exit without re-confirm.** `[✕ Exit amendment]` (or any abandonment) never touches the record: the confirmed v{n} record stays authoritative — the owner's contract is literal: *the confirmed record stays until you re-confirm*. An explicit exit discards the working changes from the record, retains any added scan rows in the audit log [G-8], returns the session to `CONFIRMED` v{n}, and persists DC-29 (E-81). Leaving the page, a crash or a device switch does **not** exit: the `AMENDING` state persists server-side exactly like an in-progress session (`[BR-8]`), and reopening Closing resumes it (E-80).

**Guards** (`[BR-41]`): an amendment cannot start while any session on any date is `IN_PROGRESS` or `AMENDING` — red toast **(spec-authored)** "✕ Another closing is open — confirm or cancel it first", DC-27 (E-79). Symmetrically, a new date's closing cannot start while an amendment is open (DC-2 `reason=amendment_open`, E-86). A second `[Amend]` on a date already `AMENDING` loads the existing amendment instead of forking one (DC-27 `reason=already_amending`, E-82 — mirror of E-55).

**Wireframe demo scope for QA.** The demo implements: the per-row `[Amend]` buttons, M3 with the byte-exact owner copy, entry into State 1 with the amber banner (date and confirmed-count interpolated per row), the target pre-raised by one (84 → 85), the live scan input, the "Re-confirm Closing (1 remaining)" label, and `[✕ Exit amendment]` restoring the resting demo state. Loading the day's real scan rows, the re-confirm write chain, the badge update and every guard are `[ADMIN]` (QA-AMEND-07…15). The static "Amended v2 · Dean · 07-13 09:12" badge on the 07-12 row is a rendering demo of the post-amend state, not a simulation.

---

### 3.25 `[L-M3]` — Modal: Amend Closing

**Trigger.** A `[Amend]` button on a confirmed Closing History row (§3.24), or the wf-bar tab `[data-modal="m-amend"]` (chrome, `[L-F4]`).

**Header.** "Amend Closing — {date}" (wireframe: "Amend Closing — 07-13"), with an `✕` close control.

**Body.**
- Bold question, byte-exact (owner copy, 2026-08-03): **"Amend the closing for {date}? The confirmed record stays until you re-confirm."**
- Context line: "Confirmed {ok}/{target} · {hh:mm} ({confirmer})" (wireframe: "Confirmed 84/84 · 18:52 (Yongwon)").
- Blue note: "Amendment mode reloads the day's confirmed scan list with the scan input active. Raise the manual target (e.g. 84 → 85), scan the found parcel, and press **Re-confirm Closing** — the record is updated **in place** with an **Amended** badge (version · actor · timestamp). Closing History itself is the system of record — the retired Daily Shipping Status sheet needs no update."

**Footer.** `[Keep the record]` (secondary) and `[Amend — open the closing]` (blue primary).

**On `[Amend — open the closing]`.** `closing.startAmend(session_id, idempotency_key)` [G-9] → the `[BR-41]` guard is evaluated server-side; on pass, `CONFIRMED → AMENDING`, DC-26 persisted, and the screen enters amendment mode (§3.24) with no page refresh [G-2]. On guard failure: red toast (§3.24), DC-27, the modal closes, the record untouched.

**Close paths.** `[Keep the record]`, the header `✕`, and a backdrop click all dismiss with **zero** side effects — no state change, no event (a dismissed M3 is a NON-event, §5.3). Confirmed-record immutability is not affected by opening and closing this dialog any number of times.

---

## 4. Business Rules

Page-scoped, stable IDs. Global rules are cited, never restated. "Date" is the date the rule was decided (or provisionally adopted).

| ID | Rule | Rationale | Date |
|---|---|---|---|
| **BR-1** | A scan is OK **only** when the matched order's status is `Prepare Shipment`; every other status is a warning. | One machine-checkable criterion replaces the current process's manual "was it outbound-processed?" judgement, which is where errors enter today. | 2026-07-23 |
| **BR-2** | The closing target is a **hand count of physical parcels**, entered by a human — never a system-derived figure. | Closing exists to catch divergence between the shelf and the database in **both** directions. Seeding the target from the system would make the check tautological. | 2026-07-23 |
| **BR-3** | The confirm gate is an **exact match**: `ok_count == target` and `outstanding_warnings == 0`. **Over-scan is also a mismatch.** | An 85th parcel against a target of 84 is exactly the discrepancy the screen is for; treating "≥ target" as a pass would hide it. | 2026-07-23 |
| **BR-4** | **No auto-confirm.** Reaching the match only *enables* the button; a human presses it. The scan input stays live after the match. | Protects against closing the day the instant the arithmetic lines up, before the operator has looked around the packing bench. | 2026-07-23, copy re-confirmed 2026-08-03 |
| **BR-5** | Duplicates are **never double-counted**. Every repeat scan produces its own warning row whose Notes cite the colliding sequence number, the first scan's time, the first scanner's name, and — where it was not an OK — that scan's verdict. | Digital replacement for the Excel column-A duplicate check; those facts are what a human needs to judge a legitimate combined box. | 2026-07-23 · non-OK original clause 2026-08-03 |
| **BR-6** | An **unknown order** (tracking matches nothing) is a warning, is excluded from `ok_count`, and blocks confirmation until cleared. | It is either a mistype or a parcel from another system — both need a human decision before the day is closed. | 2026-07-23 |
| **BR-7** | M1 performs a **real order-status change** `Processing → Prepare Shipment`, reflected on every screen, gated behind the Zero Packing attestation **and** the `[BR-38]` inbound-completeness predicate. | The closing screen must not invent a private notion of "done"; and step 6 of the current process (verify packing) survives as the checkbox. | 2026-07-23 · gate `[PD-77 · OWNER-PENDING]` 2026-08-03 · inbound-completeness clause `[BR-38]` 2026-08-03 |
| **BR-8** | **Closing progress is stored server-side.** Refresh, navigation, crash, or a switch of device restores target, scan list, counters and warnings. Nothing clears until confirmation or an explicit cancel/restart. | Shift handovers and walks to Zero Packing happen mid-closing daily; a client-only session would lose an hour of scanning. | 2026-08-03 (behavior paragraph, `[L-S1-F]`) |
| **BR-9** | **Pre-start gating**: the scan input and every progress affordance are hidden/disabled until the manual count is entered. | Makes "enter the number first" structurally true rather than instructional; a scan before a target has nothing to be judged against. | 2026-07-23 |
| **BR-10** | Closing History rows are **always "Match"** by construction — a mismatch cannot be confirmed. | The column is retained as an explicit invariant, so an auditor reading History knows a blank day means "not closed", never "closed badly". | 2026-07-23 |
| **BR-11** | **RETIRED 2026-08-03** (`[PD-71]` owner decision). Originally: confirmation auto-updates SS Daily Shipping Status. The sheet is **retired entirely — no sheet integration exists**; the admin's Closing History (daily snapshots §3.20 + per-day CSV §3.18) is the system of record and replaces the sheet wholesale. | The ID is kept (never renumber). Any downstream need the sheet served is covered by the per-day CSV export. | 2026-07-23 · failure semantics 2026-08-03 · **retired 2026-08-03 (owner)** |
| **BR-12** | Scan-row deletion always goes through the M2 confirm modal, is a **soft delete**, and the full original payload is retained in the backend forever. | The `✕` sits next to the primary action at scan speed; and a deleted scan is evidence about a physical parcel. | 2026-07-23 · confirm/toast `[PD-5 · OWNER-PENDING]` 2026-08-03 |
| **BR-13** | Voice alerts are **ON by default**; only warnings speak; the utterance is fixed `"Please check this order"` (`en-US`); a Test button exists and plays regardless of the toggle; OK scans are silent. | The operator's eyes are on parcels, not the monitor. A fixed short phrase is recognizable at distance; templating it with a tracking number would make it unparseable. | 2026-07-23 · phrase/locale confirmed 2026-08-03 [G-3b] |
| **BR-14** | The target may be **edited** and the session **cancelled** at any time while `IN_PROGRESS`, from the target banner, which is present in every in-progress rendering. | The hand count is fallible; forcing a cancel-and-restart to fix a typo would discard real scans. | 2026-07-23 · banner-everywhere clause 2026-08-03 (U-j) |
| **BR-15** | Closing History is a **separate page**, not a modal, and every row exports a per-day CSV containing the **full scan list**. | A modal cannot hold an audit table; and the CSV is what feeds the shipping report and any later dispute. | 2026-07-23 (reversal — see §10) |
| **BR-16** | The Warnings tile counts **outstanding** warnings (the gate input); **raised** is a cumulative counter that is never decremented and is what History and the Warning Resolution Summary display (`3→3`). | Without this split, resolving warnings would erase the evidence that the day had any — which is the most interesting fact about the day. | 2026-08-03 |
| **BR-17** | Sequence numbers are **never reused and never renumbered**. Gaps after deletion are normal. | Keeps every duplicate cross-reference ("Duplicate of #2") stable forever and keeps the exported record aligned with what the operator saw on screen. | 2026-08-03 (dev default DQ-2 in plans, adopted as a rule) |
| **BR-18** | After confirmation the session is **immutable**: the scan input is disabled and no second session may start on that calendar date. | A confirmed closing is a record; live input on it would create scans belonging to no session. | `[PD-73 · OWNER-PENDING]` / `[PD-70 · OWNER-PENDING]`, 2026-08-03 |
| **BR-19** | A session that crosses midnight belongs to its **start date**. | The target count and the parcels are the start date's work. | `[PD-78 · OWNER-PENDING]`, 2026-08-03 |
| **BR-20** | Non-`Processing` abnormal statuses (`Pending`/`On Hold`/`Shipped`/`Completed`/`Refunded`/`Failed`) and cancelled orders share the `⚠ Not outbounded` pill, with the actual status shown in the Order Status column (plus a `Cancelled` marker where the cancellation flag is set); `[Process this order]` appears **only** for `Processing`. **`Cancelled` is a flag, not a ninth status** — the vocabulary is the 8 lowercase-hyphenated values in §3.7, rendered as title-case labels. | M1 is specifically a `processing → prepare-shipment` transition; offering it elsewhere would produce an invalid mutation. Inventing a `Cancelled` status would break the 8-status vocabulary that VO `BR-12` / OD `BR-12` state as exhaustive. | `[PD-76 · OWNER-PENDING]`, 2026-08-03 · `Cancelled`-as-flag correction 2026-08-03 (M3a-D3; the PD-76 register title still needs the same edit) |
| **BR-21** | A duplicate warning is cleared by **✕-deleting the duplicate row after logging the combined-box reason as a comment on the order**. Deleted warning rows still count in History's raised→resolved. | Matches State 4's `3→3` display and keeps the raised count honest. | `[PD-69 · OWNER-PENDING]`, 2026-08-03 |
| **BR-22** | Deleting the **original** OK row of a duplicate pair does **not** re-judge the surviving duplicate; the operator deletes it and rescans. The same no-retro-judgment doctrine covers an unknown row whose order later appears. | Retro-judging a past row would rewrite the meaning of the scan sequence; a rescan produces a clean, timestamped verdict. | `[PD-75 · OWNER-PENDING]`, 2026-08-03 |
| **BR-23** | A closing "unknown order" **never** routes to `#unrecognized-tracking` and never creates an unrecognized-pool item. The two flows are disjoint (§3.15). | Different input (tracking number vs product barcode), different owner, different resolution. Cross-wiring them would put carrier numbers into a product pool. | 2026-07-23, re-affirmed 2026-08-03 |
| **BR-24** | Closing has **no print surface**; the report is CSV-only. | Wireframe (SST) after the 2026-07-23 rework ships a CSV download and no print affordance; the older decision-sources mention of "Closing report" under [G-4] is the stale artifact (conflict C-4). | `[PD-68 · OWNER-PENDING]`, 2026-08-03 |
| **BR-25** | **Single admin role** in v1: no role gating on start / edit / cancel / confirm / delete; every mutating action records the actor. | Six screens independently raised the same question; inventing per-page gates would produce eight inconsistent models. | [G-15] `[PD-1 · OWNER-PENDING]`, 2026-08-03 |
| **BR-26** | A scan lookup must **never lock the scan input** or gate scanning speed on network latency, and a pending verdict must never render as an OK. A lookup failure is explicit and recorded. | The operator's rhythm is physical; a UI that waits for the network turns a 12-minute closing into a 40-minute one, and a fake OK would ship an unverified parcel. | 2026-08-03 |
| **BR-27** | Every scan and every state change is persisted **at action time**, never batched to confirmation. | A crash at scan 60 of 84 must lose nothing; and the audit trail must show the day as it happened, not as it ended. | 2026-08-03 (from `[L-S1-F]` clause 9 + [G-8]) |
| **BR-28** | Comments raised from closing are **append-only** — no edit, no delete. | [G-7] declares the comment corpus an AI-training and audit asset; mutability would silently rewrite it. | `[PD-3 · OWNER-PENDING]`, 2026-08-03 |
| **BR-29** | The server **revalidates the whole gate at confirm time** against live order state and against the target the operator saw; on any mismatch it rejects with a red toast, re-judges the affected rows, and writes nothing partial. | Between the scan and the press, another operator can move an order or change the target; confirming against a stale client would certify a shipment that did not happen. | `[PD-6 · OWNER-PENDING]`, 2026-08-03 |
| **BR-30** | Concurrent operators are handled by **server-side merge** for the counting flow (sequence assignment, counters, row list) and by an optimistic version check for single-value edits (target, session state), which returns a 409 and reloads. | Closing is a running total across two stations, so merge is correct there; last-write-wins on the target would silently destroy a colleague's correction. | `[PD-7 · OWNER-PENDING]`, 2026-08-03 |
| **BR-31** | **No Slack route** fires from closing confirmation, mismatch, or unresolved warnings in v1. The only Slack traffic from this page is the [G-7] comment @mention route. | Inventing a channel would create an unowned alert stream that nobody has agreed to read. | `[PD-72 · OWNER-PENDING]`, 2026-08-03 |
| **BR-32** | Slack delivery failures **never roll back** the primary action; they are persisted and retried. (The rule's former "or sheet" clause is void since the sheet's retirement — `[PD-71]`, 2026-08-03.) | Notification is a side effect, not part of the transaction. | `[PD-4 · OWNER-PENDING]`, 2026-08-03 · sheet clause retired 2026-08-03 |
| **BR-33** | **The unit of the count is a parcel, not an order.** Each OK scan contributes exactly 1 to `ok_count`: an order split across two tracking numbers contributes 2, and a combined box carrying two orders contributes 1 (one OK + one duplicate). | The target is a hand count of boxes, so the system side must count boxes too, or the exact-match gate would be unachievable on any day with a split or combined shipment. | 2026-08-03 (spec-authored; derived from `[BR-2]`/`[BR-5]`) |
| **BR-34** | A closing cannot be started with a target of 0. A day on which nothing shipped is simply **not closed** and has no Closing History row. | There is nothing to reconcile; and a missing row already means "not closed" (`[BR-10]`), so no new representation is needed. | 2026-08-03 (spec-authored) |
| **BR-35** | A session left `IN_PROGRESS` on an earlier date **blocks** starting a closing for a new date; the operator must confirm or cancel the open session first, and the client opens it automatically. | One-session-per-date (`[PD-70]`) plus start-date attribution (`[PD-78]`) are only coherent if an abandoned session is resolved rather than orphaned; two open sessions would make "today's closing" ambiguous. | 2026-08-03 (spec-authored) |
| **BR-36** | Every rendered time, every date boundary and every "same calendar day" test uses the **warehouse's single operating timezone**; all persisted timestamps are server timestamps. | Two stations, one clock: a browser-local timestamp would let two operators disagree about the order of scans and about which day a 23:58 parcel belongs to. | 2026-08-03 (spec-authored; with E-59) |
| **BR-37** | Duplicate detection is scoped to the **current session only**. There is no cross-day duplicate check. | Yesterday's parcel is caught by its order status (`Shipped`/`Completed` → warning), which is the more informative signal; a cross-day index would also flag legitimate carrier number reuse. | 2026-08-03 (spec-authored) |
| **BR-38** | **M1 obeys the global outbound predicate.** `[Process Outbound → resolve warning]` is enabled only when the order has ≥1 line, **every line is `INBOUNDED`**, the status is `processing`, and the order is not cancelled — in addition to the Zero Packing attestation. A `Processing` order with any `PENDING` line stays `⚠ Not outbounded`, with the button disabled and the shortfall named. | M1 emits the canonical `order.outbounded` (DC-14). View Orders `BR-9` and `order-detail.md` L-9 both state the outbound gate as **iff every line is INBOUNDED**, with no page exception; a closing-only side door would ship an order whose goods were never received and would make the two other specs' "iff" false. | 2026-08-03 (cross-page defect M3a-D2; before this, closing's gate was Zero Packing alone) |
| **BR-39** | **Amendment entry.** Every confirmed Closing History row carries `[Amend]`. Amending always passes through the M3 confirm dialog (`[PD-5]` class) and transitions that date's **existing** session `CONFIRMED → AMENDING`, loading the full confirmed scan list with original sequence numbers. The confirmed record (v{n}) remains the authoritative History row until re-confirm — "the confirmed record stays until you re-confirm" is a verbatim owner requirement. | Owner decision 2026-08-03 (resolves `[PD-74]`): the correction path for a parcel found after confirmation reuses the closing screen and its whole verdict machinery, instead of inventing a parallel edit UI that could bypass the scan discipline. | 2026-08-03 (owner) |
| **BR-40** | **Re-confirm gate = the confirm gate.** `[Re-confirm Closing]` obeys `[BR-3]`/`[BR-4]`/`[BR-29]` unchanged: exact match against the amended target, 0 outstanding warnings, a human press, full server revalidation — **scoped as §3.24 states**: counts and target over the whole amended list, the live order-status re-check over the rows added in this amendment only (the confirmed v{n} snapshot rows are not re-judged, or a past-date amendment could never re-confirm, E-83). Success updates the record **in place** — same date, same single History row (`[PD-70]` upheld), version v{n}→v{n+1}, an "Amended" badge carrying version · actor · timestamp. Closing History itself carries the correction — no external sheet write exists (`[PD-71]`). | An amendment that could confirm with a looser gate would make the amended record weaker than the original; and a second row per date would break `[BR-10]`'s "one row per date" reading of History. | 2026-08-03 (owner) |
| **BR-41** | **Single working context.** An amendment cannot start while any session on any date is `IN_PROGRESS` or `AMENDING`; a new date's closing cannot start while an amendment is open (extends `[BR-35]`). A second `[Amend]` on a date already `AMENDING` loads the existing amendment, never a fork. | Two open working sessions would make "the closing being worked on" ambiguous for every scan arriving from a wedge — the same ambiguity `[BR-35]` exists to prevent. | 2026-08-03 (spec-authored; derived from `[BR-35]`/`[PD-70]`) |
| **BR-42** | **Amendment audit.** The pre-amend snapshot is never mutated: every re-confirm writes a **new** immutable snapshot version, and every version stays reproducible as CSV forever. Exiting an amendment discards the working changes from the record but retains any added scan rows in the audit log; entry, re-confirm, rejection and exit all persist (DC-26…DC-29). History's CSV serves the latest version; surfacing earlier versions is a developer decision (DQ-13). | An amendment is precisely the situation an auditor will ask about ("why does the sheet say 85 when it said 84 on the day?") — the answer must be reconstructible from data alone [G-8]. | 2026-08-03 (spec-authored) |

---

## 5. Data Capture

Doctrine [G-8]: every operator-initiated action persists **actor · timestamp · entity · old value → new value · quantity**. UI surfaces (scan list, tiles, Warning Resolution Summary, History table) are **views over these events**, never the only copy. Anything operator-initiated that is not listed in §5.3 as a NON-event **must** persist.

**Persistence timing** (`[BR-27]`): every event below is written server-side **at action time**. Nothing is batched to confirmation.

Names follow the canonical cross-page vocabulary where one exists (`order.status_changed`, `order.outbounded`, `comment.*`) — those names are byte-identical to their use on every other screen. Closing-local events use `closing.{action}`. Literal API/table naming is a developer decision.

### 5.1 Event register

| ID | Event | Trigger | Actor | Entity | Payload (old → new where applicable) | Surfaced in UI |
|---|---|---|---|---|---|---|
| **DC-1** | `closing.session_started` | `[L-S0-1]` Start Closing succeeds | starter | closing session (date) | `session_id`, `closing_date`, `target_qty`, `started_at`, `device/station` | Yes — banner "Closing in progress (started 18:02 · Dean)" |
| **DC-2** | `closing.start_rejected` | server refuses a start (session already open · date already confirmed · an earlier date still open · invalid target reaching the server) | attempting actor | date | `reason ∈ {already_in_progress, already_confirmed, prior_date_open, invalid_target}`, `attempted_target`, existing `session_id` where relevant | Red toast only |
| **DC-3** | `closing.target_edited` | `[L-S1-10]` Save after Edit count | editor | session | `old_qty → new_qty`, `edited_at`, `ok_count_at_edit`, `outstanding_warnings_at_edit` | Partially — the UI shows only the new value; **the old value is silent capture** |
| **DC-4** | `closing.target_edit_rejected` | invalid new target reaching the server | editor | session | `attempted_value`, `reason` | Red toast only |
| **DC-5** | `closing.session_cancelled` | `[L-S1-10]` Cancel confirmed | canceller | session | `cancelled_at`, `scan_row_count_discarded`, `retained_row_ids[]`, `ok_count_at_cancel`, `outstanding_warnings_at_cancel` | Toast, then silent (session disappears from the UI; rows are retained server-side) |
| **DC-6** | `closing.session_restarted` | a new session starts on a date that already had a cancelled session | starter | new session | `previous_session_id`, `sequence_of_session_on_date` | Yes (new session banner) |
| **DC-7** | `closing.scan_recorded` | **every** scan, every verdict, including rows later deleted | scanning worker | session + `tracking_no` (+ `order_id` nullable) | `seq`, `scanned_at` (hh:mm:ss + full timestamp), `tracking_no_raw`, `tracking_no_normalized`, `order_id`/`null`, `item_count`/`null`, `order_status_at_scan`, `verdict ∈ {ok, not_outbounded, duplicate, unknown, ambiguous}`, `duplicate_of_seq` + `first_scan_at` + `first_scan_actor` + `first_scan_verdict` (duplicate only), `colliding_order_ids[]` (ambiguous only), `station`, `scan_id` (idempotency key) | Yes — the scan-list row |
| **DC-8** | `closing.scan_rejected` | a scan arrives with no active session, on a `CONFIRMED` date, or against a session cancelled by another operator mid-loop | scanning worker | date / session | `tracking_no`, `reason ∈ {no_active_session, session_confirmed, session_cancelled}` | Red toast only |
| **DC-9** | `closing.scan_lookup_failed` | transport or server error between submit and verdict | scanning worker | `tracking_no` | `error_class`, `attempt`, `retried`, `resolved_by_retry`, `timestamp` | Red toast |
| **DC-10** | `closing.warning_raised` | a scan resolves to any non-OK verdict | same actor as DC-7 | scan row | `warning_class ∈ {not_outbounded, duplicate, unknown, ambiguous}`, `raised_at`, link to DC-7. May be modelled as a facet of DC-7 rather than a second row, **provided** the cumulative `warnings_raised` counter used by History and the Warning Resolution Summary is derivable from it | Yes — red row + Warnings tile |
| **DC-11** | `closing.warning_resolved` | M1 resolution, or deletion of a warning row | resolver | scan row / warning | `method ∈ {m1_outbound, row_deleted}`, `resolved_at`, `resolver`, link to the raising event | Yes — tile decrement + State 4 summary + History `raised→resolved` |
| **DC-12** | `closing.scan_row_deleted` | `[L-M2]` Yes — remove | deleter | scan row | `seq`, **full original scan payload snapshot**, `deleted_at`, `was_outstanding_warning` (bool). Soft delete — the row is retained forever and appears in the CSV with a deleted flag | Row disappears; the event itself is silent |
| **DC-13** | `order.status_changed` | `[L-M1]` Process Outbound succeeds | resolver | order | `order_id`, `tracking_no`, `old_status: processing → new_status: prepare-shipment`, `zero_packing_verified: true`, `source=closing_m1`, `closing_session_id`, `correlation_id` | Yes — row re-judged green, propagated to every screen |
| **DC-14** | `order.outbounded` | same action as DC-13 (the semantic action alongside the state transition) | resolver | order | `order_id`, `source=closing_m1`, `correlation_id` (identical to DC-13), `idempotency_key` | Yes (cross-screen) |
| **DC-15** | `comment.posted` | M1 memo with text; a combined-box reason typed into the order's comment trail from closing | author | order | `text`, `mentions[]`, `source ∈ {closing_m1, closing_manual}`, `closing_session_id`, `posted_at`. Dual-written to the order's Comments history **and** the closing log | Yes — Comments |
| **DC-16** | `comment.auto_posted` (`source=system`) | M1 confirmed with an **empty** memo; the system records the closing-driven transition on the order | system (on behalf of the resolver) | order | `text` (generated: order, old→new status, closing date, resolver), `source=system`, `closing_session_id` | Yes — Comments |
| **DC-17** | `comment.mention_notified` | a comment from this page contains an `@mention` | system | comment | `channel=#fulfillment-admin-comments` (`C0BMGEWM5QA`), `message_ts`, `mentioned_user`, `delivery_status`, `attempt`, `deep_link` | No (silent; delivery record) |
| **DC-18** | `comment.starred` / `comment.unstarred` | `★` toggle in the Comments hub | operator | comment | `old → new` saved state | Yes — star |
| **DC-19** | `comment.read` / `comment.mark_all_read` | opening a mention / "Mark all read" | operator | comment (set) | `comment_ids[]`, `read_at` (the unread badge is a view over this) | Yes — badge |
| **DC-20** | `closing.voice_alert_toggled` | `[L-S1-3]` switch | operator | session + device/user (per DQ-3 scope) | `old on/off → new on/off`, `toggled_at` | Yes — switch |
| **DC-21** | `closing.confirmed` | `[L-S1-8]` Confirm succeeds | confirmer | session | `confirmed_at`, `confirmer`, `target`, `ok_count`, `warnings_raised`, `warnings_resolved`, `match=true`, `snapshot_id`, `starter`, `started_at`, `session_duration` | Yes — State 4 + toast |
| **DC-22** | `closing.confirm_rejected` | server revalidation fails at confirm (`[BR-29]`) | attempting confirmer | session | `reason`, `offending_order_ids[]`, `server_ok_count`, `server_outstanding_warnings`, `client_ok_count`, `target_at_press` vs `server_target` (to diagnose drift) | Red toast + rows re-judged |
| **DC-23** | `closing.snapshot_created` | immediately after DC-21, inside the same transaction | system | session | `snapshot_id`, immutable copy of the **full scan list** (including deleted rows), the counters, the target-edit history, and the warning ledger. This is what every later CSV re-renders | Yes — History row |
| **DC-24** | `closing.daily_shipping_status_updated` — **RETIRED 2026-08-03** (`[PD-71]` owner decision: the sheet is retired entirely, no integration exists, and this event is **never emitted**; the ID is kept — never renumber) | — | — | — | — | Never surfaced — QA asserts its **absence** (QA-CONFIRM-10/16, QA-PERSIST-08) |
| **DC-25** | `closing.report_exported` | `[L-S4-2]` CSV button or a History row's `CSV` button | downloader | session / date | `source ∈ {state4_button, history_row_csv}`, `closing_date`, `exported_at`, `row_count`, `includes_deleted=true` | No (silent) |
| **DC-26** | `closing.amend_started` | `[L-M3]` "Amend — open the closing" succeeds (`CONFIRMED → AMENDING`) | amending actor | closing session (date) | `session_id`, `closing_date`, `base_version` (the v{n} being amended), `base_target`, `base_ok_count`, `amend_started_at` | Yes — amber AMENDING banner + History "Amendment in progress" marker |
| **DC-27** | `closing.amend_rejected` | the `[BR-41]` guard refuses an amend start | attempting actor | date | `reason ∈ {another_session_open, already_amending}`, blocking `session_id`/date | Red toast only (on `already_amending` the existing amendment is loaded) |
| **DC-28** | `closing.amended` | `[L-SH-2]` Re-confirm Closing succeeds | re-confirming actor | session | `old_target → new_target`, `added_scan_seqs[]`, `removed_scan_seqs[]`, `old_ok_count → new_ok_count`, `version` (v{n+1}), `previous_snapshot_id → new_snapshot_id`, `amended_at`, actor. The named owner contract event — old/new target · added scans · actor · timestamp [G-8] | Yes — updated History row + "Amended v{n+1}" badge + green toast |
| **DC-29** | `closing.amend_cancelled` | `[✕ Exit amendment]`, explicit abandonment of an amendment | exiting actor | session | `base_version` restored, `discarded_scan_seqs[]` (retained in the audit log), `exited_at` | Toast, then the record renders as v{n} again |

### 5.2 Notes on modelling

- **DC-13 + DC-14 are emitted together** for one M1 action, sharing a `correlation_id` and an idempotency key: `order.status_changed` is the transition, `order.outbounded` is the semantic action other screens subscribe to. QA asserts both.
- **DC-10/DC-11 form the warning ledger.** History's `raised→resolved` column and the State 4 summary are computed from it; neither number may be stored only in a UI string.
- **DC-3 captures the pre-edit counts**, not just the target, so an auditor can see whether a target was edited *to fit* the scans rather than to correct a miscount.
- **DC-7 stores the raw scanned string as well as the normalized one**, so a scanner misconfiguration (stray prefix, missing suffix) is diagnosable months later from data alone.
- **DC-7 also stores `first_scan_verdict`** on duplicates, so a duplicate-of-an-unknown (E-70) is distinguishable from a duplicate-of-an-OK without joining back to the earlier row.
- Every event carries the acting user id and the station/device identifier; two operators in one session are distinguishable at every row (`Worker` column is a projection of this).
- The retroactive `First scan` annotation on an earlier row (§3.7) is **derived** from the arrival of a duplicate — it is not a separate persisted event and must never be stored as a mutation of DC-7.

### 5.3 Declared NON-events

Stated explicitly so nobody gold-plates the event stream, and so QA does not fail a build for a missing row:

- Focus and refocus, including the click-anywhere refocus loop.
- Keystrokes in the scan input **before** a submit; a submit that is suppressed by the double-Enter debounce.
- Voice **test** button plays, the "toggle turned ON" confirmation utterance, and every TTS utterance playback (only the toggle change persists, DC-20).
- The `[G-3a]` send sound playback on M1 (the action itself persists as DC-13/DC-14).
- wf-bar state switches and in-page tab switches (`Closing` ⇄ `Closing History`).
- Opening/closing the Comments hub, switching its Mentions/Saved tabs, typing in comment search.
- Opening a modal, and dismissing M1, M2 or M3 with `Close` / `Keep the record` / `✕` / backdrop (no action taken).
- Entering target-edit mode without saving; abandoning an edit.
- Clicking an Order ID deep link.
- Hover, scroll, column resize, the annotation toggle.
- Viewing the Closing History page (the export is captured, the read is not).
- **`print.job_result`** — there is no print surface on this page `[PD-68 · OWNER-PENDING]`.
- **`product.barcode_registered`** — no product barcodes are scanned on this page.

### 5.4 Retention and export

- **Retention: indefinite** for every event in §5.1. The doctrine is maximum accumulation in admin; nothing on this page has a purge horizon in v1.
- **Deleted scan rows are retained forever** with their full payload (`[BR-12]`, verbatim owner requirement "Deletion history is kept in the backend").
- **Cancelled sessions are retained** with their scan rows, even though they never appear in Closing History.
- **Every historical date must remain reproducible as a CSV forever**, byte-identical to the day it was confirmed, because it is rendered from the immutable snapshot (DC-23) and not from live data.
- **Amended days retain every snapshot version** (`[BR-42]`): the v1 snapshot survives the v2 re-confirm untouched; the History CSV serves the latest version, and earlier versions remain queryable (DQ-13).
- The CSV export includes deleted rows with their disposition, per the wireframe's own footer ("all rows stored in the backend (fully included in the closing report export)"). Column order, encoding and filename convention are developer decisions (DQ-5).
- Comment history from this page accumulates on the **order** entity and inherits [G-7] retention.

---

## 6. Integrations

### 6.1 Slack routing

Exactly **one** Slack route fires from this page.

| Trigger on this page | Channel | Payload fields (verbatim from `_slack-routing`) | Mention target | Status |
|---|---|---|---|---|
| A comment posted from a closing context contains an `@mention` — an M1 memo that tags someone, or a combined-box reason typed onto the order | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) | order/entity no., comment text, time, author, @mentioned user, deep link to the entity | the message **body** @mentions the person, so Slack raises a personal notification while the channel doubles as a team-visible archive | CONFIRMED by owner, 2026-08-03 (per `_slack-routing`, 2026-08-03) |

System auto-comments raised here (DC-16, `source=system`) travel the same pipeline, tagged `source=system` [G-7].

**Explicit non-routes** — these are decisions, and the absence must not be read as an oversight:

| Event | Route | Why |
|---|---|---|
| Unknown-order scan (State 2b) | **none** — and specifically **NOT** `#unrecognized-tracking` | That channel serves the View Orders product-barcode pool. A closing unknown is a carrier tracking number absent from the system — a disjoint flow (`[BR-23]`, §3.15) |
| Closing confirmed | **none** in v1 | `[PD-72 · OWNER-PENDING]` — inventing a channel would create an unowned alert stream |
| Mismatch / unresolved warnings at end of day | **none** in v1 | same |
| Daily Shipping Status update failure | **none** — nothing exists to fail: the sheet was retired 2026-08-03 (`[PD-71]`, §6.4) | superseded row, kept so the non-route's history stays legible |

**Delivery failure** `[PD-4 · OWNER-PENDING]`: the primary action (the comment, the status change, the confirmation) always commits. A failed Slack dispatch is persisted (DC-17 with `delivery_status=failure`) and retried; it never blocks the UI and never rolls anything back. Retry policy is a developer decision.

### 6.2 Cross-page propagation (M1)

The M1 status change is a real mutation and must be visible **immediately** wherever that order appears:

| Consumer | Effect |
|---|---|
| View Orders | the order leaves the `Processing` working set; status pill updates |
| Order Detail | status pill, actor log entry, and the closing-sourced comment (DC-15/DC-16) |
| Order Management | dashboard status counts update |
| Ready to be Outbounded | the order's eligibility recomputes |
| Closing (this page) | the scan row is re-judged green in place, counters and gate recompute |

Propagation mechanism (poll vs push) and acceptable latency are developer decisions (DQ-4). The same transport carries multi-operator live sync inside one closing session (`[BR-30]`).

### 6.3 Deep links [G-12]

Cross-page references on this page are real links, never decoration:

| Surface | Target |
|---|---|
| `Order ID` cell in the scan list (rendered blue) | the order detail screen for that order. Wireframe path `../order-detail/#{order_id}` — the **directory form** `../{slug}/#{anchor}` fixed by `[G-12]`, never `../order-detail/index.html#…` (cross-page defect M3a-D16, normalized 2026-08-03); in the production admin the link resolves to the specific order (e.g. `/oms/orders/{order_id}`) — exact route is a developer decision. While a session is `IN_PROGRESS` the link opens in a **new tab** so the scan loop is never destroyed (E-74). **U-f: the wireframe renders these as plain `td` text, so this is `[ADMIN]` QA.** |
| M1 header order number | same target |
| Comments hub entry | the entity the comment belongs to (an order) [G-7] |
| Slack comment notification | deep link back to the order |
| `Closing History` / `Closing` in-page tabs | the history page / the live session view (`[L-S1-11]`) |

Closing has **no** inbound-request deep link (no `#reqlist` equivalent) — nothing on this page references the inbound flow.

### 6.4 Sheet / BI handoff — **none** (Daily Shipping Status retired)

**Owner decision, 2026-08-03 (`[PD-71]` resolved):** the **SS Daily Shipping Status spreadsheet is retired entirely**. There is **no automatic sheet update, no sheet target, and no column mapping** — the integration this section used to specify does not exist. The admin's **Closing History** (daily snapshots, §3.20) is the system of record for the day's shipping figures, and the **per-day CSV export** (§3.18) covers any downstream need the sheet used to serve.

Consequences that QA and developers must treat as normative:

1. Confirmation (§3.9) and amendment re-confirm (§3.24) write the closing record and its snapshot — **nothing else**. No external write is triggered by any action on this page.
2. **DC-24 is retired and never emitted** (§5.1); QA asserts its absence (QA-CONFIRM-10/16, QA-PERSIST-08).
3. The failure machinery this section used to define (retry queue, persistent error strip, "✕ Daily Shipping Status not updated" toast, `manual_retry_by`) is **void** — there is nothing to fail. E-38 and DQ-6 are superseded accordingly (IDs kept, never renumbered).
4. The confirmation toast subtext reads "Closing record saved · replaces the retired Daily Shipping Status sheet" — it asserts the record, never a sheet write.
5. Reversal impact if the owner ever revives a sheet handoff: reinstate the v1.2 §6.4 contract (trigger on confirm, idempotent per date, failure never invalidates, failure surfaces persistently, every attempt persists as DC-24) — the invariants were deliberately preserved in this spec's git history.

### 6.5 Print pipeline [G-4]

**Closing has no print surface.** The closing report is **CSV download only** `[PD-68 · OWNER-PENDING]` — adjudication C-4, global delta GD-9. Consequences that QA and developers must treat as normative:

- No Print button exists anywhere on this page (§3.23).
- The local print agent (PrintNode-class) is **not** a dependency of this screen; a printer or agent being offline has no effect here (E-49).
- `print.job_result` is a declared NON-event on this page (§5.3).
- Reversal impact if the owner restores the print surface: add one button to the State 4 Closing Report banner and wire it to the standard [G-4] pipeline (instant output, no dialog, no preview, red toast + `print.job_result` on infrastructure failure). No other section of this spec changes.

### 6.6 Audio pipeline [G-3]

| Branch | Applies here | Detail |
|---|---|---|
| `[G-3a]` send sound | **Yes — one button only**: M1's `[Process Outbound → resolve warning]`, as an outbound-class button `[PD-2 · OWNER-PENDING]`. PD-2's page enumeration does not name closing; adjudication C-5's button-class scope does. This spec applies it by class (§3.21 step 5) | Web Audio synthesized rising sweep, no external files. Must be audibly distinct from the warning voice |
| `[G-3b]` warning voice | **Yes — the page's primary audio channel** | `en-US` TTS, fixed utterance "Please check this order", on every warning verdict, toggleable (§3.4) |
| `[G-3c]` View Orders wrong-product warning tone | **No** — that is a View Orders page delta | — |

Synthesis parameters, the TTS voice fallback chain and AudioContext resume handling are developer decisions.

---

## 7. Edge Cases & Error States

IDs are page-scoped and stable. E-1…E-50 are the original planning assignments and keep their numbers wherever they appear; E-51…E-77 were added while writing and auditing this spec, **E-78** was added during the 2026-08-03 remediation pass (`[BR-38]`), and **E-79…E-86** were added with the Amend Closing flow (§7.7, PD-74 owner decision 2026-08-03). Gaps in reading order (E-50 appearing inside §7.1, E-41 inside §7.2) are original assignments and are **not** renumbered. Every ID is mapped to at least one asserting QA scenario in §8.18.

**Total: 86 edge cases.**

### 7.1 Scan input & verdict

| ID | Condition | Expected behavior |
|---|---|---|
| **E-1** | Enter / Scan pressed with an empty input | No row, no counter change, no event. Silent — the input simply stays armed. An error toast here would fire constantly from stray Enters and train the operator to ignore toasts. |
| **E-2** | Malformed / truncated barcode (partial read shorter than the minimum length) | Rejected client-side before lookup; red toast **(spec-authored)** "✕ Incomplete scan — scan again"; no row, no `closing.scan_recorded`. The minimum-length rule is a developer decision (DQ-1). |
| **E-3** | Well-formed tracking number matching no order | `unknown` verdict per §3.15: red row, `–` in Order/Items/Status, voice, excluded from `ok_count`, counted as an outstanding warning. |
| **E-4** | Order in `Processing` | `not_outbounded` verdict, red row, `[Process this order]` in Notes, voice. |
| **E-5** | Order in another non-`Prepare Shipment` status (`Pending`/`On Hold`/`Shipped`/`Completed`/`Refunded`/`Failed`), **or** an order carrying the cancellation flag | Same `⚠ Not outbounded` pill; the real status renders in the Order Status column (with a `Cancelled` marker where the flag is set — `Cancelled` is not a ninth status, §3.6); **no M1 button** `[PD-76 · OWNER-PENDING]` (`[BR-20]`). Notes: "Order status is {status} — not shipped from this closing". |
| **E-6** | Second scan of a tracking already scanned in this session | `duplicate` verdict; Notes "Duplicate of #{n} — first scanned {hh:mm:ss} ({worker})"; not double-counted. |
| **E-7** | Third and subsequent scans of the same tracking | Each repeat is its own warning row; every one references the **first** scan of that tracking `#n`, never the previous duplicate. |
| **E-8** | Duplicate whose original OK row was deleted | The surviving duplicate is **not** auto-re-judged `[PD-75 · OWNER-PENDING]`; the operator deletes it and rescans the parcel (`[BR-22]`). |
| **E-9** | Scan attempted in State 0 (session not started) | The input is `disabled`; wedge input goes nowhere; nothing is recorded. If a request nonetheless reaches the server, it is rejected with `reason=no_active_session` (DC-8). |
| **E-10** | Scan attempted after Confirm Closing | Input is disabled `[PD-73 · OWNER-PENDING]`; a request reaching the server is rejected with `reason=session_confirmed`, red toast "✕ Today's closing is confirmed — scanning is closed", DC-8. The correction path for a genuinely missed parcel is **Amend Closing** (§3.24, `[PD-74]` resolved 2026-08-03) — never a scan against the locked session. |
| **E-11** | Over-scan — `ok_count` exceeds the target (the 85th parcel) | Mismatch: Confirm re-disables, label "Confirm Closing ({n} over target)", `.proglab` states the over-scan. Resolution: `[↺ Edit count]` to the true number, or delete the extra rows. Nothing is auto-corrected. |
| **E-12** | Scanner artifacts — trailing CR/LF/Tab, leading/trailing spaces, mixed case | Normalized before lookup; both the raw and the normalized string persist (DC-7). Exact rules are a developer decision (DQ-1). |
| **E-13** | Wrong identifier scanned — product EAN (`8809…`), Order ID, Deleo number, or an **inbound-request** tracking number | `unknown` verdict. This page matches customer-order (outbound) carrier tracking numbers only; inbound tracking is a separate namespace `[PD-8 · OWNER-PENDING]` and never resolves here. There is no unified search on this page. |
| **E-14** | One tracking number matches two or more orders (carrier reuse or a data error) | `ambiguous` verdict — the server never silently picks one. Red warning row, excluded from `ok_count`, Notes lists every colliding Order ID. Default pill is `⚠ Unknown order`; a distinct label is a developer decision (DQ-2). |
| **E-50** | Very long tracking string | No truncation of the identifying tail; the table stays inside one screen (`[L-S1-9]`); the cell wraps or the column flexes rather than eliding. |
| **E-51** | A scan lands while a target edit is open and unsaved | The scan is processed normally (the scan loop is never blocked by an open edit field); refocus rules exclude the edit field so the scanned characters cannot land in it (`[L-S1-F]` clause 2). Counters recompute against the **saved** target. |
| **E-52** | A scan whose order is found but has no items / a zero-line order | Verdict follows status as normal; the `Items` column renders `0`. A zero-line order in `Prepare Shipment` is OK — closing verifies shipment, not contents. |
| **E-54** | The wedge fires Enter twice on a single read | Suppressed by the client debounce (identical value, inside the window, no intervening `input` event). Two **deliberate** scans of the same parcel are not suppressed — they produce a duplicate warning, which is the feature (§3.2). |
| **E-63** | A parcel already OK-scanned in a **previous, confirmed** closing is scanned again today | Not a duplicate — dedupe is session-scoped (`[BR-37]`). The verdict follows the order's current status, which will normally be `Shipped`/`Completed` → `⚠ Not outbounded`. That is the correct signal: a parcel that already left should not be on today's bench. |
| **E-64** | One order shipped in two boxes under two different tracking numbers | Both scans are `ok` and both count (`ok_count` +2). Dedupe is per tracking number, never per order (`[BR-33]`). |
| **E-65** | Combined box — two orders in one box under one tracking number | The first scan is `ok` (+1), any rescan of the same number is a `duplicate` (+0). Net contribution 1, which matches the one physical box the operator hand-counted. The combined-box reason is logged as an order comment and the duplicate row is removed (`[BR-21]`). |
| **E-66** | A marketing / `MKT-` order's tracking number is scanned | No special handling. The verdict is purely status-based; marketing orders are not excluded from closing, because they are physical parcels that leave the building. |
| **E-67** | The wedge is configured to append **Tab** instead of Enter, or appends nothing | Tab submits and focus stays in the scan input (§3.2). A read with no terminator remains in the field until Enter or the "Scan" button is used — it must never be silently discarded or silently submitted. |
| **E-69** | A multi-line paste of several tracking numbers into the scan input | Processed as sequential scans in the pasted order, one row and one verdict each; a single-value paste behaves like one scan. A per-paste cap is a developer decision. |
| **E-70** | The same tracking scanned twice where the **first** row was not OK (unknown, ambiguous, or an abnormal status) | Still `duplicate` — the dedupe check precedes status evaluation and ignores the earlier row's verdict. Notes carry the extra clause "· that scan was {verdict}" and DC-7 records `first_scan_verdict`, so the pair is diagnosable without a join. |
| **E-77** | Browser autofill, a spell-check suggestion popup, or an IME composition buffer intercepts a wedge burst | Prevented by the input hygiene attributes in §3.2 (`autocomplete="off"`, `spellcheck="false"`, no IME). If a composition event nonetheless occurs, the submit waits for composition end rather than submitting a partial string. |

### 7.2 Manual count & session lifecycle

| ID | Condition | Expected behavior |
|---|---|---|
| **E-15** | Target input is `0`, negative, decimal, non-numeric, or absurd | Start blocked with a visible error (§3.1). Absurd-but-possible values (>9999) get an advisory confirm, never a hard block. The wireframe now raises the red toast too (`[WF-8]` fixed 2026-08-03); the advisory confirm stays `[ADMIN]`. |
| **E-16** | Start Closing with an empty input | Blocked; red toast "✕ Enter the hand-counted parcel count first" — implemented in both the wireframe (`[WF-8]` fixed 2026-08-03) and the admin. |
| **E-17** | Target edited below the current OK count (OK 10 → target 8) | Instant over-scan mismatch; Confirm re-disables with "Confirm Closing (2 over target)"; no scan rows are touched. |
| **E-18** | Target edited to exactly the OK count with 0 outstanding warnings | Confirm enables immediately, with no new scan. This is a legitimate correction of a miscount — and it is exactly why DC-3 captures `ok_count_at_edit`. |
| **E-19** | Edit-count Save with an invalid value | Rejected; the previous target is preserved; the field stays in edit mode; red toast; DC-4. |
| **E-20** | Cancel Closing with scans present | Confirm dialog required (§3.11) — now implemented in the wireframe as `#m-cancel` (`[WF-7]` fixed 2026-08-03). Scan rows are **retained server-side** `[PD-70 · OWNER-PENDING]`; only the session resets. |
| **E-21** | Cancel Closing with zero scans | The dialog is still shown (with the count clause omitted). "Cancel always asks" must be unconditional. |
| **E-41** | Session spans midnight (start 23:50, confirm 00:10) | The snapshot belongs to the **start** date `[PD-78 · OWNER-PENDING]`; History shows one row on the start date; the `Confirmed At` value may be past midnight. |
| **E-42** | A second closing session attempted on a date that is already confirmed | Blocked `[PD-70 · OWNER-PENDING]`: red toast "✕ Today's closing is already confirmed"; DC-2 with `reason=already_confirmed`. |
| **E-53** | A browser tab left open overnight, showing yesterday's confirmed State 4 | On the next interaction the client revalidates against the server: the confirmed session is read-only; starting a new closing requires the new date's State 0. A stale tab must never write into yesterday's session. |
| **E-55** | Start attempted while another operator already has today's session open | Not an error state — the client loads the **existing** session (same target, same rows) rather than creating a second one; DC-2 with `reason=already_in_progress` and an informational toast naming the starter. |
| **E-68** | Every scan row in the session is deleted | Counters go to `ok_count=0`, `outstanding_warnings=0`, `remaining=target`; Confirm is disabled with "Confirm Closing ({target} remaining)"; the session stays `IN_PROGRESS`. Deleting rows never ends a session. |
| **E-72** | A previous date's session is still `IN_PROGRESS` when the operator opens Closing on a new date | The new date cannot be started (`[BR-35]`): red toast "✕ The closing for {date} is still open — confirm or cancel it first"; DC-2 with `reason=prior_date_open`; the client opens the stale session, showing its own date in the banner so the operator is never confused about which day they are closing. |
| **E-73** | The target is edited by another operator while a Confirm request is in flight | The server compares `target_at_press` with the live target and rejects on mismatch (`[BR-29]`), writing DC-22 with both values. A closing is never certified against a number the confirmer did not see. |
| **E-76** | A day on which no parcels shipped at all | Closing cannot be started (target ≥ 1, `[BR-34]`). The date has no History row, which is indistinguishable from — and means the same thing as — "not closed" (E-43). No empty/zero closing record is fabricated. |

### 7.3 Warning resolution & row deletion

| ID | Condition | Expected behavior |
|---|---|---|
| **E-22** | M1 with the Zero Packing checkbox unticked | `[Process Outbound → resolve warning]` stays **disabled** `[PD-77 · OWNER-PENDING]`, and cannot be triggered by keyboard activation either. The wireframe does not enforce this — `[ADMIN]` QA. |
| **E-23** | M1 success | Order status `Processing → Prepare Shipment` globally; the closing row re-judges green in place with the same sequence number; outstanding warnings −1, OK +1; memo (if any) → order Comments + closing log; green toast; send sound `[PD-2 · OWNER-PENDING]`; no page refresh. |
| **E-24** | M1 on an order another operator already transitioned | No double transition. If it is now `Prepare Shipment`: idempotent success, row re-judged green, toast "✓ Order {id} was already outbounded — warning resolved". Any other status: rejected with a red toast naming the current status; the row re-judges against live state `[PD-6 · OWNER-PENDING]`. |
| **E-25** | `[Process Outbound]` double-clicked | Exactly one transition, one comment, one warning-resolution event [G-9]. |
| **E-26** | M2 `Yes — remove` | Row removed; **all** tiles, the progress bar and the gate recompute. `No` / `✕` / backdrop → zero change, zero events. |
| **E-27** | Deleting an OK row that was part of an exact match | Confirm re-disables immediately; label returns to "Confirm Closing (1 remaining)". |
| **E-28** | Deleting a warning row (duplicate / unknown / abnormal-status) | Outstanding warnings −1; the gate may become satisfied; the **raised** counter is unchanged (`[BR-16]`); DC-11 with `method=row_deleted`. |
| **E-29** | M2 `Yes` double-clicked, or the same row deleted twice from two stations | Single deletion, no error, idempotent success [G-9]. |
| **E-56** | M1 opened from a row whose order was cancelled while the modal was open | Treated as E-24's rejection branch: no transition; red toast "✕ Order {id} is cancelled — cannot outbound from closing"; the row re-judges to `⚠ Not outbounded` showing the underlying status plus the `Cancelled` marker (§3.6). |
| **E-57** | An unknown-order row whose order is created in the system mid-session | No retro-judgment (same doctrine as `[BR-22]`). The operator deletes the unknown row and rescans the parcel, producing a clean OK. |
| **E-78** | A `Processing` order with one or more lines still `PENDING` is scanned, and the operator opens M1 | The verdict is `not_outbounded` as usual and `[Process this order]` still appears (the status is `Processing`), but inside M1 `[Process Outbound → resolve warning]` is **disabled** with the reason "Cannot outbound — {n} of {m} items are not inbounded yet. Receive them on Order Detail first." (`[BR-38]`). Ticking Zero Packing does not enable it. No transition, no DC-13/DC-14, and the warning stays outstanding until the lines are received elsewhere and the parcel is rescanned. |
| **E-75** | The Comments hub dropdown is open when a scan verdict arrives | The row, tiles and toast update behind the dropdown. The hub is never auto-closed and never takes focus from the scan input; equally, an open hub never swallows the wedge input (`[L-S1-F]` clause 2 exclusions apply only while a hub field has focus). |

### 7.4 Concurrency (`[ADMIN]` only)

| ID | Condition | Expected behavior |
|---|---|---|
| **E-30** | Two stations scan the same tracking within the same second | Server arbitrates order: exactly one `ok` and one `duplicate`; both feeds render the same two rows with the same sequence numbers `[PD-7 · OWNER-PENDING]`. |
| **E-31** | Two operators press Confirm simultaneously | Exactly one closing record and one snapshot [G-9] (and no sheet write — the sheet is retired, `[PD-71]`); the loser receives the confirmed state, not an error dialog. |
| **E-32** | Operator A edits the target while B is scanning | The gate is recomputed once on one consistent server state; no lost update; B's in-flight scan is unaffected. Optimistic version check on the target value (`[BR-30]`). |
| **E-33** | The same session open on two devices | Shared server state; both show identical sequence numbers, rows and counters within the sync latency budget (developer decision, DQ-4). Neither device may assign a sequence number the other has used. |
| **E-34** | A cancels the session while B is mid-scan | B's next scan is rejected with `reason=session_cancelled` (DC-8) and an explicit red toast **(spec-authored)** "✕ This closing was cancelled by {actor} — start a new closing". It must **never** silently create a new session. |
| **E-58** | A deletes a row while B has M2 open on the same row | B's `Yes — remove` is an idempotent no-op success; B's list refreshes to the merged state. |

### 7.5 Network, device, environment

| ID | Condition | Expected behavior |
|---|---|---|
| **E-35** | Network failure mid-scan (no response) | The retry carries the same `scan_id`, so it can never double-append (`[G-9]`). The UI shows an **unconfirmed** row state, never a fake OK (`[BR-26]`); DC-9 is persisted so a "lost scan" is diagnosable against a physical parcel. |
| **E-36** | Refresh / navigate away / crash / device switch mid-session | Full state restored — target, scan list with original sequence numbers, counters, warnings, gate (`[BR-8]`). Nothing clears. |
| **E-37** | Network failure on Confirm | Retry with the same idempotency key produces exactly one closing record; if the first attempt actually succeeded, the retry returns the confirmed state. |
| **E-38** | ~~Daily Shipping Status update fails after confirmation~~ — **retired, superseded by decision** (`[PD-71]`, 2026-08-03): the sheet no longer exists, so there is nothing to fail | The ID is kept (never renumber) and now asserts the **absence**: confirmation and re-confirm perform **no** external sheet write; the History row and the CSV are the only outputs (QA-PERSIST-08). |
| **E-39** | TTS unavailable (no voices installed, unsupported browser, muted device) | Visual warnings unaffected; no JS error; `🔊 Test voice` degrades gracefully (no crash, no infinite spinner). Consider surfacing an inline hint that audio is unavailable — copy is a developer decision. |
| **E-40** | CSV download fails, or the day has zero scans | Either a well-formed file (headers, zero data rows) or an explicit red error. **Never a silent empty success.** |
| **E-49** | Printer offline | **N/A on this page** — there is no print surface `[PD-68 · OWNER-PENDING]`. Recorded explicitly so QA does not invent a printer scenario here. CSV ≠ print. |
| **E-59** | Server clock vs client clock skew | All timestamps in §5 are **server** timestamps. The `Scan Time` column renders the server value, so two stations never disagree about ordering. |
| **E-71** | The warehouse timezone vs the browser timezone differ (a remote manager confirms the closing from another region) | Every rendered time, the closing date, and the "same calendar day" tests use the warehouse's operating timezone (`[BR-36]`) — never the viewer's. A confirmer in another timezone sees the same date and the same `Confirmed At` as the warehouse. |

### 7.6 Focus, UI, empty states

| ID | Condition | Expected behavior |
|---|---|---|
| **E-48** | Click-anywhere refocus vs typing | Refocus must **not** hijack typing in the M1 memo or checkbox, the M2 modal, the target-edit field, the Comments hub or its search, or any comment input. Refocus resumes when the modal closes or the field blurs. |
| **E-46** | Voice toggle OFF | Warnings still render red rows, pills and toasts; only audio is silenced. Turning it back ON plays one confirmation utterance. |
| **E-47** | Comments hub — mark-all-read, badge consistency, star/unstar | `mark_all_read` is idempotent; the badge is a view over DC-19; a star toggled in Mentions is reflected in Saved and vice versa. |
| **E-43** | A day with no closing at all | No History row. Gaps are legitimate; fabricated rows are forbidden (`[BR-10]` semantics: no row means "not closed"). |
| **E-44** | Closing History on first use (no records) | Empty state copy "No closing records yet — the first confirmed closing will appear here."; no CSV buttons. |
| **E-45** | Cancelled sessions in History | Never displayed `[PD-70 · OWNER-PENDING]`; retained server-side [G-8]. |
| **E-60** | The scan list grows to several hundred rows | The table remains usable at scan speed: newest rows are appended at the bottom and the view keeps the latest row visible without stealing focus. Pagination or virtualization is a developer decision; if pagination is used, the **latest** page is the default view during an active session. |
| **E-61** | Voice toggle state on a shared station between two operators | Governed by the DQ-3 persistence scope; regardless of scope the toggle **defaults to ON at the start of every session**, so a colleague's OFF never silently carries into a new day. |
| **E-62** | An `@mention` in an M1 memo naming a user who no longer exists / has no Slack account | The comment still posts and the status change still commits `[PD-4 · OWNER-PENDING]`; the mention delivery is recorded as a failure in DC-17 and retried per policy. Nothing about the closing is rolled back. |
| **E-74** | An operator clicks an Order ID deep link mid-session | The order opens in a **new tab**; the closing tab keeps its scan input, its focus and its session. Even if the operator navigates the closing tab away, the session survives server-side (`[BR-8]`) — the new-tab rule exists to protect the scan rhythm, not the data. |

### 7.7 Amendment (added 2026-08-03, `[L-SH-2]`/`[L-M3]`)

| ID | Condition | Expected behavior |
|---|---|---|
| **E-79** | `[Amend]` pressed while another date's session is `IN_PROGRESS`, or while some other amendment is open | Blocked (`[BR-41]`): red toast "✕ Another closing is open — confirm or cancel it first", DC-27 `reason=another_session_open`. The confirmed record is untouched. |
| **E-80** | The operator leaves the page, the browser crashes, or the device switches **mid-amendment** | The `AMENDING` state persists server-side exactly like an in-progress session (`[BR-8]`); reopening Closing resumes the amendment. History keeps showing the confirmed v{n} record with an "Amendment in progress" marker (DQ-13) — never the half-finished working state. |
| **E-81** | `[✕ Exit amendment]` without re-confirming | The working changes are discarded from the record; any added scan rows are retained in the audit log [G-8]; the session returns to `CONFIRMED` v{n}; History is unchanged; DC-29. "The confirmed record stays until you re-confirm" holds literally. |
| **E-82** | Two operators press `[Amend]` on the same date, or one double-clicks it | Exactly one `AMENDING` state exists [G-9]; the second entry **loads the existing amendment** (mirror of E-55), DC-27 `reason=already_amending`. Never two working copies of one day. |
| **E-83** | Amending a **past** date (not today's row) | Allowed — the amber banner names the amended date so the operator can never confuse it with today's work. The History row stays on its original date (`[BR-19]` unchanged); the amend timestamp lives in the badge, not in the Date column. The re-confirm's live order-status re-check covers only the rows added in the amendment (§3.24) — by then the day's confirmed parcels have legitimately moved past `Prepare Shipment`, so re-judging them would make this case impossible. |
| **E-84** | Re-confirm attempted with a mismatch or an outstanding warning | Identical to §3.9: the button is disabled with the blocker label ("Re-confirm Closing ({n} remaining / {n} warnings / {n} over target)"); a forced request is rejected server-side with DC-22 and no version increment. |
| **E-85** | A parcel already counted in the confirmed list is scanned again during the amendment | `duplicate` warning — the dedupe scope covers the loaded confirmed rows (§3.24). The count can never be inflated by rescanning an already-counted box; the operator deletes the duplicate row (M2) before re-confirming. |
| **E-86** | A new date's closing is started while an amendment is open | Blocked (`[BR-41]`, extension of `[BR-35]`): red toast, DC-2 `reason=amendment_open`; the client opens the amendment so the operator resolves it first. |

---

## 8. QA Acceptance Criteria (machine-runnable)

### 8.0 How to execute these scenarios

`[WF]` scenarios are executable **today** against the live wireframe. `[ADMIN]` scenarios describe the shipping admin and are deferred until it exists — they cover persistence, server verdicts, concurrency, idempotency, Slack and the sheet handoff. An agent running the `[WF]` set needs nothing beyond the rules below.

**Target.** `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/closing/` — one HTML page, no routing, no network calls, no backend.

**R1 — Reset between mutating scenarios.** The wireframe has **no reset control**. Row deletion, star toggles, the voice toggle, the target-edit lock and `lastState` all persist until the page is reloaded. Reload the page before any scenario whose Given describes an untouched state. Scenarios marked *(destructive)* must be the last in their run or be followed by a reload.

**R2 — Strip annotation dots before comparing text.** Purple annotation dots (`span.dot`) are rendered **inside** several elements, including two `<th>` cells in `#s1` (dot `6` inside `#` and dot `5` inside `Closing Verdict`). Raw `textContent` therefore reads `"#6"` and `"Closing Verdict5"`. Every text assertion in this section is made against this normalization:
```js
const t = el => { const c = el.cloneNode(true);
  c.querySelectorAll('.dot').forEach(d => d.remove());
  return c.textContent.replace(/\s+/g, ' ').trim(); };
```
Clicking `#annoToggle` only sets `display:none` on the dots — it does **not** remove them from `textContent`. Use the clone-and-strip helper, not the toggle.

**R2b — Beware nested *functional* descendants; `.dot` is not the only text polluter.** Four elements this section asks you to compare carry a nested control whose text is concatenated by `textContent`. Assert them with `starts with` (the form used throughout §8 for these four), or strip the descendant first:

| Element | Nested descendant | R2-normalized text |
|---|---|---|
| `#m-process header`, `#m-scandel header` | `<button class="x">✕</button>` | `"… Order 413511✕"`, `"Delete Scan Row✕"` |
| `[data-open="inbox1"]` | `<span class="badge-n">2</span>` | `"💬 Comments2"` |
| `.paneheader` (both panes) | `<small>Mark all read</small>` / `<small>Unstar to remove from the list</small>` | `"Comments mentioning me · Click to open the order Mark all read"`, `"Saved comments · Click to open the order Unstar to remove from the list"` |
| `span.user` | `<span class="avatar">Y</span>` | `"YYongwon Ryu"` |

An extended helper is acceptable and equivalent: `c.querySelectorAll('.dot, .badge-n, .paneheader small, header button.x, .avatar').forEach(d => d.remove())`. If you use it, the four rows above become plain equality against the string without the descendant.

**R3 — Address states and modals by attribute, never by tab text.** Use `.wf-tab[data-state="s2b"]`, `.wf-tab[data-modal="m-process"]`, `section#s2b`, `#m-process`, `#m-amend`. (`[WF-12]`'s duplicated "Modal: Process Processing Order" tab was removed 2026-08-03, so tab texts are now unique — the attribute rule stands anyway, because label text is demo chrome and may change.)

**R4 — Instrument speech before the page's script runs** (required for every QA-VOICE scenario). Inject on document start:
```js
window.__spoken = [];
window.SpeechSynthesisUtterance = function (txt) { this.text = txt; this.lang = ''; this.voice = null; };
Object.defineProperty(window, 'speechSynthesis', { configurable: true, value: {
  speak: u => window.__spoken.push({ text: u.text, lang: u.lang }),
  cancel: () => {}, getVoices: () => [] } });
```
Assertions then read `window.__spoken`. Clear it (`window.__spoken.length = 0`) between When-steps inside one scenario.

**R5 — Row addressing.** Scan-list rows are addressed by the text of their first cell (`#1` … `#7`) within the active section, e.g. `[...document.querySelectorAll('#s1 table.tbl tbody tr')].find(r => t(r.cells[0]) === '#3')`. Sequence numbers are stable and never renumbered (`[BR-17]`), so this addressing survives deletions.

**R6 — Byte-exact** means: identical after R2 normalization, including the `·` separators, the `—` em dashes, the `✓`/`⚠`/`✕` glyphs and the `①` circled digit. Do not substitute ASCII equivalents.

**R6b — Assertion verbs are normative.** Two conforming agents must return the same verdict on the same page, so the verbs are fixed:
- `reads` · `reads exactly` · `is exactly` · **byte-exact** → **strict equality** after R2 (and R2b where it applies).
- `starts with` → `String.prototype.startsWith` after R2.
- `contains` · `carries the text` → substring after R2.
- `yields N` → `querySelectorAll(...).length === N`.
Where a clause names no verb it is strict equality. Never relax `reads` to *contains* to make a scenario pass — a mismatch is a FAIL to be reported, not normalized away.

**R7 — Page-global demo state.** `voiceOn` is a single page-level variable shared by all states (U-g), so a toggle set in State 1 governs the auto-play of States 2/2b/3. `lastState` is only updated by `[data-goto]` clicks, never by `wf-bar` tabs. `delRow` is reset after each M2 confirm.

**R8 — Known demo limitations that are NOT bugs.** Assert the demo behavior in `[WF]`, the correct behavior in `[ADMIN]`: tiles do not recompute after a row deletion; State 1's "Remaining scans" tile reads 79 instead of 81 (U-a); State 4's scan input looks enabled (U-b); the Comments hub has no search (U-c) and is wired only in State 1 (U-e); the voice controls are wired only in State 1 (U-g); Order ID cells are not links (U-f); States 2/2b/3 render a muted target line instead of the full banner (U-j). The Amend demo mutates page state (`#amendBanner`, `#targetIn1`, `#confirmBtn1`) — `[✕ Exit amendment]` restores it, and QA-AMEND-04/05 are *(destructive — reload after)*. **No longer limitations** (fixed 2026-08-03): `#startBtn0` now raises red validation toasts (`[WF-8]`, QA-S0-02) and `#closeCancel` now opens the `#m-cancel` dialog (`[WF-7]`, QA-TARGET-04).

**R9 — Activating a state or a modal.** Every scenario's Given names a section or a modal but not the route to it. Unless the scenario says otherwise: **to activate a state, click its `.wf-tab[data-state="sX"]`; to open a modal outside its per-row entry point, click `.wf-tab[data-modal="m-…"]`.** Both are wireframe chrome (`[L-F4]`) and exist only to reach a rendering a reviewer could not otherwise produce — never treat them as shipping affordances. In `[ADMIN]` scenarios the equivalent Given is "the live session is in that state"; there is no tab.

**R10 — PD citations in scenario headings are shorthand.** A `[PD-n]` in a QA heading points at the behavior's defining sentence in §3 or §7, which carries the full `[PD-n · OWNER-PENDING]` tag. The scenario asserts the provisionally-adopted behavior, which is the behavior to build until the owner rules. **No NO-DEFAULT questions remain** (§9.2): `[PD-71]` was resolved 2026-08-03 (the sheet is retired — asserted as an *absence* by QA-CONFIRM-10/16 and QA-PERSIST-08) and `[PD-74]` was resolved 2026-08-03 (the Amend flow, asserted by the QA-AMEND block).

**Reading a scenario.** Every Then-clause is an assertion. Where a scenario asserts a persisted event it names the `DC-n` id; §8.17 proves every event in §5.1 has at least one asserting scenario and §8.18 does the same for every `[E-n]`.

**Totals: 193 scenarios — 74 `[WF]` · 119 `[ADMIN]` · 77 negative tests (39.9%).**
> Census delta 2026-08-03: 192 → **193** with QA-AMEND-16 (`[ADMIN]`, non-negative — it asserts a success path plus its rejection branch), added with the §3.24 revalidation-scope clarification. `[WF]` and the negative count are unchanged, so the negative share moves 40.1% → 39.9%.

---

### 8.1 QA-S0 — Pre-start & start gating `[L-S0-1]`

**QA-S0-01 `[WF]`** — the page opens on the pre-start screen
- Given the live wireframe is freshly loaded
- Then `section#s0` has class `on` and `section#s1`, `#s2`, `#s2b`, `#s3`, `#s4`, `#shist` do not
- And `.wf-tab[data-state="s0"]` has class `on` and its text is "0 · Before Start (manual count)"
- And exactly one element matches `[...document.querySelectorAll('#s0 .pagepad div')].filter(e => t(e) === "① Today's Outbound Target (manual count)")` — that element is the card heading (the wireframe styles it inline, so there is no class to address; assert by exact R2 text and by a match count of 1)
- And `#targetIn0` exists with placeholder "Hand-counted qty" and `value === ""`, followed by the literal text "orders" and the button `#startBtn0` labelled "Start Closing"

**QA-S0-02 `[WF]` (negative)** — Start is blocked with an explicit error on empty/invalid input `[E-15]` `[E-16]` (`[WF-8]` fixed 2026-08-03)
- Given `section#s0` is active and `#targetIn0.value` is `""`
- When `#startBtn0` is clicked
- Then `section#s0` still has class `on` and `section#s1` does **not**, and no `.scanbig` element exists inside the active section
- And a red toast (`#s0 .toast.err`) reads "✕ Enter the hand-counted parcel count first" (the toast self-removes after ~2.6 s; assert immediately)
- When `#targetIn0.value` is set to `abc` (repeat with `0`) and `#startBtn0` is clicked
- Then `section#s0` still has class `on` and the newest red toast reads "✕ The count must be a whole number of 1 or more" (toasts prepend — the newest is the **first** `.toast.err` in the DOM)
- And the >9999 advisory confirm and the server-side rejections remain `[ADMIN]` (QA-S0-05/09)

**QA-S0-03 `[WF]`** — Start with a value enters the in-progress screen *(destructive — reload after)*
- Given `#targetIn0.value` is set to `84`
- When `#startBtn0` is clicked
- Then `section#s1` has class `on`, `section#s0` does not, and `.wf-tab[data-state="s1"]` has class `on`

**QA-S0-04 `[WF]` (negative)** — the pre-start screen exposes nothing but the count
- Given `section#s0` is active
- Then within `#s0` there is no `.scanbig`, no `.clsstat`, no `.prog`, no `table.tbl`, no `.okline` and no button whose normalized text starts with "Confirm Closing"

**QA-S0-05 `[ADMIN]` (negative)** — invalid targets are rejected with explicit copy `[E-15]`
- Given the pre-start screen
- When Start is pressed with `0`, `-3`, `2.5`, or `abc`
- Then the session is not created, the screen does not advance, and a red toast reads "✕ The count must be a whole number of 1 or more"
- And with an empty value the toast reads "✕ Enter the hand-counted parcel count first"

**QA-S0-06 `[ADMIN]`** — starting persists the session
- When Start succeeds with target 84
- Then a `closing.session_started` event (**DC-1**) exists with `target_qty=84`, the acting user as actor, a server `started_at`, and the closing date
- And a green toast reads "✓ Closing started — target 84 orders" / "Scan the tracking barcode of each packed parcel"
- And the State 1 banner reads "Closing in progress (started {hh:mm} · {actor})"
- And the scan input is enabled and focused

**QA-S0-07 `[ADMIN]` (negative)** — starting on an already-confirmed date is blocked `[E-42]`
- Given today's closing is `CONFIRMED`
- When Start is attempted
- Then no session is created, a red toast reads "✕ Today's closing is already confirmed", and a `closing.start_rejected` event (**DC-2**) exists with `reason=already_confirmed`

**QA-S0-08 `[ADMIN]`** — starting while a colleague's session is open loads that session `[E-55]`
- Given operator A has an `IN_PROGRESS` session with 12 rows
- When operator B presses Start
- Then B sees A's session (same target, same 12 rows, same sequence numbers), not a new one
- And **DC-2** exists with `reason=already_in_progress` and the existing `session_id`

**QA-S0-09 `[ADMIN]`** — an absurd but possible count is advisory, never blocked `[E-15]`
- When Start is pressed with `12000`
- Then an amber inline confirm reads "That is far above a normal day (12000). Start anyway?"
- And confirming creates the session normally with `target_qty=12000` (**DC-1**)

**QA-S0-10 `[ADMIN]` (negative)** — a zero-parcel day produces no closing record `[E-76]` `[BR-34]`
- When Start is pressed with `0`
- Then the session is not created and the red whole-number toast appears
- And that date has **no** Closing History row afterwards, and no zero-valued record is fabricated anywhere

**QA-S0-11 `[ADMIN]` (negative)** — an unresolved earlier session blocks a new date `[E-72]` `[BR-35]`
- Given the session for 2026-08-02 is still `IN_PROGRESS`
- When an operator opens Closing on 2026-08-03 and presses Start
- Then no new session is created, a red toast reads "✕ The closing for 2026-08-02 is still open — confirm or cancel it first", **DC-2** exists with `reason=prior_date_open`
- And the client opens the 2026-08-02 session with its own date shown in the banner

---

### 8.2 QA-SCAN — Scan input protocol & focus `[L-S1-1]` `[L-S1-F]`

**QA-SCAN-01 `[WF]`** — the scan input is present and correctly shaped
- Given `section#s1` is active
- Then `#s1 .scanbig input` exists with placeholder "Scan the tracking barcode — outbound status is judged instantly on scan" and value `YT2618100710108810`
- And a sibling `button.btn-blue` labelled "Scan" exists
- And the input is **not** `disabled`

**QA-SCAN-02 `[WF]` (negative)** — no scan surface exists before start `[E-9]`
- Given `section#s0` is active
- Then `#s0 .scanbig` does not exist and `#s0` contains no `input` other than `#targetIn0`

**QA-SCAN-03 `[ADMIN]`** — the scanner's Enter submits and focus returns selected
- Given an active session and focus in the scan input
- When a scanner types a tracking number followed by Enter
- Then a verdict renders, the input regains focus, and its selection covers the whole value so the next scan overwrites it
- And a `closing.scan_recorded` event (**DC-7**) exists with `seq`, `verdict`, `station` and the acting worker

**QA-SCAN-04 `[ADMIN]` (negative)** — the page never refreshes between scans `[G-1]`
- Given a counter variable is set on `window` before the first scan
- When 20 consecutive scans are performed
- Then the counter still exists (no document reload occurred) and the scan list, tiles and gate updated in place

**QA-SCAN-05 `[ADMIN]` (negative)** — an empty submit does nothing `[E-1]`
- When Enter is pressed with an empty input
- Then no row is appended, no counter changes, no toast appears, and no **DC-7** is written

**QA-SCAN-06 `[ADMIN]` (negative)** — a truncated read is rejected before lookup `[E-2]`
- When a value shorter than the minimum length is submitted
- Then a red toast reads "✕ Incomplete scan — scan again", no row appears, and no **DC-7** exists

**QA-SCAN-07 `[ADMIN]`** — scanner artifacts are normalized and both strings persist `[E-12]`
- When the submitted value carries a trailing CR/LF/Tab and surrounding spaces
- Then the lookup uses the normalized value and **DC-7** contains both `tracking_no_raw` and `tracking_no_normalized`

**QA-SCAN-08 `[ADMIN]` (negative)** — a double-Enter from one read is suppressed, a deliberate rescan is not `[E-54]`
- When the wedge emits the same value twice inside the debounce window with no intervening `input` event
- Then exactly one **DC-7** exists
- When the operator deliberately rescans the same parcel later in the session
- Then a second **DC-7** exists with `verdict=duplicate`

**QA-SCAN-09 `[ADMIN]`** — the input is never locked while a lookup is in flight `[BR-26]`
- Given a lookup artificially delayed by 2 s
- When the operator scans two further parcels during that delay
- Then all three scans are accepted, rendered in server-assigned sequence order, and the input accepted keystrokes throughout
- And no row rendered green before its verdict returned

**QA-SCAN-10 `[ADMIN]` (negative)** — a lookup failure never renders as OK `[E-35]`
- Given the scan endpoint returns a network error
- Then the row renders in an explicit unconfirmed state (never green, never `✓ Outbounded`), a red toast appears, and a `closing.scan_lookup_failed` event (**DC-9**) exists
- And a retry carrying the same `scan_id` appends exactly one row

**QA-SCAN-11 `[ADMIN]`** — click-anywhere refocus with select-all
- Given an active session and focus lost by clicking the page background
- When any non-interactive area is clicked
- Then focus returns to the scan input and its entire value is selected

**QA-SCAN-12 `[ADMIN]` (negative)** — refocus does not hijack typing `[E-48]`
- Given M1 is open and the operator is typing in the memo textarea
- Then focus stays in the textarea and no character is lost
- And the same holds for the M2 modal, the target-edit field and the Comments hub search
- And refocus resumes once the modal closes

**QA-SCAN-13 `[WF]` (negative)** — the State 4 scan input is rendered enabled in the demo (documents U-b)
- Given `section#s4` is active
- Then `#s4 .scanbig input` exists, has `value === ""` and does **not** carry the `disabled` attribute
- And this is a known demo divergence: the shipping behavior is disabled (QA-CONFIRM-12)

**QA-SCAN-14 `[ADMIN]`** — a multi-line paste becomes sequential scans `[E-69]`
- When three newline-separated tracking numbers are pasted into the scan input and submitted
- Then three rows appear in the pasted order with consecutive sequence numbers and three **DC-7** events exist

**QA-SCAN-15 `[ADMIN]`** — Tab terminates a read; an unterminated read does not submit `[E-67]`
- When a wedge appends Tab instead of Enter
- Then the scan submits and focus remains in the scan input (focus does not move to the "Scan" button)
- When a read arrives with no terminator
- Then no submit occurs, the value stays in the field, and no **DC-7** exists until Enter or the "Scan" button is used

**QA-SCAN-16 `[WF]` (negative)** — the wireframe implements no refocus loop (documents the demo gap)
- Given `section#s1` is active
- When the page background is clicked
- Then focus does **not** move to `#s1 .scanbig input` (the demo has no refocus handler)
- And the shipping behavior is asserted in QA-SCAN-11

**QA-SCAN-17 `[ADMIN]` (negative)** — autofill, spell-check and IME composition cannot corrupt a wedge burst `[E-77]`
- Given an active session and focus in the scan input
- Then the input carries `autocomplete="off"`, `autocapitalize="off"` and `spellcheck="false"`, and no browser suggestion popup is rendered while a wedge burst is typed
- When a `compositionstart` event fires mid-burst and the terminator (Enter or Tab) arrives before `compositionend`
- Then the submit is **deferred to `compositionend`**: no partial string is submitted, exactly one row is appended, and exactly one **DC-7** exists carrying the complete tracking number
- And no **DC-7** exists for any partial prefix of that value

---

### 8.3 QA-VERDICT — Verdict engine `[L-S1-5]` `[L-S1-2]` `[L-S1-6]` `[L-S2-1]`

**QA-VERDICT-01 `[WF]`** — an OK row renders green with the exact pill
- Given `section#s1` is active
- Then the row whose first cell is `#1` has class `row-ok`, its Order Status cell contains `span.cs-shipped` with text "Prepare Shipment", and its Closing Verdict cell contains `span.cs-shipped` with text "✓ Outbounded"
- And its Notes cell reads "–" and its Worker cell reads "Dean"

**QA-VERDICT-02 `[WF]`** — the compact OK line is present and byte-exact `[L-S1-2]`
- Given `section#s1` is active
- Then `#s1 .okline` exists; its `b` element reads exactly "✓ #5 Outbounded"; it contains the text "Order 413540 · Tracking YT2618100710108810 · Prepare Shipment" and the muted right-hand text "18:41:07 · Dean"
- And `#s1` contains **no** `.bigstatus` element (no large OK panel — removed 2026-07-23)

**QA-VERDICT-03 `[WF]`** — a Processing scan renders the warning row and the in-row action
- Given `section#s2` is active
- Then the row whose first cell is `#4` has class `row-bad`, its Order Status cell shows `span.cs-processing` "Processing", its Closing Verdict cell shows `span.cs-processing` "⚠ Not outbounded", and its Notes cell contains a button labelled "Process this order" carrying `data-modal="m-process"`
- And `#s2` contains no `.bigstatus` element (no large red panel — `[WF-5]`)

**QA-VERDICT-04 `[WF]` (negative)** — OK rows carry no resolution button
- Given `section#s1` is active
- Then no `tr.row-ok` in `#s1` contains a button labelled "Process this order", and no `tr.row-ok` contains `span.cs-processing` or `span.cs-dup`

**QA-VERDICT-05 `[WF]`** — the scan-list column contract `[L-S1-6]`
- Given `section#s1` is active
- Then `#s1 table.tbl thead th` yields exactly 10 cells whose **R2-normalized** texts are, in order: `#`, `Scan Time`, `Tracking Barcode`, `Order ID`, `Items`, `Order Status`, `Closing Verdict`, `Worker`, `Notes`, `` (empty, 44px)
- And note that raw `textContent` would read `#6` and `Closing Verdict5` because two annotation dots sit inside those cells — the assertion is made after stripping `.dot` (R2)
- And the paragraph beneath the table reads "Sequence (#) = cumulative from 1 after closing starts · lowest first · all rows stored in the backend (fully included in the closing report export)"

**QA-VERDICT-06 `[ADMIN]`** — only `Prepare Shipment` is OK `[BR-1]`
- When a tracking number is scanned whose order status is `Prepare Shipment`
- Then the verdict is `ok`, the row is green, `ok_count` increments by 1, no sound plays, and **DC-7** records `verdict=ok` with `order_status_at_scan=prepare-shipment`

**QA-VERDICT-07 `[ADMIN]` (negative)** — abnormal statuses warn without offering M1 `[E-5]` `[PD-76]`
- When orders in `Shipped`, `Completed`, `On Hold`, `Refunded`, `Failed` and `Pending` are scanned
- Then each row shows the `⚠ Not outbounded` pill, the Order Status column shows the **actual** status, the Notes read "Order status is {status} — not shipped from this closing", and **no** "Process this order" button is rendered
- And each row is an outstanding warning and contributes 0 to `ok_count`
- When an order carrying the **cancellation flag** is scanned (cancellation is a flag, not a ninth status — §3.6)
- Then its row shows the same `⚠ Not outbounded` pill, its Order Status column renders the **underlying** status label plus a `Cancelled` marker, no "Process this order" button is rendered, and **DC-7** records `order_status_at_scan` as one of the 8 lowercase-hyphenated values — never the literal `cancelled`

**QA-VERDICT-08 `[ADMIN]` (negative)** — an ambiguous tracking number is never auto-resolved `[E-14]`
- Given one tracking number attached to orders 413511 and 413540
- When it is scanned
- Then no order is silently selected, the row is a warning excluded from `ok_count`, the Notes cell reads "Matches 2 orders — 413511, 413540 — resolve before closing", and **DC-7** records `verdict=ambiguous` with `colliding_order_ids=[413511,413540]`

**QA-VERDICT-09 `[ADMIN]`** — the OK toast copy
- When an OK scan completes
- Then a green toast reads "✓ Outbound confirmed — {tracking}" with subtext "Ready for the next barcode scan"

**QA-VERDICT-10 `[ADMIN]` (negative)** — warnings toast in red and name the verdict
- When a Processing scan completes
- Then the toast is red, reads "⚠ Not outbounded — {tracking}" with subtext "Order {order_id} · Processing", and a `closing.warning_raised` event (**DC-10**) exists with `warning_class=not_outbounded`

**QA-VERDICT-11 `[ADMIN]` (negative)** — an inbound-request tracking number does not resolve here `[E-13]` `[PD-8]`
- Given a tracking number registered on an inbound request but on no customer order
- When it is scanned at closing
- Then the verdict is `unknown` (never a match against the inbound request), `ok_count` is unchanged, and no inbound-request record is touched
- And the same holds for a product EAN starting `8809`, a bare Order ID, and a Deleo number

**QA-VERDICT-12 `[ADMIN]`** — a split order counts once per parcel `[E-64]` `[BR-33]`
- Given order 413600 shipped in two boxes with tracking `YTA…` and `YTB…`
- When both are scanned
- Then both verdicts are `ok` and `ok_count` increases by 2

**QA-VERDICT-13 `[ADMIN]`** — a combined box counts once `[E-65]` `[BR-33]`
- Given orders 413601 and 413602 shipped in one box under tracking `YTC…`
- When `YTC…` is scanned twice
- Then the first is `ok` (+1) and the second is `duplicate` (+0), so the box contributes exactly 1 to `ok_count`

**QA-VERDICT-14 `[ADMIN]` (negative)** — a parcel from a previous closing is not a duplicate `[E-63]` `[BR-37]`
- Given tracking `YTD…` was OK-scanned in yesterday's confirmed closing and its order is now `Shipped`
- When it is scanned in today's session
- Then the verdict is `not_outbounded` (not `duplicate`), the Order Status column shows `Shipped`, and no cross-day duplicate index is consulted

**QA-VERDICT-15 `[ADMIN]`** — a zero-line order in `Prepare Shipment` is still OK `[E-52]`
- Given order 413700 has status `prepare-shipment` and **zero** line items
- When its tracking number is scanned
- Then the verdict is `ok`, the row is green, `ok_count` increments by 1, and the `Items` cell renders exactly `0` (not `–`, not blank)
- And **DC-7** records `item_count=0` with `verdict=ok` — closing verifies that a parcel shipped, never what is inside it

**QA-VERDICT-16 `[ADMIN]`** — a marketing order is judged purely on status `[E-66]`
- Given a marketing order whose order number carries the `MKT-` prefix, status `prepare-shipment`
- When its tracking number is scanned
- Then the verdict is `ok` and it counts toward `ok_count` exactly like any other parcel — no prefix-based exclusion, no special pill, no separate bucket
- And the same order in `processing` yields `not_outbounded` with the `[Process this order]` button, identical to a non-marketing order
- And no filter anywhere in the closing pipeline references the order-number prefix

---

### 8.4 QA-UNKNOWN — Unknown order `[L-S2b-1]`

**QA-UNKNOWN-01 `[WF]`** — the unknown row renders with dashes and the red pill
- Given `section#s2b` is active
- Then the row whose first cell is `#7` has class `row-bad`, its Order ID, Items and Order Status cells all read `–`, and its Closing Verdict cell contains `span.cs-dup` with text "⚠ Unknown order"

**QA-UNKNOWN-02 `[WF]`** — the prescribed operator copy is intact
- Then that row's Notes cell reads exactly "Mistyped tracking no. or an order from another system — check the physical label"

**QA-UNKNOWN-03 `[WF]`** — the warnings tile names the unknown class
- Given `section#s2b` is active
- Then `#s2b .tile.warn .lab` reads "Warnings (not outbounded · duplicate · unknown order)" and its `.val` reads `4`
- And `#s2b .proglab` contains "unknown orders are not counted"

**QA-UNKNOWN-04 `[ADMIN]` (negative)** — an unknown scan never increments OK `[E-3]` `[BR-6]`
- When a tracking number matching no order is scanned
- Then `ok_count` is unchanged, `outstanding_warnings` increments by 1, and **DC-7** records `verdict=unknown` with `order_id=null`

**QA-UNKNOWN-05 `[ADMIN]` (negative)** — an unknown scan raises no Slack and creates no pool item `[BR-23]`
- When an unknown scan is recorded
- Then no message is dispatched to `#unrecognized-tracking`, no unrecognized-pool item is created, and no Slack event of any kind exists for this action

**QA-UNKNOWN-06 `[ADMIN]`** — an unknown row blocks confirmation until cleared
- Given `ok_count == target` and the only outstanding warning is one unknown row
- Then Confirm is disabled with the label "Confirm Closing (1 warnings)"
- When that row is deleted via M2
- Then Confirm becomes enabled and a `closing.warning_resolved` event (**DC-11**) exists with `method=row_deleted`

**QA-UNKNOWN-07 `[ADMIN]` (negative)** — an unknown row is not retro-judged when the order appears `[E-57]`
- Given an unknown row for tracking `YTE…`
- When the matching order is created in the system while the session is still open
- Then the existing row still shows `⚠ Unknown order` and no automatic re-judgment event exists
- And the operator's path is delete + rescan, which produces a new `ok` row with a new sequence number

---

### 8.5 QA-DUP — Duplicate scan `[L-S3-1]`

**QA-DUP-01 `[WF]`** — the duplicate row cites the collision with time and worker
- Given `section#s3` is active
- Then the row whose first cell is `#6` has class `row-bad`, its Closing Verdict cell contains `span.cs-dup` "⚠ Duplicate scan", and its Notes cell contains a `b` element reading "Duplicate of #2" followed by the text "— first scanned 18:40:18 (Miranti)"

**QA-DUP-02 `[WF]`** — the State 1 duplicate row variant
- Given `section#s1` is active
- Then the row whose first cell is `#3` has class `row-bad`, shows `span.cs-dup` "⚠ Duplicate scan", and its Notes cell contains a `b` element reading "Duplicate of #2" and the text "same tracking no. (check for combined box)"
- And this earlier phrasing is superseded by the canonical string in §3.7 (time + worker), which State 3 already uses

**QA-DUP-03 `[WF]`** — the first scan of a duplicated tracking is annotated
- Given `section#s1` is active
- Then the row `#2` (tracking `YT2618100710184356`, worker Miranti) has class `row-ok` and its Notes cell reads "First scan"
- And the same annotation appears on row `#2` of `section#s3`

**QA-DUP-04 `[ADMIN]` (negative)** — duplicates are never double-counted `[BR-5]`
- Given a tracking already scanned OK
- When it is scanned again
- Then `ok_count` is unchanged, `outstanding_warnings` increments by 1, and **DC-7** records `verdict=duplicate` with `duplicate_of_seq`, `first_scan_at` and `first_scan_actor`

**QA-DUP-05 `[ADMIN]`** — the third scan references the first scan, not the previous duplicate `[E-7]`
- When the same tracking is scanned a third time
- Then the new row's `duplicate_of_seq` equals the sequence number of the **first** row for that tracking, not of the second

**QA-DUP-06 `[ADMIN]`** — the duplicate warning enters the ledger
- When a duplicate is recorded
- Then **DC-10** exists with `warning_class=duplicate` and links to the raising **DC-7**

**QA-DUP-07 `[ADMIN]` (negative)** — deleting the original does not re-judge the survivor `[E-8]` `[PD-75]`
- Given rows #2 (OK) and #6 (duplicate of #2) for one tracking
- When row #2 is deleted via M2
- Then row #6 still shows `⚠ Duplicate scan`, its Notes still reference `#2`, and no automatic re-judgment event exists

**QA-DUP-08 `[ADMIN]`** — resolving a duplicate preserves the raised counter `[BR-16]` `[PD-69]`
- Given 3 warnings raised in the session, all resolved
- When the day is confirmed
- Then the tiles show `Warnings (resolved) 0`, the Warning Resolution Summary states "3 warnings today", and the History row shows `3→3`

**QA-DUP-09 `[ADMIN]`** — a duplicate of a non-OK row `[E-70]`
- Given row #4 is an `unknown` row for tracking `YTF…`
- When `YTF…` is scanned again
- Then the new row is `duplicate`, its Notes read "Duplicate of #4 — first scanned {hh:mm:ss} ({worker}) · that scan was unknown", and **DC-7** records `first_scan_verdict=unknown`

**QA-DUP-10 `[ADMIN]`** — "First scan" is applied retroactively to the original row
- Given row #2 is `ok` with Notes "–"
- When the same tracking is scanned again
- Then row #2's Notes become "First scan" while its verdict, sequence number, scan time and counter contribution are unchanged
- And no additional DC event is written for that annotation (§5.2)

---

### 8.6 QA-VOICE — Voice alerts `[L-S1-3]` `[G-3b]`

All scenarios in this block require the R4 instrumentation.

**QA-VOICE-01 `[WF]`** — entering a warning state speaks the exact utterance
- Given a freshly loaded, instrumented page with `window.__spoken` empty
- When `.wf-tab[data-state="s2"]` is clicked
- Then `window.__spoken` has exactly one entry with `text === "Please check this order"` and `lang === "en-US"`
- And `section#s2` carries the attribute `data-voice="Please check this order"`
- And the same holds for `.wf-tab[data-state="s2b"]` and `.wf-tab[data-state="s3"]`

**QA-VOICE-02 `[WF]`** — the toggle reflects state
- Given `section#s1` is active
- When `#voiceToggle` is clicked
- Then `#voiceState` text becomes "Off" and `#s1 .vtrack` gains class `off`
- And `window.__spoken` gains **no** entry from this click

**QA-VOICE-03 `[WF]` (negative)** — with voice OFF the visual warning is never suppressed `[E-46]`
- Given `#voiceState` reads "Off" and `window.__spoken` has been cleared
- When `.wf-tab[data-state="s3"]` is clicked
- Then `window.__spoken` is still empty
- And the row `#6` still renders `span.cs-dup` "⚠ Duplicate scan" with class `row-bad`, and the red `.proglab` copy is unchanged

**QA-VOICE-04 `[WF]`** — Test voice overrides the toggle without changing it
- Given `#voiceState` reads "Off", `section#s1` is active, `window.__spoken` cleared
- When `#voiceTest` (label "🔊 Test voice") is clicked
- Then `window.__spoken` has exactly one entry "Please check this order"
- And `#voiceState` still reads "Off" and `.vtrack` still has class `off`

**QA-VOICE-05 `[WF]`** — turning the toggle ON plays one confirmation utterance
- Given `#voiceState` reads "Off" and `window.__spoken` cleared
- When `#voiceToggle` is clicked
- Then `#voiceState` becomes "On", `.vtrack` loses class `off`, and `window.__spoken` has exactly one entry

**QA-VOICE-06 `[ADMIN]`** — the toggle change is persisted
- When the toggle is switched off and on
- Then two `closing.voice_alert_toggled` events (**DC-20**) exist with `old → new` values, and the toggle is ON again at the next session start `[E-61]`

**QA-VOICE-07 `[ADMIN]` (negative)** — TTS unavailable degrades gracefully `[E-39]`
- Given a browser with zero voices / speech synthesis unavailable
- When a warning verdict is rendered
- Then no JS error is raised, the red row, pill and toast render normally, and "🔊 Test voice" does not throw

**QA-VOICE-08 `[WF]`** — the replay control exists in every state
- Then `#s1` contains `#voiceTest` labelled "🔊 Test voice"; `#s2`, `#s2b` and `#s3` each contain a `.sim-voice` button labelled "🔊 Play again"; `#s4` contains a `.sim-voice` button labelled "🔊 Test voice"
- And this label split is demo copy (U-h): the canonical admin label is "🔊 Test voice" everywhere

**QA-VOICE-09 `[ADMIN]` (negative)** — OK scans are silent
- When an OK scan completes with the voice toggle ON
- Then no TTS utterance is spoken **and** no `[G-3a]` send sound plays — the audio channel on this page carries warnings only (`[BR-13]`)

---

### 8.7 QA-COUNT — Tiles, progress, gate arithmetic `[L-S1-4]` `[L-S1-8]`

**QA-COUNT-01 `[WF]`** — State 1 tiles render the demo values (documents defect U-a)
- Given `section#s1` is active
- Then the four `#s1 .tile .val` values read `84`, `3`, `2`, `79` in order
- And the four `#s1 .tile .lab` values read "Today's outbound target (manual input)", "OK (outbounded)", "Warnings (not outbounded · duplicate)", "Remaining scans"
- And the `79` is a known demo-data defect: the specified formula gives `81` (asserted in QA-COUNT-04), and the same screen's `.proglab` already says "81 short of the manual count"

**QA-COUNT-02 `[WF]`** — the progress bar segments
- Given `section#s1` is active
- Then `#s1 .prog i.p-ok` has inline width `3.6%` and `#s1 .prog i.p-warn` has inline width `2.4%`

**QA-COUNT-03 `[WF]`** — the progress label states the gate rule verbatim
- Then `#s1 .proglab` reads "Closing progress 3.6% — OK 3/84 (81 short of the manual count) · 2 warnings to resolve — closing confirms only at an exact OK 84/84 match with 0 warnings; over-scan is also a mismatch"

**QA-COUNT-04 `[ADMIN]` (negative)** — the Remaining formula is `target − OK`, warnings excluded
- Given target 84, OK 3, outstanding warnings 2
- Then the Remaining tile reads `81`, not `79`, and warnings never subtract from Remaining

**QA-COUNT-05 `[ADMIN]`** — deleting a row recomputes everything
- Given OK 5 / warnings 2 / target 10
- When an OK row is deleted
- Then OK becomes 4, Remaining becomes 6, the green bar segment shrinks accordingly, and the Confirm label updates in the same render — with no page refresh

**QA-COUNT-06 `[ADMIN]`** — an M1 resolution moves a row between buckets
- Given one `Processing` warning row
- When it is resolved via M1
- Then outstanding warnings decrement by 1, OK increments by 1, Remaining decrements by 1, and the row keeps its original sequence number

**QA-COUNT-07 `[ADMIN]`** — outstanding vs raised are tracked separately `[BR-16]`
- Given 3 warnings raised and 3 resolved
- Then the Warnings tile reads 0 while the raised counter used by History and the State 4 summary reads 3

**QA-COUNT-08 `[ADMIN]` (negative)** — over-scan re-disables the gate `[E-11]`
- Given OK 84 of target 84 with 0 warnings and Confirm enabled
- When an 85th parcel is scanned OK
- Then Confirm becomes disabled with the label "Confirm Closing (1 over target)", the Remaining tile reads `0`, and `.proglab` states the over-scan rather than a shortfall

**QA-COUNT-09 `[WF]`** — warning-state tiles in the demo
- Given `section#s2b` is active, then its four `.tile .val` read `84`, `4`, `4`, `80` and `#s2b .prog i.p-warn` width is `4.8%`
- Given `section#s3` is active, then its four `.tile .val` read `84`, `4`, `3`, `80` and `#s3 .proglab` contains "duplicates are not double-counted"

**QA-COUNT-10 `[WF]`** — State 2 tiles and bar
- Given `section#s2` is active
- Then its four `.tile .val` read `84`, `4`, `3`, `80`; `#s2 .prog i.p-ok` width is `4.8%` and `i.p-warn` is `3.6%`
- And `#s2 .proglab` reads "Closing progress 4.8% — Confirm Closing becomes available after resolving 3 warnings"

**QA-COUNT-11 `[ADMIN]`** — the percentage formulas reproduce the wireframe's own numbers
- Given target 84 with OK 3 and outstanding warnings 2
- Then `progress_ok_pct` renders `3.6%` and `progress_warn_pct` renders `2.4%`
- And with OK 4 / warnings 3 they render `4.8%` and `3.6%`, matching States 2 and 3 exactly

**QA-COUNT-12 `[ADMIN]` (negative)** — deleting every row empties the counters without ending the session `[E-68]`
- Given a session with target 40 and 12 rows
- When all 12 rows are deleted
- Then OK is 0, outstanding warnings is 0, Remaining is 40, Confirm is disabled with "Confirm Closing (40 remaining)", and the session is still `IN_PROGRESS`

**QA-COUNT-13 `[ADMIN]`** — the scan list stays usable at several hundred rows `[E-60]` `[DQ-9]`
- Given an `IN_PROGRESS` session that has accumulated **400** scan rows
- When the 401st parcel is scanned
- Then the new row is appended at the **bottom**, is visible without a manual scroll, and `document.activeElement` is still the scan input (the append never steals focus)
- And the tiles, the progress bar and the Confirm label update within the same render, with no page refresh
- And if the implementation paginates, the **latest** page is the one displayed during an active session; if it virtualizes, every row remains addressable by its sequence number for the CSV export and for `#{n}` duplicate cross-references

---

### 8.8 QA-TARGET — Target edit & cancel `[L-S1-10]`

**QA-TARGET-01 `[WF]`** — the locked banner shows the target and the starter
- Given `section#s1` is active
- Then `#s1 .clsbanner.info` contains a `b` element reading "① Today's Outbound Target (manual count)" and the text "Closing in progress (started 18:02 · Dean)"
- And `#targetIn1` has value `84` and the attribute `disabled`
- And the buttons `#targetEdit` ("↺ Edit count") and `#closeCancel` ("✕ Cancel Closing") exist

**QA-TARGET-02 `[WF]`** — Edit count unlocks the field *(destructive — reload after)*
- When `#targetEdit` is clicked
- Then `#targetIn1` no longer has `disabled`, is `document.activeElement`, has its value selected, and `#targetEdit` text becomes "Save"

**QA-TARGET-03 `[WF]`** — Save re-locks the field
- Given the field is unlocked
- When `#targetEdit` (now "Save") is clicked
- Then `#targetIn1` is `disabled` again and the button text returns to "↺ Edit count"

**QA-TARGET-04 `[WF]` (negative)** — Cancel Closing takes the confirm dialog (`[WF-7]` fixed 2026-08-03) *(destructive — reload after)*
- Given `section#s1` is active
- When `#closeCancel` is clicked
- Then `#m-cancel` gains class `open` and `section#s1` **keeps** class `on` — nothing cancels yet
- And the modal `header` R2-normalized text **starts with** "Cancel today's closing?" (R2b — the `✕` close button is nested), its body `b` reads "5 scans will be removed from this session.", and its footer buttons read "Keep scanning" and "Yes — cancel closing"
- When "Keep scanning" is clicked
- Then `#m-cancel` loses class `open` and `section#s1` still has class `on` — a true no-op
- When `#closeCancel` is clicked again and "Yes — cancel closing" (`#cancelYes`) is clicked
- Then `#m-cancel` closes and `section#s0` becomes active
- And the server-side semantics (toast, DC-5, retained rows) remain `[ADMIN]` (QA-TARGET-05/08)

**QA-TARGET-05 `[ADMIN]`** — Cancel Closing requires confirmation `[E-20]` `[PD-5]`
- When "✕ Cancel Closing" is pressed with 37 scans present
- Then a dialog titled "Cancel today's closing?" appears stating "37 scans will be removed from this session…" with buttons "Keep scanning" and "Yes — cancel closing"
- When "Keep scanning" is pressed, nothing changes and no event is written
- When "Yes — cancel closing" is pressed, the screen returns to the pre-start state and a green toast reads "✓ Closing cancelled — 37 scans discarded" / "Scan records are kept in the audit log"

**QA-TARGET-06 `[ADMIN]` (negative)** — an invalid new target is rejected `[E-19]`
- When Save is pressed with `0`
- Then the previous target is preserved, the field stays in edit mode, a red toast reads "✕ The count must be a whole number of 1 or more", and a `closing.target_edit_rejected` event (**DC-4**) exists

**QA-TARGET-07 `[ADMIN]`** — the edit captures the old value and the context
- When the target is changed 84 → 86
- Then a `closing.target_edited` event (**DC-3**) exists with `old_qty=84`, `new_qty=86`, `ok_count_at_edit` and `outstanding_warnings_at_edit`
- And a green toast reads "✓ Target updated — 84 → 86 orders"
- And the UI shows only the new value, while the old value remains queryable from the event

**QA-TARGET-08 `[ADMIN]`** — cancelling retains the scan rows `[E-20]`
- When a session with 37 rows is cancelled
- Then a `closing.session_cancelled` event (**DC-5**) exists with `scan_row_count_discarded=37` and `retained_row_ids` of length 37
- And those 37 scan records are still queryable server-side afterwards
- And starting again the same day writes `closing.session_restarted` (**DC-6**) linking to the cancelled session

**QA-TARGET-09 `[ADMIN]` (negative)** — editing below the OK count creates a mismatch `[E-17]`
- Given OK 10, target 10, Confirm enabled
- When the target is edited to 8
- Then Confirm becomes disabled with the label "Confirm Closing (2 over target)" and no scan row is modified

**QA-TARGET-10 `[ADMIN]`** — editing to exactly the OK count opens the gate `[E-18]`
- Given OK 83, target 84, 0 outstanding warnings, Confirm disabled
- When the target is edited to 83
- Then Confirm becomes enabled with no new scan, and **DC-3** records `ok_count_at_edit=83`

**QA-TARGET-11 `[ADMIN]` (negative)** — cancel with zero scans still asks `[E-21]`
- Given a session with no scans
- When "✕ Cancel Closing" is pressed
- Then the confirm dialog still appears, with the scan-count clause omitted
- And dismissing it leaves the session `IN_PROGRESS`

**QA-TARGET-12 `[WF]` (negative)** — the warning states render a muted target line, not the banner (documents U-j)
- Given `section#s2` is active
- Then `#s2 .clsbanner.info` does not exist; instead a `p.mut` reads "① Today's outbound target (manual count): 84 orders — closing started 18:02 (Dean)"
- And `#s2` contains no `#targetEdit` and no `#closeCancel`
- And the same holds for `#s2b` and `#s3`

**QA-TARGET-13 `[ADMIN]`** — the banner is present in every in-progress rendering `[BR-14]`
- Given an `IN_PROGRESS` session showing a Processing warning, an unknown warning, or a duplicate warning
- Then the full target banner with "↺ Edit count" and "✕ Cancel Closing" is rendered in every one of those views, identical to the OK-scan view

**QA-TARGET-14 `[ADMIN]`** — a scan that lands while the target edit is open is processed normally `[E-51]`
- Given target 84 and OK 40, and "↺ Edit count" has been pressed so `#targetIn1` is unlocked, focused and holds the unsaved value `86`
- When a parcel is scanned from the wedge
- Then the scan is submitted and judged normally — the edit field never blocks the loop — a row is appended and one **DC-7** exists
- And **no scanned character lands in the target field**: its value is still exactly `86` after the burst (`[L-S1-F]` clause 2 exclusion, also covered by QA-SCAN-12)
- And the counters recompute against the **saved** target `84` (OK 41, Remaining 43), not against the unsaved `86`
- When "Save" is then pressed, the counters recompute against `86` (Remaining 45) and **DC-3** records `old_qty=84 → new_qty=86` with `ok_count_at_edit=41`

---

### 8.9 QA-M1 — Process Processing Order `[L-M1]`

**QA-M1-01 `[WF]`** — the modal opens from the warning row
- Given `section#s2` is active
- When the button "Process this order" inside row `#4`'s Notes cell is clicked
- Then `#m-process` gains class `open`
- And the same button exists inside `#s1` row `#4` and opens the same modal

**QA-M1-02 `[WF]`** — the modal content is byte-exact
- Given `#m-process` is open
- Then its `header` R2-normalized text starts with "Process Processing Order — Order 413511"
- And the body contains a `b` element reading "This order has not been outbound-processed yet." and the line "Tracking YT2618100710223471 · 1 item · Status Processing"
- And a checkbox `input[type=checkbox]` is present whose label contains "Packing status of this order verified at Zero Packing" and "(step 6 of the current closing process)"
- And a `textarea.mtextarea` exists with placeholder "Packing status and actions taken — if written, it is also recorded to the order's Comments history and the closing log"
- And the `.note` contains "changes the real order status Processing → Prepare Shipment" and "If packing is incomplete, handle it separately and rescan."

**QA-M1-03 `[WF]`** — the footer buttons
- Then `#m-process .foot` contains a button labelled "Close" and a `button.btn-green` labelled "Process Outbound → resolve warning"

**QA-M1-04 `[WF]` (negative)** — dismissal changes nothing
- Given `#m-process` is open
- When "Close" is clicked (repeat the scenario with the header `✕`, and with a click on the `#m-process` overlay itself)
- Then `#m-process` loses class `open` and the underlying row `#4` still shows `span.cs-processing` "⚠ Not outbounded" with the "Process this order" button intact
- And the checkbox and textarea contents are irrelevant to the outcome — nothing is submitted

**QA-M1-05 `[ADMIN]` (negative)** — the Zero Packing checkbox gates the action `[E-22]` `[PD-77]`
- Given M1 is open with the checkbox unticked
- Then "Process Outbound → resolve warning" is `disabled` and cannot be activated by keyboard (Enter/Space on the focused control does nothing)
- When the checkbox is ticked, the button becomes enabled

**QA-M1-06 `[ADMIN]`** — a successful resolution writes the canonical events `[E-23]`
- When "Process Outbound → resolve warning" is confirmed for order 413511
- Then an `order.status_changed` event (**DC-13**) exists with `old_status=processing`, `new_status=prepare-shipment`, `zero_packing_verified=true`, `source=closing_m1`
- And an `order.outbounded` event (**DC-14**) exists with the **same** `correlation_id`
- And a `closing.warning_resolved` event (**DC-11**) exists with `method=m1_outbound`
- And a green toast reads "✓ Order 413511 outbounded — warning resolved" / "Status changed Processing → Prepare Shipment"

**QA-M1-07 `[ADMIN]`** — the row is re-judged in place
- Then the scan row keeps sequence number `#4` and its original scan time, its class changes from `row-bad` to `row-ok`, its verdict pill becomes "✓ Outbounded", its Order Status pill becomes "Prepare Shipment", and the Notes button disappears
- And no page refresh occurs

**QA-M1-08 `[ADMIN]`** — memo routing
- When the memo contains "@Yongwon checked at Zero Packing"
- Then a `comment.posted` event (**DC-15**) exists on order 413511 with `source=closing_m1` and `mentions=[Yongwon]`, written to both the order's Comments history and the closing log
- And a `comment.mention_notified` event (**DC-17**) exists targeting `#fulfillment-admin-comments` (`C0BMGEWM5QA`) carrying entity no., text, time, author, mentioned user and a deep link to the order
- When the memo is left empty, a `comment.auto_posted` event (**DC-16**) with `source=system` exists instead, naming the transition and the closing date

**QA-M1-09 `[ADMIN]` (negative)** — double-click safety `[E-25]` `[G-9]`
- When "Process Outbound → resolve warning" is clicked twice rapidly
- Then exactly one **DC-13**, one **DC-14**, one **DC-11** and one comment exist

**QA-M1-10 `[ADMIN]` (negative)** — stale order handling `[E-24]` `[E-56]`
- Given the order was moved to `Prepare Shipment` from View Orders while the modal was open
- Then no second transition occurs, the call succeeds idempotently, the row re-judges green, and the toast reads "✓ Order 413511 was already outbounded — warning resolved"
- Given instead the order was **cancelled** while the modal was open (the cancellation flag, not a status — §3.6) `[E-56]`
- Then the call is rejected, a red toast reads "✕ Order 413511 is cancelled — cannot outbound from closing", the row re-judges to `⚠ Not outbounded` showing the underlying status label plus the `Cancelled` marker, and no **DC-13**/**DC-14** is written
- Given instead the order moved to any other status (`on-hold`, `refunded`, `failed`, …)
- Then the call is rejected with "✕ Order 413511 is now {status} — cannot outbound from closing" and nothing is written except the rejection record

**QA-M1-11 `[WF]` (negative)** — the wireframe does not gate the button on the checkbox (documents the gap)
- Given `#m-process` is open with the checkbox unticked
- Then the button "Process Outbound → resolve warning" is **not** `disabled` in the demo — it merely carries `data-close`
- When it is clicked, the modal closes and the underlying row is unchanged (the demo performs no transition)
- And the shipping gate is asserted in QA-M1-05

**QA-M1-12 `[ADMIN]`** — the transition propagates across pages
- After a successful M1 resolution for order 413511
- Then View Orders no longer lists it in the `Processing` working set, Order Detail shows `Prepare Shipment` plus the closing-sourced comment, Order Management's status counts update, and Ready to be Outbounded recomputes its eligibility — all without a manual refresh on those screens

**QA-M1-13 `[ADMIN]` (negative)** — the send sound is distinct from the warning voice `[PD-2]`
- When the M1 action succeeds
- Then exactly one `[G-3a]` send sound plays and no TTS utterance is spoken
- And the sound is a synthesized rising sweep, measurably distinct from the warning voice, so an operator with eyes on a parcel cannot mistake a success for a warning

**QA-M1-14 `[ADMIN]` (negative)** — M1 cannot outbound an order with un-inbounded lines `[E-78]` `[BR-38]`
- Given order 413712 has status `processing` and 3 lines, of which **1 is still `PENDING`**, and its parcel has been scanned so the row shows `⚠ Not outbounded` with the `[Process this order]` button
- When M1 is opened and the Zero Packing checkbox is ticked
- Then "Process Outbound → resolve warning" is still `disabled`, and the modal shows the reason "Cannot outbound — 1 of 3 items are not inbounded yet. Receive them on Order Detail first."
- And a forced request is rejected server-side: no **DC-13**, no **DC-14**, no **DC-11**, no comment, and the scan row stays `⚠ Not outbounded` as an outstanding warning
- When the missing line is received on Order Detail and the parcel is rescanned
- Then the new scan is judged against the live status exactly as any other scan (this page performs no retro-judgment of the earlier row — `[BR-22]`)
- And this is the same predicate View Orders `BR-9` and `order-detail.md` L-9 enforce; closing opens no side door through it

---

### 8.10 QA-DEL — Delete Scan Row `[L-M2]` `[L-S1-6]`

**QA-DEL-01 `[WF]`** — the modal identifies the row it will remove
- Given `section#s1` is active with rows `#1`–`#5`
- When the `✕` (`button.scandel`, title "Delete scan row") on row `#3` is clicked
- Then `#m-scandel` gains class `open`, its `header` R2-normalized text **starts with** "Delete Scan Row" (the header's `✕` close button is nested inside it — R2b; same shape as QA-M1-02), its body `b` reads "Remove this scan?", and `#scandelInfo` reads exactly "#3 · YT2618100710184356"

**QA-DEL-02 `[WF]` (negative)** — "No" is a true no-op
- Given `#m-scandel` is open for row `#3`
- When the button "No" is clicked
- Then `#m-scandel` loses class `open` and `#s1 table.tbl tbody tr` still yields 5 rows including `#3`

**QA-DEL-03 `[WF]`** — "Yes — remove" removes the row and preserves numbering *(destructive — reload after)*
- Given `#m-scandel` is open for row `#3`
- When `#scandelYes` (label "Yes — remove") is clicked
- Then the overlay closes, row `#3` is removed from the DOM, `#s1 table.tbl tbody tr` yields 4 rows, and their first cells still read `#1`, `#2`, `#4`, `#5` — **no renumbering** `[BR-17]`

**QA-DEL-04 `[WF]`** — the retention promise is stated in the modal
- Then `#m-scandel .note` reads "Deleting excludes it from the list and the closing counts — for clearing mis-scans, unknown orders, etc. Deletion history is kept in the backend."

**QA-DEL-05 `[WF]` (negative)** — the wireframe does not recompute tiles (known demo limitation) *(destructive — reload after)*
- Given `#s1` tiles read `84 / 3 / 2 / 79`
- When row `#3` (a duplicate warning) is removed via `#scandelYes`
- Then the tiles are **unchanged** and `.prog i.p-warn` still has width `2.4%`
- And the shipping behavior is asserted separately in QA-DEL-08 and QA-COUNT-05

**QA-DEL-06 `[ADMIN]`** — deletion is a soft delete with a full snapshot
- When a row is removed
- Then a `closing.scan_row_deleted` event (**DC-12**) exists carrying the sequence number, the complete original scan payload, the deleting actor, the server timestamp and `was_outstanding_warning`
- And the row still appears in the day's CSV export with a deleted flag

**QA-DEL-07 `[ADMIN]` (negative)** — repeat deletion is idempotent `[E-29]` `[E-58]`
- When "Yes — remove" is clicked twice on the same row, or two operators delete it concurrently
- Then exactly one **DC-12** exists, no error is surfaced, and both operators' lists converge on the same state

**QA-DEL-08 `[ADMIN]`** — deleting a warning row resolves it and may open the gate `[E-28]`
- Given `ok_count == target` and one outstanding duplicate warning
- When that warning row is deleted
- Then **DC-11** exists with `method=row_deleted`, outstanding warnings becomes 0, Confirm becomes enabled, and the raised counter is unchanged
- And a green toast reads "✓ Scan #{seq} removed" / "Deletion history is kept in the backend"

**QA-DEL-09 `[ADMIN]` (negative)** — deleting an OK row breaks an exact match `[E-27]`
- Given target 84, OK 84, 0 warnings, Confirm enabled
- When one OK row is deleted
- Then Confirm becomes disabled with the label "Confirm Closing (1 remaining)" immediately, with no page refresh

**QA-DEL-10 `[WF]`** — the modal is also reachable from the wf-bar tab
- When `.wf-tab[data-modal="m-scandel"]` is clicked
- Then `#m-scandel` gains class `open` and `#scandelInfo` retains its default text "#7 · YT2618100719984412"
- And this entry point is review chrome only `[L-F4]`; the shipping entry point is the per-row `✕`

---

### 8.11 QA-CONFIRM — Confirm Closing & State 4 `[L-S1-8]` `[L-S4-1]` `[L-S4-2]` `[L-S4-3]`

**QA-CONFIRM-01 `[WF]`** — the disabled button carries the blockers
- Given `section#s1` is active
- Then `#s1 .clsbanner.done` contains a `b` element reading "Confirm Closing" and a button whose R2-normalized text is exactly "Confirm Closing (79 remaining · 2 warnings)"
- And the banner text contains "no auto-confirm; closing happens only when this button is pressed." and "an over-scan makes it a mismatch and disables the button again" and "the admin's Closing History replaces the retired Daily Shipping Status spreadsheet" (`[PD-71]` copy, 2026-08-03)

**QA-CONFIRM-02 `[WF]`** — the button renders as disabled
- Then that button carries class `btn-gray` (the wireframe's disabled treatment, `cursor:not-allowed`)

**QA-CONFIRM-03 `[WF]`** — the completion panel is the only large panel on the page
- Given `section#s4` is active
- Then `#s4 .bigstatus` has class `bs-ok`, its `.big` text reads "Today's closing complete — all orders verified", and its `.bmeta` contains "Manual count 84 = OK scans 84, an exact match · 0 warnings · closing confirmed 2026-07-13 18:52 (Yongwon)"
- And `#s4 .bside` contains "Warnings", the value "0" and "Remaining scans 0"
- And `document.querySelectorAll('.bs-warn')` yields **zero** elements anywhere in the document `[WF-5]`
- And `document.querySelectorAll('.bigstatus')` yields exactly one element, inside `#s4`

**QA-CONFIRM-04 `[WF]`** — the confirmation toast copy
- Given `section#s4` is active
- Then `#s4 .toast` contains "✓ Today's closing confirmed — 84/84 orders" and its `small` reads "Closing record saved · replaces the retired Daily Shipping Status sheet"
- And `#s4 .toast` does not carry class `err`

**QA-CONFIRM-05 `[WF]`** — the Closing Report banner, and no print affordance `[BR-24]`
- Then `#s4 .clsbanner.done` contains a `b` element reading "Closing Report", the text "replaces the manual copy/paste and formula-stripping into SS Daily Shipping Status (sheet retired 2026-08-03)", and a button labelled "Download Closing Report (CSV)"
- And no element anywhere in the document has text containing "Print" and no `button` exists whose normalized text is "Print"

**QA-CONFIRM-06 `[WF]`** — the Warning Resolution Summary and the State 4 tiles
- Then `#s4 .clsbanner.info` contains a `b` element reading "Warning Resolution Summary" and the text "3 warnings today — 1 Processing (413511, resolved after Outbound) · 2 duplicates (combined-box confirmed, logged in Comments)."
- And the four `#s4 .tile .val` read `84`, `84`, `0`, `0` with the third `.lab` reading "Warnings (resolved)"
- And `#s4 .prog i.p-ok` has width `100%` and no `i.p-warn` element exists in `#s4`

**QA-CONFIRM-07 `[ADMIN]` (negative)** — the gate holds below the target
- Given target 84, OK 83, warnings 0
- Then Confirm is disabled with the label "Confirm Closing (1 remaining)" and a forced request is rejected server-side with **DC-22**

**QA-CONFIRM-08 `[ADMIN]` (negative)** — the gate holds with an outstanding warning
- Given target 84, OK 84, outstanding warnings 1
- Then Confirm is disabled with the label "Confirm Closing (1 warnings)" and a forced request is rejected with **DC-22**

**QA-CONFIRM-09 `[ADMIN]` (negative)** — the gate holds above the target `[BR-3]`
- Given target 84, OK 85, warnings 0
- Then Confirm is disabled with the label "Confirm Closing (1 over target)"

**QA-CONFIRM-10 `[ADMIN]`** — a successful confirmation writes the record chain
- Given target 84, OK 84, outstanding warnings 0
- When Confirm is pressed once
- Then `closing.confirmed` (**DC-21**) exists with the confirmer, `target=84`, `ok_count=84`, `warnings_raised`, `warnings_resolved`, `match=true` and a `snapshot_id`
- And `closing.snapshot_created` (**DC-23**) exists containing the full scan list including deleted rows
- And **no** `closing.daily_shipping_status_updated` (**DC-24**) event exists — the sheet integration is retired (`[PD-71]`, §6.4)
- And the green toast reads "✓ Today's closing confirmed — 84/84 orders" / "Closing record saved · replaces the retired Daily Shipping Status sheet"
- And a History row for today appears with `84 · 84 · {raised}→{resolved} · ✓ Match`
- And the screen re-renders as State 4 with no page reload

**QA-CONFIRM-11 `[ADMIN]` (negative)** — server revalidation catches stale state `[BR-29]` `[PD-6]`
- Given order 413540 was scanned OK, then moved to `on-hold` (or cancelled — §3.6) by another screen before Confirm was pressed
- When Confirm is pressed
- Then the confirmation is rejected, nothing is written except `closing.confirm_rejected` (**DC-22**) with `offending_order_ids=[413540]`, a red toast reads "✕ Cannot confirm — order 413540 is no longer Prepare Shipment", and the affected row is re-judged in place
- And the session remains `IN_PROGRESS` with no partial snapshot

**QA-CONFIRM-12 `[ADMIN]` (negative)** — the session locks after confirmation `[E-10]` `[PD-73]`
- Given today's session is `CONFIRMED`
- Then the scan input is `disabled`, and "↺ Edit count" / "✕ Cancel Closing" are absent from the DOM
- When a wedge scan reaches the server anyway
- Then it is rejected with `closing.scan_rejected` (**DC-8**, `reason=session_confirmed`) and a red toast reads "✕ Today's closing is confirmed — scanning is closed"

**QA-CONFIRM-13 `[ADMIN]` (negative)** — a target edited mid-flight cannot be confirmed against `[E-73]`
- Given operator A presses Confirm at target 84 while operator B saves target 86 in the same moment
- Then the server compares `target_at_press=84` with the live target 86, rejects the confirmation, writes **DC-22** carrying both values, and leaves the session `IN_PROGRESS`

**QA-CONFIRM-14 `[ADMIN]`** — the CSV export and its failure mode `[E-40]`
- When "Download Closing Report (CSV)" is pressed
- Then a file downloads immediately with no dialog, a `closing.report_exported` event (**DC-25**) exists with `source=state4_button` and `includes_deleted=true`, and the file contains the full scan list including deleted rows plus the header block (date, target, OK, raised→resolved, closed by, confirmed at)
- When generation fails, a red toast reads "✕ Closing report could not be generated — try again" and no empty file is delivered
- And a zero-scan day yields a well-formed file with headers and no data rows

**QA-CONFIRM-16 `[ADMIN]` (negative)** — a retried Confirm cannot double-write `[E-37]` `[G-9]`
- Given target 84, OK 84, 0 outstanding warnings, and a `closing.confirm` request whose **response is lost** after the server committed it (network drop, not a server error)
- When the client retries with the **same idempotency key**
- Then exactly **one** `closing.confirmed` (**DC-21**) and exactly **one** `closing.snapshot_created` (**DC-23**) exist for that date, and **zero** `closing.daily_shipping_status_updated` (**DC-24**) events — the sheet is retired (`[PD-71]`)
- And the retry returns the **confirmed state** — State 4, not an error dialog and not a second confirmation toast
- And Closing History shows exactly one row for the date
- Given instead the first attempt never reached the server, when the retry is sent with the same key, then exactly one of each event is written and the outcome is identical — the caller cannot tell the two cases apart

**QA-CONFIRM-15 `[WF]` (negative)** — State 4 exposes no session controls
- Given `section#s4` is active
- Then `#s4` contains no `#targetEdit`, no `#closeCancel`, no `.clsbanner.info` with "Today's Outbound Target (manual count)" as a `b`, and no button whose text starts with "Confirm Closing"
- And instead a `p.mut` reads "① Today's outbound target (manual count): 84 orders — closing started 18:02 (Dean)"

---

### 8.12 QA-HIST — Closing History `[L-SH-1]` `[L-S1-11]`

**QA-HIST-01 `[WF]`** — the history page is reachable from the closing screen
- Given `section#s1` is active
- When the in-page tab `#s1 [data-goto="shist"]` labelled "Closing History" is clicked
- Then `section#shist` has class `on` and `section#s1` does not
- And the same tab exists in `#s0`, `#s2`, `#s2b`, `#s3` and `#s4`

**QA-HIST-02 `[WF]`** — the table contract
- Given `section#shist` is active
- Then the header cells of `#shist table.logtbl` read, in order: `Date`, `Outbound Target (manual)`, `OK Scans`, `Warnings (raised→resolved)`, `Match`, `Closed By`, `Confirmed At`, `` (empty action cell)

**QA-HIST-03 `[WF]`** — today's row and the CSV action
- Then the first data row reads `07-13 (today)` · `84` · `84` · `3→3` · `✓ Match` · `Yongwon` · `18:52` and contains a button labelled "CSV"
- And that row carries the today-highlight: its inline `style` attribute is exactly `background:var(--green-soft)`, and its computed `background-color` differs from every other data row's in the same table (the other four carry no inline background)

**QA-HIST-04 `[WF]`** — the invariant is stated on screen
- Then the paragraph below the table reads "Closing cannot be confirmed while mismatched, so records are always saved as "Match" — mismatch causes (missed scans · over-scans · unresolved warnings) must be resolved before confirmation."
- And the intro paragraph above the table reads "Daily snapshots saved automatically on closing confirmation — an audit trail of outbound target (manual count) · OK scans · warning resolution · confirmer"

**QA-HIST-05 `[WF]`** — the Closing tab returns to the previous view
- Given a freshly loaded page; when `.wf-tab[data-state="s2"]` is clicked, then `#s2 [data-goto="shist"]` is clicked
- Then `section#shist` is active and the wireframe's `lastState` is `s2`
- When `#shist [data-goto="back"]` (labelled "Closing") is clicked
- Then `section#s2` becomes active again

**QA-HIST-06 `[ADMIN]` (negative)** — cancelled sessions and blank days never appear `[E-43]` `[E-45]`
- Given a date with a cancelled session and no confirmation
- Then that date has **no** History row, and no fabricated row exists for any date without a confirmed closing
- And the cancelled session's rows remain queryable server-side

**QA-HIST-07 `[ADMIN]`** — the per-row CSV reproduces the snapshot
- When a History row's "CSV" button is pressed
- Then a `closing.report_exported` event (**DC-25**) exists with `source=history_row_csv` and the row's date
- And the file contains the full scan list including deleted rows, and is byte-identical to the file downloaded from State 4 on that day

**QA-HIST-08 `[ADMIN]` (negative)** — first-use empty state `[E-44]`
- Given no closing has ever been confirmed
- Then the history page shows "No closing records yet — the first confirmed closing will appear here." and renders no CSV buttons

**QA-HIST-09 `[ADMIN]` (negative)** — exactly one row per date `[PD-70]`
- Given a date with one cancelled session followed by one confirmed session
- Then History shows exactly one row for that date, carrying the confirmed session's numbers, and no row for the cancelled one

**QA-HIST-10 `[WF]`** — every demo row is a Match
- Given `section#shist` is active
- Then the table has 5 data rows whose Date cells **start with** `07-13 (today)`, `07-12`, `07-11`, `07-10`, `07-09` (the 07-12 Date cell also carries the Amended badge — QA-AMEND-06)
- And every row's Match cell reads "✓ Match", every row's OK Scans equals its Outbound Target, and every row carries a "CSV" button and an "Amend" button (QA-AMEND-01)

**QA-HIST-11 `[ADMIN]`** — an Order ID deep link opens a new tab and the session survives `[E-74]` `[G-12]` `[DQ-11]`
- Given an `IN_PROGRESS` session with 40 rows and focus in the scan input
- Then each scan-list `Order ID` cell is a real anchor (`<a href>`), not styled text — its `href` is the directory form `../order-detail/#{order_id}` (never `../order-detail/index.html#…`)
- When the `Order ID` of row `#12` is clicked
- Then the order opens in a **new browsing context** and the closing tab is **not** navigated: its `document` is the same one (a `window`-scoped marker set before the click still exists), all 40 rows and their sequence numbers are unchanged, the counters and the gate are unchanged, and focus is still in the scan input
- When a parcel is scanned immediately after
- Then it is judged normally and appended as row `#41` — the scan loop was never interrupted
- And clicking the link writes **no** event (§5.3 NON-event)

---

### 8.13 QA-HUB — Comments hub `[L-S1-7]` `[G-7]`

**QA-HUB-01 `[WF]`** — the hub opens with an unread badge
- Given `section#s1` is active
- Then the nav button `#s1 [data-open="inbox1"]` R2-normalized text **starts with** "💬 Comments" (the badge asserted in the next clause is nested *inside* the button, so its full normalized text is "💬 Comments2" — R2b) and it carries `.badge-n` whose text reads "2"
- When it is clicked, `#inbox1` gains class `open`, its Mentions pane header (`#inbox1 [data-pane="mentions"] .paneheader`) R2-normalized text **starts with** "Comments mentioning me · Click to open the order" (the `<small>Mark all read</small>` action is nested inside it — R2b), and it lists three entries whose bold entity labels are "Order 413540", "Order 413498" and "Order 413330"
- And the first two entries carry class `unread`
- And these two pane strings are the canonical `[G-7]` HUB-1 / HUB-4 strings since the 2026-08-03 `[WF-15]` fix; QA-HUB-09 asserts the same values at `[ADMIN]` tier

**QA-HUB-02 `[WF]`** — tab switching
- Given `#inbox1` is open
- When the tab `[data-tab="saved"]` ("★ Saved") is clicked
- Then it gains class `on`, the pane `[data-pane="saved"]` becomes visible and its `.paneheader` R2-normalized text **starts with** "Saved comments · Click to open the order" (the `<small>Unstar to remove from the list</small>` action is nested inside it — R2b), and `[data-pane="mentions"]` is hidden
- And the Saved pane lists exactly one entry, "Order 413498"

**QA-HUB-03 `[WF]`** — the star toggle *(destructive — reload after)*
- Given the Mentions pane is visible
- When the `.star` button on the "Order 413540" entry is clicked
- Then it gains class `on`; clicking it again removes the class
- And the "Order 413498" entry's star already carries class `on` on load

**QA-HUB-04 `[ADMIN]`** — full-text comment search (wireframe gap U-c)
- Given the hub is open
- When "combined-box" is typed into the comment search
- Then matching comments across **all** entities are listed newest first, regardless of mention or saved state
- And clicking a result opens the order it belongs to

**QA-HUB-05 `[ADMIN]`** — mark all read
- When "Mark all read" is pressed
- Then `comment.read` / `comment.mark_all_read` events (**DC-19**) exist for the affected comment ids, the badge clears, and pressing it again is a no-op with no further event

**QA-HUB-06 `[ADMIN]`** — starring persists and mentions route to Slack
- When a comment is starred
- Then `comment.starred` (**DC-18**) exists with the old → new state and the entry appears in the Saved pane
- And unstarring from the Saved pane writes `comment.unstarred` and removes it from that pane while leaving it in Mentions
- And any comment posted from closing containing an `@mention` produces `comment.mention_notified` (**DC-17**) to `#fulfillment-admin-comments` (`C0BMGEWM5QA`) carrying entity no., text, time, author, mentioned user and a deep link

**QA-HUB-07 `[WF]` (negative)** — only State 1 wires the dropdown (documents U-e)
- Given `section#s2` is active
- Then its "💬 Comments" button carries no `data-open` attribute and no `#inbox` dropdown exists inside `#s2`
- And the same holds for `#s0`, `#s2b`, `#s3`, `#s4` and `#shist`
- And the shipping behavior is an identical hub on every state

**QA-HUB-08 `[ADMIN]` (negative)** — an open hub never breaks the scan loop `[E-75]`
- Given the Comments hub dropdown is open and focus is not in one of its fields
- When a parcel is scanned
- Then the verdict renders, the row appends and the toast shows, the hub stays open, and the scanned characters land in the scan input — not in the hub
- When focus **is** in the hub's search field, the wedge input goes to that field and no scan is submitted (`[L-S1-F]` clause 2)

**QA-HUB-09 `[ADMIN]`** — the hub carries the canonical cross-page copy `[G-7]` HUB-1…HUB-6 `[WF-15]`
- Given the Comments hub is open on the shipping closing page
- Then the Mentions pane header reads exactly "Comments mentioning me · Click to open the order"
- And the Saved pane header reads exactly "Saved comments · Click to open the order"
- And the unstar hint reads exactly "Unstar to remove from the list" and the read-all action reads exactly "Mark all read"
- And a search returning results renders the header "{n} results · newest first · click to open the order", while a search with no match renders exactly "No matching comments"
- And none of the pre-2026-08-03 wireframe strings ("Comments where I'm tagged", "Comments I saved", "Unstar to remove from this list") appears anywhere in the rendered hub — they were removed from the drawing by the `[WF-15]` fix, so this negative now also holds at `[WF]` tier

---

### 8.14 QA-PERSIST — Persistence, concurrency, integrations (all `[ADMIN]`)

**QA-PERSIST-01 `[ADMIN]`** — refresh restores everything `[E-36]` `[BR-8]`
- Given an in-progress session with target 84, 37 rows (3 warnings) and Confirm disabled
- When the browser is refreshed, or the page is navigated away from and back, or the tab is closed and reopened
- Then the target, all 37 rows with their original sequence numbers and scan times, the counters, the warnings and the gate state are identical to before

**QA-PERSIST-02 `[ADMIN]`** — scans persist at scan time, not at confirm `[BR-27]`
- Given 10 scans have been made and the session has **not** been confirmed
- Then 10 `closing.scan_recorded` events (**DC-7**) already exist server-side
- And killing the browser process at this point loses none of them

**QA-PERSIST-03 `[ADMIN]` (negative)** — same tracking from two stations `[E-30]`
- When stations A and B submit the same tracking number within the same second
- Then exactly one row has `verdict=ok` and exactly one has `verdict=duplicate`, the duplicate references the OK row's sequence number, and both stations render the identical two rows in the identical order

**QA-PERSIST-04 `[ADMIN]` (negative)** — simultaneous confirms `[E-31]`
- When two operators press Confirm at the same instant
- Then exactly one **DC-21** and one **DC-23** exist (and zero **DC-24** — the sheet is retired, `[PD-71]`); the second operator is shown the confirmed state, not an error dialog

**QA-PERSIST-05 `[ADMIN]`** — target edit during scanning `[E-32]`
- When A edits the target while B is scanning
- Then the gate is recomputed once against one consistent server state, B's in-flight scan lands normally, and no update is lost

**QA-PERSIST-06 `[ADMIN]`** — one session on two devices `[E-33]`
- When the same session is open on two devices
- Then both show identical sequence numbers, rows and counters within the agreed sync latency, and neither device can assign a sequence number the other has used

**QA-PERSIST-07 `[ADMIN]` (negative)** — cancel during a colleague's scan `[E-34]`
- Given A cancels the session while B is mid-loop
- When B's next scan is submitted
- Then it is rejected with `closing.scan_rejected` (**DC-8**, `reason=session_cancelled`), a red toast reads "✕ This closing was cancelled by {actor} — start a new closing", and **no** new session is silently created

**QA-PERSIST-08 `[ADMIN]` (negative)** — no sheet write ever occurs `[E-38]` `[PD-71]` (rewritten 2026-08-03; the sheet-failure scenario is retired with the sheet)
- Given a closing is confirmed, and later amended and re-confirmed (§3.24)
- Then **zero** `closing.daily_shipping_status_updated` (**DC-24**) events exist for the date, and no outbound request to any external sheet/BI target was made by either action
- And the History row plus the per-day CSV are the only outputs — the session stays `CONFIRMED`, the CSV is downloadable
- And the retired failure copy ("✕ Daily Shipping Status not updated", the error strip, a re-trigger control) appears nowhere in the admin

**QA-PERSIST-09 `[ADMIN]`** — a session across midnight `[E-41]` `[PD-78]`
- Given a session started 23:50 and confirmed 00:10
- Then the History row's Date is the **start** date, and `Confirmed At` reads `00:10`

**QA-PERSIST-10 `[ADMIN]` (negative)** — one confirmed closing per date `[E-42]` `[PD-70]`
- Given today is confirmed
- When a new closing is started for the same date
- Then it is blocked with a red toast and **DC-2** (`reason=already_confirmed`), and History still shows exactly one row for that date

**QA-PERSIST-11 `[ADMIN]` (negative)** — Slack failure never rolls back `[E-62]` `[PD-4]`
- Given the Slack dispatch for a mention fails
- Then the comment still exists (**DC-15**), the M1 status change still stands (**DC-13**/**DC-14**), and **DC-17** records `delivery_status=failure` with a retry attempt
- And the same holds when the mentioned user no longer exists

**QA-PERSIST-12 `[ADMIN]`** — retention and reproducibility `[§5.4]`
- Given a closing confirmed 30 days ago whose orders have since changed status
- When that day's CSV is downloaded from History
- Then it renders from the snapshot (**DC-23**) and is byte-identical to the file produced on the day, including deleted rows and the statuses as they were at scan time

**QA-PERSIST-13 `[ADMIN]` (negative)** — a stale tab cannot write into a closed session `[E-53]`
- Given a tab left open overnight on yesterday's confirmed State 4
- When any action is attempted in it
- Then the client revalidates, renders the session read-only, and no write reaches yesterday's session; starting today's closing requires the new date's pre-start screen

**QA-PERSIST-14 `[ADMIN]`** — one timezone, server timestamps `[E-59]` `[E-71]` `[BR-36]`
- Given two stations in different browser timezones and a confirmer in a third
- Then every `Scan Time`, the `Confirmed At` value, the History `Date` and the "same calendar day" gate all render identically for all three, using the warehouse's operating timezone
- And every persisted timestamp in §5.1 is the server's, never the client's

---

### 8.15 QA-CHROME — Page furniture & layout `[L-F1]`…`[L-F4]` `[L-S1-9]`

**QA-CHROME-01 `[WF]`** — the global nav is present on every state `[L-F1]`
- For each of `#s0`, `#s1`, `#s2`, `#s2b`, `#s3`, `#s4`, `#shist`
- Then that section contains `.nav` with the brand "SkinSeoul", the four menu labels "Operation AI ▾", "Catalog Management ▾", "OMS Center ▾", "Site Management ▾", a "💬 Comments" button, the user chip "Yongwon Ryu" and a "Logout" button

**QA-CHROME-02 `[WF]`** — the page header and in-page tabs `[L-F2]` `[L-S1-11]`
- For each state
- Then `h2` reads "WMS - Closing" and the **first** `p.sub` — address it as `#sX .pagepad > p.sub:first-of-type` — reads "Barcode-scan verification of today's packed orders". (`#s1`, `#s2`, `#s2b` and `#s3` each contain a **second** `p.sub` — the "Scan list …" caption, a later sibling under the same `.pagepad` — so a bare `p.sub` selector is not unique and must not be used.)
- And a `.pagetabs` strip follows with exactly two buttons labelled "Closing" and "Closing History"; in `#shist` the active one is "Closing History", elsewhere it is "Closing"

**QA-CHROME-03 `[WF]`** — the toast slot shape `[L-F3]`
- Given `section#s1` is active
- Then `#s1 .toast` contains a `span` reading "✓ Outbound confirmed — YT2618100710108810" and a `small` reading "Ready for the next barcode scan"
- And `#s4 .toast` follows the same two-part shape
- And no `.toast.err` element exists on a fresh load (the only demo red toasts are the transient `#s0` validation toasts of the `[WF-8]` fix, QA-S0-02; every other red toast is `[ADMIN]` copy defined in §3)

**QA-CHROME-04 `[WF]` (negative)** — the legend-unit count derives from DOM units, never from tabs (`[WF-12]` fixed 2026-08-03)
- Then `document.querySelectorAll('.wf-tab[data-modal="m-process"]')` yields **1** element (the `[WF-12]` duplicate was removed)
- And the legend-unit count is computed **only** from the DOM units, not from tabs: `document.querySelectorAll('.legend ol > li')` yields **20**, `document.querySelectorAll('#m-process .dot, #m-scandel .dot, #m-amend .dot')` yields **3**, and `document.querySelectorAll('#s1 .legend > p')` yields **1** — total **24**, matching §2.1
- And the same page yields `document.querySelectorAll('.wf-tab').length === 10` and `document.querySelectorAll('.wf-tab[data-modal]').length === 3` — tabs are chrome (`[L-F4]`); never derive a unit count from `.wf-tab` (`#m-cancel` deliberately has no dot and no tab-based proxy, §2.1)

**QA-CHROME-05 `[ADMIN]` (negative)** — no wireframe chrome ships `[L-F4]`
- Given the shipping admin closing page
- Then no `.wf-bar`, `.wf-tab`, `#annoToggle`, `.dot` or `.legend` element exists anywhere in the DOM
- And states are rendered by session state, not by tab selection

**QA-CHROME-06 `[WF]`** — the single-screen layout constraint `[L-S1-9]` `[E-50]`
- Given `section#s1` is active at a viewport of 1440×900
- Then `document.body.scrollWidth <= document.body.clientWidth` (the page body does not scroll horizontally; only `.mockwrap` may)
- And all 10 `thead th` cells are rendered, none is `display:none`, and the longest tracking cell text (`YT2618100710184356`, 18 chars) is fully present in the DOM with no ellipsis character

---

### 8.15b QA-AMEND — Amend Closing `[L-SH-2]` `[L-M3]` (added 2026-08-03; numbered 8.15b so §8.16–§8.18 pointers stay stable)

**QA-AMEND-01 `[WF]`** — every History row carries an Amend button
- Given `section#shist` is active
- Then each of the 5 data rows contains a `button.amendbtn` labelled "Amend" beside its "CSV" button (5 in total), and each carries `data-date` / `data-meta` attributes

**QA-AMEND-02 `[WF]`** — M3 opens with the owner's byte-exact copy
- Given `section#shist` is active
- When the today row's `button.amendbtn[data-date="07-13"]` is clicked
- Then `#m-amend` gains class `open`, its `header` R2-normalized text **starts with** "Amend Closing — 07-13" (R2b — the `✕` close button is nested), and its `.dot` reads "M3"
- And its body `b` reads exactly "Amend the closing for 07-13? The confirmed record stays until you re-confirm."
- And `#amendMeta` reads "Confirmed 84/84 · 18:52 (Yongwon)", and the footer buttons read "Keep the record" and "Amend — open the closing"

**QA-AMEND-03 `[WF]` (negative)** — Keep the record is a true no-op
- Given `#m-amend` is open for `07-13`
- When "Keep the record" is clicked (repeat with the header `✕`, and with a click on the `#m-amend` overlay itself)
- Then `#m-amend` loses class `open`, `section#shist` still has class `on`, `#amendBanner`'s computed `display` is `none`, and the 07-13 row is unchanged

**QA-AMEND-04 `[WF]`** — entering amendment mode *(destructive — reload after)*
- Given `#m-amend` is open for `07-13`
- When "Amend — open the closing" (`#amendYes`) is clicked
- Then `#m-amend` closes and `section#s1` becomes active
- And `#amendBanner` is visible (computed `display: flex`) with `#amendBannerB` reading exactly "AMENDING — 07-13 closing (confirmed 84/84)" and the button "✕ Exit amendment" present
- And `#targetIn1` has value `85` (the demo pre-raises the target by one), the `#s1` scan input is **not** `disabled`, and `#confirmBtn1` reads exactly "Re-confirm Closing (1 remaining)"
- And repeating the flow from the `07-11` row renders "AMENDING — 07-11 closing (confirmed 78/78)" with `#targetIn1` value `79` — the banner and target interpolate per row

**QA-AMEND-05 `[WF]`** — Exit amendment restores the resting demo state *(destructive — reload after)*
- Given amendment mode is active per QA-AMEND-04
- When "✕ Exit amendment" (`#amendExit`) is clicked
- Then `section#shist` becomes active, `#amendBanner`'s computed `display` is `none`, `#targetIn1` is back to `84`, and `#confirmBtn1` reads exactly "Confirm Closing (79 remaining · 2 warnings)" (the QA-CONFIRM-01 resting string)

**QA-AMEND-06 `[WF]`** — the Amended badge demo
- Given `section#shist` is active
- Then exactly one `.amended-badge` exists, inside the `07-12` row's Date cell, reading exactly "Amended v2 · Dean · 07-13 09:12"
- And no other row carries a badge, and the badge does not alter the row's inline background (QA-HIST-03's highlight contract is untouched)

**QA-AMEND-07 `[ADMIN]`** — amend start persists and loads the confirmed list
- Given the closing for a date is `CONFIRMED` (v1, target 84, OK 84) and no other session is open
- When Amend is confirmed through M3
- Then a `closing.amend_started` event (**DC-26**) exists with the `session_id`, `base_version=1`, `base_target=84`, `base_ok_count=84` and the acting user
- And the closing screen renders every confirmed scan row with its **original** sequence number, scan time, verdict, worker and notes; the amber banner reads "AMENDING — {date} closing (confirmed 84/84)"; the target banner, `[↺ Edit count]`, the armed scan input and the "Re-confirm Closing" button are present

**QA-AMEND-08 `[ADMIN]` (negative)** — the confirmed record stays until re-confirm
- Given an amendment is open with a target edit and an extra scan already made
- Then Closing History still shows the v1 numbers (84 · 84) with an "Amendment in progress" marker, and the date's CSV still reproduces the v1 snapshot byte-identically
- And no `closing.amended` event exists yet

**QA-AMEND-09 `[ADMIN]`** — a full amendment writes the owner-contract chain
- Given amendment mode on a v1 = 84/84 day
- When the target is edited 84 → 85 (**DC-3** with `old_qty=84 → new_qty=85`), the found parcel is scanned (**DC-7**, `verdict=ok` — OK 85), and "Re-confirm Closing" is pressed once
- Then a `closing.amended` event (**DC-28**) exists with `old_target=84 → new_target=85`, the added scan's sequence in `added_scan_seqs`, `version=2`, both snapshot ids, the actor and the timestamp
- And a **new** snapshot (**DC-23**, v2) exists while the v1 snapshot is unchanged; **DC-22** does not exist; **no DC-24** exists (the sheet is retired — `[PD-71]`, the History row itself carries the corrected figures)
- And the History row for the date now reads 85 · 85 · `✓ Match` — still **exactly one row** — with the badge "Amended v2 · {actor} · {timestamp}"
- And a green toast reads "✓ Closing amended — 85/85 orders (v2)" / "Closing History updated in place"

**QA-AMEND-10 `[ADMIN]` (negative)** — the re-confirm gate holds `[E-84]` `[BR-40]`
- Given amendment mode with target 85 and OK 84, or with an outstanding warning
- Then "Re-confirm Closing" is disabled with the §3.9 blocker-label grammar ("Re-confirm Closing (1 remaining)" / "… (1 warnings)" / "… (1 over target)")
- And a forced request is rejected server-side with **DC-22** and no version increment, and History still shows v1

**QA-AMEND-11 `[ADMIN]` (negative)** — an already-counted parcel cannot inflate the count `[E-85]`
- Given amendment mode with the confirmed scan list loaded
- When a tracking number already on a non-deleted confirmed row is scanned
- Then the verdict is `duplicate` (red row, voice, **DC-7** with `duplicate_of_seq` pointing at the confirmed row), `ok_count` does not change, and the gate stays blocked until the duplicate row is deleted (M2)

**QA-AMEND-12 `[ADMIN]` (negative)** — single working context `[E-79]` `[E-86]` `[BR-41]`
- Given a session on any date is `IN_PROGRESS`
- When `[Amend]` is confirmed on any History row
- Then the amend is rejected: red toast "✕ Another closing is open — confirm or cancel it first", **DC-27** with `reason=another_session_open`, and the record is untouched
- Given instead an amendment is open
- When a new date's closing Start is pressed
- Then it is rejected with **DC-2** `reason=amendment_open` and the client opens the amendment

**QA-AMEND-13 `[ADMIN]`** — persistence and exit `[E-80]` `[E-81]`
- Given an amendment is open with one added scan
- When the browser crashes and the page is reopened
- Then the `AMENDING` state resumes with the added scan intact (`[BR-8]`)
- When "✕ Exit amendment" is then confirmed
- Then a `closing.amend_cancelled` event (**DC-29**) exists with the discarded scan's sequence, the session returns to `CONFIRMED` v1, History is unchanged, and the discarded scan row remains queryable in the audit log

**QA-AMEND-14 `[ADMIN]` (negative)** — double Amend never forks `[E-82]` `[G-9]`
- Given operator A holds an open amendment on a date
- When operator B confirms `[Amend]` on the same date (or A double-clicks the M3 primary)
- Then exactly one `AMENDING` state exists; B is loaded into A's amendment; **DC-27** exists with `reason=already_amending`; no second **DC-26** is written for a new context

**QA-AMEND-15 `[ADMIN]`** — amending a past date `[E-83]` `[BR-42]`
- Given the 07-11 row (v1 = 78/78) is amended to 79/79 three days later
- Then the History row stays on **07-11** (`[BR-19]`), its badge carries the amend timestamp, and both snapshots remain reproducible: the v1 CSV byte-identical to the original day, the v2 CSV reflecting the amendment (latest served by the row's CSV button, earlier versions per DQ-13)

**QA-AMEND-16 `[ADMIN]`** — the re-confirm revalidation is scoped to the amendment's own rows `[E-83]` `[BR-29]` `[BR-40]` (added 2026-08-03)
- Given the 07-11 closing is `CONFIRMED` v1 (78/78) and, three days later, every order on its 78 confirmed scan rows has advanced past `Prepare Shipment` (e.g. to `Shipped`)
- When that date is amended, the target is edited 78 → 79, the found parcel is scanned (verdict `ok` — OK 79) and "Re-confirm Closing" is pressed once
- Then the re-confirm **succeeds**: the loaded confirmed rows are **not** re-judged against live order state, `closing.amended` (**DC-28**) exists with `old_target=78 → new_target=79` and `version=2`, and **no DC-22** exists
- And the count and target checks still ran over the **whole** amended list, not just the added row: the re-confirm passes only at `ok_count == target == 79` (78 loaded + 1 added), and a target that drifted mid-flight is still rejected under `[BR-3]`/E-73 exactly as in §3.9
- Given instead the newly scanned parcel's own order is moved out of `Prepare Shipment` between its scan and the press
- Then the re-confirm **is** rejected exactly as in §3.9: red toast "✕ Cannot confirm — {reason}" naming that order, **DC-22** persisted, no version increment, and History still shows v1 (78/78)

---

### 8.16 Coverage summary

| Block | Keyed to | `[WF]` | `[ADMIN]` | Total | Negative |
|---|---|---|---|---|---|
| QA-S0 | `[L-S0-1]`, E-15/16/42/55/72/76 | 4 | 7 | 11 | 6 |
| QA-SCAN | `[L-S1-1]`, `[L-S1-F]`, E-1/2/9/12/35/48/54/67/69/77 | 4 | 13 | 17 | 10 |
| QA-VERDICT | `[L-S1-2]`, `[L-S1-5]`, `[L-S1-6]`, `[L-S2-1]`, E-4/5/13/14/52/63/64/65/66 | 5 | 11 | 16 | 6 |
| QA-UNKNOWN | `[L-S2b-1]`, E-3/13/57 | 3 | 4 | 7 | 3 |
| QA-DUP | `[L-S3-1]`, E-6/7/8/65/70 | 3 | 7 | 10 | 2 |
| QA-VOICE | `[L-S1-3]`, E-39/46/61 | 6 | 3 | 9 | 3 |
| QA-COUNT | `[L-S1-4]`, `[L-S1-8]`, E-11/17/18/60/68 | 5 | 8 | 13 | 3 |
| QA-TARGET | `[L-S1-10]`, E-17/18/19/20/21/51 | 5 | 9 | 14 | 5 |
| QA-M1 | `[L-M1]`, E-22/23/24/25/56/78 | 5 | 9 | 14 | 7 |
| QA-DEL | `[L-M2]`, `[L-S1-6]`, E-26/27/28/29/58 | 6 | 4 | 10 | 4 |
| QA-CONFIRM | `[L-S1-8]`, `[L-S4-1]`, `[L-S4-2]`, `[L-S4-3]`, E-10/11/37/40/49/73 | 7 | 9 | 16 | 8 |
| QA-HIST | `[L-SH-1]`, `[L-S1-11]`, E-43/44/45/74 | 6 | 5 | 11 | 3 |
| QA-HUB | `[L-S1-7]`, E-47/75 | 4 | 5 | 9 | 2 |
| QA-PERSIST | `[L-S1-F]`, E-30…34/36/38/41/53/59/62/71 | 0 | 14 | 14 | 7 |
| QA-AMEND | `[L-SH-2]`, `[L-M3]`, E-79…86 | 6 | 10 | 16 | 6 |
| QA-CHROME | `[L-F1]`…`[L-F4]`, `[L-S1-9]`, E-50 | 5 | 1 | 6 | 2 |
| **Total** | | **74** | **119** | **193** | **77 (39.9%)** |

**How to reproduce the totals** (count **scenario-header lines only** — `[WF]`, `[ADMIN]` and `(negative)` all recur in §8 prose and in the traceability tables, so an unfiltered `grep -c` over §8 over-counts):
```sh
awk '/^## 8\. QA Acceptance/,/^## 9\. Out of Scope/' closing.md | grep -E '^\*\*QA-' > /tmp/h
wc -l < /tmp/h                  # 193
grep -cF '`[WF]`'    /tmp/h     #  74
grep -cF '`[ADMIN]`' /tmp/h     # 119
grep -cF '(negative)' /tmp/h    #  77
```
Every block row above sums column-wise to those four figures (74 + 119 = 193; 77 ÷ 193 = 39.9%). `E-35` is owned by **QA-SCAN** (QA-SCAN-10) and is deliberately absent from QA-PERSIST's range, which is why that range is written out rather than as `E-30…38`.

**Legend-unit coverage — all 24 units plus the 4 furniture keys have at least one asserting scenario:**

| Unit | Asserted by |
|---|---|
| `[L-S0-1]` | QA-S0-01…11 |
| `[L-S1-1]` | QA-SCAN-01…17 |
| `[L-S1-2]` | QA-VERDICT-02, QA-VERDICT-09 |
| `[L-S1-3]` | QA-VOICE-01…09 |
| `[L-S1-4]` | QA-COUNT-01…13 |
| `[L-S1-5]` | QA-VERDICT-01, 03, 06, 07, 08, 11, 14, 15, 16 |
| `[L-S1-6]` | QA-VERDICT-05, 15, QA-DUP-01…03, QA-DEL-03, QA-HIST-11 |
| `[L-S1-7]` | QA-HUB-01…09 |
| `[L-S1-8]` | QA-CONFIRM-01, 02, 07…13, 16, QA-COUNT-08 |
| `[L-S1-9]` | QA-CHROME-06 |
| `[L-S1-10]` | QA-TARGET-01…14 |
| `[L-S1-11]` | QA-HIST-01, QA-HIST-05, QA-CHROME-02 |
| `[L-S1-F]` | QA-SCAN-04, 11, 12, 16, QA-PERSIST-01, 02, QA-HUB-08 |
| `[L-S2-1]` | QA-VERDICT-03, QA-M1-01, QA-COUNT-10 |
| `[L-S2b-1]` | QA-UNKNOWN-01…07 |
| `[L-S3-1]` | QA-DUP-01…10 |
| `[L-S4-1]` | QA-CONFIRM-03, 04, 10, 12, 15 |
| `[L-S4-2]` | QA-CONFIRM-05, QA-CONFIRM-14, QA-HIST-07 |
| `[L-S4-3]` | QA-CONFIRM-06, QA-DUP-08 |
| `[L-SH-1]` | QA-HIST-01…11 |
| `[L-SH-2]` | QA-AMEND-01, 04…16 |
| `[L-M1]` | QA-M1-01…14 |
| `[L-M2]` | QA-DEL-01…10 |
| `[L-M3]` | QA-AMEND-02, 03, 07, 12, 14 |
| `[L-F1]` | QA-CHROME-01 |
| `[L-F2]` | QA-CHROME-02 |
| `[L-F3]` | QA-CHROME-03, QA-VERDICT-09, QA-CONFIRM-04 |
| `[L-F4]` | QA-CHROME-04, QA-CHROME-05, QA-DEL-10 |

### 8.17 Data-capture traceability (every §5 event has an asserting scenario)

| Event | Asserted by |
|---|---|
| **DC-1** `closing.session_started` | QA-S0-06, QA-S0-09 |
| **DC-2** `closing.start_rejected` | QA-S0-07, QA-S0-08, QA-S0-11, QA-PERSIST-10 |
| **DC-3** `closing.target_edited` | QA-TARGET-07, QA-TARGET-10, QA-TARGET-14, QA-AMEND-09 |
| **DC-4** `closing.target_edit_rejected` | QA-TARGET-06 |
| **DC-5** `closing.session_cancelled` | QA-TARGET-08 |
| **DC-6** `closing.session_restarted` | QA-TARGET-08 |
| **DC-7** `closing.scan_recorded` | QA-SCAN-03, 05 (negative), 06 (negative), 07, 08, 14, 15, 17 (negative), QA-VERDICT-06, 07, 08, 15, QA-UNKNOWN-04, QA-DUP-04, 09, QA-TARGET-14, QA-PERSIST-02 |
| **DC-8** `closing.scan_rejected` | QA-CONFIRM-12, QA-PERSIST-07 |
| **DC-9** `closing.scan_lookup_failed` | QA-SCAN-10 |
| **DC-10** `closing.warning_raised` | QA-VERDICT-10, QA-DUP-06 |
| **DC-11** `closing.warning_resolved` | QA-UNKNOWN-06, QA-M1-06, QA-M1-09, QA-M1-14 (negative), QA-DEL-08 |
| **DC-12** `closing.scan_row_deleted` | QA-DEL-06, QA-DEL-07 |
| **DC-13** `order.status_changed` | QA-M1-06, QA-M1-09, QA-M1-10, QA-M1-14 (negative), QA-PERSIST-11 |
| **DC-14** `order.outbounded` | QA-M1-06, QA-M1-09, QA-M1-10, QA-M1-14 (negative), QA-PERSIST-11 |
| **DC-15** `comment.posted` | QA-M1-08, QA-PERSIST-11 |
| **DC-16** `comment.auto_posted` | QA-M1-08 |
| **DC-17** `comment.mention_notified` | QA-M1-08, QA-HUB-06, QA-PERSIST-11 |
| **DC-18** `comment.starred` / `comment.unstarred` | QA-HUB-06 |
| **DC-19** `comment.read` / `comment.mark_all_read` | QA-HUB-05 |
| **DC-20** `closing.voice_alert_toggled` | QA-VOICE-06 |
| **DC-21** `closing.confirmed` | QA-CONFIRM-10, QA-CONFIRM-16, QA-PERSIST-04 |
| **DC-22** `closing.confirm_rejected` | QA-CONFIRM-07, 08, 11, 13, QA-AMEND-10, QA-AMEND-16 |
| **DC-23** `closing.snapshot_created` | QA-CONFIRM-10, QA-CONFIRM-16, QA-PERSIST-04, QA-PERSIST-12 |
| **DC-24** `closing.daily_shipping_status_updated` — **retired** (`[PD-71]`) | Absence asserted by QA-CONFIRM-10, QA-CONFIRM-16, QA-PERSIST-04, QA-PERSIST-08, QA-AMEND-09 |
| **DC-25** `closing.report_exported` | QA-CONFIRM-14, QA-HIST-07 |
| **DC-26** `closing.amend_started` | QA-AMEND-07, QA-AMEND-14 (negative) |
| **DC-27** `closing.amend_rejected` | QA-AMEND-12, QA-AMEND-14 |
| **DC-28** `closing.amended` | QA-AMEND-09, QA-AMEND-16, QA-AMEND-08 (negative) |
| **DC-29** `closing.amend_cancelled` | QA-AMEND-13 |

### 8.18 Edge-case traceability (every `[E-n]` has an asserting scenario)

All **86** edge cases map to at least one scenario, and every cell below names **only scenario IDs** — no `§`-pointers and no `DQ-n` pointers, which are documentation, not assertions. Six rows were repaired in the 2026-08-03 remediation pass, where the mapped scenario existed but asserted something else: E-37 (was QA-PERSIST-04, which tests *simultaneous* confirms = E-31 — now QA-CONFIRM-16 tests retry-after-timeout), E-52 (was QA-VERDICT-06, which asserts no item count — now QA-VERDICT-15), E-60 (was QA-COUNT-12, which deletes rows — now QA-COUNT-13), E-66 (was QA-VERDICT-07, which asserts statuses, never marketing orders — now QA-VERDICT-16), E-74 (was QA-HUB-08, which asserts hub focus, never links — now QA-HIST-11), E-77 (was QA-SCAN-15, which asserts terminators, never composition — now QA-SCAN-17). E-51's mapping moved from QA-TARGET-02 (which only unlocks the field) to QA-TARGET-14, which asserts the scan-during-edit behavior itself.

| E | Asserted by | E | Asserted by |
|---|---|---|---|
| E-1 | QA-SCAN-05 | E-40 | QA-CONFIRM-14 |
| E-2 | QA-SCAN-06 | E-41 | QA-PERSIST-09 |
| E-3 | QA-UNKNOWN-04 | E-42 | QA-S0-07, QA-PERSIST-10 |
| E-4 | QA-VERDICT-03, QA-M1-01 | E-43 | QA-HIST-06 |
| E-5 | QA-VERDICT-07 | E-44 | QA-HIST-08 |
| E-6 | QA-DUP-01, QA-DUP-04 | E-45 | QA-HIST-06, QA-HIST-09 |
| E-7 | QA-DUP-05 | E-46 | QA-VOICE-03 |
| E-8 | QA-DUP-07 | E-47 | QA-HUB-05, QA-HUB-06 |
| E-9 | QA-SCAN-02, QA-S0-04 | E-48 | QA-SCAN-12 |
| E-10 | QA-CONFIRM-12, QA-SCAN-13 | E-49 | QA-CONFIRM-05 |
| E-11 | QA-COUNT-08, QA-CONFIRM-09 | E-50 | QA-CHROME-06 |
| E-12 | QA-SCAN-07 | E-51 | QA-TARGET-14, QA-SCAN-12 |
| E-13 | QA-VERDICT-11 | E-52 | QA-VERDICT-15 |
| E-14 | QA-VERDICT-08 | E-53 | QA-PERSIST-13 |
| E-15 | QA-S0-05, QA-S0-09 | E-54 | QA-SCAN-08 |
| E-16 | QA-S0-02, QA-S0-05 | E-55 | QA-S0-08 |
| E-17 | QA-TARGET-09 | E-56 | QA-M1-10 |
| E-18 | QA-TARGET-10 | E-57 | QA-UNKNOWN-07 |
| E-19 | QA-TARGET-06 | E-58 | QA-DEL-07 |
| E-20 | QA-TARGET-05, QA-TARGET-08 | E-59 | QA-PERSIST-14 |
| E-21 | QA-TARGET-11 | E-60 | QA-COUNT-13 |
| E-22 | QA-M1-05, QA-M1-11 | E-61 | QA-VOICE-06 |
| E-23 | QA-M1-06, QA-M1-07 | E-62 | QA-PERSIST-11 |
| E-24 | QA-M1-10 | E-63 | QA-VERDICT-14 |
| E-25 | QA-M1-09 | E-64 | QA-VERDICT-12 |
| E-26 | QA-DEL-02, QA-DEL-03 | E-65 | QA-VERDICT-13, QA-DUP-08 |
| E-27 | QA-DEL-09 | E-66 | QA-VERDICT-16 |
| E-28 | QA-DEL-08 | E-67 | QA-SCAN-15 |
| E-29 | QA-DEL-07 | E-68 | QA-COUNT-12 |
| E-30 | QA-PERSIST-03 | E-69 | QA-SCAN-14 |
| E-31 | QA-PERSIST-04 | E-70 | QA-DUP-09 |
| E-32 | QA-PERSIST-05 | E-71 | QA-PERSIST-14 |
| E-33 | QA-PERSIST-06 | E-72 | QA-S0-11 |
| E-34 | QA-PERSIST-07 | E-73 | QA-CONFIRM-13 |
| E-35 | QA-SCAN-10 | E-74 | QA-HIST-11, QA-HUB-08 |
| E-36 | QA-PERSIST-01 | E-75 | QA-HUB-08 |
| E-37 | QA-CONFIRM-16, QA-PERSIST-04 | E-76 | QA-S0-10 |
| E-38 | QA-PERSIST-08 | E-77 | QA-SCAN-17 |
| E-39 | QA-VOICE-07 | E-78 | QA-M1-14 |
| E-79 | QA-AMEND-12 | E-83 | QA-AMEND-15, QA-AMEND-16 |
| E-80 | QA-AMEND-13 | E-84 | QA-AMEND-10 |
| E-81 | QA-AMEND-13 | E-85 | QA-AMEND-11 |
| E-82 | QA-AMEND-14 | E-86 | QA-AMEND-12 |

---

## 9. Out of Scope & Open Questions

Per the review conventions, this section lists **only**: NO-DEFAULT owner questions, developer-time decisions, and out-of-scope pointers. Owner questions that already carry a provisional default live in the PD register and are written into the body of this spec as normal behavior tagged `[PD-n · OWNER-PENDING]` — they are **not** repeated here.

### 9.1 Explicitly out of scope for this screen

| Not here | Where it lives |
|---|---|
| Label and invoice **layouts** (DELEO A4 picking, YUN 4×6 carrier, improved DELEO) | Phase 3-1, discussed with the owner after Phase 3 |
| Any print behavior | `[G-4]` surfaces are View Orders, Ready to be Outbounded and Order Detail; closing is CSV-only `[PD-68 · OWNER-PENDING]` |
| The View Orders **product-barcode** unrecognized flow and the shared unrecognized pool | View Orders, Unrecognized Tracking (`tracking-missing`) — boundary stated in §3.15 |
| The physical **Zero Packing** procedure itself | warehouse SOP; this screen only records the attestation (M1 checkbox) |
| Carrier tracking-status sync (delivered / in transit / exception) | last-mile tracking project, not WMS 2.0 |
| Inbound receiving, expected-qty edits, inbound requests, inbound tracking numbers | View Orders State 6 / Inbound Request `[G-10]` `[G-11]`; the namespace boundary is `[PD-8]` |
| Sample-set assignment and its dual view | Order Management `[G-13]` |
| Procurement Hub, COGS, DOH | excluded from this plan entirely (2026-08-02 owner decision) |
| Box / size measurement and DWS capture | removed from this page 2026-07-23; the weighing project is separate |
| Role and permission modelling | post-v1 owner decision [G-15] |
| **Location scheme and the line-based location filter** `[G-14]` — no location is displayed, filtered, edited or captured anywhere on this page | Inventory (`stock-status`) `[G-14]`; the 1:1 question is `[PD-46]`. Closing judges a parcel by its order's status, never by where its goods sat |
| **Audit-mode-only visibility** — closing has no audit mode, no audit-only column and no audit-gated affordance; every field on this page is visible in the single normal mode | Inventory (`stock-status`) stock audit sessions |
| **JIT residual stock** and every other JIT-vs-wholesale residual concept | Inventory (`stock-status`); the fulfilment-model definitions are out of this spec set. A closing scan is judged purely on order status (`[BR-1]`), so no sourcing route, JIT flag or residual balance reaches this page |

The three rows above were added 2026-08-03 after the mandatory-inclusion audit found them coded **n** for this page but stated **nowhere** — silent N/A cells, which the "explicit N/A, never silent" convention forbids (M3b §2.2).

### 9.2 Owner questions with **no default** (behavior deliberately unspecified)

**None remain.** Both of this page's former NO-DEFAULT questions were resolved by the owner on 2026-08-03:

- **`[PD-71]`** (Daily Shipping Status auto-update contract) — resolved by **retiring the sheet entirely**: no integration exists; the admin's Closing History is the system of record and the per-day CSV covers downstream needs (§6.4). Nothing blocks implementation.
- **`[PD-74]`** (correction path after confirmation) — resolved as **Amend Closing**, specified in §3.24/§3.25 with `[BR-39]`–`[BR-42]`. See §10 for both decision rows.

### 9.3 Developer decisions (state a default, mark dev-owned — not owner questions)

| Ref | Decision | Default / guidance in this spec |
|---|---|---|
| **DQ-1** | Barcode normalization and the in-flight scan model: trim/strip rules, case handling, min/max length, queue vs concurrent submit, verdict latency budget, per-paste value cap | Trim + strip CR/LF/Tab; reject below a minimum length (E-2); Enter **and** Tab submit (E-67); the input must never lock (`[BR-26]`); persist both raw and normalized (DC-7) |
| **DQ-2** | Per-scan idempotency mechanism (client `scan_id` vs server dedupe window), the double-Enter debounce window, and the rendering label for `ambiguous` | Client-generated `scan_id` per submit; ambiguous defaults to the `⚠ Unknown order` pill with colliding IDs in Notes (§3.6) |
| **DQ-3** | Voice-toggle persistence scope (localStorage per device vs user profile) | Either is acceptable; ON at the start of every session regardless (`[BR-13]`, E-61) |
| **DQ-4** | Multi-operator live-sync transport (polling vs WebSocket/SSE) and acceptable propagation latency for rows and counters; TTS cancel-and-speak vs queue | Server is authoritative for sequence and counters (`[BR-30]`); the wireframe demonstrates cancel-and-speak |
| **DQ-5** | CSV format: column order, encoding (UTF-8 with BOM recommended so Korean opens correctly in Excel), filename convention, deleted-row flag column | Deleted rows are **included** with a disposition flag (§3.18, §5.4) |
| **DQ-6** | ~~Daily Shipping Status failure handling~~ — **retired 2026-08-03** with the sheet (`[PD-71]`); ID kept, never renumbered | Void — no sheet write exists to fail (§6.4) |
| **DQ-7** | Spec-side normalization of wireframe fossils — no behavior change | `[WF-4]` "(M2)" → Closing History page; `[WF-5]` State 1 legend #2; `[WF-12]` duplicated wf-tab; plus the unregistered divergences U-a…U-j (§2.3) |
| **DQ-8** | TTS voice-selection fallback chain and zero-voice behavior | Wireframe chain: `Samantha` → any `en-US` → browser default; zero voices must degrade silently (E-39) |
| **DQ-9** | Scan-list scale handling beyond a few hundred rows (pagination vs virtualization) | If paginated, the latest page is the default during an active session (E-60) |
| **DQ-10** | Toast duration and stacking policy; idempotency key format and TTL; how a rejected duplicate request surfaces | Global appendix items — consistent across all 8 screens |
| **DQ-11** | The deep-link route for an Order ID and the new-tab mechanism (`target="_blank"` vs scripted open) | Real link, opened in a new tab while a session is `IN_PROGRESS` (§6.3, E-74) |
| **DQ-12** | Storage timezone and the exact rendering conversion | One warehouse operating timezone for all rendering and all date boundaries; server timestamps only (`[BR-36]`, E-59, E-71) |
| **DQ-13** | Amendment surfaces: how earlier snapshot versions of an amended day are exposed (the row's CSV serves the latest — v1 access UI is dev-owned), the exact rendering of the History "Amendment in progress" marker, and the amend idempotency key format | The version data model itself is fixed by `[BR-42]` (every version immutable and reproducible); only the surfacing is dev-owned (§3.20, §3.24, E-80) |

---

## 10. Decision Log

Every decision that shaped this screen, 2026-07-09 → 2026-08-03, including reversals and removals. Sources: the Korean decision ledgers `2026-07-09-wms2-wireframes.md` (item 7) and `2026-08-02-wms2-en-spec-handoff.md`, the wireframe legends (which carry their own dates), `_review.md` adjudications C-1…C-12, `_provisional-decisions.md`, and `_wireframe-fixes.md`.

| Date | Decision | Type | Where it lands |
|---|---|---|---|
| 2026-07-09 | Closing scoped as screen 7 of the WMS 2.0 wireframe set: barcode-scan verification of packed orders, red warnings for Processing and duplicate scans, **voice alert** on warnings. Source: ledger item 7 (F Closing) | scope | §1, `[L-S1-3]` |
| 2026-07-09 | 3-channel deploy discipline established for every wireframe change (`/wf-deploy {slug}`: repo → artifact → GitHub Pages) | process | §2.2 URLs |
| 2026-07-13 | Initial closing wireframe built in the 9-screen batch (19-agent workflow, commit `1bbba3a`), inheriting the View Orders v20 design system. State 4's mock data still carries this date ("closing confirmed 2026-07-13 18:52") | build | whole page |
| 2026-07-23 | **OK verdict narrowed to a single criterion**: `Prepare Shipment` only; every other status is a warning. Replaces the current process's manual "was it outbound-processed?" step | rule | `[BR-1]`, §3.6 |
| 2026-07-23 | **Box and size columns removed** from the scan list | **removal** | §3.23 |
| 2026-07-23 | **Manual hand-count target introduced** — the day's outbound target is typed by a human, never derived from the system | rule | `[BR-2]`, `[L-S0-1]` |
| 2026-07-23 | **Exact-match gating**: confirm requires `ok == target` **and** 0 outstanding warnings; **over-scan is also a mismatch** | rule | `[BR-3]`, `[L-S1-8]` |
| 2026-07-23 | **No auto-confirm** — a match only enables the button; the scan input stays live afterwards so an 85th parcel can still be found | rule | `[BR-4]` |
| 2026-07-23 | **State 0 simplified** to the count input alone; every other affordance hidden until closing starts | simplification | `[BR-9]`, `[L-S0-1]` |
| 2026-07-23 | **Large OK panel removed** (Dean) — OK becomes a compact one-line green bar, and stays silent | **removal** | `[L-S1-2]`, §3.23 |
| 2026-07-23 | **Large red warning panel and the separate action banner removed** — warnings are verified and resolved inside the row, keeping the operator in the scan loop | **removal** | `[L-S2-1]`, §3.23 |
| 2026-07-23 | **Unknown Order state (2b) added** — a tracking number matching no order is a warning excluded from the count, explicitly distinct from the View Orders unrecognized-product flow | addition | `[L-S2b-1]`, `[BR-6]`, `[BR-23]` |
| 2026-07-23 | **REVERSAL — Closing History converted from a modal (M2) to a separate page.** The modal reference survives as a fossil in State 4's legend, and "M2" was reassigned to the Delete Scan Row modal, so the stale text now points at the wrong artifact | **reversal** | `[L-SH-1]`, `[WF-4]`, §3.17 |
| 2026-07-23 | Daily record schema fixed: date · target · OK scans · warnings raised→resolved · match · closed by · confirmed at · per-day CSV containing the full scan list | rule | `[L-SH-1]`, `[BR-15]` |
| 2026-07-23 | Duplicate note must cite the colliding sequence number **plus** the first scan's time and worker (combined-box judgment); duplicates never double-counted; combined-box reasons logged in the order's Comments | rule | `[BR-5]`, `[L-S3-1]` |
| 2026-07-23 | Voice alert confirmed as the warning channel, ON by default, with a Test button; OK scans deliberately silent | rule | `[BR-13]` |
| 2026-08-02 | English conversion of the closing wireframe (168 replacements); Playwright pass; Pages deploy. Korean survives only as data (product names, carrier names, company names) `[G-6]` | build | whole page |
| 2026-08-02 | Procurement Hub excluded from this plan entirely; the spec set is the 8 screens | scope | §9.1 |
| 2026-08-03 | **Scanner protocol elevated to a global rule** `[G-1]` with closing named explicitly as a scan surface: cursor residency, **never refresh**, no clicks between scans (owner emphasis) | rule | `[L-S1-1]`, `[L-S1-F]` |
| 2026-08-03 | **Voice utterance fixed** as en-US TTS "Please check this order" `[G-3b]` (owner confirmation) | rule | `[BR-13]` |
| 2026-08-03 | **Global confirmation toast** mandate `[G-2]` — every confirming action toasts, including removals `[GD-5]` | rule | every action in §3 |
| 2026-08-03 | **@mention channel confirmed**: `#fulfillment-admin-comments` (`C0BMGEWM5QA`); the message body @mentions the person, the channel is the team-visible archive | rule | §6.1 |
| 2026-08-03 | **Instant print `[G-4]` reconfirmed globally**; adjudication **C-4** resolves the closing conflict — decision-sources listed "Closing report" as a print surface, the wireframe (SST) ships CSV only → **CSV-only, `[G-4]` does not land on closing** `[PD-68 · OWNER-PENDING]`, global delta GD-9 | **removal / adjudication** | `[BR-24]`, §6.5 |
| 2026-08-03 | Adjudication **C-5** — the `[G-3a]` send sound is scoped by **button class**, not by page, so closing's M1 outbound button plays it `[PD-2 · OWNER-PENDING]`; PD-2's page enumeration does not name closing, so the tension is written into §3.21 for the owner rather than resolved silently | provisional / flagged | §3.21 step 5, §6.6 |
| 2026-08-03 | Adjudication **C-6** — the wireframe's silent no-op on Start with an invalid count is a gap, not a decision: an explicit validation error is required `[WF-8]` | rule | §3.1, E-15/E-16 |
| 2026-08-03 | Adjudication **C-10** — State 1 legend #2 ("large panel used only in warning states") contradicts the 2026-07-23 removal. **Net truth: no large red panel remains; the only large panel is State 4's green completion status** `[WF-5]` | normalization | §3.3, §3.14 |
| 2026-08-03 | Adjudication **C-12** — shared cross-page events use the canonical names byte-identically: `order.status_changed`, `order.outbounded`, `comment.posted` / `comment.auto_posted` / `comment.mention_notified` / `comment.starred` / `comment.unstarred` / `comment.read` / `comment.mark_all_read` | convention | §5.1 |
| 2026-08-03 | Adjudication (non-issue register) — closing "unknown order" and the unrecognized-product pool are **confirmed disjoint**; the non-route must be stated explicitly in both specs | rule | `[BR-23]`, §3.15, §6.1 |
| 2026-08-03 | `[PD-1]` v1 ships a **single admin role**; no role gating on start/edit/cancel/confirm; every mutating action records the actor `[G-15]` | provisional | `[BR-25]` |
| 2026-08-03 | `[PD-2]` the `[G-3a]` send sound applies to **every outbound-class button on every page** → closing's M1 `[Process Outbound → resolve warning]` plays it, audibly distinct from the warning voice | provisional | §3.21, §6.6 |
| 2026-08-03 | `[PD-3]` comments are **append-only** — no edit, no delete | provisional | `[BR-28]` |
| 2026-08-03 | `[PD-4]` a Slack delivery failure never rolls back the primary action; it is persisted and retried | provisional | `[BR-32]`, §6.1 |
| 2026-08-03 | `[PD-5]` every destructive action gets a confirm step and a toast → Cancel Closing gains the missing dialog `[WF-7]`, row deletion gains its toast | provisional | §3.11, §3.22 |
| 2026-08-03 | `[PD-6]` the server revalidates at confirm time; on mismatch it rejects with a red toast and refreshes the affected view — no partial writes | provisional | `[BR-29]`, §3.9 |
| 2026-08-03 | `[PD-7]` concurrency — optimistic version check for single values; **server-side merge for counting flows**, which includes closing scans | provisional | `[BR-30]`, §7.4 |
| 2026-08-03 | `[PD-8]` inbound and outbound tracking numbers are **separate namespaces** — closing resolves outbound only, so an inbound-request number scanned here is `unknown` | provisional | §3.6, E-13 |
| 2026-08-03 | `[PD-69]` a duplicate warning is cleared by ✕-deleting the row after logging the combined-box reason as a comment; deleted warning rows still count in History's raised→resolved | provisional | `[BR-21]`, §3.16 |
| 2026-08-03 | `[PD-70]` **no second closing session on a confirmed date**; History shows one row per date; cancelled sessions are retained but never displayed | provisional | `[BR-18]`, §3.20 |
| 2026-08-03 | `[PD-71]` **NO-DEFAULT** — the Daily Shipping Status sheet and column mapping are undecided; only the invariants are specified | open | §6.4, §9.2 |
| 2026-08-03 | `[PD-72]` **no Slack route** for closing confirmation or unresolved warnings in v1 | provisional / **removal** | `[BR-31]`, §6.1 |
| 2026-08-03 | `[PD-73]` scanning is **locked after confirmation**; the State 4 input is disabled (the wireframe still renders it enabled — divergence U-b) | provisional | `[BR-18]`, §3.17 |
| 2026-08-03 | `[PD-74]` **NO-DEFAULT** — no reopen/amend path is specified for a parcel found after confirmation | open | §9.2 |
| 2026-08-03 | `[PD-75]` deleting the original OK row of a duplicate pair does **not** re-judge the survivor; the operator deletes it and rescans | provisional | `[BR-22]`, §3.16 |
| 2026-08-03 | `[PD-76]` non-`Processing` abnormal statuses share the `⚠ Not outbounded` pill with the real status in the Status column; `[Process this order]` appears only for `Processing` | provisional | `[BR-20]`, §3.6 |
| 2026-08-03 | `[PD-77]` the M1 **Zero Packing checkbox is mandatory** — the action button stays disabled until it is ticked | provisional | `[BR-7]`, §3.21 |
| 2026-08-03 | `[PD-78]` a session crossing midnight belongs to its **start date** | provisional | `[BR-19]` |
| 2026-08-03 | Wireframe defect register opened for this page: `[WF-4]` "(M2)" fossil · `[WF-5]` legend contradiction · `[WF-7]` missing cancel dialog · `[WF-8]` silent start validation · `[WF-12]` duplicated wf-tab. Fixes are deferred to a separate wireframe-edit pass so spec writing and wireframe editing never race | process | §2.3 |
| 2026-08-03 | Spec-authored rules recorded during the first write-up, each with its rationale in §4: outstanding-vs-raised warning split `[BR-16]`; sequence numbers never renumbered `[BR-17]`; scan lookup must never lock the input `[BR-26]`; every scan persists at scan time `[BR-27]`. Unregistered wireframe divergences U-a…U-f filed in §2.3 | rule | §4, §2.3 |
| 2026-08-03 | **Audit pass (spec v1.1).** Independent legend recount confirmed 22 units and added the reproduction method to §2.1. Four further unregistered divergences filed: U-g (voice controls wired only in State 1) · U-h ("Play again" vs "Test voice" labels) · U-i (State 4 switch copy) · U-j (warning states render a muted target line instead of the full banner, so `[BR-14]` gained the "banner in every in-progress rendering" clause) | normalization | §2.3, §3.11 |
| 2026-08-03 | **Audit pass — five spec-authored rules added** where the earlier draft was silent: `[BR-33]` counting is per parcel, not per order (split and combined shipments) · `[BR-34]` no closing with target 0, so a zero-shipment day simply has no record · `[BR-35]` an unresolved earlier-date session blocks a new date · `[BR-36]` one warehouse timezone for every rendered time and every date boundary · `[BR-37]` duplicate detection is session-scoped, with no cross-day check. Fifteen edge cases added (E-63…E-77) | rule | §4, §7 |
| 2026-08-03 | **Remediation pass (spec v1.2) — cross-page defect M3a-D2.** Closing's M1 gate was Zero Packing alone, which let a `Processing` order with `PENDING` lines emit the canonical `order.outbounded` through a path View Orders `BR-9` and `order-detail.md` L-9 both declare impossible ("iff every line is INBOUNDED"). Closing now enforces the same predicate; the button carries the shortfall reason and the warning stays outstanding | rule | `[BR-38]`, §3.21, E-78, QA-M1-14 |
| 2026-08-03 | **Remediation — cross-page defect M3a-D3.** `Cancelled` was used as an order status in the verdict matrix, `[BR-20]` and `[E-5]`, contradicting the 8-status vocabulary VO `BR-12` / OD `BR-12` state as exhaustive. Cancellation is a **flag**: the Order Status column renders the underlying status plus a `Cancelled` marker. The `[PD-76]` register title still lists "Cancelled" and needs the same edit at the owner's next pass | **normalization** | §3.6, §3.7, `[BR-20]`, E-5, E-56, QA-VERDICT-07, QA-M1-10 |
| 2026-08-03 | **Remediation — cross-page defect M3a-D7.** The Comments hub is one component on all eight screens, so its copy is a byte-exact `[G-7]` contract. Closing was an outlier on both pane headers and the unstar hint; the four-page majority strings are adopted as canonical and the wireframe's strings are demoted to `[WF]`-only demo copy, registered as `[WF-15]` | **normalization** | §3.8, §2.3, QA-HUB-01/02/09 |
| 2026-08-03 | **Remediation — cross-page defects M3a-D16/D19/D20 and M3a-D13.** Deep links normalized to the `[G-12]` directory form `../{slug}/#{anchor}`; the 8 statuses declared as lowercase-hyphenated **values** rendered as title-case **labels**, with the mapping stated once; `[G-3a]`/`[G-3b]` fixed as this spec's sub-rule citation form; `[GD-n]` declared resolvable (`_plans/_review.md` §4) so no citation dangles | convention | §3.0, §3.7, §6.3 |
| 2026-08-03 | **Remediation — M3b §2.2 silent-N/A gap.** Mandatory items 9 (line-based location filter), 10 (audit-mode-only visibility) and 11 (JIT residual stock) were coded **n** for closing but stated nowhere. Three explicit out-of-scope rows added; `G-14` and JIT now appear in this spec by name | **normalization** | §9.1 |
| 2026-08-03 | **Remediation — M2 adversarial QA run (68/68 `[WF]` scenarios executed, 405 assertions).** Three expected strings were wrong because nested *functional* descendants pollute `textContent` the way `.dot` does (`header button.x`, `.badge-n`, `.paneheader small`, `.avatar`): fixed to `starts with`, and R2b now lists all four. §8.0 gained normative assertion verbs (R6b), a state-activation rule (R9) and a PD-shorthand rule (R10); four unassertable clauses (QA-S0-01 heading selector, QA-HIST-03 highlight, QA-CHROME-02 `p.sub`, QA-CHROME-04 "23") were made executable | QA | §8.0, QA-S0-01, QA-DEL-01, QA-HUB-01/02, QA-HIST-03, QA-CHROME-02/04 |
| 2026-08-03 | **Remediation — M1 coverage audit.** §8.18's "every `[E-n]` has an asserting scenario" was false for six edge cases whose mapped scenario asserted something else (E-37/52/60/66/74/77) plus a partial (E-51). Seven `[ADMIN]` scenarios added (QA-SCAN-17 · QA-VERDICT-15/16 · QA-COUNT-13 · QA-TARGET-14 · QA-CONFIRM-16 · QA-HIST-11), plus QA-HUB-09 and QA-M1-14 from the cross-page fixes. §8.16 key lists corrected (E-35 belongs to QA-SCAN only; E-74 to QA-HIST; `[L-S4-1..3]` enumerated), §8.0's traceability pointers un-shifted (§8.17/§8.18), and U-a extended to the Confirm button's `79`. Scenario count 168 → 177, negative share 40.5% → 40.1% | QA | §8, §2.3, §3.9 |
| 2026-08-03 | **Audit pass — QA rebuilt to a runnable contract.** §8.0 now fixes the execution environment (reset discipline, `.dot`-stripping text normalization, attribute-based selection because of `[WF-12]`, a speech-synthesis stub, row addressing, page-global demo state). One assertion in the earlier draft could not pass on the live wireframe — the 10-column header check read `#6` and `Closing Verdict5` because annotation dots sit inside those `th` cells; it is now normalized (QA-VERDICT-05). Scenario count 125 → 168, negative share 36.8% → 40.5%, and every `[E-n]` gained a traceability row (§8.18) | QA | §8 |
| 2026-08-03 | **REVERSAL — `[PD-74]` RESOLVED by owner: Amend Closing.** Owner contract (verbatim intent): "수정 누르면 마감하던 게 쭉 뜨고, 맨 위 수동 숫자를 하나 올리면 된다." Each confirmed Closing History row gains `[Amend]` → M3 confirm ("Amend the closing for {date}? The confirmed record stays until you re-confirm.") → **amendment mode** (the day's full confirmed scan list loaded, amber "AMENDING — {date} closing (confirmed {ok}/{target})" banner, editable manual target, live scan input) → exact-match **Re-confirm Closing** updates the record **in place** with an "Amended" badge (version · actor · timestamp); Closing History itself carries the correction. §3.23's "no reopen/amend affordance" negative row removed (this row records the reversal); `[PD-70]`/`[PD-73]` immutability upheld — same session reopened, one row per date, v{n} snapshots never mutated | **reversal / owner decision** | §3.24, §3.25, `[L-SH-2]`, `[L-M3]`, `[BR-39]`–`[BR-42]`, DC-26…DC-29, E-79…E-86, QA-AMEND-01…15 |
| 2026-08-03 | **Wireframe defect batch applied (owner-approved), same pass as the Amend build**: `[WF-4]` "(M2)" → "the Closing History page" · `[WF-5]` State 1 legend #2 reworded to the C-10 net truth · `[WF-7]` Cancel Closing confirm dialog added (`#m-cancel`, §3.11 copy, no legend dot) · `[WF-8]` Start validation red toasts added (empty / non-whole-number) · `[WF-12]` duplicate wf-tab removed (a "Modal: Amend Closing" tab added, `.wf-tab` stays 10). QA-S0-02, QA-TARGET-04, QA-CHROME-03/04, QA-HIST-10 and R3/R8/R10 updated to the fixed wireframe; `[WF-15]` deliberately **not** applied (corpus-wide `[G-7]` precondition, §2.3). Verified by Playwright against the edited file (70 checks, 0 fail, 0 pageerror) | wireframe fix | §2.1, §2.2, §2.3, §3.1, §3.3, §3.11, §3.14, §3.17, §8 |
| 2026-08-03 | **REVERSAL — `[PD-71]` RESOLVED by owner: the SS Daily Shipping Status spreadsheet is retired entirely.** No sheet integration exists — the former §6.4 contract (auto-update on confirm, idempotency, failure surfacing) is void, and the admin's **Closing History** (daily snapshots + per-day CSV) replaces the sheet wholesale. Fallout, IDs kept per convention: `[BR-11]` retired · `[BR-32]` sheet clause struck · DC-24 retired (never emitted; absence QA-asserted) · E-38 rewritten as an absence case · DQ-6 void · wireframe copy corrected (gate note, State 1 legend #8, State 4 toast subtext "Closing record saved · replaces the retired Daily Shipping Status sheet", "(sheet retired 2026-08-03)" on the report banner and its legend, amend copy) · QA-CONFIRM-01/04/05/10/16, QA-PERSIST-04/08, QA-AMEND-09 updated | **reversal / owner decision / removal** | §1.1, §3.9, §3.17, §3.18, §3.24, §3.25, `[BR-11]`, `[BR-32]`, `[BR-40]`, DC-24, §6.1, §6.4, E-37/E-38, §8, §9 |
| 2026-08-03 | **Clarification — the re-confirm's server-revalidation scope.** §3.24's "identical to §3.9" was read as re-running §3.9's live order-status re-check over **every** OK row, which would reject every amendment whose parcels had already shipped — structurally impossible for the past-date correction the flow exists for (E-83) and for the owner's canonical case. Scope now stated: counts and target over the whole amended list; the live status re-check over the rows **added in this amendment** only; v{n} snapshot rows keep their certified verdict (`[BR-42]`). No rule changed — the check set and the rejection semantics are as written. `[BR-40]` and E-83 carry the same scope; QA-AMEND-16 (`[ADMIN]`) added to assert both branches; census 192 → 193 | **clarification / QA** | §3.24, `[BR-40]`, `[BR-29]`, E-83, DC-22, DC-28, §8.0, §8.15b, §8.16, §8.17, §8.18 |
| 2026-08-03 | **Spec v1.3 bookkeeping.** Legend units 22 → **24** (Closing History dot 2 = `[L-SH-2]`, modal dot M3 = `[L-M3]`); business rules → `[BR-42]`; events → DC-29; edge cases 78 → **86** (§7.7); QA scenarios 177 → **192** (74 `[WF]` · 118 `[ADMIN]` · 77 negative, 40.1%) via block 8.15b QA-AMEND (lettered so §8.16–§8.18 pointers stay stable); `[PD-74]` removed from §9.2; DQ-13 added | rule / QA | §2.1, §4, §5, §7, §8, §9 |

**Nothing above has been silently dropped.** Where a feature was removed, §3.23 carries an explicit "must NOT exist" entry pointing back at the row that removed it; where a decision was reversed (Closing History modal → page), both directions are recorded here and the fossil that survives in the wireframe is named.
