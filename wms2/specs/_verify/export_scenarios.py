#!/usr/bin/env python3
"""Extract every QA scenario in the spec set into structured form.

The scenarios live in §8 of the eight screen specs in two shapes:

  table   | **QA-E-01** | `[E-5]` | `[WF]` · negative | **Given** … **When** … **Then** … |
  prose   **QA-IMP-01 [WF]** — Open the import modal from the filter bar
          Given …
          When …
          Then …

Both are parsed here so a QA engineer never retypes a scenario by hand.

Output (written next to this file):
  scenarios.json   list of objects
  scenarios.csv    same, one row per scenario

Fields: id · page · tier · negative · block · refs · title · given · when · then · section · source_line

Run:  python3 export_scenarios.py
"""

import csv
import json
import re
from pathlib import Path

SPECS = Path(__file__).resolve().parent.parent
PAGES = [
    "view-orders", "order-detail", "ready-to-outbound", "stock-status",
    "order-management", "tracking-missing", "closing", "inbound-request",
]

QA_ID = r"QA-[A-Z0-9]+(?:-[A-Z0-9]+)*"
REF = re.compile(r"\[(?:[A-Z]{1,3}-\d+[a-z]?|G-\d+|PD-\d+|L-[A-Za-z0-9-]+)\]")


def clean(s):
    """Strip markdown emphasis and collapse whitespace, keeping the words."""
    s = re.sub(r"\*\*(.+?)\*\*", r"\1", s)
    s = re.sub(r"\*(.+?)\*", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


def split_gwt(body):
    """Split one scenario body into given / when / then.

    Keywords may appear bolded, capitalised, at line start or mid-sentence
    (the table form runs them together). Anything before the first keyword is
    kept as a preamble on `given` so no text is silently dropped.
    """
    marks = [(m.start(), m.group(1).lower())
             for m in re.finditer(r"\b(Given|When|Then|And|But)\b", body)]
    if not marks:
        return "", "", ""
    out = {"given": [], "when": [], "then": []}
    cur = "given"
    if marks[0][0] > 0:
        out["given"].append(body[:marks[0][0]].strip(" —-·"))
    for i, (pos, kw) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(body)
        chunk = body[pos:end].strip()
        if kw in ("given", "when", "then"):
            cur = kw
        out[cur].append(chunk)
    return (clean(" ".join(out["given"])),
            clean(" ".join(out["when"])),
            clean(" ".join(out["then"])))


def tier_of(*candidates):
    """Read the tier from a *tier field*, never from prose.

    A scenario body may mention "[WF]" while describing another scenario
    (RTO's QA-E-20 says "the [WF] half is covered by QA-M1-03"), so scanning
    the whole row mis-tiers it. Only a candidate that *starts* with the marker
    — the dedicated tier cell, or the bracket right after the id — counts.
    """
    for c in candidates:
        s = c.strip().strip("`").lstrip("*_ ").strip()
        if s.startswith("[WF]"):
            return "WF"
        if s.startswith("[ADMIN]"):
            return "ADMIN"
    return ""


def tier_in_header(*candidates):
    """Prose headers carry the tier anywhere in the bold run.

    order-management writes `**QA-IMP-01 [WF]** — title` (tier first) while
    order-detail writes `**QA-OUT-11 ... · NEGATIVE [ADMIN]**` (tier last).
    A *header* is short and dedicated, so searching all of it is safe — unlike
    a scenario body, which is why `tier_of` stays strict for table cells.
    """
    for c in candidates:
        if "[WF]" in c:
            return "WF"
        if "[ADMIN]" in c:
            return "ADMIN"
    return ""


def block_of(qa_id):
    """QA-IMP-35 -> IMP. QA-S1b-04 -> S1b. The middle token is the block."""
    parts = qa_id.split("-")
    return parts[1] if len(parts) >= 3 else ""


def parse(page):
    path = SPECS / f"{page}.md"
    lines = path.read_text(encoding="utf-8").split("\n")

    start = next((i for i, l in enumerate(lines)
                  if re.match(r"^## 8\.", l)), None)
    if start is None:
        return []
    end = next((j for j in range(start + 1, len(lines))
                if re.match(r"^## 9\.", lines[j])), len(lines))

    rows, section, i = [], "", start
    seen = set()
    while i < end:
        line = lines[i]

        if re.match(r"^#{3,4}\s", line):
            section = clean(re.sub(r"^#+\s*", "", line))

        # --- table form -------------------------------------------------
        # the tier sometimes sits inside the first cell: | **QA-DC-06** `[ADMIN]` | …
        m = re.match(r"^\|\s*\*\*(" + QA_ID + r")\*\*([^|]*)\|(.*)$", line)
        if m:
            qa, head, rest = m.group(1), m.group(2), m.group(3)
            rest = head + "|" + rest if head.strip() else rest
            cells = [c.strip() for c in rest.split("|")]
            refs = sorted({r for c in cells[:2] for r in REF.findall(c)})
            tier = tier_of(head, *cells[:3])
            body = " ".join(cells[2:]) if len(cells) > 2 else ""
            g, w, t = split_gwt(body)
            rows.append(dict(id=qa, page=page, tier=tier,
                             negative="negative" in rest.lower() or "(neg)" in rest.lower(),
                             block=block_of(qa), refs=";".join(refs),
                             title="", given=g, when=w, then=t,
                             section=section, source_line=i + 1, form="table"))
            seen.add(qa)
            i += 1
            continue

        # --- prose form -------------------------------------------------
        m = re.match(r"^\*\*(" + QA_ID + r")\s*(.*?)\*\*\s*(?:—|-|–)?\s*(.*)$", line)
        if m:
            qa, head, title = m.group(1), m.group(2), m.group(3)
            body_lines = []
            j = i + 1
            while j < end and not re.match(r"^\*\*" + QA_ID, lines[j]) \
                    and not re.match(r"^#{2,4}\s", lines[j]) \
                    and not lines[j].startswith("| **QA-"):
                body_lines.append(lines[j])
                j += 1
            body = " ".join(x.strip("- ").strip() for x in body_lines)
            g, w, t = split_gwt(body)
            rows.append(dict(id=qa, page=page, tier=tier_in_header(head, title),
                             negative="(neg)" in head or "(neg)" in title
                                      or "negative" in head.lower(),
                             block=block_of(qa), refs=";".join(sorted(set(REF.findall(title + " " + body)))),
                             title=clean(title) or clean(head), given=g, when=w, then=t,
                             section=section, source_line=i + 1, form="prose"))
            seen.add(qa)
            i = j
            continue

        i += 1

    return rows


def main():
    all_rows = []
    for p in PAGES:
        rows = parse(p)
        all_rows.extend(rows)
        wf = sum(1 for r in rows if r["tier"] == "WF")
        adm = sum(1 for r in rows if r["tier"] == "ADMIN")
        print(f"  {p:<18} {len(rows):>4} scenarios   WF {wf:>3} · ADMIN {adm:>3}"
              f" · untagged {len(rows) - wf - adm}")

    out_json = Path(__file__).resolve().parent / "scenarios.json"
    out_csv = Path(__file__).resolve().parent / "scenarios.csv"
    out_json.write_text(json.dumps(all_rows, ensure_ascii=False, indent=1),
                        encoding="utf-8")
    cols = ["id", "page", "tier", "negative", "block", "refs", "title",
            "given", "when", "then", "section", "source_line", "form"]
    with out_csv.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(all_rows)

    wf = sum(1 for r in all_rows if r["tier"] == "WF")
    adm = sum(1 for r in all_rows if r["tier"] == "ADMIN")
    print(f"\n  TOTAL {len(all_rows)} scenarios · WF {wf} · ADMIN {adm}"
          f" · untagged {len(all_rows) - wf - adm}")
    print(f"  wrote {out_json.name} · {out_csv.name}")


if __name__ == "__main__":
    main()
