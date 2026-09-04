# Back matter has the same problem front matter had, and lands in the closing gap

```
Status:   open
Progress: 1 of 7 tasks closed
Owner:    session
Requires-Roy: false
Raised:   2026-08-20 (Roy, 2026-08-20: 'the problem with head is what happens if there
          is a tail. Many text documents have both')
Ruled:    2026-08-20 — 2026-08-20 -- ONE SERIES FOR THIS LABEL TYPE. Roy: front matter
          and back matter are both `f`; the address says the file's own matter, not
          which end of the file it sits at. ! AND THE GENERAL RULE THAT COMES WITH IT:
          *"we may find another specific type that doesn't match these four's purposes,
          so keep the code generic in how it picks it up even if we don't know the
          shape. That is how we got into the bind of trying to pick up the matter -- we
          kept trying to push it in instead of considering it was its own thing."* Acted
          on: `addresser.SERIES` is now the only list of them, `cue` counts the
          addressers rather than naming them, `--series` offers whatever is in the list,
          and `page.empty_places` RAISES on a series it has no branch for rather than
          dropping the place silently. Five tests guard it. ! What is still open here is
          the RECOGNITION half -- nothing looks for matter at the bottom of a file.
Narrowed: 2026-08-20 — 2026-08-20 -- the NAMING half is done and back matter is no
          longer hypothetical. Roy named the cases: *"like an index or a glossary or
          footnotes"* -- which is the publishing definition of back matter, and lands
          hardest on DOCUMENTATION files. Renamed so nothing encodes an end:
          `mark_front_matter` -> `mark_matter`, `FRONT_MATTER` -> `MATTER`, the
          annotation value `front-matter` -> `matter`, `Cues.front_matter()` ->
          `Cues.matter()`, and the CLI flag `--include-front-matter` -> `--include-
          matter`. ! What remains is the RECOGNITION half only: `mark_matter` still asks
          one positional question about the TOP of the file. ! It meets `a-prose-file-
          has-no-blocks`, since an index or a glossary is a documentation-file shape.
Ruled:    2026-08-20 — 2026-08-20 -- the f series is NOT a singleton. Roy: 'fk is not
          the comments below the code (which should be non- but we left it available).
          fk is the matter at the end of the page, whatever that looks like.' So f0 is
          the head and a later f is the TAIL matter -- an index, a glossary, footnotes.
          A comment run sitting below the last line of code is a b, and stays one; what
          f claims at the end of the file is matter that belongs to the FILE. Today f
          emits once, at the module, so the tail place does not exist yet and this TODO
          is what builds it.
Ruled:    2026-08-21 — the matter rule is POSITIONAL -- the comment run at the top (and
          at the foot) of a file, terminated by a blank line or a docstring. No module
          docstring need exist, so it resolves in every language.
```

## Objective

Back matter has the same problem front matter had, and lands in the closing gap.

## Tasks

- [ ] T1 | !! THE ARGUMENT THAT MOVED FRONT MATTER APPLIES UNCHANGED. A licence
      at the BOTTOM of a file, a vim modeline, a colophon -- each belongs to the
      FILE and not to the gap in the code above it. Today it lands in the
      closing `b`, which is a gap between code and the end of the file, exactly
      as front matter used to land in `b0`.
- [ ] T2 | The `f` series is already built to take it. Roy, 2026-08-20: *"maybe
      it will show up in more places for copyright or other pieces in the docs
      files."* `FRONT` counts like any other series, so a second emission is
      `f1` and nothing else changes -- and the empty kind was named
      `dark-matter` rather than `head` FOR this: Roy, *"what happens if there is
      a tail? Many text documents have both."*
- [ ] T3 | What is missing is the RECOGNITION half: `mark_front_matter` asks a
      positional question about the top of the file. There is no equivalent for
      the bottom, and the signals are the same bespoke-rule problem Roy named
      for front matter without a docstring.
- [x] T4 | FINISHED | unknown | * RULING WANTED: whether back matter is the SAME
      series as front matter -- one `f` series holding the file's own matter
      wherever it sits -- or its own. One series keeps the rule 'each series
      owns its lines exactly' with no addition; two make the address say which
      end.
- [ ] T5 | !! RULED 2026-08-21, AND IT IS POSITIONAL RATHER THAN PER-LANGUAGE.
      Roy: *"Any normal comment section at the top of the file becomes f0 until
      there is either a docstring or a blank line."* And, asked whether back
      matter differs: *"same answer for the back matter because of the same
      reason"* -- so the run at the FOOT of the file, read upward, terminated by
      a blank line or a docstring, is the back matter. ! No module docstring
      need EXIST for either, which is what made the old rule Python-only.
- [ ] T6 | !! THERE IS NO PLACE FOR BACK MATTER TO BE WRITTEN INTO YET. MEASURED
      2026-08-21: `cue` emits `f` exactly ONCE, at the MODULE trigger
      (`out._front = f.emit(MODULE)`), so a file ending in a licence gives `f
      places emitted: ['f0']` and the licence lands in `b2`, the closing gap.
      The `f` series needs a second emission at the EOF trigger -- which exists
      and which `b` already uses, ruled 2026-08-21 for this reason: *"f will
      almost certainly get it and so we might as well pick up both now."*
- [ ] T7 | THE COMPOSITOR THEN WRITES IT POSITIONALLY. Roy: *"back-matter gets a
      write if it is not None at the end of the file. front-matter gets a write
      at the front of the file if it is not None."* ! VERIFIED 2026-08-21 that
      this needs no step over the shebang: the shebang is INSIDE `f0` --
      `raw=['#!/usr/bin/env bash', '# Copyright 2001.']` with `ann=['matter']`
      -- in shell, Python and Ruby alike, because that route is a regex on line
      1 rather than a language rule. Roy: *"the shebang is front-matter"*,
      *"always"*.
