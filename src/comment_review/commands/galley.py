"""The `galley` command: its argument parsing and its exit code.

The work is `results.galley`; this is only the console face of it.

!! A LIBRARY MODULE DOES ONE JOB AND HAS NO CLI; A FLOW CALLS LIBRARIES;
A COMMAND EXPOSES A FLOW. Ruled 2026-08-24 -- `decision-log.md Process: #12`.

!! DEPRECATED FOR THIS FLOW. Roy, 2026-08-25: *"commands/galley.py can be
considered deprecated for this flow."* `commands/proof.py` is the replacement
-- it runs the full chain in `flows/proof_setter.py` (reload, verify the
binder's recorded sha, edit, set, draft, reread, prove) from a BINDER, while
this module resolves an address to a path through `rows_of(census)`, the
binder-row coupling that chain was ruled out of. That coupling is correct
here, because this file IS the old path. NOT DELETED: it still runs, and
`SKILL.md` still names it -- rewiring the skill is `agents` lane work.
"""

import argparse
from pathlib import Path

from comment_review.binder.binder import read as read_binder
from comment_review.binder.binder import rows_of
from comment_review.binder.page import page_for
from comment_review.desk import notations as notations_mod
from comment_review.machine import exceptions
from comment_review.machine.repo import read_source, undraftable
from comment_review.reading.addresser import cue_of
from comment_review.reading.lexer import language_for
from comment_review.results import compositor
from comment_review.results.galley import reset


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
    #
    # !! THE RULE ITSELF IS `repo.undraftable`'s, and it was written out here
    # AND in `commands/proof.py` -- two copies of one rule, in a repo whose
    # conventions say a rule lives in exactly one file -- while
    # `flows/proof_setter.run`, which either command's docstring says anyone may
    # call, asked it nowhere.
    why = undraftable(out, repo)
    if why:
        print(f"REFUSED: --out {why} -- no galley written")
        return 2
    try:
        census_text = Path(args.census).read_text(encoding="utf-8")
        edits_text = Path(args.edits).read_text(encoding="utf-8")
    except exceptions.READ_ERRORS as e:
        print(f"CANNOT READ ({type(e).__name__}) -- no galley written")
        return 2
    # !! READ THROUGH `notations.read`, WHICH TYPE-CHECKS EVERY VALUE. A bare
    # `json.loads` stood here and asked nothing, so `--edits '{"m.py@b0": null}'`
    # printed `1 page(s) set, 0 edit(s) refused` at exit 0 and the comment was
    # GONE -- MEASURED 2026-08-25. `null` became meaningful when `""` stopped
    # being the vacate signal, and the paragraph recording that hazard was cut
    # from this file at the same time: *"A NULL IS NOT A DECISION. `--edits` is
    # machine-written from approved text; a key whose value failed to serialise
    # arrives as `null`."* With nothing type-checking the value, an upstream
    # serialisation failure and an approved `drop` are the same bytes.
    edits, why = notations_mod.read(edits_text)
    if why:
        print(f"CANNOT READ THE EDITS: {why} -- no galley written")
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

    # !! THE SHA THE CENSUS RECORDED, PER PAGE. Measured 2026-08-25: this
    # command asked NOTHING about staleness. Censusing a file, renaming
    # `def f():` to `def RENAMED():` and running `--census <the old one>`
    # placed every edit by cue, wrote the galley and printed
    # `1 page(s) set, 0 edit(s) refused` at exit 0 -- the cues had shifted onto
    # different code and nothing compared. The `drifted` mechanism that used to
    # ask it, paragraph by paragraph, was removed with the line arithmetic; the
    # one comparison that replaces it is the recorded sha against the sha the
    # file reads at now, which is what `flows/proof_setter.py` makes. This
    # command never calls that flow, so it makes the same comparison itself.
    recorded = {
        str(page.get("path", "")): str(page.get("sha", ""))
        for page in census.get("pages", [])
    }
    # ! Which page each address is on comes from the CENSUS, which is the only
    # thing that knows -- an address names a place, and the page it sits on is
    # the record's to state.
    where = {str(b.get("address", "")): str(b.get("path", "")) for b in paragraphs}
    by_path: dict[str, dict[str, str | None]] = {}
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
        by_path.setdefault(rel, {})[cue_of(str(address)).cue] = replacement

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
            # !! READ THROUGH `read_source`. It reads with `read_raw`, whose
            # `newline=""` leaves `\r\n` untranslated -- `read_text` collapses
            # every `\r\n` to `\n`, so the compositor would never see a CRLF
            # file and every line of the galley would differ from its
            # original by its ending, which is the whole thing this module is
            # diffed for. This call is also where `source.sha` comes from,
            # passed to `page_for` below.
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

        # !! AN ABSENT RECORDED SHA REFUSES; IT DOES NOT PASS. `not was` is the
        # first clause for the reason `flows/proof_setter.py:_one` gives at the
        # same comparison: a census page carrying no sha would otherwise compare
        # "" against a real hash, and a shape that dropped the field would turn
        # this gate off silently rather than loudly.
        was = recorded.get(rel, "")
        if not was or page.sha != was:
            print(
                f"REFUSED  {rel}: the file has changed since it was censused"
                f" -- censused at {was or '<nothing recorded>'}, reads now as"
                f" {page.sha}"
            )
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
