# SP-1: The Containers and the Collate Flow -- Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give the middle of the review chain a command -- one flow that folds a stage's
returned `edit_copies` into the copy chief's own `edit_copy` and reports, by address,
everything it could not resolve.

**Architecture:** `flows/collate.py` runs the existing `gather` / `places` / `reconcile`
and then resolves downstream of them, leaving `desk.collator.Reconciled` untouched as the
intermediate. Three container types get a boundary parse in `desk/containers.py`; the
`Mark` grows its third seeded field so every seeded field is written from one place; and
`results/differences.py` gains a `compose` beside `diff3`. `flows/marks.py` becomes
`flows/distribute.py`, so the two halves of a round read as `distribute` and `collate`.

**Tech Stack:** Python 3.11 (the floor), stdlib only in `src/comment_review/**`, `pytest`
for tests, `ruff` and `ty` as pinned dev dependencies. Everything is run through `uv run`.

**Spec:** [`docs/superpowers/specs/2026-08-30-sp1-the-containers-and-the-collate-flow-design.md`](../specs/2026-08-30-sp1-the-containers-and-the-collate-flow-design.md)

**Plan (`P`):** [`docs/plans/0.2.4-the-commands-for-the-middle.md`](../../plans/0.2.4-the-commands-for-the-middle.md)
-- SP-1 delivers `P36`, `P34`, `P35`, `P21`, `P13`, `P1`, `P2`, `P24`, `P3`, `P37`, plus `D9`.

**Lane:** `backend`. No file under `plugins/comment-review/agents/`, `SKILL.md` or
`references/*.md` is touched -- verified 2026-08-30: no agent-facing file names
`mark --shape`, `--seed` or `--check`. `references/vocabulary.toml` and
`docs/vocabulary.md` belong to no lane and are updated here under the standing
crossing exception (`docs/conventions.md`, *The vocabulary is shared*).

---

## Global Constraints

Every task's requirements implicitly include this section.

- **Python 3.11 is the floor.** Run everything through `uv run`. A bare `python` is a
  different interpreter and re-opens the PEP 649 gap measured 2026-08-17.
- **`src/comment_review/**` imports the standard library and nothing else.**
  `tests/test_shipped_imports.py` enforces it.
- **No `except` clause in a shipped file holds a tuple literal.** Bind every exception
  tuple to a name (`READ_ERRORS`, `PARSE_ERRORS`). A formatter in someone else's repo
  rewrites the literal into a `SyntaxError` on an older interpreter.
- **`plugins/` is BUILT from `src/`, never edited.** `uv run python scripts/build_plugin.py`,
  and commit what it writes.
- **ASCII prose.** Write `--` for an em dash. No non-ASCII glyph in a shipped file.
- **No subjective claims in comments or commit messages** -- not "robust", "clean",
  "elegant". Write what is measured, what is enforced, or what was observed.
- **`clean` is a reserved word** -- one of the seven instructions. Never use it as a
  loose adjective.
- **Tests derive their inputs from the code.** Pages from `page_for`, binders from
  `bind`, edit_copies from `flows.marks.seed`, marks through `desk.mark.INSTRUCTIONS`.
  A literal appears only where malformed IS the input. `tests/helpers.py` already
  supplies `binder_of`, `a_small_real_tree`, `a_master_proof`, `a_correct`, `a_move`,
  `a_clean`, `a_query`, `an_add`, `a_drop`.
- **Every addition answers two questions before it is written** -- is it needed to make
  the system correct, and does it serve a purpose not already served
  (`docs/conventions.md`, *What every addition must answer*). Each task below carries a
  **Necessity** block for exactly this reason.

**Run after every task, before the commit:**

```bash
uv run pytest -q
uv run ruff check .
uv run ruff format .
uv run python scripts/check_shipped_syntax.py
uv run ty check src/comment_review/
```

---

## File Structure

| file | responsibility | task |
| --- | --- | --- |
| `src/comment_review/results/differences.py` | renders two texts against a base, **and now composes them** | 1, 7 |
| `src/comment_review/desk/collator.py` | source-verification, reconciliation, **and everything about the SET** | 1, 8, 9, 11 |
| `tests/gates/test_mark_shape.py` | the dataclasses carry exactly what `docs/the-mark.md` names | 2 |
| `docs/the-mark.md` | the mark's fields and classifiers -- the source the gate reads | 2, 3 |
| `src/comment_review/desk/mark.py` | ONE mark: its fields, its seed, its boundary parse | 3, 4, 5 |
| `src/comment_review/desk/containers.py` | **NEW** -- `Sheet`, `EditCopy`, `MasterProof` | 6 |
| `src/comment_review/flows/collate.py` | **NEW** -- one stage's copies folded into the chief's | 10, 11 |
| `src/comment_review/commands/collate.py` | **NEW** -- the console face of that flow | 12 |
| `src/comment_review/flows/distribute.py` | **RENAMED** from `flows/marks.py` -- hands a role its copy | 13 |
| `src/comment_review/commands/distribute.py` | **RENAMED** from `commands/mark.py` | 13 |

---

## Task 1: `P36` -- the false constraint, where it actually is

**Files:**
- Modify: `src/comment_review/results/differences.py:1-17`
- Read only: `src/comment_review/desk/collator.py:1-28`

**Interfaces:**
- Consumes: nothing.
- Produces: nothing. This task changes prose only.

**Necessity.** `Process: #53` rules that `Vocabulary: #11` names `collator.py` and
rules nothing else, and that a claim in a file is a claim to VERIFY, never a constraint to
obey. Task 7 adds a `compose` to `results/differences.py`, whose header today says the
module *"Rules on nothing"* and cites `#11` as the authority. **A compose ACTS.** Leaving
the sentence there means Task 7 lands a function the file's own first line denies.

!! **THE SPEC NAMES `desk/collator.py` AND THE CLAIM IS NO LONGER THERE.** Measured
2026-08-30: `collator.py`'s header was rewritten in `e4feba0` and carries no `#11`
citation. `grep -rn "Vocabulary: #11" src/` returns exactly one line, and it is
`results/differences.py:5`. **The target moved; the defect did not.**

- [x] **Step 1: Confirm where the claim is, before changing anything**

```bash
grep -rn "Vocabulary: #11" src/comment_review/
```

Expected: one line, `src/comment_review/results/differences.py:5`. If `collator.py` also
appears, fix both in Step 2 and say so in the commit.

- [x] **Step 2: Rewrite `results/differences.py`'s header**

Replace lines 1-17 with:

```python
"""Renders the difference between two texts, and composes them where they are disjoint.

One module, three operations over a base and its sides:

    unified(before, after, path)   the unified diff, one side against another
    diff3(base, sides)             the base with every edited span wrapped
    compose(base, sides)           the base with every side's edit applied,
                                   where no two sides touched one span

!! `diff3` RENDERS AND `compose` ACTS, and the pair is the reason both live here.
`diff3` wraps every span at least one side edited, even where only one side
touched it, so a person can read what each side did. `compose` acts on the
DISJOINTNESS that render only shows, and refuses where two sides met.

!! NO GIT PROCESS. A revise root is a temp copy `flows.revise.pull` made and
need not be a repo -- `difflib.unified_diff` reads two strings, not two
commits.

!! `diff3` IS N-WAY, NOT THREE-WAY. One mark per role per place, and the
all-concurrent topology dispatches four roles at once against one paragraph
-- base plus four sides is the normal case, not an edge one. `difflib` ships
no diff3 of its own; this builds the merge from `SequenceMatcher` opcodes,
base against each side.
"""
```

! **THE SENTENCE THAT GOES IS *"Neither decides settle or escalate; `decision-log.md
Vocabulary: #11` holds the collator to that same rule, and this module is held to it
too."*** `#11` rules that the copy chief is the one who rules on collated marks and that
the rename goes to `collator.py`. It says nothing about what any module may render, and
citing it as a boundary is what `#53` struck.

- [x] **Step 3: Verify the claim is gone and nothing else moved**

```bash
grep -rn "Vocabulary: #11" src/comment_review/
uv run pytest -q
```

Expected: the grep returns nothing; the suite passes unchanged.

- [x] **Step 4: Confirm `collator.py`'s remaining prose is checkable**

Read `src/comment_review/desk/collator.py:1-28` and check each claim against the code:

| the header says | check |
| --- | --- |
| "Nothing above `places` compares two marks" | no function before `places` takes two marks |
| "nothing below it opens a file" | `read_raw` is called only from `_lines`, above `places` |
| verification RETURNS, reconciliation RAISES | `verify_report` returns a list; `places` raises |

If any is false, correct it in the same commit and name it. If all hold, say so in the
commit -- **a check that was run and passed is worth recording, since the next reader
otherwise re-runs it.**

- [x] **Step 5: Commit**

```bash
git add src/comment_review/results/differences.py
git commit -F <message file>
```

Message names: `P36`'s target moved from `collator.py` (already rewritten in `e4feba0`)
to `differences.py:5`, and why it must precede Task 7.

---

## Task 2: The mark-shape gate reads its own counts

**Files:**
- Modify: `tests/gates/test_mark_shape.py`
- Modify: `docs/the-mark.md` (add the must-match statement in two places)

**Interfaces:**
- Consumes: nothing.
- Produces: a gate that accepts any field count `docs/the-mark.md`'s own heading states,
  so Task 3 adds a field without editing a test to let code through.

**Necessity.** Task 3 makes the mark's fields eight. The gate hard-codes three counts --
`^## The fields -- seven` in a regex, `assert len(names) == 7`, and `assert len(names) ==
11` -- so Task 3 would otherwise require bumping numbers in a test, which is
indistinguishable afterwards from a gate that never bit. Roy, 2026-08-30: *"Clear the
exact hard coded numbers and put in the file that they must match."*

! **THIS IS NOT A LANE CROSSING.** Roy, 2026-08-30: *"that gate is one you wrote for
yourself not systems writing it for you."* It is `backend`'s own check that `backend`'s
dataclass agrees with `backend`'s spec file.

! **AND THE GATE GETS STRONGER, NOT WEAKER.** Its own docstring says the expectation is
*"READ out of the spec here, never restated"*. The three integers are the last
restatements in it; after this the file contains no number that `docs/the-mark.md` does
not state.

- [x] **Step 1: Write the failing test**

Add to `tests/gates/test_mark_shape.py`:

```python
def test_no_count_in_this_file_restates_the_spec():
    """!! THE GATE MAY NOT CARRY A NUMBER THE SPEC STATES. Roy, 2026-08-30:
    "Clear the exact hard coded numbers and put in the file that they must
    match." A count typed here is one a field addition edits, and a gate
    edited to pass is indistinguishable afterwards from one that always
    passed."""
    source = (ROOT / "tests" / "gates" / "test_mark_shape.py").read_text(
        encoding="utf-8"
    )
    body = source.split("NUMBER = {", 1)[1].split("}", 1)[1]
    assert not re.search(r"==\s*\d+", body), (
        "a literal count survives outside NUMBER: "
        + str(re.findall(r".*==\s*\d+.*", body))
    )
```

- [x] **Step 2: Run it to verify it fails**

```bash
uv run pytest -q tests/gates/test_mark_shape.py::test_no_count_in_this_file_restates_the_spec
```

Expected: FAIL -- `NUMBER = {` is not in the file yet, raising `IndexError` on the split.
That is a legitimate red: the constant this test is written around does not exist.

- [x] **Step 3: Add the word-to-integer map and read every count from the spec**

Insert after the `SPEC = ...` line:

```python
#: The number words `docs/the-mark.md` states its own counts in. ! IT IS NOT A
#: COUNT -- it is the dictionary that turns the spec's word into an integer, so
#: no number below is a restatement of what the spec says. English has no
#: stdlib word-to-int, which is the whole reason this exists.
NUMBER = {
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "eleven": 11,
    "twelve": 12,
}
```

Replace the `_FIELDS_SECTION` block and `test_the_spec_states_SEVEN_fields` with:

```python
#: The heading's own stated count -- `## The fields -- eight`.
_FIELDS_HEADING = re.search(r"^## The fields -- (\w+)$", SPEC, re.MULTILINE)

#: The section stating the mark's own fields, up to the next `##` heading.
#: Scoped the same way `_SECTION` below is, so no other backtick-first-column
#: table in the file can be picked up.
_FIELDS_SECTION = re.search(
    r"^## The fields -- \w+.*?(?=^## )", SPEC, re.MULTILINE | re.DOTALL
).group()


def test_the_fields_table_holds_WHAT_ITS_OWN_HEADING_SAYS():
    """The heading states a number and the table under it must hold that
    many -- so a row added or lost is caught here rather than by the
    comparison below quietly agreeing with a shorter list.

    ! THE EXPECTATION IS THE SPEC'S OWN HEADING. Nothing in this file says
    how many fields a mark has."""
    stated = NUMBER[_FIELDS_HEADING.group(1)]
    names = _field_names()
    assert len(names) == stated, (stated, names)
```

Replace `allowed_names` and the `_FLAGS_BLOCK` regex:

```python
#: The classifiers heading's own stated column count, and the flags label's
#: own stated flag count -- `## The classifiers -- FOUR COLUMNS ...` and
#: `**The flags, and there are seven:**`.
_CLASSIFIER_HEADING = re.search(
    r"^## The classifiers -- (\w+) COLUMNS", SPEC, re.MULTILINE
)
_FLAGS_LABEL = re.search(r"\*\*The flags, and there are (\w+):\*\*", SPEC)


def allowed_names() -> set[str]:
    """The classifier and flag names the spec states, as field names.

    ! THE TOTAL IS READ OFF THE SPEC'S OWN TWO STATEMENTS -- the heading's
    column count plus the label's flag count -- so neither number is typed
    here."""
    names = _classifier_names() + _flag_names()
    stated = (
        NUMBER[_CLASSIFIER_HEADING.group(1).lower()] + NUMBER[_FLAGS_LABEL.group(1)]
    )
    assert len(names) == stated, (
        f"the spec states {stated} names, its tables hold: {names}"
    )
    return {FIELD_FOR[n] for n in names}
```

```python
_FLAGS_BLOCK = re.search(
    r"\*\*The flags, and there are \w+:\*\*\n\n(.*?)\n\n!!", SPEC, re.DOTALL
).group(1)
```

And rename `test_the_owes_table_names_the_same_seven_rows` to
`test_the_owes_table_names_the_same_rows` -- its body asserts
`set(OWES_TABLE) == set(INSTRUCTIONS)` and carries no number, so the count in the NAME is
the last restatement left.

- [x] **Step 4: State the must-match rule in `docs/the-mark.md`**

Directly under the fields table (after the `| \`change\` | ... |` row and its blank
line), add:

```markdown
!! **THE NUMBER IN THIS HEADING AND THE ROWS IN THIS TABLE MUST AGREE, AND A GATE READS
BOTH.** `tests/gates/test_mark_shape.py` takes the count from the heading's own word and
asserts the table holds that many, then asserts the dataclass carries exactly those names
in that order. **No count is typed in the test**, so adding a field means editing this
file and `desk/mark.py` together -- which is the only form of the check that cannot be
satisfied by editing the code alone.
```

And under `## The classifiers -- FOUR COLUMNS AND A CLOSED LIST OF FLAGS`, after the
flags block, add:

```markdown
!! **THE COLUMN COUNT IN THIS HEADING AND THE FLAG COUNT IN THE LABEL ABOVE ARE BOTH READ
BY THE GATE**, and their sum must equal the names these two tables state. Same rule as the
fields table: the numbers live here, never in the test.
```

- [x] **Step 5: Run the whole gate**

```bash
uv run pytest -q tests/gates/test_mark_shape.py
```

Expected: PASS, all tests, including
`test_no_count_in_this_file_restates_the_spec`.

- [x] **Step 6: Prove the generalised gate still bites**

By hand, in three moves:

1. Edit `docs/the-mark.md` line 30 from `## The fields -- seven` to
   `## The fields -- eight`, changing nothing else.
2. Run `uv run pytest -q tests/gates/test_mark_shape.py`. Confirm
   `test_the_fields_table_holds_WHAT_ITS_OWN_HEADING_SAYS` **FAILS**, reporting `8`
   against a list of seven names.
3. Put the heading back and confirm it passes again.

! Use `Edit`, not a shell rewrite. `CLAUDE.md`: no `sed`, no heredocs -- and a silent
half-rewrite of the spec file is exactly the failure that rule was written for.

! **THIS IS THE STEP THAT MAKES THE TASK WORTH ANYTHING.** `docs/gates.md`: *"does the
check pass" is not the question; "could the check fail" is.*

- [x] **Step 7: Commit**

```bash
git add tests/gates/test_mark_shape.py docs/the-mark.md
git commit -F <message file>
```

---

## Task 3: `P34` -- `raw_text` is the mark's eighth field

**Files:**
- Modify: `docs/the-mark.md:30-40`
- Modify: `src/comment_review/desk/mark.py:252-300` (the `Mark` dataclass), `:501-580` (`parse`)
- Test: `tests/test_mark.py`

**Interfaces:**
- Consumes: Task 2's gate, which now accepts eight.
- Produces: `Mark.raw_text: str`, third in field order, after `anchor` and before
  `instruction`. `parse` carries it through, defaulting to `""`.

**Necessity.** `raw_text` is written onto every slot by `seed` today
(`flows/marks.py:87`) and `docs/the-mark.md:53` says the seeded row carries it -- but
`parse` excludes it deliberately (`desk/mark.py:520-522`), so it does not come back. Two
things need it back:

1. **Task 4 (`P35`) builds the seeded row from the mark's own field names.** With
   `raw_text` outside the `Mark`, one of the three seeded fields stays a literal in
   another module -- which is the exact defect `P35` exists to remove.
2. **`Process: #54` makes *"did this parse back correctly"* the mark's own question.** A
   field that goes out and never comes back has no round trip at all.

! **IT IS NOT NEEDED FOR THE BASE, AND THE SPEC SAYS SO.** D10 rules that the compose and
the verbatim check take the base from the BINDER. The field on the mark is what came
BACK, and its only reader is Task 9's drift check.

- [x] **Step 1: Write the failing test**

Add to `tests/test_mark.py`:

```python
def test_the_mark_carries_the_raw_text_the_row_seeded():
    """`raw_text` is seeded onto every slot and must survive the round trip --
    `decision-log.md Process: #54` makes "did this parse back correctly" the
    mark's own question, and a field that never comes back has no round trip."""
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# the paragraph as it stands\n",
        "instruction": "clean",
    }
    mark, why = parse("m.py@b1", entry)
    assert why == []
    assert mark is not None
    assert mark.raw_text == "# the paragraph as it stands\n"


def test_a_mark_that_lost_its_raw_text_still_parses():
    """!! AN ABSENT `raw_text` IS NOT A SHAPE PROBLEM. It is seeded, so its
    absence is DRIFT -- a copy that did not come back with what it was handed
    -- and `decision-log.md` D10 of the SP-1 spec rules drift REPORTED, by the
    collator, never refused at the boundary. Refusing an absent field here
    while a CHANGED field is only reported would be two treatments of one
    problem."""
    mark, why = parse("m.py@b1", {"address": "m.py@b1", "instruction": "clean"})
    assert why == []
    assert mark is not None
    assert mark.raw_text == ""
```

- [x] **Step 2: Run them to verify they fail**

```bash
uv run pytest -q tests/test_mark.py -k raw_text
```

Expected: FAIL with `AttributeError: 'Mark' object has no attribute 'raw_text'`.

- [x] **Step 3: Add the row to `docs/the-mark.md`**

Change the heading on line 30:

```markdown
## The fields -- eight
```

Insert after the `anchor` row:

```markdown
| `raw_text` | the paragraph as it stands, verbatim -- what the role's `change` is a rewrite OF | **seeded** -- copied from the row |
```

! **THE `| the seeded row carries | ... |` MINI-TABLE FURTHER DOWN STAYS.** It names which
half of the diff pair is which, not the field list, and its first column is not
backticked so `_field_names()` does not read it.

- [x] **Step 4: Add the field to `Mark`**

In `src/comment_review/desk/mark.py`, delete the paragraph at lines 262-266 --

```
    ! NOTHING IS ADDED HERE THAT THE SPEC DOES NOT NAME. `raw_text` is the
    SEEDED ROW's, not the mark's -- `docs/the-mark.md` puts it on the row a
    role is handed, and `collator.claim_verbatim_problems` takes it as its own
    argument for that reason. `role` belongs to the `edit_copy` the mark came
    back in, and `collator.Placed` is what carries the pair.
```

-- and replace it with:

```
    ! `role` IS NOT A FIELD, and `collator.Placed` is what carries the pair. It
    belongs to the `edit_copy` a mark came back in, not to the mark.

    !! `raw_text` IS THE THIRD SEEDED FIELD AND WAS EXCLUDED UNTIL 2026-08-30.
    It went out on every slot and `parse` dropped it, so one of the three
    seeded fields could not be written from this class's own names -- which is
    what left a dict literal in `flows/marks.py` that a rename could not reach.
    ! WHAT COMES BACK IS NOT THE BASE. The binder's row is; a returned
    `raw_text` that differs from it is DRIFT, which `desk.collator.drift_in`
    reports.
```

Add the `raw_text` attribute doc after `anchor`'s:

```
        raw_text: the paragraph as it stands -- seeded, and what a role's
            `change` is a rewrite of. ! CARRIED, NEVER TRUSTED AS THE BASE:
            every check that measures a claim against the paragraph reads the
            BINDER's text, through `collator.base_texts`.
```

Add the field, third:

```python
    address: str
    anchor: str
    raw_text: str
    instruction: Instruction
    claim: dict
    reason: str
    sources: tuple[object, ...]
    change: str
```

- [x] **Step 5: Carry it through `parse`**

In `parse`'s `Args:` block, replace

```
        entry: one role's ruling on one place, as it came back. Keys the spec
            does not name (`raw_text`, seeded onto the row) are carried by the
            entry and are not part of the `Mark`.
```

with

```
        entry: one role's ruling on one place, as it came back. ! AN ABSENT
            `raw_text` IS NOT REFUSED -- it is seeded, so its absence is drift
            rather than a malformed shape, and `desk.collator.drift_in` is
            what rules on it. Refusing an absent field here while a CHANGED one
            is only reported would be two treatments of one problem.
```

Add the field to the construction, third, matching declaration order:

```python
        Mark(
            address=str(entry.get("address") or ""),
            anchor=str(entry.get("anchor") or ""),
            raw_text=str(entry.get("raw_text") or ""),
            instruction=instruction,
```

- [x] **Step 6: Run the tests**

```bash
uv run pytest -q tests/test_mark.py tests/gates/test_mark_shape.py
uv run pytest -q
```

Expected: PASS. The gate accepts eight because Task 2 made it read the heading.

- [x] **Step 7: Commit**

```bash
git add docs/the-mark.md src/comment_review/desk/mark.py tests/test_mark.py
git commit -F <message file>
```

---

## Task 4: `P35` -- `Mark.seed` builds the row from the mark's own names

**Files:**
- Modify: `src/comment_review/desk/mark.py` (add `SEEDED` and `Mark.seed`, `Mark.as_entry`)
- Modify: `src/comment_review/flows/marks.py:82-89`
- Test: `tests/test_mark.py`

**Interfaces:**
- Consumes: `Mark.raw_text` from Task 3.
- Produces:
  - `Mark.SEEDED: tuple[str, str, str]` -- `("address", "anchor", "raw_text")`
  - `Mark.seed(address: str, anchor: str, raw_text: str) -> dict`
  - `Mark.as_entry(self) -> dict`

**Necessity.** `flows/marks.py:82-89` writes four keys as literals in a module that does
not own the mark's shape, so renaming a `Mark` field leaves the flow writing the old key
and nothing notices. `Mark.seed` puts the write half where the read half already lives.

**`as_entry` is necessary for the same reason at the other end.** Task 10 writes marks
back onto the copy chief's `edit_copy`; building that dict by hand re-creates the exact
defect this task removes, one module further along.

- [x] **Step 1: Write the failing tests**

```python
def test_seed_builds_the_slot_from_the_marks_own_names():
    row = Mark.seed("m.py@b1", "def f(x):", "# as it stands\n")
    assert row == {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# as it stands\n",
        "instruction": None,
    }


def test_seed_refuses_a_name_the_mark_does_not_declare(monkeypatch):
    """!! THE POINT OF THE FUNCTION, AND THE ONLY WAY IT CAN FAIL. `P35` asks
    that a renamed field break AT CONSTRUCTION rather than leave another
    module writing the old key -- so `SEEDED` is checked against the
    dataclass's own fields every call, and this proves that check fires."""
    monkeypatch.setattr(Mark, "SEEDED", ("address", "anchor", "raw_txt"))
    with pytest.raises(AttributeError) as caught:
        Mark.seed("m.py@b1", "def f(x):", "# as it stands\n")
    assert "raw_txt" in str(caught.value)


def test_as_entry_round_trips_through_parse():
    """A mark written back onto a sheet parses as the mark it came from --
    which is what lets the copy chief's `edit_copy` be an ordinary one."""
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# as it stands\n",
        "instruction": "correct",
        "claim": {"false": "as it stands", "true": "as it should read"},
        "reason": "the paragraph names a parameter the signature dropped",
        "sources": [{"cite": "m.py:1", "verbatim": "def f(x):"}],
        "change": "# as it should read\n",
    }
    mark, why = parse("m.py@b1", entry)
    assert why == []
    assert mark is not None
    again, why_again = parse("m.py@b1", mark.as_entry())
    assert why_again == []
    assert again == mark
```

- [x] **Step 2: Run them to verify they fail**

```bash
uv run pytest -q tests/test_mark.py -k "seed or as_entry"
```

Expected: FAIL with `AttributeError: type object 'Mark' has no attribute 'seed'`.

- [x] **Step 3: Implement `SEEDED`, `seed` and `as_entry`**

Change the import at the top of `desk/mark.py`:

```python
from dataclasses import dataclass, fields
```

Add to the `Mark` class body, after the field declarations:

```python
    #: The fields SEEDED onto every slot before a role sees it -- written by
    #: `seed`, copied back unchanged, and read here by `parse`.
    #:
    #: ! NOT ANNOTATED, DELIBERATELY. `dataclasses.fields` sees only annotated
    #: names, so this stays a plain class attribute and
    #: `tests/gates/test_mark_shape.py` still compares exactly the eight the
    #: spec states.
    SEEDED = ("address", "anchor", "raw_text")

    @classmethod
    def seed(cls, address: str, anchor: str, raw_text: str) -> dict:
        """One fillable slot, keyed by this class's OWN field names.

        !! THE WRITE HALF OF THE ROUND TRIP LIVES WITH THE READ HALF, and did
        not until 2026-08-30. `flows/marks.py` wrote four keys as literals, so
        renaming a field here left that module writing the old key and nothing
        could notice -- `parse` would simply find the field absent.

        Args:
            address: `path@cue`, composed by `reading.addresser.address_for`.
            anchor: the line of code the place sits on, or "".
            raw_text: the paragraph as it stands.

        Returns:
            `{address, anchor, raw_text, instruction: None}` -- the slot as a
            role receives it. `instruction: None` is what `untouched` reads to
            say nobody has written here.

        Raises:
            AttributeError: `SEEDED` names something `Mark` does not declare.
                ! THIS IS THE WHOLE GUARD. A rename breaks HERE, loudly, at the
                point the row is built, rather than silently one module away.
        """
        declared = {f.name for f in fields(cls)}
        row: dict = {}
        for name, value in zip(cls.SEEDED, (address, anchor, raw_text), strict=True):
            if name not in declared:
                raise AttributeError(
                    f"Mark.seed writes `{name}`, which Mark does not declare"
                )
            row[name] = value
        row["instruction"] = None
        return row

    def as_entry(self) -> dict:
        """This mark as the wire entry a sheet carries -- its OWN field names.

        ! THE COUNTERPART OF `seed`, AND IT EXISTS FOR THE SAME REASON. A
        caller writing a mark back onto a sheet by hand re-creates the literal
        `seed` removed, one module further along -- which is what the copy
        chief's `edit_copy` would otherwise be built from.

        Returns:
            A dict `parse` accepts and returns an equal `Mark` from.
            `instruction` is written as its string value, since that is what
            the wire carries and what `parse` reads.
        """
        entry = {f.name: getattr(self, f.name) for f in fields(self)}
        entry["instruction"] = str(self.instruction)
        entry["claim"] = dict(self.claim)
        entry["sources"] = list(self.sources)
        return entry
```

- [x] **Step 4: Point `flows/marks.py` at it**

Replace the mark-building literal at `src/comment_review/flows/marks.py:81-90`:

```python
                "marks": [
                    Mark.seed(
                        address_for(
                            str(page.get("path", "")), str(row.get("cue", ""))
                        ),
                        str(row.get("anchor", "")),
                        str(row.get("raw_text", "")),
                    )
                    for row in page.get("rows", [])
                ],
```

Change the import line to bring in `Mark`:

```python
from comment_review.desk.mark import INSTRUCTIONS, Instruction, Mark, parse, untouched
```

Update `seed`'s own docstring `Returns:` so it names where the slot's shape comes from:

```
            `instruction: None` for the role to fill. ! THE SLOT IS BUILT BY
            `desk.mark.Mark.seed`, from the mark's own field names, so a
            renamed field breaks there rather than leaving this module writing
            the old key.
```

- [x] **Step 5: Run the tests**

```bash
uv run pytest -q tests/test_mark.py tests/test_marks_flow.py
uv run pytest -q
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add src/comment_review/desk/mark.py src/comment_review/flows/marks.py tests/test_mark.py
git commit -F <message file>
```

---

## Task 5: `D9` -- `parse` refuses a `move` onto its own address

**Files:**
- Modify: `src/comment_review/desk/mark.py` (add `_destination_problems`, call it in `parse`)
- Test: `tests/test_mark.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `parse` returns a named problem for a `move` whose `claim.to` equals its
  `address`.

**Closes:** `TODO/collator-defects.md` T1 and T2.

**Necessity.** MEASURED 2026-08-30 by running it: a `move` from `m.py@b1` to `m.py@b1`
parses with no problems reported, `collator._touches` dedupes both ends to one address, `reconcile` SETTLES
it, and `docket_from` emits one alteration -- `('m.py', 'b1', None)`. **The paragraph is
deleted and never written back.** It is the half-move `_join_moves` exists to prevent,
arriving through the one shape it cannot see: `ends_of` filters
`len(_touches(...)) > 1`.

It also wires `owes_destination`, **declared at `desk/mark.py:206` and read by nothing** --
`grep -rn "owes_destination" src/` returns three lines, all in the file that declares it.

! **ONLY THE SELF-MOVE HALF.** Whether `claim.to` names an ADDRESSABLE place (Roy,
2026-08-27) needs an addresser, which `desk/mark.py` imports nothing of -- it stays
`collator-defects` T3, beside `P28` in SP-2.

- [x] **Step 1: Write the failing test**

```python
def test_a_move_onto_its_own_address_is_refused_by_name():
    """MEASURED 2026-08-30: this parsed with no problems reported, `_touches`
    deduped its two ends
    to one address, `reconcile` settled it, and the docket carried a single
    alteration deleting the paragraph -- `('m.py', 'b1', None)` -- with no
    matching write."""
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# a paragraph\n",
        "instruction": "move",
        "claim": {"from": "a paragraph", "to": "m.py@b1"},
        "reason": "it reads better beside the function it describes",
        "sources": [{"cite": "m.py:1", "verbatim": "def f(x):"}],
        "change": "# a paragraph\n",
    }
    mark, why = parse("m.py@b1", entry)
    assert mark is None
    assert len(why) == 1
    assert "`claim.to` is this mark's own `address`" in why[0]


def test_a_move_to_a_different_address_still_parses():
    """The guard must not refuse an ordinary move -- the one that names a real
    second place."""
    entry = {
        "address": "m.py@b1",
        "anchor": "def f(x):",
        "raw_text": "# a paragraph\n",
        "instruction": "move",
        "claim": {"from": "a paragraph", "to": "m.py@b8"},
        "reason": "it reads better beside the function it describes",
        "sources": [{"cite": "m.py:1", "verbatim": "def f(x):"}],
        "change": "# a paragraph\n",
    }
    mark, why = parse("m.py@b1", entry)
    assert why == []
    assert mark is not None
```

- [x] **Step 2: Run them to verify the first fails**

```bash
uv run pytest -q tests/test_mark.py -k move_onto_its_own
```

Expected: FAIL -- `assert mark is None` fails, because `parse` returns a mark and no
problems for it today.

- [x] **Step 3: Implement the check**

Add above `parse` in `desk/mark.py`:

```python
def _destination_problems(where: str, address: object, claim: object) -> list[str]:
    """WHERE a `move` sends the paragraph, checked against where it already IS.

    !! A DESTINATION EQUAL TO THE ORIGIN IS REFUSED, and it is the half of
    `owes_destination` one mark can answer alone. MEASURED 2026-08-30: such a
    mark parsed with no problems reported, `collator._touches` deduped its two
    ends to one address,
    and `docket_from` wrote the delete at the origin with no matching write --
    the paragraph removed and never put back.

    ! THE OTHER HALF IS NOT ASKED HERE. Whether the destination is ADDRESSABLE
    (Roy, 2026-08-27) needs an addresser, and this module imports `re`,
    `dataclasses` and `enum` and nothing else.

    Args:
        where: how to name this mark in a message.
        address: the mark's own `address`, as the entry carried it.
        claim: the mark's `claim`, as the entry carried it.

    Returns:
        One message, or an empty list. A claim that is not an object, or a
        `to` that is not a filled string, says nothing here -- `_claim_problems`
        is what refuses those, and this step has nothing to compare.
    """
    if not isinstance(claim, dict) or not isinstance(address, str):
        return []
    destination = claim.get("to")
    if not isinstance(destination, str):
        return []
    if destination.strip() and destination.strip() == address.strip():
        return [
            f"{where}: `claim.to` is this mark's own `address` -- a move to "
            "where the paragraph already is deletes it and writes nothing back"
        ]
    return []
```

In `parse`, after the `_claim_problems` line:

```python
    out += _claim_problems(where, instruction, entry.get("claim"))
    if spec.owes_destination:
        out += _destination_problems(where, entry.get("address"), entry.get("claim"))
```

Update `parse`'s own "what is NOT checked here" note, which currently claims the
destination is entirely the collator's:

```
    ! What is NOT checked here, because it needs the page the role read: whether
    the address resolves, and whether a quoted sentence is really in the
    paragraph. Those belong to SOURCE-VERIFICATION, in `collator`. ! A `move`'s
    destination is HALF here: that it is not the origin is answerable from the
    entry alone; that it is ADDRESSABLE is not.
```

- [x] **Step 4: Run the tests**

```bash
uv run pytest -q tests/test_mark.py
uv run pytest -q
```

Expected: PASS.

- [x] **Step 5: Confirm the measured docket shape is now unreachable**

```bash
uv run pytest -q tests/test_collator.py tests/test_docket.py
```

Expected: PASS. If any test built a self-move as an input, it now refuses at `parse` --
fix the test to use a real destination, and say so in the commit.

- [x] **Step 6: Close the TODO tasks**

```bash
uv run python scripts/todo_tool.py check collator-defects 1
uv run python scripts/todo_tool.py check collator-defects 2
```

! **DO NOT TOUCH `TODO/move-onto-itself-deletes.md`.** It holds the same two tasks and is
one of four single-defect files `collator-defects` carries a standing note about: they
stand until the board migration and are superseded into it **in one pass** -- Roy,
2026-08-30, *"Do not close them by hand."*

- [x] **Step 7: Commit**

```bash
git add src/comment_review/desk/mark.py tests/test_mark.py TODO/
git commit -F <message file>
```

---

## Task 6: `P21` -- `desk/containers.py`

**Files:**
- Create: `src/comment_review/desk/containers.py`
- Test: `tests/test_containers.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `Sheet(path: str, sha: str, marks: tuple[object, ...])`
  - `EditCopy(role: str, read_from: dict, sheets: tuple[Sheet, ...])`
  - `MasterProof(stage: str, read_from: dict, edit_copies: tuple[EditCopy, ...])`
  - `parse_sheet(where, data) -> tuple[Sheet | None, list[str]]`
  - `parse_edit_copy(where, data) -> tuple[EditCopy | None, list[str]]`
  - `parse_master_proof(where, data) -> tuple[MasterProof | None, list[str]]`

**Necessity.** The containers' shape is code-only today, split between
`flows/marks.py:36` and `desk/proof.py:40`, and every consumer re-derives the same keys
with `isinstance` ladders -- `collator.py` alone does it in `verify_report`, `places`,
`_roles_of_stage` and `_real_pages`. `Vocabulary: #30` rules the type IS the definition,
because **no agent ever authors a container**.

! **NO `rounds` FIELD.** `Vocabulary: #30` proposed one; `P7` is superseded by
`Process: #51`, which struck carried round state as guarding an accident that cannot
happen -- nothing advances a round but a command someone invokes. A field nothing reads is
what let `Instruction` be an enum the wire never carried.

! **`marks` IS TYPED `tuple[object, ...]`, ON PURPOSE**, the same as `Mark.sources`. An
entry that is not an object must be CARRIED so `desk.mark.parse` can refuse it by name; a
container that filtered to dicts would make a bare string vanish instead of being flagged.

- [x] **Step 1: Write the failing test**

Create `tests/test_containers.py`:

```python
"""The containers parse what the real chain builds, and refuse what it cannot.

! INPUTS ARE REAL -- a binder from `bind` over a real tree, seeded by the real
`seed`, gathered by the real `gather`. A literal appears only where MALFORMED
is the input, which is what the refusals are about.
"""

import pytest
from helpers import a_small_real_tree, binder_of

from comment_review.desk.containers import (
    EditCopy,
    MasterProof,
    Sheet,
    parse_edit_copy,
    parse_master_proof,
    parse_sheet,
)
from comment_review.desk.proof import gather
from comment_review.flows.marks import seed


def a_real_copy(tmp_path, role="block-context"):
    return seed(binder_of(a_small_real_tree(tmp_path), 0), role)


class TestWhatTheChainBuilds:
    def test_an_edit_copy_seed_built_parses(self, tmp_path):
        copy, why = parse_edit_copy("copy 1", a_real_copy(tmp_path))
        assert why == []
        assert isinstance(copy, EditCopy)
        assert copy.role == "block-context"
        assert copy.sheets
        assert all(isinstance(s, Sheet) for s in copy.sheets)

    def test_every_sheet_names_a_page_the_binder_carried(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy, why = parse_edit_copy("copy 1", seed(binder, "block-context"))
        assert why == []
        assert copy is not None
        carried = {p["path"] for p in binder["pages"]}
        assert {s.path for s in copy.sheets} == carried

    def test_a_master_proof_gather_built_parses(self, tmp_path):
        copies = [
            a_real_copy(tmp_path, "block-context"),
            a_real_copy(tmp_path, "function-context"),
        ]
        proof, why = parse_master_proof("4c", gather("4c", copies))
        assert why == []
        assert isinstance(proof, MasterProof)
        assert proof.stage == "4c"
        assert [c.role for c in proof.edit_copies] == [
            "block-context",
            "function-context",
        ]

    def test_the_chiefs_copy_parses_as_an_ORDINARY_edit_copy(self, tmp_path):
        """`decision-log.md Vocabulary: #30`: the chief's copy is the same
        shape. There is no second type and no second parse."""
        copy = a_real_copy(tmp_path)
        copy["role"] = "copy-chief"
        got, why = parse_edit_copy("the chief's", copy)
        assert why == []
        assert got is not None
        assert got.role == "copy-chief"


class TestWhatItRefuses:
    def test_a_sheet_that_is_not_an_object(self):
        sheet, why = parse_sheet("sheet 1", "m.py")
        assert sheet is None
        assert "must be an object" in why[0]

    def test_a_sheet_with_no_path(self):
        sheet, why = parse_sheet("sheet 1", {"sha": "abc", "marks": []})
        assert sheet is None
        assert "`path`" in why[0]

    def test_a_sheet_whose_marks_are_not_a_list(self):
        sheet, why = parse_sheet("sheet 1", {"path": "m.py", "marks": {}})
        assert sheet is None
        assert "`marks` list" in why[0]

    def test_an_edit_copy_with_no_role(self, tmp_path):
        copy = a_real_copy(tmp_path)
        del copy["role"]
        got, why = parse_edit_copy("copy 1", copy)
        assert got is None
        assert "`role`" in why[0]

    def test_an_edit_copy_with_an_emptied_read_from(self, tmp_path):
        """`decision-log.md Process: #34`: the field exists so a later role can
        know it holds a REVISE. An empty one is the ambiguity it was added to
        remove."""
        copy = a_real_copy(tmp_path)
        copy["read_from"] = {}
        got, why = parse_edit_copy("copy 1", copy)
        assert got is None
        assert "read_from" in why[0]

    def test_an_edit_copy_reports_EVERY_bad_sheet_not_just_the_first(self, tmp_path):
        copy = a_real_copy(tmp_path)
        copy["sheets"] = [{"sha": "a"}, {"sha": "b"}]
        got, why = parse_edit_copy("copy 1", copy)
        assert got is None
        assert len(why) == 2

    def test_a_master_proof_whose_edit_copies_are_not_a_list(self):
        proof, why = parse_master_proof("4c", {"stage": "4c", "edit_copies": {}})
        assert proof is None
        assert "`edit_copies` list" in why[0]


class TestTheShape:
    def test_no_container_declares_a_field_nothing_reads(self):
        """!! `P21`'s own verify. `decision-log.md Vocabulary: #30` proposed a
        `rounds` field; `P7` is SUPERSEDED by `Process: #51`, which struck
        carried round state as guarding an accident that cannot happen. A field
        nothing reads is what let `Instruction` be an enum the wire never
        carried."""
        import dataclasses

        for kind in (Sheet, EditCopy, MasterProof):
            names = {f.name for f in dataclasses.fields(kind)}
            assert "rounds" not in names, kind.__name__
```

- [x] **Step 2: Run it to verify it fails**

```bash
uv run pytest -q tests/test_containers.py
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'comment_review.desk.containers'`.

- [x] **Step 3: Implement the module**

Create `src/comment_review/desk/containers.py`:

```python
"""The containers a mark travels in -- the sheet, the edit_copy, the master_proof.

    Sheet              one PAGE's marks, with that page's path and sha
    EditCopy           one ROLE's sheets, with the binder it was seeded from
    MasterProof        one STAGE's edit_copies
    parse_sheet()      the boundary parse for one sheet
    parse_edit_copy()  for one edit_copy, and every sheet under it
    parse_master_proof()  for one master_proof, and every copy under it

!! THE TYPE IS THE DEFINITION AND THERE IS NO MARKDOWN SOURCE, ruled
`decision-log.md Vocabulary: #30`. `docs/the-mark.md` exists because an agent
AUTHORS a mark, so a mark's shape must be published to a role. No agent ever
authors a container -- `flows.marks.seed`, `flows.fan_out.fan` and
`desk.proof.gather` build them -- so the type is where the shape lives, the way
`desk/mark.py` defines `Mark`.

!! THE WIRE STAYS DICTS. Each parse has `desk.mark.parse`'s own contract --
`(T, [])` or `(None, [one message per broken rule])` -- so a caller holds a
checked object and consumers stop re-deriving the same keys with `isinstance`
ladders. `desk/collator.py` alone did that in four functions.

! THE CHIEF'S COPY IS AN ORDINARY `EditCopy`. `Vocabulary: #30`: after the fold
every place has exactly one answer, and one mark per place is an ordinary copy.
There is no second shape and no second parse.

! `marks` IS TYPED `tuple[object, ...]`, matching `Mark.sources` and for the
same reason: an entry that is not an object is CARRIED so `desk.mark.parse` can
refuse it by name. Filtering to dicts here would make a bare string vanish
instead of being flagged.
"""

from dataclasses import dataclass

from comment_review.binder.binder import _read_from_problem


@dataclass(frozen=True)
class Sheet:
    """One page's marks, inside the `edit_copy` that seeded them.

    Attributes:
        path: the page's real repo path, as the binder stated it.
        sha: that page's sha when it was censused. Read by `docket_from`, which
            writes it onto the docket page so the setter can refuse a page that
            moved underneath the run.
        marks: one entry per place on the page, as they came back.
    """

    path: str
    sha: str
    marks: tuple[object, ...]


@dataclass(frozen=True)
class EditCopy:
    """One role's copy of the binder -- what goes out, and what comes back.

    Attributes:
        role: the editorial role that filled it, or `copy-chief` for the fold's
            result. It is what an outcome is decided from and what a place is
            sent back to.
        read_from: `{root, revise}` -- which tree this copy was censused from.
            `decision-log.md Process: #34`: the field exists so a later role can
            know it holds a REVISE and not the original.
        sheets: one per page.
    """

    role: str
    read_from: dict
    sheets: tuple[Sheet, ...]


@dataclass(frozen=True)
class MasterProof:
    """Every `edit_copy` of one stage, gathered.

    Attributes:
        stage: the label the copies were dispatched under -- `SKILL.md`'s "4a",
            "4c".
        read_from: taken from the first copy; `desk.proof.gather` refuses a set
            that disagrees.
        edit_copies: one per role, or one per SHARD under fan-out.
    """

    stage: str
    read_from: dict
    edit_copies: tuple[EditCopy, ...]


def parse_sheet(where: str, data: object) -> tuple[Sheet | None, list[str]]:
    """One sheet, checked.

    Args:
        where: how to name this sheet in a message.
        data: one entry of an edit_copy's `sheets`, as it came back.

    Returns:
        `(Sheet, [])` or `(None, [messages])`. An absent `sha` is admitted as
        "" -- a page can be censused from a tree that is not a repo, which is
        what `flows.revise.pull` produces.
    """
    if not isinstance(data, dict):
        return None, [f"{where}: a sheet must be an object"]
    path = data.get("path")
    if not isinstance(path, str) or not path.strip():
        return None, [f"{where}: a sheet needs the `path` of the page it holds"]
    marks = data.get("marks")
    if not isinstance(marks, list):
        return None, [f"{where}: {path} needs a `marks` list"]
    return Sheet(path=path, sha=str(data.get("sha", "")), marks=tuple(marks)), []


def parse_edit_copy(where: str, data: object) -> tuple[EditCopy | None, list[str]]:
    """One edit_copy and every sheet under it, checked.

    ! EVERY BAD SHEET IS REPORTED, not the first. A copy handed back with two
    malformed sheets is two things to fix, and a parse that stopped at the
    first would make the second invisible until the next run.

    Args:
        where: how to name this copy in a message.
        data: one edit_copy, as `flows.marks.seed` builds one.

    Returns:
        `(EditCopy, [])` or `(None, [messages])`.
    """
    if not isinstance(data, dict):
        return None, [f"{where}: an edit_copy must be an object"]
    role = data.get("role")
    if not isinstance(role, str) or not role.strip():
        return None, [f"{where}: an edit_copy needs the `role` that wrote it"]
    why_header = _read_from_problem(data)
    if why_header:
        return None, [f"{where}: {role}'s {why_header}"]
    raw_sheets = data.get("sheets")
    if not isinstance(raw_sheets, list):
        return None, [f"{where}: {role} needs a `sheets` list"]
    sheets: list[Sheet] = []
    problems: list[str] = []
    for i, raw in enumerate(raw_sheets, 1):
        sheet, why = parse_sheet(f"{where}: {role} sheet {i}", raw)
        if sheet is None:
            problems += why
        else:
            sheets.append(sheet)
    if problems:
        return None, problems
    return (
        EditCopy(
            role=role,
            # ! COPIED, NOT ALIASED -- `bind`, `seed` and `gather` all do the
            # same with this field, so a caller mutating its own dict cannot
            # change what a parsed copy already holds.
            read_from={**data["read_from"]},
            sheets=tuple(sheets),
        ),
        [],
    )


def parse_master_proof(
    where: str, data: object
) -> tuple[MasterProof | None, list[str]]:
    """One master_proof and every copy under it, checked.

    Args:
        where: how to name this proof in a message -- its stage label.
        data: a master_proof, as `desk.proof.gather` returns one.

    Returns:
        `(MasterProof, [])` or `(None, [messages])`. Every bad copy is reported.
    """
    if not isinstance(data, dict):
        return None, [f"{where}: a master_proof must be an object"]
    raw_copies = data.get("edit_copies")
    if not isinstance(raw_copies, list):
        return None, [f"{where}: a master_proof needs an `edit_copies` list"]
    copies: list[EditCopy] = []
    problems: list[str] = []
    for i, raw in enumerate(raw_copies, 1):
        copy, why = parse_edit_copy(f"{where}: edit_copy {i}", raw)
        if copy is None:
            problems += why
        else:
            copies.append(copy)
    if problems:
        return None, problems
    read_from = data.get("read_from")
    return (
        MasterProof(
            stage=str(data.get("stage", "")),
            read_from={**read_from} if isinstance(read_from, dict) else {},
            edit_copies=tuple(copies),
        ),
        [],
    )
```

- [x] **Step 4: Run the tests**

```bash
uv run pytest -q tests/test_containers.py
uv run pytest -q
```

Expected: PASS.

- [x] **Step 5: Commit**

```bash
git add src/comment_review/desk/containers.py tests/test_containers.py
git commit -F <message file>
```

---

## Task 7: `P13` -- the COMPOSE

**Files:**
- Modify: `src/comment_review/results/differences.py`
- Test: `tests/test_differences.py`

**Interfaces:**
- Consumes: Task 1's rewritten header.
- Produces:
  - `CannotCompose(Exception)`
  - `compose(base: str, sides: dict[str, str]) -> str`

**Necessity.** `P13` answers *"how do both get taken in"* -- Roy's own question -- and it
needs no fifth answer, because `hold` already says *my mark stands*, so two holds on
disjoint spans are saying it and the composition is arithmetic.

! **`diff3` DOES NOT DO THIS.** It RENDERS -- every span at least one side edited wrapped
in a conflict span, **even where only one side touched it**. A compose ACTS on the
disjointness that render only shows.

! **IT LIVES HERE AND NOT IN THE COLLATOR.** It is arithmetic over text using
`_conflict_spans`, `_touching_roles` and `_side_slice`, which already exist in this file
and are already correct about the hard case (an `insert` at a span boundary, measured
2026-08-29). `Process: #53`: *"Making the design fit to `collator.py` is not the way."*

- [x] **Step 1: Write the failing tests**

Add to `tests/test_differences.py`:

```python
class TestCompose:
    def test_two_edits_on_different_lines_merge(self):
        base = "# one\n# two\n# three\n"
        sides = {
            "block-context": "# ONE\n# two\n# three\n",
            "function-context": "# one\n# two\n# THREE\n",
        }
        assert compose(base, sides) == "# ONE\n# two\n# THREE\n"

    def test_two_edits_on_one_line_refuse_by_name(self):
        base = "# one\n# two\n"
        sides = {
            "block-context": "# ONE\n# two\n",
            "function-context": "# uno\n# two\n",
        }
        with pytest.raises(CannotCompose) as caught:
            compose(base, sides)
        message = str(caught.value)
        assert "block-context" in message
        assert "function-context" in message

    def test_one_side_composes_to_that_side(self):
        base = "# one\n# two\n"
        sides = {"block-context": "# ONE\n# two\n"}
        assert compose(base, sides) == "# ONE\n# two\n"

    def test_no_side_composes_to_the_base(self):
        base = "# one\n# two\n"
        assert compose(base, {}) == base

    def test_a_side_that_changed_nothing_does_not_claim_a_span(self):
        """A role that edited nothing is not a party to any span, so another
        role's lone edit still composes."""
        base = "# one\n# two\n"
        sides = {
            "block-context": "# ONE\n# two\n",
            "function-context": "# one\n# two\n",
        }
        assert compose(base, sides) == "# ONE\n# two\n"

    def test_a_pure_insert_is_carried(self):
        """!! THE SHAPE THAT WAS MEASURED LOST ONCE. An `insert` opcode has
        `i1 == i2`, and a half-open overlap test is False for every empty base
        range -- which dropped every pure insert from `diff3`'s render on
        2026-08-29. `_side_slice` uses the closed test; this proves `compose`
        inherits it."""
        base = "# a\n# b\n"
        sides = {"block-context": "# a\n# INSERTED\n# b\n"}
        assert compose(base, sides) == "# a\n# INSERTED\n# b\n"

    def test_an_insert_and_a_distant_edit_compose(self):
        base = "# a\n# b\n# c\n# d\n"
        sides = {
            "block-context": "# a\n# INSERTED\n# b\n# c\n# d\n",
            "function-context": "# a\n# b\n# c\n# D\n",
        }
        assert compose(base, sides) == "# a\n# INSERTED\n# b\n# c\n# D\n"
```

Add `CannotCompose` and `compose` to the module's import line in the test file, and
`import pytest` if it is not already there.

- [x] **Step 2: Run them to verify they fail**

```bash
uv run pytest -q tests/test_differences.py -k Compose
```

Expected: FAIL with `ImportError: cannot import name 'compose'`.

- [x] **Step 3: Implement `compose`**

Add to `src/comment_review/results/differences.py`, after `diff3`:

```python
class CannotCompose(Exception):
    """Two or more sides edited one span of the base, so no composition exists.

    !! RAISED, NOT RETURNED AS A SENTINEL, so a caller cannot mistake a refusal
    for text. A composed paragraph and "no composition" are different kinds of
    answer, and an empty string is a legal paragraph -- `drop`'s.

    ! IT NAMES THE SPAN AND THE SIDES. A refusal a caller can only report as
    "it did not work" cannot be sent back to anybody, which is what
    `decision-log.md Process: #51` asks of every step that leaves work undone.
    """


def compose(base: str, sides: dict[str, str]) -> str:
    """The base with every side's edit applied, where no two sides met.

    !! THIS IS THE ARITHMETIC HALF OF `diff3`, and the pair is why both live
    here. `diff3` wraps every span at least one side edited, EVEN WHERE ONLY ONE
    SIDE TOUCHED IT, because its job is to show a person what each side did.
    This applies exactly those single-side spans and refuses the rest.

    ! A SIDE THAT CHANGED NOTHING AT A SPAN IS NOT A PARTY TO IT.
    `_touching_roles` returns only the roles with a non-`equal` opcode there, so
    three roles of which one edited compose to that one's text.

    Args:
        base: the paragraph before any of these edits -- the BINDER's
            `raw_text`, never a returned mark's. `desk.collator.base_texts` is
            what supplies it; see the SP-1 spec's D10 for why.
        sides: role name -> that role's proposed `change`, both whole
            paragraphs as raw text (`decision-log.md Vocabulary: #27`).

    Returns:
        The composed paragraph. An empty `sides` returns `base` unchanged --
        nothing was proposed, so nothing is applied.

    Raises:
        CannotCompose: some span was edited by two or more sides, naming the
            base lines and every side that touched them.
    """
    base_lines = base.splitlines(True)
    roles = sorted(sides)
    sides_lines = {role: sides[role].splitlines(True) for role in roles}
    opcodes: dict[str, list[_Opcode]] = {
        role: difflib.SequenceMatcher(None, base_lines, sides_lines[role]).get_opcodes()
        for role in roles
    }

    out: list[str] = []
    at = 0
    for start, end in _conflict_spans(opcodes, roles):
        touching = _touching_roles(opcodes, roles, start, end)
        if len(touching) != 1:
            raise CannotCompose(
                f"base lines {start + 1}-{end} were edited by "
                f"{', '.join(touching)} -- no composition"
            )
        out.extend(base_lines[at:start])
        role = touching[0]
        out.extend(
            _side_slice(base_lines, sides_lines[role], opcodes[role], start, end)
        )
        at = end
    out.extend(base_lines[at:])
    return "".join(out)
```

- [x] **Step 4: Run the tests**

```bash
uv run pytest -q tests/test_differences.py
uv run pytest -q
```

Expected: PASS.

- [x] **Step 5: Prove the test can disagree with the implementation**

!! **THIS STEP IS THE ONE `docs/gates.md` REQUIRES OF THIS TASK.** `compose` is built from
the same opcode machinery that produced the texts it merges, so a test asserting the
result equals one side's own edit **cannot disagree with itself**. Every expectation above
is prose typed into the test, which is what makes it able to fail. Prove it:

Temporarily change `out.extend(base_lines[at:start])` to `out.extend([])` and run:

```bash
uv run pytest -q tests/test_differences.py -k Compose
```

Expected: `test_two_edits_on_different_lines_merge` and
`test_an_insert_and_a_distant_edit_compose` FAIL. Restore the line and confirm they pass.
Record the result in the commit message.

- [x] **Step 6: Commit**

```bash
git add src/comment_review/results/differences.py tests/test_differences.py
git commit -F <message file>
```

---

## Task 8: `P24` and `D5` -- the shape verbs move, and the problems stack

**Files:**
- Modify: `src/comment_review/desk/collator.py` (add `Problem`; receive `unruled`,
  `problems_in`, `tally`)
- Modify: `src/comment_review/flows/marks.py` (remove the three)
- Modify: `src/comment_review/commands/mark.py` (imports)
- Test: `tests/test_collator.py`, `tests/test_marks_flow.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `Problem(role: str, address: str, message: str)` in `desk/collator.py`
  - `problems_in(report: dict) -> tuple[list[Problem], int]`
  - `unruled(report: dict) -> list[str]`
  - `tally(report: dict) -> dict[str, int]`

**Necessity.** `Process: #54`: *"A mark problem is did this parse back correctly does it
still contain the correct stuff."* Coverage is not that -- *did every place get ruled on*
is a question about the SET, and the three verbs ask it from a flow's address. All three
are called only by `commands/mark.py`.

**And `Problem` is necessary for routing.** Roy, 2026-08-30: *"the errors should be
stacked and capable of being read off correctly so that each can be fixed or sent back to
the role."* `desk.mark.parse` returns flat sentences each opening with a `where`, and
**nobody can route on a sentence** -- so the role and the address ride beside the message.

! **NO `kind` FIELD.** The three questions stay three lists (`problems`, `drift`,
`unruled`); a `kind` would say which list a thing is already in, which is the two
spellings of one rule this repo has measured drifting apart.

- [x] **Step 1: Write the failing tests**

Add to `tests/test_collator.py`:

```python
class TestProblemsAreRoutable:
    def test_a_problem_names_the_role_and_the_address(self, tmp_path):
        """Roy, 2026-08-30: "the errors should be stacked and capable of being
        read off correctly so that each can be fixed or sent back to the role."
        A sentence cannot be routed; a role and an address can."""
        copy = seed(binder_of(a_small_real_tree(tmp_path), 0), "block-context")
        entry = copy["sheets"][0]["marks"][0]
        entry.update({"instruction": "correct", "claim": {}})
        problems, ruled = problems_in(copy)
        assert ruled == 1
        assert problems
        assert all(p.role == "block-context" for p in problems)
        assert all(p.address == entry["address"] for p in problems)
        assert all(isinstance(p.message, str) and p.message for p in problems)

    def test_every_broken_mark_is_reported_not_only_the_first(self, tmp_path):
        copy = seed(binder_of(a_small_real_tree(tmp_path), 0), "block-context")
        marks = copy["sheets"][0]["marks"]
        assert len(marks) >= 2, "this tree needs two places on its first page"
        for entry in marks[:2]:
            entry.update({"instruction": "correct", "claim": {}})
        problems, ruled = problems_in(copy)
        assert ruled == 2
        assert len({p.address for p in problems}) == 2

    def test_a_copy_level_problem_carries_an_empty_address(self, tmp_path):
        copy = seed(binder_of(a_small_real_tree(tmp_path), 0), "block-context")
        del copy["role"]
        problems, _ = problems_in(copy)
        assert any(p.address == "" and "`role`" in p.message for p in problems)
```

- [x] **Step 2: Run them to verify they fail**

```bash
uv run pytest -q tests/test_collator.py -k Routable
```

Expected: FAIL with `ImportError: cannot import name 'problems_in' from
'comment_review.desk.collator'`.

- [x] **Step 3: Move the three verbs and add `Problem`**

Cut `problems_in`, `unruled` and `tally` from `src/comment_review/flows/marks.py`
(lines 98-205) and paste them into `src/comment_review/desk/collator.py`, after
`verify_report`. Add above them:

```python
@dataclass(frozen=True)
class Problem:
    """One thing wrong with one mark, named so a reader can ROUTE it.

    !! STRUCTURED RATHER THAN A SENTENCE, ruled by Roy 2026-08-30: *"the errors
    should be stacked and capable of being read off correctly so that each can
    be fixed or sent back to the role."* `desk.mark.parse` returns flat strings
    each opening with a `where`, and a caller cannot route on a sentence -- so
    the role and the address ride beside the message.

    ! THERE IS NO `kind` FIELD. The three questions -- is this mark well formed,
    did its base drift, did anyone rule here -- stay three separate lists on
    `flows.collate.Collated`. A `kind` would only restate which list a Problem
    is already in.

    Attributes:
        role: the `edit_copy` this came back in -- WHO to send it back to.
        address: the place, or "" for a problem about the copy itself rather
            than about any one mark.
        message: the rule broken, worded by whichever check found it.
    """

    role: str
    address: str
    message: str
```

Add `from dataclasses import dataclass` to `collator.py`'s imports, and
`from comment_review.machine.repo import can_escape, read_raw` stays as it is.

Rewrite `problems_in`'s body to build `Problem`s. Its docstring keeps every existing
`!!` note and gains:

```
    !! IT RETURNS `Problem`s, NOT SENTENCES, since 2026-08-30. See `Problem`.

    !! AND IT MOVED HERE FROM `flows/marks.py`, per `decision-log.md
    Process: #54` -- "did every place get ruled on" is a question about the SET,
    which is this module's, while `desk/mark.py` answers for one mark alone.
```

```python
def problems_in(report: dict) -> tuple[list[Problem], int]:
    role = report.get("role")
    named = role if isinstance(role, str) and role.strip() else ""
    if not isinstance(report.get("sheets"), list):
        return [Problem(named, "", "the report needs a `sheets` list")], 0

    out: list[Problem] = []
    ruled = 0
    if not named:
        out.append(Problem("", "", "the report needs the `role` that wrote it"))
    why_header = _read_from_problem(report)
    if why_header:
        out.append(Problem(named, "", f"the report's {why_header}"))

    i = 0
    for sheet in report["sheets"]:
        marks = sheet.get("marks") if isinstance(sheet, dict) else None
        if not isinstance(marks, list):
            continue
        for mark in marks:
            i += 1
            if not isinstance(mark, dict):
                out.append(Problem(named, "", f"mark {i} is not an object"))
                continue
            if untouched(mark):
                continue
            ruled += 1
            address = str(mark.get("address") or "")
            where = address or f"mark {i}"
            _, why = parse(where, mark)
            out += [Problem(named, address, message) for message in why]
    return out, ruled
```

Add `from comment_review.binder.binder import _read_from_problem, rows_of` to
`collator.py` (it already imports `rows_of`).

Remove the now-unused imports from `flows/marks.py`: `_read_from_problem`,
`INSTRUCTIONS`, `Instruction`, `parse`, `untouched`. Keep `Mark` and `address_for`.

- [x] **Step 4: Repoint `commands/mark.py`**

```python
from comment_review.desk.collator import problems_in, tally, unruled
from comment_review.flows.marks import seed
```

and in `main`'s `--check` branch, print each `Problem` with its role and address:

```python
        broken, ruled = problems_in(report)
        for problem in broken:
            where = problem.address or problem.role or "the report"
            print(f"{where}: {problem.message}")
```

! **THIS IMPORT IS TEMPORARY AND TASK 12 REPLACES IT.** `Process: #12` has a command
expose a FLOW, and `flows/collate.py` does not exist until Task 10. Importing `desk/`
from a command is the state this task leaves behind for one commit, and the plan says so
rather than leaving a reader to wonder.

- [x] **Step 5: Move the tests**

Move every test in `tests/test_marks_flow.py` that exercises `problems_in`, `unruled` or
`tally` into `tests/test_collator.py`, changing only the import. **Do not rewrite an
assertion** -- a moved test that also changed what it asserts proves nothing about the
move.

- [x] **Step 6: Run the tests**

```bash
uv run pytest -q
```

Expected: PASS.

- [x] **Step 7: Commit**

```bash
git add src/comment_review/desk/collator.py src/comment_review/flows/marks.py \
        src/comment_review/commands/mark.py tests/
git commit -F <message file>
```

---

## Task 9: `D10` -- the base comes from the binder, and drift is reported

**Files:**
- Modify: `src/comment_review/desk/collator.py`
- Test: `tests/test_collator.py`

**Interfaces:**
- Consumes: `Problem` (Task 8), `Mark.raw_text` (Task 3).
- Produces:
  - `base_texts(binder: dict) -> dict[str, str]`
  - `drift_in(report: dict, base: dict[str, str]) -> list[Problem]`
  - `claim_verbatim_problems(where, mark, base)` -- third parameter renamed and
    **re-sourced**
  - `source_verification(..., base=...)` -- keyword renamed from `raw_text`

**Necessity.** `raw_text` is seeded, and Task 3 makes `parse` read it back off what the
role RETURNED. Two things would then rest on text the party being checked could have
altered: `claim_verbatim_problems` compares the quoted sentence against it, and Task 7's
`compose` diffs every side against it.

!! **THAT IS THE SHAPE `docs/gates.md` NAMES.** The round-trip identity scored **699 of
699 on its first run** because it rebuilt each file from the line positions it had just
read out of that file, and began finding things one commit later when it was made to set
from the CUES instead. A base supplied by the party being checked cannot disagree with
them.

! **DRIFT IS REPORTED, NOT REFUSED.** The tree can legitimately move between `seed` and
the return. A refusal would discard a whole copy over a change nobody made.

- [x] **Step 1: Write the failing tests**

```python
class TestTheBaseIsTheBinders:
    def test_base_texts_keys_every_address_the_binder_carries(self, tmp_path):
        binder = binder_of(a_small_real_tree(tmp_path), 0)
        base = base_texts(binder)
        carried = {r["address"] for r in rows_of(binder) if r.get("address")}
        assert set(base) == carried

    def test_a_returned_raw_text_that_changed_is_REPORTED(self, tmp_path):
        """!! THE 699/699 SHAPE, REFUSED. A check that reads its base off the
        entry it is checking cannot disagree with it -- `docs/gates.md`."""
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy = seed(binder, "block-context")
        entry = copy["sheets"][0]["marks"][0]
        entry.update(a_clean(entry["address"]))
        entry["raw_text"] = "# not what was seeded\n"
        drift = drift_in(copy, base_texts(binder))
        assert [p.address for p in drift] == [entry["address"]]
        assert drift[0].role == "block-context"

    def test_an_untouched_slot_is_not_drift(self, tmp_path):
        """Nobody wrote here, so there is nothing to have drifted."""
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy = seed(binder, "block-context")
        assert drift_in(copy, base_texts(binder)) == []

    def test_a_faithful_copy_reports_no_drift(self, tmp_path):
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy = seed(binder, "block-context")
        entry = copy["sheets"][0]["marks"][0]
        entry.update(a_clean(entry["address"]))
        assert drift_in(copy, base_texts(binder)) == []

    def test_verify_report_measures_the_claim_against_the_BINDER(self, tmp_path):
        """A mark whose `claim.false` is absent from the seeded paragraph is
        reported even when the mark's own `raw_text` was rewritten to contain
        it -- which is the whole point of taking the base from the binder."""
        repo = a_small_real_tree(tmp_path)
        binder = binder_of(repo, 0)
        copy = seed(binder, "block-context")
        entry = copy["sheets"][0]["marks"][0]
        entry.update(a_correct(entry["address"], "a sentence nobody wrote"))
        entry["raw_text"] = "a sentence nobody wrote"
        problems = verify_report(copy, binder, repo)
        assert any("is not in the paragraph" in p for p in problems)
```

- [x] **Step 2: Run them to verify they fail**

```bash
uv run pytest -q tests/test_collator.py -k TheBaseIsTheBinders
```

Expected: FAIL with `ImportError: cannot import name 'base_texts'`. The last test fails
differently once the import exists -- it passes today for the wrong reason, so run it
again after Step 3 and confirm it still passes for the right one.

- [x] **Step 3: Implement `base_texts` and `drift_in`**

Add to `desk/collator.py`, after `known_addresses`:

```python
def base_texts(binder: dict) -> dict[str, str]:
    """Every address the binder carries -> the paragraph it SEEDED there.

    !! THE BASE IS THE BINDER'S, NEVER A RETURNED MARK'S. `raw_text` is seeded
    and comes back on the mark, so a compose or a verbatim check reading it off
    the mark would measure a claim against text the party being checked
    supplied. `docs/gates.md` holds the measured case: the round-trip identity
    scored 699 of 699 on its first run by rebuilding each file from line
    positions it had just read out of that file.

    Args:
        binder: as `binder.read` returns one.

    Returns:
        address -> that place's `raw_text`. A row carrying no address is
        dropped, matching `known_addresses`.
    """
    return {
        row["address"]: str(row.get("raw_text", ""))
        for row in rows_of(binder)
        if row.get("address")
    }


def drift_in(report: dict, base: dict[str, str]) -> list[Problem]:
    """Every ruled mark whose returned `raw_text` is not the one it was handed.

    ! REPORTED, NOT REFUSED. The tree can move between `seed` and the return,
    which is an ordinary thing rather than a malformed copy -- so a whole copy
    is never discarded over it. What a run must not do is compose over a base
    nobody sanctioned, which `base_texts` prevents separately.

    ! AN UNTOUCHED SLOT IS SKIPPED. Nobody wrote there, so nothing drifted.

    ! AN ADDRESS THE BINDER DOES NOT CARRY IS NOT DRIFT EITHER -- that is
    `address_problems`' question, and reporting it twice in two vocabularies is
    the duplication `Problem` exists to avoid.

    Args:
        report: one edit_copy, as it came back.
        base: `base_texts` of the binder it was seeded from.

    Returns:
        One `Problem` per drifted place, in sheet then mark order.
    """
    role = report.get("role")
    named = role if isinstance(role, str) else ""
    sheets = report.get("sheets")
    if not isinstance(sheets, list):
        return []
    out: list[Problem] = []
    for sheet in sheets:
        marks = sheet.get("marks") if isinstance(sheet, dict) else None
        if not isinstance(marks, list):
            continue
        for entry in marks:
            if not isinstance(entry, dict) or untouched(entry):
                continue
            address = str(entry.get("address") or "")
            if address not in base:
                continue
            got = str(entry.get("raw_text") or "")
            if got != base[address]:
                out.append(
                    Problem(
                        named,
                        address,
                        "`raw_text` is not the paragraph this place was seeded "
                        "with -- the copy came back with a different base",
                    )
                )
    return out
```

- [x] **Step 4: Re-source the verbatim check**

In `claim_verbatim_problems`, rename the third parameter and rewrite its doc:

```python
def claim_verbatim_problems(where: str, mark: Mark, base: str) -> list[str]:
    """Whether the sentence this mark's claim quotes is really in the paragraph.
    ...
    Args:
        where: how to name this mark in a message -- its address, or a position.
        mark: one role's ruling, already through `desk.mark.parse`.
        base: the paragraph THE BINDER SEEDED at this place, from `base_texts`.
            ! NOT `mark.raw_text`, which is what came BACK -- a check reading
            its own base off the thing it is checking cannot disagree with it.
    """
```

and the body's last comparison becomes `if value not in base:`.

In `source_verification`, rename the keyword `raw_text` to `base` and pass it through.

In `verify_report`, replace the per-entry `raw_text` dig:

```python
    known = known_addresses(binder)
    base = base_texts(binder)
    ...
            out += source_verification(
                where,
                mark,
                base=base.get(mark.address, ""),
                known=known,
                root=root,
                cache=cache,
            )
```

and delete the two lines that read `entry.get("raw_text")`.

- [x] **Step 5: Run the tests**

```bash
uv run pytest -q tests/test_collator.py
uv run pytest -q
```

Expected: PASS, including
`test_verify_report_measures_the_claim_against_the_BINDER`, which now passes because the
base comes from the binder rather than because the mark happened to agree.

- [x] **Step 6: Commit**

```bash
git add src/comment_review/desk/collator.py tests/test_collator.py
git commit -F <message file>
```

---

## Task 10: `P1` and `P2` -- `flows/collate.py`, the resolutions and the fold

**Files:**
- Create: `src/comment_review/flows/collate.py`
- Modify: `tests/helpers.py` (extend for a real base)
- Test: `tests/test_collate.py`

**Interfaces:**
- Consumes: `Problem`, `problems_in`, `unruled`, `tally`, `base_texts`, `drift_in`
  (Tasks 8-9); `compose`, `CannotCompose` (Task 7); `Mark.as_entry` (Task 4).
- Produces:
  - `Collated` -- `chief: dict`, `problems: list[Problem]`, `drift: list[Problem]`,
    `escalations: list[dict]`, `rereads: list[dict]`, `unruled: dict[str, list[str]]`,
    `tally: dict[str, dict]`
  - `collate(stage: str, edit_copies: list[dict], binder: dict) -> Collated`

**Necessity.** `gather`, `places`, `reconcile` and `docket_from` are built and tested and
**nothing exposes them** -- the 2026-08-29 end-to-end run drove them from a hand-written
script, so the task agent cannot reach reconciliation at all.

! **THE RESOLUTIONS SIT DOWNSTREAM OF `reconcile`, WHICH IS NOT TOUCHED.** `Reconciled` is
the INTERMEDIATE (`Vocabulary: #30`) and keeps its three lists, so `A-T3`'s three outcomes
stay three and the collator keeps answering one question.

! **AN UNRESOLVED PLACE IS ABSENT FROM THE CHIEF'S COPY, NOT AN UNTOUCHED SLOT.**
`untouched` means *nobody wrote here*; a place two roles wrote on that nothing resolved is
a different fact, and giving one shape two meanings is the conflation `untouched` exists
to prevent.

- [x] **Step 1: Extend `tests/helpers.py` for a real base**

`_synthetic_binder` writes `raw_text: ""`, which no compose can act on. Add beside it:

```python
def a_binder_over(paragraphs: dict[str, str]) -> dict:
    """A binder whose rows carry REAL paragraph text, keyed by address.

    ! WRITTEN IN TASK 10, for `tests/test_collate.py`. `_synthetic_binder`
    seeds every row with an empty `raw_text`, which is enough for `places()`
    -- it groups by address and reads no text -- and not enough for a compose,
    whose whole subject is the base.

    Args:
        paragraphs: `path@cue` -> the paragraph at that place.

    Returns:
        A binder in `bind`'s shape, one page per distinct path.
    """
    by_path: dict[str, list[tuple[str, str]]] = {}
    for address, text in paragraphs.items():
        path, _, cue = address.partition("@")
        by_path.setdefault(path, []).append((cue, text))
    return {
        "read_from": {"root": "tests/helpers.py", "revise": 0},
        "pages": [
            {
                "path": path,
                "sha": "0" * 40,
                "rows": [
                    {"cue": cue, "anchor": "", "raw_text": text} for cue, text in rows
                ],
            }
            for path, rows in by_path.items()
        ],
    }


def copies_over(binder: dict, by_role: dict) -> list[dict]:
    """One real seeded `edit_copy` per role, each overlaid with that role's marks.

    ! WRITTEN IN TASK 10. `a_master_proof` builds its own synthetic binder per
    role; this seeds every role from ONE binder, which is what `collate` is
    handed and what the drift check measures against.

    Args:
        binder: the binder every copy is seeded from.
        by_role: role name -> {address: mark}.

    Returns:
        One `edit_copy` per role, in `by_role` order.
    """
    copies = []
    for role, marks_by_address in by_role.items():
        copy = seed(binder, role)
        for sheet in copy["sheets"]:
            for entry in sheet["marks"]:
                mark = marks_by_address.get(entry["address"])
                if mark is not None:
                    entry.update(mark)
        copies.append(copy)
    return copies


def a_correct_setting(address: str, sentence: str, change: str) -> dict:
    """A `correct` whose `change` is exactly `change`.

    ! WRITTEN IN TASK 10. `a_correct` writes a fixed `change` string, which
    two roles would then propose identically at every place -- so a compose
    case cannot be built from it.
    """
    mark = a_correct(address, sentence)
    mark["change"] = change
    return mark
```

- [x] **Step 2: Write the failing tests**

Create `tests/test_collate.py`:

```python
"""One stage's returned copies, folded into the copy chief's own.

! INPUTS ARE REAL -- binders from `bind`-shaped helpers, copies from the real
`seed`, marks built through `desk.mark.INSTRUCTIONS`. A literal appears only
where MALFORMED is the input.
"""

import pytest
from helpers import (
    a_binder_over,
    a_clean,
    a_correct,
    a_correct_setting,
    a_move,
    an_add,
    copies_over,
)

from comment_review.desk.mark import parse
from comment_review.flows.collate import collate

BASE = "# one\n# two\n# three\n"


def one_place():
    return a_binder_over({"m.py@b1": BASE})


def two_places():
    return a_binder_over({"m.py@b1": BASE, "m.py@b5": BASE})


class TestTheResolutions:
    def test_one_owing_mark_settles_onto_the_chiefs_copy(self):
        binder = one_place()
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}})
        got = collate("4c", copies, binder)
        assert got.escalations == []
        assert got.rereads == []
        marks = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert [m["address"] for m in marks] == ["m.py@b1"]

    def test_byte_identical_changes_are_not_a_contest(self):
        binder = one_place()
        same = "# one\n# TWO\n# three\n"
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct_setting("m.py@b1", "two", same)},
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", same)
                },
            },
        )
        got = collate("4c", copies, binder)
        assert got.escalations == []
        marks = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert [m["change"] for m in marks] == [same]

    def test_two_answers_to_one_sentence_escalate_and_reach_no_copy(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# one\n# TWO\n# three\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# one\n# dos\n# three\n")
                },
            },
        )
        got = collate("4c", copies, binder)
        assert [e["address"] for e in got.escalations] == ["m.py@b1"]
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []

    def test_disjoint_edits_compose_onto_the_chiefs_copy(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", 0, "# ONE\n# two\n# three\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", 2, "# one\n# two\n# THREE\n")
                },
            },
        )
        got = collate("4c", copies, binder)
        assert got.escalations == []
        assert got.rereads == []
        marks = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert [m["change"] for m in marks] == ["# ONE\n# two\n# THREE\n"]

    def test_a_refused_compose_stays_a_reread(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", 0, "# ONE\n# two\n# three\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", 1, "# UNO\n# two\n# three\n")
                },
            },
        )
        got = collate("4c", copies, binder)
        assert [e["address"] for e in got.rereads] == ["m.py@b1"]
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []

    def test_every_role_clean_produces_an_empty_copy_and_no_carry_forward(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_clean("m.py@b1")},
                "function-context": {"m.py@b1": a_clean("m.py@b1")},
            },
        )
        got = collate("4c", copies, binder)
        assert got.escalations == []
        assert got.rereads == []
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []

    def test_an_add_is_carried_forward(self):
        """`_outcome` widens an `add` to every role of the stage, because two
        adds at two addresses never meet under per-place grouping."""
        binder = one_place()
        copies = copies_over(binder, {"block-context": {"m.py@b1": an_add("m.py@b1")}})
        got = collate("4c", copies, binder)
        assert [e["address"] for e in got.rereads] == ["m.py@b1"]


class TestTheChiefsCopy:
    def test_it_parses_as_an_ordinary_edit_copy(self):
        binder = one_place()
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}})
        got = collate("4c", copies, binder)
        from comment_review.desk.containers import parse_edit_copy

        copy, why = parse_edit_copy("the chief's", got.chief)
        assert why == []
        assert copy is not None
        assert copy.role == "copy-chief"

    def test_every_mark_on_it_parses(self):
        binder = one_place()
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}})
        got = collate("4c", copies, binder)
        for sheet in got.chief["sheets"]:
            for entry in sheet["marks"]:
                mark, why = parse(entry["address"], entry)
                assert why == [], why
                assert mark is not None

    def test_a_composed_mark_carries_both_sides_sources(self):
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", 0, "# ONE\n# two\n# three\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", 2, "# one\n# two\n# THREE\n")
                },
            },
        )
        got = collate("4c", copies, binder)
        entry = [m for s in got.chief["sheets"] for m in s["marks"]][0]
        assert len(entry["sources"]) == 2
        assert "block-context" in entry["reason"]
        assert "function-context" in entry["reason"]

    def test_an_unresolved_place_is_ABSENT_not_untouched(self):
        """!! `untouched` MEANS NOBODY WROTE HERE. A place two roles wrote on
        that nothing resolved is a different fact, and writing it as an
        untouched slot would give one shape two meanings."""
        from comment_review.desk.mark import untouched

        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n")
                },
            },
        )
        got = collate("4c", copies, binder)
        entries = [m for s in got.chief["sheets"] for m in s["marks"]]
        assert entries == []
        assert not any(untouched(e) for e in entries)


class TestTheStackedCheck:
    def test_a_malformed_copy_is_reported_with_its_role_and_address(self):
        binder = one_place()
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}})
        copies[0]["sheets"][0]["marks"][0]["claim"] = {}
        got = collate("4c", copies, binder)
        assert got.problems
        assert got.problems[0].role == "block-context"
        assert got.problems[0].address == "m.py@b1"

    def test_TWO_malformed_copies_are_BOTH_reported(self):
        """!! IT DOES NOT STOP AT THE FIRST BAD COPY. Roy, 2026-08-30: the
        errors stack so each can be fixed or sent back to the role. A check
        that stopped here would hide the second until the next run."""
        binder = one_place()
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_correct("m.py@b1")},
                "function-context": {"m.py@b1": a_correct("m.py@b1")},
            },
        )
        for copy in copies:
            copy["sheets"][0]["marks"][0]["claim"] = {}
        got = collate("4c", copies, binder)
        assert {p.role for p in got.problems} == {"block-context", "function-context"}

    def test_drift_is_reported_and_does_not_stop_the_fold(self):
        binder = one_place()
        copies = copies_over(binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}})
        copies[0]["sheets"][0]["marks"][0]["raw_text"] = "# not what was seeded\n"
        got = collate("4c", copies, binder)
        assert [p.address for p in got.drift] == ["m.py@b1"]
        assert [m for s in got.chief["sheets"] for m in s["marks"]] != []
```

- [x] **Step 3: Run them to verify they fail**

```bash
uv run pytest -q tests/test_collate.py
```

Expected: FAIL -- `ModuleNotFoundError: No module named 'comment_review.flows.collate'`.

- [x] **Step 4: Implement the flow**

Create `src/comment_review/flows/collate.py`:

```python
"""COLLATE -- one stage's returned edit_copies, folded into the chief's own.

    collate(stage, edit_copies, binder) -> Collated

Six acts, in order:

    CHECK      every copy's marks, stacked -- `desk.collator.problems_in`
    DRIFT      a returned `raw_text` that is not the seeded one
    GATHER     `desk.proof.gather` -- the master_proof
    PLACE      `desk.collator.places` -- marks grouped by the place they touch
    RECONCILE  `desk.collator.reconcile` -- settled, escalated, re-read
    RESOLVE    the automatic resolutions, then the fold

!! THE RESOLUTIONS SIT DOWNSTREAM OF `reconcile`, WHICH IS UNTOUCHED.
`desk.collator.Reconciled` is the INTERMEDIATE -- `decision-log.md
Vocabulary: #30` -- and keeps its three lists. What this flow adds is which of
those places need no person, so the collator goes on answering one question.

!! WHAT IT CANNOT RESOLVE IT CARRIES FORWARD NAMED, resolving nothing on its
own. `Process: #22`: sending a place back is an act someone is on record for.

! THE CHECK DOES NOT STOP AT THE FIRST BAD COPY. Roy, 2026-08-30: *"the errors
should be stacked and capable of being read off correctly so that each can be
fixed or sent back to the role."* That is verification's discipline, which
`desk/collator.py`'s own header already states against reconciliation's raise.
"""

from dataclasses import dataclass, field

from comment_review.desk.collator import (
    Placed,
    Problem,
    base_texts,
    drift_in,
    problems_in,
    reconcile,
    tally,
    unruled,
)
from comment_review.desk.mark import INSTRUCTIONS, Instruction, Mark
from comment_review.desk.proof import gather
from comment_review.reading.addresser import cue_of, unflatten
from comment_review.results.differences import CannotCompose, compose


@dataclass(frozen=True)
class Collated:
    """What one stage came to, and what is left for a person.

    Attributes:
        chief: the copy chief's `edit_copy` -- one mark per RESOLVED place.
            An ordinary edit_copy; `desk.containers.parse_edit_copy` accepts it
            with no second shape.
        problems: every copy's malformed marks, stacked in copy then mark
            order, each naming the role to send it back to.
        drift: a returned `raw_text` that is not the one the place was seeded
            with, same shape and same routing.
        escalations: places carried forward -- two or more owing marks ruling
            on ONE sentence with different answers.
        rereads: places carried forward -- marks on different sentences whose
            compose refused, plus every place an `add` touches, plus every end
            of a `move` in a cycle.
        unruled: role -> the addresses nobody wrote in.
        tally: role -> how many of each instruction that copy carried.
    """

    chief: dict
    problems: list[Problem] = field(default_factory=list)
    drift: list[Problem] = field(default_factory=list)
    escalations: list[dict] = field(default_factory=list)
    rereads: list[dict] = field(default_factory=list)
    unruled: dict[str, list[str]] = field(default_factory=dict)
    tally: dict[str, dict] = field(default_factory=dict)


def _identical(owing: list[Placed]) -> Mark | None:
    """The one mark to take where every owing mark says the same thing.

    !! SAME INSTRUCTION AND BYTE-IDENTICAL `change`. Two roles that reached one
    answer are not a contest, whatever `reconcile` had to call them -- it
    groups by the sentence ruled on and cannot see that the answers agree.

    ! A DIFFERING INSTRUCTION REFUSES even where the text matches, so no mark
    on the chief's copy ever carries an instruction chosen between two that
    disagreed.

    Returns:
        The role-sorted first mark, or None where they do not all agree.
    """
    first = owing[0].mark
    for placed in owing[1:]:
        if placed.mark.instruction is not first.instruction:
            return None
        if placed.mark.change != first.change:
            return None
    return min(owing, key=lambda placed: placed.role).mark


def _composition(entry: dict, base: str) -> Mark | None:
    """The composed mark for a place whose sides touched no common span.

    !! THE COMPOSED MARK IS A SYNTHESIZED `correct` WHOSE `claim.false` IS THE
    WHOLE BASE, which is true: the whole paragraph is being replaced. It parses,
    which is what lets the chief's copy be an ordinary `edit_copy`.

    ! `sources` IS BOTH SIDES', IN ROLE ORDER. `correct` owes sources, and the
    union is what each side actually cited.

    ! ATTRIBUTION RIDES IN `reason`. `Mark` carries no `set_by`, and what the
    DOCKET says about who set a page is `P4`'s question in SP-4.

    Returns:
        The composed `Mark`, or None where the sides met on some span or where
        fewer than two roles proposed anything.
    """
    owing = entry["marks"]
    sides = {placed.role: placed.mark.change for placed in owing}
    if len(sides) < 2:
        return None
    if len({placed.mark.instruction for placed in owing}) != 1:
        return None
    try:
        text = compose(base, sides)
    except CannotCompose:
        return None
    roles = sorted(sides)
    return Mark(
        address=entry["address"],
        anchor=owing[0].mark.anchor,
        raw_text=base,
        instruction=Instruction.CORRECT,
        claim={"false": base, "true": text},
        reason=(
            "composed from disjoint edits by "
            + ", ".join(roles)
            + " -- each touched a span the others did not"
        ),
        sources=tuple(
            source for placed in owing for source in placed.mark.sources
        ),
        change=text,
    )


def _resolve(reconciled, base: dict[str, str]) -> tuple[dict, list[dict], list[dict]]:
    """The automatic resolutions over `reconcile`'s three lists.

    Returns:
        `(address -> the one Mark for it, escalations left, rereads left)`.
    """
    resolved: dict[str, Mark] = {}
    escalations: list[dict] = []
    rereads: list[dict] = []

    for entry in reconciled.settled:
        resolved[entry["address"]] = entry["marks"][0].mark

    for entry in reconciled.escalations:
        agreed = _identical(entry["marks"])
        if agreed is None:
            escalations.append(entry)
        else:
            resolved[entry["address"]] = agreed

    for entry in reconciled.rereads:
        composed = _composition(entry, base.get(entry["address"], ""))
        if composed is None:
            rereads.append(entry)
        else:
            resolved[entry["address"]] = composed

    return resolved, escalations, rereads


def _chief_copy(read_from: dict, resolved: dict[str, Mark], proof: dict) -> dict:
    """The copy chief's `edit_copy` -- one mark per resolved place.

    !! ONLY RESOLVED PLACES GET AN ENTRY. `desk.mark.untouched` means NOBODY
    WROTE HERE; a place two roles wrote on that nothing resolved is a different
    fact, so it rides beside this copy in `Collated` rather than being written
    as an empty slot.

    ! PATHS ARE THE REAL ONES. An address carries the FLATTENED path;
    `unflatten` resolves it against the proof's own sheet paths, exactly as
    `docket_from` does, so the sheets name files that are actually there.
    """
    paths: list[str] = []
    shas: dict[str, str] = {}
    for copy in proof.get("edit_copies", []):
        for sheet in copy.get("sheets", []):
            path = sheet.get("path") if isinstance(sheet, dict) else None
            if isinstance(path, str) and path and path not in shas:
                paths.append(path)
                shas[path] = str(sheet.get("sha", ""))

    sheets: dict[str, dict] = {}
    for address, mark in resolved.items():
        addr = cue_of(address)
        real = unflatten(addr.path, paths) or addr.path
        sheet = sheets.setdefault(
            real, {"path": real, "sha": shas.get(real, ""), "marks": []}
        )
        sheet["marks"].append(mark.as_entry())
    return {
        "role": "copy-chief",
        "read_from": {**read_from},
        "sheets": list(sheets.values()),
    }


def collate(stage: str, edit_copies: list[dict], binder: dict) -> Collated:
    """One stage's returned copies, checked, reconciled and folded.

    Args:
        stage: the label these copies were dispatched under -- "4a", "4c".
        edit_copies: one per role, or one per SHARD under fan-out, as each came
            back.
        binder: the binder they were seeded from. ! IT SUPPLIES THE BASE AND
            THE OTHER SIDE OF THE DRIFT CHECK, and nothing else -- address
            integrity over the docket is `P28`'s.

    Returns:
        A `Collated`.

    Raises:
        desk.collator.UnnamedRole: a copy carries no `role`.
        desk.collator.MalformedMark: an entry neither untouched nor parseable
            reached `places`. ! THE CHECK ABOVE REPORTS THE SAME ENTRIES FIRST,
            so a caller that reads `problems` before acting never gets here.
        desk.proof.MismatchedRoot: two copies were censused from different
            roots.
    """
    base = base_texts(binder)
    problems: list[Problem] = []
    drift: list[Problem] = []
    left: dict[str, list[str]] = {}
    counts: dict[str, dict] = {}
    for copy in edit_copies:
        found, _ruled = problems_in(copy)
        problems += found
        drift += drift_in(copy, base)
        role = str(copy.get("role") or "")
        left[role] = unruled(copy)
        counts[role] = tally(copy)

    proof = gather(stage, edit_copies)
    reconciled = reconcile(proof)
    resolved, escalations, rereads = _resolve(reconciled, base)
    return Collated(
        chief=_chief_copy(proof.get("read_from", {}), resolved, proof),
        problems=problems,
        drift=drift,
        escalations=escalations,
        rereads=rereads,
        unruled=left,
        tally=counts,
    )
```

- [x] **Step 5: Run the tests**

```bash
uv run pytest -q tests/test_collate.py
uv run pytest -q
```

Expected: PASS.

- [x] **Step 6: Commit**

```bash
git add src/comment_review/flows/collate.py tests/test_collate.py tests/helpers.py
git commit -F <message file>
```

---

## Task 11: `D8` -- the resolved moves are a DAG

**Files:**
- Modify: `src/comment_review/flows/collate.py`
- Test: `tests/test_collate.py`

**Interfaces:**
- Consumes: `_resolve` from Task 10.
- Produces: `_move_order(resolved) -> tuple[list[str], list[str]]` -- `(addresses in a
  safe order, the addresses caught in a cycle)`. `Collated.order: list[str]` is added.

**Closes:** `TODO/collator-defects.md` T12, T13, T14.

**Necessity.** Roy, 2026-08-30: *"the moves have to be resolved to some sorted order
because a double move can cause problems, and we can't allow circles so it has to resolve
from a DAG."* A `move` is one instruction at two places, so a SET of moves is a graph over
addresses, and applying it needs an order:

    A: b1 -> b5     A first    A writes b5, then B deletes b5   -- A's change is LOST
    B: b5 -> b9     B first    B empties b5, then A fills it    -- both land

!! **AND WHAT PROTECTS THIS TODAY IS AN ACCIDENT.** MEASURED 2026-08-30: a chain or cycle
of length 2 or more never reaches the settled set, because its shared address is a
two-mark place -- `_sentence_key` returns `id(mark)` for a `move`, so two never compare
equal. **No rule anywhere says a chained move must not settle.** It falls out of a
function whose docstring is about two `add`s.

! **AND THE ORDER OF INDEPENDENT MOVES IS WALK ORDER**, with nothing stating it is safe or
re-derivable -- measured as four alterations with deletes and writes interleaved.

- [x] **Step 1: Write the failing tests**

```python
class TestTheMovesAreADag:
    def test_a_move_resolves_only_if_BOTH_its_ends_resolve(self):
        """`_join_moves` gives both ends one outcome one layer up; this is the
        same rule at the resolution layer, so no auto-resolution can apply half
        a move -- the paragraph read twice, or deleted and never rewritten."""
        binder = two_places()
        copies = copies_over(
            binder,
            {
                "block-context": {"m.py@b1": a_move("m.py@b1", "m.py@b5")},
                "function-context": {
                    "m.py@b5": a_correct_setting("m.py@b5", "two", "# a\n")
                },
            },
        )
        got = collate("4c", copies, binder)
        assert [m for s in got.chief["sheets"] for m in s["marks"]] == []
        assert {e["address"] for e in got.rereads} >= {"m.py@b1", "m.py@b5"}

    def test_independent_moves_emit_in_a_stable_order(self):
        binder = a_binder_over(
            {f"m.py@b{n}": BASE for n in (1, 2, 7, 8)}
        )
        marks = {
            "m.py@b1": a_move("m.py@b1", "m.py@b2"),
            "m.py@b7": a_move("m.py@b7", "m.py@b8"),
        }
        first = collate("4c", copies_over(binder, {"block-context": marks}), binder)
        flipped = dict(reversed(list(marks.items())))
        second = collate("4c", copies_over(binder, {"block-context": flipped}), binder)
        assert first.order == second.order

    def test_a_move_whose_origin_another_move_fills_is_emitted_FIRST(self):
        """B must VACATE the address before A fills it."""
        from comment_review.flows.collate import _move_order

        binder = a_binder_over({f"m.py@b{n}": BASE for n in (1, 5, 9)})
        marks = {
            "m.py@b1": a_move("m.py@b1", "m.py@b5"),
            "m.py@b5": a_move("m.py@b5", "m.py@b9"),
        }
        copies = copies_over(binder, {"block-context": marks})
        got = collate("4c", copies, binder)
        resolved = {
            e["address"]: e for s in got.chief["sheets"] for e in s["marks"]
        }
        if "m.py@b1" in resolved and "m.py@b5" in resolved:
            assert got.order.index("m.py@b5") < got.order.index("m.py@b1")

    def test_a_cycle_is_carried_forward_and_NAMED(self):
        """! DRIVEN WITH A `Reconciled` BUILT DIRECTLY, because no cycle
        reaches the resolution step through `reconcile` today -- a shared
        address is a two-mark place. That is exactly why the rule is written:
        the protection upstream is a side effect, and a side effect is not a
        rule."""
        from comment_review.desk.mark import parse
        from comment_review.flows.collate import _move_order

        def a_resolved_move(origin, destination):
            mark, why = parse(origin, a_move(origin, destination))
            assert why == [], why
            return mark

        resolved = {
            "m.py@b1": a_resolved_move("m.py@b1", "m.py@b2"),
            "m.py@b2": a_resolved_move("m.py@b2", "m.py@b1"),
        }
        order, cycle = _move_order(resolved)
        assert order == []
        assert set(cycle) == {"m.py@b1", "m.py@b2"}

    def test_a_chain_orders_rather_than_cycling(self):
        from comment_review.desk.mark import parse
        from comment_review.flows.collate import _move_order

        def a_resolved_move(origin, destination):
            mark, why = parse(origin, a_move(origin, destination))
            assert why == [], why
            return mark

        resolved = {
            "m.py@b1": a_resolved_move("m.py@b1", "m.py@b5"),
            "m.py@b5": a_resolved_move("m.py@b5", "m.py@b9"),
        }
        order, cycle = _move_order(resolved)
        assert cycle == []
        assert order.index("m.py@b5") < order.index("m.py@b1")
```

- [x] **Step 2: Run them to verify they fail**

```bash
uv run pytest -q tests/test_collate.py -k Dag
```

Expected: FAIL with `ImportError: cannot import name '_move_order'`.

- [x] **Step 3: Implement the pairing, the cycle check and the order**

Add to `flows/collate.py`:

```python
def _touched_by(mark: Mark) -> list[str]:
    """Every address one mark lands on -- its own, and a `move`'s destination.

    ! THE SAME RULE `desk.collator._touches` APPLIES ONE LAYER UP, restated
    here rather than imported because that function is private to the module
    that groups places, and this one decides an ORDER. Both are read off
    `Instruction.MOVE` and `claim.to`, so neither can drift into a different
    idea of what a move touches without the other's tests going red.
    """
    touched = [mark.address] if mark.address else []
    if mark.instruction is Instruction.MOVE:
        destination = mark.claim.get("to")
        if isinstance(destination, str) and destination and destination not in touched:
            touched.append(destination)
    return touched


def _pair_moves(resolved: dict[str, Mark]) -> set[str]:
    """Addresses to withdraw, so no `move` is resolved at one end only.

    !! A `move` IS ONE INSTRUCTION AT TWO PLACES -- a delete at the origin and
    a write at the destination -- so resolving one end and not the other
    applies HALF of it: the paragraph read twice, or deleted and never
    rewritten. `desk.collator._join_moves` states the same rule over outcomes;
    this states it over resolutions.

    ! IT RUNS TO A FIXED POINT, because moves chain: withdrawing one pair can
    orphan the next.

    Returns:
        The addresses whose resolution must be given up.
    """
    withdrawn: set[str] = set()
    changed = True
    while changed:
        changed = False
        for address, mark in resolved.items():
            if address in withdrawn or mark.instruction is not Instruction.MOVE:
                continue
            ends = _touched_by(mark)
            if any(end not in resolved or end in withdrawn for end in ends):
                for end in ends:
                    if end in resolved and end not in withdrawn:
                        withdrawn.add(end)
                        changed = True
    return withdrawn


def _move_order(resolved: dict[str, Mark]) -> tuple[list[str], list[str]]:
    """The resolved MOVES in an order safe to apply, and any caught in a cycle.

    !! THE EDGE IS "VACATE BEFORE FILL". For two moves B and A, B must run
    first when B's ORIGIN is A's DESTINATION -- otherwise A writes that address
    and B then deletes it, and A's change is gone.

    ! TIES ARE BROKEN BY ADDRESS, so a stranger can re-derive the order and two
    runs over the same inputs produce the same list.

    ! A CYCLE IS RETURNED, NOT RAISED. Roy, 2026-08-30: *"we can't allow
    circles so it has to resolve from a DAG."* The caller carries those places
    forward as re-reads and names them, which is what `Process: #22` asks --
    sending a place back is an act someone is on record for.

    ! A SELF-MOVE CANNOT REACH HERE. `desk.mark.parse` refuses `claim.to ==
    address` (Task 5), so the length-one cycle is gone before resolution.

    Args:
        resolved: address -> the one Mark for it, moves and non-moves alike.
            Keyed by the mark's OWN address, so a move appears once.

    Returns:
        `(the move origins in a safe order, the origins caught in a cycle)`.
    """
    moves = {
        address: mark
        for address, mark in resolved.items()
        if mark.instruction is Instruction.MOVE and address == mark.address
    }
    needs: dict[str, set[str]] = {}
    for origin, mark in moves.items():
        destination = str(mark.claim.get("to", ""))
        needs[origin] = {destination} if destination in moves else set()

    out: list[str] = []
    remaining = dict(needs)
    while remaining:
        ready = sorted(
            origin
            for origin, wanted in remaining.items()
            if not (wanted & set(remaining))
        )
        if not ready:
            return out, sorted(remaining)
        for origin in ready:
            out.append(origin)
            del remaining[origin]
    return out, []
```

Wire both into `_resolve`'s caller. In `collate`, after `_resolve`:

```python
    resolved, escalations, rereads = _resolve(reconciled, base)

    # !! BOTH ENDS OR NEITHER, THEN AN ORDER. D8 of the SP-1 spec: a set of
    # moves is a graph over addresses, and half a move is worse than none.
    by_address = {
        entry["address"]: entry
        for entry in reconciled.settled + reconciled.escalations + reconciled.rereads
    }
    for address in _pair_moves(resolved):
        del resolved[address]
        entry = by_address.get(address)
        if entry is not None and entry not in rereads:
            rereads.append(entry)

    order, cycle = _move_order(resolved)
    for address in cycle:
        for end in _touched_by(resolved[address]):
            resolved.pop(end, None)
            entry = by_address.get(end)
            if entry is not None and entry not in rereads:
                rereads.append(entry)
    if cycle:
        order, _again = _move_order(resolved)
```

and add `order` to the returned `Collated`:

```python
    order: list[str] = field(default_factory=list)
```

with the attribute doc:

```
        order: the resolved `move` origins, in an order that vacates every
            address before it is filled. Ties broken by address, so a stranger
            re-derives it. Empty where no move resolved.
```

- [x] **Step 4: Run the tests**

```bash
uv run pytest -q tests/test_collate.py
uv run pytest -q
```

Expected: PASS.

- [x] **Step 5: Close the TODO tasks**

```bash
uv run python scripts/todo_tool.py check collator-defects 12
uv run python scripts/todo_tool.py check collator-defects 13
uv run python scripts/todo_tool.py check collator-defects 14
```

- [x] **Step 6: Commit**

```bash
git add src/comment_review/flows/collate.py tests/test_collate.py TODO/
git commit -F <message file>
```

---

## Task 12: `P3` -- the `collate` command

**Files:**
- Create: `src/comment_review/commands/collate.py`
- Modify: `src/comment_review/__main__.py` (add `COLLATE` to `Command`)
- Modify: `src/comment_review/commands/mark.py` (drop `--check`)
- Test: `tests/test_collate_command.py`

**Interfaces:**
- Consumes: `collate`, `Collated` (Tasks 10-11).
- Produces: `comment_review collate --stage S --binder B.json --out CHIEF.json
  --edit-copy A.json [--edit-copy B.json ...]`

**Closes:** `TODO/no-command-for-the-middle.md` tasks 1, 2 and 3.

**Necessity.** The task agent drives this pipeline by RUNNING COMMANDS, so with no command
here it cannot reach reconciliation at all. `A-T1` requires the chain to run with no
Python written by hand.

**Exit codes** extend the existing convention (`0` ok, `1` a rule broken, `2` unreadable
input), strongest first per `OUTCOMES`' own order:

| code | means |
| --- | --- |
| `0` | every place resolved; nothing carried forward |
| `1` | a copy broke a rule, or the proof could not be reconciled |
| `2` | an input could not be read |
| `3` | re-reads remain, and no escalations |
| `4` | escalations remain |

! **`--check` LEAVES `mark` ENTIRELY.** D5: the per-copy check is `collate`'s first act.
`places()` already raises on a malformed copy, so a malformed one could never be folded;
what a separate command added was the chance to fold **without ever having run the
check**. ! The cost is named: a role can no longer validate its own returned copy alone.
No caller does that today.

! **NO agent-facing FILE NAMES `mark --check`** -- verified 2026-08-30, `SKILL.md` names
no middle command at all, which is this plan's whole premise. Naming the new commands
there is `P10`, SP-6.

- [x] **Step 1: Write the failing test**

Create `tests/test_collate_command.py`:

```python
"""The `collate` command's exit codes and its report.

! IT RUNS `main()` IN-PROCESS with a built argv, not a subprocess -- the same
way the rest of this suite asks a question it can ask directly.
"""

import json

import pytest
from helpers import (
    a_binder_over,
    a_clean,
    a_correct,
    a_correct_setting,
    an_add,
    copies_over,
)

from comment_review.commands import collate as command

BASE = "# one\n# two\n# three\n"


def run(tmp_path, marks_by_role, monkeypatch, capsys):
    binder = a_binder_over({"m.py@b1": BASE})
    copies = copies_over(binder, marks_by_role)
    binder_path = tmp_path / "binder.json"
    binder_path.write_text(json.dumps(binder), encoding="utf-8")
    paths = []
    for i, copy in enumerate(copies):
        path = tmp_path / f"copy{i}.json"
        path.write_text(json.dumps(copy), encoding="utf-8")
        paths.append(str(path))
    argv = [
        "collate",
        "--stage",
        "4c",
        "--binder",
        str(binder_path),
        "--out",
        str(tmp_path / "chief.json"),
    ]
    for path in paths:
        argv += ["--edit-copy", path]
    monkeypatch.setattr("sys.argv", argv)
    code = command.main()
    return code, capsys.readouterr().out


class TestExitCodes:
    def test_everything_resolved_exits_zero(self, tmp_path, monkeypatch, capsys):
        code, _out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_correct("m.py@b1")}},
            monkeypatch,
            capsys,
        )
        assert code == 0

    def test_a_reread_exits_three(self, tmp_path, monkeypatch, capsys):
        code, _out = run(
            tmp_path,
            {"block-context": {"m.py@b1": an_add("m.py@b1")}},
            monkeypatch,
            capsys,
        )
        assert code == 3

    def test_an_escalation_exits_four(self, tmp_path, monkeypatch, capsys):
        code, _out = run(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n")
                },
            },
            monkeypatch,
            capsys,
        )
        assert code == 4

    def test_a_broken_mark_exits_one(self, tmp_path, monkeypatch, capsys):
        binder = a_binder_over({"m.py@b1": BASE})
        copies = copies_over(
            binder, {"block-context": {"m.py@b1": a_correct("m.py@b1")}}
        )
        copies[0]["sheets"][0]["marks"][0]["claim"] = {}
        binder_path = tmp_path / "binder.json"
        binder_path.write_text(json.dumps(binder), encoding="utf-8")
        copy_path = tmp_path / "copy.json"
        copy_path.write_text(json.dumps(copies[0]), encoding="utf-8")
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(binder_path),
                "--out",
                str(tmp_path / "chief.json"),
                "--edit-copy",
                str(copy_path),
            ],
        )
        assert command.main() == 1

    def test_an_unreadable_input_exits_two(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(
            "sys.argv",
            [
                "collate",
                "--stage",
                "4c",
                "--binder",
                str(tmp_path / "nowhere.json"),
                "--out",
                str(tmp_path / "chief.json"),
                "--edit-copy",
                str(tmp_path / "nowhere-either.json"),
            ],
        )
        assert command.main() == 2


class TestTheReport:
    def test_a_carried_forward_place_is_NAMED_not_counted(
        self, tmp_path, monkeypatch, capsys
    ):
        """`A-T2`: a run that settles 4 of 10 must say what became of the other
        6 rather than dropping them silently."""
        _code, out = run(
            tmp_path,
            {
                "block-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# a\n")
                },
                "function-context": {
                    "m.py@b1": a_correct_setting("m.py@b1", "two", "# b\n")
                },
            },
            monkeypatch,
            capsys,
        )
        assert "m.py@b1" in out
        assert "block-context" in out
        assert "function-context" in out

    def test_a_resolved_run_says_so_and_names_nothing(
        self, tmp_path, monkeypatch, capsys
    ):
        _code, out = run(
            tmp_path,
            {"block-context": {"m.py@b1": a_clean("m.py@b1")}},
            monkeypatch,
            capsys,
        )
        assert "escalation" not in out.lower() or "0 escalation" in out.lower()


class TestTheGateSeesIt:
    def test_collate_is_in_COMMANDS(self):
        from comment_review.__main__ import COMMANDS

        assert "collate" in COMMANDS
```

- [x] **Step 2: Run it to verify it fails**

```bash
uv run pytest -q tests/test_collate_command.py
```

Expected: FAIL with `ImportError: cannot import name 'collate' from
'comment_review.commands'`.

- [x] **Step 3: Implement the command**

Create `src/comment_review/commands/collate.py`:

```python
"""The `collate` command: its argument parsing, its report and its exit code.

    comment_review collate --stage 4c --binder B.json --out chief.json \\
        --edit-copy a.json --edit-copy b.json

The work is `flows.collate`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. `decision-log.md Process: #12`.

!! EVERY CARRIED-FORWARD PLACE IS NAMED, NEVER COUNTED. `A-T2` of
`TODO/no-command-for-the-middle.md`: a run that settles 4 of 10 must say what
became of the other 6. ! WHAT IT DOES NOT YET DO is name the command that
CONTINUES them -- `Process: #51`'s other half, which is `P22` in SP-6 by this
plan's own scoping.
"""

import argparse
import json
import sys
from pathlib import Path

from comment_review.binder.binder import read as read_binder
from comment_review.flows.collate import collate
from comment_review.machine import exceptions

#: Exit codes, extending `mark`'s own 0/1/2 with the two outcomes a caller
#: branches on. STRONGEST FIRST, matching `desk.collator.OUTCOMES`' order: a
#: run holding both reports 4, since an escalation is the stronger claim on a
#: person's attention.
OK = 0
BROKEN = 1
UNREADABLE = 2
REREADS = 3
ESCALATIONS = 4


def _load(path: str) -> tuple[dict, str]:
    """Read one JSON object, or say why it could not be read."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as err:
        return {}, f"cannot read {path}: {err}"
    try:
        got = json.loads(text)
    except ValueError as err:
        return {}, f"{path} is not JSON: {err}"
    if not isinstance(got, dict):
        return {}, f"{path} is a JSON {type(got).__name__}, not an object"
    return got, ""


def main() -> int:
    """Fold one stage's returned copies, report, and say what is left.

    Returns:
        One of `OK`, `BROKEN`, `UNREADABLE`, `REREADS` or `ESCALATIONS`.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True, help="the stage label, e.g. 4c")
    ap.add_argument(
        "--binder", required=True, help="the binder these copies were seeded from"
    )
    ap.add_argument(
        "--edit-copy",
        action="append",
        default=[],
        metavar="PATH",
        help="one role's returned edit_copy; repeat for each",
    )
    ap.add_argument("--out", required=True, help="where to write the chief's edit_copy")
    args = ap.parse_args()

    if not args.edit_copy:
        print("collate needs at least one --edit-copy", file=sys.stderr)
        return UNREADABLE

    try:
        binder_text = Path(args.binder).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as err:
        print(f"cannot read {args.binder}: {err}", file=sys.stderr)
        return UNREADABLE
    binder, why = read_binder(binder_text)
    if why:
        print(why, file=sys.stderr)
        return UNREADABLE

    copies = []
    for path in args.edit_copy:
        copy, problem = _load(path)
        if problem:
            print(problem, file=sys.stderr)
            return UNREADABLE
        copies.append(copy)

    got = collate(args.stage, copies, binder)

    for problem in got.problems:
        print(f"{problem.role} {problem.address or '(the copy)'}: {problem.message}")
    for problem in got.drift:
        print(f"{problem.role} {problem.address}: {problem.message}")
    if got.problems:
        return BROKEN

    Path(args.out).write_text(
        json.dumps(got.chief, indent=2), encoding="utf-8", newline=""
    )
    resolved = sum(len(sheet["marks"]) for sheet in got.chief["sheets"])
    print(f"{args.out}: {resolved} places resolved")

    # !! NAMED, NEVER COUNTED. Each carried-forward place prints its address
    # and every role that ruled there, so a reader can act on one without
    # re-opening the copies.
    for entry in got.escalations:
        print(f"escalated {entry['address']}: {', '.join(entry['roles'])}")
    for entry in got.rereads:
        print(f"re-read {entry['address']}: {', '.join(entry['roles'])}")

    if got.escalations:
        return ESCALATIONS
    if got.rereads:
        return REREADS
    return OK
```

- [x] **Step 4: Register it**

In `src/comment_review/__main__.py`'s `Command` enum, add in alphabetical position:

```python
    CENSUS = auto()
    COLLATE = auto()
    COMPOSITOR = auto()
```

- [x] **Step 5: Drop `--check` from `mark`**

In `src/comment_review/commands/mark.py`: delete the `--check` argument, the whole
`if args.check:` branch, and the now-unused imports of `problems_in`, `tally`, `unruled`
and `_load`. Update the module docstring's usage block to the two remaining forms, and
add:

```
!! `--check` LEFT 2026-08-30 AND IS `collate`'s FIRST ACT. `desk.collator.places`
already raises on an entry `parse` refuses, so a malformed copy could never be
folded; what a separate command added was the chance to fold WITHOUT EVER HAVING
RUN THE CHECK. ! The cost: a role can no longer validate its own returned copy
alone -- the whole stage's copies must be in hand. No caller does that today.
```

- [x] **Step 6: Run the tests**

```bash
uv run pytest -q tests/test_collate_command.py tests/gates/test_skill_commands.py
uv run pytest -q
```

Expected: PASS. `test_skill_commands.py` keeps passing because `SKILL.md` names no middle
command.

- [x] **Step 7: Close the TODO tasks**

```bash
uv run python scripts/todo_tool.py check no-command-for-the-middle 1
uv run python scripts/todo_tool.py check no-command-for-the-middle 2
uv run python scripts/todo_tool.py check no-command-for-the-middle 3
```

!! **TASK 1 DID NOT STAY CLOSED.** Ticked here against its original wording --
"ONE command writes the docket `proof --docket` reads" -- which a review then
found false of what shipped: `collate` writes the copy chief's `edit_copy`,
and `proof --docket` reads a docket; `commands/proof.py` refuses one given
the other. **Unticked and reworded to the remainder in `7bc5887`.** Tasks 2
and 3 stayed closed on their own terms and are unaffected.

- [x] **Step 8: Commit**

```bash
git add src/comment_review/commands/ src/comment_review/__main__.py \
        tests/test_collate_command.py TODO/
git commit -F <message file>
```

! **AND TWO MORE COMMITS FOLLOWED, NOT NAMED IN THIS STEP.** `9971a0b`
caught `flows.collate.collate`'s two documented raises (`UnnamedRole`,
`MismatchedRoot`) escaping `commands/collate.py` uncaught -- a raise is not
a refusal -- and `0da4055` reworded a comment that described one ordering
in the opposite direction word to `desk.collator.OUTCOMES`, and added a test
proving `main`'s ESCALATIONS-before-REREADS branch order rather than only
reading it sound.

---

- [x] **Step 9: Tick the boxes -- THIS STEP, in its own commit AFTER the one above**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-30-sp1-the-containers-and-the-collate-flow.md`, and tick `P3` in
`docs/plans/0.2.4-the-commands-for-the-middle.md`, recomputing its `Plan-tasks:`
line from the boxes

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and
ticking it asserts the claim. Where only part of a box is delivered, leave it open
and reword it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE `Plan-tasks:` FROM THE BOXES**, never increment it.

! **CITE THE COMMIT FROM THE STEP ABOVE** in the tick commit's message, so a
reader can get from a ticked box to the work that closed it.

## Task 13: `P37` -- `marks` becomes `distribute`

**Files:**
- Rename: `src/comment_review/flows/marks.py` -> `src/comment_review/flows/distribute.py`
- Rename: `src/comment_review/commands/mark.py` -> `src/comment_review/commands/distribute.py`
- Rename: `tests/test_marks_flow.py` -> `tests/test_distribute_flow.py`
- Modify: `src/comment_review/__main__.py`, and every importer

**Interfaces:**
- Consumes: everything above.
- Produces: `flows.distribute.seed`, `comment_review distribute --shape|--seed`.

**Necessity.** Roy, 2026-08-30: *"The command name and the flow name and the flows need to
be updated to have better names because a flow named mark reads like it is doing something
that it is probably not doing"*, and *"the broadcasting part seems like distribute, the
bringin back together seems like collate."*

! **IT IS LAST BECAUSE THE PAIR IS THE VERIFY.** `distribute` and `collate` read as two
halves of one round only once the second half exists.

! **`P37`'s CLAUSE ABOUT THE SHAPE VERBS IS NARROWED BY `P24`.** `seed` reaches a command
through the renamed flow; `unruled`, `problems_in` and `tally` do not -- they went to the
collator in Task 8 and reach `commands/collate.py` through `flows/collate.py`, which is
what `Process: #12` and `#54` require.

- [x] **Step 1: Find every reference before moving anything**

```bash
grep -rn "flows.marks\|flows/marks\|commands.mark\b\|commands/mark\|mark --check\|mark --seed\|mark --shape" \
  src/ tests/ docs/ --include=*.py --include=*.md
```

Write the list down. It is the checklist for Step 4.

- [x] **Step 2: Rename the files**

```bash
git mv src/comment_review/flows/marks.py src/comment_review/flows/distribute.py
git mv src/comment_review/commands/mark.py src/comment_review/commands/distribute.py
git mv tests/test_marks_flow.py tests/test_distribute_flow.py
```

- [x] **Step 3: Rename the enum member**

In `src/comment_review/__main__.py`:

```python
    CENSUS = auto()
    COLLATE = auto()
    COMPOSITOR = auto()
    DISTRIBUTE = auto()
    PROOF = auto()
```

-- `MARK` goes. The value derives from the member name, so `DISTRIBUTE` becomes
`"distribute"` with nothing hand-typed.

- [x] **Step 4: Repoint every reference from Step 1's list**

`from comment_review.flows.marks import seed` -> `from comment_review.flows.distribute
import seed`, in `tests/helpers.py`, `tests/test_containers.py`, `tests/test_collate.py`,
`src/comment_review/flows/fan_out.py` and anywhere else the grep found.

Every comment naming `mark --check` names what the code does now. The known sites:

| file | reads | becomes |
| --- | --- | --- |
| `desk/mark.py:66`, `:480` | "passing `mark --check` at exit 0" | "passing the per-copy check at exit 0" |
| `flows/fan_out.py:95` | "`mark --check`, blamed on the role" | "the per-copy check, blamed on the role" |
| `flows/distribute.py` (was `marks.py`) | "-- `mark --check` -- ruled only on" | "-- the per-copy check -- ruled only on" |

- [x] **Step 5: Update the flow's own header**

`src/comment_review/flows/distribute.py`'s first line becomes:

```python
"""DISTRIBUTE -- hand each role an edit_copy to fill.

    seed(binder, role)     one entry per row, ADDRESS ALREADY WRITTEN

!! NAMED FOR THE ACT, NOT THE ARTIFACT, since 2026-08-30. Roy: *"a flow named
mark reads like it is doing something that it is probably not doing"* -- and
*"the broadcasting part seems like distribute, the bringin back together seems
like collate."* `flows/collate.py` is the other half of the round.

!! AND THE CHECK IS NO LONGER HERE. `unruled`, `problems_in` and `tally` moved
to `desk/collator.py` -- `decision-log.md Process: #54`: a mark answers for
itself, and everything about the SET is the collator's.
"""
```

keeping the existing `!!` notes about seeding, coverage gaps and what this flow does not
check.

- [x] **Step 6: Verify nothing still names the old spellings**

```bash
grep -rn "flows.marks\|flows/marks\|mark --check\|mark --seed\|mark --shape" src/ tests/
```

Expected: empty.

! **NOT LITERALLY EMPTY, AND DELIBERATELY SO.** `tests/test_brief_worked_example.py`
still names `mark --check` at two sites (its own docstring lines discussing when
`--check` LEFT `mark` for `collate`, 2026-08-30, a fact about the flag's REMOVAL in
an earlier task, not about this task's rename). Rewriting those to "the per-copy
check" would make the sentence describing the split say the two sides are the same
thing. The one site that named a real path -- `commands/mark.py`'s own docstring --
was repointed to `commands/distribute.py`. No `flows.marks`, `flows/marks`, `mark
--seed` or `mark --shape` remains anywhere.

- [x] **Step 7: Run everything**

```bash
uv run pytest -q
uv run ruff check .
uv run ty check src/comment_review/
```

Expected: PASS.

- [x] **Step 8: Commit**

```bash
git add -A src/ tests/
git commit -F <message file>
```

! **COMMIT `6187f71`.**

---

- [x] **Step 9: Tick the boxes -- THIS STEP, in its own commit AFTER the one above**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-30-sp1-the-containers-and-the-collate-flow.md`, and tick `P37` in
`docs/plans/0.2.4-the-commands-for-the-middle.md`, recomputing its `Plan-tasks:`
line from the boxes

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and
ticking it asserts the claim. Where only part of a box is delivered, leave it open
and reword it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE `Plan-tasks:` FROM THE BOXES**, never increment it.

! **CITE THE COMMIT FROM THE STEP ABOVE** in the tick commit's message, so a
reader can get from a ticked box to the work that closed it.

## Task 14: The vocabulary, the build, and the whole-tree gates

**Files:**
- Modify: `src/comment_review/references/vocabulary.toml`
- Modify: `docs/vocabulary.md`
- Modify: `plugins/**` (BUILT, not edited)

**Interfaces:**
- Consumes: everything above.
- Produces: a tree where every gate passes and `plugins/` matches `src/`.

**Necessity.** `distribute` is a new term of art in the shipped tree, and
`docs/conventions.md` makes the vocabulary a standing crossing: *"any side can and should
update the vocab on the other side as soon as a split or modification is noticed."* The
cost of waiting is measured -- `evidence/rename-left-history-in-the-comments/`, where a
rename that stopped at the code left 32 quoted rulings and 31 uses of a retired word past
six green gates.

! **`collate` NEEDS NO NEW RULING.** `docs/vocabulary.md:97-99` already records it as FREE
for exactly this sense: *"stage 2 was `COLLATE` and is GATHER since 2026-08-23 ... so
`collate` is available for its trade meaning, transferring every hand's marks onto one
proof."*

- [ ] **Step 1: Add `distribute` to `docs/vocabulary.md`**

In the settled-terms table, beside `collate`:

```markdown
| **distribute** | handing each role its own `edit_copy` of the binder -- the broadcast half of one round | **`flows/distribute.py`**, ruled 2026-08-30. Roy: *"the broadcasting part seems like distribute, the bringin back together seems like collate."* It was `flows/marks.py`, named for the artifact it carried rather than the act it performs |
```

- [ ] **Step 2: Add it to the shipped vocabulary**

Add the matching entry to `src/comment_review/references/vocabulary.toml`, in the same
form as its neighbours. Read two existing entries first and match them exactly rather than
inventing a field.

- [ ] **Step 3: Run the vocabulary checks**

```bash
uv run python scripts/check_vocabulary.py
uv run python scripts/vocabulary_sweep.py
```

`check_vocabulary.py` must exit 0. `vocabulary_sweep.py` is an INPUT, not a gate -- read
its rows, and for any term it names that this plan introduced (`compose`, `drift`,
`Problem`), decide whether it is a term of art and add it if so.

- [ ] **Step 4: Build `plugins/` and prove it took**

```bash
uv run python scripts/build_plugin.py
uv run python scripts/build_plugin.py --check
```

Expected: the second exits 0.

- [ ] **Step 5: Run every gate**

```bash
uv run pytest -q
uv run ruff check .
uv run ruff format .
uv run python scripts/check_shipped_syntax.py
uv run ty check src/comment_review/
uv run python scripts/dead_sweep.py --names --links
uv run python scripts/todo_tool.py resync
```

! `ruff format` REWRITES source, so `check_shipped_syntax.py` runs AFTER it, and
`build_plugin.py` runs again if the formatter changed anything.

! `dead_sweep.py` always exits 0 and is an INPUT. Read it: this plan removed
`mark --check`, so anything that only that branch reached is now dead and should go in
this commit.

- [ ] **Step 6: Confirm the chain runs end to end with no hand-written Python**

`A-T1`'s own verify. Over a scratch tree:

```bash
uv run python src/comment-review.py census --json --repo . --out /tmp/c.json src/comment_review/desk/mark.py
uv run python src/comment-review.py distribute --seed --binder /tmp/c.json --role block-context --out /tmp/a.json
# fill /tmp/a.json by hand or with a real agent, then:
uv run python src/comment-review.py collate --stage 4c --binder /tmp/c.json --out /tmp/chief.json --edit-copy /tmp/a.json
uv run python src/comment-review.py proof --docket <docket> --repo . --out /tmp/revise
```

! Use the scratchpad directory, not `/tmp`. ! The `docket` step is `P5` in SP-4 and is not
in this plan -- stop at `collate` and record what it printed.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -F <message file>
```

---

## Self-review

**Spec coverage.** Every section of the spec maps to a task:

| spec | task |
| --- | --- |
| `P36` | 1 |
| `P34` | 3 (and 2, which makes it possible without editing a gate to pass) |
| `P35` | 4 |
| `D9` | 5 |
| `P21`, `D2` | 6 |
| `P13`, `D3` | 7 |
| `P24`, `D5` | 8 |
| `D10` | 9 |
| `P1`, `P2`, `D1`, `D4`, `D7` | 10 |
| `D8` | 11 |
| `P3`, `D6` | 12 |
| `P37` | 13 |
| vocabulary, build, gates | 14 |

**Two things the plan corrects in the spec, both measured while writing it:**

1. **`P36`'s target moved.** The spec names `desk/collator.py`; `grep -rn "Vocabulary:
   #11" src/` returns one line and it is `results/differences.py:5`. `collator.py`'s
   header was already rewritten in `e4feba0`. Task 1 fixes where the defect is, and it
   matters more than it looked: `differences.py` is the file Task 7 adds `compose` to, and
   its header says the module *"Rules on nothing."*
2. **The spec did not mention `tests/gates/test_mark_shape.py`.** It hard-codes three
   counts, so `P34` could not land without editing a test. Task 2 clears them per Roy's
   ruling and states the must-match rule in `docs/the-mark.md`.

**Type consistency.** `Problem(role, address, message)` is defined in Task 8 and used in
Tasks 9, 10 and 12 with those three names. `Collated`'s fields are declared in Task 10 and
extended once, in Task 11, with `order`. `compose`/`CannotCompose` are defined in Task 7
and used in Task 10. `Mark.seed`/`Mark.as_entry` are defined in Task 4 and used in Tasks 4
and 10. `base_texts`/`drift_in` are defined in Task 9 and used in Task 10.

**No placeholders.** Every step carries the code or the exact command it needs.
- [ ] **Step 8: Tick the boxes -- THIS STEP, in its own commit AFTER the one above**

Tick every `- [ ]` step box of this task in
`docs/superpowers/plans/2026-08-30-sp1-the-containers-and-the-collate-flow.md`

! **READ EACH BOX'S OWN VERIFY TEXT BEFORE TICKING IT.** A box is a claim and
ticking it asserts the claim. Where only part of a box is delivered, leave it open
and reword it to track the remainder -- `CLAUDE.md`'s *superseded in part*.

! **RECOMPUTE `Plan-tasks:` FROM THE BOXES**, never increment it.

! **CITE THE COMMIT FROM THE STEP ABOVE** in the tick commit's message, so a
reader can get from a ticked box to the work that closed it.

