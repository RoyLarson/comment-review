"""Commits whose prose changed and whose code did not -- an answer key by construction.

!! A GRADED CASE NEEDS AN END, AND THIS IS WHERE THE HONEST ONES ARE. Roy,
2026-08-29, asked for exactly this: *"Look through the git history there are
several places where the old code had strickly documentation updates."* A commit
that leaves every changed file's executable code byte-identical while moving its
comments and docstrings **is** a human's prose fix -- so the whole diff is the
key, with nothing in it that a reviewer was not asked to find.

! WHY THAT MATTERS MORE THAN CONVENIENCE: on a mixed commit, a reviewer's finding
can be right about prose the human changed for a reason living in the CODE half
of the diff, and the grade cannot tell the two apart. A prose-only END has no
code half.

!! IT ASKS THE SHIPPED QUESTION, NOT A SECOND ONE. The test is
`prove_unchanged.code_fingerprint`, which is what stage 7b gates every WRITE on
-- so a commit named here is one the shipped gate would also call unchanged. ! A
private "strip the comments and compare" would be a second implementation of the
repo's central claim, and the one nobody tests.

! MEASURED 2026-08-29 over the last 400 commits of `test-harness-builder`: **10
prose-only commits**, from a 3-line count correction to an 84-line rename of a
traversal. ! `the-harness-cannot-run-the-system-it-grades` D1's own START/END
pair is NOT among them -- those hashes do not resolve at all, which is T42.

! AN INPUT, NEVER A GATE. It reports candidates; which one becomes a case is a
human's call, and a case still needs a run's `findings.md` before it can be
graded at all.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import subprocess
import sys
from pathlib import Path

# The package lives in `src/` and nothing installs it -- this repo declares no
# build backend. Same insert `generator_split.py` makes, for the same reason.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from comment_review.results.prove_unchanged import code_fingerprint  # noqa: E402


@dataclasses.dataclass(frozen=True)
class Candidate:
    """One START/END pair whose Python diff is entirely prose."""

    end: str
    start: str
    date: str
    subject: str
    paths: tuple[str, ...]


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=repo, capture_output=True, text=True
    ).stdout


def _blob(repo: Path, ref: str, rel: str) -> str | None:
    """The file at a ref, or None if it did not exist there."""
    done = subprocess.run(
        ["git", "show", f"{ref}:{rel}"], cwd=repo, capture_output=True
    )
    if done.returncode != 0:
        return None
    return done.stdout.decode("utf-8", errors="replace")


def prose_only(repo: Path, start: str, end: str, paths: list[str]) -> bool:
    """Whether every named file's executable code is identical across the pair.

    ! A FILE ADDED OR DELETED IS NOT A PROSE EDIT, whatever the diff looks like:
    there is no before-and-after to compare, and a new file's whole body is code
    the reviewer never saw.

    ! A FILE THAT WILL NOT PARSE ANSWERS `False` rather than raising. History
    holds broken intermediate states, and one of them must not stop the survey.
    """
    for rel in paths:
        before, after = _blob(repo, start, rel), _blob(repo, end, rel)
        if before is None or after is None:
            return False
        try:
            if code_fingerprint(before, Path(rel)) != code_fingerprint(
                after, Path(rel)
            ):
                return False
        except Exception:
            return False
    return True


def scan(repo: Path, limit: int = 400) -> list[Candidate]:
    """Every prose-only commit in the last `limit`, newest first.

    ! PYTHON ONLY, AND NOTHING ELSE MAY CHANGE. A commit that also edits a `.md`
    may well be a prose commit, but its key would span two kinds of file and the
    census only reads one of them.
    """
    found: list[Candidate] = []
    for end in _git(repo, "log", "--format=%H", f"-{limit}").split():
        start = _git(repo, "rev-parse", f"{end}^").strip()
        if not start:
            continue
        changed = _git(repo, "diff", "--name-only", start, end).splitlines()
        python = [f for f in changed if f.endswith(".py")]
        if not python or len(python) != len(changed):
            continue
        if not prose_only(repo, start, end, python):
            continue
        found.append(
            Candidate(
                end=end,
                start=start,
                date=_git(
                    repo, "log", "-1", "--format=%ad", "--date=short", end
                ).strip(),
                subject=_git(repo, "log", "-1", "--format=%s", end).strip(),
                paths=tuple(python),
            )
        )
    return found


def main(argv: list[str] | None = None) -> int:
    """Report the candidates. ! Always exits 0 -- it is an input, not a gate."""
    parser = argparse.ArgumentParser(
        description="Commits whose Python diff is all prose (candidate answer keys).",
    )
    parser.add_argument("--repo", type=Path, default=Path("."))
    parser.add_argument("--limit", type=int, default=400)
    parser.add_argument(
        "--json", action="store_true", help="machine-readable, for staging a case"
    )
    args = parser.parse_args(argv)

    # ! A Windows console is cp1252 and this prints commit subjects, which in
    # this repo hold quotation marks and dashes.
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        reconfigure(encoding="utf-8", errors="replace")

    found = scan(args.repo, args.limit)

    if args.json:
        print(json.dumps([dataclasses.asdict(c) for c in found], indent=2))
        return 0

    print(f"{len(found)} prose-only commits in the last {args.limit}\n")
    for c in found:
        print(
            f"{c.date}  START {c.start[:8]} -> END {c.end[:8]}  {len(c.paths)} file(s)"
        )
        print(f"    {c.subject}")
        for rel in c.paths:
            print(f"    - {rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
