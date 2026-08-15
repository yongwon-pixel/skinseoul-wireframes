# Decision Sources & Mandatory Inclusions (for planning agents)

## Sources (read ALL before planning)
1. **Wireframes (SST for screens)** — `wms2/{slug}/index.html`, live at `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/{slug}/`. Legend numbers = implementation units. Legends already encode most decisions with dates.
2. **Planning doc (Notion, sections 0~J)** — fetch `38705a34aa25800da0bfec9900639b1c` via mcp__notion__notion-fetch (load via ToolSearch). Struck-through items are dead — do NOT spec them; the replacement memo next to them is the truth.
3. **Developer handoff notes (Notion)** — `3b005a34aa258184828dfa13877a09b7` (6 implementation notes: double-click bug, print agent, YUN landscape method, photo-upload deferred, audit cost source, G corrections).
4. **Decision ledgers (Korean, read for dates/reversals)** — (internal decision ledger, not published) and `2026-08-02-wms2-en-spec-handoff.md`.
5. Local inputs: `spec-template.md`, `global-rules-draft.md`, `slack-routing.md` (this folder).

## Mandatory inclusions (owner-flagged — every one must land in the right page spec)
1. Scanner protocol [G-1] — View Orders + Closing
2. Global confirmation toast [G-2] — all screens
3. Audio feedback [G-3] — View Orders/RTO (send sound), Closing (voice)
4. **Instant carrier-agnostic print [G-4]** — any Print button, any carrier, immediate output (View Orders, RTO, Order Detail, Closing report)
5. Sample dual-view + exactly-1-set [G-13] — Order Management (+ label implications noted, label details deferred to Phase 3-1 discussion with owner)
6. Unrecognized matching behavior — match writes tracking no. onto that order's product line; rescan resolves (View Orders + Unrecognized Tracking)
7. Multiple tracking numbers per inbound request [G-10] — Inbound Request + View Orders
8. RTO Korean item names [G-6] — RTO
9. Line-based location filter, dynamic lines [G-14] — Inventory
10. Audit-mode-only summary visibility [G-14] — Inventory
11. JIT residual stock in Inventory (order cancellations etc.) — Inventory
12. Comment @mention Slack routing with named channels [G-7] — all screens (channel decision pending owner)

## Page assignments (8 specs, no label appendix)
view-orders · order-detail · ready-to-outbound · stock-status (Inventory) · order-management · tracking-missing (Unrecognized Tracking) · closing · inbound-request
Label/invoice layout content is discussed separately with the owner AFTER Phase 3 ("Phase 3-1") — specs reference print behavior [G-4] and dual-view [G-13] but do not spec label layouts.
