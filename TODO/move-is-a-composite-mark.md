# A move is a composite mark and the code cannot express one

```
Status:   decision-needed
Progress: 0 of 9 tasks done
Owner:    backend
Requires-Roy: true
Raised:   2026-08-30 (2026-08-30, Roy ruling that a move is a composite mark rather than
          a singular one, after a review measured both of its ends corrupted)
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

- [ ] Implement a move as a COMPOSITE of two ordinary marks -- a `drop` at the
      origin carrying the remainder, an `add` at the destination carrying the
      arrival text -- each with a plain `str` `change`. Verify: a spec-following
      move parses; a test asserts each half is an ordinary Mark that
      `_change_problems` accepts with no second shape added to it.
- [ ] Implement the facade so a consumer iterating entries needs no move-
      awareness. Verify: `flows.collate._chief_copy` writes TWO entries for one
      move, at two distinct addresses, and a test asserts the destination entry's
      address is the DESTINATION -- it reads the origin today, measured.
- [ ] Implement the pure-deletion check on the origin half: the diff from the
      seeded `raw_text` to `change` carries no insertion. Verify: a move whose
      origin text gains a word is refused BY NAME, and the test goes red when the
      check is replaced with a no-op.
- [ ] Implement the pure-addition check on the destination half. Verify: a move
      whose destination text loses a word is refused by name, and the test goes
      red when the check is replaced with a no-op.
- [ ] Implement the pair check: the text deleted at the origin EQUALS the text
      added at the destination. Verify: a move that drops one sentence and adds a
      different one is refused by name; a move that carries the same sentence
      across passes.
- [ ] Update `docs/the-mark.md` to the composite shape, superseding the sentence
      reading that `change` carries both paragraphs as raw text in one field.
      Verify: `tests/gates/test_mark_shape.py` reads the amended headings and
      passes without a hand-edited count.
- [ ] Update `tests/helpers.py` so `a_move` builds the composite. Verify: no
      helper builds a move whose `change` is a single string, and every move test
      that changes is corrected rather than deleted.
- [ ] Delete the provisional single-mark move handling in `flows/collate.py` and
      the kind-promotion in `desk/collator.py` `_join_moves` once the composite
      makes them unreachable. Verify: both are gone and the suite stays green.
- [ ] Must a move's DESTINATION place be seeded -- present in the binder with its
      own `raw_text` -- so drift is detectable at both ends? It would make a move
      onto a place no role read a refusal, which is new behaviour.
