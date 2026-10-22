#!/usr/bin/env python3
"""demo.py - one oversight step, walked end to end.

This is the demo the README refers to. It runs three scenarios against the same
case revision and prints, for each one, what the package says, what the record
says, what each artefact's own checks report, and what the cross-artefact rule
concludes.

Scenario A  the record reviewed a version the package presented  -> passes
Scenario B  the record reviewed a version never presented          -> defect
Scenario C  a record that backdates its signing time               -> passes (the known hole)

Run:  python demo.py
"""
from __future__ import annotations

import json
from pathlib import Path

from normalize import Normalizer
from rule import decide_b2

HERE = Path(__file__).resolve().parent
REV = json.loads((HERE / "fixtures" / "case_revision.json").read_text(encoding="utf-8"))


def own_checks(record: dict) -> list[str]:
    """What either artefact can establish about itself, without the other one.

    These are the checks a producer would run: is the record well formed, does
    the version it names exist, is the signature present. All of them pass in
    every scenario below.
    """
    out = []
    ids = {v["id"] for v in REV["state_versions"]}
    out.append("record is well formed (rid, reviewed, executed, signed_at all present)"
               if all(record.get(k) for k in ("rid", "reviewed", "executed", "signed_at"))
               else "record is MALFORMED")
    out.append(f"reviewed version {record['reviewed']} exists in the revision"
               if record["reviewed"] in ids
               else f"reviewed version {record['reviewed']} DOES NOT EXIST")
    out.append("executed version exists"
               if record["executed"] in ids else "executed version DOES NOT EXIST")
    return out


def show(title: str, record: dict) -> bool:
    print("=" * 78)
    print(title)
    print("=" * 78)
    print(f"  package {REV['package']['package_id']} says it presented: "
          f"{REV['presented_set']}")
    print(f"  record  {record['rid']} says it reviewed:            "
          f"{record['reviewed']}")
    print(f"  record says it executed:                            {record['executed']}")
    print(f"  record signing time:                                {record['signed_at']}")
    print("  -- each artefact on its own --")
    for line in own_checks(record):
        print(f"     {line}")
    norm = Normalizer(REV, mode="content")
    fires, why, at = decide_b2(record, REV, norm)
    print("  -- the cross-artefact rule --")
    print(f"     act type derived: {at}")
    print(f"     verdict: {'DEFECT' if fires else 'pass'}")
    print(f"     reason: {why}")
    print()
    return fires


def main() -> None:
    a = {"rid": "DEMO-A", "desc": "reviewed a version that was presented",
         "reviewed": "s005", "executed": "s006",
         "signed_at": "2026-10-19T11:40:00Z",
         "declared_act_type": "oversight_decision", "scope": "in"}
    b = {"rid": "DEMO-B", "desc": "reviewed a version that was never presented",
         "reviewed": "s007", "executed": "s008",
         "signed_at": "2026-10-19T11:40:00Z",
         "declared_act_type": "oversight_decision", "scope": "in"}
    c = {"rid": "DEMO-C", "desc": "pre-decision with a backdated signing time",
         "reviewed": "s007", "executed": "s008",
         "signed_at": "2026-10-19T16:20:00Z",
         "declared_act_type": "oversight_decision", "scope": "in"}

    ra = show("Scenario A - the record names a version the package presented", a)
    rb = show("Scenario B - the record names a version the package never presented", b)
    rc = show("Scenario C - a pre-decision whose signing time was moved after execution", c)

    print("=" * 78)
    print("What the three scenarios show")
    print("=" * 78)
    print("  A passes and B fails even though every check either artefact can run")
    print("  on itself passes in both. The difference is not in either document;")
    print("  it is in the relation between them.")
    print()
    print("  C is the hole this repository does not close. Moving one timestamp")
    print("  makes the record look like a post-hoc audit, and a post-hoc audit is")
    print("  allowed to name the executed version. Catching it needs a signing")
    print("  time the record's author cannot rewrite - a time source, not a field.")
    print()
    ok = (not ra) and rb and (not rc)
    print(f"  demo expectation met: {ok}")
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()
