# The grading rubric -- what the judge is handed

**Version: 2.** Bump this whenever any wording below changes. A grade records the version it was
made under, because grades taken under different rubrics are not comparable and a later analysis
that mixes them is fitting a curve to two different questions.

!! **v2 REPLACED `RESTRAINT`, WHICH WAS INVALID.** It graded a run down for filing on any
paragraph END left alone -- treating *"the human did not fix this"* as *"this was correct"*.
**END is a POSITIVE key: it is evidence about what DID change and says nothing about the rest.**
So a run that found a real defect the human missed was marked down for it, and the instrument
could not record a run being BETTER than its key. Ruled by Roy, 2026-08-29: adjudicate a finding
outside END **against the code** instead.

You are grading ONE run of ONE editorial role against a defined END state. You see one arm. You do
not know what any other arm did, and you must not speculate about one.

---

## What you are measuring

The case pins a **START** commit and an **END** commit. START is what the role read. END is what a
human actually wrote afterwards -- the answer key. **You are measuring how close the run's
recommendations came to the END state**, on the axes below.

! **END IS THE KEY, NOT A CEILING.** A run may propose a correction the human did not make and
still be right; say so in your reasoning rather than marking it down for disagreeing. What you may
not do is credit a recommendation that is simply not about what END changed.

---

## The five axes

Grade each **A to F**, or **N/A** where the axis has no subject.

| axis | the question |
| --- | --- |
| **DETECTION** | Did a record land on the paragraphs the END diff changed? |
| **DIAGNOSIS** | Does the claim name the reason the END diff shows -- the actual mechanism? |
| **PRESCRIPTION** | Does the proposed text assert what END asserts? |
| **UNKEYED** | Of the claims END does not adjudicate, how many are FALSE of the code? |
| **EVIDENCE** | Does every cited `verbatim` really appear at its cite? |

### DETECTION

- **A** -- every paragraph END changed carries a record, and no changed paragraph was passed over.
- **C** -- about half.
- **F** -- none, or the run declared the changed paragraphs clean.

! **`clean` ON A CHANGED PARAGRAPH IS AN F HERE, NOT A BLANK.** Certifying a paragraph the human
went on to rewrite is a wrong answer, not a missing one.

### DIAGNOSIS

Only gradeable where DETECTION found something. **N/A** where it did not.

- **A** -- the claim names the mechanism END's change turns on.
- **C** -- right paragraph, adjacent reason; a reader would not reach END's fix from it.
- **F** -- right paragraph, wrong reason, stated confidently.

!! **THE RIGHT PARAGRAPH FOR THE WRONG REASON IS NOT A HIT.** Grade it as what it is: a detection
with a failed diagnosis. Do not let the address carry the reason.

### PRESCRIPTION

Only gradeable where DIAGNOSIS is C or better. **N/A** otherwise.

- Judge whether the proposed text **asserts what END asserts**. Two correct rewrites of one
  sentence differ in wording; that is not a defect.
- **F** -- the proposal would leave the reader believing something END contradicts.

### UNKEYED -- claims END does not adjudicate

**Itemise every finding that falls outside the END diff, and rule each one against the CODE**:
`true`, `false`, or `query`. Put them in `unkeyed_claims` with your reason for each.

**The axis grade is about the FALSE ones only** -- they are the harm:

- **A** -- no false claim outside the key.
- **F** -- a sweep of confident corrections to prose that was never wrong.
- **N/A** -- the run filed nothing outside the key.

!! **A TRUE CLAIM OUTSIDE THE KEY IS VALUE, NOT NOISE, AND IT IS THE COMMON CASE ON A REAL
CORPUS.** Roy, 2026-08-29: *"The human -- me in a lot of these cases -- certainly missed things.
Numpy and the other libraries are full of missed things."* **END is one person's fix on one day.**
On a real tree most of what a good run finds will have no counterpart in the diff, so a small
DETECTION set is not by itself a poor run -- read the unkeyed list before concluding anything from
the chain.

! **WHICH IS WHY THE TRUE ONES ARE ITEMISED RATHER THAN COUNTED INTO THIS AXIS.** They are not a
grade here; they are evidence you weigh in the OVERALL. A run finding ten real defects the human
missed and a run finding none must not come out alike, and this axis alone cannot tell them apart.

! **A `query` IS NOT A FALSE POSITIVE.** A role saying *"I could not settle this from what I was
handed"* is doing its job. Rule assertions; record hedges as `query` and hold them against nobody.

! **SILENCE IS NOT RESTRAINT.** A run that filed nothing has not shown care; it has shown nothing.
Where the run was empty this is **N/A**, never A -- and DETECTION already carries the F.

### EVIDENCE

One grade for the whole run, and the only axis with a mechanical answer -- you are given the
verification result. Report what it says.

- **F** -- any cited `verbatim` does not appear at its cite.

---

---

## Reader value -- recorded, NOT graded

In `reader_value`, write one or two sentences: **would a reader of the resulting prose learn WHY
the code is the way it is, or only what it does?**

! **NO GRADE, DELIBERATELY.** Roy, 2026-08-29: record it unscored, decide later. This repo says
the gates cannot tell whether prose is TRUE *or* whether a reader learns the reason -- the axes
above cover the first only. Whether the second is a real axis is an open question, and adding the
softest one before the spread on the hard ones is even measured would put the most variance into
the grade at the moment it can least carry it.

! It is not evidence for or against the overall. Write what you saw.

---

## The overall grade

**Give an overall A-F, and state in one or two sentences what decided it.**

!! **THERE IS NO FORMULA, AND YOU ARE NOT BEING ASKED TO APPLY ONE.** These letters are ordinals.
Nothing establishes that the A-to-B distance equals the B-to-C distance, and nothing establishes
how the five combine -- so a weighted mean would be an invented metric wearing arithmetic. Roy,
2026-08-29: *"That would make sense if there was a way of turning these ordinals into compossible
vectors and be certain that there is a mappable relationship across the grades to the final grade.
Both of those are false so we are slightly stuck with perception."*

! **SO THE OVERALL IS YOUR JUDGEMENT, AND THE REASON MATTERS AS MUCH AS THE LETTER.** It is
recorded next to the five axes so that, after enough runs, someone can ask whether a mapping
exists. **Your reason is the data for that question.** Give the actual ground, not a restatement
of the letters.

! **GRADE EACH AXIS ON ITS OWN TERMS.** Do not work backwards from an overall you have in mind, and
do not adjust an axis to make the set look consistent. An axis that disagrees with the overall is
informative; one quietly moved to agree with it is not.
