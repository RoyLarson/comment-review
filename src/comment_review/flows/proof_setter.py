"""From the reviewers' notations to a file a human can read.

    notations + the saved binder
        -> resolve each address                    -> path + cue
        -> reload the page FROM DISK                page_of
        -> the sha is the one the binder recorded
        -> galley          the marks are put on the page
        -> compositor      the page is set as text
        -> draft           a temporary file, never the original
        -> read it back    each notation is at the cue it was given
        -> prove           only comments changed
        -> the human

!! IT STOPS AT THE TEMPORARY FILE. Roy, 2026-08-25: *"The workflow stops at
making a temporary file for the human to review. The final human-review
human-edit machine-review machine copy is its own workflow."* So `approve` is
not called here, and neither is anything transactional -- the per-page state,
the manifest and the resumable retry all belong to that second workflow.

!! NOTHING TRANSFERS FROM THE BINDER TO THE END EXCEPT TWO VALUES. Roy,
2026-08-24: *"Nothing will transfer from the binder to the end."* The ADDRESS
crosses as a key, and the SHA crosses as the thing the verification compares.
No paragraph text, kind or anchor does -- the page is read again from disk.

! THE ORDER LIVES HERE AND NOWHERE ELSE. The galley edits, the compositor sets,
and neither knows what runs next. `STEPS` names that sequence as DATA; nothing
in `run()` reads it back -- `test_the_chain_IS_this_list` pins it against a
second literal, so a step dropped from the tuple shows up as a diff against
that pin, not as a call somebody forgot to make.
"""

from pathlib import Path
from typing import NamedTuple

from comment_review.binder.page import page_for
from comment_review.desk import notations as notations_mod
from comment_review.flows.page_for import page_of
from comment_review.machine import constants
from comment_review.machine.repo import read_source
from comment_review.reading.addresser import cue_of
from comment_review.reading.lexer import language_for
from comment_review.results import compositor, galley
from comment_review.results.prove_unchanged import code_fingerprint

#: The chain, as data -- read only by `test_the_chain_IS_this_list`, which
#: pins it against a second literal; `run()` itself never consults `STEPS`.
#: ! "set" and "draft" name pipeline stages with no `Refusal` of their own: no
#: site in this module builds a `Refusal("set", ...)` or `Refusal("draft", ...)`.
STEPS = ("read", "verify", "edit", "set", "draft", "reread", "prove")


class Refusal(NamedTuple):
    """One reason the run stopped, and where.

    ! A REFUSAL NAMES ITS STEP. `census.py:204` catches a bare `Exception`
    too, and prints the path, the exception type and its message -- but
    nothing that says which of several steps failed. `step` is what a caller
    of this chain gets that a caller of `census.py` does not.
    """

    step: str
    path: str
    why: str


class Drafted(NamedTuple):
    """One page set into a temporary file, and the bytes it was reviewed at."""

    path: str
    draft: Path
    sha: str


def run(
    notations: dict[str, str | None], binder: dict, repo: Path, into: Path
) -> tuple[list[Drafted], list[Refusal]]:
    """The whole chain, or nothing at all.

    !! A REFUSAL ABORTS THE RUN WHOLE, by ruling. Roy, 2026-08-25: *"fails loud
    amd stops is the right answer for now."* Every draft this run wrote is
    removed on a refusal AND on an exception escaping a page's own step, so a
    stopped run leaves no half-set of files that no page describes. !
    PROVISIONAL: the resumable per-page form belongs to the workflow that
    writes over the real files.

    Args:
        notations: address -> replacement text, or None to delete.
        binder: as `binder.read` returned it.
        repo: the checkout the pages are read from.
        into: the directory drafts are written to. Created if absent.

    Returns:
        `(drafted, [])` when every page passed, or `([], refusals)`.
    """
    grouped, unresolved = notations_mod.by_page(notations)
    if unresolved:
        return [], [Refusal("read", "", why) for why in unresolved]

    # ! THE SHA IS READ OUT OF THE SAVED BINDER, NEVER RECOMPUTED FROM THE FILE.
    # Roy, 2026-08-25: "we can't assume that the file didn't change between
    # original read and loading to write and so getting it out of the json
    # blob is important." A sha derived from the file at write time would only
    # ask whether the file equals itself, which cannot fail.
    recorded = {
        str(page.get("path", "")): str(page.get("sha", ""))
        for page in binder.get("pages", [])
    }
    into.mkdir(parents=True, exist_ok=True)
    drafted: list[Drafted] = []
    refusals: list[Refusal] = []

    for rel, edits in sorted(grouped.items()):
        try:
            made, why = _one(rel, edits, recorded.get(rel, ""), repo, into)
        except Exception:
            # !! THE CLEANUP COVERS AN EXCEPTION, NOT ONLY A REFUSAL. Measured
            # 2026-08-25: with a later page's draft path pre-occupied, a
            # `PermissionError` from `write_text` escaped as a raw traceback
            # and an earlier page's draft was left on disk -- only the
            # `refusals` branch below unlinked what had been written. The
            # exception still propagates; this removes what the run had
            # already drafted first.
            for made in drafted:
                made.draft.unlink(missing_ok=True)
            raise
        if why is not None:
            refusals.append(why)
        elif made is not None:
            drafted.append(made)

    if refusals:
        for made in drafted:
            made.draft.unlink(missing_ok=True)
        return [], refusals
    return drafted, []


def _one(
    rel: str, edits: dict[str, str | None], recorded: str, repo: Path, into: Path
) -> tuple[Drafted | None, Refusal | None]:
    """One page through every step, or the first step that refused."""
    page, why = page_of(repo / rel, rel=rel)
    if page is None:
        return None, Refusal("read", rel, why)

    # !! AN ABSENT RECORDED SHA REFUSES; IT DOES NOT PASS. `not recorded` is
    # the first clause on purpose -- a binder page carrying no sha would
    # otherwise compare "" against a real hash, and a future shape that
    # dropped the field would turn this gate off silently rather than loudly.
    # This is also the only check in the tree that catches a reviewer editing
    # the file it was reading: no agent file declares `tools:`, so all six
    # inherit Edit and Write, and "read-only" is prose until this compares.
    if not recorded or page.sha != recorded:
        return None, Refusal(
            "verify",
            rel,
            "the file has changed since it was reviewed -- reviewed at"
            f" {recorded or '<nothing recorded>'}, reads now as {page.sha}",
        )

    placed = galley.reset(page, edits)
    if placed:
        return None, Refusal("edit", rel, "; ".join(placed))

    text = compositor.set_page(page)
    # !! THE FULL REPO-RELATIVE PATH, NOT JUST THE BASENAME. Measured
    # 2026-08-25: `into / Path(rel).name` flattened `pkg/a/util.py` and
    # `pkg/b/util.py` to the same `<into>/util.py`, so the second page's
    # draft silently overwrote the first's approved text at exit 0.
    # `commands/galley.py:124` already keeps `rel` under its output
    # directory this way -- mirrored here.
    target = (into / rel).resolve()
    # !! REFUSE ANYTHING THAT WOULD LAND OUTSIDE `into`. A `rel` carrying a
    # `..` segment joins past `into` -- `pkg/a/../../escape/util.py` -- and
    # with a matching sha the draft would land on a file outside the draft
    # directory, up to and including the source file under review. Measured
    # 2026-08-25: with `rel = "../escape_repo/sub/util.py"`, the join before
    # this check wrote the edited draft onto the source file itself, at exit
    # 0.
    if not target.is_relative_to(into):
        return None, Refusal(
            "draft", rel, "would be written outside the draft directory"
        )
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8", newline="")

    off = _reread(rel, target, edits)
    if off is not None:
        target.unlink(missing_ok=True)
        return None, off

    # !! `read_source`, NOT `read_text`. The translating reader is what this
    # branch exists to remove from the write path -- reading the draft through
    # it here would compare text read one way against text read another.
    unproven = _prove(rel, page.text, read_source(target).text, target)
    if unproven is not None:
        target.unlink(missing_ok=True)
        return None, unproven
    return Drafted(rel, target, page.sha), None


def _reread(rel: str, target: Path, edits: dict[str, str | None]) -> Refusal | None:
    """Read the draft back as a page: is each notation at the cue it was given?

    !! IT IS READ FROM DISK, NOT FROM THE PAGE IN HAND. Roy, 2026-08-24: the
    workflow *"Sends that through the page system again to make certain that
    the agents put the right comments in the right places."* A page still in
    memory would be agreeing with itself -- the shape `docs/gates.md` records
    the round trip scoring 699 of 699 on.
    """
    source = read_source(target)
    lang = language_for(target)
    if lang is None:
        return Refusal("reread", rel, "the draft has no language record")
    page = page_for(target, source.text, lang, rel=rel, sha=source.sha)
    placed = {cue_of(b.address).cue: b for b in page if b.address}
    for where, replacement in edits.items():
        got = placed.get(where)
        if got is None:
            return Refusal("reread", rel, f"{where}: the draft carries no such place")
        want = [] if replacement is None else constants.text_lines(replacement)
        if got.raw_lines != want:
            return Refusal(
                "reread", rel, f"{where}: holds {got.raw_lines!r}, was given {want!r}"
            )
    return None


def _prove(rel: str, before: str, after: str, path: Path) -> Refusal | None:
    """Is the executable code in the draft the code that was there before?

    !! AN UNPROVABLE FILE IS REFUSED, NOT PASSED. `code_fingerprint` returns an
    EMPTY fingerprint for a file it cannot strip, and two empty strings compare
    equal -- so reading its verdict without reading its KIND proves every
    unprovable file identical to every other.

    ! WHAT THIS CATCHES THAT `_reread` CANNOT. `_reread` checks only the cues a
    notation named, so a notation surviving it was -- by construction -- read
    back as a comment: for the AST tier a comment never enters the fingerprint,
    so a still-a-comment edit can never trip the `want != got` branch below.
    The residual hazard is a notation that breaks its comment's RUN and
    swallows code BEYOND the edited cue -- an edit whose comment run closes
    mid-line, or never closes at all, can delete the code that followed it.
    `_reread` cannot see that: the swallowed code was never one of the cues it
    was asked about. `_prove` compares the WHOLE file's fingerprint, which is
    what catches it. See `TODO/closing-line-deletes-code.md`.
    """
    kind, want = code_fingerprint(before, path)
    got_kind, got = code_fingerprint(after, path)
    if kind == "unprovable" or got_kind == "unprovable":
        return Refusal("prove", rel, "the code in this file cannot be proven unchanged")
    if want != got:
        return Refusal("prove", rel, "the executable code is not what it was")
    return None
