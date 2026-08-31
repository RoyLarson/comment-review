# `shape` names three different things, and the axis may not be query's alone

```
Status:   open
Progress: 0 of 6 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-28 (2026-08-28, Roy asking what `claim.shape` is: 'because it is
          ambiguous. Also why is it specific to query mark? Why isn't part of the other
          enum candidates? Why "shape" why not a better word?')
```

## Objective

**One word, three jobs, none of them declared** -- and the middle one is the only one that
reaches an agent, as a field name it is instructed to fill.

| sense | where it is used |
| --- | --- |
| **the STRUCTURE of a mark** | `docs/the-mark.md:1` *"the shape, and the classifiers"*; `mark --shape`; `tests/gates/test_mark_shape.py` |
| **a QUERY'S KIND** | `claim.shape`, `QUERY_SHAPES`, and `comment-review-module-context.md:108`, which tells a role to set it |
| **the FORM A CLASSIFIER TAKES** | `docs/the-mark.md:171`, the third column of the classifier table |

! `docs/vocabulary.md` carries a polysemy rule, and this is what it is for: **the undeclared
meaning is the defect**, not the ambiguity. A reader who meets `shape` in this tree cannot tell
which question is being asked without checking which file they are in.

## !! AND THE SECOND QUESTION FOUND MORE THAN THE FIRST

Roy, 2026-08-28: *"Also why is it specific to query mark? Why isn't part of the other enum
candidates? Why 'shape' why not a better word?"*

**MEASURED the same day: the axis is not principled to `query`.**

    instruction   owes_change   sub-category field
    clean         False         --
    query         False         shape
    drop..move    True          --

**`clean` and `query` are EXACTLY the two instructions that propose no text**, and only one of
them can say what kind of not-proposing this is.

!! **THE UNFILLED NEED ON THE OTHER IS ALREADY RECORDED.** `docs/the-mark.md`, under *Open, and
NOT a new instruction*: four roles asked for it in four forms -- *enumerated it and it is true*,
*read hard and nearly marked it*, *checked internal consistency only*, *could have re-run it and
did not* -- and all four land as `clean`, **"which asserts one thing and was used for four."**
Roy, 2026-08-26: *"the word list we used was the words required else they start inventing words
... If it is anything it is a field on `clean`."*

! **So this is a STRUCTURAL question and not a rename.** Do the two no-text instructions share
ONE axis, or hold two? The answer decides what `T1.15` of
[`docs/plans/0.2.4-the-mark-and-the-collator.md`](../docs/plans/0.2.4-the-mark-and-the-collator.md)
makes a `StrEnum` of -- a set belonging to `query`, or one belonging to both.

## The word itself

`decision-log.md Process: #33` re-keyed the three onto **WHO RESOLVES IT**, deliberately replacing
an axis about where the evidence lives. A name taken from what the field DOES would therefore say
**whom the query is for** -- which is also how the trade names one, an *author query* being named
by who answers it.

! **The candidate is checked against the register BEFORE it is proposed**, per `docs/vocabulary.md`
-- the rule three law-words already broke. Recording the reasoning matters whichever way it goes:
`shape` may keep the field and lose its other two senses instead.

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
- [ ] Does `claim.shape` earn a field when nothing in `src/` reads its VALUE?
      MEASURED 2026-08-30: the four occurrences are `desk/mark.py`'s row, its
      published value list and its membership check; no collate step reads it.
      Verify: the answer is recorded in `docs/decision-log.md` beside the ruling
      on the word, and the field is either read by a module or gone.
