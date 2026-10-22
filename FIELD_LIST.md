# FIELD_LIST — the minimum fields this rule needs

Measured baseline: `python run.py` (B1 / B2) and `python ablation.py` (per-field ablation).
Fixture: 14 records = 5 defective / 8 legitimate / 1 ambiguous.

## 1. The fields

| # | field | type | produced by | what happens without it (**measured**) |
|---|---|---|---|---|
| 1 | `case_revision` | string | **jointly maintained** | not ablated. Without it, records from different revisions cannot be compared in isolation — a structural gap, producing no FP or FN |
| 2 | `state_versions[].id` | string | **the other party** (package owner) | not ablated. Without it there is no frame of reference; the rule has no input |
| 3 | `state_versions[].produced_at` | ISO-8601 (UTC, `Z`) | **the other party** | **FP 0 → 8**: all eight legitimate records become false positives (`executed_at` unavailable ⇒ act_type cannot be derived ⇒ every record judged defective) |
| 4 | `state_versions[].content` | any JSON (canonically serialisable) | **the other party** | **FN +1**: `NEG_ALIAS_CONFUSION` is missed (the hash cannot be recomputed ⇒ the declared table decides ⇒ poisonable) |
| 5 | `presented_set` | `set<string>` | **the other party** | **FP +1**: `P_CLARIF_SET` becomes a false positive (two clarification rounds, but only the first round's `s003` was reviewed; a single value cannot express that) |
| 6 | `reviewed` | string (serial / content hash / production timestamp) | **our side** (record author) | not ablated. The rule's main input |
| 7 | `executed` | string (as above) | **our side** | same cause as #3: no execution instant ⇒ act_type cannot be derived ⇒ the same "FP 0→8" |
| 8 | `signed_at` | ISO-8601, **must come from an external trusted time source, not filled in by the record author** | **external** (a time authority) | **FN 1, and the only miss that cannot be removed**: `NEG_BACKDATED` (see §3) |
| 9 | ~~`act_type` (self-declared)~~ | — | — | **explicitly not wanted.** If used: **FN(observable) 0 → 1**, `NEG_DISGUISED` is missed. Self-declaration lets the defendant pick the statute |
| 10 | `aliases` (declared alias table) | `map<string,string>` | jointly maintained | **optional and harmful**: adopting it turns `NEG_ALIAS_CONFUSION` from caught into missed. Needed only when a content hash cannot be recomputed, and then it needs a separate check |

## 2. Who holds the pen — the most important column in this table

| field class | our side | other party | external |
|---|---|---|---|
| the **criteria** (#1 #2 #3 #4 #5) | 0 | **5** | 0 |
| the **inputs** (#6 #7) | 2 | 0 | 0 |
| the **time base** (#8) | 0 | 0 | **1** |

**Conclusion: implemented as above, the party under test supplies only an allegation; every criterion sits with the other party or outside both.**

That is a good thing — it **breaks** the closed loop found in the first round (the author writing both the standard and the answer). The cost is that the author can no longer make the test pass unilaterally, and therefore can no longer promise a delivery date unilaterally.

That cost has to be stated in the text, otherwise it amounts to giving up control without getting anything acknowledged in return.

## 3. The one miss that cannot be removed, and why

`NEG_BACKDATED`: a pre-decision (reviewed `s007`, executed `s008`) with the signing time written as `16:20` (execution was at `16:00`).

The L2 derivation is `signed_at ≤ executed_at ⇒ oversight_decision`, so the record is derived as a post-hoc audit, takes the lenient branch, and passes.

The circularity check in `run.py` produces an always-true table:

| signed_at | derived act_type | refutable by the timestamp |
|---|---|---|
| 09:00 | oversight_decision | always true |
| 15:30 | oversight_decision | always true |
| 16:00 | oversight_decision | always true |
| 16:20 | post_hoc_audit | always true |
| 09:00 next day | post_hoc_audit | always true |

**The timestamp only decides the branch; it does not constrain it.** Any `signed_at` yields a legal act_type, so the derivation can never be refuted by a forged timestamp.

This is not a missing field — `signed_at` is present. What is missing is **the anchor that stops the author rewriting it**.

So: B2's FN falls from 2 to 1 by making the hash recomputable (tightening L1); going from 1 to 0 requires replacing the *source* of `signed_at`, which is not a data contract but infrastructure.

## 4. How to reproduce

```
python run.py        # the B1 / B2a / B2b tables, the three sets of numbers, and the circularity check
python ablation.py   # per-field ablation, producing the last column of §1
```

The `@{hash:sNNN}` / `@{ts:sNNN}` markers in `fixtures/records.json` are placeholders that `run.py` substitutes with real values at load time, so the fixture does not have to hard-code hashes the author could not pre-compute.

## 5. English note, usable in a comment (154 words)

One membership test is being asked to do three jobs: establish that two names denote the same version, establish which kind of act the record describes, and establish what the package presented. Its errors are not a tuning problem.

On 14 records (5 defects, 8 legitimate, 1 ambiguous), the rule as drafted gives 4 false positives, 0 false negatives. Split into identity normalisation, a derived act-type branch, and a presented set, it gives 0 false positives and 1 false negative.

That remaining miss is a backdated signature, unfixable by any field. Deriving act-type from signing time is circular: the timestamp decides the branch and can never contradict it. This is a consistency check on the record, not a truth check about the world.

This corrects my scope. Identity normalisation and the presented set are data-contract obligations needing joint maintenance; the timestamp needs an external anchor. None is inside the three artefacts I offered.
