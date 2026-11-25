"""`lost`: the removed sentences found at no place they were sent."""

from helpers import git_in

from comment_review.__main__ import main
from comment_review.binder.page import Page
from comment_review.desk.proof.master_proof import MasterProof
from comment_review.desk.proof.move import Move, Placement
from comment_review.desk.proof.place import Place
from comment_review.flows.page_for import page_of
from comment_review.flows.proof_io import save_proof
from comment_review.flows.source import source_of
from comment_review.machine.repo import Source

MODULE = (
    "def f():\n"
    "    # Kept as it stands.\n"
    "    # The cache holds one\n"
    "    # entry per page.\n"
    "    return 1\n"
)
DROPPED = "def f():\n    # Kept as it stands.\n    return 1\n"
OTHER = "def g():\n    # Reads the cache.\n    return 2\n"
CARRIED = (
    "def g():\n    # Reads the cache.\n    # The cache holds one entry per page.\n"
    "    return 2\n"
)


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


def _lost(capsys, repo, *args) -> list[str]:
    assert main(["lost", "--repo", str(repo), *map(str, args)]) == 0
    return capsys.readouterr().out.splitlines()


def _page(repo, rel: str) -> Page:
    source = source_of(repo / rel)
    assert isinstance(source, Source)
    page = page_of(repo / rel, rel=rel, source=source)
    assert isinstance(page, Page)
    return page


def _move_proof(tmp_path, repo, placement: Placement):
    """A closed proof holding one move of `mod.py`'s comment into `other.py`."""
    origin, destination = _page(repo, "mod.py"), _page(repo, "other.py")
    moved = next(p for p in origin.paragraphs if "cache holds" in p.text)
    to = next(p for p in destination.paragraphs if p.text)
    proof = MasterProof(
        stage="4a",
        read_from={},
        edit_copies=(),
        page_readings={"mod.py": origin.reading, "other.py": destination.reading},
        page_shas={"mod.py": origin.sha, "other.py": destination.sha},
        places=(Place(moved.address, moved.anchor, moved.raw_text),),
        moves=(Move(moved.address, to.address, placement=placement),),
    )
    path = tmp_path / "proof.json"
    save_proof(path, proof)
    return path


def test_a_sentence_that_survives_nowhere_is_listed_line_by_line(tmp_path, capsys):
    repo = _repo(tmp_path, {"mod.py": MODULE})
    proof = _draft(tmp_path / "proof", "mod.py", DROPPED)
    assert _lost(capsys, repo, proof) == [
        "mod.py\tThe cache holds one",
        "mod.py\tentry per page.",
        "2 sentences in no file",
    ]


def test_a_line_the_draft_keeps_is_not_joined_to_the_one_it_changes(tmp_path, capsys):
    before = (
        "def f(a, b):\n"
        '    """Do it.\n\n    Args:\n        a: first\n'
        '        b: the second one holds state.\n    """\n'
    )
    repo = _repo(tmp_path, {"m.py": before})
    proof = _draft(tmp_path / "proof", "m.py", before.replace("a: first", "a: one"))
    assert _lost(capsys, repo, proof) == ["m.py\ta: first", "1 sentences in no file"]


def test_a_sentence_rewrapped_in_its_own_file_is_not_listed(tmp_path, capsys):
    repo = _repo(tmp_path, {"mod.py": MODULE})
    rewrapped = MODULE.replace(
        "    # The cache holds one\n    # entry per page.\n",
        "    # The cache holds one entry per page.\n",
    )
    proof = _draft(tmp_path / "proof", "mod.py", rewrapped)
    assert _lost(capsys, repo, proof) == ["0 sentences in no file"]


def test_a_copy_in_a_file_no_mark_named_does_not_save_it(tmp_path, capsys):
    history = "# History\n\nThe cache holds one entry per page.\n"
    repo = _repo(tmp_path, {"mod.py": MODULE, "history.md": history})
    proof = _draft(tmp_path / "proof", "mod.py", DROPPED)
    assert _lost(capsys, repo, proof)[-1] == "2 sentences in no file"


def test_a_sentence_an_agreed_move_carried_to_its_destination_survives(
    tmp_path, capsys
):
    repo = _repo(tmp_path, {"mod.py": MODULE, "other.py": OTHER})
    drafts = _draft(tmp_path / "proof", "mod.py", DROPPED)
    _draft(drafts, "other.py", CARRIED)
    agreed = _move_proof(tmp_path, repo, Placement.AGREED)
    assert _lost(capsys, repo, "--proof", agreed, drafts) == ["0 sentences in no file"]
    withdrawn = _move_proof(tmp_path, repo, Placement.WITHDRAWN)
    out = _lost(capsys, repo, "--proof", withdrawn, drafts)
    assert out[-1] == "2 sentences in no file"


def test_an_agreed_move_saves_only_what_its_origin_held(tmp_path, capsys):
    module = MODULE.replace(
        "    return 1\n", "    x = 1\n    # Stays here.\n    return x\n"
    )
    repo = _repo(tmp_path, {"mod.py": module, "other.py": OTHER})
    dropped = module.replace("    # Stays here.\n", "").replace(
        "    # The cache holds one\n    # entry per page.\n", ""
    )
    drafts = _draft(tmp_path / "proof", "mod.py", dropped)
    _draft(drafts, "other.py", CARRIED + "# Stays here.\n")
    agreed = _move_proof(tmp_path, repo, Placement.AGREED)
    assert _lost(capsys, repo, "--proof", agreed, drafts) == [
        "mod.py\tStays here.",
        "1 sentences in no file",
    ]


def test_an_overlay_that_is_not_a_directory_is_refused(tmp_path, capsys):
    repo = _repo(tmp_path, {"mod.py": MODULE})
    assert main(["lost", "--repo", str(repo), str(tmp_path / "absent")]) == 2
    assert "not a directory" in capsys.readouterr().out


def test_a_proof_that_will_not_load_is_refused(tmp_path, capsys):
    repo = _repo(tmp_path, {"mod.py": MODULE})
    drafts = _draft(tmp_path / "proof", "mod.py", DROPPED)
    bad = tmp_path / "bad.json"
    bad.write_text("[]", encoding="utf-8")
    assert main(["lost", "--repo", str(repo), "--proof", str(bad), str(drafts)]) == 2
    assert "CANNOT READ" in capsys.readouterr().out
