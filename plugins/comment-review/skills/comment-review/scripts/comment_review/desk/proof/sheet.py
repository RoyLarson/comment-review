"""One page's rulings inside an edit_copy, and the parse that sorts its entries.

    Sheet             one PAGE's marks, with that page's path and sha
    Refused           one entry the parse could not read as a mark, and why
    NO_PLACE          the refusal for an untouched entry naming no place

!! `Sheet.marks` HOLDS `Mark`s SINCE `P51`, and was `tuple[object, ...]` --
an entry that is not an object was CARRIED so the mark parse could refuse it
by name rather than have it vanish. `_sorted_entries` refuses it at the parse
instead, into `Sheet.refused`, so nothing vanishes and nothing downstream has to
re-read a raw entry. ! `Mark.sources` IS STILL `object` for the original
reason; the two are no longer the same case.
"""

from dataclasses import dataclass, field
from typing import NamedTuple

from comment_review.desk.proof.mark import (
    Mark,
    filled,
    read_mark,
    untouched,
    without_location,
)
from comment_review.desk.proof.wire import _written


class Refused(NamedTuple):
    """One entry the parse could not read as a mark, and why.

    ! ADDRESS AND REASONS, NEVER THE ENTRY -- `decision-log.md Process: #72`.
    Roy, 2026-09-01: *"The agents can find the marks in their remit and fix in
    their stuff directly. No reason to try to duplicate or fill in the problems
    for them and have disjointed what needs fixed."* The role still holds the
    copy this came out of; what it needs is where and what, not the place back.

    Attributes:
        address: the entry's own `address`, or "" where it carried none -- an
            entry that is not an object, or one whose `address` is not a string.
            ! IT IS WHAT ROUTES, and "" means there is nothing to route on.
            Nothing may print it; `where` is for that.
        where: how to POINT AT the entry, never empty -- the address where there
            is one, else the page and the entry's position on it, as
            `m.py mark 3`.

            !! IT EXISTS BECAUSE `P51` REMOVED THE ONLY HANDLE ON AN
            ADDRESS-LESS ENTRY. `problems_in` fell back to `mark {n}` and that
            was dropped on the reasoning that *a position is not something a
            role can act on* -- which is true everywhere EXCEPT here, where the
            position is the one locator left. MEASURED 2026-09-01: a bare string
            in `marks` reported `block-context (the copy): this mark: a mark
            must be an object`, naming neither the page nor the entry, so a role
            could not find what to fix.
        reasons: every rule the entry broke, as `read_mark` worded them --
            the structural read's, or the validator's it was handed.
            ! ALL OF THEM, not the first -- one malformed `correct` breaks four,
            and a role fixing one at a time is three more round trips.
    """

    address: str
    where: str
    reasons: tuple[str, ...]


#: What a refusal says about an untouched entry naming no place. It is the one
#: sentence for that case, and it is a REFUSAL rather than a coverage gap for
#: the reason `_sorted_entries` gives.
NO_PLACE = "an untouched slot must carry the `address` it was seeded with"


def _sorted_entries(
    path: str,
    marks: list,
) -> "tuple[list[Mark], list[str], list[Refused]]":
    """One sheet's entries, split into the three kinds a returned sheet holds.

    !! THE ONLY PLACE A MARK IS PARSED, since `P51`. It was parsed at FOUR --
    `verify_report` and the passes that build a place from the marks -- so
    every ruled entry was parsed four times per run,
    measured 2026-09-01. Each of those four also spelled its own `where`
    fallback and its own untouched test, which is four chances to disagree
    about what an unruled place is.

    Args:
        path: the page this sheet holds, for the locator below. ! IT IS TAKEN
            RATHER THAN DERIVED because an address-less entry has no other way
            to say which page it sits on.
        marks: the sheet's `marks` list, as it came back. Entries are whatever
            JSON held -- an object, a string, a number.

    Returns:
        `(ruled, unruled, refused)`.

        ruled: one `Mark` per entry that parsed.
        unruled: the ADDRESS of every untouched entry -- `desk.proof.mark.untouched`,
            a place nobody wrote in. ! IT IS ASKED FIRST, because an untouched
            entry does not parse either: `read_mark` refuses its
            `instruction: None` with *"must be one of add, clean, ..."*, which
            would report a coverage gap as a malformed mark.
        refused: one `Refused` per entry that is neither.

    !! AN UNTOUCHED ENTRY NAMING NO PLACE IS REFUSED, NOT UNRULED, and that is
    a ruling rather than a convenience. *"Handed to this role and not ruled on"*
    is a claim about a PLACE, so an entry that names none cannot be it -- and
    `_coverage_problems` reads `unruled` as addresses, so an "" among them would
    count a place the binder never held. `seed` writes the address on every slot
    it hands out, so an entry reaching here without one was edited after it was
    seeded, which is a role's mistake and routes back as one.

    ! AN ENTRY THAT IS NOT AN OBJECT IS REFUSED, NOT DROPPED. `Sheet.marks` was
    typed `object` precisely so a bare string could be named rather than vanish;
    that reason survives the retyping, here, where the entry is read.

    ! AND THE POSITION IS KEPT FOR EXACTLY THE ENTRY THAT NEEDS IT. `P51` cut
    the old `mark {n}` fallback as *not something a role can act on*, which is
    true wherever an address exists and false where none does -- there it is the
    only handle there is. `Refused.where` carries it.
    """
    ruled: list[Mark] = []
    unruled: list[str] = []
    refused: list[Refused] = []
    for n, entry in enumerate(marks, 1):
        address = entry.get("address") if isinstance(entry, dict) else None
        named = str(address) if filled(address) else ""
        # ! NEVER EMPTY, which is what lets `commands/collate.py` keep
        # `(the copy)` for findings that really are about the whole document.
        where = named or f"{path} mark {n}"
        if isinstance(entry, dict) and untouched(entry):
            if named:
                unruled.append(named)
            else:
                refused.append(Refused("", where, (NO_PLACE,)))
            continue
        mark, why = read_mark(where, entry)
        if mark is None:
            # ! THE LOCATOR IS A FIELD, SO IT IS NOT ALSO A PREFIX -- T3 of
            # `collate-command-defects`. `where` went IN to name the mark in
            # each message; `Refused.where` carries it now, so the sentence
            # does not repeat it.
            refused.append(
                Refused(named, where, tuple(without_location(where, m) for m in why))
            )
        else:
            ruled.append(mark)
    return ruled, unruled, refused


@dataclass(frozen=True)
class Sheet:
    """One page's RULINGS, inside the `edit_copy` that seeded them.

    !! IT HOLDS WHAT PARSED, AND WAS `tuple[object, ...]` UNTIL `P51`. Roy,
    2026-09-01: *"we clearly need sheet to take Marks not Objects."* A returned
    sheet's entries come back in three kinds and only one is a mark -- the other
    two leave as `unruled` and `refused`, which is `Process: #72`'s shape.

    !! SO `deserialize` IS NOT `serialize`'s INVERSE FOR A SHEET THAT HOLDS
    EITHER, and that is deliberate rather than a gap. What a role hands back has
    an entry per place; what this holds is the rulings. The two other kinds are
    not thrown away -- they are the whole subject of `flows/mark_errors.py`, and
    they are addresses and reasons rather than places, so nothing can put them
    back. ! The inverse DOES hold for a sheet whose every entry ruled, which is
    what `tests/test_containers.py` round-trips.

    Attributes:
        path: the page's real repo path, as the binder stated it.
        sha: that page's sha when it was gathered. Read by
            `flows.revise.docket_of`, which writes it onto the docket page so
            the setter can refuse a page that moved underneath the run.
        marks: one `Mark` per place a role RULED on, in the order they came
            back.
        unruled: the address of every place handed to the role and left
            untouched -- `desk.proof.mark.untouched`. A coverage gap, not an error.
        refused: one `Refused` per entry that is neither untouched nor
            parseable. ! IT IS NOT FATAL TO THE SHEET, and that is what keeps
            one role's bad mark from blocking the stage: the fold
            returns early on an envelope failure, so refusing here would stop
            three roles over one. Roy, 2026-08-30: *"the errors should be
            stacked and capable of being read off correctly so that each can be
            fixed or sent back to the role."*
    """

    path: str
    sha: str
    marks: tuple[Mark, ...]
    #: ! OFF THE WIRE. Both are what the parse MADE of entries that are not
    #: marks, so no producer writes them and `_written` must not demand them.
    unruled: tuple[str, ...] = field(default=(), metadata={"wire": False})
    refused: tuple[Refused, ...] = field(default=(), metadata={"wire": False})

    @classmethod
    def seed(cls, path: str, sha: object, marks: list) -> dict:
        """One sheet as the wire dict every producer writes.

        !! `sha` IS NORMALIZED HERE, AND THIS IS THE ONE PLACE THAT DOES IT.
        `.get("sha", "")` defaults only when the key is ABSENT, so a `"sha":
        null` binder page arrives with the key PRESENT and holding None, and
        `str(None)` is the four-character word "None". `flows.distribute.seed`
        and `Sheet.deserialize` each carried this fold; a rule stated twice is a rule
        that will disagree with itself.

        Args:
            path: the page's real repo path, as the binder stated it.
            sha: that page's sha, or anything that is not a `str` -- an absent
                or null sha becomes "".
            marks: the entries for this page, carried as given.

        Returns:
            `{path, sha, marks}` -- what `Sheet.deserialize` reads back.
        """
        return _written(
            cls,
            {
                "path": path,
                "sha": sha if isinstance(sha, str) else "",
                "marks": list(marks),
            },
        )

    @classmethod
    def deserialize(cls, where: str, data: object) -> "tuple[Sheet | None, list[str]]":
        """One sheet, checked.

        Args:
            where: how to name this sheet in a message.
            data: one entry of an edit_copy's `sheets`, as it came back.

        Returns:
            `(Sheet, [])` or `(None, [messages])`. An absent OR a null `sha` is
            admitted as "".

            !! THE REASON GIVEN HERE WAS FALSE UNTIL 2026-08-31. It read *"a page
            can be gathered from a tree that is not a repo"*. `machine.repo.sha_of`
            digests the TEXT with the standard library and asks nothing of git, so
            a gather over a directory holding no `.git` reports a real sha for every
            page. Roy, 2026-08-31: *"this is not a valid reason to not sha hash the
            file ... we are not using the git sha for this we are using the python
            hashing library."*

            ! THE REAL PRODUCERS ARE TWO SITES INSIDE THE MIDDLE, and both write
            `""` for a path `unflatten` could not resolve back to a real page:
            `flows.places.chief_copy_of` and, until `P55`,
            `desk.collator._real_pages`. Neither is a gather, and neither is
            about a repo.

            ! SO WHETHER AN ABSENT KEY SHOULD BE ADMITTED AT ALL IS OPEN -- no real
            producer writes a sheet without one, and `containers-and-verification-
            are-unwired` T9 holds that question. What is fixed here is the
            justification, which was not true of this code on any day.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: a sheet must be an object"]
        path = data.get("path")
        if not filled(path):
            return None, [f"{where}: a sheet needs the `path` of the page it holds"]
        marks = data.get("marks")
        if not isinstance(marks, list):
            return None, [f"{where}: {path} needs a `marks` list"]
        # ! `.get("sha", "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT. A `"sha":
        # null` reaching here is a PRESENT key holding None, so `.get` returns
        # None and `str(None)` is the four-character word "None" -- folded into
        # the same absent-sha case above instead.
        #
        # ! `Sheet.seed` FOLDS ON THE WAY OUT AND THIS ON THE WAY IN, so a sheet
        # written by hand -- an artifact read off disk, a role's own edit -- meets
        # the same rule as one this module wrote.
        #
        # !! AND THE FOLD WAS SPELLED AT FIVE SITES. `flows.carry` and
        # `flows.places.chief_copy_of` each carry their own copy, and neither
        # imports this module; a third, `desk.collator._real_pages`, went with
        # `docket_from` at `P55`. `carry`'s own comment already
        # says it is "matching `desk.proof.sheet.Sheet.deserialize`". This pair is the
        # round trip; those three are duplicates a change to the rule would not
        # reach.
        #
        # ! THE COUNT WAS FOUR UNTIL 2026-08-31 AND THE FIFTH WAS ADDED KNOWINGLY.
        # the chief's copy subscripted `sheet["sha"]` on the belief that the envelope
        # guaranteed it; it does not, and `823834f` restored the fold there rather
        # than carry the parsed `Sheet` that already holds the answer. That is a
        # stopgap standing until `Process: #65`, and counting it here is what keeps
        # it from reading as the settled shape.
        raw_sha = data.get("sha")
        sha = raw_sha if isinstance(raw_sha, str) else ""
        ruled, unruled, refused = _sorted_entries(path, marks)
        return (
            Sheet(
                path=path,
                sha=sha,
                marks=tuple(ruled),
                unruled=tuple(unruled),
                refused=tuple(refused),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This sheet as the wire dict, the shape `seed` writes.

        !! IT WRITES THE RULINGS, AND IS NOT `deserialize`'s INVERSE FOR A SHEET
        HOLDING `unruled` OR `refused` -- see the class docstring. Those two are
        addresses and reasons rather than places, so there is nothing to write
        back; `flows/mark_errors.py` is where they go instead.

        ! THE THREE WIRE KEYS ARE THE THREE `seed` WRITES. `unruled` and
        `refused` are off the wire, which `_wire_fields` states once.
        """
        return {
            "path": self.path,
            "sha": self.sha,
            "marks": [mark.serialize() for mark in self.marks],
        }
