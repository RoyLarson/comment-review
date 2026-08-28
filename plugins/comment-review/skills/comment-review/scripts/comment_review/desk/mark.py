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

! PORTED from `prototype/original/record.py` on 2026-08-27 at Roy's direction --
*"You can copy it from there and update the rules/requirements from there but it
doesn't belong in the new records.py. It belongs in the desk/ i think."* The
table's shape is that file's; the query shapes, `ran` and the destination rule
are this branch's rulings applied on the way across.
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

    Attributes:
        claim_all: markers `claim` must ALL carry.
        claim_any: markers `claim` must carry at least ONE of.
        claim_help: what to say when either is unmet -- per row, because
            "correct needs a false/true pair" reads and a generated list does not.
        quotes_original: the `claim` key whose value the EXISTING sentence
            follows, or "" when it quotes none. ! `move`'s from/to are
            PLACES and `add` is about prose that is missing, so both quote none.
        change_all: keys `change` must carry. Only `move`, which changes two
            paragraphs and shows both.
        owes_claim: every mark but `clean` states what must happen.
        owes_reason: likewise -- why.
        owes_change: `clean` rules on nothing and `query` proposes no text.
        may_empty: this may leave the paragraph with NOTHING in it, so an
            empty `change` is the edit rather than a missing one. Only `drop`.
        owes_address: `clean` is exempt because a role returns it on most of the
            binder; transcribing each would be the bulk of a report.
        owes_sources: TWO are exempt, for two reasons. `clean` cites no claim so
            it cites no place. `patch` rules on WORDING alone -- nothing outside
            the paragraph settles whether a sentence reads better -- so a source
            would be evidence for a claim nobody made.
        diffable: the original against `change` names the edited sentence. False
            where there is nothing to diff.
        needs_anchor: `claim` names a site in backticks. ! Not a SIDE -- the
            address says that.
        needs_attempted: `claim` names a check that was tried.
        needs_settles: `claim` names what would settle it.
        substantive: this ASKS something of the apply step. Only `clean` does
            not, which is what makes it the null mark rather than a pass.
        can_declare_scope: this may be a BOUNDARY REPORT rather than
            work -- `query`, and only in its `outside-my-role` shape.
        removes: takes the sentence out of the paragraph.
        rules_on_text: keeps the sentence and changes it. ! `removes` against
            `rules_on_text` on ONE sentence is the only contradiction the set can
            express. `move` is deliberately neither: relocation and a truth fix
            COMPOSE.
        owes_destination: `claim.to` names a place that must be
            ADDRESSABLE. ! Not carried by the binder -- Roy, 2026-08-27: *"the
            destination needs to be addressable not necessarily in the binder.
            That includes an external_address-able item."*
        payload: what the brief says this `claim` carries. The row owns it, so
            there is one source and one way to copy it. ! It does NOT
            restate the key names -- those are generated by `claim_keys`.
    """

    claim_all: tuple[str, ...] = ()
    claim_any: tuple[str, ...] = ()
    claim_help: str = ""
    quotes_original: str = ""
    change_all: tuple[str, ...] = ()
    change_help: str = ""
    owes_claim: bool = True
    owes_reason: bool = True
    owes_change: bool = True
    may_empty: bool = False
    owes_address: bool = True
    owes_sources: bool = True
    diffable: bool = True
    needs_anchor: bool = False
    needs_attempted: bool = False
    needs_settles: bool = False
    substantive: bool = True
    can_declare_scope: bool = False
    removes: bool = False
    rules_on_text: bool = False
    owes_destination: bool = False
    payload: str = ""


INSTRUCTIONS: dict[str, Instruction] = {
    "clean": Instruction(
        payload=(
            "nothing. Name your role and stop -- `clean` proposes no text, so there"
            " is nothing for the apply step to apply"
        ),
        owes_claim=False,
        owes_reason=False,
        owes_change=False,
        owes_address=False,
        owes_sources=False,
        diffable=False,
        substantive=False,
    ),
    "query": Instruction(
        payload=(
            "the SHAPE in these exact words, the check you ATTEMPTED, and what WOULD"
            " settle it. All three are checked as SHAPE and none as truth; the claim"
            " itself is checked by nothing, so the other three are all that stands"
            " behind the ruling"
        ),
        claim_any=QUERY_SHAPES,
        claim_help=(
            "query must NAME its shape -- one of "
            + ", ".join(f"'{s}'" for s in QUERY_SHAPES)
            + " -- so the reason is attached to the ruling"
        ),
        owes_change=False,
        diffable=False,
        needs_attempted=True,
        needs_settles=True,
        can_declare_scope=True,
    ),
    "drop": Instruction(
        payload=(
            "the sentence, verbatim, as it stands in the paragraph. ! It is CHECKED"
            " against the page, so a paraphrase is refused"
        ),
        claim_all=("drop",),
        claim_help="drop needs the sentence being removed in `claim.drop`",
        quotes_original="drop",
        removes=True,
        may_empty=True,
    ),
    "correct": Instruction(
        payload=(
            "the false clause and the true one, and a `sources` entry carrying the"
            " line that settles it. ! The FALSE half is checked against the"
            " paragraph -- if it is not there, the finding is on the wrong one"
        ),
        claim_all=("false", "true"),
        claim_help="correct needs `claim.false` and `claim.true`, both filled",
        quotes_original="false",
        rules_on_text=True,
    ),
    "patch": Instruction(
        payload=(
            "the sentence as it stands and the rewrite. ! `from` is checked against"
            " the paragraph. A `patch` needs no source: the claim is already true,"
            " and only its wording is at issue"
        ),
        claim_all=("from", "to"),
        claim_help="patch needs `claim.from` and `claim.to`, both filled",
        quotes_original="from",
        # !! SET FROM THE PAYLOAD ABOVE, WHICH SHIPS. That sentence is generated
        # into the brief and said a patch needs no source while this stayed True,
        # so the prototype's gate fatally refused every `patch` a reviewer filed.
        # Measured 2026-08-22, re-confirmed twice. The gate and the instruction
        # now read off the same row, which is what the row is for.
        owes_sources=False,
        rules_on_text=True,
    ),
    "add": Instruction(
        payload=(
            "the text that is missing and the anchor NAMED IN BACKTICKS."
            ' ! The word "anchor" is not an anchor -- name the declaration.'
            " Which SIDE is the address's to say, never the payload's"
        ),
        claim_all=("missing",),
        claim_help="add needs the text in `claim.missing`",
        diffable=False,
        needs_anchor=True,
    ),
    "move": Instruction(
        payload=(
            "where the prose sits now and where it belongs -- another line, another"
            " file, or out of the code entirely. ! These are PLACES, not text: the"
            " same two key names in `change` mean the resulting PARAGRAPHS"
        ),
        claim_all=("from", "to"),
        claim_help="move needs `claim.from` and `claim.to`, both filled",
        owes_destination=True,
        change_all=("to",),
        change_help=(
            "move needs the DESTINATION paragraph in `change`, as `to` -- plus"
            " `from`, the origin as it reads after, unless the WHOLE paragraph moves"
        ),
        diffable=False,
    ),
}


def claim_keys(spec: Instruction) -> list[str]:
    """Every key this instruction's `claim` must carry.

    !! THE TRAITS DERIVE KEYS, AND DROPPING THAT IS WHAT BROKE THE GATE.
    MEASURED 2026-08-28: without it, `allowed()` published `query`'s three
    SHAPE VALUES as though they were claim KEYS, so a mark written from the
    brief verbatim was refused. One row states the whole obligation; a trait
    added here reaches the gate, the brief and the sheet together.
    """
    keys = list(spec.claim_all)
    if spec.claim_any:
        keys.append("shape")
    if spec.needs_attempted:
        keys.append("attempted")
    if spec.needs_settles:
        keys.append("settles")
    if spec.needs_anchor:
        keys.append("anchor")
    return keys


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
    claims = {name: claim_keys(spec) for name, spec in INSTRUCTIONS.items()}
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
    """Whether `claim` carries the keys this instruction's row demands."""
    spec = INSTRUCTIONS[instruction]
    if not spec.owes_claim:
        return []
    if not isinstance(claim, dict):
        return [f"{where}: {instruction} needs a `claim` object -- {spec.claim_help}"]

    out = []
    missing = [k for k in claim_keys(spec) if not filled(claim.get(k))]
    if missing:
        out.append(f"{where}: {spec.claim_help} (missing {', '.join(missing)})")
    # ! The shape is a VALUE in a closed set, not a key. Checking it
    # structurally is what lets `collator` route on it without reading prose.
    if spec.claim_any and claim.get("shape") not in spec.claim_any:
        out.append(f"{where}: {spec.claim_help}")
    if spec.needs_anchor and not ANCHOR_NAME.search(str(claim.get("anchor", ""))):
        out.append(
            f"{where}: add needs the anchor NAMED in backticks, e.g. {ANCHOR_EXAMPLE}"
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
    if spec.owes_address and not filled(mark.get("address")):
        # !! COPIED FROM THE ROW, NEVER BUILT. Measured 2026-08-27: with a
        # one-file binder every fanned-out agent wrote a bare cue, and 62 of 78
        # marks came back unqualified -- `a0` then means four different places.
        out.append(f"{where}: {instruction} needs the `address`, copied from the row")
    if spec.owes_reason and not filled(mark.get("reason")):
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
    for key in spec.change_all:
        change = mark.get("change")
        if isinstance(change, dict) and not filled(change.get(key)):
            out.append(f"{where}: {spec.change_help}")
    return out
