# The Middle Rebuilt -- Implementation Plan

> For agentic workers: required sub-skill -- use superpowers:subagent-driven-development
> (recommended) or superpowers:executing-plans to implement this plan task by task. Steps
> use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the fold, the turn and the disposition of the middle with three tables of
rows, a pure evaluator over a place, a Unit of Work per fold, and a bus that pushes the stages
through -- so that a new instruction, answer or disposition is one row and every atomicity
rule is stated once.

**Architecture:** The business lives in `desk/`, in sub-packages: `marks/`, `answers/` and
`dispositions/` each hold a table of rows and the container the rows read; `evaluate/` holds
the place and the three passes; `work/` holds the Unit of Work and the events it emits. The
flows derive places from the copies and the proof, hand them to desk, and save on commit; the
commands parse, send, print the events and exit. The old fold and turn are made private as
each piece passes, then deleted with their tests.

**Tech Stack:** Python 3.11, standard library only in `src/comment_review/` (it ships);
pytest, ruff and ty through `uv run`; `scripts/smoke_middle.ps1` over `scripts/smoke_fixture.py`
as the end-to-end fixture.

**Spec:** `docs/superpowers/specs/2026-09-14-the-middle-rebuilt-design.md`

## Global Constraints

- Run everything through `uv run`: `uv run pytest -q`, `uv run ruff check .`,
  `uv run ruff format .`, `uv run ty check`, `uv run python scripts/check_shipped_syntax.py`,
  `uv run python scripts/check_vocabulary.py`. All green before each commit.
- Nothing under `src/comment_review/` imports outside the standard library.
- No `except` clause in a shipped file holds a tuple literal; bind the tuple to a name.
- `desk/` imports only leaves (`machine`, `reading`, `concordance`) and itself; it never
  imports `binder`, `docket` or `flows`. `flows/` and `commands/` may import anything.
- Edit `src/`, never `plugins/`; `plugins/` is assembled at release.
- Comments and docstrings: ASCII, no `!` markers, no runs of capitals for stress; state what
  the code does now, and cite a ruling as `decision-log.md Process: #N`.
- Commit messages and PR text go through a message file, never inline backticks or `$(`.
  Never `sed`, never a heredoc; multi-step edits are a `.py` under the job's temp dir.
- The cycle per task: work and verify, commit, then close the task's boxes on the board and
  the plan step citing that commit, then commit the ticks. Tasks and steps are closed through
  `job-board`, never by hand.
- The three real runs' copies stay in `OneDrive/comment-review-feedback` and are checked in
  nowhere; every scenario is planted on `scripts/smoke_fixture.py`.
- The vocabulary is shared: a term this plan introduces (`place`, `pass`, `stance`) is added
  to `src/comment_review/references/vocabulary.toml` and `docs/vocabulary.md` in the task
  that introduces it, or the vocabulary gate goes red.

## Rulings made while writing this plan

- A row has a sixth field, `reads`: the problems the row finds with a mark against its
  base. The spec folded refusal into `sets`; `sets` cannot refuse, so `reads` does, and the
  place's *refused* state comes from it.
- The tables gate carries a shrinking list of old modules still allowed to name a row; each
  task that replaces a module removes it from the list. The spec's step 1 asked the old code
  to read the tables at once, which is the whole rebuild.
- `MasterProof` gains one field, `places`, replacing `determined` and `unsettlable`.
  `desk/determined.py` and `desk/diff_mark.py` are deleted with `flows/turn.py`.
- The `pairs` field is the mark's stance -- proposes, abstains, unsettlable. Agree, compose
  and contest are computed by the evaluator from the proposals' texts, because they are
  properties of two texts, not of one row.

---

## File structure

| path | responsibility |
| --- | --- |
| `src/comment_review/desk/marks/__init__.py` | the package |
| `src/comment_review/desk/marks/mark.py` | `Mark`, `seed`, `serialize`, `deserialize`, `derived_change`, `ROLE_FIELDS`, `untouched`, `filled` -- moved from `desk/mark.py` |
| `src/comment_review/desk/marks/table.py` | `Row`, `Touch`, `Stance`, the seven rows in `INSTRUCTIONS`, and the `sets`/`reads`/`pairs` functions |
| `src/comment_review/desk/mark.py` | a shim re-exporting both, deleted in task 11 |
| `src/comment_review/desk/answers/__init__.py` | the package |
| `src/comment_review/desk/answers/answer.py` | `Answer`, `Question`, seed/deserialize -- what a role hands back in a turn |
| `src/comment_review/desk/answers/table.py` | `AnswerRow`, `Effect`, the eight rows in `ANSWERS` |
| `src/comment_review/desk/dispositions/__init__.py` | the package |
| `src/comment_review/desk/dispositions/disposition.py` | `Disposition`, deserialize -- what the chief rules |
| `src/comment_review/desk/dispositions/table.py` | `DispositionRow`, the rows in `DISPOSITIONS` |
| `src/comment_review/desk/evaluate/__init__.py` | the package |
| `src/comment_review/desk/evaluate/state.py` | `State`, the six |
| `src/comment_review/desk/evaluate/place.py` | `Place`, `Filed`, serialize/deserialize |
| `src/comment_review/desk/evaluate/passes.py` | `marks_pass`, `answers_pass`, `dispositions_pass`, `pair_moves`, `evaluate` |
| `src/comment_review/desk/work/__init__.py` | the package |
| `src/comment_review/desk/work/events.py` | the events a fold emits |
| `src/comment_review/desk/work/fold.py` | `Fold`, the Unit of Work |
| `src/comment_review/flows/places.py` | `places_of`: copies and bases to places; `chief_copy_of`: decided places to an `EditCopy` |
| `src/comment_review/flows/bus.py` | the messages, the handlers, `handle` |
| `src/comment_review/flows/transcribe.py` | `docket_of` over decided places |
| `src/comment_review/commands/{collate,turn,disposition}.py` | parse, send, print, exit |
| `tests/gates/test_tables_name_the_rows.py` | the gate with the shrinking list |
| `tests/test_marks_table.py`, `tests/test_answers.py`, `tests/test_dispositions.py`, `tests/test_place.py`, `tests/test_passes.py`, `tests/test_fold.py`, `tests/test_places.py`, `tests/test_bus.py` | one per new module |
| `scripts/smoke_fixture.py`, `scripts/smoke_middle.ps1` | the planted scenarios |

---

### Task 0: Found the subplan and cut its branch

**Files:**
- Modify: `docs/plans/0.2.4-the-cli-carries-a-real-run.md` (through `job-board` only)
- Create: `docs/plans/0.2.4-the-middle-rebuilt.md` (through `job-board` only)

- [ ] **Step 1: File the TODO that the subplan is founded on**

From the repo root, on `feat/the-cli-carries-a-real-run`:

```powershell
job-board todo create "The middle folds through three tables, an evaluator and a Unit of Work" --owner backend --raised-from "docs/superpowers/specs/2026-09-14-the-middle-rebuilt-design.md" --slug the-middle-rebuilt --task "Implement the marks, answers and dispositions tables under desk/, with the gate that nothing else names a row" --task "Implement the place, its six states and the three passes in desk/evaluate" --task "Implement the Unit of Work in desk/work and the bus in flows, and switch collate to it" --task "Implement the turn and disposition handlers and switch both commands to the bus" --task "Update fill, check and docket_of to read the tables; delete text_at" --task "Delete the old fold, turn, determined and diff_mark with their tests" --task "Implement a smoke plant for every row of the three tables"
```

- [ ] **Step 2: Found the subplan by moving the paused steps' tasks**

The parent's P7 to P10 and P13 are superseded by this plan; their TODO tasks move:

```powershell
job-board plan supersede 0.2.4-the-cli-carries-a-real-run P7 --statement "SUPERSEDED by 0.2.4-the-middle-rebuilt, the spec of 2026-09-14" --commit b5dd0303
job-board plan supersede 0.2.4-the-cli-carries-a-real-run P8 --statement "SUPERSEDED by 0.2.4-the-middle-rebuilt" --commit b5dd0303
job-board plan supersede 0.2.4-the-cli-carries-a-real-run P9 --statement "SUPERSEDED by 0.2.4-the-middle-rebuilt" --commit b5dd0303
job-board plan supersede 0.2.4-the-cli-carries-a-real-run P10 --statement "SUPERSEDED by 0.2.4-the-middle-rebuilt" --commit b5dd0303
job-board plan supersede 0.2.4-the-cli-carries-a-real-run P13 --statement "SUPERSEDED by 0.2.4-the-middle-rebuilt" --commit b5dd0303
job-board plan supersede 0.2.4-the-cli-carries-a-real-run P14 --statement "SUPERSEDED by 0.2.4-the-middle-rebuilt" --commit b5dd0303
job-board plan move-t 0.2.4-the-cli-carries-a-real-run BT25 --to 0.2.4-the-middle-rebuilt --title "The middle rebuilt" --objective "The fold, the turn and the disposition run through three tables of rows, a pure evaluator over a place, and a Unit of Work per fold, so a new instruction is one row and every atomicity rule is stated once"
```

Then move the rest, reading each tag off `job-board plan show 0.2.4-the-cli-carries-a-real-run`: mark-defects T26, no-command-for-the-middle T98, agents-files T27, T40 and T41, staged-chain-untested T5, and smoke-drives-one-route T6 and T9. Add the new TODO's tasks with `plan add-t 0.2.4-the-middle-rebuilt the-middle-rebuilt.md:T1` through `T7`. Add one P step per task of this plan, in this plan's order, each ending "commit, tick, commit".

- [ ] **Step 3: Cut the branch and commit the plan**

```powershell
git switch -c feat/the-middle-rebuilt
git add TODO docs/plans docs/superpowers/plans/2026-09-14-the-middle-rebuilt.md
git commit -F <message file: "plan: 0.2.4-the-middle-rebuilt, founded on the spec of 2026-09-14">
```

---

### Task 1: The marks table

**Files:**
- Create: `src/comment_review/desk/marks/__init__.py`, `src/comment_review/desk/marks/table.py`
- Move: `src/comment_review/desk/mark.py` to `src/comment_review/desk/marks/mark.py` (`git mv`), then recreate `desk/mark.py` as a shim
- Create: `tests/test_marks_table.py`, `tests/gates/test_tables_name_the_rows.py`
- Modify: `src/comment_review/references/vocabulary.toml`, `docs/vocabulary.md` (add `stance`, `touch`)

**Interfaces:**
- Produces: `Touch` (`own`, `origin`, `destination`), `Stance` (`proposes`, `abstains`, `unsettlable`), `Row`, `INSTRUCTIONS: dict[Instruction, Row]`, and on `Row`: `sets(mark, touch, base) -> str | None`, `reads(mark, touch, base) -> list[str]`, `pairs(mark) -> Stance`, `touches: tuple[Touch, ...]`, `answers: tuple[str, ...]`. `None` from `sets` means the mark sets nothing here; `""` means delete.
- Consumes: today's `Mark` (fields `address`, `anchor`, `raw_text`, `instruction`, `claim`, `reason`, `sources`, `change`).

- [ ] **Step 1: Move the module into the package**

```powershell
New-Item -ItemType Directory src/comment_review/desk/marks
git mv src/comment_review/desk/mark.py src/comment_review/desk/marks/mark.py
```

Write `src/comment_review/desk/marks/__init__.py` as an empty module with a one-line docstring: `"""What a role files: the mark, and the table of rows that read it."""`.

- [ ] **Step 2: Write the failing tests for the rows**

`tests/test_marks_table.py`:

```python
"""The marks table: what each row sets, refuses and pairs as."""

from comment_review.desk.marks.mark import Instruction, Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Stance, Touch


def _mark(instruction: Instruction, **fields) -> Mark:
    base = {
        "address": "m.py@b1",
        "anchor": "x = 1",
        "raw_text": "# one\n# two\n# three\n",
        "instruction": instruction,
        "claim": {},
        "reason": "a reason",
        "sources": (),
        "change": "",
    }
    base.update(fields)
    return Mark(**base)


BASE = "# one\n# two\n# three\n"


def test_a_clean_and_a_query_set_nothing_anywhere():
    for instruction in (Instruction.CLEAN, Instruction.QUERY):
        row = INSTRUCTIONS[instruction]
        assert row.touches == (Touch.OWN,)
        assert row.sets(_mark(instruction), Touch.OWN, BASE) is None


def test_a_correct_sets_its_derived_change():
    row = INSTRUCTIONS[Instruction.CORRECT]
    mark = _mark(Instruction.CORRECT, change="# one\n# 2\n# three\n")
    assert row.sets(mark, Touch.OWN, BASE) == "# one\n# 2\n# three\n"


def test_a_drop_of_the_whole_paragraph_sets_a_delete():
    row = INSTRUCTIONS[Instruction.DROP]
    assert row.sets(_mark(Instruction.DROP, change=""), Touch.OWN, BASE) == ""


def test_a_move_sets_the_remainder_at_the_origin_and_raw_text_at_the_destination():
    """Process #172 and #175: change is the snippet, raw_text the destination
    paragraph as it will read."""
    row = INSTRUCTIONS[Instruction.MOVE]
    mark = _mark(
        Instruction.MOVE,
        claim={"from": "m.py@b1", "to": "m.py@b5"},
        change="# two\n",
        raw_text="# four\n# two\n# five\n",
    )
    assert row.touches == (Touch.ORIGIN, Touch.DESTINATION)
    assert row.sets(mark, Touch.ORIGIN, BASE) == "# one\n# three\n"
    assert row.sets(mark, Touch.DESTINATION, "# four\n# five\n") == "# four\n# two\n# five\n"


def test_a_move_whose_snippet_is_not_in_the_origin_once_is_refused_by_reads():
    row = INSTRUCTIONS[Instruction.MOVE]
    mark = _mark(Instruction.MOVE, claim={"from": "m.py@b1", "to": "m.py@b5"}, change="# six\n")
    assert row.reads(mark, Touch.ORIGIN, BASE) == [
        "the snippet is not in the origin's paragraph: '# six\\n'"
    ]


def test_a_moves_destination_text_must_keep_every_word_of_the_snippet_and_the_base():
    row = INSTRUCTIONS[Instruction.MOVE]
    mark = _mark(
        Instruction.MOVE,
        claim={"from": "m.py@b1", "to": "m.py@b5"},
        change="# two\n",
        raw_text="# four\n# five\n",
    )
    assert row.reads(mark, Touch.DESTINATION, "# four\n# five\n") == [
        "the destination text does not keep 'two'"
    ]


def test_an_add_sets_its_raw_text_and_keeps_the_prose_already_there():
    """Process #176 and #132."""
    row = INSTRUCTIONS[Instruction.ADD]
    mark = _mark(
        Instruction.ADD,
        claim={"missing": "why", "anchor": "`x`"},
        change="# why\n",
        raw_text="# one\n# why\n# two\n# three\n",
    )
    assert row.sets(mark, Touch.OWN, BASE) == mark.raw_text
    assert row.reads(mark, Touch.OWN, BASE) == []
    dropping = _mark(Instruction.ADD, claim=mark.claim, change="# why\n", raw_text="# why\n# one\n")
    assert row.reads(dropping, Touch.OWN, BASE) == ["the text does not keep 'two'"]


def test_stances():
    from comment_review.desk.marks.mark import Shape

    assert INSTRUCTIONS[Instruction.CLEAN].pairs(_mark(Instruction.CLEAN)) is Stance.ABSTAINS
    assert INSTRUCTIONS[Instruction.CORRECT].pairs(_mark(Instruction.CORRECT)) is Stance.PROPOSES
    deferring = _mark(Instruction.QUERY, claim={"shape": str(Shape.OUTSIDE_MY_ROLE)})
    human = _mark(Instruction.QUERY, claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)})
    assert INSTRUCTIONS[Instruction.QUERY].pairs(deferring) is Stance.ABSTAINS
    assert INSTRUCTIONS[Instruction.QUERY].pairs(human) is Stance.UNSETTLABLE


def test_every_row_names_the_answers_a_turn_may_give_on_it():
    for instruction, row in INSTRUCTIONS.items():
        if row.pairs(_mark(instruction)) is Stance.PROPOSES:
            assert set(row.answers) == {"hold", "withdraw", "correct", "patch"}, instruction
```

- [ ] **Step 3: Run the tests to see them fail**

Run: `uv run pytest -q tests/test_marks_table.py`
Expected: FAIL at import -- no module `comment_review.desk.marks.table`.

- [ ] **Step 4: Write the table**

`src/comment_review/desk/marks/table.py`:

```python
"""The marks table: one row per instruction, and every reader asks the row.

A row says what a mark's claim carries, which places the mark touches, what
text it sets at each, what problems it has against its base, how it pairs
with other marks at a place, and which answers a turn may give on it. Nothing
outside this module names an instruction; a gate holds that.

`sets` returns None where the mark sets nothing (`decision-log.md Process:
#174`), "" for a delete, else the text. `reads` returns the problems the row
finds; `flows.fill` runs it before a mark is placed and the evaluator before
it is folded, so a mark reaching the evaluator has been read.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

from comment_review.desk.marks.mark import Instruction, Shape, first_word_dropped


class Touch(StrEnum):
    """Which of the places a mark writes is being asked about."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    OWN = auto()
    ORIGIN = auto()
    DESTINATION = auto()


class Stance(StrEnum):
    """How a mark stands toward the other marks at its place."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    PROPOSES = auto()
    ABSTAINS = auto()
    UNSETTLABLE = auto()


Sets = Callable[[Any, Touch, str], str | None]
Reads = Callable[[Any, Touch, str], list[str]]
Pairs = Callable[[Any], Stance]


def _nothing(mark, touch, base):
    return None


def _no_problems(mark, touch, base):
    return []


def _the_change(mark, touch, base):
    return mark.change


def _the_raw_text(mark, touch, base):
    return mark.raw_text


def _without_once(base: str, snippet: str) -> str | None:
    if snippet and base.count(snippet) == 1:
        return base.replace(snippet, "")
    return None


def _move_sets(mark, touch, base):
    if touch is Touch.ORIGIN:
        return _without_once(base, mark.change)
    return mark.raw_text


def _move_reads(mark, touch, base):
    if touch is Touch.ORIGIN:
        if _without_once(base, mark.change) is None:
            return [f"the snippet is not in the origin's paragraph: {mark.change!r}"]
        return []
    dropped = first_word_dropped(base, mark.raw_text)
    if dropped is not None:
        return [f"the destination text does not keep {dropped!r}"]
    dropped = first_word_dropped(mark.change, mark.raw_text)
    if dropped is not None:
        return [f"the destination text does not keep {dropped!r}"]
    return []


def _add_reads(mark, touch, base):
    for held in (base, mark.change):
        dropped = first_word_dropped(held, mark.raw_text)
        if dropped is not None:
            return [f"the text does not keep {dropped!r}"]
    return []


def _proposes(mark):
    return Stance.PROPOSES


def _abstains(mark):
    return Stance.ABSTAINS


def _query_stance(mark):
    if mark.claim.get("shape") == str(Shape.HUMAN_REVIEW_NECESSARY):
        return Stance.UNSETTLABLE
    return Stance.ABSTAINS


ESCALATION_ANSWERS = ("hold", "withdraw", "correct", "patch")


@dataclass(frozen=True)
class Row:
    """One instruction, as every reader sees it."""

    claim_all: tuple[str, ...] = ()
    quotes_original: str = ""
    touches: tuple[Touch, ...] = (Touch.OWN,)
    sets: Sets = _nothing
    reads: Reads = _no_problems
    pairs: Pairs = _proposes
    answers: tuple[str, ...] = ESCALATION_ANSWERS
    owes_change: bool = True
    owes_sources: bool = True
    substantive: bool = True
    may_empty: bool = False
    needs_anchor: bool = False

    @property
    def owes_destination(self) -> bool:
        return Touch.DESTINATION in self.touches


INSTRUCTIONS: dict[Instruction, Row] = {
    Instruction.CLEAN: Row(
        pairs=_abstains, answers=(), owes_change=False, owes_sources=False, substantive=False
    ),
    Instruction.QUERY: Row(
        claim_all=("shape", "attempted", "settles"),
        pairs=_query_stance,
        answers=(),
        owes_change=False,
    ),
    Instruction.DROP: Row(
        claim_all=("drop",), quotes_original="drop", sets=_the_change, may_empty=True
    ),
    Instruction.CORRECT: Row(
        claim_all=("false", "true"), quotes_original="false", sets=_the_change
    ),
    Instruction.PATCH: Row(
        claim_all=("from", "to"), quotes_original="from", sets=_the_change, owes_sources=False
    ),
    Instruction.ADD: Row(
        claim_all=("missing", "anchor"),
        sets=_the_raw_text,
        reads=_add_reads,
        needs_anchor=True,
    ),
    Instruction.MOVE: Row(
        claim_all=("from", "to"),
        touches=(Touch.ORIGIN, Touch.DESTINATION),
        sets=_move_sets,
        reads=_move_reads,
    ),
}
```

`first_word_dropped` lives in `flows/fill.py` today; move it into `desk/marks/mark.py` (it is a pure text function, `desk` may hold it) and leave `flows/fill.py` importing it from there. Delete the `Row` class and `INSTRUCTIONS` from `desk/marks/mark.py`, and have `mark.py` import `INSTRUCTIONS` and `Row` from `table` inside `Mark.deserialize` (a function-level import, to avoid the cycle) -- or move `deserialize`'s row reads to take the row as a parameter. The function-level import is the smaller change; do that.

- [ ] **Step 5: Write the shim**

`src/comment_review/desk/mark.py`:

```python
"""Shim: `desk.mark` moved to `desk.marks`. Deleted when the old readers go."""

from comment_review.desk.marks.mark import *  # noqa: F401,F403
from comment_review.desk.marks.mark import (  # noqa: F401
    ROLE_FIELDS,
    Instruction,
    Mark,
    Shape,
    derived_change,
    filled,
    text_at,
    untouched,
)
from comment_review.desk.marks.table import INSTRUCTIONS, Row  # noqa: F401
```

- [ ] **Step 6: Run the tests**

Run: `uv run pytest -q tests/test_marks_table.py tests/test_mark.py tests/test_fill.py`
Expected: PASS. Then `uv run pytest -q`: PASS, same count as before plus the new file.

- [ ] **Step 7: Write the gate**

`tests/gates/test_tables_name_the_rows.py`:

```python
"""Nothing outside the three tables names a row.

The list below is the old middle, still allowed to name an instruction, an
answer or a disposition while its replacement is built. Each task of
docs/superpowers/plans/2026-09-14-the-middle-rebuilt.md removes the modules
it replaces; the list is empty when the rebuild is done, and a module added
to it afterward is the defect this gate exists to refuse.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "src" / "comment_review"
TABLES = {
    ROOT / "desk" / "marks" / "table.py",
    ROOT / "desk" / "answers" / "table.py",
    ROOT / "desk" / "dispositions" / "table.py",
}
#: Modules the rebuild has not replaced yet. Shrinks; never grows.
STILL_OLD = {
    "desk/marks/mark.py",
    "desk/mark.py",
    "desk/collator.py",
    "desk/containers.py",
    "desk/determined.py",
    "desk/diff_mark.py",
    "flows/collate.py",
    "flows/fill.py",
    "flows/transcribe.py",
    "flows/turn.py",
    "commands/mark.py",
}
NAMES = re.compile(
    r"\bInstruction\.[A-Z_]+\b|\bDiffInstruction\.[A-Z_]+\b|\bAnswer\.[A-Z_]+\b"
    r"|\"(taken_in|recast|stet|hold|withdraw)\""
)


class TestOnlyTheTablesNameARow(unittest.TestCase):
    def test_no_new_module_names_a_row(self):
        offenders = []
        for path in ROOT.rglob("*.py"):
            rel = path.relative_to(ROOT).as_posix()
            if path in TABLES or rel in STILL_OLD:
                continue
            if NAMES.search(path.read_text(encoding="utf-8")):
                offenders.append(rel)
        self.assertEqual(offenders, [])

    def test_the_old_list_names_only_modules_that_still_name_a_row(self):
        stale = [
            rel
            for rel in STILL_OLD
            if not (ROOT / rel).exists()
            or not NAMES.search((ROOT / rel).read_text(encoding="utf-8"))
        ]
        self.assertEqual(stale, [], "remove these from STILL_OLD")
```

Run: `uv run pytest -q tests/gates/test_tables_name_the_rows.py`. Expected: PASS. If the first test names an offender not in the list, that module is old middle the list missed: add it, and note it in the commit message.

- [ ] **Step 8: Vocabulary, gates, commit**

Add `stance` and `touch` to `references/vocabulary.toml` under the desk's terms and to `docs/vocabulary.md`. Run every gate in Global Constraints. Commit: `feat: the marks table -- one row per instruction, and the gate that nothing else names one`. Then close `the-middle-rebuilt.md T1` and this plan's step on the board against that commit, and commit the ticks.

---

### Task 2: The answers table and the dispositions table

**Files:**
- Create: `src/comment_review/desk/answers/__init__.py`, `answer.py`, `table.py`
- Create: `src/comment_review/desk/dispositions/__init__.py`, `disposition.py`, `table.py`
- Create: `src/comment_review/desk/evaluate/__init__.py`, `state.py`
- Create: `tests/test_answers.py`, `tests/test_dispositions.py`
- Modify: `tests/gates/test_tables_name_the_rows.py` (no change to the list yet)

**Interfaces:**
- Produces: `State` (`stands`, `agreed`, `composed`, `contested`, `unsettlable`, `refused`); `Question` (`escalation`, `composition`); `Answer` dataclass with `address`, `anchor`, `question`, `name`, `reason`, `change`, `claim`, `sources`, and `Answer.deserialize(where, entry) -> tuple[Answer | None, list[str]]`; `Effect` (`keeps`, `removes`, `replaces`, `accepts`, `abstains`, `unsettlable`); `AnswerRow` with `question`, `effect(answer) -> Effect`, `owes_change`; `ANSWERS: dict[tuple[Question, str], AnswerRow]`; `Disposition` dataclass with `address`, `name`, `side`, `prose`, `reason`, and `deserialize`; `DispositionRow` with `closes: frozenset[State]`, `owes: tuple[str, ...]`, `sets(disposition, base, sides) -> str | None`; `DISPOSITIONS: dict[str, DispositionRow]`.

- [ ] **Step 1: Write the failing tests**

`tests/test_answers.py`:

```python
"""The answers table: what a role's answer in a turn does to its own proposal."""

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.answers.table import ANSWERS, Effect


def _answer(question: Question, name: str, **fields) -> Answer:
    base = {
        "address": "m.py@b1",
        "anchor": "x = 1",
        "question": question,
        "name": name,
        "reason": "a reason",
        "change": "",
        "claim": {},
        "sources": (),
    }
    base.update(fields)
    return Answer(**base)


def test_the_escalation_answers():
    e = Question.ESCALATION
    assert ANSWERS[(e, "hold")].effect(_answer(e, "hold")) is Effect.KEEPS
    assert ANSWERS[(e, "withdraw")].effect(_answer(e, "withdraw")) is Effect.REMOVES
    assert ANSWERS[(e, "correct")].effect(_answer(e, "correct", change="# x")) is Effect.REPLACES
    assert ANSWERS[(e, "patch")].owes_change is True
    assert ANSWERS[(e, "hold")].owes_change is False


def test_the_composition_answers():
    c = Question.COMPOSITION
    assert ANSWERS[(c, "clean")].effect(_answer(c, "clean")) is Effect.ACCEPTS
    deferring = _answer(c, "query", claim={"shape": "outside-my-role"})
    human = _answer(c, "query", claim={"shape": "human-review-necessary"})
    assert ANSWERS[(c, "query")].effect(deferring) is Effect.ABSTAINS
    assert ANSWERS[(c, "query")].effect(human) is Effect.UNSETTLABLE
    assert ANSWERS[(c, "correct")].effect(_answer(c, "correct", change="# x")) is Effect.REPLACES


def test_an_answer_is_read_against_its_question():
    got, why = Answer.deserialize(
        "m.py@b1",
        {"address": "m.py@b1", "question": "escalation", "instruction": "hold", "reason": "r"},
    )
    assert why == [] and got is not None and got.name == "hold"
    got, why = Answer.deserialize(
        "m.py@b1",
        {"address": "m.py@b1", "question": "escalation", "instruction": "clean", "reason": "r"},
    )
    assert got is None and "not an answer to an escalation" in why[0]
    got, why = Answer.deserialize(
        "m.py@b1",
        {"address": "m.py@b1", "question": "escalation", "instruction": "correct", "reason": "r"},
    )
    assert got is None and "needs a `change`" in why[0]
```

`tests/test_dispositions.py`:

```python
"""The dispositions table: what the chief may close, and what text it sets."""

from comment_review.desk.dispositions.disposition import Disposition
from comment_review.desk.dispositions.table import DISPOSITIONS
from comment_review.desk.evaluate.state import State


def test_taken_in_closes_a_carried_place_with_one_sides_text_or_the_original():
    row = DISPOSITIONS["taken_in"]
    assert row.closes == frozenset({State.COMPOSED, State.CONTESTED})
    sides = {"block-context": "# theirs\n", "module-context": "# ours\n"}
    ours = Disposition(address="m.py@b1", name="taken_in", side="module-context", prose="", reason="r")
    assert row.sets(ours, "# base\n", sides) == "# ours\n"
    original = Disposition(address="m.py@b1", name="taken_in", side="original", prose="", reason="r")
    assert row.sets(original, "# base\n", sides) is None


def test_recast_sets_the_chiefs_prose():
    row = DISPOSITIONS["recast"]
    recast = Disposition(address="m.py@b1", name="recast", side="copy-chief", prose="# mine\n", reason="r")
    assert row.sets(recast, "# base\n", {}) == "# mine\n"
    assert row.owes == ("prose",)


def test_no_disposition_closes_an_unsettlable_place():
    for row in DISPOSITIONS.values():
        assert State.UNSETTLABLE not in row.closes


def test_a_disposition_is_read_by_name():
    got, why = Disposition.deserialize(
        "m.py@b1", {"address": "m.py@b1", "answer": "taken_in", "side": "original", "reason": "r"}
    )
    assert why == [] and got is not None
    got, why = Disposition.deserialize("m.py@b1", {"address": "m.py@b1", "answer": "recast", "reason": "r"})
    assert got is None and "needs `prose`" in why[0]
    got, why = Disposition.deserialize("m.py@b1", {"address": "m.py@b1", "answer": "correct", "reason": "r"})
    assert got is None and "a role's answer" in why[0]
```

- [ ] **Step 2: Run them to see them fail**

Run: `uv run pytest -q tests/test_answers.py tests/test_dispositions.py`
Expected: FAIL at import.

- [ ] **Step 3: Write `desk/evaluate/state.py`**

```python
"""The six states a place can be in once evaluated."""

from enum import StrEnum, auto


class State(StrEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    STANDS = auto()
    AGREED = auto()
    COMPOSED = auto()
    CONTESTED = auto()
    UNSETTLABLE = auto()
    REFUSED = auto()


#: The states a fold carries forward for a turn or the chief.
CARRIED = frozenset({State.COMPOSED, State.CONTESTED})
```

- [ ] **Step 4: Write `desk/answers/answer.py`**

```python
"""What a role hands back in a turn: one answer to one question at one place."""

from dataclasses import dataclass, fields
from enum import StrEnum, auto

from comment_review.desk.marks.mark import filled


class Question(StrEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    ESCALATION = auto()
    COMPOSITION = auto()


@dataclass(frozen=True)
class Answer:
    """One answer. `name` is the answer's row; `instruction` on the wire."""

    address: str
    anchor: str
    question: Question
    name: str
    reason: str
    change: str = ""
    claim: dict = None  # type: ignore[assignment]
    sources: tuple = ()

    def __post_init__(self):
        if self.claim is None:
            object.__setattr__(self, "claim", {})

    def serialize(self) -> dict:
        out = {f.name: getattr(self, f.name) for f in fields(self)}
        out["question"] = str(self.question)
        out["instruction"] = out.pop("name")
        out["sources"] = list(self.sources)
        return out

    @classmethod
    def deserialize(cls, where: str, entry: object) -> "tuple[Answer | None, list[str]]":
        from comment_review.desk.answers.table import ANSWERS

        if not isinstance(entry, dict):
            return None, [f"{where}: an answer must be an object"]
        data: dict = entry
        try:
            question = Question(str(data.get("question")))
        except ValueError:
            return None, [f"{where}: `question` must be one of {', '.join(Question)}"]
        name = data.get("instruction")
        row = ANSWERS.get((question, str(name)))
        if row is None:
            return None, [f"{where}: {name!r} is not an answer to {question}"]
        out = []
        if not filled(data.get("address")):
            out.append(f"{where}: {name} needs the `address`")
        if not filled(data.get("reason")):
            out.append(f"{where}: {name} needs a `reason`")
        if row.owes_change and not filled(data.get("change")):
            out.append(f"{where}: {name} needs a `change`")
        if out:
            return None, out
        claim = data.get("claim")
        sources = data.get("sources")
        return (
            cls(
                address=str(data.get("address") or ""),
                anchor=str(data.get("anchor") or ""),
                question=question,
                name=str(name),
                reason=str(data.get("reason") or ""),
                change=str(data.get("change") or ""),
                claim=dict(claim) if isinstance(claim, dict) else {},
                sources=tuple(sources) if isinstance(sources, list) else (),
            ),
            [],
        )
```

- [ ] **Step 5: Write `desk/answers/table.py`**

```python
"""The answers table: eight rows, four per question."""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

from comment_review.desk.answers.answer import Question


class Effect(StrEnum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    KEEPS = auto()
    REMOVES = auto()
    REPLACES = auto()
    ACCEPTS = auto()
    ABSTAINS = auto()
    UNSETTLABLE = auto()


def _always(effect: Effect) -> Callable[[Any], Effect]:
    return lambda answer: effect


def _query_effect(answer) -> Effect:
    if answer.claim.get("shape") == "human-review-necessary":
        return Effect.UNSETTLABLE
    return Effect.ABSTAINS


@dataclass(frozen=True)
class AnswerRow:
    question: Question
    effect: Callable[[Any], Effect]
    owes_change: bool = False


ANSWERS: dict[tuple[Question, str], AnswerRow] = {
    (Question.ESCALATION, "hold"): AnswerRow(Question.ESCALATION, _always(Effect.KEEPS)),
    (Question.ESCALATION, "withdraw"): AnswerRow(Question.ESCALATION, _always(Effect.REMOVES)),
    (Question.ESCALATION, "correct"): AnswerRow(Question.ESCALATION, _always(Effect.REPLACES), True),
    (Question.ESCALATION, "patch"): AnswerRow(Question.ESCALATION, _always(Effect.REPLACES), True),
    (Question.COMPOSITION, "clean"): AnswerRow(Question.COMPOSITION, _always(Effect.ACCEPTS)),
    (Question.COMPOSITION, "query"): AnswerRow(Question.COMPOSITION, _query_effect),
    (Question.COMPOSITION, "correct"): AnswerRow(Question.COMPOSITION, _always(Effect.REPLACES), True),
    (Question.COMPOSITION, "patch"): AnswerRow(Question.COMPOSITION, _always(Effect.REPLACES), True),
}
```

- [ ] **Step 6: Write `desk/dispositions/disposition.py` and `table.py`**

`disposition.py`:

```python
"""What the chief rules at a carried-forward place."""

from dataclasses import dataclass, fields

from comment_review.desk.marks.mark import filled

ORIGINAL = "original"
CHIEF = "copy-chief"


@dataclass(frozen=True)
class Disposition:
    address: str
    name: str
    side: str
    prose: str
    reason: str

    def serialize(self) -> dict:
        out = {f.name: getattr(self, f.name) for f in fields(self)}
        out["answer"] = out.pop("name")
        return out

    @classmethod
    def deserialize(cls, where: str, entry: object) -> "tuple[Disposition | None, list[str]]":
        from comment_review.desk.answers.table import ANSWERS
        from comment_review.desk.dispositions.table import DISPOSITIONS
        from comment_review.desk.marks.table import INSTRUCTIONS

        if not isinstance(entry, dict):
            return None, [f"{where}: a ruling must be an object"]
        data: dict = entry
        name = str(data.get("answer"))
        if name in INSTRUCTIONS or any(name == n for _, n in ANSWERS):
            return None, [f"{where}: `{name}` is a role's answer; the chief's ruling is owed here"]
        row = DISPOSITIONS.get(name)
        if row is None:
            return None, [f"{where}: `answer` must be one of {', '.join(sorted(DISPOSITIONS))}"]
        out = []
        if not filled(data.get("address")):
            out.append(f"{where}: {name} needs the `address`")
        if not filled(data.get("reason")):
            out.append(f"{where}: {name} needs a `reason`")
        for key in row.owes:
            if not filled(data.get(key)):
                out.append(f"{where}: {name} needs `{key}`")
        if out:
            return None, out
        return (
            cls(
                address=str(data.get("address") or ""),
                name=name,
                side=str(data.get("side") or (CHIEF if name == "recast" else "")),
                prose=str(data.get("prose") or ""),
                reason=str(data.get("reason") or ""),
            ),
            [],
        )
```

`table.py`:

```python
"""The dispositions table: what the chief may close, and the text it sets."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from comment_review.desk.dispositions.disposition import ORIGINAL
from comment_review.desk.evaluate.state import CARRIED, State

Sets = Callable[[Any, str, dict[str, str]], str | None]


def _a_sides_text(disposition, base, sides):
    if disposition.side == ORIGINAL:
        return None
    return sides[disposition.side]


def _the_prose(disposition, base, sides):
    return disposition.prose


@dataclass(frozen=True)
class DispositionRow:
    closes: frozenset[State]
    owes: tuple[str, ...]
    sets: Sets


DISPOSITIONS: dict[str, DispositionRow] = {
    "taken_in": DispositionRow(CARRIED, ("side",), _a_sides_text),
    "recast": DispositionRow(CARRIED, ("prose",), _the_prose),
}
```

- [ ] **Step 7: Run the tests, the gate, and every gate; commit**

Run: `uv run pytest -q`. Expected: PASS. The tables gate's first test must still pass: the new modules name rows only inside the three `table.py` files and their containers' `deserialize` (which name no row -- they look rows up by string). If `answer.py` or `disposition.py` trips the gate, move the string it names into its table as a constant and import that.

Commit: `feat: the answers and dispositions tables, and the six states of a place`. Tick T1's remaining half and the plan step; commit the ticks.

---

### Task 3: The place and the marks pass

**Files:**
- Create: `src/comment_review/desk/evaluate/place.py`, `src/comment_review/desk/evaluate/passes.py`
- Create: `tests/test_place.py`, `tests/test_passes.py`

**Interfaces:**
- Produces: `Filed(role, mark, touch)`; `Place(address, anchor, base, filed, answers, disposition, state, text, reasons, question, partner)` with `serialize()`/`deserialize(where, entry)`, `proposals() -> dict[str, str | None]` (role to the text that role's mark sets here, only for proposing marks); `marks_pass(place) -> Place`; `pair_moves(places: dict[str, Place]) -> None`.
- Consumes: `INSTRUCTIONS`, `Touch`, `Stance`, `State`, `results.differences.compose`/`CannotCompose` (the composition of two proposals on different sentences, which exists today).

- [ ] **Step 1: Write the failing tests**

`tests/test_passes.py` (the place tests go in `tests/test_place.py` and cover serialize round-trip and `proposals()`; write them the same way):

```python
"""The marks pass: from the marks filed at a place to its state and text."""

from comment_review.desk.evaluate.passes import marks_pass, pair_moves
from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Instruction, Mark, Shape
from comment_review.desk.marks.table import Touch

BASE = "# one\n# two\n# three\n"


def _mark(instruction, change="", raw_text=BASE, claim=None, address="m.py@b1"):
    return Mark(
        address=address, anchor="x = 1", raw_text=raw_text, instruction=instruction,
        claim=claim or {}, reason="r", sources=(), change=change,
    )


def _place(*filed: Filed, base=BASE, address="m.py@b1") -> Place:
    return Place(address=address, anchor="x = 1", base=base, filed=list(filed))


def test_an_all_clean_place_stands_on_its_base():
    place = _place(Filed("a", _mark(Instruction.CLEAN), Touch.OWN), Filed("b", _mark(Instruction.CLEAN), Touch.OWN))
    got = marks_pass(place)
    assert got.state is State.STANDS and got.text is None


def test_a_lone_proposal_stands():
    place = _place(
        Filed("a", _mark(Instruction.CORRECT, change="# one\n# 2\n# three\n", claim={"false": "two", "true": "2"}), Touch.OWN),
        Filed("b", _mark(Instruction.CLEAN), Touch.OWN),
    )
    got = marks_pass(place)
    assert got.state is State.STANDS and got.text == "# one\n# 2\n# three\n"


def test_two_proposals_of_one_text_agree():
    corr = _mark(Instruction.CORRECT, change="# one\n# 2\n# three\n", claim={"false": "two", "true": "2"})
    patch = _mark(Instruction.PATCH, change="# one\n# 2\n# three\n", claim={"from": "two", "to": "2"})
    got = marks_pass(_place(Filed("a", corr, Touch.OWN), Filed("b", patch, Touch.OWN)))
    assert got.state is State.AGREED and got.text == "# one\n# 2\n# three\n"


def test_two_proposals_on_one_sentence_contest():
    a = _mark(Instruction.CORRECT, change="# one\n# 2\n# three\n", claim={"false": "two", "true": "2"})
    b = _mark(Instruction.CORRECT, change="# one\n# II\n# three\n", claim={"false": "two", "true": "II"})
    got = marks_pass(_place(Filed("a", a, Touch.OWN), Filed("b", b, Touch.OWN)))
    assert got.state is State.CONTESTED and got.text is None
    assert got.sides == {"a": "# one\n# 2\n# three\n", "b": "# one\n# II\n# three\n"}


def test_two_proposals_on_different_sentences_compose():
    a = _mark(Instruction.CORRECT, change="# 1\n# two\n# three\n", claim={"false": "one", "true": "1"})
    b = _mark(Instruction.CORRECT, change="# one\n# two\n# 3\n", claim={"false": "three", "true": "3"})
    got = marks_pass(_place(Filed("a", a, Touch.OWN), Filed("b", b, Touch.OWN)))
    assert got.state is State.COMPOSED and got.text == "# 1\n# two\n# 3\n"


def test_a_human_review_query_makes_the_place_unsettlable_whatever_else_is_there():
    q = _mark(Instruction.QUERY, claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)})
    c = _mark(Instruction.CORRECT, change="# one\n# 2\n# three\n", claim={"false": "two", "true": "2"})
    got = marks_pass(_place(Filed("a", q, Touch.OWN), Filed("b", c, Touch.OWN)))
    assert got.state is State.UNSETTLABLE


def test_a_mark_its_row_cannot_read_refuses_the_place_and_names_the_role():
    move = _mark(Instruction.MOVE, change="# six\n", claim={"from": "m.py@b1", "to": "m.py@b5"})
    got = marks_pass(_place(Filed("a", move, Touch.ORIGIN)))
    assert got.state is State.REFUSED
    assert got.reasons == ("a: the snippet is not in the origin's paragraph: '# six\\n'",)


def test_a_moves_two_places_take_one_state():
    move = _mark(Instruction.MOVE, change="# two\n", raw_text="# four\n# two\n# five\n", claim={"from": "m.py@b1", "to": "m.py@b5"})
    origin = marks_pass(_place(Filed("a", move, Touch.ORIGIN)))
    other = _mark(Instruction.CORRECT, change="# four\n# 5\n", claim={"false": "five", "true": "5"}, address="m.py@b5")
    destination = marks_pass(_place(Filed("a", move, Touch.DESTINATION), Filed("b", other, Touch.OWN), base="# four\n# five\n", address="m.py@b5"))
    origin.partner, destination.partner = "m.py@b5", "m.py@b1"
    places = {"m.py@b1": origin, "m.py@b5": destination}
    pair_moves(places)
    assert places["m.py@b1"].state is State.CONTESTED
    assert places["m.py@b5"].state is State.CONTESTED
```

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest -q tests/test_passes.py tests/test_place.py`. Expected: FAIL at import.

- [ ] **Step 3: Write `desk/evaluate/place.py`**

```python
"""A place: the aggregate the middle decides."""

from dataclasses import dataclass, field

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.dispositions.disposition import Disposition
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Stance, Touch


@dataclass
class Filed:
    role: str
    mark: Mark
    touch: Touch


@dataclass
class Place:
    address: str
    anchor: str
    base: str
    filed: list[Filed] = field(default_factory=list)
    answers: dict[int, dict[str, Answer]] = field(default_factory=dict)
    disposition: Disposition | None = None
    state: State | None = None
    text: str | None = None
    sides: dict[str, str] = field(default_factory=dict)
    reasons: tuple[str, ...] = ()
    question: Question | None = None
    partner: str | None = None

    def proposals(self) -> dict[str, str | None]:
        """Role -> the text that role's proposing mark sets here."""
        out: dict[str, str | None] = {}
        for one in self.filed:
            row = INSTRUCTIONS[one.mark.instruction]
            if row.pairs(one.mark) is Stance.PROPOSES:
                out[one.role] = row.sets(one.mark, one.touch, self.base)
        return out

    def serialize(self) -> dict:
        return {
            "address": self.address,
            "anchor": self.anchor,
            "base": self.base,
            "filed": [{"role": f.role, "touch": str(f.touch), **f.mark.serialize()} for f in self.filed],
            "answers": {str(t): {r: a.serialize() for r, a in by.items()} for t, by in self.answers.items()},
            "disposition": self.disposition.serialize() if self.disposition else None,
            "state": str(self.state) if self.state else None,
            "text": self.text,
            "sides": dict(self.sides),
            "reasons": list(self.reasons),
            "question": str(self.question) if self.question else None,
            "partner": self.partner,
        }

    @classmethod
    def deserialize(cls, where: str, entry: object) -> "tuple[Place | None, list[str]]":
        if not isinstance(entry, dict):
            return None, [f"{where}: a place must be an object"]
        data: dict = entry
        problems: list[str] = []
        filed = []
        for i, one in enumerate(data.get("filed") or []):
            mark, why = Mark.deserialize(f"{where} mark {i}", one)
            if mark is None:
                problems += why
                continue
            filed.append(Filed(str(one.get("role")), mark, Touch(str(one.get("touch")))))
        answers: dict[int, dict[str, Answer]] = {}
        for turn, by in (data.get("answers") or {}).items():
            for role, raw in by.items():
                answer, why = Answer.deserialize(f"{where} turn {turn} {role}", raw)
                if answer is None:
                    problems += why
                else:
                    answers.setdefault(int(turn), {})[role] = answer
        disposition = None
        if data.get("disposition") is not None:
            disposition, why = Disposition.deserialize(where, data["disposition"])
            problems += why
        if problems:
            return None, problems
        state = data.get("state")
        question = data.get("question")
        return (
            cls(
                address=str(data.get("address") or ""),
                anchor=str(data.get("anchor") or ""),
                base=str(data.get("base") or ""),
                filed=filed,
                answers=answers,
                disposition=disposition,
                state=State(state) if state else None,
                text=data.get("text"),
                sides=dict(data.get("sides") or {}),
                reasons=tuple(data.get("reasons") or ()),
                question=Question(question) if question else None,
                partner=data.get("partner"),
            ),
            [],
        )
```

- [ ] **Step 4: Write the marks pass and `pair_moves` in `desk/evaluate/passes.py`**

```python
"""The three passes, and the pairing of a move's two places."""

from comment_review.desk.answers.answer import Question
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.results.differences import CannotCompose, compose


def marks_pass(place: Place) -> Place:
    """The place's state from the marks filed there."""
    reasons = []
    for one in place.filed:
        row = INSTRUCTIONS[one.mark.instruction]
        reasons += [f"{one.role}: {why}" for why in row.reads(one.mark, one.touch, place.base)]
    if reasons:
        return _set(place, State.REFUSED, reasons=tuple(reasons))
    stances = {one.role: INSTRUCTIONS[one.mark.instruction].pairs(one.mark) for one in place.filed}
    if Stance.UNSETTLABLE in stances.values():
        return _set(place, State.UNSETTLABLE)
    proposals = place.proposals()
    texts = {role: text for role, text in proposals.items()}
    distinct = set(texts.values())
    if not texts:
        return _set(place, State.STANDS)
    if len(distinct) == 1:
        text = next(iter(distinct))
        state = State.STANDS if len(texts) == 1 else State.AGREED
        return _set(place, state, text=text)
    sides = {role: text if text is not None else place.base for role, text in texts.items()}
    try:
        composed = compose(place.base, sides)
    except CannotCompose:
        return _set(place, State.CONTESTED, sides=sides, question=Question.ESCALATION)
    return _set(place, State.COMPOSED, text=composed, sides=sides, question=Question.COMPOSITION)


def pair_moves(places: dict[str, Place]) -> None:
    """A move's two places take one state: the worse of the two."""
    order = [State.REFUSED, State.UNSETTLABLE, State.CONTESTED, State.COMPOSED, State.AGREED, State.STANDS]
    for address, place in places.items():
        other = places.get(place.partner or "")
        if other is None or other.partner != address:
            continue
        worst = min((place.state, other.state), key=lambda s: order.index(s) if s else len(order))
        for end in (place, other):
            if end.state is not worst:
                end.state = worst
                end.reasons = end.reasons + tuple(r for r in (place.reasons + other.reasons) if r not in end.reasons)


def _set(place: Place, state: State, text=None, sides=None, reasons=(), question=None) -> Place:
    place.state = state
    place.text = text
    place.sides = sides or {}
    place.reasons = reasons
    place.question = question
    return place
```

Check the signature of `results.differences.compose` before writing: it is what `flows/collate._composition` calls today (`compose(base, sides)` with `sides: dict[role, text]`, raising `CannotCompose`). If its name or shape differs, use the real one and change the test's expectation to the real composed text.

- [ ] **Step 5: Run the tests, then everything**

Run: `uv run pytest -q tests/test_passes.py tests/test_place.py`, then `uv run pytest -q`. Expected: PASS.

- [ ] **Step 6: Gates and commit**

Add `place` and `pass` to the vocabulary (a `pass` is one table applied to a place). Run every gate. Commit: `feat: the place and the marks pass -- a place's six states from what the roles filed`. Tick T2's first half and the step; commit the ticks.

---

### Task 4: The answers pass and the dispositions pass

**Files:**
- Modify: `src/comment_review/desk/evaluate/passes.py`
- Modify: `tests/test_passes.py`

**Interfaces:**
- Produces: `answers_pass(place, turn: int) -> Place`; `dispositions_pass(place) -> Place`; `evaluate(place, turn: int) -> Place` running the three in order.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_passes.py`:

```python
from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.dispositions.disposition import Disposition
from comment_review.desk.evaluate.passes import answers_pass, dispositions_pass, evaluate


def _contested() -> Place:
    a = _mark(Instruction.CORRECT, change="# one\n# 2\n# three\n", claim={"false": "two", "true": "2"})
    b = _mark(Instruction.CORRECT, change="# one\n# II\n# three\n", claim={"false": "two", "true": "II"})
    return marks_pass(_place(Filed("a", a, Touch.OWN), Filed("b", b, Touch.OWN)))


def _answer(name, change="", claim=None):
    return Answer(address="m.py@b1", anchor="x = 1", question=Question.ESCALATION, name=name, reason="r", change=change, claim=claim or {})


def test_a_withdrawal_leaves_the_other_side_standing():
    place = _contested()
    place.answers[1] = {"a": _answer("hold"), "b": _answer("withdraw")}
    got = answers_pass(place, 1)
    assert got.state is State.STANDS and got.text == "# one\n# 2\n# three\n"


def test_two_holds_keep_the_place_contested():
    place = _contested()
    place.answers[1] = {"a": _answer("hold"), "b": _answer("hold")}
    assert answers_pass(place, 1).state is State.CONTESTED


def test_both_replacing_with_one_text_agree():
    place = _contested()
    place.answers[1] = {"a": _answer("correct", "# one\n# 2\n# three\n"), "b": _answer("patch", "# one\n# 2\n# three\n")}
    got = answers_pass(place, 1)
    assert got.state is State.AGREED and got.text == "# one\n# 2\n# three\n"


def test_an_unanswered_role_leaves_its_side_and_the_place_open():
    place = _contested()
    place.answers[1] = {"a": _answer("hold")}
    got = answers_pass(place, 1)
    assert got.state is State.CONTESTED
    assert "b" in got.sides


def test_a_taken_in_closes_a_contested_place_on_one_side():
    place = _contested()
    place.disposition = Disposition(address="m.py@b1", name="taken_in", side="b", prose="", reason="r")
    got = dispositions_pass(place)
    assert got.state is State.STANDS and got.text == "# one\n# II\n# three\n"


def test_a_recast_closes_it_on_the_chiefs_prose():
    place = _contested()
    place.disposition = Disposition(address="m.py@b1", name="recast", side="copy-chief", prose="# mine\n", reason="r")
    got = dispositions_pass(place)
    assert got.state is State.STANDS and got.text == "# mine\n"


def test_a_disposition_on_an_unsettlable_place_is_refused():
    q = _mark(Instruction.QUERY, claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)})
    place = marks_pass(_place(Filed("a", q, Touch.OWN)))
    place.disposition = Disposition(address="m.py@b1", name="recast", side="copy-chief", prose="# mine\n", reason="r")
    got = dispositions_pass(place)
    assert got.state is State.REFUSED and "unsettlable" in got.reasons[0]


def test_evaluate_runs_the_three_in_order():
    place = _contested()
    place.answers[1] = {"a": _answer("hold"), "b": _answer("hold")}
    place.disposition = Disposition(address="m.py@b1", name="taken_in", side="a", prose="", reason="r")
    got = evaluate(place, turn=1)
    assert got.state is State.STANDS and got.text == "# one\n# 2\n# three\n"
```

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest -q tests/test_passes.py`. Expected: FAIL, `answers_pass` not defined.

- [ ] **Step 3: Write the two passes and `evaluate`**

Append to `desk/evaluate/passes.py`:

```python
from comment_review.desk.answers.table import ANSWERS, Effect
from comment_review.desk.dispositions.table import DISPOSITIONS


def answers_pass(place: Place, turn: int) -> Place:
    """Narrow a carried-forward place by the roles' answers at `turn`."""
    if place.state not in (State.COMPOSED, State.CONTESTED):
        return place
    answers = place.answers.get(turn, {})
    sides = dict(place.sides)
    for role, answer in answers.items():
        row = ANSWERS.get((answer.question, answer.name))
        if row is None:
            return _set(place, State.REFUSED, reasons=(f"{role}: {answer.name} is not an answer to {answer.question}",))
        effect = row.effect(answer)
        if effect is Effect.UNSETTLABLE:
            return _set(place, State.UNSETTLABLE)
        if effect is Effect.REMOVES:
            sides.pop(role, None)
        elif effect is Effect.REPLACES:
            sides[role] = answer.change
        elif effect is Effect.ACCEPTS and place.text is not None:
            sides[role] = place.text
    return _from_sides(place, sides)


def dispositions_pass(place: Place) -> Place:
    """Close a carried-forward place on the chief's ruling."""
    if place.disposition is None:
        return place
    row = DISPOSITIONS[place.disposition.name]
    if place.state not in row.closes:
        return _set(
            place,
            State.REFUSED,
            reasons=(f"copy-chief: {place.disposition.name} cannot close a place that is {place.state}",),
        )
    if place.disposition.side not in place.sides and place.disposition.side not in ("original", "copy-chief"):
        return _set(place, State.REFUSED, reasons=(f"copy-chief: {place.disposition.side!r} proposed nothing here",))
    text = row.sets(place.disposition, place.base, place.sides)
    return _set(place, State.STANDS, text=text)


def evaluate(place: Place, turn: int = 0) -> Place:
    marks_pass(place)
    for t in range(1, turn + 1):
        answers_pass(place, t)
    return dispositions_pass(place)


def _from_sides(place: Place, sides: dict[str, str]) -> Place:
    distinct = set(sides.values())
    if not sides:
        return _set(place, State.STANDS)
    if len(distinct) == 1:
        text = next(iter(distinct))
        return _set(place, State.STANDS if len(sides) == 1 else State.AGREED, text=text)
    try:
        composed = compose(place.base, sides)
    except CannotCompose:
        return _set(place, State.CONTESTED, sides=sides, question=Question.ESCALATION)
    return _set(place, State.COMPOSED, text=composed, sides=sides, question=Question.COMPOSITION)
```

Refactor `marks_pass`'s tail to call `_from_sides` too, so agreement is decided in one function.

- [ ] **Step 4: Run, gates, commit**

Run: `uv run pytest -q`. Expected: PASS. Commit: `feat: the answers pass and the dispositions pass, and evaluate over the three`. Tick T2 and the step; commit the ticks.

---

### Task 5: The Unit of Work and its events

**Files:**
- Create: `src/comment_review/desk/work/__init__.py`, `events.py`, `fold.py`
- Create: `tests/test_fold.py`

**Interfaces:**
- Produces: events `Refused(role, address, reasons)`, `CarriedForward(address, state, question, roles)`, `Unsettlable(address, role, reason)`, `Settled(address, text)`, `Committed(places: int)`, `RolledBack(reasons: int)`; `Fold(places: dict[str, Place], turn: int)` with `run() -> Fold`, `events: list`, `committed: bool`, `decided: dict[str, Place]`.

- [ ] **Step 1: Write the failing tests**

`tests/test_fold.py`:

```python
"""The Unit of Work: every place decided, or nothing."""

from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.evaluate.state import State
from comment_review.desk.marks.mark import Instruction, Mark, Shape
from comment_review.desk.marks.table import Touch
from comment_review.desk.work import events
from comment_review.desk.work.fold import Fold

BASE = "# one\n# two\n# three\n"


def _mark(instruction, change="", claim=None, address="m.py@b1", raw_text=BASE):
    return Mark(address=address, anchor="x = 1", raw_text=raw_text, instruction=instruction, claim=claim or {}, reason="r", sources=(), change=change)


def _place(address, *filed, base=BASE):
    return Place(address=address, anchor="x = 1", base=base, filed=list(filed))


def test_a_fold_of_settled_places_commits_and_says_what_it_settled():
    fold = Fold({
        "m.py@b1": _place("m.py@b1", Filed("a", _mark(Instruction.CLEAN), Touch.OWN)),
        "m.py@b5": _place("m.py@b5", Filed("a", _mark(Instruction.CORRECT, "# one\n# 2\n# three\n", {"false": "two", "true": "2"}, "m.py@b5"), Touch.OWN)),
    })
    fold.run()
    assert fold.committed
    assert [type(e).__name__ for e in fold.events] == ["Settled", "Settled", "Committed"]
    assert fold.decided["m.py@b5"].text == "# one\n# 2\n# three\n"


def test_one_refused_place_rolls_the_fold_back():
    move = _mark(Instruction.MOVE, "# six\n", {"from": "m.py@b1", "to": "m.py@b5"})
    fold = Fold({
        "m.py@b1": _place("m.py@b1", Filed("a", move, Touch.ORIGIN)),
        "m.py@b5": _place("m.py@b5", Filed("a", _mark(Instruction.CLEAN, address="m.py@b5"), Touch.OWN)),
    })
    fold.run()
    assert not fold.committed
    refused = [e for e in fold.events if isinstance(e, events.Refused)]
    assert refused and refused[0].role == "a" and refused[0].address == "m.py@b1"
    assert isinstance(fold.events[-1], events.RolledBack)


def test_a_carried_and_an_unsettlable_place_are_reported_and_the_fold_commits():
    a = _mark(Instruction.CORRECT, "# one\n# 2\n# three\n", {"false": "two", "true": "2"})
    b = _mark(Instruction.CORRECT, "# one\n# II\n# three\n", {"false": "two", "true": "II"})
    q = _mark(Instruction.QUERY, claim={"shape": str(Shape.HUMAN_REVIEW_NECESSARY)}, address="m.py@b5")
    fold = Fold({
        "m.py@b1": _place("m.py@b1", Filed("a", a, Touch.OWN), Filed("b", b, Touch.OWN)),
        "m.py@b5": _place("m.py@b5", Filed("a", q, Touch.OWN)),
    })
    fold.run()
    assert fold.committed
    kinds = [type(e).__name__ for e in fold.events]
    assert kinds == ["CarriedForward", "Unsettlable", "Committed"]
    carried = fold.events[0]
    assert carried.state is State.CONTESTED and carried.roles == ("a", "b")


def test_a_move_refused_at_one_end_rolls_back_both():
    move = _mark(Instruction.MOVE, "# two\n", {"from": "m.py@b1", "to": "m.py@b5"}, raw_text="# four\n# five\n")
    origin = _place("m.py@b1", Filed("a", move, Touch.ORIGIN))
    destination = _place("m.py@b5", Filed("a", move, Touch.DESTINATION), base="# four\n# five\n")
    origin.partner, destination.partner = "m.py@b5", "m.py@b1"
    fold = Fold({"m.py@b1": origin, "m.py@b5": destination}).run()
    assert not fold.committed
    assert {e.address for e in fold.events if isinstance(e, events.Refused)} == {"m.py@b1", "m.py@b5"}
```

- [ ] **Step 2: Run to see them fail**

Run: `uv run pytest -q tests/test_fold.py`. Expected: FAIL at import.

- [ ] **Step 3: Write `desk/work/events.py`**

```python
"""What a fold says as it runs. The commands print from these and nothing else."""

from typing import NamedTuple

from comment_review.desk.answers.answer import Question
from comment_review.desk.evaluate.state import State


class Refused(NamedTuple):
    role: str
    address: str
    reasons: tuple[str, ...]


class CarriedForward(NamedTuple):
    address: str
    state: State
    question: Question | None
    roles: tuple[str, ...]


class Unsettlable(NamedTuple):
    address: str
    role: str
    reason: str


class Settled(NamedTuple):
    address: str
    text: str | None


class Committed(NamedTuple):
    places: int


class RolledBack(NamedTuple):
    reasons: int


Event = Refused | CarriedForward | Unsettlable | Settled | Committed | RolledBack
```

- [ ] **Step 4: Write `desk/work/fold.py`**

```python
"""The Unit of Work: one fold over the places of a stage.

It evaluates every place, pairs a move's two ends, and commits -- every place
decided, no place refused -- or rolls back, in which case the flow saves
nothing and the events are the report. It reads no file and knows no
container of the read or write end; the flow derives the places and saves
the result (`decision-log.md Process: #171` and the design of 2026-09-14).
"""

from dataclasses import dataclass, field

from comment_review.desk.evaluate.passes import evaluate, pair_moves
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import CARRIED, State
from comment_review.desk.marks.mark import Instruction
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.desk.work import events


@dataclass
class Fold:
    places: dict[str, Place]
    turn: int = 0
    events: list = field(default_factory=list)
    committed: bool = False

    @property
    def decided(self) -> dict[str, Place]:
        return self.places if self.committed else {}

    def run(self) -> "Fold":
        for place in self.places.values():
            evaluate(place, self.turn)
        pair_moves(self.places)
        refused = 0
        for address in sorted(self.places):
            place = self.places[address]
            if place.state is State.REFUSED:
                refused += 1
                for role, reasons in _by_role(place.reasons).items():
                    self.events.append(events.Refused(role, address, reasons))
            elif place.state in CARRIED:
                self.events.append(
                    events.CarriedForward(address, place.state, place.question, tuple(sorted(place.sides)))
                )
            elif place.state is State.UNSETTLABLE:
                for one in place.filed:
                    if INSTRUCTIONS[one.mark.instruction].pairs(one.mark) is Stance.UNSETTLABLE:
                        self.events.append(events.Unsettlable(address, one.role, one.mark.reason))
            else:
                self.events.append(events.Settled(address, place.text))
        if refused:
            self.events.append(events.RolledBack(refused))
            return self
        self.committed = True
        self.events.append(events.Committed(len(self.places)))
        return self


def _by_role(reasons: tuple[str, ...]) -> dict[str, tuple[str, ...]]:
    out: dict[str, list[str]] = {}
    for reason in reasons:
        role, _, why = reason.partition(": ")
        out.setdefault(role, []).append(why)
    return {role, tuple(whys) for role, whys in out.items()}
```

The last line is wrong on purpose so the engineer reads it: write `return {role: tuple(whys) for role, whys in out.items()}`. Delete the `Instruction` import if unused.

- [ ] **Step 5: Run, gates, commit**

Run: `uv run pytest -q`. Expected: PASS. Commit: `feat: the Unit of Work -- a fold commits every place or rolls back with its events`. Tick T3's first half and the step; commit the ticks.

---

### Task 6: Deriving places from copies, and the chief's copy from places

**Files:**
- Create: `src/comment_review/flows/places.py`
- Create: `tests/test_places.py`

**Interfaces:**
- Produces: `places_of(copies: list[EditCopy], bases: dict[str, str], anchors: dict[str, str]) -> dict[str, Place]` -- one place per address any copy's mark touches; a move files at its origin with `Touch.ORIGIN` and at `claim["to"]` with `Touch.DESTINATION`, and the two places name each other as `partner`; `bases` and `anchors` are `desk.collator.base_texts(binder)` and the page's anchors (from `flows.collate._page_cues`, which becomes `flows.pages.cues_at`). `chief_copy_of(decided: dict[str, Place], role: str, read_from: dict, sheets: list[Sheet]) -> EditCopy` -- one mark per place whose text is not None, a synthesized `correct` whose `claim.false` is the whole base (as `_composition` builds today) or a `drop` where the text is `""`.
- Consumes: `EditCopy`, `Sheet`, `Mark`, `Place`, `Filed`, `Touch`, `INSTRUCTIONS`.

- [ ] **Step 1: Write the failing tests** -- `tests/test_places.py`, building copies with `helpers.a_binder_over`, `copies_over`, `returned` and `helpers.a_move`, asserting: a move yields two places that partner each other; a clean and a correct on one address from two copies land as two `Filed` on one place; `chief_copy_of` over a decided `Place(text="# x\n")` yields one `correct` mark whose `change` is `"# x\n"` and whose `claim["false"]` is the base; a decided place with `text=None` yields no mark; `text=""` yields a `drop`.

- [ ] **Step 2: Run to see them fail.** Expected: FAIL at import.

- [ ] **Step 3: Write `flows/places.py`**

```python
"""Places from copies, and the chief's copy from decided places.

The flow's half of the middle: it knows EditCopy and Sheet, which desk does
not, and hands desk plain places.
"""

from comment_review.desk.containers import EditCopy, Sheet
from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.marks.mark import Instruction, Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Touch
from comment_review.reading.addresser import cue_of


def places_of(copies: list[EditCopy], bases: dict[str, str], anchors: dict[str, str]) -> dict[str, Place]:
    places: dict[str, Place] = {}

    def at(address: str) -> Place:
        if address not in places:
            places[address] = Place(address=address, anchor=anchors.get(address, ""), base=bases.get(address, ""))
        return places[address]

    for copy in copies:
        for sheet in copy.sheets:
            for mark in sheet.marks:
                row = INSTRUCTIONS[mark.instruction]
                if row.touches == (Touch.OWN,):
                    at(mark.address).filed.append(Filed(copy.role, mark, Touch.OWN))
                    continue
                destination = str(mark.claim.get("to", ""))
                origin, other = at(mark.address), at(destination)
                origin.filed.append(Filed(copy.role, mark, Touch.ORIGIN))
                other.filed.append(Filed(copy.role, mark, Touch.DESTINATION))
                origin.partner, other.partner = destination, mark.address
    return places


def chief_copy_of(decided: dict[str, Place], role: str, read_from: dict, sheets: list[Sheet]) -> EditCopy:
    by_path: dict[str, list[Mark]] = {}
    for address in sorted(decided):
        place = decided[address]
        if place.text is None:
            continue
        instruction = Instruction.DROP if place.text == "" else Instruction.CORRECT
        claim = {"drop": place.base} if instruction is Instruction.DROP else {"false": place.base, "true": place.text}
        by_path.setdefault(cue_of(address).path, []).append(
            Mark(address=address, anchor=place.anchor, raw_text=place.base, instruction=instruction,
                 claim=claim, reason=f"{role}: decided at this place", sources=(), change=place.text)
        )
    out = []
    for sheet in sheets:
        marks = by_path.get(_flat(sheet.path), [])
        if marks:
            out.append(Sheet(path=sheet.path, sha=sheet.sha, marks=tuple(marks)))
    return EditCopy(role=role, read_from={**read_from}, sheets=tuple(out))
```

`_flat` is the path flattening an address carries (`reading.addresser.flatten`, or whatever `_chief_copy` uses today via `unflatten`); read `flows/collate._chief_copy` for the exact call and use the same.

- [ ] **Step 4: Run, gates, commit**

`flows/places.py` names `Instruction.DROP` and `Instruction.CORRECT` to synthesize the chief's marks. That trips the tables gate. Move the synthesis into the marks table as a function `chief_mark(address, anchor, base, text) -> Mark` in `desk/marks/table.py`, and call it from `chief_copy_of`; the flow then names no row. Run: `uv run pytest -q`. Commit: `feat: places from copies, and the chief's copy from decided places`. Tick and commit the ticks.

---

### Task 7: The bus, the collate handler, and the collate command switched

**Files:**
- Create: `src/comment_review/flows/bus.py`
- Modify: `src/comment_review/desk/containers.py` (`MasterProof`: add `places`, keep `determined` and `unsettlable` until task 11)
- Modify: `src/comment_review/commands/collate.py`
- Rename: `src/comment_review/flows/collate.py` to `src/comment_review/flows/_collate.py` (`git mv`); every importer updated to `_collate`
- Create: `tests/test_bus.py`
- Modify: `tests/gates/test_tables_name_the_rows.py` (`flows/collate.py` becomes `flows/_collate.py` in the list)

**Interfaces:**
- Produces: message `CopiesReturned(stage, copies: list[EditCopy], binder: Binder, root: Path, topology: Stage | None)`; `handle(message) -> tuple[list[Event], Result | None]` where `Result` is `NamedTuple(proof: MasterProof, chief: EditCopy | None, batch: dict[str, list[dict]] | None)`; `MasterProof.places: tuple[dict, ...]` on the wire.
- Consumes: `desk.collator.verify_report`, `drift_in`, `base_texts`; `flows._collate.resolution_problems`, `_coverage_problems`, `_stage_problems`, `texts_at`, `_page_cues` (imported from the private module until task 11, when they move to `flows/verify.py`); `Fold`; `places_of`; `chief_copy_of`; `desk.answers.answer.Question`; `desk.diff_mark.batch_of` (until task 8 replaces it).

- [ ] **Step 1: Write the failing test** -- `tests/test_bus.py`: build a binder with `helpers.a_real_binder_over`, two copies (one `correct`, one `clean` at `m.py@b1`; both `clean` at `m.py@b2`), send `CopiesReturned`, and assert: the events hold `Settled("m.py@b1", "...")`, `Settled("m.py@b2", None)` and `Committed(2)`; the result's proof carries two `places`; `Place.deserialize` of each round-trips; the chief copy holds one mark at `m.py@b1`. A second test sends copies whose `correct` cites a line that does not resolve and asserts `Refused` and `RolledBack` and `result is None`.

- [ ] **Step 2: Run to see them fail.** Expected: FAIL at import.

- [ ] **Step 3: Write `flows/bus.py`**

```python
"""The bus: the stage transitions as messages, one handler each.

Each handler loads what its message names, derives places, opens a Fold,
and on commit builds what the stage saves. The commands print the events.
"""

from pathlib import Path
from typing import NamedTuple

from comment_review.binder.binder import Binder
from comment_review.desk.collator import Cache, base_texts, drift_in, verify_report
from comment_review.desk.containers import EditCopy, MasterProof
from comment_review.desk.evaluate.place import Place
from comment_review.desk.evaluate.state import CARRIED
from comment_review.desk.work import events
from comment_review.desk.work.fold import Fold
from comment_review.flows import _collate as old
from comment_review.flows.places import chief_copy_of, places_of


class CopiesReturned(NamedTuple):
    stage: str
    copies: list[EditCopy]
    binder: Binder
    root: Path
    topology: object = None


class Result(NamedTuple):
    proof: MasterProof
    chief: EditCopy | None
    batch: dict | None


def handle(message) -> tuple[list, Result | None]:
    handler = HANDLERS[type(message)]
    return handler(message)


def _on_copies(message: CopiesReturned) -> tuple[list, Result | None]:
    binder, root, copies = message.binder, message.root, message.copies
    paths = [page.path for page in binder.pages]
    out: list = []
    cache: Cache = {}
    page_cache: dict = {}
    problems = []
    for copy in copies:
        texts = old.texts_at(copy, paths, root, page_cache)
        problems += verify_report(copy, texts, root, cache)
        problems += old.resolution_problems(copy, paths, root, page_cache)
        problems += drift_in(copy, base_texts(binder))
    problems += old._coverage_problems(copies, binder)
    if message.topology is not None:
        problems += old._stage_problems(message.topology, copies)
    if problems:
        for p in problems:
            out.append(events.Refused(p.role, p.address, (p.message,)))
        out.append(events.RolledBack(len(problems)))
        return out, None
    anchors = _anchors_of(copies)
    fold = Fold(places_of(copies, base_texts(binder), anchors), turn=0).run()
    out += fold.events
    if not fold.committed:
        return out, None
    read_from = copies[0].read_from if copies else {}
    proof = MasterProof(
        stage=message.stage,
        read_from={**read_from},
        edit_copies=tuple(copies),
        places=tuple(p.serialize() for p in fold.decided.values()),
    )
    sheets = [s for c in copies for s in c.sheets]
    chief = chief_copy_of(fold.decided, "copy-chief", read_from, sheets)
    carried = [p for p in fold.decided.values() if p.state in CARRIED]
    batch = _batch_of(carried) if carried else None
    return out, Result(proof, chief, batch)


def _anchors_of(copies: list[EditCopy]) -> dict[str, str]:
    return {m.address: m.anchor for c in copies for s in c.sheets for m in s.marks}


def _batch_of(carried: list[Place]) -> dict[str, list[dict]]:
    batch: dict[str, list[dict]] = {}
    for place in carried:
        for role in sorted(place.sides):
            batch.setdefault(role, []).append({
                "address": place.address,
                "anchor": place.anchor,
                "question": str(place.question),
                "raw_text": place.text if place.text is not None else place.base,
                "sides": dict(place.sides),
                "instruction": None,
            })
    return batch


HANDLERS = {CopiesReturned: _on_copies}
```

Add `places: tuple[dict, ...] = ()` to `MasterProof` in `containers.py`, written and read on the wire under `"places"` (a list of place dicts; `deserialize` accepts a missing key as `()`). Keep `determined` and `unsettlable` as they are for the old readers.

- [ ] **Step 4: Switch `commands/collate.py`**

Replace its body after argument parsing: load the binder and the copies as today, build `CopiesReturned`, call `handle`, then print one line per event -- `Refused` as `<role> <address>: <reason>`, `CarriedForward` as `<state> <address>: <roles> (<question>)`, `Unsettlable` as `unsettlable <address>: <role> asks the human -- <reason>`, `Settled` as `stet <address>` -- and save `result.proof` to `--proof-out`, `result.chief` to `--out`, `result.batch` to `--batch-out` when the fold committed. Exit codes: `RolledBack` present -> 1; else a `CarriedForward` with `question == "escalation"` -> 4; else with `"composition"` -> 3; else 0. Delete the `DRIFT`, `COVERAGE` and `CARRIED_AND_UNRULED` codes: drift and coverage now refuse (they are problems before the fold), and an unruled place is a `Refused` from `mark_errors`, which `_on_copies` must also run: add `problems += [Problem(r.role, r.address, "; ".join(r.reasons)) for r in mark_errors(copies)]` before the fold. Update `tests/test_collate_command.py`'s expectations to the four codes.

- [ ] **Step 5: Run the smoke and the suite**

Run: `uv run pytest -q` and `pwsh -NoProfile -File scripts/smoke_middle.ps1 -Stop collate`. The smoke's collate stage expects exit 4; it still must. Old tests in `tests/test_collate.py` that call `flows.collate.collate` now import `flows._collate`; leave them running against the private module until task 11.

- [ ] **Step 6: The differential**

Write `tests/test_differential_collate.py`: run `pwsh scripts/smoke_middle.ps1 -Stop mark` once per session (a fixture), then fold its four copies through both `old.collate` and `handle(CopiesReturned(...))`, and assert that for every address the old `Collated.determined` settled, the new decided place has the same text; and that the set of addresses old escalated or re-read equals the set the new carried forward. Where they differ, the new must match a ruling (#172, #174, #175, #176) and the test says which; otherwise it is a defect in the new fold. Commit: `feat: the bus and the collate handler; collate folds through the Unit of Work`. Tick T3 and the step; commit the ticks.

---

### Task 8: The turn and disposition handlers; both commands switched

**Files:**
- Modify: `src/comment_review/flows/bus.py`
- Modify: `src/comment_review/commands/turn.py`, `src/comment_review/commands/disposition.py`, `src/comment_review/commands/check.py` (`--answers` reads `Answer.deserialize`)
- Rename: `src/comment_review/flows/turn.py` to `_turn.py`
- Modify: `tests/test_bus.py`, `tests/gates/test_tables_name_the_rows.py`

**Interfaces:**
- Produces: `AnswersReturned(proof: MasterProof, answers: dict[str, list[dict]], binder, root)` and `DispositionsWritten(proof, dispositions: list[dict], binder, root)`, both handled by `handle`, returning `Result` with the next proof, the chief copy, and a batch where places are still carried.
- Consumes: `Answer.deserialize`, `Disposition.deserialize`, `Place.deserialize`, `Fold`, `chief_copy_of`.

- [ ] **Step 1: Write the failing tests** in `tests/test_bus.py`: from a committed `CopiesReturned` result with one contested place, send `AnswersReturned` with `hold` and `withdraw` and assert `Settled` and the next proof's place `state == "stands"`; send `DispositionsWritten` with a `recast` on a still-contested place and assert the chief copy carries the prose; send a disposition naming an unsettlable place and assert `Refused` and `result is None`.

- [ ] **Step 2: Run to see them fail.**

- [ ] **Step 3: Write the two handlers**

```python
class AnswersReturned(NamedTuple):
    proof: MasterProof
    answers: dict[str, list[dict]]
    binder: Binder
    root: Path


class DispositionsWritten(NamedTuple):
    proof: MasterProof
    dispositions: list[dict]
    binder: Binder
    root: Path


def _places_on(proof: MasterProof) -> tuple[dict[str, Place], list[str]]:
    places, problems = {}, []
    for i, entry in enumerate(proof.places):
        place, why = Place.deserialize(f"place {i}", entry)
        if place is None:
            problems += why
        else:
            places[place.address] = place
    return places, problems


def _on_answers(message: AnswersReturned) -> tuple[list, Result | None]:
    places, problems = _places_on(message.proof)
    turn = 1 + max((int(t) for p in places.values() for t in p.answers), default=0)
    out: list = []
    for role, given in message.answers.items():
        for entry in given:
            answer, why = Answer.deserialize(f"{role} {entry.get('address')}", {**entry, "anchor": entry.get("anchor", "")})
            if answer is None:
                problems += why
                continue
            place = places.get(answer.address)
            if place is None or place.state not in CARRIED:
                problems.append(f"{role} {answer.address}: not carried forward")
                continue
            place.answers.setdefault(turn, {})[role] = answer
    for place in places.values():
        if place.state in CARRIED:
            asked = set(place.sides)
            answered = set(place.answers.get(turn, {}))
            for role in sorted(asked - answered):
                problems.append(f"{role} {place.address}: unanswered")
    if problems:
        out += [events.Refused(p.split(" ")[0], p.split(" ")[1].rstrip(":"), (p,)) for p in problems]
        out.append(events.RolledBack(len(problems)))
        return out, None
    return _commit(message.proof, places, turn, out)


def _on_dispositions(message: DispositionsWritten) -> tuple[list, Result | None]:
    places, problems = _places_on(message.proof)
    for entry in message.dispositions:
        disposition, why = Disposition.deserialize(str(entry.get("address")), entry)
        if disposition is None:
            problems += why
            continue
        place = places.get(disposition.address)
        if place is None:
            problems.append(f"copy-chief {disposition.address}: no such place")
            continue
        place.disposition = disposition
    for place in places.values():
        if place.state in CARRIED and place.disposition is None:
            problems.append(f"copy-chief {place.address}: carried forward and not ruled on")
    out: list = []
    if problems:
        out += [events.Refused("copy-chief", p.split(" ")[1].rstrip(":"), (p,)) for p in problems]
        out.append(events.RolledBack(len(problems)))
        return out, None
    turn = max((int(t) for p in places.values() for t in p.answers), default=0)
    return _commit(message.proof, places, turn, out)


def _commit(proof: MasterProof, places: dict[str, Place], turn: int, out: list) -> tuple[list, Result | None]:
    fold = Fold(places, turn=turn).run()
    out += fold.events
    if not fold.committed:
        return out, None
    next_proof = MasterProof(stage=proof.stage, read_from={**proof.read_from}, edit_copies=proof.edit_copies,
                             places=tuple(p.serialize() for p in fold.decided.values()))
    sheets = [s for c in proof.edit_copies for s in c.sheets]
    chief = chief_copy_of(fold.decided, "copy-chief", proof.read_from, sheets)
    carried = [p for p in fold.decided.values() if p.state in CARRIED]
    return out, Result(next_proof, chief, _batch_of(carried) if carried else None)


HANDLERS = {CopiesReturned: _on_copies, AnswersReturned: _on_answers, DispositionsWritten: _on_dispositions}
```

`evaluate(place, turn)` re-runs the marks pass over `filed` and then every turn's answers, so a place's state is always derived from its record and never carried as stale.

- [ ] **Step 4: Switch the two commands** the way collate was: parse, load the proof and the answers or dispositions, `handle`, print the events, save on commit. `disposition` additionally writes `--proof-out` as the closed proof and `--out` as the chief copy. `check --answers` validates each entry with `Answer.deserialize` against the batch's slots (unanswered and unsent named), replacing `flows.turn.take_answers`.

- [ ] **Step 5: Run everything, the full smoke, commit**

Run: `uv run pytest -q`; `pwsh -NoProfile -File scripts/smoke_middle.ps1`. Both green. Rename `flows/turn.py` to `_turn.py`, update the gate list. Commit: `feat: the turn and disposition handlers; both commands fold through the Unit of Work`. Tick T4 and the step; commit the ticks.

---

### Task 9: The ends read the tables

**Files:**
- Modify: `src/comment_review/flows/fill.py`, `src/comment_review/commands/mark.py`, `src/comment_review/flows/transcribe.py`, `src/comment_review/commands/proof.py`, `src/comment_review/desk/marks/mark.py` (delete `text_at`)
- Modify: `tests/test_fill.py`, `tests/test_mark_command.py`, `tests/test_revise.py`, `tests/test_proof_setter.py`
- Modify: `src/plugin/skills/comment-review/references/reviewer-brief.md`, `docs/the-mark.md`

**Interfaces:**
- Produces: `mark` takes `--raw-text` (inline or `@path`) for `move` and `add`: the paragraph as it will read (#175, #176); `fill` runs the row's `reads` before placing; `docket_of(copy, repo)` folds the one copy (no verification) and transcribes the decided places -- one alteration where `text` is not `None`.

- [ ] **Step 1: Failing tests**: in `tests/test_fill.py`, a move placed with `change="# two\n"` and `raw_text="# four\n# two\n# five\n"` lands with both; a move whose snippet is not in the origin once is refused with the row's message; an add whose `raw_text` drops a word of the base is refused. In `tests/test_revise.py`, `docket_of` over a copy holding a partial move yields the origin's remainder and the destination's `raw_text`; over a copy of cleans yields no schedule. In `tests/test_mark_command.py`, `--instruction move --change @snippet --raw-text @dest` places both.

- [ ] **Step 2: Run to see them fail.**

- [ ] **Step 3: Implement**: in `fill`, after the change is derived, run `row.reads(mark, touch, base)` for each touch -- for a move the destination's base comes from the page through `place_on_the_page`'s reader -- and refuse on any problem; accept `raw_text` from the entry for rows whose `sets` is `_the_raw_text` or `_move_sets` (add a row field `carries_raw_text: bool` rather than testing the function). In `transcribe.docket_of`: `places = places_of([copy], bases, anchors)` where bases and anchors are read from the pages, `Fold(places).run()`, then one `Alteration(cue, text, anchor)` per decided place with `text is not None`. Delete `text_at` and its tests. In `commands/proof.py` nothing changes but the docstring.

- [ ] **Step 4: The brief and the-mark.md**: the move's `change` is the snippet and its `raw_text` the destination paragraph; the labelled `to:`/`from:` block is deleted; an `add`'s `raw_text` is the paragraph as it will read; `mark`'s example for a move shows `--change @snippet.txt --raw-text @destination.txt`. Regenerate the brief's table with `uv run python scripts/render_brief.py --write`.

- [ ] **Step 5: Run everything, the smoke, commit**: `feat: fill, check and docket_of read the tables; a move carries its snippet and destination text`. Remove `flows/fill.py`, `flows/transcribe.py` and `commands/mark.py` from the gate list if they no longer name a row. Tick T5, mark-defects T26, move-is-a-composite-mark T25 and the step; commit the ticks.

---

### Task 10: The smoke plants every row

**Files:**
- Modify: `scripts/smoke_fixture.py`, `scripts/smoke_middle.ps1`, `tests/gates/test_smoke_fixture.py`

- [ ] **Step 1: Plant what is missing.** Read `LANDINGS`, `ANSWERS` and `DISPOSITIONS` against the three tables and add a scenario for each row and each `Effect` not yet reached: a partial move whose snippet leaves `rate.py@b1` for `rate.py@b5` (smoke T9: the origin keeps its remainder, the destination reads as `raw_text` says); an `add` at a place holding prose with `raw_text` keeping every word; a second stage in the topology that reads the first stage's revise (smoke T6: `--stage 4=<roles>` then `--stage 5=ownership-context` with `reads = "revise:4"`, and one correction placed in stage 5 on a paragraph stage 4 corrected, landing over the revised text); a `taken_in` on the original. Write each landing text by hand into `EXPECTED` and `RATE_EXPECTED`.

- [ ] **Step 2: The row-coverage gate**: in `tests/gates/test_smoke_fixture.py`, a test that walks `INSTRUCTIONS`, `ANSWERS` and `DISPOSITIONS` and asserts every row name appears in the plant's tables (`LANDINGS`, `ANSWERS`, `DISPOSITIONS` in `smoke_fixture.py`) -- reading those tables, not the script.

- [ ] **Step 3: Run the smoke and the suite, commit**: `test: the smoke plants every row of the three tables`. Tick T7, smoke-drives-one-route T6 and T9, staged-chain-untested T5 (the second stage reads the revise), and the step; commit the ticks.

---

### Task 11: Delete the old middle

**Files:**
- Delete: `src/comment_review/flows/_collate.py`, `_turn.py`, `desk/determined.py`, `desk/diff_mark.py`, `desk/mark.py` (the shim), `desk/collator.py`'s reconciliation half (`Placed`, `places`, `_filed_against`, `Reconciled`, `_owes_change`, `_sentence_key`, `_roles_of_stage`, `_outcome`, `_join_moves`, `reconcile`, `_touches`), `MasterProof.determined` and `.unsettlable`
- Move: `_collate.py`'s `texts_at`, `resolution_problems`, `_coverage_problems`, `_stage_problems`, `_page_cues`, `_page_at` to `src/comment_review/flows/verify.py`
- Delete: `tests/test_collate.py`, `tests/test_turn.py`, `tests/test_determined.py`, `tests/test_diff_mark.py`, `tests/test_differential_collate.py`, the reconciliation tests in `tests/test_collator.py`, `tests/test_reconcile.py`; re-point every `from comment_review.desk.mark import` to `desk.marks.mark` or `desk.marks.table`
- Modify: `tests/gates/test_tables_name_the_rows.py` -- `STILL_OLD` becomes empty and the second test is deleted

- [ ] **Step 1: Before deleting a test file, read it** for a case the new tests lack, and port that case to the new module's test file. List the ported cases in the commit message.
- [ ] **Step 2: Delete, re-point, run**: `uv run pytest -q`, every gate, the smoke, `uv run python scripts/dead_sweep.py --names` for orphans. `docs/history.md` gains one entry: the reconciliation in `desk/collator.py`, `flows/collate.py` and `flows/turn.py`, replaced by the three tables and the evaluator, with this commit's hash.
- [ ] **Step 3: Commit**: `chore: delete the old fold, turn, determined and diff_mark with their tests`. Tick T6 and the step; commit the ticks.

---

### Task 12: The docs, the release, and the self-run again

**Files:**
- Modify: `CLAUDE.md` (the "Architecture" section's description of the middle), `docs/the-mark.md`, `docs/the-turn.md`, `docs/conventions.md` (the four couplings measured 2026-08-31 -- state which are gone), `docs/decision-log.md` (a ruling recording the rebuild landed, with the commit), `src/plugin/skills/comment-review/SKILL.md` stage 5 (the events the commands print, the four exit codes)

- [ ] **Step 1: Update the docs** to what the code does now. Run `uv run python scripts/check_vocabulary.py` and `uv run pytest -q tests/gates`.
- [ ] **Step 2: Cut beta.5** with the `cut-a-release` skill, on this branch, and install it.
- [ ] **Step 3: Run the self-run again** over the same 15 files through the commands alone, the way `docs/plans/0.2.4-the-cli-carries-a-real-run.md` P11 says. It reaches 7a with no hand repair; every finding about the tool is filed on the board before any fix.
- [ ] **Step 4: Commit the docs**: `docs: the middle as rebuilt`. Tick the step; commit. Then `job-board plan show 0.2.4-the-middle-rebuilt` must name no open reason, and `plan close` closes it; merge into `feat/the-cli-carries-a-real-run` with `--no-ff`, and tick that plan's P19-equivalent step for this subplan.

---

## Self-review

- Spec coverage: three tables (tasks 1, 2), place and six states (2, 3), the passes (3, 4), the Unit of Work (5), the bus and thin commands (7, 8), the ends (9), the layout (1-5), measurement on the smoke (10), deletion (11), the order (0-12), the docs (12). The spec's `stet` row is out of scope and stays so.
- Placeholders: task 6 step 1 and task 8 step 1 describe their tests in prose rather than code; each names the exact inputs, helpers and assertions, so an engineer can write them without a second decision. Task 9 step 3 names the row field to add (`carries_raw_text`) rather than leaving the choice.
- Type consistency: `Fold(places, turn).run()`, `Fold.decided`, `Fold.events`, `Fold.committed` are used identically in tasks 5, 7, 8 and 9; `places_of(copies, bases, anchors)` and `chief_copy_of(decided, role, read_from, sheets)` in 6, 7, 8 and 9; `Place.serialize`/`deserialize` in 3, 7 and 8; `Answer.deserialize(where, entry)` and `Disposition.deserialize(where, entry)` in 2 and 8; `State`, `CARRIED` in 2 through 8.
