# The numbers

Everything below prints from:

```bash
uv run python evidence/the-loop-measured-2026-08-27/derive.py
```

Four rounds, 706 marks. `clean` is the coverage record and `query` hands the place on, so a
**finding** here is `correct`, `patch`, `drop`, `add` or `move`.

## Per round

| round | marks | findings | roles | what it was |
| --- | --- | --- | --- | --- |
| 1 | 20 | 16 | 4 | a degraded brief; `clean` optional |
| 2 | 304 | 19 | 4 | the real brief, `clean` mandatory, `address` on every row |
| 3 | 304 | 18 | 4 | **byte-identical inputs to round 2** |
| 4 | 78 | 19 | 1 | `block-context` fanned out, one file per agent |

## Consistency, rounds 2 and 3

Byte-identical inputs, so any difference is the system's own variance.

    round2 19   round3 18   shared 9   union 28   Jaccard 0.32

!! **KEYED ON `(role, address)`, NEVER ON THE PROPOSED TEXT.** Two roles fixing one defect write
different prose for the fix, so keying on `change` scores the best-corroborated findings as
disagreements.

! **NOT RE-DERIVABLE HERE:** three of the non-overlapping findings were spot-checked by hand
against the source and all three were real. That is what makes the non-overlap **misses rather
than false positives**, and it is the reason coverage rather than agreement is the target. The
check was manual; nothing in `marks.jsonl` records it.

## Fan-out, round 4 against the two full rounds

`block-context` over one file per agent, against the same role in rounds 2 and 3.

| file | r2 | r3 | r2 u r3 | fanned |
| --- | --- | --- | --- | --- |
| `scripts:check_vocabulary.py` | 2 | 4 | 4 | 6 |
| `src:comment_review:binder:addresses.py` | 0 | 1 | 1 | 4 |
| `src:comment_review:machine:repo.py` | **0** | **0** | **0** | 2 |
| `src:comment_review:results:compositor.py` | 2 | 1 | 3 | 7 |
| **TOTAL** | 4 | 6 | 8 | **19** |

!! **`repo.py` RETURNED NOTHING IN EITHER FULL ROUND AND TWO WHEN READ ALONE.** Its places were
marked `clean` both times -- which is the coverage failure made legible, and the reason `clean`
must mean *I read this* rather than *this is correct*.

! **THE YIELD PER AGENT-RUN IS NOT HIGHER.** 4 and 6 findings for a whole round against 19 across
four fan-out agents. **The fan-out does not make an agent more productive; it makes coverage
guaranteed rather than sampled** -- no file can go unread when a file is all an agent has.

## The address form

Whether a mark's address carried its path, or only a bare cue:

| | carried a path |
| --- | --- |
| full binder | **628 of 628** |
| fanned out | **16 of 78** |

!! **A ONE-FILE BINDER MAKES A ROLE DROP THE PATH.** With one file in play the path reads as
redundant, and 62 of 78 marks came back as bare cues -- despite the row carrying the full address
and the packet saying to copy it. **A bare cue collides on merge: `a0` means four different
places**, and the fan-out results showed zero overlap with the full rounds until the differing
form was noticed.

## Sources

    382 citations across 9 roots

| root | citations |
| --- | --- |
| `src` | 259 |
| `scripts` | 87 |
| `corpora` | 9 |
| `prototype` | 9 |
| `TODO` | 7 |
| `docs` | 7 |
| `CLAUDE.md` | 2 |
| `plugins` | 1 |
| `tests` | 1 |

!! **`corpora/` IS GITIGNORED AND `prototype/` DOES NOT RUN.** Roles cited both as evidence
without being told they could, which is what settles that a source's scope is the **library** --
every file in the project under review -- and not the checkout. See `decision-log.md
Process: #33`.

## `ran`

    marks carrying a `ran`: 0

! **The field was proposed during these rounds and never exercised in them.** It records the
command that settled a claim, after one role's first pass ran on ambient Python 3.14 instead of
the pinned 3.11 floor and produced a false negative it caught only by re-running. **A verdict
grounded in a bad run is otherwise indistinguishable from a good one.** Ratified by Roy
2026-08-27; no role has yet been told it exists.

## Costs

!! **NOT RE-DERIVABLE FROM THIS PACKAGE.** Timings were observed while the rounds ran; nothing in
`marks.jsonl` records them. Kept because they are specific enough to be checked against a new run.

| | wall clock | tokens |
| --- | --- | --- |
| a full review round, per role | 400-770 s | 150k-230k |
| a revise pass | 27-86 s | 75k-86k |

! One order of magnitude, because a revise is one question over one paragraph rather than 76
places over four files. **The standing objection to re-review is cost, and the loop is not where
the cost is.**
