# A claim can be false by arithmetic with no enforcing line to check it against

```
Status:   open
Progress: 0 of 3 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-18 (Roy, 2026-08-18, finding 'the number to beat is zero blocks
          missed' in this repo's own docs)
```

## Objective

!! **`block-context` COULD NOT HAVE CAUGHT THE DEFECT ROY FOUND IN THIS REPO'S OWN
DOCS**, and the reason is precise rather than an oversight. Its constraint check
reads: *"Find the line that enforces the bound and compare four things: the
VALUE, the DIRECTION (`>` vs `>=`), the UNITS, and what happens at the
boundary."* That needs an ENFORCING LINE. The claim had none.

**The claim:** *"The number to beat is zero blocks missed."* Blocks are counted
in whole numbers, so nothing lies below zero and there is nothing to beat. Roy,
2026-08-18: *"you can't 'beat' zero blocks missed. These are whole number counts
only not real number counts."*

! It was in `evidence/tier-measurement.md` and repeated in `docs/parsing.md`, and
every gate this repo runs was green over both.

## Why the shape is worth naming

**It is false by ARITHMETIC, not by disagreement with code.** No file resolves
it; a reviewer needs nothing but the sentence and the nature of the quantity.
That is a different check from every constraint check now written, all of which
compare prose against an enforcing line.

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
a line to compare against.

! **Not free.** `docs/limitations.md` governs prose added to a role file: the
budget is fixed, and a new rule should REPLACE one rather than accumulate. A rule
that cannot be checked without opening another file does not earn its place.

! **A rule proposed for a role file goes to**
  [`role-rule-register`](role-rule-register.md) **and is decided with the others.**
  Role prose is budget-fixed, so a candidate is judged against what it displaces.

## Tasks

- [ ] * **Rule whose remit this is.** `block-context` is the closest --
      constraints are already its -- but its check is written around an ENFORCING
      LINE, and this class has none. ! Do not add a fifth role for it: the four
      mimic real-world editorial roles and Roy has said a fifth is unlikely. The
      question is whether block-context's constraint paragraph gains a second
      half, or whether this is out of scope and stays a human's catch.
- [ ] **Write the shape down, with the measured example.** A quantity that is a
      COUNT -- whole, non-negative -- stated with comparative framing that assumes
      room below it. `the number to beat is zero blocks missed` was in
      `evidence/tier-measurement.md` and repeated in `docs/parsing.md`, and no
      gate could fire on it because there is no code to resolve it against. !
      Sibling shapes to name: a percentage over 100, a bound stated in the wrong
      direction for its own units, an interval whose lower bound exceeds its
      upper.
- [ ] **Say which CURRENCY it pays in.** `docs/limitations.md` rules that a rule
      pays for its own lines by what it CATCHES or by the search it SAVES.
      This one is currency 2: a claim false by arithmetic needs no file opened
      to settle, so the rule replaces a search rather than adding one. Verify:
      the addition names a check a reviewer runs without opening another file.
