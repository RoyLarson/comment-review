"""One page's rulings inside an edit_copy, and the parse that sorts its entries.

The module's names:

    Sheet             one page's marks, with that page's path and sha
    Refused           one entry the parse could not read as a mark, and why
    NO_PLACE          the refusal for an untouched entry naming no place
"""

from copy import deepcopy
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
from comment_review.reading.context import ReadingContext
from comment_review.reading.context_io import context_from_wire, context_to_wire


class Refused(NamedTuple):
    """One entry the parse could not read as a mark, and why.

    ! Address and reasons, never the entry. The role still holds the copy this
    came out of; what it needs is where and what, not the place back.

    Attributes:
        address: the entry's own `address`, or "" where it carried none -- an
            entry that is not an object, or one whose `address` is not a string.
            ! It is what routes, and "" means there is nothing to route on.
            Nothing may print it; `where` is for that.
        where: how to point at the entry, never empty -- the address where there
            is one, else the page and the entry's position on it, as
            `m.py mark 3`.

            !! It is the only handle on an address-less entry.
        reasons: every rule the entry broke, as `read_mark` worded them --
            the structural read's, or the validator's it was handed.
            ! All of them, not the first -- one malformed `correct` breaks four,
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

    !! The one place a returned sheet's entries are sorted into these kinds.
    `read_mark` has two other callers, `flows.fill.marks_on` and
    `flows.fill.fill`, which read a copy's wire entries themselves.

    Args:
        path: the page this sheet holds, for the locator below. ! It is taken
            rather than derived because an address-less entry has no other way
            to say which page it sits on.
        marks: the sheet's `marks` list, as it came back. Entries are whatever
            JSON held -- an object, a string, a number.

    Returns:
        `(ruled, unruled, refused)`.

        ruled: one `Mark` per entry that parsed.
        unruled: the address of every untouched entry --
            `desk.proof.mark.untouched`, a place nobody wrote in. ! It is asked
            first, because an untouched entry does not parse either: `read_mark`
            refuses its `instruction: None` with *"must be one of add, clean,
            ..."*, which would report a coverage gap as a malformed mark.
        refused: one `Refused` per entry that is neither.

    !! An untouched entry naming no place is refused, not unruled, and that is a
    ruling rather than a convenience. *"Handed to this role and not ruled on"*
    is a claim about a place, so an entry that names none cannot be it -- and
    `flows.verify.admitted_coverage_problems` reads `unruled` as addresses, so
    an "" among them would count a place the binder never held.
    `flows.distribute.seed` writes the address on every slot it hands out, so an
    entry reaching here without one was edited after it was seeded, which is a
    role's mistake and routes back as one.

    ! An entry that is not an object is refused, not dropped. A bare string is
    named here, where the entry is read, rather than left to vanish.
    """
    ruled: list[Mark] = []
    unruled: list[str] = []
    refused: list[Refused] = []
    for n, entry in enumerate(marks, 1):
        address = entry.get("address") if isinstance(entry, dict) else None
        named = str(address) if filled(address) else ""
        # ! Never empty, which is what lets `commands/check.py` and
        # `commands/report.py` keep `(the copy)` for findings that really are
        # about the whole document.
        where = named or f"{path} mark {n}"
        if isinstance(entry, dict) and untouched(entry):
            if named:
                unruled.append(named)
            else:
                refused.append(Refused("", where, (NO_PLACE,)))
            continue
        mark, why = read_mark(where, entry)
        if mark is None:
            # ! The locator is a field, so it is not also a prefix.
            # `Refused.where` carries `where`, so no message repeats it.
            refused.append(
                Refused(named, where, tuple(without_location(where, m) for m in why))
            )
        else:
            ruled.append(mark)
    return ruled, unruled, refused


@dataclass(frozen=True)
class Sheet:
    """One page's rulings, inside the `edit_copy` that seeded them.

    !! It holds what parsed. A returned sheet's entries come back in three kinds
    and only one is a mark -- the other two leave as `unruled` and `refused`.

    !! So `deserialize` is not `serialize`'s inverse for a sheet that holds
    either, and that is deliberate rather than a gap. What a role hands back has
    an entry per place; what this holds is the rulings. The two other kinds are
    not thrown away -- they are the whole subject of `flows/mark_errors.py`, and
    they are addresses and reasons rather than places, so nothing can put them
    back. ! The inverse does hold for a sheet whose every entry ruled, which is
    what `tests/test_containers.py` round-trips.

    Attributes:
        path: the page's real repo path, as the binder stated it.
        sha: that page's sha when it was gathered. Read by
            `flows.transcribe.docket_of`, which writes it onto the docket page so
            the setter can refuse a page that moved underneath the run.
        reading: the page's saved language identity and effective settings.
        marks: one `Mark` per place a role ruled on, in the order they came
            back.
        unruled: the address of every place handed to the role and left
            untouched -- `desk.proof.mark.untouched`. A coverage gap, not an error.
        refused: one `Refused` per entry that is neither untouched nor
            parseable. ! It is not fatal to the sheet, and that is what keeps
            one role's bad mark from blocking the stage: the fold
            returns early on an envelope failure, so refusing here would stop
            three roles over one.
    """

    path: str
    sha: str
    marks: tuple[Mark, ...]
    reading: ReadingContext
    #: ! OFF THE WIRE. Both are what the parse MADE of entries that are not
    #: marks, so no producer writes them and `_written` must not demand them.
    unruled: tuple[str, ...] = field(default=(), metadata={"wire": False})
    refused: tuple[Refused, ...] = field(default=(), metadata={"wire": False})

    @classmethod
    def seed(
        cls, path: str, sha: object, marks: list, *, reading: ReadingContext
    ) -> dict:
        """One sheet as the wire dict every producer writes.

        !! `sha` is normalized here, as `deserialize` does on the way in and
        `binder.page` does for a binder page. `.get("sha", "")` defaults only
        when the key is absent, so a `"sha": null` binder page arrives with the
        key present and holding None, and `str(None)` is the four-character
        word "None".

        Args:
            path: the page's real repo path, as the binder stated it.
            sha: that page's sha, or anything that is not a `str` -- an absent
                or null sha becomes "".
            marks: the entries for this page, carried as given.
            reading: the context retained by the supplying page or sheet.

        Returns:
            `{path, sha, marks, reading}` -- what `Sheet.deserialize` reads back.
        """
        return _written(
            cls,
            {
                "path": path,
                "sha": sha if isinstance(sha, str) else "",
                "marks": deepcopy(marks),
                "reading": context_to_wire(reading),
            },
        )

    @classmethod
    def deserialize(cls, where: str, data: object) -> "tuple[Sheet | None, list[str]]":
        """One sheet, checked.

        Args:
            where: how to name this sheet in a message.
            data: one entry of an edit_copy's `sheets`, as it came back.

        Returns:
            `(Sheet, [])` or `(None, [messages])`. A `sha` that is absent, null
            or not a string is admitted as "".

            ! No real producer writes a sheet without a `sha`, and whether an
            absent one should be admitted at all is not settled.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: a sheet must be an object"]
        path = data.get("path")
        if not filled(path):
            return None, [f"{where}: a sheet needs the `path` of the page it holds"]
        marks = data.get("marks")
        if not isinstance(marks, list):
            return None, [f"{where}: {path} needs a `marks` list"]
        reading, why = context_from_wire(where, data.get("reading"))
        if reading is None:
            return None, why
        # ! `.get("sha", "")` DEFAULTS ONLY WHEN THE KEY IS ABSENT. A `"sha":
        # null` reaching here is a PRESENT key holding None, so `.get` returns
        # None and `str(None)` is the four-character word "None" -- folded into
        # the same absent-sha case above instead.
        #
        # ! `Sheet.seed` FOLDS ON THE WAY OUT AND THIS ON THE WAY IN, so a sheet
        # written by hand -- an artifact read off disk, a role's own edit -- meets
        # the same rule as one this module wrote.
        raw_sha = data.get("sha")
        sha = raw_sha if isinstance(raw_sha, str) else ""
        ruled, unruled, refused = _sorted_entries(path, deepcopy(marks))
        return (
            Sheet(
                path=path,
                sha=sha,
                marks=tuple(ruled),
                reading=reading,
                unruled=tuple(unruled),
                refused=tuple(refused),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This sheet as the wire dict, the shape `seed` writes.

        !! It writes the rulings, and is not `deserialize`'s inverse for a sheet
        holding `unruled` or `refused` -- see the class docstring.

        The wire keys are the fields `seed` writes.
        """
        return {
            "path": self.path,
            "sha": self.sha,
            "marks": deepcopy([mark.serialize() for mark in self.marks]),
            "reading": context_to_wire(self.reading),
        }
