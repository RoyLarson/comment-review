# The loop, as run

    binder -> review -> marks -> collate -> revise -> review -> collate -> ... -> alterations

| # | step | who | mechanical? |
| --- | --- | --- | --- |
| 1 | **binder** | `census` | yes |
| 2 | **review** | N role agents, PARALLEL and BLIND | agent |
| 3 | **marks** | each role writes one file | agent |
| 4 | **collate** | the desk flow | **yes -- no agent** |
| 5 | **chief rules** | the copy chief | agent, and it must be able to RUN things |
| 6 | **revise** | the desk flow builds the ask | yes |
| 7 | **review** again | ONLY the roles that marked that place | agent |
| 8 | back to 4 | | |
| 9 | **alterations** | the docket | yes |
| 10 | **proof** | the write chain | yes |

! **Steps 4, 6, 9 and 10 are flow.** Only 2, 5 and 7 cost an agent, and 7 is narrow.

## 4. Collate -- what settles without waking anyone

Per place, in this order:

| condition | outcome |
| --- | --- |
| every mark `clean` | nothing. The place was READ, and that record is the coverage claim |
| `query`, scope-declaring shape | a BOUNDARY REPORT. It does not block the other roles |
| any other `query` | the chief |
| ONE substantive mark | TAKE IN |
| several, SAME sentence, same change | TAKE IN once. The roles agree |
| several, SAME sentence, differing | the chief |
| several, DIFFERENT sentences, edits disjoint | MERGE, three-way over the base |
| several, DIFFERENT sentences, edits overlap | the chief |

**MEASURED, round 2: 13 of 16 places settled here. 3 reached the chief.**

!! **THE SENTENCE IS THE KEY, NOT THE PLACE.** Two roles on one paragraph are in conflict only if
they rule on the SAME sentence; different sentences compose. Without a mark naming its sentence
the flow cannot tell a merge from a fight, and every multi-role place escalates.

!! **AND AGREEMENT CANNOT BE KEYED ON THE PROPOSED TEXT.** Two roles finding one defect write
different prose for the fix -- measured twice. Keying on `change` escalates the best-corroborated
findings.

! **A SCOPE DECLARATION MUST NOT BLOCK THE OTHER ROLES.** Measured: treating one as a question
let a single role veto three others and the docket fell from 12 alterations to 5. The SHAPE key
tells them apart; word-searching the reason does not.

## 5. The chief rules, and it must be able to execute

The chief writes a candidate for every escalation -- one role's text, a merge of two, or its own.

!! **MEASURED: two roles corrected one false usage line. One replacement RAN; the other exits 0
printing nothing, because the module it names has no `__main__` block.** Both read as plausible
and both cite real modules. Only running them told them apart.

## 6-7. Revise -- the ask, and the second review

The flow sends each escalated place back with:

    the place, and YOUR mark on it
    the ORIGINAL paragraph
    the PROPOSED replacement, and the chief's REASON for it
    the OTHER roles' claims -- their claims ONLY, never their reasoning

!! **ONLY THE ROLES THAT MARKED IT ARE ASKED.** A role that never marked the place raised no
objection and has nothing to be satisfied about.

!! **THEIR REASONS ARE WITHHELD ON PURPOSE.** A role needs to know someone else ruled on this
sentence -- that is what it needs to judge a merge. Handing over the ARGUMENT invites agreeing
with the argument instead of re-reading the code, which is the failure blind-parallel review
exists to prevent.

The role answers one question -- **does your finding still stand?**

    satisfied      -> the mark is taken in
    not satisfied  -> new marks, and it goes round
    overruled      -> the chief rules, after the loop

**MEASURED: 2 of 3 converged in one pass**, and the roles re-verified rather than deferring --
one re-traced a dispatch chain and re-grepped the tree before answering, and one declined an
invitation to widen its own finding on remit grounds.

!! **AND A REVISE PASS CAUGHT A REGRESSION THE FIX ITSELF INTRODUCED.** A round-2 finding was a
stale citation; the fix replaced it with a new false claim; the fixer verified its own fix with
the wrong predicate; a second role caught it in revise. **Nothing mechanical could have** -- the
reread passes, `prove_unchanged` passes, the suite passes. A green chain would have written a
fresh false claim into the file.

! **NOT RE-DERIVABLE HERE:** that sequence is read from the roles' answer text, which this
package does not carry.

## 8. Termination

    converged   the round produced no CLAIM the last round did not
    bounded     3 rounds, then the chief rules

! **Convergence is tested on the CLAIM SET, not the mark count.** A role re-wording one finding
has not moved, and a count can hold steady while two sides swap positions.

! Roy, 2026-08-27, on why a loop is ordinary rather than a failure: *"there are always several
full revise cycles in the business because humans also don't get the answer in the first go."*
**The bound exists to stop cleanly, not because a second pass means something went wrong.**

## 9-10. Alterations, and the net behind everything

The docket carries pages, each with its path, the sha it was read at, and its schedule of
alterations. `proof` re-reads every drafted page and proves the executable code unchanged.

!! **THE DESK CANNOT BE TRUSTED TO VALIDATE AN UPDATE, AND DOES NOT HAVE TO BE.** MEASURED: a
role returned an update that was a different paragraph with its comment markers gone. The flow
took it in mechanically. **The write chain refused it -- nothing drafted, source untouched.**

! **The chief drops such a mark and sends the finding back.** Repairing it is not the chain's
job; a chain that repaired it would be deciding what the reviewer meant.

## What sets the width of step 2

**COVERAGE, NOT CONSISTENCY** -- see [`measurements.md`](measurements.md). Two byte-identical runs
agree on 0.32 of their findings, and the disagreement is misses. Chasing agreement would select
for the shallow findings both passes happen to hit.

**SO FAN THE DETAILED ROLES OUT.** Roy, 2026-08-27: *"because block context is so detailed it may
need several agents to fan out the work so it doesn't start trying to simplify its work
wrongly."*
