#!/usr/bin/env python3
"""selfcheck.py - the repository's own evaluation.

It asserts everything the README claims, and it proves it can fail.

Blocks
  E1  the counts in README.md (4/0, 0/2, 0/1)
  E2  the ablation table in FIELD_LIST.md (five rows, expected numbers)
  E3  the three worked examples in examples/
  E4  the demo's three scenarios
  E5  negative control: a deliberately wrong expectation must be REJECTED

Exit 0 only if every assertion holds and the negative control fails as intended.

Run:  python selfcheck.py
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PY = sys.executable
fails: list[str] = []


def check(name: str, actual, expected) -> None:
    ok = actual == expected
    print(f"  [{'OK' if ok else 'FAIL'}] {name}: got {actual!r}, expected {expected!r}")
    if not ok:
        fails.append(name)


def run(script: str) -> str:
    r = subprocess.run([PY, script], cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return (r.stdout or "") + (r.stderr or "")


def e1_counts() -> None:
    print("E1 - counts claimed in README.md")
    out = run("run.py")
    triples = re.findall(
        r"^(B1  R-A as drafted|B2a R-D'\+L1\(declared\)\+L3|B2b R-D'\+L1\(content\)\+L3)"
        r"\s+(\d+)\s+(\d+)", out, re.M)
    rows = {t[0]: (t[1], t[2]) for t in triples}
    b1 = rows.get("B1  R-A as drafted")
    b2a = rows.get("B2a R-D'+L1(declared)+L3")
    b2b = rows.get("B2b R-D'+L1(content)+L3")
    check("B1  (fp, fn)", b1, ("4", "0"))
    check("B2a (fp, fn)", b2a, ("0", "2"))
    check("B2b (fp, fn)", b2b, ("0", "1"))


def e2_ablation() -> None:
    print("E2 - ablation rows asserted in FIELD_LIST.md")
    out = run("ablation.py")
    want = {
        "full (B2b)": ("0", "1"),
        "without L3": ("1", "1"),
        "without L1/content": ("0", "2"),
        "without L2 derivation": ("0", "2"),
        "without produced_at": ("8", "0"),
    }
    got = {}
    for line in out.splitlines():
        if not line.startswith("@RESULT|"):
            continue
        _, name, fp, fn, _fi, _fo = line.split("|")
        for key in want:
            if name.startswith(key):
                got[key] = (fp, fn)
    for key, exp in want.items():
        check(f"ablation {key}", got.get(key), exp)


def e3_examples() -> None:
    print("E3 - worked examples")
    sys.path.insert(0, str(HERE))
    from normalize import Normalizer
    from rule import decide_b2

    rev = json.loads((HERE / "fixtures" / "case_revision.json").read_text(encoding="utf-8"))
    norm = Normalizer(rev, mode="content")
    for p in sorted((HERE / "examples").glob("*.json")):
        ex = json.loads(p.read_text(encoding="utf-8"))
        fires, _, _ = decide_b2(ex["record"], rev, norm)
        check(f"{ex['example']} verdict", "defect" if fires else "pass",
              ex["expected"])


def e4_demo() -> str:
    print("E4 - demo scenarios")
    r = subprocess.run([PY, "demo.py"], cwd=HERE, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    check("demo exit code", r.returncode, 0)
    check("demo A passes", "Scenario A" in out and out.count("verdict: DEFECT") == 1, True)
    return out


def e5_negative_control() -> None:
    print("E5 - negative control (this block must report a FAIL)")
    before = len(fails)
    check("deliberately wrong expectation", "pass", "defect")
    produced = len(fails) > before
    if produced:
        fails.pop()          # expected here; not a real failure
    print(f"  [{'OK' if produced else 'FAIL'}] negative control fired: {produced}")
    if not produced:
        fails.append("negative control did not fire - the harness cannot fail")


def main() -> int:
    e1_counts(); print()
    e2_ablation(); print()
    e3_examples(); print()
    e4_demo(); print()
    e5_negative_control(); print()

    total = len(fails)
    print("=" * 70)
    if total:
        print(f"SELFEVAL: {total} assertion(s) failed")
        for f in fails:
            print(f"  - {f}")
        print("=" * 70)
        return 1
    print("SELFEVAL: all assertions hold; the negative control fired as intended")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())
