# A claim can be false by arithmetic with no enforcing line to check it against

```
Status:   decision-needed
Progress: 1 of 4 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-18 (Roy, 2026-08-18, finding 'the number to beat is zero blocks
          missed' in this repo's own docs)
Triaged:  2026-08-23 -- the two prose statements that carried the defect have SINCE BEEN
          CORRECTED, so the example is historical and the gap in the role file is not.
          MEASURED: `evidence/tier-measurement.md:79` now reads *"Stated as a REQUIREMENT
          and not as a number to beat, because blocks are"* and `docs/parsing.md:146`
          reads *"A REQUIREMENT, not a number to beat."* ! And the "must displace a rule"
          claim this file carried is FALSE -- `docs/limitations.md:46` says *"A new rule
          does not have to displace another."*
Split:    2026-08-23 -- 3 boxes became 4; the register box held the entry and the currency
          it must name, and both boxes carried their argument, now stated above the list
```

## Objective

!! **`block-context` COULD NOT HAVE CAUGHT THE DEFECT ROY FOUND IN THIS REPO'S OWN
DOCS**, and the reason is precise rather than an oversight. Its constraint check, verbatim at
`plugins/comment-review/agents/comment-review-block-context.md:82-83`, reads: *"Find the line
that enforces the bound and compare four things: the VALUE, the DIRECTION (`>` vs `>=`), the
UNITS, and what happens at the boundary."* That needs an ENFORCING LINE. The claim had none.

**The claim:** *"The number to beat is zero blocks missed."* Blocks are counted
in whole numbers, so nothing lies below zero and there is nothing to beat. Roy,
2026-08-18: *"you can't 'beat' zero blocks missed. These are whole number counts
only not real number counts."*

! It was in `evidence/tier-measurement.md` and repeated in `docs/parsing.md`, and
every gate this repo runs was green over both. ! **Both sentences have since been rewritten by
hand** -- see the `Triaged:` note -- so the instance is closed and the CLASS is what is left.

## Why the shape is worth naming

**It is false by ARITHMETIC, not by disagreement with code.** No file resolves
it; a reviewer needs nothing but the sentence and the nature of the quantity.
That is a different check from every constraint check now written, all of which
compare prose against an enforcing line.

**THE SHAPE, as it goes into the register:** a quantity that is a COUNT -- whole, non-negative --
stated with comparative framing that assumes room below it. **The measured example** is *"the
number to beat is zero blocks missed"*, which was in `evidence/tier-measurement.md` and repeated
in `docs/parsing.md`, and which no gate could fire on because there is no code to resolve it
against.

Sibling shapes, so the rule is not written for one instance:

- a floor stated as a target, when the count is whole and non-negative
- a percentage stated above 100, or a rate above its own ceiling
- a bound stated in the wrong direction for its units -- *"no more than -1"*
- an interval whose lower bound exceeds its upper

!! **AND IT IS THE SHAPE AN LLM IS LEAST ABLE TO SELF-INSPECT.** Roy, 2026-08-18:
*"particularly when the thing that wrote it has been trained that something
stated as better is always better -- can't inspect its logic like that."*
Comparative framing reads as good prose, and nothing in producing it asks
whether the quantity has room in that direction. The sentence was WRITTEN by
this system's author-agent and survived every later reading by one.

! That is an argument for a mechanical check rather than a better reader, and it
is the same argument this repo makes about green gates -- one level in.

## What this is NOT

! **Not a case for a fifth editorial role.** The four mimic real-world roles and
Roy has said a fifth is unlikely. If this belongs anywhere it is `block-context`,
whose remit already says CONSTRAINTS -- what is missing is that its check assumes
a line to compare against. **So the question owed is whether block-context's constraint
paragraph gains a second half, or whether this is out of scope and stays a human's catch.**

! **Not free, but it does NOT have to displace a rule.** This file previously said a new rule
*"should REPLACE one rather than accumulate"*, and `docs/limitations.md:44-65` says the
opposite: *"A new rule does not have to displace another. It has to earn the context it costs,
and there are exactly two ways"* -- it CATCHES something, or it SAVES A SEARCH.

! **WHICH CURRENCY THIS ONE PAYS IN IS CURRENCY 2.** A claim false by arithmetic needs no file
opened to settle, so the rule replaces a search rather than adding one. ! That is stated here
rather than carried as a box, because it is an argument and nobody ticks it -- what a box can
say is whether the register entry states it.

! **A rule proposed for a role file goes to**
  [`role-rule-register`](role-rule-register.md) **and is decided with the others.**
  Role prose is budget-fixed, and every candidate is judged against the same two currencies.

## Tasks

- [?] T1 -- * Rule whose remit this class is: a second half to `block-context`'s
      constraint paragraph, or out of scope. Verify: the answer is written into this file.
- [ ] T2 -- File the candidate in `role-rule-register.md`, with the shape, the example and
      the siblings. Verify: `grep -n "arithmetic"` on that file returns the entry.
- [ ] T3 -- Make that entry name currency 2 and a check a reviewer runs without opening
      another file. Verify: the entry states both.
- [x] T4 -- NOT A TASK, restated under *What this is NOT*: the currency is settled at 2,
      and the checkable half of the old box is now T2's and T3's Verify clauses.
