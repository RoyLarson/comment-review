# No stage establishes what the words mean before the roles are asked to use them

```
Status:   open
Progress: 0 of 7 tasks done
Owner:    agents
Requires-Roy: true
Raised:   2026-08-24 (Roy: most of our back and forth is making certain we and the system
          are clear on what the words mean, and there is no stage for that specific thing)
```

## Objective

**There is no stage where the terms are agreed, and the cost is a loose word read as permission.**
Roy, 2026-08-24: *"Most of our back and forth is about making certain we both -- and the system --
are clear on what the words mean, so we can be certain about what each is stating. We do not have
a stage in the agents for that specific thing. And we can see how that goes all through this code
base. **A loose term here gets interpreted as allowing something that it shouldn't, or implies
something that it doesn't.**"*

!! **NINE CASES, ALL MEASURED, SEVEN OF THEM ON ONE DAY.** This is not an argument from
principle; it is what 2026-08-24 produced while the subject was something else:

| the word | what it was read as | what it cost |
| --- | --- | --- |
| **`preferably`** | optional | Roy retracted it within the minute -- *"preferably sounds optional. They are not optional, it has to be able to do it."* A criterion had been written down as a preference |
| **`handed`** | the whole release | a one-way word named stage 3 while the scope was six stages; a SECOND PLAN was written, worked and closed against the premise before anyone re-read the sentence |
| **`stet`** | a per-mark refusal | a whole TODO section written on the wrong reading, and `no-mark-for-let-it-stand` -- 16 boxes -- is still built on it |
| **`clean`** | *nothing was found here* | it also means *a mark was proposed and refused*, so a re-run raises the same finding again |
| **`settled`** | a candidate term of art | proposed for a new job while carrying 129 uses; refused on Roy's own *"not overly generic"* test |
| **`re-review`** | the house's word | the trade's word `revise` was recorded 2026-08-21 and never carried into code -- 41 occurrences, 23 shipped |
| **`nothing converts`** | a design decision | `SKILL.md:925` and `galley.py:173` describe the same absent component two contradictory ways |
| **`a data row`** | the cost of adding a language | true lexically, false for a tokenized one -- a claim about cost that invites someone to make the change and discover it |
| **`foliator`, `folio`** | live terms | retired in code, alive in ~25 sentences of a plan, past every gate |

! **NOT ONE OF THE NINE WAS FOUND BY A GATE.** Each was found by a person reading a sentence and
disagreeing with it, which is the same finding `CLAUDE.md`'s opening section makes about prose in
general -- **arriving one level up, about the words the system uses on itself.**

### What the missing stage does

**It establishes, before the roles are asked to rule, what each term of art in scope MEANS -- and
gives a role somewhere to say that a term reads two ways.** Today a role is HANDED its vocabulary
(`vocabulary.py --reviewer <role>`, pasted at stage 4) and has no way to answer back: the handout
is one-directional, so a term that reads two ways is resolved silently, by whichever way the role
happened to read it.

!! **THE MATERIAL ALREADY EXISTS AND IS NOT WIRED TO ANYTHING.** `scripts/vocabulary_sweep.py`
finds terms of art in the shipped tree the inventory does not list, and its own docstring says it
is *"an INPUT, not a gate: every row needs a human to say whether it is a term."* **That is this
stage's input with no stage to consume it.** `check_vocabulary.py` gates the other direction --
that every key a role is given has a definition -- and neither asks whether the definition is
read the way it was meant.

! **AND THE REGISTER MAY ALREADY NAME IT.** A copy desk builds a **style sheet** for a job and a
**word list** within it -- every term of art and the decision taken about it, built AS THE WORK
GOES and travelling with the job. ! Stage 1 already finds *"the repo's style sheet"*, which is
spelling and hyphenation; whether this is the same artifact grown, or a second one, is T1. **The
name comes last**, per `CLAUDE.md`: what the job IS is above.

! **T7 IS WHAT KEEPS THIS FROM BEING A GOOD IDEA NOBODY CAN CHECK.** The nine cases are the test
set: a stage that would have caught none of them is not worth its tokens, and the number it
catches is the measurement this file is graded on.

## Tasks

- [ ] T1 -- * Rule what the stage is called and where it sits among the eight. Verify: the
      ruling is in `docs/decision-log.md`.
- [ ] T2 -- * Rule whether it runs once or grows as the roles work. Verify: the ruling is
      in `docs/decision-log.md`.
- [ ] T3 -- Give it an artifact a later stage reads. Verify: a run produces the file and
      stage 4 is handed it.
- [ ] T4 -- Feed it from `vocabulary_sweep.py`, which already finds unlisted terms.
      Verify: a sweep row reaches the artifact without being retyped.
- [ ] T5 -- Let a role RAISE a term as reading two ways. Verify: a report can name a term
      it could not read one way, and the join carries it.
- [ ] T6 -- Refuse a run that leaves a raised term unanswered. Verify: it exits nonzero
      and names the term and the role.
- [ ] T7 -- Score the stage against the nine cases in the Objective. Verify: how many it
      would have caught is written into this file with its date.

## Related

- [`settle-carries-two-meanings`](settle-carries-two-meanings.md) -- one instance, filed the same
  day, found in conversation and by no gate
- [`no-mark-for-let-it-stand`](no-mark-for-let-it-stand.md) -- another, and it is still written on
  the reading that `decision-log.md Process: #9` corrects
- [`nothing-makes-the-fair-copy`](nothing-makes-the-fair-copy.md) -- where `taken in` and `stet`
  were ruled, which is the conversation this file is about
