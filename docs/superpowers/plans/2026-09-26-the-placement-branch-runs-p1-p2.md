# Human Questions Before the Fold, and the Four Run Traps -- Implementation Plan (P1, P2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** No human-review query reaches a fold -- `collate`, `turn` and `check` stop on it, say whether the human has answered, and name the role that must act -- and the four traps a real run hits are gone.

**Architecture:** A new flow module, `flows/human.py`, finds every human-review query in returned copies or answers (by the row's stance or effect, naming no row) and reads the human's answers file (TOML, one `[[answer]]` per query). The bus refuses a stage or a turn that still holds one, with a new rollback event `AsksTheHuman` that carries the human's answer where the file has it; `collate` and `turn` take `--human PATH` and exit `ASKS_THE_HUMAN` (5) when the only refusals are human questions. The role reads its own answers by name from the file and replaces its query with a real mark or answer; the fold then runs as before.

**Tech Stack:** Python 3.11 stdlib only in `src/comment_review/` (`tomllib` for the answers file), pytest, ruff, ty -- all through `uv run`.

**Spec:** `docs/decision-log.md` Process #197 and #198 (the last two entries), and the board plan `docs/plans/0.2.4-the-placement-branch-runs.md` (P1 and P2's checks).

| board step | tasks | ticks when | TODO tasks it closes |
| --- | --- | --- | --- |
| P1 | 1, 2 | end of Task 2 | `human-questions-before-the-fold` T2, T3 |
| P2 | 3 | end of Task 3 | `rebuilt-middle-final-review` T39, T19, T6, T10 |

## Decisions this plan takes -- Roy to correct at review

- **H1.** The answers file is the hand-back. The refusal line names the role and, once the human has answered, carries the answer; the role reads its own `[[answer]]` sections by its name (#198). No new slot or batch is built for it.
- **H2.** A human query never folds. Answered or not, a copy or an answer file that still holds one is refused; the role replaces it with its real mark or answer, and the next `collate` or `turn` folds.
- **H3.** `ASKS_THE_HUMAN = 5` is a new exit code, returned when a rollback holds human questions and nothing else, so the task agent can tell "ask the human" from "fix the copy". A rollback holding both is `BROKEN`.
- **H4.** The held-for-the-human states (`State.UNSETTLABLE`, `Placement.HELD`) stay in the desk. The commands no longer reach them; deleting them is `human-questions-before-the-fold` T5's, with the write-end guard.
- **H5.** A `[[answer]]` naming a query no copy still holds is ignored: it is the record of a question already worked through.
- **H6.** T10: the chief's copy carries a place only once it has settled (`SETTLED`, which includes a place the chief closed, `STANDS`); a composed or contested place's working text is on the proof, not on the chief's copy.

## Global Constraints

- Everything runs through `uv run`; Python floor 3.11.
- `src/comment_review/**` imports the standard library only.
- No `except` clause holds a tuple literal; bind it to a name.
- Nothing outside `desk/marks/table.py`, `desk/answers/table.py`, `desk/dispositions/table.py` names a row: no `Instruction.X`, no `Answer.X`, no quoted `"taken_in"`, `"recast"`, `"stet"`, `"hold"`, `"withdraw"`.
- Files are ASCII. Docstrings and comments state what the code does or what is enforced; no subjective words.
- Edit with the file editor or a scratchpad `.py` script; no `sed`, no heredocs. Commit messages in a file, `git commit -F`, ending with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and `Claude-Session: https://claude.ai/code/session_01GZ2ebtw936BRU74FPzKYjp`.
- Gates, in order, immediately before every work commit and every tick commit: `uv run ruff check .`, `uv run ruff format .`, `uv run python scripts/check_shipped_syntax.py`, `uv run ruff check .`, `uv run ty check`, `uv run pytest -q` -- all green.
- A deleted mechanism leaves no test asserting its absence; a test whose premise a ruling superseded is deleted or rewritten to the new premise, and the report names each.
- `scripts/smoke_middle.ps1` is red until board P4; it is not a gate here.

## Review Focus

1. **A role's human query at a move's origin, and another role's human answer to the same move's placement, in one turn.** Expected: both are named, each against its own role and its own key (`m.py@b1` and `m.py@b1 -> m.py@b5`). Test in Task 2.
2. **An answers file with a section for a role that did not ask.** Expected: ignored (H5), not an error. Test in Task 1.
3. **A malformed answers file** (not TOML; `answer` not an array of tables; a section missing `answer`). Expected: `collate` and `turn` exit `UNREADABLE` naming the file and the section, before any fold. Test in Task 1 (the reader) and Task 2 (the command).
4. **A human query beside an ordinary refusal in one copy.** Expected: both reported; exit `BROKEN`, not `ASKS_THE_HUMAN`. Test in Task 2.
5. **A deferring query** (`outside-my-role`, `unable-to-determine`). Expected: not a human question; it folds as before. Test in Task 1.

---

### Task 1: Find a human question, and read the human's answers

**Files:**
- Create: `src/comment_review/flows/human.py`
- Test: `tests/test_human.py`

**Interfaces:**
- Produces:
  - `class HumanQuery(NamedTuple)`: `role: str`, `at: str` (a place's address, or a move key `"<origin> -> <destination>"`), `question: str` (the query's `reason`).
  - `class HumanAnswer(NamedTuple)`: `role`, `at`, `question`, `answer` -- all `str`.
  - `FIELDS = ("role", "at", "question", "answer")`.
  - `queries_in_copies(copies: list[EditCopy]) -> list[HumanQuery]`.
  - `queries_in_answers(given: dict[str, dict[str, Answer]]) -> list[HumanQuery]` -- `given` is role -> slot key -> Answer, as `flows.bus._on_answers` holds it.
  - `read_answers(text: str, where: str) -> tuple[list[HumanAnswer], list[str]]`.
  - `answered(queries: list[HumanQuery], answers: list[HumanAnswer]) -> list[tuple[HumanQuery, HumanAnswer | None]]` -- in the queries' order.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_human.py`:

```python
"""Human questions: found before a fold, and the human's answers read back.

`decision-log.md Process: #197` and `#198`.
"""

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.marks.mark import Shape
from comment_review.flows.human import (
    HumanAnswer,
    HumanQuery,
    answered,
    queries_in_answers,
    queries_in_copies,
    read_answers,
)
from tests.helpers import (
    a_clean,
    a_query,
    a_real_binder_over,
    copies_over,
    returned,
)

BASE = "# one\n# two\n# three"


def _copies(tmp_path, by_role):
    binder = a_real_binder_over(tmp_path / "repo", {"m.py@b1": BASE, "m.py@b2": BASE})
    return [returned(wire) for wire in copies_over(binder, by_role)]


def _answer(name, shape="", question=Question.COMPOSITION, at="m.py@b1"):
    claim = {"shape": shape, "attempted": "read it", "settles": "the author"} if shape else {}
    return Answer(address=at, anchor="v0 = 0", question=question, name=name, reason="why", claim=claim)


def test_a_human_review_query_in_a_copy_is_found_with_its_role_and_place(tmp_path):
    copies = _copies(
        tmp_path,
        {
            "block-context": {
                "m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY),
                "m.py@b2": a_clean("m.py@b2"),
            },
            "module-context": {"m.py@b1": a_clean("m.py@b1"), "m.py@b2": a_clean("m.py@b2")},
        },
    )
    got = queries_in_copies(copies)
    assert [(q.role, q.at) for q in got] == [("block-context", "m.py@b1")]
    assert got[0].question  # the query's own reason


def test_a_deferring_query_is_not_a_human_question(tmp_path):
    """Review Focus 5."""
    copies = _copies(
        tmp_path,
        {
            "block-context": {
                "m.py@b1": a_query("m.py@b1", Shape.OUTSIDE_MY_ROLE),
                "m.py@b2": a_query("m.py@b2", Shape.UNABLE_TO_DETERMINE),
            }
        },
    )
    assert queries_in_copies(copies) == []


def test_a_human_review_answer_is_found_under_its_slot_key():
    given = {
        "module-context": {
            "m.py@b1": _answer("clean"),
            "m.py@b1 -> m.py@b5": _answer(
                "query", "human-review-necessary", Question.PLACEMENT
            ),
        },
        "block-context": {"m.py@b2": _answer("query", "outside-my-role", at="m.py@b2")},
    }
    got = queries_in_answers(given)
    assert got == [HumanQuery("module-context", "m.py@b1 -> m.py@b5", "why")]


def test_an_answers_file_reads_one_section_per_query():
    text = (
        '[[answer]]\nrole = "block-context"\nat = "m.py@b1"\n'
        'question = "Is this still true?"\nanswer = "Yes, keep it."\n'
    )
    got, problems = read_answers(text, "human.toml")
    assert problems == []
    assert got == [HumanAnswer("block-context", "m.py@b1", "Is this still true?", "Yes, keep it.")]


def test_a_malformed_answers_file_is_named():
    """Review Focus 3."""
    _got, why = read_answers("[[answer\n", "human.toml")
    assert why and why[0].startswith("human.toml: not TOML")
    _got, why = read_answers('answer = "x"\n', "human.toml")
    assert why == ["human.toml: `answer` must be an array of tables, [[answer]]"]
    _got, why = read_answers(
        '[[answer]]\nrole = "block-context"\nat = "m.py@b1"\nquestion = "q"\n', "human.toml"
    )
    assert why == ["human.toml: answer 1 needs answer"]


def test_each_query_is_paired_with_its_own_roles_answer():
    """Review Focus 2: a section for a role that did not ask is not an error."""
    queries = [HumanQuery("block-context", "m.py@b1", "q1"), HumanQuery("chief", "m.py@b2", "q2")]
    answers = [
        HumanAnswer("block-context", "m.py@b1", "q1", "a1"),
        HumanAnswer("module-context", "m.py@b1", "q1", "not this role's"),
    ]
    got = answered(queries, answers)
    assert [(q.at, a.answer if a else None) for q, a in got] == [("m.py@b1", "a1"), ("m.py@b2", None)]
```

If `tests.helpers` is imported as `helpers` in the existing tests (read the imports of `tests/test_bus.py`), use the same form.

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest -q tests/test_human.py`
Expected: collection error, `No module named 'comment_review.flows.human'`.

- [ ] **Step 3: Write the module**

Create `src/comment_review/flows/human.py`:

```python
"""Human questions: found before a fold, and the human's answers read back.

`decision-log.md Process: #197`: a `human-review-necessary` query -- filed as
a mark, or given as an answer in a turn -- is asked of the human before the
fold runs, and the human's answer goes back to the role that asked, which
replaces its query with a real mark or answer. `#198`: the answers are one
TOML file, one `[[answer]]` table per query, naming the role that asked.

    [[answer]]
    role = "block-context"
    at = "m.py@b1"              # a place, or a move: "m.py@b1 -> m.py@b5"
    question = "..."
    answer = "..."

A query is found by what its row makes of it -- the stance a mark takes, the
effect an answer has -- so no row is named here.
"""

import tomllib
from typing import NamedTuple

from comment_review.desk.answers.answer import Answer
from comment_review.desk.answers.table import ANSWERS, Effect
from comment_review.desk.containers import EditCopy
from comment_review.desk.marks.table import INSTRUCTIONS, Stance


class HumanQuery(NamedTuple):
    """One question a role put to the human, and where it put it."""

    role: str
    at: str
    question: str


class HumanAnswer(NamedTuple):
    """One section of the answers file: the human's answer to one role's question."""

    role: str
    at: str
    question: str
    answer: str


#: The keys every `[[answer]]` carries, each a non-empty string.
FIELDS = ("role", "at", "question", "answer")


def queries_in_copies(copies: list[EditCopy]) -> list[HumanQuery]:
    """Every human question the roles filed as a mark, in copy and sheet order."""
    return [
        HumanQuery(copy.role, mark.address, mark.reason)
        for copy in copies
        for sheet in copy.sheets
        for mark in sheet.marks
        if INSTRUCTIONS[mark.instruction].pairs(mark) is Stance.UNSETTLABLE
    ]


def queries_in_answers(given: dict[str, dict[str, Answer]]) -> list[HumanQuery]:
    """Every human question the roles gave as an answer in a turn.

    Args:
        given: role -> slot key -> answer, as `flows.bus._on_answers` holds
            them; a slot key is a place's address or a move's key.

    Returns:
        The questions, by role and then slot key, so two runs name them in
        one order.
    """
    out = []
    for role in sorted(given):
        for at, answer in sorted(given[role].items()):
            row = ANSWERS.get((answer.question, answer.name))
            if row is not None and row.effect(answer) is Effect.UNSETTLABLE:
                out.append(HumanQuery(role, at, answer.reason))
    return out


def read_answers(text: str, where: str) -> tuple[list[HumanAnswer], list[str]]:
    """The human's answers file, read, or one problem per reason it will not read.

    Args:
        text: the file's text.
        where: how to name the file in a problem.

    Returns:
        `(the answers, [])`, or `([], problems)` where the file is not TOML or
        `answer` is not an array of tables, or `(the good ones, problems)` where
        some sections lack a field.
    """
    try:
        doc = tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        return [], [f"{where}: not TOML -- {exc}"]
    rows = doc.get("answer", [])
    if not isinstance(rows, list):
        return [], [f"{where}: `answer` must be an array of tables, [[answer]]"]
    out: list[HumanAnswer] = []
    problems: list[str] = []
    for i, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            problems.append(f"{where}: answer {i} is not a table")
            continue
        missing = [
            key
            for key in FIELDS
            if not isinstance(row.get(key), str) or not row[key].strip()
        ]
        if missing:
            problems.append(f"{where}: answer {i} needs {', '.join(missing)}")
            continue
        out.append(HumanAnswer(*(row[key] for key in FIELDS)))
    return out, problems


def answered(
    queries: list[HumanQuery], answers: list[HumanAnswer]
) -> list[tuple[HumanQuery, HumanAnswer | None]]:
    """Each query with the human's answer to it, or None where there is none yet.

    A section is the answer to a query where its role and its `at` are the
    query's; a section for a question no copy still holds is left alone -- it
    is the record of a question already worked through.
    """
    by = {(one.role, one.at): one for one in answers}
    return [(query, by.get((query.role, query.at))) for query in queries]
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest -q tests/test_human.py tests/gates/test_tables_name_the_rows.py`
Expected: all pass.

- [ ] **Step 5: Run the gates.** Expected: green.

- [ ] **Step 6: Commit** -- `feat: find a human question and read the human's answers (Process 197, 198)`. No tick.

---

### Task 2: The bus, `collate`, `turn` and `check` stop on a human question (board P1)

**Files:**
- Modify: `src/comment_review/desk/work/events.py` (new `AsksTheHuman`; `RolledBack` counts it)
- Modify: `src/comment_review/flows/bus.py` (`CopiesReturned.human`, `AnswersReturned.human`, the refusal in `_on_copies` and `_on_answers`, `_rolled_back`)
- Modify: `src/comment_review/commands/collate.py` (`ASKS_THE_HUMAN = 5`, `--human`, `_lines`, `_code_for`)
- Modify: `src/comment_review/commands/turn.py` (`--human`)
- Modify: `src/comment_review/commands/check.py` (`--human`; `--edit-copy` and `--answers` report human questions)
- Test: `tests/test_bus.py`, `tests/test_collate_command.py`, `tests/test_turn_command.py`, `tests/test_check_command.py`

**Interfaces:**
- Consumes: Task 1's `queries_in_copies`, `queries_in_answers`, `read_answers`, `answered`, `HumanAnswer`.
- Produces:
  - `events.AsksTheHuman(role: str, at: str, question: str, answer: str = "")` -- a rollback event, like `Refused`.
  - `CopiesReturned(..., human: tuple[HumanAnswer, ...] = ())`, `AnswersReturned(..., human: tuple[HumanAnswer, ...] = ())`.
  - `collate.ASKS_THE_HUMAN = 5`.
  - The console lines:
    - unanswered: `asks the human <at>: <role> -- <question>; ask it, record the answer in the answers file, and send it back to <role>`
    - answered: `answered by the human <at>: <role> -- <answer>; <role> replaces this query with its mark or answer`

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_bus.py` (reuse its existing imports and `_message`-style builders; read the file's top first):

```python
from comment_review.flows.human import HumanAnswer


def _with_a_human_query(tmp_path):
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b2": OTHER})
    by_role = {
        "block-context": {
            "m.py@b1": a_query("m.py@b1", Shape.HUMAN_REVIEW_NECESSARY),
            "m.py@b2": a_clean("m.py@b2"),
        },
        "module-context": {"m.py@b1": a_clean("m.py@b1"), "m.py@b2": a_clean("m.py@b2")},
    }
    copies = [returned(wire) for wire in copies_over(binder, by_role)]
    return binder, root, copies


class TestAHumanQuestionIsAskedBeforeTheFold:
    """`decision-log.md Process: #197`: no human question reaches a fold."""

    def test_an_unanswered_human_query_rolls_the_stage_back_naming_it(self, tmp_path):
        binder, root, copies = _with_a_human_query(tmp_path)
        out, result = handle(CopiesReturned("4c", copies, binder, root, None))
        assert result is None
        asks = [e for e in out if isinstance(e, events.AsksTheHuman)]
        assert [(e.role, e.at, e.answer) for e in asks] == [("block-context", "m.py@b1", "")]
        assert isinstance(out[-1], events.RolledBack)
        assert not any(isinstance(e, events.Refused) for e in out)

    def test_an_answered_query_still_rolls_back_and_carries_the_answer(self, tmp_path):
        binder, root, copies = _with_a_human_query(tmp_path)
        human = (HumanAnswer("block-context", "m.py@b1", "q", "Keep it."),)
        out, result = handle(CopiesReturned("4c", copies, binder, root, None, human))
        assert result is None
        (ask,) = [e for e in out if isinstance(e, events.AsksTheHuman)]
        assert ask.answer == "Keep it."

    def test_once_the_role_replaces_its_query_the_stage_folds(self, tmp_path):
        root = tmp_path / "repo"
        binder = a_real_binder_over(root, {"m.py@b1": BASE, "m.py@b2": OTHER})
        by_role = {
            role: {"m.py@b1": a_clean("m.py@b1"), "m.py@b2": a_clean("m.py@b2")}
            for role in ("block-context", "module-context")
        }
        copies = [returned(wire) for wire in copies_over(binder, by_role)]
        human = (HumanAnswer("block-context", "m.py@b1", "q", "Keep it."),)
        _out, result = handle(CopiesReturned("4c", copies, binder, root, None, human))
        assert result is not None

    def test_a_human_answer_in_a_turn_rolls_the_turn_back_naming_its_move(self, tmp_path):
        """Review Focus 1 (the placement half)."""
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        assert first is not None and first.batch is not None
        human_query = {"shape": "human-review-necessary", "attempted": "read both", "settles": "the author"}

        def answer_for(slot):
            if slot["question"] == "placement":
                return {**slot, "instruction": "query", "reason": "ask the author", "claim": human_query}
            return {**slot, "instruction": "clean", "reason": "r"}

        answers = {role: [answer_for(s) for s in slots] for role, slots in first.batch.items()}
        out, result = handle(AnswersReturned(first.proof, answers, root))
        assert result is None
        asks = [e for e in out if isinstance(e, events.AsksTheHuman)]
        assert [(e.role, e.at) for e in asks] == [("module-context", "m.py@b1 -> m.py@b2")]

    def test_a_human_query_beside_a_refusal_reports_both(self, tmp_path):
        """Review Focus 4."""
        binder, root, copies = _with_a_human_query(tmp_path)
        broken = [returned(w) for w in copies_over(binder, {"module-context": {
            "m.py@b1": a_correct("m.py@b1", "a sentence that is not there"),
            "m.py@b2": a_clean("m.py@b2"),
        }})]
        out, result = handle(CopiesReturned("4c", [copies[0], *broken], binder, root, None))
        assert result is None
        assert any(isinstance(e, events.Refused) for e in out)
        assert any(isinstance(e, events.AsksTheHuman) for e in out)
```

(`_a_move_two_roles_read`, `a_query`, `a_correct`, `Shape` -- use what test_bus.py already imports or defines; add the missing imports.)

Add to `tests/test_collate_command.py`:

```python
def test_a_human_question_prints_what_to_do_and_exits_asks_the_human():
    from comment_review.commands.collate import ASKS_THE_HUMAN, BROKEN, _code_for, _lines

    open_ = events.AsksTheHuman("block-context", "m.py@b1", "Is it true?")
    done = events.AsksTheHuman("block-context", "m.py@b1", "Is it true?", "Yes.")
    assert _lines(open_) == [
        "asks the human m.py@b1: block-context -- Is it true?; ask it, record the"
        " answer in the answers file, and send it back to block-context"
    ]
    assert _lines(done) == [
        "answered by the human m.py@b1: block-context -- Yes.; block-context"
        " replaces this query with its mark or answer"
    ]
    assert _code_for([open_, events.RolledBack(1)]) == ASKS_THE_HUMAN
    refused = events.Refused("module-context", "m.py@b1", ("bad",))
    assert _code_for([refused, open_, events.RolledBack(2)]) == BROKEN
```

Add one command-level test each to `tests/test_collate_command.py` and `tests/test_turn_command.py`, built the way the files' existing command tests are (read one first): `--human` naming a malformed TOML file exits `UNREADABLE` and prints `<path>: not TOML` (Review Focus 3); and a copy holding a human query exits `ASKS_THE_HUMAN` and writes no `--out`.

Add to `tests/test_check_command.py`, built the way its existing `--edit-copy` test is: a copy holding a human query makes `check --edit-copy` print the `asks the human` line and exit `BROKEN`; with `--human` naming a file that answers it, the line is the `answered by the human` one.

Then find the tests whose premise is a human query riding through the fold to the author -- `grep -rn "HUMAN_REVIEW_NECESSARY\|human-review-necessary\|A_QUERY_FOR_THE_HUMAN\|TestAMoveHeldForTheHuman\|Unsettlable" tests/test_bus.py tests/test_collate_command.py tests/test_turn_command.py tests/test_disposition_command.py` -- and for each: delete it where it drives a human query through `handle`, `collate`, `turn` or `disposition` and asserts it is held, printed for the author or closed around; keep the desk-level tests (`test_passes.py`, `test_move.py`, `test_fold.py`), which test the states H4 keeps. List each deleted or rewritten test and why in the report.

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest -q tests/test_bus.py -k TestAHumanQuestion tests/test_collate_command.py -k human`
Expected: FAIL -- `events` has no `AsksTheHuman`; `CopiesReturned` takes no `human`.

- [ ] **Step 3: The event**

In `src/comment_review/desk/work/events.py`, after `Refused`:

```python
class AsksTheHuman(NamedTuple):
    """One question a role put to the human, found before the fold ran.

    `decision-log.md Process: #197`: a human question never folds, so it rolls
    the stage or the turn back like a refusal, and says what is owed next --
    the human's answer where there is none yet (`answer` empty), or, where the
    answers file holds it, the role's replacement for its query.
    """

    role: str
    at: str
    question: str
    answer: str = ""
```

Add it to `Event`. The module docstring's rollback sentence becomes: a rollback emits its `Refused` and `AsksTheHuman` events and a `RolledBack`, and nothing else. `RolledBack`'s docstring: `reasons` counts the reasons across the `Refused` events before it and one per `AsksTheHuman`.

- [ ] **Step 4: The bus**

In `src/comment_review/flows/bus.py`:
- `CopiesReturned` and `AnswersReturned` each gain a last field `human: tuple[HumanAnswer, ...] = ()`, documented as the human's answers file, read (`decision-log.md Process: #198`).
- Add:

```python
def _asks(queries: list[HumanQuery], human: tuple[HumanAnswer, ...]) -> list:
    """One `AsksTheHuman` per human question, carrying the human's answer where given."""
    return [
        events.AsksTheHuman(q.role, q.at, q.question, a.answer if a else "")
        for q, a in answered(queries, list(human))
    ]
```

- `_rolled_back(problems, asks=())` emits the `Refused` events, then `asks`, then `RolledBack(len(problems) + len(asks))`.
- `_on_copies`: after `problems` is complete, `asks = _asks(queries_in_copies(copies), message.human)`; `if problems or asks: return _rolled_back(problems, asks)` (replace the inline rollback there with this call).
- `_on_answers`: after the loop that fills `given`, `asks = _asks(queries_in_answers(given), message.human)`; `if problems or asks: return _rolled_back(problems, asks)`.
- The module docstring's list of what each handler checks gains: a human question, which rolls back until the role replaces it (`#197`).

- [ ] **Step 5: The commands**

`src/comment_review/commands/collate.py`:
- `ASKS_THE_HUMAN = 5` beside the other codes, with a one-line comment: a rollback holding human questions and nothing else (`Process: #197`).
- `_lines`: before the `Refused` branch,

```python
    if isinstance(event, events.AsksTheHuman):
        if event.answer:
            return [
                f"answered by the human {event.at}: {event.role} -- {event.answer};"
                f" {event.role} replaces this query with its mark or answer"
            ]
        return [
            f"asks the human {event.at}: {event.role} -- {event.question}; ask it,"
            f" record the answer in the answers file, and send it back to {event.role}"
        ]
```

- `_code_for`: a rollback returns `BROKEN` when any `Refused` is in `out`, else `ASKS_THE_HUMAN` when any `AsksTheHuman` is; the docstring says so.
- `--human PATH` (optional): "the human's answers file, TOML, one [[answer]] per question (Process 198)". Read with `Path(path).read_text(encoding="utf-8")`; an `OSError` or any `read_answers` problem goes to `_refused(...)` (`UNREADABLE`) before anything else is read past it; pass `tuple(answers)` as `human=` to `CopiesReturned`.
- Add a small shared reader in collate.py, `_human_answers(path: str | None) -> tuple[tuple[HumanAnswer, ...], list[str]]`, returning `((), [])` for None, and use it from `turn.py` and `check.py` too, as `turn.py` already imports `_code_for`, `_print`, `_refused` from collate.

`src/comment_review/commands/turn.py`: the same `--human`, passed as `human=` to `AnswersReturned`; the module docstring names the flag.

`src/comment_review/commands/check.py`:
- `--human PATH`, optional, with either mode.
- `_check_copy`: after the existing checks, for each `(query, answer)` in `answered(queries_in_copies([copy]), human)` print the `_lines` line of `AsksTheHuman(...)` and count it as found.
- `_check_answers`: after `answers_of`, the same for `queries_in_answers({role: answers})`.

- [ ] **Step 6: Run the tests**

Run: `uv run pytest -q tests/test_human.py tests/test_bus.py tests/test_collate_command.py tests/test_turn_command.py tests/test_check_command.py tests/test_disposition_command.py tests/test_fold.py`
Expected: all pass. Then `uv run pytest -q`: all pass.

- [ ] **Step 7: Run the gates.** Expected: green.

- [ ] **Step 8: Commit the work** -- `feat: a human question stops the fold and says who acts next (Process 197, board P1)`, the body listing every deleted or rewritten test.

- [ ] **Step 9: Tick and commit** (gates again first)

```powershell
$work = git rev-parse HEAD
job-board todo finish human-questions-before-the-fold.md T2 --statement 'collate, turn and check list every human query before the fold; AsksTheHuman' --commit $work
job-board todo finish human-questions-before-the-fold.md T3 --statement 'TOML answers file read by --human; the answer rides on the refusal to the asking role' --commit $work
job-board plan finish 0.2.4-the-placement-branch-runs P1 --statement 'human questions stop the fold; ASKS_THE_HUMAN; answers file read' --commit $work
job-board plan refresh 0.2.4-the-placement-branch-runs
git add TODO docs/plans
git commit -F <tick message file>
```

---

### Task 3: The four run traps (board P2)

**Files:**
- Modify: `src/comment_review/desk/marks/mark.py` (`allowed()`: T39)
- Modify: `src/comment_review/commands/disposition.py` (docstring and help: T19)
- Modify: `src/comment_review/desk/dispositions/table.py` and `src/comment_review/desk/evaluate/passes.py` (`dispositions_pass`: T6)
- Modify: `src/comment_review/flows/places.py` (`chief_copy_of`: T10)
- Test: `tests/test_mark.py` or `tests/test_answers.py` (T39), `tests/test_disposition_command.py` (T19), `tests/test_passes.py` (T6), `tests/test_places.py` and `tests/test_bus.py` (T10)

**Interfaces:**
- Produces: `allowed()["raw_text"] == {"owed_by": [...rows with carries_raw_text, sorted...], "is": "the paragraph as it will read, with your text in, in the page's own form"}`; `DispositionRow.side` unchanged; `chief_copy_of` places only settled places.

- [ ] **Step 1: Write the four failing tests**

T39 -- in `tests/test_answers.py` (beside the contract tests):

```python
def test_the_mark_contract_names_who_writes_raw_text():
    """A role following the contract writes an add's and a move's raw_text;
    the parse refuses either without it (`decision-log.md Process: #175`, `#176`)."""
    got = contracts()["stage_4c_mark"]["raw_text"]
    assert got["owed_by"] == ["add", "move"]
    assert "as it will read" in got["is"]
```

T19 -- in `tests/test_disposition_command.py`:

```python
def test_the_help_names_the_answer_the_parse_accepts():
    import comment_review.commands.disposition as disposition

    assert "taken-in" not in (disposition.__doc__ or "")
```

T6 -- in `tests/test_passes.py`, beside the existing disposition tests (use their `_contested()` and `Disposition` shape):

```python
def test_a_taken_in_naming_the_chief_is_refused_by_name():
    place = _contested()
    place.disposition = Disposition(
        address="m.py@b1", name="taken_in", side="copy-chief", prose="", reason="r"
    )
    got = dispositions_pass(place)
    assert got.state is State.REFUSED
    assert "the chief's own prose is a recast" in got.reasons[0]
```

T10 -- in `tests/test_bus.py`: two roles correcting different sentences of one paragraph fold to COMPOSED with a composed text (use the file's existing compose fixture, `patched` from helpers, or two `a_correct_setting` on different lines); assert `result.chief` holds no mark at that address and the collate line `"<out>: N places resolved"` counts settled places only (check `result.chief`'s mark count equals the number of places in `SETTLED`).

- [ ] **Step 2: Run them and see each fail**

Run: `uv run pytest -q tests/test_answers.py -k raw_text tests/test_disposition_command.py -k help_names tests/test_passes.py -k naming_the_chief tests/test_bus.py -k <your T10 test name>`
Expected: the T39 test on `KeyError: 'raw_text'`; the T19 test on the assert; the T6 test on `KeyError: 'copy-chief'`; the T10 test on a mark present at the composed place.

- [ ] **Step 3: The four fixes**

T39, `allowed()` in `desk/marks/mark.py`, add beside `anchor_form`:

```python
        # Who writes `raw_text` rather than copying it: the rows whose
        # `carries_raw_text` is set (`decision-log.md Process: #175`, `#176`).
        "raw_text": {
            "owed_by": sorted(
                name for name, spec in INSTRUCTIONS.items() if spec.carries_raw_text
            ),
            "is": "the paragraph as it will read, with your text in, in the page's own form",
        },
```

and the Returns line of the docstring names `raw_text`.

T19, `commands/disposition.py`: in the module docstring (and any help string), `taken-in` becomes `taken_in` at every occurrence.

T6, `desk/evaluate/passes.py::dispositions_pass`, after the `closes` check:

```python
    if place.disposition.side == CHIEF and row.side != CHIEF:
        return _set(
            place,
            State.REFUSED,
            reasons=(
                f"copy-chief: {place.disposition.name} takes a role's side or the"
                f" original; the chief's own prose is a recast",
            ),
        )
```

`row.side` is `CHIEF` on the recast row alone (`desk/dispositions/table.py`), so no row is named. Add one sentence to `dispositions_pass`' docstring: a ruling that names the chief's side where its row does not fix that side is refused by name.

T10, `flows/places.py::chief_copy_of`: skip a place whose `state` is not in `SETTLED` (import it from `desk.evaluate.state`), as well as one whose text is None; the docstring says the chief's copy holds the settled places, and that a composed or contested place's working text is the proof's.

- [ ] **Step 4: Run the four tests, then the suite**

Run the Step 2 command: all pass. Then `uv run pytest -q`: fix or report any case whose premise was a composed place on the chief's copy (T10) -- rewrite it to assert the proof carries the text instead, and name it in the report.

- [ ] **Step 5: Run the gates.** Expected: green.

- [ ] **Step 6: Commit the work** -- `fix: the four run traps -- the contract names raw_text, disposition says taken_in, a taken_in cannot name the chief, the chief's copy holds settled places`.

- [ ] **Step 7: Tick and commit** (gates again first)

```powershell
$work = git rev-parse HEAD
$r = 'rebuilt-middle-final-review.md'
job-board todo finish $r T39 --statement 'check --contract names raw_text and the rows that write it' --commit $work
job-board todo finish $r T19 --statement 'disposition docstring and help say taken_in' --commit $work
job-board todo finish $r T6 --statement 'a taken_in naming copy-chief is refused by name, not a KeyError' --commit $work
job-board todo finish $r T10 --statement 'the chief copy holds settled places only; composed text stays on the proof' --commit $work
job-board plan finish 0.2.4-the-placement-branch-runs P2 --statement 'the four run traps fixed, one test each seen failing first' --commit $work
job-board plan refresh 0.2.4-the-placement-branch-runs
git add TODO docs/plans
git commit -F <tick message file>
```

---

## Self-review

- **Spec coverage.** #197: a human query filed as a mark (Task 2, `_on_copies`) or given as an answer (Task 2, `_on_answers`) stops the fold; the answer goes back to the role that asked (H1, the refusal line and the file). #198: TOML, one `[[answer]]` per query, naming the role (Task 1). P2's four traps: Task 3.
- **Names across tasks.** `HumanQuery`, `HumanAnswer`, `FIELDS`, `queries_in_copies`, `queries_in_answers`, `read_answers`, `answered`, `AsksTheHuman`, `ASKS_THE_HUMAN`, `_human_answers`, `_asks`, `CopiesReturned.human`, `AnswersReturned.human`.
- **Review Focus.** 1: Task 2 turn test (placement key) with the Task 1 answers test (place key). 2 and 5: Task 1. 3: Task 1 reader and Task 2 commands. 4: Task 2.
- **Not here.** The agents' prose (board P3), the smoke (P4), the self-run (P5); deleting the held states and the write-end guard (`human-questions-before-the-fold` T5).
