# Stage 7b — WRITE: put on disk what the human approved

Loaded by the task agent **after approval**, never by a reviewer. If you are reading this
before the human has approved a verdict list, stop.

Apply only what was approved, and only what was marked. ⚠ **An unmarked block is never written.**
If WRITE wants to touch something the mark did not reach, that is a finding for the next
run, not an edit.

## The residue check, and the four refusals

Both are defined in [`residue-check.md`](residue-check.md), loaded back at stage 5. They are
not restated here: this pass runs the SAME check against the SAME original, and a second copy
of it is a second thing to drift.

## Nothing is judged here

⚠⚠ **Write the APPROVED text verbatim.** Every question of truth, placement and length was
settled upstream — stage 5 made it correct, stage 6 cut it to any cap, and stage 7a put that
exact text in front of the author. Re-wording, re-judging or shortening one clause here writes
something the author never saw, which is the one failure this ordering exists to prevent.

⚠ **Do not compact during this pass**, even where it looks obvious. If a block still does not
fit, that is a finding to report — and it may turn out to be the code's, not the comment's.

**Keep every scratch copy**, and check against the ORIGINAL block, never against what you
leave behind.

## Rails

**Never change a line of code, a docstring's MEANING, or a string literal.** Correcting a
docstring that states something **false** is in scope — that is the `correct` verdict.
Changing what the docstring *documents* is not. ⚠ **A `correct` on a claim inside a string
literal is REPORTED, never applied** — hand it to the human as a code concern.

**Prove code identity; do not assert it.** Run the proof — do not perform it:

```bash
python <skill>/scripts/prove_unchanged.py --base <merge-base> --repo . <paths...>
```

It exits nonzero unless every path is proven, and it reports an **unprovable**
file rather than passing it. It carries the AST proof for Python, a
comment-stripped byte comparison for every other language with a `LANGUAGES`
record, and the line-ending check against an untouched sibling. ⚠ **Re-run it
after the formatter** — the formatter can reshape what you wrote.

⚠ **A `FAIL` or `UNPROVABLE` line is a stop, not a note.** The identity claim is
what this skill promises the people who run it; report the line verbatim and
restore the file. **An `UNCHECKED` line does not stop the run** — it means the
line-ending check had no untouched sibling to compare against, not that it
passed — but report it verbatim too, so the human deciding knows which claims
this run actually has a signal for.

**Edit through an exact-match tool, never raw text.** Measured, all caught only by the AST
proof: a path-rewrite regex reached inside a runtime `raise` message because it worked on raw
text instead of the block list; `open(..., newline="")` stripped CRLF from every file it
touched, in two separate runs, while the agent was reading this rail; a sweep regex without a
leading boundary doubled a directory prefix.

⚠ **A non-unique match is a re-review, not a `replace_all`.** N identical matches means N
blocks, and they may not deserve the same verdict. Reaching for `replace_all` once rewrote two
string literals.

**Extract before you cut, when the verdict is `move`.** Write the destination first, verbatim,
then remove the source. The other order loses the text on any interruption — three times,
before this became the rule.

**Re-read what you wrote, against the block-context rule.** The failure mode is producing exactly
what you are removing: a pass that cut seven obituaries wrote seven new ones, including the
same one twice in one file.

**Fix the whole claim, not the copy in front of you.** If the claim-dedup found the same
sentence in two files, both are in the same edit or neither is.

⚠⚠ **Every word you WRITE is bound by the STYLE SHEET; every word you did not touch is out of
scope.** There is no copy-editing reviewer, so this pass is where consistency is kept — but
only inside blocks a verdict already opened. Write in the sheet's dialect, capitalisation,
citation form and docstring convention; do NOT sweep the file for departures from it.

**A change no verdict asked for is out of scope** — a re-spelling, a dialect harmonisation, a
de-personalisation, an alignment with the neighbours. The residue check cannot see any of it,
because it only asks what was LOST. Measured: 14 dialect changes in one slice, in a codebase
whose identifiers use the other dialect. A departure in a block you are not editing is a
finding for the next run. Record any new decision on the sheet as you make it.

⚠⚠ **Touching a block obliges re-deriving its claim.** A mechanical repair — a renamed symbol,
a moved path — removes the only VISIBLE symptom of a stale block and leaves the claim behind,
strictly harder to find than before. Measured in three independent slices; in one, the same
six-line block carried a false claim, a repairable ghost and a stale path, and the pass fixed
only the ghost.

⚠⚠ **Run a FORWARD pass on anything you authored.** The residue check is inbound-only, so text
with no predecessor — an `add`, a coverage-driven docstring, a clause added while compacting —
is outside it entirely. Measured: **2 of 28** authored docstrings were confirmed false, and one
faithful compaction gained a clause with no antecedent anywhere. Ask of each addition: what
line settles this? The name of the function does not count.

⚠ **Re-resolve every pointer that names the block you edited.** Grep the file for *"see X's
docstring"*, *"the block above"*, *"for the reason Y gives"*. Measured twice: the defect lands
in a block the diff never touched, created by editing a different one.

⚠ **A verdict instructing what these rails forbid is a defect in the VERDICT.** Report it; do
not follow it. Measured: *"drop the comment and rewrite the user-facing string"* — the rails
say never change a string literal.

## Report

Edits applied, files touched, the AST-identity proof and how you ran it, and every block you
could not write with the reason — that is a finding, not a silence.

**Say explicitly whether every approved block landed byte-for-byte as approved.** A divergence
between what the author saw and what is on disk is the most serious thing this pass can
produce, and it is invisible in a diff that only shows the new text.

Then hand to stage 8 (REVIEW), which reads each changed file end to end and is the only pass
that can see damage the editing itself caused.
