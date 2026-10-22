#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Two decision variants:

  B1 = R-A (the reply as drafted): is reviewed in permitted_list? If not, defect. Pure string comparison.
  B2 = R-D' + L1 + L3：
       1) L1: normalise the reviewed identifier first; if it cannot be resolved, defect (not attributable)
       2) L2: act_type is derived from signed_at vs executed_at (the self-declared field is not read)
       3) L3: the pre-decision branch requires reviewed in presented_set (a set, not a single value)
              the post-hoc branch requires only that reviewed exists and is attributable
"""
from datetime import datetime


def _t(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")


def derive_act_type(record, norm):
    """post-hoc audit <=> signing later than execution. Execution time is taken from the executed version's produced_at."""
    ex_id, _ = norm.resolve(record["executed"])
    if ex_id is None:
        return "underived", "executed identifier cannot be resolved"
    ex_t = norm.versions[ex_id]["produced_at"]
    if _t(record["signed_at"]) <= _t(ex_t):
        return "oversight_decision", f"signed {record['signed_at']} <= exec {ex_t}"
    return "post_hoc_audit", f"signed {record['signed_at']} > exec {ex_t}"


def decide_b1(record, revision, norm=None):
    """B1: exactly as drafted in the reply - no normalisation, no presented set, no act type."""
    permitted = set(revision["permitted_list"])
    rv = record["reviewed"]
    if rv not in permitted:
        return True, f"reviewed({rv}) not in permitted_list", "-"
    return False, f"reviewed({rv}) in permitted_list", "-"


def decide_b2(record, revision, norm):
    # L1
    rv, path = norm.resolve(record["reviewed"])
    if rv is None:
        return True, f"identifier cannot be resolved -> attribution unprovable ({path})", "-"
    # L2
    at, why = derive_act_type(record, norm)
    # L3
    if at == "oversight_decision":
        pset = set(revision["presented_set"])
        if rv not in pset:
            return True, f"pre-decision: reviewed->{rv}, but the package only ever submitted {sorted(pset)}", at
        return False, f"pre-decision: reviewed->{rv} is in the submitted set", at
    if at == "post_hoc_audit":
        return False, f"post-hoc audit: {rv} exists and is attributable", at
    return True, f"act_type cannot be derived ({why})", at


def derivation_is_vacuous(norm, probe_signed_times):
    """
    to show that the L2 derivation is circular, not an independent check:
    for any signed_at a legal act_type can always be obtained, and that act_type never conflicts with the timestamp.
    the timestamp therefore cannot refute the derived result: it determines the branch, it does not constrain it.
    """
    rows = []
    for st in probe_signed_times:
        fake = {"reviewed": "s005", "executed": "s008", "signed_at": st}
        at, why = derive_act_type(fake, norm)
        rows.append((st, at, why, "consistent (always true)"))
    return rows
