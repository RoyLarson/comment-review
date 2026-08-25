"""The chain from notations to a drafted file a human can read.

! THE ORDER IS DATA. A missing check is then a missing element rather than a
forgotten call -- which is the one failure a runner that hard-codes its
sequence cannot show you.
"""

from conftest import SAMPLE, build, by_cue

from comment_review.binder.binder import bind
from comment_review.flows import proof_setter


def test_the_chain_IS_this_list():
    assert proof_setter.STEPS == (
        "read",
        "verify",
        "edit",
        "set",
        "draft",
        "reread",
        "prove",
    )


def _tree(tmp_path):
    """A one-file repo, and the binder taken over it."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page = build(SAMPLE)
    return repo, bind([page]), page


def test_a_notation_reaches_a_drafted_file(tmp_path):
    repo, binder, page = _tree(tmp_path)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    into = tmp_path / "out"
    drafted, refused = proof_setter.run(
        {f"m.py@{cue}": "# REPLACED"}, binder, repo, into
    )
    assert refused == []
    assert len(drafted) == 1
    assert "# REPLACED" in drafted[0].draft.read_text(encoding="utf-8")


def test_nothing_under_the_repo_is_touched(tmp_path):
    repo, binder, page = _tree(tmp_path)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    before = (repo / "m.py").read_bytes()
    proof_setter.run({f"m.py@{cue}": "# REPLACED"}, binder, repo, tmp_path / "out")
    assert (repo / "m.py").read_bytes() == before


def test_a_refusal_NAMES_ITS_STEP(tmp_path):
    repo, binder, _ = _tree(tmp_path)
    _, refused = proof_setter.run({"m.py@b99": "# x"}, binder, repo, tmp_path / "out")
    assert refused and refused[0].step in proof_setter.STEPS


def test_ONE_FILES_REFUSAL_DRAFTS_NOTHING_FOR_ANY_FILE(tmp_path):
    """Abort-whole: a good page in the same run gets no draft either."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "m.py").write_text(SAMPLE, encoding="utf-8", newline="")
    (repo / "n.py").write_text(SAMPLE, encoding="utf-8", newline="")
    page_m = build(SAMPLE, "m.py")
    page_n = build(SAMPLE, "n.py")
    binder = bind([page_m, page_n])
    cue = next(c for c in by_cue(page_m) if c.startswith("b"))
    into = tmp_path / "out"
    notations = {f"m.py@{cue}": "# REPLACED", "n.py@b99": "# bad"}
    drafted, refused = proof_setter.run(notations, binder, repo, into)
    assert drafted == []
    assert len(refused) == 1
    assert refused[0].path == "n.py"
    assert list(into.iterdir()) == []


class TestTheFileMustBeTheONEThatWasReviewed:
    """!! THE CHECK THE READ-ONLY ROLES HAVE NEVER HAD. No agent file declares
    `tools:`, so all six inherit Edit and Write -- read-only is prose. This is
    what catches a reviewer that edited the file it was reading.
    See TODO/reviewers-are-not-read-only.md."""

    def test_a_ONE_BYTE_edit_since_the_binder_refuses(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        cue = next(c for c in by_cue(page) if c.startswith("b"))
        (repo / "m.py").write_text(SAMPLE + "\n", encoding="utf-8", newline="")
        drafted, refused = proof_setter.run(
            {f"m.py@{cue}": "# REPLACED"}, binder, repo, tmp_path / "out"
        )
        assert drafted == []
        assert refused[0].step == "verify"

    def test_NO_DRAFT_is_written_when_the_sha_disagrees(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        cue = next(c for c in by_cue(page) if c.startswith("b"))
        (repo / "m.py").write_text(SAMPLE + "\n", encoding="utf-8", newline="")
        into = tmp_path / "out"
        proof_setter.run({f"m.py@{cue}": "# REPLACED"}, binder, repo, into)
        assert list(into.iterdir()) == []

    def test_an_UNCHANGED_file_passes(self, tmp_path):
        repo, binder, page = _tree(tmp_path)
        cue = next(c for c in by_cue(page) if c.startswith("b"))
        drafted, refused = proof_setter.run(
            {f"m.py@{cue}": "# REPLACED"}, binder, repo, tmp_path / "out"
        )
        assert refused == [] and len(drafted) == 1


def test_the_drafted_FILE_holds_each_notation_at_its_cue(tmp_path):
    repo, binder, page = _tree(tmp_path)
    cue = next(c for c in by_cue(page) if c.startswith("b"))
    drafted, refused = proof_setter.run(
        {f"m.py@{cue}": "# REPLACED"}, binder, repo, tmp_path / "out"
    )
    assert refused == []
    again = build(drafted[0].draft.read_text(encoding="utf-8"))
    assert by_cue(again)[cue].raw_lines == ["# REPLACED"]
