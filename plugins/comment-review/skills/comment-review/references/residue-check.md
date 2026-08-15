# The RESIDUE CHECK — loaded at stage 5, used at 5, 6 and 8

The one mechanism that catches an edit which kept a false sentence and dropped
the evidence disproving it. It is **inbound and per-block**: *did this block
lose something?*

⚠ **It is NOT stage 8's proof pass.** That one asks *does the finished page
read?* A run can satisfy this check everywhere and still fail that one, and
that is the common case, because each edit was defensible alone.

Loaded at **stage 5**, where the first replacement text is written. Stage 6
re-runs it on condensed text, and stage 7b runs it on what it applies — all
three against the SAME original, never against the previous edit.

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
