"""What a mark's claim implies, and the shape a role is handed.

    allowed()            the shape a role is handed, generated from the types
                         and the rows
    derived_change()     the `change` a claim implies, built from the paragraph,
                         so a role never types the paragraph out
    first_word_dropped() the keep-the-prose check the rows' `reads` ask
    comment_at()         the comment form an address assigns to its raw text,
                         read here and by the marks table

The mark itself -- its types, its fields and the checks reading an entry into
its type asks -- is `desk.proof.mark`. This module reads `INSTRUCTIONS`
through function-level imports, never a module-level one, which would cycle
with `desk.marks.table`'s own import of `first_word_dropped` from here.
"""

import re
from pathlib import Path

from comment_review.desk.proof.edit_copy import EditCopy
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
from comment_review.reading.comment import Comment, comment_form
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

    An `add` at a place holding prose adds to that paragraph, so its
    `raw_text` holds every word of the prose and of its change, in the order
    the prose has them, and punctuation and whitespace are free to move. A
    `move` is asked the same at its destination: its `raw_text` keeps every
    word of the destination's paragraph and of the snippet that arrives.

    The marks table asks the same of a `correct`'s change, over its seeded
    paragraph with `claim.false` taken out. This function sits in `desk` so
    the marks table can read it without `desk` importing `flows`.
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
    address: str,
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

    !! The quoted clause is one statement. A clause the paragraph holds twice
    names two statements and one it holds nowhere names none; both are refused
    rather than guessed at. `desk.collator.claim_verbatim_problems` asks the
    same of every quoting mark at the fold, a supplied change included; this
    asks it before anything is written.

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
    if others:
        return base.replace(quoted, replacement), []
    # A drop is removed within the comment form, which rewrites only the lines
    # the clause stood on.
    at = base.index(quoted)
    changed = comment_at(address, base, anchor=anchor).without_raw(at, at + len(quoted))
    if changed is None:
        return None, [f"`claim.{key}` cannot be removed within its comment form"]
    return changed, []


def allowed() -> dict:
    """The shape a role is handed -- generated, never hand-written.

    Returns:
        `instruction` -> the seven; `claim` -> the keys each instruction's claim must
        carry; `values` -> the fields whose value is itself a closed set;
        `scope_shape` -> the one shape that is a boundary report rather than
        work; `anchor_form` -> the form an `add`'s anchor takes; `raw_text` ->
        which instructions write it, and what it means where they do;
        `source_keys` -> the required and optional keys of a `sources` entry;
        `edit_copy_header` -> the keys an `edit_copy` carries beside its sheets.

    ! What a role does with the `edit_copy` header's `read_from` is the `agents`
    lane. This states the key and its shape, which `docs/conventions.md` puts on
    this side; the instruction to read `read_from` before ruling belongs in the
    reviewer brief and is not written here.
    """
    from comment_review.desk.marks.table import INSTRUCTIONS

    claims = {name: list(mark_type(name).claim_all) for name in INSTRUCTIONS}
    return {
        "instruction": sorted(INSTRUCTIONS),
        "claim": claims,
        "values": {
            "shape": list(QUERY_SHAPES),
            "admits": sorted(str(member) for member in Instruction),
        },
        "scope_shape": Shape.OUTSIDE_MY_ROLE,
        # ! A FORM, not a value set, and it is stated for the same reason the sets
        # are: a template that constrains a field without saying what is allowed
        # has only moved the guessing.
        "anchor_form": f"the anchor NAMED in backticks, e.g. {ANCHOR_EXAMPLE}",
        # Who writes `raw_text` rather than copying it: the rows whose
        # `carries_raw_text` is set.
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
        "edit_copy_header": EditCopy.header_contract(),
    }
