"""What a role writes, and the rules a mark can be judged by ON ITS OWN.

    Instruction      the seven, closed -- a StrEnum, value DERIVED from name
    Row              one row -- all this system knows about one instruction
    INSTRUCTIONS     Instruction -> Row, the seven, closed
    Shape            the three a `query` must name, closed -- a StrEnum
    QUERY_SHAPES     tuple(Shape), in the order `docs/the-mark.md` states them
    Mark             one role's ruling on one place -- the seven fields
                     `docs/the-mark.md` names, and no others
    allowed()        the shape a role is handed, generated from the rows
    parse()          THE BOUNDARY: a role's entry -> a `Mark`, or named
                     problems. There is no third outcome
    untouched()      a seeded slot no role has written in -- the coverage gap,
                     which is NOT a mark that failed to name an instruction

!! A MARK IS THE OBJECT; ITS `instruction` IS ONE OF SEVEN. The word this table
used to carry read as judicial and named the same thing twice, the object a
*finding* and its type the struck word -- `decision-log.md Vocabulary: #17`.
! `instruction` is the trade's: a proof correction has a TEXTUAL mark saying
where and a MARGINAL mark saying what to do, and the second is the instruction --
which is what a compositor executes, and this system has one.

!! `INSTRUCTION` NAMES THE ENUM; THE DATACLASS IS `Row`, NOT `Instruction`.
`decision-log.md Vocabulary: #17` landed the dataclass as `Instruction` before
the seven closed names had an enum of their own -- `T1.15` of
`docs/plans/0.2.4-the-mark-and-the-collator.md` gives the word to the enum, so
the dataclass took `Row`: `docs/the-mark.md` already calls its own subject
"four classifier columns" and "seven row flags", so `Row` is the spec's own
word for what one entry of that table holds. `decision-log.md Process: #46`.

!! EVERY CLOSED SET IN THIS FILE IS A `StrEnum`, following `reading.series.Kind`
-- `T1.15`. Each member's value is DERIVED from its name via
`_generate_next_value_`, never hand-typed, and no site asks membership of an
enum class directly (`x in SomeEnum` raises `TypeError` on Python 3.11,
measured at `lexer.py:87`) -- `INSTRUCTIONS`' own keys serve as the membership
check for `Instruction`, and `QUERY_SHAPES` is `Shape`'s companion tuple.

!! THE RULES SPLIT ON WHAT THEY NEED, AND THIS FILE IS THE HALF THAT NEEDS
NOTHING. Whether `claim.false` is a key is answerable from the mark; whether it
appears VERBATIM in the paragraph is answerable only against the page the role
read. **The first is here; the second is SOURCE-VERIFICATION**, which is not
built.
! Written this way so the shape can be checked the moment a role hands it back,
before anything has been loaded.

!! ADDING OR CHANGING AN INSTRUCTION IS A ROW, NOT NEW CODE. Measured
2026-08-17: the contract changed twice while this knowledge lived in eight
functions, each with its own branch on the field. Finding all eight is what
nobody did, and five defects shipped in one morning. A contract change should
touch one row.

!! `Row` CARRIES ONLY WHAT `docs/the-mark.md` APPROVES -- ELEVEN
FIELDS, NO PROSE. A 22-field scheme entered this file on 2026-08-27 during a
port that was never proposed and never approved -- `decision-log.md Process:
#37`. `docs/the-mark.md` is the spec; this file implements it and defines
nothing. `tests/gates/test_mark_shape.py` reads the spec's own tables and
refuses a field that is not one of them -- for `Mark`'s seven as well as for
`Row`'s eleven.

!! AND `Mark` REPLACED `problems(where, mark: dict)` ON 2026-08-29. Nothing
parsed a mark, so the seven fields existed as prose plus string literals at
the call sites, and three things were MEASURED off that: ten
`str`-into-`dict[Instruction, Row]` type errors in `desk/collator.py`; a
`flows/marks.py` skip that dropped a mark carrying no instruction and recounted
it as a place nobody looked at; and `reviewer-brief.md`'s own worked example
passing `mark --check` at exit 0 AS UNRULED, because the brief keys the ruling
`instruction` and the code read `mark`. **A reviewer following the brief
produced findings that vanished in silence.**

! THE RULING FIELD IS `instruction`, AND THE CODE IS WHAT MOVED. Roy,
2026-08-29: *"the agent emits the 'mark', the 'instruction' was ... the action
that turned the mark into an actionable thing."* The enum was already
`Instruction` and the brief already said `instruction`; a `Mark.mark` is the
self-nesting that made this ambiguous.
"""

import re
from dataclasses import dataclass
from enum import StrEnum, auto


class Instruction(StrEnum):
    """The seven, closed. `docs/the-mark.md` is the spec; this only names them.

    ! Value derived from the member name via `_generate_next_value_`, so
    `Instruction.CLEAN == "clean"` holds without a hand-typed string.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower()

    CLEAN = auto()
    QUERY = auto()
    DROP = auto()
    CORRECT = auto()
    PATCH = auto()
    ADD = auto()
    MOVE = auto()


class Shape(StrEnum):
    """The three shapes a `query`'s claim must name, KEYED ON WHO RESOLVES IT.

    `decision-log.md Process: #33`, Roy 2026-08-27. The set they replaced --
    `outside the checkout`, `outside the code` -- was keyed on WHERE the missing
    evidence lived, and rested on a reviewer in a FRESH CHECKOUT reaching the
    same evidence later. Roy: *"this really is not expected to be a repeatable
    event."*

    ! A cause belongs in `reason`, which a human reads. A SHAPE is read by the
    flow, and the flow can do nothing with a cause.

    ! Value derived from the member name -- `OUTSIDE_MY_ROLE` gives
    `"outside-my-role"` -- so the Python identifier and the wire value stay
    related without either being hand-typed against the other.
    """

    @staticmethod
    def _generate_next_value_(
        name: str, start: int, count: int, last_values: list[str]
    ) -> str:
        return name.lower().replace("_", "-")

    OUTSIDE_MY_ROLE = auto()
    #: ! The one a collate step can ACT on: another role may have settled this place.
    UNABLE_TO_DETERMINE = auto()
    HUMAN_REVIEW_NECESSARY = auto()


#: `Shape`'s companion tuple, in the spec's own order -- membership is asked of
#: this, never of the `Shape` class itself.
QUERY_SHAPES = tuple(Shape)

# ! The words are open and the CATEGORIES are not -- `TODO/the-fields-do-not-say
# -a-mark-may-cite-across.md` T6 rules the register. A rename is a row here.

#: What an `add`'s claim must carry: the anchor, NAMED. Backticks are the repo's
#: citation form, so "named" is checkable without guessing which token is an
#: identifier.
ANCHOR_NAME = re.compile(r"`[^`\s][^`]*`")
#: !! PUBLISHED WITH THE PATTERN ABOVE, so the two are one string rather than two
#: that agree today. `allowed()` used to hand-write an example beside a pattern
#: nothing held it equal to.
ANCHOR_EXAMPLE = "`compute_rates`"


@dataclass(frozen=True)
class Row:
    """Everything this system knows about one instruction, in one place.

    Four classifier columns, then seven row flags -- `docs/the-mark.md`'s
    "The classifiers" section states each; this docstring restates only which
    field carries which, not what it means.

    Attributes:
        claim_all: the CLAIM KEYS classifier -- every key `claim` must carry.
        quotes_original: the VERBATIM classifier -- the `claim` key whose value
            the EXISTING sentence follows, or "" when it quotes none. `move`'s
            from/to are PLACES and `add` is about prose that is missing, so
            both quote none.
        owes_change: the CHANGE classifier -- whether a change is owed. `clean`
            rules on nothing and `query` proposes no text.
        owes_sources: the SOURCES classifier -- whether sources are owed.
            `clean` cites no claim so it cites no place. `patch` rules on
            WORDING alone -- nothing outside the paragraph settles whether a
            sentence reads better -- so a source would be evidence for a claim
            nobody made.
        substantive: NOT SUBSTANTIVE, inverted -- this ASKS something of the
            apply step. Only `clean` does not, which is what makes it the null
            mark rather than a pass, and the row every other default (`reason`,
            `address`) is owed unless this is False.
        can_declare_scope: MAY DECLARE SCOPE -- this may be a BOUNDARY REPORT
            rather than work -- `query`, and only in its `outside-my-role`
            shape.
        may_empty: EMPTY CHANGE ALLOWED -- this may leave the paragraph with
            NOTHING in it, so an empty `change` is the edit rather than a
            missing one. Only `drop`.
        rules_on_text: RULES ON TEXT -- keeps the sentence and changes it.
            ! Against `drop` on ONE sentence is the only contradiction the set
            can express. `move` is deliberately neither: relocation and a
            truth fix COMPOSE.
        diffable: NOT DIFFABLE, inverted -- the original against `change` names
            the edited sentence. False where there is nothing to diff.
        needs_anchor: ANCHOR NAMED IN BACKTICKS -- a FORM check on
            `claim.anchor`, not a side; the address says that.
        owes_destination: DESTINATION ADDRESSABLE -- `claim.to` names a place
            that must be ADDRESSABLE. ! Not carried by the binder -- Roy,
            2026-08-27: *"the destination needs to be addressable not
            necessarily in the binder. That includes an external_address-able
            item."*
    """

    claim_all: tuple[str, ...] = ()
    quotes_original: str = ""
    owes_change: bool = True
    owes_sources: bool = True
    substantive: bool = True
    can_declare_scope: bool = False
    may_empty: bool = False
    rules_on_text: bool = False
    diffable: bool = True
    needs_anchor: bool = False
    owes_destination: bool = False


INSTRUCTIONS: dict[Instruction, Row] = {
    Instruction.CLEAN: Row(
        owes_change=False,
        owes_sources=False,
        substantive=False,
    ),
    Instruction.QUERY: Row(
        claim_all=("shape", "attempted", "settles"),
        owes_change=False,
        can_declare_scope=True,
    ),
    Instruction.DROP: Row(
        claim_all=("drop",),
        quotes_original="drop",
        may_empty=True,
    ),
    Instruction.CORRECT: Row(
        claim_all=("false", "true"),
        quotes_original="false",
        rules_on_text=True,
    ),
    Instruction.PATCH: Row(
        claim_all=("from", "to"),
        quotes_original="from",
        # !! `patch` NEEDS NO SOURCE: the claim is already true, and only its
        # wording is at issue. Measured 2026-08-22, re-confirmed twice: this
        # flag and the brief's own sentence shipped out of agreement once, and
        # the gate fatally refused every `patch` a compliant reviewer filed.
        owes_sources=False,
        rules_on_text=True,
    ),
    Instruction.ADD: Row(
        claim_all=("missing", "anchor"),
        diffable=False,
        needs_anchor=True,
    ),
    Instruction.MOVE: Row(
        claim_all=("from", "to"),
        owes_destination=True,
    ),
}


@dataclass(frozen=True)
class Mark:
    """One role's ruling on one place -- `docs/the-mark.md`'s eight fields.

    !! THE FIELD ORDER IS THE CHAIN OF CUSTODY, not alphabetical and not
    convenience -- the ruling, then the claim, the reason, the sources and the
    change it produces, with the two seeded fields that say WHERE in front of
    them. `docs/the-mark.md`, "The fields -- eight", holds Roy's own sentence
    for it, in the register that ruling was given in.

    ! `role` IS NOT A FIELD, and `collator.Placed` is what carries the pair. It
    belongs to the `edit_copy` a mark came back in, not to the mark.

    !! `raw_text` IS THE THIRD SEEDED FIELD AND WAS EXCLUDED UNTIL 2026-08-30.
    It went out on every slot and `parse` dropped it, so one of the three
    seeded fields could not be written from this class's own names -- which is
    what left a dict literal in `flows/marks.py` that a rename could not reach.
    ! WHAT COMES BACK IS NOT THE BASE. The binder's row is; a returned
    `raw_text` that differs from it is DRIFT, which `desk.collator.drift_in`
    reports.

    Attributes:
        address: `path@cue`. WHICH PLACE -- seeded, copied from the row, never
            built. Empty only for `clean`, the one row `substantive` is False
            for.
        anchor: the line of code the place sits on -- seeded, and empty where
            the census resolved none.
        raw_text: the paragraph as it stands -- seeded, and what a role's
            `change` is a rewrite of. ! CARRIED, NEVER TRUSTED AS THE BASE:
            every check that measures a claim against the paragraph reads the
            BINDER's text, through `collator.base_texts`.
        instruction: one of the seven, as an `Instruction` member, so
            `INSTRUCTIONS[mark.instruction]` resolves with no cast.
        claim: the surgical spec -- structured keys, per instruction. Which
            keys is `INSTRUCTIONS[...].claim_all`; `parse` has already checked
            that every one of them is there and filled.
        reason: WHY, in prose. No checker settles it.
        sources: `{cite, verbatim}` pairs, each optionally carrying `ran`.
            Empty for the two rows that owe none. ! TYPED `object` AND NOT
            `dict` ON PURPOSE: an entry that is not a pair is CARRIED, not
            dropped, so `collator.source_problems` can refuse it by name. A
            retired reader filtered `sources` to dicts before its own check
            ran, and a bare string vanished instead of being flagged.
        change: the RESULT -- the updated paragraph, as RAW TEXT. Roy,
            2026-08-28: *"`change` needs to be the updated paragraph as raw
            text not lines or sentences. This will make it easier to diff per
            the rest of the stages."* Empty where the row owes no change, and
            on a `drop` whose claim names the whole paragraph, where an empty
            change IS the edit.
    """

    address: str
    anchor: str
    raw_text: str
    instruction: Instruction
    claim: dict
    reason: str
    sources: tuple[object, ...]
    change: str


#: The four fields a ROLE fills that `untouched` looks at. `address` and
#: `anchor` are seeded onto every slot, so neither says whether anyone wrote
#: here; `instruction` is the field being ruled on and is read separately.
ROLE_FIELDS = ("claim", "reason", "sources", "change")


def filled(value: object) -> bool:
    """A string with something in it. ! An empty string is NOT an answer.

    Measured: a claim key present and empty passed every check that would have
    caught it missing, and each of those checks then skipped.
    """
    return isinstance(value, str) and bool(value.strip())


def allowed() -> dict:
    """The shape a role is handed -- generated from the rows, never hand-written.

    Returns:
        `instruction` -> the seven; `claim` -> the keys each instruction's claim must
        carry; `values` -> the fields whose value is itself a closed set;
        `scope_shape` -> the one shape that is a boundary report rather than
        work; `anchor_form` -> the form an `add`'s anchor takes;
        `edit_copy_header` -> the keys an `edit_copy` carries beside its sheets.

    !! IT WAS `sheet_header`, AND BOTH THE NAME AND ITS TWO DESCRIPTIONS WERE
    FALSE. `role` and `read_from` sit on the EDIT_COPY -- `seed` returns
    `{"role", "read_from", "sheets"}` and a sheet carries `{"path", "sha",
    "marks"}` -- so a role reading `mark --shape` was told to put two keys on
    the container that does not hold them. `sheet` names the PAGE-UNIT since
    `decision-log.md Vocabulary: #28`; the per-role container is `edit_copy`.

    !! THE HEADER LANDED 2026-08-28, AND UNTIL THEN `read_from` WAS PUBLISHED
    NOWHERE. `seed` began putting it on every edit_copy and `problems_in`
    began refusing one without it, while a grep for the name across
    `SKILL.md`, `references/` and `agents/` returned nothing -- so the field a
    role is required to carry was one no role was told about.

    ! `decision-log.md Process: #34` is what makes that a defect rather than an
    omission: the field exists so a later role can know it holds a REVISE and
    not the original. A role that is never told it exists cannot use it for
    that, which is the whole benefit the staged flow was designed to buy.

    ! WHAT A ROLE DOES WITH IT IS THE `agents` LANE. This states the key and its
    shape, which `docs/conventions.md` puts on this side; the instruction to
    READ it before ruling belongs in the reviewer brief and is not written here.
    """
    claims = {name: list(spec.claim_all) for name, spec in INSTRUCTIONS.items()}
    return {
        "instruction": sorted(INSTRUCTIONS),
        "claim": claims,
        "values": {"shape": list(QUERY_SHAPES)},
        "scope_shape": Shape.OUTSIDE_MY_ROLE,
        # ! A FORM, not a value set, and it is stated for the same reason the sets
        # are: a template that constrains a field without saying what is allowed
        # has only moved the guessing.
        "anchor_form": f"the anchor NAMED in backticks, e.g. {ANCHOR_EXAMPLE}",
        "source_keys": {"required": ["cite", "verbatim"], "optional": ["ran"]},
        "edit_copy_header": {
            "role": "the role this edit_copy was seeded for",
            "read_from": (
                "the tree this edit_copy was censused from -- "
                '`{"root": "<path>", "revise": <number>}`, '
                "where revise 0 is the original"
            ),
        },
    }


def _claim_problems(where: str, instruction: Instruction, claim: object) -> list[str]:
    """Whether `claim` carries the keys this instruction's row demands.

    ! READS `spec.claim_all` DIRECTLY. With every key an instruction owes
    stated once in that one list, there is nothing left to derive it from.

    Args:
        where: how to name this mark in a message -- an address, or a position.
        instruction: already resolved to a member by `parse()`, its only
            caller.
        claim: the entry's `claim`, unvalidated.
    """
    spec = INSTRUCTIONS[instruction]
    if not spec.claim_all:
        return []
    if not isinstance(claim, dict):
        return [
            f"{where}: {instruction} needs a `claim` object carrying "
            f"{', '.join(spec.claim_all)}"
        ]

    out = []
    missing = [k for k in spec.claim_all if not filled(claim.get(k))]
    if missing:
        out.append(f"{where}: {instruction} needs `claim` to carry "
                    f"{', '.join(spec.claim_all)} (missing {', '.join(missing)})")
    # ! `shape` is a VALUE in a closed set, not merely a key. Checking it
    # structurally is what lets `collator` route on it without reading prose.
    if "shape" in spec.claim_all and claim.get("shape") not in QUERY_SHAPES:
        out.append(
            f"{where}: {instruction} needs `claim.shape` to be one of "
            + ", ".join(QUERY_SHAPES)
        )
    if spec.needs_anchor and not ANCHOR_NAME.search(str(claim.get("anchor", ""))):
        out.append(
            f"{where}: {instruction} needs the anchor NAMED in backticks, e.g. "
            f"{ANCHOR_EXAMPLE}"
        )
    return out


def _source_problems(where: str, sources: object) -> list[str]:
    """Each source is a `{cite, verbatim}` pair, and may carry `ran`.

    !! PAIRS, NOT STRINGS. Measured 2026-08-27: roles returned `path:line | text`,
    which reads for a human and cannot be checked -- nothing can confirm the
    verbatim string sits near the cited line.

    ! `ran` is the command that SETTLED the claim, for a claim settled by running
    something. Measured: a role's first pass ran on ambient Python 3.14 instead
    of the pinned floor and produced a false negative. `sources` otherwise records
    WHAT was seen and never HOW, so an instruction from a bad run is indistinguishable
    from a good one.
    """
    if not isinstance(sources, list) or not sources:
        return [f"{where}: needs at least one source"]
    out = []
    for i, source in enumerate(sources):
        at = f"{where}: source {i + 1}"
        if not isinstance(source, dict):
            out.append(f"{at} must be an object with `cite` and `verbatim`")
            continue
        for key in ("cite", "verbatim"):
            if not filled(source.get(key)):
                out.append(f"{at} needs `{key}`")
    return out


def _change_problems(
    where: str, instruction: Instruction, spec: Row, change: object
) -> list[str]:
    """Whether `change` is the updated paragraph, as RAW TEXT.

    !! RAW TEXT, NOT A LINE ARRAY. `docs/the-mark.md`, Roy 2026-08-28: *"`change`
    needs to be the updated paragraph as raw text not lines or sentences. This
    will make it easier to diff per the rest of the stages."* The seeded row
    carries `raw_text` and the role returns `change`; every stage downstream is
    a diff of one against the other, and a line array has to be joined before
    any of them can run.

    ! THE ARRAY FORM IS REFUSED BY NAME rather than accepted for a release.
    It was what this gate demanded until 2026-08-29 while the brief mandated
    raw text -- the disagreement `TODO/change-is-raw-text-not-lines.md` was
    filed on -- so a list arriving here is a role written against the retired
    rule, and saying so is the only message that helps.

    ! AN EMPTY STRING IS THE EDIT on `drop`, the one row `may_empty` is True
    for, where the claim names the whole paragraph.
    """
    if not isinstance(change, str):
        return [
            f"{where}: {instruction} needs `change` as the updated paragraph in "
            f"RAW TEXT, not a {type(change).__name__}"
        ]
    if not change and not spec.may_empty:
        return [f"{where}: {instruction} needs `change` to hold the new text"]
    return []


def untouched(entry: object) -> bool:
    """A seeded slot no role has written in -- the COVERAGE GAP.

    !! THIS IS NOT "HAS NO INSTRUCTION", AND THE DIFFERENCE IS THE DEFECT THIS
    FUNCTION EXISTS FOR. `flows/marks.py` read `mark.get("mark") is None` and
    skipped, so an entry a role HAD filled in but that named no instruction --
    or named it under a key the code did not read -- was dropped before any
    check saw it and recounted as a place nobody looked at. MEASURED
    2026-08-29: `reviewer-brief.md`'s own worked example, which keys the ruling
    `instruction`, passed `mark --check` at exit 0 as UNRULED.

    ! So an untouched slot is BOTH things at once: `instruction` present and
    null -- the key `seed()` writes -- AND none of `ROLE_FIELDS` filled. An
    entry that fails either half is a ruling, and goes to `parse`, which
    refuses it by name.

    Args:
        entry: one entry of a sheet's `marks`, as it came back.

    Returns:
        True only for a slot that is still exactly as `seed()` handed it out.
    """
    if not isinstance(entry, dict):
        return False
    data: dict = entry
    if "instruction" not in data or data["instruction"] is not None:
        return False
    return not any(data.get(key) for key in ROLE_FIELDS)


def parse(where: str, entry: object) -> tuple[Mark | None, list[str]]:
    """THE BOUNDARY -- one entry becomes a `Mark`, or becomes named problems.

    !! THERE IS NO THIRD OUTCOME, and that is the whole point of the function.
    `problems(where, mark: dict)` returned messages and left the dict for the
    caller to use anyway, so a half-valid mark reached every consumer and each
    one re-derived the same fields by key.

    ! What is NOT checked here, because it needs the page the role read: whether
    the address resolves, whether a quoted sentence is really in the paragraph,
    and whether a `move`'s destination is addressable. Those belong to
    SOURCE-VERIFICATION, in `collator`.

    ! CALL `untouched` FIRST where a coverage gap is legal. This function has
    no reading of a slot nobody ruled on other than a refusal, which is correct
    for a mark and wrong for a seeded row.

    Args:
        where: how to name this mark in a message -- an address, or a position.
        entry: one role's ruling on one place, as it came back. ! AN ABSENT
            `raw_text` IS NOT REFUSED -- it is seeded, so its absence is drift
            rather than a malformed shape, and `desk.collator.drift_in` is
            what rules on it. Refusing an absent field here while a CHANGED one
            is only reported would be two treatments of one problem.

    Returns:
        `(Mark, [])` or `(None, [one message per broken rule])`, in the order a
        reader would meet them. A `Mark` says the SHAPE is sound and says
        nothing about whether the claim is true.
    """
    if not isinstance(entry, dict):
        return None, [f"{where}: a mark must be an object"]
    data: dict = entry
    if "instruction" not in data:
        return None, [
            f"{where}: carries no `instruction` -- the field naming which of "
            f"{', '.join(sorted(INSTRUCTIONS))} this mark is"
        ]
    named = data["instruction"]
    if not isinstance(named, str) or named not in INSTRUCTIONS:
        return None, [
            f"{where}: `instruction` must be one of {', '.join(sorted(INSTRUCTIONS))}"
        ]

    instruction = Instruction(named)
    spec = INSTRUCTIONS[instruction]
    out = []
    # !! `reason` AND `address` ARE OWED BY DEFAULT; ONLY `clean` DEVIATES, and
    # `clean` is the one row `substantive` is False for -- so that flag is what
    # both this function and `_claim_problems` above key off of.
    if spec.substantive and not filled(entry.get("address")):
        # !! COPIED FROM THE ROW, NEVER BUILT. Measured 2026-08-27: with a
        # one-file binder every fanned-out agent wrote a bare cue, and 62 of 78
        # marks came back unqualified -- `a0` then means four different places.
        out.append(f"{where}: {instruction} needs the `address`, copied from the row")
    if spec.substantive and not filled(entry.get("reason")):
        out.append(f"{where}: {instruction} needs a `reason`")
    out += _claim_problems(where, instruction, entry.get("claim"))
    if spec.owes_sources:
        out += _source_problems(where, entry.get("sources"))
    if spec.owes_change:
        out += _change_problems(where, instruction, spec, entry.get("change"))
    if out:
        return None, out

    claim = entry.get("claim")
    sources = entry.get("sources")
    change = entry.get("change")
    return (
        Mark(
            address=str(entry.get("address") or ""),
            anchor=str(entry.get("anchor") or ""),
            raw_text=str(entry.get("raw_text") or ""),
            instruction=instruction,
            # ! COPIED, NOT ALIASED -- a `Mark` is frozen, and sharing the
            # caller's own containers would leave it mutable through them.
            claim=dict(claim) if isinstance(claim, dict) else {},
            reason=str(entry.get("reason") or ""),
            sources=tuple(sources) if isinstance(sources, list) else (),
            change=change if isinstance(change, str) else "",
        ),
        [],
    )
