"""What a BINDER is on disk, and how one is read back.

A binder is the artifact the gatherer hands over -- a folder of pages, each
naming its file, with the rows an agent rules on -- a 3-ring binder full of
stuff, the object and not the trade; `docs/vocabulary.md`, *binder*.

!! ONE MODULE OWNS BOTH DIRECTIONS, and the reason is what happened without it.
MEASURED 2026-08-24: the gather wrote a bare list and FOUR commands each decided
for themselves what a binder file is --

    addresser   loaded.get("paragraphs", []) if isinstance(loaded, dict) else loaded
    galley      binder["paragraphs"] if isinstance(binder, dict) else binder
    record      loaded["paragraphs"] if isinstance(loaded, dict) else loaded
    collator    json.loads(binder_text)          -- no envelope handling at all

Three spellings of one guess and one absence. They already disagreed: the first
tolerates a missing key, the next two raise `KeyError`, and the last would
iterate a dict's KEYS. ! All three guesses anticipated an envelope NOTHING
PRODUCED -- so the format lived in five places, none of which could be checked
against the others.

! THE FORMAT IS A CONTRACT AND BELONGS TO NEITHER END. That is the answer to the
locality question: scattering it across the consumers is what broke locality,
and one module both sides import is the fix rather than the compromise. Roy:
*"we should have a module that does the serialization/deserialization work not
just let each parse its own."*

Each page writes itself, its path and sha included -- see `Page.serialize`.
What stands here is the envelope: the version, the header, the list of pages,
the freeform paths.
"""

from dataclasses import dataclass
from pathlib import Path

from comment_review.binder.page import Page, RedactedPage
from comment_review.reading.paragraph import Paragraph

# The shape's own version, so a reader can say which format it refused rather
# than only that it could not read one.
#
# `Binder.deserialize` refuses on it: a binder whose `version` is not `VERSION`
# is refused by name, and one at version "2" is told it carries no saved
# reading context.
VERSION = "4"


def bind(
    pages: list[Page],
    read_from: dict,
    absent: bool = False,
    freeform: tuple[str, ...] = (),
) -> "Binder":
    """Every page in scope, as the binder that is handed over.

    !! `read_from` IS REQUIRED, NOT DEFAULTED. A binder that cannot say which
    root it was gathered from is exactly the ambiguity a later stage needs
    resolved: a revise re-binds from a tree copy, and a role holding that
    binder cannot tell it apart from the original unless the binder says so.
    A caller with no root to name has nothing it was gathered FROM, so there
    is no default that would not be a fabrication.

    ! THE SHA IS REPORTED, NOT TAKEN. It arrives on the page from
    `repo.read_source`; this module hashes nothing. Roy, 2026-08-25: *"It is
    information received by page and binder, not something requested by
    page/binder."*

    !! AN ABSENT PLACE IS NOT SENT UNLESS IT IS ASKED FOR. Roy, 2026-08-25:
    *"The absent kinds are not supposed to be sent to the agents unless
    specifically asked for."* MEASURED over this repo's own source before the
    cut: **5,201 of 5,685 rows -- 91% -- held no prose.** 2,692 `margin` and
    2,437 `interval`, which is roughly one empty place per line of code, against
    2 `undocumented` in the whole tree. 850KB, and four roles read it.

    Args:
        pages: the pages in scope.
        read_from: `{"root": "<path>", "revise": <int>}` -- the root this
            binder was gathered from, and `0` for the original or the
            revise's own number otherwise.
        absent: carry the empty places too. For the callers that specifically
            ask: `gather --include-absent`, for a reviewer surveying where
            prose could go, and `flows.revise`'s address gate, which must see
            a new `undocumented` declaration.
        freeform: repo-relative posix paths of the files in scope that no
            reader claims. They have no page; the binder only names them.

    Raises:
        ValueError: `read_from` is not `{"root": str, "revise": int}`.

    The shape of `read_from` is checked here and on the way back in, by
    `_read_from_problem`.

    And it is copied, not aliased. The stored dict was the caller's own until
    2026-08-28, so a binder, every `edit_copy` seeded from it, and whatever the
    caller kept were one object -- a test writing `binder["read_from"]["revise"]
    = 1`, which is how a revise test is naturally written, would have changed
    what every later test in the session saw, with no gate able to attribute it.
    """
    why = _read_from_problem({"read_from": read_from})
    if why:
        raise ValueError(why)
    # !! `absent` CHOOSES THE PAGE TYPE, IT DOES NOT FILTER A ROW LIST --
    # `decision-log.md Process: #68`. A `Page` serializes every addressed place;
    # a `RedactedPage` serializes the ones holding prose. The cut is the page's
    # own, at the one moment it knows what it is being asked for.
    return Binder(
        version=VERSION,
        read_from={**read_from},
        pages=tuple(page if absent else RedactedPage.of(page) for page in pages),
        freeform=tuple(freeform),
    )


def _read_from_problem(loaded: dict) -> str:
    """Why a `read_from` cannot be used, or `""`: a binder's, an edit copy's, a proof's.

    MEASURED 2026-08-28, and it is why the check moved here from `seed` alone:
    `distribute --seed` over a version-"1" binder exited 1 with `KeyError:
    'read_from'` and an eight-frame traceback on stderr and nothing on stdout,
    past `main`'s own promise of *"2 when an input could not be read"*.
    `commands/distribute.py:122` calls `seed` immediately after `load_binder`
    returns a binder, and `Binder.deserialize` runs this function first, so a
    field `seed` requires could only surface as a crash. Raising is not
    refusing: a refusal in this module is a named reason, which a command turns
    into an exit code, which is what a reader can act on.

    ! AND THE SHAPE IS CHECKED, NOT ONLY THE PRESENCE. MEASURED the same day:
    `read_from="oops"`, `None`, `[]` and `{"root": 7}` each built a binder, each
    passed `ty`, and `seed` copied the value verbatim onto the `edit_copy`
    handed to an editorial role.
    """
    if "read_from" not in loaded:
        return (
            "carries no `read_from` -- a binder written before 2026-08-28 "
            f'(version "1"); re-run `gather` to get a version "{VERSION}" one'
        )
    read_from = loaded["read_from"]
    if not isinstance(read_from, dict):
        kind = type(read_from).__name__
        return f"`read_from` is a JSON {kind}, not a mapping of `root` and `revise`"
    if not isinstance(read_from.get("root"), str):
        return "`read_from` carries no `root` string -- which tree was gathered?"
    if not isinstance(read_from.get("revise"), int):
        return "`read_from` carries no `revise` number -- 0 is the original"
    return ""


def _not_a(where: str, noun: str, value: object) -> str:
    """One refusal, naming the JSON type that arrived instead of `noun`."""
    return f"{where}: a JSON {type(value).__name__}, not {noun}"


@dataclass(frozen=True)
class Binder:
    """Every page in scope, as the artifact the gatherer hands over.

    Attributes:
        version: the format's own number -- `VERSION` for one this tree wrote.
        read_from: `{"root": str, "revise": int}` -- which tree was gathered.
        pages: one per file in scope, in the order they were bound.
        freeform: sorted repo-relative posix paths of files in scope that no
            reader claims; they have no page.

    !! THE LOAD IS NOT HERE, ruled `decision-log.md Process: #67`. Roy,
    2026-08-31: *"all flows start with a load step - not the modules code."*
    `deserialize` takes what the load PRODUCED -- an already-decoded dict --
    so this module holds no `json.loads` and reaches no path. What a binder IS
    stays here; turning bytes into an object belongs to the end that owns one.

    ! `machine.json_object.object_of` IS THAT LOAD and did not go anywhere: it
    is called in `flows.proof_io`, whose `load_binder` calls it and then this;
    five commands call `load_binder`.
    """

    version: str
    read_from: dict
    pages: tuple[Page | RedactedPage, ...]
    freeform: tuple[str, ...]

    @property
    def root(self) -> Path:
        """The tree this binder was gathered from, as a path.

        `read_from["root"]` is what `_read_from_problem` requires of every
        binder, so a `Binder` always has one -- which is why the commands ask
        the container rather than re-deriving a fallback for a case `bind` and
        `deserialize` already refuse.
        """
        return Path(self.read_from["root"])

    @classmethod
    def deserialize(cls, where: str, data: object) -> "tuple[Binder | None, list[str]]":
        """A binder read back, or every rule it breaks.

        Args:
            where: how to name this binder in a message.
            data: the decoded object, as `machine.json_object.object_of`
                returns one. NEVER text and never a path.

        Returns:
            `(Binder, [])` or `(None, [messages])`.

        !! IT REFUSES RATHER THAN COPING. Every one of the four readers this
        replaced guessed at the shape, and a guess that is wrong reads as an
        EMPTY binder -- which downstream is indistinguishable from a run with
        nothing to do. The collator was measured certifying exactly that on
        2026-08-20.

        It rules on every field it carries. A `Binder` promises its fields to
        everything downstream, so a page with no `path` and a place with no
        `cue` are refused by name here rather than folded to `""` by
        whichever consumer met them first.

        !! EVERYTHING READ BACK IS A `RedactedPage`, whichever kind was written --
        `decision-log.md Process: #68`. Neither page type serializes its source
        text, so a binder off disk cannot rebuild a `Page`, and claiming it
        could is the lie a redaction exists to prevent.
        """
        if not isinstance(data, dict):
            return None, [_not_a(where, "a binder", data)]
        # !! DECLARED, NOT NARROWED, because the read at `checked["read_from"]`
        # below sits past a loop. An `isinstance` narrow is invalidated at a
        # loop back-edge, so `ty` loses it before that read; an explicit
        # annotation is a declaration and survives. Same reason, same spelling
        # as `desk.proof.edit_copy.EditCopy.deserialize`.
        checked: dict = data
        if checked.get("version") == "2":
            return None, [
                f"{where}: binder version '2' carries no saved reading context; "
                f'regather to save a version "{VERSION}" binder'
            ]
        if "pages" not in checked:
            return None, [
                f"{where}: carries no `pages` -- is this the output of `gather`?"
            ]
        raw_pages = checked["pages"]
        if not isinstance(raw_pages, list):
            return None, [_not_a(f"{where}: `pages`", "a list of pages", raw_pages)]
        pages: list[Page | RedactedPage] = []
        problems: list[str] = []
        for n, raw in enumerate(raw_pages):
            page, why = RedactedPage.deserialize(f"{where}: page {n}", raw)
            if page is None:
                problems += why
            else:
                pages.append(page)
        if problems:
            return None, problems
        # After the `pages` checks, and that order is load-bearing.
        # Put first, it answered every malformed-`pages` artifact with "carries
        # no `read_from`" -- true, and not the reason the file is unreadable.
        # `pages` is what a binder IS; the header says which tree it came from.
        why_header = _read_from_problem(checked)
        if why_header:
            return None, [f"{where}: {why_header}"]
        raw_version = checked.get("version")
        if raw_version != VERSION:
            return None, [
                f"{where}: unsupported binder version {raw_version!r}; "
                f'regather to save a version "{VERSION}" binder with reading context'
            ]
        raw_freeform = checked.get("freeform")
        if not isinstance(raw_freeform, list) or not all(
            isinstance(path, str) for path in raw_freeform
        ):
            return None, [
                f"{where}: `freeform` is not a list of path strings; "
                f'regather to save a version "{VERSION}" binder'
            ]
        return (
            cls(
                version=raw_version if isinstance(raw_version, str) else "",
                # ! COPIED, NOT ALIASED -- `bind` and `seed` both do the same
                # with this field, so a caller mutating its own dict cannot
                # change what a deserialized binder already holds.
                read_from={**checked["read_from"]},
                pages=tuple(pages),
                freeform=tuple(raw_freeform),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This binder as a wire dict; `gather`, `distribute` and `carry` write it."""
        return {
            "version": self.version,
            "read_from": {**self.read_from},
            "pages": [page.serialize() for page in self.pages],
            "freeform": list(self.freeform),
        }

    @property
    def paragraphs(self) -> list[Paragraph]:
        """Every ADDRESSED paragraph on every page, in the binder's own order.

        !! A FENCE IS NEVER CARRIED, ASKED FOR OR NOT -- `bind`'s own rule, and
        this is where it now holds. It names no place, so there is nothing to
        cite and nothing to rule on. ! `bind` used to apply it while building a
        row list; a `Page` holds every paragraph it read, fences included, so
        the rule moved to the two places that hand places out: here, and
        `Page.serialize`. **They filter alike, so what a binder carries in
        memory and what it writes are the same set.**
        """
        return [b for page in self.pages for b in page.paragraphs if b.address]
