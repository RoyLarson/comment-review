# The join merges across a boundary it cannot read, and blames the neighbour

```
Status:   in-progress
Progress: 2 of 4 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-17, after three defects of one shape landed in a single day
Triaged:  2026-08-23 -- the text reader is retired, so D7 and D8's entry point no longer
          exists; D9's does. The corroboration rule is in the shipped tree
SPLIT:    2026-08-23 -- no box held two tasks; four boxes stay four. The two closed boxes
          carried the reasoning that keeps them legible, and it moved into the Objective.
```

## Objective

**When the join cannot recognise a boundary it silently merges across it, and the diagnostic then
points at the correct work on the other side.** Roy named the class after the third instance:

| | what merged | what the error blamed |
| --- | --- | --- |
| **D7** | a malformed `SOURCES` citation into the valid entry above it | that valid citation, for a verbatim half it could no longer find |
| **D8** | a bare field label into the field above it | a correct `SOURCES` entry, same way |
| **D9** | a dropped span into the punctuation beside it | a correct edit, for naming prose its `CLAIM` does not mention |

!! **D9 came in TWO shapes and the second one had no legal expression at all.** First a trailing
`.` re-attaching to the previous word; then markdown emphasis, where the span reads
`*"a wrap ... defect"*`. That span comes from the FILE and carries the file's markup, so **no
wording of the claim could match it** -- measured both ways, cleanly quoted and quoted with the
delimiters, and both refused.

!! **The reviewer reshaped a sound finding twice to route around it**, moving its ruling onto a
differently-bounded span to avoid characters the checker mishandled. **A reviewer contorting its
judgement to satisfy a mechanical defect is CONSERVATIVE ON MEANING, FREE ON FORM failing from
the tooling side** -- the gate was deciding what could be FOUND rather than whether it was true.
That is the cost this class charges, and it does not show up as a refused record.

!! **This is the most expensive kind of diagnostic there is**, because it sends the reader to
fix something that is not broken. Every one of the three cost a session real time on the wrong
record before the tool was suspected at all.

! **D7 was fixed for citations specifically, and the class survived to produce D8 and D9.**
That is the reason this file exists rather than three closed entries: each fix was correct and
none of them addressed the shape.

## Where the two boundary decisions live now, measured 2026-08-23

Both places decided a boundary by ELIMINATION -- if a thing is not recognised as X, it is assumed
to be a continuation of the last X. **Elimination has no failure state:** there is no answer that
means *I do not know what this is*, so every unrecognised thing becomes its neighbour's problem.

- **`parse_report`'s continuation branch is GONE.** The text reader was retired; `docs/history.md:178`
  records `held.parse_report`, `held.convert`, `held.code_concerns` and `held.claim_object` as
  removed. `held.py:10-14` states the rule that removed it: *"IT READS ONE SHAPE. A reader kept for
  an older one is a shim."* A record is JSON, so there is no line to append to a previous line, and
  D7's and D8's entry point cannot recur in that form.
- **`removed_spans`' token diff is LIVE**, and it moved to `desk.py:775-837`. It aligns two token
  lists with `difflib.SequenceMatcher` and returns every `delete` and `replace` opcode as a removed
  span. **A token it cannot align is still absorbed into the surrounding span**; there is no
  opcode, and no return value, that means "cannot align".

! **THE OUTCOME ALREADY EXISTS AND THE ALIGNMENT FAILURE DOES NOT REACH IT.** `removed_spans`
has a "cannot compare" channel -- it returns `None`, and `desk.py:793-796` tells callers to
treat that as *cannot compare*, never as *nothing removed*. The alternative to absorbing the
token is to report the span as unreliable and let `edit_problem` refuse with a message that
names the alignment failure instead of the innocent word.

## ! What is NOT established

- **That the shape can be changed cheaply.** A parser that names what it cannot read has to
  have somewhere to put it -- an outcome alongside the ones it already has -- and every caller has
  to handle it.
- **That three is enough to act on.** Three instances in one file in one day is a count, not a
  proof that a fourth is coming. The rule recorded in `verdicts.py:57-60` is deliberately
  conditional: *"A fourth is a reason to change the SHAPE of the boundary decision, not to add a
  fourth case."*

## What the two closed boxes recorded

**SUPERSEDED, and worth keeping legible.** *"Give the continuation branch a fourth outcome:
UNRECOGNISED"* named a branch that no longer exists -- `parse_report` was retired with the text
record format (`docs/history.md:178`), and `held.load_report` reads JSON only. The task was
right about the SHAPE and is closed by removal rather than by fix, **which matters because the
same argument still applies to `removed_spans`, where the elimination is still there.**

**FINISHED: the corroboration rule is in the shipped tree at `verdicts.py:62-65`:** *"What
separated D9 from reviewer error was CORROBORATION: `block-context` had implemented its own
single-edit checker and passed the record this gate refused. Two implementations of 'did the
edit match the claim' disagreeing is worth running down."* ! That is how a tool defect is told
from sloppiness, and a reviewer disagreeing with the gate ALONE is not it.

## Tasks

- [x] T1 -- SUPERSEDED, not a task. The continuation branch it named was retired with the
      text record format. Kept in the Objective.
- [ ] T2 -- Say what `removed_spans` does with a token it cannot align; today
      `desk.py:831-837` absorbs it. Verify: the message names the alignment, not a word.
- [ ] T3 -- Add a test asserting the ERROR NAMES THE RIGHT THING, not merely that one
      occurred. Verify: a test in `tests/test_verdicts.py` fails if a neighbour is named.
- [x] T4 -- FINISHED. The corroboration rule ships at `verdicts.py:62-65`. Kept in the
      Objective.
## Related

- [`re-review-is-ordered-everywhere-and-defined-nowhere`](completed/re-review-is-ordered-everywhere-and-defined-nowhere.md)
  -- a refused record is what sends a paragraph back, so a wrong refusal spends a whole round.
- [`the-bridge-landed-and-the-rewrite-did-not`](the-bridge-landed-and-the-rewrite-did-not.md)
  -- the generate-then-reparse that is still inside one module, which is the same class one level
  in.
