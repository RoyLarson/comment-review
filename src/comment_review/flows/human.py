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

`corrections_to_matter` asks a second kind of question: every proposed mark that
changes the file's own matter, an `f` place, or moves text into one, is put to the
human for approval before the fold. `corrections_in_answers` asks it of a turn's
rewriting answers, and `corrections_in_rulings` of the chief's recasts.
"""

import tomllib
from typing import NamedTuple

from comment_review.desk.answers.table import asks_human
from comment_review.desk.marks.table import INSTRUCTIONS, Stance
from comment_review.desk.proof.answer import Answer
from comment_review.desk.proof.disposition import CHIEF, Disposition, RecastRuling
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import MoveMark
from comment_review.reading.addresser import COVERS, cue_of


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


#: The keys every `[[answer]]` carries, each a string holding more than whitespace.
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


def _in_matter(address: str) -> bool:
    """Whether `address` names an `f` place, the file's own matter."""
    cue = cue_of(address).cue
    return bool(cue) and cue_of(address).series == COVERS


def corrections_to_matter(
    copies: list[EditCopy], human: tuple[HumanAnswer, ...]
) -> list[HumanQuery]:
    """Every mark that changes an `f` place, or moves text into one, not yet answered.

    `decision-log.md Process: #274`, `#287`: each correction to the file's
    matter is put to the human on its own before the fold. An answer whose
    role, place and question are this one's answers it: the role holds the
    answer and its mark stands as it now reads, so it is not asked again. A
    mark changed after the answer -- its reason, or a move's destination --
    asks a different question and is asked again. A query is asked by
    `queries_in_copies`.
    """
    out = []
    for copy in copies:
        for sheet in copy.sheets:
            for mark in sheet.marks:
                if INSTRUCTIONS[mark.instruction].pairs(mark) is not Stance.PROPOSES:
                    continue
                into = isinstance(mark, MoveMark) and _in_matter(mark.to)
                if not (_in_matter(mark.address) or into):
                    continue
                to = f" -> {mark.to}" if isinstance(mark, MoveMark) else ""
                name = f"{mark.instruction}{to}"
                out.append(_approval(copy.role, mark.address, name, mark.reason))
    return _unanswered(out, human)


def corrections_in_answers(
    given: dict[str, dict[str, Answer]], human: tuple[HumanAnswer, ...]
) -> list[HumanQuery]:
    """Every turn's answer that rewrites an `f` place, not yet answered.

    `decision-log.md Process: #291`: a change to the file's matter is put to
    the human wherever it is made, so an answer that owes a `change` at an
    `f` place asks as a mark there does. A placement answer is keyed by its
    move and owes no change; a move into an `f` place asked when it was
    marked.

    Args:
        given: role -> slot key -> answer, as `queries_in_answers` takes them.
        human: the human's answers; one whose role, place and question are a
            query's answers it.
    """
    out = []
    for role in sorted(given):
        for at, answer in sorted(given[role].items()):
            if answer.owes_change and _in_matter(at):
                out.append(_approval(role, at, answer.name, answer.reason))
    return _unanswered(out, human)


def corrections_in_rulings(
    rulings: list[Disposition], human: tuple[HumanAnswer, ...]
) -> list[HumanQuery]:
    """Every chief's `recast` of an `f` place, not yet answered.

    A `taken_in` sets a role's text, or keeps the original; a role's text at
    an `f` place asked when the role proposed it.
    """
    out = [
        _approval(CHIEF, ruling.address, ruling.name, ruling.reason)
        for ruling in rulings
        if isinstance(ruling, RecastRuling) and _in_matter(ruling.address)
    ]
    return _unanswered(out, human)


def _approval(role: str, at: str, name: str, reason: str) -> HumanQuery:
    """The question that puts one change to the file's matter to the human."""
    return HumanQuery(role, at, f"approve this {name} to the file's matter: {reason}")


def _unanswered(
    queries: list[HumanQuery], human: tuple[HumanAnswer, ...]
) -> list[HumanQuery]:
    """`queries` less those an answer's role, place and question answer."""
    given = {(one.role, one.at, one.question) for one in human}
    return [q for q in queries if (q.role, q.at, q.question) not in given]


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
            if asks_human(answer):
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
        some sections are not tables, lack a non-blank string field, or answer
        a role, place and question an earlier section already answers -- the
        file does not say which of the two stands, so the later one is refused.
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
    first: dict[tuple[str, str, str], int] = {}
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
        answer = HumanAnswer(*(str(checked.get(key)) for key in FIELDS))
        key = (answer.role, answer.at, answer.question)
        if key in first:
            problems.append(
                f"{where}: answer {i} answers {answer.role} at {answer.at}"
                f" {answer.question!r}, which answer {first[key]} already answers"
            )
            continue
        first[key] = i
        out.append(answer)
    return out, problems


def answered(
    queries: list[HumanQuery], answers: list[HumanAnswer]
) -> list[tuple[HumanQuery, HumanAnswer | None]]:
    """Each query with the human's answer to it, or None where there is none yet.

    A section is the answer to a query where its role, its `at` and its
    question are the query's, as `corrections_to_matter` matches them: an
    answer to an earlier question at the same place does not answer a new one.
    A section for a question no copy still holds is left alone -- it is the
    record of a question already worked through. `read_answers` refuses two
    sections for one role, place and question, so each key here has one.
    """
    by = {(one.role, one.at, one.question): one for one in answers}
    return [
        (query, by.get((query.role, query.at, query.question))) for query in queries
    ]
