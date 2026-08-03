# WMS 2.0 — Global Rules (`_global-rules`)

Version 1.2 · 2026-08-03 · Applies to all 8 screen specs. Screen specs cite these by ID (`[G-n]`) and describe **page deltas only** — they never restate a rule body.

Status legend: **CONFIRMED** = owner-decided, dated. **[PD-n · OWNER-PENDING]** = provisionally adopted on 2026-08-03 while the owner was unavailable; see `_plans/_provisional-decisions.md` for the question, the provisional answer, and the reversal impact. PD-1 through PD-8, 51, 55, 66, 71, 74, 79 were owner-decided on 2026-08-03 — their register entries carry the ruling. The owner decision round is fully closed; remaining `[PD-n]` tags are register-adopted provisional defaults.

---

## [G-1] Scanner protocol
A barcode scanner types the number and sends an automatic Enter. During continuous scanning:
1. The cursor must always be in the scan input — after every action, focus returns there with the previous value selected (so the next scan overwrites it).
2. The page must **never** refresh between scans.
3. No extra clicks are required between scans, ever.
Applies to every scan surface: View Orders (all states), Closing. **CONFIRMED 2026-08-03 (owner emphasis).**
Page deltas may add local behavior (e.g. Closing disables the input before the count is entered), never remove the three invariants above.

## [G-2] No refresh + confirmation toast
- No full-page refresh after any action. **Sole designed exception:** RTO Bulk Outbound refreshes after completion (2026-07-09 decision, deliberately kept).
- **Every confirming action** — register, confirm, cancel, send, save, remove/delete — shows a top-right toast stating what happened. Green for success, red for failure. Removal/deletion confirmations count as confirming actions [GD-5].
- **Every removal/deletion-class (destructive) action takes a confirm dialog, plus a reason where the flow already carries a reason field, plus the toast.** **CONFIRMED 2026-08-03 (owner, PD-5).**
**CONFIRMED 2026-08-03 (owner emphasis, applies across all 8 screens).**

## [G-3] Audio feedback
(a) **Send sound** — outbound-class buttons play a short synthesized rising sweep (Web Audio, no external files). Scope: every outbound-class button on every page — View Orders (Outbound, Inbound + Outbound, bulk), RTO (Bulk Outbound), Order Detail (Outbound), Inventory (− Record Outbound). **CONFIRMED 2026-08-03 (owner, PD-2).**
(b) **Voice alert** — Closing scan warnings speak "Please check this order" (`en-US` TTS) so staff hear problems without watching the screen. **CONFIRMED 2026-07-23.**
(c) View Orders State 6 wrong-product scan uses a **distinct warning tone**, not the send sound and not TTS (page delta).

## [G-4] Instant, carrier-agnostic printing
Any Print button outputs the correct carrier's label **immediately on click** — no new tab, no browser print dialog, no preview step — regardless of carrier (Deleo, YUN, or any carrier added later). This requires a local print agent (PrintNode-class) that pushes directly to the printer queue; browsers cannot do this alone (see handoff note 2).
Print surfaces: View Orders (order Print, single-item auto-print on scan, M4 return labels), RTO (row Print, Bulk Print Labels, M1 picking list), Order Detail (Print). Closing report is **CSV download only** — not a print surface `[PD-68 · OWNER-PENDING]`.
Infrastructure failures (agent offline, printer unreachable) surface as a red toast [G-2] and are persisted as `print.job_result` [G-8]. **CONFIRMED 2026-08-03 (owner: "print button alone must produce the label").**
Carrier labels themselves are always **each carrier's existing default output, printed verbatim** — no custom carrier-label layout exists or will be built, for YUN, DELEO, or any carrier added later (e.g. FedEx). Only the internal invoice ("PACKING") is ours to design — see `specs/shipping-label.md`. **CONFIRMED 2026-08-03 (owner).**

## [G-5] Sourcing routes
- **Order-facing badges (4):** SMART BUY · JIT (purchase channel in parentheses: Coupang / Naver / Other retail) · WHOLESALE · PARTNERSHIP.
- **Inbound-request origin form (4):** SMART BUY · WHOLESALE · PARTNERSHIP · **OTHER (free-text channel)**. JIT is never a requestable inbound route — it arises order-side.
- OTHER renders downstream as black bold `OTHER (channel)` `[PD-80 · OWNER-PENDING]`.
- All route labels render as **colorless black bold text**, never colored pills. Route origin = Inbound Request; consumers = View Orders badges, Inventory, Order Detail.

## [G-6] Product naming
- English product name is always prefixed with the **brand in bold**.
- Korean product names also carry the EN brand in bold (e.g. **Dr.Jart+** 포어레미디 리뉴잉 폼 클렌저).
- **RTO "Ready Item Details" and the picking list use Korean names** — pickers locate items faster in Korean (2026-08-03).
- Korean product names, Korean carrier names (CJ대한통운 등), Korean supplier/company names, and printed label content are **data**: they stay Korean inside an English UI and are never translated.

## [G-7] Comments system
- Per-entity comment history accumulates in admin — this is a deliberate AI-training and audit asset; comments are **append-only** (no edit/delete). **CONFIRMED 2026-08-03 (owner, PD-3).**
- `@mention` notifies the mentioned person through Slack: **#fulfillment-admin-comments** (`C0BMGEWM5QA`) — the message body @mentions the person, so Slack raises a personal notification while the channel doubles as a team-visible archive. Payload: entity no., comment text, time, author, mentioned user, deep link. **CONFIRMED by owner 2026-08-03.**
- System auto-comments (expected-qty edit, unrecognized match-confirm) use the same pipeline with `source=system`.
- Commentable entity types include orders **and** inbound requests **and** unrecognized-pool items.
- Every screen carries the top-right Comments hub: `[@ Mentions]` + `[★ Saved]` + full-text search across **all** comments (entity no. / author / text), newest first, click opens the entity. Badge = unread mention count.

### Canonical hub copy (byte-identical on every page)

The hub is **one control replicated on all eight screens**, so its copy is a byte-exact cross-page contract. Until 2026-08-03 no canonical existed, so each wireframe shipped its own wording and each spec asserted its own form byte-exactly — eight QA suites that no single implementation could satisfy. The strings below are published as contract to close that fork (cross-page defect **M3a D7**; register entries `[WF-VO-1]`, `[WF-15] closing`, `[WF-NEW-E]`, `[IR-WFX-1]`, and the §F / §H factual corrections in `_wireframe-fixes.md`). **CONFIRMED 2026-08-03 (owner-approved remediation batch).**

| # | Element | Canonical string | Corpus basis before canonicalization (8 pages) |
|---|---|---|---|
| **HUB-1** | `@ Mentions` pane header | `Comments mentioning me · Click to open the order` | **majority 5/8** (OD · RTO · INV · OM · TM) |
| **HUB-2** | `★ Saved` pane header | `Saved comments · Click to open the order` | **majority 5/8** (same five) |
| **HUB-3** | Saved-pane unstar hint | `Unstar to remove from the list` | **no majority** — `… from list` 3 (VO · OM · IR) / `… from the list` 2 (RTO · TM) / `… from this list` 2 (INV · CL) / `Unstar to remove` 1 (OD). Resolved to the standard English form, which three specs had already named as the intended canonical (`closing.md` §3.8, `tracking-missing.md` §3.6, `order-detail.md` §2.7) |
| **HUB-4** | Read-all action | `Mark all read` | **majority 6/8** (only VO · IR said `Mark all as read`) |
| **HUB-5** | Search results header | `{n} results · newest first · click to open the order` | **majority 4/5** (VO was the outlier; CL · TM · IR ship no search pane) |
| **HUB-6** | Empty search state | `No matching comments` | **majority 4/5** (VO shipped a capitalized `Comments`) |
| **HUB-7** | Search box placeholder | `🔍 Search all comments — order no. · author · text` | **majority 4/5** (VO was the outlier) |

Reading rules:
- `{n}` in HUB-5 is a count substituted at render time, never a literal — a zero-hit search still renders the header, followed by HUB-6 as a separate node.
- HUB-1 / HUB-2 say **order** even on screens whose hub entries are inbound requests or unrecognized-pool items (View Orders tab 6, Inbound Request, Tracking Missing). The hub is one component with one string; "click opens the entity" is the behavior, and the word `order` is not re-worded per entity type.
- A page may not introduce a local variant of any of the seven. Where a spec's `[WF]` tier previously asserted its own wireframe's divergent string, both the wireframe and the assertion were moved to the canonical value in the same commit (2026-08-03).

## [G-8] Data-capture doctrine
Every operator-initiated action persists: actor, timestamp, entity, old value → new value, quantity. This covers inbound/outbound/cancel, quantity edits, location changes, closing confirmations, audit adjustments, comment posts, imports, sample-assignment changes, print job results, and Slack dispatch results.
UI logs (actor log, scan feed, audit history) are **views over persisted events**, never the only copy. Retention and export requirements are stated per screen.
Specs may declare explicit **NON-events** — ephemeral client-local state such as checkbox toggles, filter clicks, tab switches, cancelled edits. Anything not declared a non-event and operator-initiated **must** persist.

## [G-9] Idempotency
Inbound / Outbound / and every confirming action must be double-click safe: client-side debounce **and** a server-side idempotency key. A known current-admin bug processes double clicks twice — this must be fixed, not reproduced. Key format and debounce window are developer decisions.
**Concurrent edits** by two operators resolve by optimistic version check → 409 → reload the row + non-green toast; counting flows (State 6 receive, closing scans) merge server-side instead. **CONFIRMED 2026-08-03 (owner, PD-7).**

## [G-10] Multiple tracking numbers per inbound request
One inbound request may register several tracking numbers (split shipments). **Every** registered number matches in View Orders and enters the internal-inbound screen (State 6); partial arrivals accumulate against the same request until fully received. **CONFIRMED 2026-08-03.**
An inbound tracking number is **unique system-wide** — registering one that already exists on another inbound request is blocked. Inbound (supplier→warehouse) and outbound (warehouse→customer) tracking numbers are separate namespaces and may coincide; View Orders resolution precedence puts inbound-request tracking first (State 6). **CONFIRMED 2026-08-03 (owner, PD-8).**

## [G-11] Inbound request lifecycle
`REQUESTED → PARTIAL (n/m remaining, amber) → INBOUNDED`.
Expected-quantity edits are allowed with a **mandatory reason** — exact enum: "Damaged/defective — cannot accept" / "Supplier qty change" / "Other (memo)". Editing recomputes remaining quantity and the full-confirm gate, auto-posts a comment on the request, and notifies the requester [G-7]. Expected-qty edits originate **only** in View Orders M6; the Inbound Request list displays the resulting history.
Arrivals with no matching request route to the shared unrecognized pool (Unrecognized Tracking), not to an ad-hoc registration path.

## [G-12] Deep links
Cross-page references are real links, not decoration — e.g. View Orders State 6 banner → `../inbound-request/#reqlist` opens the Request List tab. In the production admin these deep-link to the filtered entity (e.g. the specific Inbound No.).

## [G-13] Sample assignment (Order Management is the primary home)
- Simple **ON/OFF** with multiple, possibly overlapping assignment periods (2026-07-23 redesign; reconfirmed 2026-08-03). No sample-type selection.
- **Exactly one sample set per order**, even when periods overlap — no double assignment.
- **v1 makes no sample distinction** — internal invoices and picking labels also render **"sample set" only**: no sample type, no per-type quantity. Carrier-facing data appends only "(+ sample set)" to the last product name (tax handling), so in v1 the carrier-facing and internal renderings differ only in placement. Distinguishing WHICH sample and HOW MANY is follow-up work for the moment sample types are introduced. **CONFIRMED 2026-08-03 (owner, PD-51)** — this supersedes the earlier "which sample and how many" internal-artifact requirement; whether the picking list carries a sample-set line at all remains `[PD-36 · OWNER-PENDING]` (if it does, the line reads "sample set").

## [G-14] Location scheme
- One location per SKU. Whether two SKUs may share one location is `[PD-46 · OWNER-PENDING]` (provisional: 1:1, i.e. a location holds one SKU).
- Inventory's location filter groups by **line (A / B / C …)**; the line list is derived **dynamically from registered locations**, never hard-coded. **CONFIRMED 2026-08-03.**
- Audit-mode-only UI (counted qty, diff, loss columns, the loss summary, the unregistered-product row) stays hidden until Stock Audit is started. **CONFIRMED 2026-08-03.**

## [G-15] Permissions (v1)
v1 ships a **single admin role**: no role gating on any screen, every mutating action records the actor [G-8]. A role/permission model is a post-v1 owner decision. **CONFIRMED 2026-08-03 (owner, PD-1: everyone may perform every action; who-did-it logging is mandatory)** — this rule exists because six screens independently raised the same question.

---

## Cross-page event names (canonical — byte-identical wherever used)
`comment.posted` · `comment.mention_notified` · `comment.starred` / `comment.unstarred` · `comment.read` / `comment.mark_all_read` · `comment.auto_posted` (`source=system`) · `product.barcode_registered` · `order.status_changed` · `order.outbounded` · `print.job_result`.
Other events use lowercase `entity.action` semantic names. Literal API/endpoint naming is a developer decision.

## Slack routing (all confirmed 2026-08-03 unless noted)
| Trigger | Channel | Payload |
|---|---|---|
| Unrecognized barcode sent to the Missing Tracking List | `#unrecognized-tracking` | tracking no., product, qty, memo, registrant, suspected orders |
| Morning check — inbound request without tracking no. (WHOLESALE · SMART BUY) | `#wholesale-ops` | Inbound No., supplier, requested-by, age |
| Morning check — inbound request without tracking no. (PARTNERSHIP) | `#partnership-kr` | same |
| Comment @mention (any screen) | `#fulfillment-admin-comments` (`C0BMGEWM5QA`) | entity no., text, time, author, @mentioned user, deep link |
| Expected-qty edit (auto-comment) | `#fulfillment-admin-comments` + @requester | old→new qty, reason, editor |
| Unrecognized match confirmed (auto-comment) | `#fulfillment-admin-comments` + @registrant | tracking no., matched product line, resolver |

**Failed-dispatch retry queue** — a failed Slack dispatch never blocks or rolls back the primary action; the failure is queued in a background retry queue and re-sent automatically with exponential backoff. Every dispatch result is persisted [G-8]. An item still undelivered after N retries (N = developer decision) is flagged in the admin notification log. No dedicated queue screen in v1. **CONFIRMED 2026-08-03 (owner, PD-4).**

---

## Change history
| Version | Date | Changes |
|---|---|---|
| 1.2 | 2026-08-03 | **[G-7] publishes the seven canonical hub strings** (HUB-1…HUB-7) as byte-exact cross-page contract, closing cross-page defect M3a D7. All eight wireframes and all eight spec QA suites were moved to these values in the same commit. HUB-7 (search placeholder) is one beyond the six the register enumerated — same component, same defect class, unambiguous 4/5 majority. |
| 1.1 | 2026-08-03 | Owner decisions applied: PD-1→[G-15], PD-2→[G-3a], PD-3→[G-7], PD-5→[G-2], PD-7→[G-9], PD-8→[G-10] now **CONFIRMED**; tags removed. |
| 1.1 | 2026-08-03 | [G-13] amended per **PD-51**: v1 renders "sample set" only on internal invoices and picking labels — no sample type/quantity breakdown until sample types exist. |
| 1.1 | 2026-08-03 | Slack section: **Failed-dispatch retry queue** clause added per **PD-4** (exponential backoff, persisted results, admin-log flag after N retries, background-only in v1). |
