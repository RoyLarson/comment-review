# What a check can see, and how to tell whether it sees anything

**Rules for adding a gate to this repo.** `limitations.md` governs changing the skill's prose;
this governs changing what checks it.

!! **"DOES THE CHECK PASS" IS NOT THE QUESTION. "COULD THE CHECK FAIL" IS.** A check that
consults the fact it is checking cannot fail, and nothing about a green run says which kind you
have. Before trusting a new one, ask what it would have to READ to disagree -- and whether that
is a **different source** from the one under test.

## Three ways a gate is green on a broken tree

They are not the same failure and they need different answers.

| | what happened | what finds it instead |
| --- | --- | --- |
| **1. It answers a different question** | the check is correct and its subject is not the defect | a reader -- which is the whole remit of the four editorial roles |
| **2. It shares the defect** | the check reaches the same wrong fact the system does, so it agrees with it | separating the concern, so the two have different sources |
| **3. It was never reached** | a branch, a skip, a filter that removes the case before the assertion | reading the check, not running it |

! **`CLAUDE.md` records the first with its measurements** -- 31 reader-visible defects behind
2,413 passing tests, and four more on this repo behind 519-534. **The second is recorded here**,
because it is the one that looks most like success.

## The case: a lossless check that measured nothing

!! **MEASURED 2026-08-21.** `compositor.set_page(page_for(text)) == text` is the strongest check
this system has: it asks whether the model of a page is LOSSLESS, byte for byte, and nothing here
could ask that before it existed. **Its first run scored 699 of 699 across ten languages**
(`8c39da9`, 12:44).

!! **157 ADDRESSES WERE HELD BY TWO PARAGRAPHS EACH AT THAT MOMENT, AND IT REPORTED NONE OF
THEM.**

! **Because it reached the same wrong fact the system did.** That version rebuilt the file from
each paragraph's recorded line position -- so it reconstructed the text out of numbers it had
just read from that text. The check and its subject shared a source, so agreement was guaranteed.
A tautology with a green light on it.

! **It became an instrument at `7c9ad96`, 13:56**, when it was made to set from the FOLIATION
instead -- every place named, in the order the walk emitted them, with no line consulted. Within
the hour it had surfaced the collisions and the non-contiguous `b`. **Same module, same
assertion, opposite value**; the only difference was whether it could reach a fact belonging to
another concern.

## What made it able to fail was the separation, not the check

Each concern returned to its owner made the same assertion sharper. Measured over one day:

| | the move | found by |
| --- | --- | --- |
| `7c9ad96` | the compositor sets from the reading order, not from line numbers | Roy, reading |
| `ee42920` | the LANGUAGE ROW states which side its documentation goes on | Roy, reading |
| `f411b76` | the language rows become a LEAF, read by the lexer and compositor alone | Roy, reading |
| `3ddf7b1` | the LEXER types a paragraph `matter`; the page only maps it | the identity, silent on every `.py` |
| `875b0d4` | `leading` takes the blanks a `b` owned on both sides | the identity, 16 of 185 files |
| `b998a60` | the reading order is the WALK'S; `page.py` had overwritten it | reading, after an `add` vanished |
| `97359c2` | the galley stops splicing; a change is an assignment | the split, once the order was right |

!! **SO THE ORDER IS NOT "BUILD THE DETECTOR, THEN IT FINDS THINGS."** The detector worked only
to the degree the separation had already happened, and each increment of separation made it
sharper. A round-trip check written against the ORIGINAL system would have passed -- exactly as
this one did at 12:44.

! **Roy, 2026-08-21:** *"the compositor couldn't be built until the lexer and the languages and
the page and the census was doing the work each needed to do individually. So from start to
finish the old system was insufficient and mixed up concerns in so many places that it was never
going to work."*

## A measurement across two moving parts attributes to neither

!! **THE MECHANISM MUST WORK END TO END BEFORE THE INSTRUCTIONS ARE TOUCHED**, and this is a
measurement rule rather than a tidiness one. Change the machinery and the agent prose in one
step and a movement in the output could be either -- nothing separates them afterwards, so the
question *did the change help* cannot be asked at all, however carefully the run was graded.

!! **MEASURED, AND IT COST EVERY RELEASE TO DATE.** Roy, 2026-08-23: *"v0.1.0, 0.2.0, 0.2.1,
0.2.2, 0.2.3 are all conflated about how well the system works because the mechanics of the
system didn't work and we changed both at the same time."* The 0.1.x line and 0.2.0 through
0.2.3 each moved the census, the addressing or the join AND the four role files together. Every
number in their evidence is real; none of it answers how well the SYSTEM works, because no run
holds one side still.

! **A CONFOUNDED RUN IS NOT A WEAKER MEASUREMENT, IT IS A DIFFERENT KIND OF THING.** A green
gate that shares its subject's defect (above) still reports on something. This reports on a
compound nobody will build again -- that mechanism with those instructions -- so the finding
does not carry to the next version even when the numbers look good.

! **WHAT IT ASKS OF A CHANGE THAT TOUCHES BOTH:** land the mechanism first with no agent file
edited, and require that effectiveness does NOT move -- the machinery is a CONTROL, and a move
there is the finding. Only then change what a role is told, against a baseline that now exists.
The worked instance is
[`code-concerns-cannot-carry-a-proposed-change`](../TODO/code-concerns-cannot-carry-a-proposed-change.md)
then [`a-role-with-no-code-out-damages-the-prose`](../TODO/a-role-with-no-code-out-damages-the-prose.md).

## What to do with a new check

- **Name the two sources.** What does the check read, and what does the subject read? If the
  answer is the same thing, the check is a restatement.
- **Break it on purpose once.** A check that has never been observed failing has not been
  observed at all. Every measurement in this file came from one that could.
- **Prefer a check whose input the subject cannot reach.** The identity works now because a page
  is set from the cues while the file is read by the lexer -- two sources that must be made
  to agree rather than one consulted twice.
- **A green run is not a report.** State what the check would have caught, not that it passed.
- **Move one side at a time.** If the change touches the machinery AND what an agent is told,
  the measurement attributes to neither. Land the mechanism first and require that nothing
  moves; that null result is what makes the second step readable.
