# Three different things are called `declares`, in a repo built on one name per thing

```
Status:   open
Progress: 0 of 11 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (Roy, 2026-08-21, reading a census entry: 'in a system that is a
          lot of having one-name for a thing, 3 things called declares seems like a code
          smell')
```

## Objective

**Thirteen spellings on one stem, and the vocabulary defines one of them.** Roy, 2026-08-21,
reading a census entry that said `comment ... declares=-1`: *"in a system that is a lot of having
one-name for a thing, 3 things called declares seems like a code smell."*

`references/vocabulary.toml` settles **`declaration`** — *"Something that can carry DOCUMENTATION
-- a module, class, function, method, struct -- and so what an `a` place is about."* That is
correct and stays. Three relatives borrowed the stem for other jobs:

| now | what it holds | proposed |
| --- | --- | --- |
| `Paragraph.declares` | the ordinal of the declaration a run **documents** | `documents` |
| `Language.declares` | a tuple of **keywords** that introduce one | `introduces` |
| `desk.declares_scope` | a `query` **announcing** the paragraph is not this role's | `reports_remit` |

!! **`Paragraph.declares` STATES THE RELATIONSHIP BACKWARDS**, and it is the one that misleads
rather than merely crowds. A docstring declares nothing; `def f():` is the declaration and the
prose documents it. ! `Cues.documents(ordinal)` already answers that exact question in the
right word — so one module asks in one vocabulary and another answers in a second.

! **`declares_scope` is the same class of error as `acquittal` and `jurisdiction`**: a word from
outside publishing, checked for collisions and never for register. `remit` is what replaced
`jurisdiction` for this reason, and it is the word this predicate wants.

## Why the sweep does not see it

!! **`scripts/vocabulary_sweep.py` emits ZERO rows matching `declar`.** It lists terms of art the
inventory does not hold, and `declaration` IS in the inventory — so every relative of the stem
passes. **The defect is not an unlisted word; it is a listed word doing three jobs**, and a word
match cannot express that.

## The rename shrinks if the field stops being external first

Roy, the same day: *"Do we need the declares as an external field? I think that may be an internal
implementation detail to the lexer."*

MEASURED: `census.py` writes `vars(b)`, so all 17 paragraph fields reach the agents. But the field
is needed for ONE hop — the lexer states it, `page.attach` reads it to pick which `a`. After the
address is stamped, `@a5` carries the same fact and is what every other consumer already keys on.

! **The tree shows the redundancy three ways.** `page.py` sets `declares=int(cue[1:])` on
synthetic empty places, deriving the field from the cue it duplicates. `addresser.for_anchor`
reads it twice where `series_of(address)` is the module's own stated rule three lines below:
*"an `a` declares, a `c` has a column, a `b` has neither. No second field, no inference from
kind."* The `a` branch is the one that uses a second field.

## Not in scope

`declaration`, `declarations`, `declaring` and `declared` as ordinary grammar of the settled term.
`declared_at` needs nothing — it is already dead, surviving only in comments recording that it
became `anchor_line`.

## Tasks

- [ ] !! MEASURED 2026-08-21: THIRTEEN spellings on the stem across the shipped
      tree -- `declaration` 98, `declares` 41, `declarations` 16, `declared` 13,
      `declaring` 11, `_declared` 8, `declare` 8, `declares_scope` 5,
      `can_declare_scope` 4, `document_declarations` 4, `_declares_here` 2,
      `Declaring` 1, `declared_at` 1. The vocabulary defines exactly ONE of them.
- [ ] `references/vocabulary.toml` settles `declaration` as *"Something that can
      carry DOCUMENTATION -- a module, class, function, method, struct -- and so
      what an `a` place is about."* That definition is correct and STAYS.
      Everything below is a relative that borrowed the stem for a different job.
- [ ] !! `Paragraph.declares` STATES THE RELATIONSHIP BACKWARDS, and it is the one
      that actually misleads. It holds the ORDINAL of the declaration a run
      DOCUMENTS -- a docstring declares nothing; `def f():` is the declaration. !
      `Cues.documents(ordinal)` already answers the same question in the
      right word, three modules away: one asks and one answers, in two
      vocabularies. * PROPOSED: `documents`.
- [ ] ! `Language.declares` IS A TUPLE OF KEYWORDS, not of declarations -- the
      words a language uses to INTRODUCE something documentable. * PROPOSED:
      `introduces`.
- [ ] ! `desk.declares_scope` USES A DIFFERENT VERB ENTIRELY -- to ANNOUNCE. It
      reports a `query` saying the paragraph is not this role's to read, and
      `remit` is the settled term for that; it is what replaced `jurisdiction` for
      exactly this register reason. !! SAME CLASS AS `acquittal` AND
      `jurisdiction`: a word from outside publishing, checked for collisions and
      never for register. CLAUDE.md's rule is to check the register BEFORE
      proposing. * PROPOSED: `reports_remit`, and `can_declare_scope` with it.
- [ ] !! `scripts/vocabulary_sweep.py` FINDS NONE OF THIS, and that is a finding
      about the instrument. It lists terms of art the inventory does not hold;
      `declaration` IS in the inventory, so every relative of the stem passes.
      MEASURED: the sweep emits ZERO rows matching `declar`. ! POLYSEMY IS
      INVISIBLE TO A WORD MATCH -- the defect is not an unlisted word, it is a
      listed word doing three jobs.
- [ ] THE RENAME IS SMALLER IF `declares` STOPS BEING EXTERNAL FIRST. Roy, the
      same day: *"Do we need the declares as an external field? I think that may
      be an internal implementation detail to the lexer."* MEASURED: `census.py`
      writes `vars(b)`, so all 17 paragraph fields ship -- but the field is needed
      for ONE hop, the lexer stating it and `page.attach` reading it to pick which
      `a`. After the address is stamped, `@a5` carries the same fact and is what
      everything else already keys on.
- [ ] ! THE TREE ALREADY SHOWS THE REDUNDANCY THREE WAYS. `page.py` sets
      `declares=int(cue[1:])` on synthetic empty places -- deriving the field
      FROM the cue it duplicates. `addresser.for_anchor` reads it twice where
      `series_of(address)` is the module's own stated rule three lines below: *"an
      `a` declares, a `c` has a column, a `b` has neither. No second field, no
      inference from kind."* The `a` branch is the one that uses a second field.
- [ ] ! `declared_at` IS ALREADY DEAD and needs nothing -- it survives only in
      comments recording that it became `anchor_line`.
- [ ] * CHECK BEFORE RENAMING: whether any shipped agent file or `reviewer-
      brief.md` tells a role to read `declares`. If a role is given the term, this
      is a vocabulary change as well as a field rename, and
      `scripts/check_vocabulary.py` gates it.
- [ ] * SEQUENCED AFTER THE PYTHON BRANCH, ruled by Roy 2026-08-21: *"one-stem-
      four-jobs can be its own branch after the python branch."* ! The order is
      not arbitrary -- `Paragraph.declares` is the field the python work either
      keeps or replaces, so renaming it first would rename something that may not
      survive.
