# Eleven defects in `desk/mark.py`, found by running its parse against its own prose

```
Status:   open
Progress: 19 of 28 tasks closed
Owner:    backend
Requires-Roy: false
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

- [x] T1 | FINISHED -- Mark.deserialize refuses an address with no path; test | 42987afd | Implement
      the FORM check on a substantive mark's `address` in `desk.mark.parse`, so
      an address carrying no `@` is refused by name. Verify: `parse("w",
      {"instruction": "correct", "address": "a0", ...})` returns a named problem
      -- today it returns `(mark, [])`, and `reading.addresser.cue_of("a0")`
      answers `Address('', '')`; the test goes red when the check is removed.
        > 2026-09-14 self-run 2026-09-14: still passes; fc1 marked it at mark.py b121
- [ ] T2 | Update the COPIED, NOT ALIASED comment at `desk/mark.py:719-720` and
      `:375-376` to the depth the copy holds, or copy `sources`' entries and
      `claim`'s values deeply. Verify: mutating
      `entry["sources"][0]["verbatim"]` after `parse` cannot change
      `mark.sources`, or the comment bounds the guarantee to the containers and
      names `as_entry()` as the second route -- today both mutations are visible
      through a frozen `Mark`.
- [x] T3 | Process 143: delete all three; nothing reads them | 7924d645 | Decide
      whether `can_declare_scope`, `rules_on_text` and `diffable` stay as row
      flags, and what reads each? MEASURED 2026-08-30: no reader anywhere in
      `src/` outside `desk/mark.py`; the only other sites are
      `tests/gates/test_mark_shape.py:135,137,138`, which map the spec's phrase
      to the field name. Verify: the answer is recorded in
      `docs/decision-log.md`, and each of the three is either read by a module
      or gone.
- [-] T4 | SUPERSEDED by T22: Process 143 deletes the flag | 7924d645 | Update
      `allowed()` so `scope_shape` is published from the row's
      `can_declare_scope` rather than the hardcoded `Shape.OUTSIDE_MY_ROLE`
      literal at `desk/mark.py:438`, or delete the flag. Verify: editing that
      row's `can_declare_scope` changes what `allowed()` publishes -- today the
      two are independent and the copy that ships to a role is the literal.
- [-] T5 | SUPERSEDED by T22: Process 143 deletes the flag | 7924d645 | Implement
      the contradiction `rules_on_text`'s docstring names -- a `drop` against an
      edit on ONE sentence -- in `desk.collator._outcome`, or delete the flag.
      Verify: two marks on one sentence, one `drop` and one `correct`, reach a
      named outcome; today `_outcome` routes on `Instruction.ADD`, the count and
      `_sentence_key` only, and no module in `src/` detects the pair.
- [ ] T6 | Update the comment on `Shape.UNABLE_TO_DETERMINE` at
      `desk/mark.py:132`, which calls it "the one a collate step can ACT on".
      Verify: no sentence in `desk/mark.py` names a collate step that reads
      `claim.shape`'s value -- `grep -rn 'claim\.shape\\|"shape"'
      src/comment_review/` returns four lines, all inside `desk/mark.py`.
- [ ] T7 | Implement the coupling check between a row's flags and its
      `claim_all`, so `needs_anchor`, `owes_destination` and `quotes_original`
      cannot be set on a row whose `claim_all` never names the key they read.
      Verify: a row built as `replace(INSTRUCTIONS[ADD], claim_all=(),
      needs_anchor=True)` is refused; today an `add` carrying no anchor at all
      parses with `problems: []` under it.
- [ ] T8 | Update `ROLE_FIELDS`' docstring at `desk/mark.py:380-383`, which
      enumerates seven of `Mark`'s eight fields and omits `raw_text`. Verify: a
      test differences `set(ROLE_FIELDS) \| {"address", "anchor",
      "instruction"}` against `dataclasses.fields(Mark)` and asserts it is empty
      -- today it reports `raw_text` unaccounted for.
- [ ] T9 | Update `allowed()`'s `Returns:` block at `desk/mark.py:404-409`,
      which names six keys where the function returns seven -- `source_keys` is
      missing. Verify: a test compares `set(allowed())` against the keys the
      docstring names and goes red when either is edited alone.
- [ ] T10 | Update `Mark.seed`'s "THIS IS THE WHOLE GUARD" sentence at
      `desk/mark.py:344-348`, since `zip(..., strict=True)` raises first and a
      name ADDED to or REMOVED from `SEEDED` meets a bare `ValueError` naming
      neither `Mark` nor `SEEDED`. Verify: the docstring names both failures, or
      `seed` raises one named error for both.
- [ ] T11 | Update `allowed()` at `desk/mark.py:435` so the instruction list is
      published in the order `docs/the-mark.md` states, as `QUERY_SHAPES`
      already is, or state at `sorted(INSTRUCTIONS)` why the two closed sets in
      one file order themselves by opposite rules. Verify:
      `allowed()["instruction"]` reads `clean, query, drop, correct, patch, add,
      move`, or the file says why it is alphabetical.
- [-] T12 | SUPERSEDED -- the instrument is the page's cues, not the full binder; refiled as T14 | 29e3cd4c | Update
      the mark command to refuse an address the full binder does not carry,
      before it writes. Verify: a cue no page holds is refused
        > 2026-09-07 The command has no binder today; it checks the page half only
        > 2026-09-07 The command has no binder; it checks the page half alone
        > 2026-09-07 The flow does the lookup; the command hands it the binder path
- [-] T13 | SUPERSEDED -- a redacted copy has no slot for a valid absent place; refiled as T15 | 29e3cd4c | Delete
      fill's manufactured seed, which invents raw_text and takes the anchor from
      the role's own entry. Verify: no slot means a refusal
        > 2026-09-07 The base is the binder's, never a returned mark's
- [x] T14 | fill resolves the cue against its page and refuses one the page does not carry | d8821bb4 | Update
      fill to resolve an address against its page's cues via page_of. Verify: a
      place the page does not carry is refused before any write
        > 2026-09-07 The binder on disk is always redacted; a page carries every place
        > 2026-09-07 A page carries both the absent and present places of a series
- [x] T15 | fill seeds an absent place from its page; the anchor is the page's, not the entry's | a5477f37 | Update
      fill to seed an absent place from that page, not from the role's entry.
      Verify: the anchor comes from the page and raw_text is empty
        > 2026-09-07 The base is the system's, never the party being checked
- [-] T16 | superseded by Process 162: moves are provisional, not built now | 9519ead5 | Implement
      a test that a move from f0 to a b place reaches the docket, and make it
      pass, per Addressing 25
- [-] T17 | SUPERSEDED by T20: Process 132 keeps the prose, not a refusal | 393672ef | Update
      fill to refuse an add at a place that already holds prose, which
      SKILL.md:68 defines as missing
        > 2026-09-11 smoke 89956870: add at a0 and c12 replaced the prose, every stage
- [x] T18 | Process 134: the write end checks it; galley T46 does it | 393672ef | Decide
      what a mark's anchor is for, since nothing after fill reads it; the proof
      reads the page's
        > 2026-09-12 Process 131: smoke exits 0 with the seeded anchor emptied
- [-] T19 | SUPERSEDED by T21: the f place is held to Process 132 | 393672ef | Update
      fill so an add at an f place holding prose is refused, as T17 refuses one
      elsewhere
        > 2026-09-12 384dc8cc: an f place gets no slot, so its seed is empty
- [x] T20 | an add on prose keeps every word of it, in order | bee1b7e8 | Update
      fill so an add at a place holding prose is accepted only when its change
      keeps every word of that prose, in order, per Process 132
- [x] T21 | a slot at an f place is seeded with the page's prose | 16dabbab | Update
      fill so an f place holding prose is seeded from the page, so Process 132's
      check applies there
- [x] T22 | The three flags are gone from Row, INSTRUCTIONS, the gate and docs/the-mark.md | 9fabde74 | Delete
      can_declare_scope, rules_on_text and diffable from desk/mark.py's Row and
      INSTRUCTIONS, per Process 143
        > 2026-09-13 tests/gates/test_mark_shape.py:135-138 maps the spec's phrases
        > 2026-09-13 check docs/the-mark.md names none of the three after
- [x] T23 | FINISHED -- mark reads --flag=@path from the file; two tests | f71b6ad6 | Update
      the mark command so --flag=@path reads the file as @path does, and no
      literal path lands in a claim or change
        > 2026-09-14 self-run: mc1 saved 8 marks with a scratch path as their text
        > 2026-09-14 check passed those 8; bc1 had 80 rulings refused the same way
        > 2026-09-14 evidence: OneDrive/comment-review-feedback/2026-09-14-self-run
- [x] T24 | FINISHED -- mark --withdraw takes back a placed ruling; six tests | 1a4d7cfc | Implement
      a way for a role to withdraw or replace a mark it placed, after which the
      copy holds only the new mark
        > 2026-09-14 SKILL.md's exit-1 send-back cannot be carried out without it
        > 2026-09-14 self-run: mc1 edited its copy's JSON by hand to repair 8 marks
        > 2026-09-14 evidence: OneDrive/comment-review-feedback/2026-09-14-self-run
- [x] T25 | FINISHED -- a drop's joined line is rewrapped to the paragraph's widest; test | e4d69ded | Update
      derived_change so a drop inside a line leaves no line longer than the
      paragraph's longest line before the drop
        > 2026-09-14 self-run: 11 changes past 88 columns, bc2 4 and fc2 7
        > 2026-09-14 evidence: OneDrive/comment-review-feedback/2026-09-14-self-run
- [x] T26 | mark --raw-text: an add carries its snippet in change and the paragraph as it will read in raw_text; tests/test_fill.py, test_mark_command.py | e538ea92 | Implement
      an add whose change is the snippet and whose raw_text is the paragraph as
      it will read, per Process 176
        > 2026-09-14 Roy: the location and the snippet and the destination raw text
- [ ] T27 | Implement a role correct or patch at a place composing with its own
      move there, applied at the destination; verify mark accepts both
        > 2026-09-27 mark refuses: its marks do not compose -- withdraw one
- [ ] T28 | Fix mark refusing a role add into a paragraph it also corrects; they
      rule on different sentences and should compose
        > 2026-09-27 repro: correct then add same place; do not compose
