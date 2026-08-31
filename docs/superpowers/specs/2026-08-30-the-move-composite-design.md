# The move composite, and the claim that stops repeating the diff

**Status:** design, 2026-08-30. Rulings: `decision-log.md Process: #56`, `#57`, `#60`, `#62`.

**Problem.** A `move` cannot be expressed correctly today, and two CRITICALs from the
eight-file review of 2026-08-30 sit on that. The repair is not move-specific: it comes from
settling what a mark carries at all.

---

## 1. What a mark carries -- the model this rests on

Ruled 2026-08-30 while designing this.

| | |
| --- | --- |
| **the binder** | holds the ORIGINAL text at each address, and is the only copy of it |
| **`mark.raw_text`** | seeded with the original, returned **EDITED** |
| **`change`** | **DELETED** -- it held the updated paragraph, which `raw_text` now is |
| **the claim** | states what the diff cannot show. See section 2 |
| **`diff3` / `compose`** | base is the binder, sides are the several marks' `raw_text` |
| **drift** | **DELETED** -- `Process: #62`, the middle touches no files |
| **the comparison unit** | **STRIPPED PROSE** -- markers off, newlines gone, every whitespace run collapsed, one string per paragraph. Sections 3 and 5 |

!! **THE CHECK IS `diff(binder[address], raw_text)` AGAINST THE CLAIM.** Roy, 2026-08-30:
*"the diff is between the binder at the address and the raw_text left in the mark after it
gets edited. That is the what proves the edit is what they stated was edited. If you have a
stage then the diff is between the stage binder and the mark raw_text."*

! **AT A STAGE, THE BASE IS THAT STAGE'S BINDER.** Stage N reads the revise pulled after
stage N-1, so "the original" always means the binder this copy was seeded from, never the
checkout.

! **NOTHING HERE READS OR WRITES A PAGE.** `Process: #62`.

---

## 2. The rule: carry the RESULT, or state the DELTA -- never both

Roy, 2026-08-30, on `correct`, `patch` and `add`: *"'the false clause', 'the sentence as it
stands' and 'and the anchor' are redundant and will make the other machinery more
complicated unless there is a specific holder for each ... but really diff3 to binder should
point this out."*

**Once the result is carried, the diff IS the delta.** Restating the existing half in the
claim is a second copy of something already derivable, and two copies can disagree.

| instruction | result | the claim carries |
| --- | --- | --- |
| `clean` | -- | nothing |
| `query` | -- | `shape`, `attempted`, `settles` -- not text, unchanged |
| `drop` | DERIVED | the sentence, verbatim |
| `correct` | carried | nothing about the text. **`sources` still owed** |
| `patch` | carried | nothing |
| `add` | carried | nothing |
| `move` origin | DERIVED | the sentence, verbatim |
| `move` destination | carried | nothing -- placement is expressed in the text |

!! **`add`'s CLAIM ANCHOR IS A SECOND ANCHOR ON THE SAME MARK.** `Mark.anchor` is a SEEDED
field -- *"the line of code the place sits on"* (`desk/mark.py:308`). `add`'s
`claim_all=("missing","anchor")` with `needs_anchor=True` adds a hand-typed one checked by
`ANCHOR_NAME`. The classifier's own docstring concedes the redundancy: *"a FORM check on
`claim.anchor`, not a side; the address says that."* Two anchors that can disagree, one of
them authored by the party being checked.

! **WHAT SURVIVES IS WHAT THE DIFF CANNOT SHOW**: a place (`from`, `to`), evidence
(`sources`), a reason, and a delta whose result was not carried.

---

## 3. The move, as a composite -- approach A

**A move is one authored object holding two halves.** Ruled `Process: #56`: *"A move needs to
be what it is and that is a composite Mark - Drop Here Add There. They have to go together
... Nothing else acts on two places at once."*

**A sentence moves without the paragraph moving** (Roy, 2026-08-30), so the origin keeps a
REMAINDER and both ends have new text.

### The authored form

```
move
  sentence   the moved sentence, verbatim, as it stands at the origin
  from       m.py@b1
  to         m.py@b7
  to_text    the destination paragraph as it reads once the sentence has arrived
  reason     why
```

### Why the two halves are not symmetric

Roy, 2026-08-30: *"The drop is one where you can formulate the drop and the text without
carrying the raw_text because it is a subtraction out of the binder text."* And, on the other
end: *"it could need to be inserted mid-paragraph."*

| half | is | result |
| --- | --- | --- |
| **origin** | a `drop` | **DERIVED**: `binder[from]` with `sentence` removed |
| **destination** | an `add` | **CARRIED** as `to_text`, because placement is not derivable |

! **A SUBTRACTION IS DETERMINED; AN INSERTION IS NOT.** Removing a named sentence has one
answer. Inserting one has as many answers as there are positions in the paragraph, so the
role must say which.

!! **A REWRAP IS INVISIBLE, SO NOTHING HAS TO FORBID ONE.** An earlier draft ruled that a
role may not re-flow the remainder, to keep the origin checkable. **That constraint is
RETIRED.** Roy, 2026-08-30: *"while it was a good thought it is brittle in so many ways
it is probably a good idea to retire that idea and get just the prose from the paragraphs
stripped of the white spacing and the comment markers. This makes the diff easy regardless
of if the agent flows the text around."*

! **AND A PURE REWRAP IS THEN NOT AN EDIT AT ALL** -- it produces an EMPTY diff, which is
the correct answer. A constraint that had to be policed becomes a property that holds by
itself.

### Why the equality check disappears

`sentence` is ONE field read at both ends. *"The text deleted at the origin equals the text
added at the destination"* was a check only while the two ends held separate strings. It is
now true by construction, and there is nothing left to verify.

---

## 4. The move region in the edit copy

Ruled `Process: #60`: *"no - separate semantics - will have to make a special spot in the
edit-copies for move marks because even one level up they are out of sync with what they
state they do."*

**An `edit_copy` is one slot per place; a move spans two.** So a move does not live in
`marks`:

```
edit_copy
  role
  read_from
  sheets[]        one per page
    path, sha
    marks[]       one slot per place -- clean, query, drop, correct, patch, add
  moves[]         one entry per move -- spans two places, may span two pages
```

! **THE DESTINATION IS NOT SEEDED AS A PLACE.** It is not a slot anyone rules on. The
destination's current text is read from the binder when the move is checked;
`desk.collator.base_texts(binder)` already builds `address -> raw_text` for every address.

! **`moves` SITS ON THE `edit_copy`, NOT ON A SHEET**, because a move may cross pages and a
sheet is one page.

---

## 5. The checks

For every substantive mark:

    diff(binder[address], raw_text) must match what the claim states.

For a move, at each end, with `base = binder`:

| check | asks |
| --- | --- |
| **sentence is real** | `sentence` is a substring of `binder[from]` |
| **origin** | derived: `binder[from]` minus `sentence`. Nothing asserted, nothing to check |
| **destination** | `diff(binder[to], to_text)` is exactly ONE insertion, equal to `sentence` |
| **both ends or neither** | a move that fails at either end fails whole |

!! **`quotes_original` PUTS THE MOVE ON AN EXISTING RAIL.** That classifier names the claim
key holding an existing sentence -- `claim.drop`, `claim.false`, `claim.from` -- and
`claim_verbatim_problems` substring-tests it against the base. `move`'s row is `""` today
because *"`move`'s from/to are PLACES"*. Setting it to `"sentence"` needs no new mechanism.

!! **EVERY COMPARISON ABOVE IS ON STRIPPED PROSE.** ! Measured 2026-08-30: `differences.py`
reports a sentence-level move as `replace` rather than `insert`, because the insertion
re-flows the lines after it -- a LINE diff cannot answer these questions at all. Stripped
prose is the representation that makes them arithmetic.

! **THE MIDDLE REASONS IN PROSE; THE COMPOSITOR SETS IT.** Wrapping, markers and the cap are
downstream of everything here -- the same boundary `Process: #62` draws.

! **SO THE ROLE NEED NOT WRAP WHAT IT RETURNS.** `to_text` is prose; one long line is a
legitimate answer. Placement is expressed by where the sentence sits in that prose, not by
how it is broken across lines.

---

## 6. What changes

### `desk/mark.py`

- **DELETE** the `change` field and `_change_problems`; `raw_text` is the result.
- **DELETE** `owes_change` from `Row`.
- **EMPTY the claim of `correct`, `patch` and `add`.** Both halves go in each case, not only
  the existing one: `correct`'s false AND true clause, `patch`'s sentence AND rewrite,
  `add`'s missing text AND anchor. **Every one of the six is visible in
  `diff(binder[address], raw_text)`.** `correct` keeps `owes_sources`, which is evidence
  rather than text.
- **DELETE** `needs_anchor`, `ANCHOR_NAME` and `ANCHOR_EXAMPLE` with `add`'s claim anchor --
  nothing else reads them. ! This makes half of `mark-holds-spec-and-parse` T6 moot: that
  task documents `ANCHOR_NAME` against `binder/annotate.py`'s `TICKED` per `Process: #61`.
  `TICKED` and its half stand; the `ANCHOR_NAME` half goes with the field.
- **SET** `move`'s `quotes_original = "sentence"`.
- `may_empty` exists so a `drop` may return `""` when the whole paragraph goes. **Its fate
  follows section 9's open question**: if `drop` derives its result like the move's origin,
  there is no returned text to be empty and the flag goes too.

### `binder/binder.py`

**The row gains the STRIPPED PROSE beside `raw_text`.** Ruled 2026-08-30 -- Roy, asked
whether the middle should recompute it or the binder should carry it: *"we can put it
in."*

! **THE CENSUS ALREADY COMPUTES IT AND THE BINDER DROPS IT.** `Paragraph.text` is
`_join(raw, openers)` -- markers stripped per line, joined, whitespace runs collapsed --
and `binder/binder.py` stores only `"raw_text": "\n".join(paragraph.raw_lines)`. The
work is done; the field is not kept.

!! **AND IT IS WHAT KEEPS THE LANGUAGE OUT OF THE MIDDLE.** Stripping needs a language's
comment markers. Recomputing in the desk would pull `reading.language` across the
boundary and re-derive per comparison; carrying it means the middle compares two strings
the binder handed it and needs to know nothing about either file. That is the same
separation as `Process: #62`.

! **THE ROW'S OWN DOCSTRING ALREADY ARGUES HALF OF THIS.** *"THE PROSE LEAVES AS ONE
STRING"* -- Roy: *"LLMs and the token parsers read this as a complete and coherent
statement. They do not read this as the same thing: ['LLMs and the token', 'parsers read
this as a', ...]"*. That ruling settled one string rather than a list of lines; this
settles prose rather than marked-up lines.

### `desk/containers.py`

- `EditCopy` gains `moves`; a new `Move` container holds one.
- `parse_edit_copy` refuses a move written into a per-place `marks` slot.

### `desk/collator.py`

- **DELETE** `drift_in` -- `Process: #62`.
- `places()` groups a move under BOTH addresses it touches.
- **DELETE** `_join_moves`'s kind-promotion; a composite cannot be half-held.
- **DELETE** `_sentence_key`'s `id(mark)` fallback for a move.

### `flows/collate.py`

- **DELETE** the provisional `id(mark)` dedup (`ac8cbbd`, marked provisional).
- `_resolve` must not run `_composition` over a move; a move is not a paragraph edit.
- `_chief_copy` writes a move to `moves`, once, with both addresses intact.

### `commands/collate.py`

- **DELETE** the `DRIFT` exit code and its reporting.

### `docs/the-mark.md` and `tests/gates/test_mark_shape.py`

- The field count drops; the claim table is rewritten; the gate reads the new headings.

---

## 7. What this fixes

| review finding | how |
| --- | --- |
| **CRITICAL** two roles agreeing on a move fold into two no-op `correct`s | `_resolve` no longer composes a move |
| **CRITICAL** the cycle guard is unreachable | moves reach `_move_order` because they are no longer eaten upstream |
| half a move applied | one object, both halves or neither |
| two moves sharing a destination fabricate swapped paragraphs | `_join_moves`'s cross-address union goes |
| a move written twice at one address | a move lives in `moves`, once |
| `_change_problems` refuses the specified shape | there is no `change` |

---

## 8. Out of scope

- **A move to a file the run never cued** -- `TODO/move-across-an-uncued-file.md`.
- **Splitting `desk/mark.py`** -- `TODO/mark-holds-spec-and-parse.md`, `Process: #59`.
- **Wiring the containers and the source-verification half** --
  `TODO/containers-and-verification-are-unwired.md`, `Process: #57`. This spec assumes
  neither is wired yet and does not depend on it.
- **The unqualified-address cluster** -- `filled()` cannot detect a bare cue. Separate, and
  it reaches the docket independently of anything here.

## 9. Open

- **Does `drop`'s change land in THIS plan or a later one?** Section 2 lists it as DERIVED
  because the rule gives no other answer -- a drop is a subtraction, so stating the sentence
  determines the result exactly as it does at a move's origin. What is open is SEQUENCING,
  not the decision: `drop` is otherwise untouched here, and pulling it in also removes
  `may_empty`. Landing it separately keeps this plan to the move; landing it here keeps the
  rule from being half-applied in the tree.
- **What refuses a move whose `to` names a place the binder does not hold?** The destination
  is read from the binder rather than seeded, so an unknown `to` has no text to diff against.
  `known_addresses` exists in `desk/collator.py` and `docket_from` does not consult it.
