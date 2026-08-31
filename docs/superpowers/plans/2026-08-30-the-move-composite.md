# The Move Composite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use
> checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make a `move` expressible and checkable, by settling what any mark carries -- the
binder holds the original, `raw_text` comes back edited, and the claim states only what the
diff cannot show.

**Architecture:** `change` is deleted; `raw_text` is seeded with the original and returned
edited, so `diff(binder[address], raw_text)` is the delta and the claim no longer repeats it.
A `move` becomes one authored object with two halves -- an origin that DERIVES its result by
subtracting a named sentence, and a destination that CARRIES its result because placement is
not derivable. Every comparison runs on stripped prose, which the binder now carries.

**Tech Stack:** Python 3.11 (floor, annotations EAGER), standard library only under
`src/comment_review/**`, `pytest`, `ruff`, `ty`.

**Spec:** `docs/superpowers/specs/2026-08-30-the-move-composite-design.md` -- read it with
this plan. Rulings: `decision-log.md Process: #56`, `#57`, `#60`, `#61`, `#62`.

## Global Constraints

- Run everything through `uv run`. Python **3.11** floor; annotations are EAGER, so a name in
  an annotation must be imported at runtime.
- `src/comment_review/**` imports the **standard library and nothing else**. `tests/` may use
  `pytest`.
- **No `except` clause in a shipped file holds a tuple literal** -- bind every exception tuple
  to a name.
- **ASCII only.** `--` for an em dash.
- **No subjective claims.** If a sentence cannot be falsified by reading the code or running a
  command, it does not belong.
- **`clean` is a RESERVED WORD** -- one of seven instructions (`clean`, `query`, `drop`,
  `correct`, `patch`, `add`, `move`) -- never a loose adjective, in code, prose or a commit
  message.
- **No sentence may name a symbol, file or test that does not exist at that commit.**
- **NO HEREDOCS AND NO `sed`.** A `PreToolUse` hook refuses them. Use `Edit`/`Write`, `Grep`,
  and write a commit message to a file then `git commit -F <file>`. A repeated edit is a
  `.py` script run with `uv run python`.
- `uv run ruff check .`, `uv run ruff format --check .` and `uv run ty check` (bare, both
  trees) must pass. Run `ruff check` AGAIN after any format.
- `tests/gates/test_build.py::TestTheShippedTreeMatchesTheSource::test_the_plugin_is_built_from_the_current_source`
  is EXPECTED to fail throughout -- `plugins/` is built at RELEASE, not during development.
  Roy: *"At release time. Not on development time."* Exactly one failure is correct.
- **The middle touches no files** (`Process: #62`). Nothing in `desk/`, `flows/` or
  `commands/collate.py` opens a page.
- Do not `git push`. Do not amend existing commits.

## A note on this plan's code blocks

Test code in this plan is exact and may be transcribed. **Implementation blocks are exact
only where the plan quotes existing code it has read.** Where a task changes a function whose
body this plan does not quote -- `places`, `_join_moves`, `_sentence_key`, `_outcome`,
`_resolve`, `_composition`, `_chief_copy` -- the step names the file, the function and the
change, and the implementer **reads that function first**. Inventing a replacement for a body
nobody read is how a plan ships a defect; this is stated rather than papered over.

---

## File structure

| file | responsibility after this plan |
| --- | --- |
| `binder/binder.py` | a row carries `raw_text` AND `text`, the stripped prose |
| `desk/mark.py` | the seven instructions, the classifier table, `Mark`, the boundary parse. No `change` |
| `desk/move.py` | **NEW** -- the `Move` composite and its two halves |
| `desk/containers.py` | `EditCopy` gains `moves`; a `Move` container beside `Sheet` |
| `desk/collator.py` | judges the SET. No `drift_in` |
| `flows/collate.py` | folds a stage. Moves are not composed |
| `commands/collate.py` | the console face. No `DRIFT` |
| `docs/the-mark.md` | the published shape -- the gate reads its headings |
| `tests/helpers.py` | builders, including a composite `a_move` |

---

### Task 1: The binder row carries stripped prose

**Files:**
- Modify: `src/comment_review/binder/binder.py:75-103`
- Test: `tests/test_binder_records_its_root.py`

**Interfaces:**
- Consumes: `reading.lexer.Paragraph`, which already has `.text` -- `_join(raw, openers)`,
  markers stripped per line, joined, every whitespace run collapsed to one space.
- Produces: every binder row carries `"text"`, the paragraph as ONE prose string. Tasks 8 and
  9 compare these.

**Why:** the census computes the stripped prose and the binder drops it. Roy, 2026-08-30,
asked whether the middle should recompute it or the binder carry it: *"we can put it in."*
Carrying it keeps `reading.language` out of the desk -- stripping needs a language's comment
markers, and the middle must not need to know a file's language.

- [ ] **Step 1: Write the failing test**

```python
def test_a_row_carries_the_stripped_prose_beside_the_raw_lines():
    """The wrapped comment is one prose string, markers and newlines gone."""
    source = "# The rate is capped\n# at five percent.\ndef f(): pass\n"
    page = <build a real page over `source` -- see below>
    row = bind([page], read_from={"root": "."})["pages"][0]["rows"][0]
    assert row["raw_text"] == "# The rate is capped\n# at five percent."
    assert row["text"] == "The rate is capped at five percent."
```

!! **BUILD THE PAGE WITH `binder.page.page_for` OVER REAL SOURCE, NEVER A HAND-WRITTEN
LITERAL.** Its signature is `page_for(path, text, lang, rel=None, *, sha)` and it needs a
`Language`; **read `tests/conftest.py` and use the construction the suite already has** rather
than writing your own. The angle-bracket line above is the one thing in this plan you must
replace by reading, because naming a wrapper that may not exist would be worse than saying so.

! **THIS MATTERS MORE THAN IT LOOKS.** This repo replaced its whole suite in 2026-08-25
because hand-authored fixtures were built in the shape the code expected, so they could only
CONFIRM -- and when the contract moved they went on asserting the old one.

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest tests/test_binder_records_its_root.py -k stripped_prose -v`
Expected: FAIL with `KeyError: 'text'`.

- [ ] **Step 3: Add the field**

In the row dict returned around `binder.py:75-103`, beside `"raw_text"`:

```python
        "raw_text": "\n".join(paragraph.raw_lines),
        # !! THE PROSE, AND IT IS WHAT THE MIDDLE COMPARES. `raw_text` keeps the
        # markers and the line breaks because the write chain needs them; every
        # question the desk asks is about the PROSE, and stripping it there would
        # need this language's comment markers -- pulling `reading.language`
        # across a boundary the middle does not otherwise cross. The census has
        # already computed this; storing it is keeping work rather than doing it.
        "text": paragraph.text,
```

- [ ] **Step 4: Run it and watch it pass**

Run: `uv run pytest tests/test_binder_records_its_root.py -k stripped_prose -v` -- PASS.
Then `uv run pytest -q` -- only the expected `test_build` failure.

- [ ] **Step 5: Tick this task's box here and in the parent plan, then commit**

Commit the work first, then tick `TODO/move-is-a-composite-mark.md` and this plan in a
SECOND commit that cites the first commit's SHA. A box asserts work is done, and the work is
not done until it is committed.

---

### Task 2: Delete drift

**Files:**
- Modify: `src/comment_review/desk/collator.py` -- remove `drift_in`
- Modify: `src/comment_review/flows/collate.py` -- remove the `drift` field on `Collated`
- Modify: `src/comment_review/commands/collate.py` -- remove `DRIFT` and its reporting
- Modify: `tests/test_collator.py`, `tests/test_collate.py`, `tests/test_collate_command.py`

**Interfaces:**
- Produces: `Collated` without `drift`; the command's exit codes without `DRIFT`.

**Why:** `Process: #62`. Roy: *"the middle doesn't care if the pages have changed - it is not
reading or writing to the pages at all."* `drift_in` asks whether the tree moved under a
role, and the middle is not editing the tree. ! `ac8cbbd` gave `DRIFT` its own exit code
earlier the same day; that repair pointed the wrong way and this reverses it.

- [ ] **Step 1: Write the failing test**

```python
def test_the_middle_carries_no_drift_check():
    """`Process: #62` -- nothing in the middle asks whether a page changed."""
    import comment_review.desk.collator as collator
    import comment_review.flows.collate as collate
    import comment_review.commands.collate as command

    assert not hasattr(collator, "drift_in")
    assert "drift" not in {f.name for f in dataclasses.fields(collate.Collated)}
    assert not hasattr(command, "DRIFT")
```

- [ ] **Step 2: Run it and watch it fail**

Run: `uv run pytest -k the_middle_carries_no_drift_check -v`
Expected: FAIL on the first assertion.

- [ ] **Step 3: Delete it**

Remove `drift_in` and its `Problem`-building. Remove `drift` from `Collated` and every
construction of it. In `commands/collate.py` remove the `DRIFT` constant, its branch, and its
printing. **Read each site before cutting** -- `grep -rn "drift" src/comment_review/`.

! The exit codes must stay a closed set with no gap where `DRIFT` was. Renumber so the
remaining codes are contiguous, and say in the module docstring what each means.

- [ ] **Step 4: Run the suite**

`uv run pytest -q`, `uv run ruff check .`, `uv run ty check`. Delete the tests that only
exercised drift; a test left asserting a deleted behaviour is a finding, not a pass.

- [ ] **Step 5: Tick the boxes, then commit** (work first, tick second, citing the SHA)

---

### Task 3: Delete `change`; `raw_text` is the result

**Files:**
- Modify: `src/comment_review/desk/mark.py` -- the `Mark` dataclass, `_change_problems`,
  `parse`, `Row.owes_change`, `ROLE_FIELDS`
- Modify: every consumer -- `grep -rn '"change"\|\.change\b' src/comment_review/`
- Test: `tests/test_mark.py`

**Interfaces:**
- Consumes: nothing new.
- Produces: `Mark` with SEVEN fields -- `address`, `anchor`, `raw_text`, `instruction`,
  `claim`, `reason`, `sources`. `Mark.raw_text` is the result.

**Why:** Roy, 2026-08-30: *"the diff is between the binder at the address and the raw_text
left in the mark after it gets edited. That is the what proves the edit is what they stated
was edited."* The binder holds the only original, so a mark echoing one back was a second
copy of something already held.

- [ ] **Step 1: Write the failing test**

```python
def test_a_mark_carries_no_change_field():
    """`raw_text` comes back edited; the binder holds the original."""
    assert "change" not in {f.name for f in dataclasses.fields(Mark)}


def test_a_returned_mark_keeps_the_edited_text_as_raw_text():
    entry = a_correct("m.py@b1")
    entry["raw_text"] = "The rate is capped at five percent."
    mark, problems = parse("m.py@b1", entry)
    assert problems == []
    assert mark.raw_text == "The rate is capped at five percent."
```

- [ ] **Step 2: Run and watch both fail**

Run: `uv run pytest tests/test_mark.py -k change_field -v` -- FAIL.

- [ ] **Step 3: Cut it**

Delete the `change` field from `Mark`, delete `_change_problems` entirely, delete
`owes_change` from `Row` and from all seven rows, and remove `"change"` from `ROLE_FIELDS`.
In `parse`, drop the `spec.owes_change` branch.

! `ROLE_FIELDS` is what `untouched` reads to say nobody wrote in a slot. `raw_text` is SEEDED,
so it must NOT join `ROLE_FIELDS` -- a seeded slot carries it already and an untouched slot
would otherwise read as filled. Read `untouched`'s docstring before changing it.

- [ ] **Step 4: Run the suite and follow the breakage**

`uv run pytest -q`. Every failure is a consumer that read `change`; fix each to read
`raw_text`. `uv run ty check` will name the rest.

- [ ] **Step 5: Tick the boxes, then commit**

---

### Task 4: Empty the claims of `correct`, `patch` and `add`; delete the second anchor

**Files:**
- Modify: `src/comment_review/desk/mark.py` -- `INSTRUCTIONS` rows, `Row.needs_anchor`,
  `ANCHOR_NAME`, `ANCHOR_EXAMPLE`, `_claim_problems`
- Modify: `docs/the-mark.md` -- the claim table and the classifier counts
- Test: `tests/test_mark.py`

**Interfaces:**
- Produces: `correct`, `patch` and `add` with `claim_all = ()`. `correct` keeps
  `owes_sources=True`.

**Why:** Roy, 2026-08-30: *"'the false clause', 'the sentence as it stands' and 'and the
anchor' are redundant and will make the other machinery more complicated."* Once the result is
carried, `diff(binder[address], raw_text)` IS the delta. **Both halves go** -- the new text is
as visible in the diff as the old.

!! **`ANCHOR_NAME` IS PROTOTYPE RESIDUE, WHICH IS THE STRONGER REASON.** Byte-identical to
`prototype/original/record.py:296`, ported into `src/` by `67dc82b`. Roy: *"If I had known
that something like that had slipped from the v0.2.2 prototype into here I would have had you
drop it."* `Process: #61` was corrected the same day; `binder/annotate.py`'s `TICKED` stands.

- [ ] **Step 1: Write the failing test**

```python
def test_the_carrying_instructions_state_nothing_the_diff_shows():
    for name in (Instruction.CORRECT, Instruction.PATCH, Instruction.ADD):
        assert INSTRUCTIONS[name].claim_all == ()


def test_correct_still_owes_its_evidence():
    assert INSTRUCTIONS[Instruction.CORRECT].owes_sources is True


def test_the_second_anchor_is_gone():
    import comment_review.desk.mark as mark
    assert not hasattr(mark, "ANCHOR_NAME")
    assert not hasattr(mark, "ANCHOR_EXAMPLE")
    assert "needs_anchor" not in {f.name for f in dataclasses.fields(mark.Row)}
```

- [ ] **Step 2: Run and watch them fail**

- [ ] **Step 3: Cut**

Set `claim_all=()` on those three rows. Delete `needs_anchor` from `Row` and from `add`'s
row, delete `ANCHOR_NAME` and `ANCHOR_EXAMPLE`, and delete the `spec.needs_anchor` branch in
`_claim_problems`. `add`'s `quotes_original` is already `""`.

- [ ] **Step 4: Update `docs/the-mark.md`**

Rewrite the claim table so those three rows carry nothing about the text, and RECOUNT the
classifier headings -- `## The classifiers -- <N> COLUMNS AND A CLOSED LIST OF FLAGS` and
`**The flags, and there are <N>:**`. `tests/gates/test_mark_shape.py` asserts
`columns + flags == len(fields(Row))` and reads both numbers out of those headings, so the
gate follows the document. **Recount from the table; do not decrement.**

- [ ] **Step 5: Run the gate**

`uv run pytest tests/gates/test_mark_shape.py -v` -- PASS. Then the full suite.

- [ ] **Step 6: Tick the boxes, then commit**

---

### Task 5: `drop` derives its result; delete `may_empty`

**Files:**
- Modify: `src/comment_review/desk/mark.py` -- `drop`'s row, `Row.may_empty`
- Modify: `docs/the-mark.md`
- Test: `tests/test_mark.py`

**Interfaces:**
- Produces: `drop` with `claim_all=("drop",)` and `quotes_original="drop"`, and no carried
  result. `Row` loses `may_empty`.

**Why:** Roy, 2026-08-30: *"The drop is one where you can formulate the drop and the text
without carrying the raw_text because it is a subtraction out of the binder text."* A named
sentence removed from a known base has exactly one answer.

!! **THIS IS A RULING TAKEN WHILE WRITING THIS PLAN, AND IT IS THE ONE TO OVERRIDE FIRST IF
IT IS WRONG.** The spec's section 9 left the SEQUENCING open -- this plan or a later one --
not the decision. It lands here because leaving it out half-applies *carry the result or
state the delta*, and a rule applied to some instructions and not others is the shape that
produced this repo's measured "two spellings, one of them unsafe" defects.

! `may_empty` exists so a `drop` may return `""` when the whole paragraph goes. With the
result derived there is no returned text to be empty, so the flag has nothing left to say.

- [ ] **Step 1: Write the failing test**

```python
def test_a_drop_states_its_sentence_and_carries_no_result():
    assert INSTRUCTIONS[Instruction.DROP].claim_all == ("drop",)
    assert INSTRUCTIONS[Instruction.DROP].quotes_original == "drop"


def test_may_empty_is_gone():
    import comment_review.desk.mark as mark
    assert "may_empty" not in {f.name for f in dataclasses.fields(mark.Row)}
```

- [ ] **Step 2: Run and watch it fail**
- [ ] **Step 3: Delete `may_empty` from `Row` and from `drop`'s row**
- [ ] **Step 4: Update `docs/the-mark.md` and RECOUNT the classifier headings**
- [ ] **Step 5: Run the gate and the suite**
- [ ] **Step 6: Tick the boxes, then commit**

---

### Task 6: The `Move` composite

**Files:**
- Create: `src/comment_review/desk/move.py`
- Test: `tests/test_move.py`

**Interfaces:**
- Consumes: `desk.mark.Instruction`, `desk.mark.filled`.
- Produces: the type below. !! **THE WIRE AND THE TYPE USE DIFFERENT NAMES ON PURPOSE.** A
  role sends `from` and `to`, because those are the words the instruction set already uses
  for a move's two places. The dataclass calls them `origin` and `destination`, because
  `from` is a Python keyword and cannot be a field name. **`parse_move` is the only place the
  two meet**, and no other module maps them.

```python
@dataclass(frozen=True)
class Move:
    sentence: str      # the moved sentence, verbatim, as it stands at the origin
    origin: str        # an address
    destination: str   # an address
    to_text: str       # the destination paragraph once the sentence has arrived
    reason: str

    def addresses(self) -> tuple[str, str]: ...

def parse_move(where: str, entry: object) -> tuple["Move | None", list[str]]: ...
```

**Why:** `Process: #56`. Roy: *"A move needs to be what it is and that is a composite Mark -
Drop Here Add There. They have to go together ... Nothing else acts on two places at once."*

- [ ] **Step 1: Write the failing tests**

```python
def test_a_move_names_a_sentence_and_two_places():
    move, problems = parse_move("m.py@b1", {
        "sentence": "Rates are capped at five percent.",
        "from": "m.py@b1",
        "to": "m.py@b7",
        "to_text": "Callers retry. Rates are capped at five percent.",
        "reason": "it belongs with the retry rule",
    })
    assert problems == []
    assert move.addresses() == ("m.py@b1", "m.py@b7")


def test_a_move_onto_its_own_address_is_refused_by_name():
    move, problems = parse_move("m.py@b1", {
        "sentence": "x.", "from": "m.py@b1", "to": "m.py@b1",
        "to_text": "x.", "reason": "r",
    })
    assert move is None
    assert any("its own address" in p for p in problems)


def test_a_move_missing_its_sentence_is_refused_by_name():
    move, problems = parse_move("m.py@b1", {
        "from": "m.py@b1", "to": "m.py@b7", "to_text": "x.", "reason": "r",
    })
    assert move is None
    assert any("sentence" in p for p in problems)
```

- [ ] **Step 2: Run and watch them fail** -- `ModuleNotFoundError`.

- [ ] **Step 3: Write the module**

`parse_move` returns `(None, problems)` or `(Move, [])` -- the same two-outcome shape as
`desk.mark.parse`, which `tests/test_mark.py::TestTheParseHasNoThirdOutcome` already pins for
marks. Refuse: a missing or blank `sentence`, `from`, `to`, `to_text` or `reason`; and
`from == to`, by name.

! Use `desk.mark.filled` rather than a bare truthiness test -- it returns `TypeGuard[str]`
and narrows, which is why `desk/collator.py` was able to stop restating it inline.

- [ ] **Step 4: Run the tests** -- PASS. Then the suite.
- [ ] **Step 5: Tick the boxes, then commit**

---

### Task 7: The move region in the edit copy

**Files:**
- Modify: `src/comment_review/desk/containers.py`
- Modify: `src/comment_review/flows/distribute.py` -- `seed` writes an empty `moves`
- Test: `tests/test_containers.py`

**Interfaces:**
- Produces: `EditCopy` with `moves: tuple[Move, ...]`; `parse_edit_copy` refuses a `move`
  written into a per-place `marks` slot.

**Why:** `Process: #60`. Roy: *"will have to make a special spot in the edit-copies for move
marks because even one level up they are out of sync with what they state they do."* An
`edit_copy` is one slot per place; a move spans two.

- [ ] **Step 1: Write the failing tests**

```python
def test_an_edit_copy_carries_its_moves_beside_its_sheets():
    copy, problems = parse_edit_copy({
        "role": "block-context",
        "read_from": {"root": "."},
        "sheets": [],
        "moves": [{
            "sentence": "x.", "from": "m.py@b1", "to": "m.py@b7",
            "to_text": "y. x.", "reason": "r",
        }],
    })
    assert problems == []
    assert len(copy.moves) == 1


def test_a_move_written_into_a_place_slot_is_refused_by_name():
    """A move spans two places; a slot answers for one."""
    copy, problems = parse_edit_copy(a_copy_whose_only_mark_names_instruction("move"))
    assert copy is None
    assert any("move" in p and "moves" in p for p in problems)
```

! Build the second input from `seed()` over a real binder and then set the instruction, so
the test's input is the shape the system actually hands out.

- [ ] **Step 2: Run and watch them fail**
- [ ] **Step 3: Add `moves` to `EditCopy` and `parse_edit_copy`; refuse a `move` in `marks`**

`moves` sits on the `edit_copy`, NOT on a sheet -- a move may cross pages and a sheet is one
page. An absent `moves` key parses as empty; it is not an error.

- [ ] **Step 4: `seed` writes `"moves": []`** so a role receives the region rather than
  having to invent it. Read `flows/distribute.py`'s copy builder first.

- [ ] **Step 5: Carry `moves` through `desk/proof.py`'s `gather`**

`gather` collects the returned copies for the flow. A region it does not know about is a
region the flow never sees, so a move would vanish between the role and the fold with nothing
reporting it. Read `gather` first, then add a test:

```python
def test_gather_carries_a_copys_moves_through():
    """A region gather does not know about is one the flow never sees."""
    gathered = gather([a_copy_with_one_move()], binder)
    assert len(gathered["edit_copies"][0]["moves"]) == 1
```

- [ ] **Step 6: Add the builders the later tasks need, to `tests/helpers.py`**

Tasks 8, 9 and 10 all build moves. Define them ONCE, here, where the region first exists:

```python
def a_move_of(sentence: str, origin: str, destination: str, to_text: str) -> dict:
    """One move entry, in the WIRE shape -- `from`/`to`, not origin/destination."""


def copies_with_moves(pairs: list[tuple[str, str, str]]) -> list[dict]:
    """One copy per (sentence, origin, destination), all from one role."""


def two_roles_proposing(move: dict) -> list[dict]:
    """The SAME move returned by two roles -- the CRITICAL's input."""


def a_master_proof_with_moves(triples: list[tuple[str, str, str]]) -> dict:
    """A master_proof whose copies carry moves, for `reconcile`."""


def every_mark(reconciled) -> list[dict]:
    """Every mark in a reconcile result, across all buckets."""


def one_role_proposing(move: dict) -> list[dict]:
    """A single role's copy carrying one move -- the ordinary case."""


def a_copy_with_one_move() -> dict:
    """One edit_copy whose `moves` holds exactly one entry, for `gather`."""


def a_copy_whose_only_mark_names_instruction(name: str) -> dict:
    """A copy with one PLACE SLOT whose instruction is `name`.

    Built from `seed()` over a real binder and then filled, so the input is the
    shape the system hands out. Task 7 uses it with "move" to prove a move
    written into a per-place slot is refused.
    """
```

!! **BUILD EVERY ONE OF THESE FROM `seed()` AND `bind()` OVER A REAL BINDER, NOT FROM
LITERALS.** A builder that constructs the shape the code expects can only agree with it.

!! **THE WIRE KEYS ARE `from` AND `to`; THE DATACLASS FIELDS ARE `origin` AND
`destination`.** `parse_move` is where the two meet, and it is the ONLY place that maps them.
A builder writes wire keys because that is what a role sends.

- [ ] **Step 7: Run the suite**
- [ ] **Step 8: Tick the boxes, then commit**

---

### Task 8: The move's checks

**Files:**
- Modify: `src/comment_review/desk/move.py`
- Test: `tests/test_move.py`

**Interfaces:**
- Consumes: binder rows carrying `text` (Task 1).
- Produces:

```python
def move_problems(where: str, move: Move, prose: dict[str, str]) -> list[str]: ...
```

`prose` maps address -> the binder's stripped prose. Returns `[]` or named problems.

**Why:** spec section 5. The origin is DERIVED so nothing is asserted there; the destination
is CARRIED so it is checked.

!! **EVERY COMPARISON IS ON STRIPPED PROSE.** Measured 2026-08-30: `results/differences.py`
reports a sentence-level move as `replace` rather than `insert`, because the insertion
re-flows the lines after it -- a LINE diff cannot answer these questions at all.

- [ ] **Step 1: Write the failing tests**

```python
BASE = {
    "m.py@b1": "The rate is capped. Rates are capped at five percent.",
    "m.py@b7": "Callers retry.",
}


def test_a_sentence_that_is_not_at_the_origin_is_refused():
    move = a_move_of("Nothing says this.", "m.py@b1", "m.py@b7", "Callers retry.")
    assert any("not at" in p for p in move_problems("w", move, BASE))


def test_a_destination_that_gained_more_than_the_sentence_is_refused():
    move = a_move_of(
        "Rates are capped at five percent.", "m.py@b1", "m.py@b7",
        "Callers retry. Rates are capped at five percent. And something else.",
    )
    assert any("more than" in p for p in move_problems("w", move, BASE))


def test_a_destination_that_did_not_gain_the_sentence_is_refused():
    move = a_move_of(
        "Rates are capped at five percent.", "m.py@b1", "m.py@b7", "Callers retry.",
    )
    assert move_problems("w", move, BASE) != []


def test_a_move_inserted_MID_PARAGRAPH_is_accepted():
    """Placement is the destination's to choose; only the content is checked."""
    base = dict(BASE, **{"m.py@b7": "Callers retry. Then they give up."})
    move = a_move_of(
        "Rates are capped at five percent.", "m.py@b1", "m.py@b7",
        "Callers retry. Rates are capped at five percent. Then they give up.",
    )
    assert move_problems("w", move, base) == []


def test_a_REWRAP_at_the_destination_is_not_a_change():
    """Stripped prose: how the role broke its lines is invisible."""
    move = a_move_of(
        "Rates are capped at five percent.", "m.py@b1", "m.py@b7",
        "Callers    retry.\n   Rates are capped at five percent.",
    )
    assert move_problems("w", move, BASE) == []


def test_a_destination_the_binder_does_not_hold_is_refused_by_name():
    move = a_move_of("Rates are capped at five percent.", "m.py@b1", "z.py@b1", "x.")
    assert any("z.py@b1" in p for p in move_problems("w", move, BASE))
```

- [ ] **Step 2: Run and watch them fail**

- [ ] **Step 3: Implement `move_problems`**

Normalise `to_text` the same way the binder normalised its own prose -- collapse every
whitespace run to one space and strip -- then:

1. refuse when `destination` is not a key of `prose`, naming the address;
2. refuse when `sentence` is not a substring of `prose[origin]`, naming the origin;
3. refuse when removing `sentence` from the normalised `to_text` does not leave exactly
   `prose[destination]`.

! Check 3 is the whole destination check: what arrived is the sentence and nothing else, and
what was already there is unchanged. It says nothing about WHERE, which is the point.

- [ ] **Step 4: Run the tests** -- all six PASS. Then the suite.
- [ ] **Step 5: Tick the boxes, then commit**

---

### Task 9: The collator groups a move by both its places

**Files:**
- Modify: `src/comment_review/desk/collator.py` -- `places`, `_join_moves`, `_sentence_key`
- Test: `tests/test_collator.py`, `tests/test_reconcile.py`

**Interfaces:**
- Consumes: `desk.move.Move`.
- Produces: `places()` returns a move under BOTH of its addresses; `_join_moves`'s
  kind-promotion is gone.

**Why:** a composite cannot be half-held, so the promotion hack that lifted one end's kind to
match the other has nothing left to do. `ac8cbbd` marked it PROVISIONAL against exactly this.

!! **READ EACH OF THE THREE FUNCTIONS BEFORE CHANGING IT.** This plan does not quote their
bodies. `_join_moves` was measured on 2026-08-30 to union `marks` across two ends whose base
paragraphs differ, which fabricated two `correct`s that SWAPPED the paragraphs at two
origins -- so its removal is the fix for a HIGH, not tidying.

- [ ] **Step 1: Write the failing test**

```python
def test_two_moves_sharing_a_destination_do_not_fabricate_an_edit():
    """MEASURED 2026-08-30: this produced two `correct`s swapping two origins."""
    proof = a_master_proof_with_moves([
        ("s1.", "a.py@b1", "c.py@b1"),
        ("s2.", "b.py@b1", "c.py@b1"),
    ])
    got = reconcile(proof)
    instructions = [m["instruction"] for m in every_mark(got)]
    assert "correct" not in instructions
```

- [ ] **Step 2: Run and watch it fail**
- [ ] **Step 3: Group moves by both addresses; delete the kind-promotion**
- [ ] **Step 4: Delete `_sentence_key`'s `id(mark)` fallback**, which existed only because a
  move had no stable key. Read it first: an `id()` key made every multi-mark move place a
  re-read, which is the upstream cause of Task 10's CRITICAL.
- [ ] **Step 5: Run the suite**
- [ ] **Step 6: Tick the boxes, then commit**

---

### Task 10: The flow stops composing moves, and writes them once

**Files:**
- Modify: `src/comment_review/flows/collate.py` -- `_resolve`, `_composition`, `_chief_copy`,
  and the provisional `id(mark)` dedup
- Test: `tests/test_collate.py`

**Interfaces:**
- Produces: a chief copy whose `moves` holds each move ONCE, with both addresses intact.

**Why:** **both CRITICALs from the eight-file review.** Measured 2026-08-30: `_resolve` runs
`_composition` over `reconcile`'s `rereads` with no filter on instruction, and every
multi-mark move place is a re-read -- so two roles proposing the SAME move were folded into
two no-op `correct`s with `order == []`, `rereads == []` and `problems == []`. The relocation
was destroyed and the run reported a clean fold. **A two-cycle was eaten the same way**, so
`_move_order`'s cycle refusal never saw the input it exists for.

- [ ] **Step 1: Write the failing tests**

```python
def test_two_roles_agreeing_on_one_move_keep_the_move():
    """CRITICAL, measured 2026-08-30: both were folded into no-op `correct`s."""
    got = collate("4c", two_roles_proposing(a_move_of("s.", "m.py@b1", "m.py@b7")), binder)
    assert len(got.chief["moves"]) == 1
    assert got.chief["moves"][0]["from"] == "m.py@b1"


def test_a_two_cycle_reaches_the_cycle_refusal():
    """CRITICAL: cycles were eaten upstream, so the guard could not fire."""
    got = collate("4c", copies_with_moves([
        ("s1.", "m.py@b1", "m.py@b7"),
        ("s2.", "m.py@b7", "m.py@b1"),
    ]), binder)
    assert got.problems != []
    assert any("cycle" in str(p) for p in got.problems)


def test_one_move_reaches_the_chief_copy_once():
    got = collate("4c", one_role_proposing(a_move_of("s.", "m.py@b1", "m.py@b7")), binder)
    assert len(got.chief["moves"]) == 1
```

- [ ] **Step 2: Run and watch them fail**
- [ ] **Step 3: Make `_resolve` skip moves.** A move is not a paragraph edit and
  `_composition` has nothing to say about one. Read `_resolve` first.
- [ ] **Step 4: `_chief_copy` writes moves to `moves`, once.** Delete the provisional
  `id(mark)` dedup and the comment that marks it provisional -- read `ac8cbbd` for what it
  stood in for, and confirm nothing else depended on it.
- [ ] **Step 5: Run the suite.** `tests/test_collate.py` has tests written against the
  provisional behaviour; a test asserting a deleted behaviour is a finding, not a pass.
- [ ] **Step 6: Tick the boxes, then commit**

---

### Task 11: The published shape, the gate, and the builders

**Files:**
- Modify: `docs/the-mark.md`
- Modify: `tests/gates/test_mark_shape.py`
- Modify: `tests/helpers.py` -- `a_move`
- Modify: `references/vocabulary.toml` if a role's text uses a new term

**Interfaces:**
- Produces: a published shape a role can be handed, and builders that build the composite.

**Why:** `docs/the-mark.md` is the source a role reads and the gate reads its headings. A
spec that still describes `change` and a composite `change` field would be the defect this
repo exists to catch, in the file that publishes the rules.

- [ ] **Step 1: Rewrite `## The fields -- eight` to SEVEN**, and recount by reading the
  table rather than decrementing the word.
- [ ] **Step 2: Rewrite `## move is TWO OPERATIONS UNDER ONE LABEL, AND IT IS INDIVISIBLE`.**
  Its current text says `change` carries the composite of both paragraphs -- superseded by
  `Process: #56`. Keep the INDIVISIBILITY, which stands; replace the mechanism.
- [ ] **Step 3: Rewrite the claim table** so `correct`, `patch` and `add` carry nothing about
  the text and `move` carries `sentence`, `from`, `to`.
- [ ] **Step 4: Update `tests/helpers.py`'s `a_move`** to build the composite. **No helper
  may build a move whose change is a single string** -- that shape is what made every move
  test confirm the defect.
- [ ] **Step 5: Run every gate**

```bash
uv run pytest -q
uv run ruff check . && uv run ruff format --check .
uv run ty check
uv run python scripts/check_shipped_syntax.py
uv run python scripts/check_vocabulary.py
```

- [ ] **Step 6: Tick the boxes, then commit**

---

## Ticking is its own step, in every task

Roy, 2026-08-30: *"after each step in the plan there must be an intermediate step to check off
the plan and superpowers plan. Explicit steps always."* And: *"It lands in the commit after
the work it records as finished is finished."*

**A box asserts the work is DONE, and the work is not done until it is committed** -- so a
tick in the same commit asserts a completion that has not happened yet. Each task therefore
ends: run the checks, commit the work, THEN tick this plan and
`TODO/move-is-a-composite-mark.md`, citing that commit, and commit the tick.

!! **READ THE BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** Measured on this repo the same day:
`P21` was ticked with two of its three verify clauses unmet, and `no-command-for-the-middle`'s
T1 was ticked against a chain that does not run. **Not ticking what is done and ticking what
is not are the same error** -- treating a box as bookkeeping rather than as a claim.

## Not in scope

- **A move to a file the run never cued** -- `TODO/move-across-an-uncued-file.md`.
- **Splitting `desk/mark.py`** -- `TODO/mark-holds-spec-and-parse.md`, `Process: #59`.
- **Wiring the containers and the source-verification half** --
  `TODO/containers-and-verification-are-unwired.md`, `Process: #57`.
- **The unqualified-address cluster** -- `filled()` cannot detect a bare cue, measured at 62
  of 78 marks. It reaches the docket independently of anything here.
