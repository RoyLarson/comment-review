# The join merges across a boundary it cannot read, and blames the neighbour

```
Status:   open
Progress: 0 of 4 tasks done
Owner:    session
Raised:   2026-08-17, after three defects of one shape landed in a single day
```

## Objective

**When `verdicts.py` cannot recognise a boundary it silently merges across it, and the
diagnostic then points at the correct work on the other side.** Roy named the class after the
third instance:

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

## Why it keeps happening

Two places decide a boundary, and both decide it by ELIMINATION -- if a thing is not recognised
as X, it is assumed to be a continuation of the last X:

- `parse_report`'s continuation branch. A line that is not a field label and not a new citation
  is appended to whatever came last. D7 and D8 both entered here.
- `removed_spans`' token diff. Tokens that cannot be aligned are absorbed into the surrounding
  span. D9 entered here.

**Elimination has no failure state.** There is no answer that means *I do not know what this
is*, so every unrecognised thing becomes its neighbour's problem.

## ! What is NOT established

- **That the shape can be changed cheaply.** A parser that names what it cannot read has to
  have somewhere to put it -- a fourth outcome alongside field, citation and continuation --
  and every caller has to handle it.
- **That three is enough to act on.** Three instances in one file in one day is a count, not a
  proof that a fourth is coming. The rule recorded in `verdicts.py` is deliberately conditional:
  a fourth is a reason to change the shape.

## Tasks

- [ ] **Give the continuation branch a fourth outcome: UNRECOGNISED.** A line that is neither a
      label, nor a citation, nor a plausible continuation is collected and REPORTED with its
      line, rather than appended. ! The bar is what makes this hard -- a wrapped verbatim half
      is a legitimate unrecognisable line, so the rule cannot be "anything I cannot parse".

- [ ] **Say what `removed_spans` does with a token it cannot align.** Today it absorbs it. The
      alternative is to report the span as unreliable and let `edit_problem` refuse with a
      message that names the alignment failure instead of the innocent word.

- [ ] **Add a test that asserts the ERROR NAMES THE RIGHT THING**, not merely that an error
      occurred. All three defects passed their existing tests: something was refused, and the
      tests checked that it was. ! This is the check that would have caught the class.

- [ ] **Record the corroboration rule.** What separated D9 from reviewer error was that
      `block-context` had implemented its own single-edit checker and PASSED the record this
      gate refused. Two implementations of one question disagreeing is worth running down; a
      reviewer disagreeing with the gate alone is not. ! Nothing in the shipped tree says this,
      and it is how a tool defect is told from sloppiness.

## Related

- [`re-review-is-ordered-everywhere-and-defined-nowhere`](completed/re-review-is-ordered-everywhere-and-defined-nowhere.md)
  -- a refused record is what sends a block back, so a wrong refusal spends a whole round.
