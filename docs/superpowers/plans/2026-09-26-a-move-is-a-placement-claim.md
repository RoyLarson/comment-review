# A Move Is a Placement Claim -- Implementation Plan (P7, P8, P1, P2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A move is one mark while its placement is open, answered on a `placement` question of its own, and is split into the mover's `drop` and `add` the moment every reader agrees -- replacing `Place.partner` and the pair passes.

**Architecture:** A new aggregate, `desk.evaluate.move.Move`, holds one move's placement: the pair of addresses, who filed it, who read either page, and the `placement` answers. `decide` runs a placement pass per move first; an agreed move is split on the place record into ordinary `drop` and `add` filings, a withdrawn one is taken off, and an open, contested, held or refused one holds its two ends. The places are then decided exactly as one-place marks are. The bus carries moves on the master proof beside the places and asks a placement slot once per open move.

**Tech Stack:** Python 3.11 stdlib only in `src/comment_review/` (it ships), pytest, ruff, ty -- all through `uv run`.

**Spec:** `docs/decision-log.md` Process #195 (the ruling), and the board plan `docs/plans/0.2.4-a-move-is-a-placement-claim.md` (the scope, the checks, the exclusions). Read both before Task 1.

**Board scope this document covers.** Roy, 2026-09-26: *"P1 P2 including associated todo tasks and this plans tasks necessary to accomplish and when they should be finished"*. P1 (the batch slot and the bus) and P2 (the split) need P7 (the placement question) and P8 (the move aggregate) first, so all four are here. P3 to P6 and P9 are not.

| board step | tasks here | ticks when | TODO tasks it closes |
| --- | --- | --- | --- |
| P7 | Task 1 | end of Task 1 | `move-is-a-composite-mark` T26 |
| P1 | Task 6 | end of Task 6 | `move-is-a-composite-mark` T29 |
| P8 | Tasks 2, 4, 5, 7 | end of Task 7 | `move-is-a-composite-mark` T27; `rebuilt-middle-final-review` T45, and T9 if Roy confirms D5 |
| P2 | Tasks 3, 4 | end of Task 7 | `move-is-a-composite-mark` T28, T1, T3, T4, T5, T31 |

P8 and P2 tick together because the aggregate and the split replace one set of functions (`pair_moves` and the partner reach): neither half leaves the suite green alone.

## Decisions this plan assumes -- Roy to confirm or correct at review

- **D1.** The mover's own filing is its agreement. The roles owed a placement say are the readers of either page, less the movers, less any role whose every mark at both ends is a deferring query.
- **D2.** A move no other role read is agreed at turn 0 and split in the same fold. This is the 4a case: ownership-context runs alone, so its moves land before 4c reads the revise.
- **D3.** While placement is open or contested, both ends keep the move filed as today and keep their own wording questions; an end that would settle is held carried, with no one asked about its words, until placement closes. A chief's ruling at an end is not held (the interim until P3 builds the placement ruling).
- **D4.** The split rewrites the place record: the move filing becomes the mover's `drop` at the origin and `add` at the destination, `Touch.OWN`. The next fold, the proof and the chief's copy see only those. A withdrawal removes the filing the same way. Both are final.
- **D5.** A move is identified by its own two addresses, not by a place. Two moves out of one origin, and two different roles' moves into one place, are separate moves whose texts compose at the shared place like any two proposals. One role's two moves into one place stay refused (#154). This is the answer `rebuilt-middle-final-review` T9 asks for, so T9 closes only on Roy's confirmation.
- **D6.** Placement answers and the placement state persist on `MasterProof.moves`, beside `places`.
- **D7.** A `stet` contests the move (#195 item 6). A contested move is put again each turn to its movers and the roles that stetted: a mover may `withdraw`, a stetter may `agree`. A `withdraw` from a role that did not file the move is refused by name.
- **D8.** `proof --only`'s pair refusal is deleted, not narrowed: a held move decides no text at either end, so there is nothing for it to refuse, and an agreed move has no pair rule (#195 item 5).
- **D9.** A split `add` whose destination anchor is empty names the destination address in backticks as `claim.anchor`, since the parse requires a backticked name and the write end checks the place's anchor, not the claim's.
- **D10.** `scripts/smoke_middle.ps1` goes red from Task 4 and stays red until board P9 rebuilds its move plants. The per-task gate is the pytest suite and the lint and type gates.

## Global Constraints

- Everything runs through `uv run`; Python floor is 3.11 (`.python-version`).
- `src/comment_review/**` imports the standard library only.
- No `except` clause holds a tuple literal; bind it to a name.
- Nothing outside `desk/marks/table.py`, `desk/answers/table.py` and `desk/dispositions/table.py` names a row: no `Instruction.X`, no `Answer.X`, no quoted `"taken_in"`, `"recast"`, `"stet"`, `"hold"`, `"withdraw"` (`tests/gates/test_tables_name_the_rows.py`).
- Files are ASCII; CRLF where git already stores CRLF.
- Edit with the file editor or a `.py` script under the scratchpad; no `sed`, no heredocs. Commit messages go in a file and use `git commit -F`.
- Commit messages end with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and the `Claude-Session:` line.
- Each task: work and verify, commit, tick, commit. Ticks go through `job-board`, never by hand.
- The gates after each task, in this order: `uv run ruff check .`, `uv run ruff format .`, `uv run python scripts/check_shipped_syntax.py`, `uv run ruff check .`, `uv run ty check`, `uv run pytest -q`.

## Review Focus

1. **A role answers a placement and a composition at the same origin in one turn.** Both are keyed by the origin's address today, so one would overwrite the other. Expected: both are read. Test in Task 6.
2. **A proof written before this change** -- no `moves` key, places carrying `partner` -- is handed to `turn` or `disposition`. Expected: it reads back, `partner` is ignored, and its moves are re-derived from the filed marks with no answers. Test in Task 5.
3. **A move into a place with no code line above it** (a closing gap, anchor ""). Expected: the split `add` round-trips through `Place.serialize` and `Place.deserialize`. Test in Task 3.
4. **A role that was not asked the placement answers it anyway.** Expected: refused by name as not put to that role, and the round rolls back. Test in Task 6.
5. **The snippet is not in the origin's paragraph when the move is agreed.** Expected: no split; the move stays filed and the origin's own read refuses it at both ends. Test in Task 4.

---

### Task 1: The placement question and its four answers (board P7)

**Files:**
- Modify: `src/comment_review/desk/answers/answer.py` (already modified in the working tree: `Question.PLACEMENT` and its docstring)
- Modify: `src/comment_review/desk/answers/table.py` (docstring already modified; `Effect.CONTESTS` and four rows still to add)
- Test: `tests/test_answers.py` (already modified: two new tests and three widened ones)

**Interfaces:**
- Produces: `Question.PLACEMENT == "placement"`; `Effect.CONTESTS == "contests"`; `ANSWERS[(Question.PLACEMENT, name)]` for `agree` (ACCEPTS), `stet` (CONTESTS), `withdraw` (REMOVES), `query` (ABSTAINS or UNSETTLABLE by `claim.shape`, owes `shape`, `attempted`, `settles`). No placement row owes a change. `contracts()["placement"]` is generated from these rows with no code change in `flows/answers.py`.

- [ ] **Step 1: Confirm the tests already in the working tree fail**

Run: `uv run pytest -q tests/test_answers.py`
Expected: 4 failed, 6 passed -- `test_the_placement_answers` on `AttributeError: CONTESTS` (PLACEMENT now exists), `test_a_placement_answer_is_read_against_its_question`, `test_the_contracts_are_the_tables_own_sets`, `test_the_contract_names_every_claim_key_the_parse_reads`.

- [ ] **Step 2: Add `CONTESTS` to `Effect`**

In `src/comment_review/desk/answers/table.py`, replace the `Effect` class with:

```python
class Effect(StrEnum):
    """What an answer does to the thing it answers about, once the row reads it.

    On an escalation or a composition that thing is the role's own side at the
    place. On a placement it is the move: `ACCEPTS` and `REMOVES` read the
    same way there, and `CONTESTS` is the placement's own -- the paragraph
    stays where it is by this role's reading, so the move is carried forward
    for the chief rather than agreed (`decision-log.md Process: #195`).
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    KEEPS = auto()
    REMOVES = auto()
    REPLACES = auto()
    ACCEPTS = auto()
    ABSTAINS = auto()
    UNSETTLABLE = auto()
    CONTESTS = auto()
```

- [ ] **Step 3: Add the four placement rows**

At the end of the `ANSWERS` dict, after the `(Question.COMPOSITION, "patch")` row:

```python
    (Question.PLACEMENT, "agree"): AnswerRow(
        Question.PLACEMENT, _always(Effect.ACCEPTS)
    ),
    (Question.PLACEMENT, "stet"): AnswerRow(
        Question.PLACEMENT, _always(Effect.CONTESTS)
    ),
    (Question.PLACEMENT, "withdraw"): AnswerRow(
        Question.PLACEMENT, _always(Effect.REMOVES)
    ),
    (Question.PLACEMENT, "query"): AnswerRow(
        Question.PLACEMENT,
        _query_effect,
        claim_all=("shape", "attempted", "settles"),
    ),
```

- [ ] **Step 4: Run the answers tests and the gate**

Run: `uv run pytest -q tests/test_answers.py tests/gates/test_tables_name_the_rows.py tests/test_check_command.py`
Expected: all pass.

- [ ] **Step 5: Confirm the contract publishes the question**

Run: `uv run python src/comment-review.py check --contract`
Expected: the JSON holds a `"placement"` key whose `"instruction"` is `["agree", "query", "stet", "withdraw"]` and whose `"owes_change"` is `[]`.

- [ ] **Step 6: Run the gates** (Global Constraints order). Expected: all green.

- [ ] **Step 7: Commit the work**

Message file: `feat: the placement question and its four answers (Process 195 item 6)` with a body naming the four rows and their effects.

```powershell
git add src/comment_review/desk/answers/answer.py src/comment_review/desk/answers/table.py tests/test_answers.py
git commit -F <message file>
```

- [ ] **Step 8: Tick and commit**

```powershell
$work = git rev-parse HEAD
job-board todo finish move-is-a-composite-mark.md T26 --statement 'Question.PLACEMENT and its four rows; check --contract prints them' --commit $work
job-board plan finish 0.2.4-a-move-is-a-placement-claim P7 --statement 'placement rows in desk/answers; contract generated from them' --commit $work
job-board plan refresh 0.2.4-a-move-is-a-placement-claim
git add TODO docs/plans
git commit -F <tick message file>
```

---

### Task 2: The move aggregate and its placement pass (part of board P8)

**Files:**
- Create: `src/comment_review/desk/evaluate/move.py`
- Test: `tests/test_move.py`

**Interfaces:**
- Consumes: `Question.PLACEMENT`, `Effect.CONTESTS` (Task 1); `Place`, `Filed` (`desk/evaluate/place.py`); `INSTRUCTIONS`, `Stance`, `Touch` (`desk/marks/table.py`).
- Produces:
  - `class Placement(StrEnum)`: `OPEN`, `AGREED`, `CONTESTED`, `WITHDRAWN`, `HELD`, `REFUSED`.
  - `UNDECIDED: frozenset[Placement]` = `{OPEN, CONTESTED}`; `FINAL: frozenset[Placement]` = `{AGREED, WITHDRAWN}`.
  - `key_of(origin: str, destination: str) -> str` returning `"<origin> -> <destination>"`.
  - `@dataclass class Move` with `origin`, `destination`, `movers: dict[str, Mark]`, `readers: tuple[str, ...]`, `answers: dict[int, dict[str, Answer]]`, `placement: Placement | None`, `owed`, `asking`, `reasons` (tuples of str), property `key`, `serialize() -> dict`, classmethod `deserialize(where, entry) -> tuple[Move | None, list[str]]`.
  - `moves_in(places: dict[str, Place], recorded: dict[str, Move] | None = None) -> dict[str, Move]`.
  - `one_role_twice(moves: dict[str, Move]) -> dict[str, tuple[str, ...]]` -- move key -> refusal reasons.
  - `placement_pass(move: Move, places: dict[str, Place], turn: int, refused: tuple[str, ...] = ()) -> Move`.

- [ ] **Step 1: Write the failing tests**

Create `tests/test_move.py`:

```python
"""The move: one placement claim over two places, and the pass that decides it.

`decision-log.md Process: #195`. A move claims where a paragraph belongs and
nothing else, so its placement is decided once for the pair, by every role
that read either page, before either end's words are.
"""

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.evaluate.move import (
    Move,
    Placement,
    moves_in,
    one_role_twice,
    placement_pass,
)
from comment_review.desk.evaluate.place import Filed, Place
from comment_review.desk.marks.mark import Instruction, Mark, Shape
from comment_review.desk.marks.table import Touch

ORIGIN, DESTINATION = "m.py@b1", "m.py@b5"
BASE = "# one\n# two\n# three\n"
LANDING = "# four\n# five\n"
LANDED = "# four\n# two\n# five\n"
HUMAN = {
    "shape": str(Shape.HUMAN_REVIEW_NECESSARY),
    "attempted": "read both ends",
    "settles": "the author",
}
DEFERRING = {
    "shape": str(Shape.OUTSIDE_MY_ROLE),
    "attempted": "read both ends",
    "settles": "ownership-context",
}


def _mark(instruction, address=ORIGIN, change="", raw_text=BASE, claim=None) -> Mark:
    return Mark(
        address=address,
        anchor="x = 1",
        raw_text=raw_text,
        instruction=instruction,
        claim=claim or {},
        reason="r",
        sources=(),
        change=change,
    )


def _move(origin=ORIGIN, destination=DESTINATION) -> Mark:
    return _mark(
        Instruction.MOVE,
        address=origin,
        change="# two\n",
        raw_text=LANDED,
        claim={"from": origin, "to": destination},
    )


def _ends(*, readers=("a", "b"), at_origin=(), at_destination=()) -> dict[str, Place]:
    move = _move()
    origin = Place(
        address=ORIGIN,
        anchor="x = 1",
        base=BASE,
        readers=readers,
        filed=[Filed("a", move, Touch.ORIGIN), *at_origin],
    )
    destination = Place(
        address=DESTINATION,
        anchor="y = 5",
        base=LANDING,
        readers=readers,
        filed=[Filed("a", move, Touch.DESTINATION), *at_destination],
    )
    return {ORIGIN: origin, DESTINATION: destination}


def _answer(name: str, claim=None) -> Answer:
    return Answer(
        address=ORIGIN,
        anchor="x = 1",
        question=Question.PLACEMENT,
        name=name,
        reason="r",
        claim=claim or {},
    )


def _decided(places, answers=None, turn=1) -> Move:
    (move,) = moves_in(places).values()
    if answers:
        move.answers[turn] = answers
    return placement_pass(move, places, turn)


def test_a_move_is_found_by_its_own_two_addresses():
    moves = moves_in(_ends())
    assert list(moves) == ["m.py@b1 -> m.py@b5"]
    move = moves["m.py@b1 -> m.py@b5"]
    assert set(move.movers) == {"a"} and move.readers == ("a", "b")


def test_a_move_no_other_role_read_is_agreed_at_once():
    """D2: ownership-context alone at 4a -- its moves land before 4c."""
    move = _decided(_ends(readers=("a",)), turn=0)
    assert move.placement is Placement.AGREED and move.owed == ()


def test_a_move_another_reader_has_not_answered_is_open_to_it():
    move = _decided(_ends(), turn=0)
    assert move.placement is Placement.OPEN and move.owed == ("b",)


def test_every_readers_agree_agrees_it():
    move = _decided(_ends(), {"b": _answer("agree")})
    assert move.placement is Placement.AGREED


def test_a_stet_contests_it_and_puts_it_to_the_mover_and_the_stetter():
    move = _decided(_ends(readers=("a", "b", "c")), {"b": _answer("stet"), "c": _answer("agree")})
    assert move.placement is Placement.CONTESTED
    assert move.owed == ("a", "b")


def test_a_stetter_who_later_agrees_closes_it():
    places = _ends()
    (move,) = moves_in(places).values()
    move.answers[1] = {"b": _answer("stet"), "a": _answer("agree")}
    move.answers[2] = {"b": _answer("agree"), "a": _answer("agree")}
    assert placement_pass(move, places, 2).placement is Placement.AGREED


def test_the_movers_withdraw_withdraws_it():
    move = _decided(_ends(), {"a": _answer("withdraw"), "b": _answer("agree")})
    assert move.placement is Placement.WITHDRAWN and move.movers == {}


def test_another_roles_withdraw_is_refused_by_name():
    move = _decided(_ends(), {"b": _answer("withdraw")})
    assert move.placement is Placement.REFUSED
    assert move.reasons and move.reasons[0].startswith("b: ")
    assert "only the role that filed a move withdraws it" in move.reasons[0]


def test_a_human_review_query_answer_holds_it():
    move = _decided(_ends(), {"b": _answer("query", HUMAN)})
    assert move.placement is Placement.HELD and move.asking == ("b: r",)


def test_a_human_review_query_filed_at_either_end_holds_it():
    query = _mark(Instruction.QUERY, address=DESTINATION, claim=HUMAN)
    move = _decided(_ends(at_destination=(Filed("b", query, Touch.OWN),)), turn=0)
    assert move.placement is Placement.HELD


def test_a_role_deferring_at_either_end_is_not_owed_the_placement():
    query = _mark(Instruction.QUERY, claim=DEFERRING)
    move = _decided(_ends(at_origin=(Filed("b", query, Touch.OWN),)), turn=0)
    assert move.placement is Placement.AGREED


def test_an_answer_to_another_question_is_refused():
    wrong = Answer(
        address=ORIGIN, anchor="x = 1", question=Question.COMPOSITION, name="clean", reason="r"
    )
    move = _decided(_ends(), {"b": wrong})
    assert move.placement is Placement.REFUSED


def test_an_agreed_move_stays_agreed():
    """D4: agreement is final -- the split has already been written."""
    places = _ends()
    (move,) = moves_in(places).values()
    move.placement = Placement.AGREED
    move.answers[2] = {"b": _answer("stet")}
    assert placement_pass(move, places, 2).placement is Placement.AGREED


def test_a_move_round_trips():
    move = _decided(_ends(), {"b": _answer("stet")})
    back, why = Move.deserialize("m", move.serialize())
    assert why == [] and back is not None
    assert (back.origin, back.destination, back.placement) == (ORIGIN, DESTINATION, Placement.CONTESTED)
    assert back.answers == move.answers and back.owed == move.owed


def test_one_roles_two_moves_into_one_place_are_refused():
    """#154."""
    places = _ends()
    second = _move(origin="m.py@b3")
    places["m.py@b3"] = Place(
        address="m.py@b3", anchor="z = 3", base=BASE, filed=[Filed("a", second, Touch.ORIGIN)]
    )
    places[DESTINATION].filed.append(Filed("a", second, Touch.DESTINATION))
    refused = one_role_twice(moves_in(places))
    assert set(refused) == {"m.py@b1 -> m.py@b5", "m.py@b3 -> m.py@b5"}


def test_two_roles_moves_into_one_place_are_two_moves_and_neither_is_refused():
    """D5: a move is its own two addresses; the texts compose at the place."""
    places = _ends()
    second = _move(origin="m.py@b3")
    places["m.py@b3"] = Place(
        address="m.py@b3", anchor="z = 3", base=BASE, filed=[Filed("b", second, Touch.ORIGIN)]
    )
    places[DESTINATION].filed.append(Filed("b", second, Touch.DESTINATION))
    moves = moves_in(places)
    assert set(moves) == {"m.py@b1 -> m.py@b5", "m.py@b3 -> m.py@b5"}
    assert one_role_twice(moves) == {}


def test_a_recorded_moves_answers_survive_being_found_again():
    places = _ends()
    (move,) = moves_in(places).values()
    move.answers[1] = {"b": _answer("stet")}
    again = moves_in(places, {move.key: move})
    assert again[move.key].answers == {1: {"b": _answer("stet")}}
    assert set(again[move.key].movers) == {"a"}
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest -q tests/test_move.py`
Expected: collection error, `ModuleNotFoundError: No module named 'comment_review.desk.evaluate.move'`.

- [ ] **Step 3: Write the module**

Create `src/comment_review/desk/evaluate/move.py`:

```python
"""A move: one placement claim over two places, and the pass that decides it.

`decision-log.md Process: #195`. A move claims that a paragraph is located
wrongly and belongs at its destination, and nothing about the wording of
either end. So its placement is one question for the pair, put to every role
that read either page, and decided here before either end's words are:

    OPEN        a reader owed a say has not answered it
    AGREED      every reader owed a say agreed -- final; the move is split
    CONTESTED   a reader answered `stet`; carried forward for the chief
    WITHDRAWN   every mover withdrew it -- final; the filing comes off
    HELD        a human-review query was filed at an end, or answered
    REFUSED     an answer this question does not take, or #154

A move is identified by its own two addresses (`key_of`), never by a place:
two moves through one place are two moves.
"""

from dataclasses import dataclass, field
from enum import StrEnum, auto

from comment_review.desk.answers.answer import Answer, Question
from comment_review.desk.answers.table import ANSWERS, Effect
from comment_review.desk.evaluate.place import Place
from comment_review.desk.marks.mark import Mark
from comment_review.desk.marks.table import INSTRUCTIONS, Stance, Touch


class Placement(StrEnum):
    """Where one move's placement stands, once the pass has read it."""

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    OPEN = auto()
    AGREED = auto()
    CONTESTED = auto()
    WITHDRAWN = auto()
    HELD = auto()
    REFUSED = auto()


#: The placements a fold carries forward, to a turn or to the chief.
UNDECIDED = frozenset({Placement.OPEN, Placement.CONTESTED})
#: The placements no later answer changes: the record has been rewritten.
FINAL = frozenset({Placement.AGREED, Placement.WITHDRAWN})


def key_of(origin: str, destination: str) -> str:
    """One move's name, from its own two addresses."""
    return f"{origin} -> {destination}"


@dataclass
class Move:
    """One move's placement, the roles that filed it, and what they were asked.

    `movers` and `readers` are derived from the places each fold
    (`moves_in`) and are not serialized; the answers and what the pass
    decided are, so a turn knows which moves are still open and whom to ask.
    """

    origin: str
    destination: str
    movers: dict[str, Mark] = field(default_factory=dict)
    readers: tuple[str, ...] = ()
    answers: dict[int, dict[str, Answer]] = field(default_factory=dict)
    placement: Placement | None = None
    owed: tuple[str, ...] = ()
    asking: tuple[str, ...] = ()
    reasons: tuple[str, ...] = ()

    @property
    def key(self) -> str:
        return key_of(self.origin, self.destination)

    def serialize(self) -> dict:
        """This move's recorded fields, keyed by this class's own field names."""
        return {
            "origin": self.origin,
            "destination": self.destination,
            "answers": {
                str(t): {r: a.serialize() for r, a in by.items()}
                for t, by in self.answers.items()
            },
            "placement": str(self.placement) if self.placement else None,
            "owed": list(self.owed),
            "asking": list(self.asking),
            "reasons": list(self.reasons),
        }

    @classmethod
    def deserialize(cls, where: str, entry: object) -> "tuple[Move | None, list[str]]":
        """One recorded entry becomes a `Move`, or becomes named problems."""
        if not isinstance(entry, dict):
            return None, [f"{where}: a move must be an object"]
        data: dict = entry
        origin, destination = data.get("origin"), data.get("destination")
        if not isinstance(origin, str) or not origin:
            return None, [f"{where}: a move needs its `origin`"]
        if not isinstance(destination, str) or not destination:
            return None, [f"{where}: a move needs its `destination`"]
        problems: list[str] = []
        answers: dict[int, dict[str, Answer]] = {}
        for turn, by in (data.get("answers") or {}).items():
            for role, raw in by.items():
                answer, why = Answer.deserialize(f"{where} turn {turn} {role}", raw)
                if answer is None:
                    problems += why
                else:
                    answers.setdefault(int(turn), {})[role] = answer
        if problems:
            return None, problems
        placement = data.get("placement")
        return (
            cls(
                origin=origin,
                destination=destination,
                answers=answers,
                placement=Placement(placement) if placement else None,
                owed=tuple(data.get("owed") or ()),
                asking=tuple(data.get("asking") or ()),
                reasons=tuple(data.get("reasons") or ()),
            ),
            [],
        )


def moves_in(
    places: dict[str, Place], recorded: dict[str, "Move"] | None = None
) -> dict[str, Move]:
    """Every move filed on these places, carrying what the record holds of each.

    A move is found at its origin, where it is filed with `Touch.ORIGIN`, and
    named by its two addresses. A move the record holds and no place files
    any longer -- agreed and split, or withdrawn -- keeps its record with no
    movers, so its final placement is still reported.

    Args:
        places: address -> place, as the fold holds them.
        recorded: key -> move, as the proof last recorded them; None at the
            first fold.

    Returns:
        key -> move, movers and readers derived from these places.
    """
    out: dict[str, Move] = dict(recorded or {})
    for move in out.values():
        move.movers = {}
    for place in places.values():
        for one in place.filed:
            if one.touch is not Touch.ORIGIN:
                continue
            written = INSTRUCTIONS[one.mark.instruction].places(one.mark)
            destination = next(
                (where for where, touch in written if touch is Touch.DESTINATION), ""
            )
            if not destination:
                continue
            key = key_of(place.address, destination)
            move = out.setdefault(key, Move(place.address, destination))
            move.movers[one.role] = one.mark
    for move in out.values():
        ends = (places.get(move.origin), places.get(move.destination))
        move.readers = tuple(
            sorted({role for end in ends if end for role in end.readers})
        )
    return out


def one_role_twice(moves: dict[str, Move]) -> dict[str, tuple[str, ...]]:
    """The moves `decision-log.md Process: #154` sends back: one role's two into one place.

    The order and wording of two paragraphs one role lands at one place are
    ambiguous, so both moves are refused back to that role. Two roles' moves
    into one place are not this: each is its own move, and their texts
    compose at the place as any two proposals do.

    Returns:
        key -> the reasons, for every move one role filed into a place it
        also filed another move into.
    """
    by_landing: dict[tuple[str, str], list[Move]] = {}
    for move in moves.values():
        for role in move.movers:
            by_landing.setdefault((role, move.destination), []).append(move)
    out: dict[str, tuple[str, ...]] = {}
    for (role, destination), same in by_landing.items():
        if len(same) < 2:
            continue
        named = ", ".join(sorted(move.key for move in same))
        reason = (
            f"{role}: two of its moves land at {destination} -- {named}; their"
            " order and wording are ambiguous, so file one move carrying both"
        )
        for move in same:
            out[move.key] = out.get(move.key, ()) + (reason,)
    return out


def placement_pass(
    move: Move, places: dict[str, Place], turn: int, refused: tuple[str, ...] = ()
) -> Move:
    """Decide one move's placement from what was filed at its ends and answered.

    A mover's filing is its agreement. The roles owed a say are the readers
    of either page, less the movers, less a role whose every mark at both
    ends defers; an answer up to `turn` narrows them. A final placement is
    left as it is.

    Args:
        move: the move, its movers and readers from `moves_in`.
        places: the fold's places, where its two ends are read.
        turn: the last turn whose placement answers are applied.
        refused: reasons another rule refuses this move for, as
            `one_role_twice` gives them.

    Returns:
        `move`, decided.
    """
    if move.placement in FINAL:
        return move
    ends = [end for end in (places.get(move.origin), places.get(move.destination)) if end]
    stances: dict[str, set[Stance]] = {}
    asking: list[str] = []
    for end in ends:
        for one in end.filed:
            stance = INSTRUCTIONS[one.mark.instruction].pairs(one.mark)
            stances.setdefault(one.role, set()).add(stance)
            if stance is Stance.UNSETTLABLE:
                asking.append(f"{one.role}: {one.mark.reason}")
    deferring = {role for role, held in stances.items() if held == {Stance.DEFERS}}
    movers = dict(move.movers)
    accepted: set[str] = set()
    stetted: set[str] = set()
    reasons = list(refused)
    for at in sorted(t for t in move.answers if t <= turn):
        for role, answer in move.answers[at].items():
            row = ANSWERS.get((answer.question, answer.name))
            if row is None or answer.question is not Question.PLACEMENT:
                reasons.append(f"{role}: {answer.name} is not an answer to a placement")
                continue
            effect = row.effect(answer)
            if effect is Effect.ACCEPTS:
                accepted.add(role)
                stetted.discard(role)
            elif effect is Effect.CONTESTS:
                stetted.add(role)
                accepted.discard(role)
            elif effect is Effect.REMOVES and role in movers:
                movers.pop(role)
            elif effect is Effect.REMOVES:
                reasons.append(
                    f"{role}: only the role that filed a move withdraws it -- stet"
                    " it to keep the paragraph where it is"
                )
            elif effect is Effect.UNSETTLABLE:
                asking.append(f"{role}: {answer.reason}")
            elif effect is Effect.ABSTAINS:
                deferring.add(role)
    move.movers = movers
    move.reasons, move.asking, move.owed = tuple(reasons), (), ()
    if reasons:
        move.placement = Placement.REFUSED
    elif not movers:
        move.placement = Placement.WITHDRAWN
    elif asking:
        move.placement, move.asking = Placement.HELD, tuple(asking)
    elif stetted:
        move.placement = Placement.CONTESTED
        move.owed = tuple(sorted(set(movers) | stetted))
    else:
        owed = set(move.readers) - set(movers) - deferring - accepted
        move.owed = tuple(sorted(owed))
        move.placement = Placement.OPEN if owed else Placement.AGREED
    return move
```

- [ ] **Step 4: Run the tests**

Run: `uv run pytest -q tests/test_move.py tests/gates/test_tables_name_the_rows.py`
Expected: all pass. If `Shape.OUTSIDE_MY_ROLE` is not the member name, read `desk/marks/mark.py`'s `Shape` and use the member whose value is `"outside-my-role"`.

- [ ] **Step 5: Run the gates.** Expected: green. Nothing else imports the module yet.

- [ ] **Step 6: Commit** -- `feat: a move is one placement claim, decided once for the pair (Process 195)`. No tick: P8 ticks at the end of Task 7.

---

### Task 3: The split, as the move row's own answer (part of board P2)

**Files:**
- Modify: `src/comment_review/desk/marks/table.py`
- Test: `tests/test_marks_table.py`

**Interfaces:**
- Produces: `Row.splits: Splits | None`, where `Splits = Callable[[Any, str, str], tuple[Any, Any] | None]`, called as `row.splits(mark, origin_base, destination_anchor)`. The `move` row's returns `(drop, add)` -- a `drop` at `mark.address` whose `change` is the origin's remainder and whose `claim.drop` is the snippet, and an `add` at `claim.to` whose `raw_text` is the arrival paragraph and whose `change` is the snippet -- or `None` where the snippet is not in the origin's paragraph exactly once. Every other row's `splits` is `None`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_marks_table.py` (add any missing imports at the top: `Instruction`, `Mark`, `INSTRUCTIONS`, `Touch`, `Filed`, `Place`):

```python
class TestTheSplit:
    """`decision-log.md Process: #195` item 3: an agreed move becomes the
    mover's `drop` at the origin and `add` at the destination, ordinary marks
    each end reads on its own from then on."""

    BASE = "# one\n# two\n# three\n"
    LANDING = "# four\n# five\n"
    LANDED = "# four\n# two\n# five\n"

    def _move(self, change="# two\n") -> Mark:
        return Mark(
            address="m.py@b1",
            anchor="x = 1",
            raw_text=self.LANDED,
            instruction=Instruction.MOVE,
            claim={"from": "m.py@b1", "to": "m.py@b5"},
            reason="it belongs with five",
            sources=({"cite": "m.py:5", "verbatim": "v5 = 5"},),
            change=change,
        )

    def _split(self, anchor="y = 5", change="# two\n"):
        move = self._move(change)
        return INSTRUCTIONS[move.instruction].splits(move, self.BASE, anchor)

    def test_only_the_move_row_splits(self):
        assert [i for i, row in INSTRUCTIONS.items() if row.splits] == [Instruction.MOVE]

    def test_the_drop_leaves_the_remainder_and_the_add_lands_the_arrival(self):
        drop, add = self._split()
        assert (drop.instruction, drop.address) == (Instruction.DROP, "m.py@b1")
        assert drop.claim == {"drop": "# two\n"} and drop.change == "# one\n# three\n"
        assert (add.instruction, add.address) == (Instruction.ADD, "m.py@b5")
        assert add.raw_text == self.LANDED and add.change == "# two\n"
        assert add.anchor == "y = 5" and add.claim["anchor"] == "`y = 5`"
        assert drop.reason == add.reason == "it belongs with five"
        assert drop.sources == add.sources == self._move().sources

    def test_each_half_is_an_ordinary_mark_the_parse_takes(self):
        """T1: no second shape of `change` -- each half is a plain string."""
        for half in self._split():
            back, why = Mark.deserialize("half", half.serialize())
            assert why == [] and back == half

    def test_each_half_sets_its_end_through_its_own_row(self):
        """T3 and T5: the text removed at the origin is the text the add
        carries, by construction -- both come from the one snippet."""
        drop, add = self._split()
        assert INSTRUCTIONS[drop.instruction].sets(drop, Touch.OWN, self.BASE) == "# one\n# three\n"
        assert INSTRUCTIONS[add.instruction].sets(add, Touch.OWN, self.LANDING) == self.LANDED
        assert drop.claim["drop"] == add.change

    def test_an_arrival_that_loses_a_word_of_the_landing_is_refused(self):
        """T4: the add row's own read refuses it by the word it lost."""
        _drop, add = self._split()
        lost = Mark(**{**add.__dict__, "raw_text": "# four\n# two\n"})
        why = INSTRUCTIONS[lost.instruction].reads(lost, Touch.OWN, self.LANDING)
        assert why and "five" in why[0]

    def test_a_snippet_not_in_the_origin_does_not_split(self):
        assert self._split(change="# nine\n") is None

    def test_a_landing_with_no_code_line_names_the_address_as_its_anchor(self):
        """D9 and Review Focus 3: an empty anchor would be refused by the
        parse, so the add names its destination instead, and still reads back
        off a place."""
        _drop, add = self._split(anchor="")
        assert add.claim["anchor"] == "`m.py@b5`"
        place = Place(address="m.py@b5", anchor="", base="", filed=[Filed("a", add, Touch.OWN)])
        back, why = Place.deserialize("p", place.serialize())
        assert why == [] and back is not None and back.filed[0].mark == add
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest -q tests/test_marks_table.py -k TestTheSplit`
Expected: FAIL with `AttributeError: 'Row' object has no attribute 'splits'`.

- [ ] **Step 3: Add the row field and the move's split**

In `src/comment_review/desk/marks/table.py`:

After the `Pairs = ...` alias:

```python
Splits = Callable[[Any, str, str], "tuple[Any, Any] | None"]
```

After `_move_reads`:

```python
def _move_splits(mark, origin_base, destination_anchor):
    """An agreed move as the mover's `drop` at the origin and `add` at the destination.

    `decision-log.md Process: #195` item 3. Both halves come from the one
    snippet, so the text the origin loses is the text the destination gains
    by construction; each keeps the move's reason and sources. None where the
    snippet is not in the origin's paragraph exactly once -- the move's own
    read refuses that, and a split would hide it.

    An add's claim names its anchor in backticks and the parse refuses an
    empty name, so a landing with no code line above it names its address.
    """
    remainder = _without_once(origin_base, mark.change)
    if remainder is None:
        return None
    destination = str(mark.claim.get("to", ""))
    named = destination_anchor.strip() or destination
    drop = Mark(
        address=mark.address,
        anchor=mark.anchor,
        raw_text=origin_base,
        instruction=Instruction.DROP,
        claim={"drop": mark.change},
        reason=mark.reason,
        sources=mark.sources,
        change=remainder,
    )
    add = Mark(
        address=destination,
        anchor=destination_anchor,
        raw_text=mark.raw_text,
        instruction=Instruction.ADD,
        claim={"missing": mark.change.strip().splitlines()[0], "anchor": f"`{named}`"},
        reason=mark.reason,
        sources=mark.sources,
        change=mark.change,
    )
    return drop, add
```

In `class Row`, after `pairs: Pairs = _proposes`:

```python
    #: How an agreed mark of this row becomes one-place marks
    #: (`decision-log.md Process: #195`). None for every row but `move`.
    splits: Splits | None = None
```

In the `Instruction.MOVE` row, add `splits=_move_splits,`.

- [ ] **Step 4: Run the tests**

Run: `uv run pytest -q tests/test_marks_table.py tests/gates/test_tables_name_the_rows.py tests/gates/test_mark_shape.py`
Expected: all pass. If `test_each_half_is_an_ordinary_mark_the_parse_takes` fails on the add's `claim.missing`, read the refusal: `Mark.deserialize` checks `claim_all` keys are filled strings, and the first line of a snippet that is only whitespace would be empty -- the snippet here is not.

- [ ] **Step 5: Run the gates.** Expected: green.

- [ ] **Step 6: Commit** -- `feat: the move row splits an agreed move into a drop and an add (Process 195 item 3)`. No tick.

---

### Task 4: `decide` over places and moves; the pair passes go (parts of board P8 and P2)

**Files:**
- Modify: `src/comment_review/desk/evaluate/passes.py`
- Modify: `src/comment_review/desk/evaluate/move.py` (add `settle_ends`, `hold_ends`)
- Modify: `src/comment_review/desk/evaluate/place.py` (delete `partner`)
- Modify: `src/comment_review/desk/answers/table.py` (delete `reaches_partner`)
- Modify: `src/comment_review/desk/marks/table.py` (delete `_sets_both_ends`; `chief_mark` takes no partner)
- Modify: `src/comment_review/flows/places.py` (no partner assignment; `chief_copy_of` hands no partner)
- Test: `tests/test_passes.py`, `tests/test_places.py`, `tests/test_marks_table.py`, `tests/test_place.py`

**Interfaces:**
- Consumes: `Move`, `Placement`, `moves_in`, `one_role_twice`, `placement_pass` (Task 2); `Row.splits` (Task 3).
- Produces:
  - `decide(places: dict[str, Place], moves: dict[str, Move] | None = None, turn: int = 0) -> dict[str, Place]` -- mutates `moves` too.
  - `marks_pass(place)`, `answers_pass(place, turn)`, `owed_a_say(place, text, sides, turn=0)` -- no `partner` argument.
  - `settle_ends(move, places) -> None` and `hold_ends(move, places) -> None` in `move.py`.
  - `chief_mark(place) -> Mark` -- no `partner` argument; a mark writing two places is never returned whole.
  - Deleted: `pair_moves`, `_moves_crossing`, `refuse_half_moves`, `_OUTSIDE_THE_GUARD`, `_one_mark_at_both`, `_withdrew_at_the_partner`, `_accepting`, `Place.partner`, `AnswerRow.reaches_partner`, `_sets_both_ends`.

- [ ] **Step 1: Write the failing tests**

In `tests/test_passes.py`: delete `test_a_moves_two_places_take_one_state`, `test_an_end_held_for_the_human_by_its_partner_decides_no_text`, `test_decide_pairs_a_moves_ends_before_the_chief_rules_them`, `test_decide_carries_a_refused_ruling_to_the_other_end_of_the_move`, `test_decide_leaves_a_held_move_holding_both_ends_and_deciding_no_text`, the whole `TestAnAnswerReachesBothEndsOfTheMove` class, and `TestATextEveryReaderMustHaveSeen.test_a_role_deferring_at_one_end_of_a_move_defers_at_the_other` (its rule is now `test_move.py::test_a_role_deferring_at_either_end_is_not_owed_the_placement`). Remove `pair_moves` from the import. Every rule those tests held is either restated below or superseded by #195 (the reach, #188 and #189 have nothing left to guard once a wording answer cannot touch a move). Then add:

```python
class TestAMoveIsDecidedBeforeItsEnds:
    """`decision-log.md Process: #195`: the placement is decided once for the
    pair, and the ends are decided as ordinary places after it."""

    MOVED = "# two\n"
    LANDING = "# four\n# five\n"
    LANDED = "# four\n# two\n# five\n"
    REMAINDER = "# one\n# three\n"

    def _places(self, readers=("a", "b"), change=None):
        move = _mark(
            Instruction.MOVE,
            change=change or self.MOVED,
            raw_text=self.LANDED,
            claim={"from": "m.py@b1", "to": "m.py@b5"},
        )
        origin = _place(Filed("a", move, Touch.ORIGIN))
        destination = _place(
            Filed("a", move, Touch.DESTINATION), base=self.LANDING, address="m.py@b5"
        )
        destination.anchor = "y = 5"
        origin.readers = destination.readers = readers
        places = {"m.py@b1": origin, "m.py@b5": destination}
        return places, moves_in(places)

    def _placement(self, name, claim=None):
        return _answer(name, claim=claim, question=Question.PLACEMENT)

    def test_a_move_only_its_mover_read_splits_and_settles_at_turn_0(self):
        places, moves = self._places(readers=("a",))
        decide(places, moves)
        origin, destination = places["m.py@b1"], places["m.py@b5"]
        assert [one.mark.instruction for one in origin.filed] == [Instruction.DROP]
        assert [one.mark.instruction for one in destination.filed] == [Instruction.ADD]
        assert (origin.state, origin.text) == (State.STANDS, self.REMAINDER)
        assert (destination.state, destination.text) == (State.STANDS, self.LANDED)

    def test_an_open_move_keeps_both_ends_open_and_asks_their_words_too(self):
        places, moves = self._places()
        decide(places, moves)
        assert moves["m.py@b1 -> m.py@b5"].placement is Placement.OPEN
        for end in places.values():
            assert end.state is State.COMPOSED and end.owed == ("b",)

    def test_agree_and_clean_in_one_turn_split_and_settle_it(self):
        places, moves = self._places()
        decide(places, moves)
        moves["m.py@b1 -> m.py@b5"].answers[1] = {"b": self._placement("agree")}
        for end in places.values():
            end.answers[1] = {"b": _answer("clean", question=Question.COMPOSITION)}
        decide(places, moves, turn=1)
        assert places["m.py@b1"].text == self.REMAINDER
        assert places["m.py@b5"].text == self.LANDED
        assert all(end.state is State.AGREED for end in places.values())
        assert places["m.py@b5"].filed[0].mark.instruction is Instruction.ADD

    def test_a_stet_holds_both_ends_whatever_their_words_came_to(self):
        places, moves = self._places()
        decide(places, moves)
        moves["m.py@b1 -> m.py@b5"].answers[1] = {"b": self._placement("stet")}
        for end in places.values():
            end.answers[1] = {"b": _answer("clean", question=Question.COMPOSITION)}
        decide(places, moves, turn=1)
        assert moves["m.py@b1 -> m.py@b5"].placement is Placement.CONTESTED
        for end in places.values():
            assert end.state in CARRIED and end.owed == ()
            assert end.filed[0].mark.instruction is Instruction.MOVE

    def test_the_movers_withdraw_takes_the_move_off_both_ends(self):
        places, moves = self._places()
        decide(places, moves)
        moves["m.py@b1 -> m.py@b5"].answers[1] = {"a": self._placement("withdraw")}
        decide(places, moves, turn=1)
        assert all(end.filed == [] for end in places.values())
        assert all(end.state is State.STANDS and end.text is None for end in places.values())

    def test_a_held_move_holds_both_ends_and_decides_no_text(self):
        places, moves = self._places()
        decide(places, moves)
        human = {"shape": str(Shape.HUMAN_REVIEW_NECESSARY), "attempted": "a", "settles": "b"}
        moves["m.py@b1 -> m.py@b5"].answers[1] = {"b": self._placement("query", human)}
        decide(places, moves, turn=1)
        for end in places.values():
            assert end.state is State.UNSETTLABLE and end.text is None

    def test_a_snippet_not_in_the_origin_is_refused_at_both_ends_and_not_split(self):
        """Review Focus 5."""
        places, moves = self._places(readers=("a",), change="# nine\n")
        decide(places, moves)
        for end in places.values():
            assert end.state is State.REFUSED
            assert end.filed[0].mark.instruction is Instruction.MOVE
```

Add to the imports: `from comment_review.desk.evaluate.move import Placement, moves_in` and `from comment_review.desk.evaluate.state import CARRIED, State` (merge with the existing `State` import).

In `tests/test_places.py`, `tests/test_marks_table.py` and `tests/test_place.py`: delete every test that sets or asserts `partner`, and every test of `_sets_both_ends` or of `chief_mark(place, partner)`. Run `uv run pytest -q tests/test_places.py tests/test_marks_table.py tests/test_place.py` after the deletions to see the list is complete: each remaining failure should be an `AttributeError`/`TypeError` about `partner`, which means a test was missed.

Add to `tests/test_marks_table.py`:

```python
def test_a_mark_writing_two_places_is_never_the_chiefs_mark_whole():
    """Before P3 the chief rules a move's ends one at a time, so each end is
    written from its own decided text -- a move taken whole at one end would
    land at an end the chief may have recast."""
    move = Mark(
        address="m.py@b1", anchor="x = 1", raw_text="# four\n# two\n# five\n",
        instruction=Instruction.MOVE, claim={"from": "m.py@b1", "to": "m.py@b5"},
        reason="r", sources=({"cite": "m.py:1", "verbatim": "v0 = 0"},), change="# two\n",
    )
    place = Place(
        address="m.py@b1", anchor="x = 1", base="# one\n# two\n# three\n",
        filed=[Filed("a", move, Touch.ORIGIN)], text="# one\n# three\n",
    )
    got = chief_mark(place)
    assert got.instruction is not Instruction.MOVE and got.change == "# one\n# three\n"
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest -q tests/test_passes.py -k TestAMoveIsDecidedBeforeItsEnds`
Expected: FAIL -- `decide()` takes no `moves` argument.

- [ ] **Step 3: Add `settle_ends` and `hold_ends` to `move.py`**

Add the imports `from comment_review.desk.evaluate.place import Filed, Place` (replacing the `Place`-only import) and `from comment_review.desk.evaluate.state import CARRIED, SETTLED, State`, then append:

```python
def _is_this_move(one: Filed, move: Move) -> bool:
    written = INSTRUCTIONS[one.mark.instruction].places(one.mark)
    return {where for where, _ in written} == {move.origin, move.destination} and len(
        written
    ) > 1


def settle_ends(move: Move, places: dict[str, Place]) -> None:
    """Write a final placement onto the two place records.

    AGREED: each remaining mover's filing becomes its `drop` at the origin
    and `add` at the destination (`Row.splits`), and a mover that withdrew
    comes off. WITHDRAWN: every filing of this move comes off. A split the
    row declines -- the snippet is not in the origin -- leaves the move
    filed, so the origin's own read refuses it.
    """
    if move.placement not in FINAL:
        return
    origin, destination = places.get(move.origin), places.get(move.destination)
    if origin is None or destination is None:
        return
    if move.placement is Placement.AGREED:
        halves = {}
        for role, mark in move.movers.items():
            row = INSTRUCTIONS[mark.instruction]
            split = row.splits(mark, origin.base, destination.anchor) if row.splits else None
            if split is None:
                return
            halves[role] = split
    else:
        halves = {}
    for end, index in ((origin, 0), (destination, 1)):
        kept = [one for one in end.filed if not _is_this_move(one, move)]
        added = [Filed(role, split[index], Touch.OWN) for role, split in sorted(halves.items())]
        end.filed = kept + added


def hold_ends(move: Move, places: dict[str, Place]) -> None:
    """Hold a move's two ends to its placement while it is not final.

    HELD: both ends ride to the author and decide no text. REFUSED, or either
    end refused on its own: both are refused, with every reason. OPEN or
    CONTESTED: an end that would settle is carried with nobody asked about
    its words, since the paragraph may not be moving; an end already carried
    keeps its own question. An end the chief ruled on is left as ruled.
    """
    if move.placement in FINAL:
        return
    ends = [end for end in (places.get(move.origin), places.get(move.destination)) if end]
    if move.placement is Placement.HELD:
        for end in ends:
            end.state, end.text, end.question, end.owed = State.UNSETTLABLE, None, None, ()
            end.asking = end.asking or move.asking
        return
    refused = move.placement is Placement.REFUSED or any(
        end.state is State.REFUSED for end in ends
    )
    if refused:
        reasons = move.reasons + tuple(r for end in ends for r in end.reasons)
        for end in ends:
            end.state, end.text = State.REFUSED, None
            end.reasons = tuple(dict.fromkeys(reasons))
        return
    for end in ends:
        if end.disposition is None and end.state in SETTLED:
            end.state, end.owed, end.question = State.COMPOSED, (), None
```

Note on `question = None` for a held-settled end: the fold reports a carried place only where `asked(place)` names someone (Task 5), so an end held for placement alone prints nothing of its own; the move's `PlacementCarried` event is what reports it.

- [ ] **Step 4: Rewrite `decide` and drop `partner` from the passes**

In `src/comment_review/desk/evaluate/passes.py`:

1. Module docstring: `"""The three passes over a place, run after each move's placement is decided."""`
2. Delete `_moves_crossing`, `pair_moves`, `_one_mark_at_both`, `_withdrew_at_the_partner`, `_accepting`, `refuse_half_moves`, `_OUTSIDE_THE_GUARD`.
3. `owed_a_say(place, text, sides, turn=0)`: delete the `partner` parameter, its Args entry and the bold paragraph about a role that withdrew at the other end; the body becomes:

```python
    filed_by = _by_role(place)
    answered = {
        role for at, by_role in place.answers.items() if at <= turn for role in by_role
    }
    deferring = _deferring(place)
    out = []
    for role in set(place.readers) | set(filed_by):
        if role in deferring:
            continue
        if sides.get(role) == text:
            continue
        if role not in sides and role in answered:
            continue
        out.append(role)
    return tuple(sorted(out))
```

4. `marks_pass(place)`: delete the `partner` parameter and its Args entry, delete the `crossed = _moves_crossing(place)` block, and call `_from_sides(place, sides)`.
5. `answers_pass(place, turn)`: replace the body with:

```python
    if place.state not in CARRIED:
        return place
    sides = dict(place.sides)
    for role, answer in place.answers.get(turn, {}).items():
        row = ANSWERS.get((answer.question, answer.name))
        if row is None:
            return _set(
                place,
                State.REFUSED,
                reasons=(f"{role}: {answer.name} is not an answer to {answer.question}",),
            )
        effect = row.effect(answer)
        if effect is Effect.UNSETTLABLE:
            return _set(place, State.UNSETTLABLE, asking=(f"{role}: {answer.reason}",))
        if effect is Effect.REMOVES:
            sides.pop(role, None)
        elif effect is Effect.REPLACES:
            sides[role] = answer.change
        elif effect is Effect.ACCEPTS and place.text is not None:
            sides[role] = place.text
    return _from_sides(place, sides, turn)
```

and its docstring loses the `!!` paragraph about a withdrawal at the other end.
6. `_from_sides(place, sides, turn=0)`: delete `partner`; its two `owed_a_say` calls drop the `partner` argument.
7. `decide`:

```python
def decide(
    places: dict[str, Place], moves: "dict[str, Move] | None" = None, turn: int = 0
) -> dict[str, Place]:
    """Every move's placement, then every place, in the one order they run in.

    `decision-log.md Process: #195`: a move is a placement claim decided once
    for the pair before either end's words. So each move's placement pass
    runs first and a final one is written onto the two place records -- the
    split, or the withdrawal. Then each place's marks and answers, as for any
    one-place mark; then every move not yet final holds its two ends; then
    the chief's dispositions; then the hold again, so a ruling refused at one
    end of an unsplit move refuses the other.

    Args:
        places: address -> place, each from its own record. Mutated.
        moves: key -> move, from `desk.evaluate.move.moves_in`. Mutated.
            None where the caller has none, which is every place alone.
        turn: the turn to decide at -- every answer up to it is applied.

    Returns:
        `places`, decided.
    """
    moves = {} if moves is None else moves
    refused = one_role_twice(moves)
    for move in moves.values():
        placement_pass(move, places, turn, refused.get(move.key, ()))
        settle_ends(move, places)
    for place in places.values():
        marks_pass(place)
        for t in range(1, turn + 1):
            answers_pass(place, t)
    for move in moves.values():
        hold_ends(move, places)
    for place in places.values():
        dispositions_pass(place)
    for move in moves.values():
        hold_ends(move, places)
    return places
```

with `from comment_review.desk.evaluate.move import Move, hold_ends, one_role_twice, placement_pass, settle_ends` at the top. If that import cycles (`move.py` imports nothing from `passes.py`, so it should not), move the import under `TYPE_CHECKING` for `Move` only.

- [ ] **Step 5: Delete `Place.partner`, `AnswerRow.reaches_partner`, `_sets_both_ends`**

- `desk/evaluate/place.py`: delete the `partner` field, its `"partner"` line in `serialize`, and `partner=data.get("partner")` in `deserialize`.
- `desk/answers/table.py`: delete `reaches_partner` from `AnswerRow`, its paragraph in the docstring, and `reaches_partner=True` from the escalation `withdraw` row.
- `desk/marks/table.py`: delete `_sets_both_ends`. In `chief_mark`, delete the `partner` parameter and its Args entry, and replace the loop with:

```python
    filed_marks = _in_role_order(place)
    for filed in filed_marks:
        row = INSTRUCTIONS[filed.mark.instruction]
        if len(row.places(filed.mark)) > 1:
            continue
        if row.sets(filed.mark, filed.touch, place.base) == place.text:
            return filed.mark
```

and the docstring sentence about `_sets_both_ends` becomes: *"A mark writing two places is never returned whole: an agreed move has been split into one-place marks already (`Process: #195`), and an unsplit one is written end by end from each end's decided text."*
- `flows/places.py`: in `places_of`, delete the `for other, _touch in written:` loop and the sentence *"Where one mark writes at two places, each names the other as `partner`."*; in `chief_copy_of`, call `chief_mark(place)` and replace the docstring's move paragraph with *"A move reaches this as the `drop` and `add` the fold split it into (`decision-log.md Process: #195`), each placed on its own page."*

- [ ] **Step 6: Run the tests**

Run: `uv run pytest -q tests/test_passes.py tests/test_move.py tests/test_places.py tests/test_marks_table.py tests/test_place.py tests/test_answers.py`
Expected: all pass.

Run: `uv run pytest -q`
Expected: failures only in `tests/test_fold.py`, `tests/test_bus.py`, `tests/test_collate_command.py`, `tests/test_turn_command.py`, `tests/test_disposition_command.py`, `tests/test_proof_command.py`, `tests/test_revise.py` -- the callers Tasks 5 to 7 rewire. Record the failing test names in the commit body; each must be green or deleted by the end of Task 7.

- [ ] **Step 7: Run ruff, format, the floor check and ty.** Expected: green (pytest is recorded above).

- [ ] **Step 8: Commit** -- `feat: decide runs each move's placement first and splits an agreed move; the pair passes go (Process 195)`. The body lists what was deleted and the failing callers. No tick.

---

### Task 5: The fold reports moves; the proof carries them (part of board P8)

**Files:**
- Modify: `src/comment_review/desk/work/fold.py`, `src/comment_review/desk/work/events.py`
- Modify: `src/comment_review/desk/containers.py` (`MasterProof.moves`)
- Test: `tests/test_fold.py`, `tests/test_containers.py`

**Interfaces:**
- Consumes: `decide(places, moves, turn)` (Task 4); `Move`, `Placement`, `UNDECIDED` (Task 2).
- Produces:
  - `Fold(places, moves=..., turn=0)`; `Fold.decided_moves -> dict[str, Move]` (empty on a rollback).
  - `events.PlacementCarried(origin: str, destination: str, placement: Placement, roles: tuple[str, ...])`.
  - `events.Unsettlable` unchanged in shape; for a held move it is emitted once, from the move, with `address=origin`, `partner=destination`, `move=HeldMove(mover, reason, origin, destination)`.
  - `MasterProof.moves: tuple[dict, ...]` (`wire: False`), serialized as `"moves"`, read back where present.

- [ ] **Step 1: Write the failing tests**

In `tests/test_fold.py`, delete the tests that set `partner` (four references) and add:

```python
from comment_review.desk.evaluate.move import Placement, moves_in


def _a_move_between(readers):
    move = Mark(
        address="m.py@b1", anchor="x = 1", raw_text="# four\n# two\n# five\n",
        instruction=Instruction.MOVE, claim={"from": "m.py@b1", "to": "m.py@b5"},
        reason="it belongs with five", sources=(), change="# two\n",
    )
    origin = Place(address="m.py@b1", anchor="x = 1", base="# one\n# two\n# three\n",
                   readers=readers, filed=[Filed("a", move, Touch.ORIGIN)])
    destination = Place(address="m.py@b5", anchor="y = 5", base="# four\n# five\n",
                        readers=readers, filed=[Filed("a", move, Touch.DESTINATION)])
    places = {"m.py@b1": origin, "m.py@b5": destination}
    return places, moves_in(places)


def test_an_open_move_is_reported_once_with_whom_it_is_put_to():
    places, moves = _a_move_between(("a", "b"))
    fold = Fold(places, moves).run()
    carried = [e for e in fold.events if isinstance(e, events.PlacementCarried)]
    assert carried == [events.PlacementCarried("m.py@b1", "m.py@b5", Placement.OPEN, ("b",))]
    assert fold.decided_moves["m.py@b1 -> m.py@b5"].placement is Placement.OPEN


def test_a_held_move_is_one_unsettlable_naming_both_ends():
    places, moves = _a_move_between(("a", "b"))
    human = {"shape": str(Shape.HUMAN_REVIEW_NECESSARY), "attempted": "a", "settles": "b"}
    query = Mark(address="m.py@b5", anchor="y = 5", raw_text="# four\n# five\n",
                 instruction=Instruction.QUERY, claim=human, reason="ask", sources=(), change="")
    places["m.py@b5"].filed.append(Filed("b", query, Touch.OWN))
    fold = Fold(places, moves).run()
    held = [e for e in fold.events if isinstance(e, events.Unsettlable)]
    assert len(held) == 1
    assert (held[0].address, held[0].partner) == ("m.py@b1", "m.py@b5")
    assert held[0].move == events.HeldMove("a", "it belongs with five", "m.py@b1", "m.py@b5")


def test_a_rolled_back_fold_decides_no_move():
    places, moves = _a_move_between(("a",))
    places["m.py@b1"].filed[0] = Filed(
        "a", replace(places["m.py@b1"].filed[0].mark, change="# nine\n"), Touch.ORIGIN
    )
    fold = Fold(places, moves_in(places)).run()
    assert not fold.committed and fold.decided_moves == {}
```

(`replace` from `dataclasses`; add `Filed`, `Place`, `Mark`, `Instruction`, `Shape`, `Touch` imports as the file lacks them.)

In `tests/test_containers.py` add:

```python
def test_a_master_proof_carries_its_moves_and_reads_back_one_written_before_them():
    """Review Focus 2: a proof written before moves existed still reads."""
    proof = MasterProof(stage="4c", read_from={}, edit_copies=(), places=(),
                        moves=({"origin": "m.py@b1", "destination": "m.py@b5"},))
    back, why = MasterProof.deserialize("4c", proof.serialize())
    assert why == [] and back is not None and back.moves == proof.moves
    older = {**proof.serialize()}
    del older["moves"]
    older["places"] = [{"address": "m.py@b1", "partner": "m.py@b5"}]
    back, why = MasterProof.deserialize("4c", older)
    assert why == [] and back is not None and back.moves == ()
```

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest -q tests/test_fold.py tests/test_containers.py -k "move or moves"`
Expected: FAIL -- `Fold` takes no `moves`; `MasterProof` has no `moves`.

- [ ] **Step 3: Add `moves` to `MasterProof`**

In `desk/containers.py`, directly under `places: tuple[dict, ...] = field(...)`:

```python
    moves: tuple[dict, ...] = field(default=(), metadata={"wire": False})
```

Its docstring entry, after `places`: *"moves: every move one fold of this stage decided, as `desk.evaluate.move.Move.serialize` writes one. `wire: False`, like `places`, and absent from a proof written before `decision-log.md Process: #195`."* In `serialize`, add `"moves": [dict(m) for m in self.moves],`. In `deserialize`, read `raw_moves = data.get("moves")` exactly as `raw_places` is read at `containers.py:698-701`, and pass `moves=moves` beside `places=places`.

- [ ] **Step 4: Add the event and rewire the fold**

In `desk/work/events.py`, after `CarriedForward`:

```python
class PlacementCarried(NamedTuple):
    """A move whose placement the fold could not settle -- asked of `roles` next turn.

    `decision-log.md Process: #195`. `open` is put to the readers who have
    not answered; `contested` to its movers and the roles that stetted it.
    A committed fold's only, as the module docstring says.
    """

    origin: str
    destination: str
    placement: "Placement"
    roles: tuple[str, ...]
```

with `from comment_review.desk.evaluate.move import Placement` at the top (if it cycles, import under `TYPE_CHECKING`), and add `PlacementCarried` to the `Event` union.

In `desk/work/fold.py`:
- `Fold` gains `moves: dict[str, Move] = field(default_factory=dict)` after `places`, and a property:

```python
    @property
    def decided_moves(self) -> dict[str, Move]:
        """The moves, if committed -- empty on a rollback, nothing to save."""
        return self.moves if self.committed else {}
```

- `run()` calls `decide(self.places, self.moves, self.turn)`. Before the per-place loop, collect the ends of held moves:

```python
        held_ends = {
            end
            for move in self.moves.values()
            if move.placement is Placement.HELD
            for end in (move.origin, move.destination)
        }
```

- In the per-place loop: the `CarriedForward` branch appends only `if asked(place)`; the `UNSETTLABLE` branch becomes: `if address in held_ends: pass` else emit one `Unsettlable(address, role, reason)` per `place.asking` entry with no partner and no move.
- After the per-place loop, before the refusal check:

```python
        for key in sorted(self.moves):
            move = self.moves[key]
            if move.placement in UNDECIDED:
                on_commit.append(
                    events.PlacementCarried(
                        move.origin, move.destination, move.placement, move.owed
                    )
                )
            elif move.placement is Placement.HELD:
                mover = min(move.movers) if move.movers else ""
                reason = move.movers[mover].reason if mover else ""
                held = events.HeldMove(mover, reason, move.origin, move.destination)
                for one in move.asking:
                    role, _, why = one.partition(": ")
                    on_commit.append(
                        events.Unsettlable(move.origin, role, why, move.destination, held)
                    )
```

- Delete `_held_with`, `_prints`, `_held_move`. The module docstring's order paragraph gains: *"Each move's placement is decided before its places are (`decision-log.md Process: #195`)."*

- [ ] **Step 5: Run the tests**

Run: `uv run pytest -q tests/test_fold.py tests/test_containers.py tests/test_move.py tests/test_passes.py`
Expected: all pass.

- [ ] **Step 6: Run ruff, format, the floor check, ty.** Expected: green. Full pytest still fails only in the callers Task 6 and 7 rewire.

- [ ] **Step 7: Commit** -- `feat: the fold reports a move once and the proof carries moves (Process 195)`. No tick.

---

### Task 6: The placement slot, the bus and the answer check (board P1)

**Files:**
- Modify: `src/comment_review/flows/bus.py`
- Modify: `src/comment_review/flows/answers.py` (`slot_key`; `answers_of` keys by it)
- Modify: `src/comment_review/commands/check.py:212-216` (`sent` keyed by `slot_key`)
- Test: `tests/test_bus.py`, `tests/test_answers.py`

**Interfaces:**
- Consumes: `Fold(places, moves, turn)`, `Fold.decided_moves`, `MasterProof.moves` (Task 5); `moves_in`, `Move.deserialize`, `UNDECIDED`, `key_of` (Task 2).
- Produces:
  - `slot_key(entry: dict) -> str` in `flows/answers.py`: `key_of(address, to)` where the entry carries a `to`, else its address.
  - A placement slot in a role's batch: `{"address": origin, "to": destination, "anchor": origin's anchor, "question": "placement", "movers": [...], "snippet": ..., "raw_text": the arrival paragraph, "instruction": None, "read_from": {...}}`, one per undecided move, for each role in `move.owed`.
  - `answers_of(role, sent, returned, unsent, root, cache)` -- same signature; `sent` and the result are keyed by `slot_key`.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_answers.py`:

```python
def test_a_placement_and_a_composition_at_one_origin_are_two_answers(tmp_path):
    """Review Focus 1: both are asked of one role at one address in one turn."""
    from comment_review.flows.answers import answers_of, slot_key

    sent = {
        "m.py@b1": {"question": "composition", "anchor": "x = 1"},
        slot_key({"address": "m.py@b1", "to": "m.py@b5"}): {"question": "placement", "anchor": "x = 1"},
    }
    returned = [
        {"address": "m.py@b1", "instruction": "clean", "reason": "r"},
        {"address": "m.py@b1", "to": "m.py@b5", "instruction": "agree", "reason": "r"},
    ]
    got, problems = answers_of("b", sent, returned, lambda a: "not sent", tmp_path, {})
    assert problems == []
    assert got["m.py@b1"].name == "clean"
    assert got["m.py@b1 -> m.py@b5"].name == "agree"
```

Add to `tests/test_bus.py`:

```python
MOVED_FROM = "# one\n# two\n# three"
ARRIVAL = "# four\n# two\n# five\n# six"


def _a_move_two_roles_read(tmp_path):
    root = tmp_path / "repo"
    binder = a_real_binder_over(root, {"m.py@b1": MOVED_FROM, "m.py@b2": OTHER})
    by_role = {
        "block-context": {
            "m.py@b1": a_move("m.py@b1", "m.py@b2", change="# two\n", reads=ARRIVAL),
            "m.py@b2": a_clean("m.py@b2"),
        },
        "module-context": {"m.py@b1": a_clean("m.py@b1"), "m.py@b2": a_clean("m.py@b2")},
    }
    copies = [returned(wire) for wire in copies_over(binder, by_role)]
    return CopiesReturned("4c", copies, binder, root, None), root


def _answering(batch_slots, answer_for):
    out = []
    for slot in batch_slots:
        name = answer_for(slot)
        out.append({**slot, "instruction": name, "reason": "r"})
    return out


class TestAMovesPlacementIsAskedOnce:
    """`decision-log.md Process: #195`, board P1."""

    def test_the_other_reader_is_sent_one_placement_slot(self, tmp_path):
        message, _root = _a_move_two_roles_read(tmp_path)
        out, result = handle(message)
        assert result is not None
        slots = [s for s in result.batch["module-context"] if s["question"] == "placement"]
        assert [(s["address"], s["to"]) for s in slots] == [("m.py@b1", "m.py@b2")]
        assert slots[0]["raw_text"] == ARRIVAL and slots[0]["snippet"] == "# two\n"
        assert "block-context" not in result.batch or not [
            s for s in result.batch["block-context"] if s["question"] == "placement"
        ]
        assert [m["placement"] for m in result.proof.moves] == ["open"]

    def test_agree_and_clean_land_the_paragraph_once(self, tmp_path):
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        answers = {
            role: _answering(slots, lambda s: "agree" if s["question"] == "placement" else "clean")
            for role, slots in first.batch.items()
        }
        out, result = handle(AnswersReturned(first.proof, answers, root))
        assert result is not None, out
        texts = {p["address"]: p["text"] for p in result.proof.places}
        assert texts["m.py@b1"] == "# one\n# three"
        assert texts["m.py@b2"] == ARRIVAL
        chief = [(m.instruction, m.address) for s in result.chief.sheets for m in s.marks]
        assert sorted(chief) == [("add", "m.py@b2"), ("drop", "m.py@b1")]

    def test_a_stet_puts_it_to_the_mover_and_the_stetter(self, tmp_path):
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        answers = {
            role: _answering(slots, lambda s: "stet" if s["question"] == "placement" else "clean")
            for role, slots in first.batch.items()
        }
        _out, result = handle(AnswersReturned(first.proof, answers, root))
        assert result is not None
        assert [m["placement"] for m in result.proof.moves] == ["contested"]
        for role in ("block-context", "module-context"):
            assert [s["to"] for s in result.batch[role] if s["question"] == "placement"] == ["m.py@b2"]

    def test_a_placement_answer_from_a_role_not_asked_is_refused(self, tmp_path):
        """Review Focus 4."""
        message, root = _a_move_two_roles_read(tmp_path)
        _out, first = handle(message)
        answers = {
            role: _answering(slots, lambda s: "agree" if s["question"] == "placement" else "clean")
            for role, slots in first.batch.items()
        }
        stray = {"address": "m.py@b1", "to": "m.py@b2", "instruction": "agree", "reason": "r"}
        answers.setdefault("block-context", []).append(stray)
        out, result = handle(AnswersReturned(first.proof, answers, root))
        assert result is None
        assert any(
            isinstance(e, events.Refused) and e.role == "block-context" for e in out
        )
```

(Import `a_move`, `a_clean` from `tests.helpers` and `events` from `comment_review.desk.work` if the file lacks them. `OTHER` is `test_bus.py`'s existing `"# four\n# five\n# six"`.)

Also delete or rewrite every `test_bus.py` case that reads `partner` (seven references): a case whose premise is a move's two ends taking one state, or a mover's answer reaching the other end, is deleted; a case whose premise is a move settling is rewritten to answer the placement `agree` first, as `test_agree_and_clean_land_the_paragraph_once` does.

- [ ] **Step 2: Run to verify they fail**

Run: `uv run pytest -q tests/test_answers.py -k placement_and_a_composition tests/test_bus.py -k TestAMovesPlacementIsAskedOnce`
Expected: FAIL -- `slot_key` does not exist; the batch holds no placement slot.

- [ ] **Step 3: Key answers by slot**

In `flows/answers.py`, after `ANSWER_VALUES`:

```python
def slot_key(entry: dict) -> str:
    """Which slot an entry answers: its address, or its move where it names one.

    A placement is asked of a move, at its origin's address, so a role can be
    asked a placement and a composition at one address in one turn. The move
    slot carries `to`, and the two are told apart by it.
    """
    address = str(entry.get("address") or "")
    to = entry.get("to")
    return key_of(address, str(to)) if address and to else address
```

with `from comment_review.desk.evaluate.move import key_of`. In `answers_of`, replace `address = str(entry.get("address") or "")` with `address = slot_key(entry)` in the first loop (the "names no address" check is unchanged since `slot_key` returns `""` exactly when the address is empty), and update the Args line for `sent` to *"slot key -> the slot that went out there (`slot_key`)"*. The module docstring's *"one of two questions"* becomes *"one of three questions"*.

In `commands/check.py:212-216`, key `sent` by `slot_key(slot)` and import it with `answers_of`.

- [ ] **Step 4: Carry moves through the bus**

In `flows/bus.py`:

- Import `from comment_review.desk.evaluate.move import UNDECIDED, Move, moves_in`.
- `_on_copies`: build `places = places_of(copies, bases, anchors)` and `fold = Fold(places, moves_in(places), turn=0).run()`; pass `moves=tuple(m.serialize() for m in fold.decided_moves.values())` to `MasterProof`; build the batch with `_batch_of(carried, _undecided(fold), fold.decided, read_from)` and make it None only when both lists are empty.
- Add:

```python
def _undecided(fold: Fold) -> list[Move]:
    """The moves this fold carries forward, in key order."""
    return [fold.decided_moves[k] for k in sorted(fold.decided_moves)
            if fold.decided_moves[k].placement in UNDECIDED]


def _moves_on(proof: MasterProof) -> tuple[dict[str, Move], list[Problem]]:
    """The proof's recorded moves, read back, or one `Problem` per reason they are not."""
    moves: dict[str, Move] = {}
    problems: list[Problem] = []
    for i, entry in enumerate(proof.moves):
        where = f"move {i}"
        move, why = Move.deserialize(where, entry)
        if move is None:
            problems += [Problem(THE_PROOF, where, one.removeprefix(f"{where}: ")) for one in why]
        else:
            moves[move.key] = move
    return moves, problems
```

- `_on_answers`: after `_places_on`, read `recorded, why = _moves_on(message.proof)`; `problems += why`; `moves = moves_in(places, recorded)`; `open_moves = {k: m for k, m in moves.items() if m.placement in UNDECIDED}`; `roles` also includes every role in each open move's `owed`; each role's `sent` gains `{key: {"question": "placement", "anchor": places[m.origin].anchor if m.origin in places else ""} for key, m in open_moves.items() if role in m.owed}`; when writing answers, `target = moves[address].answers if address in moves else places[address].answers`, then `target.setdefault(turn, {})[role] = answer`; call `_commit(message.proof, places, moves, turn)`.
- `_unsent(places, moves, role)`: for an address in `moves`, answer `"not an open move"` when its placement is not undecided, else `f"not put to {role} -- this move is put to {', '.join(m.owed)}"`.
- `_on_dispositions`: read the moves the same way and call `_commit(message.proof, places, moves_in(places, recorded), turn_of(message.proof))`.
- `_commit(proof, places, moves, turn)`: `Fold(places, moves, turn=turn)`; `moves=tuple(...)` on the next proof; batch as in `_on_copies`.
- `_batch_of(carried, moves, places, read_from)`: after the place slots,

```python
    for move in moves:
        mover = min(move.movers) if move.movers else ""
        mark = move.movers.get(mover)
        origin = places.get(move.origin)
        for role in move.owed:
            batch.setdefault(role, []).append(
                {
                    "address": move.origin,
                    "to": move.destination,
                    "anchor": origin.anchor if origin else "",
                    "question": "placement",
                    "movers": sorted(move.movers),
                    "snippet": mark.change if mark else "",
                    "raw_text": mark.raw_text if mark else "",
                    "instruction": None,
                    "read_from": {**read_from},
                }
            )
```

Its docstring gains: *"And one slot per move whose placement is undecided, for each role it is put to (`decision-log.md Process: #195`): the move's two addresses, the snippet and the paragraph it arrives as."* The string `"placement"` here is the question's value, not a row name, so the tables gate does not read it; write it as `str(Question.PLACEMENT)` to keep the one spelling.

- [ ] **Step 5: Run the tests**

Run: `uv run pytest -q tests/test_bus.py tests/test_answers.py tests/test_check_command.py tests/test_turn_command.py`
Expected: all pass. A `test_turn_command.py` case that builds a move and expects it to settle without a placement answer is rewritten to answer `agree`, as in Step 1.

- [ ] **Step 6: Run the gates.** Expected: ruff, format, floor, ty green; pytest fails only in `test_collate_command.py`, `test_disposition_command.py`, `test_proof_command.py`, `test_revise.py` if Task 7's sites still read `partner`.

- [ ] **Step 7: Commit the work** -- `feat: an open move is asked its placement once, beside its ends' words (Process 195, board P1)`.

- [ ] **Step 8: Tick and commit**

```powershell
$work = git rev-parse HEAD
job-board todo finish move-is-a-composite-mark.md T29 --statement 'placement slot per open move to every owed reader; tests/test_bus.py TestAMovesPlacementIsAskedOnce' --commit $work
job-board plan finish 0.2.4-a-move-is-a-placement-claim P1 --statement 'batch slot and bus: agree lands once, stet contests, a stray answer is refused' --commit $work
job-board plan refresh 0.2.4-a-move-is-a-placement-claim
git add TODO docs/plans
git commit -F <tick message file>
```

P1's box names withdraw and hold: `test_move.py` holds both at the pass (`test_the_movers_withdraw_withdraws_it`, `test_a_human_review_query_answer_holds_it`) and `test_passes.py` at the places; the bus test covers agree and stet end to end.

---

### Task 7: The last readers of the pair, and the P8 and P2 ticks

**Files:**
- Modify: `src/comment_review/commands/collate.py` (`_lines`, `_code_for`)
- Modify: `src/comment_review/flows/transcribe.py` (`_approved`: the pair refusal goes, D8)
- Test: `tests/test_collate_command.py`, `tests/test_proof_command.py`, `tests/test_disposition_command.py`, `tests/test_revise.py`

**Interfaces:**
- Consumes: `events.PlacementCarried` (Task 5).
- Produces: the console line `"<placement> <origin> -> <destination>: <roles> (placement)"`; exit `ESCALATIONS` on a contested placement and `REREADS` on an open one.

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_collate_command.py`:

```python
def test_an_undecided_move_prints_one_line_and_sets_the_exit_code():
    from comment_review.commands.collate import ESCALATIONS, REREADS, _code_for, _lines
    from comment_review.desk.evaluate.move import Placement

    opened = events.PlacementCarried("m.py@b1", "m.py@b5", Placement.OPEN, ("b",))
    contested = events.PlacementCarried("m.py@b1", "m.py@b5", Placement.CONTESTED, ("a", "b"))
    assert _lines(opened) == ["open m.py@b1 -> m.py@b5: b (placement)"]
    assert _code_for([opened, events.Committed(2)]) == REREADS
    assert _code_for([contested, events.Committed(2)]) == ESCALATIONS
```

In `tests/test_proof_command.py`, delete the cases that assert *"is the other end of a move filed here and is not approved"* (D8; a cut leaves no test behind).

- [ ] **Step 2: Run to verify it fails**

Run: `uv run pytest -q tests/test_collate_command.py -k undecided_move`
Expected: FAIL -- `_lines` returns `[]` for the event.

- [ ] **Step 3: Print and code the event; delete the pair refusal**

`commands/collate.py`, in `_lines` before the `Settled` branch:

```python
    if isinstance(event, events.PlacementCarried):
        roles = ", ".join(event.roles)
        return [
            f"{event.placement} {event.origin} -> {event.destination}: {roles} (placement)"
        ]
```

In `_code_for`, after `carried = ...`:

```python
    placements = [one for one in out if isinstance(one, events.PlacementCarried)]
    if any(one.placement is Placement.CONTESTED for one in placements):
        return ESCALATIONS
```

and the composition check becomes `if placements or any(one.question is Question.COMPOSITION for one in carried): return REREADS`. Import `Placement`. `_for_the_human` is unchanged: a held move still arrives as one `Unsettlable` with `partner` and `move` set.

`flows/transcribe.py::_approved`: delete the loop over `named` that reads `place.partner` and the docstring paragraph beginning *"One end of a move without the other is the second."*; the opening line says *"One refusal"*. Add to the docstring: *"A move's two ends are approved each on its own: an agreed move reaches the proof as a `drop` and an `add` (`decision-log.md Process: #195` item 5), and a held one sets nothing at either end."*

- [ ] **Step 4: Run the whole suite**

Run: `uv run pytest -q`
Expected: all pass. A remaining failure in `test_disposition_command.py` or `test_revise.py` is a case built on a move settling or being ruled without a placement answer: rewrite it to answer `agree` (a move that settles) or `stet` (a move the chief rules, which before board P3 is still ruled end by end), keeping what the case asserts about the chief or the docket.

- [ ] **Step 5: Confirm nothing reads the pair**

Run: `git grep -n "\.partner\b\|reaches_partner\|refuse_half_moves\|pair_moves\|_sets_both_ends\|_moves_crossing" -- src/`
Expected: no output. `partner` survives only as the field name on `events.Unsettlable`, which this grep does not match because it is not read as `.partner` in `src/` outside `commands/collate.py`'s `event.partner` -- if that line appears, it is the one expected match; confirm it is `event.partner` in `_for_the_human` and nothing else.

- [ ] **Step 6: Run the gates.** Expected: all green.

- [ ] **Step 7: Commit the work** -- `feat: collate prints an undecided move; proof --only drops the pair refusal (Process 195 item 5)`.

- [ ] **Step 8: Tick P8 and P2 and their TODO tasks, and commit**

```powershell
$work = git rev-parse HEAD
$f = 'move-is-a-composite-mark.md'
job-board todo finish $f T27 --statement 'desk/evaluate/move.py Move and placement_pass; decide runs it first; no .partner read in src' --commit $work
job-board todo finish $f T28 --statement 'Row.splits on move; settle_ends writes the drop and add on agreement' --commit $work
job-board todo finish $f T1 --statement 'split halves are ordinary Marks the parse takes; test_marks_table TestTheSplit' --commit $work
job-board todo finish $f T3 --statement 'origin half is base minus the snippet by construction; a snippet not in it does not split' --commit $work
job-board todo finish $f T4 --statement 'the add row refuses an arrival that loses a landing word; TestTheSplit' --commit $work
job-board todo finish $f T5 --statement 'drop.claim.drop == add.change: one snippet makes both halves' --commit $work
job-board todo finish $f T31 --statement 'reaches_partner, refuse_half_moves and the 189 guard deleted' --commit $work
job-board todo finish rebuilt-middle-final-review.md T45 --statement 'a move is keyed by its own two addresses; two out of one origin are two moves' --commit $work
job-board plan finish 0.2.4-a-move-is-a-placement-claim P8 --statement 'Move aggregate replaces Place.partner and the pair passes; suite green' --commit $work
job-board plan finish 0.2.4-a-move-is-a-placement-claim P2 --statement 'agreed move split into drop and add; the reach and the half-move guard deleted' --commit $work
job-board plan refresh 0.2.4-a-move-is-a-placement-claim
git add TODO docs/plans
git commit -F <tick message file>
```

`rebuilt-middle-final-review` T9 is a decision box. Close it with `todo finish ... --statement 'Roy confirmed D5 ...'` citing the decision-log commit only after Roy confirms D5 and the ruling is recorded; otherwise leave it `[ ]`.

---

## Self-review

- **Spec coverage.** #195 items 1-3 and 6 are Tasks 1-4 and 6; item 5 is Task 7's D8; item 4 (the chief) is board P3 and out of this document, with D3 and `chief_mark`'s change as the interim. Board P7, P8, P1, P2 each have a task and a tick step.
- **Placeholders.** Commit message files are named by content, not supplied verbatim; every code step carries its code.
- **Names used across tasks.** `Placement`, `UNDECIDED`, `FINAL`, `key_of`, `Move.key`, `moves_in`, `one_role_twice`, `placement_pass`, `settle_ends`, `hold_ends`, `Row.splits`, `PlacementCarried`, `Fold.decided_moves`, `MasterProof.moves`, `slot_key`.
- **Review Focus.** Each of the five has its test in the owning task: 1 in Task 6, 2 in Task 5, 3 in Task 3, 4 in Task 6, 5 in Task 4.
