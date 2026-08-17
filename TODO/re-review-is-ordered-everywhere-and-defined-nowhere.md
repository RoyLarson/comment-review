# Re-review is ordered in ten places and defined in none

```
Status:   open
Progress: 0 of 5 tasks done
Owner:    session · Roy (⭐ 1 ruling)
Raised:   2026-08-17 (the first full run of 0.1.7 hit eight contradicted blocks and had to
          invent a procedure to clear them)
```

## Objective

**Ten sites tell the task agent to send a block back for re-review. Not one says what that is.**

- `SKILL.md` × 7 — *"never to a tie-break"*, *"Re-review is normal"*, *"send the block back"*,
  *"you do not rule it here"*
- `verdicts.py` × 3 — prints the block list and *"Not a tie-break. Send the block back"*
- `references/` holds `compact.md`, `residue-check.md`, `review.md`, `reviewer-brief.md`,
  `write.md`. There is no `re-review.md`.

Every one of them says what a re-review is NOT, and who must not decide it. None says who reads
it, what they are given, what comes back, or when it stops.

⚠ **A version was run on 2026-08-17 and it worked, which is why this is a decision and not a
bug.** It is one version among several and was invented mid-run. What it did:

- **Channel** — `SendMessage` to the reviewers still holding their context, not a fresh
  `Agent` dispatch. Measured: both roles answered in ~2 minutes with **zero tool calls**. A
  fresh instance would have re-read a 165 KB census to answer eight questions.
- **Payload** — the block, the role's own record, and the competing record in full.
  ⚠ Roy ruled the independence objection out: blindness is what makes two roles AGREEING mean
  something, and it buys that in the first pass. Once they have disagreed the independent reads
  are on disk and are what the join read, so withholding the competing verdict in round two
  protects nothing and returns the same two answers.
- **First question** — `SAME SENTENCE: yes|no`, before anything else. A verdict rules on a
  sentence and the join keys on the block, so the collision may not exist.
- **Return** — `HOLD` or `REVISE`, one clause of reason, full payload on a revise.

Measured on those eight blocks: 8 HOLD from one role; 4 HOLD and 2 REVISE from the other. Both
revisions kept the verdict and shortened the payload, and neither role could have reached that
answer alone.

## Tasks

- [ ] ⭐ Rule on whether this becomes `references/re-review.md`. Every other file in that
      directory owns one stage and carries an input contract and a return shape, which is what
      this now has. The alternative is a paragraph in `SKILL.md`'s stage 5. ⚠ It cannot stay
      unwritten: it ran on a procedure one session invented, and the next session will invent a
      different one.

- [ ] State the CHANNEL as a rule, with the measurement. Nothing in the shipped tree describes
      resuming an agent at all — stage 4 is a single dispatch and no file mentions a second one.

- [ ] Decide when it TERMINATES. If round two comes back split, is there a bound, or does the
      block reach the author as a `query`? The 2026-08-17 run did not hit this: both real
      contradictions resolved in one round.

- [ ] Decide whether a re-review may be dispatched to a role that did NOT rule on the block.
      The run sent only to the two roles that collided. Widening it costs a re-read; not
      widening it means a third role never learns the block was contested.

- [ ] Record what the run measured about the GATE, since it is the reason re-review fired at
      all: 8 blocks flagged, **2 genuine contradictions**. Six were composition or a
      sentence-level false positive — see
      [`move-and-correct-compose`](move-and-correct-compose.md) and
      [`the-unit-of-review-is-the-statement-not-the-block`](the-unit-of-review-is-the-statement-not-the-block.md).
