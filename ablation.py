#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ablation: remove one layer or field at a time and watch FP / FN move.
Purpose: the "what happens without it" column in FIELD_LIST.md must be filled with measured numbers, not inference.
"""
import json
import pathlib

from normalize import Normalizer, content_hash

HERE = pathlib.Path(__file__).parent
FIX = HERE / "fixtures"
revision = json.loads((FIX / "case_revision.json").read_text(encoding="utf-8"))
VERS = {v["id"]: v for v in revision["state_versions"]}
PRODUCED = {v["id"]: v["produced_at"] for v in revision["state_versions"]}


def materialize(rec):
    r = dict(rec)
    t = r["reviewed"]
    if isinstance(t, str) and t.startswith("@{hash:"):
        r["reviewed"] = content_hash(VERS[t[7:-1]])
    elif isinstance(t, str) and t.startswith("@{ts:"):
        r["reviewed"] = VERS[t[5:-1]]["produced_at"]
    return r


records = [materialize(r) for r in
           json.loads((FIX / "records.json").read_text(encoding="utf-8"))["records"]]

NORM_C = Normalizer(revision, mode="content")
NORM_D = Normalizer(revision, mode="declared")


def decide(rec, norm, presented_as_set=True, act_type_source="derived", have_produced_at=True):
    rv, path = norm.resolve(rec["reviewed"])
    if rv is None:
        return True, f"identifier cannot be resolved"
    if act_type_source == "declared":
        at = rec.get("declared_act_type", "underived")
    else:
        if not have_produced_at:
            return True, "produced_at missing -> act_type cannot be derived"
        ex = norm.resolve(rec["executed"])[0]
        if ex is None:
            return True, "executed cannot be resolved"
        at = "oversight_decision" if rec["signed_at"] <= PRODUCED[ex] else "post_hoc_audit"
    if at == "oversight_decision":
        pset = set(revision["presented_set"]) if presented_as_set else {"s005"}
        return (rv not in pset), f"pre-decision reviewed->{rv}"
    if at == "post_hoc_audit":
        return False, f"post-hoc audit {rv}"
    return True, "act_type underived"


def score(**kw):
    fp = fn = fn_in = fn_out = 0
    detail = []
    norm = kw.pop("norm")
    for rec in records:
        fires, why = decide(rec, norm, **kw)
        gt = rec["ground_truth"]
        if gt == "ambiguous":
            continue
        if fires and gt == "legit":
            fp += 1
            detail.append(f"FP:{rec['rid']}")
        elif (not fires) and gt == "defect":
            if rec.get("scope") == "in":
                fn_in += 1
            else:
                fn_out += 1
            detail.append(f"FN:{rec['rid']}")
    fn = fn_in + fn_out
    return fp, fn, fn_in, fn_out, detail


CASES = [
    ("full (B2b)", dict(norm=NORM_C)),
    ("without L3: presented degrades to a single value {s005}", dict(norm=NORM_C, presented_as_set=False)),
    ("without L1/content: fall back to the declared alias table", dict(norm=NORM_D)),
    ("without L2 derivation: use a self-declared act_type", dict(norm=NORM_C, act_type_source="declared")),
    ("without produced_at: no production instant", dict(norm=NORM_C, have_produced_at=False)),
]

print(f"{'ablation':<44}{'FP':>4}{'FN':>4}{'FN(obs)':>9}{'FN(out)':>9}  failure detail")
print("-" * 118)
for name, kw in CASES:
    fp, fn, fi, fo, det = score(**kw)
    print(f"{name:<42}{fp:>5}{fn:>5}{fi:>13}{fo:>11}  {', '.join(det) if det else '(none)'}")
