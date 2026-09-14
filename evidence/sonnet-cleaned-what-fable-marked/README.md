# Sonnet cleaned what Fable marked

One ownership-context edit copy, returned `clean` at every place, against the marks forks of
the same role made over the same binder -- each mark graded against the code the run read.

## The run

- 2026-09-06, a comment-review run over this repository's own `src/`: 71 pages --
  `src/comment-review.py`, 69 Python files under `src/comment_review/`, and
  `src/comment_review/references/vocabulary.toml`. One stage, `4`, all four roles.
- The tree was `ab0f9266`. The binder records no commit: its `read_from` root is `.`. Every
  one of its 71 page shas (`machine.repo.sha_of`, the first 16 hex of the SHA-256 of the
  file text) reproduces from the blobs at `ab0f9266`, and at `a40e713d` and `edd48049`, whose
  pages are identical.
- The run's files -- the binder, the copies, `compare_oc.py`, and the forks' part files -- are
  untracked, in the 2026-09-06 session's scratchpad under the Claude temp directory
  (`826e369a-7629-4459-a72a-8fbb9f6fc215\scratchpad\run-2026-09-06\` and `oc_parts\`), present
  there on 2026-09-13.

## The two sides

Which model produced which file is as recorded by `reviewer-prose-is-rules-not-guidance` T6's
note, not re-derived from the files.

- **Sonnet** -- the live ownership-context role: `copies/4_ownership-context_1.json`, 71
  sheets and 888 slots. All 888 are filled, every one `clean`.
- **Fable forks** -- forks of the same role over the same binder, in eight part files `g1`-`g8`.
  - Three carry marks in the envelope `compare_oc.py` reads: `g1` (`reading/`), `g5`
    (`flows/`) and `g6` (`commands/`).
  - Together they fill 303 places: 239 `clean`, 27 `move`, 26 `drop`, 6 `correct`,
    3 `patch`, 2 `query`.
  - `g2`, `g4`, `g7`, `g8` and `g3.json` are unfilled seeds.
  - `g3_marks_1.json` holds 132 marks, 24 of them other than `clean`, at 15 places in
    `binder/` and `flows/gather.py`. `compare_oc.py` does not read it, and they are not
    graded here. So the forks marked at least 79 places other than `clean`; 64 are graded.

## What was measured

At the 64 places a fork marked other than `clean`, the Sonnet copy says `clean` at all 64.

Each of the 64 was graded against the code at `ab0f9266`, from the code and not from the
mark's reason or confidence.

| verdict | count |
| --- | --- |
| real | 64 |
| not real | 0 |
| cannot tell | 0 |

**`real` means the defect the mark names is present in the code at that commit:**

| instruction | what `real` requires |
| --- | --- |
| `drop` | the same claim stands at the site named as owner |
| `move` | the paragraph is about other code, narrates the past, or quotes a ruling `docs/decision-log.md` does not carry |
| `correct` | the false half is false |
| `patch` | the cited log entry carries the quoted words |
| `query` | the contradiction it names is in the code |

The replacement text each mark proposed was not graded.

**What each finding rests on:**

| basis | rows |
| --- | --- |
| the role file's remit -- anchoring, one owner, narration of the past | 45 |
| the run's style sheet -- a quotation of Roy in shipped code is a citation to the log | 16 |
| a code concern, raised as a `human-review-necessary` query | 2 |
| the truth of an assertion (a `correct` on an import claim) | 1 |

## How each was checked

- Per row, a `grep` or a `file:line` reading in a detached worktree at `ab0f9266`. The
  64-row table, with the evidence line for each, is [`grades.md`](grades.md).
- Whether a quoted ruling is in `docs/`: a whitespace-normalised search over every
  `docs/**/*.md`, so a quotation the log wraps across lines is still found, and a line
  `grep` of a short fragment of each quote.
- A `move` into tracked code: its destination was resolved with
  `addresser --file --line --series` against the run's binder.
- One grader, one pass.

## Not measured

- The Sonnet copy's other 824 `clean`s: 239 at places a fork also said `clean`, and 585 at
  places no fork's part file reached.
- The 15 places in `g3_marks_1.json`.
- The quality of the changes the marks proposed.
