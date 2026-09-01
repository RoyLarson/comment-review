"""MARK ERRORS -- every place a role must go back to, as addresses and reasons.

    mark_errors(edit_copies)   one `Revisit` per place a role still owes

!! ADDRESSES AND REASONS, NEVER A REBUILT COPY -- `decision-log.md Process: #72`.
Roy, 2026-09-01: *"I think the return is a list of addresses and a statement of
what the parse errors are for each address. The agents can find the marks in
their remit and fix in their stuff directly. No reason to try to duplicate or
fill in the problems for them and have disjointed what needs fixed."*

! **THE ALTERNATIVE WAS DESIGNED AND REJECTED, AND THE REASON IS THE POINT.**
Emitting one `EditCopy` per role holding only the places needing work reuses a
container a role already knows how to fill -- and it is a SECOND copy of those
marks. The role's own edit_copy still holds the originals, so *what needs
fixing* would live in two documents and a role would fill one while the other
went stale.

!! IT IS FOR THE TASK AGENT, WHICH IS WHY IT IS ASSEMBLED AT ALL. Roy, the same
day: the flow *"collects the errors and makes something that helps the task
agent point to the correct ones for the role agents."* Every entry names the
ROLE that owes it, so dispatch is a read rather than a join.

!! THE BOUND ON SENDING BACK IS NOT HERE. Roy, 2026-09-01: it *"will put it in
the task agent briefing"*, and `a-coverage-gap-should-go-back-to-the-reviewer`
T2 holds it open -- *"with no bound, send it back is a loop."* This flow says
WHAT is owed; how many times it may be asked for is the briefing's.

! WHAT IT DOES NOT DO IS VERIFICATION. `desk.collator.verify_report` asks
whether a well-formed mark's claims hold against the tree; this asks only about
places that produced no usable mark at all. The two are separate lists on
`flows.collate.Collated` for that reason.
"""

from typing import NamedTuple

from comment_review.desk.containers import EditCopy

#: What a place a role was handed and left alone is reported as. It is the one
#: sentence for that case, so a reader meets the same words wherever it is
#: printed.
NOT_RULED = "handed to this role and not ruled on"


class Revisit(NamedTuple):
    """One place a role must go back to, and why.

    Attributes:
        role: who owes it -- what makes this dispatchable rather than a list a
            task agent has to attribute by hand.
        address: the place, and "" where the entry named none. ! IT IS WHAT
            ROUTES, and nothing prints it.
        where: how to POINT AT it, never empty -- the address where there is
            one, else the page and the entry's position, as `m.py mark 3`.
            ! THE TWO ARE SEPARATE BECAUSE ONE CAN BE EMPTY AND THE OTHER MUST
            NOT BE. A reader needs somewhere to look even for an entry the
            system cannot route; a router needs to know when there is nowhere.
        reasons: every rule the entry broke, as `desk.mark.parse` worded them,
            or the one sentence `NOT_RULED` for a place nobody wrote in.
            ! ALL OF THEM TOGETHER, which is the half `Process: #72` asks for
            beyond the address -- one malformed `correct` breaks four rules, and
            a role fixing them one per round is three more round trips.
        unreadable: True where a role WROTE here and the entry would not parse;
            False where nobody wrote here at all.

            !! IT EXISTS BECAUSE THE EXIT CODE BRANCHES ON IT, which is what
            makes it necessary rather than descriptive. `commands/collate.py`
            returns `BROKEN` for a mark that would not read and `COVERAGE` for a
            place left unanswered -- the second routes back without voiding the
            round (`Process: #63`) and the first does not. Without this the two
            are one list and the command cannot tell them apart.
            ! THE TWO ARE NOT THE SAME FACT, which `desk.mark.untouched`'s own
            docstring already forbids conflating: a malformed mark means a role
            DID rule here and got the shape wrong.
    """

    role: str
    address: str
    where: str
    reasons: tuple[str, ...]
    unreadable: bool


def mark_errors(edit_copies: list[EditCopy]) -> list[Revisit]:
    """Every place a role must revisit, across one stage's returned copies.

    Args:
        edit_copies: the parsed copies, as `flows.collate.collate` holds them
            after its envelope pass. ! PARSED, because that is what sorted each
            entry: `desk.containers.Sheet` carries `unruled` and `refused`, and
            this flow reads them rather than re-deciding what an entry was.

    Returns:
        One `Revisit` per place, in ROLE then ADDRESS order -- so a task agent
        reads a role's whole list together and can hand it over in one message.
        Empty where every role answered every place readably.

        ! ONE ENTRY PER PLACE PER ROLE, and two roles owing the same address is
        two entries. They are two things to fix, by two different agents;
        collapsing them would leave a reader unable to say who owes what.

        ! NOTHING OF THE MARK IS COPIED. That is `Process: #72`, and it is why
        this returns `Revisit` and not a container.
    """
    out = [
        Revisit(copy.role, one.address, one.where, one.reasons, unreadable=True)
        for copy in edit_copies
        for sheet in copy.sheets
        for one in sheet.refused
    ] + [
        # ! AN UNRULED PLACE ALWAYS HAS AN ADDRESS, so `where` is that address.
        # `Sheet.deserialize` refuses an untouched entry that names none rather
        # than counting it a coverage gap -- see `_sorted_entries`.
        Revisit(copy.role, address, address, (NOT_RULED,), unreadable=False)
        for copy in edit_copies
        for sheet in copy.sheets
        for address in sheet.unruled
    ]
    # ! SORTED SO A STRANGER RE-DERIVES THE ORDER. The walk above is copy then
    # sheet then entry, which is an accident of how the stage was assembled;
    # what a reader acts on is a role's places together. ! ON `where` RATHER
    # THAN `address`, so an entry with no address sorts beside the page it sits
    # on instead of ahead of everything.
    return sorted(out, key=lambda one: (one.role, one.where))
