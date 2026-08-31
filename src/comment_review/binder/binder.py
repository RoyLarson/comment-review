"""What a BINDER is on disk, and how one is read back.

A binder is the artifact the gatherer hands over -- a folder of pages, each
naming its file, with the rows an agent rules on. Roy, 2026-08-24: *"The
gatherer/census hands over the binder as in a 3-ring binder full of stuff."*

!! ONE MODULE OWNS BOTH DIRECTIONS, and the reason is what happened without it.
MEASURED 2026-08-24: the census wrote a bare list and FOUR commands each decided
for themselves what a census file is --

    addresser   loaded.get("paragraphs", []) if isinstance(loaded, dict) else loaded
    galley      census["paragraphs"] if isinstance(census, dict) else census
    record      loaded["paragraphs"] if isinstance(loaded, dict) else loaded
    collator    json.loads(census_text)          -- no envelope handling at all

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

!! IT IS NOT A METHOD ON `Page`, AND THAT IS DELIBERATE. `vars(b)` WAS the wire
format once -- the internals as protocol, unable to diverge without breaking
silently -- and a `.to_dict()` puts that decision back inside the object in a
politer form. What an agent sees is an EDITORIAL ruling (`decision-log.md
Addressing: #12`), not a fact about what a `Paragraph` is. ! And one page serves
two audiences that disagree: an agent gets SIX fields, no fences and no empty
places, while the compositor needs every one of them or the file cannot be set
back.
"""

from dataclasses import dataclass

from comment_review.binder.page import Page
from comment_review.reading.addresser import address_for
from comment_review.reading.lexer import Paragraph
from comment_review.reading.series import Kind

# ! The shape's own version, so a reader can say WHICH format it refused rather
# than only that it could not read one.
#
# !! BUMPED TO "2" WHEN `read_from` BECAME REQUIRED, 2026-08-28.
#
# ! AND NOTHING REFUSES ON IT. This comment claimed for one commit that an older
# artifact was "refused by name (a version mismatch)"; nothing reads `version`
# to decide anything, so no such refusal exists and the sentence asserted an
# enforcement the file does not carry. What the field does is LABEL an artifact,
# so a reader holding one can say which format it is.
#
# !! REFUSING A MISSING `read_from` IS `Binder.deserialize`'s SINCE 2026-08-31,
# and this said it was `seed`'s. The rule it cited -- `read`'s own *"WHAT IS
# CHECKED IS WHAT IS CONSUMED and no more"* -- went with `read`: a CONTAINER
# promises its fields to everything downstream, so it checks what it DECLARES
# rather than what any one caller happens to consume. `decision-log.md Process:
# #67`. ! `seed` no longer raises; it cannot be handed a binder without the
# field.
VERSION = "2"


def page_row(paragraph: Paragraph, path: str = "") -> "BinderRow":
    """One paragraph as an agent receives it.

    !! FIVE FIELDS, RULED ONE BY ONE -- `decision-log.md Addressing: #12`. The
    row carried nineteen until 2026-08-24; eleven went, and `path` moved to the
    page that holds the row rather than being repeated on every one of them.

    ! THE PROSE LEAVES AS ONE STRING. Roy: *"LLMs and the token parsers read
    this as a complete and coherent statement. They do not read this as the same
    thing: ['LLMs and the token', 'parsers read this as a', ...]."* The four
    reviewers ARE token parsers and prose is what they judge, so fragments make
    each role reassemble the sentence before it can ask whether it is true.

    Args:
        paragraph: the place being carried.
        path: the page that holds it, so the row can carry its own address.
            Defaults to `""` for a caller building one row out of context;
            `bind` always states it.

    Returns:
        A `BinderRow`. ! IT RETURNED THE WIRE DICT UNTIL 2026-08-31 and now
        returns the container -- `decision-log.md Process: #67`. The five
        fields above are what `BinderRow.serialize` writes back out, so the
        format this docstring describes is unchanged.
    """
    values = {
        "cue": paragraph.address.split("@")[-1],
        # !! `kind` IS GONE AGAIN, AND THE ORIGINAL RULING WAS RIGHT. It read
        # *"they are stating something that the cue letter states"*; I put it
        # back on 2026-08-25 arguing the letter gives the SERIES while the kind
        # gives which half of the pair. Both are true, and the second stopped
        # mattering the moment ABSENT PLACES STOPPED BEING SENT: every row a
        # reviewer receives holds prose, so its kind is its series' `present`
        # and the letter states it after all.
        #
        # ! MEASURED before the cut, over 14,139 rows: `kind` equalled
        # `derive(cue, raw_text)` in 14,136 of them. The three exceptions are
        # `go`, `ruby` and `lua`, where the kind DISAGREES with the cue -- a
        # defect, filed, and not information.
        "anchor": paragraph.anchor,
        # !! `anchor_num` LEFT ON 2026-08-25, and it is the one cut made on the
        # expectation that it MIGHT come back. Roy: *"lets drop it and add it
        # back if it actually becomes necessary. That is safe now."* It was kept
        # in 2026-08-21 because the galley and compositor were thought to need
        # an order the cues could not be trusted to carry -- and the chain ruled
        # since (`Process: #14`) has the write path RELOAD the page from disk,
        # so it takes the anchor order from the page and never from a row.
        #
        # ! MEASURED before removing it: NOTHING read it from a row. `page`
        # stamps it and `addresser` computes it, both on the page side.
        "original_start": paragraph.original_start,
        "original_end": paragraph.original_end,
        "raw_text": "\n".join(paragraph.raw_lines),
    }
    return BinderRow(
        path=path,
        address=address_for(path, values["cue"]),
        **values,
    )


def bind(pages: list[Page], read_from: dict, absent: bool = False) -> "Binder":
    """Every page in scope, as the binder that is handed over.

    !! `read_from` IS REQUIRED, NOT DEFAULTED. A binder that cannot say which
    root it was censused from is exactly the ambiguity a later stage needs
    resolved: a revise re-binds from a tree copy, and a role holding that
    binder cannot tell it apart from the original unless the binder says so.
    A caller with no root to name has nothing it was censused FROM, so there
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

    !! AND AN EMPTY PLACE IS STILL ADDRESSED, WHICH IS WHAT MAKES THIS SAFE. The
    walk emits every place, filled or not, so a reviewer that wants to `add`
    ASKS for the one it means:

        comment_review addresser --census C --anchor "<line of code>" --series b

    -- which answers `m.py@b1`. The place is citable without being carried, so
    `add` stays expressible and nothing pays for the other 5,201.

    ! A FENCE IS NEVER CARRIED, asked for or not. It names no place, so there is
    nothing to cite and nothing to rule on.

    Args:
        pages: the pages in scope.
        read_from: `{"root": "<path>", "revise": <int>}` -- the root this
            binder was censused from, and `0` for the original or the
            revise's own number otherwise.
        absent: carry the empty places too. For the caller that specifically
            asks -- a reviewer surveying where prose COULD go rather than
            ruling on prose that is there.

    Raises:
        ValueError: `read_from` is not `{"root": str, "revise": int}`.

    !! THE SHAPE IS CHECKED HERE AND ON THE WAY BACK IN, and only the arity was
    checked until 2026-08-28. MEASURED: `read_from="oops"`, `None`, `[]` and
    `{"root": 7}` each built a binder and each passed `ty`, because `dict` says
    nothing about what is IN one. `seed` then copied the value verbatim onto the
    `edit_copy` an editorial role fills.

    ! AND IT IS COPIED, NOT ALIASED. The stored dict was the caller's own until
    the same day, so a binder, every `edit_copy` seeded from it, and whatever the
    caller kept were ONE object -- a test writing `binder["read_from"]["revise"]
    = 1`, which is how a revise test is naturally written, would have changed
    what every later test in the session saw, with no gate able to attribute it.
    """
    why = _read_from_problem({"read_from": read_from})
    if why:
        raise ValueError(why)
    return Binder(
        version=VERSION,
        read_from={**read_from},
        pages=tuple(
            BinderPage(
                path=page.path,
                sha=page.sha,
                rows=tuple(
                    page_row(b, page.path)
                    for b in page.paragraphs
                    if b.address and (absent or not Kind.holds_no_prose(b.kind))
                ),
            )
            for page in pages
        ),
    )


def _read_from_problem(loaded: dict) -> str:
    """Why this binder's `read_from` cannot be used, or `""`.

    !! THIS IS `read` RULING ON A FIELD, WHICH THE DOCSTRING BELOW SAYS IT DOES
    NOT DO -- and the rule is unchanged, because the rule is WHAT IS CHECKED IS
    WHAT IS CONSUMED. Nothing consumed a field when that was written. `seed`
    consumes this one.

    !! MEASURED 2026-08-28, and it is why the check moved here from `seed`
    alone: `distribute --seed` over a version-"1" binder exited 1 with `KeyError:
    'read_from'` and an eight-frame traceback on stderr and nothing on stdout,
    past `main`'s own promise of *"2 when an input could not be read"*.
    `commands/distribute.py:79` calls `seed` immediately after this function returns
    no problem, so a field `seed` requires and `read` ignored could only surface
    as a crash. ! RAISING IS NOT REFUSING: a refusal in this module is a NAMED
    REASON and an exit code, which is what a reader can act on.

    ! AND THE SHAPE IS CHECKED, NOT ONLY THE PRESENCE. MEASURED the same day:
    `read_from="oops"`, `None`, `[]` and `{"root": 7}` each built a binder, each
    passed `ty`, and `seed` copied the value verbatim onto the `edit_copy`
    handed to an editorial role. That is the defect this module's own header
    records being fixed on 2026-08-25 -- *"THE KEY WAS TESTED FOR PRESENCE AND
    NOT FOR SHAPE ... so it coped after all"* -- arriving on a new field.
    """
    if "read_from" not in loaded:
        return (
            "carries no `read_from` -- a binder written before 2026-08-28 "
            f'(version "1"); re-run `census --json` to get a version "{VERSION}" one'
        )
    read_from = loaded["read_from"]
    if not isinstance(read_from, dict):
        kind = type(read_from).__name__
        return f"`read_from` is a JSON {kind}, not a mapping of `root` and `revise`"
    if not isinstance(read_from.get("root"), str):
        return "`read_from` carries no `root` string -- which tree was censused?"
    if not isinstance(read_from.get("revise"), int):
        return "`read_from` carries no `revise` number -- 0 is the original"
    return ""


def _not_a(where: str, noun: str, value: object) -> str:
    """One refusal, naming the JSON type that arrived instead of `noun`."""
    return f"{where}: a JSON {type(value).__name__}, not {noun}"


@dataclass(frozen=True)
class BinderRow:
    """One paragraph, as an agent receives it and as a consumer holds it.

    Attributes:
        cue: the place's own cue -- `b1`, `a0`.
        anchor: the line of code the prose answers to.
        original_start: the paragraph's first line on the page, 1-based.
        original_end: its last.
        raw_text: the prose, as ONE string -- see `page_row` for why it is not
            split into lines.
        path: the page holding this row, put back by `BinderPage.deserialize`.
        address: `path@cue`, composed by `address_for`.

    !! `path` AND `address` ARE DERIVED AND ARE NOT ON THE WIRE, which is what
    `rows_of` did for every consumer until 2026-08-31. The file is stored once
    per page because repeating it per row is the same string as many times as
    the file has paragraphs; every consumer still wants both per row, so the
    page rejoins them at DESERIALIZE rather than four callers each remembering
    to. ! `serialize` emits the five wire fields alone, which is what keeps the
    round trip an identity.

    ! `address_for` COMPOSES THE ADDRESS, not an f-string here. It is the only
    place the two halves are joined and it flattens the path itself -- the
    compositor was MEASURED disagreeing with itself on 2026-08-22 for
    re-deriving exactly this.
    """

    cue: str
    anchor: str
    original_start: int | None
    original_end: int | None
    raw_text: str
    path: str
    address: str
    # !! THE LINE NUMBERS ARE `int | None` HERE AND `int` OFF THE WIRE, AND THAT
    # IS NOT A CONTRADICTION -- the two constructors have different sources.
    # `page_row` builds from a `Paragraph`, whose own fields are `int | None`:
    # its `__post_init__` fills them from `start`/`end` only when BOTH are None,
    # so one can survive unset. `deserialize` reads a WRITTEN binder, where a
    # line number that is not an integer is a malformed artifact and is refused
    # by name. ! The field admits what a page can produce; the boundary admits
    # only what a valid file holds, which is the stricter of the two.

    @classmethod
    def deserialize(
        cls, where: str, data: object, path: str
    ) -> "tuple[BinderRow | None, list[str]]":
        """One row, checked, and stamped with the page that holds it.

        Args:
            where: how to name this row in a message.
            data: one entry of a page's `rows`, as the load produced it.
            path: the owning page's real repo path. Context the row cannot
                know, the way `where` is -- it is stored once per page.

        Returns:
            `(BinderRow, [])` or `(None, [messages])`.

        !! THE `cue` IS WHAT MAKES A ROW ADDRESSABLE, so a row without one is
        refused rather than folded to `""`. `rows_of` did fold it, and
        `address_for(path, "")` answers a real-looking address that names no
        place -- which `tests/test_binder.py` pinned as expected behaviour.
        """
        if not isinstance(data, dict):
            return None, [_not_a(where, "a row", data)]
        cue = data.get("cue")
        if not isinstance(cue, str) or not cue.strip():
            return None, [f"{where}: a row needs the `cue` of the place it holds"]
        problems: list[str] = []
        # !! EACH VALUE IS BOUND AS IT IS CHECKED, not re-read at construction.
        # Re-reading `data["anchor"]` below the loop hands back `object`,
        # because a loop back-edge invalidates the `isinstance` narrow -- the
        # same fact `desk.containers.parse_edit_copy` records and answers with a
        # declaration. ! HERE THE ANSWER IS TO KEEP WHAT WAS CHECKED, which is
        # stronger than re-declaring the type: there is no second read that
        # could see a different value.
        text: dict[str, str] = {}
        for name in ("anchor", "raw_text"):
            value = data.get(name)
            if isinstance(value, str):
                text[name] = value
            else:
                problems.append(f"{where}: {cue} needs a `{name}` string")
        lines: dict[str, int] = {}
        for name in ("original_start", "original_end"):
            # ! `bool` IS AN `int` IN PYTHON and is refused here on purpose: a
            # JSON `true` in a line number is a malformed artifact, not a line.
            value = data.get(name)
            if isinstance(value, int) and not isinstance(value, bool):
                lines[name] = value
            else:
                problems.append(f"{where}: {cue} needs an `{name}` line number")
        if problems:
            return None, problems
        return (
            cls(
                cue=cue,
                anchor=text["anchor"],
                original_start=lines["original_start"],
                original_end=lines["original_end"],
                raw_text=text["raw_text"],
                path=path,
                address=address_for(path, cue),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This row as the wire dict, the five fields `page_row` writes."""
        return {
            "cue": self.cue,
            "anchor": self.anchor,
            "original_start": self.original_start,
            "original_end": self.original_end,
            "raw_text": self.raw_text,
        }


@dataclass(frozen=True)
class BinderPage:
    """One file in the binder, and the places on it an agent rules on.

    Attributes:
        path: the file's real repo path.
        sha: its digest when it was censused, from `machine.repo.sha_of`.
        rows: one per place carried. An EMPTY tuple is ordinary -- a page whose
            every place is absent carries no rows, and `bind`'s `absent`
            argument is what decides that.
    """

    path: str
    sha: str
    rows: tuple[BinderRow, ...]

    @classmethod
    def deserialize(
        cls, where: str, data: object
    ) -> "tuple[BinderPage | None, list[str]]":
        """One page and every row on it, checked.

        ! EVERY BAD ROW IS REPORTED, not the first, matching
        `desk.containers.parse_edit_copy`: a page handed back with two
        malformed rows is two things to fix.

        Returns:
            `(BinderPage, [])` or `(None, [messages])`.
        """
        if not isinstance(data, dict):
            return None, [_not_a(where, "a page", data)]
        path = data.get("path")
        if not isinstance(path, str) or not path.strip():
            return None, [f"{where}: a page needs the `path` of the file it holds"]
        raw_rows = data.get("rows", [])
        if not isinstance(raw_rows, list):
            where_rows = f"{where}: {path}: `rows`"
            return None, [_not_a(where_rows, "a list of rows", raw_rows)]
        rows: list[BinderRow] = []
        problems: list[str] = []
        for n, raw in enumerate(raw_rows):
            row, why = BinderRow.deserialize(f"{where}: {path} row {n}", raw, path)
            if row is None:
                problems += why
            else:
                rows.append(row)
        if problems:
            return None, problems
        # ! AN ABSENT OR NULL `sha` IS ADMITTED AS "", the fold
        # `desk.containers.parse_sheet` carries and for the same reason -- and
        # `desk.containers-and-verification-are-unwired` T9 holds the open
        # question of whether it should be.
        raw_sha = data.get("sha")
        return (
            cls(
                path=path,
                sha=raw_sha if isinstance(raw_sha, str) else "",
                rows=tuple(rows),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This page as the wire dict `bind` writes."""
        return {
            "path": self.path,
            "sha": self.sha,
            "rows": [row.serialize() for row in self.rows],
        }


@dataclass(frozen=True)
class Binder:
    """Every page in scope, as the artifact the gatherer hands over.

    Attributes:
        version: the format's own number -- `VERSION` for one this tree wrote.
        read_from: `{"root": str, "revise": int}` -- which tree was censused.
        pages: one per file in scope, in the order they were bound.

    !! THE LOAD IS NOT HERE, ruled `decision-log.md Process: #67`. Roy,
    2026-08-31: *"all flows start with a load step - not the modules code."*
    `deserialize` takes what the load PRODUCED -- an already-decoded dict --
    so this module holds no `json.loads` and reaches no path. What a binder IS
    stays here; turning bytes into an object belongs to the end that owns one.

    ! `machine.json_object.object_of` IS THAT LOAD and did not go anywhere: it
    moved to the four commands, which each call it and then this.
    """

    version: str
    read_from: dict
    pages: tuple[BinderPage, ...]

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

        !! AND IT NOW RULES ON EVERY FIELD IT CARRIES, which `read` did not.
        `read`'s own docstring stated the rule it was built to: *"WHAT IS
        CHECKED IS WHAT IS CONSUMED and no more"*, and nothing there read a
        field, so nothing there ruled on one -- the checks stopped at `pages`
        being a list of dicts of dicts. **That rule does not survive a
        container**: a `Binder` promises its fields to everything downstream,
        so a page with no `path` and a row with no `cue` are refused BY NAME
        here rather than folded to `""` by whichever consumer met them first.
        """
        if not isinstance(data, dict):
            return None, [_not_a(where, "a binder", data)]
        # !! DECLARED, NOT NARROWED, because the read at `checked["read_from"]`
        # below sits past a loop. An `isinstance` narrow is invalidated at a
        # loop back-edge, so `ty` loses it before that read; an explicit
        # annotation is a declaration and survives. Same reason, same spelling
        # as `desk.containers.parse_edit_copy`.
        checked: dict = data
        if "pages" not in checked:
            return None, [
                f"{where}: carries no `pages` -- is this the output of `census --json`?"
            ]
        raw_pages = checked["pages"]
        if not isinstance(raw_pages, list):
            return None, [_not_a(f"{where}: `pages`", "a list of pages", raw_pages)]
        pages: list[BinderPage] = []
        problems: list[str] = []
        for n, raw in enumerate(raw_pages):
            page, why = BinderPage.deserialize(f"{where}: page {n}", raw)
            if page is None:
                problems += why
            else:
                pages.append(page)
        if problems:
            return None, problems
        # ! LAST, BEHIND THE `pages` CHECKS, AND THAT ORDER IS LOAD-BEARING.
        # Put first, it answered every malformed-`pages` artifact with "carries
        # no `read_from`" -- true, and not the reason the file is unreadable.
        # `pages` is what a binder IS; the header says which tree it came from.
        why_header = _read_from_problem(checked)
        if why_header:
            return None, [f"{where}: {why_header}"]
        raw_version = checked.get("version")
        return (
            cls(
                version=raw_version if isinstance(raw_version, str) else "",
                # ! COPIED, NOT ALIASED -- `bind` and `seed` both do the same
                # with this field, so a caller mutating its own dict cannot
                # change what a deserialized binder already holds.
                read_from={**checked["read_from"]},
                pages=tuple(pages),
            ),
            [],
        )

    def serialize(self) -> dict:
        """This binder as the wire dict, which `bind` writes today."""
        return {
            "version": self.version,
            "read_from": {**self.read_from},
            "pages": [page.serialize() for page in self.pages],
        }

    @property
    def rows(self) -> list[BinderRow]:
        """Every row on every page, each already knowing its path and address.

        ! THIS IS WHAT `rows_of` ANSWERED, and the rejoining moved to
        `BinderRow.deserialize` -- see there. What is left here is the walk.
        """
        return [row for page in self.pages for row in page.rows]
