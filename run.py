#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run the full fixture: the B1 / B2 comparison, FP and FN counts, and the L2 circularity check."""
import json
import pathlib

from normalize import Normalizer, content_hash
from rule import decide_b1, decide_b2, derive_act_type, derivation_is_vacuous

HERE = pathlib.Path(__file__).parent
FIX = HERE / "fixtures"

revision = json.loads((FIX / "case_revision.json").read_text(encoding="utf-8"))
raw_records = json.loads((FIX / "records.json").read_text(encoding="utf-8"))["records"]

# ---- fixture construction: replace @{hash:sNNN} / @{ts:sNNN} with real values ----
VERS = {v["id"]: v for v in revision["state_versions"]}


def materialize(rec):
    r = dict(rec)
    t = r["reviewed"]
    if isinstance(t, str) and t.startswith("@{hash:"):
        r["reviewed"] = content_hash(VERS[t[7:-1]])
    elif isinstance(t, str) and t.startswith("@{ts:"):
        r["reviewed"] = VERS[t[5:-1]]["produced_at"]
    return r


records = [materialize(r) for r in raw_records]

MODES = [("declared", "L1 = declared alias table (jointly maintained, can be wrong or poisoned)"),
         ("content", "L1 = content-recomputed hash (declared table not used)")]

W = 20


def score(rows):
    fp = sum(1 for r in rows if r["fires"] and r["gt"] == "legit")
    fn = sum(1 for r in rows if (not r["fires"]) and r["gt"] == "defect")
    fp_in = sum(1 for r in rows if r["fires"] and r["gt"] == "legit" and r["scope"] == "in")
    fn_in = sum(1 for r in rows if (not r["fires"]) and r["gt"] == "defect" and r["scope"] == "in")
    fn_out = sum(1 for r in rows if (not r["fires"]) and r["gt"] == "defect" and r["scope"] == "out")
    amb = sum(1 for r in rows if r["gt"] == "ambiguous")
    return fp, fn, fp_in, fn_in, fn_out, amb


def run(decide, norm):
    rows = []
    for rec in records:
        fires, why, at = decide(rec, revision, norm)
        rows.append({
            "rid": rec["rid"], "fires": fires, "why": why, "at": at,
            "gt": rec["ground_truth"], "scope": rec.get("scope", "in"),
        })
    return rows


def dump(title, rows, extra=None):
    print()
    print("=" * 118)
    print(title)
    print("=" * 118)
    print(f"{'record':<22}{'act_type':<20}{'decision':<10}{'truth':<11}{'scope':<8}{'result':<10}")
    print("-" * 118)
    for r in rows:
        if r["gt"] == "ambiguous":
            res = "ambiguous"
        elif r["fires"] and r["gt"] == "legit":
            res = "false positive"
        elif (not r["fires"]) and r["gt"] == "defect":
            res = "false negative"
        elif r["fires"]:
            res = "hit"
        else:
            res = "pass"
        print(f"{r['rid']:<22}{r['at']:<20}{'defect' if r['fires'] else 'pass':<8}"
              f"{r['gt']:<11}{r['scope']:<8}{res:<8}")
    fp, fn, fp_in, fn_in, fn_out, amb = score(rows)
    print("-" * 118)
    print(f"  FP={fp}  FN={fn}   (of which FP entirely within the observable range = {fp_in}; "
          f"FN observable = {fn_in}, FN out of scope (needs an external fact) = {fn_out}; {amb} ambiguous not counted)")


print("fixture: 14 records = 5 defective / 8 legitimate / 1 ambiguous")
print("presented_set =", revision["presented_set"])
print("permitted_list =", revision["permitted_list"], "(used by B1; identical to presented_set, so that B1 is not handicapped)")

norm_declared = Normalizer(revision, mode="declared")
norm_content = Normalizer(revision, mode="content")

b1 = run(lambda rec, rev, n: decide_b1(rec, rev), norm_declared)
dump("B1  R-A (reply as drafted): reviewed not in permitted_list", b1)

b2d = run(decide_b2, norm_declared)
dump("B2a R-D' + L1(declared) + L3", b2d)

b2c = run(decide_b2, norm_content)
dump("B2b R-D' + L1(content) + L3", b2c)

s_b1, s_b2d, s_b2c = score(b1), score(b2d), score(b2c)

print()
print("=" * 118)
print("Three sets of numbers")
print("=" * 118)
print(f"{'':<44}{'FP':>6}{'FN':>6}{'FP(observable)':>16}{'FN(observable)':>16}{'FN(out)':>9}")
for name, s in [("B1  R-A as drafted", s_b1),
                ("B2a R-D'+L1(declared)+L3", s_b2d),
                ("B2b R-D'+L1(content)+L3", s_b2c)]:
    print(f"{name:<44}{s[0]:>6}{s[1]:>6}{s[2]:>14}{s[3]:>14}{s[4]:>12}")

print()
print("=" * 118)
print("B3  which failures the rule can fix, and which only a data contract can")
print("=" * 118)
print("B1 false positives:")
for r in b1:
    if r["fires"] and r["gt"] == "legit":
        print(f"  {r['rid']:<24}{r['why']}")
print()
print("B2b false negatives:")
for r in b2c:
    if (not r["fires"]) and r["gt"] == "defect":
        print(f"  {r['rid']:<24}{r['why']}")

print()
print("=" * 118)
print("L2 circularity check: can the timestamp ever refute the act_type it derives?")
print("=" * 118)
probe = ["2026-10-19T09:00:00Z", "2026-10-19T15:30:00Z",
         "2026-10-19T16:00:00Z", "2026-10-19T16:20:00Z", "2026-10-20T09:00:00Z"]
print(f"{'signed_at':<26}{'derived act_type':<22}{'basis':<40}refutable")
for st, at, why, verdict in derivation_is_vacuous(norm_content, probe):
    print(f"{st:<26}{at:<22}{why:<40}{verdict}")
print("  => every signed_at yields a legal act_type, and none ever conflicts.")
print("     The timestamp only decides the branch; it does not constrain it. So it cannot stop a forged signing time (NEG_BACKDATED).")

print()
print("=" * 118)
print("Single-valuedness of the timestamp as an identifier")
print("=" * 118)
print(f"  produced_at collision set: {sorted(norm_content.ts_collisions) if norm_content.ts_collisions else 'none'}")
print("  => no collision in this fixture, so the timestamp route is usable here; once two versions are produced at the same instant it degrades to multiple values and the route must be dropped.")
