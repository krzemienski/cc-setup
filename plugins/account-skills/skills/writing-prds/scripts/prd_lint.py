#!/usr/bin/env python3
"""prd_lint: check a Markdown PRD for the properties engineering needs to start without
follow-up questions. Exit 1 when any ERROR is found.

Checks
  sections     required top-level sections exist, in order (configurable with --sections)
  placeholders no TODO/TBD/lorem/"[Description of"/"???"/"<fill" text outside code blocks
  screens      every "### S<n>" screen heading has a "**APIs called:**" line and a "**States" line
  config       every configuration table row has a non-empty default and "set in" cell
  sources      a Sources section exists and contains at least --min-sources http(s) links
  goals        goals table rows each have a measure
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_SECTIONS = [
    "Overview and goals",
    "Screens",
    "System architecture",
    "Models",
    "Outputs",
    "Configuration",
    "Research appendix",
]
PLACEHOLDER = re.compile(r"\b(TODO|TBD|FIXME|lorem ipsum)\b|\[Description of|\?\?\?|<fill", re.I)


def strip_code(md: str) -> str:
    return re.sub(r"```.*?```", "", md, flags=re.S)


def h2_titles(md: str) -> list[str]:
    return [re.sub(r"^\d+\.\s*", "", m.strip()) for m in re.findall(r"^## (.+)$", md, flags=re.M)]


def sections_of(md: str, level: str) -> list[tuple[str, str]]:
    parts = re.split(rf"^({level} .+)$", md, flags=re.M)
    return [(parts[i].lstrip("# ").strip(), parts[i + 1]) for i in range(1, len(parts) - 1, 2)]


def table_rows(block: str) -> list[list[str]]:
    rows = []
    for line in block.splitlines():
        if line.strip().startswith("|") and not re.match(r"^\|\s*-", line.strip()):
            rows.append([c.strip() for c in line.strip().strip("|").split("|")])
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("prd")
    p.add_argument("--sections", help="comma-separated required H2 section titles, in order")
    p.add_argument("--min-sources", type=int, default=3)
    a = p.parse_args()

    md = Path(a.prd).read_text("utf-8")
    prose = strip_code(md)
    findings: list[tuple[str, str]] = []

    required = [s.strip() for s in a.sections.split(",")] if a.sections else DEFAULT_SECTIONS
    titles = h2_titles(md)
    idx = []
    for s in required:
        hits = [i for i, t in enumerate(titles) if t.lower().startswith(s.lower())]
        if not hits:
            findings.append(("ERROR", f"missing section: {s}"))
        else:
            idx.append(hits[0])
    if idx != sorted(idx):
        findings.append(("ERROR", "required sections are out of order"))

    for n, line in enumerate(prose.splitlines(), 1):
        if PLACEHOLDER.search(line):
            findings.append(("ERROR", f"placeholder text: {line.strip()[:100]}"))

    screens = [(t, b) for t, b in sections_of(md, "###") if re.match(r"\d+\.\d+\s+S\d+|S\d+\b", t)]
    for t, b in screens:
        if "**APIs called:**" not in b:
            findings.append(("ERROR", f"screen without an 'APIs called' line: {t}"))
        if "**States" not in b:
            findings.append(("WARN", f"screen without a States list: {t}"))
    if not screens:
        findings.append(("WARN", "no screen headings of the form '### 2.n S<n> — Name' found"))

    for title, body in sections_of(md, "##"):
        if title.lower().lstrip("0123456789. ").startswith("configuration"):
            for row in table_rows(body):
                if len(row) >= 4 and row[0] not in ("#", "Token") and re.match(r"^[\d.]+$|^`", row[0]):
                    default, set_in = row[2], row[3]
                    if not default or not set_in:
                        findings.append(("ERROR", f"config row {row[0]} lacks a default or 'set in'"))
        if title.lower().lstrip("0123456789. ").startswith("overview"):
            for row in table_rows(body):
                if row and re.match(r"^G\d+$", row[0]) and (len(row) < 3 or not row[-1]):
                    findings.append(("ERROR", f"goal {row[0]} has no measure"))

    src = re.search(r"^#{2,3} [^\n]*Sources[^\n]*\n", md, flags=re.M)
    links = re.findall(r"https?://[^\s)>\]]+", md[src.end():]) if src else []
    if not src:
        findings.append(("ERROR", "no Sources section"))
    elif len(links) < a.min_sources:
        findings.append(("ERROR", f"Sources has {len(links)} links; need at least {a.min_sources}"))

    for lvl, msg in findings:
        print(f"{lvl:5} {msg}")
    errors = sum(1 for f in findings if f[0] == "ERROR")
    print(f"prd_lint: {len(screens)} screens, {len(links)} source links, {errors} error(s), "
          f"{sum(1 for f in findings if f[0] == 'WARN')} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
