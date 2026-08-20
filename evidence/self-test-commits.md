# Commits this system can be graded against

**A fixture is a CHECKOUT AT A HASH, and a fix commit is an ANSWER KEY.** Ruled in
[`the-harness-cannot-run-the-system-it-grades`](../TODO/the-harness-cannot-run-the-system-it-grades.md):
this repo's own history is a fixture source, because the commit that fixes a prose defect says
what the defect was and what the correct prose is.

!! **THESE ARE PROSE DEFECTS, WHICH IS WHAT THIS SYSTEM IS FOR.** Not one of them broke a test.
The suite was green through every one -- 672 to 713 passing continuously -- and the gates were
green too. Each was found by a person READING, which is the whole claim in `CLAUDE.md`: *a green
gate is not evidence of a good result.*

! **How to use one.** `git diff <commit>^{} <commit>^{}~1` gives the tree before the fix; run
`/comment-review` over the files it touches and grade the run from its DIFF against what the
commit actually changed. ! The tags are annotated, so `^{}` is needed wherever a commit is
wanted.

## The range

`3af9752..93cc4b0`, branch `fix/folio-placement-is-not-where-the-anchor-is`, 2026-08-19 to
2026-08-20. Twenty-one commits.

## What each is an answer key FOR

| commit | the defect a reader found | the class |
| --- | --- | --- |
| `19a301c` | five sentences let a reader compute a folio from a line's ordinal, and they **disagreed with each other** -- `b8` read "after the seventh" in a test and `b7` read "after the seventh" in the module it tests. Nine more taught that an `a` anchor is a NAME when the code had carried the LINE since the morning | a claim about the code that the code contradicts |
| `791b32b` | **six terms carried a definition in two files**, and the two copies of `anchor` disagreed -- roles were handed one, humans read the other. The doc's own header said this could not happen | one fact, two sources |
| `44d8684` | the thing was called a `pCST` and every file that said so spent a paragraph apologising for it not being a syntax tree | a name that is not the thing |
| `93cc4b0` | `addresser.py` addressed nothing -- the address is composed in `page.py` | the same, one module over |
| `2cd5365` | **a plan box was ticked on work that was not done.** The claim passed a green suite because nothing shipped called the functions it said were deleted | a green gate answering a different question |
| `b342cd1` | anchoring ran in one function and addressing in another, so **every test that called `census_for` directly got half a census** and nothing said so | two passes over one fact |
| `9293806` | `b0` and `b1` were mutually exclusive on all five file shapes, so the place an `add` exists to cite was unreachable on any file with a licence header | a rule that holds only where it was measured |

## Three that are worth more than the rest

!! **`2cd5365` -- THE FALSE TICK.** The plan's own gate section says a box must be re-derivable by
someone who did none of the work. This one was ticked by its author, who had not re-derived it.
It is the cheapest possible demonstration that the checkbox is not the evidence.

!! **`9293806` -- THE PIN THAT FIRED.** `tests/test_edge_cases.py` carried an
`@unittest.expectedFailure` on `b0`, so unittest reported an UNEXPECTED SUCCESS the moment the
defect was fixed. A skip would have stayed silent. **That is a pattern worth reusing**: a known
defect pinned as an expected failure cannot be quietly left ticked-or-not.

!! **`f4f1a98` -- THE FIXTURE THAT FOUND MOST OF IT.**
`tests/fixtures/python_edge_cases.md` is twelve `add` marks over every series at every nesting
level, written by hand. It found more in one run than three sessions of reading did, and the test
reads the DOCUMENT as its source so the two cannot drift.

## What is NOT here

! **No measurement of the reviewers themselves.** Every defect above was found by a human reading
or by a probe written for the occasion; none was found by `/comment-review`. Running the system
over these commits is the point of recording them, and it has not been done --
`the-harness-cannot-run-the-system-it-grades` is 6/20 and is what blocks it.

! **`evals/grade_hazards.py` grades from the DIFF, never from a run's own report.** Self-reported
confidence has been measured not to discriminate real findings from fabricated ones.
