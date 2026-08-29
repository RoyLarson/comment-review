"""B2 -- STAGE: materialise START into the directory to be graded.

! THE FIXTURE IS THIS REPO AT A REAL COMMIT. B2's whole pass criterion is byte
identity against `git show START:<path>`, and a constructed repo would be built
from whatever this test already believes -- so the one property under test would
be the one thing the fixture could not disagree about.
"""

import pathlib
import subprocess

import pytest
import stage_case

REPO = pathlib.Path(__file__).resolve().parents[2]

START = "3e1fedfe20f0da79bc8470a86ac62e7e6756ff18"  # v0.2.3^{}
CASE_PATHS = [
    "plugins/comment-review/agents/comment-review-block-context.md",
    "plugins/comment-review/skills/comment-review/references/write.md",
]


def blob_at(commit: str, path: str) -> bytes:
    out = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{commit}:{path}"],
        capture_output=True, check=True,
    )
    return out.stdout


def test_every_staged_path_is_byte_identical_to_git_show(tmp_path):
    """The box's own pass criterion, stated as the first test.

    ! `git show` writes the STORED blob. A staging step that went through a
    worktree checkout would apply `core.autocrlf` on this machine and fail this
    on line endings alone, on every text file.
    """
    stage_case.stage(REPO, START, CASE_PATHS, tmp_path / "case")

    for path in CASE_PATHS:
        assert (tmp_path / "case" / path).read_bytes() == blob_at(START, path)


def test_nothing_but_the_case_paths_is_staged(tmp_path):
    """"Leave everything else behind" -- the reviewer must see the case, not the repo.

    A staged tree carrying the whole checkout would let a role resolve a
    reference the case never handed it, and the grade would not be about the
    case any more.
    """
    stage_case.stage(REPO, START, CASE_PATHS, tmp_path / "case")

    staged = sorted(
        p.relative_to(tmp_path / "case").as_posix()
        for p in (tmp_path / "case").rglob("*")
        if p.is_file()
    )
    assert staged == sorted(CASE_PATHS)


def test_a_path_absent_at_that_commit_is_refused(tmp_path):
    """A case naming a file that does not exist at START must not stage quietly.

    ! THE PATH BELOW IS THE REALISTIC SHAPE, not a fabricated one: it exists ON
    DISK and on HEAD, and not at `v0.2.3` -- which is how a case written today
    against an older START actually goes wrong. `git show` says so itself:
    "exists on disk, but not in '3e1fedf'".

    Staging it quietly would grade a tree missing a file the case is ABOUT, and
    a role would report nothing where the defect was.
    """
    missing = "src/comment_review/machine/__init__.py"

    with pytest.raises(stage_case.PathNotAtCommit) as refused:
        stage_case.stage(REPO, START, [*CASE_PATHS, missing], tmp_path / "case")

    assert missing in str(refused.value)
    assert START[:7] in str(refused.value)
