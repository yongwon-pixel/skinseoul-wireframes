# Unrecognized Tracking — Screen Specification

> **Decision status update (2026-08-03)** — PD-1 through PD-8, 51, 55, 66, 71, 74, 79 are now **OWNER-DECIDED** (PD-6 confirmed 2026-08-03 — the owner decision round is fully closed); any inline `[PD-{these} · OWNER-PENDING]` or `[PD-{these} · NO-DEFAULT]` tags below are superseded — see `_provisional-decisions.md` for the decisions.

**Slug:** `tracking-missing` · **Wireframe (SST):** `wms2/tracking-missing/index.html` · **Live:** https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/tracking-missing/
**Spec version:** 1.3 (PD-5/PD-60 owner confirmation + the 2026-08-03 wireframe pass — WF-6 · WF-NEW-D · WF-NEW-E · WF-10/WF-NEW-C applied) · **Written:** 2026-08-03 · **Template:** `_inputs/spec-template.md` v1 · **Global rules:** `_global-rules.md` v1.0
**Companion registers:** `_plans/_provisional-decisions.md` (PD) · `_plans/_wireframe-fixes.md` (WF) · `_plans/_review.md` (C-1…C-12, §3 conventions, §4 GD-1…GD-10)

> **Reading contract.**
> 1. Every `[G-n]` is a citation to `_global-rules.md` v1.0. This document restates a global rule body **only where the page narrows or extends it**, and in that case the delta, its rationale, and its date are named in the same sentence. Everywhere else it cites and adds the page delta only.
> 2. Every behavior resting on a provisional decision is tagged `[PD-n · OWNER-PENDING]` **in the sentence where it appears**, including inside QA scenarios. Reversing a PD means editing only the tagged sentences and nothing else. Once the owner rules, the tag becomes `[PD-n · CONFIRMED {date}]` and the behavior stops being reversible-by-tag — on this page that is `[PD-5]` and `[PD-60]` (2026-08-03).
> 3. Where the wireframe is stale, wrong, or missing an affordance, this spec states the **correct** behavior and names the defect (`WF-n`). The wireframe text is never specced as-is.
> 4. IDs `[L-*]`, `[BR-n]`, `[DC-n]`, `[N-n]`, `[E-n]` are page-scoped and **never renumbered**. Merged entries keep both IDs.
> 5. Quoted UI strings are byte-accurate to the wireframe unless marked *(spec-authored)*.
> 6. Every `[GD-n]` is one of the ten global-rule deltas recorded in `_plans/_review.md` §4. All ten landed in `_global-rules.md` v1.0 (verified 2026-08-03), so a `[GD-n]` citation is a **provenance pointer, not a live rule** — the binding text is always the `[G-n]` body it produced. `[GD-n]` IDs are resolvable only in `_review.md` §4; they are cited here for traceability and never as the source of a behavior.
> 7. Three page-level readings in this document are **candidate global amendments that have not yet been raised into `_global-rules.md`** and are therefore stated locally on purpose: `[BR-44]` (the scope of `[G-2]`'s refresh prohibition), §5.1's event-name note (shared-concept event naming), and §3.6's Comments-hub pane-header strings. Each names the cross-page defect that raised it. If the global rule is later amended, the global text supersedes and the page statement is deleted, not edited.

---

## 1. Purpose & Users

### 1.1 What this screen is

The Unrecognized Tracking page is the **desk-side resolution surface for physical products that arrived at the fulfillment center without a resolvable link to an order.** It holds one shared pool of such items, proposes the orders they most likely belong to, and lets a handler bind one to an order's product line with two clicks.

It replaces a manual process: before this page existed, parcels whose barcode scan failed were physically set aside on a shelf and chased down in Slack and spreadsheets. `[L-0]`

### 1.2 The operational moment (why the page exists)

SkinSeoul's JIT purchasing creates a structural timing gap:

- **Coupang issues the purchase order number immediately, but the last-mile tracking number only hours later.** A parcel therefore reaches the packing bench before the system knows which order it belongs to.
- At the bench, the operator scans the parcel's last-mile barcode. If the scan resolves, nothing reaches this page.
- If it does not resolve, View Orders shows an order-number lookup popup (M2). If the operator can type the Coupang purchase order number and the lookup succeeds, **the tracking number is matched and registered on the spot and the item never enters this pool** — this is why the pool's Order No column is almost always `–`. `[L-1]`
- If there is no order number, or the lookup fails, the operator sends the item to this pool through the View Orders send-to-unrecognized modal (M2b): English product-name autocomplete, quantity, optional memo. That send is the **only** way a row appears here `[BR-1]`.

Since 2026-08-02 the same pool also absorbs a second, structurally different case: **unrequested inbound stock** — supplier goods that arrive against neither a customer order nor an inbound request. The owner explicitly rejected building a separate temporary registration path for these `[BR-11]`.

### 1.3 Who uses it, and where their body is

Two populations touch this flow, and the design is deliberately asymmetric between them.

**The registrant — warehouse center staff (Miranti, Dean in the wireframe data).**
Standing at the packing bench. Scanner in the dominant hand, parcel in the other, frequently gloved, boxes queued behind them. Throughput pressure is real, and the bench operates under the scanner protocol `[G-1]`. **This page adds zero burden to them** — they never open it. Registration happens on View Orders, at the bench, in the modal they are already looking at. The single field they contribute to this page's usefulness is the optional **Memo**, their only channel to the desk-side resolver ("Box label damaged", "Looks like a 1+1 set", "suspected inbound stock"). The physical product is then set aside and **stays set aside until a resolver confirms a match**; only then does a rescan proceed as a normal flow `[DC-17]`.

**The resolver — order-team PIC (Dean / Egita / Harshit / Miranti as handler personas).**
Seated at a monitor, roughly 60 cm away, no gloves, no bench-grade time pressure. Critically, **the resolver does not poll this page.** Their flow starts in Slack: registration fires an automatic message into **`#unrecognized-tracking`** (channel ID not published in the routing table; resolved at wiring time — §6.1) that @mentions the suspected PICs with the candidates already attached `[BR-6]`. They click through, find the row, click **Review & Match**, click **Match to this product**. Two clicks, zero typing, zero searching. The loop closes back to the bench through a comment @mention routed to **`#fulfillment-admin-comments`** (`C0BMGEWM5QA`) `[BR-7]`.

That push-not-poll property is the reason for three otherwise surprising design choices, all of which this spec protects:

1. **No search bar, no filters, no pagination.** Removed 2026-07-23. The pool is expected to hold a handful of items and the resolver arrives with a deep link, not a query `[BR-16]`.
2. **No manual PIC search.** The candidate list is the complete set of "contains this product AND is in Processing" orders. If the right order is not listed, the upstream order data is wrong — searching harder will not find it `[BR-4]`.
3. **The system proposes, the human confirms.** The 2026-07-23 UX inversion. The old design made handlers hunt for their own name per product; the new one hands them a pre-computed answer `[BR-2]`.

### 1.4 Physical-reality facts that shaped specific decisions

| Fact | Decision it forced |
|---|---|
| The parcel is in the resolver's mind but not in their hand — they judge from a text row | Both an English **and** a Korean product name column, plus Size and Barcode, so a set or variant can be told apart on a photo-less row `[L-1]`, `[BR-14]` |
| Bench staff and their memos speak Korean; brands are recognized faster than product names | Brand bold-prefixing applies to **both** name columns on this page — the page delta over `[G-6]` is *which surfaces* it covers, not the rule `[BR-14]` |
| 1+1 sets arrive as one physical unit with qty 2 (the `medicube` row) | Qty mismatch at match time is **allowed**, not blocked — the difference is recorded, not litigated `[PD-65 · OWNER-PENDING]` |
| The pool row is a yellow-highlighted block (`.row-hit`, `--hl #FFFBD6` with a `--hl-line #F59E0B` border) readable across a desk | The highlight is a spec requirement, not decoration — it is how an operator confirms at a glance that a row is unresolved `[L-1]`, `[BR-36]` |
| The destructive **✕** sits directly beside the primary blue **Review & Match** button, both `.btn-sm` at ~28 px height | A one-click destructive action at that distance is a mis-tap hazard → a confirm dialog with a mandatory reason and a toast is required `[PD-60 · CONFIRMED 2026-08-03]` (owner confirmation of `[PD-5]`); wireframe gap `WF-6` **fixed 2026-08-03** — the wireframe now ships the M2 confirm modal |
| Nobody watches this page; items rot silently since the 2026-07-23 removal of wait-time chips | A once-daily aging digest restores the age signal without re-adding UI `[PD-61 · OWNER-PENDING]` |
| A resolver may be interrupted mid-decision and return with a stale screen | The server revalidates every precondition at confirm; nothing is trusted from the client's snapshot `[BR-21]`, `[PD-6 · OWNER-PENDING]` |

### 1.5 Explicit non-scope of the operator model

- **This page has no scan surface.** `[G-1]` therefore does not apply on-page. It is stated rather than omitted, because six of the eight screens do carry a scan input and a reader may assume this one does. The scanner loop closes on View Orders: after a match, rescanning the same barcode resolves normally `[DC-17]`, `[BR-30]`.
- **This page has no print surface.** `[G-4]` does not land here. There is no label, no picking artifact, no printer dependency `[BR-31]`. (The neighbouring `[PD-68 · OWNER-PENDING]` decision — Closing is CSV-only — is a different page's exclusion and is named here only so the `[G-4]` surface registry reads consistently.)
- **This page has no outbound-class button,** so the `[G-3a]` send sound does not apply and `[PD-2 · OWNER-PENDING]` cannot land here regardless of how the owner rules on it. There is no audio of any kind on this page.
- **The Closing page's "unknown order" warning is a different concept and does not route here.** A closing scan that finds no order raises an on-page warning and never creates a pool row; conversely, nothing in this pool feeds Closing. The two flows are disjoint `[BR-32]`.

---

## 2. Screen Inventory & Wireframe Map

### 2.1 Declared unit count (for coverage checking)

- **Legend units: 8.** Dots `0 · 1 · 2 · 3 · 4 · 5` plus modals `M1` and `M2` (M2 added 2026-08-03 by the wireframe pass that closed `WF-6`). Independently verified against the HTML: eight `.dot` elements, six `<li>` legend entries (0–5), two modal dots (`M1`, `M2`).
- **Numbering gaps: none.** Dots run 0–5 consecutively; there is no vacated number and no dot without a legend entry (M2 is described inside legend entry 3, mirroring how M1 is).
- **Non-legend spec units: 5.** Two off-screen normative footer blocks (`[L-S1-Fa]`, `[L-S1-Fb]` — the two `<p>` paragraphs after the legend `<ol>`) and three page-furniture units (`[L-F1]`…`[L-F3]`). *(Until 2026-08-03 `[L-M2]` was a sixth, spec-added unit mandated by `[PD-60]` / `WF-6`; the wireframe now ships it, so it counts as a legend unit above.)*
- **Total spec units: 13.** All 13 appear in §3.

This page is **single-state**, so legend keys use the plain `[L-{n}]` form per `_review.md` §3.1. The off-screen footer paragraphs use `[L-S1-F{a|b}]` because the page's only state is `#s1` and the footer holds two distinct rule blocks.

### 2.2 States, tabs, modals

| Unit | Screen element | How to reach it (live wireframe) | Spec section |
|---|---|---|---|
| `[L-0]` | Page identity: `<h2>` "WMS - Unrecognized Tracking List" + `.sub` subtitle | Default view. Dot 0 sits left of the `<h2>`. | §3.1 |
| `[L-1]` | Unrecognized product pool: `.poolhead` card + 12-column `.tbl` with `.row-hit` rows | Default view. Dot 1 is on the top-left of `.poolhead`. | §3.2 |
| `[L-2]` | "Suspected Orders (Auto-matched)" column (11th `<th>`) | Default view. Dot 2 is on that header cell. | §3.3 |
| `[L-3]` | "Action" column (12th `<th>`): `Review & Match` + `✕` (`.xdel`) | Default view. Dot 3 is on that header cell. | §3.4 |
| `[L-4]` | Brand-prefixed product naming ("Product Name" header) | Default view. Dot 4 is on the "Product Name" header cell. | §3.5 |
| `[L-5]` | Comments hub — `💬 Comments` button + `#inbox1` dropdown ([@ Mentions] / [★ Saved] / full-text search) | Top nav bar. Dot 5 sits left of the button. Click the button to open `#inbox1`. | §3.6 |
| `[L-M1]` | Modal "Review & Match — Unrecognized Product" (`#m-match`) | Two paths: any row's **Review & Match** button, **or** the purple wf-bar demo button labelled "Modal: Match Review (M1)". | §3.7 |
| `[L-M2]` | Modal "Remove this item from the pool?" (`#m-remove`, confirm + reason) — **wireframe-implemented 2026-08-03, closing `WF-6`** | Two paths: any row's **✕** button, **or** the purple wf-bar demo button labelled "Modal: Remove Confirm (M2)". In the admin: the row's **✕** only. | §3.8 |
| `[L-F1]` | Toast surface (`#matchToast`, `position:fixed; top:18px; right:18px`, 4000 ms) | Fires after a match confirm. | §3.9 |
| `[L-F2]` | Bottom count line: `Unrecognized pool · <span id="poolCountBottom">3</span> items` | Below the table. | §3.10 |
| `[L-F3]` | Top nav bar + Comments unread badge (`.badge-n` = "3") | Always visible. | §3.11 |
| `[L-S1-Fa]` | Off-screen legend footer paragraph 1: the 2026-07-23 simplification record (removed features + UX inversion) | Legend block, first `<p>` after the `<ol>`. Normative: it is the authoritative list of features that **must not exist**. | §3.12 |
| `[L-S1-Fb]` | Off-screen legend footer paragraph 2: the 5-step flow summary + the 2026-08-02 unrequested-inbound confirmation | Legend block, second `<p>` after the `<ol>`. Normative: it defines the cross-page flow and the inbound-stock route. | §3.13 |

### 2.3 Wireframe chrome that is NOT an implementation unit

The following exist only to make the static wireframe demonstrable and **must not be built**:

- The purple `.wf-bar` (title `WMS 2.0 · Unrecognized Tracking Wireframe`, hint `v3 — ✕ removal now confirms with a reason (2026-08-03) · purple numbers = new/changed annotations`).
- The wf-bar buttons `Modal: Match Review (M1)` and `Modal: Remove Confirm (M2)` — demo shortcuts. In the admin, M1 and M2 open only from a row.
- The `Hide annotations` toggle (`#annoToggle`) and all `.dot` / `.legend` markup.

### 2.4 Known wireframe demo limitations (QA must NOT file these as bugs)

Tag these `[ADMIN]` when asserting the correct behavior; the current behavior is asserted separately as `[WF]` in block **WFQ** (§8.15) so that an automated agent never reports a false failure.

1. **`finishMatch()` is hard-wired to row 1.** Clicking **Review & Match** on any of the three rows opens `#m-match` populated with row 1's COSRX item, and confirming removes `#poolrow1` regardless of which row was clicked. The admin must open M1 **scoped to the clicked row** and remove **that** row.
2. **RESOLVED 2026-08-03.** ~~`.xdel` removes the row immediately with no dialog and no toast.~~ The `WF-6` gap was closed by the wireframe pass: `.xdel` now opens the M2 confirm modal, and removal happens only on its confirm — see `[L-M2]` and `[PD-60 · CONFIRMED 2026-08-03]`.
3. **Candidate order numbers are styled blue and bold but are not anchors.** The file contains **zero** `<a>` elements. `[G-12]` requires real links — see `[BR-37]` and defect **WF-NEW-B**.
4. **The Comments hub dropdown has no search input** even though `[L-5]`'s legend text mandates "search across all comments". The 2026-07-29 global comment-search rollout (commit `8e5abeb`) never reached this page's markup — see defect **WF-NEW-A**.
5. **No empty-pool state is drawn.** Removing all three rows leaves an empty `<tbody>` and no guidance text.
6. **`poolDec()` updates both counters and floors them at 0, but nothing else re-renders.** There is no empty-state rendering, no live-arrival mechanism, and no re-computation of the remaining rows' candidate cells.
7. **`finishMatch()` decrements only if `#poolrow1` still exists.** If row 1 was already removed with `.xdel`, a subsequent `Match to this product` click still shows `#matchToast` but leaves the counters unchanged. In the admin, a confirmed match always decrements for the row it actually closed.
8. **`#inbox1` does not close on an outside click or on `Esc`.** The only handler is the toggle on the `💬 Comments` button. The admin must close it on both `[BR-40]`.
9. **`#poolrow1` is the only row carrying an `id`.** The admin assigns `id="poolrow-{pool_item_id}"` to every row so deep links can target one.
10. **RESOLVED 2026-08-03 (defect `WF-NEW-D`).** ~~`.xdel` was not double-click safe: two clicks removed one row but decremented both counters twice~~ — the unguarded `b.closest('tr').remove(); poolDec();` handler was replaced in the wireframe pass. `.xdel` now only opens M2 (a second click is a no-op while the overlay is open), and the M2 confirm handler mirrors `finishMatch()`'s guard: it captures the row first and calls `poolDec()` only when the row was actually attached (`rmRow.isConnected`), so counters always equal rendered rows `[BR-33]`, `[BR-41]`. Fixed behavior is asserted by QA-WFQ-07 (rewritten); the server-side idempotency half remains QA-NEG-03 `[ADMIN]`.

### 2.5 New wireframe defects found while writing this spec

Not present in `_wireframe-fixes.md` (WF-1…WF-14) when this spec was first written; filed here for the wireframe-edit pass. **WF-NEW-D and WF-NEW-E have since been appended to `_wireframe-fixes.md` §B so the wireframe pass is driven off the register, not off this spec.** Deploy rule: any wireframe edit goes out through `/wf-deploy tracking-missing`, never by editing the published copy.

> **2026-08-03 wireframe pass applied (local edit, deploy pending).** The register-backed items — `WF-6` (M2 confirm modal), `WF-NEW-D` (removal guard), `WF-NEW-E` (canonical hub pane headers), and `WF-10` + `WF-NEW-C` (dead v1 CSS/JS deleted; `.toast.err` retained, `.mtextarea` retained because M2's memo field now uses it, `.tag-jit` retained for M1's Channel badges) — are now **fixed in the local wireframe** and verified by an automated Playwright run (58 assertions, 0 pageerror). **`WF-NEW-A` (hub search input) and `WF-NEW-B` (order-number anchors) remain open** — they are not register §B rows and were out of that pass's scope. The three-channel deploy (`/wf-deploy tracking-missing`) has not run yet.

> **Register-citation warning.** `_review.md` §2a's tracking-missing Notes cell cites this page's dead-code cleanup as **`WF-9`**. That is wrong: `WF-9` is *ready-to-outbound — picking list modal has no sample-set lines*. The correct entry for this page's v1 CSS/JS leftovers is **`WF-10`** (confirmed against `_wireframe-fixes.md`; raised as m3b finding 5.3). Every citation in **this** document uses `WF-10`. A wireframe-edit pass driven off `_review.md` rather than off `_wireframe-fixes.md` will search the wrong file and leave the real leftovers in place.

- **[WF-NEW-A] — Comments hub is missing the full-text search input.** File: `wms2/tracking-missing/index.html`, `#inbox1`. Legend 5 and `[G-7]` both require search across all comments; the markup ships only the two tabs. Every other page carrying the hub got the search input in commit `8e5abeb` (2026-07-29). Fix: add the search input to `#inbox1`.
- **[WF-NEW-B] — Candidate order numbers are not links.** Verified: the file contains **0** `<a>` elements. Selectors: the `Suspected Orders` cells in all three pool rows, and the `Order` column in `#m-match`. `[G-12]` states cross-page references are real links. Fix: wrap in an anchor to the order.
- **[WF-NEW-D] — FIXED 2026-08-03.** `.xdel` double-click double-decremented both counters (unguarded `b.closest('tr').remove(); poolDec();`, §2.4.10). The wireframe pass replaced the handler: `.xdel` now opens M2, and the confirm handler captures the row and calls `poolDec()` only when `rmRow.isConnected` — the `finishMatch()` guard, mirrored as the register prescribed. **Also filed in `_wireframe-fixes.md` §B.**
- **[WF-NEW-E] — FIXED 2026-08-03 (this page's half).** The `#inbox1` pane headers now ship the four-page-majority strings `Comments mentioning me · Click to open the order` / `Saved comments · Click to open the order`; `Mark all read` and `Unstar to remove from the list` were already canonical and are unchanged. QA-CMT-03 / QA-CMT-05 are re-baselined to the canonical strings and §3.6's `[WF]`-vs-`[ADMIN]` table is collapsed. The corpus-wide half — publishing the six hub strings in `[G-7]` — remains open (cross-page defect m3a D7). **Also filed in `_wireframe-fixes.md` §B.**
- **[WF-NEW-C] — FIXED 2026-08-03, together with `WF-10`** (both deleted in the wireframe pass; `.toast.err` kept as specified, and `.mtextarea` was removed from the dead list because M2's memo field now uses it). Original filing: `WF-10` names `.trk`, `.shelf`, `.wait`, `.slack-pill`, `.picava`, `.picname`, `.cntchip`, `.logsec` and the trk-input script block. Additionally unused in the rendered DOM: `.ordercard`, `.seg`, `.bulkbar`, `.cpanel`, `.logtbl`, `.act-in/.act-out/.act-cancel`, `.auto`, `.mtextarea`, `.qty`, `.qty-warn`, `.tag-pending`, `.tag-inbounded`, `.tag-exist`, `.tag-smartbuy`, `.tag-wholesale`, `.tag-partnership`, `.route-note`, `.row-exist`, `.thumb`, `.grp-gap`, `.status`, `.st-processing/.st-prepare/.st-hold/.st-missing`, `.chip-return`, `.comment-btn`, `.btn-green-line`, `.btn-red-line`, `.btn-gray`, `.bar-under`, `.modal .qrow`, `.inboxdd .empty`. **Do not delete `.toast.err`** — it is unused in the wireframe but is the specified failure variant (§3.9). Fix: delete together with `WF-10`.

### 2.6 Mandatory-inclusion map (the 12 owner-flagged items)

Codes per `_review.md` §2b: **P** = primary home · **Y** = lands materially · **Δ** = delta/cross-reference only · **n** = explicit N/A. No cell is silent.

| # | Mandatory item | This page | Where stated |
|---|---|---|---|
| 1 | Scanner protocol `[G-1]` | **n** | §1.5, `[BR-30]`, §7.8 |
| 2 | Confirmation toast `[G-2]` | **Y** | `[L-F1]` §3.9, `[L-M2]` §3.8, `[BR-34]` |
| 3 | Audio `[G-3]` | **n** | §1.5, §5.3, §7.8 — no outbound-class button exists |
| 4 | Instant print `[G-4]` | **n** | §1.5, `[BR-31]`, §6.5 |
| 5 | Sample dual-view `[G-13]` | **n** | §9.3 — no sample surface, no picking artifact, no invoice on this page |
| 6 | Unrecognized matching | **P** | `[L-2]`, `[L-3]`, `[L-M1]`, `[BR-5]`, `[DC-8]`/`[DC-9]`/`[DC-17]` |
| 7 | Multiple tracking numbers `[G-10]` | **Δ** | `[L-S1-Fb]`, §6.3 — one number is handed across at a time; accumulation is the Inbound Request's concern |
| 8 | RTO Korean names `[G-6]` | **Δ** | `[L-4]` §3.5, `[BR-14]` |
| 9 | Line-based location filter `[G-14]` | **n** | §9.3 — no location surface on this page |
| 10 | Audit-mode-only visibility `[G-14]` | **n** | §9.3 — no audit mode on this page |
| 11 | JIT residual stock | **n** | §9.3 — residual-stock accounting is Inventory's; this page never moves stock |
| 12 | Comment @mention routing `[G-7]` | **Y** | `[L-5]` §3.6, §6.1 rows 2–3, `[DC-20]`/`[DC-11]` |

---

## 3. Functional Specification

Conventions used below: **Trigger** → **Behavior** → **Inputs/Outputs** → **Validation** → **Server action** → **State transition** → **Idempotency** → **What the user sees**. Exact UI strings are quoted byte-accurately from the wireframe unless marked *(spec-authored)*.

### 3.1 `[L-0]` — Page identity and purpose declaration

**Trigger.** Navigating to the page (OMS Center menu; production route is a developer decision, §9.2 D-9).

**Rendered content (exact).**
- `<h2>`: `WMS - Unrecognized Tracking List` (hyphen-minus with single spaces, not an en dash).
- `.sub`: `Unrecognized & missing-tracking status` followed by a `.mut` continuation: `· Coupang creates the order number immediately but generates the tracking number a few hours later → unrecognized items are tracked here`.
- Browser `<title>` in the wireframe is `WMS 2.0 — Unrecognized Tracking Wireframe`; in the admin it becomes `WMS - Unrecognized Tracking List` *(spec-authored)*.

**Behavior.** Static. This unit declares the page's existence as a replacement for the manual set-aside process; it carries no interaction. It is a numbered unit because the *page itself* was a decision, and because its subtitle is the only on-screen statement of the Coupang timing gap that the whole flow exists to absorb.

**Server action.** On load, fetch the open pool (see `[L-1]`). No mutation.

**Data capture.** Page view is a declared non-event `[N-1]`.

### 3.2 `[L-1]` — Unrecognized product pool

#### 3.2.1 Header card (`.poolhead`)

**Rendered content (exact).**
- Bold amber lead: `⚠ Unrecognized product pool · ` + `<span id="poolCount">` + ` items`.
- Explanatory `.cnt` text, verbatim: `Physical products sent from View Orders after barcode recognition failure. The last-mile tracking number is auto-collected at scan time and shown together. The order number (Coupang purchase) is mostly "–" — items successfully matched by Coupang order-number lookup are already resolved at the registration step and never reach this pool. Suspected orders are auto-matched only from Processing orders that contain the product (multiple possible), mostly non-Coupang channels such as Naver and the official mall.` — with `<b>` on `tracking number is auto-collected`, on `The order number (Coupang purchase) is mostly "–"`, and on `Processing orders`.
- Visual: background `--hl #FFFBD6`, border `1.5px solid --hl-line #F59E0B`, radius 8 px. A load-bearing attention signal, not styling (§1.4).

**`#poolCount` contract.** Equals the number of **OPEN** pool items, equals the number of rendered `<tbody>` rows, equals `#poolCountBottom` `[L-F2]`. This three-way equality is invariant after **every** mutation — match, removal, live arrival `[BR-33]`, `[E-20]`. Both counters are derived from the **rendered row collection**, never from the response length `[BR-41]`, `[E-72]`.

#### 3.2.2 Table column contract (12 columns, left → right)

Header row is `.tbl th` (dark `--ink` background, white text, `white-space:nowrap`). Header strings are exact.

| # | Header (exact) | Source | Format / semantics | Editable? |
|---|---|---|---|---|
| 1 | `Tracking No` | Auto-collected by the View Orders scanner at scan time; carried on the intake payload | `.num` tabular figures, digits only, no grouping (e.g. `10323100841207`). Nullability is undecided — see `[PD-66 · OWNER-PENDING]` and §9.1. **Namespace:** the number is stored with the namespace the scan originated in — `outbound` for a customer parcel, `inbound` for an unrequested supplier arrival `[BR-11]` — and the uniqueness guard `[BR-19]`, `[E-11]` is evaluated **within that namespace only**. A pool item whose number is `inbound` therefore does **not** collide with an identical `outbound` number, which is exactly the configuration `[E-33]` describes (an unrequested-inbound parcel matched to a customer order): the namespace check is silent there by design, so `[E-33]`'s only defence remains the memo surfaced in `[L-M1]` *(spec-authored)* | Read-only |
| 2 | `Order No` | The Coupang purchase order number typed by the registrant in the View Orders lookup popup (M2), carried only when the lookup **failed** | `.num`, `--ink-3` gray. Renders the literal `–` (en dash U+2013) when absent, which is the normal case `[BR-12]`. A present value is **display-only context** and never influences candidate computation `[E-2]`, `[E-68]` | Read-only |
| 3 | `Product Name` | The catalog product chosen by autocomplete in View Orders M2b, snapshotted at intake `[BR-43]` | Brand in `<b>` + space + English name + `, ` + size suffix, e.g. `COSRX Advanced Snail 96 Mucin Power Essence, 100ml` with `COSRX` bold `[L-4]` | Read-only |
| 4 | `Product Name KR` | Catalog Korean name for the same product, snapshotted at intake | Korean name with the English brand in bold, e.g. `COSRX 어드밴스드 스네일 96 뮤신 에센스` with `COSRX` bold `[G-6]` | Read-only |
| 5 | `Size` | Catalog, snapshotted | Free-form unit string as stored: `100ml`, `250ml`, `70ea` | Read-only |
| 6 | `Barcode` | The barcode that failed to resolve at the bench | `.num`, digits only, e.g. `8809416470726`. This is the **match key** for candidate computation `[L-2]` | Read-only |
| 7 | `Qty` | Registrant's entry in View Orders M2b | `.num` integer ≥ 1. `2` in the `medicube` 1+1 row | Read-only |
| 8 | `Memo` | Registrant's optional free text in M2b | `.mut` gray. Renders the literal `–` when empty. The registrant→resolver channel (§1.3). Rendered as escaped plain text; wraps; never truncated with an ellipsis *(spec-authored)* `[E-45]` | Read-only after registration; corrections are posted as comments `[BR-27]` |
| 9 | `Registrant (Center)` | Authenticated user who pressed Send in M2b | Display name (`Miranti`, `Dean`). The header's `(Center)` states that this actor is warehouse staff | Read-only |
| 10 | `Registered At` | Server timestamp of intake | `.num`, `MM-DD HH:mm` in **KST** (`07-13 10:12`). Since the 2026-07-23 removal of wait chips this is the **only** age signal on the page `[PD-61 · OWNER-PENDING]`, `[E-65]` | Read-only |
| 11 | `Suspected Orders (Auto-matched)` | Computed — see `[L-2]` | Multi-line block, 12 px / 1.5 line-height | Read-only |
| 12 | `Action` | — | `Review & Match` + `✕`, `white-space:nowrap` — see `[L-3]` | — |

#### 3.2.3 Row rendering

- Every open row carries class `.row-hit`: cell background `--hl`, plus a 2 px `--hl-line` top and bottom border. Rows are **always** highlighted while open; the highlight is not a selection state and there is no un-highlighted open-row variant `[BR-36]`.
- **Row ordering:** newest first by `Registered At` descending *(spec-authored; the wireframe's seed rows are 10:12 / 09:48 / 09:30, consistent with this rule)*. No user-controllable sort — sorting UI was part of the 2026-07-23 removal `[BR-16]`.
- **Row identity:** stable `pool_item_id`. The wireframe uses `id="poolrow1"` on the first row only; the admin gives every row `id="poolrow-{pool_item_id}"` *(spec-authored)* so a Comments deep link can target one `[PD-67 · OWNER-PENDING]`.
- **No pagination and no virtualization.** The pool is expected to hold single-digit counts. If it grows past the design assumption the table scrolls plainly `[E-30]`; this is explicitly **not** a reason to re-add the search bar `[BR-16]`.
- **Horizontal overflow.** The table lives inside `.mockwrap` (`overflow-x:auto`) with a `min-width:1280px` canvas. Below that width the table scrolls horizontally; no column is hidden or collapsed, and the `Action` column always remains reachable `[E-63]`.

#### 3.2.4 Empty state

Not drawn in the wireframe (§2.4.5). Required behavior *(spec-authored copy)*:

- `#poolCount` and `#poolCountBottom` both read `0`.
- The `.poolhead` card remains rendered (it explains the page); its lead reads `⚠ Unrecognized product pool · 0 items`.
- The table renders its header row plus one full-width body row containing: `No unrecognized items. Products sent from View Orders after a barcode recognition failure appear here.`
- Layout must not collapse; the table keeps its column widths `[E-19]`.
- A live arrival into an empty pool replaces the empty-state row with the real row and both counters read `1` `[E-21]`.

#### 3.2.5 Live arrival and post-mutation recompute

- A new pool item created upstream while a resolver has the page open **must appear without a full-page refresh** `[G-2]`. Transport (poll interval vs. push) is a developer decision (§9.2 D-2). On arrival the row is inserted at the top, both counts increment, and the three-way invariant holds `[E-21]`.
- **After any match or removal, the candidate cells of the remaining rows are recomputed** `[BR-38]`, `[DC-6]`, so no row keeps offering a line that a sibling row has just consumed. If a resolver acts on a stale cell anyway, the server blocks it `[E-10]`, `[E-51]`.

#### 3.2.6 Load failure

If the pool fetch fails, the page renders an error state with a retry affordance — never a blank table and never a silent `0 items`, which would be indistinguishable from a healthy empty pool `[E-28]`. The failure is persisted `[DC-25]`.

### 3.3 `[L-2]` — Suspected Orders (auto-matched)

**Purpose.** This column *is* the 2026-07-23 UX inversion `[BR-2]`. It converts a search problem into a confirmation problem.

**Candidate predicate (normative, testable).** An order O is a candidate for pool item P if and only if:

```
O.status == Processing
AND ∃ line L ∈ O.lines : L.product.barcode == P.barcode
```

Consequences that must be honored:

- **Both conditions are hard.** No channel filter, no PIC filter, no date window, no fuzzy product matching. Coupang orders are effectively absent because the M2 order-number lookup already resolved them upstream — an emergent property of the flow, **not** an explicit exclusion rule `[BR-3]`.
- **Multiple candidates are normal and expected.** `#poolrow1` in the wireframe carries two.
- **Zero candidates is a legitimate outcome** and means the upstream order data is wrong `[BR-4]`, `[PD-62 · OWNER-PENDING]`.
- The match target is a **product line**, so an order that contains the SKU on two separate lines yields **two** candidate entries, not one `[E-13]`.
- A missing PIC never removes an order from the set `[E-34]`. A missing barcode on a candidate line simply never matches `[E-69]`.
- If two catalog products share one barcode, lines of both appear; the `Included Product` cell is what disambiguates them `[E-47]`.

**Rendering, per candidate, exact format:**

```
{PIC in <b>} · {"Order " + order_no, blue --blue #0D6EFD, font-weight 700, .num} · {route (channel) · status — one trailing <span class="mut">, --ink-3 #7E7C83, non-bold}
```

The route and the status share **one** `.mut` span; they are not two separately styled fragments. This is the load-bearing detail behind the `[G-5]` page delta below.

Live examples from the wireframe:
- `Dean · Order 414230 · JIT (Naver) · Processing`
- `Egita · Order 413871 · JIT (Official Mall) · Processing`
- `Harshit · Order 414102 · JIT (Naver) · Processing`
- `Miranti · Order 413998 · JIT (Official Mall) · Processing`

**Route label rendering — declared page delta on `[G-5]` (decided 2026-08-03).** This page renders the route in **two structurally different places**, and `[G-5]`'s badge contract governs only one of them:

| Surface | Form | Computed rendering | Governed by |
|---|---|---|---|
| `[L-M1]`'s `Channel` cell | **Badge** — `<span class="tag tag-jit">JIT (Naver)</span>` | `background:transparent`, `padding:0`, `font-weight:800`, `color:var(--ink)` = `rgb(20, 16, 27)` | `[G-5]` in full: colorless **bold black**, never a coloured pill. Asserted by QA-M1-10 |
| `[L-2]`'s pool cell | **Running text** — the trailing `<span class="mut">JIT (Naver) · Processing</span>` of a compound candidate sentence | `background:transparent`, no border, `padding:0`, non-bold, `color:var(--ink-3)` = `rgb(126, 124, 131)` | `[G-5]`'s **"never a coloured pill"** half applies and is a hard requirement. `[G-5]`'s **bold-black** half does **not** apply — page delta, see below. Asserted by QA-SUS-05 |

**Why the delta.** `[G-5]`'s consumer list is *View Orders badges, Inventory, Order Detail* — this page is not on it, and the pool cell does not render a badge at all. The route there is one clause inside `{PIC} · {Order no.} · {route (channel)} · {status}`, a sentence in which the **order number** is the emphasized element (blue, 700). Rendering the route bold black inside that sentence would create a second competing emphasis and would require splitting a span that also carries the status. So on this page the badge contract lands on M1's `Channel` cell only; the pool cell's route is muted running text (`--ink-3`, non-bold), and the never-a-pill prohibition holds on both. **Decided 2026-08-03; rationale: the candidate line is a compound sentence, not a badge.** Reversal impact if the owner rejects the delta: change the format line above to render the route fragment `--ink` bold, split the `.mut` span in all four pool candidate lines (a new wireframe defect), and re-tag QA-SUS-05's colour clause `[ADMIN]` with a `[WF]` counterpart in §8.15. Nothing else changes.

An `OTHER`-route order renders `OTHER ({channel name})` in whichever of the two forms its surface uses `[PD-80 · OWNER-PENDING]`. The route originates in the Inbound Request and is matched via the invoice number; this page only displays it `[BR-15]`.

**Order number must be a real link** to the order `[G-12]`, `[BR-37]` — currently defect `WF-NEW-B`.

**Status token.** Always `Processing` by construction of the predicate. It is nonetheless rendered rather than implied, so a stale client list is visually detectable.

**Empty rendering** *(spec-authored copy, per `[PD-62 · OWNER-PENDING]`)*: the cell shows `No Processing order contains this product — check the order data upstream, or remove with a reason.` No search affordance is offered `[E-5]`.

**Volume.** All candidates render; there is no truncation, no "show more", and no pagination `[E-53]`. The Slack payload's `suspected_orders` list may be capped with an explicit `+N more` suffix so the message stays deliverable; the cap value is a developer decision (§9.2).

**Recompute timing.** The candidate set is computed at intake `[DC-5]` and recomputed at least on (a) page load, (b) M1 open, (c) server-side whenever an order enters or leaves `Processing`, and (d) after any match or removal on this page `[DC-6]`, `[BR-38]`. The trigger mechanism is a developer decision (§9.2 D-1). Because candidates can appear *after* registration `[E-40]` and disappear before confirm `[E-6]`, `[E-48]`, the server **always revalidates at confirm** `[PD-6 · OWNER-PENDING]`.

**Registration-time Slack.** At intake the automatic `#unrecognized-tracking` message @mentions the suspected PICs computed at that moment `[BR-6]`, `[DC-4]`, each PIC exactly once even when they own several candidate orders `[BR-39]`, `[E-52]`. The message is fired by View Orders; this page is its destination. See §6.1.

### 3.4 `[L-3]` — Action column: Review & Match, and ✕

Two independent controls in one `white-space:nowrap` cell.

#### 3.4.1 Button: `Review & Match`

- **Exact label:** `Review & Match` (rendered from `Review &amp; Match`). Classes `btn btn-blue btn-sm`; blue `--blue #0D6EFD`, white text, 12.5 px, radius 7 px.
- **Enabled condition:** always enabled while the row's pool item is `OPEN`. There is no disabled variant, including when the candidate list is empty — a resolver must be able to open M1 to read the memo and the empty-state guidance `[E-5]`.
- **Trigger:** click, or `Enter`/`Space` when focused `[E-62]`.
- **Effect:** opens `[L-M1]` **scoped to that row's `pool_item_id`**. The admin must pass the row identity; the wireframe's hard-wiring to row 1 is a demo limitation (§2.4.1).
- **Server action on open:** re-run the candidate predicate for that item and persist the returned set `[DC-7]`. This snapshot is what a later stale-candidate rejection is diffed against.
- **State transition:** none. Opening the modal never mutates the pool item.
- **Idempotency:** opening twice is harmless; each open persists its own `[DC-7]` and only the latest snapshot is authoritative for that session.
- **Feedback:** the overlay `#m-match` gains class `open` (flex, `rgba(10,6,20,.55)` backdrop) and focus moves into the modal `[BR-40]`. No toast — opening a modal is not a confirming action `[G-2]`.

#### 3.4.2 Button: `✕` (remove from list)

- **Exact label:** `✕` (U+2715). `title="Remove from list"`. Classes `btn btn-line btn-sm xdel` with inline `border-color:var(--red); color:var(--red); padding:5px 9px`. The admin additionally supplies an accessible name `[E-62]`.
- **Purpose:** cleanup for **mis-registrations**, **no-action items**, and the **unrequested-inbound handoff** step `[BR-8]`, `[BR-11]`.
- **Enabled condition:** always enabled while the item is `OPEN`.
- **Trigger:** click, or `Enter`/`Space` when focused.
- **Effect (wireframe and spec agree since 2026-08-03):** opens the confirm modal `[L-M2]` — it does **not** remove the row directly. The wireframe's former immediate removal was gap `WF-6`, closed by the 2026-08-03 wireframe pass; `[G-2]` with `[GD-5]`, `[G-8]`, and the `[G-11]` reason precedent all pointed the same way, and the owner confirmed the rule `[PD-60 · CONFIRMED 2026-08-03]`, `[PD-5 · CONFIRMED 2026-08-03]`.
- **Removal is always a soft delete.** Status `OPEN → REMOVED`; the full row snapshot is persisted permanently `[DC-14]`. Nothing on this page is ever hard-deleted `[G-8]`.
- **Idempotency:** double-click is debounced client-side and rejected server-side by an idempotency key `[G-9]`; the suppressed second attempt is logged `[DC-16]`.

#### 3.4.3 The match server action (atomic core + non-blocking tail)

Triggered from `[L-M1]`'s per-candidate button, specified here because it is `[L-3]`'s semantic payload and the page's single most important behavior `[BR-5]`.

**Ordered steps. Steps 1–3 are one atomic transaction; steps 4–6 are non-blocking side effects that never roll back 1–3** `[PD-4 · OWNER-PENDING]`.

1. **Revalidate.** All of: the pool item is still `OPEN`; the candidate order still exists and is still `Processing`; the chosen product line still exists on it; the target line does not already carry a tracking number `[E-10]`; the tracking number is not already bound to a different order line in the same namespace `[E-11]`, `[PD-8 · OWNER-PENDING]`. Any failure → reject, **no writes of any kind**, red toast, refresh the candidate list `[PD-6 · OWNER-PENDING]`, `[DC-13]`.
2. **Write the tracking number onto the selected order product line** — into the *same field the View Orders scan path reads*, so that rescanning the barcode resolves normally afterwards `[BR-5]`, `[DC-9]`. This is the whole point of the flow (mandatory inclusion #6) and a cross-spec contract `[E-15]`, §6.3.
3. **Close the pool item.** Status `OPEN → MATCHED`, recording resolver, resolved timestamp, chosen `order_id` + `line_id`, and the candidate-set snapshot in force at confirm `[DC-8]`. Resolution latency (intake → resolve) must be derivable from `[DC-1]` and `[DC-8]` without extra instrumentation `[BR-35]`.
4. **Auto-post a comment on the order**, `source=system`, @mentioning the **registrant** (not the resolver) `[DC-10]`, `[BR-7]`. Body (wireframe form): `@{registrant} (unrecognized registrant) Matched the unrecognized product ({product}) to this order`. When pool qty ≠ line qty, the comment additionally states the mismatch, e.g. `registered qty 2 against a ×1 line` `[PD-65 · OWNER-PENDING]`.
5. **Dispatch the mention to Slack** → `#fulfillment-admin-comments` (`C0BMGEWM5QA`) `[DC-11]`. Suppressed when resolver == registrant, with the comment still posted `[PD-16 · OWNER-PENDING]`, `[DC-27]`, `[E-54]`.
6. **Refresh the client:** close the modal, remove the row, decrement both counts, recompute the remaining rows' candidate cells `[BR-38]`, and show the success toast `[L-F1]`. **No full-page refresh** `[G-2]`.

**Idempotency key = `pool_item_id + line_id`** `[G-9]`. A duplicate confirm produces exactly one line write, one pool closure, one comment, one Slack message; the suppressed attempt is logged `[DC-12]`, `[E-9]`. The key always includes `pool_item_id`, so two different pool items can never share a key `[E-67]`.

**Concurrency.** Two resolvers on the same item: optimistic version check, the loser gets a 409 → non-green toast + row/list reload `[PD-7 · OWNER-PENDING]`, `[E-7]`. A match racing a removal resolves to exactly one terminal state `[E-8]`.

### 3.5 `[L-4]` — Brand-prefixed product naming

**Page delta over `[G-6]`.** The brand is rendered in `<b>` at the front of the product name on **every** surface this page owns: the `Product Name` column, the `Product Name KR` column, the `[L-M1]` summary card, the M1 `Included Product` cells, the auto-comment body, and the toast text.

**Catalog casing is preserved verbatim** and the two columns may legitimately differ — the wireframe's third row shows `medicube` in the English column and `Medicube` in the Korean column. The admin does not normalize casing *(spec-authored)*.

**Korean strings** on this page (`어드밴스드 스네일 96 뮤신 에센스`, `어성초 77% 수딩 토너`, `제로 모공 패드 2.0 (1+1)`) are data `[G-6]`.

**Rationale.** The resolver is judging a product they cannot see. The brand is the fastest discriminator; the Korean name is what the bench staff and their memos actually say (§1.4). Inherited from the View Orders decision B, reconfirmed 2026-08-03 `[BR-14]`.

**Missing Korean name.** If the catalog has no Korean name for a SKU, the KR cell renders `–` in `.mut` and never falls back to the English string *(spec-authored)* `[E-44]`.

### 3.6 `[L-5]` — Comments hub

Cited by reference to `[G-7]`; only page deltas are specified here.

**Location and chrome.** Top-right of the nav: `<button class="icon-btn" data-open="inbox1">💬 Comments<span class="badge-n">3</span></button>`. The dropdown `#inbox1` is 370 px wide, anchored `top:46px; right:110px`.

**Tabs.** `@ Mentions` (with an inline count badge, `3` in the wireframe) and `★ Saved`.

**Pane headers — canonical since the 2026-08-03 wireframe pass (`WF-NEW-E` fixed on this page).** The wireframe now ships the corpus-canonical four-page-majority strings, so the `[WF]` and `[ADMIN]` tiers assert the same values:

| Element | String (wireframe = admin) |
|---|---|
| Mentions pane header | `Comments mentioning me · Click to open the order` |
| Saved pane header | `Saved comments · Click to open the order` |
| Unstar hint | `Unstar to remove from the list` |
| Read-all action | `Mark all read` |

QA-CMT-03 / QA-CMT-05 (`[WF]`) are re-baselined to these strings and QA-CMT-15 (`[ADMIN]`) is unchanged. The corpus-wide half of `WF-NEW-E` — publishing the six hub strings in `[G-7]` as byte-exact contract so the other divergent pages can converge — remains open (cross-page defect m3a D7); when that amendment lands, the global text supersedes this table. `Mark all read` is right-aligned and blue.

**Badge semantics.** `.badge-n` on the button = **unread mention count**, not item count. The wireframe correctly shows badge `3` against 4 rendered mention items (three `.unread`, one read) — intended, not a defect. Counts above 99 render `99+` while the persisted count stays exact `[E-55]`.

**Search — page delta / defect.** `[G-7]` and legend 5 both require full-text search across all comments (entity no. / author / text), newest first, click opens the entity. The dropdown markup on this page is missing that input (`WF-NEW-A`). The admin must ship it; the query is persisted `[DC-23]`.

**Page delta #1 — pool items are a first-class commentable entity type.** The hub already renders `Unrecognized pool · Miranti: "@Yongwon Left a memo on the Snail essence (box label damaged). Please check whose order this is"` at `10:12`, starred. The entity label for a pool-item comment is the literal string `Unrecognized pool` rather than an order number `[G-7]`.

**Page delta #2 — click target for pool-entity comments.** Clicking such an entry opens **this page focused on that pool row** (`#poolrow-{pool_item_id}`); if the item is no longer `OPEN`, it opens the **matched order** instead `[PD-67 · OWNER-PENDING]`, `[E-31]`. Comments whose entity is an order behave normally and open the order.

**Dismissal.** The dropdown closes on an outside click and on `Esc` *(spec-authored; the wireframe binds neither — §2.4.8)* `[BR-40]`, `[E-56]`. Neither is a persisted event `[N-3]`.

**Append-only.** Comments cannot be edited or deleted anywhere, including on pool items; corrections are new comments `[PD-3 · OWNER-PENDING]`, `[BR-27]`. A removed pool item keeps its comments `[E-60]`.

**Star toggle.** `.star` toggles `on` (gold `--star #F59E0B`); persisted per user `[DC-21]`. Starring is a per-user state, not a shared flag.

**Mark all read.** Bulk-clears unread state for the current user and zeroes the badge `[DC-22]`.

### 3.7 `[L-M1]` — Modal "Review & Match — Unrecognized Product"

**Element.** `#m-match`, `.overlay` → `.modal` with `max-width:700px`. Opens by gaining class `open`.

**Header (exact).** `Review & Match — Unrecognized Product` (em dash), with a right-aligned `✕` close button (`.x`, `data-close`).

**Body — three blocks, top to bottom.**

**(a) Item summary card.** Yellow (`--hl` background, `--hl-line` border, radius 8 px), mirroring the pool row so the resolver knows the modal is scoped to the row they clicked. Content, in order, with the wireframe's exact separators:

- Line 1: brand-bold product name — `COSRX Advanced Snail 96 Mucin Power Essence, 100ml` (`COSRX` in `<b>`)
- Line 2 (`.mut`, 12 px): `Barcode 8809416470726 · Tracking 10323100841207 · No order number · 1 unit · Registered by: Miranti (Center) 07-13 10:12 · Memo "Box label damaged"`

Field sources and fallbacks:

| Fragment | Source | When absent |
|---|---|---|
| `Barcode {n}` | pool item barcode | always present |
| `Tracking {n}` | pool item tracking no. | undecided — `[PD-66 · OWNER-PENDING]`, §9.1 |
| `No order number` | literal, when Order No is `–` | when an order number *is* present, renders `Order no. {n}` *(spec-authored)* `[E-2]` |
| `{n} unit` / `{n} units` | pool item qty | always present; singular/plural per value *(spec-authored)* |
| `Registered by: {name} ({center}) {MM-DD HH:mm}` | registrant + timestamp | always present |
| `Memo "{text}"` | memo | the whole `· Memo "…"` fragment is omitted when the memo is empty *(spec-authored)* |

The memo fragment is never hidden, collapsed, or truncated — it is the registrant's only channel and carries the `suspected inbound stock` signal that prevents `[E-33]`.

**(b) Candidate panel.** Green frame (`1.5px solid --green #198754`, `--green-soft #D1E7DD` fill, radius 10 px).

- Heading (exact): `Suspected orders (auto-matched)` followed by `.mut`: `— only Processing orders containing this product are shown as candidates (multiple possible). Match by selecting a product line, not the order`.
- Table headers (exact, 5 columns, last empty): `Order` · `PIC` · `Channel` · `Included Product` · *(blank)*.
- Row rendering: Order no. in blue bold `.num`; PIC plain (or `–` when unassigned `[E-34]`); Channel as a black bold route label `[G-5]` (`JIT (Naver)`, `JIT (Official Mall)`); Included Product as brand-bold name + ` ×{qty}` (`COSRX Snail 96 Essence ×1`); action cell = the match button.
- **One row per product LINE**, not per order `[BR-5]`, `[E-13]`.
- **Volume:** all candidate lines render; the table scrolls inside the modal body when long. No pagination, no truncation `[E-53]`.
- **Empty rendering** *(spec-authored, per `[PD-62 · OWNER-PENDING]`)*: the table is replaced by `No Processing order contains this product — check the order data upstream, or remove with a reason.` The panel border stays green so the modal does not read as an error.

**(c) Consequence note.** `.note` (blue-soft), exact text: `On match confirmation — tracking number 10323100841207 is registered to the selected product line, this item disappears from the pool, and it is automatically posted to the order's Comments: "@Miranti (unrecognized registrant) Matched the unrecognized product (COSRX Snail 96 Essence) to this order" → Slack notification to the registrant.` In the admin the numbers and names are interpolated from the scoped item and the selected candidate. This note is normative: it is the user-facing contract for §3.4.3.

**Footer.** A single `Cancel` button (`btn btn-line btn-sm`, `data-close`). **There is deliberately no modal-level confirm button** — the per-candidate button *is* the confirming action.

**Per-candidate button.**
- **Exact label:** `Match to this product`. Classes `btn btn-green btn-sm pmatch`.
- **Enabled condition:** enabled for every rendered candidate line. Disabled only while a confirm is in flight (pending state) `[E-25]`.
- **Effect:** executes §3.4.3 for that `line_id`.
- **Feedback on success:** modal closes (`open` removed), the pool row disappears, both counts decrement, toast fires `[L-F1]`.
- **Feedback on rejection:** modal stays open, a **red** toast (`.toast.err`, `--red #DC3545`) states the reason, and the candidate list refreshes in place `[PD-6 · OWNER-PENDING]`.

**Close paths — all four are side-effect free** `[E-24]`:
1. `Cancel` in the footer,
2. the header `✕`,
3. clicking the overlay backdrop (the handler fires only when `e.target === overlay`),
4. `Esc` *(spec-authored; the wireframe does not bind it)*.

None mutates the pool item, posts a comment, or emits any event beyond the already-persisted `[DC-7]` open snapshot `[N-7]`. On close, focus returns to the `Review & Match` button that opened the modal `[BR-40]`, `[E-62]`.

### 3.8 `[L-M2]` — Modal "Remove this item from the pool?" (`#m-remove`)

Mandated by `[PD-60 · CONFIRMED 2026-08-03]` and `[PD-5 · CONFIRMED 2026-08-03]` (owner confirmation: **every** removal/deletion gets a confirm dialog and a toast); former wireframe gap `WF-6`, **closed 2026-08-03** — the wireframe now ships this modal, and the quoted copy below is byte-accurate to it. The reason list is the owner-confirmed enum (`Registered by mistake` / `No action needed` / `Other` + memo) **plus** `Routed to inbound request`, retained so `[PD-64 · OWNER-PENDING]`'s structured Inbound No. capture and the `[BR-11]` unrequested-inbound route stay mountable.

**Trigger.** The row's `✕` (in the wireframe, also the wf-bar demo button `Modal: Remove Confirm (M2)` — chrome, §2.3).

**Header.** `Remove this item from the pool?` *(owner-confirmed string)*.

**Body.**
1. An item summary card (`#rmSummary`, yellow `--hl` / `--hl-line`, mirroring `[L-M1]`'s card) scoped to the clicked row: brand-bold product name, then a `.mut` line `Tracking {n} · Qty {n} · Registered by: {name} (Center) {MM-DD HH:mm}`; the `· Memo "{text}"` fragment is appended when a memo exists and shown in full, omitted when the memo is `–`.
2. **Reason** — a required `<select>` (`#rmReason`), default unselected (`Select a reason…`). Options, exactly and in this order:
   - `Registered by mistake`
   - `Routed to inbound request`
   - `No action needed`
   - `Other`
3. **Inbound No.** — a text input (`#rmInbound`, placeholder `YYYYMMDDNNNN`) that appears **only** when reason == `Routed to inbound request`. Format `YYYYMMDDNNNN` (the Inbound Request auto-numbering scheme). Validated for format when filled. It is **not** mandatory and its absence does **not** block removal `[PD-64 · OWNER-PENDING]`.
4. **Memo** — free text (`#rmMemo`, `.mtextarea`), persisted with the removal event. Optional for every reason **except `Other`, where it is required** (the owner enum is "Other + memo": an `Other` removal without a stated why would defeat `[G-8]`'s purpose).

**Footer.** `Cancel` (`btn btn-line btn-sm`) · `Remove from pool` (`#rmConfirm`, `btn btn-red btn-sm`, destructive styling).

**Validation.** `Remove from pool` stays disabled until a reason is selected. Selecting `Routed to inbound request` and typing a malformed Inbound No. shows inline `Inbound No. must be 12 digits (YYYYMMDDNNNN)` and disables the button until corrected or cleared. Selecting `Other` disables the button until the memo is non-empty. **Existence of the referenced request is not a gate** `[E-35]`, `[E-70]`.

**On confirm.**
- Server: soft-delete — status `OPEN → REMOVED`, persisting actor, timestamp, reason, optional Inbound No., memo, and the **full row snapshot** `[DC-14]`, `[G-8]`.
- When an Inbound No. was supplied, a reciprocal link is written on the inbound request so the Inbound Request page can show provenance `[DC-15]`.
- **A comment is auto-posted on the pool item entity** (`source=system`, `[G-7]` — pool items are first-class commentable): `Removed from pool — {reason}` plus the Inbound No. and memo when present `[DC-29]` *(spec-authored body)*. It carries **no @mention**, so no Slack dispatch fires — consistent with §6.1's "no Slack route for removals". The removal is thereby readable in the Comments hub without querying events.
- Client: modal closes, the row is removed, both counts decrement, the remaining rows' candidate cells recompute `[BR-38]`, and a **green toast** fires `[L-F1]`: `✓ Removed from pool · {product}` with sub-line `Reason: {reason} · Tracking {trk}` *(wireframe-implemented; the lead string `✓ Removed from pool` is the owner-confirmed copy)*.
- **No full-page refresh** `[G-2]`.
- Idempotency key = `pool_item_id + "remove"`; duplicates suppressed and logged `[DC-16]`, `[G-9]`. The wireframe's confirm handler carries the client half of this guard: it decrements only when the captured row was still attached (`WF-NEW-D` fix, §2.4.10).
- Comments already attached to the item survive the soft delete `[E-60]`.

**On cancel.** Zero side effects; declared non-event `[N-6]`. Focus returns to the `✕` that opened it `[BR-40]`. All three wireframe close paths (`Cancel`, header `✕`, overlay backdrop) leave the pool and both counters untouched; the admin adds `Esc` (§3.14).

**No hard guard on ordering.** Removing an item whose memo says `suspected inbound stock` before the inbound request actually exists is **not** blocked. The expected order of operations (create request → enter invoice no. → remove → rescan) stays procedural, and the structured Inbound No. field is what makes an out-of-order removal auditable and recoverable `[PD-64 · OWNER-PENDING]`, `[E-17]`.

### 3.9 `[L-F1]` — Toast surface

- **Element:** `#matchToast`, inline `position:fixed; top:18px; right:18px`, `z-index:50`, radius 8 px, `--shadow`. Hidden (`display:none`) until an action fires it.
- **Success variant:** green `--green #198754`, white text. Two parts in one flex row: a bold `<span>` and a `<small>` at `opacity:.85; font-weight:400`.
- **Failure variant:** `.toast.err`, red `--red #DC3545`. The class exists in the stylesheet and is unused in the wireframe; the admin uses it for every rejection path `[G-2]`. **It must not be deleted with the dead CSS** (§2.5 `WF-NEW-C`).
- **Match success text (exact, wireframe seed values):**
  - line 1: `✓ Matched to Order 414230 · COSRX Snail 96`
  - line 2: `Tracking 10323100841207 registered · removed from pool · @Miranti notified via Slack`
  - Admin form: `✓ Matched to Order {order_no} · {short product name}` / `Tracking {tracking_no} registered · removed from pool · @{registrant} notified via Slack`.
- **Removal success text** (§3.8, wireframe-implemented 2026-08-03): line 1 `✓ Removed from pool · {product}`, line 2 `Reason: {reason} · Tracking {tracking_no}`. In the wireframe both actions share the single `#matchToast` element and the script writes the per-action content before showing it; the static markup keeps the match strings as its baseline.
- **Duration:** 4000 ms then hidden (`setTimeout` in `finishMatch()`). Auto-dismiss is not click-blocking — the toast is `position:fixed` in a corner and never overlays the table's Action column `[E-23]`.
- **Stacking:** two confirming actions within the window must not silently overwrite each other mid-read; both texts must be readable. Stack-vs-queue is a developer decision (§9.2 D-4) `[E-22]`.
- **Announcement:** the toast region is an ARIA live region so a keyboard-only operator is not required to watch the corner *(spec-authored page delta on `[G-2]`)* `[E-62]`.
- Toast display is a declared non-event `[N-5]` — the underlying action is what persists.

### 3.10 `[L-F2]` — Bottom count line

- Exact markup: `Unrecognized pool · <span id="poolCountBottom">3</span> items`, `.mut` gray, `margin-top:16px`.
- Kept in lockstep with `#poolCount` by `poolDec()`; the admin must maintain the same invariant on **every** mutation path including live arrivals `[BR-33]`, `[E-20]`, and must derive it from rendered rows `[BR-41]`, `[E-72]`.
- Purpose: the table can be long enough to push the header card off-screen; the resolver needs the count where they stop reading.

### 3.11 `[L-F3]` — Top nav bar and Comments badge

- Dark bar (`--nav #212529`), brand `SkinSeoul`, menu labels `Operation AI ▾` · `Catalog Management ▾` · `OMS Center ▾` · `Site Management ▾`, then right-aligned: the Comments button `[L-5]`, the user block (`<span class="avatar">Y</span>Yongwon Ryu`), and `Logout`.
- Shared chrome across all eight screens; specified here only so that the unread badge's placement and semantics are anchored to a unit ID.
- **Permissions:** v1 ships a single admin role `[G-15]`, `[PD-1 · OWNER-PENDING]` — no control on this page is role-gated, and the actor is recorded on every mutation `[E-29]`.

### 3.12 `[L-S1-Fa]` — Off-screen footer: the 2026-07-23 simplification record

This legend paragraph is **normative in the negative**. It is the authoritative list of features that were deliberately removed and **must not exist** in the implementation:

| Removed feature | Must NOT exist | Decision |
|---|---|---|
| Per-PIC group tables (grouped rows under a PIC avatar/name header with a count chip) | No grouping, no `.picava` / `.picname` / `.cntchip` UI | 2026-07-23 |
| Bulk-action bar | No multi-select, no checkboxes, no bulk match, no bulk remove | 2026-07-23 |
| "Slack notified" column and its pill | Slack dispatch is persisted `[DC-4]` but never surfaced as a column | 2026-07-23 |
| Resolved-completion log section | No on-page resolved list; the **data** is retained admin-side as a view over persisted events `[G-8]`, `[DC-8]`, `[DC-14]` | 2026-07-23 |
| Unified search bar | No search input on this page (the Comments-hub search in `[L-5]` is a different, required thing) | 2026-07-23 |
| In-page register button and modal | Registration exists only in View Orders M2b `[BR-1]` | 2026-07-23 |
| Second page state (State 2) | The page is single-state | 2026-07-23 |
| Wait-time chips (`.wait`, green/amber/red aging pills) | No on-page aging visual; aging is handled by the daily digest `[PD-61 · OWNER-PENDING]` | 2026-07-23 |
| Manual PIC-search fallback ("find directly") | No manual search, no PIC dropdown, no free-text order lookup `[BR-4]` | 2026-07-23 (commit `e43ce68`) |
| Photo capture / photo column | No photo upload, no photo column, no thumbnail, anywhere on this page. **Permanently removed, not deferred** `[PD-63 · OWNER-PENDING]` | 2026-07-21 hold → 2026-08-03 deletion (review item 15) |

The same paragraph also states the **UX inversion** (`[BR-2]`) and the reason the manual fallback went away: since candidates are the complete "contains the product + Processing" set, a fallback search cannot find anything the list does not already contain.

### 3.13 `[L-S1-Fb]` — Off-screen footer: flow summary and the unrequested-inbound route

**Normative five-step flow** (cross-page; this page owns steps 4–5):

1. View Orders barcode recognition fails → **order-number lookup popup** (M2).
2. **(2a)** Lookup matches → the tracking number is matched and registered on the spot. The item **never enters this pool**, and rescanning recognizes it normally. **(2b)** No order number, or lookup fails → send-to-unrecognized modal (M2b: English product-name autocomplete · quantity · memo).
3. Automatic `#unrecognized-tracking` notification, @mentioning the suspected PICs.
4. The item appears in **this page's** pool with its tracking number and its suspected orders (`contains the product + Processing`, multiple possible).
5. The responsible PIC reviews and matches via **Review & Match** (M1) → item removed from the pool + the registrant is @mentioned in a comment automatically posted to the order's Comments.

**Unrequested inbound route (confirmed 2026-08-02)** `[BR-11]`, `[G-10]` cross-reference:

When the invoice scan of arrived stock matches **neither a customer order nor an inbound request**, it is sent to the unrecognized pool the same way. The owner then:
1. creates an Inbound Request on the Inbound Request page,
2. enters the invoice (tracking) number on it,
3. removes the pool row with reason `Routed to inbound request`, capturing the Inbound No. `[PD-64 · OWNER-PENDING]`,
4. rescans — the scan now enters the View Orders **internal-inbound screen (State 6)** normally.

Leaving a `suspected inbound stock` note in the registration memo speeds up routing to the owner. A separate temporary registration path for these arrivals was **explicitly rejected by the owner** (2026-08-02) — do not reintroduce one.

### 3.14 Interaction baseline: keyboard, focus, and announcement *(spec-authored)*

This page is operated by a seated desk user who may be working keyboard-only while on a call. The wireframe binds none of the following; the admin must.

- **Tab order** follows DOM order: within a row, `Review & Match` then `✕`. Row order is the rendered order (newest first).
- **Activation:** `Enter` and `Space` activate both row buttons and both modal buttons.
- **Modal focus:** opening `[L-M1]` or `[L-M2]` moves focus into the modal and traps it until close; closing returns focus to the control that opened it `[BR-40]`, `[E-62]`.
- **`Esc`** closes `[L-M1]`, `[L-M2]`, and `#inbox1`, all with zero side effects `[E-24]`, `[E-56]`, `[N-6]`, `[N-7]`.
- **Accessible names:** `✕` carries an accessible name equivalent to its `title="Remove from list"`; the Comments button exposes the unread count as text, not colour alone.
- **Toasts** are announced through a live region `[L-F1]`.
- **No focus stealing:** a live arrival `[E-21]` inserts a row without moving focus or scroll position `[N-8]`.

---

## 4. Business Rules

Every rule carries a rationale and a decision date. Reversals appear in §10. Global rules are cited, never restated.

| ID | Rule | Rationale | Decided |
|---|---|---|---|
| **BR-1** | **Single registration entry point.** A pool row can be created only by the View Orders send-to-unrecognized modal (M2b). No in-page register button, no in-page register modal, no UI-exposed backdoor. | Registration must happen where the physical product and the scanner are. Two entry points would let the bench and the desk disagree about what arrived. | 2026-07-23 |
| **BR-2** | **Matching UX inversion.** The system presents suspected orders and their PICs; the handler only confirms. Handlers never search for their own name per product. | The old flow made every handler scan every product. The inverted flow turns an O(handlers × products) search into a single confirmation. | 2026-07-23 |
| **BR-3** | **Candidate predicate is exactly `status == Processing AND order contains the product by barcode`.** No channel filter, no PIC filter, no date window, no fuzzy matching. Coupang orders are absent as an emergent consequence of the upstream lookup, not as a rule. | Any additional filter would silently hide a legitimate candidate, and `[BR-4]` leaves no fallback to recover it. | 2026-07-23, restated in the 2026-08-03 English pass |
| **BR-4** | **No manual PIC/order search fallback.** "If it is not here, the data is wrong." An empty candidate list is an upstream data problem, not a search problem. | The candidate set is complete by construction, so a search can only return the same set or a wrong answer. | 2026-07-23 (commit `e43ce68`) |
| **BR-5** | **The match target is a product LINE, not an order.** Confirming writes the tracking number directly onto that line, into the same field the View Orders scan path reads — so a rescan of the same barcode resolves normally. | This is the mechanism that closes the physical loop; without it the parcel would stay set aside forever. Mandatory inclusion #6. | 2026-08-03 (commit `d09fe79`, cross-referenced in the View Orders behavior-rules footnote) |
| **BR-6** | **Registration auto-notifies `#unrecognized-tracking` and @mentions the suspected PICs.** No human triggers this notification. | The pool works only because it is push-driven; a notification anyone has to remember to send is a notification that does not happen. | 2026-07-23 (inversion); channel CONFIRMED 2026-08-03 |
| **BR-7** | **Match confirm auto-posts a comment on the order @mentioning the REGISTRANT** (not the resolver, not the PIC). | Closes the loop back to the warehouse bench: the person holding the parcel learns it is now claimable. | 2026-08-03 |
| **BR-8** | **✕ removal is a soft delete.** Status becomes `REMOVED`; the full row snapshot and the actor are persisted permanently. Nothing on this page is ever hard-deleted. | The pool view is reconstructible from events `[G-8]`; mis-registrations are exactly the case where the record matters most. | button 2026-07-23; doctrine 2026-08-03 |
| **BR-9** | **Removal requires a confirm dialog, a mandatory reason, and a success toast** `[PD-60 · CONFIRMED 2026-08-03]`, `[PD-5 · CONFIRMED 2026-08-03]`. Confirmed reason labels: `Registered by mistake` / `Routed to inbound request` / `No action needed` / `Other` (+ mandatory memo for `Other`). Removal also auto-posts a comment on the pool item `[DC-29]`. | `[G-2]` with `[GD-5]`, plus `[G-8]`'s "why" requirement and the `[G-11]` reason precedent. The button sits beside the primary action at speed (§1.4). | 2026-08-03 (adjudication C-6) → **owner-confirmed + wireframe-implemented 2026-08-03** |
| **BR-10** | **Reason `Routed to inbound request` captures a structured Inbound No.** on the removal event; it is prompted, not enforced `[PD-64 · OWNER-PENDING]`. | The memo convention is unqueryable. A structured link makes the recovery loop auditable without a hard guard that would strand out-of-order work. | 2026-08-03 |
| **BR-11** | **Unrequested inbound shipments reuse this pool.** A separate temporary registration path was rejected by the owner. | One holding area, one set of eyes. A second path would duplicate the notification, the audit trail, and the failure modes. | 2026-08-02 |
| **BR-12** | **Order No is the Coupang purchase order number** (`12101316464794` format) and is **normally `–`.** A present value is display-only context and never affects candidate computation. | Lookup-matched items are resolved upstream and never reach the pool; a number that reached the pool is by definition one the lookup rejected, so trusting it would re-import the error. | 2026-07-23 |
| **BR-13** | **No photo capture on this page — permanently** `[PD-63 · OWNER-PENDING]`. No upload control, no column, no thumbnail, no phase pointer. | The 2026-07-21 hold was resolved by deletion in the 2026-08-03 review (item 15). Leaving it "deferred" invites re-implementation from stale docs. | 2026-07-21 hold → 2026-08-03 deletion |
| **BR-14** | **Brand bold-prefixing covers every product surface on this page** — both name columns, M1's summary card and `Included Product` cells, the auto-comment, and the toast `[G-6]`. Catalog casing is preserved verbatim and the two columns may differ. | The resolver judges a product they cannot see; the brand is the fastest discriminator (§1.4). | View Orders decision B; reconfirmed 2026-08-03 |
| **BR-15** | **Page delta on `[G-5]`, two surfaces.** The badge form (`[G-5]` in full: colorless bold black, never a pill) lands **only** on `[L-M1]`'s `Channel` cell. In `[L-2]`'s pool cell the route is one clause of a compound sentence and renders as muted running text (`--ink-3`, non-bold) inside the same `.mut` span as the status; only `[G-5]`'s never-a-coloured-pill prohibition applies there. Rendering table, rationale and reversal impact: §3.3. `OTHER` renders `OTHER ({channel})` in whichever form its surface uses `[PD-80 · OWNER-PENDING]`. This page only displays the route; its origin is the Inbound Request, matched via the invoice number. | Coloured pills would compete with the yellow row highlight, which is the page's one real signal; and inside the candidate sentence the emphasized element is the order number, not the route. | 2026-07-13 badge convention; `OTHER` form 2026-08-03; **pool-cell delta 2026-08-03** |
| **BR-16** | **No search bar, no filters, no pagination, no column sorting.** | The pool is expected to hold a handful of items and the resolver arrives by deep link. A search bar would also re-legitimize the manual-search flow that `[BR-4]` deliberately removed. | 2026-07-23 |
| **BR-17** | **Qty mismatch at match time is allowed** (pool qty 2 vs a ×1 line). The difference is recorded on the match event and stated in the auto-comment `[PD-65 · OWNER-PENDING]`. | 1+1 sets and combined boxes make mismatches normal; blocking would strand real matches with no alternative path. | 2026-08-03 |
| **BR-18** | **A target product line that already carries a tracking number blocks the match** with an explicit error. No silent overwrite. | Overwriting would orphan whichever parcel was bound first, with no record of the swap. | 2026-08-03 |
| **BR-19** | **Page-level extension of `[PD-8]`, declared as such.** `[PD-8 · OWNER-PENDING]` decides only that an *inbound* number is unique system-wide (a second **inbound request** carrying it is blocked) and that the inbound and outbound namespaces are separate and may coincide. It says nothing about **order lines**. This page extends it: within one namespace, a tracking number may not be bound to two order lines, and a match that would do so is blocked `[E-11]`. The extension is **not** register-backed — if the owner declines it, delete this rule, `[E-11]`, QA-VAL-03 and step 1's `tracking_in_use` check; `[PD-8]`'s inbound-request guard is unaffected. A pool item's number carries the namespace of the scan that produced it (`[L-1]` column 1), so an unrequested-inbound parcel's number is checked against inbound bindings only — see `[E-33]`. | Matching integrity requires a single owner per number within a namespace; the two namespaces never resolve to the same screen. | 2026-08-03 (page extension; `[PD-8]` itself unchanged) |
| **BR-20** | **The match transaction is atomic across revalidate → line write → pool close.** Comment and Slack are non-blocking side effects: their failure never rolls back the match, and is persisted and retried `[PD-4 · OWNER-PENDING]`. | Notification is a side effect, not part of the transaction. A rolled-back match would leave the parcel unresolvable because of a Slack outage. | 2026-08-03 |
| **BR-21** | **The server revalidates every precondition at confirm time**; on mismatch it rejects with a red toast and refreshes the affected view, with no partial writes `[PD-6 · OWNER-PENDING]`. | Candidates go stale between page load and click (an order ships, is cancelled, goes on-hold, is merged, or is matched elsewhere). | 2026-08-03 |
| **BR-22** | **Concurrent edits use an optimistic version check** → 409 → reload the row + non-green toast `[PD-7 · OWNER-PENDING]`. No last-write-wins. | Two resolvers reaching for the same parcel is the expected failure, not the exotic one. | 2026-08-03 |
| **BR-23** | **Idempotency-key semantics `[G-9]`:** match = `pool_item_id + line_id`; removal = `pool_item_id + "remove"`. Suppressed duplicates are logged `[DC-12]` / `[DC-16]`. Because the key always contains `pool_item_id`, two different pool items can never collide `[E-67]`. | `[G-9]` fixes the requirement; this rule fixes the two key shapes so a developer does not invent a third. The current admin's double-processing behavior is a known defect carried in handoff note A; the wireframe reproduces it on `.xdel` (`WF-NEW-D`), so the key is what stops it reaching production. | handoff note A, 2026-07-21; key shapes 2026-08-03 |
| **BR-24** | **An empty candidate list renders explicit guidance,** not a blank cell: `No Processing order contains this product — check the order data upstream, or remove with a reason.` No search affordance is re-introduced `[PD-62 · OWNER-PENDING]`. | `[BR-4]` says an empty list means the data is wrong; the UI should say exactly that instead of implying the operator did something wrong. | 2026-08-03 |
| **BR-25** | **A once-daily digest re-notifies `#unrecognized-tracking` with pool items open for more than 24 h** `[PD-61 · OWNER-PENDING]`. Same shape as the inbound-request morning check. | The 2026-07-23 simplification removed the only age signal; a daily digest restores it without re-adding UI. | 2026-08-03 |
| **BR-26** | **No control on this page is role-gated in v1** `[G-15]`, `[PD-1 · OWNER-PENDING]`. | Six screens independently asked the same question; inventing per-page gates would produce eight inconsistent models. | 2026-08-03 |
| **BR-27** | **Page extension of `[G-7]`'s append-only property `[PD-3 · OWNER-PENDING]`:** the pool row's **Memo** is also immutable after registration. It is not a comment, so `[G-7]` does not reach it on its own; corrections to a memo are posted as comments on the pool item. | The memo is the registrant→resolver channel and is quoted verbatim into `[L-M1]` and `[DC-14]`'s snapshot; an editable memo would silently rewrite the record a resolver already acted on. | 2026-08-03 |
| **BR-28** | **An on-the-spot match performed in View Orders M2 fires the same auto-comment and Slack route,** with the @mention suppressed when resolver == registrant `[PD-16 · OWNER-PENDING]`. | One match pipeline, one audit trail, regardless of which screen resolved it. | 2026-08-03 |
| **BR-29** | **Comments-hub entries whose entity is `Unrecognized pool` open this page focused on that row;** if the item is no longer open, they open the matched order `[PD-67 · OWNER-PENDING]`. | The click must land where the operator can act; a resolved item has no row left to focus. | 2026-08-03 |
| **BR-30** | **No scan surface on this page.** `[G-1]` applies only via the cross-page rescan loop on View Orders. | The bench is where scanners live. Adding a scan input here would invite registration outside `[BR-1]`. | 2026-08-03 (stated, not changed) |
| **BR-31** | **No print surface on this page.** `[G-4]` does not land here; a print-agent outage cannot block, delay, or degrade any action on this screen. | Nothing on this page produces a physical artifact. | 2026-08-03 |
| **BR-32** | **The Closing page's "unknown order" warning does NOT route to this pool,** and nothing in this pool feeds Closing. The two concepts are disjoint. | A closing scan failure is an outbound-verification problem; an unrecognized barcode is an inbound-identity problem. Conflating them would put customer parcels into a supplier-arrival queue. | 2026-08-03 (`_review` §1 adjudicated non-issue) |
| **BR-33** | **Count invariant:** `#poolCount` == `#poolCountBottom` == rendered open rows, after every mutation including live arrival. | The counts are the only integrity check a human can perform on this screen. | 2026-07-23 (wireframe behavior), specified 2026-08-03 |
| **BR-34** | **This page claims no exception to `[G-2]`'s refresh prohibition** — the named RTO Bulk Outbound exception is the only one in the corpus and it is not here. Stated as a negative registry entry, not as a restatement. | The page's only mutations (match, removal, live arrival) are exactly where a naive implementation would reload, so the absence of an exception has to be on the record. | 2026-08-03 |
| **BR-35** | **All pool events are retained indefinitely.** Four operational figures must be derivable from persisted events alone, with no extra instrumentation: resolution latency (`[DC-1]`→`[DC-8]`), Coupang lookup-failure rate (`[DC-3]`), removal-reason distribution (`[DC-14]`), and unrequested-inbound volume (`[DC-15]`). | Retro-fitting instrumentation for these later would require a schema change. Retention is a per-screen statement required by `[G-8]`. | 2026-08-03 |
| **BR-36** | **The pool row's yellow highlight (`.row-hit`) is a requirement, not styling.** Every open row is highlighted; there is no un-highlighted open-row variant. | It is how an operator confirms across a desk that a row is still unresolved (§1.4). | 2026-07-23 |
| **BR-37** | **Every order number rendered on this page is a real link** to that order `[G-12]` — in the pool's Suspected Orders cells, in M1's Order column, and in comment bodies. | Currently a wireframe defect (`WF-NEW-B`): the file contains zero anchors. | 2026-08-03 |
| **BR-38** | **After any match or removal, the candidate cells of the remaining pool rows are recomputed** `[DC-6]`, so no row keeps offering a line a sibling row just consumed. | Without it, a second resolver clicks a dead candidate and receives an error the UI could have prevented `[E-51]`. | 2026-08-03 |
| **BR-39** | **The registration Slack message @mentions each suspected PIC exactly once,** even when that PIC owns several candidate orders. | Duplicate mentions in one message train people to ignore the channel `[E-52]`. | 2026-08-03 |
| **BR-40** | **Overlay dismissal and focus management are specified, not left to the framework:** `Esc` and outside-click close `#inbox1`; `Esc` closes both modals; modals trap focus and return it to their trigger. | The wireframe binds none of this (§2.4.8); a keyboard-only resolver would otherwise be stranded inside an overlay `[E-56]`, `[E-62]`. | 2026-08-03 |
| **BR-41** | **Both counters are derived from the rendered row collection,** never from the length of the server response. | If rendering fails, the invariant `[BR-33]` must surface the failure instead of reporting a number no human can see `[E-72]`. | 2026-08-03 |
| **BR-42** | **Notification dispatch has a terminal state.** After the retry budget is exhausted the failure is dead-lettered and persisted `[DC-28]`; it never blocks or reverses a match or a removal. | An infinitely retrying queue hides a broken integration; a recorded terminal failure can be alerted on `[E-61]`. | 2026-08-03 |
| **BR-43** | **Rows render the product identity snapshotted at intake,** never a live catalog join. | A catalog rename, merge, or deletion after intake must not blank or silently alter a pool row the operator is judging `[E-38]`. | 2026-08-03 |
| **BR-44** | **Candidate global amendment, stated locally under protest.** Reading: `[G-2]`'s "no full-page refresh after any action" targets **programmatic** post-action refresh; an operator pressing F5 is outside its scope, and state is re-fetched with both counters re-derived `[E-57]`. **This reading is not page-specific** — it applies identically to all eight screens, and settling it inside one page spec is how eight specs diverge (cross-page defect m1 D-7). It belongs in `[G-2]` as a global amendment; until that amendment is raised, this page states it here so QA has a rule to test, and deletes this row the day the global text lands. **Do not copy this row into another spec** — cite the global rule instead. | Otherwise QA cannot distinguish a forbidden auto-refresh from an operator pressing F5, and QA-FURN-07 has no verdict. | 2026-08-03 (page-local, pending promotion to `[G-2]`) |

---

## 5. Data Capture

> **Page delta on `[G-8]`.** The pool table, the Suspected Orders column, and the Comments hub are all views over the events below — no UI on this page is the only copy of anything. The resolved-completion log removed on 2026-07-23 removed the *view*, not the *data* `[L-S1-Fa]`. Retention and derivable figures are stated in §5.4 and `[BR-35]`.

**Entity.** `unrecognized_item` (one per pool row). **Lifecycle:** `OPEN → MATCHED` | `OPEN → REMOVED`. Both terminal states are soft; no row is ever hard-deleted.

**Baseline fields on every event** (omitted from the rows below to avoid repetition): `event_id`, `event_name`, `occurred_at` (UTC, rendered KST), `actor_id` + `actor_display_name` (or `system`), `source_screen` (`tracking-missing` | `view-orders` | `system`), `pool_item_id`, `idempotency_key` where the event is a confirming action, `request_id` for tracing.

### 5.1 Persisted events (29)

`[DC-27]`, `[DC-28]` and `[DC-29]` are grouped by meaning rather than by number; the numbering is stable and never renumbered.

> **Event-name scope note (cross-page defect m3a D14).** The ten canonical cross-page names fixed by `_global-rules.md` are used byte-identically here: `comment.posted`, `comment.mention_notified`, `comment.starred` / `comment.unstarred`, `comment.read` / `comment.mark_all_read`, `comment.auto_posted`. Every **other** name below is a page-scoped `entity.action` name per `_review.md` §3.3. Four of them express concepts that other specs also name, with different strings, and **no canonical name exists for those concepts yet**:
>
> | Shared concept | This page's name | Named differently elsewhere |
> |---|---|---|
> | Idempotent duplicate suppressed | `unrecognized_item.match_duplicate_suppressed` `[DC-12]`, `unrecognized_item.removal_duplicate_suppressed` `[DC-16]` | `idempotency.duplicate_rejected` (VO, RTO) · `idempotency.duplicate_suppressed` (OM) · `action.idempotency_suppressed` (OD) · `inbound_request.idempotent_replay_suppressed` (IR) |
> | Comment search executed | `comment.searched` `[DC-23]` | `comment.search_executed` (VO) · `comment.search.executed` (INV) · declared NON-event (OD) · optional telemetry (RTO) |
> | Slack dispatch outcome | `slack.registration_notified` `[DC-4]`, `slack.aging_digest_sent` `[DC-19]`, `notification.retry_result` `[DC-24]` | `slack.dispatch_result` (VO) · `slack_notification.sent` (IR) · folded into `comment.mention_notified` (OD) |
> | Stock moved | *(not emitted — this page never moves stock, §5.3)* | `inventory.stock_applied` (VO) · `inventory.movement` (OD) · `stock.inbound.recorded` (INV) |
>
> These are **names, not behaviors**: nothing in §3–§8 depends on the string. If a canonical name is promoted into `_global-rules.md`, the global name supersedes and only this table plus the affected `Event name` cells change. Note also that OD declares comment search a NON-event while three pages persist it — that is a `[G-8]` disagreement above this spec's authority and is recorded here so it is not silently resolved page by page.

#### Group A — Intake (created upstream in View Orders; persisted against this page's entity)

| ID | Event name | Actor | Trigger | Old → New / payload | UI-visible? |
|---|---|---|---|---|---|
| **DC-1** | `unrecognized_item.created` | Registrant (warehouse) | Send in View Orders M2b | `null → {barcode, product_id (autocomplete pick), product_name_en, product_name_kr, size, qty, memo (nullable), tracking_no (auto-collected at scan time), order_no (nullable — carried only when the lookup failed), registrant_id, center, created_at, status: OPEN}` | Yes — the pool row `[L-1]` |
| **DC-2** | `unrecognized_intake.deduped` | System | A second send arrives for the same `tracking_no` + `barcode` while an OPEN item exists | `{existing_pool_item_id, rejected_payload, reason: "already_in_pool"}` — no second row is created | No (upstream feedback only) `[E-1]` |
| **DC-3** | `unrecognized_lookup.attempted` | Registrant | The View Orders M2 order-number lookup runs | `{barcode, entered_order_no or null, result: matched \| no_match \| sent_to_pool}` | **Silent.** Source of the lookup-failure-rate figure `[BR-35]` |
| **DC-4** | `slack.registration_notified` | System | Immediately after `[DC-1]` | `{channel: "#unrecognized-tracking", payload: {tracking_no, product, qty, memo, registrant, suspected_orders[]}, mentioned_pic_ids[] (deduplicated [BR-39]), truncated_candidate_count, message_ts, delivery: ok \| failed, error?}` | **Silent** — the v1 "Slack notified" column was removed 2026-07-23 `[L-S1-Fa]` |

#### Group B — Candidate computation

| ID | Event name | Actor | Trigger | Old → New / payload | UI-visible? |
|---|---|---|---|---|---|
| **DC-5** | `suspected_orders.computed` | System | At intake, immediately after `[DC-1]` | `null → [{order_id, order_no, line_id, pic_id, channel, route, status}]` — the snapshot that `[DC-4]` @mentions | Yes — the Suspected Orders cell `[L-2]` |
| **DC-6** | `suspected_orders.recomputed` | System | Page load, M1 open, an order entering or leaving `Processing`, and after any match or removal on this page `[BR-38]` | `{old_set[], new_set[], trigger: page_load \| modal_open \| order_status_change \| sibling_resolution, changed_order_id?}` | Yes — cell refresh `[E-40]`, `[E-48]`, `[E-51]` |

#### Group C — Resolution by match

| ID | Event name | Actor | Trigger | Old → New / payload | UI-visible? |
|---|---|---|---|---|---|
| **DC-7** | `unrecognized_item.review_opened` | Resolver | Click `Review & Match` (or M1 opened from any entry) | `{candidate_set_snapshot[], opened_at}` — the baseline a later stale-candidate rejection is diffed against | **Silent** |
| **DC-8** | `unrecognized_item.match_confirmed` | Resolver | Click `Match to this product` | `status: OPEN → MATCHED`; `{selected_order_id, selected_line_id, selected_line_qty, pool_qty, qty_mismatch: bool [PD-65 · OWNER-PENDING], resolver_id, resolved_at, candidate_set_at_confirm[], source: tracking-missing \| view-orders-m2 [PD-16 · OWNER-PENDING]}`. Resolution latency = `resolved_at − created_at` `[BR-35]` | Yes — row disappears + toast `[L-F1]` |
| **DC-9** | `order_line.tracking_no_set` | Resolver (attributed), `source = unrecognized-match` | Step 2 of §3.4.3 | On the **order product line**: `tracking_no: null → {value}`; `{order_id, line_id, pool_item_id, previous_value}`. `source` distinguishes this from a direct View Orders M2 match | Yes — on the order and order-detail pages |
| **DC-10** | `comment.auto_posted` *(canonical)* | System on behalf of the resolver, `source = system` | Step 4 of §3.4.3 | `{entity_type: order, entity_id, body: "@{registrant} (unrecognized registrant) Matched the unrecognized product ({product}) to this order" [+ qty-mismatch clause], mention_target: registrant_id, backlink: pool_item_id}` | Yes — the order's Comments |
| **DC-11** | `comment.mention_notified` *(canonical)* | System | Step 5 of §3.4.3, and every manual @mention from `[L-5]` | `{comment_id, channel: "#fulfillment-admin-comments" (C0BMGEWM5QA), mentioned_user_id, message_ts, deep_link, delivery: ok \| failed, error?}` | **Silent** |
| **DC-12** | `unrecognized_item.match_duplicate_suppressed` | System | A second confirm arrives under an idempotency key already consumed | `{idempotency_key, attempted_by, attempted_at, original_event_id}` — no second write of any kind | **Silent** `[E-9]`, `[G-9]` |
| **DC-13** | `unrecognized_item.match_rejected` | System | Any revalidation failure in step 1 of §3.4.3 | `{reason: stale_candidate \| line_occupied \| tracking_in_use \| item_not_open \| line_not_found \| order_not_found \| version_conflict, attempted_order_id, attempted_line_id, status_snapshot_at_rejection, attempted_by}` — no partial writes | **Silent + red toast** `[E-6]`…`[E-11]`, `[E-49]`, `[E-50]` |
| **DC-27** | `comment.mention_suppressed_self` | System | Step 5 when resolver == registrant | `{comment_id, suppressed_user_id, reason: "self_notification"}` — the comment still posts; only the Slack mention is suppressed `[PD-16 · OWNER-PENDING]` | **Silent** `[E-54]` |

#### Group D — Resolution by removal

| ID | Event name | Actor | Trigger | Old → New / payload | UI-visible? |
|---|---|---|---|---|---|
| **DC-14** | `unrecognized_item.removed` | Operator | Confirm in `[L-M2]` | `status: OPEN → REMOVED`; `{reason: registered_by_mistake \| routed_to_inbound_request \| no_action_needed \| other [PD-60 · CONFIRMED 2026-08-03], inbound_no (nullable) [PD-64 · OWNER-PENDING], memo (nullable; required when reason = other), full_row_snapshot{all 12 column values + candidate set at removal}, removed_by, removed_at}` | Yes — row disappears + toast |
| **DC-15** | `inbound_request.pool_linkback` | System | `[DC-14]` with `reason = routed_to_inbound_request` and a supplied Inbound No. | On the **inbound request** entity: `{inbound_no, pool_item_id, product_id, qty, tracking_no, linked_at, resolves: bool}` — the reciprocal record that lets the Inbound Request page show provenance. `resolves:false` when the Inbound No. does not exist or covers a different product `[E-70]` | Yes — on the Inbound Request page |
| **DC-16** | `unrecognized_item.removal_duplicate_suppressed` | System | A second removal confirm under a consumed idempotency key | `{idempotency_key, attempted_by, attempted_at, original_event_id}` | **Silent** `[G-9]`, `[E-18]` |
| **DC-29** | `comment.auto_posted` *(canonical)* | System on behalf of the operator, `source = system` | Confirm in `[L-M2]`, immediately after `[DC-14]` (added by the 2026-08-03 owner confirmation of `[PD-5]`) | `{entity_type: unrecognized_item, entity_id: pool_item_id, body: "Removed from pool — {reason}" + optional " · Inbound No. {n}" + optional " · {memo}" (spec-authored), mentions: [] , backlink: removal_event_id}` — **no @mention**, so no `[DC-11]` dispatch fires (§6.1: no Slack route for removals) | Yes — the pool item's comments (hub entity label `Unrecognized pool`) |

#### Group E — Cross-page closure

| ID | Event name | Actor | Trigger | Old → New / payload | UI-visible? |
|---|---|---|---|---|---|
| **DC-17** | `unrecognized_item.rescan_resolved` | Bench operator, on View Orders | Rescanning the same barcode/tracking after `[DC-9]` | `{pool_item_id, order_id, line_id, scanned_at, scanner_actor}` — links the physical scan back to the resolution and closes the loop that started at `[DC-1]` | Cross-page (View Orders) `[E-15]` |

#### Group F — Aging

| ID | Event name | Actor | Trigger | Old → New / payload | UI-visible? |
|---|---|---|---|---|---|
| **DC-18** | `unrecognized_pool.aging_digest_computed` | System | Once daily `[PD-61 · OWNER-PENDING]` | `{as_of, items[]: [{pool_item_id, tracking_no, product, registrant, created_at, age_hours}], threshold_hours: 24}` | No |
| **DC-19** | `slack.aging_digest_sent` | System | Immediately after `[DC-18]`, only when `items[]` is non-empty `[PD-61 · OWNER-PENDING]` | `{channel: "#unrecognized-tracking", item_count, message_ts, delivery: ok \| failed}` | **Silent** `[E-37]` |

#### Group G — Comments hub `[G-7]`

| ID | Event name | Actor | Trigger | Old → New / payload | UI-visible? |
|---|---|---|---|---|---|
| **DC-20** | `comment.posted` *(canonical)* | Any user | Posting a comment on a **pool item** or an order from this page | `{entity_type: unrecognized_item \| order, entity_id, body, mentions[], posted_at}`. Pool items are a first-class commentable entity type `[G-7]`, `[L-5]` | Yes |
| **DC-21** | `comment.starred` / `comment.unstarred` *(canonical)* | User | `.star` toggle | `saved: false ↔ true` per `{user_id, comment_id}` | Yes — ★ state |
| **DC-22** | `comment.read` / `comment.mark_all_read` *(canonical)* | User | Opening a mention item / clicking `Mark all read` | `unread → read` for one item or the whole set; `{user_id, comment_ids[]}` | Yes — badge count `[L-F3]` |
| **DC-23** | `comment.searched` | User | Submitting a query in the Comments-hub search (`WF-NEW-A` must be fixed first) | `{query, result_count, searched_at}` — persisting is the doctrine default; whether to index it is a developer decision (§9.2 D-6) | **Silent** |

#### Group H — Infrastructure and failure

| ID | Event name | Actor | Trigger | Old → New / payload | UI-visible? |
|---|---|---|---|---|---|
| **DC-24** | `notification.retry_result` | System | Each retry of a failed `[DC-4]` / `[DC-11]` / `[DC-19]` dispatch | `{origin_event_id, attempt_no, delivery: ok \| failed, error, next_retry_at?}`. Retry policy is a developer decision (§9.2 D-5) `[PD-4 · OWNER-PENDING]` | **Silent** |
| **DC-25** | `unrecognized_pool.fetch_failed` | System | The pool list query fails on page load or live refresh | `{error_class, actor_id, attempted_at}` — the UI shows an error state with retry, never a blank table | Yes — error state `[E-28]` |
| **DC-26** | `unrecognized_item.registrant_unresolvable` | System | The registrant has no Slack mapping (deactivated / left) at `[DC-11]` time | `{comment_id, registrant_name_plaintext, reason: no_slack_mapping}` — the comment still posts with a plain-text name and the flow does not fail `[E-27]`, `[E-71]` | **Silent** |
| **DC-28** | `notification.dead_lettered` | System | The retry budget for a dispatch is exhausted `[BR-42]` | `{origin_event_id, channel, total_attempts, last_error, dead_lettered_at}` — terminal. Never blocks or reverses the match/removal that produced it | **Silent** `[E-61]` |

### 5.2 Declared NON-events

The following are explicitly ephemeral, client-local, and must **not** be persisted (`[G-8]` non-event doctrine, `[GD-6]`):

| ID | Non-event | Why |
|---|---|---|
| **N-1** | Page view / navigation to this page | Not mutating; the resolver arrives from a Slack link and may bounce repeatedly |
| **N-2** | Poll or push refresh of the pool list (the delivery itself) | The underlying `[DC-1]` / `[DC-8]` / `[DC-14]` already carry the facts |
| **N-3** | Comments-hub open/close, tab switch (`@ Mentions` ↔ `★ Saved`), outside-click and `Esc` dismissal | Pure view state. `[DC-22]` covers the read transition that matters |
| **N-4** | Opening M1 via the **wf-bar demo button** | Wireframe chrome only; it does not exist in the admin. Opening M1 from a **row** *is* persisted as `[DC-7]` |
| **N-5** | Toast display, stacking, and auto-dismiss | The confirming action is what persists |
| **N-6** | Opening `[L-M2]` and cancelling it | An abandoned intent is not an intent; only the confirmed removal persists `[DC-14]` |
| **N-7** | Closing M1 via `Cancel`, the header `✕`, the overlay backdrop, or `Esc` | All four are side-effect free `[E-24]` |
| **N-8** | Hover, focus, row highlight, scroll position | Rendering state |
| **N-9** | Typing in a comment draft before posting | Only the posted comment persists `[DC-20]` |
| **N-10** | Typing in `[L-M2]`'s reason / Inbound No. / memo fields before confirm | Only the confirmed removal persists |
| **N-11** | The `Hide annotations` toggle and all `.dot` / `.legend` interaction | Wireframe chrome |
| **N-12** | Clicking a candidate order link to navigate away | Navigation, not mutation |

### 5.3 Canonical cross-page events this page does NOT emit

Stated so an auditor can distinguish "missing" from "not applicable":

- `print.job_result` — no print surface `[BR-31]`, `[G-4]` N/A.
- `product.barcode_registered` — barcode registration happens in View Orders / Inventory, never here.
- `order.status_changed` — a match writes a tracking number onto a line; it never changes the order's status. An order that was `Processing` before the match is `Processing` after it.
- `order.outbounded` — no outbound-class control exists on this page, so `[G-3a]` and `[PD-2 · OWNER-PENDING]` also cannot land here.

### 5.4 Retention and export

- **Retention: indefinite.** All pool events, comments, and Slack dispatch results are permanent, and remain queryable after the entity reaches `MATCHED` or `REMOVED` `[G-7]`, `[G-8]`, `[BR-35]`.
- **The removed resolved-log UI did not remove the data.** Every `[DC-8]` and `[DC-14]` is queryable admin-side; a resolved list is a view over them and can be re-surfaced later without a schema change `[L-S1-Fa]`.
- **Derivable figures, no extra instrumentation** `[BR-35]`: (a) resolution latency `[DC-1]`→`[DC-8]`; (b) Coupang lookup-failure rate from `[DC-3]`; (c) removal-reason distribution from `[DC-14]`; (d) unrequested-inbound volume from `[DC-15]`.
- **No UI export exists on this page and none is specified.** Storage and BI/CSV export mechanics for pool-event history are a developer decision (§9.2 D-8).

---

## 6. Integrations

### 6.1 Slack routing

Payload fields are verbatim from the routing table in `_global-rules.md` (all rows CONFIRMED 2026-08-03).

| # | Trigger | Channel | Payload | Mention target | Event |
|---|---|---|---|---|---|
| 1 | Unrecognized barcode sent to the Missing Tracking List (i.e. a pool row is created) | **`#unrecognized-tracking`** — the routing table publishes no channel ID for it; dev resolves the ID at wiring time (§9.2 D-11) | tracking no., product, qty, memo, registrant, suspected orders | @mentions the **suspected PICs** computed at intake, each exactly once `[BR-39]` | `[DC-4]` |
| 2 | Match confirmed in Unrecognized Tracking | **`#fulfillment-admin-comments`** (`C0BMGEWM5QA`) — routed as a comment auto-post + mention, not a direct channel message | tracking no., matched product line, resolver | @mentions the **registrant**; suppressed when resolver == registrant `[PD-16 · OWNER-PENDING]` | `[DC-10]` → `[DC-11]` |
| 3 | Comment @mention on a pool item or an order, raised from this page | **`#fulfillment-admin-comments`** (`C0BMGEWM5QA`) | entity no., comment text, time, author, @mentioned user, deep link | the @mentioned user | `[DC-20]` → `[DC-11]` |
| 4 | Daily aging digest — pool items open > 24 h `[PD-61 · OWNER-PENDING]` | **`#unrecognized-tracking`** | as-of time, item count, and per item: tracking no., product, registrant, age | none (channel-level, no @mention) | `[DC-18]` → `[DC-19]` |

**Explicitly NOT this page's routes:**
- `#wholesale-ops` and `#partnership-kr` — the morning no-tracking checks belong to the Inbound Request page.
- **No Slack route exists for removals** `[DC-14]`. Removing a mis-registration is a cleanup action, not an event anyone needs pushed; creating a channel for it would produce an unowned alert stream. The record lives in the audit trail — and, since the 2026-08-03 `[PD-5]` confirmation, in a mention-free auto-comment on the pool item `[DC-29]`, which is a hub-readable record, not a Slack dispatch.
- Closing confirmations do not route here, and Closing's "unknown order" warning never produces a `#unrecognized-tracking` message `[BR-32]`.

**Failure handling.** Row 1 firing is **not** part of the intake transaction: if Slack is down the pool row still exists and is still resolvable from the page `[PD-4 · OWNER-PENDING]`, `[E-39]`. The same holds for rows 2–4. Failures are persisted `[DC-4]` / `[DC-11]` / `[DC-19]`, retried `[DC-24]`, and dead-lettered when the budget is exhausted `[DC-28]`, `[BR-42]`. Retry policy is a developer decision.

### 6.2 Cross-page links and deep links `[G-12]`

**Path form (normalized 2026-08-03, cross-page defect m3a D16).** All cross-page links use the **directory form** `../{slug}/#{anchor}` — the form `[G-12]` itself uses (`../inbound-request/#reqlist`) and the form the live wireframe URLs resolve to. The `index.html` variant that earlier drafts of this spec used is **not** to be re-introduced; QA asserts the directory form.

| From | To | Link form | Notes |
|---|---|---|---|
| Suspected Orders cell — each candidate's order number `[L-2]` | Order Detail | `../order-detail/#{order_no}` → filtered entity route in production | Currently rendered as non-anchored blue bold text — defect `WF-NEW-B`, rule `[BR-37]` |
| M1 candidate table — `Order` column `[L-M1]` | Order Detail | same | same defect |
| Comments hub item with entity `Unrecognized pool` `[L-5]` | This page, focused on that row; the matched order if the item is no longer open | `#poolrow-{pool_item_id}` | `[PD-67 · OWNER-PENDING]` |
| Comments hub item with an order entity | Order Detail | `../order-detail/#{order_no}` | Standard `[G-7]` behavior |
| Auto-comment backlink `[DC-10]` | This page's pool item (historical record) | `#poolrem-{pool_item_id}` for removed/matched items | Lets an order reader trace where the tracking number came from |
| `[L-M2]` removal with `Routed to inbound request` `[DC-15]` | Inbound Request → Request List tab | `../inbound-request/#reqlist` (the anchor `[G-12]` names and View Orders State 6 already uses) | The structured Inbound No. is what makes it queryable `[PD-64 · OWNER-PENDING]` |

### 6.3 Upstream / downstream page contracts

- **View Orders (upstream, mandatory).** Owns the M2 order-number lookup and the M2b send-to-unrecognized modal. It emits `[DC-1]`, `[DC-3]`, and fires Slack row 1. **Contract:** its scan path must read the *same* tracking field this page's match writes `[BR-5]`, so `[DC-17]` closes the loop. Any change to that field is a breaking change to both specs and must be reflected in both.
- **View Orders (downstream).** After a match, rescanning resolves normally. For the unrequested-inbound route, rescanning after removal + inbound-request creation enters **State 6** (internal inbound) `[L-S1-Fb]`, `[G-10]`.
- **Inbound Request.** Receives `[DC-15]` provenance links. Accumulating multiple tracking numbers on one request `[G-10]` is that page's concern; this page hands one number across at a time. Adding tracking numbers to an already-INBOUNDED request is blocked there `[PD-85 · OWNER-PENDING]`, which is why `[E-35]` accepts such an Inbound No. here without pretending to resolve it.
- **Order Detail.** Displays the tracking number written by `[DC-9]` and the auto-comment from `[DC-10]`. If the matched order is later cancelled, the tracking number stays on the line — reversal is Order Detail's flow, not this page's `[E-14]`.

### 6.4 Sheet / BI handoffs

**None from this page.** The Procurement Hub sheet pull happens from the Inbound Request list, not here (excluded 2026-08-02). No sheet is written, read, or refreshed by any action on this screen. If a pool item is routed to an inbound request, the sheet effect happens on that request `[DC-15]`.

### 6.5 Print pipeline `[G-4]`

**Not applicable.** This page has no Print button, produces no label or picking artifact, and has no local-print-agent dependency. A print-agent outage cannot block, delay, or degrade any action on this screen `[BR-31]`. Stated explicitly rather than omitted, because `[G-4]` is an owner-flagged mandatory inclusion and its absence here must be a decision on the record, not a gap.

---

## 7. Edge Cases & Error States

IDs are page-scoped and stable. `[E-1]`…`[E-31]` preserve the Lens-B plan numbering; `[E-32]`…`[E-46]` were added during drafting; `[E-47]`…`[E-72]` were added during the audit pass. **72 cases, no numbering gaps.** Every case states the expected behavior — none is left as "TBD" except the one path gated on a NO-DEFAULT decision (`[E-3]`), which is explicitly marked unspecified.

### 7.1 Intake boundary

| ID | Case | Expected behavior |
|---|---|---|
| **E-1** | Same tracking no. + barcode sent to the pool twice (double-click on View Orders send `[G-9]`, or a genuine rescan of an unresolved item) | Exactly **one** pool row exists. The server dedupes on `tracking_no + barcode` while an OPEN item exists; the second attempt gets "already in pool" feedback **upstream** on View Orders. Persist `[DC-2]`. Counts do not change |
| **E-2** | A row arrives **with** an order number (registrant typed a Coupang number but the lookup failed, e.g. a typo) | The Order No cell shows the number instead of `–`. It is **display-only** and does not influence candidate computation `[BR-12]`. M1's summary shows `Order no. {n}` in place of `No order number` |
| **E-3** | The tracking number could not be auto-collected (label destroyed) | **No behavior is specified.** `[PD-66 · OWNER-PENDING]` is NO-DEFAULT: if a tracking-less item were allowed, a "match" would have nothing to write onto the product line, breaking the `[DC-17]` rescan loop the whole flow depends on. Implementation must **escalate rather than choose**; this path has no acceptance criteria until the owner rules (§9.1) |
| **E-4** | Product unknown to the catalog | Cannot occur by design: View Orders M2b forces an autocomplete pick. The negative test lives in the View Orders spec; cross-reference only |
| **E-32** | The **same barcode** registered twice with **different** tracking numbers (two distinct parcels of the same SKU) | Two separate pool rows, each with its own candidate set. Not a duplicate — `[E-1]` dedupes on the pair, not the barcode alone. Both may match to different lines `[E-41]` |
| **E-39** | Slack registration notification fails at intake | The pool row **still exists and is still resolvable**. Notification is not the transaction `[PD-4 · OWNER-PENDING]`. Failure persisted `[DC-4]`, retried `[DC-24]`, dead-lettered on exhaustion `[DC-28]`. The only user-visible consequence is that no PIC was pushed — the row is still discoverable on the page |
| **E-45** | Memo contains very long text, newlines, or markup-like characters | Rendered as escaped plain text, wrapping within the cell. Never truncated with an ellipsis, never interpreted as markup, never breaks the table layout. The same string renders in full inside `[L-M1]`'s summary card |
| **E-46** | `Registered At` crosses a day boundary, or the client clock is skewed | Timestamps are server-generated and rendered in **KST**. The client clock is never used. Korea observes no DST, so `MM-DD HH:mm` is unambiguous within a year |
| **E-65** | An item stays open across a **year** boundary | `Registered At` still renders `MM-DD HH:mm` with no year — accepted, because an item that old is an operational failure the aging digest should already have escalated `[PD-61 · OWNER-PENDING]`. The digest and every persisted event carry full timestamps, so age is never computed from the display string `[DC-18]` |

### 7.2 Candidates and matching

| ID | Case | Expected behavior |
|---|---|---|
| **E-5** | Zero suspected orders (no Processing order contains the product) | Both the pool cell and M1's candidate panel render the explicit empty state: `No Processing order contains this product — check the order data upstream, or remove with a reason.` No search affordance appears `[PD-62 · OWNER-PENDING]`, `[BR-24]`. `Review & Match` stays enabled so the resolver can read the memo |
| **E-6** | Candidate went stale — the order left `Processing` (shipped / cancelled) between page load and confirm | M1 recomputes on open `[DC-6]`; confirm revalidates server-side `[BR-21]`. On mismatch: **red toast**, candidate list refreshes in place, modal stays open, **no partial writes**. Persist `[DC-13]` with `reason: stale_candidate` `[PD-6 · OWNER-PENDING]` |
| **E-7** | Two handlers open M1 for the same pool item; the first confirms | The second confirm is rejected ("already matched"). The loser's row disappears on refresh and both counts stay consistent. Persist `[DC-13]` with `reason: item_not_open` `[PD-7 · OWNER-PENDING]` |
| **E-8** | Match vs. removal race — A confirms a match while B confirms a removal | Exactly **one** terminal state wins, decided by the server-side state check. The loser gets a non-green toast naming what happened. Persist `[DC-13]` (`item_not_open`) or `[DC-16]` |
| **E-9** | Double-click `Match to this product` `[G-9]` | Exactly one line write, one pool closure, one comment, one Slack message. `#poolCount` decrements by exactly 1 (3→2, never 3→1). One toast cycle. Persist `[DC-12]` |
| **E-10** | The target product line already carries a tracking number | **Blocked** with an explicit error — no silent overwrite `[BR-18]`. Red toast names the existing number. Persist `[DC-13]` with `reason: line_occupied` |
| **E-11** | The same tracking number is already registered on a different order line in the same namespace | **Blocked** by the uniqueness check `[BR-19]`, `[PD-8 · OWNER-PENDING]`. Red toast names the other order. Persist `[DC-13]` with `reason: tracking_in_use`. An *inbound* number that coincides with this *outbound* number is a different namespace and does **not** trigger this block |
| **E-12** | Qty mismatch — pool qty 2 (the `medicube` 1+1 row) vs a candidate line of ×1 | **Allowed.** The match proceeds; `qty_mismatch: true` is recorded on `[DC-8]` and the auto-comment states it (`registered qty 2 against a ×1 line`) `[PD-65 · OWNER-PENDING]`, `[BR-17]` |
| **E-13** | The same SKU appears on two lines of one candidate order | M1 lists **one row per product line**, so both appear. They must be visually distinguishable — the `Included Product` cell shows the per-line qty (`×1`, `×2`), and the admin additionally renders the line's position/identifier when two lines are otherwise identical *(spec-authored)* |
| **E-14** | The matched order is later cancelled | The tracking number **stays** on the line. Reversal is the Order Detail / View Orders cancel flow, not this page's; this page holds no re-open path. Cross-reference `[PD-22 · OWNER-PENDING]` (Order Detail blocks cancelling an order with INBOUNDED lines until Cancel Inbound runs) |
| **E-15** | Rescan after a match | Scanning the same barcode/tracking on View Orders resolves normally. Persist `[DC-17]`. Mandatory inclusion #6 and the flow's exit condition |
| **E-33** | An unrequested-inbound item is mistakenly matched to a **customer** order | Not preventable by the predicate (the SKU genuinely appears in a Processing order). Consequences: the customer order's line carries a supplier parcel's tracking number, and the stock never enters Inventory. Recovery is manual on Order Detail. Mitigation is procedural: the registrant's `suspected inbound stock` memo is surfaced prominently in M1's summary card and must never be hidden or truncated `[L-M1]`, `[E-45]` |
| **E-34** | A candidate order has no PIC assigned | The candidate still renders with the PIC slot showing `–` *(spec-authored)*, and the registration Slack `[DC-4]` @mentions only the PICs that exist. A missing PIC never removes an order from the candidate set — that would violate `[BR-3]` |
| **E-40** | A candidate appears **after** registration (an order enters `Processing` later) | `[DC-6]` recompute adds it; the cell refreshes without a full-page reload `[G-2]`. No new Slack notification is sent for a late candidate in v1 — the daily digest `[PD-61 · OWNER-PENDING]` is the safety net |
| **E-41** | Two pool rows compete for the same candidate line (two parcels, one line) | The first match takes the line; the sibling row's cell recomputes `[BR-38]`. If the second is confirmed from a stale cell it hits `[E-10]` (`line_occupied`) and is blocked. The correct resolution is that the second parcel belongs to a different order or is an unrequested inbound arrival |
| **E-43** | The resolver's client list is stale — they confirm against a row the server has already closed | Server rejects with `item_not_open`; the client reloads the pool and both counts re-sync `[BR-33]`. No partial writes |
| **E-44** | The catalog has no Korean name for the SKU | The `Product Name KR` cell renders `–` in `.mut`. It never falls back to the English string, because a reader scanning for Korean text must be able to tell "no Korean name exists" from "the name happens to be Latin" `[BR-14]` |
| **E-47** | One barcode maps to more than one catalog product (recycled or shared barcode) | The predicate matches on the barcode as stored on the order line's product, so lines of **all** matching products appear as candidates. The `Included Product` cell is what disambiguates them; nothing is auto-excluded, because exclusion would violate `[BR-3]` and `[BR-4]` leaves no recovery. A shared barcode is a catalog-hygiene signal, not a page behavior |
| **E-48** | A candidate order goes **on-hold** (not shipped, not cancelled) between page load and confirm | It drops out of the set — the predicate admits `Processing` only. Confirm is rejected with `reason: stale_candidate`, exactly as `[E-6]`. Stated separately because "on-hold" reads to an operator as "still mine", and the rejection copy must name the actual status |
| **E-49** | The chosen product line is deleted on Order Detail between M1 open and confirm | Rejected with `[DC-13]` `reason: line_not_found`; red toast; candidate list refreshes; no writes |
| **E-50** | The candidate order is merged into another order (Order Management "Merge Orders") between M1 open and confirm | Rejected with `[DC-13]` `reason: order_not_found`; the refreshed candidate list shows the surviving order if it still satisfies the predicate. No auto-retarget — the resolver re-confirms explicitly |
| **E-51** | A match consumes a line that was also a candidate for a **different** pool row | The sibling row's candidate cell recomputes immediately `[BR-38]`, `[DC-6]`. If a resolver acts on a stale cell anyway, `[E-10]` blocks it server-side |
| **E-52** | One PIC owns two or more candidate orders for the same pool item | The registration Slack message @mentions that PIC exactly once `[BR-39]`; `[DC-4]` records the deduplicated mention list |
| **E-53** | A popular SKU yields many candidates (e.g. 30 Processing orders) | Every candidate renders — in the pool cell (no truncation) and in M1 (the candidate table scrolls inside the modal). No pagination and no "show more" `[BR-16]`. Only the **Slack payload** may cap the list, with an explicit `+N more` suffix so the message stays deliverable; the cap is a developer decision |
| **E-54** | Resolver == registrant (the same person registered and resolved) | The match proceeds and the auto-comment **still posts** (the audit trail is not optional); only the Slack mention is suppressed `[PD-16 · OWNER-PENDING]`, `[DC-27]` |
| **E-66** | Pool qty equals the candidate line qty (2 vs ×2) | Normal match. `qty_mismatch: false` on `[DC-8]`; the auto-comment carries no mismatch clause |
| **E-67** | Idempotency-key collision across two different pool items | Must be impossible: the key always contains `pool_item_id` `[BR-23]`. A build where two distinct items share a key is a defect, not a tolerated edge case |
| **E-68** | The order number typed at registration `[E-2]` belongs to an order that *is* `Processing` and *does* contain the product | It appears as a candidate through the normal predicate, not through the typed number. The typed value never short-circuits, pre-selects, or reorders the candidate set `[BR-12]`, `[BR-3]` |
| **E-69** | A candidate order line's product has no barcode stored | It simply never satisfies the predicate, so it never appears. No error, no warning — a null barcode is a catalog gap surfaced elsewhere |

### 7.3 Removal

| ID | Case | Expected behavior |
|---|---|---|
| **E-16** | Accidental `✕` tap | Prevented by the confirm dialog `[L-M2]` with a mandatory reason `[PD-60 · CONFIRMED 2026-08-03]`. **The wireframe ships the dialog since the 2026-08-03 pass that closed `WF-6`** — the `[WF]` tier now asserts the modal chain directly (QA-XDEL-01…03, QA-WFQ-03). In every case the removal event captures the **full row snapshot** `[DC-14]`, `[G-8]` |
| **E-17** | Unrequested-inbound route — `✕` pressed **before** the inbound request and invoice number exist | **Allowed, not blocked.** The order of operations stays procedural `[PD-64 · OWNER-PENDING]`. The removal is soft, so the item is recoverable from `[DC-14]`; a later correction is a comment on the inbound request `[BR-27]`. No hard guard is added |
| **E-18** | `✕` on a row another user has just matched | Mirror of `[E-8]`: server rejects, the row disappears on refresh, counts stay consistent. A duplicate removal under a consumed key is suppressed and logged `[DC-16]` |
| **E-35** | Removal reason `Routed to inbound request` with a non-existent, malformed, or already-INBOUNDED Inbound No. | Format is validated inline (`YYYYMMDDNNNN`). **Existence is not a hard gate:** a malformed value blocks the button; a well-formed but unknown value is accepted and recorded with `[DC-15]` `resolves:false`. An already-INBOUNDED request is accepted too — adding tracking numbers to it is separately blocked on the Inbound Request page `[PD-85 · OWNER-PENDING]`, so this page must not pretend the link resolved |
| **E-36** | The removal dialog is opened and cancelled | Zero side effects; declared non-event `[N-6]`. The row stays, counts unchanged, focus returns to `✕` |
| **E-42** | Session expires or the browser goes offline between opening `[L-M2]` and confirming | Confirm fails with a red toast; the row stays; no partial write. Retry with the same idempotency key is safe `[G-9]`. After re-auth the operator repeats the action |
| **E-60** | The removed item had comments attached | The comments **survive** the soft delete, stay queryable, and stay in the Comments hub with the entity label `Unrecognized pool`. Clicking one opens the matched order or a read-only historical view of the removed item, never a dead link `[PD-67 · OWNER-PENDING]`, `[BR-29]` |
| **E-70** | The supplied Inbound No. refers to a request for a **different** product | Accepted and recorded. `[DC-15]` still writes, flagged `resolves:false`, so the mismatch is visible on the Inbound Request page and resolved there by comment. No hard guard `[PD-64 · OWNER-PENDING]` |

### 7.4 UI and state consistency

| ID | Case | Expected behavior |
|---|---|---|
| **E-19** | Empty pool (0 items) | `.poolhead` reads `⚠ Unrecognized product pool · 0 items`; the table renders its header plus the empty-state row (§3.2.4); `[L-F2]` reads `Unrecognized pool · 0 items`. No layout collapse, no error styling |
| **E-20** | Count invariant after every mutation | `#poolCount` == `#poolCountBottom` == rendered open rows, after match, removal, and live arrival `[BR-33]`. The counter floors at 0 and must never render a negative |
| **E-21** | A new pool item arrives while the page is open | It appears at the top **without a full-page refresh** `[G-2]`; both counts increment; an empty-state row is replaced. Focus and scroll position are not disturbed `[N-8]`. Transport is a developer decision (§9.2 D-2) |
| **E-22** | Two confirming actions within 4 s → two toasts | Both texts must be readable; a toast must never be silently overwritten mid-read. Stack-vs-queue is a developer decision (§9.2 D-4) |
| **E-23** | Toast auto-dismiss | 4000 ms, then hidden. `position:fixed; top:18px; right:18px` — never click-blocking, never overlapping the Action column |
| **E-24** | M1 close paths | `Cancel`, header `✕`, overlay backdrop click, and `Esc` all close with **zero** side effects. Pool unchanged, counts unchanged, no events beyond the already-persisted `[DC-7]` |
| **E-31** | Comments-hub entry whose entity is `Unrecognized pool` (order-less) is clicked | Opens this page focused on that row; if the item is no longer open, opens the matched order instead `[PD-67 · OWNER-PENDING]`, `[BR-29]` |
| **E-55** | Unread mention count exceeds 99 | The badge renders `99+`; the persisted count stays exact `[DC-22]`. The badge must never render a value wide enough to break the nav layout |
| **E-56** | `#inbox1` is open and the user clicks elsewhere, or presses `Esc` | The dropdown closes. The wireframe binds neither handler (§2.4.8); the admin must bind both `[BR-40]`. Neither is a persisted event `[N-3]` |
| **E-63** | Viewport narrower than the table's 1280 px canvas | `.mockwrap` scrolls horizontally. No column is hidden, collapsed, or reordered, and the `Action` column always remains reachable by scrolling |
| **E-64** | Very long product name, Korean name, or memo | Cells wrap and the row grows taller. The count invariant, the row highlight, and both action buttons stay intact and reachable `[E-45]` |
| **E-72** | The server returns pool items but client rendering throws | Because both counters are derived from the **rendered** collection `[BR-41]`, the failure surfaces as a visible mismatch or an error state — never as a counter that reports rows nobody can see. Persist `[DC-25]` if the failure is fetch-side |

### 7.5 Network, browser, and integration failure

| ID | Case | Expected behavior |
|---|---|---|
| **E-25** | Network failure mid-match (request sent, no response) | The button enters a pending/disabled state. The row is **not** removed until the server confirms. On timeout: red toast. Retry with the same idempotency key is safe and produces no duplicate `[G-9]` |
| **E-26** | The comment post or the Slack notify fails **after** a successful line write | The match **stands** — steps 4–6 are non-blocking `[BR-20]`, `[PD-4 · OWNER-PENDING]`. The row is removed, the success toast still fires, and the failure is persisted `[DC-11]` and retried `[DC-24]`. It is **not** a rollback and must not be reported to the operator as a failed match |
| **E-27** | The registrant is deactivated / has no Slack mapping | The comment posts with a plain-text name; the Slack mention degrades gracefully with no hard failure. Persist `[DC-26]` |
| **E-28** | The pool fetch fails on page load | An error state with a retry affordance — never a blank page and never a silent `0 items`, which would be indistinguishable from a healthy empty pool. Persist `[DC-25]` |
| **E-37** | The daily aging digest runs against an empty pool | No Slack message is sent (`[DC-19]` fires only when `items[]` is non-empty) `[PD-61 · OWNER-PENDING]`. `[DC-18]` is still recorded with `items: []` so the job's execution is auditable |
| **E-38** | The product was renamed, merged, or deleted in the catalog after the pool item was registered | The row keeps rendering the **snapshotted** names, size, and barcode from `[DC-1]` and never blanks out `[BR-43]`. Candidate computation uses the barcode, which survives a merge; if the barcode no longer maps to any catalog product, the candidate list is empty and `[E-5]` applies |
| **E-57** | The operator presses browser Refresh / F5 | Permitted. `[G-2]` prohibits **programmatic** post-action refresh, not a user-initiated reload `[BR-44]`. State is re-fetched from the server and both counters re-derive |
| **E-58** | Browser Back returns to this page after navigating to an order | The page re-fetches; a matched or removed row must **not** reappear from cache. The pool fetch is served no-store *(spec-authored)* |
| **E-59** | The same user has this page open in two tabs; a match happens in tab A | Tab B removes the row and re-syncs both counters within the live-update transport's interval `[E-21]`. If tab B is stale and confirms anyway, `[E-43]` applies — the server is the arbiter, never the newest tab |
| **E-61** | Slack dispatch keeps failing until the retry budget is exhausted | The failure is dead-lettered and persisted `[DC-28]`, `[BR-42]`. The match or removal it belonged to **stands**; no UI badge is added, because an unowned alert surface on this page was explicitly rejected (§6.1). Ops discover it from the persisted record |
| **E-71** | The resolver has no Slack account | Every on-page action works normally. Only outbound mentions targeting that user degrade, exactly as `[E-27]` |

### 7.6 Permissions and scale

| ID | Case | Expected behavior |
|---|---|---|
| **E-29** | Who may match, and who may remove? | v1: **any authenticated operator may do both.** No role gate `[G-15]`, `[PD-1 · OWNER-PENDING]`. The actor is recorded on every event `[G-8]` |
| **E-30** | The pool grows well past the design assumption (> 20 rows) | Plain vertical scroll. **No pagination, no search, no filters** are added — the 2026-07-23 decision stands `[BR-16]`. Rendering performance is a developer concern; growth is an operational signal that something upstream is broken, not a UI requirement |

### 7.7 Accessibility and keyboard operation

| ID | Case | Expected behavior |
|---|---|---|
| **E-62** | Keyboard-only operation | Tab reaches `Review & Match` then `✕` in DOM order; `Enter`/`Space` activate. Opening a modal moves focus into it and traps it; closing returns focus to the trigger. `Esc` closes both modals and `#inbox1`. `✕` exposes an accessible name equivalent to `title="Remove from list"`. Toasts are announced through a live region so the corner does not have to be watched `[BR-40]`, §3.14 |

### 7.8 Not applicable, stated explicitly

- **Printer offline** — no print surface on this page `[BR-31]`, `[G-4]` N/A. A print-agent outage has zero effect here.
- **Scanner disconnected / focus lost / page refreshed between scans** — no scan input on this page `[BR-30]`, `[G-1]` N/A.
- **Audio device unavailable / AudioContext suspended** — no audio on this page `[G-3]` N/A; `[PD-2 · OWNER-PENDING]` cannot land here in either direction.
- **Over-scan, partial arrival, damaged-goods quantity edits, expected-qty reason enum** — inbound-quantity concepts belonging to View Orders State 6 and Inbound Request `[G-11]`, not here.
- **Sample-set assignment, location assignment, audit mode, JIT residual stock** — no such surface exists on this page (§2.6 rows 5, 9, 10, 11).

---

## 8. QA Acceptance Criteria

### 8.0 How to run this section

**Tags.**
- **[WF]** — executable **today** against the live wireframe at `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/tracking-missing/` using only the selectors, labels, and strings given. An AI agent must be able to run these with no further questions. **Every `[WF]` scenario in this document runs against that one URL** — no `[WF]` scenario targets another page's wireframe.
- **[ADMIN]** — requires the real admin: server state, persistence, Slack delivery, cross-page navigation, or an affordance the wireframe does not have.
- **(neg)** — negative test (asserts something is blocked, absent, rejected, or unchanged).
- **BLOCKED** — a scenario that cannot have a verdict until an owner decision lands. Report as BLOCKED, never as PASS or FAIL.

**Reset procedure for [WF] runs.** The wireframe holds no state. **Reload the page** to restore the baseline. Every `[WF]` scenario assumes the baseline below unless it explicitly continues a previous one.

**Baseline (post-reload).** `#poolCount` reads `3`; `#poolCountBottom` reads `3`; three `.row-hit` rows exist; the first is `#poolrow1`; `#m-match` does not have class `open`; `#m-remove` does not have class `open`; `#inbox1` does not have class `open`; `#matchToast` has `display:none`; annotations are visible.

**Selector conventions.** IDs are used verbatim (`#poolCount`, `#poolCountBottom`, `#poolrow1`, `#m-match`, `#m-remove`, `#rmSummary`, `#rmReason`, `#rmInbound`, `#rmInboundErr`, `#rmMemo`, `#rmConfirm`, `#matchToast`, `#inbox1`, `#annoToggle`). Buttons are addressed by exact accessible text where possible (`Review & Match`, `Match to this product`, `Cancel`, `Remove from pool`, `Mark all read`) and by class where the label is a glyph (`.xdel`, `.star`, `.x`).

Six mechanical rules that a text assertion in this section depends on. They apply to **every** scenario below unless the scenario says otherwise:

1. **Annotation dots are stripped before any text comparison.** `.dot` elements are demo chrome (§2.3) and three of them sit *inside* `<th>` cells, so the raw `textContent` of the `Product Name` header is `Product Name4`. Every "text is exactly X" / "reads X" assertion is made against the element's text **with all `.dot` descendants removed**. This is why the baseline can keep annotations visible.
2. **`table.tbl` matches two elements** — the pool table and the candidate table inside `#m-match`. Unless a scenario names `#m-match`, `table.tbl` means the **first** (the pool table), and `the <tbody>` means that table's tbody. Pool rows 2 and 3 are addressed as `table.tbl:first-of-type tbody tr:nth-of-type(2)` / `:nth-of-type(3)`.
3. **`.mockwrap` matches two elements and they nest.** At a narrowed viewport **both** overflow (outer 1280→viewport, inner 1457→1248) and **both** must be scrolled to bring the `Action` column into view; scrolling only the outer one leaves `.xdel` off-screen. Applies to QA-A11Y-05.
4. **`.it` items are addressed positionally, not with `:nth-of-type`.** `.paneheader` is also a `<div>` inside the pane, so `.it:nth-of-type(1)` selects nothing. "the first item" means the first element matching `.it` in document order.
5. **"Exactly" means the named node's own text**, not its subtree, whenever the scenario says so explicitly (e.g. QA-M1-01's leading text node). Where a scenario says "contains", containment is asserted.
6. **Event-listener assertions need a CDP probe.** Any clause of the form "no click handler is bound" is unverifiable from the DOM; run `DOMDebugger.getEventListeners` over the named elements. Where CDP is unavailable, assert only the observable half the scenario names and record the listener clause as not-run — never as FAIL.

**Totals: 168 scenarios — 66 [WF], 102 [ADMIN]. Negative scenarios: 61 (36.3%), above the 25% floor.** Of these, **one** (QA-VAL-10) is `BLOCKED` and carries no verdict; it is counted inside the 168 and inside the 102 `[ADMIN]`. *(Re-counted after the 2026-08-03 re-baselining: the WF-6/WF-NEW-D/WF-NEW-E fixes rewrote scenario bodies — QA-XDEL-01…03, QA-WFQ-02/03/07, QA-CMT-03/05, QA-LOAD-07/09/11/12, QA-EMPTY-01, QA-VAL-06, QA-XDEL-04/06, QA-NEG-03's note, QA-DATA-09 — but no scenario was added, retired, re-tiered, or re-tagged, so every total and per-block count below is unchanged.)*
Per-block counts: LOAD 12 · ROW 16 · SUS 13 · M1 13 · MATCH 10 · XDEL 12 · CMT 15 · FURN 10 · NEG 15 · VAL 12 · EMPTY 6 · XPG 9 · DATA 13 · A11Y 5 · WFQ 7 = 168.
Per-block `[WF]`: LOAD 11 · ROW 9 · SUS 5 · M1 9 · MATCH 5 · XDEL 3 · CMT 7 · FURN 5 · NEG 1 · VAL 0 · EMPTY 2 · XPG 0 · DATA 0 · A11Y 2 · WFQ 7 = 66.
Per-block negatives: LOAD 4 · ROW 4 · SUS 4 · M1 3 · MATCH 0 · XDEL 3 · CMT 3 · FURN 3 · NEG 15 · VAL 10 · EMPTY 2 · XPG 4 · DATA 3 · A11Y 0 · WFQ 3 = 61.

### 8.1 Block LOAD — page load and inventory (`[L-0]`, `[L-1]`, `[L-S1-Fa]`, `[L-S1-Fb]`)

**QA-LOAD-01 [WF]** — Given the page is loaded, Then the `<h2>` text is exactly `WMS - Unrecognized Tracking List`.

**QA-LOAD-02 [WF]** — Given the page is loaded, Then the `.sub` element contains `Unrecognized & missing-tracking status` And its `.mut` continuation contains `Coupang creates the order number immediately but generates the tracking number a few hours later`.

**QA-LOAD-03 [WF]** — Given the page is loaded, Then `.poolhead` is present with computed background `rgb(255, 251, 214)` (`#FFFBD6`) and border colour `rgb(245, 158, 11)` (`#F59E0B`), And its bold lead text reads `⚠ Unrecognized product pool · 3 items`.

**QA-LOAD-04 [WF]** — Given the page is loaded, Then the pool table's `<th>` texts — **each taken with its `.dot` annotation child removed** (§8.0 rule 1; three headers carry one) — are exactly, in order: `Tracking No`, `Order No`, `Product Name`, `Product Name KR`, `Size`, `Barcode`, `Qty`, `Memo`, `Registrant (Center)`, `Registered At`, `Suspected Orders (Auto-matched)`, `Action` — 12 headers, no more, no fewer. *(Without the strip the raw texts are `Product Name4`, `Suspected Orders (Auto-matched)2`, `Action3`; that is demo chrome, not a defect.)*

**QA-LOAD-05 [WF]** — Given the page is loaded, Then `#poolCount` reads `3` And `#poolCountBottom` reads `3` And the **pool table's** `<tbody>` (`table.tbl:first-of-type tbody`, §8.0 rule 2 — a second `table.tbl tbody` exists inside `#m-match`) contains exactly 3 `<tr>` elements, all carrying class `row-hit` `[BR-33]`, `[BR-36]`.

**QA-LOAD-06 [WF] (neg)** — Given the page is loaded, Then no element matching `.searchbar`, `.pager`, `.bulkbar`, `.picava`, `.picname`, `.cntchip`, `.wait`, `.slack-pill`, `.logsec`, or `input[type=checkbox]` is **rendered** anywhere in the page body — the 2026-07-23 removals must not exist `[L-S1-Fa]`. (Unused CSS **class definitions** are permitted in the wireframe file; the assertion is on rendered DOM.)

**QA-LOAD-07 [WF]** — Given the page is loaded, Then the `.legend ol` contains exactly **6** `<li>` elements whose `.n` badges read `0`, `1`, `2`, `3`, `4`, `5` in order, And exactly **8** elements with class `dot` exist in the document (the six page dots plus the `M1` dot inside `#m-match` and the `M2` dot inside `#m-remove`) — the page's declared legend-unit count (§2.1, updated 2026-08-03).

**QA-LOAD-08 [WF]** — Given the page is loaded, Then exactly **2** `<p>` paragraphs follow the legend `<ol>`, the first containing `2026-07-23 simplification decision:` `[L-S1-Fa]` and the second containing `(Confirmed 2026-08-02) Unrequested inbound shipments also use this pool` `[L-S1-Fb]`.

**QA-LOAD-09 [WF] (neg)** — Given the page is loaded, Then **zero** `<input>` elements are rendered anywhere in the document **outside `#m-remove`** — no scan input `[BR-30]`, no unified search bar `[BR-16]`, no in-page register form `[BR-1]`, and no inline tracking-number field. `#m-remove` ships exactly **one** `<input>` (`#rmInbound`, hidden until reason = `Routed to inbound request`, §3.8). *(Updated 2026-08-03; the admin additionally adds exactly one more input, the Comments-hub search `[L-5]`, and nothing else.)*

**QA-LOAD-10 [WF] (neg)** — Given the page is loaded, Then no rendered element has text `Print`, no `<audio>` element exists, no script constructs an `AudioContext`, And the only elements carrying class `btn-green` are the two `Match to this product` buttons inside `#m-match` — this page has no print surface `[BR-31]` and no outbound-class button `[G-3]`, §2.6 rows 3–4.

**QA-LOAD-11 [WF]** — Given the page is loaded, Then `.wf-bar h1` reads `WMS 2.0 · Unrecognized Tracking Wireframe`, a `.wf-tab` button reads `Modal: Match Review (M1)`, another reads `Modal: Remove Confirm (M2)`, and `#annoToggle` reads `Hide annotations` — demo chrome (§2.3).

**QA-LOAD-12 [ADMIN] (neg)** — Given the production admin page, Then no `.wf-bar`, no `.dot`, no `.legend`, and no button labelled `Modal: Match Review (M1)` or `Modal: Remove Confirm (M2)` exists; `[L-M1]` opens **only** from a row's `Review & Match` and `[L-M2]` **only** from a row's `✕` (§2.3, `[N-4]`).

### 8.2 Block ROW — pool row content (`[L-1]`, `[L-4]`)

**QA-ROW-01 [WF]** — Given `#poolrow1`, Then its first cell reads `10323100841207` And its second cell reads `–` (U+2013) rendered in the `--ink-3` gray `rgb(126, 124, 131)` `[BR-12]`.

**QA-ROW-02 [WF]** — Given `#poolrow1`, Then its `Product Name` cell contains a `<b>` whose text is `COSRX`, followed by ` Advanced Snail 96 Mucin Power Essence, 100ml` `[L-4]`.

**QA-ROW-03 [WF]** — Given `#poolrow1`, Then its `Product Name KR` cell contains a `<b>` whose text is `COSRX`, followed by ` 어드밴스드 스네일 96 뮤신 에센스` — the Korean string is preserved verbatim and is neither translated nor transliterated `[G-6]`.

**QA-ROW-04 [WF]** — Given the third pool row, Then its `Product Name` cell contains `<b>medicube</b>` And its `Product Name KR` cell contains `<b>Medicube</b>` followed by ` 제로 모공 패드 2.0 (1+1)` — catalog casing is preserved and the two columns may legitimately differ `[BR-14]`.

**QA-ROW-05 [WF]** — Given the three rows, Then their `Size` cells read `100ml`, `250ml`, `70ea`; their `Barcode` cells read `8809416470726`, `8809640733458`, `8809894261234`; their `Qty` cells read `1`, `1`, `2`.

**QA-ROW-06 [WF]** — Given the three rows, Then their `Memo` cells read `Box label damaged`, `–`, `Looks like a 1+1 set` — the empty memo renders the literal `–`, not an empty cell.

**QA-ROW-07 [WF]** — Given the three rows, Then their `Registrant (Center)` cells read `Miranti`, `Dean`, `Dean` And their `Registered At` cells read `07-13 10:12`, `07-13 09:48`, `07-13 09:30`, matching the `MM-DD HH:mm` KST format `[E-46]`.

**QA-ROW-08 [WF]** — Given the three rows, Then they are ordered by `Registered At` descending (10:12, 09:48, 09:30) And no sortable-column affordance is present `[BR-16]`: **(a)** no `<th>` renders a sort glyph (`▲ ▼ ↑ ↓ ⇅`), **(b)** no `<th>` carries an `onclick`, `data-sort`, or `aria-sort` attribute, and **(c)** no `<th>` has a bound `click` listener — clause (c) requires a `DOMDebugger.getEventListeners` probe over the 12 `<th>` elements (§8.0 rule 6, expected result `[]` on every one); without CDP, run (a) and (b) and record (c) as not-run.

**QA-ROW-09 [WF]** — Given the page is loaded, Then exactly one `<tr>` carries an `id` attribute, and it is `poolrow1` (§2.4.9 demo limitation).

**QA-ROW-10 [ADMIN]** — Given the admin, Then **every** rendered pool row carries `id="poolrow-{pool_item_id}"`, And navigating to `#poolrow-{id}` scrolls that row into view and gives it focus `[PD-67 · OWNER-PENDING]`, `[BR-29]`.

**QA-ROW-11 [ADMIN]** — Given a pool item registered while the catalog name was `COSRX Advanced Snail 96 Mucin Power Essence, 100ml`, When the catalog product is renamed afterwards, Then the pool row still renders the **intake snapshot** name, not the new one `[BR-43]`, `[E-38]`.

**QA-ROW-12 [ADMIN] (neg)** — Given a pool item whose catalog product is subsequently **deleted**, Then the row still renders its snapshotted name, size, and barcode and does **not** blank out or error `[BR-43]`, `[E-38]`; And if the barcode no longer maps to any catalog product the candidate cell renders the `[E-5]` empty state rather than a failure.

**QA-ROW-13 [ADMIN] (neg)** — Given a pool holding 25 open items, Then all 25 rows render in one plain vertically scrolling table, And **no** pagination control, **no** page-size selector, **no** search input, and **no** column filter appears anywhere on the page `[E-30]`, `[BR-16]`; And both counters read `25` `[BR-33]`.

**QA-ROW-14 [ADMIN] (neg)** — Given a pool item whose catalog product has **no** Korean name, Then the `Product Name KR` cell renders the literal `–` in `.mut` gray, And it does **not** fall back to the English name, the brand alone, an empty cell, or a placeholder `[E-44]`, `[BR-14]`.

**QA-ROW-15 [ADMIN] (neg)** — Given a pool item whose memo is 500 characters long and contains newlines and the literal text `<b>set</b>`, Then the `Memo` cell renders the string as **escaped plain text** (the characters `<b>` are visible; no bold is applied and no element is created), wraps within the cell, and is **never** truncated with an ellipsis or a "more" affordance; And the identical full string renders in `[L-M1]`'s summary card `[E-45]`, `[E-33]`.

**QA-ROW-16 [ADMIN]** — Given a pool item with a 120-character English name, a 120-character Korean name, and the long memo of QA-ROW-15, Then those cells wrap and the row grows taller, And the row still carries `.row-hit` with its highlight intact `[BR-36]`, And both `Review & Match` and `✕` remain rendered, clickable, and inside the `Action` cell, And `#poolCount` == `#poolCountBottom` == the rendered row count `[E-64]`, `[BR-33]`.

### 8.3 Block SUS — Suspected Orders column (`[L-2]`)

**QA-SUS-01 [WF]** — Given `#poolrow1`, Then its `Suspected Orders (Auto-matched)` cell contains exactly 2 `<div>` candidate lines.

**QA-SUS-02 [WF]** — Given `#poolrow1`'s first candidate line, Then it reads `Dean · Order 414230 · JIT (Naver) · Processing`, with `Dean` in `<b>`, `Order 414230` computed colour `rgb(13, 110, 253)` (`#0D6EFD`) and `font-weight: 700`, and the trailing `JIT (Naver) · Processing` in one `span.mut` computed `rgb(126, 124, 131)` — the declared `[G-5]` page delta (§3.3), not a defect.

**QA-SUS-03 [WF]** — Given `#poolrow1`'s second candidate line, Then it reads `Egita · Order 413871 · JIT (Official Mall) · Processing`.

**QA-SUS-04 [WF]** — Given rows 2 and 3, Then each contains exactly 1 candidate line, reading `Harshit · Order 414102 · JIT (Naver) · Processing` and `Miranti · Order 413998 · JIT (Official Mall) · Processing` respectively.

**QA-SUS-05 [WF] (neg)** — Given each of the **four** trailing `span.mut` elements in the pool's `Suspected Orders (Auto-matched)` cells — the `{route (channel)} · {status}` clause of every candidate line, i.e. `JIT (Naver) · Processing` ×2 and `JIT (Official Mall) · Processing` ×2 — Then each has computed `background-color: rgba(0, 0, 0, 0)`, `border-style: none`, `padding: 0px`, and computed `color: rgb(126, 124, 131)` (`--ink-3`, non-bold) — the pool cell's route clause is **muted running text, never a coloured pill**: `[G-5]`'s no-pill prohibition holds, its bold-black badge form does not reach this surface (declared page delta, §3.3, `[BR-15]`). *(The badge form of the route label exists only in `[L-M1]`'s `Channel` cells and is asserted separately by QA-M1-10; there are **zero** `.tag-jit` / `.tag-smartbuy` / `.tag-wholesale` / `.tag-partnership` elements outside `#m-match`, so a page-wide `.tag-*` sweep would pass vacuously and must not be used as the assertion.)*

**QA-SUS-06 [ADMIN]** — Given a pool item whose barcode appears in an order that is **not** in `Processing`, When the candidate set is computed, Then that order is absent from the set `[BR-3]`; And `[DC-5]` persists the computed set with the excluded order absent.

**QA-SUS-07 [ADMIN]** — Given a pool item with zero candidates, When an order containing that product later enters `Processing`, Then the candidate cell gains the new candidate **without a page reload** `[G-2]`, `[E-40]`; And `[DC-6]` persists `{old_set: [], new_set: [1 entry], trigger: order_status_change}`; And **no** new `#unrecognized-tracking` message is sent for the late candidate.

**QA-SUS-08 [ADMIN] (neg)** — Given a pool item with one candidate, When that order moves to **on-hold**, Then it is removed from the candidate set (the predicate admits `Processing` only) `[E-48]`; And `[DC-6]` persists the removal with `trigger: order_status_change`; And a confirm attempted from a stale client is rejected with `reason: stale_candidate` whose message names the actual status `on-hold`.

**QA-SUS-09 [ADMIN]** — Given a pool item whose candidates include two orders owned by the same PIC, When the registration Slack message is composed, Then that PIC is @mentioned exactly **once** `[BR-39]`, `[E-52]`; And `[DC-4]` records the deduplicated `mentioned_pic_ids[]`.

**QA-SUS-10 [ADMIN]** — Given a pool item with 30 candidate lines, Then the pool cell renders all 30 with no truncation and no "show more", And `[L-M1]`'s candidate table renders all 30 and scrolls inside the modal body, And no pagination control appears `[E-53]`, `[BR-16]`; And `[DC-4]` may cap the Slack list, recording `truncated_candidate_count`.

**QA-SUS-11 [ADMIN]** — Given a candidate order carrying the same SKU on **two** separate lines, Then the candidate set contains **two** entries for that order, distinguishable by their per-line qty and line identifier `[E-13]`, `[BR-5]`.

**QA-SUS-12 [ADMIN] (neg)** — Given two catalog products that share one barcode, Then candidates from **both** products appear and neither is auto-excluded `[E-47]`, `[BR-3]`; And the `Included Product` cell is what distinguishes them.

**QA-SUS-13 [ADMIN] (neg)** — Given a `Processing` order containing a product whose catalog record stores **no barcode**, and a pool item registered for a different SKU, Then that order never enters the candidate set for any pool item — it simply fails the predicate `[E-69]`, `[BR-3]` — And **no** error, warning, banner, or toast is raised on this page about the null barcode; And `[DC-5]` / `[DC-6]` record the set without it and without an error field.

### 8.4 Block M1 — Review & Match modal (`[L-3]`, `[L-M1]`)

**QA-M1-01 [WF]** — Given the baseline, When I click the `Review & Match` button inside `#poolrow1`, Then `#m-match` gains class `open` And its `<header>`'s **leading text node** is exactly `Review & Match — Unrecognized Product` (em dash U+2014), followed by the `✕` close button (`button.x[data-close]`) that is also a child of that `<header>`. *(The header's full `textContent` is therefore `Review & Match — Unrecognized Product✕`; assert the leading text node, not the subtree — §8.0 rule 5. The same `✕` is the control QA-EMPTY-05 clicks.)*

**QA-M1-02 [WF]** — Given the baseline, When I click the wf-bar button labelled `Modal: Match Review (M1)`, Then `#m-match` gains class `open` (demo entry path only; declared non-event `[N-4]`).

**QA-M1-03 [WF]** — Given `#m-match` is open, Then the summary card contains `<b>COSRX</b>` followed by ` Advanced Snail 96 Mucin Power Essence, 100ml`, And a `.mut` line reading exactly `Barcode 8809416470726 · Tracking 10323100841207 · No order number · 1 unit · Registered by: Miranti (Center) 07-13 10:12 · Memo "Box label damaged"`.

**QA-M1-04 [WF]** — Given `#m-match` is open, Then the candidate panel's bold heading is `Suspected orders (auto-matched)` And its `.mut` explanation contains `Match by selecting a product line, not the order`.

**QA-M1-05 [WF]** — Given `#m-match` is open, Then the candidate table headers are exactly `Order`, `PIC`, `Channel`, `Included Product`, and one empty header — 5 columns.

**QA-M1-06 [WF]** — Given `#m-match` is open, Then it contains exactly 2 candidate rows — (`414230`, `Dean`, `JIT (Naver)`, `COSRX Snail 96 Essence ×1`) and (`413871`, `Egita`, `JIT (Official Mall)`, `COSRX Snail 96 Essence ×1`), each with `COSRX` in `<b>` — And each row's last cell holds a button labelled exactly `Match to this product`.

**QA-M1-07 [WF]** — Given `#m-match` is open, Then the `.note` block's text contains `tracking number 10323100841207 is registered to the selected product line`, `this item disappears from the pool`, and `"@Miranti (unrecognized registrant) Matched the unrecognized product (COSRX Snail 96 Essence) to this order"`.

**QA-M1-08 [ADMIN]** — Given the admin, When I click `Review & Match` on the **second** pool row, Then `#m-match` opens scoped to **that** row's item (Anua toner, tracking `10323100838455`, 1 candidate: Harshit / 414102) — not row 1's *(the wireframe always shows row 1; §2.4.1 demo limitation, not a bug)*; And `[DC-7]` persists a `review_opened` event carrying that row's candidate snapshot.

**QA-M1-09 [WF] (neg)** — Given `#m-match` is open, Then its `.foot` contains exactly **one** button, labelled `Cancel`, And no element inside the modal is labelled `Confirm`, `OK`, `Save`, or `Match` on its own — the per-candidate button is the only confirming action (§3.7).

**QA-M1-10 [WF] (neg)** — Given `#m-match` is open, Then the `Channel` cells render `JIT (Naver)` / `JIT (Official Mall)` with transparent computed background, zero padding, and ink-coloured text — no pill inside the modal either `[G-5]`, `[BR-15]`.

**QA-M1-11 [ADMIN]** — Given `[L-M1]` is open in the admin, When I press `Esc`, Then the modal closes with zero side effects And focus returns to the `Review & Match` button that opened it `[BR-40]`, `[E-24]`, `[E-62]`.

**QA-M1-12 [ADMIN]** — Given the admin, When I open `[L-M1]` for one pool item twice in a row, Then **two** `[DC-7]` events are persisted, each with its own `candidate_set_snapshot` and `opened_at`, And only the later snapshot is used as the diff baseline for a stale-candidate rejection (§3.4.1).

**QA-M1-13 [ADMIN] (neg)** — Given a pool item registered with the memo `suspected inbound stock — no order expected` and a candidate set that is **not** empty (the SKU genuinely appears in a `Processing` customer order), When `[L-M1]` opens, Then the summary card renders the memo fragment `· Memo "suspected inbound stock — no order expected"` **in full**: not truncated, not ellipsised, not collapsed behind a toggle, and not hidden at any viewport width `[E-33]`, `[E-45]`, §3.7(a); And the candidate is still offered — the predicate does not and must not filter it out `[BR-3]` — so the memo is the only signal that stops the match. *(This is the mitigation `[E-33]` names; if the memo can be visually suppressed, the mitigation does not exist.)*

### 8.5 Block MATCH — happy path (`[L-3]`, `[L-M1]`, `[L-F1]`, `[E-20]`)

**QA-MATCH-01 [WF]** — Given `#m-match` is open from `#poolrow1`, When I click the first `Match to this product` button, Then `#m-match` no longer has class `open`.

**QA-MATCH-02 [WF]** — Continuing QA-MATCH-01, Then `#poolrow1` is absent from the DOM.

**QA-MATCH-03 [WF]** — Continuing QA-MATCH-01, Then `#poolCount` reads `2` And `#poolCountBottom` reads `2` `[BR-33]`.

**QA-MATCH-04 [WF]** — Continuing QA-MATCH-01, Then `#matchToast` has computed `display: flex` And contains the exact strings `✓ Matched to Order 414230 · COSRX Snail 96` and `Tracking 10323100841207 registered · removed from pool · @Miranti notified via Slack` And its computed background is `rgb(25, 135, 84)` (`#198754`).

**QA-MATCH-05 [WF]** — Continuing QA-MATCH-01, Then within 4.5 s `#matchToast` has computed `display: none` `[E-23]`, And no full-page navigation or reload occurred (the `document` was never unloaded) `[G-2]`, `[BR-34]`.

**QA-MATCH-06 [ADMIN]** — Given the admin and a pool item with tracking `10323100841207`, When a resolver confirms a match to order `414230` line L, Then the order line's tracking field equals `10323100841207` `[DC-9]`; And the pool item's status is `MATCHED` with resolver, `resolved_at`, `selected_order_id`, `selected_line_id`, and the candidate set at confirm `[DC-8]`; And the order's comment history contains exactly one system comment `@Miranti (unrecognized registrant) Matched the unrecognized product (COSRX Snail 96 Essence) to this order` `[DC-10]`; And exactly one message was delivered to `#fulfillment-admin-comments` (`C0BMGEWM5QA`) mentioning Miranti `[DC-11]`.

**QA-MATCH-07 [ADMIN]** — Given the pool item's qty is 2 and the selected line's qty is 1 (the `medicube` case), When the match is confirmed, Then the match **succeeds** `[PD-65 · OWNER-PENDING]`; And `[DC-8]` carries `qty_mismatch: true` with `pool_qty: 2` and `selected_line_qty: 1`; And the auto-comment body additionally states the mismatch `[E-12]`, `[BR-17]`.

**QA-MATCH-08 [ADMIN]** — Given the pool item's qty is 2 and the selected line's qty is also 2, When the match is confirmed, Then `[DC-8]` carries `qty_mismatch: false` And the auto-comment carries **no** mismatch clause `[E-66]`.

**QA-MATCH-09 [ADMIN]** — Given two pool rows whose candidate sets both include order `414230` line L, When the first row is matched to that line, Then the second row's candidate cell recomputes and no longer offers line L `[BR-38]`, `[E-51]`; And `[DC-6]` persists with `trigger: sibling_resolution`.

**QA-MATCH-10 [ADMIN]** — Given the resolver **is** the registrant, When the match is confirmed, Then the auto-comment **is still posted** `[DC-10]` And the Slack mention is suppressed `[PD-16 · OWNER-PENDING]` And `[DC-27]` is persisted with `reason: "self_notification"` `[E-54]`.

### 8.6 Block XDEL — removal (`[L-3]`, `[L-M2]`, `[E-16]`)

**QA-XDEL-01 [WF]** — Given the baseline, When I click the `✕` button (`.xdel`, `title="Remove from list"`) in the second pool row (Anua toner, tracking `10323100838455`), Then `#m-remove` gains class `open`, its `<header>`'s leading text node is exactly `Remove this item from the pool?`, `#rmSummary` contains `Anua` and `10323100838455` (and no `Memo` fragment — that row's memo is `–`), `#rmConfirm` is disabled, And **no row has been removed**: three rows remain and both counters still read `3` `[L-M2]`, `[PD-60 · CONFIRMED 2026-08-03]`. When I then select `Registered by mistake` and click `Remove from pool`, Then that row is absent from the DOM, `#poolCount` and `#poolCountBottom` both read `2`, And `#matchToast` shows `✓ Removed from pool · Anua Heartleaf 77% Soothing Toner, 250ml` with sub-line `Reason: Registered by mistake · Tracking 10323100838455`. *(Rewritten 2026-08-03 — the pre-fix body asserted the `WF-6` one-click removal.)*

**QA-XDEL-02 [WF]** — Given `#m-remove` is open from a row's `✕` with a reason selected, When I click `Cancel` (and, separately, the header `✕`, and a click on the overlay backdrop), Then the modal closes, all three rows remain, both counters still read `3`, And `#matchToast` remained `display:none` throughout `[E-36]`, `[N-6]`. *(Rewritten 2026-08-03 — the pre-fix body asserted the absence of any dialog.)*

**QA-XDEL-03 [WF]** — Given the baseline, When I remove each of the three rows in turn via `✕` → reason `No action needed` → `Remove from pool`, Then after the third removal `#poolCount` and `#poolCountBottom` both read `0` And neither renders a negative value `[E-20]`.

**QA-XDEL-04 [ADMIN]** — Given the admin, When I click `✕` on a pool row, Then a modal titled `Remove this item from the pool?` opens, its confirm button (`Remove from pool`) is **disabled**, and a required reason `<select>` shows `Select a reason…` with exactly the options `Registered by mistake`, `Routed to inbound request`, `No action needed`, `Other`, in that order `[PD-60 · CONFIRMED 2026-08-03]`, `[L-M2]`. *(The wireframe now demonstrates the same chain — QA-XDEL-01; this row binds the admin.)*

**QA-XDEL-05 [ADMIN] (neg)** — Given the removal modal is open, When I select `Routed to inbound request`, Then an `Inbound No.` text input appears; When I type `2026080` and attempt to confirm, Then the confirm button stays disabled and the inline message `Inbound No. must be 12 digits (YYYYMMDDNNNN)` is shown `[E-35]`; When I correct it to `202608030001`, Then the confirm button becomes enabled `[PD-64 · OWNER-PENDING]`.

**QA-XDEL-06 [ADMIN]** — Given the removal modal with reason `Registered by mistake` selected, When I confirm, Then the row disappears with **no page reload** `[G-2]`, `[BR-34]`; And a green toast reads `✓ Removed from pool · {product}` with sub-line `Reason: Registered by mistake · Tracking {trk}`; And `[DC-14]` persists `status: OPEN → REMOVED` with actor, timestamp, reason, and the **full row snapshot** of all 12 column values `[G-8]`, `[PD-60 · CONFIRMED 2026-08-03]`; And a system comment `Removed from pool — Registered by mistake` is auto-posted on the pool item entity `[DC-29]` with **no** @mention and **no** Slack dispatch (§6.1).

**QA-XDEL-07 [ADMIN]** — Given a removal confirmed with reason `Routed to inbound request` and Inbound No. `202608030001`, Then `[DC-14]` carries `inbound_no: "202608030001"` And `[DC-15]` writes a reciprocal linkback on inbound request `202608030001` carrying `pool_item_id`, product, qty, and tracking no., with `resolves: true` `[PD-64 · OWNER-PENDING]`.

**QA-XDEL-08 [ADMIN]** — Given the removal modal with reason `No action needed` and a memo `duplicate parcel, discarded`, When I confirm, Then `[DC-14]` carries `reason: no_action_needed` and the memo verbatim, And **no** `[DC-15]` is written (no Inbound No. was supplied).

**QA-XDEL-09 [ADMIN] (neg)** — Given a removal confirm is dispatched twice under the same idempotency key `pool_item_id + "remove"`, Then exactly one `REMOVED` state exists, exactly one toast cycle occurs, the counters decrement by exactly 1, And `[DC-16]` records the suppressed second attempt `[G-9]`, `[E-18]`.

**QA-XDEL-10 [ADMIN]** — Given a pool item that carries two comments, When it is removed, Then both comments remain queryable and remain visible in the Comments hub with entity label `Unrecognized pool` `[E-60]`, `[BR-27]`; And clicking one navigates to the matched order or a read-only historical view, never to a dead link `[PD-67 · OWNER-PENDING]`.

**QA-XDEL-11 [ADMIN]** — Given a removal with reason `Routed to inbound request` and a well-formed Inbound No. that does not exist, or that exists but covers a different product, Then the removal is **accepted and recorded**, And `[DC-15]` is written with `resolves: false` `[E-35]`, `[E-70]`, `[PD-64 · OWNER-PENDING]`.

**QA-XDEL-12 [ADMIN] (neg)** — Given `[L-M2]` is open on a pool row with a reason selected, an Inbound No. typed, and a memo typed, When I click `Cancel` (and, separately, when I press `Esc`), Then the modal closes, the row is still present, both counters are unchanged, no toast fires, And **no** event of any kind is persisted — not `[DC-14]`, not `[DC-16]`, and nothing for the typed field values `[E-36]`, `[N-6]`, `[N-10]`; And focus returns to the `✕` that opened it `[BR-40]`.

### 8.7 Block CMT — Comments hub (`[L-5]`, `[L-F3]`)

**QA-CMT-01 [WF]** — Given the baseline, Then the nav contains a button whose text starts with `💬 Comments` And it carries a `.badge-n` reading `3`.

**QA-CMT-02 [WF]** — Given the baseline, When I click the `💬 Comments` button, Then `#inbox1` gains class `open` And its tabs read `@ Mentions` (with an inline badge `3`) and `★ Saved`.

**QA-CMT-03 [WF]** — Given `#inbox1` is open on the Mentions tab, Then the pane header reads `Comments mentioning me · Click to open the order` with a right-aligned `Mark all read` And the pane contains exactly 4 `.it` items **addressed positionally** (§8.0 rule 4 — `.paneheader` is also a `<div>`), of which exactly 3 carry class `unread` — the badge counts unread mentions, not items (§3.6). *(Re-baselined 2026-08-03: `WF-NEW-E` fixed, the wireframe now ships the canonical string QA-CMT-15 asserts for the admin.)*

**QA-CMT-04 [WF]** — Given `#inbox1` is open on the Mentions tab, Then the second item's entity label is exactly `Unrecognized pool` (not an order number) And its body contains `Miranti: "@Yongwon Left a memo on the Snail essence (box label damaged). Please check whose order this is"` with time `10:12` `[L-5]`.

**QA-CMT-05 [WF]** — Given `#inbox1` is open, When I click the `★ Saved` tab, Then the mentions pane is hidden and the saved pane is shown, with header `Saved comments · Click to open the order` / `Unstar to remove from the list` And exactly 1 item, whose entity label is `Unrecognized pool`. *(Re-baselined 2026-08-03: `WF-NEW-E` fixed; both strings now match the canonical admin strings of QA-CMT-15.)*

**QA-CMT-06 [WF]** — Given `#inbox1` is open on the Mentions tab, When I click the `.star` button on the **first `.it` item in document order** (§8.0 rule 4), Then that button gains class `on`; When I click it again, Then it loses class `on`.

**QA-CMT-07 [ADMIN] (neg)** — Given the admin's Comments hub, Then a full-text search input is present, And searching `10323100841207` returns matching comments across **all** entity types, newest first `[G-7]`, And `[DC-23]` persists `{query, result_count, searched_at}`, And clicking a result whose entity is `Unrecognized pool` navigates per `[PD-67 · OWNER-PENDING]`. *(The `[WF]` counterpart QA-WFQ-05 asserts the input is currently absent — defect `WF-NEW-A`.)*

**QA-CMT-08 [ADMIN]** — Given the admin with 3 unread mentions, When I click `Mark all read`, Then the `.badge-n` disappears or reads `0`, And `[DC-22]` persists `comment.mark_all_read` with `{user_id, comment_ids[]}` covering exactly those 3 comments, And the state survives a reload.

**QA-CMT-09 [ADMIN]** — Given the admin, When I star a comment and reload the page, Then it is still starred and appears under `★ Saved`; And `[DC-21]` persists `comment.starred` with `{user_id, comment_id}`; When I unstar it, Then `[DC-21]` persists `comment.unstarred` and it leaves the Saved pane.

**QA-CMT-10 [ADMIN] (neg)** — Given any comment in the hub or on an entity, Then **no** edit control and **no** delete control is rendered, And a direct API mutation attempt on an existing comment is rejected — comments are append-only `[PD-3 · OWNER-PENDING]`, `[BR-27]`.

**QA-CMT-11 [WF] (neg)** — Given `#inbox1` is open, When I click on the page body outside the dropdown, Then `#inbox1` **still** has class `open`; When I press `Esc`, Then it **still** has class `open` — current wireframe behavior, §2.4.8 (the `[ADMIN]` counterpart requires the opposite).

**QA-CMT-12 [ADMIN]** — Given the admin's Comments hub is open, When I click outside it, Then it closes; When it is open and I press `Esc`, Then it closes; And neither dismissal persists any event `[N-3]`, `[BR-40]`, `[E-56]`.

**QA-CMT-13 [ADMIN]** — Given a user with 120 unread mentions, Then the `.badge-n` renders `99+` And the nav layout does not wrap or overflow, While `[DC-22]`'s underlying count remains exact `[E-55]`.

**QA-CMT-14 [ADMIN]** — Given the admin's Comments hub holds an entry whose entity label is exactly `Unrecognized pool`, When I click it **while that pool item is still `OPEN`**, Then this page opens scrolled to `#poolrow-{pool_item_id}` with that row focused; When the same entry is clicked **after** the item reached `MATCHED`, Then the **matched order** opens instead; When it is clicked after the item reached `REMOVED`, Then a read-only historical view of the removed item opens — in no case is a dead link or a 404 produced `[E-31]`, `[E-60]`, `[BR-29]`, `[PD-67 · OWNER-PENDING]`.

**QA-CMT-15 [ADMIN]** — Given the admin's Comments hub is open, Then the Mentions pane header reads exactly `Comments mentioning me · Click to open the order` And the Saved pane header reads exactly `Saved comments · Click to open the order` — the corpus-canonical strings, §3.6 — And the unstar hint reads `Unstar to remove from the list` And the read-all action reads `Mark all read`. *(Since the 2026-08-03 `WF-NEW-E` fix the `[WF]` counterparts QA-CMT-03 / QA-CMT-05 assert the same strings — the two tiers no longer diverge on this page.)*

### 8.8 Block FURN — furniture, toasts, and no-refresh (`[L-F1]`, `[L-F2]`, `[L-F3]`)

**QA-FURN-01 [WF]** — Given the baseline, Then the bottom line reads exactly `Unrecognized pool · 3 items` with the count inside `#poolCountBottom`.

**QA-FURN-02 [WF]** — Given a match has just been confirmed, Then `#matchToast` has computed `position: fixed`, `top: 18px`, `right: 18px`, and a `z-index` placing it above the table, And its bounding box does not intersect the `Action` cell of any remaining row `[E-23]`.

**QA-FURN-03 [WF] (neg)** — Given the baseline, When I perform a match and then a `✕` removal, Then no additional navigation entry was created and no `beforeunload` fired — no programmatic full-page refresh occurred at any point `[G-2]`, `[BR-34]`.

**QA-FURN-04 [WF]** — Given the baseline, Then the nav bar renders `SkinSeoul`, the four menu labels `Operation AI ▾`, `Catalog Management ▾`, `OMS Center ▾`, `Site Management ▾`, the user block `Yongwon Ryu` with avatar `Y`, and a `Logout` button `[L-F3]`.

**QA-FURN-05 [WF]** — Given the baseline (before any action), Then `#matchToast` has computed `display: none` `[L-F1]`.

**QA-FURN-06 [ADMIN]** — Given any rejection path (stale candidate, occupied line, duplicate tracking, item not open), Then the toast rendered carries class `err` with computed background `rgb(220, 53, 69)` (`#DC3545`) and states the reason `[G-2]`, `[L-F1]`.

**QA-FURN-07 [ADMIN]** — Given the admin page with 3 open items, When the operator presses browser Refresh, Then the page reloads, re-fetches, and both counters read `3` again — a user-initiated reload is permitted and is **not** a `[G-2]` violation `[BR-44]`, `[E-57]`.

**QA-FURN-08 [ADMIN]** — Given a server response containing 5 open items of which client rendering emits only 4 rows, Then `#poolCount` and `#poolCountBottom` read `4` (the rendered count), not `5` — counters are derived from rendered rows `[BR-41]`, `[E-72]`; And the discrepancy is detectable rather than hidden.

**QA-FURN-09 [ADMIN] (neg)** — Given a match is confirmed and a removal is confirmed **1 s apart** (both inside the 4000 ms toast window), Then both toast texts are readable: the first is **not** silently replaced mid-window, and each text is displayed for at least 2 s — satisfied by stacking (both visible simultaneously, neither overlapping the other's text) or by queueing (the second begins its full window when the first ends). Stack-vs-queue is a developer decision (§9.2 D-4); **either** implementation must pass this scenario, and an implementation where the second toast overwrites the first in place **fails** it `[E-22]`.

**QA-FURN-10 [ADMIN] (neg)** — Given a resolver matches a pool row, then navigates to the matched order, then presses browser **Back**, Then this page re-fetches from the server and the matched row does **not** reappear from the bfcache or the HTTP cache; And the pool fetch response carries `Cache-Control: no-store` (§9.2 D-13); And both counters read the post-match value `[E-58]`, `[BR-33]`.

### 8.9 Block NEG — idempotency and concurrency (all negative)

**QA-NEG-01 [WF] (neg)** — Given `#m-match` is open from `#poolrow1` and `#poolCount` reads `3`, When I dispatch two `click` events on the same `Match to this product` button within 200 ms, Then exactly one pool row is removed And `#poolCount` reads `2` (never `1`) And **exactly one `#matchToast` display cycle occurs**, measured as: `#matchToast` computed `display` is `flex` continuously from the first dispatch until it becomes `none`, and it does not return to `flex` again within 6 s of the first dispatch `[E-9]`, `[G-9]`. *(`finishMatch()` guards with `const row=document.getElementById('poolrow1'); if(row){…}`; since 2026-08-03 the removal confirm handler carries the mirrored guard — see QA-NEG-03 and QA-WFQ-07.)*

**QA-NEG-02 [ADMIN] (neg)** — Continuing QA-NEG-01 in the admin, Then the order has exactly **one** `Matched the unrecognized product` system comment `[DC-10]` And exactly **one** message reached `#fulfillment-admin-comments` (`C0BMGEWM5QA`) `[DC-11]` And `[DC-12]` records the suppressed second attempt under the shared idempotency key `pool_item_id + line_id` `[BR-23]`.

**QA-NEG-03 [ADMIN] (neg)** — Given the admin, When I dispatch two `click` events on the same `✕` within 200 ms and confirm the resulting `[L-M2]` once, Then exactly one row is removed And both counters decrement by exactly 1 And the counters still equal the rendered row count `[G-9]`, `[BR-33]`, `[BR-41]`. **Kept `[ADMIN]`** for the server-side idempotency-key half; since the 2026-08-03 `WF-NEW-D` fix the wireframe exhibits the same client behavior, asserted by QA-WFQ-07 (rewritten).

**QA-NEG-04 [ADMIN] (neg)** — Given two browser sessions both have `[L-M1]` open for the same pool item, When session A confirms and then session B confirms, Then B's confirm is rejected with a red toast naming "already matched", B's list refreshes, and no second line write, comment, or Slack message occurs `[E-7]`, `[PD-7 · OWNER-PENDING]`; And `[DC-13]` records `reason: item_not_open` with B's actor.

**QA-NEG-05 [ADMIN] (neg)** — Given session A has `[L-M1]` open and session B has `[L-M2]` open for the same item, When A confirms the match and B confirms the removal, Then exactly one terminal state exists on the item (`MATCHED` **or** `REMOVED`, never both), And the loser receives a non-green toast, And both sessions' counters converge to the same value `[E-8]`, `[E-18]`.

**QA-NEG-06 [ADMIN] (neg)** — Given a match request that times out with no response, Then the `Match to this product` button shows a pending state, the row is **not** removed, and a red toast appears on timeout; When the same request is retried with the same idempotency key, Then no duplicate line write, comment, or Slack message is produced `[E-25]`.

**QA-NEG-07 [ADMIN] (neg)** — Given the same tracking number **and** barcode is sent from View Orders twice, Then exactly one pool row exists, the second send returns "already in pool" feedback on View Orders, and `[DC-2]` persists the deduped attempt `[E-1]`.

**QA-NEG-08 [ADMIN] (neg)** — Given the same **barcode** sent twice with **different** tracking numbers, Then **two** pool rows exist (this is not a duplicate), each with its own candidate set `[E-32]`.

**QA-NEG-09 [ADMIN] (neg)** — Given two pool rows whose barcodes match the same single order line, When the first is matched to that line, Then a match attempt on the same line from the second row is blocked with `line_occupied` And `[DC-13]` is persisted `[E-41]`, `[E-10]`.

**QA-NEG-10 [ADMIN] (neg)** — Given `[L-M1]` is open and the chosen product line is deleted on Order Detail before confirm, When I confirm, Then the server rejects with `[DC-13]` `reason: line_not_found`, a red toast appears, the candidate list refreshes, and **no** writes occur `[E-49]`.

**QA-NEG-11 [ADMIN] (neg)** — Given `[L-M1]` is open and the candidate order is merged into another order before confirm, When I confirm, Then the server rejects with `[DC-13]` `reason: order_not_found`, and the refreshed candidate list offers the surviving order **without auto-retargeting** the confirm `[E-50]`.

**QA-NEG-12 [ADMIN] (neg)** — Given two distinct pool items are matched to the same `line_id` in sequence, Then their idempotency keys differ (each contains its own `pool_item_id`) and the second is rejected by `[E-10]`, **not** silently swallowed as a duplicate `[E-67]`, `[BR-23]`.

**QA-NEG-13 [ADMIN] (neg)** — Given a Slack dispatch that fails on every retry until the budget is exhausted, Then `[DC-28]` persists a terminal `notification.dead_lettered` record with `total_attempts` and `last_error`, And the match or removal it belonged to **still stands**, And no alert badge is introduced on this page `[E-61]`, `[BR-42]`, §6.1.

**QA-NEG-14 [ADMIN] (neg)** — Given a match whose steps 1–3 succeed (line write + pool closure committed) and whose **step 4 comment post or step 5 Slack dispatch then fails**, Then the match is **not** rolled back: the order line still carries the tracking number `[DC-9]`, the pool item is still `MATCHED` `[DC-8]`, the row is still removed from the pool, both counters still decremented, and the **green** success toast still fired — the operator is **never** shown a failed-match message `[E-26]`, `[BR-20]`, `[PD-4 · OWNER-PENDING]`; And the failure is persisted `[DC-11]` with `delivery: failed` and retried `[DC-24]`. *(This is the single most dangerous inversion on the page: an implementation that reports the match as failed, or that reverses step 2, fails this scenario.)*

**QA-NEG-15 [ADMIN] (neg)** — Given the same user has this page open in **two** tabs, both showing 3 rows, When a match is confirmed in tab A, Then tab B removes that row and both of its counters re-sync to `2` within the live-update transport's interval, with **no** full-page refresh in either tab `[E-59]`, `[E-21]`, `[G-2]`; And if tab B is stale and confirms the same item anyway, the server — not the newest tab — arbitrates: the confirm is rejected with `item_not_open` and `[DC-13]` is persisted `[E-43]`.

### 8.10 Block VAL — server validation

**QA-VAL-01 [ADMIN] (neg)** — Given a candidate order that left `Processing` after `[L-M1]` opened, When the match is confirmed, Then the server rejects it, a **red** toast appears, the candidate list refreshes in place, the modal stays open, and **no** partial writes exist (line tracking unchanged, pool item still `OPEN`, no comment, no Slack) `[E-6]`, `[PD-6 · OWNER-PENDING]`; And `[DC-13]` records `reason: stale_candidate` with the status snapshot.

**QA-VAL-02 [ADMIN] (neg)** — Given the target product line already carries a tracking number, When the match is confirmed, Then it is blocked with an error naming the existing number, with **no** overwrite `[E-10]`, `[BR-18]`; And `[DC-13]` records `reason: line_occupied`.

**QA-VAL-03 [ADMIN] (neg)** — Given the pool item's tracking number is already registered on a different order line in the same namespace, When the match is confirmed, Then it is blocked with an error naming the other order `[E-11]`, `[BR-19]`; And `[DC-13]` records `reason: tracking_in_use`.

**QA-VAL-04 [ADMIN]** — Given an **inbound** tracking number on an inbound request that happens to equal this **outbound** tracking number, When the match is confirmed, Then it is **allowed** — the namespaces are separate `[PD-8 · OWNER-PENDING]`, `[BR-19]`.

**QA-VAL-05 [ADMIN] (neg)** — Given a pool item that is already `REMOVED`, When a stale client confirms a match on it, Then the server rejects with `item_not_open`, the client reloads, and both counts re-sync `[E-43]`, `[BR-33]`; And `[DC-13]` persists with `reason: item_not_open` and the rejecting actor.

**QA-VAL-06 [ADMIN] (neg)** — Given `[L-M2]` is open with no reason selected, Then the `Remove from pool` button is disabled and no removal is possible; And with reason `Other` selected and an empty memo, it stays disabled until a memo is entered (owner enum "Other + memo", §3.8) `[PD-60 · CONFIRMED 2026-08-03]`, `[BR-9]`.

**QA-VAL-07 [ADMIN] (neg)** — Given a candidate order whose PIC is unassigned, Then the candidate still renders (with `–` in the PIC slot) and is **not** excluded from the set `[E-34]`, `[BR-3]`; And the registration Slack `[DC-4]` mentions only the PICs that exist.

**QA-VAL-08 [ADMIN] (neg)** — Given a Slack dispatch failure at registration, Then the pool row still exists and is still matchable `[E-39]`, `[PD-4 · OWNER-PENDING]`; And `[DC-4]` records `delivery: failed`; And `[DC-24]` records at least one retry attempt.

**QA-VAL-09 [ADMIN] (neg)** — Given a pool item that arrived carrying an order number `[E-2]`, and that order is `Processing` and contains the product, Then it appears in the candidate set through the **normal predicate only** — it is not pre-selected, not sorted first, and not marked; And a different Processing order containing the same product appears alongside it with equal standing `[E-68]`, `[BR-12]`, `[BR-3]`.

**QA-VAL-10 [ADMIN] BLOCKED** — Intake of an item with **no tracking number** `[E-3]`. `[PD-66 · OWNER-PENDING]` is NO-DEFAULT: no behavior is specified, so this path has **no acceptance criteria**. QA must report it as **BLOCKED** and must not infer a verdict from whichever behavior the build happens to exhibit (§9.1).

**QA-VAL-11 [ADMIN] (neg)** — Given `[L-M2]` is open with a reason selected and the session expires or the network drops before confirm, Then the confirm fails with a red toast, the row stays, and no partial write exists; And retrying with the same idempotency key after re-auth produces exactly one removal `[E-42]`, `[G-9]`.

**QA-VAL-12 [ADMIN] (neg)** — Given two different authenticated operators (neither of them the registrant, and neither holding any special role), When operator A confirms a match on one pool item and operator B confirms a removal on another, Then **both** succeed — **no** control on this page is role-gated in v1 and no permission error is returned `[E-29]`, `[BR-26]`, `[G-15]`, `[PD-1 · OWNER-PENDING]`; And `[DC-8]` and `[DC-14]` each record their own actor, so the two actions are attributable `[G-8]`.

### 8.11 Block EMPTY — empty and error states

**QA-EMPTY-01 [WF]** — Given all three rows have been removed via `✕` → `[L-M2]` confirm (reason `No action needed`, one confirm each), Then `#poolCount` and `#poolCountBottom` both read `0`, And `.poolhead` is still rendered with a bounding-box height > 0, And the layout has not collapsed, measured as: the inner `.mockwrap`'s bounding-box height is **> 300 px**, the pool table's `<thead>` is still rendered with its 12 `<th>`, and `#poolCountBottom`'s bounding box lies **below** the table's `<thead>` `[E-19]`.

**QA-EMPTY-02 [ADMIN]** — Given a pool with zero open items, Then the table renders the empty-state row `No unrecognized items. Products sent from View Orders after a barcode recognition failure appear here.` And `.poolhead` reads `⚠ Unrecognized product pool · 0 items` `[E-19]`, §3.2.4.

**QA-EMPTY-03 [ADMIN]** — Given a pool item with zero candidates, Then both the pool cell and `[L-M1]`'s candidate panel render exactly `No Processing order contains this product — check the order data upstream, or remove with a reason.` And no search input appears anywhere `[E-5]`, `[PD-62 · OWNER-PENDING]`, `[BR-24]`; And `Review & Match` is still enabled so the memo can be read.

**QA-EMPTY-04 [ADMIN] (neg)** — Given the pool fetch fails on page load, Then an error state with a retry affordance is shown — **not** a blank table and **not** `0 items` `[E-28]`; And `[DC-25]` is persisted.

**QA-EMPTY-05 [WF] (neg)** — Given `#m-match` is open, When I click `Cancel`, Then the modal closes, all three rows remain, and both counters still read `3`; Repeat for the header `✕` and for a click on the overlay backdrop — all three paths close with zero side effects `[E-24]`, `[N-7]`.

**QA-EMPTY-06 [ADMIN]** — Given a pool with zero open items showing the empty-state row, When a new item arrives upstream, Then the empty-state row is replaced by the real row, both counters read `1`, and no full-page refresh occurs `[E-19]`, `[E-21]`, `[G-2]`.

### 8.12 Block XPG — cross-page

**QA-XPG-01 [ADMIN]** — Given a pool item was matched to order `414230` line L, When the same barcode is scanned on View Orders, Then the scan resolves normally to that order line and **no** unrecognized popup appears `[BR-5]`, `[E-15]`; And `[DC-17]` links the scan to the resolution. *(Mandatory inclusion #6.)*

**QA-XPG-02 [ADMIN]** — Given a barcode scan fails on View Orders and no order number is entered, When the operator sends the item via M2b, Then a new pool row appears on this page **without a page refresh** if it is open `[E-21]`; And `[DC-1]` and `[DC-5]` are persisted; And a `#unrecognized-tracking` message is delivered carrying tracking no., product, qty, memo, registrant, and the suspected orders, @mentioning the suspected PICs `[DC-4]`.

**QA-XPG-03 [ADMIN]** — Given an unrequested inbound arrival was registered to the pool with memo `suspected inbound stock`, When the owner creates an inbound request, enters the invoice number, and removes the pool row with reason `Routed to inbound request` and that Inbound No., Then rescanning the invoice on View Orders enters **State 6** (internal inbound), not the customer-order view `[L-S1-Fb]`, `[E-17]`, `[G-10]`.

**QA-XPG-04 [ADMIN]** — Given a match is performed **on View Orders M2** (on-the-spot), Then the same auto-comment and `#fulfillment-admin-comments` route fire, with `source: view-orders-m2` on `[DC-8]` `[PD-16 · OWNER-PENDING]`; And when the resolver is the registrant, the Slack mention is suppressed and `[DC-27]` is persisted.

**QA-XPG-05 [ADMIN] (neg)** — Given a Closing scan that produces the unknown-order warning, Then the warning stays on the Closing page, no navigation to this page occurs, and **no** pool row and **no** `#unrecognized-tracking` message is produced `[BR-32]`. *(The two flows are disjoint — `_review.md` §1 adjudicated non-issue.)* **`[ADMIN]`, not `[WF]`:** three of its four clauses are server and Slack state, which §8.0 defines as `[ADMIN]`, and the trigger lives on another page's wireframe, which no `[WF]` scenario in this document may target. The Closing-side half (the warning stays put, no navigation) is asserted in the **closing** spec against the closing wireframe; this row asserts only that nothing lands **here**.

**QA-XPG-06 [ADMIN]** — Given the field written by `[DC-9]`, Then it is byte-identically the field the View Orders scan resolution path reads — a contract test that must fail loudly if either spec changes the field `[BR-5]`, §6.3.

**QA-XPG-07 [ADMIN] (neg)** — Given an order in `Processing`, When a pool item is matched to one of its lines, Then the order's status is still `Processing` afterwards And **no** `order.status_changed` event is emitted §5.3.

**QA-XPG-08 [ADMIN] (neg)** — Given any action performed on this page (match, removal, comment, star, mark-all-read, search), Then **no** `print.job_result`, **no** `product.barcode_registered`, and **no** `order.outbounded` event is ever emitted §5.3, `[BR-31]`.

**QA-XPG-09 [ADMIN] (neg)** — Given a pool item matched to order `414230` line L, When that order is later **cancelled** on Order Detail, Then the tracking number written by `[DC-9]` **stays** on the line — it is not cleared, not nulled, and not reverted — And the pool item stays `MATCHED`; And this page offers **no** re-open, un-match, or restore control for it: the reversal path is Order Detail's / View Orders' cancel flow `[E-14]`, `[PD-22 · OWNER-PENDING]`, §6.3.

### 8.13 Block DATA — persistence and derivability

**QA-DATA-01 [ADMIN]** — Given a match confirm, Then the persisted event set for that action is exactly `[DC-8]`, `[DC-9]`, `[DC-10]`, `[DC-11]` (plus `[DC-27]` when the self-mention is suppressed), with `[DC-7]` already recorded at modal open, plus `[DC-6]` for the sibling recompute `[BR-38]`. No other event is written.

**QA-DATA-02 [ADMIN]** — Given every event listed in §5.1, Then each carries `actor` (or `system`), `occurred_at`, `source_screen`, `pool_item_id`, and — where a value changed — both the old and the new value `[G-8]`.

**QA-DATA-03 [ADMIN]** — Given a pool item created at T0 and matched at T1, Then `T1 − T0` is computable from `[DC-1]` and `[DC-8]` alone, with no additional instrumentation `[BR-35]`.

**QA-DATA-04 [ADMIN]** — Given 100 View Orders lookups of which 12 ended in `sent_to_pool`, Then the lookup-failure rate is computable from `[DC-3]` alone `[BR-35]`.

**QA-DATA-05 [ADMIN] (neg)** — Given a resolver opens and closes the Comments hub, switches tabs, opens and cancels `[L-M2]`, closes `[L-M1]` via the backdrop and via `Esc`, scrolls the table, types a comment draft without posting, and clicks a candidate order link, Then **no** event is persisted for any of those actions — they are declared non-events `[N-3]`, `[N-6]`, `[N-7]`, `[N-8]`, `[N-9]`, `[N-12]` `[G-8]`.

**QA-DATA-06 [ADMIN]** — Given the aging job runs against a pool holding 2 items older than 24 h, Then `[DC-18]` records both with `age_hours` And `[DC-19]` records one delivery to `#unrecognized-tracking` `[PD-61 · OWNER-PENDING]`; Given the pool is empty, Then `[DC-18]` is recorded with `items: []` and `[DC-19]` is **not** emitted `[E-37]`.

**QA-DATA-07 [ADMIN]** — Given a comment posted on a pool item with an @mention, Then `[DC-20]` persists with `entity_type: unrecognized_item` And `[DC-11]` persists the `#fulfillment-admin-comments` (`C0BMGEWM5QA`) dispatch with the deep link `[G-7]`.

**QA-DATA-08 [ADMIN] (neg)** — Given a registrant with no Slack mapping, When a match auto-comment is posted, Then the comment posts with a plain-text name, the flow does not fail, and `[DC-26]` is persisted `[E-27]`, `[E-71]`.

**QA-DATA-09 [ADMIN]** — Given 20 removals across the four reasons, Then the removal-reason distribution is computable from `[DC-14]` alone `[BR-35]`.

**QA-DATA-10 [ADMIN]** — Given 5 removals with reason `Routed to inbound request`, Then unrequested-inbound volume is computable from `[DC-15]` alone `[BR-35]`.

**QA-DATA-11 [ADMIN]** — Given a pool item in a terminal state (`MATCHED` or `REMOVED`) for 90 days, Then its full event chain (`[DC-1]` → terminal) is still queryable, and its comments are still readable — retention is indefinite `[BR-35]`, §5.4.

**QA-DATA-12 [ADMIN]** — Given a match resolved on this page and another resolved on View Orders M2, Then their `[DC-8]` events carry `source: tracking-missing` and `source: view-orders-m2` respectively, and both carry `source_screen` on the baseline envelope `[PD-16 · OWNER-PENDING]`, §5.1.

**QA-DATA-13 [ADMIN] (neg)** — Given a pool item created on 2026-12-31 and still `OPEN` on 2027-01-02, Then the `Registered At` cell still renders `12-31 23:40` with **no** year and this is **not** an error `[E-65]`; And the aging digest reports its age as **> 24 h** computed from `[DC-1]`'s full timestamp, never from the displayed `MM-DD HH:mm` string — an age computed from the display string would read as negative or as ~2 days-minus-a-year and must not be produced `[DC-18]`, `[PD-61 · OWNER-PENDING]`; And every persisted event for the item carries a full timestamp `[E-46]`.

### 8.14 Block A11Y — keyboard and announcement (`[E-62]`, `[BR-40]`, §3.14)

**QA-A11Y-01 [WF]** — Given the baseline, When I Tab through `#poolrow1`, Then focus reaches the `Review & Match` button and then the `.xdel` button, in that order.

**QA-A11Y-02 [ADMIN]** — Given the admin, When `[L-M1]` opens, Then focus moves inside the modal and Tab cycles only within it; When it closes by any path, Then focus returns to the `Review & Match` button that opened it. The same holds for `[L-M2]` and its `✕` trigger `[BR-40]`.

**QA-A11Y-03 [ADMIN]** — Given the admin, Then the `✕` control exposes an accessible name equivalent to `Remove from list`, And the Comments button exposes its unread count as text rather than by colour alone.

**QA-A11Y-04 [ADMIN]** — Given the admin, When any toast fires, Then its text is announced through an ARIA live region without moving focus `[L-F1]`, §3.14.

**QA-A11Y-05 [WF]** — Given the browser viewport is narrowed to 900 px, Then **both** nested `.mockwrap` elements report `scrollWidth > clientWidth` (outer 1280 → 900, inner 1457 → 1248), the 12 `<th>` are all still rendered in their original order with none hidden, and — after scrolling **both** `.mockwrap` elements to their maximum `scrollLeft` (§8.0 rule 3) — the `.xdel` button of `#poolrow1` has a bounding box fully inside the 900 px viewport `[E-63]`. *(Scrolling only the outer element leaves `.xdel` at roughly `left: 1045 px` and the scenario would FAIL for the wrong reason.)*

### 8.15 Block WFQ — current wireframe quirks (all [WF]; assert, do not file as bugs)

These record the live wireframe's behavior so an automated agent produces a stable PASS instead of a false failure. Each names the `[ADMIN]` scenario that asserts the correct behavior.

**QA-WFQ-01 [WF]** — Given the baseline, When I click `Review & Match` on the **second** row, Then `#m-match` opens showing **row 1's** COSRX item (`Tracking 10323100841207`). *(§2.4.1 — correct behavior asserted by QA-M1-08.)*

**QA-WFQ-02 [WF]** — Given the baseline, When I remove `#poolrow1` via `✕` → `[L-M2]` confirm (reason `Registered by mistake`) and then open `#m-match` from the wf-bar demo button and click `Match to this product`, Then `#matchToast` appears (showing the match text) but `#poolCount` stays at `2` (no further decrement — `finishMatch()` is hard-wired to the already-removed `#poolrow1`). *(§2.4.7 — correct behavior asserted by QA-MATCH-03 and QA-XDEL-06.)*

**QA-WFQ-03 [WF] (neg)** — Given the baseline, When I click any `.xdel`, Then `#m-remove` opens, **no row is removed**, both counters still read `3`, and no toast appears until `Remove from pool` is confirmed. *(Rewritten 2026-08-03 — the pre-fix body asserted the `WF-6` quirk "no dialog, no reason, no toast", which the wireframe pass resolved; the admin contract remains QA-XDEL-04 / QA-XDEL-06.)*

**QA-WFQ-04 [WF] (neg)** — Given the baseline, Then the document contains **zero** `<a>` elements; every candidate order number is a `<span>`. *(`WF-NEW-B` — correct behavior asserted by `[BR-37]` and §6.2.)*

**QA-WFQ-05 [WF] (neg)** — Given `#inbox1` is open, Then it contains no search input and no element with placeholder text. *(`WF-NEW-A` — correct behavior asserted by QA-CMT-07.)*

**QA-WFQ-06 [WF]** — Given the baseline, When I click `#annoToggle`, Then `body` gains class `no-anno`, every `.dot` and `.legend` is hidden, and the button text becomes `Show annotations`; clicking again restores both. *(Demo chrome, §2.3; must not exist in the admin — QA-LOAD-12.)*

**QA-WFQ-07 [WF]** — Given the baseline (`#poolCount` reads `3`), When I dispatch two `click` events on the **same** `.xdel` within 200 ms, Then exactly **one** `#m-remove` overlay is open and **no** row has been removed; When I then select a reason and dispatch two `click` events on `Remove from pool`, Then exactly **one** row is removed, exactly one toast cycle occurs, And `#poolCount` and `#poolCountBottom` both read **`2`**, equal to the rendered row count. *(Rewritten 2026-08-03 — the pre-fix body asserted defect `WF-NEW-D`'s double-decrement, resolved by the guarded confirm handler (§2.4.10). The server-side half remains QA-NEG-03 `[ADMIN]`.)*

### 8.16 DC → QA coverage map

Every persisted event has at least one **[ADMIN]** Then-clause asserting the persisted event `[G-8]`.

| Event | Asserted by | Event | Asserted by |
|---|---|---|---|
Each cell was re-derived from the scenario bodies: a scenario is credited **only** where it names the `[DC-n]` ID in its own text.

| Event | Asserted by | Event | Asserted by |
|---|---|---|---|
| DC-1 | QA-XPG-02, QA-DATA-03, QA-DATA-13 | DC-15 | QA-XDEL-07, QA-XDEL-11, QA-DATA-10 |
| DC-2 | QA-NEG-07 | DC-16 | QA-XDEL-09, QA-XDEL-12 |
| DC-3 | QA-DATA-04 | DC-17 | QA-XPG-01 |
| DC-4 | QA-XPG-02, QA-VAL-08, QA-SUS-09, QA-SUS-10 | DC-18 | QA-DATA-06, QA-DATA-13 |
| DC-5 | QA-SUS-06, QA-SUS-13, QA-XPG-02 | DC-19 | QA-DATA-06 |
| DC-6 | QA-SUS-07, QA-SUS-08, QA-SUS-13, QA-MATCH-09 | DC-20 | QA-DATA-07 |
| DC-7 | QA-M1-08, QA-M1-12, QA-DATA-01 | DC-21 | QA-CMT-09 |
| DC-8 | QA-MATCH-06, QA-MATCH-07, QA-MATCH-08, QA-DATA-12, QA-NEG-14, QA-VAL-12 | DC-22 | QA-CMT-08, QA-CMT-13 |
| DC-9 | QA-MATCH-06, QA-XPG-06, QA-XPG-09, QA-NEG-14 | DC-23 | QA-CMT-07 |
| DC-10 | QA-MATCH-06, QA-MATCH-10, QA-NEG-02 | DC-24 | QA-VAL-08, QA-NEG-14 |
| DC-11 | QA-MATCH-06, QA-DATA-07, QA-NEG-02, QA-NEG-14 | DC-25 | QA-EMPTY-04 |
| DC-12 | QA-NEG-02 | DC-26 | QA-DATA-08 |
| DC-13 | QA-VAL-01, QA-VAL-02, QA-VAL-03, QA-VAL-05, QA-NEG-04, QA-NEG-09, QA-NEG-10, QA-NEG-11, QA-NEG-15 | DC-27 | QA-MATCH-10, QA-XPG-04, QA-DATA-01 |
| DC-14 | QA-XDEL-06, QA-XDEL-07, QA-XDEL-08, QA-DATA-09, QA-XDEL-12, QA-VAL-12 | DC-28 | QA-NEG-13 |
| DC-29 | QA-XDEL-06 | | |

Non-events `[N-1]`…`[N-12]` are asserted collectively by **QA-DATA-05**, with `[N-4]` additionally by QA-M1-02 / QA-LOAD-12, `[N-3]` by QA-CMT-12, and `[N-6]`/`[N-10]` by QA-XDEL-12.

### 8.17 Legend-unit → QA coverage map

| Unit | Asserted by |
|---|---|
| `[L-0]` | QA-LOAD-01, QA-LOAD-02 |
| `[L-1]` | QA-LOAD-03…05, QA-ROW-01…16, QA-EMPTY-01, QA-EMPTY-02, QA-EMPTY-06, QA-FURN-08 |
| `[L-2]` | QA-SUS-01…13, QA-EMPTY-03 |
| `[L-3]` | QA-M1-01, QA-MATCH-01…10, QA-XDEL-01…12, QA-NEG-03, QA-WFQ-07 |
| `[L-4]` | QA-ROW-02, QA-ROW-03, QA-ROW-04, QA-ROW-14, QA-ROW-16, QA-M1-03, QA-M1-06 |
| `[L-5]` | QA-CMT-01…15 |
| `[L-M1]` | QA-M1-01…13, QA-EMPTY-05 |
| `[L-M2]` | QA-XDEL-01…12, QA-WFQ-03, QA-WFQ-07, QA-VAL-06, QA-VAL-11 |
| `[L-F1]` | QA-MATCH-04, QA-MATCH-05, QA-FURN-02, QA-FURN-05, QA-FURN-06, QA-FURN-09, QA-A11Y-04 |
| `[L-F2]` | QA-FURN-01, QA-LOAD-05, QA-MATCH-03 |
| `[L-F3]` | QA-FURN-04, QA-CMT-01, QA-CMT-13 |
| `[L-S1-Fa]` | QA-LOAD-06, QA-LOAD-08, QA-LOAD-09, QA-LOAD-10, QA-ROW-13 |
| `[L-S1-Fb]` | QA-LOAD-08, QA-XPG-01, QA-XPG-02, QA-XPG-03 |

### 8.18 Edge-case → QA coverage map

Every `[E-n]` in §7 has at least one Then-clause somewhere in §8, with exactly one declared exception. Rows were re-derived by searching §8 for each ID.

| Case | Asserted by | Case | Asserted by |
|---|---|---|---|
| E-1 | QA-NEG-07 | E-37 | QA-DATA-06 |
| E-2 | QA-VAL-09 | E-38 | QA-ROW-11, QA-ROW-12 |
| E-3 | QA-VAL-10 (**BLOCKED** — no criteria until `[PD-66]` lands, §9.1) | E-39 | QA-VAL-08 |
| **E-4** | **Deliberately none — cross-reference only.** The case cannot occur here (View Orders M2b forces an autocomplete pick); its negative test lives in the **view-orders** spec, §7.1 | E-40 | QA-SUS-07 |
| E-5 | QA-EMPTY-03, QA-ROW-12 | E-41 | QA-NEG-09 |
| E-6 | QA-VAL-01 | E-42 | QA-VAL-11 |
| E-7 | QA-NEG-04 | E-43 | QA-VAL-05, QA-NEG-15 |
| E-8 | QA-NEG-05 | E-44 | QA-ROW-14 |
| E-9 | QA-NEG-01 | E-45 | QA-ROW-15, QA-M1-13, QA-ROW-16 |
| E-10 | QA-VAL-02, QA-NEG-09 | E-46 | QA-ROW-07, QA-DATA-13 |
| E-11 | QA-VAL-03 | E-47 | QA-SUS-12 |
| E-12 | QA-MATCH-07 | E-48 | QA-SUS-08 |
| E-13 | QA-SUS-11 | E-49 | QA-NEG-10 |
| E-14 | QA-XPG-09 | E-50 | QA-NEG-11 |
| E-15 | QA-XPG-01 | E-51 | QA-MATCH-09 |
| E-16 | QA-XDEL-04, QA-WFQ-03 | E-52 | QA-SUS-09 |
| E-17 | QA-XPG-03 | E-53 | QA-SUS-10 |
| E-18 | QA-XDEL-09, QA-NEG-05 | E-54 | QA-MATCH-10 |
| E-19 | QA-EMPTY-01, QA-EMPTY-02, QA-EMPTY-06 | E-55 | QA-CMT-13 |
| E-20 | QA-XDEL-03 | E-56 | QA-CMT-12 |
| E-21 | QA-EMPTY-06, QA-XPG-02, QA-NEG-15 | E-57 | QA-FURN-07 |
| E-22 | QA-FURN-09 | E-58 | QA-FURN-10 |
| E-23 | QA-MATCH-05, QA-FURN-02 | E-59 | QA-NEG-15 |
| E-24 | QA-EMPTY-05, QA-M1-11 | E-60 | QA-XDEL-10, QA-CMT-14 |
| E-25 | QA-NEG-06 | E-61 | QA-NEG-13 |
| E-26 | QA-NEG-14 | E-62 | QA-A11Y-01…04, QA-M1-11 |
| E-27 | QA-DATA-08 | E-63 | QA-A11Y-05 |
| E-28 | QA-EMPTY-04 | E-64 | QA-ROW-16 |
| E-29 | QA-VAL-12 | E-65 | QA-DATA-13 |
| E-30 | QA-ROW-13 | E-66 | QA-MATCH-08 |
| E-31 | QA-CMT-14 | E-67 | QA-NEG-12 |
| E-32 | QA-NEG-08 | E-68 | QA-VAL-09 |
| E-33 | QA-M1-13, QA-ROW-15 | E-69 | QA-SUS-13 |
| E-34 | QA-VAL-07 | E-70 | QA-XDEL-11 |
| E-35 | QA-XDEL-05, QA-XDEL-11 | E-71 | QA-DATA-08 |
| E-36 | QA-XDEL-12 | E-72 | QA-FURN-08 |

**72 cases; 71 asserted; 1 declared exception (`[E-4]`).** `[E-3]` is asserted only as `BLOCKED` and carries no verdict by design — that is coverage of the *decision gap*, not of a behavior, and it must not be counted as a passing assertion.

---

## 9. Out of Scope & Open Questions

Per `_review.md` §3.8 this section carries **only** NO-DEFAULT owner questions, developer-time decisions, and out-of-scope pointers. Owner questions that already have a provisional default live in `_provisional-decisions.md` and are tagged inline above — they are not repeated here.

### 9.1 NO-DEFAULT open question (owner must decide; no behavior is specified)

**`[PD-66]` — Can an item enter the pool with NO tracking number (label destroyed, auto-collection failed)?**
- **Status:** not decided. **No default was adopted and no behavior is specified anywhere in this document.**
- **Why it is blocking:** if allowed, a "match" has nothing to write onto the product line, which breaks the `[DC-17]` rescan-resolves loop that the entire flow depends on `[BR-5]`. Deciding either way changes the registration contract on **View Orders M2b**, not just this page.
- **Affected units:** `[L-1]` column 1 (nullability), `[L-M1]` summary card (`Tracking {n}` fragment), `[E-3]`, §3.4.3 step 2.
- **QA consequence:** **QA-VAL-10** is reported as `BLOCKED`. An implementation must escalate rather than pick a behavior.
- **Owner:** SkinSeoul Director (Yongwon). **Blocks:** the View Orders M2b validation rule and this page's column-1 nullability.

**Provisional decisions carried by this page** (behavior IS specified; listed for the owner's review pass, not re-opened here): PD-1, PD-3, PD-4, PD-6, PD-7, PD-8, PD-16, PD-61, PD-62, PD-63, PD-64, PD-65, PD-67, PD-80 — **14 entries still OWNER-PENDING**. **Owner-CONFIRMED 2026-08-03: PD-5 and PD-60** (removal confirm + reason + toast; reflected in `[L-M2]`, `[BR-9]`, `[DC-14]`, `[DC-29]`, and the wireframe's M2 modal — no longer reversible-by-tag, so their inline tags read `· CONFIRMED 2026-08-03`). Cross-referenced only: PD-2 (cannot land — no outbound button), PD-22 (Order Detail), **PD-51 (Order Management — the sample-definition source; NO-DEFAULT, cited in §9.3)**, PD-68 (Closing), PD-85 (Inbound Request) — **5 entries**. Total distinct PDs cited by this document: **21 carried or cross-referenced** (14 pending + 2 confirmed + 5 cross-referenced), plus `[PD-66]` above, which is neither carried nor cross-referenced but **owned** by this page as its one NO-DEFAULT question — **22 in all**.

> **Note on `[PD-8]`.** It is listed as *carried* because this page adopts its namespace model. The order-line uniqueness rule in `[BR-19]` is a **page-level extension** of `[PD-8]`, not part of the register entry; it is flagged as such in `[BR-19]` and reverses independently.

### 9.2 Developer-time decisions (no owner input needed; a default is stated)

| # | Decision | Stated default |
|---|---|---|
| D-1 | Candidate recompute mechanism and cache policy | Server query on page load + `[L-M1]` open, plus event-driven recompute when an order enters/leaves `Processing` and after any sibling resolution `[DC-6]`, `[BR-38]` |
| D-2 | Pool live-update transport satisfying `[G-2]` | Poll or push, developer's choice; must update in place with no programmatic full-page refresh `[E-21]` |
| D-3 | Idempotency key format, TTL, and client debounce window `[G-9]` | Key **semantics** are fixed by this spec (`pool_item_id + line_id` for match, `pool_item_id + "remove"` for removal `[BR-23]`); format and TTL are dev's |
| D-4 | Toast stacking vs. queueing for rapid successive actions | Either, provided both texts remain readable `[E-22]` |
| D-5 | Slack and comment retry policy and budget | Non-blocking, persisted, retried `[PD-4 · OWNER-PENDING]`, `[DC-24]`; terminal failures dead-lettered `[DC-28]`, `[BR-42]`; backoff curve and budget are dev's |
| D-6 | Comment-search debounce and index scope; whether `[DC-23]` is indexed | Doctrine default is to persist the query event; indexing is dev's |
| D-7 | Rendering beyond the expected small pool | Plain scroll. **No pagination and no search may be added** — the 2026-07-23 decision stands `[BR-16]`, `[E-30]` |
| D-8 | Storage and export mechanics for pool-event history (CSV / BI) | Retained indefinitely `[BR-35]`; **no UI export exists and none is specified** |
| D-9 | Production route/URL for this page and the `#poolrow-{id}` / `#poolrem-{id}` anchor scheme | Anchor forms are spec-authored (§3.2.3, §6.2); final routing is dev's |
| D-10 | Cleanup of dead wireframe CSS/JS (`WF-10`, `WF-NEW-C`) | Delete per the §2.5 list; **do not implement** any of it. `.toast.err` is **not** dead — it is the specified failure variant `[L-F1]` |
| D-11 | `#unrecognized-tracking` channel ID | Not published in the routing table; resolve at wiring time. `#fulfillment-admin-comments` is `C0BMGEWM5QA` |
| D-12 | Slack candidate-list cap and the `+N more` threshold for `[DC-4]` | A cap is permitted so the message stays deliverable; the value is dev's, and `truncated_candidate_count` must be persisted `[E-53]` |
| D-13 | Cache headers on the pool fetch | `no-store`, so browser Back cannot resurrect a resolved row `[E-58]` |

### 9.3 Out of scope — owned by another spec

| Concern | Owner spec |
|---|---|
| The barcode scan surface, the M2 order-number lookup popup, and the M2b send-to-unrecognized modal (autocomplete, qty, memo, the send toast) | **view-orders** |
| Scanner protocol `[G-1]` behavior and the rescan that closes the loop | **view-orders** |
| The internal-inbound screen (State 6 / 6b), expected-qty edits (M6) and their reason enum `[G-11]`, partial arrivals | **view-orders**, **inbound-request** |
| Multiple tracking numbers per inbound request `[G-10]`, inbound-request creation, invoice entry, Received Date, and the block on adding numbers to an INBOUNDED request `[PD-85 · OWNER-PENDING]` | **inbound-request** |
| Procurement Hub sheet pull (excluded from this page 2026-08-02) | **inbound-request** |
| Display of the written tracking number; cancel / refund / clone / reset flows on the matched order | **order-detail** |
| Closing's "unknown order" warning and its resolution path (disjoint from this pool `[BR-32]`) | **closing** |
| Sample assignment `[G-13]` and the sample-definition source `[PD-51 · OWNER-PENDING]` (mandatory item 5 — no sample surface here; PD-51 is NO-DEFAULT and owned by order-management / RTO / order-detail, cross-referenced from here only) | **order-management** |
| Sourcing-route origin and the `OTHER` free-text channel `[G-5]` (this page only renders what it is given `[BR-15]`) | **inbound-request** |
| Location scheme, line-based location filter, audit-mode-only visibility `[G-14]`, and JIT residual stock (mandatory items 9, 10, 11 — none exist here) | **stock-status** |
| Label and invoice layout content (deferred to Phase 3-1 with the owner) | none — post-Phase-3 |

### 9.4 Explicitly removed — must NOT exist

Restated from `[L-S1-Fa]` for implementers reading only §9. Each has a Decision Log row in §10 and a negative QA assertion in §8.

Per-PIC group tables · bulk-action bar and multi-select · "Slack notified" column and pill · resolved-completion log section · unified search bar · in-page register button and modal · a second page state · wait-time chips · manual PIC-search fallback · photo capture, photo column, and thumbnails · pagination · column sorting · a scan input · a Print button · any outbound-class button (and therefore any audio) · a Slack route for removals · a per-page alert badge for dead-lettered notifications.

---

## 10. Decision Log

Every decision that shaped this screen, 2026-07-09 → 2026-08-03, including reversals and removals. Commit hashes are from `yongwon-pixel/skinseoul-wireframes`.

> **Notation.** Rows below cite a PD as a **record of a dated adoption** (`[PD-64]`), not as a behavior statement. The `[PD-n · OWNER-PENDING]` tag that marks reversible behavior lives on the behavior sentences in §1–§8 and in §9.1's carried-PD list — those are the only places to edit if the owner reverses a decision.

| Date | Decision | Source / commit | Effect on this spec |
|---|---|---|---|
| 2026-07-09 | Page conceived as "트래킹넘버 미입력 리스트" under section **F (Tracking Automation)** of the WMS 2.0 plan — replaces the manual set-aside of orders without a tracking number | `AI/Plans/2026-07-09-wms2-wireframes.md`, screen 6 | `[L-0]`, §1.2 |
| 2026-07-13 | v1 built in the 9-screen batch: per-PIC group tables, bulk-action bar, Slack-notified column, resolved log, in-page register button/modal, a second state, unified search bar, wait-time chips, photo column | `1bbba3a` | All of these are now **removed** — see the 2026-07-23 rows and `[L-S1-Fa]` |
| 2026-07-13 | Sourcing-route badges adopted as **colorless black bold text**, matched from the Inbound Request via invoice number | View Orders v20 convention | `[BR-15]`, `[G-5]` |
| 2026-07-21 | **Photo registration put on hold.** The View Orders unrecognized modal swapped photo capture → qty + memo. This page's photo column left pending cleanup | `adb429f`; handoff note F | Reversal chain starts — see 2026-08-03 |
| 2026-07-21 | Double-click double-processing logged as handoff note A: fix with debounce + idempotency key, do not reproduce | handoff note A | `[BR-23]`, `[G-9]` |
| 2026-07-23 | Order No column added to the pool table | `4eeebc7` | `[L-1]` column 2 |
| 2026-07-23 | Order-number field added to the View Orders unrecognized modal (optional at this point) and included in the Slack payload | `4cdd21d` | Superseded same day |
| 2026-07-23 | **Order number made mandatory** in the View Orders unrecognized modal (send gating) | `33a0eaf` | Superseded same day by the two-step flow |
| 2026-07-23 | **Two-step flow adopted:** order-number lookup → on-the-spot tracking match; not-found/failed → send to the pool (M2b). This is why the pool's Order No is normally `–` | `817749e` | `[BR-12]`, `[L-S1-Fb]`, §1.2 |
| 2026-07-23 | **Major simplification.** Removed: per-PIC group tables, bulk-action bar, Slack-notified column, resolved log, in-page register button/modal, State 2. Order-number format fixed as the Coupang purchase order number (`12101316464794`). Match modal added | `5796cb4` | `[L-S1-Fa]`, `[BR-1]`, `[BR-12]`, §9.4 |
| 2026-07-23 | **Unified search bar removed** — the pool holds only a few items | `3cf7ff8` | `[BR-16]`, `[E-30]` |
| 2026-07-23 | **Matching UX inversion.** The system pre-proposes suspected orders and handlers; the handler only confirms via "Review & Match" | `3cf7ff8` | `[BR-2]`, `[L-2]`, `[L-M1]` |
| 2026-07-23 | Tracking No column added; order number left blank; suspected-orders condition fixed to **Processing + contains the product, multiple possible**; matching redefined to the **product line** | `152e714` | `[BR-3]`, `[BR-5]`, `[L-2]` |
| 2026-07-23 | **Manual "find directly" (PIC search) fallback removed** — "if it is not here, the data is wrong". Row **✕** removal added | `e43ce68` | `[BR-4]`, `[L-3]`, `[E-5]` |
| 2026-07-23 | Wait-time chips removed along with the group tables — `Registered At` becomes the only age signal | `5796cb4` / `3cf7ff8` | `[PD-61 · OWNER-PENDING]` exists because of this |
| 2026-07-29 | Comments hub gained **full-text search across all comments** (all pages, newest first, click opens the entity) | `8e5abeb` | **This page's markup never received it** → defect `WF-NEW-A`; the spec still requires it `[L-5]` |
| 2026-08-02 | **Unrequested inbound arrivals reuse this pool.** A separate temporary registration path was explicitly rejected by the owner. Flow: register with a memo → create inbound request + enter invoice no. → ✕ remove → rescan enters View Orders State 6 | `960f5cf`; ledger 2026-08-02 | `[BR-11]`, `[L-S1-Fb]`, `[E-17]`, `[DC-15]` |
| 2026-08-02 | Procurement Hub sheet handoff scoped to the Inbound Request list — **excluded from this page** | ledger 2026-08-02 | §6.4 |
| 2026-08-02 | Phase-1 consistency sweep (51 mechanical fixes across wireframes) | `d88673c` | No behavioral change here |
| 2026-08-03 | **Photo column deleted** (review item 15). The 2026-07-21 hold is resolved as **permanent removal**, not deferral `[PD-63 · OWNER-PENDING]` | `f8c4bae`; review item 15 | **Reversal:** 2026-07-21 "hold, check later" → 2026-08-03 "permanently removed". `[BR-13]`, §9.4 |
| 2026-08-03 | **English conversion** of this page — 63 string replacements. Korean product names, carrier names, and company names stay Korean as **data** | `8beb374` | All quoted strings in §3 are post-conversion; `[G-6]` |
| 2026-08-03 | **Match footnote confirmed:** match confirm writes the tracking number **directly onto the order's product line**, so rescanning the same barcode resolves normally | `d09fe79` (View Orders side) | `[BR-5]`, `[DC-9]`, `[DC-17]`, mandatory inclusion #6 |
| 2026-08-03 | **Unrecognized-send confirmation toast** added on the View Orders side | `d09fe79` | Upstream; this page's `[L-F1]` is the match-side counterpart |
| 2026-08-03 | **`#fulfillment-admin-comments` (`C0BMGEWM5QA`) CONFIRMED** as the comment-@mention channel, superseding the "pending" wording in the earlier drafts | owner; routing table; `_review` C-2 / `[GD-1]` | §6.1 rows 2–3, `[L-5]` |
| 2026-08-03 | **`[G-2]` owner emphasis:** every confirming action toasts; no programmatic full-page refresh except the named RTO exception | owner | `[BR-34]`, `[L-F1]` |
| 2026-08-03 | **`[G-1]` scanner protocol** reaffirmed for every scan surface | owner | N/A here; stated as `[BR-30]` rather than omitted |
| 2026-08-03 | **`[G-4]` instant carrier-agnostic print** reaffirmed | owner | N/A here; stated as `[BR-31]`, §6.5 |
| 2026-08-03 | **Adjudication C-6:** `[G-2]` beats wireframe omissions. The ✕ removal gets a confirm dialog, a mandatory reason, and a toast → `[PD-60]` (provisional at the time; confirmed later the same day — see the v1.3 rows below), wireframe gap `WF-6` | `_review.md` §1 C-6; `[GD-5]` | **Reversal:** 2026-07-23 one-click removal → 2026-08-03 confirm + reason + toast. `[BR-9]`, `[L-M2]` |
| 2026-08-03 | `[PD-64]`: the removal reason "Routed to inbound request" captures a **structured Inbound No.**, with no hard guard blocking removal without it | PD register | `[BR-10]`, `[DC-14]`, `[DC-15]`, `[E-35]`, `[E-70]` |
| 2026-08-03 | `[PD-65]`: **qty mismatch at match time is allowed** and recorded, not blocked | PD register | `[BR-17]`, `[E-12]`, `[E-66]` |
| 2026-08-03 | `[PD-62]`: an empty candidate list renders explicit guidance; **no search affordance is re-introduced** | PD register | `[BR-24]`, `[E-5]` |
| 2026-08-03 | `[PD-61]`: a **once-daily aging digest** to `#unrecognized-tracking` for pool items open > 24 h restores the age signal lost on 2026-07-23 | PD register | `[BR-25]`, `[DC-18]`, `[DC-19]`, §6.1 row 4 |
| 2026-08-03 | `[PD-67]`: a Comments-hub entry whose entity is `Unrecognized pool` opens this page focused on that row; the matched order if the item is closed | PD register | `[BR-29]`, `[E-31]`, `[E-60]` |
| 2026-08-03 | `[PD-66]` left **NO-DEFAULT**: whether an item may enter the pool with no tracking number is undecided and blocks a View Orders validation rule | PD register | §9.1, `[E-3]`, QA-VAL-10 (BLOCKED) |
| 2026-08-03 | `[PD-16]`: an on-the-spot View Orders M2 match fires the **same** auto-comment and Slack route, with self-mention suppressed | PD register | `[BR-28]`, `[DC-27]`, QA-XPG-04 |
| 2026-08-03 | `[PD-8]`: system-wide tracking-number uniqueness within a namespace; inbound and outbound namespaces are separate and may coincide | PD register | `[BR-19]`, `[E-11]`, QA-VAL-04 |
| 2026-08-03 | `[PD-4]` / `[PD-6]` / `[PD-7]`: Slack failure never rolls back; the server revalidates at confirm; concurrency uses an optimistic version check | PD register | `[BR-20]`, `[BR-21]`, `[BR-22]` |
| 2026-08-03 | `[PD-3]`: comments are **append-only** everywhere, including on pool items | PD register | `[BR-27]` |
| 2026-08-03 | `[PD-5]`: every destructive action gets a confirm step, a reason where an enum exists, and a `[G-2]` toast | PD register | `[BR-9]`, `[L-M2]` |
| 2026-08-03 | **`[G-15]` created** — v1 ships a single admin role, no role gating on any screen `[PD-1]`. Closes the identical question raised independently by six pages, including this one | `_review` `[GD-8]` | `[BR-26]`, `[E-29]` |
| 2026-08-03 | **`[G-5]` amended (`GD-2`)**: the Inbound Request origin form offers SMART BUY / WHOLESALE / PARTNERSHIP / **OTHER (free-text channel)**; `OTHER` renders downstream as black bold `OTHER (channel)` `[PD-80]`. JIT is never a requestable inbound route | `_review` C-3 / `[GD-2]` | `[BR-15]`, `[L-2]` |
| 2026-08-03 | **`[G-7]` amended (`GD-1`)**: pool items are a **first-class commentable entity type**; system auto-comments use the same pipeline with `source=system` | `_review` `[GD-1]` | `[L-5]`, `[DC-10]`, `[DC-20]` |
| 2026-08-03 | **`[G-8]` amended (`GD-6`)**: specs may declare explicit NON-events; anything else operator-initiated must persist | `_review` `[GD-6]` | §5.2 |
| 2026-08-03 | Wireframe defects **`WF-6`** (✕ has no confirm/reason/toast) and **`WF-10`** (v1 CSS/JS leftovers) filed against this page; not applied during spec writing | `_wireframe-fixes.md` | §2.4, §2.5, D-10 |
| 2026-08-03 | New defects **`WF-NEW-A`** (Comments hub missing its search input), **`WF-NEW-B`** (candidate order numbers are not links — the file contains zero anchors, violating `[G-12]`), **`WF-NEW-C`** (additional dead CSS beyond `WF-10`, excluding `.toast.err`) found while writing this spec | this document §2.5 | `[L-5]`, `[BR-37]`, D-10 |
| 2026-08-03 | Adjudicated non-issue recorded: **Closing's "unknown order" ≠ this pool's "unrecognized product"** — the flows are disjoint and Closing does not route to `#unrecognized-tracking` | `_review` §1 | `[BR-32]`, QA-XPG-05 |
| 2026-08-03 | **No Slack route for removals.** Adding one would create an unowned alert stream; the record lives in the audit trail instead | this spec, §6.1 | `[DC-14]`, §9.4 |
| 2026-08-03 | **Audit pass (spec v1.1).** Added: sibling-recompute rule `[BR-38]`, mention dedupe `[BR-39]`, overlay/focus management `[BR-40]`, counters-from-DOM `[BR-41]`, notification dead-letter `[BR-42]` + `[DC-28]`, intake-snapshot rendering `[BR-43]`, user-reload allowance `[BR-44]`; edge cases `[E-47]`…`[E-72]`; §3.14 interaction baseline; §2.6 mandatory-inclusion map; §8 rewritten to 151 scenarios with a reset procedure and per-unit coverage maps | this document | §2.6, §3.14, §4, §5.1, §7, §8 — **the 151 figure is the v1.1 count; superseded by the v1.2 row below** |
| 2026-08-03 | **`[G-5]` page delta decided (spec v1.2).** The badge contract lands on `[L-M1]`'s `Channel` cell only; `[L-2]`'s pool cell renders the route as muted running text inside the status span. Resolves the v1.1 self-contradiction between §3.3's format line and its "Route label rendering" paragraph, which had encoded two mutually exclusive `[WF]` assertions (QA-SUS-02 vs QA-SUS-05) | verification m1 D-1 (BLOCKER) | §3.3 rendering table, `[BR-15]`, QA-SUS-02, QA-SUS-05 |
| 2026-08-03 | **`WF-NEW-D` filed and QA-NEG-03 re-tiered `[WF]` → `[ADMIN]`.** The wireframe's `.xdel` double-click removes one row but decrements both counters twice; the spec had asserted the correct behavior as `[WF]`, guaranteeing a false FAIL and hiding a real wireframe bug. Counterpart `[WF]` quirk QA-WFQ-07 added; §2.4 gained limitation 10; the defect was appended to `_wireframe-fixes.md` §B | verification m1 D-2, m2 F3 | §2.4.10, §2.5, QA-NEG-03, QA-WFQ-07, `_wireframe-fixes.md` |
| 2026-08-03 | **Edge-case coverage closed (spec v1.2).** 16 of 72 `[E-n]` had no acceptance criterion. 16 scenarios added (QA-ROW-13…16, QA-SUS-13, QA-M1-13, QA-XDEL-12, QA-CMT-14, QA-CMT-15, QA-FURN-09, QA-FURN-10, QA-NEG-14, QA-NEG-15, QA-VAL-12, QA-XPG-09, QA-DATA-13) and a new **§8.18 E→QA map** published. `[E-4]` remains the single declared exception (cross-reference to view-orders) | verification m1 D-3 | §8.18, §8.2, §8.3, §8.4, §8.6, §8.7, §8.8, §8.9, §8.10, §8.12, §8.13 |
| 2026-08-03 | **`[PD-8]` extension declared.** `[BR-19]`'s order-line uniqueness rule is a page-level extension, not register text; `[L-1]` column 1 now defines which namespace a pool item's tracking number belongs to and names the `[E-33]` interaction the guard cannot catch | verification m1 D-5 | `[BR-19]`, `[L-1]` col. 1, §9.1 |
| 2026-08-03 | **QA-XPG-05 re-tiered `[WF]` → `[ADMIN]`.** Three of its four clauses are server/Slack state and its trigger lives on the closing wireframe; `_review.md` §3.4 permits only `[WF]`/`[ADMIN]`, so no `[WF-XPG]` marker was invented. §8.0 now states that every `[WF]` scenario runs against this page's URL | verification m1 D-9, m2 F5 | §8.0, QA-XPG-05 |
| 2026-08-03 | **QA assertion-mechanics hardened.** §8.0 gained six binding rules (strip `.dot` before text comparison; `table.tbl` and `.mockwrap` each match two elements; `.it` is positional; "exactly" scoping; CDP needed for listener clauses). QA-LOAD-04, QA-LOAD-05, QA-M1-01, QA-ROW-08, QA-CMT-03, QA-CMT-05, QA-CMT-06, QA-EMPTY-01, QA-NEG-01, QA-A11Y-05 amended | verification m2 F1, F2, §5, §6 | §8.0 and the ten named scenarios |
| 2026-08-03 | **`WF-NEW-E` filed — Comments-hub pane headers diverge from the four-page-majority strings.** The admin adopts `Comments mentioning me · Click to open the order` / `Saved comments · Click to open the order`; the wireframe's shorter strings stay asserted under `[WF]`. Pending a `[G-7]` amendment that publishes the six hub strings as byte-exact contract | cross-page verification m3a D7 | §2.5, §3.6, QA-CMT-03, QA-CMT-05, QA-CMT-15 |
| 2026-08-03 | **Deep-link path form normalized to the directory form** `../{slug}/#{anchor}`, matching `[G-12]` and the live wireframe URLs. The `index.html` variant is retired from this spec | cross-page verification m3a D16 | §6.2 |
| 2026-08-03 | **Event-name scope note published** (§5.1): four shared concepts carry per-page names across the corpus with no canonical name yet; this page's names are declared page-scoped and superseded the day a canonical name lands in `_global-rules.md` | cross-page verification m3a D14 | §5.1 |
| 2026-08-03 | **`[GD-n]` resolution note added** (reading contract item 6): GD IDs resolve only in `_review.md` §4, all ten landed in `_global-rules.md` v1.0, and a GD citation is provenance, never a live rule | cross-page verification m3a D13 | Reading contract |
| 2026-08-03 | **`[BR-44]` reclassified as a candidate global amendment,** not a page behavior — the `[G-2]`-scope reading applies to all eight screens and must be promoted into `[G-2]`; stated locally only so QA-FURN-07 has a rule, and marked do-not-copy | verification m1 D-7 | Reading contract item 7, `[BR-44]` |
| 2026-08-03 | **`[BR-15]`, `[BR-23]`, `[BR-27]`, `[BR-34]` trimmed to their deltas** and the reading contract's rule-restatement clause reworded to match what the document actually does | verification m1 D-6 | Reading contract item 1, §4 |
| 2026-08-03 | **`[PD-51]` tagged `· OWNER-PENDING`** and added to §9.1's cross-referenced list; §8.16's `DC-10` / `DC-13` map rows reconciled by adding the missing citations to QA-NEG-02 and QA-VAL-05; §8.0's totals sentence reworded so QA-VAL-10 reads as inside the total, not additional | verification m1 D-4, D-8, D-10 | §8.0, §8.16, §9.1, §9.3 |
| 2026-08-03 | **Register-citation warning added** to §2.5: `_review.md` §2a mis-cites this page's dead-code cleanup as `WF-9`; the correct entry is `WF-10`, which is what every citation in this document uses | verification m3b finding 5.3 | §2.5 |
| 2026-08-03 | **Remediation pass (spec v1.2).** §8 recounted from the scenario bodies: **168 scenarios — 66 `[WF]`, 102 `[ADMIN]`; 61 negatives (36.3 %)**; per-block, per-tier and per-negative counts published in §8.0 and re-derivable from the blocks | this document | §8.0 and all of §8 |
| 2026-08-03 | **Owner confirmation of `[PD-5]` → `[PD-60]` CONFIRMED (spec v1.3).** Every removal/deletion gets a confirm dialog + toast; for this page's ✕ that is `[L-M2]` with header `Remove this item from the pool?`, toast lead `✓ Removed from pool`, and a removal auto-comment on the pool item entity (new event `[DC-29]`, mention-free — §6.1's no-Slack-route stands). Reason labels finalized as `Registered by mistake` / `Routed to inbound request` / `No action needed` / `Other` (+ mandatory memo for `Other`) — the owner-confirmed enum **plus** the `Routed to inbound request` option retained so `[PD-64 · OWNER-PENDING]` and the `[BR-11]` inbound handoff stay mountable. `[DC-14]`'s reason tokens updated to match | owner confirmation, 2026-08-03; PD register PD-5/PD-60 | `[L-M2]` §3.8, `[BR-9]`, `[DC-14]`, `[DC-29]`, §5.1 count 28→29, §8.16, §9.1 |
| 2026-08-03 | **Wireframe pass applied (local edit; `/wf-deploy` pending).** `WF-6` closed (M2 modal `#m-remove` + wf-bar demo button + legend/footer updates, dot count 7→8), `WF-NEW-D` fixed (removal confirm guarded by `rmRow.isConnected`), `WF-NEW-E` fixed on this page (canonical hub pane headers), `WF-10`+`WF-NEW-C` dead v1 CSS/JS deleted (`.toast.err` kept; `.mtextarea` kept — now used by M2's memo; `.tag-jit` kept for M1). Verified by an automated Playwright run: 58 assertions PASS, 0 pageerror, M1 regression suite green. QA re-baselined (QA-XDEL-01…03, QA-WFQ-02/03/07, QA-CMT-03/05, QA-LOAD-07/09/11/12, QA-EMPTY-01, QA-NEG-01/03 notes); **§8 totals unchanged** (168 / 66 `[WF]` / 102 `[ADMIN]` / 61 neg). `WF-NEW-A` and `WF-NEW-B` remain open | this document; `_wireframe-fixes.md` §B/§C | §2.1–§2.5, §3.6, §3.8, §8 |

### 10.1 Reversal chains (verbatim, so nobody re-implements a superseded state)

1. **Photo capture:** 2026-07-13 photo column shipped → 2026-07-21 **hold** (removed from the View Orders modal, column left pending) → 2026-08-03 **permanently deleted** `[PD-63 · OWNER-PENDING]`. Current truth: no photo anywhere on this page, not deferred.
2. **Manual PIC search:** 2026-07-13 primary interaction (handlers hunt their own name per product) → 2026-07-23 demoted to a **fallback** under the new pre-proposal UX → 2026-07-23 (same day, `e43ce68`) **removed entirely**. Current truth: no search of any kind on this page.
3. **Order number in the unrecognized modal:** 2026-07-23 added as **optional** (`4cdd21d`) → 2026-07-23 made **mandatory** with send gating (`33a0eaf`) → 2026-07-23 restructured into the **two-step lookup flow** (`817749e`). Current truth: the number is entered upstream and a successful lookup means the item never reaches this pool, which is why Order No is normally `–`.
4. **Row ✕ removal:** 2026-07-23 added as **one click, no confirm, no reason, no toast** → 2026-08-03 adjudication C-6 requires **confirm + mandatory reason + toast** (`[PD-60]`, provisional) → 2026-08-03 **owner CONFIRMED** (`[PD-5]`/`[PD-60]`) **and the wireframe implements it** — M2 (`#m-remove`) shipped, `WF-6` closed, plus a removal auto-comment `[DC-29]`. Current truth: `[L-M2]` as specced **and** as wired; the fixed chain is asserted by QA-XDEL-01…03 / QA-WFQ-03/07.
5. **Comments-hub search:** 2026-07-29 added globally (`8e5abeb`) → **never wired into this page's markup**. Current truth: required by `[G-7]` and legend 5, missing in the wireframe (`WF-NEW-A`), asserted absent by QA-WFQ-05 and required by QA-CMT-07.
6. **Unrequested inbound arrivals:** a separate temporary registration path was **proposed and rejected by the owner** on 2026-08-02 in favour of reusing this pool. Current truth: `[BR-11]`. Do not re-propose a separate path.
7. **"Slack notified" column:** 2026-07-13 shipped as a visible column with a status pill → 2026-07-23 **removed from the UI**, while the dispatch itself remains fully persisted `[DC-4]`. Current truth: the data survives, the column does not.
8. **Resolved-completion log:** 2026-07-13 shipped as an on-page section → 2026-07-23 **removed from the UI**, with the resolution data retained admin-side as a view over `[DC-8]` / `[DC-14]`. Current truth: no on-page log; the data is queryable and the section can be re-surfaced later without a schema change.
