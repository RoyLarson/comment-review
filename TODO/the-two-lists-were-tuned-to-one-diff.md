# The acquittal and suppression lists are deleted -- five entries need re-deriving

```
Status:   open
Progress: 2 of 7 tasks done
Owner:    session * Roy (2 rulings)
Raised:   2026-08-16 (Roy: "yes drop both lists / and lets create a todo to clean up
          those entries - because several of them do not follow this own skills rules")
```

## Objective

**Both lists are gone from `reviewer-brief.md`. This file holds what was inside them**, because
several entries carry real checks and one carries a real measurement, and none of that survives
in the tree any more.

Why they went, in order of weight:

1. **The mechanism that decides `clean` already exists and is stated per role.** Each agent file
   says what its own `clean` asserts, and every one is a TRUTH assertion at that role's scope --
   *"EVERY SENTENCE in the block is true of the code beside it"*, *"...belongs to the line it sits
   on"*, *"name, signature, docstring, comments and body agree"*, *"the module docstring accounts
   for the exposed surface"*. The acquittal list matched on a prose SHAPE instead, and claimed to
   be *"the ONLY reasons to pass a block over"* -- so a block that is true of the code beside it
   but matches no label was `clean` by its role's file and a finding by the brief.

2. **The measurement behind it does not support it.** `evidence/ga/brief.md`: ten candidate
   SKILL.md rewrites, each applied to SIX `redacted_pkg` files at base `REDACTED_SHA_H`, scored on F1 against
   *what a later commit actually rewrote there* (`ground_truth.py` builds the answer key from that
   diff; 209 changed prose blocks out of 419). Candidate `1d` used a closed acquittal list and won
   at 0.8184. ! But `brief3.md:31-34` -- 1d and 2a ran the **same closed list** over the **same 419
   blocks** and acquitted 47% versus 14%: *"The acquittal RATE is the trait; the acquittal LIST is
   just vocabulary."*

3. **The oracle is a diff, not a judgement.** A correct finding on a block that commit happened
   not to touch counts as a false positive, so *"precision .783"* measures agreement with one
   burn-down's choices in one project.

4. **The suppression list had no provenance at all** -- it appears nowhere in `evidence/`. It was
   named as a sibling to the acquittal list, and it suppressed nothing: its content is measured
   ANNOTATION precision plus the rule that a low-precision one is a *batch to triage*.

## Tasks

- [ ] * Rule on the three CONDITIONAL entries, which were resolution procedures wearing an
      exemption's name -- each excused a block only *after* work that could equally have produced
      a finding. They are checks, and if they are kept they belong with the checks they duplicate,
      not in a list of reasons to pass over:
      - **re-run the arithmetic.** *"Pure arithmetic over committed values is checkable without
        judgement, so do the sum and report the number. Measured: one worked example was wrong,
        its first correction was ALSO wrong, and all three versions rounded to the same asserted
        value, so nothing downstream ever objected."*
      - **verify a guard is really absent.** *"...if a test does fail, one exists."* ! This one is
        already re-derived independently -- the `guard` / `unguarded-invariant` split was settled
        2026-08-16 from Roy's own renderer example, without reference to the GA.
      - **an expiry condition already met is not an acquittal.**

- [x] **Restored 2026-08-16**, in `clean`'s own section rather than the deleted list's. Roy:
      *"Nothing should be 'judged - clean' just because it is ... fits the jurisdiction labels we
      added earlier."* `acquitted` became `clean`, and the closing clause now points at the role
      file: *"none of those is your role's question unless your role file says it is."* It sits
      directly under *"Your role file states what your `clean` asserts"*, which is where the
      remit question is actually decided. Brief 261 -> 266 lines.

- [ ] `states-the-signature` is not merely unearned, it CONTRADICTS `function-context`. That
      role's absence question is *"what must be true of this function's OUTPUT, or of its CALLER,
      that the SIGNATURE CANNOT EXPRESS -- and does the docstring say it?"* A docstring that
      restates the signature is the one that has not answered it. Do not restore this entry
      anywhere without resolving that first.

- [ ] `names-its-line` was a description of a comment doing its ordinary job, not a rule. Decide
      whether anything is lost by its absence, or close this box as nothing to do.

- [x] **`detector` is DELETED, 2026-08-16.** It was stated only inside the suppression list --
      *"a census annotation read as a signal, and its PRECISION is how often it is right"* -- and
      everything it supported (precision, batch to triage, reasons to distrust) went with that
      list. The two `census.py` comments left meant `annotation`, which is settled. Roy: *"drop
      it - especially since it currently only survives in code comments where it doesn't belong
      in the first place."* ! It also failed the REGISTER: a detector is instrumentation.

- [ ] Decide what happens to **batch to triage** and the measured precision rates that went with
      it: *"An annotation below roughly 10% precision is a batch, not a finding. Reporting it raw
      spends the human's attention on a list they will learn to skip, which is how a real hit gets
      lost."* Rates were a date-or-path used as a **command-line argument** (4/4 false), an
      identifier that is also a **module stem** (8/8), a **warning glyph** as such (45/0), and a
      **repo-relative path citation** resolved only against the repo root (80/84, 18/20, 2/2).
      ! All measured on ONE repository -- the same one the GA scored against.

- [ ] * Sweep the remaining judicial register against the PUBLISHING metaphor. `acquit`
      survives as a plain verb at `agents/...-block-context.md:36` and `SKILL.md:614`.
      ! **`jurisdiction` is already done** -- renamed **`remit`** on 2026-08-16, the same day.

      ! **The metaphor is not a new standard; it is the one already in force.** Roy, 2026-08-16:
      *"I have been working under this assumption of the metaphor for a while."* Editorial roles,
      editorial marks on a manuscript, a proof, a proofreader -- the vocabulary is PUBLISHING, and
      his PROOFREADER ruling states the reason out loud: *"it is reading the PROOF and it is
      determining if the document deserves more marks. That fits the role of a PROOFREADER in
      society."*

      ! **So these words were off-metaphor when they were written, not merely unmeasured.**
      `acquittal` and `suppression` arrived with the initial plugin import. **`jurisdiction` did
      not** -- this session proposed it on 2026-08-16 against a metaphor neither of us named at
      the time. It was the one judicial word this branch ADDED, and it is now **`remit`**; what
      is left here is `acquit` as a plain verb.
