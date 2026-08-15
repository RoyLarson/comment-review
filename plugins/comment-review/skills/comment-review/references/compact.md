# The COMPACT pass — stage 6

Loaded by the task agent **after every block is edited (stage 5) and BEFORE the author is
asked to approve anything (stage 7)**. Never by a reviewer.

⚠⚠ **Nothing is on disk when this runs.** You are condensing PROPOSED text, not a file. That
is the point of the slot: the author must rule on the text that will actually be written, and
compacting after their approval would hand them one comment and write another.

## Why this is a separate pass over the whole tree

By the end of stage 5 every block is **true, in the right place, and stripped of history**.
Only then is it safe to ask how short it can be, and only then can the question be answered
correctly — because **compaction decisions depend on the final state of the tree, not of one
block**:

- a `move` relocates prose *between* blocks, so a block condensed before the move lands is
  condensed against a picture that is about to change;
- naming an **owner** collapses N restatements into one plus N pointers — the restatements only
  become compactable once the owner exists;
- a block that looks over-length often shrinks to nothing once the duplicated claim it carries
  is corrected somewhere else.

Condensing per-block during the EDIT gets all three wrong, and each error looks like a
successful edit.

⚠ **If any block is still marked incorrect or misplaced, stage 6 has not started yet.** Finish
stage 5.

⚠⚠ **An ESCALATED `query` does not block this pass, and must not.** Its destination is the
author, who is first reached at 7a -- *after* this stage. Read as "unresolved blocks stage 6", a
capped run holding one externally-unsettleable query could never legally reach approval.
Measured on a real run: two such queries, both settleable only inside a dependency outside the
checkout. **Compact the blocks whose verdicts are closed; carry an escalated query's block at
its full length and say why.**

## ⚠ This pass exists only to apply a CAP

**If no cap applies, this pass does not run at all.** Stage 5 already removed everything
false, historical and unnecessary, so what stands is true, current, local and load-bearing.
Absent a budget, "long" is not a defect and there is nothing here to do — go straight to
approval.

**Only shorten prose that is already correct.** This pass may not change a claim, relocate a
block, drop a constraint, or resolve anything stage 5 left open. If compacting makes you want
to do any of those, the EDIT was not finished — go back, or file it for the next run.

## Per block

1. **Take the ORIGINAL prose from the pre-edit text** — `git show <base>:<path>` where 1.1
   established a merge base, or **`git show HEAD:<path>` when `target` replaced the diff
   scope**, because then 1.1 never ran and `<base>` has no referent. Either way it is what is
   on disk today, which at this stage is still the UNEDITED text, and not your scratch copy.
   You are checking against what the block has ever said, not against your own last edit.
   ⚠ The blob is authoritative and cannot be lost to an interruption; keep the scratch copy
   only as a convenience.
2. **Cut, do not re-author.** For a block one or two lines over, remove the single
   least-checkable line — a hedge, an aside, a line restating the line below it. Measured:
   27 of 48 remaining runs were over by exactly ONE line, and re-authoring them all would
   have rewritten blocks that were already true, current and on-subject.
   ⚠ The four refusals still bind, and the least-checkable line is often a block's only
   refusal or the evidence for its surviving claim. If so it is not the line to cut, and the
   block reports at length.
3. **Re-run the residue check** on the condensed text against that same original: is anything
   in it **true & necessary & checkable** that the condensed version does not contain — and
   does the condensed version still pass the four refusals (not the only record of its fact;
   not what makes a surviving claim falsifiable; not a positional refusal aimed at a future
   editor; and what remains is still a proposition)?
4. **If it fails, put it back and try again.**

⚠ **Checking against your own EDITED text instead of the original is the failure mode this
pass is most likely to have.** The edit already dropped things legitimately; checking against
it lets a second, illegitimate drop through unnoticed. **The original is the baseline, twice.**

⚠⚠ **The block's KIND is part of the input, and it decides whether this pass may touch the
block at all.** The census stamps every block `comment`, `trailing-comment` or `docstring`, and
the two are governed by different rules:

| kind | governed by | what this pass may do |
| --- | --- | --- |
| `comment` / `trailing-comment` | **LENGTH** — the cap counts lines in one `#` run | cut it to the cap |
| `docstring` | **FORMAT** — the convention resolved at 1.3 | **nothing.** Long is not a violation |
| `comment` with `doc-kind-unresolved` | **UNKNOWN** — the census could not tell | **nothing.** Ask, or carry it at length |

**A cap never applies to a docstring.** Without the kind in front of you, a 107-line numpydoc
docstring and a 7-line `#` run look like the same over-length problem, and cutting the first to
six destroys documentation that was never in violation.

⚠ **A block whose kind is UNRESOLVED is not a block whose kind is `comment`.**
The census stamps `doc-kind-unresolved` where a language attaches documentation
by position (Go, Ruby) and this tier cannot separate a doc run from an ordinary
one. Do not infer it from the text, and do not cut it: carry it at length and
say why. Measured: a three-line Go export doc counted as over a cap of two.

⚠ **This is the input contract, and it is deliberately narrow:** the block's KIND, the original block, the
edited text, the cap, the style sheet. Not the reasoning that produced the edit. An agent that
never saw the argument cannot keep a sentence because it remembers writing it — which is what
makes this pass safe. ⚠ **It IS a separate subagent —
`comment-review:comment-review-compact` — not an optional handoff.** The
contract only buys anything if the reader is not the writer.

## When the cap cannot be reached

**STOP and report it** — the block, its true length, and what holds it there. Do not resolve
the conflict by cutting.

⚠ **A block that cannot be made both correct and short is a finding about the CODE** —
usually a rule with no owning function, so every site performing part of it re-explains the
whole. Trimming the comment treats the symptom. Report it, name the owner if you can see one,
and leave it.

⚠ **Never reach the cap by deleting evidence.** Between a comment that is over the cap and one
that is in-cap and unfalsifiable, **the over-cap one is correct and the in-cap one is a defect
wearing a passing grade.**

## Rails

Every rail in `apply.md` still applies. One is specific to this pass:

**Do not condense a block into the shape of its neighbours.** Matching surrounding style is how
a sentence survives review by resembling what is around it rather than by being needed.
Measured: a paraphrase reached for the word its sibling functions legitimately use, so the
wrong word read as house style and the result was wrong on two independent axes.

## Report

Blocks condensed, blocks left at length with the reason, and the final longest block. A block
you could not condense is a finding, not a silence.

⚠ **No AST-identity proof here** — nothing has been written yet. That proof belongs to the
sweep (stage 7b), which is the only pass that touches a file. What you hand back is the text
stage 7a will put in front of the author.
