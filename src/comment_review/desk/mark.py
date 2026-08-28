"""What a role writes, and the rules a mark can be judged by ON ITS OWN.

    Instruction      one row -- all this system knows about one of the seven
    INSTRUCTIONS     the seven, closed
    QUERY_SHAPES     the three a `query` must name, closed
    allowed()        the shape a role is handed, generated from the rows
    problems()       every rule this file can settle without the binder

!! A MARK IS THE OBJECT; ITS `instruction` IS ONE OF SEVEN. The word this table
used to carry read as judicial and named the same thing twice, the object a
*finding* and its type the struck word -- `decision-log.md Vocabulary: #17`.
! `instruction` is the trade's: a proof correction has a TEXTUAL mark saying
where and a MARGINAL mark saying what to do, and the second is the instruction --
which is what a compositor executes, and this system has one.

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

!! `Instruction` CARRIES ONLY WHAT `docs/the-mark.md` APPROVES -- ELEVEN
FIELDS, NO PROSE. A 22-field scheme entered this file on 2026-08-27 during a
port that was never proposed and never approved -- `decision-log.md Process:
#37`. `docs/the-mark.md` is the spec; this file implements it and defines
nothing. `tests/gates/test_mark_shape.py` reads the spec's own tables and
refuses a field that is not one of them.
"""

import re
from dataclasses import dataclass

# !! THE THREE SHAPES A `query` MUST NAME, KEYED ON WHO RESOLVES IT.
# `decision-log.md Process: #33`, Roy 2026-08-27. The set they replaced --
# `outside the checkout`, `outside the code` -- was keyed on WHERE the missing
# evidence lived, and rested on a reviewer in a FRESH CHECKOUT reaching the same
# evidence later. Roy: *"this really is not expected to be a repeatable event."*
#
# ! A cause belongs in `reason`, which a human reads. A SHAPE is read by the
# flow, and the flow can do nothing with a cause.
OUT_OF_ROLE = "outside-my-role"
#: ! The one a collate step can ACT on: another role may have settled this place.
UNDETERMINED = "unable-to-determine"
NEEDS_HUMAN = "human-review-necessary"
QUERY_SHAPES = (OUT_OF_ROLE, UNDETERMINED, NEEDS_HUMAN)

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
class Instruction:
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


INSTRUCTIONS: dict[str, Instruction] = {
    "clean": Instruction(
        owes_change=False,
        owes_sources=False,
        substantive=False,
    ),
    "query": Instruction(
        claim_all=("shape", "attempted", "settles"),
        owes_change=False,
        can_declare_scope=True,
    ),
    "drop": Instruction(
        claim_all=("drop",),
        quotes_original="drop",
        may_empty=True,
    ),
    "correct": Instruction(
        claim_all=("false", "true"),
        quotes_original="false",
        rules_on_text=True,
    ),
    "patch": Instruction(
        claim_all=("from", "to"),
        quotes_original="from",
        # !! `patch` NEEDS NO SOURCE: the claim is already true, and only its
        # wording is at issue. Measured 2026-08-22, re-confirmed twice: this
        # flag and the brief's own sentence shipped out of agreement once, and
        # the gate fatally refused every `patch` a compliant reviewer filed.
        owes_sources=False,
        rules_on_text=True,
    ),
    "add": Instruction(
        claim_all=("missing", "anchor"),
        diffable=False,
        needs_anchor=True,
    ),
    "move": Instruction(
        claim_all=("from", "to"),
        owes_destination=True,
    ),
}


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
        work; `anchor_form` -> the form an `add`'s anchor takes.
    """
    claims = {name: list(spec.claim_all) for name, spec in INSTRUCTIONS.items()}
    return {
        "instruction": sorted(INSTRUCTIONS),
        "claim": claims,
        "values": {"shape": list(QUERY_SHAPES)},
        "scope_shape": OUT_OF_ROLE,
        # ! A FORM, not a value set, and it is stated for the same reason the sets
        # are: a template that constrains a field without saying what is allowed
        # has only moved the guessing.
        "anchor_form": f"the anchor NAMED in backticks, e.g. {ANCHOR_EXAMPLE}",
        "source_keys": {"required": ["cite", "verbatim"], "optional": ["ran"]},
    }


def _claim_problems(where: str, instruction: str, claim: object) -> list[str]:
    """Whether `claim` carries the keys this instruction's row demands.

    ! READS `spec.claim_all` DIRECTLY. With every key an instruction owes
    stated once in that one list, there is nothing left to derive it from.
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


def problems(where: str, mark: dict) -> list[str]:
    """Every rule this file can settle -- the shape, not the truth.

    ! What is NOT checked here, because it needs the page the role read: whether
    the address resolves, whether a quoted sentence is really in the paragraph,
    and whether a `move`'s destination is addressable. Those belong to
    SOURCE-VERIFICATION, in `collator`.

    Args:
        where: how to name this mark in a message -- an address, or a position.
        mark: one role's ruling on one place.

    Returns:
        One message per broken rule, in the order a reader would meet them.
        Empty means the SHAPE is sound and says nothing about the claim.
    """
    instruction = mark.get("mark")
    if not isinstance(instruction, str) or instruction not in INSTRUCTIONS:
        return [f"{where}: `mark` must be one of {', '.join(sorted(INSTRUCTIONS))}"]

    spec = INSTRUCTIONS[instruction]
    out = []
    # !! `reason` AND `address` ARE OWED BY DEFAULT; ONLY `clean` DEVIATES, and
    # `clean` is the one row `substantive` is False for -- so that flag is what
    # both `problems()` here and `_claim_problems` above key off of.
    if spec.substantive and not filled(mark.get("address")):
        # !! COPIED FROM THE ROW, NEVER BUILT. Measured 2026-08-27: with a
        # one-file binder every fanned-out agent wrote a bare cue, and 62 of 78
        # marks came back unqualified -- `a0` then means four different places.
        out.append(f"{where}: {instruction} needs the `address`, copied from the row")
    if spec.substantive and not filled(mark.get("reason")):
        out.append(f"{where}: {instruction} needs a `reason`")
    out += _claim_problems(where, instruction, mark.get("claim"))
    if spec.owes_sources:
        out += _source_problems(where, mark.get("sources"))
    if spec.owes_change:
        change = mark.get("change")
        # !! A LINE ARRAY, NOT A STRING. Measured 2026-08-27: one role returned a
        # 3-line update for a 48-line paragraph and another returned a different
        # paragraph with its comment markers gone, which would have made the file
        # unparseable. Both are hand-transcription failures.
        if not isinstance(change, list):
            out.append(f"{where}: {instruction} needs `change` as an ARRAY of lines")
        elif not change and not spec.may_empty:
            out.append(f"{where}: {instruction} needs `change` to hold the new text")
        elif not all(isinstance(line, str) for line in change):
            out.append(f"{where}: every line of `change` must be a string")
    return out
