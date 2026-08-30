# The grader reads one file, and three of the four keyed cases are multi-file

```
Status:   open
Progress: 0 of 2 tasks done
Owner:    testing
Requires-Roy: true
Raised:   2026-08-30 (found staging the four keyed cases and probing the grader pre-
          flight on each)
```

## Objective

`evals/reread.py` takes ONE `--under-review` path. An END diff covers every file
its case names. **Three of the four keyed cases are multi-file**, so the key and
the artifact describe different things.

!! **MEASURED 2026-08-30, AND THE PRE-FLIGHT PASSED ALL FOUR.** The six-file case
`block-context-six-citations-name-the-wrong-module` went through every gate in
front of the paid call while handing the judge `desk.py` and a key covering
`held.py`, `lexer.py`, `page.py`, `record.py` and `verdicts.py` as well. Nothing
disagreed, because nothing compared the two.

| case | files | gradeable today |
| --- | --- | --- |
| `a-caller-list-that-names-four-of-seven` | 1 | **yes** |
| `a-worked-example-the-signature-outran` | 2 | no |
| `ownership-context-a-comment-390-lines-from-its-subject` | 2 | no |
| `block-context-six-citations-name-the-wrong-module` | 6 | no |

!! **WHAT IT WOULD HAVE COST IS A GRADE THAT READS AS A BAD REVIEWER.**
`detection` is *what fraction of the key did the run find*, so five files of
unfindable key drag it toward F -- and nothing in the output says the judge was
never shown them. ! `unkeyed` is not spared either: it rules a finding outside
the key against the CODE, and the code for those files is absent too.

! **A GUARD LANDED 2026-08-30 AND REFUSES THE MISMATCH** -- `reread._unshown`,
naming every unshown file and the price. **That makes the failure loud; it does
not make the three cases runnable.** ! It was refused rather than TRIMMED: cutting
the key to the one file shown would grade a different case than the row
describes, under the row's name.

! **THE ALREADY-GRADED CASE IS UNAFFECTED**, checked: `97359c27 -> 476def7a`
touches one file, so the guard is silent on it and the T50 measurement stands.

!! **THE OPEN QUESTION IS WHAT A READING IS, AND IT HAS A PRICE ATTACHED.** One
reading over a case's whole file set matches what a real `comment-review` run
does -- the roles walk a page set, and `ownership-context` in particular decides
placement ACROSS files, which one file cannot exercise. One reading per file
keeps T50's *grade ONE artifact twice* shape and stays cheap. At about $0.68 a
reading measured, a six-file case is a different order of spend either way.

## Tasks

- [ ] Does a multi-file case get ONE reading over its whole file set, or one
      reading per file against a split key? The first matches a real run and
      exercises cross-file placement; the second keeps the one-artifact shape and
      stays cheap. Verify: the answer is written into this file.
- [ ] Implement whichever the answer is, so a multi-file case is gradeable.
      Verify: all four keyed cases pass reread.inspect with no problems, and the
      six-file case runs as a single command.
