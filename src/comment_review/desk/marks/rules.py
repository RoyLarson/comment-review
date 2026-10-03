"""What a mark's claim implies, and the shape a role is handed.

    allowed()            the shape a role is handed, generated from the types
                         and the rows
    derived_change()     the `change` a claim implies, built from the paragraph,
                         so a role never types the paragraph out
    first_word_dropped() the keep-the-prose check the rows' `reads` ask

The mark itself -- its types, its fields and the checks reading an entry into
its type asks -- is `desk.proof.mark`. This module reads `INSTRUCTIONS`
through function-level imports, never a module-level one, which would cycle
with `desk.marks.table`'s own import of `first_word_dropped` from here.
"""

import re
import textwrap
from pathlib import Path

from comment_review.desk.proof.mark import (
    ANCHOR_EXAMPLE,
    QUERY_SHAPES,
    Instruction,
    Shape,
    filled,
    mark_type,
)
from comment_review.desk.proof.source import contract as source_contract
from comment_review.reading.addresser import cue_of
from comment_review.reading.comment import Comment
from comment_review.reading.lexer import comment_form
from comment_review.reading.series import Series


def comment_at(address: str, raw_text: str, *, anchor: str = "") -> Comment:
    """The assigned form and prose carried by this address's raw text."""
    named = cue_of(address)
    return comment_form(Path(named.path), Series.of(named.cue), raw_text, anchor)


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
    instruction: Instruction,
    claim: object,
    base: str,
    *,
    address: str = "",
    anchor: str = "",
) -> tuple[str | None, list[str]]:
    """The `change` this claim implies, built from the paragraph it rules on.

    !! ONE DEFINITION OF WHAT A CLAIM SAYS THE CHANGE IS. The `mark` command
    builds a role's `change` from it, so `claim` and `change` cannot disagree;
    a check that asks whether a returned `change` does only what its `claim`
    names would compare against the same function. Two sites deriving it are
    two that can disagree, which is why it sits with the rows rather than in
    the flow that first needed it.

    ! THE TYPE SAYS WHICH KEY IS REPLACED AND WHICH REPLACES IT.
    `quotes_original` names the clause as it stands; the other key in
    `claim_all` is what takes its place, and a type with no other key -- `drop`
    -- removes the clause. A type that quotes nothing (`clean`, `query`, `add`,
    `move`) derives nothing, and its `change` is the role's to supply.

    !! THE QUOTED CLAUSE IS ONE STATEMENT. Roy, 2026-09-07: *"a false clause is
    one statement not multiple paragraphs."* A clause the paragraph holds twice
    names two statements and one it holds nowhere names none; both are refused
    rather than guessed at. The nowhere case is the substring test
    `desk.collator.claim_verbatim_problems` runs at the fold, asked here before
    anything is written.

    Args:
        instruction: which of the seven, already resolved to a member.
        claim: the entry's `claim`, unchecked -- `read_mark` runs later and
            refuses a missing key by name; this reports only what stops the
            derivation.
        base: the paragraph the row seeded at this place.
        address: the seeded place, used to recover its assigned comment form.
        anchor: the carried code beside a trailing comment.

    Returns:
        `(text, [])` -- the paragraph with the one substitution made, "" where
        a `drop` names the whole paragraph. `(None, [])` for a row that quotes
        nothing. `(None, [one message])` where the clause is absent, is not one
        statement, or its counterpart is missing.
    """
    kind = mark_type(instruction)
    key = kind.quotes_original
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
    others = [k for k in kind.claim_all if k != key]
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
        if address:
            form = comment_at(address, base, anchor=anchor)
            at = base.index(quoted)
            changed = form.without_raw(at, at + len(quoted))
            if changed is None:
                return None, [
                    f"`claim.{key}` cannot be removed within its comment form"
                ]
        else:
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
    """The shape a role is handed -- generated, never hand-written.

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

    claims = {name: list(mark_type(name).claim_all) for name in INSTRUCTIONS}
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
        "source_keys": source_contract(),
        "edit_copy_header": {
            "role": "the role this edit_copy was seeded for",
            "read_from": (
                "the tree this edit_copy was gathered from -- "
                '`{"root": "<path>", "revise": <number>}`, '
                "where revise 0 is the original"
            ),
        },
    }
