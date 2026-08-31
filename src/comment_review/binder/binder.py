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

!!! **IT IS A METHOD ON `Page` SINCE 2026-08-31, AND THIS SAID THE OPPOSITE.**
Roy: *"the path and the sha can be put in the Page container and the
serialization of the page container can deal with it."* `decision-log.md
Process: #68`. What stands here is the ENVELOPE -- the version, the header, the
list of pages -- and each page writes itself.

!! **THE CONCERN THAT SENTENCE WAS DEFENDING IS REAL AND IS MET A DIFFERENT
WAY.** It read *"`vars(b)` WAS the wire format once -- the internals as
protocol, unable to diverge without breaking silently -- and a `.to_dict()`
puts that decision back inside the object in a politer form."* ! The defect was
never that the object serialized itself; it was that `vars()` made EVERY field
the format. `page._place` names five, and a field added to `Paragraph`
tomorrow reaches no agent. What an agent sees stays an EDITORIAL ruling
(`Addressing: #12`), not a fact about what a `Paragraph` is.

! **AND ONE PAGE SERVES TWO AUDIENCES THAT DISAGREE**, which is what the two
page types are: an agent gets five fields, no fences and no empty places, while
the compositor needs every one of them or the file cannot be set back -- so the
compositor reads the file from disk and never a binder.
"""

from dataclasses import dataclass

from comment_review.binder.page import Page, RedactedPage
from comment_review.reading.lexer import Paragraph

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
    # !! `absent` CHOOSES THE PAGE TYPE, IT DOES NOT FILTER A ROW LIST --
    # `decision-log.md Process: #68`. A `Page` serializes every addressed place;
    # a `RedactedPage` serializes the ones holding prose. The cut is the page's
    # own, at the one moment it knows what it is being asked for.
    return Binder(
        version=VERSION,
        read_from={**read_from},
        pages=tuple(page if absent else RedactedPage.of(page) for page in pages),
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
    pages: tuple[Page | RedactedPage, ...]

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
        so a page with no `path` and a place with no `cue` are refused BY NAME
        here rather than folded to `""` by whichever consumer met them first.

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
        # as `desk.containers.parse_edit_copy`.
        checked: dict = data
        if "pages" not in checked:
            return None, [
                f"{where}: carries no `pages` -- is this the output of `census --json`?"
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
    def paragraphs(self) -> list[Paragraph]:
        """Every ADDRESSED paragraph on every page, in the binder's own order.

        !! A FENCE IS NEVER CARRIED, ASKED FOR OR NOT -- `bind`'s own rule, and
        this is where it now holds. It names no place, so there is nothing to
        cite and nothing to rule on. ! `bind` used to apply it while building a
        row list; a `Page` holds every paragraph it read, fences included, so
        the rule moved to the two places that hand places out: here, and
        `Page.serialize`. **They filter alike, so what a binder carries in
        memory and what it writes are the same set.**

        ! THIS IS WHAT `rows_of` ANSWERED, and it was `.rows` of an invented row
        type for three hours on 2026-08-31 -- `decision-log.md Process: #68`. A
        page holds paragraphs, so what is left here is the walk.
        """
        return [b for page in self.pages for b in page.paragraphs if b.address]
