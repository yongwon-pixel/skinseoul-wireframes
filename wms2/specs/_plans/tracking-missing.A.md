# PLAN — tracking-missing (Unrecognized Tracking) — LENS A: OPERATOR & DATA

Planner A of 2. Wireframe SST: `wms2/tracking-missing/index.html` (v2, post-2026-07-23 simplification), live `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/tracking-missing/`.

---

## 1. LEGEND INVENTORY (7 units — 0·1·2·3·4·5·M1; every one lands in template §3)

| # | What it is | Spec treatment |
|---|---|---|
| **0** | New admin page declaration — replaces the manual "set aside orders without tracking number" process. Coupang creates order no. instantly, tracking no. hours later → unrecognized/unentered items collected here. Ref: F Tracking Automation. | §1 Purpose (operational moment), §4 BR (why the page exists), §10 Decision Log (page created; 07-23 v2 simplification). |
| **1** | **Unrecognized product pool** (yellow-highlight rows) — aggregates physical products sent from View Orders barcode-recognition-failure popup (M2b). Auto-collected last-mile tracking no. shown left of order no.; order no. mostly "–" (lookup-matched items never reach the pool). Columns: Tracking No / Order No / Product Name (EN) / Product Name KR / Size / Barcode / Qty / Memo / Registrant (Center) / Registered At / Suspected Orders / Action. | §3 [L-1]: full column contract, row states, count chips (`#poolCount` top + bottom), empty state. §5: pool-item entity schema + creation event (source = View Orders M2b). §4 BR single-entry-point rule. |
| **2** | **Suspected orders (auto-matched)** — candidates only when an order contains the product AND is in Processing; multiple possible; mostly non-Coupang JIT (Naver/Official Mall). Registration Slack alert @mentions suspected PICs → handlers only come to confirm. Ref: 2026-07-23 UX inversion. | §3 [L-2]: candidate computation rule + display (PIC · order no. · route/channel · status). §4 BR (inversion, no manual search). §5: candidate-set snapshot + recompute events (silent). §6 Slack row 1. |
| **3** | **"Review & Match" button → modal M1** + row **✕** removal. Match is to a **product line**, not order-level; no separate PIC search (manual fallback removed 07-23). Confirm = tracking no. registered to that product line, item leaves pool, auto comment on the order @mentioning the registrant → Slack. ✕ = cleanup for mis-registrations / no-action items. Ref: F Flow 2·5. | §3 [L-3]: both buttons — labels, enabled conditions, effects, toast (`matchToast`) text. §5: match-confirm + removal events (old/new values). §6 Slack match-confirmed row. §7 double-click / concurrent-resolver cases (flag to B). |
| **4** | Brand name always prefixed on Product Name (inherits View Orders decision B; [G-6] delta: KR column also carries EN bold brand). | §3 [L-4] one-liner citing [G-6]; §4 rationale (operator recognition speed). |
| **5** | Comments hub (top-right): [@ Mentions] + [★ Saved] + full-text search, newest first, badge = unread, click opens the order. [G-7]. Wireframe shows comments attached to "Unrecognized pool" items as well as orders. | §3 [L-5]: page delta only — pool items are a commentable **entity type** (not just orders). §5 comment events incl. read/star state. §6 mention routing → #fulfillment-admin-comments. |
| **M1** | Modal "Review & Match — Unrecognized Product": item summary card (barcode · tracking · no order no. · qty · registrant · memo) + candidate table (Order / PIC / Channel / Included Product / "Match to this product" green button) + behavior note + Cancel. | §3 [L-M1]: full modal contract — per-candidate-line match button, confirm side effects (tracking write, pool removal, auto comment "@{registrant} Matched the unrecognized product ({product}) to this order", Slack), toast, close paths. §8 QA anchor. |

Non-legend page furniture to still spec: success toast `matchToast` (part of L-3/M1, [G-2]); bottom count line; nav/Comments badge. Dead CSS/JS leftovers from v1 (`.trk`, `.shelf`, `.wait`, `.picava`, `.cntchip`, `.logsec`, trk-input script block) are **not implementation units** — spec must explicitly exclude them so devs don't build ghost features (per-PIC groups, wait chips, resolved log all removed 2026-07-23).

---

## 2. SECTION OUTLINES (10 template sections)

**§1 Purpose & Users** — Order-team PICs (Dean/Egita/Harshit/Miranti in mock) + warehouse registrants (Center). Operational moment: Coupang generates tracking numbers hours after order creation → scans fail at the packing bench; physical product is set aside and registered from View Orders; this page is the **desk-side resolution surface**, notification-driven (PIC arrives from a Slack @mention, not by polling). Physical context: the registrant is at the scan station under speed pressure (registration UI lives on View Orders, deliberately minimal); the resolver is at a monitor. **This page has no scan input** — [G-1] applies only via the cross-page rescan loop.

**§2 Screen Inventory & Wireframe Map** — Single state s1 (pool + resolution) + modal M1 (wf-bar button "Modal: Match Review (M1)") + Comments hub dropdown. Legend↔section map per table above. Live URL + how to open M1 (wf-bar tab or row button).

**§3 Functional Specification** — [L-0]..[L-5], [L-M1] as inventoried. Key precision points I will write: pool row field contract incl. "–" order-no. semantics; candidate line rendering (PIC bold · Order n blue · route (channel) · status); Review & Match opens M1 scoped to that row; per-candidate "Match to this product" is the only confirming action (no modal-level confirm); Cancel/backdrop/✕ close with zero side effects; ✕ row removal immediate (see OQ-1 on confirm/reason); toast contents exactly as wireframe ("✓ Matched to Order… / Tracking … registered · removed from pool · @… notified via Slack"); no full-page refresh anywhere [G-2]; count chips decrement.

**§4 Business Rules** — see deep list below (BR-1..BR-13 with dates).

**§5 Data Capture** — the full event enumeration below (18 events); this is the owner-priority section [G-8].

**§6 Integrations** — 3 Slack rows (below); cross-page: View Orders M2/M2b (registration source), View Orders rescan resolution, View Orders State 6 via inbound-request (unrequested-inbound path, 2026-08-02); deep links: Comments-hub click → order page; suspected-order number → order [G-12]. No print pipeline on this page ([G-4] N/A). No sheet/BI handoff.

**§7 Edge Cases** — A-lens contributions to B's inventory: empty pool (empty state), empty candidate list ("data is wrong" doctrine — what the operator does, OQ-4), candidate went out of Processing between page load and M1 confirm (stale candidate), two resolvers matching the same item concurrently, same barcode registered twice (two pool rows), qty>1 item matched to a line with qty 1, ✕ pressed by mistake (soft-delete recovery, OQ-1), Slack delivery failure at registration (item must still enter pool — notification is not the transaction), unrequested-inbound item mistakenly matched to a customer order.

**§8 QA Acceptance Criteria** — B owns; I will hand over event-assertion hooks: every scenario ends with "AND the following events were persisted" clauses keyed to §5 event IDs.

**§9 Out of Scope & Open Questions** — photo registration (deferred 2026-07-21, handoff F); per-PIC groups / bulk bar / resolved log / unified search / in-page register (all removed 07-23 — listed so nobody re-adds them); Procurement Hub (excluded 08-02); OQ list below.

**§10 Decision Log** — dated entries: page introduced (F, 07-09 plan); 07-13 v20-era pool format; **2026-07-21** photo registration held (removed from view-orders modal; this page's photo column later deleted — 08-03 item 15); **2026-07-23** major simplification (groups/bulk/Slack-column/log/search/in-page-register removed; single entry point; matching UX inversion; manual-search fallback removed; Coupang order-no format 12101316464794); **2026-08-02** unrequested inbound reuses this pool (separate temp path rejected by owner); **2026-08-03** match-confirm writes tracking no. directly on the product line → rescan resolves (d09fe79, cross-ref View Orders); 2026-08-03 English pass (63 replacements); 2026-08-03 #fulfillment-admin-comments confirmed (C0BMGEWM5QA); 2026-08-03 global toast emphasis [G-2].

---

## 3. LENS-A DEEP INVENTORY

### 3a. Data Capture — full event list (18 events; each with actor · timestamp · entity · old/new)

Entity: `unrecognized_item` (pool row). Lifecycle statuses: OPEN → MATCHED | REMOVED. Soft-delete only — [G-8]: UI pool is a view over persisted events; nothing is ever hard-deleted.

| # | Event | Actor | Entity | Old → New / payload | UI-visible? |
|---|---|---|---|---|---|
| E1 | `unrecognized_item.created` | registrant (warehouse, via View Orders M2b) | pool item | null → {barcode, product_id (autocomplete pick), EN/KR name, size, qty, memo, auto-collected last-mile tracking no., carried failed-lookup order no. (nullable), registrant, center, created_at} | yes (pool row) |
| E2 | `unrecognized_lookup.attempted` | registrant | scan session | {barcode, entered order no. or "no order number", result: matched / no-match / sent-to-pool} | **silent** — measures how often Coupang lookup fails (process KPI) |
| E3 | `suspected_orders.computed` | system | pool item | candidate-set snapshot at registration: [{order_id, product_line_id, PIC, channel, route, status}] | yes (column) |
| E4 | `suspected_orders.recomputed` | system | pool item | old set → new set + trigger reason (order entered/left Processing) | yes (column refresh) |
| E5 | `slack.notified.registration` | system | pool item | channel #unrecognized-tracking, payload (tracking no., product, qty, memo, registrant, suspected orders), @mentioned PIC list, message ts, delivery ok/fail | silent (v1 Slack-notified column removed 07-23) |
| E6 | `unrecognized_item.match_confirmed` | resolver | pool item | status OPEN → MATCHED; selected {order_id, product_line_id}; resolver; resolved_at; latency (created→resolved, derivable) | yes (row disappears + toast) |
| E7 | `order_line.tracking_no_set` | resolver (attributed), source=`unrecognized-match` | order product line | tracking no. null/"–" → value; source distinguishes this from direct M2 match on View Orders | yes (on order pages) |
| E8 | `comment.auto_posted.match` | system (on behalf of resolver) | order | comment text "@{registrant} Matched the unrecognized product ({product}) to this order", mention target = registrant, link back to pool item id | yes (order Comments) |
| E9 | `slack.notified.match` | system | comment | #fulfillment-admin-comments (C0BMGEWM5QA) payload per routing row; message ts; ok/fail | silent |
| E10 | `unrecognized_item.removed` | operator | pool item | status OPEN → REMOVED (+ reason if OQ-1 approved; + optional inbound-request linkage per OQ-5) | yes (row disappears) |
| E11 | `unrecognized_item.rescan_resolved` | scanner operator (View Orders) | pool item ↔ order | after E6/E7, same barcode rescan resolves normally; event links scan to the matched line (closes the physical loop) | cross-page |
| E12 | `comment.posted` | any user | pool item **or** order | text, mentions[]; pool items are a first-class commentable entity (wireframe: "Unrecognized pool · Miranti: …") | yes |
| E13 | `comment.mention_notified` | system | comment | Slack @mention route [G-7]; ts, target, ok/fail | silent |
| E14 | `comment.read` / `comment.mark_all_read` | user | mention items | unread → read (per item or bulk) | yes (badge count) |
| E15 | `comment.star_toggled` | user | comment | saved false↔true | yes (★) |
| E16 | `match.duplicate_suppressed` | system | pool item | second confirm on an already-MATCHED item rejected by server idempotency key [G-9]; log the suppressed attempt (actor, ts) | silent |
| E17 | `match.rejected_stale_candidate` | system | pool item | confirm attempted on a candidate no longer Processing → server rejects; old status snapshot logged | silent + error toast |
| E18 | `unrequested_inbound.routed` | owner/PIC | pool item | memo-flagged "suspected inbound stock" item → inbound request {request_id} created on inbound-request page, invoice no. entered, then E10 removal; linkage field per OQ-5 | cross-page |

Retention/export: all events retained indefinitely (AI-training asset doctrine, [G-7]/[G-8]); resolution latency (E1→E6) and lookup-failure rate (E2) are the page's two derivable ops metrics — spec will state they must be computable from persisted events without extra instrumentation.

### 3b. Operator-flow notes (field usability)

- **Push, not poll**: the resolver's flow starts in Slack (@mention with suspected orders already attached) → opens page → row is pre-highlighted context → one click Review & Match → one click "Match to this product". Two clicks total at the desk; zero search/typing. Spec must protect this: no filters/search bars re-introduced (07-23 removal is deliberate — pool is expected to hold only a few items).
- **Registrant never leaves the bench**: registration (M2b) is on View Orders with autocomplete + qty + optional memo only; this page adds zero registrant burden. Memo is the registrant→resolver channel (e.g., "Box label damaged", "Looks like a 1+1 set", "suspected inbound stock") — spec should encourage memo conventions but keep it optional.
- **No scan surface here** → [G-1] delta: N/A on-page; the loop closes when the bench operator rescans on View Orders (E11). Spec must state the physical product stays set aside until the resolver confirms, then rescan proceeds as a normal flow.
- **Qty>1 and set ambiguity** (medicube 1+1 row, qty 2 + memo): matching is per product line — resolver relies on memo + KR name + size columns to judge sets. KR name column exists because bench staff and memos reference Korean names [G-6].
- **✕ is one click with no confirm in the wireframe** — at speed this is a mis-click hazard on a destructive-looking action sitting next to the primary button (OQ-1).
- **Aging visibility**: after 07-23 the wait-time chips are gone; "Registered At" is the only age signal. No escalation exists for stale pool items (OQ-2).

---

## 4. BUSINESS RULES (for §4 — with rationale + dates)

- **BR-1 Single registration entry point** = View Orders unrecognized popup (M2→M2b). In-page register button/modal removed. Rationale: registration must happen where the physical product and scanner are. (2026-07-23)
- **BR-2 Matching UX inversion**: system presents suspected orders + PICs; handler only confirms. Old flow (handlers searching their own name per product) reversed. (2026-07-23)
- **BR-3 Candidate rule**: orders that contain the product AND are in Processing; multiple possible; Coupang orders are pre-filtered by the registration-time order-number lookup, so candidates are mostly JIT Naver/Official-Mall. (2026-07-23, restated 08-03 English pass)
- **BR-4 No manual PIC search fallback** — "if it is not here, the data is wrong". Empty candidates = upstream data problem, not a search problem. (2026-07-23)
- **BR-5 Match target is a product LINE, not an order.** Tracking no. written directly onto the line → same-barcode rescan resolves normally. (2026-08-03, d09fe79; cross-ref View Orders behavior-rules footnote)
- **BR-6 Registration auto-notifies #unrecognized-tracking and @mentions suspected PICs** — the pool works only because notification is automatic. (2026-07-23 inversion; channel CONFIRMED 2026-08-03)
- **BR-7 Match confirm auto-posts an order comment @mentioning the REGISTRANT** (closes the loop back to the warehouse bench) → #fulfillment-admin-comments. (2026-08-03)
- **BR-8 ✕ removal is soft** — sanctioned for mis-registrations and no-action items; event + full item snapshot persisted forever [G-8]. (07-23 button; doctrine 08-03)
- **BR-9 Unrequested inbound shipments reuse this pool** — separate temp registration path rejected by owner. Flow: register with "suspected inbound stock" memo → owner creates inbound request + enters invoice no. → ✕ removes row → rescan enters View Orders State 6. (2026-08-02, confirmed in legend footnote)
- **BR-10 Order number = Coupang purchase order number** (12101316464794 format); pool order-no. column is mostly "–" by design. (2026-07-23)
- **BR-11 Photo registration deferred** — no photo column/upload anywhere on this page. (2026-07-21 hold; column deletion 2026-08-03 review item 15)
- **BR-12 Naming**: EN name brand-bold-prefixed; KR column carries EN bold brand too [G-6 delta]. (decision B, reconfirmed 08-03)
- **BR-13 Route/channel labels** on candidates are plain bold black text, route (channel) notation identical to View Orders [G-5]; route originates from Inbound Request (I) matched via invoice number.
- Global deltas cited, not restated: [G-2] toast (matchToast + any future removal toast), [G-9] idempotency on match confirm, [G-12] deep links.

---

## 5. SLACK ROUTING ROWS THIS PAGE USES (all CONFIRMED in `_inputs/slack-routing.md`)

| Trigger | Channel | Payload | Note |
|---|---|---|---|
| Unrecognized barcode sent to Missing Tracking List (E5) | **#unrecognized-tracking** | tracking no., product (autocomplete pick), qty, memo, registrant, suspected orders; @mentions suspected PICs | CONFIRMED; fires from View Orders M2b but is this page's inbound feed |
| Match confirmed in Unrecognized Tracking (E8/E9) | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) via comment auto-post + @registrant | tracking no., matched product line, resolver | CONFIRMED — routes as a comment mention |
| Comment @mention on pool items / orders from this page (E13) | **#fulfillment-admin-comments** (`C0BMGEWM5QA`) | order/entity no., comment text, time, author, @mentioned user, deep link | CONFIRMED (owner, 2026-08-03) |

Explicitly NOT this page: morning no-tracking checks → #wholesale-ops / #partnership-kr (inbound-request page rows).

---

## 6. MANDATORY-INCLUSION MAP (of the 12)

- **#6 Unrecognized matching behavior** — PRIMARY home = this page (§3 L-3/M1, §4 BR-5, §5 E6/E7/E11); shared with view-orders (registration + rescan side).
- **#2 Global confirmation toast [G-2]** — §3 (matchToast; ✕ removal toast gap flagged to B/OQ-1).
- **#12 Comment @mention Slack routing [G-7]** — §5 E12-E15, §6 routing table (channel now CONFIRMED, no longer pending).
- **#7 Multiple tracking numbers [G-10]** — cross-reference only, via BR-9 unrequested-inbound → inbound-request → State 6 path (primary home inbound-request/view-orders).
- **#1 Scanner protocol [G-1]** — explicit N/A statement + cross-ref (no scan input here; rescan loop lives on View Orders). Not silently omitted.
- #3, #4, #5, #8, #9, #10, #11 — N/A this page (state in §9 Out of Scope).

---

## 7. OPEN QUESTIONS (not decided — flagged, not invented)

**Owner must decide:**
1. **✕ removal safeguards** — wireframe has one-click removal with no confirmation dialog and no reason field. Should removal require (a) a confirm step, and/or (b) a mandatory reason (mis-registration / routed to inbound request / no action), given the data-capture doctrine records old/new + why elsewhere (cf. [G-11] qty-edit reason)?
2. **Pool aging escalation** — after the 07-23 simplification there is no wait-time display and no stale-item alert. Is any re-notification for items sitting unresolved (e.g., >24h) wanted, and to which channel? (Morning checks currently cover inbound requests only.)
3. **Empty-candidates guidance** — BR-4 removed manual search ("the data is wrong"). What exact instruction does the UI give when Suspected Orders is empty: fix upstream order data, route via inbound request, or ✕? (Wireframe is silent.)
4. **Photo column final status** — 2026-07-21 hold said "check later whether the tracking-missing photo column needs cleanup"; the column is now deleted (08-03 item 15). Confirm "no photos, permanently" vs "deferred to a later phase" wording in the spec.
5. **Unrequested-inbound linkage** — when a pool row is removed because an inbound request was created (BR-9), should the removal event capture the Inbound Request no. (structured link) or is the memo convention enough?

**Developer decides at build time:**
6. Idempotency key scheme for match confirm and ✕ [G-9].
7. Candidate recompute trigger (on page load vs event-driven when orders enter/leave Processing) and stale-candidate rejection UX (E4/E17).
8. Concurrency handling for two resolvers on the same pool item (optimistic lock + error toast; E16).
9. Whether comment-search queries are captured as silent telemetry events (doctrine leans yes; zero UI impact).
10. Storage/export mechanics for pool-event history (CSV/BI); no UI export exists and none is specced.
11. Confirmation that v1 leftover CSS/JS (`.trk`, `.shelf`, `.wait`, `.picava`, `.cntchip`, `.logsec`, trk-input script) is ignored — not implementation units.
