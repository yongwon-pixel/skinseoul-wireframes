# M2 — Adversarial QA Execution: `ready-to-outbound.md` §8

Hostile-QA verification (executor did not author the spec). Date: 2026-08-03.

- **Spec under test:** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/ready-to-outbound.md` §8 (1,813 lines total; §8 = lines 942–1668)
- **System under test:** `file:///Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/ready-to-outbound/index.html` (486 lines, identical to the deployed page)
- **Harness:** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_verify/qa-ready-to-outbound.py` (Playwright 1.58.0, headless Chromium, viewport 1440×900)
- **Cross-reference for culprit assignment:** `/Users/yongwon/yongwon-sync/claude/repos/skinseoul-wireframes/wms2/specs/_plans/_wireframe-fixes.md`

**The question being answered:** can an AI run this spec's QA with zero questions? Answered empirically, not by reading.

---

## 1. Methodology

1. **Extraction.** All `[WF]`-tagged scenarios were pulled out of §8 mechanically. The spec's own §8.0 count table was verified as a side-check rather than trusted:

   | Metric | §8.0 claims | Measured | Verdict |
   |---|---|---|---|
   | Total scenarios | 201 | **201** | matches |
   | `[WF]` | 93 | **93** | matches |
   | `[ADMIN]` | 108 | **108** | matches |
   | Untagged / duplicate IDs | 0 | **0 / 0** | matches |
   | `· negative` | 97 | **99** | off by 2 (see fix S-5) |

2. **Sampling.** **73 of the 93 `[WF]` scenarios (78 %) were executed** — well past the 25 required. Selection was adversarial, not random: every scenario asserting an exact string, a sound path, a toast, a modal chain, a cross-state flow, or a "never / no / absent" negative was taken first. All 34 header-tagged `[WF]` negatives in scope were attempted. The 20 unrun ones are the residue of pure structural assertions in blocks already sampled 3–4 deep (e.g. QA-M1-02 column set, QA-L12-01/03/04, QA-L14-02/03/04/06, QA-F-02/03).

3. **Execution discipline.** Each scenario runs on a **fresh page load** (§8.0 precondition) and uses **only** the selectors, labels and expected strings the spec itself supplies. §8.0's three reading rules (`#pfill` inline width, `#pbarLabel.childNodes[0]`, M1 header first text node) were followed literally. Where the spec named no selector or no assertion mechanism, the scenario was recorded **AMBIGUOUS** and abandoned — no improvisation from independent knowledge of the page.

4. **Adversarial reading of negatives.** Where a negative is phrased absolutely ("never", "no occurrence of", "must not appear anywhere"), it was executed absolutely — continuous sampling, whole-document scans — not charitably.

5. **Culprit assignment for FAILs.** A FAIL is a *wireframe* fault only if `_wireframe-fixes.md` already registers it (WF-1…WF-14) or §8.0's "Known wireframe artifacts" list covers it. Otherwise the spec asserted something the page does not do, and the spec is the culprit.

**Reproduce:** `python3 wms2/specs/_verify/qa-ready-to-outbound.py` (optionally pass scenario IDs to run a subset).

---

## 2. Results

**73 attempted · 69 PASS · 2 FAIL · 2 AMBIGUOUS · 0 UNRUNNABLE.**

Zero UNRUNNABLE is itself a finding: every `[WF]` scenario sampled really is executable against a static mock today, exactly as §8.0 promises. The tier split is honest.

### 2.1 FAIL

| ID | Verdict | Evidence |
|---|---|---|
| **QA-L7-02** | **FAIL** | Spec: "`document.body.textContent` contains **no** occurrence of `JIT (channel) completed` — **not in the table, not in the legend**, not in the modal". Page: `document.body.textContent.includes('JIT (channel) completed') === true`. The string is in **legend item 7**: `…yellow row tint + "Fully Inbounded" badge (wording changed from "JIT (channel) completed" on 2026-08-03 to avoid confusion with the colorless Sourcing Route labels)…` (`index.html:336`). |
| **QA-L5-04** | **FAIL** | Spec: "a `Bulk Outbound` run **never** renders `No refresh · selection kept`, and neither print run **ever** renders `refreshes after completion`". Page, sampling `#pbarLabel.childNodes[0].textContent` every 40 ms across a full run: **7 of 38 in-flight samples** of a Bulk Outbound run read `'Bulk Print Labels in progress — 3/5 (60%) · No refresh · selection kept · toast on completion'`, and **6 of 38** samples of the following Bulk Print Labels run read `'Bulk Outbound in progress — 100% · refreshes after completion · toast on completion'`. Both mode strings cross over, in both directions. |

### 2.2 AMBIGUOUS

| ID | Why the instructions are insufficient |
|---|---|
| **QA-L6-04** | Clause 2 ("no completion string containing `failed`, `error`, or `partial`") is executable and **holds** — all six toast strings across the three actions are clean. Clause 1 — "the document contains no red/failure styling variant of `#toast` **bound to batch completion**" — names no selector, no class, no property, and never defines "variant" or "bound to". There is no mechanical procedure to run. |
| **QA-F-06** | "no element in the document has textContent `View Order`". Under **equality** it PASSES (0 elements equal it; the Print column holds only `.printbtn`). Under **containment** it FAILS — `document.body.textContent` contains `View Order` in the legend footer prose ("View Order button removed"). The spec uses both readings elsewhere without distinguishing them: QA-L7-02 says "contains no occurrence of", QA-F-01 says "must not appear in either element", QA-L3-04 says "contains no `Outbound` substring". Verdict flips on which convention applies, so the scenario is not runnable unaided. |

### 2.3 PASS (69)

All strings, counts and computed values below were read off the live page, not off the spec.

| ID | Verdict | Evidence |
|---|---|---|
| QA-L1-01 | PASS | 5 rows; checked = `{422221:T, 422176:T, 422165:T, MKT-40233:F, 422164:F}`; `.cnt` = `3 selected` |
| QA-L1-02 | PASS | `['🖨 Print Pick Locations (3 orders · 8 items)', '🖨 Bulk Print Labels (3 orders)', '📦 Bulk Outbound (3 orders)']` |
| QA-L1-04 | PASS | after clicking both select-alls: row checkboxes `[T,T,T,F,F]` unchanged, `.cnt` still `3 selected`, labels unchanged — `[RTO-WFX-1]` confirmed |
| QA-L2-02 | PASS | after opening M1 + 2 s: `#pfill.style.width === ''`, label unchanged, `#toast` `display:none` |
| QA-L2-03 | PASS | both `wf-bar` buttons open `#m-pick` — `[RTO-WFX-2]` confirmed |
| QA-M1-01 | PASS | header first text node = `Print Pick Locations — Picking List (3 orders selected · 4 SKUs · 8 units total)`; badges `[5,1,2]` sum 8; `[L-2]` label carries `8 items` |
| QA-M1-03 | PASS | 4 rows, `['A-02-13','A-03-02','B-01-07','B-02-11']` strictly ascending |
| QA-M1-04 | PASS | `['100039958','100039420','100035912','100013286']`, each present among the grid `.skupill` set |
| QA-M1-05 | PASS | row1 qty `5` inside `<b>`, Order `422221`; rows 2–4 qty `1` not bold; Korean names byte-exact |
| QA-M1-06 | PASS | `['422221','422165','422176','422165']` — ordered by location, not grouped by order |
| QA-M1-07 | PASS | `422165` appears as two separate rows (`A-03-02`, `B-02-11`); no Order cell holds >1 order |
| QA-M1-08 | PASS | SKU `100012534` absent; no Location cell reads `Not inbounded` |
| QA-M1-09 | PASS | M1 row2 = `마데카 크림 타이트닝` (no brand); grid row `422165` has `<b>Centellian24</b>`; M1 row1 = `AtoBarrier365 Body …` — `[RTO-WFX-5]` confirmed |
| QA-M1-10 | PASS | `.note` textContent byte-identical to the spec's quoted sentence |
| QA-M1-11 | PASS *(caveat)* | modal closes; `#pfill` → `100%`; running label `Print Pick Locations in progress — 20% · No refresh · selection kept · toast on completion`; `#toast b` = `✓ Print Pick Locations complete — 3 orders`; 5 rows, 3 still checked. **Caveat:** 2 samples in the first ~250 ms still showed the previous action's copy (see fix S-2) |
| QA-M1-12 | PASS | Cancel / backdrop `(4,4)` / `✕` each remove `open`; afterwards `#pfill.style.width === ''` and `#toast` hidden |
| QA-L3-01 | PASS | `Bulk Print Labels in progress — 20% · No refresh · selection kept · toast on completion` |
| QA-L3-02 | PASS | `✓ Bulk Print Labels complete — 3 orders` / `Disappears automatically after a few seconds` |
| QA-L3-03 | PASS | `window.__sentinel` survives (no reload); `sndOutbound.ac` still `undefined`; 3 checkboxes still checked |
| QA-L3-04 | PASS | label `🖨 Bulk Print Labels (3 orders)` contains no `Outbound` substring |
| QA-L4-01 | PASS | no uncaught exception; `sndOutbound.ac` is an `AudioContext` (constructible in this env) |
| QA-L4-02 | PASS | `Bulk Outbound in progress — 20% · refreshes after completion · toast on completion` |
| QA-L4-03 | PASS | `display:flex`, computed `top:54px right:16px`; `✓ Bulk Outbound complete — 3 orders`; toast up at t+1.25 s, auto-hid 2.99 s later |
| QA-L4-04 | PASS | applying the binding predicate to **every** `button` yields exactly one: `📦 Bulk Outbound (3 orders)` |
| QA-L4-05 | PASS | 0 buttons whose text contains `Ready to be Outbonded` |
| QA-L5-01 | PASS | exactly 1 `.pbar`, 1 `#pfill`; all three actions drive it to `100%` |
| QA-L5-02 | PASS | 100 ms samples `0,0,20,20,20,40,40,60,60,60,80,80,100,…` — starts at 0 %, monotonic, ends 100 % |
| QA-L5-05 | PASS | idle label byte-exact; `3/5` absent from every running-state label |
| QA-L6-01 | PASS | both actions: `display:flex`, `top:54px right:16px`, auto-dismiss ~3.00 s |
| QA-L6-02 | PASS | `['✓ Print Pick Locations complete — 3 orders','✓ Bulk Print Labels complete — 3 orders','✓ Bulk Outbound complete — 3 orders']` |
| QA-L6-03 | PASS | continuous sampling: max simultaneously-visible `.toast` = 1; final text is the most recent action's |
| QA-L6-05 | PASS | `#toast small` = `Disappears automatically after a few seconds` after every batch |
| QA-L7-01 | PASS | `.jit-badge` = `Fully Inbounded` |
| QA-L7-03 | PASS | `row-jit` present; document order `[…, MKT-40233, 422164]` |
| QA-L8-03 | PASS | 2 `.locpill` = `A-01-04` / `Not inbounded`; computed `bg #FFF3E0` = `--amber-soft`, `border #FDBA74` = `--amber-line`, `color #B45309` = `--amber` |
| QA-L8-04 | PASS | `['422221','422176','422165','MKT-40233','422164']` |
| QA-L9-02 | PASS | `Egita` / `.at` `@Yongwon` / `Please double-check the ×5 quantity.` (trailing period present) / `07-21 09:40` |
| QA-L9-03 | PASS | both placeholders byte-exact, long form in `#crow1`, short form in `#crow2` |
| QA-L9-05 | PASS | badge `1` on `422221` and `422165`; `null` on `422176`, `MKT-40233`, `422164` |
| QA-L9-06 | PASS | `#crow4` sits under `422164`, `#crow5` under `MKT-40233`; clicking `[data-open="crow5"]` opens under the MKT row — `[RTO-WFX-8]` confirmed |
| QA-L10-02 | PASS | 2 `.it.unread`, texts and `10:12`/`09:40` byte-exact; header + `Mark all read` present |
| QA-L10-04 | PASS | star gains `on`, then loses it; `#toast` stays `none` throughout |
| QA-L10-05 | PASS | `.tabs` `display:none`; header `4 results · newest first · click to open the order`; order `422165, 422221, 422176, 422108`; ≥1 `<mark>` per row |
| QA-L10-06 | PASS | 1 result, `Order 421990 · Aldo: "Box damaged — repacked and shipped"`; `421990` is not a table row |
| QA-L10-07 | PASS | `0 results · newest first · click to open the order` + `No matching comments` |
| QA-L10-08 | PASS | after clearing: `.tabs` `flex`, saved pane `block`, mentions pane `none` |
| QA-L10-09 | PASS | open after inside click; closed after background click |
| QA-L10-10 | PASS | 5 results, includes `422108` and `421990` |
| QA-L11-01 | PASS | `getComputedStyle('.pagepad').padding === '16px 14px 0px'` |
| QA-L11-02 | PASS | `.mockwrap overflow-x: auto`, `.mock min-width: 1240px` |
| QA-L12-02 | PASS | 2 `.item-line` / 2 `.locline`; `A-03-02` pairs with `마데카 크림 타이트닝`, `B-02-11` second |
| QA-L13-01 | PASS | `422221:5`, `422176:1`, `422165:2` |
| QA-L13-03 | PASS | 9 `th`; **0** elements carry class `cb-ready` — `[RTO-WFX-4]` confirmed |
| QA-L14-01 | PASS | `all` tab `on`; `['All (5)','Inventory (3)','Marketing (1)','JIT (1)']` |
| QA-L14-05 | PASS | `#crow1` `table-row` → JIT `none` → All **still** `none`; 5 rows visible; `Found 5 order(s) with items ready for outbound` |
| QA-L14-07 | PASS | `Found 1 order(s) with items ready for outbound` on Marketing |
| QA-F-01 | PASS | `WMS - Ready to be Outbonded` / `Ready to be Outbonded Orders`; `Outbounded` in neither |
| QA-F-04 | PASS | `How to use:` + 5 `li`, all five strings byte-exact |
| QA-F-05 | PASS | 9 `th`; first has the checkbox and empty text; remaining eight start with the 8 expected labels; 5 rows, 5 `.printbtn` |
| QA-F-07 | PASS | all five third cells = `2026. 7. 21.` |
| QA-F-08 | PASS | 14 `li`, `.n` order `1 2 3 4 5 6 7 8 14 13 12 9 10 11`; 15 `.dot` = 14 in `.mock` + 1 in `#m-pick` |
| QA-F-09 | PASS | `no-anno` added, all `.dot` and `.legend` compute `display:none`, button → `Show annotations`; second click restores |
| QA-F-11 | PASS | 5 `.oid`, all `SPAN`, no `href`, no ancestor `<a>` — `[RTO-WFX-3]` confirmed |
| QA-E-01 | PASS | after `.remove()` + Marketing click: no exception, 0 visible order rows, `Found 0 order(s) with items ready for outbound` |
| QA-E-02 | PASS | with both AudioContext constructors stubbed to throw: no uncaught error, `#pfill` `100%`, `✓ Bulk Outbound complete — 3 orders` |
| QA-E-03 | PASS | `.item-line white-space: nowrap`; `.qtypill` is the last element of every line on every row |
| QA-E-04 | PASS | at 800 px viewport: `overflow-x:auto`, `min-width:1240px`, `scrollWidth > clientWidth`, `th` still 9 |
| QA-E-05 | PASS | keyboard Enter on the focused button → exactly 1 progress run (1 reset to `0%`) and exactly 1 toast show-transition |
| QA-E-06 | PASS | `422165` renders 2 `.item-line` / 2 `.locline` / 2 M1 rows — no merging |

---

## 3. Culprit analysis for the FAILs

Neither FAIL is registered in `_wireframe-fixes.md`. WF-1…WF-14 touch view-orders, inbound-request, closing, tracking-missing, stock-status and (WF-9) the ready-to-outbound picking-list sample rows — **nothing about legend 7's changelog text and nothing about the progress label**. Neither is covered by §8.0's "Known wireframe artifacts QA must not file as bugs" list. Both are therefore **(a) spec wrong**.

### QA-L7-02 — culprit (a) spec wrong

The rule itself is fine and stated four times ([BR-4] line 590, §3 line 328, §4.2 removed-items row line 654, decision log line 1783). What is wrong is the **scope** QA-L7-02 gives it. `[BR-4]` is a product rule about the badge on the shipping surface; the spec's own QA-F-09 establishes that annotations and the legend are **wireframe chrome that "ship in no admin build."** Asserting a product string rule over non-shipping chrome contradicts the spec's own model of what the legend is — and it is self-defeating, because a dated changelog entry cannot record a rename without naming the superseded string. Legend 8 uses the same "changed from X" convention.

This is also the highest-yield finding for a spec-quality standpoint: **it is the one scenario in the sample where an AI running the QA unaided would file a bug against a correct wireframe.**

### QA-L5-04 — culprit (a) spec wrong

The demo script sets `fill.style.width='0%'` **synchronously** on click but only rewrites `#pbarLabel` inside the 250 ms `setInterval` callback (`index.html:404–411`). So for the first ~250 ms of every run the label still carries the *previous* action's copy — including its mode string. §8.0 is otherwise extremely careful about how to read these two elements (a whole paragraph each for `#pfill` and `#pbarLabel`) but stops one step short of bounding *when* a running-state assertion becomes valid. Consequences:

- QA-L5-04's absolute "never / ever" is **unsatisfiable as written** → hard FAIL.
- QA-M1-11, QA-L3-01, QA-L4-02, QA-L5-03 all say "during the run …" and are **flaky**: they pass or fail purely on when the executor happens to sample. They passed here only because the harness deliberately discarded the pre-first-tick samples — a charitable choice the spec never authorises.

A one-line wireframe change (write the label once before starting the interval) would also fix it, and is arguably the better repair — but it is not a *registered* wireframe defect, so per the adjudication rule the spec carries it today. It should be added to `_wireframe-fixes.md` as **WF-15** in the next wireframe-edit pass.

---

## 4. Spec fixes required

### S-1 `[MAJOR]` QA-L7-02 asserts `[BR-4]` over wireframe chrome and will produce a false bug report

**Location:** §8.8 QA-L7-02 (spec lines 1296–1297), and the §4.2 removed-items row (line 654) that scopes the rule to "Anywhere".

**Fix:** scope the assertion to the shipping surface and exempt the annotation layer. Suggested replacement:

> **QA-L7-02 `[WF]` · negative — The old wording is absent from every shipping surface**
> - **Then** `document.querySelector('.mock').textContent` and `document.querySelector('#m-pick').textContent` contain **no** occurrence of `JIT (channel) completed` — not in the table, not in the modal, not in any row badge [BR-4] §4.2. The `.legend` is exempt: it is wireframe chrome that ships in no admin build (QA-F-09), and legend item 7 deliberately records the 2026-08-03 rename by quoting the superseded string.

Also amend the §4.2 row's scope cell from `Anywhere` to `Anywhere on the shipping surface (the legend's dated changelog entry is exempt)`, and add legend 7's changelog quote to §8.0's "Known wireframe artifacts QA must not file as bugs" list.

### S-2 `[MAJOR]` §8.0 does not bound "during the run", making 5 progress-label scenarios flaky and 1 unsatisfiable

**Location:** §8.0 (the `#pbarLabel` reading paragraph, spec line 959) and QA-L5-04 (spec lines 1241–1242); knock-on: QA-M1-11, QA-L3-01, QA-L4-02, QA-L5-03.

**Evidence:** `index.html:404–411` — `fill.style.width='0%'` runs synchronously on click, the `label.childNodes[0].textContent=…` assignment runs only inside the 250 ms interval. Measured: 7/38 and 6/38 in-flight samples carry the wrong action's mode string.

**Fix (both parts):**

1. Add a third reading rule to §8.0, alongside the two that already exist:
   > **Reading a running-state label correctly.** The demo script sets `#pfill`'s inline width synchronously on click but rewrites `#pbarLabel` only on the first `setInterval` tick (250 ms). For the opening ~250 ms of a run the label still shows the **previous** action's copy — on a fresh load, the idle demo copy. **Every "during the run" assertion is valid only from the first tick onward.** Sample after `#pfill.style.width` has reached `20%` or later, never before. This is a wireframe demo artifact, not a defect to file.
2. Rewrite QA-L5-04's absolute wording so it is satisfiable:
   > **Then** from the first progress tick onward (`#pfill.style.width` ≥ `20%`), a `Bulk Outbound` run never renders `No refresh · selection kept` and neither print run ever renders `refreshes after completion` [BR-8].

Additionally register the underlying wireframe issue as **WF-15** in `_plans/_wireframe-fixes.md` §B (fix: write the label once before `setInterval` starts, mirroring the existing `fill.style.width='0%'` line), so the artifact can be removed rather than documented forever.

### S-3 `[MAJOR]` QA-L6-04's first clause has no executable procedure

**Location:** §8.7 QA-L6-04 (spec lines 1271–1272).

**Fix:** replace the unrunnable half with a concrete document-level assertion. Suggested:

> - **Then** `document.querySelectorAll('.toast').length === 1` and its computed `background-color` equals `--green` (`#198754`); **no** CSS rule and **no** class in the document styles `.toast` or `#toast` with `--red` / `--red-soft`; and after each of the three actions neither `#toast b` nor `#toast small` contains `failed`, `error`, or `partial` [BR-9] §4.2.

### S-4 `[MINOR]` The spec mixes "textContent equals" and "textContent contains" without saying which applies

**Location:** QA-F-06 (spec line 1542, "has textContent `View Order`") against QA-L7-02 (spec line 1297, "contains no occurrence of"), QA-F-01 (spec line 1526, "must not appear in either element") and QA-L3-04 (spec line 1146, "contains no `Outbound` substring").

QA-F-06's verdict flips between PASS and FAIL depending on the reading, because the legend footer prose contains "View Order button removed."

**Fix:** state the convention once in §8.0 — e.g. *"`has textContent X` means strict equality on that element; `contains no occurrence of X` means a substring scan of the named subtree"* — and rewrite QA-F-06 explicitly:

> **Then** `[...document.querySelectorAll('*')].filter(e => e.textContent === 'View Order').length === 0`, and every element in each row's Print cell carries class `printbtn` [BR-12] §4.2. (The legend footer's prose "View Order button removed" is chrome and is not in scope.)

### S-5 `[MINOR]` §8.0's negative-scenario count is off by 2, and three per-block rows disagree with the text

**Measured against the §8.0 table** (a scenario counts as negative if `· negative` appears anywhere in its body, header-tag or inline `**· negative:**` clause):

| Block | Table says | Measured | Delta |
|---|---|---|---|
| QA-M1 | 6 | **7** | +1 (QA-M1-13 carries an inline `**· negative:**`) |
| QA-F | 5 | **7** | +2 (QA-F-12, QA-F-13 inline) |
| QA-DC | 6 | **5** | −1 |
| **Total** | **97** | **99** | **+2** |

Total, `[WF]`/`[ADMIN]` split, ID uniqueness and numbering are all exactly right — only the negative tally drifts. The ≥25 % requirement is met either way (99/201 = 49.3 %).

**Fix:** state in §8.0 whether an inline `**· negative:**` clause makes the whole scenario a negative, then recompute the three rows and the total.

### S-6 `[MINOR]` QA-L4-03 / QA-L6-01 do not say what the auto-dismiss window is measured from

**Location:** QA-L4-03 (spec line 1181, "the toast hides within ~4 s") and QA-L6-01 (spec line 1262, "returns to `display:none` within ~3–4 s").

Measured: the toast appears **1.25 s after the click** and hides **3.00 s after appearing** — i.e. 4.25 s after the click. Anchored to the click, "~4 s" fails; anchored to the toast appearing, it passes. The first harness run FAILed this scenario on exactly that ambiguity.

**Fix:** anchor it — *"`#toast` returns to `display:none` within 3–4 s **of becoming visible** (not of the click that started the batch)."*

---

## 5. Answer to the question

**Can an AI run this spec's QA unaided? — yes, with caveats.**

The evidence for "yes": 69 of 73 adversarially-chosen scenarios passed on the first literal execution, including every exact-string assertion, every Korean product name, every toast string, the sound-binding predicate over all 40+ buttons, the full comments-hub search corpus, the modal close-chain, and the computed-colour and computed-padding assertions. Zero scenarios were UNRUNNABLE. §8.0's reading rules for `#pfill`, `#pbarLabel` and the M1 header are genuinely necessary and genuinely sufficient — without them at least four scenarios would have been mis-executed. The count table's structural claims (201 / 93 / 108, no duplicates, no gaps) all check out. This is a spec that was written against the real artifact, not from memory.

The caveats, in order of damage:

1. **One scenario (QA-L7-02) will make an unaided AI file a bug against a correct wireframe** — the worst possible failure mode for a machine-runnable spec, because it converts a passing system into a false defect report.
2. **Six scenarios in the progress-label family are timing-flaky and one is unsatisfiable** because §8.0 never bounds "during the run." An unaided AI sampling at 100 ms rather than 400 ms gets a different verdict on the same code. Non-determinism is worse than a wrong assertion — it destroys trust in the whole run.
3. **Two scenarios cannot be executed at all without a judgement call** (QA-L6-04's undefined "styling variant", QA-F-06's equality-vs-containment). Both are answerable in one sentence each.

All six fixes are local and mechanical; none requires re-deriving behavior or asking the owner anything. With S-1 through S-4 applied, this section reaches genuine zero-question runnability.
