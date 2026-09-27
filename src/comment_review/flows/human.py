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
        checked: dict = row
        missing = [
            key
            for key in FIELDS
            if not isinstance(checked.get(key), str)
            or not str(checked.get(key)).strip()
        ]
        if missing:
            problems.append(f"{where}: answer {i} needs {', '.join(missing)}")
            continue
        out.append(HumanAnswer(*(str(checked.get(key)) for key in FIELDS)))
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
