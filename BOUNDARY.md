# Relation to existing work

A short note, mostly citation. It records the three places in the group's record that are closest to the object tested here, states what each of them actually says, and names the one cell this repository adds.

## What this repository tests

Two artefacts about the same oversight step: a package that states which state version it presented, and a record that states which was reviewed. Each is internally consistent. The defect is that they name **different versions**.

## Three citations, and what each one actually says

**1. #6, comment 37 — 6 October, by the author of this repository.**

> *"…it compared the documents with each other, and had no view of the documents against the tree…"*

This is the two-verification structure stated plainly: a check that compares documents to one another has no view of any of them against an external reference. It is the closest existing statement of the *shape*.

**2. #13, comment 63 — 19 October, by the author of this repository.**

> *"`source_state_at_dispatch` and `receiver_state_used` are the two your requirement points to."*

Two field names, one on each side of a handoff. This is the closest existing *instance* — but it is a handoff: one party dispatches, another receives.

**3. #13, comment 65 — 21 October, by dakleyer — and this one must not be misread.**

> *"…establish that the receiver used the latest decision-applicable state at action time. This is a claim-scope distinction for review, not a new mandatory field, accepted requirement or additional H1 test case."*

That disposition is about a **different axis**: whether the receiver used the state that was applicable at the time it acted — a freshness question. It is not about which version either side *says* it reviewed.

**So it does not dispose of the object here, and this note does not cite it as if it did.** Anyone reading this repository should take the disposition as applying where it was written.

## The cell this repository adds

Same producer, same review, two artefacts, different versions named — with no handoff involved:

- **#13 c63** is two parties across a handoff; here both artefacts come from one side of one review.
- **#13 c65** is whether the state used was current; here both states may be perfectly current and the two documents still name different ones.
- **#6 c37** is the general shape; here it is instantiated and measured.

Whether that cell deserves a line of its own is a judgement for the group. **This note proposes no field, no requirement and no test case.**

## One correction to an earlier draft of this note

An earlier draft listed the group's #30 material as an existing negative control, and attributed the #13 disposition to the group rather than to its author. Both were wrong:

- **#30** is an external prior-art positioning document, not a group-internal control. It is relevant here only as the *method* — construct the control, fix the expected observation before running, report the result even when negative — and is cited for that and nothing else.
- The **#13 c65** disposition is one participant's framing of a different distinction. It is quoted above with its scope intact rather than paraphrased into a broader claim.

## Where the measurement lives

`README.md` gives the numbers; `FIELD_LIST.md` gives the fields and the measured consequence of removing each. Neither depends on the argument above.
