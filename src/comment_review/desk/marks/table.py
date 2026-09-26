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

An `add` going back to every role that read its page (`Process: #116`) was a
row of its own here, `rereads`, until `#180`: a text settles only once every
role that read the place has accepted it, which carries an add to those roles
for the same reason it carries any other lone proposal. The evaluator asks
that of every row, so no row answers it.
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
    return Stance.DEFERS


ESCALATION_ANSWERS = ("hold", "withdraw", "correct", "patch")


@dataclass(frozen=True)
class Row:
    """One instruction, as every reader sees it."""

    claim_all: tuple[str, ...] = ()
    quotes_original: str = ""
    #: The claim key that names the address a destination touch writes at,
    #: "" for a row with no destination. `places` reads the destination under
    #: it, and the parse checks the same key (`desk.marks.mark.
    #: _destination_problems`).
    names_destination: str = ""
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
    #: True where `raw_text` is the paragraph as it will read and the role
    #: writes it, rather than the seeded paragraph as it stands --
    #: `decision-log.md Process: #175` and `#176`. `flows.fill` takes it from
    #: the entry for these rows and from the page for every other.
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

    def places(self, mark: Mark) -> tuple[tuple[str, Touch], ...]:
        """Every place a mark of this row writes at, with which touch each is.

        This is the one answer to where a mark writes; every flow that walks a
        mark's places asks it. `touches` names the places, in order. A
        destination is the address the claim names under `names_destination`,
        and every other touch is the mark's own address. A place with no
        address is left out, so a mark that may carry none writes nowhere.
        """
        out = []
        for touch in self.touches:
            if touch is Touch.DESTINATION:
                where = str(mark.claim.get(self.names_destination, ""))
            else:
                where = mark.address
            if where:
                out.append((where, touch))
        return tuple(out)


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
        carries_raw_text=True,
    ),
    Instruction.MOVE: Row(
        claim_all=("from", "to"),
        names_destination="to",
        touches=(Touch.ORIGIN, Touch.DESTINATION),
        sets=_move_sets,
        reads=_move_reads,
        carries_raw_text=True,
    ),
}


def _in_role_order(place: "Place") -> list:
    """This place's filed marks, by role, then as that role filed them.

    !! THE ORDER IS A PROPERTY OF THE DATA, NOT OF THE DISPATCH.
    `flows.places.places_of` appends in the order the copies were handed over,
    which is the order a command's `--edit-copy` flags happened to be typed in.
    Reading `place.filed` as it stands makes both of `chief_mark`'s answers
    turn on that: which of two marks setting the same text is returned, and
    the order of the sources carried onto a synthesized mark.

    ! IT REPLACES A CHECK THE OLD FOLD HAD. `tests/test_collate.py::
    TestTheChiefsCopy::test_sources_and_reason_AGREE_on_the_roles_ORDER`
    asserted the same thing of the composed mark that flow built, against
    "the order `edit_copies` happened to be handed in, which is not a
    property of the data".

    Args:
        place: the place whose marks are being read.

    Returns:
        The `Filed` entries, sorted by role. `sorted` is stable, so each
        role's own marks keep the order it filed them in.
    """
    return sorted(place.filed, key=lambda one: one.role)


def _sets_both_ends(filed, place: "Place", partner: "Place | None") -> bool:
    """Whether this mark sets the decided text at BOTH the places it touches.

    !! A MARK TAKEN IN AT ONE PLACE IS PLACED AT EVERY PLACE IT TOUCHES, so
    taking in a `move` at its origin writes its destination too. That is right
    only while the destination closed on what the move sets there. The chief
    rules the two ends with two dispositions and may recast one of them, and
    then the move is not what happened: the origin must be written as its own
    remainder instead, or the chief's copy carries a move to a place that is
    about to hold different prose. MEASURED 2026-09-18, before this: a
    `taken_in` at the origin beside a `recast` at the destination put a `move`
    and a `correct` on the chief's copy, both landing at the destination, and
    `flows.transcribe.docket_of` refused the copy -- *"its marks here edit the
    same sentence and do not compose"* -- so the chief's own ruling reached no
    docket.

    Args:
        filed: one `Filed` entry at `place`.
        place: the place being written.
        partner: the other end, where this place is one end of a move.

    Returns:
        True for a mark that writes at this place alone. For a mark that also
        writes elsewhere, whether the partner is decided and its text is what
        this mark sets there.
    """
    row = INSTRUCTIONS[filed.mark.instruction]
    if all(where == place.address for where, _touch in row.places(filed.mark)):
        return True
    if partner is None or partner.text is None:
        return False
    # Compared by value, not by identity: a place read back off a proof
    # deserializes its own marks, so the one mark filed at both ends of a move
    # is two equal objects once the stage has crossed the wire.
    return any(
        INSTRUCTIONS[one.mark.instruction].sets(one.mark, one.touch, partner.base)
        == partner.text
        for one in partner.filed
        if one.mark == filed.mark
    )


def chief_mark(place: "Place", partner: "Place | None" = None) -> Mark:
    """The chief's mark at one decided place -- the side taken in, or synthesized.

    Returns the filed mark whose row sets `place.text` at this place, where
    one of the filed marks does -- the side the fold took in, returned
    unchanged. Otherwise synthesizes one: a drop where the decided text is
    empty, a correct where the base held a paragraph, an add where it did
    not.

    The marks are read in role order, so which mark is returned and which
    order its sources stand in are the same on every run -- see
    `_in_role_order`. A mark that touches two places is taken in only where
    both of them closed on what it sets -- see `_sets_both_ends`.

    Args:
        place: a decided place -- `place.text` is not None.
        partner: the other end, where this place is one end of a move. Without
            it a two-place mark is never taken in, so a caller that has the
            other end hands it over.

    Returns:
        The taken-in `Mark`, or a synthesized one whose `reason` names the
        copy chief.

    Raises:
        ValueError: `place.text` is None -- the caller's contract is a place
            the fold already decided a text for; `chief_copy_of` filters
            those out before calling this.
    """
    filed_marks = _in_role_order(place)
    for filed in filed_marks:
        row = INSTRUCTIONS[filed.mark.instruction]
        if row.sets(filed.mark, filed.touch, place.base) != place.text:
            continue
        if _sets_both_ends(filed, place, partner):
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
    cited = [source for one in filed_marks for source in one.mark.sources]
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
