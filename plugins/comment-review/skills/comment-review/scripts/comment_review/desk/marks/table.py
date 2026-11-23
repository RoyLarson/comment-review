"""The marks table: one row per instruction, and every reader asks the row.

A row says which places a mark touches, what text it sets at each, what
problems it has against its base, and how it pairs with other marks at a place.
What a mark's claim carries, and every other fact its own read needs, is its
type's, in `desk.proof.mark`; the table is keyed by instruction, which each
type names, and its callables take the typed mark.

`sets` returns None where the mark sets nothing (`decision-log.md Process:
#174`), "" for a delete, else the text. `reads` returns the problems the row
finds; `flows.fill` runs it before a mark is placed and the evaluator before
it is folded, so a mark reaching the evaluator has been read. `notes` returns
what the chief should be told about a mark that is not a problem with it --
read once, by the evaluator, and reported without changing a state
(`Process: #177`).

An `add` going back to every role that read its page (`Process: #116`) was a
row of its own here, `rereads`, until `#180`: a text settles only once every
role that read the place has accepted it, which carries an add to those roles
for the same reason it carries any other lone proposal. The evaluator asks
that of every row, so no row answers it.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any

from comment_review.desk.marks.rules import comment_at, first_word_dropped
from comment_review.desk.proof.mark import (
    CorrectMark,
    Instruction,
    Mark,
    QueryMark,
    Shape,
    Touch,
)


class Stance(StrEnum):
    """How a mark stands toward the other marks at its place.

    `ABSTAINS` and `DEFERS` are not one stance. A `clean` holds a view -- it
    read the paragraph and found nothing to report -- so a text nobody has
    shown it still owes it a say. A deferring `query` holds none: it hands the
    place to another role for the rest of the review
    (`decision-log.md Process: #121`), and nothing waits on it
    (`desk.evaluate.passes.owed_a_say`, `Process: #180`).
    """

    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name.lower()

    PROPOSES = auto()
    ABSTAINS = auto()
    DEFERS = auto()
    UNSETTLABLE = auto()


Sets = Callable[[Any, Touch, str], str | None]
Reads = Callable[[Any, Touch, str], list[str]]
Notes = Callable[[Any, Touch, str], list[str]]
Pairs = Callable[[Any], Stance]


def _nothing(mark, touch, base):
    return None


def _no_problems(mark, touch, base):
    return []


def _no_notes(mark, touch, base):
    return []


def _the_change(mark, touch, base):
    return mark.change


def _the_raw_text(mark, touch, base):
    return mark.raw_text


def _without_once(address: str, base: str, snippet: str, anchor: str) -> str | None:
    form = comment_at(address, base, anchor=anchor)
    unwrapped = comment_at(address, snippet).text
    return form.without_once(unwrapped)


def _move_sets(mark, touch, base):
    if touch is Touch.ORIGIN:
        return _without_once(mark.address, base, mark.change, mark.anchor)
    return mark.raw_text


def _move_reads(mark, touch, base):
    if touch is Touch.ORIGIN:
        if _without_once(mark.address, base, mark.change, mark.anchor) is None:
            return [f"the snippet is not in the origin's paragraph: {mark.change!r}"]
        return []
    dropped = first_word_dropped(base, mark.raw_text)
    if dropped is not None:
        return [f"the destination text does not keep {dropped!r}"]
    dropped = first_word_dropped(mark.change, mark.raw_text)
    if dropped is not None:
        return [f"the destination text does not keep {dropped!r}"]
    return []


def _correct_notes(mark: CorrectMark, touch, base):
    """The words a `correct` drops from its base that its claim never named.

    The claim's `false` clause is the part of the paragraph the mark says it
    is replacing, so the rest of the base is what it said nothing about and
    what the change is expected to keep. A word missing from there is the
    only one worth telling anyone about, and it is advisory: the chief reads
    it and the place settles either way (`decision-log.md Process: #163` and
    `#177`).
    """
    rest = base.replace(mark.false, "", 1)
    word = first_word_dropped(rest, mark.change)
    if word is None:
        return []
    return [f"its change drops {word!r}, which its claim never names"]


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


def _query_stance(mark: QueryMark):
    if mark.shape is Shape.HUMAN_REVIEW_NECESSARY:
        return Stance.UNSETTLABLE
    return Stance.DEFERS


@dataclass(frozen=True)
class Row:
    """One instruction, as every reader of a mark at a place sees it."""

    touches: tuple[Touch, ...] = (Touch.OWN,)
    sets: Sets = _nothing
    reads: Reads = _no_problems
    #: What a mark of this row should be told about itself without being
    #: refused for it. A note reaches the chief as an `Advised` event and
    #: changes no place's state -- `decision-log.md Process: #177`.
    notes: Notes = _no_notes
    pairs: Pairs = _proposes
    #: True where `raw_text` is the paragraph as it will read and the role
    #: writes it, rather than the seeded paragraph as it stands --
    #: `decision-log.md Process: #175` and `#176`. `flows.fill` takes it from
    #: the entry for these rows and from the page for every other.
    carries_raw_text: bool = False

    def places(self, mark: Mark) -> tuple[tuple[str, Touch], ...]:
        """Every place a mark of this row writes at, with which touch each is.

        This is the one answer to where a mark writes; every flow that walks a
        mark's places asks it. `touches` names the places, in order. A
        destination is the address the mark sends its paragraph to
        (`Mark.destination`), and every other touch is the mark's own address.
        A place with no address is left out, so a mark that may carry none
        writes nowhere.
        """
        out = []
        for touch in self.touches:
            where = mark.destination if touch is Touch.DESTINATION else mark.address
            if where:
                out.append((where, touch))
        return tuple(out)


INSTRUCTIONS: dict[Instruction, Row] = {
    Instruction.CLEAN: Row(pairs=_abstains),
    Instruction.QUERY: Row(pairs=_query_stance),
    Instruction.DROP: Row(sets=_the_change),
    Instruction.CORRECT: Row(sets=_the_change, notes=_correct_notes),
    Instruction.PATCH: Row(sets=_the_change),
    Instruction.ADD: Row(sets=_the_raw_text, reads=_add_reads, carries_raw_text=True),
    Instruction.MOVE: Row(
        touches=(Touch.ORIGIN, Touch.DESTINATION),
        sets=_move_sets,
        reads=_move_reads,
        carries_raw_text=True,
    ),
}
