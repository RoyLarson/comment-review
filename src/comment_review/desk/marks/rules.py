"""The rules a mark is held to, read off its instruction's row in the marks table.

    validate()           one mark against its row -- every broken rule, named
    allowed()            the shape a role is handed, generated from the rows
    derived_change()     the `change` a claim implies, built from the paragraph,
                         so a role never types the paragraph out
    first_word_dropped() the keep-the-prose check the rows' `reads` ask
    ANCHOR_NAME          the form an `add`'s anchor is named in

The mark itself -- its fields, its enums and its structural read -- is
`desk.proof.mark`. The proof's parsers are handed `validate` and apply it after
that read (`decision-log.md Process: #203`). This module reads `INSTRUCTIONS`
through function-level imports, never a module-level one, which would cycle
with `desk.marks.table`'s own import of `first_word_dropped` from here.

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

A 22-field scheme entered the marks module on 2026-08-27 during a port that was
never proposed and never approved -- `decision-log.md Process: #37`. `Row`
carried only what `docs/the-mark.md` approved for that reason. T1 of
`docs/superpowers/plans/2026-09-14-the-middle-rebuilt.md` moved it to
`desk.marks.table` and gave it `touches`, `sets`, `reads`, `pairs` and
`answers` -- fields the marks table needs -- and added the matching rows
to `docs/the-mark.md`'s own classifiers and flags tables in the same change,
so `tests/gates/test_mark_shape.py` still refuses a field that is not one
of the spec's own, for `Row` as well as the eight for `Mark`.
"""

import re
import textwrap
from typing import TYPE_CHECKING

from comment_review.desk.proof.mark import (
    QUERY_SHAPES,
    Instruction,
    Mark,
    Shape,
    filled,
)
from comment_review.reading.addresser import cue_of, folded

if TYPE_CHECKING:
    # Type-only: `table` imports `first_word_dropped` from this module, so a
    # runtime import here would be the cycle a direct coupling between the two
    # would create. A type checker resolves this import for its own analysis
    # without it ever running; every runtime read of `Row` or `INSTRUCTIONS`
    # below is a function-level import instead.
    from comment_review.desk.marks.table import Row


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


def validate(where: str, mark: Mark) -> list[str]:
    """Every rule `mark`'s instruction's row states that the mark breaks.

    A rule asks only of a field the row takes; a field the row does not take is
    never refused (`decision-log.md Process: #204`).

    What is NOT checked here, because it needs the page the role read: whether
    the address resolves, and whether a quoted sentence is really in the
    paragraph. Those belong to SOURCE-VERIFICATION, in `collator`. ! A `move`'s
    destination is HALF here: that it is not the origin is answerable from the
    entry alone; that it is ADDRESSABLE is not.

    Args:
        where: how to name this mark in a message -- an address, or a position.
        mark: the entry as `desk.proof.mark.Mark.deserialize` read it, a
            field of the wrong type already read as absent; its `instruction`
            is what selects the row. An absent `raw_text` is not refused. It is
            seeded, and the base a mark is measured against is never this
            field; a row that writes its own `raw_text` is held to what it wrote
            by that row's `reads`.

    Returns:
        One message per broken rule, in the order a reader would meet them;
        empty for a mark that keeps its row. It says nothing about whether the
        claim is true.
    """
    from comment_review.desk.marks.table import INSTRUCTIONS

    instruction = mark.instruction
    spec = INSTRUCTIONS[instruction]
    out = []
    # !! `reason` AND `address` ARE OWED BY DEFAULT; ONLY `clean` DEVIATES, and
    # `clean` is the one row `substantive` is False for -- so that flag is what
    # both this function and `_claim_problems` below key off of.
    if spec.substantive and not filled(mark.address):
        # !! COPIED FROM THE ROW, NEVER BUILT. Measured 2026-08-27: with a
        # one-file binder every fanned-out agent wrote a bare cue, and 62 of 78
        # marks came back unqualified -- `a0` then means four different places.
        out.append(f"{where}: {instruction} needs the `address`, copied from the row")
    elif spec.substantive and not _names_a_place(mark.address):
        # `mark-defects` T1: `filled` passed a bare cue, which names a
        # place on no page.
        out.append(
            f"{where}: {instruction} needs its full `path@cue` address, copied"
            f" from the row -- {mark.address!r} names a place on no page"
        )
    if spec.substantive and not filled(mark.reason):
        out.append(f"{where}: {instruction} needs a `reason`")
    out += _claim_problems(where, instruction, mark.claim)
    if spec.owes_destination:
        out += _destination_problems(
            where, mark.address, mark.claim, spec.names_destination
        )
    if spec.owes_sources:
        out += _source_problems(where, mark.sources)
    if spec.owes_change:
        out += _change_problems(where, instruction, spec, mark.change, mark.anchor)
    return out


#: A word, as the keep-the-prose check counts one: a run of letters and
#: digits. Punctuation, whitespace and the underscore only separate words.
_WORD = re.compile(r"[^\W_]+")


def first_word_dropped(prose: str, change: str) -> str | None:
    """The first word of `prose` that `change` does not keep in order, or None.

    `decision-log.md Process: #132`: an `add` at a place holding prose adds to
    that paragraph, so its change holds every word of the prose, in the order
    the prose has them, and punctuation and whitespace are free to move.

    `desk.evaluate` asks the same of a `correct`'s change, over its seeded
    paragraph with `claim.false` taken out (`decision-log.md Process: #163`).
    Moved here from `flows.fill` so the marks table can read it without
    `desk` importing `flows`.
    """
    kept = iter(_WORD.findall(change))
    for word in _WORD.findall(prose):
        if word not in kept:
            return word
    return None


def derived_change(
    instruction: Instruction, claim: object, base: str
) -> tuple[str | None, list[str]]:
    """The `change` this claim implies, built from the paragraph it rules on.

    !! ONE DEFINITION OF WHAT A CLAIM SAYS THE CHANGE IS. The `mark` command
    builds a role's `change` from it, so `claim` and `change` cannot disagree;
    a check that asks whether a returned `change` does only what its `claim`
    names would compare against the same function. Two sites deriving it are
    two that can disagree, which is why it sits with the rows rather than in
    the flow that first needed it.

    ! THE ROW SAYS WHICH KEY IS REPLACED AND WHICH REPLACES IT. `quotes_original`
    names the clause as it stands; the other key in `claim_all` is what takes
    its place, and a row with no other key -- `drop` -- removes the clause. A
    row that quotes nothing (`clean`, `query`, `add`, `move`) derives nothing,
    and its `change` is the role's to supply.

    !! THE QUOTED CLAUSE IS ONE STATEMENT. Roy, 2026-09-07: *"a false clause is
    one statement not multiple paragraphs."* A clause the paragraph holds twice
    names two statements and one it holds nowhere names none; both are refused
    rather than guessed at. The nowhere case is the substring test
    `desk.collator.claim_verbatim_problems` runs at the fold, asked here before
    anything is written.

    Args:
        instruction: which row, already resolved to a member.
        claim: the entry's `claim`, unvalidated -- `validate` runs later and
            refuses a missing key by name; this reports only what stops the
            derivation.
        base: the paragraph the row seeded at this place.

    Returns:
        `(text, [])` -- the paragraph with the one substitution made, "" where
        a `drop` names the whole paragraph. `(None, [])` for a row that quotes
        nothing. `(None, [one message])` where the clause is absent, is not one
        statement, or its counterpart is missing.
    """
    from comment_review.desk.marks.table import INSTRUCTIONS

    spec = INSTRUCTIONS[instruction]
    key = spec.quotes_original
    if not key:
        return None, []
    if not isinstance(claim, dict):
        return None, [f"{instruction} needs `claim.{key}` to derive its change"]
    # ! DECLARED, NOT NARROWED -- `desk.proof.edit_copy.EditCopy.deserialize` states
    # why: `ty` loses an `isinstance` narrow past a branch, and the reads below
    # sit past two.
    data: dict = claim
    quoted = data.get(key)
    if not filled(quoted):
        return None, [f"{instruction} needs `claim.{key}` to derive its change"]
    others = [k for k in spec.claim_all if k != key]
    replacement = ""
    if others:
        counterpart = others[0]
        given = data.get(counterpart)
        if not filled(given):
            return None, [
                f"{instruction} needs `claim.{counterpart}` to derive its change"
            ]
        replacement = given
    found = base.count(quoted)
    if found == 0:
        return None, [f"`claim.{key}` is not in the paragraph this row seeded"]
    if found > 1:
        return None, [
            f"`claim.{key}` occurs {found} times in the paragraph -- a clause "
            "names one statement"
        ]
    changed = base.replace(quoted, replacement)
    if not others:
        # `mark-defects` T25: a dropped clause that spans a line break leaves
        # the text either side of it joined on one line.
        changed = _within(changed, _widest(base))
    return changed, []


#: A line's lead: its indent, then a comment marker and the space after it. No
#: quote mark is a marker, so a docstring's opening line leads with its indent.
_LEAD = re.compile(r"^(\s*(?:[#/*;%:-]+ ?)?)")


def _widest(text: str) -> int:
    """The length of `text`'s longest line."""
    return max((len(line) for line in text.split("\n")), default=0)


def _within(text: str, width: int) -> str:
    """`text` with every line longer than `width` rewrapped under its own lead.

    `mark-defects` T25. A `drop` whose clause spans a line break joins the
    text either side onto one line, which can run past every line the
    paragraph had -- eleven changes on the 2026-09-14 self-run ran past 88
    columns, up to 126. The joined line is rewrapped to the paragraph's own
    widest line, each new line carrying the lead the joined one had. A single
    word longer than that is left whole.
    """
    out: list[str] = []
    for line in text.split("\n"):
        if len(line) <= width:
            out.append(line)
            continue
        found = _LEAD.match(line)
        lead = found.group(1) if found else ""
        wrapped = textwrap.wrap(
            line[len(lead) :],
            width=width,
            initial_indent=lead,
            subsequent_indent=lead,
            break_long_words=False,
            break_on_hyphens=False,
        )
        out += wrapped or [line]
    return "\n".join(out)


def allowed() -> dict:
    """The shape a role is handed -- generated from the rows, never hand-written.

    Returns:
        `instruction` -> the seven; `claim` -> the keys each instruction's claim must
        carry; `values` -> the fields whose value is itself a closed set;
        `scope_shape` -> the one shape that is a boundary report rather than
        work; `anchor_form` -> the form an `add`'s anchor takes; `raw_text` ->
        which instructions write it, and what it means where they do;
        `edit_copy_header` -> the keys an `edit_copy` carries beside its sheets.

    !! IT WAS `sheet_header`, AND BOTH THE NAME AND ITS TWO DESCRIPTIONS WERE
    FALSE. `role` and `read_from` sit on the EDIT_COPY -- `seed` returns
    `{"role", "read_from", "sheets"}` and a sheet carries `{"path", "sha",
    "marks"}` -- so a role reading `distribute --shape` was told to put two keys on
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
    from comment_review.desk.marks.table import INSTRUCTIONS

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
        # Who writes `raw_text` rather than copying it: the rows whose
        # `carries_raw_text` is set (`decision-log.md Process: #175`, `#176`).
        "raw_text": {
            "owed_by": sorted(
                name for name, spec in INSTRUCTIONS.items() if spec.carries_raw_text
            ),
            "is": (
                "the paragraph as it will read, with your text in, in the"
                " page's own form"
            ),
        },
        "source_keys": {"required": ["cite", "verbatim"], "optional": ["ran"]},
        "edit_copy_header": {
            "role": "the role this edit_copy was seeded for",
            "read_from": (
                "the tree this edit_copy was gathered from -- "
                '`{"root": "<path>", "revise": <number>}`, '
                "where revise 0 is the original"
            ),
        },
    }


def _claim_problems(where: str, instruction: Instruction, claim: dict) -> list[str]:
    """Whether `claim` carries the keys this instruction's row demands.

    ! READS `spec.claim_all` DIRECTLY. With every key an instruction owes
    stated once in that one list, there is nothing left to derive it from. A
    row that names no key -- `clean` -- asks nothing of `claim`.

    Args:
        where: how to name this mark in a message -- an address, or a position.
        instruction: already resolved to a member by `Mark.deserialize`;
            `validate` is its only caller.
        claim: the mark's `claim`; `{}` where the entry carried none, or one
            that is not an object.
    """
    from comment_review.desk.marks.table import INSTRUCTIONS

    spec = INSTRUCTIONS[instruction]
    if not spec.claim_all:
        return []
    out = []
    missing = [k for k in spec.claim_all if not filled(claim.get(k))]
    if missing:
        out.append(
            f"{where}: {instruction} needs `claim` to carry "
            f"{', '.join(spec.claim_all)} (missing {', '.join(missing)})"
        )
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


def _source_problems(where: str, sources: tuple[object, ...]) -> list[str]:
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
    if not sources:
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
    where: str, instruction: Instruction, spec: "Row", change: str | None, anchor: str
) -> list[str]:
    """Whether `change` is the updated paragraph, as RAW TEXT.

    !! RAW TEXT, NOT A LINE ARRAY. `docs/the-mark.md`, Roy 2026-08-28: *"`change`
    needs to be the updated paragraph as raw text not lines or sentences. This
    will make it easier to diff per the rest of the stages."* The seeded row
    carries `raw_text` and the role returns `change`; every stage downstream is
    a diff of one against the other, and a line array has to be joined before
    any of them can run.

    ! A `change` that is absent or not a string -- the retired line array
    among them -- is None on the mark, and is refused with the one message
    that names what is owed: the paragraph as RAW TEXT.

    ! AN EMPTY STRING IS THE EDIT on `drop`, the one row `may_empty` is True
    for, where the claim names the whole paragraph.

    ! `filled()`, NOT A BARE TRUTHINESS TEST -- `may_empty` decides whether NO
    content is acceptable; it says nothing about whether WHITESPACE counts as
    content, and it should not. `not change` alone let a role return `"   "`
    for a `correct` or a `patch` and pass unchallenged, the same gap `filled`
    exists to close for a `claim` key.

    A `change` holding a line equal to the mark's `anchor`, whitespace aside,
    is refused: the anchor is the line of code the place sits on, and a change
    is the paragraph alone (`collator-defects` T35).
    """
    if change is None:
        return [
            f"{where}: {instruction} needs `change` as the updated paragraph in "
            "RAW TEXT"
        ]
    if not filled(change) and not spec.may_empty:
        return [f"{where}: {instruction} needs `change` to hold the new text"]
    if filled(anchor) and anchor.strip() in (
        line.strip() for line in change.splitlines()
    ):
        return [
            f"{where}: {instruction}'s `change` carries the anchor's own line of "
            f"code, {anchor.strip()!r} -- `change` is the paragraph alone"
        ]
    return []


def _names_a_place(value: object) -> bool:
    """Whether `value` is a `path@cue` address -- a page, and a place on it.

    `reading.addresser.cue_of` is the one parse of an address, and it answers
    two blanks for anything that is not one, a bare cue included. The value is
    asked as it will be stored; whether it is spelled as the page prints it is
    `flows.verify.resolution_problems`' question.
    """
    if not isinstance(value, str):
        return False
    got = cue_of(value)
    return bool(got.path.strip() and got.cue.strip())


def _destination_problems(where: str, address: str, claim: dict, key: str) -> list[str]:
    """WHERE a `move` sends the paragraph, checked against where it already IS.

    !! A DESTINATION EQUAL TO THE ORIGIN IS REFUSED, and it is the half of
    `owes_destination` one mark can answer alone. MEASURED 2026-08-30: such a
    mark parsed with no problems reported, `collator._touches` deduped its
    two ends to one address, and the docket step wrote the delete at the origin
    with no matching write -- the paragraph removed and never put back.

    Its form is asked here too: a destination is a `path@cue` place, for now
    (`decision-log.md Process: #173`). Whether the page carries that place
    needs the page, and is `flows.verify.resolution_problems`' -- which
    `collate` and `check` both run.

    Args:
        where: how to name this mark in a message.
        address: the mark's own `address`.
        claim: the mark's `claim`.
        key: the claim key the row names its destination under
            (`desk.marks.table.Row.names_destination`).

    Returns:
        One message, or an empty list. A destination that is not a string says
        nothing here -- `_claim_problems` is what refuses a missing one, and
        this step has nothing to compare.
    """
    destination = claim.get(key)
    if not isinstance(destination, str):
        return []
    # Folded, not compared as typed: a destination differing from the origin
    # only in case or surrounding whitespace names the same paragraph on a
    # file system that ignores case, and the delete lands without the write.
    if folded(destination) and folded(destination) == folded(address):
        return [
            f"{where}: `claim.{key}` is this mark's own `address` -- a move to "
            "where the paragraph already is deletes it and writes nothing back"
        ]
    # PROVISIONAL, `decision-log.md Process: #173`: a destination that is not a
    # `path@cue` place -- a path outside the code, a `file:line`, a bare cue --
    # is carried by neither the fold nor the write end, and the 2026-09-14
    # self-run filed 23 that only `collate` refused. Once external documents
    # have addresses, a move to one of them is carried.
    if destination.strip() and not _names_a_place(destination):
        return [
            f"{where}: `claim.{key}` {destination!r} is not a `path@cue` place -- a"
            " destination on a gathered page is its full address, as the addresser"
            " prints it, and one outside the code is not carried yet"
            " (`decision-log.md Process: #173`): file a `human-review-necessary`"
            " query here naming it instead"
        ]
    return []
