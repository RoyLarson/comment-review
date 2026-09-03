# A move is a composite mark and the code cannot express one

```
Status:   open
Progress: 0 of 21 tasks closed
Owner:    backend
Requires-Roy: true
Raised:   2026-08-30 (2026-08-30, Roy ruling that a move is a composite mark rather than
          a singular one, after a review measured both of its ends corrupted)
Updated:  2026-08-30 — Task 9 was the only question owed and Roy answered it 2026-08-30:
          no seeded destination, separate semantics, a move gets its own spot in the
          edit copies. Task 9 is now an implement box.
```

## Objective

A move is a composite mark and the code cannot express one.

!! **RULED 2026-08-30 -- `decision-log.md Process: #56`.** Roy: *"A move needs to be what
it is and that is a composite Mark - Drop Here Add There. They have to go together and the
ought to have a similar facade but the underneath I don't know how we make it work
correctly without admitting that it is a composite instead of a singular mark. Nothing else
acts on two places at once"*

!! **THE FACT THAT FORCES IT: A SENTENCE MOVES WITHOUT THE PARAGRAPH MOVING.** Roy, the
same day, correcting a reading that an address names one paragraph so a move empties its
origin: *"No a sentance can move without the paragraph moving"*. **The origin keeps a
REMAINDER.** Both ends hold new text and both must be written.

!! **AND `drop` DECLARES A SENTENCE LEFT, NOT A PARAGRAPH -- WHICH IS WHAT MAKES IT
CHECKABLE.** Roy: *"And for drop - remember it is just declaring that a sentance disappeared
not the whole paragraph - it is checkable that the difference is missing and not an
addition..."* So the origin half is verifiable as a PURE DELETION against its seeded
`raw_text`, the destination half as a pure addition, and the PAIR carries the stronger
check -- **the text deleted at the origin must equal the text added at the destination.** A
move that loses a sentence in transit, or invents one on arrival, fails it.

## What is measured, and it is worse than a write bug

!! **THE CODE CANNOT EXPRESS A CORRECT MOVE AT ALL.** `desk/mark.py` `_change_problems`
refuses any `change` that is not a `str`, for every instruction, while `docs/the-mark.md`'s
claim table says a `move`'s `change` carries the same two key names as its claim, holding
the two resulting PARAGRAPHS. **The specified shape is refused at the boundary; the single
string that IS accepted is wrong by construction.**

Measured 2026-08-30 by running it, not by reading it:

| what was run | what came back |
| --- | --- |
| a spec-following move, `change` a dict of the two paragraphs | refused -- *needs `change` ... in RAW TEXT, not a dict* |
| the accepted single-string form, to the docket | origin `text=None` (deleted WHOLE, remainder lost) and the destination written the ENTIRE composite |
| two independent same-file moves, through `flows.collate` | 4 entries for 2 moves |
| a cross-file move `a.py@b1 -> b.py@b1` | an entry in `b.py`'s sheet whose address reads `a.py@b1` |

! **`change_all` WAS THE CLASSIFIER THAT CARRIED THE DICT-SHAPE CHECK**, and it was removed
on 2026-08-29 with the raw-text ruling. That ruling was aimed at LINE ARRAYS -- *"raw text
not lines or sentences"* -- and took the dict form with it, unremarked, because `move` is
the only instruction that used one.

! **NOTHING IN THE SUITE DISAGREES, BECAUSE THE FIXTURE BUILDS THE ACCEPTED FORM.**
`tests/helpers.py`'s `a_move` gives its claim the correct `from`/`to` places and its
`change` a plain string, so every move test confirms the shape the boundary happens to
admit.

## Why the composite is the SMALLER change

Two bound marks each carry a plain `str` change, so `_change_problems` stays ONE rule for
all seven instructions and no downstream stage learns that one instruction's `change` is
not text. Restoring a dict branch teaches every stage a second shape and leaves atomicity a
property prose asserts rather than one the structure holds.

! **THE FACADE IS `entries()`, NOT `address`.** That is the crux of the measured bug: a
`.address` cannot answer for a two-place mark, so every consumer that asked got the origin.
A composite yielding two entries makes the chief's copy correct by construction, and
`desk/collator.py` `_sentence_key`'s `id(mark)` fallback stops being needed.

## What already stands on this, provisionally

! `ac8cbbd` fixed the double-write by deduplicating on `id(mark)` and marked it PROVISIONAL
in the code, per `conventions.md`: *"Where a design deliberately reaches into territory that
will later belong somewhere else, mark it provisional in the code AND in the records."* The
rewritten-address alternative was not a real option -- such an entry does not parse. The
same commit marked `_join_moves`'s kind-promotion provisional for the same reason. **Task 8
deletes both.**

! **`Process: #49`'s indivisibility rule STANDS** -- the two halves still travel together,
and now there is one object that cannot be half-held.

## Tasks

- [ ] T1 | Implement a move as a COMPOSITE of two ordinary marks -- a `drop` at
      the origin carrying the remainder, an `add` at the destination carrying
      the arrival text -- each with a plain `str` `change`. Verify: a
      spec-following move parses; a test asserts each half is an ordinary Mark
      that `_change_problems` accepts with no second shape added to it.
- [ ] T2 | Implement the facade so a consumer iterating entries needs no move-
      awareness. Verify: `flows.collate._chief_copy` writes TWO entries for one
      move, at two distinct addresses, and a test asserts the destination
      entry's address is the DESTINATION -- it reads the origin today, measured.
- [ ] T3 | Implement the pure-deletion check on the origin half: the diff from
      the seeded `raw_text` to `change` carries no insertion. Verify: a move
      whose origin text gains a word is refused BY NAME, and the test goes red
      when the check is replaced with a no-op.
- [ ] T4 | Implement the pure-addition check on the destination half. Verify: a
      move whose destination text loses a word is refused by name, and the test
      goes red when the check is replaced with a no-op.
- [ ] T5 | Implement the pair check: the text deleted at the origin EQUALS the
      text added at the destination. Verify: a move that drops one sentence and
      adds a different one is refused by name; a move that carries the same
      sentence across passes.
- [ ] T6 | Update `docs/the-mark.md` to the composite shape, superseding the
      sentence reading that `change` carries both paragraphs as raw text in one
      field. Verify: `tests/gates/test_mark_shape.py` reads the amended headings
      and passes without a hand-edited count.
- [ ] T7 | Update `tests/helpers.py` so `a_move` builds the composite. Verify:
      no helper builds a move whose `change` is a single string, and every move
      test that changes is corrected rather than deleted.
- [ ] T8 | Delete the provisional single-mark move handling in
      `flows/collate.py` and the kind-promotion in `desk/collator.py`
      `_join_moves` once the composite makes them unreachable. Verify: both are
      gone and the suite stays green.
- [ ] T9 | Implement a MOVE REGION in the edit copy's shape, distinct from the
      one-slot-per-place marks, and declare it in `desk/containers.py`. RULED
      2026-08-30 -- the destination is NOT seeded; a move gets its own spot.
      Verify: `parse_edit_copy` accepts a copy carrying a move in that region
      and refuses a move written into a per-place slot; a test asserts an edit
      copy whose only ruling is a move round-trips.
- [ ] T10 | Implement a refusal in `flows.collate._composition` for any owing
      set holding a `move`, so a relocation is never rewritten as a `correct`.
      Verify: two roles returning the same `move m.py@b1 -> m.py@b5` with
      `change == base` leave the move in `resolved` and reach `_move_order`;
      today both ends compose to no-op `correct`s and `order`, `rereads` and
      `problems` all come back empty.
- [ ] T11 | Implement a both-ends-or-neither rule in `flows.collate._resolve`,
      so a `move` that resolves at its origin and refuses at its destination is
      carried forward whole rather than half-applied. Verify: a move whose two
      ends have different-length bases -- five lines at `m.py@b1`, one at
      `m.py@b5` -- leaves neither end in `resolved`; today the origin reaches
      the chief's copy as a `correct` while the destination goes to `rereads`.
- [ ] T12 | Update the `_pair_moves` note at `flows/collate.py:230-241`, which
      names `desk.collator._join_moves` as the guard that makes the withdrawal
      branch unreachable. Verify: the note states that `_join_moves` equalises
      the OUTCOME while `_resolve` resolves each end independently against a
      per-end base, and no sentence in the file claims equal outcomes imply
      equal resolutions.
- [ ] T13 | Implement a fix for `desk.collator._join_moves` unioning `marks`
      across two ends whose base paragraphs differ, so no entry carries a mark
      whose `change` belongs to another address. Verify: `alpha` moving `a.py@b1
      -> a.py@b3` and `bravo` moving `a.py@b2 -> a.py@b3` do not produce two
      fabricated `correct`s swapping the paragraphs at b1 and b2 with
      `problems`, `drift` and `escalations` all empty; today they do.
- [ ] T14 | Update `desk.collator._join_moves` so both ends of one joined pair
      receive the same `roles` and `marks` order. Verify: the two ends of one
      move report identical lists; today `a0` gets `['block-context',
      'module-context']` while `a8` and `a16` get the reverse, and
      `_composition` reads `owing[0].mark.anchor`.
- [?] T15 | Decide whether the far end's roles should reach a reader of one end of a
      move through a separate reader-facing field, leaving `marks` as the marks at THIS
      place? `_join_moves:883` skips the union whenever both ends' kinds agree, so a
      move with a collider at each end shows `a.py@b1 roles=['alpha','bravo']` and
      `a.py@b2 roles=['alpha','chi']` -- the loss its own `!!` at 838-842 exists to
      prevent -- while widening the union widens the measured corruption above, an entry
      carrying a mark whose `change` belongs to another address.
- [ ] T16 | Update `desk.collator._join_moves`'s opening illustration at lines
      823-826, which names an end settled while the other escalated -- a state
      no run reaches, because `_sentence_key` returns `id(mark)` for a `move`.
      Verify: the illustration is the settled/reread case its own MEASURED
      example at 834-838 uses, and any unreachable state is marked as such.
- [ ] T17 | Implement the FORM check on a `move`'s destination in
      `_destination_problems`, so a `claim.to` that is not `path@cue` is refused
      by name rather than falling through. Verify: a move whose `to` is the
      prose `out of the code entirely` -- the destination `reviewer-brief.md`
      offers a role -- is refused; today it parses with zero problems and the
      docket carries the origin's delete plus a page naming no file and no
      place.
- [ ] T18 | Delete `claim.from` from the `move` row, or hold it equal to the
      mark's own `address`. Verify: `grep -rn '"from"' src/comment_review/`
      shows the key gone, or a move whose `claim.from` names a place other than
      its `address` is refused by name -- today `parse` returns no problems and
      `_touches` reports `address` and `claim.to` only.
- [ ] T19 | Update `_owed_from` at `tests/gates/test_mark_shape.py:305-307`,
      which normalises the spec's `the COMPOSITE` cell to `True`, so the one
      cell the `Row` type cannot express stops being flattened to a bool.
      Verify: the gate goes red when the spec's `move` change cell is edited,
      and passes on the composite wording task 6 of this file lands.
- [ ] T20 | Implement the both-ends-or-neither check for a move in
      `desk.containers.parse_edit_copy`, which is the only level that sees every
      sheet of one role. Verify: a copy holding a cross-file move's origin half
      with no destination half is refused by name, and one holding both passes
      -- today `parse_edit_copy` looks at no marks at all.
- [ ] T21 | Implement the public classifier and slice accessor in
      `results/differences.py` that tasks 3, 4 and 5 need --
      `delete`/`insert`/`replace`/nothing for one base-side pair, and the text
      each side removed and added -- at a granularity finer than whole lines.
      Verify: a `move` carrying ONE SENTENCE out of a paragraph classifies as a
      deletion at the origin and the removed text is recoverable, where today's
      line opcodes report a single `replace` and the removed text appears in no
      opcode.
