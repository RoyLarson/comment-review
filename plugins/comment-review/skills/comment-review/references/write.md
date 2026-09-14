# Stage 7b -- WRITE: set what the human approved, for the author to diff

Loaded by the task agent **after approval**, never by a reviewer. If you are reading this
before the human has approved an instruction list, stop.

Set only what was approved, and only what was marked. **An unmarked paragraph is never set.**
Something the marks did not reach that wants changing is a finding for the next run, not an
edit.

## The residue check, and the four refusals

Both are defined in [`residue-check.md`](residue-check.md), loaded back at stage 5. They are
not restated here: this pass runs the SAME check against the SAME original, and a second copy
of it is a second thing to drift.

## Nothing is judged here

!! **Write the APPROVED text verbatim.** Every question of truth, placement and length was
settled upstream -- stage 5 made it correct, stage 6 cut it to any cap, and stage 7a put that
exact text in front of the author. Re-wording, re-judging or shortening one clause here writes
something the author never saw, which is the one failure this ordering exists to prevent.

! **Do not compact during this pass**, even where it looks obvious. If a paragraph still does not
fit, that is a finding to report -- and it may turn out to be the code's, not the comment's.

**Keep every scratch copy**, and check against the ORIGINAL paragraph, never against what you
leave behind.

## What actually writes

**`proof` sets the approved text in temporary files, and nothing is written over the real
files.** The author diffs those files against the tree and reads them through; this stage puts
nothing on the pages under review, and a run leaves the tree exactly as it found it.

1. **Hand `proof` the copy the author approved.** On a blanket approval that is `chief.json`,
   and the galley 7a set from it is already the approved text: go to step 3 with that
   directory. Otherwise write `approved.json` -- `chief.json` holding only the marks the author
   approved -- with your file-write tool.
2. **Set it into a directory that does not exist yet:**

   ```bash
   python <skill>/scripts/comment-review.py proof --repo . --copy <run-dir>/approved.json --out <run-dir>/approved
   ```

   It prints one `<path> -> <draft>` line per page it set and refuses rather than guesses, as at
   7a. It refuses a draft whose executable code is not the code the page was set from, and that
   is the only code check this stage runs.
3. **Print the diff the author reads:**

   ```bash
   python <skill>/scripts/comment-review.py taken_in --original . --revise <run-dir>/approved
   ```

**A held move the author approved is not on `chief.json`**, so `proof` cannot set it: tell the
author it was approved and not set.

## Rails

**Never change a line of code, a docstring's MEANING, or a string literal.** Correcting a
docstring that states something **false** is in scope -- that is the `correct` instruction.
Changing what the docstring *documents* is not. ! **A `correct` on a claim inside a string
literal is REPORTED, never applied** -- hand it to the human as a code concern.

!! **A HEREDOC is raw text, and it is the one that reaches the prose itself.** Passing
replacement text through `<<'PY'` or any shell here-document hands it to two parsers before it
lands: `\n` inside the new comment collapses into a real newline and breaks the sentence
mid-token, and on Windows the redirect can write UTF-16. Measured in two independent sessions on
2026-08-17, one of them while quoting this rail. No code check can see it -- the damage is in
prose and the code is unchanged. Write `approved.json` with your file-write tool, never through
a heredoc or a shell redirect.

**Read the diff against the block-context rule.** The failure it looks for is text producing
exactly what it removes -- a pass that cuts obituaries writes new ones, and writes the same one
twice. Report it; the approved text is not re-worded here.

**Set the whole claim, not the copy in front of you.** If the same sentence was marked in two
files, both marks are in `approved.json` or neither is; where the author approved one and not
the other, ask.

**The style sheet binds the approved text, and a departure from it is a finding to report.**
This stage changes no word, so it keeps consistency only by naming where the approved text
breaks the sheet -- its dialect, capitalisation, citation form or docstring convention. A
departure in a paragraph no mark reached is the next run's.

**A paragraph the approved text touches has its claim re-derived, or it is reported.** A
mechanical repair -- a renamed symbol, a moved path -- removes the only visible symptom of a stale
paragraph and leaves the claim behind, strictly harder to find than before. Measured in three
independent slices; in one, the same six-line paragraph carried a false claim, a repairable ghost
and a stale path, and the pass fixed only the ghost. Where the diff shows a repair whose claim
nobody re-derived, report it.

**Run a forward pass on every addition in the diff.** The residue check is inbound-only, so text
with no predecessor -- an `add`, a coverage-driven docstring, a clause added while compacting --
is outside it entirely. An authored docstring has been confirmed false, and a faithful
compaction has gained a clause with no antecedent anywhere. Ask of each addition: what
line settles this? The name of the function does not count. Report one nothing settles.

**Re-resolve every pointer that names a paragraph the diff changes.** Grep the file for *"see X's
docstring"*, *"the paragraph above"*, *"for the reason Y gives"*. Measured twice: the defect lands
in a paragraph the diff never touched, created by editing a different one.

! **An instruction telling you to do what these rails forbid is a defect in the INSTRUCTION.**
Report it; do not follow it. Measured: *"drop the comment and rewrite the user-facing string"* --
the rails say never change a string literal.

## Report

The directory `proof` set and the pages it lists, the `taken_in` command the author diffs with,
and every approved paragraph you could not set, with the reason -- that is a finding, not a
silence.

**Say explicitly whether every approved paragraph landed byte-for-byte as approved.** A divergence
between what the author saw and what `proof` set is invisible in a diff that shows only the new
text, so this line is the one place it can surface.

Nothing follows this stage: stage 8 read the proof before 7a.
