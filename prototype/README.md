# prototype -- how it worked before

**Reference, not source.** Nothing here is imported, shipped or maintained. It
is kept because it is the record of a design that took months to reach, and the
replacement has not been designed yet.

Roy, 2026-08-25: *"all of the old code in the agent section are prototypes ...
moving it into a prototype/folder cleans the old code out once immediately but
leaves us appropriate references for how the system could work. Then we can
figure out how the system will work."*

## Two snapshots, and only one of them runs

| | what it is | runs? |
| --- | --- | --- |
| `original/` | **every shipped module as this branch opened**, at `b3d79d2` | **YES** |
| `middle/` | the same middle after the branch reshaped it, then moved out | no |

!! **`original/` IS THE ONE TO READ.** It is the whole system, coherent, at the
last commit before any of this branch's work -- nineteen flat modules with their
own path shims, exactly as they shipped. Roy asked for it because the middle
alone *"is only part of the prototype"*, and he was right: the middle in its
half-migrated state is the least useful version of it.

! **`middle/` IS KEPT ANYWAY** because it holds this branch's work on those
modules -- absolute imports, the series leaf, the reads that were corrected --
so a decision made during the refactor is not lost with the code it was made in.
Its imports name modules that moved out from under it, so it does not run.

## It still works, and that is the point

The chain, run from `original/` on 2026-08-25:

```
census.py --json      ok    10 rows, 18 fields each
record.py --seed      ok    4 slots seeded
record.py --check     ok
verdicts.py           rc=1  (coverage gaps -- 1 of 4 slots filled)
run_context.py        ok
vocabulary.py         ok    43/42/43/46 terms per role
```

**Eighteen fields per row.** That is the census before the cut of 2026-08-24
took eleven of them, and it is the clearest way to see what changed -- run it
and look, rather than read a ruling about it.

! `references/vocabulary.toml` is here for the same reason, frozen at the same
commit: `vocabulary.py` reads it relative to itself, and without it the last
step of the chain could not be demonstrated. **It is a snapshot and nothing
maintains it** -- the live one is `src/comment_review/references/`.

## Why the middle left

It is everything between the binder an agent reads and the galley that writes.
Roy, 2026-08-25: *"There is code there none of it is correct so testing it is
solidifying wrong."*

The chain it belonged to, ruled the day before (`decision-log.md Process: #14`):

```
binder -> agents -> NOTATIONS -> desk -> {address: new paragraph}
       -> workflow RELOADS the page
       -> galley -> compositor -> page again -> human
```

Everything from `binder ->` to `-> {address: new paragraph}` is what moved. The
two ends -- reading into a binder, and setting a page back -- stayed, and are
what `tests/` holds to.

## The move was clean, and that is worth recording

MEASURED before it: **zero** modules on the keep side imported anything in the
middle. Ten edges ran the other way -- the middle read `addresser`, `series`,
`lexer`, `binder` -- which is the direction a reference may read.

! That is the boundary work of 2026-08-24 paying for itself. The same move a
week earlier would have been a rewrite.

## What it leaves broken, deliberately

!! **`SKILL.md` NAMES SIX COMMANDS THAT NO LONGER EXIST** -- `record` twice,
`run_context` twice, `verdicts` and `vocabulary`. Stages 4 through 7 of the
shipped skill cannot be followed as written. Not an oversight: the agent-facing
design is what is being reconsidered, and rewriting those stages before deciding
the new one would be inventing the answer. Tracked in
`TODO/the-skill-names-commands-that-moved-to-prototype.md`.

! `references/reviewer-brief.md` still carries a GENERATED verdict table whose
marker points at `prototype/render_brief.py`. Nothing regenerates it.

## What to read it for

- **the verdict table** (`original/record.py`) -- seven verdicts and what each
  owes. The shape most likely to survive in some form.
- **the checks** (`original/desk.py`) -- what was mechanically checkable about a
  reviewer's answer: does the cited sentence exist, does the edit touch only
  what the claim names, does a citation resolve.
- **the coverage argument** (`original/record.py`) -- why every prose paragraph
  got a slot, so a paragraph nobody ruled on is a null verdict rather than an
  absence nothing can notice.
- **the join** (`original/verdicts.py`) -- what it means for four roles to
  disagree, and why the answer was never "pick one".
- **the eighteen-field row** -- run the census and look at what an agent was
  being handed.
