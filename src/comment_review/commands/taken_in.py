"""The `taken_in` command: the original against the revise a role is holding.

Bibliography's own sense of collation -- comparing two states of one text to
find where they differ, `docs/vocabulary.md`'s own naming for this command.
Prints, per page whose text differs, the unified diff `differences.unified`
renders; then one line per address whose row-level text differs between the
two roots.

!! Neither the stage nor the role that set an address is printed. Both live
on `flows.revise.Pulled` -- `revise` and `set_by` -- and this command receives
no `Pulled`: `--original` and `--revise` are two bare directories, so a
changed address is printed alone, the one fact two directory trees can answer.

The work is inline here rather than in a flow module. A command exposes a
flow, and here there is no docket to resolve, only two trees to read and
compare, so there is no flow underneath to expose.
"""

import argparse
import sys
from pathlib import Path

from comment_review.binder.binder import bind
from comment_review.differences import unified
from comment_review.flows.page_for import page_of
from comment_review.flows.read_diagnostics import (
    ContextAdmissionFailure,
    format_failure,
)
from comment_review.flows.reading_context import context_for
from comment_review.flows.source import source_of
from comment_review.machine.repo import walk_files
from comment_review.reading.diagnostics import ReadFailure
from comment_review.reading.language import INSTALLED_REGISTRY


def main(argv: list[str] | None = None) -> int:
    """Print what changed between `--original` and `--revise`.

    Returns:
        0 whether or not anything changed -- agreement is success, not a
        no-op. 2 when `--original` or `--revise` is not a readable directory.
    """
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "paths", nargs="*", help="pages to compare; default every page under --revise"
    )
    ap.add_argument(
        "--original", required=True, help="the checkout, or an earlier revise"
    )
    ap.add_argument("--revise", required=True, help="the revise root a role is holding")
    args = ap.parse_args(argv)

    original = Path(args.original)
    revise = Path(args.revise)
    if not original.is_dir():
        print(f"CANNOT READ {args.original}: not a directory")
        return 2
    if not revise.is_dir():
        print(f"CANNOT READ {args.revise}: not a directory")
        return 2

    # With no paths, compare the pages the revise holds. A revise holds only
    # the pages its docket schedules, so no other page is the revise's to
    # compare. A path given explicitly is read from both roots, and one the
    # revise lacks is named on stderr, below.
    rels = args.paths or _every_page(revise)

    changed_addresses: list[str] = []
    # Report acquisition and page admission failures on stderr even when the
    # texts match. Exit stays 0: an unreadable page is not an unreadable root.
    skipped: list[str] = []
    for rel in rels:
        context = context_for(original / rel, {})
        before_source = source_of(original / rel)
        after_source = source_of(revise / rel)
        if isinstance(before_source, ReadFailure) or isinstance(
            after_source, ReadFailure
        ):
            failure = (
                before_source
                if isinstance(before_source, ReadFailure)
                else after_source
            )
            assert isinstance(failure, ReadFailure)
            skipped.append(format_failure(failure, path=rel))
            continue
        if isinstance(context, ReadFailure):
            before_page = after_page = context
        else:
            before_page = page_of(
                original / rel, rel=rel, source=before_source, reading_context=context
            )
            after_page = page_of(
                revise / rel, rel=rel, source=after_source, reading_context=context
            )
        context_refused = any(
            isinstance(page, ContextAdmissionFailure)
            for page in (before_page, after_page)
        )
        if before_source.text != after_source.text and not context_refused:
            print("".join(unified(before_source.text, after_source.text, rel)), end="")
        if isinstance(before_page, ReadFailure) or isinstance(after_page, ReadFailure):
            failure = (
                before_page if isinstance(before_page, ReadFailure) else after_page
            )
            assert isinstance(failure, ReadFailure)
            skipped.append(
                f"{format_failure(failure, path=rel)} (addresses not compared)"
            )
            continue
        if before_source.text == after_source.text:
            continue
        before_binder = bind(
            [before_page], read_from={"root": str(original), "revise": 0}
        )
        after_binder = bind([after_page], read_from={"root": str(revise), "revise": 0})
        before_rows = {b.address: b.raw_text for b in before_binder.paragraphs}
        after_rows = {b.address: b.raw_text for b in after_binder.paragraphs}
        # !! The union of both sides. `bind` here carries no `absent=True`, so
        # a `drop` that empties a place removes its row entirely, and that
        # address is present in the original and gone from the revise.
        #
        # ! A drop is a change a role must see. This module's docstring
        # promises *"one line per address whose row-level text differs between
        # the two roots"*, and an address that stopped existing differs.
        changed_addresses.extend(
            address
            for address in sorted(before_rows | after_rows)
            if before_rows.get(address) != after_rows.get(address)
        )

    if changed_addresses:
        print()
        for address in changed_addresses:
            print(f"{address}\trole not tracked -- no docket reaches taken_in")

    for line in skipped:
        print(f"NOT COMPARED {line}", file=sys.stderr)

    return 0


def _every_page(root: Path) -> list[str]:
    """Every page's path under `root`, posix-relative.

    What a caller naming no `paths` at all gets compared instead.
    """
    rels = []
    for path in walk_files(root):
        if INSTALLED_REGISTRY.for_path(path) is None:
            continue
        rels.append(path.resolve().relative_to(root.resolve()).as_posix())
    return sorted(rels)
