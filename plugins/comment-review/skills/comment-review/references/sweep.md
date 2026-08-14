# Stage 7b — APPROVAL: apply what the human approved

Loaded by the task agent **after approval**, never by a reviewer. If you are reading this
before the human has approved a verdict list, stop.

Apply only what was approved, and only what was marked. ⚠ **An unmarked block is never swept.**
If the sweep wants to touch something the mark did not reach, that is a finding for the next
run, not an edit.

## The residue check

For every block being changed, in this order:

1. **Copy the ORIGINAL block whole into a scratch document** — the full prose, verbatim, with
   its `file:start-end`. Not a summary, not the half you plan to cut: the whole thing.
2. **Write the new comment.**
3. **Read the new against the original and ask, of each ORIGINAL sentence:** is there anything
   here that is **true & necessary & checkable** that the new comment does not contain?
4. **If yes, it is not finished.** Put it back and repeat from 3.
5. Only when the answer is no has the block reached CORRECT. Keep the scratch copy until the
   whole pass is done.

⚠ **Write for correctness, not length.** At steps 2–4 the new comment may be **longer** than
the original, and that is an acceptable intermediate state. A residue check run against text
already trimmed to fit is checking the wrong document.

⚠ **Run it after EACH edit, not once at the end.** Its whole value is that the original is
still in front of you; a batch check at the end is a check against your memory of what you cut.

⚠ **It is asymmetric on purpose.** It asks only what the original had that the new one lacks —
never whether the new one is shorter, which was already decided. **This is the only mechanism
here that catches a compaction which kept the false sentence and dropped the evidence that
disproved it**, because at step 3 that evidence is still on the page.

## ⚠⚠ Four removals the three conjuncts miss

Refuse a removal unless **all four** also hold. Each was measured as a cut later judged wrong,
and each passes `true & necessary & checkable` cleanly:

- **NOT the only record of its fact in the tree.** Ask what, in the working tree, this
  sentence is the only statement of. A true, checkable, apparently-unnecessary sentence can be
  the one place a live-but-unread config key is recorded as dead.
- **NOT what makes a surviving claim falsifiable.** The provenance — a date, a pointer, a
  grepable name — is what lets the next reader test the sentence you kept. Deleting it leaves
  a claim that is *harder to disprove* than before.
- **NOT a refusal aimed at a future editor AT THIS LOCATION.** Its value is positional; moved
  to a document, it is read by nobody making the edit it forbids.
- **What remains is STILL A PROPOSITION** — subject, referent, and a claim. ⚠ A stump fails
  *every* conjunct, so the check reports clean when the correct answer is **restore**.

## Shorten by TRUTH here — never by LENGTH

**This pass cuts, and it can cut a lot.** Every false statement, every piece of history, every
dead citation, every sentence that narrates what the code already says — all of that goes here.
It also *adds*: correcting a claim usually means restoring the evidence that disproves it, and
naming a caller obligation adds a sentence that was never there.

**What comes out is a CORRECT comment: as long as it needs to be to carry only what is true,
current and load-bearing, and no longer than that.** It may end up far shorter than the
original, or longer. Both are right.

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

**Prove code identity; do not assert it.** Parse both versions, blank every docstring
`Constant`, compare `ast.dump`. Comments never reach the AST, so anything else that differs
fails the check. **Re-run after the formatter** — it can reshape what you wrote.

⚠⚠ **Check LINE ENDINGS against an UNTOUCHED SIBLING FILE — never against the blob.** The AST
is blind to endings, so a whole-file flip passes identity and lands as a diff touching every
line. Measured four times; the edit tool rewrites endings on its own and `git stash`/`pop`
re-applies them.

⚠ **The blob is the wrong baseline and this rail used to name it.** Under `core.autocrlf` the
stored blob is always LF, so normalising to it produces a working tree inconsistent with every
file you did not touch — and `git diff` hides the damage. Measured: a run normalised to the
blob, passed the AST proof, the residue check, the gate and 579 tests, and left the tree
internally inconsistent. Read a file in the same directory you did not edit, and match it.

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

**Re-read what you wrote, against the currency rule.** The failure mode is producing exactly
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
