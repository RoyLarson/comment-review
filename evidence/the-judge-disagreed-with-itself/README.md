# The judge disagreed with itself -- the first graded reading, 2026-08-29

**The same judge read the same artifact twice and returned different letters on two of the
three fields it could grade.** That is `TODO/the-harness-cannot-run-the-system-it-grades`
**T50** -- *is the perception stable?* -- getting its first answer, and the answer is **no, not
at n=2**.

! **THIS IS NOT A VERDICT ON THE INSTRUMENT.** `decision-log.md Process: #56`, Roy 2026-08-29:
*"just because there is variance in the result doesn't make the measure invalid it makes it
uncertain. A repeat or three or four or five off the same result fixes the variance."*
**Variance is reducible by N; validity is not.** What this fixes is the sample size a later
calibration needs -- it says nothing about whether the grades are RIGHT.

## What was graded

| | |
| --- | --- |
| artifact | [`../harness-first-two-arm-run/arms/with_skill/findings.md`](../harness-first-two-arm-run/arms/with_skill/findings.md) |
| case | `a-docstring-never-matches-its-own-file`, arm `with_skill` |
| file under review | `plugins/.../scripts/galley.py` at **START `1ad4ba72`** |
| END | **none** -- and that is the limitation below |
| judge | `claude-opus-5`, an exact id, never a family alias |
| rubric | **v2** (`unkeyed` replacing the invalid `restraint`) |
| readings | 2 |
| cost | **$0.61** |

! **NO REVIEWER WAS RE-RUN.** Both readings grade one stored `findings.md`, so a disagreement
is the judge's alone and cannot be a difference in what was filed.

## What it returned

```
detection      --  N/A N/A  (not graded)
diagnosis      --  N/A N/A  (not graded)
prescription   --  N/A N/A  (not graded)
unkeyed        !=  A B
evidence       !=  B A
overall        ==  B B

agreed: False  over 3 of 6 fields, 2 readings
```

**Two of the three measurable fields moved. The overall held.** Full letters, both judges'
reasons, the rubric version and the model id are in [`t50.json`](t50.json) -- the reason is the
data (`Process: #56`), so a letter alone was never enough to keep.

!! **THREE FIELDS ARE VACUOUS, AND THE RUN COULD NOT HAVE MEASURED THEM.** `detection`,
`diagnosis` and `prescription` are all scored against the answer key, and this case supplies
none. The judge said so in both readings -- *"No END commit and no diff were supplied, so there
is no set of changed paragraphs against which to test coverage."* **A run on a keyed case is
what exercises them**, and none had been done when this was taken.

## The two defects it bought

!! **THE COMPARISON WAS COUNTING THE VACUOUS FIELDS AS AGREEMENT.** `reread.compare` returned
`agreed: True` for an axis both readings scored `N/A`, so **three vacuous holds outvoted two
real disagreements** and the tool reported stability it had not observed. **A field that cannot
vary cannot disagree** -- which is [`docs/gates.md`](../../docs/gates.md)'s own case (*"does the
check pass" is not the question; "could the check fail" is*) arriving from inside the instrument
built to measure it, exactly as the 699/699 round trip did. ! Fixed the same day: an unmeasured
field reports `agreed: None`, prints `--  (not graded)`, and the verdict carries its
denominator.

! **AND THE CASE WAS THE WRONG ONE TO SPEND ON.** The missing END had been noted twice before
the command was handed over, and the run still bought **one axis of stability at the price of
five**. `evals/reread.py` now REFUSES a keyless case unless `--allow-no-end` says the caller
means it, and the refusal names the price.

## How to re-derive it

The stored readings are enough -- recomputing the comparison costs nothing:

```bash
uv run python -c "
import json, sys; sys.path.insert(0, 'evals'); import reread
d = json.load(open('evidence/the-judge-disagreed-with-itself/t50.json', encoding='utf-8'))
print(json.dumps(reread.compare([r['editorial'] for r in d['readings']]), indent=2))
"
```

A NEW reading is a fresh API call and is **Roy's to run** -- see
[`docs/conventions.md`](../../docs/conventions.md), *The grader costs money, and only Roy runs
it*. The invocation was:

```
uv run python evals/reread.py \
  --findings evidence/harness-first-two-arm-run/arms/with_skill/findings.md \
  --under-review <galley.py at 1ad4ba72> \
  --start 1ad4ba72 --arm with_skill \
  --eval-id a-docstring-never-matches-its-own-file \
  --runs 2 --out <path> --allow-no-end
```

! `--allow-no-end` did not exist when this was taken; the guard was added because of it.

## What it does not settle

- **Whether either grade is right.** Neither reading's letters were checked against the code.
- **The rate.** Two readings is an anecdote, not a variance -- the same caveat
  [`a-role-can-reverse-itself-between-runs`](../../TODO/a-role-can-reverse-itself-between-runs.md)
  records for the reversal it raised.
- **Anything about `detection`, `diagnosis` or `prescription`**, which were never graded.
- **T50 is therefore still open.** It closes on a run over a KEYED case, which
  [`evals/prose_commits.py`](../../evals/prose_commits.py) now finds -- 10 candidates whose
  whole diff is prose, so the key carries no code half.
