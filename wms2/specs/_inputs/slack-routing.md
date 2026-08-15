# Slack Routing (CONFIRMED 2026-08-03)

| Trigger | Channel | Payload | Status |
|---|---|---|---|
| Unrecognized barcode sent to Missing Tracking List | #unrecognized-tracking | tracking no., product (autocomplete pick), qty, memo, registrant, suspected orders | CONFIRMED |
| Morning check: inbound request has no tracking number (WHOLESALE·SMART BUY) | #wholesale-ops | Inbound No., supplier, requested-by, age | CONFIRMED (daily 1×) |
| Morning check: inbound request has no tracking number (PARTNERSHIP) | #partnership-kr | same | CONFIRMED (daily 1×) |
| Comment @mention (any screen) | **#fulfillment-admin-comments** (channel ID: `C0BMGEWM5QA`) (message body @mentions the tagged person → Slack sends them a personal mention notification; channel doubles as team-visible archive) | order/entity no., comment text, time, author, @mentioned user, deep link to the entity | CONFIRMED (owner, 2026-08-03) |
| Expected-qty edit on inbound request | comment auto-post on the request + @requester (same route as comment mention) | old→new qty, reason, editor | CONFIRMED — routes to #fulfillment-admin-comments with @mention |
| Match confirmed in Unrecognized Tracking | comment auto-post + @registrant | tracking no., matched product line, resolver | CONFIRMED — routes to #fulfillment-admin-comments with @mention |
| Other-channel notifications (future routes) | decide per feature at dev time | — | — |
