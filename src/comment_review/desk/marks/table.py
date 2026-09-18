"""The marks table: one row per instruction, and every reader asks the row.

A row says what a mark's claim carries, which places the mark touches, what
text it sets at each, what problems it has against its base, how it pairs
with other marks at a place, and which answers a turn may give on it. Nothing
outside this module names an instruction; a gate holds that.

`sets` returns None where the mark sets nothing (`decision-log.md Process:
#174`), "" for a delete, else the text. `reads` returns the problems the row
finds; `flows.fill` runs it before a mark is placed and the evaluator before
it is folded, so a mark reaching the evaluator has been read. `notes` returns
what the chief should be told about a mark that is not a problem with it --
read once, by the evaluator, and reported without changing a state
(`Process: #177`).

`rereads` is True on `add` alone: an add is carried forward for every role
that read its page, per `decision-log.md Process: #116` and `#121`.
"""

from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import TYPE_CHECKING, Any

from comment_review.desk.dispositions.disposition import CHIEF
from comment_review.desk.marks.mark import Instruction, Mark, Shape, first_word_dropped

if TYPE_CHECKING:
    # Type-only: `place` imports `INSTRUCTIONS`, `Stance` and `Touch` from this
    # module, so a runtime import here would cycle back to it.
    from comment_review.desk.evaluate.place import Place


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


def _correct_notes(mark, touch, base):
    """The words a `correct` drops from its base that its claim never named.

    The claim's `false` clause is the part of the paragraph the mark says it
    is replacing, so the rest of the base is what it said nothing about and
    what the change is expected to keep. A word missing from there is the
    only one worth telling anyone about, and it is advisory: the chief reads
    it and the place settles either way (`decision-log.md Process: #163` and
    `#177`).
    """
    rest = base.replace(str(mark.claim.get("false", "")), "", 1)
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
    #: What a mark of this row should be told about itself without being
    #: refused for it. A note reaches the chief as an `Advised` event and
    #: changes no place's state -- `decision-log.md Process: #177`.
    notes: Notes = _no_notes
    pairs: Pairs = _proposes
    answers: tuple[str, ...] = ESCALATION_ANSWERS
    owes_change: bool = True
    owes_sources: bool = True
    substantive: bool = True
    may_empty: bool = False
    needs_anchor: bool = False
    #: Set True on `add` alone -- Ruling R4, `decision-log.md Process: #116`
    #: and `#121`: an add is carried forward for every role that read its
    #: page, not only the role that filed it.
    rereads: bool = False
    #: True where `raw_text` is the paragraph as it will read and the role
    #: writes it, rather than the seeded paragraph as it stands --
    #: `decision-log.md Process: #175` and `#176`. `flows.fill` takes it from
    #: the entry for these rows and from the page for every other, and
    #: `desk.collator.drift_in` asks nothing of it here, since it is not the
    #: base the place was seeded with.
    carries_raw_text: bool = False
    #: Derived from `touches` in `__post_init__`, below -- never set by a row
    #: literal. The default here is only what a `Row()` with no `touches`
    #: argument gets before the derivation runs.
    owes_destination: bool = False

    def __post_init__(self) -> None:
        """Derive `owes_destination` from `touches`, overwriting any literal.

        The dataclass is frozen, so this is the one place allowed to set a
        field after construction. `owes_destination` is a fact about
        `touches`, not a second fact a row author could state differently --
        deriving it here is what keeps the two from drifting apart, the way
        a stored copy next to its source could.
        """
        object.__setattr__(self, "owes_destination", Touch.DESTINATION in self.touches)


INSTRUCTIONS: dict[Instruction, Row] = {
    Instruction.CLEAN: Row(
        pairs=_abstains,
        answers=(),
        owes_change=False,
        owes_sources=False,
        substantive=False,
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
        claim_all=("false", "true"),
        quotes_original="false",
        sets=_the_change,
        notes=_correct_notes,
    ),
    Instruction.PATCH: Row(
        claim_all=("from", "to"),
        quotes_original="from",
        sets=_the_change,
        owes_sources=False,
    ),
    Instruction.ADD: Row(
        claim_all=("missing", "anchor"),
        sets=_the_raw_text,
        reads=_add_reads,
        needs_anchor=True,
        rereads=True,
        carries_raw_text=True,
    ),
    Instruction.MOVE: Row(
        claim_all=("from", "to"),
        touches=(Touch.ORIGIN, Touch.DESTINATION),
        sets=_move_sets,
        reads=_move_reads,
        carries_raw_text=True,
    ),
}


def chief_mark(place: "Place") -> Mark:
    """The chief's mark at one decided place -- the side taken in, or synthesized.

    Returns the filed mark whose row sets `place.text` at this place, where
    one of the filed marks does -- the side the fold took in, returned
    unchanged. Otherwise synthesizes one: a drop where the decided text is
    empty, a correct where the base held a paragraph, an add where it did
    not.

    Args:
        place: a decided place -- `place.text` is not None.

    Returns:
        The taken-in `Mark`, or a synthesized one whose `reason` names the
        copy chief.

    Raises:
        ValueError: `place.text` is None -- the caller's contract is a place
            the fold already decided a text for; `chief_copy_of` filters
            those out before calling this.
    """
    for filed in place.filed:
        row = INSTRUCTIONS[filed.mark.instruction]
        if row.sets(filed.mark, filed.touch, place.base) == place.text:
            return filed.mark

    text = place.text
    if text is None:
        raise ValueError(
            "chief_mark needs a place the fold decided a text for, "
            f"got None at {place.address!r}"
        )
    reason = f"{CHIEF}: decided at this place"
    # The evidence the filed marks brought, carried onto the synthesized one:
    # every row that owes a change owes sources too, so a mark handed back
    # without them is one the parse refuses -- and the chief read those marks
    # to decide the text, so they are what stands behind it. Deduped in
    # place, since a source is a dict and cannot go through a set.
    cited = [source for one in place.filed for source in one.mark.sources]
    sources = tuple(s for i, s in enumerate(cited) if s not in cited[:i])
    if text == "":
        return Mark(
            address=place.address,
            anchor=place.anchor,
            raw_text=place.base,
            instruction=Instruction.DROP,
            claim={"drop": place.base},
            reason=reason,
            sources=sources,
            change="",
        )
    if place.base:
        return Mark(
            address=place.address,
            anchor=place.anchor,
            raw_text=place.base,
            instruction=Instruction.CORRECT,
            claim={"false": place.base, "true": text},
            reason=reason,
            sources=sources,
            change=text,
        )
    return Mark(
        address=place.address,
        anchor=place.anchor,
        # An `add`'s `raw_text` is the paragraph as it will read, which its
        # own row sets at the place (`decision-log.md Process: #176`). The
        # base here is empty, so that is the decided text itself; writing ""
        # would make the row set nothing where the fold decided something.
        raw_text=text,
        instruction=Instruction.ADD,
        # The anchor NAMED in backticks, which is what the parse requires --
        # and a place's anchor is a line of code, indented where the code is.
        # Backticked as it stands, a mark at any indented place is one the
        # parse refuses, and the chief's own decision is then carried on a
        # mark nothing downstream can read.
        claim={"missing": text.splitlines()[0], "anchor": f"`{place.anchor.strip()}`"},
        reason=reason,
        sources=sources,
        change=text,
    )
