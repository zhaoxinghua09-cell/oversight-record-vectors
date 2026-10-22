# Relation to existing work

A short note, mostly citation. It records where the object tested here already appears in the group's record, the one cell that is not covered, and one correction to an earlier draft of this note.

## What this repository tests

Two artefacts about the same oversight step: a package that states which state version it presented, and a record that states which was reviewed. Each is internally consistent. The defect is that they name different versions.

## Where this is already named in the group

It is not new as a *structure*. The group has already said, in several places, that a document agreeing with itself is not the same as a document agreeing with something else:

- **#6, comment 36 (6 October)**: a check "compared the documents with each other, and had no view of the documents against the tree". That is the two-verification arrangement, stated plainly.
- **#13, comment 54**: a self-report and a trace cross-checked against one another; when the other side is absent, what the trace can carry is different in kind.
- **#13, comment 57**: the same source-to-receiver divergence, measured in both directions on H1 v0.4.1-r1 — `source_state_at_dispatch` against `receiver_state_used`.
- **#13, comment 62**: which comparison a line of evidence supports decides which half of a gap it belongs to.
- **#13, comment 64**: *"This is a claim-scope distinction for review, not a new mandatory field, accepted requirement or additional H1 test case."*

That last sentence is the group's disposition, and this note does not reopen it. **Nothing here proposes a field, a requirement, or a test case.**

## The one cell that is not covered

The H1 pair above is a handoff: one party dispatches, another receives. The case tested in this repository is different in two respects:

- the two artefacts come from the **same producer**, within one review, rather than from two parties in a handoff;
- what differs is not the state each side used, but **which version each side says was reviewed** — so the disagreement can exist with no handoff at all.

Whether that cell is worth a line of its own is a judgement for the group, not a claim made here.

## One correction to an earlier draft of this note

An earlier version listed the group's #30 material as an existing negative control. That is a category error: #30 is an external prior-art positioning document, not a group-internal control. It is relevant here only as the method — construct the control, fix the expected observation before running, report the result even when negative — and it is cited for that and nothing else.

## Where the measurement itself lives

`README.md` gives the numbers; `FIELD_LIST.md` gives the fields and the measured consequence of removing each one. Neither depends on the argument above.
