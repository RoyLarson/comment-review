"""Source verification: one role's marks against the tree they were read from.

    claim_verbatim_problems()  the sentence the claim quotes is really in a
                               text at its place
    source_problems()          every `cite` resolves inside the checkout, and
                               its `verbatim` sits near the line it names
    source_verification()      those two, over one mark
    verify_report()            those two, over every ruled mark of one
                               edit_copy
    Problem                    one thing wrong with one mark or with the copy,
                               named to route
    cited_problems()           the source check, over sources as handed rather
                               than a mark's
    cite_at()                  a `cite` split into its path and line
    WITHIN                     how many lines from its cite a `verbatim` may sit
    Cache                      a cited path -> its lines, one cache per root

!! Every check here needs the page the role read and the files it cited, which is
what separates this module from `desk/marks/rules.py`, which answers everything a
mark can be judged by on its own. `claim_verbatim_problems`, `source_problems`,
`source_verification`, `cited_problems` and `verify_report` measure a mark against
the texts `flows.verify` reads off the page, and against those files -- never a
mark's own `raw_text`, the base a party being checked could have altered. Whether a
role's report is complete and well formed is `flows.mark_errors`' question. Nothing
here compares a returned `raw_text` with what was seeded: the middle does not ask
whether a page changed, so there is no drift check.

!! How one role's marks meet another's is not asked here at all.
`flows.places.places_of` builds the places and `desk.evaluate` rules them, from
each place's own record, and an entry that will not parse is `Sheet.refused`
before either runs.

!! `verify_report` returns a `Problem` per broken rule, so a whole report is
checked in one pass and every problem is read at once. `Problem` is what a
caller can route -- see that type. Every `Problem` `verify_report` returns names
a mark; a `Problem` carrying `address=""`, about the copy rather than any one
mark, is built in other modules: `flows.bus`, `flows.answers`, `flows.verify` and
`commands/check.py`.

!! The per-mark checks take a `Mark` and `verify_report` an `EditCopy`, never a
wire dict; `cited_problems` takes the sources as handed.

`flows.verify.admit` calls `verify_report` per copy, for every entry point
that admits one: `flows.bus` admits all returned copies together, and
`commands/check.py`, `flows.fill` and `flows.transcribe` the one copy each holds.
`flows.fill` splits a cite with `cite_at`, so the two agree on which line was
cited, and `flows.answers` holds a turn's answer to `cited_problems`.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from comment_review import constants
from comment_review.desk.proof.edit_copy import EditCopy
from comment_review.desk.proof.mark import Mark, filled, without_location
from comment_review.desk.proof.source import entry_problems
from comment_review.exceptions import READ_ERRORS
from comment_review.machine.repo import can_escape, read_raw

#: How far from the line a `source` cites its `verbatim` may sit, in lines, on
#: either side. A role reads a paragraph and cites the line it was looking at,
#: so the window is what admits a cite that is off by a line or two while still
#: refusing one that names a place the text is not.
WITHIN = 3

#: The cited path, exactly as the `cite` spelled it, -> that file's lines, or
#: None where it could not be read. ! KEYED ON THE PATH ALONE, so one cache
#: belongs to one root.
Cache = dict[str, tuple[str, ...] | None]


def claim_verbatim_problems(
    where: str, mark: Mark, texts: tuple[str, ...]
) -> list[str]:
    """Whether the sentence this mark's claim quotes is really in a text at its place.

    !! The mark says which clause it quotes, never branched on the
    instruction: `Mark.quoted` is it, and the type's `quotes_original` names
    the key -- `claim.drop` for a `drop`, `claim.false` for a `correct`,
    `claim.from` for a `patch`. A type that quotes no existing sentence quotes
    "", and is passed over here entirely.

    It passes when one of `texts` holds the quote exactly once, counted over
    each whole text: the quoted text may run across several of its lines, and
    is anchored at neither end. A quote no text holds names no statement, and
    one every holding text holds more than once names several; both are
    refused, whether the mark's change was derived or supplied.

    Args:
        where: how to name this mark in a message -- its address, or a position.
        mark: one role's ruling, already read into its type.
        texts: every text at this place the quote may be in, as the flow reads
            them: the page's text at the mark's address, whether or not the
            binder holds that place or its file, and for a place a turn's batch
            sent the role, the text sent there. Where no page can be read the
            page's text is "", so a quote nothing else holds is refused. Never
            `mark.raw_text`, which is what came back -- a check reading its own
            base off the thing it is checking cannot disagree with it.

    Returns:
        One message, or an empty list.
    """
    value = mark.quoted
    if not filled(value):
        return []
    counts = [text.count(value) for text in texts]
    if 1 in counts:
        return []
    if any(counts):
        return [
            f"{where}: `claim.{mark.quotes_original}` occurs {max(counts)} times in"
            " the paragraph at this place -- a clause names one statement"
        ]
    return [
        f"{where}: `claim.{mark.quotes_original}` is not in the paragraph at this place"
    ]


def cite_at(cite: str) -> tuple[str, int] | None:
    """`path:line` split at the last colon, or None where it is not that form.

    ! The last colon, so a path carrying one of its own -- a Windows drive,
    `C:/pkg/mod.py:12` -- keeps it and only the line number is taken off.

    ! Public: `flows.fill` reads the cited line to fill a source's `verbatim`,
    and it has to split the cite the way this check does or the two would
    disagree about which line was cited.

    Returns:
        `(path, lineno)`, or None for an empty path, a line that is not
        digits, or a line below 1.
    """
    path, sep, line = cite.rpartition(":")
    if not sep or not path or not line.strip().isdigit():
        return None
    lineno = int(line)
    return (path, lineno) if lineno >= 1 else None


def _lines(root: Path, path: str, cache: Cache) -> tuple[str, ...] | None:
    """One cited file's lines, read at most once per path.

    !! SPLIT BY `constants.text_lines`, WHICH BREAKS ON CR, LF AND CRLF AND ON
    NOTHING ELSE. A role cites the number the page handed it, so the count here
    has to be a count of line ENDINGS; `str.splitlines()` also breaks on the
    vertical tab, the form feed, the three ASCII separators, NEL and Unicode's
    own line and paragraph separators, every one of which a file may hold
    inside a string literal.

    ! `read_raw` LEAVES THE ENDINGS ALONE, so a CRLF checkout and an LF one
    number the same file identically -- the three sequences the splitter breaks
    on are the three universal-newline translation would have collapsed.

    Returns:
        The lines, or None where the file could not be read. ! THE None IS
        CACHED TOO, so an unreadable path is attempted once however many
        sources cite it.
    """
    if path not in cache:
        try:
            text = read_raw(root / path)
        except READ_ERRORS:
            cache[path] = None
        else:
            cache[path] = tuple(constants.text_lines(text))
    return cache[path]


def source_problems(where: str, mark: Mark, root: Path, cache: Cache) -> list[str]:
    """Every source on this mark, checked against the file it cites.

    The checks are `cited_problems`, over the mark's own `sources`. An answer a
    turn brings back cites its evidence the same way and is held to the same
    checks, which is why they take a list of sources rather than the mark that
    carries them.
    """
    return cited_problems(where, mark.sources, root, cache)


def cited_problems(where: str, sources: object, root: Path, cache: Cache) -> list[str]:
    """Every source in this list, checked against the file it cites.

    !! IT WALKS THE SOURCES AS HANDED. Each entry is typed `object` and
    nothing narrows it first, so an entry that is not an object is REFUSED BY
    NAME rather than filtered out and lost.

    The refusals, in the order they are asked, each one ending that source:

        not an object            a bare string cannot be resolved
        `cite` not `path:line`   nothing to open and nothing to number
        the path can escape      `root / path` DISCARDS `root` when `path` is
                                 absolute, so this is asked BEFORE any file is
                                 opened and the cache stays untouched
        the file cannot be read
        the line is past the end of the file
        `verbatim` out of reach  more than `WITHIN` lines from the cited line

    Each supplied entry must carry usable `cite` and `verbatim` before its
    file is read. Whether sources are required is the carrying type's check.

    Args:
        where: how to name the citing ruling in a message -- its address, or
            a position.
        sources: what it cites, as a mark or an answer carries them. A
            value that is not a list or tuple is passed over, with no message.
        root: the checkout every `cite` is resolved against.
        cache: shared across the rulings of one report so a file cited many
            times is read once.

    Returns:
        One message per refused source, each opening `{where}: source {n}` and
        numbered from 1 in the order they were carried.
    """
    out = []
    if not isinstance(sources, (list, tuple)):
        return out
    for i, source in enumerate(sources, 1):
        at = f"{where}: source {i}"
        shape = entry_problems(at, source)
        if shape:
            out += shape
            continue
        assert isinstance(source, dict)
        cite = source.get("cite")
        verbatim = source.get("verbatim")
        assert isinstance(cite, str) and isinstance(verbatim, str)
        parsed = cite_at(cite)
        if parsed is None:
            out.append(f"{at}: `cite` {cite!r} is not `path:line`")
            continue
        path, lineno = parsed
        if can_escape(path):
            out.append(f"{at}: `cite` {cite!r} names a path outside the checkout")
            continue
        lines = _lines(root, path, cache)
        if lines is None:
            out.append(
                f"{at}: `cite` {cite!r} does not resolve -- the file cannot be read"
            )
            continue
        if lineno > len(lines):
            out.append(f"{at}: `cite` {cite!r} names a line past the end of the file")
            continue
        # ! The cited line plus `WITHIN` on each side, clamped at both ends of
        # the file, and rejoined with `\n` whatever the file's own endings are
        # -- so a `verbatim` may span lines of the window, and one quoting a
        # CRLF file's own endings will not be found in it.
        lo = max(0, lineno - 1 - WITHIN)
        hi = min(len(lines), lineno + WITHIN)
        window = "\n".join(lines[lo:hi])
        if verbatim not in window:
            out.append(f"{at}: `verbatim` is not within {WITHIN} lines of {cite}")
    return out


def source_verification(
    where: str,
    mark: Mark,
    *,
    texts: tuple[str, ...],
    root: Path,
    cache: Cache,
) -> list[str]:
    """The two checks over one mark.

    ! WHAT IT ADDS IS THE ORDER AND NOTHING ELSE -- the quoted sentence, then
    the sources. The two lists are concatenated and neither short-circuits, so
    one mark can come back carrying problems from both at once.

    Args:
        where: how to name this mark in a message -- its address, or a position.
        mark: one role's ruling, already read into its type.
        texts: every text at this place the quoted sentence may be in -- see
            `claim_verbatim_problems`.
        root: the checkout every `cite` is resolved against.
        cache: path -> lines, shared across the marks of one report.
    """
    return claim_verbatim_problems(where, mark, texts) + source_problems(
        where, mark, root, cache
    )


@dataclass(frozen=True)
class Problem:
    """One thing wrong with one mark or with the copy, named so a reader can route it.

    !! Structured rather than a sentence. `desk.proof.mark.read_mark` returns
    flat strings each opening with a `where`, and a caller cannot route on a
    sentence -- so the role and the address ride beside the message.

    ! THERE IS NO `kind` FIELD. The questions -- is this mark well formed, is
    what it quotes and cites really there, did anyone rule here -- stay
    separate lists. A `kind` would only restate which list a Problem is
    already in.

    Attributes:
        role: the `edit_copy` this came back in -- WHO to send it back to.
        address: the place, or "" for a problem about the copy itself rather
            than about any one mark.
        message: the rule broken, worded by whichever check found it.
    """

    role: str
    address: str
    message: str


def verify_report(
    copy: EditCopy, texts: Mapping[str, tuple[str, ...]], root: Path, cache: Cache
) -> list[Problem]:
    """Source-verification over every ruled mark of one role's edit_copy.

    Args:
        copy: one parsed edit_copy, as `flows.distribute.seed` hands it out and
            a role hands it back. Its `role` names who to send a finding back
            to, and `EditCopy.deserialize` has already refused a copy that
            carries none.
        texts: address -> every text a quote there may be in, as
            `flows.verify.admit` reads them. An address it lacks is
            checked against nothing, so a quote there is refused.
        root: the checkout every `cite` is resolved against.
        cache: a `Cache` to read cited files through.
            !! Required, and one per stage.
            `flows.verify.admit` calls this for every entry point, once
            per copy, and a cache built per call
            re-reads a file for every citing role.
            ! It is not optional, deliberately. A default would let a caller
            get the per-call cache back by saying nothing, which is exactly the
            defect this parameter exists to remove -- and a caller who has no
            stage to share one across can still pass `{}` and say so.

    Returns:
        Every problem found, in sheet order and then in mark order.

        !! `Problem`s rather than sentences -- see `Problem`: a caller cannot
        route on a sentence, and every one of these findings names a mark, so
        it has both a role and an address to route on. ! The three leaf
        functions return strings. They answer about one mark and are
        handed a `where`; assembling the routing is this function's job,
        because it is the one that holds the copy and therefore the role.

    !! An untouched slot is skipped, and so is an unparseable entry. The first
    is `desk.proof.mark.untouched`: a coverage gap, a place no role wrote in.
    The second has no `Mark` to check, and its parse messages belong to
    `flows.mark_errors`.

    ! The two questions this function owns are the only ones it answers --
    is the quoted sentence really in the paragraph, does every `cite` resolve.
    Whether the mark is well formed at all is asked once, one function over.

    ! A mark is named by its own `address`.
    """
    out: list[Problem] = []
    for sheet in copy.sheets:
        # !! It walks parsed marks and parses nothing. `Sheet.marks` holds only
        # what ruled, so an untouched slot and an unparseable entry are both
        # already elsewhere.
        for mark in sheet.marks:
            # ! The address is `Problem.address`, so it is not also the opening
            # of every message. The three leaf checks are handed a `where` and
            # prefix it, which is right for a caller holding nothing else; this
            # one records it as a field.
            out += [
                Problem(
                    copy.role, mark.address, without_location(mark.address, message)
                )
                for message in source_verification(
                    mark.address,
                    mark,
                    texts=texts.get(mark.address, ()),
                    root=root,
                    cache=cache,
                )
            ]
    return out
