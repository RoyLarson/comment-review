# Eleven defects in `desk/mark.py`, found by running its parse against its own prose

```
Status:   open
Progress: 0 of 11 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-30 (2026-08-30, a code review of `desk/mark.py` that ran `parse`
          against the claims in `docs/the-mark.md` and the module's own docstrings --
          eleven defects in one module, with no per-module TODO to hold them)
```

## Objective

Eleven defects in `desk/mark.py`, found on 2026-08-30 by running its `parse` against
the claims in `docs/the-mark.md` and in the module's own docstrings.

!! **PER-MODULE, NOT A DESIGN OBJECTIVE.** `conventions.md` sanctions one TODO per
module for general fixes, and the together-or-not-at-all test is NOT claimed here --
these eleven are independent. Precedent is [`collator-defects`](collator-defects.md),
opened the same day for the same shape.

! **WHY NOT [`mark-holds-spec-and-parse`](mark-holds-spec-and-parse.md):** that file's
subject is the SPLIT and every one of its boxes is the extraction, so eleven unrelated
defects there would stop its `Progress:` being a claim about whether the split has
happened. ! The tasks below therefore name SYMBOLS wherever the split will move them
-- `allowed()`, `ROLE_FIELDS`, `Mark.seed`, the row flags -- so that file landing
first does not stale them. A line number is quoted only as evidence of what was
measured.

## What was measured

Run:

- `parse` accepts a substantive mark whose `address` carries no `@`: `filled()` asks
  only for a non-blank string, so the bare cue this module's own 62-of-78 measurement
  is about passes, `docket_from` writes a page with an empty path and an empty cue,
  and `places()` collides two files onto one address
- `sources=tuple(sources)` and `claim=dict(claim)` are one level deep, so mutating
  `entry["sources"][0]["verbatim"]` after `parse` is visible through a frozen `Mark`;
  `collator.source_problems` re-reads `mark.sources`, so a caller holding the original
  entry -- which `places()` does -- can make source verification read a string `parse`
  never saw
- a row monkeypatched to `replace(INSTRUCTIONS[ADD], claim_all=(), needs_anchor=True)`
  yields an `add` carrying no anchor at all with `problems: []`. All seven real rows
  satisfy the coupling, and `test_mark_shape.py` compares flag to PHRASE rather than
  to behaviour, so the gate stays green because it shares the defect
- a fourth name in `SEEDED` meets `ValueError: zip() argument 2 is shorter than
  argument 1`, naming neither `Mark` nor `SEEDED`; a renamed one gives the documented
  `AttributeError`
- `allowed()["instruction"]` is alphabetical while `QUERY_SHAPES` holds the spec's
  order; `allowed()`'s `Returns:` names six keys where it returns seven, and
  `commands/distribute.py:56` prints that dict as the `--shape` JSON a role is given;
  `ROLE_FIELDS`' docstring enumerates seven of `Mark`'s eight fields, omitting
  `raw_text` -- the stale count `2f6b84e` fixed at the module docstring and left here

Grepped: `can_declare_scope`, `rules_on_text` and `diffable` have no reader in `src/`
outside this file, and `claim.shape`'s four occurrences are all inside it, so the
comment calling `Shape.UNABLE_TO_DETERMINE` the one a collate step can act on names a
step that does not exist. Same shape as the `owes_destination` case `conventions.md`
cites as its measured example of a field answering neither necessary nor purposeful.

## What was measured

Run:

- `parse` accepts a substantive mark whose `address` carries no `@`: `filled()` asks
  only for a non-blank string, so the bare cue this module's own 62-of-78 measurement
  is about passes, `docket_from` writes a page with an empty path and an empty cue,
  and `places()` collides two files onto one address
- `sources=tuple(sources)` and `claim=dict(claim)` are one level deep, so mutating
  `entry["sources"][0]["verbatim"]` after `parse` is visible through a frozen `Mark`;
  `collator.source_problems` re-reads `mark.sources`, so a caller holding the original
  entry -- which `places()` does -- can make source verification read a string `parse`
  never saw
- a row monkeypatched to `replace(INSTRUCTIONS[ADD], claim_all=(), needs_anchor=True)`
  yields an `add` carrying no anchor at all with `problems: []`. All seven real rows
  satisfy the coupling, and `test_mark_shape.py` compares flag to PHRASE rather than
  to behaviour, so the gate stays green because it shares the defect
- a fourth name in `SEEDED` meets `ValueError: zip() argument 2 is shorter than
  argument 1`, naming neither `Mark` nor `SEEDED`; a renamed one gives the documented
  `AttributeError`
- `allowed()["instruction"]` is alphabetical while `QUERY_SHAPES` holds the spec's
  order; `allowed()`'s `Returns:` names six keys where it returns seven, and
  `commands/distribute.py:56` prints that dict as the `--shape` JSON a role is given;
  `ROLE_FIELDS`' docstring enumerates seven of `Mark`'s eight fields, omitting
  `raw_text` -- the stale count `2f6b84e` fixed at the module docstring and left here

Grepped: `can_declare_scope`, `rules_on_text` and `diffable` have no reader in `src/`
outside this file, and `claim.shape`'s four occurrences are all inside it, so the
comment calling `Shape.UNABLE_TO_DETERMINE` the one a collate step can act on names a
step that does not exist. Same shape as the `owes_destination` case `conventions.md`
cites as its measured example of a field answering neither necessary nor purposeful.

## What was measured

Run:

- `parse` accepts a substantive mark whose `address` carries no `@`: `filled()` asks
  only for a non-blank string, so the bare cue this module's own 62-of-78 measurement
  is about passes, `docket_from` writes a page with an empty path and an empty cue,
  and `places()` collides two files onto one address
- `sources=tuple(sources)` and `claim=dict(claim)` are one level deep, so mutating
  `entry["sources"][0]["verbatim"]` after `parse` is visible through a frozen `Mark`;
  `collator.source_problems` re-reads `mark.sources`, so a caller holding the original
  entry -- which `places()` does -- can make source verification read a string `parse`
  never saw
- a row monkeypatched to `replace(INSTRUCTIONS[ADD], claim_all=(), needs_anchor=True)`
  yields an `add` carrying no anchor at all with `problems: []`. All seven real rows
  satisfy the coupling, and `test_mark_shape.py` compares flag to PHRASE rather than
  to behaviour, so the gate stays green because it shares the defect
- a fourth name in `SEEDED` meets `ValueError: zip() argument 2 is shorter than
  argument 1`, naming neither `Mark` nor `SEEDED`; a renamed one gives the documented
  `AttributeError`
- `allowed()["instruction"]` is alphabetical while `QUERY_SHAPES` holds the spec's
  order, and `allowed()`'s `Returns:` names six keys where the function returns seven
  -- `commands/distribute.py:56` prints that dict as the `--shape` JSON a role is given
- `ROLE_FIELDS`' docstring enumerates seven of `Mark`'s eight fields, omitting
  `raw_text` -- the stale count `2f6b84e` fixed at the module docstring and left here

Grepped: `can_declare_scope`, `rules_on_text` and `diffable` have no reader in `src/`
outside this file, and `claim.shape`'s four occurrences are all inside it, so the
comment calling `Shape.UNABLE_TO_DETERMINE` the one a collate step can act on names a
step that does not exist. Same shape as the `owes_destination` case `conventions.md`
cites as its measured example of a field answering neither necessary nor purposeful.

## Tasks

- [ ] Implement the FORM check on a substantive mark's `address` in
      `desk.mark.parse`, so an address carrying no `@` is refused by name. Verify:
      `parse("w", {"instruction": "correct", "address": "a0", ...})` returns a
      named problem -- today it returns `(mark, [])`, and
      `reading.addresser.cue_of("a0")` answers `Address('', '')`; the test goes
      red when the check is removed.
- [ ] Update the COPIED, NOT ALIASED comment at `desk/mark.py:719-720` and
      `:375-376` to the depth the copy holds, or copy `sources`' entries and
      `claim`'s values deeply. Verify: mutating `entry["sources"][0]["verbatim"]`
      after `parse` cannot change `mark.sources`, or the comment bounds the
      guarantee to the containers and names `as_entry()` as the second route --
      today both mutations are visible through a frozen `Mark`.
- [?] Do `can_declare_scope`, `rules_on_text` and `diffable` stay as row flags,
      and what reads each? MEASURED 2026-08-30: no reader anywhere in `src/`
      outside `desk/mark.py`; the only other sites are
      `tests/gates/test_mark_shape.py:135,137,138`, which map the spec's phrase to
      the field name. Verify: the answer is recorded in `docs/decision-log.md`,
      and each of the three is either read by a module or gone.
- [ ] Update `allowed()` so `scope_shape` is published from the row's
      `can_declare_scope` rather than the hardcoded `Shape.OUTSIDE_MY_ROLE`
      literal at `desk/mark.py:438`, or delete the flag. Verify: editing that
      row's `can_declare_scope` changes what `allowed()` publishes -- today the
      two are independent and the copy that ships to a role is the literal.
- [ ] Implement the contradiction `rules_on_text`'s docstring names -- a `drop`
      against an edit on ONE sentence -- in `desk.collator._outcome`, or delete
      the flag. Verify: two marks on one sentence, one `drop` and one `correct`,
      reach a named outcome; today `_outcome` routes on `Instruction.ADD`, the
      count and `_sentence_key` only, and no module in `src/` detects the pair.
- [ ] Update the comment on `Shape.UNABLE_TO_DETERMINE` at `desk/mark.py:132`,
      which calls it "the one a collate step can ACT on". Verify: no sentence in
      `desk/mark.py` names a collate step that reads `claim.shape`'s value --
      `grep -rn 'claim\.shape\|"shape"' src/comment_review/` returns four lines,
      all inside `desk/mark.py`.
- [ ] Implement the coupling check between a row's flags and its `claim_all`, so
      `needs_anchor`, `owes_destination` and `quotes_original` cannot be set on a
      row whose `claim_all` never names the key they read. Verify: a row built as
      `replace(INSTRUCTIONS[ADD], claim_all=(), needs_anchor=True)` is refused;
      today an `add` carrying no anchor at all parses with `problems: []` under
      it.
- [ ] Update `ROLE_FIELDS`' docstring at `desk/mark.py:380-383`, which enumerates
      seven of `Mark`'s eight fields and omits `raw_text`. Verify: a test
      differences `set(ROLE_FIELDS) | {"address", "anchor", "instruction"}`
      against `dataclasses.fields(Mark)` and asserts it is empty -- today it
      reports `raw_text` unaccounted for.
- [ ] Update `allowed()`'s `Returns:` block at `desk/mark.py:404-409`, which names
      six keys where the function returns seven -- `source_keys` is missing.
      Verify: a test compares `set(allowed())` against the keys the docstring
      names and goes red when either is edited alone.
- [ ] Update `Mark.seed`'s "THIS IS THE WHOLE GUARD" sentence at
      `desk/mark.py:344-348`, since `zip(..., strict=True)` raises first and a
      name ADDED to or REMOVED from `SEEDED` meets a bare `ValueError` naming
      neither `Mark` nor `SEEDED`. Verify: the docstring names both failures, or
      `seed` raises one named error for both.
- [ ] Update `allowed()` at `desk/mark.py:435` so the instruction list is
      published in the order `docs/the-mark.md` states, as `QUERY_SHAPES` already
      is, or state at `sorted(INSTRUCTIONS)` why the two closed sets in one file
      order themselves by opposite rules. Verify: `allowed()["instruction"]` reads
      `clean, query, drop, correct, patch, add, move`, or the file says why it is
      alphabetical.
