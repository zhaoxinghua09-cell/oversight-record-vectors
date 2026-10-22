# Worked examples

Three pairs of artefacts, each self-contained. Run them with `python selfcheck.py`, or read them here.

| example | what changes | expected |
|---|---|---|
| `01-legitimate.json` | the record reviewed `s005`, which the package presented | pass |
| `02-never-presented.json` | the record reviewed `s007`, which the package never presented | **defect** |
| `03-backdated.json` | same defect as 02, but the signing time is moved after execution | pass (**the documented hole**) |

## The one that matters

In **01** and **02**, every check that either artefact can run on itself passes:

- the record is well formed;
- the version it names exists in the case revision;
- the executed version exists;
- the signature is present.

The difference between them is not in either document. It is in the relation between the record and the package.

That is the whole point of this repository, and it is why a single-artefact checker — however thorough — cannot find it.

## The one that is honest about failing

**03** is 02 with **one field changed**: `signed_at` moves from `11:40` to `16:20`, past the execution time of `16:00`.

The rule then derives the act type as a post-hoc audit, and a post-hoc audit is allowed to name the executed version. So the same defect passes.

Nothing in the schema closes this, because nothing in the record can refute the signing time the record carries. It would need a time source the record's author cannot rewrite — infrastructure, not a field. `FIELD_LIST.md` §3 sets out why.

`selfcheck.py` asserts that 03 passes, so the failure is locked in as a known result rather than allowed to look like an oversight.
