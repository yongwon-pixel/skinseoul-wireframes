# M2 — Adversarial QA execution of `closing.md` §8

**Verifier role:** hostile QA robot. I did not write this spec and used no knowledge of the page
beyond what §8 supplies. Selectors, expected strings and activation steps come from §8 only; the
wireframe source was consulted **after** a failure, solely to quote what the page actually does.

- **Spec under test:** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/closing.md` §8 (lines 1033–2112)
- **System under test:** `file:///Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/closing/index.html`
- **Runner:** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_verify/qa-closing.py` (Playwright · python · headless chromium · viewport 1440×900)
- **Raw results:** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_verify/qa-closing-results.json`
- **Wireframe-defect cross-reference:** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_plans/_wireframe-fixes.md`

---

## 1. Methodology

### 1.1 Scenario extraction

`grep -E '^\*\*QA-'` over §8 yields **168 scenario headers**; 68 carry `` `[WF]` ``, 100 carry
`` `[ADMIN]` ``, 68 carry `(negative)`. Those three counts match §8.0's claimed
"168 scenarios — 68 `[WF]` · 100 `[ADMIN]` · 68 negative tests (40.5%)" **exactly**, and the
per-block splits in the §8.16 coverage table also reconcile block-by-block (4+4+5+3+3+6+5+5+5+6+7+6+4+0+5 = 68 WF; 100 ADMIN). The spec's own arithmetic is sound.

The brief asked for ≥25 adversarially-weighted scenarios. I ran **all 68 `[WF]` scenarios** instead
of sampling — the population is small enough that sampling would only weaken the result.
**405 individual assertions** were executed (401 passed, 4 failed).

### 1.2 Execution rules taken verbatim from §8.0

| Rule | How it was implemented |
|---|---|
| **R1** reset between mutating scenarios | every scenario begins with a fresh `page.goto()` — no scenario inherits another's DOM |
| **R2** strip `.dot` before comparing text | `window.__t()` injected exactly as printed in §8.0 (clone → remove `.dot` → collapse whitespace → trim) |
| **R3** address states/modals by attribute | `.wf-tab[data-state="…"]`, `.wf-tab[data-modal="…"]`, `section#s2b`, `#m-process` — never by tab text |
| **R4** instrument speech on document start | the §8.0 snippet injected via `context.add_init_script`, verbatim |
| **R5** row addressing by first-cell text | `window.__row('#s1','#3')` helper, exactly the §8.0 expression |
| **R6** byte-exact incl. `·` `—` `✓` `⚠` `✕` `①` | all string comparisons are Python `==` on the R2-normalized value; no ASCII folding |
| **R7** page-global demo state | `voiceOn` / `lastState` treated as page-global; `lastState` read with `page.evaluate(() => lastState)` |
| **R8** known demo limitations are not bugs | asserted as *demo behavior* where §8 says so (tiles do not recompute, silent no-op start, no cancel dialog, 79-not-81, State 4 input enabled, …) |

### 1.3 Verdict rules

- **PASS** — every assertion the spec states was executed and held.
- **FAIL** — spec says X, page does Y. Both quoted.
- **AMBIGUOUS** — the spec does not say what to click or what to assert. Recorded, not improvised.
  Where a scenario is ambiguous in *one clause only*, the clause is recorded as ambiguous and the
  scenario is scored on its remaining clauses (marked `PASS ⚠` in the table below).
- **UNRUNNABLE** — assertion impossible against a static mock and not tagged `[ADMIN]`.

### 1.4 One derivation the spec forced

§8 never says **how to make a state active**. Every scenario opens with "Given `section#s2b` is
active" and stops there. It is derivable — R3 plus the explicit "When `.wf-tab[data-state="s2"]` is
clicked" in QA-VOICE-01 and QA-HIST-05 — so I clicked the corresponding `wf-tab`, and every
subsequent assertion in every state passed, which retro-validates the derivation. It is still a
one-hop inference the spec should not require. See fix **F5**.

---

## 2. Results

**68 attempted · 65 PASS · 3 FAIL · 0 AMBIGUOUS (whole-scenario) · 0 UNRUNNABLE.**
4 scenarios passed with one under-specified clause each (`PASS ⚠`).

| # | Scenario | Verdict | Assertions | Evidence / quote |
|---|---|---|---|---|
| 1 | QA-S0-01 | PASS ⚠ | 15 | s0 `on`, six others not; tab text `"0 · Before Start (manual count)"`; `#targetIn0` ph=`"Hand-counted qty"` value=`""`; next sibling text `"orders"`; `#startBtn0` = `"Start Closing"`. ⚠ "the card heading" names no selector — resolved by exact-text search inside `#s0` (1 match) |
| 2 | QA-S0-02 | PASS | 5 | click `#startBtn0` with `value===""` → `#s0` still `on`, `#s1` not; 0 `.scanbig` in the active section; 0 **visible** `.toast` |
| 3 | QA-S0-03 | PASS | 3 | `84` → `#s1.on`, `#s0` off, `.wf-tab[data-state="s1"].on` |
| 4 | QA-S0-04 | PASS | 6 | `#s0` has 0 × `.scanbig`/`.clsstat`/`.prog`/`table.tbl`/`.okline` and 0 buttons starting `"Confirm Closing"` |
| 5 | QA-SCAN-01 | PASS | 5 | placeholder + `value="YT2618100710108810"` + sibling `button.btn-blue` `"Scan"` + not `disabled` |
| 6 | QA-SCAN-02 | PASS | 2 | `#s0 .scanbig` = 0; `#s0 input` ids = `['targetIn0']` |
| 7 | QA-SCAN-13 | PASS | 3 | `#s4 .scanbig input` `value===""`, no `disabled` (U-b documented as-is) |
| 8 | QA-SCAN-16 | PASS | 1 | background click → `activeElement !== #s1 .scanbig input` |
| 9 | QA-VERDICT-01 | PASS | 8 | row `#1` `row-ok`; `span.cs-shipped` `"Prepare Shipment"` / `"✓ Outbounded"`; Notes `"–"`; Worker `"Dean"` |
| 10 | QA-VERDICT-02 | PASS | 5 | `.okline b` = `"✓ #5 Outbounded"`; contains `"Order 413540 · Tracking YT2618100710108810 · Prepare Shipment"`; `.mut` = `"18:41:07 · Dean"`; `#s1 .bigstatus` = 0 |
| 11 | QA-VERDICT-03 | PASS | 9 | row `#4` `row-bad`; `cs-processing` × 2; Notes button `"Process this order"` `data-modal="m-process"`; `#s2 .bigstatus` = 0 |
| 12 | QA-VERDICT-04 | PASS | 2 | 0 `tr.row-ok` with that button; 0 with `cs-processing`/`cs-dup` |
| 13 | QA-VERDICT-05 | PASS | 3 | 10 headers exactly as listed; **raw** `textContent` confirmed to be `"#6"` / `"Closing Verdict5"`, proving R2 is required; trailing paragraph byte-exact |
| 14 | QA-UNKNOWN-01 | PASS | 7 | row `#7` `row-bad`; Order ID/Items/Status all `"–"`; `span.cs-dup` `"⚠ Unknown order"` |
| 15 | QA-UNKNOWN-02 | PASS | 1 | Notes exactly `"Mistyped tracking no. or an order from another system — check the physical label"` |
| 16 | QA-UNKNOWN-03 | PASS | 3 | `.tile.warn .lab` = `"Warnings (not outbounded · duplicate · unknown order)"`, `.val` = `4`; proglab contains `"unknown orders are not counted"` |
| 17 | QA-DUP-01 | PASS | 6 | row `#6` `row-bad`; `"⚠ Duplicate scan"`; `b` = `"Duplicate of #2"`; `"— first scanned 18:40:18 (Miranti)"` |
| 18 | QA-DUP-02 | PASS | 6 | row `#3` `row-bad`; `b` = `"Duplicate of #2"`; `"same tracking no. (check for combined box)"` |
| 19 | QA-DUP-03 | PASS | 6 | `#s1` row `#2` `row-ok`, tracking/worker match, Notes `"First scan"`; identical on `#s3` row `#2` |
| 20 | QA-VOICE-01 | PASS | 15 | for each of s2/s2b/s3 on a fresh instrumented load: exactly 1 `__spoken` entry, `text="Please check this order"`, **`lang==="en-US"`**, and `data-voice` attribute present |
| 21 | QA-VOICE-02 | PASS | 3 | `#voiceState`→`"Off"`, `#s1 .vtrack` gains `off`, `__spoken` gains nothing |
| 22 | QA-VOICE-03 | PASS | 5 | with Off, clicking s3 leaves `__spoken` empty; row `#6` still `row-bad` + `"⚠ Duplicate scan"`; `#s3 .proglab` unchanged |
| 23 | QA-VOICE-04 | PASS | 6 | `#voiceTest` = `"🔊 Test voice"`; 1 utterance; state still `"Off"` and `.vtrack` still `off` |
| 24 | QA-VOICE-05 | PASS | 4 | Off→On: state `"On"`, `off` class dropped, exactly 1 utterance |
| 25 | QA-VOICE-08 | PASS | 6 | `#s1 #voiceTest`=`"🔊 Test voice"`; `#s2`/`#s2b`/`#s3` `.sim-voice`=`"🔊 Play again"`; `#s4` `.sim-voice`=`"🔊 Test voice"` |
| 26 | QA-COUNT-01 | PASS | 3 | vals `["84","3","2","79"]`; four labels exact; proglab does say `"81 short of the manual count"` (U-a confirmed) |
| 27 | QA-COUNT-02 | PASS | 2 | inline widths `3.6%` / `2.4%` |
| 28 | QA-COUNT-03 | PASS | 1 | `.proglab` byte-exact incl. `—` and `·` |
| 29 | QA-COUNT-09 | PASS | 4 | s2b `["84","4","4","80"]` + `p-warn 4.8%`; s3 `["84","4","3","80"]` + `"duplicates are not double-counted"` |
| 30 | QA-COUNT-10 | PASS | 4 | s2 `["84","4","3","80"]`; `4.8%`/`3.6%`; proglab byte-exact |
| 31 | QA-TARGET-01 | PASS | 6 | banner `b` + `"Closing in progress (started 18:02 · Dean)"`; `#targetIn1` `84` + `disabled`; both buttons |
| 32 | QA-TARGET-02 | PASS | 4 | unlocked, `document.activeElement`, `selectionStart=0`/`selectionEnd=len`, label `"Save"` |
| 33 | QA-TARGET-03 | PASS | 2 | re-`disabled`, label back to `"↺ Edit count"` |
| 34 | QA-TARGET-04 | PASS | 3 | `#s0` active immediately, `#s1` loses `on`, `.overlay.open` = 0 before and after (WF-7 gap confirmed) |
| 35 | QA-TARGET-12 | PASS | 12 | s2/s2b/s3: no `.clsbanner.info`, `p.mut` line present, no `#targetEdit`, no `#closeCancel` |
| 36 | QA-M1-01 | PASS | 3 | row-`#4` button opens `#m-process` from `#s2`; identical button in `#s1` row `#4` opens the same modal |
| 37 | QA-M1-02 | PASS | 9 | header **starts with** the title; body `b`; tracking line; checkbox label both fragments; textarea placeholder; `.note` both fragments |
| 38 | QA-M1-03 | PASS | 2 | `.foot` has `"Close"` and `button.btn-green` `"Process Outbound → resolve warning"` |
| 39 | QA-M1-04 | PASS | 9 | all three dismissals (footer Close, header `✕`, `MouseEvent` on the overlay itself) close the modal and leave row `#4` intact |
| 40 | QA-M1-11 | PASS | 5 | button not `disabled`, carries `data-close`; click closes modal, row still `row-bad` / `"⚠ Not outbounded"` |
| 41 | **QA-DEL-01** | **FAIL** | 5 pass / 1 fail | **spec:** ``its `header` reads "Delete Scan Row"`` · **page:** R2-normalized header = `"Delete Scan Row✕"` (`index.html:780` `<header>Delete Scan Row<button class="x" data-close>✕</button></header>`). Every other clause passed (`#m-scandel.open`, body `b` `"Remove this scan?"`, `#scandelInfo` = `"#3 · YT2618100710184356"`, `✕` title `"Delete scan row"`) |
| 42 | QA-DEL-02 | PASS | 2 | `"No"` closes; 5 rows `["#1","#2","#3","#4","#5"]` |
| 43 | QA-DEL-03 | PASS | 3 | `#scandelYes` = `"Yes — remove"`; 4 rows `["#1","#2","#4","#5"]` — no renumbering |
| 44 | QA-DEL-04 | PASS | 1 | `.note` byte-exact |
| 45 | QA-DEL-05 | PASS | 3 | tiles still `["84","3","2","79"]`, `p-warn` still `2.4%` (demo limitation confirmed) |
| 46 | QA-DEL-10 | PASS | 2 | wf-bar tab opens `#m-scandel`; `#scandelInfo` default `"#7 · YT2618100719984412"` |
| 47 | QA-CONFIRM-01 | PASS | 5 | `b` `"Confirm Closing"`; button text exactly `"Confirm Closing (79 remaining · 2 warnings)"`; all three banner fragments |
| 48 | QA-CONFIRM-02 | PASS | 2 | class `btn-gray`; computed `cursor: not-allowed` |
| 49 | QA-CONFIRM-03 | PASS | 8 | `.bs-ok`; `.big`; `.bmeta`; `.bside` fragments; **`.bs-warn` = 0 document-wide**; `.bigstatus` = exactly 1, inside `#s4` |
| 50 | QA-CONFIRM-04 | PASS | 3 | toast span + `small`; no class `err` |
| 51 | QA-CONFIRM-05 | PASS | 5 | `b` `"Closing Report"`; the copy fragment; CSV button; **0 leaf elements whose text contains `"Print"`**; 0 buttons named `"Print"` |
| 52 | QA-CONFIRM-06 | PASS | 6 | `b` `"Warning Resolution Summary"` + full sentence; tiles `["84","84","0","0"]`; 3rd lab `"Warnings (resolved)"`; `p-ok 100%`; no `p-warn` |
| 53 | QA-CONFIRM-15 | PASS | 5 | no `#targetEdit`/`#closeCancel`; no `.clsbanner.info` whose `b` is the target heading; no `"Confirm Closing…"` button; `p.mut` line present |
| 54 | QA-HIST-01 | PASS | 8 | `#s1 [data-goto="shist"]` = `"Closing History"`; navigates; tab present in s0/s2/s2b/s3/s4 |
| 55 | QA-HIST-02 | PASS | 1 | 8 header cells exactly as listed, last empty |
| 56 | QA-HIST-03 | PASS ⚠ | 3 | row = `["07-13 (today)","84","84","3→3","✓ Match","Yongwon","18:52"]` + `"CSV"`. ⚠ "green highlight" has no stated value/selector — resolved via inline `background:var(--green-soft)` + computed-colour diff vs row 2 |
| 57 | QA-HIST-04 | PASS | 2 | both paragraphs byte-exact (incl. the straight `"Match"` quotes) |
| 58 | QA-HIST-05 | PASS | 4 | s2 → shist; **`lastState === "s2"`** readable via `page.evaluate(() => lastState)`; `"Closing"` returns to `#s2` |
| 59 | QA-HIST-10 | PASS | 4 | 5 rows in stated date order; all `"✓ Match"`; OK == Target on every row; CSV on every row |
| 60 | **QA-HUB-01** | **FAIL** | 4 pass / 2 fail | **(a) spec:** ``the nav button `#s1 [data-open="inbox1"]` reads "💬 Comments"`` · **page:** `"💬 Comments2"` (`index.html:275` `…>💬 Comments<span class="badge-n">2</span></button>` — the badge the very next clause asserts is *inside* the button). **(b) spec:** ``its Mentions pane header reads "Comments where I'm tagged"`` · **page:** `"Comments where I'm tagged Mark all read"` (`index.html:286` `<div class="paneheader">Comments where I'm tagged <small>Mark all read</small></div>`). Passing clauses: `#inbox1.open`; three `b` labels `["Order 413540","Order 413498","Order 413330"]`; first two `unread` |
| 61 | **QA-HUB-02** | **FAIL** | 5 pass / 1 fail | **spec:** ``the pane `[data-pane="saved"]` becomes visible with the header "Comments I saved"`` · **page:** `"Comments I saved Unstar to remove from this list"` (`index.html:292`). Passing: tab gains `on`, saved visible, mentions hidden, exactly one entry `"Order 413498"` |
| 62 | QA-HUB-03 | PASS | 3 | star toggles `on` → off; `"Order 413498"` star already `on` at load |
| 63 | QA-HUB-07 | PASS | 12 | s2/s0/s2b/s3/s4/shist: 0 Comments buttons with `data-open`, 0 `.inboxdd` |
| 64 | QA-CHROME-01 | PASS | 63 | all 7 sections: brand, 4 menu labels, a `💬 Comments` button, `"Yongwon Ryu"`, `"Logout"` |
| 65 | QA-CHROME-02 | PASS ⚠ | 28 | `h2` = `"WMS - Closing"`; `.pagetabs` exactly `["Closing","Closing History"]`; active tab correct in all 7. ⚠ ``p.sub reads X`` — 6 of 7 sections contain **two** `p.sub` nodes (the 2nd is the `"Scan list …"` caption), so the clause was scored as membership |
| 66 | QA-CHROME-03 | PASS | 4 | `#s1 .toast` span + small byte-exact; `#s4 .toast` same two-part shape; 0 `.toast.err` |
| 67 | QA-CHROME-04 | PASS ⚠ | 3 | `.wf-tab[data-modal="m-process"]` yields **2** with identical text; **legend-unit count = 22** (19 `.legend ol > li` + 2 modal dots + 1 `#s1 .legend > p`). ⚠ the "which would give 23" clause names no counting method; `document.querySelectorAll('.wf-tab')` is **10**, not 23 — clause left unasserted |
| 68 | QA-CHROME-06 | PASS | 3 | at 1440×900 `body.scrollWidth (1440) <= body.clientWidth (1440)`; all 10 `th` rendered, none `display:none`; `"YT2618100710184356"` present, no `…` anywhere in the tracking column |

---

## 3. FAIL analysis — culprit attribution

All three failures are **one defect with three instances**, and the culprit is **(a) the spec**.

### The defect

R2 tells the QA agent to strip **only** `span.dot` before comparing text. But the wireframe nests
*functional* descendants inside three of the elements §8 asks to compare with `reads`:

| Element | Nested descendant | R2-normalized text |
|---|---|---|
| `#m-scandel header` | `<button class="x">✕</button>` | `"Delete Scan Row✕"` |
| `#s1 [data-open="inbox1"]` | `<span class="badge-n">2</span>` | `"💬 Comments2"` |
| `.paneheader` (both panes) | `<small>Mark all read</small>` / `<small>Unstar to remove…</small>` | `"Comments where I'm tagged Mark all read"` / `"Comments I saved Unstar to remove from this list"` |

**The spec already knows about this class of problem and handles it correctly once:** QA-M1-02
asserts the *structurally identical* `#m-process header` with ``starts with "Process Processing
Order — Order 413511"`` — precisely because the `✕` button is glued on. QA-DEL-01, 12 sections
later, asserts the same shape with `reads`. That is a copy-consistency failure inside the spec, not
a page defect.

### Not a wireframe fault

`_wireframe-fixes.md` lists 14 wireframe defects (WF-1 … WF-14) plus an explicit
"do not correct these" list. **None of them mention** the modal-header `✕`, the Comments badge, or
the `.paneheader` `<small>` actions. All three are intentional, correct UI. The wireframe is right;
the expected strings are wrong.

### Verdict-flip note

If `reads` is read loosely as *contains*, all three FAILs become PASS and the run is 68/68. That is
exactly the problem: **§8 uses `reads`, `reads exactly` and `is exactly` interchangeably and R2/R6
define only the strict sense**, so two conforming QA agents will return different verdicts on the
same page. This is the single most damaging finding for the "an AI can run QA with zero questions"
goal — the ambiguity does not block the run, it silently corrupts it.

---

## 4. Spec fixes required

Ordered by damage.

**F1 — Fix the three wrong expected strings (blocks a clean run).** *Severity: high.*
- QA-DEL-01: change ``its `header` reads "Delete Scan Row"`` → ``its `header` R2-normalized text **starts with** "Delete Scan Row"`` (mirror QA-M1-02's wording).
- QA-HUB-01: change ``reads "💬 Comments"`` → ``**starts with** "💬 Comments"``; change ``its Mentions pane header reads "Comments where I'm tagged"`` → ``**starts with** "Comments where I'm tagged"`` (or assert `.paneheader` minus its `small`).
- QA-HUB-02: change ``with the header "Comments I saved"`` → ``**starts with** "Comments I saved"``.

**F2 — Make the assertion verbs normative in §8.0.** *Severity: high.*
R6 defines "byte-exact" but never binds it to a verb. Add one line, e.g.:
> *"`reads exactly` / `is exactly` = strict equality after R2. `reads` = strict equality after R2
> unless the clause says `starts with` / `contains`. `contains` = substring after R2."*
Without this, `reads` is a coin flip and the whole §8 corpus inherits the ambiguity.

**F3 — Extend R2 (or warn) for nested controls, not just `.dot`.** *Severity: high.*
R2 exists because purple annotation dots pollute `textContent`. The same pollution comes from
`button.x`, `.badge-n` and `.paneheader small` — and, latent, from
`<span class="user"><span class="avatar">Y</span>Yongwon Ryu</span>`, whose normalized text is
`"YYongwon Ryu"` (QA-CHROME-01 survives only because it says *contains*). Either extend the helper
to also drop `.dot, .badge-n, .paneheader small, header button.x, .avatar`, or add an explicit
"beware nested controls" note listing these four.

**F4 — QA-CHROME-04: the "23" is unverifiable as written.** *Severity: medium.*
`document.querySelectorAll('.wf-tab')` is **10**. The 23 is only reconstructible as
"19 `li` + 1 `p` + **3 modal tabs**" — i.e. counting modal units from tabs instead of from modals.
State that method, or drop the clause. A QA agent that tries to assert the sentence as written fails
the scenario for the wrong reason.

**F5 — §8.0 never says how to activate a state.** *Severity: medium.*
Every scenario opens with "Given `section#sX` is active" and no rule says how to get there. R3 only
governs *addressing*. Add to R3 or as R9:
> *"To activate a state, click its `.wf-tab[data-state="sX"]`. To open a modal outside a per-row
> entry point, click `.wf-tab[data-modal="m-…"]`."*

**F6 — QA-CHROME-02: `p.sub` is not unique.** *Severity: low.*
Six of seven sections contain two `p.sub` nodes (the second is the `"Scan list …"` caption). Change
to ``the **first** `p.sub` reads …`` or `#sX .pagepad > p.sub:first-of-type`.

**F7 — QA-S0-01: "the card heading" names no selector.** *Severity: low.*
It resolves uniquely by exact text today, but that is luck. Give it a selector or say
"the element whose R2 text is exactly …".

**F8 — QA-HIST-03: "the green highlight" has no assertable value.** *Severity: low.*
Give the token (`background: var(--green-soft)`) or the computed colour, or say "differs from every
other row's background".

**F9 — §8.18 rows that point at non-scenarios.** *Severity: low, hygiene.*
E-60 → "QA-COUNT-12 (scale behavior), **DQ-9**", E-74 → "QA-HUB-08, **§6.3**",
E-77 → "QA-SCAN-15, **§3.2**". The table's title claims "every `[E-n]` has an asserting scenario";
three rows lean on a non-scenario pointer. Either accept it explicitly in the table caption or add
the missing scenarios.

**Non-findings (checked, spec is right):** the §8.0 totals (168/68/100/68) and every per-block count
in §8.16 reconcile exactly; R2's `"#6"` / `"Closing Verdict5"` claim is reproduced verbatim by the
page; R4's stub yields `lang === "en-US"` because `speak()` assigns it before `speak(u)`;
R7's claim that `lastState` is readable holds (`page.evaluate(() => lastState)` returns `"s2"`);
R8's eight demo limitations were each asserted as demo behavior and each held (79-not-81, silent
start no-op, no cancel dialog, tiles frozen after deletion, State 4 input enabled, hub wired only in
State 1, `.bs-warn` absent, muted target line in warning states).

---

## 5. Can an AI run this spec's QA unaided?

**Yes, with caveats.**

Evidence for *yes*: a hostile agent with no prior knowledge of the page produced a runnable
68-scenario, 405-assertion suite straight from §8, and **401 of 405 assertions passed on the first
execution**. Every selector, every expected string, every glyph, every inline width, every class
name and every count in §8 matched the live page. R2, R4, R5 and R7 were not merely correct, they
were *necessary* — the run would have failed without them, and each was validated independently
(the raw `"#6"`/`"Closing Verdict5"` check, the `en-US` check, the `lastState` check). Zero
scenarios were UNRUNNABLE and zero were wholly AMBIGUOUS. That is a far better result than a spec of
this size normally yields.

Caveats that keep it from an unqualified *yes*: **(1)** three expected strings are wrong (F1) and
the run cannot come out clean until they are fixed; **(2)** the `reads` / `reads exactly` verb
ambiguity (F2) means two compliant agents can disagree on those same three scenarios — a silent
correctness hazard, not just noise; **(3)** the state-activation step (F5) has to be inferred;
**(4)** four clauses (F4, F6, F7, F8) are not assertable as written and must be either skipped or
improvised. Fix F1–F3 and F5 and this becomes a clean *yes*.

---

## 6. Reproducing

```bash
cd /Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_verify
python3 qa-closing.py          # prints the table, writes qa-closing-results.json
```
The script targets the local `index.html` by relative path; point `URL` at
`https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/closing/` to run against the deployed
copy named in §8.0.
