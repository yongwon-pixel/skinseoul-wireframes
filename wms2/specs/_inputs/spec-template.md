# Spec Template — WMS 2.0 Screen Specifications (v1, 2026-08-03)

Every screen spec MUST use these 10 sections, in this order. Audience priority: (1) AI agents that will read everything and execute QA end-to-end, (2) developers implementing without ambiguity, (3) reviewers. Write in English. Be exhaustive — "nothing left ambiguous" is the acceptance bar set by the owner. When a behavior references a global rule, cite it as `[G-n]` from `_global-rules` instead of restating it, then add only page-specific deltas.

## 1. Purpose & Users
What the screen is for, who uses it (warehouse staff / order team / admin), and the operational moment it serves. Include the operator's physical context (scanner in hand, distance from monitor, gloves, speed pressure) when it shaped a decision.

## 2. Screen Inventory & Wireframe Map
Table of every state, tab, modal, and sub-page with: wireframe legend number(s) ↔ spec section 1:1 mapping, live wireframe URL + how to reach the state (which top-bar button/tab). The wireframe legend numbers are the implementation units — every legend item MUST appear somewhere in section 3.

## 3. Functional Specification
Per legend item (keyed `[L-n]`): trigger, exact behavior, inputs/outputs, validation rules, server actions, state transitions, idempotency requirements, and what the user sees at every step (including toasts/sounds). Buttons: exact label, enabled/disabled conditions, effect, confirmation feedback.

## 4. Business Rules
Page-specific rules with rationale and decision date. Reference global rules by ID. Include rules that exist to protect operations (e.g., gating, exact-match closing, no auto-confirm).

## 5. Data Capture (mandatory section — owner priority)
Enumerate EVERY event this screen must persist to the admin DB: actor, timestamp, entity, old/new values, quantities. Include logs surfaced in UI (actor log, scan feed, audit logs, comment history) AND events persisted without UI. State retention/export expectations. The doctrine: maximize data accumulation in admin.

## 6. Integrations
- Slack routing table: trigger → channel → payload fields → mention target (use `_slack-routing`).
- Cross-page links and deep links (e.g., `#reqlist`).
- Sheet/BI handoffs (e.g., Inbound Request list → Procurement Hub sheet pull; Closing → Daily Shipping Status).
- Print pipeline: local print agent, carrier-agnostic instant output [G-4].

## 7. Edge Cases & Error States
Exhaustive enumeration with expected behavior for each: scan failures, duplicates, over-scan, partial arrivals, damaged goods, cancelled orders, concurrent operators, network failure mid-action, printer offline, empty states, permission edge cases. Each edge case gets an ID `[E-n]` for QA reference.

## 8. QA Acceptance Criteria (machine-runnable)
Given/When/Then scenarios keyed to `[L-n]`/`[E-n]`, written so an AI agent can execute them against the live wireframe (and later the real admin) — exact selectors/labels to click, exact expected texts/sounds/toasts. Include negative tests. This section is the QA runbook; completeness here is what makes automated QA possible.

## 9. Out of Scope & Open Questions
What this screen explicitly does not do; unresolved decisions with owner and blocking status.

## 10. Decision Log
Dated list of every decision that shaped this screen (from planning docs, review rounds 2026-07-09 → 2026-08-03), including reversals (e.g., sample assignment removed 07-22 → reinstated as ON/OFF 07-23). Nothing gets silently dropped — this is the "no second-guessing later" record.
