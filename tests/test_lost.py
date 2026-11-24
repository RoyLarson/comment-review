"""`lost`: the removed sentences the tree as written holds nowhere."""

from helpers import git_in

from comment_review.__main__ import main

MODULE = (
    "def f():\n"
    "    # Kept as it stands.\n"
    "    # The cache holds one\n"
    "    # entry per page.\n"
    "    return 1\n"
)
DROPPED = "def f():\n    # Kept as it stands.\n    return 1\n"


def _repo(tmp_path, files: dict[str, str]):
    repo = tmp_path / "repo"
    repo.mkdir()
    for rel, text in files.items():
        (repo / rel).write_text(text, encoding="utf-8", newline="")
    git_in(repo, "init", "-q")
    git_in(repo, "add", "-A")
    return repo


def _draft(root, rel: str, text: str):
    root.mkdir(exist_ok=True)
    (root / rel).write_text(text, encoding="utf-8", newline="")
    return root


def _lost(capsys, repo, *overlays) -> list[str]:
    assert main(["lost", "--repo", str(repo), *map(str, overlays)]) == 0
    return capsys.readouterr().out.splitlines()


def test_a_sentence_that_survives_nowhere_is_listed(tmp_path, capsys):
    repo = _repo(tmp_path, {"mod.py": MODULE})
    proof = _draft(tmp_path / "proof", "mod.py", DROPPED)
    assert _lost(capsys, repo, proof) == [
        "mod.py\tThe cache holds one entry per page.",
        "1 sentences in no file",
    ]


def test_a_sentence_another_tracked_file_holds_is_not_listed(tmp_path, capsys):
    history = "# History\n\nThe cache holds one entry per page.\n"
    repo = _repo(tmp_path, {"mod.py": MODULE, "history.md": history})
    proof = _draft(tmp_path / "proof", "mod.py", DROPPED)
    assert _lost(capsys, repo, proof) == ["0 sentences in no file"]


def test_a_reflowed_sentence_still_matches(tmp_path, capsys):
    other = "def g():\n    # The cache holds\n    # one entry per\n    # page.\n"
    other += "    return 2\n"
    repo = _repo(tmp_path, {"mod.py": MODULE, "other.py": other})
    proof = _draft(tmp_path / "proof", "mod.py", DROPPED)
    assert _lost(capsys, repo, proof) == ["0 sentences in no file"]


def test_a_sentence_carried_in_a_freeform_draft_survives(tmp_path, capsys):
    repo = _repo(tmp_path, {"mod.py": MODULE, "NOTES.md": "# Notes\n"})
    proof = _draft(tmp_path / "proof", "mod.py", DROPPED)
    freeform = _draft(
        tmp_path / "freeform",
        "NOTES.md",
        "# Notes\n\nThe cache holds one entry per page.\n",
    )
    assert _lost(capsys, repo, proof) == [
        "mod.py\tThe cache holds one entry per page.",
        "1 sentences in no file",
    ]
    assert _lost(capsys, repo, proof, freeform) == ["0 sentences in no file"]


def test_an_overlay_that_is_not_a_directory_is_refused(tmp_path, capsys):
    repo = _repo(tmp_path, {"mod.py": MODULE})
    assert main(["lost", "--repo", str(repo), str(tmp_path / "absent")]) == 2
    assert "not a directory" in capsys.readouterr().out
