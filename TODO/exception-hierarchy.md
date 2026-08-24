# The exception tuples are a surface, not a hierarchy

```
Status:   open
Progress: 2 of 5 tasks done
Owner:    backend
Requires-Roy: false
Raised:   2026-08-22 (Roy, 2026-08-22, on the exceptions.py layer: a human would have
          created the hierarchy rather than moving the tuples)
TRIAGED:  2026-08-23 — 2026-08-23. Tasks 2 and 3 are REASONING -- the cost of the
          boundary, and why deferring is safe because exceptions.py's named tuples are
          the SEAM. Neither can be finished; both are ticked and moved to the Objective.
          What is left is task 1 (design and land the hierarchy), task 4 (audit the
          unexamined bare `raise ValueError`, waiting on task 1) and task 5, which names
          a choice the dev scripts have not made. ! Two counts were re-measured today
          and one of them had drifted -- see task 5.
```

## Objective

The exception tuples are a surface, not a hierarchy. `exceptions.py` holds one class,
`Refused(ValueError)`, and five tuples of stdlib classes -- `READ_ERRORS`, `TOML_ERRORS`,
`TOKENIZE_ERRORS`, `PARSE_ERRORS`, `GIT_ERRORS`. A caller catches a list of stdlib classes that
happen to co-occur, not one of our concepts.

## Why this is a TODO and not a patch

**THE COST IS THE BOUNDARY.** Python raises `OSError`, not `Unreadable`, so every read, parse and
git site has to catch the stdlib tuple and re-raise as ours with `from e` -- roughly 30 sites
across 14 modules. It changes what escapes `page_for`, `identity`, `code_names` and the census,
and it makes the tuples INTERNAL to the wrappers rather than the public surface they are today.

**AND DEFERRING IS SAFE, which is the whole reason this can wait:** the named tuples in
`exceptions.py` are the SEAM. Roy: *"we have the surface, we understand the problem. The
constants in that file will allow us to get past this without too much risk of this being
unrefactorable later."* Every call site now names a QUESTION -- read, decode, tokenize, parse,
git -- instead of spelling a tuple, so swapping what that name resolves to is contained. The
version that WOULD have been unrefactorable is the one from before 2026-08-22, with nine
definitions of `READ_ERRORS` in nine files and two of them a different tuple.

## Criterion, 2026-08-22

THE TEST IS NOT WHETHER IT CAN BE REFACTORED. Roy: *"I know technically all code can eventually
be refactored, but sometimes that is a serious mess that becomes not worth it."* Everything is
possible in principle; what decays is whether anyone will pay for it. Nine definitions of one
name across nine files, two of them subtly different, is the state where the cost keeps rising
until the answer is permanently no -- not because it is impossible, but because no version of the
work is ever worth its price. The named surface holds that cost flat, which is what makes waiting
a decision rather than a drift.

AND THE DEFERRAL ALWAYS LOOKS CHEAP, WHICH IS HOW IT GETS DEFERRED. Roy: *"the amortization of
the now cost versus the over always seems small."* Spread the fix across every future encounter
and the per-encounter share is below the threshold that would make anyone act -- so the
comparison comes out in favour of waiting EVERY time it is made, and the decision is never
actually taken. ! That is exactly how nine definitions of `READ_ERRORS` arrived: adding the TENTH
costs nothing visible, and the bill only lands when two of them disagree. ! So a filed TODO is
not free, and this one is filed on a specific ground rather than by default. Where there is no
seam, the same reasoning argues for paying NOW.

## Tasks

- [ ] T1 -- DESIGN AND LAND THE HIERARCHY. Roy, 2026-08-22: *"a human would not have just moved
      the tuples, they would have properly created the exception hierarchy and used that to catch
      the expected exceptions."* The shape: a `CommentReviewError(Exception)` root over `Refused`
      (we declined this page), `Unreadable` (the bytes could not be got), `Undecodable` (the bytes
      came, the TOML would not decode), `Unparsable` (the source came, it would not parse) and
      `GitSilent` (git could not answer). Verify: `grep -rn "exceptions.READ_ERRORS\|
      exceptions.PARSE_ERRORS\|exceptions.GIT_ERRORS\|exceptions.TOML_ERRORS\|
      exceptions.TOKENIZE_ERRORS" plugins/` comes back empty, every `except` names one of our
      classes, and `uv run pytest -q` passes.

- [x] T2 -- Reasoning, moved to the Objective: the cost is the boundary -- roughly 30 sites across
      14 modules must catch the stdlib tuple and re-raise with `from e`.

- [x] T3 -- Reasoning, moved to the Objective: deferring is safe because the named tuples are the
      seam, and every call site already names a QUESTION rather than spelling a tuple.

- [ ] T4 -- AUDIT THE `raise` SIDE ONCE T1 LANDS. RE-MEASURED 2026-08-23: **22** bare
      `raise ValueError` across `plugins/` and `scripts/` -- the same 22 the 2026-08-22
      measurement left unexamined after three deliberate refusals became `exceptions.Refused`.
      `ValueError` is a member of `PARSE_ERRORS` (`exceptions.py:82`), because `ast.parse` raises
      it on a NUL byte, so each of the 22 is either something the hierarchy should name or a
      genuinely bad argument that should stay a `ValueError`. Verify: every remaining bare
      `raise ValueError` sits beside a comment saying it is a bad argument and not a refusal.
      ! Waits on T1; there is nothing to re-classify to until the classes exist.

- [ ] T5 -- SETTLE THE DEVELOPMENT SCRIPTS, which are currently neither joined nor declared
      separate. MEASURED 2026-08-23: **five** files under `scripts/` define their own
      `READ_ERRORS` -- `check_shipped_syntax.py:39`, `check_vocabulary.py:200`,
      `render_brief.py:48`, `render_page.py:65`, `vocabulary_sweep.py:89` -- and **one** of them
      is the TOML variant, not two as previously recorded (`check_vocabulary.py:200` adds
      `tomllib.TOMLDecodeError`). They cannot import the shipped leaf without coupling the dev
      tree to `plugins/`, which ships alone -- so either they take it through the path shim two
      of them already use (`render_brief.py:39`, `render_page.py:60`), or the duplication is
      stated as deliberate in each file. Verify: either `grep -rn "^READ_ERRORS" scripts/` is
      empty, or each of the five carries a comment saying why it holds its own.
