"""What a binder is on disk, and how one is read back.

A binder is the artifact the gatherer hands over -- a folder of pages, each
naming its file, with the rows an agent rules on -- a 3-ring binder full of
stuff, the object and not the trade; `docs/vocabulary.md`, *binder*.

!! One module owns both directions: the format is a contract and belongs to
neither end. Scattered across its consumers, each would decide for itself what
a binder file is; one module both sides import states it once.

Each page writes itself, its path and sha included -- see `Page.serialize`.
What stands here is the envelope: the version, the header, the list of pages,
the freeform paths.

`known_addresses` turns a binder into the set of addresses its rows carry;
the address gate in `flows.revise` compares that set before and after a pull.
"""

from dataclasses import dataclass
from pathlib import Path

from comment_review.binder.page import Page, RedactedPage
from comment_review.read_from import BINDER_VERSION as VERSION
from comment_review.read_from import read_from_problem
from comment_review.reading.paragraph import Paragraph


def bind(
    pages: list[Page],
    read_from: dict,
    absent: bool = False,
    freeform: tuple[str, ...] = (),
) -> "Binder":
    """Every page in scope, as the binder that is handed over.

    !! `read_from` is required, not defaulted. A binder that cannot say which
    root it was gathered from is exactly the ambiguity a later stage needs
    resolved: a stage tree re-binds from a tree copy, and a role holding that
    binder cannot tell it apart from the checkout unless the binder says so.
    A caller with no root to name has nothing it was gathered from, so there
    is no default that would not be a fabrication.

    ! The sha is reported, not taken. It arrives on the page from
    `repo.read_source`; this module hashes nothing.

    !! An absent place is not sent unless it is asked for.

    Args:
        pages: the pages in scope.
        read_from: `{"root": "<path>"}` -- the root this binder was
            gathered from -- and `"stage"`, the stage `stage open` built
            that root for.
        absent: carry the empty places too. For the callers that specifically
            ask: `gather --include-absent`, for a reviewer surveying where
            prose could go, and `flows.revise`'s address gate, which must see
            a new `undocumented` declaration.
        freeform: repo-relative posix paths of the files in scope that no
            reader claims. They have no page; the binder only names them.
            `bind` keeps them in the order given, and `Binder.freeform`
            promises them sorted, so the caller sorts -- `flows.gather` does.

    Raises:
        ValueError: `read_from` is not `{"root": str}`, with an optional
            `"stage": str`.

    The shape of `read_from` is checked here and on the way back in, by
    `read_from_problem`.

    And it is copied, not aliased. Aliased, a binder, every `edit_copy` seeded
    from it, and whatever the caller kept would be one object -- a test writing
    `binder["read_from"]["root"] = "elsewhere"` would change what every later
    test in the session saw, with no gate able to attribute it.
    """
    why = read_from_problem({"read_from": read_from})
    if why:
        raise ValueError(why)
    # !! `absent` chooses the page type, it does not filter a row list. A `Page`
    # serializes every addressed place; a `RedactedPage` serializes the ones
    # holding prose. The cut is the page's own, at the one moment it knows what
    # it is being asked for.
    return Binder(
        version=VERSION,
        read_from={**read_from},
        pages=tuple(page if absent else RedactedPage.of(page) for page in pages),
        freeform=tuple(freeform),
    )


def _not_a(where: str, noun: str, value: object) -> str:
    """One refusal, naming the JSON type that arrived instead of `noun`."""
    return f"{where}: a JSON {type(value).__name__}, not {noun}"


@dataclass(frozen=True)
class Binder:
    """Every page in scope, as the artifact the gatherer hands over.

    Attributes:
        version: the format's own number -- `VERSION` for one this tree wrote.
        read_from: `{"root": str}` and an optional `"stage": str` -- which
            tree was gathered, and for which stage.
        pages: one per file in scope, in the order they were bound.
        freeform: sorted repo-relative posix paths of files in scope that no
            reader claims; they have no page.
    """

    version: str
    read_from: dict
    pages: tuple[Page | RedactedPage, ...]
    freeform: tuple[str, ...]

    @property
    def root(self) -> Path:
        """The tree this binder was gathered from, as a path.

        `read_from["root"]` is what `read_from_problem` requires of every
        binder, so a `Binder` always has one -- which is why the commands ask
        the container rather than re-deriving a fallback for a case `bind` and
        `deserialize` already refuse.
        """
        return Path(self.read_from["root"])

    @classmethod
    def deserialize(cls, where: str, data: object) -> "tuple[Binder | None, list[str]]":
        """A binder read back, or every rule it breaks.

        !! The load is not here. `deserialize` takes what the load produced --
        an already-decoded dict -- so this module holds no `json.loads` and
        reaches no path. What a binder is stays here; turning bytes into an
        object belongs to the end that owns one.

        ! `machine.json_object.object_of` is that load: it is called in
        `flows.proof_io`, whose `load_binder` calls it through `_object` and
        then this; five commands call `load_binder`.

        Args:
            where: how to name this binder in a message.
            data: the decoded object, as `machine.json_object.object_of`
                returns one. Never text and never a path.

        Returns:
            `(Binder, [])` or `(None, [messages])`.

        !! It refuses rather than coping. A guess at the shape that is wrong reads
        as an empty binder -- which downstream is indistinguishable from a run
        with nothing to do.

        It rules on every field it carries. A `Binder` promises its fields to
        everything downstream, so a page with no `path` and a place with no
        `cue` are refused by name here rather than folded to `""` by
        whichever consumer met them first.

        !! Everything read back is a `RedactedPage`, whichever kind was written.
        Neither page type serializes its source text, so a binder off disk
        cannot rebuild a `Page`, and claiming it could is the lie a redaction
        exists to prevent.
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
        why_header = read_from_problem(checked)
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
        """This binder as a wire dict; `gather` and `stage open` write it."""
        return {
            "version": self.version,
            "read_from": {**self.read_from},
            "pages": [page.serialize() for page in self.pages],
            "freeform": list(self.freeform),
        }

    @property
    def paragraphs(self) -> list[Paragraph]:
        """Every ADDRESSED paragraph on every page, in the binder's own order.

        !! A fence is never carried, asked for or not -- `bind`'s own rule, and
        this is where it holds. It names no place, so there is nothing to cite
        and nothing to rule on. A `Page` holds every paragraph it read, fences
        included, so the rule holds at the two places that hand places out: here,
        and `Page.serialize`. **They filter alike, so what a binder carries in
        memory and what it writes are the same set.**
        """
        return [b for page in self.pages for b in page.paragraphs if b.address]


def known_addresses(binder: Binder) -> frozenset[str]:
    """Every address the binder's rows carry, as a set to test membership on.

    Args:
        binder: a binder, as `bind` or `Binder.deserialize` returns one. Each
            row already knows its own path and address -- a page rejoins them
            when it is read back.

    Returns:
        The addresses. A row carrying an empty one is dropped.
    """
    return frozenset(b.address for b in binder.paragraphs if b.address)
