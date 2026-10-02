# The test suite

**Invariants derived from the code, checked over real inputs.**

```bash
uv run pytest            # 873 passed, 1 skipped, 3 xfailed, 451 subtests, ~1.6s
                         # the skip needs symlinks; it runs where they exist.
                         # the subtest count moves with `TODO/`: three per open
                         # file, from `gates/test_todo_counts_agree.py`
```

## How it got here

Built overnight on 2026-08-25 as `shadow/`, deliberately **without reading the
suite it replaced**, then swapped in. Roy: *"Delete the old test suit put in the
new one."*

The old suite was 866 tests. Three changes on 2026-08-24 each broke something
real and were noticed by **zero** of them:

| what changed | tests that noticed |
| --- | --- |
| fences stopped being emitted to agents | 0 |
| eleven fields left the census row | 0 |
| `text` renamed, breaking EVERY finding | 0 |

One mechanism each time: **the fixtures were hand-authored in the shape the code
expected, by whoever wrote the code, so they could only confirm.** When the
contract moved, the fixtures did not -- and they went on supplying the old
fields and asserting the old contract was met. That is not 866 independent
tests; it is one assumption restated 866 times.

## What is different

**218 test functions, collected as 877 tests.** A small set of invariants, each
checked over many real inputs -- rather than one test per remembered incident.

- **Nothing is hand-built where the system can build it.** Pages come from
  `page_for` over real source; binders from `bind`. A literal appears only in a
  refusal case, where malformed IS the input.
- **Every asserted value was OBSERVED first**, by running the code and looking.
- **Completeness is asserted.** Every galley case names the exact set of places
  allowed to differ, so an edit that also disturbed a neighbour fails even
  though its own place is right.

## The files

| file | what it holds to |
| --- | --- |
| `test_reading.py` | a file becomes a page -- partition, ordering, addresses |
| `test_addressing.py` | the naming scheme, and the series definition |
| `test_binder.py` | reading -> binder: what an agent is handed |
| `test_galley.py` | page -> galley: every cue type x every operation |
| `test_compositor.py` | page -> compositor: 54 forms, in equals out |
| `gates/` | does a GATE still bite -- the build, the release, the floor |

`gates/` is the part of the old suite that survived, because it asks a different
question: it tests `scripts/` and the release rather than the code under
redesign.

## Two chains, and they are independent

Roy, 2026-08-25: *"Reading -> binder. Page -> galley -> compositor. The binder is
not going through the galley."* The write path re-reads each page from disk,
because it needs the FULL page -- fences included -- and none of what a binder
carries.

## What is deliberately NOT tested

- **The desk, the verdicts, the record.** Roy: *"There is code there none of it is
  correct so testing it is solidifying wrong."* That code now lives in
  `prototype/`.
- **The front-matter/`b` collision** -- a file whose front matter is not on line
  1. A ruled normalisation; a test over it would pin the sacrifice.

## The update matrix

`test_galley.py` covers **every series x every operation**, discovering the
target cue from the page rather than hardcoding it:

| | `a` | `b` | `c` | `f` |
| --- | --- | --- | --- | --- |
| modify a filled place | yes | yes | yes | yes |
| drop it (empty string) | yes | yes | yes | yes |
| add to an ABSENT place | yes | yes | yes | yes |

Each asserts the place changed **and that nothing else did** -- including the
fences, which have their own rule: a drop vacates the fence it owns, and a `c`
owns none.

## Does it catch more?

Measured by mutating the source and running both suites while both existed.
`tests/` was mid-refactor and already red, so only the DELTA counts.

| mutation | old | new |
| --- | --- | --- |
| the binder drops `kind` from every row | +0 | **+2** |
| the binder repeats `path` on every row | +0 | **+2** |
| a `c` drop vacates leading it does not own | +0 | **+2** |
| line endings always LF | +3 | +7 |
| the trailing newline is always added | +2 | +4 |
| a non-text replacement is accepted | +5 | +12 |

Three defects only this suite catches, and they are exactly the class that broke
on 2026-08-24.

## The turn's checks, each caught by one mutation

Measured 2026-09-04 on `feat/the-mark-and-the-collator` after SP-4, P9: one
exact-string mutation per check, the module's own test file run, the source
restored from memory. A missed row was a finding; the one found became a test.

**The mutation run is of its date, and the modules it ran over are gone.** The
old middle was deleted 2026-09-18 (`0e2ff82a`), taking `desk/determined.py`,
`desk/diff_mark.py`, `flows/collate.py`, `flows/turn.py` and their four test
files with it. **What the checks ASK survives the rebuild**, so the table is
kept and re-pointed: each row names where that question is settled now and the
test read to confirm it. **Nothing here claims a mutation was re-run against
the new modules.** Re-running it means one exact-string mutation per row
against the module in the middle column, and it is the way to find out whether
a row's new home really bites -- which is a measurement this table would then
carry its own date for.

| what the check asks | settled now in | read to confirm |
| --- | --- | --- |
| a role's answer is refused by name | `desk/proof/answer.py` | `test_answers.py::test_an_answer_is_read_against_its_question` -- `clean` under an escalation gives "not an answer to an escalation" |
| the chief's own ruling refuses a role's answer name | `desk/proof/disposition.py` | `test_dispositions.py::test_a_disposition_is_read_by_name` -- `correct` gives "a role's answer" |
| a null mark stands only for the original | `desk/dispositions/table.py` | `test_dispositions.py::test_taken_in_closes_a_carried_place_with_one_sides_text_or_the_original` -- the `original` side sets `None`, and `test_disposition_command.py::test_a_taken_in_of_the_original_writes_no_entry` is the same through the command |
| correct and patch owe a change | `desk/proof/answer.py` | `test_answers.py::test_the_escalation_answers` (the `owes_change` flags) and `::test_an_answer_is_read_against_its_question` (a `correct` with none gives "needs a `change`") |
| a query answer owes the shape its effect reads | `desk/proof/answer.py` | `test_answers.py::test_a_query_answer_with_no_shape_is_refused_rather_than_read_as_deferring` |
| an unanswered slot is refused, not read as a withdraw | `flows/answers.py` | `test_turn_command.py::test_an_unanswered_slot_is_BROKEN_and_nothing_is_written` and `::test_a_slot_left_unanswered_beside_an_answered_one_is_BROKEN` |
| a role that was asked and returned nothing is refused | `flows/bus.py` | `test_bus.py::test_a_role_that_was_asked_and_answered_nothing_is_refused` |
| an address never sent is refused | `flows/bus.py` | `test_bus.py::test_an_answer_at_a_place_no_turn_carried_is_refused` and `::test_an_answer_from_a_role_the_place_was_not_put_to_is_refused` |
| a place an earlier fold settled is not re-opened | `desk/evaluate/passes.py` | `test_turn_command.py::TestOnceSettledAlwaysSettled::test_a_place_the_first_fold_settled_still_reads_the_same_after_a_turn` -- across two processes, the place is derived again from the same marks |
| the chief's close refuses an unruled place | `flows/bus.py` | `test_disposition_command.py::TestRefusals::test_an_unruled_place_is_BROKEN_naming_it_and_its_roles` |
| agreement needs byte-identical text | `desk/evaluate/passes.py` | `test_passes.py::test_two_proposals_of_one_text_agree` against `::test_two_proposals_on_one_sentence_contest` |
| a lone mark goes back to the roles that read the page | `desk/evaluate/passes.py` | `test_passes.py::TestATextEveryReaderMustHaveSeen::test_a_lone_correct_against_three_cleans_is_composed_and_asked_of_them` |
| a human-review query refuses a place that would have resolved | `desk/evaluate/passes.py` | `test_passes.py::test_a_human_review_query_refuses_the_place_whatever_else_is_there` |
| a deferring query's role is out of the place | `desk/marks/table.py` | `test_marks_table.py::test_only_a_deferring_query_defers` and `test_passes.py::TestATextEveryReaderMustHaveSeen::test_a_role_that_filed_only_a_query_is_not_waited_on` |
| check exits BROKEN on a refused answer | `commands/check.py` | `test_check_command.py::TestABatchIsHeldToWhatTheTurnRefuses::test_what_the_turn_refuses_is_named_here_too` |
| check exits BROKEN on a place left alone | `commands/check.py` | `test_check_command.py::TestACopy::test_a_place_left_alone_is_named` |

## The three xfails are a tripwire

`go`, `ruby` and `lua` place a declaration's documentation at an `a` cue and type
it `comment` -- the `b` series' kind. Held as **strict** xfails, so fixing it
turns them red and demands their removal rather than leaving them green and
forgotten. Filed as `TODO/a-doc-comment-is-cued-a-and-typed-b.md`.
