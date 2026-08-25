# prototype -- how the middle of the chain used to work

**Reference, not source.** Nothing imports this, nothing ships it, and it does
not run: its imports name modules that moved out from under it. It is kept
because it is the only record of a design that took months to reach, and the
replacement has not been designed yet.

Roy, 2026-08-25: *"all of the old code in the agent section are prototypes and
can be either be moved into an appropriate folder or commented out. I would go
for moving it into a prototype/folder so it cleans the old code out once
immediately but leaves us appropriate references for how the system could work.
Then we can figure out how the system will work."*

## Why it left

It is the MIDDLE of the chain -- everything between the binder an agent reads
and the galley that writes. Roy, 2026-08-25: *"There is code there none of it is
correct so testing it is solidifying wrong."*

The chain it belonged to, ruled the day before (`decision-log.md Process: #14`):

```
binder -> agents -> NOTATIONS -> desk -> {address: new paragraph}
       -> workflow RELOADS the page
       -> galley -> compositor -> page again -> human
```

Everything from `binder ->` to `-> {address: new paragraph}` is what this folder
holds. The two ends -- reading into a binder, and setting a page back -- stayed,
and are tested by `tests/`.

## What moved, and where it lived

| here | was |
| --- | --- |
| `desk/desk.py` | `src/comment_review/desk/desk.py` |
| `desk/verdicts.py` | the join -- reports against the census, citations checked |
| `desk/run_context.py` | the dispatch packet a run was checked against |
| `desk/vocabulary.py` | the terms one role was handed |
| `binder/record.py` | the shape a reviewer filled, and the verdict table |
| `binder/held.py` | reading a filled record back |
| `commands/*.py` | their console faces |
| `render_brief.py` | generated the brief's verdict table FROM `record.VERDICTS` |
| `tests/*.py` | everything that asserted how any of it behaved |

## The move was clean, and that is worth recording

MEASURED before it: **zero** modules on the keep side imported anything here.
Ten edges ran the other way -- the middle read `addresser`, `series`, `lexer`,
`binder` -- which is the direction a prototype may read.

! That is the boundary work of 2026-08-24 paying off. A year of this code being
tangled would have made the same move a rewrite.

## What it leaves broken, deliberately

!! **`SKILL.md` NAMES SIX COMMANDS THAT NO LONGER EXIST** -- `record` twice,
`run_context` twice, `verdicts` and `vocabulary`. Stages 4 through 7 of the
shipped skill cannot be followed as written. That is not an oversight: the
agent-facing design is what is being reconsidered, and rewriting those stages
before deciding the new one would be inventing the answer. Tracked in
`TODO/the-skill-names-commands-that-moved-to-prototype.md`.

! `references/reviewer-brief.md` still carries a GENERATED verdict table. Its
marker now points here, so a reader can find the generator; nothing regenerates
it.

## What to read it for

- **the verdict table** (`binder/record.py`) -- seven verdicts and what each
  owes. The shape most likely to survive in some form.
- **the checks** (`desk/desk.py`) -- what was mechanically checkable about a
  reviewer's answer: does the cited sentence exist, does the edit touch only
  what the claim names, does a citation resolve.
- **the coverage argument** (`binder/record.py`) -- why every prose paragraph
  got a slot, so a paragraph nobody ruled on is a null verdict rather than an
  absence nothing can notice.
- **the join** (`desk/verdicts.py`) -- what it means for four roles to disagree,
  and why the answer was never "pick one".
