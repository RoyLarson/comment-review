# September review: TODO coverage and handoff

Reviewed on 2026-09-30 against HEAD fc1408a1 on
feat/the-middle-rebuilt. Source: .tmp/code-review-2026-09-27/09-merged.md
and its cited individual reports. Three independent reviewers traced the
findings through current code, existing goals, tests and recorded decisions.

## Result and scope

The source has seven numbered roots. R1 and R5 were merged at 165bc64a and
282327e1 respectively. A focused check of the current move folding, proof
containers and proof command ran successfully: 101 tests passed using
`uv run pytest -q tests/test_move_ends_at_the_fold.py tests/test_containers.py tests/test_proof_command.py`.
That check supports the completed implementation; it does not claim all
related backlog goals are finished. The remaining move origin/rewrap goals
and middle-side Binder boundary remain explicitly open.

R2, R3, R4, R6 and R7 had partial or missing goal coverage. Existing TODO
subjects already own the work, so goals were added there rather than creating
duplicate root files. Job-board wrote all tasks and notes. Existing labels,
IDs and completion marks were retained. No plan, repair, task closure or
commit was made.

There is no numbered R8 in the identified list. The unnumbered standalone
findings were included in the coverage review as the working interpretation
of Roy's uncertain reference. They are labeled standalone throughout these
records. The scope clarification remains open if Roy intended another list.

## Filed goals and detailed acceptance

Each linked report supplies the goals, current file/line evidence, necessary
changes, dependencies, acceptance cases and runnable completion checks.
New regression nodes are explicitly FUTURE; their names do not claim tests
already exist or pass. The reports retain proposed labels; allocated IDs
below are the final board association.

| Area | Owning TODO and new IDs | Detailed review |
| --- | --- | --- |
| R2: seal query admission and remove the obsolete lifecycle | [human-questions-before-the-fold](../../TODO/human-questions-before-the-fold.md) T8; [rebuilt-middle-final-review](../../TODO/rebuilt-middle-final-review.md) T47 | [R2-A through R2-C](2026-09-30-r2-r3.md) |
| R3: compose equal operations and convergent filings; relinquish deferred sides; exhaustively handle answer effects | [rebuilt-middle-final-review](../../TODO/rebuilt-middle-final-review.md) T48-T51 | [R3-A through R3-D](2026-09-30-r2-r3.md) |
| R4: source shape, unique quoted statement, complete headers, per-language rewrap | [mark-defects](../../TODO/mark-defects.md) T29-T32 | [R4 A, B, C, F](2026-09-30-r4.md) |
| R4: generated chief ruling contract and remaining answer-payload decision | [the-chief-has-no-recast-workflow](../../TODO/the-chief-has-no-recast-workflow.md) T13-T14 | [R4 D and Genuine ruling](2026-09-30-r4.md) |
| R6: complete readable chief result, source-free/anchorless cases, chief reason | [collate-flow-defects](../../TODO/collate-flow-defects.md) T17-T19, T23 | [R6 items 1-3 and 5](2026-09-30-r6-r7-r8.md) |
| R6: reject undecided synthesis input | [rebuilt-middle-final-review](../../TODO/rebuilt-middle-final-review.md) T52 | [R6 item 4](2026-09-30-r6-r7-r8.md) |
| R7: duplicate rulings/answers, exact human-question identity, all anchor provenance | [collate-flow-defects](../../TODO/collate-flow-defects.md) T20-T22, T24 | [R7 items 6-9](2026-09-30-r6-r7-r8.md) |
| Standalone: literal topology paths | [staged-chain-untested](../../TODO/staged-chain-untested.md) T6 | [Standalone 06:3](2026-09-30-r6-r7-r8.md) |
| Standalone: withdrawal respects stage dealing | [mark-defects](../../TODO/mark-defects.md) T33 | [Standalone 06:6](2026-09-30-r6-r7-r8.md) |
| Standalone: unfinished sketch stays outside shipped code | [external-address-cites-dead-modules](../../TODO/external-address-cites-dead-modules.md) T2 | [Standalone 07:6](2026-09-30-r6-r7-r8.md) |
| Standalone: chief overrides are printed as rulings | [collate-command-defects](../../TODO/collate-command-defects.md) T23 | [Standalone 03:6](2026-09-30-r6-r7-r8.md) |
| Standalone: current flow map and docstrings | [collate-flow-defects](../../TODO/collate-flow-defects.md) T25 | [Standalone false commentary](2026-09-30-r6-r7-r8.md) |

These are 26 new goals: 25 implementation goals and one decision goal.
They reside in eight existing TODO files. No source finding was treated as
unresolved solely because the September 27 report predates the typed records.
R4's ledger identifies the findings already resolved or overtaken by
Processes 204 and 206.

## Existing goals strengthened

Ten existing goals received references to exact evidence or acceptance:

- human-questions-before-the-fold T6, T7: coordinated cleanup and pre-fold
  single-copy refusal, including no-output checks.
- rebuilt-middle-final-review T17, T22, T25, T30, T46: dead Row.answers,
  synthesis ownership, the obsolete unsettlable-side goal, already-decided
  chief-copy purpose, and event documentation.
- move-is-a-composite-mark T38, T50: current typed move origin behavior,
  word-based snippet location and shared per-language rewrap checks.
- the-chief-has-no-recast-workflow T2: recast prose does not depend on a
  supplied role side that its setter does not use.

T30 remains a legacy open decision box, with a note that Process 184 already
settles purpose and collate-flow-defects T17 owns the implementation gap.
T25 conflicts with Process 197. A later approved repair must reconcile these
legacy boxes through evidence-backed supersession or closure. Filing did not
rewrite them or invent a completion commit.

## Design constraints and open decisions

R3 repairs equal edit operations; it does not silently change Process 124's
reader-acceptance/escalation behavior. Distinct insertions without a decided
order remain conflicts. A supported two-move retry retains both origin
filings and uses a shared resulting arrival paragraph.

R7 validates anchor provenance from the returned records before a dictionary
can erase it. It does not authorize new middle-side page reads or page-drift
checks. Preserve the write-end anchor authority in Process 134.

R6's readable record must honor Process 184 without fabricating source
evidence or anchors. Compare repairing ordinary-mark synthesis with an
appropriate resolved-record representation during the repair design. The
authoritative write input remains the closed proof.

The generated chief contract goal has an agents-lane dependency for consuming
the runtime contract in SKILL.md. No agent instructions were edited here.
Language marker definitions stay with their language owner; drop and move
remainder should consume one suitable rewrap service. Existing machine-boundary
goals under Process 207 own the movement of pure composition helpers.

The remaining explicit ruling is chief-workflow T14: should correct/patch
turn answers require initial-mark claims and evidence, or retain their current
change payload? Type ownership under Process 206 does not answer that semantic
question. Source-entry validation can proceed independently of making sources
mandatory on every answer.

Standalone plan steps P19-P24 already exist on 0.2.4-the-middle-rebuilt.
The scratch report's claim that move T50 is unplanned is stale. Missing TODO
goals were filed during the coverage review. Roy subsequently requested
adding all 26 goals to that plan; the plan associations are now recorded
through job-board. Its existing execution steps remain at 24.

## Verification and handoff

The initial board audit reported zero integrity issues, zero excluded files
and zero resync changes. It also reported pre-existing format/migration
warnings across the older backlog. Those warnings do not justify silently
migrating this board during a scoped filing review.

Final `job-board audit --check` still exits 1 for format/migration warnings;
its integrity, excluded-file and resync-change sections each report zero.
`git diff --check` passes. The production/test/plugin/plan diff check is empty.
The final coverage document's relative links resolve, and the TODO diff
contains exactly 26 added task rows. The review files were also checked for
trailing whitespace.

Done: source-to-goal coverage reviewed, missing goals filed, existing coverage
strengthened, and detailed future completion checks preserved.
Blocked: no filing work; implementation awaits its normal approved plan and
any design decisions governing the chosen repair.
Open questions: R8 identification and the recorded answer-payload ruling.

Files touched: TODO/README.md and the eight owning TODO files in the table,
plus move-is-a-composite-mark.md (supporting notes only), and the four review
files in docs/reviews/. Source, tests, generated plugins, plans and live
settings were unchanged during the coverage review. All changes are left
uncommitted for Roy's review.

## Plan association follow-up, 2026-09-30

Roy requested: "Add the 26 missing todo goals to this plan".
All 26 owning TODO task references in the table above were added to
[0.2.4-the-middle-rebuilt](../plans/0.2.4-the-middle-rebuilt.md) through
`job-board plan add-t`, followed by `plan refresh`.

Verification: `job-board plan show 0.2.4-the-middle-rebuilt` reports 47 of 74
TODO tasks closed, compared with 47 of 48 before the association. The 26
added rows retain their owning task IDs and marks. Chief-workflow T14 retains
its ruling flag, which makes the plan decision-needed. Its existing 24 plan
steps retain their IDs and completion state. `git diff --check` passes.

Done: all requested goals associated with the plan and its index refreshed.
Open: the recorded answer-payload decision and the plan's unfinished work.
Files touched in this follow-up: docs/plans/0.2.4-the-middle-rebuilt.md,
docs/plans/README.md and this handoff. These edits are also uncommitted.
