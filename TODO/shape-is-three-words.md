# `shape` names three different things, and the axis may not be query's alone

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-28 (2026-08-28, Roy asking what `claim.shape` is: 'because it is
          ambiguous. Also why is it specific to query mark? Why isn't part of the other
          enum candidates? Why "shape" why not a better word?')
```

## Objective

`shape` names three different things, and the axis may not be query's alone.

## Tasks

- [ ] RULE the word. `shape` means THREE things in this tree, none declared: the
      STRUCTURE of a mark (`docs/the-mark.md:1`, `mark --shape`,
      `tests/gates/test_mark_shape.py`); a QUERY'S KIND (`claim.shape`,
      `QUERY_SHAPES`, instructed at `comment-review-module-context.md:108`); and
      THE FORM A CLASSIFIER TAKES (`the-mark.md:171`). Verify: the ruling names
      which sense keeps the word and `docs/vocabulary.md` declares the others.
- [ ] RULE whether the axis is `query`'s alone. MEASURED 2026-08-28: `clean` and
      `query` are EXACTLY the two instructions with `owes_change=False` -- the two
      that propose no text -- and only `query` carries a sub-category. `docs/the-
      mark.md` already records the unfilled need on the other: four roles asked
      for it in four forms and all landed as `clean`, 'which asserts one thing and
      was used for four'. Roy, 2026-08-26: 'If it is anything it is a field on
      `clean`.' Verify: the answer says whether the two share one axis or hold
      two, and `docs/the-mark.md` states it.
- [ ] Name it for WHAT IT DOES. `decision-log.md Process: #33` keyed the three on
      WHO RESOLVES IT, replacing an axis about where evidence lives -- so the
      field says whom the query is FOR, which is also how publishing names one (an
      *author query* is named by who answers it). Verify: the candidate is checked
      against the register BEFORE it is proposed, per `docs/vocabulary.md`, and
      the reasoning is recorded whichever way it goes.
- [ ] Carry the ruling into the enum sweep. T1.15 of the 0.2.4 plan lists
      `QUERY_SHAPES` as a closed set to make a `StrEnum`; if the axis generalises,
      the enum is not query's. Verify: T1.15 names the right set, and no site
      hand-writes the values.
- [ ] Carry it into the agent-facing prose in the SAME change. The field name is
      published in `reviewer-brief.md` and instructed at `comment-review-module-
      context.md:108`. Verify: `grep -rn` finds no shipped file using a retired
      sense, and `check_vocabulary.py` passes.
