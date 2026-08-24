# Three different things are called `declares`, in a repo built on one name per thing

```
Status:   deferred
Progress: 6 of 11 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, reading a census entry: 'in a system that is a
          lot of having one-name for a thing, 3 things called declares seems like a code
          smell')
TRIAGED:  2026-08-23 -- NINE OF THE ELEVEN BOXES WERE NOT TASKS. They were the
          measurement of the thirteen spellings, the settled definition, three PROPOSED
          names, a finding about the sweep, the redundancy argument, a dead field, and
          Roy's sequencing ruling -- every one of them true the day it was written and
          every day after, with no state in which anyone ticks it. All nine are ticked and
          their content is in the Objective above the tasks; the record stays. FIVE TASKS
          replace them, each a rename or a check with a command behind it.
          ! RE-MEASURED 2026-08-23, all three relatives still live: `Paragraph.declares`
          is `lexer.py:134` (set at :1617 and :1899, read at `page.py:316-318`),
          `Language.declares` is `language.py:89` (a keyword tuple, populated on every
          row), `desk.declares_scope` is `desk.py:701` with `can_declare_scope` at
          `record.py:158`. ! STATUS CHANGED open -> deferred, on the ruling already in
          this file: Roy, 2026-08-21, *"one-stem-four-jobs can be its own branch after
          the python branch."* Deferred is not done; the boxes still say the work remains.
```

## Objective

**Thirteen spellings on one stem, and the vocabulary defines one of them.** Roy, 2026-08-21,
reading a census entry that said `comment ... declares=-1`: *"in a system that is a lot of having
one-name for a thing, 3 things called declares seems like a code smell."*

MEASURED 2026-08-21, across the shipped tree: `declaration` 98, `declares` 41, `declarations` 16,
`declared` 13, `declaring` 11, `_declared` 8, `declare` 8, `declares_scope` 5, `can_declare_scope`
4, `document_declarations` 4, `_declares_here` 2, `Declaring` 1, `declared_at` 1.

`references/vocabulary.toml` settles **`declaration`** -- *"Something that can carry DOCUMENTATION
-- a module, class, function, method, struct -- and so what an `a` place is about."* **That
definition is correct and STAYS.** Three relatives borrowed the stem for other jobs:

| now | where | what it holds | proposed |
| --- | --- | --- | --- |
| `Paragraph.declares` | `lexer.py:134` | the ordinal of the declaration a run **documents** | `documents` |
| `Language.declares` | `language.py:89` | a tuple of **keywords** that introduce one | `introduces` |
| `desk.declares_scope` | `desk.py:701` | a `query` **announcing** the paragraph is not this role's | `reports_remit` |

!! **`Paragraph.declares` STATES THE RELATIONSHIP BACKWARDS**, and it is the one that misleads
rather than merely crowds. A docstring declares nothing; `def f():` is the declaration and the
prose documents it. ! `Cues.documents(ordinal)` already answers that exact question in the
right word -- `page.py:318` calls it with the value of `declares` -- so one module asks in one
vocabulary and another answers in a second.

! **`declares_scope` is the same class of error as `acquittal` and `jurisdiction`**: a word from
outside publishing, checked for collisions and never for register. `remit` is what replaced
`jurisdiction` for this reason, and it is the word this predicate wants. CLAUDE.md's rule is to
check the register BEFORE proposing.

## Why the sweep does not see it

!! **`scripts/vocabulary_sweep.py` emits ZERO rows matching `declar`.** It lists terms of art the
inventory does not hold, and `declaration` IS in the inventory -- so every relative of the stem
passes. **The defect is not an unlisted word; it is a listed word doing three jobs**, and a word
match cannot express that. ! POLYSEMY IS INVISIBLE TO A WORD MATCH, which is a finding about the
instrument and not about this rename.

## The rename shrinks if the field stops being external first

Roy, the same day: *"Do we need the declares as an external field? I think that may be an internal
implementation detail to the lexer."*

MEASURED: `census.py` writes `vars(b)`, so all 17 paragraph fields reach the agents. But the field
is needed for ONE hop -- the lexer states it, `page.attach` reads it to pick which `a`. After the
address is stamped, `@a5` carries the same fact and is what every other consumer already keys on.

! **The tree shows the redundancy three ways.** `page.py:487` sets `declares=int(cue_name[1:])` on
synthetic empty places, deriving the field from the cue it duplicates. `addresser.for_anchor`
reads it twice (`addresser.py:1009`, `:1042`) where `series_of(address)` is the module's own
stated rule three lines below: *"an `a` declares, a `c` has a column, a `b` has neither. No second
field, no inference from kind."* The `a` branch is the one that uses a second field.

## Not in scope

`declaration`, `declarations`, `declaring` and `declared` as ordinary grammar of the settled term.
`declared_at` needs nothing -- it is already dead, surviving only in comments recording that it
became `anchor_line`.

## Sequencing

* **RULED by Roy, 2026-08-21: *"one-stem-four-jobs can be its own branch after the python
branch."*** ! The order is not arbitrary -- `Paragraph.declares` is the field the python work
either keeps or replaces, so renaming it first would rename something that may not survive. That
ruling is why this file is `deferred` and what it waits on:
[`python-cannot-read-python`](python-cannot-read-python.md).

## Tasks

- [ ] T1 -- Rename `Paragraph.declares` to `documents` (`lexer.py:134`, set at `:1617` and
      `:1899`, read at `page.py:316-318`). Verify: `grep -rn 'declares' plugins/` returns no
      paragraph-field use, `page.py` asks `cues.documents(...)` with a field of the same name,
      and the census round trip is unchanged on the fixture corpus.

- [ ] T2 -- Rename `Language.declares` to `introduces` (`language.py:61`, `:89`, and every row
      that populates it, plus `lexer._declares_here` at `lexer.py:1503`). Verify: `grep -rn
      'declares' plugins/.../language.py plugins/.../lexer.py` returns nothing, and
      `uv run pytest -q` is green.

- [ ] T3 -- Rename `desk.declares_scope` to `reports_remit`, and `record.can_declare_scope` with
      it (`desk.py:701`, `:708`; `record.py:129`, `:158`, `:212`; `verdicts.py:95`, `:622-623`,
      `:684`). Verify: `grep -rn 'declares_scope\|can_declare_scope' plugins/` returns nothing.

- [ ] T4 -- Make `declares` internal to the lexer, so the rename is a one-hop change rather than
      a field seventeen consumers can read. Verify: the field does not appear in `census.py`'s
      emitted paragraph JSON, and every consumer keys on the stamped address instead.

- [ ] T5 -- * CHECK BEFORE RENAMING whether any shipped agent file or `references/reviewer-
      brief.md` tells a role to read `declares`. If a role is given the term, this is a
      vocabulary change as well as a field rename and `scripts/check_vocabulary.py` gates it.
      Verify: `grep -rn 'declares' plugins/comment-review/agents/ plugins/comment-review/skills/comment-review/references/`
      and record the answer here; then `uv run python scripts/check_vocabulary.py` exits 0 after
      T1 to T4.

- [x] T6 -- NOT A TASK. MEASUREMENT, moved to the Objective: THIRTEEN spellings on the stem
      across the shipped tree, and the vocabulary defines exactly ONE of them.

- [x] T7 -- NOT A TASK. The SETTLED DEFINITION, moved to the Objective: `references/
      vocabulary.toml` settles `declaration` and that definition is correct and stays.

- [x] T8 -- NOT A TASK. The ARGUMENT that `Paragraph.declares` states the relationship
      backwards, and the PROPOSED name `documents`. Moved to the Objective; the rename is T1.

- [x] T9 -- NOT A TASK. The finding that `scripts/vocabulary_sweep.py` FINDS NONE OF THIS, and
      why -- polysemy is invisible to a word match. Moved to *Why the sweep does not see it*.
      ! It is a finding about the instrument, and belongs to whoever works the sweep.

- [x] T10 -- NOT A TASK. The REDUNDANCY ARGUMENT (`page.py:487` derives the field from the cue;
      `addresser.for_anchor` reads it twice against the module's own stated rule) and the note
      that `declared_at` is already dead. Moved to the Objective; the work is T4.

- [x] T11 -- NOT A TASK. RULING, already made and moved to *Sequencing*: Roy, 2026-08-21,
      *"one-stem-four-jobs can be its own branch after the python branch."*
