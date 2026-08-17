# Re-review is ordered in ten places and defined in none

```
Status:   open
Progress: 7 of 11 tasks done
Owner:    session * Roy (* 1 ruling)
Raised:   2026-08-17 (the first full run of 0.1.7 hit eight contradicted blocks and had to
          invent a procedure to clear them)
```

## Objective

**Ten sites tell the task agent to send a block back for re-review. Not one says what that is.**

- `SKILL.md` x 7 -- *"never to a tie-break"*, *"Re-review is normal"*, *"send the block back"*,
  *"you do not rule it here"*
- `verdicts.py` x 3 -- prints the block list and *"Not a tie-break. Send the block back"*
- `references/` held `compact.md`, `residue-check.md`, `review.md`, `reviewer-brief.md`,
  `write.md` and no `re-review.md`. ! It has one as of 2026-08-17 -- see the tasks below.

Every one of them says what a re-review is NOT, and who must not decide it. None says who reads
it, what they are given, what comes back, or when it stops.

! **A version was run on 2026-08-17 and it worked, which is why this is a decision and not a
bug.** It is one version among several and was invented mid-run. What it did:

- **Channel** -- `SendMessage` to the reviewers still holding their context, not a fresh
  `Agent` dispatch. Measured: both roles answered in ~2 minutes with **zero tool calls**. A
  fresh instance would have re-read a 165 KB census to answer eight questions.
- **Payload** -- the block, the role's own record, and the competing record in full.
  ! Roy ruled the independence objection out: blindness is what makes two roles AGREEING mean
  something, and it buys that in the first pass. Once they have disagreed the independent reads
  are on disk and are what the join read, so withholding the competing verdict in round two
  protects nothing and returns the same two answers.
- **First question** -- `SAME SENTENCE: yes|no`, before anything else. A verdict rules on a
  sentence and the join keys on the block, so the collision may not exist.
- **Return** -- `HOLD` or `REVISE`, one clause of reason, full payload on a revise.

Measured on those eight blocks: 8 HOLD from one role; 4 HOLD and 2 REVISE from the other. Both
revisions kept the verdict and shortened the payload, and neither role could have reached that
answer alone.

## Tasks

- [x] * **RULED 2026-08-17: `references/re-review.md`.** Roy: *"Re-review authorized"*. The
      term is already shipped -- ten sites order a re-review -- so the file takes the word that
      exists rather than coining one for the wider job it now covers.

      Was: Rule on whether this becomes `references/re-review.md`. Every other file in that
      directory owns one stage and carries an input contract and a return shape, which is what
      this now has. The alternative is a paragraph in `SKILL.md`'s stage 5. ! It cannot stay
      unwritten: it ran on a procedure one session invented, and the next session will invent a
      different one.

- [x] * **RULED 2026-08-17: round two reviews the JOINED RESOLVED BLOCK, not the contradiction.**

      Roy: *"you ruled that the apply would send back only the reviewer's CHANGE but that
      defeats the purpose, because a reviewer would then just be stating yes I said that would
      fix it. The block change is already done, sending it right back doesn't help. Sending the
      joined resolved block back to the reviewers that had comments does help because each can
      say yes my edits made it and are correct and the other edits do not negate that or cause
      mine to be wrong."*

      So the question a round-2 reviewer answers is not *"do you stand by your verdict"* -- it
      is three questions about stage 5's synthesis:

      1. Did my edit SURVIVE into the joined block?
      2. Is it still correct THERE?
      3. Do the other edits negate it, or make it wrong?

      ! **Only the third can be answered by anyone but that reviewer, and only after the join.**
      No round-1 reviewer saw the other findings, so nothing before this point could ask it.

- [x] !! **BLOCKER CLEARED 2026-08-17 -- `scripts/galley.py`, and `verdicts.py` did not change.**

      Was: `verdicts.py` assumes ROUND ONE and cannot admit a round-2 record, because round 2's
      subject is the synthesised block -- text on no disk and in no census -- so
      `address_problem` refuses it and `edit_problem` measures one claim against one edit when
      the block now holds several.

      **The option taken is the first of the three: a second census over the proposed text.** A
      GALLEY is the proposal spliced into a COPY of each file; censusing it gives every proposed
      block a real address and a real transcription, so a round-2 record is an ORDINARY record
      that happens to cite a different census. Demonstrated end to end on this repo's own census:
      a block re-worded through the galley came back as `census.py:76-76` with its new text in
      `raw_lines`.

      ! The two rejected options are why: a distinct round-2 record shape is a second contract to
      hold in sync with the first, which is the two-copies-of-a-rule defect this repo spends its
      days catching; and `--round 2` selecting a different check set turns the checks off for the
      one text the author actually approves, which this task's own wording forbade.

      !! **INDICES DO NOT SURVIVE THE GALLEY, and nothing should pretend they do.** A replacement
      whose line count differs shifts every block below it, so the same prose is index 123 in the
      run census and 31 in the galley's. **Round 2 is self-consistent against its own census, and
      maps back to round 1 by PATH AND CONTENT, never by index.** The task agent holds both
      records and is the only participant that can relate them.

      ! `galley.py` REFUSES rather than guesses: a census range that no longer matches the file,
      two edits over one line, or an index outside the census stops that file instead of writing
      a galley nobody can trust. Its exit is nonzero when anything refused, because a galley
      missing a block is not a galley of the proposal.

- [ ] Decide WHICH BLOCKS get a round two. Roy's model -- *"the reviewers that had comments"* --
      is any block where two or more roles filed a finding, not only the contradicted ones.
      ! Measured on a live run: **51 of 150 blocks** had 2+ roles converge, against 8 flagged as
      contradictions. That is a 6x change in how often round two fires, and it is a cost
      decision, not a detail.

- [x] **WRITTEN 2026-08-17: `references/re-review.md`**, and `SKILL.md` now loads it -- both in
      the references list at the top and at the *"Re-review is normal"* paragraph, which had
      ordered a re-review for ten sites' worth of prose without naming what one is. The file
      carries what the role is given, the three questions, the return shape, the channel and the
      stop rule.

- [x] **The CHANNEL is stated, with the measurement.** Message the roles that still hold their
      read; do not dispatch fresh ones. Measured 2026-08-17: two roles answered in about two
      minutes with ZERO tool calls, where a fresh instance would have re-read a 165 KB census to
      answer eight questions. ! A role that cannot be reached is replaced and **that is said in
      the report** -- it answers from the record rather than from its own read, and the two are
      not the same evidence.

- [x] ! **TERMINATION: one round, then the author** -- and this one is the SESSION'S call, not a
      ruling. If a block comes back split it reaches the author as a `query` carrying both
      answers. The argument is this file's own: once both roles have seen each other's records,
      **a second round between the same readers returns the same two answers**, because nothing
      further enters the argument. ! Overrule it if the cost of a `query` to the author turns out
      higher than another round; nothing measured either.

- [x] **Recorded: what the run measured about the GATE.** 8 blocks flagged, **2 genuine
      contradictions**; six were composition or a sentence-level false positive. It is in the
      file as the reason `SAME SENTENCE` is answered FIRST -- see
      [`move-and-correct-compose`](move-and-correct-compose.md) and
      [`the-unit-of-review-is-the-statement-not-the-block`](the-unit-of-review-is-the-statement-not-the-block.md).

- [ ] * **WHICH BLOCKS get a round two -- still open, and it is a COST decision.** Roy's model,
      *"the reviewers that had comments"*, is any block where two or more roles filed, not only
      the contradicted ones. ! Measured on a live run: **51 of 150 blocks** had 2+ roles
      converge, against 8 flagged as contradictions -- a 6x change in how often round two fires.
      ! **Deliberately NOT in `re-review.md`.** That file defines the mechanism; WHEN it fires is
      the caller's, the same way `compact.md` defines compaction and `SKILL.md` says stage 6 is
      skipped without a cap.

- [ ] Decide whether a re-review may be dispatched to a role that did NOT rule on the block.
      The run sent only to the two roles that collided. Widening it costs a re-read; not
      widening it means a third role never learns the block was contested. ! Partly answered:
      the third case -- a block stage 6 must edit that NO role ruled on -- goes to all four, and
      that is in the file. What is open is whether a CONTESTED block widens beyond its filers.

- [ ] ! `re-review.md` is PASTED into a round-2 message the way the brief is, so no agent file
      names it -- which means `check_vocabulary.py` does not cover its terms for those roles. It
      introduces one: **galley**. Defined inline there today. Decide whether it earns a
      `vocabulary.toml` entry when 5b/6b are wired into `SKILL.md`'s stages.
