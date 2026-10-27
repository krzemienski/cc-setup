#!/usr/bin/env python3
"""phase_status: report which Speakwright phases and plans have passed their gates and which
plan to execute next. Reads .planning/ROADMAP.md and .planning/phases/*/.

A plan is complete when phases/<phase>/<plan>-SUMMARY.md exists. A phase is complete when
phases/<phase>/<NN>-VALIDATION.md exists and contains a line 'Verdict: PASS' for VG-PHASE-<NN>.

usage: phase_status.py [--root .] [--json]   exit 0 when every phase passed, 1 otherwise
"""
import argparse
import json
import re
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=".")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    planning = Path(a.root) / ".planning"
    if not (planning / "ROADMAP.md").exists():
        print(f"no {planning / 'ROADMAP.md'}", file=sys.stderr)
        return 2
    phases = []
    for d in sorted((planning / "phases").iterdir()):
        if not d.is_dir():
            continue
        nn = d.name.split("-")[0]
        plans = sorted(x.name.replace("-PLAN.md", "") for x in d.glob("*-PLAN.md"))
        done = [pl for pl in plans if (d / f"{pl}-SUMMARY.md").exists()]
        val = d / f"{nn}-VALIDATION.md"
        passed = val.exists() and re.search(rf"VG-PHASE-{nn}.*?Verdict:\s*PASS", val.read_text("utf-8"), re.S) is not None
        phases.append({"phase": d.name, "plans": plans, "plans_done": done, "phase_gate_passed": passed})
    nxt = None
    for ph in phases:
        pending = [pl for pl in ph["plans"] if pl not in ph["plans_done"]]
        if pending:
            nxt = f".planning/phases/{ph['phase']}/{pending[0]}-PLAN.md"
            break
        if not ph["phase_gate_passed"]:
            nxt = f".planning/phases/{ph['phase']} (phase gate VG-PHASE-{ph['phase'][:2]} not recorded as PASS)"
            break
    report = {"phases": phases, "next": nxt, "all_passed": nxt is None}
    if a.json:
        print(json.dumps(report, indent=2))
    else:
        for ph in phases:
            mark = "PASS" if ph["phase_gate_passed"] else f"{len(ph['plans_done'])}/{len(ph['plans'])} plans"
            print(f"{ph['phase']:32} {mark}")
        print(f"next: {nxt or 'none — every phase gate passed'}")
    return 0 if nxt is None else 1


if __name__ == "__main__":
    sys.exit(main())
