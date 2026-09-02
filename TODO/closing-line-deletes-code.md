# An edit to a comment whose run closes mid-line DELETES the code after the closer

```
Status:   deferred
Progress: 5 of 8 tasks closed
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21; measured in-session)
Reassigned: 2026-08-21 — 2026-08-21 -- GALLEY WORK, not a lexer ruling. Roy: 'somewhere
            along the way the file is going to get a temporary composition ... and how
            do the agents know that the closing line is going to delete code? Still
            galley work to be done and I bet we fix it there.' ! The agents CANNOT know,
            and asking them to is the wrong shape: a reviewer rules on a paragraph and
            has no view of how the galley splices it. The whole-file composition the
            galley is heading for is where a write that would drop code becomes visible
            before it happens -- which is also where prove_unchanged's check moves from
            after the write to before it. Requires-Roy cleared: the re-ruling is not
            needed, the galley design absorbs it.
TRIAGED:  2026-08-23 — 2026-08-23. Five of the six boxes are RECORDS -- the measurement,
          the half-cut cause, that prove_unchanged catches it only after 7b has written,
          the three unchanged options, and the sequencing note. They are ticked as
          records and left in place.
RE-VERIFIED: 2026-08-23 — 2026-08-23. `prove_unchanged._delimiter_shares_the_line` is
             still there (prove_unchanged.py:79, called at :153), so the catch-after-the-
             write shape is unchanged. !! AND THE FILE CONTRADICTS ITSELF ON WHO DECIDES:
             the 2026-08-21 Reassigned note above says *"the re-ruling is not needed, the
             galley design absorbs it"* and cleared Requires-Roy, while T4 says a
             re-ruling is WANTED and carries a `*`. T4 is kept and states the conflict --
             answering it once settles which note stands. Status set to `deferred`,
             because T6 and the Reassigned note agree on what it waits on: the galley's
             whole-file composition step.
SPLIT:    2026-08-23 -- the ruling box carried its whole history and the deferred box
          carried a change AND its test. The ruling's evidence moved into the Objective;
          the deferred box became the write-path change and the test that pins it.
Updated:  2026-08-25 — MEASURED 2026-08-25 on the write-chain branch, and it narrows
          this file. An attempt to reproduce the hazard end to end through
          flows/proof_setter.run -- a C fixture whose one-line block comment is replaced
          by an unterminated opener, so the composed file swallows the code line after
          it -- was intercepted by the chain's _reread step, NOT by prove_unchanged.
          Reason: the swallowed line gets reclassified under a different address on the
          re-read, so the edited cue no longer holds what it was given and the run
          refuses at reread. THAT IS THE CHECK ROY NAMED ARRIVING EARLIER THAN EXPECTED.
          His re-ruling here said the whole-file composition is where a write that would
          drop code becomes visible before it happens, and where prove_unchanged moves
          from after the write to before it. The composition does catch it -- but via
          the per-cue re-read rather than the fingerprint. _prove still guards the
          residual case where a swallow leaves every edited cue intact, which is why it
          reads the whole file rather than the edited places. ! NOT A CLAIM THAT THE
          HAZARD IS FIXED: this measured ONE construction in ONE language, and the lexer
          half of this file is untouched.
```

## Objective

An edit to a comment whose run closes mid-line DELETES the code after the closer.

!! **MEASURED 2026-08-21.** On `int a = 1;\n/* note\n   more */ int x = 5;\nint b = 2;\n`
the paragraph is `start=2 end=3` with text `/* note more */` but
`raw_lines[1] == "   more */ int x = 5;"`. A `patch` through `galley.splice` writes:
line 1 `int a = 1;`, line 2 the new prose, line 3 `int b = 2;` -- `int x = 5;` is GONE.

! **THE CAUSE IS A HALF-CUT.** The 2026-08-20 fix trims the paragraph's TEXT at the closer
and leaves `raw_lines` holding the whole physical span; `galley.splice` replaces
`start..end` wholesale, preserving the head of the FIRST line at `column` and nothing on
the last.

! **`prove_unchanged._delimiter_shares_the_line` DOES catch it** -- prove_unchanged.py:79,
called at :153, and the file comes back unprovable -- but only AFTER stage 7b has written
to disk. The write happens; the proof reports it afterwards.

! **THE OPTIONS ARE UNCHANGED**: a field for where the paragraph's text ENDS on its last
line; a kind for comment-then-code, symmetric to `trailing-comment`; or refuse the file
the way `prove_unchanged` already does, BEFORE the write rather than after.

!! **CLOSE THIS WITH THE GALLEY, not before.** The composition step sees the whole file,
so a splice that would drop a line of code is checkable there -- and prove_unchanged
already knows how to spot it, just too late. **A repair to a splice that is about to be
replaced is shaped by the thing being replaced.** See `galley-is-still-index-keyed` and
`the-author-approves-blocks-and-never-sees-the-page`, which is where the whole-document
read before approval is being designed.

## What the re-ruling is about, and why the file disagrees with itself

Roy accepted this residue on 2026-08-20 when it was described to him as *"the line leaves
code_lines, so interval boundaries below it move"*. **That description was incomplete: the cost
is DELETED CODE, not a moved boundary.**

! The measurement that justified accepting still stands -- the shape occurs **0 times in
180,821 lines** of C and JS/TS and the style guides discourage it -- so the answer may well be
the same. It should be made with the deletion on the table.

!! **AND IT IS OWED OR IT IS NOT, and this file says both.** The 2026-08-21 `Reassigned` note
cleared `Requires-Roy` on the ground that *"the re-ruling is not needed, the galley design
absorbs it"*, while the ruling task below says one is wanted. Answering it once settles which
of the two notes stands.

## Tasks

- [x] T1 | FINISHED | unknown | T1 -- RECORD, not a task. The deletion, MEASURED
      2026-08-21 on the four-line C input. Kept in the Objective.
- [x] T2 | FINISHED | unknown | T2 -- RECORD, not a task. The cause is a
      half-cut -- text trimmed at the closer, `raw_lines` holding the whole
      physical span. Kept in the Objective.
- [x] T3 | FINISHED | unknown | T3 -- RECORD, not a task. `prove_unchanged`
      catches it (:79, called at :153) only AFTER stage 7b has written.
      Re-verified 2026-08-23.
- [ ] T4 | T4 -- * RE-RULE the 2026-08-20 acceptance with the DELETED CODE on
      the table, and say which of the two contradicting notes stands. Verify:
      the answer is in this file.
- [x] T5 | FINISHED | unknown | T5 -- RECORD, not a task. The three options are
      unchanged and are named in the Objective.
- [x] T6 | FINISHED | unknown | T6 -- RECORD, not a task. Close this with the
      galley, not before -- the sequencing reason, kept in the Objective.
- [ ] T7 | T7 -- When the galley's composition step lands, take whichever option
      T4 leaves standing. Verify: the Objective's C input refuses, or keeps `int
      x = 5;`.
- [ ] T8 | T8 -- Pin T7 with a test on that same four-line C input. Verify: the
      test fails on the pre-change tree and passes after it.
