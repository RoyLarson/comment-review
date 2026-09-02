# Three different things are called `declares`, in a repo built on one name per thing

```
Status:   deferred
Progress: 6 of 15 tasks closed
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
SPLIT:    2026-08-23 -- one action per box. The five tasks the triage left became eight:
          each rename is its own box, and the pre-rename check split from the gate it ends
          with. The citations moved to *The sites* below so no box carries a line of them.
SPLIT:    2026-08-24 -- second pass, fourteen boxes to fifteen. The `Language.declares`
          rename verified against TWO artifacts, a grep and the suite; the suite guard is
          the same guard for every rename in the file, so it is one box of its own.
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

## The sites

Kept here so no box carries a line of citations.

| what | where |
| --- | --- |
| `Paragraph.declares` | `lexer.py:134`, set at `:1617` and `:1899`, read at `page.py:316-318` |
| `Language.declares` | `language.py:61`, `:89`, and every row that populates it |
| `lexer._declares_here` | `lexer.py:1503` -- the private reader named after that field |
| `desk.declares_scope` | `desk.py:701`, `:708` |
| `record.can_declare_scope` | `record.py:129`, `:158`, `:212`; `verdicts.py:95`, `:622-623`, `:684` |

## Why the sweep does not see it

!! **`scripts/vocabulary_sweep.py` emits ZERO rows matching `declar`.** It lists terms of art the
inventory does not hold, and `declaration` IS in the inventory -- so every relative of the stem
passes. **The defect is not an unlisted word; it is a listed word doing three jobs**, and a word
match cannot express that. ! POLYSEMY IS INVISIBLE TO A WORD MATCH, which is a finding about the
instrument and not about this rename -- so it belongs to whoever works the sweep, not here.

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

## Whether this is a vocabulary change as well as a rename

The files to check are the five under `plugins/comment-review/agents/` and
`references/reviewer-brief.md`. **If a role is given the term `declares`, the renames are a
VOCABULARY change** and `scripts/check_vocabulary.py` is the gate that says so; if no role holds
it, the renames are internal and the gate is only a regression guard. ! `references/` and
`docs/vocabulary.md` belong to no lane, so `backend` updates both sides in the same change.

## Sequencing

* **RULED by Roy, 2026-08-21: *"one-stem-four-jobs can be its own branch after the python
branch."*** ! The order is not arbitrary -- `Paragraph.declares` is the field the python work
either keeps or replaces, so renaming it first would rename something that may not survive. That
ruling is why this file is `deferred` and what it waits on:
[`python-cannot-read-python`](python-cannot-read-python.md).

## Tasks

- [ ] T1 | T1 -- Rename `Paragraph.declares` to `documents` at the sites above.
      Verify: `grep -rn declares plugins/` shows no paragraph-field use; the
      round trip holds.
- [ ] T2 | T2 -- Rename `Language.declares` to `introduces`, on the field and on
      every row. Verify: `grep -n declares` over `language.py` returns nothing.
- [ ] T3 | T3 -- Rename `lexer._declares_here` to match `introduces`. Verify:
      `grep -n declares` over `lexer.py` returns no use of the language keyword
      tuple.
- [ ] T4 | T4 -- Rename `desk.declares_scope` to `reports_remit`. Verify: `grep
      -rn declares_scope plugins/` returns nothing.
- [ ] T5 | T5 -- Rename `record.can_declare_scope` to match, at its
      `verdicts.py` call sites too. Verify: `grep -rn can_declare_scope
      plugins/` returns nothing.
- [ ] T6 | T6 -- Make `declares` internal to the lexer. Verify: it is absent
      from the paragraph JSON `census.py` emits.
- [ ] T7 | T7 -- * Check whether any shipped agent file or reference gives a
      role the term `declares`. Verify: the grep over `agents/` and
      `references/` is recorded here.
- [ ] T8 | T8 -- Keep the vocabulary gate green across the renames in T1 to T6.
      Verify: `uv run python scripts/check_vocabulary.py` exits 0.
- [ ] T9 | T9 -- Keep the suite green across the renames in T1 to T6. Verify:
      `uv run pytest -q` exits 0 after the last of them lands.
- [x] T10 | FINISHED | unknown | T10 -- NOT A TASK. MEASUREMENT, in the
      Objective: THIRTEEN spellings on the stem across the shipped tree, and the
      vocabulary defines exactly ONE of them.
- [x] T11 | FINISHED | unknown | T11 -- NOT A TASK. The SETTLED DEFINITION is in
      the Objective: `references/vocabulary.toml` settles `declaration`, and
      that definition stays.
- [x] T12 | FINISHED | unknown | T12 -- NOT A TASK. The ARGUMENT that
      `Paragraph.declares` states the relationship backwards, and the PROPOSED
      name `documents`. In the Objective; the rename is T1.
- [x] T13 | FINISHED | unknown | T13 -- NOT A TASK. The finding that
      `scripts/vocabulary_sweep.py` finds none of this, and why, is in *Why the
      sweep does not see it*.
- [x] T14 | FINISHED | unknown | T14 -- NOT A TASK. The REDUNDANCY ARGUMENT and
      the note that `declared_at` is already dead. In *The rename shrinks...*
      and *Not in scope*; the work is T6.
- [x] T15 | FINISHED | unknown | T15 -- NOT A TASK. RULING, already made and in
      *Sequencing*: Roy, 2026-08-21, *"one-stem-four-jobs can be its own branch
      after the python branch."*
