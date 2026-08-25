"""The `galley` command: its argument parsing and its exit code.

The work is `results.galley`; this is only the console face of it.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.
"""

import argparse
import json
from pathlib import Path

from comment_review.binder.binder import read as read_binder
from comment_review.binder.binder import rows_of
from comment_review.binder.page import page_for
from comment_review.machine import exceptions
from comment_review.machine.repo import read_source
from comment_review.reading.lexer import language_for
from comment_review.results import compositor
from comment_review.results.galley import drifted, reset


def main() -> int:
    """Set a galley of every page an edit touches, and report what refused."""
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--repo", default=".", help="repo root the census resolves against")
    ap.add_argument("--census", required=True, help="the JSON census these edits cite")
    ap.add_argument(
        "--edits",
        required=True,
        help='JSON: {"<address>": "<replacement paragraph>"}',
    )
    ap.add_argument("--out", required=True, help="directory the galley is written to")
    args = ap.parse_args()

    repo = Path(args.repo).resolve()
    out = Path(args.out).resolve()
    # !! `--out` MUST BE DISJOINT FROM `--repo`, AND NOTHING ASKED UNTIL
    # 2026-08-22. The per-file guard below checks that a target lands inside
    # `--out`; on an OVERLAP that is satisfied by the source file itself, so the
    # guard passed and `compositor.draft` OVERWROTE the file under review --
    # printing `1 page(s) set` and exiting 0.
    #
    # ! IT IS THE SAME DESTRUCTIVE OUTCOME THE GUARD BELOW RECORDS from
    # 2026-08-17. That fix closed the absolute-path cause and left this one, and
    # a per-file test cannot close it: the question is about the two ROOTS and
    # has to be asked once, here, before any file is read.
    #
    # ! REFUSED WHOLE. Nothing under `--repo` is touched by this module, so a
    # run that could touch it is not a run with some bad files in it.
    # ! `is_relative_to` IS TRUE OF A PATH AND ITSELF, so the equality test
    # that stood here first was covered by the one beside it.
    if out.is_relative_to(repo) or repo.is_relative_to(out):
        print(
            f"REFUSED: --out {out} overlaps --repo {repo}, so a galley would be"
            " written over the files under review -- no galley written"
        )
        return 2
    try:
        census_text = Path(args.census).read_text(encoding="utf-8")
        edits = json.loads(Path(args.edits).read_text(encoding="utf-8"))
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- no galley written")
        return 2
    except json.JSONDecodeError as e:
        print(f"CANNOT PARSE as JSON ({e}) -- no galley written")
        return 2
    # ! REFUSED BY NAME. `rows_of` alone answers `[]` for a binder it cannot
    # read, and the check below would then report "carries no addresses" about
    # a file whose real problem is its shape.
    census, why = read_binder(census_text)
    if why:
        print(f"CANNOT USE {args.census}: {why} -- no galley written")
        return 2

    paragraphs = rows_of(census)
    # !! AN UNADDRESSED CENSUS MATCHES NOTHING. `--edits` is keyed by address, so
    # every edit would be refused one at a time with a message about the EDIT
    # rather than about the census. ! `page_for` does not stamp addresses -- the
    # run loop does, once the path is repo-relative -- so a census built by
    # calling that function directly reaches here looking complete.
    if paragraphs and not any(str(b.get("address", "")) for b in paragraphs):
        print(
            f"CANNOT USE {args.census}: it carries no addresses, so no edit can"
            " be keyed against it. Write it with `census.py --json`"
        )
        return 2

    # ! Which page each address is on comes from the CENSUS, which is the only
    # thing that knows -- an address names a place, and the page it sits on is
    # the record's to state.
    where = {str(b.get("address", "")): str(b.get("path", "")) for b in paragraphs}
    by_path: dict[str, dict[str, str]] = {}
    refused = 0
    for address, replacement in edits.items():
        rel = where.get(str(address), "")
        if not rel:
            print(
                f"REFUSED  {address!r}: no paragraph in this census"
                " carries that address"
            )
            refused += 1
            continue
        by_path.setdefault(rel, {})[str(address)] = replacement

    written = 0
    for rel, file_edits in sorted(by_path.items()):
        # !! REFUSE ANYTHING THAT WOULD LAND OUTSIDE `--out`, BEFORE READING.
        # `out / rel` is the source path itself when `rel` is absolute --
        # Python's join lets an absolute right-hand side win -- and an absolute
        # path is exactly what a census taken before that was fixed carries.
        # Measured 2026-08-17: the galley overwrote the file under review,
        # wrote nothing under `--out`, and reported success.
        target = (out / rel).resolve()
        if not target.is_relative_to(out):
            print(f"REFUSED  {rel}: would be written outside --out")
            refused += len(file_edits)
            continue
        source_path = repo / rel
        try:
            # !! READ RAW. `read_text` collapses every `\r\n` to `\n`, so the
            # compositor would never see a CRLF file and every line of the
            # galley would differ from its original by its ending -- which is
            # the whole thing this module is diffed for.
            source = read_source(source_path)
        except exceptions.READ_ERRORS as e:
            print(f"REFUSED  {rel}: {type(e).__name__}")
            refused += len(file_edits)
            continue
        text = source.text

        lang = language_for(source_path)
        if lang is None:
            print(f"REFUSED  {rel}: no language record, so it has no page")
            refused += len(file_edits)
            continue
        page = page_for(source_path, text, lang, rel=rel, sha=source.sha)

        # ! The CHEAPER refusal first, and the one that is about the FILE rather
        # than about any one edit: a census taken before the code moved names
        # places that no longer sit where the reviewers read them.
        moved = drifted(page, [b for b in paragraphs if str(b.get("path", "")) == rel])
        if moved:
            print(f"REFUSED  {rel}: {len(moved)} anchor(s) moved since the census")
            for line in moved[:3]:
                print(f"           {line}")
            refused += len(file_edits)
            continue

        problems = reset(page, file_edits)
        if problems:
            # ! Every edit is placed BEFORE anything is written, so one that
            # cannot be refuses its file rather than half-setting it.
            print(f"REFUSED  {rel}: {len(problems)} edit(s) could not be placed")
            for line in problems[:3]:
                print(f"           {line}")
            refused += len(file_edits)
            continue

        target.parent.mkdir(parents=True, exist_ok=True)
        compositor.draft(page, target)
        print(f"galley   {rel} ({len(file_edits)} paragraph(s))")
        written += 1

    print(f"\n{written} page(s) set, {refused} edit(s) refused -> {out}")
    # ! Nonzero when anything refused. A galley missing a paragraph is not a
    # galley of the proposal, and censusing it would measure a text nobody
    # proposed.
    return 1 if refused else 0
