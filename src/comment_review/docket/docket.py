"""The docket: every alteration the write chain is asked to make.

    {"pages": [
        {"path": "pkg/a/util.py",
         "sha":  "e3b0c44298fc",
         "role":  "block-context",
         "reading": {"format": 1, "language": "python",
                     "reader": "python-lexical", "settings": {},
                     "compatibility": "<the reader's 64-hex digest>"},
         "alterations": [{"cue": "b1", "text": "# the new comment"},
                         {"cue": "c0", "text": null}]}]}

!! It is the write side's binder, and its three levels mirror the binder's:
paragraph, page, binder.

    level       read                    write
    one place   a Paragraph             an alteration -- a cue, its text, its anchor
    one file    a Page / RedactedPage   a schedule: path, sha, alterations
    the whole   a Binder                a docket: its schedules

!! All six are types. The write side's three answer `deserialize` over an
already-loaded dict and `serialize` back to one. On the read side `Binder` and
`RedactedPage` do both, `Page` only serializes and `Paragraph` does neither.

!! The load is the command's, `commands/proof.py`, and that makes three
failures separable.

    step           fails on                                        owned by
    read_text      the file is missing, unreadable, undecodable    the command
    object_of      the text is not JSON, or not an object          the command
    deserialize    it is an object, and not a docket               the container

! A docket in print production is the instruction paperwork that travels with a
job, which is what this is: what the desk hands the chain that sets type.

!! The nesting is not tidiness -- it removes two couplings. A flat docket, one
map from address to text, would have to derive the per-page grouping by
splitting every address, and the path an address carries is flattened
(`pkg:a:util.py`), so something else would have to turn it back.

    flat    address -> text     grouping derived; path flattened; sha from the binder
    nested  pages -> schedule   grouping structural; path real; sha on the page

!! So the gathered binder does not reach the write chain; `flows.revise` binds
the pages it pulled only for its address gate. The docket carries the sha and
the real path, the two facts of the binder the write chain reads.

!! The sha is recorded, never recomputed. The file may change between the
gather and the write, so the sha is read from the docket. A sha taken from the
file at write time would ask whether the file equals itself, which cannot fail.
"""

from dataclasses import dataclass, field

from comment_review import constants
from comment_review.reading.context import ReadingContext
from comment_review.reading.context_io import context_from_wire, context_to_wire


def _not_a(where: str, noun: str, value: object) -> str:
    """One refusal, naming the JSON type that arrived instead of `noun`."""
    return f"{where}: a JSON {type(value).__name__}, not {noun}"


@dataclass(frozen=True)
class Alteration:
    """One place, and what the chain is to set there.

    Attributes:
        cue: the place on the page -- `b1`, `c0`.
        text: the replacement, or None to delete.
        anchor: the page's anchor at this place, as the docket's writer took
            it -- `flows.transcribe.docket_of` takes a mark's own, and the
            page's at a move's destination -- or None where a docket carries
            none. The write end refuses one that is not the page's anchor
            here, and refuses None.

    !! `None` is the delete and an empty patch is refused. Were `""` the
    delete, a key whose value failed to serialise would arrive looking exactly
    like a deliberate deletion. Two spellings for one act is how a bug upstream
    becomes a deletion downstream at exit 0. A replacement is measured with its
    white space removed, so `"   "` is the same empty patch as `""`.

    ! It is the `one place` row of the header's table.
    """

    cue: str
    text: str | None
    anchor: str | None = None

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[Alteration | None, list[str]]":
        """One alteration, checked.

        Args:
            where: how to name this alteration in a message.
            data: one entry of a page's `alterations`, as the load produced it.

        Returns:
            `(Alteration, [])` or `(None, [messages])`.
        """
        if not isinstance(data, dict):
            return None, [f"{where}: an alteration must be an object"]
        # ! Declared, not narrowed -- `ty` narrows an `object` to `Top[dict]`,
        # whose `__getitem__` takes no key, and refuses the reads below.
        checked: dict = data
        cue = checked.get("cue")
        if not isinstance(cue, str) or not cue:
            return None, [f"{where}: every alteration needs a `cue`"]
        if "text" not in checked:
            return None, [f"{where}@{cue}: an alteration needs `text` (null deletes)"]
        anchor = checked.get("anchor")
        if anchor is not None and not isinstance(anchor, str):
            return None, [
                f"{where}@{cue}: an anchor must be text or absent, not"
                f" {type(anchor).__name__}"
            ]
        text = checked["text"]
        if text is None:
            return cls(cue=cue, text=None, anchor=anchor), []
        if not isinstance(text, str):
            return None, [
                f"{where}@{cue}: a replacement must be text or null, not"
                f" {type(text).__name__}"
            ]
        if not constants.holds_text(text):
            return None, [
                f"{where}@{cue}: {constants.EMPTY_PATCH}: text with no characters"
                " is not a delete -- null is. Two spellings for one act is how a"
                " serialisation bug becomes a deletion"
            ]
        return cls(cue=cue, text=text, anchor=anchor), []

    def serialize(self) -> dict:
        """This alteration as the wire dict, with `anchor` only where it has one."""
        out: dict = {"cue": self.cue, "text": self.text}
        if self.anchor is not None:
            out["anchor"] = self.anchor
        return out


@dataclass(frozen=True)
class Schedule:
    """One page's alterations, and the page they are checked against.

    `role` is optional and, when present, one per page: the role of the
    `edit_copy` this docket was transcribed from. `flows.transcribe.docket_of`
    writes it, and `flows.revise._set_by` reads it back into `address -> role`,
    the provenance a reversal pairs against. A docket with no `role` field maps
    every one of its addresses to `""`. A role's own copy names that role on
    every schedule; the copy chief's names `copy-chief`, because the fold set
    those places.

    Attributes:
        path: as the REPO sees it -- `pkg/a/util.py`, NOT flattened. It is
            joined to the checkout and to the draft directory, so it is the one
            field a containment guard has to rule on.
        sha: of the page's text when the agents read it. `proof_setter` compares
            it against the file it is about to set.
        alterations: one `Alteration` per place, in the order the docket lists
            them.
        reading: the original context that assigned the saved cues.
        role: the role whose mark settled every alteration here, or "" when
            the docket carries none. `proof_setter` does not read this --
            `flows.revise._set_by` does; carried here so a caller unwinding a
            docket sees every field the format defines.
    """

    path: str
    sha: str
    alterations: tuple[Alteration, ...]
    reading: ReadingContext
    role: str = ""

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[Schedule | None, list[str]]":
        """One page's schedule and every alteration on it, checked.

        ! EVERY BAD ALTERATION IS REPORTED, not the first -- matching
        `binder.page.RedactedPage.deserialize` and
        `desk.proof.edit_copy.EditCopy.deserialize`.
        A schedule with two malformed alterations is two things to fix.

        Returns:
            `(Schedule, [])` or `(None, [messages])`.
        """
        if not isinstance(data, dict):
            return None, [_not_a(where, "a page", data)]
        path = data.get("path")
        if not isinstance(path, str) or not path:
            return None, [f"{where}: every page needs a `path`, as the repo names it"]
        problems: list[str] = []
        reading, why = context_from_wire(path, data.get("reading"))
        problems.extend(why)
        sha = data.get("sha")
        if not isinstance(sha, str) or not sha:
            problems.append(f"{path}: every page needs the `sha` it was read at")
        raw_role = data.get("role")
        if raw_role is not None and (not isinstance(raw_role, str) or not raw_role):
            problems.append(f"{path}: `role`, when present, must be a non-empty string")
        raw = data.get("alterations")
        if not isinstance(raw, list) or not raw:
            problems.append(f"{path}: `alterations` must be a non-empty list")
            return None, problems
        alterations: list[Alteration] = []
        # ! ONE ALTERATION PER PLACE. Two would let a later one silently win,
        # and which of them applied would depend on iteration order.
        seen: set[str] = set()
        for one in raw:
            got, why = Alteration.deserialize(path, one)
            if got is None:
                problems += why
                continue
            if got.cue in seen:
                problems.append(f"{path}@{got.cue}: two alterations for one place")
                continue
            seen.add(got.cue)
            alterations.append(got)
        if problems or reading is None:
            return None, problems
        return (
            cls(
                path=path,
                sha=sha if isinstance(sha, str) else "",
                alterations=tuple(alterations),
                reading=reading,
                role=raw_role if isinstance(raw_role, str) else "",
            ),
            [],
        )

    def serialize(self) -> dict:
        """This schedule as the wire dict.

        ! `role` is omitted when empty, so an absent field and an empty one stay
        one thing rather than two. `flows.transcribe.docket_of` writes the
        source copy's own role and an `edit_copy` always carries one, so an
        empty `role` reaches here only from a `Schedule` built directly, or from
        a docket read with no `role`. Emitting `"role": ""` would write a
        schedule `deserialize` refuses: a `role` that is present must be a
        non-empty string.
        """
        out: dict = {
            "path": self.path,
            "sha": self.sha,
            "alterations": [one.serialize() for one in self.alterations],
            "reading": context_to_wire(self.reading),
        }
        if self.role:
            out["role"] = self.role
        return out

    @property
    def edits(self) -> dict[str, str | None]:
        """Cue -> the replacement text, or None to delete.

        What `flows.proof_setter._one` consumes. It sets places by cue and never
        asks about order, so the mapping is built once here rather than by every
        caller. A repeated cue is the one thing that would make this lossy --
        the last alteration at a place would win. `deserialize` refuses one, and
        `flows.proof_setter.run` refuses a schedule built directly that holds
        one, through `repeated`, before this is read.
        """
        return {one.cue: one.text for one in self.alterations}

    @property
    def repeated(self) -> dict[str, tuple[Alteration, ...]]:
        """Each cue holding more than one alteration, with the alterations there.

        Empty for a schedule `deserialize` read, which refuses a repeated cue.
        `flows.transcribe.docket_of` builds its schedules directly, so the write
        end asks this before it sets a page.
        """
        at: dict[str, list[Alteration]] = {}
        for one in self.alterations:
            at.setdefault(one.cue, []).append(one)
        return {cue: tuple(ones) for cue, ones in at.items() if len(ones) > 1}

    @property
    def anchors(self) -> dict[str, str]:
        """Cue -> the anchor the alteration there carries, for each one with one.

        What `flows.proof_setter._one` checks against the page's own anchors.
        """
        return {
            one.cue: one.anchor for one in self.alterations if one.anchor is not None
        }


@dataclass(frozen=True)
class Docket:
    """Every alteration the write chain is asked to make.

    Attributes:
        schedules: one `Schedule` per page, in the order the docket lists them.

    !! The field is `schedules` and the wire key is `pages`, and that
    disagreement is deliberate. `Binder.pages` holds pages. A docket holds
    schedules: what to do to a page, which is not a page. Naming both `pages`
    would put two attributes of the same name on the two halves of the system
    returning different kinds of thing, and the write half's would be lying
    about what it holds.

    ! The wire keeps `pages`: a docket is written to disk by `proof --to-docket`
    and read back by `proof --from-docket`, so the key is a file format rather
    than an attribute name. `serialize` writes `pages`; `deserialize` reads it.
    """

    schedules: tuple[Schedule, ...] = field(default_factory=tuple)

    @classmethod
    def deserialize(cls, where: str, data: object) -> "tuple[Docket | None, list[str]]":
        """A docket read back, or every rule it breaks.

        Args:
            where: how to name this docket in a message.
            data: the decoded object, as `machine.json_object.object_of`
                returns one. Never text and never a path.

        Returns:
            `(Docket, [])` or `(None, [messages])`.

        !! It refuses rather than coping, which is the shape the binder's own
        boundary uses and for the same measured reason: a guess that is wrong
        reads as an empty input, and downstream that is indistinguishable from
        a run with nothing to do.

        !! An empty docket is refused by name, the same floor the binder puts
        under a missing `pages` key.

        !! It reports every broken rule, not the first, so a docket with three
        bad pages takes one run to fix. Every other container in this tree
        returns `(T | None, [messages])`, and this one does too.
        """
        if not isinstance(data, dict):
            return None, [_not_a(where, "a docket", data)]
        checked: dict = data
        if "pages" not in checked:
            return None, [
                f"{where}: no `pages` key -- a docket names the pages it alters"
            ]
        raw = checked["pages"]
        if not isinstance(raw, list) or not raw:
            return None, [f"{where}: `pages` must be a non-empty list of pages"]
        schedules: list[Schedule] = []
        problems: list[str] = []
        # ! ONE SCHEDULE PER PAGE. Two would let a later one silently win, and
        # which of them applied would depend on iteration order.
        seen: set[str] = set()
        for n, one in enumerate(raw):
            got, why = Schedule.deserialize(f"{where}: page {n}", one)
            if got is None:
                problems += why
                continue
            if got.path in seen:
                problems.append(f"{got.path}: two schedules for one page")
                continue
            seen.add(got.path)
            schedules.append(got)
        if problems:
            return None, problems
        return cls(schedules=tuple(schedules)), []

    def serialize(self) -> dict:
        """This docket as the wire dict."""
        # ! THE WIRE KEY IS `pages` AND THE FIELD IS `schedules` -- see the
        # class docstring. The format is not this module's to rename.
        return {"pages": [one.serialize() for one in self.schedules]}
