"""Mark errors -- every place a role must go back to, as addresses and reasons.

    mark_errors(edit_copies, required=None)
                               one `Revisit` per place a role still owes

!! Addresses and reasons, never a rebuilt copy. A role holds its own edit_copy
and finds the marks in its remit there; what it needs told is where and what.

! **Why not one `EditCopy` per role holding only the places needing work.** It
would reuse a container a role already knows how to fill -- and it is a second
copy of those marks. The role's own edit_copy still holds the originals, so
*what needs fixing* would live in two documents and a role would fill one while
the other went stale.

!! It has two readers: the task agent, through `flows.bus`, and a role checking its
own copy, through `commands/check.py`. Every entry names the role that owes it, so
dispatch is a read rather than a lookup across two lists.

!! The bound on sending back is not here. This flow says what is owed; how
many times a role is sent back is the task agent's instructions, and nothing in
code bounds it.

! What it does not do is verification. `desk.collator.verify_report` asks
whether a well-formed mark's claims hold against the tree; this asks only about
places that produced no usable mark at all. `flows.verify.admitted_copy_problems`
calls `verify_report`; `flows.bus` turns each `Revisit` into a `Problem` and
puts both into the one `problems` list it rolls back with.
"""

from typing import NamedTuple

from comment_review.desk.proof.edit_copy import EditCopy

#: What a place a role was handed and left alone is reported as. It is the one
#: sentence for that case, so a reader meets the same words wherever it is
#: printed.
NOT_RULED = "handed to this role and not ruled on"


class Revisit(NamedTuple):
    """One place a role must go back to, and why.

    Attributes:
        role: who owes it -- what makes this dispatchable rather than a list a
            task agent has to attribute by hand.
        address: the place, and "" where the entry named none. ! Nothing reads
            it: `flows.bus` and `commands/check.py` route and print by `where`.
        where: how to point at it, never empty -- the address where there is
            one, else the page and the entry's position, as `m.py mark 3`.
            ! A reader needs somewhere to look even for an entry the system
            cannot route.
        reasons: every rule the entry broke, as its type's read worded them,
            or the one sentence `NOT_RULED` for a place nobody wrote in.
            ! All of them together -- one malformed `correct` breaks four
            rules, and a role fixing them one per round is three more round
            trips.
    """

    role: str
    address: str
    where: str
    reasons: tuple[str, ...]


def mark_errors(
    edit_copies: list[EditCopy], required: list[frozenset[str]] | None = None
) -> list[Revisit]:
    """Every place a role must revisit, across one stage's returned copies.

    Args:
        edit_copies: the parsed copies, as `flows.bus` holds them after the
            command's envelope pass. ! Parsed, because that is what sorted each
            entry: `desk.proof.sheet.Sheet` carries `unruled` and `refused`, and
            this flow reads them rather than re-deciding what an entry was.
        required: each copy's assigned addresses, in the same order as the copies.
            An unruled place outside them is not reported, and `None` reports
            every unruled place; a refused entry is reported whatever this holds.

    Returns:
        One `Revisit` per place, in role then `where` order -- so a task agent
        reads a role's whole list together and can hand it over in one message.
        Empty where every role answered every place readably.

        ! One entry per place per role, and two roles owing the same address is
        two entries. They are two things to fix, by two different agents;
        collapsing them would leave a reader unable to say who owes what.

        ! Nothing of the mark is copied, which is why this returns `Revisit`
        and not a container.
    """
    out = [
        Revisit(copy.role, one.address, one.where, one.reasons)
        for copy in edit_copies
        for sheet in copy.sheets
        for one in sheet.refused
    ] + [
        # ! An unruled place always has an address, so `where` is that address.
        # `Sheet.deserialize` refuses an untouched entry that names none rather
        # than counting it a coverage gap -- see `_sorted_entries`.
        Revisit(copy.role, address, address, (NOT_RULED,))
        for i, copy in enumerate(edit_copies)
        for sheet in copy.sheets
        for address in sheet.unruled
        if required is None or address in required[i]
    ]
    # ! Sorted so a stranger re-derives the order. The walk above is copy then
    # sheet then entry, which is an accident of how the stage was assembled;
    # what a reader acts on is a role's places together. ! On `where`; an entry
    # with no address sorts by its page's path spelled with `/`, an addressed
    # one by the path flattened with `:`, so the two need not sit together.
    return sorted(out, key=lambda one: (one.role, one.where))
