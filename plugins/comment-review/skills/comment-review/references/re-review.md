# RE-REVIEW -- every round after the first

Loaded by the task agent when a block goes back to the roles that ruled on it. **Ten sites order
a re-review; this is the only one that says what one is.**

!! **A RE-REVIEW IS NOT RELITIGATION.** *"Reconsider your verdict"* is unanswerable -- nothing
has changed since the role formed it, so it returns the verdict it already filed. What HAS
changed is that stage 5 turned several verdicts into ONE block, and **the filer is the only
participant who can say whether that block still carries what it filed.**

! **MARK and APPLY stay separate.** The finding is already filed and already read by the join.
The role is not fixing anything; it is answering whether the fix matches what it asked for.
Blindness protects the FIRST read, and that read is banked on disk.

## The subject is the JOINED BLOCK, never the finding

Roy, 2026-08-17: *"you ruled that the apply would send back only the reviewer's CHANGE but that
defeats the purpose, because a reviewer would then just be stating yes I said that would fix it.
The block change is already done, sending it right back doesn't help."*

So a role is sent the block **as stage 5 or stage 6 left it**, holding every role's edits at
once, and answers three questions about it:

1. Did my edit SURVIVE into this block?
2. Is it still correct THERE?
3. Do the other edits negate it, or make it wrong?

!! **Only the third could not be asked before now.** No round-1 reviewer saw another role's
findings, so nothing earlier in the pipeline could put this question to anyone.

!! **SO A BLOCK GOES BACK TO THE ROLES THAT FILED ON IT, AND TO NO OTHERS.** Ruled 2026-08-17.
All three questions are about the role's OWN edit -- did it survive, is it still correct, did
the others negate it -- and a role that filed nothing has no edit to answer for. Handing it the
joined block asks a different question in the same envelope, and it would come back with what a
first reading returns rather than what a re-review returns.

! **A third role CAN be sent that block; it is a FRESH REVIEW and it is stage 4's, not this
file's.** That route already exists for the case below, where nobody filed at all, and it runs
6 -> 4. What is forbidden is calling it a re-review: the round comes back with verdicts on a
block, which is what stage 5 joins, and not with answers about an edit, which is what stage 5b
reads.

! **The cost of the narrow rule is stated so it is not mistaken for free**: a role whose remit
the merged text now violates does not hear about it here. Stage 6b catches what compaction
broke, and stage 8 reads the finished page against itself -- but between the two, a block that
became wrong for a role that never filed on it reaches the author.

## Two slots, and they ask different things

| | runs after | the question | what it catches |
| --- | --- | --- | --- |
| **5b** | APPLY | *is this what you meant?* | a synthesis that misread a finding |
| **6b** | COMPACT | *is this still correct after my edits?* | compaction that cut what the finding rested on |

!! **They are not interchangeable and must not be collapsed.** A single *"is this still right"*
prompt answers neither: 5b asks whether the synthesis carried the finding, 6b asks whether
shortening broke it.

! **6b is the only reader of stage 6's output before the author sees it.** The compact agent
reads stage 5's work; nothing else reads the compact agent's own. Stage 7a presents and rules on
nothing, the CODE CHECK reads only executable code, and stage 8 runs after the write.

## The third case: a block NO role ruled on

**A block stage 6 must edit that carries no verdict goes to ALL FOUR roles as a fresh block, and
comes back with verdicts.** A block every role returned `clean` on can still be over the cap;
compacting it is an edit with nothing behind it, and neither 5b nor 6b reaches it because there
is no filer to ask.

! It is the only path by which stage 6 originates work, and it runs the opposite way to
everything else: every other finding travels 4 -> 5, this one travels 6 -> 4.

## What the role is GIVEN

- **The joined block**, in full, as it now reads.
- **Its own record**, so it is not answering from memory.
- **The other records on that block, in full.** ! The independence objection is ruled out:
  blindness is what makes two roles AGREEING mean something, and it bought that in round one.
  Once the reads are on disk, withholding the competing verdict protects nothing.
- **Where the block now lives** -- its address in the galley census, if one was taken.

!! **The joined block is on no disk and in no census until a GALLEY is set.** `galley.py`
splices the proposed text into a copy of its file; censusing that copy gives the block a real
address and a real transcription, so **a round-2 record is an ORDINARY record** and every check
in `verdicts.py` applies to it unchanged.

! **Cite the galley census, and do not carry a round-1 index into round 2.** A replacement whose
line count differs shifts every block below it, so the same prose holds different indices in the
two censuses. They relate by PATH and CONTENT; only the task agent holds both.

## What comes back

```text
SAME SENTENCE  yes | no
VERDICT        HOLD | REVISE
REASON         one clause
```

- **`SAME SENTENCE`** is answered FIRST, because **two marks on two different sentences
  COMPOSE** -- they are not a conflict, however much they share a block. Ruled 2026-08-17. ! The
  join already keys on the edited span rather than the block index, so most of this is caught
  before you are asked; you are the last check on it, and the only one that can read the
  sentences as sentences. ! Measured 2026-08-17: of 8 blocks the gate flagged, **2 were genuine
  contradictions**; six were composition or a sentence-level false positive.
- **`HOLD`** -- the block carries what I filed, and the other edits do not break it. Nothing
  further is owed.
- **`REVISE`** -- it does not, and the **full record** comes with it, in the shape
  `reviewer-brief.md` gives. A revise without its payload is not a finding, in round two exactly
  as in round one.

## The channel

**Message the roles that still hold their read. Do not dispatch fresh ones.** A role that
reviewed this run holds the census, the code and its own reasoning already.

! Measured 2026-08-17: both roles answered in about two minutes with **zero tool calls**. A
fresh instance would have re-read a 165 KB census to answer eight questions.

! Where a role can no longer be reached, a fresh one is given the same payload as any other and
that is **said in the report** -- it is answering from the record rather than from its own read,
and the two are not the same evidence.

## When it stops

**AT MOST TWO re-review rounds, and then the APPLIER judges.** Ruled 2026-08-17. Counting, so
nobody has to guess it: stage 4 is the first read and is not a round here. A block may go back
twice. If it is still split after the second, **stage 5 rules on it** -- it does not go to the
author and it does not go back a third time.

!! **This does NOT license a tie-break, and the distinction is the whole rule.** *"Never a
tie-break"* forbids stage 5 preferring one role over another INSTEAD OF sending the block back.
Ruling after two rounds is not that: the process has been run and has not converged, and the
applier is the participant holding every record, both rounds of answers, the census and the
code. Deciding then is its job. Deciding first is the thing it may not do.

! **Say in the report which blocks were ruled this way, and on what.** A block stage 5 settled
because two rounds did not converge is a weaker result than one the roles agreed on, and the
two must not read alike.

! Measured 2026-08-17: both genuine contradictions resolved in the FIRST round -- 8 HOLD from
one role, 4 HOLD and 2 REVISE from the other, and both revisions kept the verdict and shortened
the payload. **Nothing has yet reached a second round**, so the bound is a decision about cost,
not a response to a measured failure.

## Rails

- **Never a tie-break.** Two roles disagreeing is not a vote, and the task agent does not break
  it by preferring one. It goes back, or it goes to the author.
- **A `REVISE` re-enters the join.** It is a record like any other and is checked like any
  other; it does not bypass `verdicts.py` because it arrived late.
- **Nothing is on disk.** Both slots run before stage 7, and 5b runs before COMPACT has touched
  anything. A galley is a copy, and it is discarded with the run.

## Report

Blocks sent, per slot; `HOLD` and `REVISE` counts per role; every block still split after one
round, named, with both answers. ! A block that went back and returned nothing is a finding, not
a silence.
