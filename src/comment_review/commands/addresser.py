"""The `addresser` command: its argument parsing and its exit code.

The work is `reading.addresser`; this is only the console face of it.

!! A MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS MODULES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
from collections.abc import Mapping
from pathlib import Path

from comment_review.binder.addresses import resolve
from comment_review.constants import text_lines
from comment_review.flows.page_for import page_of
from comment_review.flows.read_diagnostics import format_failure
from comment_review.flows.reading_context import load_settings
from comment_review.reading.addresser import (
    DECLARED,
    EOF,
    MODULE,
    SEPARATOR,
    SERIES,
    address_for,
    cue_of,
)
from comment_review.reading.diagnostics import ReadFailure


def main() -> int:
    """Look a place up on the page it names: by line, or by address.

    Both read the file under `--repo` and no binder: an address is looked up
    from the page it names, filled or empty (`decision-log.md Process: #96`,
    `#111`).

    Returns:
        0 when a place was named, 1 when the page has no such place, 2 when the
        question was malformed or the file could not be read as a page.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="the repo root the file is under")
    ap.add_argument("--reading-settings", type=Path, metavar="FILE")
    ap.add_argument(
        "--file",
        metavar="PATH",
        help="a file under --repo, relative to it -- with --line and --series,"
        " the address of the place at that line",
    )
    ap.add_argument(
        "--line",
        type=_line,
        metavar=f"N|{MODULE}|{EOF}",
        help=f"a line NUMBER of that file, or {MODULE} or {EOF}"
        " for the places no line names: the module's documentation and front"
        " matter, and the closing gap, documentation and back matter",
    )
    ap.add_argument(
        "--series",
        choices=SERIES,
        help="which place AT that line: a the documentation of the declaration"
        " opening there, b the gap it falls in, c the room beside it, f the"
        " file's own matter",
    )
    ap.add_argument(
        "--resolve",
        metavar="ADDRESS",
        help="an address in, the LINES that cover it out, read from the file as"
        " it is now",
    )
    args = ap.parse_args()

    repo = Path(args.repo)
    settings: dict[Path, dict[str, str]] = {}
    if args.reading_settings is not None:
        settings, problems = load_settings(args.reading_settings, repo)
        if problems:
            for problem in problems:
                print(problem)
            return 2

    if args.resolve:
        return _resolve_one(repo, args.resolve, settings)
    if not (args.file and args.line is not None and args.series):
        # ! THE SET IS DERIVED from the `Series` enum, so adding a series
        # carries this sentence with it.
        print(f"--line needs --file and --series: {', '.join(SERIES)}, or --resolve")
        return 2
    given = (repo / args.file).resolve()
    return _at_line(repo, args.file, args.line, args.series, settings.get(given, {}))


def _line(given: str) -> int | str:
    """`--line`'s value: a line number, or the sentinel `MODULE` or `EOF`."""
    if given in (MODULE, EOF):
        return given
    try:
        return int(given)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"{given!r} is neither a line number nor {MODULE} or {EOF}"
        ) from None


def _resolve_one(
    repo: Path, address: str, settings: Mapping[Path, Mapping[str, str]]
) -> int:
    """An address in, the LINES that now cover it out.

    Stage 8 needs this direction after the write: every line number a record
    carried is stale by then, so the file as it is now turns an address into
    lines to read. The address is read as that file places it, which need not
    be the place the text was written at -- written text can share a
    neighbour's paragraph and read at another address.

    Several paragraphs can answer to one address -- a docstring and the comment
    run beneath it sit in the same gap -- so every match is printed.

    Returns:
        0 when the address named something, 1 when nothing on the page carries
        it, 2 when it is not an address or the file could not be read.
    """
    path, where = cue_of(address)
    if not where:
        print(f"{address!r} is not an address -- it needs a `@place`")
        return 2
    # The separator is a character a path cannot hold, so the flattened path
    # inverts by substitution; see `reading.addresser.flatten`.
    rel = path.replace(SEPARATOR, "/")
    page = page_of(
        repo / rel, rel=rel, settings=settings.get((repo / rel).resolve(), {})
    )
    if isinstance(page, ReadFailure):
        print(format_failure(page, path=rel))
        return 2
    hits = resolve(address, page.paragraphs)
    if not hits:
        print(f"{address} names no place on {rel}")
        return 1
    for i in hits:
        paragraph = page.paragraphs[i - 1]
        span = f"{paragraph.original_start}-{paragraph.original_end}"
        print(f"{rel}:{span}\t{cue_of(paragraph.address).cue}")
    return 0


def _at_line(
    repo: Path, file: str, line: int | str, series: str, settings: Mapping[str, str]
) -> int:
    """Print the address of one series' place at one line of one file.

    `line` is a line number, or a sentinel naming the places at the file's head
    or foot that no line number reaches -- see `Cues.at_line`.

    At a line number the file's own matter answers twice, head and foot, since
    no line tells them apart; a caller chooses by address, or asks at a sentinel.

    Returns:
        0 when a place was named, 1 when the page has no such place at that
        line, 2 when the file could not be read as a page.
    """
    rel = Path(file).as_posix()
    page = page_of(repo / rel, rel=rel, settings=settings)
    if isinstance(page, ReadFailure):
        print(format_failure(page, path=rel))
        return 2
    count = len(text_lines(page.text))
    if isinstance(line, int) and not 1 <= line <= count:
        print(f"{rel} has {count} lines; line {line} is not one of them")
        return 1
    found = page.cues.at_line(line, series)
    if not found and isinstance(line, str):
        print(f"{line} of {rel} has no `{series}` place")
        return 1
    if not found:
        what = "holds no code"
        if series == DECLARED:
            what = "declares nothing documentable"
        print(f"line {line} of {rel} {what}, so it has no `{series}` place")
        if series == DECLARED and page.cues.documents(None):
            head = address_for(rel, page.cues.documents(None))
            print(f"  the module's own documentation is {head}")
        return 1
    for c in found:
        print(f"{address_for(rel, c)}\t{page.cues.anchor_of(c)!r}")
    if len(found) > 1:
        print(
            f"\n{len(found)} places answer to line {line} in `{series}`."
            " Choose by ADDRESS."
        )
    return 0
