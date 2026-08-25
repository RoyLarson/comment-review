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
and neither knows what runs next. `STEPS` is the sequence as DATA so a missing
check is a missing element rather than a forgotten call.
"""

from pathlib import Path
from typing import NamedTuple

from comment_review.desk import notations as notations_mod
from comment_review.flows.page_for import page_of
from comment_review.results import compositor, galley

#: The chain, as data. ! A test asserts this tuple, so removing a check is a
#: visible deletion rather than a call somebody forgot to make.
STEPS = ("read", "verify", "edit", "set", "draft", "reread", "prove")


class Refusal(NamedTuple):
    """One reason the run stopped, and where.

    ! A REFUSAL NAMES ITS STEP. `census.py` was measured catching bare
    `Exception` and printing a type name, which tells a reader that something
    went wrong and nothing about where to look.
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
    removed, so a stopped run leaves no half-set of files that no page
    describes. ! PROVISIONAL: the resumable per-page form belongs to the
    workflow that writes over the real files.

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

    # ! THE `verify` STEP IS ADDED IN TASK 9, test-first. `recorded` and the
    # comparison that reads it arrive there together; leaving them out here is
    # what lets Task 9's test fail before it passes.
    recorded: dict[str, str] = {}
    into.mkdir(parents=True, exist_ok=True)
    drafted: list[Drafted] = []
    refusals: list[Refusal] = []

    for rel, edits in sorted(grouped.items()):
        made, why = _one(rel, edits, recorded.get(rel, ""), repo, into)
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

    # ! THE `verify` STEP LANDS HERE IN TASK 9, test-first.

    placed = galley.reset(page, edits)
    if placed:
        return None, Refusal("edit", rel, "; ".join(placed))

    text = compositor.set_page(page)
    target = into / Path(rel).name
    target.write_text(text, encoding="utf-8", newline="")
    return Drafted(rel, target, page.sha), None
