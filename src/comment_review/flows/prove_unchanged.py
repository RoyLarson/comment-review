"""Admit exact current and revision pages before comparing executable code."""

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

from comment_review.flows.page_for import page_of
from comment_review.flows.read_diagnostics import format_failure
from comment_review.flows.source import revision_source_of, source_of
from comment_review.machine.repo import Source, git_ls_files
from comment_review.reading.diagnostics import ReadFailure
from comment_review.results.prove_unchanged import code_fingerprint, dominant_ending


@dataclass(frozen=True)
class ProofReport:
    """Complete per-path messages and the counts used by the console policy."""

    messages: tuple[str, ...]
    failures: int
    unchecked: int


def _sibling(
    repo: Path, target: Path, edited: set[Path], tracked: list[str]
) -> tuple[Path, Source] | None:
    """A READABLE tracked file beside `target` that WRITE did not edit.

    Skips a candidate this process cannot itself read as UTF-8 text: a binary
    or non-UTF-8 sibling is unusable as a line-ending reference, and committing
    to the first NAME in the directory disabled the check where trying the next
    tracked file would have answered.

    Args:
        repo: the repository root.
        target: the file being proven; never returned as its own sibling.
        edited: every path this run was asked to prove, resolved -- none of
            them qualifies as "untouched".
        tracked: `git_ls_files(repo)` (or `[]`), passed in rather than
            queried here so a multi-path run spawns git once, not per path.
    """
    for rel in tracked:
        cand = (repo / rel).resolve()
        # ! `cand == target` IS COVERED. `edited` is built from every path this
        # run was given and `target` is one of them, so a candidate equal to
        # the target is already in the set the test above it uses.
        if cand.parent != target.parent or cand in edited:
            continue
        held = source_of(cand)
        if not isinstance(held, ReadFailure):
            return cand, held
    return None


def run(repo: Path, base: str, paths: Sequence[Path]) -> ProofReport:
    """Prove admitted pages against their exact Git baselines and sibling endings."""
    repo = repo.resolve()
    edited = {path.resolve() for path in paths}
    tracked = git_ls_files(repo) or []
    messages: list[str] = []
    failures = unchecked = 0
    for raw in paths:
        target = raw.resolve()
        try:
            rel = target.relative_to(repo).as_posix()
        except ValueError:
            messages.append(f"FAIL      {raw}: outside --repo")
            failures += 1
            continue
        before = revision_source_of(repo, base, rel)
        if isinstance(before, ReadFailure):
            if any(d.code == "missing-revision-source" for d in before.diagnostics):
                messages.append(
                    f"UNPROVABLE {rel}: no {base}:./{rel} -- new file, or bad ref"
                )
                messages.append(format_failure(before, path=rel))
            else:
                messages.append(
                    f"FAIL      baseline: {format_failure(before, path=rel)}"
                )
            failures += 1
            continue
        after = source_of(target)
        if isinstance(after, ReadFailure):
            messages.append(f"FAIL      current: {format_failure(after, path=rel)}")
            failures += 1
            continue
        page_b = page_of(target, rel=rel, source=before)
        page_a = page_of(target, rel=rel, source=after)
        failed = False
        for side, page in (("baseline", page_b), ("current", page_a)):
            if isinstance(page, ReadFailure):
                messages.append(f"FAIL      {side}: {format_failure(page, path=rel)}")
                failed = True
        if failed:
            failures += 1
            continue
        kind_b, fp_b = code_fingerprint(before.text, target)
        kind_a, fp_a = code_fingerprint(after.text, target)
        if kind_a not in ("ast", "stripped") or kind_b not in ("ast", "stripped"):
            messages.append(
                f"UNPROVABLE {rel}: prose could not be separated from code"
                " -- sameness NOT shown"
            )
            failures += 1
        elif kind_a != kind_b:
            messages.append(
                f"FAIL      {rel}: proof kind changed ({kind_b} -> {kind_a}) "
                "-- likely broke Python syntax"
            )
            failures += 1
        elif fp_a != fp_b:
            messages.append(
                f"FAIL      {rel}: executable code DIFFERS ({kind_a} proof)"
            )
            failures += 1
        else:
            messages.append(f"PROVEN    {rel}: reads the same ({kind_a})")
        sib = _sibling(repo, target, edited, tracked)
        if sib is None:
            messages.append(
                f"UNCHECKED  {rel}: no readable untouched sibling -- line endings"
            )
            unchecked += 1
        else:
            sibling, held = sib
            want = dominant_ending(held.text)
            got = dominant_ending(after.text)
            # ! BOTH sides are guarded against "none". A single-line file with
            # no trailing newline has no ending to measure, so it reads "none"
            # and would FAIL against any CRLF sibling on ABSENT endings rather
            # than wrong ones.
            if want != "none" and got != "none" and got != want:
                messages.append(
                    f"FAIL      {rel}: line endings {got}, "
                    f"sibling {sibling.name} {want}"
                )
                failures += 1
    return ProofReport(tuple(messages), failures, unchecked)
