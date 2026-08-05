# M2 — Adversarial QA Execution · `inbound-request` §8

**Verifier role:** hostile QA robot. I did not write this spec and did not read the wireframe
source before writing the tests.
**Target spec:** `wms2/specs/inbound-request.md` §8 (QA Acceptance Criteria)
**System under test:** `wms2/inbound-request/index.html`
(identical to the deployed page at `https://yongwon-pixel.github.io/skinseoul-wireframes/wms2/inbound-request/`)
**Runner:** `_verify/qa-inbound-request.py` — Playwright, python, headless chromium, viewport 1440×900
**Date:** 2026-08-03

---

## 1. Methodology

1. **Extraction.** Every scenario in §8 carrying a `[WF]` assertion was extracted — 51 `[WF]`-only
   plus the 2 dual-tier scenarios (`QA-A-19`, `QA-A-25`, WF half only) = **53**. This matches the
   spec's own tier-split claim in §8 ("53 scenarios carry a `[WF]` assertion"), so the sample is
   **the whole `[WF]` population**, not a subset — well past the 25-scenario floor, and adversarial
   by construction because nothing was left out to flatter the spec.
2. **Transcription.** Each scenario was coded using **only** the selectors, labels and expected
   strings the spec supplies. Where the spec names `.opt`, the test queries `.opt` — not
   `.auto .opt`. Where it says "reads exactly", the test compares for equality. No knowledge of the
   wireframe's DOM was used to repair a spec instruction.
3. **Execution.** `python3 qa-inbound-request.py`. Every scenario starts from **NX** (fresh load)
   as §8 requires; `N1/N2/N3/NM/NR` are implemented verbatim from the §8.0 navigation preamble.
4. **Self-audit before judging the spec.** The first run produced 15 failures. Seven were **my**
   defects, not the spec's, and were fixed before any culprit was assigned:
   - `#gtoast` is `position:fixed`, so `offsetParent` is always `null` — my visibility helper was
     wrong, which falsely failed `QA-A-18`, `QA-A-19`, `QA-B-04`, `QA-D-04`.
   - `page.goto(url + '#reqlist')` from the same document only fires `hashchange`; it does not
     re-run the page script. `QA-C-01` needed a hard reload (`about:blank` first). The page's
     deep-link handling is correct.
   - `QA-B-02`/`QA-A-01` used `textContent` where the data lives in `input.value` / where the
     paragraph has a child `<b>`.
   These are disclosed rather than silently corrected, because a spec that "passes" only after the
   runner improvises is not a spec an AI can run unaided. After the fix, **zero** remaining
   failures are test-instruction defects.
5. **Classification.** PASS · FAIL (spec says X, page does Y) · AMBIGUOUS (instructions
   insufficient to execute) · UNRUNNABLE (impossible in a static mock and not tagged `[ADMIN]`).
   Every FAIL was then cross-checked against `_plans/_wireframe-fixes.md` to see whether a known
   WF defect makes it a wireframe fault.

---

## 2. Results

| Verdict | Count |
|---|---|
| **PASS** | **45** |
| **FAIL** | **8** |
| **AMBIGUOUS** | **0** |
| **UNRUNNABLE** | **0** |
| **Attempted** | **53** |

**Culprit split for the 8 FAILs: spec 8 · wireframe 0 · test-instruction 0.**
None of the 8 corresponds to any entry in `_wireframe-fixes.md`; in every case the page renders
legitimate, intended content and the spec's assertion is mechanically wrong (unscoped selector,
over-strict "reads exactly", or an unscoped negative). The two known defects that *do* touch this
page (**WF-2** stale "Received Date and Carrier" footer, still present at line 396; **WF-11**
removed-modal HTML comment, still present at line 702) are correctly documented in §2.4 and
correctly kept **out** of the `[WF]` tier — the spec is right on both.

### 2.1 Scenario table

| ID | Verdict | Evidence / quote |
|---|---|---|
| QA-A-01 | PASS | `h2` = `WMS - Inbound Request`, `.sub` = `Inbound Request — New Request`, 2 pagetabs, trailing `<p class="mut">` matches byte-for-byte |
| QA-A-02 | **FAIL** | spec: "**no card is labelled `JIT`**". Page: the Smart Buy `.routecard` contains `Stock replenishment · Coupang JIT sourcing (via PH)`. Scoped to `<b>` title + `.rc-badge` (the two labels the same scenario enumerates) there is no JIT — the assertion is unscoped |
| QA-A-03 | PASS | Wholesale gains `on`, Smart Buy loses it, exactly 1 `.routecard.on` |
| QA-A-04 | PASS | `.etc-in` placeholder `Enter channel name`, `disabled === false`, `document.activeElement` |
| QA-A-05 (neg) | PASS | re-selecting Smart Buy re-disables + blurs `.etc-in`, `Other` loses `on` |
| QA-A-07 | **FAIL** | spec: "the dropdown shows exactly **3** `.opt` rows". Page: `#s1 .opt` matches **4** — `['opt sel','opt','opt','fld opt fld-inv anno']`. The Tracking No wrapper carries `class="fld opt fld-inv"` (`opt` = optional), colliding with the autocomplete's `.opt`. `#s1 .auto .opt` = 3 |
| QA-A-10 (neg) | PASS | 3rd row `prefill`, all 3 catalog inputs `readonly` + computed `pointer-events: none`, values unchanged after typing |
| QA-A-11 | PASS | 3 rows, 1 `prefill`, each row exactly one `.rm[title="Delete row"]` reading `✕` |
| QA-A-13 | **FAIL** | spec: headers read exactly `… 'Unit Cost (KRW) *', 'JIT Price (KRW)' …`. Page: `'Unit Cost (KRW) *10'`, `'JIT Price (KRW)11'` — the annotation `<span class="dot">10/11</span>` lives **inside** the `<th>`. Strip `.dot` → exact match |
| QA-A-17 | PASS (caveat) | Supplier `*` + `— who is shipping the goods` + value `Coupang`; `.fld-inv` label/placeholder exact; date `2026-07-16`. **Caveat:** spec says a *red* `*` but supplies no selector or colour value — the colour half is not executable |
| QA-A-18 | PASS | `#gtoast` visible with `✓ Inbound request registered` + `Inbound No. auto-assigned · added to the Request List · No refresh`; URL unchanged; hidden again by 3000 ms |
| QA-A-19 (neg) | PASS | exactly one `#gtoast` in DOM after a 400 ms double-fire; still visible at t+2.8 s (timer reset), gone by t+3.8 s |
| QA-A-23 | PASS | `.note.purple` contains `auto-matches it to View Orders`, with 0 `<a>`, 0 `<button>`, 0 `[data-modal]` inside |
| QA-A-24 | PASS | `textarea.mtextarea` under `Memo (Optional)`, placeholder exact, value empty |
| QA-A-25 | PASS | `#s1 .pagepad` computed padding `18px 16px 0px`; `#s1 .mock` `min-width: 1280px`; `.submitrow` inside `.formcard` |
| QA-A-26 | **FAIL** | spec: "each Request List Actions button reads `💬 Comments`". Page: `['💬 Comments 1','💬 Comments 2','💬 Comments 3','💬 Comments','💬 Comments','💬 Comments']` — 3 buttons carry an unread-count `<span class="badge-n">` **inside** the button. §8 never mentions this badge anywhere |
| QA-A-28 | **FAIL** | two sub-failures. (a) same `.dot` pollution as QA-A-13. (b) spec: "**no column, field or label named `Size` exists anywhere on the page**"; page has one `Size` — inside legend prose `… locked in via the unified search; no Size`. No `<th>`, `<label>` or field is named Size. (DOM ordering of the 7 form inputs itself: PASS) |
| QA-B-01 | PASS (caveat) | `#s2.on`, only Wholesale `on`, no `Inbound No.` label in `#s2 .formcard`, submit copy present. **Caveat:** spec says the copy "reads exactly" X but `#s2 .submitrow` textContent is `Register Inbound Request On registration, … Request List1` — it also holds the button label *and* legend dot `1`; equality is impossible, executed as containment |
| QA-B-02 | PASS | row 2 = `Round Lab` / `1025 Dokdo Cleanser, 150ml`, Qty `300`, Unit Cost `0`, JIT empty; `0 entered directly in Unit Cost (0 allowed)` present; no FOC control. The scenario's own "Precision note" is the reason this passed cleanly |
| QA-B-03 | PASS | `비엠유통` verbatim, `10325661220417`, placeholder without the `(add later)` suffix, `2026-07-18`, memo + `.note.purple` exact |
| QA-B-04 | PASS | toast text byte-identical to State 1 — registration feedback is route-invariant |
| QA-B-06 (neg) | PASS | `REQUESTED → PARTIAL → INBOUNDED` and `SHIPPED retired 2026-07-27 · PARTIAL added 2026-08-02` present; no chip/badge/tag/option reads `SHIPPED`. (Executed with control-scoping; a literal document-text search would false-fail — see fix S-4) |
| QA-C-01 | PASS | both `#reqlist` and `#s3` activate `#s3` and the top-bar tab on first paint |
| QA-C-02 | PASS | 4 chips `All 12 / REQUESTED 8 / PARTIAL 1 / INBOUNDED 3`, `All` on, 8+1+3=12, no SHIPPED chip |
| QA-C-03 | PASS | `PARTIAL 1` gains `on`, `All 12` loses it, exactly 1 chip `on` |
| QA-C-05 | PASS | `Bulk add tracking numbers` + the full count string; no "Mark as shipped" |
| QA-C-07 | PASS | 6 route `.tag` spans: `background-color: rgba(0, 0, 0, 0)`, `color: rgb(20, 16, 27)`, `font-weight: 800` |
| QA-C-08 | PASS | `202607120004` shows both numbers + `2 tracking numbers — all matching active`; `…130003`/`…130002` show `Add tracking`; `…120001` shows `10324880021991` and no button |
| QA-C-09 | PASS | `PARTIAL 120/180`; Qty `180 ✎ 300→180 (damaged)`; `title="Expected qty edit history"`; short token, not the enum |
| QA-C-10 | PASS | both INBOUNDED, `07-11 14:22` / `07-09 10:05`, `Switched by View Orders scan inbound`, zero View-Orders links |
| QA-C-11 (neg) | **FAIL** | spec: 12 `th` reading `… 'Sourcing Route','Tracking No','Received Date','Status' …`. Page: `'Sourcing Route3'`, `'Tracking No4'`, `'Received Date10'`, `'Status5'` — legend dots inside the `<th>`. Count (12), order and "no Carrier column" all hold once `.dot` is stripped |
| QA-C-12 (neg) | PASS | no `Add tracking` on either INBOUNDED row |
| QA-C-13 | PASS | `.note.purple` holds all three substrings incl. `#wholesale-ops` / `#partnership-kr` |
| QA-C-14 | PASS | an element (`p.mut`) reads exactly `Showing 6 of 12 request(s) · Status: REQUESTED 8 · PARTIAL 1 · INBOUNDED 3`; exactly 6 data rows |
| QA-C-15 | PASS | `＋ New Inbound Request` activates `#s1` with the `New Request` pagetab `on` |
| QA-C-16 | PASS | `COSRX` in `<b>` + `… +2 more`, SKU `100040311 +2`; `Beauty of Joseon` + `Relief Sun, 50ml +1 more`, SKU `100031820 +1` |
| QA-C-19 | PASS | nav items present in the stated order, `💬 Comments` button, `Yongwon Ryu`, `Logout` |
| QA-C-24 | PASS | static `#s3 .toast` (id ≠ `gtoast`) reads `✓ Inbound request registered — 202607130003` + `No refresh · added to top of the list`, still visible after 3.2 s |
| QA-D-01 | **FAIL** | spec: `header` "reads exactly `Add Tracking No — 202607130003`". Page: `Add Tracking No — 202607130003✕` — the `<header>` also contains `<button class="x" data-close>✕</button>`. Body substrings both PASS |
| QA-D-02 | PASS | the row-level `Add tracking` opens the same `#m-invoice` |
| QA-D-03 | PASS (caveat) | 1 → 3 `.qrow` after two `#tnAdd`, newest input focused, each row has input + `.tn-del ✕`; two removals → 1 row; final `✕` clears instead of removing. **Caveat:** the spec asserts the last input's "value cleared" but never instructs the runner to *put* a value in it — the assertion is vacuous as written; a marker value was typed to make it real |
| QA-D-04 | PASS | modal closes, `✓ Tracking number(s) saved` + `Every registered number is now matched to View Orders · No refresh` |
| QA-D-05 | PASS | Cancel, header `✕` and backdrop each close the modal with no toast |
| QA-D-06 | PASS | both placeholders exact, `status stays REQUESTED` present, every `.tn-del` carries `title="Remove this tracking number"` |
| QA-D-17 | PASS | backdrop dismissal behaves exactly like Cancel |
| QA-F-01 | PASS | `#inbox1` opens, `@ Mentions` (badge 2) `on` + `★ Saved` |
| QA-F-02 | **FAIL** | spec: "the pane lists exactly **two** `.it` entries". Page: `.it` matches **3** — the `[data-pane="saved"]` pane is `display:none` but still in the DOM and holds a third `.it`. Scoped: mentions 2, saved 1. Every text/`unread`/entity-label assertion inside the scenario PASSes |
| QA-F-03 | PASS | `★` toggles `on`; Saved pane header `Comments I saved` + `Unstar to remove from list` |
| QA-F-04 | PASS | `tr.cpanel-ir` inserted as the immediate next sibling, `colspan="12"`, both comments + times, `@Dean` in `.at`, write-box placeholder exact, `Post` button |
| QA-F-05 | PASS | second click removes the panel (toggle) |
| QA-F-06 | PASS | `No comments yet` + the write box |
| QA-G-10 (neg) | PASS | across N1→N2→N3→NM: no Print control, no scan placeholder, no `autofocus`, no `AudioContext`/`speechSynthesis`/`new Audio`, no media element, no print binding |
| QA-G-16 (neg) | PASS | only `data-modal` is `m-invoice`; no `Inbound No.` label/input in any `.formcard`; no FOC checkbox; no `SHIPPED` chip/badge/option; no `Size`/`Carrier` cell; exactly one Register button per state; no `Add tracking` on either INBOUNDED row |

### 2.2 Failure pattern

The 8 failures are **three defect classes, not eight independent bugs**:

| Class | Scenarios | Root cause |
|---|---|---|
| **Annotation-dot pollution of exact-text assertions** | A-13, A-28(a), C-11 — plus latent in B-01 | The wireframe has 29 `.anno` blocks; 6 `<th>`/`<label>` elements carry an inline `<span class="dot">N</span>`. Any `textContent === "…"` check on those elements fails. §8 never tells the runner to strip `.dot`, and never mentions the `#annoToggle` "Hide annotations" control (which §2.2 does describe, but §8 does not reference) |
| **Selector not unique / not scoped** | A-07, F-02 | `.opt` also means "optional field wrapper" (`fld opt fld-inv`); `.it` also lives in the hidden Saved pane. §8's own contract — "with the exact selector … given" — is not met |
| **Unscoped negative assertion hitting legitimate prose** | A-02, A-28(b) | "no card labelled `JIT`", "no `Size` **anywhere on the page**". The spec demonstrably knows this trap — QA-B-02 carries an explicit Precision note about `free of charge` — but applied the note exactly once. `SHIPPED` (B-06/G-16, 3 prose occurrences) is the same trap and survived only because I scoped to controls |
| **Undeclared UI element inside an asserted label** | A-26, D-01 | `<span class="badge-n">` inside the Actions buttons; `<button class="x">✕</button>` inside the modal `<header>` |

---

## 3. Spec fixes required

Ordered by damage. Every item is a **spec** edit; no wireframe change is implied by any of them.

**S-1 · Add a global text-normalisation rule to §8, before Block A.**
Something with teeth, e.g.: *"All exact-string assertions are evaluated against the element's
textContent with every `.dot` descendant removed (the wireframe's annotation numbers are demo
chrome, not copy). Equivalently, click `#annoToggle` before running the text assertions."*
Fixes A-13, A-28(a), C-11 and de-risks every other "reads exactly" clause in §8.

**S-2 · Fix the two colliding selectors.**
- QA-A-07: `.opt` → **`#s1 .auto .opt`**. As written, `#s1 .opt` matches 4 because the Tracking No
  wrapper is `class="fld opt fld-inv"`.
- QA-F-02: `.it` → **`#inbox1 [data-pane="mentions"] .it`**. As written it matches 3, because the
  `[data-pane="saved"]` pane is `display:none` but present.

**S-3 · Re-scope the three unscoped negatives, using QA-B-02's Precision note as the template.**
- QA-A-02: "no card is labelled `JIT`" → *"no `.routecard` `<b>` title and no `.rc-badge` reads
  `JIT`. Precision note: the word JIT legitimately appears in the Smart Buy card's `<small>`
  sub-copy (`Coupang JIT sourcing (via PH)`) — a full-text search will false-fail."*
- QA-A-28: "no column, field or label named `Size` anywhere on the page" → adopt QA-G-16's already
  correct form (*"no `<th>` or cell labelled `Size`"*) and add the note that the legend prose
  `… no Size` is the intended negative declaration.
- QA-B-06 / QA-G-16: same treatment for `SHIPPED` — 3 prose occurrences exist by design; state
  explicitly that the assertion is about controls (`.chip`, `.tag`, `.pill`, `option`, `button`).

**S-4 · Declare the two elements that live inside asserted labels.**
- QA-A-26: the Request List Actions buttons carry an unread-count `<span class="badge-n">`, so 3 of
  6 read `💬 Comments 1|2|3`. Restate as *"every Actions button's label begins with `💬 Comments`;
  an optional trailing `.badge-n` unread count is expected on rows 1–3"*. Nothing anywhere in §8
  currently mentions this badge.
- QA-D-01: the modal `<header>` contains the close `<button class="x">✕</button>`. Restate as
  *"the header's text, excluding the `.x` close control, reads exactly …"*.

**S-5 · QA-B-01: drop "reads exactly" for the submit-row copy.**
`#s2 .submitrow` textContent is `Register Inbound Request On registration, … Request List1` — it
contains the button label and a legend dot. Either scope the assertion to the copy element itself
or change the verb to "contains".

**S-6 · QA-D-03: make the "value cleared" assertion non-vacuous.**
The scenario asserts the surviving row's input value is cleared but never instructs the runner to
enter a value first, so the check passes trivially against an already-empty input. Add: *"type
`TEST123` into the surviving row's input before clicking its `✕`."*

**S-7 · QA-A-17: the "red `*`" is not executable as written.**
Either give the assertion a mechanism (*"the `*` span's computed `color` is `rgb(…)`"* / *"carries
`style` colour `var(--red)`"*) or drop "red" and assert only that the Supplier label contains `*`.

---

## 4. Verdict on the owner's goal

**Can an AI run this spec's QA unaided? — yes, with caveats.**

Nothing in the 53-scenario `[WF]` set forced a question: the navigation preamble, the wireframe
reality baseline and the tier split are all sufficient to code and execute the whole set in one
pass, and **0 scenarios came out AMBIGUOUS or UNRUNNABLE**. That is a genuinely strong result —
this spec is far closer to executable than a normal acceptance-criteria document.

The caveat is that a literal runner files **8 spurious defects (15 %)**, and all 8 are avoidable
with the ~7 edits above. The failure mode is not missing information; it is that §8 asserts against
*rendered text* while the target page interleaves demo annotation chrome and secondary controls
into that same text, and hands over two selectors that are not unique. An owner reading that QA
report would spend the review triaging false positives — which is the exact cost the "zero
questions" goal is meant to eliminate. Apply S-1 through S-4 and the `[WF]` set should run clean.

---

## 5. Artefacts

- Runner (re-runnable): `wms2/specs/_verify/qa-inbound-request.py`
- This report: `wms2/specs/_verify/m2-inbound-request.md`
- Command: `python3 qa-inbound-request.py --json results.json`
