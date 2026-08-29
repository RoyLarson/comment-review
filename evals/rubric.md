# The grading rubric -- what the judge is handed

**Version: 1.** Bump this whenever any wording below changes. A grade records the version it was
made under, because grades taken under different rubrics are not comparable and a later analysis
that mixes them is fitting a curve to two different questions.

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
| **RESTRAINT** | What did it file on paragraphs END left alone? |
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

### RESTRAINT

One grade for the whole run.

- **A** -- nothing filed on paragraphs END left alone, beyond well-founded `query`s.
- **F** -- a wide sweep of corrections on prose that was never wrong.

! **A `query` IS NOT A FALSE POSITIVE.** A role saying *"I could not settle this from what I was
handed"* is doing its job. Count assertions, not hedges.

! **SILENCE IS NOT RESTRAINT.** A run that filed nothing has not shown restraint; it has shown
nothing. Where DETECTION is F because the run was empty, RESTRAINT is **N/A**, not A.

### EVIDENCE

One grade for the whole run, and the only axis with a mechanical answer -- you are given the
verification result. Report what it says.

- **F** -- any cited `verbatim` does not appear at its cite.

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
