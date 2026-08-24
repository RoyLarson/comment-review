# Shipped prose still describes formats and flags this branch deleted

```
Status:   open
Progress: 1 of 4 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-21 (the /code-review xhigh of 2026-08-21, focused on the file-to-
          census route)
Re-checked: 2026-08-23 -- one of the four is fixed: `addresser.py` no longer names
          `--repo` anywhere. The other three are live, and every line number in the
          file had moved.
```

## Objective

**Shipped prose still describes formats and flags this branch deleted.** These are the obituary
class `block-context` is chartered to catch, shipping inside the tool that catches it. Re-taken
2026-08-23; the citations below are today's.

## Tasks

- [ ] T1 -- Take the second record format out of `record.py`'s prose. It describes
      a shape that no longer exists: `:6-11` says a record *"used to travel as
      prose that `verdicts.py` reconstructed a table from by guessing where each
      field ended"*; `:518` returns *"the rendered claim for a text record"*;
      `:573-584` explains *"the marker form the text record carried"* and what
      *"the old format carried"*. ! While there, `:14` says `--seed` writes a slot
      with *"`paragraph` and `address` already in it"*, and `record.SEEDED` is
      `("place", "anchor")` with `:699` reading *"THE ADDRESS AND NOTHING ELSE"* --
      the same paragraph contradicts itself. ! The fifth site, said to be in
      `desk.py`, was NOT found on re-read: its history lines (`:130`, `:207`) are
      about `desk`'s own behaviour, not a second record format. Verify: no shipped
      script describes a record format the code cannot read, and
      `uv run pytest -q` stays green.
- [x] T2 -- FINISHED. `addresser.py`'s module usage line named `--repo`, which
      argparse rejects. RE-MEASURED 2026-08-23: `--repo` has zero occurrences in
      the file, the usage line at `:3` reads
      `python addresser.py --census census.json --anchor "def f():" --series a`,
      and `addresser.py --repo .` now fails on the missing required `--census`.
- [ ] T3 -- Re-take the uniqueness example in `docs/addressing.md:142`. It states
      *"Every ADDRESS is unique -- measured `a0 b1 b2 b3 c1 c2`"* over the
      five-line example directly above it. MEASURED 2026-08-23: `addresser.py:85`
      rules that **every series starts at 0**, and `f0` -- the file's own matter --
      is a fourth series that the cue emits at the module (`:78`, `:176`), so the
      cited spelling cannot be what that example yields. ! `CLAUDE.md` calls this
      file the crux. Verify: the cues in that sentence are the ones a census of the
      example prints, and the command that produced them is named beside it.
- [ ] T4 -- Give the record shape in `reviewer-brief.md:93-107` its envelope. The
      brief shows a bare `{page, records}` while `record.seed()` writes
      `{record_version, reviewer, allowed, pages, code_concerns}`
      (`record.py:873-883`), with the pages under `pages` -- and the brief is a
      reviewer's only spec for the shape this branch changed. Verify: the JSON in
      the brief is the shape `record.py --seed` writes, and `record.py --check`
      accepts a file filled to match it.
